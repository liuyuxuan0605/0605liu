import os


def _load_env_file():
    """加载同目录 .env。

    python-dotenv 为可选依赖：若未安装（本机常见），退化为手动解析，
    避免 '.env 存在却因 import 失败被静默忽略' 的坑
    （曾导致配了 key/semantic 却仍 naive+offline）。
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return
    except Exception:
        pass
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            # 去掉成对的引号（' 或 "）
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                v = v[1:-1]
            if k and k not in os.environ:  # 真实环境变量优先，不覆盖
                os.environ[k] = v


_load_env_file()


def _env(name, default=""):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


# retriever: naive(零依赖, 开箱即跑) | semantic(pickle+内存余弦) | chroma(真·向量数据库, 需 OPENAI_API_KEY 做嵌入)
# 默认 chroma：生产架构 = hybrid 双路（向量 + 关键词 BM25 经 RRF 融合）。
# 无 key / chromadb 缺失时经 build_retriever 与 server 降级链自动落到 naive 单路，
# 离线可用性由降级链保证（chroma → semantic → naive），而非靠默认值保守。
RETRIEVER = _env("RETRIEVER", "chroma")
OPENAI_API_KEY = _env("OPENAI_API_KEY", "")
OPENAI_BASE_URL = _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "text-embedding-v3")
# llm: offline(无 key 也能跑, 规则拼接) | openai(真实大模型)
# 若未显式指定 LLM_PROVIDER，但提供了 key，则自动启用 openai，
# 避免“明明配了 key 却还是离线拼接”的困惑。
_LLM_PROVIDER_EXPLICIT = os.environ.get("LLM_PROVIDER") not in (None, "")
LLM_PROVIDER = _env("LLM_PROVIDER", "offline")
if not _LLM_PROVIDER_EXPLICIT and OPENAI_API_KEY:
    LLM_PROVIDER = "openai"
PORT = int(_env("PORT", "8000"))

# 范围收敛开关（review S6）：默认关闭，需要时显式开启。
# QUERY_TRANSLATE：查询中译英跨语言对齐。中文语料（book/ 已隐藏）下是死路，
#   且每次查询白烧一次 LLM 调用；设 RAG_QUERY_TRANSLATE=1 开启。
QUERY_TRANSLATE = _env("RAG_QUERY_TRANSLATE", "0") == "1"
# QUERY_REWRITE：Direct Query Rewrite（口语→规范术语）。设 RAG_QUERY_REWRITE=1 开启。
QUERY_REWRITE = _env("RAG_QUERY_REWRITE", "0") == "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_PATH = os.path.join(BASE_DIR, "naive_index.pkl")
# 语义检索向量缓存目录（由 SemanticRetriever 内部维护 semantic_index.pkl）
SEMANTIC_CACHE = os.path.join(BASE_DIR, "semantic_index.pkl")
