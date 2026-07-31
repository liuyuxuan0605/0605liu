---
structure: BTree
source: book/ods_14_2_b-trees.md
chapter: 14. External Memory Searching
section: 14.2
page: 299
kind: textbook
---

# 14.2 B-Trees

## B-Trees (1/2)

In this section, we discuss a generalization of binary trees, called B-trees,
which is efficient in the external memory model. Alternatively, B-trees
can be viewed as the natural generalization of 2-4 trees described in Sec-
tion 9.1. (A 2-4 tree is a special case of a B-tree that we get by setting
B = 2.)
For any integer B 2, a B-tree is a tree in which all of the leaves have
≥
the same depth and every non-root internal node, u, has at least B chil-
dren and at most 2B children. The children of u are stored in an array,
u.children. The required number of children is relaxed at the root, which
can have anywhere between 2 and 2B children.
If the height of a B-tree is h, then it follows that the number, (cid:96), of
leaves in the B-tree satisfies
2Bh − 1 (cid:96) 2(2B)h − 1 .
≤ ≤
Taking the logarithm of the first inequality and rearranging terms yields:
log (cid:96) 1
h − + 1
≤ log B
log (cid:96)
+ 1
≤ log B
= log (cid:96) + 1 .
B
That is, the height of a B-tree is proportional to the base-B logarithm of
the number of leaves.
Each node, u, in B-tree stores an array of keys u.keys[0], . . . , u.keys[2B
−
1]. If u is an internal node with k children, then the number of keys stored
at u is exactly k 1 and these are stored in u.keys[0], . . . , u.keys[k 2]. The
− −
remaining 2B k + 1 array entries in u.keys are set to null. If u is a non-
−
root leaf node, then u contains between B 1 and 2B 1 keys. The keys in
− −
a B-tree respect an order similar to the keys in a binary search tree. For
any node, u, that stores k 1 keys,
−
u.keys[0] < u.keys[1] < < u.keys[k 2] .
· · · −
If u is an internal node, then for every i 0, . . . , k 2 , u.keys[i] is larger
∈ { − }
than every key stored in the subtree rooted at u.children[i] but smaller
than every key stored in the subtree rooted at u.children[i + 1]. Infor-
mally,
u.children[i] u.keys[i] u.children[i + 1] .
≺ ≺
10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
Figure 14.2: A B-tree with B = 2.
An example of a B-tree with B = 2 is shown in Figure 14.2.
Note that the data stored in a B-tree node has size O(B). Therefore, in
an external memory setting, the value of B in a B-tree is chosen so that
a node fits into a single external memory block. In this way, the time
it takes to perform a B-tree operation in the external memory model is
proportional to the number of nodes that are accessed (read or written)
by the operation.

（中文关键词：树、B树、外存、数组、2-4树、二叉搜索树）

## B-Trees (2/2)

For example, if the keys are 4 byte integers and the node indices are
also 4 bytes, then setting B = 256 means that each node stores
(4 + 4) 2B = 8 512 = 4096
× ×
bytes of data. This would be a perfect value of B for the hard disk or
solid state drive discussed in the introduction to this chaper, which have
a block size of 4096 bytes.
The BTree class, which implements a B-tree, stores a BlockStore, bs,
that stores BTree nodes as well as the index, ri, of the root node. As
usual, an integer, n, is used to keep track of the number of items in the
data structure:
BTree
int n;
BlockStore<Node> bs;
int ri;
10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
16.5
Figure 14.3: A successful search (for the value 4) and an unsuccessful search (for
the value 16.5) in a B-tree. Shaded nodes show where the value of z is updated
during the searches.

（中文关键词：树、B树）

## 14.2.1 Searching (1/2)

