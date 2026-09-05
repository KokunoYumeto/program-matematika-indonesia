---
title: "Worksheet 3 — The Zariski Topology and Radicals"
stable_id: br-ak-2025-2026-w03
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 3"
upstream_pageid: 165922
upstream_revid: 1061785
upstream_timestamp: "2025-12-08T09:46:03Z"
upstream_mediawiki_sha1: d030496f7c78a434250657f10206ab4ba69ade1e
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Arbeitsblatt_3?oldid=1061785"
license: CC BY-SA 4.0
translation_status: complete
---

# Worksheet 3 {#br-ak-2025-2026-w03}

## Practice exercises {#br-ak-2025-2026-w03-practice}

### Exercise 3.1 {#br-ak-2025-2026-w03-ex-01}

<!-- upstream_entity: Affine Gerade/Zariski-offen/Definitionsbereich/Aufgabe -->

Prove that the nonempty Zariski open subsets of the affine line
$\mathbb A_K^1$ are precisely the maximal domains of definition of rational functions.

**Edition note:** Assume $K$ is infinite. The source omits this hypothesis: over a finite field with $q$ elements, the rational expression $1/(X^q-X)$ has empty domain on $K$.

### Exercise 3.2 {#br-ak-2025-2026-w03-ex-02}

<!-- upstream_entity: Polynom/Unendlicher Körper/Unendlich viele Werte/Aufgabe -->

Let $K$ be an infinite field and $P\in K[X]$ a nonconstant polynomial. Prove
that the function

$$
P:K\longrightarrow K
$$

defined by $P$ takes infinitely many values.

### Exercise 3.3 {#br-ak-2025-2026-w03-ex-03}

<!-- upstream_entity: Ebene algebraische Kurven/Y^n-X^n/Reelle Nullstelle und beschreibendes Ideal der regulären n-Strahlen/Aufgabe -->

1. Sketch the real zero loci of $Y^n-X^n$.
2. Determine the vanishing ideals of the affine algebraic sets
   $V_n\subseteq\mathbb A_{\mathbb R}^2$ consisting of the union of all lines
   through the origin and a vertex of a regular $n$-gon with $(1,0)$ as one vertex.

### Exercise 3.4 {#br-ak-2025-2026-w03-ex-04}

<!-- upstream_entity: Zariski-Topologie/Affine Gerade/Nicht polynomial, aber Zariski stetig/Finde Beispiel/Aufgabe -->

Describe a map

$$
\varphi:\mathbb A_K^1\longrightarrow\mathbb A_K^1
$$

that is continuous in the Zariski topology but is not given by a polynomial.

**Edition note:** The source omits the necessary assumption that $K$ is infinite. Over a finite field, every map $K\to K$ is represented by a polynomial, so no such example exists.

### Exercise 3.5 {#br-ak-2025-2026-w03-ex-05}

<!-- upstream_entity: Komplexer affiner Raum/Affin-algebraisch/Reell/Aufgabe -->

Let

$$
V\subseteq\mathbb A_{\mathbb C}^n=\mathbb C^n
$$

be an affine algebraic set. Prove that under the identification

$$
\mathbb C^n=\mathbb R^{2n},
$$

the subset $V$ is also an affine algebraic set in $\mathbb A_{\mathbb R}^{2n}$.
Prove that the converse does not hold.

### Exercise 3.6 {#br-ak-2025-2026-w03-ex-06}

<!-- upstream_entity: Metrischer Raum/Abstand zu Teilmenge/Stetig/Aufgabe -->

Let $(M,d)$ be a metric space and $T\subseteq M$ a nonempty subset. Prove that

$$
d_T(x):=\inf\{d(x,y)\mid y\in T\}
$$

defines a well-defined continuous function $M\to\mathbb R$.

### Exercise 3.7 {#br-ak-2025-2026-w03-ex-07}

<!-- upstream_entity: Metrischer Raum/Abgeschlossene Teilmenge/Nullfaser/Aufgabe -->

