"""Hybrid 检索：向量路 + 关键词路(BM25) 双路并行，RRF 融合 + 规则式重排。

从 server.py 抽出的独立模块，供 server / eval_retrieval / eval_generation 共用，
保证评估与生产走同一套融合逻辑。
"""
from retriever import _dedup_by_source, _expand_terms, _terms

RRF_K = 60


def _passage_key(h):
    # 文档级 RRF：以 source 为合并键。两路各自返回的 hits 已按 source 去重，
    # 故 key 不会在单路内重复；不同路命中同一文档时在此累加 rank 贡献，
    # 与最终 _dedup_by_source 的粒度一致（hybrid 的价值：同文档在向量路第5、
    # 关键词路第1，合并后名次提升）。
    return str(h.metadata.get("source", ""))


def hybrid_search(question, vec_retriever, kw_retriever, k=5, structure=None,
                  context=None, rewrite_fn=None):
    """向量检索 + 关键词(BM25)检索 双路并行，RRF 合并排名后再按来源去重。

    RRF: fused_score(passage) = Σ 1/(RRF_K + rank_i)，两路排名独立贡献，
    不要求 passage 严格对齐，覆盖面比单路宽很多（向量捕语义、关键词精准命中）。

    参数：
        vec_retriever: 向量检索器（ChromaRetriever / SemanticRetriever），可为 None
        kw_retriever:  关键词检索器（NaiveRetriever / BM25），可为 None
        rewrite_fn:    可选的查询改写函数 (question, context) -> str；
                       仅作用于向量路，关键词路保持原查询。为 None 则不改写。
    """
    struct = structure or None
    # 两路是同一实例（降级场景）→ 退化为单路，避免重复检索
    same = (vec_retriever is kw_retriever)

    # —— 向量路查询改写（Direct Query Rewrite）——
    vec_query = question
    if not same and rewrite_fn is not None:
        vec_query = rewrite_fn(question, context)

    vec_hits = []
    if vec_retriever is not None and not same:
        vec_hits = vec_retriever.query(vec_query, k=max(k * 2, 10), structure=struct)

    kw_hits = []
    if kw_retriever is not None and not same:
        kw_hits = kw_retriever.query(question, k=max(k * 2, 10), structure=struct)

    # 单路模式（降级 / 两路同实例）：直接用该路结果
    if same:
        r = vec_retriever or kw_retriever
        if r is not None:
            return r.query(question, k=k, structure=struct)
        return []

    # 极端兜底：两路皆空时强制跑一次关键词路，保证总有资料可答
    if not vec_hits and not kw_hits and kw_retriever is not None:
        kw_hits = kw_retriever.query(question, k=max(k * 2, 10), structure=struct)

    # ---- RRF 融合 ----
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

    # ---- 规则式 rerank（无 key 可跑）----
    # 用 query 的「规范化概念词」与正文重叠度二次重排，抬 Precision。
    # 只取 ascii/长 token 作为信号（即同义词引入的 evict/rotate/union-find/deque/mst
    # 等规范术语）；中文按单字太碎、重叠不可靠，留给 RRF 主排序。
    # qsig 为空（纯中文无规范词）时 rerank 退化为恒等，不影响原排序，安全。
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
