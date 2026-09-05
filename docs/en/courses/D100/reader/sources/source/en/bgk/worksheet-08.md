---
title: "Worksheet 8 - Spectra and Maps on Spectra"
stable_id: br-bgk-2019-w08
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 8"
upstream_pageid: 109250
upstream_revid: 767578
upstream_timestamp: "2022-08-15T16:40:27Z"
upstream_mediawiki_sha1: 825abbae5b4bf1875f24cd915f2b37819f30d7d4
source_url: "https://de.wikiversity.org/w/index.php?oldid=767578"
authority_manifest: authority/wikiversity-bgk/unit-08/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: cadebf48e67a54a238f4b22e0abf806fbf1f81821b6d012993739ecf50dd8d32
worksheet_xml: authority/wikiversity-bgk/unit-08/worksheet-08.xml
worksheet_xml_sha256: 642586e18b22f64505bafef094cb36b3206d1fcea7f9ce62380757d8669f0b8f
worksheet_expanded_tex: authority/wikiversity-bgk/unit-08/worksheet-08-expanded.tex
worksheet_expanded_tex_sha256: 57d8a50579be711720d8125d4f7d3308ed9e07a588445d4c9ad4a40188a41b85
exercise_map: authority/wikiversity-bgk/unit-08/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: 97c9bf59cae3e34263681875e74c4ad2f0626b87f19a6e0490d127ac4c921f1a
official_pdf: authority/artifacts/bgk-worksheet-08-official.pdf
official_pdf_sha256: f32f11e7fd3ec9d3ba2f6a20a89ab23c3652b4e8026db037278d2022108208bf
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
exercise_count: 22
public_solution_count: 3
---

# Worksheet 8: Spectra and Maps on Spectra {#br-bgk-2019-w08}

<!-- upstream_entity: Maximale Ideale/Existenz/Lemma von Zorn/Aufgabe -->

## Exercise 8.1 {#br-bgk-2019-w08-ex01}

Let $R$ be a nonzero commutative ring. Use Zorn's lemma to show that $R$
has a maximal ideal.

<!-- upstream_entity: Kommutative Ringtheorie/Maximales Ideal/Primideal/Fakt/Beweis/Aufgabe -->

## Exercise 8.2 {#br-bgk-2019-w08-ex02}

Show that every maximal ideal $\mathfrak m$ in a commutative ring $R$ is
a prime ideal.

<!-- upstream_entity: Kommutative Ringtheorie/Primideal/Charakterisierung mit Restklassenring/Fakt/Beweis/Aufgabe -->

## Exercise 8.3* {#br-bgk-2019-w08-ex03}

Let $R$ be a commutative ring and let $\mathfrak p$ be an ideal. Show
that $\mathfrak p$ is prime if and only if the quotient ring

$$
R/\mathfrak p
$$

is an integral domain.

<!-- upstream_entity: Primideal/Charakterisierung als Kern nach Körper/Aufgabe -->

## Exercise 8.4* {#br-bgk-2019-w08-ex04}

Let $\mathfrak a$ be an ideal in a commutative ring $R$. Show that
$\mathfrak a$ is prime if and only if it is the kernel of a ring
homomorphism

$$
\varphi:R\longrightarrow K
$$

to a field $K$.

<!-- upstream_entity: Ideal und multiplikatives System/Disjunkt/Primideal/Zorn/Aufgabe -->

## Exercise 8.5 {#br-bgk-2019-w08-ex05}

Let $R$ be a commutative ring, let $\mathfrak a\subseteq R$ be an ideal,
and let $M\subseteq R$ be a multiplicative system with

$$
\mathfrak a\cap M=\varnothing.
$$

Use Zorn's lemma to show that there is a prime ideal $\mathfrak p$
satisfying

$$
\mathfrak a\subseteq\mathfrak p,
\qquad
\mathfrak p\cap M=\varnothing.
$$

<!-- upstream_entity: Idealtheorie (kommutative Algebra)/Ideale im Restklassenring/Korrespondenz/Aufgabe -->

## Exercise 8.6 {#br-bgk-2019-w08-ex06}

Let $R$ be a commutative ring, let $\mathfrak a$ be an ideal, and let

$$
S=R/\mathfrak a.
$$

Show that the ideals of $S$ correspond bijectively to the ideals of $R$
containing $\mathfrak a$.

<!-- upstream_entity: Nenneraufnahme/Verhalten von Primidealen/Aufgabe -->

## Exercise 8.7 {#br-bgk-2019-w08-ex07}

Let $R$ be a commutative ring and let $S\subseteq R$ be a multiplicative
system. Show that the prime ideals in $R_S$ correspond exactly to the
prime ideals in $R$ disjoint from $S$.

