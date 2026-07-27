---
structure:
source: open/ods_p263.md
page: 263
---

# ODS p263: AdjacencyMatrix : Representing a Graph by a Matrix §12.1

AdjacencyMatrix : Representing a Graph by a Matrix §12.1
However, di ﬀerent applications of graphs have di ﬀerent performance
requirements for these operations and, ideally, we can use the simplest
implementation that satisﬁes all the application’s requirements. For this
reason, we discuss two broad categories of graph representations.
12.1 AdjacencyMatrix : Representing a Graph by a Matrix
Anadjacency matrix is a way of representing an nvertex graph G= (V;E)
by an nnmatrix, a, whose entries are boolean values.
AdjacencyMatrix
int n;
boolean[][] a;
AdjacencyMatrix(int n0) {
n = n0;
a = new boolean[n][n];
}
The matrix entry a[i][j] is deﬁned as
a[i][j] =8>><>>:true if (i;j)2E
false otherwise
The adjacency matrix for the graph in Figure 12.1 is shown in Figure 12.2.
In this representation, the operations addEdge (i;j),removeEdge (i;j),
andhasEdge (i;j) just involve setting or reading the matrix entry a[i][j]:
AdjacencyMatrix
void addEdge(int i, int j) {
a[i][j] = true;
}
void removeEdge(int i, int j) {
a[i][j] = false;
}
boolean hasEdge(int i, int j) {
return a[i][j];
}
249

（中文关键词：图）
