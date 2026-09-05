---
title: "Lecture 22 - The Divisor Class Group"
stable_id: br-bgk-2019-l22
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 22"
upstream_pageid: 109026
upstream_revid: 1003751
upstream_timestamp: "2025-06-08T15:48:32Z"
upstream_mediawiki_sha1: c81e7984c77ecb9624a5aa799029d3bbd3e80823
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003751"
authority_manifest: authority/wikiversity-bgk/unit-22/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 98e1716c4a8e95d42a19fd6a8b9efb04e222687e5bb6dc296ae42496baab1e39
lecture_xml: authority/wikiversity-bgk/unit-22/lecture-22.xml
lecture_xml_sha256: d231b1260ad47b265cd975cbc9205b213b3562a51bc1d36082d81ebdf2cb9146
lecture_expanded_tex: authority/wikiversity-bgk/unit-22/lecture-22-expanded.tex
lecture_expanded_tex_sha256: 28cca51595ca349e6ff98df7abe3ea45e51344ddfe55603b7f46d64ef88169ac
official_pdf: authority/artifacts/bgk-lecture-22-official.pdf
official_pdf_sha256: 710a732e3683593615ad9a6a005504e207b173248f06b46539e20b9018dd886e
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete_semantic_authority_bound
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
rights_ledger: authority/RIGHTS-bgk-unit-22.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-22.json
asset_closure_sha256: e7bf39c238717349b7d2e02a8f05eb252fe6aa39199bce82a8c9f60d1b5ea718
---

# Lecture 22: The Divisor Class Group {#br-bgk-2019-l22}

## Weil divisors {#br-bgk-2019-l22-s01}

We call an irreducible closed subset $Y\subset X$ of codimension $1$
in an integral scheme $X$ a *prime divisor*. If $X$ is normal and
Noetherian, the local ring $\mathcal O_{X,\eta}$ at the generic point
$\eta$ of $Y$ is a discrete valuation ring. Thus every element

$$
f\ne 0
$$

of the function field $K(X)$ has a well-defined order along $Y$,
which we denote by $\operatorname{ord}_Y(f)$. If $\pi$ denotes
a uniformiser, that is, a generator of the maximal ideal, in the discrete
valuation ring $\mathcal O_{X,\eta}$, we can write

$$
f=u\pi^n
$$

with a unit $u$ of that ring and $n\in\mathbb Z$. This exponent $n$
is called the order of $f$ along $Y$. Positive order means a zero,
whereas negative order means a pole. If

$$
U=\operatorname{Spek}(R)\subseteq X
$$

is an affine open subset with $U\cap Y\ne\varnothing$, then $Y$
corresponds to a prime ideal $\mathfrak p$ of height $1$ in $R$,
and the local ring satisfies

$$
\mathcal O_{X,\eta}=R_{\mathfrak p}.
$$

<!-- upstream_entity: Noethersches normales integres Schema/Hauptdivisor/Definition -->

### Definition 22.1: principal divisor {#br-bgk-2019-l22-def-01}

Let $X$ be a normal Noetherian integral scheme with function field $K$,
and let $f\in K$, $f\ne 0$. The formal sum

$$
\operatorname{div}(f)
=\sum_{Y\text{ prime divisor}}\operatorname{ord}_Y(f)\cdot Y,
$$

where $\operatorname{ord}_Y(f)$ denotes the order of $f$ in the local
ring at $Y$, is called the *principal divisor* defined by $f$.

The principal divisor thus describes the zeros and poles of the function
$f$. We first show that a principal divisor is a finite sum.

<!-- upstream_entity: Noethersches normales integres Schema/Hauptdivisor/Endlich/Fakt -->

### Lemma 22.2: a principal divisor has finite support {#br-bgk-2019-l22-lem-01}

Let $X$ be a normal Noetherian integral scheme with function field $K$,
and let $f\in K$, $f\ne 0$. There are only finitely many prime divisors
$Y$ with

$$
\operatorname{ord}_Y(f)\ne 0.
$$

#### Proof {#br-bgk-2019-l22-lem-01-proof}

