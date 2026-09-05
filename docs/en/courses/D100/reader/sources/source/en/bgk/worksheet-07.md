---
title: "Worksheet 7 - Ringed Spaces and Local Rings"
stable_id: br-bgk-2019-w07
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 7"
upstream_pageid: 110212
upstream_revid: 618943
upstream_timestamp: "2020-02-16T12:35:13Z"
upstream_mediawiki_sha1: fe0e1a1fd6c0ca988bc7aea5d9f262f55f785aa1
source_url: "https://de.wikiversity.org/w/index.php?oldid=618943"
authority_manifest: authority/wikiversity-bgk/unit-07/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 001074c62cedb1efc988d3214416d2d86a02976d5b22dc272f4fe064e72dfc95
worksheet_xml: authority/wikiversity-bgk/unit-07/worksheet-07.xml
worksheet_xml_sha256: 4115e3aef855bacb808d29db8d41477629bb0a50e895c8a38b5e237fb0b1436b
worksheet_expanded_tex: authority/wikiversity-bgk/unit-07/worksheet-07-expanded.tex
worksheet_expanded_tex_sha256: 5318e77fd0a3d79dbd08281bca06b39c6639940901fbf6aaf13fac16fd60d898
exercise_map: authority/wikiversity-bgk/unit-07/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 309a1478ffcc6b7fdd02ddb72f29dca37d9d9ca8756737e7723d9bae148365c0
official_pdf: authority/artifacts/bgk-worksheet-07-official.pdf
official_pdf_sha256: a0cacead1e51ae62e560992c04bb9e519a1aaa85c8fd007d6756602bd594693f
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 21
public_solution_count: 1
---

# Worksheet 7: Ringed Spaces and Local Rings {#br-bgk-2019-w07}

<!-- upstream_entity: Beringter Raum/Offene Teilmenge/Aufgabe -->

## Exercise 7.1 {#br-bgk-2019-w07-ex01}

Show that every open subset $U\subseteq X$ of a ringed space
$\bigl(X,\mathcal O_X\bigr)$ is again a ringed space.

<!-- upstream_entity: Beringter Raum/Global 0/Aufgabe -->

## Exercise 7.2 {#br-bgk-2019-w07-ex02}

Let $(X,\mathcal O_X)$ be a ringed space with

$$
\Gamma(X,\mathcal O_X)=0.
$$

Show that for every open subset $U\subseteq X$ we also have

$$
\Gamma(U,\mathcal O_X)=0.
$$

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Offene dichte Teilmenge/Restriktion/Injektiv/Aufgabe -->

## Exercise 7.3 {#br-bgk-2019-w07-ex03}

Let $X$ be a topological space equipped with the sheaf of real-valued
continuous functions, and let $U\subseteq X$ be a dense open subset.
Show that the restriction map

$$
\begin{aligned}
\Gamma(X,\mathcal O_X)&\longrightarrow\Gamma(U,\mathcal O_X),\\
f&\longmapsto f\big|_U
\end{aligned}
$$

is injective.

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Offene dichte Teilmenge/Restriktion/Nicht surjektiv/Aufgabe -->

## Exercise 7.4 {#br-bgk-2019-w07-ex04}

Let $X$ be a topological space equipped with the sheaf of real-valued
continuous functions, and let $U\subseteq X$ be a dense open subset.
Show that the restriction map

$$
\Gamma(X,\mathcal O_X)\longrightarrow\Gamma(U,\mathcal O_X),
\qquad f\longmapsto f\big|_U,
$$

need not be surjective.

> **Edition note — continuity in Exercises 7.3 and 7.4.** Their source
> prose says only “real-valued functions”, while their source titles
> specify continuous functions. The translation makes continuity explicit;
> the assertions are not valid for the sheaf of all set-theoretic functions.

<!-- upstream_entity: Beringter Raum/Einheiten/Garbe/Aufgabe -->

## Exercise 7.5 {#br-bgk-2019-w07-ex05}

Let $(X,\mathcal O_X)$ be a ringed space. Show that the assignment taking
each open subset $U\subseteq X$ to the unit group

$$
\bigl(\Gamma(U,\mathcal O_X)\bigr)^\times
$$

