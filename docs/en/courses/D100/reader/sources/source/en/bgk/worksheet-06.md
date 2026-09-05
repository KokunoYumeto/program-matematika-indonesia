---
title: "Worksheet 6 - Covering Maps, Exactness, and Pullback and Pushforward of Sheaves"
stable_id: br-bgk-2019-w06
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 6"
upstream_pageid: 110211
upstream_revid: 900086
upstream_timestamp: "2023-06-27T11:07:09Z"
upstream_mediawiki_sha1: 619536dcd80063470e12de7a3ebb3fc9fe1aa5e5
source_url: "https://de.wikiversity.org/w/index.php?oldid=900086"
authority_manifest: authority/wikiversity-bgk/unit-06/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 69a10e682e853c6f386afbc68438605846e5096220b21bd1e827c07633a79244
worksheet_xml: authority/wikiversity-bgk/unit-06/worksheet-06.xml
worksheet_xml_sha256: b82d2ac0f8a0420a53e44be87c0b5a0f8237daac39ef86cf3be365a3b8fe37bd
worksheet_expanded_tex: authority/wikiversity-bgk/unit-06/worksheet-06-expanded.tex
worksheet_expanded_tex_sha256: 0de1911162df14c38fa00755cf67583fbdd9b101134314e6d47a546922e875c1
exercise_map: authority/wikiversity-bgk/unit-06/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: ea15e1f79b4dfc0928fe132eb83e8d20d10fbc84837de153da2b4e345e5a04a0
official_pdf: authority/artifacts/bgk-worksheet-06-official.pdf
official_pdf_sha256: 7b4f4569e7ab749a9e6affac715592316c109507d91971fd1c7b82cefaa825b5
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 19
public_solution_count: 0
---

# Worksheet 6: Covering Maps, Exactness, and Pullback and Pushforward of Sheaves {#br-bgk-2019-w06}

<!-- upstream_entity: Überlagerung/Diskret/Definition -->

### Definition: covering map {#br-bgk-2019-w06-def-01}

Let $X$ and $Y$ be topological spaces. A continuous map

$$
p:Y\longrightarrow X
$$

is called a *covering map* if there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

and a family of discrete topological spaces $F_i$, for $i\in I$, such that
$p^{-1}(U_i)$ is homeomorphic to $U_i\times F_i$ with the product topology,
and these homeomorphisms are compatible with the maps to $U_i$.

<!-- upstream_entity: R und S^1/Überlagerung/Aufgabe -->

## Exercise 6.1 {#br-bgk-2019-w06-ex01}

Show that the map

$$
\begin{aligned}
\mathbb R&\longrightarrow S^1,\\
t&\longmapsto(\cos t,\sin t)
\end{aligned}
$$

is a covering map.

<!-- upstream_entity: C und C^x/Überlagerung/Aufgabe -->

## Exercise 6.2 {#br-bgk-2019-w06-ex02}

Show that the map

$$
\begin{aligned}
\mathbb C&\longrightarrow\mathbb C^{\times}=\mathbb C\setminus\{0\},\\
z&\longmapsto\exp z
\end{aligned}
$$

is a covering map.

<!-- upstream_entity: Überlagerung/Lokaler Schnitt/Aufgabe -->

## Exercise 6.3 {#br-bgk-2019-w06-ex03}

Prove that, for every covering map

$$
p:Y\longrightarrow X
$$

and every point $x\in X$, there is an open neighbourhood

$$
x\in U\subseteq X
$$

and a continuous section

$$
s:U\longrightarrow p^{-1}(U)
$$

with $p\circ s=\operatorname{Id}_U$.

> **Edition note — non-empty fibres.** This assertion requires $p$ to be
> surjective (or, at the chosen point, $p^{-1}(x)\ne\varnothing$). The
> source definition above does not exclude empty discrete fibres $F_i$.
> Read the exercise with this additional hypothesis; no section over $x$
> can exist when its fibre is empty.

<!-- upstream_entity: Topologische Gruppen/Spaltende Sequenz/Garbenversion/Aufgabe -->

