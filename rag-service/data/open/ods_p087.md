---
structure:
source: open/ods_p087.md
page: 87
---

# ODS p87: SEList : A Space-E ﬃcient Linked List §3.3

SEList : A Space-E ﬃcient Linked List §3.3
3.3.2 Finding Elements
The ﬁrst challenge we face with an SEList is ﬁnding the list item with a
given index i. Note that the location of an element consists of two parts:
1. The node uthat contains the block that contains the element with
index i; and
2. the index jof the element within its block.
SEList
class Location {
Node u;
int j;
Location(Node u, int j) {
this.u = u;
this.j = j;
}
}
To ﬁnd the block that contains a particular element, we proceed the
same way as we do in a DLList . We either start at the front of the list and
traverse in the forward direction, or at the back of the list and traverse
backwards until we reach the node we want. The only di ﬀerence is that,
each time we move from one node to the next, we skip over a whole block
of elements.
SEList
Location getLocation(int i) {
if (i < n/2) {
Node u = dummy.next;
while (i >= u.d.size()) {
i -= u.d.size();
u = u.next;
}
return new Location(u, i);
} else {
Node u = dummy;
int idx = n;
73

（中文关键词：链表）
