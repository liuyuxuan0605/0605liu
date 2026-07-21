"""构建检索索引。

naive 模式把 chunk 持久化到 naive_index.pkl（零依赖）；
semantic 模式调用 DashScope /embeddings 生成向量，缓存到 semantic_index.pkl。运行示例：

    python ingest.py                # 用 .env 里的 RETRIEVER
    python ingest.py --retriever semantic
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks
from retriever import build_retriever, NaiveRetriever
from config import (
    RETRIEVER, DATA_DIR, INDEX_PATH, EMBEDDING_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default=RETRIEVER, choices=["naive", "semantic"])
    args = ap.parse_args()

    print(f"loading chunks from {DATA_DIR} ...")
    chunks = load_chunks(DATA_DIR)
    print(f"  {len(chunks)} chunks")

    r = build_retriever(
        args.retriever, EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
    )
    r.add(chunks)

    if isinstance(r, NaiveRetriever):
        r.save(INDEX_PATH)
        print(f"naive index saved -> {INDEX_PATH}")
    else:
        print(f"semantic index built -> {r._cache_path}")


if __name__ == "__main__":
    main()
