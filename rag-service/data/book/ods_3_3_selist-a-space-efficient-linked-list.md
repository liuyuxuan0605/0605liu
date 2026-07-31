---
structure: DoublyLinkedList
source: book/ods_3_3_selist-a-space-efficient-linked-list.md
chapter: 3. Linked Lists
section: 3.3
page: 85
kind: textbook
---

# 3.3 SEList: A Space-Efficient Linked List

One of the drawbacks of linked lists (besides the time it takes to access
elements that are deep within the list) is their space usage. Each node in
a DLList requires an additional two references to the next and previous
nodes in the list. Two of the fields in a Node are dedicated to maintaining
the list, and only one of the fields is for storing data!
An SEList (space-efficient list) reduces this wasted space using a sim-
ple idea: Rather than store individual elements in a DLList, we store a
block (array) containing several items. More precisely, an SEList is pa-
rameterized by a block size b. Each individual node in an SEList stores a
block that can hold up to b + 1 elements.
For reasons that will become clear later, it will be helpful if we can
do Deque operations on each block. The data structure that we choose for
this is a BDeque (bounded deque), derived from the ArrayDeque structure
described in Section 2.4. The BDeque differs from the ArrayDeque in one
small way: When a new BDeque is created, the size of the backing array a
is fixed at b + 1 and never grows or shrinks. The important property of a
BDeque is that it allows for the addition or removal of elements at either
the front or back in constant time. This will be useful as elements are
shifted from one block to another.
SEList
class BDeque extends ArrayDeque<T> {
BDeque() {
super(SEList.this.type());
a = newArray(b+1);
}
void resize() { }
}
An SEList is then a doubly-linked list of blocks:
SEList
class Node {
BDeque d;
Node prev, next;
}
SEList
int n;
Node dummy;

（中文关键词：双端队列、数组、链表、双向链表）

## 3.3.1 Space Requirements

An SEList places very tight restrictions on the number of elements in a
block: Unless a block is the last block, then that block contains at least
b 1 and at most b + 1 elements. This means that, if an SEList contains n
−
elements, then it has at most
n/(b 1) + 1 = O(n/b)
−
blocks. The BDeque for each block contains an array of length b + 1 but,
for every block except the last, at most a constant amount of space is
wasted in this array. The remaining memory used by a block is also con-
stant. This means that the wasted space in an SEList is only O(b + n/b).
By choosing a value of b within a constant factor of √n, we can make
the space-overhead of an SEList approach the √n lower bound given in
Section 2.6.2.

（中文关键词：数组、双端队列）

## 3.3.2 Finding Elements

The first challenge we face with an SEList is finding the list item with a
given index i. Note that the location of an element consists of two parts:
1. The node u that contains the block that contains the element with
index i; and
2. the index j of the element within its block.
SEList
class Location {
Node u;
int j;
Location(Node u, int j) {
this.u = u;
this.j = j;
}
}
To find the block that contains a particular element, we proceed the
same way as we do in a DLList. We either start at the front of the list and
traverse in the forward direction, or at the back of the list and traverse
backwards until we reach the node we want. The only difference is that,
each time we move from one node to the next, we skip over a whole block
of elements.
SEList
Location getLocation(int i) {
if (i < n/2) {
Node u = dummy.next;
while (i >= u.d.size()) {
i -= u.d.size();
u = u.next;
}
return new Location(u, i);
} else {
Node u = dummy;
int idx = n;
while (i < idx) {
u = u.prev;
idx -= u.d.size();
}
return new Location(u, i-idx);
}
}
Remember that, with the exception of at most one block, each block
contains at least b 1 elements, so each step in our search gets us b 1
− −
elements closer to the element we are looking for. If we are searching
forward, this means that we reach the node we want after O(1 + i/b)
steps. If we search backwards, then we reach the node we want after
O(1 + (n i)/b) steps. The algorithm takes the smaller of these two quan-
−
tities depending on the value of i, so the time to locate the item with
index i is O(1 + min i, n i /b).
{ − }
Once we know how to locate the item with index i, the get(i) and
set(i, x) operations translate into getting or setting a particular index in
the correct block:
SEList
T get(int i) {
Location l = getLocation(i);
return l.u.d.get(l.j);
}
T set(int i, T x) {
Location l = getLocation(i);
T y = l.u.d.get(l.j);
l.u.d.set(l.j,x);
return y;
}
The running times of these operations are dominated by the time it
takes to locate the item, so they also run in O(1 + min i, n i /b) time.
{ − }

## 3.3.3 Adding an Element (1/2)

