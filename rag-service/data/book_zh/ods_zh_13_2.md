---
structure: 
source: book_zh/ods_zh_13_2.md
chapter: 13.1 二进制字典树：一种数字搜索树
section: 13.2
page: 286
kind: textbook
---

# 13.2 XFastTrie：以双对数时间进行搜索

## XFastTrie：以双对数时间进行搜索 (1/2)

BinaryTrie 结构的性能并不令人印象深刻。存储在该结构中的元素数量 n
最大为 2w，因此 log n w。换句话说，本书其他部分描述的任何基于比
≤
较的 SSet 结构，其效率至少与 BinaryTrie 相当，而且不限于仅存储整数。
接下来我们描述 XFastTrie，它只是一个带有 w 个哈希表的 BinaryTrie
——每一层 trie 对应一个哈希表。这些哈希表用于将 find(x) 操作加速到 lo
g w 时间。回想一下，在 BinaryTrie 中的 find(x) 操作几乎在到达节点 u 时
就完成了，其中 x 的搜索路径会尝试继续向 u 的右子节点（或左子节点）
移动，但 u 没有右子节点（或左子节点）。此时，搜索使用 u 的 jump 跳
到 BinaryTrie 的一个叶子节点 v，然后返回 v 或者叶子节点链表中的其后
继节点。XFastTrie 通过在 trie 的各个层上使用二分搜索来定位节点 u，从
而加快搜索过程。
要使用二分查找，我们需要一种方法来确定我们要寻找的节点 u 是否
位于某个特定的层 i 之上，或者 u 是否位于层 i 或其以下。这个信息由 x
的二进制表示中的最高位 i 位提供；这些位决定了 x 从根节点到第 i 层的
搜索路径。举个例子，请参见图 13.6；在这个图中，搜索 14（其二进制表
示为 1110）的路径上的最后一个节点 u 是标记为 11(cid:63)(cid:63) 的第 2 层节点，因
为在第 3 层不存在标记为 111(cid:63) 的节点。因此，我们可以用一个 i 位的整
数标记每个第 i 层的节点。然后，我们要寻找的节点 u 当且仅当第 i 层存
在其标签与最高位 i 位匹配的节点时，才会位于第 i 层或其以下。
? ? ? ? 0
1
0? ? ? 1? ? ? 1
1
00?? 01?? 10?? 11?? 2
1
000? 001? 010? 011? 100? 101? 110? 111? 3
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 4
图 13.6：由于没有标记为 111(cid:63) 的节点，搜索 14 (1110) 的路径在标记为 11(cid:63)(cid:63) 的节
点结束。
x 的位
在 XFastTrie 中，对于每个 i {0, . . . , w}，我们将所有在第 i 级别的节
∈
点存储在一个 USet t[i] 中，该 USet 实现为哈希表（第 5 章）。使用这个
USet 使我们能够在期望常数时间内检查是否存在第 i 级别的节点，其标签
与 x 的最高 i 位匹配。实际上，我们甚至可以使用 t[i].find(x>>>(w i)) 找
−
到这个节点。
哈希表 t[0], . . . , t[w] 使我们可以使用二分查找来找到 u。最初，我们知
道 u 位于某个层级 i，其中 0 i < w + 1。因此，我们初始化 l = 0 和 h = w
≤
+ 1，并重复查看哈希表 t[i]，其中 i = (l + h)/2 。如果 t[i] 包含一个标签
(cid:98) (cid:99)
与 x 的最高 i 位匹配的节点，则我们将 l = i（u 位于或低于第 i 层）；否
则我们将 h = i（u 位于第 i 层之上）。当 h l 1 时，该过程终止，此时
− ≤
我们确定 u 位于第 l 层。然后，我们使用 u.jump 和叶子节点的双向链表完
成 find(x) 操作。
XFastTrie
T find(T x) {
int l = 0, h = w+1, ix = it.intValue(x);
Node v, u = r, q = newNode();
while (h-l > 1) {
int i = (l+h)/2;
q.prefix = ix >>> w-i;
如果 ((v = t[i].find(q)) == null) { h = i; } 否则 { u
= v; l = i; } } 如果 (l == w) 返回 u.x; 节点 pred = (((ix
>>> w-l-1) & 1) == 1) ? u.jump : u.jump.child[0]; 返
回 (pred.child[next] == dummy) ? null : pred.child[next].
x; }
上面方法中 while 循环的每次迭代大约将 h l 减半，因此这个循环在
−
O(log w) 次迭代后找到 u。每次迭代执行恒定量的工作和在 USet 中的一次
find(x) 操作，这需要恒定的期望时间。剩余的工作只需要恒定时间，因此
XFastTrie 中的 find(x) 方法只需 O(log w) 的期望时间。
XFastTrie 的 add(x) 和 remove(x) 方法与 BinaryTrie 中的相同方法几乎
完全相同。唯一的修改是用于管理哈希表 t[0],...,t[w]。在 add(x) 操作中，
当在级别 i 创建一个新节点时，该节点会被添加到 t[i]。在 remove(x) 操作
中，当从级别 i 移除一个节点时，该节点会从 t[i] 中删除。由于在哈希表
中添加和删除操作的期望时间是常数，因此这不会使 add(x) 和 remove(x)
的运行时间增加超过一个常数因子。我们省略了 add(x) 和 remove(x) 的代
码列表，因为其代码与之前提供的 BinaryTrie 中相同方法的（较长）代码
列表几乎完全相同。

（中文关键词：字典树）

## XFastTrie：以双对数时间进行搜索 (2/2)

下列定理总结了 XFastTrie 的性能：
定理 13.2. An XFastTrie implements the SSet interface for w-bit inte-
gers. An XFastTrie supports the operations
• 添加(x) and 移除(x) in O(w) expected time per operation and
• find(x) in O(log w) expected time per operation.
The space used by an XFastTrie that stores n values is O (n · w).

（中文关键词：字典树）
