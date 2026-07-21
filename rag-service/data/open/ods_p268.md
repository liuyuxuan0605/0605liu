---
structure:
source: open/ods_p268.md
page: 268
---

# ODS p268: §12.2 Graphs

§12.2 Graphs
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
This takesO(deg( i)) time, where deg( i) (the degree ofi) counts the
number of edges in Ethat have ias their source.
The hasEdge (i;j) operation is similar; it searches through the list
adj[i] until it ﬁnds j(and returns true), or reaches the end of the list
(and returns false):
AdjacencyLists
boolean hasEdge(int i, int j) {
return adj[i].contains(j);
}
This also takes O(deg( i)) time.
TheoutEdges (i) operation is very simple; it returns the list adj[i]:
AdjacencyLists
List<Integer> outEdges(int i) {
return adj[i];
}
This clearly takes constant time.
The inEdges (i) operation is much more work. It scans over every
vertexjchecking if the edge ( i;j) exists and, if so, adding jto the output
list:
AdjacencyLists
List<Integer> inEdges(int i) {
List<Integer> edges = new ArrayStack<Integer>();
254

（中文关键词：数组、栈、图）
