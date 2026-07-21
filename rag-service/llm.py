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
        # API 调用失败（key 无效 / 网络不可达）→ 降级为离线拼接，至少把检索资料给用户
        print("[WARN] openai 调用失败，降级为离线拼接答案", flush=True)

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


def _call_openai(question, hits, context, api_key, base_url, model):
    prompt = build_prompt(question, hits, context)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        # 部分厂商会在 JSON 外包 ```json 围栏，解析前剥离
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.lower().startswith("json"):
                content = content[4:]
        obj = json.loads(content)
        return obj.get("answer", ""), obj.get("highlight_nodes", []), obj.get("sources", [])
    except Exception as e:  # noqa: BLE001
        return f"[LLM 调用失败：{e}]", _extract_ints(question), []
