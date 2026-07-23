# DSVisualizer · RAG 智能助教服务

> 本文档说明 `rag-service/` 这个后端服务的**功能、架构、配置、接口与排错**。
> 它是 DSVisualizer（数据结构可视化工具）的「AI 导师」问答后端：你在界面上看某个数据结构、问一个问题，它检索本地知识库 + 调用大模型，返回带讲解、可高亮节点的答案。

---

## 1. 它解决什么问题

DSVisualizer 能把各种数据结构（链表 / 栈 / 队列 / BST / AVL / 红黑树 / 堆 / 哈希表 / B / B+ 树……）的**插入、删除、旋转、分裂、合并**等操作拆成微步骤，逐步动画演示。

但它本身只负责「演示」，不解释「为什么」。RAG 后端补上这一环：

- 前端把 **「当前正在看哪个数据结构」+「用户问题」** 发给后端；
- 后端从**本地知识库**（代码实现 + VisuAlgo 理论讲解）里检索最相关的资料片段；
- 调大模型（OpenAI 兼容 / DashScope）基于这些资料生成**面向面试的中文讲解**，并给出要在图上高亮的节点值。

---

## 2. 整体架构

```
┌──────────────┐      POST /ask       ┌──────────────────────────────┐
│  DSVisualizer │ ───────────────────▶ │   rag-service (http.server)   │
│  (Qt 前端)    │                      │                              │
│              │ ◀─────────────────── │  server.py                   │
│  展示答案+高亮 │   {answer, hl, src}  │    ├─ retriever  (检索)        │
└──────────────┘                      │    ├─ llm        (生成)        │
                                      │    ├─ chunks     (切片)        │
                                      │    └─ config     (配置)        │
                                      └──────────────────────────────┘
                                                │
                                                ▼
                                   data/  (知识库: *.md)
                                   ├─ interview/  notes/  generated/
                                   ├─ open/        (ODS 教材)
                                   └─ knowledge/   (VisuAlgo 理论, kind=theory)
```

**零框架依赖**：整个服务只用 Python 标准库（`http.server` / `urllib` / `pickle`），外加两个按需导入的第三方库：

- `requests`：调用 DashScope 的 `/embeddings` 与 `/chat/completions`（只有 semantic / chroma / openai 模式才需要）。
- `chromadb`：仅 chroma 检索模式需要。

`naive` 检索 + `offline` 生成模式下**完全离线可用**，开箱即跑。

---

## 3. 检索模式（三种）

通过 `.env` 的 `RETRIEVER` 选择，失败会自动降级：

| 模式 | 依赖 | 原理 | 何时用 |
|------|------|------|--------|
| `naive` | 无 | 标准库 TF-IDF 风格关键词打分 + pickle 缓存 | 零配置、离线、快速验证 |
| `semantic` | `requests` + API key | DashScope 嵌入成向量 + **本地纯 Python 余弦**（不依赖 numpy/chromadb），向量落盘 `semantic_index.pkl` | 想要语义相关性、但本机装不动 torch/chromadb |
| `chroma` ✅（当前推荐） | `chromadb` + `requests` + API key | **真·向量数据库**（ChromaDB HNSW 持久化） + DashScope 嵌入，检索走 `collection.query` 原生 metadata 过滤 | 生产级语义检索，支持跨文档 metadata 过滤 |

**降级链**（保证服务永远能起来）：

- 选了 `semantic` / `chroma` 但**没配 `OPENAI_API_KEY`** → 自动降级为 `naive` 关键词检索；
- `semantic` / `chroma` 构建过程中**探针失败**（key 错 / 网络不可达 / 嵌入 API 报错）→ 捕获异常，降级为 `naive`；
- `offline` 生成模式下 LLM 调用失败 → 直接把检索到的资料片段拼接成答案返回。

---

## 4. 知识库：来源与结构

知识库是 `rag-service/data/` 下的一组 Markdown 文件，`chunks.py` 在启动时把它们切成带元数据的 chunk。

### 4.1 子目录与性质

| 子目录 | 内容 | 典型 `kind` |
|--------|------|-------------|
| `interview/` | 面试口语笔记 | implementation |
| `notes/` | 手写笔记 | implementation |
| `generated/` | 由代码/对话生成的资料 | implementation |
| `open/` | 《Open Data Structures》(ODS) 教材抽取 | implementation |
| `knowledge/` | **VisuAlgo 理论知识点（预处理后）** | **theory** |

### 4.2 每篇文档的元数据（frontmatter）

`chunks.py` 解析文件顶部 `--- key: value ---` 块，切片后每个 chunk 带这些字段：

```yaml
structure:  AVLTree     # 该资料「属于」哪个数据结构；空值=通用文档(任意结构可命中)
kind:       theory      # implementation(代码/笔记) 或 theory(原理讲解)
operation:  insert      # 关联的操作（insert/delete/...）
phase:      rotate      # 操作的阶段（rotate/balance/...）
difficulty: medium      # 难度
```

> **`structure` 决定「看 AVL 时会不会召回红黑树内容」**：检索时若前端传了 `structure`，retriever 只会返回 `structure` 匹配的文档（除非是 `kind=theory` 的理论文档，见下）。

