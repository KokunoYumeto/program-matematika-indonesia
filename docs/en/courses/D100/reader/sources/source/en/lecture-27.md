---
title: "Lecture 27 - Projective Space"
stable_id: br-ak-2012-l27
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 27"
upstream_pageid: 50733
upstream_revid: 1052572
upstream_timestamp: "2025-08-27T14:01:03Z"
upstream_mediawiki_sha1: 9a396f3a601f0a0a0606657550a30b9a601da2f6
source_url: "https://de.wikiversity.org/w/index.php?oldid=1052572"
authority_manifest: authority/wikiversity/unit-27/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 98f9ebcc0d3b41bb0b955c5190d416b9ebfc07433015732faaf7f38366a1d9b2
lecture_xml: authority/wikiversity/unit-27/lecture-27.xml
lecture_xml_sha256: 9e1a4f687ca1faf008e9864460dc036f7849e2a3203f7d30dd509c7876b69ea6
lecture_expanded_tex: authority/wikiversity/unit-27/lecture-27-expanded.tex
lecture_expanded_tex_sha256: 2b75b62d96c149f8344de2060fcbc96a4d2061140dd6c509b2b11ad2e95dc8b4
license: "Current semantic course text and this translation: CC BY-SA 4.0. Unit 27 reader media retain their component-specific licenses and public-domain status as recorded in authority/RIGHTS-unit-27.csv. No blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; media component rights remain item-specific; official-PDF notices remain component-specific; no blanket relicensing claim."
license_evidence: "authority/UNIT_27_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-27.csv; authority/ASSET_CLOSURE-unit-27.json"
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 21
source_corrections: 8
correction_ids: "AGC-CORR-0108; AGC-CORR-0109; AGC-CORR-0110; AGC-CORR-0111; AGC-CORR-0112; AGC-CORR-0113; AGC-CORR-0114; REVIEW-AK-26-30-C04"
reader_media_positions: 10
---

# Lecture 27: Projective Space {#br-ak-2012-l27}

## Projective space {#br-ak-2012-l27-s01}

![A dandelion with many lines and stalks radiating from a single centre](authority/assets/Loewenzahn_20.jpg)

*Lines through a point. Waugsberg; historical course label: CC BY-SA 2.5; frozen Commons description: CC BY-SA 3.0. Both notices are retained; local file: `authority/assets/Loewenzahn_20.jpg`.*

<!-- upstream_entity: Projektiver Raum/Geradenmenge/Tafelbilder/Einführung/Textabschnitt -->

<!-- upstream_entity: Der projektive Raum/Als Geradenmenge/Homogene Koordinaten/Ohne Topologie/Definition -->

### Definition 27.1: projective space {#br-ak-2012-l27-def-01}

Let $K$ be a field. The *$n$-dimensional projective space*

$$
\mathbb P_K^n
$$

consists of all lines through the origin in the affine space $\mathbb A_K^{n+1}$, each such line being regarded as a point. Such a projective point is represented by *homogeneous coordinates*

$$
(a_0,a_1,\ldots,a_n),
$$

where the $a_i$ are not all zero. Two such coordinate tuples represent the same point precisely when one is obtained from the other by multiplication by a scalar

$$
\lambda\in K^\times.
$$

We shall gradually equip projective space with additional structures.

<!-- upstream_entity: Der projektive Raum/Offene Standardüberdeckung mit affinen Räumen/Fakt -->

### Theorem 27.2: the standard open cover by affine spaces {#br-ak-2012-l27-thm-01}

Let $K$ be a field, let $\mathbb P_K^n$ be a projective space, and let

$$
i\in\{0,1,\ldots,n\}.
$$

Indexing the source coordinates by all $j\ne i$, there is a natural map

$$
\begin{aligned}
\varphi_i:\mathbb A_K^n&\longrightarrow\mathbb P_K^n,\\
(u_0,\ldots,\widehat{u_i},\ldots,u_n)
&\longmapsto
[u_0:\cdots:u_{i-1}:1:u_{i+1}:\cdots:u_n].
\end{aligned}
$$

