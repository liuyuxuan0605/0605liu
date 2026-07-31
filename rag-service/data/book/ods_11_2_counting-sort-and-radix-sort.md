---
structure: 
source: book/ods_11_2_counting-sort-and-radix-sort.md
chapter: 11. Sorting Algorithms
section: 11.2
page: 252
kind: textbook
---

# 11.2 Counting Sort and Radix Sort

In this section we study two sorting algorithms that are not comparison-
based. Specialized for sorting small integers, these algorithms elude the
lower-bounds of Theorem 11.5 by using (parts of) the elements in a as
indices into an array. Consider a statement of the form
c[a[i]] = 1 .
This statement executes in constant time, but has c.length possible dif-
ferent outcomes, depending on the value of a[i]. This means that the
execution of an algorithm that makes such a statement cannot be mod-
elled as a binary tree. Ultimately, this is the reason that the algorithms in
this section are able to sort faster than comparison-based algorithms.

（中文关键词：排序、计数排序、二叉树、数组、基数排序、树）

## 11.2.1 Counting Sort (1/2)

Suppose we have an input array a consisting of n integers, each in the
range 0, . . . , k 1. The counting-sort algorithm sorts a using an auxiliary
−
array c of counters. It outputs a sorted version of a as an auxiliary array
b.
The idea behind counting-sort is simple: For each i 0, . . . , k 1 ,
∈ { − }
count the number of occurrences of i in a and store this in c[i]. Now,
after sorting, the output will look like c[0] occurrences of 0, followed by
c[1] occurrences of 1, followed by c[2] occurrences of 2,. . . , followed by
c[k 1] occurrences of k 1. The code that does this is very slick, and its
− −
execution is illustrated in Figure 11.7:
Algorithms
int[] countingSort(int[] a, int k) {
int c[] = new int[k];
for (int i = 0; i < a.length; i++)
c[a[i]]++;
for (int i = 1; i < k; i++)
c[i] += c[i-1];
int b[] = new int[a.length];
for (int i = a.length-1; i >= 0; i--)
b[--c[a[i]]] = a[i];
return b;
}
The first for loop in this code sets each counter c[i] so that it counts
the number of occurrences of i in a. By using the values of a as indices,
a 7 2 9 0 1 2 0 9 7 4 4 6 9 1 0 9 3 2 5 9
c 3 2 3 1 2 1 1 2 0 5
0 1 2 3 4 5 6 7 8 9
c 3 5 8 9 11 12 13 15 15 20
0
b 0 0 0 1 1 2 2 2 3 4 4 5 6 7 7 9 9 9 9 9
0 1 2 3 4 5 6 78 9
c 3 5 8 9 11 12 13 15 20
0
a 7 2 9 0 1 2 0 9 7 4 4 6 9 1 0 9 3 2 5 9
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
Figure 11.7: The operation of counting sort on an array of length n = 20 that stores
integers 0,..., k 1 = 9.
−
these counters can all be computed in O(n) time with a single for loop. At
this point, we could use c to fill in the output array b directly. However,
this would not work if the elements of a have associated data. Therefore
we spend a little extra effort to copy the elements of a into b.

（中文关键词：数组、计数排序、排序）

## 11.2.1 Counting Sort (2/2)

The next for loop, which takes O(k) time, computes a running-sum
of the counters so that c[i] becomes the number of elements in a that are
less than or equal to i. In particular, for every i 0, . . . , k 1 , the output
∈ { − }
array, b, will have
b[c[i 1]] = b[c[i 1] + 1] = = b[c[i] 1] = i .
− − · · · −
Finally, the algorithm scans a backwards to place its elements, in order,
into an output array b. When scanning, the element a[i] = j is placed at
location b[c[j] 1] and the value c[j] is decremented.
−
Theorem 11.7. The countingSort(a, k) method can sort an array a contain-
ing n integers in the set 0, . . . , k 1 in O(n + k) time.
{ − }
The counting-sort algorithm has the nice property of being stable; it
preserves the relative order of equal elements. If two elements a[i] and
a[j] have the same value, and i < j then a[i] will appear before a[j] in b.
This will be useful in the next section.

（中文关键词：数组、计数排序）

## 11.2.2 Radix-Sort (1/2)

Counting-sort is very efficient for sorting an array of integers when the
length, n, of the array is not much smaller than the maximum value, k 1,
−
that appears in the array. The radix-sort algorithm, which we now de-
scribe, uses several passes of counting-sort to allow for a much greater
range of maximum values.
Radix-sort sorts w-bit integers by using w/d passes of counting-sort to
sort these integers d bits at a time.2 More precisely, radix sort first sorts
the integers by their least significant d bits, then their next significant d
bits, and so on until, in the last pass, the integers are sorted by their most
significant d bits.
2We assume that d divides w, otherwise we can always increase w to d w/d .
(cid:100) (cid:101)
01010001 11001000 11110000 00000001 00000001
00000001 00101000 01010001 11001000 00001111
11001000 11110000 00000001 00001111 00101000
00101000 01010001 01010101 01010001 01010001
00001111 00000001 11001000 01010101 01010101
11110000 01010101 00101000 00101000 10101010
10101010 10101010 10101010 10101010 11001000
01010101 00001111 00001111 11110000 11110000
Figure 11.8: Using radixsort to sort w = 8-bit integers by using 4 passes of count-
ing sort on d = 2-bit integers.
Algorithms
int[] radixSort(int[] a) {
int[] b = null;
for (int p = 0; p < w/d; p++) {
int c[] = new int[1<<d];
// the next three for loops implement counting-sort
b = new int[a.length];
for (int i = 0; i < a.length; i++)
c[(a[i] >> d*p)&((1<<d)-1)]++;
for (int i = 1; i < 1<<d; i++)
c[i] += c[i-1];
for (int i = a.length-1; i >= 0; i--)
b[--c[(a[i] >> d*p)&((1<<d)-1)]] = a[i];
a = b;
}
return b;
}
(In this code, the expression (a[i]>>d p)&((1<<d) 1) extracts the in-
∗ −
teger whose binary representation is given by bits (p + 1)d 1, . . . , pd of
−
a[i].) An example of the steps of this algorithm is shown in Figure 11.8.
This remarkable algorithm sorts correctly because counting-sort is a
stable sorting algorithm. If x < y are two elements of a, and the most
significant bit at which x differs from y has index r, then x will be placed
before y during pass r/d and subsequent passes will not change the rel-
(cid:98) (cid:99)
ative order of x and y.
Radix-sort performs w/d passes of counting-sort. Each pass requires
O(n + 2d) time. Therefore, the performance of radix-sort is given by the
following theorem.
Theorem 11.8. For any integer d > 0, the radixSort(a, k) method can sort
an array a containing n w-bit integers in O((w/d)(n + 2d)) time.

（中文关键词：基数排序、数组、排序）

## 11.2.2 Radix-Sort (2/2)

If we think, instead, of the elements of the array being in the range
0, . . . , nc 1 , and take d = log n we obtain the following version of The-
{ − } (cid:100) (cid:101)
orem 11.8.
Corollary 11.1. The radixSort(a, k) method can sort an array a containing
n integer values in the range 0, . . . , nc 1 in O(cn) time.
{ − }

（中文关键词：数组、基数排序）
