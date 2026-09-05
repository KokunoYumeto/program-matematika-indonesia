---
title: "Worksheet 18 - Kähler Differentials"
stable_id: br-bgk-2019-w18
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 18"
upstream_pageid: 110225
upstream_revid: 1008805
upstream_timestamp: "2025-07-10T16:33:18Z"
upstream_mediawiki_sha1: 9d122888e407ae4a211bdff1a5368dd467ac9ff6
source_url: "https://de.wikiversity.org/w/index.php?oldid=1008805"
authority_manifest: authority/wikiversity-bgk/unit-18/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f0014846fe068d3b1bfd4488c1db66fdd6039fa2d70ff7b8a213875a56d39495
authority_manifest_status: "Complete terminal authority freeze; all 41 file records have been recomputed without mismatches."
worksheet_xml: authority/wikiversity-bgk/unit-18/worksheet-18.xml
worksheet_xml_sha256: 6756943999b9441a20a48b7c1890dedd42d37d862965b1be1e7caa263c99623b
worksheet_expanded_tex: authority/wikiversity-bgk/unit-18/worksheet-18-expanded.tex
worksheet_expanded_tex_sha256: 0b01a90880f15272b078a42e6d510f20bbdd9b0498d4cb4b300d6e278b1cacd0
official_pdf: authority/artifacts/bgk-worksheet-18-official.pdf
official_pdf_sha256: 2d9a8cb439babbb5bb4f671ded98614d86f29871f26ae689e5d7b3280f6f8bb1
official_pdf_status: "Local official PDF witness; 56,337 bytes, 5 pages, and upload SHA-1 60eb61113b2059edae845ecb161b9fcb1cb5f7a3 have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-18/official-pdfs-api.json
official_pdf_source_bytes: 56337
official_pdf_source_sha1: 60eb61113b2059edae845ecb161b9fcb1cb5f7a3
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
ordered_exercise_map: authority/wikiversity-bgk/unit-18/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 2d687492b05ef02025dd2d7e53e3bf76c8034f69e26047f9ba72d9d1a1a5f79f
exercise_count: 25
public_solution_count: 3
public_solution_numbers: "6, 17, 18"
media_credits: source/id-ID/media-credits-bgk-unit-18.md
rights_ledger: authority/RIGHTS-bgk-unit-18.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-18.json
asset_closure_sha256: 33d6804e99934e11b06f7d05a732646e9371a51dd6fbbb35d642da28080caa77
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 18: Kähler Differentials {#br-bgk-2019-w18}

Stars mark exactly three exercises with frozen public solutions: Exercises 18.6, 18.17, and 18.18. The other twenty-two exercises have negative candidate results; this edition does not invent new solutions.

<!-- upstream_entity: Derivation/Potenz/Aufgabe -->

## Exercise 18.1 {#br-bgk-2019-w18-ex01}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, let $M$ be an $A$-module, and let

$$
D:A\longrightarrow M
$$

be an $R$-derivation. Prove that

$$
D(f^n)=nf^{n-1}D(f)
$$

for every $f\in A$.

> **Editorial note — the module in Exercises 18.1–18.3.** The source calls $M$ an $R$-module. The products by elements of $A$ in the Leibniz rule require an $A$-module structure, as in Definition 18.1. This edition makes that required structure explicit in all three exercises.

<!-- upstream_entity: Derivation/Allgemeine Produktregel/Aufgabe -->

## Exercise 18.2 {#br-bgk-2019-w18-ex02}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, let $M$ be an $A$-module, and let $D:A\to M$ be an $R$-derivation. Prove that

$$
\begin{aligned}
D(f_1\cdots f_r)={}&f_2\cdots f_rD(f_1)
+f_1f_3\cdots f_rD(f_2)\\
&+\cdots+f_1\cdots f_{r-1}D(f_r)
\end{aligned}
$$

for $f_1,\ldots,f_r\in A$.

<!-- upstream_entity: Derivation/Monom/Aufgabe -->

## Exercise 18.3 {#br-bgk-2019-w18-ex03}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, let $M$ be an $A$-module, and let $D:A\to M$ be an $R$-derivation. Let

$$
x_1^{n_1}\cdots x_r^{n_r}\in A.
$$

Prove that

$$
\begin{aligned}
D(x_1^{n_1}\cdots x_r^{n_r})={}&
n_1x_1^{n_1-1}x_2^{n_2}\cdots x_{r-1}^{n_{r-1}}x_r^{n_r}D(x_1)\\
&+\cdots+
n_rx_1^{n_1}\cdots x_{r-1}^{n_{r-1}}x_r^{n_r-1}D(x_r).
\end{aligned}
$$

<!-- upstream_entity: Derivation/R-Modul/Aufgabe -->

## Exercise 18.4 {#br-bgk-2019-w18-ex04}

Let $A$ be a commutative $R$-algebra and let $M$ be an $A$-module. Prove that the set of derivations from $A$ to $M$ becomes an $A$-module if $f\delta$ is defined by

$$
(f\delta)(a)=f\delta(a).
$$

<!-- upstream_entity: Derivation/Fortsetzung auf Nenneraufnahme/Aufgabe -->

## Exercise 18.5 {#br-bgk-2019-w18-ex05}

Let $R$ be a commutative $K$-algebra, let $W\subseteq R$ be a multiplicative system, and let $D:R\to R$ be a $K$-derivation. Prove that the formula

$$
D\left(\frac fg\right):=\frac{gD(f)-fD(g)}{g^2}
$$

defines a derivation on the localisation $R_W$ extending $D$.

<!-- upstream_entity: Derivation/Lie-Klammer/Multiplikation/Aufgabe -->

## Exercise 18.6 ★ {#br-bgk-2019-w18-ex06}

Let $A$ be a commutative $R$-algebra over a commutative ring $R$. For $f\in A$, write the $R$-linear map given by multiplication by $f$ as

$$
\mu_f:A\longrightarrow A,\qquad x\longmapsto fx,
$$

and for two $R$-linear maps

$$
\varphi_1,\varphi_2:A\longrightarrow A
$$

write

$$
[\varphi_1,\varphi_2]
=\varphi_1\circ\varphi_2-\varphi_2\circ\varphi_1.
$$

Let $\delta:A\to A$ be an $R$-derivation. Prove that for every $g\in A$, the map $[\delta,\mu_g]$ is a multiplication map.

<!-- upstream_entity: Universelle Derivation/Derivation/Aufgabe -->

## Exercise 18.7 {#br-bgk-2019-w18-ex07}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $\Omega_{A/R}$ be the module of Kähler differentials. Prove that the universal derivation

$$
A\longrightarrow\Omega_{A/R},\qquad f\longmapsto df,
$$

is a derivation.

<!-- upstream_entity: Kähler-Modul/C über R/Aufgabe -->

## Exercise 18.8 {#br-bgk-2019-w18-ex08}

Determine $\Omega_{\mathbb C/\mathbb R}$.

<!-- upstream_entity: Kähler-Modul/Endliche Körpererweiterung/Separabel/Aufgabe -->

## Exercise 18.9 {#br-bgk-2019-w18-ex09}

Let $K\subseteq L$ be a finite separable field extension. Prove that

$$
\Omega_{L/K}=0.
$$

<!-- upstream_entity: Kähler-Modul/Zi über Z/Aufgabe -->

## Exercise 18.10 {#br-bgk-2019-w18-ex10}

Determine $\Omega_{\mathbb Z[i]/\mathbb Z}$.

<!-- upstream_entity: Graph/Kähler-Modul/Frei/Aufgabe -->

## Exercise 18.11 {#br-bgk-2019-w18-ex11}

Let $R$ be a commutative ring and let

$$
A=R[X_1,\ldots,X_n]/(X_n-f(X_1,\ldots,X_{n-1}))
$$

with $f\in R[X_1,\ldots,X_{n-1}]$, so that the zero locus is the graph of $f$. Prove in two different ways that $\Omega_{A/R}$ is a free $A$-module of rank $n-1$.

The following exercises concern tensor products of modules and algebras; see also the appendix.

<!-- upstream_entity: Z-Moduln/Tensorprodukt/Z mod 5 und Q/Aufgabe -->

## Exercise 18.12 {#br-bgk-2019-w18-ex12}

Calculate $\mathbb Q\otimes_{\mathbb Z}\mathbb Z/(5)$.

<!-- upstream_entity: Abelsche Gruppen/Endlich erzeugte/Tensorprodukt/Berechne/Aufgabe -->

## Exercise 18.13 {#br-bgk-2019-w18-ex13}

Calculate the tensor product

$$
\bigl(\mathbb Z^3\oplus(\mathbb Z/(2))^2\oplus\mathbb Z/(3)\bigr)
\otimes_{\mathbb Z}
\bigl(\mathbb Z^2\oplus\mathbb Z/(2)\oplus\mathbb Z/(4)\bigr).
$$

<!-- upstream_entity: Tensorprodukt/Freie endliche Moduln/Aufgabe -->

## Exercise 18.14 {#br-bgk-2019-w18-ex14}

Let $R$ be a commutative ring. Prove the $R$-module isomorphism

$$
R^n\otimes_RR^m\cong R^{nm}.
$$

<!-- upstream_entity: Kommutativer Ring/Restklassenringe/Tensorprodukt/Fakt/Beweis/Aufgabe -->

## Exercise 18.15 {#br-bgk-2019-w18-ex15}

Let $R$ be a commutative ring and let $\mathfrak a,\mathfrak b\subseteq R$ be ideals. Prove the $R$-algebra isomorphism

$$
R/\mathfrak a\otimes_RR/\mathfrak b
=R/(\mathfrak a+\mathfrak b).
$$

<!-- upstream_entity: Kommutativer Ring/Nenneraufnahmen/Tensorprodukt/Fakt/Beweis/Aufgabe -->

## Exercise 18.16 {#br-bgk-2019-w18-ex16}

Let $R$ be a commutative ring and let $S,T\subseteq R$ be multiplicative systems. Prove the $R$-algebra isomorphism

$$
R_S\otimes_RR_T=R_{S\cdot T}.
$$

<!-- upstream_entity: Monoidringe/Tensorprodukt/Aufgabe -->

## Exercise 18.17 ★ {#br-bgk-2019-w18-ex17}

Let $M$ and $N$ be commutative monoids and let $R$ be a commutative ring. Prove the $R$-algebra isomorphism

$$
R[M\times N]\cong R[M]\otimes_RR[N].
$$

<!-- upstream_entity: Kähler-Differentiale/Nenneraufnahme über Ring/Aufgabe -->

## Exercise 18.18 ★ {#br-bgk-2019-w18-ex18}

Let $A$ be a commutative ring and let $S\subseteq A$ be a multiplicative system. Prove that

$$
\Omega_{A_S/A}=0.
$$

<!-- upstream_entity: Kähler-Differentiale/Nenneraufnahme/Fakt/Beweis/Aufgabe -->

## Exercise 18.19 {#br-bgk-2019-w18-ex19}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $S\subseteq A$ be a multiplicative system. Prove that

$$
\Omega_{A_S/R}\cong(\Omega_{A/R})_S.
$$

<!-- upstream_entity: Kähler-Differentiale/Konormalensequenz/Positive Charakteristik/Variablenpotenz/Aufgabe -->

## Exercise 18.20 {#br-bgk-2019-w18-ex20}

Discuss Lemma 18.8 in the case where $R=K$ is a field of positive characteristic $p$, $A=K[X]$, and $I=(X^p)$.

<!-- upstream_entity: E8-Singularität/Kähler-Modul/Aufgabe -->

## Exercise 18.21 {#br-bgk-2019-w18-ex21}

For

$$
A=\mathbb C[X,Y,Z]/(X^2+Y^3+Z^5),
$$

describe the module of Kähler differentials by generators and relations.

<!-- upstream_entity: Kähler-Modul/C über R/Restklassenbeschreibung/Aufgabe -->

## Exercise 18.22 {#br-bgk-2019-w18-ex22}

Determine $\Omega_{\mathbb C/\mathbb R}$ using Corollary 18.9.

<!-- upstream_entity: Nichtseparable Standarderweiterung/Kotangentialraum und Kählerversion/Aufgabe -->

## Exercise 18.23 {#br-bgk-2019-w18-ex23}

Let $p$ be a prime number. Consider the field extension given by

$$
K=\mathbb Z/(p)(U)\subseteq\mathbb Z/(p)(Y)=L,
\qquad U\longmapsto Y^p.
$$

Prove that Lemma 18.14 does not hold in this situation.

<!-- upstream_entity: Nichtvollkommener Körper/Regulär/Kählermodul nicht frei/Aufgabe -->

## Exercise 18.24 {#br-bgk-2019-w18-ex24}

Let $p$ be a prime number and let

$$
K=\mathbb Z/(p)(U)\subseteq
R=K[Y]/(Y^p-U).
$$

Prove that $R\cong K(Y)$, that $R$ is regular, and that the module of Kähler differentials $\Omega_{R/K}$ is not free.

> **Editorial note — inconsistent source conclusion.** The final claim is false for the displayed ring. If $y$ is the residue class of $Y$, then $R=K(y)\cong\mathbb F_p(y)$ is a field with $U=y^p$, hence is regular of dimension $0$. Corollary 18.9 gives $\Omega_{R/K}=R\,dy$, since $d(Y^p-U)=0$ relative to $K$. It is therefore free of rank $1$, not nonfree. Here $K(y)$ means the field generated by the algebraic element $y$, not a rational function field in an independent variable over $K$. The source exercise is retained with this diagnosis; no replacement exercise or public source solution is asserted. Its rank differs from $\dim R$, and the natural map $K\to R/\mathfrak m=R$ is not an isomorphism, so it also fails the residue-field hypothesis used in Theorem 18.17.

<!-- upstream_entity: Zweidimensionale Sphäre/Kählermodul/Lokal frei/Explizit/Aufgabe -->

## Exercise 18.25 {#br-bgk-2019-w18-ex25}

Let

$$
R=\mathbb R[X,Y,Z]/(X^2+Y^2+Z^2-1).
$$

Prove that the $R$-module of Kähler differentials

$$
\Omega_{R/\mathbb R}
=RdX\oplus RdY\oplus RdZ/(XdX+YdY+ZdZ)
$$

becomes free when restricted to the open sets $D(X),D(Y),D(Z)$, so that, for example, $(\Omega_{R/\mathbb R})_X=\Omega_{R_X/\mathbb R}$, and deduce that $\Omega_{R/\mathbb R}$ is locally free.
