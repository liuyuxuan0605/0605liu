---
structure:
source: open/ods_p156.md
page: 156
---

# ODS p156: §6.2 Binary Trees

§6.2 Binary Trees
1
4 6 12 14133
57
11
9
8
1
4 6 12 14133
57
11
9
8
(a) (b)
Figure 6.6: An example of (a) a successful search (for 6) and (b) an unsuccessful
search (for 10) in a binary search tree.
}
return z == nil ? null : z.x;
}
6.2.2 Addition
To add a new value, x, to a BinarySearchTree , we ﬁrst search for x. If we
ﬁnd it, then there is no need to insert it. Otherwise, we store xat a leaf
child of the last node, p, encountered during the search for x. Whether the
new node is the left or right child of pdepends on the result of comparing
xandp:x.
BinarySearchTree
boolean add(T x) {
Node p = findLast(x);
return addChild(p, newNode(x));
}
BinarySearchTree
Node findLast(T x) {
Node w = r, prev = nil;
while (w != nil) {
142

（中文关键词：二叉搜索树、二叉树、树）
