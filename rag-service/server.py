"""零依赖服务入口（stdlib http.server，无需 pip install 即可运行）。

    python server.py
    curl -X POST http://localhost:8000/ask \
      -H 'Content-Type: application/json' \
      -d '{"question":"为什么 AVL 插入 20 后要右旋","context":{}}'

依赖：仅 Python 标准库。retriever=naive、llm=offline 时完全离线可用。
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks
from retriever import NaiveRetriever, build_retriever
from llm import call_llm
from config import (
    RETRIEVER, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL, PORT,
)

print("building retriever ...")
_chunks = load_chunks(DATA_DIR)
_retriever = build_retriever(RETRIEVER, EMBEDDING_MODEL)
if isinstance(_retriever, NaiveRetriever) and os.path.exists(INDEX_PATH):
    _retriever.load(INDEX_PATH)
    print(f"loaded naive index ({len(_retriever.docs)} docs)")
else:
    _retriever.add(_chunks)
    if isinstance(_retriever, NaiveRetriever):
        _retriever.save(INDEX_PATH)
print(f"retriever={RETRIEVER} llm={LLM_PROVIDER}")


def answer(question, context):
    structure = context.get("structure", "") if isinstance(context, dict) else ""
    hits = _retriever.query(question, k=4, structure=structure or None)
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
        try:
            if self.path.rstrip("/") != "/ask":
                self.send_response(404)
                self.end_headers()
                return
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            res = answer(body.get("question", ""), body.get("context", {}))
            data = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            err = json.dumps({"error": str(e), "traceback": tb}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"serving on http://localhost:{PORT}/ask  (Ctrl+C to stop)")
    HTTPServer(("0.0.0.0", PORT), _Handler).serve_forever()
