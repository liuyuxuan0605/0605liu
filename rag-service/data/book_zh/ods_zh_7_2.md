---
structure: BST
source: book_zh/ods_zh_7_2.md
chapter: 7.1 随机二叉搜索树
section: 7.2
page: 173
kind: textbook
---

# 7.2 Treap：一种随机化二叉搜索树

## Treap：一种随机化二叉搜索树 (1/3)

随机二叉搜索树的问题当然在于，它们不是动态的。它们不支持实现 SSet
接口所需的 add(x) 或 remove(x) 操作。在本节中，我们将描述一种称为 Tr
eap 的数据结构，该数据结构使用引理 7.1 来实现 SSet 接口。2
Treap 中的一个节点就像二叉搜索树中的节点一样，它有一个数据值 x
，但它还包含一个唯一的随机分配的数值 priority，p：
Treap
class Node<T> extends BSTNode<Node<T>,T> {
int p;
}
除了是二叉搜索树之外，Treap 中的节点还遵循 heap property：
• (堆性质) 在每个节点 u 上，除了根节点，u.的父节点.为 p < u.为 p。
换句话说，每个节点的优先级都小于其两个子节点的优先级。示例如图7.5
所示。
堆和二叉搜索树的条件共同确保，一旦每个节点的键（x）和优先级（
p）被定义，Treap 的形状就完全确定。堆属性告诉我们节点
2The names Treap comes from the fact that this data structure is simultaneously a binary
search tree (Section 6.2) and a heap (Chapter 10).
3, 1
1, 6 5, 11
0, 9 2, 99 4, 14 9, 17
7, 22
6, 42 8, 49
图 7.5：一个包含整数 0 到 9 的 Treap 示例。每个节点 u 都表示为一个包含 u、x 和
u 的 p 的方框。
具有最低优先级的必须是 Treap 的根，r。二叉搜索树的性质告诉我们，所
有键小于 r.x 的节点都存储在以 r.left 为根的子树中，而所有键大于 r.x 的
节点都存储在以 r.right 为根的子树中。
关于 Treap 中优先级值的重要一点是，它们是唯一的并且随机分配的
。正因为如此，我们可以用两种等效的方式来理解 Treap。如上所定义，T
reap 遵循堆和二叉搜索树的性质。或者，我们可以将 Treap 看作是一个二
叉搜索树，其节点是按照优先级递增的顺序添加的。例如，图 7.5 中的 Tr
eap 可以通过添加 (x, p) 值的序列来获得。
(3, 1), (1, 6), (0, 9), (5, 11), (4, 14), (9, 17), (7, 22), (6, 42), (8, 49), (2, 99)
(cid:104) (cid:105)
变成一个二叉搜索树。
由于优先级是随机选择的，这相当于对键进行随机排列——在这种情
况下排列是
3, 1, 0, 5, 9, 4, 7, 6, 8, 2
(cid:104) (cid:105)
——并将这些添加到二叉搜索树中。但这意味着 treap 的形状与随机二叉
搜索树的形状相同。在
特别地，如果我们将每个键 x 替换为它的秩 3，那么引理 7.1 就适用。用
Treaps 来重新表述引理 7.1，我们有：
引理 7.2. In a Treap that stores a set S of n keys, the following statements
hold:
1. For any x S, the expected length of the search path for x is H +
r(x)+1
∈
H O(1).
n r(x)
− −
2. For any x (cid:60) S, the expected length of the search path for x is H +
r(x)
H .
n r(x)
−
Here, r(x) denotes the rank of x in the set S {x}.
∪
再次，我们强调引理 7.2 中的期望是针对每个节点的优先级的随机选择
而言的。它不要求关于键的随机性做任何假设。
引理 7.2 告诉我们，Treap 可以高效地实现 find(x) 操作。然而，Treap
的真正好处在于它可以支持 add(x) 和 delete(x) 操作。为了做到这一点，它
需要执行旋转以维持堆性质。参见图 7.6。二叉搜索树中的 rotation 是一
种局部修改，它将节点 w 的父节点 u 改为 w 的子节点，同时保持二叉搜
索树的性质。旋转有两种类型：left 或 right，取决于 w 是 u 的右孩子还是
左孩子。

