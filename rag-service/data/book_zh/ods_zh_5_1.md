---
structure: HashMap
source: book_zh/ods_zh_5_1.md
chapter: 5.1 链式哈希表：使用链式法的哈希
section: 5.1
page: 121
kind: textbook
---

# 5.1 链式哈希表：使用链式法的哈希

链式哈希表数据结构使用 hashing with chaining 将数据存储为一个列表数
组 t。一个整数 n 用于跟踪所有列表中的项目总数（见图 5.1）： 
ChainedHashTable
List<T>[] t;
int n;
The ha sh value 数据项 x 的散列值，记作 hash(x)，是 th 中的一个范值围
t 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
b d i x h j f m ‘ k
c g e
a
图 5.1：一个链式哈希表的示例，其中 n = 14，t.长度 = 16。在此示例中 hash(x) =
6
{0, . . . , t.长度 1}。所有哈希值为 i 的项都存储在 t[i] 的列表中。为了确保
−
列表不会变得过长，我们保持不变量
n t.长度
≤
这样存储在这些列表中的元素的平均数量就是 n/t.length 1。
≤
要向哈希表中添加一个元素 x，我们首先检查 t 的长度是否需要增加，
如果需要，我们就扩展 t。解决这个问题后，我们将 x 进行哈希运算，得
到一个整数 i，范围在 {0⋯t.length - 1}，然后将 x 添加到列表 t[i] 中：
ChainedHashTable
boolean add(T x) {
if (find(x) != null) return false;
if (n+1 > t.length) resize();
t[hash(x)].add(x);
n++;
return true;
}
如果有必要，扩展表格涉及将 t 的长度加倍，并将所有元素重新插入
到新表中。这一策略与 ArrayStack 实现中使用的完全相同，并且同样的结
果适用：在一系列插入操作的摊销下，扩展的成本只是常数（见第 33 页
的引理 2.1）。
除了增长之外，将一个新值 x 添加到链式哈希表时所做的唯一其他工
作是将 x 附加到列表 t[hash(x)] 中。对于
在第2章或第3章中描述的任何列表实现中，这只需恒定时间。
要从哈希表中移除一个元素 x，我们遍历列表 t[hash(x)]，直到找到 x，
这样我们就可以将其移除：
ChainedHashTable
T remove(T x) {
Iterator<T> it = t[hash(x)].iterator();
while (it.hasNext()) {
T y = it.next();
if (y.equals(x)) {
it.remove();
n--;
return y;
}
}
return null;
}
这需要 O(n ) 时间，其中 n 表示存储在 t[i] 的列表的长度。
hash(x) i
在哈希表中搜索元素 x 是类似的。我们在列表 t[hash(x)] 上执行线性搜
索：
ChainedHashTable
T find(Object x) {
for (T y : t[hash(x)])
if (y.equals(x))
return y;
return null;
}
同样，这需要与列表 t[hash(x)] 的长度成正比的时间。
哈希表的性能在很大程度上取决于哈希函数的选择。一个好的哈希函
数会将元素均匀地分布在长度为 t. 的列表中，这样列表 t[hash(x)] 的预期
大小为 O(n/t.length) = O(1)。另一方面，一个糟糕的哈希函数会将所有值
（包括 x）哈希到同一个表位置，在这种情况下，大小
列表 t[hash(x)] 将是 n。在下一节中，我们将描述一个好的哈希函数。

（中文关键词：哈希、数组、栈；英文术语：HashMap）

## 5.1.1 乘法哈希 (1/2)

