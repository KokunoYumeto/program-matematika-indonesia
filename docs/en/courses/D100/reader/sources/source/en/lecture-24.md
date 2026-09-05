---
title: "Lecture 24 - Tangent Lines and Formal Power Series Rings"
stable_id: br-ak-2012-l24
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24"
upstream_pageid: 50730
upstream_revid: 933672
upstream_timestamp: "2024-05-06T16:57:23Z"
upstream_mediawiki_sha1: af86fa9893c96376f910495b9a5d0c8be417b09e
source_url: "https://de.wikiversity.org/w/index.php?oldid=933672"
authority_manifest: authority/wikiversity/unit-24/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 3731896a5980c565d9d69a2e01eee497f13b6f449f2f9c701fce726271c026a5
lecture_xml: authority/wikiversity/unit-24/lecture-24.xml
lecture_xml_sha256: 0dd11d94f88e81036d00c2662c6377e13e25d749bed7721902ec75c737251bd3
lecture_expanded_tex: authority/wikiversity/unit-24/lecture-24-expanded.tex
lecture_expanded_tex_sha256: b391d18cc0cea33afedfff5e6db46842d2ef6504843336b71f44eda448f12f5e
lecture_dependency_identity_rows_sha256: 861c2d4566a137c9c3d791480bfa2f1f36a7885798f54f34c8e60557d34e75b2
license: "Current semantic course text and this translation: CC BY-SA 4.0. The official 2012 PDF file-description surface also records the legacy CC BY-SA 2.0 Germany route. Unit 24 contains no substantive media; no blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; official-PDF legacy file-description notice: CC BY-SA 2.0 Germany; official-PDF current print-version notice: CC BY-SA 4.0; no blanket relicensing claim."
license_evidence: "authority/UNIT_24_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-24.csv; authority/ASSET_CLOSURE-unit-24.json"
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 22
source_corrections: 9
reader_media_positions: 0
---

# Lecture 24: Tangent Lines and Formal Power Series Rings {#br-ak-2012-l24}

<!-- upstream_entity: Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24#Tangenten bei Parametrisierungen -->

## Tangent lines from parametrisations {#br-ak-2012-l24-s01}

<!-- upstream_entity: Algebraische Kurven/Rationale Parametrisierung/Verhältnis Tangenten/Fakt -->

### Theorem 24.1: the derivative vector of a parametrisation {#br-ak-2012-l24-thm-01}

Let $K$ be an infinite field and

$$
\varphi\colon \mathbb A_K^1\longrightarrow \mathbb A_K^n
$$

a map given by $n$ polynomials in one variable,

$$
\varphi=\bigl(\varphi_1(t),\ldots,\varphi_n(t)\bigr),
$$

whose image is contained in the curve

$$
C=V(F_1,\ldots,F_m).
$$

Take $Q\in\mathbb A_K^1$ and

$$
P=\varphi(Q)\in C.
$$

Then the derivative vector

$$
\left(
  \frac{\partial\varphi_1}{\partial t}(Q),\ldots,
  \frac{\partial\varphi_n}{\partial t}(Q)
\right)
$$

lies in the kernel of the linear tangent map

$$
(TF)_P\colon\mathbb A_K^n\longrightarrow\mathbb A_K^m
$$

defined by the Jacobian matrix

$$
\left(
  \frac{\partial F_i}{\partial X_j}(P)
\right)_{ij}.
$$

If $n=2$, the derivatives $\varphi_1'(Q)$ and $\varphi_2'(Q)$ do not both
vanish, and $P$ is a smooth point of $C$, then

$$
\left(
  \frac{\partial\varphi_1}{\partial t}(Q),
  \frac{\partial\varphi_2}{\partial t}(Q)
\right)
$$

determines the direction of the tangent line to $C$ at $P$.

<!-- upstream_entity: Algebraische Kurven/Rationale Parametrisierung/Verhältnis Tangenten/Fakt/Beweis -->

#### Proof {#br-ak-2012-l24-thm-01-proof}

Write $F=(F_1,\ldots,F_m)$. Since

$$
\varphi\bigl(\mathbb A_K^1\bigr)\subseteq V(F_1,\ldots,F_m),
$$

the composite $F\circ\varphi$ is the constant map to the origin. Since
$K$ is infinite, each component polynomial representing $F_i\circ\varphi$
is the zero polynomial. The formal chain rule for polynomials therefore gives

