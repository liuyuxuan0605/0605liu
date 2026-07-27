---
structure:
source: open/ods_p272.md
page: 272
---

# ODS p272: §12.3 Graphs

§12.3 Graphs
Theorem 12.3. When given as input a Graph ,g, that is implemented using
theAdjacencyLists data structure, the bfs(g;r)algorithm runs in O(n+m)
time.
A breadth-ﬁrst traversal has some very special properties. Calling
bfs(g;r) will eventually enqueue (and eventually dequeue) every vertex
jsuch that there is a directed path from rtoj. Moreover, the vertices at
distance 0 from r(ritself) will enter qbefore the vertices at distance 1,
which will enter qbefore the vertices at distance 2, and so on. Thus, the
bfs(g;r) method visits vertices in increasing order of distance from rand
vertices that cannot be reached from rare never visited at all.
A particularly useful application of the breadth-ﬁrst-search algorithm
is, therefore, in computing shortest paths. To compute the shortest path
from rto every other vertex, we use a variant of bfs(g;r) that uses an
auxilliary array, p, of length n. When a new vertex jis added to q, we set
p[j] =i. In this way, p[j] becomes the second last node on a shortest path
from rtoj. Repeating this, by taking p[p[j],p[p[p[j]]], and so on we can
reconstruct the (reversal of) a shortest path from rtoj.
12.3.2 Depth-First Search
The depth-ﬁrst-search algorithm is similar to the standard algorithm for
traversing binary trees; it ﬁrst fully explores one subtree before returning
to the current node and then exploring the other subtree. Another way to
think of depth-ﬁrst-search is by saying that it is similar to breadth-ﬁrst
search except that it uses a stack instead of a queue.
During the execution of the depth-ﬁrst-search algorithm, each vertex,
i, is assigned a colour, c[i]:white if we have never seen the vertex before,
grey if we are currently visiting that vertex, and black if we are done
visiting that vertex. The easiest way to think of depth-ﬁrst-search is as a
recursive algorithm. It starts by visiting r. When visiting a vertex i, we
ﬁrst mark iasgrey . Next, we scan i’s adjacency list and recursively visit
any white vertex we ﬁnd in this list. Finally, we are done processing i, so
we colour iblack and return.
Algorithms
void dfs(Graph g, int r) {
258

（中文关键词：数组、栈、队列、双端队列、二叉树、树、图、深度优先搜索）
