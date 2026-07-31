---
structure: BTree
source: book/ods_14_1_the-block-store.md
chapter: 14. External Memory Searching
section: 14.1
page: 299
kind: textbook
---

# 14.1 The Block Store

The notion of external memory includes a large number of possible differ-
ent devices, each of which has its own block size and is accessed with its
own collection of system calls. To simplify the exposition of this chapter
so that we can focus on the common ideas, we encapsulate external mem-
ory devices with an object called a BlockStore. A BlockStore stores a
collection of memory blocks, each of size B. Each block is uniquely iden-
tified by its integer index. A BlockStore supports these operations:
1. readBlock(i): Return the contents of the block whose index is i.
2. writeBlock(i, b): Write contents of b to the block whose index is i.
3. placeBlock(b): Return a new index and store the contents of b at
this index.
4. freeBlock(i): Free the block whose index is i. This indicates that
the contents of this block are no longer used so the external memory
allocated by this block may be reused.
The easiest way to imagine a BlockStore is to imagine it as storing
a file on disk that is partitioned into blocks, each containing B bytes. In
this way, readBlock(i) and writeBlock(i, b) simply read and write bytes
iB, . . . , (i + 1)B 1 of this file. In addition, a simple BlockStore could
−
keep a free list of blocks that are available for use. Blocks freed with
freeBlock(i) are added to the free list. In this way, placeBlock(b) can
use a block from the free list or, if none is available, append a new block
to the end of the file.

（中文关键词：外存）
