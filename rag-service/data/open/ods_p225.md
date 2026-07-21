---
structure:
source: open/ods_p225.md
page: 225
---

# ODS p225: Chapter 10

Chapter 10
Heaps
In this chapter, we discuss two implementations of the extremely useful
priority Queue data structure. Both of these structures are a special kind
of binary tree called a heap , which means “a disorganized pile.” This
is in contrast to binary search trees that can be thought of as a highly
organized pile.
The ﬁrst heap implementation uses an array to simulate a complete bi-
nary tree. This very fast implementation is the basis of one of the fastest
known sorting algorithms, namely heapsort (see Section 11.1.3). The sec-
ond implementation is based on more ﬂexible binary trees. It supports a
meld (h) operation that allows the priority queue to absorb the elements
of a second priority queue h.
10.1 BinaryHeap : An Implicit Binary Tree
Our ﬁrst implementation of a (priority) Queue is based on a technique that
is over four hundred years old. Eytzinger’s method allows us to represent
a complete binary tree as an array by laying out the nodes of the tree in
breadth-ﬁrst order (see Section 6.1.2). In this way, the root is stored at
position 0, the root’s left child is stored at position 1, the root’s right child
at position 2, the left child of the left child of the root is stored at position
3, and so on. See Figure 10.1.
If we apply Eytzinger’s method to a su ﬃciently large tree, some pat-
terns emerge. The left child of the node at index iis at index left (i) =
211

（中文关键词：数组、队列、二叉搜索树、堆、二叉树、树、排序、优先队列）
