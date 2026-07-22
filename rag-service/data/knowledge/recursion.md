---
structure: Recursion
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# Recursion 知识点（理论讲解，来源 VisuAlgo）

## Visualization

This visualization can visualize the recursion tree of any recursive algorithm or the recursion tree of a Divide and Conquer (D&C) algorithm recurrence (e.g., Master Theorem) that we can legally write in JavaScript.<\/p>
We can also visualize the Directed Acyclic Graph (DAG) of a Dynamic Programming (DP) algorithm and compare the dramatic search-space difference of a DP problem versus when its overlapping sub-problems are naively recomputed, e.g.,
the exponential \u03a9(2
n\/2<\/sup>) recursive Fibonacci versus its O(n) DP version<\/u><\/a>.<\/p>
On some problems, we can also visualize the difference between what a Complete Search (recursive backtracking) that explores the entire search space, a greedy algorithm (that greedily picks one branch each time), versus Dynamic Programming look like in the same recursion tree, e.g.,
Coin-Change<\/u><\/a> of v = 7 cents with 4 coins {4, 3, 1, 5} cents.<\/p>
Most recursion trees require large drawing space, therefore view this visualization page on a large screen. For obvious reason, we cannot really visualize very big trees\/DAGs. Therefore, we call our recursion with small parameter(s).<\/p>

## Recursion Tree

This is the Recursion Tree and Recursion Directed Acyclic Graph (DAG) visualization area. The Recursion Tree\/DAG are drawn\/animated as per how a real computer program that implements this recursion works, i.e., "depth-first".<\/p>
The recursion starts from the initial state that is colored
dark brown<\/span>. The current parameter value is shown inside each vertex (comma-separated for recursion with two or more parameters). Active vertices will be colored
orange<\/span>. Vertices that are no longer calling any other recursive problem (the base cases) will be colored
green<\/span>. Vertices (subproblems) that are repeated will be colored
lightblue<\/span> for the second occurrence onwards. The return value of each recursive call is written as a
red<\/span> text below the vertex. This visualization is generic for any recursion that you can legally write in JavaScript.<\/p>
Note that due to combinatorial explosion, it will be very hard to visualize the Recursion Tree for large instances.<\/p>

## Recursion DAG

For the Recursion DAG, it will also be very hard to minimize the number of edge crossings in the event of overlapping subproblems. However, we try our best to give a custom DAG drawing layout for certain DP problems to improve the presentation.<\/p>
For example, we currently show the recursion DAG of the computation of the n-th Fibonacci number. We layout the vertices from leftmost (the two
green-colored base cases
n = 0<\/samp> and
n = 1<\/samp><\/span>) to rightmost (
the initial
n<\/samp><\/span>). Ideally this is shown as a flat 1-D (memoization) array. However as VisuAlgo does not have curvy edge yet, we decided to put odd-numbered vertices slightly below the even-numbered vertices to get around the overlapping edges issue. To compute
fib(n)<\/samp>, we only need to know the result of two immediate results:
fib(n-1) + fib(n-2)<\/samp> that is depicted as the two arrows from vertex
n<\/samp> to vertices
n-1<\/samp> and
n-2<\/samp>. The results of the summation, i.e., the values of each
fib(n)<\/samp>, are displayed as
red text below the vertices<\/span>. As there is no repeated subproblem computation, there is no
lightblue<\/span> vertex at all in this recursion DAG (such vertices\/states will have more than one incoming arrows instead).<\/p>

## Example Recursion - One Subproblem

Select one of the example recursive algorithms in the drop-down list or write our own recursive code \u2014 in JavaScript. The final recursion Tree \/ DAG is immediately displayed. Note that this visualization can run
any<\/i> JavaScript code, including malicious code, so please be careful (it will only affect your own web browser, don't worry).<\/p>
Click the 'Run' button at the top right corner of the action box to start the step-by-step visualization of the recursive function after you have selected (or written) a valid JavaScript code!<\/p>
In the next sub-sections, we start with example recursive algorithms with just one sub-problem, i.e., not branching. For these one-subproblem examples, their recursion trees and recursion DAGs are 100% identical (they looked like Singly Linked Lists from the root (initial call) to the leaf (base case)). As there is no overlapping subproblem for the examples in this category, you will not see any
lightblue<\/span>-colored vertex and only one
green<\/span>-colored vertex (the base case). The default orientation for recursion Tree is top-right-to-bottom-left whereas the default orientation for recursion DAG is right-to-left.<\/p>

## Factorial Numbers

The Factorial Numbers example computes the factorial of an integer
n<\/samp>.<\/p>
f(n) = 1 (if n == 0);
f(n) = n*f(n-1) otherwise<\/samp>
It is one of the simplest (tail) recursive function that can be easily rewritten into an iterative version. It's time complexity is also simply Θ(
n<\/samp>).<\/p>
The value of Factorial
f(n)<\/samp> grows very fast, thus try only the small integers
n<\/samp> \u2208 [0..10]
(we randomize the value of the
initial
n<\/samp><\/span> between this range).<\/p>

