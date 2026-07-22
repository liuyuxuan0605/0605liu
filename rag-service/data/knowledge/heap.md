---
structure: Heap
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# Heap 知识点（理论讲解，来源 VisuAlgo）

## Binary (Max) Heap

A Binary (Max) Heap is a
complete binary tree
that maintains the
Max Heap property
.
Binary Heap is one possible data structure to model an efficient
Priority Queue
(PQ) Abstract Data Type (ADT). In a PQ, each element has a "priority" and an element with higher priority is served before an element with lower priority (ties are either simply resolved arbitrarily or broken with standard First-In First-Out (FIFO) rule as with a normal Queue). Try clicking
ExtractMax()
for a sample animation on extracting the max value of random Binary Heap above.
To focus the discussion scope, this visualization show a Binary
Max
Heap of integers where duplicates are allowed. See
this
for an easy conversion to Binary
Min
Heap. Generally, any other objects that can be compared can be stored in a Binary Max Heap, e.g., Binary Max Heap of floating points, etc.

## Definitions

Complete Binary Tree
: Every level in the binary tree, except possibly the last/lowest level, is completely filled, and all vertices in the last level are as far left as possible.
Binary Max Heap property
: The parent of each vertex - except the root - contains value greater than (or equal to — we now allow duplicates) the value of that vertex. This is an easier-to-verify definition than the following alternative definition: The value of a vertex - except the leaf/leaves - must be greater than (or equal to) the value of its one (or two) child(ren).

## Priority Queue ADT

Priority Queue (PQ) Abstract Data Type (ADT) is similar to normal Queue ADT, but with these two major operations:
Enqueue(
x
): Put a new element (key)
x
into the PQ (in some order),
y
= Dequeue(): Return an existing element
y
that has the highest priority (key) in the PQ and if ties, return any.
Discussion: Some PQ ADT reverts to First-In First-Out (FIFO) behavior of a normal
Queue
in the event there is a tie of highest priority (key) in the PQ. Does guaranteeing stability on equal highest priority (key) makes PQ ADT harder to implement?

## Stability of Equal Highest Key

To maintain stability if there are equal keys, we probably need to attach extra information (arrival time/arrival index) of each key, so that the comparison function can take the one with earlier arrival time first. Without this extra information, there is no guarantee of stability in the standard Binary Heap implementation.

## Example

Imagine: You are an
Air Traffic Controller (ATC)
working in the control tower
T
of an airport. You have scheduled aircraft
X
/
Y
to land in the next 3/6 minutes, respectively. Both have enough fuel for at least the next 15 minutes and both are just 2 minutes away from your airport. You observe that your airport runway is clear at the moment.
In case you do not know, aircraft can be instructed to fly in
holding pattern
near the airport until the designated landing time.

## For Live Lecture @ NUS Only

You have to attend the live lecture to figure out what happens next...
There will be two options presented to you and you will have to decide:
Raise AND wave your hand if you choose option A,
Raise your hand but do NOT wave it if you choose option B,
If none of the two options is reasonable for you, simply do nothing.

## The Example - Continued

Suddenly, you receive an urgent SOS message that another aircraft
Z
is running out of fuel and request to land soon. The pilot of aircraft
Z
estimates that he only have 3 minutes of flying time and also approximately 3 minutes away from your airport...
Quiz:
You...
Option A: Let aircraft
Z
lands first and hold
X
and
Y
...
Option B: Stick with the original plan…
Submit
History:
Avianca Flight 52
.

## PQ Examples

There are several potential usages of PQ ADT in real-life on top of what you have seen just now regarding ATC (only in live lecture).
Discussion: Can you mention a few other real-life situations where a PQ is needed?

## Potential Answers

Emergency situation in a Hospital prioritizing urgent cases (triage),
Priority lanes for pregnant women and senior citizens in public places,
Call center (priority) queue management, e.g., emergency-related calls (995 in Singapore, 911 in the Americas, etc) are prioritised,
Priority (more expensive, usually limited per day) tickets in amusement parks,
Stock market trading where higher priority/value transactions are prioritized,
Etc

