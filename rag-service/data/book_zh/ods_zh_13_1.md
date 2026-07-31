---
structure: 
source: book_zh/ods_zh_13_1.md
chapter: 13.1 二进制字典树：一种数字搜索树
section: 13.1
page: 280
kind: textbook
---

# 13.1 二进制字典树：一种数字搜索树

## 二进制字典树：一种数字搜索树 (1/2)

BinaryTrie 在二叉树中编码一组 w 位整数。树中的所有叶子节点深度为 w
，每个整数都编码为从根到叶子的路径。如果整数 x 的第 i 个最高有效位
是 0，则路径在第 i 层向左转；如果是 1，则向右转。图 13.1 显示了 w = 4
的示例，其中 trie 存储整数 3(0011)、9(1001)、12(1100) 和 13(1101)。
因为某个值 x 的搜索路径取决于 x 的位，因此为一个节点 u 的子节点
命名会很有帮助：u.child[0]（左）和 u.child[1]（右）。这些子指针实际上
会具有双重用途。由于二叉字典树的叶子节点没有子节点，这些指针被用
来将叶子节点串联成双向链表。在二叉字典树中叶子节点 u.child[0]（前一
个）是位于列表中 u 之前的节点，而 u.child[1]（下一个）是位于列表中 u
之后的节点。一个特殊节点 dummy 被用在列表的第一个节点之前和最后
一个节点之后（见第 3.2 节）。
每个不 de, u，还包含一个额外的指针 u.jump。如果 u 的左边
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
图 13.2：一个带有跳转指针的二叉字典树，跳转指针显示为弯曲的虚线边。
如果子节点缺失，则 u.jump 指向 u 子树中最小的叶子。如果 u 的右子节
点缺失，则 u.jump 指向 u 子树中最大的叶子。二叉字典树的一个示例，
展示了跳转指针和叶子处的双向链表，如图 13.2 所示。
在 BinaryTrie 中，find(x) 操作相当直接。我们尝试沿着 trie 中 x 的搜索
路径进行查找。如果我们到达一个叶子节点，那么就找到了 x。如果我们
到达一个节点 u，无法继续向下（因为 u 缺少一个子节点），那么我们就
沿着 u.jump 跳转，这会将我们带到比 x 大的最小叶子节点或者比 x 小的
最大叶子节点。这两种情况哪一种发生取决于 u 分别缺少左子节点还是右
子节点。在前一种情况（u 缺少左子节点）中，我们找到了想要的节点。
在后一种情况（u 缺少右子节点）中，我们可以使用链表到达想要的节点
。这些情况在图 13.3 中都有说明。
BinaryTrie
T find(T x) {
int i, c = 0, ix = it.intValue(x);
Node u = r;
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) break;
u = u.child[c];
}
? ? ? ?
0? ? ? 1? ? ?
find(5) find(8)
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
图 13.3：find(5) 和 find(8) 所遵循的路径。
如果 (i == w) 返回 u.x; // 找到了 u = (c == 0) ? u.jum
p : u.jump.child[next]; 返回 u == dummy ? null : u.x;
}
find(x) 方法的运行时间主要取决于沿根到叶路径的时间，因此其运行
时间为 O(w)。
BinaryTrie 中的 add(x) 操作也相当简单，但有很多工作要做：
1. 它沿着 x 的搜索路径前进，直到到达一个无法继续的节点 u。
2. 它从 u 创建通向包含 x 的叶子的剩余搜索路径。
3. 它将包含 x 的节点 u 添加到叶子链表中（它可以通过在第 1 步中遇
(cid:48)
到的最后一个节点 u 的跳转指针访问 u 在链表中的前驱 pred）。
(cid:48)
4. 它沿着搜索路径向上回溯，对那些其跳转指针现在应指向 x 的节点调
整跳转指针。
图 13.4 展示了一个加法运算。
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
图13.4：将数值2和15添加到图13.2中的二叉Trie中。

（中文关键词：字典树）

## 二进制字典树：一种数字搜索树 (2/2)

BinaryTrie 布尔 add(T x) { int i, c = 0, ix
= it.intValue(x); Node u = r; // 1 - 搜索 ix，直到从 trie 中掉出 for (i = 0; i
< w; i++) { c = (ix >>> w-i-1) & 1; if (u.child[c] == null) break; u = u.chil
d[c]; }if (i == w) return false; // 已经包含 x - 中止 Node pred = (c == righ
t) ? u.jump : u.jump.child[0]; u.jump = null; // u 很快将有两个子节点 // 2
- 添加到 ix 的路径 for (; i < w; i++) { c = (ix >>> w-i-1) & 1; u.child[c]
= newNode(); u.child[c].parent = u; u = u.child[c]; }u.x = x; // 3 - 将 u 添
加到链表 u.child[prev] = pred; u.child[next] = pred.child[next];
u.child[prev].child[next] = u; u.child[next].child[prev] = u; // 4 - 回溯，同
时更新跳跃指针 Node v = u.parent; while (v != null) { if ((v.child[left] == nu
ll && (v.jump == null || it.intValue(v.jump.x) > ix)) || ( v.child[right] == n
ull && (v.jump == null || it.intValue(v.jump.x) < ix))) v.jump = u; v = v.par
ent; } n++; return true; }
此方法对 x 执行一次沿搜索路径的下行遍历和一次返回上行遍历。这
些遍历的每一步都需要常数时间，因此 add(x) 方法的运行时间为 O(w)。
remove(x) 操作会撤销 add(x) 的工作。像 add(x) 一样，它有很多工作要
做：
1. 它沿着 x 的搜索路径直到到达包含 x 的叶子节点 u。
2. 它将 u 从双向链表中移除。
3. 它先删除 u，然后沿着 x 的搜索路径向上回溯删除节点，直到到达一
个节点 v，该节点有一个子节点不在 x 的搜索路径上。4. 它从 v 向上走
到根节点，更新任何指向 u 的跳转指针。
图 13.5 展示了一个移除的例子。
BinaryTrie
boolean remove(T x) {
// 1 - find leaf, u, containing x
int i = 0, c, ix = it.intValue(x);
Node u = r;
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
图 13.5：从图 13.2 的二叉字典树中移除值 9。
for (i = 0; i < w; i++) { c = (ix >>> w-i-1) & 1; if (u.ch
ild[c] == null) return false; u = u.child[c]; }// 2 - 从链
表中移除 u u.child[prev].child[next] = u.child[next]; u.
child[next].child[prev] = u.child[prev]; Node v = u; // 3
- 删除通向 u 的路径上的节点 for (i = w-1; i >= 0; i--)
{ c = (ix >>> w-i-1) & 1; v = v.parent; v.child[c] = nul
l; if (v.child[1-c] != null) break; }// 4 - 更新跳跃指针 v
.jump = u; for (; i >= 0; i--) { c = (ix >>> w-i-1) & 1; i
f (v.jump == u) v.jump = u.child[1-c]; v = v.parent; }n-
-;
return true;
}
定理 13.1. A 二叉字典树 implements the S 集合 interface for w-bit inte-
gers. A 二叉字典树 supports the operations 添加(x), 删除(x), and 查找(x)
in O(w) time per operation. The space used by a 二叉字典树 that stores n
values is O(n · w).

（中文关键词：字典树）
