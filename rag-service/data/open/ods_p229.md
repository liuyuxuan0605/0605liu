---
structure:
source: open/ods_p229.md
page: 229
---

# ODS p229: BinaryHeap : An Implicit Binary Tree §10.1

BinaryHeap : An Implicit Binary Tree §10.1
if (3 *n < a.length) resize();
return x;
}
void trickleDown(int i) {
do {
int j = -1;
int r = right(i);
if (r < n && compare(a[r], a[i]) < 0) {
int l = left(i);
if (compare(a[l], a[r]) < 0) {
j = l;
} else {
j = r;
}
} else {
int l = left(i);
if (l < n && compare(a[l], a[i]) < 0) {
j = l;
}
}
if (j >= 0) swap(i, j);
i = j;
} while (i >= 0);
}
As with other array-based structures, we will ignore the time spent
in calls to resize (), since these can be accounted for using the amortiza-
tion argument from Lemma 2.1. The running times of both add(x) and
remove () then depend on the height of the (implicit) binary tree. Luckily,
this is a complete binary tree; every level except the last has the maximum
possible number of nodes. Therefore, if the height of this tree is h, then it
has at least 2hnodes. Stated another way
n2h:
Taking logarithms on both sides of this equation gives
hlogn:
Therefore, both the add(x) and remove () operation run in O(logn) time.
215

（中文关键词：数组、堆、二叉树、树）
