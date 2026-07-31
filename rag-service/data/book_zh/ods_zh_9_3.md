---
structure: RedBlackTree
source: book_zh/ods_zh_9_3.md
chapter: 9.1 2-4 树
section: 9.3
page: 219
kind: textbook
---

# 9.3 小结

以下定理总结了红黑树数据结构的性能：
定理 9.1. A 红黑树 implements the 有序集合 interface and supports
the operations 添加(x) , 移除(x) , and 查找(x) in O(log n ) worst-case time per
operation.
上述定理中未包括以下额外奖励：
定理 9.2. Beginning with an empty 红黑树 , any sequence of m 添加(x) and
删除(x) operations results in a total of O(m) time spent during all calls 添加
修正(u) and 删除修正(u) .
我们仅对定理 9.2 给出证明的概要。通过将 addFixup(u) 和 removeFixu
p(u) 与在 2-4 树中添加或删除叶子的算法进行比较，我们可以说服自己，
这个性质是从 2-4 树继承下来的。特别地，如果我们能够证明在 2-4 树中
用于分裂、合并和借用的总时间为 O(m)，那么这就意味着定理 9.2。
该定理对 2-4 树的证明使用了摊销分析的势能法。2 将 2-4 树中内部节
点 u 的势能定义为
1 if u has 2 children
Φ(u) = 0 if u has 3 children

 3 if u has 4 children
将 2-4 树的潜在量定义为其各  个节点潜在量的总和。当发生分裂时，这是
因为一个有四个子节点的节点变成两个节点，分别有两个和三个子节点。
这意味着整体潜在量下降了 3 1 0 = 2。当发生合并时，原本各有两个
− −
子节点的两个节点被一个有三个子节点的节点替代。结果是潜在量下降了
2 0 = 2。因此，对于每次分裂或合并，潜在量都会减少两个。
−
接下来请注意，如果我们忽略节点的拆分和合并，只有常量数量的节
点其子节点数量会发生变化
2See the proofs of Lemma 2.2 and Lemma 3.1 for other applications of the potential
method.
添加或移除一个叶子节点。添加节点时，一个节点的子节点数量增加一个
，潜在值最多增加三。在移除叶子节点时，一个节点的子节点数量减少一
个，潜在值最多增加一，并且可能有两个节点参与借节点操作，它们的总
潜在值最多增加一。
总而言之，每次合并和分裂都会使势能至少下降两。忽略合并和分裂
时，每次增加或删除最多使势能上升三，并且势能始终为非负。因此，对
一个初始为空的树进行 m 次增加或删除所导致的分裂和合并次数最多为 3
m/2。定理 9.2 是这一分析以及 2-4 树与红黑树之间对应关系的结果。

（英文术语：RedBlackTree）
