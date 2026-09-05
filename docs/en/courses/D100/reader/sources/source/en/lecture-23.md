---
title: "Lecture 23 - Cotangent Spaces and Hilbert–Samuel Multiplicity"
stable_id: br-ak-2025-2026-l23
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 23"
upstream_pageid: 165912
upstream_revid: 1112318
upstream_timestamp: "2026-08-21T09:42:07Z"
upstream_mediawiki_sha1: a38160a106cf39298b3f2cb23f7880e05a5a86f7
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112318"
authority_manifest: authority/wikiversity/unit-23/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f7ee49a4bfa589b831c1fdb69e6f091ac1762d9da019a133670e4e0d723d34ae
lecture_xml_sha256: e03f37dab14063c982dec993e0da4dd94e9e4cbdf9b73b38ad4c77a63dd83116
lecture_expanded_tex_sha256: 17aa88b5aa9a8d130f0995c036cb9ca332ef1b0feaef3b2d5ac5396e47b343a0
license: "CC BY-SA 4.0"
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 17
source_corrections: 4
reader_media_positions: 0
---

# Lecture 23: Cotangent Spaces and Hilbert–Samuel Multiplicity {#br-ak-2025-2026-l23}

## Interpretation as a cotangent space {#br-ak-2025-2026-l23-s01}

We give another indication that calling $\mathfrak m/\mathfrak m^2$ the
*cotangent space* is well justified. From analysis, we know that for a point
$P\in M$ on a manifold $M$ and a differentiable function
$f:M\longrightarrow\mathbb R$, the differential

$$
df:T_PM\longrightarrow\mathbb R
$$

is linear (see Lemma 9.10 (Differential Geometry (Osnabrück 2023)), part
(3)). Thus $df$ is an element of the cotangent space $T_P^*M$. The overall
assignment

$$
C^1(M,\mathbb R)\longrightarrow T_P^*M,
\qquad f\longmapsto df,
$$

is a derivation: it satisfies the Leibniz rule

$$
d(fg)=f\,dg+g\,df.
$$

We now introduce the general algebraic concept.

<!-- upstream_entity: Algebraische Derivation/Definition -->

### Definition: algebraic derivation {#br-ak-2025-2026-l23-def-01}

Let $R$ be a commutative ring, $A$ a commutative $R$-algebra, and $M$ an
$A$-module. An $R$-linear map

$$
\delta:A\longrightarrow M
$$

is called an *$R$-derivation* with values in $M$ if

$$
\delta(ab)=a\delta(b)+b\delta(a)
$$

for all $a,b\in A$.

<!-- upstream_entity: K-Algebra/Algebraischer Kotangentialraum an K-Punkt/Direkte Derivation/Fakt -->

### Theorem: the canonical derivation into the cotangent space {#br-ak-2025-2026-l23-thm-01}

Let $K$ be a field, $R$ a $K$-algebra of finite type, and

$$
P\in K\!-\!\operatorname{Spek}(R)
$$

a point with corresponding maximal ideal $\mathfrak m$. Then the map

$$
\begin{aligned}
d:R&\longrightarrow\mathfrak m/\mathfrak m^2,\\
f&\longmapsto d f:=\overline{f-f(P)}
\end{aligned}
$$

is a $K$-derivation.

<!-- upstream_entity: K-Algebra/Algebraischer Kotangentialraum an K-Punkt/Direkte Derivation/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-01}

There is a canonical isomorphism $K\longrightarrow R/\mathfrak m$ between
the base field and the residue field. The map $d$ is well defined because

$$
(f-f(P))(P)=0,
$$

so $f-f(P)\in\mathfrak m$. Its $K$-linearity is immediate. For the product
rule, all the following equalities are understood in
$\mathfrak m/\mathfrak m^2$:

$$
\begin{aligned}
d(fg)
&=\overline{fg-(fg)(P)}\\
&=\overline{fg-f(P)g(P)}\\
&=\overline{fg-f(P)g(P)+(f-f(P))(g-g(P))}\\
&=\overline{2fg-f\cdot g(P)-g\cdot f(P)}\\
&=\overline{f(g-g(P))+g(f-f(P))}\\
&=f\,dg+g\,df.
\end{aligned}
$$

