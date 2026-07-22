---
structure: Sorting
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# Sorting 知识点（理论讲解，来源 VisuAlgo）

## Sorting Problem and Sorting Algorithms

Sorting is a very classic problem of reordering items (that can be compared, e.g., integers, floating-point numbers, strings, etc) of an array (or a list) in a certain order (increasing, non-decreasing (increasing or flat), decreasing, non-increasing (decreasing or flat), lexicographical, etc).<\/p>
There are many different sorting algorithms, each has its own advantages and limitations.<\/p>
Sorting is commonly used as the introductory problem in various Computer Science classes to showcase a range of algorithmic ideas.<\/p>
Without loss of generality, we assume that we will sort only
Integers<\/b>, not necessarily distinct, in
non-decreasing order<\/b> in this visualization. Try clicking
Bubble Sort<\/span> for a sample animation of sorting the list of 5 jumbled integers (with duplicate) above.<\/p>

## Motivation - Interesting CS Ideas

Sorting problem has a variety of interesting algorithmic solutions that embody many Computer Science ideas:<\/p>
Comparison<\/u><\/a> versus
non-comparison<\/u><\/a> based strategies,<\/li>
Iterative versus Recursive implementation,<\/li>
Divide-and-Conquer paradigm (e.g.,
Merge Sort<\/u><\/a> or
Quick Sort<\/u><\/a>),<\/li>
Best\/Worst\/Average-case Time Complexity analysis,<\/li>
Randomized Algorithms<\/u><\/a>, etc.<\/li><\/ol>

## Motivation - Applications

When an (integer) array
A<\/b> is sorted, many problems involving
A<\/b> become easy (or easier), please review the
applications<\/u><\/a>, the slower\/harder
unsorted array<\/u><\/a> solutions, and the faster\/easier
sorted array<\/u><\/a> solutions.<\/p>

## Actions

There are two actions that you can do in this visualization.<\/p>

## Define Your Own Input

The first action is about defining
your own<\/b> input, an array\/a list
A<\/b> that is:<\/p>
Totally random,<\/li>
Random but sorted (in non-decreasing or non-increasing order),<\/li>
Random but
nearly<\/b> sorted (in non-decreasing or non-increasing order),<\/li>
Random and contain many duplicates (thus small range of integers), or<\/li>
Defined solely by yourself.<\/li><\/ol>
In Exploration mode, you can experiment with various sorting algorithms provided in this visualization to figure out their best and worst case inputs.<\/p>

## Execute the Selected Sorting Algorithm

The second action is the most important one: Execute the active sorting algorithm by clicking the "Sort" button.<\/p>
Remember that you can switch active algorithm by clicking the
respective abbreviation<\/u><\/a> on the top side of this visualization page.<\/p><\/div>

## Visualisation

View the visualisation\/animation of the chosen sorting algorithm here.<\/p>
Without loss of generality, we only show Integers in this visualization and our objective is to sort them from the initial state into non-decreasing order state. Remember, non-decreasing means mostly ascending (or increasing) order, but because there can be duplicates, there can be flat\/equal line between two adjacent equal integers.<\/p><\/div>

## Common Sorting Algorithms

At the top, you will see the list of commonly taught sorting algorithms in Computer Science classes. To activate each algorithm, select the
abbreviation<\/u><\/a> of respective algorithm name before clicking "Sort".<\/p>
To facilitate more diversity, we randomize the active algorithm upon each page load.<\/p><\/span>
The first six algorithms in this module are
comparison-based<\/b> sorting algorithms while the last two are not. We will discuss this idea
midway through<\/u><\/a> this e-Lecture.<\/p>
The middle three algorithms are
recursive<\/b> sorting algorithms while the rest are usually implemented iteratively.<\/p>

## Abbreviations

To save screen space, we abbreviate algorithm names into three characters each:<\/p>
Comparison-based Sorting Algorithms:
BUB - Bubble Sort,<\/li>
SEL - Selection Sort,<\/li>
INS - Insertion Sort,<\/li>
MER - Merge Sort (recursive implementation),<\/li>
QUI - Quick Sort (recursive implementation),<\/li>
R-Q - Random Quick Sort (recursive implementation).<\/li><\/ol><\/li>
Not Comparison-based Sorting Algorithms:
COU - Counting Sort,<\/li>
RAD - Radix Sort.<\/li><\/ol><\/li><\/ol>

