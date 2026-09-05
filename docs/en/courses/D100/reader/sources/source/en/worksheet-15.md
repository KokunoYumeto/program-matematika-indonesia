---
title: "Worksheet 15 - Local Rings, Topological Filters, and Colimits"
stable_id: br-ak-2025-2026-w15
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 15"
upstream_pageid: 165934
upstream_revid: 1062620
upstream_timestamp: "2025-12-18T15:03:34Z"
upstream_mediawiki_sha1: 346fec4a9ab11ba39f42f25198e5adfc26d6c71c
source_url: "https://de.wikiversity.org/w/index.php?oldid=1062620"
authority_manifest: authority/wikiversity/unit-15/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 86e394725e766838f01eb035ca53044c4d3b85ff20eb99f8fecda9c2a0156425
worksheet_xml_sha256: bdb2534afe94169781ca9c73d16fd50e1d3e511c7e775f776dc99e5eef224085
worksheet_expanded_tex_sha256: 92474c829153b3dc1004c8c916ca77890ac0210ef1425c76f4b76fe5ca7636e0
exercise_map: authority/wikiversity/unit-15/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 3c8c41458f5418ff858a58748ba4b23bc0a8cb34d9c386c155806b4482760470
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 15 {#br-ak-2025-2026-w15}

## Practice exercises {#br-ak-2025-2026-w15-practice}

<!-- upstream_entity: Kommutative Ringtheorie/Lokaler Ring/Definition äquivalent/Aufgabe -->

### Exercise 15.1 {#br-ak-2025-2026-w15-ex-01}

Let $R$ be a commutative ring. Show that the following statements are equivalent.

1. $R$ has exactly one maximal ideal.
2. The set of nonunits $R\setminus R^\times$ is an ideal in $R$.

<!-- upstream_entity: Lokaler Ring/Charakterisierung mit Addition/Aufgabe -->

### Exercise 15.2 {#br-ak-2025-2026-w15-ex-02}

Let $R$ be a nonzero commutative ring. Show that $R$ is local if and only if,
whenever $a+b$ is a unit, at least one of $a$ and $b$ is a unit.

> **Edition note.** The source omits the nonzero-ring hypothesis. The zero
> ring satisfies the displayed unit-sum criterion but has no maximal ideal,
> so it is not local under the definition used in the lecture.

<!-- upstream_entity: Rationale Zahlen/Unterringe/Lokaler Ring/Aufgabe -->

### Exercise 15.3 {#br-ak-2025-2026-w15-ex-03}

Determine all subrings of the rational numbers $\mathbb Q$ that are local rings.

<!-- upstream_entity: Lokaler Ring/Zusamenhängend/Aufgabe -->

### Exercise 15.4 {#br-ak-2025-2026-w15-ex-04}

Let $R$ be a commutative local ring. Show that $R$ is connected.

<!-- upstream_entity: Ring/Maximales Ideale/Restekörper/Aufgabe -->

### Exercise 15.5 {#br-ak-2025-2026-w15-ex-05}

Let $\mathfrak n$ be a maximal ideal in a commutative ring $R$. Let
$R_{\mathfrak n}$ be the localisation of $R$ at $\mathfrak n$, and let

$$
\mathfrak m=\mathfrak nR_{\mathfrak n}
$$

be the maximal ideal of $R_{\mathfrak n}$. Show that

$$
R/\mathfrak n=R_{\mathfrak n}/\mathfrak m.
$$

<!-- upstream_entity: Kommutative Ringtheorie/Primideal/Restekörper als Quotientenring/Fakt/Beweis/Aufgabe -->

### Exercise 15.6 ★ {#br-ak-2025-2026-w15-ex-06}

Let $R$ be a commutative ring and let $\mathfrak p$ be a prime ideal. The
quotient ring

$$
S=R/\mathfrak p
$$

is an integral domain with fraction field $Q=Q(S)$, while
$R_{\mathfrak p}$ is a local ring with maximal ideal
$\mathfrak pR_{\mathfrak p}$. Show that there is a natural isomorphism

$$
Q(S)\cong R_{\mathfrak p}/\mathfrak pR_{\mathfrak p}.
$$

This field is also called the residue field at $\mathfrak p$.

<!-- upstream_entity: Polynomring/Eine Variable/C/Evaluationsabbildung/Aufgabe -->

### Exercise 15.7 {#br-ak-2025-2026-w15-ex-07}

For $a\in\mathbb C$, show that the substitution homomorphism

$$
\begin{aligned}
\mathbb C[X]&\longrightarrow\mathbb C,\\
X&\longmapsto a,
\end{aligned}
$$

agrees with the evaluation map to the residue field at the prime ideal
$(X-a)$, namely

$$
\mathbb C[X]_{(X-a)}/(X-a)\mathbb C[X]_{(X-a)}.
$$

<!-- upstream_entity: Lokaler Ring/Enthält Körper/Gleiche Charakteristik/Aufgabe -->

### Exercise 15.8 {#br-ak-2025-2026-w15-ex-08}

Let $R$ be a local ring with residue field $K$. Show that $R$ and $K$ have
the same characteristic if and only if $R$ contains a field.

<!-- upstream_entity: Lokaler Ring/Restklassenring/Einheiten surjektiv/Aufgabe -->

### Exercise 15.9 ★ {#br-ak-2025-2026-w15-ex-09}

Let $R$ be a local ring and let $\mathfrak a$ be an ideal in $R$. Show
that the map

$$
R^\times\longrightarrow(R/\mathfrak a)^\times
$$

is surjective.

<!-- upstream_entity: Affiner Raum/Algebraisch abgeschlossen/Lokalisierung/Aufgabe -->

### Exercise 15.10 {#br-ak-2025-2026-w15-ex-10}

Let $K$ be an algebraically closed field and let

$$
R=K[X_1,\ldots,X_n].
$$

Show that all localisations of $R$ at maximal ideals are mutually isomorphic.

<!-- upstream_entity: K-Spektrum/Achsenkreuz/Integre und nicht integre Punkte/Aufgabe -->

### Exercise 15.11 {#br-ak-2025-2026-w15-ex-11}

Let $K$ be a field and consider the coordinate cross

$$
V=K\!-\!\operatorname{Spek}\bigl(K[X,Y]/(XY)\bigr).
$$

For each point $P\in V$, determine whether the local ring at $P$ is an
integral domain.

<!-- upstream_entity: Neilsche Parabel/Isomorphe Lokalisierungen/Ausnahme/Aufgabe -->

### Exercise 15.12 {#br-ak-2025-2026-w15-ex-12}

Consider Neil's parabola

$$
C=V(X^2-Y^3)\subseteq\mathbb A_K^2
$$

over an algebraically closed field $K$. Show that all localisations of
$C$ at points $P\ne(0,0)$ are mutually isomorphic, but are not isomorphic
to the localisation at the origin.

<!-- upstream_entity: Y^2 ist X^3+X^2/Lokalisierungen/Aufgabe -->

### Exercise 15.13 {#br-ak-2025-2026-w15-ex-13}

Let $R$ be the localisation at the origin of the curve

$$
C=V(Y^2-X^2-X^3)\subseteq\mathbb A_K^2,
$$

and let $S$ be the localisation of the coordinate cross at the origin.
Are these two local rings isomorphic?

<!-- upstream_entity: Kommutative Ringtheorie/Minimales Primideales/Reduktion von Lokalisierung ist ein Körper/Aufgabe -->

### Exercise 15.14 {#br-ak-2025-2026-w15-ex-14}

Let $R$ be a commutative ring and let $\mathfrak p$ be a prime ideal. Show
that $\mathfrak p$ is a minimal prime ideal if and only if the reduction
of the localisation $R_{\mathfrak p}$ is a field.

<!-- upstream_entity: Lokalisierung/Ideal im Kern/Lokalisierung von Restklassenring/Aufgabe -->

### Exercise 15.15 {#br-ak-2025-2026-w15-ex-15}

Let $R$ be a commutative ring, let $\mathfrak m$ be a maximal ideal with
localisation $R_{\mathfrak m}$, and let $\mathfrak a$ be an ideal
contained in the kernel of the localisation map. Show that
$R_{\mathfrak m}$ is also a localisation of $R/\mathfrak a$.

<!-- upstream_entity: Lokaler Ring/K/Wesentlich von endlichem Typ/Restklassenkörper/Aufgabe -->

### Exercise 15.16 {#br-ak-2025-2026-w15-ex-16}

Let $K$ be a field and let $R$ be a finitely generated $K$-algebra. Let

$$
S=R_{\mathfrak m}
$$

be the localisation of $R$ at a maximal ideal $\mathfrak m$. Show that
the residue field of $S$ is a finite extension of $K$.

<!-- upstream_entity: Lokalisierung/Idealzugehörigkeit/Lokaler Test/Aufgabe -->

### Exercise 15.17 {#br-ak-2025-2026-w15-ex-17}

Let $R$ be a commutative ring, let $f\in R$, and let $\mathfrak a$ be an
ideal. Show that

$$
f\in\mathfrak a
$$

if and only if for every prime ideal $\mathfrak p$ we have

$$
f\in\mathfrak aR_{\mathfrak p}.
$$

**Remark.** For this reason, ideal membership is called a local property.

<!-- upstream_entity: Kommutative Ringtheorie/Lokalisierungen/Reduziert ist lokal/Aufgabe -->

### Exercise 15.18 {#br-ak-2025-2026-w15-ex-18}

Let $R$ be a commutative ring. Prove that the following statements are equivalent.

1. $R$ is reduced.
2. For every prime ideal $\mathfrak p$, the ring $R_{\mathfrak p}$ is reduced.
3. For every maximal ideal $\mathfrak m$, the ring $R_{\mathfrak m}$ is reduced.

**Remark.** For this reason, reducedness is called a local property. Also
give an example of a commutative ring that is not an integral domain but
whose localisations at prime ideals are all integral domains.

<!-- upstream_entity: Integre endlich erzeugte Algebren/Lokaler Isomorphismus/In Umgebung/Aufgabe -->

### Exercise 15.19 ★ {#br-ak-2025-2026-w15-ex-19}

Let $K$ be a field and let $R,S$ be finitely generated $K$-algebras that
are integral domains. Let

$$
\varphi:R\longrightarrow S
$$

be a $K$-algebra homomorphism, and let $\mathfrak n$ be a maximal ideal
in $S$ with

$$
\varphi^{-1}(\mathfrak n)=\mathfrak m.
$$

Suppose the induced map is an isomorphism

$$
R_{\mathfrak m}\longrightarrow S_{\mathfrak n}.
$$

Show that there is an $f\in R$ with $f\notin\mathfrak m$ such that

$$
R_f\longrightarrow S_{\varphi(f)}
$$

is an isomorphism.

<!-- upstream_entity: K-Spektrum/Topologische Filter/Inklusion/Abbildung der Halme/Aufgabe -->

### Exercise 15.20 {#br-ak-2025-2026-w15-ex-20}

Let $K$ be an algebraically closed field, let $R$ be a finitely generated
commutative $K$-algebra, and let $F_1,F_2$ be topological filters in
$K\!-\!\operatorname{Spek}(R)$ with $F_1\subseteq F_2$. Show that there
is a ring homomorphism

$$
\mathcal O_{F_1}\longrightarrow\mathcal O_{F_2}.
$$

<!-- upstream_entity: K-Spektrum/Halm der Strukturgarbe im Punkt/Ist lokal/direkt/Aufgabe -->

### Exercise 15.21 {#br-ak-2025-2026-w15-ex-21}

Let $K$ be an algebraically closed field, let $R$ be a finitely generated
commutative $K$-algebra, and let

$$
P\in K\!-\!\operatorname{Spek}(R).
$$

Without using Theorem 15.12, show that the stalk $\mathcal O_P$ is a local ring.

<!-- upstream_entity: Endlich erzeugte integre K-Algebra/Definitionsort im K-Spektrum ist offen/Aufgabe -->

### Exercise 15.22 ★ {#br-ak-2025-2026-w15-ex-22}

Let $K$ be a field, let $R$ be a finitely generated $K$-algebra that is an
integral domain with fraction field $Q(R)$, and let $q\in Q(R)$. Show
that the set

$$
\left\{P\in K\!-\!\operatorname{Spek}(R)
\mathrel{\Big|}q\in\mathcal O_P\right\}
$$

is open in $K\!-\!\operatorname{Spek}(R)$, where $\mathcal O_P$ denotes
the local ring at $P$.

<!-- upstream_entity: Gerichtetes System/Von kommutativen Gruppen/Kolimes ist kommutative Gruppe/Aufgabe -->

### Exercise 15.23 {#br-ak-2025-2026-w15-ex-23}

Let $I$ be a directed index set and let $(G_i)_{i\in I}$ be a directed
system of abelian groups. Show that its colimit is an abelian group.

<!-- upstream_entity: Gerichtetes System/Kolimes/Universelle Eigenschaft/Mengen und Gruppen/Aufgabe -->

### Exercise 15.24 {#br-ak-2025-2026-w15-ex-24}

Let $I$ be a directed index set and let $(M_i)_{i\in I}$ be a directed
system of sets. Let $N$ be another set. Suppose that for every $i\in I$
a map

$$
\psi_i:M_i\longrightarrow N
$$

is given such that for every $i\preccurlyeq j$ we have

$$
\psi_i=\psi_j\circ\varphi_{ij},
$$

where $\varphi_{ij}$ are the maps of the system. Prove the universal
property of the colimit: there is exactly one map

$$
\psi:\operatorname{colim}_{i\in I}M_i\longrightarrow N
$$

such that

$$
\psi_i=\psi\circ j_i,
$$

where $j_i:M_i\to\operatorname{colim}_{i\in I}M_i$ are the natural maps.

Show also that if $(M_i)_{i\in I}$ is a directed system of groups, $N$ is
a group, and all the $\psi_i$ are group homomorphisms, then $\psi$ is a
group homomorphism as well.

## Exercises for submission {#br-ak-2025-2026-w15-submit}

<!-- upstream_entity: K-Spektrum/2x3-Matrizen vom Rang eins/K-Algebra/Aufgabe -->

### Exercise 15.25 (4 points) {#br-ak-2025-2026-w15-ex-25}

Describe the set $M$ of all $2\times3$ matrices of rank at most one over
a field $K$ as the $K$-spectrum of a suitable $K$-algebra. Show that there
is an isomorphism between a nonempty Zariski-open subset of $M$ and an
open set in $\mathbb A_K^4$.

<!-- upstream_entity: K-Spektrum/Endlich viele Punkte/Umgebungsfilter hat D(f) als Basis/Aufgabe -->

### Exercise 15.26 (4 points) {#br-ak-2025-2026-w15-ex-26}

Let $K$ be a field, let $R$ be a $K$-algebra of finite type, and let
$P_1,\ldots,P_n$ be finitely many points in

$$
X=K\!-\!\operatorname{Spek}(R).
$$

Show that the neighbourhood filter of these points is generated by open
sets of the form $D(f)$. In other words, for every open set $U$ containing
$P_1,\ldots,P_n$, show that there is an $F\in R$ with

$$
P_1,\ldots,P_n\in D(F)\subseteq U.
$$

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektrum/Multiplikatives System und topologischer Filter/Aufgabe -->

### Exercise 15.27 (5 points: 1+2+2) {#br-ak-2025-2026-w15-ex-27}

Let $K$ be a field, let $R$ be a commutative $K$-algebra of finite type,
and let $S$ be a multiplicative system in $R$. Define

$$
F(S)=\left\{U\subseteq K\!-\!\operatorname{Spek}(R)
\mathrel{\Big|}
U\text{ is open and there is }f\in S\text{ with }D(f)\subseteq U
\right\}.
$$

1. Show that $F=F(S)$ is a topological filter in
   $K\!-\!\operatorname{Spek}(R)$.
2. Show that there is a ring homomorphism

   $$
   R_S\longrightarrow\mathcal O_F.
   $$

3. Show that the homomorphism in part 2 is an isomorphism if $K$ is
   algebraically closed and $R$ is reduced.

> **Edition note.** Although the lecture defines the pointwise structure
> rings over an algebraically closed field, the same local-fraction and
> colimit construction is used verbatim in parts 1 and 2 over an arbitrary
> field. The reconstruction assertion in part 3 retains its stated
> algebraically closed and reduced hypotheses.

<!-- upstream_entity: K-Spektrum/Endlich viele Punkte/Umgebungshalm ist nicht lokal/Aufgabe -->

### Exercise 15.28 (4 points) {#br-ak-2025-2026-w15-ex-28}

Let

$$
X=K\!-\!\operatorname{Spek}(R)
$$

be an affine variety, let $P_1,\ldots,P_n\in X$ be finitely many distinct points,
let $F$ be their neighbourhood filter, and let $\mathcal O_F$ be the
associated stalk. Show that $\mathcal O_F$ is a local ring if and only if
$n=1$.

> **Edition note.** The source's $n$ points are understood to form a finite
> set of distinct points; allowing repetitions would make the criterion false.

<!-- upstream_entity: Kommutative Ringtheorie/Nenneraufnahme/Als gerichtetes System/Aufgabe -->

### Exercise 15.29 (4 points) {#br-ak-2025-2026-w15-ex-29}

Let $R$ be a commutative ring and let $S\subseteq R$ be a multiplicative
system. Consider the following partial order on $S$: set
$f\preccurlyeq g$ if $f$ divides a power of $g$, identifying two elements
when this relation holds in both directions. Show that the commutative rings

$$
R_f,\qquad f\in S,
$$

form a directed system and that

$$
\operatorname{colim}_{f\in S}R_f=R_S.
$$
