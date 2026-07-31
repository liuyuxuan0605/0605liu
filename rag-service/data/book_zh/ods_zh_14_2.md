---
structure: BTree
source: book_zh/ods_zh_14_2.md
chapter: 14. External Memory Searching
section: 14.2
page: 299
kind: textbook
---

# 14.2 B 树

在本节中，我们讨论了二叉树的一种推广，称为B-树，它在外部存储模型
中是高效的。或者，B-树
可以被视为第9.1节中描述的2-4树的自然推广。（2-4树是B-树的一个特例
，通过将B =设为2得到。）
对于任意整数 B ≥ 2，B-tree 是一种树，其中所有叶子具有相同的深
≥
度，并且每个非根内部节点 u 至少有 B 个子节点，最多有 2B 个子节点。u
的子节点存储在数组 u.children 中。根节点的子节点数量有一定的放宽，
可以有 2 到 2B 个子节点。
如果一棵 B 树的高度为 h，那么 B 树中的叶子数量 (cid:96) 满足
2Bh − 1 (cid:96) 2(2B)h − 1 .
≤ ≤
对第一个不等式取对数并重新排列项得到：
log (cid:96) 1
h − + 1
≤ log B
log (cid:96)
+ 1
≤ log B
= log (cid:96) + 1 .
B
也就是说，B 树的高度与叶子数量的以 B 为底的对数成正比。
在 B-树中，每个节点 u 都存储一个键数组 u.keys[0], . . . , u.keys[2B 1]
−
。如果 u 是一个有 k 个子节点的内部节点，则 u 存储的键的数量恰好为
k 1，并且这些键存储在 u.keys[0], . . . , u.keys[k 2] 中。u.keys 中其余的 2
− −
B k + 1 个数组项被设置为 null。如果 u 是一个非根叶节点，那么 u 将包
−
含 B 1 到 2B 1 个键。B-树中的键遵循类似于二叉搜索树中键的顺序。
− −
对于任何存储 k 1 个键的节点 u,
−
u.keys[0] < u.keys[1] < < u.keys[k 2] .
· · · −
如果 u 是一个内部节点，那么对于每个 i {0, . . . , k 2}，u.keys[i] 大于存
∈ −
储在以 u.children[i] 为根的子树中的每个键，但小于存储在以 u.children[i +
1] 为根的子树中的每个键。非正式地说，
u.children[i] u.keys[i] u.children[i + 1] .
≺ ≺
10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
图14.2：一个 B-树，具有 B = 2。
图14.2显示了一个B-树，B =为2的示例。
请注意，存储在 B 树节点中的数据大小为 O(B)。因此，在外部存储环
境中，B 树中的 B 值是这样选择的，以便一个节点可以适合一个外部存储
块。这样，在外部存储模型中执行 B 树操作所需的时间与操作访问（读取
或写入）的节点数量成正比。
例如，如果键是 4 字节的整数，节点索引也是 4 字节，那么设置 B = 2
56 意味着每个节点存储
(4 + 4) 2B = 8 512 = 4096
× ×
字节的数据。这将是本章介绍的硬盘或固态硬盘的完美值 B，它们的块大
小为 4096 字节。
BTree 类实现了一个 B-树，它存储了一个 BlockStore（bs），该 Block
Store 存储 BTree 节点，以及根节点的索引 ri。和往常一样，一个整数 n 被
用来跟踪数据结构中的项目数量：
B树
int n; BlockStore<Node>
bs; int ri;
10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
16.5
图14.3：在B-树中一次成功的搜索（寻找值4）和一次不成功的搜索（寻找值16.5
）。阴影节点显示在搜索过程中z的值被更新的位置。

（中文关键词：树、B树；英文术语：BTree）

## 14.2.1 搜索

