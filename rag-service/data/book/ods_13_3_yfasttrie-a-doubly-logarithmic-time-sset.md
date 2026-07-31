---
structure: 
source: book/ods_13_3_yfasttrie-a-doubly-logarithmic-time-sset.md
chapter: 13. Data Structures for Integers
section: 13.3
page: 289
kind: textbook
---

# 13.3 YFastTrie: A Doubly-Logarithmic Time SSet

## YFastTrie: A Doubly-Logarithmic Time SSet (1/4)

The XFastTrie is a vast—even exponential—improvement over the Bi-
naryTrie in terms of query time, but the add(x) and remove(x) operations
are still not terribly fast. Furthermore, the space usage, O(n w), is higher
·
than the other SSet implementations described in this book, which all
use O(n) space. These two problems are related; if n add(x) operations
build a structure of size n w, then the add(x) operation requires at least
·
on the order of w time (and space) per operation.
The YFastTrie, discussed next, simultaneously improves the space
and speed of XFastTries. A YFastTrie uses an XFastTrie, xft, but only
stores O(n/w) values in xft. In this way, the total space used by xft is only
O(n). Furthermore, only one out of every w add(x) or remove(x) operations
in the YFastTrie results in an add(x) or remove(x) operation in xft. By
doing this, the average cost incurred by calls to xft’s add(x) and remove(x)
operations is only constant.
The obvious question becomes: If xft only stores n/w elements, where
do the remaining n(1 1/w) elements go? These elements move into sec-
−
ondary structures, in this case an extended version of treaps (Section 7.2).
There are roughly n/w of these secondary structures so, on average, each
of them stores O(w) items. Treaps support logarithmic time SSet opera-
tions, so the operations on these treaps will run in O(log w) time, as re-
quired.
More concretely, a YFastTrie contains an XFastTrie, xft, that con-
tains a random sample of the data, where each element appears in the
sample independently with probability 1/w. For convenience, the value
2w 1, is always contained in xft. Let x < x < < x denote the
0 1 k 1
− · · · −
elements stored in xft. Associated with each element, x , is a treap, t ,
i i
that stores all values in the range x + 1, . . . , x . This is illustrated in
i 1 i
−
Figure 13.7.
The find(x) operation in a YFastTrie is fairly easy. We search for x in
xft and find some value x associated with the treap t . We then use the
i i
treap find(x) method on t to answer the query. The entire method is a
i
one-liner:
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0, 1, 3 4, 5, 8, 9 10, 11, 13
Figure 13.7: A YFastTrie containing the values 0, 1, 3, 4, 6, 8, 9, 10, 11, and 13.

（中文关键词：字典树、树堆、概率）

## YFastTrie: A Doubly-Logarithmic Time SSet (2/4)

YFastTrie
T find(T x) {
return xft.find(new Pair<T>(it.intValue(x))).t.find(x);
}
The first find(x) operation (on xft) takes O(log w) time. The second
find(x) operation (on a treap) takes O(log r) time, where r is the size of
the treap. Later in this section, we will show that the expected size of the
treap is O(w) so that this operation takes O(log w) time.1
Adding an element to a YFastTrie is also fairly simple—most of the
time. The add(x) method calls xft.find(x) to locate the treap, t, into
which x should be inserted. It then calls t.add(x) to add x to t. At this
point, it tosses a biased coin that comes up as heads with probability 1/w
and as tails with probability 1 1/w. If this coin comes up heads, then x
−
will be added to xft.
This is where things get a little more complicated. When x is added
to xft, the treap t needs to be split into two treaps, t1 and t . The treap
(cid:48)
t1 contains all the values less than or equal to x; t is the original treap,
(cid:48)
1This is an application of Jensen’s Inequality: If E[r] = w, then E[logr] logw.
≤
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0, 1, 2, 3 4, 5, 6 4, 5,88,,99 10, 11, 13
Figure 13.8: Adding the values 2 and 6 to a YFastTrie. The coin toss for 6 came
up heads, so 6 was added to xft and the treap containing 4,5,6,8,9 was split.
t, with the elements of t1 removed. Once this is done, we add the pair
(x, t1) to xft. Figure 13.8 shows an example.
YFastTrie
boolean add(T x) {
int ix = it.intValue(x);
STreap<T> t = xft.find(new Pair<T>(ix)).t;
if (t.add(x)) {
n++;
if (rand.nextInt(w) == 0) {
STreap<T> t1 = t.split(x);
xft.add(new Pair<T>(ix, t1));
}
return true;
}
return false;
}
Adding x to t takes O(log w) time. Exercise 7.12 shows that splitting
t into t1 and t can also be done in O(log w) expected time. Adding the
(cid:48)
pair (x,t1) to xft takes O(w) time, but only happens with probability 1/w.
Therefore, the expected running time of the add(x) operation is
1
O(log w) + O(w) = O(log w) .
w
The remove(x) method undoes the work performed by add(x). We use
xft to find the leaf, u, in xft that contains the answer to xft.find(x).
From u, we get the treap, t, containing x and remove x from t. If x was
also stored in xft (and x is not equal to 2w 1) then we remove x from xft
−
and add the elements from x’s treap to the treap, t2, that is stored by u’s
successor in the linked list. This is illustrated in Figure 13.9.

