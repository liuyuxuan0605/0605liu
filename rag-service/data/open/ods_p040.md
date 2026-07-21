---
structure:
source: open/ods_p040.md
page: 40
---

# ODS p40: §1.8 Introduction

§1.8 Introduction
1.8 Discussion and Exercises
The List ,USet , and SSet interfaces described in Section 1.2 are inﬂu-
enced by the Java Collections Framework [54]. These are essentially sim-
pliﬁed versions of the List ,Set,Map,SortedSet , and SortedMap inter-
faces found in the Java Collections Framework. The accompanying source
code includes wrapper classes for making USet and SSet implementa-
tions into Set,Map,SortedSet , and SortedMap implementations.
For a superb (and free) treatment of the mathematics discussed in this
chapter, including asymptotic notation, logarithms, factorials, Stirling’s
approximation, basic probability, and lots more, see the textbook by Ley-
man, Leighton, and Meyer [50]. For a gentle calculus text that includes
formal deﬁnitions of exponentials and logarithms, see the (freely avail-
able) classic text by Thompson [73].
For more information on basic probability, especially as it relates to
computer science, see the textbook by Ross [65]. Another good reference,
which covers both asymptotic notation and probability, is the textbook by
Graham, Knuth, and Patashnik [37].
Readers wanting to brush up on their Java programming can ﬁnd
many Java tutorials online [56].
Exercise 1.1. This exercise is designed to help familiarize the reader with
choosing the right data structure for the right problem. If implemented,
the parts of this exercise should be done by making use of an implemen-
tation of the relevant interface ( Stack ,Queue ,Deque ,USet , orSSet ) pro-
vided by the Java Collections Framework.
Solve the following problems by reading a text ﬁle one line at a time
and performing operations on each line in the appropriate data struc-
ture(s). Your implementations should be fast enough that even ﬁles con-
taining a million lines can be processed in a few seconds.
1. Read the input one line at a time and then write the lines out in
reverse order, so that the last input line is printed ﬁrst, then the
second last input line, and so on.
2. Read the ﬁrst 50 lines of input and then write them out in reverse
order. Read the next 50 lines and then write them out in reverse
26

（中文关键词：栈、队列、双端队列、排序、概率）