## Binary Search

The Binary Search example finds the index of
a2<\/samp> in a sorted array
a1[a..b]<\/samp>. We start binary search from the initial search space of
a=0,b=a1.length-1<\/samp> (the entire array
a1<\/samp>, with
n = (a1.length-1) - 0 + 1 = a1.length<\/samp>)<\/span>.<\/p>
f(a,b) = -1 (if a > b);
let mid = floor((a+b)\/2);
f(a,b) = mid (if a2 = a1[mid]);
f(a,b) = f(a,mid-1) (if a2 < a1[mid]);
f(a,b) = f(mid+1,b) (if a2 > a1[mid]);<\/samp>
Only one of the two possible branches will be executed each time, resulting in a recursion tree = recursion DAG situation. The time complexity if Θ(log
n<\/samp>) as we keep halving the search space each time. The worst-case happens when
a2<\/samp> is not found in sorted array
a1<\/samp>.<\/p>
In this visualization, we randomize the content of sorted array
a1<\/samp> and the value to be searched
a2<\/samp>.<\/p>
TBC: In the near future, we will draw the entire Θ(
n<\/samp>) search space (both left and right branches at each vertex) and highlight the efficient Θ(log
n<\/samp>) path taken by Binary Search on this search space. This is like seeing the animation of
Search(v) function of a (balanced) Binary Search Tree<\/u><\/a>.<\/p>

## Modulo Power

The Modulo Power example computes the
a1^p % a2<\/samp> in efficient way.<\/p>
f(p) = 1 (if p == 0);
f(p) = f(floor(p\/2))^2 % a2 (if p is even)
f(p) = f(floor(p\/2))^2 * a1 % a2 (if p is odd)<\/samp>
This Divide & Conquer (D&C) algorithm runs in Θ(log
p<\/samp>).<\/p>
In this visualization, we randomize the values of
a1<\/samp> (the base, a small value ∈ [2..4]),
a2<\/samp> (the modulo, a prime ∈ [7, 97, 997, 9973]), and
power
p<\/samp> (we want to raise
a1<\/samp> to its
p<\/samp>-th power, modulo
a2<\/samp>. Due to its low time complexity, it is OK to try
very large
0 \u2264 p \u2264 256<\/samp><\/span>.<\/p>
TBC: In the near future, we may draw the comparison between this efficient D&C modulo power algorithm with the naive version that multiply
a1<\/samp>
p<\/samp><\/span> times that runs in Θ(
p<\/samp><\/span>).<\/p>

## Greatest Common Divisor (GCD)

The Greatest Common Divisor (GCD) example computes the GCD of two integers
a<\/samp> and
b<\/samp>.<\/p>
f(a, b) = a (if b == 0);
f(a, b) = f(b, a%b) otherwise<\/samp>
This is the classic Euclid's algorithm that runs in O(log
n<\/samp>) where
n = min(a, b)<\/samp> \u2014 depending of the details,
n = max(a, b)<\/samp> or
n = a+b<\/samp> are also possible.<\/p>
Euclid's algorithm is an example of Divide & Conquer (D&C) algorithm.<\/p>
Due to its low time complexity, it should be OK to try
0 \u2264 a, b \u2264 99<\/samp><\/span>.
(we randomize the values of
a<\/samp> and
b<\/samp> between this range and set
a \u2265 b<\/samp>).
Note that if we put
a < b<\/samp>, technically the first recursive step will swap
a<\/samp> and
b<\/samp>.<\/p>
Do explore various possible combinations of
a<\/samp> and
b<\/samp> and notice on what values
f(a, b)<\/samp> terminates very quickly in 1 step (
b = 0<\/samp>), 2 steps (
b = gcd(a, b)<\/samp>), or the maximum number of steps (try
this sequence<\/u><\/a>) \u2014 to show the lowerbound \u03a9(log
n<\/samp>).<\/p>

## Max Range Sum