图 14.3 中展示的 find(x) 操作的实现，将二叉搜索树中的 find(x) 操作进行
了推广。对 x 的搜索从根节点开始，并使用存储在节点 u 中的键来确定搜
索应继续在哪个子节点中进行。
更具体地说，在节点 u 处，搜索会检查 x 是否存储在 u 的 keys 中。如
果是这样，表示已经找到 x，搜索完成。否则，搜索会找到最小的整数 i
，使得 u 的 keys[i] 大于或等于 x，并在以 u 的 children[i] 为根的子树中继
续搜索。如果 u 的 keys 中没有任何键大于 x，则搜索会继续到 u 的最右子
节点。与二叉搜索树一样，该算法会跟踪最近看到的比 x 大的键 z。如果
未找到 x，则返回 z 作为大于或等于 x 的最小值。
BTree
T find(T x) {
T z = null;
int ui = ri;
while (ui >= 0) {
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) return u.keys[-(i+1)]; // found it
if (u.keys[i] != null)
z = u.keys[i];
ui = u.children[i];
}
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
a 1 4 5 8 9 10 14 16 22 31 45 – – – – –
27
图14.4：执行 findIt(a,27)。
返回 z;
}
find(x) 方法的核心是 findIt(a x) 方法，它在一个以 null 填充的排序数组
a 中搜索值 x。该方法如图 14.4 所示，适用于任何数组 a，其中 a[0] 到 a[a.
length - 1] 是按顺序排列的键序列，且 a[a.length - 1] 之后的所有元素都设
置为 null。如果 x 位于数组的第 i 个位置，则 findIt(a, x) 返回 i + 1。否则
，它返回最小的索引 i，使得 a[i] ≥ x 或 a[i] == null。
BTree
int findIt(T[] a, T x) {
int lo = 0, hi = a.length;
while (hi != lo) {
int m = (hi+lo)/2;
int cmp = a[m] == null ? -1 : compare(x, a[m]);
if (cmp < 0)
hi = m; // look in first half
else if (cmp > 0)
lo = m+1; // look in second half
else
return -m-1; // found it
}
return lo;
}
findIt(a, x) 方法使用二分查找，每一步都将搜索空间减半，因此它的运
行时间为 O(log(a.length))。在我们的设置中，a.length = 2B，所以 findIt(a,
x) 的运行时间为 O(log B)。
我们可以分析 B-树的 find(x) 操作的运行时间，既可以在通常的字RA
M模型中（这里每条指令都计算在内），也可以在外部存储模型中（这里
只计算访问的节点数）。由于 B-树中的每个叶子至少存储一个键，并且具
有 (cid:96) 个叶子的 B-树的高度是 O(log (cid:96))，因此存储 n 个键的 B-树的高度是
B
O(log n)。因此，在外部存储模型中，find(x) 操作所需的时间是 O(log n)
B B
。为了确定在字RAM模型中的运行时间，我们必须考虑对每个访问节点
调用 findIt(a, x) 的代价，因此在字RAM模型中 find(x) 的运行时间是
O(log n) O(log B) = O(log n) .
B ×

（中文关键词：树；英文术语：BTree）

## 14.2.2 加法 (1/2)

