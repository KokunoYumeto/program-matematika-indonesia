---
title: "Worksheet 30 - Bézout's Theorem"
stable_id: br-ak-2012-w30
language: en
source_course: "Kurs:Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 30"
upstream_pageid: 50925
upstream_revid: 1112597
upstream_timestamp: "2026-08-21T16:19:24Z"
upstream_mediawiki_sha1: 2111599a8a79cbd491a5f334baf54bb39e9af931
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112597"
authority_manifest: authority/wikiversity/unit-30/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b990783fda97e721cc415740671e75c749400c408481ab88f4afd68f286d8b8a
worksheet_xml: authority/wikiversity/unit-30/worksheet-30.xml
worksheet_xml_sha256: 0525c13b64a201759a6982c6f8885cc3fe456fb23abbd1be9ad1e1e6cc780382
worksheet_expanded_tex: authority/wikiversity/unit-30/worksheet-30-expanded.tex
worksheet_expanded_tex_sha256: c32bea5c89b6606a5171f79958a1dccded6575c4cca1ff4ca154fe5961800966
exercise_map: authority/wikiversity/unit-30/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 7b6ed646202784b0ae03782e76e751336516d2dda0ed17ecf70500ea2d7a491e
license: "Current semantic course text and this translation: CC BY-SA 4.0. Official PDF components retain their recorded component routes."
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 12
warm_up_exercises: "1-4"
submitted_exercises: "5-12"
authored_points: "1:3; 2:3; 3:4; 4:7; 5:6; 6:5; 7:5; 8:4; 9:4; 10:4; 11:4; 12:5"
starred_exercises: "3, 4"
displayed_points: "5:6; 6:5; 7:5; 8:4; 9:4; 10:4; 11:4; 12:5"
displayed_points_total: 37
public_solution_count: 2
public_solution_exercises: "3, 4"
source_corrections: 2
correction_ids: "AGC-CORR-0133; REVIEW-AK-26-30-C19"
source_discrepancies: 1
discrepancy_ids: "AGC-U30-SRC-001"
reader_media_positions: 0
---

# Worksheet 30: Bézout's Theorem {#br-ak-2012-w30}

## Warm-up exercises {#br-ak-2012-w30-warmup}

<!-- upstream_entity: Schnitttheorie von Kurven/Satz von Bézout/Injektivität der Multiplikation mit Z im homogenen Restklassenring/Beispiel bei nicht algebraisch abgeschlossen/Aufgabe -->

### Exercise 30.1 {#br-ak-2012-w30-ex01}

Give an example showing that Lemma 30.2 fails if the assumption that the base field is algebraically closed is omitted.

<!-- upstream_entity: Satz von Bézout/ZY^2-X^3 und (X-Z)^2+Y^2-1/Beispiel/Transversaler Schnitt/Aufgabe -->

### Exercise 30.2 {#br-ak-2012-w30-ex02}

Show that the two curves in Example 30.6 intersect transversely at every computed intersection point other than $(0,0)$.

<!-- upstream_entity: Ebene Kurven/Schnitt und Schnittmultiplizität/Y ist X^3 und Y^2 ist X^3/Aufgabe -->

### Exercise 30.3 * {#br-ak-2012-w30-ex03}

Let $K=\mathbb C$. For the two affine curves

$$
V(Y-X^3)
\qquad\text{and}\qquad
V(Y^2-X^3),
$$

determine all their intersection points and the intersection multiplicity at each point. Also examine intersection points in $\mathbb P_{\mathbb C}^2$ and verify Bézout's Theorem in this example.

<!-- upstream_entity: Ebene Kurven/Schnitt und Schnittmultiplizität/Y ist X^2 und Y^2 ist X^5/Aufgabe -->

### Exercise 30.4 * {#br-ak-2012-w30-ex04}

Let $K=\mathbb C$. Consider the two plane algebraic curves

$$
C=V(X-Y^2)
\qquad\text{and}\qquad
D=V(Y^2-X^5).
$$

Determine all intersection points of the two curves in the affine plane and compute the intersection multiplicity at each. Also determine the points at infinity of both curves, namely the additional points on the projective closures $\overline C$ and $\overline D$, and check for intersections at infinity. Finally, verify Bézout's Theorem in this example.

> **Source discrepancy AGC-U30-SRC-001.** The semantic source-page title names the first curve as “$Y=X^2$”, whereas the formula displayed in both the exercise and the source solution is $X=Y^2$. This edition follows the formula actually displayed and does not alter the frozen source-page identity.

## Exercises to submit {#br-ak-2012-w30-submit}

<!-- upstream_entity: Projektive Kurve/Parametrisierung einer glatten Quadrik/Aufgabe -->

### Exercise 30.5 (6 points) {#br-ak-2012-w30-ex05}

Let

$$
C\subseteq\mathbb P_K^2
$$

