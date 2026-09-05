---
title: "Lecture 14 - Algebraic Functions on Varieties"
stable_id: br-ak-2025-2026-l14
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 14"
upstream_pageid: 165903
upstream_revid: 1051343
upstream_timestamp: "2025-08-18T08:06:49Z"
upstream_mediawiki_sha1: 5bc2e2c3db815edeb4f10640564c8cd793de74a8
source_url: "https://de.wikiversity.org/w/index.php?oldid=1051343"
authority_manifest: authority/wikiversity/unit-14/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a63c3481d0a9cfa9b960f12c9bf0eec9a5d39cecfb61eddb8f9d96190e52e83e
lecture_xml_sha256: 779422f6a20c9462db83e79f38450073da2b0653a239b1028795cc6b49cf7a32
lecture_expanded_tex_sha256: 26347a8614ea18ca719d548ea3d58d9e8d419bf5adc469c19e757d48e53c3f55
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-14.csv"
translation_status: complete
---

# Lecture 14: Algebraic Functions on Varieties {#br-ak-2025-2026-l14}

## Algebraic functions {#br-ak-2025-2026-l14-s01}

What is a morphism between two affine algebraic sets $V$ and $W$? We first
consider the case in which

$$
W=\mathbb A_K^1
$$

is the affine line. Suppose that

$$
V=V(\mathfrak a)\subseteq\mathbb A_K^n
$$

is given as a closed subset of an affine space. Every polynomial

$$
F\in K[X_1,\ldots,X_n]
$$

then gives a map

$$
F:\mathbb A_K^n\longrightarrow\mathbb A_K^1=K
$$

and hence, by restriction, a map on $V$. We already considered this when
defining the coordinate ring. Likewise, an element $F$ of a finitely
generated $K$-algebra $R$ gives a function

$$
\begin{aligned}
K\!-\!\operatorname{Spek}(R)&\longrightarrow\mathbb A_K^1,\\
P&\longmapsto F(P).
\end{aligned}
$$

This is also the map of spectra that, by Proposition 12.8(2), corresponds
to the substitution homomorphism

$$
K[T]\longrightarrow R,
\qquad T\longmapsto F.
$$

On the open set

$$
D(F)\cong K\!-\!\operatorname{Spek}(R_F),
$$

the function $1/F$ is well defined by Theorem 13.4. We shall now explain
what an algebraic function on an arbitrary Zariski-open set $U\subseteq V$
is. The following definition is arranged so that being “algebraic” is a
local property.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische (reguläre) Funktion auf offener Menge/Punktweise und global/Definition -->

### Definition: algebraic functions on an open set {#br-ak-2025-2026-l14-def-01}

Let $K$ be an algebraically closed field, let $R$ be a $K$-algebra of finite
type, and let

$$
V=K\!-\!\operatorname{Spek}(R).
$$

Let $P\in V$, let $U\subseteq V$ be a Zariski-open set with $P\in U$, and
let

$$
f:U\longrightarrow\mathbb A_K^1=K
$$

be a function. We call $f$ *algebraic* (also *regular* or *polynomial*) at
$P$ if there are elements $G,H\in R$ such that

$$
P\in D(H)\subseteq U
$$

and

$$
f(Q)=\frac{G(Q)}{H(Q)}
\qquad\text{for every }Q\in D(H).
$$

We call $f$ *algebraic on $U$* if it is algebraic at every point of $U$.

Of course, every element $f\in R$ defines an algebraic function on every
open subset of the $K$-spectrum. In general, however, it is rather difficult
to give a concise description of all algebraic functions.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische Funktion auf offener Menge/Bemerkung -->

### Remark: locality and fractional representations {#br-ak-2025-2026-l14-rem-01}

In Definition 14.1, the condition $D(H)\subseteq U$ is not essential. If
there is a representation $f=G/H$ on $D(H)$ with $P\in D(H)$, choose $H'$
such that

