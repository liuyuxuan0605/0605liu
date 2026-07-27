---
structure:
source: open/ods_p273.md
page: 273
---

# ODS p273: Graph Traversal §12.3

Graph Traversal §12.3
0 1 2 3
4 11 10 9
8 7 6 5
Figure 12.5: An example of depth-ﬁrst-search starting at node 0. Nodes are la-
belled with the order in which they are processed. Edges that result in a recursive
call are drawn in black, other edges are drawn in grey .
byte[] c = new byte[g.nVertices()];
dfs(g, r, c);
}
void dfs(Graph g, int i, byte[] c) {
c[i] = grey; // currently visiting i
for (Integer j : g.outEdges(i)) {
if (c[j] == white) {
c[j] = grey;
dfs(g, j, c);
}
}
c[i] = black; // done visiting i
}
An example of the execution of this algorithm is shown in Figure 12.5.
Although depth-ﬁrst-search may best be thought of as a recursive al-
gorithm, recursion is not the best way to implement it. Indeed, the code
given above will fail for many large graphs by causing a stack overﬂow.
An alternative implementation is to replace the recursion stack with an
explicit stack, s. The following implementation does just that:
Algorithms
void dfs2(Graph g, int r) {
259

（中文关键词：栈、图）
