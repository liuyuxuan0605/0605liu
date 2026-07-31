---
structure: DoublyLinkedList
source: book_zh/ods_zh_3_2.md
chapter: 3.1 SLList：单链表
section: 3.2
page: 81
kind: textbook
---

# 3.2 DLList：双向链表

DLList（双向链表）与SLList非常相似，只是DLList中的每个节点u都包含
指向其后继节点u.next以及前驱节点u.prev的引用。
DLList
class Node {
T x;
Node prev, next;
}
在实现 SLList 时，我们看到总是有几个需要注意的特殊情况。例如，
从 SLList 中移除最后一个元素或向空 SLList 添加一个元素都需要小心，
以确保 head 和 tail 被正确更新。在 DLList 中，这些特殊情况的数量会显
著增加。也许处理 DLList 中所有这些特殊情况最干净的方法是引入一个
虚拟节点。这是一个不包含任何数据的节点，但作为占位符，使得没有特
殊节点；每个节点都有 next 和 prev，虚拟节点充当紧跟列表最后一个节点
之后和列表第一个节点之前的节点。通过这种方式，列表中的节点（双向
）链接成一个循环，如图 3.2 所示。
DLList
int n;
Node dummy;
DLList() {
dummy = new Node();
dummy.next = dummy; d
ummy.prev = dummy; n
= 0;
}
在双向链表中找到具有特定索引的节点很容易；我们可以从链表的头
部（dummy.next）开始向前查找，或者从链表的尾部（dummy.prev）开始
向后查找。这使我们能够在 O(1 + min{i, n i}) 时间内到达第 i 个节点：
−
DLList
Node getNode(int i) {
Node p = null;
if (i < n / 2) {
p = dummy.next;
for (int j = 0; j < i; j++)
p = p.next;
} else {
p = dummy;
for (int j = n; j > i; j--)
p = p.prev;
}
return (p);
}
现在，get(i) 和 set(i, x) 操作也很简单。我们首先找到第 i 个节点，然后
获取或设置它的 x 值：
DLList
T get(int i) {
return getNode(i).x;
}
T set(int i, T x) {
Node u = getNode(i);
T y = u.x;
u.x = x;
return y;
}
这些操作的运行时间主要取决于找到第 i 个节点所需的时间，因此为
O(1 + min{i, n i})。
−
u
u.prev u.next
w
· · · · · ·
图 3.3：在 DLList 中将节点 u 添加到节点 w 之前。

（英文术语：DoublyLinkedList）

## 3.2.1 添加与移除

如果我们有一个指向双向链表节点 w 的引用，并且我们想在 w 之前插入
一个节点 u，那么这只是设置 u.next = w、u.prev = w.prev，然后调整 u.pre
v.next 和 u.next.prev 的问题。（见图 3.3。）多亏了哑节点，不需要担心 w
.prev 或 w.next 不存在。
DLList
Node addBefore(Node w, T x) {
Node u = new Node();
u.x = x;
u.prev = w.prev;
u.next = w;
u.next.prev = u;
u.prev.next = u;
n++;
return u;
}
现在，列表操作 add(i, x) 的实现很简单。我们找到 DLList 中的第 i 个
节点，并在其前插入一个包含 x 的新节点 u。
DLList
void add(int i, T x) {
addBefore(getNode(i), x);
}
add(i, x) 的运行时间中唯一的非恒定部分是找到第 i 个节点（使用 getN
ode(i)）所需的时间。因此，add(i, x) 的运行时间为 O(1 + min{i, n i}) 时
−
间。
从双向链表中移除节点 w 很容易。我们只需要调整 w 的下一个和上一
个指针，使它们跳过 w。再次使用哑节点消除了考虑任何特殊情况的需要
：
DLList
void remove(Node w) {
w.prev.next = w.next;
w.next.prev = w.prev;
n--;
}
现在 remove(i) 操作很简单。我们找到索引为 i 的节点并将其移除：
DLList
T remove(int i) {
Node w = getNode(i);
remove(w);
return w.x;
}
同样，这个操作中唯一昂贵的部分是使用 getNode(i) 查找第 i 个节点，
因此 remove(i) 的运行时间为 O(1 + min{i, n i})。
−

（英文术语：DoublyLinkedList）

## 3.2.2 总结

下列定理总结了 DLList 的性能：
定理 3.2. A 双向链表 implements the 列表 interface. In this implementa-
tion, the 获取(i), 设置(i, x), 添加(i, x) and 删除(i) operations run in O(1 +
最小{i, n i}) time per operation.
−
值得注意的是，如果我们忽略 getNode(i) 操作的成本，那么对 DLList
的所有操作都需要恒定时间。因此，对 DLList 的操作中唯一昂贵的部分
是查找相关的节点。
一旦我们得到相关的节点，在该节点添加、删除或访问数据只需恒定时间
。
这与第2章的基于数组的列表实现形成了鲜明的对比；在那些实现中，
相关的数组项可以在常数时间内找到。然而，添加或删除元素需要移动数
组中的元素，并且一般来说，需要非恒定时间。
因此，链表结构非常适合那些可以通过外部手段获取对列表节点的引
用的应用。一个例子是 Java 集合框架中的 LinkedHashSet 数据结构，其中
一组元素存储在双向链表中，而双向链表的节点存储在哈希表中（在第 5
章讨论）。当从 LinkedHashSet 中删除元素时，使用哈希表在常数时间内
找到相关的列表节点，然后删除该列表节点（也在常数时间内）。

（英文术语：DoublyLinkedList）
