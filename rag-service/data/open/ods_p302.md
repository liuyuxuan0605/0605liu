---
structure:
source: open/ods_p302.md
page: 302
---

# ODS p302: §14.2 External Memory Searching

§14.2 External Memory Searching
012 45 789 111213 1516 181920 222336 14172110
16 .5
Figure 14.3: A successful search (for the value 4) and an unsuccessful search (for
the value 16.5) in a B-tree. Shaded nodes show where the value of zis updated
during the searches.
14.2.1 Searching
The implementation of the find (x) operation, which is illustrated in Fig-
ure 14.3, generalizes the find (x) operation in a binary search tree. The
search for xstarts at the root and uses the keys stored at a node, u, to
determine in which of u’s children the search should continue.
More speciﬁcally, at a node u, the search checks if xis stored in u:keys .
If so, xhas been found and the search is complete. Otherwise, the search
ﬁnds the smallest integer, i, such that u:keys [i]>xand continues the
search in the subtree rooted at u:children [i]. If no key in u:keys is
greater than x, then the search continues in u’s rightmost child. Just like
binary search trees, the algorithm keeps track of the most recently seen
key, z, that is larger than x. In case xis not found, zis returned as the
smallest value that is greater or equal to x.
BTree
T find(T x) {
T z = null;
int ui = ri;
while (ui >= 0) {
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) return u.keys[-(i+1)]; // found it
if (u.keys[i] != null)
z = u.keys[i];
ui = u.children[i];
}
288

（中文关键词：二叉搜索树、B树、树）
