---
structure:
source: open/ods_p308.md
page: 308
---

# ODS p308: §14.2 External Memory Searching

§14.2 External Memory Searching
BTree
boolean add(T x) {
Node w;
try {
w = addRecursive(x, ri);
} catch (DuplicateValueException e) {
return false;
}
if (w != null) { // root was split, make new root
Node newroot = new Node();
x = w.remove(0);
bs.writeBlock(w.id, w);
newroot.children[0] = ri;
newroot.keys[0] = x;
newroot.children[1] = w.id;
ri = newroot.id;
bs.writeBlock(ri, newroot);
}
n++;
return true;
}
The add(x) method and its helper, addRecursive (x;ui), can be ana-
lyzed in two phases:
Downward phase: During the downward phase of the recursion, before
xhas been added, they access a sequence of BTree nodes and call
findIt (a;x) on each node. As with the find (x) method, this takes
O(logBn) time in the external memory model and O(logn) time in
the word-RAM model.
Upward phase: During the upward phase of the recursion, after xhas
been added, these methods perform a sequence of at most O(logBn)
splits. Each split involves only three nodes, so this phase takes
O(logBn) time in the external memory model. However, each split
involves moving Bkeys and children from one node to another, so
in the word-RAM model, this takes O(Blogn) time.
Recall that the value of Bcan be quite large, much larger than even
logn. Therefore, in the word-RAM model, adding a value to a B-tree can
294

（中文关键词：B树、树）