of the commutative ring $\Gamma(U,\mathcal O_X)$, together with the natural
restrictions, is a sheaf of commutative groups.

This sheaf has its own name. For a ringed space $(X,\mathcal O_X)$, the
sheaf defined on open sets $U\subseteq X$ by

$$
\Gamma(U,\mathcal O_X^\times)
:=\bigl(\Gamma(U,\mathcal O_X)\bigr)^\times
$$

is called the *sheaf of units* on $X$.

<!-- upstream_entity: Beringter Raum/Morphismus/Hintereinanderschaltung/Aufgabe -->

## Exercise 7.6 {#br-bgk-2019-w07-ex06}

Show that the composition of morphisms of ringed spaces is again a
morphism of ringed spaces.

<!-- upstream_entity: Beringter Raum/Offene Teilmenge/Inklusion/Morphismus/Aufgabe -->

## Exercise 7.7 {#br-bgk-2019-w07-ex07}

Show that, for every open subset $U\subseteq X$ of a ringed space
$(X,\mathcal O_X)$, there is a morphism of ringed spaces

$$
(U,\mathcal O_X|_U)\longrightarrow(X,\mathcal O_X).
$$

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Beringter Raum/Morphismus/Aufgabe -->

## Exercise 7.8 {#br-bgk-2019-w07-ex08}

Let $X$ and $Y$ be topological spaces, and let $\varphi:X\to Y$ be a
continuous map. Show that this induces a morphism of locally ringed spaces.

<!-- upstream_entity: Reelle Mannigfaltigkeit/Differenzierbare Abbildung/Beringter Raum/Morphismus/Aufgabe -->

## Exercise 7.9 {#br-bgk-2019-w07-ex09}

Let $L$ and $M$ be differentiable manifolds, and let $\varphi:L\to M$ be a
differentiable map. Show that this induces a morphism of locally ringed
spaces.

<!-- upstream_entity: Reelle Mannigfaltigkeit/Stetige Funktionen/Differenzierbare Funktionen/Morphismus/Aufgabe -->

## Exercise 7.10 {#br-bgk-2019-w07-ex10}

Let $M$ be a differentiable manifold. We can make it a ringed space in two
ways: using the sheaf of continuous functions $C^0(-,\mathbb R)$, or using
the sheaf of differentiable functions $C^1(-,\mathbb R)$. Show that there is
a morphism of ringed spaces

$$
(M,C^0(-,\mathbb R))\longrightarrow(M,C^1(-,\mathbb R))
$$

which is topologically the identity, but is not an isomorphism of ringed
spaces.

> **Edition note — the functions in question.** The two sheaves in the
> source are read as the sheaves of real-valued continuous and
> differentiable functions on the same open sets; the notation
> $C^0(-,\mathbb R)$ and $C^1(-,\mathbb R)$ is retained.
> The non-isomorphism assertion requires $M$ to have a positive-dimensional
> component. For a zero-dimensional manifold the two sheaves coincide;
> the source omits this exception.

The following exercises focus on local rings.

<!-- upstream_entity: Lokaler Ring/Charakterisierung mit Addition/Aufgabe -->

## Exercise 7.11 {#br-bgk-2019-w07-ex11}

Let $R$ be a commutative ring. Show that $R$ is a local ring if and only if
$a+b$ can be a unit only when $a$ or $b$ is a unit.

> **Edition note — exclusion of the zero ring.** Here assume $R\ne0$.
> The source does not state this hypothesis: the zero ring satisfies the
> displayed unit condition but has no maximal ideal, so is not local in
> the sense of Exercise 7.12.

<!-- upstream_entity: Kommutative Ringtheorie/Lokaler Ring/Definition äquivalent/Aufgabe -->

## Exercise 7.12 {#br-bgk-2019-w07-ex12}

Let $R$ be a commutative ring. Show that the following statements are
equivalent.

1. $R$ has exactly one maximal ideal.
2. The set of nonunits $R\setminus R^\times$ forms an ideal in $R$.

<!-- upstream_entity: Lokaler Ring/Enthält Körper/Gleiche Charakteristik/Aufgabe -->

## Exercise 7.13 {#br-bgk-2019-w07-ex13}

Let $R$ be a local ring with residue field $K$. Show that $R$ and $K$ have
the same characteristic if and only if $R$ contains a field.