## Linear DS for PQ?

We are able to implement this PQ ADT using (circular)
Array
or
Linked List
but we will have slow (i.e., in O(
N
)) Enqueue or Dequeue operation.
Discussion: Why?

## The Answer - Part 1

There are two strategies using (circular) Array or Linked List implementation.
Strategy 1 maintains this property: The content of array/linked list is always in correct order, i.e. from higher priority elements to lower priority elements.
Enqueue(x) requires lots of work as we have to scan the PQ from front to back in O(
N
) to find the correct insertion point and make a space (if using array) – recall
Insertion Sort
.
But y = Dequeue() is just O(
1
) as we can just return the front-most element  (front of circular array or head of a Linked List) which has the highest priority.

## The Answer - Part 2

Strategy 2 maintains another property: Dequeue() operation returns the correct element.
Enqueue(x) can be made simple. We simply put the new element at the back of the PQ (back of circular array or back of a Linked List), O(
1
).
y = Dequeue() requires lots of work as we need to scan the whole PQ from front to back in O(
N
) to correctly return the first element with highest priority and close the gap (if using array).
We see that both strategies have inefficient O(
N
) operation in it. We will soon see one possible data structure that allows us to implement both Enqueue and Dequeue operations in much more efficient O(log
N
) time: Binary Heap.

## Visualisation + Max Heap Property

Now, let's view the visualisation of a (random) Binary (Max) Heap above. You should see a complete binary tree and all vertices except the root satisfy the Max Heap property (A[parent(i)] ≥ A[i]). Duplicate integer keys may appear (note that the
stability
of equal keys is not guaranteed).
You can
Toggle the Visualization Mode
between the visually more intuitive complete binary tree form or the compact array based implementation of a Binary (Max) Heap.
Quiz:
Based on this Binary (Max) Heap property, where will the largest integer be located?
At one of the leaf
Can be anywhere
At the root
Submit

## Binary Heap has O(log N) Height

Important fact to memorize at this point: If we have a Binary Heap of
N
elements, its height will not be taller than O(log
N
) since we will store it as a complete binary tree.
Simple analysis: The size
N
of a full (more than just a complete) binary tree of height
h
is always
N = 2
(h+1)
-1
, therefore
h = log
2
(N+1)-1 ~= log
2
N
.
See example above with
N = 7 = 2
(2+1)
-1
or
h = log
2
(7+1)-1 = 2
.
This fact is important in the analysis of all Binary Heap-related operations.

## 1-based Compact Array

A complete binary tree can be stored efficiently as a compact array A as there is no gap between vertices of a complete binary tree/elements of a compact array. To simplify the navigation operations below, we use 1-based array. VisuAlgo displays the index of each vertex as a
red label
below each vertex. Read those indices in sorted order from 1 to
N
, then you will see the vertices of the complete binary tree from top to down, left to right. To help you understand this,
Toggle the Visualization Mode
several times.
This way, we can implement basic binary tree traversal operations with simple index manipulations (with help of
bit shift manipulation
):
parent(i) = i>>1, index i divided by 2 (integer division),
left(i) = i<<1, index i multiplied by 2,
right(i) = (i<<1)+1, index i multiplied by 2 and added by 1.
Pro tip: Try opening two copies of VisuAlgo on two browser windows. Try to visualize the same Binary Max Heap in two different modes and compare them.

## Binary (Max) Heap Operations

In this visualization, you can perform several Binary (Max) Heap operations:
Create(A)
- O(
N
log
N
) version (
N
calls of
Insert(v)
below)
Create(A)
- O(
N
) version
Insert(v)
in O(log
N
) — you are allowed to insert duplicates
3 versions of
ExtractMax()
:
Once, in O(log
N
)
K
times, i.e.,
PartialSort()
, in O(
K
log
N
), or
N
times, i.e.,
HeapSort()
, in O(
N
log
N)
UpdateKey(i, newv)
in O(log
N
if
i
is known)
Delete(i)
in O(log
N
if
i
is known)
There are a few other possible Binary (Max) Heap operations, but currently we do not elaborate them for pedagogical reason in a certain NUS module.

