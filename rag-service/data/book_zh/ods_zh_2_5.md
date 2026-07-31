---
structure: Deque
source: book_zh/ods_zh_2_5.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.5
page: 57
kind: textbook
---

# 2.5 双数组双端队列：用两个栈构建双端队列

## 双数组双端队列：用两个栈构建双端队列 (1/2)

接下来，我们介绍一种数据结构——双数组双端队列（DualArrayDeque）
，它通过使用两个数组栈（ArrayStacks）实现与数组双端队列（ArrayDeq
ue）相同的性能界限。尽管双数组双端队列的渐近性能并不优于数组双端
队列，但它仍然值得研究，因为它提供了一个很好的例子，展示了如何通
过结合两种更简单的数据结构来构建一个复杂的数据结构。
DualArrayDeque 使用两个 ArrayStacks 来表示一个列表。回想一下，当
对 ArrayStack 的操作修改元素时，它是很快的
接近末端。DualArrayDeque 将两个 ArrayStack 放置在一起，称为 front 和
back，使得在任一端的操作都很快。
DualArrayDeque
List<T> front;
List<T> back;
DualArrayDeque 并不会显式地存储其包含的元素数量 n。它不需要这
样做，因为它包含 n = front.size() + back.size() 个元素。尽管如此，在分析
DualArrayDeque 时，我们仍将使用 n 来表示它包含的元素数量。
DualArrayDeque
int size() {
return front.size() + back.size();
}
前端 ArrayStack 存储索引在 0 到 front.size() - 1 的列表元素，但以逆序
存储。后端 ArrayStack 包含索引在 front.size() 到 size() - 1 的列表元素，按
正常顺序存储。通过这种方式，get(i) 和 set(i, x) 可以转换为对前端或后端
的相应 get(i) 或 set(i, x) 调用，每次操作耗时 O(1)。
DualArrayDeque
T get(int i) {
if (i < front.size()) {
return front.get(front.size()-i-1);
} else {
return back.get(i-front.size());
}
}
T set(int i, T x) {
if (i < front.size()) {
return front.set(front.size()-i-1, x);
} else {
return back.set(i-front.size(), x);
}
}
front back
a b c d
add(3,x)
a b c x d
add(4,y)
a b c x y d
remove(0)
∗
b c x y d
b c x y d
4 3 2 1 0 0 1 2 3 4
图2.4：在双数组双端队列上的add(i,x)和remove(i)操作序列。箭头表示正在复制的
元素。导致通过balance()进行重新平衡的操作标有星号。
请注意，如果索引 i 小于 front 的大小，那么它对应于 front 中位置为 fr
ont 的大小减 1 的元素，因为 front 中的元素是按相反顺序存储的。
在图 2.4 中说明了如何向 DualArrayDeque 添加和移除元素。add(i, x)
操作根据需要操作前端或后端：
DualArrayDeque
void add(int i, T x) {
if (i < front.size()) {
front.add(front.size()-i, x);
} else {
back.add(i-front.size(), x);
}
balance();
}
add(i, x) 方法通过调用 balance() 方法对两个 ArrayStacks front 和 back
进行重新平衡。其实现
balance() 的作用如下所述，但目前只需知道 balance() 确保，除非 size() <
2，否则 front.size() 和 back.size() 的差异不会超过 3 倍。具体来说，3 · fron
t.size() back.size()，以及 3 · back.size() front.size()。
≥ ≥
接下来我们分析 add(i, x) 的成本，不考虑对 balance() 的调用成本。如
果 i < front.size()，那么 add(i, x) 的实现是通过调用 front.add(front.size() i
−
1, x) 来完成的。由于 front 是一个 ArrayStack，其成本是
−
O(front.size() (front.size() i 1) + 1) = O(i + 1) . (2.1)
− − −
另一方面，如果我 i front.size()，那么 add(i, x) 就实现为 back.add(i fron
≥ −
t.size(), x)。其成本是
O(back.size() (i front.size()) + 1) = O(n i + 1) . (2.2)
− − −
请注意，第一个情况 (2.1) 发生在 i < n/4 时。第二个情况 (2.2) 发生在 i
3n/4 时。当 n/4 i < 3n/4 时，我们无法确定该操作是影响前面还是后面
≥ ≤
，但无论哪种情况，该操作都需要 O(n) = O(i) = O(n i) 时间，因为 i n
− ≥
/4 且 n i > n/4。总结这种情况，我们有
−
O(1 + i) if i < n/4
Running time of add(i, x) O(n) if n/4 i < 3n/4
≤  ≤
 O(1 + n
−
i) if i
≥
3n/4
因此，如果我们忽略对 balance() 的

