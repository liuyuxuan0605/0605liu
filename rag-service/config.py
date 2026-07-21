import os

# python-dotenv 是可选依赖：naive/offline 零依赖模式下没有它也能跑
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def _env(name, default=""):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


# retriever: naive(零依赖, 开箱即跑) | semantic(语义向量检索, 需 OPENAI_API_KEY 做嵌入)
RETRIEVER = _env("RETRIEVER", "naive")
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_PATH = os.path.join(BASE_DIR, "naive_index.pkl")
# 语义检索向量缓存目录（由 SemanticRetriever 内部维护 semantic_index.pkl）
SEMANTIC_CACHE = os.path.join(BASE_DIR, "semantic_index.pkl")
