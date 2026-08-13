"""零依赖服务入口（stdlib http.server）。

    python server.py

依赖：仅 Python 标准库。retriever=naive、llm=offline 时完全离线可用。
"""
import json
import os
import sys
import time
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks
from retriever import NaiveRetriever, build_retriever
from doc_index import load_manifest, compute_sync_plan, save_manifest
from llm import call_llm, rewrite_query
from hybrid import hybrid_search
from config import (
    RETRIEVER, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL, PORT, QUERY_REWRITE,
)

print("building retriever ...", flush=True)
_chunks = load_chunks(DATA_DIR)


def _index_retriever(retriever, chunks, plan, first_run):
    """对单个 retriever 做「首次全量 / 后续增量」。

    关键点：用 ``retriever.add()`` 的返回值区分「真·全量重建」与「复用缓存」，
    避免重复烧 API：

    - ``built=True``（add 真的全量重建了）：索引此刻已含**所有**当前 chunk，
      连 plan 里的变更都已在内 → **不再** sync，否则会把变更文档再删再加一遍、
      白调一次 DashScope 嵌入。naive 路需显式落盘 pickle；semantic/chroma 内部已持久化。
    - ``built=False``（add 复用了未失效缓存）：缓存是「上次同步后」的快照，
      仅 plan 里的 rechunk/remove（**新增/修改/删除**文档）尚未反映 → 走 ``sync`` 增量，
      只动变化文档，不变文档不重嵌（省 DashScope API）。

    naive 的 add 恒返回 True（本地 BM25 零 API 成本，故意每次全量）；
    semantic/chroma 的 add 在缓存有效时返回 False、走后续 sync 增量。
    """
    built = retriever.add(chunks, force=first_run)
    if built:
        # 全量重建已完成（含所有当前 chunk，含本批变化）。
        if isinstance(retriever, NaiveRetriever):
            retriever.save(INDEX_PATH)  # naive 不自动落盘，需显式 save
        return
    # 复用缓存：仅把「上次同步后新发生的变化」增量 sync 进去。
    if not first_run and (plan["rechunk"] or plan["remove"]):
        retriever.sync(plan["rechunk"], plan["remove"])
        if isinstance(retriever, NaiveRetriever):
            retriever.save(INDEX_PATH)


# —— 增量索引：用 manifest（doc_id→{mtime,hash,chunk_ids}）对比 data/ 变化 ——
# mtime 粗筛（没变直接跳过），变了才算 sha256 精判；真正变化的文档才重切重嵌。
_manifest = load_manifest(DATA_DIR)
_plan = compute_sync_plan(DATA_DIR, _manifest)
_first_run = not _manifest
_n_rechunk = sum(len(v) for v in _plan["rechunk"].values())
_n_remove = sum(len(v) for v in _plan["remove"].values())
print(f"[index] {'首次全量构建' if _first_run else '增量检查'}："
      f"待重切文档 {len(_plan['rechunk'])}（{_n_rechunk} chunk），待删除 {_n_remove} chunk",
      flush=True)

try:
    _retriever = build_retriever(
        RETRIEVER, EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
        chat_model=OPENAI_MODEL,
    )
    _index_retriever(_retriever, _chunks, _plan, _first_run)
except Exception as e:  # noqa: BLE001
    # 三级降级链（有 key 前提下）：chroma 构建失败 → semantic 离线语义档（pickle+内存余弦）→ naive。
    # 此前 chroma 一失败就直接跳 naive，丢失中间档；semantic 只需 key 做查询嵌入，
    # 不依赖 chromadb 包，是 chroma 与纯关键词之间的真实中间档。
    print(f"[WARN] {RETRIEVER} 检索构建失败（{e}）", flush=True)
    _retriever = None
    if RETRIEVER == "chroma" and OPENAI_API_KEY:
        try:
            print("[WARN] 降级为 semantic 语义缓存档（pickle+内存余弦）", flush=True)
            _retriever = build_retriever(
                "semantic", EMBEDDING_MODEL,
                api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
                chat_model=OPENAI_MODEL,
            )
            _index_retriever(_retriever, _chunks, _plan, _first_run)
        except Exception as e2:  # noqa: BLE001
            print(f"[WARN] semantic 中间档也失败（{e2}），继续降级", flush=True)
            _retriever = None
    if _retriever is None:
        print("[WARN] 降级为 naive 关键词检索", flush=True)
        _retriever = NaiveRetriever()
        _index_retriever(_retriever, _chunks, _plan, _first_run)
print(f"retriever={RETRIEVER} llm={LLM_PROVIDER} embedding={EMBEDDING_MODEL}", flush=True)

# ---- hybrid 检索：向量路(_retriever) + 关键词路(_kw, BM25) 经 RRF 合并 ----
# 关键词路复用现成的 NaiveRetriever（Okapi BM25：binary tf + 文档长度归一 + 标准 IDF）。
# 若主路本身就是 naive（降级 / RETRIEVER=naive），则两路同一实例，
# hybrid_search 退化为单路，避免重复检索。
_kw = None
if isinstance(_retriever, NaiveRetriever):
    _kw = _retriever
    print("[hybrid] 主路即 naive，关键词路复用（单路模式）", flush=True)