## What Are The Extra Operations?

For NUS students only:
Increase/Decrease/UpdateKey(old_v, new_v),
DeleteKey(v) — v is not necessarily the max element,
ExtractMin() and ExtractMax() on the same priority queue.

## Insert(v)

Insert(v)
: Insertion of a new item
v
into a Binary Max Heap can only be done at the
last index
N
plus 1
to maintain the compact array = complete binary tree property. However, the Max Heap property
may
still be violated. This operation then fixes Max Heap property from the insertion point
upwards
(if necessary) and stop when there is no more Max Heap property violation. Now try clicking
Insert(v)
several times to insert a few random
v
to the currently displayed Binary (Max Heap).
The fix Max Heap property upwards operation has no standard name. We call it
ShiftUp
but others may call it
BubbleUp
or
IncreaseKey
operation.

## Why it is Correct?

Do you understand why starting from the insertion point (index
N
+1) upwards (at most until the root) and swapping a vertex with its parent when there is a Max Heap property violation during insertion is always a correct strategy?

## The Answer

Think about Max Heap property before and after such swap (vertex
x
and its parent
y
has value
A[y] < A[x]
), you should see that such swap fixes the Max Heap property between swapped vertices (
A[y] > A[x]
afterwards).

## Time Complexity Analysis

The time complexity of this
Insert(v)
operation is O(log
N
).
Discussion: Do you understand the derivation?

## The Answer

Analysis: The worst case of
Insert(v)
is when we insert a new element
v
that is greater than the value of the current root. Such insertion causes
Insert(v)
to fix Max Heap property from a leaf up to the root and therefore runs in O(log
N
) as a complete binary tree can never be taller than O(log
N
). Now try
Insert(v) - Extreme
where we will insert a new element that is always 1 more than the current root.

## ExtractMax() - Once

ExtractMax()
: The reporting and then the deletion of the maximum element (the root) of a Binary Max Heap requires an existing element to replace the root, otherwise the Binary Max Heap (a single complete binary tree, or 林/Lín in Chinese/tree) becomes two disjoint subtrees (two copies of 木/mù in Chinese/wood). That element must be the
last index
N
for the same reason: To maintain the compact array = complete binary tree property.
Because we promote a leaf vertex to the root vertex of a Binary Max Heap, it will very likely violates the Max Heap property. ExtractMax() operation then fixes Binary Max Heap property from the root
downwards
by comparing the current value with the its child/the larger of its two children (if necessary). Now try
ExtractMax()
on the currently displayed Binary (Max) Heap.
The fix Max Heap property downwards operation has no standard name. We call it
ShiftDown
but others may call it
BubbleDown
or
Heapify
operation.

## Why Compare with the Larger Child?

Why if a vertex has two children, we have to check (and possibly swap) that vertex with
the larger
of its two children during the downwards fix of Max Heap property?
Why can't we just compare with the left (or right, if exists) vertex only?

## The Answer

You can construct a simple counterexample that comparing with left vertex only (or right vertex only) can produce wrong answer, try extracting 4 out of Binary (Max) Heap [4,2,3,1], see the ASCII art below.
4
/ \
2   3
/
1
When 4 is extracted and vertex with value 1 becomes the new root, what happens if 1 does NOT swap with max(2, 3) = 3 but swap with 2 instead?

## Time Complexity Analysis

The time complexity of this
ExtractMax()
operation is O(log
N
).
Discussion: Do you understand the derivation?

## The Answer

Analysis: This operation also runs in O(log
N
) as in the worst case, the last vertex (a leaf) happens to have the smallest value, try [9,8,7,6,5,4,3,2,1], see the ASCII art below.
9
/     \
8       7
/ \     / \
6   5   4   3
/ \
2   1
When the last existing leaf with value 1 is promoted to the root (replacing 9), it will eventually trickle back to one of the leaf via a path that has up to O(log
N
) edges.

