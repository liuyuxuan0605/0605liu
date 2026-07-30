# DSVisualizer

> **为面试准备打造的数据结构可视化教学工具**：用 C++17 + Qt 把 16 种高频数据结构的核心操作拆成「微步骤」逐帧演出来；并外接一个 **RAG 讲解后端**，让你对着屏幕上的真实节点问 *"为什么这一步要左旋"*——AI 检索资料 + 结合当前结构给你讲解，并把关键节点高亮到图上，还能直接驱动可视化（跳转结构 / 分步演示 / 执行操作）。

---

## ✨ 功能特性

**可视化本体**
- **16 种数据结构**，全部自实现（不依赖任何第三方算法库）。
- **步骤分解动画**：每个操作（插入 / 删除 / 查找 / 遍历 …）既真正修改数据结构，又返回一串 `Frame`（微步快照）；可视化层对相邻帧做差分，用 `QPropertyAnimation` 平滑过渡（节点位置 / 颜色 / 缩放），效果类似 IDE 调试器的 step-by-step，目标 60fps。
- **交互外壳**：分类下拉选结构、动态操作面板、值输入、播放 / 暂停 / 逐帧、撤销重做、切换即清空画布。
- **遍历展示**：Graph 与 BST 上实现 BFS / DFS 去重顺序高亮（对标 VisuAlgo）。

**AI 讲解模块（重点）**
- 对着**当前真实结构**提问 → 检索知识库 + 拼装真实状态 → LLM 生成讲解。
- 答案中的关键节点**自动高亮到图上**，建立「文字 ↔ 结构」的对应。
- 可**驱动可视化本身**：JSON `actions` 协议支持 `jump`（跳到指定结构）、`step_explain`（分步 / 按顺序演示）、`run_operation`（直接执行某个操作）。
- 检索管线为 **hybrid**：向量检索（ChromaDB / 本地余弦）+ 关键词检索（TF-IDF）经 **RRF** 融合；向量路带 **Direct Query Rewrite**（口语 / 指代归一）与**中英跨语言对齐**，召回比单路更稳。

---

## 📚 支持的数据结构（16 种）

| 分类 | 结构 | 可视化重点 |
|------|------|-----------|
| **链表类** | 单链表 SinglyLinkedList | 指针断开 / 重连 |
| | 双链表 DoublyLinkedList | 双向指针同步 |
| **栈与队列** | 栈 Stack | 栈顶入出（竖向） |
| | 队列 Queue | 队首 / 队尾移动（横排） |
| | 双端队列 Deque | 头尾均可插入 / 删除 |
| | 阻塞队列 BlockingQueue | 固定容量 + 牺牲 1 单元判满；满时拒绝入队（模拟阻塞） |
| | 环形缓冲区 RingBuffer | 满时**覆盖**最旧（与 BlockingQueue 语义对照） |
| **树结构** | 二叉搜索树 BST | 比较路径、删除后继替换（✅ BFS+DFS） |
| | AVL 平衡树 | 平衡因子变化 + 四种旋转 |
| | 红黑树 RedBlackTree | 颜色 + 旋转 + 双黑修复 |
| | B 树 B-Tree | 多路分裂 / 合并 |
| | B+ 树 B+Tree | 叶子链表、内部 / 叶子节点区分 |
| | 最小堆 MinHeap | 数组布局 + 上浮 / 下沉交换 |
| **哈希与缓存** | 哈希表 HashMap | 链式冲突：`hash(key)%8` 定位桶 → 桶内链追加 |
| | LRU 缓存 LRUCache | get 命中移到队首、容量满淘汰队尾 |
| **图** | 图 Graph | 邻接遍历、边权（✅ BFS+DFS+Dijkstra） |

---

## 🏗️ 架构总览

### 可视化本体（三层解耦）

