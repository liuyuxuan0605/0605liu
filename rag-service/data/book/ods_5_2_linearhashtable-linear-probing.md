---
structure: HashMap
source: book/ods_5_2_linearhashtable-linear-probing.md
chapter: 5. Hash Tables
section: 5.2
page: 128
kind: textbook
---

# 5.2 LinearHashTable: Linear Probing

## LinearHashTable: Linear Probing (1/3)

The ChainedHashTable data structure uses an array of lists, where the
ith list stores all elements x such that hash(x) = i. An alternative, called
open addressing is to store the elements directly in an array, t, with each
array location in t storing at most one value. This approach is taken by
the LinearHashTable described in this section. In some places, this data
structure is described as open addressing with linear probing.
The main idea behind a LinearHashTable is that we would, ideally,
like to store the element x with hash value i = hash(x) in the table loca-
tion t[i]. If we cannot do this (because some element is already stored
there) then we try to store it at location t[(i + 1) mod t.length]; if that’s
not possible, then we try t[(i + 2) mod t.length], and so on, until we find
a place for x.
There are three types of entries stored in t:
1. data values: actual values in the USet that we are representing;
2. null values: at array locations where no data has ever been stored;
and
3. del values: at array locations where data was once stored but that
has since been deleted.
In addition to the counter, n, that keeps track of the number of elements
in the LinearHashTable, a counter, q, keeps track of the number of ele-
ments of Types 1 and 3. That is, q is equal to n plus the number of del
values in t. To make this work efficiently, we need t to be considerably
larger than q, so that there are lots of null values in t. The operations on
a LinearHashTable therefore maintain the invariant that t.length 2q.
≥
To summarize, a LinearHashTable contains an array, t, that stores
data elements, and integers n and q that keep track of the number of
data elements and non-null values of t, respectively. Because many hash
functions only work for table sizes that are a power of 2, we also keep an
integer d and maintain the invariant that t.length = 2d.
LinearHashTable
T[] t; // the table
int n; // the size
int d; // t.length = 2ˆd
int q; // number of non-null entries in t
The find(x) operation in a LinearHashTable is simple. We start at
array entry t[i] where i = hash(x) and search entries t[i], t[(i + 1) mod
t.length], t[(i + 2) mod t.length], and so on, until we find an index i
(cid:48)
such that, either, t[i ] = x, or t[i ] = null. In the former case we return
(cid:48) (cid:48)
t[i ]. In the latter case, we conclude that x is not contained in the hash
(cid:48)
table and return null.

（中文关键词：数组、字典树）

## LinearHashTable: Linear Probing (2/3)

LinearHashTable
T find(T x) {
int i = hash(x);
while (t[i] != null) {
if (t[i] != del && x.equals(t[i])) return t[i];
i = (i == t.length-1) ? 0 : i + 1; // increment i
}
return null;
}
The add(x) operation is also fairly easy to implement. After checking
that x is not already stored in the table (using find(x)), we search t[i],
t[(i+1) mod t.length], t[(i+2) mod t.length], and so on, until we find a
null or del and store x at that location, increment n, and q, if appropriate.
LinearHashTable
boolean add(T x) {
if (find(x) != null) return false;
if (2*(q+1) > t.length) resize(); // max 50% occupancy
int i = hash(x);
while (t[i] != null && t[i] != del)
i = (i == t.length-1) ? 0 : i + 1; // increment i
if (t[i] == null) q++;
n++;
t[i] = x;
return true;
}
By now, the implementation of the remove(x) operation should be ob-
vious. We search t[i], t[(i + 1) mod t.length], t[(i + 2) mod t.length],
and so on until we find an index i such that t[i ] = x or t[i ] = null.
(cid:48) (cid:48) (cid:48)
In the former case, we set t[i ] = del and return true. In the latter case
(cid:48)
we conclude that x was not stored in the table (and therefore cannot be
deleted) and return false.

## LinearHashTable: Linear Probing (3/3)

LinearHashTable
T remove(T x) {
int i = hash(x);
while (t[i] != null) {
T y = t[i];
if (y != del && x.equals(y)) {
t[i] = del;
n--;
if (8*n < t.length) resize(); // min 12.5% occupancy
return y;
}
i = (i == t.length-1) ? 0 : i + 1; // increment i
}
return null;
}
The correctness of the find(x), add(x), and remove(x) methods is easy
to verify, though it relies on the use of del values. Notice that none of
these operations ever sets a non-null entry to null. Therefore, when we
reach an index i such that t[i ] = null, this is a proof that the element, x,
(cid:48) (cid:48)
that we are searching for is not stored in the table; t[i ] has always been
(cid:48)
null, so there is no reason that a previous add(x) operation would have
proceeded beyond index i .
(cid:48)
The resize() method is called by add(x) when the number of non-
null entries exceeds t.length/2 or by remove(x) when the number of
data entries is less than t.length/8. The resize() method works like the
resize() methods in other array-based data structures. We find the small-
est non-negative integer d such that 2d 3n. We reallocate the array t so
≥
that it has size 2d, and then we insert all the elements in the old version
of t into the newly-resized copy of t. While doing this, we reset q equal
to n since the newly-allocated t contains no del values.
LinearHashTable
void resize() {
d = 1;
while ((1<<d) < 3*n) d++;
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
}