This map is injective and induces a bijection onto the set of projective points whose $i$th homogeneous coordinate is nonzero, namely

$$
D_+(X_i)
:=
\{[x_0:\cdots:x_n]\in\mathbb P_K^n\mid x_i\ne0\}.
$$

Its inverse is given by

$$
[x_0:\cdots:x_n]
\longmapsto
\left(
\frac{x_0}{x_i},\ldots,
\frac{x_{i-1}}{x_i},
\frac{x_{i+1}}{x_i},\ldots,
\frac{x_n}{x_i}
\right).
$$

Projective space is covered by these $n+1$ affine spaces. The complement of the affine chart

$$
\mathbb A_K^n\cong D_+(X_i)\subseteq\mathbb P_K^n
$$

is a projective space of dimension $n-1$.

> **Editorial note - chart insertion indices.** The source writes the source coordinates as $(u_1,\ldots,u_n)$ and then inserts $1$ “in position $i$” for $i\in\{0,\ldots,n\}$. This notation is ambiguous at the endpoints and does not display a coordinate $u_0$. This edition indexes coordinates by $\{0,\ldots,n\}\setminus\{i\}$ and uses a hat to mark the omitted coordinate.

<!-- upstream_entity: Der projektive Raum/Offene Standardüberdeckung mit affinen Räumen/Fakt/Beweis -->

#### Proof {#br-ak-2012-l27-thm-01-proof}

The map is well defined because the coordinate $1$ ensures that at least one homogeneous coordinate is nonzero. If

$$
[u_0:\cdots:u_{i-1}:1:u_{i+1}:\cdots:u_n]
=
[v_0:\cdots:v_{i-1}:1:v_{i+1}:\cdots:v_n],
$$

then some $\lambda\in K^\times$ multiplies every coordinate on the right. Comparing the $i$th coordinates gives $1=\lambda$, so all the other coordinates agree and the map is injective.

On $D_+(X_i)$, every point has exactly one representative with $i$th coordinate equal to $1$, obtained by dividing all coordinates by $x_i$. This proves the formula for the inverse. Every projective point has at least one nonzero coordinate, so the charts $D_+(X_i)$ cover $\mathbb P_K^n$.

The complement of $D_+(X_i)$ is

$$
V_+(X_i)
=
\{[x_0:\cdots:x_{i-1}:0:x_{i+1}:\cdots:x_n]
\mid \text{at least one }x_j\ne0\}.
$$

Retaining the identification of tuples that differ by a scalar factor, this set is $\mathbb P_K^{n-1}$. $\square$

![First of three diagrams of affine charts on the projective line](authority/assets/Projektiveline1bb.jpg)

*Illustration of the projective line, part 1. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveline1bb.jpg`.*

![Second of three diagrams of affine charts on the projective line](authority/assets/Projektiveline2bb.jpg)

*Illustration of the projective line, part 2. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveline2bb.jpg`.*

![Third of three diagrams of affine charts on the projective line](authority/assets/Projektiveline3bb.jpg)

*Illustration of the projective line, part 3. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveline3bb.jpg`.*

<!-- upstream_entity: Die projektive Gerade/Einführende Beschreibung/Beispiel -->

### Example 27.3: the projective line {#br-ak-2012-l27-ex-01}

The projective line $\mathbb P_K^1$ is the set of lines through the origin in the affine plane $\mathbb A_K^2$. Such a line is either the $x$-axis or intersects the line

$$
V(y-1)
$$

at exactly one point. The line $V(y-1)$ is parallel to the $x$-axis and passes through $(0,1)$. Conversely, every point

$$
P\in V(y-1)\cong\mathbb A_K^1
$$

uniquely determines a line through the origin. Thus the projective line consists of an affine line and one additional point, called the point “at infinity”.

This point is not intrinsically different from the other projective points. Take any line $G$ through the origin and a parallel line $L\ne G$. The line $L$ can play the role of the affine line, while $G$ represents the point at infinity as seen from that affine chart.

![First of four diagrams of affine charts and points at infinity in the projective plane](authority/assets/Projektiveplane1bb.jpg)

*Illustration of the projective plane, part 1. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveplane1bb.jpg`.*