## 3 O(N^2) Comparison-based Sorting Algorithms

We will discuss three comparison-based sorting algorithms in the next few slides:<\/p>
Bubble Sort<\/u><\/a>,<\/li>
Selection Sort<\/u><\/a>,<\/li>
Insertion Sort<\/u><\/a>.<\/li><\/ol>
They are called
comparison-based<\/b> as they compare pairs of elements of the array and decide whether to swap them or not.<\/p>
These three sorting algorithms are the easiest to implement but also not the most efficient, as they run in O(
N<\/b>
2<\/sup>).<\/p>

## Analysis of Algorithms (Basics)

Before we start with the discussion of various sorting algorithms, it may be a good idea to discuss the basics of asymptotic algorithm analysis, so that you can follow the discussions of the various O(
N<\/b>^2), O(
N<\/b> log
N<\/b>), and special O(
N<\/b>) sorting algorithms later.<\/p>
This section can be skipped if you already know this topic.<\/p>

## Mathematical Pre-requisites

You need to already understand\/remember all these:
-. Logarithm and Exponentiation, e.g., log
2<\/sub>(1024) = 10, 2
10<\/sup> = 1024
-. Arithmetic progression, e.g., 1+2+3+4+\u2026+10 = 10*11\/2 = 55
-. Geometric progression, e.g., 1+2+4+8+..+1024 = 1*(1-2
11<\/sup>)\/(1-2) = 2047
-. Linear\/Quadratic\/Cubic function, e.g., f1(x) = x+2, f2(x) = x
2<\/sup>+x-1, f3(x) = x
3<\/sup>+2x
2<\/sup>-x+7
-. Ceiling, Floor, and Absolute function, e.g., ceil(3.1) = 4, floor(3.1) = 3, abs(-7) = 7<\/p>

## What Is It?

Analysis of Algorithm is a process to evaluate rigorously the resources (time and space) needed by an algorithm and represent the result of the evaluation with a (simple) formula.<\/p>
The time\/space requirement of an algorithm is also called the time\/space complexity of the algorithm, respectively.<\/p>
For this module, we focus more on time requirement of various sorting algorithms.<\/p>

## Measuring the Actual Running Time?

We can measure the actual running time of a program by using wall clock time or by inserting timing-measurement code into our program, e.g., see the code shown in
SpeedTest.cpp<\/u><\/a> |
py<\/u><\/a> |
java<\/u><\/a>.<\/p>
However, actual running time is not meaningful when comparing two algorithms as they are possibly coded in different languages, using different data sets, or running on different computers.<\/p>

## Counting # of Operations (1)

Instead of measuring the actual timing, we count the # of operations (arithmetic, assignment, comparison, etc). This is a way to assess its efficiency as an algorithm's execution time is correlated to the # of operations that it requires.<\/p>
See the code shown in
SpeedTest.cpp<\/u><\/a> |
py<\/u><\/a> |
java<\/u><\/a> and the comments (especially on how to get the final value of variable counter).<\/p>
Knowing the (precise) number of operations required by the algorithm, we can state something like this: Algorithm
X<\/b> takes
2n
2<\/sup> + 100n<\/b> operations to solve problem of size
n<\/b>.<\/p>

## Counting # of Operations (2)

If the time
t<\/b> needed for one operation is known, then we can state that algorithm
X<\/b> takes
(2n
2<\/sup> + 100n)t<\/b> time units to solve problem of size
n<\/b>.<\/p>
However, time
t<\/b> is dependent on the factors mentioned earlier, e.g., different languages, compilers and computers, the complexity of the operation itself (addition\/subtraction is easier\/faster to compute than multiplication\/division), etc.<\/p>
Therefore, instead of tying the analysis to actual time
t<\/b>, we can state that algorithm
X<\/b> takes time that is
proportional to 2n
2<\/sup> + 100n<\/b> to solving problem of size
n<\/b>.<\/p>

## Asymptotic Analysis

