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


# retriever: naive(零依赖, 开箱即跑) | chroma(生产, 需 chromadb + sentence-transformers)
RETRIEVER = _env("RETRIEVER", "naive")
# llm: offline(无 key 也能跑, 规则拼接) | openai(真实大模型)
LLM_PROVIDER = _env("LLM_PROVIDER", "offline")
OPENAI_API_KEY = _env("OPENAI_API_KEY", "")
OPENAI_BASE_URL = _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
PORT = int(_env("PORT", "8000"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_PATH = os.path.join(BASE_DIR, "naive_index.pkl")
