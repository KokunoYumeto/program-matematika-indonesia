---
title: "Lecture 25 - Power Series Solutions for Algebraic Curves"
stable_id: br-ak-2012-l25
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 25"
upstream_pageid: 50731
upstream_revid: 793525
upstream_timestamp: "2022-08-25T06:09:07Z"
upstream_mediawiki_sha1: c589c3b9586e551eb81d7d941d79a9bc1461fe06
source_url: "https://de.wikiversity.org/w/index.php?oldid=793525"
authority_manifest: authority/wikiversity/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7cafbca7b5fd080529c2019967647ef8ffa823539b2113caaf0ad65e56d6afc1
lecture_xml: authority/wikiversity/unit-25/lecture-25.xml
lecture_xml_sha256: 4063269fa3a4e919790799935760600f5df9fecb1c8a677554188f059b316aa1
lecture_expanded_tex: authority/wikiversity/unit-25/lecture-25-expanded.tex
lecture_expanded_tex_sha256: 47cd10c4b01ead8e51b1fa6e1e020900032bae6517030efd4cc116ef0ba1fe5e
lecture_dependency_identity_rows_sha256: aa14c07698e5e2911790457bee99f6e58a47b68fd5e75520c175ecc2756df8b1
license: "Current semantic course text and this translation: CC BY-SA 4.0. The official 2012 PDF file-description surface also records the legacy CC BY-SA 2.0 Germany route. Unit 25 contains no substantive media; no blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; official-PDF legacy file-description notice: CC BY-SA 2.0 Germany; official-PDF current print-version notice: CC BY-SA 4.0; no blanket relicensing claim."
license_evidence: "authority/UNIT_25_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-25.csv; authority/ASSET_CLOSURE-unit-25.json"
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 9
source_corrections: 4
correction_ids: "AGC-CORR-0091; AGC-CORR-0092; AGC-CORR-0093"
reader_media_positions: 0
---

# Lecture 25: Power Series Solutions for Algebraic Curves {#br-ak-2012-l25}

## Power series solutions for algebraic curves {#br-ak-2012-l25-s01}

<!-- upstream_entity: Ebene algebraische Kurve/Potenzreihenansatz/Einführung und Beispiele/Textabschnitt -->

Let $F\ne 0$ be a polynomial describing a plane algebraic curve $C$, and
assume that

$$
P=(0,0)\in C.
$$

This is no restriction, since it can always be achieved by a translation.
How can we describe the curve near the origin using power series? In other
words, when is there a ring homomorphism determined by nonconstant power
series $G$ and $H$ with constant term zero,

$$
\begin{aligned}
K[X,Y]&\longrightarrow K[[T]],\\
X&\longmapsto G,\\
Y&\longmapsto H,
\end{aligned}
$$

such that

$$
F(G,H)=0?
$$

Equivalently, we seek a ring homomorphism

$$
K[X,Y]/(F)\longrightarrow K[[T]].
$$

Thus the problem is to find power series solutions of the equation

$$
F(X,Y)=0
$$

that describe more precisely the behaviour of the curve around the point
solution $(0,0)$.

The basic approach is a power series ansatz, as also used in the theory of
differential equations. We start with

$$
G=\sum_{k=0}^{\infty}a_kT^k
\qquad\text{and}\qquad
H=\sum_{\ell=0}^{\infty}b_\ell T^\ell,
$$

where the coefficients $a_k$ and $b_\ell$ are initially unknown. Direct
substitution into $F=0$, followed by expansion of the products, produces
an expression that is in principle infinite. For each power $T^k$, however,
the expression for its coefficient is determined by only finitely many
data: the finitely many coefficients of $F$, and only the coefficients of
$G$ and $H$ through degree $k$, are needed.

> **Edition note — coefficient range.** The source says only coefficients
> below degree $k$ are relevant. A degree-$k$ coefficient can be required:
> for $F=X$, the coefficient of $T^k$ in $F(G,H)$ is $a_k$. The
> finite-dependence claim is retained with the corrected bound “through
> degree $k$”.

