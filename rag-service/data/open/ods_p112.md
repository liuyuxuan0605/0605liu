---
structure:
source: open/ods_p112.md
page: 112
---

# ODS p112: §4.4 Skiplists

§4.4 Skiplists
int j = -1; // index of node u
while (r >= 0) {
while (u.next[r] != null && j+u.length[r] < i) {
j += u.length[r];
u = u.next[r];
}
u.length[r]--; // for the node we are removing
if (j + u.length[r] + 1 == i && u.next[r] != null) {
x = u.next[r].x;
u.length[r] += u.next[r].length[r];
u.next[r] = u.next[r].next[r];
if (u == sentinel && u.next[r] == null)
h--;
}
r--;
}
n--;
return x;
}
4.3.1 Summary
The following theorem summarizes the performance of the Skiplist-
List data structure:
Theorem 4.2. ASkiplistList implements the List interface. A Skip-
listList supports the operations get(i),set(i;x),add(i;x), and remove (i)
inO(logn)expected time per operation.
4.4 Analysis of Skiplists
In this section, we analyze the expected height, size, and length of the
search path in a skiplist. This section requires a background in basic
probability. Several proofs are based on the following basic observation
about coin tosses.
Lemma 4.2. LetTbe the number of times a fair coin is tossed up to and
including the ﬁrst time the coin comes up heads. Then E[T] = 2 .
98

（中文关键词：跳表、概率、复杂度分析）
