---
title: "Lecture 3 - Linear Constructions of Vector Bundles and Presheaves"
stable_id: br-bgk-2019-l03
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 3"
upstream_pageid: 109005
upstream_revid: 793623
upstream_timestamp: "2022-08-25T06:25:18Z"
upstream_mediawiki_sha1: 065d606279906a405645b5b97abf2e3c027e2b4c
source_url: "https://de.wikiversity.org/w/index.php?oldid=793623"
authority_manifest: authority/wikiversity-bgk/unit-03/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 60270cc7ba74a4ed744687ae18c3887eca8a2fff6bce48a819be102d4a619a5a
lecture_xml: authority/wikiversity-bgk/unit-03/lecture-03.xml
lecture_xml_sha256: 7c048b329215669e01d8068cd150f5a1bee11bc00c2466e2d9b63e3d7abfa258
lecture_expanded_tex: authority/wikiversity-bgk/unit-03/lecture-03-expanded.tex
lecture_expanded_tex_sha256: 04989737d12bf8ac77127e60f193e6ac2c19201d4f5d66221f8c5e1de85a87eb
official_pdf: authority/artifacts/bgk-lecture-03-official.pdf
official_pdf_sha256: f418f7acb52670e0d274528450101c93f7dacdef880f99d4aa0e80ac920da884
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 3: Linear Constructions of Vector Bundles and Presheaves {#br-bgk-2019-l03}

## Linear constructions of vector bundles {#br-bgk-2019-l03-s01}

There are many constructions for vector spaces, such as the direct sum, tensor product and dual space. We want to introduce corresponding constructions for vector bundles. Fibrewise, they should agree with the constructions of linear algebra, while also taking into account how the fibres depend on the base space. We shall work with gluing data for vector bundles and use the fact that, given two vector bundles on a topological space $X$, there is always a sufficiently fine open cover of $X$ relative to which both bundles admit trivialisations. In particular, we can reduce to the case where both bundles are given by matrix descriptions. The constructions then take place at the level of matrix operations.

### Definition 3.1: direct sum {#br-bgk-2019-l03-def-01}

Let $E$ and $F$ be real vector bundles over a topological space $X$, with trivialisations

$$
\alpha_i:E|_{U_i}\longrightarrow U_i\times\mathbb R^m
$$

and

$$
\beta_i:F|_{U_i}\longrightarrow U_i\times\mathbb R^n.
$$

The vector bundle obtained from the gluing data

$$
G_i=U_i\times\mathbb R^m\times\mathbb R^n
$$

and

$$
\varphi_{ij}:G_i|_{U_i\cap U_j}\longrightarrow G_j|_{U_i\cap U_j},
$$

with

$$
\varphi_{ij}(x,v,w)
=\bigl(x,\alpha_j(\alpha_i^{-1}(x,v)),
          \beta_j(\beta_i^{-1}(x,w))\bigr),
$$

is called the *direct sum* of $E$ and $F$, denoted by $E\oplus F$.

> **Editorial note - fibre coordinates.** In the source formula above, $\alpha_j(\alpha_i^{-1}(x,v))$ and $\beta_j(\beta_i^{-1}(x,w))$ are themselves pairs containing the base point. In the second and third slots of $\varphi_{ij}(x,v,w)$, only their fibre coordinates are intended; formally, apply $\operatorname{pr}_2$ to each pair. The base coordinate remains $x$. The tensor, exterior-power and homomorphism constructions below likewise use the induced linear maps on each fibre.

If $E$ is given by the matrix description

$$
\varphi_{ij}:U_i\cap U_j\longrightarrow\operatorname{GL}_m(\mathbb R)
$$

and $F$ by

$$
\psi_{ij}:U_i\cap U_j\longrightarrow\operatorname{GL}_n(\mathbb R),
$$

then a matrix description of $E\oplus F$ is obtained by placing the two matrices in the diagonal blocks of an $(m+n)\times(m+n)$ matrix and filling the other blocks with zeros.

### Definition 3.2: tensor product {#br-bgk-2019-l03-def-02}

Let $E$ and $F$ be real vector bundles over $X$, with trivialisations $\alpha_i$ and $\beta_i$ as above. The vector bundle obtained from the gluing data

$$
G_i=U_i\times(\mathbb R^m\otimes\mathbb R^n)
$$

and

$$
\varphi_{ij}:G_i|_{U_i\cap U_j}\longrightarrow G_j|_{U_i\cap U_j},
\qquad
\varphi_{ij}
=\bigl(\alpha_j\circ\alpha_i^{-1}\bigr)
 \otimes
 \bigl(\beta_j\circ\beta_i^{-1}\bigr),
$$

is called the *tensor product* of $E$ and $F$, denoted by $E\otimes F$. Here the tensor product of the linear maps is taken at each base point.

Given matrix descriptions of the two bundles, a matrix description of their tensor product is obtained by the *Kronecker product*: every entry of one matrix is multiplied by every entry of the other.

### Definition 3.3: exterior power {#br-bgk-2019-l03-def-03}

Let $E$ be a real vector bundle of rank $m$ over a topological space $X$, with trivialisations

$$
\alpha_i:E|_{U_i}\longrightarrow U_i\times\mathbb R^m,
$$

and let $r\in\mathbb N$. The vector bundle obtained from the gluing data

$$
G_i=U_i\times\bigwedge^r\mathbb R^m
$$

and

$$
\varphi_{ij}:G_i|_{U_i\cap U_j}\longrightarrow G_j|_{U_i\cap U_j},
\qquad
\varphi_{ij}=\bigwedge^r\bigl(\alpha_j\circ\alpha_i^{-1}\bigr),
$$

is called the *$r$th exterior power* of $E$, denoted by $\bigwedge^rE$. At each base point, the $r$th exterior power of the corresponding linear map is taken.

Given a matrix description of $E$, a matrix description of $\bigwedge^rE$ is obtained by assembling all determinants of $r\times r$ submatrices into a matrix.

### Definition 3.4: determinant bundle {#br-bgk-2019-l03-def-04}

Let $E$ be a real vector bundle of rank $m$ over a topological space $X$. The $m$th exterior power

$$
\bigwedge^mE
$$

is called the *determinant bundle* of $E$, denoted by $\det E$.

The determinant bundle is a line bundle. Its matrix description is given by the determinant.

### Definition 3.5: homomorphism bundle {#br-bgk-2019-l03-def-05}

Let $E$ and $F$ be real vector bundles over a topological space $X$, with trivialisations

$$
\alpha_i:E|_{U_i}\longrightarrow U_i\times\mathbb R^m,
\qquad
\beta_i:F|_{U_i}\longrightarrow U_i\times\mathbb R^n.
$$

The vector bundle obtained from the gluing data

$$
G_i=U_i\times\operatorname{Hom}_{\mathbb R}
       (\mathbb R^m,\mathbb R^n)
$$

and

$$
\varphi_{ij}:G_i|_{U_i\cap U_j}\longrightarrow G_j|_{U_i\cap U_j},
$$

with

$$
\varphi_{ij}(\theta)
=\bigl(\beta_j\circ\beta_i^{-1}\bigr)
 \circ\theta\circ
 \bigl(\alpha_i\circ\alpha_j^{-1}\bigr),
$$

is called the *homomorphism bundle* from $E$ to $F$, denoted by $\operatorname{Hom}(E,F)$.

### Definition 3.6: dual bundle {#br-bgk-2019-l03-def-06}

For a real vector bundle $E$ over a topological space $X$, the homomorphism bundle

$$
\operatorname{Hom}(E,X\times\mathbb R)
$$

is called the *dual bundle* of $E$, denoted by $E^*$.

On a manifold, the dual of the tangent bundle is called the *cotangent bundle*.

## Presheaves {#br-bgk-2019-l03-s02}

### Definition 3.7: presheaf {#br-bgk-2019-l03-def-07}

Let $X$ be a topological space. A *presheaf* $\mathcal F$ on $X$ is an assignment associating a set $\mathcal F(U)$ to each open set $U\subseteq X$, and a map

$$
\rho_{V,U}:\mathcal F(V)\longrightarrow\mathcal F(U),
$$

to each pair of open sets $U\subseteq V$, subject to the following two conditions.

1. For $U=V$,

   $$
   \rho_{U,U}=\operatorname{Id}_{\mathcal F(U)}.
   $$

2. For open sets $U\subseteq V\subseteq W$,

   $$
   \rho_{W,U}=\rho_{V,U}\circ\rho_{W,V}.
   $$

The maps $\rho_{V,U}$ are called *restriction maps*. The set $\mathcal F(U)$ is also called the value of the presheaf on the open set $U$.

The following constructions are basic examples of presheaves, and later of sheaves.

### Example 3.8: continuous maps {#br-bgk-2019-l03-exa-01}

Let $X$ and $Z$ be topological spaces. To each open set $U\subseteq X$, associate the set of continuous maps from $U$ to $Z$, namely

$$
C^0(U,Z)=\{\varphi:U\to Z\mid\varphi\text{ continuous}\}.
$$

Every continuous map $\varphi:U\to Z$ can be restricted to an open subset $V\subseteq U$. Moreover, for $U\subseteq V\subseteq W$, restriction from $W$ to $U$ can be performed either in one step or in two. Thus this construction is a presheaf.

The following special case has additional structure, namely that of a ringed space.

### Example 3.9: continuous real-valued functions {#br-bgk-2019-l03-exa-02}

Let $X$ be a topological space. To each open set $U\subseteq X$, associate the set of continuous real-valued functions on $U$,

$$
\mathcal C(U)=C^0(U,\mathbb R)
=\{f:U\to\mathbb R\mid f\text{ continuous}\}.
$$

Since every continuous function on $U$ can be restricted to any open subset $V\subseteq U$, this construction is a presheaf.

### Example 3.10: differentiable functions {#br-bgk-2019-l03-exa-03}

Let $X$ be a differentiable manifold. To each open set $U\subseteq X$, associate the set of differentiable real-valued functions on $U$,

$$
\mathcal C(U)=C^1(U,\mathbb R)
=\{f:U\to\mathbb R\mid f\text{ continuously differentiable}\}.
$$

Since every differentiable function on $U$ can be restricted to any open subset $V\subseteq U$, this construction is a presheaf.

### Example 3.11: constant presheaf {#br-bgk-2019-l03-exa-04}

On a topological space $X$, for a fixed set $M$, the assignment associating $M$ to every open set $U\subseteq X$ and the identity on $M$ to every inclusion is a presheaf. It is called the *constant presheaf*.

For the next example, think of a vector bundle over the base $X$.

### Example 3.12: the presheaf of continuous sections {#br-bgk-2019-l03-exa-05}

Let $X$ and $Y$ be topological spaces, and let

$$
p:Y\longrightarrow X
$$

be a fixed continuous map. For each open set $U\subseteq X$, this induces a continuous map

$$
Y|_U=p^{-1}(U)\longrightarrow U.
$$

To $U$, associate the set of continuous sections of this map over $U$,

$$
S(U,Y)=\{s:U\to p^{-1}(U)\mid s\text{ a continuous section of }p\}.
$$

A continuous section can be restricted to any open subset $V\subseteq U$, with its codomain restricted accordingly to $p^{-1}(V)$. Thus this construction is a presheaf.

Because of this important example, an element $s\in\mathcal F(U)$ is also called a *section* of the presheaf $\mathcal F$ over $U$. For the restriction of a section to a smaller open set $V\subseteq U$, we also write

$$
s|_V=\rho_{U,V}(s).
$$

### Definition 3.13: subpresheaf {#br-bgk-2019-l03-def-08}

Let $\mathcal F$ be a presheaf on a topological space $X$. A presheaf $\mathcal G$ is called a *subpresheaf* of $\mathcal F$ if, for every open set $U\subseteq X$,

$$
\mathcal G(U)\subseteq\mathcal F(U),
$$

and, for every $U\subseteq V$, the restriction maps are compatible:

$$
\rho^{\mathcal G}_{V,U}
=\rho^{\mathcal F}_{V,U}|_{\mathcal G(V)}.
$$

> **Editorial note - restriction condition missing from the source.** The source definition states only $\mathcal G(U)\subseteq\mathcal F(U)$ for each $U$ and does not state compatibility of the restriction maps. This edition includes the restriction condition above so that the object defined is indeed a subpresheaf; the shorter source form is preserved in this note.

Since differentiable functions on a manifold are in particular continuous, the presheaf of differentiable functions forms a subsheaf of the presheaf of continuous real-valued functions.

## Presheaves with additional structure {#br-bgk-2019-l03-s03}

### Definition 3.14: presheaf of groups {#br-bgk-2019-l03-def-09}

A presheaf $\mathcal F$ on a topological space $X$ is called a *presheaf of groups* if $\mathcal F(U)$ is a group for every open set $U\subseteq X$ and, for every inclusion $U\subseteq V$, the restriction map

$$
\rho_{V,U}:\mathcal F(V)\longrightarrow\mathcal F(U)
$$

is a group homomorphism.

### Definition 3.15: presheaf of commutative rings {#br-bgk-2019-l03-def-10}

A presheaf $\mathcal F$ on a topological space $X$ is called a *presheaf of commutative rings* if $\mathcal F(U)$ is a commutative ring for every open set $U\subseteq X$ and, for every inclusion $U\subseteq V$, the restriction map

$$
\rho_{V,U}:\mathcal F(V)\longrightarrow\mathcal F(U)
$$

is a ring homomorphism.

### Remark 3.16: presheaves as functors {#br-bgk-2019-l03-rem-01}

A presheaf $\mathcal F$ on a topological space $(X,\mathcal T)$ can be viewed as a contravariant functor

$$
\mathcal F:\mathcal T\longrightarrow\operatorname{MEN},
$$

where $\mathcal T$ is regarded as a category as in Appendix Example 1.11, and $\operatorname{MEN}$ denotes the category of sets. Likewise, a presheaf of commutative groups is a contravariant functor to the category of commutative groups, and a presheaf of commutative rings is a contravariant functor to the category of commutative rings, and so on.

### Definition 3.17: topological group {#br-bgk-2019-l03-def-11}

A *topological group* is a group $G$ which is also a topological space, such that the group operation

$$
G\times G\longrightarrow G,
\qquad (g,h)\longmapsto g\circ h,
$$

and inversion

$$
G\longrightarrow G,
\qquad g\longmapsto g^{-1},
$$

are continuous maps.

Examples of topological groups are

$$
(\mathbb R,+),\quad
(\mathbb R\setminus\{0\},\cdot),\quad
(\mathbb C,+),\quad
(\mathbb C\setminus\{0\},\cdot),\quad
(\mathbb R^n,+),
$$

the circle $S^1$ with addition of angles, the general linear groups $\operatorname{GL}_n(\mathbb R)$ and $\operatorname{GL}_n(\mathbb C)$, and a complex torus $\mathbb C/\Gamma$ for a lattice $\Gamma\subseteq\mathbb C$. Every group becomes a topological group when equipped with the discrete topology.

For a topological space $X$, the set of continuous maps from $X$ to a topological group $G$ is itself a group under the natural operation. Restriction to an open subset is a group homomorphism. Therefore the assignment

$$
U\longmapsto C^0(U,G)
$$

is a presheaf of groups on $X$.

## Stalks of presheaves {#br-bgk-2019-l03-s04}

A fundamental idea behind vector bundles and presheaves is to distinguish meaningfully between local and global properties of geometric objects and to understand their interplay. A local property, for example, is one that holds on “small” open sets. We often want to replace small open sets by still smaller ones, particularly to understand behaviour in an arbitrarily small neighbourhood of a point. We introduce the following concepts for this purpose.

### Definition 3.18: topological filter {#br-bgk-2019-l03-def-12}

Let $X$ be a topological space. A collection $F$ of open subsets of $X$ is called a *filter* if the following hold for open sets $U$ and $V$:

1. $X\in F$;
2. if $U\in F$ and $U\subseteq V$, then $V\in F$;
3. if $U\in F$ and $V\in F$, then $U\cap V\in F$.

The most important examples here are neighbourhood filters of points: such a filter consists of all open neighbourhoods of a fixed point.

> **Editorial note - corrupted source sentence.** The source prints “Die wichtigsten Filter sind für und die Umgebungsfilter zu einer Punkt, der aus allen offenen Mengen eines fixierten Punktes besteht.” This sentence is grammatically corrupted. Based on the definition just given and the use of filters in the definition of a stalk below, this edition gives a complete contextual reading about neighbourhood filters, without attributing this reconstruction to the source author.

### Definition 3.19: directed set {#br-bgk-2019-l03-def-13}

A nonempty ordered set $(I,\preccurlyeq)$ is called *directed* if for every $i,j\in I$ there is a $k\in I$ such that

$$
i,j\preccurlyeq k.
$$

> **Editorial note - nonempty directed systems.** The source does not explicitly require $I\ne\varnothing$. This standard hypothesis is included here because the later assertion that a directed colimit of groups has a group structure would otherwise fail for the empty system. All neighbourhood-filter systems used here are nonempty.

We regard a topological filter as a set ordered by inclusion. The intersection property of a filter makes it a directed set; the direction convention is $\preccurlyeq\,=\,\supseteq$.

### Definition 3.20: ordered and directed systems {#br-bgk-2019-l03-def-14}

Let $(I,\preccurlyeq)$ be an ordered index set. A family

$$
M_i,\qquad i\in I,
$$

is called an *ordered system of sets* if:

1. for $i\preccurlyeq j$ there is a map $\varphi_{ij}:M_i\to M_j$;
2. for $i\preccurlyeq j\preccurlyeq k$ we have $\varphi_{ik}=\varphi_{jk}\circ\varphi_{ij}$.

If the index set is also directed, the family is called a *directed system of sets*.

If all the $M_i$ are groups, respectively rings, and all maps between them are group homomorphisms, respectively ring homomorphisms, we speak of an ordered or directed system of groups, respectively rings.

### Definition 3.21: colimit {#br-bgk-2019-l03-def-15}

Let $(M_i)_{i\in I}$ be a directed system of sets. The *colimit*, also called the direct or inductive limit, of the system is

$$
\operatorname{colim}_{i\in I}M_i
=\left(\biguplus_{i\in I}M_i\right)\big/\!\sim.
$$

Here $\sim$ is the equivalence relation declaring two elements $m\in M_i$ and $n\in M_j$ equivalent if there is a $k\in I$ with $i,j\preccurlyeq k$ and

$$
\varphi_{ik}(m)=\varphi_{jk}(n).
$$

In particular, $s_i\in M_i$ is equivalent to its image $\varphi_{ik}(s_i)\in M_k$ for all $i\preccurlyeq k$. If the system is a directed system of groups or rings, the colimit of sets can also be given a group or ring structure. This is because two colimit elements represented by $s_i\in M_i$ and $s_j\in M_j$ can be identified with their images in some $M_k$ with $i,j\preccurlyeq k$, where the operation is then performed. See Exercise 3.13.

Our main example is the directed system determined by a topological filter for a presheaf $\mathcal F$ on $X$, namely

$$
\mathcal F(U),\qquad U\in F.
$$

### Definition 3.22: stalk at a point {#br-bgk-2019-l03-def-16}

For a presheaf $\mathcal F$ on a topological space $X$ and a point $P\in X$,

$$
\mathcal F_P
:=\operatorname{colim}_{P\in U}\Gamma(U,\mathcal F)
$$

is called the *stalk* of the presheaf at $P$.

In particular, every section $s\in\mathcal F(U)$ and every point $P\in U$ determine a unique element

$$
s_P\in\mathcal F_P,
$$

called the *germ* of $s$ at $P$. The map

$$
\mathcal F(U)\longrightarrow\mathcal F_P,
\qquad s\longmapsto s_P,
$$

is called a restriction map and is denoted by $\rho_{U,P}$. For $P\in V\subseteq U$, the following diagram commutes:

$$
\begin{array}{ccc}
\mathcal F(U)&\xrightarrow{\rho_{U,V}}&\mathcal F(V)\\
&\searrow\scriptstyle\rho_{U,P}&\downarrow\scriptstyle\rho_{V,P}\\
&&\mathcal F_P.
\end{array}
$$

The following definition is slightly more general.

### Definition 3.23: stalk at a filter {#br-bgk-2019-l03-def-17}

For a presheaf $\mathcal G$ on a topological space $X$ and a topological filter $F$,

$$
\mathcal G_F
:=\operatorname{colim}_{U\in F}\Gamma(U,\mathcal G)
$$

is called the *stalk* of the presheaf at the filter $F$.

## Morphisms of presheaves {#br-bgk-2019-l03-s05}

### Definition 3.24: morphism of presheaves {#br-bgk-2019-l03-def-18}

Let $\mathcal F$ and $\mathcal G$ be presheaves on a topological space $X$. A *morphism of presheaves*

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

is a family of maps

$$
\varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
$$

for every open set $U\subseteq X$, such that for every open inclusion $U\subseteq V$ the following diagram commutes:

$$
\begin{array}{ccc}
\mathcal F(V)&\xrightarrow{\varphi_V}&\mathcal G(V)\\
\downarrow\scriptstyle\rho^{\mathcal F}_{V,U}&&
\downarrow\scriptstyle\rho^{\mathcal G}_{V,U}\\
\mathcal F(U)&\xrightarrow{\varphi_U}&\mathcal G(U).
\end{array}
$$

> **Editorial note - reversed source diagram.** For $U\subseteq V$, the source diagram places $\mathcal F(U)$ and $\mathcal G(U)$ in the top row, $\mathcal F(V)$ and $\mathcal G(V)$ in the bottom row, and labels the downward vertical arrows $\rho_{U,V}$. Presheaves are contravariant, so restriction maps instead go from the value on $V$ to the value on $U$. This edition displays the correctly typed diagram above, with superscripts distinguishing the two presheaves; the source layout is preserved in this note.

### Definition 3.25: isomorphism of presheaves {#br-bgk-2019-l03-def-19}

A morphism of presheaves $\varphi:\mathcal F\to\mathcal G$ on $X$ is called an *isomorphism* if, for every open subset $U\subseteq X$, the map

$$
\varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
$$

is a bijection.

### Lemma 3.26: identity, composition and inclusion {#br-bgk-2019-l03-lem-01}

Let $X$ be a topological space and $\mathcal F,\mathcal G,\mathcal H$ presheaves on $X$. The following statements hold.

1. The identity $\mathcal F\to\mathcal F$ is a morphism of presheaves.
2. If $\varphi:\mathcal F\to\mathcal G$ and $\psi:\mathcal G\to\mathcal H$ are morphisms of presheaves, then $\psi\circ\varphi$ is also a morphism of presheaves.
3. For a subpresheaf $\mathcal F\subseteq\mathcal G$, the natural inclusion is a morphism of presheaves.

> **Editorial note - source typographical error.** In the third item, the source and Exercise 3.17 print *Prägraben*, an evident typographical error for *Prägarben* (presheaves). This edition uses the mathematically correct term.

#### Proof {#br-bgk-2019-l03-lem-01-proof}

See Exercise 3.17.

### Lemma 3.27: induced maps on stalks {#br-bgk-2019-l03-lem-02}

A morphism of presheaves

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

on a topological space $X$ defines, for every point $P\in X$, a map between stalks

$$
\varphi_P:\mathcal F_P\longrightarrow\mathcal G_P
$$

compatible with the restriction maps. That is, for $P\in U$, the diagram

$$
\begin{array}{ccc}
\mathcal F(U)&\xrightarrow{\varphi_U}&\mathcal G(U)\\
\downarrow\scriptstyle\rho_{U,P}&&\downarrow\scriptstyle\rho_{U,P}\\
\mathcal F_P&\xrightarrow{\varphi_P}&\mathcal G_P
\end{array}
$$

commutes.

#### Proof {#br-bgk-2019-l03-lem-02-proof}

Let $s_P\in\mathcal F_P$. This means that there are an open neighbourhood $P\in U\subseteq X$ and an $s\in\mathcal F(U)$ with $\rho_{U,P}(s)=s_P$. Set

$$
\varphi_P(s_P):=\rho_{U,P}\bigl(\varphi_U(s)\bigr).
$$

We must show that this definition is independent of the representative $s$ and of $U$. Let $t\in\mathcal F(V)$ be another representative. Since $s_P=t_P$, there is an open neighbourhood

$$
P\in W\subseteq U\cap V
$$

such that $s|_W=t|_W$. Then

$$
\varphi_U(s)|_W
=\varphi_W(s|_W)
=\varphi_W(t|_W)
=\varphi_V(t)|_W,
$$

and hence

$$
\rho_{U,P}\bigl(\varphi_U(s)\bigr)
=\rho_{V,P}\bigl(\varphi_V(t)\bigr).
$$

Thus the map $\varphi_P$ is well-defined and the diagram above commutes.