The implementation of the find(x) operation, which is illustrated in Fig-
ure 14.3, generalizes the find(x) operation in a binary search tree. The
search for x starts at the root and uses the keys stored at a node, u, to
determine in which of u’s children the search should continue.
More specifically, at a node u, the search checks if x is stored in u.keys.
If so, x has been found and the search is complete. Otherwise, the search
finds the smallest integer, i, such that u.keys[i] > x and continues the
search in the subtree rooted at u.children[i]. If no key in u.keys is
greater than x, then the search continues in u’s rightmost child. Just like
binary search trees, the algorithm keeps track of the most recently seen
key, z, that is larger than x. In case x is not found, z is returned as the
smallest value that is greater or equal to x.
BTree
T find(T x) {
T z = null;
int ui = ri;
while (ui >= 0) {
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) return u.keys[-(i+1)]; // found it
if (u.keys[i] != null)
z = u.keys[i];
ui = u.children[i];
}
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
a 1 4 5 8 9 10 14 16 22 31 45 – – – – –
27
Figure 14.4: The execution of findIt(a,27).
return z;
}
Central to the find(x) method is the findIt(a, x) method that searches
in a null-padded sorted array, a, for the value x. This method, illustrated
in Figure 14.4, works for any array, a, where a[0], . . . , a[k 1] is a sequence
−
of keys in sorted order and a[k], . . . , a[a.length 1] are all set to null. If x
−
is in the array at position i, then findIt(a, x) returns i 1. Otherwise,
− −
it returns the smallest index, i, such that a[i] > x or a[i] = null.
BTree
int findIt(T[] a, T x) {
int lo = 0, hi = a.length;
while (hi != lo) {
int m = (hi+lo)/2;
int cmp = a[m] == null ? -1 : compare(x, a[m]);
if (cmp < 0)
hi = m; // look in first half
else if (cmp > 0)
lo = m+1; // look in second half
else
return -m-1; // found it
}
return lo;
}
The findIt(a, x) method uses a binary search that halves the search
space at each step, so it runs in O(log(a.length)) time. In our setting,
a.length = 2B, so findIt(a, x) runs in O(log B) time.

（中文关键词：树、数组、二叉搜索树）

## 14.2.1 Searching (2/2)

We can analyze the running time of a B-tree find(x) operation both
in the usual word-RAM model (where every instruction counts) and in
the external memory model (where we only count the number of nodes
accessed). Since each leaf in a B-tree stores at least one key and the height
of a B-Tree with (cid:96) leaves is O(log (cid:96)), the height of a B-tree that stores
B
n keys is O(log n). Therefore, in the external memory model, the time
B
taken by the find(x) operation is O(log n). To determine the running
B
time in the word-RAM model, we have to account for the cost of calling
findIt(a, x) for each node we access, so the running time of find(x) in
the word-RAM model is
O(log n) O(log B) = O(log n) .
B ×

（中文关键词：B树、树、外存）

## 14.2.2 Addition (1/3)

One important difference between B-trees and the BinarySearchTree
data structure from Section 6.2 is that the nodes of a B-tree do not store
pointers to their parents. The reason for this will be explained shortly.
The lack of parent pointers means that the add(x) and remove(x) opera-
tions on B-trees are most easily implemented using recursion.
Like all balanced search trees, some form of rebalancing is required
during an add(x) operation. In a B-tree, this is done by splitting nodes. Re-
fer to Figure 14.5 for what follows. Although splitting takes place across
two levels of recursion, it is best understood as an operation that takes a
node u containing 2B keys and having 2B + 1 children. It creates a new
node, w, that adopts u.children[B], . . . , u.children[2B]. The new node w
also takes u’s B largest keys, u.keys[B], . . . , u.keys[2B 1]. At this point, u
−
has B children and B keys. The extra key, u.keys[B 1], is passed up to
−
the parent of u, which also adopts w.
Notice that the splitting operation modifies three nodes: u, u’s parent,
and the new node, w. This is why it is important that the nodes of a B-
tree do not maintain parent pointers. If they did, then the B + 1 children
adopted by w would all need to have their parent pointers modified. This
would increase the number of external memory accesses from 3 to B + 4
and would make B-trees much less efficient for large values of B.
The add(x) method in a B-tree is illustrated in Figure 14.6. At a high
b d f u
u
¢h¢¢ j m o q s
A C E V
G I K N P R T
u.split()
⇓
b d f m u
u w
h¢ j m o q s
A C E V
G I K N P R T
Figure 14.5: Splitting the node u in a B-tree (B = 3). Notice that the key
u.keys[2] = m passes from u to its parent.

（中文关键词：树、B树、递归、外存）

## 14.2.2 Addition (2/3)

