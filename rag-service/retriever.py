"""检索器：naive(零依赖) 与 chroma(生产) 两种实现，统一接口。"""
import os
import pickle
import math
import re


class Hit:
    def __init__(self, text, metadata, score):
        self.text = text
        self.metadata = metadata
        self.score = score


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
    """纯标准库 TF 风格打分 + pickle 持久化，无需任何第三方依赖。"""

    def __init__(self):
        self.docs = []  # list of (terms_set, text, metadata)

    def add(self, chunks):
        for c in chunks:
            self.docs.append((c["terms"], c["text"], c["metadata"]))

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
                score = len(inter) / (1.0 + math.sqrt(max(1, len(terms))))
                scored.append((score, txt, meta))
            scored.sort(key=lambda x: -x[0])
            return [Hit(t, m, s) for s, t, m in scored[:k]]

        res = _score(structure)
        # 严格按结构过滤无结果时，回退到全库检索，保证总有资料可答
        if not res and structure:
            res = _score(None)
        return res

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.docs, f)

    def load(self, path):
        with open(path, "rb") as f:
            self.docs = pickle.load(f)


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
            hits.append(Hit(doc, meta, 1.0 - dist))
        # 结构过滤无结果时回退全库
        if not hits and structure:
            res = self._col.query(query_embeddings=[emb], n_results=k)
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
                hits.append(Hit(doc, meta, 1.0 - dist))
        return hits


def build_retriever(kind, embedding_model=None):
    if kind == "chroma":
        return ChromaRetriever(embedding_model)
    return NaiveRetriever()
