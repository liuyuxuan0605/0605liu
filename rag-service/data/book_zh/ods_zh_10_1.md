---
structure: MinHeap
source: book_zh/ods_zh_10_1.md
chapter: 10.1 二叉堆：一种隐式二叉树
section: 10.1
page: 225
kind: textbook
---

# 10.1 二叉堆：一种隐式二叉树

## 二叉堆：一种隐式二叉树 (1/2)

我们对（优先）队列的第一次实现基于一个已有四百多年历史的技术。
Eytzinger’s method 允许我们通过按广度优先顺序排列树的节点，将一个完
全二叉树表示为一个数组（参见第6.1.2节）。这样，根节点存储在位置0
，根节点的左子节点存储在位置1，根节点的右子节点存储在位置2，根节
点左子节点的左子节点存储在位置3，依此类推。参见图10.1。
如果我们将 Eytzinger 的方法应用于一个足够大的树，一些模式会出现
。索引为 i 的节点的左孩子在索引 left(i) =
0
1 2
3 4 5 6
7 8 9 10 11 12 13 14
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
图 10.1：Eytzinger 方法将完全二叉树表示为数组。
2i + 1，并且索引为 i 的节点的右子节点位于索引 right(i) = 2i + 2。索引为
i 的节点的父节点位于索引 parent(i) = (i 1)/2。
−
BinaryHeap
int left(int i) {
return 2*i + 1;
}
int right(int i) {
return 2*i + 2;
}
int parent(int i) {
return (i-1)/2;
}
二叉堆使用这种技术来隐式表示一个完全二叉树，其中的元素是
heap-ordered：存储在任意索引 i 的值不小于存储在索引 parent(i) 的值，根
值 i = 0 除外。因此，优先队列中最小的值存储在位置 0（根）。
在二叉堆中，n 个元素存储在一个数组 a 中：
BinaryHeap
T[] a;
int n;
实现 add(x) 操作相当直接。与所有基于数组的结构一样，我们首先检
查数组是否已满（通过检查 a.length = n），如果已满，则扩大数组 a。接
下来，我们将 x 放置在位置 a[n] 并将 n 增加。此时，剩下的就是确保我们
维护堆属性。我们通过反复将 x 与其父节点交换，直到 x 不再小于其父节
点。见图 10.2。
BinaryHeap
boolean add(T x) {
if (n + 1 > a.length) resize();
a[n++] = x;
bubbleUp(n-1);
return true;
}
void bubbleUp(int i) {
int p = parent(i);
while (i > 0 && compare(a[i], a[p]) < 0) {
swap(i,p);
i = p;
p = parent(i);
}
}
实现 remove() 操作，即从堆中移除最小值，有点棘手。我们知道最小
值的位置（在根节点），但在移除它之后，我们需要替换它，并确保保持
堆的性质。
最简单的方法是用值 a[n 1] 替换根节点，删除该值，并将 n 减 1。不
−
幸的是，现在新的根元素可能不再是最小的元素，所以需要向下移动。我
们通过反复将该元素与它的两个子节点进行比较来实现。如果它是三者中
最小的，那么我们就完成了。否则，我们将该元素与它两个子节点中较小
的那个交换，并继续进行。
BinaryHeap
T remove() {
T x = a[0];
a[0] = a[--n];
trickleDown(0);
4
9 8
17 26 50 16
19 69 32 93 55
4 9 8 17 26 50 16 19 69 32 93 55
4
9 8
17 26 50 16
19 69 32 93 55 6
4 9 8 17 26 50 16 19 69 32 93 55 6
4
9 8
17 26 6 16
19 69 32 93 55 50
4 9 8 17 26 6 16 19 69 32 93 55 50
4
9 6
17 26 8 16
19 69 32 93 55 50
4 9 6 17 26 8 16 19 69 32 93 55 50
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
图 10.2：向二叉堆添加值 6。
if (3*n < a.length) resize();
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
与其他基于数组的结构一样，我们将忽略 resize() 调用所花费的时间，
因为这些可以使用引理 2.1 中的摊销论证来计算。add(x) 和 remove() 的运
行时间取决于（隐式）二叉树的高度。幸运的是，这是一个 complete 二叉
树；除最后一层外，每一层都有可能的最大节点数。因此，如果这棵树的
高度是 h，那么它至少有 2h 个节点。换句话说
n 2h .
≥
对这个方程的两边取对数得到
h log n .
≤
因此 重申，add(x) 和 remove() 操作都运行在 O(log 中 n) 时间。

（中文关键词：堆；英文术语：MinHeap）

## 二叉堆：一种隐式二叉树 (2/2)

4
9 6
17 26 8 16
19 69 32 93 55 50
4 9 6 17 26 8 16 19 69 32 93 55 50
50
9 6
17 26 8 16
19 69 32 93 55
50 9 6 17 26 8 16 19 69 32 93 55
6
9 50
17 26 8 16
19 69 32 93 55
6 9 50 17 26 8 16 19 69 32 93 55
6
9 8
17 26 50 16
19 69 32 93 55
6 9 8 17 26 50 16 19 69 32 93 55
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
图 10.3：从二叉堆中移除最小值 4。

（英文术语：MinHeap）

## 10.1.1 总结

下列定理总结了二叉堆的性能：
定理 10.1. A 二叉堆 implements the (priority) 队列 interface.
Ignoring the cost of calls to 调整大小(), a 二叉堆 supports the operations 添
加(x) and 移除() in O(log n) time per operation.
Furthermore, beginning with an empty BinaryHeap, any sequence of m
添加(x) and 移除() operations results in a total of O(m) time spent during
all calls to 调整大小().

（中文关键词：堆；英文术语：MinHeap）
