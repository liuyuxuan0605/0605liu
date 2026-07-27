---
structure:
source: open/ods_p220.md
page: 220
---

# ODS p220: §9.4 Red-Black Trees

§9.4 Red-Black Trees
the addition or removal of a leaf. When adding a node, one node has its
number of children increase by one, increasing the potential by at most
three. During the removal of a leaf, one node has its number of children
decrease by one, increasing the potential by at most one, and two nodes
may be involved in a borrowing operation, increasing their total potential
by at most one.
To summarize, each merge and split causes the potential to drop by
at least two. Ignoring merging and splitting, each addition or removal
causes the potential to rise by at most three, and the potential is always
non-negative. Therefore, the number of splits and merges caused by m
additions or removals on an initially empty tree is at most 3 m=2. Theo-
rem 9.2 is a consequence of this analysis and the correspondence between
2-4 trees and red-black trees.
9.4 Discussion and Exercises
Red-black trees were ﬁrst introduced by Guibas and Sedgewick [38]. De-
spite their high implementation complexity they are found in some of
the most commonly used libraries and applications. Most algorithms and
data structures textbooks discuss some variant of red-black trees.
Andersson [6] describes a left-leaning version of balanced trees that is
similar to red-black trees but has the additional constraint that any node
has at most one red child. This implies that these trees simulate 2-3 trees
rather than 2-4 trees. They are signiﬁcantly simpler, though, than the
RedBlackTree structure presented in this chapter.
Sedgewick [66] describes two versions of left-leaning red-black trees.
These use recursion along with a simulation of top-down splitting and
merging in 2-4 trees. The combination of these two techniques makes for
particularly short and elegant code.
A related, and older, data structure is the AVL tree [3]. AVL trees
areheight-balanced : At each node u, the height of the subtree rooted at
u:left and the subtree rooted at u:right diﬀer by at most one. It follows
immediately that, if F(h) is the minimum number of leaves in a tree of
206

（中文关键词：红黑树、AVL树、2-4树、树、复杂度分析）
