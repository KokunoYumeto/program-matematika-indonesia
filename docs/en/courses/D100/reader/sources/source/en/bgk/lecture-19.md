---
title: "Lecture 19 - Tangent Bundles"
stable_id: br-bgk-2019-l19
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 19"
upstream_pageid: 109023
upstream_revid: 793611
upstream_timestamp: "2022-08-25T06:23:18Z"
upstream_mediawiki_sha1: 4eb53f5c2f3154e392b0a8989bc69dca84449e0c
source_url: "https://de.wikiversity.org/w/index.php?oldid=793611"
authority_manifest: authority/wikiversity-bgk/unit-19/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ffd4e79d12cd6fd63836cb6d7fd17e5dc6481f3befaeb50efeb9a47c4cc70512
authority_manifest_status: "Complete terminal authority freeze; all 33 file records have been recomputed without mismatches."
lecture_xml: authority/wikiversity-bgk/unit-19/lecture-19.xml
lecture_xml_sha256: 55e9011a39d21322986e608435f0689cadc87e316dc82d304ed821df9d4f0175
lecture_expanded_tex: authority/wikiversity-bgk/unit-19/lecture-19-expanded.tex
lecture_expanded_tex_sha256: fab690126be772df0cc413b7bb2ad907b23084b9b0a5301016b39bfe17cf441d
official_pdf: authority/artifacts/bgk-lecture-19-official.pdf
official_pdf_sha256: 656e979ceed28a4a9af768d91d4a0fdc53adcf65272e40edb153bc74c3b4ead7
official_pdf_status: "Local official PDF witness; 100,644 bytes, 7 pages, and upload SHA-1 b4925ff55aa2f3c72a595abfc8bb93c95e5bb4ac have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-19/official-pdfs-api.json
official_pdf_metadata_sha256: a37c74918c2fea4dd11a6ce3f9aee6d903596250bf8471c3d089d1c162fbb2af
official_pdf_source_bytes: 100644
official_pdf_source_sha1: b4925ff55aa2f3c72a595abfc8bb93c95e5bb4ac
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
media_credits: source/id-ID/media-credits-bgk-unit-19.md
rights_ledger: authority/RIGHTS-bgk-unit-19.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-19.json
asset_closure_sha256: 0adbc2e593bd9dab369022c73e8d4e69e988ce95bc57e7b1414147c8eb0e03fd
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 19: Tangent Bundles {#br-bgk-2019-l19}

## The sheaf of Kähler differentials on a scheme {#br-bgk-2019-l19-s01}

Let $X$ be a scheme over a base scheme $S$. We wish to define a sheaf version of the module of Kähler differentials.

<!-- upstream_entity: Kähler-Differentiale/Schema/Einführung/Textabschnitt -->

<!-- upstream_entity: Affines Schema/Affines Basisschema/Garbe der Kähler-Differentiale/Lokalisierungseigenschaften/Fakt -->

### Lemma 19.1: localisation of the affine sheaf of Kähler differentials {#br-bgk-2019-l19-lem-01}

Let $A$ be a commutative algebra over a commutative ring $R$. For every $f\in A$ we have

$$
\left(\Gamma\bigl(D(f),\widetilde{\Omega_{A\mid R}}\bigr),
\widetilde d\right)
=\left(\Omega_{A_f\mid R},d\right),
$$

and for every prime ideal $\mathfrak p\in\operatorname{Spek}(A)$ we have

$$
\left(\bigl(\widetilde{\Omega_{A\mid R}}\bigr)_{\mathfrak p},
d_{\mathfrak p}\right)
=\left(\Omega_{A_{\mathfrak p}\mid R},d\right).
$$

#### Proof {#br-bgk-2019-l19-lem-01-proof}

This follows from Lemma 18.6 together with Lemma 14.5.

<!-- upstream_entity: Schema/Basisschema/Garbe der Kähler-Differentiale/Definition -->

### Definition 19.2: the sheaf of Kähler differentials {#br-bgk-2019-l19-def-01}

Let $p:X\to S$ be a scheme over a base scheme $S$. The *sheaf of Kähler differentials* $\Omega_{X\mid S}$ is the quasicoherent $\mathcal O_X$-module on $X$, together with a derivation over $p^{-1}\mathcal O_S$,

$$
d:\mathcal O_X\longrightarrow\Omega_{X\mid S},
$$

such that for every point $P\in X$,

$$
\bigl((\Omega_{X\mid S})_P,d_P\bigr)
=\bigl(\Omega_{\mathcal O_{X,P}\mid\mathcal O_{S,p(P)}},d\bigr).
$$

We must show that such an object exists and is unique. By quasicoherence, for every affine open subset $V=\operatorname{Spek}(R)\subseteq S$ and every affine open subset $U=\operatorname{Spek}(A)\subseteq X$ with $U\subseteq p^{-1}(V)$, the module on $U$ must agree with $\widetilde{\Omega_{A\mid R}}$. In the affine case, Lemma 19.1 shows that $\widetilde{\Omega_{A\mid R}}$ is indeed the correct model.

If $(\Omega,d)$ and $(\Omega',d')$ are two models, the universal property, first on affine pieces and then in general, gives an $\mathcal O_X$-module homomorphism

$$
\widetilde{\Omega_{A\mid R}}\longrightarrow\Omega'.
$$

Since this is an isomorphism at every point, it is an isomorphism. Thus there can be only one such sheaf.

Given an affine cover

$$
S=\bigcup_{j\in J}V_j
$$

and a corresponding affine cover

$$
X=\bigcup_{i\in I}U_i,
$$

with $U_i\subseteq p^{-1}(V_j)$ for some $j=j(i)$, the sheaves $\Omega_{U_i\mid V_{j(i)}}$ can be glued together. This is because their restrictions to affine pieces $U\subseteq U_i\cap U_{i'}$ over $V\subseteq V_{j(i)}\cap V_{j(i')}$ are uniquely determined.

