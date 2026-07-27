---
structure: Graph
kind: theory
operation: mixed
phase: algorithm
difficulty: medium
---

# 图遍历算法详解

## 核心原理

图遍历是指访问图中所有顶点的过程，主要分为广度优先搜索（BFS）和深度优先搜索（DFS）。

## 图的表示方式

### 邻接矩阵

```
顶点数n，矩阵大小n×n
matrix[i][j] = 1 表示顶点i和j之间有边
matrix[i][j] = 0 表示顶点i和j之间无边
```

### 邻接表

```
每个顶点维护一个链表，存储相邻顶点
adj[0] → 1 → 2 → null
adj[1] → 0 → 3 → null
adj[2] → 0 → 3 → null
adj[3] → 1 → 2 → null
```

## 广度优先搜索（BFS）

### 原理

使用队列，逐层访问顶点：
1. 访问起始顶点
2. 依次访问起始顶点的所有邻接顶点
3. 依次访问这些邻接顶点的邻接顶点
4. 重复直到所有顶点被访问

### 步骤

```
图：A-B, A-C, B-D, B-E, C-F

BFS从A开始：
队列：[A]
访问A → 队列：[B, C]
访问B → 队列：[C, D, E]
访问C → 队列：[D, E, F]
访问D → 队列：[E, F]
访问E → 队列：[F]
访问F → 队列：[]

访问顺序：A → B → C → D → E → F
```

### 伪代码

```python
def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        print(vertex)
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### 时间复杂度

- **邻接表**：O(V + E)
- **邻接矩阵**：O(V²)

## 深度优先搜索（DFS）

### 原理

使用栈（或递归），深入访问顶点：
1. 访问起始顶点
2. 递归访问起始顶点的一个邻接顶点
3. 深入到该邻接顶点的邻接顶点
4. 回溯，访问其他邻接顶点

### 步骤

```
图：A-B, A-C, B-D, B-E, C-F

DFS从A开始：
访问A → 访问B → 访问D → 回溯到B → 访问E
回溯到B → 回溯到A → 访问C → 访问F

访问顺序：A → B → D → E → C → F
```

### 递归实现

```python
def dfs_recursive(graph, vertex, visited):
    visited.add(vertex)
    print(vertex)
    
    for neighbor in graph[vertex]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
```

### 迭代实现

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            print(vertex)
            for neighbor in reversed(graph[vertex]):
                if neighbor not in visited:
                    stack.append(neighbor)
```

### 时间复杂度

- **邻接表**：O(V + E)
- **邻接矩阵**：O(V²)

## BFS vs DFS

| 特性 | BFS | DFS |
|------|-----|-----|
| 数据结构 | 队列 | 栈/递归 |
| 访问顺序 | 逐层访问 | 深入访问 |
| 最短路径 | 可以求无权图最短路径 | 不能直接求最短路径 |
| 内存占用 | 最坏O(V) | 最坏O(V) |
| 应用 | 最短路径、连通性检测 | 拓扑排序、强连通分量 |

## Dijkstra算法

### 原理

用于求带权图的最短路径，使用优先队列（最小堆）：
1. 起始顶点距离设为0，其他设为无穷大
2. 每次选择距离最小的顶点
3. 更新该顶点邻接顶点的距离
4. 重复直到所有顶点被处理

### 步骤

```
图（权重）：A-B(4), A-C(2), B-D(10), C-D(3), D-E(1)

Dijkstra从A开始：
距离：A:0, B:∞, C:∞, D:∞, E:∞
选择A → 更新B:4, C:2
选择C → 更新D:5
选择B → 更新D:min(5, 4+10)=5
选择D → 更新E:6
选择E → 结束

最短路径：
A→B: 4
A→C: 2
A→D: 5（A→C→D）
A→E: 6（A→C→D→E）
```

### 伪代码

```python
import heapq

def dijkstra(graph, start):
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        dist, vertex = heapq.heappop(pq)
        
        if dist > distances[vertex]:
            continue
        
        for neighbor, weight in graph[vertex].items():
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances
```

### 时间复杂度

- **朴素实现**：O(V²)
- **优先队列实现**：O((V + E) log V)

## 关键要点

- BFS适合求无权图的最短路径
- DFS适合拓扑排序和强连通分量
- Dijkstra适用于非负权图的最短路径
- 图遍历需要标记已访问顶点，避免重复访问