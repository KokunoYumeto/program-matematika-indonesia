---
title: "Worksheet 14 - Quasicoherent Modules"
stable_id: br-bgk-2019-w14
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 14"
upstream_pageid: 110221
upstream_revid: 1005264
upstream_timestamp: "2025-06-23T17:55:24Z"
upstream_mediawiki_sha1: 86f9f44b4b41b187f66c06e15294d4b2a3d11517
source_url: "https://de.wikiversity.org/w/index.php?oldid=1005264"
worksheet_xml: authority/wikiversity-bgk/unit-14/worksheet-14.xml
worksheet_xml_sha256: 8ddd8aeaf012194a6cd7982ebd0677b2f65757c2ae843007afe1c8537e411694
worksheet_expanded_tex: authority/wikiversity-bgk/unit-14/worksheet-14-expanded.tex
worksheet_expanded_tex_sha256: e6645368e0aeb0160fb3909544bae84da2e1c51ef8b07a4511a231df415b6e85
ordered_exercise_map: authority/wikiversity-bgk/unit-14/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 5e5e8e176197359fb6726abc791fc58ad61051ad150859b24f746e83cb91cac4
candidate_evidence: authority/wikiversity-bgk/unit-14/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 69af9a5a8678c2af5cb8b562b588b9eda47635744dd9cf0bcc790194396cfd5c
official_pdf_metadata: authority/wikiversity-bgk/unit-14/official-pdfs-api.json
official_pdf_metadata_sha256: 87597a5f905829e257b9997c3b4b9855ae455be7d1272aa1dec2fa0f4b5851a3
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_bytes: 2104862
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "126-130"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
exercise_count: 26
public_solution_count: 0
public_solution_numbers: ""
negative_public_solution_count: 26
negative_solution_numbers: "1-26"
media_credits: source/id-ID/media-credits-bgk-unit-14.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Worksheet 14: Quasicoherent Modules {#br-bgk-2019-w14}

At the frozen revision boundary, none of the 26 exercises has a public solution page. This edition preserves those negative candidate results and creates no new solutions.

<!-- upstream_entity: Kommutativer Ring/Ideal/Spektrumsmodul/Isomorphie/Aufgabe -->

## Exercise 14.1 {#br-bgk-2019-w14-ex01}

Let $\mathfrak a\subseteq R$ be an ideal of a commutative ring $R$, and let $X=\operatorname{Spek}(R)$. Prove that

$$
\widetilde{\mathfrak a}|_{D(\mathfrak a)}
\cong\mathcal O_X|_{D(\mathfrak a)}.
$$

<!-- upstream_entity: Kommutativer Ring/Modul/Nenneraufnahme/Spektrum/Aufgabe -->

## Exercise 14.2 {#br-bgk-2019-w14-ex02}

Let $M$ be an $R$-module over a commutative ring $R$, and let $f\in R$. Prove that

$$
\widetilde M|_{D(f)}\cong\widetilde{M_f},
$$

where the right-hand side denotes the sheaf of modules associated with the $R_f$-module $M_f$.

<!-- upstream_entity: Kommutativer Ring/Modul/Endlich erzeugter/0 in Punkt/Umgebung/Aufgabe -->

## Exercise 14.3 {#br-bgk-2019-w14-ex03}

Let $R$ be a commutative ring and $M$ a finitely generated $R$-module. Let $\mathfrak p\in\operatorname{Spek}(R)$ be a prime ideal with $M_{\mathfrak p}=0$. Prove that there is an $f\notin\mathfrak p$ with

$$
M_f=0.
$$

<!-- upstream_entity: Kommutativer Ring/Moduln/Endlich erzeugt/Homomorphismus/Surjektiv/Punkt/Aufgabe -->

## Exercise 14.4 {#br-bgk-2019-w14-ex04}

Let $R$ be a commutative ring and

$$
\varphi:M\longrightarrow N
$$

an $R$-module homomorphism between finitely generated $R$-modules. Let $\mathfrak p\in\operatorname{Spek}(R)$ be a prime ideal such that the induced homomorphism

$$
\varphi:M_{\mathfrak p}\longrightarrow N_{\mathfrak p}
$$

is surjective. Prove that there is an $f\notin\mathfrak p$ such that

$$
\varphi:M_f\longrightarrow N_f
$$

is surjective.

<!-- upstream_entity: Kommutativer Ring/Noethersch/Moduln/Endlich erzeugt/Homomorphismus/Injektiv/Punkt/Aufgabe -->

## Exercise 14.5 {#br-bgk-2019-w14-ex05}

Let $R$ be a noetherian commutative ring and

$$
\varphi:M\longrightarrow N
$$

an $R$-module homomorphism between finitely generated $R$-modules. Let $\mathfrak p\in\operatorname{Spek}(R)$ be a prime ideal such that the induced homomorphism

$$
\varphi:M_{\mathfrak p}\longrightarrow N_{\mathfrak p}
$$

is injective. Prove that there is an $f\notin\mathfrak p$ such that

$$
\varphi:M_f\longrightarrow N_f
$$

is injective.

<!-- upstream_entity: Z/Q mod Z/Nicht endlich erzeugt/Lokalisierungsphänomene/Aufgabe -->

## Exercise 14.6 {#br-bgk-2019-w14-ex06}

Using $R=\mathbb Z$ and $M=\mathbb Q/\mathbb Z$, show that the assertions in Exercises 14.3, 14.4, and 14.5 are false without the assumption of finite generation.

<!-- upstream_entity: Kommutativer Ring/Nicht noethersch/Moduln/Homomorphismus/Lokalisierungsphänomene/Aufgabe -->

## Exercise 14.7 {#br-bgk-2019-w14-ex07}

Let $K$ be a field,

$$
R=K[X_n,Y_n,\ n\in\mathbb N]/(X_nY_n,\ n\in\mathbb N),
$$

and

$$
\mathfrak p=(X_n,\ n\in\mathbb N)\subseteq R.
$$

1. Prove that $\mathfrak p$ is a prime ideal.
2. Prove that $\mathfrak p_{\mathfrak p}=0$.
3. Prove that $\mathfrak p_f\ne0$ for every $f\notin\mathfrak p$.
4. Prove that

   $$
   \varphi:R\longrightarrow R/\mathfrak p
   $$

   becomes injective after localisation at $\mathfrak p$ (and hence also bijective), but that no localisation of this homomorphism at a single element $f\notin\mathfrak p$ is injective.

<!-- upstream_entity: Integritätsbereich/Quotientenkörper/Konstante Garbe/Spektrum/Aufgabe -->

## Exercise 14.8 {#br-bgk-2019-w14-ex08}

Let $R$ be an integral domain with fraction field $Q(R)$. Prove that

$$
\widetilde{Q(R)}
$$

is a constant sheaf on the spectrum $\operatorname{Spek}(R)$.

<!-- upstream_entity: Kommutativer Ring/Moduln/Homomorphismenmodul/Spektrum/Aufgabe -->

## Exercise 14.9 {#br-bgk-2019-w14-ex09}

Let $R$ be a commutative ring and $M,N$ be $R$-modules. Prove that

$$
\widetilde{\operatorname{Hom}(M,N)}
\cong
\mathcal Hom(\widetilde M,\widetilde N).
$$

> **Editorial note - missing finiteness hypothesis.** The source states this for arbitrary modules, but the comparison is not an isomorphism in that generality. Add the hypothesis that $M$ is finitely presented (with $N$ arbitrary), so that localisation commutes with $\operatorname{Hom}_R(M,-)$. This is a correction to the exercise, not an added source solution.

<!-- upstream_entity: Punktierte Ebene/Festlegungssatz/Kein Einheitsideal/Surjektiv/Aufgabe -->

## Exercise 14.10 {#br-bgk-2019-w14-ex10}

Let

$$
U=(\mathbb A_K^2\setminus\{(0,0)\},\mathcal O_X)
$$

be the punctured affine plane. Give an example of global sections

$$
s_1,s_2\in\Gamma(U,\mathcal O_X)
$$

such that $(s_1,s_2)$ is not the unit ideal, but the associated $\mathcal O_X$-module homomorphism

$$
\mathcal O_U^2\longrightarrow\mathcal O_U,
\qquad e_i\longmapsto s_i,
$$

is surjective.

<!-- upstream_entity: Punktierte Ebene/Maximales Ideal/Kurze exakte Sequenz/Aufgabe -->

## Exercise 14.11 {#br-bgk-2019-w14-ex11}

For $R=K[X,Y]$, consider the short exact sequence

$$
0\longrightarrow R\longrightarrow R^2
\longrightarrow(X,Y)=\mathfrak m\longrightarrow0,
$$

where the right-hand map sends the standard basis vectors to the ideal generators, while the left-hand map sends $1$ to $(Y,-X)$. By Lemma 14.9, this gives an exact sequence of sheaves

$$
0\longrightarrow\mathcal O_{\operatorname{Spek}(R)}
\longrightarrow\mathcal O_{\operatorname{Spek}(R)}^2
\longrightarrow\widetilde{\mathfrak m}\longrightarrow0.
$$

Let $U=D(X,Y)$. Prove the following assertions.

1. $\Gamma(U,\mathcal O_{\operatorname{Spek}(R)})=R$.
2. $\Gamma(U,\widetilde{\mathfrak m})=R$.
3. Evaluation of this exact sequence of sheaves on $U$ gives

   $$
   0\longrightarrow R\longrightarrow R^2\longrightarrow R,
   $$

   and the right-hand map is not surjective.

<!-- upstream_entity: Ring/Ideal/Kurze exakte Sequenz/Spektrum/Aufgabe -->

## Exercise 14.12 {#br-bgk-2019-w14-ex12}

Let $R$ be a commutative ring and $I\subseteq R$ an ideal with associated short exact sequence

$$
0\longrightarrow I\longrightarrow R\longrightarrow R/I\longrightarrow0.
$$

Interpret the corresponding short exact sequence of sheaves

$$
0\longrightarrow\widetilde I\longrightarrow\widetilde R
\longrightarrow\widetilde{R/I}\longrightarrow0
$$

on the spectrum of $R$. On which open subsets and at which points do the objects—their evaluations and stalks, respectively—become zero, and the homomorphisms become isomorphisms?

<!-- upstream_entity: Ringwechsel/Spektrumsabbildung/Vorgeschobener Modul/Aufgabe -->

## Exercise 14.13 {#br-bgk-2019-w14-ex13}

Let $\theta:A\to B$ be a ring homomorphism between commutative rings $A$ and $B$, and let

$$
\varphi:\operatorname{Spek}(B)\longrightarrow\operatorname{Spek}(A)
$$

be the associated map on spectra. Let $N$ be a $B$-module with associated sheaf of modules $\widetilde N$ on $\operatorname{Spek}(B)$. Prove that

$$
\varphi_*(\widetilde N)=\widetilde{N'},
$$

where $N'$ is simply the $B$-module $N$ regarded as an $A$-module.

<!-- upstream_entity: Ringwechsel/Spektrumsabbildung/Zurückgezogener Modul/Aufgabe -->

## Exercise 14.14 {#br-bgk-2019-w14-ex14}

Let $\theta:A\to B$ be a ring homomorphism between commutative rings $A$ and $B$, and let

$$
\varphi:\operatorname{Spek}(B)\longrightarrow\operatorname{Spek}(A)
$$

be the associated map on spectra. Let $M$ be an $A$-module with associated sheaf of modules $\widetilde M$ on $\operatorname{Spek}(A)$. Prove that

$$
\varphi^*(\widetilde M)=\widetilde{M\otimes_AB}
$$

on $\operatorname{Spek}(B)$.

The following exercise describes the ring-theoretic version of Appendix Lemma 4.3. Together with the preceding two exercises, it recovers the spectrum version of that assertion.

<!-- upstream_entity: Ringwechsel/Vorgezogener und zurückgezogener Modul/Homomorphismus/Aufgabe -->

## Exercise 14.15 {#br-bgk-2019-w14-ex15}

Let $\theta:A\to B$ be a homomorphism between commutative rings $A$ and $B$. Let $M$ be an $A$-module and $N$ a $B$-module. Prove that there is a natural group isomorphism

$$
\operatorname{Hom}_B(M\otimes_AB,N)
=\operatorname{Hom}_A(M,N'),
$$

where $N'$ denotes the $B$-module $N$ regarded as an $A$-module.

<!-- upstream_entity: Affines Schema/Quasikohärenter Modul/Global/Aufgabe -->

## Exercise 14.16 {#br-bgk-2019-w14-ex16}

Let $R$ be a commutative ring and $\mathcal M$ a quasicoherent module on $\operatorname{Spek}(R)$. Prove that

$$
\mathcal M\cong\widetilde M
$$

for some $R$-module $M$.

<!-- upstream_entity: Schema/Quasikohärente Garbe/Direkte Summe/Aufgabe -->

## Exercise 14.17 {#br-bgk-2019-w14-ex17}

Let $\mathcal F$ and $\mathcal G$ be quasicoherent modules on a scheme $(X,\mathcal O_X)$. Prove that the direct sum

$$
\mathcal F\oplus\mathcal G
$$

is also quasicoherent.

<!-- upstream_entity: Schema/Kohärente Garbe/Direkte Summe/Aufgabe -->

## Exercise 14.18 {#br-bgk-2019-w14-ex18}

Let $\mathcal F$ and $\mathcal G$ be coherent modules on a scheme $(X,\mathcal O_X)$. Prove that the direct sum

$$
\mathcal F\oplus\mathcal G
$$

is also coherent.

<!-- upstream_entity: Schema/Quasikohärente Garben/Homomorphismus/Kern/Aufgabe -->

## Exercise 14.19 {#br-bgk-2019-w14-ex19}

Let $\mathcal F$ and $\mathcal G$ be quasicoherent modules on a scheme $(X,\mathcal O_X)$, and let

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

be a homomorphism. Prove that the kernel $\ker\varphi$ is also quasicoherent.

<!-- upstream_entity: Noethersches Schema/Kohärente Garben/Homomorphismus/Kern/Aufgabe -->

## Exercise 14.20 {#br-bgk-2019-w14-ex20}

Let $\mathcal F$ and $\mathcal G$ be coherent modules on a noetherian scheme $(X,\mathcal O_X)$, and let

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

be a homomorphism. Prove that the kernel $\ker\varphi$ is also coherent.

<!-- upstream_entity: Schema/Quasikohärente Garben/Homomorphismus/Kokern/Aufgabe -->

## Exercise 14.21 {#br-bgk-2019-w14-ex21}

Let $\mathcal F$ and $\mathcal G$ be quasicoherent modules on a scheme $(X,\mathcal O_X)$, and let

$$
\varphi:\mathcal F\longrightarrow\mathcal G
$$

be a homomorphism. Prove that the cokernel $\operatorname{coker}\varphi$ is also quasicoherent.

<!-- upstream_entity: Noethersches Schema/Invertierbarkeitsort/Quasikohärenter Modul/Nenneraufnahme/Aufgabe -->

## Exercise 14.22 {#br-bgk-2019-w14-ex22}

Let $(X,\mathcal O_X)$ be a noetherian scheme and

$$
f\in\Gamma(X,\mathcal O_X)
$$

a global function with invertibility locus $X_f$. Let $\mathcal M$ be a quasicoherent $\mathcal O_X$-module on $X$. Prove that

$$
\Gamma(X_f,\mathcal M)=\Gamma(X,\mathcal M)_f.
$$

> **Editorial note - base space.** The source writes $\mathcal O_U$ although the module is on $X$ and no $U$ has been introduced. This edition corrects it to $\mathcal O_X$.

<!-- upstream_entity: Noethersches Schema/Offenes Unterschema/Quasikohärenter Modul/Vorschub/Aufgabe -->

## Exercise 14.23 {#br-bgk-2019-w14-ex23}

Let $(X,\mathcal O_X)$ be a noetherian scheme and $U\subseteq X$ an open subset. Let $\mathcal M$ be a quasicoherent $\mathcal O_U$-module on $U$. Prove that the direct image

$$
i_*\mathcal M
$$

is a quasicoherent module on $X$.

Hint: first consider the case where $X$ is affine.

<!-- upstream_entity: Projektiver Raum/Funktion auf D+(x0)/Globale Liftung/Aufgabe -->

## Exercise 14.24 {#br-bgk-2019-w14-ex24}

Consider the invertible sheaf $\mathcal O_{\mathbb P_K^n}(1)$ on projective space over a field $K$, together with the global section

$$
X_0\in\Gamma(\mathbb P_K^n,\mathcal O_{\mathbb P_K^n}(1))
$$

and its invertibility locus

$$
(\mathbb P_K^n)_{X_0}=D_+(X_0).
$$

Let

$$
f\in\Gamma(D_+(X_0),\mathcal O_{\mathbb P_K^n})
$$

be a function defined on $D_+(X_0)\subseteq\mathbb P_K^n$. Prove directly that there is an $m\in\mathbb N$ such that

$$
X_0^mf\in
\Gamma\!\left(
D_+(X_0),
(\mathcal O_{\mathbb P_K^n}(1))^m\otimes
\mathcal O_{\mathbb P_K^n}
\right)
$$

comes from a global element in

$$
\Gamma\!\left(
\mathbb P_K^n,
(\mathcal O_{\mathbb P_K^n}(1))^m\otimes
\mathcal O_{\mathbb P_K^n}
\right).
$$

> **Editorial note - local section before extension.** The source places $X_0^mf$ in the global section module before asking it to extend globally. Here its initial domain is corrected to $D_+(X_0)$, where $f$ is given; the requested global target is unchanged.

<!-- upstream_entity: Projektive Gerade/Funktion auf D+(x0)/Globale Liftung/Aufgabe -->

## Exercise 14.25 {#br-bgk-2019-w14-ex25}

Consider the invertible sheaf $\mathcal O_{\mathbb P_K^1}(1)$ on the projective line

$$
\mathbb P_K^1=\operatorname{Proj}(K[X,Y])
$$

over a field $K$, together with the global section

$$
X\in\Gamma(\mathbb P_K^1,\mathcal O_{\mathbb P_K^1}(1))
$$

and its invertibility locus

$$
(\mathbb P_K^1)_X=D_+(X).
$$

For each of the following functions $f$ in $\Gamma(D_+(X),\mathcal O_{\mathbb P_K^1})$, find a suitable $n$ such that

$$
X^nf\in\Gamma(D_+(X),\mathcal O_{\mathbb P_K^1}(n))
$$

comes from an element—which one?—of $\Gamma(\mathbb P_K^1,\mathcal O_{\mathbb P_K^1}(n))$.

1. $\displaystyle\frac YX$,
2. $\displaystyle\frac{2Y^3-3Y^2X+4X^3}{X^3}$,
3. $\displaystyle\frac{Y^{17}+X^{17}}{X^{17}}$.

> **Editorial note - degree of the input.** The source puts the listed degree-zero fractions in $\mathcal O(1)$. They are regular functions, hence sections of $\mathcal O$; multiplying by $X^n$ then has degree $n$, as required by the unchanged target $\mathcal O(n)$. This edition removes the erroneous input twist.

<!-- upstream_entity: Noethersches Schema/Quasikohärente Garbe/Invertierbare Garbe/Invertierbarkeitsort/Globale Ausdehnung/Strukturgarbe/Aufgabe -->

## Exercise 14.26 {#br-bgk-2019-w14-ex26}

Specialise Theorem 14.13 to the case where $\mathcal M$ is the structure sheaf of $X$.