乘法散列是一种基于模运算（在第2.3节讨论）和整数除法生成散列值的高
效方法。它使用 div 运算符，该运算符计算商的整数部分，同时舍弃余数
。形式上，对于任意整数 a 0 和 b 1，a div b = a/b 。
≥ ≥ (cid:98) (cid:99)
在乘法哈希中，我们使用大小为 2d 的哈希表，对于某个整数 d（称为
dimension）。整数 x {0, . . . , 2w 1} 的哈希公式是
∈ −
hash(x) = ((z x) mod 2w) div 2w − d .
·
这里，z 是在 {1, . . . , 2w 1} 中随机选择的一个 odd 整数。通过观察到默认
−
情况下，整数运算已经按 2w 取模（其中 w 是整数的位数），可以非常高
效地实现这个哈希函数。（见图 5.2）此外，将整数除以 2w d 等价于在二
−
进制表示中去掉最右边的 w d 位（这通过将位向右移 w d 实现）。通过
− −
这种方式，实现上述公式的代码比公式本身更简单：
ChainedHashTable
int hash(Object x) {
return (z * x.hashCode()) >>> (w-d);
}
以下引理，其证明将在本节稍后给出，表明乘法哈希在避免冲突方面
表现良好：
引理 5.1. Let x and y be any two values in {0, . . . , 2w 1} with x (cid:44) y. Then Pr
{hash(x) = hash(y)} 2/2d. −
≤
根据引理 5.1，remove(x) 和 find(x) 的性能很容易分析：
2w (4294967296) 100000000000000000000000000000000
z (4102541685) 11110100100001111101000101110101
x (42) 00000000000000000000000000101010
z x 10100000011110010010000101110100110010
(z · x) mod 2w 00011110010010000101110100110010
((z · x) mod 2w) div 2w d 00011110
−
·
图 5.2：乘法哈希函数的操作，w = 32 和 d = 8。
引理 5.2. For any data value x, the expected length of the list t[hash(x)]
is at most n + 2, where n is the number of occurrences of x in the hash table.
x x
Proof. 设 S 为哈希表中不等于 x 的元素（多重）集合。对于元素 y S，
∈
定义指示变量
1 if hash(x) = hash(y)
I =
y 0 otherwise
(cid:40)
并注意，根据引理 5.1，E[I ] 2/2d = 2/t.长度。列表 t[hash(x)] 的期望长
y
≤
度由下式给出
E [t[hash(x)].size()] = E n + I
x y
 
y S
= n
x

+
(cid:88)
E
∈
[I
y
]

y S
(cid:88)∈
n + 2/t.length
x
≤
y S
(cid:88)∈
n + 2/n
x
≤
y S
(cid:88)∈
n + (n n )2/n
x x
≤ −
n + 2 ,
x
≤
根据要求。
现在，我们想要证明引理 5.1，但首先我们需要一个来自数论的结果。
在下面的证明中，我们使用记号 (b , . . . , b ) 来表示 r b 2i，其中每个 b
r 0 2 i=0 i i
是一个比特，取值为 0 或 1。换句话说,
(cid:80)
(b r , . . . , b 0)2 是其二进制表示为 b , . . . , b 的整数。我们使用 (cid:63) 来表示一个未
r 0
知值的比特。
引理 5.3. Let S be the set of odd integers in {1, . . . , 2w 1}; let q and i
−
be any two elements in S. Then there is exactly one value z S such that
∈
zq 模 2w = i.
Proof. 由于 z 和 i 的选择数量相同，只需证明存在一个值 z S 满足 zq mo
d 2w = i。 ∈
假设，为了矛盾起见，存在两个这样的值 z 和 z ，且 z > z 。那么
(cid:48) (cid:48)
zq mod 2w = z (cid:48)q mod 2w = i
所以
(z z
(cid:48)
)q mod 2w = 0
−
但这意味着
(z z
(cid:48)
)q = k2w (5.1)
−
对于某个整数 k。用二进制数来思考，我们有
(z z (cid:48) )q = k (1, 0, . . . , 0) 2 ,
− ·
w
以便 (z z )q 的二进制表示中尾随的 w 位(cid:124)全(cid:123)(cid:122)为(cid:125) 0。
(cid:48)
− (cid:32) (cid:32)
此外 k (cid:44) 0，因为 q (cid:44) 0 且 z z (cid:44) 0。由于 q 是奇数，它的二进制表示
(cid:48)
−
中没有尾随的 0：
q = ((cid:63), . . . , (cid:63), 1) .

（中文关键词：哈希表；英文术语：HashMap）

## 5.1.1 乘法哈希 (2/2)