Adding elements to an SEList is a little more complicated. Before consid-
ering the general case, we consider the easier operation, add(x), in which
x is added to the end of the list. If the last block is full (or does not exist
because there are no blocks yet), then we first allocate a new block and
append it to the list of blocks. Now that we are sure that the last block
exists and is not full, we append x to the last block.
SEList
boolean add(T x) {
Node last = dummy.prev;
if (last == dummy || last.d.size() == b+1) {
last = addBefore(dummy);
}
last.d.add(x);
n++;
return true;
}
Things get more complicated when we add to the interior of the list
using add(i, x). We first locate i to get the node u whose block contains
the ith list item. The problem is that we want to insert x into u’s block,
but we have to be prepared for the case where u’s block already contains
b + 1 elements, so that it is full and there is no room for x.
Let u , u , u , . . . denote u, u.next, u.next.next, and so on. We explore
0 1 2
u , u , u , . . . looking for a node that can provide space for x. Three cases
0 1 2
can occur during our space exploration (see Figure 3.4):
1. We quickly (in r + 1 b steps) find a node u whose block is not full.
r
≤
In this case, we perform r shifts of an element from one block into
the next, so that the free space in u becomes a free space in u . We
r 0
can then insert x into u ’s block.
0
2. We quickly (in r +1 b steps) run off the end of the list of blocks. In
≤
this case, we add a new empty block to the end of the list of blocks
and proceed as in the first case.
3. After b steps we do not find any block that is not full. In this case,
u , . . . , u is a sequence of b blocks that each contain b+1 elements.
0 b 1
−
We insert a new block u at the end of this sequence and spread the
b
original b(b + 1) elements so that each block of u , . . . , u contains
0 b
a b c d e f g h i j
··· ···
a x b c d e f g h i j
··· ···
a b c d e f g h
···
a x b c d e f g h
···
a b c d e f g h i j k l
··· ···
a x b c d e f g h i j k l
··· ···
Figure 3.4: The three cases that occur during the addition of an item x in the
interior of an SEList. (This SEList has block size b = 3.)
exactly b elements. Now u ’s block contains only b elements so it
0
has room for us to insert x.

## 3.3.3 Adding an Element (2/2)

SEList
void add(int i, T x) {
if (i == n) {
add(x);
return;
}
Location l = getLocation(i);
Node u = l.u;
int r = 0;
while (r < b && u != dummy && u.d.size() == b+1) {
u = u.next;
r++;
}
if (r == b) { // b blocks each with b+1 elements
spread(l.u);
u = l.u;
}
if (u == dummy) { // ran off the end - add new node
u = addBefore(u);
}
while (u != l.u) { // work backwards, shifting elements
u.d.add(0, u.prev.d.remove(u.prev.d.size()-1));
u = u.prev;
}
u.d.add(l.j, x);
n++;
}
The running time of the add(i, x) operation depends on which of the
three cases above occurs. Cases 1 and 2 involve examining and shifting
elements through at most b blocks and take O(b) time. Case 3 involves
calling the spread(u) method, which moves b(b + 1) elements and takes
O(b2) time. If we ignore the cost of Case 3 (which we will account for
later with amortization) this means that the total running time to locate
i and perform the insertion of x is O(b + min i, n i /b).
{ − }

## 3.3.4 Removing an Element

Removing an element from an SEList is similar to adding an element.
We first locate the node u that contains the element with index i. Now,
we have to be prepared for the case where we cannot remove an element
from u without causing u’s block to become smaller than b 1.
−
Again, let u , u , u , . . . denote u, u.next, u.next.next, and so on. We
0 1 2
examine u , u , u , . . . in order to look for a node from which we can bor-
0 1 2
row an element to make the size of u ’s block at least b 1. There are three
0
−
cases to consider (see Figure 3.5):
1. We quickly (in r + 1 b steps) find a node whose block contains
≤
more than b 1 elements. In this case, we perform r shifts of an
−
element from one block into the previous one, so that the extra ele-
ment in u becomes an extra element in u . We can then remove the
r 0
appropriate element from u ’s block.
0
2. We quickly (in r + 1 b steps) run off the end of the list of blocks.
≤
In this case, u is the last block, and there is no need for u ’s block
r r
a b c d e f g
· · · · · ·
a c d e f g
· · · · · ·
a b c d e f
· · ·
a c d e f
· · ·
a b c d e f
· · · · · ·
a c d e f
· · · · · ·
Figure 3.5: The three cases that occur during the removal of an item x in the
interior of an SEList. (This SEList has block size b = 3.)
to contain at least b 1 elements. Therefore, we proceed as above,
−
borrowing an element from u to make an extra element in u . If
r 0
this causes u ’s block to become empty, then we remove it.
r
3. After b steps, we do not find any block containing more than b 1
−
elements. In this case, u , . . . , u is a sequence of b blocks that
0 b 1
−
each contain b 1 elements. We gather these b(b 1) elements into
− −
u , . . . , u so that each of these b 1 blocks contains exactly b el-
0 b 2
− −
ements and we remove u , which is now empty. Now u ’s block
b 1 0
−
contains b elements and we can then remove the appropriate ele-
ment from it.
SEList
T remove(int i) {
Location l = getLocation(i);
T y = l.u.d.get(l.j);
Node u = l.u;
int r = 0;
while (r < b && u != dummy && u.d.size() == b-1) {
u = u.next;
r++;
}
if (r == b) { // b blocks each with b-1 elements
gather(l.u);
}
u = l.u;
u.d.remove(l.j);
while (u.d.size() < b-1 && u.next != dummy) {
u.d.add(u.next.d.remove(0));
u = u.next;
}
if (u.d.isEmpty()) remove(u);
n--;
return y;
}
Like the add(i, x) operation, the running time of the remove(i) opera-
tion is O(b + min i, n i /b) if we ignore the cost of the gather(u) method
{ − }
that occurs in Case 3.

