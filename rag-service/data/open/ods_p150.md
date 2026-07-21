---
structure:
source: open/ods_p150.md
page: 150
---

# ODS p150: §6.1 Binary Trees

§6.1 Binary Trees
}
return d;
}
6.1.1 Recursive Algorithms
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
6.1.2 Traversing Binary Trees
The two algorithms from the previous section both use recursion to visit
all the nodes in a binary tree. Each of them visits the nodes of the binary
tree in the same order as the following code:
BinaryTree
void traverse(Node u) {
if (u == nil) return;
traverse(u.left);
traverse(u.right);
}
136

（中文关键词：二叉树、树）
