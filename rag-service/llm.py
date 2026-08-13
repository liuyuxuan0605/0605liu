"""LLM 调用层。

- offline：无 API key 也能跑，用检索到的资料规则拼接答案，并从问题中
  抽取整数作为高亮节点值（用于演示完整链路）。
- openai：调用 OpenAI 兼容接口，要求返回 JSON（answer / highlight_nodes / sources）。
"""
import re
import json
import urllib.request
from enum import Enum

# 硬拒阈值：空检索或 top 相似度低于此值 → 直接拒答，不调 LLM。
# 用于拦截"李白是谁"这类明显离域、但 chroma 仍能捞出 0.25~0.4 弱命中的查询。
HARD_REJECT_FLOOR = 0.4

# 弱相关阈值：top 相似度低于此值（但高于 HARD_REJECT_FLOOR）→ 注入收紧指令。
# chroma/semantic 是余弦相似度(0..1)；naive 是 IDF 加权和(常>1)，不受影响。
WARN_FLOOR = 0.55


def _best_score(hits):
    """取 top5 最高分。chroma/semantic 的 score 是余弦(0..1)，naive 是 IDF 加权和(常>1)。"""
    return max((h.score for h in hits[:5]), default=0.0)


SYSTEM_PROMPT = """你是一个数据结构可视化教学助教，面向正在准备技术面试的学习者。
回答原则：
1. 优先依据【当前数据结构真实状态】作答——它是屏幕上真实的节点与结构，是最高事实来源；【检索资料】作为原理补充。两者冲突时以真实状态为准。
2. 严格依据资料与真实状态，不要编造资料/状态以外的知识点或伪造成功/失败案例。
3. 如果真实状态/检索资料不足以回答，坦诚说明“根据现有资料，无法回答该问题”，不要硬编。
4. 用中文，简洁、有结构（必要时用步骤/要点），面向“面试怎么答”讲清原理与触发条件。
5. 若回答涉及图里的具体节点，在 highlight_nodes 给出这些节点的整数值。
6. 若某条【检索资料】与用户问题无关，请直接忽略，不要据此作答；不要把不相关的资料当作答案依据，也不要为了凑内容而引用它。
7. 若用户明确要求“跳到/演示/查看/切换到”另一个数据结构，可在 JSON 里附加 actions：[{"type":"jump","structure":"<结构名>"}]。可用结构名（严格区分大小写）：SinglyLinkedList, DoublyLinkedList, Stack, Queue, BinarySearchTree, AVLTree, HashMap, MinHeap, RedBlackTree, Deque, BlockingQueue, BTree, BPlusTree, RingBuffer, Graph, LRUCache。仅当用户主动要求切换时才使用，不要主动跳转。
8. 若用户明确要求“演示/分步讲解/逐步演示/动画演示”某个数据结构的操作，或问题中出现“按顺序/依次/顺序”等明显要观察过程的词（如“演示 AVL 树插入并解释旋转”“逐步讲解红黑树删除”“动画演示栈的 push/pop”“按顺序插入 12,3,9,18,5”），**必须在 actions 中返回 step_explain，禁止只给文字解释**。structure 为要演示的结构（与当前不同会自动切换）；steps 为依次执行的操作序列，op 取值：insert/find/remove/pushFront/pushBack/popFront/popBack/addVertex/addEdge/bfs/dfs/dijkstra，value 为操作值（无值操作如 remove/popFront 用空字符串 ""）。**若用户没有给出具体数值，你必须自行选择 3-5 个能演示该知识点的典型数值**；若用户给出多个数值（如“按顺序插入 12,3,9,18,5”），则必须把每个数值拆成一个 step，按顺序放入 steps，例如："按顺序插入 12,3,9,18,5" → [{"op":"insert","value":"12"},{"op":"insert","value":"3"},{"op":"insert","value":"9"},{"op":"insert","value":"18"},{"op":"insert","value":"5"}]。例如：演示 AVL 右旋用 30,20,10；左旋用 10,20,30；左右双旋用 30,10,20；红黑树插入触发旋转用 10,20,30；栈 push/pop 用 10,20,30,20。steps 不能为空。
9. 若用户问题包含明确操作词 + 可选具体数值，且**没有**要求"演示/分步/逐步/动画/讲解/按顺序/依次"，则**必须在 actions 中返回 run_operation，禁止只给文字解释**。常见操作词：插入、删除、查找、push、pop、pushFront、pushBack、popFront、popBack、addVertex、addEdge、bfs、dfs、dijkstra。示例："在 AVL 树里插入 42" → [{"type":"run_operation","structure":"AVLTree","op":"insert","value":"42"}]；"push 5" → [{"type":"run_operation","op":"push","value":"5"}]；"删除 10" → [{"type":"run_operation","op":"remove","value":"10"}]。structure 仅在目标结构与当前结构不同才填（前端会自动先切换），相同则可省略。run_operation 用于"立刻执行单个操作"，与 step_explain 的"分步讲解"区分：用户要"演示/讲解步骤/按顺序看过程"用 step_explain，要"直接做某操作"用 run_operation。
10. **分析类操作问题**：若用户问"插入 8 会导致什么/会怎样/为什么/分析"等，他想要的是**该操作的影响、原理或历史过程分析**，不是让你现在执行这个操作。请基于【当前数据结构真实状态】作答：如果当前状态已经包含该操作结果（如树中已有这个值），则解释从操作前到当前状态的历史变换（包括旋转、高度变化、遍历路径等）；如果当前状态不包含该操作结果，则分析 hypothetical 执行该操作后会产生什么变化。只需输出文字讲解和 highlight_nodes，**不要返回 run_operation 或 step_explain actions**。"""


