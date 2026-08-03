---
structure: Array
kind: concept
operation: sliding_window
phase: intermediate
difficulty: medium
---

# 滑动窗口与双指针技巧

## 滑动窗口模板

适用于"连续子数组/子串"类问题（最长/最短/计数）。维护一个窗口 [left, right]，right 扩张探索、left 收缩满足约束。

```
left = 0
window = 初始化空状态
for right in 0..n-1:
    将 a[right] 加入 window（更新状态）
    while 窗口不满足约束:
        将 a[left] 移出 window（更新状态）
        left += 1
    # 此时 [left, right] 是以 right 为右端的最优/合法窗口
    更新答案
```

时间 O(n)：left 和 right 各最多移动 n 次。

## 经典题型

### 长度最小的子数组（和 ≥ target）

```
left = 0, s = 0, ans = ∞
for right in 0..n-1:
    s += a[right]
    while s >= target:
        ans = min(ans, right - left + 1)
        s -= a[left]
        left += 1
```

### 无重复字符的最长子串

用哈希集合/数组记录窗口内字符。right 扩入新字符；若重复则 left 收缩直到无重复。

### 固定窗口（大小为 k）

窗口大小恒定，每次右移一格：加入 a[right]、移出 a[right-k]。适用于"大小为 k 的子数组最大和"等。

## 双指针（对撞型）

适用于有序数组上的配对问题（两数之和、三数之和、盛水容器）。

```
lo, hi = 0, n-1
while lo < hi:
    s = a[lo] + a[hi]
    if s == target: 记录答案
    elif s < target: lo += 1
    else: hi -= 1
```

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 滑动窗口为什么是 O(n)？ | left 只增不减，总移动 ≤ n 次（摊还） |
| 什么时候不能用滑动窗口？ | 窗口状态不具备单调性（收缩不一定使约束更容易满足） |
| 与二分答案的区别？ | 二分答案 O(n log V)；滑动窗口 O(n) 但要求连续+单调 |
| 三数之和怎么去重？ | 排序 + 外层跳过重复 + 内层对撞 |
