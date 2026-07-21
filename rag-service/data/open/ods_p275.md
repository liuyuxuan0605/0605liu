---
structure:
source: open/ods_p275.md
page: 275
---

# ODS p275: Discussion and Exercises §12.4

Discussion and Exercises §12.4
i jCP
Figure 12.6: The depth-ﬁrst-search algorithm can be used to detect cycles in G.
The node jis coloured grey while iis still grey . This implies that there is a path,
P, from itojin the depth-ﬁrst-search tree, and the edge ( j;i) implies that Pis
also a cycle.
precedes ion the cycle C. Then, by the above property, jwill be coloured
grey and the edge ( j;i) will be considered by the algorithm while iis still
grey . Thus, the algorithm can conclude that there is a path, P, from ito
jin the depth-ﬁrst-search tree and the edge ( j;i) exists. Therefore, Pis
also a cycle.
12.4 Discussion and Exercises
The running times of the depth-ﬁrst-search and breadth-ﬁrst-search al-
gorithms are somewhat overstated by the Theorems 12.3 and 12.4. De-
ﬁne nras the number of vertices, i, ofG, for which there exists a path
from rtoi. Deﬁne mras the number of edges that have these vertices
as their sources. Then the following theorem is a more precise statement
of the running times of the breadth-ﬁrst-search and depth-ﬁrst-search al-
gorithms. (This more reﬁned statement of the running time is useful in
some of the applications of these algorithms outlined in the exercises.)
Theorem 12.5. When given as input a Graph ,g, that is implemented using
theAdjacencyLists data structure, the bfs(g;r),dfs(g;r)anddfs2 (g;r)
algorithms each run in O(nr+mr)time.
Breadth-ﬁrst search seems to have been discovered independently by
Moore [52] and Lee [49] in the contexts of maze exploration and circuit
routing, respectively.
Adjacency-list representations of graphs were presented by Hopcroft
and Tarjan [40] as an alternative to the (then more common) adjacency-
261

（中文关键词：树、图）
