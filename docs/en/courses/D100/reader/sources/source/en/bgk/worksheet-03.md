---
title: "Worksheet 3 - Linear Constructions, Presheaves and Stalks"
stable_id: br-bgk-2019-w03
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 3"
upstream_pageid: 109057
upstream_revid: 619301
upstream_timestamp: "2020-02-17T10:29:54Z"
upstream_mediawiki_sha1: a6abf3d53e491ec12c798e96f3dfeec8b84de8c7
source_url: "https://de.wikiversity.org/w/index.php?oldid=619301"
authority_manifest: authority/wikiversity-bgk/unit-03/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 60270cc7ba74a4ed744687ae18c3887eca8a2fff6bce48a819be102d4a619a5a
worksheet_xml: authority/wikiversity-bgk/unit-03/worksheet-03.xml
worksheet_xml_sha256: a34ac6428f6d2074e4bc01f3d3d6064c38625eea36fa4b5c48e18a524e583c15
worksheet_expanded_tex: authority/wikiversity-bgk/unit-03/worksheet-03-expanded.tex
worksheet_expanded_tex_sha256: 08f9268af226916ef212041a50d430ca5fcf71df2c5a57ab5adb36183e2a4b2a
exercise_map: authority/wikiversity-bgk/unit-03/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 5242db043a773e412806fd066ed831fe6ebbdc7d16a35af8070ff1ce7398901f
official_pdf: authority/artifacts/bgk-worksheet-03-official.pdf
official_pdf_sha256: 615cfac501c1397cab86e7a4a000adae7587161b7cf7b2fd28f9bd6df7c7993c
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 18
public_solution_count: 1
---

# Worksheet 3: Linear Constructions, Presheaves and Stalks {#br-bgk-2019-w03}

The Kronecker product of the matrices

$$
A=(a_{ij})_{1\le i\le m,\,1\le j\le n}
$$

and

$$
B=(b_{k\ell})_{1\le k\le p,\,1\le\ell\le r}
$$

is the matrix

$$
(a_{ij}b_{k\ell})_{
  1\le i\le m,\,1\le k\le p;\,
  1\le j\le n,\,1\le\ell\le r}.
$$

<!-- upstream_entity: Kroneckerprodukt/2x2/Berechnung/Aufgabe -->

## Exercise 3.1 {#br-bgk-2019-w03-ex01}

Compute the Kronecker product of the two matrices

$$
\begin{pmatrix}3&-4\\5&-2\end{pmatrix}
\quad\text{and}\quad
\begin{pmatrix}-2&7\\6&3\end{pmatrix}.
$$

<!-- upstream_entity: Matrizen/Tensorprodukt/Kroneckerprodukt/Aufgabe -->

## Exercise 3.2 {#br-bgk-2019-w03-ex02}

Let $K$ be a field, and let

$$
A=(a_{ij})_{1\le i\le m,\,1\le j\le n},
\qquad
B=(b_{k\ell})_{1\le k\le p,\,1\le\ell\le r}
$$

be matrices with associated linear maps

$$
A:K^n\longrightarrow K^m,
\qquad
B:K^r\longrightarrow K^p.
$$

Show that the tensor product of these linear maps, relative to the basis

$$
(e_j\otimes e_\ell)_{1\le j\le n,\,1\le\ell\le r}
$$

of $K^n\otimes K^r$ and the basis

$$
(e_i\otimes e_k)_{1\le i\le m,\,1\le k\le p}
$$

of $K^m\otimes K^p$, is described by the Kronecker product of $A$ and $B$.

<!-- upstream_entity: Möbiusband/Tensorprodukt/Trivial/Aufgabe -->

## Exercise 3.3 {#br-bgk-2019-w03-ex03}

Show that the tensor product of the Möbius strip with itself is a trivial line bundle.

<!-- upstream_entity: Prägarbe/Produkt/Aufgabe -->

## Exercise 3.4 {#br-bgk-2019-w03-ex04}

Let $\mathcal F$ and $\mathcal G$ be presheaves on a topological space $X$. Show that the assignment

$$
U\longmapsto\mathcal F(U)\times\mathcal G(U),
$$

together with the natural product maps as restriction maps, defines a presheaf on $X$.

