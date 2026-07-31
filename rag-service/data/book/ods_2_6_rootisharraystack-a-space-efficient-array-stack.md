---
structure: Stack
source: book/ods_2_6_rootisharraystack-a-space-efficient-array-stack.md
chapter: 2. Array-Based Lists
section: 2.6
page: 63
kind: textbook
---

# 2.6 RootishArrayStack: A Space-Efficient Array Stack

## RootishArrayStack: A Space-Efficient Array Stack (1/3)

One of the drawbacks of all previous data structures in this chapter is
that, because they store their data in one or two arrays and they avoid
resizing these arrays too often, the arrays frequently are not very full. For
example, immediately after a resize() operation on an ArrayStack, the
backing array a is only half full. Even worse, there are times when only
1/3 of a contains data.
blocks
a b c d e f g h
add(2,x)
a b x c d e f g h
remove(1)
a x c d e f g h
remove(7)
a x c d e f g
remove(6)
a x c d e f
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
Figure 2.5: A sequence of add(i,x) and remove(i) operations on a RootishArray-
Stack. Arrows denote elements being copied.
In this section, we discuss the RootishArrayStack data structure, that
addresses the problem of wasted space. The RootishArrayStack stores
n elements using O(√n) arrays. In these arrays, at most O(√n) array lo-
cations are unused at any time. All remaining array locations are used
to store data. Therefore, these data structures waste at most O(√n) space
when storing n elements.
A RootishArrayStack stores its elements in a list of r arrays called
blocks that are numbered 0, 1, . . . , r 1. See Figure 2.5. Block b contains
−
b + 1 elements. Therefore, all r blocks contain a total of
1 + 2 + 3 + + r = r(r + 1)/2
· · ·
elements. The above formula can be obtained as shown in Figure 2.6.
RootishArrayStack
List<T[]> blocks;
int n;
As we might expect, the elements of the list are laid out in order
within the blocks. The list element with index 0 is stored in block 0,
. . .
.
.
.
r . . .
.
.
.
. . .
r + 1
Figure 2.6: The number of white squares is 1+2+3+ +r. The number of shaded
···
squares is the same. Together the white and shaded squares make a rectangle
consisting of r(r + 1) squares.
elements with list indices 1 and 2 are stored in block 1, elements with list
indices 3, 4, and 5 are stored in block 2, and so on. The main problem
we have to address is that of determining, given an index i, which block
contains i as well as the index corresponding to i within that block.

（中文关键词：数组、栈）

## RootishArrayStack: A Space-Efficient Array Stack (2/3)

Determining the index of i within its block turns out to be easy. If
index i is in block b, then the number of elements in blocks 0, . . . , b 1 is
−
b(b + 1)/2. Therefore, i is stored at location
j = i b(b + 1)/2
−
within block b. Somewhat more challenging is the problem of determin-
ing the value of b. The number of elements that have indices less than or
equal to i is i + 1. On the other hand, the number of elements in blocks
0,. . . ,b is (b + 1)(b + 2)/2. Therefore, b is the smallest integer such that
(b + 1)(b + 2)/2 i + 1 .
≥
We can rewrite this equation as
b2 + 3b 2i 0 .
− ≥
The corresponding quadratic equation b2 + 3b 2i = 0 has two solutions:
−
b = ( 3 + √9 + 8i)/2 and b = ( 3 √9 + 8i)/2. The second solution makes
− − −
no sense in our application since it always gives a negative value. There-
fore, we obtain the solution b = ( 3 + √9 + 8i)/2. In general, this solution
−
is not an integer, but going back to our inequality, we want the smallest
integer b such that b ( 3 + √9 + 8i)/2. This is simply
≥ −
b = ( 3 + √9 + 8i)/2 .
−
(cid:108) (cid:109)
RootishArrayStack
int i2b(int i) {
double db = (-3.0 + Math.sqrt(9 + 8*i)) / 2.0;
int b = (int)Math.ceil(db);
return b;
}
With this out of the way, the get(i) and set(i, x) methods are straight-
forward. We first compute the appropriate block b and the appropriate
index j within the block and then perform the appropriate operation:
RootishArrayStack
T get(int i) {
int b = i2b(i);
int j = i - b*(b+1)/2;
return blocks.get(b)[j];
}
T set(int i, T x) {
int b = i2b(i);
int j = i - b*(b+1)/2;
T y = blocks.get(b)[j];
blocks.get(b)[j] = x;
return y;
}
If we use any of the data structures in this chapter for representing
the blocks list, then get(i) and set(i, x) will each run in constant time.
The add(i, x) method will, by now, look familiar. We first check to see
if our data structure is full, by checking if the number of blocks r is such
that r(r + 1)/2 = n. If so, we call grow() to add another block. With this
done, we shift elements with indices i, . . . , n 1 to the right by one position
−
to make room for the new element with index i:
RootishArrayStack
void add(int i, T x) {
int r = blocks.size();
if (r*(r+1)/2 < n + 1) grow();
n++;
for (int j = n-1; j > i; j--)
set(j, get(j-1));
set(i, x);
}
The grow() method does what we expect. It adds a new block:

