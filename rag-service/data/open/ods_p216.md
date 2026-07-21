---
structure:
source: open/ods_p216.md
page: 216
---

# ODS p216: §9.2 Red-Black Trees

§9.2 Red-Black Trees
new uu uw
u
pullBlack (w) pullBlack (w)
flipLeft (w) flipRight (w)uw
u v v
v
v
v
vu
u
u
u
uw
w
w
w
wqqq
q
qq.colour
rotateLeft (w)
flipRight (v)
pushBlack (q)v
qv
v
v
v
vw
w
w
w
w
w
wq
q
q
qq.colour
rotateRight (w)
flipLeft (v)
pushBlack (q)v
v
vq qqw
w w
uu u
u u
u
u
uv.left .colour
flipLeft (v)
w(new u)
qw
upushBlack (v)v(new u)w
wflipRight (w)
v.right .colour
v
uwq
v
uwq
vuwqflipLeft (v)v vremoveFixupCase1 (u) removeFixupCase3 (u) removeFixupCase2 (u)
Figure 9.9: A single round in the process of eliminating a double-black node after
a removal.
202

（中文关键词：红黑树、树）