$$
0=(T(F\circ\varphi))_Q=(TF)_P\circ(T\varphi)_Q.
$$

Thus the image of $(T\varphi)_Q$, spanned by the derivative vector above,
is contained in the kernel of $(TF)_P$.

In the plane case stated in the final part of the theorem, choose a reduced
defining polynomial $H$ for $C$. The same chain-rule argument with $H$ in
place of the tuple $F$ puts the derivative vector in $\ker(dH_P)$. This
kernel is one-dimensional because $P$ is smooth. The image of
$(T\varphi)_Q$ is also one-dimensional because the derivative vector is
nonzero. The inclusion is therefore an equality, so that vector determines
the tangent direction. $\square$

> **Edition note — defining equations.** The source treats the kernel of
> the original Jacobian as necessarily one-dimensional in the plane case.
> This requires equations generating the reduced curve's ideal near $P$;
> arbitrary equations with the same zero locus need not do so. For example,
> $Y^2=0$ defines the line $Y=0$ set-theoretically but has zero differential
> on that line. The argument above uses a reduced equation for the final
> assertion; the initial chain-rule inclusion for all $F_i$ is unchanged.

<!-- upstream_entity: Endlicher Körper/(t^q-t,t^q-t)/Gerade/Ableitung ist keine Tangente/Beispiel -->

### Example 24.2: why the field must be infinite {#br-ak-2012-l24-ex-01}

Let $K$ be a finite field with

$$
q=p^e
$$

elements, where $p$ is prime and $e\geq1$. The map

$$
\begin{aligned}
\mathbb A_K^1&\longrightarrow\mathbb A_K^2,\\
t&\longmapsto(t^q-t,t^q-t)
\end{aligned}
$$

sends every $K$-rational point to the single image point $(0,0)$, since
$t^q=t$ for every $t\in K$. However, the formal derivative vector of this
polynomial parametrisation is

$$
(-1,-1).
$$

Thus a map on $K$-rational points can be constant in positive characteristic
even though the formal derivative of its defining polynomials is nonzero.
The origin is a smooth point on every line

$$
C=V(aX+bY),
$$

with $(a,b)\ne(0,0)$.

Its tangent direction is the kernel of the linear form $aX+bY$, but this
form annihilates $(-1,-1)$ only when $a=-b$. The assumption that $K$ is
infinite in Theorem 24.1 therefore cannot be omitted.

> **Edition note.** Constancy here refers explicitly to the function on
> $K$-rational points. The morphism defined by the pair of polynomials
> $(t^q-t,t^q-t)$ is not constant. This distinction prevents “constant”
> from being mistaken for a statement about the polynomials or the morphism
> itself.

<!-- upstream_entity: Ebene algebraische Kurve/x^2-y^2+y^3/Tangente unter Parametrisierung/t ist 2/Beispiel -->

### Example 24.3: a tangent line from a parametrisation {#br-ak-2012-l24-ex-02}

In this example we work over a field $K$ of characteristic zero. Returning
to Example 6.3, consider the curve

$$
V(y^2-x^2-x^3)
$$

with parametrisation

$$
(\varphi(t),\psi(t))
=\bigl(t^2-1,t(t^2-1)\bigr)
=(x,y).
$$

For

$$
F=y^2-x^2-x^3,
$$

the partial derivatives are

$$
\frac{\partial F}{\partial x}=-2x-3x^2
\qquad\text{and}\qquad
\frac{\partial F}{\partial y}=2y.
$$

The Jacobian matrix of the parametrisation, viewed as a row vector, is

$$
\left(
  \frac{\partial\varphi}{\partial t},
  \frac{\partial\psi}{\partial t}
\right)
=(2t,3t^2-1).
$$

With $P=(\varphi(t),\psi(t))$, the formal polynomial chain-rule computation
indeed gives

$$
\begin{aligned}
&\left(
  \frac{\partial F}{\partial x}(P),
  \frac{\partial F}{\partial y}(P)
\right)
\begin{pmatrix}2t\\3t^2-1\end{pmatrix}\\
&=\left(
  -2(t^2-1)-3(t^2-1)^2,
  2(t^3-t)
\right)
\begin{pmatrix}2t\\3t^2-1\end{pmatrix}\\
&=-4t(t^2-1)-6t(t^2-1)^2
  +2(t^3-t)(3t^2-1)\\
