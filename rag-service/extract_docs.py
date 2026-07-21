"""从引擎层头文件自动抽取接口讲解文档（亮点功能：版权安全、与动画一致）。

扫描 src/core/*.h，解析每个数据结构的 public 方法签名与紧跟的注释，
生成 data/generated/<ClassName>.md，带 structure 元数据。
"""
import os
import re
import glob

CORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "core")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "generated")

CLASS_RE = re.compile(r"class\s+(\w+)\s*(?::\s*public\s+\w+)?\s*\{")
METHOD_RE = re.compile(
    r"(?:virtual\s+)?[\w:<>\s&*]+\b(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*(?:override)?\s*(?:=\s*0)?\s*;"
)
PUB_RE = re.compile(r"public\s*:")


def parse_header(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    class_name = None
    in_public = False
    methods = []
    comments = []
    for line in lines:
        m = CLASS_RE.search(line)
        if m:
            class_name = m.group(1)
        if PUB_RE.search(line):
            in_public = True
            continue
        if "private" in line or "protected" in line:
            in_public = False
        if line.strip().startswith("//") or line.strip().startswith("///"):
            comments.append(line.strip().lstrip("/").strip())
            continue
        if in_public:
            mm = METHOD_RE.search(line)
            if mm and mm.group(1) not in ("if", "for", "while", "switch", "return"):
                methods.append((mm.group(1), mm.group(2).strip(), list(comments)))
                comments = []
            else:
                comments = []
    return class_name, methods


def op_from_name(name):
    n = name.lower()
    for kw in ("insert", "add", "push", "enqueue", "pushfront", "pushback"):
        if n.startswith(kw):
            return "insert"
    for kw in ("delete", "remove", "pop", "dequeue", "erase", "poll"):
        if n.startswith(kw):
            return "delete"
    for kw in ("find", "search", "contains", "get", "peek", "top"):
        if n.startswith(kw):
            return "query"
    if "rotat" in n:
        return "rotation"
    if "balanc" in n:
        return "balance"
    return "other"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    headers = sorted(glob.glob(os.path.join(CORE_DIR, "*.h")))
    count = 0
    for h in headers:
        name, methods = parse_header(h)
        if not name or not methods:
            continue
        out = []
        out.append("---\n")
        out.append(f"structure: {name}\n")
        out.append("operation: mixed\n")
        out.append("phase: api\n")
        out.append("difficulty: medium\n")
        out.append("---\n\n")
        out.append(f"# {name} 接口讲解（由引擎头文件自动抽取）\n\n")
        out.append(
            f"> 本文件由 `extract_docs.py` 从 `src/core/{os.path.basename(h)}` 自动生成，"
            f"与可视化实现保持一致。\n\n"
        )
        for mname, margs, mcomments in methods:
            op = op_from_name(mname)
            out.append(f"## {mname}({margs})\n\n")
            out.append(f"- 操作类型: `{op}`\n")
            if mcomments:
                out.append("\n".join(f"- {c}" for c in mcomments) + "\n")
            else:
                out.append("- 说明: （头文件未提供注释，请结合源码实现阅读）\n")
            out.append("\n")
        with open(os.path.join(OUT_DIR, name + ".md"), "w", encoding="utf-8") as f:
            f.write("".join(out))
        count += 1
        print(f"generated {name}.md ({len(methods)} methods)")
    print(f"done: {count} files -> {OUT_DIR}")


if __name__ == "__main__":
    main()
