---
structure:
source: open/ods_p265.md
page: 265
---

# ODS p265: AdjacencyMatrix : Representing a Graph by a Matrix §12.1

AdjacencyMatrix : Representing a Graph by a Matrix §12.1
These operations clearly take constant time per operation.
Where the adjacency matrix performs poorly is with the outEdges (i)
andinEdges (i) operations. To implement these, we must scan all nen-
tries in the corresponding row or column of aand gather up all the in-
dices, j, where a[i][j], respectively a[j][i], is true.
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
These operations clearly take O(n) time per operation.
Another drawback of the adjacency matrix representation is that it
is large. It stores an nnboolean matrix, so it requires at least n2bits
of memory. The implementation here uses a matrix of boolean values
so it actually uses on the order of n2bytes of memory. A more careful
implementation, which packs wboolean values into each word of memory,
could reduce this space usage to O(n2=w) words of memory.
Theorem 12.1. TheAdjacencyMatrix data structure implements the Graph
interface. An AdjacencyMatrix supports the operations
•addEdge (i;j),removeEdge (i;j), and hasEdge (i;j)in constant time
per operation; and
•inEdges (i), and outEdges (i)inO(n)time per operation.
The space used by an AdjacencyMatrix isO(n2).
Despite its high memory requirements and poor performance of the
inEdges (i) and outEdges (i) operations, an AdjacencyMatrix can still be
251

（中文关键词：数组、图）