&=-4t^3+4t-6t^5+12t^3-6t
  +6t^5-2t^3-6t^3+2t\\
&=0.
\end{aligned}
$$

For $t=2$, for example, the image point is

$$
P=(3,6).
$$

The derivative vector is $(4,11)$, while the partial derivatives at $P$
give the gradient $(-33,12)$, which is perpendicular to the tangent
direction vector. The tangent line can be written as

$$
\bigl\{(3,6)+s(4,11)\mid s\in K\bigr\}
$$

or as

$$
V(-11x+4y+9).
$$

> **Edition note.** The source does not specify a characteristic restriction
> for this numerical example. This edition restricts it to characteristic
> zero because the coefficients $2$, $3$, and $11$, as well as the particular
> value $t=2$, can change or vanish upon reduction in small positive
> characteristic. In positive characteristic, smoothness and the tangent
> direction must be checked again over the field in question.

<!-- upstream_entity: Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24#Tangenten bei Raumkurven -->

## Tangent lines to space curves {#br-ak-2012-l24-s02}

<!-- upstream_entity: Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24#Tangenten bei Raumkurven/Jacobi-Absatz -->

Although our discussion is mainly restricted to plane curves, derivatives
can also be used to define smooth and singular points on curves in
higher-dimensional spaces, and indeed on arbitrary varieties. As an
illustration, suppose that a space curve is given by two polynomials with
no common component,

$$
F,G\in K[X,Y,Z].
$$

Not every space curve can be described in this way. For $P\in C=V(F,G)$,
assume also that $(F,G)$ generates the ideal of the reduced curve locally
at $P$. Consider again the map given by the Jacobian matrix

$$
\left(
\begin{array}{ccc}
\dfrac{\partial F}{\partial x}&
\dfrac{\partial F}{\partial y}&
\dfrac{\partial F}{\partial z}\\[4pt]
\dfrac{\partial G}{\partial x}&
\dfrac{\partial G}{\partial y}&
\dfrac{\partial G}{\partial z}
\end{array}
\right)_P
\colon\mathbb A_K^3\longrightarrow\mathbb A_K^2.
$$

The point $P$ is smooth on the curve precisely when this matrix has rank
two. Its kernel is then one-dimensional and defines the tangent line.

> **Edition note — reduced-curve hypothesis.** The source assumes only that
> $F$ and $G$ have no common component. For the intrinsic smoothness of the
> reduced curve, this alone is insufficient: $F=X^2$, $G=Y$ have no common
> component and their zero locus is the smooth $Z$-axis, but their Jacobian
> has rank one there. The added local ideal-generation hypothesis makes the
> stated rank criterion applicable to the reduced curve.

<!-- upstream_entity: Algebraische Raumkurven/Schnitt von zwei gleichgroßen Zylindern/Singuläre Punkte/Beispiel -->

### Example 24.4: the intersection of two cylinders {#br-ak-2012-l24-ex-03}

Assume $\operatorname{char}(K)\ne2$. Returning to Example 4.6, consider the
intersection $C$ of the two cylinders

$$
F=x^2+y^2-1
\qquad\text{and}\qquad
G=y^2+z^2-1.
$$

Their partial derivative vectors are

$$
\partial F=(2x,2y,0)
\qquad\text{and}\qquad
\partial G=(0,2y,2z).
$$

A singular point occurs when the map defined by this Jacobian matrix has
rank at most one, that is, when the two partial derivative vectors are
linearly dependent and the point actually lies on the corresponding variety.
Linear dependence requires

$$
xy=xz=yz=0.
$$

On the curve with both parameters equal to $1$, the curve equations exclude
the cases $x=y=0$ and $y=z=0$. Thus the remaining candidates satisfy

$$
x=z=0,
$$

and at these values the vectors are indeed linearly dependent for every
$y$. When $x=z=0$, only

$$
y=\pm1
$$

give points on the curve. These are therefore exactly the two singular
points of $C$. They are also the two intersection points of the two circles
that form the irreducible components of $C$, as in Example 4.6.

For the version with unequal radii, write $r_1,r_2\in K^\times$ for the
*nonzero squared radii* and use

$$
F=x^2+y^2-r_1,
\qquad
G=y^2+z^2-r_2.
$$

