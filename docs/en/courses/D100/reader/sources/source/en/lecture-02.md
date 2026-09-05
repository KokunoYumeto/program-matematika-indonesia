---
title: "Lecture 2 — Affine Algebraic Sets"
stable_id: br-ak-2025-2026-l02
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 2"
upstream_pageid: 165891
upstream_revid: 1055217
upstream_timestamp: "2025-10-10T09:51:04Z"
upstream_mediawiki_sha1: be3bd8706fc4945584860560ee832690f17184ab
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_2?oldid=1055217"
license: "CC BY-SA 4.0 for translated course text; media retain component licences in authority/RIGHTS-unit-02.csv"
translation_status: complete
---

# Lecture 2: Affine Algebraic Sets {#br-ak-2025-2026-l02}

## Affine algebraic sets {#br-ak-2025-2026-l02-s01}

### Definition: affine space {#br-ak-2025-2026-l02-def-01}

Let $K$ be a field. The space

$$
\mathbb A_K^n=K^n
$$

is called *affine space* of dimension $n$ over $K$.

Thus, to begin with, affine space is simply a set of points. A point in affine
space is an $n$-tuple $(a_1,\ldots,a_n)$ with coordinates in $K$. Why, then,
introduce a new term? The term “affine space” indicates that we wish to regard
$K^n$ as an object of algebraic geometry. In other words, we regard
$n$-dimensional affine space as the natural geometric object on which
polynomials in $n$ variables act as functions. We shall gradually equip affine
space with further structures—the Zariski topology and the structure sheaf—which
make it clear that it is “more” than “just” $K^n$. For $n=1$ we speak of the
*affine line*, and for $n=2$ of the *affine plane*.

A polynomial $F\in K[X_1,\ldots,X_n]$ can naturally be regarded as a function
on affine space. To a point

$$
P=(a_1,\ldots,a_n)\in\mathbb A_K^n,
$$

we assign the value

$$
F(P)=F(a_1,\ldots,a_n)
$$

by replacing each variable $X_i$ by $a_i$ and carrying out all the operations
in $K$. Given a polynomial $F\in K[X_1,\ldots,X_n]$, we can ask whether
$F(P)=0$. One object of particular interest associated with $F$ is therefore
the zero locus it defines,

$$
V(F)=\{P\in\mathbb A_K^n\mid F(P)=0\}.
$$

We encountered several examples in the first lecture. It is also useful,
however, to study the common, or simultaneous, zero locus of several
polynomials. This is the intersection of their individual zero loci—for
example, in the case of conic sections, where a cone in three-dimensional
space is intersected with various planes.

![Conic sections](authority/assets/Conic_sections_2n-330.png)

We therefore make the following general definition.

### Definition: the zero locus of a family of polynomials {#br-ak-2025-2026-l02-def-02}

Let $K$ be a field, and let

$$
F_j\in K[X_1,\ldots,X_n],\qquad j\in J,
$$

be a family of polynomials in $n$ variables. The set

$$
\{P\in\mathbb A_K^n\mid F_j(P)=0\text{ for every }j\in J\}
$$

is called the *zero locus* (or *zero set*) defined by the family. It is denoted
by $V(F_j,j\in J)$.

Those subsets of affine space that arise as zero sets deserve a name of their own.

### Definition: affine algebraic set {#br-ak-2025-2026-l02-def-03}

Let $K$ be a field and $K[X_1,\ldots,X_n]$ the polynomial ring in $n$
variables. A subset $V\subseteq\mathbb A_K^n$ is called an *affine algebraic
set* if it is the zero set of a family of polynomials $F_j$, $j\in J$, with
$F_j\in K[X_1,\ldots,X_n]$; that is, if

$$
V=V(F_j,j\in J).
$$

The simplest examples are finite sets of points on the affine line
$\mathbb A_K^1$, each given by a single polynomial, and affine linear
subspaces of $\mathbb A_K^n$, which are the solution sets of inhomogeneous
systems of linear equations over $K$.

### Example: the axes and the origin {#br-ak-2025-2026-l02-ex-01}

Consider the affine plane $\mathbb A_K^2$ and some affine algebraic subsets
defined by the variables $X$ and $Y$.

