---
structure:
source: open/ods_p176.md
page: 176
---

# ODS p176: §7.2 Random Binary Search Trees

§7.2 Random Binary Search Trees
rotateRight (u)⇒
⇐rotateLeft (w)
A BCwu
A
B Cuw
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
162

（中文关键词：二叉搜索树、树、随机）