（中文关键词：数组、栈）

## RootishArrayStack: A Space-Efficient Array Stack (3/3)

RootishArrayStack
void grow() {
blocks.add(newArray(blocks.size()+1));
}
Ignoring the cost of the grow() operation, the cost of an add(i, x) oper-
ation is dominated by the cost of shifting and is therefore O(1 + n i), just
−
like an ArrayStack.
The remove(i) operation is similar to add(i, x). It shifts the elements
with indices i + 1, . . . , n left by one position and then, if there is more than
one empty block, it calls the shrink() method to remove all but one of the
unused blocks:
RootishArrayStack
T remove(int i) {
T x = get(i);
for (int j = i; j < n-1; j++)
set(j, get(j+1));
n--;
int r = blocks.size();
if ((r-2)*(r-1)/2 >= n) shrink();
return x;
}
RootishArrayStack
void shrink() {
int r = blocks.size();
while (r > 0 && (r-2)*(r-1)/2 >= n) {
blocks.remove(blocks.size()-1);
r--;
}
}
Once again, ignoring the cost of the shrink() operation, the cost of a
remove(i) operation is dominated by the cost of shifting and is therefore
O(n i).
−

（中文关键词：数组、栈）

## 2.6.1 Analysis of Growing and Shrinking

The above analysis of add(i, x) and remove(i) does not account for the
cost of grow() and shrink(). Note that, unlike the ArrayStack.resize()
operation, grow() and shrink() do not copy any data. They only allocate
or free an array of size r. In some environments, this takes only constant
time, while in others, it may require time proportional to r.
We note that, immediately after a call to grow() or shrink(), the situ-
ation is clear. The final block is completely empty, and all other blocks
are completely full. Another call to grow() or shrink() will not happen
until at least r 1 elements have been added or removed. Therefore, even
−
if grow() and shrink() take O(r) time, this cost can be amortized over at
least r 1 add(i, x) or remove(i) operations, so that the amortized cost of
−
grow() and shrink() is O(1) per operation.

（中文关键词：摊还分析、数组、栈）

## 2.6.2 Space Usage

