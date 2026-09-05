---
title: "Worksheet 29 - The genus of a curve"
stable_id: br-bgk-2019-w29
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 29"
upstream_pageid: 110238
upstream_revid: 1069438
upstream_timestamp: "2026-02-05T20:36:09Z"
upstream_mediawiki_sha1: fe4fc776bdfd80cb3337cfb807de3168abe73d09
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069438"
authority_manifest: authority/wikiversity-bgk/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 376380a874b545579d61c100d1f66eac11bad854d76f7e586b10cd621e7a54f7
worksheet_xml: authority/wikiversity-bgk/unit-29/worksheet-29.xml
worksheet_xml_sha256: b298ec1566a1a1c1a3ba3bbc2606679ffba8ad2dfe9c8cd3d1269fc0c96e2ce4
worksheet_expanded_tex: authority/wikiversity-bgk/unit-29/worksheet-29-expanded.tex
worksheet_expanded_tex_sha256: 2243dc1483422ccc3747f4d924abf46f29e1d67cd6cd66ed06a3b9587ae79429
official_pdf: authority/artifacts/bgk-worksheet-29-official.pdf
official_pdf_sha256: 112cba176b947010eb3e4ff2123b7b04756f06c579b61bb3826c284cff3533f0
ordered_exercise_map: authority/wikiversity-bgk/unit-29/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 1ee8ba36620cda1bb7b7da82f277d42c0284c0c3858f368d517fc0206c00889c
exercise_count: 15
public_solution_count: 2
public_solution_numbers: "5, 12"
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-29.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 29: The genus of a curve {#br-bgk-2019-w29}

<!-- upstream_entity: Projektive Gerade/Quotient aus Linearformen/Schnitte/Lineare Transformation/Aufgabe -->
### Exercise 29.1 {#br-bgk-2019-w29-ex01}

Prove that the following data or constructions determine the same morphism $\mathbb P^1_K\to\mathbb P^1_K$, where $(a,b),(c,d)\in K^2$ are linearly independent.

1. The morphism induced, as in Theorem 12.11, by the homogeneous ring homomorphism $K[X,Y]\to K[S,T]$ with $X\mapsto aS+bT$ and $Y\mapsto cS+dT$.
2. The morphism of Lemma 28.1 defined by the two sections
   $$
   as+bt,\ cs+dt\in
   \Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K}(1)).
   $$
3. The morphism of Lemma 29.7 defined by the rational function
   $$
   \frac{cs+dt}{as+bt}\in K\!\left(\frac st\right).
   $$

> **Edition note (source).** The source prints the reciprocal rational function. Under the convention $Y/X\mapsto q$ in Lemma 29.7, the first two constructions send $X$ to $as+bt$ and $Y$ to $cs+dt$, so the corresponding rational function is $(cs+dt)/(as+bt)$, as displayed above.

<!-- upstream_entity: Kuspe/Affine Gerade/Keine Fortsetzung/Aufgabe -->
### Exercise 29.2 {#br-bgk-2019-w29-ex02}

Let $K$ be a field. Prove that there is a morphism

$$
V(X^2-Y^3)\supseteq
U=V(X^2-Y^3)\setminus\{(0,0)\}
\longrightarrow\mathbb A^1_K
$$

which cannot be extended to all of $V(X^2-Y^3)$.

> **Edition note (source).** The source leaves the ground field unstated and prints the target with an empty base subscript. The curve and affine line have been placed over an explicit field $K$; no further hypothesis on $K$ is used.

<!-- upstream_entity: Projektion weg vom Punkt/Auf Kurve/Sekanten/Aufgabe -->
### Exercise 29.3 {#br-bgk-2019-w29-ex03}

Let $K$ be a field, let $C\subseteq\mathbb P^2_K$ be a projective plane curve, let $P\in C$, and let

$$
\varphi:C\setminus\{P\}\longrightarrow\mathbb P^1_K
$$

be the morphism defined by projection away from $P$. Thus a point $Q\in C$, $Q\ne P$, maps to the secant line through $Q$ and $P$.

