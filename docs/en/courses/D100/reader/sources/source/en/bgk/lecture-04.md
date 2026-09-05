---
title: "Lecture 4 - Sheaves and Sheaf Morphisms"
stable_id: br-bgk-2019-l04
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 4"
upstream_pageid: 109008
upstream_revid: 1003714
upstream_timestamp: "2025-06-08T15:26:17Z"
upstream_mediawiki_sha1: 8eceb7ac307706e0858ffa278bd9d1235574a596
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003714"
authority_manifest: authority/wikiversity-bgk/unit-04/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 3f26616ff7e9f4ac0d5bb0e64ad8435fefc18e32e4c91b16d780d4346498f680
lecture_xml: authority/wikiversity-bgk/unit-04/lecture-04.xml
lecture_xml_sha256: 008241be410fe252da296e8332fa11c1db08960ff84eaac3c073564007d5845a
lecture_expanded_tex: authority/wikiversity-bgk/unit-04/lecture-04-expanded.tex
lecture_expanded_tex_sha256: 4dc55e0810888863946316396cff73ce5ef1a1bb9b46864b64b3ed80ba3a8ea1
official_pdf: authority/artifacts/bgk-lecture-04-official.pdf
official_pdf_sha256: 9e6dd93da57ae35f96568fc717442ac4c6fb209733527143068c34f32248d222
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF and media retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 4: Sheaves and Sheaf Morphisms {#br-bgk-2019-l04}

![Sheaves of spelt wheat standing upright in a field](authority/assets/bgk-u04-triticum-spelta.jpg)

*Sheaves of spelt wheat. André Karwath aka Aka, CC BY-SA 2.5; see the Unit 4 media credits.*

## Sheaves {#br-bgk-2019-l04-s01}

### Definition 4.1: sheaf {#br-bgk-2019-l04-def-01}

Let $X$ be a topological space. A *sheaf* $\mathcal F$ on $X$ is a presheaf $\mathcal F$ on $X$ satisfying the following two properties.

1. For every open cover

   $$
   U=\bigcup_{i\in I}U_i
   $$

   and every $s,t\in\mathcal F(U)$ with

   $$
   \rho_{U,U_i}(s)=\rho_{U,U_i}(t)
   $$

   for all $i\in I$, we have $s=t$.

2. For every open cover

   $$
   U=\bigcup_{i\in I}U_i
   $$

   and every compatible family $s_i\in\mathcal F(U_i)$, meaning that

   $$
   \rho_{U_i,U_i\cap U_j}(s_i)
   =\rho_{U_j,U_i\cap U_j}(s_j)
   $$

   for all $i,j\in I$, there exists an $s\in\mathcal F(U)$ with

   $$
   s_i=\rho_{U,U_i}(s)
   $$

   for all $i\in I$.

These two properties are called the *Serre conditions*. The first says that equality of sections can be checked locally on an open cover. The second says that compatible local sections come from a global section. That global section is unique by the first condition.

The set $\mathcal F(\varnothing)$ has exactly one element. Set-theoretically, this follows by applying the two conditions to the cover of the empty set indexed by the empty set.

As a representative of many similar examples, we show that the presheaf of sections of a continuous map is a sheaf.

### Example 4.2: the sheaf of continuous sections {#br-bgk-2019-l04-exa-01}

We continue Example 3.12. Let $X$ and $Y$ be topological spaces and

$$
p:Y\longrightarrow X
$$

a fixed continuous map. The presheaf of continuous sections in $Y$ is given by

$$
U\longmapsto S(U,Y)
=\{s:U\to p^{-1}(U)\mid s\text{ a continuous section of }p\}.
$$

This presheaf is a sheaf. The first Serre condition holds because two sections are equal when their values agree at every point $P\in U$, and this equality can be checked locally on an open cover. For the second condition, a compatible family of continuous sections

$$
s_i:U_i\longrightarrow Y|_{U_i}
$$

directly defines a section

$$
s:U\longrightarrow Y|_U
$$

extending all the $s_i$ simultaneously. The map $s$ is continuous because continuity can be checked locally.

### Example 4.3: the sheaf of continuous group-valued maps {#br-bgk-2019-l04-exa-02}

Let $G$ be a topological group and $X$ a topological space. The assignment

$$
U\longmapsto C^0(U,G)
$$

is a sheaf: the sheaf of groups of continuous maps with values in $G$. The sheaf properties follow from two facts: equality of continuous maps can be checked pointwise, and continuous maps on open sets which agree on every intersection can be glued to a global continuous map.

### Lemma 4.4: a local test for equality of sections {#br-bgk-2019-l04-lem-01}

Let $\mathcal F$ be a sheaf on a topological space $X$, and let

$$
s,t\in\mathcal F(X).
$$

If

$$
s_P=t_P
$$

in the stalk $\mathcal F_P$ for every $P\in X$, then $s=t$.

#### Proof {#br-bgk-2019-l04-lem-01-proof}

By hypothesis, for every $P\in X$ there is an open neighbourhood

$$
P\in U_P\subseteq X
$$

such that

$$
\rho_{X,U_P}(s)=\rho_{X,U_P}(t).
$$

Since

$$
X=\bigcup_{P\in X}U_P,
$$

the first sheaf property gives $s=t$.

## Sheaf morphisms {#br-bgk-2019-l04-s02}

A sheaf morphism is simply a presheaf morphism between two sheaves. Nevertheless, there are important special features concerning injectivity, surjectivity, images and local tests for isomorphisms.

> **Editorial note - typographical error in the source heading.** The source prints *Garbenmorpismen*; the intended German word is *Garbenmorphismen*. This edition uses the correct mathematical term, “sheaf morphisms”.

### Lemma 4.5: injectivity can be tested on stalks {#br-bgk-2019-l04-lem-02}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a sheaf morphism. The following statements are equivalent.

1. The map

   $$
   \varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
   $$

   is injective for every open set $U\subseteq X$.

2. The stalk map

   $$
   \varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
   $$

   is injective for every $P\in X$.

#### Proof {#br-bgk-2019-l04-lem-02-proof}

First suppose that all maps on sections over open sets are injective. Let $s_P,t_P\in\mathcal F_P$ with

$$
\varphi_P(s_P)=\varphi_P(t_P).
$$

We may represent both germs by sections $s,t\in\mathcal F(U)$ on an open neighbourhood $U$ of $P$. Equality in the stalk $\mathcal G_P$ gives a smaller open neighbourhood

$$
P\in U'\subseteq U
$$

with

$$
\varphi_{U'}(s|_{U'})=\varphi_{U'}(t|_{U'}).
$$

