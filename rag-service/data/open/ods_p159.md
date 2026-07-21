---
structure:
source: open/ods_p159.md
page: 159
---

# ODS p159: BinarySearchTree : An Unbalanced Binary Search Tree §6.2

BinarySearchTree : An Unbalanced Binary Search Tree §6.2
13
45
67
8 12 1413 911
Figure 6.8: Removing a leaf (6) or a node with only one child (9) is easy.
s.parent = p;
}
n--;
}
Things get tricky, though, when uhas two children. In this case, the
simplest thing to do is to ﬁnd a node, w, that has less than two children
and such that w:xcan replace u:x. To maintain the binary search tree
property, the value w:xshould be close to the value of u:x. For example,
choosing wsuch that w:xis the smallest value greater than u:xwill work.
Finding the node wis easy; it is the smallest value in the subtree rooted at
u:right . This node can be easily removed because it has no left child (see
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
145

（中文关键词：二叉搜索树、树）
