# -*- coding: utf-8 -*-
"""用 pdfplumber + PDF 书签层级，把中文版《Open Data Structures》(DataBook-mono.pdf)
切成**语义完整**的 Markdown 片段，产物入 data/book_zh/。

⚠️ 维护约定（review S9）：本文件与 extract_pdf_plumber.py 是同源拷贝（相似度 ~0.8），
均为一次性语料生成脚本，语料已产出并入索引。不抽公共基模块（对一次性脚本是过度设计），
也不再双份维护：若需重新生成语料，以**本文件（中文版）为准**修改——book_zh/ 是当前
主语料；英文版脚本仅作历史参考保留，不要同步改它。

与英文版 extract_pdf_plumber.py 同源，关键差异只在「标题怎么找」：
- 英文 PDF 书签标题与正文标题同语言，用 `norm(标题)` 在正文做字符级匹配即可。
- 中文 PDF 的**书签标题是英文**（如 `1.2.1 The Queue, Stack, and Deque Interfaces`），
  **正文标题是中文**（`1.2.1 队列、栈和双端队列接口`）。字号还全 10.0，不能靠字号分标题。
  → 改为「用书签的小节编号前缀（`1.2.1`）在 destination page 附近抓中文标题行」。
  已验证稳：`1.2.1→队列、栈和双端队列接口`、`2.3→ArrayQueue：基于数组的队列`、
  `13.1→二进制字典树：一种数字搜索树`、`4.2→跳表集合：一种高效的集合`。

其余复用英文版已验证的工程点：
- x_tolerance=1.0 修复空格丢失（中文无空格问题，但保留以统一行为）。
- 页眉（含 § 的短首行）/ 页脚（纯数字末行）剔除。
- 一个文件 = 一个 level2 节（天然 parent），文件内 ## = level3 小节（child）；
  chunks.py 自动按 ## 切 child、按 source 聚合 parent —— Parent-Child 的 parent_id
  关联零代码改动。
- 超长 child 二次切分（2500 上限）+ 段落还原。
- 逐 child 注入中文关键词（≤6）+ 英文 structure 名（帮「中文查询翻英文」时英文向量对齐中文 doc）。

用法:
    python extract_pdf_plumber_zh.py                 # 写入 data/book_zh/
    python extract_pdf_plumber_zh.py --dry           # 只打印统计
    python extract_pdf_plumber_zh.py --keep-exercises
"""
import argparse
import os
import re
import sys

try:
    import pdfplumber
    from pdfminer.pdftypes import resolve1
except ImportError:
    print("need pdfplumber: pip install pdfplumber")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = "D:/ai_canshow/DataBook-mono.pdf"
OUT_DIR = os.path.join(HERE, "data", "book_zh")

X_TOL = 1.0
MIN_SECTION_CHARS = 200

# 非正文书签（目录/致谢/参考文献/索引）：中文 PDF 同样有这些英文书签
SKIP_TOP = {
    "front matter", "contents", "acknowledgments", "why this book?",
    "bibliography", "index",
}

# 章号 -> 14 种数据结构的 structure 名（与英文版一致，按 sec_no 判）
SECTION_STRUCTURE = {
    "2.1": "Stack", "2.2": "Stack", "2.6": "Stack",
    "2.3": "Queue",
    "2.4": "Deque", "2.5": "Deque",
    "3.1": "SinglyLinkedList",
    "3.2": "DoublyLinkedList", "3.3": "DoublyLinkedList",
    "5.1": "HashMap", "5.2": "HashMap", "5.3": "HashMap",
    "6.1": "BST", "6.2": "BST",
    "7.1": "BST", "7.2": "BST",
    "8.1": "AVLTree",
    "9.1": "RedBlackTree", "9.2": "RedBlackTree", "9.3": "RedBlackTree",
    "10.1": "MinHeap", "10.2": "MinHeap",
    "14.2": "BTree",
}
CHAPTER_STRUCTURE = {
    "2": "Stack", "3": "SinglyLinkedList", "5": "HashMap",
    "6": "BST", "7": "BST", "8": "AVLTree", "9": "RedBlackTree",
    "10": "MinHeap", "14": "BTree",
}

