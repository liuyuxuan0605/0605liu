# PDF 语义分块改造（pdfplumber + 书签层级）

把《Open Data Structures》(DataBook.pdf, 336 页) 的入库方式从「按物理页切」换成
「按 PDF 书签的章节层级切」，产出 `data/book/` 取代 `data/open/`。

## 为什么换

旧的 `extract_pdf.py`（PyPDF2，一页一个 md，共 323 个文件）有四个实测问题：

| # | 问题 | 证据 |
|---|------|------|
| 1 | 按物理页切，语义被拦腰截断 | 一页里可能塞两个不相干小节；一节被切成 5 段互不相连 |
| 2 | 提取丢空格 | `operationssupportedbytheQueueinterfaceare`，空格占比仅 **0.056** |
| 3 | 页眉页脚混进正文 | 每页都带 `Interfaces §1.2` 和页码 |
| 4 | `structure:` 一律留空 | 323 个页片段对**任何**数据结构的查询都可召回 → precision 噪声源 |

第 2 条尤其致命：TF-IDF 关键词路靠分词，单词粘连后基本失效。

## 新方案

`extract_pdf_plumber.py`：

1. **pdfplumber + `x_tolerance=1.0`** 修复空格丢失 —— 空格占比 0.056 → **0.151**（正常英文水平）。
   默认值 3.0 判定字符间距不够大就不插空格，LaTeX 紧排文档必踩。
2. **用 PDF 自带的 148 条书签做切分边界**。书签只精确到页，所以再用「标题文本在正文
   中的位置」二次定位到**字符级**（normalized 匹配，命中 146/148；2 条兜底：
   `Front Matter` 无正文、`10.2.1 Analysis of merge(varh1,varh2)` 书签写的是 LaTeX 变量名）。
3. **一个输出文件 = 原书一个 level2 节，文件内 `##` = level3 小节**。
   这一步是关键：现有 `chunks.py` 本来就按 `##` 切 child、按 source（文件）聚合 parent，
   所以 **Parent-Child 的 parent_id 关联不需要改任何代码**就成立了。
   一个 level2 节平均 7215 字，整篇当 parent 上下文也不会爆。
4. **超长 child 二次切分**（上限 2500 字）。原始 level3 里 `13.3 YFastTrie` 单块 8142 字、
   `14.2 B-Trees` 平均 4900 字/块，作为向量检索粒度太粗。
5. **按章节映射 `structure`**（`2.3 ArrayQueue` → `Queue`，`9.2 RedBlackTree` → `RedBlackTree`……）。
   只有数学基础、跳表、排序、图、Trie 这些项目里没有对应结构的才留空。
6. **剔除**目录 / 致谢 / 参考文献 / 索引 / 习题节（`Discussion and Exercises`）——
   共约 16 万字纯噪声。
7. **中文关键词逐 child 注入**，且**每块最多 6 个**（按词频取 top-N）。

## 效果

| | 旧 `open/` | 新 `book/` |
|---|---|---|
| 文件数 | 323（=页数） | **43**（=章节数） |
| 正文字符 | 518,694 | **310,262**（砍掉 16 万字噪声） |
| child chunk | 323 | **196** |
| child 大小 | 整页，不可控 | p50 **1782** / p90 2416 / max 2724，无超 3000 |
| parent | 无概念 | 43 个，平均 **7215** 字 |
| structure 绑定 | 0（全空） | **127/196** 绑定到具体结构，69 通用 |
| 空格占比 | 0.056（粘连） | **0.151** |

## 过程中修掉的三个 bug

1. **正文首字母被吃**：`In this section` → `n this section`。
   `end_of_title` 取 `n2o[pos+len(nt)]` 指向的是正文第一个字母而非标题末字符，
   off-by-one，应为 `pos+len(nt)-1`。
2. **中文关键词只挂在文件末尾**：`chunks.py` 按 `##` 切 child，放末尾等于只有最后一个
   child 带中文词 → 所有中文查询被系统性吸到「每个文件的最后一段」。
   实测「堆排序原理」命中 `11.1.4 A Lower-Bound` 而不是 `11.1.3 Heap-sort`。改为逐 child 注入。
3. **术语清单节成万能匹配**：`1.7 List of Data Structures` 命中几十个英文术语 → 注入几十个
   中文词 → 同时出现在「堆排序」「B树节点分裂」「哈希表链地址法」的 top-3。
   限制每块最多 6 个关键词后消失。

## 顺带修的既有问题

* **`build_source_full` 的 `cap=4000`**（`chunks.py`）和 **`_source_context` 的 `cap=4000`**
  （`eval_generation.py`）→ 统一放宽到 **20000**。
  这两个 cap 是之前诊断出的 Judge 假阴性根因（[18] 排序复杂度 faith=0.26、
  [35] 图找环 faith=0.29，关键事实分别在 char 18592 / 9390 处被截掉）。
  换 `book/` 之后 43 个 parent **全部**超过 4000，从偶发变成必中，所以一并修了。
  ⚠️ **这会让新分数与放宽前的历史批次不可直接比较。**
