---
structure: RedBlackTree
source: book_zh/ods_zh_9_2.md
chapter: 9.1 2-4 树
section: 9.2
page: 204
kind: textbook
---

# 9.2 红黑树：一个模拟的 2-4 树

红黑树是一种二叉搜索树，其中每个节点 u 都有一个 colour，该值要么是
red，要么是 black。红色表示值为 0，黑色表示值为 1。
RedBlackTree
class Node<T> extends BSTNode<Node<T>,T> {
byte colour;
}
在对红黑树进行任何操作之前和之后，以下两个性质都是满足的。每
个性质既以红色和黑色来定义，也以数值 0 和 1 来定义。
属性 9.3（黑色高度）。每条从根到叶子的路径上黑色节点的数量相同。
（任何从根到叶子的路径上颜色的总和都是相同的。）
属性 9.4（无红边）。没有两个红色节点相邻。（对于任意节点 u，除了根
节点，u 的颜色与 u 的父节点的颜色不都是 1。）
注意，我们总是可以将红黑树的根 r 染成黑色而不违反这两个属性，
因此我们将假设根是黑色的，而更新红黑树的算法也将维持这一点。另一
个简化红黑树的技巧是将外部节点（由 nil 表示）视为黑色节点。这样，
红黑树的每个真实节点 u 都恰好有两个子节点，并且每个子节点都有明确
的颜色。红黑树的一个例子如图 9.4 所示。

（中文关键词：树；英文术语：RedBlackTree）

## 9.2.1 红黑树与2-4树

起初，红黑树能够有效地更新以维护黑高和无红边属性可能看起来令人惊
讶，而且甚至考虑这些作为有用属性似乎也不寻常。然而，
black node
red node
图 9.4：一个黑高为 3 的红黑树示例。外部（nil）节点绘制为方形。
红黑树被设计成作为二叉树对2-4树进行高效模拟。
参考图9.5。考虑任意红黑树 T，它有 n 个节点，并执行以下变换：移
除每个红色节点 u，并将 u 的两个子节点直接连接到 u 的（黑色）父节点
。经过此变换后，我们得到一个只包含黑色节点的树 T 。
(cid:48)
T 中的每个内部节点都有两个、三个或四个子节点：一个最初有两个
(cid:48)
黑色子节点的黑色节点在此变换后仍然有两个黑色子节点。一个最初有一
个红色和一个黑色子节点的黑色节点在此变换后将有三个子节点。一个最
初有两个红色子节点的黑色节点在此变换后将有四个子节点。此外，黑色
高度属性现在保证 T 中从根到叶子的每条路径的长度相同。换句话说，
(cid:48)
T 是一棵 2-4 树！
(cid:48)
2-4 树 T 有 n + 1 个叶子节点，这些叶子节点对应红黑树的 n + 1 个外
(cid:48)
部节点。因此，这棵树的高度最多为 log(n + 1)。现在，2-4 树中从根到叶
子的每一条路径都对应红黑树中从根节点 T 到外部节点的一条路径。该路
径的第一个和最后一个节点是黑色的，并且每两个内部节点中最多有一个
是红色的，因此该路径最多有 log(n + 1) 个黑色节点，以及最多 log(n + 1)
1 个红色节点。因此，从根节点到 T 中任意 internal 节点的最长路径最
−
多为
2 log(n + 1) 2 2 log n ,
− ≤
对于任何 n 1. 这证明了红蓝最重要的特性 确认树：
≥
图 9.5：每个红黑树都有一个对应的 2-4 树。
Lemma 9.2. The height of red-black tree with n nodes is at most 2 log n.
既然我们已经看到了 2-4 树与红黑树之间的关系，那么相信在添加和
移除元素的同时，我们能够高效地维护红黑树也就不难理解了。
我们已经看到，在二叉搜索树中添加一个元素可以通过添加一个新的
叶子节点来完成。因此，要在红黑树中实现 add(x)，我们需要一种模拟在
2-4 树中分裂一个具有五个子节点的节点的方法。一个具有五个子节点的
2-4 树节点可以表示为一个黑色节点，该节点有两个红色子节点，其中一
个子节点还有一个红色子节点。我们可以通过将该节点着色为红色，并将
它的两个子节点着色为黑色来“分裂”这个节点。图 9.6 显示了这个例子
。
同样，实现 remove(x) 需要一种合并两个节点并从兄弟节点借用子节点
的方法。合并两个节点是拆分的逆过程（如图 9.6 所示），涉及将两个（
黑色）兄弟染成红色，并将它们的（红色）父节点染成黑色。从兄弟节点
借用是这些操作中最复杂的，涉及旋转和重新着色节点。
当然 当然，在这一切过程中我们仍然必须保持不重做 d-edge
w
w
u
w w
0
u
图 9.6：在红黑树中进行添加时模拟 2-4 树的分裂操作。（这模拟了图 9.2 中显示
的 2-4 树添加。）
属性和黑色高度属性。虽然现在不再令人惊讶可以做到这一点，但如果我
们尝试通过红黑树直接模拟2-4树时，需要考虑的情况仍然很多。在某些
时候，干脆忽略底层的2-4树，直接努力维护红黑树的属性会更简单。

