"""LLM 调用层。

- offline：无 API key 也能跑，用检索到的资料规则拼接答案，并从问题中
  抽取整数作为高亮节点值（用于演示完整链路）。
- openai：调用 OpenAI 兼容接口，要求返回 JSON（answer / highlight_nodes / sources）。
"""
import re
import json
import urllib.request


def build_prompt(question, hits, context):
    ctx_text = context if isinstance(context, str) else json.dumps(context, ensure_ascii=False)
    knowledge = "\n\n".join(
        f"[资料 {i+1} | {h.metadata.get('source','')} | {h.metadata.get('structure','')}]\n{h.text}"
        for i, h in enumerate(hits)
    )
    return f"""你是一个数据结构可视化教学助教。根据下面的检索资料回答用户问题。
当前可视化上下文：{ctx_text}

检索资料：
{knowledge}

要求：
1. 用中文简洁回答，结合资料。
2. 如果回答中涉及图里的具体节点，请在 highlight_nodes 中给出这些节点的“值”(整数)，例如涉及节点20就写20。
3. 只输出 JSON，格式：{{"answer": "...", "highlight_nodes": [整数...], "sources": ["资料来源文件名"]}}
"""


def _extract_ints(text):
    return [int(x) for x in re.findall(r"\d+", text)]


def call_llm(question, hits, context, provider="offline", api_key="", base_url="", model=""):
    if provider != "offline" and api_key:
        return _call_openai(question, hits, context, api_key, base_url, model)

    # 离线兜底：直接把检索到的资料拼接成答案
    # 相关性闸门：只有"查询里语料稀有的词被真正命中"（h.q_match）才视为相关，
    # 否则老实说"库里没相关的"，拦掉靠超长文档兜底万能匹配的问题。
    top = hits[:3]
    relevant = bool(top) and any(h.q_match for h in top)
    if not relevant:
        answer = ("【离线模式】未在知识库中找到与问题直接相关的内容。"
                  "可切换到 chroma 语义检索或 openai 模式以获得更准的答案。")
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
        "messages": [{"role": "user", "content": prompt}],
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
        obj = json.loads(content)
        return obj.get("answer", ""), obj.get("highlight_nodes", []), obj.get("sources", [])
    except Exception as e:  # noqa: BLE001
        return f"[LLM 调用失败：{e}]", _extract_ints(question), []
