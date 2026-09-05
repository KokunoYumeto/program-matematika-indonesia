---
title: "Worksheet 1 - Vector Bundles and Tangent Bundles"
stable_id: br-bgk-2019-w01
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 1"
upstream_pageid: 110204
upstream_revid: 1069465
upstream_timestamp: "2026-02-05T20:48:01Z"
upstream_mediawiki_sha1: a2c9deb62e10eb9942aac56cde2e33aed04823fd
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069465"
authority_manifest: authority/wikiversity-bgk/unit-01/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ad271f5ad69f9990dbe3082c22f8c52b7a4c58494c8f6614350078535d4f2ba1
worksheet_xml: authority/wikiversity-bgk/unit-01/worksheet-01.xml
worksheet_xml_sha256: 95e392e04115c0dcfc94eebc28bfdbdbdfc1cda3c46d6f008d7d1324b3e81095
worksheet_expanded_tex: authority/wikiversity-bgk/unit-01/worksheet-01-expanded.tex
worksheet_expanded_tex_sha256: 566b4211d5b25be90256a24567f0c448a6cc9fe23aec74c4fde8c6922cba2d97
exercise_map: authority/wikiversity-bgk/unit-01/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 21244128b357d5fc35d5a8dc7129c27e091a781594516c4f6db87e9202b162ba
official_pdf: authority/artifacts/bgk-worksheet-01-official.pdf
official_pdf_sha256: 0f65dad0173f0ad40d22cf5f255f9379aca90a090d0c54cc268379f8628ee70a
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF and media retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 17
public_solution_count: 0
---

# Worksheet 1: Vector Bundles and Tangent Bundles {#br-bgk-2019-w01}

In the following exercises, we use the notation

$$
D(r)=\left\{(r,s,t)\in\mathbb R^3\mid r\ne0\right\}.
$$

<!-- upstream_entity: Lineare Gleichung/Drei Variablen/Parameter/Trivialisierungen/Übergangsabbildungen/Aufgabe -->

## Exercise 1.1 {#br-bgk-2019-w01-ex01}

For the vector bundle

$$
\begin{aligned}
L={}&\left\{(r,s,t,u,v,w)\mathrel{\Big|}
ru+sv+tw=0,\ (r,s,t)\ne(0,0,0)\right\}\\
&\subseteq
\left(\mathbb R^3\setminus\{(0,0,0)\}\right)\times\mathbb R^3
\longrightarrow\mathbb R^3\setminus\{(0,0,0)\},
\end{aligned}
$$

determine linear trivialisations over $D(r)$, $D(s)$ and $D(t)$, that is, bases depending on $r,s,t$ over $D(r)$ and so on. Determine the change-of-basis maps on

$$
D(rs)=D(r)\cap D(s).
$$

<!-- upstream_entity: Lineare Gleichung/Drei Variablen/Parameter/Trivialisierungen/Vektorzugehörigkeit/Aufgabe -->

## Exercise 1.2 {#br-bgk-2019-w01-ex02}

For the vector bundle

$$
\begin{aligned}
L={}&\left\{(r,s,t,u,v,w)\mathrel{\Big|}
ru+sv+tw=0,\ (r,s,t)\ne(0,0,0)\right\}\\
&\subseteq
\left(\mathbb R^3\setminus\{(0,0,0)\}\right)\times\mathbb R^3
\longrightarrow\mathbb R^3\setminus\{(0,0,0)\},
\end{aligned}
$$

determine all parameters $(r,s,t)$ for which the vector $(3,7,4)$ belongs to the fibre $L_{(r,s,t)}$.

<!-- upstream_entity: Lineare Gleichung/Drei Variablen/Parameter/Trivialisierungen/Fortsetzungsfunktion/Aufgabe -->

## Exercise 1.3 {#br-bgk-2019-w01-ex03}

Show that, in Example 1.2 and over $D(r)$, the formula

