"""检索器：naive(零依赖) 与 chroma(生产) 两种实现，统一接口。"""
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


class BaseRetriever:
    def add(self, chunks):
        raise NotImplementedError

    def query(self, text, k=4, structure=None):
        raise NotImplementedError

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
        q = _terms(text)

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


class ChromaRetriever(BaseRetriever):
    """生产级：chromadb 向量库 + sentence-transformers 嵌入。"""

    def __init__(self, embedding_model, collection="dsv"):
        from chromadb import Client
        from chromadb.config import Settings
        import sentence_transformers

        self._st = sentence_transformers.SentenceTransformer(embedding_model)
        self._client = Client(Settings(anonymized_telemetry=False))
        self._col = self._client.get_or_create_collection(collection)

    def _embed(self, texts):
        return self._st.encode(texts).tolist()

    def add(self, chunks):
        ids, docs, metas = [], [], []
        for i, c in enumerate(chunks):
            ids.append(f"c{i}")
            docs.append(c["text"])
            metas.append({k: str(v) for k, v in c["metadata"].items()})
        self._col.add(ids=ids, documents=docs, metas=metas)

    def query(self, text, k=4, structure=None):
        emb = self._embed([text])[0]
        where = {"structure": structure} if structure else None
        res = self._col.query(query_embeddings=[emb], n_results=k, where=where)
        hits = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            hits.append(Hit(doc, meta, 1.0 - dist, q_match=True))
        # 结构过滤无结果时回退全库
        if not hits and structure:
            res = self._col.query(query_embeddings=[emb], n_results=k)
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
                hits.append(Hit(doc, meta, 1.0 - dist, q_match=True))
        return hits


def build_retriever(kind, embedding_model=None):
    if kind == "chroma":
        return ChromaRetriever(embedding_model)
    return NaiveRetriever()
