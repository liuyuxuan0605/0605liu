---
structure: 
source: book_zh/ods_zh_12_4.md
chapter: 12. Graphs
section: 12.4
page: 275
kind: textbook
---

# 12.4 讨论与练习

## 讨论与练习 (1/2)

深度优先搜索和广度优先搜索算法的运行时间在定理 12.3 和 12.4 中有所
夸大。定义 n 为顶点数 i 的数量，其中存在从 r 到 i 的路径。定义 m 为
r r
以这些顶点为源的边的数量。那么，以下定理更精确地说明了广度优先搜
索和深度优先搜索算法的运行时间。（在这些算法的一些练习应用中，这
种更精细的运行时间说明是有用的。）
定理 12.5. When given as input a 图, g, that is implemented using the 邻接
表 data structure, the bfs(g, r), dfs(g, r) and dfs2(g, r)
algorithms each run in O(n + m ) time.
r r
广度优先搜索似乎在迷宫探索和电路布线的背景下，分别由 Moore [52
] 和 Lee [49] 独立发现。
霍普克罗夫特和塔尔詹 [40] 提出了图的邻接表表示，作为（当时更常
见的）邻接-的替代方案
5
9
0
4
1 6
3
2
8
7
图12.7：一个示例图。
矩阵表示。这种表示方式以及深度优先搜索，在著名的 Hopcroft-Tarjan 平
面性测试算法中起了重要作用，该算法可以在 O(n) 时间内确定图是否可
以在平面上绘制，并且保证没有一对边相互交叉 [41]。
在以下练习中，无向图是指对于每个 i 和 j，边 (i, j) 存在当且仅当边 (j,
i) 存在。
练习 12.1。绘制图 12.7 中图的邻接表表示和邻接矩阵表示。
练习 12.2。图的 incidence matrix 表示法，G，是一个 n m 矩阵，A，其
×
中
1 if vertex i the source of edge j
−
A = +1 if vertex i the target of edge j
i,j 
 0 otherwise.
1. 画出图 12.7 中图

的关联矩阵表示。
2. 设计、分析并实现图的关联矩阵表示。请务必分析空间、addEdge(i, j
)、removeEdge(i, j)、hasEdge(i, j)、inEdges(i) 和 outEdges(i) 的代价。
习题 12.3。说明在图 12.7 中的图 G 上执行 bfs(G, 0) 和 dfs(G, 0) 的过程。
练习 12.4。设 G 为一个无向图。我们说 G 是 connected，如果在 G 中每一
对顶点 i 和 j 之间都有一条从 i 到 j 的路径（由于 G 是无向的，也存在从 j
到 i 的路径）。说明如何在 O(n + m) 时间内测试 G 是否在 O( 中是连通的
。
练习 12.5。设 G 为一个无向图。connected-component la- belling 的 G 将 G
的顶点划分为最大集合，每个集合都形成一个连通子图。展示如何在 O(n
+ m) 时间内计算 G 的连通分量标记。
练习 12.6。设 G 为一个无向图。G 的 spanning forest 是一组树，每个连通
分量对应一棵树，其边为 G 的边，其顶点包含 G 的所有顶点。展示如何
在 O(n + m) 时间内计算 G 的生成森林。
练习 12.7。我们说一个图 G 是 strongly-connected 的，如果对于 G 中的每
一对顶点 i 和 j，都存在一条从 i 到 j 的路径。说明如何在 O(n + m) 时间内
测试 G 是否是强连通的。
练习 12.8。给定一个图 G = (V , E) 和一些特殊顶点 r V，展示如何计算
∈
从 r 到每个顶点 i V 的最短路径长度。
∈
练习 12.9。给出一个（简单的）例子，其中 dfs(g, r) 代码访问图的节点的
顺序与 dfs2(g, r) 代码的顺序不同。写一个 dfs2(g, r) 的版本，使其总是按
照与 dfs(g, r) 完全相同的顺序访问节点。（提示：只需在某个源点 r 有多
于 1 条边的图上跟踪每个算法的执行即可。）
练习 12.10. 图 G 中的 universal sink 是一个顶点，它是 n 条 1 条边的目
−
标，并且没有边以它为源。1 设计并实现一个算法，测试一个用邻接矩阵
表示的图 G 是否有一个通用汇点。你的算法应在 O(n) 时间内运行。
1A universal sink, v, is also sometimes called a celebrity: Everyone in the room recognizes
v, but v doesn’t recognize anyone else in the room.
第十三章
整数的数据结构
在本章中，我们回到实现 SSet 的问题。现在的区别是，我们假设存储在 S
Set 中的元素是 w 位整数。也就是说，我们希望实现 add(x)、remove(x) 和
find(x)，其中 x ∈ ∪ {0, . . . , 2w 1}。想出很多数据或者至少用于排序数
∈ −
据的关键字是整数的应用并不难。
我们将讨论三种数据结构，每种都建立在前一种的思想之上。第一种
结构，BinaryTrie 在 O(w) 时间内执行所有三种 SSet 操作。这并不令人印
象深刻，因为 {0, . . . , 2w 1} 的任何子集大小为 n 2w，所以 log n w。
− ≤ ≤
本书讨论的所有其他 SSet 实现都能在 O(log n) 时间内执行所有操作，因
此它们至少与 BinaryTrie 一样快。
第二种结构，XFastTrie，通过使用哈希加速了BinaryTrie中的搜索。采
用这种加速后，find(x)操作的运行时间为O(log w)。然而，XFastTrie中的a
dd(x)和remove(x)操作仍然需要O(w)时间，XFastTrie使用的空间为O(n · w)
。

（中文关键词：字典树）

## 讨论与练习 (2/2)

第三种数据结构，YFastTrie，使用 XFastTrie 仅存储大约每 w 个元素
中的一个样本，并将剩余的元素存储在标准的 SSet 结构中。这一技巧将 a
dd(x) 和 remove(x) 的运行时间降低到 O(log w)，并将空间减少到 O(n)。
本章中作为示例使用的实现可以存储任何类型的数据，只要可以将一
个整数与之关联。在代码示例中，变量 ix 始终是与 x 关联的整数值，而
且
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
图 13.1：存储在二叉字典树中的整数被编码为从根到叶子的路径。
.intValue(x) 方法将 x 转换为其关联的整数。然而，在文本中，我们将简单
地将 x 当作一个整数来处理。

（中文关键词：字典树）