（中文关键词：树堆、堆、旋转、树；英文术语：BST）

## Treap：一种随机化二叉搜索树 (2/3)

实现这一功能的代码必须处理这两种可能性，并注意一个边界情况（
当 u 是根节点时），所以实际代码比图 7.6 给读者的印象要长一些：
BinarySearchTree
void rotateLeft(Node u) {
Node w = u.right;
w.parent = u.parent;
if (w.parent != nil) {
if (w.parent.left == u) {
w.parent.left = w;
} else {
3The rank of an element x in a set S of elements is the number of elements in S that are
less than x.
u w
w u
rotateRight(u)
⇒
C rotateLeft(w) A
⇐
A B B C
图 7.6：二叉搜索树中的左旋和右旋。
w.parent.right = w; } }u.right = w.left; if (u.r
ight != nil) { u.right.parent = u; }u.parent = w; w.left
= u; if (u == r) { r = w; r.parent = nil; } }void rotateR
ight(Node u) { Node w = u.left; w.parent = u.parent;
if (w.parent != nil) { if (w.parent.left == u) { w.paren
t.left = w; } else { w.parent.right = w; } }u.left = w.ri
ght; if (u.left != nil) { u.left.parent = u; }u.parent = w
; w.right = u;
如果 (u == r) { r = w; r.parent = nil; } }
在 Treap 数据结构中，旋转最重要的属性是 w 的深度减少一，而 u 的
深度增加一。
使用旋转，我们可以如下实现 add(x) 操作：我们创建一个新节点 u，
赋值 u{x} = x，并为 u{p} 随机选择一个值。接着，我们使用二叉搜索树的
常规 add(x) 算法将 u 添加进去，使得 u 现在成为 Treap 的一个叶子节点。
此时，我们的 Treap 满足二叉搜索树的性质，但不一定满足堆的性质。特
别地，可能出现 u{parent}{p} > u{p} 的情况。如果出现这种情况，我们就
在节点 w{u}{parent} 处进行旋转，使 u 成为 w 的父节点。如果 u 继续违
反堆的性质，我们将必须重复此操作，每次使 u 的深度减少一，直到 u 成
为根节点或者 u{parent}{p} > u{p}。
Treap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
u.p = rand.nextInt();
if (super.add(u)) {
bubbleUp(u);
return true;
}
return false;
}
void bubbleUp(Node<T> u) {
while (u.parent != nil && u.parent.p > u.p) {
if (u.parent.right == u) {
rotateLeft(u.parent);
} else {
rotateRight(u.parent);
}
}
if (u.parent == nil) {
r = u;
}
}
图 7.7 显示了 add(x) 操作的一个例子。
add(x) 操作的运行时间由寻找 x 的搜索路径所需的时间加上为将新添
加的节点 u 移动到 Treap 中正确位置而执行的旋转次数决定。根据引理 7.
2，搜索路径的期望长度至多为 2 ln n + O(1)。此外，每次旋转都会减少 u
的深度。如果 u 成为根节点，则旋转停止，因此期望旋转次数不会超过搜
索路径的期望长度。因此，Treap 中 add(x) 操作的期望运行时间为 O(log n
)。(练习 7.5 要求你证明在一次添加过程中执行的旋转次数的期望实际上
仅为 O(1)。)
Treap 中的 remove(x) 操作与 add(x) 操作相反。我们首先搜索包含 x 的
节点 u，然后执行旋转将 u 向下移动，直到它成为叶子节点，然后将 u 从
Treap 中删除。注意，为了将 u 向下移动，我们可以在 u 处执行左旋或右
旋，这将分别用 u 的右子节点或左子节点替换 u。选择哪种旋转取决于以
下首先适用的情况：
1. 如果 u.left 和 u.right 都为空，那么 u 是叶子节点，不进行旋转。 2. 如
果 u.left（或 u.right）为空，则在 u 处分别执行右旋（或左旋）。 3. 如
果 u.left.p < u.right.p（或 u.left.p > u.right.p），则在 u 处分别执行右旋
（或左旋）。
这三条规则确保 Treap 不会断开连接，并且在移除 u 后堆属性能够恢复。