调用成本，add(i, x) 的运行时间是 O(1
+ 最小{i, n i})。
−
remove(i) 操作及其分析类似于 add(i, x) 操作及分析。

（中文关键词：数组、双端队列、栈；英文术语：Deque）

## 双数组双端队列：用两个栈构建双端队列 (2/2)

双数组双端队列
T remove(int i) { T x; if (i < front.size()) { x = fron
t.remove(front.size() - i - 1); } else { x = back.re
move(i - front.size()); } balance();}
返回 x;
}

（英文术语：Deque）

## 2.5.1 平衡

最后，我们来看 add(i, x) 和 remove(i) 执行的 balance() 操作。该操作确保
前部或后部不会变得过大（或过小）。它确保，除非元素少于两个，否则
前部和后部各至少包含 n/4 个元素。如果情况不是这样，则会在它们之间
移动元素，使前部和后部分别正好包含 n/2 个元素和 n/2 个元素。
(cid:98) (cid:99) (cid:100) (cid:101)
DualArrayDeque
void balance() {
int n = size();
if (3*front.size() < back.size()) {
int s = n/2 - front.size();
List<T> l1 = newStack();
List<T> l2 = newStack();
l1.addAll(back.subList(0,s));
Collections.reverse(l1);
l1.addAll(front);
l2.addAll(back.subList(s, back.size()));
front = l1;
back = l2;
} else if (3*back.size() < front.size()) {
int s = front.size() - n/2;
List<T> l1 = newStack();
List<T> l2 = newStack();
l1.addAll(front.subList(s, front.size()));
l2.addAll(front.subList(0, s));
Collections.reverse(l2);
l2.addAll(back);
front = l1;
back = l2;
}
}
这里 t 这里几乎没有可以分析的。如果 balance() 操作做 重新平衡
ancing，然后它会移动 O(n) 个元素，这需要 O(n) 时间。这很糟糕，因为
每次调用 add(i, x) 和 remove(i) 时都会调用 balance()。然而，下面的引理
表明，平均而言，balance() 每次操作只花费恒定的时间。
引理 2.2. If an empty 双端数组双端队列 is created and any sequence of
m 1 calls to 添加(i, x) and 删除(i) are performed, then the total time
≥
spent during all calls to 平衡() is O(m).
Proof. 我们将展示，如果 balance() 被迫移动元素，那么自上次 balance()
移动任何元素以来，add(i, x) 和 remove(i) 操作的次数至少为 n/2 1。与引
−
理 2.1 的证明中一样，这足以证明 balance() 花费的总时间为 O(m)。
我们将使用一种称为 potential method 的技术来进行分析。将 DualArra
yDeque 的 potential、Φ 定义为前部和后部之间大小的差异：
Φ = front.size() back.size() .
| − |
关于这个势能有趣的是，对 add(i, x) 或 remove(i) 的调用如果不进行任何
平衡，最多只能使势能增加1。
注意到，在一次调用 balance() 并移动元素之后，势能 Φ 至多为 1，因
0
为
Φ = n/2 n/2 1 .
0
|(cid:98) (cid:99) − (cid:100) (cid:101)| ≤
考虑在调用 balance() 之前立即的情况，它会移动元素，并假设在不失
一般性的情况下，balance() 正在移动元素因为 3front.size() < back.size()。
注意，在这种情况下，
n = front.size() + back.size()
< back.size()/3 + back.size()
4
= back.size()
此外，此时此刻的潜力是
Φ = back.size() front.size()
1
−
> back.size() back.size()/3
−
2
= back.size()
3
2 3
> n
3 × 4
= n/2
因此，自上次 balance() 移动元素以来，对 add(i, x) 或 remove(i) 的调用次
数至少为 Φ Φ > n/2 1。这就完成了证明。
1 0
− −

（中文关键词：栈、双端队列、数组；英文术语：Deque）

## 2.5.2 总结

下列定理总结了双数组双端队列的性质：
定理 2.4. A 双数组双端队列 implements the 列表 interface. Ignoring
the cost of calls to 调整大小() and 平衡(), a 双数组双端队列 supports the
operations
• 获取(i) and 设置(i, x) in O(1) time per operation; and
• 添加(i, x) and 删除(i) in O(1 + 最小{i, n i}) time per operation.
−
Furthermore, beginning with an empty DualArrayDeque, any sequence of m
添加(i, x) and 删除(i) operations results in a total of O(m) time spent dur-
ing all calls to 调整大小() and 平衡().

（中文关键词：数组、双端队列；英文术语：Deque）