### 4.3 两种资料：implementation vs theory

DSVisualizer 并没有把**所有**数据结构都做成可视化（例如线段树、并查集、图遍历只是知识点，没有动画）。如果 theory 文档也按 `structure` 严格过滤，用户问「线段树怎么区间查询」就会扑空。

因此理论文档被打上 `kind: theory`，并在检索时用 **`$or` 跨结构始终召回**：

```python
# retriever.py · ChromaRetriever.query()
where = {"$or": [{"structure": structure}, {"kind": "theory"}]}
```

效果：**任何数据结构下，理论知识点都能被引用**，而代码/笔记类资料仍按当前结构精确过滤。这是本服务的一大特色。

---

## 5. 启动方式

| 脚本 | 平台 | 说明 |
|------|------|------|
| `start_rag.sh` | Linux / Git-Bash | 启动 RAG 后端 |
| `start_rag.bat` | Windows | 启动 RAG 后端 |
| `launch_all.bat` | Windows | 一键同时拉起 RAG 后端 + 打开 DSVisualizer |

```bash
cd rag-service
./start_rag.sh          # 或 Windows 下双击 start_rag.bat
# 正常输出：
# building retriever ...
# chroma 嵌入连通性探针(15s)...
# built chroma index via text-embedding-v3 (~1100 docs)
# serving on http://localhost:8000/ask  (Ctrl+C to stop)
```

首次启动会调用 DashScope 把全部语料嵌入成向量（一次性，~1100 篇约几十秒到几分钟，取决于网络与文档长度）。之后重启若语料没变化，会直接复用 `chroma_db/` 缓存。

---

## 6. 配置（`.env`）

在 `rag-service/.env` 配置（该文件已被 `.gitignore` 忽略，**不要提交**）。`config.py` 会优先读系统环境变量，否则读 `.env`。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `RETRIEVER` | `naive` | `naive` / `semantic` / `chroma` |
| `OPENAI_API_KEY` | （空） | DashScope / OpenAI 兼容 key，semantic·chroma·openai 模式必需 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | 指向 DashScope 时改成其 OpenAI 兼容地址 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 生成答案用的大模型名 |
| `EMBEDDING_MODEL` | `text-embedding-v3` | 嵌入模型名（DashScope） |
| `LLM_PROVIDER` | `offline` | `offline`（规则拼接）/ `openai`（真实大模型）；**若已配 key 会自动切到 `openai`** |
| `PORT` | `8000` | 服务监听端口 |

示例（DashScope）：

```ini
RETRIEVER=chroma
OPENAI_API_KEY=sk-xxxxxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
LLM_PROVIDER=openai
PORT=8000
```

---

## 7. HTTP 接口

### `POST /ask`

请求体（JSON）：

```json
{
  "question": "BST 和 AVL 的区别是什么？",
  "context": { "structure": "BST" }
}
```

- `question`：用户问题。
- `context.structure`：前端当前正在演示的数据结构名（用于结构过滤；不传或为空则全库检索）。

响应体（JSON）：

```json
{
  "answer": "AVL 是带平衡因子的二叉搜索树……（基于检索资料生成的中文讲解）",
  "highlight_nodes": [33, 17, 50],
  "sources": ["knowledge/bst.md", "open/ods/..."]
}
```

- `answer`：大模型生成的讲解（offline 模式则是检索资料拼接）。
- `highlight_nodes`：要在可视化图上高亮的节点整数值（从问题中抽取，或由模型给出）。
- `sources`：命中资料的来源文件名，便于前端标注「引用自哪里」。

> 服务对请求体做了 UTF-8 / GBK / latin-1 多编码回退解码，兼容 Windows `curl` 发送的中文。

---

## 8. 理论文档预处理（`build_knowledge.py`）

`data/knowledge/` 下的 16 篇理论文档，由脚本从外部 VisuAlgo 工作区预处理而来。

| 项 | 值 |
|----|----|
| 源目录（用户机器） | `C:/Users/13035/.qoderworkcn/workspace/mrvyb4qpria56due/rag_knowledge` |
| 目标目录（项目内，自包含） | `rag-service/data/knowledge/` |
| 运行 | `python build_knowledge.py` |

**清洗步骤**：
1. `html.unescape` 反转义；
2. 删噪音行（`**来源**` / `**幻灯片数量**`）；
3. 删 HTML 标签（只删真标签，保留 `a < b` 这类不等式）；
4. 去标题编号（`## 1. Foo` → `## Foo`）、删原一级标题与幻灯片 `---` 分隔符；
5. 加 frontmatter（`structure: <主题>` + `kind: theory` + `operation/phase/difficulty`）与统一一级标题。

**主题映射**（`STRUCT_MAP`）：`array→Array`、`list→List`、`bst→BST`、`heap→Heap`、`hashtable→HashMap`、`graphds→Graph`、`ufds→UFDS`、`fenwicktree→FenwickTree`、`segmenttree→SegmentTree`、`dfsbfs→GraphTraversal`、`mst→MST`、`sssp→SSSP`、`sorting→Sorting`、`bitmask→Bitmask`、`recursion→Recursion`、`cyclefinding→CycleFinding`（`README.md` 无映射，跳过）。

