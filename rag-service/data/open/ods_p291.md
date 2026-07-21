---
structure:
source: open/ods_p291.md
page: 291
---

# ODS p291: YFastTrie : A Doubly-Logarithmic Time SSet §13.3

YFastTrie : A Doubly-Logarithmic Time SSet §13.3
01234567891011121314150⋆ ⋆ ⋆ 1⋆ ⋆ ⋆⋆ ⋆ ⋆ ⋆
00⋆⋆ 01⋆⋆ 10⋆⋆ 11⋆⋆
000⋆001⋆010⋆011⋆100⋆101⋆110⋆111⋆
0,1,2,3 4,5,8,9 10,11,13 4,5,6 8,9
Figure 13.8: Adding the values 2 and 6 to a YFastTrie . The coin toss for 6 came
up heads, so 6 was added to xftand the treap containing 4 ;5;6;8;9 was split.
t, with the elements of t1removed. Once this is done, we add the pair
(x;t1) toxft. Figure 13.8 shows an example.
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
Adding xtottakesO(logw) time. Exercise 7.12 shows that splitting
tinto t1andt0can also be done in O(logw) expected time. Adding the
277