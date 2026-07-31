---
structure: BST
source: book/ods_6_1_binarytree-a-basic-binary-tree.md
chapter: 6. Binary Trees
section: 6.1
page: 149
kind: textbook
---

# 6.1 BinaryTree: A Basic Binary Tree

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
the number of steps on the path from u to the root:
BinaryTree
int depth(Node u) {
int d = 0;
while (u != r) {
u = u.parent;
d++;
}
return d;
}

（中文关键词：树、二叉树）

## 6.1.1 Recursive Algorithms

Using recursive algorithms makes it very easy to compute facts about bi-
nary trees. For example, to compute the size of (number of nodes in) a
binary tree rooted at node u, we recursively compute the sizes of the two
subtrees rooted at the children of u, sum up these sizes, and add one:
BinaryTree
int size(Node u) {
if (u == nil) return 0;
return 1 + size(u.left) + size(u.right);
}
To compute the height of a node u, we can compute the height of u’s
two subtrees, take the maximum, and add one:
BinaryTree
int height(Node u) {
if (u == nil) return -1;
return 1 + max(height(u.left), height(u.right));
}

（中文关键词：树、二叉树）

## 6.1.2 Traversing Binary Trees (1/2)

The two algorithms from the previous section both use recursion to visit
all the nodes in a binary tree. Each of them visits the nodes of the binary
tree in the same order as the following code:
BinaryTree
void traverse(Node u) {
if (u == nil) return;
traverse(u.left);
traverse(u.right);
}
Using recursion this way produces very short, simple code, but it can
also be problematic. The maximum depth of the recursion is given by the
maximum depth of a node in the binary tree, i.e., the tree’s height. If the
height of the tree is very large, then this recursion could very well use
more stack space than is available, causing a crash.
To traverse a binary tree without recursion, you can use an algorithm
that relies on where it came from to determine where it will go next. See
Figure 6.3. If we arrive at a node u from u.parent, then the next thing to
do is to visit u.left. If we arrive at u from u.left, then the next thing to
do is to visit u.right. If we arrive at u from u.right, then we are done
visiting u’s subtree, and so we return to u.parent. The following code
implements this idea, with code included for handling the cases where
any of u.left, u.right, or u.parent is nil:
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
pute the size of the tree we keep a counter, n, and increment n whenever
visiting a node for the first time:
r
u.parent
u
u.left u.right
Figure 6.3: The three cases that occur at node u when traversing a binary tree
non-recursively, and the resultant traversal of the tree.
BinaryTree
int size2() {
Node u = r, prev = nil, next;
int n = 0;
while (u != nil) {
if (prev == u.parent) {
n++;
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
return n;
}
In some implementations of binary trees, the parent field is not used.

（中文关键词：树、二叉树、递归、遍历、栈）

## 6.1.2 Traversing Binary Trees (2/2)

When this is the case, a non-recursive implementation is still possible,
but the implementation has to use a List (or Stack) to keep track of the
path from the current node to the root.
r
Figure 6.4: During a breadth-first traversal, the nodes of a binary tree are visited
level-by-level, and left-to-right within each level.
A special kind of traversal that does not fit the pattern of the above
functions is the breadth-first traversal. In a breadth-first traversal, the
nodes are visited level-by-level starting at the root and moving down,
visiting the nodes at each level from left to right (see Figure 6.4). This is
similar to the way that we would read a page of English text. Breadth-first
traversal is implemented using a queue, q, that initially contains only the
root, r. At each step, we extract the next node, u, from q, process u and
add u.left and u.right (if they are non-nil) to q:
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
7
3 11
1 5 9 13
4 6 8 12 14
Figure 6.5: A binary search tree.

（中文关键词：遍历、广度优先搜索、树、二叉树、队列、二叉搜索树）