Let $U\subseteq X$ be a non-empty affine open subset with

$$
f\in R=\Gamma(U,\mathcal O_X).
$$

Since the generic point of $X$ belongs to $U$, the prime divisors
not meeting $U$ are irreducible components of $X\smallsetminus U$.
The set $X\smallsetminus U$ is closed in $X$ and hence Noetherian,
so it has only finitely many components. We therefore need only consider
prime divisors meeting $U$. Their generic points correspond to prime
ideals of height $1$ in $R$. We have

$$
\operatorname{ord}_Y(f)=\operatorname{ord}_{\mathfrak p}(f)\geq 0,
$$

and this is positive only if $f\in\mathfrak p$. The prime ideals
$\mathfrak p$ of height $1$ containing $f$ are the minimal prime
ideals of $R/(f)$; since the ring is Noetherian, there are only finitely
many of them.

<!-- upstream_entity: Noethersches normales integres Schema/Weildivisor/Definition -->

### Definition 22.3: Weil divisor {#br-bgk-2019-l22-def-02}

Let $X$ be a normal Noetherian integral scheme. A formal sum

$$
\sum_Y n_Y\cdot Y,
$$

where $Y$ ranges over the prime divisors of $X$ and only finitely many
$n_Y$ are non-zero, is called a *Weil divisor* on $X$.

A Weil divisor is an arbitrary prescription for the “theoretically possible”
zeros and poles of a rational function. Such a prescription need not,
however, be realised by a function. A divisor whose coefficients all satisfy
$a_Y\geq 0$ is called *effective*. On an irreducible normal (hence smooth)
curve $X$, a prime divisor is simply a closed point. In this case,
a Weil divisor is a finite sum

$$
\sum_{P\in X}n_P\cdot P.
$$

> **Editorial note - coefficients and smoothness.** The coefficients of a
> Weil divisor are integers. The source leaves this implicit and calls a
> normal curve smooth: a normal Noetherian curve is regular, but smoothness
> over its ground field additionally holds, for example, when that field is perfect.

<!-- upstream_entity: Noethersches normales integres Schema/Weildivisorengruppe/Definition -->

### Definition 22.4: Weil divisor group {#br-bgk-2019-l22-def-03}

Let $X$ be a normal Noetherian integral scheme. The group of all Weil
divisors, with componentwise addition, is called the *Weil divisor group*
of $X$. It is denoted by

$$
\operatorname{Div}(X).
$$

<!-- upstream_entity: Noethersches normales integres Schema/Hauptdivisor/Gruppenhomomorphismus/Fakt -->

### Lemma 22.5: principal divisors define a group homomorphism {#br-bgk-2019-l22-lem-02}

Let $X$ be a normal Noetherian integral scheme with function field $K$.
The map

$$
K^\times\longrightarrow\operatorname{Div}(X),
\qquad f\longmapsto\operatorname{div}(f),
$$

is a group homomorphism.

#### Proof {#br-bgk-2019-l22-lem-02-proof}

By Lemma 22.2, the principal divisor of $f$ is indeed a Weil divisor.
For a fixed prime divisor $Y$ with its associated discrete valuation
ring $\mathcal O_Y$, the homomorphism property follows from Lemma 21.7 (1).

## The divisor class group {#br-bgk-2019-l22-s02}

<!-- upstream_entity: Noethersches normales integres Schema/Divisorenklassengruppe/Definition -->

### Definition 22.6: divisor class group {#br-bgk-2019-l22-def-04}

Let $X$ be a normal Noetherian integral scheme with function field $K$.
The quotient group

$$
\operatorname{DKG}(X)
=\operatorname{Div}(X)/\operatorname{HDiv}(X)
$$

is called the *divisor class group* of $X$.

For a normal Noetherian integral domain $R$, similarly,

$$
\operatorname{DKG}(R)
=\operatorname{DKG}(\operatorname{Spek}(R))
$$

is called the divisor class group of the ring $R$. In number theory,
when $R$ is the ring of integers in a finite extension of $\mathbb Q$,
this group is also called the *ideal class group*. Divisors defining
the same divisor class are called *linearly equivalent*.