1. Let $K=\mathbb C$ and let $(Q_n)$ be a sequence on $C$ converging to $P$ in the complex topology. Does $\varphi(Q_n)$ converge?
2. Does $\varphi(Q_n)$ have an accumulation point?
3. Let $P$ be a smooth point. Prove that the morphism extends to all of $C$.

<!-- upstream_entity: Projektion weg vom Punkt/Auf Kurve/Sekanten/Achsenkreuz/Aufgabe -->
### Exercise 29.4 {#br-bgk-2019-w29-ex04}

Discuss the situation of Exercise 29.3 for the crossing of axes

$$
V_+(YZ)\subseteq\mathbb P^2_K
$$

and its crossing point $(1,0,0)$.

<!-- upstream_entity: Projektion weg von Punkt/Ebene/Generischer Grad/Aufgabe -->
### Exercise 29.5 ★ {#br-bgk-2019-w29-ex05}

Let $K$ be an algebraically closed field of characteristic $0$, let $C\subseteq\mathbb P^2_K$ be an irreducible projective plane curve of degree $d$, and let

$$
\varphi:C\longrightarrow\mathbb P^1_K
$$

be the morphism given by projection away from a point $P\notin C$. Prove that, with at most finitely many exceptions, the fibre over each $t\in\mathbb P^1_K$ consists of exactly $d$ points.

<!-- upstream_entity: Projektive ebene glatte Kurve/Grad d/Morphismus mit d-1 Faserpunkte/Aufgabe -->
### Exercise 29.6 {#br-bgk-2019-w29-ex06}

Let $K$ be an algebraically closed field and let $C\subseteq\mathbb P^2_K$ be a smooth curve of degree $d\ge2$. Prove that there is a morphism $C\to\mathbb P^1_K$ such that every fibre consists of at most $d-1$ points.

<!-- upstream_entity: Ebene projektive Kurven/Fermat-Kubik auf P^1/2 zu 1/Aufgabe -->
### Exercise 29.7 {#br-bgk-2019-w29-ex07}

Let

$$
C=V_+(X^3+Y^3+Z^3)\subseteq\mathbb P^2_K
$$

be the Fermat cubic over an algebraically closed field of characteristic other than $3$. Describe explicitly a morphism $C\to\mathbb P^1_K$ with at most two points over each point.

<!-- upstream_entity: Glatte projektive Kurve/q nach P^1/Konstante/Transformation/Aufgabe -->
### Exercise 29.8 {#br-bgk-2019-w29-ex08}

Let $C$ be a smooth irreducible projective curve over a field $K$, with function field $Q(C)$, and let $q\in Q(C)$ have associated morphism $q:C\to\mathbb P^1_K$. Let $a\in K$. Prove that there is an automorphism

$$
\theta:\mathbb P^1_K\longrightarrow\mathbb P^1_K
$$

such that the diagram

$$
\begin{CD}
C @>{q}>> \mathbb P^1_K\\
@V{q-a}VV @VV{\theta}V\\
\mathbb P^1_K @= \mathbb P^1_K
\end{CD}
$$

commutes.

> **Edition note (source).** The frozen semantic revision and the official 2020 PDF witness display $Q(C)=$ with an empty right-hand side and use $K$ without first naming it as the ground field. This edition repairs the visible defect to “with function field $Q(C)$” and makes the implicit ground field explicit; it does not impose algebraic closedness here.

<!-- upstream_entity: Glatte projektive Kurve/q nach P^1/Fasern/Linear äquivalent/Aufgabe -->
### Exercise 29.9 {#br-bgk-2019-w29-ex09}

Let $C$ be a smooth irreducible projective curve over an algebraically closed field $K$, and let $q\in Q(C)$ be nonconstant with associated morphism $q:C\to\mathbb P^1_K$. Prove that, as $P$ ranges over $\mathbb P^1_K$, the pullback divisors $q^*(P)$ are linearly equivalent to one another. Use Exercise 29.8.

> **Edition note (source).** The frozen source says only “over an algebraically closed field” but then writes $\mathbb P^1_K$. The field has been named $K$ above so that the base in the target is bound.

