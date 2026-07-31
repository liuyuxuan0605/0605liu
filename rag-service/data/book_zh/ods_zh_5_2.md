---
structure: HashMap
source: book_zh/ods_zh_5_2.md
chapter: 5.1 链式哈希表：使用链式法的哈希
section: 5.2
page: 128
kind: textbook
---

# 5.2 线性哈希表：线性探测

## 线性哈希表：线性探测 (1/2)

链式哈希表数据结构使用一个列表数组，其中第 i 个列表存储所有满足 ha
sh(x) = i 的元素 x。另一种方法，称为 open addressing，是将元素直接存
储在数组 t 中，每个数组位置最多存储一个值。本节所述的线性哈希表采
用了这种方法。在某些地方，这种数据结构被描述为
open addressing with linear probing。
线性哈希表的主要思想是，我们理想情况下希望将哈希值为 i = hash(x)
的元素 x 存储在表的位置 t[i]。如果无法这样做（因为那里已经存储了某
个元素），那么我们尝试将其存储在位置 t[(i + 1) mod t.length]；如果这仍
然不可能，那么我们尝试 t[(i + 2) mod t.length]，以此类推，直到找到 x 的
合适位置。
t 中存储了三种类型的条目：
1. 数据值：我们在 USet 中表示的实际值；
2. 空值：在数组中从未存储过数据的位置；以及
3. del 值：在数组中曾经存储数据但后来已被删除的位置。
除了用于记录线性哈希表中元素数量的计数器 n 外，还有一个计数器 q 用
于记录类型 1 和类型 3 元素的数量。也就是说，q 等于 n 加上 t 中 del 值的
数量。为了让此操作高效运行，我们需要 t 的大小远大于 q，这样 t 中就
有大量的空值。因此，对线性哈希表的操作保持不变量 t 的长度至少为 2q
。
总而言之，线性哈希表包含一个数组 t，用于存储数据元素，以及整数
n 和 q，用于分别跟踪数据元素的数量和 t 的非空值数量。由于许多哈希
函数仅适用于大小为 2 的幂的表，我们还保持一个整数 d，并保持不变式
t 的长度为 2 的 d 次方。
LinearHashTable
T[] t; // the table
int n; // the size
int d; // t.length = 2ˆd
int q; // number of non-null entries in t
在线性哈希表中，find(x) 操作很简单。我们从数组条目 t[i] 开始，其中
i = hash(x)，然后依次搜索条目 t[i]、t[(i + 1) mod t.length]、t[(i + 2) mod t.le
ngth]，依此类推，直到找到一个索引 i，使得 t[i] = x，或者 t[i] = null。在
前一种情况下，我们返回 t[i]。在后一种情况下，我们得出 x 不包含在哈
希表中并返回 null。
LinearHashTable
T find(T x) {
int i = hash(x);
while (t[i] != null) {
if (t[i] != del && x.equals(t[i])) return t[i];
i = (i == t.length-1) ? 0 : i + 1; // increment i
}返回空; }
add(x) 操作也相当容易实现。在检查 x 是否已存储在表中（使用 find(x
)）之后，我们搜索 t[i]、t[(i+1) mod t.length]、t[(i+2) mod t.length]，依此
类推，直到我们找到 null 或 del，并将 x 存储在该位置，必要时增加 n 和
q。
LinearHashTable
boolean add(T x) {
if (find(x) != null) return false;
if (2*(q+1) > t.length) resize(); // max 50% occupancy
int i = hash(x);
while (t[i] != null && t[i] != del)
i = (i == t.length-1) ? 0 : i + 1; // increment i
if (t[i] == null) q++;
n++;
t[i] = x;
return true;
}
到现在为止，remove(x) 操作的实现应该很明显。我们搜索 t[i]、t[(i + 1
) mod t.length]、t[(i + 2) mod t.length]，依此类推，直到找到一个索引 i，使
得 t[i] = x 或 t[i] = null。在前一种情况下，我们将 t[i] 设置为 del 并返回 tru
e。在后一种情况下，我们得出 x 没有存储在表中（因此无法删除）并返
回 false。

