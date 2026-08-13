# DSVisualizer RAG 后端

数据结构可视化的 **AI 讲解服务**（检索增强生成 / RAG）。

针对 16 种数据结构（单/双向链表、栈、队列、双端队列、阻塞队列、二叉搜索树、AVL 树、红黑树、哈希表、最小堆、B 树、B+ 树、循环缓冲区、图、LRU 缓存），对插入 / 删除 / 旋转等操作给出**分步讲解**，并在可视化画面上**高亮关键节点**。

> 本仓库是后端服务。前端 Qt (C++) 可视化客户端在另一个目录编译运行，通过 HTTP 调用这里的 `/ask` 接口获取 AI 讲解。

---

## 快速开始

```bash
cd rag-service
cp .env.example .env          # 可选：填 OPENAI_API_KEY 启用真实大模型
pip install -r requirements.txt
python server.py              # 启动后访问 http://localhost:8000/ask
```

**不填 key 也能跑**：未配置 `OPENAI_API_KEY` 时自动降级为「本地 BM25 关键词检索 + 规则拼接答案」，服务不崩，适合离线演示。

---

## 配置

复制 `.env.example` 为 `.env`，按需填写：

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | DashScope / 通义千问 key。留空 → 离线降级 |
| `OPENAI_BASE_URL` | OpenAI 兼容端点，默认指向 DashScope |
| `OPENAI_MODEL` | 生成模型，如 `qwen-plus` |
| `EMBEDDING_MODEL` | 向量模型，默认 `text-embedding-v3` |
| `RETRIEVER` | `naive`（默认，零依赖）/ `semantic` / `chroma` |
| `LLM_PROVIDER` | `openai` / `offline` |
| `QUERY_TRANSLATE` | 0/1，查询中译英开关（默认 0） |
| `QUERY_REWRITE` | 0/1，LLM 查询改写开关（默认 0） |

---

## 外部 API 如何接入

后端把 **DashScope 当作 OpenAI 兼容端点**，直接 HTTP 调用两个接口，不依赖任何 SDK：

- 生成答案：`POST {OPENAI_BASE_URL}/chat/completions`
- 文本向量化：`POST {OPENAI_BASE_URL}/embeddings`

只需在 `.env` 填好 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / 两个模型名即可，其余 HTTP 调用、重试、降级逻辑都已写死在 `llm.py` 与 `retriever.py`。

---

## 降级链（缺 key / 构建失败都不崩）

```
检索器:  chroma  →  semantic  →  naive (本地 BM25, 零依赖)
生成器:  openai  →  offline   (规则拼接答案)
```

- `OPENAI_API_KEY` 为空 → `RETRIEVER` 退化 `naive`，`LLM_PROVIDER` 退化 `offline`
- `chroma` 构建失败 → 自动往下走 `semantic → naive`

---

## 依赖说明

见 [`rag-service/requirements.txt`](rag-service/requirements.txt)：

- `naive + offline`：**零依赖**，纯标准库开箱即跑
- `semantic`：需 `requests`
- `chroma`：需 `requests` + `chromadb`
- 自动加载 `.env`：需 `python-dotenv`（可选）

---

## 目录结构（rag-service/）

| 文件 | 职责 |
|------|------|
| `server.py` | 主入口，基于标准库 `http.server` 的 HTTP 服务（默认 `:8000/ask`） |
| `llm.py` | 意图分类、提示词构建、LLM / 翻译 / 改写调用 |
| `retriever.py` | 三档检索器（Naive / Semantic / Chroma）与增量同步 |
| `config.py` | 配置与 `.env` 加载 |
| `eval_common.py` / `eval_generation.py` / `eval_retrieval.py` | 评测脚本 |
| `data/` | 知识库语料（已纳入版本控制，clone 即带） |

> `app.py` 为可选的 FastAPI 生产入口，当前未接线；默认请使用 `server.py`。

---

## 安全

- `.env`（含真密钥）已被 `.gitignore` 忽略，**永不进版本库**；仅 `.env.example` 模板入库。
- `chroma_db/`、`*.pkl`、`data/.doc_index.json` 等缓存均不入库。
- 提交前已扫描确认：代码内无硬编码密钥。