## Binary Heap for Efficient PQ

Up to here, we have a data structure that can implement the two major operations of Priority Queue (PQ) ADT efficiently:
For
Enqueue(x)
, we can use
Insert(x)
in O(log
N
) time, and
For
y
= Dequeue(), we can use
y = ExtractMax()
in O(log
N
) time.
However, we can do a few more operations with Binary Heap.

## Create(A) - Two Versions

Create(A)
: Creates a valid Binary (Max) Heap from an input array
A
of
N
integers (comma separated) into an initially empty Binary Max Heap.
There are two variants for this operations, one that is simpler but runs in O(
N
log
N
) and a more advanced technique that runs in O(
N
).
Pro tip: Try opening two copies of VisuAlgo on two browser windows. Execute different Create(A) versions on the worst case 'Sorted example' to see the
somewhat dramatic
differences of the two.

## Create(A) - O(N log N)

Create(A) - O(N log N)
: Simply insert (that is, by calling
Insert(v)
operation) all
N
integers of the input array into an initially empty Binary Max Heap one by one.
Analysis
: This operation is clearly O(
N
log
N
) as we call O(log
N
)
Insert(v)
operation
N
times. Let's examine the 'Sorted example' which is one of the hard case of this operation (Now try the
Hard Case - O(N log N)
where we show a case where
A = [1,2,3,4,5,6,7]
-- please be patient as this example will take some time to complete). If we insert values in increasing order into an initially empty Binary Max Heap, then every insertion triggers a path from the insertion point (a new leaf) upwards to the root.

## Create(A) - O(N)

Create(A) - O(N)
: This faster version of
Create(A)
operation was invented by Robert W. Floyd in 1964. It takes advantage of the fact that a compact array = complete binary tree and all leaves (i.e., half of the vertices — see the next slide) are Binary Max Heap by default. This operation then fixes Binary Max Heap property (if necessary) only from the last internal vertex back to the root.
Analysis
: A loose analysis gives another O(
N
/2 log
N
) = O(
N
log
N
) complexity but it is actually just O(2*
N
) = O(
N
) — details
here
. Now try the
Hard Case - O(N)
on the same input array
A = [1,2,3,4,5,6,7]
and see that on the same hard case as with the previous slide (but not the one that generates maximum number of swaps — try 'Diagonal Entry' test case), this operation is far superior than the O(
N
log
N
) version.

## Many Leaf Vertices

Simple explanation on why half of Binary (Max) Heap of
N
(without loss of generality, let's assume that
N
is even) elements are leaves are as follows:
Suppose that the last leaf is at index
N
, then the parent of that last leaf is at index
i = N/2
(remember
this slide
). The left child of vertex
i+1
, if exists (it actually does not exist), will be
2*(i+1) = 2*(N/2+1) = N+2
, which exceeds index
N
(the last leaf) so index
i+1
must also be a leaf vertex that has no child. As Binary Heap indexing is consecutive, basically indices [
i+1 = N/2+1
,
i+2 = N/2+2
, ...,
N
], or half of the vertices, are leaves.

## HeapSort()

HeapSort()
: John William Joseph Williams invented
HeapSort()
algorithm in 1964, together with this Binary Heap data structure.
HeapSort()
operation (assuming the Binary Max Heap has been created in O(
N
)) is very easy. Simply call the O(log
N
)
ExtractMax()
operation
N
times. Now try
HeapSort()
on the currently displayed Binary (Max) Heap.
Simple Analysis
:
HeapSort()
clearly runs in O(
N
log
N
) — an optimal comparison-based sorting algorithm.
Quiz:
In worst case scenario, HeapSort() is asymptotically faster than...
Selection Sort
Merge Sort
Insertion Sort
Bubble Sort
Submit

## Discussion

Although
HeapSort()
runs in θ(
N
log
N
) time for all (best/average/worst) cases, is it really the best
comparison-based
sorting algorithm?
Discussion: How about caching performance of
HeapSort()
?

