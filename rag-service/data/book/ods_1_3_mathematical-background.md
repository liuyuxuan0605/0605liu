---
structure: 
source: book/ods_1_3_mathematical-background.md
chapter: 1. Introduction
section: 1.3
page: 23
kind: textbook
---

# 1.3 Mathematical Background

In this section, we review some mathematical notations and tools used
throughout this book, including logarithms, big-Oh notation, and proba-
bility theory. This review will be brief and is not intended as an introduc-
tion. Readers who feel they are missing this background are encouraged
to read, and do exercises from, the appropriate sections of the very good
(and free) textbook on mathematics for computer science [50].

## 1.3.1 Exponentials and Logarithms

The expression bx denotes the number b raised to the power of x. If x is
a positive integer, then this is just the value of b multiplied by itself x 1
−
times:
bx = b b b .
× × · · · ×
x
When x is a negative integer, bx =(cid:124)1/b(cid:123)x(cid:122). Wh(cid:125)en x = 0, bx = 1. When b is not
−
(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)
an integer, we can still define exponentiation in terms of the exponential
function ex (see below), which is itself defined in terms of the exponential
series, but this is best left to a calculus text.
In this book, the expression log k denotes the base-b logarithm of k.
b
That is, the unique value x that satisfies
bx = k .
Most of the logarithms in this book are base 2 (binary logarithms). For
these, we omit the base, so that log k is shorthand for log k.
2
An informal, but useful, way to think about logarithms is to think of
log k as the number of times we have to divide k by b before the result
b
is less than or equal to 1. For example, when one does binary search,
each comparison reduces the number of possible answers by a factor of 2.
This is repeated until there is at most one possible answer. Therefore, the
number of comparison done by binary search when there are initially at
most n + 1 possible answers is at most log (n + 1) .
(cid:100) 2 (cid:101)
Another logarithm that comes up several times in this book is the nat-
ural logarithm. Here we use the notation ln k to denote log k, where e —
e
Euler’s constant — is given by
1 n
e = lim 1 + 2.71828 .
n n ≈
→∞ (cid:18) (cid:19)
The natural logarithm comes up frequently because it is the value of a
particularly common integral:
k
1/x dx = ln k .
1
(cid:90)
Two of the most common manipulations we do with logarithms are re-
moving them from an exponent:
blog b k = k
and changing the base of a logarithm:
log k
log k = a .
b log b
a
For example, we can use these two manipulations to compare the natural
and binary logarithms
log k log k
ln k = = = (ln 2)(log k) 0.693147 log k .
log e (ln e)/(ln 2) ≈

## 1.3.2 Factorials

In one or two places in this book, the factorial function is used. For a non-
negative integer n, the notation n! (pronounced “n factorial”) is defined
to mean
n! = 1 2 3 n .
· · · · · · ·
Factorials appear because n! counts the number of distinct permutations,
i.e., orderings, of n distinct elements. For the special case n = 0, 0! is
defined as 1.
The quantity n! can be approximated using Stirling’s Approximation:
n n
n! = √2πn eα(n) ,
e
(cid:18) (cid:19)
where
1 1
< α(n) < .
12n + 1 12n
Stirling’s Approximation also approximates ln(n!):
1
ln(n!) = n ln n n + ln(2πn) + α(n)
− 2
(In fact, Stirling’s Approximation is most easily proven by approximating
n
ln(n!) = ln 1 + ln 2 + + ln n by the integral ln n dn = n ln n n + 1.)
· · · 1 −
Related to the factorial function are the binomial coefficients. For a
(cid:82)
non-negative integer n and an integer k 0, . . . , n , the notation n de-
∈ { } k
notes:
n n! (cid:0) (cid:1)
= .
k k!(n k)!
(cid:32) (cid:33) −
The binomial coefficient n (pronounced “n choose k”) counts the num-
k
ber of subsets of an n element set that have size k, i.e., the number of ways
(cid:0) (cid:1)
of choosing k distinct integers from the set 1, . . . , n .
{ }

## 1.3.3 Asymptotic Notation (1/3)

