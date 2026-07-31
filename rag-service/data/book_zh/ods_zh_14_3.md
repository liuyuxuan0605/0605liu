---
structure: BTree
source: book_zh/ods_zh_14_3.md
chapter: 14. External Memory Searching
section: 14.3
page: 318
kind: textbook
---

# 14.3 讨论与练习

## 讨论与练习 (1/7)

外部存储计算模型是由 Aggarwal 和 Vitter [4] 提出的。它有时也被称为
I/O model 或 disk access model。
B- 树对于外部存储搜索的作用，就像二叉搜索树对于内部存储搜索的
作用一样。B-树由Bayer和McCreight [9] 在1970年提出，不到十年后，Co
mer在ACM Computing Surveys的文章标题就将它们称为无处不在的 [15]。
像二叉搜索树一样，B-树也有许多变体，包括 B+-树、B -树 和计数 B-
∗
树。B-树确实无处不在，是许多文件系统的主要数据结构，包括苹果的 H
FS+、微软的 NTFS 以及 Linux 的 Ext4；每个主要的数据库系统；以及用
于云计算的键值存储。Graefe 最近的综述 [36] 提供了关于 B-树的众多现
代应用、变体和优化的 200+ 页概述。
B-树实现了 SSet 接口。如果只需要 USet 接口，那么可以使用外存哈
希作为 B-树的替代方案。确实存在外存哈希方案；例如，参见 Jensen 和 P
agh [43]。这些方案在外存模型中以 O(1) 期望时间实现 USet 操作。然而
，由于各种原因，许多应用程序仍然使用 B-树，即使它们只需要 USet 操
作。
一个原因说明为什么 B-树如此受欢迎的选择是，它们的性能常常比其
O(log n) 的运行时间界限所示的要好。其原因在于，在外部存储环境中，
B
B 的值通常相当大——可能达到数百甚至数千。这意味着 B-树中 99% 或甚
至 99.9% 的数据存储在叶节点中。在具有大内存的数据库系统中，可能将
B-树的所有内部节点缓存到 RAM 中，因为它们仅占总数据集的 1% 或 0.1
%。当这种情况发生时，这意味着在 B-树中的搜索涉及在 RAM 中对内部
节点进行非常快速的搜索，然后通过一次外部存储访问来检索一个叶节点
。
练习 14.1. 展示当将键 1.5 然后 7.5 添加到图 14.2 中的 B-树时会发生什么
。
练习 14.2。展示当从图 14.2 中的 B-树中依次移除键 3 和 4 时会发生什么
。
练习 14.3。一个存储 n 个关键字的 B- 树的内部节点最大数量是多少（作
为 n 和 B 的函数）？
练习14.4。本章的介绍声称B-树只需要大小为O(B + log n)的内部存储器
B
。然而，这里给出的实现实际上需要更多的内存。
1. 证明本章中给出的 add(x) 和 remove(x) 方法的实现使用的内部内存与
B log n 成正比。 2. 描述如何修改这些方法以将其内存消耗降低到
B
O(B + log n)。
B
练习 14.5。在图 14.6 和 14.7 的树上画出引理 14.1 证明中使用的积分。验
证（加上三个额外的积分）
有可能为拆分、合并和借用支付费用，并保持信用不变性。
练习 14.6 设计一个 B-树 的修改版本，其中节点可以有从 B 到 3B 个子节
点（因此有 B 1 到 3B 1 个键）。证明这个新的 B-树 版本在一系列 m
− −
操作中只进行 O(m/B) 次分裂、合并和借用。（提示：为了实现这一点，
你必须在合并时更加积极，有时甚至在严格必要之前就合并两个节点。）
练习 14.7。在本练习中，您将设计一种在 B-树中拆分和合并的改进方法，
通过一次考虑最多三个节点，从而在渐近意义上减少拆分、借用和合并的
次数。
1. 设 u 为一个超满节点，v 为紧邻 u 右侧的兄弟节点。有两种方法可以
修复 u 的溢出：
(a) 你可以将其中一些键给 v；或者 (b) 你可以进行分裂，u 和 v 的
键可以在 u、v 以及新创建的节点 w 之间平均分配。
证明可以总是以这样一种方式进行操作，使得在操作之后，每个（
最多 3 个）受影响的节点至少有 B + αB 个键，最多有 2B αB 个键
−
，对于某个常数 α > 0。
2. 设 u 为一个节点容量不足的节点，设 v 和 w 为 u 的兄弟节点。有两
种方法可以修复 u 的容量不足问题：
(a) 密钥可以在 u、v 和 w 之间重新分配；或者
(b) u、v 和 w 可以合并为两个节点，并且 u、v 和 w 的键可以在这
些节点之间重新分配。
证明可以总是以这样一种方式进行操作，使得在操作之后，每个（
最多 3 个）受影响的节点至少有 B + αB 个键，最多有 2B αB 个键
−
，其中 α > 是某个常数且大于 0。
3. 证明在这些修改下，在 m 次操作中发生的合并、借用和拆分的次数
是 O(m/B)。
7
2 4 10 12 14
B-tree
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 14 16 17
数字 e 14.11：一个 B+-树是在一个双向链表上方的 B-树 方块。
练习 14.8。一个 B+-树，如图 14.11 所示，将每个键存储在叶子节点中，
并将其叶子节点存储为双向链表。和往常一样，每个叶子节点存储的键数
介于 B 1 和 2B 1 之间。在这个列表之上是一个标准的 B-树，它存储每
− −
个叶子节点（除了最后一个）的最大值。
1. 描述在 B+-树中 add(x)、remove(x) 和 find(x) 的快速实现方法。 2. 解
释如何高效地实现 findRange(x, y) 方法，该方法报告所有大于 x 且小于
或等于 y 的值，在 B+-树中。 3. 实现一个类 BPlusTree，该类实现 find(
x)、add(x)、remove(x) 和 findRange(x, y)。 4. B+-树会重复存储一些键
，因为它们同时存储在 B-树和列表中。解释为什么这种重复对于大的
B 值来说并不会占用太多空间。

