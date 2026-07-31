---
structure: Deque
source: book/ods_2_5_dualarraydeque-building-a-deque-from-two-stacks.md
chapter: 2. Array-Based Lists
section: 2.5
page: 57
kind: textbook
---

# 2.5 DualArrayDeque: Building a Deque from Two Stacks

## DualArrayDeque: Building a Deque from Two Stacks (1/2)

Next, we present a data structure, the DualArrayDeque that achieves the
same performance bounds as an ArrayDeque by using two ArrayStacks.
Although the asymptotic performance of the DualArrayDeque is no bet-
ter than that of the ArrayDeque, it is still worth studying, since it offers a
good example of how to make a sophisticated data structure by combin-
ing two simpler data structures.
A DualArrayDeque represents a list using two ArrayStacks. Recall
that an ArrayStack is fast when the operations on it modify elements
near the end. A DualArrayDeque places two ArrayStacks, called front
and back, back-to-back so that operations are fast at either end.
DualArrayDeque
List<T> front;
List<T> back;
A DualArrayDeque does not explicitly store the number, n, of ele-
ments it contains. It doesn’t need to, since it contains n = front.size() +
back.size() elements. Nevertheless, when analyzing the DualArrayDeque
we will still use n to denote the number of elements it contains.
DualArrayDeque
int size() {
return front.size() + back.size();
}
The front ArrayStack stores the list elements that whose indices are
0, . . . , front.size() 1, but stores them in reverse order. The back Array-
−
Stack contains list elements with indices in front.size(), . . . , size() 1 in
−
the normal order. In this way, get(i) and set(i, x) translate into appro-
priate calls to get(i) or set(i, x) on either front or back, which take O(1)
time per operation.
DualArrayDeque
T get(int i) {
if (i < front.size()) {
return front.get(front.size()-i-1);
} else {
return back.get(i-front.size());
}
}
T set(int i, T x) {
if (i < front.size()) {
return front.set(front.size()-i-1, x);
} else {
return back.set(i-front.size(), x);
}
}
front back
a b c d
add(3,x)
a b c x d
add(4,y)
a b c x y d
remove(0)
∗
b c x y d
b c x y d
4 3 2 1 0 0 1 2 3 4
Figure 2.4: A sequence of add(i,x) and remove(i) operations on a DualArray-
Deque. Arrows denote elements being copied. Operations that result in a rebal-
ancing by balance() are marked with an asterisk.
Note that if an index i < front.size(), then it corresponds to the ele-
ment of front at position front.size() i 1, since the elements of front
− −
are stored in reverse order.
Adding and removing elements from a DualArrayDeque is illustrated
in Figure 2.4. The add(i, x) operation manipulates either front or back,
as appropriate:

（中文关键词：数组、双端队列、栈）

## DualArrayDeque: Building a Deque from Two Stacks (2/2)

DualArrayDeque
void add(int i, T x) {
if (i < front.size()) {
front.add(front.size()-i, x);
} else {
back.add(i-front.size(), x);
}
balance();
}
The add(i, x) method performs rebalancing of the two ArrayStacks
front and back, by calling the balance() method. The implementation
of balance() is described below, but for now it is sufficient to know that
balance() ensures that, unless size() < 2, front.size() and back.size()
do not differ by more than a factor of 3. In particular, 3 front.size()
· ≥
back.size() and 3 back.size() front.size().
· ≥
Next we analyze the cost of add(i, x), ignoring the cost of calls to
balance(). If i < front.size(), then add(i, x) gets implemented by the
call to front.add(front.size() i 1, x). Since front is an ArrayStack,
− −
the cost of this is
O(front.size() (front.size() i 1) + 1) = O(i + 1) . (2.1)
− − −
On the other hand, if i front.size(), then add(i, x) gets implemented
≥
as back.add(i front.size(), x). The cost of this is
−
O(back.size() (i front.size()) + 1) = O(n i + 1) . (2.2)
− − −
Notice that the first case (2.1) occurs when i < n/4. The second case
(2.2) occurs when i 3n/4. When n/4 i < 3n/4, we cannot be sure
≥ ≤
whether the operation affects front or back, but in either case, the op-
eration takes O(n) = O(i) = O(n i) time, since i n/4 and n i > n/4.
− ≥ −
Summarizing the situation, we have
O(1 + i) if i < n/4
Running time of add(i, x) O(n) if n/4 i < 3n/4
≤  ≤
 O(1 + n
−
i) if i
≥
3n/4
Thus, the running time of add(i,

x), if we ignore the cost of the call to
balance(), is O(1 + min i, n i ).
{ − }
The remove(i) operation and its analysis resemble the add(i, x) oper-
ation and analysis.
DualArrayDeque
T remove(int i) {
T x;
if (i < front.size()) {
x = front.remove(front.size()-i-1);
} else {
x = back.remove(i-front.size());
}
balance();
return x;
}

