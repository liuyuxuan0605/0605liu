---
structure: Stack
source: book_zh/ods_zh_2_6.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.6
page: 63
kind: textbook
---

# 2.6 RootishArrayStack：一种节省空间的数组S 图钉

## RootishArrayStack：一种节省空间的数组S 图钉 (1/2)

本章中所有先前数据结构的一个缺点是，由于它们将数据存储在一个或两
个数组中，并且它们尽量避免频繁调整这些数组的大小，因此这些数组经
常不是很满。例如，在对 ArrayStack 进行 resize() 操作后，支持数组 a 只
填充了一半。更糟糕的是，有时只有 1/3 的 a 包含数据。
blocks
a b c d e f g h
add(2,x)
a b x c d e f g h
remove(1)
a x c d e f g h
remove(7)
a x c d e f g
remove(6)
a x c d e f
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
图 2.5：在 RootishArray-栈上进行 add(i,x) 和 remove(i) 操作的序列。箭头表示被复
制的元素。
在本节中，我们讨论 RootishArrayStack 数据结构，它解决了空间浪费
的问题。RootishArrayStack 使用 O(√n) 个数组来存储 n 个元素。在这些数
组中，最多有 O(√n) 个数组位置在任何时候未被使用。所有剩余的数组位
置都用来存储数据。因此，当存储 n 个元素时，这些数据结构最多浪费
O(√n) 的空间。
RootishArrayStack 将其元素存储在一个由 r 个数组组成的列表中，这些
数组称为 blocks，编号从 0,、1, . . . , 到 r -1。见图 2.5。块 b 包含 b +-1 个
−
元素。因此，所有 r 个块总共包含
1 + 2 + 3 + + r = r(r + 1)/2
· · ·
元素。上述公式可以如图2.6所示得到。
Rootish数组栈
List<T[]> 块；int n；
正如我们所预期的，列表的元素按顺序排列在各个块中。索引为 0 的
列表元素存储在块 0 中，
. . .
.
.
.
r . . .
.
.
.
. . .
r + 1
图 2.6：白色方格的数量是 1+2+3+···+r。阴影方格的数量相同。白色和阴影方格
一起组成了一个由 r(r + 1) 个方格组成的矩形。
索引为1和2的元素存储在块1中，索引为3、4和5的元素存储在块2中，依
此类推。我们必须解决的主要问题是确定给定索引i，哪个块包含i，以及
该块中对应于i的索引。

（中文关键词：数组、栈；英文术语：Stack）

## RootishArrayStack：一种节省空间的数组S 图钉 (2/2)