（中文关键词：数组、字典树）

## 5.2.1 Analysis of Linear Probing (1/4)

Notice that each operation, add(x), remove(x), or find(x), finishes as soon
as (or before) it discovers the first null entry in t. The intuition behind
the analysis of linear probing is that, since at least half the elements in t
are equal to null, an operation should not take long to complete because
it will very quickly come across a null entry. We shouldn’t rely too heav-
ily on this intuition, though, because it would lead us to (the incorrect)
conclusion that the expected number of locations in t examined by an
operation is at most 2.
For the rest of this section, we will assume that all hash values are
independently and uniformly distributed in 0, . . . , t.length 1 . This is
{ − }
not a realistic assumption, but it will make it possible for us to analyze
linear probing. Later in this section we will describe a method, called
tabulation hashing, that produces a hash function that is “good enough”
for linear probing. We will also assume that all indices into the positions
of t are taken modulo t.length, so that t[i] is really a shorthand for
t[i mod t.length].
We say that a run of length k that starts at i occurs when all the table en-
tries t[i], t[i + 1], . . . , t[i+k 1] are non-null and t[i 1] = t[i+k] = null.
− −
The number of non-null elements of t is exactly q and the add(x) method
ensures that, at all times, q t.length/2. There are q elements x , . . . , x
1 q
≤
that have been inserted into t since the last rebuild() operation. By our
assumption, each of these has a hash value, hash(x ), that is uniform and
j
independent of the rest. With this setup, we can prove the main lemma
required to analyze linear probing.
Lemma 5.4. Fix a value i 0, . . . , t.length 1 . Then the probability that a
∈ { − }
run of length k starts at i is O(ck) for some constant 0 < c < 1.

（中文关键词：概率、哈希、字典树）

## 5.2.1 Analysis of Linear Probing (2/4)