（中文关键词：树堆、字典树、概率、链表）

## YFastTrie: A Doubly-Logarithmic Time SSet (3/4)

YFastTrie
boolean remove(T x) {
int ix = it.intValue(x);
Node<T> u = xft.findNode(ix);
boolean ret = u.x.t.remove(x);
if (ret) n--;
if (u.x.x == ix && ix != 0xffffffff) {
STreap<T> t2 = u.child[1].x.t;
t2.absorb(u.x.t);
xft.remove(u.x);
}
return ret;
}
Finding the node u in xft takes O(log w) expected time. Removing
x from t takes O(log w) expected time. Again, Exercise 7.12 shows that
merging all the elements of t into t2 can be done in O(log w) time. If
necessary, removing x from xft takes O(w) time, but x is only contained
in xft with probability 1/w. Therefore, the expected time to remove an
element from a YFastTrie is O(log w).
Earlier in the discussion, we delayed arguing about the sizes of treaps
in this structure until later. Before finishing this chapter, we prove the
result we need.
Lemma 13.1. Let x be an integer stored in a YFastTrie and let n denote the
x
number of elements in the treap, t, that contains x. Then E[n ] 2w 1.
x
≤ −
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0,1,2,3 4, 5, 6 8, 9 8, 10, 11, 13
Figure 13.9: Removing the values 1 and 9 from a YFastTrie in Figure 13.8.

（中文关键词：字典树、树堆、概率）

## YFastTrie: A Doubly-Logarithmic Time SSet (4/4)

Proof. Refer to Figure 13.10. Let x < x < < x = x < x < < x
1 2 i i+1 n
· · · · · ·
denote the elements stored in the YFastTrie. The treap t contains some
elements greater than or equal to x. These are x , x , . . . , x , where
i i+1 i+j 1
−
x is the only one of these elements in which the biased coin toss per-
i+j 1
−
formed in the add(x) method turned up as heads. In other words, E[j] is
equal to the expected number of biased coin tosses required to obtain the
first heads.2 Each coin toss is independent and turns up as heads with
probability 1/w, so E[j] w. (See Lemma 4.2 for an analysis of this for the
≤
case w = 2.)
Similarly, the elements of t smaller than x are x , . . . , x where all
i 1 i k
− −
these k coin tosses turn up as tails and the coin toss for x turns up as
i k 1
− −
heads. Therefore, E[k] w 1, since this is the same coin tossing exper-
≤ −
iment considered in the preceding paragraph, but one in which the last
toss is not counted. In summary, n = j + k, so
x
E[n ] = E[j + k] = E[j] + E[k] 2w 1 .
x
≤ −
2This analysis ignores the fact that j never exceeds n i +1. However, this only decreases
−
E[j], so the upper bound still holds.
elements in treap, t, containing x
H T T ... T T T T T ... T H
x i
−
k
−
1 xz i
−
k x i
−
k + 1 . . . x i
−
2 x i
−
1 x i }=| x x i + 1 x i + 2 . . . x i + j
−
2 x i + j {
−
1
k j
| {z } | {z }
Figure 13.10: The number of elements in the treap t containing x is determined
by two coin tossing experiments.
Lemma 13.1 was the last piece in the proof of the following theorem,
which summarizes the performance of the YFastTrie:
Theorem 13.3. A YFastTrie implements the SSet interface for w-bit inte-
gers. A YFastTrie supports the operations add(x), remove(x), and find(x)
in O(log w) expected time per operation. The space used by a YFastTrie that
stores n values is O(n + w).
The w term in the space requirement comes from the fact that xft al-
ways stores the value 2w 1. The implementation could be modified (at
−
the expense of adding some extra cases to the code) so that it is unneces-
sary to store this value. In this case, the space requirement in the theorem
becomes O(n).

（中文关键词：字典树、树堆、概率、图）
