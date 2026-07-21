---
structure:
source: open/ods_p311.md
page: 311
---

# ODS p311: B-Trees §14.2

B-Trees §14.2
012 45 789 111213 1516 181920 222336 14172110
+
012 45 789 1213 1516 181920 222336 14172111
Figure 14.8: The remove (x) operation in a BTree . To remove the value x= 10 we
replace it with the the value x0= 11 and remove 11 from the leaf that contains it.
if (ui < 0) return false; // didn’t find it
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) { // found it
i = -(i+1);
if (u.isLeaf()) {
u.remove(i);
} else {
u.keys[i] = removeSmallest(u.children[i+1]);
checkUnderflow(u, i+1);
}
return true;
} else if (removeRecursive(x, u.children[i])) {
checkUnderflow(u, i);
return true;
}
return false;
}
T removeSmallest(int ui) {
Node u = bs.readBlock(ui);
if (u.isLeaf())
297

（中文关键词：B树、树）