B-树与第6.2节的二叉搜索树数据结构之间的一个重要区别是，B-树的节点
不存储指向其父节点的指针。这个原因将在稍后解释。缺少父节点指针意
味着在B-树上实现 add(x) 和 remove(x) 操作时，最容易使用递归方式。
像所有平衡搜索树一样，在执行 add(x) 操作时需要进行某种形式的重
新平衡。在 B-树中，这是通过 splitting 节点完成的。请参见图 14.5 了解
以下内容。虽然分裂操作会在两层递归中进行，但最好将其理解为对包含
2B 个键且有 2B ++1 个子节点的节点 u 执行的操作。它会创建一个新节点
w，w 接管 u 的部分子节点［B］至 u 的子节点［2B］。新节点 w 还会接
管 u 的 B 个最大键，即 u 的键［B］至 u 的键［2B +1］。此时，u 具有
−
B 个子节点和 B 个键。额外的键 u 的键［B +1］被传递给 u 的父节点，
−
父节点同时也接纳了 w。
请注意，分裂操作会修改三个节点：u、u的父节点以及新节点w。这就
是为什么B-树的节点不维护父指针很重要的原因。如果它们维护了，那么
被w收养的B + 1个子节点都需要修改它们的父指针。这会将外部内存访问
次数从3增加到B + 4，并使B-树在B较大值时效率大大降低。
添加 在图 14.6 中展示了 B-树中的 (x) 方法。 在一个 高
b d f u
u
¢h¢¢ j m o q s
A C E V
G I K N P R T
u.split()
⇓
b d f m u
u w
h¢ j m o q s
A C E V
G I K N P R T
图14.5：在B =3的B树中拆分节点u。注意键u.keys[2]=从u传递到其父节点。
10
3 6 14 17 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 21 23 24
⇓
10
3 6 14 17 19 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 21 23 24
⇓
10 17
3 6 14 17 19 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 20 21 23 24
图 14.6：B 树中的 add(x) 操作。添加值 21 会导致两个节点被拆分。
在该级别上，该方法会找到一个叶子节点 u，在该节点添加值 x。如果这
导致 u 变得超出容量（因为它已经包含 B 1 个键），那么 u 会被分裂。
−
如果这导致 u 的父节点超出容量，那么 u 的父节点也会被分裂，这可能会
导致 u 的祖父节点超出容量，依此类推。这个过程会继续，每次向上移动
一层，直到到达一个未超出容量的节点或直到根节点被分裂。在前一种情
况下，过程会停止。在后一种情况下，会创建一个新的根节点，其两个子
节点成为原根节点分裂时得到的节点。
add(x) 方法的执行摘要是，它从根节点走向一个叶子节点搜索 x，将 x
添加到该叶子节点，然后再走回根节点，在此过程中分裂沿途遇到的任何
超额节点。考虑到这个高级概述，我们现在可以深入探讨如何递归实现此
方法的细节。
add(x) 的实际工作是由 addRecursive(x, ui) 方法完成的，该方法将值 x
添加到以 u 为根、标识符为 ui 的子树中。如果 u 是叶子节点，那么 x 就
直接插入到 u.keys 中。否则，x 会递归地添加到 u 的适当子节点 u 中。这
(cid:48)
次递归调用的结果通常是 null，但也可能是对新创建的节点 w 的引用，该
节点是因为 u 被分裂而创建的。在这种情况下，u 会接纳 w 并获取它的第
(cid:48)
一个键，从而完成对 u 的分裂操作。
(cid:48)
在将值 x 添加到 u 或 u 的一个子节点后，addRecursive(x, ui) 方法会检
查 u 是否存储了太多（超过 2B 1）个键。如果是这样，那么 u 需要通过
−
调用 u.split() 方法进行 split。调用 u.split() 的结果是一个新节点，该节点
用作 addRecursive(x, ui) 的返回值。
BTree 节点 addRecursive(T x, int ui)
{ 节点 u = bs.readBlock(ui); int i = findIt(u.keys, x); if (i < 0) throw new
DuplicateValueException(); if (u.children[i] < 0) { // 叶节点，直接添加
u.add(x, -1); bs.writeBlock(u.id, u); } else { 节点 w = addRecursive(x, u.c
hildren[i]); if (w != null) { // 子节点被分裂，w 是新子节点 x = w.remo
ve(0); bs.writeBlock(w.id, w); u.add(x, w.id); bs.writeBlock(u.id, u); } } r
eturn u.isFull() ? u.split() : null; }
addRecursive(x, ui) 方法是 add(x) 方法的一个辅助方法，它调用 addRec
ursive(x, ri) 将 x 插入到 B-树的根节点。如果 addRecursive(x, ri) 导致根节
点分裂，则会创建一个新根节点，其子节点包括旧根节点和由旧根节点分
裂产生的新节点。