- The zero locus $V(X,Y)$ consists only of the *origin* $(0,0)$, since both
  variables must be zero.
- The set $V(X)$ is the *$Y$-axis*: all points of the form $(0,y)$.
- The set $V(Y)$ is the *$X$-axis*.
- The set $V(X+Y)$ consists of all points $(x,y)$ with $y=-x$: it is the
  *antidiagonal*.
- The set $V(XY)$ consists of the points $(x,y)$ with $xy=0$. Since $K$ is a
  field, a product can be zero only if one of its factors is zero (Lemma 3.10
  of Linear Algebra, Osnabrück 2024–2025). Thus

  $$
  V(XY)=V(X)\cup V(Y),
  $$

  the union of the two coordinate axes.

Points in affine space or on an affine algebraic set are often interpreted as
representing more complicated mathematical objects. Properties of those
objects are then reflected in whether their representing points satisfy
certain algebraic equations or, equivalently, lie on certain affine algebraic
sets. The following example illustrates this idea.

### Example: matrices as points of affine space {#br-ak-2025-2026-l02-ex-02}

A $2\times2$ matrix

$$
\begin{pmatrix}
a_{11}&a_{21}\\
a_{12}&a_{22}
\end{pmatrix}
$$

is uniquely determined by the four numbers $a_{11},a_{21},a_{12},a_{22}\in K$.
It can therefore be identified with a point of $\mathbb A_K^4$. In this
interpretation, it is natural to denote the variables by
$X_{11},X_{21},X_{12},X_{22}$. We can now ask which properties of matrices can
be described by algebraic equations. We discuss several typical properties.

A matrix is upper triangular precisely when $a_{12}=0$. Thus the set of upper
triangular matrices is the zero locus of $X_{12}$.

A matrix is invertible when

$$
a_{11}a_{22}-a_{12}a_{21}\ne0.
$$

Consequently, the set of non-invertible matrices is described by the algebraic
determinant condition

$$
X_{11}X_{22}-X_{12}X_{21}=0.
$$

A matrix describes multiplication by a scalar if it is diagonal with equal
diagonal entries. This set is described by the three equations

$$
X_{12}=0,\qquad X_{21}=0,\qquad X_{11}-X_{22}=0.
$$

An element $\lambda\in K$ is an eigenvalue of a matrix precisely when it is
a root of its characteristic polynomial (Theorem 23.2 of Linear Algebra,
Osnabrück 2024–2025), that is, when

$$
\det\begin{pmatrix}
\lambda-a_{11}&-a_{21}\\
-a_{12}&\lambda-a_{22}
\end{pmatrix}
=\lambda^2-\lambda(a_{11}+a_{22})+a_{11}a_{22}-a_{12}a_{21}=0.
$$

In linear algebra, the matrix is usually given and we seek roots $\lambda$
of this polynomial in one variable. We can also reverse the viewpoint: fix
$\lambda$ and study the zero locus

$$
\lambda^2-\lambda(X_{11}+X_{22})
+X_{11}X_{22}-X_{12}X_{21}=0
$$

in four variables. This equation describes all matrices having $\lambda$ as
an eigenvalue.

Similarly, a matrix has the two distinct eigenvalues $\lambda\ne\delta$
precisely when

$$
\lambda^2-\lambda(X_{11}+X_{22})
+X_{11}X_{22}-X_{12}X_{21}=0
$$

and

$$
\delta^2-\delta(X_{11}+X_{22})
+X_{11}X_{22}-X_{12}X_{21}=0.
$$

Subtracting the two equations gives

$$
\lambda^2-\delta^2-(\lambda-\delta)(X_{11}+X_{22})=0,
$$

which such a matrix must also satisfy. Since $\lambda\ne\delta$, we can
write this as

$$
X_{11}+X_{22}=\lambda+\delta.
$$

The sum of a matrix's diagonal entries is called its *trace*. The last
equation therefore says that the trace of a matrix with eigenvalues
$\lambda\ne\delta$ must equal their sum.

The characteristic polynomial of a matrix can also be written as

$$
\lambda^2-\lambda\operatorname{Trace}(M)+\det(M),
$$

