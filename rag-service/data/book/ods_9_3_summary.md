---
structure: RedBlackTree
source: book/ods_9_3_summary.md
chapter: 9. Red-Black Trees
section: 9.3
page: 219
kind: textbook
---

# 9.3 Summary

## Summary (1/2)

The following theorem summarizes the performance of the RedBlack-
Tree data structure:
Theorem 9.1. A RedBlackTree implements the SSet interface and supports
the operations add(x), remove(x), and find(x) in O(log n) worst-case time per
operation.
Not included in the above theorem is the following extra bonus:
Theorem 9.2. Beginning with an empty RedBlackTree, any sequence of m
add(x) and remove(x) operations results in a total of O(m) time spent during
all calls addFixup(u) and removeFixup(u).
We only sketch a proof of Theorem 9.2. By comparing addFixup(u)
and removeFixup(u) with the algorithms for adding or removing a leaf
in a 2-4 tree, we can convince ourselves that this property is inherited
from a 2-4 tree. In particular, if we can show that the total time spent
splitting, merging, and borrowing in a 2-4 tree is O(m), then this implies
Theorem 9.2.
The proof of this theorem for 2-4 trees uses the potential method of
amortized analysis.2 Define the potential of an internal node u in a 2-4
tree as
1 if u has 2 children
Φ(u) = 0 if u has 3 children

 3 if u has 4 children
and the potential of a 2-4 tr ee as the sum of the potentials of its nodes.
When a split occurs, it is because a node with four children becomes two
nodes, with two and three children. This means that the overall potential
drops by 3 1 0 = 2. When a merge occurs, two nodes that used to have
− −
two children are replaced by one node with three children. The result is
a drop in potential of 2 0 = 2. Therefore, for every split or merge, the
−
potential decreases by two.
Next notice that, if we ignore splitting and merging of nodes, there are
only a constant number of nodes whose number of children is changed by
2See the proofs of Lemma 2.2 and Lemma 3.1 for other applications of the potential
method.
the addition or removal of a leaf. When adding a node, one node has its
number of children increase by one, increasing the potential by at most
three. During the removal of a leaf, one node has its number of children
decrease by one, increasing the potential by at most one, and two nodes
may be involved in a borrowing operation, increasing their total potential
by at most one.

（中文关键词：树、2-4树、摊还分析）

## Summary (2/2)

To summarize, each merge and split causes the potential to drop by
at least two. Ignoring merging and splitting, each addition or removal
causes the potential to rise by at most three, and the potential is always
non-negative. Therefore, the number of splits and merges caused by m
additions or removals on an initially empty tree is at most 3m/2. Theo-
rem 9.2 is a consequence of this analysis and the correspondence between
2-4 trees and red-black trees.

（中文关键词：树、红黑树、2-4树）
