---
structure:
source: open/ods_p158.md
page: 158
---

# ODS p158: §6.2 Binary Trees

§6.2 Binary Trees
1
4 6 12 14133
57
11
9
8
1
4 6 12 1413
8.53
57
11
9
8
Figure 6.7: Inserting the value 8 :5 into a binary search tree.
6.2.3 Removal
Deleting a value stored in a node, u, of a BinarySearchTree is a little
more di ﬃcult. If uis a leaf, then we can just detach ufrom its parent.
Even better: If uhas only one child, then we can splice ufrom the tree by
having u:parent adopt u’s child (see Figure 6.8):
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
144

（中文关键词：二叉搜索树、二叉树、树）