where

$$
\operatorname{Trace}(M)=X_{11}+X_{22},\qquad
\det(M)=X_{11}X_{22}-X_{12}X_{21}.
$$

Thus two matrices have the same characteristic polynomial precisely when they
have the same trace and determinant. The set of matrices with a prescribed
characteristic polynomial can therefore be regarded as a fibre of the map

$$
\mathbb A_K^4\longrightarrow\mathbb A_K^2,
\qquad M\longmapsto(\operatorname{Trace}(M),\det(M)).
$$

This map is given by simple polynomial expressions. Is it surjective? Do its
fibres always look alike—that is, does the set of matrices with a prescribed
trace and determinant always have the same structure—or are there differences?

Fix $s$ and $d$. We must study the solution set of the system

$$
X_{11}+X_{22}=s,
\qquad
X_{11}X_{22}-X_{12}X_{21}=d.
$$

The variable $X_{11}$ is uniquely determined by $X_{22}$, and conversely. We
can therefore *eliminate* one variable by putting $X_{22}=s-X_{11}$. This
gives an “equivalent” system in the three variables $X_{11},X_{12},X_{21}$
with the single equation

$$
X_{11}(s-X_{11})-X_{12}X_{21}=d,
$$

or

$$
X_{11}^2-sX_{11}+X_{12}X_{21}+d=0.
$$

Here “equivalent” means that the two solution sets are in bijection through
maps given by polynomials. The last form shows that a solution always exists:
we may choose any value of $X_{11}$ and obtain an equation of the form
$X_{12}X_{21}=a$, which has solutions.

A linear change of variables simplifies the equation further. Suppose that
$2$ is invertible in $K$, so the characteristic of $K$ is not $2$. With

$$
X=X_{11}-\frac{s}{2},\qquad Y=X_{12},\qquad Z=X_{21},
$$

we obtain

$$
X^2+YZ+c=0,
\qquad
c=-\frac{s^2}{4}+d.
$$

Thus the shape of the set of matrices with a prescribed trace and determinant
depends only on $-s^2/4+d$. Indeed, the zero locus differs according to whether
this expression is zero or nonzero. In the first case it has a singularity;
in the second it does not, as we shall see later.

## Ideals and zero loci {#br-ak-2025-2026-l02-s02}

Since for now we allow arbitrary families of polynomials to define zero loci
and hence affine algebraic sets, these objects initially seem difficult to
get a handle on. Three important statements nevertheless hold, which we
shall prove in stages.

1. The zero locus of a family of polynomials equals the zero locus of the
   ideal generated by that family.
