---
title: "Lecture 5 - Homogeneous Components, Noether Normalisation, and Polynomial Maps"
stable_id: br-ak-2025-2026-l05
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 5"
upstream_pageid: 165894
upstream_revid: 1051269
upstream_timestamp: "2025-08-18T07:26:27Z"
upstream_mediawiki_sha1: 31f879dfdf7a47a2387eb3fa1200ae7918cc205e
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_5?oldid=1051269"
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-05.csv"
translation_status: complete
---

# Lecture 5: Homogeneous Components, Noether Normalisation, and Polynomial Maps {#br-ak-2025-2026-l05}

## Homogeneous components {#br-ak-2025-2026-l05-s01}

We discuss the degree of a polynomial in several variables and its
decomposition into homogeneous components.

### Definition: degree {#br-ak-2025-2026-l05-def-01}

Let $S$ be a commutative ring and

$$
R=S[X_1,\ldots,X_n]
$$

the polynomial ring in $n$ variables over $S$. For a monomial

$$
G=X^\nu=X_1^{\nu_1}\cdots X_n^{\nu_n},
$$

the number

$$
|\nu|=\sum_{j=1}^n\nu_j
$$

is called the *degree* of $G$. For a nonzero polynomial

$$
F=\sum_\nu a_\nu X^\nu,
$$

the number

$$
\max\{|\nu|:a_\nu\ne0\}
$$

is called the *degree* of $F$.

### Definition: homogeneous decomposition {#br-ak-2025-2026-l05-def-02}

Let $S$ and $R=S[X_1,\ldots,X_n]$ be as above. For a polynomial

$$
F=\sum_\nu a_\nu X^\nu\in R,
$$

the decomposition

$$
F=\sum_{i=0}^d F_i,
$$

where

$$
F_i=\sum_{\substack{\nu\\|\nu|=i}}a_\nu X^\nu,
$$

is called the *homogeneous decomposition* of $F$. The polynomial $F_i$ is
called the *homogeneous component* of $F$ of degree $i$. The polynomial $F$
itself is called *homogeneous* if its homogeneous decomposition has only one
nonzero component.

![A cone: the zero set of a homogeneous polynomial](authority/assets/Kuzel_obecny.svg)

The zero set of a homogeneous polynomial $F$ is a cone of lines through the
origin: if a point $P$ belongs to $V(F)$, the entire line through $P$ and $0$
also belongs to $V(F)$.

### Example: total degree and degree in one variable {#br-ak-2025-2026-l05-ex-01}

The polynomial

$$
F=4X^3YZ^2+2X^2Y^5+5XYZ^7-3X^4YZ^4+X^8-Y^7+2Y^6Z^3+X+5
$$

has degree $9$, with homogeneous components

$$
F_9=5XYZ^7-3X^4YZ^4+2Y^6Z^3,
$$

$$
F_8=X^8,
$$

$$
F_7=2X^2Y^5-Y^7,
$$

$$
F_6=4X^3YZ^2,
$$

$$
F_5=F_4=F_3=F_2=0,
$$

and

$$
F_1=X,
\qquad
F_0=5.
$$

If we regard $F$ as a polynomial in $(K[Y,Z])[X]$ and consider only the
powers of $X$, we speak of its *$X$-degree*. The $X$-degree of $F$ is $8$.
There is also a homogeneous decomposition with respect to the $X$-grading:
the component of $X$-degree zero is

$$
-Y^7+2Y^6Z^3+5,
$$

while the component of $X$-degree one is

$$
5XYZ^7+X.
$$

## The number of points on curves II {#br-ak-2025-2026-l05-s02}

![Emmy Noether (1882-1935)](authority/assets/Noether.jpg)

The following theorem is called *Noether normalisation* in the case of plane curves.

### Theorem: Noether normalisation for plane curves {#br-ak-2025-2026-l05-thm-01}

Let $K$ be an algebraically closed field and $F\in K[X,Y]$ a nonconstant
polynomial of degree $d$ defining the algebraic curve

$$
C=V(F).
$$

There is a linear change of coordinates such that, in the new coordinates
$\widetilde X,\widetilde Y$, the transformed polynomial has the form

