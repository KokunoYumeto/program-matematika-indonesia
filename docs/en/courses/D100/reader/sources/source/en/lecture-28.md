---
title: "Lecture 28 - Projective Varieties and Projective Plane Curves"
stable_id: br-ak-2012-l28
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 28"
upstream_pageid: 50734
upstream_revid: 1052516
upstream_timestamp: "2025-08-27T13:52:03Z"
upstream_mediawiki_sha1: d037d0173bca4c443e06c7991d830568fa8dc0ea
source_url: "https://de.wikiversity.org/w/index.php?oldid=1052516"
authority_manifest: authority/wikiversity/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f2e34fc420c4beec300ea9e0accc52598e12c27f46c9022611996b1b43e29a99
lecture_xml: authority/wikiversity/unit-28/lecture-28.xml
lecture_xml_sha256: 3dc1abff96585199774b74910d1fc93102d0baf31e09ffa432a6e3966ddb5423
lecture_expanded_tex: authority/wikiversity/unit-28/lecture-28-expanded.tex
lecture_expanded_tex_sha256: ed9054224eb4f1d8d5849d9e44c88f82107866c8f0944ee7cb047e27ad337709
license: "Current semantic course text and this translation: CC BY-SA 4.0. Unit 28 reader media retain their component-specific CC0 or public-domain status as recorded in authority/RIGHTS-unit-28.csv. No blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; media component rights remain item-specific; official-PDF notices remain component-specific; no blanket relicensing claim."
license_evidence: "authority/UNIT_28_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-28.csv; authority/ASSET_CLOSURE-unit-28.json"
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 19
source_corrections: 12
correction_ids: "AGC-CORR-0115; AGC-CORR-0116; AGC-CORR-0117; AGC-CORR-0118; AGC-CORR-0119; AGC-CORR-0120; AGC-CORR-0123; AGC-CORR-0124; AGC-CORR-0125; REVIEW-AK-26-30-C06; REVIEW-AK-26-30-C08; REVIEW-AK-26-30-C10"
reader_media_positions: 4
---

# Lecture 28: Projective Varieties and Projective Plane Curves {#br-ak-2012-l28}

## Projective varieties {#br-ak-2012-l28-s01}

<!-- upstream_entity: Projektive Varietäten/Über Körper/Nullstellengebilde zu homogenen Polynomen/Definition -->

### Definition 28.1: projective variety {#br-ak-2012-l28-def-01}

A *projective variety* is a Zariski-closed subset

$$
V_+(\mathfrak a)\subseteq\mathbb P_K^n,
$$

where $\mathfrak a$ is a homogeneous ideal in $K[X_0,X_1,\ldots,X_n]$. Thus a projective variety $Y$ is the zero locus in projective space of a finite collection of homogeneous polynomials.

With the induced topology, a projective variety again carries a Zariski topology. Its open sets have the form $D_+(\mathfrak b)$ for a homogeneous ideal $\mathfrak b$, either in $K[X_0,\ldots,X_n]$ or in the quotient ring

$$
K[X_0,\ldots,X_n]/\mathfrak a,
$$

which is also called the *homogeneous coordinate ring* of $V_+(\mathfrak a)$. In particular, every homogeneous element $F\in K[X_0,\ldots,X_n]$ defines an open set

$$
D_+(F)\subseteq Y.
$$

<!-- upstream_entity: Projektive Varietät/Wird überdeckt von affinen Varietäten/Fakt -->

### Lemma 28.2: covering by affine varieties {#br-ak-2012-l28-lem-01}

Let $Y\subseteq\mathbb P_K^n$ be a projective variety. The affine spaces

$$
D_+(X_i)\cong\mathbb A_K^n\subset\mathbb P_K^n
$$

give affine varieties

$$
D_+(X_i)\cap Y
$$

which cover $Y$. In particular, for every point $P\in Y$ and every open neighbourhood $P\in U$, there is an affine open neighbourhood of $P$ contained in $U$.

<!-- upstream_entity: Projektive Varietät/Wird überdeckt von affinen Varietäten/Fakt/Beweis -->