<!-- upstream_entity: Normaler noetherscher Bereich/Divisorenklassengruppe/Faktoriell/Fakt -->

### Theorem 22.7: a divisor criterion for unique factorisation {#br-bgk-2019-l22-thm-01}

Let $R$ be a normal Noetherian integral domain, and let
$\operatorname{DKG}(R)$ denote the divisor class group of $R$.
The following statements are equivalent.

1. $R$ is a unique factorisation domain.
2. Every prime ideal of height $1$ is principal.
3. Every divisor is principal.
4. $\operatorname{DKG}(R)=0$.

#### Proof {#br-bgk-2019-l22-thm-01-proof}

Suppose (1) holds and $\mathfrak p$ is a prime ideal of height $1$.
There is an element $f\in\mathfrak p$, $f\ne 0$.
It has a prime factorisation

$$
f=p_1\cdots p_n.
$$

Since $\mathfrak p$ is prime, we must have $p_i\in\mathfrak p$ for
some $i$. The height condition then gives

$$
(p_i)=\mathfrak p.
$$

Now suppose every prime ideal of height $1$ is principal. Writing

$$
\mathfrak p=(p),
$$

we have the divisor relation

$$
\operatorname{div}(p)=1\cdot\mathfrak p,
$$

since $p$ belongs to no other prime ideal of height $1$, and in
$R_{\mathfrak p}$ the element $p$ also generates
$\mathfrak pR_{\mathfrak p}$. Thus the generators of the divisor class
group are principal divisors, so all divisors are principal.
The equivalence of (3) and (4) is clear.

> **Editorial note - group name in the source.** At this step, the source
> prints *Divisorenklassengruppe* (divisor class group), although the argument
> uses prime divisors as generators. This edition preserves the printed
> group name and does not silently replace it with the divisor group.

Next suppose every divisor is principal. For every prime ideal
$\mathfrak p$ of height $1$, there is an element $f\in Q(R)$, $f\ne 0$,
with

$$
\operatorname{div}(f)=1\cdot\mathfrak p.
$$

Since this principal divisor is non-negative, Theorem 21.12 gives $f\in R$.
Thus among prime ideals of height $1$, $f$ belongs only to $\mathfrak p$.
Let

$$
\mathfrak p=(g_1,\ldots,g_n).
$$

Then

$$
\operatorname{div}(g_i)\geq\operatorname{div}(f),
$$

so $g_i/f\in R$, that is, $g_i\in(f)$, and hence $\mathfrak p=(f)$.

Finally, suppose (2) holds and take $f\in R$, $f\ne 0$. Let
$\mathfrak p_1,\ldots,\mathfrak p_s$ be the minimal prime ideals
containing $f$. By Krull's principal ideal theorem, they all have height
$1$. Let $\mathfrak p_i=(p_i)$ with prime element $p_1$. We have

$$
\operatorname{div}(f)=\sum_{i=1}^s n_i\mathfrak p_i.
$$

The element $\prod_{i=1}^s p_i^{n_i}$ has the same principal divisor.
Therefore the quotient

$$
f\bigg/\prod_{i=1}^s p_i^{n_i}
$$

is a unit, and

$$
f=u\prod_{i=1}^s p_i^{n_i}
$$

for a unit $u$. Thus $R$ is a unique factorisation domain.

> **Editorial note - subscript on the prime element.** In the final step,
> the source writes $\mathfrak p_i=(p_i)$ but then refers to the prime
> element $p_1$. This edition preserves the printed subscript;
> the subsequent product again uses $p_i$.

<!-- upstream_entity: Projektiver Raum/Körper/Divisorenklassengruppe/Beispiel -->

### Example 22.8: the divisor class group of projective space {#br-bgk-2019-l22-exm-01}

We shall describe the Weil divisors and the divisor class group of projective
space $\mathbb P_K^d$ over a field $K$, with $d\geq 1$.
Consider the disjoint decomposition

$$
\mathbb P_K^d
=D_+(X_0)\cup V_+(X_0)
=\mathbb A_K^d\cup\mathbb P_K^{d-1}.
$$

In other words, we fix the hyperplane

