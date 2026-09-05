---
title: "Worksheet 12 - The Projective Spectrum of a Graded Ring"
stable_id: br-bgk-2019-w12
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 12"
upstream_pageid: 110219
upstream_revid: 660098
upstream_timestamp: "2020-10-12T13:10:37Z"
upstream_mediawiki_sha1: ed53f8b78bd5729244e9d7576a281721387c234a
source_url: "https://de.wikiversity.org/w/index.php?oldid=660098"
authority_manifest: authority/wikiversity-bgk/unit-12/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 0e83f8718364e1d902dbe961cbf142cc7fb61e4ebfc7537f24488d508334e914
worksheet_xml: authority/wikiversity-bgk/unit-12/worksheet-12.xml
worksheet_xml_sha256: 7e4960f06b955fb3255110735f89020ae9ca348834cd2c5f891977f6b3d4c0b9
worksheet_expanded_tex: authority/wikiversity-bgk/unit-12/worksheet-12-expanded.tex
worksheet_expanded_tex_sha256: d411c9610c0dc133391df2ca2e010a7e42b58cd00e0bc6704a3d129d95d56eaa
official_pdf: authority/artifacts/bgk-worksheet-12-official.pdf
official_pdf_sha256: 5b789ca531394c68352a85464ff7030f5d07ff70276a22e7202a72f15c5e85a8
ordered_exercise_map: authority/wikiversity-bgk/unit-12/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 62678f3ece59348d362ed7bdf32726642957e6e977970fb276238ad2387e610a
exercise_count: 19
public_solution_count: 2
public_solution_numbers: "5, 10"
media_credits: source/id-ID/media-credits-bgk-unit-12.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 12: The Projective Spectrum of a Graded Ring {#br-bgk-2019-w12}

Asterisks mark exactly the two exercises with frozen public solutions, Exercises 12.5 and 12.10. The other seventeen exercises have negative candidate results; this edition creates no new solutions.

<!-- upstream_entity: Graduierte Algebra/1 in 0ter Stufe/Aufgabe -->

## Exercise 12.1 {#br-bgk-2019-w12-ex01}

Let $R$ be a commutative ring, $D$ a commutative group, and $A$ a $D$-graded $R$-algebra. Prove that

$$
1\in A_0,
$$

and deduce that $A_0$ is an $R$-subalgebra of $A$.

<!-- upstream_entity: Graduierter Ring/Stufe mit Einheit/Isomorph/Aufgabe -->

## Exercise 12.2 {#br-bgk-2019-w12-ex02}

Let

$$
A=\bigoplus_{d\in D}A_d
$$

be a graded commutative ring, and suppose that the component $A_e$ contains a unit. Prove that $A_e$ is isomorphic to $A_0$ as an $A_0$-module.

<!-- upstream_entity: Graduierter kommutativer Ring/Homogenes Ideal/Restklassenring/Fakt/Beweis/Aufgabe -->

## Exercise 12.3 {#br-bgk-2019-w12-ex03}

Let $R$ be a commutative ring, $D$ a commutative group, and $A$ a $D$-graded commutative $R$-algebra. Let $\mathfrak a\subseteq A$ be a homogeneous ideal. Prove that the quotient ring $A/\mathfrak a$ is also $D$-graded.

<!-- upstream_entity: Homogene Polynome/n Variablen/Monomanzahl/Aufgabe -->

## Exercise 12.4 {#br-bgk-2019-w12-ex04}

Prove that a polynomial ring in $n$ variables contains exactly

$$
\binom{d+n-1}{n-1}
$$

monomials of degree $d$.

<!-- upstream_entity: Monomiales Ideal/Produkt/Erzeugergrad/Aufgabe -->

## Exercise 12.5 ★ {#br-bgk-2019-w12-ex05}

Give an example of two monomial ideals $\mathfrak a$ and $\mathfrak b$ in a polynomial ring and a natural number $d$ such that the product ideal $\mathfrak a\mathfrak b$ has a generating system consisting of monomials of degree at most $d$, but neither of the two ideals has such a generating system.

<!-- upstream_entity: Projektives Spektrum/Topologie/Aufgabe -->

## Exercise 12.6 {#br-bgk-2019-w12-ex06}

Let $R$ be a $\mathbb Z$-graded ring. Prove that the subsets

$$
D_+(\mathfrak a)\subseteq\operatorname{Proj}(R),
$$

for homogeneous ideals $\mathfrak a\subseteq R$, do indeed define a topology on the projective spectrum $\operatorname{Proj}(R)$.

<!-- upstream_entity: Projektives Spektrum/Topologie/Basis/Aufgabe -->

## Exercise 12.7 {#br-bgk-2019-w12-ex07}

Let $R$ be a $\mathbb Z$-graded ring. Prove that the open subsets

$$
D_+(f)\subseteq\operatorname{Proj}(R),
$$

for homogeneous elements $f\in R_+$, form a basis for the topology of the projective spectrum.

<!-- upstream_entity: Achsenkreuz/Projektives Spektrum/Aufgabe -->

## Exercise 12.8 {#br-bgk-2019-w12-ex08}

Determine the projective spectrum associated with the coordinate cross

$$
\operatorname{Spek}(K[X,Y]/(XY))
$$

with its standard grading.

<!-- upstream_entity: Achsenebenen/Projektives Spektrum/Skizze/Aufgabe -->

## Exercise 12.9 {#br-bgk-2019-w12-ex09}

Sketch the projective spectrum associated with the union of coordinate planes

$$
\operatorname{Spek}(K[X,Y,Z]/(XYZ))
$$

with its standard grading.

<!-- upstream_entity: Projektive Ebene/Zwei Geraden/Schnittpunkt/1/Aufgabe -->

## Exercise 12.10 ★ {#br-bgk-2019-w12-ex10}

Determine the intersection point of the two lines

$$
L=V_+(6X-8Y+3Z)
$$

and

$$
M=V_+(2X+9Y-5Z)
$$

in the projective plane.

> **Editorial note - base field.** The source solution uses division by $70$, so its displayed affine coordinates assume a field of characteristic different from $2$, $5$, and $7$. Over those exceptional characteristics, the same exercise can be treated in homogeneous coordinates without that division.

<!-- upstream_entity: Projektive Ebene/Zwei verschiedene Punkte/Definieren projektive Gerade/Aufgabe -->

## Exercise 12.11 {#br-bgk-2019-w12-ex11}

Prove that two distinct points $P$ and $Q$ in the projective plane uniquely determine a projective line containing both. How is its equation computed from the coordinates of the two points?

> **Editorial note - rational points.** Here “points” means $K$-rational points of $\mathbb P_K^2$, as required by the coordinate formulation. The assertion is not about arbitrary points of the underlying scheme.

<!-- upstream_entity: Projektiver Raum/Grundring/Globale Schnitte/Aufgabe -->

## Exercise 12.12 {#br-bgk-2019-w12-ex12}

Prove that the ring of global sections of projective space is the base ring:

$$
\Gamma(\mathbb P_R^n,\mathcal O_{\mathbb P_R^n})=R.
$$

<!-- upstream_entity: Projektive Gerade/Verklebung/Proj/Aufgabe -->

## Exercise 12.13 {#br-bgk-2019-w12-ex13}

Prove that the projective line $\mathbb P_K^1$ constructed by gluing in Example 10.7 agrees with the projective line in the sense of Example 12.10, namely

$$
\operatorname{Proj}(K[X,Y]).
$$

<!-- upstream_entity: Projektiver Raum/Zariski Topologie/Einschränkung auf affinen Raum/Aufgabe -->

## Exercise 12.14 {#br-bgk-2019-w12-ex14}

Let $L$ be a homogeneous linear form in $K[X_0,\ldots,X_n]$, and let

$$
D_+(L)\cong\mathbb A_K^n\subseteq\mathbb P_K^n.
$$

Prove that the Zariski topology on projective space induces the Zariski topology on this affine space.

<!-- upstream_entity: Projektiver Raum/Für jeden Punkt affine Umgebung, wo Nullpunkt/Aufgabe -->

## Exercise 12.15 {#br-bgk-2019-w12-ex15}

Let

$$
P=(a_0,\ldots,a_n)\in\mathbb P_K^n.
$$

Prove that there is an affine open neighbourhood

$$
U\cong\mathbb A_K^n\subset\mathbb P_K^n
$$

such that $P$ corresponds to the origin in this affine space.

<!-- upstream_entity: Projektiver Raum/Übergang zwischen affinen Standardmengen/Aufgabe -->

## Exercise 12.16 {#br-bgk-2019-w12-ex16}

Let $\mathbb P_K^n$ be projective $n$-space over a field $K$, and let

$$
D_+(X_i)\cong\mathbb A_K^n,
\qquad
D_+(X_j)\cong\mathbb A_K^n
$$

be two affine open subsets of $\mathbb P_K^n$. Describe the transition map from $D_+(X_i)$ to $D_+(X_j)$, which is not defined everywhere.

<!-- upstream_entity: Projektive Abbildung/Morphismus durch homogenen Polynome vom gleichen Grad/Auf offener Menge/Aufgabe -->

## Exercise 12.17 {#br-bgk-2019-w12-ex17}

Suppose that $m+1$ homogeneous polynomials

$$
F_0,\ldots,F_m
$$

in $n+1$ variables are given, all of the same degree $d$. Prove that there is an open subset $U\subseteq\mathbb P_K^n$ on which these polynomials define a morphism

$$
\mathbb P_K^n\supseteq U\longrightarrow\mathbb P_K^m.
$$

<!-- upstream_entity: Standard-graduierter Ring/Einheit im Grad 1/Homogenes Ideal/n-te Stufe/Aufgabe -->

## Exercise 12.18 {#br-bgk-2019-w12-ex18}

Let $S$ be a $\mathbb Z$-graded ring with a homogeneous unit of degree one, and let $\mathfrak a\subseteq S$ be a homogeneous ideal. For $n\in\mathbb Z$, prove the equality of $(S/\mathfrak a)_0$-modules

$$
(S/\mathfrak a)_n
=(S/\mathfrak a)_0\otimes_{S_0}S_n.
$$

<!-- upstream_entity: Standard-graduierter Ring/Homogenes Ideal/Nenneraufnahme/n-te Stufe/Aufgabe -->

## Exercise 12.19 {#br-bgk-2019-w12-ex19}

Let $R$ be a standard-graded ring, $\mathfrak a\subseteq R$ a homogeneous ideal, and $f\in R$ a homogeneous element of degree $1$. For $n\in\mathbb Z$, prove the equality of $(R_f/\mathfrak a_f)_0$-modules

$$
((R/\mathfrak a)_f)_n
=(R_f/\mathfrak a_f)_n
=(R_f/\mathfrak a_f)_0\otimes_{(R_f)_0}(R_f)_n.
$$
