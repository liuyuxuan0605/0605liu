---
structure:
source: open/ods_p034.md
page: 34
---

# ODS p34: §1.5 Introduction

§1.5 Introduction
Correctness: The data structure should correctly implement its inter-
face.
Time complexity: The running times of operations on the data structure
should be as small as possible.
Space complexity: The data structure should use as little memory as
possible.
In this introductory text, we will take correctness as a given; we won’t
consider data structures that give incorrect answers to queries or don’t
perform updates properly. We will, however, see data structures that
make an extra e ﬀort to keep space usage to a minimum. This won’t usu-
ally aﬀect the (asymptotic) running times of operations, but can make the
data structures a little slower in practice.
When studying running times in the context of data structures we
tend to come across three di ﬀerent kinds of running time guarantees:
Worst-case running times: These are the strongest kind of running time
guarantees. If a data structure operation has a worst-case running
time off(n), then one of these operations never takes longer than
f(n) time.
Amortized running times: If we say that the amortized running time of
an operation in a data structure is f(n), then this means that the
cost of a typical operation is at most f(n). More precisely, if a data
structure has an amortized running time of f(n), then a sequence
ofmoperations takes at most mf(n) time. Some individual opera-
tions may take more than f(n) time but the average, over the entire
sequence of operations, is at most f(n).
Expected running times: If we say that the expected running time of an
operation on a data structure is f(n), this means that the actual run-
ning time is a random variable (see Section 1.3.4) and the expected
value of this random variable is at most f(n). The randomization
here is with respect to random choices made by the data structure.
To understand the di ﬀerence between worst-case, amortized, and ex-
pected running times, it helps to consider a ﬁnancial example. Consider
the cost of buying a house:
20

（中文关键词：随机、摊还分析）
