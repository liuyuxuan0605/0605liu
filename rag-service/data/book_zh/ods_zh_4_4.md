---
structure: 
source: book_zh/ods_zh_4_4.md
chapter: 4.1 基本结构
section: 4.4
page: 112
kind: textbook
---

# 4.4 跳表的分析

## 跳表的分析 (1/2)

在本节中，我们分析跳表中搜索路径的预期高度、大小和长度。本节需要
具备基本概率的背景知识。几个证明基于关于抛硬币的以下基本观察。
引理 4.2. Let T be the number of times a fair coin is tossed up to and
including the first time the coin comes up heads. Then E[T] = 2.
Proof. 假设我们在第一次抛硬币出现正面时停止抛掷。定义指示变量
0 if the coin is tossed less than i times
I =
i 1 if the coin is tossed i or more times
(cid:40)
请注意，I = 1 当且仅当前 i 1 次抛硬币都是反面，因此 E[I ] = Pr{I = 1
i i i
−
} = 1/2i − 1。注意到 T ，抛硬币的总次数，可以写成 T = ∞i=1 I i 。因此，
(cid:80)
∞
E[T ] = E I
i
 
i=1
=
∞
 (cid:88)
E [I ]

i
i=1
(cid:88)
= ∞ 1/2i
−
1
i=1
(cid:88)
= 1 + 1/2 + 1/4 + 1/8 +
· · ·
= 2 .
接下来的两个引理告诉我们，跳表具有线性大小：
引理 4.3. The expected number of nodes in a skiplist containing n ele-
ments, not including occurrences of the sentinel, is 2n.
Proof. 任何特定元素 x 被包含在列表 L 中的概率是 1/2r，因此 L 中节点
r r
的预期数量是 n/2r.2 因此，所有列表中节点的总预期数量是
∞ n/2r = n(1 + 1/2 + 1/4 + 1/8 + ) = 2n .
· · ·
r=0
(cid:88)
引理 4.4. The expected height of a skiplist containing n elements is at most log
n + 2.
Proof. 对于每个 r {1, 2, 3, . . . , }，定义指示随机变量
∈ ∞
0 if L is empty
I = r
r 1 if L is non-empty
r
(cid:40)
参见第1.3.4节，了解如何使用指示变量和期望的线性性来推导这一点。
跳表的高度 h 定义为
∞
h = I .
r
i=1
(cid:88)
请注意，I 永远不会超过 L 的长度 L ，所以
r r r
| |
E[I ] E[ L ] = n/2r .
r r
≤ | |
因此，我们有
∞
E[h] = E I
r
r=1 
=
∞
 (cid:88)
E[I ]

r
r=1
(cid:88)
logn
(cid:98) (cid:99) ∞
= E[I ] + E[I ]
r r
r=1 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
(cid:98) (cid:99) 1 + ∞ n/2r
≤
r=1 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
log n + ∞ 1/2r
≤
r=0
(cid:88)
= log n + 2 .
引理 4.5. The expected number of nodes in a skiplist containing n ele-
ments, including all occurrences of the sentinel, is 2n + O(log n).
Proof. 根据引理 4.3，预期的节点数（不包括哨兵节点）是 2n。哨兵节点
的出现次数等于跳表的高度 h，因此根据引理 4.4，哨兵节点的预期出现次
数至多是 log n + 2 = O(log n)。
引理 4.6. The expected length of a search path in a skiplist is at most 2 对
数 n + O(1).
Proof. 看这个最简单的方法是考虑节点 x 的 reverse search path。这条路径
从 L 中 x 的前驱开始。在任何时刻
时间，如果路径可以向上一个等级，那么它就向上。如果它不能向上一个
等级，那么它就向左。思考这一点几分钟会让我们相信，x 的反向搜索路
径与 x 的搜索路径是相同的，只是顺序相反。
在特定层次 r 上，反向搜索路径访问的节点数量与以下实验有关：抛
一枚硬币。如果硬币正面朝上，则向上移动并停止。否则，向左移动并重
复实验。在出现正面之前的抛硬币次数表示反向搜索路径在特定层次向左
移动的步数。引理 4.2 告诉我们，在第一次出现正面之前，抛硬币的期望
次数是 1。

（中文关键词：跳表）

## 跳表的分析 (2/2)

令 S 表示前向搜索路径在第 r 级向右走的步数。我们刚才已经论证了
r
E[S ] 1。此外，S L ，因为我们不能在 L 中采取比 L 的长度更多
r r r r r
≤ ≤ | |
的步数，所以
E[S ] E[ L ] = n/2r .
r r
≤ | |
我们现在可以像在引理 4.4 的证明中一样完成。设 S 为跳表中某个节点 u
的搜索路径长度，h 为跳表的高度。然后
∞
E[S] = E h + S
r
 r=0 
= E[
h]
+
(cid:88)
∞
E[
S
]
r
r=0
(cid:88)
logn
(cid:98) (cid:99) ∞
= E[h] + E[S ] + E[S ]
r r
r=0 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
E[h] + (cid:98) (cid:99) 1 + ∞ n/2r
≤
r=0 r= logn +1
(cid:88) (cid:98)(cid:88)(cid:99)
logn
E[h] + (cid:98) (cid:99) 1 + ∞ 1/2r
≤
r=0 r=0
(cid:88) (cid:88)
3Note that this might overcount the number of steps to the left, since the experiment
should end either at the first heads or when the search path reaches the sentinel, whichever
comes first. This is not a problem since the lemma is only stating an upper bound.
logn
E[h] + (cid:98) (cid:99) 1 + ∞ 1/2r
≤
r=0 r=0
(cid:88) (cid:88)
E[h] + log n + 3
≤
2 log n + 5 .
≤
以下定理总结了本节的结果：
定理 4.3. A skiplist containing n elements has expected size O(n) and
the expected length of the search path for any particular element is at most
2 log n + O(1).

（中文关键词：跳表）
