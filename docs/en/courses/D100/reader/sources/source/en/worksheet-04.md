---
title: "Worksheet 4 - Irreducibility, Prime Ideals, and Intersections"
stable_id: br-ak-2025-2026-w04
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 4"
upstream_pageid: 165923
upstream_revid: 1075377
upstream_timestamp: "2026-03-11T10:41:52Z"
upstream_mediawiki_sha1: e938dbe41b7474eff311dfc04732ab251fe9c086
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Arbeitsblatt_4?oldid=1075377"
license: CC BY-SA 4.0
translation_status: complete
---

# Worksheet 4 {#br-ak-2025-2026-w04}

## Practice exercises {#br-ak-2025-2026-w04-practice}

### Exercise 4.1 {#br-ak-2025-2026-w04-ex-01}

<!-- upstream_entity: Affin-algebraische Mengen/Finde Beschreibung als Nullstellenmenge zu Bild/Fläche und senkrechte Gerade/Aufgabe -->

![A surface and a vertical line](authority/assets/Non_cohen_macaulay_scheme_thumb.png)

Find an ideal whose zero locus is the object shown above.

### Exercise 4.2 {#br-ak-2025-2026-w04-ex-02}

<!-- upstream_entity: Punktmengen im affinen Raum/Irreduzibel genau dann, wenn einpunktig/Aufgabe -->

Let $V\subseteq\mathbb A_K^n$ be a subset consisting of finitely many points.
Prove that $V$ is irreducible if and only if it consists of a single point.

### Exercise 4.3 {#br-ak-2025-2026-w04-ex-03}

<!-- upstream_entity: Affin-algebraische Mengen/Zusammenhängend/Nicht irreduzibel/Beispiel/Aufgabe -->

Sketch an example of an affine algebraic subset that is connected but not irreducible.

### Exercise 4.4 {#br-ak-2025-2026-w04-ex-04}

<!-- upstream_entity: Reelle Hyperbel/Irreduzible Komponenten/Aufgabe -->

![Rectangular hyperbola](authority/assets/Rectangular_hyperbola-250-unit-04.png)

Determine the irreducible components of the real hyperbola.

### Exercise 4.5 {#br-ak-2025-2026-w04-ex-05}

<!-- upstream_entity: Quadrik in zwei Variablen/X^2+Y^2+a/a nicht 0/Irreduzibel/Aufgabe -->

Let $K$ be a field of characteristic $\ne2$ and $a\in K$ nonzero. Prove that
the polynomial

$$
X^2+Y^2+a\in K[X,Y]
$$

is irreducible.

### Exercise 4.6 {#br-ak-2025-2026-w04-ex-06}

<!-- upstream_entity: Primideal/Verschwindungsmenge/Affine Gerade/Aufgabe -->

Let $K$ be a field and

$$
\mathfrak p=(p)\subseteq K[X]
$$

a prime ideal. Prove that the zero locus $V(\mathfrak p)\subseteq\mathbb A_K^1$
is either the whole of $\mathbb A_K^1$ (whose irreducibility depends on the
field) or a single point (and hence irreducible).

**Edition note:** As written, the source statement omits the case
$V(\mathfrak p)=\varnothing$, for example $K=\mathbb R$ and
$\mathfrak p=(X^2+1)$. This note does not alter the source exercise.

### Exercise 4.7 {#br-ak-2025-2026-w04-ex-07}

<!-- upstream_entity: Primideal/Verschwindungsmenge/Endlicher Körper/Aufgabe -->

Let $K$ be a finite field and $\mathfrak p\subset K[X_1,\ldots,X_n]$ a prime
ideal. Prove that its zero locus

$$
V(\mathfrak p)\subseteq\mathbb A_K^n
$$

can be irreducible only if it consists of a single point.

### Exercise 4.8 {#br-ak-2025-2026-w04-ex-08}

<!-- upstream_entity: Primideal/Verschwindungsmenge/R/Primpolynom/Aufgabe -->

Prove that the real polynomial

$$
P=X^2(X-1)^2+Y^2\bigl(X^2+(X-1)^2\bigr)
\in\mathbb R[X,Y]
$$