<!-- upstream_entity: Prägarbe/Produkt/Beliebige Indexmenge/Aufgabe -->

## Exercise 3.5 {#br-bgk-2019-w03-ex05}

Let $I$ be an index set and $(\mathcal F_i)_{i\in I}$ a family of presheaves on a topological space $X$. Show that the assignment

$$
U\longmapsto\prod_{i\in I}\mathcal F_i(U),
$$

together with the natural product maps as restriction maps, defines a presheaf on $X$.

<!-- upstream_entity: Prägarbe/Stetige Abbildungen/Schnitte/Aufgabe -->

## Exercise 3.6 {#br-bgk-2019-w03-ex06}

Interpret Example 3.8 in the framework of Example 3.12.

<!-- upstream_entity: Reelles Vektorbündel/Trivialisierung/Stetige Schnitte/Aufgabe -->

## Exercise 3.7 {#br-bgk-2019-w03-ex07}

Let

$$
p:V\longrightarrow X
$$

be a real vector bundle of rank $m$ on a topological space $X$. Show that for every open set $U\subseteq X$ on which $V$ is trivial, the corresponding presheaf of continuous sections is isomorphic to

$$
C^0(U,\mathbb R)^m.
$$

Explain the sense in which this isomorphism is meant.

<!-- upstream_entity: Topologische Gruppe/Nachweis/Aufgabe -->

## Exercise 3.8 {#br-bgk-2019-w03-ex08}

Show that the groups

$$
(\mathbb R,+),\quad
(\mathbb R\setminus\{0\},\cdot),\quad
(\mathbb C,+),\quad
(\mathbb C\setminus\{0\},\cdot),\quad
(\mathbb R^n,+),
$$

the circle $S^1$ with addition of angles, and the general linear groups $\operatorname{GL}_n(\mathbb R)$ and $\operatorname{GL}_n(\mathbb C)$ are topological groups.

<!-- upstream_entity: Topologische Gruppe/Untergruppe/Unterprägarbe/Aufgabe -->

## Exercise 3.9 {#br-bgk-2019-w03-ex09}

Let $G$ be a topological group and $H\subseteq G$ a subgroup. Show that, on every topological space $X$, the presheaf $C^0(-,H)$ is a subpresheaf of $C^0(-,G)$.

A differentiable manifold $G$ which is also a group, and for which inversion and the group operation are differentiable maps, is called a *real Lie group*.

<!-- upstream_entity: Lie-Gruppe/Nachweis/Aufgabe -->

## Exercise 3.10 {#br-bgk-2019-w03-ex10}

Show that the groups

$$
(\mathbb R,+),\quad
(\mathbb R\setminus\{0\},\cdot),\quad
(\mathbb C,+),\quad
(\mathbb C\setminus\{0\},\cdot),\quad
(\mathbb R^n,+),
$$

the circle $S^1$ with addition of angles, and $\operatorname{GL}_n(\mathbb R)$ and $\operatorname{GL}_n(\mathbb C)$ are Lie groups.

<!-- upstream_entity: Reelle Lie-Gruppe/Tangentialbündel/Trivial/Aufgabe -->

## Exercise 3.11 {#br-bgk-2019-w03-ex11}

Show that the tangent bundle of a Lie group is trivial.

> **Hint.** Show that the tangent space at the identity element can be transported naturally to the other tangent spaces.

<!-- upstream_entity: Gerichtetes System/Kolimes/Universelle Eigenschaft/Mengen und Gruppen/Aufgabe -->

## Exercise 3.12 {#br-bgk-2019-w03-ex12}

Let $I$ be a directed index set and $(M_i)_{i\in I}$ a directed system of sets, with system maps $\varphi_{ij}:M_i\to M_j$. Let $N$ be another set, and suppose that for every $i\in I$ a map

$$
\psi_i:M_i\longrightarrow N
$$

is given such that

$$
\psi_i=\psi_j\circ\varphi_{ij}
$$

for all $i\preccurlyeq j$. Prove the universal property of the colimit: there is a unique map

$$
\psi:\operatorname{colim}_{i\in I}M_i\longrightarrow N
$$

such that

$$
\psi_i=\psi\circ j_i,
$$

