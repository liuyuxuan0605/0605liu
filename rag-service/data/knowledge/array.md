---
structure: Array
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# Array 知识点（理论讲解，来源 VisuAlgo）

本文讲解**数组（Array）**这一最基础的数据结构，以及它如何实现 List ADT。
数组的核心特征是元素在内存中**连续存储**，因此支持 O(1) 随机访问（直接按下标取元素）；这正是它与**链表（Linked List）**最本质的区别——链表节点非连续、靠指针串联，随机访问需要 O(N) 从头遍历。

## 数组与链表的区别（Array vs Linked List 对比）

面试常问「数组和链表有什么区别」，核心差异如下表：

| 维度 | 数组（Array） | 链表（Linked List） |
| --- | --- | --- |
| 内存布局 | 元素**连续**存储在一块内存 | 节点**非连续**存储，靠指针串联 |
| 随机访问 get(i) | O(1)，直接下标访问 | O(N)，必须从头遍历 |
| 头部插入 / 删除 | O(N)，需搬移后续元素 | O(1) |
| 尾部插入（已知尾指针） | O(1)（动态数组均摊 O(1)） | O(1) |
| 尾部删除 | O(1) | 单链表 O(N)、双链表 O(1) |
| 空间开销 | 可能预留空间浪费，满时需扩容搬移（O(N)） | 每节点额外指针（双向链表多一个 prev 指针） |
| 适用场景 | 频繁随机访问、大小较固定 | 频繁在头尾增删、大小不确定（如实现栈 / 队列） |

一句话总结：**数组胜在随机访问快、缓存友好；链表胜在增删灵活、无需搬移**。两者都能实现 List ADT，取舍看操作 profile（访问多就用数组，增删多就用链表）。

## (Resize-able) Array

Visualization of one of the simplest data structure in Computer Science:
Array
(and its sorted form) surprisingly has not been done in VisuAlgo since its inception 2011-January 2024...
Stay tuned while we improve this page and its features.

## Motivation

(Compact) Array is among the easiest and the most versatile data structure in Computer Science. Array is built-in almost all programming languages, e.g., C++, Python ('array' is called as 'list' in Python), Java, etc.
We can use (Compact) Array to implement List ADT.
We can use (Compact) Array to solve many classic problems. When not being used as a List ADT implementation (where positional order matters), it is often beneficial to first
sort
the elements first so that we can utilize faster algorithms.

## List ADT

Please see
List ADT
overview.

## Array Implementation (Part 1)

(Compact) Array is a good candidate for implementing the List ADT as it is a simple construct to handle a collection of items.
When we say compact array, we mean an array that has
no gap
, i.e., if there are
N
items in the array (that has size
M
, where
M ≥ N
), then only index [0..
N
-1] are occupied and other indices [
N
..
M
-1] should remain
empty
.

## Array Implementation (Part 1)

Let the
compact
array name be
A
with index [0..
N
-1] occupied with the items of the list.
get(i)
, just return
A[i]
.
This simple operation will be unnecessarily complicated if the array is
not
compact.
search(v)
, we check each index
i
∈ [0..
N
-1] one by one to see if
A[i] == v
.
This is because
v
(if it exists) can be anywhere in index [0..
N
-1].
Since this visualization only accept distinct items,
v
can only be found at most once.
In a general List ADT, we may want to have
search(v)
returns a list of indices.
insert(i, v)
, we shift items ∈ [
i
..
N
-1] to [
i
+1..
N
] (
from backwards
) and set
A[i] = v
.
This is so that
v
is inserted correctly at index
i
and maintain compactness.
remove(i)
, we shift items ∈ [
i+1
..
N
-1] to [
i
..
N
-2], overwriting the old
A[i]
.
This is to maintain compactness.

## Time Complexity Summary

get(i)
is very fast: Just one access, O(
1
).
Another CS course: 'Computer Organisation' discusses the details on this O(
1
)
performance of this array indexing operation.
search(v)
In the best case,
v
is found at the first position, O(
1
).
In the worst case,
v
is not found in the list and we require O(
N
) scan to determine that.
insert(i, v)
In the best case, insert at
i = N
, there is no shifting of element, O(
1
).
In the worst case, insert at
i = 0
, we shift all
N
elements, O(
N
).
remove(i)
In the best case, remove at
i = N-1
, there is no shifting of element, O(
1
).
In the worst case, remove at
i = 0
, we shift all
N
elements, O(
N
).

## Fixed Space Issue

The size of the compact array
M
is not infinite, but a finite number. This poses a problem as the maximum size may not be known in advance in many applications.
If
M
is too big, then the unused spaces are wasted.
If
M
is too small, then we will run out of space easily.

## Variable Space

Solution: Make
M
a variable. So when the array is full, we create a larger array (usually two times larger) and move the elements from the old array to the new array. Thus, there is no more limits on size other than the (usually large) physical computer memory size.
C++ STL std::vector
,
Python list
,
Java Vector
, or
Java ArrayList
all implement this variable-size array. Note that Python
list
and Java Array
List
are
not
Linked Lists, but are actually variable-size arrays. This array visualization implements this doubling-when-full strategy.
However, the classic array-based issues of space wastage and copying/shifting items overhead are still problematic.

## Compact Array Applications

There are various applications that can be done on a Compact (Integer) Array
A
:
Searching for a specific value
v
in array
A
,
Finding the min/max or the k-th smallest/largest value in (static) array
A
,
Testing for uniqueness and deleting duplicates in array
A
,
Counting how many time a specific value
v
appear in array
A
,
Set intersection/union between array
A
and another sorted array
B
,
Finding a target pair
x
∈
A
and
y
∈
A
such that
x+y
equals to a target
z
,
Counting how many values in array
A
is inside range [
lo
..
hi
], etc.
See
unsorted array
and
sorted array
hints.

## Actions

We will outline the possible actions that you can do in this page. For now, just try to guess based on the name of the function.

## Visualizations

We will talk about the two modes: array (the content can be unsorted) versus sorted array (the content must always be sorted, without loss of generality: sorted in non-decreasing order).

## (Unsorted) Array

There are already lots of (simple) applications that we can do with unsorted array.

## Algorithm Ideas (Unsorted Array)

We can use O(
N
) linear search (leftmost to rightmost or vice versa) to find
v
,
For min/max, we can use O(
N
) linear search again;
for k-th smallest/largest, we may need to use O(
kN
) algorithm
1
,
We can use O(
N^2
) nested-loop to see if any two indices in
A
are the same,
We may need to use
Hash Table
to do this in O(
N
),
O(
N^2
) nested-loop is needed,
O(
N^2
) nested-loop is needed,
We may need to use
Hash Table
to do this in O(
N
).
There are better ways, especially if the array if
sorted
.
1
There is a faster expected O(
N
) QuickSelect or O(
N
) worst-case linear time selection.

## (Sorted) Array

When the array is sorted, we open up a lot of possibilities.

## Algorithm Ideas (Sorted Array)

We can use O(log
N
) binary search on a sorted array,
A[0]/A[k-1]/A[N-k]/A[N-1] are the min/k-th smallest/k-th largest/max value in (static sorted) array
A
,
Duplicates, if any, will be next to each other in a sorted array
A
,
Same as above,
We can use modifications of merge routine of Merge Sort,
We can use two pointers method,
The index of
y
- the index of
x
+ 1 (use two binary searches).
There can be other ways.
