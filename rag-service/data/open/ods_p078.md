---
structure:
source: open/ods_p078.md
page: 78
---

# ODS p78: §3.1 Linked Lists

§3.1 Linked Lists
a b c d ehead tail
a b c d eadd(x)
xhead tail
b c d eremove()
xhead tail
c d epop()
xhead tail
y c d epush(y)
xhead tail
Figure 3.1: A sequence of Queue (add(x) and remove ()) and Stack (push (x) and
pop()) operations on an SLList .
SLList
class Node {
T x;
Node next;
}
For eﬃciency, an SLList uses variables head andtail to keep track
of the ﬁrst and last node in the sequence, as well as an integer nto keep
track of the length of the sequence:
SLList
Node head;
Node tail;
int n;
A sequence of Stack andQueue operations on an SLList is illustrated
in Figure 3.1.
AnSLList can eﬃciently implement the Stack operations push () and
pop() by adding and removing elements at the head of the sequence. The
push () operation simply creates a new node uwith data value x, sets
u:next to the old head of the list and makes uthe new head of the list.
Finally, it increments nsince the size of the SLList has increased by one:
64

（中文关键词：链表、栈、队列）
