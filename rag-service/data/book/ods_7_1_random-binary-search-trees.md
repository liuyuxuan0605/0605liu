---
structure: BST
source: book/ods_7_1_random-binary-search-trees.md
chapter: 7. Random Binary Search Trees
section: 7.1
page: 167
kind: textbook
---

# 7.1 Random Binary Search Trees

## Random Binary Search Trees (1/2)

Consider the two binary search trees shown in Figure 7.1, each of which
has n = 15 nodes. The one on the left is a list and the other is a perfectly
balanced binary search tree. The one on the left has a height of n 1 = 14
−
and the one on the right has a height of three.
Imagine how these two trees could have been constructed. The one on
the left occurs if we start with an empty BinarySearchTree and add the
sequence
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 .
(cid:104) (cid:105)
No other sequence of additions will create this tree (as you can prove by
induction on n). On the other hand, the tree on the right can be created
by the sequence
7, 3, 11, 1, 5, 9, 13, 0, 2, 4, 6, 8, 10, 12, 14 .
(cid:104) (cid:105)
Other sequences work as well, including
7, 3, 1, 5, 0, 2, 4, 6, 11, 9, 13, 8, 10, 12, 14 ,
(cid:104) (cid:105)
and
7, 3, 1, 11, 5, 0, 2, 4, 6, 9, 13, 8, 10, 12, 14 .
(cid:104) (cid:105)
0
1
2
7
3
3 11
...
1 5 9 13
14 0 2 4 6 8 10 12 14
Figure 7.1: Two binary search trees containing the integers 0,..., 14.
In fact, there are 21, 964, 800 addition sequences that generate the tree on
the right and only one that generates the tree on the left.
The above example gives some anecdotal evidence that, if we choose a
random permutation of 0, . . . , 14, and add it into a binary search tree, then
we are more likely to get a very balanced tree (the right side of Figure 7.1)
than we are to get a very unbalanced tree (the left side of Figure 7.1).
We can formalize this notion by studying random binary search trees.
A random binary search tree of size n is obtained in the following way: Take
a random permutation, x , . . . , x , of the integers 0, . . . , n 1 and add its
0 n 1
− −
elements, one by one, into a BinarySearchTree. By random permutation
we mean that each of the possible n! permutations (orderings) of 0, . . . , n 1
−
is equally likely, so that the probability of obtaining any particular per-
mutation is 1/n!.
Note that the values 0, . . . , n 1 could be replaced by any ordered set of
−
n elements without changing any of the properties of the random binary
search tree. The element x 0, . . . , n 1 is simply standing in for the
∈ { − }
element of rank x in an ordered set of size n.
Before we can present our main result about random binary search
trees, we must take some time for a short digression to discuss a type of
number that comes up frequently when studying randomized structures.

（中文关键词：树、二叉搜索树、概率、随机化）

## Random Binary Search Trees (2/2)

For a non-negative integer, k, the k-th harmonic number, denoted H , is
k
1 1
f (x) = 1/x
1/2 1/2
1/3 1/3
. .
. .
. .
1/k 1/k
0 1 2 3 ... k 1 2 3 ... k
Figure 7.2: The kth harmonic number Hk = k
i=1
1/i is upper- and lower-bounded
by two integrals. The value of these integrals is given by the area of the shaded
region, while the value of Hk is given by the(cid:80)area of the rectangles.
defined as
H = 1 + 1/2 + 1/3 + + 1/k .
k
· · ·
The harmonic number H has no simple closed form, but it is very closely
k
related to the natural logarithm of k. In particular,
ln k < H ln k + 1 .
k
≤
Readers who have studied calculus might notice that this is because the
k
integral (1/x) dx = ln k. Keeping in mind that an integral can be in-
1
terpreted as the area between a curve and the x-axis, the value of H
(cid:82) k
k
can be lower-bounded by the integral (1/x) dx and upper-bounded by
1
k
1 + (1/x) dx. (See Figure 7.2 for a grap(cid:82)hical explanation.)
1
(cid:82)
Lemma 7.1. In a random binary search tree of size n, the following statements
hold:
1. For any x 0, . . . , n 1 , the expected length of the search path for x is
∈ { − }
H + H O(1).1
x+1 n x
− −
2. For any x ( 1, n) 0, . . . , n 1 , the expected length of the search path
∈ − \ { − }
for x is H + H .
x n x
(cid:100) (cid:101) −(cid:100) (cid:101)
1The expressions x+1 and n x can be interpreted respectively as the number of elements
−
in the tree less than or equal to x and the number of elements in the tree greater than or
equal to x.
We will prove Lemma 7.1 in the next section. For now, consider what
the two parts of Lemma 7.1 tell us. The first part tells us that if we search
for an element in a tree of size n, then the expected length of the search
path is at most 2 ln n+O(1). The second part tells us the same thing about
searching for a value not stored in the tree. When we compare the two
parts of the lemma, we see that it is only slightly faster to search for some-
thing that is in the tree compared to something that is not.

