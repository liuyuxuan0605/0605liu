---
structure: 
source: book_zh/ods_zh_13_4.md
chapter: 13.1 二进制字典树：一种数字搜索树
section: 13.4
page: 294
kind: textbook
---

# 13.4 讨论与练习

第一个提供 O(log w) 时间的 add(x)、remove(x) 和 find(x) 操作的数据结构
是由 van Emde Boas 提出的，并且自此被称为 van Emde Boas ( 或
stratified) tree [74]。原始的 van Emde Boas 结构大小为 2w，使其对于大整
数来说不切实际。
XFastTrie 和 YFastTrie 数据结构是由 Willard [77] 发现的。XFastTrie 结
构与 van Emde Boas 树密切相关；例如，XFastTrie 中的哈希表取代了 van
Emde Boas 树中的数组。也就是说，van Emde Boas 树不是存储哈希表 t[i]
，而是存储长度为 2i 的数组。
又一个 用于存储整数的结构是 Fredman 和 Willard 的 f 融合
树 [32]。这种结构可以在 O(n) 空间中存储 n 个 w 位整数，从而 find(x) 操
作可以在 O((log n)/(log w)) 时间内运行。当 log w > log n 时使用融合树
，而当 log w log n 时使用 YFastTrie，可以得到一个 O(n) 空间的数据
≤ (cid:112)
结构，该结构可以在 O( log n) 时间内实现 find(x) 操作。Pˇatras¸cu 和 Thor
(cid:112)
up [59] 最近的下界结果表明，至少对于只使用 O(n) 空间的结构来说，这
(cid:112)
些结果或多或少是最优的。
练习 13.1。设计并实现一个简化版本的二叉字典树，它没有链表或跳转指
针，但可以执行 find(x)
仍然以 O(w) 时间运行。
练习 13.2。设计并实现一个简化的 XFastTrie 实现，该实现完全不使用二
叉 trie。相反，你的实现应将所有内容存储在双向链表和 w + 个哈希表中
。
练习 13.3。我们可以将二叉字典树（BinaryTrie）视为一种存储长度为 w
的位字符串的结构，其中每个位字符串表示为从根到叶子的路径。将这一
想法扩展到一个存储可变长度字符串的 SSet 实现中，并实现 add(s)、remo
ve(s) 和 find(s) 操作，其时间与 s 的长度成比例。
提示：你数据结构中的每个节点都应该存储一个按字符值索引的哈希表。
练习 13.4。对于一个整数 x {0, . . . 2w 1}，令 d(x) 表示 x 与 find(x) 返回
∈ −
的值之间的差 [如果 find(x) 返回 null，则定义 d(x) 为 2w]。例如，如果 fin
d(23) 返回 43，那么 d(23) = 为 20。
1. 设计并实现 XFastTrie 中 find(x) 操作的一个修改版本，其期望运行时
间为 O(log x)。提示：哈希表 [w] 包含所有满足 x ≥ 0 的值 x，因此从
这里开始是一个好选择。
2. 设计并实现 XFastTrie 中 find(x) 操作的修改版本，其期望运行时间为
O(1 + log log d(x))。

（中文关键词：字典树、树）