# ⚠️ 普通字符串（非 f-string、非 .format），其中的 { } 是 JSON 示例的合法字符，
# 必须保持单引号包裹、绝不能放进会被求值的模板里，否则触发 "Invalid format specifier" 运行时错误。
JSON_INSTRUCTION = '请只输出 JSON，格式：{"answer": "你的讲解", "highlight_nodes": [涉及的整数节点值...], "sources": ["资料来源文件名..."], "actions": []}。其中 actions 规则：① 用户要求切换结构时填 [{"type":"jump","structure":"结构名"}]；② 用户要求分步/逐步/动画演示时**必须**填 [{"type":"step_explain","structure":"结构名","steps":[...]}]，steps 不能为空，且用户未给数值时你要自行选择典型序列；③ 用户给出明确操作词+数值（如"插入 42""push 5""删除 10"）且未要求分步演示时**必须**填 [{"type":"run_operation","structure":"结构名","op":"insert","value":"42"}]（structure 仅目标结构≠当前时填，op 取值同②，value 无值用空串），用于立刻执行。不需要动作时才留空数组 []。'


def _text_of(h):
    """兼容 Hit 对象与纯 dict 两种 hit，取 child 文本。"""
    t = getattr(h, "text", None)
    if t is None and isinstance(h, dict):
        t = h.get("text", "")
    return t or ""


# _passage_text 已内联为 _text_of（review S12：中间人透传，无附加逻辑）


# 操作词（与 run_hint 保持一致）
_OPERATION_RE = re.compile(
    r"(插入|删除|查找|push|pop|pushFront|pushBack|popFront|popBack|addVertex|addEdge|bfs|dfs|dijkstra)\s*(\d+)",
    re.IGNORECASE,
)

# 分析类语气词：出现这些词说明用户要"影响/原理/过程/结果"，不是执行。
_ANALYZE_KWS = (
    "会导致", "会怎样", "会发生什么", "为什么", "分析", "解释", "原理", "过程", "结果",
    "后果", "之后", "走势", "变化", "影响", "怎么", "变成",
    "会旋转", "会失衡", "会变化", "会变", "会触发",
)

# —— 意图关键词单一来源（review S7/S15）——
# 此前演示词表在 build_prompt 里还有一份内联拷贝（且已分叉：多了"顺序"），
# 现合并为唯一一份，关键词集绑定到 Intent 枚举；任何增删只改这里。
_DEMO_KWS = (
    "演示", "分步", "逐步", "动画", "讲解", "按顺序", "依次", "顺序", "walk through", "show me",
)
# 执行词：出现则说明用户要"做"而不是"问影响"，用于排除分析类。
_EXEC_KWS = ("执行", "给我", "走一遍", "看一下")
# 演示/执行词并集：分析类判定的排除集。
_DEMO_EXEC_KWS = _DEMO_KWS + _EXEC_KWS


