"""eval 脚本共用：检索器构建（review S10 从 eval_generation/eval_retrieval 抽出的单一来源）。

两脚本的 build_eval_retriever 此前各自维护一份、已分叉（naive 分支的陈旧判定逻辑不同）。
统一为严谨版：naive 用 _naive_stale() + load() 复用，否则重建；向量路包 try/except 给出明确失败原因。
"""
import os

from config import (
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    EMBEDDING_MODEL, DATA_DIR, INDEX_PATH,
)
import glob

from chunks import load_chunks, SUBDIRS
from retriever import build_retriever, NaiveRetriever


def _naive_stale():
    """data/ 下任意 .md 比索引新 → 过期（与历史 server._index_is_stale 对齐）。"""
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


def build_eval_retriever(kind):
    """构建评估用的检索器，与 server.py 的索引/降级口径保持一致。"""
    if kind == "naive":
        r = NaiveRetriever()
        # 关键：与 server.py 一致——索引缺失/过期时重建，否则会吃到陈旧、不完整的索引。
        # load() 返回 False = 语料目录集（SUBDIRS）已变，旧索引口径不同 → 必须重建。
        if os.path.exists(INDEX_PATH) and not _naive_stale() and r.load(INDEX_PATH):
            print(f"[eval] loaded naive index ({len(r.docs)} docs)", flush=True)
        else:
            reason = "缺失" if not os.path.exists(INDEX_PATH) else "过期或语料目录集已变"
            print(f"[eval] naive index{reason}，离线重建中（数秒）...", flush=True)
            r.add(load_chunks(DATA_DIR))
            r.save(INDEX_PATH)
            print(f"[eval] rebuilt naive index ({len(r.docs)} docs)", flush=True)
        return r
    if not OPENAI_API_KEY:
        raise SystemExit(
            f"[eval] RETRIEVER={kind} 需要 OPENAI_API_KEY + 网络（DashScope 嵌入），"
            f"本环境未配置。请在本机 .env 配好 key 后用 --retriever {kind} 运行。"
        )
    try:
        r = build_retriever(
            kind, EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
            chat_model=OPENAI_MODEL,
        )
        # 若已建好缓存/库则直接复用，避免重复耗 API
        r.add(load_chunks(DATA_DIR))
        print(f"[eval] built {kind} retriever", flush=True)
        return r
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"[eval] 构建 {kind} 检索器失败：{e}")
