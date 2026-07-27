---
structure:
source: open/ods_p031.md
page: 31
---

# ODS p31: Mathematical Background §1.3

Mathematical Background §1.3
tures we are interested in their average or expected running times.
Formally, the running time of an operation on a randomized data
structure is a random variable, and we want to study its expected value .
For a discrete random variable Xtaking on values in some countable uni-
verseU, the expected value of X, denoted by E[ X], is given by the formula
E[X] =X
x2UxPrfX=xg:
Here PrfEgdenotes the probability that the event Eoccurs. In all of the
examples in this book, these probabilities are only with respect to the ran-
dom choices made by the randomized data structure; there is no assump-
tion that the data stored in the structure, nor the sequence of operations
performed on the data structure, is random.
One of the most important properties of expected values is linearity of
expectation . For any two random variables XandY,
E[X+Y] = E[X] + E[Y]:
More generally, for any random variables X1;:::;Xk,
E2
666664kX
i=1Xk3
777775=kX
i=1E[Xi]:
Linearity of expectation allows us to break down complicated random
variables (like the left hand sides of the above equations) into sums of
simpler random variables (the right hand sides).
A useful trick, that we will use repeatedly, is deﬁning indicator ran-
dom variables . These binary variables are useful when we want to count
something and are best illustrated by an example. Suppose we toss a fair
coinktimes and we want to know the expected number of times the coin
turns up as heads. Intuitively, we know the answer is k=2, but if we try to
prove it using the deﬁnition of expected value, we get
E[X] =kX
i=0iPrfX=ig
=kX
i=0i k
i!
=2k
17

（中文关键词：概率、随机）
