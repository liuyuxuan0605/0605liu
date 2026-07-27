---
structure:
source: open/ods_p019.md
page: 19
---

# ODS p19: Interfaces §1.2

Interfaces §1.2
x · · ·
add (x)/enqueue (x) remove ()/dequeue ()
Figure 1.1: A FIFO Queue .
1.2.1 The Queue ,Stack , and Deque Interfaces
TheQueue interface represents a collection of elements to which we can
add elements and remove the next element. More precisely, the opera-
tions supported by the Queue interface are
•add(x): add the value xto the Queue
•remove (): remove the next (previously added) value, y, from the
Queue and return y
Notice that the remove () operation takes no argument. The Queue ’squeue-
ing discipline decides which element should be removed. There are many
possible queueing disciplines, the most common of which include FIFO,
priority, and LIFO.
AFIFO (ﬁrst-in-ﬁrst-out) Queue , which is illustrated in Figure 1.1, re-
moves items in the same order they were added, much in the same way
a queue (or line-up) works when checking out at a cash register in a gro-
cery store. This is the most common kind of Queue so the qualiﬁer FIFO
is often omitted. In other texts, the add(x) and remove () operations on a
FIFO Queue are often called enqueue (x) and dequeue (), respectively.
Apriority Queue , illustrated in Figure 1.2, always removes the small-
est element from the Queue , breaking ties arbitrarily. This is similar to the
way in which patients are triaged in a hospital emergency room. As pa-
tients arrive they are evaluated and then placed in a waiting room. When
a doctor becomes available he or she ﬁrst treats the patient with the most
life-threatening condition. The remove (x) operation on a priority Queue
is usually called deleteMin () in other texts.
A very common queueing discipline is the LIFO (last-in-ﬁrst-out) dis-
cipline, illustrated in Figure 1.3. In a LIFO Queue , the most recently
added element is the next one removed. This is best visualized in terms
of a stack of plates; plates are placed on the top of the stack and also
5

（中文关键词：栈、队列、双端队列、优先队列）
