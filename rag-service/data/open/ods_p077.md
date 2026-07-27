---
structure:
source: open/ods_p077.md
page: 77
---

# ODS p77: Chapter 3

Chapter 3
Linked Lists
In this chapter, we continue to study implementations of the List inter-
face, this time using pointer-based data structures rather than arrays. The
structures in this chapter are made up of nodes that contain the list items.
Using references (pointers), the nodes are linked together into a sequence.
We ﬁrst study singly-linked lists, which can implement Stack and (FIFO)
Queue operations in constant time per operation and then move on to
doubly-linked lists, which can implement Deque operations in constant
time.
Linked lists have advantages and disadvantages when compared to
array-based implementations of the List interface. The primary disad-
vantage is that we lose the ability to access any element using get(i) or
set(i;x) in constant time. Instead, we have to walk through the list, one
element at a time, until we reach the ith element. The primary advantage
is that they are more dynamic: Given a reference to any list node u, we
can delete uor insert a node adjacent to uin constant time. This is true
no matter where uis in the list.
3.1 SLList : A Singly-Linked List
AnSLList (singly-linked list) is a sequence of Node s. Each node ustores
a data value u:xand a reference u:next to the next node in the sequence.
For the last node win the sequence, w:next =null
63

（中文关键词：数组、链表、双向链表、栈、队列、双端队列）
