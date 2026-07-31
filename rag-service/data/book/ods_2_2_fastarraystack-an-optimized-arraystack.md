---
structure: Stack
source: book/ods_2_2_fastarraystack-an-optimized-arraystack.md
chapter: 2. Array-Based Lists
section: 2.2
page: 49
kind: textbook
---

# 2.2 FastArrayStack: An Optimized ArrayStack

Much of the work done by an ArrayStack involves shifting (by add(i, x)
and remove(i)) and copying (by resize()) of data. In the implementa-
tions shown above, this was done using for loops. It turns out that many
programming environments have specific functions that are very efficient
at copying and moving blocks of data. In the C programming language,
there are the memcpy(d, s, n) and memmove(d, s, n) functions. In the C++
language there is the std :: copy(a0, a1, b) algorithm. In Java there is the
System.arraycopy(s, i, d, j, n) method.
FastArrayStack
void resize() {
T[] b = newArray(max(2*n,1));
System.arraycopy(a, 0, b, 0, n);
a = b;
}
void add(int i, T x) {
if (n + 1 > a.length) resize();
System.arraycopy(a, i, a, i+1, n-i);
a[i] = x;
n++;
}
T remove(int i) {
T x = a[i];
System.arraycopy(a, i+1, a, i, n-i-1);
n--;
if (a.length >= 3*n) resize();
return x;
}
These functions are usually highly optimized and may even use spe-
cial machine instructions that can do this copying much faster than we
could by using a for loop. Although using these functions does not
asymptotically decrease the running times, it can still be a worthwhile
optimization. In the Java implementations here, the use of the native
System.arraycopy(s, i, d, j, n) resulted in speedups of a factor between 2
and 3, depending on the types of operations performed. Your mileage
may vary.

（中文关键词：数组、栈）