The Max Range Sum example computes the value of the subarray with the maximum total sum inside the given (global) array
a1<\/samp> with
n = a1.length<\/samp> integers (the first textbox below the code editor textbox). The value of
a1<\/samp> can be positive integers, zeroes, or negative integers (without negative integer, the answer will obviously the sum of the entire integers in
a1<\/samp>).<\/p>
Formally, let's define
RSQ(i, j) = a1[i] + a1[i+1] + ... + a1[j]<\/samp>, where
0 \u2264 i \u2264 j \u2264 n-1<\/samp> (RSQ stands for Range Sum Query). Max Range Sum problem seeks to find the optimal
i<\/samp> and
j<\/samp> such that
RSQ(i, j)<\/samp> is the maximum.<\/p>
f(i) = max(ai[0], 0) (if i == 0, as ai[0] can be negative);
f(i) = max(f(i-1) + ai[i], 0) otherwise<\/samp>
We call
f(n-1)<\/samp><\/span>. The largest value of
f(i)<\/samp> is the answer.<\/p>
This is the classic
Kadane's algorithm<\/u><\/a> that runs in O(
n<\/samp>).<\/p>

## Catalan Numbers

The Catalan example computes the
n<\/b>-th
Catalan number<\/u><\/a> recursively.<\/p>
f(n) = 1 (if n == 0);
f(n) = f(n-1)*2*n*(2*n-1)\/(n+1)\/n; otherwise<\/samp>
This explanation is a stub that will be expanded later.<\/p>

## Example Recursion - Two Subproblems

In the next sub-sections, we will see example recursive algorithms that have exactly two sub-problems, i.e., branching. The sizes of the subproblems can be identical or vary. For these two sub-problems examples, their recursion trees will usually be much bigger that their recursion DAGs (especially if there are (many) overlapping sub-problems, indicated with the
lightblue<\/span> vertices on the recursion tree drawing).<\/p>
Currently shown on screen is the recursion tree of a Fibonacci recurrence.<\/p>

## Fibonacci Numbers (Tree)

The Fibonacci Numbers example computes the
n<\/samp>-th Fibonacci number.<\/p>
f(n) = n (if n <= 1); \/\/ i.e., 0 if n == 0 or 1 if n == 1
f(n) = f(n-1) + f(n-2) otherwise<\/samp>
Unlike
Factorial<\/u><\/a> example, this time each recursive step recurses to two other smaller sub-problems (if we call f(n-1) first before f(n-2), then the left side of the recursion tree will be taller than the right side \u2014 try swapping the two sub-problems).<\/p>
The value of Fibonacci
f(n)<\/samp><\/span> grows very fast and its recursion tree — if implemented verbatim as defined above — also grows exponentially, i.e., at least \u03a9(2
n\/2<\/sup>), thus try only the small initial values of
n \u2264 7<\/samp><\/span> (to avoid crashing your web browser).<\/p>
Fibonacci recursion tree is frequently used to showcase the basic idea of recursion, its inefficiency (due to the many
overlapping subproblems<\/span>), and the linkage to Dynamic Programming (DP) topic.<\/p>

## Fibonacci Numbers (DAG)

The recursion DAG (shown in the background) of Fibonacci computation only contains O(
n<\/samp>) vertices and thus can go to a larger
n<\/samp> \u2264 30<\/span> (so it still looks nice in this visualization; in practice
n<\/samp><\/span> can go to millions with this DP solution).<\/p>
Most of the time, the Fibonacci computation is written in iterative fashion after one understands the concept of DP.<\/p>
It is probably rare to think this way, but this visualization shows that the computation of Fibonacci
f(n)<\/samp><\/span> is basically counting the number of paths from
n<\/samp><\/span> to vertex
1<\/samp>.<\/p>

## Binomial Coefficient C(n, k) (Tree)

The C(n, k) example computes the
binomial coefficient<\/u><\/a>
C(n, k)<\/samp>.<\/p>
f(n, k) = 1 (if k == 0); \/\/ 1 way to take nothing out of n items
f(n, k) = 1 (if k == n); \/\/ 1 way to take everything out of n items
f(n, k) = f(n-1, k-1) + f(n-1, k) \/\/ take the last item or skip it<\/samp>
The recursion tree of
C(n, k)<\/samp><\/span> grows very fast, with the largest tree when
k = n\/2<\/samp>, smaller trees when
k<\/samp> is close to
0<\/samp> or
n<\/samp> (a few path(s) with short leafs), and smallest trees when
k<\/samp> is
0<\/samp> or
n<\/samp> (only one vertex).<\/p>

## Binomial Coefficient C(n, k) (DAG)

The recursion DAG of
C(n, k)<\/samp><\/span> is basically an inverted
Pascal's Triangle<\/u><\/a>. It only contains O(
(n\/2)*(n\/2)<\/samp>) = O(
n^2\/4<\/samp>) vertices at most (when
k = n\/2<\/samp>) although in practice we probably just use a DP\/memo table of size O(
n^2<\/samp>). Thus we can go to a larger
n<\/samp> \u2264 15<\/span> (so it still looks nice in this visualization) and
k∈[0..n]<\/samp><\/span>, including when
k≈n\/2<\/samp><\/span>.<\/p>
TBC: In the near future, we may draw a dummy vertex (0, 0) ---
C(n, k)<\/samp><\/span> will not actually reach it unless started from
C(0, 0)<\/samp><\/span> with return value of 1 to complete the inverted Pascal's Triangle visualization.<\/p>

