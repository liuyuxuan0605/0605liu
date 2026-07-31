---
structure: Stack
source: book/ods_2_1_arraystack-fast-stack-operations-using-an-array.md
chapter: 2. Array-Based Lists
section: 2.1
page: 44
kind: textbook
---

# 2.1 ArrayStack: Fast Stack Operations Using an Array

An ArrayStack implements the list interface using an array a, called the
backing array. The list element with index i is stored in a[i]. At most
times, a is larger than strictly necessary, so an integer n is used to keep
track of the number of elements actually stored in a. In this way, the list
elements are stored in a[0],. . . ,a[n 1] and, at all times, a.length n.
− ≥
ArrayStack
T[] a;
int n;
int size() {
return n;
}
2.1.1

（中文关键词：数组、栈）

## The Basics

Accessing and modifying the elements of an ArrayStack using get(i) and
set(i, x) is trivial. After performing any necessary bounds-checking we
simply return or set, respectively, a[i].
ArrayStack
T get(int i) {
return a[i];
}
T set(int i, T x) {
T y = a[i];
a[i] = x;
return y;
}
The operations of adding and removing elements from an ArrayStack
are illustrated in Figure 2.1. To implement the add(i, x) operation, we first
check if a is already full. If so, we call the method resize() to increase
the size of a. How resize() is implemented will be discussed later. For
now, it is sufficient to know that, after a call to resize(), we can be sure
that a.length > n. With this out of the way, we now shift the elements
a[i], . . . , a[n 1] right by one position to make room for x, set a[i] equal to
−
x, and increment n.
ArrayStack
void add(int i, T x) {
if (n + 1 > a.length) resize();
for (int j = n; j > i; j--)
a[j] = a[j-1];
a[i] = x;
n++;
}
If we ignore the cost of the potential call to resize(), then the cost of
the add(i, x) operation is proportional to the number of elements we have
to shift to make room for x. Therefore the cost of this operation (ignoring
the cost of resizing a) is O(n i + 1).
−
Implementing the remove(i) operation is similar. We shift the ele-
ments a[i + 1], . . . , a[n 1] left by one position (overwriting a[i]) and de-
−
crease the value of n. After doing this, we check if n is getting much
smaller than a.length by checking if a.length 3n. If so, then we call
≥
resize() to reduce the size of a.
ArrayStack
T remove(int i) {
T x = a[i];
b r e d
add(2,e)
b r e e d
add(5,r)
b r e e d r
add(5,e)
∗
b r e e d r
b r e e d e r
remove(4)
b r e e e r
remove(4)
b r e e r
remove(4)
∗
b r e e
b r e e
set(2,i)
b r i e
0 1 2 3 4 5 6 7 8 9 10 11
Figure 2.1: A sequence of add(i,x) and remove(i) operations on an ArrayStack.
Arrows denote elements being copied. Operations that result in a call to resize()
are marked with an asterisk.
for (int j = i; j < n-1; j++)
a[j] = a[j+1];
n--;
if (a.length >= 3*n) resize();
return x;
}
If we ignore the cost of the resize() method, the cost of a remove(i)
operation is proportional to the number of elements we shift, which is
O(n i).
−
2.1.2

（中文关键词：数组、栈）

## Growing and Shrinking (1/2)

The resize() method is fairly straightforward; it allocates a new array b
whose size is 2n and copies the n elements of a into the first n positions in
b, and then sets a to b. Thus, after a call to resize(), a.length = 2n.
ArrayStack
void resize() {
T[] b = newArray(max(n*2,1));
for (int i = 0; i < n; i++) {
b[i] = a[i];
}
a = b;
}
Analyzing the actual cost of the resize() operation is easy. It allocates
an array b of size 2n and copies the n elements of a into b. This takes O(n)
time.
The running time analysis from the previous section ignored the cost
of calls to resize(). In this section we analyze this cost using a technique
known as amortized analysis. This technique does not try to determine the
cost of resizing during each individual add(i, x) and remove(i) operation.
Instead, it considers the cost of all calls to resize() during a sequence of
m calls to add(i, x) or remove(i). In particular, we will show:
Lemma 2.1. If an empty ArrayList is created and any sequence of m 1
≥
calls to add(i, x) and remove(i) are performed, then the total time spent dur-
ing all calls to resize() is O(m).
Proof. We will show that any time resize() is called, the number of calls
to add or remove since the last call to resize() is at least n/2 1. Therefore,
−
if n denotes the value of n during the ith call to resize() and r denotes
i
the number of calls to resize(), then the total number of calls to add(i, x)
or remove(i) is at least
r
(n /2 1) m ,
i
− ≤
i=1
(cid:88)
which is equivalent to
r
n 2m + 2r .
i
≤
i=1
(cid:88)
On the other hand, the total time spent during all calls to resize() is
r
O(n ) O(m + r) = O(m) ,
i
≤
i=1
(cid:88)
since r is not more than m. All that remains is to show that the number
of calls to add(i, x) or remove(i) between the (i 1)th and the ith call to
−
resize() is at least n /2.
i
There are two cases to consider. In the first case, resize() is being
called by add(i, x) because the backing array a is full, i.e., a.length = n =
n . Consider the previous call to resize(): after this previous call, the
i
size of a was a.length, but the number of elements stored in a was at
most a.length/2 = n /2. But now the number of elements stored in a is
i
n = a.length, so there must have been at least n /2 calls to add(i, x) since
i i
the previous call to resize().

（中文关键词：数组、摊还分析、栈）

## Growing and Shrinking (2/2)

The second case occurs when resize() is being called by remove(i)
because a.length 3n = 3n . Again, after the previous call to resize()
i
≥
the number of elements stored in a was at least a.length/2 1.1 Now
−
there are n a.length/3 elements stored in a. Therefore, the number of
i
≤
1The 1 in this formula accounts for the special case that occurs when n = 0 and
−
a.length = 1.
remove(i) operations since the last call to resize() is at least
R a.length/2 1 a.length/3
≥ − −
= a.length/6 1
−
= (a.length/3)/2 1
−
n /2 1 .
i
≥ −
In either case, the number of calls to add(i, x) or remove(i) that occur
between the (i 1)th call to resize() and the ith call to resize() is at least
−
n /2 1, as required to complete the proof.
i
−
2.1.3

## Summary

The following theorem summarizes the performance of an ArrayStack:
Theorem 2.1. An ArrayStack implements the List interface. Ignoring the
cost of calls to resize(), an ArrayStack supports the operations
• get(i) and set(i, x) in O(1) time per operation; and
• add(i, x) and remove(i) in O(1 + n i) time per operation.
−
Furthermore, beginning with an empty ArrayStack and performing any se-
quence of m add(i, x) and remove(i) operations results in a total of O(m) time
spent during all calls to resize().
The ArrayStack is an efficient way to implement a Stack. In particu-
lar, we can implement push(x) as add(n, x) and pop() as remove(n 1), in
−
which case these operations will run in O(1) amortized time.

（中文关键词：栈、数组、摊还分析）
