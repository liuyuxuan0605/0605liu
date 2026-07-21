---
structure:
source: open/ods_p131.md
page: 131
---

# ODS p131: i = (i == t.length-1) ? 0 : i + 1; // increment i

LinearHashTable : Linear Probing §5.2
}
i = (i == t.length-1) ? 0 : i + 1; // increment i
}
return null;
}
The correctness of the find (x),add(x), and remove (x) methods is easy
to verify, though it relies on the use of del values. Notice that none of
these operations ever sets a non- null entry to null . Therefore, when we
reach an index i0such that t[i0] =null , this is a proof that the element, x,
that we are searching for is not stored in the table; t[i0] has always been
null , so there is no reason that a previous add(x) operation would have
proceeded beyond index i0.
The resize () method is called by add(x) when the number of non-
null entries exceeds t:length=2 or by remove (x) when the number of
data entries is less than t:length=8. The resize () method works like the
resize () methods in other array-based data structures. We ﬁnd the small-
est non-negative integer dsuch that 2d3n. We reallocate the array tso
that it has size 2d, and then we insert all the elements in the old version
oftinto the newly-resized copy of t. While doing this, we reset qequal
tonsince the newly-allocated tcontains no delvalues.
LinearHashTable
void resize() {
d = 1;
while ((1<<d) < 3 *n) d++;
T[] told = t;
t = newArray(1<<d);
q = n;
// insert everything from told
for (int k = 0; k < told.length; k++) {
if (told[k] != null && told[k] != del) {
int i = hash(told[k]);
while (t[i] != null)
i = (i == t.length-1) ? 0 : i + 1;
t[i] = told[k];
}
}
117

（中文关键词：数组、哈希）