10
3 6 14 17 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 21 23 24
⇓
10
3 6 14 17 19 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 21 23 24
⇓
10 17
3 6 14 17 19 22
0 1 2 4 5 7 8 9 11 12 13 15 16 18 20 21 23 24
Figure 14.6: The add(x) operation in a BTree. Adding the value 21 results in two
nodes being split.
level, this method finds a leaf, u, at which to add the value x. If this
causes u to become overfull (because it already contained B 1 keys), then
−
u is split. If this causes u’s parent to become overfull, then u’s parent is
also split, which may cause u’s grandparent to become overfull, and so
on. This process continues, moving up the tree one level at a time until
reaching a node that is not overfull or until the root is split. In the former
case, the process stops. In the latter case, a new root is created whose two
children become the nodes obtained when the original root was split.
The executive summary of the add(x) method is that it walks from the
root to a leaf searching for x, adds x to this leaf, and then walks back up
to the root, splitting any overfull nodes it encounters along the way. With
this high level view in mind, we can now delve into the details of how
this method can be implemented recursively.
The real work of add(x) is done by the addRecursive(x, ui) method,
which adds the value x to the subtree whose root, u, has the identifier ui.
If u is a leaf, then x is simply inserted into u.keys. Otherwise, x is added
recursively into the appropriate child, u , of u. The result of this recursive
(cid:48)
call is normally null but may also be a reference to a newly-created node,
w, that was created because u was split. In this case, u adopts w and takes
(cid:48)
its first key, completing the splitting operation on u .
(cid:48)
After the value x has been added (either to u or to a descendant of
u), the addRecursive(x, ui) method checks to see if u is storing too many
(more than 2B 1) keys. If so, then u needs to be split with a call to the
−
u.split() method. The result of calling u.split() is a new node that is
used as the return value for addRecursive(x, ui).

（中文关键词：树）

## 14.2.2 Addition (3/3)

BTree
Node addRecursive(T x, int ui) {
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) throw new DuplicateValueException();
if (u.children[i] < 0) { // leaf node, just add it
u.add(x, -1);
bs.writeBlock(u.id, u);
} else {
Node w = addRecursive(x, u.children[i]);
if (w != null) { // child was split, w is new child
x = w.remove(0);
bs.writeBlock(w.id, w);
u.add(x, w.id);
bs.writeBlock(u.id, u);
}
}
return u.isFull() ? u.split() : null;
}
The addRecursive(x, ui) method is a helper for the add(x) method,
which calls addRecursive(x, ri) to insert x into the root of the B-tree. If
addRecursive(x, ri) causes the root to split, then a new root is created
that takes as its children both the old root and the new node created by
the splitting of the old root.
BTree
boolean add(T x) {
Node w;
try {
w = addRecursive(x, ri);
} catch (DuplicateValueException e) {
return false;
}
if (w != null) { // root was split, make new root
Node newroot = new Node();
x = w.remove(0);
bs.writeBlock(w.id, w);
newroot.children[0] = ri;
newroot.keys[0] = x;
newroot.children[1] = w.id;
ri = newroot.id;
bs.writeBlock(ri, newroot);
}
n++;
return true;
}
The add(x) method and its helper, addRecursive(x, ui), can be ana-
lyzed in two phases:
Downward phase: During the downward phase of the recursion, before
x has been added, they access a sequence of BTree nodes and call
findIt(a, x) on each node. As with the find(x) method, this takes
O(log n) time in the external memory model and O(log n) time in
B
the word-RAM model.
Upward phase: During the upward phase of the recursion, after x has
been added, these methods perform a sequence of at most O(log n)
B
splits. Each split involves only three nodes, so this phase takes
O(log n) time in the external memory model. However, each split
B
involves moving B keys and children from one node to another, so
in the word-RAM model, this takes O(B log n) time.
Recall that the value of B can be quite large, much larger than even
log n. Therefore, in the word-RAM model, adding a value to a B-tree can
be much slower than adding into a balanced binary search tree. Later,
in Section 14.2.4, we will show that the situation is not quite so bad; the
amortized number of split operations done during an add(x) operation
is constant. This shows that the (amortized) running time of the add(x)
operation in the word-RAM model is O(B + log n).

（中文关键词：树、外存、摊还分析、递归、B树、二叉搜索树）

## 14.2.3 Removal (1/4)

