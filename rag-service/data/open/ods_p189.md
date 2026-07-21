---
structure:
source: open/ods_p189.md
page: 189
---

# ODS p189: At all times, nandqobey the following inequalities:

ScapegoatTree : A Binary Search Tree with Partial Rebuilding §8.1
012
34567
8
9
Figure 8.1: A ScapegoatTree with 10 nodes and height 5.
At all times, nandqobey the following inequalities:
q=2nq:
In addition, a ScapegoatTree has logarithmic height; at all times, the
height of the scapegoat tree does not exceed:
log3=2qlog3=22n<log3=2n+ 2: (8.1)
Even with this constraint, a ScapegoatTree can look surprisingly unbal-
anced. The tree in Figure 8.1 has q=n= 10 and height 5 <log3=210
5:679.
Implementing the find (x) operation in a ScapegoatTree is done us-
ing the standard algorithm for searching in a BinarySearchTree (see Sec-
tion 6.2). This takes time proportional to the height of the tree which, by
(8.1) isO(logn).
To implement the add(x) operation, we ﬁrst increment nand qand
then use the usual algorithm for adding xto a binary search tree; we
search for xand then add a new leaf uwith u:x=x. At this point, we may
get lucky and the depth of umight not exceed log3=2q. If so, then we leave
well enough alone and don’t do anything else.
Unfortunately, it will sometimes happen that depth (u)>log3=2q. In
this case, we need to reduce the height. This isn’t a big job; there is only
175

（中文关键词：二叉搜索树、替罪羊树、树）