Proof. If a run of length k starts at i, then there are exactly k elements x
j
such that hash(x ) i, . . . , i + k 1 . The probability that this occurs is
j
∈ { − }
exactly
k q k
q k t.length k −
p = − ,
k k t.length t.length
(cid:32) (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
since, for each choice of k elements, these k elements must hash to one of
the k locations and the remaining q k elements must hash to the other
−
t.length k table locations.1
−
In the following derivation we will cheat a little and replace r! with
(r/e)r . Stirling’s Approximation (Section 1.3.2) shows that this is only a
factor of O(√r) from the truth. This is just done to make the derivation
simpler; Exercise 5.4 asks the reader to redo the calculation more rigor-
ously using Stirling’s Approximation in its entirety.
The value of p is maximized when t.length is minimum, and the
k
data structure maintains the invariant that t.length 2q, so
≥
k q k
q k 2q k −
p −
k ≤ k 2q 2q
(cid:32) (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
k q k
q! k 2q k −
= −
(q k)!k! 2q 2q
(cid:32) − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
qq k k 2q k q − k
− [Stirling’s approximation]
≈ (q k)q kkk 2q 2q
(cid:32) − − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
qkqq − k k k 2q k q − k
= −
(q k)q kkk 2q 2q
(cid:32) − − (cid:33) (cid:32) (cid:33) (cid:32) (cid:33)
k q k
qk q(2q k) −
= −
2qk 2q(q k)
(cid:32) (cid:33) (cid:32) − (cid:33)
1 k (2q k) q − k
= −
2 2(q k)
(cid:18) (cid:19) (cid:32) − (cid:33)
1 k k q − k
= 1 +
2 2(q k)
(cid:18) (cid:19) (cid:32) − (cid:33)
k
√e
.
≤ 2
(cid:32) (cid:33)
(In the last step, we use the inequality (1 + 1/x)x e, which holds for all
≤
x > 0.) Since √e/2 < 0.824360636 < 1, this completes the proof.

（中文关键词：概率）

## 5.2.1 Analysis of Linear Probing (3/4)

Using Lemma 5.4 to prove upper-bounds on the expected running
time of find(x), add(x), and remove(x) is now fairly straightforward. Con-
sider the simplest case, where we execute find(x) for some value x that
1Note that pk is greater than the probability that a run of length k starts at i, since the
definition of pk does not include the requirement t[i
−
1] = t[i + k] = null.
has never been stored in the LinearHashTable. In this case, i = hash(x)
is a random value in 0, . . . , t.length 1 independent of the contents of
{ − }
t. If i is part of a run of length k, then the time it takes to execute the
find(x) operation is at most O(1 + k). Thus, the expected running time
can be upper-bounded by
t.length
1 ∞
O 1 + k Pr i is part of a run of length k .
t.length { }
 
Note t
hat
e
(cid:18)
ach run of
(cid:19)
le
(cid:88)
n
i=
g
1
th
(cid:88)
k
k=
c
0
ontributes to the inner sum k time
s
for a
total contribution of k2, so the above sum can be rewritten as
t.length
O 1 + 1 ∞ k2 Pr i starts a run of length k
t.length { }
 

O 1
(cid:18)
+ 1
(cid:19) (cid:88) i
t
=
.
1
leng
(cid:88) k
t
=
h
0
∞ k2p

≤ t.length k
 
= O
1
+
(cid:18)
∞ k2p
(cid:19) (cid:88) i=1 (cid:88) k=0 
k
 
k=0
= O
1
+
(cid:88)
∞ k2 O
(ck)
·
 
k=0
= O(

1) .
(cid:88) 
The last step in this derivation comes from the fact that
∞k=0
k2
·
O(ck)
is an exponentially decreasing series.2 Therefore, we conclude that the
(cid:80)
expected running time of the find(x) operation for a value x that is not
contained in a LinearHashTable is O(1).
If we ignore the cost of the resize() operation, then the above analysis
gives us all we need to analyze the cost of operations on a LinearHash-
Table.
First of all, the analysis of find(x) given above applies to the add(x)
operation when x is not contained in the table. To analyze the find(x)
operation when x is contained in the table, we need only note that this
2In the terminology of many calculus texts, this sum passes the ratio test: There exists a
(k+1)2ck+1
positive integer k0 such that, for all k
≥
k0,
k2ck
< 1.
is the same as the cost of the add(x) operation that previously added x to
the table. Finally, the cost of a remove(x) operation is the same as the cost
of a find(x) operation.

（中文关键词：概率）

## 5.2.1 Analysis of Linear Probing (4/4)

In summary, if we ignore the cost of calls to resize(), all operations on
a LinearHashTable run in O(1) expected time. Accounting for the cost of
resize can be done using the same type of amortized analysis performed
for the ArrayStack data structure in Section 2.1.

（中文关键词：摊还分析、数组、栈）

## 5.2.2 Summary

The following theorem summarizes the performance of the LinearHash-
Table data structure:
Theorem 5.2. A LinearHashTable implements the USet interface. Ignor-
ing the cost of calls to resize(), a LinearHashTable supports the operations
add(x), remove(x), and find(x) in O(1) expected time per operation.
Furthermore, beginning with an empty LinearHashTable, any sequence
of m add(x) and remove(x) operations results in a total of O(m) time spent
during all calls to resize().

## 5.2.3 Tabulation Hashing

While analyzing the LinearHashTable structure, we made a very strong
assumption: That for any set of elements, x , . . . , x , the hash values
1 n
{ }
hash(x ), . . . , hash(x ) are independently and uniformly distributed over
1 n
the set 0, . . . , t.length 1 . One way to achieve this is to store a giant
{ − }
array, tab, of length 2w, where each entry is a random w-bit integer, inde-
pendent of all the other entries. In this way, we could implement hash(x)
by extracting a d-bit integer from tab[x.hashCode()]:
LinearHashTable
int idealHash(T x) {
return tab[x.hashCode() >>> w-d];
}
Unfortunately, storing an array of size 2w is prohibitive in terms of
memory usage. The approach used by tabulation hashing is to, instead,
treat w-bit integers as being comprised of w/r integers, each having only r
bits. In this way, tabulation hashing only needs w/r arrays each of length
2r. All the entries in these arrays are independent w-bit integers. To ob-
tain the value of hash(x) we split x.hashCode() up into w/r r-bit integers
and use these as indices into these arrays. We then combine all these
values with the bitwise exclusive-or operator to obtain hash(x). The fol-
lowing code shows how this works when w = 32 and r = 4:
LinearHashTable
int hash(T x) {
int h = x.hashCode();
return (tab[0][h&0xff]
ˆ tab[1][(h>>>8)&0xff]
ˆ tab[2][(h>>>16)&0xff]
ˆ tab[3][(h>>>24)&0xff])
>>> (w-d);
}
In this case, tab is a two-dimensional array with four columns and
232/4 = 256 rows.
One can easily verify that, for any x, hash(x) is uniformly distributed
over 0, . . . , 2d 1 . With a little work, one can even verify that any pair
{ − }
of values have independent hash values. This implies tabulation hashing
could be used in place of multiplicative hashing for the ChainedHash-
Table implementation.
However, it is not true that any set of n distinct values gives a set of n
independent hash values. Nevertheless, when tabulation hashing is used,
the bound of Theorem 5.2 still holds. References for this are provided at
the end of this chapter.

（中文关键词：哈希、数组、字典树）