$$
H=V_+(X_0)\cong\mathbb P_K^{d-1}
$$

“at infinity”. A prime divisor of projective space either equals the
hyperplane on the right, or meets the affine space on the left non-trivially
and can be viewed as a prime ideal of height $1$ in the polynomial ring

$$
K\left[\frac{X_1}{X_0},\ldots,\frac{X_d}{X_0}\right].
$$

Every function $f$ in the function field can be written uniquely, up to
scaling and cancellation of common factors, as

$$
f=\frac PQ,
$$

with

$$
P,Q\in K\left[\frac{X_1}{X_0},\ldots,\frac{X_d}{X_0}\right].
$$

Using prime factorisations of $P$ and $Q$, we can write directly

$$
f=\prod_{i=1}^n cP_i^{\nu_i},
$$

with a constant $c\ne 0$ and $\nu_i\in\mathbb Z$, and read off the
principal divisor of $f$ as far as components in affine space are concerned.
The order of $f$ “at infinity”, at $V_+(X_0)$, is obtained as follows.
The local ring at this prime divisor is

$$
\begin{aligned}
K[X_0,X_1,\ldots,X_n]_{((X_0))}
&=\left(
K[X_0,X_1,\ldots,X_n]_{
(K[X_0,X_1,\ldots,X_n]\smallsetminus(X_0))
\cap\{\text{homogeneous elements}\}}
\right)_0\\
&=K\left(\frac{X_2}{X_1},\ldots,\frac{X_d}{X_1}\right)
\left[\frac{X_0}{X_1}\right]_{(\frac{X_0}{X_1})}.
\end{aligned}
$$

We rewrite $P$ (and similarly $Q$ or $f$) by replacing each $X_i/X_0$ with

$$
\frac{X_i}{X_1}\cdot\frac{X_1}{X_0}.
$$

We view this expression as a rational function in the single variable
$X_0/X_1$ over the field

$$
K\left(\frac{X_2}{X_1},\ldots,\frac{X_d}{X_1}\right).
$$

Its degree in $X_0/X_1$, which is typically negative, is its order.
For example,

$$
\begin{aligned}
P
&=\frac{X_1}{X_0}+\left(\frac{X_2}{X_0}\right)^3\\
&=\frac{X_1}{X_0}
+\left(\frac{X_2}{X_1}\right)^3
\left(\frac{X_1}{X_0}\right)^3\\
&=\left(
\left(\frac{X_0}{X_1}\right)^2
+\left(\frac{X_2}{X_1}\right)^3
\right)
\left(\frac{X_0}{X_1}\right)^{-3},
\end{aligned}
$$

so the order is $-3$.

> **Editorial note - factorisation and order.** In the source product, the
> constant belongs outside the product: $f=c\prod_iP_i^{\nu_i}$, for
> $f\ne0$. The source's “degree” at infinity means the valuation in
> $X_0/X_1$, namely the least Laurent exponent for a polynomial expressed
> in that variable, not the usual degree of a rational function. For
> $f=P/Q$, the order is $\deg Q-\deg P$.

Since the polynomial ring is a unique factorisation domain, on affine space
every Weil divisor equals a principal divisor. Thus every Weil divisor
is linearly equivalent to a divisor of the form

$$
nV_+(X_0),\qquad n\in\mathbb Z.
$$

The class of $V_+(X_0)$ is also called the *hyperplane class*.
For $n\ne 0$, such a divisor is not principal: such a principal divisor
would be trivial on affine space and would therefore have to come from a
constant, whereas a constant also has order $0$ at infinity.
Thus the divisor class group of projective space is $\mathbb Z$,
and any hyperplane can be chosen as a generator.

> **Editorial note - indices in the local-ring display.** The source uses
> $d$ for the dimension of projective space but writes
> $K[X_0,X_1,\ldots,X_n]$ in the local-ring display. This edition
> preserves both indices as printed.

## The divisor class group and the Picard group {#br-bgk-2019-l22-s03}

We now discuss the relationship between divisors and invertible subsheaves
of the function-field sheaf $\mathcal K$, and between the divisor class
group and the Picard group. An invertible subsheaf

