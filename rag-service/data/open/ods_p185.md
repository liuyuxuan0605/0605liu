---
structure:
source: open/ods_p185.md
page: 185
---

# ODS p185: Discussion and Exercises §7.3

Discussion and Exercises §7.3
Exercise 7.5. Use both parts of Lemma 7.2 to prove that the expected
number of rotations performed by an add(x) operation (and hence also a
remove (x) operation) is O(1).
Exercise 7.6. Modify the Treap implementation given here so that it does
not explicitly store priorities. Instead, it should simulate them by hashing
thehashCode () of each node.
Exercise 7.7. Suppose that a binary search tree stores, at each node, u,
the height, u:height , of the subtree rooted at u, and the size, u:size of the
subtree rooted at u.
1. Show how, if we perform a left or right rotation at u, then these two
quantities can be updated, in constant time, for all nodes a ﬀected
by the rotation.
2. Explain why the same result is not possible if we try to also store
the depth, u:depth , of each node u.
Exercise 7.8. Design and implement an algorithm that constructs a Treap
from a sorted array, a, ofnelements. This method should run in O(n)
worst-case time and should construct a Treap that is indistinguishable
from one in which the elements of awere added one at a time using the
add(x) method.
Exercise 7.9. This exercise works out the details of how one can e ﬃ-
ciently search a Treap given a pointer that is close to the node we are
searching for.
1. Design and implement a Treap implementation in which each node
keeps track of the minimum and maximum values in its subtree.
2. Using this extra information, add a fingerFind (x;u) method that
executes the find (x) operation with the help of a pointer to the node
u(which is hopefully not far from the node that contains x). This
operation should start at uand walk upwards until it reaches a node
wsuch that w:minxw:max. From that point onwards, it should
perform a standard search for xstarting from w. (One can show
that fingerFind (x;u) takesO(1 + logr) time, where ris the number
of elements in the treap whose value is between xandu:x.)
171

（中文关键词：数组、哈希、二叉搜索树、树、排序）
