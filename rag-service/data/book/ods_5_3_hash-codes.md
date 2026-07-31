---
structure: HashMap
source: book/ods_5_3_hash-codes.md
chapter: 5. Hash Tables
section: 5.3
page: 136
kind: textbook
---

# 5.3 Hash Codes

The hash tables discussed in the previous section are used to associate
data with integer keys consisting of w bits. In many cases, we have keys
that are not integers. They may be strings, objects, arrays, or other com-
pound structures. To use hash tables for these types of data, we must
map these data types to w-bit hash codes. Hash code mappings should
have the following properties:
1. If x and y are equal, then x.hashCode() and y.hashCode() are equal.
2. If x and y are not equal, then the probability that x.hashCode() =
y.hashCode() should be small (close to 1/2w).
The first property ensures that if we store x in a hash table and later
look up a value y equal to x, then we will find x—as we should. The sec-
ond property minimizes the loss from converting our objects to integers.
It ensures that unequal objects usually have different hash codes and so
are likely to be stored at different locations in our hash table.

（中文关键词：哈希表、哈希码、概率、数组）

## 5.3.1 Hash Codes for Primitive Data Types

Small primitive data types like char, byte, int, and float are usually
easy to find hash codes for. These data types always have a binary rep-
resentation and this binary representation usually consists of w or fewer
bits. (For example, in Java, byte is an 8-bit type and float is a 32-bit
type.) In these cases, we just treat these bits as the representation of an
integer in the range 0, . . . , 2w 1 . If two values are different, they get
{ − }
different hash codes. If they are the same, they get the same hash code.
A few primitive data types are made up of more than w bits, usually
cw bits for some constant integer c. (Java’s long and double types are
examples of this with c = 2.) These data types can be treated as compound
objects made of c parts, as described in the next section.

（中文关键词：哈希码）

## 5.3.2 Hash Codes for Compound Objects (1/2)

For a compound object, we want to create a hash code by combining the
individual hash codes of the object’s constituent parts. This is not as easy
as it sounds. Although one can find many hacks for this (for example,
combining the hash codes with bitwise exclusive-or operations), many of
these hacks turn out to be easy to foil (see Exercises 5.7–5.9). However,
if one is willing to do arithmetic with 2w bits of precision, then there are
simple and robust methods available. Suppose we have an object made
up of several parts P , . . . , P whose hash codes are x , . . . , x . Then we
0 r 1 0 r 1
− −
can choose mutually independent random w-bit integers z , . . . , z and a
0 r 1
−
random 2w-bit odd integer z and compute a hash code for our object with
r 1
h(x , . . . , x ) = z − z x mod 22w div 2w .
0 r 1 i i
−   
i=0
Note that this hash code has a

fi

na
(cid:88)
l step (m

ultiplyin

g by z and dividing by
2w) that uses the multiplicative hash function from Section 5.1.1 to take
the 2w-bit intermediate result and reduce it to a w-bit final result. Here
is an example of this method applied to a simple compound object with
three parts x0, x1, and x2:
Point3D
int hashCode() {
// random numbers from rand.org
long[] z = {0x2058cc50L, 0xcb19137eL, 0x2cb6b6fdL};
long zz = 0xbea0107e5067d19dL;
// convert (unsigned) hashcodes to long
long h0 = x0.hashCode() & ((1L<<32)-1);
long h1 = x1.hashCode() & ((1L<<32)-1);
long h2 = x2.hashCode() & ((1L<<32)-1);
return (int)(((z[0]*h0 + z[1]*h1 + z[2]*h2)*zz)
>>> 32);
}
The following theorem shows that, in addition to being straightfor-
ward to implement, this method is provably good:
Theorem 5.3. Let x , . . . , x and y , . . . , y each be sequences of w bit inte-
0 r 1 0 r 1
gers in 0, . . . , 2w 1 and ass − ume x (cid:44) y for a − t least one index i 0, . . . , r 1 .
i i
{ − } ∈ { − }
Then
Pr h(x , . . . , x ) = h(y , . . . , y ) 3/2w .

（中文关键词：哈希码）

## 5.3.2 Hash Codes for Compound Objects (2/2)