## Exercise 6.4 {#br-bgk-2019-w06-ex04}

Let $F$ and $H$ be commutative topological groups, and let

$$
G=F\times H
$$

be their product group with the product topology. Let

$$
0\longrightarrow F\longrightarrow G\longrightarrow H\longrightarrow0
$$

be the corresponding short exact sequence. Show that, for every topological
space $X$, there is a short exact sequence of sheaves

$$
0\longrightarrow C^0(-,F)\longrightarrow C^0(-,G)\longrightarrow
C^0(-,H)\longrightarrow0
$$

whose rightmost map is always surjective on global sections.

<!-- upstream_entity: Stetige Abbildung/Prägarbe/Vorschub/Halme/Fakt/Beweis/Aufgabe -->

## Exercise 6.5 {#br-bgk-2019-w06-ex05}

Let $\varphi:X\to Y$ be a continuous map, let $Q\in Y$ be a point, and let
$\mathcal F$ be a presheaf on $X$. Show that the stalk of the pushforward
presheaf $\varphi_*\mathcal F$ at $Q$ is equal to

$$
\operatorname*{colim}_{\substack{V\subseteq Y,\;V\text{ open}\\Q\in V}}
\mathcal F(\varphi^{-1}(V))
=
\operatorname*{colim}_{\substack{U\subseteq X,\;U\text{ open}\\
\text{there is an open }V\text{ with }Q\in V\text{ and }\varphi^{-1}(V)\subseteq U}}
\mathcal F(U).
$$

> **Edition note — the colimit index in the source.** The source abbreviates
> the neighbourhood condition to “there is $Q\in V$”; the intended meaning
> is that there is an open set $V\ni Q$. This explicit formulation is used
> above. Both colimits range over open sets; the source leaves this
> presheaf-domain requirement implicit.

<!-- upstream_entity: Stetige Abbildung/Garbe/Rückzug/Halme/Fakt/Beweis/Aufgabe -->

## Exercise 6.6 {#br-bgk-2019-w06-ex06}

Let $\varphi:X\to Y$ be a continuous map and let $\mathcal G$ be a sheaf on
$Y$. Show that the stalk of the pullback sheaf at a point $P\in X$ is equal
to the stalk of $\mathcal G$ at $\varphi(P)$.

> **Edition note — source grammar.** The source prints the German phrase
> *einer stetige Abbildung*, with a mismatch between the article and
> adjective. The translation uses grammatical English without changing
> the mathematical content.

<!-- upstream_entity: Menge/Topologien/Vorschub und Rückzug/Aufgabe -->

## Exercise 6.7 {#br-bgk-2019-w06-ex07}

Let $X$ be a set with two topologies $\tau_1$ and $\tau_2$ such that the
identity

$$
\varphi:X_1=(X,\tau_1)\longrightarrow X_2=(X,\tau_2)
$$

is continuous; thus the first topology is finer than the second. Let
$\mathcal F_1$ be a sheaf on $X_1$ and let $\mathcal F_2$ be a sheaf on
$X_2$. Determine $\varphi_*\mathcal F_1$ and $\varphi^{-1}\mathcal F_2$.
What do they look like when $\tau_1$ is the discrete topology and $\tau_2$
is the indiscrete topology?

<!-- upstream_entity: Topologischer Raum/Konstante Abbildung/Vorschub/Aufgabe -->

## Exercise 6.8 {#br-bgk-2019-w06-ex08}

Let $X$ be a topological space and let $\varphi:X\to\{P\}$ be the constant
map. If $\mathcal F$ is a sheaf on $X$, determine $\varphi_*\mathcal F$.

<!-- upstream_entity: Topologischer Raum/Punkt/Vorschub/Wolkenkratzergarbe/Aufgabe -->

## Exercise 6.9 {#br-bgk-2019-w06-ex09}

Let $X$ be a topological space, let $P\in X$, and let

$$
i:\{P\}\longrightarrow X
$$

