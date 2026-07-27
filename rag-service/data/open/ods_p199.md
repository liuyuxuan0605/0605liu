---
structure:
source: open/ods_p199.md
page: 199
---

# ODS p199: Chapter 9

Chapter 9
Red-Black Trees
In this chapter, we present red-black trees, a version of binary search trees
with logarithmic height. Red-black trees are one of the most widely used
data structures. They appear as the primary search structure in many
library implementations, including the Java Collections Framework and
several implementations of the C++ Standard Template Library. They are
also used within the Linux operating system kernel. There are several
reasons for the popularity of red-black trees:
1. A red-black tree storing nvalues has height at most 2log n.
2. The add(x) and remove (x) operations on a red-black tree run in
O(logn)worst-case time.
3. The amortized number of rotations performed during an add(x) or
remove (x) operation is constant.
The ﬁrst two of these properties already put red-black trees ahead of
skiplists, treaps, and scapegoat trees. Skiplists and treaps rely on ran-
domization and their O(logn) running times are only expected. Scapegoat
trees have a guaranteed bound on their height, but add(x) and remove (x)
only run in O(logn) amortized time. The third property is just icing on
the cake. It tells us that that the time needed to add or remove an element
xis dwarfed by the time it takes to ﬁnd x.1
However, the nice properties of red-black trees come with a price: im-
plementation complexity. Maintaining a bound of 2log non the height
1Note that skiplists and treaps also have this property in the expected sense. See Exer-
cises 4.6 and 7.5.
185

（中文关键词：跳表、二叉搜索树、红黑树、替罪羊树、树、摊还分析）
