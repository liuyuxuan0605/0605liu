---
structure:
source: open/ods_p154.md
page: 154
---

# ODS p154: §6.2 Binary Trees

§6.2 Binary Trees
1
4 6 12 14133
57
11
9
8
Figure 6.5: A binary search tree.
6.2 BinarySearchTree : An Unbalanced Binary Search
Tree
ABinarySearchTree is a special kind of binary tree in which each node,
u, also stores a data value, u:x, from some total order. The data values in a
binary search tree obey the binary search tree property : For a node, u, every
data value stored in the subtree rooted at u:left is less than u:xand every
data value stored in the subtree rooted at u:right is greater than u:x. An
example of a BinarySearchTree is shown in Figure 6.5.
6.2.1 Searching
The binary search tree property is extremely useful because it allows us
to quickly locate a value, x, in a binary search tree. To do this we start
searching for xat the root, r. When examining a node, u, there are three
cases:
1. If x<u:x, then the search proceeds to u:left ;
2. If x>u:x, then the search proceeds to u:right ;
3. If x=u:x, then we have found the node ucontaining x.
The search terminates when Case 3 occurs or when u=nil. In the former
case, we found x. In the latter case, we conclude that xis not in the binary
140

（中文关键词：二叉搜索树、二叉树、树）
