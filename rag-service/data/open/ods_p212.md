---
structure:
source: open/ods_p212.md
page: 212
---

# ODS p212: §9.2 Red-Black Trees

§9.2 Red-Black Trees
Otherwise, we ﬁrst determine if u’s parent, w, violates the left-leaning
property and, if so, perform a flipLeft (w) operation and set u=w. This
leaves us in a well-deﬁned state: uis the left child of its parent, w, sow
now satisﬁes the left-leaning property. All that remains is to ensure the
no-red-edge property at u. We only have to worry about the case in which
wis red, since otherwise ualready satisﬁes the no-red-edge property.
Since we are not done yet, uis red and wis red. The no-red-edge prop-
erty (which is only violated by uand not by w) implies that u’s grand-
parent gexists and is black. If g’s right child is red, then the left-leaning
property ensures that both g’s children are red, and a call to pushBlack (g)
makes gred and wblack. This restores the no-red-edge property at u, but
may cause it to be violated at g, so the whole process starts over with
u=g.
Ifg’s right child is black, then a call to flipRight (g) makes wthe
(black) parent of gand gives wtwo red children, uand g. This ensures
that usatisﬁes the no-red-edge property and gsatisﬁes the left-leaning
property. In this case we can stop.
RedBlackTree
void addFixup(Node<T> u) {
while (u.colour == red) {
if (u == r) { // u is the root - done
u.colour = black;
return;
}
Node<T> w = u.parent;
if (w.left.colour == black) { // ensure left-leaning
flipLeft(w);
u = w;
w = u.parent;
}
if (w.colour == black)
return; // no red-red edge = done
Node<T> g = w.parent; // grandparent of u
if (g.right.colour == black) {
flipRight(g);
return;
} else {
pushBlack(g);
198

（中文关键词：红黑树、树）
