---
structure:
source: open/ods_p315.md
page: 315
---

# ODS p315: B-Trees §14.2

B-Trees §14.2
if (w.size() < B-1) { // underflow at w
Node v = bs.readBlock(u.children[i-1]); // v left of w
if (v.size() > B) { // w can borrow from v
shiftLR(u, i-1, v, w);
} else { // v will absorb w
merge(u, i-1, v, w);
}
}
}
void checkUnderflowZero(Node u, int i) {
Node w = bs.readBlock(u.children[i]); // w is child of u
if (w.size() < B-1) { // underflow at w
Node v = bs.readBlock(u.children[i+1]); // v right of w
if (v.size() > B) { // w can borrow from v
shiftRL(u, i, v, w);
} else { // w will absorb w
merge(u, i, w, v);
u.children[i] = w.id;
}
}
}
To summarize, the remove (x) method in a B-tree follows a root to leaf
path, removes a key x0from a leaf, u, and then performs zero or more
merge operations involving uand its ancestors, and performs at most one
borrowing operation. Since each merge and borrow operation involves
modifying only three nodes, and only O(logBn) of these operations occur,
the entire process takes O(logBn) time in the external memory model.
Again, however, each merge and borrow operation takes O(B) time in
the word-RAM model, so (for now) the most we can say about the run-
ning time required by remove (x) in the word-RAM model is that it is
O(BlogBn).
14.2.4 Amortized Analysis of B-Trees
Thus far, we have shown that
1. In the external memory model, the running time of find (x),add(x),
andremove (x) in aB-tree isO(logBn).
301

（中文关键词：B树、树、摊还分析、复杂度分析）
