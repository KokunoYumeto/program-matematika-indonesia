---
title: "Worksheet 26 - Intersection Multiplicity"
stable_id: br-ak-2012-w26
language: en
source_course: "Kurs:Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 26"
upstream_pageid: 50761
upstream_revid: 793494
upstream_timestamp: "2022-08-25T06:04:07Z"
upstream_mediawiki_sha1: 10aad7862403732dbaa5a05ae637a084c2758751
source_url: "https://de.wikiversity.org/w/index.php?oldid=793494"
authority_manifest: authority/wikiversity/unit-26/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 981fa3c86534514215c722b6d4f6d711c040a7829465f20ae18940373f94763c
worksheet_xml_sha256: b5cc1634fba66dca202dec1947c17adf55182effecb80e3f298bf597e1535e78
worksheet_expanded_tex_sha256: 2959064d81372593e3a7c619b0753d0be90dde49318262a5995e2b4abccfce71
exercise_map: authority/wikiversity/unit-26/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: efa1d77d8b594a24078097f3595c0ae8078d9735dfe7d2b3abb05392d7340423
license: "CC BY-SA 4.0"
source_component_license_route: "Semantic source: CC BY-SA 4.0; historical official PDFs retain the CC BY-SA 2.0 Germany and CC BY-SA 4.0 notices"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 4
correction_ids: "AGC-CORR-0101; AGC-CORR-0103; AGC-CORR-0105; AGC-CORR-0107"
source_discrepancies: 0
reader_media_positions: 0
---

# Worksheet 26 {#br-ak-2012-w26}

## Warm-up exercises {#br-ak-2012-w26-practice}

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Schulbeispiel/Aufgabe -->

### Exercise 26.1 {#br-ak-2012-w26-ex-01}

For each $n$, give an example of two plane algebraic curves familiar from school which intersect at exactly one point with intersection multiplicity $n$.

<!-- upstream_entity: Affine Ebene/y ist 2x^4+3x^2-x+1/(1,5)/Transformation auf Nullpunkt, Tangente auf x-Achse/Aufgabe -->

### Exercise 26.2 {#br-ak-2012-w26-ex-02}

Consider the curve given by

$$
y=2x^4+3x^2-x+1
$$

with the point

$$
P=(1,5).
$$

Find a change of coordinates that takes $P$ to $(0,0)$ and the tangent line at $P$ to the $x$-axis.

<!-- upstream_entity: Ebene monomiale Kurve/Schnittmultiplizität mit Gerade durch Nullpunkt/Aufgabe -->

### Exercise 26.3 (3 points) {#br-ak-2012-w26-ex-03}

Let the monomial plane curve

$$
C=V\left(X^d-Y^e\right),
$$

be given, with $d$ and $e$ coprime. Compute the intersection multiplicity of this curve with every line $G$ through the origin which is not a component of $C$.

> **Editorial note - the common-component case.** The source asks for every line through the origin. If $d=e=1$, the curve $C=V(X-Y)$ itself is one of these lines, and the finite intersection multiplicity defined in the lecture is not available for a curve intersecting itself. This edition excludes lines which are components of $C$.

<!-- upstream_entity: Kartesisches Blatt/Schnittmultiplizität im Nullpunkt/Mit jeder Geraden/Aufgabe -->

### Exercise 26.4 ★ {#br-ak-2012-w26-ex-04}

Determine the intersection multiplicity at the origin of the folium of Descartes

$$
C=V\left(X^3+Y^3-3XY\right)
$$

with every affine line in the affine plane. Assume that the characteristic of the field is not $3$.

## Exercises to submit {#br-ak-2012-w26-submitted}

<!-- upstream_entity: Ebene Kurven/Schnittmultiplizität von x^5-y^2 und x^7-y^3 im Nullpunkt/Aufgabe -->

### Exercise 26.5 (4 points) {#br-ak-2012-w26-ex-05}

Compute the intersection multiplicity of the two monomial curves

$$
C=V\left(X^5-Y^2\right)
\qquad\text{and}\qquad
D=V\left(X^7-Y^3\right)
$$