（中文关键词：树、B树；英文术语：BTree）

## 讨论与练习 (2/7)

参考文献
[1] 古腾堡计划免费电子书。可从以下网址获取：http://www.gutenberg.or
g/ [引用日期 2011-10-12]。
[2] IEEE 浮点运算标准。技术报告，IEEE 计算机协会微处理器标准委员
会，美国纽约州纽约市公园大道 3 号，邮编 10016-5997，2008 年 8 月。
doi:10.1109/IEEESTD.2008.4610935。
[3] G. Adelson-Velskii 和 E. Landis. 信息组织的算法。
Soviet Mathematics Doklady, 3(1259-1262):4, 1962.
[4] A. Aggarwal 和 J. S. Vitter。排序及相关问题的输入/输出复杂性。《v1
》，31(9):1116–1127，1988。
[5] A. Andersson. 通过使用简单的平衡标准改进部分重建。收录于 F. K. H
. A. Dehne、J.-R. Sack 和 N. Santoro 编者, Al-
gorithms and Data Structures, Workshop WADS ’89, Ottawa, Canada,
August 17–19, 1989, Proceedings, Lecture Notes in Computer Science 第
382 卷, 第 393–402 页. Springer, 1989.
[6] A. Andersson. 平衡搜索树简单化. 见 F. K. H. A. Dehne, J.-R. Sack, N. S
antoro, 和 S. Whitesides 编者, Algorithms
and Data Structures, Third Workshop, WADS ’93, Montre´al, Canada,
August 11–13, 1993, Proceedings, Lecture Notes in Computer Science 第
709 卷, 第 60–71 页. Springer, 1993.
[7] A. Andersson. 一般平衡树. Journal of Algorithms, 30(1):1–18, 1999.
Bibliography
[8] A. Bagchi, A. L. Buchsbaum, 和 M. T. Goodrich. 偏向跳表。收录于 P. B
ose 和 P. Morin 编辑, Algorithms and Computation, 13th Inter-
national Symposium, ISAAC 2002 Vancouver, BC, Canada, November
21–23, 2002, Proceedings, Lecture Notes in Computer Science 第 2518 卷,
页 1–13. Springer, 2002.
[9] R. Bayer 和 E. M. McCreight. 大型有序索引的组织与维护. 收录于
SIGFIDET Workshop, 页码 107–141. ACM, 1970.
[10] 关于哈希的参考文献。可从以下网址获得：http://liinwww.ira.uka.de/bi
bliography/Theory/hash.html [引用于2011-07-20]。
[11] J. Black, S. Halevi, H. Krawczyk, T. Krovetz 和 P. Rogaway。UMAC：
快速且安全的消息认证。收录于 M. J. Wiener 主编的
Advances in Cryptology - CRYPTO ’99, 19th Annual International
Cryptology Conference, Santa Barbara, California, USA, August 15–19,
1999, Proceedings，Lecture Notes in Computer Science 第 1666 卷，第 79–7
9 页。施普林格，1999 年。
[12] P. Bose, K. Dou¨(cid:0)eb 和 S. Langerman. 跳表和 B 树的动态最优性. 收录于
S.-H. Teng 主编, Proceedings of the Nineteenth
Annual ACM-SIAM Symposium on Discrete Algorithms, SODA 2008,
San Francisco, California, USA, January 20–22, 2008, 页 1106–1114. SIA
M, 2008.
[13] A. Brodnik，S. Carlsson，E. D. Demaine，J. I. Munro 和 R. Sedgewick
。可调整大小的数组在最优时间和空间内。载于 Dehne 等 [18]，第 37–48
页。
[14] J. Carter 和 M. Wegman. 哈希函数的通用类. Jour-
nal of computer and system sciences, 18(2):143–154, 1979.
[15] D. Comer. 无处不在的B树。ACM Computing Surveys, 11(2):121–137,
1979.
[16] C. Crane. 作为平衡二叉树的线性表和优先队列。技术报告 STAN-CS-7
2-259，斯坦福大学计算机科学系，1972 年。

