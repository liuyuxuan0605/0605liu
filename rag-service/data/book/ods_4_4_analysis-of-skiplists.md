---
structure: 
source: book/ods_4_4_analysis-of-skiplists.md
chapter: 4. Skiplists
section: 4.4
page: 112
kind: textbook
---

# 4.4 Analysis of Skiplists

## Analysis of Skiplists (1/3)

In this section, we analyze the expected height, size, and length of the
search path in a skiplist. This section requires a background in basic
probability. Several proofs are based on the following basic observation
about coin tosses.
Lemma 4.2. Let T be the number of times a fair coin is tossed up to and
including the first time the coin comes up heads. Then E[T ] = 2.
Proof. Suppose we stop tossing the coin the first time it comes up heads.
Define the indicator variable
0 if the coin is tossed less than i times
I =
i 1 if the coin is tossed i or more times
(cid:40)
Note that I = 1 if and only if the first i 1 coin tosses are tails, so E[I ] =
i i
−
Pr I = 1 = 1/2i 1. Observe that T , the total number of coin tosses, can
i −
{ }
be written as T = ∞i=1 I i . Therefore,
(cid:80)
∞
E[T ] = E I
i
 
i=1
=
∞
 (cid:88)
E [I ]

i
i=1
(cid:88)
= ∞ 1/2i
−
1
i=1
(cid:88)
= 1 + 1/2 + 1/4 + 1/8 +
· · ·
= 2 .
The next two lemmata tell us that skiplists have linear size:
Lemma 4.3. The expected number of nodes in a skiplist containing n ele-
ments, not including occurrences of the sentinel, is 2n.
Proof. The probability that any particular element, x, is included in list
L is 1/2r, so the expected number of nodes in L is n/2r.2 Therefore, the
r r
total expected number of nodes in all lists is
∞ n/2r = n(1 + 1/2 + 1/4 + 1/8 + ) = 2n .
· · ·
r=0
(cid:88)
Lemma 4.4. The expected height of a skiplist containing n elements is at most
log n + 2.
Proof. For each r 1, 2, 3, . . . , , define the indicator random variable
∈ { ∞}
0 if L is empty
I = r
r 1 if L is non-empty
r
(cid:40)
2See Section 1.3.4 to see how this is derived using indicator variables and linearity of
expectation.
The height, h, of the skiplist is then given by
∞
h = I .
r
i=1
(cid:88)
Note that I is never more than the length, L , of L , so
r r r
| |
E[I ] E[ L ] = n/2r .
r r
≤ | |
Therefore, we have
∞
E[h] = E I
r
r=1 
=
∞
 (cid:88)
E[I ]

r
r=1
(cid:88)
logn
(cid:98) (cid:99) ∞
= E[I ] + E[I ]
r r
r=1 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
(cid:98) (cid:99) 1 + ∞ n/2r
≤
r=1 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
log n + ∞ 1/2r
≤
r=0
(cid:88)
= log n + 2 .
Lemma 4.5. The expected number of nodes in a skiplist containing n ele-
ments, including all occurrences of the sentinel, is 2n + O(log n).

（中文关键词：跳表、概率）

## Analysis of Skiplists (2/3)

Proof. By Lemma 4.3, the expected number of nodes, not including the
sentinel, is 2n. The number of occurrences of the sentinel is equal to
the height, h, of the skiplist so, by Lemma 4.4 the expected number of
occurrences of the sentinel is at most log n + 2 = O(log n).
Lemma 4.6. The expected length of a search path in a skiplist is at most
2 log n + O(1).
Proof. The easiest way to see this is to consider the reverse search path for
a node, x. This path starts at the predecessor of x in L . At any point in
time, if the path can go up a level, then it does. If it cannot go up a level
then it goes left. Thinking about this for a few moments will convince
us that the reverse search path for x is identical to the search path for x,
except that it is reversed.
The number of nodes that the reverse search path visits at a particular
level, r, is related to the following experiment: Toss a coin. If the coin
comes up as heads, then move up and stop. Otherwise, move left and
repeat the experiment. The number of coin tosses before the heads rep-
resents the number of steps to the left that a reverse search path takes at
a particular level.3 Lemma 4.2 tells us that the expected number of coin
tosses before the first heads is 1.
Let S denote the number of steps the forward search path takes at
r
level r that go to the right. We have just argued that E[S ] 1. Further-
r
≤
more, S L , since we can’t take more steps in L than the length of L ,
r r r r
≤ | |
so
E[S ] E[ L ] = n/2r .
r r
≤ | |
We can now finish as in the proof of Lemma 4.4. Let S be the length of
the search path for some node, u, in a skiplist, and let h be the height of
the skiplist. Then
∞
E[S] = E h + S
r
 r=0 
= E[
h]
+
(cid:88)
∞
E[
S
]
r
r=0
(cid:88)
logn
(cid:98) (cid:99) ∞
= E[h] + E[S ] + E[S ]
r r
r=0 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
E[h] + (cid:98) (cid:99) 1 + ∞ n/2r
≤
r=0 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
E[h] + (cid:98) (cid:99) 1 + ∞ 1/2r
≤
r=0 r=0
(cid:88) (cid:88)
3Note that this might overcount the number of steps to the left, since the experiment
should end either at the first heads or when the search path reaches the sentinel, whichever
comes first. This is not a problem since the lemma is only stating an upper bound.
logn
E[h] + (cid:98) (cid:99) 1 + ∞ 1/2r
≤
r=0 r=0
(cid:88) (cid:88)
E[h] + log n + 3
≤
2 log n + 5 .
≤
The following theorem summarizes the results in this section:

（中文关键词：跳表）

## Analysis of Skiplists (3/3)

Theorem 4.3. A skiplist containing n elements has expected size O(n) and
the expected length of the search path for any particular element is at most
2 log n + O(1).

（中文关键词：跳表）
