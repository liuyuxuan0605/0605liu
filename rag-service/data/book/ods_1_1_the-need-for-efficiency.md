---
structure: 
source: book/ods_1_1_the-need-for-efficiency.md
chapter: 1. Introduction
section: 1.1
page: 16
kind: textbook
---

# 1.1 The Need for Efficiency

## The Need for Efficiency (1/3)

In the next section, we look at the operations supported by the most com-
monly used data structures. Anyone with a bit of programming experi-
ence will see that these operations are not hard to implement correctly.
We can store the data in an array or a linked list and each operation can
be implemented by iterating over all the elements of the array or list and
possibly adding or removing an element.
This kind of implementation is easy, but not very efficient. Does this
really matter? Computers are becoming faster and faster. Maybe the ob-
vious implementation is good enough. Let’s do some rough calculations
to find out.
Number of operations: Imagine an application with a moderately-sized
data set, say of one million (106), items. It is reasonable, in most appli-
cations, to assume that the application will want to look up each item
at least once. This means we can expect to do at least one million (106)
searches in this data. If each of these 106 searches inspects each of the
106 items, this gives a total of 106 106 = 1012 (one thousand billion)
×
inspections.
Processor speeds: At the time of writing, even a very fast desktop com-
puter can not do more than one billion (109) operations per second.1 This
1Computer speeds are at most a few gigahertz (billions of cycles per second), and each
operation typically takes a few cycles.
means that this application will take at least 1012/109 = 1000 seconds, or
roughly 16 minutes and 40 seconds. Sixteen minutes is an eon in com-
puter time, but a person might be willing to put up with it (if he or she
were headed out for a coffee break).

（中文关键词：数组、链表）

## The Need for Efficiency (2/3)

Bigger data sets: Now consider a company like Google, that indexes
over 8.5 billion web pages. By our calculations, doing any kind of query
over this data would take at least 8.5 seconds. We already know that this
isn’t the case; web searches complete in much less than 8.5 seconds, and
they do much more complicated queries than just asking if a particular
page is in their list of indexed pages. At the time of writing, Google re-
ceives approximately 4, 500 queries per second, meaning that they would
require at least 4, 500 8.5 = 38, 250 very fast servers just to keep up.
×
The solution: These examples tell us that the obvious implementations
of data structures do not scale well when the number of items, n, in the
data structure and the number of operations, m, performed on the data
structure are both large. In these cases, the time (measured in, say, ma-
chine instructions) is roughly n m.
×
The solution, of course, is to carefully organize data within the data
structure so that not every operation requires every data item to be in-
spected. Although it sounds impossible at first, we will see data struc-
tures where a search requires looking at only two items on average, in-
dependent of the number of items stored in the data structure. In our
billion instruction per second computer it takes only 0.000000002 sec-
onds to search in a data structure containing a billion items (or a trillion,
or a quadrillion, or even a quintillion items).
We will also see implementations of data structures that keep the
items in sorted order, where the number of items inspected during an
operation grows very slowly as a function of the number of items in the
data structure. For example, we can maintain a sorted set of one billion
items while inspecting at most 60 items during any operation. In our bil-
lion instruction per second computer, these operations take 0.00000006
seconds each.
The remainder of this chapter briefly reviews some of the main con-
cepts used throughout the rest of the book. Section 1.2 describes the in-
terfaces implemented by all of the data structures described in this book
and should be considered required reading. The remaining sections dis-
cuss:
• some mathematical review including exponentials, logarithms, fac-
torials, asymptotic (big-Oh) notation, probability, and randomiza-
tion;
• the model of computation;
• correctness, running time, and space;
• an overview of the rest of the chapters; and
• the sample code and typesetting conventions.

（中文关键词：概率）

## The Need for Efficiency (3/3)

A reader with or without a background in these areas can easily skip them
now and come back to them later if necessary.
