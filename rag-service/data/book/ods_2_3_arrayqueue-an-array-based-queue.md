---
structure: Queue
source: book/ods_2_3_arrayqueue-an-array-based-queue.md
chapter: 2. Array-Based Lists
section: 2.3
page: 50
kind: textbook
---

# 2.3 ArrayQueue: An Array-Based Queue

## ArrayQueue: An Array-Based Queue (1/2)

In this section, we present the ArrayQueue data structure, which imple-
ments a FIFO (first-in-first-out) queue; elements are removed (using the
remove() operation) from the queue in the same order they are added (us-
ing the add(x) operation).
Notice that an ArrayStack is a poor choice for an implementation of
a FIFO queue. It is not a good choice because we must choose one end of
the list upon which to add elements and then remove elements from the
other end. One of the two operations must work on the head of the list,
which involves calling add(i, x) or remove(i) with a value of i = 0. This
gives a running time proportional to n.
To obtain an efficient array-based implementation of a queue, we first
notice that the problem would be easy if we had an infinite array a. We
could maintain one index j that keeps track of the next element to remove
and an integer n that counts the number of elements in the queue. The
queue elements would always be stored in
a[j], a[j + 1], . . . , a[j + n 1] .
−
Initially, both j and n would be set to 0. To add an element, we would
place it in a[j + n] and increment n. To remove an element, we would
remove it from a[j], increment j, and decrement n.
Of course, the problem with this solution is that it requires an infinite
array. An ArrayQueue simulates this by using a finite array a and modular
arithmetic. This is the kind of arithmetic used when we are talking about
the time of day. For example 10:00 plus five hours gives 3:00. Formally,
we say that
10 + 5 = 15 3 (mod 12) .
≡
We read the latter part of this equation as “15 is congruent to 3 modulo
12.” We can also treat mod as a binary operator, so that
15 mod 12 = 3 .
More generally, for an integer a and positive integer m, a mod m is the
unique integer r 0, . . . , m 1 such that a = r + km for some integer k.
∈ { − }
Less formally, the value r is the remainder we get when we divide a by
m. In many programming languages, including Java, the mod operator
is represented using the % symbol.2
2This is sometimes referred to as the brain-dead mod operator, since it does not correctly
implement the mathematical mod operator when the first argument is negative.

（中文关键词：队列、数组、栈）

## ArrayQueue: An Array-Based Queue (2/2)

Modular arithmetic is useful for simulating an infinite array, since
i mod a.length always gives a value in the range 0, . . . , a.length 1. Us-
−
ing modular arithmetic we can store the queue elements at array locations
a[j%a.length], a[(j + 1)%a.length], . . . , a[(j + n 1)%a.length] .
−
This treats the array a like a circular array in which array indices larger
than a.length 1 “wrap around” to the beginning of the array.
−
The only remaining thing to worry about is taking care that the num-
ber of elements in the ArrayQueue does not exceed the size of a.
ArrayQueue
T[] a;
int j;
int n;
A sequence of add(x) and remove() operations on an ArrayQueue is
illustrated in Figure 2.2. To implement add(x), we first check if a is full
and, if necessary, call resize() to increase the size of a. Next, we store x
in a[(j + n)%a.length] and increment n.
ArrayQueue
boolean add(T x) {
if (n + 1 > a.length) resize();
a[(j+n) % a.length] = x;
n++;
return true;
}
To implement remove(), we first store a[j] so that we can return it
later. Next, we decrement n and increment j (modulo a.length) by set-
ting j = (j + 1) mod a.length. Finally, we return the stored value of a[j].
If necessary, we may call resize() to decrease the size of a.
ArrayQueue
T remove() {
if (n == 0) throw new NoSuchElementException();
T x = a[j];
j = (j + 1) % a.length;
j = 2, n = 3 a b c
add(d)
j = 2, n = 4 a b c d
add(e)
j = 2, n = 5 e a b c d
remove()
j = 3, n = 4 e b c d
add(f)
j = 3, n = 5 e f b c d
add(g)
j = 3, n = 6 e f g b c d
add(h)
∗
j = 0, n = 6 b c d e f g
j = 0, n = 7 b c d e f g h
remove()
j = 1, n = 6 c d e f g h
0 1 2 3 4 5 6 7 8 9 10 11
Figure 2.2: A sequence of add(x) and remove(i) operations on an ArrayQueue.
Arrows denote elements being copied. Operations that result in a call to resize()
are marked with an asterisk.
n--;
if (a.length >= 3*n) resize();
return x;
}
Finally, the resize() operation is very similar to the resize() opera-
tion of ArrayStack. It allocates a new array b of size 2n and copies
a[j], a[(j + 1)%a.length], . . . , a[(j + n 1)%a.length]
−
onto
b[0], b[1], . . . , b[n 1]
−
and sets j = 0.
ArrayQueue
void resize() {
T[] b = newArray(max(1,n*2));
for (int k = 0; k < n; k++)
b[k] = a[(j+k) % a.length];
a = b;
j = 0;
}

（中文关键词：数组、队列、栈）

## 2.3.1 Summary

The following theorem summarizes the performance of the ArrayQueue
data structure:
Theorem 2.2. An ArrayQueue implements the (FIFO) Queue interface. Ig-
noring the cost of calls to resize(), an ArrayQueue supports the operations
add(x) and remove() in O(1) time per operation. Furthermore, beginning with
an empty ArrayQueue, any sequence of m add(i, x) and remove(i) operations
results in a total of O(m) time spent during all calls to resize().

（中文关键词：队列、数组）
