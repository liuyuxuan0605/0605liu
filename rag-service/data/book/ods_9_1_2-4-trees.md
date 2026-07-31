---
structure: RedBlackTree
source: book/ods_9_1_2-4-trees.md
chapter: 9. Red-Black Trees
section: 9.1
page: 200
kind: textbook
---

# 9.1 2-4 Trees

A 2-4 tree is a rooted tree with the following properties:
Property 9.1 (height). All leaves have the same depth.
Property 9.2 (degree). Every internal node has 2, 3, or 4 children.
An example of a 2-4 tree is shown in Figure 9.1. The properties of 2-4
trees imply that their height is logarithmic in the number of leaves:
Lemma 9.1. A 2-4 tree with n leaves has height at most log n.
Proof. The lower-bound of 2 on the number of children of an internal
node implies that, if the height of a 2-4 tree is h, then it has at least 2h
leaves. In other words,
n 2h .
≥
Taking logarithms on both sides of this inequality gives h log n.
≤

（中文关键词：树、2-4树）

## 9.1.1 Adding a Leaf

Adding a leaf to a 2-4 tree is easy (see Figure 9.2). If we want to add a
leaf u as the child of some node w on the second-last level, then we simply
make u a child of w. This certainly maintains the height property, but
could violate the degree property; if w had four children prior to adding
u, then w now has five children. In this case, we split w into two nodes,
w and w’, having two and three children, respectively. But now w’ has no
parent, so we recursively make w’ a child of w’s parent. Again, this may
cause w’s parent to have too many children in which case we split it. This
process goes on until we reach a node that has fewer than four children,
or until we split the root, r, into two nodes r and r . In the latter case,
(cid:48)
we make a new root that has r and r as children. This simultaneously
(cid:48)
increases the depth of all leaves and so maintains the height property.
Since the height of the 2-4 tree is never more than log n, the process of
adding a leaf finishes after at most log n steps.

（中文关键词：2-4树、树）

## 9.1.2 Removing a Leaf

Removing a leaf from a 2-4 tree is a little more tricky (see Figure 9.3). To
remove a leaf u from its parent w, we just remove it. If w had only two
children prior to the removal of u, then w is left with only one child and
violates the degree property.
To correct this, we look at w’s sibling, w . The node w is sure to exist
(cid:48) (cid:48)
since w’s parent had at least two children. If w has three or four children,
(cid:48)
then we take one of these children from w and give it to w. Now w has two
(cid:48)
children and w has two or three children and we are done.
(cid:48)
On the other hand, if w has only two children, then we merge w and
(cid:48)
w into a single node, w, that has three children. Next we recursively re-
(cid:48)
move w from the parent of w . This process ends when we reach a node,
(cid:48) (cid:48)
u, where u or its sibling has more than two children, or when we reach
the root. In the latter case, if the root is left with only one child, then
we delete the root and make its child the new root. Again, this simul-
taneously decreases the height of every leaf and therefore maintains the
height property.
Again, since the height of the tree is never more than log n, the process
w
w
u
w w
0
u
Figure 9.2: Adding a leaf to a 2-4 Tree. This process stops after one split because
w.parent has a degree of less than 4 before the addition.
u
Figure 9.3: Removing a leaf from a 2-4 Tree. This process goes all the way to the
root because each of u’s ancestors and their siblings have only two children.
of removing a leaf finishes after at most log n steps.

（中文关键词：树、2-4树）
