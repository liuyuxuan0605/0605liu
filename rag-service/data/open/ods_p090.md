---
structure:
source: open/ods_p090.md
page: 90
---

# ODS p90: §3.3 Linked Lists

§3.3 Linked Lists
abcd efgh ij · · · · · ·
axbc defg hi · · · · · · j
abcd efgh · · ·
axbc defg h · · ·
abcd efgh ij · · · · · ·
axbc def gh · · · ikl
· · · jkl
Figure 3.4: The three cases that occur during the addition of an item xin the
interior of an SEList . (This SEList has block size b= 3.)
exactly belements. Now u0’s block contains only belements so it
has room for us to insert x.
SEList
void add(int i, T x) {
if (i == n) {
add(x);
return;
}
Location l = getLocation(i);
Node u = l.u;
int r = 0;
while (r < b && u != dummy && u.d.size() == b+1) {
u = u.next;
r++;
}
if (r == b) { // b blocks each with b+1 elements
spread(l.u);
u = l.u;
}
76

（中文关键词：链表）
