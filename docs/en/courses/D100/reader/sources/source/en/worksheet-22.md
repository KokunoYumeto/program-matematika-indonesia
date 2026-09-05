---
title: "Worksheet 22 - Embedding Dimension, Singularities, and Tangent Lines"
stable_id: br-ak-2025-2026-w22
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 22"
upstream_pageid: 165941
upstream_revid: 1062660
upstream_timestamp: "2025-12-19T12:06:58Z"
upstream_mediawiki_sha1: e82e91c94f0a39d73aa10913d6821f673925893e
source_url: "https://de.wikiversity.org/w/index.php?oldid=1062660"
authority_manifest: authority/wikiversity/unit-22/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: fefb7f6221a3e71b94649f03c75693f9eb34ec228cedf0af7d9e332aeda7d38a
worksheet_xml_sha256: 84114f9130aa04acd7db9ddd306a2c221a7fbd1f3dad29e51187c2211d015722
worksheet_expanded_tex_sha256: f72523eee3cc5d807be6435787581d95da6902348172780cad88423ab19f9e34
exercise_map: authority/wikiversity/unit-22/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: d4b1d1f0a08de69d6fb7da513b8bce9ebaf697d5dad51632d0db063925d05f1e
license: "CC BY-SA 4.0"
component_rights:
  - path: authority/assets/Cercle_tangente_rayon.svg
    creator: "Christophe Dang Ngoc Chan (Cdang); derivative work by Hagman"
    license: "CC BY-SA 3.0"
  - path: authority/assets/Cardioid.svg
    creator: "D.328"
    license: "CC BY-SA 3.0"
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
---

# Worksheet 22 {#br-ak-2025-2026-w22}

## Practice exercises {#br-ak-2025-2026-w22-practice}

<!-- upstream_entity: Achsenkreuz/3/Einbettungsdimension/Aufgabe -->

### Exercise 22.1 {#br-ak-2025-2026-w22-ex-01}

Let $R$ be the local ring at the intersection of the three coordinate axes
in three-dimensional space. Determine its embedding dimension.

<!-- upstream_entity: Raumkurve/Verschiedene Einbettungsdimensionen/Aufgabe -->

### Exercise 22.2 {#br-ak-2025-2026-w22-ex-02}

Give an example of a curve

$$
C\subseteq\mathbb A_K^n
$$

with points $P_1,P_2,P_3\in C$ whose embedding dimensions are respectively
$1,2,3$.

<!-- upstream_entity: Ebene Kurve/Graph/Multiplizität/Tangente/Aufgabe -->

### Exercise 22.3 {#br-ak-2025-2026-w22-ex-03}

Let $H(X)\in K[X]$, $F=Y-H$, and let

$$
C=V(F)\subseteq\mathbb A_K^2
$$

be the graph of $H$, regarded as a plane algebraic curve. Let

$$
P=(a,b)=(a,H(a))
$$

be a point on this graph.

1. Show that the multiplicity of $C$ at $P$ is $1$.
2. Show that the tangent to $C$ at $P$ agrees with the usual tangent to the
   graph at $a$.

<!-- upstream_entity: Polynomiale Abbildung/Kettenregel/Formal/Aufgabe -->

### Exercise 22.4 {#br-ak-2025-2026-w22-ex-04}

Let $K$ be a field and let

$$
F_1,\ldots,F_m\in K[X_1,\ldots,X_\ell]
$$

and

$$
G_1,\ldots,G_n\in K[X_1,\ldots,X_m]
$$

be polynomials giving rise to polynomial maps

$$
\mathbb A_K^\ell\mathrel{\mathop{\longrightarrow}^{F}}
\mathbb A_K^m\mathrel{\mathop{\longrightarrow}^{G}}\mathbb A_K^n.
$$

Let $J(F)_P$ and $J(G)_Q$ be the Jacobian matrices defined by formal partial
differentiation. Prove the formal chain rule

$$
J(G\circ F)_P=J(G)_{F(P)}\circ J(F)_P.
$$

<!-- upstream_entity: Homogenes Polynom/Partielle Ableitung/Dehomogenisierung/Aufgabe -->

### Exercise 22.5 ★ {#br-ak-2025-2026-w22-ex-05}

1. Show that formal partial differentiation with respect to one variable
   in the polynomial ring $K[X_1,\ldots,X_n]$ commutes with
   dehomogenisation with respect to another variable.
2. Show that this does not hold when both operations concern the same
   variable.

<!-- upstream_entity: Homogenes Polynom/Darstellung mit formalen partiellen Ableitungen/Aufgabe -->

### Exercise 22.6 ★ {#br-ak-2025-2026-w22-ex-06}

Let

$$
H\in K[X_1,\ldots,X_n]
$$

be a homogeneous polynomial of degree $e$ in the standard grading. Show that

$$
eH=X_1\frac{\partial H}{\partial X_1}+\cdots+
X_n\frac{\partial H}{\partial X_n}.
$$

