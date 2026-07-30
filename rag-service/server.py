"""零依赖服务入口（stdlib http.server）。

    python server.py

依赖：仅 Python 标准库。retriever=naive、llm=offline 时完全离线可用。
"""
import json
import os
import sys
import glob
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks
from retriever import NaiveRetriever, build_retriever, _dedup_by_source
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
    for sub in ("interview", "notes", "generated", "open", "knowledge"):
        d = os.path.join(DATA_DIR, sub)
        if not os.path.isdir(d):
            continue
        for fp in glob.glob(os.path.join(d, "*.md")):
            if os.path.getmtime(fp) > pk_mtime:
                return True
    return False


print("building retriever ...", flush=True)
_chunks = load_chunks(DATA_DIR)
try:
    _retriever = build_retriever(
        RETRIEVER, EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
        chat_model=OPENAI_MODEL,
    )
    if isinstance(_retriever, NaiveRetriever):
        if os.path.exists(INDEX_PATH) and not _index_is_stale():
            _retriever.load(INDEX_PATH)
            print(f"loaded naive index ({len(_retriever.docs)} docs)", flush=True)
        else:
            _retriever.add(_chunks)
            _retriever.save(INDEX_PATH)
            print(f"rebuilt naive index ({len(_retriever.docs)} docs)", flush=True)
    else:
        # 语义/向量检索：把「是否重建」的判断完全交给 retriever.add()。
        # ⚠️ 不能用 count()>0 直接复用——ChromaRetriever 的过期检测（拿 collection
        # 里存的 data_mtime 和当前语料 mtime 比较）写在 add() 内部，若不调用 add()，
        # 新增/修改的语料（如 theory 知识文档）永远不会触发重建，表现就是「还是 538 条」。
        _retriever.add(_chunks)
except Exception as e:  # noqa: BLE001
    # 语义/向量检索失败（如 key 无效 / 网络不可达 / 嵌入函数不兼容），降级为关键词检索，保证服务可用
    print(f"[WARN] {RETRIEVER} 检索构建失败（{e}），降级为 naive 关键词检索", flush=True)
    _retriever = NaiveRetriever()
    if os.path.exists(INDEX_PATH) and not _index_is_stale():
        _retriever.load(INDEX_PATH)
    else:
        _retriever.add(_chunks)
        _retriever.save(INDEX_PATH)
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
        if os.path.exists(INDEX_PATH) and not _index_is_stale():
            _kw.load(INDEX_PATH)
            print(f"[hybrid] loaded keyword index ({len(_kw.docs)} docs)", flush=True)
        else:
            _kw.add(_chunks)
            _kw.save(INDEX_PATH)
            print(f"[hybrid] built keyword index ({len(_kw.docs)} docs)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 关键词路构建失败，退回纯向量检索: {e}", flush=True)
        _kw = None

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
        question, hits, context, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
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
