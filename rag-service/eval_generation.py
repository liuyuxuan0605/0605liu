"""RAG 生成层质量评估：LLM-as-a-Judge 四指标。

评估维度（对齐 RAGAs 框架）：
  1. Context Precision  — 检索回来的 top-k 里有多少是真正相关的（噪声比例）
  2. Context Recall     — 检索资料是否覆盖了回答所需的全部关键信息（需 ground truth）
  3. Faithfulness       — LLM 回答是否忠实于检索资料，有没有编造（幻觉检测）
  4. Answer Relevancy   — LLM 回答是否在直接回答用户的问题（有没有跑偏）

运行方式：
    python eval_generation.py                          # 默认 chroma，跑全部 80 条
    python eval_generation.py --retriever naive        # 用 naive 检索器
    python eval_generation.py --limit 20               # 只跑前 20 条（省 API 调用）
    python eval_generation.py --metrics faithfulness   # 只跑忠实度（最省）
    python eval_generation.py --metrics faithfulness relevancy

依赖：与 eval_retrieval.py 相同（config / chunks / retriever / llm）。
Judge 调用走 DashScope OpenAI 兼容接口（与主 LLM 同 key），temperature=0 保证评分稳定。
"""
import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chunks import load_chunks
from retriever import build_retriever, NaiveRetriever
from hybrid import hybrid_search
from llm import call_llm, build_prompt, rewrite_query
from config import (
    RETRIEVER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    DATA_DIR, INDEX_PATH, EMBEDDING_MODEL,
)
from eval_questions import QUERIES

# 合并扩展标注集
try:
    from eval_questions_ext import NEW_QUERIES
    QUERIES = QUERIES + NEW_QUERIES
except ImportError:
    pass
try:
    from eval_questions_ext2 import NEW_QUERIES_2
    QUERIES = QUERIES + NEW_QUERIES_2
except ImportError:
    pass


# ============================================================
# Judge LLM 调用（复用主 key，temperature=0 保证评分稳定）
# ============================================================

