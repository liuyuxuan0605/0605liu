---
structure: 
source: book/ods_12_3_graph-traversal.md
chapter: 12. Graphs
section: 12.3
page: 270
kind: textbook
---

# 12.3 Graph Traversal

In this section we present two algorithms for exploring a graph, starting
at one of its vertices, i, and finding all vertices that are reachable from
i. Both of these algorithms are best suited to graphs represented using
an adjacency list representation. Therefore, when analyzing these algo-
rithms we will assume that the underlying representation is an Adjacen-
cyLists.

（中文关键词：图、邻接表、遍历）

## 12.3.1 Breadth-First Search (1/2)

The bread-first-search algorithm starts at a vertex i and visits, first the
neighbours of i, then the neighbours of the neighbours of i, then the
neighbours of the neighbours of the neighbours of i, and so on.
This algorithm is a generalization of the breadth-first traversal algo-
rithm for binary trees (Section 6.1.2), and is very similar; it uses a queue,
q, that initially contains only i. It then repeatedly extracts an element
from q and adds its neighbours to q, provided that these neighbours have
never been in q before. The only major difference between the breadth-
first-search algorithm for graphs and the one for trees is that the algo-
rithm for graphs has to ensure that it does not add the same vertex to q
more than once. It does this by using an auxiliary boolean array, seen,
that tracks which vertices have already been discovered.
Algorithms
void bfs(Graph g, int r) {
boolean[] seen = new boolean[g.nVertices()];
Queue<Integer> q = new SLList<Integer>();
q.add(r);
seen[r] = true;
while (!q.isEmpty()) {
int i = q.remove();
for (Integer j : g.outEdges(i)) {
0 1 3 7
2 5 4 8
6 10 9 11
Figure 12.4: An example of bread-first-search starting at node 0. Nodes are la-
belled with the order in which they are added to q. Edges that result in nodes
being added to q are drawn in black, other edges are drawn in grey.
if (!seen[j]) {
q.add(j);
seen[j] = true;
}
}
}
}
An example of running bfs(g, 0) on the graph from Figure 12.1 is
shown in Figure 12.4. Different executions are possible, depending on
the ordering of the adjacency lists; Figure 12.4 uses the adjacency lists in
Figure 12.3.
Analyzing the running-time of the bfs(g, i) routine is fairly straight-
forward. The use of the seen array ensures that no vertex is added to q
more than once. Adding (and later removing) each vertex from q takes
constant time per vertex for a total of O(n) time. Since each vertex is pro-
cessed by the inner loop at most once, each adjacency list is processed at
most once, so each edge of G is processed at most once. This processing,
which is done in the inner loop takes constant time per iteration, for a
total of O(m) time. Therefore, the entire algorithm runs in O(n + m) time.
The following theorem summarizes the performance of the bfs(g, r)
algorithm.
Theorem 12.3. When given as input a Graph, g, that is implemented using
the AdjacencyLists data structure, the bfs(g, r) algorithm runs in O(n + m)
time.

（中文关键词：图、邻接表、广度优先搜索、数组、队列、树）

## 12.3.1 Breadth-First Search (2/2)

