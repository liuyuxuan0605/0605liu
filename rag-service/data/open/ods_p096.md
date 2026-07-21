---
structure:
source: open/ods_p096.md
page: 96
---

# ODS p96: §3.4 Linked Lists

§3.4 Linked Lists
add or remove a list item and the time it takes to locate a particular list
item.
3.4 Discussion and Exercises
Both singly-linked and doubly-linked lists are established techniques,
having been used in programs for over 40 years. They are discussed,
for example, by Knuth [46, Sections 2.2.3–2.2.5]. Even the SEList data
structure seems to be a well-known data structures exercise. The SEList
is sometimes referred to as an unrolled linked list [69].
Another way to save space in a doubly-linked list is to use so-called
XOR-lists. In an XOR-list, each node, u, contains only one pointer, called
u:nextprev , that holds the bitwise exclusive-or of u:prev andu:next . The
list itself needs to store two pointers, one to the dummy node and one to
dummy:next (the ﬁrst node, or dummy if the list is empty). This technique
uses the fact that, if we have pointers to uandu:prev , then we can extract
u:next using the formula
u:next =u:prevˆu:nextprev:
(Here ˆcomputes the bitwise exclusive-or of its two arguments.) This
technique complicates the code a little and is not possible in some lan-
guages that have garbage collection—including Java—but gives a doubly-
linked list implementation that requires only one pointer per node. See
Sinha’s magazine article [70] for a detailed discussion of XOR-lists.
Exercise 3.1. Why is it not possible to use a dummy node in an SLList
to avoid all the special cases that occur in the operations push (x),pop(),
add(x), and remove ()?
Exercise 3.2. Design and implement an SLList method, secondLast (),
that returns the second-last element of an SLList . Do this without using
the member variable, n, that keeps track of the size of the list.
Exercise 3.3. Implement the List operations get(i),set(i;x),add(i;x)
andremove (i) on an SLList . Each of these operations should run in O(1+
i) time.
82

（中文关键词：链表、双向链表）
