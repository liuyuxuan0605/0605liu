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


SUBDIRS = ("interview", "notes", "generated", "open")


def load_chunks(data_dir):
    chunks = []
    files = []
    for sub in SUBDIRS:
        d = os.path.join(data_dir, sub)
        if os.path.isdir(d):
            files += glob.glob(os.path.join(d, "*.md"))

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_frontmatter(raw)
        structure = meta.get("structure") or os.path.splitext(os.path.basename(fp))[0]

        parts = re.split(r"(?m)^#{1,3}\s+(.*)$", body)
        heading = "概览"

        def flush(h, b):
            if not b.strip():
                return
            text = (("# " + h + "\n") if h else "") + b.strip()
            chunks.append({
                "text": text,
                "metadata": {
                    "source": os.path.relpath(fp, data_dir),
                    "structure": structure,
                    "operation": meta.get("operation", ""),
                    "phase": meta.get("phase", ""),
                    "difficulty": meta.get("difficulty", ""),
                    "heading": h,
                },
                "terms": _terms(text),
            })

        if parts[0].strip():
            flush(heading, parts[0])
        for i in range(1, len(parts), 2):
            h = parts[i].strip()
            b = parts[i + 1] if i + 1 < len(parts) else ""
            flush(h, b)

    return chunks


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    cs = load_chunks(os.path.join(here, "data"))
    print(f"{len(cs)} chunks loaded")
    for c in cs[:3]:
        print("-", c["metadata"])
