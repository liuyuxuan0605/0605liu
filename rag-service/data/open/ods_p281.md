---
structure:
source: open/ods_p281.md
page: 281
---

# ODS p281: BinaryTrie : A digital search tree §13.1

BinaryTrie : A digital search tree §13.1
01234567891011121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 10⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆100⋆101⋆110⋆111⋆
Figure 13.2: A BinaryTrie with jump pointers shown as curved dashed edges.
child is missing, then u:jump points to the smallest leaf in u’s subtree.
Ifu’s right child is missing, then u:jump points to the largest leaf in u’s
subtree. An example of a BinaryTrie , showing jump pointers and the
doubly-linked list at the leaves, is shown in Figure 13.2.
Thefind (x) operation in a BinaryTrie is fairly straightforward. We
try to follow the search path for xin the trie. If we reach a leaf, then we
have found x. If we reach a node uwhere we cannot proceed (because
uis missing a child), then we follow u:jump , which takes us either to the
smallest leaf larger than xor the largest leaf smaller than x. Which of
these two cases occurs depends on whether uis missing its left or right
child, respectively. In the former case ( uis missing its left child), we have
found the node we want. In the latter case ( uis missing its right child),
we can use the linked list to reach the node we want. Each of these cases
is illustrated in Figure 13.3.
BinaryTrie
T find(T x) {
int i, c = 0, ix = it.intValue(x);
Node u = r;
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) break;
u = u.child[c];
}
267

（中文关键词：链表、双向链表、树）
