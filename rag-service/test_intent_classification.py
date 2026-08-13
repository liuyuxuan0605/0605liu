"""意图分类回归测试：验证"分析操作影响" vs "执行操作" vs "分步演示"的判定。

沙箱无 API key，本测试纯离线，只测 prompt 生成逻辑（不调用 LLM）。
"""
import sys
import os
import re
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm import (
    _is_analyze_operation, build_prompt, classify_intent, Intent,
    _enforce_intent_contract, _should_reject, _valid_highlights,
    _DEMO_KWS, _EXEC_KWS, _DEMO_EXEC_KWS,
)


class FakeHit:
    """模拟检索命中的最小对象。"""
    def __init__(self, text, source="test.md", structure="AVLTree", score=0.9, q_match=True):
        self.text = text
        self.metadata = {"source": source, "structure": structure}
        self.score = score
        self.q_match = q_match


def prompt_hints(question):
    """调用 build_prompt 并返回其中出现的各类 hint 标记。"""
    hits = [FakeHit("AVL 树插入后若失衡需旋转。")]
    ctx = {
        "structure": "AVLTree",
        "tree_state": "20[id=3]\n  8[id=7]\n    1[id=1]\n    10[id=2]\n  41[id=5]\n    21[id=6]\n",
    }
    prompt = build_prompt(question, hits, ctx)
    return {
        "analyze": "属于分析类问题" in prompt,
        "run": "直接执行某个具体操作" in prompt,
        "demo": "step_explain" in prompt and "用户要求分步演示" in prompt,
        "prompt": prompt,
    }


class AnalyzeOperationTests(unittest.TestCase):
    """测试 _is_analyze_operation 的判定边界。"""

    def test_insert_what_happens(self):
        self.assertTrue(_is_analyze_operation("插入8会导致什么"))
        self.assertTrue(_is_analyze_operation("插入 8 会导致什么"))
        self.assertTrue(_is_analyze_operation("插入8会怎样"))
        self.assertTrue(_is_analyze_operation("插入8会发生什么"))

    def test_delete_what_happens(self):
        self.assertTrue(_is_analyze_operation("删除10会怎样"))
        self.assertTrue(_is_analyze_operation("删除 10 会导致什么"))

    def test_push_what_happens(self):
        self.assertTrue(_is_analyze_operation("push 5 之后栈怎么变"))
        self.assertTrue(_is_analyze_operation("push 5 有什么影响"))

    def test_will_rotate(self):
        self.assertTrue(_is_analyze_operation("插入8会旋转吗"))
        self.assertTrue(_is_analyze_operation("插入8会失衡吗"))
        self.assertTrue(_is_analyze_operation("插入8会触发旋转吗"))

    def test_why_rotate(self):
        # "为什么要旋转" 没有操作词+数值，所以 _is_analyze_operation 返回 False；
        # 它本来就不该走 run_operation 路径，属于普通分析问。
        self.assertFalse(_is_analyze_operation("为什么要旋转"))

    def test_plain_execute_not_analyze(self):
        self.assertFalse(_is_analyze_operation("插入8"))
        self.assertFalse(_is_analyze_operation("删除10"))
        self.assertFalse(_is_analyze_operation("push 5"))
        self.assertFalse(_is_analyze_operation("在AVL树里插入8"))
        self.assertFalse(_is_analyze_operation("avl insert 8"))

    def test_demo_not_analyze(self):
        self.assertFalse(_is_analyze_operation("演示插入8"))
        self.assertFalse(_is_analyze_operation("按顺序插入8,9,10"))
        self.assertFalse(_is_analyze_operation("给我执行插入8"))

    def test_explain_not_analyze(self):
        # "讲解"单独出现视为演示，不归分析类
        self.assertFalse(_is_analyze_operation("讲解插入8的过程"))


class PromptHintTests(unittest.TestCase):
    """测试 build_prompt 最终包含/排除的 hint。"""

    def test_insert_what_happens_prompt(self):
        h = prompt_hints("插入8会导致什么")
        self.assertTrue(h["analyze"], "应包含 analyze_hint")
        self.assertFalse(h["run"], "分析类问题不应触发 run_operation hint")
        self.assertFalse(h["demo"], "不应触发 step_explain hint")

    def test_plain_execute_prompt(self):
        h = prompt_hints("插入8")
        self.assertFalse(h["analyze"])
        self.assertTrue(h["run"], "应触发 run_operation hint")
        self.assertFalse(h["demo"])

    def test_demo_prompt(self):
        h = prompt_hints("演示插入8")
        self.assertFalse(h["analyze"])
        self.assertFalse(h["run"], "演示请求不应再触发 run_operation")
        self.assertTrue(h["demo"], "应触发 step_explain hint")

    def test_execute_with_context_prompt(self):
        h = prompt_hints("在AVL树里插入8")
        self.assertFalse(h["analyze"])
        self.assertTrue(h["run"])
        self.assertFalse(h["demo"])

    def test_delete_what_happens_prompt(self):
        h = prompt_hints("删除10会怎样")
        self.assertTrue(h["analyze"])
        self.assertFalse(h["run"])
        self.assertFalse(h["demo"])


