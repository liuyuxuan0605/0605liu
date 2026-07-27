---
structure:
source: open/ods_p236.md
page: 236
---

# ODS p236: §10.3 Heaps

§10.3 Heaps
10.3 Discussion and Exercises
The implicit representation of a complete binary tree as an array, or list,
seems to have been ﬁrst proposed by Eytzinger [27]. He used this rep-
resentation in books containing pedigree family trees of noble families.
The BinaryHeap data structure described here was ﬁrst introduced by
Williams [78].
The randomized MeldableHeap data structure described here appears
to have ﬁrst been proposed by Gambin and Malinowski [34]. Other meld-
able heap implementations exist, including leftist heaps [16, 48, Sec-
tion 5.3.2], binomial heaps [75], Fibonacci heaps [30], pairing heaps [29],
and skew heaps [72], although none of these are as simple as the Meld-
ableHeap structure.
Some of the above structures also support a decreaseKey (u;y) oper-
ation in which the value stored at node uis decreased to y. (It is a pre-
condition that yu:x.) In most of the preceding structures, this opera-
tion can be supported in O(logn) time by removing node uand adding
y. However, some of these structures can implement decreaseKey (u;y)
more e ﬃciently. In particular, decreaseKey (u;y) takesO(1) amortized
time in Fibonacci heaps and O(loglog n) amortized time in a special ver-
sion of pairing heaps [25]. This more e ﬃcient decreaseKey (u;y) opera-
tion has applications in speeding up several graph algorithms, including
Dijkstra’s shortest path algorithm [30].
Exercise 10.1. Illustrate the addition of the values 7 and then 3 to the
BinaryHeap shown at the end of Figure 10.2.
Exercise 10.2. Illustrate the removal of the next two values (6 and 8) on
theBinaryHeap shown at the end of Figure 10.3.
Exercise 10.3. Implement the remove (i) method, that removes the value
stored in a[i] in a BinaryHeap . This method should run in O(logn) time.
Next, explain why this method is not likely to be useful.
Exercise 10.4. Ad-ary tree is a generalization of a binary tree in which
each internal node has dchildren. Using Eytzinger’s method it is also
possible to represent complete d-ary trees using arrays. Work out the
222

（中文关键词：数组、堆、左偏堆、二叉树、树、图、随机、摊还分析）