（中文关键词：红黑树、树；英文术语：RedBlackTree）

## 9.2.2 左倾红黑树

红黑树没有单一的定义。相反，有一系列结构在执行 add(x) 和 remove(x)
操作时能够维持黑高（black-height）和无红边（no-red-edge）的属性。不
同的结构以不同的方式实现这一点。在这里，我们实现了一种称为 RedBla
ckTree 的数据结构。该结构实现了一种特定的红黑树变体，并满足一个附
加属性：
属性 9.5（左倾）。在任何节点 u，如果 u.left 是黑色的，那么 u.right 也是
黑色的。
请注意，图9.4所示的红黑树不满足左倾属性；它被最右路径上红色节
点的父节点违反了。
保持左倾属性的原因是，它在执行 add(x) 和 remove(x) 操作更新树时
减少了遇到的情况数量。就 2-4 树而言，这意味着每棵 2-4 树都有唯一的
表示：度为二的节点变成一个具有两个黑色子节点的黑色节点；度为三的
节点变成一个黑色节点，其左子节点为红色，右子节点为黑色；度为四的
节点变成一个具有两个红色子节点的黑色节点。
在详细描述 add(x) 和 remove(x) 的实现之前，我们首先介绍一些这些
方法使用的简单子程序，这些子程序在图 9.7 中有所说明。前两个子程序
用于操作颜色，同时保持黑色高度属性。pushBlack(u) 方法的输入是一个
有两个红色子节点的黑色节点 u，它会将 u 染成红色，并将它的两个子节
点染成黑色。pullBlack(u) 方法则是该操作的逆过程：
u u u u
pushBlack(u) pullBlack(u) flipLeft(u) flipRight(u)
⇓ ⇓ ⇓ ⇓
u u
u u
图 9.7：翻转、拉动和推送
RedBlackTree
void pushBlack(Node<T> u) {
u.colour--;
u.left.colour++;
u.right.colour++;
}
void pullBlack(Node<T> u) {
u.colour++;
u.left.colour--;
u.right.colour--;
}
flipLeft(u) 方法交换 u 和 u.right 的颜色，然后在 u 上执行左旋转。该方
法会反转这两个节点的颜色以及它们的父子关系：
RedBlackTree
void flipLeft(Node<T> u) {
swapColors(u, u.right);
rotateLeft(u);
}
flipLeft(u) 操作在恢复违反该性质的节点 u 的左倾属性时尤其有用（因
为 u. 左子节点是黑色而 u. 右子节点是红色）。在这种特殊情况下，我们
可以确信该操作能够保持黑高和无红边属性。
当左右的角色互换时，flipRight(u) 操作与 flipLeft(u) 对称。
RedBlackTree
void flipRight(Node<T> u) {
swapColors(u, u.left);
rotateRight(u);
}

（中文关键词：树；英文术语：RedBlackTree）

