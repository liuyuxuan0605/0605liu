---
structure: DoublyLinkedList
source: book_zh/ods_zh_3_3.md
chapter: 3.1 SLList：单链表
section: 3.3
page: 85
kind: textbook
---

# 3.3 SEList：一种节省空间的链表

链表的一个缺点（除了访问列表中深层元素所需的时间之外）是它们的空
间使用。双向链表（DLList）中的每个节点都需要额外的两个引用，分别
指向列表中的下一个和上一个节点。节点中的两个字段专门用于维护列表
，而只有一个字段用于存储数据！
SEList（节省空间的列表）通过一个简单的想法减少了这种浪费空间：
不是将单个元素存储在 DLList 中，而是存储一个包含多个项目的块（数
组）。更准确地说，SEList 由一个 b 参数化。SEList 中的每个单独节点存
储一个块，该块最多可以容纳 b + 1 个元素。
出于稍后将会明白的原因，如果我们能对每个块执行双端队列操作会
很有帮助。我们为此选择的数据结构是 BDeque（有界双端队列），它源
自第 2.4 节中描述的 ArrayDeque 结构。BDeque 与 ArrayDeque 在一点上有
所不同：当创建新的 BDeque 时，支持数组 a 的大小固定为 b + 1，并且永
远不会增长或缩小。BDeque 的重要特性是它允许在常数时间内在前端或
后端添加或移除元素。随着元素的添加，这将非常有用。
从一个街区搬到另一个街区。
SEList
class BDeque extends ArrayDeque<T> {
BDeque() {
super(SEList.this.type());
a = newArray(b+1);
}
void resize() { }
}
然后，SEList 是一个由块组成的双向链表：
SEList
class Node {
BDeque d;
Node prev, next;
}
SE列表
int n; 节点 du
mmy;

（中文关键词：双端队列、数组；英文术语：DoublyLinkedList）

## 3.3.1 空间要求

SEList 对块中的元素数量施加非常严格的限制：除非一个块是最后一个块
，否则该块至少包含 b 1 个元素，最多包含 b + 1 个元素。这意味着，如
−
果一个 SEList 包含 n 个元素，那么它最多有
n/(b 1) + 1 = O(n/b)
−
块。每个块的 BDeque 包含一个长度为 b 的数组 + 1，但对于每个块（除
了最后一个之外），在这个数组中最多只有一个常数空间被浪费。块使用
的剩余内存也是常数。这意味着 SEList 中的浪费空间仅为 O(b + n/b)。通
过选择一个与 √n 在常数因子内的 b 值，我们可以使 SEList 的空间开销接
近第 2.6.2 节中给出的 √n 下限。

（中文关键词：双端队列；英文术语：DoublyLinkedList）

## 3.3.2 查找元素

我们在使用 SEList 时面临的第一个挑战是找到具有给定索引 i 的列表项。
请注意，一个元素的位置由两部分组成：
1. 包含索引为 i 的元素所在块的节点 u；以及
2. 元素在其块内的索引 j。
SEList
class Location {
Node u;
int j;
Location(Node u, int j) {
this.u = u;
this.j = j;
}
}
要找到包含特定元素的块，我们按照在双向链表（DLList）中相同的
方式进行。我们要么从列表的前端开始，向前遍历，要么从列表的后端开
始，向后遍历，直到到达我们想要的节点。唯一的区别是，每次从一个节
点移动到下一个节点时，我们会跳过整块的元素。
SEList
Location getLocation(int i) {
if (i < n/2) {
Node u = dummy.next;
while (i >= u.d.size()) {
i -= u.d.size();
u = u.next;
}
return new Location(u, i);
} else {
Node u = dummy;
int idx = n;
while (i < idx) { u = u.prev; idx -= u.d.s
ize(); }return new Location(u, i-idx); } }
请记住，除最多一个块外，每个块至少包含 b 1 个元素，所以我们搜
−
索的每一步都会让我们离所寻找的元素更近 b 1 个元素。如果我们向前
−
搜索，这意味着我们在 O(1 + i/b) 步后到达我们想要的节点。如果我们向
后搜索，则在 O(1 + (n i)/b) 步后到达我们想要的节点。算法根据 i 的值
−
取这两个数量中的较小值，因此找到索引为 i 的项的时间是 O(1 + min{i, n
i}/b)。
−
一旦我们知道如何定位索引为 i 的项，get(i) 和 set(i, x) 操作就可以转换
为在正确的块中获取或设置特定索引：
SEList
T get(int i) {
Location l = getLocation(i);
return l.u.d.get(l.j);
}
T set(int i, T x) {
Location l = getLocation(i);
T y = l.u.d.get(l.j);
l.u.d.set(l.j,x);
return y;
}
这些操作的运行时间主要取决于找到项目所需的时间，因此它们的运
行时间也为 O(1 + min{i, n i}/b) 时间。
−

