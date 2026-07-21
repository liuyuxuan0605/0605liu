---
structure:
source: open/ods_p016.md
page: 16
---

# ODS p16: §1.1 Introduction

§1.1 Introduction
over 8.5 billion web pages on the Internet and each page contains a
lot of potential search terms.
• Phone emergency services (9-1-1): The emergency services network
looks up your phone number in a data structure that maps phone
numbers to addresses so that police cars, ambulances, or ﬁre trucks
can be sent there without delay. This is important; the person mak-
ing the call may not be able to provide the exact address they are
calling from and a delay can mean the di ﬀerence between life or
death.
1.1 The Need for E ﬃciency
In the next section, we look at the operations supported by the most com-
monly used data structures. Anyone with a bit of programming experi-
ence will see that these operations are not hard to implement correctly.
We can store the data in an array or a linked list and each operation can
be implemented by iterating over all the elements of the array or list and
possibly adding or removing an element.
This kind of implementation is easy, but not very e ﬃcient. Does this
really matter? Computers are becoming faster and faster. Maybe the ob-
vious implementation is good enough. Let’s do some rough calculations
to ﬁnd out.
Number of operations: Imagine an application with a moderately-sized
data set, say of one million (106), items. It is reasonable, in most appli-
cations, to assume that the application will want to look up each item
at least once. This means we can expect to do at least one million (106)
searches in this data. If each of these 106searches inspects each of the
106items, this gives a total of 106106= 1012(one thousand billion)
inspections.
Processor speeds: At the time of writing, even a very fast desktop com-
puter can not do more than one billion (109) operations per second.1This
1Computer speeds are at most a few gigahertz (billions of cycles per second), and each
operation typically takes a few cycles.
2

（中文关键词：数组、链表）