# 英文术语 -> 中文关键词（与英文版一致；中文正文里英文术语出现少，注入中文同义词帮对齐）
TERM_ZH = {
    "array": "数组", "linked list": "链表", "doubly-linked": "双向链表",
    "singly-linked": "单向链表", "skiplist": "跳表", "skip list": "跳表",
    "stack": "栈", "queue": "队列", "deque": "双端队列",
    "hash table": "哈希表", "hashing": "哈希", "hash code": "哈希码",
    "binary search tree": "二叉搜索树", "red-black": "红黑树",
    "scapegoat": "替罪羊树", "treap": "树堆", "2-4 tree": "2-4树",
    "b-tree": "B树", "binary heap": "二叉堆", "heap": "堆",
    "meldable": "可合并堆", "binary tree": "二叉树", "tree": "树",
    "graph": "图", "breadth-first": "广度优先搜索", "depth-first": "深度优先搜索",
    "adjacency matrix": "邻接矩阵", "adjacency list": "邻接表",
    "merge-sort": "归并排序", "mergesort": "归并排序",
    "quicksort": "快速排序", "heap-sort": "堆排序", "radix": "基数排序",
    "counting sort": "计数排序", "sorting": "排序",
    "priority queue": "优先队列", "amortized": "摊还分析",
    "rotation": "旋转", "traversal": "遍历", "recursion": "递归",
    "probability": "概率", "randomized": "随机化", "complexity": "复杂度",
    "trie": "字典树", "external memory": "外存",
}


# --------------------------------------------------------------------------
# 文本提取
# --------------------------------------------------------------------------
def page_text(pg):
    """提取单页文本，剔除页眉（含 § 的短首行）与页脚（纯数字末行）。"""
    t = pg.extract_text(x_tolerance=X_TOL) or ""
    lines = t.split("\n")
    if lines and "\u00a7" in lines[0] and len(lines[0]) < 80:
        lines = lines[1:]
    while lines and re.fullmatch(r"\s*\d{1,4}\s*", lines[-1] or ""):
        lines = lines[:-1]
    return "\n".join(lines)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def strip_num(title):
    return re.sub(r"^\d+(\.\d+)*\s*", "", title).strip()


def sec_no(title):
    m = re.match(r"^(\d+(?:\.\d+)*)", title)
    return m.group(1) if m else ""


# --------------------------------------------------------------------------
# 书签解析（同英文版：把 named destination 解析成页码）
# --------------------------------------------------------------------------
def read_outline(pdf):
    doc = pdf.doc
    pmap = {p.page_obj.pageid: i for i, p in enumerate(pdf.pages)}

    def dest_page(a):
        d = a.get("D") if isinstance(a, dict) else None
        if isinstance(d, bytes):
            try:
                d = resolve1(doc.get_dest(d))
            except Exception:
                return None
        d = resolve1(d)
        if isinstance(d, dict):
            d = d.get("D")
        if isinstance(d, list) and d:
            return pmap.get(getattr(d[0], "objid", None))
        return None

    out = []
    for lvl, title, dest, action, se in doc.get_outlines():
        p = dest_page(resolve1(action))
        if p is not None:
            out.append({"level": lvl, "title": title.strip(), "page": p})
    return out


def find_zh_title(full, page_off, page, no):
    """在 destination page 附近（±1 页）找「以小节编号 no 开头」的中文标题行。

    返回 (该标题行在 full 中的字符 offset, 标题文本)；找不到返回 (None, None)。
    用编号前缀而非整标题匹配：书签是英文、正文是中文，但两者编号严格一致，
    编号是稳定的锚点。页可能落在图页，故向后多扫一页。
    """
    lo = max(0, page - 1)
    hi = min(len(page_off) - 1, page + 1)
    start = page_off[lo]
    end = page_off[hi + 1] if hi + 1 < len(page_off) else len(full)
    window = full[start:end]
    pat = re.compile(r"^" + re.escape(no) + r"([\s.:。、：]|$)")
    for line in window.split("\n"):
        s = line.strip()
        if pat.match(s):
            idx = window.find(line)
            return start + idx, s
    return None, None


