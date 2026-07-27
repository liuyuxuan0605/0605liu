---
structure:
source: open/ods_p297.md
page: 297
---

# ODS p297: Chapter 14

Chapter 14
External Memory Searching
Throughout this book, we have been using the w-bit word-RAM model of
computation deﬁned in Section 1.4. An implicit assumption of this model
is that our computer has a large enough random access memory to store
all of the data in the data structure. In some situations, this assumption
is not valid. There exist collections of data so large that no computer has
enough memory to store them. In such cases, the application must resort
to storing the data on some external storage medium such as a hard disk,
a solid state disk, or even a network ﬁle server (which has its own external
storage).
Accessing an item from external storage is extremely slow. The hard
disk attached to the computer on which this book was written has an aver-
age access time of 19ms and the solid state drive attached to the computer
has an average access time of 0.3ms. In contrast, the random access mem-
ory in the computer has an average access time of less than 0.000113ms.
Accessing RAM is more than 2 500 times faster than accessing the solid
state drive and more than 160 000 times faster than accessing the hard
drive.
These speeds are fairly typical; accessing a random byte from RAM is
thousands of times faster than accessing a random byte from a hard disk
or solid-state drive. Access time, however, does not tell the whole story.
When we access a byte from a hard disk or solid state disk, an entire block
of the disk is read. Each of the drives attached to the computer has a
block size of 4 096; each time we read one byte, the drive gives us a block
containing 4 096 bytes. If we organize our data structure carefully, this
283

（中文关键词：排序、随机）
