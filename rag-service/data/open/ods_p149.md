---
structure:
source: open/ods_p149.md
page: 149
---

# ODS p149: BinaryTree : A Basic Binary Tree §6.1

BinaryTree : A Basic Binary Tree §6.1
We sometimes think of the tree as being augmented with external
nodes . Any node that does not have a left child has an external node as
its left child, and, correspondingly, any node that does not have a right
child has an external node as its right child (see Figure 6.2.b). It is easy
to verify, by induction, that a binary tree with n1 real nodes has n+ 1
external nodes.
6.1 BinaryTree : A Basic Binary Tree
The simplest way to represent a node, u, in a binary tree is to explicitly
store the (at most three) neighbours of u:
BinaryTree
class BTNode<Node extends BTNode<Node>> {
Node left;
Node right;
Node parent;
}
When one of these three neighbours is not present, we set it to nil.
In this way, both external nodes of the tree and the parent of the root
correspond to the value nil.
The binary tree itself can then be represented by a reference to its root
node, r:
BinaryTree
Node r;
We can compute the depth of a node, u, in a binary tree by counting
the number of steps on the path from uto the root:
BinaryTree
int depth(Node u) {
int d = 0;
while (u != r) {
u = u.parent;
d++;
135

（中文关键词：二叉树、树）