![Second of four diagrams of affine charts and points at infinity in the projective plane](authority/assets/Projektiveplane2bb.jpg)

*Illustration of the projective plane, part 2. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveplane2bb.jpg`.*

![Third of four diagrams of affine charts and points at infinity in the projective plane](authority/assets/Projektiveplane3bb.jpg)

*Illustration of the projective plane, part 3. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveplane3bb.jpg`.*

![Fourth of four diagrams of affine charts and points at infinity in the projective plane](authority/assets/Projektiveplane4bb.jpg)

*Illustration of the projective plane, part 4. Darapti, CC BY-SA 3.0; local file: `authority/assets/Projektiveplane4bb.jpg`.*

<!-- upstream_entity: Die projektive Ebene/Einführende Beschreibung/Beispiel -->

### Example 27.4: the projective plane {#br-ak-2012-l27-ex-02}

Points in the projective plane $\mathbb P_K^2$ correspond to lines through the origin in the affine space $\mathbb A_K^3$. Each point of the projective plane is represented by a tuple

$$
(x,y,z),
$$

where $x,y,z$ are not all zero. Two tuples are identified if one is obtained from the other by multiplication by a nonzero scalar. The projective plane is covered by three affine planes

$$
D_+(X),\qquad D_+(Y),\qquad D_+(Z).
$$

The chart $D_+(Z)$ consists of all points with nonzero third coordinate. Multiplying the coordinates by $z^{-1}$ gives the representative

$$
\left(\frac{x}{z},\frac{y}{z},\frac{z}{z}\right)
=(u,v,1),
$$

so this chart is indeed an affine plane. Its complement is $V_+(Z)$, the set of points with third coordinate zero. Retaining scalar identification makes $V_+(Z)$ a projective line.

A point $(x,y,0)$ on this line, together with the origin $(0,0,1)$ of $D_+(Z)$, determines the direction $(x,y)$ of a line through the origin in the affine plane. The homogeneous equation of this line is

$$
yX-xY=0,
$$

or $V_+(yX-xY)$. Thus we can picture the projective plane as an affine plane with one additional point at infinity for every direction of a line through the origin.

![Perspective diagram with projection rays joining an object, a projection centre, and an image plane](authority/assets/Perspective_Projection_Principle.jpg)

*Principle of perspective projection. Historical course credit: Fantagu; the frozen Commons description credits the drawing to Joachim Baecker and identifies Fantagu as the uploader. CC BY-SA 3.0; local file: `authority/assets/Perspective_Projection_Principle.jpg`.*

## Zeros of homogeneous polynomials {#br-ak-2012-l27-s02}

<!-- upstream_entity: Homogene Polynome/Projektive Nullstellengebilde/Zariski-Topologie/Einführung/Textabschnitt -->

For an arbitrary polynomial

$$
F\in K[X_0,\ldots,X_n],
$$

the assertion that a point $P\in\mathbb P_K^n$ is a zero of $F$ is generally not well defined. The value can change when a coordinate representative of $P$ is multiplied by a scalar. The situation is different for homogeneous polynomials.

<!-- upstream_entity: Der projektive Raum/Homogenes Polynom/Nullsein ist wohldefiniert/Fakt -->

### Lemma 27.5: vanishing of a homogeneous polynomial is well defined {#br-ak-2012-l27-lem-01}

Let $K$ be a field and let

$$
F\in K[X_0,\ldots,X_n]
$$

be a homogeneous polynomial of degree $d$. For every $(x_0,\ldots,x_n)\in K^{n+1}$ and $\lambda\in K$,

$$
F(\lambda x_0,\ldots,\lambda x_n)
=
\lambda^d F(x_0,\ldots,x_n).
$$

In particular, $F$ vanishes at $(x_0,\ldots,x_n)$ if and only if it vanishes at $\lambda(x_0,\ldots,x_n)$ for every $\lambda\ne0$.

<!-- upstream_entity: Der projektive Raum/Homogenes Polynom/Nullsein ist wohldefiniert/Fakt/Beweis -->

