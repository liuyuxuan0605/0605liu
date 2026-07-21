---
structure:
source: open/ods_p174.md
page: 174
---

# ODS p174: §7.2 Random Binary Search Trees

§7.2 Random Binary Search Trees
6,420,91,6
2,993,1
5,11
4,14
7,229,17
8,49
Figure 7.5: An example of a Treap containing the integers 0 ;:::;9. Each node, u,
is illustrated as a box containing u:x;u:p.
with minimum priority has to be the root, r, of the Treap . The binary
search tree property tells us that all nodes with keys smaller than r:xare
stored in the subtree rooted at r:left and all nodes with keys larger than
r:xare stored in the subtree rooted at r:right .
The important point about the priority values in a Treap is that they
are unique and assigned at random. Because of this, there are two equiv-
alent ways we can think about a Treap . As deﬁned above, a Treap obeys
the heap and binary search tree properties. Alternatively, we can think
of aTreap as aBinarySearchTree whose nodes were added in increasing
order of priority. For example, the Treap in Figure 7.5 can be obtained by
adding the sequence of ( x;p) values
h(3;1);(1;6);(0;9);(5;11);(4;14);(9;17);(7;22);(6;42);(8;49);(2;99)i
into a BinarySearchTree .
Since the priorities are chosen randomly, this is equivalent to taking a
random permutation of the keys—in this case the permutation is
h3;1;0;5;9;4;7;6;8;2i
—and adding these to a BinarySearchTree . But this means that the
shape of a treap is identical to that of a random binary search tree. In
160

（中文关键词：二叉搜索树、堆、树、随机）
