---
structure: RedBlackTree
source: book/ods_9_2_redblacktree-a-simulated-2-4-tree.md
chapter: 9. Red-Black Trees
section: 9.2
page: 204
kind: textbook
---

# 9.2 RedBlackTree: A Simulated 2-4 Tree

A red-black tree is a binary search tree in which each node, u, has a colour
which is either red or black. Red is represented by the value 0 and black
by the value 1.
RedBlackTree
class Node<T> extends BSTNode<Node<T>,T> {
byte colour;
}
Before and after any operation on a red-black tree, the following two
properties are satisfied. Each property is defined both in terms of the
colours red and black, and in terms of the numeric values 0 and 1.
Property 9.3 (black-height). There are the same number of black nodes
on every root to leaf path. (The sum of the colours on any root to leaf path
is the same.)
Property 9.4 (no-red-edge). No two red nodes are adjacent. (For any node
u, except the root, u.colour + u.parent.colour 1.)
≥
Notice that we can always colour the root, r, of a red-black tree black
without violating either of these two properties, so we will assume that
the root is black, and the algorithms for updating a red-black tree will
maintain this. Another trick that simplifies red-black trees is to treat the
external nodes (represented by nil) as black nodes. This way, every real
node, u, of a red-black tree has exactly two children, each with a well-
defined colour. An example of a red-black tree is shown in Figure 9.4.

（中文关键词：树、红黑树、二叉搜索树、2-4树）

## 9.2.1 Red-Black Trees and 2-4 Trees (1/2)

At first it might seem surprising that a red-black tree can be efficiently
updated to maintain the black-height and no-red-edge properties, and
it seems unusual to even consider these as useful properties. However,
black node
red node
Figure 9.4: An example of a red-black tree with black-height 3. External (nil)
nodes are drawn as squares.
red-black trees were designed to be an efficient simulation of 2-4 trees as
binary trees.
Refer to Figure 9.5. Consider any red-black tree, T , having n nodes
and perform the following transformation: Remove each red node u and
connect u’s two children directly to the (black) parent of u. After this
transformation we are left with a tree T having only black nodes.
(cid:48)
Every internal node in T has two, three, or four children: A black
(cid:48)
node that started out with two black children will still have two black
children after this transformation. A black node that started out with
one red and one black child will have three children after this transfor-
mation. A black node that started out with two red children will have
four children after this transformation. Furthermore, the black-height
property now guarantees that every root-to-leaf path in T has the same
(cid:48)
length. In other words, T is a 2-4 tree!
(cid:48)
The 2-4 tree T has n + 1 leaves that correspond to the n + 1 external
(cid:48)
nodes of the red-black tree. Therefore, this tree has height at most log(n +
1). Now, every root to leaf path in the 2-4 tree corresponds to a path
from the root of the red-black tree T to an external node. The first and
last node in this path are black and at most one out of every two internal
nodes is red, so this path has at most log(n + 1) black nodes and at most
log(n + 1) 1 red nodes. Therefore, the longest path from the root to any
−
internal node in T is at most
2 log(n + 1) 2 2 log n ,
− ≤
for any n 1. This proves the most important property of red-black trees:
≥
Figure 9.5: Every red-black tree has a corresponding 2-4 tree.
Lemma 9.2. The height of red-black tree with n nodes is at most 2 log n.
Now that we have seen the relationship between 2-4 trees and red-
black trees, it is not hard to believe that we can efficiently maintain a
red-black tree while adding and removing elements.

（中文关键词：树、红黑树、2-4树、二叉树）

## 9.2.1 Red-Black Trees and 2-4 Trees (2/2)

