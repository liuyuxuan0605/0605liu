"""检索器：naive(零依赖关键词) 与 semantic(语义向量检索) 两种实现，统一接口。"""
import os
import glob
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
        self._dim = None  # 向量维度，由探针/首次成功嵌入确定，用于单条失败时的零向量对齐
        self._try_load()

    # ---------- 嵌入（DashScope /embeddings） ----------
    def _embed_one_batch(self, texts, timeout=30):
        payload = {"model": self._model, "input": texts}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        last_err = None
        for attempt in range(2):
            try:
                print(f"    · 调 embeddings 接口 (n={len(texts)}, attempt={attempt+1}, timeout={timeout}s)",
                      flush=True)
                resp = self._requests.post(
                    self._base_url + "/embeddings",
                    json=payload, headers=headers, timeout=timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                order = sorted(data.get("data", []), key=lambda d: d["index"])
                return [d["embedding"] for d in order]
            except Exception as e:  # noqa: BLE001
                last_err = e
                print(f"    ! 嵌入接口异常 (attempt {attempt+1}): {type(e).__name__}: {e}", flush=True)
        raise RuntimeError(f"embedding API 调用失败（{self._model}）: {last_err}")

    def _embed(self, texts):
        total = (len(texts) + self._batch - 1) // self._batch
        out = []
        for bi, i in enumerate(range(0, len(texts), self._batch)):
            batch = texts[i:i + self._batch]
            print(f"[embed {bi + 1}/{total}] 提交 {len(batch)} 条文本做向量化", flush=True)
            out.extend(self._embed_with_fallback(batch))
        return out

    def _embed_with_fallback(self, batch):
        """整批嵌入；失败时按原因恢复，保证最终返回与 batch 等长的向量列表。

        - 整批 400（DashScope 对单次请求的文本条数/总 token 有限制）：对半拆分重试，
          自动收敛到该接口能接受的最大批大小，避免退化成逐条慢速。
        - 单条仍失败（如文本超长）：截断到 1500 字符再试；仍失败则补零向量，
          保证 self._vecs 与 self._docs 长度对齐，检索余弦不会错位。
        """
        try:
            return self._embed_one_batch(batch)
        except Exception:  # noqa: BLE001
            if len(batch) <= 1:
                txt = batch[0] if batch else ""
                try:
                    return self._embed_one_batch([txt[:1500]])
                except Exception as e:  # noqa: BLE001
                    print(f"  ! 单条嵌入最终失败，补零向量跳过: {e}", flush=True)
                    dim = self._dim or 0
                    return [[0.0] * dim] if dim else []
            # 整批失败 → 对半拆分，分别重试
            mid = len(batch) // 2
            return self._embed_with_fallback(batch[:mid]) + self._embed_with_fallback(batch[mid:])

    # ---------- 索引 / 缓存 ----------
    def _cache_is_stale(self):
        if not os.path.exists(self._cache_path):
            return True
        cache_mtime = os.path.getmtime(self._cache_path)
        if not self._data_dir:
            return False
        for sub in ("interview", "notes", "generated", "open", "knowledge"):
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

    def _calibrate_batch(self, texts):
        """用真实文档（取最长的若干篇）二分确定 DashScope 单次能接受的最大批大小。

        原因：text-embedding-v3 对单次请求的总 token 有限制，本知识库里长文档
        （ODS 教材整页）多，32 条打包稳定 400、16 条也 400、8 条才过。若不校准，
        每个 32 批次都会先试 32/16 再落到 8，白打一堆 400 且慢。
        用最长文档做样本校准，得到的大小对所有（更短的）文档都安全。
        """
        # 取最长的若干篇做样本（长文档最易触发 token 上限，校准结果对短文档也安全）
        sample_pool = sorted(texts, key=len, reverse=True)[: max(1, self._batch)]
        lo, hi = 1, min(self._batch, len(sample_pool))
        best = 1
        while lo <= hi:
            mid = (lo + hi) // 2
            try:
                self._embed_one_batch(sample_pool[:mid], timeout=15)
                best = mid
                lo = mid + 1
            except Exception:  # noqa: BLE001
                hi = mid - 1
        return max(1, best)

    def add(self, chunks):
        # 若 __init__ 已加载未过期的 pickle 缓存，直接复用，避免每次启动重复调 API 嵌入
        if self._docs and not self._cache_is_stale():
            print(f"reused semantic cache ({len(self._docs)} docs)", flush=True)
            return
        self._docs = [(c["text"], c["metadata"]) for c in chunks]
        self._structs = [c["metadata"].get("structure", "") for c in chunks]
        texts = [d[0] for d in self._docs]
        # 先做一次性连通性/鉴权探针（短超时），避免 17 批全卡在慢网络上无反馈：
        # 若 DashScope 不可达 / key 错 / 模型名错，这里会在 ~30s 内快速失败并给出明确原因，
        # 而不是傻等整轮嵌入（最坏 17 批 × 重试可能卡数十分钟）。
        try:
            print("先做嵌入连通性探针（短超时 15s）...", flush=True)
            probe_vec = self._embed_one_batch(["连通性测试 ping"], timeout=15)[0]
            self._dim = len(probe_vec)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                f"语义嵌入探针失败，请检查 OPENAI_API_KEY / OPENAI_BASE_URL / EMBEDDING_MODEL 是否正确，"
                f"以及本机能否访问 DashScope：{e}"
            )
        # 用最长真实文档校准最大批大小，之后所有批次直接用该大小，避免每批反复试大批次打 400
        self._batch = self._calibrate_batch(texts)
        print(f"校准批大小={self._batch}（DashScope 单次请求上限）", flush=True)
        self._vecs = self._embed(texts)
        self._save()
        print(f"built semantic index via {self._model} ({len(self._docs)} docs)", flush=True)

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


