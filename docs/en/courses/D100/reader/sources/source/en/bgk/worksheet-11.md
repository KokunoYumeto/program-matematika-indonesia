---
title: "Worksheet 11 - Irreducible Spaces and Noetherian Schemes"
stable_id: br-bgk-2019-w11
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Marymay0609"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 11"
upstream_pageid: 110218
upstream_revid: 612137
upstream_timestamp: "2020-01-24T13:09:14Z"
upstream_mediawiki_sha1: 0d36ef9ba0541058aa2bb8cc7bcfa015382e3106
source_url: "https://de.wikiversity.org/w/index.php?oldid=612137"
authority_manifest: authority/wikiversity-bgk/unit-11/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: c55c715d0a1bd3ef5b13ac96ccf38f9b5c261e87124c6da5ccc5984cb61deb09
worksheet_xml: authority/wikiversity-bgk/unit-11/worksheet-11.xml
worksheet_xml_sha256: 9d73692e385b17a84901ed9e15baeeb0c9793929c5a8263777f69554b6ca6de5
worksheet_expanded_tex: authority/wikiversity-bgk/unit-11/worksheet-11-expanded.tex
worksheet_expanded_tex_sha256: 3361e7036c8432a1a14adcf8ac3fb859ddf999e3b5f44007caefa33e8e320a4b
official_pdf: authority/artifacts/bgk-worksheet-11-official.pdf
official_pdf_sha256: 83ef811e6047d4e23643881048dc614d58d7e8e328b55173a2e67fd09a65e6cd
ordered_exercise_map: authority/wikiversity-bgk/unit-11/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 44c6b2f4a86976163360cf7d0b0b60e39334ec54336e8483249431039365c161
exercise_count: 19
public_solution_count: 3
public_solution_numbers: "9, 13, 14"
media_credits: source/id-ID/media-credits-bgk-unit-11.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 11: Irreducible Spaces and Noetherian Schemes {#br-bgk-2019-w11}

Asterisks mark exactly the three exercises with frozen public solutions: Exercises 11.9, 11.13, and 11.14. The other sixteen exercises have negative candidate results; this edition creates no new solutions.

<!-- upstream_entity: Irreduzibler Raum/Offene Teilmenge/Dicht/Aufgabe -->

## Exercise 11.1 {#br-bgk-2019-w11-ex01}

Prove that, in an irreducible topological space $X$, every nonempty open subset $U\subseteq X$ is dense.

<!-- upstream_entity: Metrischer Raum/Irreduzible Teilmengen/Aufgabe -->

## Exercise 11.2 {#br-bgk-2019-w11-ex02}

Prove that a metric space $X$ can be irreducible only if it consists of a single point.

<!-- upstream_entity: Topologischer Raum/Irreduzible Teilmenge/Abschluss/Aufgabe -->

## Exercise 11.3 {#br-bgk-2019-w11-ex03}

Let $X$ be a topological space and $Y\subseteq X$ a subset with the induced topology. Prove that $Y$ is irreducible if and only if its closure $\overline Y$ is irreducible.

A topological space is said to satisfy the *$T_0$ separation property* if, for any two points $x\ne y$, there is an open set $U$ with $x\in U$ and $y\notin U$, or an open set $V$ with $x\notin V$ and $y\in V$.

A topological space is said to satisfy the *$T_1$ separation property* if every point $x\in X$ is closed.

<!-- upstream_entity: Schema/T0/Aufgabe -->

## Exercise 11.4 {#br-bgk-2019-w11-ex04}

Prove that a scheme satisfies the $T_0$ separation property.

<!-- upstream_entity: Affines Schema/T1/Hausdorffsch/Nulldimensional/Aufgabe -->

## Exercise 11.5 {#br-bgk-2019-w11-ex05}

Prove that, for an affine scheme $X=\operatorname{Spek}(R)$, the following properties are equivalent.

1. Every prime ideal of $R$ is maximal.
2. Every point of $X$ is closed.
3. $X$ is a Hausdorff space.

<!-- upstream_entity: Affines Schema/Nulldimensional/Nicht diskret/Aufgabe -->

## Exercise 11.6 {#br-bgk-2019-w11-ex06}

Give an example of a zero-dimensional affine scheme $X=\operatorname{Spek}(R)$ that is not discrete.

<!-- upstream_entity: Topologischer Raum/Irreduzible Teilmenge/Generischer Punkt/Abschluss/Aufgabe -->

## Exercise 11.7 {#br-bgk-2019-w11-ex07}

Let $Y\subseteq X$ be an irreducible subset of a topological space $X$, and let $\eta\in Y$. Prove that $\eta$ is a generic point of $Y$ if and only if

$$
\overline{\{\eta\}}=Y.
$$

> **Editorial note - closedness of the subset.** The source omits the hypothesis that $Y$ is closed. With closure taken in $X$, include that hypothesis, as in Definition 11.4. For an arbitrary irreducible subset, the corresponding statement uses closure in the subspace $Y$ instead.

<!-- upstream_entity: Affines Schema/Irreduzible Teilmenge/Generischer Punkt/Aufgabe -->

## Exercise 11.8 {#br-bgk-2019-w11-ex08}

Let $X=\operatorname{Spek}(R)$ be the spectrum of a commutative ring $R$, and let

$$
Y=V(\mathfrak p)\subseteq X
$$

be the closed subset associated with a prime ideal $\mathfrak p$. Prove that $\mathfrak p$ is the generic point of $V(\mathfrak p)$.

<!-- upstream_entity: Differenzierbare Mannigfaltigkeit/Kette von abgeschlossenen Untermannigfaltigkeiten/Aufgabe -->

## Exercise 11.9* {#br-bgk-2019-w11-ex09}

Let $M\ne\varnothing$ be a differentiable manifold of dimension $n$. Prove that there is a chain of closed submanifolds

$$
M_0\subseteq M_1\subseteq M_2\subseteq\cdots
\subseteq M_{n-1}\subseteq M_n=M
$$

such that the closed submanifold $M_i$ has dimension $i$.

<!-- upstream_entity: Noetherscher Raum/Unterraum/Aufgabe -->

## Exercise 11.10 {#br-bgk-2019-w11-ex10}

Let $X$ be a noetherian topological space. Prove that every subset $Y\subseteq X$ with the induced topology is also noetherian.

<!-- upstream_entity: Noetherscher Raum/Jede Teilmenge quasikompakt/Aufgabe -->

## Exercise 11.11 {#br-bgk-2019-w11-ex11}

Let $X$ be a noetherian topological space. Prove that every subset $Y\subseteq X$ with the induced topology is quasicompact.

<!-- upstream_entity: Reelle Zahlen/Kein noetherscher Raum/Aufgabe -->

## Exercise 11.12 {#br-bgk-2019-w11-ex12}

Prove that the real numbers $\mathbb R$ with the metric topology do not form a noetherian topological space.

<!-- upstream_entity: Kommutativer Ring/Ideal/Endlich erzeugt/Überdeckungstest/Aufgabe -->

## Exercise 11.13* {#br-bgk-2019-w11-ex13}

Let $R$ be a commutative ring and

$$
\operatorname{Spek}(R)=\bigcup_{i\in I}D(f_i),
\qquad f_i\in R.
$$

Let $\mathfrak a$ be an ideal of $R$ such that each extended ideal $\mathfrak aR_{f_i}$ is finitely generated. Prove that $\mathfrak a$ is finitely generated.

<!-- upstream_entity: Kommutativer Ring/Spektrum/Noethersches Schema/Aufgabe -->

## Exercise 11.14* {#br-bgk-2019-w11-ex14}

Let $R$ be a commutative ring and $X=\operatorname{Spek}(R)$ the associated affine scheme. Prove that $X$ is a noetherian scheme if and only if $R$ is a noetherian ring.

<!-- upstream_entity: Noetherscher Ring/Minimale Primideale/Endlich/Fakt/Beweis/Aufgabe -->

## Exercise 11.15 {#br-bgk-2019-w11-ex15}

Prove that a noetherian commutative ring has only finitely many minimal prime ideals.

<!-- upstream_entity: Nicht-noethersche Ringe/Beispiel/Reduktion ist Körper/Aufgabe -->

## Exercise 11.16 {#br-bgk-2019-w11-ex16}

Give an example of a non-noetherian ring whose reduction is a field.

Let $R$ be a commutative ring. A multiplicative system $F\subseteq R$ is called an *ultrafilter* if $0\notin F$ and $F$ is maximal with this property.

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikatives System/Maximal ohne 1/Komplement ist minimales Primideal/Aufgabe -->

## Exercise 11.17 {#br-bgk-2019-w11-ex17}

Let $R$ be a commutative ring and $F\subset R$ an ultrafilter. Prove that the complement of $F$ is a minimal prime ideal of $R$.

<!-- upstream_entity: Beringter Raum/Reduziert/Lokale Eigenschaft/Fakt/Beweis/Aufgabe -->

## Exercise 11.18 {#br-bgk-2019-w11-ex18}

Let $(X,\mathcal O_X)$ be a ringed space. Prove that the following assertions are equivalent.

1. $(X,\mathcal O_X)$ is a reduced ringed space.
2. For every point $P\in X$, the stalk $\mathcal O_{X,P}$ is reduced.

<!-- upstream_entity: Schema/Integrität/Keine lokale Eigenschaft/Aufgabe -->

## Exercise 11.19 {#br-bgk-2019-w11-ex19}

Prove that integrality of a scheme is not, in general, a local property.
