# -*- coding: utf-8 -*-
"""回归测试：增量索引的「修改文档」路径（先删后增）。

验证三个历史静默 bug 已修复（无 key / 无网，纯 naive 路离线可跑）：
  ① 修改文档后，compute_sync_plan 必须把它**同时**放进 rechunk(新 chunks)
     和 remove(旧 chunk_ids) —— 否则 chroma 同 id add 静默忽略、改动不生效；
  ② NaiveRetriever.sync 后，文档的新旧两版不得并存（id 不重复）；
  ③ 文档「改小」(段落减少) 时，旧尾段不得成为永久孤儿向量（能被检索到）。

运行：
    cd rag-service && python test_incremental_modify.py
"""
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chunks import chunk_file, sanitize_id
from doc_index import compute_sync_plan, save_manifest, load_manifest
from retriever import NaiveRetriever


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _run():
    tmp = tempfile.mkdtemp(prefix="incr_test_")
    data_dir = os.path.join(tmp, "data")
    gen = os.path.join(data_dir, "generated")
    try:
        # —— 初始两个文档：A(3 段) / B(2 段) —— 直接复用真实 chunk_file 派生 id ——
        a_path = os.path.join(gen, "docA.md")
        b_path = os.path.join(gen, "docB.md")
        _write(a_path,
               "# Doc A\n"
               "## s1\nOLD_A_1 content\n"
               "## s2\nOLD_A_2 content\n"
               "## s3\nOLD_A_3 content\n")
        _write(b_path,
               "# Doc B\n"
               "## t1\nB_1 content\n"
               "## t2\nB_2 content\n")

        # —— 首次：manifest 空 → 全量 rechunk，remove 为空 ——
        plan0 = compute_sync_plan(data_dir, {})
        assert len(plan0["rechunk"]) == 2, f"首次应 rechunk 2 篇，实际 {len(plan0['rechunk'])}"
        assert len(plan0["remove"]) == 0, f"首次 remove 应为空，实际 {len(plan0['remove'])}"

        doc_a_id = sanitize_id("generated/docA.md")
        doc_b_id = sanitize_id("generated/docB.md")
        # 用真实 chunk_file 派生「旧 id 列表」（不硬编码，抗切分规则变动）
        old_a_ids = [c["id"] for c in chunk_file(a_path, data_dir)]
        old_b_ids = [c["id"] for c in chunk_file(b_path, data_dir)]
        assert old_a_ids, "A 应至少切出 1 个 chunk"

        # 用 naive 全量装载（本地 TF-IDF，零 API）
        chunks_v1 = []
        for ch in plan0["rechunk"].values():
            chunks_v1.extend(ch)
        r = NaiveRetriever()
        built = r.add(chunks_v1)
        assert built is True, "naive add 应返回 True(全量重建)"
        assert r.count() == len(old_a_ids) + len(old_b_ids), \
            f"首次 count={r.count()}，应={len(old_a_ids)+len(old_b_ids)}"

        # 落地 manifest（模拟 server 启动后的 save_manifest）
        save_manifest(data_dir, plan0["new_manifest"])
        m0_mtime = os.path.getmtime(a_path)

        # —— 修改 A：内容全改 + 段落减少(3→2 段，尾巴消失) ——
        # 强制把 mtime 往后拨，确保粗筛( mtime 比较 )一定触发精判
        _write(a_path,
               "# Doc A\n"
               "## s1\nNEW_A_1 content\n"
               "## s2\nNEW_A_2 content\n")
        os.utime(a_path, (m0_mtime + 100, m0_mtime + 100))

        # —— 二次：B 未动应跳过；A 应同时出现在 rechunk 与 remove ——
        plan1 = compute_sync_plan(data_dir, load_manifest(data_dir))
        assert doc_a_id in plan1["rechunk"], "修改后 A 必须进 rechunk"
        assert doc_a_id in plan1["remove"], "修改后 A 必须进 remove（先删后增）"
        assert doc_b_id not in plan1["rechunk"], "B 未变，不应进 rechunk"
        assert doc_b_id not in plan1["remove"], "B 未变，不应进 remove"
        # remove 里装的是**旧** chunk_ids（含已消失的尾巴）
        assert set(plan1["remove"][doc_a_id]) == set(old_a_ids), \
            f"remove 应为旧 id 全量，实际 {plan1['remove'][doc_a_id]}"
        # 重新切出的新 id（段落减少，应比旧少）
        new_a_ids = [c["id"] for c in chunk_file(a_path, data_dir)]
        assert set(new_a_ids) == set(c["id"] for c in plan1["rechunk"][doc_a_id]), \
            "rechunk 的新 id 应与重新切分一致"
        assert len(new_a_ids) < len(old_a_ids), \
            f"测试设计：A 应改小（{len(old_a_ids)}→{len(new_a_ids)}）以验证孤儿回收"

        # —— 增量 sync（只动 A，不动 B）——
        r.sync(plan1["rechunk"], plan1["remove"])

        ids = r._cids
        # ② 无重复 id（新旧不得并存）
        assert len(ids) == len(set(ids)), f"存在重复 id（新旧并存）: {ids}"
        # ③ 旧尾巴已回收（改小后消失的 id 不应残留）
        orphan = set(old_a_ids) - set(new_a_ids)
        assert orphan, "测试设计：应存在旧尾巴 id 用于验证回收"
        for cid in orphan:
            assert cid not in ids, f"旧尾段 {cid} 应被删除，却仍残留（孤儿向量）"
        # 新 A 全在；旧 B 全在
        for cid in new_a_ids + old_b_ids:
            assert cid in ids, f"应有 {cid}，却缺失"
        # total = 新A + 旧B
        assert r.count() == len(new_a_ids) + len(old_b_ids), \
            f"修改后 count 应为 {len(new_a_ids)+len(old_b_ids)}，实际 {r.count()}"
        # ① 内容已更新为新版
        a0_id = new_a_ids[0]
        a0_text = next(t for cid, t in zip(r._cids, [d[1] for d in r.docs]) if cid == a0_id)
        assert "NEW_A_1" in a0_text, f"A 文本未更新: {a0_text!r}"
        assert "OLD_A_1" not in a0_text, "A 仍含旧文本，先删后增失败"

        # —— 幂等：再次 sync 同一 plan 不应产生重复 / 不应丢内容 ——
        r.sync(plan1["rechunk"], plan1["remove"])
        assert len(r._cids) == len(set(r._cids)), "二次 sync 产生重复 id"
        assert r.count() == len(new_a_ids) + len(old_b_ids), \
            f"二次 sync 后 count 应为 {len(new_a_ids)+len(old_b_ids)}，实际 {r.count()}"

        print("ALL ASSERTIONS PASSED ✅")
        print(f"  - 修改文档同时进 rechunk({len(new_a_ids)} new) 与 remove({len(old_a_ids)} old) ✅")
        print("  - sync 后无重复 id、旧尾段已回收、文本更新为新版 ✅")
        print("  - 幂等：重复 sync 不改变状态 ✅")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(_run())