is a prime polynomial, whereas its zero locus

$$
V(P)\subseteq\mathbb R^2
$$

is nonempty but reducible.

### Exercise 4.9 {#br-ak-2025-2026-w04-ex-09}

<!-- upstream_entity: Affiner Raum/Irreduzibilität/Schnitt von Zylinder und Kugel/Aufgabe -->

In $\mathbb A_{\mathbb R}^3$, calculate the intersection of the cylinder

$$
V(x^2+y^2-1)
$$

with the sphere of centre $P=(0,0,0)$ and radius $r$, as a function of $r$.
When is the intersection empty, and when is it irreducible?

You may use the fact that the real circle is irreducible.

The next exercise says that the intersection of the graphs of two
one-variable polynomials agrees, not only pointwise but also algebraically,
with the intersection of the graph of their difference and the $x$-axis.
See also Exercise 26.3.

### Exercise 4.10 ★ {#br-ak-2025-2026-w04-ex-10}

<!-- upstream_entity: Zwei Polynome in einer Variablen/Graph/Restklassenring/Aufgabe -->

Let $F,G\in K[X]$ be polynomials in one variable over a field $K$. Prove that
there is a $K$-algebra isomorphism

$$
K[X,Y]/(Y-F,Y-G)\cong K[X]/(F-G).
$$

### Exercise 4.11 ★ {#br-ak-2025-2026-w04-ex-11}

<!-- upstream_entity: Zwei Kreise/Durchschnitt/Restklassenring/Gerade/Aufgabe -->

Let two distinct circles in the plane be given by circle equations $F$ and $G$.

1. Prove that the quotient ring $K[X,Y]/(F,G)$ is isomorphic to
   $K[X,Y]/(F,H)$, where $H$ has degree at most $1$.
2. Prove that $K[X,Y]/(F,G)$ is isomorphic to a ring of the form $K[U]/(Q)$,
   where $Q\in K[U]$ has degree at most $2$.

### Exercise 4.12 ★ {#br-ak-2025-2026-w04-ex-12}

<!-- upstream_entity: Kommutativer Ring/Polynomring/1/Restklassenring/Aufgabe -->

Let $R$ be a commutative ring and $R[X]$ the polynomial ring over $R$. Let
$\mathfrak a\subseteq R[X]$ be an ideal with generators

$$
\mathfrak a=(F_0,F_1,\ldots,F_n),
$$

where $F_0=X-r$ for some $r\in R$. For $i\ge1$, let $G_i\in R$ be obtained
from $F_i$ by replacing $X$ with $r$. Prove the isomorphism of quotient rings

$$
R[X]/\mathfrak a\cong R/(G_1,\ldots,G_n).
$$

### Exercise 4.13 {#br-ak-2025-2026-w04-ex-13}

<!-- upstream_entity: Reelle Zahlen/Topologie/Mit metrischer Topologie irreduzibel/Aufgabe -->

Consider the real numbers $\mathbb R$ with the metric topology. Is $\mathbb R$
irreducible?

### Exercise 4.14 ★ {#br-ak-2025-2026-w04-ex-14}

<!-- upstream_entity: Restklassenkörper (Z)/Summe von zwei Quadraten/Lösung/Fakt/Beweis/Aufgabe -->

Let $p$ be a prime number and $\mathbb Z/(p)$ the corresponding residue field.
Prove that every quadratic equation of the form

$$
F=aX^2+bY^2+c=0,
\qquad a,b\ne0,
$$

has at least one solution in $\mathbb Z/(p)$.

### Exercise 4.15 ★ {#br-ak-2025-2026-w04-ex-15}

<!-- upstream_entity: Primideal/Charakterisierung als Kern nach Körper/Aufgabe -->

Let $\mathfrak a$ be an ideal in a commutative ring $R$. Prove that
$\mathfrak a$ is prime if and only if it is the kernel of a ring homomorphism

$$
\varphi:R\longrightarrow K
$$

to a field $K$.

### Exercise 4.16 {#br-ak-2025-2026-w04-ex-16}

