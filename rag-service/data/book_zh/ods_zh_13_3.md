---
structure: 
source: book_zh/ods_zh_13_3.md
chapter: 13.1 二进制字典树：一种数字搜索树
section: 13.3
page: 289
kind: textbook
---

# 13.3 YFastTrie：双对数时间 SSet

## YFastTrie：双对数时间 SSet (1/3)

XFastTrie 在查询时间方面相比 BinaryTrie 有巨大的——甚至是指数级的—
—提升，但 add(x) 和 remove(x) 操作仍然不是特别快。此外，空间使用量
O(n · w) 也高于本书中描述的其他 SSet 实现，它们都使用 O(n) 的空间。
这两个问题是相关的；如果 n 次 add(x) 操作构建了一个大小为 n · w 的结
构，那么每次 add(x) 操作至少需要 w 级别的时间（和空间）。
接下来讨论的 YFastTrie 同时提高了 XFastTrie 的空间利用率和速度。
YFastTrie 使用一个 XFastTrie，称为 xft，但只在 xft 中存储 O(n/w) 个值。
通过这种方式，xft 使用的总空间仅为 O(n)。此外，在 YFastTrie 中，每进
行 w 次 add(x) 或 remove(x) 操作，只有一次会导致在 xft 中执行 add(x) 或
remove(x) 操作。通过这样做，对 xft 的 add(x) 和 remove(x) 操作的平均开
销仅为常数。
显而易见的问题是：如果 xft 只存储 n/w 个元素，其余的 n(1 1/w) 个
−
元素会去哪儿？这些元素会移入 sec- ondary structures，在此情况下是一
种扩展版的 treaps（第 7.2 节）。大约有 n/w 个这样的二级结构，因此平
均而言，每个结构存储 O(w) 个元素。Treaps 支持对数时间的 SSet 操作，
因此这些 treaps 上的操作将按 O(log w) 时间运行，如所要求的。
更具体地说，YFastTrie 包含一个 XFastTrie，即 xft，它包含数据的一
个随机样本，其中每个元素以概率 1/w 独立地出现在样本中。为了方便起
见，值 2w 1 总是包含在 xft 中。设 x < x < · · · < x 表示存储在 xft
0 1 k 1
− −
中的元素。与每个元素 x 关联的是一个 treap，即 t ，它存储范围在 x +
i i i 1
−
1, . . . , x 内的所有值。这在图 13.7 中有所示。
i
在 YFastTrie 中，find(x) 操作相当简单。我们在 xft 中搜索 x，并找到
与 treap t 相关的某个值 x 。然后我们使用 t 上的 treap find(x) 方法来回答
i i i
查询。整个方法是一行代码：
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0, 1, 3 4, 5, 8, 9 10, 11, 13
图 13.7：一个 YFastTrie，包含值 0、1、3、4、6、8、9、10、11 和 13。
YFastTrie T find(T x) { return xft.find(ne
w Pair<T>(it.intValue(x))).t.find(x); }
第一次 find(x) 操作（在 xft 上）需要 O(log w) 时间。第二次 find(x) 操
作（在 treap 上）需要 O(log r) 时间，其中 r 是 treap 的大小。在本节后面
，我们将展示 treap 的期望大小是 O(w)，因此该操作需要 O(log w) 时间。
1
向 YFastTrie 添加元素通常也相当简单——大多数时候。add(x) 方法调
用 xft.find(x) 来定位应该插入 x 的 treap t。然后它调用 t.add(x) 将 x 添加到
t。此时，它投掷一个偏置硬币，这个硬币出现正面（heads）的概率是 1/
w，出现反面（tails）的概率是 1 1/w。如果硬币正面朝上，那么 x 将被
−
添加到 xft。
事情在这里变得有点复杂。当 x 被加入到 xft 时，treap t 需要被分成两
个 treap，t1 和 t 。treap t1 包含所有小于或等于 x 的值；t 是原始的 treap
(cid:48) (cid:48)
，
1This is an application of Jensen’s Inequality: If E[r] = w, then E[logr] logw.
≤
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0, 1, 2, 3 4, 5, 6 4, 5,88,,99 10, 11, 13
图 13.8：向 YFastTrie 添加值 2 和 6。6 的掷币结果是正面，所以 6 被添加到 xft，
并且包含 4,5,6,8,9 的 treap 被拆分。
t，已移除 t1 的元素。一旦完成此操作，我们将对 (x, t1) 添加到 xft 中。图
13.8 显示了一个示例。

（中文关键词：树堆、字典树）

## YFastTrie：双对数时间 SSet (2/3)

