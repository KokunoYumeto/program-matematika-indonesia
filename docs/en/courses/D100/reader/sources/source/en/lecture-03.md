---
title: "Lecture 3 — The Zariski Topology, Vanishing Ideals, and Radicals"
stable_id: br-ak-2025-2026-l03
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 3"
upstream_pageid: 165892
upstream_revid: 1052207
upstream_timestamp: "2025-08-27T11:33:02Z"
upstream_mediawiki_sha1: 9ce92720a5f22f16453faa79345392063318ee86
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_3?oldid=1052207"
license: "CC BY-SA 4.0 for translated course text; media retain component licences in authority/RIGHTS-unit-03.csv"
translation_status: complete
---

# Lecture 3: The Zariski Topology, Vanishing Ideals, and Radicals {#br-ak-2025-2026-l03}

## The Zariski topology {#br-ak-2025-2026-l03-s01}

![Oscar Zariski (1899-1986)](authority/assets/Oscar_Zariski.jpg)

In Proposition 2.8 we showed that the affine algebraic subsets of an affine
space satisfy the axioms for the closed sets of a topology. This topology is
called the *Zariski topology*.

### Definition: the Zariski topology {#br-ak-2025-2026-l03-def-01}

On affine space $\mathbb A_K^n$, the *Zariski topology* is the topology in
which the affine algebraic sets are declared to be closed.

Thus the open sets of the Zariski topology are the complements of affine
algebraic sets. For an ideal $\mathfrak a$, this complement is denoted by

$$
D(\mathfrak a)=\mathbb A_K^n\setminus V(\mathfrak a).
$$

The Zariski topology differs greatly from other topologies, especially those
given by a metric. In particular, the Zariski topology is not Hausdorff.
Generally speaking, nonempty open sets in the Zariski topology are very large
(see Exercise 3.20), while the closed sets—the affine algebraic sets—are very
thin, apart from the whole space itself.

**Edition note:** The source's non-Hausdorff assertion requires $K$ to be infinite and $n\ge1$. Over a finite field, affine space is a finite discrete space and is Hausdorff; $\mathbb A_K^0$ is also Hausdorff.

### Example: the Zariski topology on the affine line {#br-ak-2025-2026-l03-ex-01}

The Zariski topology on the affine line $\mathbb A_K^1$ over a field $K$ is
easy to describe. The whole affine line is a closed set, given by $V(0)$.
All other closed subsets are given by $V(\mathfrak a)$ with $\mathfrak a\ne0$.
Since $K[X]$ is a principal ideal domain, we can even write

$$
\mathfrak a=(f),\qquad f\ne0.
$$

The corresponding zero locus consists of only finitely many points.
Conversely, each individual point $P$ with coordinate $a$ is the unique zero
of the linear polynomial $X-a$, so

$$
\{P\}=V(X-a)
$$

is Zariski closed. A finite collection of points $P_1,\ldots,P_k$ with
coordinates $a_1,\ldots,a_k$ is the zero locus of the polynomial

$$
(X-a_1)\cdots(X-a_k).
$$

The Zariski closed sets of the affine line are therefore all finite subsets,
including the empty set, together with the whole affine line.

![A line in the plane](authority/assets/Lineline.jpg)

### Example: points are closed {#br-ak-2025-2026-l03-ex-02}

Every point

$$
P=(a_1,\ldots,a_n)\in\mathbb A_K^n
$$

is Zariski closed; more precisely,

$$
P=V(X_1-a_1,X_2-a_2,\ldots,X_n-a_n).
$$

Apart from the empty set and the whole space, points are the simplest affine
algebraic sets. The ideal

$$
(X_1-a_1,X_2-a_2,\ldots,X_n-a_n),
$$

called the *point ideal*, is maximal; see Exercise 2.12.

![Intersection of two planes](authority/assets/IntersectingPlanes.png)

![Intersection of three planes](authority/assets/Secretsharing-3-point.png)

By Proposition 2.8(3), every finite subset of affine space is Zariski closed.
Thus, if $E$ is a finite set of points, its complement

$$
\mathbb A_K^n\setminus E
$$

is Zariski open. Likewise, for a rational function $P/Q$ with

$$
P,Q\in K[X_1,\ldots,X_n],\qquad Q\ne0,
$$

its domain of definition, namely $D(Q)$, is open.

## Vanishing ideals {#br-ak-2025-2026-l03-s02}

### Definition: vanishing ideal {#br-ak-2025-2026-l03-def-02}

Let $T\subseteq\mathbb A_K^n$ be a subset. The set

$$
\operatorname{Id}(T)
=\{F\in K[X_1,\ldots,X_n]\mid F(P)=0
\text{ for every }P\in T\}
$$

is called the *vanishing ideal* of $T$.

This set is indeed an ideal. If $F(P)=0$ and $G(P)=0$ for every $P\in T$,
the same holds for the sum $F+G$ and every multiple $HF$.