Let $(M,d)$ be a metric space and $T\subseteq M$ a subset. Prove that $T$ is
closed if and only if there is a continuous function

$$
f:M\longrightarrow\mathbb R
$$

with

$$
f^{-1}(0)=T.
$$

### Exercise 3.8 {#br-ak-2025-2026-w03-ex-08}

<!-- upstream_entity: Ball/R^n/Zariski-Topologie/Nicht offen/Aufgabe -->

Prove that, for $r>0$, the open ball $U(P,r)$ in $\mathbb R^n$ is not
Zariski open, and the closed ball $B(P,r)$ is not Zariski closed.

### Exercise 3.9 {#br-ak-2025-2026-w03-ex-09}

<!-- upstream_entity: Ganze Zahlen/Ideale/Charakterisierung von Radikalen/mit Primfaktorzerlegung/Aufgabe -->

Characterise the radical ideals in $\mathbb Z$ using prime factorisation.

### Preliminary definition: nilpotent element {#br-ak-2025-2026-w03-def-nilpotent}

An element $a$ of a commutative ring $R$ is called *nilpotent* if

$$
a^n=0
$$

for some natural number $n$.

### Exercise 3.10 {#br-ak-2025-2026-w03-ex-10}

<!-- upstream_entity: Kommutative Ringtheorie/Nilpotente Elemente/Summe/Aufgabe -->

Let $R$ be a commutative ring and $f,g\in R$ nilpotent elements. Prove that
their sum $f+g$ is also nilpotent.

### Exercise 3.11 ★ {#br-ak-2025-2026-w03-ex-11}

<!-- upstream_entity: Kommutative Ringtheorie/Nilpotentes Element/1+a ist Einheit/Aufgabe -->

Let $R$ be a commutative ring and $f\in R$ a nilpotent element. Prove that
$1+f$ is a unit.

### Exercise 3.12 {#br-ak-2025-2026-w03-ex-12}

<!-- upstream_entity: Kommutative Ringtheorie/Polynomring/Nilpotente Elemente und Einheiten/Aufgabe -->

Let $R$ be a commutative ring and $r\in R$ a nilpotent element. Construct a
linear polynomial in $R[X]$ that is a unit, and give its inverse.

**Edition note:** If “linear” means degree exactly $1$, assume $r\ne0$. The source allows $r=0$; in that case a polynomial of degree at most $1$ is the appropriate formulation, and the construction may be constant.

### Preliminary definition: reduced ring {#br-ak-2025-2026-w03-def-reduced}

A commutative ring $R$ is called *reduced* if $0$ is its only nilpotent element.

### Exercise 3.13 ★ {#br-ak-2025-2026-w03-ex-13}

<!-- upstream_entity: Kommutative Ringtheorie/Ideale/Radikal und reduzierter Restklassenring/Aufgabe -->

Prove that an ideal $\mathfrak a$ in a commutative ring $R$ is radical if and
only if the quotient ring $R/\mathfrak a$ is reduced.

### Exercise 3.14 {#br-ak-2025-2026-w03-ex-14}

<!-- upstream_entity: Ideal/Potenzen/Radikal gleich/Aufgabe -->

Let $\mathfrak a\subseteq R$ be an ideal in a commutative ring $R$. Prove
that all the powers

$$
\mathfrak a^n,\qquad n\in\mathbb N_+,
$$

have the same radical.

### Exercise 3.15 {#br-ak-2025-2026-w03-ex-15}

<!-- upstream_entity: Kommutative Ringtheorie/Ideale/Primideal ist Radikal/Aufgabe -->

Prove that every prime ideal is a radical ideal.

### Exercise 3.16 {#br-ak-2025-2026-w03-ex-16}

<!-- upstream_entity: Kommutative Ringtheorie/Ideal/Radikal unter Ringhomomorphismus/Aufgabe -->

Let $R$ and $S$ be commutative rings, $\varphi:R\to S$ a ring homomorphism,
and $\mathfrak a$ a radical ideal in $S$. Prove that the inverse image
$\varphi^{-1}(\mathfrak a)$ is a radical ideal in $R$.