In the third step we add an element of $\mathfrak m^2$, whose class in the
quotient is zero. This proves the Leibniz rule. $\square$

*Edition note -- clarification of the source notation:* The source writes
the chain above without a residue-class bar on each term. These are
equalities modulo $\mathfrak m^2$, not polynomial equalities in $R$.

## Smooth points and normal points {#br-ak-2025-2026-l23-s02}

We shall show that a point on a plane algebraic curve is smooth precisely
when the corresponding local ring is a discrete valuation ring. Smoothness
at a point was initially defined extrinsically, with reference to the
ambient plane, whereas being a discrete valuation ring depends only on the
curve's coordinate ring. The following lemma handles one direction. For
the other, we must first develop an intrinsic multiplicity for a local ring.

<!-- upstream_entity: Ebene algebraische Kurve/Glatter Punkt/Lokaler Ring ist diskreter Bewertungsring/Fakt -->

### Lemma: smooth points give discrete valuation rings {#br-ak-2025-2026-l23-lem-01}

Let $K$ be a field, $F\in K[X,Y]$ a nonzero polynomial without repeated
factors, and

$$
P\in C=V(F)
$$

a smooth point of the curve. If $R$ is the local ring of the curve at $P$,
then $R$ is a discrete valuation ring.

<!-- upstream_entity: Ebene algebraische Kurve/Glatter Punkt/Lokaler Ring ist diskreter Bewertungsring/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-02}

First, $R$ is a Noetherian local ring and, by Lemma 22.12, an integral
domain. Its only prime ideals are therefore the zero ideal and the maximal
ideal $\mathfrak m_P$. We shall show that this maximal ideal is principal.

We may assume that $P$ is the origin and write

$$
F=F_d+\cdots+F_1,
\qquad F_1\ne0,
$$

where each $F_i$ is homogeneous of degree $i$. Since $P$ is smooth, this
form has a nonzero linear term. A linear change of variables allows us to
arrange that $F_1=Y$. Collect all the pure powers of $X$, that is, the
monomials not involving $Y$, and factor $Y$ out of the remaining terms.
The equation $F=0$ can then be written as

$$
Y(1+G)=XH(X),
\qquad G\in(X,Y).
$$

The element $1+G$ is a unit in $K[X,Y]_{(X,Y)}$, and hence also in the local
ring of the curve at the origin,

$$
R=K[X,Y]_{(X,Y)}/(F).
$$

In $R$ we have

$$
Y=\frac{H}{1+G}X.
$$

Thus the maximal ideal of $R$ is generated by $X$ alone. By Theorem 21.8,
$R$ is a discrete valuation ring. $\square$

## Hilbert–Samuel multiplicity {#br-ak-2025-2026-l23-s03}

<!-- upstream_entity: Noetherscher lokaler Ring/Potenzen vom maximalen Ideal/Restklassenring und Jets sind endlich-dimensional/Fakt -->

### Lemma: quotients by powers of the maximal ideal are finite-dimensional {#br-ak-2025-2026-l23-lem-02}

Let $R$ be a Noetherian local ring with maximal ideal $\mathfrak m$ and
residue field

$$
K=R/\mathfrak m.
$$

Then the quotient modules $\mathfrak m^n/\mathfrak m^{n+1}$ are
finite-dimensional over $K$. If $R$ contains a field $K$ mapping
isomorphically onto the residue field, the quotient rings $R/\mathfrak m^n$
are also finite-dimensional over $K$.

<!-- upstream_entity: Noetherscher lokaler Ring/Potenzen vom maximalen Ideal/Restklassenring und Jets sind endlich-dimensional/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-03}

We write

$$
\mathfrak m^n/\mathfrak m^{n+1}
\cong
\mathfrak m^n/(\mathfrak m^n)\mathfrak m.
$$