be a smooth conic, that is, a curve of degree two, over an algebraically closed field. Show that $C$ is isomorphic to the projective line $\mathbb P_K^1$.

<!-- upstream_entity: Projektive ebene glatte Kurve/Grad d/Morphismus mit d-1 Faserpunkte/Aufgabe -->

### Exercise 30.6 (5 points) {#br-ak-2012-w30-ex06}

Let $K$ be an algebraically closed field and let

$$
C\subset\mathbb P_K^2
$$

be a smooth curve of degree $d\geq2$. Show that there is a morphism

$$
C\longrightarrow\mathbb P_K^1
$$

such that each fibre consists of at most $d-1$ points.

<!-- upstream_entity: Ebene projektive Kurven/Fermat-Kubik auf P^1/2 zu 1/Aufgabe -->

### Exercise 30.7 (5 points) {#br-ak-2012-w30-ex07}

Let

$$
C=V_+(X^3+Y^3+Z^3)\subseteq\mathbb P_K^2
$$

be the Fermat cubic over an algebraically closed field of characteristic different from $3$. Describe explicitly a morphism

$$
C\longrightarrow\mathbb P_K^1
$$

whose fibres each contain at most two points.

<!-- upstream_entity: Der komplex-projektive Einheitskreis/Explizite bijektive Parametrisierung/Aufgabe -->

### Exercise 30.8 (4 points) {#br-ak-2012-w30-ex08}

Let

$$
C\subseteq\mathbb P_{\mathbb C}^2
$$

be the complex projective closure of the unit circle. Determine an explicit bijective parametrisation

$$
\mathbb P_{\mathbb C}^1\longrightarrow C.
$$

<!-- upstream_entity: Satz von Bézout/Bestätige für ZY^2-X^3 und X^2+(Y-Z)^2-Z^2/Aufgabe -->

### Exercise 30.9 (4 points) {#br-ak-2012-w30-ex09}

Over $\mathbb C$, verify Bézout's Theorem for the two projective plane curves

$$
C=V_+(ZY^2-X^3)
$$

and

$$
D=V_+\!\left(X^2+(Y-Z)^2-Z^2\right).
$$

Sketch the situation.

<!-- upstream_entity: Satz von Bézout/Bestätige für ZY-X^2 und X^2+(Y-Z)^2-Z^2/Aufgabe -->

### Exercise 30.10 (4 points) {#br-ak-2012-w30-ex10}

Over $\mathbb C$, verify Bézout's Theorem for the two projective plane curves

$$
C=V_+(ZY-X^2)
$$

and

$$
D=V_+\!\left(X^2+(Y-Z)^2-Z^2\right).
$$

Sketch the situation.

> **Scope note AGC-CORR-0133.** The source of Exercises 30.9 and 30.10 does not specify a base field. This edition explicitly states $\mathbb C$, in keeping with the geometric interpretation and the instruction to sketch; in characteristic $2$, the second quadratic form degenerates to the square of a line, so the intended calculation is no longer the same.

<!-- upstream_entity: Satz von Bézout/Bestätige für X^2-Y^3 und X^5-Y^4/Aufgabe -->

### Exercise 30.11 (4 points) {#br-ak-2012-w30-ex11}

Over an algebraically closed field $K$, verify Bézout's Theorem for the two monomial curves given in affine form by

$$
C=V(X^2-Y^3)
$$

and

$$
D=V(X^5-Y^4).
$$

> **Source-condition note REVIEW-AK-26-30-C19 - base field.** The source does not specify the base field, while Bézout's Theorem 30.3 is stated over an algebraically closed field. This edition makes that ambient hypothesis explicit without imposing an unnecessary characteristic restriction.

<!-- upstream_entity: Modultheorie/Exakte Komplexe/Kurze exakte Sequenzen/Hom-Funktoren/Aufgabe -->

### Exercise 30.12 (5 points) {#br-ak-2012-w30-ex12}

Let $R$ be a commutative ring and let $M,N$ be $R$-modules. If

$$
f:M\longrightarrow N
$$

is an $R$-module homomorphism, then the map

$$
\begin{aligned}
f^*:\operatorname{Hom}(N,R)&\longrightarrow\operatorname{Hom}(M,R),\\
\varphi&\longmapsto\varphi\circ f
\end{aligned}
$$

is also an $R$-module homomorphism.

Now let

$$
0\longrightarrow M\longrightarrow N\longrightarrow P\longrightarrow0
$$

be a short exact sequence of $R$-modules. Show that the induced sequence

$$
0\longrightarrow\operatorname{Hom}(P,R)
\longrightarrow\operatorname{Hom}(N,R)
\longrightarrow\operatorname{Hom}(M,R)
$$

is exact. Also give an example with $R=\mathbb Z$ showing that the last arrow is not surjective in general.
