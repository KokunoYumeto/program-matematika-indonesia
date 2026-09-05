---
title: "Worksheet 11 - Hilbert's Nullstellensatz and coordinate rings"
stable_id: br-ak-2025-2026-w11
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 11"
upstream_pageid: 165930
upstream_revid: 1062657
upstream_timestamp: "2025-12-19T12:03:06Z"
upstream_mediawiki_sha1: 1b95cc02cb9d0260971c1fa369afc8969fa13262
source_url: "https://de.wikiversity.org/w/index.php?oldid=1062657"
authority_manifest: authority/wikiversity/unit-11/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ea2d4936bb27e88b2863f8fecbddd5570992c432aee66c72066597709da65a47
worksheet_xml_sha256: 89a6af1d88b9e07bf99fc5dc6a97d739aab9bc8094a7d9feb70cd3ab681841c4
worksheet_expanded_tex_sha256: abfaeecd8c9dcb591c8757dca4d28a5f91e1ab1595889380903dc8858dd81eac
exercise_map: authority/wikiversity/unit-11/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 6298bafd7656e4653b504706b437e89de7faa92a75fac10c31d51ad9644a20cf
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 11 {#br-ak-2025-2026-w11}

## Practice exercises {#br-ak-2025-2026-w11-practice}

<!-- upstream_entity: Hilbertscher Nullstellensatz/Eindimensional/Direkt/Aufgabe -->

### Exercise 11.1 {#br-ak-2025-2026-w11-ex-01}

Let $K$ be an algebraically closed field. Prove Hilbert's Nullstellensatz
directly for the polynomial ring in one variable.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Einzelne Funktionen/Radikal/Aufgabe -->

### Exercise 11.2 {#br-ak-2025-2026-w11-ex-02}

Let $K$ be an algebraically closed field and

$$
f,g\in K[X_1,\ldots,X_n].
$$

Show that

$$
V(f)\subseteq V(g)
$$

holds if and only if there are a natural number $r$ and
$h\in K[X_1,\ldots,X_n]$ with

$$
fh=g^r.
$$

Also consider the special cases where $f$, or where $g$, is a constant polynomial.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Korrespondenz/Maximales Ideal/Aufgabe -->

### Exercise 11.3 {#br-ak-2025-2026-w11-ex-03}

Show that, in the correspondence given by Hilbert's Nullstellensatz,
points correspond to maximal ideals.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Korrespondenz/Primideal/Fakt/Beweis/Aufgabe -->

### Exercise 11.4 {#br-ak-2025-2026-w11-ex-04}

Show that, in the correspondence given by Hilbert's Nullstellensatz,
irreducible varieties correspond to prime ideals.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Nullstellenfrei/Einheit/Aufgabe -->

### Exercise 11.5 {#br-ak-2025-2026-w11-ex-05}

Let $K$ be an algebraically closed field. Prove directly the following
special case of Hilbert's Nullstellensatz: if

$$
f\in K[X_1,\ldots,X_n]
$$

has no zero in $K^n$, then $f$ is a nonzero constant polynomial.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Ebene algebraische Kurven/R und C/1/Aufgabe -->

### Exercise 11.6 ★ {#br-ak-2025-2026-w11-ex-06}

Consider the two polynomials $X^2+Y^2$ and $X^2-Y^3$ and the corresponding
algebraic curves over the fields $\mathbb R$ and $\mathbb C$.

1. Does

   $$
   V(X^2+Y^2)\subseteq V(X^2-Y^3)
   $$

   hold in $\mathbb A_{\mathbb R}^2$?
2. Does the same inclusion hold in $\mathbb A_{\mathbb C}^2$?
3. Does $X^2-Y^3$ belong to the radical of $(X^2+Y^2)$ in $\mathbb R[X,Y]$?
4. Does $X^2-Y^3$ belong to the radical of $(X^2+Y^2)$ in $\mathbb C[X,Y]$?

<!-- upstream_entity: Hilbertscher Nullstellensatz/C/Linearkombination mit Funktionen/Aufgabe -->

### Exercise 11.7 ★ {#br-ak-2025-2026-w11-ex-07}

Let polynomials

$$
f_1,\ldots,f_k\in\mathbb C[X_1,\ldots,X_n]
$$

be given, regarded as functions

$$
f_i:\mathbb C^n\longrightarrow\mathbb C.
$$

Let $f\in\mathbb C[X_1,\ldots,X_n]$ be another polynomial, and let

$$
g_1,\ldots,g_k:\mathbb C^n\longrightarrow\mathbb C
$$

be functions that need not be polynomial. Suppose that the following
equality of functions holds:

$$
f=g_1f_1+\cdots+g_kf_k.
$$

Show that $f$ belongs to the radical of $(f_1,\ldots,f_k)$.

<!-- upstream_entity: Rationale Funktionen/Nullstellenfrei/Ring/Aufgabe -->

### Exercise 11.8 {#br-ak-2025-2026-w11-ex-08}

Let $K$ be a field and $n\in\mathbb N_+$. Show that all functions
$\varphi:K^n\to K$ of the form

$$
\varphi=\frac{P}{Q},
$$

where $P,Q\in K[X_1,\ldots,X_n]$ and $Q$ has no zero on $K^n$, form a
commutative ring. Show that if $K$ is algebraically closed, this ring
coincides with the polynomial ring.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Endlicher Körper/Nullstellen und Radikale/Aufgabe -->

### Exercise 11.9 {#br-ak-2025-2026-w11-ex-09}

Let $K$ be a finite field. Show that there are only finitely many zero
loci in $\mathbb A_K^n$, but infinitely many radical ideals in
$K[X_1,\ldots,X_n]$.

<!-- upstream_entity: Kommutative Ringtheorie/Einheitsideal/Endlich viele Erzeuger/Aufgabe -->

### Exercise 11.10 {#br-ak-2025-2026-w11-ex-10}

Let $R$ be a commutative ring and let $f_j$, $j\in J$, be a family of
elements of $R$. Suppose that the $f_j$ together generate the unit ideal.
Show that there is a finite subfamily

$$
f_j,\qquad j\in J_0\subseteq J,
$$

that also generates the unit ideal.

<!-- upstream_entity: Affine Varietäten/Affine Äquivalenz/Radikal und Nullstellenmenge/Aufgabe -->

### Exercise 11.11 {#br-ak-2025-2026-w11-ex-11}

Let $K$ be an algebraically closed field and

$$
\mathfrak a,\mathfrak b\subseteq K[X_1,\ldots,X_n]
$$

radical ideals. Show that the zero loci $V(\mathfrak a)$ and
$V(\mathfrak b)$ are affine-linearly equivalent if and only if there is
an affine-linear change of variables taking one ideal to the other.

### Aside: extension ideals {#br-ak-2025-2026-w11-note-01}

Let

$$
\varphi:A\longrightarrow B
$$

be a ring homomorphism between commutative rings $A$ and $B$. For an ideal
$\mathfrak a\subseteq A$, the ideal in $B$ generated by
$\varphi(\mathfrak a)$ is called the *extension ideal* of $\mathfrak a$
under $\varphi$. It is denoted by $\mathfrak aB$. If $\varphi$ is
surjective, this is simply the image ideal.

<!-- upstream_entity: Idealzugehörigkeit/Reell/Komplex/Aufgabe -->

### Exercise 11.12 {#br-ak-2025-2026-w11-ex-12}

Let

$$
\mathfrak a\subseteq\mathbb R[X_1,\ldots,X_n]
$$

be an ideal and $f\in\mathbb R[X_1,\ldots,X_n]$. Show that
$f\in\mathfrak a$ if and only if

$$
f\in\mathfrak a\mathbb C[X_1,\ldots,X_n]
$$

for this extension ideal.

<!-- upstream_entity: Ebene algebraische Kurven/Graph von x auf V(xy)/Skizziere/Aufgabe -->

### Exercise 11.13 {#br-ak-2025-2026-w11-ex-13}

Sketch the graphs of the functions $x$ and $y$ on $V(xy)$. Convince yourself
that the product $xy$ is the zero function.

<!-- upstream_entity: Endliche Punktmenge/Koordinatenring/Aufgabe -->

### Exercise 11.14 {#br-ak-2025-2026-w11-ex-14}

Determine the coordinate ring of an affine algebraic set
$V\subseteq\mathbb A_K^n$ consisting of $d$ points.

<!-- upstream_entity: Affine Ebene/Gerade/Koordinatenring/1/Aufgabe -->

### Exercise 11.15 {#br-ak-2025-2026-w11-ex-15}

Determine the coordinate ring of the affine algebraic set

$$
V=V(5X-8Y+3)\subseteq\mathbb A_K^2.
$$

<!-- upstream_entity: Affin-algebraische Mengen/Hyperbel/Koordinatenring über Z mod 11/Inverses von 4x^3/Aufgabe -->

### Exercise 11.16 {#br-ak-2025-2026-w11-ex-16}

Consider the hyperbola $V(xy-1)$ over the field $K=\mathbb Z/(11)$.
Determine the inverse of $4x^3$ in the corresponding coordinate ring.

<!-- upstream_entity: Affin-algebraische Mengen/Inklusion und Koordinatenring/Aufgabe -->

### Exercise 11.17 {#br-ak-2025-2026-w11-ex-17}

Let $K$ be a field and

$$
V,W\subseteq\mathbb A_K^n
$$

affine algebraic sets with $V\subseteq W$. Define a $K$-algebra
homomorphism between the two coordinate rings $R(V)$ and $R(W)$, and
describe its main properties. Give an example of two affine algebraic
sets neither of which contains the other, but whose coordinate rings are
isomorphic.

<!-- upstream_entity: Polynomring/Restklassenring/Radikalgleich/Gleiche Radikale/Aufgabe -->

### Exercise 11.18 {#br-ak-2025-2026-w11-ex-18}

Let $K$ be a field and

$$
\mathfrak a,\mathfrak b\subseteq K[X_1,\ldots,X_n]
$$

ideals with the same radical. Show that there is a natural bijection
between the radical ideals of the quotient rings

$$
K[X_1,\ldots,X_n]/\mathfrak a
\qquad\text{and}\qquad
K[X_1,\ldots,X_n]/\mathfrak b.
$$

<!-- upstream_entity: Koordinatenring/Endlicher Körper/Nicht nur Frobenius Gleichung/Beispiel/Aufgabe -->

### Exercise 11.19 {#br-ak-2025-2026-w11-ex-19}

Let $K$ be a field with $q$ elements and
$V=V(\mathfrak a)\subseteq\mathbb A_K^n$ an affine algebraic set. Show
that the coordinate ring of $V$ need not equal

$$
K[x_1,\ldots,x_n]\big/
\big((x_1^q-x_1,\ldots,x_n^q-x_n)+\mathfrak a\big).
$$

> **Edition note:** The source typographically places $+\mathfrak a$
> outside the denominator of the quotient ring. The parentheses above
> make the intended mathematical reading explicit.
> With this reading, however, the source assertion is false: the displayed
> quotient always is the coordinate ring of $V$. Indeed, the quotient by
> the Frobenius equations is the ring of all functions $K^n\to K$, a finite
> product of copies of $K$; imposing $\mathfrak a$ leaves precisely the
> factors indexed by $V(\mathfrak a)$. This is an editorial correction,
> not a public source solution.

<!-- upstream_entity: Algebraische Raumkurven/Schnitt/Zylinder und Kugel/(x-3)^2+y^2+z^2-7/Realisierung in zwei Variablen/Aufgabe -->

### Exercise 11.20 {#br-ak-2025-2026-w11-ex-20}

Let $K$ be a field of characteristic $0$. Consider the intersection of a
cylinder and a sphere,

$$
C=V(X^2+Y^2-1)\cap
V((X-3)^2+Y^2+Z^2-7)\subseteq\mathbb A_K^3.
$$

Show that the coordinate ring of $C$ can be written as a quotient ring of
a polynomial ring in two variables.

## Exercises for submission {#br-ak-2025-2026-w11-submit}

<!-- upstream_entity: Identitätssatz für Polynome/Komplex-analytisch/Aufgabe -->

### Exercise 11.21 (4 points) {#br-ak-2025-2026-w11-ex-21}

Let $F\in\mathbb C[X_1,\ldots,X_n]$ and let
$U\subseteq\mathbb A_{\mathbb C}^n$ be a nonempty subset open in the
metric topology. If $F|_U=0$ is the zero function, show that $F$ is the
zero polynomial.

<!-- upstream_entity: Hilberts Nullstellensatz/Algebraisch abgeschlossen/Keine gemeinsame Nullstelle/Dann Einheitsideal/Aufgabe -->

### Exercise 11.22 (3 points) {#br-ak-2025-2026-w11-ex-22}

Prove Corollary 11.3 directly from Theorem 10.10.

<!-- upstream_entity: Hilberts Nullstellensatz/Rabinowich-Trick/Aufgabe -->

### Exercise 11.23 (7 points) {#br-ak-2025-2026-w11-ex-23}

Let $K$ be an algebraically closed field and $R$ the polynomial ring in
$n$ variables over $K$. We want to understand an alternative proof,
based on Corollary 11.3, that

$$
\operatorname{Id}(V(J))=\operatorname{rad}(J)
$$

for every ideal $J$ in $R$. Let $f\in\operatorname{Id}(V(J))$. Consider
the ring $R[T]$ and show that the ideal

$$
J'=(J,1-f\cdot T)
$$

is the unit ideal. Deduce that $f$ belongs to the radical of $J$.

<!-- upstream_entity: Affin-algebraische Mengen/Vergleich von Mengen und ihr Bild im Graph/Aufgabe -->

### Exercise 11.24 (3 points) {#br-ak-2025-2026-w11-ex-24}

Let $F\in K[X_1,\ldots,X_n]$ and consider the polynomial map

$$
\begin{aligned}
\varphi:\mathbb A_K^n&\longrightarrow\mathbb A_K^{n+1},\\
(x_1,\ldots,x_n)&\longmapsto
(x_1,\ldots,x_n,F(x_1,\ldots,x_n)),
\end{aligned}
$$

which defines a bijection between affine space and the graph of $F$. For
an affine algebraic set $V(\mathfrak a)\subseteq\mathbb A_K^n$, consider
the image $V'=\varphi(V)$. Show that $V'$ is also affine algebraic and
give an ideal describing it. Show that $V$ is irreducible if and only if
$V'$ is irreducible.

<!-- upstream_entity: Ebene algebraische Kurven/Schnitt/x^2+y^2-2 und x^2+2y^2-1/Über Z mod 7/Punkte in Erweiterungskörper/Aufgabe -->

### Exercise 11.25 (5 points) {#br-ak-2025-2026-w11-ex-25}

Consider the two algebraic curves

$$
V(x^2+y^2-2)
\qquad\text{and}\qquad
V(x^2+2y^2-1)
$$

over the field $\mathbb Z/(7)$. Show that their intersection is empty,
then find an extension field $K\supseteq\mathbb Z/(7)$ over which it
is nonempty. Calculate all intersection points over $K$ and over every
other extension field. Also describe the coordinate ring of the intersection.

<!-- upstream_entity: Affine Ebene/Endlich viele Punkte/Beliebige Wertvorgabe/Funktion/Aufgabe -->

### Exercise 11.26 (4 points) {#br-ak-2025-2026-w11-ex-26}

Let $K$ be a field, and $P_1,\ldots,P_n$ finitely many points in the
affine plane $\mathbb A_K^2$. Let $a_1,\ldots,a_n\in K$ be arbitrarily
prescribed values. Show that there is a polynomial $F\in K[X,Y]$ with

$$
F(P_i)=a_i\qquad\text{for every }i=1,\ldots,n.
$$

> **Edition note:** The points must be pairwise distinct, as is implicit
> in the source's reference to finitely many points. If repetitions are
> allowed, the prescribed values must agree whenever $P_i=P_j$.
