---
structure:
source: open/ods_p267.md
page: 267
---

# ODS p267: AdjacencyLists : A Graph as a Collection of Lists §12.2

AdjacencyLists : A Graph as a Collection of Lists §12.2
0 1 2 3
7 6 5 4
8 9 10 11
012345 6 7 8 9 10 11
101201 5 6 4 8 9 10
423752 2 3 9 5 6 7
66 86 7 11 10 11
5 910
4
Figure 12.3: A graph and its adjacency lists
adj[i] = new ArrayStack<Integer>();
}
(An example is shown in Figure 12.3.) In this particular implementa-
tion, we represent each list in adjas an ArrayStack , because we would
like constant time access by position. Other options are also possible.
Speciﬁcally, we could have implemented adjas aDLList .
TheaddEdge (i;j) operation just appends the value jto the list adj[i]:
AdjacencyLists
void addEdge(int i, int j) {
adj[i].add(j);
}
This takes constant time.
TheremoveEdge (i;j) operation searches through the list adj[i] until
it ﬁnds jand then removes it:
253

（中文关键词：数组、栈、图）
