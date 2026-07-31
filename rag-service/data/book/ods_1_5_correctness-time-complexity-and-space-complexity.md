---
structure: 
source: book/ods_1_5_correctness-time-complexity-and-space-complexity.md
chapter: 1. Introduction
section: 1.5
page: 33
kind: textbook
---

# 1.5 Correctness, Time Complexity, and Space Complexity

## Correctness, Time Complexity, and Space Complexity (1/2)

When studying the performance of a data structure, there are three things
that matter most:
Correctness: The data structure should correctly implement its inter-
face.
Time complexity: The running times of operations on the data structure
should be as small as possible.
Space complexity: The data structure should use as little memory as
possible.
In this introductory text, we will take correctness as a given; we won’t
consider data structures that give incorrect answers to queries or don’t
perform updates properly. We will, however, see data structures that
make an extra effort to keep space usage to a minimum. This won’t usu-
ally affect the (asymptotic) running times of operations, but can make the
data structures a little slower in practice.
When studying running times in the context of data structures we
tend to come across three different kinds of running time guarantees:
Worst-case running times: These are the strongest kind of running time
guarantees. If a data structure operation has a worst-case running
time of f (n), then one of these operations never takes longer than
f (n) time.
Amortized running times: If we say that the amortized running time of
an operation in a data structure is f (n), then this means that the
cost of a typical operation is at most f (n). More precisely, if a data
structure has an amortized running time of f (n), then a sequence
of m operations takes at most mf (n) time. Some individual opera-
tions may take more than f (n) time but the average, over the entire
sequence of operations, is at most f (n).
Expected running times: If we say that the expected running time of an
operation on a data structure is f (n), this means that the actual run-
ning time is a random variable (see Section 1.3.4) and the expected
value of this random variable is at most f (n). The randomization
here is with respect to random choices made by the data structure.
To understand the difference between worst-case, amortized, and ex-
pected running times, it helps to consider a financial example. Consider
the cost of buying a house:
Worst-case versus amortized cost: Suppose that a home costs $120 000.
In order to buy this home, we might get a 120 month (10 year) mortgage
with monthly payments of $1 200 per month. In this case, the worst-case
monthly cost of paying this mortgage is $1 200 per month.

（中文关键词：摊还分析、复杂度）

## Correctness, Time Complexity, and Space Complexity (2/2)

If we have enough cash on hand, we might choose to buy the house
outright, with one payment of $120 000. In this case, over a period of 10
years, the amortized monthly cost of buying this house is
$120 000/120 months = $1 000 per month .
This is much less than the $1 200 per month we would have to pay if we
took out a mortgage.
Worst-case versus expected cost: Next, consider the issue of fire insur-
ance on our $120 000 home. By studying hundreds of thousands of cases,
insurance companies have determined that the expected amount of fire
damage caused to a home like ours is $10 per month. This is a very small
number, since most homes never have fires, a few homes may have some
small fires that cause a bit of smoke damage, and a tiny number of homes
burn right to their foundations. Based on this information, the insurance
company charges $15 per month for fire insurance.
Now it’s decision time. Should we pay the $15 worst-case monthly cost
for fire insurance, or should we gamble and self-insure at an expected cost
of $10 per month? Clearly, the $10 per month costs less in expectation,
but we have to be able to accept the possibility that the actual cost may be
much higher. In the unlikely event that the entire house burns down, the
actual cost will be $120 000.
These financial examples also offer insight into why we sometimes set-
tle for an amortized or expected running time over a worst-case running
time. It is often possible to get a lower expected or amortized running
time than a worst-case running time. At the very least, it is very often
possible to get a much simpler data structure if one is willing to settle for
amortized or expected running times.

（中文关键词：摊还分析、复杂度）
