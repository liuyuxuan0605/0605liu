---
structure: 
source: book_zh/ods_zh_12_1.md
chapter: 12. Graphs
section: 12.1
page: 263
kind: textbook
---

# 12.1 邻接矩阵：用矩阵表示图

adjacency matrix 是表示一个 n 顶点图 G = (V , E) 的一种方法，通过一个 n
× n 矩阵 a 来表示，其元素是布尔值。
AdjacencyMatrix
int n;
boolean[][] a;
AdjacencyMatrix(int n0) {
n = n0;
a = new boolean[n][n];
}
矩阵项 a[i][j] 定义为
true if (i, j) E
a[i][j] = ∈
false otherwise


图 12.1 中图的邻接矩阵如图 12.2 所示。
在这种表示中，操作 addEdge(i, j)、removeEdge(i, j) 和 hasEdge(i, j) 仅
涉及设置或读取矩阵条目 a[i][j]：
邻接矩阵 void add
Edge(int i, int j) { a[i][j] = true; } void removeEd
ge(int i, int j) { a[i][j] = false; } boolean hasEdge
(int i, int j) { return a[i][j]; }
0 1 2 3
4 5 6 7
8 9 10 11
0 1 2 3 4 5 6 7 8 9 10 11
0 0 1 0 0 1 0 0 0 0 0 0 0
1 1 0 1 0 0 1 1 0 0 0 0 0
2 1 0 0 1 0 0 1 0 0 0 0 0
3 0 0 1 0 0 0 0 1 0 0 0 0
4 1 0 0 0 0 1 0 0 1 0 0 0
5 0 1 1 0 1 0 1 0 0 1 0 0
6 0 0 1 0 0 1 0 1 0 0 1 0
7 0 0 0 1 0 0 1 0 0 0 0 1
8 0 0 0 0 1 0 0 0 0 1 0 0
9 0 0 0 0 0 1 0 0 1 0 1 0
10 0 0 0 0 0 0 1 0 0 1 0 1
11 0 0 0 0 0 0 0 1 0 0 1 0
图 12.2：一个图及其邻接矩阵。
这些操作显然每次操作都需要常量时间 离子。
邻接矩阵表现不佳的地方在于 outEdges(i) 和 inEdges(i) 操作。要实现
这些操作，我们必须扫描 a 的相应行或列中的所有 n 个条目，并收集所有
索引 j，其中 a[i][j] 或 a[j][i] 为真。
AdjacencyMatrix
List<Integer> outEdges(int i) {
List<Integer> edges = new ArrayList<Integer>();
for (int j = 0; j < n; j++)
if (a[i][j]) edges.add(j);
return edges;
}
List<Integer> inEdges(int i) {
List<Integer> edges = new ArrayList<Integer>();
for (int j = 0; j < n; j++)
if (a[j][i]) edges.add(j);
return edges;
}
这些操作显然每次操作需要 O(n) 时间。
邻接矩阵表示的另一个缺点是它很大。它存储一个 n×n 的布尔矩阵，
因此至少需要 n² 位的内存。这里的实现使用了布尔值矩阵，因此实际上
使用的内存大约为 n² 字节。更精细的实现方法是将 w 个布尔值打包到每
个内存字中，这可以将空间使用量减少到 n²/w 个内存字。
定理 12.1. The 邻接矩阵 data structure implements the 图 interface. An 邻接
矩阵 supports the operations
• 添加边(i, j), 删除边(i, j), and 是否有边(i, j) in constant time
per operation; and
• 入边(i), and 出边(i)in O(n) time per operation.
The space used by an 邻接矩阵 is O(n2).
尽管邻接矩阵对内存的要求很高，并且 inEdges(i) 和 outEdges(i) 操作
的性能较差，邻接矩阵仍然可以被
对某些应用程序有用。特别是，当图 G 是 dense 时，即它的边数接近 n2，
那么 n2 的内存使用可能是可以接受的。
邻接矩阵数据结构也很常用，因为对矩阵 a 的代数运算可以用来高效
地计算图的属性 G。这是算法课程中的一个主题，但我们在这里指出一个
这样的属性：如果我们将 a 的条目视为整数（1 表示真，0 表示假）并使
用矩阵乘法将 a 乘以自身，那么我们得到矩阵 a2。回想一下，根据矩阵乘
法的定义，
n 1
a2[i][j] = − a[i][k] a[k][j] .
·
k=0
(cid:88)
将这个和解释为图 G 的情况，这个公式计算了顶点 k 的数量，使得 G 同
时包含边 (i, k) 和 (k, j)。也就是说，它计算了从 i 到 j（通过中间顶点 k）
的路径数量，这些路径的长度恰好为二。这个观察是一个算法的基础，该
算法仅使用 O(log n) 次矩阵乘法就能够计算 G 中所有顶点对之间的最短路
径。

（中文关键词：数组、邻接矩阵）