<!-- upstream_entity: Schema/Basisschema/Garbe der Kähler-Differentiale/Tangentialgarbe/Definition -->

### Definition 19.3: the tangent sheaf {#br-bgk-2019-l19-def-02}

Let $p:X\to S$ be a scheme over a base scheme $S$. The *tangent sheaf* $\mathcal T_{X,S}$ is the dual module

$$
\mathcal T_{X,S}=\Omega_{X\mid S}^{*}.
$$

Thus

$$
\mathcal T_{X,S}
=\Omega_{X\mid S}^{*}
=\mathcal Hom(\Omega_{X\mid S},\mathcal O_X)
=\mathcal{Der}_{p^{-1}\mathcal O_S}(\mathcal O_X,\mathcal O_X),
$$

where the last equality follows from the universal property of Kähler differentials. Accordingly, the sheaf of Kähler differentials is also called the *cotangent sheaf*.

> **Editorial note — derivations relative to the base.** The source writes $\mathcal{Der}(\mathcal O_X,\mathcal O_X)$ without a base subscript. Since $\mathcal T_{X,S}$ is the tangent sheaf relative to $S$, the universal property identifies it with derivations over $p^{-1}\mathcal O_S$, as written here.

We now formulate, for a scheme over a base scheme, the general versions of the statements about Kähler differentials in the affine case from the previous lecture.

<!-- upstream_entity: Kähler-Differentiale/Relative Differentialsequenz/Schema/Fakt -->

### Lemma 19.4: the sequence of relative differentials {#br-bgk-2019-l19-lem-02}

Let $\varphi:X\to Y$ be a scheme morphism over a base scheme $S$. Then the sequence of quasicoherent $\mathcal O_X$-modules

$$
\varphi^*\Omega_{Y\mid S}
\longrightarrow\Omega_{X\mid S}
\longrightarrow\Omega_{X\mid Y}
\longrightarrow 0
$$

is exact.

#### Proof {#br-bgk-2019-l19-lem-02-proof}

This follows from Lemma 18.7.

<!-- upstream_entity: Kähler-Differentiale/Konormalensequenz/Schema/Fakt -->

### Lemma 19.5: the conormal sequence {#br-bgk-2019-l19-lem-03}

Let $X$ be a scheme over a base scheme $S$, and let $\mathcal I\subseteq\mathcal O_X$ be an ideal sheaf on $X$ with associated closed subscheme $j:Y\to X$. Then the sequence of quasicoherent $\mathcal O_Y$-modules