<!-- upstream_entity: Affine Ebene/y ist 2x^4+3x^2-x+1/(1,5)/Transformation auf Nullpunkt, Tangente auf x-Achse/Aufgabe -->

### Exercise 22.7 {#br-ak-2025-2026-w22-ex-07}

Consider the curve given by

$$
y=2x^4+3x^2-x+1
$$

with the point

$$
P=(1, 5).
$$

Find a coordinate transformation taking $P$ to $(0,0)$ and the tangent at
$P$ to the $x$-axis.

<!-- upstream_entity: Ebene algebraische Kurve/Reduziert/Nur endlich viele singuläre Punkte/Aufgabe -->

### Exercise 22.8 {#br-ak-2025-2026-w22-ex-08}

Let $K$ be a field and $F\in K[X,Y]$ a nonconstant polynomial all of whose
prime factors have multiplicity one. Let

$$
C=V(F)
$$

be the corresponding plane curve. Assume in addition that $F$ remains
squarefree after extending scalars to an algebraic closure of $K$. Show that
$C$ has only finitely many singular points.

*Edition note — correction to the source hypotheses:* Requiring the prime
factors of $F$ to have multiplicity one only in $K[X,Y]$ is insufficient
when $K$ is imperfect. For example, in characteristic $p>0$, a reduced
polynomial in $K[X,Y]$ may become a $p$th power after extending scalars, so
that both partial derivatives vanish and its geometric singular locus has
positive dimension. This edition states the precise condition needed in
the argument: $F$ is geometrically reduced. This is automatic, for example,
if $K$ is perfect and $F$ is squarefree.

<!-- upstream_entity: Ebene algebraische Kurve/Glatter Punkt/Liegt nur auf einer Komponente/Fakt/Beweis/Aufgabe -->

### Exercise 22.9 ★ {#br-ak-2025-2026-w22-ex-09}

Prove Lemma 22.12.

![Diagram of a circle with a radius to the point of tangency and a tangent line perpendicular to that radius](authority/assets/Cercle_tangente_rayon.svg)

*Figure: A tangent to a circle at a point is perpendicular to the radius
ending at that point. Work by Christophe Dang Ngoc Chan (Cdang), derivative
SVG version by Hagman; CC BY-SA 3.0.*

<!-- upstream_entity: Ebene algebraische Kurven/Einheitskreis/Bestimme Tangente/Aufgabe -->

### Exercise 22.10 ★ {#br-ak-2025-2026-w22-ex-10}

Show that the unit circle over a field of characteristic $\ne2$ is smooth,
and determine the tangent-line equation at each of its points.

<!-- upstream_entity: Ebene algebraische Kurve/Glattheit/Graph von Polynom und rationaler Funktion/Aufgabe -->

### Exercise 22.11 {#br-ak-2025-2026-w22-ex-11}

Let $K$ be a field.

1. Show that the graph of a polynomial $F\in K[X]$ is a smooth algebraic
   curve.
2. Let $F,G\in K[X]$ be polynomials with no common zero. Show that the graph
   of the rational function $F/G$ is also a smooth algebraic curve.

<!-- upstream_entity: Ebene Kurve/-2x^3+3x^2y-y+2/3 \sqrt(1/3)/C/Singularitäten/Aufgabe -->

### Exercise 22.12 ★ {#br-ak-2025-2026-w22-ex-12}

Determine the singular points of the plane algebraic curve

$$
V\left(-2X^3+3X^2Y-Y+\frac{2}{3}\sqrt{\frac{1}{3}}\right)
\subseteq\mathbb A_{\mathbb C}^2.
$$

<!-- upstream_entity: Mechanisch definierte Kurven/Stangenkonfiguration/Kreis und tangentiale Gerade/Mittlere Trajektorie/Aufgabe -->

### Exercise 22.13 {#br-ak-2025-2026-w22-ex-13}

For the trajectory computed in Example 8.5, determine the coordinates of
the points where the curve is singular.

<!-- upstream_entity: Ebene algebraische Kurve/x^3+xy^2/C/Singularitäten/Aufgabe -->

### Exercise 22.14 ★ {#br-ak-2025-2026-w22-ex-14}

Determine the prime factorisation of the polynomial

$$
X^3+XY^2\in\mathbb C[X,Y],
$$

and determine the singularities of the corresponding affine curve,
together with their multiplicities and tangent lines.

<!-- upstream_entity: Ebene algebraische Kurve/y^4+x^3+3xy^2+2x^2y/C/Multiplizität und Tangenten/Aufgabe -->

### Exercise 22.15 ★ {#br-ak-2025-2026-w22-ex-15}

Determine the multiplicity and tangent lines at the origin $(0,0)$ of the
plane algebraic curve

$$
C=V\left(Y^4+X^3+3XY^2+2X^2Y\right)
\subseteq\mathbb A_{\mathbb C}^2.
$$

<!-- upstream_entity: Ebene Kurve/v^3+u^2v-2uv+2u^2-4u-2v/Bestimme Singularität/Aufgabe -->

### Exercise 22.16 ★ {#br-ak-2025-2026-w22-ex-16}

