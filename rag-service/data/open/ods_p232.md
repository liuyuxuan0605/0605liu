---
structure:
source: open/ods_p232.md
page: 232
---

# ODS p232: §10.2 Heaps

§10.2 Heaps
19179
264
551625
3228
9319
998920
19179
264
5516 508
25
3228
9319
998920merge (h1 .right ,h2)merge (h1 ,h2) h1 h2
⇓8
50
Figure 10.4: Merging h1and h2is done by merging h2with one of h1:left or
h1:right .
if (h2 == nil) return h1;
if (compare(h2.x, h1.x) < 0) return merge(h2, h1);
// now we know h1.x <= h2.x
if (rand.nextBoolean()) {
h1.left = merge(h1.left, h2);
h1.left.parent = h1;
} else {
h1.right = merge(h1.right, h2);
h1.right.parent = h1;
}
return h1;
}
In the next section, we show that merge (h1;h2) runs inO(logn) ex-
218

（中文关键词：堆）
