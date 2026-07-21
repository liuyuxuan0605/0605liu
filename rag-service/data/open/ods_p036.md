---
structure:
source: open/ods_p036.md
page: 36
---

# ODS p36: §1.6 Introduction

§1.6 Introduction
1.6 Code Samples
The code samples in this book are written in the Java programming lan-
guage. However, to make the book accessible to readers not familiar with
all of Java’s constructs and keywords, the code samples have been sim-
pliﬁed. For example, a reader won’t ﬁnd any of the keywords public ,
protected ,private , orstatic . A reader also won’t ﬁnd much discus-
sion about class hierarchies. Which interfaces a particular class imple-
ments or which class it extends, if relevant to the discussion, should be
clear from the accompanying text.
These conventions should make the code samples understandable by
anyone with a background in any of the languages from the ALGOL tradi-
tion, including B, C, C++, C#, Objective-C, D, Java, JavaScript, and so on.
Readers who want the full details of all implementations are encouraged
to look at the Java source code that accompanies this book.
This book mixes mathematical analyses of running times with Java
source code for the algorithms being analyzed. This means that some
equations contain variables also found in the source code. These vari-
ables are typeset consistently, both within the source code and within
equations. The most common such variable is the variable nthat, without
exception, always refers to the number of items currently stored in the
data structure.
1.7 List of Data Structures
Tables 1.1 and 1.2 summarize the performance of data structures in this
book that implement each of the interfaces, List ,USet , and SSet , de-
scribed in Section 1.2. Figure 1.6 shows the dependencies between vari-
ous chapters in this book. A dashed arrow indicates only a weak depen-
dency, in which only a small part of the chapter depends on a previous
chapter or only the main results of the previous chapter.
22