$$
\mathcal L\subseteq\mathcal K
$$

defines, for every point $x\in X$, a free $\mathcal O_{X,x}$-submodule
of rank $1$,

$$
\mathcal L_x\subseteq\mathcal K_x=K.
$$

If $\mathcal O_{X,x}$ is a discrete valuation ring with uniformiser
$\pi$, as happens on a normal scheme at the generic point of every prime
divisor, then

$$
\mathcal L_x=\pi^n\mathcal O_{X,x}
$$

for a unique $n\in\mathbb Z$. We denote this number by
$\operatorname{ord}_Y(\mathcal L)$ when $Y$ is the prime divisor in question.

<!-- upstream_entity: Lokal faktorielles integres Schema/Invertierbare Untergarben/Weildivisoren/Fakt -->

### Theorem 22.9: invertible subsheaves and Weil divisors {#br-bgk-2019-l22-thm-02}

Let $X$ be a locally factorial Noetherian integral scheme. The invertible
$\mathcal O_X$-submodules of the constant function-field sheaf $\mathcal K$
and the Weil divisors correspond to one another via

$$
\mathcal L\longmapsto
\sum_Y\operatorname{ord}_Y(\mathcal L)
$$

and

$$
D=\sum_Y a_YY\longmapsto\mathcal L_D,
$$

where

$$
\mathcal L_D(U)
=\{f\in K\mid \operatorname{ord}_Y(f)\geq D
\text{ for all }Y\in U\}
$$

for an open subset $U\subseteq X$. These correspondences are compatible
with the group structures; trivial subsheaves correspond to principal
divisors. Invertible ideals

$$
\mathcal L\subseteq\mathcal O_X\subseteq\mathcal K
$$

correspond to effective divisors.

> **Editorial note - two source displays.** In the first map, the source
> omits the factor $Y$ after $\operatorname{ord}_Y(\mathcal L)$,
> although the proof later writes
> $D=\sum_Y\operatorname{ord}_Y(\mathcal L)Y$.
> In the definition of $\mathcal L_D(U)$, the source compares
> $\operatorname{ord}_Y(f)$ directly with the divisor $D$, without naming
> its coefficient. Both displays are preserved as they stand.
> The intended first sum is $\sum_Y\operatorname{ord}_Y(\mathcal L)Y$.
> For non-empty $U$, the intended section set is
> $\{0\}\cup\{f\in K^\times\mid\operatorname{ord}_Y(f)\geq a_Y
> \text{ for all }Y\text{ meeting }U\}$; the zero section must be included,
> since the order was defined only for non-zero functions. On the empty
> open set there is the unique zero section.

#### Proof {#br-bgk-2019-l22-thm-02-proof}

There is a finite affine open cover

$$
X=\bigcup_{i\in I}U_i
$$

with

$$
\mathcal L=(f_i)\mathcal O_X|_{U_i},
$$

where $f_i\in K$ and $f_i\ne 0$. By Lemma 22.2, for each $i$
there are only finitely many irreducible Weil divisors in $U_i$ satisfying

$$
\operatorname{ord}_Y(f_i)\ne 0.
$$

Consequently,

$$
D=\sum_Y\operatorname{ord}_Y(\mathcal L)Y
$$

is indeed a Weil divisor.

Conversely, let $D$ be a Weil divisor and $\mathcal L$ the associated
subsheaf of the constant sheaf of the function field. We must show that
$\mathcal L$ is invertible. Take a point $x\in X$ and an affine open
neighbourhood

$$
x\in U\subseteq X.
$$

By hypothesis, the local ring $\mathcal O_{X,x}$ is a unique factorisation
domain. By Theorem 22.7, the divisor $D_x$ consisting of all irreducible
components of $D$ passing through $x$ is principal. By removing the
components of $D$ not passing through $x$, we can replace $U$ with a
smaller affine neighbourhood $V$ of $x$ on which the divisor is principal.
There we have

$$
D|_V=\operatorname{div}(f)|_V
$$

for some $f\in K$, and then

$$
\mathcal L_D|_V=(f)\mathcal O_X|_V.
$$

