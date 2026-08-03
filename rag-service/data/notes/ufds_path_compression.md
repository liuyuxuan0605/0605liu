---
structure: UFDS
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# 并查集（Union-Find Disjoint Sets, UFDS）

## 基本原理

并查集（UFDS，也叫 Disjoint Set Union / DSU）用一片森林表示若干互不相交的集合：每棵树代表一个集合，树根是集合的"代表元"（representative）。通常用一个 parent 数组记录每个节点的父节点，初始时每个元素自成集合（parent[i] = i）。

核心操作只有两个：
- Find(x)：从 x 沿父节点向上找到根节点，用于判断两个元素是否属于同一集合
- Union(x, y)：分别找到 x 和 y 的根，若不同则将一棵树挂到另一棵树下，合并两个集合

## 路径压缩（Path Compression）

朴素 Find 在最坏情况下树退化成链，单次查询 O(n)。路径压缩在 Find 时把沿途所有节点直接连到根节点，使树变扁：

```
find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  // 递归压缩
    return parent[x]
```

效果：经过一次 Find 后，路径上所有节点的深度变为 1。后续再查这些节点几乎是 O(1)。

## 按秩合并（Union by Rank）

用 rank 数组记录每棵树的近似高度（上界）。合并时让秩小的树挂到秩大的树下，避免矮树变高：

```
union(x, y):
    rx, ry = find(x), find(y)
    if rx == ry: return
    if rank[rx] < rank[ry]: swap(rx, ry)
    parent[ry] = rx
    if rank[rx] == rank[ry]: rank[rx] += 1
```

## 时间复杂度

路径压缩 + 按秩合并结合后，单次操作的均摊复杂度为 O(α(n))，其中 α 是反阿克曼函数（inverse Ackermann function）。对于任何实际输入规模（n < 2^65536），α(n) ≤ 5，可视为常数。

单独使用路径压缩或单独使用按秩合并，复杂度为 O(log n) 均摊。两者结合才能达到近似常数。

## 典型应用

- 无向图连通分量（Connected Components）统计
- Kruskal 最小生成树算法中判断加边是否形成环
- 网格/迷宫连通性判断（如 LeetCode 岛屿问题）
- 等价类划分（社交网络好友关系、图片像素连通区域）
- 在线动态连通性查询（边逐步加入，随时问两点是否连通）

## 面试要点

- 为什么用 while 循环版 find 时路径压缩要分两趟（先找根，再压缩）：递归版天然两趟，迭代版需要显式第二趟
- 按秩合并的 rank 不是精确高度：路径压缩会改变树形，但 rank 只增不减，作为上界仍然有效
- 与 BFS/DFS 判断连通性的区别：并查集适合"动态加边 + 在线查询"，BFS/DFS 适合"一次性全图遍历"
- 变体：带权并查集（维护节点到根的相对关系，如食物链问题）、可撤销并查集（用栈记录操作，支持回退）
