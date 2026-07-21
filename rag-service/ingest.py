"""构建检索索引。

naive 模式把 chunk 持久化到 naive_index.pkl（零依赖）；
chroma 模式把向量写入 chromadb 集合。运行示例：

    python ingest.py            # 用 .env 里的 RETRIEVER
    python ingest.py --retriever chroma
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunks import load_chunks
from retriever import build_retriever, NaiveRetriever
from config import RETRIEVER, DATA_DIR, INDEX_PATH, EMBEDDING_MODEL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default=RETRIEVER, choices=["naive", "chroma"])
    args = ap.parse_args()

    print(f"loading chunks from {DATA_DIR} ...")
    chunks = load_chunks(DATA_DIR)
    print(f"  {len(chunks)} chunks")

    r = build_retriever(args.retriever, EMBEDDING_MODEL)
    r.add(chunks)

    if isinstance(r, NaiveRetriever):
        r.save(INDEX_PATH)
        print(f"naive index saved -> {INDEX_PATH}")
    else:
        print("chroma collection built")


if __name__ == "__main__":
    main()
