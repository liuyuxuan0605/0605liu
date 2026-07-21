"""检索器：naive(零依赖关键词) 与 semantic(语义向量检索) 两种实现，统一接口。"""
import os
import pickle
import math
import re


class Hit:
    def __init__(self, text, metadata, score, best_idf=0.0, q_match=False):
        self.text = text
        self.metadata = metadata
        self.score = score
        # 交集词中的最大 IDF（诊断用）
        self.best_idf = best_idf
        # 查询里那些"在语料中稀有"的词，是否真的被本篇命中。
        # 这是相关性闸门的主依据：能拦掉靠超长文档兜底万能匹配的问题。
        self.q_match = q_match


def _terms(s):
    terms = set()
    for w in re.findall(r"[A-Za-z0-9_]{2,}", s):
        terms.add(w.lower())
    for ch in s:
        if "一" <= ch <= "鿿":
            terms.add(ch)
    return terms


# 查询同义词扩展：中文口语词映射到检索语料里真正出现的词，
# 让"翻转"也能命中写的是"旋转"的笔记，"加"也能命中写"插入"的笔记。
_SYNONYMS = {
    "翻转": ["旋转", "rotate", "左旋", "右旋", "双旋"],
    "旋转": ["翻转", "rotate", "左旋", "右旋", "双旋"],
    "加": ["插入", "insert"],
    "加入": ["插入", "insert"],
    "添加": ["插入", "insert"],
    "插入": ["旋转", "加"],
    "左旋": ["旋转", "翻转", "rotate"],
    "右旋": ["旋转", "翻转", "rotate"],
    "双旋": ["旋转", "翻转", "rotate"],
    "叔叔": ["叔节点", "uncle"],
    "红红": ["红红冲突", "recolor"],
    "重新着色": ["recolor", "旋转"],
}


def _expand_terms(s):
    terms = _terms(s)
    for trigger, adds in _SYNONYMS.items():
        if trigger in s:
            for a in adds:
                terms |= _terms(a)
    return terms


def _detect_topic(text):
    """从问题里粗判数据结构话题，用于同话题笔记加权。"""
    t = text.lower()
    if "红黑" in text or "redblack" in t or "red-black" in t or " rb" in t or t.startswith("rb"):
        return "RedBlackTree"
    if "avl" in t:
        return "AVLTree"
    return ""


class BaseRetriever:
    def add(self, chunks):
        raise NotImplementedError

    def query(self, text, k=4, structure=None):
        raise NotImplementedError

    def count(self):
        """已索引的文档数；语义模式用于判断是否需重建（缓存命中则跳过嵌入）。"""
        return 0

    def save(self, path):
        raise NotImplementedError

    def load(self, path):
        raise NotImplementedError