#### Proof {#br-ak-2012-l28-lem-01-proof}

Within $Y$, we have

$$
D_+^Y(X_i):=Y\cap D_+^{\mathbb P_K^n}(X_i)
\cong Y\cap\mathbb A_K^n,
$$

where $D_+^Y(X_i)$ denotes the relative open set in $Y$, whereas $D_+^{\mathbb P_K^n}(X_i)$ is the standard chart in the ambient projective space. Thus $D_+^Y(X_i)$ is a closed subset (see Exercise 28.2) of the affine space $D_+^{\mathbb P_K^n}(X_i)\cong\mathbb A_K^n$, and is therefore an affine variety. Since the sets $D_+^{\mathbb P_K^n}(X_i)$ cover projective space, the sets $D_+^Y(X_i)$ cover $Y$.

> **Editorial bridge.** To obtain the claim about an arbitrary open neighbourhood $U$, choose one of the affine charts above containing $P$, then shrink the intersection to a principal open set containing $P$ and contained in $U$. That principal open set is affine, giving the required affine neighbourhood. $\square$

> **Editorial note - relative and ambient notation.** The source uses $D_+(X_i)$ both for the relative open set in $Y$ and for the standard chart in $\mathbb P_K^n$. This edition displays the intersection with $Y$ to distinguish the two meanings.

An immediate consequence is that local concepts developed for affine varieties also apply to projective varieties. To check a property at a point, we can pass straight to an affine open neighbourhood of that point. This applies, for example, to smoothness, normality, and regular functions.

## Algebraic functions and morphisms {#br-ak-2012-l28-s02}

Using the result just proved, we can again define what is meant by a regular or algebraic function on a projective variety.

<!-- upstream_entity: Projektive Varietät/Als abgeschlossene Teilmenge/Algebraische Funktion/Definition -->

### Definition 28.3: regular function {#br-ak-2012-l28-def-02}

Let $K$ be an algebraically closed field, let $Y\subseteq\mathbb P_K^n$ be a projective variety, let $U\subseteq Y$ be an open set, and let $P\in U$. A function

$$
f:U\longrightarrow\mathbb A_K^1=K
$$

is called *algebraic*, *regular*, or *polynomial* at $P$ if there is an affine open neighbourhood

$$
P\in V\subseteq U
$$

such that $f|_V$ is algebraic at $P$. The function $f$ is called algebraic on $U$ if it is algebraic at every point of $U$.

For an open set $U$, the set of all regular functions on $U$ again forms a commutative $K$-algebra, denoted $\Gamma(U,\mathcal O)$. From now on, a projective variety means a projective zero locus equipped with the induced Zariski topology and the *structure sheaf* $\mathcal O$ of regular functions.

These concepts extend immediately to open subsets, leading to the notion of a quasiprojective variety.

<!-- upstream_entity: Varietäten/K/Quasiprojektive Varietät/Definition -->

### Definition 28.4: quasiprojective variety {#br-ak-2012-l28-def-03}

An open subset of a projective variety, equipped with the induced Zariski topology and the structure sheaf of algebraic functions, is called a *quasiprojective variety*.

In particular, both projective varieties and affine varieties are quasiprojective. For the latter, an affine variety $Y\subseteq\mathbb A_K^n$ can be extended to a projective variety $\widetilde Y\subseteq\mathbb P_K^n$ containing $Y$ as an open subset.

The definition of a morphism also applies word for word in this more general situation.

<!-- upstream_entity: Quasiprojektive Varietäten/K/Morphismus/Definition -->

### Definition 28.5: morphism of quasiprojective varieties {#br-ak-2012-l28-def-04}

Let $X$ and $Y$ be quasiprojective varieties over an algebraically closed field, and let

$$
\psi:Y\longrightarrow X
$$

be a continuous map. The map $\psi$ is called a *morphism* if, for every open set $U\subseteq X$ and every algebraic function $f\in\Gamma(U,\mathcal O_X)$, the composition

$$
f\circ\psi:
\psi^{-1}(U)\longrightarrow U\stackrel{f}{\longrightarrow}\mathbb A_K^1
$$

