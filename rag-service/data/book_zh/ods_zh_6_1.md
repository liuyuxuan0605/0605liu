---
structure: BST
source: book_zh/ods_zh_6_1.md
chapter: 6. Binary Trees
section: 6.1
page: 149
kind: textbook
---

# 6.1 二叉树：基础二叉树

表示二叉树中节点 u 的最简单方法是明确存储 u 的（最多三个）邻居：
BinaryTree
class BTNode<Node extends BTNode<Node>> {
Node left;
Node right;
Node parent;
}
当这三邻居中的一个不存在时，我们将其设置为 nil。通过这种方式，
树的外部节点和根节点的父节点都对应于值 nil。
二叉树本身可以通过对其根节点 r 的引用来表示：
二叉树
节点 r;
我们可以通过计算从节点 u 到根节点路径上的步数来计算二叉树中节
点 u 的深度：
BinaryTree
int depth(Node u) {
int d = 0;
while (u != r) {
u = u.parent;
d++;
}
return d;
}

（中文关键词：树；英文术语：BST）

## 6.1.1 递归算法

使用递归算法可以非常容易地计算二叉树的各种性质。例如，要计算以节
点 u 为根的二叉树的大小（节点数），我们递归地计算以 u 的子节点为根
的两个子树的大小，将这些大小相加，然后再加一：
BinaryTree
int size(Node u) {
if (u == nil) return 0;
return 1 + size(u.left) + size(u.right);
}
要计算节点 u 的高度，我们可以计算 u 的两个子树的高度，取最大值
，然后加一：
BinaryTree int height(Node u) { i
f (u == nil) return -1; return 1 + max(height(u.left), height(u.right)
); }

（中文关键词：树；英文术语：BST）

## 6.1.2 遍历二叉树

前一节的两个算法都使用递归来访问二叉树中的所有节点。它们每一个访
问二叉树节点的顺序都与以下代码相同：
BinaryTree
void traverse(Node u) {
if (u == nil) return;
traverse(u.left);
traverse(u.right);
}
使用递归这种方式可以产生非常短且简单的代码，但它也可能带来问
题。递归的最大深度由二叉树中节点的最大深度决定，即树的高度。如果
树的高度非常大，那么这种递归很可能会使用比可用更多的堆栈空间，从
而导致崩溃。
要在不使用递归的情况下遍历二叉树，可以使用一种算法，该算法依
赖于当前节点的来源来确定下一步该去哪里。见图6.3。如果我们从 u.pare
nt 到达节点 u，那么下一步要做的是访问 u.left。如果我们从 u.left 到达 u
，那么下一步要做的是访问 u.right。如果我们从 u.right 到达 u，那么我们
已经完成了对 u 的子树的访问，因此返回到 u.parent。以下代码实现了这
个思想，其中包括处理 u.left、u.right 或 u.parent 为 nil 的情况的代码：
二叉树 void 遍历2() { 节点
u = r, 前一个 = nil, 下一个; 当 (u != nil) { 如果 (前一个 ==
u.parent) { 如果 (u.left != nil) 下一个 = u.left; 否则如果 (u.
right != nil) 下一个 = u.right; 否则 下一个 = u.parent; } 否
则如果 (前一个 == u.left) { 如果 (u.right != nil) 下一个 = u
.right; 否则 下一个 = u.parent; } 否则 { 下一个 = u.parent;
} 前一个 = u; u = 下一个; } }
同样的事实可以用递归算法计算，也可以用这种方式计算，而不使用
递归。例如，要计算树的大小，我们保持一个计数器 n，每次第一次访问
一个节点时就增加 n：
r
u.parent
u
u.left u.right
图 6.3：在非递归遍历二叉树时，节点 u 处发生的三种情况，以及由此得到的树的
遍历结果。
BinaryTree
int size2() {
Node u = r, prev = nil, next;
int n = 0;
while (u != nil) {
if (prev == u.parent) {
n++;
if (u.left != nil) next = u.left;
else if (u.right != nil) next = u.right;
else next = u.parent;
} else if (prev == u.left) {
if (u.right != nil) next = u.right;
else next = u.parent;
} else {
next = u.parent;
}
prev = u;
u = next;
}
return n;
}
在某些二叉树的实现中，父节点字段未被使用。当出现这种情况时，
仍然可以实现非递归的方法，但实现必须使用列表（或栈）来记录从当前
节点到根节点的路径。
r
图 6.4：在广度优先遍历过程中，二叉树的节点按层逐级访问，并在每一层从左到
右访问。
一种不符合上述函数模式的特殊遍历是breadth-first traversal。在广度
优先遍历中，节点从根开始逐层访问，从上到下，按从左到右的顺序访问
每一层的节点（见图6.4）。这类似于我们阅读一页英文文本的方式。广度
优先遍历是使用队列q来实现的，该队列最初只包含根节点r。在每一步，
我们从q中提取下一个节点u，处理u，并将u.左子节点和u.右子节点（如果
它们非空）加入到q中：
BinaryTree
void bfTraverse() {
Queue<Node> q = new LinkedList<Node>();
if (r != nil) q.add(r);
while (!q.isEmpty()) {
Node u = q.remove();
if (u.left != nil) q.add(u.left);
if (u.right != nil) q.add(u.right);
}
}
7
3 11
1 5 9 13
4 6 8 12 14
图 6.5：一棵二叉搜索树。

（中文关键词：树、广度优先搜索、遍历、队列；英文术语：BST）