```
┌──────────────────────────────────────────────────────────────┐
│  UI 层 (src/ui)   OperationPanel · MainWindow · LogViewer       │
│   选择结构 / 输入值 / 点按钮 → MainWindow::doOperation          │
└───────────────┬──────────────────────────────────────────────┘
                │  operationRequested("insert","42")
                ▼
┌──────────────────────────────────────────────────────────────┐
│  Core 引擎 (src/core)   纯 C++17，零 Qt 依赖                    │
│   IDataStructure::insert/remove/find/bfs/dfs …                │
│     ↓ 既修改结构，又返回 FrameList（一串微步快照）              │
└───────────────┬──────────────────────────────────────────────┘
                │  FrameList
                ▼
┌──────────────────────────────────────────────────────────────┐
│  Visual 层 (src/visual)   DSScene + StepAnimator               │
│   DSScene::applyFrame 对相邻帧差分 → QPropertyAnimation 过渡    │
│   StepAnimator 用 QTimer 按 BASE_MS/speed 逐帧推进             │
└──────────────────────────────────────────────────────────────┘
```

**关键不变量**：引擎层只产数据（`FrameList`），不碰任何 Qt 绘图；Visual 层只消费数据做动画。两层仅靠 `Common.h` 的 `Frame` 结构耦合，因此引擎可被独立单测。

### AI 讲解模块（外接 RAG 后端）

```
┌──────────────────────────── Qt 客户端 ────────────────────────────┐
│  用户输入 → postAsk(question, context) ──HTTP POST /ask──▶ 后端     │
│   onReply() → 渲染 answer 气泡 + DSScene::highlightByValue() 上色  │
│   onReply() 还会解析 actions → 跳转结构 / 分步演示 / 执行操作       │
└───────────────────────────────┬──────────────────────────────────┘
                                 ▼
┌──────────────────────────── rag-service 后端 ──────────────────────┐
│  server.py::answer(question, context)                              │
│    ├─ hybrid_search(): 向量路(ChromaRetriever 中英双向量            │
│    │      + Direct Query Rewrite) + 关键词路(NaiveRetriever TF-IDF) │
│    │      → RRF 融合 → top-k                                       │
│    └─ llm.call_llm(): build_prompt(真实状态+资料) → OpenAI 兼容接口 │
│  return { answer, highlight_nodes, sources, actions }             │
└────────────────────────────────────────────────────────────────────┘
```

`context` 由客户端拼（含 `tree_state` 当前帧结构、`structure` 类型、`desc` 当前步描述、`highlight_ids` 本步节点 id），发到 `/ask`；后端召回知识块 + 拼 prompt 调 LLM，返回结构化 JSON。

---

## 🤖 AI 讲解：请求 / 响应协议

**请求** `POST /ask`
```json
{
  "question": "为什么插入 42 之后这里要左旋？",
  "context": {
    "structure": "RedBlackTree",
    "desc": "插入42后触发左旋",
    "tree_state": "42 [id=11]\n  17 [id=5]\n    8 [id=2]\n  ...（整棵当前红黑树，缩进=父子层级）",
    "highlight_ids": "11"
  }
}
```

**响应**
```json
{
  "answer": "插入 42 后，节点 42 的父为红、叔叔为黑，且形成「左-右」形状；按红黑树修复规则需先对父节点做一次左旋……",
  "highlight_nodes": [42, 17],
  "sources": ["notes/redblack_rotation.md", "theory/tree_rotation.md"],
  "actions": [
    { "type": "step_explain", "structure": "RedBlackTree",
      "steps": [ {"op":"insert","value":"42"} ] }
  ]
}
```

`actions` 三种动作（前端解析后自动执行，无需用户再点按钮）：
- `jump`：`{"type":"jump","structure":"RedBlackTree"}` —— 切换到指定结构。
- `step_explain`：`{"type":"step_explain","structure":"AVLTree","steps":[{"op":"insert","value":"30"}, ...]}` —— 分步 / 按顺序演示；用户没给数值时模型自行选典型序列。
- `run_operation`：`{"type":"run_operation","structure":"AVLTree","op":"insert","value":"42"}` —— 直接执行单个操作。

> 约束（防幻觉）：后端设三级忠实度闸门 `HARD_REJECT_FLOOR=0.4` / `WARN_FLOOR=0.55`，检索不到相关内容时直接拒答，绝不用模型自身知识编造。

---

## 🔍 AI 检索管线

`hybrid_search` 并行跑两路、再用 **RRF**（`fused = Σ 1/(60+rank)`）按来源融合，比单路召回更宽：

| 路 | 实现 | 说明 |
|----|------|------|
| 向量路 | `ChromaRetriever` / `SemanticRetriever` | 中文查询**翻成英文**再检索（跨语言对齐）；向量路前还会过 **Direct Query Rewrite**（口语 / 指代 / 省略 → 规范查询）。 |
| 关键词路 | `NaiveRetriever`（TF-IDF） | 自带**同义词扩展**（「翻转」→「旋转」、「加」→「插入」），做字面精准命中兜底。 |