## 3.3.5 Amortized Analysis of Spreading and Gathering (1/2)

Next, we consider the cost of the gather(u) and spread(u) methods that
may be executed by the add(i, x) and remove(i) methods. For the sake of
completeness, here they are:
SEList
void spread(Node u) {
Node w = u;
for (int j = 0; j < b; j++) {
w = w.next;
}
w = addBefore(w);
while (w != u) {
while (w.d.size() < b)
w.d.add(0,w.prev.d.remove(w.prev.d.size()-1));
w = w.prev;
}
}
SEList
void gather(Node u) {
Node w = u;
for (int j = 0; j < b-1; j++) {
while (w.d.size() < b)
w.d.add(w.next.d.remove(0));
w = w.next;
}
remove(w);
}
The running time of each of these methods is dominated by the two
nested loops. Both the inner and outer loops execute at most b + 1 times,
so the total running time of each of these methods is O((b + 1)2) = O(b2).
However, the following lemma shows that these methods execute on at
most one out of every b calls to add(i, x) or remove(i).
Lemma 3.1. If an empty SEList is created and any sequence of m 1 calls
≥
to add(i, x) and remove(i) is performed, then the total time spent during all
calls to spread() and gather() is O(bm).
Proof. We will use the potential method of amortized analysis. We say
that a node u is fragile if u’s block does not contain b elements (so that u is
either the last node, or contains b 1 or b + 1 elements). Any node whose
−
block contains b elements is rugged. Define the potential of an SEList
as the number of fragile nodes it contains. We will consider only the
add(i, x) operation and its relation to the number of calls to spread(u).
The analysis of remove(i) and gather(u) is identical.
Notice that, if Case 1 occurs during the add(i, x) method, then only
one node, u has the size of its block changed. Therefore, at most one
r
node, namely u , goes from being rugged to being fragile. If Case 2 occurs,
r
then a new node is created, and this node is fragile, but no other node
changes size, so the number of fragile nodes increases by one. Thus, in
either Case 1 or Case 2 the potential of the SEList increases by at most
one.
Finally, if Case 3 occurs, it is because u , . . . , u are all fragile nodes.
0 b 1
−
Then spread(u ) is called and these b fragile nodes are replaced with b+1
0
rugged nodes. Finally, x is added to u ’s block, making u fragile. In total
0 0
the potential decreases by b 1.
−
In summary, the potential starts at 0 (there are no nodes in the list).
Each time Case 1 or Case 2 occurs, the potential increases by at most 1.

（中文关键词：摊还分析）

## 3.3.5 Amortized Analysis of Spreading and Gathering (2/2)

Each time Case 3 occurs, the potential decreases by b 1. The poten-
−
tial (which counts the number of fragile nodes) is never less than 0. We
conclude that, for every occurrence of Case 3, there are at least b 1 oc-
−
currences of Case 1 or Case 2. Thus, for every call to spread(u) there are
at least b calls to add(i, x). This completes the proof.

（中文关键词：摊还分析）

## 3.3.6 Summary

The following theorem summarizes the performance of the SEList data
structure:
Theorem 3.3. An SEList implements the List interface. Ignoring the cost
of calls to spread(u) and gather(u), an SEList with block size b supports the
operations
• get(i) and set(i, x) in O(1 + min i, n i /b) time per operation; and
{ − }
• add(i, x) and remove(i) in O(b + min i, n i /b) time per operation.
{ − }
Furthermore, beginning with an empty SEList, any sequence of m add(i, x)
and remove(i) operations results in a total of O(bm) time spent during all
calls to spread(u) and gather(u).
The space (measured in words)1 used by an SEList that stores n elements
is n + O(b + n/b).
The SEList is a trade-off between an ArrayList and a DLList where
the relative mix of these two structures depends on the block size b. At
the extreme b = 2, each SEList node stores at most three values, which
is not much different than a DLList. At the other extreme, b > n, all
the elements are stored in a single array, just like in an ArrayList. In
between these two extremes lies a trade-off between the time it takes to
1Recall Section 1.4 for a discussion of how memory is measured.
add or remove a list item and the time it takes to locate a particular list
item.

（中文关键词：数组）