（中文关键词：字典树；英文术语：HashMap）

## 线性哈希表：线性探测 (2/2)

LinearHashTable
T remove(T x) {
int i = hash(x);
while (t[i] != null) {
T y = t[i];
if (y != del && x.equals(y)) {
t[i] = del;
n--;
if (8*n < t.length) resize(); // min 12.5% occupancy
return y;
}
i = (i == t.length-1) ? 0 : i + 1; // increment i
}
return null;
}
find(x)、add(x) 和 remove(x) 方法的正确性很容易验证，尽管它依赖于
使用 del 值。请注意，这些操作中没有任何一个会将非空条目设置为 null
。因此，当我们到达一个索引 i 且 t[i ] 为 null 时，这是一个证明我们正在
(cid:48) (cid:48)
搜索的元素 x 没有存储在表中的证据；t[i ] 一直为 null，因此没有理由之
(cid:48)
前的 add(x) 操作会在索引 i 之后继续进行。
(cid:48)
当非空条目的数量超过 t.length/2 时，add(x) 会调用 resize() 方法，或者
当数据条目的数量少于 t.length/8 时，remove(x) 会调用 resize() 方法。resiz
e() 方法的工作方式类似于其他基于数组的数据结构中的 resize() 方法。我
们找到最小的非负整数 d，使得 2d ≥ 3n。我们重新分配数组 t，使其大
≥
小为 2d，然后将旧版本 t 中的所有元素插入到新调整大小的 t 中。在此过
程中，我们将 q 重置为 n，因为新分配的 t 中不包含 del 值。
LinearHashTable void resize
() { d = 1; while ((1<<d) < 3*n) d++; T[] told = t; t = new
Array(1<<d); q = n; // 将所有元素从 told 插入 for (int k
= 0; k < told.length; k++) { if (told[k] != null && told[k] !
= del) { int i = hash(told[k]); while (t[i] != null) i = (i ==
t.length-1) ? 0 : i + 1; t[i] = told[k]; } }
}

（中文关键词：数组；英文术语：HashMap）

## 5.2.1 线性探测分析 (1/2)

