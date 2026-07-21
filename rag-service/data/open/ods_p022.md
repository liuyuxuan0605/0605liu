---
structure:
source: open/ods_p022.md
page: 22
---

# ODS p22: §1.2 Introduction

§1.2 Introduction
1.2.3 The USet Interface: Unordered Sets
TheUSet interface represents an unordered set of unique elements, which
mimics a mathematical set. AUSet contains ndistinct elements; no ele-
ment appears more than once; the elements are in no speciﬁc order. A
USet supports the following operations:
1.size (): return the number, n, of elements in the set
2.add(x): add the element xto the set if not already present;
Add xto the set provided that there is no element yin the set such
that xequals y. Return true ifxwas added to the set and false
otherwise.
3.remove (x): remove xfrom the set;
Find an element yin the set such that xequals yand remove y.
Return y, ornull if no such element exists.
4.find (x): ﬁnd xin the set if it exists;
Find an element yin the set such that yequals x. Return y, ornull
if no such element exists.
These deﬁnitions are a bit fussy about distinguishing x, the element
we are removing or ﬁnding, from y, the element we may remove or ﬁnd.
This is because xandymight actually be distinct objects that are never-
theless treated as equal.2Such a distinction is useful because it allows for
the creation of dictionaries ormaps that map keys onto values.
To create a dictionary/map, one forms compound objects called Pair s,
each of which contains a keyand a value . Two Pair s are treated as equal
if their keys are equal. If we store some pair ( k;v) in a USet and then
later call the find (x) method using the pair x= (k;null ) the result will be
y= (k;v). In other words, it is possible to recover the value, v, given only
the key, k.
2In Java, this is done by overriding the class’s equals (y) and hashCode () methods.
8

（中文关键词：哈希）