We therefore have two assignments in opposite directions: a subset of affine
space is assigned its vanishing ideal, while an ideal in the polynomial ring
is assigned its zero locus. We wish to understand to what extent ideals and
zero loci correspond to one another.

### Example: the empty set and the whole space {#br-ak-2025-2026-l03-ex-03}

The vanishing ideal of the empty set is the unit ideal, since there is no
point at which the vanishing condition needs to be checked.

The vanishing ideal of the whole space $\mathbb A_K^n$ depends on the field.
If $K$ is infinite, only the zero polynomial vanishes everywhere, so the
vanishing ideal is the zero ideal. This follows from Exercise 3.18.

If, on the other hand, $K$ is a finite field with $q$ elements, then

$$
x^q-x=0
$$

for every $x\in K$. Thus the polynomial $X^q-X$ vanishes at every point of
the affine line and belongs to its vanishing ideal. In higher dimensions,

$$
\operatorname{Id}(\mathbb A_K^n)
=(X_1^q-X_1,X_2^q-X_2,\ldots,X_n^q-X_n).
$$

### Example: the vanishing ideal of a point {#br-ak-2025-2026-l03-ex-04}

Let

$$
P=(a_1,\ldots,a_n)\in\mathbb A_K^n.
$$

Then

$$
\operatorname{Id}(P)=(X_1-a_1,\ldots,X_n-a_n).
$$

First, the linear polynomials $X_i-a_i$ clearly vanish at $P$, since
$(X_i-a_i)(P)=a_i-a_i=0$. Hence the ideal they generate is contained in the
vanishing ideal.

Conversely, let $F$ be a polynomial with $F(P)=0$. Express $F$ in the “new
variables”

$$
\widetilde X_1=X_1-a_1,\ldots,
\widetilde X_n=X_n-a_n
$$

by replacing $X_i$ with $X_i-a_i+a_i$. In these new variables, write

$$
F=\sum_\nu b_\nu\widetilde X^\nu.
$$

This polynomial has a constant term $b_0$, while every other monomial
contains at least one variable. Thus, for suitable polynomials $F_i$, we can write

$$
F=F_1\widetilde X_1+\cdots+F_n\widetilde X_n+c.
$$

Since $F(P)=c=0$, we obtain

$$
F\in(\widetilde X_1,\ldots,\widetilde X_n)
=(X_1-a_1,\ldots,X_n-a_n).
$$

### Lemma: inclusion of subsets reverses inclusion of vanishing ideals {#br-ak-2025-2026-l03-lem-01}

Let $V\subseteq W\subseteq\mathbb A_K^n$. Then

$$
\operatorname{Id}(W)\subseteq\operatorname{Id}(V).
$$

#### Proof {#br-ak-2025-2026-l03-lem-01-proof}

Take $F\in\operatorname{Id}(W)$. In other words, $F(P)=0$ for every $P\in W$.
Since $V\subseteq W$, in particular $F(P)=0$ for every $P\in V$. Thus
$F\in\operatorname{Id}(V)$. $\square$

### Lemma: relations between zero loci and vanishing ideals {#br-ak-2025-2026-l03-lem-02}

Let $I\subseteq K[X_1,\ldots,X_n]$ be an ideal and
$T\subseteq\mathbb A_K^n$ a subset. The following statements hold.

1. $T\subseteq V(\operatorname{Id}(T))$.
2. $I\subseteq\operatorname{Id}(V(I))$.
3. $V(I)=V(\operatorname{Id}(V(I)))$.
4. $\operatorname{Id}(T)=\operatorname{Id}(V(\operatorname{Id}(T)))$.

#### Proof {#br-ak-2025-2026-l03-lem-02-proof}

For (1), take $P\in T$. By definition, every polynomial
$F\in\operatorname{Id}(T)$ vanishes on $T$, so
$P\in V(\operatorname{Id}(T))$.

For (2), take $F\in I$. The polynomial $F$ vanishes throughout $V(I)$, so
$F\in\operatorname{Id}(V(I))$.

For (3), apply (1) to $T=V(I)$ to obtain
$V(I)\subseteq V(\operatorname{Id}(V(I)))$. By (2),
$I\subseteq\operatorname{Id}(V(I))$; applying $V(-)$ and Lemma 2.7 gives the
reverse inclusion.

Statement (4) is proved in the same way. $\square$

### Example: strict inclusions {#br-ak-2025-2026-l03-ex-05}

Both inclusions in Lemma 3.8(1) and (2) can be strict. For example, let
$T\subsetneq\mathbb A_K^1$ be an infinite proper subset; this requires $K$
to be infinite. Then

$$
\operatorname{Id}(T)=0,
$$

so $V(0)=\mathbb A_K^1$ is strictly larger than $T$.

For the inclusion in (2), take $R=K[X]$ and $I=(X^2)$. Then