<!-- upstream_entity: Lokaler Ring/Restklassenring/Einheiten surjektiv/Aufgabe -->

## Exercise 7.14* {#br-bgk-2019-w07-ex14}

Let $R$ be a local ring and let $\mathfrak a$ be an ideal of $R$. Show that
the map

$$
R^\times\longrightarrow(R/\mathfrak a)^\times
$$

is surjective.

<!-- upstream_entity: Rationale Zahlen/Unterringe/Lokaler Ring/Aufgabe -->

## Exercise 7.15 {#br-bgk-2019-w07-ex15}

Determine the subrings of the rational numbers $\mathbb Q$ that are local.

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Restekörper/Aufgabe -->

## Exercise 7.16 {#br-bgk-2019-w07-ex16}

Let $X$ be a topological space equipped with the sheaf of real-valued
continuous functions. Show that the residue field at every point of $X$
is equal to $\mathbb R$.

<!-- upstream_entity: Reelle Zahlen/Körperisomorphismus/Ist Identität/Aufgabe -->

## Exercise 7.17 {#br-bgk-2019-w07-ex17}

Show that the only field isomorphism

$$
\varphi:\mathbb R\longrightarrow\mathbb R
$$

is the identity.

<!-- upstream_entity: Topologischer Raum/Stetige Funktion/Beringter Raum/Rekonstruktion/Aufgabe -->

## Exercise 7.18 {#br-bgk-2019-w07-ex18}

Let $X$ be a topological space equipped with the sheaf of real-valued
continuous functions. Regard it as an abstract ringed space: we forget
that its elements are functions, but still know the topological space,
the rings, and their restriction maps. Can the meaning of the ring
elements as functions be reconstructed from these data?

<!-- upstream_entity: Topologischer Raum/Stetige Funktion/C/Beringter Raum/Automorphismus/Rekonstruktion/Aufgabe -->

## Exercise 7.19 {#br-bgk-2019-w07-ex19}

Let $X$ be a topological space equipped with the sheaf of complex-valued
continuous functions. Show that the assignment

$$
(X,C^0(-,\mathbb C))\longrightarrow(X,C^0(-,\mathbb C)),
$$

which is topologically the identity and takes each function on an open set
to its complex conjugate, is an automorphism of ringed spaces. Deduce that
knowing $(X,C^0(-,\mathbb C))$ as an abstract ringed space does not allow
one to reconstruct how the ring elements act as functions.

<!-- upstream_entity: Beringter Raum/Einheit/Lokale Eigenschaft/Aufgabe -->

## Exercise 7.20 {#br-bgk-2019-w07-ex20}

Let $(X,\mathcal O_X)$ be a ringed space and let

$$
f\in\Gamma(X,\mathcal O_X).
$$

Show that the following properties are equivalent.

1. $f$ is a unit in $\Gamma(X,\mathcal O_X)$.
2. There is an open cover

   $$
   X=\bigcup_{i\in I}U_i
   $$

   such that every restriction $f|_{U_i}$ is a unit.
3. The germ $f_P\in\mathcal O_{X,P}$ is a unit for every point $P\in X$.

> **Edition note — source variable.** In the restriction in item (2), the
> source uses the letter $s$, although the function introduced is $f$.
> The translation writes $f|_{U_i}$ to make the mathematical
> quantification consistent; no new content is added.

<!-- upstream_entity: Lokal beringter Raum/Invertierbarkeitsort/Monoidhomomorphismus/Aufgabe -->

## Exercise 7.21 {#br-bgk-2019-w07-ex21}

Let $(X,\mathcal O_X)$ be a locally ringed space. Show that the assignment

$$
\begin{aligned}
\Gamma(X,\mathcal O_X)&\longrightarrow\tau(X),\\
f&\longmapsto X_f
\end{aligned}
$$

is a monoid homomorphism from the multiplicative monoid of the ring of
global sections to the monoid of open subsets of $X$, with intersection as
the operation.

> **Edition note — underlying space in the source.** The final sentence
> in the source refers to the monoid of open subsets of $M$, although the
> space under consideration is $X$. The translation corrects the symbol
> for the underlying space to $X$; the definition of $X_f$ and the
> intersection operation remain unchanged.
