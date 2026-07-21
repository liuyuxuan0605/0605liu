"""生产级服务入口（FastAPI + chroma + openai）。

    pip install -r requirements.txt
    python app.py
    # 或：uvicorn app:app --port 8000

与 server.py 共用 answer() 逻辑；requires fastapi / chromadb / sentence-transformers / openai。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import answer  # 复用检索 + LLM 逻辑
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="DSVisualizer RAG Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"])


class AskRequest(BaseModel):
    question: str
    context: dict = {}


@app.post("/ask")
def ask(req: AskRequest):
    return answer(req.question, req.context)


if __name__ == "__main__":
    import uvicorn
    from config import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)
