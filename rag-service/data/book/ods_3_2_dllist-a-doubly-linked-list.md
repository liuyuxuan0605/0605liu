---
structure: DoublyLinkedList
source: book/ods_3_2_dllist-a-doubly-linked-list.md
chapter: 3. Linked Lists
section: 3.2
page: 81
kind: textbook
---

# 3.2 DLList: A Doubly-Linked List

A DLList (doubly-linked list) is very similar to an SLList except that each
node u in a DLList has references to both the node u.next that follows it
and the node u.prev that precedes it.
DLList
class Node {
T x;
Node prev, next;
}
When implementing an SLList, we saw that there were always several
special cases to worry about. For example, removing the last element
from an SLList or adding an element to an empty SLList requires care
to ensure that head and tail are correctly updated. In a DLList, the
number of these special cases increases considerably. Perhaps the cleanest
way to take care of all these special cases in a DLList is to introduce a
dummy node. This is a node that does not contain any data, but acts as a
placeholder so that there are no special nodes; every node has both a next
and a prev, with dummy acting as the node that follows the last node in the
list and that precedes the first node in the list. In this way, the nodes of
the list are (doubly-)linked into a cycle, as illustrated in Figure 3.2.
DLList
int n;
Node dummy;
DLList() {
dummy = new Node();
dummy.next = dummy;
dummy.prev = dummy;
n = 0;
}
Finding the node with a particular index in a DLList is easy; we can
either start at the head of the list (dummy.next) and work forward, or start
at the tail of the list (dummy.prev) and work backward. This allows us to
reach the ith node in O(1 + min i, n i ) time:
{ − }
DLList
Node getNode(int i) {
Node p = null;
if (i < n / 2) {
p = dummy.next;
for (int j = 0; j < i; j++)
p = p.next;
} else {
p = dummy;
for (int j = n; j > i; j--)
p = p.prev;
}
return (p);
}
The get(i) and set(i, x) operations are now also easy. We first find
the ith node and then get or set its x value:
DLList
T get(int i) {
return getNode(i).x;
}
T set(int i, T x) {
Node u = getNode(i);
T y = u.x;
u.x = x;
return y;
}
The running time of these operations is dominated by the time it takes
to find the ith node, and is therefore O(1 + min i, n i ).
{ − }
u
u.prev u.next
w
· · · · · ·
Figure 3.3: Adding the node u before the node w in a DLList.

（中文关键词：双向链表、链表）

## 3.2.1 Adding and Removing

If we have a reference to a node w in a DLList and we want to insert a node
u before w, then this is just a matter of setting u.next = w, u.prev = w.prev,
and then adjusting u.prev.next and u.next.prev. (See Figure 3.3.) Thanks
to the dummy node, there is no need to worry about w.prev or w.next not
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
Now, the list operation add(i, x) is trivial to implement. We find the
ith node in the DLList and insert a new node u that contains x just before
it.
DLList
void add(int i, T x) {
addBefore(getNode(i), x);
}
The only non-constant part of the running time of add(i, x) is the time
it takes to find the ith node (using getNode(i)). Thus, add(i, x) runs in
O(1 + min i, n i ) time.
{ − }
Removing a node w from a DLList is easy. We only need to adjust
pointers at w.next and w.prev so that they skip over w. Again, the use of
the dummy node eliminates the need to consider any special cases:
DLList
void remove(Node w) {
w.prev.next = w.next;
w.next.prev = w.prev;
n--;
}
Now the remove(i) operation is trivial. We find the node with index i
and remove it:
DLList
T remove(int i) {
Node w = getNode(i);
remove(w);
return w.x;
}
Again, the only expensive part of this operation is finding the ith node
using getNode(i), so remove(i) runs in O(1 + min i, n i ) time.
{ − }

## 3.2.2 Summary

The following theorem summarizes the performance of a DLList:
Theorem 3.2. A DLList implements the List interface. In this implementa-
tion, the get(i), set(i, x), add(i, x) and remove(i) operations run in O(1 +
min i, n i ) time per operation.
{ − }
It is worth noting that, if we ignore the cost of the getNode(i) opera-
tion, then all operations on a DLList take constant time. Thus, the only
expensive part of operations on a DLList is finding the relevant node.
Once we have the relevant node, adding, removing, or accessing the data
at that node takes only constant time.
This is in sharp contrast to the array-based List implementations
of Chapter 2; in those implementations, the relevant array item can be
found in constant time. However, addition or removal requires shifting
elements in the array and, in general, takes non-constant time.
For this reason, linked list structures are well-suited to applications
where references to list nodes can be obtained through external means.
An example of this is the LinkedHashSet data structure found in the Java
Collections Framework, in which a set of items is stored in a doubly-
linked list and the nodes of the doubly-linked list are stored in a hash ta-
ble (discussed in Chapter 5). When elements are removed from a Linked-
HashSet, the hash table is used to find the relevant list node in constant
time and then the list node is deleted (also in constant time).

（中文关键词：链表、数组、双向链表、哈希表）
