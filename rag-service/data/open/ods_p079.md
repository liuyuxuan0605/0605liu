---
structure:
source: open/ods_p079.md
page: 79
---

# ODS p79: SLList : A Singly-Linked List §3.1

SLList : A Singly-Linked List §3.1
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
Thepop() operation, after checking that the SLList is not empty, re-
moves the head by setting head =head:next and decrementing n. A spe-
cial case occurs when the last element is being removed, in which case
tail is set to null :
SLList
T pop() {
if (n == 0) return null;
T x = head.x;
head = head.next;
if (--n == 0) tail = null;
return x;
}
Clearly, both the push (x) and pop() operations run in O(1) time.
3.1.1 Queue Operations
AnSLList can also implement the FIFO queue operations add(x) and
remove () in constant time. Removals are done from the head of the list,
and are identical to the pop() operation:
SLList
T remove() {
if (n == 0) return null;
T x = head.x;
head = head.next;
65

（中文关键词：链表、队列）