This is the situation of Lemma 22.2. Since $\mathfrak m^n$ is a finitely
generated ideal, the quotient module is finite-dimensional over the residue
field.

For the quotient rings, consider the short exact sequence of $R$-modules

$$
0\longrightarrow
\mathfrak m^n/\mathfrak m^{n+1}
\longrightarrow R/\mathfrak m^{n+1}
\longrightarrow R/\mathfrak m^n
\longrightarrow0.
$$

Under the additional hypothesis, this is also a short exact sequence of
$K$-vector spaces, so their dimensions add. The space on the left is
finite-dimensional by the part just proved. Induction on $n$ now gives the
desired result, with initial case $R/\mathfrak m=K$. $\square$

For a plane algebraic curve

$$
V=V(F)\subseteq\mathbb A_K^2
$$

and a point $P=(a,b)\in V$, the local ring is

$$
K[X,Y]_{(X-a,Y-b)}/(F).
$$

Its residue field is $K$ itself. Thus all the hypotheses of Lemma 23.4 hold,
and all the following dimensions are over the base field.

<!-- upstream_entity: Ebene algebraische Kurve/Multiplizität über Hilbert-Samuel Polynom/Fakt -->

### Theorem: multiplicity via the Hilbert–Samuel function {#br-ak-2025-2026-l23-thm-02}

Let

$$
P\in V=V(F)\subseteq\mathbb A_K^2
$$

be a point on an affine plane curve. Let

$$
R=\mathcal O_{V,P}
$$

be its local ring, with maximal ideal $\mathfrak m$. Then the multiplicity
$m_P$ of $P$ satisfies

$$
m_P=\dim_K\left(\mathfrak m^n/\mathfrak m^{n+1}\right)
$$

for all sufficiently large $n$.

<!-- upstream_entity: Ebene algebraische Kurve/Multiplizität über Hilbert-Samuel Polynom/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-04}

Consider the short exact sequence of $K$-vector spaces

$$
0\longrightarrow
\mathfrak m^n/\mathfrak m^{n+1}
\longrightarrow R/\mathfrak m^{n+1}
\longrightarrow R/\mathfrak m^n
\longrightarrow0.
$$

By Lemma 23.4, all dimensions are finite. The assertion that the dimension
of $\mathfrak m^n/\mathfrak m^{n+1}$ is eventually constant and equal to the
multiplicity is equivalent to the assertion that the difference

$$
\dim_K(R/\mathfrak m^{n+1})-\dim_K(R/\mathfrak m^n)
$$

is eventually constant and equal to the multiplicity. By induction, this
is equivalent to the existence of a constant $c$ such that

$$
\dim_K(R/\mathfrak m^n)=m_Pn+c
$$

for sufficiently large $n$.

After a translation, we may assume that $P$ is the origin. Set

$$
\mathfrak a=(X,Y)\subseteq S=K[X,Y].
$$

Then

$$
K[X,Y]/(\mathfrak a^n+(F))=R/\mathfrak m^n,
$$

so it suffices to prove the statement for the quotient on the left. By
hypothesis, $F$ has the form

$$
F=F_m+F_{m+1}+\cdots,
\qquad m=m_P,
$$

and in particular $F\in\mathfrak a^m$. If $G\in\mathfrak a^{n-m}$ with
$n\ge m$, then $GF\in\mathfrak a^n$. There is therefore a short exact
sequence

$$
0\longrightarrow
S/\mathfrak a^{n-m}
\xrightarrow{\,\cdot F\,}
S/\mathfrak a^n
\longrightarrow
S/(\mathfrak a^n,F)=R/\mathfrak m^n
\longrightarrow0.
$$

Injectivity on the left follows from a direct degree argument; see Exercise
23.4. We know that

$$
\dim_K(S/\mathfrak a^n)=\frac{n(n+1)}2.
$$

Hence, for $n\ge m$,

$$
\begin{aligned}
\dim_K(R/\mathfrak m^n)
&=\frac{n(n+1)}2-\frac{(n-m)(n-m+1)}2\\
&=\frac{n^2+n-(n-m)^2-n+m}{2}\\
&=\frac{2nm-m^2+m}{2}\\
&=mn-\frac{m(m-1)}2.
\end{aligned}
$$