The remove(x) operation in a BTree is, again, most easily implemented as
a recursive method. Although the recursive implementation of remove(x)
spreads the complexity across several methods, the overall process, which
is illustrated in Figure 14.7, is fairly straightforward. By shuffling keys
around, removal is reduced to the problem of removing a value, x , from
(cid:48)
some leaf, u. Removing x may leave u with less than B 1 keys; this
(cid:48)
−
situation is called an underflow.
When an underflow occurs, u either borrows keys from, or is merged
with, one of its siblings. If u is merged with a sibling, then u’s parent will
now have one less child and one less key, which can cause u’s parent to
underflow; this is again corrected by borrowing or merging, but merging
may cause u’s grandparent to underflow. This process works its way back
up to the root until there is no more underflow or until the root has its
last two children merged into a single child. When the latter case occurs,
the root is removed and its lone child becomes the new root.
Next we delve into the details of how each of these steps is imple-
mented. The first job of the remove(x) method is to find the element x
that should be removed. If x is found in a leaf, then x is removed from
this leaf. Otherwise, if x is found at u.keys[i] for some internal node, u,
then the algorithm removes the smallest value, x , in the subtree rooted at
(cid:48)
u.children[i + 1]. The value x is the smallest value stored in the BTree
(cid:48)
that is greater than x. The value of x is then used to replace x in u.keys[i].
(cid:48)
This process is illustrated in Figure 14.8.
The removeRecursive(x, ui) method is a recursive implementation of
the preceding algorithm:
BTree
boolean removeRecursive(T x, int ui) {
10
3 14 17 21
1 4 11 12 13 15 16 18 19 20 22 23
⇓
10
3 14 17 21
v w
1 4 11 12 13 15 16 18 19 20 22 23
merge(v, w)
⇓
10
w v
14 17 21
1 3 11 12 13 15 16 18 19 20 22 23
shiftLR(w, v)
⇓
14
10 17 21
1 3 11 12 13 15 16 18 19 20 22 23
Figure 14.7: Removing the value 4 from a B-tree results in one merge and one
borrowing operation.

（中文关键词：树、复杂度、B树）

## 14.2.3 Removal (2/4)

10
3 6 14 17 21
0 1 2 4 5 7 8 9 11 12 13 15 16 18 19 20 22 23
⇓
11
3 6 14 17 21
0 1 2 4 5 7 8 9 12 13 15 16 18 19 20 22 23
Figure 14.8: The remove(x) operation in a BTree. To remove the value x = 10 we
replace it with the the value x = 11 and remove 11 from the leaf that contains it.
(cid:48)
if (ui < 0) return false; // didn’t find it
Node u = bs.readBlock(ui);
int i = findIt(u.keys, x);
if (i < 0) { // found it
i = -(i+1);
if (u.isLeaf()) {
u.remove(i);
} else {
u.keys[i] = removeSmallest(u.children[i+1]);
checkUnderflow(u, i+1);
}
return true;
} else if (removeRecursive(x, u.children[i])) {
checkUnderflow(u, i);
return true;
}
return false;
}
T removeSmallest(int ui) {
Node u = bs.readBlock(ui);
if (u.isLeaf())
return u.remove(0);
T y = removeSmallest(u.children[0]);
checkUnderflow(u, 0);
return y;
}
Note that, after recursively removing the value x from the ith child
of u, removeRecursive(x, ui) needs to ensure that this child still has at
least B 1 keys. In the preceding code, this is done using a method called
−
checkUnderflow(x, i), which checks for and corrects an underflow in the
ith child of u. Let w be the ith child of u. If w has only B 2 keys, then this
−
needs to be fixed. The fix requires using a sibling of w. This can be either
child i + 1 of u or child i 1 of u. We will usually use child i 1 of u,
− −
which is the sibling, v, of w directly to its left. The only time this doesn’t
work is when i = 0, in which case we use the sibling directly to w’s right.
BTree
void checkUnderflow(Node u, int i) {
if (u.children[i] < 0) return;
if (i == 0)
checkUnderflowZero(u, i); // use u’s right sibling
else
checkUnderflowNonZero(u,i);
}
In the following, we focus on the case when i (cid:44) 0 so that any under-
flow at the ith child of u will be corrected with the help of the (i 1)st
−
child of u. The case i = 0 is similar and the details can be found in the
accompanying source code.
To fix an underflow at node w, we need to find more keys (and possibly
also children), for w. There are two ways to do this:

