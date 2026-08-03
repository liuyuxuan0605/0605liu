---
structure: Tree
kind: concept
operation: trie_ops
phase: intermediate
difficulty: medium
---

# Trie（前缀树 / 字典树）

## 结构

每个节点代表一个前缀，从根到某节点的路径拼出该前缀。节点包含：children 映射（字符→子节点）、is_end 标记（是否为完整单词终点）。

```
        root
       / | \
      a  b  c
     /       \
    p         a
   / \         \
  p   r        t
  |   |
  le  il
```

## 核心操作

### 插入 O(L)

```
node = root
for ch in word:
    if ch not in node.children:
        node.children[ch] = Node()
    node = node.children[ch]
node.is_end = True
```

### 查找 O(L)

```
node = root
for ch in word:
    if ch not in node.children:
        return False
    node = node.children[ch]
return node.is_end
```

### 前缀查询 O(L)

与查找相同，但不要求 `is_end == True`，只要路径存在即返回 True。

## 空间与时间

| 操作 | 时间 | 说明 |
|------|------|------|
| 插入/查找/删除 | O(L) | L = 单词长度，与字典大小无关 |
| 空间 | O(N·L·σ) 最坏 | N 个单词、σ 为字符集大小 |

实际中大量前缀共享，空间远小于最坏值。

## 应用场景

- 自动补全 / 搜索建议
- 拼写检查
- IP 路由（最长前缀匹配）
- 词频统计（节点额外存 count）
- 最大异或值（01-Trie）

## 与其他方案对比

| 方案 | 查找 | 前缀查询 | 空间 |
|------|------|----------|------|
| HashSet | O(L) 平均 | 不支持 | O(N·L) |
| 排序数组 | O(L·log N) | 二分+逐字符 | O(N·L) |
| Trie | O(L) | O(L) 天然支持 | 前缀共享省空间 |

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 如何优化空间？ | 压缩 Trie（Radix Tree）：单子链合并为一条边 |
| 如何支持删除？ | 沿路径清除 is_end；若子节点全空则回收节点 |
| 与 HashMap 比优势？ | 前缀查询 O(L) vs HashMap 无法高效前缀匹配 |
| 01-Trie 求最大异或？ | 贪心：每一位尽量走与当前位相反的方向 |
