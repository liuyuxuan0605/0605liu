---
structure:
source: open/ods_p161.md
page: 161
---

# ODS p161: Discussion and Exercises §6.3

Discussion and Exercises §6.3
6.3 Discussion and Exercises
Binary trees have been used to model relationships for thousands of years.
One reason for this is that binary trees naturally model (pedigree) family
trees. These are the family trees in which the root is a person, the left
and right children are the person’s parents, and so on, recursively. In
more recent centuries binary trees have also been used to model species
trees in biology, where the leaves of the tree represent extant species and
the internal nodes of the tree represent speciation events in which two
populations of a single species evolve into two separate species.
Binary search trees appear to have been discovered independently by
several groups in the 1950s [48, Section 6.2.2]. Further references to spe-
ciﬁc kinds of binary search trees are provided in subsequent chapters.
When implementing a binary tree from scratch, there are several de-
sign decisions to be made. One of these is the question of whether or
not each node stores a pointer to its parent. If most of the operations
simply follow a root-to-leaf path, then parent pointers are unnecessary,
waste space, and are a potential source of coding errors. On the other
hand, the lack of parent pointers means that tree traversals must be done
recursively or with the use of an explicit stack. Some other methods (like
inserting or deleting into some kinds of balanced binary search trees) are
also complicated by the lack of parent pointers.
Another design decision is concerned with how to store the parent,
left child, and right child pointers at a node. In the implementation given
here, these pointers are stored as separate variables. Another option is to
store them in an array, p, of length 3, so that u:p[0] is the left child of u,
u:p[1] is the right child of u, and u:p[2] is the parent of u. Using an array
this way means that some sequences of ifstatements can be simpliﬁed
into algebraic expressions.
An example of such a simpliﬁcation occurs during tree traversal. If a
traversal arrives at a node ufrom u:p[i], then the next node in the traver-
sal is u:p[(i+ 1) mod 3]. Similar examples occur when there is left-right
symmetry. For example, the sibling of u:p[i] isu:p[(i+ 1) mod 2]. This
trick works whether u:p[i] is a left child ( i= 0) or a right child ( i= 1)
ofu. In some cases this means that some complicated code that would
otherwise need to have both a left version and right version can be writ-
147

（中文关键词：数组、栈、二叉搜索树、二叉树、树）