请注意，每个操作 add(x)、remove(x) 或 find(x) 在发现 t 中的第一个空条
目时（或之前）就会结束。线性探测分析背后的直觉是，由于 t 中至少有
一半的元素是空的，操作完成应该不会花费很长时间，因为它很快就会遇
到一个空条目。然而，我们不应过分依赖这种直觉，因为这会导致我们得
出（错误的）结论，即操作在 t 中检查的位置的期望数量最多为 2。
在本节的其余部分，我们将假设所有的哈希值在 {0, . . . , t.length 1} 中
−
是独立且均匀分布的。这并不是一个现实的假设，但它将使我们能够分析
线性探测法。本节稍后我们将描述一种称为表格哈希（tabulation hashing
）的方法，它可以产生一个对线性探测法“足够好”的哈希函数。我们还
将假设对 t 的位置的所有索引都取模 t.length，因此 t[i] 实际上是 t[i mod t.l
ength] 的简写。
当所有表项 t[i]、t[i + 1]、t[i + 1] 都非空且 t[i + 1] 不为 null 并且 t[i] 不
为 null 时，我们称出现了一个 run of length k that starts at i。t 中的非空元
素正好有 q 个，并且 add(x) 方法保证在任何时候 q ≤ t.length/2。从上一次
rebuild() 操作以来，已经插入到 t 中的元素有 q 个 x，它们各自的哈希值 h
ash(x) 是均匀且相互独立的。在这种设置下，我们可以证明分析线性探测
所需的主要引理。
引理 5.4. Fix a value i {0, . . . , t.长度 1}. Then the probability that a
∈ −
run of length k starts at i is O(ck) for some constant 0 < c < 1.
Proof. 如果长度为 k 的连续序列从 i 开始，那么恰好有 k 个元素 x 使得 ha
j
sh(x ) {i, . . . , i + k 1}。这种情况发生的概率正好是
j
∈ −
k q k
q k t.length k −
p = − ,
k k t.length t.length
(cid:32) (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
因为，对于每一个 k 元素的选择，这些 k 元素必须哈希到 k 个位置中的一
个，而剩余的 q 个 k 元素必须哈希到其他 t. 长度的 k 表位置。1
− −
在以下推导中，我们将稍微作弊一下，用 (r/e)r 替代 r!。斯特林近似（
第 1.3.2 节）表明，这与实际值仅相差一个 O(√r) 的因子。这样做只是为
了使推导更简单；练习 5.4 要求读者用完整的斯特林近似更严格地重新计
算。
p 的值在 t.length 最小的时候最大，并且数据结构保持不变式，即 t.len
k
gth 2q，因此
≥
k q k
q k 2q k −
p −
k ≤ k 2q 2q
(cid:32) (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
k q k
q! k 2q k −
= −
(q k)!k! 2q 2q
(cid:32) − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
qq k k 2q k q − k
− [斯特林近似]
≈ (q k)q kkk 2q 2q
(cid:32) − − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
qkqq − k k k 2q k q − k
= −
(q k)q kkk 2q 2q
(cid:32) − − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
k q k
qk q(2q k) −
= −
2qk 2q(q k)
(cid:32) (cid:33) (cid:32) − (cid:33)
1 k (2q k) q − k
= −
2 2(q k)
(cid:18) (cid:19) (cid:32) − (cid:33)
1 k k q − k
= 1 +
2 2(q k)
(cid:18) (cid:19) (cid:32) − (cid:33)
k
√e
.
≤ 2
(cid:32) (cid:33)
(在最后一步中，我们使用不等式 (1 + 1/x)x e，它对所有 x > 0 都成立。
≤
) 由于 √e/2 < 0.824360636 < 1，这就完成了证明。
使用引理5.4来证明 find(x)、add(x) 和 remove(x) 的预期运行时间上界
现在相当简单。考虑最简单的情况，即我们对某个值 x 执行 find(x) 时
1Note that pk is greater than the probability that a run of length k starts at i, since the
definition of pk does not include the requirement t[i
−
1] = t[i + k] = null.

（中文关键词：概率、哈希；英文术语：HashMap）

## 5.2.1 线性探测分析 (2/2)

从未存储在线性哈希表中。在这种情况下，i = hash(x) 是 {0, . . . , t.length
−
1} 中的一个随机值，与 t 的内容无关。如果 i 是长度为 k 的一段中的一部
分，那么执行 find(x) 操作所需的时间最多为 O(1 + k)。因此，期望运行时
间可以被上界为
t.length
1 ∞
O 1 + k Pr i is part of a run of length k .
t.length { }
 
请注意
，每 (cid:18)
个长度为
(cid:19)
k 的
(cid:88) i=
运
1
行
(cid:88) k
在
=0
内部求和中贡献了 k 次，总贡献为
k2，因
此上述求和可以重写为
t.length
O 1 + 1 ∞ k2 Pr i starts a run of length k
t.length { }
 

O 1
(cid:18)
+ 1
(cid:19) (cid:88) i
t
=
.
1
leng
(cid:88) k
t
=
h
0
∞ k2p

≤ t.length k
 
= O
1
+
(cid:18)
∞ k2p
(cid:19) (cid:88) i=1 (cid:88) k=0 
k
 
k=0
= O
1
+
(cid:88)
∞ k2 O
(ck)
·
 
k=0
= O(

1) .
(cid:88) 
这个推导的最后一步来源于这样一个事实： ∞k=0 k2 · O(ck) 是一个指数递
减的序列。2 因此，我们得出结论，对于一个不包含在线性哈希表中的值
(cid:80)
x，find(x) 操作的期望运行时间是 O(1)。
如果我们忽略 resize() 操作的成本，那么以上分析就为我们提供了分析
线性哈希表上操作成本所需的一切。
首先，上述对 find(x) 的分析适用于当 x 不在表中时的 add(x) 操作。要
分析 x 在表中时的 find(x) 操作，我们只需注意这一点
2In the terminology of many calculus texts, this sum passes the ratio test: There exists a
(k+1)2ck+1
positive integer k0 such that, for all k
≥
k0,
k2ck
< 1.
与之前将 x 添加到表中的 add(x) 操作的成本相同。最后，remove(x) 操作
的成本与 find(x) 操作的成本相同。
总之，如果我们忽略调用 resize() 的成本，LinearHashTable 上的所有操
作的期望时间都是 O(1)。考虑 resize 的成本可以使用与第 2.1 节 ArrayStac
k 数据结构相同类型的摊还分析来完成。

（中文关键词：数组；英文术语：HashMap）

## 5.2.2 总结

以下定理总结了线性哈希表数据结构的性能：
定理 5.2. A 线性哈希表 implements the U集 interface. Ignor-
ing the cost of calls to 调整大小() , a 线性哈希表 supports the operations 添
加(x) , 移除(x) , and 查找(x) in O(1) expected time per operation.
Furthermore, beginning with an empty 线性哈希表, any sequence of m
添加(x) and 删除(x) operations results in a total of O(m) time spent
during all calls to 调整大小().

（英文术语：HashMap）

## 5.2.3 表格哈希

在分析线性哈希表结构时，我们做了一个非常强的假设：对于任意元素集
合 {x , . . . , x }，哈希值 hash(x ), . . . , hash(x ) 是在集合 {0, . . . , t.length 1}
1 n 1 n
−
上独立且均匀分布的。一种实现方法是存储一个长度为 2w 的巨型数组 tab
，其中每个条目都是一个独立于其他所有条目的随机 w 位整数。通过这种
方式，我们可以通过从 tab[x.hashCode()] 中提取一个 d 位整数来实现 hash(
x)：
LinearHashTable
int idealHash(T x) {
return tab[x.hashCode() >>> w-d];
}
不幸的是，存储一个大小为 2w 的数组在内存使用方面是不可行的。
tabulation hashing 使用的方法是，取而代之，
将 w 位整数视为由 w/ 个 r 位整数组成，每个整数仅有 r 位。通过这种方
式，制表哈希只需要 w/ 个长度为 2r 的数组。这些数组中的所有条目都是
独立的 w 位整数。为了获得 hash(x) 的值，我们将 x.hashCode() 分成 w/ 个
r 位整数，并将这些作为这些数组的索引。然后我们使用按位异或运算符
将所有这些值组合以获得 hash(x)。以下代码展示了当 w = 32 且 r = 4 时的
工作原理：
LinearHashTable
int hash(T x) {
int h = x.hashCode();
return (tab[0][h&0xff]
ˆ tab[1][(h>>>8)&0xff]
ˆ tab[2][(h>>>16)&0xff]
ˆ tab[3][(h>>>24)&0xff])
>>> (w-d);
}
在这种情况下，tab 是一个具有四列和 232/4 = 256 行的二维数组。
可以很容易地验证，对于任意的 x，hash(x) 在 {0, . . . , 2d 1} 上是均匀
−
分布的。通过一些工作，甚至可以验证任意一对值的哈希值是独立的。这
意味着表填充哈希可以用于替代链式哈希表实现中的乘法哈希。
然而，任意 n 个不同的值会产生 n 个独立哈希值的说法并不正确。尽
管如此，当使用表格哈希时，定理 5.2 的界限仍然成立。本章末尾提供了
相关参考文献。

（中文关键词：哈希；英文术语：HashMap）
