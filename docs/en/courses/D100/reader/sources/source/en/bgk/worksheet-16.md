---
title: "Worksheet 16 - Locally Free Sheaves"
stable_id: br-bgk-2019-w16
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 16"
upstream_pageid: 110223
upstream_revid: 619454
upstream_timestamp: "2020-02-17T16:19:33Z"
upstream_mediawiki_sha1: 24134a0ca04b3c50ce0559772d5870e22c79401a
source_url: "https://de.wikiversity.org/w/index.php?oldid=619454"
authority_manifest: null
authority_manifest_status: "Not published by the capture process; the audit binding uses the exact individual surfaces below."
worksheet_api: authority/wikiversity-bgk/unit-16/worksheet-16-api.json
worksheet_api_sha256: ff6db5399f5db8602d7580bde3262b2ea3313c2c12ad4887b745c12fa733c189
worksheet_xml: authority/wikiversity-bgk/unit-16/worksheet-16.xml
worksheet_xml_sha256: 96cded28a6359e233f24552c42fd53be657452e16e4d13ca132298c09fc5ba60
worksheet_expanded_tex: authority/wikiversity-bgk/unit-16/worksheet-16-expanded.tex
worksheet_expanded_tex_sha256: fd1035bbdc57bb7ff9da79f1ea0d26d2e17666b33e373c4c36f23f2c2ce3500a
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_pages: "145-148"
ordered_exercise_map: authority/wikiversity-bgk/unit-16/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: da420bada3728eb5f3fcf0a6c0ed7e75c1dd792b9ed99f1579a5acf7e7500526
candidate_evidence: authority/wikiversity-bgk/unit-16/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 022a9d9912991339073c1768b0ac14ff886b6bbb9c601778ce683a6d9f5a98a7
exercise_count: 23
public_solution_count: 1
public_solution_numbers: "12"
media_credits: source/id-ID/media-credits-bgk-unit-16.md
license: "Semantic course text and this translation: CC BY-SA 4.0. Commons metadata for the official course PDF states CC BY-SA 4.0, whereas page 265 of the PDF carries a CC BY-SA 3.0 notice; both are retained without a blanket relicensing claim."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
source_binding_status: "verified_individual_surfaces_and_exact_course_pdf_without_unit_manifest"
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 16: Locally Free Sheaves {#br-bgk-2019-w16}

The star marks the only exercise with a frozen public solution, Exercise 16.12. The other twenty-two exercises have negative candidate results; this edition does not invent new solutions.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Direkte Summe/Aufgabe -->

## Exercise 16.1 {#br-bgk-2019-w16-ex01}

Let $\mathcal F$ and $\mathcal G$ be locally free sheaves on a ringed space, of ranks $r$ and $s$ respectively. Prove that the direct sum $\mathcal F\oplus\mathcal G$ is locally free of rank $r+s$.

<!-- upstream_entity: Beringter Raum/Lokal freie Garben/Duale Garbe/Lokal frei/Aufgabe -->

## Exercise 16.2 {#br-bgk-2019-w16-ex02}

Let $\mathcal F$ be a locally free sheaf of rank $r$ on the ringed space $(X,\mathcal O_X)$. Prove that the dual sheaf $\mathcal F^*$ is also locally free of rank $r$.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Bidual/Aufgabe -->

## Exercise 16.3 {#br-bgk-2019-w16-ex03}

Prove that a locally free sheaf $\mathcal F$ on a ringed space $(X,\mathcal O_X)$ is naturally isomorphic to its bidual $\mathcal F^{**}$.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Homomorphismus/Surjektiv/Kern/Aufgabe -->

## Exercise 16.4 {#br-bgk-2019-w16-ex04}

Let $\mathcal F$ and $\mathcal G$ be locally free sheaves on a ringed space, and let

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

be a surjective module homomorphism. Prove that the kernel $\operatorname{kern}\varphi$ is also locally free.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Rang/Additiv/Aufgabe -->

## Exercise 16.5 {#br-bgk-2019-w16-ex05}

Prove that the rank of locally free sheaves on a ringed space $(X,\mathcal O_X)$ is additive in short exact sequences. That is, if there is a short exact sequence of locally free sheaves

$$
0\longrightarrow\mathcal F
\longrightarrow\mathcal G
\longrightarrow\mathcal H
\longrightarrow0,
$$

then

$$
\operatorname{rank}\mathcal G
=\operatorname{rank}\mathcal F+\operatorname{rank}\mathcal H.
$$

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Tensorprodukt/Aufgabe -->

## Exercise 16.6 {#br-bgk-2019-w16-ex06}

Let $\mathcal F$ and $\mathcal G$ be locally free sheaves on a ringed space, of ranks $r$ and $s$ respectively. Prove that the tensor product

$$
\mathcal F\otimes_{\mathcal O_X}\mathcal G
$$

is locally free of rank $rs$.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Homomorphismus/Injektiv/Quotient/Aufgabe -->

## Exercise 16.7 {#br-bgk-2019-w16-ex07}

Let $\mathcal F$ and $\mathcal G$ be locally free sheaves on a ringed space, and let $\varphi:\mathcal F\to\mathcal G$ be an injective module homomorphism. Show that the quotient sheaf $\mathcal G/\mathcal F$ is generally not locally free.

<!-- upstream_entity: Noethersches Schema/Kohärenter Modul/Lokal frei/Punktweise/Aufgabe -->

## Exercise 16.8 {#br-bgk-2019-w16-ex08}

Let $\mathcal F$ be a coherent module on the Noetherian scheme $(X,\mathcal O_X)$, and let $r\in\mathbb N$. Prove that the following properties are equivalent.

1. $\mathcal F$ is locally free of rank $r$.
2. For every point $P\in X$, the stalk $\mathcal F_P$ is a free $\mathcal O_{X,P}$-module of rank $r$.

<!-- upstream_entity: Integres noethersches Schema/Kohärenter Modul/Offene Menge/Frei/Aufgabe -->

## Exercise 16.9 {#br-bgk-2019-w16-ex09}

Let $(X,\mathcal O_X)$ be a Noetherian integral scheme and let $\mathcal F$ be a coherent module on $X$. Prove that there is a nonempty open subset $U\subseteq X$ such that $\mathcal F|_U$ is free.

<!-- upstream_entity: Noethersches Schema/Kohärente Garben/Isomorphismus im Punkt/Isomorphismus auf Umgebung/Aufgabe -->

## Exercise 16.10 {#br-bgk-2019-w16-ex10}

Let $(X,\mathcal O_X)$ be a Noetherian scheme and let $\varphi:\mathcal F\to\mathcal G$ be a homomorphism of coherent modules $\mathcal F$ and $\mathcal G$ on $X$. Let $P\in X$ be a point such that

$$
\varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
$$

is an isomorphism. Prove that there is an open neighbourhood $P\in U\subseteq X$ such that

$$
\varphi:\mathcal F|_U\longrightarrow\mathcal G|_U
$$

is an isomorphism.

<!-- upstream_entity: Flacher Modul/Ringwechsel/Aufgabe -->

## Exercise 16.11 {#br-bgk-2019-w16-ex11}

Let $R$ be a commutative ring, let $M$ be a flat $R$-module, and let $S$ be an $R$-algebra. Prove that $M\otimes_RS$ is a flat $S$-module.

<!-- upstream_entity: Kommutativer Ring/Projektiver Modul/Universell und direkter Summand/Fakt/Beweis/Aufgabe -->

## Exercise 16.12 ★ {#br-bgk-2019-w16-ex12}

Let $R$ be a commutative ring and let $M$ be an $R$-module. Prove that $M$ is a projective module if and only if there is another module $N$ such that the direct sum $M\oplus N$ is free.

<!-- upstream_entity: Produktring/Körper/Projektiver Modul/Aufgabe -->

## Exercise 16.13 {#br-bgk-2019-w16-ex13}

Let $K$ be a field and let $R=K^n$ be the product ring. Prove that every $R$-module $M$ is projective.

<!-- upstream_entity: Kommutativer Ring/Nulldimensional/Nicht projektiv/Aufgabe -->

## Exercise 16.14 {#br-bgk-2019-w16-ex14}

Give an example of an Artinian ring and a finitely generated $R$-module $M$ that is not projective.

<!-- upstream_entity: Z/Q/Nicht projektiv/Aufgabe -->

## Exercise 16.15 {#br-bgk-2019-w16-ex15}

Prove that for the surjective group homomorphism

$$
p:\mathbb Z^{(\mathbb N_+)}\longrightarrow\mathbb Q,
\qquad
e_n\longmapsto\frac1n,
$$

there is no group homomorphism

$$
i:\mathbb Q\longrightarrow\mathbb Z^{(\mathbb N_+)}
$$

with $p\circ i=\operatorname{Id}_{\mathbb Q}$. Deduce that $\mathbb Q$ is not projective as a $\mathbb Z$-module.

<!-- upstream_entity: Projektiver Modul/Nenneraufnahme/Aufgabe -->

## Exercise 16.16 {#br-bgk-2019-w16-ex16}

Let $R$ be a commutative ring, let $M$ be a projective $R$-module, and let $T\subseteq R$ be a multiplicative system. Prove that $M_T$ is a projective $R_T$-module.

<!-- upstream_entity: Projektiver Modul/Ringwechsel/Aufgabe -->

## Exercise 16.17 {#br-bgk-2019-w16-ex17}

Let $R$ be a commutative ring, let $M$ be a projective $R$-module, and let $S$ be an $R$-algebra. Prove that $M\otimes_RS$ is a projective $S$-module.

<!-- upstream_entity: Affines Schema/Syzygienbündel/Explizite Trivialisierungen/Aufgabe -->

## Exercise 16.18 {#br-bgk-2019-w16-ex18}

Let $R$ be a commutative ring and let $f_1,\ldots,f_n\in R$. Let

$$
\mathcal S=\operatorname{Syz}(f_1,\ldots,f_n)
$$

be the corresponding syzygy sheaf on

$$
U=D(f_1,\ldots,f_n)\subseteq\operatorname{Spek}(R).
$$

Give explicit trivialisations of $\mathcal S|_{D(f_i)}$.

<!-- upstream_entity: Projektives Schema/Syzygienbündel/Lokal frei/Aufgabe -->

## Exercise 16.19 {#br-bgk-2019-w16-ex19}

Let $R$ be a $\mathbb Z$-graded ring and let $f_1,\ldots,f_n\in R$ be homogeneous elements of degrees $d_i$. Suppose that the ideal $I$ generated by the $f_i$ and the irrelevant ideal $R_+$ have the same radical. Put $Y=\operatorname{Proj}(R)$, and assume that each twisting sheaf $\mathcal O_Y(-d_i)$ is invertible; this holds, for example, when $R$ is standard graded. Prove the following statements.

1. There is a short exact sequence

   $$
   0\longrightarrow\operatorname{Syz}(f_1,\ldots,f_n)
   \longrightarrow\bigoplus_{i=1}^nR(-d_i)
   \longrightarrow I
   \longrightarrow0
   $$

   of graded $R$-modules with homogeneous homomorphisms.

2. On $Y$ there is a short exact sequence

   $$
   0\longrightarrow\operatorname{Syz}(f_1,\ldots,f_n)
   \longrightarrow\bigoplus_{i=1}^n\mathcal O_Y(-d_i)
   \longrightarrow\mathcal O_Y
   \longrightarrow0
   $$

   of locally free sheaves.

3. On $D_+(f_i)$, the restriction of the locally free sheaf $\operatorname{Syz}(f_1,\ldots,f_n)$ is isomorphic to a direct sum of twisted structure sheaves.

> **Editorial note — the grading hypothesis.** The source assumes only that $R$ is $\mathbb Z$-graded, but under that hypothesis the sheaves $\mathcal O_Y(-d_i)$ need not be invertible, so the sequence in part (2) need not consist of locally free sheaves. This edition states the precise invertibility hypothesis used by parts (2) and (3); standard grading is a familiar sufficient condition.

<!-- upstream_entity: Lokal freie Garbe/Beringter Raum/Determinantengarbe/Invertierbar/Aufgabe -->

## Exercise 16.20 {#br-bgk-2019-w16-ex20}

Let $\mathcal F$ be a locally free sheaf on a ringed space. Prove that its determinant sheaf $\operatorname{Det}F$ is invertible.

<!-- upstream_entity: Lokal freie Garbe/Beringter Raum/Duale Garbe/Determinantengarbe/Aufgabe -->

## Exercise 16.21 {#br-bgk-2019-w16-ex21}

Let $\mathcal F$ be a locally free sheaf on a ringed space, with dual sheaf $\mathcal F^*$. Prove the following relation between their determinant sheaves:

$$
(\operatorname{Det}F)^*
=\operatorname{Det}(F^*).
$$

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Direkte Summe/Invertierbare Garben/Determinantengarbe/Fakt/Beweis/Aufgabe -->

## Exercise 16.22 {#br-bgk-2019-w16-ex22}

Let $(X,\mathcal O_X)$ be a ringed space and let

$$
\mathcal F=\mathcal L_1\oplus\cdots\oplus\mathcal L_r
$$

be a direct sum of invertible sheaves. Prove that

$$
\operatorname{Det}F
\cong\mathcal L_1\otimes\cdots\otimes\mathcal L_r.
$$

<!-- upstream_entity: Projektives Schema/Syzygienbündel/Determinantengarbe/Aufgabe -->

## Exercise 16.23 {#br-bgk-2019-w16-ex23}

Prove that in the situation of Exercise 16.19, the determinant sheaf of the locally free sheaf $\operatorname{Syz}(f_1,\ldots,f_n)$ on $Y=\operatorname{Proj}(R)$ is

$$
\operatorname{Det}(\operatorname{Syz}(f_1,\ldots,f_n))
=\mathcal O_Y\left(-\sum_{i=1}^n d_i\right).
$$
