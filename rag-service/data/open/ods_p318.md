---
structure:
source: open/ods_p318.md
page: 318
---

# ODS p318: §14.3 External Memory Searching

§14.3 External Memory Searching
to maintain the credit invariant and pay for all borrows and merges that
occur. This completes the proof of the lemma.
The purpose of Lemma 14.1 is to show that, in the word-RAM model
the cost of splits, merges and joins during a sequence of madd(x) and
remove (x) operations is only O(Bm). That is, the amortized cost per op-
eration is only O(B), so the amortized cost of add(x) and remove (x) in the
word-RAM model is O(B+ log n). This is summarized by the following
pair of theorems:
Theorem 14.1 (External Memory B-Trees) .ABTree implements the SSet
interface. In the external memory model, a BTree supports the operations
add(x),remove (x), and find (x)inO(logBn)time per operation.
Theorem 14.2 (Word-RAM B-Trees) .ABTree implements the SSet inter-
face. In the word-RAM model, and ignoring the cost of splits, merges, and
borrows, a BTree supports the operations add(x),remove (x), and find (x)
inO(logn)time per operation. Furthermore, beginning with an empty BTree ,
any sequence of madd(x)andremove (x)operations results in a total of O(Bm)
time spent performing splits, merges, and borrows.
14.3 Discussion and Exercises
The external memory model of computation was introduced by Aggarwal
and Vitter [4]. It is sometimes also called the I/O model or the disk access
model .
B-Trees are to external memory searching what binary search trees
are to internal memory searching. B-trees were introduced by Bayer and
McCreight [9] in 1970 and, less than ten years later, the title of Comer’s
ACM Computing Surveys article referred to them as ubiquitous [15].
Like binary search trees, there are many variants of B-Trees, including
B+-trees,B-trees, and counted B-trees.B-trees are indeed ubiquitous and
are the primary data structure in many ﬁle systems, including Apple’s
HFS+, Microsoft’s NTFS, and Linux’s Ext4; every major database system;
and key-value stores used in cloud computing. Graefe’s recent survey
[36] provides a 200+ page overview of the many modern applications,
variants, and optimizations of B-trees.
304

（中文关键词：二叉搜索树、B树、树、摊还分析）
