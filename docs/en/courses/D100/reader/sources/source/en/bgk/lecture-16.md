---
title: "Lecture 16 - Locally Free Sheaves"
stable_id: br-bgk-2019-l16
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 16"
upstream_pageid: 109020
upstream_revid: 1003746
upstream_timestamp: "2025-06-08T15:43:34Z"
upstream_mediawiki_sha1: 2be1b6927bfef758198ff94dd1e90dc52c4630f2
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003746"
authority_manifest: null
authority_manifest_status: "Not published by the capture process; the audit binding uses the exact individual surfaces below."
lecture_api: authority/wikiversity-bgk/unit-16/lecture-16-api.json
lecture_api_sha256: 8fbe4645d52075558a760a25948f289b3e994473e2e858e190baf2c5fab4a8d3
lecture_xml: authority/wikiversity-bgk/unit-16/lecture-16.xml
lecture_xml_sha256: 916136735d3b6f88ae5f92ef73b32bc60d672dbd04883e7d2f1dccc14e786e85
lecture_expanded_tex: authority/wikiversity-bgk/unit-16/lecture-16-expanded.tex
lecture_expanded_tex_sha256: a0cdb7121044eb271b5fed03fe82f84ce95174e4146afcd744547fe68d1dd276
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_pages: "138-145"
media_credits: source/id-ID/media-credits-bgk-unit-16.md
license: "Semantic course text and this translation: CC BY-SA 4.0. Commons metadata for the official course PDF states CC BY-SA 4.0, whereas page 265 of the PDF carries a CC BY-SA 3.0 notice; both are retained without a blanket relicensing claim."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
source_binding_status: "verified_individual_surfaces_and_exact_course_pdf_without_unit_manifest"
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 16: Locally Free Sheaves {#br-bgk-2019-l16}

## Locally free sheaves {#br-bgk-2019-l16-s01}

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Definition -->

### Definition 16.1: locally free sheaves {#br-bgk-2019-l16-def-01}

An $\mathcal O_X$-module $\mathcal F$ on a ringed space $X$ is called *locally free* of *rank* $r$ if there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

and $\mathcal O_{U_i}$-module isomorphisms

$$
\mathcal F|_{U_i}\cong(\mathcal O_{U_i})^r
$$

for every $i\in I$.

For $r=1$, we obtain the invertible sheaves: these are precisely the locally free sheaves of rank $1$. The simplest locally free sheaves are the *free sheaves*

$$
\mathcal O_X^r,
\qquad r\in\mathbb N.
$$

> **Editorial note — the rank variable in the source.** Both the frozen semantic page and the official course PDF print “rank $r$” in the sentence after setting $r=1$. This edition states the mathematical consequence, namely rank $1$, and explicitly records the change.

By definition, a locally free sheaf is free locally, that is, on a cover by open sets. Thus free sheaves and locally free sheaves cannot be distinguished locally. Locally free sheaves therefore reflect global properties of the ringed space $X$.

We consider locally free sheaves on schemes, where there are close connections with projective and flat modules. In particular, locally free sheaves are coherent modules. Over a local ring, all locally free sheaves are free, because its spectrum has only one closed point, whose only open neighbourhood is the whole space. However, if we consider the punctured spectrum

$$
U=D(\mathfrak m)=\operatorname{Spek}(R)\setminus\{\mathfrak m\}
$$

of a local ring, there are generally many nontrivial (nonfree) locally free sheaves on it, reflecting properties of the local ring, or of the singularity. Since every scheme is covered by affine schemes, we must first understand locally free sheaves on an affine scheme.

<!-- upstream_entity: Endlich erzeugter Modul/Lokal freie Garbe/Charakterisierungen von lokal/Fakt -->

### Theorem 16.2: local characterisations of local freeness {#br-bgk-2019-l16-thm-01}

Let $R$ be a commutative Noetherian ring, let $M$ be a finitely generated $R$-module, and let $r\in\mathbb N$. The following properties are equivalent.

1. The localisations $M_{\mathfrak p}$ are free of rank $r$ for every prime ideal $\mathfrak p\in\operatorname{Spek}(R)$.
2. The localisations $M_{\mathfrak m}$ are free of rank $r$ for every maximal ideal $\mathfrak m$ of $R$.
3. There are elements $f_1,\ldots,f_k\in R$ generating the unit ideal such that the localisations $M_{f_j}$ are free of rank $r$ for every $j=1,\ldots,k$.
4. The coherent sheaf $\widetilde M$ associated with $M$ on $\operatorname{Spek}(R)$ is locally free of rank $r$.

#### Proof {#br-bgk-2019-l16-thm-01-proof}

$(1)\Rightarrow(2)$. This is a special case.

$(2)\Rightarrow(3)$. Fix a maximal ideal $\mathfrak m$. By assumption, there is an $R_{\mathfrak m}$-module isomorphism

$$
\varphi:(R_{\mathfrak m})^r\longrightarrow M_{\mathfrak m}.
$$

Write the image of the $i$th standard vector $e_i$ as

$$
\varphi(e_i)=\frac{m_i}{g_i},
$$

with $m_i\in M$ and $g_i\in R\setminus\mathfrak m$. Let $g=g_1\cdots g_r$ be the product of the denominators. We consider the situation over $D(g)$. The isomorphism $\varphi$ is defined over $D(g)$, that is, on $R_g$, so we have an $R_g$-module homomorphism

$$
\psi:(R_g)^r\longrightarrow M_g
$$

which induces the isomorphism $\varphi$ after localisation at $\mathfrak m$. In general, however, $\psi$ need not be an isomorphism.

Let $v_1,\ldots,v_s$ be a generating system for the module $M$. Since $\psi$ induces a surjection over $R_{\mathfrak m}$, there are elements

$$
u_j=\frac{a_j}{h_j}\in(R_{\mathfrak m})^r
$$

mapping to $v_j$. The denominators $h_j$ do not belong to $\mathfrak m$. We can therefore replace $g$ by $h=gh_1\cdots h_s$ and obtain

$$
\psi:(R_h)^r\longrightarrow M_h.
$$

Here there are elements $u_j\in(R_h)^r$ such that $\psi(u_j)$ and the generators $v_j$ have the same restrictions in $M_{\mathfrak m}$. This means that there are elements $p_j\notin\mathfrak m$ with

$$
p_j\psi(u_j)=p_jv_j
$$

in $M_h$. Replacing $h$ by $p=hp_1\cdots p_s$ makes $\psi$ surjective as well.

> **Editorial note — the relation symbol in the source.** The source prints $u_j=(R_h)^r$ in the sentence above. Since $u_j$ is an element and $(R_h)^r$ is the module containing it, this edition uses the membership relation $u_j\in(R_h)^r$ and explicitly records the change.

Let $N$ be the kernel of this new $\psi$. Since $\varphi$ is injective, $N_{\mathfrak m}=0$. As $R$ is Noetherian, Lemma 23.2 (Commutative Algebra) implies that $N$ is finitely generated. Hence there is again an element $f\notin\mathfrak m$ with $N_f=0$. Shrinking the open set once more gives an isomorphism

$$
\psi:(R_f)^r\longrightarrow M_f
$$

for some $f\notin\mathfrak m$.

Thus every maximal ideal $\mathfrak m$ has an open neighbourhood

$$
\mathfrak m\in D(f_{\mathfrak m})
$$

such that $M_{f_{\mathfrak m}}$ is free of rank $r$. Consequently,

$$
\bigcup_{\mathfrak m\text{ maximal ideal}}D(f_{\mathfrak m})
$$

contains all maximal ideals and also all prime ideals, and hence is an open cover of $\operatorname{Spek}(R)$. By Proposition 8.4 (4), the ideal

$$
(f_{\mathfrak m}:\mathfrak m\text{ maximal ideal})
$$

is the unit ideal, and it is already generated by finitely many of the elements $f_{\mathfrak m}$.

$(3)\Rightarrow(4)$. Since the elements generate the unit ideal, the open sets $D(f_j)$, $j=1,\ldots,k$, cover $\operatorname{Spek}(R)$. Since the $M_{f_j}$ are free $R_{f_j}$-modules of rank $r$, there are $\mathcal O_X|_{D(f_j)}$-module isomorphisms

$$
\widetilde M|_{D(f_j)}
\cong\widetilde{(R_{f_j})^r}
\cong\mathcal O_{D(f_j)}^r.
$$

Thus $\widetilde M$ is locally free.

$(4)\Rightarrow(1)$. Let $\mathfrak p\in\operatorname{Spek}(R)$ be a prime ideal. Local freeness means that there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

such that the $\widetilde M|_{U_i}$ are free of rank $r$. Hence there is an index $i$ with $\mathfrak p\in U_i$. Passing to a possibly smaller open neighbourhood, we may take $U_i=D(f)$ with $f\notin\mathfrak p$. There,

$$
\widetilde{M_f}\cong\widetilde M|_{D(f)}
$$

is free of rank $r$. Its localisation $M_{\mathfrak p}$ is therefore also free of rank $r$.

The example in Exercise 14.7 shows that, over a non-Noetherian ring $R$, there may be a module $M$ with

$$
M_{\mathfrak p}=R_{\mathfrak p}
$$

without this isomorphism extending to an open neighbourhood.

We now relate locally free modules to projective modules.

<!-- upstream_entity: Kommutativer Ring/Projektiv/Universell/Definition -->

### Definition 16.3: projective modules {#br-bgk-2019-l16-def-02}

Let $R$ be a commutative ring and let $M$ be an $R$-module. The module $M$ is called *projective* if, for every surjective $R$-module homomorphism

$$
\theta:A\longrightarrow B
$$

and every module homomorphism

$$
\varphi:M\longrightarrow B,
$$

there is a module homomorphism

$$
\psi:M\longrightarrow A
$$

with

$$
\varphi=\theta\circ\psi.
$$

A module is projective if and only if it is a direct summand of a free module.

<!-- upstream_entity: Kommutativer Ring/Lokal/Projektiver Modul/Frei/Fakt -->

### Lemma 16.4: finitely generated projective modules over a local ring {#br-bgk-2019-l16-lem-01}

Let $R$ be a commutative local ring and let $M$ be a finitely generated $R$-module. Then $M$ is free if and only if $M$ is a projective module.

#### Proof {#br-bgk-2019-l16-lem-01-proof}

That free modules are projective was proved in Lemma 47.2 (Commutative Algebra). Thus suppose that $M$ is projective. Choose a minimal generating system $m_1,\ldots,m_n$ of $M$, and let

$$
p:R^n\longrightarrow M
$$

be the corresponding surjective module homomorphism. By minimality, the map

$$
(R/\mathfrak m)^n\longrightarrow M/\mathfrak mM
$$

is a bijective $R/\mathfrak m$-linear map. Since $M$ is projective, there is a module homomorphism $i:M\to R^n$ with

$$
p\circ i=\operatorname{Id}_M.
$$

Then

$$
R^n\cong M\oplus N,
$$

with $N=\operatorname{kern}p$, where we identify $M$ with $i(M)$. Now consider

$$
R^n\xrightarrow{\ \cong\ }M\oplus N\longrightarrow M
$$

and the induced $R/\mathfrak m$-linear maps

$$
(R/\mathfrak m)^n
\longrightarrow M/\mathfrak mM\oplus N/\mathfrak mN
\longrightarrow M/\mathfrak mM.
$$

Both the map on the left and the composite are bijective. Hence $N/\mathfrak mN=0$. Lemma 29.5 (Commutative Algebra) gives $N=0$, so $R^n=M$ is free.

<!-- upstream_entity: Kommutativer Ring/Noethersch/Lokal frei/Projektiv/Fakt -->

### Lemma 16.5: local freeness and projectivity {#br-bgk-2019-l16-lem-02}

Let $R$ be a commutative Noetherian ring and let $M$ be a finitely generated $R$-module. Then $M$ is locally free if and only if $M$ is a projective module.

#### Proof {#br-bgk-2019-l16-lem-02-proof}

One direction follows directly from Lemma 16.4, taking Exercise 16.16 into account. To prove the converse, let

$$
p:L\longrightarrow M
$$

be a surjective module homomorphism, with $L$ a finitely generated free $R$-module. We must show that there is a homomorphism $i:M\to L$ with

$$
p\circ i=\operatorname{Id}_M.
$$

In particular, this is assured if the natural homomorphism

$$
\operatorname{Hom}_R(M,L)
\longrightarrow\operatorname{Hom}_R(M,M),
\qquad
\varphi\longmapsto p\circ\varphi,
$$

is surjective, since then its image contains the identity. By Appendix Theorem 1.4, surjectivity can be tested locally. Under the given finiteness assumptions, the homomorphism modules satisfy

$$
(\operatorname{Hom}_R(M,L))_{\mathfrak p}
=\operatorname{Hom}_{R_{\mathfrak p}}
(M_{\mathfrak p},L_{\mathfrak p}).
$$

For every prime ideal $\mathfrak p$, surjectivity of the map

$$
\operatorname{Hom}_{R_{\mathfrak p}}
(M_{\mathfrak p},L_{\mathfrak p})
\longrightarrow
\operatorname{Hom}_{R_{\mathfrak p}}
(M_{\mathfrak p},M_{\mathfrak p})
$$

follows from the freeness of $M_{\mathfrak p}$ and Lemma 47.2 (Commutative Algebra).

> **Editorial note — unresolved reference.** Immediately before the localisation identity for homomorphism modules, the semantic source page displays the reference `Fakt *****` to `Nenneraufnahme/Homomorphismenmodul/Fakt`. This edition retains the mathematical identity without inventing an unavailable reference number.

The following theorem also holds; we do not prove it.

<!-- upstream_entity: Endlich erzeugter Modul/Lokal frei/Projektiv und flach/Fakt -->

### Theorem 16.6: locally free, projective, and flat {#br-bgk-2019-l16-thm-02}

Let $R$ be a commutative Noetherian ring and let $M$ be a finitely generated $R$-module. The following statements are equivalent.

1. $M$ is locally free.
2. $M$ is a projective module.
3. $M$ is a flat module.

The following theorem produces many locally free sheaves that are generally nontrivial.

<!-- upstream_entity: Schema/Lokal freie Garben/Surjektiv/Kern/Fakt -->

### Theorem 16.7: the kernel of a surjection of locally free sheaves {#br-bgk-2019-l16-thm-03}

Let $X$ be a Noetherian scheme and let

$$
\theta:\mathcal F\longrightarrow G
$$

be a surjective sheaf homomorphism between locally free sheaves on $X$. Then the kernel of $\theta$ is also locally free.

#### Proof {#br-bgk-2019-l16-thm-03-proof}

Since local freeness is a local property, we may assume at once that

$$
X=\operatorname{Spek}(R)
$$

is the affine scheme of a Noetherian ring $R$ and, after shrinking the open set further, that we have a surjective module homomorphism

$$
\theta:R^r\longrightarrow R^s.
$$

By Theorem 19.11 (Commutative Algebra), there is a map $\varphi:R^s\to R^r$ with

$$
\theta\circ\varphi=\operatorname{Id}_{R^s}.
$$

Thus there is a direct sum decomposition

$$
R^r=\operatorname{kern}\theta\oplus R^s,
$$

and $\theta$ is the projection onto the summand $R^s$. Hence, by Lemma 47.3 (Commutative Algebra), $\operatorname{kern}\theta$ is a projective $R$-module, and by Lemma 16.5 it is locally free.

<!-- upstream_entity: Affines Schema/Syzygiengarbe zu Idealerzeugern/Bemerkung -->

### Remark 16.8: syzygy sheaves {#br-bgk-2019-l16-rem-01}

Elements $f_1,\ldots,f_n\in R$ in a commutative ring $R$ give a module homomorphism

$$
R^n\longrightarrow R,
\qquad
e_i\longmapsto f_i.
$$

Its image is the ideal generated by the $f_i$. In particular, this map is surjective only if the $f_i$ generate the unit ideal. The corresponding homomorphism of sheaves of modules

$$
\mathcal O_X^n\longrightarrow\mathcal O_X
$$

is also generally not surjective, and its kernel is generally not locally free. However, consider the restriction of this sheaf homomorphism to the open subset

$$
U=\bigcup_{i=1}^nD(f_i),
$$

namely

$$
\mathcal O_U^n\longrightarrow\mathcal O_U.
$$

We obtain a surjective sheaf homomorphism, since on each $D(f_i)$ we have

$$
\frac{1}{f_i}e_i\longmapsto1.
$$

By Theorem 16.7, its kernel is a locally free sheaf on the quasiaffine scheme $U$. This kernel is denoted by

$$
\operatorname{Syz}(f_1,\ldots,f_n)
$$

and is called the *syzygy sheaf* or *kernel sheaf*. If $R$ is a local ring and the $f_i$ generate an ideal primary to the maximal ideal $\mathfrak m$ — in other words, the $f_i$ geometrically cut out the closed point — then the syzygy sheaf is a locally free sheaf on the punctured spectrum $D(\mathfrak m)$.

<!-- upstream_entity: Polynomring/Syzygiengarbe zu Variablen/Beispiel -->

### Example 16.9: the syzygy sheaf of the variables {#br-bgk-2019-l16-exm-01}

The variables

$$
X_1,\ldots,X_n\in K[X_1,\ldots,X_n]=R
$$

define the maximal ideal $(X_1,\ldots,X_n)$ and the short exact sequence

$$
0\longrightarrow\operatorname{Syz}(X_1,\ldots,X_n)
\longrightarrow R^n
\longrightarrow(X_1,\ldots,X_n)
\longrightarrow0
$$

of $R$-modules, where the $i$th standard vector $e_i$ is sent to $X_i$. By Lemma 14.9, this induces a short exact sequence of quasicoherent modules

$$
0\longrightarrow\widetilde{\operatorname{Syz}(X_1,\ldots,X_n)}
\longrightarrow\mathcal O_{\mathbb A_K^n}^n
\longrightarrow\widetilde{(X_1,\ldots,X_n)}
\longrightarrow0
$$

on affine space $\mathbb A_K^n$. The middle sheaf is free, whereas the sheaves on the left and right are not locally free, except for small $n$. If we restrict this sequence to the punctured spectrum

$$
U=D(X_1,\ldots,X_n)\subseteq\mathbb A_K^n,
$$

then, by Exercise 14.1, the maximal ideal on the right becomes the structure sheaf. We thus obtain the situation of Remark 16.8,

$$
0\longrightarrow\operatorname{Syz}(X_1,\ldots,X_n)
\longrightarrow\mathcal O_U^n
\longrightarrow\mathcal O_U
\longrightarrow0,
$$

with the locally free syzygy sheaf on the left. For $n=3$, this is the sheaf version of Example 1.2.

## Determinant sheaves {#br-bgk-2019-l16-s02}

<!-- upstream_entity: Lokal freie Garbe/Beringter Raum/Determinantengarbe/Definition -->

### Definition 16.10: determinant sheaves {#br-bgk-2019-l16-def-03}

Let $\mathcal G$ be a locally free sheaf of rank $r$ on the ringed space $(X,\mathcal O_X)$. The sheafification of the presheaf

$$
U\longmapsto\bigwedge^r\Gamma(U,\mathcal G)
$$

is called the *determinant sheaf* of $\mathcal G$. It is denoted by

$$
\operatorname{Det}\mathcal G.
$$

<!-- upstream_entity: Beringter Raum/Lokal freie Garben/Kurze exakte Sequenz/Determinantengarbe/Fakt -->

### Theorem 16.11: the determinant of a short exact sequence {#br-bgk-2019-l16-thm-04}

Let $(X,\mathcal O_X)$ be a ringed space and let

$$
0\longrightarrow\mathcal F
\longrightarrow\mathcal G
\longrightarrow\mathcal H
\longrightarrow0
$$

be a short exact sequence of locally free sheaves on $X$. Then there is a canonical isomorphism

$$
\operatorname{Det}G
\cong
\operatorname{Det}F\otimes\operatorname{Det}H.
$$

#### Proof {#br-bgk-2019-l16-thm-04-proof}

Let $r$ be the rank of $\mathcal F$ and $s$ the rank of $\mathcal H$. Consider open subsets $U\subseteq X$ on which all three sheaves are trivial and on which the sheaf surjection $\mathcal G\to\mathcal H$ has a section. Such open sets cover $X$. On each $U$ we have the situation

$$
0\longrightarrow\mathcal O_U^r
\longrightarrow\mathcal O_U^{r+s}
\longrightarrow\mathcal O_U^s
\longrightarrow0,
$$

and let

$$
\theta:\mathcal O_U^s\longrightarrow\mathcal O_U^{r+s}
$$

be a section. Define

$$
\Psi:
\bigwedge^r\mathcal O_U^r\times
\bigwedge^s\mathcal O_U^s
\longrightarrow
\bigwedge^{r+s}\mathcal O_U^{r+s}
$$

by

$$
\begin{aligned}
&\Psi(u_1\wedge\cdots\wedge u_r,
w_1\wedge\cdots\wedge w_s)\\
&\qquad:=u_1\wedge\cdots\wedge u_r
\wedge\theta(w_1)\wedge\cdots\wedge\theta(w_s).
\end{aligned}
$$

This map is independent of the chosen section $\theta$. For another section $\theta'$, the difference $\theta-\theta'$ takes values in $\mathcal F$. Then

$$
\begin{aligned}
&u_1\wedge\cdots\wedge u_r
\wedge\theta'(w_1)\wedge\cdots\wedge\theta'(w_s)\\
&=u_1\wedge\cdots\wedge u_r
\wedge(\theta(w_1)+u_1')\wedge\cdots\wedge(\theta(w_s)+u_s')\\
&=u_1\wedge\cdots\wedge u_r
\wedge\theta(w_1)\wedge\cdots\wedge\theta(w_s),
\end{aligned}
$$

because the $r+1$ vectors $u_1,\ldots,u_r,u_j'$ are always linearly dependent, so the corresponding wedge products are $0$. The map $\Psi$ is bilinear and therefore defines a linear map

$$
\widetilde\Psi:
\bigwedge^r\mathcal O_U^r\otimes
\bigwedge^s\mathcal O_U^s
\longrightarrow
\bigwedge^{r+s}\mathcal O_U^{r+s}.
$$

Since these maps are canonical, their restrictions to smaller open subsets always give the same map. By Corollary 4.10, they therefore glue to a sheaf homomorphism

$$
\bigwedge^r\mathcal F\otimes\bigwedge^s\mathcal H
\longrightarrow\bigwedge^{r+s}\mathcal G.
$$

By its explicit description, this homomorphism is locally an isomorphism, and hence, by Lemma 4.6, it is also a global isomorphism.

> **Editorial note — the surjection in the source proof.** The opening sentence of the source proof prints the surjection $\mathcal F\to\mathcal H$. The displayed exact sequence and the section $\theta:\mathcal O_U^s\to\mathcal O_U^{r+s}$ show that the surjection used in the construction is $\mathcal G\to\mathcal H$. This edition uses that surjection in the sentence above and explicitly records the correction.

<!-- upstream_entity: Beringter Raum/Lokal freie Garbe/Direkte Summe/Invertierbare Garben/Determinantengarbe/Fakt -->

### Corollary 16.12: the determinant of a direct sum of invertible sheaves {#br-bgk-2019-l16-cor-01}

Let $(X,\mathcal O_X)$ be a ringed space and let

$$
\mathcal F=\mathcal L_1\oplus\cdots\oplus\mathcal L_r
$$

be a direct sum of invertible sheaves. Then

$$
\operatorname{Det}F
\cong
\mathcal L_1\otimes\cdots\otimes\mathcal L_r.
$$

#### Proof {#br-bgk-2019-l16-cor-01-proof}

See Exercise 16.22.
