# -*- coding: utf-8 -*-
"""用 pdfplumber + PDF 书签层级，把《Open Data Structures》(DataBook.pdf)
切成**语义完整**的 Markdown 片段，替代旧的 extract_pdf.py（PyPDF2 按物理页切）。

旧方案的问题
------------
1. 按物理页切：一节内容被拦腰截断，一页里可能塞两个不相干小节 -> 检索命中的
   片段常常缺上下文、或混入无关内容，是 precision 偏低的主要噪声源。
2. PyPDF2 提取丢空格：`operationssupportedbytheQueueinterfaceare`，
   TF-IDF 关键词路基本失效（分不出词），向量质量也受损。
3. 页眉页脚（`Interfaces §1.2` / 页码）混进正文。
4. `structure:` 一律留空 -> 任何数据结构的查询都能召回这 323 个页片段。

新方案
------
* pdfplumber + `x_tolerance=1.0` 修复空格丢失（空格占比 0.056 -> 0.151）。
* 用 PDF 自带的 148 条书签（含 level1 章 / level2 节 / level3 小节）做切分边界，
  书签只精确到页，因此再用「标题文本在正文中的位置」二次定位到字符级。
* **一个输出文件 = 一个 level2 节**，文件内用 `##` 标记 level3 小节。
  这样现有 chunks.py 会自动把每个 `##` 切成 child chunk，而 source（文件）
  天然就是 parent —— Parent-Child 的 parent_id 关联无需改任何代码。
  一个 level2 节通常 3000~8000 字，整篇当 parent 上下文也不会爆。
* 按章节标题映射 `structure`（如 2.3 ArrayQueue -> Queue），
  只有真正通用的内容（数学基础、排序、图）才留空。
* 保留旧脚本的中文关键词注入（原书是英文，用户用中文提问）。

用法:
    python extract_pdf_plumber.py                 # 写入 data/book/
    python extract_pdf_plumber.py --dry           # 只打印统计，不写文件
    python extract_pdf_plumber.py --keep-exercises  # 同时保留习题节

依赖: pdfplumber
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
DEFAULT_SRC = "D:/ai_canshow/DataBook.pdf"
OUT_DIR = os.path.join(HERE, "data", "book")

X_TOL = 1.0          # 关键：默认 3.0 会吞掉单词间空格
MIN_SECTION_CHARS = 200

# 非正文书签：目录/致谢/参考文献/索引，全是页码和文献列表，纯噪声
SKIP_TOP = {
    "front matter", "contents", "acknowledgments", "why this book?",
    "bibliography", "index",
}

# 章号 -> 本项目 14 种数据结构的 structure 名。留空 = 通用文档（任意结构可召回）。
# 粒度到 level2 节号，找不到时回退到章号。
SECTION_STRUCTURE = {
    "2.1": "Stack", "2.2": "Stack", "2.6": "Stack",
    "2.3": "Queue",
    "2.4": "Deque", "2.5": "Deque",
    "3.1": "SinglyLinkedList",
    "3.2": "DoublyLinkedList", "3.3": "DoublyLinkedList",
    "5.1": "HashMap", "5.2": "HashMap", "5.3": "HashMap",
    "6.1": "BST", "6.2": "BST",
    "7.1": "BST", "7.2": "BST",
    "8.1": "AVLTree",          # 替罪羊树：同属「自平衡 BST + 重建」思路
    "9.1": "RedBlackTree", "9.2": "RedBlackTree", "9.3": "RedBlackTree",
    "10.1": "MinHeap", "10.2": "MinHeap",
    "14.2": "BTree",
}
CHAPTER_STRUCTURE = {
    "2": "Stack", "3": "SinglyLinkedList", "5": "HashMap",
    "6": "BST", "7": "BST", "8": "AVLTree", "9": "RedBlackTree",
    "10": "MinHeap", "14": "BTree",
}

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
    """去掉标题前的章节编号，用于书签编号与正文不一致时的兜底匹配。"""
    return re.sub(r"^\d+(\.\d+)*\s*", "", title).strip()


# --------------------------------------------------------------------------
# 书签解析
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


def locate(marks, full, nfull, n2o, page_off):
    """把每条书签定位到正文的字符 offset。"""
    # normalized offset -> 每页起点
    def n_start_of_page(p):
        p = max(0, min(p, len(page_off) - 1))
        o = page_off[p]
        lo, hi = 0, len(n2o)
        while lo < hi:                      # n2o 单调递增，二分找第一个 >= o
            mid = (lo + hi) // 2
            if n2o[mid] < o:
                lo = mid + 1
            else:
                hi = mid
        return lo

    for m in marks:
        nt = norm(m["title"])
        start_n = n_start_of_page(max(0, m["page"] - 1))
        pos = nfull.find(nt, start_n) if nt else -1
        if pos < 0:                          # 兜底 1：去掉编号
            nt2 = norm(strip_num(m["title"]))
            if nt2:
                pos = nfull.find(nt2, start_n)
                if pos >= 0:
                    nt = nt2
        if pos < 0:                          # 兜底 2：全局搜
            pos = nfull.find(nt) if nt else -1
        if pos >= 0:
            m["offset"] = n2o[pos]
            # 注意 off-by-one：pos+len(nt)-1 才是标题最后一个字符在原文中的下标，
            # 取 pos+len(nt) 会指向正文的第一个字母并把它一起切掉
            # （曾导致 "In this section" 变成 "n this section"）。
            m["end_of_title"] = n2o[min(pos + len(nt) - 1, len(n2o) - 1)] + 1
        else:
            m["offset"] = page_off[min(m["page"], len(page_off) - 1)]
            m["end_of_title"] = m["offset"]
            m["fuzzy"] = True
    return marks


# --------------------------------------------------------------------------
# 组装
# --------------------------------------------------------------------------
def clean_body(s):
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# 单个 child chunk 的目标上限。PDF 里一个 level3 小节可能上万字
# （如 14.2 B-Trees 平均 4900 字/块、13.3 YFastTrie 单块 8142 字），
# 直接做向量检索粒度太粗，命中后噪声也多，因此超长块再按段落二次切分。
MAX_CHILD_CHARS = 2500


def to_paragraphs(body):
    """PDF 提取出来是逐行的、段落间没有空行，这里按启发式还原段落。

    规则：上一行以句末标点结尾、且当前行以大写字母/数字编号开头 -> 新段落。
    还原失败也不影响正确性，只是切点没那么漂亮。
    """
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
            if prev.endswith((".", "!", "?", ":")) and re.match(r"[A-Z0-9\u2022]", s):
                paras.append("\n".join(cur))
                cur = []
        cur.append(s)
    if cur:
        paras.append("\n".join(cur))
    return paras


def split_long(body, max_chars=MAX_CHILD_CHARS):
    """把超长正文按段落累积切成若干 <= max_chars 的片段。"""
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


def sec_no(title):
    m = re.match(r"^(\d+(?:\.\d+)*)", title)
    return m.group(1) if m else ""


def pick_structure(chap_no, sect_no):
    if sect_no in SECTION_STRUCTURE:
        return SECTION_STRUCTURE[sect_no]
    return CHAPTER_STRUCTURE.get(chap_no, "")


MAX_ZH_TERMS = 6


def chinese_keywords(text, limit=MAX_ZH_TERMS):
    """按术语在本块中的出现频次取 top-N 中文关键词。

    为什么要限量：注入的中文词会作为额外 term 进入 TF-IDF 词表。像
    「1.7 List of Data Structures」这种术语清单节会命中几十个英文术语，
    于是注入几十个中文词，任何中文查询都能匹配上 —— 成为万能匹配噪声源
    （实测它同时出现在「堆排序」「B树节点分裂」「哈希表链地址法」的 top-3）。
    只保留出现最频繁的几个，让关键词真正反映本块主题。
    """
    low = text.lower()
    scored = []
    for en, zh in TERM_ZH.items():
        c = low.count(en)
        if c:
            scored.append((c, len(en), zh))
    # 频次高优先；同频次时更长的术语（更具体，如 binary search tree）优先
    scored.sort(key=lambda x: (-x[0], -x[1]))
    out = []
    for _, _, zh in scored:
        if zh not in out:
            out.append(zh)
        if len(out) >= limit:
            break
    return out


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:60] or "section"


def build_sections(marks, full, keep_exercises):
    """按 level2 聚合成 section，每个 section 内含若干 level3 子块。"""
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

        # 该 level2 的结束位置 = 下一个 level<=2 书签的起点
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
    name = "ods_" + (s_no.replace(".", "_") + "_" if s_no else "") + slugify(strip_num(sec["title"])) + ".md"
    src = "book/" + name

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
            # 中文关键词必须逐 child 注入，不能整篇合并成一行放文件末尾：
            # chunks.py 按 ## 切 child，放末尾的话只有最后一个 child 带中文词，
            # 于是所有中文查询都被系统性地吸到「每个文件的最后一段」——
            # 实测「堆排序原理」命中的是 11.1.4 A Lower-Bound 而不是 11.1.3 Heap-sort。
            zh = chinese_keywords((t or sec["title"]) + "\n" + part)
            if zh:
                lines.append("")
                lines.append("（中文关键词：" + "、".join(zh) + "）")
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

    n2o = [i for i, ch in enumerate(full) if ch.isalnum() and ord(ch) < 128]
    nfull = "".join(full[i] for i in n2o).lower()

    marks = locate(marks, full, nfull, n2o, page_off)
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
