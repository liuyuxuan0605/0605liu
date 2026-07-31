---
structure: AVLTree
source: book/ods_8_1_scapegoattree-a-binary-search-tree-with-partial-rebuilding.md
chapter: 8. Scapegoat Trees
section: 8.1
page: 188
kind: textbook
---

# 8.1 ScapegoatTree: A Binary Search Tree with Partial Rebuilding

## ScapegoatTree: A Binary Search Tree with Partial Rebuilding (1/2)

A ScapegoatTree is a BinarySearchTree that, in addition to keeping
track of the number, n, of nodes in the tree also keeps a counter, q, that
maintains an upper-bound on the number of nodes.
ScapegoatTree
int q;
7
6 8
5 9
2
1 4
0 3
Figure 8.1: A ScapegoatTree with 10 nodes and height 5.
At all times, n and q obey the following inequalities:
q/2 n q .
≤ ≤
In addition, a ScapegoatTree has logarithmic height; at all times, the
height of the scapegoat tree does not exceed:
log q log 2n < log n + 2 . (8.1)
3/2 ≤ 3/2 3/2
Even with this constraint, a ScapegoatTree can look surprisingly unbal-
anced. The tree in Figure 8.1 has q = n = 10 and height 5 < log 10
3/2 ≈
5.679.
Implementing the find(x) operation in a ScapegoatTree is done us-
ing the standard algorithm for searching in a BinarySearchTree (see Sec-
tion 6.2). This takes time proportional to the height of the tree which, by
(8.1) is O(log n).
To implement the add(x) operation, we first increment n and q and
then use the usual algorithm for adding x to a binary search tree; we
search for x and then add a new leaf u with u.x = x. At this point, we may
get lucky and the depth of u might not exceed log q. If so, then we leave
3/2
well enough alone and don’t do anything else.
Unfortunately, it will sometimes happen that depth(u) > log q. In
3/2
this case, we need to reduce the height. This isn’t a big job; there is only
one node, namely u, whose depth exceeds log q. To fix u, we walk from
3/2
u back up to the root looking for a scapegoat, w. The scapegoat, w, is a very
unbalanced node. It has the property that
size(w.child) 2
> , (8.2)
size(w) 3
where w.child is the child of w on the path from the root to u. We’ll very
shortly prove that a scapegoat exists. For now, we can take it for granted.
Once we’ve found the scapegoat w, we completely destroy the subtree
rooted at w and rebuild it into a perfectly balanced binary search tree. We
know, from (8.2), that, even before the addition of u, w’s subtree was not a
complete binary tree. Therefore, when we rebuild w, the height decreases
by at least 1 so that height of the ScapegoatTree is once again at most
log q.

（中文关键词：树、替罪羊树、二叉搜索树、二叉树）

## ScapegoatTree: A Binary Search Tree with Partial Rebuilding (2/2)

3/2
ScapegoatTree
boolean add(T x) {
// first do basic insertion keeping track of depth
Node<T> u = newNode(x);
int d = addWithDepth(u);
if (d > log32(q)) {
// depth exceeded, find scapegoat
Node<T> w = u.parent;
while (3*size(w) <= 2*size(w.parent))
w = w.parent;
rebuild(w.parent);
}
return d >= 0;
}
If we ignore the cost of finding the scapegoat w and rebuilding the
subtree rooted at w, then the running time of add(x) is dominated by the
initial search, which takes O(log q) = O(log n) time. We will account for
the cost of finding the scapegoat and rebuilding using amortized analysis
in the next section.
The implementation of remove(x) in a ScapegoatTree is very simple.
We search for x and remove it using the usual algorithm for removing a
node from a BinarySearchTree. (Note that this can never increase the
7 7
6 8 6 8
5 6 > 2 9 3 9
7 3
2 3 1 4
6
1 4 2 0 2 3.5 5
3
0 3 1
2
3.5
Figure 8.2: Inserting 3.5 into a ScapegoatTree increases its height to 6, which vio-
lates (8.1) since 6 > log 11 5.914. A scapegoat is found at the node containing
3/2 ≈
5.
height of the tree.) Next, we decrement n, but leave q unchanged. Finally,
we check if q > 2n and, if so, then we rebuild the entire tree into a perfectly
balanced binary search tree and set q = n.
ScapegoatTree
boolean remove(T x) {
if (super.remove(x)) {
if (2*n < q) {
rebuild(r);
q = n;
}
return true;
}
return false;
}
Again, if we ignore the cost of rebuilding, the running time of the
remove(x) operation is proportional to the height of the tree, and is there-
fore O(log n).

（中文关键词：树、替罪羊树、二叉搜索树、摊还分析）

## 8.1.1 Analysis of Correctness and Running-Time (1/2)

