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
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL, PORT,
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
    # 语义/向量检索失败（如 key 无效 / 网络不可达 / 嵌入函数不兼容），降级为关键词检索，保证服务可用
    print(f"[WARN] {RETRIEVER} 检索构建失败（{e}），降级为 naive 关键词检索", flush=True)
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
    """向量路查询改写：仅在主路为向量、且 LLM 可用时尝试。"""
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
    )
    return {"answer": ans, "highlight_nodes": hl, "sources": src, "actions": actions}


class _Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

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

            # decode: try utf-8 first (Qt client / proper tools),
            # fall back to gbk (Windows curl sends Chinese in GBK by default)
            text = None
            for enc in ("utf-8", "gbk", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
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
            self._cors()
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
                self._cors()
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
