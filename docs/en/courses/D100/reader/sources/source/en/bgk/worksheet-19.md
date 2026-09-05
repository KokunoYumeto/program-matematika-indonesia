---
title: "Worksheet 19 - Tangent Bundles"
stable_id: br-bgk-2019-w19
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 19"
upstream_pageid: 110228
upstream_revid: 617377
upstream_timestamp: "2020-02-11T17:14:48Z"
upstream_mediawiki_sha1: e8bfe61141c279e01d73db7311fbd7842378f7ee
source_url: "https://de.wikiversity.org/w/index.php?oldid=617377"
authority_manifest: authority/wikiversity-bgk/unit-19/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ffd4e79d12cd6fd63836cb6d7fd17e5dc6481f3befaeb50efeb9a47c4cc70512
authority_manifest_status: "Complete terminal authority freeze; all 33 file records have been recomputed without mismatches."
worksheet_xml: authority/wikiversity-bgk/unit-19/worksheet-19.xml
worksheet_xml_sha256: c5237f3f8c6ccca68151c05caede35449f1737da3a7cfe0986900b2c8072f186
worksheet_expanded_tex: authority/wikiversity-bgk/unit-19/worksheet-19-expanded.tex
worksheet_expanded_tex_sha256: 3e7da405f0b52b7e2c5a3831ce99214a3a3fed9221fc54d2b55f247a0cd101fc
official_pdf: authority/artifacts/bgk-worksheet-19-official.pdf
official_pdf_sha256: 7b9a60924fac5d61d119a9a6156a7c22ce767a10a0dc645c4ff188a53c900283
official_pdf_status: "Local official PDF witness; 54,883 bytes, 5 pages, and upload SHA-1 1b67f5b59317b2e082f112250a2612d7a4e22ac8 have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-19/official-pdfs-api.json
official_pdf_metadata_sha256: a37c74918c2fea4dd11a6ce3f9aee6d903596250bf8471c3d089d1c162fbb2af
official_pdf_source_bytes: 54883
official_pdf_source_sha1: 1b67f5b59317b2e082f112250a2612d7a4e22ac8
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
ordered_exercise_map: authority/wikiversity-bgk/unit-19/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 93905796d627d6ce9fe5926808e2589c25c4513ca38d14c9099ca91693805af6
exercise_count: 12
public_solution_count: 1
public_solution_numbers: "10"
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

# Worksheet 19: Tangent Bundles {#br-bgk-2019-w19}

The star marks exactly one exercise with a frozen public solution, Exercise 19.10. The other eleven exercises have negative candidate results; this edition does not invent new solutions.

<!-- upstream_entity: Achsenkreuz/Kähler-Differentiale/Nicht frei im Nullpunkt/Aufgabe -->

## Exercise 19.1 {#br-bgk-2019-w19-ex01}

Let

$$
R=K[X,Y]/(XY).
$$

Show that the module of Kähler differentials $\Omega_{R\mid K}$ is not free at the origin.

<!-- upstream_entity: Glattes Schema/Nichtzusammenhängend/Kählermodul/Rang/Aufgabe -->

## Exercise 19.2 {#br-bgk-2019-w19-ex02}

Show that there is a smooth scheme of finite type over a field whose module of Kähler differentials does not have constant rank.

<!-- upstream_entity: Kommutativer Ring/Modul/Derivation/Spektrum/Aufgabe -->

## Exercise 19.3 {#br-bgk-2019-w19-ex03}

Let $R$ be a commutative ring, let $A$ be a commutative algebra over $R$, let $M$ be an $A$-module, and let $\delta:A\to M$ be an $R$-derivation. Show that on every open set $U\subseteq\operatorname{Spek}(A)$ there is an $R$-derivation

$$
\delta_U:\Gamma(U,\mathcal O_U)
\longrightarrow\Gamma(U,\widetilde M)
$$

commuting with $\delta$.

> **Hint.** First consider the open sets $D(f)$.

<!-- upstream_entity: Integres Schema/Basischema/Derivation/Funktionenkörper/Aufgabe -->

## Exercise 19.4 {#br-bgk-2019-w19-ex04}

Let $p:X\to S$ be a dominant morphism of integral schemes. Show that a derivation over $p^{-1}\mathcal O_S$ defined on an open set $U\subseteq X$,

$$
\delta:\mathcal O_U\longrightarrow\mathcal O_U,
$$

defines a $Q(S)$-derivation

$$
Q(X)\longrightarrow Q(X).
$$

> **Editorial note — dominance.** The source does not assume that $p$ is dominant. Without dominance there is generally no induced embedding $Q(S)\hookrightarrow Q(X)$, so the claimed $Q(S)$-derivation is not defined. This edition adds the required hypothesis.

<!-- upstream_entity: Schema/Endlicher Typ/Kohärente Garbe/Aufgabe -->

## Exercise 19.5 {#br-bgk-2019-w19-ex05}

Let $X$ be a scheme of finite type over a locally Noetherian base scheme $S$. Show that $\Omega_{X\mid S}$ is a coherent $\mathcal O_X$-module.

> **Editorial note — coherence.** The source allows an arbitrary base scheme. Finite type alone makes $\Omega_{X\mid S}$ finite type, but does not ensure coherence over a non-Noetherian base. The locally Noetherian hypothesis stated here makes $X$ locally Noetherian and gives the claimed coherence.

<!-- upstream_entity: Schema/Kähler-Differentiale/Prägarbe/Aufgabe -->

## Exercise 19.6 {#br-bgk-2019-w19-ex06}