> 预处理结果已入库（`data/knowledge/*.md` 已提交），**日常使用无需重跑**；只有当外部 VisuAlgo 源更新时才需要再跑一次。

---

## 9. 索引重建与排错

### 9.1 怎么触发重建

服务用 **「语料最新修改时间 vs 索引记录时间」** 判断是否重建：

- `ChromaRetriever`：collection 元数据里记了 `data_mtime`，每次 `add()` 会比较；语料有更新就按 id 删旧文档、重新嵌入。
- `SemanticRetriever`：pickle 缓存 `semantic_index.pkl` 的 mtime 比较。
- `NaiveRetriever`：`naive_index.pkl` 的 mtime 比较。

**手动强制重建**：删掉缓存目录/文件再启动即可——

```bash
rm -rf rag-service/chroma_db      # chroma 模式
# 或
rm -f rag-service/semantic_index.pkl rag-service/naive_index.pkl
./start_rag.sh
```

### 9.2 已知坑（ChromaDB 1.5.x）

本机装的是 **chromadb 1.5.9**，与旧教程写法有几处不兼容，已在本项目中逐一修复：

| 现象 | 根因 | 修复 |
|------|------|------|
| `'_DashScopeEmbedding' object has no attribute 'name'` | 1.5.9 自定义 embedding function 需要 `.name` 属性 | 改用**手动嵌入**：自己算好向量再 `collection.add(embeddings=...)` / `query(query_embeddings=...)`，彻底不依赖 chroma 的 EF 接口 |
| 元数据 `None` 值报错 | 1.5.x 不允许 metadata 值为 `None` | `add()` 时把所有 `None` 清洗成空串 |
| `Expected where to have exactly one operator, got {} in delete.` | 1.5.9 不再接受 `delete(where={})` 清空整集合 | 改为**按 id 删除**：`old_ids = coll.get(...)["ids"]; coll.delete(ids=old_ids)` |
| 「还是 538 条，知识文档没进索引」 | 旧 `server.py` 用 `count()==0` 才重建，`count()>0` 就永远复用、永不调 `add()`，导致 ChromaRetriever 写在 `add()` 内的过期检测没机会跑 | `server.py` 改为**无条件调用 `_retriever.add()`**，是否重建完全交给 retriever 内部判断 |

> 上面这些坑都是「沙箱（Linux）无法本地复现、只能靠本机实测」的，若你升级 chromadb 大版本后遇到新的 API 报错，把**第一行 error** 发出来即可定位。

### 9.3 常见日志含义

| 日志 | 含义 |
|------|------|
| `built chroma index via text-embedding-v3 (~1100 docs)` | 成功重建并嵌入（含 16 篇 theory） |
| `reused chroma index (... docs)` | 语料无变化，直接复用旧索引 |
| `[WARN] chroma 检索构建失败（...），降级为 naive 关键词检索` | 嵌入/连接失败，已降级；检查 key 与 `OPENAI_BASE_URL` 可达性 |
| `[WARN] LLM_PROVIDER 设为 openai 但 OPENAI_API_KEY 为空` | 会退化成离线拼接，答案质量下降，请补 key |

---

## 10. 如何扩展知识库

1. **加一篇 implementation 资料**：往 `data/interview/`（或 `notes/`、`generated/`、`open/`）放一个 `.md`，顶部用 frontmatter 声明 `structure` 和可选的 `kind/operation/phase/difficulty`；重启服务即自动纳入索引。
2. **加一篇 theory 理论资料**：直接放 `data/knowledge/<name>.md`，frontmatter 写 `structure: <主题>` 与 `kind: theory`；重启后会跨结构始终召回。
3. **换大模型 / 嵌入源**：改 `.env` 的 `OPENAI_BASE_URL` / `OPENAI_MODEL` / `EMBEDDING_MODEL` 即可，代码走 OpenAI 兼容协议。
4. **换检索后端**：`RETRIEVER` 在 `naive` / `semantic` / `chroma` 间切换；三者共享同一套 `chunks` 切片与 `query(text, k, structure)` 接口，切换无需改其他代码。

---

## 11. 文件导航

| 文件 | 职责 |
|------|------|
| `server.py` | 入口：加载语料、构建 retriever、暴露 `POST /ask` |
| `retriever.py` | `NaiveRetriever` / `SemanticRetriever` / `ChromaRetriever`，统一 `add/query/count` 接口 |
| `chunks.py` | 把 `data/*.md` 切成带 frontmatter 元数据的 chunk |
| `llm.py` | `offline` 规则拼接 / `openai` 真实大模型调用，输出 `{answer, highlight_nodes, sources}` |
| `config.py` | 读 `.env` 与系统环境变量 |
| `build_knowledge.py` | 预处理 VisuAlgo 理论文档到 `data/knowledge/` |
| `start_rag.sh` / `start_rag.bat` / `launch_all.bat` | 启动器 |
