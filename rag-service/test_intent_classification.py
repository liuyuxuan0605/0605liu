"""意图分类回归测试：验证"分析操作影响" vs "执行操作" vs "分步演示"的判定。

沙箱无 API key，本测试纯离线，只测 prompt 生成逻辑（不调用 LLM）。
"""
import sys
import os
import re
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm import _is_analyze_operation, build_prompt


class FakeHit:
    """模拟检索命中的最小对象。"""
    def __init__(self, text, source="test.md", structure="AVLTree", score=0.9):
        self.text = text
        self.metadata = {"source": source, "structure": structure}
        self.score = score


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
