---
title: "Worksheet 10 - Noetherian modules and Hilbert's Nullstellensatz"
stable_id: br-ak-2025-2026-w10
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 10"
upstream_pageid: 165929
upstream_revid: 1058833
upstream_timestamp: "2025-11-13T14:59:04Z"
upstream_mediawiki_sha1: 48ce873997cecbd45efdceb3a7caa19ae7844876
source_url: "https://de.wikiversity.org/w/index.php?oldid=1058833"
authority_manifest: authority/wikiversity/unit-10/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f8b4f8bf12a0613f774352df31941d79a35d9eed10f2d8fb5570f9ffe07bfb43
worksheet_xml_sha256: 9a52bae904d62f5f15dbf7f7f8ba2a5470bdb4f706773be0b0419f8096511a00
worksheet_expanded_tex_sha256: 1631c95c639e523ea8d4daa7b4aac9460280f2f7c2a13dab49230980675442d3
exercise_map: authority/wikiversity/unit-10/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 972e36256d128916533a33be1d2feedfdecbd133a0dbba96193a85477cf7e92c
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 10 {#br-ak-2025-2026-w10}

## Practice exercises {#br-ak-2025-2026-w10-practice}

<!-- upstream_entity: Endliche Algebra über Körper/Kommutativ/Einheit und Nichtnullteiler/Aufgabe -->

### Exercise 10.1 ★ {#br-ak-2025-2026-w10-ex-01}

Let $K$ be a field and $A$ a commutative $K$-algebra that is finite as a
$K$-module. Show that an element $f\in A$ is a unit if and only if it is a
non-zero-divisor.

<!-- upstream_entity: Endliche Körpererweiterung/Zwischenring/Körper/Aufgabe -->

### Exercise 10.2 {#br-ak-2025-2026-w10-ex-02}

Let $K$ and $L$ be fields, let $K\subseteq L$ be a finite field extension,
and let $A$ be an intermediate ring,

$$
K\subseteq A\subseteq L.
$$

Show that $A$ is also a field.

<!-- upstream_entity: Kommutative Ringtheorie/Endliche Erweiterung/Nichteinheit bleibt Nichteinheit/Aufgabe -->

### Exercise 10.3 {#br-ak-2025-2026-w10-ex-03}

Let $R\subseteq S$ be a finite ring extension and $f\in R$. Show that if
$f$, regarded as an element of $S$, is a unit, then $f$ is a unit in $R$.

<!-- upstream_entity: Kommutativer Ring/Modul/Noethersch und Aufstiegsbedingung/Aufgabe -->

### Exercise 10.4 {#br-ak-2025-2026-w10-ex-04}

Let $R$ be a commutative ring and $M$ an $R$-module. Show that $M$ is
Noetherian if and only if every ascending chain of $R$-submodules

$$
M_0\subseteq M_1\subseteq M_2\subseteq\cdots
$$

becomes stationary.

<!-- upstream_entity: Nichtnullteiler/Kurze exakte Sequenz/Aufgabe -->

### Exercise 10.5 {#br-ak-2025-2026-w10-ex-05}

Let $f\in R$ be a non-zero-divisor in a commutative ring $R$. Show that
this gives a short exact sequence of $R$-modules

$$
0\longrightarrow R\xrightarrow{\cdot f}R
\longrightarrow R/(f)\longrightarrow0.
$$

<!-- upstream_entity: Kommutativer Ring/Ideale/Chinesischer Restsatz/Kurze exakte Sequenz/Aufgabe -->

### Exercise 10.6 ★ {#br-ak-2025-2026-w10-ex-06}

Let $R$ be a commutative ring and $I,J\subseteq R$ ideals. Show that the sequence

$$
0\longrightarrow R/(I\cap J)\longrightarrow R/I\times R/J
\longrightarrow R/(I+J)\longrightarrow0
$$

with maps $r\mapsto(r,r)$ and $(s,t)\mapsto s-t$ is exact.

<!-- upstream_entity: Moduln (kommutative Algebra)/L in M in N/Kurze exakte Sequenz/Aufgabe -->

### Exercise 10.7 {#br-ak-2025-2026-w10-ex-07}

Let $R$ be a commutative ring and $N$ an $R$-module with $R$-submodules

$$
L\subseteq M\subseteq N.
$$

Show that the quotient modules are related by the short exact sequence

$$
0\longrightarrow M/L\longrightarrow N/L
\longrightarrow N/M\longrightarrow0.
$$

<!-- upstream_entity: Modul-Homomorphismus/Exakte Sequenz/Aufgabe -->

### Exercise 10.8 {#br-ak-2025-2026-w10-ex-08}

Let $R$ be a commutative ring and

$$
\varphi:M\longrightarrow N
$$

an $R$-module homomorphism between $R$-modules $M$ and $N$. Show that this
gives a short exact sequence

$$
0\longrightarrow\operatorname{kern}\varphi\longrightarrow M
\longrightarrow\operatorname{bild}\varphi\longrightarrow0.
$$

Let $R$ be a commutative ring and $M$ an $R$-module. The $R$-module

$$
M^*=\operatorname{Hom}_R(M,R)
$$

is called the *dual module* of $M$.

<!-- upstream_entity: Kurze exakte Sequenz/Modul/Duale Sequenz/Aufgabe -->

### Exercise 10.9 ★ {#br-ak-2025-2026-w10-ex-09}

Let $R$ be a commutative ring and let

$$
0\longrightarrow L\longrightarrow M\longrightarrow N\longrightarrow0
$$

be a short exact sequence of $R$-modules $L,M,N$. Show that this gives an
exact sequence of dual modules

$$
0\longrightarrow N^*\longrightarrow M^*\longrightarrow L^*.
$$

<!-- upstream_entity: Kurze exakte Sequenz/Vektorraum/Duale Sequenz/Aufgabe -->

### Exercise 10.10 {#br-ak-2025-2026-w10-ex-10}

Let $K$ be a field and let

$$
0\longrightarrow L\longrightarrow M\longrightarrow N\longrightarrow0
$$

be a short exact sequence of $K$-vector spaces $L,M,N$. Show that this gives
a short exact sequence of dual spaces

$$
0\longrightarrow N^*\longrightarrow M^*\longrightarrow L^*
\longrightarrow0.
$$

<!-- upstream_entity: Kurze exakte Sequenz/Z/Duale Sequenz/Nicht exakt/Aufgabe -->

### Exercise 10.11 {#br-ak-2025-2026-w10-ex-11}

Let $a\ne0$ be an integer. We consider the short exact sequence of
$\mathbb Z$-modules

$$
0\longrightarrow\mathbb Z\xrightarrow{\cdot a}\mathbb Z
\longrightarrow\mathbb Z/(a)\longrightarrow0.
$$

Show that, for $a\geq2$, the sequence that is exact by Exercise 10.9,

$$
0\longrightarrow(\mathbb Z/(a))^*\longrightarrow\mathbb Z^*
\longrightarrow\mathbb Z^*,
$$

cannot be extended exactly to the right by $\longrightarrow0$.

<!-- upstream_entity: Kurze exakte Sequenz/Modul/Erzeugendenzahl/Aufgabe -->

### Exercise 10.12 {#br-ak-2025-2026-w10-ex-12}

Let $R$ be a commutative ring and let

$$
0\longrightarrow L\longrightarrow M\longrightarrow N\longrightarrow0
$$

be a short exact sequence of $R$-modules. Suppose that $L$ has a set of
$R$-module generators with $k$ elements and $N$ has a set of $R$-module
generators with $n$ elements. Show that $M$ has a set of $R$-module
generators with $k+n$ elements.

<!-- upstream_entity: Endlicher Modul/Endliche Algebra/Endlich/Aufgabe -->

### Exercise 10.13 {#br-ak-2025-2026-w10-ex-13}

Let $R$ be a commutative ring, $A$ a commutative finite $R$-algebra, and
$M$ a finite $A$-module. Show that $M$ is also a finite $R$-module.

The following exercises use the notion of an Artinian module, which is
“dual” to the notion of a Noetherian module.

Let $R$ be a commutative ring. An $R$-module $M$ is called *Artinian* if
every descending chain of $R$-submodules

$$
M_1\supseteq M_2\supseteq M_3\supseteq\cdots
$$

becomes stationary. A commutative ring $R$ is called *Artinian* if it is
Artinian as an $R$-module.

<!-- upstream_entity: Artinsche Ringe/Artinsche Integritätsbereiche sind Körper/Aufgabe -->

### Exercise 10.14 {#br-ak-2025-2026-w10-ex-14}

Let $A$ be an Artinian integral domain. Show that $A$ is a field. Give an
example of an Artinian commutative ring that is not a field.

<!-- upstream_entity: Kommutative Algebra/Noethersche bzw. artinsche Moduln/Endomorphismen/Aufgabe -->

### Exercise 10.15 {#br-ak-2025-2026-w10-ex-15}

Let $R$ be a commutative ring and $M$ an $R$-module. Show that if $M$ is
Artinian and

$$
\phi:M\longrightarrow M
$$

is $R$-linear and injective, then $\phi$ is an isomorphism. Also formulate
and prove an analogous statement for the case where $M$ is Noetherian.

<!-- upstream_entity: Kommutative Ringtheorie/f nicht nilpotent/Existenz von Primidealen/Fakt/Beweis/Aufgabe -->

### Exercise 10.16 ★ {#br-ak-2025-2026-w10-ex-16}

Let $R$ be a commutative ring and let $f\in R$ be non-nilpotent. Show that
there is a prime ideal $\mathfrak p$ with $f\notin\mathfrak p$.

<!-- upstream_entity: Kommutative Ringtheorie/Ideale/Radikal ist Durchschnitt von Primidealen/Aufgabe -->

### Exercise 10.17 ★ {#br-ak-2025-2026-w10-ex-17}

Let $\mathfrak a$ be a radical ideal in a commutative ring. Show that
$\mathfrak a$ is an intersection of prime ideals.

One approach follows from the preceding exercise; another follows from
Exercise 13.5 below.

<!-- upstream_entity: Polynom/1/Nicht konstant/Nicht algebraisch/Aufgabe -->

### Exercise 10.18 {#br-ak-2025-2026-w10-ex-18}

Let $K$ be a field and $P\in K[X]$ a nonconstant polynomial. Show that $P$
is not algebraic over $K$.

<!-- upstream_entity: Rationaler Funktionenkörper/Echter Zwischenkörper/Darüber endlich/Aufgabe -->

### Exercise 10.19 {#br-ak-2025-2026-w10-ex-19}

Let $K$ be a field and $L=K(X)$ the field of fractions of the polynomial
ring $K[X]$. Let $M$ be an intermediate field with

$$
K\subseteq M\subseteq L,
\qquad M\ne K.
$$

Show that $M\subseteq L$ is a finite field extension.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Algebraisch/Z/Endlicher Körper/Aufgabe -->

### Exercise 10.20 ★ {#br-ak-2025-2026-w10-ex-20}

Let $A$ be a finitely generated $\mathbb Z$-algebra and $\mathfrak m\subseteq A$
a maximal ideal. Show that the quotient ring $A/\mathfrak m$ is a finite field.

Let $K$ be a field and $A$ a commutative $K$-algebra. Elements
$f_1,\ldots,f_n\in A$ are called *algebraically dependent* if there is a
nonzero polynomial $P\in K[X_1,\ldots,X_n]$ such that

$$
P(f_1,\ldots,f_n)=0.
$$

<!-- upstream_entity: Polynome/n Variablen/Variablen/Algebraisch unabhängig/Aufgabe -->

### Exercise 10.21 {#br-ak-2025-2026-w10-ex-21}

Let $K[X_1,\ldots,X_n]$ be the polynomial ring over a field $K$. Show that
the variables $X_1,\ldots,X_n$ are algebraically independent.

<!-- upstream_entity: Polynome/n Variablen/Algebraisch abhängig/Aufgabe -->

### Exercise 10.22 {#br-ak-2025-2026-w10-ex-22}

Let $K[X_1,\ldots,X_n]$ be the polynomial ring over a field $K$, and let
$n+1$ polynomials

$$
f_1,\ldots,f_{n+1}\in K[X_1,\ldots,X_n]
$$

be given. Show that these polynomials are algebraically dependent.

<!-- upstream_entity: Affiner Raum/Polynomiale Abbildung/Höhere Dimension/Nicht surjektiv/Aufgabe -->

### Exercise 10.23 {#br-ak-2025-2026-w10-ex-23}

Let

$$
\varphi:\mathbb A_K^m\longrightarrow\mathbb A_K^n
$$

be a polynomial map between affine spaces with $m<n$. Show that $\varphi$
is not surjective.

<!-- upstream_entity: Algebra/K/Algebraisch unabhängig/Isomorphie/Aufgabe -->

### Exercise 10.24 {#br-ak-2025-2026-w10-ex-24}

Let $A$ be a commutative $K$-algebra over a field $K$, and let $n$ elements
$f_1,\ldots,f_n\in A$ be given. Show that these elements are algebraically
independent if and only if the $K$-algebra they generate,
$K[f_1,\ldots,f_n]$, is isomorphic to the polynomial ring
$K[X_1,\ldots,X_n]$.

## Exercises for submission {#br-ak-2025-2026-w10-submit}

<!-- upstream_entity: Ebene algebraische Kurve/Restklassenring/Algebraisch abgeschlossen/Endlich über Polynomring in einer Variablen/Aufgabe -->

### Exercise 10.25 - 3 points {#br-ak-2025-2026-w10-ex-25}

Let $K$ be an algebraically closed field and $F\in K[X,Y]$ a nonconstant
polynomial. Show that the quotient ring

$$
K[X,Y]/(F)
$$

can be regarded as a finite $K[T]$-algebra.

<!-- upstream_entity: Kommutative Ringtheorie/Transitivität der Endlichkeit (Algebren)/Aufgabe -->

### Exercise 10.26 - 3 points {#br-ak-2025-2026-w10-ex-26}

Let $R,S,T$ be commutative rings, and let $\varphi:R\to S$ and
$\psi:S\to T$ be ring homomorphisms such that $S$ is finite over $R$ and
$T$ is finite over $S$. Show that $T$ is also finite over $R$.

<!-- upstream_entity: Artinscher Modul/Kurze exakte Sequenz/Aufgabe -->

### Exercise 10.27 - 5 points {#br-ak-2025-2026-w10-ex-27}

Let $A$ be a commutative ring and let

$$
0\longrightarrow M\longrightarrow N\longrightarrow P\longrightarrow0
$$

be a short exact sequence of $A$-modules. Show that $N$ is Artinian if
and only if both $M$ and $P$ are Artinian.

<!-- upstream_entity: Modultheorie/Exakte Komplexe/Kurze exakte Sequenzen/Aufgabe -->

### Exercise 10.28 - 4 points (1+3) {#br-ak-2025-2026-w10-ex-28}

Let $R$ be a commutative ring, and let $M_i$, $i\in\mathbb N$, be
$R$-modules with fixed $R$-module homomorphisms

$$
\varphi_i:M_i\longrightarrow M_{i+1}.
$$

The sequence

$$
\cdots\longrightarrow M_i\longrightarrow M_{i+1}
\longrightarrow M_{i+2}\longrightarrow M_{i+3}\longrightarrow\cdots
$$

is called *exact* if, for every $i$,

$$
\operatorname{Kern}(\varphi_i)=\operatorname{Bild}(\varphi_{i-1}).
$$

1. Show that, in the case of a short exact sequence, this definition agrees
   with Definition 10.2 in the lecture.
2. Now suppose that the sequence is exact, $R=K$ is a field, all the $M_i$ are finitely generated,
   $M_0=0$, and $M_i=0$ for all $i\geq n$ for some $n$. Show that

   $$
   \sum_{i=0}^{n}(-1)^i\operatorname{dim}_K M_i=0.
   $$

*Edition note.* Part 2 requires the sequence to be exact. The source defines this property immediately beforehand but does not repeat it as a hypothesis; it is made explicit here.

<!-- upstream_entity: Körpertheorie/Endliche Erweiterung von Körper/Ist artinsch/Aufgabe -->

### Exercise 10.29 - 3 points {#br-ak-2025-2026-w10-ex-29}

Let $K$ be a field and $A$ a finite $K$-algebra. Show that $A$ is Artinian.