#### Proof {#br-ak-2012-l27-lem-01-proof}

It suffices to check each homogeneous monomial. For

$$
X_0^{d_0}\cdots X_n^{d_n},
\qquad
\sum_{i=0}^{n}d_i=d,
$$

we obtain

$$
\begin{aligned}
(\lambda X_0)^{d_0}\cdots(\lambda X_n)^{d_n}
&=(\lambda^{d_0}X_0^{d_0})\cdots
  (\lambda^{d_n}X_n^{d_n})\\
&=\lambda^d X_0^{d_0}\cdots X_n^{d_n}.
\end{aligned}
$$

Linearity then gives the assertion for $F$. $\square$

The lemma makes the property “vanishes or does not vanish” well defined at a projective point. However, the numerical value of a homogeneous polynomial at a projective point need not be intrinsically defined. In general, a homogeneous polynomial does not define a function on projective space by evaluation of representatives.

> **Editorial note - scope of the evaluation claim.** The source makes the last assertion without qualification. Constant polynomials, for example, do give well-defined values, so this edition states it as a general warning rather than an assertion about every homogeneous polynomial.

<!-- upstream_entity: Der projektive Raum/Nullstellengebilde zu einem homogenen Polynom/Definition -->

### Definition 27.6: projective zero locus {#br-ak-2012-l27-def-02}

Let $K$ be a field and let

$$
F\in K[X_0,\ldots,X_n]
$$

be a homogeneous polynomial. The set

$$
V_+(F)
=
\{P=[x_0:\cdots:x_n]\in\mathbb P_K^n
\mid F(x_0,\ldots,x_n)=0\}
$$

is called the *projective zero locus* of $F$.

To determine $V_+(F)$, we can use the disjoint decomposition

$$
\mathbb P_K^n=D_+(X_0)\mathbin{\uplus}V_+(X_0),
$$

and likewise for any other variable. In the chart $D_+(X_0)\cong\mathbb A_K^n$, we set $X_0=1$ and solve

$$
F(1,X_1,\ldots,X_n)=0.
$$

The polynomial may become inhomogeneous, one variable is eliminated, and the ambient dimension stays the same, but the problem becomes affine. On $V_+(X_0)\cong\mathbb P_K^{n-1}$, we set $X_0=0$ and solve

$$
F(0,X_1,\ldots,X_n)=0.
$$

Here one variable is again eliminated, the polynomial remains homogeneous, and the dimension of the projective space decreases by one.

> **Editorial note - dehomogenisation.** The source displays the malformed expressions $F\{1/X_0\}$ and $F\{0/X_0\}$. The immediately preceding prose specifies the substitutions $X_0=1$ and $X_0=0$. This edition writes the intended polynomials explicitly as $F(1,X_1,\ldots,X_n)$ and $F(0,X_1,\ldots,X_n)$.

<!-- upstream_entity: Der Projektive Raum/Homogenes lineares Polynom/Nullstellenmenge/Beispiel -->

### Example 27.7: homogeneous linear polynomials {#br-ak-2012-l27-ex-03}

The simplest homogeneous polynomials in $K[X_0,\ldots,X_n]$ are those of degree one,

$$
F=a_0X_0+a_1X_1+\cdots+a_nX_n,
$$

with coefficients not all zero. The affine zero locus $V(F)$ in $\mathbb A_K^{n+1}$ is an $n$-dimensional affine space through the origin. The projective zero locus $V_+(F)$ in $\mathbb P_K^n$ is isomorphic to a projective space of dimension $n-1$.

> **Editorial note - index of the linear term.** The source writes $a_0X_0+a_1X_0+\cdots+a_nX_n$. The second term must use $X_1$ for the expression to be a general linear form in the variables $X_0,\ldots,X_n$.

<!-- upstream_entity: Polynomring/Homogenes Ideal/Definition -->

### Definition 27.8: homogeneous ideal {#br-ak-2012-l27-def-03}

Let $K$ be a field and let

$$
\mathfrak a\subseteq K[X_1,\ldots,X_n]
$$