We have already seen that adding an element in a BinarySearchTree
can be done by adding a new leaf. Therefore, to implement add(x) in a
red-black tree we need a method of simulating splitting a node with five
children in a 2-4 tree. A 2-4 tree node with five children is represented
by a black node that has two red children, one of which also has a red
child. We can “split” this node by colouring it red and colouring its two
children black. An example of this is shown in Figure 9.6.
Similarly, implementing remove(x) requires a method of merging two
nodes and borrowing a child from a sibling. Merging two nodes is the in-
verse of a split (shown in Figure 9.6), and involves colouring two (black)
siblings red and colouring their (red) parent black. Borrowing from a sib-
ling is the most complicated of the procedures and involves both rotations
and recolouring nodes.
Of course, during all of this we must still maintain the no-red-edge
w
w
u
w w
0
u
Figure 9.6: Simulating a 2-4 tree split operation during an addition in a red-black
tree. (This simulates the 2-4 tree addition shown in Figure 9.2.)
property and the black-height property. While it is no longer surprising
that this can be done, there are a large number of cases that have to be
considered if we try to do a direct simulation of a 2-4 tree by a red-black
tree. At some point, it just becomes simpler to disregard the underlying
2-4 tree and work directly towards maintaining the properties of the red-
black tree.

（中文关键词：树、2-4树、红黑树、旋转）

## 9.2.2 Left-Leaning Red-Black Trees (1/2)

No single definition of red-black trees exists. Rather, there is a family
of structures that manage to maintain the black-height and no-red-edge
properties during add(x) and remove(x) operations. Different structures
do this in different ways. Here, we implement a data structure that we
call a RedBlackTree. This structure implements a particular variant of
red-black trees that satisfies an additional property:
Property 9.5 (left-leaning). At any node u, if u.left is black, then u.right
is black.
Note that the red-black tree shown in Figure 9.4 does not satisfy the
left-leaning property; it is violated by the parent of the red node in the
rightmost path.
The reason for maintaining the left-leaning property is that it reduces
the number of cases encountered when updating the tree during add(x)
and remove(x) operations. In terms of 2-4 trees, it implies that every 2-4
tree has a unique representation: A node of degree two becomes a black
node with two black children. A node of degree three becomes a black
node whose left child is red and whose right child is black. A node of
degree four becomes a black node with two red children.
Before we describe the implementation of add(x) and remove(x) in de-
tail, we first present some simple subroutines used by these methods that
are illustrated in Figure 9.7. The first two subroutines are for manipulat-
ing colours while preserving the black-height property. The pushBlack(u)
method takes as input a black node u that has two red children and
colours u red and its two children black. The pullBlack(u) method re-
verses this operation:
u u u u
pushBlack(u) pullBlack(u) flipLeft(u) flipRight(u)
⇓ ⇓ ⇓ ⇓
u u
u u
Figure 9.7: Flips, pulls and pushes
RedBlackTree
void pushBlack(Node<T> u) {
u.colour--;
u.left.colour++;
u.right.colour++;
}
void pullBlack(Node<T> u) {
u.colour++;
u.left.colour--;
u.right.colour--;
}
The flipLeft(u) method swaps the colours of u and u.right and then
performs a left rotation at u. This method reverses the colours of these
two nodes as well as their parent-child relationship:

（中文关键词：树、红黑树、2-4树、旋转）

## 9.2.2 Left-Leaning Red-Black Trees (2/2)

RedBlackTree
void flipLeft(Node<T> u) {
swapColors(u, u.right);
rotateLeft(u);
}
The flipLeft(u) operation is especially useful in restoring the left-
leaning property at a node u that violates it (because u.left is black and
u.right is red). In this special case, we can be assured that this oper-
ation preserves both the black-height and no-red-edge properties. The
flipRight(u) operation is symmetric with flipLeft(u), when the roles
of left and right are reversed.
RedBlackTree
void flipRight(Node<T> u) {
swapColors(u, u.left);
rotateRight(u);
}

（中文关键词：树、红黑树）

## 9.2.3 Addition (1/2)

