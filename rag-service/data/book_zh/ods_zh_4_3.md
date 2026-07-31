---
structure: 
source: book_zh/ods_zh_4_3.md
chapter: 4.1 基本结构
section: 4.3
page: 107
kind: textbook
---

# 4.3 跳表列表：一种高效的随机访问列表

## 跳表列表：一种高效的随机访问列表 (1/2)

SkiplistList使用跳表结构实现了List接口。在SkiplistList中，L 包含列表中
0
按出现顺序排列的元素。与SkiplistSSet一样，元素可以在O(log n)时间内
添加、删除和访问。
为了使这成为可能，我们需要一种方法来跟踪L 中第i个元素的搜索路
0
径。实现这一点最简单的方法是定义某个列表L 中一条边的length的概念
r
。我们将L 中每条边的长度定义为1。L 中一条边e的长度，r > 0，被定义
0 r
为其下方边的长度之和L 。等价地，e的长度是它下方L 中边的数量。
r 1 0
−
见图4.5，例子中展示了跳表及其边的长度。由于跳表的边存储在数组中，
因此长度也可以以相同方式存储:
SkiplistList
class Node {
5
L5
5
L4
3 2
L3
3 1 1
L2
3 1 1 1 1
L1
1 1 1 1 1 1 1
L0 0 1 2 3 4 5 6
sentinel
图 4.5：跳表中边的长度。
T x; Node[] next; int[] length; Node(T ix, int h) { x = ix; n
ext = Array.newInstance(Node.class, h+1); length = new int[
h+1]; }int height() { return next.length - 1; } }
这种长度定义的有用性质是，如果我们当前处在 L 中位置为 j 的节点
0
，并且沿着长度为 (cid:96) 的边移动，那么我们将移动到在 L 中位置为 j + (cid:96) 的
0
节点。通过这种方式，在沿着搜索路径前进时，我们可以跟踪当前节点在
L 中的位置 j。当处在 L 中的节点 u 时，如果 j 加上边 u.next[r] 的长度小
0 r
于 i，则向右移动。否则，我们进入 L 向下移动。
r 1
−
SkiplistList 节点 findPred(int i) { 节点
u = 哨兵; int r = h; int j = -1; // 当前节点在列表 0 中的索引 while (r
>= 0) { while (u.next[r] != null && j + u.length[r] < i) { j += u.length[r]
;
u = u.next[r];
}
r--;
}
return u;
}
SkiplistList
T get(int i) {
return findPred(i).next[0].x;
}
T set(int i, T x) {
Node u = findPred(i).next[0];
T y = u.x;
u.x = x;
return y;
}
由于操作 get(i) 和 set(i, x) 最困难的部分是在 L 中找到第 i 个节点，这
0
些操作的运行时间是 O(log n)。
在 SkiplistList 的位置 i 添加一个元素相当简单。与 SkiplistSSet 不同，
我们可以确定一个新节点确实会被添加，因此我们可以在搜索新节点位置
的同时进行添加。我们首先选择新插入节点 w 的高度 k，然后按照 i 的搜
索路径进行查找。每当搜索路径从 L 向下移动，且 r k 时，我们就将 w
r
≤
插入到 L 中。唯一额外需要注意的是确保边的长度被正确更新。见图 4.6
r
。
请注意，每次搜索路径在 L 中的某个节点 u 处向下时，边 u.next[r] 的
r
长度都会增加一，因为我们在该边下的 i 位置添加了一个元素。在两个节
点 u 和 z 之间插入节点 w 的操作如图 4.7 所示。在沿搜索路径进行查找时
，我们已经在跟踪 u 在 L 中的位置 j。因此，我们知道从 u 到 w 的边的长
0
度为 i j。我们还可以根据从 u 到 z 的边的长度 (cid:96) 推导出从 w 到 z 的边的
−
长度。因此，我们可以插入 w 并在常数时间内更新边的长度。
5 6
5 6
3 2 3 2 1
3 1 1 2 1 1
3 1 1 2 1 1 1 1
1 1 1 1 1 2 1 1 1 1
0 1 2 3 x 4 5 6
sentinel add(4,x)
图 4.6：向跳表列表中添加一个元素。
u z
‘
j
‘ + 1
u w z
i j ‘ + 1 (i j)
− − −
j i
图 4.7：在将节点 w 插入跳表时更新边的长度。

（中文关键词：跳表、数组）

## 跳表列表：一种高效的随机访问列表 (2/2)

这听起来比实际复杂，但代码实际上非常简单：
SkiplistList
void add(int i, T x) {
Node w = new Node(x, pickHeight());
if (w.height() > h)
h = w.height();
add(i, w);
}
跳表列表
节点 add(int i, 节点 w) { 节点 u =
哨兵; int k = w.高度(); int r = h; int
j = -1; // u 的索引 当 (r >= 0) {
5 4
L5
5 4
L4
3 2 1
L3
1
3 1 1
L2
1
3 1 1 1 1
L1
1
1 1 1 1 1 1 1
L0 0 1 2 3 4 5 6
sentinel remove(3)
图 4.8：从跳表列表中移除一个元素。
while (u.next[r] != null && j+u.length[r] < i) { j += u.length[r]; u
= u.next[r]; }u.length[r]++; // 考虑列表中新节点 0 if (r <= k) { w.ne
xt[r] = u.next[r]; u.next[r] = w; w.length[r] = u.length[r] - (i - j); u.len
gth[r] = i - j; }r--; }n++; return u; }
到现在为止，在跳表中实现 remove(i) 操作应该很明显。我们沿着位于
位置 i 的节点的搜索路径进行操作。每次搜索路径从某个节点 u 的 r 层向
下移动时，我们就会把从 u 在该层出发的边的长度减一。我们还会检查 u.
next[r] 是否是秩为 i 的元素，如果是，则在该层将其从列表中删除。示例
如图 4.8 所示。
SkiplistList
T remove(int i) {
T x = null;
Node u = sentinel;
int r = h;
int j = -1; // 节点 u 的索引 while (r >= 0) { while (u.next[r] != null &&
j+u.length[r] < i) { j += u.length[r]; u = u.next[r]; }u.length[r]--; // 对于我
们要删除的节点 if (j + u.length[r] + 1 == i && u.next[r] != null) { x = u.
next[r].x; u.length[r] += u.next[r].length[r]; u.next[r] = u.next[r].next[r]; if
(u == sentinel && u.next[r] == null) h--; }r--; }n--; return x; }

（中文关键词：跳表）

## 4.3.1 总结

以下定理总结了跳表列表数据结构的性能：
定理 4.2. A 跳表列表 implements the 列表 interface. A 跳表列表
supports the operations 获取(i), 设置(i, x), 添加(i, x), and 移除(i) in O(对数 n
) expected time per operation.
