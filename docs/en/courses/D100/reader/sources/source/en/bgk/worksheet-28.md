---
title: "Worksheet 28 - Morphisms to projective space"
stable_id: br-bgk-2019-w28
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 28"
upstream_pageid: 110237
upstream_revid: 793599
upstream_timestamp: "2022-08-25T06:21:18Z"
upstream_mediawiki_sha1: ea85b787c20468bfd111f5afe6022adb84c3e3d7
source_url: "https://de.wikiversity.org/w/index.php?oldid=793599"
authority_manifest: authority/wikiversity-bgk/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 1ab20936afe74fcfdde3318452f2211f2458911ff0a77c554fba894de49f4b9f
worksheet_xml: authority/wikiversity-bgk/unit-28/worksheet-28.xml
worksheet_xml_sha256: 56c469f5194deedc36448313ba7056ac42e3dae859c87095f9e833ae8bae66fc
worksheet_expanded_tex: authority/wikiversity-bgk/unit-28/worksheet-28-expanded.tex
worksheet_expanded_tex_sha256: 4bb944ec5c5519518f1b5983de082ca0bcd4e149a788ecc57ec2da2633b769b8
official_pdf: authority/artifacts/bgk-worksheet-28-official.pdf
official_pdf_sha256: 663106b4ccb3fff4ef022fad226e0e9765deec1a39fa8e1d1c2b873886a728df
ordered_exercise_map: authority/wikiversity-bgk/unit-28/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 00380c3c1746989c8e7e12a8058732b96cd631c88a22750de4b174a5c884755e
exercise_count: 14
public_solution_count: 1
public_solution_numbers: "6"
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-28.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 28: Morphisms to projective space {#br-bgk-2019-w28}

## Exercises {#br-bgk-2019-w28-s01}

<!-- upstream_entity: Kegelabbildung/Lineares System/Aufgabe -->
### Exercise 28.1 {#br-bgk-2019-w28-ex01}

Describe the cone map

$$
\mathbb A^{d+1}_K\setminus\{(0,0,\ldots,0)\}
\longrightarrow\mathbb P^d_K
$$

using a linear system in an invertible sheaf.

<!-- upstream_entity: Projektion weg von einem Punkt/Lineares System/Aufgabe -->
### Exercise 28.2 {#br-bgk-2019-w28-ex02}

Describe projection away from a point using a linear system in an invertible sheaf.

<!-- upstream_entity: Projektiver Raum/Bijektive lineare Abbildung/Automorphismus/Aufgabe -->
### Exercise 28.3 {#br-bgk-2019-w28-ex03}

Let $K$ be a field and let $\mathbb P^n_K$ be the associated projective space. Let $\varphi:K^{n+1}\to K^{n+1}$ be a bijective linear map.

1. Prove that $\varphi$ induces an automorphism
   $$
   \varphi:\mathbb P^n_K\longrightarrow\mathbb P^n_K,
   \qquad
   (x_0,x_1,\ldots,x_n)\longmapsto
   \varphi(x_0,x_1,\ldots,x_n).
   $$
2. Determine the inverse image of $D_+(X_i)$ in the situation of part (1). What does the morphism look like on these affine sets?
3. Prove that $\varphi_1$ and $\varphi_2$ induce the same automorphism of projective space precisely when one is a nonzero scalar multiple of the other.
4. Does every linear map $\varphi:K^{n+1}\to K^{n+1}$ induce a morphism $\varphi:\mathbb P^n_K\to\mathbb P^n_K$?

In the situation above, we speak of a *projective linear automorphism*.

<!-- upstream_entity: Projektiver Raum/Bijektive lineare Abbildung/Lineares System/Aufgabe -->
### Exercise 28.4 {#br-bgk-2019-w28-ex04}

Describe a projective linear automorphism

$$
\mathbb P^d_K\longrightarrow\mathbb P^d_K
$$

using a linear system in an invertible sheaf.

<!-- upstream_entity: Projektiver Raum/Zwei Punkte/Automorphismus/Aufgabe -->
### Exercise 28.5 {#br-bgk-2019-w28-ex05}

Let $P,Q\in\mathbb P^n_K$ be points of projective space over a field $K$. Prove that there is an automorphism $\varphi:\mathbb P^n_K\to\mathbb P^n_K$ with $\varphi(P)=Q$.

<!-- upstream_entity: Ebene/Drei Vektoren/Transformierbar/Aufgabe -->
### Exercise 28.6 ★ {#br-bgk-2019-w28-ex06}

Let $V$ be a two-dimensional vector space over a field $K$. Let $v_1,v_2,v_3$ and $w_1,w_2,w_3$ be vectors in $V$, with each pair of vectors in each family linearly independent. Prove that there is a bijective linear map $\varphi:V\to V$ such that

$$
\varphi(v_i)\in Kw_i
$$

for $i=1,2,3$.

<!-- upstream_entity: Projektive Gerade/Drei Punkte/Automorphismus/Aufgabe -->
### Exercise 28.7 {#br-bgk-2019-w28-ex07}

Let $P_1,P_2,P_3\in\mathbb P^1_K$ and $Q_1,Q_2,Q_3\in\mathbb P^1_K$ each be three distinct points on the projective line over a field $K$. Prove that there is a $K$-automorphism $\varphi:\mathbb P^1_K\to\mathbb P^1_K$ with $\varphi(P_i)=Q_i$ for $i=1,2,3$.

<!-- upstream_entity: Projektiver Raum/Automorphismus/Aufgabe -->
### Exercise 28.8 {#br-bgk-2019-w28-ex08}

Let $K$ be a field. Prove that every $K$-automorphism of projective space $\mathbb P^n_K$ is projective linear.

Use the fact that the pullback of $\mathcal O_{\mathbb P^n_K}(1)$ must again be $\mathcal O_{\mathbb P^n_K}(1)$.

<!-- upstream_entity: Lineares System/Basiswechsel/Projektiver Automorphismus/Aufgabe -->
### Exercise 28.9 {#br-bgk-2019-w28-ex09}

Let $X$ be a scheme over a field $K$, let $\mathcal L$ be an invertible sheaf on $X$, and let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections determining the linear system

$$
\langle s_0,s_1,\ldots,s_n\rangle
\subseteq\Gamma(X,\mathcal L).
$$

Let $t_0,t_1,\ldots,t_n$ be another generating system for the same linear system. Prove the following assertions.

1. $\bigcup_{i=0}^{n}X_{s_i}=\bigcup_{i=0}^{n}X_{t_i}$.
2. For the morphisms defined by the two generating systems, there is a projective linear automorphism
   $$
   \theta:\mathbb P^n_K\longrightarrow\mathbb P^n_K
   $$
   such that
   $$
   \theta\circ\varphi_{s_0,s_1,\ldots,s_n}
   =\varphi_{t_0,t_1,\ldots,t_n}.
   $$

<!-- upstream_entity: Projektive Gerade/O(1)/Lineare Einbettung/Aufgabe -->
### Exercise 28.10 {#br-bgk-2019-w28-ex10}

Consider the projective line $\mathbb P^1_K$ and the complete linear system

$$
L:=\langle s,t\rangle
=\Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K}(1)).
$$

