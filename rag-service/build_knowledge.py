# -*- coding: utf-8 -*-
"""预处理 VisuAlgo 知识点文档，清洗后写入 rag-service/data/knowledge/。

这些文档作为 **theory 类**检索资料（与 src/core/*.h 的 implementation 类源码互补）：
- implementation：DSVisualizer 各数据结构的 C++ 实现，仅看该结构时召回
- theory：数据结构/算法原理讲解（来源 VisuAlgo），跨结构始终参与召回

源目录（用户机器上的外部工作区）：
  C:/Users/13035/.qoderworkcn/workspace/mrvyb4qpria56due/rag_knowledge
目标目录（本项目内，自包含）：
  <本脚本所在目录>/data/knowledge

运行：python build_knowledge.py
"""
import os
import re
import glob
import html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:/Users/13035/.qoderworkcn/workspace/mrvyb4qpria56due/rag_knowledge"
DST = os.path.join(HERE, "data", "knowledge")

# 理论文档的主题结构名（仅作 metadata 标签；theory 类检索时不受 structure 过滤）
STRUCT_MAP = {
    "array": "Array",
    "list": "List",
    "bst": "BST",
    "heap": "Heap",
    "hashtable": "HashMap",
    "graphds": "Graph",
    "ufds": "UFDS",
    "fenwicktree": "FenwickTree",
    "segmenttree": "SegmentTree",
    "dfsbfs": "GraphTraversal",
    "mst": "MST",
    "sssp": "SSSP",
    "sorting": "Sorting",
    "bitmask": "Bitmask",
    "recursion": "Recursion",
    "cyclefinding": "CycleFinding",
    # README.md 是目录索引，无映射 → 跳过
}

# 只删真正的 HTML 标签，避免误伤 "a < b" 之类不等式
HTML_RE = re.compile(
    r"</?(?:p|b|i|u|li|ul|ol|span|div|center|sub|sup|pre|br|h[1-6]|"
    r"a|img|em|strong|code|button|form|input|table|tr|td|th|tbody|thead|small|big)\b[^>]*>",
    re.IGNORECASE,
)
# 去掉「来源 / 幻灯片数量」等噪音行
NOISE_RE = re.compile(r"^\*\*(?:来源|幻灯片数量)\*\*.*$", re.M)
# 去掉标题编号（"## 1. Foo" -> "## Foo"）
HEAD_RE = re.compile(r"(?m)^(#{1,3})\s+\d+\.\s+")


def main():
    os.makedirs(DST, exist_ok=True)
    n = 0
    for fp in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        name = os.path.splitext(os.path.basename(fp))[0]
        if name not in STRUCT_MAP:  # 跳过 README 等无映射文件
            print("skip (no mapping):", name)
            continue
        with open(fp, encoding="utf-8") as f:
            raw = f.read()
        raw = html.unescape(raw)
        raw = NOISE_RE.sub("", raw)
        raw = HTML_RE.sub("", raw)
        raw = HEAD_RE.sub(r"\1 ", raw)
        raw = re.sub(r"(?m)^#\s+.*$", "", raw)      # 删除原文件一级标题（脚本已加自己的）
        raw = re.sub(r"(?m)^\s*---\s*$", "", raw)   # 删除幻灯片分隔符
        raw = re.sub(r"\n{3,}", "\n\n", raw).strip() + "\n"

        struct = STRUCT_MAP[name]
        out = [
            "---\n",
            f"structure: {struct}\n",
            "kind: theory\n",
            "operation: mixed\n",
            "phase: concept\n",
            "difficulty: medium\n",
            "---\n\n",
            f"# {struct} 知识点（理论讲解，来源 VisuAlgo）\n\n",
            raw,
        ]
        with open(os.path.join(DST, name + ".md"), "w", encoding="utf-8") as f:
            f.write("".join(out))
        n += 1
        print(f"processed {name}.md -> structure={struct}")
    print(f"done: {n} theory docs -> {DST}")


if __name__ == "__main__":
    main()
