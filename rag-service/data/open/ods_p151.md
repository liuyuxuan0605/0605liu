---
structure:
source: open/ods_p151.md
page: 151
---

# ODS p151: BinaryTree : A Basic Binary Tree §6.1

BinaryTree : A Basic Binary Tree §6.1
Using recursion this way produces very short, simple code, but it can
also be problematic. The maximum depth of the recursion is given by the
maximum depth of a node in the binary tree, i.e., the tree’s height. If the
height of the tree is very large, then this recursion could very well use
more stack space than is available, causing a crash.
To traverse a binary tree without recursion, you can use an algorithm
that relies on where it came from to determine where it will go next. See
Figure 6.3. If we arrive at a node ufrom u:parent , then the next thing to
do is to visit u:left . If we arrive at ufrom u:left , then the next thing to
do is to visit u:right . If we arrive at ufrom u:right , then we are done
visiting u’s subtree, and so we return to u:parent . The following code
implements this idea, with code included for handling the cases where
any of u:left ,u:right , oru:parent isnil:
BinaryTree
void traverse2() {
Node u = r, prev = nil, next;
while (u != nil) {
if (prev == u.parent) {
if (u.left != nil) next = u.left;
else if (u.right != nil) next = u.right;
else next = u.parent;
} else if (prev == u.left) {
if (u.right != nil) next = u.right;
else next = u.parent;
} else {
next = u.parent;
}
prev = u;
u = next;
}
}
The same facts that can be computed with recursive algorithms can
also be computed in this way, without recursion. For example, to com-
pute the size of the tree we keep a counter, n, and increment nwhenever
visiting a node for the ﬁrst time:
137

（中文关键词：栈、二叉树、树）
