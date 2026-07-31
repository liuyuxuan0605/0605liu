---
structure: BST
source: book/ods_7_2_treap-a-randomized-binary-search-tree.md
chapter: 7. Random Binary Search Trees
section: 7.2
page: 173
kind: textbook
---

# 7.2 Treap: A Randomized Binary Search Tree

## Treap: A Randomized Binary Search Tree (1/5)

The problem with random binary search trees is, of course, that they
are not dynamic. They don’t support the add(x) or remove(x) operations
needed to implement the SSet interface. In this section we describe a
data structure called a Treap that uses Lemma 7.1 to implement the SSet
interface.2
A node in a Treap is like a node in a BinarySearchTree in that it has
a data value, x, but it also contains a unique numerical priority, p, that is
assigned at random:
Treap
class Node<T> extends BSTNode<Node<T>,T> {
int p;
}
In addition to being a binary search tree, the nodes in a Treap also
obey the heap property:
• (Heap Property) At every node u, except the root, u.parent.p < u.p.
In other words, each node has a priority smaller than that of its two chil-
dren. An example is shown in Figure 7.5.
The heap and binary search tree conditions together ensure that, once
the key (x) and priority (p) for each node are defined, the shape of the
Treap is completely determined. The heap property tells us that the node
2The names Treap comes from the fact that this data structure is simultaneously a binary
search tree (Section 6.2) and a heap (Chapter 10).
3, 1
1, 6 5, 11
0, 9 2, 99 4, 14 9, 17
7, 22
6, 42 8, 49
Figure 7.5: An example of a Treap containing the integers 0,..., 9. Each node, u,
is illustrated as a box containing u.x,u.p.
with minimum priority has to be the root, r, of the Treap. The binary
search tree property tells us that all nodes with keys smaller than r.x are
stored in the subtree rooted at r.left and all nodes with keys larger than
r.x are stored in the subtree rooted at r.right.
The important point about the priority values in a Treap is that they
are unique and assigned at random. Because of this, there are two equiv-
alent ways we can think about a Treap. As defined above, a Treap obeys
the heap and binary search tree properties. Alternatively, we can think
of a Treap as a BinarySearchTree whose nodes were added in increasing
order of priority. For example, the Treap in Figure 7.5 can be obtained by
adding the sequence of (x, p) values
(3, 1), (1, 6), (0, 9), (5, 11), (4, 14), (9, 17), (7, 22), (6, 42), (8, 49), (2, 99)
(cid:104) (cid:105)
into a BinarySearchTree.

（中文关键词：树堆、树、堆、二叉搜索树、随机化）

## Treap: A Randomized Binary Search Tree (2/5)

Since the priorities are chosen randomly, this is equivalent to taking a
random permutation of the keys—in this case the permutation is
3, 1, 0, 5, 9, 4, 7, 6, 8, 2
(cid:104) (cid:105)
—and adding these to a BinarySearchTree. But this means that the
shape of a treap is identical to that of a random binary search tree. In
particular, if we replace each key x by its rank,3 then Lemma 7.1 applies.
Restating Lemma 7.1 in terms of Treaps, we have:
Lemma 7.2. In a Treap that stores a set S of n keys, the following statements
hold:
1. For any x S, the expected length of the search path for x is H +
r(x)+1
∈
H O(1).
n r(x)
− −
2. For any x (cid:60) S, the expected length of the search path for x is H +
r(x)
H .
n r(x)
−
Here, r(x) denotes the rank of x in the set S x .
∪ { }
Again, we emphasize that the expectation in Lemma 7.2 is taken over
the random choices of the priorities for each node. It does not require any
assumptions about the randomness in the keys.
Lemma 7.2 tells us that Treaps can implement the find(x) operation
efficiently. However, the real benefit of a Treap is that it can support the
add(x) and delete(x) operations. To do this, it needs to perform rotations
in order to maintain the heap property. Refer to Figure 7.6. A rotation
in a binary search tree is a local modification that takes a parent u of a
node w and makes w the parent of u, while preserving the binary search
tree property. Rotations come in two flavours: left or right depending on
whether w is a right or left child of u, respectively.
The code that implements this has to handle these two possibilities
and be careful of a boundary case (when u is the root), so the actual code
is a little longer than Figure 7.6 would lead a reader to believe:

（中文关键词：树堆、树、二叉搜索树、旋转、随机化、堆）

## Treap: A Randomized Binary Search Tree (3/5)

BinarySearchTree
void rotateLeft(Node u) {
Node w = u.right;
w.parent = u.parent;
if (w.parent != nil) {
if (w.parent.left == u) {
w.parent.left = w;
} else {
3The rank of an element x in a set S of elements is the number of elements in S that are
less than x.
u w
w u
rotateRight(u)
⇒
C rotateLeft(w) A
⇐
A B B C
Figure 7.6: Left and right rotations in a binary search tree.
w.parent.right = w;
}
}
u.right = w.left;
if (u.right != nil) {
u.right.parent = u;
}
u.parent = w;
w.left = u;
if (u == r) { r = w; r.parent = nil; }
}
void rotateRight(Node u) {
Node w = u.left;
w.parent = u.parent;
if (w.parent != nil) {
if (w.parent.left == u) {
w.parent.left = w;
} else {
w.parent.right = w;
}
}
u.left = w.right;
if (u.left != nil) {
u.left.parent = u;
}
u.parent = w;
w.right = u;
if (u == r) { r = w; r.parent = nil; }
}
In terms of the Treap data structure, the most important property of
a rotation is that the depth of w decreases by one while the depth of u
increases by one.
Using rotations, we can implement the add(x) operation as follows:
We create a new node, u, assign u.x = x, and pick a random value for u.p.
Next we add u using the usual add(x) algorithm for a BinarySearchTree,
so that u is now a leaf of the Treap. At this point, our Treap satisfies
the binary search tree property, but not necessarily the heap property. In
particular, it may be the case that u.parent.p > u.p. If this is the case, then
we perform a rotation at node w=u.parent so that u becomes the parent of
w. If u continues to violate the heap property, we will have to repeat this,
decreasing u’s depth by one every time, until u either becomes the root or
u.parent.p < u.p.
Treap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
u.p = rand.nextInt();
if (super.add(u)) {
bubbleUp(u);
return true;
}
return false;
}
void bubbleUp(Node<T> u) {
while (u.parent != nil && u.parent.p > u.p) {
if (u.parent.right == u) {
rotateLeft(u.parent);
} else {
rotateRight(u.parent);
}
}
if (u.parent == nil) {
r = u;
}
}
An example of an add(x) operation is shown in Figure 7.7.
The running time of the add(x) operation is given by the time it takes
to follow the search path for x plus the number of rotations performed
to move the newly-added node, u, up to its correct location in the Treap.

