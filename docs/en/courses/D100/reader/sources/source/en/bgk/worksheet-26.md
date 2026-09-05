---
title: "Worksheet 26 - Čech cohomology"
stable_id: br-bgk-2019-w26
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 26"
upstream_pageid: 110235
upstream_revid: 619292
upstream_timestamp: "2020-02-17T10:05:10Z"
upstream_mediawiki_sha1: 1d06dfb2baf64dec2ba57276ae62c90a99d239e1
source_url: "https://de.wikiversity.org/w/index.php?oldid=619292"
worksheet_xml: authority/wikiversity-bgk/unit-26/worksheet-26.xml
worksheet_xml_sha256: a1237075d1c6c2e9c640cd70db62b1cc189dd3c2b76c8094c6803353fa8b0249
worksheet_expanded_tex: authority/wikiversity-bgk/unit-26/worksheet-26-expanded.tex
worksheet_expanded_tex_sha256: 38f0c59409cde291c78bdf19cafe7ce406c9d9f35ee37a6ab84524543b56fe72
ordered_exercise_map: authority/wikiversity-bgk/unit-26/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: cfe90a0669c135507097265ba5f5b392fe82d2fcf074d94110d3733fe0f53cc3
candidate_evidence: authority/wikiversity-bgk/unit-26/worksheet-solution-candidates-api.json
candidate_evidence_sha256: db25b84749b9fcc9805ac6fd43f72519ef208a989ed45be7ed5b3361c7fe935b
official_pdf_metadata: authority/wikiversity-bgk/unit-26/official-pdfs-api.json
official_pdf_metadata_sha256: c209d22600d20ebfe6f1479b1b6a9a0f20295711dab60905e6d35039c3ca6262
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_bytes: 2104862
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "231-232"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
exercise_count: 8
public_solution_count: 0
public_solution_numbers: ""
negative_public_solution_count: 8
negative_solution_numbers: "1-8"
media_credits: source/id-ID/media-credits-bgk-unit-26.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain the recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
authority_manifest: authority/wikiversity-bgk/unit-26/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7ed3c9a3a480daeb4332e9de8ff2251e43d3a43845df5744ef16aabac5f2c6b4
authority_manifest_status: "Complete terminal authority freeze; all 29 file records have been rehashed without mismatches."
official_pdf: authority/artifacts/bgk-worksheet-26-official.pdf
official_pdf_sha256: 082b40cf5174191581ab19561d7080a2519c1ddc67a2546e0ff4572e91227499
official_pdf_source_bytes: 42483
official_pdf_source_sha1: 9fc70f7c9c14609c747d19c3f6142cdc6ea47f5b
official_pdf_status: "Local official PDF witness; byte identity, SHA-256, upload SHA-1, and component rights notices have been verified."
asset_closure: authority/ASSET_CLOSURE-bgk-unit-26.json
asset_closure_sha256: e9c1c7cf41349d4ae9d66f2e04cb9a214e5b453f41f536832a2af4103d55c1e3
media_rights: authority/RIGHTS-bgk-unit-26.csv
media_rights_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
media_credits_sha256: 3cfc1664f010b72c0ac540cbd35b74412a434788662fdc7c0f2a4cfe49abdcba
---

# Worksheet 26: Čech cohomology {#br-bgk-2019-w26}

None of the eight exercises has a public solution at the frozen revision boundary. This edition does not create new solutions.

<!-- upstream_entity: Spektrum/Z/Garbe/Nichttriviale Kohomologie/Aufgabe -->

## Exercise 26.1 {#br-bgk-2019-w26-ex01}

Define a sheaf on $\operatorname{Spek}(\mathbb Z)$ with nontrivial first cohomology.

<!-- upstream_entity: Cech-Kohomologie/0/Globale Auswertung/Aufgabe -->

## Exercise 26.2 {#br-bgk-2019-w26-ex02}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$, and let $\mathcal G$ be a sheaf of commutative groups on $X$. Prove that

$$
\check H^0(U_i,\ i\in I,\ \mathcal G)=\Gamma(X,\mathcal G).
$$

<!-- upstream_entity: Cech-Kohomologie/Eine Komponente/Bild/Aufgabe -->

## Exercise 26.3 {#br-bgk-2019-w26-ex03}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$, and let $\mathcal G$ be a sheaf of commutative groups on $X$. Let

$$
s\in\check C^k(U_i,\mathcal G)
$$

be a Čech cocycle which, for a particular

$$
J=\{i_0,i_1,\ldots,i_k\}\subseteq I
$$

has value

$$
a\in\Gamma(U_J,\mathcal G),
$$

and has value $0$ on all other $(k+1)$-element subsets $J'\ne J$. Determine

$$
\delta(s)\in\check C^{k+1}(U_i,\mathcal G).
$$

Edition note: the frozen source calls $s$ a cocycle, not an arbitrary cochain. That hypothesis is retained; it restricts which single-component tuples are admissible. This note does not supply a source solution.

<!-- upstream_entity: Projektive Gerade/Einheitengarbe/Erste Kohomologie/Endlicher Raum/Vergleich/Aufgabe -->

## Exercise 26.4 {#br-bgk-2019-w26-ex04}

Let $K$ be a field and let

$$
\mathbb P_K^1=\operatorname{Proj}(K[X,Y])
$$

be the projective line over $K$. Determine the first Čech cohomology

$$
\check H^1\!\left(D_+(X),D_+(Y),\mathcal O_{\mathbb P_K^1}^{\times}\right).
$$

How does this relate to Example 26.1?

<!-- upstream_entity: Cech-Kohomologie/Abgeleitete Kohomologie/Endliche azyklische Überdeckung/Übereinstimmung/Details/Aufgabe -->

## Exercise 26.5 {#br-bgk-2019-w26-ex05}

Prove that the assignment in the proof of Lemma 26.8, which associates to a section

$$
t\in\Gamma(X,\mathcal H),
$$

a Čech cohomology class for $\mathcal F$, is independent of the chosen local representatives in $\mathcal I$ and is a group homomorphism.

<!-- upstream_entity: Irreduzibler Raum/Konstante Garbe/Cech-Kohomologie/Aufgabe -->

## Exercise 26.6 {#br-bgk-2019-w26-ex06}

Let $X$ be an irreducible topological space and let $\mathcal G$ be the constant sheaf associated with a commutative group $G$. Determine the Čech complex and Čech cohomology of $\mathcal G$ for a finite open cover

$$
X=\bigcup_{i\in I}U_i.
$$

<!-- upstream_entity: Beringter Raum/Modul/Cech-Komplex und Kohomologie/Modul/Aufgabe -->

## Exercise 26.7 {#br-bgk-2019-w26-ex07}

Let $(X,\mathcal O_X)$ be a ringed space, let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover, and let $\mathcal F$ be an $\mathcal O_X$-module. Prove that the Čech complex of $\mathcal F$ for this cover is a complex of $\Gamma(X,\mathcal O_X)$-modules, and hence that the corresponding Čech cohomology groups are also $\Gamma(X,\mathcal O_X)$-modules.

<!-- upstream_entity: Affines Schema/Zweierüberdeckung/Strukturgabe/Cech-Kohomologie/Aufgabe -->

## Exercise 26.8 {#br-bgk-2019-w26-ex08}

Let $R$ be a commutative ring and let

$$
X=\operatorname{Spek}(R)=D(f)\cup D(g)
$$

with $f,g\in R$. Prove that

$$
\check H^1(\{D(f),D(g)\},\mathcal O_X)=0.
$$
