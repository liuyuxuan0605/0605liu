---
structure: BST
source: book/ods_6_2_binarysearchtree-an-unbalanced-binary-search-tree.md
chapter: 6. Binary Trees
section: 6.2
page: 154
kind: textbook
---

# 6.2 BinarySearchTree: An Unbalanced Binary Search Tree

A BinarySearchTree is a special kind of binary tree in which each node,
u, also stores a data value, u.x, from some total order. The data values in a
binary search tree obey the binary search tree property: For a node, u, every
data value stored in the subtree rooted at u.left is less than u.x and every
data value stored in the subtree rooted at u.right is greater than u.x. An
example of a BinarySearchTree is shown in Figure 6.5.

（中文关键词：树、二叉搜索树、二叉树）

## 6.2.1 Searching

The binary search tree property is extremely useful because it allows us
to quickly locate a value, x, in a binary search tree. To do this we start
searching for x at the root, r. When examining a node, u, there are three
cases:
1. If x < u.x, then the search proceeds to u.left;
2. If x > u.x, then the search proceeds to u.right;
3. If x = u.x, then we have found the node u containing x.
The search terminates when Case 3 occurs or when u = nil. In the former
case, we found x. In the latter case, we conclude that x is not in the binary
search tree.
BinarySearchTree
T findEQ(T x) {
Node u = r;
while (u != nil) {
int comp = compare(x, u.x);
if (comp < 0)
u = u.left;
else if (comp > 0)
u = u.right;
else
return u.x;
}
return null;
}
Two examples of searches in a binary search tree are shown in Fig-
ure 6.6. As the second example shows, even if we don’t find x in the tree,
we still gain some valuable information. If we look at the last node, u, at
which Case 1 occurred, we see that u.x is the smallest value in the tree that
is greater than x. Similarly, the last node at which Case 2 occurred con-
tains the largest value in the tree that is less than x. Therefore, by keeping
track of the last node, z, at which Case 1 occurs, a BinarySearchTree can
implement the find(x) operation that returns the smallest value stored in
the tree that is greater than or equal to x:
BinarySearchTree
T find(T x) {
Node w = r, z = nil;
while (w != nil) {
int comp = compare(x, w.x);
if (comp < 0) {
z = w;
w = w.left;
} else if (comp > 0) {
w = w.right;
} else {
return w.x;
}
7 7
3 11 3 11
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 12 14
(a) (b)
Figure 6.6: An example of (a) a successful search (for 6) and (b) an unsuccessful
search (for 10) in a binary search tree.
}
return z == nil ? null : z.x;
}

（中文关键词：树、二叉搜索树）

## 6.2.2 Addition

To add a new value, x, to a BinarySearchTree, we first search for x. If we
find it, then there is no need to insert it. Otherwise, we store x at a leaf
child of the last node, p, encountered during the search for x. Whether the
new node is the left or right child of p depends on the result of comparing
x and p.x.
BinarySearchTree
boolean add(T x) {
Node p = findLast(x);
return addChild(p, newNode(x));
}
BinarySearchTree
Node findLast(T x) {
Node w = r, prev = nil;
while (w != nil) {
prev = w;
int comp = compare(x, w.x);
if (comp < 0) {
w = w.left;
} else if (comp > 0) {
w = w.right;
} else {
return w;
}
}
return prev;
}
BinarySearchTree
boolean addChild(Node p, Node u) {
if (p == nil) {
r = u; // inserting into empty tree
} else {
int comp = compare(u.x, p.x);
if (comp < 0) {
p.left = u;
} else if (comp > 0) {
p.right = u;
} else {
return false; // u.x is already in the tree
}
u.parent = p;
}
n++;
return true;
}
An example is shown in Figure 6.7. The most time-consuming part
of this process is the initial search for x, which takes an amount of time
proportional to the height of the newly added node u. In the worst case,
this is equal to the height of the BinarySearchTree.
7 7
3 11 3 11
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 12 14
8.5
Figure 6.7: Inserting the value 8.5 into a binary search tree.

（中文关键词：树、二叉搜索树）

## 6.2.3 Removal

Deleting a value stored in a node, u, of a BinarySearchTree is a little
more difficult. If u is a leaf, then we can just detach u from its parent.
Even better: If u has only one child, then we can splice u from the tree by
having u.parent adopt u’s child (see Figure 6.8):
BinarySearchTree
void splice(Node u) {
Node s, p;
if (u.left != nil) {
s = u.left;
} else {
s = u.right;
}
if (u == r) {
r = s;
p = nil;
} else {
p = u.parent;
if (p.left == u) {
p.left = s;
} else {
p.right = s;
}
}
if (s != nil) {
7
3 11
1 5 9 13
4 6 8 12 14
Figure 6.8: Removing a leaf (6) or a node with only one child (9) is easy.
s.parent = p;
}
n--;
}
Things get tricky, though, when u has two children. In this case, the
simplest thing to do is to find a node, w, that has less than two children
and such that w.x can replace u.x. To maintain the binary search tree
property, the value w.x should be close to the value of u.x. For example,
choosing w such that w.x is the smallest value greater than u.x will work.
Finding the node w is easy; it is the smallest value in the subtree rooted at
u.right. This node can be easily removed because it has no left child (see
Figure 6.9).
BinarySearchTree
void remove(Node u) {
if (u.left == nil || u.right == nil) {
splice(u);
} else {
Node w = u.right;
while (w.left != nil)
w = w.left;
u.x = w.x;
splice(w);
}
}
7 7
3 11 3 12
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 14
Figure 6.9: Deleting a value (11) from a node, u, with two children is done by
replacing u’s value with the smallest value in the right subtree of u.

（中文关键词：树、二叉搜索树）

## 6.2.4 Summary

The find(x), add(x), and remove(x) operations in a BinarySearchTree
each involve following a path from the root of the tree to some node in
the tree. Without knowing more about the shape of the tree it is difficult
to say much about the length of this path, except that it is less than n,
the number of nodes in the tree. The following (unimpressive) theorem
summarizes the performance of the BinarySearchTree data structure:
Theorem 6.1. BinarySearchTree implements the SSet interface and sup-
ports the operations add(x), remove(x), and find(x) in O(n) time per opera-
tion.
Theorem 6.1 compares poorly with Theorem 4.1, which shows that the
SkiplistSSet structure can implement the SSet interface with O(log n)
expected time per operation. The problem with the BinarySearchTree
structure is that it can become unbalanced. Instead of looking like the
tree in Figure 6.5 it can look like a long chain of n nodes, all but the last
having exactly one child.
There are a number of ways of avoiding unbalanced binary search
trees, all of which lead to data structures that have O(log n) time opera-
tions. In Chapter 7 we show how O(log n) expected time operations can
be achieved with randomization. In Chapter 8 we show how O(log n)
amortized time operations can be achieved with partial rebuilding opera-
tions. In Chapter 9 we show how O(log n) worst-case time operations can
be achieved by simulating a tree that is not binary: one in which nodes
can have up to four children.

（中文关键词：树、摊还分析、跳表）