## 9.2.3 加法

要在红黑树中实现 add(x)，我们执行标准的二叉搜索树插入操作来添加一
个新的叶子节点 u，其中 u 的值为 x，并将 u 的颜色设置为红色。注意，
这不会改变任何节点的黑高度，因此不会违反黑高属性。然而，它可能会
违反左倾属性（如果 u 是其父节点的右子节点），也可能违反无红边属性
（如果 u 的父节点是红色）。为了恢复这些属性，我们调用方法 addFixup
(u)。
RedBlackTree
boolean add(T x) {
Node<T> u = newNode(x);
u.colour = red;
boolean added = add(u);
if (added)
addFixup(u);
return added;
}
如图9.8所示，addFixup(u) 方法的输入是一个节点 u，该节点的颜色为
红色，并且可能违反了无红边属性和/或左倾属性。没有参考图9.8或在纸
上重新绘制它，以下讨论可能几乎无法理解。事实上，读者可能希望在继
续之前先学习这个图。
如果 u 是树的根，那么我们可以把 u 染成黑色以恢复这两个属性。如
果 u 的兄弟也是红色，那么 u 的父节点必须是黑色，因此左倾和无红边属
性已经成立。
u
u.parent.left.colour
w w w
u u u
return flipLeft(w) ; u = w
w
u
w.colour
w w
u u
g.right.colour return
g g g
w w w
u u u
flipRight(g) pushBlack(g) pushBlack(g)
w new u = g new u = g
u g w w
u u
return
图 9.8：插入后修复属性 2 过程中的一次循环。
否则，我们首先确定 u 的父节点 w 是否违反了左倾属性，如果是，则
执行 flipLeft(w) 操作并将 u = w。这使我们处于一个定义良好的状态：u
是其父节点 w 的左子节点，因此 w 现在满足左倾属性。剩下的就是确保 u
的无红边属性。我们只需要担心 w 是红色的情况，因为否则 u 已经满足无
红边属性。
由于我们还没有完成，u 是红色，w 也是红色。无红边属性（仅被 u 违
反，而 w 没有违反）意味着 u 的祖父 g 存在且为黑色。如果 g 的右子是红
色，那么左倾属性确保 g 的两个子都是红色，并且调用 pushBlack(g) 会使
g 变为红色，w 变为黑色。这在 u 处恢复了无红边属性，但可能导致 g 处
被违反，因此整个过程从 u = g 重新开始。
如果 g 的右子节点是黑色的，那么调用 flipRight(g) 会使 w 成为 g 的（
黑色）父节点，并且给 w 两个红色子节点 u 和 g。这确保了 u 满足无红边
属性，并且 g 满足左倾属性。在这种情况下，我们可以停止。
红黑树 void addFixup(Node<T> u) { 当 (
u.colour == 红) { 如果 (u == r) { // u 是根节点 - 完成 u.colour = 黑色;
返回; }Node<T> w = u.parent; 如果 (w.left.colour == 黑色) { // 确保左
倾 flipLeft(w); u = w; w = u.parent; }如果 (w.colour == 黑色) return; //
没有红-红边 = 完成 Node<T> g = w.parent; // u 的祖父 如果 (g.right.col
our == 黑色) { flipRight(g); return; } else { pushBlack(g);
u = g;
}
}
}
insertFixup(u) 方法每次迭代花费恒定时间，并且每次迭代要么完成，
要么将 u 移向根。因此，insertFixup(u) 方法在 O(log n) 次迭代后完成，总
共花费 O(log n) 时间。

（中文关键词：树；英文术语：RedBlackTree）

## 9.2.4 移除 (1/2)