def locate_zh(marks, full, page_off):
    """把每条书签定位到正文的标题行 + 字符 offset（中文版专用）。"""
    for m in marks:
        no = sec_no(m["title"])
        off, title = find_zh_title(full, page_off, m["page"], no) if no else (None, None)
        if off is not None:
            m["title"] = title
            m["offset"] = off
            # 标题行结尾（含标题文本本身），正文从下一字符开始
            m["end_of_title"] = off + len(title)
        else:
            # 兜底：拿不到中文标题就退回页起点，正文从页首开始（多切一点，不丢内容）
            m["offset"] = page_off[min(m["page"], len(page_off) - 1)]
            m["end_of_title"] = m["offset"]
            m["fuzzy"] = True
    return marks


# --------------------------------------------------------------------------
# 组装（与英文版同逻辑）
# --------------------------------------------------------------------------
def clean_body(s):
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


MAX_CHILD_CHARS = 2500


def to_paragraphs(body):
    """PDF 提取是逐行的、段落间无空行，按启发式还原段落。"""
    lines = [l for l in body.split("\n")]
    paras, cur = [], []
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                paras.append("\n".join(cur))
                cur = []
            continue
        if cur:
            prev = cur[-1].rstrip()
            if prev.endswith((".", "!", "?", ":", "。", "！", "？")) and re.match(r"[A-Z0-9一-鿿\u2022]", s):
                paras.append("\n".join(cur))
                cur = []
        cur.append(s)
    if cur:
        paras.append("\n".join(cur))
    return paras


def split_long(body, max_chars=MAX_CHILD_CHARS):
    if len(body) <= max_chars:
        return [body]
    out, cur = [], ""
    for p in to_paragraphs(body):
        if cur and len(cur) + len(p) + 2 > max_chars:
            out.append(cur.strip())
            cur = p
        else:
            cur = (cur + "\n" + p) if cur else p
    if cur.strip():
        out.append(cur.strip())
    return out or [body]


def pick_structure(chap_no, sect_no):
    if sect_no in SECTION_STRUCTURE:
        return SECTION_STRUCTURE[sect_no]
    return CHAPTER_STRUCTURE.get(chap_no, "")


MAX_ZH_TERMS = 6


def chinese_keywords(text, limit=MAX_ZH_TERMS):
    """按术语在块中出现频次取 top-N 中文关键词（与英文版同逻辑，限量防万能匹配）。"""
    low = text.lower()
    scored = []
    for en, zh in TERM_ZH.items():
        c = low.count(en)
        if c:
            scored.append((c, len(en), zh))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    out = []
    for _, _, zh in scored:
        if zh not in out:
            out.append(zh)
        if len(out) >= limit:
            break
    return out


def build_sections(marks, full, keep_exercises):
    """按 level2 聚合成 section（与英文版同逻辑，标题已是中文）。"""
    marks = [m for m in marks if m["title"].strip().lower() not in SKIP_TOP]
    marks.sort(key=lambda m: m["offset"])

    sections = []
    cur_chapter = ""
    i = 0
    while i < len(marks):
        m = marks[i]
        if m["level"] == 1:
            cur_chapter = m["title"]
            i += 1
            continue
        if m["level"] != 2:
            i += 1
            continue

        end = len(full)
        j = i + 1
        subs = []
        while j < len(marks):
            if marks[j]["level"] <= 2:
                end = marks[j]["offset"]
                break
            subs.append(marks[j])
            j += 1

        title = m["title"]
        if not keep_exercises and "exercise" in title.lower():
            i = j
            continue

        blocks = []
        if subs:
            lead = clean_body(full[m["end_of_title"]:subs[0]["offset"]])
            if lead:
                blocks.append(("", lead))
            for k, s in enumerate(subs):
                s_end = subs[k + 1]["offset"] if k + 1 < len(subs) else end
                body = clean_body(full[s["end_of_title"]:s_end])
                if body:
                    blocks.append((s["title"], body))
        else:
            body = clean_body(full[m["end_of_title"]:end])
            if body:
                blocks.append(("", body))

        sections.append({
            "chapter": cur_chapter,
            "title": title,
            "page": m["page"],
            "blocks": blocks,
            "fuzzy": m.get("fuzzy", False),
        })
        i = j
    return sections


