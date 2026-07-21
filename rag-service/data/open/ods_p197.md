---
structure:
source: open/ods_p197.md
page: 197
---

# ODS p197: Discussion and Exercises §8.2

Discussion and Exercises §8.2
rooted at each node. Compare the performance of the resulting imple-
mentation with that of the original ScapegoatTree implementation as
well as the implementation from Exercise 8.5.
Exercise 8.7. Reimplement the rebuild (u) method discussed at the be-
ginning of this chapter so that it does not require the use of an array to
store the nodes of the subtree being rebuilt. Instead, it should use re-
cursion to ﬁrst connect the nodes into a linked list and then convert this
linked list into a perfectly balanced binary tree. (There are very elegant
recursive implementations of both steps.)
Exercise 8.8. Analyze and implement a WeightBalancedTree . This is a
tree in which each node u, except the root, maintains the balance invariant
that size (u)(2=3)size (u:parent ). The add(x) and remove (x) operations
are identical to the standard BinarySearchTree operations, except that
any time the balance invariant is violated at a node u, the subtree rooted
atu:parent is rebuilt. Your analysis should show that operations on a
WeightBalancedTree run inO(logn) amortized time.
Exercise 8.9. Analyze and implement a CountdownTree . In a Countdown-
Tree each node ukeeps a timer u:t. The add(x) and remove (x) opera-
tions are exactly the same as in a standard BinarySearchTree except that,
whenever one of these operations a ﬀectsu’s subtree, u:tis decremented.
When u:t= 0 the entire subtree rooted at uis rebuilt into a perfectly
balanced binary search tree. When a node uis involved in a rebuilding
operation (either because uis rebuilt or one of u’s ancestors is rebuilt) u:t
is reset to size (u)=3.
Your analysis should show that operations on a CountdownTree run in
O(logn) amortized time. (Hint: First show that each node usatisﬁes some
version of a balance invariant.)
Exercise 8.10. Analyze and implement a DynamiteTree . In a Dynamite-
Tree each node ukeeps tracks of the size of the subtree rooted at uin
a variable u:size . The add(x) and remove (x) operations are exactly the
same as in a standard BinarySearchTree except that, whenever one of
these operations a ﬀects a node u’s subtree, uexplodes with probability
1=u:size . When uexplodes, its entire subtree is rebuilt into a perfectly
balanced binary search tree.
183

（中文关键词：数组、链表、二叉搜索树、替罪羊树、二叉树、树、概率、摊还分析、复杂度分析）
