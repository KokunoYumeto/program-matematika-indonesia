---
title: "Lecture 7 - Ringed Spaces and Locally Ringed Spaces"
stable_id: br-bgk-2019-l07
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 7"
upstream_pageid: 109011
upstream_revid: 1003731
upstream_timestamp: "2025-06-08T15:30:36Z"
upstream_mediawiki_sha1: b0b4d8ab050e0948ecc6e3f8cb86a1c7091c1f3d
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003731"
authority_manifest: authority/wikiversity-bgk/unit-07/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 001074c62cedb1efc988d3214416d2d86a02976d5b22dc272f4fe064e72dfc95
lecture_xml: authority/wikiversity-bgk/unit-07/lecture-07.xml
lecture_xml_sha256: 34de24fb81ee5bae5fa6664ecbc592b1103f6497e766f77be4404aadea6fcb4a
lecture_expanded_tex: authority/wikiversity-bgk/unit-07/lecture-07-expanded.tex
lecture_expanded_tex_sha256: b321142f917f6bf95e169b293cbd407288d59cd21266f09ad0174f0547a47189
official_pdf: authority/artifacts/bgk-lecture-07-official.pdf
official_pdf_sha256: 9be947907e8d819612a7c824fc7dd949ca447887547732769f967f27f19df43a
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 7: Ringed Spaces and Locally Ringed Spaces {#br-bgk-2019-l07}

## Ringed spaces {#br-bgk-2019-l07-s01}

<!-- upstream_entity: Beringter Raum/Definition -->

### Definition 7.1: ringed space {#br-bgk-2019-l07-def-01}

A topological space equipped with a sheaf of commutative rings is called a
*ringed space*.

A ringed space is often written in the form

$$
(X,\mathcal O_X),
$$

where $X$ is the underlying space and $\mathcal O_X$ is its sheaf of
commutative rings. This sheaf is called the *structure sheaf* of the ringed
space. The evaluation

$$
\Gamma(U,\mathcal O_X)=\mathcal O_X(U)
$$

is also called the *ring of sections* on the open set $U\subseteq X$, and
the notation

$$
\Gamma(U,\mathcal O_X)
$$

is called the *ring of global sections* (on $U$). Following Examples 3.9
and 3.10, we have the following standard examples.

> **Edition note — global sections.** The source repeats
> $\Gamma(U,\mathcal O_X)$ when naming the global ring of sections.
> This is global on the open subspace $U$; the global ring of sections of
> $X$ itself is $\Gamma(X,\mathcal O_X)$.

<!-- upstream_entity: Topologischer Raum/Prägarbe der stetigen Funktionen/Garbe/beringter Raum/Beispiel -->

### Example 7.2: real-valued continuous functions {#br-bgk-2019-l07-exa-01}

Let $X$ be a topological space. For each open set $U\subseteq X$, set

$$
\mathcal C(U)=C^0(U,\mathbb R)
 =\{f:U\longrightarrow\mathbb R\mid f\text{ continuous}\}.
$$

This is a commutative ring, and the assignment $U\mapsto\mathcal C(U)$,
together with the natural restriction maps, is a sheaf. This makes $X$ a
ringed space.

<!-- upstream_entity: Differenzierbare Mannigfaltigkeit/Prägarbe der differenzierbaren Funktionen/Beispiel -->

### Example 7.3: differentiable functions {#br-bgk-2019-l07-exa-02}

On a differentiable manifold $M$, each open set $U\subseteq M$ has the
commutative ring

$$
C^1(U,\mathbb R)=\{f:U\longrightarrow\mathbb R\mid f\text{ continuously differentiable}\}.
$$

This assignment is a sheaf, making $M$ a ringed space.

<!-- upstream_entity: Komplexe Mannigfaltigkeit/Holomorphe Funktion/Beringter Raum/Beispiel -->

### Example 7.4: holomorphic functions {#br-bgk-2019-l07-exa-03}

On a complex manifold $M$, for each open set $U\subseteq M$ we have the
commutative ring

$$
C^1(U,\mathbb C)=\{f:U\longrightarrow\mathbb C\mid f\text{ holomorphic}\}.
$$

This assignment is a sheaf and makes $M$ a ringed space.

> **Edition note — the source notation $C^1$.** In this example the
> right-hand side explicitly means holomorphic functions. The source's
> symbol $C^1(U,\mathbb C)$ is retained, but does not mean all functions
> that are merely continuously differentiable in real coordinates.

<!-- upstream_entity: Kommutativer Ring/Punkt/Beringter Raum/Beispiel -->

### Example 7.5: a one-point space {#br-bgk-2019-l07-exa-04}

Let $R$ be a commutative ring and let $X=\{P\}$ be a topological space with
just one point. Setting

$$
\Gamma(X,\mathcal O_X):=R,\qquad
\Gamma(\varnothing,\mathcal O_X):=0
$$

makes $X$ a ringed space.

<!-- upstream_entity: Beringter Raum/Punkt/Halm/Definition -->

### Definition 7.6: stalk of a ringed space {#br-bgk-2019-l07-def-02}

For a point $P\in X$ in a ringed space $\bigl(X,\mathcal O_X\bigr)$, the
stalk of the structure sheaf at $P$ is called the *stalk at $P$*. It is
denoted by

$$
\mathcal O_{X,P}\quad\text{or, for short,}\quad\mathcal O_P.
$$

## Morphisms of ringed spaces {#br-bgk-2019-l07-s02}

For a continuous map $\varphi:X\to Y$ between topological spaces, each open
set $V\subseteq Y$ gives a ring homomorphism

$$
\begin{aligned}
C^0(V,\mathbb R)&\longrightarrow C^0(\varphi^{-1}(V),\mathbb R),\\
f&\longmapsto f\circ\varphi.
\end{aligned}
$$

This pulled-back continuous function is also written $\varphi^*f$. We use
the same notation in the following abstract definition.

<!-- upstream_entity: Beringter Raum/Morphismus/Definition -->

### Definition 7.7: morphism of ringed spaces {#br-bgk-2019-l07-def-03}

Let $(X,\mathcal O_X)$ and $(Y,\mathcal O_Y)$ be ringed spaces. A *morphism
of ringed spaces* is a continuous map

$$
\varphi:X\longrightarrow Y
$$

together with a family of ring homomorphisms

$$
\varphi_V^*:\Gamma(V,\mathcal O_Y)
\longrightarrow\Gamma(\varphi^{-1}(V),\mathcal O_X)
$$

for every open set $V\subseteq Y$, compatible with the restriction maps.

Compatibility means that, for open sets $W\subseteq V\subseteq Y$, the
diagram

$$
\begin{array}{ccc}
\Gamma(V,\mathcal O_Y)&\xrightarrow{\ \varphi_V^*\ }&
\Gamma(\varphi^{-1}(V),\mathcal O_X)\\
\downarrow&&\downarrow\\
\Gamma(W,\mathcal O_Y)&\xrightarrow{\ \varphi_W^*\ }&
\Gamma(\varphi^{-1}(W),\mathcal O_X)
\end{array}
$$

commutes. A morphism $\varphi:X\to Y$ of ringed spaces induces, for every
point $P\in X$, a ring homomorphism on stalks

$$
\mathcal O_{Y,\varphi(P)}\longrightarrow\mathcal O_{X,P}.
$$

Explicitly, if $f\in\mathcal O_{Y,\varphi(P)}$ is represented by
$f\in\Gamma(V,\mathcal O_Y)$ on an open neighbourhood $\varphi(P)\in V$,
its image is the germ of

$$
\varphi^*(f)\in\Gamma(\varphi^{-1}(V),\mathcal O_X).
$$

<!-- upstream_entity: Beringter Raum/Isomorphismus/Definition -->

### Definition 7.8: isomorphism of ringed spaces {#br-bgk-2019-l07-def-04}

A morphism of ringed spaces

$$
\varphi:(X,\mathcal O_X)\longrightarrow(Y,\mathcal O_Y)
$$

is called an *isomorphism* if there is a morphism of ringed spaces

$$
\psi:(Y,\mathcal O_Y)\longrightarrow(X,\mathcal O_X)
$$

such that

$$
\psi\circ\varphi=\operatorname{Id}_X,\qquad
\varphi\circ\psi=\operatorname{Id}_Y,
$$

where both identities are understood as identities of ringed spaces.

## Gluing data for ringed spaces {#br-bgk-2019-l07-s03}

The following construction extends Lemma 2.6.

<!-- upstream_entity: Beringter Raum/Verklebungsdatum/Definition -->

### Definition 7.9: gluing data {#br-bgk-2019-l07-def-05}

*Gluing data* for ringed spaces consist of the following.

1. A family of ringed spaces

   $$
   (U_i,\mathcal O_{U_i}),\qquad i\in I.
   $$

2. For each pair $(i,j)$, an open set $U_{ij}\subseteq U_i$, with
   $U_{ii}=U_i$.

3. For each pair $(i,j)$, an isomorphism of ringed spaces

   $$
   \varphi_{ji}:(U_{ij},\mathcal O_{U_{ij}})
   \longrightarrow(U_{ji},\mathcal O_{U_{ji}}),
   $$

   with $\varphi_{ii}=\operatorname{Id}_{(U_i,\mathcal O_{U_i})}$.

4. For indices $i,j,k\in I$, the *cocycle condition*

   $$
   \varphi_{kj}\circ\varphi_{ji}=\varphi_{ki}
   $$

   holds as a morphism from $U_{ik}\cap U_{ij}$ to $U_k$.

<!-- upstream_entity: Beringter Raum/Verklebungsdatum/Existenz/Fakt -->

### Lemma 7.10: existence of the glued space {#br-bgk-2019-l07-lem-01}

Suppose gluing data $\bigl(U_i,\mathcal O_{U_i}\bigr)_{i\in I}$ for ringed
spaces are given. Then there are a ringed space $(X,\mathcal O_X)$, an
open cover

$$
X=\bigcup_{i\in I}V_i,
$$

and isomorphisms of ringed spaces

$$
\psi_i:U_i\longrightarrow V_i
$$

such that

$$
\psi_i(U_{ij})=V_i\cap V_j
$$

and

$$
\psi_i|_{U_{ij}}=\psi_j|_{U_{ji}}\circ\varphi_{ji}.
$$

#### Proof {#br-bgk-2019-l07-lem-01-proof}

The underlying space $X$ exists by Lemma 2.6. For an open set
$W\subseteq X$, we have the cover

$$
W=\bigcup_{i\in I}(W\cap V_i).
$$

Define the ring of sections by

$$
\begin{aligned}
\Gamma(W,\mathcal O_X):=\bigl\{(s_i)_{i\in I}\mid {}
&
s_i\in\Gamma\bigl(\psi_i^{-1}(W\cap V_i),\mathcal O_{U_i}\bigr),\\
&\varphi_{ij}^*\!\left(s_i\big|_{\psi_i^{-1}(W)\cap U_{ij}}\right)
=s_j\big|_{\psi_j^{-1}(W)\cap U_{ji}}\bigr\}.
\end{aligned}
$$

This is a sheaf of commutative rings on $X$ which, on $V_i$, agrees via
$\psi_i$ with the given sheaf on $U_i$.

> **Edition note — transport of sections.** The source writes
> $\varphi_{ji}(s_i|_{\cdots})$. Since $\varphi_{ji}$ maps points from
> $U_{ij}$ to $U_{ji}$, its action in that direction on sections is the
> pullback by its inverse $\varphi_{ij}$. The formula above writes this
> as $\varphi_{ij}^*$, in accordance with Definition 7.7.

## Locally ringed spaces {#br-bgk-2019-l07-s04}

<!-- upstream_entity: Lokal beringter Raum/Definition -->

### Definition 7.11: locally ringed space {#br-bgk-2019-l07-def-06}

A ringed space $(X,\mathcal O_X)$ is called a *locally ringed space* if,
for every point $P\in X$, the stalk $\mathcal O_P$ is a local ring.

<!-- upstream_entity: Topologischer Raum/Stetige Funktionen/Lokal beringter Raum/Beispiel -->

### Example 7.12: continuous functions {#br-bgk-2019-l07-exa-05}

A topological space $X$, together with the sheaf of continuous functions
$C^0(-,\mathbb R)$, is a locally ringed space. For every point $P\in X$
and every continuous function $f$ defined on an open neighbourhood of $P$,

$$
f(P)\ne0
$$

if and only if there is an open neighbourhood on which $f$ is invertible.
Consequently, every stalk $\mathcal O_P$ is a local ring and $X$ is locally
ringed. The same applies to real and complex manifolds.

> **Edition note — point variable.** The source refers here to a
> neighbourhood of $x$ after introducing $P$. The translation consistently
> uses $P$.

<!-- upstream_entity: Lokal beringter Raum/Punkt/Restekörper/Definition -->

### Definition 7.13: residue field {#br-bgk-2019-l07-def-07}

For a locally ringed space $(X,\mathcal O_X)$ and a point $P\in X$, the
residue field of the local ring $\mathcal O_P$ is called the *residue
field* of the point $P$. It is denoted by

$$
\kappa(P).
$$

The residue field of a topological space equipped with the sheaf of
continuous functions is simply $\mathbb R$; see Exercise 7.16.

<!-- upstream_entity: Lokal beringter Raum/Funktion/Auswertung/Definition -->

### Definition 7.14: evaluation {#br-bgk-2019-l07-def-08}

For a locally ringed space $(X,\mathcal O_X)$, a point $x\in X$, and a
global function

$$
f\in\Gamma(X,\mathcal O_X),
$$

the value of $f$ in the residue field $\kappa(x)$ is called the
*evaluation* of $f$ at $x$ and is denoted by $f(x)$.

In a locally ringed space, for every $f\in\Gamma(X,\mathcal O_X)$ and
$P\in X$, we have the equivalences

$$
f(P)=0\text{ in }\kappa(P)
\quad\Longleftrightarrow\quad
f_P\in\mathfrak m_P
\quad\Longleftrightarrow\quad
f_P\text{ is not a unit in }\mathcal O_{X,P}.
$$

> **Edition note — source capitalisation.** The source writes “IN einem
> lokal beringten Raum”. The translation uses normal English
> capitalisation; the mathematical content and the equivalences are
> unchanged.

<!-- upstream_entity: Lokal beringter Raum/Morphismus/Definition -->

### Definition 7.15: morphism of locally ringed spaces {#br-bgk-2019-l07-def-09}

For locally ringed spaces $(X,\mathcal O_X)$ and $(Y,\mathcal O_Y)$, a
*morphism of locally ringed spaces* from $X$ to $Y$ is a morphism of ringed
spaces $\varphi:X\to Y$ whose induced ring homomorphism on stalks

$$
\varphi_P^*:\mathcal O_{Y,\varphi(P)}\longrightarrow\mathcal O_{X,P}
$$

is a local homomorphism for every point $P\in X$.

## The invertibility locus {#br-bgk-2019-l07-s05}

<!-- upstream_entity: Lokal beringter Raum/Funktion/Invertierbarkeit/Offen/Fakt -->

### Lemma 7.16: openness of the invertibility locus {#br-bgk-2019-l07-lem-02}

For a locally ringed space $(X,\mathcal O_X)$ and a global function
$f\in\Gamma(X,\mathcal O_X)$, the set

$$
X_f:=\{P\in X\mid f(P)\ne0\text{ in }\kappa(P)\}
$$

is open.

#### Proof {#br-bgk-2019-l07-lem-02-proof}

First, $f(P)=0$ in the residue field if and only if
$f_P\in\mathfrak m_P$ in the local ring $\mathcal O_P$, and this holds
exactly when $f$ is not invertible in $\mathcal O_P$. Take $P\in X_f$.
Then $f$ is invertible in $\mathcal O_P$, so there is $g\in\mathcal O_P$
with

$$
gf=1.
$$

There is an open neighbourhood $P\in U\subseteq X$ on which $g$ has a
representative

$$
g\in\Gamma(U,\mathcal O_X),
$$

and, possibly after shrinking, an open neighbourhood $U'$ with

$$
fg=1.
$$

Thus $f$ is invertible on $U'$ and

$$
P\in U'\subseteq X_f.
$$

Taking the union of all such open neighbourhoods shows that $X_f$ is open.

In contrast, the set of points at which $f$, as an element of the stalk
$\mathcal O_P$, is nonzero need not be open; see Example 11.17.

<!-- upstream_entity: Lokal beringter Raum/Funktion/Invertierbarkeitsort/Definition -->

### Definition 7.17: invertibility locus {#br-bgk-2019-l07-def-10}

For a locally ringed space $(X,\mathcal O_X)$ and a global function
$f\in\Gamma(X,\mathcal O_X)$, the set

$$
X_f:=\{P\in X\mid f(P)\ne0\text{ in }\kappa(P)\}
$$

is called the *invertibility locus* of $f$.

By Exercise 7.20, $f$ is a unit in $\Gamma(X_f,\mathcal O_X)$.

<!-- upstream_entity: Lokal beringte Räume/Morphismus/Invertierbarkeitsort/Fakt -->

### Lemma 7.18: inverse image of an invertibility locus {#br-bgk-2019-l07-lem-03}

Let $X$ and $Y$ be locally ringed spaces, and let $\varphi:X\to Y$ be a
morphism of locally ringed spaces. For every

$$
f\in\Gamma(Y,\mathcal O_Y),
$$

we have

$$
\varphi^{-1}(Y_f)=X_{\varphi^*f}.
$$

#### Proof {#br-bgk-2019-l07-lem-03-proof}

The element $f$ is a unit in $\Gamma(Y_f,\mathcal O_Y)$. The induced ring
homomorphism

$$
\Gamma(Y_f,\mathcal O_Y)\longrightarrow
\Gamma\bigl(\varphi^{-1}(Y_f),\mathcal O_X\bigr)
$$

shows that $\varphi^*f$ is a unit in

$$
\Gamma\bigl(\varphi^{-1}(Y_f),\mathcal O_X\bigr),
$$

so

$$
\varphi^{-1}(Y_f)\subseteq X_{\varphi^*f}.
$$

Conversely, take $P\in X_{\varphi^*f}$. Then $\varphi^*f$ is a unit in the
local ring $\mathcal O_{X,P}$. Since the stalk homomorphism

$$
\mathcal O_{Y,\varphi(P)}\longrightarrow\mathcal O_{X,P}
$$

is local, $f\in\mathcal O_{Y,\varphi(P)}$ must also be a unit. This means
$\varphi(P)\in Y_f$, and therefore

$$
P\in\varphi^{-1}(Y_f).
$$

The two inclusions give the desired equality.