## 0-1 Knapsack (Tree)

The 0-1 Knapsack example solves the
0\/1 Knapsack Problem<\/u><\/a>: What is the maximum value that we can get, given a knapsack that can hold a maximum weight of
w<\/samp>, where the value of the
i<\/samp>-th item is
a1[i]<\/samp>, the weight of the i-th item is
a2[i]<\/samp>?<\/p>
0-1 Knapsack has a classic DP recurrence
f(i, w)<\/samp> which we call using
f(n-1, max-w)<\/samp> where
n = a1.length<\/samp><\/span>.<\/p>
f(i, w) = f(i-1, w); \/\/ ignore item i (always possible)
f(i, w) = a1[i] + f(i-1, w-a2[i]); \/\/ take item i (if a2[i]≤w)
f(<0, w) = 0; \/\/ all items have been considered
f(i, 0) = 0; \/\/ cannot carry anything else<\/samp>
The recursion tree of this DP recurrence has a few (like currently shown on screen) to many (e.g., try all items having the same weight, i.e., ones)
overlapping sub-problems<\/span>.<\/p>

## 0-1 Knapsack (DAG)

The recursion DAG of 0-1 Knapsack only contains O(
n * max-w<\/samp>) vertices. Thus we can go to a
larger
n<\/samp> \u2264 7 and
max-w<\/samp> \u2264 15<\/span> (so it still looks nice in this visualization).<\/p>
This DP recurrence basically tries to find the longest (weighted) path in this implicit DAG and has time complexity of O(
n * max-w<\/samp>).<\/p>
If the weights of each item in
a2<\/samp> vary a lot, the recursion DAG will look sparse. Try setting
a2=[1,2,...,2^i]<\/samp> for a denser recursion DAG (but no overlap) or
a2=[1,1,...,1]<\/samp> (lots of overlap).<\/p>

## Example Recursion - Many Subproblems

In the next sub-sections, we will see example recursive algorithms that have many sub-problems (1, 2, 3, ..., a certain limit). For many of these examples, the sizes of their Recursion Trees are exponential and we will really need to use Dynamic Programming to compute its Recursion DAGs instead.<\/p>

## Longest Inc Subseq (LIS) (DAG)

The Longest Increasing Subsequence example solves the
Longest Increasing Subsequence<\/u><\/a> problem: Given an array a1, how long is the Longest Increasing Subsequnce of the array?<\/p>
The recursion DAG of the default example (not randomized) is as follows: Vertex
j \u2208 [0..i-1]<\/samp> is laid out horizontally (along the x-axis from left\/vertex 0 to right\/vertex
i-1<\/samp>), then placed vertically (along the y-axis according to the value of
a1[j]<\/samp>). We draw an edge between two indices
j<\/samp> and
k<\/samp> if
a1[j] < a1[k]<\/samp> (with all vertices having hidden edge to the dummy max(a1)+1 value at the top-right cell so that all LIS ends at this dummy vertex and we can start the recursion with
f(i)<\/samp> where
i = a1.length-1<\/samp><\/span>). Then this LIS problem can be visualized as finding the longest path in this (implicit) recursion DAG.<\/p>
As there are
|V| = n<\/b> vertices and
|E| = O(n^2)<\/b> edges (use sorted ascending test case, e.g., {1,2,4,8,16,...} to have nice visualization), the overall time complexity to solve LIS using DP is O(
n^2<\/b>). Since early 2000s, we should use the faster O(
n log k<\/b>) greedy+binary search solution for LIS (not explained in this slide).<\/p>

## Coin Change (Tree)

The Coin Change example solves the
Coin Change problem<\/u><\/a>: Given a list of coin values in a1, what is the minimum number of coins needed to get the value v?<\/p>
The recursion tree of the default example (not randomized) has
v = 7<\/span> cents and 4 coins that are specifically selected to be {4, 3, 1, 5}. What is shown on-screen is the entire recursion tree of Coin-Change recursive function.<\/p>
A typical greedy algorithm for Coin-Change that always take the largest coin value that does not exceed current value v will be trapped into taking the rightmost branch: 7 cents (take 5 cents coin) → 2 cents (take 1 cent coin) → 1 cent (take another 1 cent coin) → 0 (total 3 coins).<\/p>
DP algorithm that explores this recursion tree (but avoiding repeated computations on the
lightblue<\/span> vertices will find the lefmost branch: 7 cents (take 4 cents coin) → 3 cents (take 3 cents coin) → 0 (total 2 coins). Alternative solution: 7 → 4 → 0 (also 2 coins).<\/p>
