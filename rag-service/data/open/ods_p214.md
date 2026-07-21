---
structure:
source: open/ods_p214.md
page: 214
---

# ODS p214: §9.2 Red-Black Trees

§9.2 Red-Black Trees
u.x = w.x;
u = w.right;
}
splice(w);
u.colour += w.colour;
u.parent = w.parent;
removeFixup(u);
return true;
}
TheremoveFixup (u) method takes as its input a node uwhose colour
is black (1) or double-black (2). If uis double-black, then removeFixup (u)
performs a series of rotations and recolouring operations that move the
double-black node up the tree until it can be eliminated. During this
process, the node uchanges until, at the end of this process, urefers to
the root of the subtree that has been changed. The root of this subtree
may have changed colour. In particular, it may have gone from red to
black, so the removeFixup (u) method ﬁnishes by checking if u’s parent
violates the left-leaning property and, if so, ﬁxing it.
RedBlackTree
void removeFixup(Node<T> u) {
while (u.colour > black) {
if (u == r) {
u.colour = black;
} else if (u.parent.left.colour == red) {
u = removeFixupCase1(u);
} else if (u == u.parent.left) {
u = removeFixupCase2(u);
} else {
u = removeFixupCase3(u);
}
}
if (u != r) { // restore left-leaning property if needed
Node<T> w = u.parent;
if (w.right.colour == red && w.left.colour == black) {
flipLeft(w);
}
}
200

（中文关键词：红黑树、树）