A breadth-first traversal has some very special properties. Calling
bfs(g, r) will eventually enqueue (and eventually dequeue) every vertex
j such that there is a directed path from r to j. Moreover, the vertices at
distance 0 from r (r itself) will enter q before the vertices at distance 1,
which will enter q before the vertices at distance 2, and so on. Thus, the
bfs(g, r) method visits vertices in increasing order of distance from r and
vertices that cannot be reached from r are never visited at all.
A particularly useful application of the breadth-first-search algorithm
is, therefore, in computing shortest paths. To compute the shortest path
from r to every other vertex, we use a variant of bfs(g, r) that uses an
auxilliary array, p, of length n. When a new vertex j is added to q, we set
p[j] = i. In this way, p[j] becomes the second last node on a shortest path
from r to j. Repeating this, by taking p[p[j], p[p[p[j]]], and so on we can
reconstruct the (reversal of) a shortest path from r to j.
12.3.2

（中文关键词：广度优先搜索、队列、遍历、数组、双端队列）

## 12.3.3 Depth-First Search (1/2)

The depth-first-search algorithm is similar to the standard algorithm for
traversing binary trees; it first fully explores one subtree before returning
to the current node and then exploring the other subtree. Another way to
think of depth-first-search is by saying that it is similar to breadth-first
search except that it uses a stack instead of a queue.
During the execution of the depth-first-search algorithm, each vertex,
i, is assigned a colour, c[i]: white if we have never seen the vertex before,
grey if we are currently visiting that vertex, and black if we are done
visiting that vertex. The easiest way to think of depth-first-search is as a
recursive algorithm. It starts by visiting r. When visiting a vertex i, we
first mark i as grey. Next, we scan i’s adjacency list and recursively visit
any white vertex we find in this list. Finally, we are done processing i, so
we colour i black and return.
Algorithms
void dfs(Graph g, int r) {
0 1 2 3
9 10 11 4
8 7 6 5
Figure 12.5: An example of depth-first-search starting at node 0. Nodes are la-
belled with the order in which they are processed. Edges that result in a recursive
call are drawn in black, other edges are drawn in grey.
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
Although depth-first-search may best be thought of as a recursive al-
gorithm, recursion is not the best way to implement it. Indeed, the code
given above will fail for many large graphs by causing a stack overflow.
An alternative implementation is to replace the recursion stack with an
explicit stack, s. The following implementation does just that:
Algorithms
void dfs2(Graph g, int r) {
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
In the preceding code, when the next vertex, i, is processed, i is
coloured grey and then replaced, on the stack, with its adjacent vertices.
During the next iteration, one of these vertices will be visited.
Not surprisingly, the running times of dfs(g, r) and dfs2(g, r) are the
same as that of bfs(g, r):

（中文关键词：深度优先搜索、栈、图、树、递归、邻接表）

## 12.3.3 Depth-First Search (2/2)

Theorem 12.4. When given as input a Graph, g, that is implemented using
the AdjacencyLists data structure, the dfs(g, r) and dfs2(g, r) algorithms
each run in O(n + m) time.
As with the breadth-first-search algorithm, there is an underlying tree
associated with each execution of depth-first-search. When a node i (cid:44) r
goes from white to grey, this is because dfs(g, i, c) was called recursively
while processing some node i . (In the case of dfs2(g, r) algorithm, i is
(cid:48)
one of the nodes that replaced i on the stack.) If we think of i as the
(cid:48) (cid:48)
parent of i, then we obtain a tree rooted at r. In Figure 12.5, this tree is a
path from vertex 0 to vertex 11.
An important property of the depth-first-search algorithm is the fol-
lowing: Suppose that when node i is coloured grey, there exists a path
from i to some other node j that uses only white vertices. Then j will be
coloured first grey then black before i is coloured black. (This can be
proven by contradiction, by considering any path P from i to j.)
One application of this property is the detection of cycles. Refer to
Figure 12.6. Consider some cycle, C, that can be reached from r. Let
i be the first node of C that is coloured grey, and let j be the node that
P
j i
C
Figure 12.6: The depth-first-search algorithm can be used to detect cycles in G.
The node j is coloured grey while i is still grey. This implies that there is a path,
P , from i to j in the depth-first-search tree, and the edge (j,i) implies that P is
also a cycle.
precedes i on the cycle C. Then, by the above property, j will be coloured
grey and the edge (j, i) will be considered by the algorithm while i is still
grey. Thus, the algorithm can conclude that there is a path, P , from i to
j in the depth-first-search tree and the edge (j, i) exists. Therefore, P is
also a cycle.

（中文关键词：深度优先搜索、树、广度优先搜索、栈、图）
