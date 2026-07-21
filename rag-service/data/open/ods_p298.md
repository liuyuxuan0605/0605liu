---
structure:
source: open/ods_p298.md
page: 298
---

# ODS p298: §14 External Memory Searching

§14 External Memory Searching
x
diskRAM
External MemoryxxCPU
Figure 14.1: In the external memory model, accessing an individual item, x, in
the external memory requires reading the entire block containing xinto RAM.
means that each disk access could yield 4 096 bytes that are helpful in
completing whatever operation we are doing.
This is the idea behind the external memory model of computation, il-
lustrated schematically in Figure 14.1. In this model, the computer has
access to a large external memory in which all of the data resides. This
memory is divided into memory blocks each containing Bwords. The
computer also has limited internal memory on which it can perform com-
putations. Transferring a block between internal memory and external
memory takes constant time. Computations performed within the in-
ternal memory are free; they take no time at all. The fact that internal
memory computations are free may seem a bit strange, but it simply em-
phasizes the fact that external memory is so much slower than RAM.
In the full-blown external memory model, the size of the internal
memory is also a parameter. However, for the data structures described
in this chapter, it is su ﬃcient to have an internal memory of size O(B+
logBn). That is, the memory needs to be capable of storing a constant
number of blocks and a recursion stack of height O(logBn). In most cases,
theO(B) term dominates the memory requirement. For example, even
with the relatively small value B= 32,BlogBnfor all n2160. In deci-
284

（中文关键词：栈）
