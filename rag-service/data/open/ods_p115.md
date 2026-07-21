---
structure:
source: open/ods_p115.md
page: 115
---

# ODS p115: Analysis of Skiplists §4.4

Analysis of Skiplists §4.4
time, if the path can go up a level, then it does. If it cannot go up a level
then it goes left. Thinking about this for a few moments will convince
us that the reverse search path for xis identical to the search path for x,
except that it is reversed.
The number of nodes that the reverse search path visits at a particular
level, r, is related to the following experiment: Toss a coin. If the coin
comes up as heads, then move up and stop. Otherwise, move left and
repeat the experiment. The number of coin tosses before the heads rep-
resents the number of steps to the left that a reverse search path takes at
a particular level.3Lemma 4.2 tells us that the expected number of coin
tosses before the ﬁrst heads is 1.
LetSrdenote the number of steps the forward search path takes at
level rthat go to the right. We have just argued that E[ Sr]1. Further-
more,SrjLrj, since we can’t take more steps in Lrthan the length of Lr,
so
E[Sr]E[jLrj] =n=2r:
We can now ﬁnish as in the proof of Lemma 4.4. Let Sbe the length of
the search path for some node, u, in a skiplist, and let hbe the height of
the skiplist. Then
E[S] = E2
666664h+1X
r=0Sr3
777775
= E[h] +1X
r=0E[Sr]
= E[h] +blogncX
r=0E[Sr] +1X
r=blognc+1E[Sr]
E[h] +blogncX
r=01 +1X
r=blognc+1n=2r
E[h] +blogncX
r=01 +1X
r=01=2r
3Note that this might overcount the number of steps to the left, since the experiment
should end either at the ﬁrst heads or when the search path reaches the sentinel, whichever
comes ﬁrst. This is not a problem since the lemma is only stating an upper bound.
101

（中文关键词：跳表、复杂度分析）
