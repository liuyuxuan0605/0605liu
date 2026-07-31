---
structure: 
source: book/ods_4_1_the-basic-structure.md
chapter: 4. Skiplists
section: 4.1
page: 101
kind: textbook
---

# 4.1 The Basic Structure

## The Basic Structure (1/2)

Conceptually, a skiplist is a sequence of singly-linked lists L , . . . , L . Each
0 h
list L contains a subset of the items in L . We start with the input list
r r 1
−
L that contains n items and construct L from L , L from L , and so on.
0 1 0 2 1
The items in L are obtained by tossing a coin for each element, x, in L
r r 1
−
and including x in L if the coin turns up as heads. This process ends
r
when we create a list L that is empty. An example of a skiplist is shown
r
in Figure 4.1.
For an element, x, in a skiplist, we call the height of x the largest value
L5
L4
L3
L2
L1
L0 0 1 2 3 4 5 6
sentinel
Figure 4.1: A skiplist containing seven elements.
r such that x appears in L . Thus, for example, elements that only appear
r
in L have height 0. If we spend a few moments thinking about it, we
0
notice that the height of x corresponds to the following experiment: Toss
a coin repeatedly until it comes up as tails. How many times did it come
up as heads? The answer, not surprisingly, is that the expected height of
a node is 1. (We expect to toss the coin twice before getting tails, but we
don’t count the last toss.) The height of a skiplist is the height of its tallest
node.
At the head of every list is a special node, called the sentinel, that acts
as a dummy node for the list. The key property of skiplists is that there is
a short path, called the search path, from the sentinel in L to every node
h
in L . Remembering how to construct a search path for a node, u, is easy
0
(see Figure 4.2) : Start at the top left corner of your skiplist (the sentinel
in L ) and always go right unless that would overshoot u, in which case
h
you should take a step down into the list below.
More precisely, to construct the search path for the node u in L , we
0
start at the sentinel, w, in L . Next, we examine w.next. If w.next contains
h
an item that appears before u in L , then we set w = w.next. Otherwise,
0
we move down and continue the search at the occurrence of w in the list
L . We continue this way until we reach the predecessor of u in L .
h 1 0
−
The following result, which we will prove in Section 4.4, shows that
the search path is quite short:
Lemma 4.1. The expected length of the search path for any node, u, in L is
0
at most 2 log n + O(1) = O(log n).

（中文关键词：跳表、单向链表、链表）

## The Basic Structure (2/2)

A space-efficient way to implement a skiplist is to define a Node, u,
L5
L4
L3
L2
L1
L0 0 1 2 3 4 5 6
sentinel
Figure 4.2: The search path for the node containing 4 in a skiplist.
as consisting of a data value, x, and an array, next, of pointers, where
u.next[i] points to u’s successor in the list L . In this way, the data, x, in
i
a node is referenced only once, even though x may appear in several lists.
SkiplistSSet
class Node<T> {
T x;
Node<T>[] next;
Node(T ix, int h) {
x = ix;
next = Array.newInstance(Node.class, h+1);
}
int height() {
return next.length - 1;
}
}
The next two sections of this chapter discuss two different applica-
tions of skiplists. In each of these applications, L stores the main struc-
0
ture (a list of elements or a sorted set of elements). The primary difference
between these structures is in how a search path is navigated; in partic-
ular, they differ in how they decide if a search path should go down into
L or go right within L .
r 1 r
−

（中文关键词：跳表、数组）
