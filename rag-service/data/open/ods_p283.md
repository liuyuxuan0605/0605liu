---
structure:
source: open/ods_p283.md
page: 283
---

# ODS p283: BinaryTrie : A digital search tree §13.1

BinaryTrie : A digital search tree §13.1
01234567891011121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 10⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆100⋆101⋆110⋆111⋆
Figure 13.4: Adding the values 2 and 15 to the BinaryTrie in Figure 13.2.
BinaryTrie
boolean add(T x) {
int i, c = 0, ix = it.intValue(x);
Node u = r;
// 1 - search for ix until falling out of the trie
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) break;
u = u.child[c];
}
if (i == w) return false; // already contains x - abort
Node pred = (c == right) ? u.jump : u.jump.child[0];
u.jump = null; // u will have two children shortly
// 2 - add path to ix
for (; i < w; i++) {
c = (ix >>> w-i-1) & 1;
u.child[c] = newNode();
u.child[c].parent = u;
u = u.child[c];
}
u.x = x;
// 3 - add u to linked list
u.child[prev] = pred;
u.child[next] = pred.child[next];
269

（中文关键词：链表、树）
