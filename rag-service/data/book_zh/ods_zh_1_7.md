---
structure: 
source: book_zh/ods_zh_1_7.md
chapter: 1.1 对效率的需求
section: 1.7
page: 36
kind: textbook
---

# 1.7 数据结构列表

表 1.1 和表 1.2 总结了本书中实现每个接口（List、USet 和 SSet，见第 1.2
节）的数据结构的性能。图 1.6 显示了本书各章节之间的依赖关系。虚线
箭头表示只有弱依赖，即只有章节的一小部分依赖于前一章节，或者仅依
赖前一章节的主要结果。
List implementations
get(i)/set(i, x) add(i, x)/remove(i)
ArrayStack O(1) O(1 + n i)A § 2.1
ArrayDeque O(1) O(1 + m − in i, n i )A § 2.4
DualArrayDeque O(1) O(1 + min { i, n − i } )A § 2.5
RootishArrayStack O(1) O(1 + n i { )A − } § 2.6
−
DLList O(1 + min i, n i ) O(1 + min i, n i ) § 3.2
SEList O(1 + min { i, n − i } /b) O(b + min { i, n − i } /b)A § 3.3
SkiplistList O(log n)E { − } O(log n)E { − } § 4.3
USet implementations
find(x) add(x)/remove(x)
ChainedHashTable O(1)E O(1)A,E § 5.1
LinearHashTable O(1)E O(1)A,E § 5.2
A 表示一个 amortized 的运行时间。E
表示一个 expected 的运行时间。
表 1.1：列表和 USet 实现摘要。
SSet implementations
find(x) add(x)/remove(x)
SkiplistSSet O(log n)E O(log n)E § 4.2
Treap O(log n)E O(log n)E § 7.2
ScapegoatTree O(log n) O(log n)A § 8.1
RedBlackTree O(log n) O(log n) § 9.2
BinaryTrieI O(w) O(w) § 13.1
XFastTrieI O(log w)A,E O(w)A,E § 13.2
YFastTrieI O(log w)A,E O(log w)A,E § 13.3
BTree O(log n) O(B + log n)A § 14.2
BTreeX O(log n) O(log n) § 14.2
B B
(Priority) Queue implementations
findMin() add(x)/remove()
BinaryHeap O(1) O(log n)A § 10.1
MeldableHeap O(1) O(log n)E § 10.2
我 这个结构只能存储 w 位整数数据。X 这表示外存模型中
的运行时间；参见第14章。
表1.2：SSet和优先队列实现摘要。
1. Introduction
2. Array-based lists 3. Linked lists
3.3 Space-efficient linked lists
5. Hash tables
4. Skiplists
6. Binary trees 7. Random binary search trees 11. Sorting algorithms
11.1.2. Quicksort
8. Scapegoat trees 11.1.3. Heapsort
9. Red-black trees
10. Heaps
12. Graphs
13. Data structures for integers
14. External-memory searching
图1.6：本书各章节之间的依赖关系。

（中文关键词：树、数组、堆、跳表、字典树、链表）
