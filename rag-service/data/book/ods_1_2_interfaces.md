---
structure: 
source: book/ods_1_2_interfaces.md
chapter: 1. Introduction
section: 1.2
page: 18
kind: textbook
---

# 1.2 Interfaces

When discussing data structures, it is important to understand the dif-
ference between a data structure’s interface and its implementation. An
interface describes what a data structure does, while an implementation
describes how the data structure does it.
An interface, sometimes also called an abstract data type, defines the
set of operations supported by a data structure and the semantics, or
meaning, of those operations. An interface tells us nothing about how
the data structure implements these operations; it only provides a list of
supported operations along with specifications about what types of argu-
ments each operation accepts and the value returned by each operation.
A data structure implementation, on the other hand, includes the inter-
nal representation of the data structure as well as the definitions of the
algorithms that implement the operations supported by the data struc-
ture. Thus, there can be many implementations of a single interface. For
example, in Chapter 2, we will see implementations of the List interface
using arrays and in Chapter 3 we will see implementations of the List
interface using pointer-based data structures. Each implements the same
interface, List, but in different ways.
x
· · ·
add(x)/enqueue(x) remove()/dequeue()
Figure 1.1: A FIFO Queue.

（中文关键词：队列、数组、双端队列）

## 1.2.1 The Queue, Stack, and Deque Interfaces (1/2)

The Queue interface represents a collection of elements to which we can
add elements and remove the next element. More precisely, the opera-
tions supported by the Queue interface are
• add(x): add the value x to the Queue
• remove(): remove the next (previously added) value, y, from the
Queue and return y
Notice that the remove() operation takes no argument. The Queue’s queue-
ing discipline decides which element should be removed. There are many
possible queueing disciplines, the most common of which include FIFO,
priority, and LIFO.
A FIFO (first-in-first-out) Queue, which is illustrated in Figure 1.1, re-
moves items in the same order they were added, much in the same way
a queue (or line-up) works when checking out at a cash register in a gro-
cery store. This is the most common kind of Queue so the qualifier FIFO
is often omitted. In other texts, the add(x) and remove() operations on a
FIFO Queue are often called enqueue(x) and dequeue(), respectively.
A priority Queue, illustrated in Figure 1.2, always removes the small-
est element from the Queue, breaking ties arbitrarily. This is similar to the
way in which patients are triaged in a hospital emergency room. As pa-
tients arrive they are evaluated and then placed in a waiting room. When
a doctor becomes available he or she first treats the patient with the most
life-threatening condition. The remove(x) operation on a priority Queue
is usually called deleteMin() in other texts.
A very common queueing discipline is the LIFO (last-in-first-out) dis-
cipline, illustrated in Figure 1.3. In a LIFO Queue, the most recently
added element is the next one removed. This is best visualized in terms
of a stack of plates; plates are placed on the top of the stack and also
remove()/deleteMin()
add(x)
3
6
x
13
16
Figure 1.2: A priority Queue.
add(x)/push(x)
x
· · ·
remove()/ pop()
Figure 1.3: A stack.
removed from the top of the stack. This structure is so common that it
gets its own name: Stack. Often, when discussing a Stack, the names
of add(x) and remove() are changed to push(x) and pop(); this is to avoid
confusing the LIFO and FIFO queueing disciplines.

（中文关键词：队列、栈、优先队列、双端队列）

## 1.2.1 The Queue, Stack, and Deque Interfaces (2/2)

A Deque is a generalization of both the FIFO Queue and LIFO Queue
(Stack). A Deque represents a sequence of elements, with a front and a
back. Elements can be added at the front of the sequence or the back of
the sequence. The names of the Deque operations are self-explanatory:
addFirst(x), removeFirst(), addLast(x), and removeLast(). It is worth
noting that a Stack can be implemented using only addFirst(x) and
removeFirst() while a FIFO Queue can be implemented using addLast(x)
and removeFirst().

（中文关键词：队列、双端队列、栈）

## 1.2.2 The List Interface: Linear Sequences