## The Answer

HeapSort() actually has a rather bad caching performance as it does not utilize array locality well.
Notice that the index i and its parent(i) differ by factor of 2 and similarly between index i and either its left(i)/right(i) child.

## Extras

You have reached the end of the basic stuffs of this Binary (Max) Heap data structure and we encourage you to explore further in the
Exploration Mode
.
However, we still have a few more interesting Binary (Max) Heap challenges for you that are outlined in this section.
When you have cleared them all, we invite you to study more advanced algorithms that use Priority Queue as (one of) its underlying data structure, like
Prim's MST algorithm
,
Dijkstra's SSSP algorithm
, A* search algorithm (not in VisuAlgo yet), a few other greedy-based algorithms, etc.

## Create(A) - O(N) Analysis (1)

Earlier
, we have seen that we can create Binary Max Heap from a random array of size
N
elements in O(
N
) instead of O(
N
log
N
). Now, we will properly analyze this tighter bound.
First, we need to recall that the height of a full binary tree of size
N
is log
2
N
.
Second, we need to realise that the cost to run
shiftDown(i)
operation is not the gross upper bound O(log
N
), but O(
h
) where
h
is the height of the subtree rooted at
i
.
Third, there are
ceil(N/2
h+1
)
vertices at height
h
in a full binary tree.
On the example full binary tree above with
N = 7
and
h = 2
, there are:
ceil(7/2
0+1
) = 4
vertices: {44,35,26,17} at height
h = 0
,
ceil(7/2
1+1
) = 2
vertices: {62,53} at height
h = 1
, and
ceil(7/2
2+1
) = 1
vertex: {71} at height
h = 2
.

## Create(A) - O(N) Analysis (2)

Cost of Create(A), the O(
N
) version is thus:
PS: If the formula is too complicated, a modern student can also use
WolframAlpha
instead.

## PartialSort()

The faster O(
N
) Create Max Heap from a random array of
N
elements is important for getting a faster solution if we only need top
K
elements out of
N
items, i.e.,
PartialSort()
.
After O(
N
) Create Max Heap, we can then call the O(log
N
)
ExtractMax()
operation
K
times to get the top
K
largest elements in the Binary (Max) Heap. Now try
PartialSort()
on the currently displayed Binary (Max) Heap.
Analysis
:
PartialSort()
clearly runs in O(
N + K
log
N
) — an output-sensitive algorithm where the time complexity depends on the output size
K
. This is faster than the
lower-bound of O(
N
log
N
)
if we fully sort the entire
N
elements when
K < N
.

## Easy Max to Min Heap Conversion

If we only deal with numbers (including this visualization that is restricted to integers only), it is easy to convert a Binary Max Heap into a Binary Min Heap without changing anything, or vice versa.
We can re-create a Binary Heap with the negation of every integer in the original Binary Heap. If we start with a Binary Max Heap, the resulting Binary Heap is a Binary Min Heap (if we ignore the negative symbols — see the picture above), and vice versa.

## UpdateKey(i, newv)

For some Priority Queue applications (e.g.,
HeapDecreaseKey in Dijkstra's algorithm
), we may have to modify (increase or decrease) the priority of an existing value that is already inserted into a Binary (Max) Heap. If the index
i
of the value is known, we can do the following simple strategy: Simply update
A[i] = newv
and then call
both
shiftUp(i)
and
shiftDown(i)
. Only at most one of this Max Heap property restoration operation will be successful, i.e.,
shiftUp(i)
/
shiftDown(i)
will be triggered if
newv
>/< old value of
A[parent(i)]
/
A[larger of the two children of i]
, respectively.
Thus,
UpdateKey(i, newv)
can be done in O(log
N
), provided we know index
i
.

## Delete(i)

