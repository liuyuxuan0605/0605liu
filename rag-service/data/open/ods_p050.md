---
structure:
source: open/ods_p050.md
page: 50
---

# ODS p50: §2.3 Array-Based Lists

§2.3 Array-Based Lists
language there is the std::copy (a0;a1;b) algorithm. In Java there is the
System:arraycopy (s;i;d;j;n) method.
FastArrayStack
void resize() {
T[] b = newArray(max(2 *n,1));
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
if (a.length >= 3 *n) resize();
return x;
}
These functions are usually highly optimized and may even use spe-
cial machine instructions that can do this copying much faster than we
could by using a for loop. Although using these functions does not
asymptotically decrease the running times, it can still be a worthwhile
optimization. In the Java implementations here, the use of the native
System:arraycopy (s;i;d;j;n) resulted in speedups of a factor between 2
and 3, depending on the types of operations performed. Your mileage
may vary.
2.3 ArrayQueue : An Array-Based Queue
In this section, we present the ArrayQueue data structure, which imple-
ments a FIFO (ﬁrst-in-ﬁrst-out) queue; elements are removed (using the
remove () operation) from the queue in the same order they are added (us-
ing the add(x) operation).
36

（中文关键词：数组、栈、队列）
