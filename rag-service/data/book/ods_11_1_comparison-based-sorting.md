---
structure: 
source: book/ods_11_1_comparison-based-sorting.md
chapter: 11. Sorting Algorithms
section: 11.1
page: 240
kind: textbook
---

# 11.1 Comparison-Based Sorting

In this section, we present three sorting algorithms: merge-sort, quick-
sort, and heap-sort. Each of these algorithms takes an input array a and
sorts the elements of a into non-decreasing order in O(n log n) (expected)
time. These algorithms are all comparison-based. Their second argument,
c, is a Comparator that implements the compare(a, b) method. These al-
gorithms don’t care what type of data is being sorted; the only opera-
tion they do on the data is comparisons using the compare(a, b) method.
Recall, from Section 1.2.4, that compare(a, b) returns a negative value if
a < b, a positive value if a > b, and zero if a = b.

（中文关键词：排序、归并排序、堆排序、数组、堆）

## 11.1.1 Merge-Sort (1/3)

The merge-sort algorithm is a classic example of recursive divide and con-
quer: If the length of a is at most 1, then a is already sorted, so we do
nothing. Otherwise, we split a into two halves, a0 = a[0], . . . , a[n/2 1]
−
and a1 = a[n/2], . . . , a[n 1]. We recursively sort a0 and a1, and then we
−
merge (the now sorted) a0 and a1 to get our fully sorted array a:
Algorithms
<T> void mergeSort(T[] a, Comparator<T> c) {
if (a.length <= 1) return;
T[] a0 = Arrays.copyOfRange(a, 0, a.length/2);
T[] a1 = Arrays.copyOfRange(a, a.length/2, a.length);
mergeSort(a0, c);
mergeSort(a1, c);
merge(a0, a1, a, c);
}
An example is shown in Figure 11.1.
Compared to sorting, merging the two sorted arrays a0 and a1 is fairly
easy. We add elements to a one at a time. If a0 or a1 is empty, then we
add the next elements from the other (non-empty) array. Otherwise, we
a 13 8 5 2 4 0 6 9 7 3 12 1 10 11
a0 13 8 5 2 4 0 6 9 7 3 12 1 10 11 a1
mergeSort(a0, c) mergeSort(a1, c)
a0 0 2 4 5 6 8 13 1 3 7 9 10 11 12 a1
merge(a0, a1, a)
a 0 1 2 3 4 5 6 7 8 9 10 11 12 13
Figure 11.1: The execution of mergeSort(a,c)
take the minimum of the next element in a0 and the next element in a1
and add it to a:
Algorithms
<T> void merge(T[] a0, T[] a1, T[] a, Comparator<T> c) {
int i0 = 0, i1 = 0;
for (int i = 0; i < a.length; i++) {
if (i0 == a0.length)
a[i] = a1[i1++];
else if (i1 == a1.length)
a[i] = a0[i0++];
else if (compare(a0[i0], a1[i1]) < 0)
a[i] = a0[i0++];
else
a[i] = a1[i1++];
}
}
Notice that the merge(a0, a1, a, c) algorithm performs at most n 1
−
comparisons before running out of elements in one of a0 or a1.
To understand the running-time of merge-sort, it is easiest to think
of it in terms of its recursion tree. Suppose for now that n is a power of
n = n
n n = n
2 2
n + n + n + n = n
4 4 4 4
n + n + n + n + n + n + n + n = n
8 8 8 8 8 8 8 8
... ... ... ... ... ... ... ...

（中文关键词：归并排序、数组、递归、排序、树）

## 11.1.1 Merge-Sort (2/3)

