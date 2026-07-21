---
structure:
source: open/ods_p147.md
page: 147
---

# ODS p147: Chapter 6

Chapter 6
Binary Trees
This chapter introduces one of the most fundamental structures in com-
puter science: binary trees. The use of the word tree here comes from
the fact that, when we draw them, the resultant drawing often resembles
the trees found in a forest. There are many ways of ways of deﬁning bi-
nary trees. Mathematically, a binary tree is a connected, undirected, ﬁnite
graph with no cycles, and no vertex of degree greater than three.
For most computer science applications, binary trees are rooted: A
special node, r, of degree at most two is called the root of the tree. For
every node, u,r, the second node on the path from utoris called the
parent ofu. Each of the other nodes adjacent to uis called a child ofu.
Most of the binary trees we are interested in are ordered , so we distinguish
between the left child and right child ofu.
In illustrations, binary trees are usually drawn from the root down-
ward, with the root at the top of the drawing and the left and right chil-
dren respectively given by left and right positions in the drawing (Fig-
ure 6.1). For example, Figure 6.2.a shows a binary tree with nine nodes.
Because binary trees are so important, a certain terminology has de-
veloped for them: The depth of a node, u, in a binary tree is the length of
the path from uto the root of the tree. If a node, w, is on the path from u
tor, then wis called an ancestor ofuanduadescendant ofw. The subtree
of a node, u, is the binary tree that is rooted at uand contains all of u’s
descendants. The height of a node, u, is the length of the longest path
from uto one of its descendants. The height of a tree is the height of its
root. A node, u, is a leafif it has no children.
133

（中文关键词：二叉树、树、图）
