---
structure: SinglyLinkedList
source: book/ods_3_1_sllist-a-singly-linked-list.md
chapter: 3. Linked Lists
section: 3.1
page: 77
kind: textbook
---

# 3.1 SLList: A Singly-Linked List

An SLList (singly-linked list) is a sequence of Nodes. Each node u stores
a data value u.x and a reference u.next to the next node in the sequence.
For the last node w in the sequence, w.next = null
head tail
a b c d e
head tail add(x)
a b c d e x
head tail remove()
b c d e x
head tail pop()
c d e x
head tail push(y)
y c d e x
Figure 3.1: A sequence of Queue (add(x) and remove()) and Stack (push(x) and
pop()) operations on an SLList.
SLList
class Node {
T x;
Node next;
}
For efficiency, an SLList uses variables head and tail to keep track
of the first and last node in the sequence, as well as an integer n to keep
track of the length of the sequence:
SLList
Node head;
Node tail;
int n;
A sequence of Stack and Queue operations on an SLList is illustrated
in Figure 3.1.
An SLList can efficiently implement the Stack operations push() and
pop() by adding and removing elements at the head of the sequence. The
push() operation simply creates a new node u with data value x, sets
u.next to the old head of the list and makes u the new head of the list.
Finally, it increments n since the size of the SLList has increased by one:
SLList
T push(T x) {
Node u = new Node();
u.x = x;
u.next = head;
head = u;
if (n == 0)
tail = u;
n++;
return x;
}
The pop() operation, after checking that the SLList is not empty, re-
moves the head by setting head = head.next and decrementing n. A spe-
cial case occurs when the last element is being removed, in which case
tail is set to null:
SLList
T pop() {
if (n == 0) return null;
T x = head.x;
head = head.next;
if (--n == 0) tail = null;
return x;
}
Clearly, both the push(x) and pop() operations run in O(1) time.

（中文关键词：栈、单向链表、链表、队列）

## 3.1.1 Queue Operations

An SLList can also implement the FIFO queue operations add(x) and
remove() in constant time. Removals are done from the head of the list,
and are identical to the pop() operation:
SLList
T remove() {
if (n == 0) return null;
T x = head.x;
head = head.next;
if (--n == 0) tail = null;
return x;
}
Additions, on the other hand, are done at the tail of the list. In most
cases, this is done by setting tail.next = u, where u is the newly created
node that contains x. However, a special case occurs when n = 0, in which
case tail = head = null. In this case, both tail and head are set to u.
SLList
boolean add(T x) {
Node u = new Node();
u.x = x;
if (n == 0) {
head = u;
} else {
tail.next = u;
}
tail = u;
n++;
return true;
}
Clearly, both add(x) and remove() take constant time.

（中文关键词：队列）

## 3.1.2 Summary

The following theorem summarizes the performance of an SLList:
Theorem 3.1. An SLList implements the Stack and (FIFO) Queue inter-
faces. The push(x), pop(), add(x) and remove() operations run in O(1) time
per operation.
An SLList nearly implements the full set of Deque operations. The
only missing operation is removing from the tail of an SLList. Removing
from the tail of an SLList is difficult because it requires updating the
value of tail so that it points to the node w that precedes tail in the
SLList; this is the node w such that w.next = tail. Unfortunately, the
only way to get to w is by traversing the SLList starting at head and taking
n 2 steps.
−
dummy
a b c d e
Figure 3.2: A DLList containing a,b,c,d,e.

（中文关键词：栈、队列、双端队列）