（中文关键词：图；英文术语：BTree）

## 讨论与练习 (3/7)

Bibliography
[17] S. Crosby 和 D. Wallach. 通过算法复杂性攻击进行拒绝服务。收录于
Proceedings of the 12th USENIX Security Symposium, 第 29–44 页, 2003 年
。
[18] F. K. H. A. Dehne、A. Gupta、J.-R. Sack 和 R. Tamassia，编辑。《
Algorithms and Data Structures, 6th International Workshop, WADS
’99, Vancouver, British Columbia, Canada, August 11–14, 1999, Pro-
ceedings》，Lecture Notes in Computer Science 第1663卷。斯普林格出版社
，1999年。
[19] L. Devroye. 记录理论在随机树研究中的应用。Acta Informatica, 26(1):
123–130, 1988.
[20] P. Dietz 和 J. Zhang。单调列表标注的下界。载于 J. R. Gilbert 和 R. G.
Karlsson 编辑，SWAT 90, 2nd Scandi-
navian Workshop on Algorithm Theory, Bergen, Norway, July 11–14,
1990, Proceedings，第 447 卷 Lecture Notes in Computer Science，第 173–
180 页。Springer，1990 年。
[21] M. Dietzfelbinger. 通过整数运算而非质数实现的通用哈希和 k-次独立
随机变量。收录于 C. Puech 和 R. Reischuk 编辑的
STACS 96, 13th Annual Symposium on The-
oretical Aspects of Computer Science, Grenoble, France, February 22–24,
1996, Proceedings，第 1046 卷的 Lecture Notes in Computer Science，页 56
7–580。施普林格，1996 年。
[22] M. Dietzfelbinger, J. Gil, Y. Matias, 和 N. Pippenger. 多项式哈希函数是
可靠的。在 W. Kuich 编辑, Automata, Languages
and Programming, 19th International Colloquium, ICALP92, Vienna,
Austria, July 13–17, 1992, Proceedings, Lecture Notes in Computer Science
第 623 卷, 页 235–246. Springer, 1992.
[23] M. Dietzfelbinger, T. Hagerup, J. Katajainen, 和 M. Penttonen. 一个针对
最近点对问题的可靠随机算法。Journal of Algorithms, 25(1):19–51, 1997.
[24] M. Dietzfelbinger, A. R. Karlin, K. Mehlhorn, F. M. auf der Heide, H. Roh
nert, 和 R. E. Tarjan. 动态完美哈希：上界与下界。SIAM J. Comput., 23(4):
738–761, 1994.