belongs to $\Gamma(\psi^{-1}(U),\mathcal O_Y)$.

## Homogenisation and projective closure {#br-ak-2012-l28-s03}

Let $K$ be algebraically closed, and consider the hyperbola

$$
V(XY-1)\subset\mathbb A_K^2\subset\mathbb P_K^2.
$$

The hyperbola is closed in the affine plane but not in the projective plane. Embed the affine plane as $V(Z-1)$ in three-dimensional space, and consider the lines through the origin and the points of the hyperbola. Geometrically these lines tilt increasingly and, in the real or complex picture, approach the $x$-axis and the $y$-axis. The following algebraic computation gives a statement valid over this base field.

> **Source-condition note REVIEW-AK-26-30-C08 - base field.** The source does not state a field hypothesis in this introductory paragraph. This edition uses the algebraically closed-field setting of Definition 28.3 and Theorem 28.8; over a finite field, the stated non-closedness fails for the Zariski topology on $K$-points. The source's expression “approach” remains Euclidean intuition for $\mathbb R$ or $\mathbb C$.

<!-- upstream_entity: Polynomring/Homogenisierung zu einem Ideal/Definition -->

### Definition 28.6: homogenisation of an ideal {#br-ak-2012-l28-def-05}

For an ideal

$$
\mathfrak a\subseteq K[X_1,\ldots,X_n],
$$

the ideal in $K[X_1,\ldots,X_n,Z]$ generated by the homogenisations of all elements of $\mathfrak a$ is called the *homogenisation* $\mathfrak a^h$ of $\mathfrak a$.

In general, homogenising only a generating set of the ideal $\mathfrak a$ is not enough.

<!-- upstream_entity: Affine Varietät/Projektiver Abschluss/Definition -->

### Definition 28.7: projective closure {#br-ak-2012-l28-def-06}

For an affine variety

$$
V(\mathfrak a)\subseteq\mathbb A_K^n\subseteq\mathbb P_K^n,
$$

the Zariski closure of $V(\mathfrak a)$ in $\mathbb P_K^n$ is called the *projective closure* of $V(\mathfrak a)$.

<!-- upstream_entity: Affine Varietät/Projektiver Abschluss/Beschreibung mit Homogenisierung/Fakt -->

### Theorem 28.8: projective closure by homogenisation {#br-ak-2012-l28-thm-01}

Let $K$ be an algebraically closed field and let

$$
V=V(\mathfrak a)\subseteq\mathbb A_K^n\cong D_+(X_0)
$$

be an affine variety. The projective closure of $V(\mathfrak a)$ in $\mathbb P_K^n$ is $V_+(\mathfrak b)$, where $\mathfrak b$ is the homogenisation of $\mathfrak a$ in $K[X_0,X_1,\ldots,X_n]$.

<!-- upstream_entity: Affine Varietät/Projektiver Abschluss/Beschreibung mit Homogenisierung/Fakt/Beweis -->

#### Proof {#br-ak-2012-l28-thm-01-proof}

A point $P=(x_1,\ldots,x_n)$ in $\mathbb A_K^n$ determines the point $\widehat P=(1,x_1,\ldots,x_n)$ in $\mathbb P_K^n$. For $F\in K[X_1,\ldots,X_n]$ and its homogenisation $\widehat F$, we have

$$
F(P)=\widehat F(\widehat P).
$$

Consequently, all homogeneous polynomials in $\mathfrak b$ vanish on $V(\mathfrak a)$, so

$$
V(\mathfrak a)\subseteq V_+(\mathfrak b).
$$

We obtain a commutative diagram in which every arrow is injective,

$$
\begin{matrix}
V(\mathfrak a)&\longrightarrow&V_+(\mathfrak b)\\
\downarrow&&\downarrow\\
\mathbb A_K^n&\longrightarrow&\mathbb P_K^n.
\end{matrix}
$$

Write the projective closure of $V(\mathfrak a)$ as $V_+(\mathfrak c)$ for a homogeneous ideal $\mathfrak c$. Minimality of the closure gives $V_+(\mathfrak c)\subseteq V_+(\mathfrak b)$. To prove the reverse inclusion, it suffices to show

