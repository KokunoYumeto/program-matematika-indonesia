---
title: "Lecture 14 - Quasicoherent Modules"
stable_id: br-bgk-2019-l14
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 14"
upstream_pageid: 109018
upstream_revid: 1019980
upstream_timestamp: "2025-08-09T13:36:46Z"
upstream_mediawiki_sha1: f6d1200be466cd501f566a755ab3009dedda8b3e
source_url: "https://de.wikiversity.org/w/index.php?oldid=1019980"
lecture_xml: authority/wikiversity-bgk/unit-14/lecture-14.xml
lecture_xml_sha256: 29dacade22fd06d6d59b435665a143004580611eef2bebc706a507507b30d27c
lecture_expanded_tex: authority/wikiversity-bgk/unit-14/lecture-14-expanded.tex
lecture_expanded_tex_sha256: c7baacd23aa5ab8ae7b0525bebd1c3646438b5df95af3fa3b6e235974bfed279
official_pdf_metadata: authority/wikiversity-bgk/unit-14/official-pdfs-api.json
official_pdf_metadata_sha256: 87597a5f905829e257b9997c3b4b9855ae455be7d1272aa1dec2fa0f4b5851a3
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_bytes: 2104862
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "120-126"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
media_credits: source/id-ID/media-credits-bgk-unit-14.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 14: Quasicoherent Modules {#br-bgk-2019-l14}

## Quasicoherent modules on affine schemes {#br-bgk-2019-l14-s01}

For a commutative ring $R$, its $R$-modules are important objects that characterise the ring: for example, ideals, quotient rings, projective modules, and the module of Kähler differentials. We want to recover these modules in the context of the spectrum, that is, in a geometrised form. The construction runs parallel to the introduction of the structure sheaf on the spectrum.

<!-- upstream_entity: Spektrum/Modul/Prägarbe/Beispiel -->

### Example 14.1: the presheaf arising from a module {#br-bgk-2019-l14-exm-01}

Let $M$ be an $R$-module over a commutative ring $R$, and write $X=\operatorname{Spek}(R)$. We can define a presheaf of modules by setting, for each open subset $U\subseteq X$,

$$
\mathcal P(U)=\operatorname*{colim}_{U\subseteq D(f)}M_f.
$$

These are modules over the ring

$$
\operatorname*{colim}_{U\subseteq D(f)}R_f,
$$

and there are natural restriction homomorphisms compatible with the module structures. The stalk of this presheaf at a prime ideal $\mathfrak p$ is $M_{\mathfrak p}$.

<!-- upstream_entity: Spektrum/Modul/Definition -->

### Definition 14.2: the sheaf of modules on the spectrum {#br-bgk-2019-l14-def-01}

Let

$$
(X,\mathcal O_X)=\operatorname{Spek}(R)
$$

be the affine scheme of a commutative ring $R$, and let $M$ be an $R$-module. The *$\mathcal O_X$-module associated with $M$*, denoted by $\widetilde M$, is the assignment that associates to each open subset $U\subseteq X$ the commutative group

$$
\begin{aligned}
\Gamma(U,\widetilde M)=\biggl\{&(s_{\mathfrak p})_{\mathfrak p\in U}
\in\prod_{\mathfrak p\in U}M_{\mathfrak p}\ \bigg|\\
&\text{for every }\mathfrak p\in U\text{ there are }m\in M\text{ and }f\in R
\text{ with }\mathfrak p\in D(f)\subseteq U,\\
&\text{and }s_{\mathfrak q}=m/f\text{ in }M_{\mathfrak q}
\text{ for all }\mathfrak q\in D(f)\biggr\},
\end{aligned}
$$

together with scalar multiplication

$$
\begin{aligned}
\Gamma(U,\mathcal O_X)\times\Gamma(U,\widetilde M)
&\longrightarrow\Gamma(U,\widetilde M),\\
\bigl((g_{\mathfrak p})_{\mathfrak p\in U},
(s_{\mathfrak p})_{\mathfrak p\in U}\bigr)
&\longmapsto(g_{\mathfrak p}s_{\mathfrak p})_{\mathfrak p\in U}.
\end{aligned}
$$

To each inclusion $U\subseteq V$ it assigns the natural projection.

Starting the construction with the ring $R$ itself gives the structure sheaf.

<!-- upstream_entity: Spektrum/Modul/Garbe/Fakt -->

### Lemma 14.3: the construction gives an $\mathcal O_X$-module {#br-bgk-2019-l14-lem-01}

For an $R$-module $M$ over a commutative ring $R$, $\widetilde M$ is an $\mathcal O_X$-module on the affine scheme $X=\operatorname{Spek}(R)$.

#### Proof {#br-bgk-2019-l14-lem-01-proof}

This follows from the fact that $\widetilde M$ is defined as the sheafification of the presheaf

$$
U\longmapsto\operatorname*{colim}_{U\subseteq D(f)}M_f,
$$

and the module structure is inherited by its sheafification.

<!-- upstream_entity: Affines Schema/Modul/Punkt/Halm/Lokalisierung/Fakt -->

### Lemma 14.4: stalks are localisations {#br-bgk-2019-l14-lem-02}

Let $(X,\mathcal O_X)$ be the affine scheme of a commutative ring $R$, and let $x\in X$ be the point corresponding to a prime ideal $\mathfrak p$. If $M$ is an $R$-module with associated sheaf of modules $\widetilde M$, then its stalk is

$$
\widetilde M_x=M_{\mathfrak p}.
$$

#### Proof {#br-bgk-2019-l14-lem-02-proof}

This follows from Example 14.1 and Lemma 5.2(2).

<!-- upstream_entity: Affines Schema/Modul/Hauptmenge/Nenneraufnahme/Fakt -->

### Lemma 14.5: sections on principal open subsets {#br-bgk-2019-l14-lem-03}

Let $(X,\mathcal O_X)$ be the affine scheme of a commutative ring $R$, and let $M$ be an $R$-module with associated $\mathcal O_X$-module $\widetilde M$. For $f\in R$,

$$
\Gamma(D(f),\widetilde M)=M_f.
$$

In particular, the module of global sections is

$$
\Gamma(X,\widetilde M)=M.
$$

#### Proof {#br-bgk-2019-l14-lem-03-proof}

We first prove the special case stated last. There is a natural $R$-module homomorphism

$$
M\longrightarrow\Gamma(X,\widetilde M).
$$

It is injective because the vanishing of an element can be tested locally; compare Appendix Lemma 1.1. For surjectivity, let $s\in\Gamma(X,\widetilde M)$ be a global element. This means that there is an open cover

$$
X=\bigcup_{i\in I}U_i=\bigcup_{i\in I}D(f_i)
$$

and elements

$$
s_i=\frac{a_i}{f_i^{k_i}},
\qquad a_i\in M,
$$

which agree as sections on

$$
D(f_i)\cap D(f_j)=D(f_if_j),
$$

that is, as elements of $M_{f_if_j}$. By Corollary 8.6, we may assume that $I$ is finite. We may also replace all $k_i$ by their maximum $k$; naturally, this also changes the local numerators $a_i$. The compatibility

$$
\frac{a_i}{f_i^k}=\frac{a_j}{f_j^k}
$$

means that there are equations

$$
(f_if_j)^m a_i f_j^k=(f_if_j)^m a_j f_i^k
$$

in $M$, where $m$ is chosen as a maximum valid for all pairs. By Proposition 8.4(2),(4), the elements $f_i$, $i\in I$, generate the unit ideal. The same holds for $f_i^{m+k}$, so there are $g_i\in R$ with

$$
1=\sum_{i\in I}g_if_i^{m+k}.
$$

Set

$$
a:=\sum_{i\in I}g_ia_if_i^m.
$$

Then, for each $j$,

$$
\begin{aligned}
af_j^{m+k}
&=\sum_{i\in I}g_ia_if_i^mf_j^{m+k}\\
&=\sum_{i\in I}g_i(f_if_j)^ma_if_j^k\\
&=\sum_{i\in I}g_i(f_if_j)^ma_jf_i^k\\
&=a_jf_j^m\left(\sum_{i\in I}g_if_i^{m+k}\right)\\
&=a_jf_j^m.
\end{aligned}
$$

This means that

$$
\frac a1=\frac{a_j}{f_j^k}=s_j
$$

in $M_{f_j}$, so the section is represented by a single module element.

Now consider the situation on $D(f)$. It is the case just treated, with $R_f$ as the new ring and $M_f$ as the new module.

<!-- upstream_entity: Ganzheitsring/Wurzel -5/Standardideal/Garbe/Invertierbar/Beispiel -->

### Example 14.6: a nonprincipal ideal giving an invertible sheaf {#br-bgk-2019-l14-exm-02}

In the quadratic number ring

$$
R=A_{-5}=\mathbb Z[\sqrt{-5}]=\mathbb Z[T]/(T^2+5)
$$

we have the equality

$$
2\cdot3=6=(1+\sqrt5\,\mathrm i)(1-\sqrt5\,\mathrm i).
$$

Consider the ideal

$$
I=(2,1+\sqrt{-5}),
$$

which is prime but not principal, and its associated ideal sheaf $\widetilde I$ on $X=\operatorname{Spek}(R)$. The spectrum is covered by the two open sets $D(2)$ and $D(3)$. We have

$$
\widetilde I|_{D(2)}\cong\mathcal O_X|_{D(2)},
$$

since $2\in I$, so the ideal becomes the unit ideal in the localisation $R_2$. In $R_3$, that is, on $D(3)$,

$$
2=\frac{1-\sqrt5\,\mathrm i}3(1+\sqrt5\,\mathrm i),
$$

so $I_3$ is principal with generator $1+\sqrt5\,\mathrm i$. Hence

$$
\widetilde I|_{D(3)}\cong\mathcal O_X|_{D(3)},
$$

and $\widetilde I$ is an invertible sheaf.

<!-- upstream_entity: An-Singularität/Punktiertes Schema/Invertierbares Ideal/Beispiel -->

### Example 14.7: an invertible ideal on a punctured singularity {#br-bgk-2019-l14-exm-03}

Consider the ideal $I=(X,Z)$ in the $A_{n-1}$ singularity

$$
R=K[X,Y,Z]/(XY-Z^n).
$$

It defines an ideal sheaf $\widetilde I$ on $\operatorname{Spek}(R)$, and hence also a restricted ideal sheaf $\widetilde I|_U$ on the quasiaffine scheme

$$
U=D(X,Y,Z)=D(X,Y)
=\operatorname{Spek}(R)\setminus\{(X,Y,Z)\}
\subset\operatorname{Spek}(R).
$$

This restricted sheaf is invertible on $U$. Indeed, $X\in I$, and in $R_Y$,

$$
X=\frac{Z^{n-1}}Y Z.
$$

There are therefore isomorphisms

$$
\widetilde I|_{D(X)}\cong
\mathcal O_{\operatorname{Spek}(R)}|_{D(X)}
\qquad\text{and}\qquad
\widetilde I|_{D(Y)}\cong
\mathcal O_{\operatorname{Spek}(R)}|_{D(Y)}.
$$

By contrast, $\widetilde I$ is not invertible on the whole spectrum, since the ideal $I$ in the localisation $R_{(X,Y,Z)}$ is not principal.

> **Editorial note - singularity parameter.** This noninvertibility assertion requires $n\geq2$. For $n=1$, the relation is $Z=XY$, and $I=(X,Z)=(X)$ is principal. The source leaves this lower bound implicit in the singularity terminology.

<!-- upstream_entity: Affines Schema/Moduln/Homomorphismus/Garbenversion/Fakt -->

### Lemma 14.8: module homomorphisms induce sheaf morphisms {#br-bgk-2019-l14-lem-04}

Let $(X,\mathcal O_X)$ be the affine scheme of a commutative ring $R$, and let

$$
\varphi:M\longrightarrow N
$$

be an $R$-module homomorphism. There is exactly one $\mathcal O_X$-module homomorphism

$$
\widetilde M\longrightarrow\widetilde N
$$

that agrees globally with $\varphi$.

#### Proof {#br-bgk-2019-l14-lem-04-proof}

For each $f\in R$, compatibility with restrictions requires the following diagram to commute:

$$
\begin{matrix}
\Gamma(X,\widetilde M)=M&\xrightarrow{\ \varphi\ }&
\Gamma(X,\widetilde N)=N\\
\downarrow&&\downarrow\\
\Gamma(D(f),\widetilde M)=M_f&\longrightarrow&
\Gamma(D(f),\widetilde N)=N_f.
\end{matrix}
$$

The diagram uniquely determines the bottom map. These assignments then determine a unique presheaf morphism and, by sheafification, a unique sheaf morphism.

<!-- upstream_entity: Affines Schema/Moduln/Exaktheit/Fakt -->

### Lemma 14.9: short exact sequences pass to sheaves {#br-bgk-2019-l14-lem-05}

Let $R$ be a commutative ring and

$$
0\longrightarrow L\longrightarrow M\longrightarrow N\longrightarrow0
$$

a short exact sequence of $R$-modules. On the affine scheme $(X,\mathcal O_X)=\operatorname{Spek}(R)$ there is a short exact sequence of sheaves

$$
0\longrightarrow\widetilde L\longrightarrow\widetilde M
\longrightarrow\widetilde N\longrightarrow0
$$

consisting of quasicoherent $\mathcal O_X$-modules.

#### Proof {#br-bgk-2019-l14-lem-05-proof}

By Appendix Lemma 2.2, for every prime ideal $\mathfrak p$, the original short exact sequence gives a short exact sequence

$$
0\longrightarrow L_{\mathfrak p}\longrightarrow M_{\mathfrak p}
\longrightarrow N_{\mathfrak p}\longrightarrow0.
$$

By Lemma 14.4, this is the stalkwise version of the module homomorphisms between $\widetilde L$, $\widetilde M$, and $\widetilde N$ at the point $\mathfrak p$. By Lemma 6.3, this says precisely that the complex of sheaves is exact.

<!-- upstream_entity: Affines Schema/Moduln/Tensorprodukt/Fakt -->

### Lemma 14.10: tensor products of affine sheaves of modules {#br-bgk-2019-l14-lem-06}

Let $R$ be a commutative ring, $M$ and $N$ be $R$-modules, and $\widetilde M$ and $\widetilde N$ the associated sheaves of modules on $X=\operatorname{Spek}(R)$. There is a canonical isomorphism

$$
\widetilde M\otimes_{\mathcal O_X}\widetilde N
\cong\widetilde{M\otimes_RN}.
$$

#### Proof {#br-bgk-2019-l14-lem-06-proof}

We have

$$
M_f\otimes_{R_f}N_f=(M\otimes_RN)_f.
$$

Consider the presheaf

$$
U\longmapsto
\operatorname*{colim}_{U\subseteq D(f)}
(M_f\otimes_{R_f}N_f)
=
\operatorname*{colim}_{U\subseteq D(f)}(M\otimes_RN)_f.
$$

By definition, sheafification of the right-hand side gives the quasicoherent sheaf $\widetilde{M\otimes_RN}$. For open subsets $U\subseteq D(f)$, there are canonical module homomorphisms

$$
M_f\otimes_{R_f}N_f\longrightarrow
\left(\operatorname*{colim}_{U\subseteq D(f)}M_f\right)
\otimes_{\operatorname*{colim}_{U\subseteq D(f)}R_f}
\left(\operatorname*{colim}_{U\subseteq D(f)}N_f\right).
$$

Taking colimits gives, for every open subset, a module homomorphism

$$
\operatorname*{colim}_{U\subseteq D(f)}(M_f\otimes_{R_f}N_f)
\longrightarrow
\left(\operatorname*{colim}_{U\subseteq D(f)}M_f\right)
\otimes_{\operatorname*{colim}_{U\subseteq D(f)}R_f}
\left(\operatorname*{colim}_{U\subseteq D(f)}N_f\right).
$$

This is a map from the first presheaf to the tensor product of the two presheaves of modules. These homomorphisms are compatible with restrictions, so they form a presheaf morphism. By Lemma 5.2(1),(5), it passes to the associated sheaves. By the initial observation, the sheafification on the left is $\widetilde{M\otimes_RN}$, while by definition the sheafification on the right is $\widetilde M\otimes_{\mathcal O_X}\widetilde N$. Since this homomorphism is an isomorphism on every stalk, Lemma 4.6 shows that it is an isomorphism of sheaves.

## Quasicoherent modules {#br-bgk-2019-l14-s02}

For arbitrary schemes, the most important sheaves of modules are those that look like $\widetilde M$ on affine pieces.

<!-- upstream_entity: Schema/Quasikohärente Garbe/Definition -->

### Definition 14.11: quasicoherent module {#br-bgk-2019-l14-def-02}

An $\mathcal O_X$-module $\mathcal M$ on a scheme $(X,\mathcal O_X)$ is called *quasicoherent* if there is an affine open cover

$$
X=\bigcup_{i\in I}U_i,
\qquad U_i=\operatorname{Spek}(R_i),
$$

and $R_i$-modules $M_i$ such that

$$
\mathcal M|_{U_i}=\widetilde{M_i}.
$$

In particular, the structure sheaf of a scheme is quasicoherent, since on an affine open subset $U=\operatorname{Spek}(R)$ it agrees with $\widetilde R$. Invertible sheaves are also quasicoherent.

One can prove that, for a quasicoherent sheaf, its restriction to every affine open subset $U\subseteq X$ already equals the sheaf of modules associated with a module over the ring $\Gamma(U,\mathcal O_X)$.

<!-- upstream_entity: Schema/Kohärenter Modul/Definition -->

### Definition 14.12: coherent module {#br-bgk-2019-l14-def-03}

A quasicoherent $\mathcal O_X$-module $\mathcal M$ on a scheme $(X,\mathcal O_X)$ is called *coherent* if there is an affine open cover

$$
X=\bigcup_{i\in I}U_i
$$

such that $\Gamma(U_i,\mathcal M)$ is a finitely generated module over $\Gamma(U_i,\mathcal O_X)$.

> **Editorial note - terminology outside the noetherian case.** This is the source's convention for “coherent”. On a locally noetherian scheme it agrees with the usual definition. On an arbitrary scheme the displayed condition means quasicoherent of finite type; usual coherence additionally imposes finite-type relations, so the two notions must not be identified without further hypotheses.

On an affine scheme $\operatorname{Spek}(R)$, quasicoherent modules and $R$-modules correspond. In particular, on an affine scheme a quasicoherent module $\mathcal M$ has “many” global sections, which can be used to understand and reconstruct $\mathcal M$. This is by no means true in general for quasicoherent sheaves on nonaffine schemes, and in particular it often fails on projective schemes. There it is even common for a complicated quasicoherent module to have the zero module as its global evaluation.

In such a situation, suitable invertible sheaves can be used to “twist” the module so that the twisted version has global sections. The following general theorem provides guidance. Note that elements

$$
g\in\Gamma(X,\mathcal L),
\qquad
s\in\Gamma(X,\mathcal M),
$$

with $\mathcal L$ invertible, define via sheafification elements

$$
g^ns\in\Gamma(X,\mathcal L^n\otimes\mathcal M),
$$

where $\mathcal L^n$ denotes the $n$th tensor power of $\mathcal L$.

<!-- upstream_entity: Noethersches Schema/Quasikohärente Garbe/Invertierbare Garbe/Invertierbarkeitsort/Globale Ausdehnung/Fakt -->

### Theorem 14.13: global extension from the invertibility locus {#br-bgk-2019-l14-thm-01}

Let $\mathcal M$ be a quasicoherent $\mathcal O_X$-module on a noetherian scheme $(X,\mathcal O_X)$. Let $\mathcal L$ be an invertible sheaf on $X$ and

$$
g\in\Gamma(X,\mathcal L)
$$

a global section with invertibility locus $X_g$. Then the following assertions hold.

1. For a global section $r\in\Gamma(X,\mathcal M)$ with $r|_{X_g}=0$, there is an $m\in\mathbb N$ such that

   $$
   g^mr=0
   $$

   in $\Gamma(X,\mathcal L^m\otimes\mathcal M)$.

2. For a section $s\in\Gamma(X_g,\mathcal M)$, there is an $n\in\mathbb N$ such that

   $$
   g^ns\in\Gamma(X_g,\mathcal L^n\otimes\mathcal M)
   $$

   comes from a global section in $\Gamma(X,\mathcal L^n\otimes\mathcal M)$.

#### Proof {#br-bgk-2019-l14-thm-01-proof}

Choose a finite affine open cover

$$
X=\bigcup_{i\in I}U_i
$$

such that the restriction of $\mathcal L$ to every $U_i$ is trivial. Consider

$$
V_i=X_g\cap U_i\subseteq U_i,
$$

an open subset of the affine scheme $U_i=\operatorname{Spek}(R_i)$. There is an $R_i$-module $M_i$ with

$$
\mathcal M|_{U_i}=\widetilde{M_i}.
$$

Under the isomorphism $\mathcal L|_{U_i}\cong\mathcal O_{U_i}$, the restriction of $g$ to $U_i$ corresponds to a function $f_i\in R_i$, and its invertibility locus satisfies

$$
X_g\cap U_i=D(f_i).
$$

Thus,

$$
\Gamma(V_i,\mathcal M)\cong(M_i)_{f_i}.
$$

1. Let $r_i=r|_{U_i}\in M_i$. By assumption, its restriction to $V_i$ is zero, so there is an $m_i\in\mathbb N$ with

   $$
   f_i^{m_i}r_i=0
   $$

   in $M_i$; the equation continues to hold for every larger exponent. Translated into $\mathcal L^{m_i}\otimes\mathcal M$, this means that the global element $g^{m_i}r$ restricts to zero on $U_i$. Hence, setting

   $$
   m=\max(m_i\mid i\in I),
   $$

   we obtain an $m$ such that $g^mr$ vanishes on every $U_i$. By the sheaf property, $g^mr=0$ on $X$.

2. The given section $s\in\Gamma(X_g,\mathcal M)$ yields, by restriction, sections

   $$
   s_i\in\Gamma(V_i,\mathcal M)
   =\Gamma(D(f_i),\widetilde{M_i})=(M_i)_{f_i}.
   $$

   Thus

   $$
   s_i=\frac{t_i}{f_i^{\ell_i}}
   $$

   with $t_i\in M_i$. The exponents $\ell_i$ can be increased, so we may assume that such a representation holds for every $i$ with a common exponent $\ell$. This means that the restriction of

   $$
   g^\ell s\in\Gamma(X_g,\mathcal L^\ell\otimes\mathcal M)
   $$

   to $X_g\cap U_i$ comes from an element

   $$
   t_i\in\Gamma(U_i,\mathcal L^\ell\otimes\mathcal M).
   $$

   In general, these elements $t_i$ are not yet compatible. However, the restriction of $t_i-t_j$ to $X_g\cap U_i\cap U_j$ is zero. Applying the first part to

   $$
   X_g\cap U_i\cap U_j\subseteq U_i\cap U_j,
   $$

   gives an $m_{ij}$ such that

   $$
   g^{m_{ij}}(t_i-t_j)=0
   $$

   in $\Gamma(U_i\cap U_j,\mathcal L^{\ell+m_{ij}}\otimes\mathcal M)$. Multiply the entire situation by $g^m$, where $m$ is the maximum of all the $m_{ij}$. The local elements are then compatible, so for $n=\ell+m$ we obtain a global extension of $g^ns$.

> **Editorial note - proof notation.** In part 1 the source introduces $n_i$ but uses $m_i$ throughout the equation and maximum; this edition consistently uses $m_i$. In part 2 the source writes $\Gamma(D(f_i),M_i)$ for sections of the associated sheaf; the tilde is made explicit here. Neither correction changes the argument.
