"""LLM 调用层。

- offline：无 API key 也能跑，用检索到的资料规则拼接答案，并从问题中
  抽取整数作为高亮节点值（用于演示完整链路）。
- openai：调用 OpenAI 兼容接口，要求返回 JSON（answer / highlight_nodes / sources）。
"""
import re
import json
import urllib.request


SYSTEM_PROMPT = """你是一个数据结构可视化教学助教，面向正在准备技术面试的学习者。
回答原则：
1. 严格依据下面提供的【检索资料】作答，不要编造资料以外的知识点或伪造成功/失败案例。
2. 如果检索资料不足以回答，坦诚说明“资料里没讲清楚这部分”，不要硬编。
3. 用中文，简洁、有结构（必要时用步骤/要点），面向“面试怎么答”讲清原理与触发条件。
4. 若回答涉及图里的具体节点，在 highlight_nodes 给出这些节点的整数值。"""


def build_prompt(question, hits, context):
    ctx_text = context if isinstance(context, str) else json.dumps(context, ensure_ascii=False)
    knowledge = "\n\n".join(
        f"[资料 {i+1} | {h.metadata.get('source','')} | {h.metadata.get('structure','')}]\n{h.text}"
        for i, h in enumerate(hits)
    )
    return f"""当前可视化上下文：{ctx_text}

检索资料：
{knowledge}

用户问题：{question}

请只输出 JSON，格式：{{"answer": "你的讲解", "highlight_nodes": [涉及的整数节点值...], "sources": ["资料来源文件名..."]}}"""


def _extract_ints(text):
    return [int(x) for x in re.findall(r"\d+", text)]


def call_llm(question, hits, context, provider="offline", api_key="", base_url="", model=""):
    if provider != "offline" and api_key:
        ans, hl, src = _call_openai(question, hits, context, api_key, base_url, model)
        if not ans.startswith("[LLM 调用失败"):
            return ans, hl, src
        # API 调用失败（key 无效 / 网络不可达 / 参数不支持）→ 降级为离线拼接，至少把检索资料给用户
        print(f"[WARN] openai 调用失败，降级为离线拼接答案。原因：{ans}", flush=True)

    # 离线兜底：直接把检索到的资料拼接成答案
    # 相关性闸门：只有"查询里语料稀有的词被真正命中"（h.q_match）才视为相关，
    # 否则老实说"库里没相关的"，拦掉靠超长文档兜底万能匹配的问题。
    top = hits[:3]
    relevant = bool(top) and any(h.q_match for h in top)
    if not relevant:
        answer = ("【离线模式】未在知识库中找到与问题直接相关的内容。"
                  "可切换到 semantic 语义检索或 openai 模式以获得更准的答案。")
    else:
        parts = []
        for h in top[:2]:
            src = h.metadata.get("source", "")
            parts.append(f"· ({src}) {h.text[:1200]}")
        answer = "【离线模式·检索到的资料】\n\n" + "\n\n".join(parts)
    highlight = _extract_ints(question)
    sources = [h.metadata.get("source", "") for h in top]
    return answer, highlight, sources


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
    return obj.get("answer", ""), obj.get("highlight_nodes", []), obj.get("sources", [])


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
            return _do_chat_request(payload, api_key, base_url)
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
                return f"[LLM 调用失败：{last_err}]", _extract_ints(question), []
            # 否则继续下一次（去掉 response_format 重试）
            continue
        except Exception as e:  # noqa: BLE001
            print(f"    [openai error] attempt={idx+1} {type(e).__name__}: {e}", flush=True)
            last_err = str(e)
            if idx == len(attempts) - 1:
                return f"[LLM 调用失败：{last_err}]", _extract_ints(question), []
            continue
    return f"[LLM 调用失败：{last_err}]", _extract_ints(question), []