（中文关键词：树；英文术语：BTree）

## 14.2.2 加法 (2/2)

BTree 布尔 add(T x) { 节点 w;
尝试 { w = addRecursive(x, ri); } 捕获 (DuplicateValueException e)
{ 返回 false; } 如果 (w != null) { // 根被分裂，创建新根节点 节点
newroot = 新节点(); x = w.remove(0); bs.writeBlock(w.id, w); newro
ot.children[0] = ri; newroot.keys[0] = x; newroot.children[1] = w.id; ri
= newroot.id; bs.writeBlock(ri, newroot); }n++; 返回 true; }
add(x) 方法及其辅助方法 addRecursive(x, ui) 可以分两个阶段进行分析
：
向下阶段：在递归的向下阶段，在 x 被添加之前，它们访问一系列 BTree
节点，并在每个节点上调用 findIt(a, x)。与 find(x) 方法一样，在外部存储
模型中，这需要 O(log n) 时间，在字 RAM 模型中需要 O(log n) 时间。
B
上升阶段：在递归的上升阶段，在 x 被添加之后，这些方法执行最多 O(lo
g n) 次分割。每次分割仅涉及三个节点，因此在外部存储模型中，这一
B
阶段花费 O(log n) 时间。然而，每次分割都涉及将 B 个键和值从一个节
B
点移动到另一个节点，所以在字-RAM 模型中，这花费 O(B log n) 时间。
请记住，B 的值可能非常大，甚至比 log n 还要大得多。因此，在 word
-RAM 模型中，将一个值添加到 B-树中可以
比向平衡二叉搜索树中添加要慢得多。在第14.2.4节中，我们将展示情况
并没有那么糟；在执行 add(x) 操作期间完成的分裂操作的均摊次数是常数
。这表明，在字RAM模型中，add(x) 操作的（均摊）运行时间是 O(B + lo
g n)。

（中文关键词：树；英文术语：BTree）

## 14.2.3 移除 (1/2)

