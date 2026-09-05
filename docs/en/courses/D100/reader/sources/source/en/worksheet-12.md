---
title: "Worksheet 12 - The K-spectrum and its functoriality"
stable_id: br-ak-2025-2026-w12
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 12"
upstream_pageid: 165931
upstream_revid: 1067822
upstream_timestamp: "2026-01-30T07:25:08Z"
upstream_mediawiki_sha1: c65053c29d4a96d478740742ae6d7157b48019fe
source_url: "https://de.wikiversity.org/w/index.php?oldid=1067822"
authority_manifest: authority/wikiversity/unit-12/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 181ce377bd68639b12511a9b1402ca03fd76c6107325195d3aa51a81b7286559
worksheet_xml_sha256: c9eabfdb542ec4a1cf6743eea85848e337bec0a82f37a6fce7f18ef2e33df858
worksheet_expanded_tex_sha256: fce614601e7d40ba07b65692d0233ed93019a237444e4263aef2ab289ac9c961
exercise_map: authority/wikiversity/unit-12/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: a37f874ffa17dd35ed4375f2956786793e475fcd5e2ded0333207c546e7e91db
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 12 {#br-ak-2025-2026-w12}

## Practice exercises {#br-ak-2025-2026-w12-practice}

<!-- upstream_entity: Geometrie/Punkt/Mit und ohne Koordinaten/Aufgabe -->

### Exercise 12.1 {#br-ak-2025-2026-w12-ex-01}

Explain the concept of a point in Euclidean (coordinate-free) geometry
and in Cartesian geometry. In which situations is it useful to introduce
coordinates?

<!-- upstream_entity: Algebraische Kurven/Punkt/Aufgabe -->

### Exercise 12.2 {#br-ak-2025-2026-w12-ex-02}

What is a point in algebraic geometry? Which notions of a point have you
encountered in the course on algebraic curves, and how are they related?

<!-- upstream_entity: K-Spektrum/K^n/Aufgabe -->

### Exercise 12.3 {#br-ak-2025-2026-w12-ex-03}

Determine the $K$-spectrum of $K^d$.

<!-- upstream_entity: K-Spektrum/R-Algebra C/Aufgabe -->

### Exercise 12.4 {#br-ak-2025-2026-w12-ex-04}

Determine the $\mathbb R$-spectrum of the $\mathbb R$-algebra $\mathbb C$.

<!-- upstream_entity: K-Spektrum/R/Kreisgleichung/Aufgabe -->

### Exercise 12.5 {#br-ak-2025-2026-w12-ex-05}

Determine the $\mathbb R$-spectrum of

$$
\mathbb R[X,Y]/(X^2+Y^2-1).
$$

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen/K-Punkt und maximales Ideal/Aufgabe -->

### Exercise 12.6 ★ {#br-ak-2025-2026-w12-ex-06}

Let $K$ be an algebraically closed field and $R$ a commutative $K$-algebra
of finite type. Show that the points of

$$
K\!-\!\operatorname{Spek}(R)
$$

correspond to the maximal ideals of $R$.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Nullstelle zu Ideal und zu Radikal/Aufgabe -->

### Exercise 12.7 {#br-ak-2025-2026-w12-ex-07}

Let $R$ be a commutative $K$-algebra of finite type. Show that, for every
ideal $\mathfrak a\subseteq R$, we have

$$
V(\mathfrak a)=V\bigl(\operatorname{rad}(\mathfrak a)\bigr)
$$

inside $K\!-\!\operatorname{Spek}(R)$.

<!-- upstream_entity: Endlich erzeugte K-Algebren/K-Spektrum mit Zariski-Topologie/Ist Topologie/Aufgabe -->

### Exercise 12.8 {#br-ak-2025-2026-w12-ex-08}

Show that the Zariski topology on the $K$-spectrum of a commutative
$K$-algebra $R$ of finite type is indeed a topology.

<!-- upstream_entity: Affine Varietät/Koordinatenring/K-Spektrum/Aufgabe -->

### Exercise 12.9 {#br-ak-2025-2026-w12-ex-09}

Let $K$ be a field and

$$
V\subseteq\mathbb A_K^n
$$

an affine algebraic set with vanishing ideal $\operatorname{Id}(V)$ and
coordinate ring

$$
R:=K[X_1,\ldots,X_n]/\operatorname{Id}(V).
$$

Show that the $K$-spectrum of $R$ is homeomorphic to $V$.

All versions of Hilbert's Nullstellensatz, such as Corollary 11.11, carry
over to the $K$-spectrum of a $K$-algebra of finite type over an
algebraically closed field $K$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen/Hilbertscher Nullstellensatz/Aufgabe -->

### Exercise 12.10 {#br-ak-2025-2026-w12-ex-10}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type. Prove that there is a bijective correspondence between the closed
subsets of the $K$-spectrum

$$
K\!-\!\operatorname{Spek}(R)
$$

and the radical ideals of $R$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen und reduziert/Identitätssatz/Aufgabe -->

### Exercise 12.11 {#br-ak-2025-2026-w12-ex-11}

Let $K$ be an algebraically closed field and $R$ a reduced $K$-algebra of
finite type. Prove the *identity theorem* in the following form: if
$f,g\in R$ satisfy

$$
f(P)=g(P)
$$

for all $P\in K\!-\!\operatorname{Spek}(R)$, then $f=g$.

<!-- upstream_entity: K-Spektrum/Einheitsideal und leere Nullstellenmenge/Nilpotent und ganze Nullstellenmenge/Aufgabe -->

### Exercise 12.12 ★ {#br-ak-2025-2026-w12-ex-12}

Let $K$ be a field, $R$ a finitely generated $K$-algebra,
$\mathfrak a\subseteq R$ an ideal, and

$$
X=K\!-\!\operatorname{Spek}(R).
$$

What is the relationship between the two statements

$$
V(\mathfrak a)=\varnothing
\qquad\text{and}\qquad
\mathfrak a\text{ is the unit ideal},
$$

and between the two statements

$$
V(\mathfrak a)=X
\qquad\text{and}\qquad
\mathfrak a\text{ is nilpotent}?
$$

Show that the answer depends on whether $K$ is algebraically closed.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Spektrumsabbildung zum Algebra-Strukturhomomorphismus/Aufgabe -->

### Exercise 12.13 {#br-ak-2025-2026-w12-ex-13}

For a commutative $K$-algebra $R$ of finite type, describe the spectrum
map associated with the algebra structure homomorphism

$$
K\longrightarrow R.
$$

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Funktorialität/Nachweis/Aufgabe -->

### Exercise 12.14 {#br-ak-2025-2026-w12-ex-14}

Let $R,S,T$ be commutative $K$-algebras of finite type, and let

$$
\varphi:R\longrightarrow S
\qquad\text{and}\qquad
\psi:S\longrightarrow T
$$

be $K$-algebra homomorphisms. Show that the corresponding spectrum maps satisfy

$$
(\psi\circ\varphi)^*=\varphi^*\circ\psi^*.
$$

Also show that the map $\operatorname{Id}^*$ associated with the identity
$\operatorname{Id}:R\to R$ is itself the identity.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Stetige Abbildung zwischen K-Spektren/Nicht von Homomorphismus/Beispiel/Aufgabe -->

### Exercise 12.15 {#br-ak-2025-2026-w12-ex-15}

Give an example of two commutative $K$-algebras $R,S$ of finite type and
a continuous map between their $K$-spectra that cannot arise from a
$K$-algebra homomorphism.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Element und Abbildung nach affiner Gerade/Nullfaser/Aufgabe -->

### Exercise 12.16 {#br-ak-2025-2026-w12-ex-16}

Let $K$ be a field, $R$ a commutative $K$-algebra of finite type, and
$F\in R$. Let

$$
\varphi^*:K\!-\!\operatorname{Spek}(R)\longrightarrow\mathbb A_K^1
$$

be the spectrum map associated with the substitution homomorphism. Show that

$$
(\varphi^*)^{-1}(0)=V(F).
$$

<!-- upstream_entity: Kommutative Algebra/K-Spektren/Isomorphie mit Reduktion/Aufgabe -->

### Exercise 12.17 {#br-ak-2025-2026-w12-ex-17}

Let $K$ be a field and $R$ a commutative $K$-algebra of finite type,
with reduction

$$
S=R_{\mathrm{red}}.
$$

Show that there is a natural homeomorphism

$$
K\!-\!\operatorname{Spek}(R)
\cong K\!-\!\operatorname{Spek}(S).
$$

<!-- upstream_entity: Polynomring/K-Spektrum/Polynomiale Abbildung/Aufgabe -->

### Exercise 12.18 {#br-ak-2025-2026-w12-ex-18}

Let $K$ be a field and let

$$
F_i\in K[X_1,\ldots,X_n],
\qquad i=1,\ldots,m,
$$

be polynomials. Let

$$
\begin{aligned}
\varphi:K[Y_1,\ldots,Y_m]&\longrightarrow K[X_1,\ldots,X_n],\\
Y_i&\longmapsto F_i
\end{aligned}
$$

be the corresponding substitution homomorphism. Show that, under the
identification in Lemma 12.3, the spectrum map

$$
\varphi^*:\mathbb A_K^n
=K\!-\!\operatorname{Spek}(K[X_1,\ldots,X_n])
\longrightarrow
\mathbb A_K^m
=K\!-\!\operatorname{Spek}(K[Y_1,\ldots,Y_m])
$$

agrees with the direct polynomial map

$$
(x_1,\ldots,x_n)\longmapsto
\bigl(F_1(x_1,\ldots,x_n),\ldots,F_m(x_1,\ldots,x_n)\bigr).
$$

<!-- upstream_entity: Funktor/Kennen/Aufgabe -->

### Exercise 12.19 {#br-ak-2025-2026-w12-ex-19}

Which “functors” in mathematics do you know?

In the following exercises, for an arbitrary topological space—for example
a manifold, a subset of $\mathbb R^n$, or a real interval—we consider
the ring of continuous real-valued functions on it. The spaces should be
viewed as analogous to $K$-spectra, and their function rings as analogous
to coordinate rings.

<!-- upstream_entity: Topologischer Raum/Ring der stetigen reellwertigen Funktionen/Nachweis/Aufgabe -->

### Exercise 12.20 {#br-ak-2025-2026-w12-ex-20}

Let $X$ be a topological space and

$$
R=C(X,\mathbb R)
=\{f:X\longrightarrow\mathbb R\mid f\text{ is continuous}\}.
$$

Show that $R$ is a commutative ring.

<!-- upstream_entity: Stetige Funktionen/R/Integritätsbereich/Aufgabe -->

### Exercise 12.21 {#br-ak-2025-2026-w12-ex-21}

Consider the ring of continuous functions

$$
R=C(\mathbb R,\mathbb R)
$$

from $\mathbb R$ to $\mathbb R$. Is this ring an integral domain?

<!-- upstream_entity: Stetige Funktionen/R/Teilmenge/Ideal/Aufgabe -->

### Exercise 12.22 {#br-ak-2025-2026-w12-ex-22}

Let $T\subseteq\mathbb R$ be a subset. Show that, in the ring of
continuous functions

$$
R=C(\mathbb R,\mathbb R),
$$

the subset

$$
I=\{f\in R\mid f(x)=0\text{ for all }x\in T\}
$$

is an ideal of $R$.

<!-- upstream_entity: Stetige Funktionen/R/Punkt/Hauptideal/Aufgabe -->

### Exercise 12.23 {#br-ak-2025-2026-w12-ex-23}

Consider the ideal associated with

$$
T=\{0\}\subseteq\mathbb R
$$

in the sense of Exercise 12.22. Is it a principal ideal?

<!-- upstream_entity: Kommutative Ringtheorie/Funktionenringe/Teilmengen und Ideal/Aufgabe -->

### Exercise 12.24 {#br-ak-2025-2026-w12-ex-24}

Let $X$ be a topological space and

$$
R=C^0(X,\mathbb R)
$$

the ring of continuous functions on $X$. For a subset $T\subseteq X$,
show that

$$
I=\{f\in R\mid f|_T=0\}
$$

is an ideal of $R$. Define a ring homomorphism

$$
R/I\longrightarrow C^0(T,\mathbb R).
$$

Is this homomorphism always injective? Is it always surjective?

<!-- upstream_entity: Topologischer Raum/Ring der stetigen reellwertigen Funktionen/Funktorialität/Aufgabe -->

### Exercise 12.25 {#br-ak-2025-2026-w12-ex-25}

Let $X$ and $Y$ be topological spaces and

$$
\varphi:X\longrightarrow Y
$$

a continuous map. Show that it induces a ring homomorphism

$$
\begin{aligned}
C(Y,\mathbb R)&\longrightarrow C(X,\mathbb R),\\
f&\longmapsto f\circ\varphi.
\end{aligned}
$$

<!-- upstream_entity: Kommutative Ringtheorie/Funktionenringe/Aufgabe -->

### Exercise 12.26 {#br-ak-2025-2026-w12-ex-26}

Let $X\subseteq\mathbb R$ and let $C(X,\mathbb R)$ be the ring of
continuous functions from $X$ to $\mathbb R$. Restriction of functions
gives a ring homomorphism

$$
\begin{aligned}
\varphi:C(\mathbb R,\mathbb R)&\longrightarrow C(X,\mathbb R),\\
f&\longmapsto f|_X.
\end{aligned}
$$

1. Show that $\varphi$ is surjective if and only if $X$ is closed.
2. For which sets $X$ is $\varphi$ injective?

## Exercises for submission {#br-ak-2025-2026-w12-submit}

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Element und Abbildung nach affiner Gerade/Konstant und konstant/Aufgabe -->

### Exercise 12.27 (4 points: 2+2) {#br-ak-2025-2026-w12-ex-27}

Let $K$ be an infinite field, $R$ a commutative $K$-algebra of finite
type, and $F\in R$. Let

$$
\varphi^*:K\!-\!\operatorname{Spek}(R)\longrightarrow\mathbb A_K^1
$$

be the spectrum map associated with the substitution homomorphism.

1. Show that $F$ is constant if and only if $\varphi^*$ is constant.
2. Show that this statement need not hold for a finite field.

**Hint:** Also note the different meanings of “constant” in these two contexts.

> **Edition note:** Part (1), as stated in the source, needs an additional
> hypothesis: infinitude of $K$ alone is insufficient. For example, in
> $R=K[\varepsilon]/(\varepsilon^2)$ the nonconstant element
> $F=\varepsilon$ induces the constant zero function, even when $K$ is
> infinite. A sufficient correction is to assume that $K$ is algebraically
> closed and $R$ is reduced, as in Exercise 12.11. More generally, it
> suffices that evaluation on $K$-points separates elements of $R$.
> This is an editorial clarification of the hypothesis, not a public
> source solution.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/C/Homöomorph, nicht isomorph/Integer/Aufgabe -->

### Exercise 12.28 (4 points) {#br-ak-2025-2026-w12-ex-28}

Give an example of two $\mathbb C$-algebras $R$ and $S$ of finite type
that are integral domains, and a $\mathbb C$-algebra homomorphism

$$
\varphi:R\longrightarrow S,
$$

which is not a ring isomorphism, but whose induced spectrum map

$$
\varphi^*:
\mathbb C\!\!-\!\operatorname{Spek}(S)
\longrightarrow
\mathbb C\!\!-\!\operatorname{Spek}(R)
$$

is a homeomorphism.

<!-- upstream_entity: Kommutative Ringtheorie/Algebraisch abgeschlossen/Eine Ganzheitsgleichung/K-Spektrum surjektiv/Aufgabe -->

### Exercise 12.29 (3 points) {#br-ak-2025-2026-w12-ex-29}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type. Consider the finite extension

$$
\varphi:R\longrightarrow
S=R[X]/\left(
X^n+r_{n-1}X^{n-1}+\cdots+r_2X^2+r_1X+r_0
\right).
$$

Show that

$$
\varphi^*:K\!-\!\operatorname{Spek}(S)
\longrightarrow K\!-\!\operatorname{Spek}(R)
$$

is surjective.

<!-- upstream_entity: Algebraische Raumkurven/Monomial/u^5-v^3,u^11-w^3,v^11-w^5/w-u^2v im Radikal/Realisierung in zwei Variablen/Aufgabe -->

### Exercise 12.30 (5 points) {#br-ak-2025-2026-w12-ex-30}

Consider the ideal

$$
\mathfrak a=
\left(U^5-V^3,\,U^{11}-W^3,\,V^{11}-W^5\right)
\subseteq K[U,V,W]
$$

and its zero locus

$$
Z=V(\mathfrak a)\subseteq\mathbb A_K^3.
$$

Show that $W-U^2V$ belongs to the radical of $\mathfrak a$. Use this to
show that $Z$ is isomorphic to a plane algebraic curve.

**Hint:** Use the fact that a radical is the intersection of all prime
ideals containing it, or reduce to the case where $K$ is algebraically closed.
