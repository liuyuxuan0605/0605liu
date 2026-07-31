---
structure: BTree
source: book_zh/ods_zh_14_1.md
chapter: 14. External Memory Searching
section: 14.1
page: 299
kind: textbook
---

# 14.1 块存储

外部存储的概念包括大量可能的不同设备，每种设备都有自己的块大小，
并通过自己的一组系统调用进行访问。为了简化本章的阐述，以便我们能
够专注于共同的理念，我们使用一个称为 BlockStore 的对象来封装外部存
储设备。BlockStore 存储一组内存块，每个块的大小为 B。每个块由其整
数索引唯一标识。BlockStore 支持以下操作：
1. readBlock(i)：返回索引为 i 的区块的内容。
2. writeBlock(i, b)：将 b 的内容写入索引为 i 的块。 3. placeBlock(b)：
返回一个新的索引，并将 b 的内容存储在该索引处。 4. freeBlock(i)：
释放索引为 i 的块。这表示该块的内容不再使用，因此该块分配的外部
内存可以被重新使用。
想象 BlockStore 最简单的方式是把它想象成在磁盘上存储一个文件，
该文件被分成若干个块，每个块包含 B 字节。这样，readBlock(i) 和 write
Block(i, b) 只是简单地读取和写入该文件的字节 iB, . . . , (i + 1)B 1。另外
−
，一个简单的 BlockStore 可以维护一个可用块的 free list。使用 freeBlock(
i) 释放的块会被添加到空闲列表中。这样，placeBlock(b) 可以使用空闲列
表中的块，或者如果没有可用块，则在文件末尾追加一个新块。

（英文术语：BTree）
