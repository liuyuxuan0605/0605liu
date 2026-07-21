---
structure:
source: open/ods_p085.md
page: 85
---

# ODS p85: SEList : A Space-E ﬃcient Linked List §3.3

SEList : A Space-E ﬃcient Linked List §3.3
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
HashSet , the hash table is used to ﬁnd the relevant list node in constant
time and then the list node is deleted (also in constant time).
3.3 SEList : A Space-E ﬃcient Linked List
One of the drawbacks of linked lists (besides the time it takes to access
elements that are deep within the list) is their space usage. Each node in
aDLList requires an additional two references to the next and previous
nodes in the list. Two of the ﬁelds in a Node are dedicated to maintaining
the list, and only one of the ﬁelds is for storing data!
AnSEList (space-e ﬃcient list) reduces this wasted space using a sim-
ple idea: Rather than store individual elements in a DLList , we store a
block (array) containing several items. More precisely, an SEList is pa-
rameterized by a block size b. Each individual node in an SEList stores a
block that can hold up to b+1elements.
For reasons that will become clear later, it will be helpful if we can
doDeque operations on each block. The data structure that we choose for
this is a BDeque (bounded deque), derived from the ArrayDeque structure
described in Section 2.4. The BDeque diﬀers from the ArrayDeque in one
small way: When a new BDeque is created, the size of the backing array a
is ﬁxed at b+1and never grows or shrinks. The important property of a
BDeque is that it allows for the addition or removal of elements at either
the front or back in constant time. This will be useful as elements are
71

（中文关键词：数组、链表、双向链表、双端队列、哈希表、哈希）