Asymptotic<\/u><\/a> analysis is an analysis of algorithms that focuses on analyzing problems of
large input size n<\/b>, considers
only the leading term<\/b> of the formula, and
ignores the coefficient<\/b> of the leading term.<\/p>
We choose the leading term because the lower order terms contribute lesser to the overall cost as the input grows larger, e.g., for f(n) = 2n
2<\/sup> + 100n, we have:
f(1000) = 2*1000
2<\/sup> + 100*1000 = 2.1M, vs
f(100000) = 2*100000
2<\/sup> + 100*100000 = 20010M.
(notice that the lower order term 100n has lesser contribution).<\/p>

## Ignoring Coefficient of the Leading Term

Suppose two algorithms have 2n
2<\/sup> and 30n
2<\/sup> as the leading terms, respectively.<\/p>
Although actual time will be different due to the different constants, the growth rates of the running time are the same.<\/p>
Compared with another algorithm with leading term of n
3<\/sup>, the difference in growth rate is a much more dominating factor.<\/p>
Hence, we can drop the coefficient of leading term when studying algorithm complexity.<\/p>

## Upper Bound: The Big-O Notation

If algorithm A requires time proportional to
f(n)<\/b>, we say that algorithm A is of the order of f(n).<\/p>
We write that algorithm A has time complexity of
O(f(n))<\/b>, where
f(n)<\/b> is the growth rate function for algorithm A.<\/p>

## Big-O Notation (Mathematics)

Mathematically, an algorithm A is of O(
f(n)<\/b>) if there exist a constant
k<\/b> and a positive integer
n0<\/b> such that algorithm A requires no more than
k*f(n)<\/b> time units to solve a problem of size
n \u2265 n0<\/b>, i.e., when the problem size is larger than
n0<\/b>, then algorithm A is (always) bounded from above by this simple formula
k*f(n)<\/b>.<\/p>
<\/center>
Note that:
n0<\/b> and
k<\/b> are not unique and there can be many possible valid
f(n)<\/b>.<\/p>

## Growth Terms

In asymptotic analysis, a formula can be simplified to a single term with coefficient 1.<\/p>
Such a term is called a growth term (rate of growth, order of growth, order of magnitude).<\/p>
The most common growth terms can be ordered from fastest to slowest as follows:
O(
1<\/b>)\/constant time < O(log
n<\/b>)\/logarithmic time < O(
n<\/b>)\/linear time <
O(
n<\/b> log
n<\/b>)\/quasilinear time < O(
n<\/b>
2<\/sup>)\/quadratic time < O(
n<\/b>
3<\/sup>)\/cubic time <
O(2
n<\/b><\/sup>)\/exponential time < O(
n<\/b>!)\/also-exponential time < ∞ (e.g., an infinite loop).<\/p>
Note that a few other common time complexities are not shown (also see the visualization in the next slide).<\/p>

## Growth Terms (Visualized\/Compared)

We will see three different growth rates O(
n
2<\/sup><\/b>), O(
n log n<\/b>), and O(
n<\/b>) throughout the remainder of this sorting module.<\/p>

## Bubble Sort

Given an array of
N<\/b> elements, Bubble Sort will:<\/p>
Compare<\/b> a pair of adjacent items (a, b),<\/li>
Swap that pair if the items are out of order (in this case, when a > b),<\/li>
Repeat Step 1 and 2 until we reach the end of array
(the last pair is the (
N<\/b>-2)-th and (
N<\/b>-1)-th items as we use 0-based indexing),<\/li>
By now, the largest item will be at the last position.
We then reduce
N<\/b> by 1 and repeat Step 1 until we have
N = 1<\/b>.<\/li><\/ol>
Without further ado, let's try
Bubble Sort<\/span> on the small example array [29, 10, 14, 37, 14].<\/p>
You should see a 'bubble-like' animation if you imagine the larger items 'bubble up' (actually 'float to the right side of the array').<\/p><\/span>

## Bubble Sort, Pseudocode & Analysis

