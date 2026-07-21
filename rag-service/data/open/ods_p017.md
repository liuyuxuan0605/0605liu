---
structure:
source: open/ods_p017.md
page: 17
---

# ODS p17: The Need for E ﬃciency §1.1

The Need for E ﬃciency §1.1
means that this application will take at least 1012=109= 1000 seconds, or
roughly 16 minutes and 40 seconds. Sixteen minutes is an eon in com-
puter time, but a person might be willing to put up with it (if he or she
were headed out for a co ﬀee break).
Bigger data sets: Now consider a company like Google, that indexes
over 8.5 billion web pages. By our calculations, doing any kind of query
over this data would take at least 8.5 seconds. We already know that this
isn’t the case; web searches complete in much less than 8.5 seconds, and
they do much more complicated queries than just asking if a particular
page is in their list of indexed pages. At the time of writing, Google re-
ceives approximately 4 ;500 queries per second, meaning that they would
require at least 4 ;5008:5 = 38;250 very fast servers just to keep up.
The solution: These examples tell us that the obvious implementations
of data structures do not scale well when the number of items, n, in the
data structure and the number of operations, m, performed on the data
structure are both large. In these cases, the time (measured in, say, ma-
chine instructions) is roughly nm.
The solution, of course, is to carefully organize data within the data
structure so that not every operation requires every data item to be in-
spected. Although it sounds impossible at ﬁrst, we will see data struc-
tures where a search requires looking at only two items on average, in-
dependent of the number of items stored in the data structure. In our
billion instruction per second computer it takes only 0 :000000002 sec-
onds to search in a data structure containing a billion items (or a trillion,
or a quadrillion, or even a quintillion items).
We will also see implementations of data structures that keep the
items in sorted order, where the number of items inspected during an
operation grows very slowly as a function of the number of items in the
data structure. For example, we can maintain a sorted set of one billion
items while inspecting at most 60 items during any operation. In our bil-
lion instruction per second computer, these operations take 0 :00000006
seconds each.
The remainder of this chapter brieﬂy reviews some of the main con-
cepts used throughout the rest of the book. Section 1.2 describes the in-
3

（中文关键词：排序）
