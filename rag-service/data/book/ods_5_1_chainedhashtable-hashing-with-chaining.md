---
structure: HashMap
source: book/ods_5_1_chainedhashtable-hashing-with-chaining.md
chapter: 5. Hash Tables
section: 5.1
page: 121
kind: textbook
---

# 5.1 ChainedHashTable: Hashing with Chaining

## ChainedHashTable: Hashing with Chaining (1/2)

A ChainedHashTable data structure uses hashing with chaining to store
data as an array, t, of lists. An integer, n, keeps track of the total number
of items in all lists (see Figure 5.1):
ChainedHashTable
List<T>[] t;
int n;
The hash value of a data item x, denoted hash(x) is a value in the range
t 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
b d i x h j f m ‘ k
c g e
a
Figure 5.1: An example of a ChainedHashTable with n = 14 and t.length = 16.
In this example hash(x) = 6
0, . . . , t.length 1 . All items with hash value i are stored in the list at
{ − }
t[i]. To ensure that lists don’t get too long, we maintain the invariant
n t.length
≤
so that the average number of elements stored in one of these lists is
n/t.length 1.
≤
To add an element, x, to the hash table, we first check if the length of
t needs to be increased and, if so, we grow t. With this out of the way
we hash x to get an integer, i, in the range 0, . . . , t.length 1 , and we
{ − }
append x to the list t[i]:
ChainedHashTable
boolean add(T x) {
if (find(x) != null) return false;
if (n+1 > t.length) resize();
t[hash(x)].add(x);
n++;
return true;
}
Growing the table, if necessary, involves doubling the length of t and
reinserting all elements into the new table. This strategy is exactly the
same as the one used in the implementation of ArrayStack and the same
result applies: The cost of growing is only constant when amortized over
a sequence of insertions (see Lemma 2.1 on page 33).
Besides growing, the only other work done when adding a new value
x to a ChainedHashTable involves appending x to the list t[hash(x)]. For
any of the list implementations described in Chapters 2 or 3, this takes
only constant time.
To remove an element, x, from the hash table, we iterate over the list
t[hash(x)] until we find x so that we can remove it:
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
This takes O(n ) time, where n denotes the length of the list
hash(x) i
stored at t[i].
Searching for the element x in a hash table is similar. We perform a
linear search on the list t[hash(x)]:
ChainedHashTable
T find(Object x) {
for (T y : t[hash(x)])
if (y.equals(x))
return y;
return null;
}
Again, this takes time proportional to the length of the list t[hash(x)].

（中文关键词：哈希表、哈希、数组、摊还分析、栈）

## ChainedHashTable: Hashing with Chaining (2/2)

The performance of a hash table depends critically on the choice of
the hash function. A good hash function will spread the elements evenly
among the t.length lists, so that the expected size of the list t[hash(x)] is
O(n/t.length) = O(1). On the other hand, a bad hash function will hash
all values (including x) to the same table location, in which case the size
of the list t[hash(x)] will be n. In the next section we describe a good hash
function.

（中文关键词：哈希表、哈希）

## 5.1.1 Multiplicative Hashing (1/4)

Multiplicative hashing is an efficient method of generating hash values
based on modular arithmetic (discussed in Section 2.3) and integer divi-
sion. It uses the div operator, which calculates the integral part of a quo-
tient, while discarding the remainder. Formally, for any integers a 0
≥
and b 1, a div b = a/b .
≥ (cid:98) (cid:99)
In multiplicative hashing, we use a hash table of size 2d for some in-
teger d (called the dimension). The formula for hashing an integer x
∈
0, . . . , 2w 1 is
{ − }
hash(x) = ((z x) mod 2w) div 2w − d .
·
Here, z is a randomly chosen odd integer in 1, . . . , 2w 1 . This hash func-
{ − }
tion can be realized very efficiently by observing that, by default, opera-
tions on integers are already done modulo 2w where w is the number of
bits in an integer. (See Figure 5.2.) Furthermore, integer division by 2w d
−
is equivalent to dropping the rightmost w d bits in a binary representa-
−
tion (which is implemented by shifting the bits right by w d). In this way,
−
the code that implements the above formula is simpler than the formula
itself:
ChainedHashTable
int hash(Object x) {
return (z * x.hashCode()) >>> (w-d);
}
The following lemma, whose proof is deferred until later in this sec-
tion, shows that multiplicative hashing does a good job of avoiding colli-
sions:
Lemma 5.1. Let x and y be any two values in 0, . . . , 2w 1 with x (cid:44) y. Then
{ − }
Pr hash(x) = hash(y) 2/2d.
{ } ≤
With Lemma 5.1, the performance of remove(x), and find(x) are easy
to analyze:
2w (4294967296) 100000000000000000000000000000000
z (4102541685) 11110100100001111101000101110101
x (42) 00000000000000000000000000101010
z x 10100000011110010010000101110100110010
(z · x) mod 2w 00011110010010000101110100110010
((z · x) mod 2w) div 2w d 00011110
−
·
Figure 5.2: The operation of the multiplicative hash function with w = 32 and
d = 8.

