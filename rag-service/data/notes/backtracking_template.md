---
structure: Tree
kind: concept
operation: backtrack
phase: intermediate
difficulty: medium
---

# 回溯法（Backtracking）与搜索模板

## 核心思想

回溯 = DFS + 撤销选择。在解空间树上深度搜索，每到一个节点：做选择 → 递归 → 撤销选择。适用于排列、组合、子集、棋盘等"列举所有方案"的问题。

## 通用模板

```
result = []
def backtrack(path, choices):
    if 满足结束条件:
        result.append(path[:])   # 注意拷贝
        return
    for choice in choices:
        if 不合法: continue       # 剪枝
        path.append(choice)       # 做选择
        backtrack(path, 下一层choices)
        path.pop()                # 撤销选择
```

## 三类经典问题

### 子集（Subsets）

每层从 `start` 开始选，避免重复。递归时 `start = i + 1`。

### 排列（Permutations）

每层从 0 开始，用 `used[]` 数组标记已选元素。

### 组合（Combinations）

与子集类似，但只收集长度恰好为 k 的路径。

## 剪枝技巧

- **排序 + 跳过重复**：`if i > start and nums[i] == nums[i-1]: continue`（去重组合）
- **可行性剪枝**：当前和已超过 target，直接 return（组合总和）
- **对称性剪枝**：N 皇后中利用对称性减半搜索量

## 复杂度

最坏 O(n!)（排列）或 O(2^n)（子集），剪枝后实际远小于上界。面试中需说明上界 + 剪枝如何缩减。

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 回溯与 DFS 的关系？ | 回溯是 DFS 在解空间树上的应用，强调"撤销" |
| 为什么用 path[:] 拷贝？ | path 是引用，不拷贝则 result 中全是同一对象 |
| 如何避免重复排列？ | 排序 + 同层跳过相同值（`used[i-1]` 判断） |
| 能否用迭代代替递归？ | 可以，用显式栈模拟，但代码复杂度大增 |
