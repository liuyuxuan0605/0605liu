"""从《Open Data Structures》(DataBook.pdf) 抽取每页文本为 Markdown 片段，
作为 RAG 的通用知识库（放入 data/open/，structure 留空 → 任意数据结构演示时均可召回）。

关键点：原书是英文，而用户常用中文提问。纯英文词无法与中文查询命中，
因此每页额外注入"中文关键词"行（基于英→中术语表），让中文提问也能召回本书。

用法:
    python extract_pdf.py            # 默认读取 D:/ai_canshow/DataBook.pdf
    python extract_pdf.py "路径.pdf" # 也可指定其他 PDF

仅抽取文本长度达阈值的页（跳过纯图页），降低噪声。
依赖: PyPDF2 (pip install PyPDF2)
"""
import os
import re
import sys

try:
    import PyPDF2
except ImportError:
    print("需要 PyPDF2：pip install PyPDF2")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = "D:/ai_canshow/DataBook.pdf"
OUT_DIR = os.path.join(HERE, "data", "open")
MIN_CHARS = 60  # 短于此的页视为图页，跳过

# 英 → 中术语表：命中英文术语时，注入对应的中文词，使中文查询可召回
TERM_ZH = {
    "array": "数组", "linked list": "链表", "doubly-linked": "双向链表",
    "skip list": "跳表", "skiplist": "跳表",
    "stack": "栈", "queue": "队列", "deque": "双端队列",
    "hash table": "哈希表", "hash map": "哈希表", "hashing": "哈希", "hash": "哈希",
    "binary search tree": "二叉搜索树", "bst": "二叉搜索树",
    "red-black": "红黑树", "red black": "红黑树",
    "avl": "AVL树", "scapegoat": "替罪羊树",
    "2-4 tree": "2-4树", "b-tree": "B树", "b+ tree": "B+树", "b tree": "B树",
    "binary heap": "二叉堆", "heap": "堆", "leftist": "左偏堆", "melding": "合并堆",
    "binary tree": "二叉树", "tree": "树",
    "graph": "图", "depth-first": "深度优先搜索", "breadth-first": "广度优先搜索",
    "mergesort": "归并排序", "quicksort": "快速排序", "sort": "排序",
    "priority queue": "优先队列", "probability": "概率", "random": "随机",
    "amortized": "摊还分析", "analysis": "复杂度分析",
}


def guess_title(text):
    """从第 1~5 行里挑一个像章节标题的短行。"""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if 3 <= len(s) <= 60 and not s[0].isdigit() and "Figure" not in s and "Table" not in s:
            return s
    return ""


def chinese_keywords(text):
    low = text.lower()
    hits = []
    for en, zh in TERM_ZH.items():
        if en in low and zh not in hits:
            hits.append(zh)
    return hits


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    if not os.path.exists(src):
        print(f"找不到 PDF: {src}")
        sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)

    reader = PyPDF2.PdfReader(src)
    n = len(reader.pages)
    written = skipped = 0
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if len(text) < MIN_CHARS:
            skipped += 1
            continue
        title = guess_title(text)
        zh = chinese_keywords(text)
        zh_line = f"\n\n（中文关键词：{'、'.join(zh)}）\n" if zh else ""
        # structure: 后留空 → 通用文档（任意 structure 查询都能命中）
        md = (
            f"---\n"
            f"structure:\n"
            f"source: open/ods_p{i:03d}.md\n"
            f"page: {i}\n"
            f"---\n\n"
            f"# ODS p{i}: {title}\n\n"
            f"{text}{zh_line}"
        )
        with open(os.path.join(OUT_DIR, f"ods_p{i:03d}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        written += 1
    print(f"PDF 共 {n} 页 → 写入 {written} 个片段，跳过图页 {skipped} 个 → {OUT_DIR}")


if __name__ == "__main__":
    main()
