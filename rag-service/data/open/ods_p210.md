---
structure:
source: open/ods_p210.md
page: 210
---

# ODS p210: §9.2 Red-Black Trees

§9.2 Red-Black Trees
flipRight (u) operation is symmetric with flipLeft (u), when the roles
of left and right are reversed.
RedBlackTree
void flipRight(Node<T> u) {
swapColors(u, u.left);
rotateRight(u);
}
9.2.3 Addition
To implement add(x) in a RedBlackTree , we perform a standard Binary-
SearchTree insertion to add a new leaf, u, with u:x=xand set u:colour =
red. Note that this does not change the black height of any node, so it
does not violate the black-height property. It may, however, violate the
left-leaning property (if uis the right child of its parent), and it may
violate the no-red-edge property (if u’s parent is red). To restore these
properties, we call the method addFixup (u).
RedBlackTree
boolean add(T x) {
Node<T> u = newNode(x);
u.colour = red;
boolean added = add(u);
if (added)
addFixup(u);
return added;
}
Illustrated in Figure 9.8, the addFixup (u) method takes as input a
node uwhose colour is red and which may violate the no-red-edge prop-
erty and/or the left-leaning property. The following discussion is proba-
bly impossible to follow without referring to Figure 9.8 or recreating it on
a piece of paper. Indeed, the reader may wish to study this ﬁgure before
continuing.
Ifuis the root of the tree, then we can colour ublack to restore both
properties. If u’s sibling is also red, then u’s parent must be black, so both
the left-leaning and no-red-edge properties already hold.
196

（中文关键词：红黑树、树）