（中文关键词：数组、双端队列、栈）

## 2.5.1 Balancing (1/2)

Finally, we turn to the balance() operation performed by add(i, x) and
remove(i). This operation ensures that neither front nor back becomes
too big (or too small). It ensures that, unless there are fewer than two
elements, each of front and back contain at least n/4 elements. If this
is not the case, then it moves elements between them so that front and
back contain exactly n/2 elements and n/2 elements, respectively.
(cid:98) (cid:99) (cid:100) (cid:101)
DualArrayDeque
void balance() {
int n = size();
if (3*front.size() < back.size()) {
int s = n/2 - front.size();
List<T> l1 = newStack();
List<T> l2 = newStack();
l1.addAll(back.subList(0,s));
Collections.reverse(l1);
l1.addAll(front);
l2.addAll(back.subList(s, back.size()));
front = l1;
back = l2;
} else if (3*back.size() < front.size()) {
int s = front.size() - n/2;
List<T> l1 = newStack();
List<T> l2 = newStack();
l1.addAll(front.subList(s, front.size()));
l2.addAll(front.subList(0, s));
Collections.reverse(l2);
l2.addAll(back);
front = l1;
back = l2;
}
}
Here there is little to analyze. If the balance() operation does rebal-
ancing, then it moves O(n) elements and this takes O(n) time. This is bad,
since balance() is called with each call to add(i, x) and remove(i). How-
ever, the following lemma shows that, on average, balance() only spends
a constant amount of time per operation.
Lemma 2.2. If an empty DualArrayDeque is created and any sequence of
m 1 calls to add(i, x) and remove(i) are performed, then the total time
≥
spent during all calls to balance() is O(m).
Proof. We will show that, if balance() is forced to shift elements, then
the number of add(i, x) and remove(i) operations since the last time any
elements were shifted by balance() is at least n/2 1. As in the proof
−
of Lemma 2.1, this is sufficient to prove that the total time spent by
balance() is O(m).
We will perform our analysis using a technique knows as the potential
method. Define the potential, Φ, of the DualArrayDeque as the difference
in size between front and back:
Φ = front.size() back.size() .
| − |
The interesting thing about this potential is that a call to add(i, x) or
remove(i) that does not do any balancing can increase the potential by
at most 1.
Observe that, immediately after a call to balance() that shifts ele-
ments, the potential, Φ , is at most 1, since
0
Φ = n/2 n/2 1 .

（中文关键词：栈、数组、双端队列）

## 2.5.1 Balancing (2/2)

0
|(cid:98) (cid:99) − (cid:100) (cid:101)| ≤
Consider the situation immediately before a call to balance() that
shifts elements and suppose, without loss of generality, that balance()
is shifting elements because 3front.size() < back.size(). Notice that, in
this case,
n = front.size() + back.size()
< back.size()/3 + back.size()
4
= back.size()
Furthermore, the potential at this point in time is
Φ = back.size() front.size()
1
−
> back.size() back.size()/3
−
2
= back.size()
3
2 3
> n
3 × 4
= n/2
Therefore, the number of calls to add(i, x) or remove(i) since the last time
balance() shifted elements is at least Φ Φ > n/2 1. This completes
1 0
− −
the proof.

## 2.5.2 Summary

The following theorem summarizes the properties of a DualArrayDeque:
Theorem 2.4. A DualArrayDeque implements the List interface. Ignoring
the cost of calls to resize() and balance(), a DualArrayDeque supports the
operations
• get(i) and set(i, x) in O(1) time per operation; and
• add(i, x) and remove(i) in O(1 + min i, n i ) time per operation.
{ − }
Furthermore, beginning with an empty DualArrayDeque, any sequence of m
add(i, x) and remove(i) operations results in a total of O(m) time spent dur-
ing all calls to resize() and balance().

（中文关键词：数组、双端队列）