This is the required linear form. $\square$

<!-- upstream_entity: Ebene algebraische Kurve/Multiplizität über Hilbert-Samuel Polynom/Bemerkung -->

### Remark: multiplicity as an intrinsic invariant {#br-ak-2025-2026-l23-rem-01}

Theorem 23.5 says in particular that the multiplicity of a point on a plane
curve is an invariant of the local ring of the curve at that point. It
therefore depends only on intrinsic properties of the curve, not on its
realisation in an ambient plane.

Every Noetherian local ring has a *Hilbert–Samuel multiplicity*, defined in
terms of the dimensions over $R/\mathfrak m$ of the quotient modules
$\mathfrak m^n/\mathfrak m^{n+1}$. In the one-dimensional case it is

$$
\lim_{n\to\infty}
\dim_{R/\mathfrak m}
\left(\mathfrak m^n/\mathfrak m^{n+1}\right),
$$

since this function eventually becomes constant—a nontrivial fact. If $R$
contains a field $K$ isomorphic to its residue field, as is the case for
the local rings of curves considered here, the same number is also given by

$$
\lim_{n\to\infty}
\frac{\dim_K(R/\mathfrak m^n)}{n}.
$$

<!-- upstream_entity: Ebene algebraische Kurve/Punkt/Glatt,diskreter Bewertungsring, Multiplizität/Fakt -->

### Theorem: smoothness, multiplicity, discrete valuation, and normality {#br-ak-2025-2026-l23-thm-03}

Let $K$ be a field and $F\in K[X,Y]$ a nonconstant polynomial without
repeated factors, with corresponding algebraic curve

$$
C=V(F).
$$

Let $P=(a,b)\in C$, with maximal ideal

$$
\mathfrak m=(X-a,Y-b)
$$

and local ring

$$
R=K[X,Y]_{\mathfrak m}/(F).
$$

The following statements are equivalent.

1. $P$ is a smooth point of the curve.
2. The multiplicity of $P$ is one.
3. $R$ is a discrete valuation ring.
4. $R$ is a normal integral domain.

<!-- upstream_entity: Ebene algebraische Kurve/Punkt/Glatt,diskreter Bewertungsring, Multiplizität/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-05}

The equivalence (1) $\Leftrightarrow$ (2) follows from Definition 22.7 of
multiplicity. The equivalence (3) $\Leftrightarrow$ (4) was proved in
Theorem 21.8, and the implication (1) $\Rightarrow$ (3) in Lemma 23.3. It
remains to prove (3) $\Rightarrow$ (2); by Theorem 23.5 we may work with
Hilbert–Samuel multiplicity.

It suffices to show that, for the local ring of a plane curve that is a
discrete valuation ring, all the quotient modules

$$
\mathfrak m^n/\mathfrak m^{n+1}
\cong
\mathfrak m^n/\mathfrak m^n\mathfrak m
$$

are one-dimensional over the residue field $R/\mathfrak m\cong K$. Since
$\mathfrak m^n=(\pi^n)$, this follows immediately from Nakayama's lemma.
$\square$

## Monomial curves and multiplicity {#br-ak-2025-2026-l23-s04}

<!-- upstream_entity: Monomiale Kurve/Multiplizität/Numerisch und Hilbert-Samuel/Textabschnitt -->

Let $M\subseteq\mathbb N$ be a numerical monoid generated by coprime
natural numbers

$$
e_1<e_2<\cdots<e_r.
$$

The least generator $e_1$ is also called the *numerical multiplicity* of
$M$. We shall show that this does indeed give the correct ring-theoretic
multiplicity. Set

$$
M_+=\{m\in M\mid m\ge1\}
$$

and, for $n\ge1$,

$$
nM_+=
\left\{
m\in M\ \middle|\
m=m_1+\cdots+m_n\text{ for some }m_i\in M_+
\right\}.
$$

Both are monoid ideals of $M$. Thus the monomial spaces

