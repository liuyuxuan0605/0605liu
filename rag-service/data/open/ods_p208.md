---
structure:
source: open/ods_p208.md
page: 208
---

# ODS p208: §9.2 Red-Black Trees

§9.2 Red-Black Trees
property and the black-height property. While it is no longer surprising
that this can be done, there are a large number of cases that have to be
considered if we try to do a direct simulation of a 2-4 tree by a red-black
tree. At some point, it just becomes simpler to disregard the underlying
2-4 tree and work directly towards maintaining the properties of the red-
black tree.
9.2.2 Left-Leaning Red-Black Trees
No single deﬁnition of red-black trees exists. Rather, there is a family
of structures that manage to maintain the black-height and no-red-edge
properties during add(x) and remove (x) operations. Di ﬀerent structures
do this in di ﬀerent ways. Here, we implement a data structure that we
call a RedBlackTree . This structure implements a particular variant of
red-black trees that satisﬁes an additional property:
Property 9.5 (left-leaning) .At any node u, ifu:left is black, then u:right
is black.
Note that the red-black tree shown in Figure 9.4 does not satisfy the
left-leaning property; it is violated by the parent of the red node in the
rightmost path.
The reason for maintaining the left-leaning property is that it reduces
the number of cases encountered when updating the tree during add(x)
andremove (x) operations. In terms of 2-4 trees, it implies that every 2-4
tree has a unique representation: A node of degree two becomes a black
node with two black children. A node of degree three becomes a black
node whose left child is red and whose right child is black. A node of
degree four becomes a black node with two red children.
Before we describe the implementation of add(x) and remove (x) in de-
tail, we ﬁrst present some simple subroutines used by these methods that
are illustrated in Figure 9.7. The ﬁrst two subroutines are for manipulat-
ing colours while preserving the black-height property. The pushBlack (u)
method takes as input a black node uthat has two red children and
colours ured and its two children black. The pullBlack (u) method re-
verses this operation:
194

（中文关键词：红黑树、2-4树、树）