（中文关键词：树堆、旋转、树、二叉搜索树、堆、随机化）

## Treap: A Randomized Binary Search Tree (4/5)

By Lemma 7.2, the expected length of the search path is at most 2 ln n +
O(1). Furthermore, each rotation decreases the depth of u. This stops if
u becomes the root, so the expected number of rotations cannot exceed
the expected length of the search path. Therefore, the expected running
time of the add(x) operation in a Treap is O(log n). (Exercise 7.5 asks
you to show that the expected number of rotations performed during an
addition is actually only O(1).)
The remove(x) operation in a Treap is the opposite of the add(x) op-
eration. We search for the node, u, containing x, then perform rotations
to move u downwards until it becomes a leaf, and then we splice u from
the Treap. Notice that, to move u downwards, we can perform either a
left or right rotation at u, which will replace u with u.right or u.left,
respectively. The choice is made by the first of the following that apply:
1. If u.left and u.right are both null, then u is a leaf and no rotation
is performed.
2. If u.left (or u.right) is null, then perform a right (or left, respec-
tively) rotation at u.
3. If u.left.p < u.right.p (or u.left.p > u.right.p), then perform a
right rotation (or left rotation, respectively) at u.
These three rules ensure that the Treap doesn’t become disconnected and
that the heap property is restored once u is removed.
Treap
boolean remove(T x) {
Node<T> u = findLast(x);
if (u != nil && compare(u.x, x) == 0) {
trickleDown(u);
splice(u);
return true;
3, 1
1, 6 5, 11
0, 9 2, 99 4, 14 9, 14
1.5, 4 7, 22
6, 42 8, 49
3, 1
1, 6 5, 11
0, 9 1.5, 4 4, 14 9, 14
2, 99 7, 22
6, 42 8, 49
3, 1
1.5, 4 5, 11
1, 6 2, 99 4, 14 9, 14
0, 9 7, 22
6, 42 8, 49
Figure 7.7: Adding the value 1.5 into the Treap from Figure 7.5.
}
return false;
}
void trickleDown(Node<T> u) {
while (u.left != nil || u.right != nil) {
if (u.left == nil) {
rotateLeft(u);
} else if (u.right == nil) {
rotateRight(u);
} else if (u.left.p < u.right.p) {
rotateRight(u);
} else {
rotateLeft(u);
}
if (r == u) {
r = u.parent;
}
}
}
An example of the remove(x) operation is shown in Figure 7.8.

（中文关键词：旋转、树堆、二叉搜索树、随机化、堆、树）

## Treap: A Randomized Binary Search Tree (5/5)

The trick to analyze the running time of the remove(x) operation is to
notice that this operation reverses the add(x) operation. In particular, if
we were to reinsert x, using the same priority u.p, then the add(x) opera-
tion would do exactly the same number of rotations and would restore the
Treap to exactly the same state it was in before the remove(x) operation
took place. (Reading from bottom-to-top, Figure 7.8 illustrates the addi-
tion of the value 9 into a Treap.) This means that the expected running
time of the remove(x) on a Treap of size n is proportional to the expected
running time of the add(x) operation on a Treap of size n 1. We conclude
−
that the expected running time of remove(x) is O(log n).

（中文关键词：树堆、二叉搜索树、随机化、旋转、树）

## 7.2.1 Summary

The following theorem summarizes the performance of the Treap data
structure:
Theorem 7.2. A Treap implements the SSet interface. A Treap supports
the operations add(x), remove(x), and find(x) in O(log n) expected time per
3,1
1,6 5,11
0,9 2,99 4,14 9,17
7,22
6,42 8,49
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 9,17
8,49
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 8,49
9,17
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 8,49
Figure 7.8: Removing the value 9 from the Treap in Figure 7.5.
operation.
It is worth comparing the Treap data structure to the SkiplistSSet
data structure. Both implement the SSet operations in O(log n) expected
time per operation. In both data structures, add(x) and remove(x) involve
a search and then a constant number of pointer changes (see Exercise 7.5
below). Thus, for both these structures, the expected length of the search
path is the critical value in assessing their performance. In a SkiplistS-
Set, the expected length of a search path is
2 log n + O(1) ,
In a Treap, the expected length of a search path is
2 ln n + O(1) 1.386 log n + O(1) .
≈
Thus, the search paths in a Treap are considerably shorter and this trans-
lates into noticeably faster operations on Treaps than Skiplists. Exer-
cise 4.7 in Chapter 4 shows how the expected length of the search path in
a Skiplist can be reduced to
e ln n + O(1) 1.884 log n + O(1)
≈
by using biased coin tosses. Even with this optimization, the expected
length of search paths in a SkiplistSSet is noticeably longer than in a
Treap.

（中文关键词：树堆、跳表）
