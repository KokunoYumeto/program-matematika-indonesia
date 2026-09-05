---
title: "Worksheet 28 - Projective Varieties and Projective Closure"
stable_id: br-ak-2012-w28
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 28"
upstream_pageid: 50763
upstream_revid: 793497
upstream_timestamp: "2022-08-25T06:04:27Z"
upstream_mediawiki_sha1: 7ee8f07ea803541b23e8e1fa686c7b2c17e6f67a
source_url: "https://de.wikiversity.org/w/index.php?oldid=793497"
authority_manifest: authority/wikiversity/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f2e34fc420c4beec300ea9e0accc52598e12c27f46c9022611996b1b43e29a99
worksheet_xml: authority/wikiversity/unit-28/worksheet-28.xml
worksheet_xml_sha256: dc1af11088dac5f3ae3597a94af6bdba91afe35de35d8c2aecf4d26edd00f4fa
worksheet_expanded_tex: authority/wikiversity/unit-28/worksheet-28-expanded.tex
worksheet_expanded_tex_sha256: 9505f42a5a87139ca3e3dae694dc90b1692b38e0a9e312efa3b9159bbf2bab94
license: "Current semantic course text and this translation: CC BY-SA 4.0. Official PDF and media components retain their recorded component routes."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 14
warm_up_exercises: "1-10"
submitted_exercises: "11-14"
starred_exercises: "10"
displayed_points: "11:3; 12:4; 13:3; 14:3"
public_solution_count: 1
public_solution_exercises: "10"
source_corrections: 3
correction_ids: "AGC-CORR-0121; REVIEW-AK-26-30-C08; REVIEW-AK-26-30-C09"
---

# Worksheet 28 {#br-ak-2012-w28}

## Warm-up exercises {#br-ak-2012-w28-warmup}

<!-- upstream_entity: Projektiver Raum/Für jeden Punkt affine Umgebung, wo Nullpunkt/Aufgabe -->

### Exercise 28.1 {#br-ak-2012-w28-ex01}

Let

$$
P=(a_0,\ldots,a_n)\in\mathbb P_K^n
$$

be a point in projective space. Show that there is an affine open neighbourhood

$$
U\cong\mathbb A_K^n\subset\mathbb P_K^n
$$

such that $P$ corresponds to the origin in this affine space.

<!-- upstream_entity: Projektiver Raum/Zariski Topologie/Einschränkung auf affinen Raum/Aufgabe -->

### Exercise 28.2 {#br-ak-2012-w28-ex02}

Let

$$
D_+(L)\cong\mathbb A_K^n\subseteq\mathbb P_K^n,
$$

where $L$ is a homogeneous linear form in $K[X_0,\ldots,X_n]$. Show that the Zariski topology on projective space induces the Zariski topology on this affine space.

<!-- upstream_entity: Projektive Gerade/Morphismus durch beliebige Potenzen/Aufgabe -->

### Exercise 28.3 {#br-ak-2012-w28-ex03}

For each $n\in\mathbb Z$, define the power map

$$
x\longmapsto x^n
$$

as a morphism from the projective line to itself. What are the fibres of this morphism?

> **Editorial note - all integer exponents.** The source quantifier $n\in\mathbb Z$ is retained. The cases $n=0$, $n<0$, and characteristic dividing $|n|$ must be distinguished; this edition does not silently substitute an assumption of $n>0$ or characteristic zero.

<!-- upstream_entity: Ebene algebraische Kurve/Kardioide/Projektiver Abschluss/Aufgabe -->

### Exercise 28.4 {#br-ak-2012-w28-ex04}

Determine the projective closure of the complex cardioid

$$
V\!\left((X^2+Y^2)^2-2X(X^2+Y^2)-Y^2\right),
$$

and in particular its points at infinity.

<!-- upstream_entity: Projektiver Raum/Kegelabbildung/Ist Morphismus/Aufgabe -->

### Exercise 28.5 {#br-ak-2012-w28-ex05}

Show that the cone map

$$
\mathbb A_K^{n+1}\setminus\{0\}\longrightarrow\mathbb P_K^n
$$

is a morphism of quasiprojective varieties.

<!-- upstream_entity: Projektiver Raum/Kegelabbildung/Ist nicht abgeschlossen/Aufgabe -->

### Exercise 28.6 {#br-ak-2012-w28-ex06}

Give an example showing that the cone map

$$
\mathbb A_K^{n+1}\setminus\{0\}\longrightarrow\mathbb P_K^n
$$

need not be a closed map.

<!-- upstream_entity: Quasiprojektive Varietäten/Offene Überdeckung des Ziels/Kriterium für Morphismus/Aufgabe -->

### Exercise 28.7 {#br-ak-2012-w28-ex07}

Let $X$ and $Y$ be quasiprojective varieties and let $\varphi:X\to Y$ be a continuous map. Let

