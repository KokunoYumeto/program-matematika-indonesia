---
title: "Lecture 5 - Sheafification, Homomorphisms and Quotient Sheaves"
stable_id: br-bgk-2019-l05
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 5"
upstream_pageid: 109009
upstream_revid: 1003725
upstream_timestamp: "2025-06-08T15:27:50Z"
upstream_mediawiki_sha1: 1697741995f2c7537d0b38edc16fe8df38024e13
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003725"
authority_manifest: authority/wikiversity-bgk/unit-05/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 328774ffd66341ba8841b86935037a043067202dd10916d3e0be5082faeac35e
lecture_xml: authority/wikiversity-bgk/unit-05/lecture-05.xml
lecture_xml_sha256: edc881b76f88954eeceb7fa0a1902791218e064b947adee9e01119969c21c237
lecture_expanded_tex: authority/wikiversity-bgk/unit-05/lecture-05-expanded.tex
lecture_expanded_tex_sha256: d5d29f43c3209ccf8c8f80290ba3e44e800552807d4975ae0e78cb2dcd73735f
official_pdf: authority/artifacts/bgk-lecture-05-official.pdf
official_pdf_sha256: 85be007896876a0717ef5eddfe64ed919aeb6559dce44ec2828ffe2b1d755085
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 5: Sheafification, Homomorphisms and Quotient Sheaves {#br-bgk-2019-l05}

## Sheafification {#br-bgk-2019-l05-s01}

A presheaf can be assigned a sheaf in a canonical way. This construction is called *sheafification*.

### Definition 5.1: sheafification {#br-bgk-2019-l05-def-01}

Let $\mathcal F$ be a presheaf on a topological space $X$. The presheaf given by

$$
\widetilde{\mathcal F}(U)
:=
\left\{
(s_P)_{P\in U}\in\prod_{P\in U}\mathcal F_P
\ \middle|\
\begin{array}{l}
\text{for every }P\in U\text{ there is an open set }V\\
\text{with }P\in V\subseteq U\text{ and }t\in\mathcal F(V)\\
\text{such that }s_Q=t_Q\text{ in }\mathcal F_Q
\text{ for every }Q\in V
\end{array}
\right\},
$$

together with the natural restriction maps, is called the *sheafification* of $\mathcal F$.

The condition in this definition, that the local sections define the same germs in the stalks, is also called the *compatibility condition*.

> **Editorial note - openness of the local neighbourhood.** The source formula writes only $P\in V\subseteq U$, without saying that $V$ is open. Since $\mathcal F(V)$ and this local construction use the presheaf, $V$ must be an open neighbourhood. This edition makes that condition explicit.

### Lemma 5.2: properties of sheafification {#br-bgk-2019-l05-lem-01}

Let $\mathcal F$ be a presheaf on a topological space $X$, and let $\widetilde{\mathcal F}$ be its sheafification. The following properties hold.

1. There is a natural presheaf morphism

   $$
   \eta:\mathcal F\longrightarrow\widetilde{\mathcal F},
   $$

   given on every open set $U$ by

   $$
   \begin{aligned}
   \eta_U:\mathcal F(U)&\longrightarrow\widetilde{\mathcal F}(U),\\
   s&\longmapsto(s_P)_{P\in U}.
   \end{aligned}
   $$

2. For every $P\in X$, there is a natural isomorphism

   $$
   \widetilde{\mathcal F}_P\cong\mathcal F_P.
   $$

3. The sheafification $\widetilde{\mathcal F}$ is a sheaf.

4. If $\mathcal F$ is already a sheaf, the natural morphism

   $$
   \mathcal F\longrightarrow\widetilde{\mathcal F}
   $$

   is an isomorphism.

5. For every presheaf morphism

   $$
   \psi:\mathcal F\longrightarrow\mathcal G
   $$

   to a sheaf $\mathcal G$, there is a unique factorisation

   $$
   \widetilde\psi:
   \widetilde{\mathcal F}\longrightarrow\mathcal G.
   $$

#### Proof {#br-bgk-2019-l05-lem-01-proof}

1. An element $s\in\mathcal F(U)$ defines a tuple

   $$
   (s_P)_{P\in U},
   $$

   which immediately satisfies the compatibility condition. Thus there is a well-defined map

   $$
   \eta_U:\mathcal F(U)\longrightarrow\widetilde{\mathcal F}(U).
   $$

   If $V\subseteq U$, we have the commutative diagram

   $$
   \begin{array}{ccc}
   \mathcal F(U)
   &\xrightarrow{\ \eta_U\ }&
   \displaystyle\prod_{P\in U}\mathcal F_P\\[2mm]
   {\scriptstyle\rho_{U,V}}\downarrow
   &&
   \downarrow\\[2mm]
   \mathcal F(V)
   &\xrightarrow{\ \eta_V\ }&
   \displaystyle\prod_{P\in V}\mathcal F_P.
   \end{array}
   $$

   Commutativity follows because the germ of a section in the stalk at a point depends only on the open neighbourhoods of that point.

2. By part (1) and Lemma 3.27, there is a natural map

   $$
   \mathcal F_P\longrightarrow\widetilde{\mathcal F}_P.
   $$

   To prove surjectivity, take $s\in\widetilde{\mathcal F}_P$, represented by some

   $$
   s'\in\widetilde{\mathcal F}(U).
   $$

   On an open neighbourhood $V\subseteq U$ of $P$, this section is represented by an element

   $$
   s''\in\mathcal F(V).
   $$

   The germ $s''_P\in\mathcal F_P$ is immediately a preimage of $s$.

   To prove injectivity, let $s,t\in\mathcal F_P$ have the same image in $\widetilde{\mathcal F}_P$. We may assume that $s$ and $t$ are represented by sections on the same open set, say $U$. Equality in the stalk of the sheafification means that there is an open neighbourhood $P\in V\subseteq U$ with

   $$
   (s_Q)_{Q\in V}=(t_Q)_{Q\in V}.
   $$

   In particular, the germs of the two sections at $P$ agree, so $s=t$ in $\mathcal F_P$.

3. Let

   $$
   U=\bigcup_{i\in I}U_i
   $$

   be an open cover, and let

   $$
   s,t\in\Gamma(U,\widetilde{\mathcal F})
   $$

   satisfy

   $$
   s|_{U_i}=t|_{U_i}
   $$

   for every $i$. Every point $P\in U$ belongs to some $U_i$, so

   $$
   s_P=t_P
   $$

   for every $P\in U$. Thus the two tuples in the product of stalks agree, and consequently $s=t$ in the sheafification.

   Now suppose sections

   $$
   s_i\in\widetilde{\mathcal F}(U_i)
   $$

   are given with

   $$
   s_i|_{U_i\cap U_j}=s_j|_{U_i\cap U_j}.
   $$

   For every $P\in U$, one of the $s_i$ with $P\in U_i$ determines a germ $s_P$. This germ is unique by compatibility on the intersections. The tuple

   $$
   (s_P)_{P\in U}
   $$

   immediately satisfies the compatibility condition in the definition of sheafification. Thus $\widetilde{\mathcal F}$ satisfies both sheaf conditions.

4. By part (1), there is a presheaf morphism

   $$
   \mathcal F\longrightarrow\widetilde{\mathcal F}.
   $$

   By part (2), this morphism is bijective on every stalk. The left-hand side is a sheaf by hypothesis, and the right-hand side is a sheaf by part (3). Lemma 4.6 shows that the morphism is an isomorphism.

5. See Exercise 5.2. $\square$

> **Editorial note - incorrect article in the source.** In item (4), the source prints *die natürliche Morphismus*. The correct German form is *der natürliche Morphismus*. The translation uses the intended mathematical expression, “natural morphism”. (The source heading typo *Garbenmorpismen* is also preserved in the Unit 4 authority notes; the term used here remains “sheaf morphism”.)

## Homomorphisms of sheaves of groups {#br-bgk-2019-l05-s02}

### Definition 5.3: homomorphism of sheaves of commutative groups {#br-bgk-2019-l05-def-02}

Let $X$ be a topological space, and let $\mathcal F$ and $\mathcal G$ be sheaves of commutative groups on $X$. A sheaf morphism

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

is called a *homomorphism of sheaves of commutative groups* if, for every open set $U\subseteq X$, the map

$$
\varphi_U:\mathcal F(U)\longrightarrow\mathcal G(U)
$$

is a group homomorphism.

### Example 5.4: homomorphisms induced by topological groups {#br-bgk-2019-l05-exa-01}

A continuous group homomorphism

$$
\varphi:F\longrightarrow G
$$

between topological groups $F$ and $G$ determines a homomorphism of sheaves of groups on every topological space $X$. On each open set $U$, it is given by

$$
\begin{aligned}
C^0(U,F)&\longrightarrow C^0(U,G),\\
f&\longmapsto\varphi\circ f.
\end{aligned}
$$

> **Scope note.** Definition 5.3 is phrased for sheaves of commutative groups, whereas this source example uses general topological groups. The composition construction above does not require commutativity; this edition therefore calls it a homomorphism of sheaves of groups in the general sense.

### Definition 5.5: kernel sheaf {#br-bgk-2019-l05-def-03}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. The subsheaf of $\mathcal F$ defined by

$$
(\ker\varphi)(U):=\ker\varphi_U
$$

is called the *kernel sheaf* of $\varphi$.

More precisely, it is a subsheaf of commutative groups: for every open set $U$, its value is a subgroup of $\mathcal F(U)$; see Exercise 5.6.

### Definition 5.6: image sheaf {#br-bgk-2019-l05-def-04}

Let $X$ be a topological space and

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

a homomorphism of sheaves of commutative groups. The sheafification of the presheaf given by

$$
(\operatorname{im}\varphi)(U):=\operatorname{im}\varphi_U
$$

is called the *image sheaf* of $\varphi$.

By Lemma 5.2(5), the image sheaf is naturally a subsheaf of $\mathcal G$, and more precisely a subsheaf of commutative groups. It is denoted by $\operatorname{im}\varphi$.

### Example 5.7: homomorphisms of trivial vector bundles {#br-bgk-2019-l05-exa-02}

Let $X$ be a topological space and

$$
\varphi:X\times\mathbb R^n\longrightarrow X\times\mathbb R^m
$$

a homomorphism between trivial vector bundles. This homomorphism is described by a continuous map

$$
M:X\longrightarrow
\operatorname{Mat}_{m\times n}\bigl(C^0(X,\mathbb R)\bigr),
$$

that is, a matrix is assigned continuously to each point, describing at that point a linear map $\mathbb R^n\to\mathbb R^m$. This can immediately be viewed as a homomorphism of sheaves of groups on $X$:

$$
\begin{aligned}
C^0(-,\mathbb R)^n&\longrightarrow C^0(-,\mathbb R)^m,\\
\begin{pmatrix}
f_1\\
\vdots\\
f_n
\end{pmatrix}
&\longmapsto
M
\begin{pmatrix}
f_1\\
\vdots\\
f_n
\end{pmatrix}.
\end{aligned}
$$

This map is the sheaf morphism at the level of sections of the bundles.

In Example 1.2, for $X=\mathbb R^3$, we have the map

$$
\begin{aligned}
\varphi:\mathbb R^3\times\mathbb R^3
&\longrightarrow\mathbb R^3\times\mathbb R,\\
(r,s,t;u,v,w)&\longmapsto(r,s,t;ru+sv+tw),
\end{aligned}
$$

or, equivalently,

$$
\begin{aligned}
M:\mathbb R^3&\longrightarrow
\operatorname{Mat}_{1\times3}(K),\\
(r,s,t)&\longmapsto(r,s,t).
\end{aligned}
$$

> **Editorial note - two type mismatches in the source matrix notation.** The source writes $M:X\to\operatorname{Mat}_{m\times n}(C^0(X,\mathbb R))$, whereas the following description treats $M$ as a pointwise matrix-valued function. The usual correctly typed expression is $M:X\to\operatorname{Mat}_{m\times n}(\mathbb R)$, or equivalently $M\in\operatorname{Mat}_{m\times n}(C^0(X,\mathbb R))$. In the concrete real example, the source also writes $\operatorname{Mat}_{1\times3}(K)$, although $K$ is undefined and the context uses $\mathbb R$. Both source formulae are retained above so that these discrepancies remain visible.

The kernel sheaf over $U$ is

$$
\begin{aligned}
(\ker\varphi)(U)
&=
\left\{
\begin{pmatrix}
f_1\\
\vdots\\
f_n
\end{pmatrix}
\in C^0(U,\mathbb R)^n
\ \middle|\
M
\begin{pmatrix}
f_1\\
\vdots\\
f_n
\end{pmatrix}
=0
\right\}\\
&\subseteq C^0(U,\mathbb R)^n.
\end{aligned}
$$

## The quotient sheaf {#br-bgk-2019-l05-s03}

### Definition 5.8: quotient sheaf {#br-bgk-2019-l05-def-05}

Let $\mathcal G$ be a sheaf of commutative groups and

$$
\mathcal F\subseteq\mathcal G
$$

a subsheaf of groups. The sheafification of the presheaf

$$
U\longmapsto\mathcal G(U)/\mathcal F(U)
$$

is called the *quotient sheaf* of $\mathcal G$ by $\mathcal F$.

The quotient sheaf is denoted by $\mathcal G/\mathcal F$. Because its construction uses sheafification, the equality

$$
(\mathcal G/\mathcal F)(U)
=
\mathcal G(U)/\mathcal F(U).
$$

need not hold in general. However, for every point $P\in X$,

$$
(\mathcal G/\mathcal F)_P
=
\mathcal G_P/\mathcal F_P;
$$

see Exercise 5.11.

### Lemma 5.9: an explicit description of the quotient sheaf {#br-bgk-2019-l05-lem-02}

Let $\mathcal G$ be a sheaf of commutative groups and

$$
\mathcal F\subseteq\mathcal G
$$

a subsheaf of groups, with quotient sheaf $\mathcal G/\mathcal F$. The following statements hold.

1. Every element

   $$
   s\in\Gamma(X,\mathcal G/\mathcal F)
   $$

   is represented by a family

   $$
   (U_i,g_i)_{i\in I},
   $$

   where

   $$
   X=\bigcup_{i\in I}U_i
   $$

   is an open cover and the sections

   $$
   g_i\in\Gamma(U_i,\mathcal G)
   $$

   satisfy

   $$
   g_i|_{U_i\cap U_j}-g_j|_{U_i\cap U_j}
   \in\Gamma(U_i\cap U_j,\mathcal F)
   $$

   for all $i,j\in I$.

   Every such family determines an element of $\Gamma(X,\mathcal G/\mathcal F)$.

2. Two families

   $$
   (U_i,g_i)_{i\in I}
   \qquad\text{and}\qquad
   (U_i,h_i)_{i\in I}
   $$

   on the same open cover determine the same element of

   $$
   \Gamma(X,\mathcal G/\mathcal F)
   $$

   precisely when

   $$
   g_i-h_i\in\Gamma(U_i,\mathcal F)
   $$

   for every $i$.

3. Two families

   $$
   (U_i,g_i)_{i\in I}
   \qquad\text{and}\qquad
   (V_j,h_j)_{j\in J}
   $$

   determine the same element precisely when, on some—and hence every—common refinement of the two covers, the differences of their sections belong to $\mathcal F$.

#### Proof {#br-bgk-2019-l05-lem-02-proof}

1. The canonical sheaf homomorphism

   $$
   \mathcal G\longrightarrow\mathcal G/\mathcal F
   $$

   is surjective. Therefore every section

   $$
   s\in\Gamma(X,\mathcal G/\mathcal F)
   $$

   has local preimages. Thus there are an open cover

   $$
   X=\bigcup_{i\in I}U_i
   $$

   and elements

   $$
   g_i\in\Gamma(U_i,\mathcal G)
   $$

   mapping to $s|_{U_i}$. Hence

   $$
   g_i|_{U_i\cap U_j}-g_j|_{U_i\cap U_j}
   \in\Gamma(U_i\cap U_j,\mathcal G)
   $$

   maps to zero, so this difference belongs to the kernel, namely $\mathcal F$.

   Conversely, a family satisfying this condition determines classes

   $$
   [g_i]\in\Gamma(U_i,\mathcal G/\mathcal F).
   $$

   On every intersection we have

   $$
   \begin{aligned}
   [g_i]|_{U_i\cap U_j}-[g_j]|_{U_i\cap U_j}
   &=
   [g_i|_{U_i\cap U_j}-g_j|_{U_i\cap U_j}]\\
   &=0.
   \end{aligned}
   $$

   Thus the classes are compatible and determine a global section of the quotient sheaf.

2. Replacing the two families by their difference, it suffices to consider the case $h_i=0$. We must show that $(U_i,g_i)$ determines the zero element in the quotient sheaf precisely when every

   $$
   g_i\in\Gamma(U_i,\mathcal F).
   $$

   If the family determines the zero element, its image in every stalk is also zero. Thus, for every $P\in U_i$, its germ satisfies

   $$
   (g_i)_P\in\mathcal F_P.
   $$

   Membership in a subsheaf can be tested on stalks, so

   $$
   g_i\in\Gamma(U_i,\mathcal F).
   $$

   The converse is immediate.

3. Equality of sections of a sheaf can be tested locally on any open cover. The statement follows from part (2) and the fact that membership in a subsheaf can also be tested locally. $\square$

> **Editorial note - sections and germs in the source proof.** In item (2), the source writes $g_i\in\mathcal F_P$, although $g_i$ is a section on $U_i$ and $\mathcal F_P$ is a stalk. The correctly typed statement used above is $(g_i)_P\in\mathcal F_P$.
