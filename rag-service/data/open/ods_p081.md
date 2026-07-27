---
structure:
source: open/ods_p081.md
page: 81
---

# ODS p81: DLList : A Doubly-Linked List §3.2

DLList : A Doubly-Linked List §3.2
a b c d edummy
Figure 3.2: A DLList containing a,b,c,d,e.
3.2 DLList : A Doubly-Linked List
ADLList (doubly-linked list) is very similar to an SLList except that each
node uin aDLList has references to both the node u:next that follows it
and the node u:prev that precedes it.
DLList
class Node {
T x;
Node prev, next;
}
When implementing an SLList , we saw that there were always several
special cases to worry about. For example, removing the last element
from an SLList or adding an element to an empty SLList requires care
to ensure that head and tail are correctly updated. In a DLList , the
number of these special cases increases considerably. Perhaps the cleanest
way to take care of all these special cases in a DLList is to introduce a
dummy node. This is a node that does not contain any data, but acts as a
placeholder so that there are no special nodes; every node has both a next
and a prev , with dummy acting as the node that follows the last node in the
list and that precedes the ﬁrst node in the list. In this way, the nodes of
the list are (doubly-)linked into a cycle, as illustrated in Figure 3.2.
DLList
int n;
Node dummy;
DLList() {
dummy = new Node();
67

（中文关键词：链表、双向链表）
