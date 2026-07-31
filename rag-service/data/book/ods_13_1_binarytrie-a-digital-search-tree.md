---
structure: 
source: book/ods_13_1_binarytrie-a-digital-search-tree.md
chapter: 13. Data Structures for Integers
section: 13.1
page: 280
kind: textbook
---

# 13.1 BinaryTrie: A digital search tree

## BinaryTrie: A digital search tree (1/3)

A BinaryTrie encodes a set of w bit integers in a binary tree. All leaves in
the tree have depth w and each integer is encoded as a root-to-leaf path.
The path for the integer x turns left at level i if the ith most significant
bit of x is a 0 and turns right if it is a 1. Figure 13.1 shows an example
for the case w = 4, in which the trie stores the integers 3(0011), 9(1001),
12(1100), and 13(1101).
Because the search path for a value x depends on the bits of x, it
will be helpful to name the children of a node, u, u.child[0] (left) and
u.child[1] (right). These child pointers will actually serve double-duty.
Since the leaves in a binary trie have no children, the pointers are used to
string the leaves together into a doubly-linked list. For a leaf in the bi-
nary trie u.child[0] (prev) is the node that comes before u in the list and
u.child[1] (next) is the node that follows u in the list. A special node,
dummy, is used both before the first node and after the last node in the list
(see Section 3.2).
Each node, u, also contains an additional pointer u.jump. If u’s left
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
Figure 13.2: A BinaryTrie with jump pointers shown as curved dashed edges.
child is missing, then u.jump points to the smallest leaf in u’s subtree.
If u’s right child is missing, then u.jump points to the largest leaf in u’s
subtree. An example of a BinaryTrie, showing jump pointers and the
doubly-linked list at the leaves, is shown in Figure 13.2.
The find(x) operation in a BinaryTrie is fairly straightforward. We
try to follow the search path for x in the trie. If we reach a leaf, then we
have found x. If we reach a node u where we cannot proceed (because
u is missing a child), then we follow u.jump, which takes us either to the
smallest leaf larger than x or the largest leaf smaller than x. Which of
these two cases occurs depends on whether u is missing its left or right
child, respectively. In the former case (u is missing its left child), we have
found the node we want. In the latter case (u is missing its right child),
we can use the linked list to reach the node we want. Each of these cases
is illustrated in Figure 13.3.
BinaryTrie
T find(T x) {
int i, c = 0, ix = it.intValue(x);
Node u = r;
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) break;
u = u.child[c];
}
? ? ? ?
0? ? ? 1? ? ?
find(5) find(8)
00?? 01?? 10?? 11??

（中文关键词：字典树、树、链表、双向链表、二叉树）

## BinaryTrie: A digital search tree (2/3)

000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
Figure 13.3: The paths followed by find(5) and find(8).
if (i == w) return u.x; // found it
u = (c == 0) ? u.jump : u.jump.child[next];
return u == dummy ? null : u.x;
}
The running-time of the find(x) method is dominated by the time it
takes to follow a root-to-leaf path, so it runs in O(w) time.
The add(x) operation in a BinaryTrie is also fairly straightforward,
but has a lot of work to do:
1. It follows the search path for x until reaching a node u where it can
no longer proceed.
2. It creates the remainder of the search path from u to a leaf that
contains x.
3. It adds the node, u , containing x to the linked list of leaves (it has
(cid:48)
access to the predecessor, pred, of u in the linked list from the jump
(cid:48)
pointer of the last node, u, encountered during step 1.)
4. It walks back up the search path for x adjusting jump pointers at the
nodes whose jump pointer should now point to x.
An addition is illustrated in Figure 13.4.
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
Figure 13.4: Adding the values 2 and 15 to the BinaryTrie in Figure 13.2.
BinaryTrie
boolean add(T x) {
int i, c = 0, ix = it.intValue(x);
Node u = r;
// 1 - search for ix until falling out of the trie
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) break;
u = u.child[c];
}
if (i == w) return false; // already contains x - abort
Node pred = (c == right) ? u.jump : u.jump.child[0];
u.jump = null; // u will have two children shortly
// 2 - add path to ix
for (; i < w; i++) {
c = (ix >>> w-i-1) & 1;
u.child[c] = newNode();
u.child[c].parent = u;
u = u.child[c];
}
u.x = x;
// 3 - add u to linked list
u.child[prev] = pred;
u.child[next] = pred.child[next];
u.child[prev].child[next] = u;
u.child[next].child[prev] = u;
// 4 - walk back up, updating jump pointers
Node v = u.parent;
while (v != null) {
if ((v.child[left] == null
&& (v.jump == null || it.intValue(v.jump.x) > ix))
|| (v.child[right] == null
&& (v.jump == null || it.intValue(v.jump.x) < ix)))
v.jump = u;
v = v.parent;
}
n++;
return true;
}
This method performs one walk down the search path for x and one
walk back up. Each step of these walks takes constant time, so the add(x)
method runs in O(w) time.
The remove(x) operation undoes the work of add(x). Like add(x), it
has a lot of work to do:

（中文关键词：字典树、链表、树）

## BinaryTrie: A digital search tree (3/3)

1. It follows the search path for x until reaching the leaf, u, containing
x.
2. It removes u from the doubly-linked list.
3. It deletes u and then walks back up the search path for x deleting
nodes until reaching a node v that has a child that is not on the
search path for x.
4. It walks upwards from v to the root updating any jump pointers that
point to u.
A removal is illustrated in Figure 13.5.
BinaryTrie
boolean remove(T x) {
// 1 - find leaf, u, containing x
int i = 0, c, ix = it.intValue(x);
Node u = r;
? ? ? ?
0? ? ? 1? ? ?
00?? 01?? 10?? 11??
000? 001? 010? 011? 100? 101? 110? 111?
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
Figure 13.5: Removing the value 9 from the BinaryTrie in Figure 13.2.
for (i = 0; i < w; i++) {
c = (ix >>> w-i-1) & 1;
if (u.child[c] == null) return false;
u = u.child[c];
}
// 2 - remove u from linked list
u.child[prev].child[next] = u.child[next];
u.child[next].child[prev] = u.child[prev];
Node v = u;
// 3 - delete nodes on path to u
for (i = w-1; i >= 0; i--) {
c = (ix >>> w-i-1) & 1;
v = v.parent;
v.child[c] = null;
if (v.child[1-c] != null) break;
}
// 4 - update jump pointers
v.jump = u;
for (; i >= 0; i--) {
c = (ix >>> w-i-1) & 1;
if (v.jump == u)
v.jump = u.child[1-c];
v = v.parent;
}
n--;
return true;
}
Theorem 13.1. A BinaryTrie implements the SSet interface for w-bit inte-
gers. A BinaryTrie supports the operations add(x), remove(x), and find(x)
in O(w) time per operation. The space used by a BinaryTrie that stores n
values is O(n w).
·

（中文关键词：字典树、链表、双向链表、树）
