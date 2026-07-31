---
structure: Stack
source: book_zh/ods_zh_2_1.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.1
page: 44
kind: textbook
---

# 2.1 数组栈：使用 A 的快速栈操作 rray

ArrayStack 使用一个数组 a（称为 backing array）来实现列表接口。索引
为 i 的列表元素存储在 a[i] 中。在大多数情况下，a 的大小比实际所需的
要大，因此使用一个整数 n 来跟踪实际存储在 a 中的元素数量。通过这种
方式，列表元素存储在 a[0], ..., a[n 1] 中，并且在任何时候，a.length n
− ≥
。
ArrayStack
T[] a;
int n;
int size() {
return n;
}
2.1.1 基础
使用 get(i) 和 set(i, x) 访问和修改 ArrayStack 的元素是很简单的。在执行
任何必要的边界检查之后，我们只需分别返回或设置 a[i]。
ArrayStack
T get(int i) {
return a[i];
}
T set(int i, T x) {
T y = a[i];
a[i] = x;
return y;
}
向 ArrayStack 添加和移除元素的操作如图 2.1 所示。要实现 add(i, x) 操
作，我们首先检查数组 a 是否已满。如果已满，我们调用方法 resize() 来
增加数组 a 的大小。resize() 的实现方式将在后文讨论。目前，知道在调用
resize() 之后，我们可以确保 a.length = n 就足够了。在解决了这个问题之
后，我们现在将元素 a[i] 到 a[n - 1] 向右移动一个位置，为 x 腾出空间，
将 a[i] 设为 x，然后将 n 加 1。
ArrayStack
void add(int i, T x) {
if (n + 1 > a.length) resize();
for (int j = n; j > i; j--)
a[j] = a[j-1];
a[i] = x;
n++;
}
如果我们忽略可能调用 resize() 的成本，那么 add(i, x) 操作的成本与我
们必须移动以给 x 腾出空间的元素数量成正比。因此，该操作的成本（忽
略调整 a 大小的成本）为 O(n i + 1)。
−
实现 remove(i) 操作类似。我们将元素 a[i + 1] 到 a[n - 1] 左移一个位置
（覆盖 a[i]）并将 n 的值减一。完成此操作后，我们检查 n 是否比 a 的长
度小得多，通过检查是否 a.length ≥ 3n。如果是这样，则调用 resize() 来
减少 a 的大小。
ArrayStack
T remove(int i) {
T x = a[i];
b r e d
add(2,e)
b r e e d
add(5,r)
b r e e d r
add(5,e)
∗
b r e e d r
b r e e d e r
remove(4)
b r e e e r
remove(4)
b r e e r
remove(4)
∗
b r e e
b r e e
set(2,i)
b r i e
0 1 2 3 4 5 6 7 8 9 10 11
图 2.1：在 ArrayStack 上执行 add(i,x) 和 remove(i) 操作的序列。箭头表示被复制的
元素。导致调用 resize() 的操作用星号标记。

（中文关键词：数组、栈；英文术语：Stack）

## Growing and Shrinking

for (int j = i; j < n-1; j++) a[j] = a[j+1];
n--; if (a.length >= 3*n) resize(); return
x;
}
如果我们忽略 resize() 方法的成本，remove(i) 操作的成本与我们移动的
元素数量成正比，即 O(n i)。
−
2.1.2 放大和缩小
resize() 方法相当直接；它分配一个大小为 2n 的新数组 b，并将 a 的 n 个
元素复制到 b 的前 n 个位置，然后将 a 设置为 b。因此，在调用 resize() 之
后，a 的长度为 2n。
ArrayStack
void resize() {
T[] b = newArray(max(n*2,1));
for (int i = 0; i < n; i++) {
b[i] = a[i];
}
a = b;
}
分析 resize() 操作的实际成本很容易。它分配一个大小为 2n 的数组 b，
并将 a 的 n 个元素复制到 b 中。这需要 O(n) 时间。
上一节的运行时间分析忽略了对 resize() 调用的成本。在本节中，我们
使用一种称为 amortized analysis 的技术来分析这一成本。这种技术不试图
确定在每次单独的 add(i, x) 和 remove(i) 操作中调整大小的成本。相反，
它考虑在一个由 m 次 add(i, x) 或 remove(i) 调用组成的序列中，所有 resize
() 调用的总成本。具体来说，我们将演示：
引理 2.1. If an empty ArrayList is created and any sequence of m 1
≥
calls to add(i, x) and remove(i) are performed, then the total time spent dur-
ing all calls to resize() is O(m).
Proof. 我们将证明，每当调用 resize() 时，自上次调用 resize() 以来对 add
或 remove 的调用次数至少为 n/2 1。因此，如果 n 表示在第 i 次调用 resi
i
−
ze() 时 n 的值，且 r 表示 resize() 的调用次数，那么对 add(i, x) 或 remove(i)
的调用总次数至少为
r
(n /2 1) m ,
i
− ≤
i=1
(cid:88)
等同于
r
n 2m + 2r .
i
≤
i=1
(cid:88)
另一方面，调用 resize() 的所有时间总和是
r
O(n ) O(m + r) = O(m) ,
i
≤
i=1
(cid:88)
由于 r 不大于 m。剩下的就是证明在第 (i 1) 次和第 i 次调用 resize() 之
−
间，对 add(i, x) 或 remove(i) 的调用次数至少为 n /2。
i
有两种情况需要考虑。第一种情况是，resize() 被 add(i{x} x) 调用，因
为底层数组 a 已经满了，即 a.length = n。考虑前一次对 resize() 的调用：
在这次前一次调用后，a 的大小是 a.length，但存储在 a 中的元素数量最多
为 a.length/2 = n/2。但现在存储在 a 中的元素数量是 n = a.length，因此自
从前一次调用 resize() 以来，至少调用了 n/2 次 add(i x) 。
第二种情况发生在 remove(i) 调用 resize() 时，因为 a.长度 3n = 3n 。
i
≥
同样，在上一次调用 resize() 之后，存储在 a 中的元素数量至少为 a.长度/2
1.1 现在，a 中存储了 n a.长度/3 个元素。因此，数量为
i
− ≤
1The 1 in this formula accounts for the special case that occurs when n = 0 and
−
a.length = 1.

（中文关键词：数组、摊还分析、栈；英文术语：Stack）