$$
Y=\bigcup_{i\in I}U_i
$$

be an open cover. Show that $\varphi$ is a morphism if and only if, for every $i$, the restriction

$$
\varphi_i:\varphi^{-1}(U_i)\longrightarrow U_i
$$

is a morphism.

<!-- upstream_entity: Die projektive Gerade/Globaler Schnittring/Aufgabe -->

### Exercise 28.8 {#br-ak-2012-w28-ex08}

Let $K$ be an algebraically closed field. Determine the ring of global sections

$$
\Gamma\!\left(\mathbb P_K^1,\mathcal O_{\mathbb P_K^1}\right).
$$

What does this imply for a morphism

$$
\mathbb P_K^1\longrightarrow\mathbb A_K^1?
$$

> **Source-condition note REVIEW-AK-26-30-C08 - classical base-field convention.** The source says only “field” in Exercises 28.8, 28.10 and 28.14. The structure sheaf used in this chapter was defined in Definition 28.3 over an algebraically closed field; with the source's topology on $K$-points, the asserted closure and global-function conclusions can fail over other fields. This edition keeps all three exercises in that defined setting.

<!-- upstream_entity: Quasiprojektive Varietät/Normal/Definiere/Aufgabe -->

### Exercise 28.9 {#br-ak-2012-w28-ex09}

Define and characterise when an irreducible quasiprojective variety is *normal*.

<!-- upstream_entity: Ebene Kurve/y-x^3+x+2/Rationale Parametrisierung/Fortsetzung auf P^1/Aufgabe -->

### Exercise 28.10 * {#br-ak-2012-w28-ex10}

Let $K$ be an algebraically closed field. Consider the affine plane curve

$$
C=V(Y-X^3+X+2).
$$

Define an isomorphism between $C$ and the affine line $\mathbb A_K^1$. Can such an isomorphism be extended to an isomorphism between $\mathbb P_K^1$ and the projective closure

$$
\overline C\subset\mathbb P_K^2?
$$

## Exercises to submit {#br-ak-2012-w28-submit}

<!-- upstream_entity: Affiner Raum/K ist R oder C/Offene Menge auf Hyperebene und zugehöriger Kegel/Ist offen/Aufgabe -->

### Exercise 28.11 (3 points) {#br-ak-2012-w28-ex11}

Let $\mathbb K=\mathbb R$ or $\mathbb K=\mathbb C$. Let $H\subset\mathbb K^{n+1}$ be an $n$-dimensional affine subspace not containing the origin, and let $\widetilde H$ be the subspace parallel to $H$ through the origin. Let $U\subseteq H$ be open in the metric topology on $H\cong\mathbb K^n$, and let $V$ be the union of all lines through the origin and a point of $U$. Show that

$$
V\cap(\mathbb K^{n+1}\setminus\widetilde H)
$$

is open.

<!-- upstream_entity: Projektiver Raum/Kegelabbildung/Abschluss des Bildes einer abgeschlossenen Menge/Aufgabe -->

### Exercise 28.12 (4 points) {#br-ak-2012-w28-ex12}

For the cone map

$$
\mathbb A_K^{n+1}\setminus\{0\}\longrightarrow\mathbb P_K^n,
$$

determine the Zariski closure in $\mathbb P_K^n$ of the image of the closed set

$$
V(\mathfrak a)\cap(\mathbb A_K^{n+1}\setminus\{0\}).
$$

<!-- upstream_entity: Quasiprojektive Varietät/Integer/Durchschnitt/Aufgabe -->

### Exercise 28.13 (3 points) {#br-ak-2012-w28-ex13}

Let $X$ be an irreducible quasiprojective variety with function field $L=K(X)$. Let $U$ be a nonempty open set, and let $(U_i)_{i\in I}$ be a cover of $U$ by nonempty open sets:

$$
U=\bigcup_{i\in I}U_i.
$$

Show that

$$
\Gamma(U,\mathcal O)
=
\bigcap_{i\in I}\Gamma(U_i,\mathcal O),
$$

where the intersection is taken inside $L$.

> **Source-condition note REVIEW-AK-26-30-C09 - nonempty opens.** The source allows arbitrary open sets. Identifying a section ring with a subring of the function field requires the open set to be nonempty; empty members of a cover must therefore be omitted before taking this intersection.

<!-- upstream_entity: Projektiver Raum/Globale algebraische Funktionen/Sind K/Aufgabe -->

### Exercise 28.14 (3 points) {#br-ak-2012-w28-ex14}

Let $K$ be an algebraically closed field and let $\mathbb P_K^n$ be projective space over $K$. Show that the only global algebraic functions are constants, that is,

$$
\Gamma\!\left(\mathbb P_K^n,\mathcal O_{\mathbb P_K^n}\right)=K.
$$

> **Source remark.** This statement holds for every connected projective variety over an algebraically closed field.