B 树中的 remove(x) 操作，同样，最容易通过递归方法来实现。尽管 remo
ve(x) 的递归实现将复杂性分散到多个方法，但总体过程，如图 14.7 所示
，相当直接。通过调整键的位置，删除操作被简化为从某个叶子节点 u 中
移除一个值 x 的问题。移除 x 可能会导致 u 的键少于 B 1 个；这种情况
(cid:48) (cid:48)
−
称为 underflow。
当发生下溢时，u 要么从其一个兄弟节点借用键，要么与一个兄弟节点
合并。如果 u 与一个兄弟节点合并，那么 u 的父节点将少一个子节点和少
一个键，这可能导致 u 的父节点下溢；这再次通过借用或合并来纠正，但
合并可能导致 u 的祖父节点下溢。这个过程会一直向上回溯到根节点，直
到不再发生下溢，或者根节点的最后两个子节点合并为一个子节点。当出
现后一种情况时，根节点被移除，它的唯一子节点将成为新的根节点。
接下来，我们深入探讨每一个步骤是如何实现的。remove(x) 方法的第
一个任务是找到应该被移除的元素 x。如果在一个叶子节点中找到了 x，
那么就从这个叶子节点中移除 x。否则，如果在某个内部节点 u 的 u.keys[i
] 中找到了 x，那么算法会移除以 u.children[i+1] 为根的子树中的最小值 x
(cid:48)
。x 是存储在 B 树中大于 x 的最小值。然后使用 x 的值来替换 u.keys[i]
(cid:48) (cid:48)
中的 x。这个过程如图 14.8 所示。
removeRecursive(x, ui) 方法是前述算法的递归实现：
B树
boolean removeRecursive(T x, int ui) {
10
3 14 17 21
1 4 11 12 13 15 16 18 19 20 22 23
⇓
10
3 14 17 21
v w
1 4 11 12 13 15 16 18 19 20 22 23
merge(v, w)
⇓
10
w v
14 17 21
1 3 11 12 13 15 16 18 19 20 22 23
shiftLR(w, v)
⇓
14
10 17 21
1 3 11 12 13 15 16 18 19 20 22 23
图 14.7：从 B 树中移除值 4 会导致一次合并和一次借用操作。
10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
⇓
11
3 6 14 17 21
0 1 2 4 5 7 8 9 12 13 15 16 18 19 20 22 23
图14.8：B树中的 remove(x) 操作。要移除值 x = 10，我们将其替换为值 x = 11，
(cid:48)
并从包含它的叶子节点中移除 11。
if (ui < 0) return false; // 没有找到它 Node u = bs.readBlock(ui
); int i = findIt(u.keys, x); if (i < 0) { // 找到了 i = -(i+1); if (u.isL
eaf()) { u.remove(i); } else { u.keys[i] = removeSmallest(u.childre
n[i+1]); checkUnderflow(u, i+1); }return true; } else if (removeRe
cursive(x, u.children[i])) { checkUnderflow(u, i); return true; }ret
urn false; }T removeSmallest(int ui) { Node u = bs.readBlock(ui);
if (u.isLeaf())
return u.remove(0); T y = removeSmallest(u.
children[0]); checkUnderflow(u, 0); return y;
}
请注意，在从 u 的第 i 个子节点递归移除值 x 后，removeRecursive(x, u
i) 需要确保该子节点至少仍有 B 个键。在前面的代码中，这是通过一个
−
名为 checkUnderflow(x, i) 的方法来完成的，该方法检查并纠正 u 的第 i 个
子节点的下溢。设 w 为 u 的第 i 个子节点。如果 w 只有 B 个键，则需要
−
进行修复。修复需要使用 w 的一个兄弟节点。这个兄弟节点可以是 u 的第
i + 1 个子节点，也可以是 u 的第 i 1 个子节点。我们通常使用 u 的第 i
− −
1 个子节点，即直接在 w 左侧的兄弟 v。唯一不适用的情况是 i = 0，这种
情况下我们使用直接在 w 右侧的兄弟。
BTree
void checkUnderflow(Node u, int i) {
if (u.children[i] < 0) return;
if (i == 0)
checkUnderflowZero(u, i); // use u’s right sibling
else
checkUnderflowNonZero(u,i);
}
在下文中，我们重点讨论 i (cid:44) 0 的情况，以便在 u 的第 i 个子节点出现
下溢时，可以借助 u 的第 (i 1) 个子节点进行修正。i = 0 的情况类似，具
−
体细节可以在随附的源代码中找到。

（中文关键词：树；英文术语：BTree）

## 14.2.3 移除 (2/2)