（中文关键词：图；英文术语：BTree）

## 讨论与练习 (4/7)

Bibliography
[25] A. Elmasry. 配对堆的下降操作成本为 O(log log n)。载于 Pro-
ceedings of the twentieth Annual ACM-SIAM Symposium on Discrete
Algorithms, 页 471–476。工业与应用数学学会, 2009.
[26] F. Ergun, S. C. Sahinalp, J. Sharp, 和 R. Sinha. 带有快速插入/删除的偏
置字典. 载于 Proceedings of the thirty-third annual ACM
symposium on Theory of computing, 第483–491页, 纽约, 纽约州, 美国, 200
1. ACM.
[27] M. Eytzinger. Thesaurus principum hac aetate in Europa viventium
(Cologne). 1590年。在评论中，“Eytzinger”可能以不同形式出现，包括
：Aitsingeri、Aitsingero、Aitsingerum、Eyzingern。
[28] R. W. Floyd. 算法 245: 树排序 3. Communications of the ACM, 7(12):70
1, 1964.
[29] M. Fredman, R. Sedgewick, D. Sleator 和 R. Tarjan。配对堆：一种新的
自调整堆形式。Algorithmica, 1(1):111–129, 1986.
[30] M. Fredman 和 R. Tarjan. 斐波那契堆及其在改进网络优化算法中的应
用。Journal of the ACM, 34(3):596–615, 1987.
[31] M. L. Fredman, J. Koml ´os, 和 E. Szemer´edi. 用 0 (1) 最坏情况访问时间
存储稀疏表。Journal of the ACM, 31(3):538–544, 1984。
[32] M. L. Fredman 和 D. E. Willard。利用融合树超越信息论界限。
Journal of computer and system sciences, 47(3):424–436, 1993。
[33] I. Galperin 和 R. Rivest. 替罪羊树. 收录于 Proceedings of the
fourth annual ACM-SIAM Symposium on Discrete algorithms, 第165–174
页. 工业与应用数学学会, 1993年.
[34] A. Gambin 和 A. Malinowski。可随机合并的优先队列。收录于
SOFSEM98: Theory and Practice of Informatics，第 344–349 页。施普林格
，1998 年。
Bibliography
[35] M. T. Goodrich 和 J. G. Kloss。《分层向量：基于秩的序列的高效动态
数组》。载于 Dehne 等 [18]，第 205–216 页。
[36] G. Graefe. 现代 B 树技术. Foundations and Trends in Databases, 3(4):2
03–402, 2010.
[37] R. L. Graham, D. E. Knuth, 和 O. Patashnik. Concrete Mathematics. 艾迪
生-韦斯利出版社，第2版，1994年。
[38] L. Guibas 和 R. Sedgewick. 一种平衡树的二色框架。收录于
19th Annual Symposium on Foundations of Computer Science,
Ann Arbor, Michigan, 16–18 October 1978, Proceedings, 第 8–21 页。IEE
E 计算机学会, 1978 年。
[39] C. A. R. Hoare. 算法64：快速排序。Communications of the ACM, 4(7):
321, 1961。
[40] J. E. Hopcroft 和 R. E. Tarjan. 算法 447：图操作的高效算法.
Communications of the ACM, 16(6):372–378, 1973.
[41] J. E. Hopcroft 和 R. E. Tarjan. 高效平面性测试. Journal of the ACM, 21(
4):549–568, 1974.
[42] HP-UX 进程管理白皮书，版本 1.3，1997 年。可从以下网址获取：htt
p://h21007.www2.hp.com/portal/download/files/prot/files/STK/pdfs/proc_mgt.p
df [引用于 2011-07-20]。
[43] M. S. Jensen 和 R. Pagh。《外存哈希的最优性》。Algorithmica, 52(3):
403–411, 2008。
[44] P. Kirschenhofer, C. Martinez, 和 H. Prodinger. 对跳表的优化搜索算法
的分析。Theoretical Computer Science, 144:199–220, 1995.
[45] P. Kirschenhofer 和 H. Prodinger。随机跳表的路径长度。