In this section, we analyze the correctness and amortized running time of
operations on a ScapegoatTree. We first prove the correctness by show-
ing that, when the add(x) operation results in a node that violates Condi-
tion (8.1), then we can always find a scapegoat:
Lemma 8.1. Let u be a node of depth h > log q in a ScapegoatTree. Then
3/2
there exists a node w on the path from u to the root such that
size(w)
> 2/3 .
size(parent(w))
Proof. Suppose, for the sake of contradiction, that this is not the case, and
size(w)
2/3 .
size(parent(w)) ≤
for all nodes w on the path from u to the root. Denote the path from the
root to u as r = u , . . . , u = u. Then, we have size(u ) = n, size(u ) 2 n,
0 h 0 1 ≤ 3
size(u ) 4 n and, more generally,
2 ≤ 9
2 i
size(u ) n .
i ≤ 3
(cid:18) (cid:19)
But this gives a contradiction, since size(u) 1, hence
≥
2 h 2 log 3/2 q 2 log 3/2 n 1
1 size(u) n < n n = n = 1 .
≤ ≤ 3 3 ≤ 3 n
(cid:18) (cid:19) (cid:18) (cid:19) (cid:18) (cid:19) (cid:18) (cid:19)
Next, we analyze the parts of the running time that are not yet ac-
counted for. There are two parts: The cost of calls to size(u) when search-
ing for scapegoat nodes, and the cost of calls to rebuild(w) when we find
a scapegoat w. The cost of calls to size(u) can be related to the cost of
calls to rebuild(w), as follows:
Lemma 8.2. During a call to add(x) in a ScapegoatTree, the cost of finding
the scapegoat w and rebuilding the subtree rooted at w is O(size(w)).
Proof. The cost of rebuilding the scapegoat node w, once we find it, is
O(size(w)). When searching for the scapegoat node, we call size(u) on a
sequence of nodes u , . . . , u until we find the scapegoat u = w. However,
0 k k
since u is the first node in this sequence that is a scapegoat, we know that
k
2
size(u ) < size(u )
i 3 i+1
for all i 0, . . . , k 2 . Therefore, the cost of all calls to size(u) is
∈ { − }
k k 1
−
O size(u ) = O size(u ) + size(u )
k i k k i 1
 −   − − 
i=0 i=0
 (cid:88)   (cid:88)
k − 1 2 i

= O size(u ) + size(u )
k 3 k
 
 (cid:88) i=0
k
(cid:18)
− 1
(cid:19)
2 i

= O size(u ) 1 +
k 3
  
= O(

size(u
k
))

= O(
(cid:88) i
s
=
i
0
z
(cid:18)
e(
(cid:19)
w)

)

,
where the last line follows from the fact that the sum is a geometrically
decreasing series.
All that remains is to prove an upper-bound on the cost of all calls to
rebuild(u) during a sequence of m operations:

（中文关键词：替罪羊树、树、摊还分析）

## 8.1.1 Analysis of Correctness and Running-Time (2/2)

Lemma 8.3. Starting with an empty ScapegoatTree any sequence of m
add(x) and remove(x) operations causes at most O(m log m) time to be used
by rebuild(u) operations.
Proof. To prove this, we will use a credit scheme. We imagine that each
node stores a number of credits. Each credit can pay for some constant, c,
units of time spent rebuilding. The scheme gives out a total of O(m log m)
credits and every call to rebuild(u) is paid for with credits stored at u.
During an insertion or deletion, we give one credit to each node on
the path to the inserted node, or deleted node, u. In this way we hand
out at most log q log m credits per operation. During a deletion we
3/2 ≤ 3/2
also store an additional credit “on the side.” Thus, in total we give out at
most O(m log m) credits. All that remains is to show that these credits are
sufficient to pay for all calls to rebuild(u).
If we call rebuild(u) during an insertion, it is because u is a scapegoat.
Suppose, without loss of generality, that
size(u.left) 2
> .
size(u) 3
Using the fact that
size(u) = 1 + size(u.left) + size(u.right)
we deduce that
1
size(u.left) > size(u.right)
2
and therefore
1 1
size(u.left) size(u.right) > size(u.left) > size(u) .
− 2 3
Now, the last time a subtree containing u was rebuilt (or when u was
inserted, if a subtree containing u was never rebuilt), we had
size(u.left) size(u.right) 1 .
− ≤
Therefore, the number of add(x) or remove(x) operations that have af-
fected u.left or u.right since then is at least
1
size(u) 1 .
3 −
and there are therefore at least this many credits stored at u that are avail-
able to pay for the O(size(u)) time it takes to call rebuild(u).
If we call rebuild(u) during a deletion, it is because q > 2n. In this
case, we have q n > n credits stored “on the side,” and we use these
−
to pay for the O(n) time it takes to rebuild the root. This completes the
proof.

（中文关键词：树、替罪羊树）

## 8.1.2 Summary

The following theorem summarizes the performance of the Scapegoat-
Tree data structure:
Theorem 8.1. A ScapegoatTree implements the SSet interface. Ignoring
the cost of rebuild(u) operations, a ScapegoatTree supports the operations
add(x), remove(x), and find(x) in O(log n) time per operation.
Furthermore, beginning with an empty ScapegoatTree, any sequence of
m add(x) and remove(x) operations results in a total of O(m log m) time spent
during all calls to rebuild(u).

（中文关键词：替罪羊树、树）