要修复节点 w 的下溢，我们需要为 w 找到更多键（可能还包括子节点
）。有两种方法可以做到这一点：
借用：如果 w 有一个兄弟节点 v，并且 v 有多于 B 个键，那么 w 可以从
−
v 借一些键（也可能包括子节点）。更具体地说，如果 v 存储了 size(v) 个
键，那么它们两者 v 和 w 的总数为
B 2 + size(w) 2B 2
− ≥ −
u
b d f o s
v w
h j m q¢
A C E T
G I K N P R
shiftRL(v, w)
⇓
u
b d f m s
v w
h¢ j o¢ q
A C E T
G I K N P R
图 14.9：如果 v 有超过 B 个 1 键，则 w 可以从 v 借用键。
−
钥匙。因此，我们可以将钥匙从 v 移到 w，使得 v 和 w 每个至少都
有 B 个 1 键。这个过程如图 14.9 所示。
−
合并：如果 v 只有 B 个 1 键，我们必须采取更激烈的措施，因为 v 无法
−
向 w 提供任何键。因此，我们按图 14.10 所示合并 v 和 w。合并操作是分
裂操作的相反操作。它将包含总共 2B 3 个键的两个节点合并为一个包含
−
2B 2 个键的节点。（额外的键来自这样一个事实：当我们合并 v 和 w 时
−
，它们的共同父节点 u 现在少了一个子节点，因此需要放弃其中一个键。
）
BTree
void checkUnderflowNonZero(Node u, int i) {
Node w = bs.readBlock(u.children[i]); // w is child of u
u
b d f m q
v w
h¢ j o¢
A C E R
G I K N P
merge(v, w)
⇓
u
b d f q
h j m o
A C E R
G I K N P
图 14.10：在 B 树 (B = 3) 中合并两个兄弟节点 v 和 w。
if (w.size() < B-1) { // w节点下溢 Node v = bs.readBlock(u.children[i-1]);
// v在w的左边 if (v.size() > B) { // w可以从v借元素 shiftLR(u, i-1, v, w); }
else { // v将吸收w merge(u, i-1, v, w); } } }void checkUnderflowZero(Node
u, int i) { Node w = bs.readBlock(u.children[i]); // w是u的子节点 if (w.size()
< B-1) { // w节点下溢 Node v = bs.readBlock(u.children[i+1]); // v在w的右
边 if (v.size() > B) { // w可以从v借元素 shiftRL(u, i, v, w); } else { // w将吸
收v merge(u, i, w, v); u.children[i] = w.id; } } }
总而言之，B-树中的 remove(x) 方法沿着从根到叶子的路径进行，从叶
子 u 中删除键 x ，然后对 u 及其祖先执行零次或多次合并操作，并最多执
(cid:48)
行一次借位操作。由于每次合并和借位操作只涉及修改三个节点，并且这
些操作仅发生 O(log n) 次，因此在外部存储模型中，整个过程需要 O(log
B
n) 时间。然而，每次合并和借位操作在字长 RAM 模型中需要 O(B) 时间
B
，因此（目前）我们关于在字长 RAM 模型中 remove(x) 所需运行时间所
能说明的最多是它为 O(B log n)。
B

（中文关键词：树；英文术语：BTree）

## 14.2.4 B-树的摊销分析 (1/2)

到目前为止，我们已经展示了
1. 在外部存储模型中，B-树中 find(x)、add(x) 和 remove(x) 的运行时间
是 O(log n)。
B
2. 在字RAM模型中，find(x) 的运行时间是 O(log n)，而 add(x) 和 remov
e(x) 的运行时间是 O(B log n)。
下列引理表明，到目前为止，我们高估了 B-树执行的合并和拆分操作
的次数。
引理 14.1. Starting with an empty B-tree and performing any sequence
of m 添加(x) and 移除(x) operations results in at most 3m/2 splits, merges,
and borrows being performed.
Proof. 这一点的证明已经在第9.3节中针对特例B = 2进行了概述。引理可
以使用一种积分方案来证明，其中
1. 每次拆分、合并或借用操作都需要支付两个积分，即每当发生这些操
作之一时，将扣除一个积分；并且
2. 在任何 add(x) 或 remove(x) 操作期间，最多创建三个学分。
由于最多仅创建 3m 个学分，并且每次分割、合并和借用都需要用两个学
分支付，因此最多执行 3m/2 次分割、合并和借用。这些学分在图 14.5、1
4.9 和 14.10 中使用 符号表示。
¢
为了跟踪这些信用，证明保持了以下 credit invariant：任何非根节点
如果有 B 1 个键，则存储一个信用；任何有 2B 1 个键的节点存储三个
− −
信用。一个存储至少 B 个键且最多 2B 2 个键的节点无需存储任何信用
−
。剩下的就是要展示我们可以在每次 add(x) 和 remove(x) 操作中保持信用
不变性，并满足上述性质 1 和 2。
添加：add(x) 方法不会执行任何合并或借位操作，所以我们只需要考虑由
于调用 add(x) 而发生的拆分操作。
每次分裂操作的发生是因为一个键被添加到已经包含 2B 1 个键的节
−
点 u。当这种情况发生时，u 被分裂为两个节点，u 和 u ，分别拥有 B 1
(cid:48) (cid:48)(cid:48)
−
和 B 个键。在此操作之前，u 存储了 2B 1 个键，因此有三个积分。这些
−
积分中的两个可以
用于支付分裂费用，另一部分信用可以给予 u (，它有 B 个 1 键 ) 来维
(cid:48)
−
持信用不变式。因此，我们可以支付分裂费用并在任何分裂期间维持信用
不变式。
在 add(x) 操作过程中，对节点唯一的其他修改发生在所有分裂（如果
有的话）完成之后。这个修改涉及向某个节点 u 添加一个新键。如果在此
(cid:48)
之前，u 有 2B 个子节点，那么现在它有 2B 个子节点，因此必须获得
(cid:48)
− −
三个积分。这些是 add(x) 方法发放的唯一积分。
删除：在调用 remove(x) 时，会发生零次或多次合并，并可能随后进行一
次借用。每次合并的发生是因为两个节点 v 和 w，它们在调用 remove(x)
之前各自恰好有 B 个键，被合并为一个恰好有 2B 个键的单个节点。
− −
因此，每次这样的合并都会释放两个信用点，可用于支付合并的成本。
在执行任何合并操作之后，最多只会发生一次借键操作，此后不会再
进行进一步的合并或借键操作。只有在我们从一个叶子节点 v 中移除一个
键，而该节点 v 刚好有 B 1 个键时，才会发生借键操作。因此节点 v 有
−
一个信用，这个信用用于支付借键的成本。这个单一的信用不足以支付借
键费用，所以我们再创建一个信用来完成支付。
此时，我们已经创建了一个信用，并且我们仍然需要证明可以维护信
用不变量。在最坏的情况下，v 的兄弟节点 w 在借用之前恰好有 B 个键，
因此之后，v 和 w 都有 B 个键。这意味着在操作完成时，v 和 w 每个都
−
应该存储一个信用。因此，在这种情况下，我们创建额外的两个信用分给
v 和 w。由于在 remove(x) 操作过程中，借用最多发生一次，这意味着我
们最多创建三个信用，如所要求的。
如果 remove(x) 操作不包含借位操作，这是因为它通过从某个节点中移
除一个键来完成，在操作之前，该节点至少有 B 个键。在最坏的情况下，
该节点恰好有 B 个键，现在有 B 1 个键，并且必须给予一个信用，我们
−
创建这个信用。
无论哪种情况——不管移除是否以借操作结束——在调用 remove(x) 时
最多只需要创建三个 credit
以维持信用不变量并支付所有发生的借用和合并。这完成了引理的证明。
引理 14.1 的目的是说明，在 word-RAM 模型中，在一系列 m 次 add(x)
和 remove(x) 操作过程中，拆分、合并和连接的成本仅为 O(Bm)。也就是
说，每次操作的摊还成本仅为 O(B)，因此在 word-RAM 模型中，add(x)
和 remove(x) 的摊还成本为 O(B + log n)。这通过以下一对定理总结如下：
定理 14.1（外部存储 B-树）。A B 树 implements the S 集合
interface. In the external memory model, a B 树 supports the operations
添加(x), 删除(x), and 查找(x) in O(log n) time per operation.

（中文关键词：外存、B树、树；英文术语：BTree）

## 14.2.4 B-树的摊销分析 (2/2)

B
定理 14.2（Word-RAM B 树）。A BTree implements the SSet inter-
face. In the word-RAM model, and ignoring the cost of splits, merges, and
borrows, a BTree supports the operations 添加(x), 删除(x), and 查找(x)
in O(log n) time per operation. Furthermore, beginning with an empty BTree,
any sequence of m 添加(x) and 删除(x) operations results in a total of O(Bm)
time spent performing splits, merges, and borrows.

（中文关键词：树；英文术语：BTree）
