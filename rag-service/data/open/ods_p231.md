---
structure:
source: open/ods_p231.md
page: 231
---

# ODS p231: MeldableHeap : A Randomized Meldable Heap §10.2

MeldableHeap : A Randomized Meldable Heap §10.2
10.1.1 Summary
The following theorem summarizes the performance of a BinaryHeap :
Theorem 10.1. ABinaryHeap implements the (priority) Queue interface.
Ignoring the cost of calls to resize (), aBinaryHeap supports the operations
add(x)andremove ()inO(logn)time per operation.
Furthermore, beginning with an empty BinaryHeap , any sequence of m
add(x)andremove ()operations results in a total of O(m)time spent during
all calls to resize ().
10.2 MeldableHeap : A Randomized Meldable Heap
In this section, we describe the MeldableHeap , a priority Queue imple-
mentation in which the underlying structure is also a heap-ordered bi-
nary tree. However, unlike a BinaryHeap in which the underlying binary
tree is completely deﬁned by the number of elements, there are no re-
strictions on the shape of the binary tree that underlies a MeldableHeap ;
anything goes.
The add(x) and remove () operations in a MeldableHeap are imple-
mented in terms of the merge (h1;h2) operation. This operation takes two
heap nodes h1andh2and merges them, returning a heap node that is the
root of a heap that contains all elements in the subtree rooted at h1and
all elements in the subtree rooted at h2.
The nice thing about a merge (h1;h2) operation is that it can be deﬁned
recursively. See Figure 10.4. If either h1orh2isnil, then we are merging
with an empty set, so we return h2orh1, respectively. Otherwise, assume
h1:xh2:xsince, if h1:x>h2:x, then we can reverse the roles of h1and
h2. Then we know that the root of the merged heap will contain h1:x, and
we can recursively merge h2with h1:left orh1:right , as we wish. This
is where randomization comes in, and we toss a coin to decide whether to
merge h2with h1:left orh1:right :
MeldableHeap
Node<T> merge(Node<T> h1, Node<T> h2) {
if (h1 == nil) return h2;
217

（中文关键词：队列、堆、二叉树、树、优先队列、随机）
