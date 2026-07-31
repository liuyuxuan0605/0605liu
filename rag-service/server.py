"""零依赖服务入口（stdlib http.server）。

    python server.py

依赖：仅 Python 标准库。retriever=naive、llm=offline 时完全离线可用。
"""
import json
import os
import sys
import glob
import time
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks, build_source_full, build_parent_index, SUBDIRS
from retriever import NaiveRetriever, build_retriever, _dedup_by_source, _expand_terms, _terms
from doc_index import load_manifest, compute_sync_plan, save_manifest
from llm import call_llm, rewrite_query
from config import (
    RETRIEVER, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL, PORT,
)

def _index_is_stale():
    """data/ 下任意 .md 比索引新 → 索引过期，需重建。"""
    if not os.path.exists(INDEX_PATH):
        return True
    pk_mtime = os.path.getmtime(INDEX_PATH)
    for sub in SUBDIRS:
        d = os.path.join(DATA_DIR, sub)
        if not os.path.isdir(d):
            continue
        for fp in glob.glob(os.path.join(d, "*.md")):
            if os.path.getmtime(fp) > pk_mtime:
                return True
    return False


print("building retriever ...", flush=True)
_chunks = load_chunks(DATA_DIR)
# Parent-Child：把每篇 source 的所有 child chunk 聚合成整篇，作为喂给 LLM 的
# parent 上下文。检索仍用 child（向量/关键词精度高），阅读用整篇（少漏事实）。
SOURCE_FULL = build_source_full(_chunks)          # 兜底 / 兼容用整篇
PARENT_INDEX = build_parent_index(_chunks)        # 主 LLM 用「命中段窗口」，防大文件喂爆上下文


def _index_retriever(retriever, chunks, plan, first_run):
    """对单个 retriever 做「首次全量 / 后续增量」。

    - naive：pickle 缓存未过期就 load（快、零 API）；过期则全量 add；
      非首次且有变化再 sync 增量（轮询路径走这条，不重建）。
    - 语义/向量：add() 内部已判缓存是否过期（加载或全量嵌入），不调 add 就永远不重建；
      非首次且有变化再 sync（只重嵌变更文档，省 DashScope API）。
    """
    if isinstance(retriever, NaiveRetriever):
        if os.path.exists(INDEX_PATH) and not _index_is_stale():
            retriever.load(INDEX_PATH)
            if not first_run and (plan["rechunk"] or plan["remove"]):
                retriever.sync(plan["rechunk"], plan["remove"])
                retriever.save(INDEX_PATH)
        else:
            retriever.add(chunks)
            retriever.save(INDEX_PATH)
    else:
        retriever.add(chunks)  # 内部判缓存：未过期则复用，不重复嵌入
        if not first_run and (plan["rechunk"] or plan["remove"]):
            retriever.sync(plan["rechunk"], plan["remove"])


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

# ---- hybrid 检索：向量路(_retriever) + 关键词路(_kw, TF-IDF) 经 RRF 合并 ----
# 关键词路复用现成的 NaiveRetriever（IDF 加权词项交集，等价于轻量 BM25）。
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

RRF_K = 60

def _passage_key(h):
    # 文档级 RRF：以 source 为合并键。两路各自返回的 hits 已按 source 去重，
    # 故 key 不会在单路内重复；不同路命中同一文档时在此累加 rank 贡献，
    # 与最终 _dedup_by_source 的粒度一致（hybrid 的价值：同文档在向量路第5、
    # 关键词路第1，合并后名次提升）。
    return str(h.metadata.get("source", ""))