be an ideal. The ideal $\mathfrak a$ is called *homogeneous* if, for every $H\in\mathfrak a$ with homogeneous decomposition

$$
H=\sum_i H_i,
$$

every homogeneous component $H_i$ also belongs to $\mathfrak a$.

<!-- upstream_entity: Der projektive Raum/Nullstellengebilde zu einem homogenen Ideal/Definition -->

### Definition 27.9: projective variety {#br-ak-2012-l27-def-04}

For a homogeneous ideal

$$
\mathfrak a\subseteq K[X_0,\ldots,X_n],
$$

the set

$$
V_+(\mathfrak a)
=
\{P\in\mathbb P_K^n
\mid F(P)=0\text{ for every homogeneous }F\in\mathfrak a\}
$$

is called the *projective zero locus* or *projective variety* of $\mathfrak a$.

<!-- upstream_entity: Der projektive Raum/Mit Zariski-Topologie/Definition -->

### Definition 27.10: the Zariski topology on projective space {#br-ak-2012-l27-def-05}

Projective space $\mathbb P_K^n$ is equipped with the *Zariski topology* by declaring the sets

$$
V_+(\mathfrak a)\subseteq\mathbb P_K^n,
$$

for every homogeneous ideal

$$
\mathfrak a\subseteq K[X_0,\ldots,X_n],
$$

to be the closed sets.

Thus the open sets of projective space have the form

$$
D_+(\mathfrak a)
:=
\mathbb P_K^n\setminus V_+(\mathfrak a).
$$

In particular, each standard open set $D_+(X_i)$ is isomorphic to an affine space of dimension $n$.

<!-- upstream_entity: Der projektive Raum/Punkt ist abgeschlossen/Beschreibung/Bemerkung -->

### Remark 27.11: projective points are closed {#br-ak-2012-l27-rem-01}

Let

$$
P=[a_0:\cdots:a_n]\in\mathbb P_K^n.
$$

The point $P$ is closed. More precisely,

$$
P=V_+(\mathfrak a_P),
\qquad
\mathfrak a_P
=
(a_iX_j-a_jX_i\mid 0\leq i,j\leq n).
$$

If $a_0\ne0$, this ideal can also be written as

$$
\mathfrak a_P
=
\left(X_j-\frac{a_j}{a_0}X_0\ \middle|\ j\ne0\right);
$$

the generators $a_iX_j-a_jX_i$ with $i\ne0$ are then redundant. This ideal is clearly homogeneous, and $P\in V_+(\mathfrak a_P)$. If

$$
Q=[b_0:\cdots:b_n]\in V_+(\mathfrak a_P),
$$

then, since $a_0\ne0$,

$$
b_j-\frac{a_j}{a_0}b_0=0
$$

for every $j$. Hence

$$
(b_0,\ldots,b_n)
=
\frac{b_0}{a_0}(a_0,\ldots,a_n),
$$

so $Q=P$ as projective points.

The ideal $\mathfrak a_P$ is not a maximal ideal in the polynomial ring. It is a homogeneous prime ideal: the quotient by it is isomorphic to a polynomial ring in one variable. In $\mathbb A_K^{n+1}$, this ideal defines the line through the origin corresponding to the projective point $P$.

> **Editorial note - maximality claim.** The source states that $\mathfrak a_P$ is maximal among all homogeneous ideals other than the irrelevant ideal $(X_0,\ldots,X_n)$. This claim is false without further conditions. For example, after choosing $a_0\ne0$, the homogeneous ideal $\mathfrak a_P+(X_0^2)$ lies strictly between $\mathfrak a_P$ and the irrelevant ideal. This edition retains the correct and necessary statement: $\mathfrak a_P$ is a homogeneous prime ideal and defines exactly the projective point $P$.

There is no natural map from all of $\mathbb A_K^{n+1}$ to $\mathbb P_K^n$, since the origin does not determine a line. There is, however, a natural map

$$
\begin{aligned}
\mathbb A_K^{n+1}\setminus\{0\}&\longrightarrow\mathbb P_K^n,\\
(x_0,\ldots,x_n)&\longmapsto[x_0:\cdots:x_n].
\end{aligned}
$$