class NaiveRetriever(BaseRetriever):
    """纯标准库 TF-IDF 风格打分 + pickle 持久化，无需任何第三方依赖。

    IDF 加权：稀有词（红黑树 / 着色 / 旋转 / 哈希 …）权重高，
    超高频字（的 / 是 / 数据 / 节点 …）权重≈0，避免通用文档靠
    共享常用字胜出，让真正相关的专业文档排到前面。
    """

    def __init__(self):
        self.docs = []   # list of (terms_set, text, metadata)
        self._df = {}    # term -> document frequency
        self._N = 0

    def add(self, chunks):
        for c in chunks:
            self.docs.append((c["terms"], c["text"], c["metadata"]))
        self._build_df()

    def _build_df(self):
        self._N = len(self.docs)
        df = {}
        for terms, _, _ in self.docs:
            for t in terms:
                df[t] = df.get(t, 0) + 1
        self._df = df

    def _idf(self, t):
        # 平滑 IDF：越稀有的词权重越大
        return math.log((self._N + 1) / (self._df.get(t, 0) + 1)) + 1.0

    def query(self, text, k=4, structure=None):
        q = _expand_terms(text)
        topic = _detect_topic(text)

        def _score(filter_struct):
            scored = []
            for terms, txt, meta in self.docs:
                sm = meta.get("structure", "")
                # 元数据未声明结构类型的文档，视为可匹配任意结构
                if filter_struct and sm and sm != filter_struct:
                    continue
                inter = q & terms
                if not inter:
                    continue
                # IDF 加权求和
                score = sum(self._idf(t) for t in inter)
                # 来源加权：
                # - 面试口语笔记（interview/）含大量常见中文词，容易蹭分胜出，
                #   进一步降权，避免它盖过更专业的文档；
                # - 教科书《Open Data Structures》(open/ods) 是权威来源，适当加权，
                #   让中文提问也能召回这本英文书的内容。
                # 注意 source 在 Windows 上是反斜杠，先统一为正斜杠再判断。
                src_prefix = str(meta.get("source", "")).replace("\\", "/")
                if src_prefix.startswith("interview/"):
                    score *= 0.4
                elif src_prefix.startswith("open/ods"):
                    score *= 1.6
                # 话题加权：问题明显指向某类结构（红黑树 / AVL）时，
                # 同话题笔记再加成，避免被"旋转"这个通用词拉来别的树的笔记。
                if topic and sm == topic:
                    score *= 1.3
                best_idf = max((self._idf(t) for t in inter), default=0.0)
                # 相关性闸门依据：查询里"语料稀有"的词，至少命中 2 个才算相关。
                # 单字命中太松——超长《面试逐字稿》几乎能撞上任意稀有字变成万能兜底。
                rare_hits = sum(1 for t in inter if self._idf(t) >= 2.5)
                q_match = rare_hits >= 2
                scored.append((score, txt, meta, best_idf, q_match))
            scored.sort(key=lambda x: -x[0])
            return [Hit(t, m, s, b, qm) for s, t, m, b, qm in scored[:k]]

        res = _score(structure)
        # 严格按结构过滤无结果时，回退到全库检索，保证总有资料可答
        if not res and structure:
            res = _score(None)
        return res

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump({"docs": self.docs, "df": self._df, "N": self._N}, f)

    def load(self, path):
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if isinstance(obj, dict):
            self.docs = obj["docs"]
            self._df = obj.get("df", {})
            self._N = obj.get("N", len(self.docs))
        else:
            # 兼容旧格式（仅存 docs 列表）
            self.docs = obj
            self._build_df()

    def count(self):
        return len(self.docs)


