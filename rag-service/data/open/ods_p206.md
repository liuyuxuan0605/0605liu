---
structure:
source: open/ods_p206.md
page: 206
---

# ODS p206: §9.2 Red-Black Trees

§9.2 Red-Black Trees
Figure 9.5: Every red-black tree has a corresponding 2-4 tree.
Lemma 9.2. The height of red-black tree with nnodes is at most 2log n.
Now that we have seen the relationship between 2-4 trees and red-
black trees, it is not hard to believe that we can e ﬃciently maintain a
red-black tree while adding and removing elements.
We have already seen that adding an element in a BinarySearchTree
can be done by adding a new leaf. Therefore, to implement add(x) in a
red-black tree we need a method of simulating splitting a node with ﬁve
children in a 2-4 tree. A 2-4 tree node with ﬁve children is represented
by a black node that has two red children, one of which also has a red
child. We can “split” this node by colouring it red and colouring its two
children black. An example of this is shown in Figure 9.6.
Similarly, implementing remove (x) requires a method of merging two
nodes and borrowing a child from a sibling. Merging two nodes is the in-
verse of a split (shown in Figure 9.6), and involves colouring two (black)
siblings red and colouring their (red) parent black. Borrowing from a sib-
ling is the most complicated of the procedures and involves both rotations
and recolouring nodes.
Of course, during all of this we must still maintain the no-red-edge
192

（中文关键词：红黑树、2-4树、树）
