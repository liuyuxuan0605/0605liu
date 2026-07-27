"""RAG 检索质量量化评估：recall@k + MRR。

这是之前完全没有的环节——没有任何标注集、recall@k、MRR。
本脚本给出一份小型但真实的标注集（见 eval_questions.py），并算出：
  - recall@k：至少有一个相关文档进入前 k 个的比例（k 默认 1/3/5/8）
  - MRR      ：首个相关文档排名的倒数的均值（衡量"相关文档排第几"）

为什么重要：app 实际把 top-5 喂给 LLM。如果真正相关的文档没进前 5，
模型只能靠噪声/万能兜底文档作答——这正是前面讨论的"噪声干扰"根因之一。
本评估直接量化这个命中率。

运行方式：
    python eval_retrieval.py                  # 默认 naive（零依赖、离线，加载 naive_index.pkl）
    python eval_retrieval.py --retriever chroma   # 需 .env 配 OPENAI_API_KEY + 网络（DashScope 嵌入）
    python eval_retrieval.py --k 1 3 5 8 10

离线可跑说明：naive 检索器是纯 TF-IDF 风格打分，结果落盘在 naive_index.pkl，
不依赖任何第三方库/网络。semantic/chroma 需要 API key 才能算向量，本沙箱无 key，
请在本地 Windows 环境用 --retriever chroma 跑，横向对比。
"""
import os
import sys
import glob
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chunks import load_chunks
from retriever import build_retriever, NaiveRetriever
from config import (
    RETRIEVER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL,
)
from eval_questions import QUERIES

# 扩展标注集（30 条口语化/冷门结构/跨结构对比/边界问法）
try:
    from eval_questions_ext import NEW_QUERIES
    QUERIES = QUERIES + NEW_QUERIES
except ImportError:
    pass

# 扩展标注集 2（29 条：为什么类/反事实/中英混杂/极短查询/选型/多跳组合）
try:
    from eval_questions_ext2 import NEW_QUERIES_2
    QUERIES = QUERIES + NEW_QUERIES_2
except ImportError:
    pass


def _naive_stale():
    """与 server.py 的 _index_is_stale 对齐：data/ 下任意 .md 比索引新 → 过期。"""
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


def build_eval_retriever(kind):
    if kind == "naive":
        r = NaiveRetriever()
        # 关键：与 server.py 一致——索引缺失/过期时重建，否则会吃到陈旧、不完整的索引
        #（之前磁盘上的 naive_index.pkl 缺少若干 notes 文件，导致大量结构过滤查询误判为空、回退全库）。
        if os.path.exists(INDEX_PATH) and not _naive_stale():
            r.load(INDEX_PATH)
            print(f"[eval] loaded naive index ({len(r.docs)} docs)", flush=True)
        else:
            reason = "缺失" if not os.path.exists(INDEX_PATH) else "过期"
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


def rel_rank(hits, rel_sources):
    """返回第一个命中相关源的 1-based 排名；未命中返回 None。"""
    rel = set(rel_sources)
    for i, h in enumerate(hits, start=1):
        src = str(h.metadata.get("source", "")).replace("\\", "/")
        if src in rel:
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default="naive",
                    choices=["naive", "semantic", "chroma"])
    ap.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 8])
    args = ap.parse_args()

    retr = build_eval_retriever(args.retriever)
    ks = sorted(set(args.k))
    K = max(ks + [8]) + 1   # 拉满排名用于准确计算 MRR（排名不受截断影响）

    rows = []
    recall_sum = {k: 0 for k in ks}
    mrr_sum = 0.0

    for item in QUERIES:
        q = item["q"]
        struct = item["structure"] or None
        hits = retr.query(q, k=K, structure=struct)
        rank = rel_rank(hits, item["rel"])
        top5 = [str(h.metadata.get("source", "")).replace("\\", "/") for h in hits[:5]]
        rows.append((q, struct, rank, top5))
        if rank is not None:
            mrr_sum += 1.0 / rank
            for k in ks:
                if rank <= k:
                    recall_sum[k] += 1

    n = len(QUERIES)
    print()
    print("=" * 78)
    print(f"RAG 检索质量评估   retriever={args.retriever}   queries={n}")
    print("=" * 78)
    print("【核心指标】")
    for k in ks:
        c = recall_sum[k]
        print(f"  Recall@{k:<2} = {c}/{n} = {c / n:.2%}   "
              f"(至少 1 个相关文档进入前 {k})")
    print(f"  MRR      = {mrr_sum / n:.3f}   (首个相关文档排名的倒数的均值)")
    print("-" * 78)
    print("【逐条诊断】 rank = 首个相关文档的 1-based 位置；None = 前{K}个都没命中")
    for q, struct, rank, top5 in rows:
        flag = "OK " if rank is not None else "MISS"
        s = struct if struct else "(无结构过滤)"
        print(f"  [{flag}] rank={str(rank):>4}  struct={s:<16} {q}")
        if rank is None:
            print(f"           top5 实际召回: {top5}")
    print("=" * 78)
    print("提示：recall@5 直接对应『喂给 LLM 的 top-5 里有没有答案』。"
          "若偏低，优先看上面 MISS 行的 top5，判断是结构过滤误杀还是词面不匹配。")


if __name__ == "__main__":
    main()
