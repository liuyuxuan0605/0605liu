---
structure:
source: open/ods_p028.md
page: 28
---

# ODS p28: §1.3 Introduction

§1.3 Introduction
Simple
void snippet() {
for (int i = 0; i < n; i++)
a[i] = i;
}
One execution of this method involves
• 1 assignment ( inti =0),
•n+ 1 comparisons ( i<n),
•nincrements ( i+ +),
•narray o ﬀset calculations ( a[i]), and
•nindirect assignments ( a[i] =i).
So we could write this running time as
T(n) =a+b(n+ 1) +cn+dn+en;
wherea,b,c,d, andeare constants that depend on the machine running
the code and represent the time to perform assignments, comparisons,
increment operations, array o ﬀset calculations, and indirect assignments,
respectively. However, if this expression represents the running time of
two lines of code, then clearly this kind of analysis will not be tractable
to complicated code or algorithms. Using big-Oh notation, the running
time can be simpliﬁed to
T(n) =O(n):
Not only is this more compact, but it also gives nearly as much informa-
tion. The fact that the running time depends on the constants a,b,c,d,
andein the above example means that, in general, it will not be possible
to compare two running times to know which is faster without knowing
the values of these constants. Even if we make the e ﬀort to determine
these constants (say, through timing tests), then our conclusion will only
be valid for the machine we run our tests on.
Big-Oh notation allows us to reason at a much higher level, making it
possible to analyze more complicated functions. If two algorithms have
14

（中文关键词：数组、复杂度分析）
