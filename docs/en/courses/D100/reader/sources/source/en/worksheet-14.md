---
title: "Worksheet 14 - Algebraic Functions, Sheaves, and Minimal Prime Ideals"
stable_id: br-ak-2025-2026-w14
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 14"
upstream_pageid: 165933
upstream_revid: 1061213
upstream_timestamp: "2025-12-04T10:14:37Z"
upstream_mediawiki_sha1: 3313c0d85b8477557eca2efe9b74d71d3b712a4b
source_url: "https://de.wikiversity.org/w/index.php?oldid=1061213"
authority_manifest: authority/wikiversity/unit-14/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a63c3481d0a9cfa9b960f12c9bf0eec9a5d39cecfb61eddb8f9d96190e52e83e
worksheet_xml_sha256: a609fae99cd725b97bb930076be7c1b3929bcee1321fca87e93abaf118c7169e
worksheet_expanded_tex_sha256: 2cbbe34e0c689587e5d7ffe1f6b86893c744409ed7e487db49ce43a42f9edc66
exercise_map: authority/wikiversity/unit-14/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 0d223f7f3c56c4714736dfc6eb3dbd40dc8cd3cb30a05f66281a6f2b1b875dbe
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 14 {#br-ak-2025-2026-w14}

## Practice exercises {#br-ak-2025-2026-w14-practice}

<!-- upstream_entity: Polynomring/1/K-Spektrum/Algebraische Abbildung/Aufgabe -->

### Exercise 14.1 {#br-ak-2025-2026-w14-ex-01}

Let $K$ be an algebraically closed field and let $R=K[X]$ be the polynomial
ring over $K$. Show that every algebraic function $f$ on an open set

$$
U=D(F)\subseteq K\!-\!\operatorname{Spek}(R)=\mathbb A_K^1
$$

has the form

$$
f=\frac GH,
$$

where $G,H\in R$ have no common nonunit factor and $D(F)\subseteq D(H)$.

<!-- upstream_entity: Integritätsbereich/Faktoriell/K-Spektrum/Algebraische Abbildung/Eindeutige Darstellung/Aufgabe -->

### Exercise 14.2 ★ {#br-ak-2025-2026-w14-ex-02}

Let $K$ be an algebraically closed field and let $R$ be a $K$-algebra of
finite type that is a unique factorisation domain. Show that every
algebraic function $f$ on an open set

$$
U\subseteq K\!-\!\operatorname{Spek}(R)
$$

has the form $f=G/H$, where $G,H\in R$ have no common nonunit factor and
$U\subseteq D(H)$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische Funktion auf offener Menge/Ring/Aufgabe -->

### Exercise 14.3 {#br-ak-2025-2026-w14-ex-03}

Complete the proof of Lemma 14.4.

<!-- upstream_entity: K-Spektrum/Quasiaffin/Globaler Schnitt/Stetige Abbildung/Aufgabe -->

### Exercise 14.4 {#br-ak-2025-2026-w14-ex-04}

Let $U\subseteq K\!-\!\operatorname{Spek}(R)$ be an open subset of the
$K$-spectrum of a $K$-algebra $R$ over an algebraically closed field $K$,
and let

$$
f\in\Gamma(U,\mathcal O)
$$

be an algebraic function. Show that $f$ defines a continuous map to $K$.

<!-- upstream_entity: K-Spektrum/Quasiaffin/Ring der algebraischen Funktionen/Reduziert/Aufgabe -->

### Exercise 14.5 {#br-ak-2025-2026-w14-ex-05}

Show that the ring $\Gamma(U,\mathcal O)$ is reduced.

<!-- upstream_entity: Fermat-Kubik/Affin/Algebraische Funktion/Aufgabe -->

### Exercise 14.6 {#br-ak-2025-2026-w14-ex-06}

Let $K$ be an algebraically closed field. Consider the point

$$
P=(0,1)\in V(X^3-Y^3+1)=C\subseteq\mathbb A_K^2
$$

and set $U=C\setminus\{P\}$. Describe an algebraic function on $U$ that
cannot be extended to an algebraic function on all of $C$.

<!-- upstream_entity: Neilsche Parabel/Rationale Funktion mit Pol in (1,1)/Aufgabe -->

### Exercise 14.7 ★ {#br-ak-2025-2026-w14-ex-07}

Consider Neil's parabola

$$
C=V(Y^2-X^3)\subseteq\mathbb A_K^2
$$

and the point $P=(1,1)\in C$. Find an algebraic function defined on
$C\setminus\{P\}$ but not on all of $C$.

**Hint.** Find two different factorisations of $X^3-X^2$.

> **Edition note:** This exercise uses the standing assumption of this
> lecture that $K$ is algebraically closed. The source does not repeat it
> here; the notion of algebraic function used in Definition 14.1 is stated
> under that assumption.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Integritätsbereich/Algebraische Funktion/Durchschnitt/Aufgabe -->

### Exercise 14.8 {#br-ak-2025-2026-w14-ex-08}

Let $K$ be an algebraically closed field, let $R$ be a $K$-algebra of finite
type that is an integral domain, and let

$$
U=D(\mathfrak a)\subseteq K\!-\!\operatorname{Spek}(R),
\qquad
\mathfrak a=(f_1,\ldots,f_n).
$$

Show that

$$
\Gamma(U,\mathcal O)=\bigcap_{i=1}^n R_{f_i},
$$

where the intersection is taken inside the fraction field $Q(R)$.

> **Edition note:** For this fraction-field interpretation, assume
> $U\ne\varnothing$ and omit any zero generators $f_i$. The source does
> not state these qualifications. Localisation at zero is the zero ring
> and cannot be viewed as a subring of $Q(R)$; for $U=\varnothing$ the
> ring of functions is the zero ring instead.

<!-- upstream_entity: K-Spektrum/Quasiaffin/Algebraischen Funktionen/Lokale Eigenschaft/Aufgabe -->

### Exercise 14.9 {#br-ak-2025-2026-w14-ex-09}

Let $R$ be a commutative $K$-algebra of finite type over an algebraically
closed field, let $U\subseteq K\!-\!\operatorname{Spek}(R)$ be open, and
let $f:U\to K$ be a function. Suppose that

$$
U=\bigcup_{i\in I}U_i
$$

is an open cover and that every restriction $f_i=f|_{U_i}$ is an algebraic
function. Show that $f$ itself is algebraic.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Integritätsbereich/Algebraische Funktion/Injektive Restriktion/Aufgabe -->

### Exercise 14.10 {#br-ak-2025-2026-w14-ex-10}

Let $K$ be an algebraically closed field and let $R$ be a $K$-algebra of
finite type that is an integral domain. Show that for open sets
$U\subseteq V$, the restriction map

$$
\Gamma(V,\mathcal O)\longrightarrow\Gamma(U,\mathcal O)
$$

is injective.

> **Edition note:** The source needs the hypothesis $U\ne\varnothing$
> (unless $V$ is also empty). Restriction from a nonempty $V$ to the empty
> set sends all functions to the sole element of the zero ring and is
> not injective.

<!-- upstream_entity: K-Spektrum/Abgeschlossene Einbettung/ux-vy/Auf D(x,y) nicht surjektiv/Aufgabe -->

### Exercise 14.11 {#br-ak-2025-2026-w14-ex-11}

Consider

$$
V=V(XW-YZ)\subseteq\mathbb A_K^4.
$$

Describe an open set $U\subseteq\mathbb A_K^4$ such that the ring
homomorphism corresponding to $U\cap V\subseteq U$,

$$
\Gamma(U,\mathcal O)\longrightarrow\Gamma(U\cap V,\mathcal O),
$$

is not surjective.

The next exercise uses the concept of the limit of a map. Exercise 1.9 may
be helpful.

<!-- upstream_entity: Algebraische Funktion/C/y^2 ist x^2+x^3/Funktionslimes/Aufgabe -->

### Exercise 14.12 {#br-ak-2025-2026-w14-ex-12}

Consider the curve

$$
C=V(Y^2-X^2-X^3)\subseteq\mathbb A_{\mathbb C}^2,
$$

the point $P=(0,0)\in C$, and the open complement $U=C\setminus\{P\}$.

1. Show that $Y/X$ is an algebraic function on $U$ that cannot be extended
   algebraically to all of $C$.
2. Show that the limit at $P$ of the map
   $\varphi=Y/X:U\to\mathbb C$ does not exist.
3. Show that there are sequences $(w_n)_{n\in\mathbb N}$ and
   $(z_n)_{n\in\mathbb N}$ in $U$, both converging to $P$, whose image
   sequences under $\varphi$ converge to different values.

The following concepts are important in many areas of mathematics and
concisely capture essential properties of the structure sheaf on a
$K$-spectrum.

### Supporting definition: presheaves {#br-ak-2025-2026-w14-praberkas}

Let $X$ be a topological space. A *presheaf* $\mathcal F$ on $X$ is an
assignment associating:

- to every open set $U\subseteq X$, a set $\mathcal F(U)$;
- to every inclusion of open sets $U\subseteq V$, a map

  $$
  \rho_{V,U}:\mathcal F(V)\longrightarrow\mathcal F(U),
  $$

such that

$$
\rho_{U,U}=\operatorname{Id}_{\mathcal F(U)}
$$

and, for $U\subseteq V\subseteq W$,

$$
\rho_{W,U}=\rho_{V,U}\circ\rho_{W,V}.
$$

The maps $\rho_{V,U}$ are called *restriction maps*. The presheaf is a
*presheaf of groups* if every $\mathcal F(U)$ is a group and every
restriction map is a group homomorphism. It is a *presheaf of commutative
rings* if every $\mathcal F(U)$ is a commutative ring and every restriction
map is a ring homomorphism.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Prägarbe/Aufgabe -->

### Exercise 14.13 {#br-ak-2025-2026-w14-ex-13}

Show that the assignment associating to every open set

$$
U\subseteq K\!-\!\operatorname{Spek}(R)
$$

the ring of algebraic functions $\Gamma(U,\mathcal O)$, and to every
inclusion $U_1\subseteq U_2$ the restriction map (see Lemma 14.6)

$$
\Gamma(U_2,\mathcal O)\longrightarrow\Gamma(U_1,\mathcal O),
$$

is a presheaf of $K$-algebras.

### Supporting definition: sheaves {#br-ak-2025-2026-w14-sheaf}

A *sheaf* $\mathcal F$ on a topological space $X$ is a presheaf satisfying
the following two properties.

1. **Local uniqueness.** For every open cover $U=\bigcup_{i\in I}U_i$ and
   $s,t\in\mathcal F(U)$, if

   $$
   \rho_{U,U_i}(s)=\rho_{U,U_i}(t)
   \qquad\text{for all }i\in I,
   $$

   then $s=t$.
2. **Gluing.** For every open cover $U=\bigcup_{i\in I}U_i$ and sections
   $s_i\in\mathcal F(U_i)$ that are compatible on each intersection, meaning

   $$
   \rho_{U_i,U_i\cap U_j}(s_i)
   =\rho_{U_j,U_i\cap U_j}(s_j)
   \qquad(i,j\in I),
   $$

   there is an $s\in\mathcal F(U)$ with $s_i=\rho_{U,U_i}(s)$ for all
   $i\in I$.

<!-- upstream_entity: Topologischer Raum/Stetige Abbildungen nach Y/Garbe/Aufgabe -->

### Exercise 14.14 {#br-ak-2025-2026-w14-ex-14}

Let $X,Y$ be topological spaces. For every open set $U\subseteq X$, set

$$
\mathcal C(U)=C^0(U,Y)
=\{\varphi:U\to Y\mid\varphi\text{ is continuous}\}.
$$

Show that this assignment is a sheaf on $X$.

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Garbe/Ringe/Aufgabe -->

### Exercise 14.15 {#br-ak-2025-2026-w14-ex-15}

Let $X$ be a topological space. For every open set $U\subseteq X$, set

$$
\mathcal C(U)=C^0(U,\mathbb R)
=\{\varphi:U\to\mathbb R\mid\varphi\text{ is continuous}\}.
$$

Show that this assignment is a sheaf of commutative $\mathbb R$-algebras
on $X$.

<!-- upstream_entity: Mannigfaltigkeit/Differenzierbare Funktionen/Garbeneigenschaft/Aufgabe -->

### Exercise 14.16 {#br-ak-2025-2026-w14-ex-16}

Let $M$ be a differentiable manifold. For every open set $U\subseteq M$,
consider the set $C^1(U,\mathbb R)$ of differentiable functions on $U$.
Let

$$
M=\bigcup_{i\in I}U_i
$$

be an open cover.

1. Show that if $V\subseteq U$ is open and $f\in C^1(U,\mathbb R)$, then
   $f|_V\in C^1(V,\mathbb R)$.
2. Let $f\in C^1(M,\mathbb R)$. Show that $f=0$ if and only if
   $f|_{U_i}=0$ for every $i$.
3. Suppose that functions $f_i\in C^1(U_i,\mathbb R)$ are given satisfying
   the compatibility condition

   $$
   f_i|_{U_i\cap U_j}=f_j|_{U_i\cap U_j}
   $$

   for all $i,j$. Show that there is an $f\in C^1(M,\mathbb R)$ with
   $f|_{U_i}=f_i$ for all $i$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Garbe/Aufgabe -->

### Exercise 14.17 {#br-ak-2025-2026-w14-ex-17}

Show that the assignment associating to every open set
$U\subseteq K\!-\!\operatorname{Spek}(R)$ the ring of algebraic functions
$\Gamma(U,\mathcal O)$, and to every inclusion $U_1\subseteq U_2$ the
restriction map (see Lemma 14.6)

$$
\Gamma(U_2,\mathcal O)\longrightarrow\Gamma(U_1,\mathcal O),
$$

is a sheaf of $K$-algebras.

The following exercises concern ultrafilters and minimal prime ideals. We
give the definitions.

A prime ideal $\mathfrak p$ in a commutative ring is called a *minimal
prime ideal* if there is no prime ideal $\mathfrak q$ with
$\mathfrak q\subsetneq\mathfrak p$.

Let $R$ be a commutative ring. A multiplicative system $F\subseteq R$ is
called an *ultrafilter* if $0\notin F$ and $F$ is maximal among the
multiplicative systems not containing $0$.

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikatives System/Charakterisierung von Ultrafilter/Aufgabe -->

### Exercise 14.18 {#br-ak-2025-2026-w14-ex-18}

Let $R$ be a commutative ring and let $F\subseteq R$ be a multiplicative
system with $0\notin F$. Show that $F$ is an ultrafilter if and only if for
every $g\in R$ with $g\notin F$ there are $f\in F$ and $n\in\mathbb N$
such that

$$
fg^n=0.
$$

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikatives System/Maximal ohne 1/Komplement ist minimales Primideal/Aufgabe -->

### Exercise 14.19 {#br-ak-2025-2026-w14-ex-19}

Let $R$ be a commutative ring and let $F\subseteq R$ be an ultrafilter.
Show that the complement $R\setminus F$ is a minimal prime ideal in $R$.

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikatives System/Maximal ohne 1/Existenz/Aufgabe -->

### Exercise 14.20 {#br-ak-2025-2026-w14-ex-20}

Let $R$ be a commutative ring and let $S$ be a multiplicative system with
$0\notin S$. Show that $S$ is contained in an ultrafilter.

**Hint.** Use Zorn's lemma.

<!-- upstream_entity: Kommutative Ringtheorie/reduzierte Ringe/Nullteiler und minimale Primideale/Aufgabe -->

### Exercise 14.21 {#br-ak-2025-2026-w14-ex-21}

Let $R$ be a reduced commutative ring. Show that every zero divisor is
contained in a minimal prime ideal.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Affin-algebraische Menge/Korrespondenz/Minimale Primideale/Aufgabe -->

### Exercise 14.22 {#br-ak-2025-2026-w14-ex-22}

Let $K$ be an algebraically closed field and let
$\mathfrak a\subseteq K[X_1,\ldots,X_n]$ be a radical ideal. Set

$$
R=K[X_1,\ldots,X_n]/\mathfrak a,
\qquad
V=V(\mathfrak a).
$$

Show that the irreducible components of $V$ correspond to the minimal prime
ideals of its coordinate ring $R$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen/Minimale Primideale und irreduzible Komponente/Aufgabe -->

### Exercise 14.23 {#br-ak-2025-2026-w14-ex-23}

Let $K$ be an algebraically closed field and let $R$ be a commutative
$K$-algebra of finite type. Show that the minimal prime ideals of $R$
correspond to the irreducible components of $K\!-\!\operatorname{Spek}(R)$.

## Exercises for submission {#br-ak-2025-2026-w14-submit}

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen/Affine Ebene ohne einen Punkt/Schnittring/Aufgabe -->

### Exercise 14.24 (3 points) {#br-ak-2025-2026-w14-ex-24}

Let $K$ be an algebraically closed field, let $P\in\mathbb A_K^2$, and let

$$
U=\mathbb A_K^2\setminus\{P\}.
$$

Show that

$$
\Gamma(U,\mathcal O)=K[X,Y].
$$

In other words, every algebraic function defined away from a single point
of the affine plane extends to that point.

<!-- upstream_entity: Neilsche Parabel/C/Algebraische Funktion/Stetige Fortsetzung/Aufgabe -->

### Exercise 14.25 (5 points: 1+2+2) {#br-ak-2025-2026-w14-ex-25}

Consider Neil's parabola

$$
C=V(X^2-Y^3)\subseteq\mathbb A_{\mathbb C}^2.
$$

1. Show that $D(X)=D(Y)$ on $C$.
2. Show that on $U=D(Y)\subseteq C$, the fraction $X/Y$ defines an
   algebraic function that cannot be extended algebraically to all of $C$.
3. Show that the continuous function $X/Y:D(Y)\to\mathbb C$ has a
   continuous extension to all of $C$.

<!-- upstream_entity: K-Spektrum/Affin/Irreduzibel/Definitionsbereich einer rationalen Funktion/Aufgabe -->

### Exercise 14.26 (4 points) {#br-ak-2025-2026-w14-ex-26}

Let $R$ be a $K$-algebra of finite type that is an integral domain over an
algebraically closed field $K$, and let

$$
q\in Q=Q(R)
$$

be an element of the fraction field of $R$. Show that

$$
\mathfrak a
=\left\{f\in R\mathrel{\Big|}
\text{there is }n\in\mathbb N\text{ with }f^nq\in R\right\}
$$

is an ideal in $R$. Show also that

$$
D(\mathfrak a)\subseteq K\!-\!\operatorname{Spek}(R)
$$

is the maximal domain of definition of the algebraic function $q$.

<!-- upstream_entity: Kommutative Ringtheorie/Nenneraufnahme R_f ist noethersch für Überdeckung/Dann noethersch/Aufgabe -->

### Exercise 14.27 (4 points) {#br-ak-2025-2026-w14-ex-27}

Let $R$ be a commutative ring and let $f_1,\ldots,f_n\in R$ generate the
unit ideal. Suppose that every localisation $R_{f_i}$, $i=1,\ldots,n$, is
Noetherian. Show that $R$ is also Noetherian.