确定 i 在其所在块中的索引结果很简单。如果索引 i 在块 b 中，那么块
0 到 b-1 的元素数量为 b(b-1)/2。因此，i 存储的位置为
j = i b(b + 1)/2
−
在块 B 内。更具挑战性的问题是确定 b 的值。索引小于或等于 i 的元素数
量是 i + 1。另一方面，块 0、⋯、b 中的元素数量是 (b + 1)(b + 2)/2。因
此，b 是满足以下条件的最小整数
(b + 1)(b + 2)/2 i + 1 .
≥
我们可以将这个方程改写为
b2 + 3b 2i 0 .
− ≥
对应的二次方程 b2 + 3b 2i = 0 有两个解：b = ( 3 + √9 + 8i)/2 和 b = ( 3
− − −
√9 + 8i)/2。第二个解在我们的应用中没有意义，因为它总是给出负值。
−
因此，我们得到的解是 b = ( 3 + √9 + 8i)/2。一般来说，这个解
−
不是整数，但回到我们的不等式，我们想要最小的整数 b，使得 b ( 3
≥ −
+ √9 + 8i)/2。这很简单
b = ( 3 + √9 + 8i)/2 .
−
(cid:108) (cid:109)
RootishArrayStack int i2b(int i) { d
ouble db = (-3.0 + Math.sqrt(9 + 8*i)) / 2.0; int b = (int)Ma
th.ceil(db); return b;
}
有了这些基础，get(i) 和 set(i, x) 方法就很直接了。我们首先计算出合
适的块 b 以及块内的合适索引 j，然后执行相应的操作：
RootishArrayStack
T get(int i) {
int b = i2b(i);
int j = i - b*(b+1)/2;
return blocks.get(b)[j];
}
T set(int i, T x) {
int b = i2b(i);
int j = i - b*(b+1)/2;
T y = blocks.get(b)[j];
blocks.get(b)[j] = x;
return y;
}
如果我们使用本章中的任何数据结构来表示块列表，那么 get(i) 和 set(i
, x) 将各自以常数时间运行。
add(i, x) 方法现在看起来应该很熟悉。我们首先检查数据结构是否已满
，通过检查块的数量 r 是否满足 r(r + 1)/2 = n。如果是这样，我们调用 gro
w() 来添加另一个块。完成这一步后，我们将索引为 i, . . . , 到 n 1 的元素向
−
右移动一个位置，为索引为 i 的新元素腾出空间：
RootishArrayStack
void add(int i, T x) {
int r = blocks.size();
if (r*(r+1)/2 < n + 1) grow();
n++;
for (int j = n-1; j > i; j--)
set(j, get(j-1));
set(i, x);
}
grow() 方法的作用符合我们的预期。它会添加一个新的区块：
RootishArrayStack void
grow() { blocks.add(newArray(blocks.size()+1)); }
忽略 grow() 操作的成本，add(i, x) 操作的成本主要由移动元素的成本
决定，因此其成本为 O(1 + n i)，就像 ArrayStack 一样。
−
remove(i) 操作类似于 add(i x)。它将索引为 i 到 n 的元素向左移动一个
位置，然后，如果有多个空区块，它会调用 shrink() 方法来删除除一个未
使用区块之外的所有区块：
RootishArrayStack
T remove(int i) {
T x = get(i);
for (int j = i; j < n-1; j++)
set(j, get(j+1));
n--;
int r = blocks.size();
if ((r-2)*(r-1)/2 >= n) shrink();
return x;
}
RootishArrayStack vo
id shrink() { int r = blocks.size();
while (r > 0 && (r-2)*(r-1)/2 >= n) { blocks.rem
ove(blocks.size()-1); r--; } }
再次，忽略 shrink() 操作的成本，remove(i) 操作的成本主要由移动元
素的成本决定，因此为 O(n i)。
−

（中文关键词：数组、栈；英文术语：Stack）

## 2.6.1 增长与缩小的分析

上述对 add(i, x) 和 remove(i) 的分析没有考虑 grow() 和 shrink() 的成本。请
注意，与 ArrayStack. 的 resize() 操作不同，grow() 和 shrink() 并不复制任
何数据。它们只是分配或释放一个大小为 r 的数组。在某些环境中，这只
需常量时间，而在其他环境中，可能需要与 r 成比例的时间。
我们注意到，在调用 grow() 或 shrink() 之后，情况是清晰的。最后一
个块是完全空的，所有其他块都是完全满的。在至少添加或删除 r 1 个
−
元素之前，另一调用 grow() 或 shrink() 不会发生。因此，即使 grow() 和 sh
rink() 需要 O(r) 时间，这个成本也可以在至少 r 1 次 add(i, x) 或 remove(i
−
) 操作中摊销，因此 grow() 和 shrink() 的摊销成本是每次操作 O(1)。

（中文关键词：数组、栈；英文术语：Stack）

## 2.6.2 空间使用

接下来，我们分析 RootishArrayStack 使用的额外空间量。特别是，我们希
望统计 RootishArrayStack 使用的、当前没有被用来存放列表元素的数组元
素所占的空间。我们将所有这样的空间称为 wasted space。
remove(i) 操作确保 RootishArrayStack 永远不会有超过两个不完全满的
块。因此，存储 n 个元素的 RootishArrayStack 所使用的块数 r 满足
(r 2)(r 1) n .
− − ≤
再次，使用二次方程在这个上得到
r (3 + √1 + 4n)/2 = O(√n) .
≤
最后两个块的大小分别是 r 和 r 1，因此这两个块浪费的空间最多为 2r 1
− −
= O(√n)。如果我们将这些块存储在（例如）ArrayList 中，那么存储这些
r 个块的 List 浪费的空间也是 O(r) = O(√n)。存储 n 和其他会计信息所需
的其他空间是 O(1)。因此，RootishArrayStack 中总的浪费空间是 O(√n)。
接下来，我们论证这种空间使用对于任何最初为空、并且能够一次添
加一个元素的数据结构来说是最优的。更准确地说，我们将展示，在添加
n 个元素的过程中，数据结构在某个时刻至少浪费了 √n 的空间（尽管可
能只是暂时浪费）。
假设我们从一个空的数据结构开始，然后一次添加 n 个元素。在这个
过程结束时，所有 n 个元素都存储在数据结构中，并分布在 r 个内存块上
。如果 r √n，那么数据结构必须使用 r 个指针（或引用）来跟踪这些 r
≥
个内存块，而这些指针是浪费的空间。另一方面，如果 r < √n，那么根据
抽屉原理，某些内存块的大小必须至少为 n/r > √n。考虑该内存块第一次
被分配的时刻。在它被分配后，这个内存块是空的，因此浪费了 √n 的空
间。因此，在插入 n 个元素的过程中，在某个时刻数据结构浪费了 √n 的
空间。

