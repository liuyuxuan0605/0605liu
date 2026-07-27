---
structure:
source: open/ods_p061.md
page: 61
---

# ODS p61: DualArrayDeque : Building a Deque from Two Stacks §2.5

DualArrayDeque : Building a Deque from Two Stacks §2.5
return x;
}
2.5.1 Balancing
Finally, we turn to the balance () operation performed by add(i;x) and
remove (i). This operation ensures that neither front norback becomes
too big (or too small). It ensures that, unless there are fewer than two
elements, each of front and back contain at least n=4 elements. If this
is not the case, then it moves elements between them so that front and
back contain exactlybn=2celements anddn=2eelements, respectively.
DualArrayDeque
void balance() {
int n = size();
if (3 *front.size() < back.size()) {
int s = n/2 - front.size();
List<T> l1 = newStack();
List<T> l2 = newStack();
l1.addAll(back.subList(0,s));
Collections.reverse(l1);
l1.addAll(front);
l2.addAll(back.subList(s, back.size()));
front = l1;
back = l2;
} else if (3 *back.size() < front.size()) {
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
Here there is little to analyze. If the balance () operation does rebal-
47

（中文关键词：数组、栈、双端队列）