class Intent(Enum):
    """用户意图四分类（review S15：消除字符串/布尔散落的基本类型偏执）。

    判定优先级：DEMO > ANALYZE > EXECUTE > NONE。
    """
    DEMO = "demo"        # step_explain：演示/分步/按顺序等演示词
    ANALYZE = "analyze"  # 会怎样/为什么/分析：只讲解，不执行（actions 锁死为空）
    EXECUTE = "execute"  # run_operation：操作词+数值，无演示/分析词
    NONE = "none"        # 普通问答


def classify_intent(question):
    """意图分类（唯一入口）。优先级：演示 > 分析 > 执行 > 普通。"""
    q = question
    ql = q.lower()
    # 演示词优先（演示词不 lower 匹配，与历史 build_prompt 行为一致）
    if any(kw in q for kw in _DEMO_KWS):
        return Intent.DEMO
    if not _OPERATION_RE.search(q):
        return Intent.NONE
    has_analyze = any(kw in q for kw in _ANALYZE_KWS)
    has_demo_exec = any(kw in ql for kw in _DEMO_EXEC_KWS)
    if has_analyze and not has_demo_exec:
        return Intent.ANALYZE
    return Intent.EXECUTE


def _is_analyze_operation(question):
    """判断是否为'分析操作影响/原理/历史过程'类问题（classify_intent 的便捷封装）。

    例如："插入 8 会导致什么"、"删除 10 会怎样"、"push 5 之后栈怎么变"。
    反例："插入 8"（执行）、"演示插入 8"（分步）、"在 AVL 树里插入 8"（执行）。
    """
    return classify_intent(question) == Intent.ANALYZE


def _is_arithmetic_only(question):
    """意图分类的正式规则之一：纯算术问题（如 5+3=几、1+1=?）直接拒答。

    这类问题的数字是运算数、不是数据结构节点值，不应触发检索高亮或模型计算。
    归入意图分类体系：与 _is_analyze_operation 平级，由 call_llm 最先判定。
    """
    # 去掉空格、常见疑问词和中文标点
    cleaned = re.sub(r"[等于几是多少多少？?！!，,、；;：:\s]+", "", question)
    # 清理后必须非空，且只含数字（半角/全角）和运算符
    return bool(cleaned) and bool(re.fullmatch(r"[\d０-９\.\+\-\*/%=]+", cleaned))