（英文术语：DoublyLinkedList）

## 3.3.3 添加一个元素

向 SEList 添加元素稍微复杂一些。在考虑一般情况之前，我们先考虑较简
单的操作 add(x)，其中
x 被添加到列表的末尾。如果最后一个块已满（或者不存在，因为还没有
块），那么我们首先分配一个新块并将其附加到块列表中。现在我们确定
最后一个块存在且未满，我们将 x 添加到最后一个块中。
SEList
boolean add(T x) {
Node last = dummy.prev;
if (last == dummy || last.d.size() == b+1) {
last = addBefore(dummy);
}
last.d.add(x);
n++;
return true;
}
当我们使用 add(i, x) 向列表内部添加元素时，情况会变得更复杂。我
们首先定位 i，以找到其所属 block 包含第 i 个列表项的节点 u。问题是，
我们希望将 x 插入到 u 的 block 中，但我们必须为 u 的 block 已经包含 b +
1 个元素的情况做好准备，这样它就满了，没有空间放置 x。
设 u , u , u , . . . 表示 u、u.next、u.next.next，依此类推。我们探索 u , u
0 1 2 0
, u , . . . 以寻找可以为 x 提供空间的节点。在我们的空间探索过程中可能
1 2
发生三种情况（见图 3.4）：
1. 我们快速（在 r + 1 b 步中）找到一个节点 u ，其块未满。在这种
r
≤
情况下，我们将执行 r 次从一个块到下一个块的元素移动，使得 u 中
r
的空闲空间变为 u 中的空闲空间。然后我们可以将 x 插入 u 的块中。
0 0
2. 我们很快（在 r +1 b 步中）跑到块列表的末尾。在这种情况下，我
≤
们在块列表的末尾添加一个新的空块，然后像第一种情况一样继续。
3. 在经过 b 步之后，我们没有找到任何未满的块。在这种情况下，u
, . . . , u 是由 b 个块组成的序列，每个块包含 b+1 个元素。我们在该
0 b 1
−
序列的末尾插入一个新块 u ，并 spread 原来的 b(b + 1) 个元素，以便 u
b
, . . . , u 的每个块都包含
0 b
a b c d e f g h i j
··· ···
a x b c d e f g h i j
··· ···
a b c d e f g h
···
a x b c d e f g h
···
a b c d e f g h i j k l
··· ···
a x b c d e f g h i j k l
··· ···
图 3.4：在 SEList 内部添加元素 x 时发生的三种情况。（此 SEList 的块大小 b 为 3
。）
正好有 b 个元素。现在 u 的块只包含 b 个元素，所以它有空间让我
0
们插入 x。
SEList
void add(int i, T x) {
if (i == n) {
add(x);
return;
}
Location l = getLocation(i);
Node u = l.u;
int r = 0;
while (r < b && u != dummy && u.d.size() == b+1) {
u = u.next;
r++;
}
if (r == b) { // b blocks each with b+1 elements
spread(l.u);
u = l.u;
}
if (u == dummy) { // 到达末尾 - 添加新节点 u = addBefore(u); }while (
u != l.u) { // 反向操作，移动元素 u.d.add(0, u.prev.d.remove(u.prev.d.siz
e()-1)); u = u.prev; }u.d.add(l.j, x); n++; }
add(i, x) 操作的运行时间取决于上述三种情况中的哪一种发生。情况 1
和情况 2 涉及检查和移动通过最多 b 个块的元素，耗时为 O(b)。情况 3 涉
及调用 spread(u) 方法，该方法移动 b(b + 1) 个元素，耗时为 O(b2)。如果
我们忽略情况 3 的成本（我们稍后将通过摊销来考虑），这意味着定位 i
并执行 x 插入的总运行时间为 O(b + min{i, n i}/b)。
−