$$
V(I)=\{0\},\qquad \operatorname{Id}(\{0\})=(X),
$$

but $X\notin(X^2)$. A more extreme example in $R=\mathbb R[X,Y]$ is
$I=(X^2+Y^2)$, with $V(I)=\{(0,0)\}$. The vanishing ideal of that point is $(X,Y)$.

### Lemma: Zariski closure {#br-ak-2025-2026-l03-lem-03}

Let $T\subseteq\mathbb A_K^n$. The Zariski closure of $T$ is

$$
\overline T=V(\operatorname{Id}(T)).
$$

#### Proof {#br-ak-2025-2026-l03-lem-03-proof}

The inclusion $T\subseteq V(\operatorname{Id}(T))$ was proved in Lemma
3.8(1). Since $V(\operatorname{Id}(T))$ is closed by definition, we obtain

$$
\overline T\subseteq V(\operatorname{Id}(T)).
$$

Conversely, take $P\in V(\operatorname{Id}(T))$ and suppose that
$P\notin\overline T$. Then there is a Zariski open set $U$ such that

$$
P\in U,
\qquad
U\cap T=\varnothing.
$$

Write $U=D(\mathfrak a)$. The condition $P\in U$ means that some
$G\in\mathfrak a$ satisfies $G(P)\ne0$. Then

$$
P\in D(G)\subseteq U,
$$

so $T\cap D(G)=\varnothing$. Hence $T\subseteq V(G)$ and
$G\in\operatorname{Id}(T)$. But $G(P)\ne0$ contradicts
$P\in V(\operatorname{Id}(T))$. $\square$

## Radicals {#br-ak-2025-2026-l03-s03}

### Definition: radical ideal {#br-ak-2025-2026-l03-def-03}

An ideal $\mathfrak a$ in a commutative ring $R$ is called a *radical ideal*
if the following holds: whenever $f^n\in\mathfrak a$ for some
$n\in\mathbb N$, we already have $f\in\mathfrak a$.

### Definition: the radical of an ideal {#br-ak-2025-2026-l03-def-04}

Let $R$ be a commutative ring and $\mathfrak a\subseteq R$ an ideal. The set

$$
\operatorname{rad}(\mathfrak a)
=\{f\in R\mid\text{there is an }r\text{ with }f^r\in\mathfrak a\}
$$

is called the *radical* of $\mathfrak a$.

The radical of an ideal is itself a radical ideal.

### Lemma: the radical of an ideal is a radical ideal {#br-ak-2025-2026-l03-lem-04}

Let $R$ be a commutative ring and $\mathfrak a\subseteq R$ an ideal. Then
$\operatorname{rad}(\mathfrak a)$ is a radical ideal.

#### Proof {#br-ak-2025-2026-l03-lem-04-proof}

First we show that the set is an ideal. Clearly $0$ belongs to the radical.
If $f\in\operatorname{rad}(\mathfrak a)$, say $f^r\in\mathfrak a$, then

$$
(af)^r=a^rf^r\in\mathfrak a,
$$

so $af$ belongs to the radical. For closure under addition, let
$f,g\in\operatorname{rad}(\mathfrak a)$ with $f^r\in\mathfrak a$ and
$g^s\in\mathfrak a$. Then

$$
\begin{aligned}
(f+g)^{r+s}
&=\sum_{i+j=r+s}\binom{r+s}{i}f^ig^j\\
&=\sum_{\substack{i+j=r+s\\i<r}}\binom{r+s}{i}f^ig^j
 +\sum_{\substack{i+j=r+s\\i\ge r}}\binom{r+s}{i}f^ig^j
\in\mathfrak a.
\end{aligned}
$$

Now suppose that $f^k\in\operatorname{rad}(\mathfrak a)$. For some $r$ we have

$$
(f^k)^r=f^{kr}\in\mathfrak a,
$$

so $f\in\operatorname{rad}(\mathfrak a)$. $\square$

### Lemma: vanishing ideals are radical ideals {#br-ak-2025-2026-l03-lem-05}

Let $T\subseteq\mathbb A_K^n$. Then the vanishing ideal
$\operatorname{Id}(T)$ is a radical ideal.

#### Proof {#br-ak-2025-2026-l03-lem-05-proof}

Let $F\in K[X_1,\ldots,X_n]$ and $F^s\in\operatorname{Id}(T)$. Then

$$
F^s(P)=0
$$

for every $P\in T$. Consequently $F(P)=0$ for every $P\in T$, so
$F\in\operatorname{Id}(T)$. $\square$

Later we shall see that over an algebraically closed field, radical ideals
and algebraic zero loci correspond to one another. This is the content of
Hilbert's Nullstellensatz.

---

**Source navigation:** [course](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)) · [Lecture 2](#br-ak-2025-2026-l02) · [Lecture 4 (source)](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_4) · [Worksheet 3](#br-ak-2025-2026-w03)
