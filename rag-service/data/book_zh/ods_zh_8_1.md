---
structure: AVLTree
source: book_zh/ods_zh_8_1.md
chapter: 8.1 替罪羊树：一种带部分重建的二叉搜索树
section: 8.1
page: 188
kind: textbook
---

# 8.1 替罪羊树：一种带部分重建的二叉搜索树

替罪羊树是一种二叉搜索树，除了跟踪树中的节点数 n 之外，还维护一个
计数器 q，用于保持节点数量的上界。
ScapegoatTree
int q;
7
6 8
5 9
2
1 4
0 3
图 8.1：一个有 10 个节点、高度为 5 的替罪羊树。
在任何时候，n 和 q 都遵守以下不等式：
q/2 n q .
≤ ≤
此外，替罪羊树具有对数高度；在任何时候，替罪羊树的高度都不超过：
log q log 2n < log n + 2 . (8.1)
3/2 ≤ 3/2 3/2
即使有这个限制，替罪羊树看起来也可能极不平衡。图 8.1 中的树有 q = n
= 10，高度为 5 < log 10 5.679。
3/2 ≈
在 ScapegoatTree 中实现 find(x) 操作是使用在二叉搜索树中搜索的标准
算法（见第 6.2 节）完成的。这需要的时间与树的高度成正比，根据 (8.1)
，为 O(log n)。
要实现 add(x) 操作，我们首先增加 n 和 q，然后使用将 x 添加到二叉
搜索树的常规算法；我们搜索 x，然后添加一个新的叶子节点 u，并使 u{x
} = x。在这一点上，我们可能很幸运，u 的深度可能不会超过 log q。如果
是这样，那么我们就保持原样，不做其他任何操作。
不幸的是，有时会发生 depth(u) > log q。在这种情况下，我们需要
3/2
降低高度。这不是一项大工作；只有
一个节点，即 u，其深度超过 log q。为了修复 u，我们从 u 向上走到根
3/2
节点寻找一个 scapegoat，w。替罪羊节点 w 是一个非常不平衡的节点。它
具有如下属性
size(w.child) 2
> , (8.2)
size(w) 3
其中 w.child 是从根到 u 的路径上 w 的子节点。我们很快就会证明替罪羊
的存在。现在，我们可以先默认它存在。一旦找到替罪羊 w，我们会完全
销毁以 w 为根的子树，并将其重建为一个完全平衡的二叉搜索树。根据 (
8.2)，即使在添加 u 之前，w 的子树也不是完全二叉树。因此，当我们重
建 w 时，高度至少减少 1，从而使 ScapegoatTree 的高度再次至多为 log
3/2
q。
ScapegoatTree
boolean add(T x) {
// first do basic insertion keeping track of depth
Node<T> u = newNode(x);
int d = addWithDepth(u);
if (d > log32(q)) {
// depth exceeded, find scapegoat
Node<T> w = u.parent;
while (3*size(w) <= 2*size(w.parent))
w = w.parent;
rebuild(w.parent);
}
return d >= 0;
}
如果我们忽略寻找替罪羊 w 以及重建以 w 为根的子树的成本，那么 ad
d(x) 的运行时间将主要取决于初始搜索，其耗时为 O(log q) = O(log n) 时
间。我们将在下一节中使用摊销分析来考虑寻找替罪羊和重建的成本。
在 ScapegoatTree 中，remove(x) 的实现非常简单。我们搜索 x 并使用
从二叉搜索树中删除节点的常规算法将其删除。（请注意，这永远不会增
加
7 7
6 8 6 8
5 6 > 2 9 3 9
7 3
2 3 1 4
6
1 4 2 0 2 3.5 5
3
0 3 1
2
3.5
图 8.2：将 3.5 插入 ScapegoatTree 会将其高度增加到 6，这违反了 (8.1)，因为 6 > l
og3/2 11 5.914。在包含 5 的节点上找到了替罪羊。
≈
树的高度。) 接下来，我们将 n 减 1，但保持 q 不变。最后，我们检查 q
是否 > 2n，如果是，那么我们将其 rebuild the entire tree 成一个完美平衡
的二叉搜索树，并将 q 设置为 = n。
ScapegoatTree
boolean remove(T x) {
if (super.remove(x)) {
if (2*n < q) {
rebuild(r);
q = n;
}
return true;
}
return false;
}
再次，如果我们忽略重建的成本，remove(x) 操作的运行时间与树的高
度成正比，因此是 O(log n)。

（中文关键词：替罪羊树、树；英文术语：AVLTree）

## 8.1.1 正确性和运行时间分析 (1/2)

