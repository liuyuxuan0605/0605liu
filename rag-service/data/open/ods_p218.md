---
structure:
source: open/ods_p218.md
page: 218
---

# ODS p218: §9.2 Red-Black Trees

§9.2 Red-Black Trees
The more complicated case occurs when qis black. In this case, we
examine the colour of v’s left child. If it is red, then vhas two red children
and its extra black can be pushed down with a call to pushBlack (v). At
this point, vnow has w’s original colour, and we are done.
Ifv’s left child is black, then vviolates the left-leaning property, and
we restore this with a call to flipLeft (v). We then return the node vso
that the next iteration of removeFixup (u) then continues with u=v.
RedBlackTree
Node<T> removeFixupCase3(Node<T> u) {
Node<T> w = u.parent;
Node<T> v = w.left;
pullBlack(w);
flipRight(w); // w is now red
Node<T> q = w.left;
if (q.colour == red) { // q-w is red-red
rotateRight(w);
flipLeft(v);
pushBlack(q);
return q;
} else {
if (v.left.colour == red) {
pushBlack(v); // both v’s children are red
return v;
} else { // ensure left-leaning
flipLeft(v);
return w;
}
}
}
Each iteration of removeFixup (u) takes constant time. Cases 2 and 3
either ﬁnish or move ucloser to the root of the tree. Case 0 (where u
is the root) always terminates and Case 1 leads immediately to Case 3,
which also terminates. Since the height of the tree is at most 2log n, we
conclude that there are at most O(logn) iterations of removeFixup (u), so
removeFixup (u) runs inO(logn) time.
204

（中文关键词：红黑树、树）
