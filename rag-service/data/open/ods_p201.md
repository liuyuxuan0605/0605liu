---
structure:
source: open/ods_p201.md
page: 201
---

# ODS p201: adding a leaf ﬁnishes after at most log nsteps.

2-4 Trees §9.1
9.1.1 Adding a Leaf
Adding a leaf to a 2-4 tree is easy (see Figure 9.2). If we want to add a
leafuas the child of some node won the second-last level, then we simply
make ua child of w. This certainly maintains the height property, but
could violate the degree property; if whad four children prior to adding
u, then wnow has ﬁve children. In this case, we split winto two nodes,
wandw’, having two and three children, respectively. But now w’ has no
parent, so we recursively make w’ a child of w’s parent. Again, this may
cause w’s parent to have too many children in which case we split it. This
process goes on until we reach a node that has fewer than four children,
or until we split the root, r, into two nodes randr0. In the latter case,
we make a new root that has rand r0as children. This simultaneously
increases the depth of all leaves and so maintains the height property.
Since the height of the 2-4 tree is never more than log n, the process of
adding a leaf ﬁnishes after at most log nsteps.
9.1.2 Removing a Leaf
Removing a leaf from a 2-4 tree is a little more tricky (see Figure 9.3). To
remove a leaf ufrom its parent w, we just remove it. If whad only two
children prior to the removal of u, then wis left with only one child and
violates the degree property.
To correct this, we look at w’s sibling, w0. The node w0is sure to exist
since w’s parent had at least two children. If w0has three or four children,
then we take one of these children from w0and give it to w. Now whas two
children and w0has two or three children and we are done.
On the other hand, if w0has only two children, then we merge wand
w0into a single node, w, that has three children. Next we recursively re-
move w0from the parent of w0. This process ends when we reach a node,
u, where uor its sibling has more than two children, or when we reach
the root. In the latter case, if the root is left with only one child, then
we delete the root and make its child the new root. Again, this simul-
taneously decreases the height of every leaf and therefore maintains the
height property.
Again, since the height of the tree is never more than log n, the process
187

（中文关键词：2-4树、树）
