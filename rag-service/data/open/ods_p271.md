---
structure:
source: open/ods_p271.md
page: 271
---

# ODS p271: Graph Traversal §12.3

Graph Traversal §12.3
0 1 3 7
8 4 5 2
6 10 9 11
Figure 12.4: An example of bread-ﬁrst-search starting at node 0. Nodes are la-
belled with the order in which they are added to q. Edges that result in nodes
being added to qare drawn in black, other edges are drawn in grey.
if (!seen[j]) {
q.add(j);
seen[j] = true;
}
}
}
}
An example of running bfs(g;0) on the graph from Figure 12.1 is
shown in Figure 12.4. Di ﬀerent executions are possible, depending on
the ordering of the adjacency lists; Figure 12.4 uses the adjacency lists in
Figure 12.3.
Analyzing the running-time of the bfs(g;i) routine is fairly straight-
forward. The use of the seen array ensures that no vertex is added to q
more than once. Adding (and later removing) each vertex from qtakes
constant time per vertex for a total of O(n) time. Since each vertex is pro-
cessed by the inner loop at most once, each adjacency list is processed at
most once, so each edge of Gis processed at most once. This processing,
which is done in the inner loop takes constant time per iteration, for a
total ofO(m) time. Therefore, the entire algorithm runs in O(n+m) time.
The following theorem summarizes the performance of the bfs(g;r)
algorithm.
257

（中文关键词：数组、图）
