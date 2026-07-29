"""检索器：naive(零依赖关键词) 与 semantic(语义向量检索) 两种实现，统一接口。"""
import os
import glob
import pickle
import math
import re
import json
import urllib.request
import urllib.error

# 相关性阈值：chroma/semantic 的余弦相似度 >= 此值才视为"有相关命中"。
# 用于让 q_match 在向量检索路径上也是真实信号（原先硬编码 True，
# 导致 llm.py 的空检索硬拒闸门在 chroma 下永不触发）。
SIM_RELEVANT = 0.25


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


def _dedup_by_source(hits, k):
    """按来源(source)去重：同一文档的多个 chunk 只保留相似度最高的一条，
    剩下的槽位让给下一个不同来源。避免「同一篇笔记霸占 top-k 全部槽位」
    （实测出现过 notes/b_tree_operations.md 占满 top5 的 5 个槽），提升
    召回多样性，让第 2、3 个相关文档也有机会进 top-k。"""
    seen = set()
    out = []
    for h in hits:
        src = str(h.metadata.get("source", ""))
        if src in seen:
            continue
        seen.add(src)
        out.append(h)
        if len(out) >= k:
            break
    return out


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


def _translate_to_english(text, api_key, base_url, chat_model):
    """把含中文的问题翻译成英文，用于跨语言对齐检索（中文查询 vs 英文知识库）。

    背景：知识库 15/16 篇是 VisuAlgo 英文文档；产品只服务中文提问，
    中文 query 的 embedding 与英文 doc 的 embedding 跨语言弱对齐，
    导致部分相关英文文档排不进 top-k（chroma 评估里的 B 类 MISS）。
    把查询翻成英文再去查英文库，英文对英文对齐最强，直接消除该鸿沟。

    约定：
    - 仅当文本含 CJK 字符才调用翻译；纯英文/无中文直接返回 None（无需翻译）。
    - 翻译失败（网络/key/模型问题）一律回退 None，绝不阻断检索。
    - 复用 DashScope OpenAI 兼容 /chat/completions 端点（与 llm.py 同源），
      纯标准库 urllib，不引入新依赖。
    """
    if not api_key or not chat_model:
        return None
    if not re.search(r"[\u4e00-\u9fff]", text):
        return None
    try:
        payload = {
            "model": chat_model,
            "messages": [
                {"role": "system", "content":
                 "You are a translation engine. Translate the user's text into English. "
                 "Output ONLY the English translation, no explanations, no quotes, no markdown."},
                {"role": "user", "content": text},
            ],
            "temperature": 0.0,
        }
        req = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        en = data["choices"][0]["message"]["content"].strip()
        en = en.strip('"').strip("'").strip("`").strip()
        if en and re.search(r"[A-Za-z]", en):
            return en
    except Exception as e:  # noqa: BLE001
        print(f"    [translate] 中文→英文翻译失败，回退原文检索: {e}", flush=True)
    return None


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

        def _score(filter_struct, topn=k):
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
                # - 教科书《Open Data Structures》(open/ods) 是英文泛参考资料。
                #   产品只服务中文提问：英文页与中文查询存在跨语言弱对齐，且
                #   不是任何已知中文问题的正确答案（离线评估 21 条 query，top5
                #   含 open/ 页 = 0）。故**恒降权 ×0.3**，仅作极低优先级兜底，
                #   绝不允许其盖过 knowledge/notes/generated 的中文文档。
                #   注：早期曾对"无结构过滤"场景 ×1.6 加权，导致英文页在泛话题下
                #   淹没相关文档；现改为恒定降权（仅服务中文，方向不可逆）。
                # 注意 source 在 Windows 上是反斜杠，先统一为正斜杠再判断。
                src_prefix = str(meta.get("source", "")).replace("\\", "/")
                if src_prefix.startswith("interview/"):
                    score *= 0.4
                elif src_prefix.startswith("open/ods"):
                    # 仅服务中文：英文 ODS 页恒降权，不加权。
                    score *= 0.3
                # 仅服务中文：无结构过滤的泛查询里，声明了具体 structure 的文档
                # （如 UFDS / List / Array / Sorting）默认"答非所问"，轻度降权，
                # 避免它抢在真正的通用/对比答案前面（典型：并查集笔记在"链表和数组区别"里占位）。
                # 已指定结构时不做此降权（该文档本就是对应结构的答案）。
                if filter_struct is None and sm:
                    score *= 0.5
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
            return [Hit(t, m, s, b, qm) for s, t, m, b, qm in scored[:topn]]

        # 多取候选再做来源去重，防止同一文档多个 chunk 霸占 top-k
        # （如 ufds.md 曾占满 5 槽中的 3 个）。先取 k*3 候选，去重后取前 k。
        cand = _score(structure, topn=max(k * 3, 20))
        res = _dedup_by_source(cand, k)
        # 严格按结构过滤无结果时，回退到全库检索，保证总有资料可答
        if not res and structure:
            cand = _score(None, topn=max(k * 3, 20))
            res = _dedup_by_source(cand, k)
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
                 data_dir=None, cache_path=None, batch_size=32, chat_model=""):
        import requests
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = embedding_model
        self._requests = requests
        self._chat_model = chat_model
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
        # 跨语言对齐：中文查询翻成英文，英文向量对英文知识库对齐更强；
        # 最终相似度取「中文向量」与「英文向量」两者的最大值，互不丢分。
        qv = self._embed([text])[0]
        en = _translate_to_english(text, self._api_key, self._base_url, self._chat_model)
        qv_en = self._embed([en])[0] if en else None
        if en:
            print(f"    [translate] 中文查询已翻英文检索: {en!r}", flush=True)

        def _sim(vec):
            s = self._cosine(qv, vec)
            if qv_en is not None:
                s = max(s, self._cosine(qv_en, vec))
            return s

        candidates = []
        for i, (vec, st) in enumerate(zip(self._vecs, self._structs)):
            # 结构过滤：给定结构时跳过声明了不同结构的文档；
            # 结构为空/未声明 → 匹配任意（对齐 naive 宽松语义，ODS 通用文档可召回）
            if structure and st and st != structure:
                continue
            sim = _sim(vec)
            candidates.append((sim, i))
        candidates.sort(key=lambda x: -x[0])
        hits = [Hit(self._docs[i][0], self._docs[i][1], float(sim),
                    best_idf=0.0, q_match=sim >= SIM_RELEVANT) for sim, i in candidates]
        hits = _dedup_by_source(hits, k)
        # 结构过滤无结果时回退全库，保证总有资料可答
        if not hits and structure:
            fallback = sorted(
                ((_sim(vec), i) for i, vec in enumerate(self._vecs)),
                key=lambda x: -x[0],
            )
            fb_hits = [Hit(self._docs[i][0], self._docs[i][1], float(sim),
                          best_idf=0.0, q_match=sim >= SIM_RELEVANT) for sim, i in fallback]
            hits = _dedup_by_source(fb_hits, k)
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
                 data_dir=None, persist_dir=None, chat_model=""):
        import requests
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = embedding_model
        self._requests = requests
        self._chat_model = chat_model
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
        count = self._coll.count() or 1
        # 多取一些再按来源去重：同一篇笔记的多个 chunk 会占满 top-k 槽位，
        # 去重后能腾出槽位给第 2、3 个相关文档，提升召回多样性与 recall@k。
        fetch_n = max(1, min(count, k * 3))
        # 跨语言对齐（修复 B 类 MISS）：中文查询翻成英文，英文向量对英文知识库
        # 对齐最强；每个检索阶段都同时用「中文向量」和「英文向量」查一次，再按
        # 来源合并（同来源取相似度更高者），互不丢分。英文翻译失败则退化为纯中文查询。
        qv = self._embed_texts([text])[0]   # 手动嵌入提问向量（中文）
        en = _translate_to_english(text, self._api_key, self._base_url, self._chat_model)
        qv_en = self._embed_texts([en])[0] if en else None
        if en:
            print(f"    [translate] 中文查询已翻英文检索: {en!r}", flush=True)

        def _stage(where):
            # 用中文向量查
            res_zh = self._coll.query(query_embeddings=[qv], n_results=fetch_n, where=where)
            hits = self._to_hits(res_zh)
            # 用英文向量查（若有），按来源合并，取相似度更高者
            if qv_en is not None:
                res_en = self._coll.query(query_embeddings=[qv_en], n_results=fetch_n, where=where)
                hits = self._merge_hits(hits, self._to_hits(res_en))
            return hits  # 不在内层 dedup，留给外层统一合并/截断

        if structure:
            # 结构优先 + 全库补充（修复 #1/#5 跨结构过滤误杀）：
            # 仅用 structure 过滤会把跨结构相关文档整体排除——例如问
            # "Dijkstra 的优先队列是不是最小堆"(struct=Graph) 时，正确答案在
            # sssp.md(SSSP)/heap.md(Heap)/MinHeap.md(MinHeap)，全是 Graph 以外的
            # 标签，被 where={"structure":"Graph"} 挡在门外；同理"图里有没有环"
            # (struct=Graph) 的正确答案 cyclefinding.md(CycleFinding)/
            # dfsbfs.md(GraphTraversal) 也被排除。
            # 改为：结构过滤结果 与 全库结果 按来源合并取最高相似度，再取 top-k。
            # 结构文档因强语义匹配仍居前，跨结构答案也能进 top-k（互不丢分）。
            # 旧 3 阶段里的 "kind=theory 单独阶段" 已被全库检索覆盖，不再需要。
            hits = self._merge_hits(_stage({"structure": structure}), _stage(None))
            return _dedup_by_source(hits, k)
        else:
            return _dedup_by_source(_stage(None), k)

    @staticmethod
    def _merge_hits(a, b):
        """合并两次检索（中文向量 + 英文向量）的结果：按来源(source)去重，
        同一来源取相似度更高者，最终按相似度降序。"""
        best = {}
        for h in a + b:
            src = str(h.metadata.get("source", ""))
            if src not in best or h.score > best[src].score:
                best[src] = h
        return sorted(best.values(), key=lambda h: -h.score)

    @staticmethod
    def _to_hits(res):
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        hits = []
        for d, m, dist in zip(docs, metas, dists):
            sim = 1.0 - (dist if dist is not None else 1.0)  # chroma 返回余弦距离
            hits.append(Hit(d, m, float(sim), best_idf=0.0, q_match=sim >= SIM_RELEVANT))
        return hits


def build_retriever(kind, embedding_model=None, api_key="", base_url="", data_dir=None,
                    chat_model=""):
    """kind: naive(零依赖) | semantic(pickle+内存余弦) | chroma(真·向量数据库)。

    语义/向量模式需要 api_key（调 DashScope embeddings）。若未提供 key，
    自动降级为 NaiveRetriever，保证服务仍可启动（只是检索退化为关键词）。

    chat_model：用于「中文查询→英文」翻译（跨语言对齐检索）。为空则跳过翻译，
    退化为纯中文查询（仍可用，只是英文知识库召回偏弱）。
    """
    if kind == "chroma":
        if not api_key:
            print("[WARN] RETRIEVER=chroma 但未配置 OPENAI_API_KEY，降级为 naive 关键词检索",
                  flush=True)
            return NaiveRetriever()
        return ChromaRetriever(
            api_key=api_key, base_url=base_url,
            embedding_model=embedding_model or "text-embedding-v3",
            data_dir=data_dir, chat_model=chat_model,
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
            data_dir=data_dir, chat_model=chat_model,
        )
    return NaiveRetriever()
