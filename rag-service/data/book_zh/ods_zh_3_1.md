---
structure: SinglyLinkedList
source: book_zh/ods_zh_3_1.md
chapter: 3.1 SLList：单链表
section: 3.1
page: 77
kind: textbook
---

# 3.1 SLList：单链表

SLList（单链表）是一系列节点。每个节点 u 存储一个数据值 u.x 和一个
指向序列中下一个节点的引用 u.next。对于序列中的最后一个节点 w，w.n
ext = null
head tail
a b c d e
head tail add(x)
a b c d e x
head tail remove()
b c d e x
head tail pop()
c d e x
head tail push(y)
y c d e x
图3.1：在SLList上进行队列（add(x) 和 remove()）和栈（push(x) 和 pop()）操作的
序列。
SLList
class Node {
T x;
Node next;
}
为了提高效率，SLList 使用变量 head 和 tail 来跟踪序列中的第一个和
最后一个节点，以及一个整数 n 来跟踪序列的长度：
SLList
Node head;
Node tail;
int n;
图 3.1 展示了在 SLList 上进行的一系列栈和队列操作。
SLList 可以通过在序列的头部添加和移除元素来高效地实现栈操作 pus
h() 和 pop()。push() 操作仅需创建一个数据值为 x 的新节点 u，将 u.next
设置为列表的旧头节点，并将 u 作为列表的新头节点。最后，由于 SLList
的大小增加了 1，所以将 n 增加 1:
SLList
T push(T x) {
Node u = new Node();
u.x = x;
u.next = head;
head = u;
if (n == 0)
tail = u;
n++;
return x;
}
pop() 操作在检查 SLList 不为空之后，通过设置 head = head.next 并减
少 n 来移除头部。当移除最后一个元素时，会发生一个特殊情况，在这种
情况下 tail 被设置为 null：
SLList
T pop() {
if (n == 0) return null;
T x = head.x;
head = head.next;
if (--n == 0) tail = null;
return x;
}
显然，push(x) 和 pop() 操作的运行时间都是 O(1)。

（英文术语：SinglyLinkedList）

## 3.1.1 队列操作

SLList 也可以以常数时间实现 FIFO 队列操作 add(x) 和 remove()。移除操
作是从列表的头部进行的，与 pop() 操作相同：
SLList
T remove() {
if (n == 0) return null;
T x = head.x;
head = head.next;
if (--n == 0) tail = null;
return x;
}
另一方面，添加操作是在列表的尾部进行的。在大多数情况下，这是
通过设置 tail.next = u 来完成的，其中 u 是包含 x 的新创建节点。然而，
当 n = 0 时会出现一种特殊情况，此时 tail = head = null。在这种情况下，t
ail 和 head 都被设置为 u。
SLList
boolean add(T x) {
Node u = new Node();
u.x = x;
if (n == 0) {
head = u;
} else {
tail.next = u;
}
tail = u;
n++;
return true;
}
显然，add(x) 和 remove() 都是常数时间操作。

（英文术语：SinglyLinkedList）

## 3.1.2 总结

下列定理总结了 SLList 的性能：
定理 3.1. An SLList implements the 栈 and (FIFO) 队列 inter- faces. The pu
sh(x), pop(), add(x) and remove() operations run in O(1) time per operation.
SLList几乎实现了双端队列的全部操作。唯一缺少的操作是从SLList的
尾部移除元素。从SLList的尾部移除元素很困难，因为这需要更新tail的值
，使其指向SLList中位于tail之前的节点w；这个节点w满足 w.next = tail。
不幸的是，唯一达到w的方法是从head开始遍历SLList，经过 n - 2 步。
dummy
a b c d e
图 3.2：一个包含 a、b、c、d、e 的双向链表。

（英文术语：SinglyLinkedList）
