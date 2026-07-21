---
structure:
source: open/ods_p027.md
page: 27
---

# ODS p27: Mathematical Background §1.3

Mathematical Background §1.3
A number of useful shortcuts can be applied when using asymptotic
notation. First:
O(nc1)O(nc2);
for anyc1<c2. Second: For any constants a;b;c> 0,
O(a)O(logn)O(nb)O(cn):
These inclusion relations can be multiplied by any positive value, and
they still hold. For example, multiplying by nyields:
O(n)O(nlogn)O(n1+b)O(ncn):
Continuing in a long and distinguished tradition, we will abuse this
notation by writing things like f1(n) =O(f(n)) when what we really mean
isf1(n)2O(f(n)). We will also make statements like “the running time
of this operation is O(f(n))” when this statement should be “the running
time of this operation is a member of O(f(n)).” These shortcuts are mainly
to avoid awkward language and to make it easier to use asymptotic nota-
tion within strings of equations.
A particularly strange example of this occurs when we write state-
ments like
T(n) = 2logn+O(1):
Again, this would be more correctly written as
T(n)2logn+ [some member of O(1)]:
The expression O(1) also brings up another issue. Since there is no
variable in this expression, it may not be clear which variable is getting
arbitrarily large. Without context, there is no way to tell. In the example
above, since the only variable in the rest of the equation is n, we can
assume that this should be read as T(n) = 2logn+O(f(n)), wheref(n) = 1.
Big-Oh notation is not new or unique to computer science. It was used
by the number theorist Paul Bachmann as early as 1894, and is immensely
useful for describing the running times of computer algorithms. Consider
the following piece of code:
13