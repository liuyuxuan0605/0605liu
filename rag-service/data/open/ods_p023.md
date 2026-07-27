---
structure:
source: open/ods_p023.md
page: 23
---

# ODS p23: Mathematical Background §1.3

Mathematical Background §1.3
1.2.4 The SSet Interface: Sorted Sets
The SSet interface represents a sorted set of elements. An SSet stores
elements from some total order, so that any two elements xand ycan
be compared. In code examples, this will be done with a method called
compare (x;y) in which
compare (x;y)8>>>><>>>>:<0 if x<y
>0 if x>y
= 0 if x=y
AnSSet supports the size (),add(x), and remove (x) methods with exactly
the same semantics as in the USet interface. The di ﬀerence between a
USet and an SSet is in the find (x) method:
4.find (x): locate xin the sorted set;
Find the smallest element yin the set such that yx. Return yor
null if no such element exists.
This version of the find (x) operation is sometimes referred to as a
successor search . It diﬀers in a fundamental way from USet:find (x) since
it returns a meaningful result even when there is no element equal to x
in the set.
The distinction between the USet andSSet find (x) operations is very
important and often missed. The extra functionality provided by an SSet
usually comes with a price that includes both a larger running time and a
higher implementation complexity. For example, most of the SSet imple-
mentations discussed in this book all have find (x) operations with run-
ning times that are logarithmic in the size of the set. On the other hand,
the implementation of a USet as a ChainedHashTable in Chapter 5 has
afind (x) operation that runs in constant expected time. When choosing
which of these structures to use, one should always use a USet unless the
extra functionality o ﬀered by an SSet is truly needed.
1.3 Mathematical Background
In this section, we review some mathematical notations and tools used
throughout this book, including logarithms, big-Oh notation, and proba-
9

（中文关键词：哈希、排序）