def render(sec):
    chap_no = sec_no(sec["chapter"])
    s_no = sec_no(sec["title"])
    structure = pick_structure(chap_no, s_no)
    # 文件名只用小节编号（唯一、稳定、无中文编码风险）：book_zh/ods_zh_2_3.md
    name = "ods_zh_" + (s_no.replace(".", "_") if s_no else "sec") + ".md"
    src = "book_zh/" + name

    lines = [
        "---",
        "structure: " + structure,
        "source: " + src,
        "chapter: " + sec["chapter"],
        "section: " + s_no,
        "page: " + str(sec["page"] + 1),
        "kind: textbook",
        "---",
        "",
        "# " + sec["title"],
        "",
    ]
    n_child = 0
    for sub_title, body in sec["blocks"]:
        parts = split_long(body)
        for k, part in enumerate(parts):
            t = sub_title
            if len(parts) > 1:
                base = sub_title or strip_num(sec["title"])
                t = "%s (%d/%d)" % (base, k + 1, len(parts))
            if t:
                lines.append("## " + t)
                lines.append("")
            lines.append(part)
            # 逐 child 注入（关键坑：放文件末尾只有最后一段带词 → 所有中文查询被吸到末段）
            zh = chinese_keywords((t or sec["title"]) + "\n" + part)
            extra = []
            if zh:
                extra.append("中文关键词：" + "、".join(zh))
            # 注入英文 structure 名：帮「中文查询翻英文」时英文向量对齐中文 doc 召回
            if structure:
                extra.append("英文术语：" + structure)
            if extra:
                lines.append("")
                lines.append("（" + "；".join(extra) + "）")
            lines.append("")
            n_child += 1
    return name, "\n".join(lines), n_child


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", default=DEFAULT_SRC)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--keep-exercises", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        print("PDF not found: " + args.src)
        sys.exit(1)

    pdf = pdfplumber.open(args.src)
    marks = read_outline(pdf)

    texts, page_off, cur = [], [], 0
    for pg in pdf.pages:
        t = page_text(pg)
        page_off.append(cur)
        texts.append(t)
        cur += len(t) + 1
    full = "\n".join(texts)

    marks = locate_zh(marks, full, page_off)
    fuzzy = [m["title"] for m in marks if m.get("fuzzy")]

    sections = build_sections(marks, full, args.keep_exercises)

    print("pages=%d  outline=%d  chars=%d" % (len(pdf.pages), len(marks), len(full)))
    if fuzzy:
        print("fallback-located (%d): %s" % (len(fuzzy), fuzzy))

    total = 0
    n_child = 0
    written = 0
    for sec in sections:
        name, md, kids = render(sec)
        body_len = sum(len(b) for _, b in sec["blocks"])
        if body_len < MIN_SECTION_CHARS:
            print("  SKIP(too short) %-52s %d" % (sec["title"][:50], body_len))
            continue
        total += body_len
        n_child += kids
        if not args.dry:
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
                f.write(md)
        written += 1
        print("  %-46s child=%-3d chars=%-6d -> %s" % (
            sec["title"][:44], kids, body_len, name))

    print("\nsections(parent)=%d  child-blocks=%d  chars=%d  avg-parent=%d" % (
        written, n_child, total, total // max(written, 1)))
    if args.dry:
        print("(dry run, nothing written)")
    else:
        print("written -> " + OUT_DIR)


if __name__ == "__main__":
    main()
