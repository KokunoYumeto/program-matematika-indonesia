---
title: "Lecture 17 - Geometric Vector Bundles"
stable_id: br-bgk-2019-l17
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 17"
upstream_pageid: 109021
upstream_revid: 1019984
upstream_timestamp: "2025-08-09T13:37:26Z"
upstream_mediawiki_sha1: b4e1dbede8d862ac8bd1b25d94157448625ff938
source_url: "https://de.wikiversity.org/w/index.php?oldid=1019984"
authority_manifest: authority/wikiversity-bgk/unit-17/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b896a47254cbbea5f77f5eecaa1f8db99fe24c662fc9ba56e10f9db1be186b99
authority_manifest_status: "Complete terminal authority freeze; all 31 file records have been recomputed without mismatches."
lecture_xml: authority/wikiversity-bgk/unit-17/lecture-17.xml
lecture_xml_sha256: 91665b82598c78819adc45fbec423266a7fb9bd89ec59eb5cb269d24fb35fa74
lecture_expanded_tex: authority/wikiversity-bgk/unit-17/lecture-17-expanded.tex
lecture_expanded_tex_sha256: 38a95b240a54ec4f26529e06d774fdc3196e3f0d73431e94bea06b4465919d42
official_pdf: authority/artifacts/bgk-lecture-17-official.pdf
official_pdf_sha256: d451a9af49bf0734c3d212a5b07e7152b9b6c067d6b87fe9c9cd3923f7cb4a3b
official_pdf_status: "Local official PDF witness; 96,487 bytes, 9 pages, and upload SHA-1 583a63cef01d8c7ef948f3b69ed860f31de8b6ac have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-17/official-pdfs-api.json
official_pdf_source_bytes: 96487
official_pdf_source_sha1: 583a63cef01d8c7ef948f3b69ed860f31de8b6ac
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
media_credits: source/id-ID/media-credits-bgk-unit-17.md
rights_ledger: authority/RIGHTS-bgk-unit-17.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-17.json
asset_closure_sha256: 1173bbfd2583a146d58bee689a94fdaa143b543da0b3f4dbc89fe869d57037cb
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 17: Geometric Vector Bundles {#br-bgk-2019-l17}

## Geometric vector bundles {#br-bgk-2019-l17-s01}

For an affine scheme

$$
U=\operatorname{Spek}(R),
$$

the scheme

$$
\mathbb A_U^r:=\operatorname{Spek}(R[T_1,\ldots,T_r])
$$

together with its natural projection to $\operatorname{Spek}(R)$, namely the spectrum map arising from

$$
R\longrightarrow R[T_1,\ldots,T_r],
$$

is called the *trivial bundle of rank $r$ over $U$*. For a point $P\in\operatorname{Spek}(R)$ corresponding to the ring homomorphism

$$
R\longrightarrow\kappa(P),
$$

the fibre of $\mathbb A_U^r$ over $P$ is $\mathbb A_{\kappa(P)}^r$, that is, affine space of dimension $r$ over the residue field $\kappa(P)$.

For an arbitrary scheme $X$ with an affine cover

$$
X=\bigcup_{i\in I}U_i,
$$

we define $\mathbb A_X^r$ by gluing the $\mathbb A_{U_i}^r$ as prescribed by the gluing of the $U_i$ inside $X$, in the sense of Lemma 7.10. This trivial bundle of rank $r$ comes with a projection

$$
\mathbb A_X^r\longrightarrow X.
$$

It is also called the *affine cylinder of rank $r$ over $X$* and is written $X\times\mathbb A^r$. These trivial bundles are the local building blocks for the concept of a geometric vector bundle over a scheme.

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Als Schema/Definition -->

### Definition 17.1: geometric vector bundles {#br-bgk-2019-l17-def-01}

Let $X$ be a scheme. A scheme $V$ together with a morphism

$$
p:V\longrightarrow X
$$

is called a *geometric vector bundle of rank $r$ over $X$* if there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

and $U_i$-isomorphisms

$$
\psi_i:U_i\times\mathbb A^r=\mathbb A_{U_i}^r
\longrightarrow V|_{U_i}=p^{-1}(U_i)
$$

such that, for every affine open subset $U\subseteq U_i\cap U_j$, the transition maps

$$
\psi_j^{-1}\circ\psi_i:
\mathbb A_{U_i}^r|_U\longrightarrow\mathbb A_{U_j}^r|_U
$$

are linear automorphisms. At the ring level, this means that they are induced by automorphisms of the polynomial ring $\Gamma(U,\mathcal O_X)[T_1,\ldots,T_r]$ of the form

$$
T_i\longmapsto\sum_{j=1}^r a_{ij}T_j.
$$

The maps $\psi_i$ are called *trivialisations* of the vector bundle.

The following example continues Example 14.6.

<!-- upstream_entity: Ganzheitsring/Wurzel -5/Standardideal/Geometrisches Geradenbündel/Beispiel -->

### Example 17.2: a line bundle from the standard ideal {#br-bgk-2019-l17-exm-01}

Consider the quadratic number ring

$$
R=\mathbb Z[\sqrt{-5}],
$$

in which the equality

$$
2\cdot3=6=(1+\sqrt5\,i)(1-\sqrt5\,i),
$$

holds, and the $R$-algebra

$$
A=R[X,Y]/(3X-(1-i\sqrt5)Y)
$$

with its associated spectrum map $\operatorname{Spek}(A)\to\operatorname{Spek}(R)$. We claim that this is a geometric line bundle. To see this, use the open cover

$$
\operatorname{Spek}(R)=D(2)\cup D(3).
$$

We have

$$
A_2=R_2[X,Y]/(3X-(1-i\sqrt5)Y)\cong R_2[S]
$$

with $X\mapsto2S$ and $Y\mapsto(1+i\sqrt5)S$. Indeed, $S=X/2$, hence $X=2S$, and

$$
Y=\frac{3}{1-i\sqrt5}X
=\frac{1+i\sqrt5}{2}X
=(1+i\sqrt5)S.
$$

Similarly,

$$
A_3=R_3[X,Y]/(3X-(1-i\sqrt5)Y)\cong R_3[T]
$$

with $X\mapsto(1-i\sqrt5)T$ and $Y\mapsto3T$. Indeed, $T=Y/3$, hence $Y=3T$ and

$$
X=\frac{1-i\sqrt5}{3}Y=(1-i\sqrt5)T.
$$

On $D(6)=D(2)\cap D(3)$, the transition map is given by

$$
S=\frac X2=\frac{1-i\sqrt5}{2}T,
$$

and is therefore linear.

> **Editorial note — two source defects in this example.** The source prints the malformed factor ${1-i\sqrt5|}$; the displayed substitution $Y=3T$ gives $(1-i\sqrt5)$, used above. More substantially, the algebra $A$ as stated is not a line bundle over all of $\operatorname{Spek}(R)$. At the maximal ideal $\mathfrak p=(3,1-\sqrt{-5})$, both coefficients of its defining relation vanish, so its fibre is $\operatorname{Spek}(\mathbb F_3[X,Y])$, an affine plane. This point lies in $D(2)$, and the claimed isomorphism $A_2\cong R_2[S]$ therefore fails. The source construction is retained here with this warning; no replacement algebra is attributed to the author.

<!-- upstream_entity: Affiner Raum/Punktiert/Syzygienbündel/Beispiel -->

### Example 17.3: a syzygy bundle on punctured affine space {#br-bgk-2019-l17-exm-02}

Consider the ring homomorphism

$$
K[X,Y,Z]\longrightarrow
K[X,Y,Z][U,V,W]/(XU+YV+ZW),
$$

the associated spectrum map

$$
\operatorname{Spek}
\bigl(K[X,Y,Z][U,V,W]/(XU+YV+ZW)\bigr)
\longrightarrow\mathbb A_K^3,
$$

and its restriction

$$
\begin{aligned}
\varphi:\quad
\operatorname{Spek}
\bigl(K[X,Y,Z][U,V,W]/(XU+YV+ZW)\bigr)
&\supseteq D(X)\cup D(Y)\cup D(Z)\\
&\longrightarrow
\mathbb A_K^3\setminus\{(0,0,0)\}
=D(X)\cup D(Y)\cup D(Z).
\end{aligned}
$$

The latter is a geometric vector bundle of rank $2$ over punctured affine space. Natural trivialisations are given on $D(X)$, $D(Y)$, and $D(Z)$; compare Example 1.2. For example,

$$
\bigl(K[X,Y,Z][U,V,W]/(XU+YV+ZW)\bigr)_X
\cong K[X,Y,Z]_X[V,W],
$$

because $U$ can be expressed as

$$
U=-\frac{YV+ZW}{X}.
$$

<!-- upstream_entity: Projektiver Raum/Getwistetes Geradenbündel/Geometrische Realisierung/Beispiel -->

### Example 17.4: geometric realisation of twisted line bundles {#br-bgk-2019-l17-exm-03}

Consider projective space

$$
\mathbb P_K^n=\operatorname{Proj}(K[X_0,X_1,\ldots,X_n])
$$

and the projective spectrum

$$
W_k=\operatorname{Proj}(K[X_0,X_1,\ldots,X_n,Y]),
$$

with $\deg(X_i)=1$ and $\deg(Y)=k$. By Theorem 12.11, the homogeneous inclusion

$$
K[X_0,X_1,\ldots,X_n]
\subset K[X_0,X_1,\ldots,X_n,Y]
$$

induces a scheme morphism

$$
p:W_k\supset D_+(X_0,X_1,\ldots,X_n)=V_k
\longrightarrow\mathbb P_K^n.
$$

Over $D_+(X_i)$, the map takes the form

$$
D_+(X_i)
\cong\operatorname{Spek}K\left[
\frac{X_j}{X_i},\ j\ne i,\ \frac{Y}{X_i^k}
\right]
\longrightarrow
D_+(X_i)
\cong\operatorname{Spek}K\left[
\frac{X_j}{X_i},\ j\ne i
\right],
$$

and is thus a trivial line bundle. For $D_+(X_i)$ and $D_+(X_j)$, the transition maps over

$$
\Gamma(D_+(X_iX_j),\mathcal O_{\mathbb P_K^n})
=K\left[
\frac{X_r}{X_i},\ r\ne i,
\frac{X_s}{X_j},\ s\ne j
\right]
$$

are given by

$$
\frac{Y}{X_i^k}
\longmapsto
\frac{Y}{X_j^k}\frac{X_j^k}{X_i^k}.
$$

These maps are linear, so we obtain a line bundle over projective space.

A geometric vector bundle has additional structures. First consider the case

$$
\mathbb A_{\operatorname{Spek}(R)}^r
=\operatorname{Spek}(R[T_1,\ldots,T_r])
\longrightarrow\operatorname{Spek}(R).
$$

The $R$-algebra homomorphism

$$
R[T_1,\ldots,T_r]\longrightarrow R,
\qquad T_i\longmapsto0,
$$

gives a spectrum map

$$
\operatorname{Spek}(R)
\longrightarrow\operatorname{Spek}(R[T_1,\ldots,T_r]),
$$

which is a closed embedding, called the *zero section*. The $R$-algebra homomorphism

$$
R[T_1,\ldots,T_r]
\longrightarrow R[S_1,\ldots,S_r,T_1,\ldots,T_r],
\qquad T_i\longmapsto S_i+T_i,
$$

gives a spectrum map

$$
\alpha:\mathbb A_R^{r+r}
\cong\mathbb A_R^r\times_{\operatorname{Spek}(R)}\mathbb A_R^r
\longrightarrow\mathbb A_R^r,
$$

called addition on the vector bundle. Furthermore, the $R$-algebra homomorphism

$$
R[T_1,\ldots,T_r]\longrightarrow R[Z,T_1,\ldots,T_r],
\qquad T_i\longmapsto ZT_i,
$$

gives a spectrum map

$$
\mathbb A_R^{r+1}
\cong\mathbb A_R^1\times_{\operatorname{Spek}(R)}\mathbb A_R^r
\longrightarrow\mathbb A_R^r,
$$

called scalar multiplication.

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Addition/Fakt -->

### Lemma 17.5: operations on geometric vector bundles {#br-bgk-2019-l17-lem-01}

A geometric vector bundle $p:V\to X$ over a scheme $X$ has a zero section

$$
X\longrightarrow V,
$$

an addition map

$$
V\times_XV\longrightarrow V,
$$

and a scalar multiplication

$$
\mathbb A_X^1\times_XV\longrightarrow V.
$$

#### Proof {#br-bgk-2019-l17-lem-01-proof}

On an affine subset $U=\operatorname{Spek}(R)\subseteq X$ with a trivialisation

$$
V|_U\cong\mathbb A_U^r
\cong\operatorname{Spek}(R[T_1,\ldots,T_r]),
$$

there is a zero section given by $T_i\mapsto0$. Since the transition maps are linear, on the intersection $U_i\cap U_j$ this section is independent of the chosen affine subset, and is therefore well-defined.

The existence of addition rests essentially on the fact that, for a linear $R$-algebra isomorphism

$$
\theta:R[T_1,\ldots,T_r]\longrightarrow R[U_1,\ldots,U_r],
$$

the diagram

$$
\begin{CD}
R[T_1,\ldots,T_r] @>{\alpha^*}>>
R[T_1,\ldots,T_r,S_1,\ldots,S_r]\\
@V{\theta}VV @VV{\theta\times\theta}V\\
R[U_1,\ldots,U_r] @>{\alpha^*}>>
R[U_1,\ldots,U_r,V_1,\ldots,V_r]
\end{CD}
$$

commutes. Scalar multiplication is obtained similarly.

## Vector bundle homomorphisms {#br-bgk-2019-l17-s02}

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Homomorphismus/Definition -->

### Definition 17.6: vector bundle homomorphisms {#br-bgk-2019-l17-def-02}

Let $V$ and $W$ be vector bundles over a scheme $X$. A *vector bundle homomorphism* $\varphi:V\to W$ is a scheme morphism from $V$ to $W$ over $X$ with the following property. For every point $P\in X$, there is an affine open neighbourhood $P\in U\subseteq X$ refining the given trivialising neighbourhoods of both bundles, that is, $U\subseteq U_i,U_j'$ for suitable $i,j$, such that the composite

$$
\mathbb A_U^r
\xrightarrow{\ \psi_i|_U\ }V|_U
\xrightarrow{\ \varphi|_U\ }W|_U
\xrightarrow{\ \theta_j^{-1}|_U\ }\mathbb A_U^s
$$

is given at the ring level by a linear substitution homomorphism.

In the following statement, the kernel means the inverse image of the zero section, hence the inverse image of the zero point in each fibre. For a vector bundle homomorphism, the fibre map over every point $P\in X$ is given by a matrix over its residue field $\kappa(P)$. However, affine spaces over this field contain points with very different residue fields, so concepts from linear algebra must be applied with some care.

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Homomorphismus/Surjektiv/Kern/Fakt -->

### Lemma 17.7: the kernel of a surjective homomorphism {#br-bgk-2019-l17-lem-02}

Let $V$ and $W$ be vector bundles over a scheme $X$, and let $\varphi:V\to W$ be a surjective vector bundle homomorphism. Then its pointwise kernel is a vector bundle over $X$.

#### Proof {#br-bgk-2019-l17-lem-02-proof}

See Exercise 17.18.

Without the surjectivity condition, the kernel of a vector bundle homomorphism need not be a vector bundle. In Example 17.3, the pointwise-defined kernel is a vector bundle only on the punctured spectrum; at the origin, the kernel degenerates to a three-dimensional vector space.

## Vector bundles and locally free sheaves {#br-bgk-2019-l17-s03}

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Schnitte/Definition -->

### Definition 17.8: the sheaf of sections {#br-bgk-2019-l17-def-03}

For a geometric vector bundle $p:V\to X$ on a scheme $X$, the sheaf $\mathcal F$ defined on an open subset $U\subseteq X$ by

$$
\Gamma(U,\mathcal F)
=\{s:U\to V|_U\text{ scheme morphism}\mid p\circ s=\operatorname{Id}_U\}
$$

is called the *sheaf of sections of $V$*.

<!-- upstream_entity: Schema/Geometrisches Vektorbündel/Schnitte/Lokal frei/Fakt -->

### Lemma 17.9: the sheaf of sections is locally free {#br-bgk-2019-l17-lem-03}

For a geometric vector bundle $p:V\to X$, the sheaf of sections $\mathcal F$ is a locally free sheaf.

#### Proof {#br-bgk-2019-l17-lem-03-proof}

The addition

$$
V\times_XV\longrightarrow V,
$$

gives, by Exercise 17.19, a well-defined addition on the sheaf of sections. By Exercise 17.11, this makes $\mathcal F$ a sheaf of commutative groups. Scalar multiplication

$$
\mathbb A_X^1\times_XV\longrightarrow V
$$

gives $\mathcal F$ an $\mathcal O_X$-module structure. For an open set $U\subseteq X$ with $V|_U\cong\mathbb A_U^r$, we have

$$
\mathcal F|_U\cong(\mathcal O_X|_U)^r,
$$

so $\mathcal F$ is locally free.

Geometric vector bundles and locally free sheaves are essentially equivalent objects.

<!-- upstream_entity: Schema/Lokal freie Garben und Vektorbündel/Äquivalenz/Fakt -->

### Theorem 17.10: the correspondence between vector bundles and locally free sheaves {#br-bgk-2019-l17-thm-01}

On a scheme, geometric vector bundles correspond to locally free sheaves. Moreover, vector bundle homomorphisms correspond to $\mathcal O_X$-module homomorphisms.

A geometric vector bundle $V$ over $X$ is assigned its sheaf of sections $\mathcal S_V$, which is locally free by Lemma 17.9. A vector bundle homomorphism $\varphi:V\to W$ is assigned the module homomorphism $\mathcal S_V\to\mathcal S_W$ sending a section $s:U\to V|_U$ to the section $\varphi\circ s:U\to W|_U$.

#### Proof {#br-bgk-2019-l17-thm-01-proof}

First we show that every locally free sheaf is isomorphic to the sheaf of sections of a vector bundle. A locally free sheaf $\mathcal F$ of rank $r$ is given by an open cover

$$
X=\bigcup_{i\in I}U_i,
$$

where the $U_i$ may be chosen affine, together with isomorphisms

$$
\varphi_i:\mathcal O_{U_i}^r\longrightarrow\mathcal F|_{U_i}.
$$

By Theorem 13.10, the composite

$$
\mathcal O_{U_i}^r|_{U_i\cap U_j}
=\mathcal O_{U_i\cap U_j}^r
\xrightarrow{\ \varphi_i|_{U_i\cap U_j}\ }
\mathcal F|_{U_i\cap U_j}
\xrightarrow{\ \varphi_j^{-1}|_{U_i\cap U_j}\ }
\mathcal O_{U_i\cap U_j}^r
=\mathcal O_{U_j}^r|_{U_i\cap U_j}
$$

is given by $e_k\mapsto f_k$ with

$$
f_k\in\Gamma(U_i\cap U_j,\mathcal O_{U_i\cap U_j}^r).
$$

Here $f_k=(f_{k\ell})_{1\leq\ell\leq r}$ with

$$
f_{k\ell}\in\Gamma(U_i\cap U_j,\mathcal O_X).
$$

The determinant of the matrix $(f_{k\ell})_{k\ell}$ is a unit in $\Gamma(U_i\cap U_j,\mathcal O_X)$. Via

$$
T_k\longmapsto\sum_{\ell=1}^r f_{k\ell}S_\ell,
$$

these data define a linear $\Gamma(U_i\cap U_j,\mathcal O_X)$-algebra isomorphism

$$
\Gamma(U_i\cap U_j,\mathcal O_X)[T_1,\ldots,T_r]
\longrightarrow
\Gamma(U_i\cap U_j,\mathcal O_X)[S_1,\ldots,S_r]
$$

and a scheme isomorphism

$$
\varphi_{ji}:\mathbb A_{U_i\cap U_j}^r
\longrightarrow\mathbb A_{U_i\cap U_j}^r,
$$

of the form required in the definition of a geometric vector bundle.

Consider the gluing data for ringed spaces

$$
(W_i=\mathbb A_{U_i}^r,
\ W_{ij}=\mathbb A_{U_i}^r|_{U_j}\subseteq W_i,
\ \varphi_{ji}:W_{ij}\longrightarrow W_{ji}).
$$

The cocycle condition holds because these data come from the global object $\mathcal F$. By Lemma 7.10, there is a scheme $W$ realising these gluing data. The local projections

$$
W_i=\mathbb A_{U_i}^r\longrightarrow U_i
$$

glue to a scheme morphism

$$
W\longrightarrow X.
$$

By construction, this is a geometric vector bundle over $X$. Let $\mathcal S$ be the sheaf of sections of $W$. We claim that there is a natural isomorphism

$$
\mathcal F\longrightarrow\mathcal S.
$$

The construction gives natural sheaf isomorphisms

$$
\mathcal F|_{U_i}\longrightarrow\mathcal S|_{U_i}
$$

for every $U_i$, whose restrictions to the intersections $U_i\cap U_j$ agree. By Corollary 4.10, there is a global sheaf homomorphism, and by Lemma 4.6 it is an isomorphism. The assignment is injective because a vector bundle can be reconstructed, up to isomorphism, from its sheaf of sections by the construction above. For the statements about homomorphisms, see Exercises 17.21, 17.22, and 17.23.

Under this equivalence, the free sheaf of rank $r$ corresponds to affine space $\mathbb A_X^r$ over $X$.

<!-- upstream_entity: Spektrum/Nichtnullteiler/Triviales Vektorbündel/Strukturgarbe/Beispiel -->

### Example 17.11: injectivity for bundles and for sheaves {#br-bgk-2019-l17-exm-04}

Let $R$ be a commutative ring and let $f\in R$. Via

$$
\operatorname{Spek}(R[T])=\mathbb A_R^1
\longrightarrow
\operatorname{Spek}(R[T])=\mathbb A_R^1,
\qquad T\longmapsto fT,
$$

the element $f$ defines a vector bundle homomorphism. On the fibres over points $P\in\operatorname{Spek}(R)$ where $f$ is a unit, namely the points of $D(f)$, this map is bijective; over the other points it is the zero map. Thus this map is injective — and at the same time surjective and bijective — only if $f$ is a unit.

However, multiplication by $f$ also defines a homomorphism of the structure sheaf

$$
\mathcal O_X\longrightarrow\mathcal O_X,
\qquad1\longmapsto f.
$$

Thus, on every open subset $U\subseteq X=\operatorname{Spek}(R)$, there is a $\Gamma(U,\mathcal O_X)$-module homomorphism

$$
\Gamma(U,\mathcal O_X)\longrightarrow\Gamma(U,\mathcal O_X),
\qquad r\longmapsto rf.
$$

This sheaf homomorphism is injective exactly when $f$ is a non-zero-divisor in $R$, and bijective exactly when $f$ is a unit. Thus the notions of injectivity for vector bundles and locally free sheaves do not coincide.
