---
title: "Lecture 28 - Morphisms to projective space"
stable_id: br-bgk-2019-l28
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 28"
upstream_pageid: 109032
upstream_revid: 793621
upstream_timestamp: "2022-08-25T06:24:58Z"
upstream_mediawiki_sha1: e7e7f2f42fcdd2f5fe1f284396867bf05a9ab815
source_url: "https://de.wikiversity.org/w/index.php?oldid=793621"
authority_manifest: authority/wikiversity-bgk/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 1ab20936afe74fcfdde3318452f2211f2458911ff0a77c554fba894de49f4b9f
lecture_xml: authority/wikiversity-bgk/unit-28/lecture-28.xml
lecture_xml_sha256: f29af0601c37c1c8d49489080a8d7b274bf530905dfd7ea680d9fecd11d73f0b
lecture_expanded_tex: authority/wikiversity-bgk/unit-28/lecture-28-expanded.tex
lecture_expanded_tex_sha256: 85df8cce341d0d4fe6d95086d52e1954ce90415f5eb556669f466f77457f6814
official_pdf: authority/artifacts/bgk-lecture-28-official.pdf
official_pdf_sha256: f38e9f12ad1d5a6d715389f28e942b2e6ae93c2f336a8e97a9b1795cbafb392f
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-28.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 28: Morphisms to projective space {#br-bgk-2019-l28}

By definition, a projective variety $X$ over a field $K$ can be realised as a closed subvariety $X\subseteq\mathbb P^n_K$. Two competing viewpoints arise here.

On the one hand, realising $X$ as part of a projective space lets us use concepts, structures, and properties of the ambient space by restricting them to $X$. We can investigate how $X$ intersects other subvarieties $Y$, look for relationships with the open complement $\mathbb P^n_K\setminus X$, and visualise $X$ inside an ambient space. This is the *extrinsic* viewpoint.

On the other hand, we can ask which properties belong to the variety $X$ itself, independently of a particular realisation. This is the *intrinsic* viewpoint. Typically, $X$ is isomorphic to an “other” variety $X'$ given as a closed subset $X'\subseteq\mathbb P^{n'}_K$. Which properties of $X$ and $X'$ are independent of their respective embeddings?

The two viewpoints meet in the following questions. How many embeddings does a given $X$ have? Can one understand all embeddings of $X$ into projective space at once? Is there a best embedding, for example into an ambient space of small dimension or with a particularly transparent relationship to it? Is there a natural embedding related to characteristic objects on $X$?

For example, consider the closed projective curve

$$
C=V_+(Y^2-XZ)\subseteq\mathbb P^2_K.
$$

This curve has degree $2$, and its intersection with any line consists of two points, counted with multiplicities. The map

$$
\mathbb P^1_K\longrightarrow\mathbb P^2_K,
\qquad (s,t)\longmapsto(s^2,st,t^2),
$$

induces an isomorphism $\mathbb P^1_K\to C\subseteq\mathbb P^2_K$. Thus $C$ is isomorphic to the projective line and can be regarded as an “unnecessarily curved” version of it. Curves of degree two—quadrics or conic sections—are nevertheless natural objects in the plane. From the projective line's viewpoint, the elements $s^2,st,t^2$ form a basis of the second homogeneous component $K[s,t]_2$ of the homogeneous coordinate ring $K[s,t]$. These elements also occur as global sections of the invertible sheaf $\mathcal O_{\mathbb P^1_K}(2)$. We will see that different embeddings of $X$ into projective space are related to global sections of invertible sheaves on $X$.

## Invertible sheaves and morphisms to projective space {#br-bgk-2019-l28-s01}

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Fakt -->
### Lemma 28.1 {#br-bgk-2019-l28-lem-01}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, and let

$$
s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L).
$$

If $U\subseteq X$ is the union of the open sets $X_{s_i}$, then

$$
U\longrightarrow\mathbb P^n_R,
\qquad x\longmapsto(s_0(x),s_1(x),\ldots,s_n(x))
$$

is a morphism.

#### Proof {#br-bgk-2019-l28-lem-01-proof}

First consider the situation on $X_i=X_{s_i}$. By Lemma 13.22,

$$
\mathcal O_X|_{X_i}\longrightarrow\mathcal L|_{X_i},
\qquad 1\longmapsto s_i,
$$

is an isomorphism of $\mathcal O_X$-modules. Under this isomorphism, the section $s_k$ corresponds to a function

$$
f_{ki}\in\Gamma(X_i,\mathcal O_X),
\qquad f_{ki}=\frac{s_k}{s_i}.
$$

This quotient is well-defined. By Corollary 10.13, the functions $f_{ki}$, for $k\ne i$, define a morphism

$$
\varphi_i:X_i\longrightarrow D_+(x_i)\cong\mathbb A^n_R
\subseteq\mathbb P^n_R.
$$

Altogether we have a commutative diagram

$$
\begin{CD}
X_i @>{\varphi_i}>> D_+(x_i)\cong\mathbb A^n_R\subseteq\mathbb P^n_R\\
@AAA @AAA\\
X_i\cap X_j @>>> D_+(x_i)\cap D_+(x_j)\\
@VVV @VVV\\
X_j @>{\varphi_j}>> D_+(x_j)\cong\mathbb A^n_R\subseteq\mathbb P^n_R.
\end{CD}
$$

On $X_i\cap X_j$, these two morphisms correspond to the same gluing as on the intersection $D_+(x_i)\cap D_+(x_j)$ in projective space. They therefore glue to a single morphism on the union of all $X_i$. $\square$

> **Edition note (source).** The source restricts the trivialisation and the functions $f_{ki}$ to $U$ in the middle of an argument taking place on $X_i$, and then writes $\mathbb P^n_K$ at a corner of the diagram although the base is $\operatorname{Spec}(R)$. This edition consistently displays $X_i$ and $\mathbb P^n_R$; the mathematical content of the argument is unchanged.

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Zugehöriger Morphismus/Definition -->
### Definition 28.2: the morphism defined by sections {#br-bgk-2019-l28-def-02}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, and let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections. The morphism of Lemma 28.1 defined on

$$
U=\bigcup_{i=0}^{n}X_{s_i},
$$

namely

$$
U\longrightarrow\mathbb P^n_R,
\qquad x\longmapsto(s_0(x),s_1(x),\ldots,s_n(x)),
$$

is called the *morphism defined by the sections* $s_0,\ldots,s_n$, or the *morphism defined by the linear system* $s_0,\ldots,s_n$. It is denoted by $\varphi_{s_0,\ldots,s_n}$ or $\varphi_{\mathcal L;s_0,\ldots,s_n}$.

<!-- upstream_entity: Schema/Invertierbare Garbe/Lineares System/Definition -->
### Definition 28.3: a linear system {#br-bgk-2019-l28-def-03}

Let $X$ be a scheme over a commutative ring $R$ and let $\mathcal L$ be an invertible sheaf on $X$. An $R$-submodule

$$
T\subseteq\Gamma(X,\mathcal L)
$$

is called a *linear system* on $X$.

By Exercise 28.9, the morphism defined by a family of sections depends primarily on the submodule they generate. This is particularly clear when the sections are linearly independent, as is often required. If $T=\Gamma(X,\mathcal L)$, we speak of a *complete linear system*.

A linear system has a geometric meaning. Each section $s\in T$ determines its invertibility locus $X_s$ and its zero locus

$$
Z(s):=X\setminus X_s.
$$

If $X$ is integral, a nonzero section $s$ defines an effective Cartier divisor. When its support is nonempty and $X$ is locally Noetherian, $Z(s)$ has pure codimension $1$ and is therefore a hypersurface in $X$; a nowhere-vanishing section instead has $Z(s)=\varnothing$. Thus the sets $Z(s)$ for $s\in T$, $s\ne0$, form a family of zero loci—often hypersurfaces—associated with the linear system; this family itself is also often called the linear system. If $X$ is normal, the nonempty $Z(s)$ can be viewed as a family of linearly equivalent divisors.

> **Edition note (source).** The source calls $Z(s)$ a codimension-one hypersurface for every nonzero section, while only informally suggesting that $X$ be integral. A nonzero section can be nowhere vanishing, in which case $Z(s)$ is empty; the codimension-one assertion above therefore includes the necessary nonemptiness and local Noetherian hypotheses.

<!-- upstream_entity: Projektive Gerade/O(1)/Variablen/Zugehöriger voller Morphismus/Beispiel -->
### Example 28.4 {#br-bgk-2019-l28-exa-04}

On the projective line

$$
\mathbb P^1_R=\operatorname{Proj}(R[X,Y])
$$

over a commutative ring $R$, the morphism associated with the complete linear system

$$
(X,Y)\subseteq\Gamma(\mathbb P^1_R,\mathcal O_{\mathbb P^1_R}(1))
$$

is the identity.

<!-- upstream_entity: Projektive Gerade/O(2)/Variablen/Zugehöriger voller Morphismus/Beispiel -->
### Example 28.5 {#br-bgk-2019-l28-exa-05}

On $\mathbb P^1_R=\operatorname{Proj}(R[X,Y])$ over a commutative ring $R$, the complete linear system

$$
(X^2,XY,Y^2)\subseteq
\Gamma(\mathbb P^1_R,\mathcal O_{\mathbb P^1_R}(2))
$$

gives the morphism

$$
\mathbb P^1_R\longrightarrow\mathbb P^2_R,
\qquad (x,y)\longmapsto(x^2,xy,y^2).
$$

The point with homogeneous coordinates $(x,y)$ maps to the point with homogeneous coordinates $(x^2,xy,y^2)=(u,v,w)$. Its image satisfies $uw=v^2$ and thus lies on the plane curve

$$
V_+(uw-v^2)\subseteq\mathbb P^2_R.
$$

In fact, there is an isomorphism $\mathbb P^1_R\cong V_+(uw-v^2)$.

<!-- upstream_entity: Schema/Invertierbare Garbe/Lineares System/Basispunktfrei/Definition -->
### Definition 28.6: base-point-free {#br-bgk-2019-l28-def-06}

Let $X$ be a scheme over a commutative ring $R$ and let $\mathcal L$ be an invertible sheaf on $X$. A linear system $T\subseteq\Gamma(X,\mathcal L)$ is called *base-point-free* if for every $x\in X$ there is an $s\in T$ such that $x\in X_s$.

This term is mainly used for schemes over a field. We also say that sections $s_0,s_1,\ldots,s_n$ are base-point-free if the linear system they generate is base-point-free.

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Global definiert/Fakt -->
### Lemma 28.7 {#br-bgk-2019-l28-lem-07}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, and let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections. The following statements are equivalent.

1. $X=\bigcup_{i=0}^{n}X_{s_i}$.
2. The morphism to $\mathbb P^n_R$ defined by the linear system $(s_0,s_1,\ldots,s_n)$ is defined on all of $X$.
3. The linear system $(s_0,s_1,\ldots,s_n)$ is base-point-free.

#### Proof {#br-bgk-2019-l28-lem-07-proof}

See Exercise 28.14. $\square$

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Korrespondenz/Fakt -->
### Theorem 28.8 {#br-bgk-2019-l28-thm-08}

Let $X$ be a scheme over a commutative ring $R$. The following concepts correspond to one another.

1. An invertible sheaf $\mathcal L$ on $X$ together with base-point-free sections
   $$
   s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L).
   $$
