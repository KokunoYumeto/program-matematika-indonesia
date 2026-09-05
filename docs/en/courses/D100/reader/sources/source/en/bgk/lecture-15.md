---
title: "Lecture 15 - Modules on Projective Schemes"
stable_id: br-bgk-2019-l15
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 15"
upstream_pageid: 109019
upstream_revid: 1003744
upstream_timestamp: "2025-06-08T15:41:44Z"
upstream_mediawiki_sha1: 35b2de7ebb7276afe88784ffa590aae83faa8788
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003744"
authority_manifest: authority/wikiversity-bgk/unit-15/UNIT_AUTHORITY_MANIFEST.json
lecture_xml: authority/wikiversity-bgk/unit-15/lecture-15.xml
lecture_xml_sha256: d7f8c9271d15063c1d37396fb4ba0c46cc1aeadbe39f04d5a41d7545fd925be8
lecture_expanded_tex: authority/wikiversity-bgk/unit-15/lecture-15-expanded.tex
lecture_expanded_tex_sha256: 59c9522b6920c91ef70091593891f8444f60ce73ad31b150b77d4e8c89931796
official_pdf: authority/artifacts/bgk-lecture-15-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-15.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 15: Modules on Projective Schemes {#br-bgk-2019-l15}

## Quasicoherent modules on projective schemes {#br-bgk-2019-l15-s01}

Graded modules over a graded ring $R$ give rise to quasicoherent modules on

$$
\operatorname{Proj}(R).
$$

> **Editorial note - terminology.** The source says “quasiprojective modules”,
> but the construction and Lemma 15.3 concern quasicoherent modules. This
> edition corrects that slip.

<!-- upstream_entity: Graduierter Ring/Graduierter Modul/Affin/Graduierung auf homogenen Mengen/Fakt -->

### Lemma 15.1: gradings on homogeneous open subsets {#br-bgk-2019-l15-lem-01}

Let $R$ be a $\mathbb Z$-graded commutative ring and $M$ a $\mathbb Z$-graded $R$-module. The associated $\mathcal O_X$-module $\widetilde M$ on $X=\operatorname{Spek}(R)$ has the following property: for every open subset

$$
U=D(\mathfrak a)\subseteq\operatorname{Spek}(R)
$$

arising from a homogeneous ideal $\mathfrak a$, the $\Gamma(U,\mathcal O_X)$-module $\Gamma(U,\widetilde M)$ has a $\mathbb Z$-grading compatible with the restriction maps.

#### Proof {#br-bgk-2019-l15-lem-01-proof}

For $M=R$, the assertion first means that the structure sheaf has a grading on the open subsets arising from homogeneous ideals. This is clear for $D(f)$ with $f$ homogeneous, and follows from this for $D(\mathfrak a)$ with any homogeneous ideal $\mathfrak a$. The module case follows in the same way.

It makes no sense to say that $\widetilde M$ is graded as a whole, since the grading is not defined on arbitrary open subsets that do not arise from homogeneous ideals. However, the grading on homogeneous subsets allows us to define a sheaf of modules on the projective spectrum associated with $R$.

<!-- upstream_entity: Graduierter Ring/Projektives Spektrum/Graduierter Modul/Garbe/Definition -->

### Definition 15.2: the sheaf of modules on the projective spectrum {#br-bgk-2019-l15-def-01}

Let $R$ be a $\mathbb Z$-graded commutative ring, $M$ a $\mathbb Z$-graded $R$-module, and

$$
Y=\operatorname{Proj}(R)
$$

the projective spectrum of $R$. The sheaf of $\mathcal O_Y$-modules associated with $M$, denoted by $\widehat M$, is specified as follows. For every open subset

$$
V=D_+(\mathfrak a)\subseteq Y
$$

arising from a homogeneous ideal $\mathfrak a$, set

$$
\Gamma(V,\widehat M)
:=\Gamma(D(\mathfrak a),\widetilde M)_0,
$$

and equip this with the natural restriction maps and the natural $\mathcal O_Y$-module structure.

For a graded $R$-module $M$ and a homogeneous prime ideal $\mathfrak p$, we set

$$
M_{(\mathfrak p)}
=\left(M_{\{h\text{ homogeneous}\mid h\notin\mathfrak p\}}\right)_0.
$$

<!-- upstream_entity: Graduierter Ring/Projektives Spektrum/Graduierter Modul/Garbe/Quasikohärenz/Fakt -->

### Lemma 15.3: properties of the projective sheaf of modules {#br-bgk-2019-l15-lem-02}

Let $R$ be a $\mathbb Z$-graded commutative ring, $M$ a $\mathbb Z$-graded $R$-module, $Y=\operatorname{Proj}(R)$ the projective spectrum of $R$, and $\widehat M$ the associated $\mathcal O_Y$-module. Then the following properties hold.

1. $\widehat M$ is a quasicoherent module.

2. For a homogeneous element $f\in R_+$,

   $$
   \Gamma(D_+(f),\widehat M)=(M_f)_0.
   $$

   Moreover, the restriction of $\widehat M$ to $D_+(f)$ equals the affine sheaf associated with $(M_f)_0$ on

   $$
   D_+(f)=\operatorname{Spek}((R_f)_0).
   $$

3. For a homogeneous prime ideal $\mathfrak p$ with $R_+\nsubseteq\mathfrak p$,

   $$
   \widehat M_{\mathfrak p}=M_{(\mathfrak p)}.
   $$

4. We have

   $$
   \Gamma(Y,\widehat M)
   =\left(\Gamma(D(R_+),\widetilde M)\right)_0.
   $$

#### Proof {#br-bgk-2019-l15-lem-02-proof}

1. The sheaf property follows from that of $\widetilde M$. For quasicoherence, see part (2).

2. For homogeneous $f\in R_+$, Lemma 14.5 gives

   $$
   \Gamma(D_+(f),\widehat M)
   =\Gamma(D(f),\widetilde M)_0
   =(M_f)_0.
   $$

   Thus, on the whole of $D_+(f)$, the sheaf $\widehat M|_{D_+(f)}$ agrees with $\widetilde{(M_f)_0}$. The corresponding equalities hold for open subsets $D(g)\subseteq D(f)$, and these identifications are compatible with restrictions. Hence the sheaves agree, and quasicoherence follows.

3. This follows from (2) via

   $$
   \begin{aligned}
   \widehat M_{\mathfrak p}
   &=\operatorname*{colim}_{\mathfrak p\in D_+(f)}
     \Gamma(D_+(f),\widehat M)\\
   &=\operatorname*{colim}_{\mathfrak p\in D_+(f)}(M_f)_0\\
   &=\left(\operatorname*{colim}_{\mathfrak p\in D_+(f)}M_f\right)_0\\
   &=\left(M_{\{h\in R\mid h\text{ homogeneous and }h\notin\mathfrak p\}}\right)_0\\
   &=M_{(\mathfrak p)}.
   \end{aligned}
   $$

   > **Editorial note - localisation set.** In this line the source writes
   > $R\setminus\mathfrak p\cap H$ without defining $H$ or parenthesising the
   > set operations. The explicit set above is the multiplicative system of
   > homogeneous elements outside $\mathfrak p$ used in Definition 15.2.

4. This is a special case of the general definition.

The last assertion means that, in general, the module of global sections of $\widehat M$ on $Y$ cannot be computed directly from $M$.

<!-- upstream_entity: Graduierter Ring/Projektives Spektrum/Verschiebung/Twist/Definition -->

### Definition 15.4: twisted structure sheaf {#br-bgk-2019-l15-def-02}

Let $R$ be a $\mathbb Z$-graded commutative ring and let $R(n)$ be the graded $R$-module obtained by shifting $R$ by $n$. The associated $\mathcal O_Y$-module on $Y=\operatorname{Proj}(R)$, denoted by

$$
\mathcal O_Y(n):=\widehat{R(n)}
$$

is called a *twisted structure sheaf*.

> **Editorial note - module rather than ring.** The source calls $R(n)$ a
> shifted graded ring. With the shifted grading it is a graded $R$-module and,
> as Exercise 15.11 notes, is a graded ring only when $n=0$.

<!-- upstream_entity: Polynomring/Projektiver Raum/Getwistete Strukturgarben/Beispiel -->

### Example 15.5: twisted structure sheaves on projective space {#br-bgk-2019-l15-exm-01}

For the standard-graded polynomial ring $K[X_0,X_1,\ldots,X_d]$, with $d\geq 1$, we have

$$
\Gamma\left(\mathbb P_K^d,
\mathcal O_{\mathbb P_K^d}(\ell)\right)
=K[X_0,X_1,\ldots,X_d]_\ell,
$$

the space of polynomials of degree $\ell$ in $d+1$ variables. For $\ell<0$, this is the zero space; for $\ell=0$ (the structure sheaf), it equals $K$; for $\ell=1$, it consists of all linear forms; and so on. For the open subsets $D_+(X_i)$,

$$
\begin{aligned}
\Gamma\left(D_+(X_i),\mathcal O_{\mathbb P_K^d}(\ell)\right)
&=\left(K[X_0,X_1,\ldots,X_d]_{X_i}\right)_\ell\\
&=K\left[\frac{X_0}{X_i},\ldots,
\frac{X_{i-1}}{X_i},\frac{X_{i+1}}{X_i},\ldots,
\frac{X_d}{X_i}\right]\cdot X_i^\ell.
\end{aligned}
$$

For projective space, we already saw in Example 13.19 that these sheaves are invertible. This also holds in general.

<!-- upstream_entity: Standard-graduierter Ring/Projektives Spektrum/Verschiebung/Twist/Invertierbar/Fakt -->

### Lemma 15.6: twisted structure sheaves are invertible {#br-bgk-2019-l15-lem-03}

Let $R$ be a standard-graded commutative ring. Then the twisted structure sheaves $\mathcal O_Y(n)$ on $Y=\operatorname{Proj}(R)$ are invertible.

#### Proof {#br-bgk-2019-l15-lem-03-proof}

Write

$$
R=R_0[x_1,\ldots,x_d]
=R_0[X_1,\ldots,X_d]/\mathfrak a,
$$

where the $x_i$ have degree $1$. The elements $x_i$ also generate the irrelevant ideal, so there is an affine open cover

$$
\operatorname{Proj}(R)=\bigcup_{i=1}^d D_+(x_i).
$$

Let $x$ be one of the $x_i$. By Lemma 15.3(2),

$$
\mathcal O_Y(n)|_{D_+(x)}=\mathcal L,
$$

where $\mathcal L$ is the affine sheaf associated with the $(R_x)_0$-module

$$
L=(R_x(n))_0=(R_x)_n
$$

on

$$
D_+(x)=\operatorname{Spek}((R_x)_0).
$$

In this situation,

$$
(R_x)_0\longrightarrow(R_x)_n,
\qquad h\longmapsto hx^n,
$$

is an isomorphism of $(R_x)_0$-modules. There is therefore an isomorphism of $\mathcal O_Y|_{D_+(x)}$-modules

$$
\mathcal O_Y|_{D_+(x)}
\longrightarrow\mathcal O_Y(n)|_{D_+(x)}.
$$

The twisted structure sheaves $\mathcal O_Y(n)$ are distinguished invertible sheaves associated with the projective scheme $Y=\operatorname{Proj}(R)$, although they depend on the graded ring $R$.

<!-- upstream_entity: Standard-graduierter Ring/Projektives Spektrum/Modul/Verschiebung/Twist/Tensorierung/Fakt -->

### Lemma 15.7: shifting a module and tensoring with a twisted sheaf {#br-bgk-2019-l15-lem-04}

Let $R$ be a standard-graded commutative ring, $M$ a graded $R$-module, and $n\in\mathbb Z$. There is a natural $\mathcal O_Y$-isomorphism

$$
\widehat M\otimes_{\mathcal O_Y}\mathcal O_Y(n)
\longrightarrow\widehat{M(n)}
$$

on $Y=\operatorname{Proj}(R)$, where $M(n)$ denotes the module obtained by shifting $M$ by $n$.

#### Proof {#br-bgk-2019-l15-lem-04-proof}

For a homogeneous element $f\in R_+$, there is an $(R_f)_0$-module homomorphism

$$
(M_f)_0\otimes_{(R_f)_0}(R_f)_n
\longrightarrow(M_f)_n,
\qquad
\frac{m}{f^k}\otimes\frac{r}{f^\ell}
\longmapsto\frac{rm}{f^{k+\ell}},
$$

arising directly from the homogeneous module multiplication $M\times R\to M$. For every open subset $U\subseteq\operatorname{Proj}(R)$, these homomorphisms induce a module homomorphism

$$
\operatorname*{colim}_{U\subseteq D_+(f)}
\left((M_f)_0\otimes_{(R_f)_0}(R_f)_n\right)
\longrightarrow
\operatorname*{colim}_{U\subseteq D_+(f)}(M_f)_n,
$$

which together form a presheaf morphism. Since

$$
(M(n)_f)_0=(M_f)_n,
$$

the sheafification of the presheaf on the right is $\widehat{M(n)}$. Sheafifying the left-hand side, in two steps, gives

$$
\widehat M\otimes_{\mathcal O_{\operatorname{Proj}(R)}}\mathcal O_Y(n),
$$

so we obtain a module homomorphism

$$
\widehat M\otimes_{\mathcal O_{\operatorname{Proj}(R)}}\mathcal O_Y(n)
\longrightarrow\widehat{M(n)}.
$$

That this is an isomorphism can be proved on an affine cover. If $f$ is homogeneous, then by Lemma 14.10 and Lemma 15.3(2), the $(R_f)_0$-module homomorphism above,

$$
(M_f)_0\otimes_{(R_f)_0}(R_f)_n
\longrightarrow(M_f)_n,
$$

equals the evaluation of the sheafified homomorphism. If $f$ has degree $1$—and the corresponding open subsets $D_+(f)$ cover $Y$—then it is an isomorphism. By Exercise 12.2,

$$
(R_f)_0\cong(R_f)_n
$$

via $1\mapsto f^n$, so the module on the left is isomorphic to $(M_f)_0$. With this identification, the map is given by

$$
\frac{m}{f^k}\longmapsto f^n\cdot\frac{m}{f^k},
$$

and it is bijective because $f$ is a unit.

<!-- upstream_entity: Standard-graduierter Ring/Projektives Spektrum/Quasikohärenter Modul/Twist/Definition -->

### Definition 15.8: twist of a quasicoherent module {#br-bgk-2019-l15-def-03}

Let $R$ be a standard-graded ring, $\mathcal F$ a quasicoherent module on $Y=\operatorname{Proj}(R)$, and $n\in\mathbb Z$. The module

$$
\mathcal F(n):=\mathcal F\otimes_{\mathcal O_Y}\mathcal O_Y(n)
$$

is called the *$n$th twist* of $\mathcal F$.

Thus the sheaf of modules $\widehat{M(n)}$ agrees with the $n$th twist of $\widehat M$.

## Global generation {#br-bgk-2019-l15-s02}

<!-- upstream_entity: Beringter Raum/Modulgarbe/Von globalen Schnitten erzeugt/Definition -->

### Definition 15.9: generated by global sections {#br-bgk-2019-l15-def-04}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal M$ an $\mathcal O_X$-module on $X$. We say that $\mathcal M$ is *generated by global sections* if there is a family

$$
s_i\in\Gamma(X,\mathcal M),\qquad i\in I,
$$

such that, for every point $x\in X$, the stalk $\mathcal M_x$ is generated as an $\mathcal O_{X,x}$-module by the restrictions of the $s_i$.

<!-- upstream_entity: Schema/Modulgarbe/Von globalen Schnitten erzeugt/Fakt -->

### Proposition 15.10: properties of global generation {#br-bgk-2019-l15-prop-01}

Let $(X,\mathcal O_X)$ be a scheme. Then the following assertions hold.

1. The structure sheaf $\mathcal O_X$ is generated by global sections.

2. A quasicoherent module $\mathcal M$ is generated by global sections if and only if there is a surjective module homomorphism

   $$
   \mathcal O_X^{(I)}\longrightarrow\mathcal M.
   $$

3. On an affine scheme, every quasicoherent module is generated by global sections.

4. If $\mathcal M$ is generated by global sections and $\mathcal M\to\mathcal N$ is surjective, then $\mathcal N$ is also generated by global sections.

#### Proof {#br-bgk-2019-l15-prop-01-proof}

See Exercise 15.17.

<!-- upstream_entity: Projektiver Raum/Getwistete Strukturgarbe/Von globalen Schnitten erzeugt/Fakt -->

### Lemma 15.11: global generation of twisted structure sheaves {#br-bgk-2019-l15-lem-05}

On projective space $\mathbb P_R^d$ over a commutative ring $R$, the twisted structure sheaf $\mathcal O_{\mathbb P_R^d}(k)$ is generated by global sections for $k\geq0$, and is not generated by global sections for $k<0$ and $d\geq1$.

#### Proof {#br-bgk-2019-l15-lem-05-proof}

See Exercise 15.18.

<!-- upstream_entity: Projektiver Raum/Noethersch/Kohärente Garbe/Twist/Von globalen Schnitten erzeugt/Fakt -->

### Theorem 15.12: a positive twist is eventually globally generated {#br-bgk-2019-l15-thm-01}

Let $\mathbb P_R^d$ be projective space over a noetherian ring $R$, and let $\mathcal G$ be a coherent sheaf on $\mathbb P_R^d$. Then there is an $\ell\in\mathbb N_+$ such that $\mathcal G(\ell)$ is generated by global sections.

#### Proof {#br-bgk-2019-l15-thm-01-proof}

There is an isomorphism

$$
\mathcal G|_{D_+(X_i)}\cong\widetilde M_i,
$$

where $M_i$ is a finitely generated module over the polynomial ring $R_i$ associated with $D_+(X_i)$. For the invertible sheaf $\mathcal O_{\mathbb P_R^d}(1)$, the invertibility locus of the global section $X_i$ is $D_+(X_i)$ by Exercise 13.21. For a finite generating system $s_{ij}$, $j\in J_i$, of the $R_i$-module $M_i$, Theorem 14.13(2) gives a common exponent $n$ such that the $X_i^n s_{ij}$ come from global elements in

$$
\Gamma(\mathbb P_R^d,\mathcal G(n)).
$$

This can be done for every $i$, giving an $\ell$ such that global sections in $\Gamma(\mathbb P_R^d,\mathcal G(\ell))$ generate the modules on the affine open cover. They therefore also generate every stalk, so global generation follows.

<!-- upstream_entity: Projektiver Raum/Kohärente Garbe/Surjektion mit direkter Summe/Fakt -->

### Theorem 15.13: a surjective presentation by twisted structure sheaves {#br-bgk-2019-l15-thm-02}

Let $\mathbb P_R^d$ be projective space over a noetherian ring $R$, and let $\mathcal G$ be a coherent sheaf on $\mathbb P_R^d$. Then there is a finite direct sum

$$
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^d}(\ell_j)
$$

and a surjective module homomorphism

$$
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^d}(\ell_j)
\longrightarrow\mathcal G.
$$

#### Proof {#br-bgk-2019-l15-thm-02-proof}

By Theorem 15.12, there is an $\ell$ such that $\mathcal G(\ell)$ is generated by finitely many global sections. By Proposition 15.10(2), there is a surjective module homomorphism

$$
\mathcal O_{\mathbb P_R^d}^{r}\longrightarrow\mathcal G(\ell).
$$

Tensoring this map with $\mathcal O_{\mathbb P_R^d}(-\ell)$ gives a surjection

$$
\left(\mathcal O_{\mathbb P_R^d}(-\ell)\right)^r
\longrightarrow\mathcal G.
$$