（中文关键词：哈希、哈希表）

## 5.1.1 Multiplicative Hashing (2/4)

Lemma 5.2. For any data value x, the expected length of the list t[hash(x)]
is at most n + 2, where n is the number of occurrences of x in the hash table.
x x
Proof. Let S be the (multi-)set of elements stored in the hash table that
are not equal to x. For an element y S, define the indicator variable
∈
1 if hash(x) = hash(y)
I =
y 0 otherwise
(cid:40)
and notice that, by Lemma 5.1, E[I ] 2/2d = 2/t.length. The expected
y
≤
length of the list t[hash(x)] is given by
E [t[hash(x)].size()] = E n + I
x y
 
y S
= n
x

+
(cid:88)
E
∈
[I
y
]

y S
(cid:88)∈
n + 2/t.length
x
≤
y S
(cid:88)∈
n + 2/n
x
≤
y S
(cid:88)∈
n + (n n )2/n
x x
≤ −
n + 2 ,
x
≤
as required.
Now, we want to prove Lemma 5.1, but first we need a result from
number theory. In the following proof, we use the notation (b , . . . , b )
r 0 2
to denote r b 2i, where each b is a bit, either 0 or 1. In other words,
i=0 i i
(cid:80)
(b , . . . , b ) is the integer whose binary representation is given by b , . . . , b .
r 0 2 r 0
We use (cid:63) to denote a bit of unknown value.
Lemma 5.3. Let S be the set of odd integers in 1, . . . , 2w 1 ; let q and i
{ − }
be any two elements in S. Then there is exactly one value z S such that
∈
zq mod 2w = i.
Proof. Since the number of choices for z and i is the same, it is sufficient
to prove that there is at most one value z S that satisfies zq mod 2w = i.
∈
Suppose, for the sake of contradiction, that there are two such values
z and z , with z > z . Then
(cid:48) (cid:48)
zq mod 2w = z (cid:48)q mod 2w = i
So
(z z
(cid:48)
)q mod 2w = 0
−
But this means that
(z z
(cid:48)
)q = k2w (5.1)
−
for some integer k. Thinking in terms of binary numbers, we have
(z z (cid:48) )q = k (1, 0, . . . , 0) 2 ,
− ·
w
so that the w trailing bits in the binary (cid:124)re(cid:123)p(cid:122)re(cid:125)sentation of (z z )q are all
(cid:48)
(cid:32) (cid:32) −
0’s.
Furthermore k (cid:44) 0, since q (cid:44) 0 and z z (cid:44) 0. Since q is odd, it has no
(cid:48)
−
trailing 0’s in its binary representation:
q = ((cid:63), . . . , (cid:63), 1) .

（中文关键词：哈希表、哈希）

## 5.1.1 Multiplicative Hashing (3/4)