2. A morphism
   $$
   \varphi:X\longrightarrow\mathbb P^n_R
   $$
   over $\operatorname{Spec}(R)$.

The sections in (1) are assigned the morphism $\varphi_{s_0,s_1,\ldots,s_n}$. Conversely, the morphism $\varphi$ in (2) is assigned the invertible sheaf $\varphi^*(\mathcal O_{\mathbb P^n_R}(1))$ together with the sections $\varphi^*(x_i)$, $i=0,1,\ldots,n$.

#### Proof {#br-bgk-2019-l28-thm-08-proof}

First suppose that $\mathcal L$ and the sections $s_0,\ldots,s_n$ are given. We must show

$$
\varphi^*\mathcal O_{\mathbb P^n_R}(1)\cong\mathcal L.
$$

On projective space there are $\mathcal O_{\mathbb P^n_R}$-module homomorphisms

$$
\Psi_i:\mathcal O_{\mathbb P^n_R}
\longrightarrow\mathcal O_{\mathbb P^n_R}(1),
\qquad 1\longmapsto x_i,
$$

which become isomorphisms when restricted to $D_+(x_i)$. Pullback gives homomorphisms

$$
\mathcal O_X\longrightarrow
\varphi^*\mathcal O_{\mathbb P^n_R}(1),
\qquad 1\longmapsto\varphi^*(x_i),
$$