（中文关键词：数组、栈；英文术语：Stack）

## 2.6.3 总结

以下定理总结了我们对 RootishArray-Stack 数据结构的讨论：
定理 2.5. A RootishArrayStack implements the 列表 interface. Ignor-
ing the cost of calls to 增长() and 收缩(), a RootishArrayStack supports
the operations
• 获取(i) and 设置(i, x) in O(1) time per operation; and
• 添加(i, x) and 删除(i) in O(1 + n i) time per operat ion.
−
Furthermore, beginning with an empty RootishArrayStack, any sequence
of m 添加(i, x) and 移除(i) operations results in a total of O(m) time spent
during all calls to 扩容() and 缩容().
The space (measured in words)3 used by a 根数组栈 that stores n
elements is n + O(√n).

（中文关键词：数组、栈；英文术语：Stack）

## 2.6.4 计算平方根 (1/2)

接触过一些计算模型的读者可能会注意到，上述描述的 RootishArrayStack
并不符合通常的字-RAM 模型（第 1.4 节），因为它需要进行平方根运算
。平方根运算通常不被认为是基本操作，因此通常不包含在字-RAM 模型
中。
在本节中，我们展示了平方根运算可以高效地实现。特别地，我们展
示了对于任意整数 x {0, . . . , n}， √x 可以在常数时间内计算，在 O(√n)
∈ (cid:98) (cid:99)
预处理后，该预处理创建了两个长度为 O(√n) 的数组。以下引理表明，我
们可以将 x 的平方根问题归约为相关值 x 的平方根问题。
(cid:48)
引理 2 .3. Let x 1 and let x = x a, where 0 a √x. Then √x √x 1.
≥ (cid:48) − ≤ ≤ (cid:48) ≥ −
Proof. 只需表明
x √x √x 1 .
− ≥ −
(cid:113)
将这个不等式的两边平方得到
x √x x 2√x + 1
− ≥ −
并将项合并得到
√x 1
≥
对于任何 x 1，这显然是正确的。
≥
3Recall Section 1.4 for a discussion of how memory is measured.
首先通过稍微限制问题来开始，并假设 2r x < 2r+1，使得 log x = r
≤ (cid:98) (cid:99)
，即 x 是一个在其二进制表示中具有 r 个 + 1 位的整数。我们可以取 x =
(cid:48)
x (x mod 2 r/2 )。现在，x 满足引理 2.3 的条件，因此 √x √x 1。此
− (cid:98) (cid:99) (cid:48) − (cid:48) ≤
外，x 的所有低位 r/2 位都等于 0，因此只有
(cid:48)
(cid:98) (cid:99)
2r+1 r/2 4 2r/2 4√x
−(cid:98) (cid:99)
≤ · ≤
x 的可能取值。这意味着我们可以使用一个数组 sqrttab，该数组存储每个
(cid:48)
可能的 x 对应的 √x 的值。更准确一点，我们有
(cid:48) (cid:98) (cid:48)(cid:99)
sqrttab[i] = i2 r/2 .
(cid:98) (cid:99)
(cid:22)(cid:112) (cid:23)
以这种方式，sqrttab[i] 与 √x 相差不超过 2，适用于所有 x {i2
∈
r/2 , . . . , (i + 1)2 r/2 1}。换句话说，数组项 s = sqrttab[x>> r/2 ] 要么等于
(cid:98) (cid:99) (cid:98) (cid:99)
− (cid:98) (cid:99)
√x ，要么等于 √x 1，或者等于 √x 2。通过 s，我们可以通过递增
(cid:98) (cid:99) (cid:98) (cid:99) − (cid:98) (cid:99) −
s 直到 (s + 1)2 > x 来确定 √x 的值。
(cid:98) (cid:99)
快速平方根
int sqrt(int x, int r) { int s = sqrtab[x>>r/2]; while ((s+1)*(s+1) <= x) s++; //
最多执行两次 return s;
}
现在，这只适用于 x {2r, . . . , 2r+1 1}，而 sqrttab 是一个特殊的表，
∈ −
只适用于 r = log x 的特定值。为了解决这个问题，我们可以计算 log n
(cid:98) (cid:99) (cid:98) (cid:99)
个不同的 sqrttab 数组，每个可能的 log x 值对应一个数组。这些表的大
(cid:98) (cid:99)
小形成一个指数序列，其最大值至多为 4√n，因此所有表的总大小为 O(√
n)。
然而，事实证明，不止一个 sqrttab 数组是多余的；我们只需要一个用
于值 r = log n 的 sqrttab 数组。任何满足 log x = r < r 的值 x 都可以通过
(cid:48)
(cid:98) (cid:99)
将 x 乘以 2r − r (cid:48) 并使用该方程 upgraded 来处理。
√2r − r (cid:48) x = 2(r − r (cid:48))/2√x .
数值 2r − r (cid:48) x 位于范围 {2r, . . . , 2r+1 1} 内，因此我们可以在 sqrttab 中查找
−
它的平方根。以下代码实现了这个想法来
使用大小为 216 的数组 sqrttab，计算所有非负整数 x 在范围 {0, . . . , 230 1
−
} 内的 √x 。
(cid:98) (cid:99)
FastSqrt
int sqrt(int x) {
int rp = log(x);
int upgrade = ((r-rp)/2) * 2;
int xp = x << upgrade; // xp has r or r-1 bits
int s = sqrtab[xp>>(r/2)] >> (upgrade/2);
while ((s+1)*(s+1) <= x) s++; // executes at most twice
return s;
}
到目前为止，我们一直视为理所当然的一件事是如何计算 r = log x
(cid:48)
(cid:98) (cid:99)
的问题。同样，这是一个可以用大小为 2r/2 的数组 logtab 来解决的问题。