If the given quantities are the radii $\rho_1$ and $\rho_2$ themselves,
then $r_i=\rho_i^2$. The dependence condition $xy=xz=yz=0$ must now be
solved together with the two curve equations. In the case $x=z=0$, these
equations become

$$
y^2=r_1
\qquad\text{and}\qquad
y^2=r_2.
$$

Thus this case forces $r_1=r_2$. The case $x=y=0$ forces $r_1=0$, while
$y=z=0$ forces $r_2=0$. All three are impossible when $r_1,r_2\ne0$ and
$r_1\ne r_2$. The intersection curve is therefore smooth when the squared
radii are nonzero and distinct. For real cylinders with positive radii,
nonvanishing is automatic.

> **Edition note.** The frozen live semantic text uses $G=y^2+z^2-1$; the
> historical official PDF incorrectly prints $G=x^2+z^2-1$. This edition
> follows the live semantic text. The source also calls $r_1,r_2$ “radii”
> but then uses the equations $y^2=r_i$; here these parameters are clarified
> as squared radii. Their nonvanishing is also made explicit, since if
> $r_1=0$ or $r_2=0$, the Jacobian rank can drop even when $r_1\ne r_2$.
> The assumption $\operatorname{char}(K)\ne2$ is made visible because all
> the displayed derivatives vanish in characteristic $2$.

<!-- upstream_entity: Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24#Potenzreihenringe -->

## Power series rings {#br-ak-2012-l24-s03}

<!-- upstream_entity: Potenzreihenring/Allgemein und eine Variable/Einführung/Textabschnitt -->

<!-- upstream_entity: Potenzreihenring/Endlich viele Variablen/Formale Potenzreihe/Definition -->

### Definition 24.5: formal power series {#br-ak-2012-l24-def-01}

Let $R$ be a commutative ring and $T_1,\ldots,T_n$ a set of variables. A
*formal power series* is an expression of the form

$$
F=\sum_\nu a_\nu T^\nu
 =\sum_\nu a_\nu T_1^{\nu_1}\cdots T_n^{\nu_n},
$$

where

$$
a_\nu\in R
$$

for every multi-index

$$
\nu=(\nu_1,\ldots,\nu_n)\in\mathbb N^n.
$$

Two power series are added coefficientwise and multiplied in the same way
as polynomials. In one variable,

$$
\begin{aligned}
F\cdot G
&=\left(\sum_{i=0}^{\infty}a_iT^i\right)
  \left(\sum_{j=0}^{\infty}b_jT^j\right)\\
&=\sum_{k=0}^{\infty}c_kT^k,
\end{aligned}
$$

where

$$
c_k=\sum_{i=0}^k a_i b_{k-i}.
$$

<!-- upstream_entity: Potenzreihenring/Endlich viele Variablen/Definition -->

### Definition 24.6: the power series ring {#br-ak-2012-l24-def-02}

Let $R$ be a commutative ring. The notation

$$
R[\![X_1,\ldots,X_n]\!]
$$

denotes the *power series ring in $n$ variables*, also called the *ring of
formal power series in $n$ variables*.

<!-- upstream_entity: Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 24#Potenzreihenringe/zusatz1 -->

We shall mainly use the one-variable power series ring $K[\![T]\!]$ over
a field $K$. Under suitable hypotheses, power series rings allow us to find
“formal parametrisations” of branches of algebraic curves at a point; this
will be treated in the next lecture. First we need to understand some basic
properties of power series rings.

> **Edition note — scope of existence.** The source states this for
> arbitrary algebraic curves at every point over a general field. Some
> hypothesis, or a suitable scalar extension, is necessary. For example,
> over $\mathbb R$ the curve $V(X^2+Y^2)$ admits no nonconstant formal
> parametrisation through the origin by series in $\mathbb R[\![T]\!]$.
> Writing the two series as $G=\sum a_iT^i$ and $H=\sum b_iT^i$, if $n$
> were the first degree occurring in either one, the coefficient of
> $T^{2n}$ would be $a_n^2+b_n^2=0$, forcing $a_n=b_n=0$. The next lecture
> proves existence for a tangent of multiplicity one and also records an
> obstruction in a multiple-tangent example.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Konstante nicht null, dann Einheit/Fakt -->

### Theorem 24.7: the unit criterion {#br-ak-2012-l24-thm-02}

Let $K$ be a field. A formal power series

$$
F=\sum_{n=0}^{\infty}a_nT^n\in K[\![T]\!]
$$

