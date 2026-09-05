---
title: "Worksheet 29 - Projections and Parametrised Projective Curves"
stable_id: br-ak-2012-w29
language: en
source_course: "Kurs:Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 29"
upstream_pageid: 50924
upstream_revid: 1052757
upstream_timestamp: "2025-08-27T18:11:31Z"
upstream_mediawiki_sha1: 0e8dd5d1e5b9bf9552bdbd8f8c61c47ee2a0b726
source_url: "https://de.wikiversity.org/w/index.php?oldid=1052757"
authority_manifest: authority/wikiversity/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ec3b34ad387ae827ecaa365c4def3b0550f74b629d0db3873a7cc28dc0831bc5
worksheet_xml: authority/wikiversity/unit-29/worksheet-29.xml
worksheet_xml_sha256: d82d020fef6e0d4f604bda9807f1befa2b8e1392afd9fb9459dbe17461d34574
worksheet_expanded_tex: authority/wikiversity/unit-29/worksheet-29-expanded.tex
worksheet_expanded_tex_sha256: 53a54b5b7e59be71c94d41dc791021c0b2d6165bf0b489670800b09387d560d2
exercise_map: authority/wikiversity/unit-29/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 75b07cabcb83cc12a6fd1259017f7e169c0ded461e7b7c94e65f033b71d12bc9
license: "Current semantic course text and this translation: CC BY-SA 4.0. Official PDF and media components retain their recorded component routes."
component_rights:
  - path: authority/assets/Lemniscate_of_Bernoulli.svg
    creator: "Zorgit"
    license: "Public domain"
  - path: authority/assets/Tschirnhausen_cubic-500.png
    creator: "Oleg Alexandrov"
    license: "Public domain"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 10
warm_up_exercises: "1-5"
submitted_exercises: "6-10"
authored_points: "1:2; 2:4; 3:3; 4:3; 5:4; 6:3; 7:3; 8:3; 9:3; 10:5"
starred_exercises: "2, 3"
displayed_points: "6:3; 7:3; 8:3; 9:3; 10:5"
public_solution_count: 2
public_solution_exercises: "2, 3"
source_corrections: 2
correction_ids: "REVIEW-AK-26-30-C17; REVIEW-AK-26-30-C18"
source_discrepancies: 1
discrepancy_ids: "AGC-U29-SRC-002"
component_discrepancies: 1
reader_media_positions: 2
---

# Worksheet 29 {#br-ak-2012-w29}

## Warm-up exercises {#br-ak-2012-w29-warmup}

<!-- upstream_entity: Projektive ebene Kurve/Schnitt mit projektiver Geraden/Algebraisch abgeschlossen/Nicht leer/Aufgabe -->

### Exercise 29.1 {#br-ak-2012-w29-ex01}

Let $K$ be an algebraically closed field. Show that every projective plane curve has nonempty intersection with every projective line in the projective plane.

<!-- upstream_entity: Ebene algebraische Kurven/Z mod 5/Einheitskreis und x^3-2y^2+3/Durchschnitt und unendlich ferne Punkte/Aufgabe -->

### Exercise 29.2 * {#br-ak-2012-w29-ex02}

Let

$$
K=\mathbb Z/(5),
$$

and consider the two affine plane algebraic curves

$$
C=V(X^2+Y^2-1)
\qquad\text{and}\qquad
D=V(X^3-2Y^2+3).
$$

a. Determine the intersection $C\cap D$.

b. Determine the points in

$$
V_+(X^2+Y^2-Z^2)\setminus V(X^2+Y^2-1).
$$

c. Determine the points in

$$
V_+(X^3-2Y^2Z+3Z^3)\setminus V(X^3-2Y^2+3).
$$

d. Is $V_+(X^2+Y^2-Z^2)$ the projective closure of $V(X^2+Y^2-1)$?

<!-- upstream_entity: Projektive Gerade/K-Punkte/Lokale Ringe isomorph/Aufgabe -->

### Exercise 29.3 * {#br-ak-2012-w29-ex03}

Let $K$ be a field. Show that the local rings of the projective line $\mathbb P_K^1$ at all its $K$-rational points are isomorphic to one another. Give the simplest possible description of this ring.

> **Source-convention note REVIEW-AK-26-30-C17 - $K$-rational points.** The frozen source-page identity explicitly says “$K$-points”, although the exercise body says only “all local rings”. The restriction is essential: scheme-theoretic points of $\mathbb P_K^1$ include the generic point, whose local ring is not isomorphic to the local ring at a $K$-rational closed point.

![Bernoulli’s lemniscate. By Zorgit, public domain.](authority/assets/Lemniscate_of_Bernoulli.svg){fig-alt="Bernoulli’s lemniscate in the shape of a horizontal figure eight"}

<!-- upstream_entity: Lemniskate/Projektive Punkte/Aufgabe -->

### Exercise 29.4 {#br-ak-2012-w29-ex04}

