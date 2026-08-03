---
structure: String
kind: concept
operation: kmp_search
phase: advanced
difficulty: hard
---

# KMP 字符串匹配算法

## 核心思想

暴力匹配在失配时主串指针回退，KMP 的改进是：**主串指针永不回退**，只移动模式串指针。利用已匹配的前缀信息跳过不可能成功的对齐位置。

## next 数组（前缀函数 / failure function）

`next[i]` 表示模式串 `p[0..i]` 的 **最长相等真前后缀** 的长度。

```
p = "ababaca"
next = [0, 0, 1, 2, 3, 0, 1]
```

构建过程（O(m)）：

```
next[0] = 0
j = 0
for i = 1 to m-1:
    while j > 0 and p[i] != p[j]:
        j = next[j-1]       # 回退到上一个可能匹配的前缀
    if p[i] == p[j]:
        j += 1
    next[i] = j
```

## 匹配过程（O(n)）

```
j = 0   # 模式串已匹配长度
for i = 0 to n-1:
    while j > 0 and s[i] != p[j]:
        j = next[j-1]       # 利用前缀信息跳转
    if s[i] == p[j]:
        j += 1
    if j == m:
        找到匹配，起始位置 = i - m + 1
        j = next[j-1]       # 继续找下一个匹配
```

总时间 O(n + m)，空间 O(m)。

## 为什么主串指针不回退

失配时，`s[i-k..i-1]` 已经和 `p[0..k-1]` 匹配。next[k-1] 告诉我们 `p[0..next[k-1]-1]` 也是这段文本的后缀，所以可以直接从 `j = next[k-1]` 继续比较 `s[i]` 与 `p[next[k-1]]`，无需重看主串。

## 面试常见追问

| 问题 | 要点 |
|------|------|
| next 数组的本质？ | 模式串自身的最长 border（相等真前后缀） |
| 与 Z 函数的区别？ | Z[i] 是 s[i:] 与 s 的 LCP；next 是前缀与后缀的匹配 |
| 如何统计所有出现位置？ | 匹配成功后 j = next[j-1] 继续扫描 |
| 最短循环节？ | 若 n % (n - next[n-1]) == 0，则最小周期 = n - next[n-1] |