When analyzing data structures in this book, we want to talk about the
running times of various operations. The exact running times will, of
course, vary from computer to computer and even from run to run on an
individual computer. When we talk about the running time of an opera-
tion we are referring to the number of computer instructions performed
during the operation. Even for simple code, this quantity can be diffi-
cult to compute exactly. Therefore, instead of analyzing running times
exactly, we will use the so-called big-Oh notation: For a function f (n),
O(f (n)) denotes a set of functions,
g(n) : there exists c > 0, and n such that
O(f (n)) = 0 .
g(n) c f (n) for all n n
0
(cid:40) ≤ · ≥ (cid:41)
Thinking graphically, this set consists of the functions g(n) where c f (n)
·
starts to dominate g(n) when n is sufficiently large.
We generally use asymptotic notation to simplify functions. For exam-
ple, in place of 5n log n + 8n 200 we can write O(n log n). This is proven
−
as follows:
5n log n + 8n 200 5n log n + 8n
− ≤
5n log n + 8n log n for n 2 (so that log n 1)
≤ ≥ ≥
13n log n .
≤
This demonstrates that the function f (n) = 5n log n + 8n 200 is in the set
−
O(n log n) using the constants c = 13 and n = 2.
A number of useful shortcuts can be applied when using asymptotic
notation. First:
O(nc1) O(nc2) ,
⊂
for any c < c . Second: For any constants a, b, c > 0,
1 2
O(a) O(log n) O(nb) O(cn) .
⊂ ⊂ ⊂
These inclusion relations can be multiplied by any positive value, and
they still hold. For example, multiplying by n yields:
O(n) O(n log n) O(n1+b) O(ncn) .
⊂ ⊂ ⊂
Continuing in a long and distinguished tradition, we will abuse this
notation by writing things like f (n) = O(f (n)) when what we really mean
1
is f (n) O(f (n)). We will also make statements like “the running time
1
∈
of this operation is O(f (n))” when this statement should be “the running
time of this operation is a member of O(f (n)).” These shortcuts are mainly
to avoid awkward language and to make it easier to use asymptotic nota-
tion within strings of equations.
A particularly strange example of this occurs when we write state-
ments like
T (n) = 2 log n + O(1) .

（中文关键词：图）

## 1.3.3 Asymptotic Notation (2/3)

Again, this would be more correctly written as
T (n) 2 log n + [some member of O(1)] .
≤
The expression O(1) also brings up another issue. Since there is no
variable in this expression, it may not be clear which variable is getting
arbitrarily large. Without context, there is no way to tell. In the example
above, since the only variable in the rest of the equation is n, we can
assume that this should be read as T (n) = 2 log n+O(f (n)), where f (n) = 1.
Big-Oh notation is not new or unique to computer science. It was used
by the number theorist Paul Bachmann as early as 1894, and is immensely
useful for describing the running times of computer algorithms. Consider
the following piece of code:
Simple
void snippet() {
for (int i = 0; i < n; i++)
a[i] = i;
}
One execution of this method involves
• 1 assignment (int i = 0),
• n + 1 comparisons (i < n),
• n increments (i + +),
• n array offset calculations (a[i]), and
• n indirect assignments (a[i] = i).
So we could write this running time as
T (n) = a + b(n + 1) + cn + dn + en ,
where a, b, c, d, and e are constants that depend on the machine running
the code and represent the time to perform assignments, comparisons,
increment operations, array offset calculations, and indirect assignments,
respectively. However, if this expression represents the running time of
two lines of code, then clearly this kind of analysis will not be tractable
to complicated code or algorithms. Using big-Oh notation, the running
time can be simplified to
T (n) = O(n) .
Not only is this more compact, but it also gives nearly as much informa-
tion. The fact that the running time depends on the constants a, b, c, d,
and e in the above example means that, in general, it will not be possible
to compare two running times to know which is faster without knowing
the values of these constants. Even if we make the effort to determine
these constants (say, through timing tests), then our conclusion will only
be valid for the machine we run our tests on.

（中文关键词：数组）

## 1.3.3 Asymptotic Notation (3/3)

Big-Oh notation allows us to reason at a much higher level, making it
possible to analyze more complicated functions. If two algorithms have
the same big-Oh running time, then we won’t know which is faster, and
there may not be a clear winner. One may be faster on one machine,
and the other may be faster on a different machine. However, if the two
algorithms have demonstrably different big-Oh running times, then we
can be certain that the one with the smaller running time will be faster
for large enough values of n.
An example of how big-Oh notation allows us to compare two differ-
ent functions is shown in Figure 1.5, which compares the rate of grown
of f (n) = 15n versus f (n) = 2n log n. It might be that f (n) is the run-
1 2 1
ning time of a complicated linear time algorithm while f (n) is the run-
2
ning time of a considerably simpler algorithm based on the divide-and-
conquer paradigm. This illustrates that, although f (n) is greater than
1
f (n) for small values of n, the opposite is true for large values of n. Even-
2
tually f (n) wins out, by an increasingly wide margin. Analysis using
1
big-Oh notation told us that this would happen, since O(n) O(n log n).
⊂
In a few cases, we will use asymptotic notation on functions with more
than one variable. There seems to be no standard for this, but for our
purposes, the following definition is sufficient:
g(n , . . . , n ) : there exists c > 0, and z such that
1 k
O(f (n , . . . , n )) = g(n , . . . , n ) c f (n , . . . , n ) .
1 k 1 k 1 k
 ≤ · 
 for all n 1 , . . . , n k such that g(n 1 , . . . , n k )
