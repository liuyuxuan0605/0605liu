---
structure:
source: open/ods_p111.md
page: 111
---

# ODS p111: SkiplistList : An Eﬃcient Random-Access List §4.3

SkiplistList : An Eﬃcient Random-Access List §4.3
0 1 2 4 5 6
sentinelL0L1L2L3L4L5
1 1 1 1 13 1 133 2 15 45 4
remove(3)31 11 11 11
1
1
Figure 4.8: Removing an element from a SkiplistList .
while (u.next[r] != null && j+u.length[r] < i) {
j += u.length[r];
u = u.next[r];
}
u.length[r]++; // accounts for new node in list 0
if (r <= k) {
w.next[r] = u.next[r];
u.next[r] = w;
w.length[r] = u.length[r] - (i - j);
u.length[r] = i - j;
}
r--;
}
n++;
return u;
}
By now, the implementation of the remove (i) operation in a Skip-
listList should be obvious. We follow the search path for the node at
position i. Each time the search path takes a step down from a node, u,
at level rwe decrement the length of the edge leaving uat that level. We
also check if u:next [r] is the element of rank iand, if so, splice it out of
the list at that level. An example is shown in Figure 4.8.
SkiplistList
T remove(int i) {
T x = null;
Node u = sentinel;
int r = h;
97

（中文关键词：跳表、随机）
