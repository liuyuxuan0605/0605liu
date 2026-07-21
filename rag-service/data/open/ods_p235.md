---
structure:
source: open/ods_p235.md
page: 235
---

# ODS p235: MeldableHeap : A Randomized Meldable Heap §10.2

MeldableHeap : A Randomized Meldable Heap §10.2
Information Theoretic Proof of Lemma 10.1. Letdidenote the depth of the
ith external node and recall that a binary tree with nnodes has n+1exter-
nal nodes. The probability of the random walk reaching the ith external
node is exactly pi= 1=2di, so the expected length of the random walk is
given by
H=nX
i=0pidi=nX
i=0pilog
2di
=nX
i=0pilog(1=pi)
The right hand side of this equation is easily recognizable as the entropy
of a probability distribution over n+ 1 elements. A basic fact about the
entropy of a distribution over n+ 1 elements is that it does not exceed
log(n+ 1), which proves the lemma.
With this result on random walks, we can now easily prove that the
running time of the merge (h1;h2) operation is O(logn).
Lemma 10.2. Ifh1andh2are the roots of two heaps containing n1andn2
nodes, respectively, then the expected running time of merge (h1;h2)is at most
O(logn), where n=n1+n2.
Proof. Each step of the merge algorithm takes one step of a random walk,
either in the heap rooted at h1or the heap rooted at h2. The algorithm
terminates when either of these two random walks fall out of its corre-
sponding tree (when h1=null orh2=null ). Therefore, the expected
number of steps performed by the merge algorithm is at most
log(n1+ 1) + log( n2+ 1)2log n:
10.2.2 Summary
The following theorem summarizes the performance of a MeldableHeap :
Theorem 10.2. AMeldableHeap implements the (priority) Queue interface.
AMeldableHeap supports the operations add(x)andremove ()inO(logn)
expected time per operation.
221

（中文关键词：队列、堆、二叉树、树、概率、随机）