主路是 `naive` 时两路同一实例，退化为单路；嵌向量用 **DashScope `text-embedding-v3`**（OpenAI 兼容端点），无 key 时自动降级为 `naive` 关键词检索，服务仍可启动。

---

## 🛠️ 技术栈

| 维度 | 选型 |
|------|------|
| 语言 / 框架 | C++17 + Qt 5.12.11 (MinGW 7.3) |
| 构建 | qmake（`.pro` 工程） |
| 架构 | 三层：引擎层（纯 C++17，零 Qt）/ 渲染层（Qt Graphics View）/ 交互层（Qt Widgets） |
| 核心机制 | `Frame` 帧快照 + 差分动画；`unique_ptr` 持有节点 + 裸 `parent` 导航 |
| AI 后端 | Python 3（stdlib `http.server` 零依赖入口 `server.py`，或 FastAPI 入口 `app.py`）；OpenAI 兼容 LLM（生产用 DashScope） |
| 向量库 | ChromaDB（HNSW + 余弦）/ 或本地 pickle + 内存余弦 |

---

## ⚙️ 配置（rag-service/.env）

| 变量 | 默认值 | 取值 / 说明 |
|---|---|---|
| `RETRIEVER` | `naive` | `naive`（零依赖关键词）\| `semantic`（本地余弦）\| `chroma`（ChromaDB 向量库） |
| `OPENAI_API_KEY` | `""` | 语义 / 向量嵌入 + openai 模式必填；缺省时 chroma/semantic 自动降级为 naive |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | 兼容 OpenAI 的 chat/embeddings 端点（生产用 DashScope） |
| `OPENAI_MODEL` | `gpt-4o-mini` | 对话模型名（生产示例用 `qwen-plus`） |
| `EMBEDDING_MODEL` | `text-embedding-v3` | 嵌入模型名 |
| `LLM_PROVIDER` | `offline` | `offline`（规则拼接，无 key 可跑）\| `openai`（真实大模型）；**若配了 key 但未显式设此项，自动启用 `openai`** |
| `PORT` | `8000` | 服务监听端口 |

> `.env` 由 `config.py` 手动解析（不强制依赖 `python-dotenv`）；真实环境变量优先级高于 `.env` 文件。

---

## 📁 目录结构

```
DSVisualizer_push/
├── DSVisualizer.pro          # 主程序 qmake 工程（GUI）
├── launch_all.bat            # 一键构建+启动（含 AI 插件与 RAG 后端）
├── src/
│   ├── app/                  # 程序入口
│   ├── core/                 # 数据结构引擎（纯 C++，无 Qt）：Frame/IDataStructure/各结构
│   ├── visual/               # 渲染层：VisualNode/Edge、LayoutEngine、DSScene、StepAnimator
│   ├── ui/                   # 交互层：MainWindow、OperationPanel、LogViewer
│   └── ai/                   # AI 讲解插件（QPluginLoader 加载的 aichatplugin）
├── rag-service/              # 外挂 Python RAG 后端
│   ├── server.py             # 零依赖入口（stdlib http.server）
│   ├── app.py                # 生产入口（FastAPI + chroma + openai）
│   ├── config.py / chunks.py / retriever.py / llm.py
│   ├── extract_docs.py       # 从 src/core/*.h 自动抽取讲解文档
│   ├── ingest.py             # 构建索引
│   ├── data/                 # 知识库（interview / notes / generated / open / knowledge）
│   ├── requirements.txt / .env.example
├── tests/                    # 无 Qt 核心引擎单测
└── docs/                     # 开发文档（DESIGN.md）
```

---

## 📖 更多文档

- `docs/DESIGN.md` —— 权威开发文档（架构、Frame 数据模型、统一接口、各结构可视化重点、构建与踩坑）。
- `AI讲解模块功能文档.md` —— AI 讲解闭环的接口、配置、正常 / 异常流程与边界。
- `rag-service/README.md` —— RAG 后端单独的部署与接口说明。

---

*项目最初为技术面试复习而做，重点展示算法分步思维与树旋转 / B 树分裂 / 图遍历等过程。*
