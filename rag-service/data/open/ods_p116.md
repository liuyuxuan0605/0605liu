---
structure:
source: open/ods_p116.md
page: 116
---

# ODS p116: §4.5 Skiplists

§4.5 Skiplists
E[h] +blogncX
r=01 +1X
r=01=2r
E[h] + log n+ 3
2log n+ 5:
The following theorem summarizes the results in this section:
Theorem 4.3. A skiplist containing nelements has expected size O(n)and
the expected length of the search path for any particular element is at most
2log n+O(1).
4.5 Discussion and Exercises
Skiplists were introduced by Pugh [62] who also presented a number of
applications and extensions of skiplists [61]. Since then they have been
studied extensively. Several researchers have done very precise analyses
of the expected length and variance of the length of the search path for
theith element in a skiplist [45, 44, 58]. Deterministic versions [53], bi-
ased versions [8, 26], and self-adjusting versions [12] of skiplists have all
been developed. Skiplist implementations have been written for various
languages and frameworks and have been used in open-source database
systems [71, 63]. A variant of skiplists is used in the HP-UX operating
system kernel’s process management structures [42]. Skiplists are even
part of the Java 1.6 API [55].
Exercise 4.1. Illustrate the search paths for 2.5 and 5.5 on the skiplist in
Figure 4.1.
Exercise 4.2. Illustrate the addition of the values 0.5 (with a height of 1)
and then 3.5 (with a height of 2) to the skiplist in Figure 4.1.
Exercise 4.3. Illustrate the removal of the values 1 and then 3 from the
skiplist in Figure 4.1.
Exercise 4.4. Illustrate the execution of remove (2) on the SkiplistList
in Figure 4.5.
102

（中文关键词：跳表）
