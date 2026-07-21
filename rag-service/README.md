# rag-service —— DSVisualizer 的外挂 RAG 后端

独立进程（FastAPI / stdlib http.server），主程序通过 HTTP 调用 `POST /ask`。
知识库来自项目自有文档 + 引擎头文件自动抽取，版权安全、与动画一致。

## 目录
```
rag-service/
  server.py          # 零依赖入口（stdlib http.server），naive+offline 开箱即跑
  app.py             # 生产入口（FastAPI + chroma + openai）
  config.py          # 读 .env
  chunks.py          # markdown 切片 + 元数据
  retriever.py       # NaiveRetriever（零依赖）/ ChromaRetriever（生产）
  llm.py             # offline 兜底 / openai 调用
  extract_docs.py    # 从 src/core/*.h 自动抽取讲解文档
  ingest.py          # 构建索引
  data/              # 知识库（interview / notes / generated / open）
  requirements.txt
  .env.example
```

## 快速开始（零安装，推荐先这样验证）
```bash
cd rag-service
python server.py
# 另开终端
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"为什么 AVL 插入 15 后要对 20 右旋","context":{}}'
```
默认 `RETRIEVER=naive` + `LLM_PROVIDER=offline`：无需联网、无需 key，
直接用检索到的资料拼接答案，并从问题中抽取整数作为高亮节点。

## 生成知识库文档（亮点）
```bash
python extract_docs.py   # 扫描 src/core/*.h -> data/generated/<结构名>.md
python ingest.py         # 构建索引
```

## 生产模式
```bash
pip install -r requirements.txt
cp .env.example .env     # 填 OPENAI_API_KEY，RETRIEVER=chroma，LLM_PROVIDER=openai
python ingest.py --retriever chroma
python app.py
```
- `RETRIEVER=chroma`：用 chromadb + sentence-transformers 做语义检索。
- `LLM_PROVIDER=openai`：调用 OpenAI 兼容接口，返回 JSON（answer / highlight_nodes / sources）。
- API key 只存在后端环境变量，**绝不**进前端或仓库。

## 请求 / 响应
请求：`{"question": "...", "context": {"structure": "AVLTree", "desc": "...", "index": 3, "total": 5}}`
响应：`{"answer": "...", "highlight_nodes": [20], "sources": ["data/generated/AVLTree.md"]}`

`context.structure` 用于按当前演示的数据结构过滤检索结果。