where $j_i:M_i\to\operatorname{colim}_{i\in I}M_i$ are the natural maps.

Show also that if $(M_i)$ is a directed system of groups, $N$ is a group, and all the $\psi_i$ are group homomorphisms, then $\psi$ is a group homomorphism.

<!-- upstream_entity: Gerichtetes System/Von kommutativen Gruppen/Kolimes ist kommutative Gruppe/Aufgabe -->

## Exercise 3.13 {#br-bgk-2019-w03-ex13}

Let $I$ be a directed index set and $(G_i)_{i\in I}$ a directed system of commutative groups. Show that its colimit is a commutative group.

<!-- upstream_entity: Kommutative Ringtheorie/Nenneraufnahme/Als gerichtetes System/Aufgabe -->

## Exercise 3.14 {#br-bgk-2019-w03-ex14}

Let $R$ be a commutative ring and $S\subseteq R$ a multiplicative system. Consider the following partial order on $S$: write $f\preccurlyeq g$ if $f$ divides a power of $g$, identifying two elements if this relation holds in both directions.

Show that the commutative rings

$$
R_f,\qquad f\in S,
$$

form a directed system, and that

$$
\operatorname{colim}_{f\in S}R_f=R_S.
$$

<!-- upstream_entity: Mannigfaltigkeit/Tangentialbündel/Halm/Gleich/Aufgabe -->

## Exercise 3.15 {#br-bgk-2019-w03-ex15}

Let $M$ be a differentiable manifold and $P\in M$. Show that the stalk at $P$ of the presheaf of continuous sections of the tangent bundle $TM\to M$ depends only on the dimension of the manifold at $P$.

> **Editorial note - clarification of the object whose stalk is taken.** The source asks for a statement about the “stalk of the tangent bundle”. Stalks belong to presheaves, not directly to bundles. The context of Lecture 3 and Example 3.12 identifies the intended object as the presheaf of continuous sections of the tangent bundle. This edition states that object explicitly and preserves the source's shorthand in this note.

<!-- upstream_entity: Prägarbe/Produkt/Halm/Aufgabe -->

## Exercise 3.16 {#br-bgk-2019-w03-ex16}

Let $\mathcal F$ and $\mathcal G$ be presheaves on a topological space $X$, and let $\mathcal F\times\mathcal G$ be their product presheaf. Show that for every point $P\in X$,

$$
(\mathcal F\times\mathcal G)_P
=\mathcal F_P\times\mathcal G_P.
$$

<!-- upstream_entity: Prägarbe/Homomorphismus/Verknüpfung/Fakt/Beweis/Aufgabe -->

## Exercise 3.17 {#br-bgk-2019-w03-ex17}

Let $X$ be a topological space and $\mathcal F,\mathcal G,\mathcal H$ presheaves on $X$. Prove the following statements.

1. The identity $\mathcal F\to\mathcal F$ is a morphism of presheaves.
2. If $\varphi:\mathcal F\to\mathcal G$ and $\psi:\mathcal G\to\mathcal H$ are morphisms of presheaves, then $\psi\circ\varphi$ is also a morphism of presheaves.
3. If $\mathcal F\subseteq\mathcal G$ is a subpresheaf, the natural inclusion is a morphism of presheaves.

> **Editorial note - source typographical error.** In the third item, the source prints *Prägraben*, an evident typographical error for *Prägarben* (presheaves). The correct form is used above; the same defect is also recorded in Lemma 3.26.

<!-- upstream_entity: Prägarbe/Produkt/Beliebige Indexmenge/Morphismus/Aufgabe -->

## Exercise 3.18 {#br-bgk-2019-w03-ex18}

Let $I$ be an index set, $(\mathcal F_i)_{i\in I}$ a family of presheaves on a topological space $X$, and $\prod_{i\in I}\mathcal F_i$ their product presheaf. Let $\mathcal G$ be another presheaf on $X$. Show that a morphism of presheaves

$$
\psi:\mathcal G\longrightarrow\prod_{i\in I}\mathcal F_i
$$

is the same as a family of morphisms of presheaves

$$
\psi_i:\mathcal G\longrightarrow\mathcal F_i,
\qquad i\in I.
$$