def build_prompt(question, hits, context, history=None):
    if isinstance(context, dict):
        blocks = []
        if context.get("tree_state"):
            blocks.append("【当前数据结构真实状态（节点值+父子结构，务必以此为准）】\n" + str(context["tree_state"]))
        if context.get("structure"):
            blocks.append("【结构类型】" + str(context["structure"]))
        if context.get("desc"):
            blocks.append("【当前步骤】" + str(context["desc"]))
        if context.get("highlight_ids"):
            blocks.append("【本步涉及节点id】" + str(context["highlight_ids"]))
        for k, v in context.items():
            if k not in ("tree_state", "structure", "desc", "highlight_ids"):
                blocks.append(f"【{k}】{v}")
        ctx_text = "\n\n".join(blocks)
    else:
        ctx_text = context if isinstance(context, str) else json.dumps(context, ensure_ascii=False)

    # 多轮对话历史（窗口由前端裁剪并 trim，后端直接使用收到的 history，不再自行截断——review S13 单一所有权）
    history_text = ""
    if history:
        items = []
        for h in history:
            if not isinstance(h, dict):
                continue
            q = (h.get("question") or "").strip()
            a = (h.get("answer") or "").strip()
            if q or a:
                items.append(f"Q: {q}\nA: {a}")
        if items:
            history_text = (
                "【对话历史（最近若干轮，仅用于理解用户追问中的指代，如“它/这个/刚才说的”；"
                "历史答案可能过时或不完整，请以“检索资料”和“当前可视化上下文”为准】\n"
                + "\n\n".join(items)
            )

    knowledge = "\n\n".join(
        f"[资料 {i+1} | {h.metadata.get('source','')} | {h.metadata.get('structure','')}]\n{_text_of(h)}"
        for i, h in enumerate(hits)
    )
    # 检索质量 → 动态指令（忠实度防线）
    best = _best_score(hits)
    if not hits:
        grounding = "【未找到任何相关资料。必须直接回答：当前知识库未覆盖此问题。严禁使用自身知识作答。】"
    elif best < HARD_REJECT_FLOOR:
        grounding = "【未找到任何有效相关资料。必须直接回答：当前知识库未覆盖此问题。严禁使用自身知识作答。】"
    elif best < WARN_FLOOR:
        grounding = "【检索资料相关性较低。请严格仅依据以下资料作答，资料不足时声明未覆盖，禁止补充自身知识。】"
    else:
        grounding = ""
    # 意图分类（单一入口 classify_intent；review S7：删除内联关键词拷贝，防再分叉）
    intent = classify_intent(question)
    # 演示类请求：动态再强调一次，防止模型只文字解释而不生成 step_explain actions
    demo_hint = ""
    if intent == Intent.DEMO:
        demo_hint = "【用户要求分步演示/按顺序观察过程，必须在 actions 中返回 step_explain；steps 不能为空。若用户没有给出具体数值，请自行选择 3-5 个典型数值；若用户给出多个数值（如“插入 12,3,9,18,5”），必须把每个数值拆成一个 step 按顺序放入 steps。】\n"
    # 分析类操作请求：问"插入8会导致什么/会怎样/为什么"——要原理/历史过程，不是执行。
    analyze_hint = ""
    if intent == Intent.ANALYZE:
        analyze_hint = (
            "【用户问的是某个操作会造成什么影响/结果/原理，属于分析类问题，不是要求执行该操作。"
            "请基于当前真实状态回答：若当前状态已包含该操作结果（如树中已有该值），则解释从操作前到当前状态的历史变换过程（包括旋转、高度变化、遍历路径等）；"
            "若当前状态不包含该操作结果，则分析 hypothetical 执行该操作后会怎样。"
            "不要返回 run_operation 或 step_explain actions，只需文字讲解 + highlight_nodes。】\n"
        )
    # 直接执行类请求：问题含操作词+数值，且未要求分步演示、且不是分析类 → 必须 run_operation
    run_hint = ""
    if intent == Intent.EXECUTE:
        run_hint = "【用户要求直接执行某个具体操作（含操作词和数值），必须在 actions 中返回 run_operation，禁止只给文字解释。】\n"
    # 注意：JSON 示例说明必须是普通字符串（非 f-string），否则其中的 { } 会被当成形
    # 式字段解析，导致 "Invalid format specifier" 运行时错误。仅下面的 6 个动态字段走 f-string。
    return f"""当前可视化上下文：{ctx_text}

{history_text}

{grounding}

{demo_hint}{analyze_hint}{run_hint}检索资料：
{knowledge}

用户问题：{question}

{JSON_INSTRUCTION}"""


# ----------------------------------------------------------------------------
# Direct Query Rewrite（直接改写）
# ----------------------------------------------------------------------------
# 作用：在检索之前，用【单次】LLM 调用把口语化 / 指代不清 / 上下文丢失的查询，
# 改写成检索友好的规范查询（术语归一 + 上下文补全）。仅用于「向量检索路」，
# 关键词路(BM25)保持原查询不变（它自带同义词扩展兜底，且改写可能丢掉字面词）。
#
# 约束（防止跑偏 / 防止幻觉）：
# - 只做「术语归一」和「上下文补全」，禁止引入资料里没有的新知识点。
# - 输出必须是单行改写查询，不含解释 / 引号 / markdown。
# - 若 LLM 判定无需改写（或任何失败：无 key / 网络 / 模型），一律回退原 query，
#   绝不阻断检索（生成侧忠实度地板照常生效）。
# ----------------------------------------------------------------------------

# 闸门用的「已明确指定结构」关键词（只放具体名，不放「树/堆/图/数组」这类泛词——
# 泛词不构成定位，用户大概率指「当前这个树」，仍需上下文补全）。
_STRUCT_HINTS = [
    "链表", "栈", "队列", "红黑", "avl", "二叉", "b树", "b+", "b+树", "deque",
    "ring", "blocking", "lru", "ufds", "并查", "优先队列", "最小堆", "maxheap",
    "minheap", "hashmap", "hash", "哈希表", "哈希",
]


def _rewrite_needed(question):
    """轻量闸门：已规范的查询（含明确数值操作 / 含已知具体结构名）跳过改写，
    省一次 LLM 调用；口语 / 指代 / 纯概念类才进入改写。"""
    q = question.lower()
    # 明确操作 + 数值（插入42 / push 5 / 删除10）→ 已规范
    if re.search(r"(插入|删除|查找|push|pop|add|remove|insert|find|delete)\s*\d", q):
        return False
    # 已含具体结构名 → 已规范
    for h in _STRUCT_HINTS:
        if h in q:
            return False
    return True


