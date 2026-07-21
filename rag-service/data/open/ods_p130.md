---
structure:
source: open/ods_p130.md
page: 130
---

# ODS p130: return null;

§5.2 Hash Tables
}
return null;
}
Theadd(x) operation is also fairly easy to implement. After checking
that xis not already stored in the table (using find (x)), we search t[i],
t[(i+1) mod t:length ],t[(i+2) mod t:length ], and so on, until we ﬁnd a
null ordeland store xat that location, increment n, and q, if appropriate.
LinearHashTable
boolean add(T x) {
if (find(x) != null) return false;
if (2 *(q+1) > t.length) resize(); // max 50% occupancy
int i = hash(x);
while (t[i] != null && t[i] != del)
i = (i == t.length-1) ? 0 : i + 1; // increment i
if (t[i] == null) q++;
n++;
t[i] = x;
return true;
}
By now, the implementation of the remove (x) operation should be ob-
vious. We search t[i],t[(i+ 1) mod t:length ],t[(i+ 2) mod t:length ],
and so on until we ﬁnd an index i0such that t[i0] =xort[i0] =null .
In the former case, we set t[i0] =deland return true . In the latter case
we conclude that xwas not stored in the table (and therefore cannot be
deleted) and return false .
LinearHashTable
T remove(T x) {
int i = hash(x);
while (t[i] != null) {
T y = t[i];
if (y != del && x.equals(y)) {
t[i] = del;
n--;
if (8 *n < t.length) resize(); // min 12.5% occupancy
return y;
116

（中文关键词：哈希表、哈希）
