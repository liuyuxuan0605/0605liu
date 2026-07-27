---
structure:
source: open/ods_p319.md
page: 319
---

# ODS p319: Discussion and Exercises §14.3

Discussion and Exercises §14.3
B-trees implement the SSet interface. If only the USet interface is
needed, then external memory hashing could be used as an alternative
toB-trees. External memory hashing schemes do exist; see, for example,
Jensen and Pagh [43]. These schemes implement the USet operations in
O(1) expected time in the external memory model. However, for a vari-
ety of reasons, many applications still use B-trees even though they only
require USet operations.
One reason B-trees are such a popular choice is that they often per-
form better than their O(logBn) running time bounds suggest. The rea-
son for this is that, in external memory settings, the value of Bis typically
quite large—in the hundreds or even thousands. This means that 99% or
even 99.9% of the data in a B-tree is stored in the leaves. In a database
system with a large memory, it may be possible to cache all the internal
nodes of aB-tree in RAM, since they only represent 1% or 0.1% of the
total data set. When this happens, this means that a search in a B-tree
involves a very fast search in RAM, through the internal nodes, followed
by a single external memory access to retrieve a leaf.
Exercise 14.1. Show what happens when the keys 1.5 and then 7.5 are
added to the B-tree in Figure 14.2.
Exercise 14.2. Show what happens when the keys 3 and then 4 are re-
moved from the B-tree in Figure 14.2.
Exercise 14.3. What is the maximum number of internal nodes in a B-
tree that stores nkeys (as a function of nandB)?
Exercise 14.4. The introduction to this chapter claims that B-trees only
need an internal memory of size O(B+ logBn). However, the implemen-
tation given here actually requires more memory.
1. Show that the implementation of the add(x) and remove (x) meth-
ods given in this chapter use an internal memory proportional to
BlogBn.
2. Describe how these methods could be modiﬁed in order to reduce
their memory consumption to O(B+ logBn).
Exercise 14.5. Draw the credits used in the proof of Lemma 14.1 on the
trees in Figures 14.6 and 14.7. Verify that (with three additional credits)
305

（中文关键词：哈希、B树、树）
