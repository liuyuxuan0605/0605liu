---
structure:
source: open/ods_p195.md
page: 195
---

# ODS p195: Discussion and Exercises §8.2

Discussion and Exercises §8.2
Theorem 8.1. AScapegoatTree implements the SSet interface. Ignoring
the cost of rebuild (u)operations, a ScapegoatTree supports the operations
add(x),remove (x), and find (x)inO(logn)time per operation.
Furthermore, beginning with an empty ScapegoatTree , any sequence of
madd(x)andremove (x)operations results in a total of O(mlogm)time spent
during all calls to rebuild (u).
8.2 Discussion and Exercises
The term scapegoat tree is due to Galperin and Rivest [33], who deﬁne and
analyze these trees. However, the same structure was discovered earlier
by Andersson [5, 7], who called them general balanced trees since they can
have any shape as long as their height is small.
Experimenting with the ScapegoatTree implementation will reveal
that it is often considerably slower than the other SSet implementations
in this book. This may be somewhat surprising, since height bound of
log3=2q1:709log n+O(1)
is better than the expected length of a search path in a Skiplist and not
too far from that of a Treap . The implementation could be optimized by
storing the sizes of subtrees explicitly at each node or by reusing already
computed subtree sizes (Exercises 8.5 and 8.6). Even with these optimiza-
tions, there will always be sequences of add(x) and delete (x) operation
for which a ScapegoatTree takes longer than other SSet implementa-
tions.
This gap in performance is due to the fact that, unlike the other SSet
implementations discussed in this book, a ScapegoatTree can spend a lot
of time restructuring itself. Exercise 8.3 asks you to prove that there are
sequences of noperations in which a ScapegoatTree will spend on the or-
der of nlogntime in calls to rebuild (u). This is in contrast to other SSet
implementations discussed in this book, which only make O(n) structural
changes during a sequence of noperations. This is, unfortunately, a nec-
essary consequence of the fact that a ScapegoatTree does all its restruc-
turing by calls to rebuild (u) [20].
Despite their lack of performance, there are applications in which a
181

（中文关键词：跳表、替罪羊树、树）