Next, we analyze the amount of extra space used by a RootishArray-
Stack. In particular, we want to count any space used by a Rootish-
ArrayStack that is not an array element currently used to hold a list ele-
ment. We call all such space wasted space.
The remove(i) operation ensures that a RootishArrayStack never has
more than two blocks that are not completely full. The number of blocks,
r, used by a RootishArrayStack that stores n elements therefore satisfies
(r 2)(r 1) n .
− − ≤
Again, using the quadratic equation on this gives
r (3 + √1 + 4n)/2 = O(√n) .
≤
The last two blocks have sizes r and r 1, so the space wasted by these
−
two blocks is at most 2r 1 = O(√n). If we store the blocks in (for example)
−
an ArrayList, then the amount of space wasted by the List that stores
those r blocks is also O(r) = O(√n). The other space needed for storing n
and other accounting information is O(1). Therefore, the total amount of
wasted space in a RootishArrayStack is O(√n).
Next, we argue that this space usage is optimal for any data structure
that starts out empty and can support the addition of one item at a time.
More precisely, we will show that, at some point during the addition of
n items, the data structure is wasting an amount of space at least in √n
(though it may be only wasted for a moment).
Suppose we start with an empty data structure and we add n items one
at a time. At the end of this process, all n items are stored in the structure
and distributed among a collection of r memory blocks. If r √n, then
≥
the data structure must be using r pointers (or references) to keep track
of these r blocks, and these pointers are wasted space. On the other hand,
if r < √n then, by the pigeonhole principle, some block must have a size
of at least n/r > √n. Consider the moment at which this block was first
allocated. Immediately after it was allocated, this block was empty, and
was therefore wasting √n space. Therefore, at some point in time during
the insertion of n elements, the data structure was wasting √n space.

（中文关键词：数组、栈）

## 2.6.3 Summary

The following theorem summarizes our discussion of the RootishArray-
Stack data structure:
Theorem 2.5. A RootishArrayStack implements the List interface. Ignor-
ing the cost of calls to grow() and shrink(), a RootishArrayStack supports
the operations
• get(i) and set(i, x) in O(1) time per operation; and
• add(i, x) and remove(i) in O(1 + n i) time per operation.
−
Furthermore, beginning with an empty RootishArrayStack, any sequence
of m add(i, x) and remove(i) operations results in a total of O(m) time spent
during all calls to grow() and shrink().
The space (measured in words)3 used by a RootishArrayStack that stores
n elements is n + O(√n).

（中文关键词：数组、栈）

## 2.6.4 Computing Square Roots (1/3)

A reader who has had some exposure to models of computation may no-
tice that the RootishArrayStack, as described above, does not fit into the
usual word-RAM model of computation (Section 1.4) because it requires
taking square roots. The square root operation is generally not consid-
ered a basic operation and is therefore not usually part of the word-RAM
model.
In this section, we show that the square root operation can be imple-
mented efficiently. In particular, we show that for any integer x 0, . . . , n ,
∈ { }
√x can be computed in constant-time, after O(√n) preprocessing that
(cid:98) (cid:99)
creates two arrays of length O(√n). The following lemma shows that we
can reduce the problem of computing the square root of x to the square
root of a related value x .
(cid:48)
Lemma 2.3. Let x 1 and let x = x a, where 0 a √x. Then √x √x 1.
≥ (cid:48) − ≤ ≤ (cid:48) ≥ −
Proof. It suffices to show that
x √x √x 1 .
− ≥ −
(cid:113)
Square both sides of this inequality to get
x √x x 2√x + 1
− ≥ −
and gather terms to get
√x 1
≥
which is clearly true for any x 1.
≥
3Recall Section 1.4 for a discussion of how memory is measured.

（中文关键词：数组、栈）

## 2.6.4 Computing Square Roots (2/3)

