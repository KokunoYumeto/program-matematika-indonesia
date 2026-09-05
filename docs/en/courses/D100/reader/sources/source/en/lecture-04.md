---
title: "Lecture 4 - Irreducibility, Components, and Intersections of Curves"
stable_id: br-ak-2025-2026-l04
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 4"
upstream_pageid: 165893
upstream_revid: 1112250
upstream_timestamp: "2026-08-20T16:46:15Z"
upstream_mediawiki_sha1: 5931f665f4ab4e6180050ddde5164d5edc94e37a
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_4?oldid=1112250"
license: "CC BY-SA 4.0 for translated course text; media retain component licences in authority/RIGHTS-unit-04.csv"
translation_status: complete
---

# Lecture 4: Irreducibility, Components, and Intersections of Curves {#br-ak-2025-2026-l04}

## Irreducible affine algebraic sets {#br-ak-2025-2026-l04-s01}

### Definition: irreducible set {#br-ak-2025-2026-l04-def-01}

An affine algebraic set

$$
V\subseteq\mathbb A_K^n
$$

is called *irreducible* if $V\ne\varnothing$ and there is no decomposition

$$
V=Y\cup Z
$$

with affine algebraic sets $Y,Z\subsetneq V$.

Thus a Zariski closed set $V$ is irreducible precisely when
$V\ne\varnothing$ and every decomposition $V=Y\cup Z$ forces $V=Y$ or $V=Z$.
The same immediately follows for every finite expression as a union of closed sets.

Irreducibility is a purely topological property. In a general topological
space, the preceding definition is formulated using closed sets in place of
affine algebraic sets, which are the closed sets of the Zariski topology.

The following pictures show some irreducible and some reducible affine
algebraic subsets. What are their irreducible components (see the definition below)?

![Points for a Delaunay triangulation](authority/assets/Delaunay_points.png)

![A line](authority/assets/Gerade.svg)

![Several straight lines](authority/assets/Straight_lines.svg)

![A linear space](authority/assets/Linear_space2.png)

### Example: affine space {#br-ak-2025-2026-l04-ex-01}

Consider affine space $\mathbb A_K^n$. If $K$ is finite, this space consists
of only finitely many points, and only its one-point subsets are irreducible.
In particular, except when $n=0$, affine space is not irreducible.

If $K$ is infinite, on the other hand, affine space $\mathbb A_K^n$ is
irreducible. Suppose that

$$
\mathbb A_K^n=Y\cup Z
$$

with $Y$ and $Z$ both proper affine algebraic subsets. Their open complements,

$$
U=\mathbb A_K^n\setminus Y,
\qquad
W=\mathbb A_K^n\setminus Z,
$$

satisfy $U,W\ne\varnothing$, but $U\cap W=\varnothing$. This contradicts
Exercise 3.20.

### Lemma: irreducibility and prime ideals {#br-ak-2025-2026-l04-lem-01}

Let $V\subseteq\mathbb A_K^n$ be an affine algebraic set with vanishing
ideal $\operatorname{Id}(V)$. Then $V$ is irreducible if and only if
$\operatorname{Id}(V)$ is a prime ideal.

#### Proof {#br-ak-2025-2026-l04-lem-01-proof}

First suppose that $\operatorname{Id}(V)$ is not prime. If

$$
\operatorname{Id}(V)=K[X_1,\ldots,X_n],
$$

then $V=\varnothing$, so $V$ is not irreducible by definition. Otherwise there
are polynomials

$$
F,G\in K[X_1,\ldots,X_n]
$$

with

$$
FG\in\operatorname{Id}(V),
\qquad
F,G\notin\operatorname{Id}(V).
$$

Hence there are $P,Q\in V$ with $F(P)\ne0$ and $G(Q)\ne0$. Form the two ideals

$$
\mathfrak a_1=\operatorname{Id}(V)+(F),
\qquad
\mathfrak a_2=\operatorname{Id}(V)+(G).
$$

By Lemma 3.8(3),

$$
V(\mathfrak a_1),V(\mathfrak a_2)
\subseteq V(\operatorname{Id}(V))=V.
$$

Both inclusions are proper because $P\notin V(\mathfrak a_1)$ and
$Q\notin V(\mathfrak a_2)$. On the other hand,

$$
V(\mathfrak a_1)\cup V(\mathfrak a_2)
=V(\mathfrak a_1\mathfrak a_2)
=V(\operatorname{Id}(V))
=V.
$$

Thus $V$ has a nontrivial decomposition and is not irreducible.

Now suppose that $V$ is not irreducible. If $V=\varnothing$, then
$\operatorname{Id}(V)$ is the whole ring and is not prime. Suppose, then,
that $V\ne\varnothing$ and

$$
V=Y\cup Z
$$

is a nontrivial decomposition. Write

