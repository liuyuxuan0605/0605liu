---
structure: Graph
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# Dijkstra 最短路径算法详解

## 基本原理

Dijkstra 算法解决单源最短路径（SSSP）问题：给定带权有向图和一个源点 s，求 s 到所有其他顶点的最短路径。核心思想是贪心——每次从未确定最短路径的顶点中，选距离最小的顶点"确定"下来，然后用它松弛邻居。

## 算法步骤

1. 初始化：dist[s] = 0，其余 dist[v] = ∞；所有顶点标记为"未确定"
2. 从未确定顶点中选 dist 最小的顶点 u（贪心选择）
3. 将 u 标记为"已确定"（此后 dist[u] 不再改变）
4. 松弛（Relax）：对 u 的每条出边 (u, v, w)，若 dist[u] + w < dist[v]，则更新 dist[v] = dist[u] + w
5. 重复 2-4 直到所有顶点确定（或目标顶点确定）

## 为什么不能有负权边

Dijkstra 的正确性依赖一个前提：已确定的顶点的 dist 值不会再被更新。

如果有负权边：假设 u 已确定（dist[u] = 5），但存在一条经过未确定顶点 x 的路径 s→x→u，其中 dist[x] = 10，边 x→u 权为 -8。则 s→x→u 的总权为 2 < 5，u 的 dist 应该被更新——但 u 已经被"确定"了，不会再被处理。算法给出错误答案。

本质：Dijkstra 是贪心，贪心要求"局部最优 = 全局最优"，负权边破坏了这个性质。

负权边的替代方案：Bellman-Ford 算法（O(VE)，允许负权边，能检测负权环）。

## 优先队列 = 最小堆

Dijkstra 第 2 步"选 dist 最小的未确定顶点"，朴素实现是 O(V) 扫描，总复杂度 O(V²)。

用最小堆（优先队列）优化：把 (dist, vertex) 放入最小堆，每次取堆顶即为当前 dist 最小的顶点。更新 dist 时把新值入堆（懒删除：取出时若已确定则跳过）。

复杂度：O((V + E) log V)——每个顶点最多入堆一次（确定），每条边最多触发一次入堆（松弛）。

所以"Dijkstra 用的优先队列就是最小堆"——是的，Java 里是 PriorityQueue，C++ 里是 priority_queue<pair<int,int>, vector<...>, greater<...>>。

## 与 BFS 的关系

- BFS 是 Dijkstra 在"所有边权 = 1"时的特化：队列天然保证先出队的距离最短
- Dijkstra 是 BFS 在"边权不等"时的推广：用优先队列替代普通队列

## 面试高频问题

- 为什么 Dijkstra 不能处理负权边：贪心确定性被破坏（已确定顶点可能被更短路径更新）
- Dijkstra 和 Prim 的区别：Prim 选"连接已选集合的最小边"（MST），Dijkstra 选"距源点最近的未确定顶点"（最短路径）；Prim 的 key 是边权，Dijkstra 的 key 是累计距离
- 如何输出具体路径：维护 prev[v] 数组，松弛时记录前驱，最后从终点沿 prev 回溯
- 稠密图用数组 O(V²) vs 稀疏图用堆 O((V+E)logV)：与 Prim 的选型逻辑一致
- A* 算法：Dijkstra + 启发函数 h(v)，优先扩展"估计离目标最近"的顶点，加速目标搜索
