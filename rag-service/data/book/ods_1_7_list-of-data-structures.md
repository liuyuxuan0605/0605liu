---
structure: 
source: book/ods_1_7_list-of-data-structures.md
chapter: 1. Introduction
section: 1.7
page: 36
kind: textbook
---

# 1.7 List of Data Structures

Tables 1.1 and 1.2 summarize the performance of data structures in this
book that implement each of the interfaces, List, USet, and SSet, de-
scribed in Section 1.2. Figure 1.6 shows the dependencies between vari-
ous chapters in this book. A dashed arrow indicates only a weak depen-
dency, in which only a small part of the chapter depends on a previous
chapter or only the main results of the previous chapter.
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
A Denotes an amortized running time.
E Denotes an expected running time.
Table 1.1: Summary of List and USet implementations.
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
I This structure can only store w-bit integer data.
X This denotes the running time in the external-memory
model; see Chapter 14.
Table 1.2: Summary of SSet and priority Queue implementations.
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
Figure 1.6: The dependencies between chapters in this book.

（中文关键词：树、数组、堆、跳表、字典树、链表）