<!-- upstream_entity: Lokalisierung/Beschreibung des Spektrums/Aufgabe -->

## Exercise 8.8 {#br-bgk-2019-w08-ex08}

Describe the spectrum

$$
\operatorname{Spek}(R_{\mathfrak p})
$$

of the localisation of a commutative ring $R$ at a prime ideal
$\mathfrak p$.

<!-- upstream_entity: Kommutative Ringtheorie/Primideal/Unter Morphismus/Aufgabe -->

## Exercise 8.9 {#br-bgk-2019-w08-ex09}

Let $R$ and $S$ be commutative rings and let $\varphi:R\to S$ be a ring
homomorphism. If $\mathfrak p$ is a prime ideal in $S$, show that the
inverse image

$$
\varphi^{-1}(\mathfrak p)
$$

is a prime ideal in $R$.

Give an example showing that the inverse image of a maximal ideal need
not be maximal.

<!-- upstream_entity: Ringhomomorphismus/Primideal/Abbildung der Lokalisierung und der Restekörper/Aufgabe -->

## Exercise 8.10 {#br-bgk-2019-w08-ex10}

Let $\varphi:R\to S$ be a ring homomorphism between commutative rings $R$
and $S$, and let $\mathfrak p\in\operatorname{Spek}(S)$ be a prime ideal.
Show that there are natural ring homomorphisms

$$
R_{\varphi^{-1}(\mathfrak p)}\longrightarrow S_{\mathfrak p}
$$

between the localisations, and

$$
\kappa\!\left(\varphi^{-1}(\mathfrak p)\right)
\longrightarrow\kappa(\mathfrak p)
$$

between the residue fields.

<!-- upstream_entity: Integre endlich erzeugte Algebren/Lokaler Isomorphismus/In Umgebung/Aufgabe -->

## Exercise 8.11* {#br-bgk-2019-w08-ex11}

Let $K$ be a field, and let $R$ and $S$ be finitely generated
$K$-algebras that are integral domains. Let

$$
\varphi:R\longrightarrow S
$$

be a $K$-algebra homomorphism, and let $\mathfrak n$ be a maximal ideal
in $S$ with

$$
\varphi^{-1}(\mathfrak n)=\mathfrak m.
$$

Suppose the map induces an isomorphism

$$
R_{\mathfrak m}\longrightarrow S_{\mathfrak n}.
$$

Show that there is $f\in R$ with $f\notin\mathfrak m$ such that

$$
R_f\longrightarrow S_{\varphi(f)}
$$

is an isomorphism.

<!-- upstream_entity: Reduktion/Spektrumsabbildung/Homöomorphismus/Aufgabe -->

## Exercise 8.12 {#br-bgk-2019-w08-ex12}

Show that the map on spectra associated with the reduction

$$
R\longrightarrow R/\mathfrak n_R
$$

of a commutative ring $R$ is a homeomorphism.

<!-- upstream_entity: Kommutative Ringtheorie/Charakteristik/Positiv/Frobenius/Existenz/Aufgabe -->

## Exercise 8.13 {#br-bgk-2019-w08-ex13}

Let $R$ be a commutative ring containing a field of positive
characteristic

$$
p>0,
$$

where $p$ is prime. Show that the map

$$
\begin{aligned}
R&\longrightarrow R,\\
f&\longmapsto f^p
\end{aligned}
$$

is a ring homomorphism, called the *Frobenius homomorphism*.

<!-- upstream_entity: Frobeniushomomorphismus/Spektrumsabbildung/Homöomorphismus/Aufgabe -->

## Exercise 8.14 {#br-bgk-2019-w08-ex14}

Let $R$ be a commutative ring of positive characteristic $p>0$. Show that
the map on spectra associated with the Frobenius homomorphism

$$
\begin{aligned}
R&\longrightarrow R,\\
f&\longmapsto f^p
\end{aligned}
$$

is a homeomorphism.

> **Edition note — characteristic hypothesis.** Here $p$ must be prime, as
> in Exercise 8.13. A unital ring can have composite positive
> characteristic, for which $f\mapsto f^p$ need not be a ring
> homomorphism. The source leaves the word “prime” implicit in this
> exercise.

<!-- upstream_entity: Kommutativer Ring/Produktring/Spektrum/Fakt/Beweis/Aufgabe -->

## Exercise 8.15 {#br-bgk-2019-w08-ex15}

Let $R_1$ and $R_2$ be commutative rings and let

$$
R=R_1\times R_2
$$

be their product ring. Show that there is a natural homeomorphism

$$
\operatorname{Spek}(R_1)\uplus\operatorname{Spek}(R_2)
\longrightarrow\operatorname{Spek}(R_1\times R_2).
$$