$$
\mathcal I/\mathcal I^2
\longrightarrow j^*\Omega_{X\mid S}
\longrightarrow\Omega_{Y\mid S}
\longrightarrow 0
$$

is exact.

#### Proof {#br-bgk-2019-l19-lem-03-proof}

This follows directly from Lemma 18.8.

<!-- upstream_entity: Schema/Glatt/Kählermodul/Lokal frei/Fakt -->

### Corollary 19.6: smoothness and local freeness of Kähler differentials {#br-bgk-2019-l19-cor-01}

Let $K$ be an algebraically closed field and let $X$ be a connected scheme of finite type over $K$. Then $X$ is smooth if and only if the module of Kähler differentials $\Omega_{X\mid K}$ is locally free of constant rank $\dim(X)$.

#### Proof {#br-bgk-2019-l19-cor-01-proof}

This follows from Theorem 18.16 and Theorem 18.17.

<!-- upstream_entity: Schema/Glatt/Kanonische Garbe/Definition -->

### Definition 19.7: the canonical sheaf {#br-bgk-2019-l19-def-03}

Let $K$ be an algebraically closed field and let $X$ be a connected smooth scheme of finite type over $K$, of dimension $d$. The sheaf

$$
\omega_X:=\det\Omega_{X\mid K}
=\bigwedge^d\Omega_{X\mid K}
$$

is called the *canonical sheaf* of $X$.

## The tangent bundle on projective space {#br-bgk-2019-l19-s02}

<!-- upstream_entity: Projektiver Raum/R/Kählermodul/Fakt -->

### Theorem 19.8: the Euler sequence for Kähler differentials {#br-bgk-2019-l19-thm-01}

Let

$$
\mathbb P_R^n=\operatorname{Proj}(R[X_0,X_1,\ldots,X_n])
$$

be projective space over a commutative ring $R$. The $\mathcal O_{\mathbb P_R^n}$-module of Kähler differentials $\Omega_{\mathbb P_R^n\mid R}$ is described by the short exact sequence

$$
0\longrightarrow\Omega_{\mathbb P_R^n\mid R}
\longrightarrow\mathcal O_{\mathbb P_R^n}(-1)^{\oplus(n+1)}
\xrightarrow{\ X_0,\ldots,X_n\ }
\mathcal O_{\mathbb P_R^n}
\longrightarrow 0,
$$

together with the universal derivation which, on every open set $U\subseteq\mathbb P_R^n$, maps a function $f\in\Gamma(U,\mathcal O_{\mathbb P_R^n})$ to

$$
df=\left(\frac{\partial f}{\partial X_0},\ldots,
\frac{\partial f}{\partial X_n}\right).
$$

#### Proof {#br-bgk-2019-l19-thm-01-proof}

Denote the kernel sheaf on the left, which we wish to identify as the Kähler module, by

$$
\mathcal S=\operatorname{Syz}(X_0,\ldots,X_n).
$$

The displayed map $d$, arising from the universal derivation on $n+1$-dimensional space, turns a function of degree $0$ into one of degree $-1$, as can be checked directly for rational monomials. Thus there is an $R$-linear map

$$
d:\Gamma(U,\mathcal O_{\mathbb P_R^n})
\longrightarrow
\Gamma\bigl(U,\mathcal O_{\mathbb P_R^n}(-1)^{\oplus(n+1)}\bigr).
$$

The Leibniz rule carries over because partial derivatives satisfy it. We must show that the image of $d$ lies in the kernel of the last map. For a monomial $X^\nu$ of degree $0$, we have

$$
\sum_{j=0}^n X_j\frac{\partial X^\nu}{\partial X_j}
=\sum_{j=0}^n\nu_jX^\nu
=\left(\sum_{j=0}^n\nu_j\right)X^\nu
=0.
$$

Now consider the situation on $D_+(X_0)$ and set $Y_j=X_j/X_0$. Using Example 12.10 and Example 15.5 gives

