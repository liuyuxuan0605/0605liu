---
structure:
source: open/ods_p073.md
page: 73
---

# ODS p73: Discussion and Exercises §2.7

Discussion and Exercises §2.7
for (int i = 0; i < 1<<(r/2); i++) {
if ((s+1) *(s+1) <= i << (r/2)) s++; // sqrt increases
sqrtab[i] = s;
}
}
To summarize, the computations done by the i2b(i) method can be
implemented in constant time on the word-RAM using O(pn) extra mem-
ory to store the sqrttab andlogtab arrays. These arrays can be rebuilt
when nincreases or decreases by a factor of two, and the cost of this re-
building can be amortized over the number of add(i;x) and remove (i)
operations that caused the change in nin the same way that the cost of
resize () is analyzed in the ArrayStack implementation.
2.7 Discussion and Exercises
Most of the data structures described in this chapter are folklore. They
can be found in implementations dating back over 30 years. For example,
implementations of stacks, queues, and deques, which generalize eas-
ily to the ArrayStack ,ArrayQueue andArrayDeque structures described
here, are discussed by Knuth [46, Section 2.2.2].
Brodnik et al. [13] seem to have been the ﬁrst to describe the Rootish-
ArrayStack and prove apnlower-bound like that in Section 2.6.2. They
also present a di ﬀerent structure that uses a more sophisticated choice
of block sizes in order to avoid computing square roots in the i2b(i)
method. Within their scheme, the block containing iis blockblog(i+ 1)c,
which is simply the index of the leading 1 bit in the binary representation
ofi+1. Some computer architectures provide an instruction for comput-
ing the index of the leading 1-bit in an integer.
A structure related to the RootishArrayStack is the two-level tiered-
vector of Goodrich and Kloss [35]. This structure supports the get(i;x)
andset(i;x) operations in constant time and add(i;x) and remove (i) in
O(pn) time. These running times are similar to what can be achieved with
the more careful implementation of a RootishArrayStack discussed in
Exercise 2.11.
59

（中文关键词：数组、栈、队列、双端队列、摊还分析）