<!-- upstream_entity: Kommutative Ringtheorie/Maximales Ideal/Primideal/Fakt/Beweis/Aufgabe -->

Prove that every maximal ideal $\mathfrak m$ in a commutative ring $R$ is prime.

### Exercise 4.17 ★ {#br-ak-2025-2026-w04-ex-17}

<!-- upstream_entity: Kommutative Ringtheorie/Primideal/Charakterisierung mit Restklassenring/Fakt/Beweis/Aufgabe -->

Let $R$ be a commutative ring and $\mathfrak p$ an ideal. Prove that
$\mathfrak p$ is prime if and only if the quotient ring $R/\mathfrak p$ is
an integral domain.

### Exercise 4.18 {#br-ak-2025-2026-w04-ex-18}

<!-- upstream_entity: Primideal/Idealdurchschnitt/Inklusion/Aufgabe -->

Let $\mathfrak p\subseteq R$ be a prime ideal in a commutative ring $R$.
Prove that

$$
\mathfrak a\cap\mathfrak b\subseteq\mathfrak p
$$

implies $\mathfrak a\subseteq\mathfrak p$ or $\mathfrak b\subseteq\mathfrak p$.

### Exercise 4.19 {#br-ak-2025-2026-w04-ex-19}

<!-- upstream_entity: Kommutative Ringtheorie/Primideal/Unter Morphismus/Aufgabe -->

Let $R$ and $S$ be commutative rings, $\varphi:R\to S$ a ring homomorphism,
and $\mathfrak p$ a prime ideal in $S$. Prove that the inverse image
$\varphi^{-1}(\mathfrak p)$ is a prime ideal in $R$.

Give an example showing that the inverse image of a maximal ideal need not
be maximal.

### Exercise 4.20 {#br-ak-2025-2026-w04-ex-20}

<!-- upstream_entity: Rationaler Funktionenkörper/Unendlich viele Zwischenkörper/Aufgabe -->

Let $K$ be a field and $L=K(X)$ the field of fractions of the polynomial ring
$K[X]$. Prove that there are infinitely many intermediate fields between $K$ and $L$.

### Exercise 4.21 {#br-ak-2025-2026-w04-ex-21}

<!-- upstream_entity: Ebene Kurven/Schnitt ohne Komponenten/Endlich viele Punkte/Fakt/Frage zu Beweis in mehr Variablen/Aufgabe -->

Explain where the proof of Theorem 4.8 breaks down if one tries to extend it
to more than two variables.

### Exercise 4.22 {#br-ak-2025-2026-w04-ex-22}

<!-- upstream_entity: Polynome in je einer Variable/Durchschnitt/Abschätzung/Aufgabe -->

Let $P(X)$ and $Q(Y)$ be nonconstant polynomials in the indicated variables.
Give a bound (under what condition?) for the number of intersection points of
the two curves

$$
V(Y-P(X))
\qquad\text{and}\qquad
V(X-Q(Y)).
$$

The following exercises use the terms *closed map* and *open map*. A
continuous map $f:X\to Y$ between topological spaces is called *closed* if
the image of every closed set is closed. It is called *open* if the image of
every open set is open.

### Exercise 4.23 {#br-ak-2025-2026-w04-ex-23}

<!-- upstream_entity: Affine Ebene/Projektion/Nicht abgeschlossen/Beispiel/Aufgabe -->

Prove that the projection

$$
\mathbb A_K^2\longrightarrow\mathbb A_K^1,
\qquad
(x,y)\longmapsto x,
$$

is not a closed map in the Zariski topology.

**Edition note:** Assume $K$ is infinite. The source omits this hypothesis; over a finite field, both spaces are discrete and every map between them is closed.

### Exercise 4.24 {#br-ak-2025-2026-w04-ex-24}

<!-- upstream_entity: Ebene algebraische Kurven/C/Ist nicht kompakt/Aufgabe -->

Prove that a plane algebraic curve over the complex numbers $\mathbb C$ is
not compact in the metric topology.

## Exercises to hand in {#br-ak-2025-2026-w04-submission}

### Exercise 4.25 - 6 points {#br-ak-2025-2026-w04-ex-25}