2
由于 z z < 2w，z z 在其二进制表示中尾随的 0 少于 w：
(cid:48) (cid:48)
| − | −
z z (cid:48) = ((cid:63), . . . , (cid:63), 1, 0, . . . , 0) 2 .
−
<w
因此，乘积 (z z
(cid:48)
)q 在其二进制表示中尾(cid:124)随(cid:123)的(cid:122) (cid:125)0 少于 w 个：
−
(cid:32) (cid:32)
(z z (cid:48) )q = ((cid:63), , (cid:63), 1, 0, . . . , 0) 2 .
− · · ·
<w
(cid:124) (cid:123)(cid:122) (cid:125)
(cid:32) (cid:32)
因此 (z z )q 无法满足 (5.1)，从而产生矛盾并完成证明。
(cid:48)
−
引理 5.3 的实用性来自以下观察：如果 z 从 S 中均匀随机选择，那么 zt
在 S 上均匀分布。在下面的证明中，有助于考虑 z 的二进制表示，它由 w
个 1 个随机比特后跟一个 1 组成。
−
Proof of Lemma 5.1. 首先，我们注意到条件 hash(x) = hash(y) 等价于“zx
mod 2w 的最高 d 位和 zy mod 2w 的最高 d 位相同”这一说法。该说法的一
个必要条件是 z(x y) mod 2w 的二进制表示中的最高 d 位要么全为 0，要
−
么全为 1。也就是说，
z(x y) mod 2w = (0, . . . , 0, (cid:63), . . . , (cid:63)) (5.2)
2
−
d w d
−
当 zx mod 2w > zy mod 2w 或 (cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
(cid:32) (cid:32) (cid:32) (cid:32)
z(x y) mod 2w = (1, . . . , 1, (cid:63), . . . , (cid:63)) . (5.3)
2
−
d w d
−
当 zx mod 2w < zy mod 2w。因此，我们(cid:124)只(cid:123)(cid:122)需(cid:125)要(cid:124)限(cid:123)制(cid:122) (cid:125)z(x y) mod 2w 看起来
(cid:32) (cid:32) (cid:32) (cid:32) −
像 (5.2) 或 (5.3) 的概率。
设 q 为唯一的奇整数，使得 (x y) mod 2w = q2r 对某个整数 r ≥ 0 成
− ≥
立。根据引理 5.3，zq mod 2w 的二进制表示有 w 个随机比特 1，后跟一
−
个 1：
zq mod 2w = (b , . . . , b , 1)
w 1 1 2
−
w 1
−
因此，z(x y) mod 2w = zq2r mod 2w 的 (cid:124) 二进 (cid:123) 制 (cid:122) 表 (cid:125) 示有 w r 个随机位，后
− (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) − −
跟一个 1，再后跟 r 个 0：
z(x y) mod 2w = zq2r mod 2w = (b , . . . , b , 1, 0, 0, . . . , 0)
w r 1 1 2
− − −
w r 1 r
− −
我们现在可以完成证明：如果 r > w d，(cid:124)那么(cid:123) z(cid:122)(x (cid:125) y) m(cid:124)od (cid:123)2(cid:122)w 的 (cid:125) 前 d 位既
− (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)−(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)
包含 0 也包含 1，因此 z(x 的概率
−
y) mod 2w 看起来像 (5.2) 或 (5.3) 是 0。如果 r = w d，那么看起来像 (5.2)
−
的概率是 0，但看起来像 (5.3) 的概率是 1/2d 1 = 2/2d (，因为我们必须有
−
b , . . . , b = 1, . . . , 1)。如果 r < w d，那么我们必须有
1 d 1
− −
b , . . . , b = 0, . . . , 0 或 b , . . . , b = 1, . . . , 1。这些情况的概率
w r 1 w r d w r 1 w r d
各 − 是 − 1/2d，并 − 且 − 它们是互斥的， − 所 − 以这两 − 种 − 情况的概率是 2/2d。这完成了
证明。

（英文术语：HashMap）

## 5.1.2 总结

下列定理总结了链式哈希表数据结构的性能：
定理 5.1. A 链式哈希表 implements the USet interface. Ignor-
ing the cost of calls to grow(), a 链式哈希表 supports the operations 添加(x),
移除(x), and 查找(x) in O(1) expected time per operation.
Furthermore, beginning with an empty 链式哈希表, any sequence of m 添
加(x) and 移除(x) operations results in a total of O(m) time spent
during all calls to 扩展().

（英文术语：HashMap）