$$
\widetilde F=\widetilde X^d+\text{terms of lower degree in }\widetilde X.
$$

#### Proof {#br-ak-2025-2026-l05-thm-01-proof}

Write the homogeneous decomposition

$$
F=F_d+F_{d-1}+\cdots+F_1+F_0,
$$

with

$$
F_i=\sum_{a+b=i}c_{a,b}X^aY^b.
$$

A homogeneous polynomial in two variables has the same factorisation
properties as a polynomial in one variable. Since $K$ is algebraically
closed, there is a factorisation

$$
F_d=c(Y-e_1X)\cdots(Y-e_kX)X^{d-k}.
$$

Since $c$ has a $d$th root, scaling the variables allows us to assume $c=1$.
In particular, $K$ is infinite, so we can choose $e\in K$ distinct from all
the $e_j$. Use the new coordinates

$$
\widetilde Y=Y-eX,
\qquad
\widetilde X=X.
$$

In these coordinates, each linear factor becomes

$$
\begin{aligned}
Y-e_jX
&=Y-eX+eX-e_jX\\
&=\widetilde Y-(e_j-e)X\\
&=\widetilde Y-(e_j-e)\widetilde X,
\end{aligned}
$$

with $e_j-e\ne0$, while the factor $X$ becomes $\widetilde X$. On expanding,
$\widetilde X^d$ occurs with a nonzero coefficient in $K$, which can again
be made $1$ by scaling. The top homogeneous component consequently has the
form $\widetilde X^d$ plus terms of $\widetilde X$-degree at most $d-1$.
Since the lower-degree homogeneous components retain their degrees, all
other monomials also have $\widetilde X$-degree at most $d-1$. $\square$

### Corollary: plane curves have infinitely many points {#br-ak-2025-2026-l05-cor-01}

Let $K$ be an algebraically closed field and $F\in K[X,Y]$ a nonconstant
polynomial defining the algebraic curve $C=V(F)$. Then $C$ has infinitely
many elements.

#### Proof {#br-ak-2025-2026-l05-cor-01-proof}

By Noether normalisation, we may assume that

$$
F=X^d+P_{d-1}(Y)X^{d-1}+\cdots+P_1(Y)X+P_0(Y),
$$

with $P_i(Y)\in K[Y]$. For every prescribed value $a\in K$ of $Y$,
substituting $Y=a$ gives a monic polynomial of degree $d$ in $X$. Since $K$
is algebraically closed, this polynomial has at least one root $b\in K$.
Thus the point with coordinates $X=b$ and $Y=a$ lies on $C$. Since $K$ is
infinite, the curve has infinitely many points. $\square$

**Edition note:** After setting $Y=a$ and choosing a root $X=b$, the source
writes the point as $(a,b)$. This edition specifies both coordinates
explicitly to retain the order $X=b$, $Y=a$.

## Polynomial maps between affine spaces {#br-ak-2025-2026-l05-s03}

Consider the map

$$
\begin{aligned}
\varphi:\mathbb A_K^r&\longrightarrow\mathbb A_K^n,\\
(t_1,\ldots,t_r)&\longmapsto
(\varphi_1(t_1,\ldots,t_r),\ldots,\varphi_n(t_1,\ldots,t_r))
=(x_1,\ldots,x_n),
\end{aligned}
$$

where each component function $\varphi_i\in K[T_1,\ldots,T_r]$ is a
polynomial. Thus each component of the map is given by a polynomial in $r$
variables. The case $n=1$ is a polynomial in $r$ variables; the case $r=1$
and $n=2$ is a parametrisation of an algebraic curve. Later we shall define
morphisms between affine algebraic sets in greater generality.

**Edition note:** The source prints the ring of component functions as
$K[X_1,\ldots,X_r]$, although the map's parameters and the target ring of
its substitution homomorphism use $T_1,\ldots,T_r$. This edition consistently
uses $K[T_1,\ldots,T_r]$.