（中文关键词：图；英文术语：BTree）

## 讨论与练习 (5/7)

Acta Informatica, 31:775–792, 1994。
[46] D. Knuth. Fundamental Algorithms，The Art of Computer
Programming 第1卷。Addison-Wesley，第3版，1997年。
Bibliography
[47] D. Knuth. Seminumerical Algorithms，The Art of Com-
puter Programming 第二卷。Addison-Wesley，第三版，1997年。
[48] D. Knuth. Sorting and Searching，The Art of Computer Programming
第3卷。Addison-Wesley，第2版，1997年。
[49] C. Y. Lee. 一种路径连接算法及其应用。
IRE Transaction on Electronic Computers, EC-10(3):346–365, 1961年。
[50] E. Lehman, F. T. Leighton, 和 A. R. Meyer. Mathematics for Com-
puter Science. 2011. 可从以下网址获取: http://courses.csail.mit.edu/6.042/spri
ng12/mcs.pdf [引用于 2012-09-06].
[51] C. Mart´(cid:0)nez 和 S. Roura. 随机二叉搜索树. Journal of the ACM, 45(2):28
8–323, 1998.
[52] E. F. Moore. 穿过迷宫的最短路径。发表于 Proceedings of the
International Symposium on the Theory of Switching, 页码 285–292, 1959.
[53] J. I. Munro, T. Papadakis 和 R. Sedgewick. 确定性跳跃表. 收录于
Proceedings of the third annual ACM-SIAM symposium on Discrete
algorithms (SODA’92), 第 367–375 页, 美国宾夕法尼亚州费城, 1992. 工业
与应用数学学会.
[54] Oracle. The Collections Framework. 可从以下网址获得：http:// downlo
ad.oracle.com/javase/1.5.0/docs/guide/collections/ [引用于 2011-07-19]。
[55] 甲骨文公司. Java Platform Standard Ed. 6. 可从以下网址获取: http://
download.oracle.com/javase/6/docs/api/ [引用于 2011-07-19].
[56] Oracle. The Java Tutorials. 可从以下网址获取：http://download.oracle.
com/javase/tutorial/ [引用于2011-07-19]。
[57] R. Pagh 和 F. Rodler. 布谷鸟哈希。Journal of Algorithms, 51(2):122–1
44, 2004.
[58] T. Papadakis, J. I. Munro, 和 P. V. Poblete. 跳表的平均搜索和更新成本
。BIT, 32:316–332, 1992.
Bibliography
[59] M. Pˇatras¸cu 和 M. Thorup。随机化对搜索前驱无帮助。在 N. Bansal, K.
Pruhs 和 C. Stein 编辑，Pro-
ceedings of the Eighteenth Annual ACM-SIAM Symposium on Discrete
Algorithms, SODA 2007, New Orleans, Louisiana, USA, January 7–9,
2007，第 555–564 页。SIAM, 2007。
[60] M. Pˇatras¸cu 和 M. Thorup。简单列举哈希的威力。Journal of the ACM,
59(3):14, 2012.
[61] W. Pugh. 跳表手册。技术报告，马里兰大学计算机科学系高级计算机
研究所，1989年。可从以下网址获取：ftp://ftp.cs.umd.edu/pub/skipLists/coo
kbook.pdf [引用于2011-07-20]。
[62] W. Pugh. 跳表：平衡树的一种概率替代方案。