在本节中，我们分析 ScapegoatTree 上操作的正确性和摊还运行时间。我
们首先通过展示当 add(x) 操作导致某个节点违反条件 (8.1) 时，我们总是
可以找到一个替罪羊节点，来证明其正确性：
引理 8.1. Let u be a node of depth h > log q in a 替罪羊树. Then
3/2
there exists a node w on the path from u to the root such that
size(w)
> 2/3 .
size(parent(w))
Proof. 你好假设，为了反证，这不是这种情况 看，然后
size(w)
2/3 .
size(parent(w)) ≤
对于从 u 到根的路径上的所有节点 w。将从根到 u 的路径表示为 r = u
, . . . , u = u。然后，我们有 size(u ) = n, size(u ) 2 n, size(u ) 4 n，并且
0 h 0 1 ≤ 3 2 ≤ 9
，更一般地，
2 i
size(u ) n .
i ≤ 3
(cid:18) (cid:19)
但这产生了矛盾，因为 size(u) 1，因此
≥
2 h 2 log 3/2 q 2 log 3/2 n 1
1 size(u) n < n n = n = 1 .
≤ ≤ 3 3 ≤ 3 n
(cid:18) (cid:19) (cid:18) (cid:19) (cid:18) (cid:19) (cid:18) (cid:19)
接下来，我们分析运行时间中尚未计算的部分。有两个部分：在搜索
替罪羊节点时调用 size(u) 的成本，以及在找到替罪羊 w 时调用 rebuild(w)
的成本。调用 size(u) 的成本可以与调用 rebuild(w) 的成本相关联，如下所
示：
引理 8.2. During a call to add(x) in a 替罪羊树 , the cost of finding
the scapegoat w and rebuilding the subtree rooted at w is O(大小(w)).
Proof. 一旦我们找到替罪羊节点 w，重建它的成本是 O(size(w))。在搜索
替罪羊节点时，我们在 u 上调用 size(u)
节点序列 u , . . . , u 直到我们找到替罪羊 u = w。然而，由于 u 是该序列
0 k k k
中第一个是替罪羊的节点，我们知道
2
size(u ) < size(u )
i 3 i+1
对于所有 i {0, . . . , k 2}。因此，所有对 size(u) 的调用成本是
∈ −
k k 1
−
O size(u ) = O size(u ) + size(u )
k i k k i 1
 −   − − 
i=0 i=0
 (cid:88)   (cid:88)
k − 1 2 i

= O size(u ) + size(u )
k 3 k
 
 (cid:88) i=0
k
(cid:18)
− 1
(cid:19)
2 i

= O size(u ) 1 +
k 3
  
= O(

size(u
k
))

= O(
(cid:88) i
s
=
i
0
z
(cid:18)
e(
(cid:19)
w)

)

,
最后一行来源于这个事实，即该和是一个几何递减级数。
剩下的就是证明在一系列 m 操作中对 rebuild(u) 的所有调用的成本上
界：
引理 8.3. Starting with an empty 替罪羊树 any sequence of m 添加(x) and
移除(x) operations causes at most O(m 日志 m) time to be used by 重建(u)
operations.
Proof. 为了证明这一点，我们将使用一个 credit scheme。我们假设每个节
点存储一定数量的信用。每个信用可以支付重建所花费的一些常数 c 时间
单位。该方案总共发放了 O(m log m) 个信用，每次调用 rebuild(u) 都由存
储在 u 的信用支付。
在插入或删除过程中，我们给通向被插入节点或被删除节点 u 的路径
上的每个节点分配一个信用。这样，每次操作我们最多分配 log q log
3/2 ≤
m 个信用。在删除过程中，我们还会额外存储一个“备用”信用。因
3/2
此，总体上我们最多分配 O(m log m) 个信用。剩下的就是要证明这些信
用足以支付所有对 rebuild(u) 的调用。
如果我们在插入过程中调用 rebuild(u)，那是因为 u 是替罪羊。假设，
不失一般性，
size(u.left) 2
> .
size(u) 3
利用这个事实
size(u) = 1 + size(u.left) + size(u.right)
我们推断出
1
size(u.left) > size(u.right)
2
因此
1 1
size(u.left) size(u.right) > size(u.left) > size(u) .
− 2 3
现在，上一次包含 u 的子树被重建时（或者如果从未重建过包含 u 的子树
，则在 u 被插入时），我们有
size(u.left) size(u.right) 1 .
− ≤
因此，自那时起，影响 u.left 或 u.right 的 add(x) 或 remove(x) 操作的次数
至少为
1
size(u) 1 .
3 −
因此，在 u 中至少存储了这么多的信用，可用于支付调用 rebuild(u) 所需
的 O(size(u)) 时间。

（中文关键词：替罪羊树、树；英文术语：AVLTree）

## 8.1.1 正确性和运行时间分析 (2/2)

如果我们在删除过程中调用 rebuild(u)，那是因为 q > 2n。在这种情况
下，我们有 q n > n 个积分存储在“旁边”，我们使用这些积分来支付重
−
建根节点所需的 O(n) 时间。这完成了证明。

（英文术语：AVLTree）

## 8.1.2 总结

下列定理总结了替罪羊树数据结构的性能：
定理 8.1. A 替罪羊树 implements the 有序集合 interface. Ignoring
the cost of 重建(u) operations, a 替罪羊树 supports the operations 添加(x) ,
删除(x) , and 查找(x) in O( log n ) time per operation.
Furthermore, beginning with an empty 替罪羊树, any sequence of m 添
加(x) and 移除(x) operations results in a total of O(m 日志 m) time spent
during all calls to 重建(u).

（英文术语：AVLTree）
