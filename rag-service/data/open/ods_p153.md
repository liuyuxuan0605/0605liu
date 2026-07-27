---
structure:
source: open/ods_p153.md
page: 153
---

# ODS p153: BinaryTree : A Basic Binary Tree §6.1

BinaryTree : A Basic Binary Tree §6.1
r
Figure 6.4: During a breadth-ﬁrst traversal, the nodes of a binary tree are visited
level-by-level, and left-to-right within each level.
A special kind of traversal that does not ﬁt the pattern of the above
functions is the breadth-ﬁrst traversal . In a breadth-ﬁrst traversal, the
nodes are visited level-by-level starting at the root and moving down,
visiting the nodes at each level from left to right (see Figure 6.4). This is
similar to the way that we would read a page of English text. Breadth-ﬁrst
traversal is implemented using a queue, q, that initially contains only the
root, r. At each step, we extract the next node, u, from q, process uand
addu:left andu:right (if they are non- nil) toq:
BinaryTree
void bfTraverse() {
Queue<Node> q = new LinkedList<Node>();
if (r != nil) q.add(r);
while (!q.isEmpty()) {
Node u = q.remove();
if (u.left != nil) q.add(u.left);
if (u.right != nil) q.add(u.right);
}
}
139

（中文关键词：队列、二叉树、树）