For Bernoulli's lemniscate given by

$$
V\!\left((X^2+Y^2)^2-X^2+Y^2\right),
$$

determine its singularities and its points at infinity in $\mathbb P_{\mathbb C}^2$. Compute the multiplicity and tangent lines at all these points.

<!-- upstream_entity: Algebraische Kurve/ZX^2 ist Y^3/Charakteristik null/Singuläre Punkte und Parametrisierung/Aufgabe -->

### Exercise 29.5 {#br-ak-2012-w29-ex05}

Consider the projective curve

$$
C\subset\mathbb P_K^2
$$

over a field $K$ of characteristic $0$, given by the homogeneous equation

$$
ZX^2=Y^3.
$$

a. Determine the singular points of the curve.

b. Show that the assignment

$$
\varphi:(S,T)\longmapsto(T^3,ST^2,S^3)=(X,Y,Z)
$$

gives a well-defined map

$$
\varphi:\mathbb P^1\longrightarrow\mathbb P^2.
$$

c. Show that the image points of $\varphi$ lie on the curve $C$.

d. Which points in $\mathbb P^1$ correspond to the singular points of $C$?

## Exercises to submit {#br-ak-2012-w29-submit}

<!-- upstream_entity: Projektive Abbildung/Morphismus durch homogenen Polynome vom gleichen Grad/Auf offener Menge/Aufgabe -->

### Exercise 29.6 (3 points) {#br-ak-2012-w29-ex06}

Let $m+1$ homogeneous polynomials

$$
F_0,\ldots,F_m
$$

in $n+1$ variables be given, all of the same degree $d$. Show that there is an open set

$$
U\subseteq\mathbb P_K^n
$$

on which these polynomials define a morphism

$$
\mathbb P_K^n\supseteq U\longrightarrow\mathbb P_K^m.
$$

<!-- upstream_entity: Projektiver Raum/Projektion weg von beliebigem Punkt/Matrixbeschreibung/Aufgabe -->

### Exercise 29.7 (3 points) {#br-ak-2012-w29-ex07}

Let

$$
P=(a_0,\ldots,a_n)\in\mathbb P_K^n
$$

be a point in projective space. Show that projection from $\mathbb P_K^n$ to $\mathbb P_K^{n-1}$ with centre $P$ is given by a matrix. The source does not supply that matrix. It then displays the map

$$
\begin{pmatrix}
x_0\\
x_1\\
\vdots\\
x_n
\end{pmatrix}
\longmapsto
\begin{pmatrix}
x_0\\
x_1\\
\vdots\\
x_n
\end{pmatrix}.
$$

> **Source discrepancy AGC-U29-SRC-002.** The matrix block in the source is blank, and the subsequent vector is repeated unchanged, so it does not describe a projection to $\mathbb P_K^{n-1}$. This edition preserves both facts and does not guess the intended matrix or map.

!["Tschirnhausen cubic" according to the course’s inline caption. By Oleg Alexandrov, public domain.](authority/assets/Tschirnhausen_cubic-500.png){fig-alt="Red illustration of a plane cubic curve with a double point"}

> **Media component note.** The Commons description page for this file warns that, despite its filename, the curve in the image is not a Tschirnhausen cubic because the angle of intersection at its double point differs. The image actually used by the source is retained.

<!-- upstream_entity: Tschirnhausen Kubik/Projektive Punkte/Aufgabe -->

### Exercise 29.8 (3 points) {#br-ak-2012-w29-ex08}

For the Tschirnhausen cubic given by

$$
V(X^3+3X^2-Y^2),
$$

determine its singularities, including points at infinity. Determine the tangent lines at the singularities and at the points at infinity.

<!-- upstream_entity: Kartesisches Blatt/Projektive Punkte/Aufgabe -->

### Exercise 29.9 (3 points) {#br-ak-2012-w29-ex09}

For the folium of Descartes defined by

$$
V(X^3+Y^3-3XY),
$$

determine its points at infinity in $\mathbb P_{\mathbb C}^2$, and compute the multiplicity and tangent lines at those points.

<!-- upstream_entity: Lemniskate von Bernoulli/Projektiv/Abbildung auf Quadrik/Aufgabe -->

### Exercise 29.10 (5 points) {#br-ak-2012-w29-ex10}

Let $K$ be an algebraically closed field of characteristic different from $2$. For the projective Bernoulli lemniscate

$$
V_+\!\left((X^2+Y^2)^2-Z^2X^2+Z^2Y^2\right)
\subset\mathbb P_K^2,
$$

give a surjective morphism to a projective conic. How many points of the lemniscate map to a single point of the conic?

> **Source-condition note REVIEW-AK-26-30-C18 - base field.** The source supplies no restriction on $K$. Algebraic closure is needed for the intended pointwise surjectivity, while in characteristic $2$ the conic obtained from the standard squared-coordinate construction degenerates and its fibre count changes. The stated hypotheses preserve the intended smooth-conic problem.
