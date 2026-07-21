---
structure:
source: open/ods_p157.md
page: 157
---

# ODS p157: BinarySearchTree : An Unbalanced Binary Search Tree §6.2

BinarySearchTree : An Unbalanced Binary Search Tree §6.2
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
this is equal to the height of the BinarySearchTree .
143

（中文关键词：二叉搜索树、树）