（中文关键词：图、跳表、排序；英文术语：BTree）

## 讨论与练习 (6/7)

Communications of the ACM, 33(6):668–676, 1990.
[63] Redis. 可从以下网址获取：http://redis.io/ [引用于2011-07-20]。
[64] B. Reed. 随机二叉搜索树的高度。Journal of the ACM, 50(3):306–332,
2003.
[65] S. M. Ross. Probability Models for Computer Science. 学术出版社公司,
美国佛罗里达州奥兰多市, 2001年.
[66] R. Sedgewick. 左倾红黑树，2008年9月。可从以下网址获得：http://w
ww.cs.princeton.edu/˜rs/talks/LLRB/LLRB.pdf [引用于2011-07-21]。
[67] R. Seidel 和 C. Aragon。随机搜索树。Algorithmica, 16(4):464–497, 199
6.
[68] H. H. Seward。《信息排序在电子数字计算机应用于商业运营中的应
用》。硕士论文，麻省理工学院，数字计算机实验室，1954年。
[69] Z. 邵, J. H. Reppy, 和 A. W. Appel. 列表展开. 收录于 Proceed-
ings of the 1994 ACM conference LISP and Functional Programming
(LFP’94), 第185–195页, 纽约, 1994. ACM.
Bibliography
[70] P. Sinha. 一种节省内存的双向链表。Linux Journal, 129, 2005. 可从以
下网址获取: http://www.linuxjournal.com/article/6828 [引用于 2013-06-05].
[71] SkipDB。可从以下网址获得：http://dekorte.com/projects/opensource/Sk
ipDB/ [引用于2011-07-20]。
[72] D. Sleator 和 R. Tarjan。自调整二叉树。发表于 Proceedings
of the 15th Annual ACM Symposium on Theory of Computing, 25–27
April, 1983, Boston, Massachusetts, USA，第 235–245 页。ACM，ACM，1
983 年。
[73] S. P. Thompson. Calculus Made Easy. 麦克米伦，多伦多，1914年。古
腾堡计划电子书 33283。可从以下网址获取：http://www.gutenberg.org/ebo
oks/33283 [引用于2012-06-14]。
[74] P. van Emde Boas. 在小于对数时间和线性空间中保持森林的顺序。
Inf. Process. Lett., 6(3):80–82, 1977.
[75] J. Vuillemin. 用于操作优先队列的数据结构。
Communications of the ACM, 21(4):309–315, 1978.
[76] J. Vuillemin. 数据结构的统一视角。Communications of the ACM, 23(4)
:229–239, 1980.
[77] D. E. Willard. 对数-对数最坏情况范围查询在空间 Θ(N ) 中是可能的。
Inf. Process. Lett., 17(2):81–84, 1983.
[78] J. Williams. 算法232：堆排序。Communications of the ACM, 7(6):347–
348, 1964.

（中文关键词：概率、图；英文术语：BTree）

## 讨论与练习 (7/7)