2
Since z z < 2w, z z has fewer than w trailing 0’s in its binary repre-
(cid:48) (cid:48)
| − | −
sentation:
z z (cid:48) = ((cid:63), . . . , (cid:63), 1, 0, . . . , 0) 2 .
−
<w
Therefore, the product (z z
(cid:48)
)q has fewe(cid:124)r (cid:123)th(cid:122)a(cid:125)n w trailing 0’s in its binary
−
representation: (cid:32) (cid:32)
(z z (cid:48) )q = ((cid:63), , (cid:63), 1, 0, . . . , 0) 2 .
− · · ·
<w
(cid:124) (cid:123)(cid:122) (cid:125)
(cid:32) (cid:32)
Therefore (z z )q cannot satisfy (5.1), yielding a contradiction and com-
(cid:48)
−
pleting the proof.

（中文关键词：哈希）

## 5.1.1 Multiplicative Hashing (4/4)

The utility of Lemma 5.3 comes from the following observation: If z is
chosen uniformly at random from S, then zt is uniformly distributed over
S. In the following proof, it helps to think of the binary representation of
z, which consists of w 1 random bits followed by a 1.
−
Proof of Lemma 5.1. First we note that the condition hash(x) = hash(y) is
equivalent to the statement “the highest-order d bits of zx mod 2w and the
highest-order d bits of zy mod 2w are the same.” A necessary condition of
that statement is that the highest-order d bits in the binary representation
of z(x y) mod 2w are either all 0’s or all 1’s. That is,
−
z(x y) mod 2w = (0, . . . , 0, (cid:63), . . . , (cid:63)) (5.2)
2
−
d w d
−
when zx mod 2w > zy mod 2w or (cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
(cid:32) (cid:32) (cid:32) (cid:32)
z(x y) mod 2w = (1, . . . , 1, (cid:63), . . . , (cid:63)) . (5.3)
2
−
d w d
−
when zx mod 2w < zy mod 2w. Ther(cid:124)e(cid:123)fo(cid:122)re(cid:125), (cid:124)w(cid:123)e (cid:122)on(cid:125)ly have to bound the
(cid:32) (cid:32) (cid:32) (cid:32)
probability that z(x y) mod 2w looks like (5.2) or (5.3).
−
Let q be the unique odd integer such that (x y) mod 2w = q2r for some
−
integer r 0. By Lemma 5.3, the binary representation of zq mod 2w has
≥
w 1 random bits, followed by a 1:
−
zq mod 2w = (b , . . . , b , 1)
w 1 1 2
−
w 1
−
Therefore, the binary representation(cid:124)of z(cid:123)(x(cid:122) y(cid:125)) mod 2w = zq2r mod 2w has
(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) −(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)
w r 1 random bits, followed by a 1, followed by r 0’s:
− −
z(x y) mod 2w = zq2r mod 2w = (b , . . . , b , 1, 0, 0, . . . , 0)
w r 1 1 2
− − −
w r 1 r
− −
We can now finish the proof: If r > w (cid:124)d, th(cid:123)e(cid:122)n th(cid:125)e d h (cid:124) ig (cid:123) h (cid:122) er (cid:125) order bits
− (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32) (cid:32)(cid:32)(cid:32)(cid:32)
of z(x y) mod 2w contain both 0’s and 1’s, so the probability that z(x
− −
y) mod 2w looks like (5.2) or (5.3) is 0. If r = w d, then the probabil-
−
ity of looking like (5.2) is 0, but the probability of looking like (5.3) is
1/2d 1 = 2/2d (since we must have b , . . . , b = 1, . . . , 1). If r < w d, then
− 1 d 1
− −
we must have b , . . . , b = 0, . . . , 0 or b , . . . , b = 1, . . . , 1. The
w r 1 w r d w r 1 w r d
probability of ea − ch − of thes − e − cases is 1/2d an − d − they ar − e − mutually exclu-
sive, so the probability of either of these cases is 2/2d. This completes the
proof.

（中文关键词：概率、哈希）

## 5.1.2 Summary

The following theorem summarizes the performance of a ChainedHash-
Table data structure:
Theorem 5.1. A ChainedHashTable implements the USet interface. Ignor-
ing the cost of calls to grow(), a ChainedHashTable supports the operations
add(x), remove(x), and find(x) in O(1) expected time per operation.
Furthermore, beginning with an empty ChainedHashTable, any sequence
of m add(x) and remove(x) operations results in a total of O(m) time spent
during all calls to grow().