$$
P\in D(H')\subseteq U.
$$

On

$$
D(H)\cap D(H')=D(HH')
$$

we may use the representation

$$
f=\frac{GH'}{HH'}.
$$

If $f=G/H$ is a fractional representation at $P$, the same representation
works for every point of $D(H)$. Thus $f$ is algebraic on the whole open
set $D(H)$. In particular, we need not work with infinitely many different
representations: finitely many fractions $G_i/H_i$ for a cover

$$
U=\bigcup_{i\in I}D(H_i)
$$

suffice.

For $K=\mathbb C$, an algebraic function is also continuous in the metric
topology; when $R=\mathbb C[X_1,\ldots,X_n]$, it is holomorphic.

<!-- upstream_entity: Affine Varietäten/Algebraische Funktionen/ux-vy/Funktion auf D(x,y)/Beispiel -->

### Example: a function glued from two fractions {#br-ak-2025-2026-l14-exm-01}

Let

$$
V=V(WX-ZY)\subseteq\mathbb A_K^4
$$

and let

$$
U=D(X,Y)=D(X)\cup D(Y)\subset V
$$

be the Zariski-open set defined by $X$ and $Y$. The function on $U$ defined
by

$$
f=\frac ZX=\frac WY
$$

is algebraic. The two fractions clearly give algebraic functions on $D(X)$
and $D(Y)$ respectively. To define a single function on $U$, their values
must agree on the intersection $D(X)\cap D(Y)=D(XY)$. Take

$$
Q=(w,x,y,z)\in D(XY)\cap V.
$$

We have $x,y\ne0$ and $wx=zy$, so

$$
\frac ZX(Q)=\frac zx=\frac wy=\frac WY(Q).
$$

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische Funktion auf offener Menge/Ring/Fakt -->

### Lemma: algebraic functions form an algebra {#br-ak-2025-2026-l14-lem-01}

Let $K$ be an algebraically closed field, let $R$ be a $K$-algebra of finite
type, let $V=K\!-\!\operatorname{Spek}(R)$, and let $U\subseteq V$ be
Zariski-open. The algebraic functions on $U$ form a subring—in fact, a
$K$-subalgebra—of the ring of all functions $U\to K$, with operations
performed in $K$.

#### Proof {#br-ak-2025-2026-l14-lem-01-proof}

We must check that the constant zero and one functions, the negative of an
algebraic function, and the sum and product of two algebraic functions are
again algebraic. We restrict ourselves to the sum. Let $f_1,f_2$ be
algebraic and let $P\in U$. There are $G_1,H_1,G_2,H_2\in R$ such that

$$
f_1(Q)=\frac{G_1(Q)}{H_1(Q)}
\quad(Q\in D(H_1)\subseteq U),
\qquad P\in D(H_1),
$$

and

$$
f_2(Q)=\frac{G_2(Q)}{H_2(Q)}
\quad(Q\in D(H_2)\subseteq U),
\qquad P\in D(H_2).
$$

Set $H=H_1H_2$. Then

$$
P\in D(H)=D(H_1)\cap D(H_2)\subseteq U.
$$

For $Q\in D(H)$ we have

$$
\begin{aligned}
(f_1+f_2)(Q)
&=f_1(Q)+f_2(Q)\\
&=\frac{G_1(Q)}{H_1(Q)}+\frac{G_2(Q)}{H_2(Q)}\\
&=\frac{G_1(Q)H_2(Q)+G_2(Q)H_1(Q)}{H_1(Q)H_2(Q)}\\
&=\frac{(G_1H_2+G_2H_1)(Q)}{(H_1H_2)(Q)}.
\end{aligned}
$$

Thus the sum has a fractional representation on the Zariski-open
neighbourhood $D(H)$ of $P$. The other cases are similar.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische (reguläre) Funktion auf offener Menge/Schnittring/Definition -->

### Definition: the ring of algebraic sections {#br-ak-2025-2026-l14-def-02}

In the situation above, the ring

$$
\Gamma(U,\mathcal O)
=\{f:U\longrightarrow K\mid f\text{ is algebraic}\}
$$

is called the *ring of algebraic functions* on $U$. It is also called the
*structure ring* or *ring of sections* on $U$. By Lemma 14.4 this set is
indeed a ring. The symbol $\mathcal O$ (pronounced “O”) denotes the
so-called *structure sheaf*.

<!-- upstream_entity: K-Spektrum/Ring der algebraischen Funktionen/Restriktion/Fakt -->

### Lemma: restriction maps {#br-ak-2025-2026-l14-lem-02}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type. Let $U_1\subseteq U_2$ be open subsets of
$V=K\!-\!\operatorname{Spek}(R)$. There is a natural $K$-algebra
homomorphism

$$
\Gamma(U_2,\mathcal O)\longrightarrow\Gamma(U_1,\mathcal O).
$$

#### Proof {#br-ak-2025-2026-l14-lem-02-proof}

A function $f:U_2\to K$ immediately gives a function on $U_1$ by
restriction. The local algebraic description of $f$ at each point
$P\in U_2$ also applies on the smaller subset $U_1$.

The map in this lemma is called the *restriction map*.

<!-- upstream_entity: K-Spektrum/Ring der algebraischen Funktionen/U subseteq D(f)/Unabhängigkeit/Fakt -->

### Lemma: independence of a principal open ambient space {#br-ak-2025-2026-l14-lem-03}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type. Let $F\in R$ and let

$$
U\subseteq D(F)\subseteq V=K\!-\!\operatorname{Spek}(R)
$$

be open. The definition of $\Gamma(U,\mathcal O)$ gives the same ring
whether we take the ambient space to be $V$ or

$$
D(F)=K\!-\!\operatorname{Spek}(R_F).
$$

#### Proof {#br-ak-2025-2026-l14-lem-03-proof}

Functions on $U$ clearly depend only on $U$, not on an ambient space. It
remains to show that the local algebraic condition also depends only on $U$.

Take $P\in U$. A representation

$$
\varphi=\frac GH\text{ on }D(H),
\qquad P\in D(H),\quad G,H\in R,
$$

immediately gives a fractional representation on $D(HF)$ by regarding
$G,H$ as elements of $R_F$.

Conversely, suppose that there is a representation over $R_F$

$$
\varphi=\frac{\widetilde G}{\widetilde H}
\text{ on }D(\widetilde H),
\qquad P\in D(\widetilde H),
$$

where

$$
\widetilde G=\frac G{F^r},
\qquad
\widetilde H=\frac H{F^s}.
$$

For $Q\in D(HF)$ we have

$$
\varphi(Q)
=\frac{\widetilde G(Q)}{\widetilde H(Q)}
=\frac{G(Q)/F^r(Q)}{H(Q)/F^s(Q)}
=\frac{G(Q)F^s(Q)}{H(Q)F^r(Q)}.
$$

In the last step we multiplied numerator and denominator by $F^{r+s}$.
The final numerator and denominator lie in $R$, and $HF^r(P)\ne0$.
Thus $D(HF^r)$ is an open neighbourhood of $P$ giving a representation
relative to $V$.

> **Edition note:** In the source's last neighbourhood argument, take
> $r\ge1$, which is always possible by multiplying the numerator and
> denominator of $\widetilde G=G/F^r$ by $F$. Then
> $D(HF^r)=D(HF)\subseteq U$. If $r=0$ were retained, $D(HF^r)=D(H)$
> could extend outside the original domain.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Verschiedene rationale Darstellungen einer aIgebraischen Funktion/Beziehung im Koordinatenring/Fakt -->

### Lemma: the relation between two rational representations {#br-ak-2025-2026-l14-lem-04}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type. Let $f:U\to K$ be an algebraic function on a Zariski-open set
$U\subseteq V=K\!-\!\operatorname{Spek}(R)$. Suppose that near $P\in U$
it has two representations

$$
\frac{G_1}{H_1}
\qquad\text{and}\qquad
\frac{G_2}{H_2},
$$

with $G_1,H_1,G_2,H_2\in R$ and
$P\in D(H_1),D(H_2)\subseteq U$. Then there is an $r\in\mathbb N$ such
that

$$
H_1^rH_2^r(G_1H_2-G_2H_1)^r=0
\quad\text{in }R.
$$

If $R$ is reduced, we even have

$$
H_1H_2(G_1H_2-G_2H_1)=0.
$$

#### Proof {#br-ak-2025-2026-l14-lem-04-proof}

Consider the element

$$
F=H_1H_2(G_1H_2-G_2H_1)
$$

on $V$. We show that it induces the zero function. Take $Q\in V$. If
$H_1(Q)=0$ or $H_2(Q)=0$, then $F(Q)=0$ immediately. If neither is zero,
then $Q\in D(H_1)\cap D(H_2)$ and

$$
\frac{G_1(Q)}{H_1(Q)}=f(Q)=\frac{G_2(Q)}{H_2(Q)}.
$$

Hence $G_1(Q)H_2(Q)=G_2(Q)H_1(Q)$ and again $F(Q)=0$. By Hilbert's
Nullstellensatz there is an $r$ such that $F^r=0$ in $R$. If $R$ is
reduced, $F=0$.

![Copper-coloured monkey saddle surface with three valleys and three ridges](authority/assets/Monkey_Saddle_Surface_Shaded-500.png)

*The graph of a global function on two-dimensional affine space;
Inductiveload, public domain. Source details are given in the Unit 14 media
credits.*

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische (reguläre) Funktion auf offener Menge/Globaler Schnittring ist Koordinatenring/Fakt -->

### Theorem: global sections on an affine spectrum {#br-ak-2025-2026-l14-thm-01}

Let $K$ be an algebraically closed field, let $R$ be a reduced $K$-algebra
of finite type, and let $V=K\!-\!\operatorname{Spek}(R)$. Then

$$
\Gamma(V,\mathcal O)=R.
$$

#### Proof {#br-ak-2025-2026-l14-thm-01-proof}

Every $F\in R$ directly gives an algebraic function on all of $V$, so
there is a $K$-algebra homomorphism

$$
R\longrightarrow\Gamma(V,\mathcal O).
$$

If $F$ induces the zero function at every point, Theorem 11.1 and the
reducedness of $R$ imply $F=0$. Thus the map is injective.

Now let $f:V\to K$ be an algebraic function. For every $P\in V$ there are
$G_P,H_P\in R$ with $P\in D(H_P)$ and

$$
f=\frac{G_P}{H_P}\quad\text{on }D(H_P).
$$

The sets $D(H_P)$ cover $V$. By Corollary 11.12, the elements $H_P$
generate the unit ideal, so finitely many of them already generate the unit
ideal. Denote them by

$$
H_i=H_{P_i},\qquad i=1,\ldots,m.
$$

Then the $D(H_i)$ cover all of $V$. On each intersection
$D(H_iH_j)=D(H_i)\cap D(H_j)$ we have

$$
f(Q)=\frac{G_i(Q)}{H_i(Q)}=\frac{G_j(Q)}{H_j(Q)}.
$$

By Lemma 14.8 and reducedness,

$$
H_iH_jG_iH_j=H_iH_jG_jH_i
$$

in $R$. Replace $H_i$ by $H_i^2$ and $G_i$ by $G_iH_i$. The
representation $G_i/H_i$ remains unchanged, while the last relation
simplifies to

$$
H_iG_j=H_jG_i.
$$

Since the $H_i$ generate the unit ideal, there are $A_i\in R$ with

$$
\sum_{i=1}^m A_iH_i=1.
$$

Set

$$
F=\sum_{i=1}^m A_iG_i.
$$

We claim that $F$ induces $f$ on all of $V$. Take $Q\in V$; without loss
of generality, suppose $Q\in D(H_1)$. Then

$$
\begin{aligned}
f(Q)
&=\frac{G_1(Q)}{H_1(Q)}\\
&=\frac{G_1(Q)}{H_1(Q)}
  \left(\sum_{i=1}^m A_iH_i\right)(Q)\\
&=\sum_{i=1}^m A_i(Q)\frac{G_1(Q)H_i(Q)}{H_1(Q)}\\
&=\sum_{i=1}^m A_i(Q)G_i(Q)\\
&=F(Q).
\end{aligned}
$$

The homomorphism above is therefore also surjective.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossener Körper/Algebraische (reguläre) Funktion auf D(f)/Ist R f/Fakt -->

### Corollary: sections on a principal open set {#br-ak-2025-2026-l14-cor-01}

Let $F\in R$ in the situation of the preceding theorem. Then

$$
\Gamma(D(F),\mathcal O)=R_F.
$$

#### Proof {#br-ak-2025-2026-l14-cor-01-proof}

This follows directly from Lemma 14.7 and Theorem 14.9.

<!-- upstream_entity: Hilbertsches Problem/14/Schnittring/Bemerkung -->

### Remark: Hilbert's fourteenth problem {#br-ak-2025-2026-l14-rem-02}

One variant of Hilbert's fourteenth problem asks whether the ring of
algebraic functions $\Gamma(U,\mathcal O)$ is finitely generated for every
open set $U$. This is true for open sets of the form $U=D(f)$, also when
$R$ is regular or factorial, and in small dimensions. In general, however,
it is false.

> **Edition note:** “Small dimensions” is the source's informal wording;
> it specifies no dimension bound or additional hypotheses. No precise
> low-dimensional theorem is being asserted by that phrase here.

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
