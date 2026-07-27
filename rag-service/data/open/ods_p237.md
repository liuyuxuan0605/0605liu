---
structure:
source: open/ods_p237.md
page: 237
---

# ODS p237: Discussion and Exercises §10.3

Discussion and Exercises §10.3
equations that, given an index i, determine the index of i’s parent and
each of i’sdchildren in this representation.
Exercise 10.5. Using what you learned in Exercise 10.4, design and im-
plement a DaryHeap , thed-ary generalization of a BinaryHeap . Analyze
the running times of operations on a DaryHeap and test the performance
of your DaryHeap implementation against that of the BinaryHeap imple-
mentation given here.
Exercise 10.6. Illustrate the addition of the values 17 and then 82 in the
MeldableHeap h1 shown in Figure 10.4. Use a coin to simulate a random
bit when needed.
Exercise 10.7. Illustrate the removal of the next two values (4 and 8)
in the MeldableHeap h1 shown in Figure 10.4. Use a coin to simulate a
random bit when needed.
Exercise 10.8. Implement the remove (u) method, that removes the node
ufrom a MeldableHeap . This method should run in O(logn) expected
time.
Exercise 10.9. Show how to ﬁnd the second smallest value in a Binary-
Heap orMeldableHeap in constant time.
Exercise 10.10. Show how to ﬁnd the kth smallest value in a BinaryHeap
orMeldableHeap inO(klogk) time. (Hint: Using another heap might
help.)
Exercise 10.11. Suppose you are given ksorted lists, of total length n. Us-
ing a heap, show how to merge these into a single sorted list in O(nlogk)
time. (Hint: Starting with the case k= 2 can be instructive.)
223

（中文关键词：堆、排序、随机）
