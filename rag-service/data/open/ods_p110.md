---
structure:
source: open/ods_p110.md
page: 110
---

# ODS p110: §4.3 Skiplists

§4.3 Skiplists
0 1 2 3 4 5 6
sentinelx
add(4,x)1 1 1 1 12 1 1 1 13335 65 6
1
1
1 1 1 12 112 123 2
11
Figure 4.6: Adding an element to a SkiplistList .
j/lscriptu
ju w
ii−j /lscript+ 1−(i−j)/lscript+ 1z
z
Figure 4.7: Updating the lengths of edges while splicing a node winto a skiplist.
This sounds more complicated than it is, for the code is actually quite
simple:
SkiplistList
void add(int i, T x) {
Node w = new Node(x, pickHeight());
if (w.height() > h)
h = w.height();
add(i, w);
}
SkiplistList
Node add(int i, Node w) {
Node u = sentinel;
int k = w.height();
int r = h;
int j = -1; // index of u
while (r >= 0) {
96

（中文关键词：跳表）