Let $p:X\to S$ be a scheme over a scheme $S$. Show that the sheaf of Kähler differentials $\Omega_{X\mid S}$ on $X$ is the sheafification of the presheaf

$$
U\longmapsto
\operatorname*{colim}_{\substack{V\subseteq S\text{ open}\\
U\subseteq p^{-1}(V)}}
\Omega_{\Gamma(U,\mathcal O_X)\mid\Gamma(V,\mathcal O_S)}.
$$

<!-- upstream_entity: Projektive Gerade/Kählermodul/Aufgabe -->

## Exercise 19.7 {#br-bgk-2019-w19-ex07}

Show that the module of Kähler differentials $\Omega_{\mathbb P_R^1\mid R}$ on the projective line $\mathbb P_R^1$ over a commutative ring $R$ is isomorphic to the twisted structure sheaf $\mathcal O_{\mathbb P_R^1}(-2)$.

<!-- upstream_entity: Projektive Gerade/Tangentialgarbe/Globale Vektorfelder/Aufgabe -->

## Exercise 19.8 {#br-bgk-2019-w19-ex08}

Consider the tangent sheaf $\mathcal T_{\mathbb P_R^1,R}$ on the projective line $\mathbb P_R^1$ over a commutative ring $R$, with the isomorphism

$$
\mathcal T_{\mathbb P_R^1,R}
\cong\mathcal O_{\mathbb P_R^1}(2).
$$

Determine the global sections of $\mathcal O_{\mathbb P_R^1}(2)$ corresponding to the global derivations

$$
X\frac{\partial}{\partial X},\qquad
Y\frac{\partial}{\partial X},\qquad
X\frac{\partial}{\partial Y},\qquad
Y\frac{\partial}{\partial Y}.
$$

<!-- upstream_entity: Projektive Ebene/Globale Vektorfelder/Rationale Auswertung/Aufgabe -->

## Exercise 19.9 {#br-bgk-2019-w19-ex09}

On the projective plane

$$
\mathbb P_K^2=\operatorname{Proj}(K[X,Y,Z]),
$$

determine the derivative

$$
Y\frac{\partial f}{\partial X}
$$

of the rational function

$$
f=\frac{XY-YZ+3Z^2-X^2}{4X^2-YZ}.
$$

On which open subset are $f$ and $Y\frac{\partial f}{\partial X}$ defined?

<!-- upstream_entity: Fermat-Kubik/Explizite Differentialform/Aufgabe -->

## Exercise 19.10 ★ {#br-bgk-2019-w19-ex10}

Consider the curve

$$
C=V_+(X^3+Y^3+Z^3)\subseteq\mathbb P_K^2
$$

over a field of characteristic different from $3$. Show that the differential forms

$$
\frac{X^2}{Y^2}\,d\!\left(\frac ZX\right)
\quad\text{on }D_+(XY),
$$

$$
\frac{Y^2}{Z^2}\,d\!\left(\frac XY\right)
\quad\text{on }D_+(YZ),
$$

and

$$
\frac{Z^2}{X^2}\,d\!\left(\frac YZ\right)
\quad\text{on }D_+(XZ)
$$

agree on the intersections and therefore define a nontrivial differential form on the curve $C$.

<!-- upstream_entity: Projektiver Raum/Globale Derivationen/Affine Beschreibung/Aufgabe -->

## Exercise 19.11 {#br-bgk-2019-w19-ex11}

Express the restrictions of the global derivations

$$
X_i\frac{\partial}{\partial X_j}
$$

of projective space

$$
\mathbb P_R^n=\operatorname{Proj}(R[X_0,X_1,\ldots,X_n])
$$

to the open subset

$$
D_+(X_0)=\operatorname{Spek}(R[Y_1,\ldots,Y_n])
\subseteq\mathbb P_R^n,
$$

with $Y_k=X_k/X_0$, as linear combinations of the form

$$
\sum_{k=1}^n g_k\frac{\partial}{\partial Y_k},
\qquad g_k\in R[Y_1,\ldots,Y_n].
$$

<!-- upstream_entity: Fermat-Kubik/4 Variablen/Affin/Explizite Parametrisierung/Aufgabe -->

## Exercise 19.12 {#br-bgk-2019-w19-ex12}

Consider the Fermat cubic in four variables,

$$
V=V_+(X^3+Y^3+Z^3+W^3)\subseteq\mathbb P_K^3,
$$

and the affine piece

$$
U=D_+(W)\cap V
=\operatorname{Spek}\bigl(K[X,Y,Z]/(X^3+Y^3+Z^3+1)\bigr)
$$

over an algebraically closed field $K$ of characteristic different from $3$. Show that the formulae

$$
x(s,t)=
\frac{3t-\frac13(s^2+st+t^2)^2}
{t(s^2+st+t^2)-3},
$$

$$
y(s,t)=
\frac{3s+3t+\frac13(s^2+st+t^2)^2}
{t(s^2+st+t^2)-3},
$$

and

$$
z(s,t)=
\frac{-3-(s^2+st+t^2)(s+t)}
{t(s^2+st+t^2)-3}
$$

give a rational parametrisation

$$
K^2\dashrightarrow U.
$$

> **Editorial note — the rational map.** The source omits a closing parenthesis in the coordinate ring and prints an ordinary arrow $K^2\to U$. The coordinate-ring parenthesis is supplied above, and a dashed arrow is used because the displayed rational functions are defined only where $t(s^2+st+t^2)-3\ne0$.