$$
\mathfrak c\subseteq\operatorname{rad}(\mathfrak b).
$$

Take a nonzero homogeneous polynomial $F\in\mathfrak c$ and write

$$
F=X_0^rG,
$$

where $G$ is not a multiple of $X_0$. Since $F$ vanishes on $V(\mathfrak a)$ and $X_0$ does not vanish on $V(\mathfrak a)\subseteq D_+(X_0)$, the polynomial $G$ also vanishes there. Its dehomogenisation

$$
g=G(1,X_1,\ldots,X_n)
$$

therefore vanishes on $V(\mathfrak a)$. Hilbert's Nullstellensatz gives an integer $N\geq1$ such that $g^N\in\mathfrak a$. Because $X_0$ does not divide $G$, the degree of $g$ equals the degree of $G$, so homogenising $g^N$ gives $G^N$. Hence $G^N\in\mathfrak b$, and consequently

$$
F^N=X_0^{rN}G^N\in\mathfrak b.
$$

Thus $F\in\operatorname{rad}(\mathfrak b)$. This proves the required inclusion and shows that the closure is exactly $V_+(\mathfrak b)$. $\square$

> **Source correction REVIEW-AK-26-30-C06 - the radical step.** The source replaces $\mathfrak a$ by its radical and then concludes membership in the original homogenised ideal $\mathfrak b$, although replacing $\mathfrak a$ can change that ideal. The argument above keeps $\mathfrak a$ and $\mathfrak b$ fixed and proves the required power-membership $F^N\in\mathfrak b$.

## Projective plane curves {#br-ak-2012-l28-s04}

<!-- upstream_entity: Algebraische Kurve/Projektive ebene Kurve/Definition -->

### Definition 28.9: projective plane curve {#br-ak-2012-l28-def-07}

A *projective plane curve* is the zero locus

$$
C=V_+(F)\subset\mathbb P_K^2
$$

of a nonconstant homogeneous polynomial $F\in K[X,Y,Z]$.

For an affine plane curve $V=V(G)\subset\mathbb A_K^2\subset\mathbb P_K^2$, the Zariski closure of $V$ in $\mathbb P_K^2$ is called the projective closure of the curve.

<!-- upstream_entity: Ebene projektive Kurve/Gleichung für projektiven Abschluss mit Homogenisierung/Fakt -->

### Corollary 28.10: an equation for the projective closure of a curve {#br-ak-2012-l28-cor-01}

Let $K$ be an algebraically closed field and let

$$
V=V(G)\subseteq\mathbb A_K^2\subseteq\mathbb P_K^2,
\qquad G\in K[X,Y].
$$

The Zariski closure of $V$ in $\mathbb P_K^2$ is

$$
C=V_+(H),
$$

where $H$ is the homogenisation of $G$ in $K[X,Y,Z]$.

<!-- upstream_entity: Ebene projektive Kurve/Gleichung für projektiven Abschluss mit Homogenisierung/Fakt/Beweis -->

#### Proof {#br-ak-2012-l28-cor-01-proof}

This follows directly from Theorem 28.8 and the fact that the homogenisation of a principal ideal is generated by the homogenisation of its generator. $\square$