$$
Y=V(\mathfrak a_1),
\qquad
Z=V(\mathfrak a_2).
$$

Since $Y\subsetneq V$, there is a point

$$
P\in V=V(\operatorname{Id}(V)),
\qquad
P\notin V(\mathfrak a_1).
$$

There is therefore an $F\in\mathfrak a_1$ with $F(P)\ne0$, so
$F\notin\operatorname{Id}(V)$. Similarly, there is a $G\in\mathfrak a_2$
with $G\notin\operatorname{Id}(V)$. For every $Q\in V=Y\cup Z$, we have
$(FG)(Q)=0$, since $F$ vanishes on $Y$ and $G$ on $Z$. Thus

$$
FG\in\operatorname{Id}(V),
$$

although neither factor belongs to the ideal. Consequently
$\operatorname{Id}(V)$ is not prime. $\square$

### Definition: irreducible component {#br-ak-2025-2026-l04-def-02}

Let $V$ be an affine algebraic set. An affine algebraic subset $W\subseteq V$
is called an *irreducible component* of $V$ if $W$ is irreducible and there
is no irreducible subset $W'$ with

$$
W\subsetneq W'\subseteq V.
$$

If $V$ is irreducible, then $V$ itself is its only irreducible component.
In Theorem 9.11 we shall prove that every affine algebraic set can be written
as a finite union of irreducible components.

### Example: behaviour over the real and complex numbers {#br-ak-2025-2026-l04-ex-02}

Consider the equation

$$
F=Y^2+X^2(X+1)^2=0.
$$

Over the real numbers, this equation has two solutions. Since a real square
is never negative, $F$ can be zero only when both summands are zero. Hence
$Y=0$ and either $X=0$ or $X=-1$. In particular, the real solution set is
neither connected nor irreducible; its vanishing ideal in the real setting
is also very large.

Over the complex numbers, there is a factorisation

$$
F=(Y+iX(X+1))(Y-iX(X+1))
$$

into irreducible polynomials. This also shows that $F$, as a polynomial in
$\mathbb R[X,Y]$, is irreducible, even though its real zero locus is not
irreducible. Its complex zero locus consists of the two graphs

$$
Y=\pm iX(X+1),
$$

which intersect at $(0,0)$ and $(-1,0)$.

For the equation

$$
Y^2+Z^2+X^2(X+1)^2=0
$$

there are again only two real solution points, whereas the polynomial is
irreducible over both the real and the complex numbers.

![Hydrant on the island of Krk, Croatia](authority/assets/Hydrant_Insel_Krk_Kroatien-500.jpg)

### Example: the intersection of two congruent cylinders {#br-ak-2025-2026-l04-ex-03}

In affine space $\mathbb A_K^3$ with $K=\mathbb R$, consider the two cylinders

$$
S_1=\{(x,y,z)\mid x^2+y^2=1\},
\qquad
S_2=\{(x,y,z)\mid y^2+z^2=1\}.
$$

Both are irreducible sets, as we shall see later for infinite $K$. What does
their intersection look like? It is described by the ideal $\mathfrak a$
generated by $X^2+Y^2-1$ and $Y^2+Z^2-1$. Subtracting one equation from the
other gives

$$
X^2-Z^2=(X-Z)(X+Z)\in\mathfrak a.
$$

Neither factor itself belongs to $\mathfrak a$. For example, $(1,0,-1)$ is
a point of the intersection at which $X-Z$ does not vanish (in characteristic
$\ne2$), while $(1,0,1)$ is a point at which $X+Z$ does not vanish. The
components of the intersection are instead described by

$$
\mathfrak b_1=\mathfrak a+(X-Z),
\qquad
\mathfrak b_2=\mathfrak a+(X+Z).
$$

Both are prime ideals, and the first quotient ring is

$$
\begin{aligned}
K[X,Y,Z]/\mathfrak b_1
&=K[X,Y,Z]/(\mathfrak a+(X-Z))\\
&\cong K[X,Y]/(X^2+Y^2-1).
\end{aligned}
$$

To see the last isomorphism, eliminate $Z$ using $X-Z=0$; the two cylinder
equations then become identical. The argument for the other ideal is the
same. Geometrically, every point of $S_1\cap S_2$ lies in the plane

$$
E_1=V(Z-X)
\qquad\text{or}\qquad
E_2=V(Z+X).
$$

Moreover,

$$
E_1\cap S_1=E_1\cap S_1\cap S_2=E_1\cap S_2,
$$

and likewise for $E_2$, since on each of these planes the two cylinder
equations become identical.

**Edition note:** At this point the source repeats $E_1$; the second plane is $E_2=V(Z+X)$, as used here.

What do these intersections look like within their planes? On $E_1$, use the
coordinates $Y$ and $U=Z+X$. Since

$$
X=\frac12((Z+X)-(Z-X)),
$$