def rewrite_query(question, context=None, api_key="", base_url="", model=""):
    """Direct Query Rewrite：返回（可能改写过的）检索查询字符串。

    失败时原样返回 question，调用方无需额外处理。
    """
    if not api_key or not model:
        return question
    if not _rewrite_needed(question):
        return question

    # 上下文补全：把当前结构 / 步骤告诉模型，让它把省略/指代补全成具体查询
    ctx_bits = []
    if isinstance(context, dict):
        if context.get("structure"):
            ctx_bits.append(f"当前正在查看的数据结构是 {context['structure']}")
        if context.get("desc"):
            ctx_bits.append(f"当前步骤：{context['desc']}")
        if context.get("tree_state"):
            ctx_bits.append("屏幕上已有一个具体的数据结构实例")
    ctx_text = "；".join(ctx_bits) if ctx_bits else "无额外上下文"

    system = (
        "You are a query rewriter for a data-structure visualization RAG system. "
        "Rewrite the user's question into ONE concise, retrieval-friendly query. "
        "Rules: (1) Normalize colloquial terms to canonical data-structure terminology "
        "(e.g. 翻转->旋转/rotate, 加->插入/insert, 搞/弄->操作, 满了/踢谁/挤掉->淘汰/evict, "
        "转来转去->旋转/rotate, 并查集->union-find). "
        "(2) If context provides the current structure or topic, inject it so a "
        "pronoun/ellipsis query becomes concrete (e.g. '这个树的删除' -> 'RedBlackTree delete operation'). "
        "(3) Do NOT invent facts or knowledge beyond what the query and context imply. "
        "(4) Output ONLY the rewritten query on a single line: no quotes, no explanation, no markdown."
    )
    user = (
        f"Context: {ctx_text}\n"
        f"Original query: {question}\n"
        f"Rewritten query:"
    )
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
        }
        req = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rewritten = data["choices"][0]["message"]["content"].strip()
        rewritten = rewritten.strip('"').strip("'").strip("`").strip()
        if rewritten and rewritten.lower() != question.lower():
            print(f"    [rewrite] 查询已改写: {question!r} -> {rewritten!r}", flush=True)
            return rewritten
    except Exception as e:  # noqa: BLE001
        print(f"    [rewrite] 查询改写失败，回退原文检索: {e}", flush=True)
    return question


def _extract_ints(text):
    return [int(x) for x in re.findall(r"\d+", text)]


def _enforce_intent_contract(question, actions):
    """分析类意图锁死：服务端强制剥离 run_operation/step_explain。

    prompt 规则 10 只是软约束，模型可能不守；契约由这里兜底兑现——
    用户问"会怎样/为什么/分析"时，前端绝不收到可执行动作。
    """
    if not _is_analyze_operation(question):
        return actions
    return [a for a in actions
            if not (isinstance(a, dict) and a.get("type") in ("run_operation", "step_explain"))]


def _should_reject(hits, retriever_kind):
    """分路质量门控：是否应硬拒答（不调 LLM）。

    naive 路 BM25 分数是无界 IDF 加权和，0.4/0.55 阈值对它无意义，
    改用检索器算好的 q_match（IDF≥2.5 稀有词至少命中 2 个）；
    vector/hybrid 路保留余弦相似度 0.4 硬拒阈值。
    """
    if retriever_kind == "naive":
        return (not hits) or not any(getattr(h, "q_match", False) for h in hits[:5])
    best = _best_score(hits)
    return (not hits) or best < HARD_REJECT_FLOOR


def _valid_highlights(question, context):
    """highlight_nodes 后端校验：只返回真实存在于当前结构中的节点值。

    从 context.tree_state 提取真实节点值集合，与问题中抽取的整数求交。
    无 tree_state（或为空）时交集为空 —— 宁缺毋滥，绝不高亮不存在的节点。
    契约由后端兑现，前端的静默跳过仅作防御纵深。
    """
    tree_state = ""
    if isinstance(context, dict):
        tree_state = str(context.get("tree_state", "") or "")
    real_nodes = set(_extract_ints(tree_state))
    return [v for v in _extract_ints(question) if v in real_nodes]