> **Editorial note - two unresolved source references.** In the preceding step, the source prints `nach Aufgabe *****` while linking to the [exercise on homogenising a principal ideal](https://de.wikiversity.org/wiki/Hauptideal/Homogenisierung/Aufgabe). After the corollary, it also prints `siehe Aufgabe *****` while linking to the [exercise on a homogeneous equation for the projective closure over a field that is not algebraically closed](https://de.wikiversity.org/wiki/R/Projektiver_Abschluss/Homogene_Gleichungen/Aufgabe). Neither exercise number is supplied; this edition preserves the exact linked identities without guessing their numbers.

Without the assumption that the field is algebraically closed, the assertion need not hold.

<!-- upstream_entity: Ebene projektive Kurve/Verschiedene affine Ausschnitte/Glattheit/Bemerkung -->

### Remark 28.11: affine charts and points at infinity {#br-ak-2012-l28-rem-01}

Let $G\in K[X,Y]$ and let $F\in K[X,Y,Z]$ be its homogenisation. We recover $G$ from $F$ by setting $Z=1$. The polynomial $G$ describes the intersection $D_+(Z)\cap V_+(F)$. The other two affine pieces,

$$
D_+(X)\cap V_+(F)
\quad\text{and}\quad
D_+(Y)\cap V_+(F),
$$

play equal roles and give affine neighbourhoods of the points of $C=V_+(F)$ not lying in $D_+(Z)$.

To check smoothness at $P\in C$, choose an affine open neighbourhood, preferably one of $D_+(L)\cap C$ with $L=X,Y,Z$, and apply the derivative criterion to the affine equation in that chart. The result does not depend on the chart chosen, although one chart may be computationally more convenient.

From the viewpoint of the affine curve $V(G)$, the points at infinity are

$$
V_+(F)\cap V_+(Z).
$$

This is the intersection of the projective curve with a projective line.

The intersection is finite unless the line $V_+(Z)$ is a component of the curve. This cannot occur when we start with an affine curve, since $Z$ does not divide the homogenisation $F$. Write the homogeneous decomposition

$$
G=G_d+\cdots+G_m,\qquad m\leq d,
$$

so that

$$
F=G_d+G_{d-1}Z+\cdots+G_mZ^{d-m}.
$$

Setting $Z=0$ shows that the points at infinity are given by the projective zeros of the homogeneous polynomial $G_d(X,Y)$. Thus the degree $d$ immediately bounds the number of points at infinity on the curve.

<!-- upstream_entity: Ebene projektive Kurven/Kegelschnitt als affine Ausschnitte/Beispiel -->

### Example 28.12: conic sections as affine charts {#br-ak-2012-l28-ex-01}

Assume $\operatorname{char}(K)\ne2$, and consider the standard cone

$$
V(X^2+Y^2-Z^2)\subset\mathbb A_K^3.
$$

Since its equation is homogeneous, the cone can also be regarded as the projective plane curve of degree two

$$
V_+(X^2+Y^2-Z^2)\subset\mathbb P_K^2.
$$

Intersections of the cone with arbitrary planes $E\subset\mathbb A_K^3$ are called *conic sections*. If $E$ does not pass through the origin, it can naturally be identified with an open affine plane $D_+(L)\subseteq\mathbb P_K^2$, where $L$ is a homogeneous linear form describing the vector subspace parallel to $E$. The intersections of the cone with $E$ are different affine pieces of the same projective curve. In particular, circles, hyperbolas, and parabolas are such affine pieces.

By contrast, intersections with planes through the origin, viewed projectively, are the finite sets

$$
V_+(X^2+Y^2-Z^2)\cap V_+(L).
$$

> **Editorial note - characteristic two.** The source imposes no restriction on the characteristic. In characteristic $2$, the polynomial above becomes $(X+Y+Z)^2$; if $L=X+Y+Z$, the projective intersection is the whole line, not a finite set. The characteristic restriction above ensures that the conic is nonsingular and has no line as a component.

<!-- upstream_entity: Projektive Kurve/Fermat-Kurve vom Grad d/Definition -->

### Definition 28.13: Fermat curve {#br-ak-2012-l28-def-08}

Let $K$ be a field and let $d\geq1$. The projective plane curve

$$
V_+(X^d+Y^d+Z^d)\subseteq\mathbb P_K^2
$$

is called the *Fermat curve* of degree $d$. For $d=1$, it is simply a projective line.

> **Editorial note - projective zero-locus operator.** In this definition the source writes $V(X^d+Y^d+Z^d)$ although the object lies in $\mathbb P_K^2$; the next lemma correctly writes $V_+$. This edition consistently uses $V_+$.

<!-- upstream_entity: Projektive Kurve/Fermat-Kurve vom Grad d/Glattheit/Fakt -->

### Lemma 28.14: smoothness of Fermat curves {#br-ak-2012-l28-lem-02}

Let $K$ be an algebraically closed field of characteristic $p\geq0$, and let

$$
C=V_+(X^d+Y^d+Z^d)\subset\mathbb P_K^2
$$

be the Fermat curve of degree $d$. If the characteristic of $K$ does not divide $d$, then $C$ is smooth.

<!-- upstream_entity: Projektive Kurve/Fermat-Kurve vom Grad d/Glattheit/Fakt/Beweis -->

#### Proof {#br-ak-2012-l28-lem-02-proof}

Smoothness is a local property, so it suffices to work on any affine piece. By symmetry, consider

$$
V(X^d+Y^d+1)\subset\mathbb A_K^2.
$$

The partial derivatives are $dX^{d-1}$ and $dY^{d-1}$. The characteristic hypothesis gives $d\ne0$. If $d=1$, both derivatives are nonzero constants and never vanish. If $d>1$, both vanish simultaneously only at $x=y=0$, which does not lie on the curve. $\square$

> **Editorial note - degree-one case.** The source immediately states that both derivatives vanish simultaneously only at $(0,0)$; this does not hold for $d=1$, when both derivatives are nonzero constants. The case distinction above preserves the smoothness conclusion for all permitted $d$.

![Football pattern illustrating a surface of genus zero](authority/assets/Soccerball.svg)

*Sphere, or surface of genus zero. OpenClipart file, currently uploaded to Commons by MapGrid, CC0 1.0; the historical course label records Ranveig/PD.*

![A torus as a surface with one handle](authority/assets/Torus_illustration.png)

*Torus, a surface of genus one. Oleg Alexandrov, public domain.*

![A double torus as a surface with two handles](authority/assets/Double_torus_illustration.png)

*Double torus, a surface of genus two. Oleg Alexandrov, public domain.*

![A sphere with three handles](authority/assets/Sphere_with_three_handles.png)

*Sphere with three handles, a surface of genus three. Oleg Alexandrov, public domain.*

<!-- upstream_entity: Glatte projektive Kurven/C/Kurzübersicht zur topologischen Gestalt/Bemerkung -->

### Remark 28.15: topological shape and genus {#br-ak-2012-l28-rem-02}

Over the base field $\mathbb C$, a smooth connected projective curve can be viewed as a compact oriented real two-dimensional manifold. Topologically, such a manifold is homeomorphic to a sphere with $g$ handles attached. The number $g$ is called the *genus* of the real surface, and also the genus of the curve.

> **Source-condition note REVIEW-AK-26-30-C10 - connectedness.** The source says “a smooth projective curve” here, but the description by one sphere with $g$ handles and one genus presupposes that the curve is connected. This edition states that convention explicitly.

The complex projective line is a two-dimensional sphere with no handles, so its genus is $0$. A surface of genus $1$ is a torus (like a car tyre), homeomorphic to $S^1\times S^1$. In the source's exposition, projective curves whose underlying topological manifolds have genus one are called elliptic curves.

> **Editorial note - convention for elliptic curves.** In modern terminology, an elliptic curve usually means a smooth projective curve of genus one together with a base point. The source's statement describes a genus-one curve without a chosen base point; this edition retains the exposition and notes the difference in convention.

Genus also has algebraic definitions and is therefore defined for smooth connected projective curves over every algebraically closed field. It equals the $K$-dimension of the first cohomology group of the structure sheaf, and also the $K$-dimension of the space of global differential forms on the curve.

For every $g$, there is a projective curve of genus $g$. In particular, every compact oriented real two-dimensional surface can be realised as a complex projective curve. Such objects are also called *Riemann surfaces*.

For a smooth plane curve

$$
C=V_+(F)\subset\mathbb P_K^2
$$

of degree $d=\deg(F)$, the genus is

$$
g=\frac{(d-1)(d-2)}{2}.
$$

Smooth projective plane curves of degree one or two, namely lines and conics, have genus $0$ and are isomorphic to the projective line. For $d=3$ we obtain genus $1$, giving elliptic curves in the source's convention, whereas $d=4$ gives genus $3$. Thus not every genus can be realised by a smooth plane curve. For example, giving explicit equations for a curve of genus $2$ is by no means easy.