0 r 1 0 r 1
{ − − } ≤
Proof. We will first ignore the final multiplicative hashing step and see
how that step contributes later. Define:
r 1
h(cid:48) (x
0
, . . . , x
r 1
) = − z
j
x
j
mod 22w .
−  
j=0
 (cid:88) 
Suppose that h (x , . . . , x ) = h (y , . . . , y ). We can rewrite this as:
(cid:48) 0 r 1 (cid:48) 0 r 1
− −
z (x y ) mod 22w = t (5.4)
i i i
−
where
i 1 r 1
t = − z (y x ) + − z (y x ) mod 22w
j j j j j j
 − − 
j=0 j=i+1
If we assume, with
 (cid:88)
out loss of gener
(cid:88)
ality that x
i
>

y
i
, then (5.4) becomes
z (x y ) = t , (5.5)
i i i
−
since each of z and (x y ) is at most 2w 1, so their product is at
i i i
− −
most 22w 2w+1 + 1 < 22w 1. By assumption, x y (cid:44) 0, so (5.5) has
i i
− − −
at most one solution in z . Therefore, since z and t are independent
i i
(z , . . . , z are mutually independent), the probability that we select z
0 r 1 i
so that h − (x , . . . , x ) = h (y , . . . , y ) is at most 1/2w.
(cid:48) 0 r 1 (cid:48) 0 r 1
− −
The final step of the hash function is to apply multiplicative hashing
to reduce our 2w-bit intermediate result h (x , . . . , x ) to a w-bit final re-
(cid:48) 0 r 1
sult h(x , . . . , x ). By Theorem 5.3, if h (x , . . . , x )
−(cid:44)
h (y , . . . , y ), then
0 r 1 (cid:48) 0 r 1 (cid:48) 0 r 1
Pr h(x , . . . , x − ) = h(y , . . . , y ) 2/2w. − −
0 r 1 0 r 1
{ − − } ≤
To summarize,
h(x , . . . , x )
Pr 0 r 1
= h(y , . .−. , y )
0 r 1
(cid:40) − (cid:41)
h (x , . . . , x ) = h (y , . . . , y ) or
(cid:48) 0 r 1 (cid:48) 0 r 1
= Pr h (x , . . . , x − ) (cid:44) h (y , . . . , y − )
(cid:48) 0 r 1 (cid:48) 0 r 1
≤
1/2
 
 w + 2
a
/
n
2
d
w =
zh
3
(cid:48)
/
(x
2
− 0
w
, .
.
. . , x r
−
1 ) div 2w−= zh (cid:48) (y 0 , . . . , y r
−
1 ) div 2w  


（中文关键词：哈希、概率、哈希码）

## 5.3.3 Hash Codes for Arrays and Strings (1/2)

The method from the previous section works well for objects that have a
fixed, constant, number of components. However, it breaks down when
we want to use it with objects that have a variable number of components,
since it requires a random w-bit integer z for each component. We could
i
use a pseudorandom sequence to generate as many z ’s as we need, but
i
then the z ’s are not mutually independent, and it becomes difficult to
i
prove that the pseudorandom numbers don’t interact badly with the hash
function we are using. In particular, the values of t and z in the proof of
i
Theorem 5.3 are no longer independent.
A more rigorous approach is to base our hash codes on polynomials
over prime fields; these are just regular polynomials that are evaluated
modulo some prime number, p. This method is based on the following
theorem, which says that polynomials over prime fields behave pretty-
much like usual polynomials:
Theorem 5.4. Let p be a prime number, and let f (z) = x z0 + x z1 + +
0 1
· · ·
x zr 1 be a non-trivial polynomial with coefficients x 0, . . . , p 1 . Then
r 1 − i
− ∈ { − }
the equation f (z) mod p = 0 has at most r 1 solutions for z 0, . . . , p 1 .
− ∈ { − }
To use Theorem 5.4, we hash a sequence of integers x , . . . , x with
0 r 1
−
each x 0, . . . , p 2 using a random integer z 0, . . . , p 1 via the for-
i
∈ { − } ∈ { − }
mula
h(x 0 , . . . , x r 1 ) = x 0 z0 + + x r 1 zr − 1 + (p 1)zr mod p .
− · · · − −
Note the extra (p 1)z(cid:16)r term at the end of the formula(cid:17). It helps to think
−
of (p 1) as the last element, x , in the sequence x , . . . , x . Note that this
r 0 r
−
element differs from every other element in the sequence (each of which
is in the set 0, . . . , p 2 ). We can think of p 1 as an end-of-sequence
{ − } −
marker.
The following theorem, which considers the case of two sequences of
the same length, shows that this hash function gives a good return for the
small amount of randomization needed to choose z:
Theorem 5.5. Let p > 2w + 1 be a prime, let x , . . . , x and y , . . . , y each
0 r 1 0 r 1
be sequences of w-bit integers in 0, . . . , 2w 1 , and ass − ume x (cid:44) y for − at least
i i
{ − }
one index i 0, . . . , r 1 . Then
∈ { − }
Pr h(x , . . . , x ) = h(y , . . . , y ) (r 1)/p .

