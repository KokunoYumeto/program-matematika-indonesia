---
title: "Lecture 30 - The Riemann–Roch theorem"
stable_id: br-bgk-2019-l30
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 30"
upstream_pageid: 109034
upstream_revid: 793624
upstream_timestamp: "2022-08-25T06:25:28Z"
upstream_mediawiki_sha1: 18925f7cd309e5a1f414208fad07124d8680ea79
source_url: "https://de.wikiversity.org/w/index.php?oldid=793624"
authority_manifest: authority/wikiversity-bgk/unit-30/UNIT_AUTHORITY_MANIFEST.json
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-30.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 30: The Riemann–Roch theorem {#br-bgk-2019-l30}

## The degree of twisted structure sheaves on plane curves {#br-bgk-2019-l30-s01}

### Lemma 30.1 {#br-bgk-2019-l30-lem-01}

Let

$$
C=V_+(F)\subseteq\mathbb P^2_K
$$

be a smooth projective plane curve of degree $d=\deg(F)$ over an algebraically closed field $K$. The restriction of $\mathcal O_{\mathbb P^2_K}(e)$ to $C$ has degree $de$.

> **Edition note (source).** The source uses the symbol $K$ throughout the statement but calls the base only “an algebraically closed field”. The missing name has been supplied above.

#### Proof {#br-bgk-2019-l30-lem-01-proof}

It suffices to take $e=1$, since pullback of sheaves is compatible with tensor products and, by Exercise 29.15, degree is additive under tensor products of invertible sheaves. Let

$$
G\in\Gamma(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(1))
=K[X,Y,Z]_1
$$

be a section which, as a polynomial in $K[X,Y,Z]$, is not a multiple of $F$. Then $G$ can also be regarded as a nonzero section in

$$
\Gamma(C,\mathcal O_{\mathbb P^2_K}(1)|_C)
=\Gamma(C,\mathcal O_C(1)).
$$

We must compute the degree of the divisor of zeros of $G$ on $C=V_+(F)$. Let $P=(a,b,c)\in V_+(F)$. The order of vanishing of a section of an invertible sheaf can be computed in an affine neighbourhood of the point. Without loss of generality, take $c=1$ and $P\in D_+(Z)$. The affine equation of the curve is the dehomogenisation $F'$ with respect to $Z$, and under the identification

$$
\mathcal O_{\mathbb P^2_K}|_{D_+(Z)}
\longrightarrow
\mathcal O_{\mathbb P^2_K}(1)|_{D_+(Z)},
\qquad 1\longmapsto Z,
$$

the section becomes the dehomogenisation $G'$ of $G$. The local ring of the curve is

$$
\mathcal O_{C,P}
=\left(K\!\left[\frac XZ,\frac YZ\right]/(F')\right)_{
(X/Z-a,\,Y/Z-b)}.
$$

By Lemma 21.9, the order of $G'$ in this ring equals the $K$-dimension of

$$
\mathcal O_{C,P}/(G')
=\left(K\!\left[\frac XZ,\frac YZ\right]/(F')\right)_{
(X/Z-a,\,Y/Z-b)}/(G')
=K\!\left[\frac XZ,\frac YZ\right]_{(X/Z-a,\,Y/Z-b)}/(F',G').
$$

This description is symmetric in $F$ and $G$. Hence the degree of the divisor of zeros of $G$ on $V_+(F)$ equals the degree of the divisor of zeros of $F$ on $V_+(G)=\mathbb P^1_K$. For a homogeneous polynomial of degree $d$ on the projective line, the sum of all orders of vanishing is $d$. $\square$

## Riemann–Roch for invertible sheaves {#br-bgk-2019-l30-s02}

Let $C=V_+(F)\subseteq\mathbb P^2_K$ be a smooth projective plane curve of degree $d$ over an algebraically closed field $K$, and let

$$
\mathcal L=\mathcal O_C(e)=\mathcal O_{\mathbb P^2_K}(e)|_C.
$$

> **Edition note (source).** The source omits smoothness here, although the subsequent appeal to the cohomological genus in Definition 29.1 and the transition to Riemann–Roch use a smooth projective curve. The missing hypothesis has been made explicit.

We want to compute the number of global sections of $\mathcal O_C(e)$. Consider the short exact sequence

$$
0\longrightarrow\mathcal O_{\mathbb P^2_K}(e-d)
\xrightarrow{\ F\ }
\mathcal O_{\mathbb P^2_K}(e)
\longrightarrow\mathcal O_C(e)\longrightarrow0
$$

on the projective plane and the beginning of the associated long exact cohomology sequence:

$$
0\longrightarrow
H^0(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(e-d))
\longrightarrow
H^0(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(e))
\longrightarrow
H^0(\mathbb P^2_K,\mathcal O_C(e))
\longrightarrow
H^1(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(e-d))=0.
$$

The equality on the right follows from Theorem 27.4. For $e\ge d$, the dimensions of the vector spaces involved can be computed directly using Exercise 12.4:

$$
\begin{aligned}
\dim_K H^0(\mathbb P^2_K,\mathcal O_C(e))
&=\dim_K H^0(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(e))
-\dim_K H^0(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(e-d))\\
&=\binom{e+2}{2}-\binom{e-d+2}{2}\\
&=\frac{(e+2)(e+1)-(e+2-d)(e+1-d)}{2}\\
&=\frac{2de+3d-d^2}{2}\\
&=de-\frac{(d-1)(d-2)}{2}+1.
\end{aligned}
$$

By Theorem 27.6, $H^0(\mathbb P^2_K,\mathcal O_C(e))=H^0(C,\mathcal O_C(e))$. By Lemma 30.1, $de$ is the degree of $\mathcal O_C(e)$, and by Theorem 29.5, $(d-1)(d-2)/2$ is the cohomological genus $g$ of the curve. Thus, for $e\ge d$,

$$
\dim_K H^0(C,\mathcal O_C(e))
=\deg(\mathcal O_C(e))-g+1.
$$

For $e<0$, this formula cannot be correct: the left-hand side is zero, while the right-hand side can be arbitrarily negative. The Riemann–Roch theorem shows that an analogous formula holds for an invertible sheaf $\mathcal L$ on a smooth projective curve $C$, but the left-hand side must be replaced by

$$
\dim_K H^0(C,\mathcal L)-\dim_K H^1(C,\mathcal L).
$$

Thus first cohomology appears as a correction term.

### Theorem 30.2: Riemann–Roch {#br-bgk-2019-l30-thm-02}

Let $C$ be a smooth irreducible projective curve of genus $g$ over an algebraically closed field $K$, and let $\mathcal L$ be an invertible sheaf on $C$. Then

$$
h^0(C,\mathcal L)-h^1(C,\mathcal L)
=\deg(\mathcal L)+1-g.
$$

#### Proof {#br-bgk-2019-l30-thm-02-proof}

The assertion is true for the structure sheaf. For a closed point $P\in C$, consider the short exact sequence

$$
0\longrightarrow\mathcal I_P
\longrightarrow\mathcal O_C
\longrightarrow\kappa(P)\longrightarrow0,
$$

where $\mathcal I_P=\mathcal O_C(-P)$ is the reduced invertible ideal sheaf of $P$, and $\kappa(P)$ is the structure sheaf of the point, regarded as a skyscraper sheaf on $C$. Tensoring this sequence with the invertible sheaf $\mathcal L$ gives

$$
0\longrightarrow\mathcal I_P\otimes\mathcal L
\longrightarrow\mathcal L
\longrightarrow\kappa(P)\otimes\mathcal L=\kappa(P)
\longrightarrow0.
$$

This sequence relates two invertible sheaves differing by the point $P$. The long exact cohomology sequence gives

$$
h^0(C,\mathcal L)-h^1(C,\mathcal L)
=h^0(C,\mathcal I_P\otimes\mathcal L)
-h^1(C,\mathcal I_P\otimes\mathcal L)+1,
$$

since $h^0(C,\kappa(P))=1$ and $h^1(C,\kappa(P))=0$, as its support is zero-dimensional. Since $\deg(\mathcal I_P)=-1$, we also have

$$
\deg(\mathcal L)=\deg(\mathcal I_P\otimes\mathcal L)+1.
$$

Thus the degree changes in exactly the same way as the difference between the dimensions of zeroth and first cohomology. The Riemann–Roch formula holds for $\mathcal L$ precisely when it holds for $\mathcal I_P\otimes\mathcal L$. By Corollary 22.11, every invertible sheaf on the curve has the form $\mathcal O_C(-D)$ for a Weil divisor $D$. Hence every invertible sheaf can be obtained from the structure sheaf by adding or removing finitely many points. The formula therefore holds for all invertible sheaves. $\square$

### Corollary 30.3 {#br-bgk-2019-l30-cor-03}

Let $C$ be a smooth irreducible projective curve of genus $g$ over an algebraically closed field $K$, and let $\mathcal L$ be an invertible sheaf on $C$. Then

$$
h^0(C,\mathcal L)\ge\deg(\mathcal L)+1-g.
$$

If the degree of $\mathcal L$ is at least the genus of the curve, then $\mathcal L$ has nontrivial global sections.

#### Proof {#br-bgk-2019-l30-cor-03-proof}

This follows immediately from Theorem 30.2. $\square$

### Corollary 30.4 {#br-bgk-2019-l30-cor-04}

Let $C$ be a smooth irreducible projective curve over an algebraically closed field $K$. For every closed point $P\in C$, there is a nonconstant rational function $f\in Q(C)$ defined outside $P$.

#### Proof {#br-bgk-2019-l30-cor-04-proof}

By Corollary 30.3, for sufficiently large $n$ the invertible sheaf $\mathcal O_C(nP)$ has nontrivial global sections, with arbitrarily many as $n$ grows. These correspond to rational functions on $C$ whose principal divisors are greater than or equal to $-nP$. Such a function can have a pole only at $P$, and is therefore defined on $C\setminus\{P\}$. Among these functions are nonconstant ones. $\square$

## Riemann–Roch for locally free sheaves {#br-bgk-2019-l30-s03}

We will generalise the Riemann–Roch theorem to locally free sheaves. First we must define the degree of a locally free sheaf.

### Definition 30.5 {#br-bgk-2019-l30-def-05}

Let $C$ be a smooth projective curve over an algebraically closed field $K$. The degree of a locally free sheaf $\mathcal G$ of rank $r$ on $C$ is defined as the degree of its determinant sheaf

$$
\bigwedge^r\mathcal G.
$$

### Theorem 30.6 {#br-bgk-2019-l30-thm-06}

Let $C$ be a smooth projective curve over an algebraically closed field $K$. The degree of locally free sheaves on $C$ is additive in short exact sequences.

#### Proof {#br-bgk-2019-l30-thm-06-proof}

This follows from Theorem 16.11. $\square$

Thus we have three additive invariants for locally free sheaves on a smooth projective curve: rank, degree, and Euler characteristic.

### Lemma 30.7 {#br-bgk-2019-l30-lem-07}

Let $C$ be a smooth irreducible projective curve over an algebraically closed field $K$. Every nonzero coherent ideal sheaf $\mathcal I\subseteq\mathcal O_C$ is invertible.

#### Proof {#br-bgk-2019-l30-lem-07-proof}

Since invertibility can be checked locally at the stalks $\mathcal O_{C,x}$, the assertion follows from the fact that these local rings are discrete valuation rings and hence principal ideal domains. $\square$

### Theorem 30.8 {#br-bgk-2019-l30-thm-08}

Let $C$ be a smooth irreducible projective curve over an algebraically closed field $K$, and let $\mathcal F$ be a locally free sheaf of rank $r$ on $C$. Then there is a filtration

$$
0=\mathcal F_0\subset\mathcal F_1\subset\cdots
\subset\mathcal F_{r-1}\subset\mathcal F_r=\mathcal F
$$

by locally free sheaves $\mathcal F_i$ such that the quotient sheaves $\mathcal F_{i+1}/\mathcal F_i$ are invertible for $0\le i<r$.

> **Edition note (source).** The source statement omits the symbol $r$ after “of rank” and prints the filtration starting with $0=\mathcal F_1$, giving a rank-$r$ sheaf only $r-1$ quotients. This edition displays the rank parameter $r$ and the indexing $\mathcal F_0,\ldots,\mathcal F_r$, consistently with the induction and the number of rank-one factors.

#### Proof {#br-bgk-2019-l30-thm-08-proof}

For sufficiently large $n$, Theorem 15.12 gives a nontrivial global section $s\in\Gamma(C,\mathcal F^*(n))$. This section corresponds to a nontrivial module homomorphism

$$
\mathcal O_C\longrightarrow\mathcal F^*(n).
$$

Dualising gives a nontrivial module homomorphism

$$
\mathcal F(-n)\longrightarrow\mathcal O_C.
$$

Its image is an ideal sheaf $\mathcal I\ne0$, which is invertible by Lemma 30.7 (cited as “Lemma 30.6” in the historical source PDF). Thus there is a surjective sheaf homomorphism

$$
\mathcal F(-n)\longrightarrow\mathcal I,
$$

and therefore a surjective sheaf homomorphism

$$
\mathcal F\longrightarrow
\mathcal I\otimes\mathcal O_C(n)=:\mathcal L.
$$

Since $\mathcal L$ is invertible, the kernel $\mathcal G\subset\mathcal F$ is locally free of smaller rank by Theorem 16.7. Applying this procedure inductively to $\mathcal F_{r-1}:=\mathcal G$ yields the filtration. $\square$

> **Edition note (source).** The historical source PDF proof refers to “Lemma 30.6” for invertibility of nonzero coherent ideal sheaves. That result is Lemma 30.7 in this lecture, as the frozen semantic proof now records; the historical printed number is preserved explicitly in the proof above.

### Theorem 30.9 {#br-bgk-2019-l30-thm-09}

Let $C$ be a smooth irreducible projective curve of genus $g$ over an algebraically closed field $K$, and let $\mathcal F$ be a locally free sheaf of rank $r$ on $C$. Then

$$
h^0(C,\mathcal F)-h^1(C,\mathcal F)
=\deg(\mathcal F)+r(1-g).
$$

#### Proof {#br-bgk-2019-l30-thm-09-proof}

We use induction on the rank $r$. The base case $r=1$ is Theorem 30.2. For a locally free sheaf of rank $r$, use the filtration with invertible quotients from Theorem 30.8,

$$
0=\mathcal F_0\subset\mathcal F_1\subset\cdots
\subset\mathcal F_{r-1}\subset\mathcal F_r.
$$

In particular, there is a short exact sequence

$$
0\longrightarrow\mathcal F_{r-1}
\longrightarrow\mathcal F
\longrightarrow\mathcal F_r/\mathcal F_{r-1}
\longrightarrow0.
$$

By the induction hypothesis, the Riemann–Roch formula holds for $\mathcal F_{r-1}$, and by Theorem 30.2 it holds for the invertible sheaf $\mathcal F_r/\mathcal F_{r-1}$. The Euler characteristic

$$
\chi(\mathcal G)=h^0(C,\mathcal G)-h^1(C,\mathcal G)
$$

is additive in short exact sequences by Lemma 27.9, and the degree of locally free sheaves is likewise additive in short exact sequences by Theorem 30.6 (cited as “Theorem 30.7” in the historical source PDF). Hence the formula also holds for $\mathcal F$. $\square$

> **Edition note (source).** The degree-additivity result used in the proof above is Theorem 30.6, not Theorem 30.7. The frozen semantic proof uses the correct reference. This edition preserves the historical source number explicitly in the proof and discloses the incorrect historical cross-reference here.
