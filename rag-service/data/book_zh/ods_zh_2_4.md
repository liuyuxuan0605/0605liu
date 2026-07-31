---
structure: Deque
source: book_zh/ods_zh_2_4.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.4
page: 54
kind: textbook
---

# 2.4 ArrayDeque：使用数组进行快速双端队列操作

上一节的 ArrayQueue 是一种用于表示序列的数据结构，它允许我们高效
地在一端添加元素
从另一端进行顺序操作并移除。ArrayDeque 数据结构允许在两端高效地添
加和移除。该结构通过使用与表示 ArrayQueue 相同的循环数组技术实现
List 接口。
ArrayDeque
T[] a;
int j;
int n;
在 ArrayDeque 上的 get(i) 和 set(i, x) 操作很直接。它们获取或设置数组
元素 a[(j + i) mod a.length]。
ArrayDeque
T get(int i) {
return a[(j+i)%a.length];
}
T set(int i, T x) {
T y = a[(j+i)%a.length];
a[(j+i)%a.length] = x;
return y;
}
add(i{x} x) 的实现有趣一些。像往常一样，我们首先检查 a 是否已满
，如果必要的话，调用 resize() 来调整 a 的大小。记住，当 i 较小（接近 0
）或 i 较大（接近 n）时，我们希望此操作尽可能快。因此，我们检查 i
是否小于 n/2。如果是，我们将元素 a[0] 到 a[i-1] 左移一位。否则（i >= n/
2），我们将元素 a[i] 到 a[n-1] 右移一位。有关 ArrayDeque 上 add(i, x) 和 r
emove(x) 操作的示意，请参见图 2.3。
ArrayDeque void add(int i, T x) { if (n+1 > a.l
ength) resize(); if (i < n/2) { // 将 a[0],..,a[i-1] 向左移动一个位置 j = (j == 0)
? a.length - 1 : j - 1; //(j-1)mod a.length for (int k = 0; k <= i-1; k++) a[(j+k)%a.
length] = a[(j+k+1)%a.length];
j = 0, n = 8 a b c d e f g h
remove(2)
j = 1, n = 7 a b d e f g h
add(4,x)
j = 1, n = 8 a b d e x f g h
add(3,y)
j = 0, n = 9 a b d y e x f g h
add(4,z)
j = 11, n = 10 b d y z e x f g h a
0 1 2 3 4 5 6 7 8 9 10 11
图 2.3：在 ArrayDeque 上进行 add(i,x) 和 remove(i) 操作的序列。箭头表示正在复
制的元素。
} else { // 将 a[i],..,a[n-1] 向右移动一个位置 for (int k = n; k > i; k
--) a[(j+k)%a.length] = a[(j+k-1)%a.length]; }a[(j+i)%a.length] = x; n
++; }
通过以这种方式进行移动，我们保证 add(i, x) 永远不需要移动超过 min
{i, n i} 个元素。因此，add(i, x) 操作的运行时间（忽略 resize() 操作的开
−
销）为 O(1 + min{i, n i})。
−
remove(i) 操作的实现类似。它要么将元素 a[0], . . . , 到 a[i - 1] 向右移
−
动一个位置，要么将元素 a[i +] 到 a[n - 1], . . . , 向左移动一个位置，这取
−
决于 i < 是否小于 n//2。同样，这意味着 remove(i) 在移动元素时从不花费
超过 O(1 + min{i,, n - i}) 的时间。
数组双端队列
T remove(int i) { T x = a[(j+i)%a.length]; if (i < n/2) { // 将 a[0],..,[i-1] 元素
向右移动一个位置 for (int k = i; k > 0; k--)
a[(j+k)%a.length] = a[(j+k-1)%a.length]; j = (j + 1) % a.lengt
h; } else { // 将 a[i+1],..,a[n-1] 左移一位 for (int k = i; k < n-1; k++) a[
(j+k)%a.length] = a[(j+k+1)%a.length]; } n--; if (3*n < a.length) resize(
); return x; }

（中文关键词：数组、双端队列、队列；英文术语：Deque）

## 2.4.1 总结

以下定理总结了 ArrayDeque 数据结构的性能：
定理 2.3. An ArrayDeque implements the 列表 interface. Ignoring the
cost of calls to 调整大小(), an ArrayDeque supports the operations
• 获取(i) and 设置(i, x) in O(1) time per operation; and
• 添加(i, x) and 删除(i) in O(1 + 最小{i, n i}) time per operation.
−
Furthermore, beginning with an empty ArrayDeque, performing any sequence
of m 添加(i, x) and 删除(i) operations results in a total of O(m) time spent
during all calls to 调整大小().

（中文关键词：数组、双端队列；英文术语：Deque）
