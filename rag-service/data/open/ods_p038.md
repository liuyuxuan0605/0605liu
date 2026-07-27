---
structure:
source: open/ods_p038.md
page: 38
---

# ODS p38: §1.7 Introduction

§1.7 Introduction
SSet implementations
find (x) add(x)/remove (x)
SkiplistSSet O(logn)EO(logn)E§ 4.2
Treap O(logn)EO(logn)E§ 7.2
ScapegoatTree O(logn)O(logn)A§ 8.1
RedBlackTree O(logn)O(logn) § 9.2
BinaryTrieIO(w)O(w) § 13.1
XFastTrieIO(logw)A,EO(w)A,E§ 13.2
YFastTrieIO(logw)A,EO(logw)A,E§ 13.3
BTree O(logn)O(B+ log n)A§ 14.2
BTreeXO(logBn)O(logBn) § 14.2
(Priority) Queue implementations
findMin ()add(x)/remove ()
BinaryHeap O(1)O(logn)A§ 10.1
MeldableHeap O(1)O(logn)E§ 10.2
IThis structure can only store w-bit integer data.
XThis denotes the running time in the external-memory
model; see Chapter 14.
Table 1.2: Summary of SSet and priority Queue implementations.
24

（中文关键词：跳表、队列、替罪羊树、堆、树、优先队列）