This map sends a nonzero point to the line through that point and the origin. It is called the *canonical map* or *cone map*. The inverse image of $D_+(X_i)$ under this map is $D(X_i)$.

## Projective space over $\mathbb R$ and $\mathbb C$ {#br-ak-2012-l27-s03}

We now develop a topological picture of projective space for $\mathbb K=\mathbb R$ and $\mathbb K=\mathbb C$. The real $n$-dimensional sphere is

$$
S^n
=
\{x\in\mathbb R^{n+1}\mid\lVert x\rVert=1\},
$$

where

$$
\lVert x\rVert=\sqrt{x_0^2+\cdots+x_n^2}
$$

is the Euclidean norm.

<!-- upstream_entity: Projektiver Raum/R oder C/Repräsentiert durch Sphäre/Fakt -->

### Theorem 27.12: representation by spheres {#br-ak-2012-l27-thm-02}

Real projective space $\mathbb P_{\mathbb R}^n$ can be represented by the sphere $S^n\subseteq\mathbb R^{n+1}$ modulo the equivalence relation identifying each pair of antipodal points.

Complex projective space $\mathbb P_{\mathbb C}^n$ can be represented by the sphere

$$
S^{2n+1}\subseteq\mathbb R^{2n+2}\cong\mathbb C^{n+1}
$$

modulo the equivalence relation identifying $z,w\in S^{2n+1}$ if

$$
z=\lambda w
$$

for some $\lambda\in S^1\subseteq\mathbb C$.

<!-- upstream_entity: Projektiver Raum/R oder C/Repräsentiert durch Sphäre/Fakt/Beweis -->

#### Proof {#br-ak-2012-l27-thm-02-proof}

We treat the real and complex cases together. Each point of the sphere $S$ determines a real or complex line through the origin in the ambient space, and hence a projective point. Two points $z,w\in S$ determine the same line precisely when

$$
z=\lambda w
$$

for some $\lambda\in\mathbb K$. Multiplicativity of the norm gives

$$
\lVert z\rVert=|\lambda|\lVert w\rVert.
$$

Since both norms equal one, $|\lambda|=1$. In the real case this means $\lambda=\pm1$, so the identified points form antipodal pairs. In the complex case it means $\lambda\in S^1\subseteq\mathbb C$. $\square$

Altogether, we have surjective maps

$$
S^n\subseteq\mathbb R^{n+1}\setminus\{0\}
\longrightarrow\mathbb P_{\mathbb R}^n
$$

in the real case, and

$$
S^{2n+1}\subseteq\mathbb R^{2n+2}\setminus\{0\}
\cong\mathbb C^{n+1}\setminus\{0\}
\longrightarrow\mathbb P_{\mathbb C}^n
$$

in the complex case. Real and complex projective spaces are equipped with the quotient topology of the metric topology of the real vector space. Thus $U\subseteq\mathbb P_{\mathbb K}^n$ is declared open if its inverse image in $\mathbb A_{\mathbb K}^{n+1}\setminus\{0\}$ is open. Equivalently, its inverse image on the corresponding sphere is open. With this metric or natural topology, the maps above are continuous.

<!-- upstream_entity: Projektiver Raum/R oder C/Offen überdeckt und Mannigfaltigkeit/Fakt -->

### Lemma 27.13: open charts and manifold structure {#br-ak-2012-l27-lem-02}

For real and complex projective spaces, the sets $D_+(X_i)$ are open in the natural topology and homeomorphic to $\mathbb R^n$ and $\mathbb C^n$, respectively. In particular, real and complex projective spaces are topological manifolds.

<!-- upstream_entity: Projektiver Raum/R oder C/Offen überdeckt und Mannigfaltigkeit/Fakt/Beweis -->

#### Proof {#br-ak-2012-l27-lem-02-proof}

The inverse image of $D_+(X_i)$ under the canonical map

$$
\mathbb A_{\mathbb K}^{n+1}\setminus\{0\}
\longrightarrow\mathbb P_{\mathbb K}^n
$$

