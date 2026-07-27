---
structure:
source: open/ods_p209.md
page: 209
---

# ODS p209: RedBlackTree : A Simulated 2-4 Tree §9.2

RedBlackTree : A Simulated 2-4 Tree §9.2
u
upushBlack (u)
⇓u
upullBlack (u)
⇓flipLeft (u)
⇓u
uflipRight (u)
⇓
uu
Figure 9.7: Flips, pulls and pushes
RedBlackTree
void pushBlack(Node<T> u) {
u.colour--;
u.left.colour++;
u.right.colour++;
}
void pullBlack(Node<T> u) {
u.colour++;
u.left.colour--;
u.right.colour--;
}
TheflipLeft (u) method swaps the colours of uandu:right and then
performs a left rotation at u. This method reverses the colours of these
two nodes as well as their parent-child relationship:
RedBlackTree
void flipLeft(Node<T> u) {
swapColors(u, u.right);
rotateLeft(u);
}
The flipLeft (u) operation is especially useful in restoring the left-
leaning property at a node uthat violates it (because u:left is black and
u:right is red). In this special case, we can be assured that this oper-
ation preserves both the black-height and no-red-edge properties. The
195

（中文关键词：2-4树、树）
