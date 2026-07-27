---
structure:
source: open/ods_p152.md
page: 152
---

# ODS p152: §6.1 Binary Trees

§6.1 Binary Trees
uu.parent
u.left u.right
r
Figure 6.3: The three cases that occur at node uwhen traversing a binary tree
non-recursively, and the resultant traversal of the tree.
BinaryTree
int size2() {
Node u = r, prev = nil, next;
int n = 0;
while (u != nil) {
if (prev == u.parent) {
n++;
if (u.left != nil) next = u.left;
else if (u.right != nil) next = u.right;
else next = u.parent;
} else if (prev == u.left) {
if (u.right != nil) next = u.right;
else next = u.parent;
} else {
next = u.parent;
}
prev = u;
u = next;
}
return n;
}
In some implementations of binary trees, the parent ﬁeld is not used.
When this is the case, a non-recursive implementation is still possible,
but the implementation has to use a List (orStack ) to keep track of the
path from the current node to the root.
138

（中文关键词：栈、二叉树、树）
