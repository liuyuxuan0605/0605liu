---
structure: 
source: book_zh/ods_zh_4_2.md
chapter: 4.1 基本结构
section: 4.2
page: 104
kind: textbook
---

# 4.2 跳表集合：一种高效的集合

## 跳表集合：一种高效的集合 (1/2)

SkiplistSSet 使用跳表结构来实现 SSet 接口。当以这种方式使用时，列表
L 以排序顺序存储 SSet 的元素。find(x) 方法通过查找最小值 y 的搜索路
0
径来工作，使得 y x：
≥
SkiplistSSet
Node<T> findPredNode(T x) {
Node<T> u = sentinel;
int r = h;
while (r >= 0) {
while (u.next[r] != null && compare(u.next[r].x,x) < 0)
u = u.next[r]; // go right in list r
r--; // go down into list r-1
}
return u;
}
T find(T x) {
Node<T> u = findPredNode(x);
return u.next[0] == null ? null : u.next[0].x;
}
沿着 y 的搜索路径很容易：当位于集合 L 中的某个节点 u 时，我们向
r
右查看 u.next[r].x。如果 x > u.next[r].x，那么我们就在 L 中向右移动一步
r
；否则，我们向下进入 L 。在此搜索中每一步（向右或向下）只需常数
r 1
−
时间；因此，根据引理 4.1，find(x) 的期望运行时间是 O(log n)。
在我们向 SkipListSSet 添加元素之前，我们需要一个方法来模拟掷硬币
，以确定新节点的高度 k。我们通过选择一个随机整数 z，并计算 z 的二
进制表示中尾随 1 的数量来实现这一点：1
SkiplistSSet
int pickHeight() {
int z = rand.nextInt();
1This method does not exactly replicate the coin-tossing experiment since the value of k
will always be less than the number of bits in an int. However, this will have negligible im-
pact unless the number of elements in the structure is much greater than 232 = 4294967296.
int k = 0;
int m = 1;
while ((z & m) != 0) {
k++;
m <<= 1;
}
return k;
}
要在 SkiplistSSet 中实现 add(x) 方法，我们首先搜索 x，然后将 x 插入
到几个列表 L , ... , L 中，其中 k 是通过 pickHeight() 方法选择的。实现这
0 k
一点最简单的方法是使用一个数组 stack 来跟踪搜索路径从某个列表 L 下
r
行到 L 时经过的节点。更准确地说，stack[r] 是搜索路径下行到 L 时
r 1 r 1
− −
在 L 中的节点。我们修改以插入 x 的节点正是 stack[0] 到 stack[k]。以下
r
代码实现了 add(x) 的这一算法：
SkiplistSSet
boolean add(T x) {
Node<T> u = sentinel;
int r = h;
int comp = 0;
while (r >= 0) {
while (u.next[r] != null
&& (comp = compare(u.next[r].x,x)) < 0)
u = u.next[r];
if (u.next[r] != null && comp == 0) return false;
stack[r--] = u; // going down, store u
}
Node<T> w = new Node<T>(x, pickHeight());
while (h < w.height())
stack[++h] = sentinel; // height increased
for (int i = 0; i < w.next.length; i++) {
w.next[i] = stack[i].next[i];
stack[i].next[i] = w;
}
n++;
return true;
}
0 1 2 3 3.5 4 5 6
sentinel add(3.5)
图 4.3：将包含 3.5 的节点添加到跳表中。存储在栈中的节点已突出显示。

（中文关键词：栈、跳表）

## 跳表集合：一种高效的集合 (2/2)

移除一个元素 x 的方法类似，只是无需使用栈来跟踪搜索路径。移除
可以在我们沿着搜索路径进行时完成。我们搜索 x，每次搜索从节点 u 向
下移动时，我们检查 u.next.x = x，如果是这样，我们就将 u 从列表中剪出
：
SkiplistSSet
boolean remove(T x) {
boolean removed = false;
Node<T> u = sentinel;
int r = h;
int comp = 0;
while (r >= 0) {
while (u.next[r] != null
&& (comp = compare(u.next[r].x, x)) < 0) {
u = u.next[r];
}
if (u.next[r] != null && comp == 0) {
removed = true;
u.next[r] = u.next[r].next[r];
if (u == sentinel && u.next[r] == null)
h--; // height has gone down
}
r--;
}
if (removed) n--;
return removed;
}
0 1 2 3 4 5 6
sentinel remove(3)
图 4.4：从跳表中移除包含 3 的节点。

（中文关键词：跳表）

## 4.2.1 总结

下列定理总结了跳表在实现有序集合时的性能：
定理 4.1. SkiplistSSet implements the SSet interface. A SkiplistS- Set
supports the operations 添加(x), 移除(x), and 查找(x) in O(log n) ex-
pected time per operation.

（中文关键词：跳表）
