---
structure:
source: open/ods_p215.md
page: 215
---

# ODS p215: RedBlackTree : A Simulated 2-4 Tree §9.2

RedBlackTree : A Simulated 2-4 Tree §9.2
}
The removeFixup (u) method is illustrated in Figure 9.9. Again, the
following text will be di ﬃcult, if not impossible, to follow without refer-
ring to Figure 9.9. Each iteration of the loop in removeFixup (u) processes
the double-black node u, based on one of four cases:
Case 0: uis the root. This is the easiest case to treat. We recolour uto be
black (this does not violate any of the red-black tree properties).
Case 1: u’s sibling, v, is red. In this case, u’s sibling is the left child of
its parent, w(by the left-leaning property). We perform a right-ﬂip at w
and then proceed to the next iteration. Note that this action causes w’s
parent to violate the left-leaning property and the depth of uto increase.
However, it also implies that the next iteration will be in Case 3 with w
coloured red. When examining Case 3 below, we will see that the process
will stop during the next iteration.
RedBlackTree
Node<T> removeFixupCase1(Node<T> u) {
flipRight(u.parent);
return u;
}
Case 2: u’s sibling, v, is black, and uis the left child of its parent, w. In
this case, we call pullBlack (w), making ublack, vred, and darkening the
colour of wto black or double-black. At this point, wdoes not satisfy the
left-leaning property, so we call flipLeft (w) to ﬁx this.
At this point, wis red and vis the root of the subtree with which we
started. We need to check if wcauses the no-red-edge property to be vi-
olated. We do this by inspecting w’s right child, q. Ifqis black, then w
satisﬁes the no-red-edge property and we can continue the next iteration
with u=v.
Otherwise ( qis red), so both the no-red-edge property and the left-
leaning properties are violated at qandw, respectively. The left-leaning
property is restored with a call to rotateLeft (w), but the no-red-edge
property is still violated. At this point, qis the left child of v,wis the
left child of q,qand ware both red, and vis black or double-black. A
flipRight (v) makes qthe parent of both vandw. Following this up by a
201

（中文关键词：红黑树、2-4树、树）