To implement add(x) in a RedBlackTree, we perform a standard Binary-
SearchTree insertion to add a new leaf, u, with u.x = x and set u.colour =
red. Note that this does not change the black height of any node, so it
does not violate the black-height property. It may, however, violate the
left-leaning property (if u is the right child of its parent), and it may
violate the no-red-edge property (if u’s parent is red). To restore these
properties, we call the method addFixup(u).
RedBlackTree
boolean add(T x) {
Node<T> u = newNode(x);
u.colour = red;
boolean added = add(u);
if (added)
addFixup(u);
return added;
}
Illustrated in Figure 9.8, the addFixup(u) method takes as input a
node u whose colour is red and which may violate the no-red-edge prop-
erty and/or the left-leaning property. The following discussion is proba-
bly impossible to follow without referring to Figure 9.8 or recreating it on
a piece of paper. Indeed, the reader may wish to study this figure before
continuing.
If u is the root of the tree, then we can colour u black to restore both
properties. If u’s sibling is also red, then u’s parent must be black, so both
the left-leaning and no-red-edge properties already hold.
u
u.parent.left.colour
w w w
u u u
return flipLeft(w) ; u = w
w
u
w.colour
w w
u u
g.right.colour return
g g g
w w w
u u u
flipRight(g) pushBlack(g) pushBlack(g)
w new u = g new u = g
u g w w
u u
return
Figure 9.8: A single round in the process of fixing Property 2 after an insertion.
Otherwise, we first determine if u’s parent, w, violates the left-leaning
property and, if so, perform a flipLeft(w) operation and set u = w. This
leaves us in a well-defined state: u is the left child of its parent, w, so w
now satisfies the left-leaning property. All that remains is to ensure the
no-red-edge property at u. We only have to worry about the case in which
w is red, since otherwise u already satisfies the no-red-edge property.
Since we are not done yet, u is red and w is red. The no-red-edge prop-
erty (which is only violated by u and not by w) implies that u’s grand-
parent g exists and is black. If g’s right child is red, then the left-leaning
property ensures that both g’s children are red, and a call to pushBlack(g)
makes g red and w black. This restores the no-red-edge property at u, but
may cause it to be violated at g, so the whole process starts over with
u = g.

（中文关键词：树）

## 9.2.3 Addition (2/2)

If g’s right child is black, then a call to flipRight(g) makes w the
(black) parent of g and gives w two red children, u and g. This ensures
that u satisfies the no-red-edge property and g satisfies the left-leaning
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
u = g;
}
}
}
The insertFixup(u) method takes constant time per iteration and
each iteration either finishes or moves u closer to the root. Therefore,
the insertFixup(u) method finishes after O(log n) iterations in O(log n)
time.

（中文关键词：树）

## 9.2.4 Removal (1/4)

The remove(x) operation in a RedBlackTree is the most complicated to
implement, and this is true of all known red-black tree variants. Just
like the remove(x) operation in a BinarySearchTree, this operation boils
down to finding a node w with only one child, u, and splicing w out of the
tree by having w.parent adopt u.
The problem with this is that, if w is black, then the black-height
property will now be violated at w.parent. We may avoid this prob-
lem, temporarily, by adding w.colour to u.colour. Of course, this in-
troduces two other problems: (1) if u and w both started out black, then
u.colour + w.colour = 2 (double black), which is an invalid colour. If
w was red, then it is replaced by a black node u, which may violate the
left-leaning property at u.parent. Both of these problems can be resolved
with a call to the removeFixup(u) method.
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
u.x = w.x;
u = w.right;
}
splice(w);
u.colour += w.colour;
u.parent = w.parent;
removeFixup(u);
return true;
}
The removeFixup(u) method takes as its input a node u whose colour
is black (1) or double-black (2). If u is double-black, then removeFixup(u)
performs a series of rotations and recolouring operations that move the
double-black node up the tree until it can be eliminated. During this
process, the node u changes until, at the end of this process, u refers to
the root of the subtree that has been changed. The root of this subtree
may have changed colour. In particular, it may have gone from red to
black, so the removeFixup(u) method finishes by checking if u’s parent
violates the left-leaning property and, if so, fixing it.

（中文关键词：树、红黑树、旋转）

