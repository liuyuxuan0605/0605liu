---
structure:
source: open/ods_p114.md
page: 114
---

# ODS p114: §4.4 Skiplists

§4.4 Skiplists
The height, h, of the skiplist is then given by
h=1X
i=1Ir:
Note thatIris never more than the length, jLrj, ofLr, so
E[Ir]E[jLrj] =n=2r:
Therefore, we have
E[h] = E2
6666641X
r=1Ir3
777775
=1X
r=1E[Ir]
=blogncX
r=1E[Ir] +1X
r=blognc+1E[Ir]
blogncX
r=11 +1X
r=blognc+1n=2r
logn+1X
r=01=2r
= log n+ 2:
Lemma 4.5. The expected number of nodes in a skiplist containing nele-
ments, including all occurrences of the sentinel, is 2n+O(logn).
Proof. By Lemma 4.3, the expected number of nodes, not including the
sentinel, is 2 n. The number of occurrences of the sentinel is equal to
the height, h, of the skiplist so, by Lemma 4.4 the expected number of
occurrences of the sentinel is at most log n+ 2 =O(logn).
Lemma 4.6. The expected length of a search path in a skiplist is at most
2log n+O(1).
Proof. The easiest way to see this is to consider the reverse search path for
a node, x. This path starts at the predecessor of xinL0. At any point in
100

（中文关键词：跳表）
