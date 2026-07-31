---
structure: Queue
source: book_zh/ods_zh_2_3.md
chapter: 2.1 数组栈：使用 A 的快速栈操作 rray
section: 2.3
page: 50
kind: textbook
---

# 2.3 ArrayQueue：基于数组的队列

## ArrayQueue：基于数组的队列 (1/2)

在本节中，我们介绍了 ArrayQueue 数据结构，它实现了一个 FIFO（先进
先出）队列；元素从队列中移除（使用 remove() 操作）的顺序与它们被添
加（使用 add(x) 操作）的顺序相同。
注意，ArrayStack 并不是 FIFO 队列实现的好选择。这不是一个好的选
择，因为我们必须选择列表的一端来添加元素，然后从另一端移除元素。
两个操作中的一个必须在列表的头部进行，这涉及调用 add(i, x) 或 remove
(i)，其中 i 的值为 = 0。这会带来与 n 成正比的运行时间。
为了获得一个高效的基于数组的队列实现，我们首先注意到如果我们
有一个无限数组 a，问题会很容易。我们可以维护一个索引 j 来跟踪下一
个要移除的元素，以及一个整数 n 来计算队列中的元素数量。队列元素将
始终存储在
a[j], a[j + 1], . . . , a[j + n 1] .
−
最初，j 和 n 都会被设置为 0。要添加一个元素，我们会将其放入 a[j + n]
并将 n 增加。要移除一个元素，我们会从 a[j] 中移除它，增加 j，并将 n
减少。
当然，这种解决方案的问题在于它需要一个无限数组。ArrayQueue 通
过使用一个有限数组 a 和 modular arithmetic 来模拟这一点。这就是我们
在谈论时间时使用的那种算术。例如 10:00 加上五小时得到 3:00。正式地
，我们说
10 + 5 = 15 3 (mod 12) .
≡
我们把这个等式的后半部分读作“15 模 12 同余于 3”。我们也可以把 mo
d 当作一个二元运算符，这样
15 mod 12 = 3 .
更一般地，对于一个整数 a 和正整数 m，a mod m 是唯一的整数 r {0
∈
, . . . , m 1}，使得 a = r + km 对某个整数 k 成立。非正式地，值 r 是我们
−
用 a 除以 m 时得到的余数。在许多编程语言中，包括 Java，mod 运算符
用 % 符号表示。2
2This is sometimes referred to as the brain-dead mod operator, since it does not correctly
implement the mathematical mod operator when the first argument is negative.
模运算对于模拟无限数组非常有用，因为 i mod a.length 总是给出一个
位于 0, . . . , a.length 1 范围内的值。使用模运算，我们可以将队列元素存
−
储在数组位置上
a[j%a.length], a[(j + 1)%a.length], . . . , a[(j + n 1)%a.length] .
−
这将数组 a 视为一个 circular array，其中大于 a.length 1 的数组索引会
−
“回绕”到数组的开头。
唯一剩下需要担心的事情是确保 ArrayQueue 中的元素数量不超过 a 的
大小。
ArrayQueue
T[] a;
int j;
int n;
图 2.2 展示了在 ArrayQueue 上进行 add(x) 和 remove() 操作的序列。为
了实现 add(x)，我们首先检查 a 是否已满，如有必要，调用 resize() 来增
加 a 的大小。接下来，我们将 x 存储在 a[(j + n)%a.length] 中，并增加 n。
ArrayQueue
boolean add(T x) {
if (n + 1 > a.length) resize();
a[(j+n) % a.length] = x;
n++;
return true;
}
要实现 remove()，我们首先存储 a[j] 以便稍后返回。接下来，我们通
过设置 j = (j + 1) mod a.length 来递减 n 并递增 j。最后，我们返回存储的 a
[j] 的值。如有必要，我们可以调用 resize() 来减小数组 a 的大小。
数组队列
T remove() { if (n == 0) 抛出新的 NoSuchElementException();
T x = a[j]; j = (j + 1) % a.length;
j = 2, n = 3 a b c
add(d)
j = 2, n = 4 a b c d
add(e)
j = 2, n = 5 e a b c d
remove()
j = 3, n = 4 e b c d
add(f)
j = 3, n = 5 e f b c d
add(g)
j = 3, n = 6 e f g b c d
add(h)
∗
j = 0, n = 6 b c d e f g
j = 0, n = 7 b c d e f g h
remove()
j = 1, n = 6 c d e f g h
0 1 2 3 4 5 6 7 8 9 10 11
图 2.2：在 ArrayQueue 上进行 add(x) 和 remove(i) 操作的序列。箭头表示正在被复
制的元素。导致调用 resize() 的操作用星号标出。
n--;
if (a.length >= 3*n) resize();
return x;
}
最后，resize() 操作与 ArrayStack 的 resize() 操作非常相似。它分配一
个大小为 2n 的新数组 b 并进行复制
a[j], a[(j + 1)%a.length], . . . , a[(j + n 1)%a.length]
−
到⋯上面
b[0], b[1], . . . , b[n 1]
−
并将 j = 设为 0。

（中文关键词：数组、队列、栈；英文术语：Queue）

## ArrayQueue：基于数组的队列 (2/2)

ArrayQueue
void resize() {
T[] b = newArray(max(1,n*2));
for (int k = 0; k < n; k++)
b[k] = a[(j+k) % a.length];
a = b;
j = 0;
}

（中文关键词：数组、队列；英文术语：Queue）

## 2.3.1 总结

以下定理总结了 ArrayQueue 数据结构的性能：
定理 2.2. An 数组队列 implements the (FIFO) 队列 interface. Ig-
noring the cost of calls to 调整大小() , an 数组队列 supports the operations
添加(x) and 移除() in O(1) time per operation. Furthermore, beginning with
an empty 数组队列 , any sequence of m 添加(i, x) and 移除(i) operations
results in a total of O(m) time spent during all calls to 调整大小() .

（中文关键词：数组、队列；英文术语：Queue）
