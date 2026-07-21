---
structure:
source: open/ods_p204.md
page: 204
---

# ODS p204: §9.2 Red-Black Trees

§9.2 Red-Black Trees
of removing a leaf ﬁnishes after at most log nsteps.
9.2 RedBlackTree : A Simulated 2-4 Tree
A red-black tree is a binary search tree in which each node, u, has a colour
which is either redorblack . Red is represented by the value 0 and black
by the value 1.
RedBlackTree
class Node<T> extends BSTNode<Node<T>,T> {
byte colour;
}
Before and after any operation on a red-black tree, the following two
properties are satisﬁed. Each property is deﬁned both in terms of the
colours red and black, and in terms of the numeric values 0 and 1.
Property 9.3 (black-height) .There are the same number of black nodes
on every root to leaf path. (The sum of the colours on any root to leaf path
is the same.)
Property 9.4 (no-red-edge) .No two red nodes are adjacent. (For any node
u, except the root, u:colour +u:parent:colour1.)
Notice that we can always colour the root, r, of a red-black tree black
without violating either of these two properties, so we will assume that
the root is black, and the algorithms for updating a red-black tree will
maintain this. Another trick that simpliﬁes red-black trees is to treat the
external nodes (represented by nil) as black nodes. This way, every real
node, u, of a red-black tree has exactly two children, each with a well-
deﬁned colour. An example of a red-black tree is shown in Figure 9.4.
9.2.1 Red-Black Trees and 2-4 Trees
At ﬁrst it might seem surprising that a red-black tree can be e ﬃciently
updated to maintain the black-height and no-red-edge properties, and
it seems unusual to even consider these as useful properties. However,
190

（中文关键词：二叉搜索树、红黑树、2-4树、树）