be the corresponding inclusion. Let $\mathcal F$ be a sheaf of
commutative groups on $\{P\}$. Describe the sheaf $i_*\mathcal F$ on the
open sets of $X$. What do the stalks of $i_*\mathcal F$ look like when $P$
is a closed point?

Compare also Exercise 4.9.

<!-- upstream_entity: Topologischer Raum/Konstante Abbildung/Rückzug/Aufgabe -->

## Exercise 6.10 {#br-bgk-2019-w06-ex10}

Let $X$ be a topological space and let $\varphi:X\to\{P\}$ be the constant
map. If $\mathcal G$ is a sheaf on $\{P\}$, determine
$\varphi^{-1}\mathcal G$.

<!-- upstream_entity: Topologische Räume/Stetige Abbildung/Garbe vorne/Vorschub und Rückzug/Morphismus/Aufgabe -->

## Exercise 6.11 {#br-bgk-2019-w06-ex11}

Let $\varphi:X\to Y$ be a continuous map between topological spaces $X$ and
$Y$, and let $\mathcal F$ be a sheaf on $X$. Prove that there is a natural
sheaf morphism on $X$,

$$
\varphi^{-1}(\varphi_*\mathcal F)\longrightarrow\mathcal F.
$$

<!-- upstream_entity: Topologische Räume/Stetige Abbildung/Garbe hinten/Rückzug und Vorschub/Morphismus/Aufgabe -->

## Exercise 6.12 {#br-bgk-2019-w06-ex12}

Let $\varphi:X\to Y$ be a continuous map between topological spaces $X$ and
$Y$, and let $\mathcal G$ be a sheaf on $Y$. Prove that there is a natural
sheaf morphism on $Y$,

$$
\mathcal G\longrightarrow\varphi_*\bigl(\varphi^{-1}\mathcal G\bigr).
$$

<!-- upstream_entity: Topologische Räume/Stetige Abbildung/Rückzug und Vorschub/Morphismen/Aufgabe -->

## Exercise 6.13 {#br-bgk-2019-w06-ex13}

Let $\varphi:X\to Y$ be a continuous map between topological spaces $X$ and
$Y$. Let $\mathcal F$ be a sheaf on $X$ and let $\mathcal G$ be a sheaf on
$Y$. Prove that there is a natural bijection between sheaf morphisms on $X$

$$
\psi:\varphi^{-1}\mathcal G\longrightarrow\mathcal F
$$

and sheaf morphisms on $Y$

$$
\theta:\mathcal G\longrightarrow\varphi_*\mathcal F.
$$

<!-- upstream_entity: Mengen/Relatives Produkt/Aufgabe -->

## Exercise 6.14 {#br-bgk-2019-w06-ex14}

Let $L_1,L_2,M$ be sets, and let $p_1:L_1\to M$ and $p_2:L_2\to M$ be
maps. Define

$$
L_1\times_M L_2
:=\{(x_1,x_2)\mid p_1(x_1)=p_2(x_2)\}
\subseteq L_1\times L_2.
$$

1. Show that there is a commutative diagram

$$
\begin{matrix}
L_1\times_M L_2&\longrightarrow&L_1\\
\downarrow&&\downarrow\\
L_2&\longrightarrow&M
\end{matrix}
$$

2. Let $T$ be another set, and let $\psi_1:T\to L_1$ and
   $\psi_2:T\to L_2$ be maps with

   $$
   p_1\circ\psi_1=p_2\circ\psi_2.
   $$

   Show that there is a unique map $\psi:T\to L_1\times_M L_2$ whose
   projections to $L_1$ and $L_2$ agree with $\psi_1$ and $\psi_2$,
   respectively.

<!-- upstream_entity: Topologische Räume/Relatives Produkt/Aufgabe -->

## Exercise 6.15 {#br-bgk-2019-w06-ex15}

Let $L_1,L_2,M$ be topological spaces, and let $p_1:L_1\to M$ and
$p_2:L_2\to M$ be continuous maps. Define

$$
L_1\times_M L_2
:=\{(x_1,x_2)\mid p_1(x_1)=p_2(x_2)\}
\subseteq L_1\times L_2
$$