2 + 2 + 2 + + 2 + 2 + 2 = n
···
1 + 1 + 1 + 1 + 1 + 1 + + 1 + 1 + 1 + 1 + 1 + 1 = n
···
Figure 11.2: The merge-sort recursion tree.
two, so that n = 2logn, and log n is an integer. Refer to Figure 11.2. Merge-
sort turns the problem of sorting n elements into two problems, each of
sorting n/2 elements. These two subproblem are then turned into two
problems each, for a total of four subproblems, each of size n/4. These
four subproblems become eight subproblems, each of size n/8, and so
on. At the bottom of this process, n/2 subproblems, each of size two, are
converted into n problems, each of size one. For each subproblem of size
n/2i, the time spent merging and copying data is O(n/2i). Since there are
2i subproblems of size n/2i, the total time spent working on problems of
size 2i, not counting recursive calls, is
2i O(n/2i) = O(n) .
×
Therefore, the total amount of time taken by merge-sort is
logn
O(n) = O(n log n) .
i=0
(cid:88)
The proof of the following theorem is based on preceding analysis,
but has to be a little more careful to deal with the cases where n is not a
power of 2.
Theorem 11.1. The mergeSort(a, c) algorithm runs in O(n log n) time and
performs at most n log n comparisons.
Proof. The proof is by induction on n. The base case, in which n = 1,
is trivial; when presented with an array of length 0 or 1 the algorithm
simply returns without performing any comparisons.
Merging two sorted lists of total length n requires at most n 1 compar-
−
isons. Let C(n) denote the maximum number of comparisons performed
by mergeSort(a, c) on an array a of length n. If n is even, then we apply
the inductive hypothesis to the two subproblems and obtain
C(n) n 1 + 2C(n/2)
≤ −
n 1 + 2((n/2) log(n/2))
≤ −
= n 1 + n log(n/2)
−
= n 1 + n log n n
− −
< n log n .
The case where n is odd is slightly more complicated. For this case, we
use two inequalities that are easy to verify:
log(x + 1) log(x) + 1 , (11.1)
≤
for all x 1 and
≥
log(x + 1/2) + log(x 1/2) 2 log(x) , (11.2)
− ≤
for all x 1/2. Inequality (11.1) comes from the fact that log(x) + 1 =
≥
log(2x) while (11.2) follows from the fact that log is a concave function.

（中文关键词：归并排序、排序、数组、递归、树）

## 11.1.1 Merge-Sort (3/3)

With these tools in hand we have, for odd n,
C(n) n 1 + C( n/2 ) + C( n/2 )
≤ − (cid:100) (cid:101) (cid:98) (cid:99)
n 1 + n/2 log n/2 + n/2 log n/2
≤ − (cid:100) (cid:101) (cid:100) (cid:101) (cid:98) (cid:99) (cid:98) (cid:99)
= n 1 + (n/2 + 1/2) log(n/2 + 1/2) + (n/2 1/2) log(n/2 1/2)
− − −
n 1 + n log(n/2) + (1/2)(log(n/2 + 1/2) log(n/2 1/2))
≤ − − −
n 1 + n log(n/2) + 1/2
≤ −
< n + n log(n/2)
= n + n(log n 1)
−
= n log n .

（中文关键词：归并排序）

## 11.1.2 Quicksort (1/3)

