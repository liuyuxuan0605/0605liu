---
structure:
source: open/ods_p155.md
page: 155
---

# ODS p155: BinarySearchTree : An Unbalanced Binary Search Tree §6.2

BinarySearchTree : An Unbalanced Binary Search Tree §6.2
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
ure 6.6. As the second example shows, even if we don’t ﬁnd xin the tree,
we still gain some valuable information. If we look at the last node, u, at
which Case 1 occurred, we see that u:xis the smallest value in the tree that
is greater than x. Similarly, the last node at which Case 2 occurred con-
tains the largest value in the tree that is less than x. Therefore, by keeping
track of the last node, z, at which Case 1 occurs, a BinarySearchTree can
implement the find (x) operation that returns the smallest value stored in
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
141

（中文关键词：二叉搜索树、树）
