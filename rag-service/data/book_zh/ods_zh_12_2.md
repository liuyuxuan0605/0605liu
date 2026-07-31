---
structure: 
source: book_zh/ods_zh_12_2.md
chapter: 12. Graphs
section: 12.2
page: 266
kind: textbook
---

# 12.2 邻接表：作为列表集合的图

Adjacency list 图的表示采用了以顶点为中心的方法。邻接表有许多可能
的实现方式。在本节中，我们展示了一种简单的实现。在本节的结尾，我
们将讨论不同的可能性。在邻接表表示法中，图 G = (V , E) 被表示为一个
列表数组 adj。列表 adj[i] 包含与顶点 i 相邻的所有顶点的列表。也就是说
，它包含每个索引 j，使得 (i, j) E。
∈
AdjacencyLists
int n;
List<Integer>[] adj;
AdjacencyLists(int n0) {
n = n0;
adj = (List<Integer>[])new List[n];
for (int i = 0; i < n; i++)
0 1 2 3
4 5 6 7
8 9 10 11
0 1 2 3 4 5 6 7 8 9 10 11
1 0 1 2 0 1 5 6 4 8 9 10
4 2 3 7 5 2 2 3 9 5 6 7
6 6 8 6 7 11 10 11
5 9 10
4
图 12.3：一个图及其邻接表
adj[i] = 新的 ArrayStack<整数>();
}
（如图 12.3 所示。）在这个特定的实现中，我们将 adj 中的每个列表
表示为 ArrayStack，因为我们希望按位置进行常量时间访问。其他选项也
是可能的。具体来说，我们本可以将 adj 实现为 DLList。
addEdge(i, j) 操作只是将值 j 添加到列表 adj[i] 中：
AdjacencyLists
void addEdge(int i, int j) {
adj[i].add(j);
}
这需要恒定时间。
removeEdge(i, j) 操作会遍历列表 adj[i] 直到找到 j，然后将其移除：
AdjacencyLists
void removeEdge(int i, int j) {
Iterator<Integer> it = adj[i].iterator();
while (it.hasNext()) {
if (it.next() == j) {
it.remove();
return;
}
}
}
这需要 O(deg(i)) 时间，其中 deg(i)（i 的 degree）计算 E 中以 i 为源的
边的数量。
hasEdge(i, j) 操作类似；它会搜索列表 adj[i]，直到找到 j（并返回 true
），或者到达列表末尾（并返回 false）：
AdjacencyLists
boolean hasEdge(int i, int j) {
return adj[i].contains(j);
}
这也需要 O(deg(i)) 时间。
outEdges(i) 操作非常简单；它返回列表 adj[i]：
AdjacencyLists
List<Integer> outEdges(int i) {
return adj[i];
}
这显然需要常数时间。
inEdges(i) 操作要复杂得多。它扫描每个顶点 j，检查边 (i, j) 是否存在
，如果存在，则将 j 添加到输出列表中：
邻接表 List<Integer> inEdges(int i)
{ List<Integer> 边 = new ArrayStack<Integer>();
for (int j = 0; j < n; j++) if (adj[j].contains(i)) edges.a
dd(j); return edges;
}
这个操作非常慢。它会扫描每个顶点的邻接表，因此需要 O(n + m) 时
间。
下列定理总结了上述数据结构的性能：
定理 12.2. The 邻接表 data structure implements the 图 interface. An 邻接
表 supports the operations
• addEdge(i, j) in constant time per operation;
• removeEdge(i, j) and hasEdge(i, j) in O(deg(i)) time per operation;
• outEdges(i) in constant time per operation; and
• inEdges(i) in O(n + m) time per operation.
The space used by a 邻接表 is O(n + m).
正如前面提到的，在将图实现为邻接表时，需要做出很多不同的选择
。一些常见的问题包括：
• 应该使用哪种类型的集合来存储 adj 的每个元素？可以使用基于数组
的列表、链表，甚至哈希表。
• 是否应该有第二个邻接表 inadj，用于存储每个 i 的顶点列表 j，使得
(j, i) E? 这可以大大减少 inEdges(i) 操作的运行时间，但在添加或删
∈
除边时需要稍微多一些工作。
• adj[i] 中边 (i, j) 的条目是否应该通过引用链接到 inadj[j] 中对应的条
目？
• 边是否应当成为拥有自身关联数据的一等对象？通过这种方式，adj
将包含边的列表，而不是顶点（整数）的列表。
这些问题大多归结为实现的复杂性（和空间）与实现的性能特性之间的权
衡。

（中文关键词：数组、栈、邻接表）