* **四处硬编码的语料目录列表** → 统一引用 `chunks.SUBDIRS`。
  原先 `server.py` / `retriever.py`(×2) / `eval_retrieval.py` 各写一份
  `("interview","notes","generated","open","knowledge")`，新增目录极易漏改导致索引不刷新。

## 需要在本地做的事

沙箱没有 API key、没有网络到 DashScope，所以**向量索引没法在这边重建，评测也跑不了**。
请在本地按顺序执行：

```bash
cd rag-service
python extract_pdf_plumber.py      # 已跑过，data/book/ 43 个文件已生成，可跳过
python server.py                   # 首次启动会检测到索引过期并重建（需 DashScope key）
python eval_generation.py          # 重跑评测
```

重建索引这一步会重新 embedding 196 个 chunk，同时旧的 323 个 open/ chunk 从索引消失。

## 遗留

* `data/open/` 的 323 个文件**仍在磁盘上**，只是从 `chunks.SUBDIRS` 移除、不再进检索。
  确认新方案效果更好之后可以删掉。
* `chunks._terms` 对中文是**按单字**切词（"跳表"→{跳,表}，"链表"→{链,表}），
  naive 关键词路的中文精度天然很差（实测「跳表的查找复杂度」误命中 AdjacencyLists）。
  这是既有架构问题，与本次分块无关，生产主路走向量检索不受影响。要根治得引入中文分词。
* 代码块没有用 ``` 标记，公式的上下标会换行错位（LaTeX PDF 通病），语义仍可读。

---

## 中文版 `book_zh/` + 增量索引（2026-07-31 第二批）

### 中文分块 `extract_pdf_plumber_zh.py`
- 源：`D:/ai_canshow/DataBook-mono.pdf`（中文版《Open Data Structures》），336 页。
- 书签层级与英文版**完全相同**（148 条三级书签），但**书签标题是英文、正文标题是中文**，且全文字号均匀（10.0）不能靠字号分标题。
- 标题定位改用「小节编号前缀」：用每条书签的编号（`1.2.1`/`2.3`…）在 destination page ±1 页内抓「以该编号开头」的中文标题行（已验证稳：`2.3→ArrayQueue：基于数组的队列`、`13.1→二进制字典树：一种数字搜索树`）。
- 其余工程点与英文版一致：`x_tolerance=1.0`、剔除页眉页脚、level2=文件(level2 节)/level3=`##`、超长 child 二次切分（2500）、逐 child 注入中文关键词（≤6）+ 英文 structure 名（帮「中文查询翻英文」跨语言对齐）。
- 产物：`data/book_zh/`，文件名只用编号（`ods_zh_2_3.md`，无中文编码风险）。
- 体量：57 个 parent / 172 个 child / 22.4 万字 / 平均 parent 3931 字。

### 增量索引（内容 hash + mtime 粗筛）
- 新增 `doc_index.py`：manifest 落在 `data/.doc_index.json`（隐藏文件，不被 `*.md` glob 当 chunk），记录 `doc_id→{mtime, hash(sha256), chunk_ids}`。
- `compute_sync_plan`：mtime 没变 → 直接跳过（不读内容、不算 hash）；mtime 变了才算 sha256 精判；内容真变才重切重嵌；磁盘消失的文档取其旧 chunk_ids 进 `remove`。
- 三个 retriever 全部加 `sync(rechunk, remove)`：只清旧向量、只重嵌变化文档，**不变文档不重建**（省 DashScope API 调用）。
- chunk 稳定 id：`sanitize(source)+"_"+i`（chroma 合规 `[A-Za-z0-9_-]`），增量定位旧向量靠它。
- `server.py`：启动时首次全量 `add`、后续 `sync`；另起 daemon 线程**每 30s 轮询**一次 `compute_sync_plan`+`sync`，实现「文档变了，chunk 和向量跟着变」且**增量、不每次全量重建**。

### 沙箱验证（无 key/无网）
- `py_compile` 全过。
- `compute_sync_plan` 单元全通过：首跑全 rechunk → 改 1 文件仅该文件 rechunk → 删 1 文件 `remove` 含其 chunk_ids → touch（内容不变）仅更新 mtime 不重切。
- `NaiveRetriever.sync` 增量正确：删1加1 后 docs 数不变、旧词移除、新词命中。
- 真实语料 `load_chunks`：1326 chunks，chroma id **0 不合规**，中文查询命中 `book_zh`。
- **未验（需本地 key/网）**：semantic/chroma 的 `sync` 真·向量增量、后台轮询端到端。

### 已知遗留
- 中文 naive 路单字切词精度弱（同英文），生产走向量路不受影响。
- `book_zh` 部分 level1 chapter 字段有轻微提取瑕疵（英文书签标题断字），仅影响元数据展示、不影响检索。
- 待用户本地跑：`python server.py`（首次全量建索引）→ 改一个 `book_zh` 文件 → 重启/等 30s → 日志应只 `增量同步：+N/-M`，检索结果对应更新。