The quicksort algorithm is another classic divide and conquer algorithm.
Unlike merge-sort, which does merging after solving the two subprob-
lems, quicksort does all of its work upfront.
Quicksort is simple to describe: Pick a random pivot element, x, from
a; partition a into the set of elements less than x, the set of elements
equal to x, and the set of elements greater than x; and, finally, recursively
sort the first and third sets in this partition. An example is shown in
Figure 11.3.
Algorithms
<T> void quickSort(T[] a, Comparator<T> c) {
quickSort(a, 0, a.length, c);
}
<T> void quickSort(T[] a, int i, int n, Comparator<T> c) {
if (n <= 1) return;
T x = a[i + rand.nextInt(n)];
int p = i-1, j = i, q = i+n;
// a[i..p]<x, a[p+1..q-1]??x, a[q..i+n-1]>x
while (j < q) {
int comp = compare(a[j], x);
if (comp < 0) { // move to beginning of array
swap(a, j++, ++p);
} else if (comp > 0) {
swap(a, j, --q); // move to end of array
} else {
j++; // keep in the middle
}
}
// a[i..p]<x, a[p+1..q-1]=x, a[q..i+n-1]>x
quickSort(a, i, p-i+1, c);
quickSort(a, q, n-(q-i), c);
}
All of this is done in place, so that instead of making copies of subar-
rays being sorted, the quickSort(a, i, n, c) method only sorts the subarray
a[i], . . . , a[i + n 1]. Initially, this method is invoked with the arguments
−
quickSort(a, 0, a.length, c).
x
13 8 5 2 4 0 6 9 7 3 12 1 10 11
1 8 5 2 4 0 6 7 3 9 12 10 11 13
quickSort(a, 0, 9) quickSort(a, 10, 4)
0 1 2 3 4 5 6 7 8 9 10 11 12 13
0 1 2 3 4 5 6 7 8 9 10 11 12 13
Figure 11.3: An example execution of quickSort(a,0,14,c)
At the heart of the quicksort algorithm is the in-place partitioning al-
gorithm. This algorithm, without using any extra space, swaps elements
in a and computes indices p and q so that
< x if 0 i p
≤ ≤
a[i] = x if p < i < q

 > x if q
≤
i
≤
n
−
1
This partitioning, which is d

one by the while loop in the code, works by
iteratively increasing p and decreasing q while maintaining the first and
last of these conditions. At each step, the element at position j is either
moved to the front, left where it is, or moved to the back. In the first two
cases, j is incremented, while in the last case, j is not incremented since
the new element at position j has not yet been processed.

（中文关键词：快速排序、数组、归并排序）

## 11.1.2 Quicksort (2/3)

Quicksort is very closely related to the random binary search trees
studied in Section 7.1. In fact, if the input to quicksort consists of n
distinct elements, then the quicksort recursion tree is a random binary
search tree. To see this, recall that when constructing a random binary
search tree the first thing we do is pick a random element x and make it
the root of the tree. After this, every element will eventually be compared
to x, with smaller elements going into the left subtree and larger elements
into the right.
In quicksort, we select a random element x and immediately compare
everything to x, putting the smaller elements at the beginning of the array
and larger elements at the end of the array. Quicksort then recursively
sorts the beginning of the array and the end of the array, while the random
binary search tree recursively inserts smaller elements in the left subtree
of the root and larger elements in the right subtree of the root.
The above correspondence between random binary search trees and
quicksort means that we can translate Lemma 7.1 to a statement about
quicksort:
Lemma 11.1. When quicksort is called to sort an array containing the inte-
gers 0, . . . , n 1, the expected number of times element i is compared to a pivot
−
element is at most H + H .
i+1 n i
−
A little summing up of harmonic numbers gives us the following the-
orem about the running time of quicksort:
Theorem 11.2. When quicksort is called to sort an array containing n distinct
elements, the expected number of comparisons performed is at most 2n ln n +
O(n).
Proof. Let T be the number of comparisons performed by quicksort when
sorting n distinct elements. Using Lemma 11.1 and linearity of expecta-
tion, we have:
n 1
−
E[T ] = (H + H )
i+1 n i
−
i=0
(cid:88)
n
= 2 H
i
i=1
(cid:88)
n
2 H
n
≤
i=1
(cid:88)
2n ln n + 2n = 2n ln n + O(n)
≤
Theorem 11.3 describes the case where the elements being sorted are
all distinct. When the input array, a, contains duplicate elements, the
expected running time of quicksort is no worse, and can be even better;
any time a duplicate element x is chosen as a pivot, all occurrences of x get
grouped together and do not take part in either of the two subproblems.
Theorem 11.3. The quickSort(a, c) method runs in O(n log n) expected time
and the expected number of comparisons it performs is at most 2n ln n + O(n).

（中文关键词：快速排序、树、数组、二叉搜索树、递归、排序）

## 11.1.2 Quicksort (3/3)