（中文关键词：数组、栈；英文术语：Stack）

## 2.6.4 计算平方根 (2/2)

在这种情况下，代码特别简单，因为 log x 只是 x 的二进制表示中最重
(cid:98) (cid:99)
要的 1 位的索引。这意味着，对于 x > 2r/2，我们可以在将其用作 logtab
的索引之前，将 x 的位右移 r/2 个位置。下面的代码使用大小为 216 的数
组 logtab 来计算范围为 {1, . . . , 232 1} 内所有 x 的 log x 。
− (cid:98) (cid:99)
FastSqrt
int log(int x) {
if (x >= halfint)
return 16 + logtab[x>>>16];
return logtab[x];
}
最后，为了完整性，我们包括了以下初始化 logtab 和 sqrttab 的代码：
FastSqrt
void inittabs() {
sqrtab = new int[1<<(r/2)];
logtab = new int[1<<(r/2)];
for (int d = 0; d < r/2; d++)
Arrays.fill(logtab, 1<<d, 2<<d, d);
int s = 1<<(r/4); // sqrt(2ˆ(r/2))
for (int i = 0; i < 1<<(r/2); i++) { if ((s+1)*(s+1) <= i << (r/2)) s++; // s
qrt 增加 sqrtab[i] = s; } }
总而言之，i2b(i) 方法所进行的计算可以在 word-RAM 上以常数时间实
现，使用 O(√n) 额外内存来存储 sqrttab 和 logtab 数组。当 n 增加或减少
一倍时，可以重建这些数组，并且这种重建的成本可以在导致 n 变化的 ad
d(i, x) 和 remove(i) 操作的数量上进行摊销，就像在 ArrayStack 实现中分析
resize() 的成本一样。

（中文关键词：数组、栈；英文术语：Stack）
