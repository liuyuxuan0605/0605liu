---
structure:
source: open/ods_p160.md
page: 160
---

# ODS p160: §6.2 Binary Trees

§6.2 Binary Trees
13
45
67
8 12 1413 911
13
45
67
8 1413 912
Figure 6.9: Deleting a value (11) from a node, u, with two children is done by
replacing u’s value with the smallest value in the right subtree of u.
6.2.4 Summary
The find (x),add(x), and remove (x) operations in a BinarySearchTree
each involve following a path from the root of the tree to some node in
the tree. Without knowing more about the shape of the tree it is di ﬃcult
to say much about the length of this path, except that it is less than n,
the number of nodes in the tree. The following (unimpressive) theorem
summarizes the performance of the BinarySearchTree data structure:
Theorem 6.1. BinarySearchTree implements the SSet interface and sup-
ports the operations add(x),remove (x), and find (x)inO(n)time per opera-
tion.
Theorem 6.1 compares poorly with Theorem 4.1, which shows that the
SkiplistSSet structure can implement the SSet interface with O(logn)
expected time per operation. The problem with the BinarySearchTree
structure is that it can become unbalanced . Instead of looking like the
tree in Figure 6.5 it can look like a long chain of nnodes, all but the last
having exactly one child.
There are a number of ways of avoiding unbalanced binary search
trees, all of which lead to data structures that have O(logn) time opera-
tions. In Chapter 7 we show how O(logn)expected time operations can
be achieved with randomization. In Chapter 8 we show how O(logn)
amortized time operations can be achieved with partial rebuilding opera-
tions. In Chapter 9 we show how O(logn)worst-case time operations can
be achieved by simulating a tree that is not binary: one in which nodes
can have up to four children.
146

（中文关键词：跳表、二叉树、树、随机、摊还分析）
