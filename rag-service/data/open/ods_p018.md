---
structure:
source: open/ods_p018.md
page: 18
---

# ODS p18: §1.2 Introduction

§1.2 Introduction
terfaces implemented by all of the data structures described in this book
and should be considered required reading. The remaining sections dis-
cuss:
• some mathematical review including exponentials, logarithms, fac-
torials, asymptotic (big-Oh) notation, probability, and randomiza-
tion;
• the model of computation;
• correctness, running time, and space;
• an overview of the rest of the chapters; and
• the sample code and typesetting conventions.
A reader with or without a background in these areas can easily skip them
now and come back to them later if necessary.
1.2 Interfaces
When discussing data structures, it is important to understand the dif-
ference between a data structure’s interface and its implementation. An
interface describes what a data structure does, while an implementation
describes how the data structure does it.
Aninterface , sometimes also called an abstract data type , deﬁnes the
set of operations supported by a data structure and the semantics, or
meaning, of those operations. An interface tells us nothing about how
the data structure implements these operations; it only provides a list of
supported operations along with speciﬁcations about what types of argu-
ments each operation accepts and the value returned by each operation.
A data structure implementation , on the other hand, includes the inter-
nal representation of the data structure as well as the deﬁnitions of the
algorithms that implement the operations supported by the data struc-
ture. Thus, there can be many implementations of a single interface. For
example, in Chapter 2, we will see implementations of the List interface
using arrays and in Chapter 3 we will see implementations of the List
interface using pointer-based data structures. Each implements the same
interface, List , but in di ﬀerent ways.
4

（中文关键词：数组、二叉搜索树、概率、随机）
