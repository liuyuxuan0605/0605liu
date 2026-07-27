---
structure:
source: open/ods_p041.md
page: 41
---

# ODS p41: Discussion and Exercises §1.8

Discussion and Exercises §1.8
order. Do this until there are no more lines left to read, at which
point any remaining lines should be output in reverse order.
In other words, your output will start with the 50th line, then the
49th, then the 48th, and so on down to the ﬁrst line. This will be
followed by the 100th line, followed by the 99th, and so on down to
the 51st line. And so on.
Your code should never have to store more than 50 lines at any given
time.
3. Read the input one line at a time. At any point after reading the
ﬁrst 42 lines, if some line is blank (i.e., a string of length 0), then
output the line that occured 42 lines prior to that one. For example,
if Line 242 is blank, then your program should output line 200.
This program should be implemented so that it never stores more
than 43 lines of the input at any given time.
4. Read the input one line at a time and write each line to the output
if it is not a duplicate of some previous input line. Take special care
so that a ﬁle with a lot of duplicate lines does not use more memory
than what is required for the number of unique lines.
5. Read the input one line at a time and write each line to the output
only if you have already read this line before. (The end result is that
you remove the ﬁrst occurrence of each line.) Take special care so
that a ﬁle with a lot of duplicate lines does not use more memory
than what is required for the number of unique lines.
6. Read the entire input one line at a time. Then output all lines sorted
by length, with the shortest lines ﬁrst. In the case where two lines
have the same length, resolve their order using the usual “sorted
order.” Duplicate lines should be printed only once.
7. Do the same as the previous question except that duplicate lines
should be printed the same number of times that they appear in the
input.
8. Read the entire input one line at a time and then output the even
numbered lines (starting with the ﬁrst line, line 0) followed by the
odd-numbered lines.
27

（中文关键词：排序）