Since we require

$$
F(G,H)=0,
$$

the coefficients of $F$, $G$, and $H$ must make the coefficient of every
$T^k$ vanish.

We then seek conditions for the existence of solutions, their form, and
their uniqueness. The condition

$$
a_0=b_0=0
$$

is an initial condition expressing that the power series solution passes
through the origin.

A condition on the linear terms of the power series, namely $a_1$ and
$b_1$, emerges immediately. This further justifies interpreting the linear
factors of the lowest-degree homogeneous component $F_m$ in the homogeneous
decomposition of $F$ as tangent-line equations.

<!-- upstream_entity: Ebene algebraische Kurven/Potenzreihenlösung für Punkt/Linearer Term liegt auf Tangente/Fakt -->

### Lemma 25.1: the linear term lies on a tangent line {#br-ak-2012-l25-lem-01}

Let $K$ be an algebraically closed field and

$$
F\in K[X,Y]
$$

a polynomial with homogeneous decomposition

$$
F=F_m+\cdots+F_d,
\qquad d\geq m\geq1,
\qquad F_m\ne0.
$$

Let

$$
F_m=\prod_{\lambda=1}^{m}(u_\lambda X+v_\lambda Y)
$$

be the factorisation of $F_m$ into linear factors. These linear factors
define the tangent lines to the curve

$$
C=V(F)
$$

at $P=(0,0)$. Let

$$
G=\sum_{n=0}^{\infty}a_nT^n
\qquad\text{and}\qquad
H=\sum_{\ell=0}^{\infty}b_\ell T^\ell
$$

be elements of $K[[T]]$ giving a solution of the curve equation through
the origin, that is,

$$
a_0=b_0=0
\qquad\text{and}\qquad
F(G,H)=0.
$$

Then, for some $\lambda$,

$$
u_\lambda a_1+v_\lambda b_1=0.
$$

In other words, the pair of linear terms of the two power series is
constrained by one of the tangent lines.

<!-- upstream_entity: Ebene algebraische Kurven/Potenzreihenlösung für Punkt/Linearer Term liegt auf Tangente/Fakt/Beweis -->

#### Proof {#br-ak-2012-l25-lem-01-proof}

Substitute

$$
G=a_1T+a_2T^2+\cdots
\qquad\text{and}\qquad
H=b_1T+b_2T^2+\cdots
$$

into $F$. A homogeneous component $F_k$ is a sum of terms $c_{ij}X^iY^j$
with $i+j=k$. We can immediately factor out $T^k$ and obtain an expression
of the form

$$
\begin{aligned}
F_k(G,H)
={}&\left(\sum_{i+j=k}c_{ij}a_1^ib_1^j\right)T^k\\
&+\left(\sum_{i+j=k}c_{ij}
\left(ia_1^{i-1}a_2b_1^j
+ja_1^ib_1^{j-1}b_2\right)\right)T^{k+1}
+\cdots.
\end{aligned}
$$

Thus $a_1$ and $b_1$ enter the coefficient of $T^k$ directly through
$F_k$; in general that coefficient also receives more complicated
contributions from $F_\ell$ with $\ell<k$. For $F_m$, there are no lower
homogeneous components. The decisive equation for $a_1$ and $b_1$ is
therefore

$$
\sum_{i+j=m}c_{ij}a_1^ib_1^j=0,
$$

or, equivalently,

$$
F_m(a_1,b_1)=0.
$$

Since $F_m$ is a product of linear factors, the row vector $(a_1,b_1)$ must
annihilate one of them. This is the assertion. $\square$

Note that Lemma 25.1 does not exclude the possibility

$$
a_1=b_1=0.
$$

