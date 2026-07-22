---
structure: SegmentTree
kind: theory
operation: mixed
phase: concept
difficulty: medium
---

# SegmentTree 知识点（理论讲解，来源 VisuAlgo）

## Segment Tree

A Segment Tree (ST) is a binary tree that is build on top of an (usually Integer) array so that we can solve the Range Min/Max/Sum (other variants are possible) Query (abbreviated as
RMinQ/RMaxQ/RSumQ)
as well as any Range (that includes Point) Update Query of this array in O(log
N
) time instead of the naive O(
N
) time. Given an array A of
N
(usually Integer) elements, we can build the corresponding RMinQ/RMaxQ/RSumQ Segment Tree in O(
N
) time.

## Modes

To toggle between the RMinQ/RMaxQ/RSumQ Segment Tree, select the respective header. Note that there can be other type of range queries than the three classics shown in this visualization.

## Visualization - Top Side

View the visualization of Segment Tree (tree on top of an array) here!
The tree on the top side shows the Segment Tree structure. The vertices are indexed in the same manner as with
Binary Heap
data structure where the root is at index 1 and the left/right child of a vertex
p
is
2*p
/
2*p+1
, respectively. The value inside each vertex shows the MinIndex/MaxIndex/Sum value of the corresponding range/segment
[L,R]
of the underlying array
A
. We put
"
p:[L,R]
" identifier in red color
below each vertex except when
L=R
and that segment corresponds to a single array index (only that index is shown).
Vertices that are lazily updated will have this
purple ring highlight
. This lazy update technique will be explained in subsequent slides.

## Visualization - Bottom Side

The bottommost row shows the content of the underlying array
A
(
yellow colored
) from which the Segment Tree structure is built.
Each leaf vertex in the Segment Tree corresponds to an individual index in the corresponding array A. For Min ST and Max ST, the leaf vertex in the Segment Tree contains the index itself (the minimum/maximum element of a subarray with just one element is that element itself). For Sum ST, the leaf vertex in the Segment Tree contains the only value of that single-element subarray.

## Operations

There are three basic operations that are available in Segment Tree data structure visualization (for all 3 modes: RMinQ/RMaxQ/RSumQ):
You can create RMinQ/RMaxQ/RSumQ Segment Tree from either a user-defined array of integers (maximum of 16 two-digits integer), or let the system provide a small random integer array or a small random but sorted integer array.
You can do RMinQ/RMaxQ/RSumQ by specifying a left (L) and a right (R) indices.
You can do Range Update by specifying a left (L) index, a right (R) index, and a new VALUE for this range [L,R]. We employ lazy update strategy for fast performance. You can still do Point Update (updating a single index only) by setting L = R.
For the details of these three operations, read CP4 or attend live CS3233 class.

## Implementation

Unfortunately, this data structure is not yet available in C++ STL, Python, Java API, or OCaml Standard Library as of 2024. Therefore, we have to write our own implementation.
Please look at the following C++/Python/Java/OCaml implementations of this Segment Tree data structure in Object-Oriented Programming (OOP) fashion:
segmenttree_ds.cpp
|
py
|
java
|
ml
Again, you are free to customize this custom library implementation to suit your needs.