在红黑树中，remove(x) 操作是最复杂的实现，对于所有已知的红黑树变
种也是如此。就像二叉搜索树中的 remove(x) 操作一样，这个操作归结为
找到一个只有一个子节点 u 的节点 w，然后通过让 w 的父节点收养 u，将
w 从树中删除。
这个问题在于，如果 w 是黑色的，那么现在黑色高度属性将在 w 的父
节点处被违反。我们可以通过将 w 的颜色加到 u 的颜色上，暂时避免这个
问题。当然，这会引入另外两个问题：（1）如果 u 和 w 最初都是黑色的
，那么 u 的颜色加 w 的颜色等于 2（双黑），这是一个无效的颜色。如果
w 是红色的，那么它会被一个黑色节点 u 替换，这可能会在 u 的父节点处
违反左倾属性。这两个问题都可以通过调用 removeFixup(u) 方法来解决。
RedBlackTree
boolean remove(T x) {
Node<T> u = findLast(x);
if (u == nil || compare(u.x, x) != 0)
return false;
Node<T> w = u.right;
if (w == nil) {
w = u;
u = w.left;
} else {
while (w.left != nil)
w = w.left;
u.x = w.x; u = w.right; }s
plice(w); u.colour += w.colour
; u.parent = w.parent; remove
Fixup(u); 返回 true; }
removeFixup(u) 方法以一个节点 u 作为输入，该节点的颜色为黑色 (1)
或双黑色 (2)。如果 u 是双黑色，那么 removeFixup(u) 会执行一系列旋转
和重新着色操作，将双黑节点沿树向上移动，直到它可以被消除。在此过
程中，节点 u 会发生变化，直到该过程结束时，u 指向已更改的子树的根
。该子树的根节点的颜色可能已发生变化。特别是，它可能从红色变为黑
色，因此 removeFixup(u) 方法的最后会检查 u 的父节点是否违反了左倾属
性，如果违反，则进行修复。
RedBlackTree void removeFixup(Node<T> u
) { while (u.colour > 黑色) { if (u == r) { u.colour = 黑色; } else if (u.parent.
left.colour == 红色) { u = removeFixupCase1(u); } else if (u == u.parent.left
) { u = removeFixupCase2(u); } else { u = removeFixupCase3(u); } }if (u !=
r) { // 如有需要，恢复左倾属性 Node<T> w = u.parent; if (w.right.colour
== 红色 && w.left.colour == 黑色) { flipLeft(w); } }
}
removeFixup(u) 方法在图 9.9 中进行了说明。同样，如果不参考图 9.9
，以下文本将很难理解，甚至几乎不可能理解。removeFixup(u) 中循环的
每次迭代都根据四种情况之一处理双黑节点 u：
情况 0：u 是根节点。这是最容易处理的情况。我们将 u 重新着色为黑色
（这不会违反红黑树的任何性质）。
案例 1：u 的兄弟 v 是红色的。在这种情况下，u 的兄弟是其父节点 w 的
左孩子（根据左倾属性）。我们在 w 处执行右旋，然后继续下一次迭代。
注意，这个操作会导致 w 的父节点违反左倾属性，并且 u 的深度增加。然
而，这也意味着下一次迭代将是 Case 3，并且 w 是红色的。在下面查看 C
ase 3 时，我们将看到该过程将在下一次迭代中停止。
RedBlackTree
Node<T> removeFixupCase1(Node<T> u) {
flipRight(u.parent);
return u;
}
案例2：u的兄弟v是黑色的，并且u是其父节点w的左孩子。在这种情况下
，我们调用pullBlack(w)，将u变为黑色，v变为红色，并将w的颜色加深为
黑色或双黑色。此时，w不满足左倾特性，因此我们调用flipLeft(w)来修复
它。
此时，w 是红色的，而 v 是我们开始的子树的根。我们需要检查 w 是
否会导致无红边属性被违反。我们通过检查 w 的右子节点 q 来完成此操作
。如果 q 是黑色的，那么 w 满足无红边属性，我们可以使用 u = v 继续下
一次迭代。

（中文关键词：树；英文术语：RedBlackTree）

## 9.2.4 移除 (2/2)

