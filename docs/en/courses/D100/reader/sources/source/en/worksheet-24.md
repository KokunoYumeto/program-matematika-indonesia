---
title: "Worksheet 24 - Formal Power Series and Tangent Lines"
stable_id: br-ak-2012-w24
language: en
source_course: "Kurs:Algebraische Kurven (Osnabrück 2012)"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Arbeitsblatt 24"
upstream_pageid: 50759
upstream_revid: 793492
upstream_timestamp: "2022-08-25T06:03:47Z"
upstream_mediawiki_sha1: 507a5966770c007e813734ca85da4e85f8a93b60
source_url: "https://de.wikiversity.org/w/index.php?oldid=793492"
authority_manifest: authority/wikiversity/unit-24/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 3731896a5980c565d9d69a2e01eee497f13b6f449f2f9c701fce726271c026a5
worksheet_xml_sha256: c6b2e329dc1326aef1b0372702a03fba7fc7106c9e866498df92e1fc9508d4b2
worksheet_expanded_tex_sha256: 37b53c3b6049ba45ff4aa1f4b7b4c4f0666e8a97248ba3c6c34a38061b758a4f
exercise_map: authority/wikiversity/unit-24/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 250744d177bc2d5cf2a1cc506a99e05f1250c771de88b214a0e8d5cabfe7b9b8
license: "CC BY-SA 4.0"
source_component_license_route: "Semantic source: CC BY-SA 4.0; historical official PDFs retain the CC BY-SA 2.0 Germany and CC BY-SA 4.0 notices"
no_blanket_relicensing_claim: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 1
reader_media_positions: 0
---

# Worksheet 24 {#br-ak-2012-w24}

## Warm-up exercises {#br-ak-2012-w24-practice}

<!-- upstream_entity: Ebene algebraische Kurve/Glatt/Parametrisierung ist singulär/Aufgabe -->

### Exercise 24.1 {#br-ak-2012-w24-ex-01}

Give an example of a smooth curve

$$
C\subseteq\mathbb A_K^2
$$

with a parametrisation whose differential vanishes at at least one point.

<!-- upstream_entity: Achsenkreuz/R mod m^n/Basis und Hilbert Funktion/Berechne/Aufgabe -->

### Exercise 24.2 {#br-ak-2012-w24-ex-02}

Consider the union of the coordinate axes

$$
V(xy)\subseteq\mathbb A_K^2
$$

and the local ring $R$ at the origin, with maximal ideal $\mathfrak m$.
Describe explicitly a $K$-basis of the quotient rings $R/\mathfrak m^n$
and determine their dimensions.

<!-- upstream_entity: Formale Potenzreihe/Inverses von 1-T/Aufgabe -->

### Exercise 24.3 {#br-ak-2012-w24-ex-03}

Let $K$ be a field and $K[[T]]$ the formal power series ring. Determine the
power series inverse of $1-T$.

<!-- upstream_entity: Potenzreihenring eine Variable/Abbildung der Lokalisierung an maximalen Ideal/Aufgabe -->

### Exercise 24.4 ★ {#br-ak-2012-w24-ex-04}

Let $K$ be a field and

$$
\mathfrak m=(T)\subseteq K[T]
$$

the maximal ideal corresponding to the origin, with localisation

$$
R=K[T]_{\mathfrak m}.
$$

Define a $K$-algebra homomorphism

$$
\varphi:R\longrightarrow K[[T]]
$$

satisfying $\varphi(T)=T$, where $K[[T]]$ denotes the formal power series
ring.

<!-- upstream_entity: Potenzreihe/Eine Variable/Einsetzen/Erste vier Glieder/Aufgabe -->

### Exercise 24.5 {#br-ak-2012-w24-ex-05}

Compute the first five coefficients, up to and including $c_4$, of the
composite power series $F(G)$ in the sense of Definition 24.9.

## Exercises for submission {#br-ak-2012-w24-submitted}

<!-- upstream_entity: Polynom in zwei Variablen/Identische partielle Ableitungen/über R und C/Aufgabe -->

### Exercise 24.6 (5 points) {#br-ak-2012-w24-ex-06}

Give an example of an irreducible real polynomial

$$
F\in\mathbb R[X,Y]
$$

whose two partial derivatives agree and are nonconstant. Show that this is
impossible over $\mathbb C$.

<!-- upstream_entity: Ebene algebraische Kurve/x^2 ist y^2+y^3/Singulärer Punkt, Tangenten/Parametrisierung t ist 1,0,-1 /Aufgabe -->

### Exercise 24.7 (3 points) {#br-ak-2012-w24-ex-07}

Consider the curve

$$
C=V\left(Y^2-X^2-X^3\right)
$$

with the parametrisation discussed in Example 24.3. Determine the singular
points of the curve, together with their multiplicities and tangent lines.
Also compute the image points and tangent lines for the parameter values

$$
t=-1,0,1.
$$

For the geometric conclusions about tangent lines and the parameter values
above, take the base field to be $\mathbb R$; in particular, it has
characteristic zero.

*Edition note - correction to the source equation:* The source displays
$C=V(X^2-Y^2-Y^3)$, but the referenced parametrisation is

$$
(x,y)=\left(t^2-1,t(t^2-1)\right).
$$

Direct substitution gives

$$
y^2-x^2-x^3
=(t^2-1)^2\left(t^2-1-(t^2-1)\right)=0.
$$

The edition therefore uses $C=V(Y^2-X^2-X^3)$, in agreement with the
parametrisation and the source's object category.

<!-- upstream_entity: Potenzreihe über C, die nirgendwo konvergiert/Aufgabe -->

### Exercise 24.8 (3 points) {#br-ak-2012-w24-ex-08}

Describe a formal power series over $\mathbb C$ that converges in no
neighbourhood of the origin.

<!-- upstream_entity: Potenzreihenring und Polynomring/Reihenfolge/Vergleiche/Aufgabe -->

### Exercise 24.9 (3 points) {#br-ak-2012-w24-ex-09}

Let $K$ be a field. Compare the two rings

$$
(K[X])[[Y]]
\qquad\text{and}\qquad
(K[[Y]])[X].
$$

In particular, determine whether one is contained in the other and, if so,
in which direction the inclusion holds.

<!-- upstream_entity: Hilberts Basissatz/Erweiterung auf Potenzreihenringe/Aufgabe -->

### Exercise 24.10 (6 points) {#br-ak-2012-w24-ex-10}

Let $R$ be a Noetherian commutative ring. Show that

$$
R[[T_1,\ldots,T_n]]
$$

is Noetherian.

> **Hint.** Take inspiration from the proof of Hilbert's basis theorem.