Prove that choosing a generating system of three elements for $L$, up to scalar multiplication, corresponds to an embedding of the projective line into the projective plane as a line. How can the image line be described?

<!-- upstream_entity: Projektive Gerade/O(2)/3 Schnitte/Einbettung/Aufgabe -->
### Exercise 28.11 {#br-bgk-2019-w28-ex11}

Consider the projective line $\mathbb P^1_K$ and the complete linear system

$$
L:=\langle s^2,st,t^2\rangle
=\Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K}(2)).
$$

Prove that choosing a basis of $L$, up to scalar multiplication, corresponds to an embedding of the projective line into the projective plane. How can the image curve be described?

<!-- upstream_entity: Projektive Gerade/O(4)/4 Schnitte/Veronese-Einbettung/Aufgabe -->
### Exercise 28.12 {#br-bgk-2019-w28-ex12}

Consider the projective line $\mathbb P^1_K$ and the complete linear system

$$
L:=\langle s^3,s^2t,st^2,t^3\rangle
=\Gamma(\mathbb P^1_K,\mathcal O_{\mathbb P^1_K}(3)).
$$

Prove that the associated map

$$
\mathbb P^1_K\longrightarrow\mathbb P^3_K
$$

gives an embedding of the projective line into projective space. Give as many equations as possible satisfied by the image curve.

> **Edition note (source).** The title of the transcluded exercise page contains the segment `O(4)`, but the exercise itself uses four cubic sections and $\mathcal O(3)$. This edition preserves the formula displayed in the exercise; the exact source title remains recorded in the entity marker above.

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Über affinen Kegel/Aufgabe -->
### Exercise 28.13 {#br-bgk-2019-w28-ex13}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, and let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections. Let $L\to X$ be the line bundle in the sense of Theorem 17.10 associated with the dual invertible sheaf $\mathcal L^*$, so that the $s_i$ can be regarded as morphisms

$$
L\longrightarrow X\times\mathbb A^1_R\longrightarrow\mathbb A^1_R.
$$

Put $U=\bigcup_{i=0}^{n}X_{s_i}$, and let $L^\times|_U$ be the restriction of $L$ to $U$ with its zero section removed. Prove that there is a commutative diagram

$$
\begin{CD}
L^\times|_U @>{(s_0,s_1,\ldots,s_n)}>>
\mathbb A^{n+1}_R\setminus\{0\}=\displaystyle\bigcup_{i=0}^{n}D(x_i)\\
@VVV @VV{\pi}V\\
U @>{\varphi_{s_0,s_1,\ldots,s_n,\mathcal L}}>> \mathbb P^n_R,
\end{CD}
$$

with the cone map on the right.

> **Edition note (source).** In both unions in the source diagram, the printed index starts at $i=1$, although the family of sections is $s_0,\ldots,s_n$ and the cone map uses all coordinates. Moreover, the source places all of $L$ in the upper left, but the zero section maps to the origin, where the cone map $\pi$ is undefined; over a base point outside $U$, every fibre point also maps to the origin. The diagram has therefore been restricted to $L^\times|_U$, and both unions use the consistent bounds $i=0,\ldots,n$.

<!-- upstream_entity: Schema über R/Invertierbare Garbe/Schnitte/Morphismus in projektiven Raum/Global definiert/Fakt/Beweis/Aufgabe -->
### Exercise 28.14 {#br-bgk-2019-w28-ex14}

Let $X$ be a scheme over a commutative ring $R$, let $\mathcal L$ be an invertible sheaf on $X$, and let $s_0,s_1,\ldots,s_n\in\Gamma(X,\mathcal L)$ be global sections. Prove that the following statements are equivalent.

1. $X=\bigcup_{i=0}^{n}X_{s_i}$.
2. The morphism to $\mathbb P^n_R$ defined by the linear system $(s_0,s_1,\ldots,s_n)$ is defined on all of $X$.
3. The linear system $(s_0,s_1,\ldots,s_n)$ is base-point-free.