An important accompanying feature of a polynomial map
$\varphi:\mathbb A_K^r\to\mathbb A_K^n$ is that it induces a $K$-algebra
homomorphism between the polynomial rings in the opposite direction. This
substitution homomorphism is determined by $X_i\mapsto\varphi_i$ and is denoted by

$$
\begin{aligned}
\widetilde\varphi:
K[X_1,\ldots,X_n]&\longrightarrow K[T_1,\ldots,T_r],\\
F&\longmapsto F\circ\varphi
=F(\varphi_i/X_i).
\end{aligned}
$$

The notation $\varphi_i/X_i$ means replacing the variable $X_i$ with
$\varphi_i$. As a function, $F\circ\varphi$ is the composite map

$$
\mathbb A_K^r\xrightarrow{\varphi}\mathbb A_K^n
\xrightarrow{F}\mathbb A_K^1.
$$

For the zero locus $V(F)\subseteq\mathbb A_K^n$, we have

$$
\varphi^{-1}(V(F))=V(\widetilde\varphi(F)).
$$

Apart from constant maps, the simplest polynomial maps are affine-linear
maps, whose component functions are affine-linear polynomials:

$$
\varphi_i=a_{i1}T_1+\cdots+a_{ir}T_r+c_i.
$$

These maps need not be linear, since the origin need not map to the origin:
translations are allowed. An affine-linear map is the composition of a
linear map and a translation. For $r=n$, a bijective affine-linear map is
regarded as a coordinate transformation, or change of variables.

### Definition: affine-linear change of variables {#br-ak-2025-2026-l05-def-03}

Let $K$ be a field. A map $\varphi:\mathbb A_K^n\to\mathbb A_K^n$ of the form

$$
\varphi(x_1,\ldots,x_n)
=M
\begin{pmatrix}
x_1\\
\vdots\\
x_n
\end{pmatrix}
+(v_1,\ldots,v_n),
$$

where $M$ is an invertible matrix, is called an *affine-linear change of variables*.

One can debate whether a linear change of variables actually moves anything
in space or merely changes the coordinates. In either case, such
transformations are important tools for putting a polynomial, a system of
algebraic equations, or an affine algebraic set into a simpler form. Under
a change of variables, the set

$$
V=V(F_1,\ldots,F_m)
$$

becomes

$$
\widetilde V=V(\widetilde F_1,\ldots,\widetilde F_m),
\qquad
\widetilde F_i=\widetilde\varphi(F_i),
$$

and $\widetilde V$ is the inverse image of $V$ under $\varphi$.

### Definition: affine-linear equivalence {#br-ak-2025-2026-l05-def-04}

Two affine algebraic sets

$$
V,\widetilde V\subseteq\mathbb A_K^n
$$

are called *affine-linearly equivalent* if there is an affine-linear change
of variables $\varphi:\mathbb A_K^n\to\mathbb A_K^n$ such that

$$
\varphi^{-1}(V)=\widetilde V.
$$

This notion depends on how the objects are embedded. Later we shall see that
a parabola and a line in the plane are isomorphic, since both are isomorphic
to the affine line, but they are not affine-linearly equivalent.

The essential algebraic and topological properties of an affine algebraic
set are preserved under an affine-linear change of variables: irreducibility,
singularities, intersections, connectedness, and compactness. By contrast,
properties typical of real metric geometry may change: angles, lengths and
ratios of lengths, volumes, and shapes. These latter notions are not relevant
to algebraic geometry. Henceforth we shall transform a situation into a
desired form without special emphasis whenever such a transformation is available.

### Theorem: quotient rings under affine-linear equivalence {#br-ak-2025-2026-l05-thm-02}

Let $K$ be a field and $V,\widetilde V\subseteq\mathbb A_K^n$ two
affine-linearly equivalent affine algebraic sets. Let $\operatorname{Id}(V)$
and $\operatorname{Id}(\widetilde V)$ be their vanishing ideals. Then there
is a $K$-algebra isomorphism

$$
K[X_1,\ldots,X_n]/\operatorname{Id}(V)
\cong
K[X_1,\ldots,X_n]/\operatorname{Id}(\widetilde V).
$$

#### Proof {#br-ak-2025-2026-l05-thm-02-proof}

