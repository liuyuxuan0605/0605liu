"""把 data/ 下的 markdown 切成带元数据的 chunk。

每个 chunk 带 structure / operation / phase / difficulty 元数据，
检索时可按当前演示的数据结构类型过滤（看 AVL 时不返回红黑树内容）。
支持文件顶部 frontmatter（--- key: value ---）显式声明元数据。
"""
import os
import re
import glob


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text):
    meta = {}
    m = FRONTMATTER_RE.match(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def _terms(s):
    """英文/数字词 + 每个汉字，作为朴素检索的词表。"""
    terms = set()
    for w in re.findall(r"[A-Za-z0-9_]{2,}", s):
        terms.add(w.lower())
    for ch in s:
        if "一" <= ch <= "鿿":
            terms.add(ch)
    return terms


# 参与检索的语料目录。
# book/ 由 extract_pdf_plumber.py 生成：pdfplumber + PDF 书签层级做语义切分，
#   一个文件 = 原书的一个 level2 节（天然的 parent），文件内 ## = level3 小节（child）。
# book_zh/ 由 extract_pdf_plumber_zh.py 生成：同一本书的中文版（DataBook-mono.pdf），
#   切分逻辑与 book/ 完全一致（书签层级同英文，仅中文标题靠「小节编号前缀」从正文抓）。
# open/ 是它的前身（extract_pdf.py + PyPDF2 按物理页切的 323 个页片段），
#   内容与 book/ 完全重复，但丢空格、混页眉页脚、切断语义、structure 一律留空导致
#   任何查询都能召回，是 precision 偏低的主要噪声源 —— 已被 book/ 取代，
#   文件保留在磁盘上作为对照，但不再进入检索。
SUBDIRS = ("interview", "notes", "generated", "book", "book_zh", "knowledge")


def sanitize_id(s):
    """把任意 source 路径转成稳定、安全的 id（chroma 要求 [A-Za-z0-9_-]）。

    source 形如 `book_zh/ods_zh_2_3.md`，含 `/` `.` 都不合法（chroma id 拒绝），
    统一换成 `_`。同一文档每次启动都生成同一 id —— 这是增量检索能按文档
    定位「清掉旧向量、只重嵌变更」的前提。
    """
    return re.sub(r"[^A-Za-z0-9_-]", "_", s)


def chunk_file(path, data_dir):
    """单文件切分，返回带**稳定 id** 的 chunks。

    与 load_chunks 的切分规则完全一致，但额外给每个 chunk 分配
    `id = sanitize(source) + "_" + i`（i 为文件内顺序，跨运行稳定）。
    增量索引（doc_index.sync_plan）只重切发生变化的文件，就靠这个稳定 id
    来定位「该清掉哪些旧向量」。
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    meta, body = parse_frontmatter(raw)
    # 尊重 frontmatter 中显式声明的 structure：
    # - structure: AVLTree 等具体名 → 仅在看该结构时召回
    # - structure: （空值，即 "structure:" 后无内容）→ 通用文档，任意结构均可命中
    # - 不写 structure → 回退用文件名（保持旧行为）
    if "structure" in meta:
        structure = meta["structure"]
    else:
        structure = os.path.splitext(os.path.basename(path))[0]

    source = os.path.relpath(path, data_dir).replace("\\", "/")
    base_id = sanitize_id(source)
    parts = re.split(r"(?m)^#{1,3}\s+(.*)$", body)
    heading = "概览"

    chunks = []

    def flush(h, b, idx):
        if not b.strip():
            return
        text = (("# " + h + "\n") if h else "") + b.strip()
        chunks.append({
            "id": base_id + "_" + str(idx),
            "text": text,
            "metadata": {
                "source": source,
                "structure": structure,
                "kind": meta.get("kind", ""),
                "operation": meta.get("operation", ""),
                "phase": meta.get("phase", ""),
                "difficulty": meta.get("difficulty", ""),
                "heading": h,
            },
            "terms": _terms(text),
        })

    idx = 0
    if parts[0].strip():
        flush(heading, parts[0], idx)
        idx += 1
    for i in range(1, len(parts), 2):
        h = parts[i].strip()
        b = parts[i + 1] if i + 1 < len(parts) else ""
        flush(h, b, idx)
        idx += 1

    return chunks


def load_chunks(data_dir):
    chunks = []
    files = []
    for sub in SUBDIRS:
        d = os.path.join(data_dir, sub)
        if os.path.isdir(d):
            files += glob.glob(os.path.join(d, "*.md"))

    for fp in files:
        chunks.extend(chunk_file(fp, data_dir))

    return chunks


def build_source_full(chunks, cap=20000):
    """把一个 source 下的所有 child chunk 聚合成整篇文本（Parent-Child 的 parent 视图）。

    检索用 child chunk（向量/关键词匹配精度高），但喂给 LLM 的上下文用整篇
    parent —— 避免模型只看到单段、漏掉同篇其它段落的关键事实（如
    lru_mechanism.md「最久未访问的在表尾」落在另一段时，单段上下文会让模型
    答错或被判 unsupported）。parent_id 即 source 自身；不再重新切分、不破坏
    中文语义边界。超长文档按 cap 截断，避免喂爆上下文窗口。

    cap 为什么是 20000 而不是原来的 4000：
    source_full 的主要消费者是 eval_generation 的 Judge —— 它要逐条核验 claim
    是否被原文支持，看不到的部分一律判 unsupported。原 cap=4000 从篇首硬截，
    而 knowledge/ 单篇平均 1.9 万字、book/ 每个 parent 平均 7215 字（43 个全部
    超过 4000），关键事实落在截断线之后时会被误判成幻觉（实测 [18] 排序复杂度
    faith=0.26、[35] 图找环 faith=0.29 都是这么来的，属于评测假阴性而非真幻觉）。
    生产路径受影响较小（llm._passage_text 优先走 parent_index 窗口，
    source_full 只是回退），但 Judge 必然踩中，因此放宽到 20000。
    """
    source_full = {}
    for c in chunks:
        s = str(c.get("metadata", {}).get("source", "")).replace("\\", "/")
        if s:
            source_full[s] = (source_full.get(s, "") + "\n\n" + c["text"]).strip()
    return {s: t[:cap] for s, t in source_full.items()}


def build_parent_index(chunks):
    """建 {source: [child_text, ...]} 有序映射，供 Parent-Child 动态取「命中段窗口」。

    检索命中某 child 后，喂给主 LLM 的上下文不取整篇（2~4 万字大文件会喂爆
    上下文窗口），而是以命中 child 为中心、取其同 source 前后各 window 个 ## 段
    拼成 parent 窗口（见 llm._passage_text）。粒度介于单 child 与整篇之间：
    既补上同篇相邻段漏看的关键事实，又不把巨文件整篇塞进上下文。
    """
    idx = {}
    for c in chunks:
        s = str(c.get("metadata", {}).get("source", "")).replace("\\", "/")
        if s:
            idx.setdefault(s, []).append(c["text"])
    return idx


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    cs = load_chunks(os.path.join(here, "data"))
    print(f"{len(cs)} chunks loaded")
    for c in cs[:3]:
        print("-", c["metadata"])
