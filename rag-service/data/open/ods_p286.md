---
structure:
source: open/ods_p286.md
page: 286
---

# ODS p286: §13.2 Data Structures for Integers

§13.2 Data Structures for Integers
return true;
}
Theorem 13.1. ABinaryTrie implements the SSet interface for w-bit inte-
gers. A BinaryTrie supports the operations add(x),remove (x), and find (x)
inO(w)time per operation. The space used by a BinaryTrie that stores n
values isO(nw).
13.2 XFastTrie : Searching in Doubly-Logarithmic Time
The performance of the BinaryTrie structure is not very impressive. The
number of elements, n, stored in the structure is at most 2w, so log nw.
In other words, any of the comparison-based SSet structures described
in other parts of this book are at least as e ﬃcient as a BinaryTrie , and
are not restricted to only storing integers.
Next we describe the XFastTrie , which is just a BinaryTrie with w+1
hash tables—one for each level of the trie. These hash tables are used to
speed up the find (x) operation to O(logw) time. Recall that the find (x)
operation in a BinaryTrie is almost complete once we reach a node, u,
where the search path for xwould like to proceed to u:right (oru:left )
butuhas no right (respectively, left) child. At this point, the search uses
u:jump to jump to a leaf, v, of the BinaryTrie and either return vor its
successor in the linked list of leaves. An XFastTrie speeds up the search
process by using binary search on the levels of the trie to locate the node
u.
To use binary search, we need a way to determine if the node uwe
are looking for is above a particular level, i, of if uis at or below level
i. This information is given by the highest-order ibits in the binary
representation of x; these bits determine the search path that xtakes from
the root to level i. For an example, refer to Figure 13.6; in this ﬁgure the
last node, u, on search path for 14 (whose binary representation is 1110)
is the node labelled 11 ??at level 2 because there is no node labelled 111 ?
at level 3. Thus, we can label each node at level iwith an i-bit integer.
Then, the node uwe are searching for would be at or below level iif and
only if there is a node at level iwhose label matches the highest-order i
272

（中文关键词：链表、哈希表、哈希）