method bubbleSort(array A, integer N) \/\/ the standard version
for each R from N-1 down to 1 \/\/ repeat for N-1 iterations
for each index i in [0..R-1] \/\/ the 'unsorted region', O(N)
if A[i] > A[i+1] \/\/ these two are not in non-decreasing order
swap(a[i], a[i+1]) \/\/ swap them in O(1)<\/pre>
Comparison and swap require time that is bounded by a constant, let's call it
c<\/b>. Then, there are two nested loops in (the standard) Bubble Sort. The outer loop runs for exactly
N-1<\/b> iterations. But the inner loop runs get shorter and shorter:<\/p>
When R=
N<\/b>-1, (
N<\/b>\u22121) iterations (of comparisons and possibly swaps),<\/li>
When R=
N<\/b>-2, (
N<\/b>\u22122) iterations,
...,<\/li>
When R=1, 1 iteration (then done).<\/li><\/ol>
Thus, the total number of iterations = (
N<\/b>\u22121)+(
N<\/b>\u22122)+...+1 =
N<\/b>*(
N<\/b>\u22121)\/2 (
derivation<\/u><\/a>).<\/p>
Total time = c*
N<\/b>*(
N<\/b>\u22121)\/2 = O(
N<\/b>^2).<\/p>
See the code shown in
SortingDemo.cpp<\/u><\/a> |
py<\/u><\/a> |
java<\/u><\/a>.<\/p>

## Bubble Sort: Early Termination

Bubble Sort is actually inefficient with its
O(N^2)<\/b> time complexity. Imagine that we have
N<\/b> = 10
5<\/sup> numbers. Even if our computer is super fast and can compute 10
8<\/sup> operations in 1 second, Bubble Sort will need about 100 seconds to complete.<\/p>
However, it can be terminated early, e.g., on the small sorted ascending example shown above [3, 6, 11, 25, 39],
Bubble Sort<\/span> can terminates in O(
N<\/b>) time.<\/p>
The improvement idea is simple: If we go through the inner loop with
no swapping<\/b> at all, it means that the array is
already sorted<\/b> and we can stop Bubble Sort at that point.<\/p>
Discussion: Although it makes Bubble Sort runs faster in general cases, this improvement idea does not change
O(N^2)<\/b> time complexity of Bubble Sort... Why?<\/p>

## The Answer