$$
\begin{aligned}
\Gamma(D_+(X_0),\mathcal S)
&=\ker\left(
\Gamma\bigl(D_+(X_0),\mathcal O_{\mathbb P_R^n}(-1)^{\oplus(n+1)}\bigr)
\xrightarrow{\ X_0,X_1,\ldots,X_n\ }
\Gamma(D_+(X_0),\mathcal O_{\mathbb P_R^n})
\right)\\
&=\ker\left(
(R[X_0,X_1,\ldots,X_n]_{X_0})_{-1}^{\oplus(n+1)}
\xrightarrow{\ X_0,X_1,\ldots,X_n\ }
(R[X_0,X_1,\ldots,X_n]_{X_0})_0
\right)\\
&=\ker\left(
R[Y_1,\ldots,Y_n]X_0^{-1}\oplus\cdots\oplus
R[Y_1,\ldots,Y_n]X_0^{-1}
\xrightarrow{\ X_0,X_0Y_1,\ldots,X_0Y_n\ }
R[Y_1,\ldots,Y_n]
\right)\\
&\cong R[Y_1,\ldots,Y_n]\oplus\cdots\oplus R[Y_1,\ldots,Y_n],
\end{aligned}
$$

with $n$ summands in the last line. Under this isomorphism, the tuple $(P_1,\ldots,P_n)$ corresponds to the kernel tuple

$$
\left(-\sum_{i=1}^nP_iY_iX_0^{-1},
P_1X_0^{-1},\ldots,P_nX_0^{-1}\right).
$$

Under the map $d$, the monomial

$$
Y^\mu
=\left(\frac{X_1}{X_0}\right)^{\mu_1}\cdots
\left(\frac{X_n}{X_0}\right)^{\mu_n}
=X_0^{-\sum_{j=1}^n\mu_j}X_1^{\mu_1}\cdots X_n^{\mu_n}
\in\Gamma(D_+(X_0),\mathcal O_{\mathbb P_R^n})
$$

maps to the element

$$
\begin{aligned}
\biggl(&-\Bigl(\sum_{j=1}^n\mu_j\Bigr)
X_0^{-\sum_{j=1}^n\mu_j-1}X_1^{\mu_1}\cdots X_n^{\mu_n},\\
&\mu_1X_0^{-\sum_{j=1}^n\mu_j}X_1^{\mu_1-1}X_2^{\mu_2}\cdots X_n^{\mu_n},
\ldots,
\mu_nX_0^{-\sum_{j=1}^n\mu_j}X_1^{\mu_1}\cdots X_n^{\mu_n-1}
\biggr).
\end{aligned}
$$

Under the identification above, namely omitting the first component and multiplying by $X_0$, this becomes the tuple of derivatives with respect to the variables $Y_j$. Thus, by Lemma 18.5, we obtain the universal derivation of the polynomial ring $R[Y_1,\ldots,Y_n]$.

In particular, the module of Kähler differentials on projective space is locally free.

<!-- upstream_entity: Projektiver Raum/R/Tangentialgarbe/Fakt -->

### Corollary 19.9: the Euler sequence for the tangent sheaf {#br-bgk-2019-l19-cor-02}

Let

$$
\mathbb P_R^n=\operatorname{Proj}(R[X_0,X_1,\ldots,X_n])
$$

be projective space over a commutative ring $R$. The tangent sheaf on $\mathbb P_R^n$ is described by the short exact sequence

$$
0\longrightarrow\mathcal O_{\mathbb P_R^n}
\xrightarrow{\ X_0,\ldots,X_n\ }
\mathcal O_{\mathbb P_R^n}(1)^{\oplus(n+1)}
\longrightarrow\mathcal T_{\mathbb P_R^n,R}
\longrightarrow 0.
$$

At the right-hand end, the global element $X_i e_j$ in the $j$th component maps to the global derivation

$$
X_i\frac{\partial}{\partial X_j}.
$$

#### Proof {#br-bgk-2019-l19-cor-02-proof}

This follows directly from Theorem 19.8 by dualising. The additional assertion also follows from Theorem 19.8: under duality, the element $X_i e_j$ in the $j$th component of $\mathcal O_{\mathbb P_R^n}(1)^{\oplus(n+1)}$ corresponds to the map

$$
X_i\circ p_j:
\mathcal O_{\mathbb P_R^n}(-1)^{\oplus(n+1)}
\longrightarrow\mathcal O_{\mathbb P_R^n},
$$

that is, projection onto the $j$th component followed by multiplication by $X_i$. Viewed as a linear form on the module of Kähler differential forms $\Omega_{\mathbb P_R^n\mid R}\subseteq
\mathcal O_{\mathbb P_R^n}(-1)^{\oplus(n+1)}$, this corresponds to the linear form associated with the derivation