5
9 6
10 13 8 7
11 12
5 9 6 10 13 8 7 11 12 4 3 2 1 0
0 1 2 3 4 5 6 7 8 11 12 13 14 15
Figure 11.4: A snapshot of the execution of heapSort(a,c). The shaded part of
the array is already sorted. The unshaded part is a BinaryHeap. During the next
iteration, element 5 will be placed into array location 8.

（中文关键词：数组、堆、快速排序）

## 11.1.3 Heap-sort (1/2)

The heap-sort algorithm is another in-place sorting algorithm. Heap-sort
uses the binary heaps discussed in Section 10.1. Recall that the Binary-
Heap data structure represents a heap using a single array. The heap-sort
algorithm converts the input array a into a heap and then repeatedly ex-
tracts the minimum value.
More specifically, a heap stores n elements in an array, a, at array lo-
cations a[0], . . . , a[n 1] with the smallest value stored at the root, a[0].
−
After transforming a into a BinaryHeap, the heap-sort algorithm repeat-
edly swaps a[0] and a[n 1], decrements n, and calls trickleDown(0) so
−
that a[0], . . . , a[n 2] once again are a valid heap representation. When
−
this process ends (because n = 0) the elements of a are stored in decreas-
ing order, so a is reversed to obtain the final sorted order.1 Figure 11.4
shows an example of the execution of heapSort(a, c).
BinaryHeap
<T> void sort(T[] a, Comparator<T> c) {
BinaryHeap<T> h = new BinaryHeap<T>(a, c);
while (h.n > 1) {
1The algorithm could alternatively redefine the compare(x,y) function so that the heap
sort algorithm stores the elements directly in ascending order.
h.swap(--h.n, 0);
h.trickleDown(0);
}
Collections.reverse(Arrays.asList(a));
}
A key subroutine in heap sort is the constructor for turning an un-
sorted array a into a heap. It would be easy to do this in O(n log n) time by
repeatedly calling the BinaryHeap add(x) method, but we can do better by
using a bottom-up algorithm. Recall that, in a binary heap, the children
of a[i] are stored at positions a[2i + 1] and a[2i + 2]. This implies that
the elements a[ n/2 ], . . . , a[n 1] have no children. In other words, each
(cid:98) (cid:99) −
of a[ n/2 ], . . . , a[n 1] is a sub-heap of size 1. Now, working backwards,
(cid:98) (cid:99) −
we can call trickleDown(i) for each i n/2 1, . . . , 0 . This works, be-
∈ {(cid:98) (cid:99) − }
cause by the time we call trickleDown(i), each of the two children of a[i]
are the root of a sub-heap, so calling trickleDown(i) makes a[i] into the
root of its own subheap.

（中文关键词：堆、数组、堆排序、二叉堆、排序）

## 11.1.3 Heap-sort (2/2)

BinaryHeap
BinaryHeap(T[] a, Comparator<T> c) {
this.c = c;
this.a = a;
n = a.length;
for (int i = n/2-1; i >= 0; i--) {
trickleDown(i);
}
}
The interesting thing about this bottom-up strategy is that it is more
efficient than calling add(x) n times. To see this, notice that, for n/2 el-
ements, we do no work at all, for n/4 elements, we call trickleDown(i)
on a subheap rooted at a[i] and whose height is one, for n/8 elements,
we call trickleDown(i) on a subheap whose height is two, and so on.
Since the work done by trickleDown(i) is proportional to the height of
the sub-heap rooted at a[i], this means that the total work done is at most
logn
∞ ∞
O((i 1)n/2i) O(in/2i) = O(n) i/2i = O(2n) = O(n) .
− ≤
i=1 i=1 i=1
(cid:88) (cid:88) (cid:88)
The second-last equality follows by recognizing that the sum
∞i=1
i/2i is
equal, by definition of expected value, to the expected number of times
(cid:80)
we toss a coin up to and including the first time the coin comes up as
heads and applying Lemma 4.2.
The following theorem describes the performance of heapSort(a, c).
Theorem 11.4. The heapSort(a, c) method runs in O(n log n) time and per-
forms at most 2n log n + O(n) comparisons.
Proof. The algorithm runs in three steps: (1) transforming a into a heap,
(2) repeatedly extracting the minimum element from a, and (3) revers-
ing the elements in a. We have just argued that step 1 takes O(n) time
and performs O(n) comparisons. Step 3 takes O(n) time and performs no
comparisons. Step 2 performs n calls to trickleDown(0). The ith such
call operates on a heap of size n i and performs at most 2 log(n i) com-
− −
parisons. Summing this over i gives
n i n i
− −
2 log(n i) 2 log n = 2n log n
− ≤
i=0 i=0
(cid:88) (cid:88)
Adding the number of comparisons performed in each of the three steps
completes the proof.

