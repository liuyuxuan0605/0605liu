---
structure:
source: open/ods_p188.md
page: 188
---

# ODS p188: §8.1 Scapegoat Trees

§8.1 Scapegoat Trees
p.right.parent = p;
} else {
p.left = buildBalanced(a, 0, ns);
p.left.parent = p;
}
}
int packIntoArray(Node<T> u, Node<T>[] a, int i) {
if (u == nil) {
return i;
}
i = packIntoArray(u.left, a, i);
a[i++] = u;
return packIntoArray(u.right, a, i);
}
Node<T> buildBalanced(Node<T>[] a, int i, int ns) {
if (ns == 0)
return nil;
int m = ns / 2;
a[i + m].left = buildBalanced(a, i, m);
if (a[i + m].left != nil)
a[i + m].left.parent = a[i + m];
a[i + m].right = buildBalanced(a, i + m + 1, ns - m - 1);
if (a[i + m].right != nil)
a[i + m].right.parent = a[i + m];
return a[i + m];
}
A call to rebuild (u) takesO(size (u)) time. The resulting subtree has
minimum height; there is no tree of smaller height that has size (u) nodes.
8.1 ScapegoatTree : A Binary Search Tree with Partial
Rebuilding
AScapegoatTree is a BinarySearchTree that, in addition to keeping
track of the number, n, of nodes in the tree also keeps a counter, q, that
maintains an upper-bound on the number of nodes.
ScapegoatTree
int q;
174

（中文关键词：数组、二叉搜索树、替罪羊树、树）