is a unit if and only if its constant term satisfies $a_0\ne0$.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Konstante nicht null, dann Einheit/Fakt/Beweis -->

#### Proof {#br-ak-2012-l24-thm-02-proof}

The condition is necessary because formal evaluation at $T=0$,

$$
\begin{aligned}
\operatorname{ev}_0\colon K[\![T]\!]&\longrightarrow K,\\
F&\longmapsto F(0)=a_0,
\end{aligned}
$$

is a ring homomorphism. A unit must therefore map to a nonzero element of
$K$.

Conversely, assume $a_0\ne0$. We shall construct

$$
G=\sum_{j=0}^{\infty}b_jT^j
$$

such that

$$
FG=\left(\sum_{i=0}^{\infty}a_iT^i\right)
   \left(\sum_{j=0}^{\infty}b_jT^j\right)=1.
$$

For the constant coefficient we require

$$
a_0b_0=1,
$$

which has the unique solution $b_0=a_0^{-1}$. Inductively, suppose that
$b_j$ has been constructed for $j<n$ so that all coefficients $c_k$ of
$FG$ with $1\leq k<n$ are zero. The condition for the $n$th coefficient is

$$
0=c_n=a_0b_n+a_1b_{n-1}+\cdots+a_{n-1}b_1+a_nb_0.
$$

All values except $b_n$ have already been determined. Since $a_0\ne0$,
this equation has exactly one solution for $b_n$. This induction constructs
an inverse $G$ for $F$. $\square$

> **Edition note.** The live semantic text ends its explanation of the
> constant-term homomorphism with an unfilled exercise placeholder. This
> edition does not retain that dangling reference; evaluation at $T=0$ is
> stated and used directly.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Diskreter Bewertungsring/Fakt -->

### Corollary 24.8: a discrete valuation ring {#br-ak-2012-l24-cor-01}

If $K$ is a field, then the one-variable power series ring

$$
R=K[\![T]\!]
$$

is a discrete valuation ring.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Diskreter Bewertungsring/Fakt/Beweis -->

#### Proof {#br-ak-2012-l24-cor-01-proof}

First, $R$ is a local ring with maximal ideal

$$
\mathfrak m=(T).
$$

Indeed, if a power series $F$ is not a unit, Theorem 24.7 says that its
constant term is zero. Consequently,

$$
F=T\widetilde F
$$

for the power series $\widetilde F$ obtained by shifting the indices.

The absence of zero divisors follows by considering initial terms. If $F$
and $G$ are nonzero power series, write

$$
F=a_kT^k+a_{k+1}T^{k+1}+\cdots
$$

and

$$
G=b_\ell T^\ell+b_{\ell+1}T^{\ell+1}+\cdots,
$$

where $a_k\ne0$ and $b_\ell\ne0$. Since all earlier coefficients vanish,
the coefficient of degree $k+\ell$ in their product is

$$
c_{k+\ell}=a_kb_\ell\ne0.
$$

It remains to show that $R$ is Noetherian; in fact, it is a principal ideal
domain. For a nonzero ideal $I\subseteq R$, let $j$ be the smallest index
of a nonzero coefficient among all series in $I$. Choose $H\in I$ with
initial term of degree $j$. Then $H=T^jU$, where $U$ is a unit by Theorem
24.7, so $T^j\in I$. The minimality of $j$ also gives $I\subseteq(T^j)$,
hence

$$
I=(T^j).
$$

Thus $R$ is a local principal ideal domain with maximal ideal $(T)$, and
is therefore a discrete valuation ring. $\square$

> **Edition note.** Both the live semantic text and the historical PDF
> write the second term of $G$ as $a_{\ell+1}T^{\ell+1}$. The correct
> coefficient family is $b_{\ell+1}$, as displayed above.

Power series can not only be added and multiplied. Under certain additional
conditions, one power series can also be substituted into another. This
operation corresponds to composition of maps.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Einsetzen von Potenzreihen mit Konstante null/Definition -->

### Definition 24.9: substitution of power series {#br-ak-2012-l24-def-03}

Let $K$ be a field and

$$
F=\sum_{i=0}^{\infty}a_iT^i\in K[\![T]\!].
$$

Let

$$
G=\sum_{j=0}^{\infty}b_jT^j
$$

be another power series with constant term $b_0=0$. The series

