---
structure:
source: open/ods_p217.md
page: 217
---

# ODS p217: RedBlackTree : A Simulated 2-4 Tree §9.2

RedBlackTree : A Simulated 2-4 Tree §9.2
pushBlack (q) makes both vandwblack and sets the colour of qback to
the original colour of w.
At this point, the double-black node is has been eliminated and the
no-red-edge and black-height properties are reestablished. Only one pos-
sible problem remains: the right child of vmay be red, in which case the
left-leaning property would be violated. We check this and perform a
flipLeft (v) to correct it if necessary.
RedBlackTree
Node<T> removeFixupCase2(Node<T> u) {
Node<T> w = u.parent;
Node<T> v = w.right;
pullBlack(w); // w.left
flipLeft(w); // w is now red
Node<T> q = w.right;
if (q.colour == red) { // q-w is red-red
rotateLeft(w);
flipRight(v);
pushBlack(q);
if (v.right.colour == red)
flipLeft(v);
return q;
} else {
return v;
}
}
Case 3: u’s sibling is black and uis the right child of its parent, w. This
case is symmetric to Case 2 and is handled mostly the same way. The only
diﬀerences come from the fact that the left-leaning property is asymmet-
ric, so it requires di ﬀerent handling.
As before, we begin with a call to pullBlack (w), which makes vred
andublack. A call to flipRight (w) promotes vto the root of the subtree.
At this point wis red, and the code branches two ways depending on the
colour of w’s left child, q.
Ifqis red, then the code ﬁnishes up exactly the same way as Case 2
does, but is even simpler since there is no danger of vnot satisfying the
left-leaning property.
203

（中文关键词：2-4树、树）