Try
Bubble Sort Extreme Case<\/span> where we run Bubble Sort on a small reverse sorted input array. We will encounter the O(
N<\/b>
2<\/sup>) time complexity again.<\/p>
Note that running Bubble Sort on a `nearly sorted' array like [2,3,4,5,6,...,1] will also make this Optimized Bubble Sort still runs in O(
N<\/b>
2<\/sup>).<\/p>

## Selection Sort

Given an array of
N<\/b> items and
L<\/b> = 0, Selection Sort will:<\/p>
Find the position
X<\/b> of the smallest item in the range of [
L<\/b>...
N<\/b>\u22121],<\/li>
Swap
X<\/b>-th item with the
L<\/b>-th item,<\/li>
Increase the lower-bound
L<\/b> by 1 and repeat Step 1 until
L<\/b> =
N<\/b>-2.<\/li><\/ol>
Let's try
Selection Sort<\/span> on the same small example array [29, 10, 14, 37, 13].<\/p>
Without loss of generality, we can also implement Selection Sort in reverse:
Find the position of the largest item
Y<\/b> and swap it with the last item.<\/p>

## Selection Sort, Pseudocode & Analysis

method selectionSort(array A[], integer N)
for each L in [0..N-2] \/\/ O(
N<\/b>)
let X be the index of the minimum element in A[L..N-1] \/\/ O(
N<\/b>)
swap(A[X], A[L]) \/\/ O(1), X may be equal to L (no actual swap)<\/pre>
Total: O(
N<\/b>
2<\/sup>) \u2014 To be precise, it is similar to
Bubble Sort analysis<\/u><\/a>.<\/p>
See the code shown in
SortingDemo.cpp<\/u><\/a> |
py<\/u><\/a> |
java<\/u><\/a>.<\/p>

## Mini Quiz

Quiz:
How many (real) swaps are required to sort [29, 10, 14, 37, 13] by Selection Sort?<\/b><\/p>
3
4
1
2
<\/form>
Submit<\/button>
<\/span><\/span>

## Insertion Sort

Insertion sort is similar to how most people arrange a hand of poker cards.
<\/p>
Start with one card in your hand,<\/li>
Pick the next card and insert it into its proper sorted order,<\/li>
Repeat previous step for all cards.<\/li><\/ol>
Let's try
Insertion Sort<\/span> on the small example array [6, 2, 10, 7].<\/p>

## Insertion Sort, Pseudocode and Analysis 1

method insertionSort(array A[], integer N)
for i in [1..N-1] \/\/ O(N)
let X be A[i] \/\/ X is the next item to be inserted into A[0..i-1]
for j from i-1 down to 0 \/\/ this loop can be fast or slow
if A[j] > X
A[j+1] = A[j] \/\/ make a place for X
else
break
A[j+1] = X \/\/ insert X at index j+1<\/pre>
See the code shown in
SortingDemo.cpp<\/u><\/a> |
py<\/u><\/a> |
java<\/u><\/a>.<\/p>

## Insertion Sort: Analysis 2

The outer loop executes
N<\/b>\u22121 times, that's quite clear.<\/p>
But the number of times the inner-loop is executed depends on the input:<\/p>
In best-case scenario, the array is already sorted and (a[j] > X) is always false
So no shifting of data is necessary and the inner loop runs in O(
1<\/b>),<\/li>
In worst-case scenario, the array is reverse sorted and (a[j] > X) is always true
Insertion always occur at the front of the array and the inner loop runs in O(
N<\/b>).<\/li><\/ol>
Thus, the best-case time is O(
N ×  1<\/b>) = O(
N<\/b>) and the worst-case time is O(
N × N<\/b>) = O(
N<\/b>
2<\/sup>).<\/p>

## Mini Quiz

Quiz:
What is the complexity of Insertion Sort on any input array?<\/b><\/p>
O(N)
O(1)
O(N^2)
O(N log N)
<\/form>
Submit<\/button>
<\/span>
Ask your instructor if you are not clear on this or read similar remarks on
this slide<\/u><\/a>.<\/p><\/span>

## 2.5 O(N log N) Comparison-based Sorting

We will discuss two (and a half) comparison-based sorting algorithms soon:<\/p>
Merge Sort<\/u><\/a>,<\/li>
Quick Sort<\/u><\/a> and its
Randomized version<\/u><\/a> (which only has one change).<\/li><\/ol>
These sorting algorithms are usually implemented recursively, use Divide and Conquer problem solving paradigm, and run in O(
N<\/b> log
N<\/b>) time for Merge Sort and O(
N<\/b> log
N<\/b>) time
in expectation<\/i> for Randomized Quick Sort.<\/p>
PS: The non-randomized version of Quick Sort runs in O(
N
2<\/sup><\/b>) though.<\/p>

## Merge Sort

Given an array of
N<\/b> items, Merge Sort will:<\/p>
Merge each pair of individual element (which is by default, sorted) into sorted arrays of 2 elements,<\/li>
Merge each pair of sorted arrays of 2 elements into sorted arrays of 4 elements,
Repeat the process...,<\/li>
Final step: Merge 2 sorted arrays of
N<\/b>\/2 elements (for simplicity of this discussion, we assume that
N<\/b> is even) to obtain a fully sorted array of
N<\/b> elements.<\/li><\/ol>
This is just the general idea and we need a few more details before we can discuss the true form of Merge Sort.<\/p>

## Important Subroutine, O(N) Merge

We will dissect this Merge Sort algorithm by first discussing its most important sub-routine: The O(
N<\/b>)
merge<\/samp>.<\/p>
Given two sorted array, A and B, of size
N
1<\/sub><\/b> and
N
2<\/sub><\/b>, we can efficiently merge them into one larger combined sorted array of size
N<\/b> =
N
1<\/sub><\/b>+
N
2<\/sub><\/b>, in O(
N<\/b>) time.<\/p>
This is achieved by simply comparing the front of the two arrays and take the smaller of the two at all times. However, this simple but fast O(
N<\/b>)
merge<\/samp> sub-routine will need additional array to do this merging correctly.<\/p>