class IntentEnumTests(unittest.TestCase):
    """S7/S15：关键词集合单一来源 + Intent 枚举分类。"""

    def test_keyword_sets_single_source(self):
        # _DEMO_EXEC_KWS 必须由 _DEMO_KWS + _EXEC_KWS 组成，防再分叉
        self.assertEqual(set(_DEMO_EXEC_KWS), set(_DEMO_KWS) | set(_EXEC_KWS))

    def test_classify_intent_enum(self):
        self.assertEqual(classify_intent("演示插入8"), Intent.DEMO)
        self.assertEqual(classify_intent("插入8会怎样"), Intent.ANALYZE)
        self.assertEqual(classify_intent("插入8"), Intent.EXECUTE)
        self.assertEqual(classify_intent("什么是红黑树"), Intent.NONE)

    def test_is_analyze_consistent_with_classify(self):
        for q in ("插入8会怎样", "插入8", "演示插入8", "什么是栈"):
            self.assertEqual(
                _is_analyze_operation(q),
                classify_intent(q) == Intent.ANALYZE,
            )


class ContractTests(unittest.TestCase):
    """服务端契约：意图锁死 / 分路门控 / 高亮校验（不依赖 LLM，纯函数测试）。"""

    # ---- S1：分析类问题 → actions 不含 run_operation/step_explain ----
    def test_analyze_strips_run_operation(self):
        actions = [{"type": "run_operation", "op": "insert", "value": "8"}]
        self.assertEqual(_enforce_intent_contract("插入8会怎样", actions), [])

    def test_analyze_strips_step_explain(self):
        actions = [{"type": "step_explain", "structure": "AVLTree",
                    "steps": [{"op": "insert", "value": "8"}]}]
        self.assertEqual(_enforce_intent_contract("插入8会导致什么", actions), [])

    def test_analyze_keeps_jump(self):
        # jump 是结构切换，不是"执行操作"，分析类保留
        actions = [{"type": "jump", "structure": "RedBlackTree"}]
        self.assertEqual(_enforce_intent_contract("插入8会怎样", actions), actions)

    def test_execute_not_stripped(self):
        actions = [{"type": "run_operation", "op": "insert", "value": "8"}]
        self.assertEqual(_enforce_intent_contract("插入8", actions), actions)
        self.assertEqual(_enforce_intent_contract("演示插入8", actions), actions)

    # ---- S2：分路门控 ----
    def test_naive_gate_uses_q_match(self):
        # naive 路：score 再高，q_match 全 False 也应拒答（BM25 分数无界，阈值无意义）
        hits = [FakeHit("x", score=99.0, q_match=False) for _ in range(3)]
        self.assertTrue(_should_reject(hits, "naive"))
        hits_ok = [FakeHit("x", score=0.1, q_match=True)] + [FakeHit("y", q_match=False)]
        self.assertFalse(_should_reject(hits_ok, "naive"))

    def test_vector_gate_uses_threshold(self):
        # vector 路：低于 0.4 硬拒，高于则放行（与 q_match 无关）
        self.assertTrue(_should_reject([FakeHit("x", score=0.3)], "vector"))
        self.assertFalse(_should_reject([FakeHit("x", score=0.6)], "vector"))

    def test_empty_hits_rejected_both_kinds(self):
        self.assertTrue(_should_reject([], "naive"))
        self.assertTrue(_should_reject([], "vector"))

    # ---- S3：highlight_nodes 与 context 真实节点求交 ----
    def test_highlight_filtered_by_context(self):
        ctx = {"tree_state": "1 2 3"}
        # 请求高亮 99（不存在）→ 被过滤；2（存在）→ 保留
        self.assertEqual(_valid_highlights("节点 2 和 99 的关系", ctx), [2])

    def test_highlight_empty_without_tree_state(self):
        self.assertEqual(_valid_highlights("插入 8 会怎样", {}), [])
        self.assertEqual(_valid_highlights("插入 8 会怎样", {"tree_state": ""}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
