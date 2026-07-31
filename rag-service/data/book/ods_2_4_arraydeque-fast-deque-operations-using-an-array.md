---
structure: Deque
source: book/ods_2_4_arraydeque-fast-deque-operations-using-an-array.md
chapter: 2. Array-Based Lists
section: 2.4
page: 54
kind: textbook
---

# 2.4 ArrayDeque: Fast Deque Operations Using an Array

## ArrayDeque: Fast Deque Operations Using an Array (1/2)

The ArrayQueue from the previous section is a data structure for rep-
resenting a sequence that allows us to efficiently add to one end of the
sequence and remove from the other end. The ArrayDeque data structure
allows for efficient addition and removal at both ends. This structure im-
plements the List interface by using the same circular array technique
used to represent an ArrayQueue.
ArrayDeque
T[] a;
int j;
int n;
The get(i) and set(i, x) operations on an ArrayDeque are straightfor-
ward. They get or set the array element a[(j + i) mod a.length].
ArrayDeque
T get(int i) {
return a[(j+i)%a.length];
}
T set(int i, T x) {
T y = a[(j+i)%a.length];
a[(j+i)%a.length] = x;
return y;
}
The implementation of add(i, x) is a little more interesting. As usual,
we first check if a is full and, if necessary, call resize() to resize a. Re-
member that we want this operation to be fast when i is small (close
to 0) or when i is large (close to n). Therefore, we check if i < n/2. If
so, we shift the elements a[0], . . . , a[i 1] left by one position. Otherwise
−
(i n/2), we shift the elements a[i], . . . , a[n 1] right by one position. See
≥ −
Figure 2.3 for an illustration of add(i, x) and remove(x) operations on an
ArrayDeque.
ArrayDeque
void add(int i, T x) {
if (n+1 > a.length) resize();
if (i < n/2) { // shift a[0],..,a[i-1] left one position
j = (j == 0) ? a.length - 1 : j - 1; //(j-1)mod a.length
for (int k = 0; k <= i-1; k++)
a[(j+k)%a.length] = a[(j+k+1)%a.length];
j = 0, n = 8 a b c d e f g h
remove(2)
j = 1, n = 7 a b d e f g h
add(4,x)
j = 1, n = 8 a b d e x f g h
add(3,y)
j = 0, n = 9 a b d y e x f g h
add(4,z)
j = 11, n = 10 b d y z e x f g h a
0 1 2 3 4 5 6 7 8 9 10 11
Figure 2.3: A sequence of add(i,x) and remove(i) operations on an ArrayDeque.

（中文关键词：数组、双端队列、队列）

## ArrayDeque: Fast Deque Operations Using an Array (2/2)

Arrows denote elements being copied.
} else { // shift a[i],..,a[n-1] right one position
for (int k = n; k > i; k--)
a[(j+k)%a.length] = a[(j+k-1)%a.length];
}
a[(j+i)%a.length] = x;
n++;
}
By doing the shifting in this way, we guarantee that add(i, x) never
has to shift more than min i, n i elements. Thus, the running time
{ − }
of the add(i, x) operation (ignoring the cost of a resize() operation) is
O(1 + min i, n i ).
{ − }
The implementation of the remove(i) operation is similar. It either
shifts elements a[0], . . . , a[i 1] right by one position or shifts the ele-
−
ments a[i + 1], . . . , a[n 1] left by one position depending on whether i <
−
n/2. Again, this means that remove(i) never spends more than O(1 +
min i, n i ) time to shift elements.
{ − }
ArrayDeque
T remove(int i) {
T x = a[(j+i)%a.length];
if (i < n/2) { // shift a[0],..,[i-1] right one position
for (int k = i; k > 0; k--)
a[(j+k)%a.length] = a[(j+k-1)%a.length];
j = (j + 1) % a.length;
} else { // shift a[i+1],..,a[n-1] left one position
for (int k = i; k < n-1; k++)
a[(j+k)%a.length] = a[(j+k+1)%a.length];
}
n--;
if (3*n < a.length) resize();
return x;
}

（中文关键词：数组、双端队列）

## 2.4.1 Summary

The following theorem summarizes the performance of the ArrayDeque
data structure:
Theorem 2.3. An ArrayDeque implements the List interface. Ignoring the
cost of calls to resize(), an ArrayDeque supports the operations
• get(i) and set(i, x) in O(1) time per operation; and
• add(i, x) and remove(i) in O(1 + min i, n i ) time per operation.
{ − }
Furthermore, beginning with an empty ArrayDeque, performing any sequence
of m add(i, x) and remove(i) operations results in a total of O(m) time spent
during all calls to resize().

（中文关键词：数组、双端队列）
