---
structure:
source: open/ods_p285.md
page: 285
---

# ODS p285: BinaryTrie : A digital search tree §13.1

BinaryTrie : A digital search tree §13.1
1010⋆⋆
9100⋆
012345678 11121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆ 101⋆110⋆111⋆
Figure 13.5: Removing the value 9 from the BinaryTrie in Figure 13.2.
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) return false;
u = u.child[c];
}
// 2 - remove u from linked list
u.child[prev].child[next] = u.child[next];
u.child[next].child[prev] = u.child[prev];
Node v = u;
// 3 - delete nodes on path to u
for (i = w-1; i >= 0; i--) {
c = (ix >>> w-i-1) & 1;
v = v.parent;
v.child[c] = null;
if (v.child[1-c] != null) break;
}
// 4 - update jump pointers
v.jump = u;
for (; i >= 0; i--) {
c = (ix >>> w-i-1) & 1;
if (v.jump == u)
v.jump = u.child[1-c];
v = v.parent;
}
n--;
271

（中文关键词：链表、树）
