---
structure: 
source: book/ods_4_3_skiplistlist-an-efficient-random-access-list.md
chapter: 4. Skiplists
section: 4.3
page: 107
kind: textbook
---

# 4.3 SkiplistList: An Efficient Random-Access List

## SkiplistList: An Efficient Random-Access List (1/3)

A SkiplistList implements the List interface using a skiplist structure.
In a SkiplistList, L contains the elements of the list in the order in
0
which they appear in the list. As in a SkiplistSSet, elements can be
added, removed, and accessed in O(log n) time.
For this to be possible, we need a way to follow the search path for the
ith element in L . The easiest way to do this is to define the notion of the
0
length of an edge in some list, L . We define the length of every edge in
r
L as 1. The length of an edge, e, in L , r > 0, is defined as the sum of the
0 r
lengths of the edges below e in L . Equivalently, the length of e is the
r 1
−
number of edges in L below e. See Figure 4.5 for an example of a skiplist
0
with the lengths of its edges shown. Since the edges of skiplists are stored
in arrays, the lengths can be stored the same way:
SkiplistList
class Node {
5
L5
5
L4
3 2
L3
3 1 1
L2
3 1 1 1 1
L1
1 1 1 1 1 1 1
L0 0 1 2 3 4 5 6
sentinel
Figure 4.5: The lengths of the edges in a skiplist.
T x;
Node[] next;
int[] length;
Node(T ix, int h) {
x = ix;
next = Array.newInstance(Node.class, h+1);
length = new int[h+1];
}
int height() {
return next.length - 1;
}
}
The useful property of this definition of length is that, if we are cur-
rently at a node that is at position j in L and we follow an edge of length
0
(cid:96), then we move to a node whose position, in L , is j + (cid:96). In this way,
0
while following a search path, we can keep track of the position, j, of the
current node in L . When at a node, u, in L , we go right if j plus the
0 r
length of the edge u.next[r] is less than i. Otherwise, we go down into
L .
r 1
−
SkiplistList
Node findPred(int i) {
Node u = sentinel;
int r = h;
int j = -1; // index of the current node in list 0
while (r >= 0) {
while (u.next[r] != null && j + u.length[r] < i) {
j += u.length[r];
u = u.next[r];
}
r--;
}
return u;
}
SkiplistList
T get(int i) {
return findPred(i).next[0].x;
}
T set(int i, T x) {
Node u = findPred(i).next[0];
T y = u.x;
u.x = x;
return y;
}
Since the hardest part of the operations get(i) and set(i, x) is finding
the ith node in L , these operations run in O(log n) time.
0
Adding an element to a SkiplistList at a position, i, is fairly simple.

（中文关键词：跳表、数组）

## SkiplistList: An Efficient Random-Access List (2/3)

Unlike in a SkiplistSSet, we are sure that a new node will actually be
added, so we can do the addition at the same time as we search for the
new node’s location. We first pick the height, k, of the newly inserted
node, w, and then follow the search path for i. Any time the search path
moves down from L with r k, we splice w into L . The only extra care
r r
≤
needed is to ensure that the lengths of edges are updated properly. See
Figure 4.6.
Note that, each time the search path goes down at a node, u, in L ,
r
the length of the edge u.next[r] increases by one, since we are adding an
element below that edge at position i. Splicing the node w between two
nodes, u and z, works as shown in Figure 4.7. While following the search
path we are already keeping track of the position, j, of u in L . Therefore,
0
we know that the length of the edge from u to w is i j. We can also
−
deduce the length of the edge from w to z from the length, (cid:96), of the edge
from u to z. Therefore, we can splice in w and update the lengths of the
edges in constant time.
5 6
5 6
3 2 3 2 1
3 1 1 2 1 1
3 1 1 2 1 1 1 1
1 1 1 1 1 2 1 1 1 1
0 1 2 3 x 4 5 6
sentinel add(4,x)
Figure 4.6: Adding an element to a SkiplistList.
u z
‘
j
‘ + 1
u w z
i j ‘ + 1 (i j)
− − −
j i
Figure 4.7: Updating the lengths of edges while splicing a node w into a skiplist.
This sounds more complicated than it is, for the code is actually quite
simple:

（中文关键词：跳表）

## SkiplistList: An Efficient Random-Access List (3/3)

SkiplistList
void add(int i, T x) {
Node w = new Node(x, pickHeight());
if (w.height() > h)
h = w.height();
add(i, w);
}
SkiplistList
Node add(int i, Node w) {
Node u = sentinel;
int k = w.height();
int r = h;
int j = -1; // index of u
while (r >= 0) {
5 4
L5
5 4
L4
3 2 1
L3
1
3 1 1
L2
1
3 1 1 1 1
L1
1
1 1 1 1 1 1 1
L0 0 1 2 3 4 5 6
sentinel remove(3)
Figure 4.8: Removing an element from a SkiplistList.
while (u.next[r] != null && j+u.length[r] < i) {
j += u.length[r];
u = u.next[r];
}
u.length[r]++; // accounts for new node in list 0
if (r <= k) {
w.next[r] = u.next[r];
u.next[r] = w;
w.length[r] = u.length[r] - (i - j);
u.length[r] = i - j;
}
r--;
}
n++;
return u;
}
By now, the implementation of the remove(i) operation in a Skip-
listList should be obvious. We follow the search path for the node at
position i. Each time the search path takes a step down from a node, u,
at level r we decrement the length of the edge leaving u at that level. We
also check if u.next[r] is the element of rank i and, if so, splice it out of
the list at that level. An example is shown in Figure 4.8.
SkiplistList
T remove(int i) {
T x = null;
Node u = sentinel;
int r = h;
int j = -1; // index of node u
while (r >= 0) {
while (u.next[r] != null && j+u.length[r] < i) {
j += u.length[r];
u = u.next[r];
}
u.length[r]--; // for the node we are removing
if (j + u.length[r] + 1 == i && u.next[r] != null) {
x = u.next[r].x;
u.length[r] += u.next[r].length[r];
u.next[r] = u.next[r].next[r];
if (u == sentinel && u.next[r] == null)
h--;
}
r--;
}
n--;
return x;
}

（中文关键词：跳表）

## 4.3.1 Summary

The following theorem summarizes the performance of the Skiplist-
List data structure:
Theorem 4.2. A SkiplistList implements the List interface. A Skip-
listList supports the operations get(i), set(i, x), add(i, x), and remove(i)
in O(log n) expected time per operation.

（中文关键词：跳表）
