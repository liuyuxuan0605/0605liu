---
structure: Array
kind: concept
operation: binary_search
phase: intermediate
difficulty: medium
---

# 二分查找变体与边界处理

## 基本形式

在有序数组中查找目标值，每次将搜索区间缩小一半，时间 O(log n)。

```
lo, hi = 0, n - 1
while lo <= hi:
    mid = lo + (hi - lo) // 2    # 防溢出
    if a[mid] == target:
        return mid
    elif a[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
return -1
```

## 常见变体

### 查找第一个 ≥ target 的位置（lower_bound）

```
lo, hi = 0, n      # 注意 hi = n（开区间右端）
while lo < hi:
    mid = lo + (hi - lo) // 2
    if a[mid] < target:
        lo = mid + 1
    else:
        hi = mid
return lo          # 若 lo == n 则不存在
```

### 查找最后一个 ≤ target 的位置（upper_bound - 1）

```
lo, hi = 0, n
while lo < hi:
    mid = lo + (hi - lo) // 2
    if a[mid] <= target:
        lo = mid + 1
    else:
        hi = mid
return lo - 1
```

### 旋转数组中查找

先判断哪半段有序，再决定 target 落在哪半段：

```
if a[lo] <= a[mid]:       # 左半有序
    if a[lo] <= target < a[mid]:
        hi = mid - 1
    else:
        lo = mid + 1
else:                      # 右半有序
    if a[mid] < target <= a[hi]:
        lo = mid + 1
    else:
        hi = mid - 1
```

## 边界陷阱

| 陷阱 | 说明 |
|------|------|
| `lo + hi` 溢出 | 用 `lo + (hi - lo) // 2` |
| 死循环 | `lo < hi` 配合 `hi = mid`；`lo <= hi` 配合 `hi = mid - 1` |
| 空数组 | n=0 时 lo=0, hi=-1（闭区间）或 hi=0（开区间），需先判空 |
| 重复元素 | lower_bound 找第一个，upper_bound 找最后一个之后 |

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 为什么不能写 `(lo+hi)/2`？ | 大数相加可能整数溢出（C++/Java） |
| 开区间 vs 闭区间？ | 统一一种风格；混用是 bug 之源 |
| 二分答案（最小化最大值）？ | 对"答案"做二分，check 函数判定可行性 |
| 浮点二分？ | 循环 `hi - lo > eps`，通常 100 次迭代足够 |