For the zero locus given by the polynomial

$$
V^3+U^2V-2UV+2U^2-4U-2V,
$$

use partial derivatives to determine a singular point. Perform a coordinate
transformation taking this point to the origin. Determine the multiplicity
and tangent lines at that point.

*Edition note — correction to the source's scope:* The exercise does not
specify the base field, while the source solution divides by $2$ and $3$
and then factors using $\sqrt3$. To follow that solution, assume
$\operatorname{char}(K)\notin\{2,3\}$ and $\sqrt3\in K$ (for example,
$K=\mathbb R$ or $\mathbb C$). Over other fields, the point found can still
be checked directly, but the factorisation and tangent multiplicities must
be interpreted over the relevant base field; in characteristic $2$, the
tangent cone has one double tangent line.

![Symmetric cardioid with a cusp on the left and a rounded lobe on the right](authority/assets/Cardioid.svg)

*Figure: The cardioid with polar equation $r=a(1+\cos\theta)$ for $a=1$.
Work by D.328; CC BY-SA 3.0.*

<!-- upstream_entity: Ebene algebraische Kurve/Kardioide/Singularitäten/Aufgabe -->

### Exercise 22.17 {#br-ak-2025-2026-w22-ex-17}

Determine the singularities, including their multiplicities and tangent
lines, of the cardioid given by

$$
V\left(\left(X^2+Y^2\right)^2
-2X\left(X^2+Y^2\right)-Y^2\right).
$$

<!-- upstream_entity: Ebene Kurven/Lokale Diffeomorphie/Beispiel/1/Aufgabe -->

### Exercise 22.18 ★ {#br-ak-2025-2026-w22-ex-18}

Consider the two real curves

$$
V\left(X^5-X^3+2XY+7Y^2-9\right)
$$

at $(1,1)$ and

$$
V\left(X^4+Y^4-3X^2Y^2+5X+7Y\right)
$$

at the origin. Are these curves locally diffeomorphic to one another at the
specified points?

## Exercises for submission {#br-ak-2025-2026-w22-submit}

<!-- upstream_entity: Formales Ableiten/Zwei Variablen/Positive Charakteristik/Eine partielle Ableitung und beide sind null/Charakterisiere/Aufgabe -->

### Exercise 22.19 (3 points) {#br-ak-2025-2026-w22-ex-19}

Let $K$ be a field of characteristic $p\geq0$. Characterise the polynomials
$F\in K[X,Y]$ satisfying each of the following three conditions:

1. the first partial derivative is $0$;
2. the second partial derivative is $0$;
3. both partial derivatives are $0$.

<!-- upstream_entity: Ebene Kurve/x^3+y^3-3xy+1/Singularitäten und Tangenten über R und C/Aufgabe -->

### Exercise 22.20 (4 points) {#br-ak-2025-2026-w22-ex-20}

For the curve

$$
V\left(X^3+Y^3-3XY+1\right),
$$

determine its singular points over $\mathbb R$ and over $\mathbb C$. In each
case give the multiplicities and tangent lines.

<!-- upstream_entity: Ebene algebraische Kurve/Produkt/Einzelne Tangenten sind Tangenten/Aufgabe -->

### Exercise 22.21 (3 points) {#br-ak-2025-2026-w22-ex-21}

Let $K$ be an algebraically closed field and $G,H\in K[X,Y]$ polynomials
satisfying

$$
G(P)=H(P)=0
$$

at a specified point $P\in\mathbb A_K^2$. Let $F=GH$. Show that every
tangent to $G$ at $P$ and every tangent to $H$ at $P$ is also a tangent
to $F$ at $P$.

<!-- upstream_entity: Ebene algebraische Kurve/x^3+5x^2y-6xy^2-x^2-xy+4y^2/Tangenten in (0,0) und (1,2)/Aufgabe -->

### Exercise 22.22 (6 points) {#br-ak-2025-2026-w22-ex-22}

Let $K$ be an algebraically closed field. Consider the curve

$$
C=V\left(x^3+5x^2y-6xy^2-x^2-xy+4y^2\right).
$$

1. Determine the tangent lines at the origin.
2. Show that

   $$
   P=(1,2)
   $$

   is a point on the curve, and compute the tangent line or lines to $C$ at
   $P$ using derivatives.
3. Transform the variables so that $P$ is the origin in the new variables,
   and determine the tangent line or lines at $P$ from the transformed
   curve equation.

<!-- upstream_entity: Ebene algebraische Kurve/9y^4+10x^2y^2+x^4-12y^3-12x^2y+4y^2/Singularitäten und Multiplizität/Aufgabe -->

### Exercise 22.23 (4 points) {#br-ak-2025-2026-w22-ex-23}

For the algebraic curve

$$
C=V\left(9y^4+10x^2y^2+x^4-12y^3-12x^2y+4y^2\right),
$$

determine its singularities together with their multiplicities and tangent
lines.

*Source hint:* Compare Example 8.5.

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are preserved
as stated in the metadata and the edition's rights files.
