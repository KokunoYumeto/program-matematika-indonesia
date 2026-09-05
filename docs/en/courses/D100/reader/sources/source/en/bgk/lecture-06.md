---
title: "Lecture 6 - Exactness, Global Sections, and Pullback and Pushforward of Sheaves"
stable_id: br-bgk-2019-l06
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 6"
upstream_pageid: 109010
upstream_revid: 1003728
upstream_timestamp: "2025-06-08T15:29:32Z"
upstream_mediawiki_sha1: 0dfea13421076e8f6486836e9fc799822bf52053
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003728"
authority_manifest: authority/wikiversity-bgk/unit-06/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 69a10e682e853c6f386afbc68438605846e5096220b21bd1e827c07633a79244
lecture_xml: authority/wikiversity-bgk/unit-06/lecture-06.xml
lecture_xml_sha256: 8d60efeb0563ba0268a61940d94a71c8fd489c2e3d6e83cc61c785e75cdb1d54
lecture_expanded_tex: authority/wikiversity-bgk/unit-06/lecture-06-expanded.tex
lecture_expanded_tex_sha256: 0bdf28cb69d063b1782b7b42eb2212241e109f66ba382368dcd8e782d5ae829d
official_pdf: authority/artifacts/bgk-lecture-06-official.pdf
official_pdf_sha256: 55fbef2b5d9eae950ac7ab064a8029f2e2932c49280a98a4a7ec6ed16262c75d
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 6: Exactness, Global Sections, and Pullback and Pushforward of Sheaves {#br-bgk-2019-l06}

## Exactness {#br-bgk-2019-l06-s01}

### Definition 6.1: complex of sheaves {#br-bgk-2019-l06-def-01}

Let $X$ be a topological space, let $\mathcal F_n$ be sheaves of commutative
groups on $X$, and let

$$
\varphi_n:\mathcal F_{n-1}\longrightarrow\mathcal F_n
$$

be sheaf homomorphisms. We say that these form a *complex of sheaves* if

$$
\operatorname{im}\varphi_n\subseteq\ker\varphi_{n+1}
$$

holds.

### Definition 6.2: exactness {#br-bgk-2019-l06-def-02}

Let $X$ be a topological space and let $\mathcal F_\bullet$ be a complex of
sheaves of commutative groups on $X$. The complex is called *exact* if

$$
\operatorname{im}\varphi_n=\ker\varphi_{n+1}
$$

for every $n\in\mathbb Z$.

### Lemma 6.3: stalkwise characterisation of exactness {#br-bgk-2019-l06-lem-01}

Let $X$ be a topological space and let

$$
\mathcal F\longrightarrow\mathcal G\longrightarrow\mathcal H
$$

be a complex of sheaves of commutative groups on $X$. This complex is exact
if and only if, for every point $P\in X$, the complex of stalks

$$
\mathcal F_P\longrightarrow\mathcal G_P\longrightarrow\mathcal H_P
$$

is exact.

#### Proof {#br-bgk-2019-l06-lem-01-proof}

Denote the maps in question by

$$
\mathcal F\xrightarrow{\alpha}\mathcal G\xrightarrow{\beta}\mathcal H.
$$

By Corollary 4.11, this is a complex of sheaves if and only if all the
induced maps on stalks form complexes. Suppose the complex is exact, so that

$$
\operatorname{im}\alpha=\ker\beta.
$$

Fix $P\in X$ and take $s\in\mathcal G_P$ with
$\beta_P(s)=0$. There is an open neighbourhood $U$ of $P$ on which $s$ is
represented by a section $s$, and a smaller open neighbourhood

$$
P\in V\subseteq U
$$

such that

$$
\beta_V(s|_V)=0.
$$

The element $s\in\mathcal G(V)$ (we again denote the restriction by $s$)
belongs to the kernel of $\beta_V$, and hence to the sheaf image of
$\alpha$. Thus there is an open neighbourhood

$$
P\in W\subseteq V
$$

on which $s$ lies in the image of

$$
\alpha_W:\mathcal F(W)\longrightarrow\mathcal G(W).
$$

Consequently, the germ $s$ lies in the image of $\alpha_P$. This proves
exactness of the complex of stalks.

> **Edition note — converse of Lemma 6.3.** The frozen source proves only
> the forward implication. For completeness, the converse added in this
> edition is as follows: if $s\in(\ker\beta)(U)$, stalkwise exactness gives
> a germ lifting $s_P$ at every $P\in U$. Representing that germ and then
> shrinking its neighbourhood makes its image equal to $s$ there. Thus
> $s$ belongs locally to the image of $\alpha$, hence belongs to its sheaf
> image. The opposite inclusion follows from the complex condition.

### Definition 6.4: short exact sequence {#br-bgk-2019-l06-def-03}

An exact complex

$$
0\longrightarrow\mathcal F\longrightarrow\mathcal G\longrightarrow
\mathcal H\longrightarrow0
$$

of sheaves of commutative groups on a topological space $X$ is called a
*short exact sequence*.

In particular, the first map is injective and the last map is surjective
as a map of sheaves (that is, locally surjective at every point).

### Lemma 6.5: a sheaf sequence from a sequence of topological groups {#br-bgk-2019-l06-lem-02}

Let

$$
0\longrightarrow F\longrightarrow G\longrightarrow H\longrightarrow0
$$

be a short exact sequence of commutative topological groups, with continuous
group homomorphisms. Suppose that $F$ carries the topology induced by $G$,
and that the surjection

$$
p:G\longrightarrow H
$$

has the following property: for every $h\in H$ there is an open
neighbourhood

$$
h\in W\subseteq H
$$

and a continuous section of $p$ over $W$. Then, for every topological space
$X$, the corresponding sequence of sheaves of continuous maps,

$$
0\longrightarrow C^0(-,F)\longrightarrow C^0(-,G)\longrightarrow
C^0(-,H)\longrightarrow0,
$$

is also exact.

#### Proof {#br-bgk-2019-l06-lem-02-proof}

Clearly this is a complex of sheaves of commutative groups on $X$.
Injectivity on the left is also clear. For exactness in the middle, let
$U\subseteq X$ be open and let $\varphi:U\to G$ be continuous with
$p\circ\varphi$ the zero map. The image of $\varphi$ lies in $F$; since $F$
carries the topology induced by $G$, the map $\varphi:U\to F$ is continuous
as well.

For surjectivity as a sheaf map on the right, take a point $P\in X$ and a
continuous map $\psi:V\to H$ defined on an open neighbourhood $V$ of $P$.
Write $\psi(P)=h$. By hypothesis, there is an open neighbourhood

$$
h\in W\subseteq H
$$

and a section $s:W\to G$ with

$$
p\circ s=\operatorname{Id}_W.
$$

Set

$$
U:=V\cap\psi^{-1}(W).
$$

Then $s\circ\psi$, restricted to $U$, is a continuous $G$-valued section
that is mapped to $\psi$ by $p$.

### Example 6.6: the exponential sequence {#br-bgk-2019-l06-exa-01}

Consider the short exact sequence

$$
0\longrightarrow2\pi\mathrm i\,\mathbb Z\longrightarrow\mathbb C
\xrightarrow{\operatorname{exp}}\mathbb C^{\times}
\longrightarrow0
$$

of topological groups. Exactness in the middle follows from Theorem 21.5
(Analysis (Osnabrück 2021--2023), part (2)); the homomorphism property follows
from the functional equation of the exponential function. By Theorem 21.6
(Analysis (Osnabrück 2021--2023)), the complex exponential function maps
surjectively onto $\mathbb C\setminus\{0\}$ and is a covering map (see
Example 21.3, Funktionentheorie (Osnabrück 2023--2024)). Since a logarithm
exists locally, the hypotheses of Lemma 6.5 are satisfied. Thus, for every
topological space $X$, we obtain a short exact sequence of sheaves

$$
0\longrightarrow C^0(-,\mathbb Z)\longrightarrow C^0(-,\mathbb C)
\longrightarrow C^0(-,\mathbb C^{\times})\longrightarrow0.
$$

This is called the *continuous complex exponential sequence*. On the left
is the locally constant sheaf with values in $\mathbb Z$; in the middle is
the sheaf of complex-valued continuous functions; and on the right is the
sheaf of nowhere-zero complex-valued continuous functions. If
$X=\mathbb C^{\times}$, the induced map on global sections at the right is
not surjective, since the identity function is not in its image.

> **Edition note — dates in the source references.** Although this course
> is entitled 2019--2020, the two source surfaces differ: the terminal PDF
> cites Analysis (Osnabrück 2014--2016), whereas the current semantic TeX
> witness cites Analysis 2021--2023 and Funktionentheorie 2023--2024. All
> dates are retained as identifiers of their respective sources, without
> implying that the editions have been harmonised.

## Global sections {#br-bgk-2019-l06-s02}

### Lemma 6.7: taking global sections preserves complexes {#br-bgk-2019-l06-lem-03}

Let $X$ be a topological space and let

$$
\mathcal F\xrightarrow{d}\mathcal G\xrightarrow{d'}\mathcal H
$$

be a complex of homomorphisms of sheaves of commutative groups on $X$. Then

$$
\Gamma(X,\mathcal F)\longrightarrow\Gamma(X,\mathcal G)
\longrightarrow\Gamma(X,\mathcal H)
$$

is also a complex.

#### Proof {#br-bgk-2019-l06-lem-03-proof}

The hypothesis says precisely that $d'\circ d$ is the zero map.
Consequently, its evaluation on global sections is also the zero map.

### Lemma 6.8: taking global sections is left exact {#br-bgk-2019-l06-lem-04}

Let $X$ be a topological space and let

$$
0\longrightarrow\mathcal F\xrightarrow{d}\mathcal G
\xrightarrow{d'}\mathcal H
$$

be an exact complex of homomorphisms of sheaves of commutative groups on
$X$. Then

$$
0\longrightarrow\Gamma(X,\mathcal F)\longrightarrow\Gamma(X,\mathcal G)
\longrightarrow\Gamma(X,\mathcal H)
$$

is also exact.

#### Proof {#br-bgk-2019-l06-lem-04-proof}

By Lemma 6.7, the sequence of global sections is a complex. Exactness means
that, at every point $P\in X$,

$$
0\longrightarrow\mathcal F_P\longrightarrow\mathcal G_P
\longrightarrow\mathcal H_P
$$

is exact on stalks.

Take $s\in\Gamma(X,\mathcal F)$ with $d(s)=0$ in
$\Gamma(X,\mathcal G)$. Then $d(s)_P=0$ at every point. Hence $s_P=0$ for
every $P$, and Lemma 4.4 gives $s=0$. The map on the left is injective.

Next, take $t\in\Gamma(X,\mathcal G)$ with
$d'(t)=0$ in $\Gamma(X,\mathcal H)$. Exactness on stalks means that, for
every $P$, the germ $t_P$ belongs to $\mathcal F_P$. By Exercise 5.5, this
implies that $t$ itself is a section of $\mathcal F$.

Thus taking global sections of sheaves of abelian groups is an *additive
covariant left exact functor*.

## Pullback and pushforward {#br-bgk-2019-l06-s03}

So far we have considered sheaves and their relationships only on a fixed
topological space. We now consider topological spaces connected by a
continuous map.

### Definition 6.9: pushforward presheaf {#br-bgk-2019-l06-def-04}

For a continuous map

$$
\varphi:X\longrightarrow Y
$$

and a presheaf $\mathcal F$ on $X$, the presheaf on $Y$ given on each open
set $U\subseteq Y$ by

$$
(\varphi_*\mathcal F)(U):=\mathcal F\bigl(\varphi^{-1}(U)\bigr)
$$

is called the *pushforward presheaf* of $\mathcal F$ along $\varphi$.

If $V\subseteq W$ are open, then

$$
\varphi^{-1}(V)\subseteq\varphi^{-1}(W),
$$

so there are natural restriction maps, and this does indeed define a
presheaf.

### Lemma 6.10: the pushforward of a sheaf is a sheaf {#br-bgk-2019-l06-lem-05}

For a continuous map $\varphi:X\to Y$ and a sheaf $\mathcal F$ on $X$, the
pushforward presheaf $\varphi_*\mathcal F$ is a sheaf.

#### Proof {#br-bgk-2019-l06-lem-05-proof}

Let

$$
V=\bigcup_{i\in I}V_i
$$

be an open cover of an open set $V\subseteq Y$. Then
$\varphi^{-1}(V_i)$, for $i\in I$, form an open cover of
$\varphi^{-1}(V)$. If $s,t\in(\varphi_*\mathcal F)(V)$ satisfy

$$
s|_{V_i\cap V_j}=t|_{V_i\cap V_j}\qquad(i,j\in I),
$$

then $s,t\in\mathcal F(\varphi^{-1}(V))$, and, interpreted on $X$,

$$
\begin{aligned}
s|_{\varphi^{-1}(V_i)\cap\varphi^{-1}(V_j)}
&=s|_{\varphi^{-1}(V_i\cap V_j)}\\
&=t|_{\varphi^{-1}(V_i\cap V_j)}\\
&=t|_{\varphi^{-1}(V_i)\cap\varphi^{-1}(V_j)}.
\end{aligned}
$$

The first sheaf axiom for $\mathcal F$ gives $s=t$ in
$\mathcal F(\varphi^{-1}(V))$, and hence in $(\varphi_*\mathcal F)(V)$.

Now take sections $s_i\in(\varphi_*\mathcal F)(V_i)$ with

$$
s_i|_{V_i\cap V_j}=s_j|_{V_i\cap V_j}\qquad(i,j\in I).
$$

Interpreted on $X$, these are sections
$s_i\in\mathcal F(\varphi^{-1}(V_i))$ compatible on all intersections.
The gluing axiom for $\mathcal F$ yields a section in

$$
\mathcal F(\varphi^{-1}(V))=(\varphi_*\mathcal F)(V).
$$

> **Edition note — the type of the sections in the proof of Lemma 6.10.**
> The source writes $s_i\in\mathcal F(V_i)$, although $\mathcal F$ is a
> presheaf on $X$ and $V_i\subseteq Y$. The well-typed expression is
> $s_i\in\mathcal F(\varphi^{-1}(V_i))$; this is used above, and the source
> discrepancy is recorded rather than concealed.

### Lemma 6.11: stalks of the pushforward presheaf {#br-bgk-2019-l06-lem-06}

For a continuous map $\varphi:X\to Y$, a point $Q\in Y$, and a presheaf
$\mathcal F$ on $X$, the stalk of the pushforward presheaf
$\varphi_*\mathcal F$ at $Q$ is

$$
\operatorname*{colim}_{\substack{V\subseteq Y,\;V\text{ open}\\Q\in V}}
\mathcal F(\varphi^{-1}(V))
=
\operatorname*{colim}_{\substack{U\subseteq X,\;U\text{ open}\\
\exists\text{ open neighbourhood }V\ni Q:\,\varphi^{-1}(V)\subseteq U}}
\mathcal F(U).
$$

> **Edition note — the neighbourhood index in the source.** In the second
> colimit index, the source writes “there is an open neighbourhood
> $Q\in V$”; this is read as “there is an open neighbourhood $V\ni Q$”.
> The translation displays the explicit, well-typed formulation, including
> the implicit requirement that $U$ be open, since $\mathcal F(U)$ is
> defined only for open sets.

See Exercise 6.5. Thus the stalk of the pushforward presheaf is a stalk of
the original presheaf at a filter (namely, the inverse-image filter of the
neighbourhood filter $\mathcal U(Q)$), but in general not at a point.

### Definition 6.12: pullback presheaf {#br-bgk-2019-l06-def-05}

For a continuous map $\varphi:X\to Y$ and a presheaf $\mathcal G$ on $Y$,
the presheaf on $X$ given on an open set $U\subseteq X$ by

$$
U\longmapsto
\operatorname*{colim}_{\substack{V\subseteq Y,\;V\text{ open}\\U\subseteq\varphi^{-1}(V)}}
\mathcal G(V)
$$

is called the *pullback presheaf* of $\mathcal G$ along $\varphi$.

> **Edition note — the source colimit display.** The expanded German TeX
> interchanges the index and the term, placing $\mathcal G(V)$ beneath
> $\operatorname{colim}$. The formula above restores their intended roles
> and explicitly restricts $V$ to open sets, as required for a presheaf.

### Definition 6.13: pullback sheaf {#br-bgk-2019-l06-def-06}

For a continuous map $\varphi:X\to Y$ and a sheaf $\mathcal G$ on $Y$, the
*pullback sheaf* is the sheafification of the pullback presheaf. It is
denoted by

$$
\varphi^{-1}\mathcal G.
$$

### Lemma 6.14: stalks of the pullback sheaf {#br-bgk-2019-l06-lem-07}

For a continuous map $\varphi:X\to Y$ and a sheaf $\mathcal G$ on $Y$, the
stalk of the pullback sheaf at a point $P\in X$ is equal to the stalk of
$\mathcal G$ at $\varphi(P)$.

See Exercise 6.6.
