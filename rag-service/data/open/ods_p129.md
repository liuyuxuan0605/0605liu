---
structure:
source: open/ods_p129.md
page: 129
---

# ODS p129: and

LinearHashTable : Linear Probing §5.2
1. data values: actual values in the USet that we are representing;
2.null values: at array locations where no data has ever been stored;
and
3.delvalues: at array locations where data was once stored but that
has since been deleted.
In addition to the counter, n, that keeps track of the number of elements
in the LinearHashTable , a counter, q, keeps track of the number of ele-
ments of Types 1 and 3. That is, qis equal to nplus the number of del
values in t. To make this work e ﬃciently, we need tto be considerably
larger than q, so that there are lots of null values in t. The operations on
aLinearHashTable therefore maintain the invariant that t:length2q.
To summarize, a LinearHashTable contains an array, t, that stores
data elements, and integers nand qthat keep track of the number of
data elements and non- null values of t, respectively. Because many hash
functions only work for table sizes that are a power of 2, we also keep an
integer dand maintain the invariant that t:length = 2d.
LinearHashTable
T[] t; // the table
int n; // the size
int d; // t.length = 2ˆd
int q; // number of non-null entries in t
The find (x) operation in a LinearHashTable is simple. We start at
array entry t[i] where i=hash (x) and search entries t[i],t[(i+ 1) mod
t:length ],t[(i+ 2) mod t:length ], and so on, until we ﬁnd an index i0
such that, either, t[i0] =x, ort[i0] =null . In the former case we return
t[i0]. In the latter case, we conclude that xis not contained in the hash
table and return null .
LinearHashTable
T find(T x) {
int i = hash(x);
while (t[i] != null) {
if (t[i] != del && x.equals(t[i])) return t[i];
i = (i == t.length-1) ? 0 : i + 1; // increment i
115

（中文关键词：数组、哈希）
