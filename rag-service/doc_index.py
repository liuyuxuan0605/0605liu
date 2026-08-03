# -*- coding: utf-8 -*-
"""文档增量索引：用「内容 hash + mtime 粗筛」做到只重切/重嵌变化的文档。

为什么需要它
------------
之前两个向量后端（Semantic/Chroma）都是「data/ 任意文件 mtime 一变就全量重建」
（Chroma 删全部再 add；Semantic 重嵌全部）。语料只有几百篇、但每次嵌入都要调
DashScope API —— 改一个笔记就触发全量重嵌，既慢又烧 key。

本模块把索引状态外置成一个 manifest（`data/.doc_index.json`），记录每个文档的
`doc_id → {mtime, hash(sha256), chunk_ids}`：
- **mtime 粗筛**：mtime 没变 → 直接跳过，不读内容、不算 hash（绝大多数轮询都是这情况）。
- **content hash 精判**：mtime 变了才读文件算 sha256，和旧 hash 比；一致说明只是
  touch/同内容落盘，不重嵌，仅更新 mtime。
- **真正变化的文档**才重切（chunk_file）并重嵌；磁盘上消失的文档取其旧 chunk_ids 清向量。

轮询检测：server.py 后台线程每 ~30s 调一次 compute_sync_plan，只对变化的文档触发
retriever.sync（清旧向量 + 重嵌变更）。首次启动 manifest 为空 → 全量（仅一次）。

manifest 是隐藏文件（`.doc_index.json`），不被 `*.md` glob 当成 chunk。
"""
import os
import json
import hashlib
import glob

from chunks import SUBDIRS, chunk_file, sanitize_id


MANIFEST_NAME = ".doc_index.json"


def _manifest_path(data_dir):
    return os.path.join(data_dir, MANIFEST_NAME)


def load_manifest(data_dir):
    p = _manifest_path(data_dir)
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 损坏则作废，交给全量重建
        return {}


def save_manifest(data_dir, manifest):
    p = _manifest_path(data_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)  # 原子替换，避免写到一半被轮询线程读走


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def compute_sync_plan(data_dir, manifest):
    """扫描 data/ 下所有 .md，对比 manifest，产出增量计划。

    返回:
        {
          "rechunk": {doc_id: [chunk, ...]},   # 新增或修改 → 需重切重嵌
          "remove":  {doc_id: [chunk_id, ...]}, # 修改或删除 → 需清旧向量
          "new_manifest": {doc_id: {mtime, hash, chunk_ids}},
        }
    rechunk 里的 chunk 已带稳定 id（sanitize(source)+"_"+i），retriever 直接用于
    增量 add；remove 里是旧 chunk_ids，retriever 直接用于增量 delete。

    ⚠️ **修改的文档同时出现在 remove 和 rechunk 里**，这是「先删后增」语义的关键，
    不是冗余。原始文档与 chunk 是一对多关系：内容一改，切分结果的数量/边界/内容
    可能完全不同，无法逐条 update，只能整篇先清后建。漏掉这一支会同时产生三个
    静默错误（详见下方真变化分支的注释）。
    """
    rechunk = {}
    remove = {}
    new_manifest = {}
    seen = set()

    for sub in SUBDIRS:
        d = os.path.join(data_dir, sub)
        if not os.path.isdir(d):
            continue
        for fp in glob.glob(os.path.join(d, "*.md")):
            rel = os.path.relpath(fp, data_dir).replace("\\", "/")
            doc_id = sanitize_id(rel)
            seen.add(doc_id)
            mtime = os.path.getmtime(fp)

            old = manifest.get(doc_id)
            # —— 粗筛：mtime 没变，内容必没变（不读文件、不算 hash）——
            if old is not None and old.get("mtime") == mtime:
                new_manifest[doc_id] = old
                continue

            # —— 精判：算内容 hash，与旧 hash 比 ——
            h = _sha256(fp)
            if old is not None and old.get("hash") == h:
                # 内容未变（仅 mtime 变了，如 git checkout / touch），沿用旧 chunk_ids
                new_manifest[doc_id] = {"mtime": mtime, "hash": h,
                                        "chunk_ids": old.get("chunk_ids", [])}
                continue

            # —— 真变化（新增或修改）→ 重切 ——
            chunks = chunk_file(fp, data_dir)
            if old is not None:
                # 【修改】必须先清掉这篇文档的**全部**旧 chunk，再入新的。
                # 少了这一句会同时踩三个静默坑（均已实测确认）：
                #   ① chromadb 1.5.9 同 id 再 add 是「静默忽略」而非覆盖 —— 不抛异常、
                #      不告警、count 不变，库里留着旧向量，改动完全不生效；
                #   ② Naive/Semantic 是 list 追加 —— 同一段话的新旧两版并存、id 重复，
                #      检索会同时命中两个版本；
                #   ③ 文档「改小」时（如 5 段删成 3 段）旧的 _3/_4 无人清理，成为永久
                #      孤儿向量 —— 已经从文档里删掉的内容仍能被检索到。
                # 注意取的是 old（manifest 里的旧 id 列表）而非新 chunks 的 id：
                # 段落增删会让 _i 位置编号整体平移，只删「新 id」清不干净旧的尾巴。
                remove[doc_id] = old.get("chunk_ids", [])
            new_manifest[doc_id] = {
                "mtime": mtime,
                "hash": h,
                "chunk_ids": [c["id"] for c in chunks],
            }
            rechunk[doc_id] = chunks

    # —— 磁盘消失的文档 → removed（取其旧 chunk_ids）——
    for doc_id, old in manifest.items():
        if doc_id not in seen:
            remove[doc_id] = old.get("chunk_ids", [])

    return {"rechunk": rechunk, "remove": remove, "new_manifest": new_manifest}


def flatten_chunk_ids(rechunk, remove):
    """把同步计划摊平成「要删的 id 集合 / 要加的 chunk 列表」，供 retriever.sync。"""
    to_remove = [cid for ids in remove.values() for cid in ids]
    to_add = [c for chunks in rechunk.values() for c in chunks]
    return to_remove, to_add