For some Priority Queue applications, we may have to delete an existing value that is already inserted into a Binary (Max) Heap (and this value happens to be not the root). Again, if the index
i
of the value is known, we can do the following simple strategy: Simply update
A[i] = A[1]+1
(a larger number greater than the current root), call
shiftUp(i)
(technically,
UpdateKey(i, A[1]+1)
). This will floats index
i
to be the new root, and from there, we can easily call
ExtractMax()
once to remove it.
Thus,
Delete(i)
can be done in O(log
N
), provided we know index
i
.
Discussion: Now for
UpdateKey(i, newv)
and
Delete(i)
, what if we are given
oldv
instead and thus we have to search for its location in the Binary (Max) Heap? Can we do this faster than O(
N
)?

## The Answer

We still can, at the expense of more complex solution. We can use an additional separate Hash Table to map any value to its index in the Binary (Max) Heap. This way, the "search" can be done via O(
1
) hashing instead.

## Stability Issue

If there are duplicate keys, the standard implementation of Binary Heap as shown in this visualization does not guarantee stability. For example, if we insert three copies of {7, 7, 7}, e.g., {7a, 7b, and 7c} (suffix a, b, c are there only for clarity), in that order, into an initially empty Binary (Max) Heap. Then, upon first extraction, the root (7a) will be extracted first and the last existing leaf (7c) will replaces 7a. As 7c and 7b (without the suffixes) are equal (7 and 7), there is no swap happening and thus the second extract max will take out 7c instead of 7b first —
not stable
.
If we really need to guarantee stability of equal elements, we probably need to attach different suffixes as shown earlier to make those identical elements to be unique again.

## Source Code

If you are looking for an implementation of Binary (Max) Heap to actually model a Priority Queue, then there is a good news.
C++ and Java already have built-in Priority Queue implementations that very likely use this data structure. They are
C++ STL priority_queue
(the default is a Max Priority Queue) and
Java PriorityQueue
(the default is a Min Priority Queue). However, the built-in implementation may not be suitable to do some PQ extended operations efficiently (details omitted for pedagogical reason in a certain NUS course).
Python
heapq
exists but its performance is rather slow. OCaml doesn't have built-in Priority Queue but we can use something else that is going to be mentioned in the other modules in VisuAlgo (the reason on why the details are omitted is the same as above).
PS: Heap Sort is likely used in C++ STL algorithm
partial_sort
.
Nevertheless, here is our implementation of
BinaryHeapDemo.cpp
|
py
|
java
.

## Online Quiz

For a few more interesting questions about this data structure, please practice on
Binary Heap
training module (no login is required).
However, for NUS students, you should login using your official class account, officially clear this module, and such achievement will be recorded in your user account.

## Online Judge Exercises

We also have a few programming problems that somewhat requires the usage of this Binary Heap data structure:
UVa 01203 - Argus
and
Kattis - numbertree
.
Try them to consolidate and improve your understanding about this data structure. You are allowed to use C++ STL priority_queue, Python heapq, or Java PriorityQueue if that simplifies your implementation.

## Discussion

For
UVa 01203 - Argus
, consider using PQ ADT to simulate the process in O(
K
log
#Register
) time.
For
Kattis - numbertree
, stare at
this slide
very carefully.

## Shocking Stuff

After spending one long lecture on Binary (Max) Heap, here is a jaw-dropping moment...
Binary (Max) Heap data structure is probably
not
the best data structure to implement (certain operations of) ADT Priority Queue...
Discussion: So what is the alternative data structure?

## The Answer

The main motivation of this lecture is that we need a data structure to implement Priority Queue ADT efficiently.
Now we tell you that there is an
alternative (click this link)
data structure that can also be used to implement Priority Queue ADT and that data structure is actually more versatile...
Think about it, what if we need fast, i.e., in O(log
N
) for all these: the standard
Insert(v)
operation, both the
ExtractMax()
+
ExtractMin()
operations, the
UpdateKey(oldv, newv)
operation, and/or the
Delete(oldv)
operation — with just one single data structure?
Study that alternative data structure and think how that alternative data structure can support all those operations all in O(log
N
) easily.