$$
f\longmapsto X_i\frac{\partial f}{\partial X_j}.
$$

Compared with other projective varieties, projective space has the special feature of possessing many global vector fields.

<!-- upstream_entity: Projektiver Raum/K/Kanonische Garbe/Fakt -->

### Corollary 19.10: the canonical sheaf of projective space {#br-bgk-2019-l19-cor-03}

Let

$$
\mathbb P_R^n=\operatorname{Proj}(R[X_0,X_1,\ldots,X_n])
$$

be projective space over a commutative ring $R$. Then its canonical sheaf is

$$
\omega_{\mathbb P_R^n\mid R}
=\det\Omega_{\mathbb P_R^n\mid R}
\cong\mathcal O_{\mathbb P_R^n}(-n-1).
$$

#### Proof {#br-bgk-2019-l19-cor-03-proof}

This follows from Theorem 19.8, Theorem 16.11, and Corollary 16.12.

Thus the anticanonical sheaf, the dual of the canonical sheaf, on projective space equals $\mathcal O_{\mathbb P_R^n}(n+1)$ and has many global sections.

> **Editorial note — the base ring.** The source changes the subscript from the theorem's base ring $R$ to an undefined $K$ in this sentence. This edition keeps $R$.

## Hypersurfaces in projective space {#br-bgk-2019-l19-s03}

<!-- upstream_entity: Projektiver Raum/K/Hyperfläche/Glatt/Charakterisierungen/Fakt -->

### Theorem 19.11: characterisations of smooth projective hypersurfaces {#br-bgk-2019-l19-thm-02}

Let $K$ be an algebraically closed field and let

$$
F\in K[X_0,X_1,\ldots,X_n]
$$

be a homogeneous polynomial of degree $d$. The following statements are equivalent.

1. The affine hypersurface

   $$
   V(F)=\operatorname{Spek}(K[X_0,X_1,\ldots,X_n]/(F))
   \subseteq\mathbb A_K^{n+1}
   $$

   is smooth away from the origin.

2. The projective hypersurface

   $$
   Y=V_+(F)
   =\operatorname{Proj}(K[X_0,X_1,\ldots,X_n]/(F))
   \subseteq\mathbb P_K^n
   $$

   is smooth.

3. For every variable $X_i$, the algebra

   $$
   K[X_0,\ldots,X_{i-1},X_{i+1},\ldots,X_n]/(\widetilde F_i)
   $$

   is smooth, where

   $$
   \widetilde F_i=\frac{F}{X_i^d}
   $$

   denotes the dehomogenisation of $F$ with respect to $X_i$.

> **Editorial note — dehomogenisation and degree notation.** The source prints $F/X_i$ here, although a degree-$d$ homogeneous polynomial gives the degree-zero element $F/X_i^d$ on $D_+(X_i)$. It also changes the degree symbol from $d$ to $\delta$ three times in the proof and uses $R$ there without defining it. This edition uses $F/X_i^d$, keeps the stated degree $d$, and names the homogeneous coordinate ring below.

4. The module of Kähler differentials $\Omega_{Y\mid K}$ is locally free.

5. There is a short exact sequence of locally free sheaves on $Y$,

   $$
   0\longrightarrow\mathcal O_Y(-d)
   \longrightarrow j_Y^*\Omega_{\mathbb P_K^n\mid K}
   \longrightarrow\Omega_{Y\mid K}
   \longrightarrow 0.
   $$

#### Proof {#br-bgk-2019-l19-thm-02-proof}

The equivalence of (2) and (3) is clear from Lemma 12.17 and the fact that smoothness is local. The equivalence of (2) and (4) follows from Corollary 19.6. Write

$$
R=K[X_0,X_1,\ldots,X_n]/(F).
$$

The equivalence of (1) and (3) rests on the fact that, locally over $D_+(X_i)$, the cone map is given by

$$
D(X_i)=\operatorname{Spek}(R_{X_i})
=\operatorname{Spek}\bigl((R_{X_i})_0[X_i,X_i^{-1}]\bigr)
\longrightarrow
D_+(X_i)=\operatorname{Spek}((R_{X_i})_0).
$$

