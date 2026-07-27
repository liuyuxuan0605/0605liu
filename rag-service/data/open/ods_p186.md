---
structure:
source: open/ods_p186.md
page: 186
---

# ODS p186: §7.3 Random Binary Search Trees

§7.3 Random Binary Search Trees
3. Extend your implementation into a version of a treap that starts
all its find (x) operations from the node most recently found by
find (x).
Exercise 7.10. Design and implement a version of a Treap that includes
aget(i) operation that returns the key with rank iin the Treap . (Hint:
Have each node, u, keep track of the size of the subtree rooted at u.)
Exercise 7.11. Implement a TreapList , an implementation of the List
interface as a treap. Each node in the treap should store a list item, and
an in-order traversal of the treap ﬁnds the items in the same order that
they occur in the list. All the List operations get(i),set(i;x),add(i;x)
andremove (i) should run in O(logn) expected time.
Exercise 7.12. Design and implement a version of a Treap that supports
thesplit (x) operation. This operation removes all values from the Treap
that are greater than xand returns a second Treap that contains all the
removed values.
Example: the code t2=t:split (x) removes from tall values greater than
xand returns a new Treap t2 containing all these values. The split (x)
operation should run in O(logn) expected time.
Warning: For this modiﬁcation to work properly and still allow the size ()
method to run in constant time, it is necessary to implement the modiﬁ-
cations in Exercise 7.10.
Exercise 7.13. Design and implement a version of a Treap that supports
theabsorb (t2) operation, which can be thought of as the inverse of the
split (x) operation. This operation removes all values from the Treap
t2and adds them to the receiver. This operation presupposes that the
smallest value in t2is greater than the largest value in the receiver. The
absorb (t2) operation should run in O(logn) expected time.
Exercise 7.14. Implement Martinez’s randomized binary search trees, as
discussed in this section. Compare the performance of your implementa-
tion with that of the Treap implementation.
172

（中文关键词：二叉搜索树、树、随机）
