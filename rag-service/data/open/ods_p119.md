---
structure:
source: open/ods_p119.md
page: 119
---

# ODS p119: Discussion and Exercises §4.5

Discussion and Exercises §4.5
Hint 1: Every substring is a preﬁx of some su ﬃx, so it su ﬃces to store all
suﬃxes of the text ﬁle.
Hint 2: Any su ﬃx can be represented compactly as a single integer indi-
cating where the su ﬃx begins in the text.
Test your application on some large texts, such as some of the books
available at Project Gutenberg [1]. If done correctly, your applications
will be very responsive; there should be no noticeable lag between typing
keystrokes and seeing the results.
Exercise 4.15. (This excercise should be done after reading about binary
search trees, in Section 6.2.) Compare skiplists with binary search trees
in the following ways:
1. Explain how removing some edges of a skiplist leads to a structure
that looks like a binary tree and is similar to a binary search tree.
2. Skiplists and binary search trees each use about the same number
of pointers (2 per node). Skiplists make better use of those pointers,
though. Explain why.
105

（中文关键词：跳表、二叉搜索树、二叉树、树）