at the origin.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Glatter Punkt auf C/Ordnung von G im Bewertungsring/Aufgabe -->

### Exercise 26.6 (4 points) {#br-ak-2012-w26-ex-06}

Let $K$ be a field, and let

$$
C=V(F)
\qquad\text{and}\qquad
D=V(G)
$$

be two plane algebraic curves with no common component. Let

$$
P\in C
$$

be a smooth point, so that the local ring

$$
R=K[X,Y]_{\mathfrak m_P}/(F)
$$

is a discrete valuation ring. Show that

$$
\operatorname{mult}_P(F,G)=\operatorname{ord}(G),
$$

where $\operatorname{ord}$ denotes the order of the nonzero image of $G$ in the valuation ring $R$.

> **Editorial note - finiteness condition.** The source does not state that the two curves must have no common component. This condition, or locally the condition that the image of $G$ in $R$ is nonzero, is necessary for both sides to be finite numbers. This edition states it explicitly.

<!-- upstream_entity: Ebene Kurven/Parabel und Kreis um (0,r) mit Radius r/Schnitt und Schnittmultiplizität/Aufgabe -->

### Exercise 26.7 (4 points) {#br-ak-2012-w26-ex-07}

In the real plane, let $r>0$. Consider the parabola

$$
C=V\left(Y-X^2\right)
$$

and the circle $D$ with centre $(0,r)$ and radius $r$, namely

$$
D=V\left(X^2+(Y-r)^2-r^2\right).
$$

Determine the intersection points of $C$ and $D$ and their respective intersection multiplicities.

> **Editorial note - geometric scope.** The source specifies a centre and radius without fixing a base field or a condition on $r$. To give “a circle of radius $r$” its usual geometric meaning and prevent degeneration to a point, this edition interprets the exercise over $\mathbb R$ with $r>0$ and writes out the circle's equation.

<!-- upstream_entity: Schnittmultiplizität/Einheitshyperbel und Kreis/Restklassenring als Produktring/Aufgabe -->

### Exercise 26.8 (4 points) {#br-ak-2012-w26-ex-08}

For each $a\in\mathbb C$, describe the quotient ring

$$
\mathbb C[X,Y]/\left(XY-1,X^2+Y^2-a\right)
$$

as a product of local rings. Also give the dimension of each factor ring as a vector space over $\mathbb C$.

<!-- upstream_entity: Ebene Kurve/x^3+y^3-3xy+1/Singularitäten und Tangenten über R und C/Aufgabe -->

### Exercise 26.9 (4 points) {#br-ak-2012-w26-ex-09}

For the curve

$$
V\left(X^3+Y^3-3XY+1\right),
$$

determine its singular points over $\mathbb R$ and over $\mathbb C$. For each point, give its multiplicity and tangent lines.

<!-- upstream_entity: Ebene Kurven/y ist 2x^4+3x^2-x+1/(1,5)/Transformiere und Potenzreihenansatz bis 5/Aufgabe -->

### Exercise 26.10 (3 points) {#br-ak-2012-w26-ex-10}

Consider the curve

$$
y=2x^4+3x^2-x+1
$$

at the point

$$
P=(1,5),
$$

in the coordinates found in Exercise 26.2. Determine the power series for the curve at $P$ along the tangent line.

The following exercise is probably more difficult.

<!-- upstream_entity: Zwei ebene monomiale Kurven/Schnittmultiplizität/Aufgabe -->

### Exercise 26.11 (8 points) {#br-ak-2012-w26-ex-11}

Let two distinct monomial plane curves

$$
C=V\left(X^d-Y^e\right)
\qquad\text{and}\qquad
D=V\left(X^r-Y^s\right),
$$

be given, with $d,e$ coprime and $r,s$ coprime. Compute the intersection multiplicity of the two curves at the origin.

> **Editorial note - zero-locus symbol.** In the second equation, the source writes $D=(X^r-Y^s)$ and omits the symbol $V$, although the text calls $D$ a curve. This edition restores the intended expression, $D=V(X^r-Y^s)$.
