---
structure:
source: open/ods_p270.md
page: 270
---

# ODS p270: §12.3 Graphs

§12.3 Graphs
Most of these questions come down to a tradeo ﬀbetween complexity (and
space) of implementation and performance features of the implementa-
tion.
12.3 Graph Traversal
In this section we present two algorithms for exploring a graph, starting
at one of its vertices, i, and ﬁnding all vertices that are reachable from
i. Both of these algorithms are best suited to graphs represented using
an adjacency list representation. Therefore, when analyzing these algo-
rithms we will assume that the underlying representation is an Adjacen-
cyLists .
12.3.1 Breadth-First Search
The bread-ﬁrst-search algorithm starts at a vertex iand visits, ﬁrst the
neighbours of i, then the neighbours of the neighbours of i, then the
neighbours of the neighbours of the neighbours of i, and so on.
This algorithm is a generalization of the breadth-ﬁrst traversal algo-
rithm for binary trees (Section 6.1.2), and is very similar; it uses a queue,
q, that initially contains only i. It then repeatedly extracts an element
from qand adds its neighbours to q, provided that these neighbours have
never been in qbefore. The only major di ﬀerence between the breadth-
ﬁrst-search algorithm for graphs and the one for trees is that the algo-
rithm for graphs has to ensure that it does not add the same vertex to q
more than once. It does this by using an auxiliary boolean array, seen ,
that tracks which vertices have already been discovered.
Algorithms
void bfs(Graph g, int r) {
boolean[] seen = new boolean[g.nVertices()];
Queue<Integer> q = new SLList<Integer>();
q.add(r);
seen[r] = true;
while (!q.isEmpty()) {
int i = q.remove();
for (Integer j : g.outEdges(i)) {
256

（中文关键词：数组、队列、二叉树、树、图、广度优先搜索）