and isomorphisms on $X_{s_i}$. Combined with the isomorphism

$$
\mathcal O_X|_{X_{s_i}}\longrightarrow\mathcal L|_{X_{s_i}},
\qquad 1\longmapsto s_i,
$$

we obtain local isomorphisms

$$
\varphi^*\mathcal O_{\mathbb P^n_R}(1)|_{X_{s_i}}
\longrightarrow\mathcal L|_{X_{s_i}}
$$

which identify $\varphi^*(x_i)$ with $s_i$. Their restrictions to $X_{s_i s_j}$ agree. By Corollary 4.10, they therefore glue to a global isomorphism

$$
\varphi^*\mathcal O_{\mathbb P^n_R}(1)\longrightarrow\mathcal L.
$$

Conversely, suppose $\varphi:X\to\mathbb P^n_R$ is given. This morphism determines sections $s_i=\varphi^*(x_i)$, which in turn determine a morphism $\varphi'$. Since a morphism is determined locally, it suffices to compare them on

$$
\varphi^{-1}(D_+(x_i))\longrightarrow D_+(x_i)\cong\mathbb A^n_R.
$$

Here the variables $x_k/x_i$ pull back to $s_k/s_i$, exactly as in the definition of $\varphi'$. Thus $\varphi'=\varphi$. $\square$

