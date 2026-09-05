---
title: "Lecture 10 - Schemes and Scheme Morphisms"
stable_id: br-bgk-2019-l10
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 10"
upstream_pageid: 109014
upstream_revid: 1003733
upstream_timestamp: "2025-06-08T15:32:21Z"
upstream_mediawiki_sha1: 4dfde713fd1b38ebf77c1be9a8717dbde34c76ba
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003733"
authority_manifest: authority/wikiversity-bgk/unit-10/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a8b6384c316086dde5825b6c776289f93a1a2c4a4654bac57148f9e25a6f197f
lecture_xml: authority/wikiversity-bgk/unit-10/lecture-10.xml
lecture_xml_sha256: 556c26db6a7eb22b32d9fbbfb0bf1c04e6d769a7738b3f5f14ed21410059e15c
lecture_expanded_tex: authority/wikiversity-bgk/unit-10/lecture-10-expanded.tex
lecture_expanded_tex_sha256: 8b05be7634ca7c81f3aca9a8c7c3cad93637563d7341fb9987a29541043c9d6e
official_pdf: authority/artifacts/bgk-lecture-10-official.pdf
official_pdf_sha256: 4f30cd25b1460fe216019e36529d80b3880b9ba7c7ee85ee6246f9454b51411a
media_credits: source/id-ID/media-credits-bgk-unit-10.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 10: Schemes and Scheme Morphisms {#br-bgk-2019-l10}

## Schemes {#br-bgk-2019-l10-s01}

<!-- upstream_entity: Schema/Beringter Raum/Definition -->

### Definition 10.1: scheme {#br-bgk-2019-l10-def-01}

A *scheme* is a ringed space $(X,\mathcal O_X)$ for which there is an
open cover

$$
X=\bigcup_{i\in I}U_i
$$

such that, for every $i$,

$$
(U_i,\mathcal O_X|_{U_i})
$$

is an affine scheme.

<!-- upstream_entity: Schema/Punkt/Offene Umgebung/Affin/Fakt -->

### Lemma 10.2: affine neighbourhoods inside open neighbourhoods {#br-bgk-2019-l10-lem-01}

Let $(X,\mathcal O_X)$ be a scheme and let $P\in X$ be a point. For
every open neighbourhood $P\in U$, there is an affine open neighbourhood

$$
P\in V\subseteq U.
$$

#### Proof {#br-bgk-2019-l10-lem-01-proof}

Take an affine open neighbourhood

$$
P\in W=\operatorname{Spec}(R).
$$

Then

$$
P\in U\cap W\subseteq\operatorname{Spek}(R)
$$

is an open subset of $\operatorname{Spek}(R)$, and therefore has the
form

$$
U\cap W=D(\mathfrak a)
$$

for an ideal $\mathfrak a\subseteq R$. Since

$$
D(\mathfrak a)=\bigcup_{f\in\mathfrak a}D(f),
$$

there is $f\in\mathfrak a$ with

$$
P\in D(f)\subseteq D(\mathfrak a)\subseteq U.
$$

By Lemma 9.13, $D(f)$ is affine.

> **Edition note — source operator notation.** The proof writes
> $W=\operatorname{Spec}(R)$ and then returns to
> $\operatorname{Spek}(R)$. Both spellings of the operator are retained
> and refer to the same ring spectrum.

<!-- upstream_entity: Schema/Offene Teilmenge/Affine Überdeckung/Fakt -->

### Lemma 10.3: an open subset of a scheme is a scheme {#br-bgk-2019-l10-lem-02}

Every open subset $U\subseteq X$ of a scheme $(X,\mathcal O_X)$ has a
cover by affine open sets and is therefore itself a scheme.

#### Proof {#br-bgk-2019-l10-lem-02-proof}

As an open subset of a ringed space, $U$ is also a ringed space. The
existence of an affine cover follows immediately from Lemma 10.2.

<!-- upstream_entity: Schema/Quasiaffin/Definition -->

### Definition 10.4: quasi-affine scheme {#br-bgk-2019-l10-def-02}

An open subset

$$
U\subseteq X=\operatorname{Spek}(R)
$$

of an affine scheme $X$ is called a *quasi-affine scheme*.

<!-- upstream_entity: Lokaler Ring/Spektrum/Punktiert/Definition -->

### Definition 10.5: punctured spectrum {#br-bgk-2019-l10-def-03}

For a local ring $(R,\mathfrak m)$, the space

$$
\operatorname{Spek}(R)\setminus\{\mathfrak m\}
$$

is called the *punctured spectrum* of $R$.

As ringed spaces, schemes can be glued along open subsets as in
Lemma 7.10. Here are two examples.

<!-- upstream_entity: Affine Geraden/Punktiert/Verklebung/Verdoppelte Gerade/Beispiel -->

### Example 10.6: the line with a doubled point {#br-bgk-2019-l10-exa-01}

Take two copies of the affine line,

$$
U=\mathbb A^1_K=\operatorname{Spek}(K[S]),
\qquad
V=\mathbb A^1_K=\operatorname{Spek}(K[T]),
$$

with the open subsets

$$
U'=\mathbb A^1_K\setminus\{(S)\}
=\operatorname{Spek}(K[S,S^{-1}])\subset\mathbb A^1_K
$$

and

$$
V'=\mathbb A^1_K\setminus\{(T)\}
=\operatorname{Spek}(K[T,T^{-1}])\subset\mathbb A^1_K.
$$

Consider the isomorphism

$$
\varphi:U'\longrightarrow V'
$$

determined by $S\mapsto T$, and glue $U$ and $V$ in the sense of
Lemma 7.10. The resulting space is a scheme $X$ called the line with a
doubled point. Denote the points of $X$ determined by $(S)$ and $(T)$
by $P$ and $Q$, respectively.

There is a commutative diagram of restriction homomorphisms

$$
\begin{matrix}
\Gamma(X,\mathcal O_X)&\longrightarrow&\Gamma(U,\mathcal O_X)=K[S]\\
\downarrow&&\downarrow\\
\Gamma(V,\mathcal O_X)=K[S]&\longrightarrow&
\Gamma(U',\mathcal O_X)=K[S,S^{-1}],
\end{matrix}
$$

where we have made the identification $S=T$. The sheaf condition gives

$$
\Gamma(X,\mathcal O_X)=K[S],
$$

and global functions have the same value at $P$ and $Q$. A similar
argument shows that the stalks also agree:

$$
\mathcal O_{X,P}=\mathcal O_{X,Q}=K[S]_{(S)}.
$$

The entire calculation takes place in the function field $K(S)$.

<!-- upstream_entity: Affine Geraden/Punktiert/Verklebung/Projektive Gerade/Beispiel -->

### Example 10.7: the projective line by gluing {#br-bgk-2019-l10-exa-02}

Again take two copies of the affine line

$$
U=\mathbb A^1_K=\operatorname{Spek}(K[S]),
\qquad
V=\mathbb A^1_K=\operatorname{Spek}(K[T])
$$

with the punctured open subsets

$$
U'=\mathbb A^1_K\setminus\{(S)\}
=\operatorname{Spek}(K[S,S^{-1}])\subset\mathbb A^1_K
$$

and

$$
V'=\mathbb A^1_K\setminus\{(T)\}
=\operatorname{Spek}(K[T,T^{-1}])\subset\mathbb A^1_K.
$$

Now use the isomorphism

$$
\varphi:U'\longrightarrow V',
\qquad S\longmapsto T^{-1},
$$

to glue $U$ and $V$ in the sense of Lemma 7.10. The resulting space,

$$
X=\mathbb P^1_K,
$$

is a model of the projective line over $K$. Denote the points determined
by $(S)$ and $(T)$ by $P$ and $Q$, respectively. For $K=\mathbb R$ or
$K=\mathbb C$ with the metric topology, a sequence in $U'$ converging
to $P\in U$ necessarily tends to infinity when viewed in $V$.

The commutative diagram of restriction homomorphisms is

$$
\begin{matrix}
\Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K})&\longrightarrow&
\Gamma(U,\mathcal O_{\mathbb P^1_K})=K[S]\\
\downarrow&&\downarrow\\
\Gamma(V,\mathcal O_{\mathbb P^1_K})=K[T]=K[S^{-1}]&\longrightarrow&
\Gamma(U',\mathcal O_{\mathbb P^1_K})=K[S,S^{-1}],
\end{matrix}
$$

with the identification $S=T^{-1}$. The sheaf condition gives

$$
\Gamma(X,\mathcal O_X)=K,
$$

since only the constant functions belong to both $K[S]$ and $K[S^{-1}]$;
the intersection is taken in the function field $K(S)$. Moreover,

$$
\mathcal O_{X,P}=K[S]_{(S)},
\qquad
\mathcal O_{X,Q}=K[S^{-1}]_{(S^{-1})}.
$$

## Scheme morphisms {#br-bgk-2019-l10-s02}

<!-- upstream_entity: Schema/Morphismus/Definition -->

### Definition 10.8: scheme morphism {#br-bgk-2019-l10-def-04}

A *scheme morphism*

$$
\varphi:X\longrightarrow Y
$$

between schemes $X$ and $Y$ is a morphism of locally ringed spaces.

We first want to make the map on spectra associated with a ring
homomorphism $\theta:R\to S$,

$$
\operatorname{Spek}(S)\longrightarrow\operatorname{Spek}(R),
$$

into a scheme morphism. This is a special case of the following theorem.

<!-- upstream_entity: Lokal beringter Raum/Affines Schema/Morphismus/Fakt -->

### Theorem 10.9: morphisms to an affine scheme {#br-bgk-2019-l10-thm-01}

Let $(X,\mathcal O_X)$ be a locally ringed space and let
$Y=\operatorname{Spek}(R)$ be an affine scheme. For every ring
homomorphism

$$
\theta:R\longrightarrow\Gamma(X,\mathcal O_X),
$$

there is a unique morphism of locally ringed spaces $X\to Y$ whose
homomorphism on global sections is $\theta$.

#### Proof {#br-bgk-2019-l10-thm-01-proof}

By Lemma 7.18, for every $x\in X$ we must have

$$
\varphi(x)
=\{f\in R\mid x\notin X_{\theta(f)}\}
=(\rho_x\circ\theta)^{-1}(\mathfrak m_x),
$$

where

$$
\rho_x:\Gamma(X,\mathcal O_X)\longrightarrow\mathcal O_{X,x}
$$

is the restriction homomorphism to the stalk $\mathcal O_{X,x}$ and
$\mathfrak m_x\subseteq\mathcal O_{X,x}$ is its maximal ideal. This
formula determines a continuous map, since

$$
\varphi^{-1}(D(f))=X_{\theta(f)};
$$

the sets $D(f)$ form a basis by Proposition 8.4(8), and
$X_{\theta(f)}$ is open by Lemma 7.16.

For every $f\in R$, there are ring homomorphisms

$$
R\mathrel{\mathop{\longrightarrow}^{\theta}}
\Gamma(X,\mathcal O_X)
\longrightarrow\Gamma(X_{\theta(f)},\mathcal O_X),
$$

and $\theta(f)$ becomes a unit in the rightmost ring. By Theorem 11.13
in the Commutative Algebra course, there is a unique homomorphism

$$
R_f\longrightarrow\Gamma(X_{\theta(f)},\mathcal O_X)
$$

compatible with these homomorphisms. By the sheaf property, for every
open set $D(\mathfrak a)$ we also obtain a unique homomorphism

$$
\Gamma(D(\mathfrak a),\mathcal O_Y)
\longrightarrow
\Gamma(\varphi^{-1}(D(\mathfrak a)),\mathcal O_X).
$$

Indeed, if

$$
D(\mathfrak a)=\bigcup_{i\in I}D(f_i),
$$

then

$$
\Gamma(D(\mathfrak a),\mathcal O_Y)
=\left\{
(s_i)_{i\in I}\in\prod_{i\in I}R_{f_i}
\ \middle|\
s_i=s_j\text{ in }R_{f_if_j}
\right\}
$$

and

$$
\Gamma(\varphi^{-1}(D(\mathfrak a)),\mathcal O_X)
=\left\{
(t_i)_{i\in I}\in
\prod_{i\in I}\Gamma(X_{\theta(f_i)},\mathcal O_X)
\ \middle|\
t_i=t_j\text{ in }\Gamma(X_{\theta(f_if_j)},\mathcal O_X)
\right\}.
$$

The homomorphisms already defined on $R_{f_i}$ and $R_{f_if_j}$ respect
the compatibility equations, and therefore give a homomorphism from the
ring in the first display to the ring in the second. These assignments
do indeed yield a morphism of locally ringed spaces.

> **Edition note — two source surfaces.** In the map $\rho_x$, the
> semantic witness writes $\Gamma(X,\mathcal O)$, while the context and
> surrounding maps use $\mathcal O_X$; the edition writes the subscript
> $X$ explicitly. The semantic witness also refers to Theorem 11.13 in
> Commutative Algebra, whereas the older official PDF prints Theorem
> 15.13. The edition follows the semantic authority's numbering and
> records the difference without conflating the editions of the cited
> course.

<!-- upstream_entity: Ringhomomorphismus/Spektrumsabbildung/Morphismus/Fakt -->

### Corollary 10.10: ring homomorphisms give morphisms of spectra {#br-bgk-2019-l10-cor-01}

Let $R$ and $S$ be commutative rings, and let $\theta:R\to S$ be a ring
homomorphism. There is a unique scheme morphism

$$
\operatorname{Spek}(S)\longrightarrow\operatorname{Spek}(R)
$$

whose homomorphism on global sections is $\theta$. Topologically, this is
the map on spectra.

#### Proof {#br-bgk-2019-l10-cor-01-proof}

This follows immediately from Theorem 10.9. The beginning of its proof
shows that the underlying topological map is the map on spectra.

<!-- upstream_entity: Lokal beringter Raum/Spek Z/Kanonischer Morphismus/Fakt -->

### Corollary 10.11: the canonical morphism to the spectrum of the integers {#br-bgk-2019-l10-cor-02}

For every locally ringed space $(X,\mathcal O_X)$, there is a canonical
morphism of locally ringed spaces

$$
X\longrightarrow\operatorname{Spek}(\mathbb Z).
$$

It sends a point $x\in X$ to the characteristic of its residue field
$\kappa(x)$.

> **Edition clarification — the target point.** A point of
> $\operatorname{Spek}(\mathbb Z)$ is a prime ideal. Thus “the
> characteristic” here means $\ker(\mathbb Z\to\kappa(x))$: it is $(0)$
> in characteristic zero and $(p)$ in characteristic $p>0$.

#### Proof {#br-bgk-2019-l10-cor-02-proof}

The canonical ring homomorphism

$$
\mathbb Z\longrightarrow\Gamma(X,\mathcal O_X)
$$

determines a unique morphism of locally ringed spaces

$$
X\longrightarrow\operatorname{Spek}(\mathbb Z)
$$

by Theorem 10.9.

<!-- upstream_entity: Lokal beringter Raum/Globale Funktion/Affine Gerade/Morphismus/Fakt -->

### Corollary 10.12: global functions give morphisms to the affine line {#br-bgk-2019-l10-cor-03}

Let $(X,\mathcal O_X)$ be a locally ringed space. Every global function

$$
f\in\Gamma(X,\mathcal O_X)
$$

determines a unique morphism of locally ringed spaces

$$
X\longrightarrow\mathbb A^1_{\mathbb Z},
$$

which sends the variable of the affine line to $f$. If
$\Gamma(X,\mathcal O_X)$ is a $K$-algebra over a field $K$, the function
$f$ also determines a morphism of locally ringed spaces

$$
X\longrightarrow\mathbb A^1_K.
$$

In this case, a point $x\in X$ is sent to the kernel of the ring
homomorphism

$$
K[T]\longrightarrow\kappa(x),
\qquad T\longmapsto f(x).
$$

#### Proof {#br-bgk-2019-l10-cor-03-proof}

The ring element $f\in\Gamma(X,\mathcal O_X)$ determines a unique
substitution homomorphism

$$
\mathbb Z[T]\longrightarrow\Gamma(X,\mathcal O_X).
$$

By Theorem 10.9, this homomorphism determines a unique morphism of locally
ringed spaces

$$
(X,\mathcal O_X)\longrightarrow
\operatorname{Spek}(\mathbb Z[T])=\mathbb A^1_{\mathbb Z}.
$$

The additional assertion follows in the same way.

<!-- upstream_entity: Lokal beringter Raum/Affiner Raum/Morphismus/Fakt -->

### Corollary 10.13: tuples of functions give morphisms to affine space {#br-bgk-2019-l10-cor-04}

Let $(X,\mathcal O_X)$ be a locally ringed space. Every tuple of functions

$$
f_1,\ldots,f_n\in\Gamma(X,\mathcal O_X)
$$

determines a unique morphism of locally ringed spaces

$$
X\longrightarrow\mathbb A^n_{\mathbb Z},
$$

which sends the variable $T_i$ of affine space to $f_i$. If
$\Gamma(X,\mathcal O_X)$ is an $R$-algebra over a commutative ring $R$,
the functions $f_1,\ldots,f_n$ also determine a morphism of locally
ringed spaces

$$
X\longrightarrow\mathbb A^n_R.
$$

In this case, a point $x\in X$ is sent to the kernel of the ring
homomorphism

$$
R[T_1,\ldots,T_n]\longrightarrow\kappa(x),
\qquad T_i\longmapsto f_i(x).
$$

#### Proof {#br-bgk-2019-l10-cor-04-proof}

See Exercise 10.3.

Thus a morphism to affine space is nothing other than a tuple of global
functions.

If $\varphi:X\to Y$ is a morphism, then for every open subset
$V\subseteq Y$, the induced map

$$
\varphi^{-1}(V)\longrightarrow V
$$

is also a morphism. If $V$ is moreover affine, then by Theorem 10.9 this
morphism is given locally on $Y$ by a ring homomorphism. This means that,
using an affine cover

$$
Y=\bigcup_{i\in I}V_i
=\bigcup_{i\in I}\operatorname{Spek}(R_i),
$$

the scheme morphism $\varphi:X\to Y$ is essentially determined by the
ring homomorphisms

$$
R_i\longrightarrow\Gamma(\varphi^{-1}(V_i),\mathcal O_X).
$$

## Schemes over a base scheme {#br-bgk-2019-l10-s03}

For a commutative $K$-algebra $A$ over a field $K$, the canonical ring
homomorphism $K\to A$ determines a canonical map on spectra

$$
\operatorname{Spek}(A)\longrightarrow\operatorname{Spek}(K).
$$

Topologically this is simply the constant map, but it still specifies how
the constants from $K$ are to be interpreted. In the context of schemes,
the role of a ground ring is taken by a base scheme.

<!-- upstream_entity: Schema/Basisschema/Definition -->

### Definition 10.14: scheme over a base {#br-bgk-2019-l10-def-05}

A scheme $X$ together with a fixed morphism

$$
p:X\longrightarrow S
$$

to another scheme $S$ is called a *scheme over $S$*. The scheme $S$ is
called the *base scheme*.

Often the base scheme is simply the spectrum of a field. By Corollary
10.11, every scheme is uniquely a scheme over
$\operatorname{Spek}(\mathbb Z)$. A scheme over
$\operatorname{Spek}(R)$ is also called a scheme over $R$. The role of
algebra homomorphisms is taken by morphisms compatible with the base.

<!-- upstream_entity: Schemata/Basisschema/Morphismus/Definition -->

### Definition 10.15: scheme morphism over a base {#br-bgk-2019-l10-def-06}

Let $X$ and $Y$ be schemes over a base scheme $S$. A scheme morphism

$$
\varphi:X\longrightarrow Y
$$

is called a *scheme morphism over $S$* if the diagram

$$
\begin{matrix}
X&\mathrel{\mathop{\longrightarrow}^{\varphi}}&Y\\
&\searrow&\downarrow\\
&&S
\end{matrix}
$$

commutes.

<!-- upstream_entity: Schemamorphismus/Von endlichem Typ/Definition -->

### Definition 10.16: morphism of finite type {#br-bgk-2019-l10-def-07}

A scheme morphism

$$
\varphi:X\longrightarrow Y
$$

is called *of finite type* if there is an affine open cover

$$
Y=\bigcup_{i\in I}V_i
$$

such that, for every $i\in I$, there is a finite affine cover

$$
\varphi^{-1}(V_i)=\bigcup_{j\in J_i}U_{ij}
$$

and, for every $j\in J_i$, the ring homomorphism

$$
\Gamma(V_i,\mathcal O_Y)
\longrightarrow
\Gamma(U_{ij},\mathcal O_X)
$$

is of finite type.

> **Edition note — conflicting indices in the source.** The source
> writes the cover $Y=\bigcup_{i\in I}V_i$, but then uses
> $\varphi^{-1}(V_i)=\bigcup_{i\in I_j}U_i$, the condition $i\in I_j$,
> and a map from $\Gamma(V_j,\mathcal O_Y)$. The edition explicitly
> replaces these dummy indices by $j\in J_i$ and $U_{ij}$, keeping the
> base open set $V_i$ fixed; the mathematical definition is not expanded.

## Immersions {#br-bgk-2019-l10-s04}

<!-- upstream_entity: Schema/Morphismus/Offene Einbettung/Definition -->

### Definition 10.17: open immersion {#br-bgk-2019-l10-def-08}

A scheme morphism $f:Y\to X$ is called an *open immersion* if $f$
induces an isomorphism onto an open subset of $X$.

<!-- upstream_entity: Schema/Morphismus/Abgeschlossene Einbettung/Definition -->

### Definition 10.18: closed immersion {#br-bgk-2019-l10-def-09}

A scheme morphism $f:Y\to X$ is called a *closed immersion* if $f(Y)$ is
a closed subset of $X$, there is a homeomorphism

$$
Y\longrightarrow f(Y),
$$

and the associated sheaf homomorphism

$$
\mathcal O_X\longrightarrow f_*\mathcal O_Y
$$

is surjective.

<!-- upstream_entity: Schema/Morphismus/Einbettung/Offen und abgeschlossen/Definition -->

### Definition 10.19: immersion {#br-bgk-2019-l10-def-10}

A scheme morphism $f:Y\to X$ is called an *immersion* if there is a
factorisation

$$
Y\mathrel{\mathop{\longrightarrow}^{g}}
Z\mathrel{\mathop{\longrightarrow}^{h}}X
$$

with $g$ an open immersion and $h$ a closed immersion.
