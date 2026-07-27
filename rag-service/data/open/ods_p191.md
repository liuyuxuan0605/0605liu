---
structure:
source: open/ods_p191.md
page: 191
---

# ODS p191: balanced binary search tree and set q=n.

ScapegoatTree : A Binary Search Tree with Partial Rebuilding §8.1
012
34567
8
9
3.51
22
33
66
7>2
3
67
8
9
01
23
4
5 3.5
Figure 8.2: Inserting 3.5 into a ScapegoatTree increases its height to 6, which vio-
lates (8.1) since 6 >log3=2115:914. A scapegoat is found at the node containing
5.
height of the tree.) Next, we decrement n, but leave qunchanged. Finally,
we check if q>2nand, if so, then we rebuild the entire tree into a perfectly
balanced binary search tree and set q=n.
ScapegoatTree
boolean remove(T x) {
if (super.remove(x)) {
if (2 *n < q) {
rebuild(r);
q = n;
}
return true;
}
return false;
}
Again, if we ignore the cost of rebuilding, the running time of the
remove (x) operation is proportional to the height of the tree, and is there-
foreO(logn).
177

（中文关键词：二叉搜索树、替罪羊树、树）
