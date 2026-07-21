---
structure:
source: open/ods_p280.md
page: 280
---

# ODS p280: §13.1 Data Structures for Integers

§13.1 Data Structures for Integers
01234567891011121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 10⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆100⋆101⋆110⋆111⋆
Figure 13.1: The integers stored in a binary trie are encoded as root-to-leaf paths.
the method in:intValue (x) converts xto its associated integer. In the text,
however, we will simply treat xas if it is an integer.
13.1 BinaryTrie : A digital search tree
ABinaryTrie encodes a set of wbit integers in a binary tree. All leaves in
the tree have depth wand each integer is encoded as a root-to-leaf path.
The path for the integer xturns left at level iif the ith most signiﬁcant
bit of xis a 0 and turns right if it is a 1. Figure 13.1 shows an example
for the case w= 4, in which the trie stores the integers 3(0011), 9(1001),
12(1100), and 13(1101).
Because the search path for a value xdepends on the bits of x, it
will be helpful to name the children of a node, u,u:child [0] (left ) and
u:child [1] (right ). These child pointers will actually serve double-duty.
Since the leaves in a binary trie have no children, the pointers are used to
string the leaves together into a doubly-linked list. For a leaf in the bi-
nary trie u:child [0] (prev ) is the node that comes before uin the list and
u:child [1] (next ) is the node that follows uin the list. A special node,
dummy , is used both before the ﬁrst node and after the last node in the list
(see Section 3.2).
Each node, u, also contains an additional pointer u:jump . If u’s left
266

（中文关键词：链表、双向链表、二叉树、树）
