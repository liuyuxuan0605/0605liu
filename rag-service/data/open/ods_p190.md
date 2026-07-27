---
structure:
source: open/ods_p190.md
page: 190
---

# ODS p190: §8.1 Scapegoat Trees

§8.1 Scapegoat Trees
one node, namely u, whose depth exceeds log3=2q. To ﬁx u, we walk from
uback up to the root looking for a scapegoat ,w. The scapegoat, w, is a very
unbalanced node. It has the property that
size (w:child )
size (w)>2
3; (8.2)
where w:child is the child of won the path from the root to u. We’ll very
shortly prove that a scapegoat exists. For now, we can take it for granted.
Once we’ve found the scapegoat w, we completely destroy the subtree
rooted at wand rebuild it into a perfectly balanced binary search tree. We
know, from (8.2), that, even before the addition of u,w’s subtree was not a
complete binary tree. Therefore, when we rebuild w, the height decreases
by at least 1 so that height of the ScapegoatTree is once again at most
log3=2q.
ScapegoatTree
boolean add(T x) {
// first do basic insertion keeping track of depth
Node<T> u = newNode(x);
int d = addWithDepth(u);
if (d > log32(q)) {
// depth exceeded, find scapegoat
Node<T> w = u.parent;
while (3 *size(w) <= 2 *size(w.parent))
w = w.parent;
rebuild(w.parent);
}
return d >= 0;
}
If we ignore the cost of ﬁnding the scapegoat wand rebuilding the
subtree rooted at w, then the running time of add(x) is dominated by the
initial search, which takes O(logq) =O(logn) time. We will account for
the cost of ﬁnding the scapegoat and rebuilding using amortized analysis
in the next section.
The implementation of remove (x) in a ScapegoatTree is very simple.
We search for xand remove it using the usual algorithm for removing a
node from a BinarySearchTree . (Note that this can never increase the
176

（中文关键词：二叉搜索树、替罪羊树、二叉树、树、摊还分析、复杂度分析）