def _judge_call(prompt, timeout=30):
    """调用 LLM 做裁判，返回解析后的 dict。失败返回 None。"""
    if not OPENAI_API_KEY:
        print("[ERROR] 生成层评估需要 OPENAI_API_KEY（Judge 调用）", flush=True)
        return None
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个严格的评估专家。只输出 JSON，不要输出其他内容。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    # 优先 JSON 模式，失败则去掉 response_format 重试
    attempts = [
        {**payload, "response_format": {"type": "json_object"}},
        payload,
    ]
    for idx, p in enumerate(attempts):
        try:
            req = urllib.request.Request(
                OPENAI_BASE_URL.rstrip("/") + "/chat/completions",
                data=json.dumps(p).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            # 剥离 ```json 围栏
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.lower().startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:  # noqa: BLE001
            if idx == len(attempts) - 1:
                print(f"  [judge] 调用失败: {type(e).__name__}: {e}", flush=True)
                return None
    return None


# ============================================================
# 评测上下文构造：给 Judge 看「整篇来源文档」而非单 chunk 前 800 字
# ============================================================
def _source_context(h):
    """faithfulness / precision 判分时构造喂给 Judge 的上下文。

    标准 RAG：检索命中的小块即作为证据上下文，直接返回该 chunk 原文，
    不扩展整篇 parent（之前 Parent-Child 的整篇/窗口扩展为非标准做法，已回退）。
    """
    t = getattr(h, "text", None)
    if t is None and isinstance(h, dict):
        t = h.get("text", "")
    return t or ""


# ============================================================
# Judge 自报分数交叉校验：以明细为准重算，防虚高
# ============================================================
def _recompute_faith(r):
    """用 results 明细重算 faithfulness，不信 Judge 自报的分数字段。

    2026-07-30 实测坑：Judge 返回 {"faithfulness": 1.00} 却在 results 里带 1 条
    status=unsupported；另一条自报 0.97 但只有 2 条 unsupported（反推需 66 条
    claim，不现实）。Judge 的算术不可靠，自报值会让均值虚高。
    这里一律用 supported/total 重算，并在与自报值不符时提示。

    返回 (faith, supported, total, mismatch_note)。
    """
    results = r.get("results") or []
    claims = r.get("claims") or []
    reported = r.get("faithfulness", None)
    if not results:
        # Judge 未给明细（或调用失败），只能退回自报值
        return (reported if isinstance(reported, (int, float)) else 0.0), 0, 0, ""
    total = len(results)
    supported = sum(1 for x in results if x.get("status") == "supported")
    faith = supported / total if total else 0.0
    notes = []
    if isinstance(reported, (int, float)) and abs(reported - faith) > 0.01:
        notes.append(f"judge自报{reported:.2f}已修正")
    if claims and total != len(claims):
        notes.append(f"judge漏判{len(claims) - total}条claim")
    return faith, supported, total, "; ".join(notes)


def _recompute_precision(r, n_hits):
    """用 scores 明细重算 precision（score>=2 视为相关），不信 Judge 自报值。"""
    scores = [s for s in (r.get("scores") or []) if isinstance(s, (int, float))]
    reported = r.get("precision", None)
    if not scores:
        return (reported if isinstance(reported, (int, float)) else 0.0), ""
    rel = sum(1 for s in scores if s >= 2)
    prec = rel / len(scores)
    notes = []
    if isinstance(reported, (int, float)) and abs(reported - prec) > 0.01:
        notes.append(f"judge自报{reported:.2f}已修正")
    if n_hits and len(scores) != min(n_hits, 5):
        notes.append(f"judge评了{len(scores)}条/实际{min(n_hits, 5)}条")
    return prec, "; ".join(notes)


# ============================================================
# 指标 1：Context Precision（上下文精确度）
# ============================================================

CONTEXT_PRECISION_PROMPT = """请评估以下每条检索资料与用户问题的相关性。

用户问题：{question}

检索资料（共 {n} 条）：
{numbered_contexts}

对每条资料打分：
- 3 = 直接相关（包含回答该问题所需的关键信息）
- 2 = 边缘相关（提及了相关概念但不直接回答问题）
- 1 = 无关（与问题无关或只是泛泛提及）

只输出 JSON：{{"scores": [3, 2, 1, ...], "relevant_count": 2, "precision": 0.4}}
precision = relevant_count（score>=2 的条数）/ 总条数"""


def eval_context_precision(question, hits):
    """评估 top-k 检索结果中有多少是真正相关的。"""
    if not hits:
        return {"scores": [], "relevant_count": 0, "precision": 0.0}
    numbered = "\n\n".join(
        f"【资料 {i+1}】{_source_context(h)}" for i, h in enumerate(hits[:5])
    )
    prompt = CONTEXT_PRECISION_PROMPT.format(
        question=question, n=min(len(hits), 5), numbered_contexts=numbered
    )
    result = _judge_call(prompt)
    if result is None:
        return {"scores": [], "relevant_count": 0, "precision": 0.0, "error": True}
    return result


# ============================================================
# 指标 2：Context Recall（上下文召回率，需 ground truth）
# ============================================================

CONTEXT_RECALL_PROMPT = """请评估检索资料是否覆盖了标准答案中的关键信息。

用户问题：{question}

标准答案（理想回答应包含的要点）：
{ground_truth}

检索资料：
{context}

请逐条检查标准答案中的关键事实，判断每条是否能在检索资料中找到支撑。
只输出 JSON：
{{"covered": 3, "total": 5, "recall": 0.6,
  "missing": ["标准答案中提到但检索资料缺失的信息1", "..."]}}
recall = covered / total"""


def eval_context_recall(question, hits, ground_truth):
    """评估检索资料是否覆盖了回答所需的全部关键信息。"""
    if not ground_truth:
        return None  # 没有 ground truth 就跳过
    context = "\n\n".join(_source_context(h) for h in hits[:5])
    prompt = CONTEXT_RECALL_PROMPT.format(
        question=question, ground_truth=ground_truth, context=context
    )
    result = _judge_call(prompt)
    if result is None:
        return {"covered": 0, "total": 0, "recall": 0.0, "missing": [], "error": True}
    return result


# ============================================================
# 指标 3：Faithfulness（忠实度 / 幻觉检测）
# ============================================================

EXTRACT_CLAIMS_PROMPT = """从以下回答中提取所有事实声明（每句话拆成独立的事实陈述，忽略语气词和连接词）。

回答：{answer}

只输出 JSON：{{"claims": ["声明1", "声明2", ...]}}"""

VERIFY_CLAIMS_PROMPT = """请判断以下每条声明是否能在给定资料中找到支撑。

资料：
{context}

声明列表：
{claims}

对每条声明判断：
- "supported" = 资料中有明确支撑
- "unsupported" = 资料中找不到依据（可能是模型自身知识或编造）

只输出 JSON：
{{"results": [{{"claim": "...", "status": "supported"}}, ...],
  "supported_count": 8, "total": 10, "faithfulness": 0.8}}
faithfulness = supported_count / total"""


def eval_faithfulness(question, hits, answer):
    """检测 LLM 回答中有多少事实声明有资料支撑（幻觉检测）。"""
    if not answer or answer.startswith("[LLM 调用失败"):
        return {"faithfulness": 0.0, "error": True}
    context = "\n\n".join(_source_context(h) for h in hits[:5])

    # 第一步：提取事实声明
    extract_result = _judge_call(EXTRACT_CLAIMS_PROMPT.format(answer=answer[:2000]))
    if extract_result is None or not extract_result.get("claims"):
        return {"faithfulness": 0.0, "claims": [], "error": True}
    claims = extract_result["claims"]

    # 第二步：逐条验证
    claims_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(claims))
    verify_result = _judge_call(VERIFY_CLAIMS_PROMPT.format(
        context=context, claims=claims_text
    ))
    if verify_result is None:
        return {"faithfulness": 0.0, "claims": claims, "error": True}
    verify_result["claims"] = claims
    return verify_result