We must now show that these correspondences are inverse to one another.
Start with an invertible subsheaf and use the notation above.
On $U_i$ we have

$$
D|_{U_i}=\operatorname{div}(f_i)|_{U_i}.
$$

Hence for $g\in K$, membership

$$
g\in\{f\in K\mid\operatorname{ord}_Y(f)\geq D
\text{ for all }Y\in U\}
$$

holds precisely when the relation between principal divisors

$$
\operatorname{div}(g)\geq\operatorname{div}(f_i)
$$

holds on $U$. By Theorem 21.12, this is equivalent to

$$
g\in f\cdot\Gamma(X,\mathcal O_X).
$$

If we start with a Weil divisor, it locally equals a principal divisor.
An element of the function field with that principal divisor then locally
generates the associated invertible sheaf, and the same element is used
to recover the associated divisor.

> **Editorial note - notation at the end of the source proof.** After using
> the generator $f_i$ on $U_i$, the source prints
> $g\in f\cdot\Gamma(X,\mathcal O_X)$. This edition does not silently
> change the index or the open set.
> On $U_i$, the intended conclusion is
> $g\in f_i\Gamma(U_i,\mathcal O_X)$. In the preceding shrinking argument,
> one removes the support of $D-\operatorname{div}(f)$, whose components
> avoid $x$, not just components of $D$ avoiding $x$; this also removes any
> extra zeros or poles of the chosen $f$.

In the correspondence above, ideals correspond to effective divisors, and
the principal ideal $(f)$ corresponds to the principal divisor
$\operatorname{div}(f)$. There are also good reasons to modify this
correspondence by inserting a minus sign. With that convention, an effective
divisor corresponds to a global section of the associated invertible sheaf.

<!-- upstream_entity: Schema/Lokal faktoriell/Picardgruppe und Divisorenklassengruppe/Fakt -->

### Theorem 22.10: the divisor class group and the Picard group {#br-bgk-2019-l22-thm-03}

Let $X$ be a locally factorial Noetherian integral scheme.
Then the divisor class group of $X$ agrees with the Picard group of $X$.

#### Proof {#br-bgk-2019-l22-thm-03-proof}

This follows from Lemma 20.6 and Theorem 22.9.

<!-- upstream_entity: Glattes Schema/Picardgruppe und Divisorenklassengruppe/Fakt -->

### Corollary 22.11: the case of smooth schemes {#br-bgk-2019-l22-cor-01}

Let $X$ be a smooth scheme over an algebraically closed field $K$.
Then the divisor class group of $X$ agrees with the Picard group of $X$.

#### Proof {#br-bgk-2019-l22-cor-01-proof}

On a smooth scheme, the local rings are regular by Theorem 18.16, and
they are unique factorisation domains by Theorem 25.12 of
*Singularity Theory (Osnabrück 2019)*. Thus the statement follows
from Theorem 22.10.

<!-- upstream_entity: Projektiver Raum/Körper/Picardgruppe/Z/Fakt -->

### Theorem 22.12: the Picard group of projective space {#br-bgk-2019-l22-thm-04}

The Picard group of projective space $\mathbb P_K^d$, with $d\geq 1$,
over a field $K$ is $\mathbb Z$. The invertible sheaves on projective
space are represented by the twisted structure sheaves

$$
\mathcal O_{\mathbb P_K^d}(\ell),
\qquad \ell\in\mathbb Z.
$$

#### Proof {#br-bgk-2019-l22-thm-04-proof}

This follows from Theorem 22.10 and Example 22.8. Under the explicit
correspondence in Theorem 22.9, the negative of the hyperplane class
corresponds to the tautological bundle $\mathcal O_{\mathbb P_K^d}(1)$.

> **Editorial note - bundle name.** The negative hyperplane class does
> correspond to $\mathcal O(1)$ under the sign convention of Theorem 22.9.
> With the usual twisting notation also used in Exercise 22.13, however,
> the tautological line subbundle is $\mathcal O(-1)$; $\mathcal O(1)$ is
> its dual. The source's bundle name should be read with this distinction.