$$
u(r,s,t)=
\frac{t}{r}\begin{pmatrix}s\\-r\\0\end{pmatrix}
-\frac{s}{r}\begin{pmatrix}t\\0\\-r\end{pmatrix}
$$

defines a parameter-dependent vector in the solution space that extends polynomially to all of $\mathbb R^3$, even though the coefficient functions $t/r$ and $-s/r$ are defined only on $D(r)$ and do not extend. Is $u(r,s,t)$ part of a basis at every point?

<!-- upstream_entity: Zwei lineare Gleichungen/Drei Variablen/Parameter/Trivialisierung/Stratifizierung/Aufgabe -->

## Exercise 1.4 {#br-bgk-2019-w01-ex04}

In Example 1.3, determine the parameters for which the solution space $L_{(a,b,c,d,e,f)}$ is one-, two- or three-dimensional. Are these parameter sets open or closed?

<!-- upstream_entity: Körper/Kreuzprodukt/Keine Basis/Aufgabe -->

## Exercise 1.5 {#br-bgk-2019-w01-ex05}

Show that, over an arbitrary field $K$, for two linearly independent vectors

$$
u=\begin{pmatrix}a\\b\\c\end{pmatrix}
\quad\text{and}\quad
v=\begin{pmatrix}d\\e\\f\end{pmatrix},
$$

the family consisting of $u$, $v$ and their cross product

$$
\begin{pmatrix}a\\b\\c\end{pmatrix}
\times
\begin{pmatrix}d\\e\\f\end{pmatrix}
$$

need not form a basis of $K^3$.

<!-- upstream_entity: Affin-lineares Bündel/R^2/Fasern/Aufgabe -->

## Exercise 1.6 {#br-bgk-2019-w01-ex06}

Consider the topological space

$$
Y:=\left\{(s,t,u,v)\in\mathbb R^4\mid su+tv=1\right\}
$$

with projection

$$
\begin{aligned}
p:Y&\longrightarrow\mathbb R^2\setminus\{(0,0)\}=X,\\
(s,t,u,v)&\longmapsto(s,t).
\end{aligned}
$$

1. Show that every fibre of $p$ is homeomorphic to a real line.
2. Show that

   $$
   \varphi(s,t)=(s,t,u(s,t),v(s,t))
   =\left(s,t,\frac{s}{s^2+t^2},\frac{t}{s^2+t^2}\right)
   $$

   defines a continuous map $\varphi:X\to Y$ with

   $$
   p\circ\varphi=\operatorname{Id}_X.
   $$

3. Define a homeomorphism between $Y$ and $X\times\mathbb R$.
4. Show that there is no polynomial map $\psi:X\to Y$ with

   $$
   p\circ\psi=\operatorname{Id}_X.
   $$

<!-- upstream_entity: Reelles Vektorbündel/Ein Punkt/Aufgabe -->

## Exercise 1.7 {#br-bgk-2019-w01-ex07}

Show that a real vector bundle over a point, that is, over a one-point topological space, is the same as a finite-dimensional real vector space.

<!-- upstream_entity: Reelles Vektorbündel/Hausdorff/Aufgabe -->

## Exercise 1.8 {#br-bgk-2019-w01-ex08}

Let $p:V\to X$ be a real vector bundle over a topological space $X$. Show that $V$ is a Hausdorff space if and only if $X$ is a Hausdorff space.

<!-- upstream_entity: Reelles Vektorbündel/Identität/Aufgabe -->

## Exercise 1.9 {#br-bgk-2019-w01-ex09}

Let $X$ be a topological space. Show that the identity map

$$
\operatorname{Id}_X:X\longrightarrow X
$$

can be regarded as a real vector bundle of rank $0$.

<!-- upstream_entity: Triviale Bündel/Homomorphismus/Matrixbeschreibung/Aufgabe -->

## Exercise 1.10 {#br-bgk-2019-w01-ex10}

