---
structure: Stack
kind: concept
operation: monotonic_stack
phase: advanced
difficulty: medium
---

# 单调栈（Monotonic Stack）

## 核心思想

维护一个栈内元素保持单调递增（或递减）的栈。新元素入栈前，弹出所有破坏单调性的栈顶元素。被弹出时，恰好确定了该元素的"下一个更大/更小元素"。

## 模板：下一个更大元素（Next Greater Element）

```
stack = []          # 存索引，栈底到栈顶对应值递减
result = [-1] * n
for i in 0..n-1:
    while stack and a[stack[-1]] < a[i]:
        result[stack.pop()] = a[i]   # a[i] 是它的下一个更大
    stack.append(i)
# 栈中剩余元素没有下一个更大元素，result 保持 -1
```

时间 O(n)：每个元素最多入栈一次、出栈一次。

## 变体

| 问题 | 栈的单调性 | 弹出条件 |
|------|-----------|----------|
| 下一个更大元素 | 递减栈（底大顶小） | 当前 > 栈顶 |
| 下一个更小元素 | 递增栈（底小顶大） | 当前 < 栈顶 |
| 柱状图最大矩形 | 递增栈 | 当前 < 栈顶时结算高度 |
| 每日温度（等待天数） | 递减栈 | 当前温度 > 栈顶 |

## 柱状图最大矩形（经典）

```
stack = []
max_area = 0
for i in 0..n:              # 末尾补 0 强制清空
    h = heights[i] if i < n else 0
    while stack and heights[stack[-1]] > h:
        height = heights[stack.pop()]
        width = i if not stack else i - stack[-1] - 1
        max_area = max(max_area, height * width)
    stack.append(i)
```

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 为什么是 O(n)？ | 每个元素入栈出栈各一次，摊还 O(1) |
| 存索引还是存值？ | 通常需要索引（计算宽度/距离），值可从数组取 |
| 循环数组怎么处理？ | 遍历 2n 次，索引用 i % n |
| 与单调队列的区别？ | 单调队列双端操作（滑动窗口最值）；单调栈只操作栈顶 |