（中文关键词：树、二叉搜索树）

## 7.1.1 Proof of Lemma 7.1 (1/2)

The key observation needed to prove Lemma 7.1 is the following: The
search path for a value x in the open interval ( 1, n) in a random binary
−
search tree, T , contains the node with key i < x if, and only if, in the
random permutation used to create T , i appears before any of i + 1, i +
{
2, . . . , x .
(cid:98) (cid:99)}
To see this, refer to Figure 7.3 and notice that until some value in
i, i + 1, . . . , x is added, the search paths for each value in the open in-
{ (cid:98) (cid:99)}
terval (i 1, x + 1) are identical. (Remember that for two values to have
− (cid:98) (cid:99)
different search paths, there must be some element in the tree that com-
pares differently with them.) Let j be the first element in i, i +1, . . . , x to
{ (cid:98) (cid:99)}
appear in the random permutation. Notice that j is now and will always
be on the search path for x. If j (cid:44) i then the node u containing j is created
j
before the node u that contains i. Later, when i is added, it will be added
i
to the subtree rooted at u .left, since i < j. On the other hand, the search
j
path for x will never visit this subtree because it will proceed to u .right
j
after visiting u .
j
Similarly, for i > x, i appears in the search path for x if and only if
i appears before any of x , x + 1, . . . , i 1 in the random permutation
{(cid:100) (cid:101) (cid:100) (cid:101) − }
used to create T .
Notice that, if we start with a random permutation of 0, . . . , n , then
{ }
the subsequences containing only i, i + 1, . . . , x and x , x + 1, . . . , i 1
{ (cid:98) (cid:99)} {(cid:100) (cid:101) (cid:100) (cid:101) − }
are also random permutations of their respective elements. Each element,
then, in the subsets i, i+1, . . . , x and x , x +1, . . . , i 1 is equally likely
{ (cid:98) (cid:99)} {(cid:100) (cid:101) (cid:100) (cid:101) − }
to appear before any other in its subset in the random permutation used
j
. . . , i, . . . , j 1 j + 1, . . . , x , . . .
− b c
Figure 7.3: The value i < x is on the search path for x if and only if i is the first
element among i,i + 1,..., x added to the tree.
{ (cid:98) (cid:99)}
to create T . So we have
1/( x i + 1) if i < x
Pr i is on the search path for x = (cid:98) (cid:99) − .
{ } 1/(i x + 1) if i > x
(cid:40) − (cid:100) (cid:101)
With this observation, the proof of Lemma 7.1 involves some simple
calculations with harmonic numbers:

（中文关键词：树）

## 7.1.1 Proof of Lemma 7.1 (2/2)

Proof of Lemma 7.1. Let I be the indicator random variable that is equal
i
to one when i appears on the search path for x and zero otherwise. Then
the length of the search path is given by
I
i
i 0,...,n 1 x
∈{ (cid:88)− }\{ }
so, if x 0, . . . , n 1 , the expected length of the search path is given by
∈ { − }
Pr I = 1 1 1 1 1 1 1 1
{ i } x+1 x ··· 3 2 2 3 ··· n x
−
i 0 1 x 1 x x + 1 n 1
··· − ··· −
(a)
Pr I = 1 1 1 1 1 1 1 1 1 1
{ i } b x c +1 b x c ··· 3 2 2 3 ··· n −b x c
i 0 1 x x n 1
··· b c d e ··· −
(b)
Figure 7.4: The probabilities of an element being on the search path for x when
(a) x is an integer and (b) when x is not an integer.
(see Figure 7.4.a)
x 1 n 1 x 1 n 1
− − − −
E I + I = E [I ] + E [I ]
i i i i
 i=0 i=x+1  i=0 i=x+1
 (cid:88) (cid:88) 
=
(cid:88)
x
−
1
1/( x
(cid:88)
i + 1) +
n
−
1
1/(i x + 1)
(cid:98) (cid:99) − − (cid:100) (cid:101)
i=0 i=x+1
(cid:88) (cid:88)
x 1 n 1
− −
= 1/(x i + 1) + 1/(i x + 1)
− −
i=0 i=x+1
(cid:88) (cid:88)
1 1 1
= + + +
2 3 · · · x + 1
1 1 1
+ + + +
2 3 · · · n x
−
= H + H 2 .
x+1 n x
− −
The corresponding calculations for a search value x ( 1, n) 0, . . . , n 1
∈ − \ { − }
are almost identical (see Figure 7.4.b).

## 7.1.2 Summary

The following theorem summarizes the performance of a random binary
search tree:
Theorem 7.1. A random binary search tree can be constructed in O(n log n)
time. In a random binary search tree, the find(x) operation takes O(log n)
expected time.
We should emphasize again that the expectation in Theorem 7.1 is
with respect to the random permutation used to create the random binary
search tree. In particular, it does not depend on a random choice of x; it
is true for every value of x.

（中文关键词：树、二叉搜索树）
