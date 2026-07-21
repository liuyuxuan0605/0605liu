---
structure:
source: open/ods_p213.md
page: 213
---

# ODS p213: RedBlackTree : A Simulated 2-4 Tree §9.2

RedBlackTree : A Simulated 2-4 Tree §9.2
u = g;
}
}
}
The insertFixup (u) method takes constant time per iteration and
each iteration either ﬁnishes or moves ucloser to the root. Therefore,
theinsertFixup (u) method ﬁnishes after O(logn) iterations in O(logn)
time.
9.2.4 Removal
The remove (x) operation in a RedBlackTree is the most complicated to
implement, and this is true of all known red-black tree variants. Just
like the remove (x) operation in a BinarySearchTree , this operation boils
down to ﬁnding a node wwith only one child, u, and splicing wout of the
tree by having w:parent adopt u.
The problem with this is that, if wis black, then the black-height
property will now be violated at w:parent . We may avoid this prob-
lem, temporarily, by adding w:colour tou:colour . Of course, this in-
troduces two other problems: (1) if uandwboth started out black, then
u:colour +w:colour = 2 (double black), which is an invalid colour. If
wwas red, then it is replaced by a black node u, which may violate the
left-leaning property at u:parent . Both of these problems can be resolved
with a call to the removeFixup (u) method.
RedBlackTree
boolean remove(T x) {
Node<T> u = findLast(x);
if (u == nil || compare(u.x, x) != 0)
return false;
Node<T> w = u.right;
if (w == nil) {
w = u;
u = w.left;
} else {
while (w.left != nil)
w = w.left;
199

（中文关键词：红黑树、2-4树、树）
