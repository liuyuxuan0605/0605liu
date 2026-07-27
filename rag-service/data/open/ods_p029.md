---
structure:
source: open/ods_p029.md
page: 29
---

# ODS p29: Mathematical Background §1.3

Mathematical Background §1.3
the same big-Oh running time, then we won’t know which is faster, and
there may not be a clear winner. One may be faster on one machine,
and the other may be faster on a di ﬀerent machine. However, if the two
algorithms have demonstrably di ﬀerent big-Oh running times, then we
can be certain that the one with the smaller running time will be faster
for large enough values of n.
An example of how big-Oh notation allows us to compare two di ﬀer-
ent functions is shown in Figure 1.5, which compares the rate of grown
off1(n) = 15 nversusf2(n) = 2 nlogn. It might be that f1(n) is the run-
ning time of a complicated linear time algorithm while f2(n) is the run-
ning time of a considerably simpler algorithm based on the divide-and-
conquer paradigm. This illustrates that, although f1(n) is greater than
f2(n) for small values of n, the opposite is true for large values of n. Even-
tuallyf1(n) wins out, by an increasingly wide margin. Analysis using
big-Oh notation told us that this would happen, since O(n)O(nlogn).
In a few cases, we will use asymptotic notation on functions with more
than one variable. There seems to be no standard for this, but for our
purposes, the following deﬁnition is su ﬃcient:
O(f(n1;:::;nk)) =8>>><>>>:g(n1;:::;nk) : there exists c>0, andzsuch that
g(n1;:::;nk)cf(n1;:::;nk)
for alln1;:::;nksuch thatg(n1;:::;nk)z9>>>=>>>;:
This deﬁnition captures the situation we really care about: when the ar-
gumentsn1;:::;nkmakegtake on large values. This deﬁnition also agrees
with the univariate deﬁnition of O(f(n)) whenf(n) is an increasing func-
tion ofn. The reader should be warned that, although this works for our
purposes, other texts may treat multivariate functions and asymptotic
notation di ﬀerently.
1.3.4 Randomization and Probability
Some of the data structures presented in this book are randomized ; they
make random choices that are independent of the data being stored in
them or the operations being performed on them. For this reason, per-
forming the same set of operations more than once using these structures
could result in di ﬀerent running times. When analyzing these data struc-
15

（中文关键词：概率、随机、复杂度分析）
