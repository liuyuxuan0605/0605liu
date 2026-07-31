---
structure: 
source: book/ods_4_2_skiplistsset-an-efficient-sset.md
chapter: 4. Skiplists
section: 4.2
page: 104
kind: textbook
---

# 4.2 SkiplistSSet: An Efficient SSet

## SkiplistSSet: An Efficient SSet (1/2)

A SkiplistSSet uses a skiplist structure to implement the SSet interface.
When used in this way, the list L stores the elements of the SSet in sorted
0
order. The find(x) method works by following the search path for the
smallest value y such that y x:
≥
SkiplistSSet
Node<T> findPredNode(T x) {
Node<T> u = sentinel;
int r = h;
while (r >= 0) {
while (u.next[r] != null && compare(u.next[r].x,x) < 0)
u = u.next[r]; // go right in list r
r--; // go down into list r-1
}
return u;
}
T find(T x) {
Node<T> u = findPredNode(x);
return u.next[0] == null ? null : u.next[0].x;
}
Following the search path for y is easy: when situated at some node, u,
in L , we look right to u.next[r].x. If x > u.next[r].x, then we take a step
r
to the right in L ; otherwise, we move down into L . Each step (right
r r 1
−
or down) in this search takes only constant time; thus, by Lemma 4.1, the
expected running time of find(x) is O(log n).
Before we can add an element to a SkipListSSet, we need a method
to simulate tossing coins to determine the height, k, of a new node. We do
so by picking a random integer, z, and counting the number of trailing 1s
in the binary representation of z:1
SkiplistSSet
int pickHeight() {
int z = rand.nextInt();
1This method does not exactly replicate the coin-tossing experiment since the value of k
will always be less than the number of bits in an int. However, this will have negligible im-
pact unless the number of elements in the structure is much greater than 232 = 4294967296.
int k = 0;
int m = 1;
while ((z & m) != 0) {
k++;
m <<= 1;
}
return k;
}
To implement the add(x) method in a SkiplistSSet we search for x
and then splice x into a few lists L ,. . . ,L , where k is selected using the
0 k
pickHeight() method. The easiest way to do this is to use an array, stack,
that keeps track of the nodes at which the search path goes down from
some list L into L . More precisely, stack[r] is the node in L where
r r 1 r
−
the search path proceeded down into L . The nodes that we modify to
r 1
−
insert x are precisely the nodes stack[0], . . . , stack[k]. The following code
implements this algorithm for add(x):

（中文关键词：跳表、栈、数组）

## SkiplistSSet: An Efficient SSet (2/2)

SkiplistSSet
boolean add(T x) {
Node<T> u = sentinel;
int r = h;
int comp = 0;
while (r >= 0) {
while (u.next[r] != null
&& (comp = compare(u.next[r].x,x)) < 0)
u = u.next[r];
if (u.next[r] != null && comp == 0) return false;
stack[r--] = u; // going down, store u
}
Node<T> w = new Node<T>(x, pickHeight());
while (h < w.height())
stack[++h] = sentinel; // height increased
for (int i = 0; i < w.next.length; i++) {
w.next[i] = stack[i].next[i];
stack[i].next[i] = w;
}
n++;
return true;
}
0 1 2 3 3.5 4 5 6
sentinel add(3.5)
Figure 4.3: Adding the node containing 3.5 to a skiplist. The nodes stored in
stack are highlighted.
Removing an element, x, is done in a similar way, except that there is
no need for stack to keep track of the search path. The removal can be
done as we are following the search path. We search for x and each time
the search moves downward from a node u, we check if u.next.x = x and
if so, we splice u out of the list:
SkiplistSSet
boolean remove(T x) {
boolean removed = false;
Node<T> u = sentinel;
int r = h;
int comp = 0;
while (r >= 0) {
while (u.next[r] != null
&& (comp = compare(u.next[r].x, x)) < 0) {
u = u.next[r];
}
if (u.next[r] != null && comp == 0) {
removed = true;
u.next[r] = u.next[r].next[r];
if (u == sentinel && u.next[r] == null)
h--; // height has gone down
}
r--;
}
if (removed) n--;
return removed;
}
0 1 2 3 4 5 6
sentinel remove(3)
Figure 4.4: Removing the node containing 3 from a skiplist.

（中文关键词：栈、跳表）

## 4.2.1 Summary

The following theorem summarizes the performance of skiplists when
used to implement sorted sets:
Theorem 4.1. SkiplistSSet implements the SSet interface. A SkiplistS-
Set supports the operations add(x), remove(x), and find(x) in O(log n) ex-
pected time per operation.

（中文关键词：跳表）
