---
title: "Worksheet 30 - The Riemann–Roch theorem"
stable_id: br-bgk-2019-w30
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 30"
upstream_pageid: 110239
upstream_revid: 991891
upstream_timestamp: "2025-01-23T14:50:11Z"
upstream_mediawiki_sha1: fd0f75147d3f8a494f1238b4cf4b400b35fcc871
source_url: "https://de.wikiversity.org/w/index.php?oldid=991891"
authority_manifest: authority/wikiversity-bgk/unit-30/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 956990c5550c5fa417f3441dc1bb8f093acbdbb8fe1064ae37c384fa17b8fcb0
ordered_exercise_map: authority/wikiversity-bgk/unit-30/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 3bbf65672ab614c8f88caa438f06230328a87849a245447ae3207be682a59ecc
candidate_evidence: authority/wikiversity-bgk/unit-30/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 3ffdcede4d7bb2407ad0028ad3f8e18046b6142814bb7dcfe89dd3551a4b498a
exercise_count: 5
public_solution_count: 0
public_solution_numbers: ""
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-30.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 30: The Riemann–Roch theorem {#br-bgk-2019-w30}

<!-- upstream_entity: Projektive Gerade/Riemann-Roch/Direkt/Aufgabe -->
### Exercise 30.1 {#br-bgk-2019-w30-ex01}

Let $K$ be an algebraically closed field. Prove the Riemann–Roch theorem directly for the projective line $\mathbb P^1_K$.

> **Edition note (source).** The source leaves the base field implicit. The algebraically closed field $K$ required by the version of Riemann–Roch stated in Lecture 30 has been made explicit.

<!-- upstream_entity: Glatte Ebene Kurve/Syzygienbündel/Gradberechnung/Aufgabe -->
### Exercise 30.2 {#br-bgk-2019-w30-ex02}

Let $f\in K[X,Y,Z]$ be a homogeneous polynomial of degree $e$ over an algebraically closed field $K$ such that

$$
C=\operatorname{Proj}(K[X,Y,Z]/(f))\subseteq\mathbb P^2_K
$$

is a smooth projective curve. Let $g_1,\ldots,g_n\in K[X,Y,Z]$ be homogeneous elements of degrees $d_1,\ldots,d_n$ such that the $D_+(g_i)$ cover the curve. Regard $g_i$ as a sheaf homomorphism

$$
\mathcal O_C(-d_i)\longrightarrow\mathcal O_C,
\qquad h\longmapsto hg_i,
$$

or, for $m\in\mathbb Z$,

$$
\mathcal O_C(m-d_i)\longrightarrow\mathcal O_C(m),
\qquad h\longmapsto hg_i.
$$

1. Prove that the sheaf homomorphism
   $$
   \bigoplus_{i=1}^{n}\mathcal O_C(m-d_i)
   \longrightarrow\mathcal O_C(m)
   $$
   is surjective.
2. Let $\operatorname{Syz}(g_1,\ldots,g_n)(m)$ be the kernel sheaf of the homomorphism in part (1). Prove that this sheaf is locally free.
3. Determine the rank of $\operatorname{Syz}(g_1,\ldots,g_n)(m)$.
4. Determine the degree of $\operatorname{Syz}(g_1,\ldots,g_n)(m)$.

<!-- upstream_entity: Projektive Gerade/Rang 2/Grad 0/Schnitte/Aufgabe -->
### Exercise 30.3 {#br-bgk-2019-w30-ex03}

Let $K$ be an algebraically closed field. Give examples on the projective line $\mathbb P^1_K$ of locally free sheaves of rank $2$ and degree $0$ whose spaces of global sections have arbitrarily large dimension.

> **Edition note (source).** The historical source exercise omits the value after “of degree”, whereas the official entity title states `Grad 0`. This edition restores degree $0$ so that the exercise agrees with its entity identity and the frozen semantic content.

> **Edition note (source).** The source uses $K$ in $\mathbb P^1_K$ without declaring it. The algebraically closed base field assumed by the lecture's degree formalism has been stated explicitly.

<!-- upstream_entity: Projektive Ebene/Kotangentialbündel/Einschränkung/Gerade/Aufgabe -->
### Exercise 30.4 {#br-bgk-2019-w30-ex04}

Let $K$ be a field and, as in Theorem 19.8, let

$$
\operatorname{Syz}(x,y,z)\cong\Omega_{\mathbb P^2_K\mid K}
$$

be the cotangent sheaf on the projective plane, and let $L\subseteq\mathbb P^2_K$ be a projective line. Prove

$$
\operatorname{Syz}(x,y,z)|_L
\cong\mathcal O_L(-1)\oplus\mathcal O_L(-2).
$$

> **Edition note (source).** The source uses $K$ without declaring the base field. No algebraic-closure hypothesis is needed for this exercise, so $K$ has been stated to be an arbitrary field.

<!-- upstream_entity: Projektive Ebene/Kotangentialbündel/Einschränkung/Quadrik/Aufgabe -->
### Exercise 30.5 {#br-bgk-2019-w30-ex05}

Let $K$ be an algebraically closed field and, as in Theorem 19.8, let

$$
\operatorname{Syz}(x,y,z)\cong\Omega_{\mathbb P^2_K\mid K}
$$

be the cotangent sheaf on the projective plane, and let $C=V_+(F)\subseteq\mathbb P^2_K$ be a smooth quadric. Prove that $\operatorname{Syz}(x,y,z)|_C$ decomposes as a direct sum of two invertible sheaves. Use an isomorphism $\mathbb P^1_K\cong C$.

> **Edition note (source).** The source leaves $K$ undeclared while instructing the reader to use an isomorphism $\mathbb P^1_K\cong C$. A smooth conic need not have such an isomorphism over an arbitrary field; the algebraically closed hypothesis that guarantees it has therefore been supplied.