class SemanticRetriever(BaseRetriever):
    """语义检索（生产级，零重依赖）：

    - 嵌入：调用 DashScope（通义千问）OpenAI 兼容的 /embeddings 接口
      （text-embedding-v3），把知识库与提问都转成向量。
    - 检索：本地纯 Python 余弦相似度（不依赖 numpy/chromadb/torch）。
    - 缓存：向量落盘到 semantic_index.pkl；首次启动嵌入一次（按批调 API），
      之后重启若 data/ 无更新则直接复用缓存，不再耗 API 调用。
    - 结构过滤：对齐 naive 的宽松语义（structure 空=匹配任意），给定结构时精确过滤。

    选择这套而不是 chromadb/sentence-transformers 的原因：本机环境装不动
    torch/chromadb（网络/超时限制），而用户已有 DashScope key 且本就联网，
    用 API 做嵌入既省本地算力、又与 chat 厂商解耦，效果等价于语义向量检索。
    """

    def __init__(self, api_key, base_url, embedding_model="text-embedding-v3",
                 data_dir=None, cache_path=None, batch_size=32):
        import requests
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = embedding_model
        self._requests = requests
        self._batch = batch_size
        self._data_dir = data_dir
        self._cache_path = cache_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "semantic_index.pkl"
        )
        # 内存态：docs(text,meta) / vecs / structs
        self._docs = []
        self._vecs = []
        self._structs = []
        self._try_load()

    # ---------- 嵌入（DashScope /embeddings） ----------
    def _embed_one_batch(self, texts):
        payload = {"model": self._model, "input": texts}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        last_err = None
        for attempt in range(3):
            try:
                resp = self._requests.post(
                    self._base_url + "/embeddings",
                    json=payload, headers=headers, timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                order = sorted(data.get("data", []), key=lambda d: d["index"])
                return [d["embedding"] for d in order]
            except Exception as e:  # noqa: BLE001
                last_err = e
        raise RuntimeError(f"embedding API 调用失败（{self._model}）: {last_err}")

    def _embed(self, texts):
        out = []
        for i in range(0, len(texts), self._batch):
            batch = texts[i:i + self._batch]
            try:
                out.extend(self._embed_one_batch(batch))
            except Exception:  # noqa: BLE001
                # 单批失败（可能该模型不接受数组 input）→ 逐条重试，保证不整体崩
                if len(batch) > 1:
                    for t in batch:
                        out.extend(self._embed_one_batch([t]))
                else:
                    raise
        return out

    # ---------- 索引 / 缓存 ----------
    def _cache_is_stale(self):
        if not os.path.exists(self._cache_path):
            return True
        cache_mtime = os.path.getmtime(self._cache_path)
        if not self._data_dir:
            return False
        for sub in ("interview", "notes", "generated", "open"):
            d = os.path.join(self._data_dir, sub)
            if not os.path.isdir(d):
                continue
            for fp in glob.glob(os.path.join(d, "*.md")):
                if os.path.getmtime(fp) > cache_mtime:
                    return True
        return False

    def _try_load(self):
        if not os.path.exists(self._cache_path) or self._cache_is_stale():
            return
        try:
            with open(self._cache_path, "rb") as f:
                obj = pickle.load(f)
            self._docs = obj["docs"]
            self._vecs = obj["vecs"]
            self._structs = obj.get("structs",
                                    [m.get("structure", "") for _, m in self._docs])
        except Exception:
            # 缓存损坏则作废，交给 add() 重建
            self._docs, self._vecs, self._structs = [], [], []

    def add(self, chunks):
        self._docs = [(c["text"], c["metadata"]) for c in chunks]
        self._structs = [c["metadata"].get("structure", "") for c in chunks]
        texts = [d[0] for d in self._docs]
        self._vecs = self._embed(texts)
        self._save()

    def _save(self):
        with open(self._cache_path, "wb") as f:
            pickle.dump(
                {"docs": self._docs, "vecs": self._vecs, "structs": self._structs},
                f,
            )

    def count(self):
        return len(self._docs)

    # ---------- 检索 ----------
    @staticmethod
    def _cosine(a, b):
        dot = 0.0
        na = 0.0
        nb = 0.0
        for x, y in zip(a, b):
            dot += x * y
            na += x * x
            nb += y * y
        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (na ** 0.5 * nb ** 0.5)

    def query(self, text, k=5, structure=None):
        qv = self._embed([text])[0]
        scored = []
        for i, (vec, st) in enumerate(zip(self._vecs, self._structs)):
            # 结构过滤：给定结构时跳过声明了不同结构的文档；
            # 结构为空/未声明 → 匹配任意（对齐 naive 宽松语义，ODS 通用文档可召回）
            if structure and st and st != structure:
                continue
            sim = self._cosine(qv, vec)
            scored.append((sim, i))
        scored.sort(key=lambda x: -x[0])
        top = scored[:k]
        # 结构过滤无结果时回退全库，保证总有资料可答
        if not top and structure:
            scored = sorted(
                ((self._cosine(qv, vec), i) for i, vec in enumerate(self._vecs)),
                key=lambda x: -x[0],
            )
            top = scored[:k]
        hits = []
        for sim, i in top:
            text_i, meta_i = self._docs[i]
            hits.append(Hit(text_i, meta_i, float(sim), best_idf=0.0, q_match=True))
        return hits


def build_retriever(kind, embedding_model=None, api_key="", base_url="", data_dir=None):
    """kind: naive(零依赖) | chroma/semantic(语义向量检索)。

    语义模式需要 api_key（调 DashScope embeddings）。若未提供 key，
    自动降级为 NaiveRetriever，保证服务仍可启动（只是检索退化为关键词）。
    """
    if kind in ("chroma", "semantic"):
        if not api_key:
            print("[WARN] RETRIEVER=semantic 但未配置 OPENAI_API_KEY，降级为 naive 关键词检索",
                  flush=True)
            return NaiveRetriever()
        return SemanticRetriever(
            api_key=api_key,
            base_url=base_url,
            embedding_model=embedding_model or "text-embedding-v3",
            data_dir=data_dir,
        )
    return NaiveRetriever()
