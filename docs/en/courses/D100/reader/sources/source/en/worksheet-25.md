---
title: "Worksheet 25 - Power Series Solutions for Algebraic Curves"
stable_id: br-ak-2012-w25
language: en
source_course: "Kurs:Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 25"
upstream_pageid: 50760
upstream_revid: 793493
upstream_timestamp: "2022-08-25T06:03:57Z"
upstream_mediawiki_sha1: 1418cec6171ff8fd056dda7e6461f5ca4d91d910
source_url: "https://de.wikiversity.org/w/index.php?oldid=793493"
authority_manifest: authority/wikiversity/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7cafbca7b5fd080529c2019967647ef8ffa823539b2113caaf0ad65e56d6afc1
worksheet_xml_sha256: f682934e1b3b2cc74a078af4611c56de2aa73b41cfa5d61edf406ff7b13601f7
worksheet_expanded_tex_sha256: 40661bb4202b74ed245da30306df0456c3b60d17ee62e054871386a70300514e
exercise_map: authority/wikiversity/unit-25/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 1a887b81de9ccf9707e1e4835e477f9c9fb4a4358ab697242b17fd29873e8370
license: "CC BY-SA 4.0"
source_component_license_route: "Semantic source: CC BY-SA 4.0; historical official PDFs retain the CC BY-SA 2.0 Germany and CC BY-SA 4.0 notices"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
correction_ids: "AGC-CORR-0094; AGC-CORR-0095"
source_discrepancies: 1
source_discrepancy_ids: "AGC-CORR-0096; AGC-U25-POINT-001"
reader_media_positions: 0
---

# Worksheet 25 {#br-ak-2012-w25}

## Warm-up exercises {#br-ak-2012-w25-practice}

<!-- upstream_entity: Ebene algebraische Kurve/Potenzreihenansatz/x^3+y^2-xy+x/Nullpunkt/Aufgabe -->

### Exercise 25.1 ★ {#br-ak-2012-w25-ex-01}

For the plane algebraic curve

$$
V\left(X^3+Y^2-XY+X\right),
$$

determine a nonconstant power series solution

$$
X=F(Y)
$$

at the origin through degree six.

<!-- upstream_entity: Ebene algebraische Kurve/Potenzreihenansatz/x^2y+x^2+y^2-5xy+y/Nullpunkt/Aufgabe -->

### Exercise 25.2 ★ {#br-ak-2012-w25-ex-02}

For the plane algebraic curve

$$
V\left(X^2Y+X^2+Y^2-5XY+Y\right),
$$

determine a nonconstant power series solution

$$
Y=F(X)
$$

at the origin through fifth order.

The following exercises concern the completion of a local ring.

<!-- upstream_entity: Komplettierung eines lokalen Ringes/Begriff und kanonische Abbildung/Aufgabe -->

### Exercise 25.3 {#br-ak-2012-w25-ex-03}

Let $R$ be a local ring with maximal ideal $\mathfrak m$. Consider the
diagram

$$
\longrightarrow R/\mathfrak m^4
\longrightarrow R/\mathfrak m^3
\longrightarrow R/\mathfrak m^2
\longrightarrow R/\mathfrak m.
$$

The maps are the canonical projections

$$
\varphi_n:R/\mathfrak m^{n+1}\longrightarrow R/\mathfrak m^n
$$

induced by the ideal inclusions $\mathfrak m^{n+1}\subseteq\mathfrak m^n$.
A sequence of elements

$$
a_n\in R/\mathfrak m^n
$$

is called *compatible* if

$$
\varphi_n(a_{n+1})=a_n
$$

for every $n$. Define a ring structure on the set of all such compatible
sequences. This ring is called the *completion* of $R$. Also show that there
is a canonical ring homomorphism from $R$ to its completion.

<!-- upstream_entity: Komplettierung eines lokalen Ringes/Eindimensional/Injektivität der kanonischen Abbildung/Aufgabe -->

### Exercise 25.4 {#br-ak-2012-w25-ex-04}

Let $R$ be a one-dimensional Noetherian local commutative ring. Show that
the canonical map from $R$ to its completion is injective.

> **Remark.** This injectivity holds for every Noetherian local ring, but
> the proof is more difficult.

<!-- upstream_entity: Kommutative Ringtheorie/Ideal-adische Topologie eines Rings/Aufgabe -->

### Exercise 25.5 {#br-ak-2012-w25-ex-05}

Let $R$ be a commutative ring and $I$ an ideal. Show that, for each $x\in R$,
the family

$$
\left\{x+I^n\mid n\in\mathbb N\right\}
$$

defines a neighbourhood basis at $x$. These families define the $I$-adic
topology on $R$. Show also that this topology is Hausdorff if and only if

$$
\bigcap_n I^n=\{0\}.
$$

> **Remark.** The completion of a local ring with respect to its maximal
> ideal is precisely its topological completion for this topology.

## Exercises for submission {#br-ak-2012-w25-submitted}

<!-- upstream_entity: Ebene algebraische Kurve/Kardioide/Potenzreihe in (2,0) bis Term c4/Aufgabe -->

