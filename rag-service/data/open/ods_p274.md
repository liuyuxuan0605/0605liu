---
structure:
source: open/ods_p274.md
page: 274
---

# ODS p274: §12.3 Graphs

§12.3 Graphs
byte[] c = new byte[g.nVertices()];
Stack<Integer> s = new Stack<Integer>();
s.push(r);
while (!s.isEmpty()) {
int i = s.pop();
if (c[i] == white) {
c[i] = grey;
for (int j : g.outEdges(i))
s.push(j);
}
}
}
In the preceding code, when the next vertex, i, is processed, iis
coloured grey and then replaced, on the stack, with its adjacent vertices.
During the next iteration, one of these vertices will be visited.
Not surprisingly, the running times of dfs(g;r) and dfs2 (g;r) are the
same as that of bfs(g;r):
Theorem 12.4. When given as input a Graph ,g, that is implemented using
theAdjacencyLists data structure, the dfs(g;r)anddfs2 (g;r)algorithms
each run inO(n+m)time.
As with the breadth-ﬁrst-search algorithm, there is an underlying tree
associated with each execution of depth-ﬁrst-search. When a node i,r
goes from white togrey , this is because dfs(g;i;c) was called recursively
while processing some node i0. (In the case of dfs2 (g;r) algorithm, iis
one of the nodes that replaced i0on the stack.) If we think of i0as the
parent of i, then we obtain a tree rooted at r. In Figure 12.5, this tree is a
path from vertex 0 to vertex 11.
An important property of the depth-ﬁrst-search algorithm is the fol-
lowing: Suppose that when node iis coloured grey , there exists a path
from ito some other node jthat uses only white vertices. Then jwill be
coloured ﬁrst grey then black before iis coloured black . (This can be
proven by contradiction, by considering any path Pfrom itoj.)
One application of this property is the detection of cycles. Refer to
Figure 12.6. Consider some cycle, C, that can be reached from r. Let
ibe the ﬁrst node of Cthat is coloured grey , and let jbe the node that
260

（中文关键词：栈、红黑树、树、图）