By definition, there is an affine-linear change of variables

$$
\mathbb A_K^n\longrightarrow\mathbb A_K^n,
\qquad
P\longmapsto\varphi(P),
$$

with $\varphi^{-1}(V)=\widetilde V$. Let $\widetilde\varphi$ be the
corresponding automorphism of $K[X_1,\ldots,X_n]$. Then

$$
\widetilde\varphi^{-1}\bigl(\operatorname{Id}(\widetilde V)\bigr)
=\operatorname{Id}(V).
$$

The isomorphism theorem gives the isomorphism of the two quotient rings. $\square$

### Remark: the coordinate ring as an intrinsic invariant {#br-ak-2025-2026-l05-rem-01}

The preceding theorem expresses an important principle of algebraic geometry:
the algebraic object attached to a zero locus is the quotient of the
polynomial ring by its vanishing ideal. This is an *intrinsic invariant* of
the zero locus, independent of its embedding.

From this perspective, Noether normalisation for plane curves takes on new
meaning. We may assume that the curve equation has the form

$$
F=X^d+P_{d-1}(Y)X^{d-1}+\cdots+P_1(Y)X+P_0(Y).
$$

The equation $F=0$ is an equation of integral dependence for the residue
class of $X$. More precisely, the residue class of $X$ in $K[X,Y]/(F)$ is
integral over $K[Y]$. These notions may be familiar from elementary number
theory and will again play an important role here. Since $X$ generates the
ring as an algebra over $K[Y]$, there is an integral, indeed finite, ring extension

$$
K[Y]\longrightarrow
K[X,Y]/\bigl(X^d+P_{d-1}(Y)X^{d-1}+\cdots+P_1(Y)X+P_0(Y)\bigr).
$$

Thus Noether normalisation also says that, for every algebraic curve over
an algebraically closed field, its coordinate ring can be realised as a
finite extension of the principal ideal domain $K[Y]$. This is a direct
analogy with rings of integers in number theory, which are likewise finite
extensions of the principal ideal domain $\mathbb Z$.

Under general polynomial maps between affine spaces, unlike affine-linear
transformations, many algebraic properties may change: dimension may change,
singularities may arise, and so on. Irreducibility, however, passes to the
Zariski closure of the image.

### Theorem: the closure of the image of a polynomial map is irreducible {#br-ak-2025-2026-l05-thm-03}

Let $K$ be an infinite field and

$$
\varphi:\mathbb A_K^r\longrightarrow\mathbb A_K^n
$$

a map given by $n$ polynomials in $r$ variables. Then the Zariski closure of
the image of $\varphi$ is irreducible.

#### Proof {#br-ak-2025-2026-l05-thm-03-proof}

Let

$$
B=\varphi(\mathbb A_K^r)
$$

be the image of the map. By Lemma 3.10,

$$
\overline B=V(\operatorname{Id}(B)).
$$

For $P=\varphi(Q)$ with $Q\in\mathbb A_K^r$ and
$F\in K[X_1,\ldots,X_n]$, we have

$$
F(P)=F(\varphi(Q))=(F\circ\varphi)(Q),
$$

where $F\circ\varphi\in K[T_1,\ldots,T_r]$ is obtained by replacing $X_i$
with the $i$th component function $\varphi_i\in K[T_1,\ldots,T_r]$.
Consequently, $F$ vanishes throughout $B$ precisely when $F\circ\varphi$
vanishes throughout $\mathbb A_K^r$. Since $K$ is infinite, the latter
condition means that $F\circ\varphi$ is the zero polynomial.

Thus

$$
F\in\operatorname{Id}(B)
$$

precisely when $F$ maps to zero under the homomorphism

$$
\widetilde\varphi:
K[X_1,\ldots,X_n]\longrightarrow K[T_1,\ldots,T_r].
$$

Hence $\operatorname{Id}(B)$ is the inverse image of a prime ideal, namely
the zero ideal in $K[T_1,\ldots,T_r]$, and so is itself prime by Exercise
4.19. Lemma 4.3 then shows that $V(\operatorname{Id}(B))$ is irreducible. $\square$
