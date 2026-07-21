---
structure:
source: open/ods_p177.md
page: 177
---

# ODS p177: Treap : A Randomized Binary Search Tree §7.2

Treap : A Randomized Binary Search Tree §7.2
if (u == r) { r = w; r.parent = nil; }
}
In terms of the Treap data structure, the most important property of
a rotation is that the depth of wdecreases by one while the depth of u
increases by one.
Using rotations, we can implement the add(x) operation as follows:
We create a new node, u, assign u:x=x, and pick a random value for u:p.
Next we add uusing the usual add(x) algorithm for a BinarySearchTree ,
so that uis now a leaf of the Treap . At this point, our Treap satisﬁes
the binary search tree property, but not necessarily the heap property. In
particular, it may be the case that u:parent:p>u:p. If this is the case, then
we perform a rotation at node w=u:parent so that ubecomes the parent of
w. Ifucontinues to violate the heap property, we will have to repeat this,
decreasing u’s depth by one every time, until ueither becomes the root or
u:parent:p<u:p.
Treap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
u.p = rand.nextInt();
if (super.add(u)) {
bubbleUp(u);
return true;
}
return false;
}
void bubbleUp(Node<T> u) {
while (u.parent != nil && u.parent.p > u.p) {
if (u.parent.right == u) {
rotateLeft(u.parent);
} else {
rotateRight(u.parent);
}
}
if (u.parent == nil) {
r = u;
}
163

（中文关键词：二叉搜索树、堆、树、随机）