Thus the cone map is locally a punctured affine cylinder over the base.

For the implication from (4), or (2), to (5), Lemma 19.5 gives the exact sequence

$$
\mathcal I/\mathcal I^2
\longrightarrow j_Y^*\Omega_{\mathbb P_K^n\mid K}
\longrightarrow\Omega_{Y\mid K}
\longrightarrow 0.
$$

Here $\mathcal I$ is the principal ideal generated by $F$, and $\mathcal I\cong\mathcal O_{\mathbb P_K^n}(-d)$ via the map

$$
\mathcal O_{\mathbb P_K^n}
\longrightarrow\mathcal O_{\mathbb P_K^n}(d),
\qquad 1\longmapsto F.
$$

Furthermore, the restriction of this ideal sheaf to $Y$ is

$$
\mathcal O_Y(-d)
=\mathcal I\otimes\mathcal O_Y
=\mathcal I\otimes\mathcal O_{\mathbb P_K^n}/\mathcal I
=\mathcal I/\mathcal I^2.
$$

As the restriction of an invertible sheaf, it is again invertible. Locally, the map on the left is given, as in Remark 18.10, by the Jacobian matrix of the dehomogenisation of $F$. By smoothness, this map is injective, even after passing to residue fields. The implication from (5) to (4) is immediate by restricting the assertion.

<!-- upstream_entity: Projektiver Raum/K/Hyperfläche/Glatt/Kanonische Garbe/Fakt -->

### Corollary 19.12: the canonical sheaf of a smooth hypersurface {#br-bgk-2019-l19-cor-04}

Let $K$ be an algebraically closed field and let $F\in K[X_0,X_1,\ldots,X_n]$ be a homogeneous polynomial of degree $d$ such that the projective hypersurface $Y=V_+(F)$ is smooth. Then

$$
\omega_Y\cong\mathcal O_Y(d-n-1).
$$

#### Proof {#br-bgk-2019-l19-cor-04-proof}

Apply the short exact sequence of locally free sheaves on $Y$ from Theorem 19.11,

$$
0\longrightarrow\mathcal O_Y(-d)
\longrightarrow j_Y^*\Omega_{\mathbb P_K^n\mid K}
\longrightarrow\Omega_{Y\mid K}
\longrightarrow 0.
$$

By Theorem 16.11 and Corollary 19.10,

$$
\begin{aligned}
\mathcal O_Y(-d)\otimes\omega_{Y\mid K}
&=\mathcal O_Y(-d)\otimes\det\Omega_{Y\mid K}\\
&=\det j_Y^*\Omega_{\mathbb P_K^n\mid K}\\
&=j_Y^*\det\Omega_{\mathbb P_K^n\mid K}\\
&=j_Y^*\mathcal O_{\mathbb P_K^n}(-n-1)\\
&=\mathcal O_Y(-n-1).
\end{aligned}
$$

The last equality follows from Appendix Lemma 4.7. Tensoring with $\mathcal O_Y(d)$ proves the claim.

<!-- upstream_entity: Projektiver Raum/Hyperfläche/Kanonische Garbe/Grobe Klassifikation/Bemerkung -->

### Remark 19.13: a rough classification of smooth hypersurfaces {#br-bgk-2019-l19-rem-01}

Corollary 19.12 permits a rough classification of smooth hypersurfaces

$$
Y=V_+(F)\subseteq\mathbb P_K^n
$$

in projective space according to whether the twist $d-n-1$ in $\omega_Y\cong\mathcal O_Y(d-n-1)$ is negative, equal to $0$, or positive.

For $n=2$, that is, curves in the projective plane, $d=1,2$ gives a projective line; $d=3$, when the canonical sheaf is trivial, gives an elliptic curve; and $d\geq4$ gives a curve of general type.

For $n=3$, that is, surfaces in projective space, $d=1$ gives a projective plane; $d=2$ gives a surface isomorphic to $\mathbb P_K^1\times\mathbb P_K^1$; and $d=3$ gives a surface isomorphic to a projective plane blown up at six points. In any case, for $d\leq3$ one obtains a so-called *rational surface*, whose function field is the rational function field in two variables. For $d=4$, when the canonical sheaf is trivial, one obtains a so-called $K3$ surface. For $d\geq5$ one obtains a surface of general type.