YFastTrie
boolean add(T x) {
int ix = it.intValue(x);
STreap<T> t = xft.find(new Pair<T>(ix)).t;
if (t.add(x)) {
n++;
if (rand.nextInt(w) == 0) {
STreap<T> t1 = t.split(x);
xft.add(new Pair<T>(ix, t1));
}
return true;
}
return false;
}
将 x 添加到 t 需要 O(log w) 时间。练习 7.12 显示，将 t 拆分为 t1 和 t
(cid:48)
也可以在 O(log w) 的预期时间内完成。添加该
将 (x,t1) 配对到 xft 需要 O(w) 时间，但只以概率 1/w 发生。因此，add(x)
操作的期望运行时间是
1
O(log w) + O(w) = O(log w) .
w
remove(x) 方法撤销 add(x) 所执行的操作。我们使用 xft 在 xft 中找到包
含 xft.find(x) 答案的叶节点 u。从 u，我们得到包含 x 的 treap t，并从 t 中
移除 x。如果 x 也存储在 xft 中（且 x 不等于 2w 1），那么我们从 xft 中
−
移除 x，并将 x 的 treap 中的元素添加到由 u 在链表中的后继存储的 treap t
2 中。这在图 13.9 中有所说明。
YFastTrie
boolean remove(T x) {
int ix = it.intValue(x);
Node<T> u = xft.findNode(ix);
boolean ret = u.x.t.remove(x);
if (ret) n--;
if (u.x.x == ix && ix != 0xffffffff) {
STreap<T> t2 = u.child[1].x.t;
t2.absorb(u.x.t);
xft.remove(u.x);
}
return ret;
}
在 xft 中查找节点 u 需要 O(log w) 的期望时间。从 t 中移除 x 需要 O(l
og w) 的期望时间。同样，练习 7.12 显示，将 t 的所有元素合并到 t2 中可
以在 O(log w) 时间内完成。如果有必要，从 xft 中移除 x 需要 O(w) 时间
，但 x 仅以概率 1/w 出现在 xft 中。因此，从 YFastTrie 中移除一个元素的
期望时间为 O(log w)。
在讨论的早期，我们推迟了关于这个结构中 treaps 大小的争论，留到
以后再讨论。在结束本章之前，我们证明我们需要的结果。
引理 13.1. Let x be an integer stored in a YFastTrie and let n denote the
x
number of elements in the treap, t, that contains x. Then E[n ] 2w 1.
x
≤ −
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0,1,2,3 4, 5, 6 8, 9 8, 10, 11, 13
图13.9：从图13.8中的YFastTrie中移除值1和9。
Proof. 参见图13.10。设 x < x < · · · < x = x < x < · · · < x 表示存储在
1 2 i i+1 n
YFastTrie 中的元素。treap t 包含一些大于或等于 x 的元素。这些元素是 x
, x , . . . , x ，其中 x 是这些元素中唯一在 add(x) 方法中进行的偏
i i+1 i+j 1 i+j 1
− −
置投币结果为正面的元素。换句话说，E[j] 等于获得第一次正面所需的偏
置投币的期望次数。每次投币都是独立的，并且正面出现的概率为 1/w，
所以 E[j] w。（对于 w = 2 的情况，参见引理 4.2 的分析。）
≤
同样，小于 x 的 t 元素是 x , . . . , x ，其中所有这些 k 次投币都显示
i 1 i k
− −
为反面，而 x 的投币显示为正面。因此，E[k] w 1，因为这是前
i k 1
− − ≤ −
一段中考虑的相同投币实验，只是最后一次投币未被计入。总之，n
= j + k，所以
x
E[n ] = E[j + k] = E[j] + E[k] 2w 1 .
x
≤ −
2This analysis ignores the fact that j never exceeds n i +1. However, this only decreases
−
E[j], so the upper bound still holds.
elements in treap, t, containing x
H T T ... T T T T T ... T H
x i
−
k
−
1 xz i
−
k x i
−
k + 1 . . . x i
−
2 x i
−
1 x i }=| x x i + 1 x i + 2 . . . x i + j
−
2 x i + j {
−
1
k j
| {z } | {z }
图13.10：包含x的treap t中的元素数量由两个抛硬币实验决定。

（中文关键词：树堆、字典树）

## YFastTrie：双对数时间 SSet (3/3)

引理 13.1 是以下定理证明的最后一部分，该定理总结了 YFastTrie 的
性能：
定理 13.3. A YFastTrie implements the SSet interface for w-bit inte- gers. A
YFastTrie supports the operations 添加(x), 删除(x), and 查找(x) in O(log w
) expected time per operation. The space used by a YFastTrie that stores n
values is O(n + w).
空间需求中的 w 项来自于 xft 总是存储值 2w 1 的事实。实现可以被
−
修改（代价是向代码中添加一些额外的情况），以便不再需要存储这个值
。在这种情况下，定理中的空间需求变为 O(n)。

（中文关键词：字典树）
