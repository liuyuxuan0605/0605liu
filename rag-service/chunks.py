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
# book_zh/ 由 extract_pdf_plumber_zh.py 生成：ODS 教材中文版（DataBook-mono.pdf），
#   pdfplumber + PDF 书签层级做语义切分，一个文件 = 原书一个 level2 节，
#   文件内 ## = level3 小节（child）。
# book/ 是同一本书的**英文原版**（extract_pdf_plumber.py 生成，切分逻辑一致）。
#   ⚠️ 默认**不参与检索**：与 book_zh/ 内容完全重复，中文问答场景下英文 child
#   只会挤占 top-k、稀释中文召回，属同源冗余。文件保留在磁盘上（可随时启用）。
#   需要临时启用英文原版时，设环境变量即可，无需改代码：
#       set RAG_SUBDIRS=interview,notes,generated,book,book_zh,knowledge
# open/ 是 book/ 的前身（extract_pdf.py + PyPDF2 按物理页切的 323 个页片段），
#   丢空格、混页眉页脚、切断语义、structure 一律留空导致任何查询都能召回，
#   是 precision 偏低的主要噪声源 —— 已被 book/ 取代，同样不再进入检索。
_DEFAULT_SUBDIRS = ("interview", "notes", "generated", "book_zh", "knowledge")

_env_subdirs = os.environ.get("RAG_SUBDIRS", "").strip()
SUBDIRS = (tuple(s.strip() for s in _env_subdirs.split(",") if s.strip())
           if _env_subdirs else _DEFAULT_SUBDIRS)


def subdirs_signature():
    """当前生效语料目录集的指纹，用于让索引缓存感知「目录集变化」。

    为什么必须有它：各 retriever 判断缓存是否过期，靠的都是「data/ 下有没有 .md
    比索引新」。而启用/隐藏一个语料目录（如隐藏 book/）只改这里的常量、**不会
    改动任何文件的 mtime** —— 于是缓存一律被判定为「未过期」，直接复用仍含
    book/ 向量的旧索引，改动静默失效。把指纹写进缓存元数据并参与过期判定，
    目录集一变就自动重建，从根上杜绝孤儿向量。

    用 sorted 是为了让「顺序调整」不触发无谓重建（集合相同即视为相同）。
    """
    return "|".join(sorted(SUBDIRS))


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


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    cs = load_chunks(os.path.join(here, "data"))
    print(f"{len(cs)} chunks loaded")
    for c in cs[:3]:
        print("-", c["metadata"])
