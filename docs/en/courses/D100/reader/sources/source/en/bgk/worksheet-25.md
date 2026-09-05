---
title: "Worksheet 25 - Sheaf Cohomology"
stable_id: br-bgk-2019-w25
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 25"
upstream_pageid: 110234
upstream_revid: 613127
upstream_timestamp: "2020-01-27T15:28:07Z"
upstream_mediawiki_sha1: 45f8aa55eae6ae2447eb9783f5329b25eeb50519
source_url: "https://de.wikiversity.org/w/index.php?oldid=613127"
authority_manifest: authority/wikiversity-bgk/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f454cb2f8ada795015dcf78d4ad56a54107d9773705b7113a1ef1600b341e26d
authority_manifest_status: "Terminal authority freeze complete; all 33 file records have been recomputed without discrepancies."
worksheet_xml: authority/wikiversity-bgk/unit-25/worksheet-25.xml
worksheet_xml_sha256: 37a26281d72997f22d841319e204ec793d6eac8cf4b387392f4d344c9e8aaa9f
worksheet_expanded_tex: authority/wikiversity-bgk/unit-25/worksheet-25-expanded.tex
worksheet_expanded_tex_sha256: 2ccc656c99f53228b9a5cc564a2f2ac5098e37a3c0c729654142e577c84817f7
official_pdf: authority/artifacts/bgk-worksheet-25-official.pdf
official_pdf_sha256: 8909d39c3a3d0fe800a41f63aedcade07de8f558e2b9c6f053cf51cd724e0c40
official_pdf_source_bytes: 56663
official_pdf_source_sha1: e902ef47db2e116d1fde03cca818c4e8132decf8
official_pdf_metadata: authority/wikiversity-bgk/unit-25/official-pdfs-api.json
official_pdf_metadata_sha256: f49c28f3f600974f8cd7bcf29377dbad5429e789769d0953fc28075adce5c767
authority_precedence: "The frozen semantic Wikiversity revisions govern the text; the official PDFs are retained as historical witnesses without overriding newer revisions."
ordered_exercise_map: authority/wikiversity-bgk/unit-25/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 03b696f0c666352947f89c01a2c1ca0c1c5fb38bae0af77693cf21021b6b381b
candidate_evidence: authority/wikiversity-bgk/unit-25/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 37ce99c2c415ef9bc13592e6e9d0537322c4fcf0b83b3112f8b6d1796828c939
exercise_count: 13
public_solution_count: 1
public_solution_numbers: "1"
media_credits: source/id-ID/media-credits-bgk-unit-25.md
media_credits_sha256: c0367344876a648ab7141eb306e6a9a02f14c47b3b57a03012073940f4297037
rights_ledger: authority/RIGHTS-bgk-unit-25.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-25.json
asset_closure_sha256: b897e839fc6999e5c149e1bf065a634b96246b563860d46f0a16ddb82ae1c9d5
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDFs are authority witnesses, not the edition text; the Commons CC BY-SA 4.0 metadata and embedded CC-by-sa 3.0 notices are preserved without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 25: Sheaf Cohomology {#br-bgk-2019-w25}

The star marks exactly one exercise with a frozen public solution:
Exercise 25.1. The other twelve exercises have negative candidate results;
this edition does not invent new solutions.

<!-- upstream_entity: Intervall/Intervallüberdeckung/2/Stetige Funktion/Differenz/Aufgabe -->

## Exercise 25.1 ★ {#br-bgk-2019-w25-ex01}

Let $I\subseteq\mathbb R$ be a real interval and $I=U\cup V$
a cover by intervals open in $I$. Show that a continuous function

$$
f:U\cap V\longrightarrow\mathbb R
$$

can be written as

$$
f=g\big|_{U\cap V}-h\big|_{U\cap V}
$$

with continuous functions $g:U\to\mathbb R$ and $g:V\to\mathbb R$.

> **Editorial note - function names in the source.** The last line of the
> printed source names both functions $g$, whereas the formula uses $g$
> and $h$. This edition preserves the printed statement and does not
> silently change the name of the second function.

<!-- upstream_entity: Intervall/Intervallüberdeckung/2/Funktionen modulo stetige Funktionen/Global surjektiv/Aufgabe -->

## Exercise 25.2 {#br-bgk-2019-w25-ex02}

Let $I\subseteq\mathbb R$ be a real interval. On $I$, consider the
short exact sequence of sheaves

$$
0\longrightarrow C^0(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)/C^0(-,\mathbb R)
\longrightarrow 0.
$$

Let $I=U\cup V$ be a cover by intervals open in $I$.
Suppose we are given a global section of the quotient sheaf
$\operatorname{Abb}(-,\mathbb R)/C^0(-,\mathbb R)$ represented by sections
$s\in\operatorname{Abb}(U,\mathbb R)$ and
$t\in\operatorname{Abb}(V,\mathbb R)$. Show that this section is represented
by a map $r\in\operatorname{Abb}(I,\mathbb R)$.

<!-- upstream_entity: Abgeschlossenes Intervall/Funktionen modulo stetige Funktionen/Global surjektiv/Aufgabe -->

## Exercise 25.3 {#br-bgk-2019-w25-ex03}

Let $I\subseteq\mathbb R$ be a closed real interval.
On $I$, consider the short exact sequence of sheaves

$$
0\longrightarrow C^0(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)/C^0(-,\mathbb R)
\longrightarrow 0.
$$

Show that

$$
\operatorname{Abb}(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)/C^0(-,\mathbb R)
$$

is surjective.

<!-- upstream_entity: Abgeschlossenes Intervall/Stetige Funktionen/Garbe/1. Kohomologie/Aufgabe -->

## Exercise 25.4 {#br-bgk-2019-w25-ex04}

Let $I\subseteq\mathbb R$ be a closed real interval. Show that

$$
H^1(I,C^0(-,\mathbb R))=0.
$$

<!-- upstream_entity: Kreis/Diskrete Gruppe/Lokal konstante Garbe/Überdeckung/Erste Garbenkohomologie/Aufgabe -->

## Exercise 25.5 {#br-bgk-2019-w25-ex05}

Let $G$ be a discrete topological abelian group with at least two elements
$a\ne b$. On $S^1$, consider the exact sequence of sheaves

$$
0\longrightarrow G\longrightarrow\operatorname{Abb}(-,G)
\longrightarrow\operatorname{Abb}(-,G)/G\longrightarrow 0,
$$

where $G$ here denotes the sheaf of locally constant functions with values
in $G$, namely $C^0(-,G)$. Let $S^1=U\cup V$ be an open cover
of the unit circle by two overlapping arcs such that $U\cap V$
consists of two disjoint arcs, $A$ and $B$.

> **Edition note — group hypothesis.** The source says only “group”, but its
> quotient sheaf, exact sequence, and group $H^1$ use the abelian category of
> sheaves of abelian groups. Accordingly `G` is taken to be abelian here;
> no non-abelian cohomology assertion is intended.

Let

$$
h\in\Gamma\bigl(S^1,\operatorname{Abb}(-,G)/G\bigr)
$$

be a section represented on $V$ by the zero map
$0\in\operatorname{Abb}(V,G)$ and on $U$ by a map
$g\in\operatorname{Abb}(U,G)$ that has the constant value $a$ on $A$
and the constant value $b$ on $B$. Show that this section cannot be
represented by an element of $\operatorname{Abb}(S^1,G)$, and consequently

$$
H^1(S^1,G)\ne 0.
$$

<!-- upstream_entity: Topologischer Raum/Komplexe Exponentialsequenz/Stetig/Beispiel/Erste Garbenkohomologie/Aufgabe -->

## Exercise 25.6 {#br-bgk-2019-w25-ex06}

Using Example 6.6, show that

$$
H^1(\mathbb C^\times,\mathbb Z)\ne 0.
$$

Here $\mathbb Z$ denotes the sheaf of continuous functions with values
in the discrete topological group $\mathbb Z$.

<!-- upstream_entity: Topologischer Raum/Lokal/Keine Garbenkohomologie/Aufgabe -->

## Exercise 25.7 {#br-bgk-2019-w25-ex07}

Let $X$ be a topological space with a point $x\in X$ whose only
open neighbourhood is the entire space.

1. Show that the spectrum of a local ring has this property.
2. Show that every sheaf of abelian groups $\mathcal G$ on $X$
   has no non-trivial cohomology.
3. Show that not every sheaf on $\operatorname{Spek}(R)$ for a local
   ring $R$ is flasque.

<!-- upstream_entity: Integritätsbereich/Idealgarbe/Erste Kohomologie/Aufgabe -->

## Exercise 25.8 {#br-bgk-2019-w25-ex08}

Let $R$ be an integral domain and $I$ an ideal of $R$, with associated
quasi-coherent ideal sheaf $\widetilde I$ on $\operatorname{Spek}(R)$.
Using Lemma 25.7, show that

$$
H^1(\operatorname{Spek}(R),\widetilde I)=0.
$$

<!-- upstream_entity: Punktierte Ebene/Koszul/Garbeninterpretation/Aufgabe -->

## Exercise 25.9 {#br-bgk-2019-w25-ex09}

Let $R=K[X,Y]$ be the polynomial ring over a field $K$, with maximal
ideal $\mathfrak m=(X,Y)$. Consider the short exact sequence of $R$-modules

$$
0\longrightarrow R
\xrightarrow{\ e\mapsto(Y,-X)\ }R^2
\xrightarrow{\ e_1\mapsto X,\ e_2\mapsto Y\ }\mathfrak m
\longrightarrow 0.
$$

1. Write down the short exact sequence of sheaves of the associated
   quasi-coherent modules on $\mathbb A_K^2=\operatorname{Spek}(R)$.
2. Show that evaluating the sheaf sequence from (1) on
   $U=D(X,Y)\subset\mathbb A_K^2$ does not give an exact sequence.
3. What is the image of

   $$
   1\in R=\Gamma(U,\mathcal O_X)=\Gamma(U,\widetilde{\mathfrak m})
   $$

   in $H^1(U,\mathcal O_X)$ under the connecting homomorphism?

<!-- upstream_entity: Schema/Integer/Einheitengarbe/Funktionenkörpergruppe/Erste Kohomologie/Fakt/Beweis/Aufgabe -->

## Exercise 25.10 {#br-bgk-2019-w25-ex10}

Let $(X,\mathcal O_X)$ be an integral scheme with function field $K$.
Let $\mathcal O_X^\times$ be the sheaf of units on $X$, and let
$\mathcal U$ be the constant sheaf with value $K^\times$. Show that

$$
H^1(X,\mathcal O_X^\times)
=\Gamma(X,\mathcal U/\mathcal O_X^\times)
/\operatorname{im}\bigl(K^\times\longrightarrow
\Gamma(X,\mathcal U/\mathcal O_X^\times)\bigr).
$$

<!-- upstream_entity: Faktorieller Integritätsbereich/Einheitengarbe/Erste Kohomologie/Aufgabe -->

## Exercise 25.11 {#br-bgk-2019-w25-ex11}

Let $R$ be a unique factorisation domain. Show that

$$
H^1(\operatorname{Spek}(R),\mathcal O_X^\times)=\{1\}.
$$

<!-- upstream_entity: Ganzheitsring/Wurzel -5/Einheitengarbe/Erste Kohomologie nicht trivial/Aufgabe -->

## Exercise 25.12 {#br-bgk-2019-w25-ex12}

Consider the quadratic number ring

$$
R=A_{-5}=\mathbb Z[\sqrt{-5}]
\cong\mathbb Z[T]/(T^2+5).
$$

Using Example 14.6, show that

$$
H^1(\operatorname{Spek}(R),
\mathcal O_{\operatorname{Spek}(R)}^\times)\ne\{1\}.
$$

<!-- upstream_entity: Stetige Abbildung/Vorgeschobene Garbe/Linksexakt/Aufgabe -->

## Exercise 25.13 {#br-bgk-2019-w25-ex13}

Let $f:X\to Y$ be a continuous map between topological spaces.
Show that pushforward

$$
\mathcal G\longmapsto f_*\mathcal G
$$

is a left exact covariant functor from the category of sheaves of abelian
groups on $X$ to the category of sheaves of abelian groups on $Y$.

**Remark.** The associated right derived functors are called
*higher direct image sheaves*.
