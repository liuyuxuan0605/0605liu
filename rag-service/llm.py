"""LLM 调用层。

- offline：无 API key 也能跑，用检索到的资料规则拼接答案，并从问题中
  抽取整数作为高亮节点值（用于演示完整链路）。
- openai：调用 OpenAI 兼容接口，要求返回 JSON（answer / highlight_nodes / sources）。
"""
import re
import json
import urllib.request

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
3. 如果真实状态/检索资料不足以回答，坦诚说明“资料/状态里没讲清楚这部分”，不要硬编。
4. 用中文，简洁、有结构（必要时用步骤/要点），面向“面试怎么答”讲清原理与触发条件。
5. 若回答涉及图里的具体节点，在 highlight_nodes 给出这些节点的整数值。
6. 若某条【检索资料】与用户问题无关，请直接忽略，不要据此作答；不要把不相关的资料当作答案依据，也不要为了凑内容而引用它。
7. 若用户明确要求“跳到/演示/查看/切换到”另一个数据结构，可在 JSON 里附加 actions：[{"type":"jump","structure":"<结构名>"}]。可用结构名（严格区分大小写）：SinglyLinkedList, DoublyLinkedList, Stack, Queue, BinarySearchTree, AVLTree, HashMap, MinHeap, RedBlackTree, Deque, BlockingQueue, BTree, BPlusTree, RingBuffer, Graph, LRUCache。仅当用户主动要求切换时才使用，不要主动跳转。
8. 若用户明确要求“演示/分步讲解/逐步演示”某个数据结构的某个操作（如“演示 AVL 树插入并解释旋转”“逐步讲解红黑树删除”），可在 actions 填 [{"type":"step_explain","structure":"<结构名>","steps":[{"op":"insert","value":"30"},{"op":"insert","value":"20"},{"op":"insert","value":"10"}]}]。structure 为要演示的结构（与当前不同会自动切换）；steps 为依次执行的操作序列，op 取值：insert/find/remove/pushFront/pushBack/popFront/popBack/addVertex/addEdge/bfs/dfs/dijkstra，value 为操作值（无值操作如 remove/popFront 用空字符串 ""）。仅当用户明确要求分步演示时才使用，且 steps 应选能演示你想讲的知识点（如“讲解旋转”就插入会触发旋转的序列）。"""


def build_prompt(question, hits, context):
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
    knowledge = "\n\n".join(
        f"[资料 {i+1} | {h.metadata.get('source','')} | {h.metadata.get('structure','')}]\n{h.text}"
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
    return f"""当前可视化上下文：{ctx_text}

{grounding}

检索资料：
{knowledge}

用户问题：{question}

请只输出 JSON，格式：{{"answer": "你的讲解", "highlight_nodes": [涉及的整数节点值...], "sources": ["资料来源文件名..."], "actions": []}}。其中 actions 可选，支持两种：① 用户要求切换结构时填 [{"type":"jump","structure":"结构名"}]；② 用户要求分步演示操作时填 [{"type":"step_explain","structure":"结构名","steps":[{"op":"insert","value":"30"},...]}]。不需要动作时留空数组 []。"""


def _extract_ints(text):
    return [int(x) for x in re.findall(r"\d+", text)]


def _is_arithmetic_only(question):
    """检测是否纯算术问题（如 5+3=几、1+1=?）。
    这类问题的数字是运算数，不是数据结构节点值，应直接拒答、不高亮。"""
    # 去掉空格、常见疑问词和中文标点
    cleaned = re.sub(r"[等于几是多少多少？?！!，,、；;：:\s]+", "", question)
    # 清理后必须非空，且只含数字（半角/全角）和运算符
    return bool(cleaned) and bool(re.fullmatch(r"[\d０-９\.\+\-\*/%=]+", cleaned))


def call_llm(question, hits, context, provider="offline", api_key="", base_url="", model=""):
    # 算术问题拦截：数字是运算数，不是节点值，不应触发高亮或模型计算。
    if _is_arithmetic_only(question):
        return (
            "当前知识库未覆盖此问题。\n"
            "建议：尝试更具体的问法，或查阅对应教材章节。",
            [],
            [],
            [],
        )

    # 硬兜底（跨检索器通用）：空检索或 top 相似度低于硬拒阈值 → 直接拒答，不调 LLM。
    # 不再依赖检索器的 q_match（其在 chroma 下太宽松，0.25 即可通过），改用最高分。
    best = _best_score(hits)
    if not hits or best < HARD_REJECT_FLOOR:
        return (
            "当前知识库未覆盖此问题。\n"
            "建议：尝试更具体的问法，或查阅对应教材章节。",
            _extract_ints(question),
            [],
            [],
        )
    if provider != "offline" and api_key:
        ans, hl, src, actions = _call_openai(question, hits, context, api_key, base_url, model)
        if not ans.startswith("[LLM 调用失败"):
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
    highlight = _extract_ints(question)
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


def _call_openai(question, hits, context, api_key, base_url, model):
    prompt = build_prompt(question, hits, context)
    base_payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
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
