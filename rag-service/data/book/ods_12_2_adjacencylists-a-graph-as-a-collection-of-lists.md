---
structure: 
source: book/ods_12_2_adjacencylists-a-graph-as-a-collection-of-lists.md
chapter: 12. Graphs
section: 12.2
page: 266
kind: textbook
---

# 12.2 AdjacencyLists: A Graph as a Collection of Lists

## AdjacencyLists: A Graph as a Collection of Lists (1/2)

Adjacency list representations of graphs take a more vertex-centric ap-
proach. There are many possible implementations of adjacency lists. In
this section, we present a simple one. At the end of the section, we dis-
cuss different possibilities. In an adjacency list representation, the graph
G = (V , E) is represented as an array, adj, of lists. The list adj[i] contains
a list of all the vertices adjacent to vertex i. That is, it contains every
index j such that (i, j) E.
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
Figure 12.3: A graph and its adjacency lists
adj[i] = new ArrayStack<Integer>();
}
(An example is shown in Figure 12.3.) In this particular implementa-
tion, we represent each list in adj as an ArrayStack, because we would
like constant time access by position. Other options are also possible.
Specifically, we could have implemented adj as a DLList.
The addEdge(i, j) operation just appends the value j to the list adj[i]:
AdjacencyLists
void addEdge(int i, int j) {
adj[i].add(j);
}
This takes constant time.
The removeEdge(i, j) operation searches through the list adj[i] until
it finds j and then removes it:
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
This takes O(deg(i)) time, where deg(i) (the degree of i) counts the
number of edges in E that have i as their source.
The hasEdge(i, j) operation is similar; it searches through the list
adj[i] until it finds j (and returns true), or reaches the end of the list
(and returns false):
AdjacencyLists
boolean hasEdge(int i, int j) {
return adj[i].contains(j);
}
This also takes O(deg(i)) time.
The outEdges(i) operation is very simple; it returns the list adj[i]:
AdjacencyLists
List<Integer> outEdges(int i) {
return adj[i];
}
This clearly takes constant time.
The inEdges(i) operation is much more work. It scans over every
vertex j checking if the edge (i, j) exists and, if so, adding j to the output
list:

（中文关键词：邻接表、图、数组、栈）

## AdjacencyLists: A Graph as a Collection of Lists (2/2)

AdjacencyLists
List<Integer> inEdges(int i) {
List<Integer> edges = new ArrayStack<Integer>();
for (int j = 0; j < n; j++)
if (adj[j].contains(i)) edges.add(j);
return edges;
}
This operation is very slow. It scans the adjacency list of every vertex,
so it takes O(n + m) time.
The following theorem summarizes the performance of the above data
structure:
Theorem 12.2. The AdjacencyLists data structure implements the Graph
interface. An AdjacencyLists supports the operations
• addEdge(i, j) in constant time per operation;
• removeEdge(i, j) and hasEdge(i, j) in O(deg(i)) time per operation;
• outEdges(i) in constant time per operation; and
• inEdges(i) in O(n + m) time per operation.
The space used by a AdjacencyLists is O(n + m).
As alluded to earlier, there are many different choices to be made
when implementing a graph as an adjacency list. Some questions that
come up include:
• What type of collection should be used to store each element of adj?
One could use an array-based list, a linked-list, or even a hashtable.
• Should there be a second adjacency list, inadj, that stores, for each
i, the list of vertices, j, such that (j, i) E? This can greatly reduce
∈
the running-time of the inEdges(i) operation, but requires slightly
more work when adding or removing edges.
• Should the entry for the edge (i, j) in adj[i] be linked by a reference
to the corresponding entry in inadj[j]?
• Should edges be first-class objects with their own associated data?
In this way, adj would contain lists of edges rather than lists of
vertices (integers).
Most of these questions come down to a tradeoff between complexity (and
space) of implementation and performance features of the implementa-
tion.

（中文关键词：邻接表、图、数组、复杂度、栈）
