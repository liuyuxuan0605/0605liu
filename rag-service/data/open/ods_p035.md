---
structure:
source: open/ods_p035.md
page: 35
---

# ODS p35: Correctness, Time Complexity, and Space Complexity §1.5

Correctness, Time Complexity, and Space Complexity §1.5
Worst-case versus amortized cost: Suppose that a home costs $120 000.
In order to buy this home, we might get a 120 month (10 year) mortgage
with monthly payments of $1 200 per month. In this case, the worst-case
monthly cost of paying this mortgage is $1 200 per month.
If we have enough cash on hand, we might choose to buy the house
outright, with one payment of $120 000. In this case, over a period of 10
years, the amortized monthly cost of buying this house is
$120000=120 months = $1000 per month :
This is much less than the $1 200 per month we would have to pay if we
took out a mortgage.
Worst-case versus expected cost: Next, consider the issue of ﬁre insur-
ance on our $120 000 home. By studying hundreds of thousands of cases,
insurance companies have determined that the expected amount of ﬁre
damage caused to a home like ours is $10 per month. This is a very small
number, since most homes never have ﬁres, a few homes may have some
small ﬁres that cause a bit of smoke damage, and a tiny number of homes
burn right to their foundations. Based on this information, the insurance
company charges $15 per month for ﬁre insurance.
Now it’s decision time. Should we pay the $15 worst-case monthly cost
for ﬁre insurance, or should we gamble and self-insure at an expected cost
of $10 per month? Clearly, the $10 per month costs less in expectation ,
but we have to be able to accept the possibility that the actual cost may be
much higher. In the unlikely event that the entire house burns down, the
actual cost will be $120 000.
These ﬁnancial examples also o ﬀer insight into why we sometimes set-
tle for an amortized or expected running time over a worst-case running
time. It is often possible to get a lower expected or amortized running
time than a worst-case running time. At the very least, it is very often
possible to get a much simpler data structure if one is willing to settle for
amortized or expected running times.
21

（中文关键词：摊还分析）