<!-- upstream_entity: Projektive Gerade/t^n/Divisor/Aufgabe -->
### Exercise 29.10 {#br-bgk-2019-w29-ex10}

Let $\mathbb P^1_K=\operatorname{Proj}(K[X,Y])$ have function field $K(t)$, with $t=Y/X$. Describe the associated morphism of schemes

$$
\mathbb P^1_K\longrightarrow\mathbb P^1_K,
\qquad t\longmapsto t^n,
$$

for $n\in\mathbb N_+$. What is the inverse image of zero? What is the inverse image of the point at infinity? What are the ramification orders?

<!-- upstream_entity: Projektive Gerade/Polynom/Verzweigungsordnung im Unendlichen/Aufgabe -->
### Exercise 29.11 {#br-bgk-2019-w29-ex11}

Let $\mathbb P^1_K=\operatorname{Proj}(K[X,Y])$ have function field $K(t)$, with $t=Y/X$, and let $P\in K[t]$ be a polynomial of degree $e\ge1$. Describe the ramification order at $\infty$ of the associated morphism of schemes

$$
\mathbb P^1_K\longrightarrow\mathbb P^1_K,
\qquad t\longmapsto P.
$$

<!-- upstream_entity: Projektive Gerade/Rationale Funktion/u+u invers/Aufgabe -->
### Exercise 29.12 ★ {#br-bgk-2019-w29-ex12}

Let $\mathbb P^1_K=\operatorname{Proj}(K[X,Y])$ and $\mathbb P^1_K=\operatorname{Proj}(K[W,Z])$ be two projective lines with function fields $K(t)$, $t=Y/X$, and $K(u)$, $u=Z/W$, over an algebraically closed field $K$ of characteristic other than $2$. On the second projective line, consider the linear system given by

$$
WZ,\ W^2+Z^2\in
\Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K}(2))
$$

with associated map

$$
\varphi:\mathbb P^1_K\longrightarrow\mathbb P^1_K,
\qquad (w,z)\longmapsto(wz,w^2+z^2).
$$

1. Is this linear system complete?
2. Determine the inverse images of $D_+(X)$ and $D_+(Y)$, and describe the induced maps between the affine open subsets.
3. Is this linear system base-point-free?
4. Describe the associated extension of function fields $K(t)\subseteq K(u)$. What is its degree?
5. For each $(x,y)\in\mathbb P^1_K$, determine its inverse image under $\varphi$ and the respective ramification orders.
6. Describe the pullback divisor $\varphi^*(0-\infty)=\varphi^*((Y)-(X))$.

<!-- upstream_entity: Normales integres Schema/Rationale Funktion/Morphismus/Aufgabe -->
### Exercise 29.13 {#br-bgk-2019-w29-ex13}

Let $X$ be a normal Noetherian integral scheme over a field $K$, and let $q\in Q(X)$. Prove that $q$ defines a morphism

$$
q:U\longrightarrow\mathbb P^1_K
$$

on an open set $U\subseteq X$ such that $X\setminus U$ has codimension at least $2$.

> **Edition note (source).** The frozen source writes the target as $\mathbb P^1$ although $X$ is a scheme over the named field $K$. The base subscript has been supplied above.

<!-- upstream_entity: Glatte projektive Kurve/Invertierbare Garbe/Negativer Grad/Schnitte/Aufgabe -->
### Exercise 29.14 {#br-bgk-2019-w29-ex14}

Let $\mathcal L$ be an invertible sheaf of negative degree on a smooth irreducible projective curve $C$ over an algebraically closed field. Prove

$$
\Gamma(C,\mathcal L)=0.
$$

<!-- upstream_entity: Glatte projektive Kurve/Invertierbare Garbe/Tensorierung/Grad/Aufgabe -->
### Exercise 29.15 {#br-bgk-2019-w29-ex15}

Prove that, for a smooth projective curve $C$ over an algebraically closed field, the degree of invertible sheaves gives a surjective group homomorphism

$$
\operatorname{Pic}(C)\longrightarrow\mathbb Z,
\qquad\mathcal L\longmapsto\deg(\mathcal L).
$$