the first cylinder equation can be written as

$$
\left(\frac12((Z+X)-(Z-X))\right)^2+Y^2=1.
$$

On the plane $E_1$, where $Z=X$, this becomes

$$
\left(\frac12U\right)^2+Y^2=1,
$$

or

$$
\frac14U^2+Y^2=1.
$$

This is the equation of an ellipse, as is also geometrically apparent. The
earlier calculation of $K[X,Y,Z]/\mathfrak b_1$, however, gave a circle
equation. There is no contradiction: a circle and an ellipse can be
transformed into each other by a linear change of variables, so their
quotient rings are isomorphic. As metric objects they are different, and the
intersection of these two cylinders consists of two ellipses. An orthonormal
change of variables preserves the metric structure, but the variables $Y$,
$X+Z$, and $X-Z$ do not define an orthonormal transformation.

Thus

$$
S_1\cap S_2=V(\mathfrak b_1)\cup V(\mathfrak b_2),
$$

where

$$
\mathfrak b_1=(X^2+Y^2-1,X-Z),
\qquad
\mathfrak b_2=(X^2+Y^2-1,X+Z),
$$

describe two ellipses. To determine how the ellipses intersect, calculate the
sum of their ideals:

$$
\begin{aligned}
\mathfrak b_1+\mathfrak b_2
&=(X^2+Y^2-1,X-Z,X+Z)\\
&=(Y^2-1,X,Z).
\end{aligned}
$$

Its zero locus consists of the two points $(0,1,0)$ and $(0,-1,0)$.

![Principal directions on a cylinder](authority/assets/Cylinder_principal_directions-250.png)

## The number of points on curves {#br-ak-2025-2026-l04-s02}

We have already seen that the intersection of a curve and a line consists
of only finitely many points, unless the line itself is a component of the
curve; see Lemma 1.3. We shall now generalise this to the intersection of two
arbitrary plane curves. We need the following definition.

### Definition: rational function field {#br-ak-2025-2026-l04-def-03}

Let $K$ be a field and $K[X]$ the polynomial ring in one variable over $K$.
The field of fractions $Q(K[X])$ is called the *rational function field*
(or *field of rational functions*) over $K$ and is denoted by

$$
K(X).
$$

### Theorem: intersection of curves without a common component {#br-ak-2025-2026-l04-thm-01}

Let $K$ be a field, and let

$$
F,G\in K[X,Y]
$$

be two polynomials without a common nonconstant factor. Then $V(F,G)$
contains only finitely many points $P_1,\ldots,P_n$.

#### Proof {#br-ak-2025-2026-l04-thm-01-proof}

Regard $F,G\in K[X,Y]$ as elements of $K(X)[Y]$, where $K(X)$ is the field
of rational functions in $X$. By Exercise 4.27, $F$ and $G$ also have no
common nonconstant factor in $K(X)[Y]$. Since this ring is a principal ideal
domain, they generate the unit ideal. Thus there are

$$
A,B\in K(X)[Y]
$$

with

$$
AF+BG=1.
$$

Multiplying by a common denominator of $A$ and $B$ gives, in $K[X,Y]$,

$$
\widetilde A F+\widetilde B G=H,
\qquad
0\ne H\in K[X].
$$

Every common zero of $F$ and $G$ in $\mathbb A_K^2$ must be a zero of $H$.
Thus only finitely many $X$-values can occur at common zeros. Interchanging
$X$ and $Y$ shows that only finitely many $Y$-values can occur as well.
Consequently, there are only finitely many common zeros altogether. $\square$

![Two cubic curves](authority/assets/Two_cubic_curves.png)

### Corollary: a prime curve with infinitely many points {#br-ak-2025-2026-l04-cor-01}

Let $K$ be a field and $F\in K[X,Y]$ a prime polynomial. Suppose that the
curve $V(F)$ has infinitely many points. Then its vanishing ideal is the
principal ideal $(F)$, and $V(F)$ is irreducible.

#### Proof {#br-ak-2025-2026-l04-cor-01-proof}

Clearly

$$
(F)\subseteq\operatorname{Id}(V(F)).
$$

Take $G\in\operatorname{Id}(V(F))$. By Lemma 3.8(3),

$$
V(F)=V(\operatorname{Id}(V(F)))\subseteq V(F,G).
$$

If $G$ were not a multiple of $F$, Theorem 4.8 would immediately contradict
the assumption that $V(F)$ has infinitely many points. Hence

$$
\operatorname{Id}(V(F))=(F).
$$

This ideal is prime, and by Lemma 4.3, $V(F)$ is irreducible. $\square$

---

**Source navigation:** [course](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)) - [Lecture 3](#br-ak-2025-2026-l03) - [Lecture 5 (source)](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_5) - [Worksheet 4](#br-ak-2025-2026-w04)