Indeed, realising a curve by power series along a prescribed tangent line
is possible only under additional conditions; see
[Theorem 25.2](#br-ak-2012-l25-thm-01) and the examples below.

The computational effort needed to determine a power series solution can
be greatly reduced by restricting to “graph solutions”, where one power
series is simply a linear polynomial prescribed by a tangent line and the
other is a power series to be determined. This is often no essential
restriction, as follows from [Lemma 24.11](#br-ak-2012-l24-lem-02). That
lemma lets us easily reparametrise

$$
G,H\in K[[T]]
$$

when their linear terms do not both vanish. Assume

$$
G=a_1T+\cdots,
\qquad a_1\ne0.
$$

Choose a power series $U(T)$ that is the compositional inverse of $G$.
Then

$$
G(U(T))=T
\qquad\text{and}\qquad
H(U(T))=\widetilde H(T).
$$

Following the original map by a power series ring automorphism gives the
composite

$$
K[X,Y]
\mathop{\longrightarrow}^{X\mapsto G,\,Y\mapsto H}
K[[T]]
\mathop{\longrightarrow}^{T\mapsto U(T)}
K[[T]],
$$

which has the particularly simple form

$$
X\longmapsto T,
\qquad
Y\longmapsto\widetilde H.
$$

That is, we seek to realise the curve as the graph of a formal function
in one variable.

> **Edition note - correction to the source's composition order.** The
> source writes $U(G(T))=T$ and $U(H(T))=\widetilde H(T)$. However, the
> displayed arrow substitutes $T\mapsto U(T)$ after the first map, so its
> resulting images are $G(U(T))$ and $H(U(T))$. The edition uses the
> composition order corresponding to that arrow.

<!-- upstream_entity: Ebene algebraische Kurven/Tangenten mit Kontaktordnung eins/Formal-analytische Realisierung als Graph/Fakt -->

### Theorem 25.2: a tangent of multiplicity one gives a graph solution {#br-ak-2012-l25-thm-01}

Let $K$ be a field and

$$
F\in K[X,Y]
$$

a nonzero polynomial with

$$
(0,0)\in C=V(F).
$$

Let

$$
F=F_d+\cdots+F_m,
\qquad d\geq m,
\qquad F_m\ne0,
$$

be the homogeneous decomposition of $F$, and let $uX+vY$ be a simple
linear factor of $F_m$, that is, a linear polynomial defining a tangent
line of multiplicity $1$. Then there are power series

$$
G=\sum_{n=0}^{\infty}a_nT^n,
\qquad
H=\sum_{\ell=0}^{\infty}b_\ell T^\ell
\in K[[T]]
$$

such that

$$
F(G,H)=0,
\qquad
a_0=b_0=0,
\qquad
a_1u+b_1v=0.
$$

Moreover, one of the two power series can be chosen to be a linear
polynomial.

> **Edition note - clarification of the initial condition.** The source
> writes “$a_0,b_0=0$”. The edition states the intended equality
> unambiguously as $a_0=b_0=0$.

<!-- upstream_entity: Ebene algebraische Kurven/Tangenten mit Kontaktordnung eins/Formal-analytische Realisierung als Graph/Fakt/Beweis -->

#### Proof {#br-ak-2012-l25-thm-01-proof}

By a linear change of variables, we may assume that

$$
uX+vY=Y.
$$

We shall construct a power series solution with

$$
G=T
$$

and

$$
H=b_2T^2+b_3T^3+\cdots.
$$

Since $a_1=1$ and $b_1=0$, this solution satisfies the linear condition
specified by the tangent line.

Write

$$
F=\sum_{i,j}c_{ij}X^iY^j.
$$

We have

$$
c_{m,0}=0,
$$

since otherwise $Y$ could not be a linear factor of $F_m$. Moreover,

$$
c_{m-1,1}\ne0,
$$

since if this coefficient were zero, $Y$ would be a linear factor with
multiplicity at least $2$.

We now show that these initial data determine a unique power series

$$
H=b_2T^2+b_3T^3+\cdots.
$$

Substituting $G$ and $H$ into $F$ gives one condition for each $k$, since
the resulting coefficient of $T^k$ must be zero. The $k$th coefficient is
a sum of expressions of the form

$$
c_{ij}b_{\ell_1}\cdots b_{\ell_j},
\qquad
i+\sum_{\rho=1}^{j}\ell_\rho=k.
$$

These expressions may occur repeatedly, with a multinomial coefficient.
Since $\ell_\rho\geq2$, the term $b_\ell$ does not yet occur when

$$
k<m+\ell-1.
$$

It first occurs in the coefficient with

$$
k=m+\ell-1,
$$

and its only occurrence there is

$$
c_{m-1,1}b_\ell.
$$

The other terms in that coefficient involve only the $c_{ij}$ and $b_r$
with $r<\ell$. Since $c_{m-1,1}\ne0$, this determines $b_\ell$ uniquely.
The coefficients $b_\ell$ can therefore be constructed inductively, each
value being uniquely determined by the corresponding coefficient equation.
$\square$

<!-- upstream_entity: Potenzreihe für ebene Kurven/Graph einer rationalen Funktion/X^3+XY+Y ist 0/Beispiel -->

### Example 25.3: the graph of a rational function {#br-ak-2012-l25-ex-01}

Consider the affine plane curve of degree three given by

$$
F=X^3+XY+Y=0.
$$

Its partial derivatives are

$$
\frac{\partial F}{\partial X}=3X^2+Y
\qquad\text{and}\qquad
\frac{\partial F}{\partial Y}=X+1.
$$

The second partial derivative vanishes only when $X=-1$, but on that line
$F$ has value $-1$. Thus the curve is smooth. At the origin the partial
derivatives have values $(0,1)$. The tangent line is therefore the
$X$-axis, in agreement with the fact that the linear term of the curve
equation is $Y$.

We compute the power series

$$
Y=H(T)=\sum_{\ell=0}^{\infty}b_\ell T^\ell
$$

that describes the curve as a graph at the origin, with $X=T$. The initial
conditions are

$$
b_0=b_1=0.
$$

The subsequent coefficients must satisfy

$$
F(T,H)=T^3+TH+H=0,
$$

or

$$
T^3+T(b_2T^2+b_3T^3+\cdots)
+(b_2T^2+b_3T^3+\cdots)=0.
$$

For $b_2$, the second coefficient of the equation immediately gives

$$
b_2=0.
$$

For $b_3$, the third coefficient gives

$$
1+b_3=0,
$$

hence $b_3=-1$. The subsequent coefficients give the relation

$$
b_{\ell-1}+b_\ell=0.
$$

Thus the later coefficients alternate between $1$ and $-1$, giving a
simple recurrence, and

$$
H=-T^3+T^4-T^5+T^6-T^7+\cdots.
$$

Rewriting the curve equation as

$$
Y=\frac{-X^3}{1+X}
$$

shows that this is the graph of a rational function with a pole at $X=-1$.
The power series above describes that rational function's graph as the
graph of a formal-analytic function.

<!-- upstream_entity: Potenzreihe für ebene Kurven/Kartesisches Blatt/Graph/Beispiel -->

### Example 25.4: the folium of Descartes as a formal graph {#br-ak-2012-l25-ex-02}

Consider the folium of Descartes

$$
X^3+Y^3-3XY=0
$$

at the origin, with tangent line $Y=0$. We seek the power series describing
as a graph the branch of the curve corresponding to this tangent line. Set

$$
X=T
$$

and

$$
H=b_2T^2+b_3T^3+b_4T^4+\cdots,
$$

assuming that the characteristic of $K$ is not $3$. The coefficients
$b_\ell$ are determined by

$$
\begin{aligned}
0
&=T^3+H^3-3TH\\
&=T^3+(b_2T^2+b_3T^3+\cdots)^3
-3T(b_2T^2+b_3T^3+\cdots).
\end{aligned}
$$

This substitution and expansion first gives a condition at $k=3$. The
term $X^3$, or $T^3$, needs to be considered only once, when $k=3$. The
term $Y^3$ contributes only from $k\geq6$ onwards, since $Y=H$ is a
multiple of $T^2$. The term $XY$ must be considered from $k=3$ onwards.

For $b_2$ we obtain

$$
1-3b_2=0,
$$

hence

$$
b_2=\frac13.
$$

The coefficient $b_3$ first occurs in the condition for the fourth
coefficient, where it stands alone, so

$$
b_3=0.
$$

For the same reason,

$$
b_4=0.
$$

For $b_5$, the sixth coefficient is decisive, and now the term $Y^3$ must
also be included. The condition is

$$
b_2^3-3b_5=0,
$$

so

$$
b_5=\frac1{81}.
$$

For $b_6,b_7,b_8$, note that the term

$$
Y^3=(b_2T^2+b_5T^5+\cdots)
(b_2T^2+b_5T^5+\cdots)
(b_2T^2+b_5T^5+\cdots)
$$

next contributes at the ninth coefficient, with contribution $3b_2^2b_5$.
Thus $b_6$ and $b_7$ stand alone and must be zero. For $b_8$ we obtain

$$
3b_2^2b_5-3b_8=0,
$$

hence

$$
b_8=\frac1{729}.
$$

The beginning of the power series describing this branch of the curve as
a graph is therefore

$$
H=\frac13T^2+\frac1{81}T^5+\frac1{729}T^8+\cdots.
$$

<!-- upstream_entity: Potenzreihe für ebene Kurven/Neilsche Parabel/Keine tangentiale Potenzreihe/Beispiel -->

### Example 25.5: Neil's parabola without a nonzero linear term {#br-ak-2012-l25-ex-03}

Consider Neil's parabola given by

$$
X^3-Y^2=0.
$$

The origin is singular and has only one tangent line, namely

$$
Y=0.
$$

However, this tangent has multiplicity two, so
[Theorem 25.2](#br-ak-2012-l25-thm-01) does not apply. In fact, there is no
power series solution at the origin with a nonzero linear term.

To see this, suppose that

$$
X=G=a_1T+a_2T^2+\cdots
$$

and

$$
Y=H=b_1T+b_2T^2+\cdots
$$

satisfy the curve equation. After substitution, the second coefficient gives

$$
-b_1^2=0,
$$

so $b_1=0$. The third coefficient then gives

$$
a_1^3=0,
$$

so $a_1=0$ as well.

Nevertheless, there are power series solutions for Neil's parabola through
the origin. We may take the monomial solution

$$
G=T^2
\qquad\text{and}\qquad
H=T^3.
$$

This even gives a bijection between the affine line and Neil's parabola,
but its linear term is indeed zero.

<!-- upstream_entity: Satz über implizite Funktionen/Ebene Kurven/Bemerkung -->

### Remark 25.6: comparison with the implicit function theorem {#br-ak-2012-l25-rem-01}

Let

$$
K=\mathbb R
\qquad\text{or}\qquad
K=\mathbb C,
$$

and $F\in K[X,Y]$. If

$$
\left(
\frac{\partial F}{\partial x}(P),
\frac{\partial F}{\partial y}(P)
\right)\ne(0,0),
$$

that is, if $P$ is a regular point of the function $F$, or equivalently a
smooth point of

$$
C=V(F-F(P)),
$$

then the implicit function theorem guarantees that, in a metric
neighbourhood of $P$, the curve can be expressed as the graph of a
differentiable function.

> **Edition note - correction to the source wording.** The source writes
> “$K=\mathbb R$ or $=\mathbb C$”. The edition supplies the subject in the
> second alternative, writing $K=\mathbb R$ or $K=\mathbb C$.