### Exercise 25.6 (4 points) {#br-ak-2012-w25-ex-06}

Consider the cardioid

$$
V\left(\left(X^2+Y^2\right)^2
-2X\left(X^2+Y^2\right)-Y^2\right)
$$

at $(2,0)$. Determine a formal parametrisation of the curve at this point,
through the fifth term, in terms of a tangent parameter.

> **Edition note - base field.** The source does not specify the base
> field. For the geometric interpretation of the cardioid and tangent
> parameter in this exercise, the edition uses $\mathbb R$ as the base
> field; in particular, it has characteristic zero.

<!-- upstream_entity: Potenzreihe/Lösung für Einheitskreis/Aufgabe -->

### Exercise 25.7 (4 points) {#br-ak-2012-w25-ex-07}

Let $K$ be a field with $\operatorname{char}(K)\ne2$. Consider the unit
circle

$$
X^2+Y^2=1
$$

at $(1,0)$. Determine power series

$$
G,H\in K[[T]]
$$

with initial conditions

$$
a_0=1,\qquad a_1=0,\qquad b_0=0,\qquad b_1=1,
$$

and satisfying

$$
G(T)^2+H(T)^2=1.
$$

> **Edition note - characteristic.** The source places no restriction on
> the characteristic of $K$. The condition $\operatorname{char}(K)\ne2$
> is added because, in characteristic $2$, the coefficient of $T^2$ in the
> required equation would force $1=0$, so series with these initial
> conditions could not exist.

<!-- upstream_entity: Potenzreihe/Neilsche Parabel in (1,1)/Lösung als Graph/Aufgabe -->

### Exercise 25.8 (4 points) {#br-ak-2012-w25-ex-08}

Consider Neil's parabola

$$
C=V\left(Y^3-X^2\right)
$$

at $(1,1)$. Find a parametrisation of the curve at this point by power
series through the fifth term, such that one of the series is a linear
polynomial.

<!-- upstream_entity: Potenzreihenring/Eine Variable/Quotientenkörper/Formale Laurentreihen/Aufgabe -->

### Exercise 25.9 (3 points) {#br-ak-2012-w25-ex-09}

Let $K$ be a field. A *formal Laurent series with finite principal part*
is an infinite sum of the form

$$
F=\sum_{n=k}^{\infty}a_nT^n,
\qquad a_n\in K,\quad k\in\mathbb Z.
$$

Show that the ring of these formal series, with suitable ring operations,
is isomorphic to the field of fractions of the power series ring $K[[T]]$.

<!-- upstream_entity: Polynomring in einer Variablen über Körper/Komplettierung ist Potenzreihenring/Aufgabe -->

### Exercise 25.10 (4 points) {#br-ak-2012-w25-ex-10}

Let $K$ be a field and $K[T]$ the polynomial ring in one variable. Let $R$
be the localisation of $K[T]$ at the maximal ideal

$$
\mathfrak m=(T).
$$

Show that the completion of $R$ is isomorphic to the power series ring
$K[[T]]$.

<!-- upstream_entity: Potenzreihenring eine Variable/Keine Quadratwurzel aus T/Quadratwurzel aus T+2 über Z mod 7/Aufgabe -->

### Exercise 25.11 (4 points) {#br-ak-2012-w25-ex-11}

Let $K$ be a field and

$$
R=K[[T]]
$$

the power series ring. Show that $T$ has no square root in $R$. Show also
that, when $K=\mathbb Z/(7)$, the element $T+2$ has a square root in $R$,
and determine the first five coefficients of one such square root.

<!-- upstream_entity: Ebene integrale Kurve/Potenzreihenlösung/Lift in die Normalisierung/Aufgabe -->

### Exercise 25.12 (5 points) {#br-ak-2012-w25-ex-12}

Let

$$
F\in K[X,Y]
$$

be an irreducible polynomial and

$$
R=K[X,Y]/(F)
$$

the integral coordinate ring of the plane curve

$$
C=V(F).
$$

Let

$$
R\longrightarrow S=R^{\operatorname{norm}}
$$

be the normalisation of $R$, and let

$$
R\longrightarrow K[[T]]
$$

be the ring homomorphism corresponding to a nonconstant formal power series
solution of the curve. Show that there is a unique ring homomorphism

$$
S\longrightarrow K[[T]]
$$

making the diagram

$$
\begin{array}{ccc}
R & \longrightarrow & S \\
& \searrow & \downarrow \\
& & K[[T]]
\end{array}
$$

commute.

## Exercise for upload {#br-ak-2012-w25-upload}

<!-- upstream_entity: Ebene Kurven/Tangenten und Potenzreihen/Bilder für Beispiele/Zeichne/Aufgabe -->

### Exercise 25.13 (4 points) {#br-ak-2012-w25-ex-13}

Using suitable software, plot one of the example curves from the lecture,
together with the various polynomial approximations computed there.

> **Edition note - discrepancy in source points.** The official worksheet
> displays 4 points for this exercise, whereas the transcluded semantic
> exercise page records 3 points. The edition retains the displayed value
> of 4 and records the exercise page's value of 3 without silently
> reconciling them.