索引
9-1-1, 2 二分查找, 272, 289 二叉搜索树,
140 高度平衡, 206 部分重建, 173
抽象数据类型，see 接口 邻接表，2 随机, 154 随机化, 169 红黑, 185
52 邻接矩阵，249 算法复杂度 攻击 大小平衡, 148 与跳表比较, 105
，132 摊销成本，21 摊销运行时间 二叉搜索树性质, 140 二叉树, 13
，20 祖先，133 循环数组，38 Arra 3 完全, 215 堆有序, 212 查找, 14
yDeque，40 ArrayQueue，36 数组 0 二叉树遍历, 136 二叉堆, 211
，29 ArrayStack，30 渐近符号，12 二叉搜索树, 140 二叉树类, 135
AVL 树，206 B ∗ -树，304 B+-树，30 二叉字典树, 266 二项式系数, 12
4 B-树，286 支撑数组，29 Bag，28 二项堆, 222 黑色节点, 190 黑高
BDeque，71 哈希书目，128 大 O 符 度性质, 190 块, 283, 284 块存储,
号，12 二叉堆，211 二进制对数，1 285 块存储类, 285 借用, 298 有
0 界双端队列, 71
索引
BPlusTree，307 广度优先遍 循环检测，260
历，139 广度优先搜索，25
6 DaryHeap, 223 decreaseKe
y(u, y), 222 度, 254 依赖,
名人，see 通用接收器 链式哈 22 深度, 133 深度优先搜
希表，107 链接，107 子节点， 索, 258 双端队列, 6 有界,
133 左，133 右，133 循环数组 71 子孙, 133 字典, 8 有向
，38 掷硬币，17, 98 冲突解决 边, 247 有向图, 247 磁盘
，128 颜色，190 比较器，226 c 访问模型, 304 分治法, 22
ompare(a, b)，226 compare(x, y) 6 DLList, 67 双向链表, 67
，9 比较树，236 基于比较的排 DualArrayDeque, 43 虚节
序，226 完全二叉树，215 复杂 点, 67 Dyck 字, 28 Dynam
度 空间，20 时间，20 冲突图 iteTree, 183
，247 连通分量，263 连通图，
263 联系人列表，1 conted B-树
，304 正确性，20 倒计时树，1
83 计数排序，239 信用不变量
，302 信用方案，179, 302 Cubi
sh数组栈，61 杜鹃哈希，129
循环，247
e (欧拉常数), 10 边, 247 紧急服
务, 2 欧拉常数, 10 预期成本, 21
预期运行时间, 17, 20 期望值, 1
7 指数, 10 Ext4, 304 外部内存,
283 外部内存哈希, 305 外部内
存模型, 284 外部存储, 283
Index
艾茨inger的方法，211 乘法的, 110, 129 乘加, 129
制表, 169 通用的, 129 链式哈希,
阶乘, 11 家谱, 147 快速数组栈,
107, 128 堆, 211 二进制, 211 二项
35 斐波那契堆, 222 先进先出队
堆, 222 斐波那契堆, 222 左偏堆,
列, 5 文件系统, 1 手指, 103, 171
222 配对堆, 222 斜堆, 222 堆序, 2
跳表中的手指搜索, 103 树堆中
12 堆属性, 159 堆序二叉树, 212
的手指搜索, 171 融合树, 281 一
堆排序, 233 树的高度, 133 跳表
般平衡树, 181 Git, xiv 谷歌, 3 图
的高度, 87 树的高度, 133 高度平
, 247 连通, 263 强连通, 263 H (
k 衡, 206 HFS+, 304
调和数), 154 硬盘, 283 调和数, 1
54 哈希码, 107, 122 数组用, 125
复合对象用, 123 原始数据用, 12
3 字符串用, 125 哈希函数 完美
哈希, 128 哈希表, 107 杜鹃哈希,
129 两级哈希, 129 哈希值, 107 h
ash(x), 107 哈希
输入/输出模型, 304 顺序号, 14
8 顺序遍历, 148 原地算法, 243
关联矩阵, 262 指示随机变量, 1
7 接口, 4
Java集合框架，26 Java运行时环
境，60
叶子，133 左子
节点，133 左旋
转，161
Index
左倾属性, 194 左倾红黑树, 194 NTFS，304 顺序编号，148 后
左翼堆, 222 后进先出队列, 5, 序，148 先序，148 O 表示法，
see also 栈 线性探测, 114 线性 12 开放寻址，114，128 开源，
哈希表, 114 期望的线性性, 17 xiii 有序树，133 对，8 配对堆
链表, 63 双向, 67 单向, 63 节省 ，222 回文，83 父节点，133
空间, 71 展开, see also SEList 列 部分重建，173 路径，247 族谱
表, 6 对数, 10 二进制, 10 自然对 家谱图，147，222 完美哈希函
数, 10 下界, 235 数，128 完美哈希，128 排列，
11 随机，154 枢轴元素，230
平面性测试，262 后序编号，1
48 后序遍历，148 势能，48 势
能法，48，80，205 先序编号
，148 先序遍历，148 质数域，
126 优先队列，5，see also 堆
概率，15
映射, 8 匹配字符串, 28 可合并堆,
217 memcpy(d, s, n), 36 内存管理
器, 60 合并, 187, 299 归并排序, 8
4, 226 最小化独立性, 169 MinDeq
ue, 85 MinQueue, 85 MinStack, 85
模运算, 37 乘法散列, 110, 129 乘
加散列, 129
n，22 队列FIFO, 5
自然对数，10 无红边属性 后进先出LI
，190 FO, 5
索引
优先级， SEList, 71 哨兵节点, 88 序列, 184
5 快速排序，2
共享, xiii 简单路径/循环, 247 单链
30
表, 63 大小平衡, 148 偏斜堆, 222
基数排序, 241 随机存取存储器, 18 跳表, 87 与二叉搜索树, 105 Skiplist
随机二叉搜索树, 154 随机排列, 154 List, 93 SkiplistSSet, 90 SLList, 63
随机化, 15 随机化算法, 15 随机化二 社交网络, 1 固态硬盘, 283 基于比
叉搜索树, 169 随机化数据结构, 15 较的排序算法, 226 排序下界, 235
随机队列, 60 可达顶点, 247 递归算 来源, 247 空间复杂度, 20 生成森林
法, 136 红节点, 190 红黑树, 185, 194 , 263 物种形成事件, 147 物种树, 14
红黑树类, 194 混音, xiii 右子节点, 1 7 分割, 187, 290 平方根, 56 SSet, 9
33 右旋转, 161 根树, 133 根数组栈, 稳定排序算法, 241 栈, 5 std :: copy(
49 旋转, 161 运行, 118 运行时间, 20 a0, a1, b), 36 斯特林近似, 11 分层树
摊销, 20 期望, 17, 20 最坏情况, 20 , 280 字符串匹配, 28 强连通图, 263
后继搜索, 9 System.arraycopy(s, i, d,
j, n), 36
替罪羊，173 替罪羊树，174 二
叉字典树中的搜索路径，266 二
叉搜索树中的搜索路径，140 跳
表中的搜索路径，88 二级结构
，275
Index
制表哈希, 121, 169 目标, 247 XFastTrie，272
分层向量, 59 时间复杂度, 20 XOR 列表，82
遍历 广度优先, 139 中序, 148
YFastTrie，275
二叉树的, 136 后序, 148 前序
, 148 Treap, 159 Treap列表, 17
2 树, 133 d-叉, 222 二叉, 133
有序, 133 根, 133 树遍历, 136
Treque, 60 两级哈希表, 129
下溢, 295 通用哈希, 129 通用汇点, 2
63 展开链表, see also SEList USet, 8
van Emde Boas 树，280
个顶点，247
浪费空间, 54 网络搜索, 1 权
重平衡树, 183 单词, 19 单词
RAM, 18 最坏情况运行时间,

（中文关键词：数组、双端队列、跳表、栈、队列、树堆；英文术语：BTree）