class ChromaRetriever(BaseRetriever):
    """真·向量数据库检索：ChromaDB 持久化 (HNSW) + DashScope 嵌入。

    与 SemanticRetriever（pickle + 内存余弦）的区别：
    - 向量交给 ChromaDB 管理，落盘到 chroma_db/ 目录，重启即加载，
      无需手动维护 semantic_index.pkl 缓存文件；
    - 检索由 Chroma 的 collection.query 完成，并支持原生 metadata 过滤
      （structure），比手写循环更省心；
    - 嵌入仍走 DashScope text-embedding-v3（本机无需 torch/sentence-transformers）。
    """

    def __init__(self, api_key, base_url, embedding_model="text-embedding-v3",
                 data_dir=None, persist_dir=None):
        import requests
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = embedding_model
        self._requests = requests
        self._data_dir = data_dir
        self._persist = persist_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        self._batch = 8
        self._dim = None
        self._coll = None
        self._connect()

    def _connect(self):
        import chromadb
        self._client = chromadb.PersistentClient(path=self._persist)
        self._coll = self._client.get_or_create_collection(
            name="dsvis_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    # ---------- DashScope 嵌入（批处理 + 兜底） ----------
    def _embed_one(self, texts):
        payload = {"model": self._model, "input": texts}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        resp = self._requests.post(
            self._base_url + "/embeddings", json=payload, headers=headers, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        order = sorted(data.get("data", []), key=lambda d: d["index"])
        vecs = [d["embedding"] for d in order]
        if self._dim is None and vecs:
            self._dim = len(vecs[0])
        return vecs

    def _embed_batch_fb(self, batch):
        try:
            return self._embed_one(batch)
        except Exception:  # noqa: BLE001
            if len(batch) <= 1:
                try:
                    return self._embed_one([batch[0][:1500]])
                except Exception as e:  # noqa: BLE001
                    print(f"  ! chroma 单条嵌入失败，补零向量: {e}", flush=True)
                    return [[0.0] * self._dim] if self._dim else []
            mid = len(batch) // 2
            return self._embed_batch_fb(batch[:mid]) + self._embed_batch_fb(batch[mid:])

    def _embed_texts(self, texts):
        if not texts:
            return []
        out = []
        total = (len(texts) + self._batch - 1) // self._batch
        for bi, i in enumerate(range(0, len(texts), self._batch)):
            batch = texts[i:i + self._batch]
            print(f"[chroma embed {bi + 1}/{total}] {len(batch)} 条", flush=True)
            out.extend(self._embed_batch_fb(batch))
        return out

    def _calibrate(self, texts):
        sample = sorted(texts, key=len, reverse=True)[: max(1, min(self._batch, len(texts)))]
        lo, hi = 1, len(sample)
        best = 1
        while lo <= hi:
            mid = (lo + hi) // 2
            try:
                v = self._embed_one(sample[:mid])
                self._dim = len(v[0])
                best = mid
                lo = mid + 1
            except Exception:  # noqa: BLE001
                hi = mid - 1
        self._batch = max(1, best)

    def _data_mtime(self):
        mt = 0.0
        if not self._data_dir:
            return mt
        for sub in ("interview", "notes", "generated", "open", "knowledge"):
            d = os.path.join(self._data_dir, sub)
            if not os.path.isdir(d):
                continue
            for fp in glob.glob(os.path.join(d, "*.md")):
                mt = max(mt, os.path.getmtime(fp))
        return mt

    # ---------- 索引 / 持久化 ----------
    def add(self, chunks):
        # 连通性探针（短超时），key 错/不可达时快速失败，交由 server.py 降级
        try:
            print("chroma 嵌入连通性探针(15s)...", flush=True)
            v = self._embed_one(["连通性测试 ping"])
            self._dim = len(v[0])
            self._calibrate([c["text"] for c in chunks])
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                f"chroma 嵌入探针失败，请检查 OPENAI_API_KEY/OPENAI_BASE_URL/EMBEDDING_MODEL "
                f"及 DashScope 可达性: {e}"
            )
        cur = self._coll.count()
        stale = abs((self._coll.metadata or {}).get("data_mtime", 0.0) - self._data_mtime()) > 1
        if cur > 0 and not stale:
            print(f"reused chroma index ({cur} docs)", flush=True)
            return
        if cur > 0:
            # chromadb 1.5.x 不再接受 delete(where={})（要求至少一个 operator），
            # 改为按 id 删除已有文档后再重建。
            try:
                old_ids = self._coll.get(limit=cur)["ids"]
            except Exception:  # noqa: BLE001
                old_ids = []
            if old_ids:
                self._coll.delete(ids=old_ids)
        ids = [f"c{i}" for i in range(len(chunks))]
        docs = [c["text"] for c in chunks]
        metas = []
        for c in chunks:
            # chromadb 不允许元数据值为 None，先清洗掉 None（转成空串），否则 add 会直接报错
            m = {k: ("" if v is None else v) for k, v in c["metadata"].items()}
            m["structure"] = m.get("structure", "") or ""
            metas.append(m)
        # 手动用 DashScope 算好向量再交给 chroma（不依赖 chroma 的 embedding_function 接口，
        # 规避不同 chroma 版本对自定义 EF 的 name/调用约定差异导致的报错）
        vecs = self._embed_texts(docs)
        self._coll.add(ids=ids, documents=docs, embeddings=vecs, metadatas=metas)
        self._coll.modify(metadata={"data_mtime": self._data_mtime()})
        print(f"built chroma index via {self._model} ({self._coll.count()} docs)", flush=True)

    def count(self):
        try:
            return self._coll.count()
        except Exception:  # noqa: BLE001
            return 0

    # ---------- 检索 ----------
    def query(self, text, k=5, structure=None):
        n = max(1, min(k, self._coll.count() or 1))
        if structure:
            # implementation 文档按当前结构过滤；theory 文档（kind=theory）跨结构始终召回，
            # 让"面试知识点"在任何结构下都能被引用，而不仅局限 DSVisualizer 已可视化的结构。
            where = {"$or": [{"structure": structure}, {"kind": "theory"}]}
        else:
            where = None
        qv = self._embed_texts([text])[0]   # 手动嵌入提问向量
        res = self._coll.query(query_embeddings=[qv], n_results=n, where=where)
        hits = self._to_hits(res)
        # 结构过滤无结果 → 回退全库，保证总有资料可答
        if not hits and structure:
            res = self._coll.query(query_embeddings=[qv], n_results=n)
            hits = self._to_hits(res)
        return hits

    @staticmethod
    def _to_hits(res):
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        hits = []
        for d, m, dist in zip(docs, metas, dists):
            sim = 1.0 - (dist if dist is not None else 1.0)  # chroma 返回余弦距离
            hits.append(Hit(d, m, float(sim), best_idf=0.0, q_match=True))
        return hits


def build_retriever(kind, embedding_model=None, api_key="", base_url="", data_dir=None):
    """kind: naive(零依赖) | semantic(pickle+内存余弦) | chroma(真·向量数据库)。

    语义/向量模式需要 api_key（调 DashScope embeddings）。若未提供 key，
    自动降级为 NaiveRetriever，保证服务仍可启动（只是检索退化为关键词）。
    """
    if kind == "chroma":
        if not api_key:
            print("[WARN] RETRIEVER=chroma 但未配置 OPENAI_API_KEY，降级为 naive 关键词检索",
                  flush=True)
            return NaiveRetriever()
        return ChromaRetriever(
            api_key=api_key, base_url=base_url,
            embedding_model=embedding_model or "text-embedding-v3",
            data_dir=data_dir,
        )
    if kind == "semantic":
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
