---
structure: UFDS
kind: concept
operation: union_by_rank
phase: intermediate
difficulty: medium
---

# 并查集：按秩合并与加权应用

## 按秩合并（Union by Rank）

路径压缩让 find 摊还 O(α(n))，但若不控制合并方向，树仍可能退化为链。按秩合并保证树高 O(log n)：

```
rank[x] 初始为 0（表示树高的上界）

def union(x, y):
    rx, ry = find(x), find(y)
    if rx == ry: return
    if rank[rx] < rank[ry]:
        parent[rx] = ry
    elif rank[rx] > rank[ry]:
        parent[ry] = rx
    else:
        parent[ry] = rx
        rank[rx] += 1     # 等高合并，新根高度+1
```

rank 是高度上界（路径压缩后实际高度可能更小），只增不减。

## 路径压缩 + 按秩合并 = 近常数

两者同时使用时，m 次操作总时间 O(m · α(m, n))，α 为反 Ackermann 函数，实际 ≤ 5。面试中说"近似 O(1)"即可。

## 加权并查集（带权合并）

节点额外维护 `weight[x]`（到父节点的相对关系），find 时路径压缩同步更新权重。典型应用：

- **食物链**（A 吃 B、B 吃 C、C 吃 A）：weight 模 3 表示关系
- **等式方程可满足性**：weight 表示差值
- **带权图连通分量**：维护分量大小 / 到根距离

```
def find(x):
    if parent[x] != x:
        root = find(parent[x])
        weight[x] += weight[parent[x]]   # 累加到根
        parent[x] = root
    return parent[x]

def union(x, y, w):    # 约束: weight[y] - weight[x] = w
    rx, ry = find(x), find(y)
    if rx == ry:
        return weight[y] - weight[x] == w   # 检查一致性
    parent[rx] = ry
    weight[rx] = w + weight[y] - weight[x]
```

## 面试常见追问

| 问题 | 要点 |
|------|------|
| 只用路径压缩够吗？ | 够（摊还 O(log n)），但加按秩合并更优（O(α)） |
| rank 和 size 选哪个？ | 都可以；size 更直观（合并小树到大树），rank 理论更紧 |
| 如何判断无向图连通分量数？ | 初始 count=n，每次成功 union 则 count-- |
| 离线 vs 在线？ | 并查集天然在线；若需"撤销合并"则用可持久化或离线逆序处理 |
