---
structure:
source: open/ods_p196.md
page: 196
---

# ODS p196: §8.2 Scapegoat Trees

§8.2 Scapegoat Trees
ScapegoatTree could be the right choice. This would occur any time
there is additional data associated with nodes that cannot be updated
in constant time when a rotation is performed, but that can be updated
during a rebuild (u) operation. In such cases, the ScapegoatTree and
related structures based on partial rebuilding may work. An example of
such an application is outlined in Exercise 8.11.
Exercise 8.1. Illustrate the addition of the values 1.5 and then 1.6 on the
ScapegoatTree in Figure 8.1.
Exercise 8.2. Illustrate what happens when the sequence 1 ;5;2;4;3 is
added to an empty ScapegoatTree , and show where the credits described
in the proof of Lemma 8.3 go, and how they are used during this sequence
of additions.
Exercise 8.3. Show that, if we start with an empty ScapegoatTree and
calladd(x) for x= 1;2;3;:::;n, then the total time spent during calls to
rebuild (u) is at leastcnlognfor some constant c>0.
Exercise 8.4. The ScapegoatTree , as described in this chapter, guaran-
tees that the length of the search path does not exceed log3=2q.
1. Design, analyze, and implement a modiﬁed version of Scapegoat-
Tree where the length of the search path does not exceed logbq,
where bis a parameter with 1 <b<2.
2. What does your analysis and/or your experiments say about the
amortized cost of find (x),add(x) and remove (x) as a function of
nandb?
Exercise 8.5. Modify the add(x) method of the ScapegoatTree so that it
does not waste any time recomputing the sizes of subtrees that have al-
ready been computed. This is possible because, by the time the method
wants to compute size (w), it has already computed one of size (w:left )
orsize (w:right ). Compare the performance of your modiﬁed implemen-
tation with the implementation given here.
Exercise 8.6. Implement a second version of the ScapegoatTree data
structure that explicitly stores and maintains the sizes of the subtree
182

（中文关键词：替罪羊树、树、摊还分析、复杂度分析）
