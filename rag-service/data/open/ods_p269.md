---
structure:
source: open/ods_p269.md
page: 269
---

# ODS p269: AdjacencyLists : A Graph as a Collection of Lists §12.2

AdjacencyLists : A Graph as a Collection of Lists §12.2
for (int j = 0; j < n; j++)
if (adj[j].contains(i)) edges.add(j);
return edges;
}
This operation is very slow. It scans the adjacency list of every vertex,
so it takesO(n+m) time.
The following theorem summarizes the performance of the above data
structure:
Theorem 12.2. TheAdjacencyLists data structure implements the Graph
interface. An AdjacencyLists supports the operations
•addEdge (i;j)in constant time per operation;
•removeEdge (i;j)andhasEdge (i;j)inO(deg( i))time per operation;
•outEdges (i)in constant time per operation; and
•inEdges (i)inO(n+m)time per operation.
The space used by a AdjacencyLists isO(n+m).
As alluded to earlier, there are many di ﬀerent choices to be made
when implementing a graph as an adjacency list. Some questions that
come up include:
• What type of collection should be used to store each element of adj?
One could use an array-based list, a linked-list, or even a hashtable.
• Should there be a second adjacency list, inadj , that stores, for each
i, the list of vertices, j, such that ( j;i)2E? This can greatly reduce
the running-time of the inEdges (i) operation, but requires slightly
more work when adding or removing edges.
• Should the entry for the edge ( i;j) inadj[i] be linked by a reference
to the corresponding entry in inadj [j]?
• Should edges be ﬁrst-class objects with their own associated data?
In this way, adj would contain lists of edges rather than lists of
vertices (integers).
255

（中文关键词：数组、哈希、图）
