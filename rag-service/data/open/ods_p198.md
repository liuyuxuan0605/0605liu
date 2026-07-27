---
structure:
source: open/ods_p198.md
page: 198
---

# ODS p198: §8.2 Scapegoat Trees

§8.2 Scapegoat Trees
Your analysis should show that operations on a DynamiteTree run in
O(logn) expected time.
Exercise 8.11. Design and implement a Sequence data structure that
maintains a sequence (list) of elements. It supports these operations:
•addAfter (e): Add a new element after the element ein the se-
quence. Return the newly added element. (If eis null, the new
element is added at the beginning of the sequence.)
•remove (e): Remove efrom the sequence.
•testBefore (e1;e2): return true if and only if e1comes before e2
in the sequence.
The ﬁrst two operations should run in O(logn) amortized time. The third
operation should run in constant time.
TheSequence data structure can be implemented by storing the ele-
ments in something like a ScapegoatTree , in the same order that they oc-
cur in the sequence. To implement testBefore (e1;e2) in constant time,
each element eis labelled with an integer that encodes the path from the
root to e. In this way, testBefore (e1;e2) can be implemented by com-
paring the labels of e1ande2.
184

（中文关键词：替罪羊树、树、摊还分析、复杂度分析）
