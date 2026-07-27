---
structure:
source: open/ods_p192.md
page: 192
---

# ODS p192: §8.1 Scapegoat Trees

§8.1 Scapegoat Trees
8.1.1 Analysis of Correctness and Running-Time
In this section, we analyze the correctness and amortized running time of
operations on a ScapegoatTree . We ﬁrst prove the correctness by show-
ing that, when the add(x) operation results in a node that violates Condi-
tion (8.1), then we can always ﬁnd a scapegoat:
Lemma 8.1. Letube a node of depth h>log3=2qin aScapegoatTree . Then
there exists a node won the path from uto the root such that
size (w)
size (parent (w))>2=3:
Proof. Suppose, for the sake of contradiction, that this is not the case, and
size (w)
size (parent (w))2=3:
for all nodes won the path from uto the root. Denote the path from the
root to uasr=u0;:::;uh=u. Then, we have size (u0) =n,size (u1)2
3n,
size (u2)4
9nand, more generally,
size (ui)2
3i
n:
But this gives a contradiction, since size (u)1, hence
1size (u)2
3h
n<2
3log3=2q
n2
3log3=2n
n=1
n
n= 1:
Next, we analyze the parts of the running time that are not yet ac-
counted for. There are two parts: The cost of calls to size (u) when search-
ing for scapegoat nodes, and the cost of calls to rebuild (w) when we ﬁnd
a scapegoat w. The cost of calls to size (u) can be related to the cost of
calls to rebuild (w), as follows:
Lemma 8.2. During a call to add(x)in aScapegoatTree , the cost of ﬁnding
the scapegoat wand rebuilding the subtree rooted at wisO(size (w)).
Proof. The cost of rebuilding the scapegoat node w, once we ﬁnd it, is
O(size (w)). When searching for the scapegoat node, we call size (u) on a
178

（中文关键词：替罪羊树、树、摊还分析、复杂度分析）
