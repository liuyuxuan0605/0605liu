---
structure:
source: open/ods_p301.md
page: 301
---

# ODS p301: B-Trees §14.2

B-Trees §14.2
012 45 789 111213 1516 181920 222336 14172110
Figure 14.2: A B-tree withB= 2.
An example of a B-tree withB= 2 is shown in Figure 14.2.
Note that the data stored in a B-tree node has size O(B). Therefore, in
an external memory setting, the value of Bin aB-tree is chosen so that
a node ﬁts into a single external memory block. In this way, the time
it takes to perform a B-tree operation in the external memory model is
proportional to the number of nodes that are accessed (read or written)
by the operation.
For example, if the keys are 4 byte integers and the node indices are
also 4 bytes, then setting B= 256 means that each node stores
(4 + 4)2B= 8512 = 4096
bytes of data. This would be a perfect value of Bfor the hard disk or
solid state drive discussed in the introduction to this chaper, which have
a block size of 4096 bytes.
TheBTree class, which implements a B-tree, stores a BlockStore ,bs,
that stores BTree nodes as well as the index, ri, of the root node. As
usual, an integer, n, is used to keep track of the number of items in the
data structure:
BTree
int n;
BlockStore<Node> bs;
int ri;
287

（中文关键词：B树、树）