（中文关键词：树堆、树；英文术语：BST）

## Treap：一种随机化二叉搜索树 (3/3)

Treap 布尔值 rem
ove(T x) { 节点<T> u = findLast(x); 如果 (u != nil &
& compare(u.x, x) == 0) { trickleDown(u); splice(u);
返回 true;
3, 1
1, 6 5, 11
0, 9 2, 99 4, 14 9, 14
1.5, 4 7, 22
6, 42 8, 49
3, 1
1, 6 5, 11
0, 9 1.5, 4 4, 14 9, 14
2, 99 7, 22
6, 42 8, 49
3, 1
1.5, 4 5, 11
1, 6 2, 99 4, 14 9, 14
0, 9 7, 22
6, 42 8, 49
图 7.7：将值 1.5 添加到图 7.5 的 Treap 中。
}返回 false; }void 下沉(Node<T> u) { while (u.left !
= nil || u.right != nil) { if (u.left == nil) { 左旋(u); } els
e if (u.right == nil) { 右旋(u); } else if (u.left.p < u.right.
p) { 右旋(u); } else { 左旋(u); }if (r == u) { r = u.parent;
} } }
Figure 7.8 显示了 remove(x) 操作的一个例子。
分析 remove(x) 操作运行时间的关键是注意到该操作会逆转 add(x) 操
作。具体来说，如果我们用相同的优先级 u.p 重新插入 x，那么 add(x) 操
作将执行完全相同数量的旋转，并将 Treap 恢复到 remove(x) 操作发生之
前的状态。（从下到上读取，图 7.8 展示了将数值 9 添加到 Treap 中的过
程。）这意味着，在大小为 n 的 Treap 上，remove(x) 的期望运行时间与在
大小为 n 1 的 Treap 上 add(x) 操作的期望运行时间成正比。我们得出结论
−
，remove(x) 的期望运行时间为 O(log n)。

（中文关键词：树堆；英文术语：BST）

## 7.2.1 总结

以下定理总结了 Treap 数据结构的性能：
定理 7.2. A Treap implements the SSet interface. A Treap supports
the operations 添加(x), 移除(x), and 查找(x) in O(log n) expected time per
3,1
1,6 5,11
0,9 2,99 4,14 9,17
7,22
6,42 8,49
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 9,17
8,49
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 8,49
9,17
3,1
1,6 5,11
0,9 2,99 4,14 7,22
6,42 8,49
图 7.8：从图 7.5 的 Treap 中移除值 9。
operation.
值得将 Treap 数据结构与 SkiplistSSet 数据结构进行比较。两者都以每
次操作 O(log n) 的期望时间实现 SSet 操作。在这两种数据结构中，add(x)
和 remove(x) 都涉及一次搜索，然后进行恒定次数的指针修改（见下面的
练习 7.5）。因此，对于这两种结构，搜索路径的期望长度是评估其性能
的关键值。在 SkiplistS-Set 中，搜索路径的期望长度是
2 log n + O(1) ,
在 Treap 中，搜索路径的期望长度是
2 ln n + O(1) 1.386 log n + O(1) .
≈
因此，Treap 中的搜索路径明显更短，这转化为 Treap 上的操作比跳表快
得多。第 4 章的练习 4.7 展示了如何将跳表中搜索路径的期望长度减少到
e ln n + O(1) 1.884 log n + O(1)
≈
通过使用有偏的掷硬币。即使有了这种优化，在 SkiplistSSet 中搜索路径
的预期长度仍明显长于在 Treap 中的预期长度。

（中文关键词：树堆、跳表；英文术语：BST）
