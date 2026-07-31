---
structure: BST
source: book_zh/ods_zh_6_2.md
chapter: 6. Binary Trees
section: 6.2
page: 154
kind: textbook
---

# 6.2 二叉搜索树：一个不平衡的二叉搜索树

二叉搜索树是一种特殊的二叉树，其中每个节点 u 还存储一个数据值 u.x
，来自某个全序集合。二叉搜索树中的数据值遵循
binary search tree property：对于一个节点 u，存储在以 u.left 为根的子树
中的每个数据值都小于 u.x，而存储在以 u.right 为根的子树中的每个数据
值都大于 u.x。二叉搜索树的一个示例如图 6.5 所示。

（中文关键词：二叉搜索树、树；英文术语：BST）

## 6.2.1 搜索

二叉搜索树的特性非常有用，因为它允许我们在二叉搜索树中快速定位一
个值 x。为此，我们从根节点 r 开始搜索 x。在检查一个节点 u 时，有三
种情况：
1. 如果 x < u.x，那么搜索继续到 u.左； 2. 如果 x
> u.x，那么搜索继续到 u.右；
3. 如果 x = u.x，那么我们就找到了包含 x 的节点 u。
当发生情况 3 或者 u = 为 nil 时，搜索终止。在前一种情况下，我们找到
了 x。在后一种情况下，我们得出结论 x 不在二叉中
搜索树。
BinarySearchTree
T findEQ(T x) {
Node u = r;
while (u != nil) {
int comp = compare(x, u.x);
if (comp < 0)
u = u.left;
else if (comp > 0)
u = u.right;
else
return u.x;
}
return null;
}
二叉搜索树中搜索的两个例子如图6.6所示。正如第二个例子所示，即
使我们在树中没有找到x，我们仍然获得了一些有价值的信息。如果我们
看最后一个发生情况1的节点u，我们会发现u.x是树中大于x的最小值。类
似地，最后一个发生情况2的节点包含树中小于x的最大值。因此，通过跟
踪最后一个发生情况1的节点z，二叉搜索树可以实现find(x)操作，该操作
返回树中存储的最小值，该值大于或等于x。
BinarySearchTree
T find(T x) {
Node w = r, z = nil;
while (w != nil) {
int comp = compare(x, w.x);
if (comp < 0) {
z = w;
w = w.left;
} else if (comp > 0) {
w = w.right;
} else {
return w.x;
}
7 7
3 11 3 11
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 12 14
(a) (b)
图 6.6：（a）在二叉搜索树中成功搜索（寻找 6）的示例；（b）在二叉搜索树中
未成功搜索（寻找 10）的示例。
}return z == nil ? null : z.x; }

（中文关键词：树；英文术语：BST）

## 6.2.2 加法

要向二叉搜索树中添加一个新的值 x，我们首先搜索 x。如果找到它，则
无需插入。否则，我们将 x 存储在搜索 x 时遇到的最后一个节点 p 的叶子
子节点上。新的节点是 p 的左子节点还是右子节点取决于比较 x 和 p 的值
的结果。
BinarySearchTree
boolean add(T x) {
Node p = findLast(x);
return addChild(p, newNode(x));
}
BinarySearchTree
Node findLast(T x) {
Node w = r, prev = nil;
while (w != nil) {
prev = w; int comp = compare(x, w.
x); if (comp < 0) { w = w.left; } else if (c
omp > 0) { w = w.right; } else { return w
; } }return prev; }
BinarySearchTree
boolean addChild(Node p, Node u) {
if (p == nil) {
r = u; // inserting into empty tree
} else {
int comp = compare(u.x, p.x);
if (comp < 0) {
p.left = u;
} else if (comp > 0) {
p.right = u;
} else {
return false; // u.x is already in the tree
}
u.parent = p;
}
n++;
return true;
}
如图6.7所示。该过程中最耗时的部分是对x的初始搜索，其所需时间与
新添加节点u的高度成正比。在最坏的情况下，这等于二叉搜索树的高度
。
7 7
3 11 3 11
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 12 14
8.5
图6.7：将数值 8.5 插入二叉搜索树。

（中文关键词：树；英文术语：BST）

## 6.2.3 移除

删除存储在二叉搜索树节点 u 中的值要困难一些。如果 u 是叶子节点，那
么我们可以直接将 u 从它的父节点中分离。更好的是：如果 u 只有一个子
节点，那么我们可以将 u 从树中拼接出去，让 u 的父节点收养 u 的子节点
（见图 6.8）：
二叉搜索树 void spl
ice(Node u) { Node s, p; if (u.left != nil) { s = u.le
ft; } else { s = u.right; } if (u == r) { r = s; p = nil;
} else { p = u.parent; if (p.left == u) { p.left = s; }
else { p.right = s; } } if (s != nil) {
7
3 11
1 5 9 13
4 6 8 12 14
图6.8：删除一个叶子节点（6）或只有一个子节点的节点（9）很容易。
s.parent = p;
}
n--;
}
然而，当 u 有两个子节点时，情况就变得复杂了。在这种情况下，最
简单的做法是找到一个节点 w，它的子节点少于两个，并且使 w.x 可以替
换 u.x。为了保持二叉搜索树的性质，w.x 的值应接近 u.x 的值。例如，选
择 w，使得 w.x 是大于 u.x 的最小值，这样就可以。找到节点 w 很容易；
它是以 u.right 为根的子树中的最小值。这个节点可以很容易地移除，因为
它没有左子节点（见图 6.9）。
BinarySearchTree
void remove(Node u) {
if (u.left == nil || u.right == nil) {
splice(u);
} else {
Node w = u.right;
while (w.left != nil)
w = w.left;
u.x = w.x;
splice(w);
}
}
7 7
3 11 3 12
1 5 9 13 1 5 9 13
4 6 8 12 14 4 6 8 14
图 6.9：从有两个子节点的节点 u 中删除一个值 (11) 是通过将 u 的值替换为 u 右子
树中的最小值来完成的。

（中文关键词：树；英文术语：BST）

## 6.2.4 总结

在二叉搜索树中，find(x)、add(x) 和 remove(x) 操作都涉及从树的根节点
沿路径访问某个节点。如果不了解树的具体结构，很难对这条路径的长度
作出准确判断，只能说它小于 n，即树中的节点数。以下（不太令人印象
深刻的）定理总结了二叉搜索树数据结构的性能：
定理 6.1. 二叉搜索树 implements the SSet interface and sup-
ports the operations 添加(x), 删除(x), and 查找(x) in O(n) time per opera-
tion.
定理6.1与定理4.1相比表现不佳，后者表明SkiplistSSet结构可以以每次
操作预期时间O(log n)实现SSet接口。BinarySearchTree结构的问题在于它
可能变得unbalanced。它可能不是像图6.5中的树那样，而是看起来像一个
由n个节点组成的长链，除最后一个节点外，每个节点恰好只有一个子节
点。
有多种方法可以避免不平衡的二叉搜索树，这些方法都会导致具有O(l
og n)时间操作的数据结构。在第7章中，我们展示了如何通过随机化实现
O(log n) expected时间操作。在第8章中，我们展示了如何通过部分重建操
作实现O(log n)amortized时间操作。在第9章中，我们展示了如何通过模拟
一种非二叉树来实现O(log n) worst-case时间操作：其中节点最多可以有四
个子节点。

（中文关键词：摊还分析、跳表、树；英文术语：BST）