with the induced topology.

1. Show that there is a commutative diagram of continuous maps,

   $$
   \begin{matrix}
   L_1\times_M L_2&\longrightarrow&L_1\\
   \downarrow&&\downarrow\\
   L_2&\longrightarrow&M
   \end{matrix}
   $$

2. Let $T$ be another topological space, and let $\psi_1:T\to L_1$ and
   $\psi_2:T\to L_2$ be continuous maps with

   $$
   p_1\circ\psi_1=p_2\circ\psi_2.
   $$

   Show that there is a unique continuous map
   $\psi:T\to L_1\times_M L_2$ whose projections to $L_1$ and $L_2$ agree
   with $\psi_1$ and $\psi_2$, respectively.

> **Edition note — source grammar.** The source prints the German phrase
> *eine weiterer topologischer Raum*, with a mismatch between the article
> and adjective. The translation uses “another topological space” without
> changing the mathematical content.

> **Edition note — fibre-product notation in the source.** On some source
> surfaces, the equality condition is written with the symbols
> $\varphi_1,\varphi_2$, although the maps just defined are called $p_1,p_2$.
> The translation uses $p_1,p_2$ consistently and preserves the intended
> mathematical object.

<!-- upstream_entity: Topologische Räume/Vektorbündel/Rückzug/Aufgabe -->

## Exercise 6.16 {#br-bgk-2019-w06-ex16}

Let $X$ and $Y$ be topological spaces, let $\varphi:Y\to X$ be a continuous
map, and let $p:V\to X$ be a vector bundle over $X$. Prove that

$$
Y\times_XV
$$

(see Exercise 6.15) is a vector bundle over $Y$.

<!-- upstream_entity: Topologischer Raum/Vektorbündel/Summe/Produktrealisierung/Aufgabe -->

## Exercise 6.17 {#br-bgk-2019-w06-ex17}

Let $X$ be a topological space, and let $p:V\to X$ and $q:W\to X$ be vector
bundles over $X$. Prove that

$$
V\times_XW
$$

(see Exercise 6.15) is a vector bundle over $X$ that agrees with the direct
sum of the vector bundles over $X$.

<!-- upstream_entity: Topologische Räume/Relatives Produkt/Schnitt/Charakterisierung/Aufgabe -->

## Exercise 6.18 {#br-bgk-2019-w06-ex18}

Let $X,Y,Z$ be topological spaces, and let $\varphi:Y\to X$ and $p:Z\to X$
be continuous maps. Let

$$
p_Y:Y\times_XZ\longrightarrow Y
$$

be the natural projection. Show that a continuous section

$$
s:Y\longrightarrow Y\times_XZ
$$

is the same as a continuous map $t:Y\to Z$ satisfying

$$
p\circ t=\varphi.
$$

<!-- upstream_entity: Topologische Räume/Relatives Produkt/Rückzug/Schnitte/Aufgabe -->

## Exercise 6.19 {#br-bgk-2019-w06-ex19}

Let $X,Y,Z$ be topological spaces, and let $\varphi:Y\to X$ and $p:Z\to X$
be continuous maps. Let $p_Y:Y\times_XZ\to Y$ be the natural projection.
Let $\mathcal G$ be the sheaf of continuous sections of $p$ on $X$. Show
that the pullback $\varphi^*\mathcal G$ agrees with the sheaf of sections
of $p_Y$.

> **Edition note — meaning of pullback.** The source uses
> $\varphi^*\mathcal G$ here, whereas Definition 6.13 denotes the inverse
> image of a sheaf by $\varphi^{-1}\mathcal G$. If the former is intended
> to mean the latter, the assertion is false for arbitrary continuous
> $p$: for $X$ a point and $Y=Z=\mathbb R$, the inverse image consists of
> locally constant real-valued functions, while sections of $p_Y$ are all
> continuous real-valued functions. A sufficient additional hypothesis is
> that $p$ be a local homeomorphism. This qualification is editorial, not
> an available source solution; the original notation is retained.