≥
z 
This definition capt
ures
the situation we really care about: when th
e
ar-
guments n , . . . , n make g take on large values. This definition also agrees
1 k
with the univariate definition of O(f (n)) when f (n) is an increasing func-
tion of n. The reader should be warned that, although this works for our
purposes, other texts may treat multivariate functions and asymptotic
notation differently.

## 1.3.4 Randomization and Probability (1/2)

Some of the data structures presented in this book are randomized; they
make random choices that are independent of the data being stored in
them or the operations being performed on them. For this reason, per-
forming the same set of operations more than once using these structures
could result in different running times. When analyzing these data struc-
1600
1400
1200
1000
800
600
400
200
0
10 20 30 40 50 60 70 80 90 100
)n(f
15n
2nlogn
n
300000
250000
200000
150000
100000
50000
0
0 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000
)n(f
15n
2nlogn
n
Figure 1.5: Plots of 15n versus 2nlogn.
tures we are interested in their average or expected running times.
Formally, the running time of an operation on a randomized data
structure is a random variable, and we want to study its expected value.
For a discrete random variable X taking on values in some countable uni-
verse U , the expected value of X, denoted by E[X], is given by the formula
E[X] = x Pr X = x .
· { }
x U
(cid:88)∈
Here Pr denotes the probability that the event occurs. In all of the
{E} E
examples in this book, these probabilities are only with respect to the ran-
dom choices made by the randomized data structure; there is no assump-
tion that the data stored in the structure, nor the sequence of operations
performed on the data structure, is random.
One of the most important properties of expected values is linearity of
expectation. For any two random variables X and Y ,
E[X + Y ] = E[X] + E[Y ] .
More generally, for any random variables X , . . . , X ,
1 k
k k
E X = E[X ] .
k i
 
i=1 i=1
Linearity of expectation al
l (cid:88)
ows u
s
to
(cid:88)
break down complicated random
variables (like the left hand sides of the above equations) into sums of
simpler random variables (the right hand sides).
A useful trick, that we will use repeatedly, is defining indicator ran-
dom variables. These binary variables are useful when we want to count
something and are best illustrated by an example. Suppose we toss a fair
coin k times and we want to know the expected number of times the coin
turns up as heads. Intuitively, we know the answer is k/2, but if we try to
prove it using the definition of expected value, we get
k
E[X] = i Pr X = i
· { }
i=0
(cid:88)
k
k
= i /2k
· i
i=0 (cid:32) (cid:33)
(cid:88)
k 1
− k 1
= k − /2k
· i
i=0 (cid:32) (cid:33)
(cid:88)
= k/2 .

（中文关键词：随机化、概率）

## 1.3.4 Randomization and Probability (2/2)

This requires that we know enough to calculate that Pr X = i = k /2k,
{ } i
and that we know the binomial identities i k i = k k −i 1 and k i=0 k i (cid:0) = (cid:1) 2k.
Using indicator variables and linearity of expectation makes things
(cid:0) (cid:1) (cid:0) (cid:1) (cid:80) (cid:0) (cid:1)
much easier. For each i 1, . . . , k , define the indicator random variable
∈ { }
1 if the ith coin toss is heads
I =
i
0 otherwise.


Then 
E[I ] = (1/2)1 + (1/2)0 = 1/2 .
i
Now, X = k I , so
i=1 i
(cid:80) k
E[X] = E I
i
 
i=1
k
 (cid:88) 
= E[I ]
i
i=1
(cid:88)
k
= 1/2
i=1
(cid:88)
= k/2 .
This is a bit more long-winded, but doesn’t require that we know any
magical identities or compute any non-trivial probabilities. Even better,
it agrees with the intuition that we expect half the coins to turn up as
heads precisely because each individual coin turns up as heads with a
probability of 1/2.

（中文关键词：概率）