（中文关键词：堆、堆排序）

## 11.1.4 A Lower-Bound for Comparison-Based Sorting (1/3)

We have now seen three comparison-based sorting algorithms that each
run in O(n log n) time. By now, we should be wondering if faster algo-
rithms exist. The short answer to this question is no. If the only oper-
ations allowed on the elements of a are comparisons, then no algorithm
can avoid doing roughly n log n comparisons. This is not difficult to prove,
but requires a little imagination. Ultimately, it follows from the fact that
log(n!) = log n + log(n 1) + + log(1) = n log n O(n) .
− · · · −
(Proving this fact is left as Exercise 11.11.)
We will start by focusing our attention on deterministic algorithms
like merge-sort and heap-sort and on a particular fixed value of n. Imag-
ine such an algorithm is being used to sort n distinct elements. The key
a[0] ≶ a[1]
< >
a[1] ≶ a[2] a[0] ≶ a[2]
< > < >
a[0] < a[1] < a[2] a[0] ≶ a[2] a[1] < a[0] < a[2] a[1] ≶ a[2]
< > < >
a[0] < a[2] < a[1] a[2] < a[0] < a[1] a[1] < a[2] < a[0] a[2] < a[1] < a[0]
Figure 11.5: A comparison tree for sorting an array a[0],a[1],a[2] of length n = 3.
to proving the lower-bound is to observe that, for a deterministic algo-
rithm with a fixed value of n, the first pair of elements that are compared
is always the same. For example, in heapSort(a, c), when n is even, the
first call to trickleDown(i) is with i = n/2 1 and the first comparison is
−
between elements a[n/2 1] and a[n 1].
− −
Since all input elements are distinct, this first comparison has only
two possible outcomes. The second comparison done by the algorithm
may depend on the outcome of the first comparison. The third compar-
ison may depend on the results of the first two, and so on. In this way,
any deterministic comparison-based sorting algorithm can be viewed as
a rooted binary comparison tree. Each internal node, u, of this tree is la-
belled with a pair of indices u.i and u.j. If a[u.i] < a[u.j] the algorithm
proceeds to the left subtree, otherwise it proceeds to the right subtree.
Each leaf w of this tree is labelled with a permutation w.p[0], . . . , w.p[n 1]
−
of 0, . . . , n 1. This permutation represents the one that is required to sort
−
a if the comparison tree reaches this leaf. That is,
a[w.p[0]] < a[w.p[1]] < < a[w.p[n 1]] .
· · · −
An example of a comparison tree for an array of size n = 3 is shown in
Figure 11.5.

（中文关键词：树、排序、数组、堆、归并排序、堆排序）

## 11.1.4 A Lower-Bound for Comparison-Based Sorting (2/3)