$$
\begin{aligned}
F(G)
&=a_0+a_1\left(\sum_{j=0}^{\infty}b_jT^j\right)
 +a_2\left(\sum_{j=0}^{\infty}b_jT^j\right)^2\\
&\quad
 +a_3\left(\sum_{j=0}^{\infty}b_jT^j\right)^3+\cdots\\
&=\sum_{k=0}^{\infty}c_kT^k
\end{aligned}
$$

is called the *composite power series*. Its coefficients are determined by

$$
c_0=a_0
$$

and, for $k\geq1$,

$$
c_k=\sum_{s=0}^k a_s
\left(
  \sum_{j_1+\cdots+j_s=k}b_{j_1}\cdots b_{j_s}
\right),
$$

where the inner sum runs over all ordered $s$-tuples

$$
(j_1,\ldots,j_s)\in\mathbb N_+^s.
$$

Since $b_0=0$, only indices $j\geq1$ occur, so every sum determining a
coefficient is finite. These formulas agree with ordinary polynomial
substitution when $F$ and $G$ are polynomials. Substituting power series
into power series produces substitution homomorphisms between power series
rings.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Einsetzen ergibt Ringhomomorphismus/Fakt -->

### Lemma 24.10: substitution is a homomorphism {#br-ak-2012-l24-lem-01}

Let $K$ be a field and $G\in K[\![S]\!]$ a power series with constant
term zero. Substitution of $G$ defines a $K$-algebra homomorphism

$$
\begin{aligned}
K[\![T]\!]&\longrightarrow K[\![S]\!],\\
F&\longmapsto F(G).
\end{aligned}
$$

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/Einsetzen ergibt Ringhomomorphismus/Fakt/Beweis -->

#### Proof {#br-ak-2012-l24-lem-01-proof}

The map is well defined. To show that it is a ring homomorphism, we need
only compare the relevant coefficients. Each depends on only finitely many
coefficients of the series involved. The required identities therefore
follow from the polynomial case. The map also preserves scalars in $K$,
so it is a $K$-algebra homomorphism. $\square$

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/T+../Transformierbar auf T/Fakt -->

### Lemma 24.11: a formal change of parameter {#br-ak-2012-l24-lem-02}

Let $K$ be a field and

$$
G=\sum_{j=0}^{\infty}b_jT^j\in K[\![T]\!]
$$

with $b_0=0$ and $b_1\ne0$. Then the substitution homomorphism determined by

$$
T\longmapsto G
$$

is a $K$-algebra automorphism of $K[\![T]\!]$.

<!-- upstream_entity: Formaler Potenzreihenring/Eine Variable/T+../Transformierbar auf T/Fakt/Beweis -->

#### Proof {#br-ak-2012-l24-lem-02-proof}

We first construct a power series

$$
F=\sum_{i=0}^{\infty}a_iT^i
$$

with

$$
F(G)=T.
$$

We must have $a_0=0$ and $a_1=b_1^{-1}$. For $k\geq2$, suppose inductively
that the coefficients of $F$ through $a_{k-1}$ have been constructed to give
the required coefficients. By Definition 24.9, the condition on $c_k$ is

$$
\begin{aligned}
0=c_k
&=\sum_{s=0}^k a_s
  \left(
    \sum_{j_1+\cdots+j_s=k}b_{j_1}\cdots b_{j_s}
  \right)\\
&=\sum_{s=0}^{k-1}a_s
  \left(
    \sum_{j_1+\cdots+j_s=k}b_{j_1}\cdots b_{j_s}
  \right)
  +a_kb_1^k.
\end{aligned}
$$

Since $b_1\ne0$, this equation determines $a_k$ uniquely.

Now consider the composite

$$
K[\![T]\!]
\xrightarrow{\ T\mapsto F\ }
K[\![T]\!]
\xrightarrow{\ T\mapsto G\ }
K[\![T]\!].
$$

The composite map is substitution $T\mapsto T$, which is the identity.
Therefore the second map, determined by $T\mapsto G$, is surjective. By
Corollary 24.8, $K[\![T]\!]$ is a discrete valuation ring, and its ideals
are known. If the kernel of the second map were nonzero, it would contain
some $T^j$, but its image is $G^j\ne0$. Only the zero ideal can therefore
be the kernel. The map is also injective, hence bijective and a $K$-algebra
automorphism. $\square$