$$
K[nM_+]=\bigoplus_{m\in nM_+}KT^m
$$

are ideals in the monoid ring. In particular,

$$
\mathfrak m=K[M_+]
$$

is a maximal ideal, and its powers are

$$
\mathfrak m^n=K[nM_+].
$$

<!-- upstream_entity: Monomiale Kurven/Multiplizität/Abschätzungen für Anzahl in Differenzmengen/Fakt -->

### Lemma: bounds for monoid difference sets {#br-ak-2025-2026-l23-lem-03}

Let $M\subseteq\mathbb N$ be a numerical monoid of numerical multiplicity
$e_1$. Choose $\ell\ge1$ such that $\mathbb N_{\ge\ell}\subseteq M$. Then,
for each $n\ge1$,

$$
ne_1-\ell
\le
\#(M\setminus nM_+)
\le
(n-1)e_1+\ell.
$$

<!-- upstream_entity: Monomiale Kurven/Multiplizität/Abschätzungen für Anzahl in Differenzmengen/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-06}

The lower bound follows from the fact that the smallest number in $nM_+$
is $ne_1$. Thus $0,1,\ldots,ne_1-1$ lie outside it. All numbers at least
$\ell$ belong to $M$, so at least $ne_1-\ell$ of these $ne_1$ numbers belong
to $M$ but not to $nM_+$.

For the upper bound, we claim that every number at least $(n-1)e_1+\ell$
belongs to $nM_+$. Let

$$
x\ge(n-1)e_1+\ell.
$$

Write

$$
x=(n-1)e_1+\ell',
\qquad \ell'\ge\ell.
$$

Since $\ell'\in M_+$, the right-hand side is a sum of $n$ elements of
$M_+$: $n-1$ summands equal to $e_1$ and one equal to $\ell'$. Thus
$x\in nM_+$, proving the upper bound. $\square$

*Edition note -- correction to the source's bound:* The source describes
$\ell$ only as “a number” and says in the final step that the summands
belong to $M$. The hypothesis $\ell\ge1$, which can always be achieved by
increasing the threshold, ensures that all $n$ summands really lie in
$M_+$, as required by the definition of $nM_+$. The source also leaves the
range of $n$ implicit. Here $n\ge1$: the displayed definition by sums of
positive elements does not give the zeroth ideal power when $n=0$.

<!-- upstream_entity: Monomiale Kurve/Hilbert-Samuel Multiplizität ist numerische Multiplizität/Fakt -->

### Corollary: numerical multiplicity equals Hilbert–Samuel multiplicity {#br-ak-2025-2026-l23-cor-01}

Let $M\subseteq\mathbb N$ be a numerical monoid generated by coprime
numbers, with numerical multiplicity $e_1$. Let

$$
\mathfrak m=K[M_+]
$$

be the maximal ideal of the monoid ring $K[M]$ corresponding to the origin.
Then

$$
\lim_{n\to\infty}
\frac{\dim_K\left(K[M]/\mathfrak m^n\right)}{n}
=e_1.
$$

In other words, numerical multiplicity equals Hilbert–Samuel multiplicity.

<!-- upstream_entity: Monomiale Kurve/Hilbert-Samuel Multiplizität ist numerische Multiplizität/Fakt/Beweis -->

### Proof {#br-ak-2025-2026-l23-prf-07}

Since $\mathfrak m^n=K[nM_+]$, the quotient ring

$$
K[M]/\mathfrak m^n
=K[M]/K[nM_+]
$$

has the monomials $T^m$ with $m\in M\setminus nM_+$ as a basis over $K$.
Its dimension therefore equals $\#(M\setminus nM_+)$. By the bounds in
Lemma 23.8,

$$
\frac{\#(M\setminus nM_+)}{n}\longrightarrow e_1.
$$

The same convergence holds for these dimensions. $\square$

*Edition note -- clarification of the source notation:* The source notation
$K[M]/(nM_+)$ means the quotient by the monomial ideal $K[nM_+]$; the
parentheses do not denote scalar multiplication of a set by $n$.