The comparison tree for a sorting algorithm tells us everything about
the algorithm. It tells us exactly the sequence of comparisons that will be
performed for any input array, a, having n distinct elements and it tells
us how the algorithm will reorder a in order to sort it. Consequently, the
comparison tree must have at least n! leaves; if not, then there are two
distinct permutations that lead to the same leaf; therefore, the algorithm
a[0] ≶ a[1]
< >
a[1] ≶ a[2] a[0] ≶ a[2]
< > < >
a[0] < a[1] < a[2] a[0] < a[2] < a[1] a[1] < a[0] < a[2] a[1] < a[2] < a[0]
Figure 11.6: A comparison tree that does not correctly sort every input permuta-
tion.
does not correctly sort at least one of these permutations.
For example, the comparison tree in Figure 11.6 has only 4 < 3! = 6
leaves. Inspecting this tree, we see that the two input arrays 3, 1, 2 and
3, 2, 1 both lead to the rightmost leaf. On the input 3, 1, 2 this leaf correctly
outputs a[1] = 1, a[2] = 2, a[0] = 3. However, on the input 3, 2, 1, this node
incorrectly outputs a[1] = 2, a[2] = 1, a[0] = 3. This discussion leads to the
primary lower-bound for comparison-based algorithms.
Theorem 11.5. For any deterministic comparison-based sorting algorithm
A
and any integer n 1, there exists an input array a of length n such that
≥ A
performs at least log(n!) = n log n O(n) comparisons when sorting a.
−
Proof. By the preceding discussion, the comparison tree defined by
A
must have at least n! leaves. An easy inductive proof shows that any
binary tree with k leaves has a height of at least log k. Therefore, the
comparison tree for has a leaf, w, with a depth of at least log(n!) and
A
there is an input array a that leads to this leaf. The input array a is an
input for which does at least log(n!) comparisons.
A
Theorem 11.5 deals with deterministic algorithms like merge-sort and
heap-sort, but doesn’t tell us anything about randomized algorithms like
quicksort. Could a randomized algorithm beat the log(n!) lower bound
on the number of comparisons? The answer, again, is no. Again, the way
to prove it is to think differently about what a randomized algorithm is.

（中文关键词：树、数组、排序、随机化、二叉树、归并排序）

## 11.1.4 A Lower-Bound for Comparison-Based Sorting (3/3)

In the following discussion, we will assume that our decision trees
have been “cleaned up” in the following way: Any node that can not be
reached by some input array a is removed. This cleaning up implies that
the tree has exactly n! leaves. It has at least n! leaves because, otherwise, it
could not sort correctly. It has at most n! leaves since each of the possible
n! permutation of n distinct elements follows exactly one root to leaf path
in the decision tree.
We can think of a randomized sorting algorithm, , as a determin-
R
istic algorithm that takes two inputs: The input array a that should be
sorted and a long sequence b = b , b , b , . . . , b of random real numbers
1 2 3 m
in the range [0, 1]. The random numbers provide the randomization for
the algorithm. When the algorithm wants to toss a coin or make a ran-
dom choice, it does so by using some element from b. For example, to
compute the index of the first pivot in quicksort, the algorithm could use
the formula nb .
1
(cid:98) (cid:99)
Now, notice that if we fix b to some particular sequence b ˆ then
R
becomes a deterministic sorting algorithm, (b ˆ), that has an associated
R
comparison tree, (b ˆ). Next, notice that if we select a to be a random per-
T
mutation of 1, . . . , n , then this is equivalent to selecting a random leaf, w,
{ }
from the n! leaves of (b ˆ).
T
Exercise 11.13 asks you to prove that, if we select a random leaf from
any binary tree with k leaves, then the expected depth of that leaf is at
least log k. Therefore, the expected number of comparisons performed by
the (deterministic) algorithm (b ˆ) when given an input array containing a
R
random permutation of 1, . . . , n is at least log(n!). Finally, notice that this
{ }
is true for every choice of b ˆ, therefore it holds even for . This completes
R
the proof of the lower-bound for randomized algorithms.
Theorem 11.6. For any integer n 1 and any (deterministic or randomized)
≥
comparison-based sorting algorithm , the expected number of comparisons
A
done by when sorting a random permutation of 1, . . . , n is at least log(n!) =
A { }
n log n O(n).
−

（中文关键词：排序、树、随机化、数组、二叉树、快速排序）
