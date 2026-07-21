---
structure:
source: open/ods_p242.md
page: 242
---

# ODS p242: §11.1 Sorting Algorithms

§11.1 Sorting Algorithms
2
1 12
1 12
1 12
1 12
1 12n
2n
2n
n
4n
4n
4n
4
n
8n
8n
8n
8n
8n
8n
8n
8
........................+ + +
+ + + + + + +
+ + + + + + · · ·
+ + + + + +1 1=n=n=n=n=n=n
+ + + + + + · · ·
Figure 11.2: The merge-sort recursion tree.
two, so that n= 2logn, and log nis an integer. Refer to Figure 11.2. Merge-
sort turns the problem of sorting nelements into two problems, each of
sorting n=2 elements. These two subproblem are then turned into two
problems each, for a total of four subproblems, each of size n=4. These
four subproblems become eight subproblems, each of size n=8, and so
on. At the bottom of this process, n=2 subproblems, each of size two, are
converted into nproblems, each of size one. For each subproblem of size
n=2i, the time spent merging and copying data is O(n=2i). Since there are
2isubproblems of size n=2i, the total time spent working on problems of
size 2i, not counting recursive calls, is
2iO(n=2i) =O(n):
Therefore, the total amount of time taken by merge-sort is
lognX
i=0O(n) =O(nlogn):
The proof of the following theorem is based on preceding analysis,
but has to be a little more careful to deal with the cases where nis not a
power of 2.
Theorem 11.1. ThemergeSort (a;c)algorithm runs in O(nlogn)time and
performs at most nlogncomparisons.
228

（中文关键词：树、归并排序、排序、复杂度分析）
