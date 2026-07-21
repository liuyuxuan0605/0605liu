---
structure:
source: open/ods_p200.md
page: 200
---

# ODS p200: §9.1 Red-Black Trees

§9.1 Red-Black Trees
Figure 9.1: A 2-4 tree of height 3.
is not easy. It requires a careful analysis of a number of cases. We must
ensure that the implementation does exactly the right thing in each case.
One misplaced rotation or change of colour produces a bug that can be
very di ﬃcult to understand and track down.
Rather than jumping directly into the implementation of red-black
trees, we will ﬁrst provide some background on a related data structure:
2-4 trees. This will give some insight into how red-black trees were dis-
covered and why e ﬃciently maintaining them is even possible.
9.1 2-4 Trees
A 2-4 tree is a rooted tree with the following properties:
Property 9.1 (height) .All leaves have the same depth.
Property 9.2 (degree) .Every internal node has 2, 3, or 4 children.
An example of a 2-4 tree is shown in Figure 9.1. The properties of 2-4
trees imply that their height is logarithmic in the number of leaves:
Lemma 9.1. A 2-4 tree with nleaves has height at most logn.
Proof. The lower-bound of 2 on the number of children of an internal
node implies that, if the height of a 2-4 tree is h, then it has at least 2h
leaves. In other words,
n2h:
Taking logarithms on both sides of this inequality gives hlogn.
186

（中文关键词：红黑树、2-4树、树、复杂度分析）