# ============================================================
# 指标 4：Answer Relevancy（回答相关性）
# ============================================================

RELEVANCY_PROMPT = """根据以下回答，反推它最可能在回答什么问题。

回答：{answer}

请生成 3 个这段回答最可能在回答的问题，然后判断原始问题与这些反推问题的匹配程度。

原始问题：{question}

只输出 JSON：
{{"generated_questions": ["问题1", "问题2", "问题3"],
  "relevancy": 0.8,
  "reason": "简要说明回答是否切题"}}
relevancy 取值 0-1：1=完全切题，0.5=部分切题，0=完全跑偏"""


def eval_answer_relevancy(question, answer):
    """评估 LLM 回答是否在直接回答用户的问题。"""
    if not answer or answer.startswith("[LLM 调用失败"):
        return {"relevancy": 0.0, "error": True}
    prompt = RELEVANCY_PROMPT.format(answer=answer[:2000], question=question)
    result = _judge_call(prompt)
    if result is None:
        return {"relevancy": 0.0, "error": True}
    return result


# ============================================================
# 主评估流程
# ============================================================

# 部分 query 的 ground truth（用于 Context Recall）
# 格式：query 文本 → 理想回答应包含的要点
GROUND_TRUTHS = {
    "红黑树删除一个节点后怎么保持平衡、怎么修复": (
        "1. 删除后可能产生双黑节点（被删节点是黑色且其替代节点也是黑色）；"
        "2. 修复分四种情况：兄弟是红色→旋转+重着色；兄弟是黑色且兄弟的孩子有红色→旋转；"
        "兄弟是黑色且孩子全黑→重着色+向上传播；兄弟是红色→先转成黑色兄弟情况再处理；"
        "3. 最终通过旋转和重着色消除双黑，恢复红黑树五条性质"
    ),
    "AVL树怎么通过旋转修复失衡": (
        "1. 插入/删除后从底向上检查每个节点的平衡因子（左子树高度-右子树高度）；"
        "2. 平衡因子超出[-1,1]范围即失衡；"
        "3. 四种失衡类型：LL→右旋、RR→左旋、LR→先左旋后右旋、RL→先右旋后左旋；"
        "4. 旋转后更新涉及节点的高度和平衡因子"
    ),
    "哈希表怎么解决哈希冲突": (
        "1. 开放寻址法：线性探测、二次探测、双重哈希；"
        "2. 链地址法（拉链法）：每个桶挂一个链表/红黑树；"
        "3. Java HashMap 在链表长度>8 时转红黑树；"
        "4. 负载因子控制扩容阈值，避免冲突过多"
    ),
    "AVL树和红黑树有什么区别，各自适合什么场景": (
        "1. AVL 严格平衡（平衡因子∈{-1,0,1}），红黑树弱平衡（最长路径≤2×最短路径）；"
        "2. AVL 查找更快（树更矮），红黑树插入删除旋转次数更少（最多2-3次）；"
        "3. AVL 适合读多写少（数据库索引），红黑树适合写多读少（STL map/set、Linux CFS）；"
        "4. 两者查找都是 O(logn)，差异在常数项"
    ),
    "LRU缓存怎么淘汰最久没使用的元素": (
        "1. 用哈希表+双向链表实现：哈希表 O(1) 查找，双向链表维护访问顺序；"
        "2. 每次访问把节点移到链表头部（最近使用）；"
        "3. 容量满时淘汰链表尾部（最久未使用）；"
        "4. 插入新节点放头部，同时哈希表记录映射"
    ),
}