is $D(X_i)$, the complement of an $n$-dimensional vector subspace, and is therefore open in the natural topology. Consider the continuous map

$$
\mathbb K^n
\cong V(X_i-1)
\subset D(X_i)
\longrightarrow D_+(X_i).
$$

This map is bijective. To show that it is a homeomorphism, it suffices to show that it is open. Let

$$
U\subseteq V(X_i-1)\cong\mathbb K^n
$$

be open and let $U'$ be its image in $D_+(X_i)$. The inverse image of $U'$ in $D(X_i)$ is the cone

$$
U''=\{\lambda P\mid \lambda\in\mathbb K^\times, P\in U\}.
$$

The map

$$
\begin{aligned}
\mathbb K^\times\times V(X_i-1)&\longrightarrow D(X_i),\\
(\lambda,P)&\longmapsto\lambda P
\end{aligned}
$$

is a homeomorphism, with inverse

$$
Q\longmapsto\left(Q_i,\frac{Q}{Q_i}\right).
$$

Consequently,

$$
U''\cong\mathbb K^\times\times U
$$

is open in $D(X_i)$. By the definition of the quotient topology, $U'$ is open. Thus the bijection is a homeomorphism. $\square$

> **Editorial note - neighbourhood in the cone.** The source chooses an open ball $B$ around $P$ and then asserts without qualification that its cone lies in $U''$. For this conclusion to hold, the ball must be chosen with $P\in B\subseteq U$. This edition gives an equivalent global argument using the homeomorphism $\mathbb K^\times\times V(X_i-1)\cong D(X_i)$, which also closes this gap.

![A blue sphere shown in three dimensions, representing the complex projective line](authority/assets/Blue-sphere.png)

*The projective line over $\mathbb C$ is a sphere. Historical course credit: Kieff; the frozen Commons description credits Lucas Vieira (LucasVB). Public domain; local file: `authority/assets/Blue-sphere.png`.*

<!-- upstream_entity: Projektiver Raum/R oder C/Kompakt/Fakt -->

### Corollary 27.14: compactness and the Hausdorff property {#br-ak-2012-l27-cor-01}

Real and complex projective spaces are compact and Hausdorff in their natural topology.

<!-- upstream_entity: Projektiver Raum/R oder C/Kompakt/Fakt/Beweis -->

#### Proof {#br-ak-2012-l27-cor-01-proof}

For each such projective space, there is a continuous surjective map from the corresponding sphere. The sphere is closed and bounded in a finite-dimensional real vector space, and is therefore compact by the Heine–Borel Theorem. A continuous image of a compact space is compact. Hence real and complex projective spaces are compact.

Now take two distinct points

$$
P,Q\in\mathbb P_{\mathbb K}^n,
\qquad
\mathbb K\in\{\mathbb R,\mathbb C\}.
$$

Since $\mathbb K$ is infinite, there is a homogeneous linear form $L$ vanishing at neither $P$ nor $Q$. Indeed, in the dual space the forms vanishing at $P$ and those vanishing at $Q$ each form a proper hyperplane, and the union of these two hyperplanes does not fill the entire dual space.

By a linear change of coordinates, $L$ can be made one of the homogeneous coordinates. Then

$$
P,Q\in D_+(L)\cong\mathbb K^n.
$$

By Lemma 27.13, this chart is homeomorphic to a real or complex Euclidean space and is therefore Hausdorff. Hence $P$ and $Q$ have disjoint open neighbourhoods. Thus the whole projective space is Hausdorff. $\square$

> **Editorial note - two points in one chart.** The source assumes that any two projective points lie together in one of the standard charts $D_+(X_i)$. This is false, for example for $[1:0]$ and $[0:1]$ in $\mathbb P^1$. This edition chooses a linear form $L$ vanishing at neither point and uses a change of coordinates to obtain an affine chart $D_+(L)$ containing both.

> **Editorial note - broken reference.** In the compactness argument, the source refers to “Fakt *****”. This edition replaces the broken placeholder with the standard result actually used: a continuous image of a compact space is compact.