### Exercise 3.17 {#br-ak-2025-2026-w03-ex-17}

<!-- upstream_entity: Affin-algebraische Mengen/Ideale mit gleichem Radikal/Gleiche Nullstellenmenge/Aufgabe -->

Let $\mathfrak a$ and $\mathfrak b$ be ideals in $K[X_1,\ldots,X_n]$ with
the same radical. Prove that their zero loci are also equal. Give an example
showing that the converse does not hold.

### Exercise 3.18 {#br-ak-2025-2026-w03-ex-18}

<!-- upstream_entity: Identitätssatz für Polynome/Unendlicher Körper/Zariski-offene nicht-leere Menge/Aufgabe -->

Let $K$ be an infinite field, $F\in K[X_1,\ldots,X_n]$ a polynomial, and
$U\subseteq\mathbb A_K^n$ a nonempty Zariski open subset. Suppose that
$F|_U=0$ as a function. Prove that $F$ is the zero polynomial.

## Exercises to hand in {#br-ak-2025-2026-w03-submission}

### Exercise 3.19 — 3 points {#br-ak-2025-2026-w03-ex-19}

<!-- upstream_entity: Zariski-Topologie/Affiner Raum/Polynomiale Abbildungen sind Zariski-stetig/Aufgabe -->

Let

$$
\varphi:\mathbb A_K^n\longrightarrow\mathbb A_K^m
$$

be a map given by $m$ polynomials in $n$ variables. Prove that $\varphi$ is
continuous in the Zariski topology.

### Exercise 3.20 — 4 points {#br-ak-2025-2026-w03-ex-20}

<!-- upstream_entity: Zariski-Topologie/Affiner Raum/Offene Mengen sind dicht/Aufgabe -->

Let $K$ be an infinite field. Prove that every nonempty Zariski open subset

$$
U\subseteq\mathbb A_K^n
$$

is dense.

**Source hint:** Reduce to the case $n=1$. Do not use Exercise 3.18.

### Exercise 3.21 — 5 points {#br-ak-2025-2026-w03-ex-21}

<!-- upstream_entity: Zariski-Topologie/Affine Ebene/Bestimme Abschluss zu verschiedenen Mengen/Aufgabe -->

Determine the Zariski closure of each of the following subsets of the affine
plane $\mathbb A_K^2$.

1. $\{(x,\sin x)\mid x\in\mathbb R\}$.
2. $\{(\cos x,\sin x)\mid x\in\mathbb R\}$.
3. $\{(x,x^3)\mid 0\le x\le1,\ x\in\mathbb R\}$.
4. $\{(x,x^3)\mid 0\le x\le1,\ x\in\mathbb Q\}$.
5. $\{(x,x^3)\mid x\in\mathbb Z/(5)\}$.

The next exercise uses some more advanced topological concepts.

### Exercise 3.22 — 4 points {#br-ak-2025-2026-w03-ex-22}

<!-- upstream_entity: Zariski-Topologie/Vergleich zu anderen Topologien/Aufgabe -->

Let $K$ be a field.

1. Prove that for both $K=\mathbb R$ and $K=\mathbb C$, the standard topology
   (the metric or Euclidean topology) is finer than the Zariski topology on
   $\mathbb A_K^1$.
2. Prove that the Zariski topology on $\mathbb A_K^1$ equals the cofinite
   topology. Does this also hold on $\mathbb A_K^n$ for $n\ge2$?
3. When does the Zariski topology on $\mathbb A_K^n$ satisfy $T_1$? When is it
   Hausdorff?
4. What does the Zariski topology on $\mathbb A_K^n$ look like when $K$ is a
   finite field?

---

**Source navigation:** [Lecture 3](#br-ak-2025-2026-l03) · [public solutions for Unit 3](#br-ak-2025-2026-w03-solutions) · [Worksheet 2](#br-ak-2025-2026-w02) · [Worksheet 4 (source)](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Arbeitsblatt_4)
