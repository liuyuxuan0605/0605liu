---
structure:
source: open/ods_p053.md
page: 53
---

# ODS p53: ArrayQueue : An Array-Based Queue §2.3

ArrayQueue : An Array-Based Queue §2.3
ab
bc aadd(d)
add(e)
remove()e bc a d
e bcd
ef bcd
bc ef dadd(g)
add(h)∗
01234567891011c
d
ef bcd gadd(f)
g
bc ef d gh
c ef d ghremove()j= 2 ,n= 3
j= 2 ,n= 4
j= 2 ,n= 5
j= 3 ,n= 4
j= 3 ,n= 5
j= 3 ,n= 6
j= 0 ,n= 7
j= 1 ,n= 6j= 0 ,n= 6
Figure 2.2: A sequence of add(x) and remove (i) operations on an ArrayQueue .
Arrows denote elements being copied. Operations that result in a call to resize ()
are marked with an asterisk.
39

（中文关键词：数组、队列）