（英文术语：DoublyLinkedList）

## 3.3.4 移除一个元素

从 SEList 中移除一个元素类似于添加一个元素。我们首先定位包含索引为
i 的元素的节点 u。现在，我们必须为以下情况做好准备：如果从 u 中移
除一个元素会导致 u 的块小于 b，我们就无法移除该元素。
再次，让 u , u , u , . . . 表示 u、u.next、u.next.next，等等。我们检查 u
0 1 2
, u , u , . . . 以寻找一个节点，从该节点可以借用一个元素，使 u 的块的
0 1 2 0
大小至少为 b 1。有三种情况需要考虑（见图 3.5）：
−
1. 我们快速地（在 r + 1 b 步内）找到一个其块包含超过 b 1 个元素
≤ −
的节点。在这种情况下，我们执行 r 次将一个元素从一个块移入前一个
块的操作，这样 u 中的多余元素就会成为 u 中的多余元素。然后我们
r 0
可以从 u 的块中移除适当的元素。
0
2. 我们很快（在 r + 1 b 步中）跑完了块列表的末尾。在这种情况下
≤
，u 是最后一个块，并且不需要 u 的块
r r
a b c d e f g
· · · · · ·
a c d e f g
· · · · · ·
a b c d e f
· · ·
a c d e f
· · ·
a b c d e f
· · · · · ·
a c d e f
· · · · · ·
图 3.5：在 SEList 内部移除一个元素 x 时发生的三种情况。（此 SEList 的块大小 b
为 3。）
至少包含 b 1 个元素。因此，我们按上述方法进行，从 u 借一个
r
−
元素，在 u 中增加一个额外元素。如果这导致 u 的块变为空，则我
0 r
们将其移除。
3. 在经过 b 步之后，我们没有找到任何包含多于 b 个 1 元素的区块。
−
在这种情况下，u , . . . , u 是一个由 b 个区块组成的序列，每个区块包
0 b 1
−
含 b 1 个元素。我们将这 b(b 1) 个元素 gather 到 u , . . . , u 中，使
0 b 2
− − −
得这 b 1 个区块中的每一个恰好包含 b 个元素，并且我们移除现在为
−
空的 u 。现在 u 的区块包含 b 个元素，然后我们可以从中移除适当
b 1 0
−
的元素。
SE列表
T remove(int i) { Location l = getLocat
ion(i); T y = l.u.d.get(l.j); Node u = l.
u; int r = 0;
while (r < b && u != dummy && u.d.size() == b-1) { u = u.next; r
++; }if (r == b) { // 每个包含 b-1 个元素的 b 块收集(l.u); }u = l.u;
u.d.remove(l.j); while (u.d.size() < b-1 && u.next != dummy) { u.d.a
dd(u.next.d.remove(0)); u = u.next; }if (u.d.isEmpty()) remove(u); n-
-; return y; }
像 add(i, x) 操作一样，remove(i) 操作的运行时间是 O(b + min{i, n i}/
−
b)，如果我们忽略发生在情况 3 中的 gather(u) 方法的成本。

（英文术语：DoublyLinkedList）

## 3.3.5 扩散与收集的摊销分析

接下来，我们考虑可能由 add(i, x) 和 remove(i) 方法执行的 gather(u) 和 spr
ead(u) 方法的成本。为了完整起见，这里列出它们：
SEList
void spread(Node u) {
Node w = u;
for (int j = 0; j < b; j++) {
w = w.next;
}
w = addBefore(w);
while (w != u) {
while (w.d.size() < b)
w.d.add(0,w.prev.d.remove(w.prev.d.size()-1));
w = w.prev;
}
}
SEList
void gather(Node u) {
Node w = u;
for (int j = 0; j < b-1; j++) {
while (w.d.size() < b)
w.d.add(w.next.d.remove(0));
w = w.next;
}
remove(w);
}
每种方法的运行时间主要由两个嵌套循环决定。内循环和外循环最多
各执行 b + 1 次，因此每种方法的总运行时间为 O((b + 1)2) = O(b2)。然而
，以下引理表明，这些方法在每 b 次调用 add(i, x) 或 remove(i) 中最多只
执行一次。
引理 3.1. If an empty SEList is created and any sequence of m 1 calls to 添
≥
加(i, x) and 删除(i) is performed, then the total time spent during all calls to
扩散() and 收集() is O(bm).
Proof. 我们将使用摊销分析的势能方法。我们说一个节点 u 是 fragile 的，
如果 u 的块不包含 b 个元素（因此 u 要么是最后一个节点，要么包含 b
−
1 或 b + 1 个元素）。任何一个块中包含 b 个元素的节点是 rugged。定义
SEList 的 potential 为它包含的脆弱节点的数量。我们将只考虑 add(i, x) 操
作及其与调用 spread(u) 次数的关系。remove(i) 和 gather(u) 的分析是相同
的。
请注意，如果在 add(i, x) 方法中发生情况 1，那么只有一个节点 u 的
r
块大小发生了变化。因此，最多只有一个节点，即 u ，从坚固变为脆弱。
r
如果发生情况 2，则会创建一个新节点，并且该节点是脆弱的，但没有其
他节点的大小发生变化，因此脆弱节点的数量增加了一个。因此，无论是
情况 1 还是情况 2，SEList 的潜在值最多增加 1。
最后，如果发生情况3，是因为 u , . . . , 和 u 都是易碎节点。然后调
0 b 1
−
用 spread(u )，并将这 b 个易碎节点替换为 b+1 个坚固节点。最后，将 x
0
添加到 u 的区块中，使 u 变为易碎节点。总的来说，潜在值减少了 b 1
0 0
−
。
总之，势能从0开始（列表中没有节点）。每次发生情况1或情况2时，
势能最多增加1。每次发生情况3时，势能减少 b 1。势能（计算易碎节
−
点的数量）从不小于0。我们得出结论，对于每次发生情况3，至少有 b
−
1 次情况1或情况2的发生。因此，对于每次调用 spread(u)，至少有 b 次调
用 add(i, x)。这就完成了证明。

（英文术语：DoublyLinkedList）

## 3.3.6 总结

以下定理总结了 SEList 数据结构的性能：
定理 3.3. An SEList implements the 列表 interface. Ignoring the cost
of calls to 展开(u) and 收集(u), an SEList with block size b supports the
operations
• 获取(i) and 设置(i, x) in O(1 + 最小{i, n i}/b) time per operation; and
−
• 添加(i, x) and 移除(i) in O(b + 最小{i, n i}/b) time per operation.
−
Furthermore, beginning with an empty SEList, any sequence of m 添加(i, x)
and 移除(i) operations results in a total of O(bm) time spent during all
calls to 扩展(u) and 收集(u).
The space (measured in words)1 used by an SEList that stores n elements
is n + O(b + n/b).
SEList 是 ArrayList 和 DLList 之间的一种折衷，其中这两种结构的相对
混合取决于块大小 b。在极端情况下，当 b = 2 时，每个 SEList 节点最多
存储三个值，这与 DLList 没有太大不同。在另一个极端，当 b = n 时，所
有元素都存储在单个数组中，就像在 ArrayList 中一样。这两个极端之间
存在一个折衷，即所需时间的权衡
1Recall Section 1.4 for a discussion of how memory is measured.
添加或删除列表项以及查找特定列表项所需的时间。

（中文关键词：数组；英文术语：DoublyLinkedList）
