---
structure: Stack
source: book_zh/ods_zh_2_2.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.2
page: 49
kind: textbook
---

# 2.2 FastArrayStack: An Optimized ArrayStack

r 自上次调用 resize() 以来的 remove(i) 操作次数为 最少
R a.length/2 1 a.length/3
≥ − −
= a.length/6 1
−
= (a.length/3)/2 1
−
n /2 1 .
i
≥ −
无论哪种情况，从第(i 1)次调用 resize() 到第 i 次调用 resize() 之间，调用
−
add(i, x) 或 remove(i) 的次数至少为 n /2 1，这是完成证明所必需的。
i
−
2.1.3 总结
下列定理总结了 ArrayStack 的性能：
定理 2.1. An 数组栈 implements the 列表 interface. Ignoring the
cost of calls to 调整大小(), an 数组栈 supports the operations
• 获取(i) and 设置(i, x) in O(1) time per operation; and
• add(i, x) and remove(i) in O(1 + n i) time per operation.
−
Furthermore, beginning with an empty ArrayStack and performing any se-
quence of m 添加(i, x) and 删除(i) operations results in a total of O(m) time
spent during all calls to 调整大小().
ArrayStack 是实现栈的一种高效方式。特别地，我们可以将 push(x) 实
现为 add(n, x)，将 pop() 实现为 remove(n 1)，在这种情况下，这些操作
−
将在 O(1) 的摊销时间内运行。
二.2 FastArrayStack：一个优化的 ArraySta ck
ArrayStack 所做的大部分工作涉及数据的移动（通过 add(i, x) 和 remove(i)
）和复制（通过 resize()）。在上面展示的实现中，这是使用 for 循环完成
的。事实证明，许多编程环境都有特定的函数，非常高效地复制和移动数
据块。在 C 编程语言中，有 memcpy(d, s, n) 和 memmove(d, s, n) 函数。在
C++
在该语言中有 std::copy(a0, a1, b) 算法。在 Java 中有 System.arraycopy(s, i,
d, j, n) 方法。
FastArrayStack
void resize() {
T[] b = newArray(max(2*n,1));
System.arraycopy(a, 0, b, 0, n);
a = b;
}
void add(int i, T x) {
if (n + 1 > a.length) resize();
System.arraycopy(a, i, a, i+1, n-i);
a[i] = x;
n++;
}
T remove(int i) {
T x = a[i];
System.arraycopy(a, i+1, a, i, n-i-1);
n--;
if (a.length >= 3*n) resize();
return x;
}
这些函数通常经过高度优化，甚至可能使用特殊的机器指令，这些指
令可以比使用 for 循环进行复制快得多。虽然使用这些函数并不会在渐近
意义上减少运行时间，但它仍然可能是一个值得考虑的优化。在这里的 Ja
va 实现中，使用本地的 System.arraycopy(src, srcPos, dest, destPos, length)
使速度提高了大约 2 到 3 倍，具体取决于执行的操作类型。实际效果可能
会有所不同。

（中文关键词：数组、栈；英文术语：Stack）