def call_llm(question, hits, context, provider="offline", api_key="", base_url="", model="", temperature=0.3, history=None, retriever_kind="vector"):
    # 算术问题拦截：数字是运算数，不是节点值，不应触发高亮或模型计算。
    if _is_arithmetic_only(question):
        return (
            "当前知识库未覆盖此问题。\n"
            "建议：尝试更具体的问法，或查阅对应教材章节。",
            [],
            [],
            [],
        )

    # 硬兜底：空检索/低相关 → 直接拒答，不调 LLM。按检索路分门控（详见 _should_reject）。
    if _should_reject(hits, retriever_kind):
        return (
            "当前知识库未覆盖此问题。\n"
            "建议：尝试更具体的问法，或查阅对应教材章节。",
            _valid_highlights(question, context),
            [],
            [],
        )
    if provider != "offline" and api_key:
        ans, hl, src, actions = _call_openai(question, hits, context, api_key, base_url, model, temperature, history)
        if not ans.startswith("[LLM 调用失败"):
            # 分析类意图锁死（服务端强制兑现契约，不信任模型自觉遵守 prompt）
            actions = _enforce_intent_contract(question, actions)
            return ans, hl, src, actions
        # API 调用失败（key 无效 / 网络不可达 / 参数不支持）→ 降级为离线拼接，至少把检索资料给用户
        print(f"[WARN] openai 调用失败，降级为离线拼接答案。原因：{ans}", flush=True)

    # 离线兜底：直接把检索到的资料拼接成答案（已通过顶部相关性闸门，必为相关命中）
    top = hits[:3]
    parts = []
    for h in top[:2]:
        src = h.metadata.get("source", "")
        parts.append(f"· ({src}) {h.text[:1200]}")
    answer = "【离线模式·检索到的资料】\n\n" + "\n\n".join(parts)
    highlight = _valid_highlights(question, context)
    sources = [h.metadata.get("source", "") for h in top]
    return answer, highlight, sources, []


def _parse_content(content):
    """把模型返回的 content 解析成 dict（容忍外层 ```json 围栏）。"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1]
        if content.lower().startswith("json"):
            content = content[4:]
    return json.loads(content)


def _do_chat_request(payload, api_key, base_url):
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    obj = _parse_content(content)
    return (obj.get("answer", ""),
            obj.get("highlight_nodes", []),
            obj.get("sources", []),
            obj.get("actions", []))


def _call_openai(question, hits, context, api_key, base_url, model, temperature=0.3, history=None):
    prompt = build_prompt(question, hits, context, history)
    base_payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    # 优先带 JSON 模式；若 DashScope 因 response_format 参数拒绝（部分模型/chat 端点不支持），
    # 自动去掉该参数重试（prompt 已强约束只输出 JSON，且 _parse_content 会剥离 ```json 围栏）。
    attempts = [
        {**base_payload, "response_format": {"type": "json_object"}},
        base_payload,
    ]
    last_err = None
    for idx, payload in enumerate(attempts):
        try:
            ans, hl, src, actions = _do_chat_request(payload, api_key, base_url)
            if not ans.startswith("[LLM 调用失败"):
                return ans, hl, src, actions
            # _do_chat_request 内部已返回失败标记，直接降级
            print(f"[WARN] openai 返回失败标记，降级为离线拼接答案。原因：{ans}", flush=True)
        except urllib.error.HTTPError as e:  # noqa: BLE001
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:  # noqa: BLE001
                pass
            print(f"    [openai HTTPError] attempt={idx+1} status={e.code} body={body}", flush=True)
            last_err = f"HTTP {e.code} {body}"
            # 若是最后一次尝试（已是不带 response_format 的兜底）仍失败，则放弃
            if idx == len(attempts) - 1:
                return f"[LLM 调用失败：{last_err}]", _extract_ints(question), [], []
            # 否则继续下一次（去掉 response_format 重试）
            continue
        except Exception as e:  # noqa: BLE001
            print(f"    [openai error] attempt={idx+1} {type(e).__name__}: {e}", flush=True)
            last_err = str(e)
            if idx == len(attempts) - 1:
                return f"[LLM 调用失败：{last_err}]", _extract_ints(question), [], []
            continue
    return f"[LLM 调用失败：{last_err}]", _extract_ints(question), [], []