This book will talk very little about the FIFO Queue, Stack, or Deque in-
terfaces. This is because these interfaces are subsumed by the List inter-
face. A List, illustrated in Figure 1.4, represents a sequence, x , . . . , x ,
0 n 1
−
0 1 2 3 4 5 6 7 n 1
· · · −
a b c d e f b k c
· · ·
Figure 1.4: A List represents a sequence indexed by 0,1,2,..., n. In this List a
call to get(2) would return the value c.
of values. The List interface includes the following operations:
1. size(): return n, the length of the list
2. get(i): return the value x
i
3. set(i, x): set the value of x equal to x
i
4. add(i, x): add x at position i, displacing x , . . . , x ;
i n 1
−
Set x = x , for all j n 1, . . . , i , increment n, and set x = x
j+1 j i
∈ { − }
5. remove(i) remove the value x , displacing x , . . . , x ;
i i+1 n 1
−
Set x = x , for all j i, . . . , n 2 and decrement n
j j+1
∈ { − }
Notice that these operations are easily sufficient to implement the Deque
interface:
addFirst(x) add(0, x)
⇒
removeFirst() remove(0)
⇒
addLast(x) add(size(), x)
⇒
removeLast() remove(size() 1)
⇒ −
Although we will normally not discuss the Stack, Deque and FIFO
Queue interfaces in subsequent chapters, the terms Stack and Deque are
sometimes used in the names of data structures that implement the List
interface. When this happens, it highlights the fact that these data struc-
tures can be used to implement the Stack or Deque interface very effi-
ciently. For example, the ArrayDeque class is an implementation of the
List interface that implements all the Deque operations in constant time
per operation.

（中文关键词：双端队列、栈、队列、数组）

## 1.2.3 The USet Interface: Unordered Sets

The USet interface represents an unordered set of unique elements, which
mimics a mathematical set. A USet contains n distinct elements; no ele-
ment appears more than once; the elements are in no specific order. A
USet supports the following operations:
1. size(): return the number, n, of elements in the set
2. add(x): add the element x to the set if not already present;
Add x to the set provided that there is no element y in the set such
that x equals y. Return true if x was added to the set and false
otherwise.
3. remove(x): remove x from the set;
Find an element y in the set such that x equals y and remove y.
Return y, or null if no such element exists.
4. find(x): find x in the set if it exists;
Find an element y in the set such that y equals x. Return y, or null
if no such element exists.
These definitions are a bit fussy about distinguishing x, the element
we are removing or finding, from y, the element we may remove or find.
This is because x and y might actually be distinct objects that are never-
theless treated as equal.2 Such a distinction is useful because it allows for
the creation of dictionaries or maps that map keys onto values.
To create a dictionary/map, one forms compound objects called Pairs,
each of which contains a key and a value. Two Pairs are treated as equal
if their keys are equal. If we store some pair (k, v) in a USet and then
later call the find(x) method using the pair x = (k, null) the result will be
y = (k, v). In other words, it is possible to recover the value, v, given only
the key, k.
2In Java, this is done by overriding the class’s equals(y) and hashCode() methods.

## 1.2.4 The SSet Interface: Sorted Sets

The SSet interface represents a sorted set of elements. An SSet stores
elements from some total order, so that any two elements x and y can
be compared. In code examples, this will be done with a method called
compare(x, y) in which
< 0 if x < y
compare(x, y) > 0 if x > y

 = 0 if x = y
An SSet supports the size(), add(x),  and remove(x) methods with exactly
the same semantics as in the USet interface. The difference between a
USet and an SSet is in the find(x) method:
4. find(x): locate x in the sorted set;
Find the smallest element y in the set such that y x. Return y or
≥
null if no such element exists.
This version of the find(x) operation is sometimes referred to as a
successor search. It differs in a fundamental way from USet.find(x) since
it returns a meaningful result even when there is no element equal to x
in the set.
The distinction between the USet and SSet find(x) operations is very
important and often missed. The extra functionality provided by an SSet
usually comes with a price that includes both a larger running time and a
higher implementation complexity. For example, most of the SSet imple-
mentations discussed in this book all have find(x) operations with run-
ning times that are logarithmic in the size of the set. On the other hand,
the implementation of a USet as a ChainedHashTable in Chapter 5 has
a find(x) operation that runs in constant expected time. When choosing
which of these structures to use, one should always use a USet unless the
extra functionality offered by an SSet is truly needed.

（中文关键词：复杂度）