def hybrid_search(question, k=5, structure=None, context=None):
    """向量检索 + 关键词(TF-IDF)检索 双路并行，RRF 合并排名后再按来源去重。

    RRF: fused_score(passage) = Σ 1/(RRF_K + rank_i)，两路排名独立贡献，
    不要求 passage 严格对齐，覆盖面比单路宽很多（向量捕语义、关键词精准命中）。

    Direct Query Rewrite：仅对「向量检索路」的查询做改写（术语归一 + 上下文补全），
    关键词路保持原查询（自带同义词扩展兜底）。改写失败/无需改写时回退原 query，
    不影响关键词路，也不影响最终答案的忠实度地板。
    """
    struct = structure or None
    # —— 向量路查询改写（Direct Query Rewrite）——
    # 仅在主路为向量、且 LLM 可用时尝试；改写只作用于向量路检索，
    # 关键词路(kw_hits)仍用原始 question，保证字面兜底不丢。
    vec_query = question
    if _kw is not _retriever and LLM_PROVIDER != "offline" and OPENAI_API_KEY:
        vec_query = rewrite_query(
            question, context,
            api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, model=OPENAI_MODEL,
        )
    vec_hits = []
    if _kw is not _retriever:  # 主路是向量时才单独跑，避免与关键词路重复
        vec_hits = _retriever.query(vec_query, k=max(k * 2, 10), structure=struct)
    kw_hits = []
    if _kw is not None and _kw is not _retriever:
        kw_hits = _kw.query(question, k=max(k * 2, 10), structure=struct)
    # 极端兜底：两路皆空时强制跑一次关键词路，保证总有资料可答
    if not vec_hits and not kw_hits and _kw is not None:
        kw_hits = _kw.query(question, k=max(k * 2, 10), structure=struct)

    fused = {}
    order = []
    seen = set()
    # ⚠️ 标准 RRF：每条检索路各自独立排名（rank 在每路内部从 0 起算），
    # 不能把两路拼接后统一 enumerate——否则关键词路的 rank 被向量路长度偏移，
    # 导致关键词路被系统性低估。逐路枚举才正确。
    for results in (vec_hits, kw_hits):
        for rank, h in enumerate(results):
            key = _passage_key(h)
            contrib = 1.0 / (RRF_K + rank)
            if key in fused:
                fused[key] += contrib
            else:
                fused[key] = contrib
                if key not in seen:
                    seen.add(key)
                    order.append((key, h))
    order.sort(key=lambda kv: -fused[kv[0]])
    # —— 规则式 rerank（无 key 可跑）：用 query 的「规范化概念词」与正文重叠度二次重排，抬 Precision。
    # 只取 ascii/长 token 作为信号（即同义词引入的 evict/rotate/union-find/deque/mst 等规范术语）；
    # 中文按单字太碎、重叠不可靠，留给 RRF 主排序。qsig 为空（纯中文无规范词）时 rerank 退化为
    # 恒等，不影响原排序，安全。fused 分乘以 (1 + 0.8*overlap) 让高重叠的相关文档压过同分段噪声。
    qterms = _expand_terms(question)
    qsig = {t for t in qterms if any(c.isascii() for c in t) and len(t) > 1}
    scored = []
    for key, h in order:
        htext = getattr(h, "text", "") or ""
        dsig = {t for t in _terms(htext) if any(c.isascii() for c in t) and len(t) > 1}
        if qsig:
            inter = qsig & dsig
            # 前缀兜底：evict 也能命中 evicts/eviction，rotate 命中 rotated/rotation 等，
            # 避免整词切分把复数/分词挡在门外导致 rerank 漏判。
            for q in qsig:
                if len(q) >= 4:
                    for d in dsig:
                        if d.startswith(q) or q.startswith(d):
                            inter.add(q)
                            break
            overlap = len(inter) / max(1, len(qsig))
        else:
            overlap = 0.0
        scored.append((key, h, fused[key] * (1.0 + 0.8 * overlap)))
    scored.sort(key=lambda x: -x[2])
    order = [(k, h) for k, h, _ in scored]
    merged = [h for _, h in order[: max(k * 3, 20)]]
    return _dedup_by_source(merged, k)

if LLM_PROVIDER != "offline" and not OPENAI_API_KEY:
    print("[WARN] LLM_PROVIDER 设为 openai 但 OPENAI_API_KEY 为空，将降级为离线拼接！请检查 .env 的 OPENAI_API_KEY", flush=True)
if RETRIEVER in ("semantic", "chroma") and not OPENAI_API_KEY:
    print(f"[WARN] RETRIEVER={RETRIEVER} 但 OPENAI_API_KEY 为空，将降级为 naive 关键词检索！", flush=True)


def answer(question, context):
    structure = context.get("structure", "") if isinstance(context, dict) else ""
    hits = hybrid_search(question, k=5, structure=structure or None, context=context)
    ans, hl, src, actions = call_llm(
        question, hits, context, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
        source_full=SOURCE_FULL, parent_index=PARENT_INDEX,
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
            print(f"[DEBUG] question={question!r}", file=sys.stderr, flush=True)

            res = answer(question, context)
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
