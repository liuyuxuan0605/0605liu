---
structure:
source: open/ods_p178.md
page: 178
---

# ODS p178: §7.2 Random Binary Search Trees

§7.2 Random Binary Search Trees
}
An example of an add(x) operation is shown in Figure 7.7.
The running time of the add(x) operation is given by the time it takes
to follow the search path for xplus the number of rotations performed
to move the newly-added node, u, up to its correct location in the Treap .
By Lemma 7.2, the expected length of the search path is at most 2ln n+
O(1). Furthermore, each rotation decreases the depth of u. This stops if
ubecomes the root, so the expected number of rotations cannot exceed
the expected length of the search path. Therefore, the expected running
time of the add(x) operation in a Treap isO(logn). (Exercise 7.5 asks
you to show that the expected number of rotations performed during an
addition is actually only O(1).)
The remove (x) operation in a Treap is the opposite of the add(x) op-
eration. We search for the node, u, containing x, then perform rotations
to move udownwards until it becomes a leaf, and then we splice ufrom
theTreap . Notice that, to move udownwards, we can perform either a
left or right rotation at u, which will replace uwith u:right oru:left ,
respectively. The choice is made by the ﬁrst of the following that apply:
1. If u:left andu:right are both null , then uis a leaf and no rotation
is performed.
2. If u:left (oru:right ) isnull , then perform a right (or left, respec-
tively) rotation at u.
3. If u:left:p<u:right:p(oru:left:p>u:right:p), then perform a
right rotation (or left rotation, respectively) at u.
These three rules ensure that the Treap doesn’t become disconnected and
that the heap property is restored once uis removed.
Treap
boolean remove(T x) {
Node<T> u = findLast(x);
if (u != nil && compare(u.x, x) == 0) {
trickleDown(u);
splice(u);
return true;
164

（中文关键词：二叉搜索树、堆、树、随机）
