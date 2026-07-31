---
structure: 
source: book/ods_13_2_xfasttrie-searching-in-doubly-logarithmic-time.md
chapter: 13. Data Structures for Integers
section: 13.2
page: 286
kind: textbook
---

# 13.2 XFastTrie: Searching in Doubly-Logarithmic Time

## XFastTrie: Searching in Doubly-Logarithmic Time (1/2)

The performance of the BinaryTrie structure is not very impressive. The
number of elements, n, stored in the structure is at most 2w, so log n w.
≤
In other words, any of the comparison-based SSet structures described
in other parts of this book are at least as efficient as a BinaryTrie, and
are not restricted to only storing integers.
Next we describe the XFastTrie, which is just a BinaryTrie with w + 1
hash tables—one for each level of the trie. These hash tables are used to
speed up the find(x) operation to O(log w) time. Recall that the find(x)
operation in a BinaryTrie is almost complete once we reach a node, u,
where the search path for x would like to proceed to u.right (or u.left)
but u has no right (respectively, left) child. At this point, the search uses
u.jump to jump to a leaf, v, of the BinaryTrie and either return v or its
successor in the linked list of leaves. An XFastTrie speeds up the search
process by using binary search on the levels of the trie to locate the node
u.
To use binary search, we need a way to determine if the node u we
are looking for is above a particular level, i, of if u is at or below level
i. This information is given by the highest-order i bits in the binary
representation of x; these bits determine the search path that x takes from
the root to level i. For an example, refer to Figure 13.6; in this figure the
last node, u, on search path for 14 (whose binary representation is 1110)
is the node labelled 11(cid:63)(cid:63) at level 2 because there is no node labelled 111(cid:63)
at level 3. Thus, we can label each node at level i with an i-bit integer.
Then, the node u we are searching for would be at or below level i if and
only if there is a node at level i whose label matches the highest-order i
? ? ? ? 0
1
0? ? ? 1? ? ? 1
1
00?? 01?? 10?? 11?? 2
1
000? 001? 010? 011? 100? 101? 110? 111? 3
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 4
Figure 13.6: Since there is no node labelled 111(cid:63), the search path for 14 (1110)
ends at the node labelled 11(cid:63)(cid:63) .
bits of x.
In an XFastTrie, we store, for each i 0, . . . , w , all the nodes at level
∈ { }
i in a USet, t[i], that is implemented as a hash table (Chapter 5). Using
this USet allows us to check in constant expected time if there is a node
at level i whose label matches the highest-order i bits of x. In fact, we
can even find this node using t[i].find(x>>>(w i))
−
The hash tables t[0], . . . , t[w] allow us to use binary search to find u.

（中文关键词：字典树、哈希表、链表）

## XFastTrie: Searching in Doubly-Logarithmic Time (2/2)

Initially, we know that u is at some level i with 0 i < w + 1. We therefore
≤
initialize l = 0 and h = w + 1 and repeatedly look at the hash table t[i],
where i = (l + h)/2 . If t[i] contains a node whose label matches x’s
(cid:98) (cid:99)
highest-order i bits then we set l = i (u is at or below level i); otherwise
we set h = i (u is above level i). This process terminates when h l 1,
− ≤
in which case we determine that u is at level l. We then complete the
find(x) operation using u.jump and the doubly-linked list of leaves.
XFastTrie
T find(T x) {
int l = 0, h = w+1, ix = it.intValue(x);
Node v, u = r, q = newNode();
while (h-l > 1) {
int i = (l+h)/2;
q.prefix = ix >>> w-i;
if ((v = t[i].find(q)) == null) {
h = i;
} else {
u = v;
l = i;
}
}
if (l == w) return u.x;
Node pred = (((ix >>> w-l-1) & 1) == 1)
? u.jump : u.jump.child[0];
return (pred.child[next] == dummy)
? null : pred.child[next].x;
}
Each iteration of the while loop in the above method decreases h l
−
by roughly a factor of two, so this loop finds u after O(log w) iterations.
Each iteration performs a constant amount of work and one find(x) op-
eration in a USet, which takes a constant expected amount of time. The
remaining work takes only constant time, so the find(x) method in an
XFastTrie takes only O(log w) expected time.
The add(x) and remove(x) methods for an XFastTrie are almost iden-
tical to the same methods in a BinaryTrie. The only modifications are
for managing the hash tables t[0],. . . ,t[w]. During the add(x) operation,
when a new node is created at level i, this node is added to t[i]. During
a remove(x) operation, when a node is removed form level i, this node
is removed from t[i]. Since adding and removing from a hash table take
constant expected time, this does not increase the running times of add(x)
and remove(x) by more than a constant factor. We omit a code listing for
add(x) and remove(x) since the code is almost identical to the (long) code
listing already provided for the same methods in a BinaryTrie.
The following theorem summarizes the performance of an XFastTrie:
Theorem 13.2. An XFastTrie implements the SSet interface for w-bit inte-
gers. An XFastTrie supports the operations
• add(x) and remove(x) in O(w) expected time per operation and
• find(x) in O(log w) expected time per operation.
The space used by an XFastTrie that stores n values is O(n w).
·

（中文关键词：字典树、哈希表、双向链表、链表）