（中文关键词：哈希码、数组）

## 5.3.3 Hash Codes for Arrays and Strings (2/2)

0 r 1 0 r 1
{ − − } ≤ − }
Proof. The equation h(x , . . . , x ) = h(y , . . . , y ) can be rewritten as
0 r 1 0 r 1
− −
(x
0
y
0
)z0 + + (x
r 1
y
r 1
)zr
−
1 mod p = 0. (5.6)
− · · · − − −
Since x (cid:44) y ,(cid:16)this polynomial is non-trivial. Th(cid:17)erefore, by Theorem 5.4,
i i
it has at most r 1 solutions in z. The probability that we pick z to be one
−
of these solutions is therefore at most (r 1)/p.
−
Note that this hash function also deals with the case in which two
sequences have different lengths, even when one of the sequences is a
prefix of the other. This is because this function effectively hashes the
infinite sequence
x , . . . , x , p 1, 0, 0, . . . .
0 r 1
− −
This guarantees that if we have two sequences of length r and r with
(cid:48)
r > r , then these two sequences differ at index i = r. In this case, (5.6)
(cid:48)
becomes
i=r(cid:48)− 1 i=r
−
1
(x y )zi + (x p + 1)zr(cid:48) + x zi + (p 1)zr mod p = 0 ,
i i r i
− (cid:48) − −
 
i=0 i=r +1
whi
ch (cid:88)
, by Theorem 5.4, has at most r
(cid:88)
so
(cid:48)
lutions in z. Thi
s
combined with
Theorem 5.5 suffice to prove the following more general theorem:
Theorem 5.6. Let p > 2w + 1 be a prime, let x , . . . , x and y , . . . , y be
0 r 1 0 r 1
distinct sequences of w-bit integers in 0, . . . , 2w 1 . The − n (cid:48)−
{ − }
Pr h(x
0
, . . . , x
r 1
) = h(y
0
, . . . , y
r 1
) max r, r(cid:48) /p .
{ − − } ≤ { }
The following example code shows how this hash function is applied
to an object that contains an array, x, of values:
GeomVector
int hashCode() {
long p = (1L<<32)-5; // prime: 2ˆ32 - 5
long z = 0x64b6055aL; // 32 bits from random.org
int z2 = 0x5067d19d; // random odd 32 bit number
long s = 0;
long zi = 1;
for (int i = 0; i < x.length; i++) {
// reduce to 31 bits
long xi = (x[i].hashCode() * z2) >>> 1;
s = (s + zi * xi) % p;
zi = (zi * z) % p;
}
s = (s + zi * (p-1)) % p;
return (int)s;
}
The preceding code sacrifices some collision probability for imple-
mentation convenience. In particular, it applies the multiplicative hash
function from Section 5.1.1, with d = 31 to reduce x[i].hashCode() to a 31-
bit value. This is so that the additions and multiplications that are done
modulo the prime p = 232 5 can be carried out using unsigned 63-bit
−
arithmetic. Thus the probability of two different sequences, the longer of
which has length r, having the same hash code is at most
2/231 + r/(232 5)
−
rather than the r/(232 5) specified in Theorem 5.6.
−

（中文关键词：概率、哈希码、数组）