Start by restricting the problem a little, and assume that 2r x < 2r+1,
≤
so that log x = r, i.e., x is an integer having r + 1 bits in its binary rep-
(cid:98) (cid:99)
resentation. We can take x = x (x mod 2 r/2 ). Now, x satisfies the con-
(cid:48) (cid:98) (cid:99) (cid:48)
−
ditions of Lemma 2.3, so √x √x 1. Furthermore, x has all of its
− (cid:48) ≤ (cid:48)
lower-order r/2 bits equal to 0, so there are only
(cid:98) (cid:99)
2r+1 r/2 4 2r/2 4√x
−(cid:98) (cid:99)
≤ · ≤
possible values of x . This means that we can use an array, sqrttab, that
(cid:48)
stores the value of √x for each possible value of x . A little more pre-
(cid:98) (cid:48)(cid:99) (cid:48)
cisely, we have
sqrttab[i] = i2 r/2 .
(cid:98) (cid:99)
In this way, sqrttab[i] is within 2 of √
(cid:22)(cid:112)
x for all
(cid:23)
x i2 r/2 , . . . , (i + 1)2 r/2
(cid:98) (cid:99) (cid:98) (cid:99)
∈ { −
1 . Stated another way, the array entry s = sqrttab[x>> r/2 ] is either
} (cid:98) (cid:99)
equal to √x , √x 1, or √x 2. From s we can determine the value of
(cid:98) (cid:99) (cid:98) (cid:99) − (cid:98) (cid:99) −
√x by incrementing s until (s + 1)2 > x.
(cid:98) (cid:99)
FastSqrt
int sqrt(int x, int r) {
int s = sqrtab[x>>r/2];
while ((s+1)*(s+1) <= x) s++; // executes at most twice
return s;
}
Now, this only works for x 2r, . . . , 2r+1 1 and sqrttab is a special
∈ { − }
table that only works for a particular value of r = log x . To overcome
(cid:98) (cid:99)
this, we could compute log n different sqrttab arrays, one for each pos-
(cid:98) (cid:99)
sible value of log x . The sizes of these tables form an exponential se-
(cid:98) (cid:99)
quence whose largest value is at most 4√n, so the total size of all tables is
O(√n).
However, it turns out that more than one sqrttab array is unneces-
sary; we only need one sqrttab array for the value r = log n . Any value
(cid:98) (cid:99)
x with log x = r (cid:48) < r can be upgraded by multiplying x by 2r − r (cid:48) and using
the equation
√2r − r (cid:48) x = 2(r − r (cid:48))/2√x .
The quantity 2r − r (cid:48) x is in the range 2r, . . . , 2r+1 1 so we can look up
{ − }
its square root in sqrttab. The following code implements this idea to
compute √x for all non-negative integers x in the range 0, . . . , 230 1
(cid:98) (cid:99) { − }
using an array, sqrttab, of size 216.

（中文关键词：数组）

## 2.6.4 Computing Square Roots (3/3)

FastSqrt
int sqrt(int x) {
int rp = log(x);
int upgrade = ((r-rp)/2) * 2;
int xp = x << upgrade; // xp has r or r-1 bits
int s = sqrtab[xp>>(r/2)] >> (upgrade/2);
while ((s+1)*(s+1) <= x) s++; // executes at most twice
return s;
}
Something we have taken for granted thus far is the question of how
to compute r = log x . Again, this is a problem that can be solved with
(cid:48)
(cid:98) (cid:99)
an array, logtab, of size 2r/2. In this case, the code is particularly simple,
since log x is just the index of the most significant 1 bit in the binary
(cid:98) (cid:99)
representation of x. This means that, for x > 2r/2, we can right-shift the
bits of x by r/2 positions before using it as an index into logtab. The
following code does this using an array logtab of size 216 to compute
log x for all x in the range 1, . . . , 232 1 .
(cid:98) (cid:99) { − }
FastSqrt
int log(int x) {
if (x >= halfint)
return 16 + logtab[x>>>16];
return logtab[x];
}
Finally, for completeness, we include the following code that initial-
izes logtab and sqrttab:
FastSqrt
void inittabs() {
sqrtab = new int[1<<(r/2)];
logtab = new int[1<<(r/2)];
for (int d = 0; d < r/2; d++)
Arrays.fill(logtab, 1<<d, 2<<d, d);
int s = 1<<(r/4); // sqrt(2ˆ(r/2))
for (int i = 0; i < 1<<(r/2); i++) {
if ((s+1)*(s+1) <= i << (r/2)) s++; // sqrt increases
sqrtab[i] = s;
}
}
To summarize, the computations done by the i2b(i) method can be
implemented in constant time on the word-RAM using O(√n) extra mem-
ory to store the sqrttab and logtab arrays. These arrays can be rebuilt
when n increases or decreases by a factor of two, and the cost of this re-
building can be amortized over the number of add(i, x) and remove(i)
operations that caused the change in n in the same way that the cost of
resize() is analyzed in the ArrayStack implementation.

（中文关键词：数组、摊还分析、栈）
