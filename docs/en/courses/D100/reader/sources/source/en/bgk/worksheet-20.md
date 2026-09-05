---
title: "Worksheet 20 - The Picard Group"
stable_id: br-bgk-2019-w20
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 20"
upstream_pageid: 110229
upstream_revid: 1069949
upstream_timestamp: "2026-02-06T08:22:42Z"
upstream_mediawiki_sha1: deebce0847dc537e97deb2cccbd5eb87000a92c1
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069949"
authority_manifest: authority/wikiversity-bgk/unit-20/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a59a4536a441cfdbcd579525119112156fcc5dc8041ba97d4834e18db55cd658
authority_manifest_status: "Complete terminal authority freeze; all 32 file records have been recomputed without mismatches."
worksheet_xml: authority/wikiversity-bgk/unit-20/worksheet-20.xml
worksheet_xml_sha256: 577758f4198bd4095caa4b44f18ceb55d037f80f7378a9ec1eec89630c6a26aa
worksheet_expanded_tex: authority/wikiversity-bgk/unit-20/worksheet-20-expanded.tex
worksheet_expanded_tex_sha256: 02ea49af16ac9adb623fae14e9af088c7349f6c2b903d3dd4e79b24dd4d7c68d
official_pdf: authority/artifacts/bgk-worksheet-20-official.pdf
official_pdf_sha256: e477498aa6c1b82e4ae1ec37e9f2c814db79734f04583b0da77ca00cc2423daf
official_pdf_status: "Local official PDF witness; 53,758 bytes, 5 pages, and upload SHA-1 a826ee89acd343a57ccd7102d7b5eadc9c2569b9 have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-20/official-pdfs-api.json
official_pdf_source_bytes: 53758
official_pdf_source_sha1: a826ee89acd343a57ccd7102d7b5eadc9c2569b9
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
ordered_exercise_map: authority/wikiversity-bgk/unit-20/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 3c424a95222b09ffe0c26d0f5fb18d3408922fa95487ef176cf310bb5c17582a
exercise_count: 13
public_solution_count: 0
media_credits: source/id-ID/media-credits-bgk-unit-20.md
rights_ledger: authority/RIGHTS-bgk-unit-20.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-20.json
asset_closure_sha256: 2cdfc5e32e86b5f704f1f00f6d5690166967464fbe2c6474086e28e470463b40
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 20: The Picard Group {#br-bgk-2019-w20}

None of the 13 exercises has a public solution at the frozen revision boundary. No solution stars are therefore used, and this edition does not invent new solutions.

<!-- upstream_entity: Schemamorphismus/Picardgruppe/Funktoriell/Aufgabe -->

## Exercise 20.1 {#br-bgk-2019-w20-ex01}

Let

$$
\varphi:X\longrightarrow Y
$$

be a scheme morphism. Prove that the assignment

$$
\mathcal L\longmapsto\varphi^*\mathcal L
$$

defines a group homomorphism

$$
\operatorname{Pic}(Y)\longrightarrow\operatorname{Pic}(X).
$$

For the next two exercises, take Remark 20.3 into account.

<!-- upstream_entity: Schemamorphismus/Picardgruppe/Funktoriell/Cech-Beschreibung/Aufgabe -->

## Exercise 20.2 {#br-bgk-2019-w20-ex02}

Let

$$
\varphi:X\longrightarrow Y
$$

be a scheme morphism. Prove that the group homomorphism

$$
\operatorname{Pic}(Y)\longrightarrow\operatorname{Pic}(X),
\qquad
\mathcal L\longmapsto\varphi^*\mathcal L,
$$

can be described using the cocycle description in Remark 20.2 as follows. The cocycle

$$
r_{ij}\in\left(\Gamma(V_i\cap V_j,\mathcal O_Y)\right)^\times,
\qquad i<j,
$$

for an open cover

$$
Y=\bigcup_{i\in I}V_i
$$

is sent to the cocycle

$$
\theta_{ij}(r_{ij})
\in
\left(\Gamma\!\left(
\varphi^{-1}(V_i)\cap\varphi^{-1}(V_j),\mathcal O_X
\right)\right)^\times,
\qquad i<j,
$$

with respect to the cover

$$
X=\bigcup_{i\in I}\varphi^{-1}(V_i),
$$

where

$$
\theta_{ij}:\Gamma(V_i\cap V_j,\mathcal O_Y)
\longrightarrow
\Gamma\!\left(\varphi^{-1}(V_i\cap V_j),\mathcal O_X\right)
$$

denotes the associated ring homomorphism.

<!-- upstream_entity: Projektives Spektrum/Getwistete Strukturgarbe/Cech-Beschreibung/Kegelabbildung/Aufgabe -->

## Exercise 20.3 {#br-bgk-2019-w20-ex03}

Let

$$
A=K[X_1,\ldots,X_n]/\mathfrak a
$$

be a standard-graded ring, with the open cover

$$
U=\operatorname{Spek}(A)\setminus\{A_+\}
=\bigcup_{i=1}^nD(X_i)
\subseteq\operatorname{Spek}(A)=X
$$

of the punctured spectrum and the open cover

$$
Y=\operatorname{Proj}(A)
=\bigcup_{i=1}^nD_+(X_i)
$$

of the associated projective spectrum. Let $\ell\in\mathbb Z$. Prove the following statements.

1. The family of units

   $$
   X_i^\ell\in\left(\Gamma(D(X_i),\mathcal O_X)\right)^\times,
   \qquad i=1,\ldots,n,
   $$

   defines the cocycle

   $$
   X_j^\ell X_i^{-\ell}
   \in\left(\Gamma(D(X_iX_j),\mathcal O_X)\right)^\times,
   \qquad i<j,
   $$

   representing the trivial invertible sheaf on $U$.

2. The cocycle from part (1) can be regarded as a cocycle on the projective spectrum $Y$.

3. The invertible sheaf on $Y$ determined by the cocycle from part (2) is isomorphic to the twisted structure sheaf $\mathcal O_Y(\ell)$, or to $\mathcal O_Y(-\ell)$; there is a choice of sign here.

4. The pullback of a twisted structure sheaf under the cone map $U\to Y$ is trivial.

> **Editorial note — the ring symbol in the source.** The source defines $A=K[X_1,\ldots,X_n]/\mathfrak a$ but prints $\operatorname{Spek}(R)=X$ in the cover of the punctured spectrum. This edition uses $A$, the ring defined in the exercise.

<!-- upstream_entity: Faktorieller Integritätsbereich/Exponent/Lokalisierung/Fakt/Beweis/Aufgabe -->

## Exercise 20.4 {#br-bgk-2019-w20-ex04}

Let $R$ be a unique factorisation domain. Prove the following statements.

1. For $f\in R$, $f\ne0$, we have

   $$
   (f)R_{(p)}=(p^s)
   $$

   if and only if $p$ occurs with exponent $s$ in the prime factorisation of $f$.

2. Two principal ideals $(f)$ and $(g)$ agree if and only if, for every prime element $p$, the ideals

   $$
   (f)R_{(p)}
   \quad\text{and}\quad
   (g)R_{(p)}
   $$

   agree in the localisation $R_{(p)}$.

The following exercise prepares for Lemma 20.13.

<!-- upstream_entity: Faktorieller Integritätsbereich/D(f,g)/Picardgruppe/Aufgabe -->

## Exercise 20.5 {#br-bgk-2019-w20-ex05}

Let $R$ be a unique factorisation domain and let $f,g\in R$. Using Remark 20.2, prove that the Picard group of

$$
D(f,g)\subseteq\operatorname{Spek}(R)
$$

is trivial.

<!-- upstream_entity: Integritätsbereich/Lokal faktoriell/Offene Teilmenge/Picardgruppe/Ausdehnbarkeit/Kodimension/Aufgabe -->

## Exercise 20.6 {#br-bgk-2019-w20-ex06}

Let $R$ be a Noetherian integral domain such that all localisations $R_{\mathfrak p}$ are factorial. Let $U\subseteq\operatorname{Spek}(R)$ be an open subset and let $\mathfrak p\notin U$ be a point of codimension $\geq2$, so the prime ideal $\mathfrak p$ has height $\geq2$. Prove that an invertible sheaf $\mathcal L$ on $U$ has a unique extension to an open set $U'$ containing $U$ and $\mathfrak p$.

<!-- upstream_entity: Ganzheitsring/Wurzel -5/Lokal faktoriell/Mehrere Ausdehnungen/Aufgabe -->

## Exercise 20.7 {#br-bgk-2019-w20-ex07}

Consider the quadratic number ring

$$
R=\mathbb Z[\sqrt{-5}]
$$

with open subset $D(2)\subseteq\operatorname{Spek}(R)$. Prove that the structure sheaf on $D(2)$ can be extended in more than one way to an invertible sheaf on $\operatorname{Spek}(R)$.

<!-- upstream_entity: An-Singularität/Punktiert/Lokal/Picardgruppe/Aufgabe -->

## Exercise 20.8 {#br-bgk-2019-w20-ex08}

Prove that the Picard group of the punctured spectrum

$$
U=D(X,Y,Z)
\subseteq
\operatorname{Spek}\!\left(
\left(K[X,Y,Z]/(XY-Z^n)\right)_{(X,Y,Z)}
\right)
$$

of the local ring

$$
\left(K[X,Y,Z]/(XY-Z^n)\right)_{(X,Y,Z)}
$$

is $\mathbb Z/(n)$; compare Example 20.15.

> **Editorial note — the scope of localisation in the source formula.** In both displays the source places the subscript $(X,Y,Z)$ directly on $(XY-Z^n)$ within the quotient. Since the text calls this a local ring and asks for its punctured spectrum, this edition places the localisation on the quotient ring itself.

<!-- upstream_entity: An-Singularität/Punktiert/Invertierbare Garben/Nicht ausdehnbar/Aufgabe -->

## Exercise 20.9 {#br-bgk-2019-w20-ex09}

Prove that on the punctured spectrum

$$
U=D(X,Y,Z)
\subseteq
\operatorname{Spek}\!\left(K[X,Y,Z]/(XY-Z^n)\right),
$$

for $n\geq2$, there are invertible sheaves that cannot be extended to invertible sheaves on

$$
\operatorname{Spek}\!\left(K[X,Y,Z]/(XY-Z^n)\right).
$$

<!-- upstream_entity: An-Singularität/Punktiert/Invertierbare Garben/Kohärente Ausdehnung/Aufgabe -->

## Exercise 20.10 {#br-bgk-2019-w20-ex10}

Prove that the invertible sheaves on the punctured spectrum

$$
U=D(X,Y,Z)
\subseteq
\operatorname{Spek}\!\left(K[X,Y,Z]/(XY-Z^n)\right)
$$

are restrictions of the coherent ideal sheaves associated with the ideals

$$
(X,Z^i),
\qquad i=0,\ldots,n-1,
$$

in $K[X,Y,Z]/(XY-Z^n)$.

<!-- upstream_entity: An-Singularität/Punktiert/Invertierbare Garben/Ausdehnung als Gruppenschema/Aufgabe -->

## Exercise 20.11 {#br-bgk-2019-w20-ex11}

Let

$$
R=K[X,Y,Z]/(XY-Z^n).
$$

For $i=0,1,\ldots,n-1$, consider the $R$-algebras

$$
A_i=R[S,T]/(SX+TZ^i)
$$

and the associated spectrum maps

$$
\pi_i:\operatorname{Spek}(A_i)
\longrightarrow\operatorname{Spek}(R).
$$

Prove that over

$$
U=D(X,Y,Z)
\subseteq
\operatorname{Spek}\!\left(K[X,Y,Z]/(XY-Z^n)\right),
$$

the maps $\pi_i$ are line bundles that are nontrivial for $i\ne0$. Prove also that for $i\ne0$, the scheme $\operatorname{Spek}(A_i)$ is not a line bundle over $\operatorname{Spek}(R)$.

<!-- upstream_entity: Projektiver Raum/D_+(X,Y)/Picardgruppe/Aufgabe -->

## Exercise 20.12 {#br-bgk-2019-w20-ex12}

Let

$$
\mathbb P_K^d
=\operatorname{Proj}(K[X_0,X_1,\ldots,X_d])
$$

be projective space over a field $K$. Prove that the Picard group of the open subset

$$
D_+(X_i,X_j)\subseteq\mathbb P_K^d,
\qquad i\ne j,
$$

is isomorphic to $\mathbb Z$.

<!-- upstream_entity: Projektiver Raum/Picardgruppe/Aufgabe -->

## Exercise 20.13 {#br-bgk-2019-w20-ex13}

Let

$$
\mathbb P_K^d
=\operatorname{Proj}(K[X_0,X_1,\ldots,X_d])
$$

be projective space over a field $K$. Prove that for $d\geq1$, the Picard group of $\mathbb P_K^d$ is isomorphic to $\mathbb Z$.
