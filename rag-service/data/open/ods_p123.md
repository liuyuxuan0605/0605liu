---
structure:
source: open/ods_p123.md
page: 123
---

# ODS p123: only constant time.

ChainedHashTable : Hashing with Chaining §5.1
any of the list implementations described in Chapters 2 or 3, this takes
only constant time.
To remove an element, x, from the hash table, we iterate over the list
t[hash (x)] until we ﬁnd xso that we can remove it:
ChainedHashTable
T remove(T x) {
Iterator<T> it = t[hash(x)].iterator();
while (it.hasNext()) {
T y = it.next();
if (y.equals(x)) {
it.remove();
n--;
return y;
}
}
return null;
}
This takesO(nhash (x)) time, where nidenotes the length of the list
stored at t[i].
Searching for the element xin a hash table is similar. We perform a
linear search on the list t[hash (x)]:
ChainedHashTable
T find(Object x) {
for (T y : t[hash(x)])
if (y.equals(x))
return y;
return null;
}
Again, this takes time proportional to the length of the list t[hash (x)].
The performance of a hash table depends critically on the choice of
the hash function. A good hash function will spread the elements evenly
among the t:length lists, so that the expected size of the list t[hash (x)] is
O(n=t:length ) =O(1). On the other hand, a bad hash function will hash
all values (including x) to the same table location, in which case the size
109

（中文关键词：哈希表、哈希）
