---
title: "Worksheet 5 - Sheafification and Quotient Sheaves"
stable_id: br-bgk-2019-w05
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 5"
upstream_pageid: 110210
upstream_revid: 619386
upstream_timestamp: "2020-02-17T12:38:11Z"
upstream_mediawiki_sha1: 7ea9208cb3444aa48e23d1acbe66e27672d28d27
source_url: "https://de.wikiversity.org/w/index.php?oldid=619386"
authority_manifest: authority/wikiversity-bgk/unit-05/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 328774ffd66341ba8841b86935037a043067202dd10916d3e0be5082faeac35e
worksheet_xml: authority/wikiversity-bgk/unit-05/worksheet-05.xml
worksheet_xml_sha256: 89e545b88502d4e9f4bd19c8ca79a68cf86a480aca360f4d0c3740589366a7f5
worksheet_expanded_tex: authority/wikiversity-bgk/unit-05/worksheet-05-expanded.tex
worksheet_expanded_tex_sha256: af4235ab3c393b02ad8f081f8f8fb17c24067fa07af63ec7f9bb3f17e1526b86
exercise_map: authority/wikiversity-bgk/unit-05/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: b6bf28ef883ac91c07d0c50526ff655b2bcf7fc1b0d45773f0543092d463cadf
official_pdf: authority/artifacts/bgk-worksheet-05-official.pdf
official_pdf_sha256: 206418f092c563128b3dbf893b8547dc6db727773d4e4ec88e07140886d79113
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 11
public_solution_count: 1
---

# Worksheet 5: Sheafification and Quotient Sheaves {#br-bgk-2019-w05}

<!-- upstream_entity: Prägarbe/Diskretisierung/Aufgabe -->

## Exercise 5.1 {#br-bgk-2019-w05-ex01}

Let $X$ be a topological space and $\mathcal F$ a presheaf on $X$. Show that the assignment

$$
U\longmapsto\prod_{P\in U}\mathcal F_P,
$$

the product of all stalks at points of $U$, together with the natural projections as restriction maps, defines a presheaf. Show also that there is a natural presheaf morphism from $\mathcal F$ to this presheaf.

<!-- upstream_entity: Prägarbe/Vergarbung/Universelle Eigenschaft/Aufgabe -->

## Exercise 5.2 {#br-bgk-2019-w05-ex02}

Let $\mathcal F$ be a presheaf on a topological space $X$, and let $\widetilde{\mathcal F}$ be its sheafification. Show that, for every presheaf morphism

$$
\psi:\mathcal F\longrightarrow\mathcal G
$$

to a sheaf $\mathcal G$, there is a unique factorisation

$$
\widetilde\psi:
\widetilde{\mathcal F}\longrightarrow\mathcal G.
$$

The sheafification of a constant presheaf is called a *locally constant sheaf*, and sometimes simply a *constant sheaf*.

<!-- upstream_entity: Konstante Prägarbe/Vergarbung/Halm/Aufgabe -->

## Exercise 5.3 {#br-bgk-2019-w05-ex03}

Let $\mathcal F$ be the constant presheaf with value a set $M$ on a topological space $X$. Show that the stalk of the sheafification of $\mathcal F$ at every point

$$
P\in X
$$

is equal to $M$.

<!-- upstream_entity: Konstante Prägarbe/Diskrete Gruppe/Vergarbung/Aufgabe -->

## Exercise 5.4 {#br-bgk-2019-w05-ex04}

Let $G$ be a discrete topological group and $X$ a topological space. Let $\mathcal G$ be the constant presheaf with value $G$ on $X$. Show that the sheafification of $\mathcal G$ is equal to

$$
C^0(-,G).
$$

<!-- upstream_entity: Garbe/Untergarbe/Halmweise Zugehörigkeit/Aufgabe -->

## Exercise 5.5* {#br-bgk-2019-w05-ex05}

Let $X$ be a topological space, $\mathcal G$ a sheaf on $X$, and

$$
\mathcal F\subseteq\mathcal G
$$

a subsheaf. Suppose

$$
t\in\Gamma(X,\mathcal G)
$$

satisfies

$$
t_P\in\mathcal F_P
$$

for every

$$
P\in X.
$$

Show that

$$
t\in\Gamma(X,\mathcal F).
$$

<!-- upstream_entity: Garben von Gruppen/Homomorphismus/Kern/Garbe/Aufgabe -->

## Exercise 5.6 {#br-bgk-2019-w05-ex06}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. Show that the assignment

$$
(\ker\varphi)(U):=\ker\varphi_U
$$

defines a sheaf of groups on $X$.

<!-- upstream_entity: Garben von Gruppen/Homomorphismus/Injektiv und Kern/Aufgabe -->

## Exercise 5.7 {#br-bgk-2019-w05-ex07}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. Show that $\varphi$ is injective precisely when

$$
\ker\varphi
$$

is the zero sheaf.

<!-- upstream_entity: Garben von Gruppen/Homomorphismus/Surjektiv und Bild/Aufgabe -->

## Exercise 5.8 {#br-bgk-2019-w05-ex08}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. Show that $\varphi$ is surjective precisely when

$$
\operatorname{im}\varphi=\mathcal G.
$$

<!-- upstream_entity: Garben von Gruppen/Homomorphismus/Bild/Halm/Aufgabe -->

## Exercise 5.9 {#br-bgk-2019-w05-ex09}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. Show that, for every

$$
P\in X,
$$

we have

$$
(\operatorname{im}\varphi)_P
=
\operatorname{im}(\varphi_P).
$$

<!-- upstream_entity: Garben von Gruppen/Untergarbe/Quotientengarbe/Surjektiv/Aufgabe -->

## Exercise 5.10 {#br-bgk-2019-w05-ex10}

Let $\mathcal G$ be a sheaf of commutative groups and

$$
\mathcal F\subseteq\mathcal G
$$

a subsheaf of groups. Show that there is a canonical surjective homomorphism of sheaves of commutative groups

$$
\mathcal G\longrightarrow\mathcal G/\mathcal F.
$$

<!-- upstream_entity: Garben von Gruppen/Untergarbe/Quotientengarbe/Halm/Aufgabe -->

## Exercise 5.11 {#br-bgk-2019-w05-ex11}

Let $\mathcal G$ be a sheaf of commutative groups and

$$
\mathcal F\subseteq\mathcal G
$$

a subsheaf of groups, and let $\mathcal G/\mathcal F$ be their quotient sheaf. Show that

$$
(\mathcal G/\mathcal F)_P
=
\mathcal G_P/\mathcal F_P
$$

for every point

$$
P\in X.
$$