> **Edition note (source).** Although Theorem 28.8 is stated over a commutative ring $R$ with target $\mathbb P^n_R$, the converse direction of the source proof switches to $\mathbb P^n_K$ and $\mathbb A^n_K$ without introducing $K$. Both occurrences have been corrected to the stated base $R$ above; this is a notation repair, not a new generalisation or restriction.

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Hyperebene/Urbild/Fakt -->
### Lemma 28.9 {#br-bgk-2019-l28-lem-09}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections, and let $\varphi:X\to\mathbb P^n_R$ be the associated morphism. The inverse image of the zero locus

$$
V_+(a_0X_0+a_1X_1+\cdots+a_nX_n)\subseteq\mathbb P^n_R,
$$

with $a_i\in R$ is the zero locus of the pulled-back section,

$$
Z(a_0s_0+a_1s_1+\cdots+a_ns_n)
=X\setminus X_{a_0s_0+a_1s_1+\cdots+a_ns_n}.
$$

#### Proof {#br-bgk-2019-l28-lem-09-proof}

This follows from Appendix Lemma 4.3. If $(a_0,\ldots,a_n)=R$, the displayed zero locus is a relative hyperplane. Over a field, this condition is equivalent to the coefficients not all being zero. $\square$

The twisted structure sheaf $\mathcal O_{\mathbb P^n_R}(1)$, through the global sections whose coefficient tuples generate the unit ideal, determines the family of relative hyperplanes in projective space. Over a field, these are precisely its nonzero global sections. Similarly, an invertible sheaf on a scheme determines the family of zero loci of its nonzero global sections. Under the correspondence of Theorem 28.8, inverse images of relative hyperplanes agree with the corresponding zero loci. If $\varphi$ factors through a closed subvariety, that is, if there is a map

$$
X\longrightarrow Y\subseteq\mathbb P^n_R,
$$