2. Every ideal has a finite set of generators. Thus every zero locus can be
   described by finitely many polynomials (Hilbert's basis theorem).
3. Over an algebraically closed field, zero loci correspond bijectively to
   radical ideals, a special class of ideals (Hilbert's Nullstellensatz).

We can prove the first statement immediately. The other two require some
algebraic preparation, which we shall develop in the following lectures.

### Lemma: a family of polynomials and the ideal it generates {#br-ak-2025-2026-l02-lem-01}

Let $K$ be a field and $F_j\in K[X_1,\ldots,X_n]$, $j\in J$, a family of
polynomials in $n$ variables. Let $\mathfrak a$ be the ideal of
$K[X_1,\ldots,X_n]$ generated by all the $F_j$. Then

$$
V(F_j,j\in J)=V(\mathfrak a).
$$

#### Proof {#br-ak-2025-2026-l02-lem-01-proof}

The ideal $\mathfrak a$ consists of all finite linear combinations of the
polynomials $F_j$ and in particular contains every $F_j$. The inclusion

$$
V(F_j,j\in J)\supseteq V(\mathfrak a)
$$

is therefore clear. For the reverse inclusion, take $P\in V(F_j,j\in J)$ and
$H\in\mathfrak a$. There are polynomials $A_i\in K[X_1,\ldots,X_n]$ and
indices $j_1,\ldots,j_k$ such that

$$
H=\sum_{i=1}^k A_iF_{j_i}.
$$

Then

$$
H(P)=\sum_{i=1}^k A_i(P)F_{j_i}(P)=0.
$$

Thus every element of the ideal vanishes at $P$, so
$P\in V(\mathfrak a)$. $\square$

Henceforth, then, we may assume that every zero set is given by an ideal.

### Lemma: inclusion of ideals reverses inclusion of zero loci {#br-ak-2025-2026-l02-lem-02}

For ideals $\mathfrak a\subseteq\mathfrak b$ in $K[X_1,\ldots,X_n]$, the
corresponding zero loci satisfy

$$
V(\mathfrak a)\supseteq V(\mathfrak b).
$$

#### Proof {#br-ak-2025-2026-l02-lem-02-proof}

Take $P\in V(\mathfrak b)$. This means that $F(P)=0$ for every
$F\in\mathfrak b$. Since $\mathfrak a\subseteq\mathfrak b$, it follows in
particular that $F(P)=0$ for every $F\in\mathfrak a$. Thus
$P\in V(\mathfrak a)$. $\square$

Affine algebraic subsets of affine space have the following important
structural properties.

### Proposition: unions and intersections of affine algebraic sets {#br-ak-2025-2026-l02-prop-01}

Let $K$ be a field, $K[X_1,\ldots,X_n]$ the polynomial ring in $n$ variables,
and $\mathbb A_K^n$ the corresponding affine space. The following properties hold.

1. $V(0)=\mathbb A_K^n$: the whole affine space is an affine algebraic set.
2. $V(1)=\varnothing$: the empty set is an affine algebraic set.
3. If $V_1,\ldots,V_k$ are affine algebraic sets with $V_i=V(\mathfrak a_i)$, then

   $$
   V_1\cup V_2\cup\cdots\cup V_k
   =V(\mathfrak a_1\mathfrak a_2\cdots\mathfrak a_k).
   $$

   In particular, a finite union of affine algebraic sets is again an affine
   algebraic set.
4. If $V_i$, $i\in I$, are affine algebraic sets with $V_i=V(\mathfrak a_i)$, then

   $$
   \bigcap_{i\in I}V_i=V\left(\sum_{i\in I}\mathfrak a_i\right).
   $$

   In particular, an arbitrary intersection of affine algebraic sets is again
   an affine algebraic set.

#### Proof {#br-ak-2025-2026-l02-prop-01-proof}

Statements (1) and (2) are clear: the constant polynomial $0$ vanishes
everywhere, whereas the constant polynomial $1$ vanishes nowhere.

For (3), take a point in the union, say $P\in V(\mathfrak a_1)$. Then
$f(P)=0$ for every $f\in\mathfrak a_1$. Every element of the product ideal
$\mathfrak a_1\cdots\mathfrak a_k$ has the form

$$
h=\sum_{j=1}^m r_j f_{1j}f_{2j}\cdots f_{kj},
$$

with $f_{ij}\in\mathfrak a_i$. Since $f_{1j}(P)=0$ in every term, we get
$h(P)=0$. Thus $P$ belongs to the zero locus on the right.

Conversely, suppose that $P$ does not belong to the union on the left. Then
$P\notin V(\mathfrak a_i)$ for every $i=1,\ldots,k$. For each $i$ there is an
$f_i\in\mathfrak a_i$ with $f_i(P)\ne0$. Since $K$ is a field,

$$
(f_1f_2\cdots f_k)(P)\ne0,
$$

while $f_1f_2\cdots f_k\in\mathfrak a_1\cdots\mathfrak a_k$. Therefore $P$
cannot belong to the zero locus on the right.

For (4), take $P\in\mathbb A_K^n$. The point $P$ belongs to
$V(\mathfrak a_i)$ for every $i\in I$ precisely when $f(P)=0$ for every
$f\in\mathfrak a_i$ and every $i\in I$. This holds precisely when $f(P)=0$
for every $f$ in the sum of these ideals. $\square$

![Examples of algebraic sets](authority/assets/Conjuntos_algebraicos_2.svg)

---

**Source navigation:** [course](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)) · [Lecture 1](#br-ak-2025-2026-l01) · [Lecture 3 (source)](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_3) · [Worksheet 2](#br-ak-2025-2026-w02)
