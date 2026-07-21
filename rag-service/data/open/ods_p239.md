---
structure:
source: open/ods_p239.md
page: 239
---

# ODS p239: Chapter 11

Chapter 11
Sorting Algorithms
This chapter discusses algorithms for sorting a set of nitems. This might
seem like a strange topic for a book on data structures, but there are sev-
eral good reasons for including it here. The most obvious reason is that
two of these sorting algorithms (quicksort and heap-sort) are intimately
related to two of the data structures we have already studied (random
binary search trees and heaps, respectively).
The ﬁrst part of this chapter discusses algorithms that sort using only
comparisons and presents three algorithms that run in O(nlogn) time. As
it turns out, all three algorithms are asymptotically optimal; no algorithm
that uses only comparisons can avoid doing roughly nlogncomparisons
in the worst case and even the average case.
Before continuing, we should note that any of the SSet or priority
Queue implementations presented in previous chapters can also be used
to obtain an O(nlogn) time sorting algorithm. For example, we can sort
nitems by performing n add (x) operations followed by n remove () op-
erations on a BinaryHeap orMeldableHeap . Alternatively, we can use n
add(x) operations on any of the binary search tree data structures and
then perform an in-order traversal (Exercise 6.8) to extract the elements
in sorted order. However, in both cases we go through a lot of overhead
to build a structure that is never fully used. Sorting is such an important
problem that it is worthwhile developing direct methods that are as fast,
simple, and space-e ﬃcient as possible.
The second part of this chapter shows that, if we allow other opera-
tions besides comparisons, then all bets are o ﬀ. Indeed, by using array-
225

（中文关键词：数组、队列、二叉搜索树、堆、树、快速排序、排序、随机）
