---
structure:
source: open/ods_p098.md
page: 98
---

# ODS p98: §3.4 Linked Lists

§3.4 Linked Lists
then after calling l1:absorb (l2),l1will contain a;b;c;d;e;f andl2will
be empty.
Exercise 3.11. Write a method deal () that removes all the elements with
odd-numbered indices from a DLList and return a DLList containing
these elements. For example, if l1, contains the elements a;b;c;d;e;f ,
then after calling l1:deal (),l1should contain a;c;e and a list containing
b;d;f should be returned.
Exercise 3.12. Write a method, reverse (), that reverses the order of ele-
ments in a DLList .
Exercise 3.13. This exercise walks you through an implementation of the
merge-sort algorithm for sorting a DLList , as discussed in Section 11.1.1.
In your implementation, perform comparisons between elements using
thecompareTo (x) method so that the resulting implementation can sort
anyDLList containing elements that implement the Comparable inter-
face.
1. Write a DLList method called takeFirst (l2). This method takes
the ﬁrst node from l2and appends it to the the receiving list. This
is equivalent to add(size ();l2:remove (0)), except that it should not
create a new node.
2. Write a DLList static method, merge (l1;l2), that takes two sorted
lists l1andl2, merges them, and returns a new sorted list contain-
ing the result. This causes l1andl2to be emptied in the proces.
For example, if l1containsa;c;d and l2containsb;e;f , then this
method returns a new list containing a;b;c;d;e;f .
3. Write a DLList method sort () that sorts the elements contained in
the list using the merge sort algorithm. This recursive algorithm
works in the following way:
(a) If the list contains 0 or 1 elements then there is nothing to do.
Otherwise,
(b) Using the truncate (size ()=2) method, split the list into two
lists of approximately equal length, l1andl2;
(c) Recursively sort l1;
84

（中文关键词：链表、排序）
