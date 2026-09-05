---
title: "Worksheet 4 - Sheaves and Sheaf Morphisms"
stable_id: br-bgk-2019-w04
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 4"
upstream_pageid: 110209
upstream_revid: 1003857
upstream_timestamp: "2025-06-10T09:15:51Z"
upstream_mediawiki_sha1: 879b20dfad7b078a205c00bf5e341035b8307f8e
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003857"
authority_manifest: authority/wikiversity-bgk/unit-04/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 3f26616ff7e9f4ac0d5bb0e64ad8435fefc18e32e4c91b16d780d4346498f680
worksheet_xml: authority/wikiversity-bgk/unit-04/worksheet-04.xml
worksheet_xml_sha256: 3e205caf77b5388ff6a0aa2bb1fa3643e354ce4ccc7e5e19d2dc7f6e29daca8a
worksheet_expanded_tex: authority/wikiversity-bgk/unit-04/worksheet-04-expanded.tex
worksheet_expanded_tex_sha256: 7af2dce83605791269ba4fc1d5351100411b0a8081920cce8f1241724249f974
exercise_map: authority/wikiversity-bgk/unit-04/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: a53d958595d6fd0aac34f8ea6562204dda96b44a375e68b33d93d92e63485dcf
official_pdf: authority/artifacts/bgk-worksheet-04-official.pdf
official_pdf_sha256: 082b49c71d075c7bd137ff66ce20d1ec3a76fe2368e1a2c2f0141e774e270ed9
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 9
public_solution_count: 0
---

# Worksheet 4: Sheaves and Sheaf Morphisms {#br-bgk-2019-w04}

<!-- upstream_entity: Garbe/Produkt/Aufgabe -->

## Exercise 4.1 {#br-bgk-2019-w04-ex01}

Let $\mathcal F$ and $\mathcal G$ be sheaves on a topological space $X$. Show that the assignment

$$
U\longmapsto\mathcal F(U)\times\mathcal G(U),
$$

together with the natural product maps as restriction maps, defines a sheaf on $X$.

<!-- upstream_entity: Garbe/Unzusammenhängender Raum/Produkt/Aufgabe -->

## Exercise 4.2 {#br-bgk-2019-w04-ex02}

Let $\mathcal G$ be a sheaf on a disconnected space $X$ with a decomposition

$$
X=U\mathbin{\uplus}V
$$

into two disjoint nonempty open sets. Show that

$$
\mathcal G(X)=\mathcal G(U)\times\mathcal G(V).
$$

<!-- upstream_entity: Topologischer Raum/Disjunkte offene Vereinigung/Garben/Aufgabe -->

## Exercise 4.3 {#br-bgk-2019-w04-ex03}

Let $X$ be a topological space with a decomposition

$$
X=Y\mathbin{\uplus}Z
$$

into two disjoint nonempty open subsets. Let $\mathcal G$ be a sheaf on $Y$ and $\mathcal H$ a sheaf on $Z$. Show that, for each open set $U\subseteq X$, the assignment

$$
\mathcal F(U)
=\mathcal G(U\cap Y)\times\mathcal H(U\cap Z)
$$

defines a sheaf $\mathcal F$ on $X$.

<!-- upstream_entity: Hausdorffraum/Konstante Prägarbe/Keine Garbe/Aufgabe -->

## Exercise 4.4 {#br-bgk-2019-w04-ex04}

Let $X$ be a Hausdorff space with at least two points and let $M$ be a set with at least two elements. Show that the constant presheaf with value $M$ is not a sheaf.

> **Editorial note - source hypothesis too weak.** The source assumes only $M\ne\varnothing$. The conclusion is false if $M$ is a singleton, since the constant singleton-valued presheaf satisfies both sheaf conditions. This edition states the intended hypothesis that $M$ has at least two elements.

<!-- upstream_entity: Garbe/Einschränkung/Garbe/Aufgabe -->

## Exercise 4.5 {#br-bgk-2019-w04-ex05}

Show that the restriction of a sheaf to an open subset

$$
U\subseteq X
$$

is a sheaf.

<!-- upstream_entity: C/Holomorphe Funktion/Keim/Potenzreihe/Aufgabe -->

## Exercise 4.6 {#br-bgk-2019-w04-ex06}

Show that the stalk at $0\in\mathbb C$ of the sheaf of holomorphic functions is isomorphic to the ring of convergent power series in one variable.

<!-- upstream_entity: Garbenmorphismus/Surjektiv/Halmweise surjektiv/Aufgabe -->

## Exercise 4.7 {#br-bgk-2019-w04-ex07}

Let

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

be a sheaf morphism on a topological space $X$. Suppose

$$
\varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
$$

is surjective for every open set $U\subseteq X$. Show that every stalk map

$$
\varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
$$

is also surjective.

<!-- upstream_entity: Garbe/Kommutative Gruppen/Leere Menge/Aufgabe -->

## Exercise 4.8 {#br-bgk-2019-w04-ex08}

Let $\mathcal G$ be a sheaf of commutative groups on a topological space $X$. Show that

$$
\mathcal G(\varnothing)=0,
$$

that is, the value of the sheaf on the empty set is the trivial group.

<!-- upstream_entity: Wolkenkratzergarbe/Gruppe/Garbeneigenschaft/Aufgabe -->

## Exercise 4.9 {#br-bgk-2019-w04-ex09}

Let $X$ be a topological space, $P\in X$ a point, and $G$ a commutative group. Consider the assignment

$$
U\longmapsto
\mathcal G(U):=
\begin{cases}
G,&\text{if }P\in U,\\
0,&\text{if }P\notin U,
\end{cases}
$$

with the natural restriction maps for each inclusion of open sets $V\subseteq U$.

1. Show that $\mathcal G$ is a sheaf of commutative groups.
2. Determine the stalk $\mathcal G_P$.
3. Now suppose that $P$ is a closed point. Determine the stalk $\mathcal G_Q$ at every point $Q\ne P$.

> **Editorial note - two source typographical errors.** The last instruction in the source reads *Besitmme die Halm*. The intended wording is *Bestimme die Halme*, meaning to determine the stalks at all points $Q\ne P$.

The sheaf constructed in the preceding exercise is called the *skyscraper sheaf* with value $G$ at $P$.