Injectivity of $\varphi_{U'}$ gives $s|_{U'}=t|_{U'}$, hence $s_P=t_P$.

Conversely, suppose that all stalk maps are injective. Let $s,t\in\mathcal F(U)$ with $\varphi_U(s)=\varphi_U(t)$. For every $P\in U$, we obtain

$$
\varphi_P(s_P)=\varphi_P(t_P),
$$

so $s_P=t_P$. Applying Lemma 4.4 to the restriction of the sheaf to $U$, we obtain $s=t$.

### Lemma 4.6: testing isomorphisms on stalks {#br-bgk-2019-l04-lem-03}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a sheaf morphism. The morphism $\varphi$ is a sheaf isomorphism if and only if, for every $P\in X$, the stalk map

$$
\varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
$$

is an isomorphism.

#### Proof {#br-bgk-2019-l04-lem-03-proof}

The forward direction is immediate. For the converse, we must show that

$$
\varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
$$

is bijective for every open set $U\subseteq X$. By restricting both sheaves, it suffices to consider $U=X$. Injectivity follows from Lemma 4.5.

For surjectivity, take $t\in\mathcal G(X)$. For every $P\in X$, there is a unique $s_P\in\mathcal F_P$ with

$$
\varphi_P(s_P)=t_P.
$$

Choose a representative $r_P\in\mathcal F(U_P)$ on an open neighbourhood $U_P$ of $P$. Since $\varphi(r_P)$ and $t$ have the same germ at $P$, after shrinking $U_P$ if necessary we obtain

$$
\varphi_{U_P}(r_P)=t|_{U_P}.
$$

The sets $U_P$ cover $X$. On $U_P\cap U_Q$, for every $Z\in U_P\cap U_Q$, both germs $(r_P)_Z$ and $(r_Q)_Z$ are sent by the isomorphism $\varphi_Z$ to $t_Z$. Thus

$$
(r_P)_Z=(r_Q)_Z.
$$

By Lemma 4.4,

$$
r_P|_{U_P\cap U_Q}=r_Q|_{U_P\cap U_Q}.
$$

The second sheaf property then glues all the $r_P$ to an $r\in\mathcal F(X)$. On each $U_P$, we have $\varphi(r)|_{U_P}=t|_{U_P}$, so the first sheaf property gives $\varphi(r)=t$.

This statement holds neither for presheaves—for example, consider the sheafification of a presheaf—nor without the existence of a morphism between the two sheaves. Two sheaves whose stalks are isomorphic at every point need not be isomorphic as sheaves. Important examples are locally free sheaves: they are locally isomorphic to free sheaves, but in general are not globally free.

At first sight, it may be surprising, perhaps even disappointing, that for a sheaf morphism surjectivity on sections over open sets differs from surjectivity on stalks. What initially appears to be a shortcoming is actually a strength of sheaf theory: the failure of global surjectivity for a stalkwise-surjective morphism can reflect topological properties of the underlying space.

### Definition 4.7: surjective sheaf morphism {#br-bgk-2019-l04-def-02}

A sheaf morphism

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

on a topological space $X$ is called *surjective* if, for every point $P\in X$, the stalk map

$$
\varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
$$

is surjective. This is substantially weaker than surjectivity of the map on sections over every open set.

### Example 4.8: surjective on stalks, but not always on sections {#br-bgk-2019-l04-exa-03}

Consider the continuous group homomorphism

$$
\varphi:\mathbb R\longrightarrow S^1,
\qquad
t\longmapsto(\cos t,\sin t),
$$

that is, the periodic trigonometric parametrisation of the unit circle. On every topological space $X$, this map induces a sheaf morphism

$$
C^0(-,\mathbb R)\longrightarrow C^0(-,S^1),
$$

sending a continuous function $f:U\to\mathbb R$ to the composite

$$
\varphi\circ f:U\longrightarrow S^1.
$$

This morphism is surjective because $\varphi$ is locally invertible. However, the map on sections is not always surjective. For example, if $X=S^1$, the identity on $S^1$ has no continuous lift to $\mathbb R$.

### Lemma 4.9: the sheaf of morphisms {#br-bgk-2019-l04-lem-04}

For two sheaves $\mathcal F$ and $\mathcal G$ on a topological space $X$, the assignment

$$
U\longmapsto
\operatorname{Mor}(\mathcal F|_U,\mathcal G|_U)
$$

is a sheaf.

#### Proof {#br-bgk-2019-l04-lem-04-proof}

Restricting a sheaf morphism

$$
\varphi:\mathcal F|_U\longrightarrow\mathcal G|_U
$$

to any open set $V\subseteq U$ gives a morphism

$$
\varphi|_V:\mathcal F|_V\longrightarrow\mathcal G|_V.
$$

Thus the assignment above is, to begin with, a presheaf.

Let $U=\bigcup_{i\in I}U_i$. For the equality condition, let $\varphi$ and $\psi$ be two morphisms on $U$ whose restrictions agree on every $U_i$. For every open set $V\subseteq U$ and every $s\in\mathcal F(V)$, the sections $\varphi_V(s)$ and $\psi_V(s)$ of $\mathcal G(V)$ agree after restriction to each $V\cap U_i$. The first sheaf property of $\mathcal G$ gives $\varphi_V(s)=\psi_V(s)$. Since this holds for all $V$ and $s$, we obtain $\varphi=\psi$.

For the gluing condition, suppose morphisms

$$
\varphi_i:\mathcal F|_{U_i}\longrightarrow\mathcal G|_{U_i}
$$

are given satisfying

$$
\varphi_i|_{U_i\cap U_j}=\varphi_j|_{U_i\cap U_j}.
$$

For every open set $V\subseteq U$ and every $s\in\mathcal F(V)$, set, on $V\cap U_i$,

$$
t_i=(\varphi_i)_{V\cap U_i}(s|_{V\cap U_i}).
$$

The family $(t_i)$ is compatible on all intersections, so there is a unique $t\in\mathcal G(V)$ with $t|_{V\cap U_i}=t_i$. Set

$$
\varphi_V(s):=t.
$$

If $W\subseteq V$, then $\varphi_V(s)|_W$ and $\varphi_W(s|_W)$ have the same local restrictions on every $W\cap U_i$; uniqueness of gluing shows that they are equal. Thus the family $\varphi_V$ is compatible with all restriction maps and genuinely defines a sheaf morphism

$$
\varphi:\mathcal F|_U\longrightarrow\mathcal G|_U.
$$

Its restriction to each $U_i$ is $\varphi_i$, again by uniqueness of gluing.

> **Editorial note - completion of the source proof.** The source proof checks equality and constructs the gluing only for sections over $U$. A sheaf morphism must have a component on every open set $V\subseteq U$ and must commute with restrictions. The proof above supplies the missing standard step, using the cover $(V\cap U_i)_i$ and uniqueness of gluing. The abbreviated source form remains preserved within the Unit 4 authority boundary.

### Corollary 4.10: gluing sheaf morphisms {#br-bgk-2019-l04-cor-01}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$, and let $\mathcal F$ and $\mathcal G$ be sheaves on $X$. For each $i\in I$, suppose a sheaf morphism

$$
\alpha_i:\mathcal F|_{U_i}\longrightarrow\mathcal G|_{U_i}
$$

is given with

$$
\alpha_i|_{U_i\cap U_j}=\alpha_j|_{U_i\cap U_j}
$$

for all $i,j$. Then there is a unique sheaf morphism

$$
\alpha:\mathcal F\longrightarrow\mathcal G
$$

satisfying $\alpha|_{U_i}=\alpha_i$ for every $i$.

#### Proof {#br-bgk-2019-l04-cor-01-proof}

This follows directly from Lemma 4.9.

### Corollary 4.11: testing equality on stalks {#br-bgk-2019-l04-cor-02}

Let $\mathcal F$ and $\mathcal G$ be sheaves on a topological space $X$, and let

$$
\alpha,\beta:\mathcal F\longrightarrow\mathcal G
$$

be sheaf morphisms. Then

$$
\alpha=\beta
$$

if and only if

$$
\alpha_P=\beta_P
$$

for every $P\in X$.

> **Editorial note - inconsistent source index.** The source writes $\alpha_p=\beta_P$ after quantifying over the point $P$. This edition uses the consistent indices $\alpha_P=\beta_P$.

#### Proof {#br-bgk-2019-l04-cor-02-proof}

This follows directly from Lemma 4.9 and Lemma 4.4.

