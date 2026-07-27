---
structure:
source: open/ods_p165.md
page: 165
---

# ODS p165: Discussion and Exercises §6.3

Discussion and Exercises §6.3
Exercise 6.16. If we have some BinarySearchTree and perform the op-
erations add(x) followed by remove (x) (with the same value of x) do we
necessarily return to the original tree?
Exercise 6.17. Can a remove (x) operation increase the height of any node
in aBinarySearchTree ? If so, by how much?
Exercise 6.18. Can an add(x) operation increase the height of any node
in aBinarySearchTree ? Can it increase the height of the tree? If so, by
how much?
Exercise 6.19. Design and implement a version of BinarySearchTree
in which each node, u, maintains values u:size (the size of the subtree
rooted at u),u:depth (the depth of u), and u:height (the height of the
subtree rooted at u).
These values should be maintained, even during calls to the add(x)
andremove (x) operations, but this should not increase the cost of these
operations by more than a constant factor.
151

（中文关键词：树）