（中文关键词：树）

## 14.2.3 Removal (3/4)

Borrowing: If w has a sibling, v, with more than B 1 keys, then w can
−
borrow some keys (and possibly also children) from v. More specif-
ically, if v stores size(v) keys, then between them, v and w have a
total of
B 2 + size(w) 2B 2
− ≥ −
u
b d f o s
v w
h j m q¢
A C E T
G I K N P R
shiftRL(v, w)
⇓
u
b d f m s
v w
h¢ j o¢ q
A C E T
G I K N P R
Figure 14.9: If v has more than B 1 keys, then w can borrow keys from v.
−
keys. We can therefore shift keys from v to w so that each of v and w
has at least B 1 keys. This process is illustrated in Figure 14.9.
−
Merging: If v has only B 1 keys, we must do something more drastic,
−
since v cannot afford to give any keys to w. Therefore, we merge v
and w as shown in Figure 14.10. The merge operation is the opposite
of the split operation. It takes two nodes that contain a total of 2B 3
−
keys and merges them into a single node that contains 2B 2 keys.
−
(The additional key comes from the fact that, when we merge v and
w, their common parent, u, now has one less child and therefore
needs to give up one of its keys.)
BTree
void checkUnderflowNonZero(Node u, int i) {
Node w = bs.readBlock(u.children[i]); // w is child of u
u
b d f m q
v w
h¢ j o¢
A C E R
G I K N P
merge(v, w)
⇓
u
b d f q
h j m o
A C E R
G I K N P
Figure 14.10: Merging two siblings v and w in a B-tree (B = 3).
if (w.size() < B-1) { // underflow at w
Node v = bs.readBlock(u.children[i-1]); // v left of w
if (v.size() > B) { // w can borrow from v
shiftLR(u, i-1, v, w);
} else { // v will absorb w
merge(u, i-1, v, w);
}
}
}
void checkUnderflowZero(Node u, int i) {
Node w = bs.readBlock(u.children[i]); // w is child of u
if (w.size() < B-1) { // underflow at w
Node v = bs.readBlock(u.children[i+1]); // v right of w
if (v.size() > B) { // w can borrow from v
shiftRL(u, i, v, w);
} else { // w will absorb w
merge(u, i, w, v);
u.children[i] = w.id;
}
}
}
To summarize, the remove(x) method in a B-tree follows a root to leaf
path, removes a key x from a leaf, u, and then performs zero or more
(cid:48)
merge operations involving u and its ancestors, and performs at most one
borrowing operation. Since each merge and borrow operation involves
modifying only three nodes, and only O(log n) of these operations occur,
B
the entire process takes O(log n) time in the external memory model.

（中文关键词：树、B树、外存）

## 14.2.3 Removal (4/4)

B
Again, however, each merge and borrow operation takes O(B) time in
the word-RAM model, so (for now) the most we can say about the run-
ning time required by remove(x) in the word-RAM model is that it is
O(B log n).
B

## 14.2.4 Amortized Analysis of B-Trees (1/3)

