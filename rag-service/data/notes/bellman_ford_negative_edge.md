---
structure: Graph
kind: concept
operation: bellman_ford
phase: advanced
difficulty: medium
---

# Bellman-Ford 算法与负权边处理

## 为什么需要 Bellman-Ford

Dijkstra 算法基于贪心，要求所有边权非负。一旦存在负权边，贪心"确定最短"的前提被打破（后续可能通过负权边获得更短路径）。Bellman-Ford 通过 **松弛所有边 V-1 轮** 来处理负权边。

## 算法流程

```
dist[s] = 0, 其余 = ∞
for i = 1 to V-1:
    for each edge (u, v, w):
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w    # 松弛

# 第 V 轮检测负权环
for each edge (u, v, w):
    if dist[u] + w < dist[v]:
        → 存在从 s 可达的负权环，最短路无定义
```

时间复杂度 O(V·E)，空间 O(V)。

## 与 Dijkstra 的对比

| 维度 | Dijkstra | Bellman-Ford |
|------|----------|--------------|
| 负权边 | 不支持 | 支持 |
| 负权环检测 | 无 | 第 V 轮松弛仍更新 → 有环 |
| 时间复杂度 | O((V+E) log V)（优先队列） | O(V·E) |
| 思想 | 贪心（确定一个不再改） | 动态规划（逐轮逼近） |
| 适用图 | 非负权有向/无向 | 任意有向图 |

## SPFA 优化

队列优化版 Bellman-Ford（SPFA）：只将"被松弛成功"的节点入队，避免每轮遍历全部边。平均 O(kE)，最坏仍 O(V·E)。面试中需说明最坏退化为 Bellman-Ford。

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 为什么恰好 V-1 轮？ | 最短路最多经过 V-1 条边（无环路径） |
| 如何输出具体路径？ | 维护 prev[] 数组，松弛时记录前驱 |
| 负权环一定不可达吗？ | 不一定；只有从源点可达的负权环才影响结果 |
| 无向图负权边？ | 无向负权边等价于负权环（u→v 和 v→u 构成环），最短路无定义 |
