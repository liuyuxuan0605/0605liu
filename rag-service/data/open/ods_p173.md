---
structure:
source: open/ods_p173.md
page: 173
---

# ODS p173: Treap : A Randomized Binary Search Tree §7.2

Treap : A Randomized Binary Search Tree §7.2
Theorem 7.1. A random binary search tree can be constructed in O(nlogn)
time. In a random binary search tree, the find (x)operation takes O(logn)
expected time.
We should emphasize again that the expectation in Theorem 7.1 is
with respect to the random permutation used to create the random binary
search tree. In particular, it does not depend on a random choice of x; it
is true for every value of x.
7.2 Treap : A Randomized Binary Search Tree
The problem with random binary search trees is, of course, that they
are not dynamic. They don’t support the add(x) orremove (x) operations
needed to implement the SSet interface. In this section we describe a
data structure called a Treap that uses Lemma 7.1 to implement the SSet
interface.2
A node in a Treap is like a node in a BinarySearchTree in that it has
a data value, x, but it also contains a unique numerical priority ,p, that is
assigned at random:
Treap
class Node<T> extends BSTNode<Node<T>,T> {
int p;
}
In addition to being a binary search tree, the nodes in a Treap also
obey the heap property :
• (Heap Property) At every node u, except the root, u:parent:p<u:p.
In other words, each node has a priority smaller than that of its two chil-
dren. An example is shown in Figure 7.5.
The heap and binary search tree conditions together ensure that, once
the key ( x) and priority ( p) for each node are deﬁned, the shape of the
Treap is completely determined. The heap property tells us that the node
2The names Treap comes from the fact that this data structure is simultaneously a binary
search tree (Section 6.2) and a h eap(Chapter 10).
159

（中文关键词：二叉搜索树、堆、树、随机）