Thus far, we have shown that
1. In the external memory model, the running time of find(x), add(x),
and remove(x) in a B-tree is O(log n).
B
2. In the word-RAM model, the running time of find(x) is O(log n)
and the running time of add(x) and remove(x) is O(B log n).
The following lemma shows that, so far, we have overestimated the
number of merge and split operations performed by B-trees.
Lemma 14.1. Starting with an empty B-tree and performing any sequence
of m add(x) and remove(x) operations results in at most 3m/2 splits, merges,
and borrows being performed.
Proof. The proof of this has already been sketched in Section 9.3 for the
special case in which B = 2. The lemma can be proven using a credit
scheme, in which
1. each split, merge, or borrow operation is paid for with two credits,
i.e., a credit is removed each time one of these operations occurs;
and
2. at most three credits are created during any add(x) or remove(x)
operation.
Since at most 3m credits are ever created and each split, merge, and bor-
row is paid for with with two credits, it follows that at most 3m/2 splits,
merges, and borrows are performed. These credits are illustrated using
the symbol in Figures 14.5, 14.9, and 14.10.
T¢o keep track of these credits the proof maintains the following credit
invariant: Any non-root node with B 1 keys stores one credit and any
−
node with 2B 1 keys stores three credits. A node that stores at least B
−
keys and most 2B 2 keys need not store any credits. What remains is to
−
show that we can maintain the credit invariant and satisfy properties 1
and 2, above, during each add(x) and remove(x) operation.
Adding: The add(x) method does not perform any merges or borrows, so
we need only consider split operations that occur as a result of calls to
add(x).
Each split operation occurs because a key is added to a node, u, that
already contains 2B 1 keys. When this happens, u is split into two nodes,
−
u and u having B 1 and B keys, respectively. Prior to this operation, u
(cid:48) (cid:48)(cid:48)
−
was storing 2B 1 keys, and hence three credits. Two of these credits can
−
be used to pay for the split and the other credit can be given to u (which
(cid:48)
has B 1 keys) to maintain the credit invariant. Therefore, we can pay for
−
the split and maintain the credit invariant during any split.

（中文关键词：B树、树、外存、摊还分析）

## 14.2.4 Amortized Analysis of B-Trees (2/3)

The only other modification to nodes that occur during an add(x) op-
eration happens after all splits, if any, are complete. This modification
involves adding a new key to some node u . If, prior to this, u had 2B 2
(cid:48) (cid:48)
−
children, then it now has 2B 1 children and must therefore receive three
−
credits. These are the only credits given out by the add(x) method.
Removing: During a call to remove(x), zero or more merges occur and
are possibly followed by a single borrow. Each merge occurs because
two nodes, v and w, each of which had exactly B 1 keys prior to call-
−
ing remove(x) were merged into a single node with exactly 2B 2 keys.
−
Each such merge therefore frees up two credits that can be used to pay
for the merge.
After any merges are performed, at most one borrow operation occurs,
after which no further merges or borrows occur. This borrow operation
only occurs if we remove a key from a leaf, v, that has B 1 keys. The
−
node v therefore has one credit, and this credit goes towards the cost of
the borrow. This single credit is not enough to pay for the borrow, so we
create one credit to complete the payment.
At this point, we have created one credit and we still need to show that
the credit invariant can be maintained. In the worst case, v’s sibling, w,
has exactly B keys before the borrow so that, afterwards, both v and w have
B 1 keys. This means that v and w each should be storing a credit when
−
the operation is complete. Therefore, in this case, we create an additional
two credits to give to v and w. Since a borrow happens at most once during
a remove(x) operation, this means that we create at most three credits, as
required.
If the remove(x) operation does not include a borrow operation, this
is because it finishes by removing a key from some node that, prior to the
operation, had B or more keys. In the worst case, this node had exactly B
keys, so that it now has B 1 keys and must be given one credit, which we
−
create.
In either case—whether the removal finishes with a borrow operation
or not—at most three credits need to be created during a call to remove(x)
to maintain the credit invariant and pay for all borrows and merges that
occur. This completes the proof of the lemma.

（中文关键词：摊还分析、B树、树）

## 14.2.4 Amortized Analysis of B-Trees (3/3)

The purpose of Lemma 14.1 is to show that, in the word-RAM model
the cost of splits, merges and joins during a sequence of m add(x) and
remove(x) operations is only O(Bm). That is, the amortized cost per op-
eration is only O(B), so the amortized cost of add(x) and remove(x) in the
word-RAM model is O(B + log n). This is summarized by the following
pair of theorems:
Theorem 14.1 (External Memory B-Trees). A BTree implements the SSet
interface. In the external memory model, a BTree supports the operations
add(x), remove(x), and find(x) in O(log n) time per operation.
B
Theorem 14.2 (Word-RAM B-Trees). A BTree implements the SSet inter-
face. In the word-RAM model, and ignoring the cost of splits, merges, and
borrows, a BTree supports the operations add(x), remove(x), and find(x)
in O(log n) time per operation. Furthermore, beginning with an empty BTree,
any sequence of m add(x) and remove(x) operations results in a total of O(Bm)
time spent performing splits, merges, and borrows.

（中文关键词：树、摊还分析、B树、外存）