then these corresponding zero loci are also inverse images of intersections $Y\cap H$ with a relative hyperplane $H$. In Example 28.5, for instance, the zero loci arising from unimodular linear combinations in the complete linear system on $\mathcal O_{\mathbb P^1_R}(2)$ agree with the intersections $V_+(uw-v^2)\cap H$, where $H$ is a relative line.

> **Edition note (source).** Over an arbitrary commutative ring, the source calls the zero locus of every nonzero linear form a hyperplane. Such a form defines a relative hyperplane only when its coefficients generate the unit ideal; the distinction disappears over a field. The inverse-image identity itself remains valid for every coefficient tuple.

## Very ample sheaves {#br-bgk-2019-l28-s02}

<!-- upstream_entity: Schema/R/Invertierbare Garbe/Sehr ampel/Einbettung/Definition -->
### Definition 28.10: very ample {#br-bgk-2019-l28-def-10}

Let $X$ be a scheme over a commutative ring $R$ and let $\mathcal L$ be an invertible sheaf on $X$. The sheaf $\mathcal L$ is called *very ample* if there is an embedding $\varphi:X\to\mathbb P^n_R$, for some $n$, such that

$$
\varphi^*(\mathcal O_{\mathbb P^n_R}(1))\cong\mathcal L.
$$

<!-- upstream_entity: Schema/R/Invertierbare Garbe/Sehr ampel/Schnitte/Fakt -->
### Lemma 28.11 {#br-bgk-2019-l28-lem-11}

Let $X$ be a scheme over a commutative ring $R$ and let $\mathcal L$ be an invertible sheaf on $X$. The sheaf $\mathcal L$ is very ample precisely when there are base-point-free global sections

$$
s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)
$$

such that the associated morphism $\varphi_{s_0,s_1,\ldots,s_n}$ is an embedding.

#### Proof {#br-bgk-2019-l28-lem-11-proof}

This follows from Theorem 28.8. $\square$

<!-- upstream_entity: Projektiver Raum/O(n)/Sehr ampel/Beispiel -->
### Example 28.12 {#br-bgk-2019-l28-exa-12}

On projective space $\mathbb P^n_R$ over a commutative ring $R$, the invertible sheaf $\mathcal O_{\mathbb P^n_R}(k)$ is very ample for every $k\ge1$. We have

$$
\Gamma(\mathbb P^n_R,\mathcal O_{\mathbb P^n_R}(k))
=R[X_0,X_1,\ldots,X_n]_k.
$$

Consider the linear system generated by all monomials of degree $k$ in the $n+1$ variables of $R[X_0,X_1,\ldots,X_n]$, and its associated morphism

$$
\varphi:\mathbb P^n_R\longrightarrow\mathbb P^m_R,
$$

where $m$ is one less than the number of these monomials. On $D_+(X_0)=(\mathbb P^n_R)_{X_0^k}$, this map is given by

$$
\mathbb A^n_R\longrightarrow D_+(Y_\nu)\subseteq\mathbb P^m_R,
\qquad
\left(\frac{X_1}{X_0},\ldots,\frac{X_n}{X_0}\right)
\longmapsto
\left(\frac{X^\mu}{X_0^k}
:\mu\text{ monomial of degree }k\right),
$$

and analogously on each $D_+(X_i)$. At the level of polynomial rings, this is the substitution homomorphism

$$
R[S_\mu:\mu\in I_k]\longrightarrow R[T_1,\ldots,T_n],
\qquad S_\mu\longmapsto T^\mu,
$$

where $I_k$ is the index set of all monomials in $n$ variables of degree at most $k$ (note the inequality). This map is surjective, so the morphism above is a closed embedding.

For $k\le0$ and $n\ge1$, the sheaf $\mathcal O_{\mathbb P^n_R}(k)$ is not very ample.

<!-- upstream_entity: Invertierbare Garbe/Ampel/Potenz/Definition -->
### Definition 28.13: ample {#br-bgk-2019-l28-def-13}

Let $X$ be a scheme over a commutative ring $R$ and let $\mathcal L$ be an invertible sheaf on $X$. The sheaf $\mathcal L$ is called *ample* if $\mathcal L^n$ is very ample for some $n\ge1$.
