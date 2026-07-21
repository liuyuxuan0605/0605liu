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
from retriever import NaiveRetriever, build_retriever
from llm import call_llm
from config import (
    RETRIEVER, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL, PORT,
)

def _index_is_stale():
    """data/ 下任意 .md 比索引新 → 索引过期，需重建。"""
    if not os.path.exists(INDEX_PATH):
        return True
    pk_mtime = os.path.getmtime(INDEX_PATH)
    for sub in ("interview", "notes", "generated", "open"):
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
        # 语义检索：__init__ 已尝试加载本地向量缓存；count()==0 说明需首次/重建嵌入
        if _retriever.count() == 0:
            _retriever.add(_chunks)
            print(f"built semantic index via {EMBEDDING_MODEL} ({_retriever.count()} docs)", flush=True)
        else:
            print(f"reused semantic cache ({_retriever.count()} docs, persistent)", flush=True)
except Exception as e:  # noqa: BLE001
    # 语义检索失败（如 key 无效 / 网络不可达），降级为关键词检索，保证服务可用
    print(f"[WARN] 语义检索构建失败（{e}），降级为 naive 关键词检索", flush=True)
    _retriever = NaiveRetriever()
    if os.path.exists(INDEX_PATH) and not _index_is_stale():
        _retriever.load(INDEX_PATH)
    else:
        _retriever.add(_chunks)
        _retriever.save(INDEX_PATH)
print(f"retriever={RETRIEVER} llm={LLM_PROVIDER} embedding={EMBEDDING_MODEL}", flush=True)


def answer(question, context):
    structure = context.get("structure", "") if isinstance(context, dict) else ""
    hits = _retriever.query(question, k=5, structure=structure or None)
    ans, hl, src = call_llm(
        question, hits, context, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
    )
    return {"answer": ans, "highlight_nodes": hl, "sources": src}


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
