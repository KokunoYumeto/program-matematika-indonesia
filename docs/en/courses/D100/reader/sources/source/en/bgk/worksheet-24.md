---
title: "Worksheet 24 - Right Derived Functors"
stable_id: br-bgk-2019-w24
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 24"
upstream_pageid: 110232
upstream_revid: 991890
upstream_timestamp: "2025-01-23T14:50:01Z"
upstream_mediawiki_sha1: 267b9d5873c17927e9a9b7beb9f1813c9457b401
source_url: "https://de.wikiversity.org/w/index.php?oldid=991890"
authority_capture_identity: authority/wikiversity-bgk/unit-24/CAPTURE_IDENTITY.json
authority_capture_identity_sha256: 842c6963306e8d2f624a632554364d970b2d021300974752b7337b8e70b6f1f8
worksheet_xml: authority/wikiversity-bgk/unit-24/worksheet-24.xml
worksheet_xml_sha256: 161d18638b2b70fe8b5adf830fe0bd0f7fba8871a92c85db78688a9e7371e3bc
worksheet_expanded_tex: authority/wikiversity-bgk/unit-24/worksheet-24-expanded.tex
worksheet_expanded_tex_sha256: 666884df00892d3abd5971f56207c83f6de3ecef34dd9b196100ee56bd38a94b
official_pdf_inventory: authority/wikiversity-bgk/unit-24/official-pdfs-api.json
official_pdf_inventory_sha256: 303704d2786c8c83db4a4d3ee5104de5078c240f9245257d25437ec40f812bee
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "214-215"
ordered_exercise_map: authority/wikiversity-bgk/unit-24/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 3813f5740b62adf17ac60ee082465511407366955148ff46e77d0a13379ad02f
exercise_count: 5
public_solution_count: 0
public_solution_numbers: "none"
media_credits: source/id-ID/media-credits-bgk-unit-24.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. This edition does not extend the rights in the PDFs or any of their components."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
authority_manifest: authority/wikiversity-bgk/unit-24/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b938d6366fb91058f9e35b1b3b7c4ba255f5f53a7860f9f0dc2b905f732b263b
official_pdf: authority/artifacts/bgk-worksheet-24-official.pdf
official_pdf_sha256: 38586fce4aaeb057584f01f781a3972fdd71648e8baacc7eaaf350869fce8981
component_metadata: authority/commons-imageinfo-bgk-unit-24.json
component_metadata_sha256: 9b595f13f72a9416a587b97aa694b5655c538fa88ffbc69b54508da64c394f97
rights_ledger: authority/RIGHTS-bgk-unit-24.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-24.json
asset_closure_sha256: 1583dbc371fb9c97b43346d27b50e1e733424d89c4972cc1e6171e5c258c019b
media_credits_sha256: f3db5e0d70186a875db9c554930417bec4413b763f0cd4061f09a577288f440a
---

# Worksheet 24: Right Derived Functors {#br-bgk-2019-w24}

At the frozen revision boundary, all five exercises have negative candidate
results: there are no public solution pages. This worksheet therefore
uses no stars, and this edition does not invent new solutions.

<!-- upstream_entity: Modul/Homomorphismenmodul/Kovariant/Linksexakt/Aufgabe -->

## Exercise 24.1 {#br-bgk-2019-w24-ex01}

Let $R$ be a commutative ring and $A$ an $R$-module. Let

$$
0\longrightarrow L\longrightarrow M\longrightarrow N\longrightarrow0
$$

be a short exact sequence of $R$-modules. Show that

$$
0\longrightarrow\operatorname{Hom}(A,L)
\longrightarrow\operatorname{Hom}(A,M)
\longrightarrow\operatorname{Hom}(A,N)
$$

is exact.

<!-- upstream_entity: Modul/Homomorphismenmodul/Kovariant/Nicht rechtsexakt/Aufgabe -->

## Exercise 24.2 {#br-bgk-2019-w24-ex02}

Let $R$ be a commutative ring and $A$ an $R$-module. Let
$M\longrightarrow N$ be a surjective $R$-module homomorphism.
Show that the induced map

$$
\operatorname{Hom}(A,M)\longrightarrow\operatorname{Hom}(A,N)
$$

need not be surjective.

Consider $A=N=\mathbb Z/(k)$.

<!-- upstream_entity: Projektiver Modul/Extmoduln/Aufgabe -->

## Exercise 24.3 {#br-bgk-2019-w24-ex03}

Let $R$ be a commutative ring, $P$ a projective $R$-module, and
$M$ another $R$-module. Show that

$$
\operatorname{Ext}^n(P,M)=0
$$

for $n\geq1$.

<!-- upstream_entity: Extmodul/1/Z mod k und Z/Nicht 0/Aufgabe -->

## Exercise 24.4 {#br-bgk-2019-w24-ex04}

Using the short exact sequence

$$
0\longrightarrow\mathbb Z
\overset{\cdot k}{\longrightarrow}\mathbb Z
\longrightarrow\mathbb Z/(k)\longrightarrow0,
$$

show that

$$
\operatorname{Ext}^1(\mathbb Z/(k),\mathbb Z)
$$

is not the zero module for $k\geq2$.

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Rechtsabgeleiteter Funktor/Delta-Eigenschaften/Verträglichkeit von Delta/Aufgabe -->

## Exercise 24.5 {#br-bgk-2019-w24-ex05}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let
$F:\mathcal A\longrightarrow\mathcal B$ be a covariant, additive,
left exact functor, and let $R^nF$ denote its right derived functors.
Show that for a homomorphism of exact sequences

$$
\begin{matrix}
0&\longrightarrow&A&\longrightarrow&B&\longrightarrow&C&\longrightarrow&0\\
\downarrow&&\downarrow&&\downarrow&&\downarrow&&\downarrow\\
0&\longrightarrow&A'&\longrightarrow&B'&\longrightarrow&C'&\longrightarrow&0,
\end{matrix}
$$

the diagram

$$
\begin{matrix}
R^nF(C)&\overset{\delta^n}{\longrightarrow}&R^{n+1}F(A)\\
\downarrow&&\downarrow\\
R^nF(C')&\overset{\delta^n}{\longrightarrow}&R^{n+1}F(A')
\end{matrix}
$$

commutes.