<!-- upstream_entity: Polynomring/Mehrere Variablen/Fasern der Spektrumsabbildung/Aufgabe -->

## Exercise 8.16 {#br-bgk-2019-w08-ex16}

Let $R$ be a commutative ring. Determine the fibres of the map on spectra
associated with the ring extension

$$
R\subseteq R[X_1,\ldots,X_n].
$$

<!-- upstream_entity: RX in CX/Spektrumsabbildung/Fasern/Aufgabe -->

## Exercise 8.17 {#br-bgk-2019-w08-ex17}

Determine the fibres of the map on spectra associated with

$$
\mathbb R[X]\subseteq\mathbb C[X].
$$

When the ground field is the complex numbers, the $\mathbb C$-spectrum
also has a complex topology, which is much finer than the Zariski topology.
The following exercises develop this.

<!-- upstream_entity: C-Spektrum/Natürliche Topologie/Aufgabe -->

## Exercise 8.18 {#br-bgk-2019-w08-ex18}

Let $R$ be a finitely generated commutative $\mathbb C$-algebra. Show that
the $\mathbb C$-spectrum

$$
\mathbb C\!\operatorname{-Spek}(R)
$$

has a *natural topology* (or *complex topology*) that, for the polynomial
ring $\mathbb C[X_1,\ldots,X_n]$, agrees with the metric topology on
$\mathbb C^n$. Show also that, for a $\mathbb C$-algebra homomorphism

$$
\varphi:R\longrightarrow S
$$

between finitely generated $\mathbb C$-algebras, the induced map

$$
\mathbb C\!\operatorname{-Spek}(S)
\longrightarrow
\mathbb C\!\operatorname{-Spek}(R)
$$

is continuous in the natural topology.

<!-- upstream_entity: Polynom/C nach C/Ganz/Urbild beschränkt/Aufgabe -->

## Exercise 8.19 {#br-bgk-2019-w08-ex19}

Let $P\in\mathbb C[X]$ be a nonconstant polynomial. Show that the function

$$
\begin{aligned}
\mathbb C&\longrightarrow\mathbb C,\\
z&\longmapsto P(z)
\end{aligned}
$$

has the property that the inverse image of every bounded subset
$T\subseteq\mathbb C$ is bounded.

<!-- upstream_entity: Polynom/C/Mehrere Variablen/Ganz/Urbild beschränkt/Aufgabe -->

## Exercise 8.20 {#br-bgk-2019-w08-ex20}

Let

$$
F_1,\ldots,F_k\in\mathbb C[X_1,\ldots,X_n]
$$

be polynomials such that the $\mathbb C$-algebra homomorphism

$$
\begin{aligned}
\mathbb C[Y_1,\ldots,Y_k]&\longrightarrow
\mathbb C[X_1,\ldots,X_n],\\
Y_j&\longmapsto F_j
\end{aligned}
$$

is integral. Show that the associated map

$$
\begin{aligned}
\mathbb C^n&\longrightarrow\mathbb C^k,\\
(x_1,\ldots,x_n)&\longmapsto
(F_1(x_1,\ldots,x_n),\ldots,F_k(x_1,\ldots,x_n))
\end{aligned}
$$

has the property that the inverse image of every bounded subset
$T\subseteq\mathbb C^k$ is again bounded.

Deduce that, in this situation, the map $F$ is proper, meaning that inverse
images of compact subsets are compact, and that $F$ is a closed map.

<!-- upstream_entity: QX in RX/Spektrumsabbildung/Fasern/Aufgabe -->

## Exercise 8.21 {#br-bgk-2019-w08-ex21}

Determine the fibres of the map on spectra associated with

$$
\mathbb Q[X]\subseteq\mathbb R[X].
$$

Which fibres are finite?

<!-- upstream_entity: Ringhomomorphismus/Spektrumsabbildung/Faserbeschreibung/Tensorprodukt/Aufgabe -->

## Exercise 8.22 {#br-bgk-2019-w08-ex22}

Let $\varphi:R\to S$ be a ring homomorphism between commutative rings,
and let

$$
\begin{aligned}
\varphi^*:\operatorname{Spek}(S)&\longrightarrow\operatorname{Spek}(R),\\
\mathfrak p&\longmapsto\varphi^*(\mathfrak p)
\end{aligned}
$$

be the associated map on spectra. Show that the fibre over a prime ideal
$\mathfrak p\in\operatorname{Spek}(R)$ is canonically homeomorphic to

$$
\operatorname{Spec}\!\left(S\otimes_R\kappa(\mathfrak p)\right).
$$

> **Edition note — source notation.** The final exercise uses
> $\operatorname{Spec}$, whereas the lecture and preceding exercises use
> $\operatorname{Spek}$. This source difference is preserved; both symbols
> denote the spectrum of a ring.
