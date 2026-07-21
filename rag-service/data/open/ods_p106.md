---
structure:
source: open/ods_p106.md
page: 106
---

# ODS p106: §4.2 Skiplists

§4.2 Skiplists
0 1 2 3 4 5 6
sentinel3.5
add(3.5)
Figure 4.3: Adding the node containing 3 :5 to a skiplist. The nodes stored in
stack are highlighted.
Removing an element, x, is done in a similar way, except that there is
no need for stack to keep track of the search path. The removal can be
done as we are following the search path. We search for xand each time
the search moves downward from a node u, we check if u:next:x=xand
if so, we splice uout of the list:
SkiplistSSet
boolean remove(T x) {
boolean removed = false;
Node<T> u = sentinel;
int r = h;
int comp = 0;
while (r >= 0) {
while (u.next[r] != null
&& (comp = compare(u.next[r].x, x)) < 0) {
u = u.next[r];
}
if (u.next[r] != null && comp == 0) {
removed = true;
u.next[r] = u.next[r].next[r];
if (u == sentinel && u.next[r] == null)
h--; // height has gone down
}
r--;
}
if (removed) n--;
return removed;
}
92

（中文关键词：跳表、栈）
