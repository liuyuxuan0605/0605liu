---
structure:
source: open/ods_p233.md
page: 233
---

# ODS p233: MeldableHeap : A Randomized Meldable Heap §10.2

MeldableHeap : A Randomized Meldable Heap §10.2
pected time, where nis the total number of elements in h1andh2.
With access to a merge (h1;h2) operation, the add(x) operation is easy.
We create a new node ucontaining xand then merge uwith the root of
our heap:
MeldableHeap
boolean add(T x) {
Node<T> u = newNode();
u.x = x;
r = merge(u, r);
r.parent = nil;
n++;
return true;
}
This takesO(log( n+ 1)) =O(logn) expected time.
Theremove () operation is similarly easy. The node we want to remove
is the root, so we just merge its two children and make the result the root:
MeldableHeap
T remove() {
T x = r.x;
r = merge(r.left, r.right);
if (r != nil) r.parent = nil;
n--;
return x;
}
Again, this takes O(logn) expected time.
Additionally, a MeldableHeap can implement many other operations
inO(logn) expected time, including:
•remove (u): remove the node u(and its key u:x) from the heap.
•absorb (h): add all the elements of the MeldableHeap h to this heap,
emptying hin the process.
Each of these operations can be implemented using a constant number of
merge (h1;h2) operations that each take O(logn) expected time.
219

（中文关键词：堆、随机）