def build_eval_retriever(kind):
    """与 eval_retrieval.py 一致的检索器构建逻辑。"""
    if kind == "naive":
        r = NaiveRetriever()
        if os.path.exists(INDEX_PATH):
            r.load(INDEX_PATH)
            print(f"[eval-gen] loaded naive index ({len(r.docs)} docs)", flush=True)
        else:
            r.add(load_chunks(DATA_DIR))
            r.save(INDEX_PATH)
            print(f"[eval-gen] built naive index ({len(r.docs)} docs)", flush=True)
        return r
    if not OPENAI_API_KEY:
        raise SystemExit(
            f"[eval-gen] RETRIEVER={kind} 需要 OPENAI_API_KEY。"
            f"请在 .env 配好 key 后用 --retriever {kind} 运行。"
        )
    r = build_retriever(
        kind, EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, data_dir=DATA_DIR,
    )
    r.add(load_chunks(DATA_DIR))
    print(f"[eval-gen] built {kind} retriever", flush=True)
    return r


def main():
    ap = argparse.ArgumentParser(description="RAG 生成层质量评估（LLM-as-a-Judge）")
    ap.add_argument("--retriever", default="chroma",
                    choices=["naive", "semantic", "chroma", "hybrid"])
    ap.add_argument("--limit", type=int, default=0,
                    help="只评估前 N 条（0=全部）")
    ap.add_argument("--start", type=int, default=0,
                    help="从第 N 条开始（0-indexed），配合 --limit 做切片")
    ap.add_argument("--metrics", nargs="+",
                    default=["precision", "faithfulness", "relevancy"],
                    choices=["precision", "recall", "faithfulness", "relevancy"],
                    help="要评估的指标（默认不跑 recall，因为需要 ground truth）")
    ap.add_argument("--no-rewrite", action="store_true",
                    help="hybrid 模式下禁用向量路查询改写（省 API 调用）")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        raise SystemExit("[eval-gen] 需要 OPENAI_API_KEY 做 Judge 调用，请在 .env 配置。")

    # hybrid 模式：同时构建向量路 + 关键词路，走 RRF 融合（与生产 server.py 一致）
    if args.retriever == "hybrid":
        vec_retr = build_eval_retriever("chroma")
        kw_retr = build_eval_retriever("naive")
        retr = None
        rewrite_fn = None
        if not args.no_rewrite:
            def rewrite_fn(q, ctx):
                return rewrite_query(
                    q, ctx,
                    api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, model=OPENAI_MODEL,
                )
    else:
        vec_retr = None
        kw_retr = None
        retr = build_eval_retriever(args.retriever)
        rewrite_fn = None

    # 标准 RAG：命中小块即返回该小块，无需聚合整篇 / parent 窗口。

    queries = QUERIES[args.start:]
    if args.limit > 0:
        queries = queries[:args.limit]
    metrics = set(args.metrics)

    print(f"\n{'='*78}")
    print(f"RAG 生成层评估   retriever={args.retriever}   queries={len(queries)}   "
          f"metrics={sorted(metrics)}")
    print(f"{'='*78}\n")

    # 聚合统计
    agg = {m: [] for m in ["precision", "recall", "faithfulness", "relevancy"]}
    rows = []

    for i, item in enumerate(queries):
        q = item["q"]
        struct = item["structure"] or None
        gt = GROUND_TRUTHS.get(q, "")

        print(f"[{i+1}/{len(queries)}] {q[:40]}...", flush=True)

        # 1) 检索
        if args.retriever == "hybrid":
            hits = hybrid_search(
                q, vec_retr, kw_retr, k=5,
                structure=struct, context={"structure": struct or ""},
                rewrite_fn=rewrite_fn,
            )
        else:
            hits = retr.query(q, k=5, structure=struct)

        # 2) 生成回答（复用主 LLM 链路）
        context = {"structure": struct or ""}
        answer, hl, src, _ = call_llm(
            q, hits, context,
            provider="openai", api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL, model=OPENAI_MODEL,
            temperature=0.0,   # 评测钉死温度，保证同 query 回答可复现、faithfulness 跑批可比
        )

        row = {"q": q, "struct": struct, "answer_len": len(answer)}

        # 3) 逐指标评估
        if "precision" in metrics:
            r = eval_context_precision(q, hits)
            p, pnote = _recompute_precision(r, len(hits))  # 以 scores 明细为准
            agg["precision"].append(p)
            row["precision"] = p
            print(f"    precision={p:.2f}" + (f"  [{pnote}]" if pnote else ""),
                  flush=True)

        if "recall" in metrics and gt:
            r = eval_context_recall(q, hits, gt)
            if r:
                rc = r.get("recall", 0.0)
                agg["recall"].append(rc)
                row["recall"] = rc
                print(f"    recall={rc:.2f}", flush=True)

        if "faithfulness" in metrics:
            r = eval_faithfulness(q, hits, answer)
            f, sup, tot, fnote = _recompute_faith(r)  # 以 results 明细为准，防虚高
            agg["faithfulness"].append(f)
            row["faithfulness"] = f
            unsupported = [
                x.get("claim", "") for x in r.get("results", [])
                if x.get("status") == "unsupported"
            ]
            row["unsupported_claims"] = unsupported
            detail = f" ({sup}/{tot})" if tot else ""
            print(f"    faithfulness={f:.2f}{detail}"
                  + (f"  unsupported:{len(unsupported)}" if unsupported else "")
                  + (f"  [{fnote}]" if fnote else ""),
                  flush=True)

        if "relevancy" in metrics:
            r = eval_answer_relevancy(q, answer)
            rv = r.get("relevancy", 0.0)
            agg["relevancy"].append(rv)
            row["relevancy"] = rv
            print(f"    relevancy={rv:.2f}", flush=True)

        rows.append(row)
        time.sleep(0.5)  # 避免 API 限流

    # ============================================================
    # 输出报告
    # ============================================================
    print(f"\n{'='*78}")
    print(f"RAG 生成层评估报告   retriever={args.retriever}   queries={len(rows)}")
    print(f"{'='*78}")
    print("\n【核心指标（均值）】")
    for m in ["precision", "recall", "faithfulness", "relevancy"]:
        vals = agg[m]
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  {m:<14} = {avg:.3f}   (n={len(vals)})")
        else:
            print(f"  {m:<14} = N/A   (未评估)")

    # 忠实度最差的 5 条（幻觉高风险）
    faith_rows = [r for r in rows if "faithfulness" in r]
    if faith_rows:
        faith_rows.sort(key=lambda r: r["faithfulness"])
        print(f"\n【忠实度最低 Top-5（幻觉高风险）】")
        for r in faith_rows[:5]:
            print(f"  faith={r['faithfulness']:.2f}  {r['q'][:50]}")
            for c in r.get("unsupported_claims", [])[:2]:
                print(f"    ✗ {c[:60]}")

    # 相关性最差的 5 条（跑偏风险）
    rel_rows = [r for r in rows if "relevancy" in r]
    if rel_rows:
        rel_rows.sort(key=lambda r: r["relevancy"])
        print(f"\n【相关性最低 Top-5（跑偏风险）】")
        for r in rel_rows[:5]:
            print(f"  relevancy={r['relevancy']:.2f}  {r['q'][:50]}")

    # 精确度最差的 5 条（噪声多）
    prec_rows = [r for r in rows if "precision" in r]
    if prec_rows:
        prec_rows.sort(key=lambda r: r["precision"])
        print(f"\n【精确度最低 Top-5（检索噪声多）】")
        for r in prec_rows[:5]:
            print(f"  precision={r['precision']:.2f}  {r['q'][:50]}")

    print(f"\n{'='*78}")
    print("提示：faithfulness < 0.7 的条目需重点排查——模型可能在编造。")
    print("      precision < 0.4 说明检索噪声大，考虑加 rerank 或调 chunk 粒度。")
    print("      relevancy < 0.5 说明回答跑偏，检查 prompt 约束是否够强。")


if __name__ == "__main__":
    main()
