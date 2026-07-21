---
structure:
source: open/ods_p083.md
page: 83
---

# ODS p83: DLList : A Doubly-Linked List §3.2

DLList : A Doubly-Linked List §3.2
wu
· · · · · ·u.next u.prev
Figure 3.3: Adding the node ubefore the node win aDLList .
3.2.1 Adding and Removing
If we have a reference to a node win aDLList and we want to insert a node
ubefore w, then this is just a matter of setting u:next =w,u:prev =w:prev ,
and then adjusting u:prev:next andu:next:prev . (See Figure 3.3.) Thanks
to the dummy node, there is no need to worry about w:prev orw:next not
existing.
DLList
Node addBefore(Node w, T x) {
Node u = new Node();
u.x = x;
u.prev = w.prev;
u.next = w;
u.next.prev = u;
u.prev.next = u;
n++;
return u;
}
Now, the list operation add(i;x) is trivial to implement. We ﬁnd the
ith node in the DLList and insert a new node uthat contains xjust before
it.
DLList
void add(int i, T x) {
addBefore(getNode(i), x);
}
69

（中文关键词：链表、双向链表）