else:
    try:
        _kw = NaiveRetriever()
        _index_retriever(_kw, _chunks, _plan, _first_run)
        print(f"[hybrid] built keyword index ({len(_kw.docs)} docs)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 关键词路构建失败，退回纯向量检索: {e}", flush=True)
        _kw = None

# manifest 落地：首次运行把当前 chunk_ids 记下来；后续每次 sync 后也更新
save_manifest(DATA_DIR, _plan["new_manifest"])


# ---- 后台轮询：每 30s 检测 data/ 变化并增量 sync（实现「轮询检测」）----
def _poll_loop():
    while True:
        time.sleep(30)
        try:
            m = load_manifest(DATA_DIR)
            p = compute_sync_plan(DATA_DIR, m)
            if p["rechunk"] or p["remove"]:
                _retriever.sync(p["rechunk"], p["remove"])
                if _kw is not _retriever and _kw is not None:
                    _kw.sync(p["rechunk"], p["remove"])
                save_manifest(DATA_DIR, p["new_manifest"])
                added = sum(len(v) for v in p["rechunk"].values())
                removed = sum(len(v) for v in p["remove"].values())
                print(f"[poll] 增量同步完成：+{added} chunk / -{removed} chunk", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[poll] 同步异常（忽略，30s 后重试）: {e}", flush=True)


_poll_thread = threading.Thread(target=_poll_loop, daemon=True)
_poll_thread.start()

if LLM_PROVIDER != "offline" and not OPENAI_API_KEY:
    print("[WARN] LLM_PROVIDER 设为 openai 但 OPENAI_API_KEY 为空，将降级为离线拼接！请检查 .env 的 OPENAI_API_KEY", flush=True)
if RETRIEVER in ("semantic", "chroma") and not OPENAI_API_KEY:
    print(f"[WARN] RETRIEVER={RETRIEVER} 但 OPENAI_API_KEY 为空，将降级为 naive 关键词检索！", flush=True)


def _rewrite_fn(question, context):
    """向量路查询改写：仅在主路为向量、LLM 可用、且开关开启时尝试。

    范围收敛（review S6）：Direct Query Rewrite 默认关闭（RAG_QUERY_REWRITE=1 开启），
    避免每次查询多烧一次 LLM 调用；关键词路(BM25)本就带同义词扩展兜底。
    """
    if not QUERY_REWRITE:
        return question
    if _kw is not _retriever and LLM_PROVIDER != "offline" and OPENAI_API_KEY:
        return rewrite_query(
            question, context,
            api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, model=OPENAI_MODEL,
        )
    return question


def answer(question, context, history=None):
    structure = context.get("structure", "") if isinstance(context, dict) else ""
    hits = hybrid_search(
        question, _retriever, _kw, k=5,
        structure=structure or None, context=context,
        rewrite_fn=_rewrite_fn,
    )
    ans, hl, src, actions = call_llm(
        question, hits, context, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
        history=history,
        # 分路门控信号：主路为 naive（含降级）时走 q_match 门控，向量/hybrid 走相似度阈值
        retriever_kind="naive" if isinstance(_retriever, NaiveRetriever) else "vector",
    )
    return {"answer": ans, "highlight_nodes": hl, "sources": src, "actions": actions}


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("[DEBUG] do_POST entered", file=sys.stderr, flush=True)
        try:
            path = self.path
            print(f"[DEBUG] path={path!r}", file=sys.stderr, flush=True)

            if path.rstrip("/") != "/ask":
                self.send_response(404)
                self.end_headers()
                return

            n_str = self.headers.get("Content-Length", "0")
            print(f"[DEBUG] Content-Length header={n_str!r}", file=sys.stderr, flush=True)
            n = int(n_str)

            raw = self.rfile.read(n)
            print(f"[DEBUG] read {len(raw)} bytes", file=sys.stderr, flush=True)

            # decode：仅 UTF-8（Qt 客户端与规范工具均发 UTF-8）。
            # review S6：删除多编码兜底——Qt 客户端用不到；多编码猜测可能
            # 把合法 UTF-8 误判。若需 Windows curl 调试，请用 -H 显式 UTF-8 或加回兜底。
            text = raw.decode("utf-8", errors="replace")
            body = json.loads(text if text else "{}")
            question = body.get("question", "")
            context = body.get("context", {})
            history = body.get("history", [])
            print(f"[DEBUG] question={question!r}", file=sys.stderr, flush=True)

            res = answer(question, context, history)
            data = json.dumps(res, ensure_ascii=False).encode("utf-8")
            print(f"[DEBUG] answer len={len(data)} highlight={res['highlight_nodes']}", file=sys.stderr, flush=True)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            print("[DEBUG] response sent OK", file=sys.stderr, flush=True)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"[ERROR] {e}\n{tb}", file=sys.stderr, flush=True)
            # Ultra-safe: pure ASCII error response
            err_body = ("{\"error\": \"" + str(e).replace("\"", "'") +
                        "\", \"detail\": \"check server stderr for traceback\"}").encode("ascii", errors="replace")
            try:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            except Exception:
                pass  # if even this fails, nothing we can do

    def log_message(self, *a):
        # Print requests to stderr so we see them
        print(f"[REQ] {a}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    print(f"serving on http://localhost:{PORT}/ask  (Ctrl+C to stop)", flush=True)
    HTTPServer(("0.0.0.0", PORT), _Handler).serve_forever()
