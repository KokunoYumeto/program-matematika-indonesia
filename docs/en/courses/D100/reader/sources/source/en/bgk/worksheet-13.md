---
title: "Worksheet 13 - The Cone Map, Sheaves of Modules, and Invertible Sheaves"
stable_id: br-bgk-2019-w13
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 13"
upstream_pageid: 110220
upstream_revid: 1003881
upstream_timestamp: "2025-06-10T09:35:07Z"
upstream_mediawiki_sha1: aaf88e277115448a7cfc6398010a8083696cbd70
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003881"
authority_manifest: authority/wikiversity-bgk/unit-13/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 792935b01daf0a2ee22decd78d3f9ccb8d95719c628cdd306b66405ea1427282
worksheet_xml: authority/wikiversity-bgk/unit-13/worksheet-13.xml
worksheet_xml_sha256: 2e8528baca276e3669a92a38fff9e097dbe5954d3bf133e5657fea90865fb3fa
worksheet_expanded_tex: authority/wikiversity-bgk/unit-13/worksheet-13-expanded.tex
worksheet_expanded_tex_sha256: 6b6e308777adf2c2f3791cdde6581b45b7da8d4e3431ab3eee6bcf52608e1b6e
official_pdf: authority/artifacts/bgk-worksheet-13-official.pdf
official_pdf_sha256: da5afab54c1ae5035074d5254b3d91a980c436609e83961705ec55701fe0cecb
ordered_exercise_map: authority/wikiversity-bgk/unit-13/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: e62a98e5f5e0ac45138bce8ba904a90e869332d0e6321811fc06b6126b2dfcf1
exercise_count: 23
public_solution_count: 0
public_solution_numbers: ""
media_credits: source/id-ID/media-credits-bgk-unit-13.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 13: The Cone Map, Sheaves of Modules, and Invertible Sheaves {#br-bgk-2019-w13}

The frozen source marks none of the exercises with an asterisk. Separately, the frozen candidate evidence records negative results for all 23 exercises. This edition creates no new solutions.

<!-- upstream_entity: Projektiver Raum/Kegelabbildung/Ist nicht abgeschlossen/Aufgabe -->

## Exercise 13.1 {#br-bgk-2019-w13-ex01}

Give an example showing that the cone map

$$
\mathbb A_K^{n+1}\setminus\{0\}\longrightarrow\mathbb P_K^n
$$

need not be a closed map.

<!-- upstream_entity: Graduierter Ring/Primideal/Homogenisierung/Aufgabe -->

## Exercise 13.2 {#br-bgk-2019-w13-ex02}

Let $R$ be a $\mathbb Z$-graded ring and $\mathfrak p$ a prime ideal of $R$. Prove that the homogenisation $\mathfrak p^h$ is also a prime ideal.

<!-- upstream_entity: Kegelabbildung/Schema/Affiner Raum/Abgeschlossene Teilmenge/Aufgabe -->

## Exercise 13.3 {#br-bgk-2019-w13-ex03}

Let $K$ be a field and

$$
R=K[X_0,X_1,\ldots,X_n]/\mathfrak a
$$

a standard-graded $K$-algebra. Prove that the diagram

$$
\begin{matrix}
\operatorname{Spek}(R)\supseteq D(R_+)
&\longrightarrow&
V(\mathfrak a)\cap D(X_0,X_1,\ldots,X_n)
&\longrightarrow&
\mathbb A_K^{n+1}\supseteq D(X_0,X_1,\ldots,X_n)
\\
\downarrow&&\downarrow&&\downarrow
\\
\operatorname{Proj}(R)
&\longrightarrow&
V_+(\mathfrak a)
&\longrightarrow&
\mathbb P_K^n
\end{matrix}
$$

of scheme morphisms commutes. Here the vertical maps on the left and right are cone maps, and the horizontal maps are isomorphisms and the natural closed immersions.

<!-- upstream_entity: Kegelabbildung/C/Hopf-Faserung/Aufgabe -->

## Exercise 13.4 {#br-bgk-2019-w13-ex04}

Discuss the relationship between the cone map

$$
\mathbb A_{\mathbb C}^{2}
\supset \mathbb A_{\mathbb C}^{2}\setminus\{(0,0)\}
\longrightarrow\mathbb P_{\mathbb C}^{1}
$$

and the Hopf fibration

$$
S^3\longrightarrow S^2.
$$

<!-- upstream_entity: Beringter Raum/Modul/Halm/Aufgabe -->

## Exercise 13.5 {#br-bgk-2019-w13-ex05}

Let $\mathcal F$ be an $\mathcal O_X$-module on a ringed space $(X,\mathcal O_X)$. Prove that, for every point $P\in X$, the stalk $\mathcal F_P$ is an $\mathcal O_{X,P}$-module.

<!-- upstream_entity: Beringter Raum/Modul/Direkte Summe/Aufgabe -->

## Exercise 13.6 {#br-bgk-2019-w13-ex06}

Let $\mathcal F$ and $\mathcal G$ be $\mathcal O_X$-modules on a ringed space $(X,\mathcal O_X)$. Prove that the direct sum

$$
\mathcal F\oplus\mathcal G
$$

is also an $\mathcal O_X$-module.

<!-- upstream_entity: Beringter Raum/Modul/Untermodul/Restklassenmodul/Aufgabe -->

## Exercise 13.7 {#br-bgk-2019-w13-ex07}

Let $\mathcal F$ be an $\mathcal O_X$-module on a ringed space $(X,\mathcal O_X)$, and let

$$
\mathcal G\subseteq\mathcal F
$$

be an $\mathcal O_X$-submodule. Prove that the quotient sheaf

$$
\mathcal F/\mathcal G
$$

is naturally an $\mathcal O_X$-module.

<!-- upstream_entity: Beringter Raum/Strukturgarbe/Festlegungssatz/Einheit und Isomorphismus/Aufgabe -->

## Exercise 13.8 {#br-bgk-2019-w13-ex08}

Let $(X,\mathcal O_X)$ be a ringed space. Prove that

$$
s\in\Gamma(X,\mathcal O_X)
$$

is a unit if and only if the associated $\mathcal O_X$-module homomorphism

$$
\mathcal O_X\longrightarrow\mathcal O_X
$$

is an isomorphism.

<!-- upstream_entity: Beringter Raum/Freie Garbe/Strukturgarbe/Festlegungssatz/Surjektiv/Aufgabe -->

## Exercise 13.9 {#br-bgk-2019-w13-ex09}

Let $(X,\mathcal O_X)$ be a ringed space. Let

$$
s_1,\ldots,s_n\in\Gamma(X,\mathcal O_X)
$$

be global sections generating the unit ideal in $\Gamma(X,\mathcal O_X)$. Prove that the associated $\mathcal O_X$-module homomorphism

$$
\begin{aligned}
\mathcal O_X^n&\longrightarrow\mathcal O_X,\\
e_i&\longmapsto s_i,
\end{aligned}
$$

is surjective.

The converse of this assertion does not hold; see Exercise 14.10.

<!-- upstream_entity: Beringter Raum/Freier Modul/Festlegungssatz/Determinante/Isomorphismus/Aufgabe -->

## Exercise 13.10 {#br-bgk-2019-w13-ex10}

Let $(X,\mathcal O_X)$ be a ringed space. Let

$$
s_1,\ldots,s_n\in\Gamma(X,\mathcal O_X)^n
$$

be global sections with

$$
s_i=(s_{i1},\ldots,s_{in}).
$$

Prove that the determinant of the matrix

$$
(s_{ij})_{1\leq i,j\leq n}
$$

is a unit in $\Gamma(X,\mathcal O_X)$ if and only if the associated $\mathcal O_X$-module homomorphism

$$
\begin{aligned}
\mathcal O_X^n&\longrightarrow\mathcal O_X^n,\\
e_i&\longmapsto s_i,
\end{aligned}
$$

is an isomorphism.

<!-- upstream_entity: Beringter Raum/Modulgarben/Homomorphismenmodulgarbe/Lokaler Homomorphietest/Aufgabe -->

## Exercise 13.11 {#br-bgk-2019-w13-ex11}

Let $(X,\mathcal O_X)$ be a ringed space, $\mathcal M$ and $\mathcal N$ sheaves of modules on $X$, and

$$
\varphi:\mathcal M\longrightarrow\mathcal N
$$

a sheaf morphism. Also let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover. Prove the following assertions.

1. If, for every $i$, the map

   $$
   \varphi_{U_i}:\Gamma(U_i,\mathcal M)
   \longrightarrow\Gamma(U_i,\mathcal N)
   $$

   is compatible with addition, then the same holds for

   $$
   \varphi_X:\Gamma(X,\mathcal M)\longrightarrow\Gamma(X,\mathcal N).
   $$

2. If, for every $i$, the map

   $$
   \varphi_{U_i}:\Gamma(U_i,\mathcal M)
   \longrightarrow\Gamma(U_i,\mathcal N)
   $$

   is compatible with scalar multiplication by $\Gamma(U_i,\mathcal O_X)$, then the same holds for $\varphi_X$.

3. If, for every $i$, the map

   $$
   \varphi|_{U_i}:\mathcal M|_{U_i}\longrightarrow\mathcal N|_{U_i}
   $$

   is an $\mathcal O_X|_{U_i}$-module homomorphism, then $\varphi$ is also an $\mathcal O_X$-module homomorphism.

<!-- upstream_entity: Beringter Raum/Modulgarbe/Bidual/Aufgabe -->

## Exercise 13.12 {#br-bgk-2019-w13-ex12}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal F$ a sheaf of modules on $X$. Prove that there is a natural $\mathcal O_X$-module homomorphism

$$
\mathcal F\longrightarrow\mathcal F^{**}.
$$

<!-- upstream_entity: Beringter Raum/Modulgarben/Tensorprodukt/Prägarbe/Halm/Aufgabe -->

## Exercise 13.13 {#br-bgk-2019-w13-ex13}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal F,\mathcal G$ sheaves of modules on $X$. Prove that the stalk at a point $P\in X$ of the presheaf

$$
U\longmapsto
\Gamma(U,\mathcal F)
\otimes_{\Gamma(U,\mathcal O_X)}
\Gamma(U,\mathcal G)
$$

equals

$$
\begin{aligned}
&\operatorname{colim}_{P\in U}
  \left(\Gamma(U,\mathcal F)\otimes_{\Gamma(U,\mathcal O_X)}
  \Gamma(U,\mathcal G)\right)
\\
&\qquad=
\left(\operatorname{colim}_{P\in U}\Gamma(U,\mathcal F)\right)
\otimes_{
  \left(\operatorname{colim}_{P\in U}\Gamma(U,\mathcal O_X)\right)}
\left(\operatorname{colim}_{P\in U}\Gamma(U,\mathcal G)\right)
\\
&\qquad=\mathcal F_P\otimes_{\mathcal O_{X,P}}\mathcal G_P.
\end{aligned}
$$

> **Editorial note - colimit notation.** The source interchanges each colimit's index and argument. This edition places $P\in U$ in the subscript and the section module in the argument. The index runs over open neighbourhoods of $P$, with maps given by restriction to smaller neighbourhoods; the asserted tensor-product identity is unchanged.

<!-- upstream_entity: Beringter Raum/Modulgarbe/Duale Garbe/Tensorierung/Auswertung/Aufgabe -->

## Exercise 13.14 {#br-bgk-2019-w13-ex14}

Let $\mathcal F$ be a sheaf of modules on a ringed space $(X,\mathcal O_X)$, and let $\mathcal F^*$ be its dual sheaf. Prove that there is a natural $\mathcal O_X$-module homomorphism

$$
\mathcal F\otimes_{\mathcal O_X}\mathcal F^*
\longrightarrow\mathcal O_X.
$$

<!-- upstream_entity: Lokal beringter Raum/Invertierbare Garbe/Invertierbarkeitsort/Aufgabe -->

## Exercise 13.15 {#br-bgk-2019-w13-ex15}

Let $(X,\mathcal O_X)$ be a locally ringed space and $\mathcal L$ an invertible sheaf on $X$. Let $U\subseteq X$ be an open subset such that the restriction $\mathcal L|_U$ is trivial, and let

$$
\varphi:\mathcal L|_U\longrightarrow\mathcal O_X|_U
$$

be an isomorphism. Let

$$
s\in\Gamma(X,\mathcal L)
$$

be a global section with invertibility locus $X_s$. Prove that

$$
X_s\cap U=U_{\varphi(s)},
$$

where the right-hand side denotes the invertibility locus of $\varphi(s)\in\Gamma(U,\mathcal O_X|_U)$.

<!-- upstream_entity: Beringter Raum/Invertierbare Garben/Duale Garbe/Invertierbar/Aufgabe -->

## Exercise 13.16 {#br-bgk-2019-w13-ex16}

Let $\mathcal L$ be an invertible sheaf on a ringed space $(X,\mathcal O_X)$. Prove that the dual sheaf

$$
\mathcal L^*
$$

is also invertible.

<!-- upstream_entity: Beringter Raum/Invertierbare Garben/Tensorierung/Aufgabe -->

## Exercise 13.17 {#br-bgk-2019-w13-ex17}

Let $\mathcal L$ and $\mathcal M$ be invertible sheaves on a ringed space $(X,\mathcal O_X)$. Prove that the tensor product

$$
\mathcal L\otimes_{\mathcal O_X}\mathcal M
$$

is also invertible.

<!-- upstream_entity: Lokal beringter Raum/Invertierbare Garben/Tensorierung/Invertierbarkeitsort/Aufgabe -->

## Exercise 13.18 {#br-bgk-2019-w13-ex18}

Let $\mathcal L$ and $\mathcal M$ be invertible sheaves on a locally ringed space $(X,\mathcal O_X)$. Let

$$
s\in\Gamma(X,\mathcal L),
\qquad
t\in\Gamma(X,\mathcal M),
$$

and

$$
st\in\Gamma(X,\mathcal L\otimes\mathcal M).
$$

Prove that their invertibility loci satisfy

$$
X_{st}=X_s\cap X_t.
$$

<!-- upstream_entity: Beringter Raum/Invertierbare Garbe/Bidual/Aufgabe -->

## Exercise 13.19 {#br-bgk-2019-w13-ex19}

Prove that an invertible sheaf $\mathcal L$ on a ringed space $(X,\mathcal O_X)$ is naturally isomorphic to its bidual $\mathcal L^{**}$.

<!-- upstream_entity: Beringter Raum/Invertierbare Garben/Duale Garbe/Tensorierung/Aufgabe -->

## Exercise 13.20 {#br-bgk-2019-w13-ex20}

Let $\mathcal L$ be an invertible sheaf on a ringed space $(X,\mathcal O_X)$ and $\mathcal L^*$ its dual sheaf. Prove that there is a natural $\mathcal O_X$-module isomorphism

$$
\mathcal L\otimes_{\mathcal O_X}\mathcal L^*
\longrightarrow\mathcal O_X.
$$

<!-- upstream_entity: Projektiver Raum/Getwistete Strukturgarben/Positiver Twist/Invertierbarkeitsort/Aufgabe -->

## Exercise 13.21 {#br-bgk-2019-w13-ex21}

Consider projective space over a field $K$ and the invertible sheaf

$$
\mathcal O_{\mathbb P_K^n}(m)
$$

for $m>0$. Let

$$
f\in\Gamma\!\left(\mathbb P_K^n,
\mathcal O_{\mathbb P_K^n}(m)\right)
=K[X_0,X_1,\ldots,X_n]_m.
$$

Prove the following equality of invertibility loci:

$$
(\mathbb P_K^n)_f=D_+(f).
$$

<!-- upstream_entity: Projektiver Raum/Getwistete  Strukturgarben/Tensorierung/Aufgabe -->

## Exercise 13.22 {#br-bgk-2019-w13-ex22}

Consider projective space over a field $K$ and the invertible sheaves $\mathcal O_{\mathbb P_K^n}(\ell)$. Prove that

$$
\mathcal O_{\mathbb P_K^n}(\ell)
\otimes\mathcal O_{\mathbb P_K^n}(m)
\cong\mathcal O_{\mathbb P_K^n}(\ell+m).
$$

<!-- upstream_entity: Projektive Hyperebene/Kurze exakte Sequenz/Aufgabe -->

## Exercise 13.23 {#br-bgk-2019-w13-ex23}

Let

$$
0\ne F\in K[X_0,X_1,\ldots,X_n]
$$

be a homogeneous polynomial of degree $d$. Prove that it determines a short exact sequence of sheaves

$$
0\longrightarrow
\mathcal O_{\mathbb P_K^n}(-d)
\xrightarrow{\,\cdot F\,}
\mathcal O_{\mathbb P_K^n}
\longrightarrow
\mathcal O_{V_+(F)}
\longrightarrow 0
$$

on projective space. Here the structure sheaf of the projective hypersurface $V_+(F)$ is regarded as a sheaf on projective space.
