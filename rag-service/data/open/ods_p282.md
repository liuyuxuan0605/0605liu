---
structure:
source: open/ods_p282.md
page: 282
---

# ODS p282: §13.1 Data Structures for Integers

§13.1 Data Structures for Integers
01234567891011121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 10⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆100⋆101⋆110⋆111⋆find (5) find (8)
Figure 13.3: The paths followed by find (5) and find (8).
if (i == w) return u.x; // found it
u = (c == 0) ? u.jump : u.jump.child[next];
return u == dummy ? null : u.x;
}
The running-time of the find (x) method is dominated by the time it
takes to follow a root-to-leaf path, so it runs in O(w) time.
The add(x) operation in a BinaryTrie is also fairly straightforward,
but has a lot of work to do:
1. It follows the search path for xuntil reaching a node uwhere it can
no longer proceed.
2. It creates the remainder of the search path from uto a leaf that
contains x.
3. It adds the node, u0, containing xto the linked list of leaves (it has
access to the predecessor, pred , ofu0in the linked list from the jump
pointer of the last node, u, encountered during step 1.)
4. It walks back up the search path for xadjusting jump pointers at the
nodes whose jump pointer should now point to x.
An addition is illustrated in Figure 13.4.
268

（中文关键词：链表）
