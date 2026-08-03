---
structure: Graph
kind: concept
operation: topological_sort
phase: advanced
difficulty: medium
---

# 拓扑排序（Topological Sort）

## 适用场景

拓扑排序仅适用于 **有向无环图（DAG）**。典型应用：课程先修依赖、编译单元依赖、任务调度。

## 两种实现方式

### BFS 方式（Kahn 算法）

维护入度数组 `indegree[]`，将所有入度为 0 的节点入队。每次出队一个节点，将其邻接节点入度减 1；若减至 0 则入队。出队顺序即为拓扑序。

```
queue ← 所有入度为0的节点
order = []
while queue 非空:
    u = queue.pop()
    order.append(u)
    for v in adj[u]:
        indegree[v] -= 1
        if indegree[v] == 0:
            queue.push(v)
if len(order) < 节点总数:
    → 存在环，拓扑排序不存在
```

时间复杂度 O(V + E)，空间 O(V)。

### DFS 方式

对图做 DFS，记录每个节点的完成时间（后序）。将所有节点按完成时间 **逆序** 排列即为拓扑序。等价地，可以在 DFS 回溯时将节点压入栈，最终栈中顺序即拓扑序。

```
visited = set()
stack = []
def dfs(u):
    visited.add(u)
    for v in adj[u]:
        if v not in visited:
            dfs(v)
    stack.append(u)       # 后序位置入栈

for each node u:
    if u not in visited:
        dfs(u)
topo_order = reversed(stack)
```

## 环检测

- Kahn 算法：若最终 order 长度 < V，说明有环（剩余节点入度永远无法降为 0）。
- DFS：若 DFS 过程中遇到"灰色"节点（正在当前递归栈中），则存在后向边 → 有环。

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 拓扑排序结果唯一吗？ | 不唯一；同一层入度为 0 的节点可任意排列 |
| 如何判断唯一性？ | 每一步队列中恰好只有 1 个元素 → 唯一 |
| 无向图能做拓扑排序吗？ | 不能，拓扑排序定义在有向图上 |
| 与 DFS 后序的关系？ | 拓扑序 = DFS 完成时间的逆序 |