<!-- upstream_entity: Restklassenringe (Z)/p prim/Quadratische Form/Hat Lösung oder beschreibt Nichtquadrat in einer Variablen/Aufgabe -->

Let $p\ge3$ be a prime number and $K=\mathbb Z/(p)$ the corresponding residue
field. Consider the polynomial

$$
F=\alpha X^2+\beta XY+\gamma Y^2+\delta X+\epsilon Y+\eta
\in\mathbb Z/(p)[X,Y].
$$

If $\alpha,\beta,\gamma$ are not all zero, this is a quadratic polynomial.
Prove that exactly one of the following three alternatives holds for its
zero locus $V(F)\subseteq\mathbb A_K^2$.

1. $V(F)$ has at least one point.
2. $F=c$ for a constant $c\ne0$.
3. There is a change of variables such that, in the new coordinates, the
   polynomial has the form $Z^2-u$ with $u\in\mathbb Z/(p)$ a nonsquare.

**Edition note:** In alternative (3), one must also allow multiplication of the polynomial by a nonzero scalar, which does not change its zero locus. The source omits this normalisation: for example, $2X^2+2$ over $\mathbb F_3$ has no zero, but an invertible linear or affine change of variables alone cannot turn its nonsquare leading coefficient into $1$.

**Source hint:** Exercise 9.20 in *Number Theory (Osnabrück 2025)* is useful
for one important case.

### Exercise 4.26 - 3 points {#br-ak-2025-2026-w04-ex-26}

<!-- upstream_entity: Affin-algebraische Mengen/Irreduzibel/Ohne endlich viele Punkte/ist irreduzibel/Aufgabe -->

Let $V$ be an irreducible affine algebraic set with at least two points, and
let $P_1,\ldots,P_m\in V$ be finitely many points. Prove that

$$
V\setminus\{P_1,\ldots,P_m\}
$$

is also irreducible in the induced topology.

### Exercise 4.27 - 4 points {#br-ak-2025-2026-w04-ex-27}

<!-- upstream_entity: Polynomring über faktoriellem Grundring/Teilerfremd/Teilerfremd über Quotientenkörper/Aufgabe -->

Let $R$ be a unique factorisation domain with field of fractions $Q(R)$.
Prove that if $F,G\in R[X]$ have no common nonconstant factor, then they
also have no common nonconstant factor when regarded as elements of $Q(R)[X]$.

**Source note:** You may restrict attention to the case where $R$ is a
principal ideal domain.

### Exercise 4.28 - 3 points {#br-ak-2025-2026-w04-ex-28}

<!-- upstream_entity: Quadrik in zwei Variablen/Kreis/Rationale Zahlen/Irreduzibel/Aufgabe -->

Let $K=\mathbb Q$ be the field of rational numbers. Determine, with
justification, whether

$$
V(X^2+Y^2-1)\subseteq\mathbb A_{\mathbb Q}^2
$$

is irreducible.

**Source hint:** Use Exercise 1.28 on the rational parametrisation of the
unit circle and Corollary 4.9.

### Exercise 4.29 - 4 points {#br-ak-2025-2026-w04-ex-29}

<!-- upstream_entity: Affine Ebene/Projektion/Offen/Aufgabe -->

Prove that the projection

$$
\mathbb A_K^2\longrightarrow\mathbb A_K^1,
\qquad
(x,y)\longmapsto x,
$$

is an open map in the Zariski topology.

### Exercise 4.30 - 4 points {#br-ak-2025-2026-w04-ex-30}

<!-- upstream_entity: Affine Ebene (K)/Ist quasikompakt/Aufgabe -->

Prove that the affine plane $\mathbb A_K^2$ with the Zariski topology is compact.

**Terminology note:** Here “compact” means that every open cover has a finite subcover; no Hausdorff condition is included (this is also called *quasi-compact*).

---

**Source navigation:** [Lecture 4](#br-ak-2025-2026-l04) - [public solutions for Unit 4](#br-ak-2025-2026-w04-solutions) - [Worksheet 3](#br-ak-2025-2026-w03) - [Worksheet 5 (source)](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Arbeitsblatt_5)