## 9.2.4 Removal (2/4)

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
}
The removeFixup(u) method is illustrated in Figure 9.9. Again, the
following text will be difficult, if not impossible, to follow without refer-
ring to Figure 9.9. Each iteration of the loop in removeFixup(u) processes
the double-black node u, based on one of four cases:
Case 0: u is the root. This is the easiest case to treat. We recolour u to be
black (this does not violate any of the red-black tree properties).
Case 1: u’s sibling, v, is red. In this case, u’s sibling is the left child of
its parent, w (by the left-leaning property). We perform a right-flip at w
and then proceed to the next iteration. Note that this action causes w’s
parent to violate the left-leaning property and the depth of u to increase.
However, it also implies that the next iteration will be in Case 3 with w
coloured red. When examining Case 3 below, we will see that the process
will stop during the next iteration.
RedBlackTree
Node<T> removeFixupCase1(Node<T> u) {
flipRight(u.parent);
return u;
}
Case 2: u’s sibling, v, is black, and u is the left child of its parent, w. In
this case, we call pullBlack(w), making u black, v red, and darkening the
colour of w to black or double-black. At this point, w does not satisfy the
left-leaning property, so we call flipLeft(w) to fix this.
At this point, w is red and v is the root of the subtree with which we
started. We need to check if w causes the no-red-edge property to be vi-
olated. We do this by inspecting w’s right child, q. If q is black, then w
satisfies the no-red-edge property and we can continue the next iteration
with u = v.

（中文关键词：树、红黑树）

## 9.2.4 Removal (3/4)

Otherwise (q is red), so both the no-red-edge property and the left-
leaning properties are violated at q and w, respectively. The left-leaning
property is restored with a call to rotateLeft(w), but the no-red-edge
property is still violated. At this point, q is the left child of v, w is the
left child of q, q and w are both red, and v is black or double-black. A
flipRight(v) makes q the parent of both v and w. Following this up by a
removeFixupCase2(u) removeFixupCase3(u) removeFixupCase1(u)
w w w
u v v u u
pullBlack(w) pullBlack(w)
flipRight(w)
w w
u v v u
flipLeft(w) flipRight(w) w
new u
v v
w w
u q
q.colour q.colour
v v (new u) v v
w w w
u q q q u q u
v.left.colour
rotateLeft(w) rotateRight(w)
v
v v w w
q q q u q u
w w flipLeft(v) pushBlack(v)
u u
flipRight(v) flipLeft(v) w (new u)
v u w
q q q u
w v v w
u u
pushBlack(q) pushBlack(q)
q q
w v v w
u u
v.right.colour
q q
w v w v
u u
flipLeft(v)
q
w
u v
Figure 9.9: A single round in the process of eliminating a double-black node after
a removal.
pushBlack(q) makes both v and w black and sets the colour of q back to
the original colour of w.
At this point, the double-black node is has been eliminated and the
no-red-edge and black-height properties are reestablished. Only one pos-
sible problem remains: the right child of v may be red, in which case the
left-leaning property would be violated. We check this and perform a
flipLeft(v) to correct it if necessary.
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
Case 3: u’s sibling is black and u is the right child of its parent, w. This
case is symmetric to Case 2 and is handled mostly the same way. The only
differences come from the fact that the left-leaning property is asymmet-
ric, so it requires different handling.
As before, we begin with a call to pullBlack(w), which makes v red
and u black. A call to flipRight(w) promotes v to the root of the subtree.
At this point w is red, and the code branches two ways depending on the
colour of w’s left child, q.
If q is red, then the code finishes up exactly the same way as Case 2
does, but is even simpler since there is no danger of v not satisfying the
left-leaning property.

（中文关键词：树）

## 9.2.4 Removal (4/4)

The more complicated case occurs when q is black. In this case, we
examine the colour of v’s left child. If it is red, then v has two red children
and its extra black can be pushed down with a call to pushBlack(v). At
this point, v now has w’s original colour, and we are done.
If v’s left child is black, then v violates the left-leaning property, and
we restore this with a call to flipLeft(v). We then return the node v so
that the next iteration of removeFixup(u) then continues with u = v.
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
Each iteration of removeFixup(u) takes constant time. Cases 2 and 3
either finish or move u closer to the root of the tree. Case 0 (where u
is the root) always terminates and Case 1 leads immediately to Case 3,
which also terminates. Since the height of the tree is at most 2 log n, we
conclude that there are at most O(log n) iterations of removeFixup(u), so
removeFixup(u) runs in O(log n) time.

（中文关键词：树）