Let $X$ be a topological space. Show that a homomorphism of trivial vector bundles

$$
\varphi:X\times\mathbb R^n\longrightarrow X\times\mathbb R^m
$$

is the same as an $m\times n$ matrix whose entries are continuous functions from $X$ to $\mathbb R$.

<!-- upstream_entity: Stetige differenzierbare Abbildung/Totales Differential/Vektorbündelhomomorphismus/Aufgabe -->

## Exercise 1.11 {#br-bgk-2019-w01-ex11}

Let $U\subseteq\mathbb R^n$ be open and $f:U\to\mathbb R^m$ a continuously differentiable map. Show that the total differential, in the form

$$
\begin{aligned}
U\times\mathbb R^n&\longrightarrow U\times\mathbb R^m,\\
(x,v)&\longmapsto\bigl(x,(Df)_x(v)\bigr),
\end{aligned}
$$

defines a homomorphism from the vector bundle $U\times\mathbb R^n$ to the vector bundle $U\times\mathbb R^m$.

<!-- upstream_entity: Tangentialbündel/S^1/Trivial/Aufgabe -->

## Exercise 1.12 {#br-bgk-2019-w01-ex12}

Show that the tangent bundle $TS^1$ of the $1$-sphere $S^1$ is homeomorphic to the product $S^1\times\mathbb R$.

How is this exercise related to Example 1.1?

<!-- upstream_entity: S^1/Weg/Tangentialbündel/Basiskonvergenz/Beispiel/Aufgabe -->

## Exercise 1.13 {#br-bgk-2019-w01-ex13}

Give an example of a differentiable curve

$$
\gamma:[0,1)\longrightarrow S^1
$$

such that the limit

$$
\lim_{t\to1}\gamma(t)
$$

exists, but the limit

$$
\lim_{t\to1}\bigl(\gamma(t),T_t(\gamma)(1)\bigr)
$$

does not exist in $TS^1$.

<!-- upstream_entity: Einheitssphäre/Untermannigfaltigkeit/Tangentialabbildung/Aufgabe -->

## Exercise 1.14 {#br-bgk-2019-w01-ex14}

Show that the map

$$
\begin{aligned}
TS^1&\longrightarrow\mathbb R^2,\\
((a,b),t(-b,a))&\longmapsto(a,b)+t(-b,a)
\end{aligned}
$$

has two preimages for every point $(x,y)\in\mathbb R^2$ outside the unit disc, one preimage for every point on the unit circle, and no preimage for any point inside the open unit disc. Interpret this geometrically.

<!-- upstream_entity: Mannigfaltigkeit/Differenzierbare Abbildung/Injektiv/Tangentialabbildung nicht injektiv/Beispiel/Aufgabe -->

## Exercise 1.15 {#br-bgk-2019-w01-ex15}

Give an example of an injective differentiable map

$$
\varphi:M\longrightarrow N
$$

between two differentiable manifolds $M$ and $N$ such that the associated tangent map

$$
T(\varphi):TM\longrightarrow TN
$$

is not injective.

<!-- upstream_entity: Mannigfaltigkeit/Differenzierbare Abbildung/Surjektiv/Tangentialabbildung nicht surjektiv/Beispiel/Aufgabe -->

## Exercise 1.16 {#br-bgk-2019-w01-ex16}

Give an example of a surjective differentiable map

$$
\varphi:M\longrightarrow N
$$

between two differentiable manifolds $M$ and $N$ such that the associated tangent map

$$
T(\varphi):TM\longrightarrow TN
$$

is not surjective.

<!-- upstream_entity: Mannigfaltigkeit/Tangentialabbildung/Stetig/Aufgabe -->

## Exercise 1.17 {#br-bgk-2019-w01-ex17}

Let $M$ and $N$ be differentiable manifolds and $\varphi:M\to N$ a differentiable map. Show that the associated tangent map

$$
T(\varphi):TM\longrightarrow TN
$$

is continuous.

