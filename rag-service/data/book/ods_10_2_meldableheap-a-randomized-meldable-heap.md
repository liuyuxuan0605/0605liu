---
structure: MinHeap
source: book/ods_10_2_meldableheap-a-randomized-meldable-heap.md
chapter: 10. Heaps
section: 10.2
page: 231
kind: textbook
---

# 10.2 MeldableHeap: A Randomized Meldable Heap

## MeldableHeap: A Randomized Meldable Heap (1/2)

In this section, we describe the MeldableHeap, a priority Queue imple-
mentation in which the underlying structure is also a heap-ordered bi-
nary tree. However, unlike a BinaryHeap in which the underlying binary
tree is completely defined by the number of elements, there are no re-
strictions on the shape of the binary tree that underlies a MeldableHeap;
anything goes.
The add(x) and remove() operations in a MeldableHeap are imple-
mented in terms of the merge(h1, h2) operation. This operation takes two
heap nodes h1 and h2 and merges them, returning a heap node that is the
root of a heap that contains all elements in the subtree rooted at h1 and
all elements in the subtree rooted at h2.
The nice thing about a merge(h1, h2) operation is that it can be defined
recursively. See Figure 10.4. If either h1 or h2 is nil, then we are merging
with an empty set, so we return h2 or h1, respectively. Otherwise, assume
h1.x h2.x since, if h1.x > h2.x, then we can reverse the roles of h1 and
≤
h2. Then we know that the root of the merged heap will contain h1.x, and
we can recursively merge h2 with h1.left or h1.right, as we wish. This
is where randomization comes in, and we toss a coin to decide whether to
merge h2 with h1.left or h1.right:
MeldableHeap
Node<T> merge(Node<T> h1, Node<T> h2) {
if (h1 == nil) return h2;
h1 merge(h1,h2) h2
4 19
9 8 25 20
17 26 50 16 28 89
19 55 32 93 99
⇓
4
9
merge(h1.right,h2)
17 26
8
19
19
50 16
25 20
55
28 89
32 93 99
Figure 10.4: Merging h1 and h2 is done by merging h2 with one of h1.left or
h1.right.
if (h2 == nil) return h1;
if (compare(h2.x, h1.x) < 0) return merge(h2, h1);
// now we know h1.x <= h2.x
if (rand.nextBoolean()) {
h1.left = merge(h1.left, h2);
h1.left.parent = h1;
} else {
h1.right = merge(h1.right, h2);
h1.right.parent = h1;
}
return h1;
}
In the next section, we show that merge(h1, h2) runs in O(log n) ex-
pected time, where n is the total number of elements in h1 and h2.
With access to a merge(h1, h2) operation, the add(x) operation is easy.
We create a new node u containing x and then merge u with the root of
our heap:
MeldableHeap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
r = merge(u, r);
r.parent = nil;
n++;
return true;
}
This takes O(log(n + 1)) = O(log n) expected time.
The remove() operation is similarly easy. The node we want to remove
is the root, so we just merge its two children and make the result the root:

（中文关键词：堆、可合并堆、树、优先队列、二叉树、随机化）

## MeldableHeap: A Randomized Meldable Heap (2/2)

MeldableHeap
T remove() {
T x = r.x;
r = merge(r.left, r.right);
if (r != nil) r.parent = nil;
n--;
return x;
}
Again, this takes O(log n) expected time.
Additionally, a MeldableHeap can implement many other operations
in O(log n) expected time, including:
• remove(u): remove the node u (and its key u.x) from the heap.
• absorb(h): add all the elements of the MeldableHeap h to this heap,
emptying h in the process.
Each of these operations can be implemented using a constant number of
merge(h1, h2) operations that each take O(log n) expected time.

（中文关键词：堆、可合并堆、随机化）

## 10.2.1 Analysis of merge(varh1,varh2) (1/2)

10.2.1 Analysis of merge(h1, h2)
The analysis of merge(h1, h2) is based on the analysis of a random walk in
a binary tree. A random walk in a binary tree starts at the root of the tree.
At each step in the random walk, a coin is tossed and, depending on the
result of this coin toss, the walk proceeds to the left or to the right child
of the current node. The walk ends when it falls off the tree (the current
node becomes nil).
The following lemma is somewhat remarkable because it does not de-
pend at all on the shape of the binary tree:
Lemma 10.1. The expected length of a random walk in a binary tree with n
nodes is at most log(n + 1).
Proof. The proof is by induction on n. In the base case, n = 0 and the
walk has length 0 = log(n + 1). Suppose now that the result is true for all
non-negative integers n < n.
(cid:48)
Let n denote the size of the root’s left subtree, so that n = n n 1
1 2 1
− −
is the size of the root’s right subtree. Starting at the root, the walk takes
one step and then continues in a subtree of size n or n . By our inductive
1 2
hypothesis, the expected length of the walk is then
1 1
E[W ] = 1 + log(n + 1) + log(n + 1) ,
1 2
2 2
since each of n and n are less than n. Since log is a concave function,
1 2
E[W ] is maximized when n = n = (n 1)/2. Therefore, the expected
1 2
−
number of steps taken by the random walk is
1 1
E[W ] = 1 + log(n + 1) + log(n + 1)
1 2
2 2
1 + log((n 1)/2 + 1)
≤ −
= 1 + log((n + 1)/2)
= log(n + 1) .
We make a quick digression to note that, for readers who know a little
about information theory, the proof of Lemma 10.1 can be stated in terms
of entropy.
Information Theoretic Proof of Lemma 10.1. Let d denote the depth of the
i
ith external node and recall that a binary tree with n nodes has n + 1 exter-
nal nodes. The probability of the random walk reaching the ith external
node is exactly p
i
= 1/2di , so the expected length of the random walk is
given by
n n n
H = p d = p log 2di = p log(1/p )
i i i i i
i=0 i=0 i=0
(cid:88) (cid:88) (cid:16) (cid:17) (cid:88)
The right hand side of this equation is easily recognizable as the entropy
of a probability distribution over n + 1 elements. A basic fact about the
entropy of a distribution over n + 1 elements is that it does not exceed
log(n + 1), which proves the lemma.
With this result on random walks, we can now easily prove that the
running time of the merge(h1, h2) operation is O(log n).

（中文关键词：树、二叉树、概率）

## 10.2.1 Analysis of merge(varh1,varh2) (2/2)

Lemma 10.2. If h1 and h2 are the roots of two heaps containing n and n
1 2
nodes, respectively, then the expected running time of merge(h1, h2) is at most
O(log n), where n = n + n .
1 2
Proof. Each step of the merge algorithm takes one step of a random walk,
either in the heap rooted at h1 or the heap rooted at h2. The algorithm
terminates when either of these two random walks fall out of its corre-
sponding tree (when h1 = null or h2 = null). Therefore, the expected
number of steps performed by the merge algorithm is at most
log(n + 1) + log(n + 1) 2 log n .
1 2
≤

（中文关键词：堆、树）

## 10.2.2 Summary

The following theorem summarizes the performance of a MeldableHeap:
Theorem 10.2. A MeldableHeap implements the (priority) Queue interface.
A MeldableHeap supports the operations add(x) and remove() in O(log n)
expected time per operation.

（中文关键词：可合并堆、堆、队列）
