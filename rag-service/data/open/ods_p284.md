---
structure:
source: open/ods_p284.md
page: 284
---

# ODS p284: §13.1 Data Structures for Integers

§13.1 Data Structures for Integers
u.child[prev].child[next] = u;
u.child[next].child[prev] = u;
// 4 - walk back up, updating jump pointers
Node v = u.parent;
while (v != null) {
if ((v.child[left] == null
&& (v.jump == null || it.intValue(v.jump.x) > ix))
|| (v.child[right] == null
&& (v.jump == null || it.intValue(v.jump.x) < ix)))
v.jump = u;
v = v.parent;
}
n++;
return true;
}
This method performs one walk down the search path for xand one
walk back up. Each step of these walks takes constant time, so the add(x)
method runs in O(w) time.
The remove (x) operation undoes the work of add(x). Like add(x), it
has a lot of work to do:
1. It follows the search path for xuntil reaching the leaf, u, containing
x.
2. It removes ufrom the doubly-linked list.
3. It deletes uand then walks back up the search path for xdeleting
nodes until reaching a node vthat has a child that is not on the
search path for x.
4. It walks upwards from vto the root updating any jump pointers that
point to u.
A removal is illustrated in Figure 13.5.
BinaryTrie
boolean remove(T x) {
// 1 - find leaf, u, containing x
int i = 0, c, ix = it.intValue(x);
Node u = r;
270

（中文关键词：链表、双向链表）