否则（q 为红色），因此无红边属性和左倾属性分别在 q 和 w 处被破
坏。通过调用 rotateLeft(w) 可以恢复左倾属性，但无红边属性仍然被破坏
。此时，q 是 v 的左子节点，w 是 q 的左子节点，q 和 w 都是红色，v 是
黑色或双黑色。一次 flipRight(v) 会使 q 成为 v 和 w 的父节点。随后通过
removeFixupCase2(u) removeFixupCase3(u) removeFixupCase1(u)
w w w
u v v u u
pullBlack(w) pullBlack(w)
flipRight(w)
w w
u v v u
flipLeft(w) flipRight(w) w
new u
v v
w w
u q
q.colour q.colour
v v (new u) v v
w w w
u q q q u q u
v.left.colour
rotateLeft(w) rotateRight(w)
v
v v w w
q q q u q u
w w flipLeft(v) pushBlack(v)
u u
flipRight(v) flipLeft(v) w (new u)
v u w
q q q u
w v v w
u u
pushBlack(q) pushBlack(q)
q q
w v v w
u u
v.right.colour
q q
w v w v
u u
flipLeft(v)
q
w
u v
图 9.9：删除后消除双黑节点过程中的一次循环。
pushBlack(q) 使 v 和 w 都变为黑色，并将 q 的颜色设置回 w 的原始颜色。
此时，双黑节点已经被消除，并且无红边和黑高属性已重新建立。只
剩下一个可能的问题：v 的右子节点可能是红色的，在这种情况下，左倾
性质将被破坏。我们检查这一点，并在必要时执行 flipLeft(v) 来纠正它。
RedBlackTree
Node<T> removeFixupCase2(Node<T> u) {
Node<T> w = u.parent;
Node<T> v = w.right;
pullBlack(w); // w.left
flipLeft(w); // w is now red
Node<T> q = w.right;
if (q.colour == red) { // q-w is red-red
rotateLeft(w);
flipRight(v);
pushBlack(q);
if (v.right.colour == red)
flipLeft(v);
return q;
} else {
return v;
}
}
情况3：u的兄弟是黑色的，并且u是其父节点w的右子节点。这个情况与情
况2是对称的，处理方式大致相同。唯一的不同之处在于左倾属性是不对
称的，因此需要不同的处理方法。
和以前一样，我们首先调用 pullBlack(w)，这会使 v 变为红色，u 变为
黑色。调用 flipRight(w) 会将 v 提升为子树的根节点。此时 w 是红色的，
代码根据 w 的左子节点 q 的颜色分为两条路径。
如果 q 是红色的，那么代码的执行最终与情况 2 完全相同，但更简单
，因为不存在 v 不满足左倾属性的风险。
更复杂的情况发生在 q 是黑色时。在这种情况下，我们检查 v 的左孩
子的颜色。如果它是红色的，那么 v 有两个红色的孩子，其额外的黑色可
以通过调用 pushBlack(v) 来向下推进。到这一点，v 现在具有 w 的原始颜
色，我们完成了。
如果 v 的左子节点是黑色的，那么 v 违反了左倾属性，我们通过调用 f
lipLeft(v) 来恢复它。然后我们返回节点 v，以便下一次 removeFixup(u) 的
迭代继续处理 u = v。
RedBlackTree 节点<T> remove
FixupCase3(节点<T> u) { 节点<T> w = u.parent; 节点<T> v =
w.left; 拉黑(w); 右旋(w); // w 现在是红色 节点<T> q = w.left
; if (q.颜色 == 红) { // q-w 是红红 右旋(w); 左旋(v); 推黑(q);
return q; } else { if (v.left.颜色 == 红) { 推黑(v); // v 的两个
子节点都是红色 return v; } else { // 确保左倾 左旋(v); return
w; } } }
removeFixup(u) 的每次迭代都需要常量时间。情况 2 和情况 3 要么结束
，要么将 u 移向树的根。情况 0（即 u 是根节点）总是会终止，而情况 1
则立即进入情况 3，情况 3 也会终止。由于树的高度最多为 2 log n，我们
可以得出结论，removeFixup(u) 最多有 O(log n) 次迭代，因此 removeFixu
p(u) 的运行时间为 O(log n)。

（中文关键词：树；英文术语：RedBlackTree）
