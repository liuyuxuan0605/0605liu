---
structure: MinHeap
source: book_zh/ods_zh_10_2.md
chapter: 10.1 二叉堆：一种隐式二叉树
section: 10.2
page: 231
kind: textbook
---

# 10.2 可合并堆：一种随机可合并堆

在本节中，我们描述了可合并堆（MeldableHeap），一种优先队列实现，
其底层结构同样是堆序二叉树。然而，不同于底层二叉树完全由元素数量
决定的二叉堆（BinaryHeap），可合并堆的底层二叉树形状没有任何限制
；形状可以是任意的。
MeldableHeap 中的 add(x) 和 remove() 操作是通过 merge(h1, h2) 操作来
实现的。该操作接收两个堆节点 h1 和 h2 并将它们合并，返回一个堆节点
，该节点是一个堆的根，包含以 h1 为根的子树中的所有元素以及以 h2 为
根的子树中的所有元素。
关于 merge(h1, h2) 操作的好处是，它可以递归地定义。见图 10.4。如
果 h1 或 h2 为 nil，那么我们实际上是在与一个空集合合并，所以我们分
别返回 h2 或 h1。否则，假设 h1.x h2.x，因为如果 h1.x > h2.x，那么我
≤
们可以交换 h1 和 h2 的角色。然后我们知道合并堆的根将包含 h1.x，并且
我们可以根据需要递归地将 h2 与 h1.左子树或 h1.右子树合并。这就是随
机化的用武之地，我们抛硬币来决定是将 h2 与 h1.左子树还是 h1.右子树
合并：
MeldableHeap
Node<T> merge(Node<T> h1, Node<T> h2) {
if (h1 == nil) return h2;
h1 merge(h1,h2) h2
4 19
9 8 25 20
17 26 50 16 28 89
19 55 32 93 99
⇓
4
9
merge(h1.right,h2)
17 26
8
19
19
50 16
25 20
55
28 89
32 93 99
图 10.4：合并 h1 和 h2 是通过将 h2 与 h1.left 或 h1.right 中的一个合并来完成的。
if (h2 == nil) return h1; if (compare(h2.x, h1.x) < 0) return merge(
h2, h1); // 现在我们知道 h1.x <= h2.x if (rand.nextBoolean()) { h
1.left = merge(h1.left, h2); h1.left.parent = h1; } else { h1.right =
merge(h1.right, h2); h1.right.parent = h1; }return h1;
} 在
在下一部分中，我们展示了 merge(h1, h2) 在 O(lo 中运行g n) ex-
pect ed 时间，其中 n 是 h1 a 中元素的总数 和 h2。
通过访问 merge(h1, h2) 操作，add(x) 操作很简单。我们创建一个包含
x 的新节点 u，然后将 u 与我们堆的根节点合并：
MeldableHeap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
r = merge(u, r);
r.parent = nil;
n++;
return true;
}
这需要 O(log(n + 1)) = O(log n) 的预期时间。
remove() 操作同样很简单。我们想要移除的节点是根节点，所以我们
只需将它的两个子节点合并，并将结果设为根节点：
MeldableHeap
T remove() {
T x = r.x;
r = merge(r.left, r.right);
if (r != nil) r.parent = nil;
n--;
return x;
}
同样，这需要 O(log n) 的期望时间。
此外，MeldableHeap 可以在 O(log n) 的期望时间内实现许多其他操作
，包括：
• remove(u)：从堆中移除节点 u（以及它的键 u.x）。
• 吸收(h)：将 MeldableHeap h 的所有元素添加到此堆中，同时清空 h
。
每个这些操作都可以通过使用常数次数的 merge(h1, h2) 操作来实现，每次
操作的预期时间为 O(log n)。

（中文关键词：堆、可合并堆；英文术语：MinHeap）

## 10.2.1 merge(h1, h2) 的分析

对 merge(h1, h2) 的分析是基于对二叉树中随机游走的分析。二叉树中的
random walk 从树的根节点开始。在随机游走的每一步，会掷一次硬币，
根据硬币的结果，游走会向当前节点的左子节点或右子节点进行。当游走
掉出树之外（当前节点变为 nil）时，游走结束。
下面的引理有些值得注意，因为它完全不依赖于二叉树的形状：
引理 10.1. The expected length of a random walk in a binary tree with n
nodes is at most log(n + 1).
Proof. 证明是通过对 n 进行归纳。 在基例中，n = 0 且行走的长度为 0 = l
og(n + 1)。 现在假设该结果对所有非负整数 n < n 都成立。
(cid:48)
设 n 表示根节点左子树的大小，那么 n = n n 1 就是根节点右子
1 2 1
− −
树的大小。从根节点开始，行走走一步，然后继续在大小为 n 或 n 的子
1 2
树中进行。根据我们的归纳假设，行走的期望长度为
1 1
E[W ] = 1 + log(n + 1) + log(n + 1) ,
1 2
2 2
由于 n 和 n 都小于 n。由于对数是一个凹函数，E[W] 在 n = n = (n 1
1 2 1 2
−
)/2 时达到最大值。因此，随机游走的预期步数是
1 1
E[W ] = 1 + log(n + 1) + log(n + 1)
1 2
2 2
1 + log((n 1)/2 + 1)
≤ −
= 1 + log((n + 1)/2)
= log(n + 1) .
我们快速插入一段说明，对于对信息论略有了解的读者，Lemma 10.1
的证明可以用熵来表述。
Information Theoretic Proof of Lemma 10.1. 令 d 表示第 i 个外部节点的深
i
度，并回忆一个有 n 个节点的二叉树有 n + 1 个外部节点。随机游走到达
第 i 个外部节点的概率恰好是 p
i
= 1/2di，因此随机游走的期望长度为
n n n
H = p d = p log 2di = p log(1/p )
i i i i i
i=0 i=0 i=0
(cid:88) (cid:88) (cid:16) (cid:17) (cid:88)
这个方程的右侧很容易被识别为对 n + 1 个元素的概率分布的熵。关于对
n + 1 个元素的分布的熵的一个基本事实是，它不会超过 log(n + 1)，这证
明了该引理。
有了关于随机游走的这个结果，我们现在可以轻松地证明 merge(h1, h2
) 操作的运行时间是 O(log n)。
引理 10.2. If h1 and h2 are the roots of two heaps containing n and n
1 2
nodes, respectively, then the expected running time of 合并(h1, h2) is at most
O(log n), where n = n + n .
1 2
Proof. 合并算法的每一步都执行随机游走的一步，要么在以 h1 为根的堆
中，要么在以 h2 为根的堆中。当这两个随机游走中的任意一个走出其对
应的树（当 h1 = null 或 h2 = null）时，算法终止。因此，合并算法执行的
步骤预期次数最多为
log(n + 1) + log(n + 1) 2 log n .
1 2
≤

（中文关键词：二叉树、堆、树；英文术语：MinHeap）

## 10.2.2 总结

下列定理总结了可合并堆的性能：
定理 10.2. A 可合并堆 implements the (priority) 队列 interface. A 可合并堆
supports the operations 添加(x) and 移除() in O( log n )
expected time per operation.

（英文术语：MinHeap）
