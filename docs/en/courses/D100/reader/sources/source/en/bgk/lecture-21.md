---
title: "Lecture 21 - Normal Schemes"
stable_id: br-bgk-2019-l21
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 21"
upstream_pageid: 109025
upstream_revid: 793614
upstream_timestamp: "2022-08-25T06:23:48Z"
upstream_mediawiki_sha1: 937e82c634f49d87e1555222366229d89f65aef0
source_url: "https://de.wikiversity.org/w/index.php?oldid=793614"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
authority_manifest: authority/wikiversity-bgk/unit-21/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 684637decc945c94137670f7c4238110b4a4c395287cf985b3f69adceedd9ef7
authority_manifest_status: "Terminal authority freeze complete; all 35 file records have been recomputed without discrepancies."
unit_capture_identity: authority/wikiversity-bgk/unit-21/CAPTURE_IDENTITY.json
unit_capture_identity_sha256: 869931efce9e3df0e42984b2db28fc367f93f113a8d632175ac0f9d7414cb791
lecture_api: authority/wikiversity-bgk/unit-21/lecture-21-api.json
lecture_api_sha256: 9dbf8ae5a489a2a6cb88cf63cf0220382a14f7fda7caf2f413e97d2b3bcf90d1
lecture_xml: authority/wikiversity-bgk/unit-21/lecture-21.xml
lecture_xml_sha256: e6b557402bf4338a73831da5d496b873bcec4c27f6ac317e7df5bbe0bb2427f8
lecture_html: authority/wikiversity-bgk/unit-21/lecture-21.html
lecture_html_sha256: c8c8dae22b766c2a17ab06b247677ada97feae22818fb2804bce6816fb0b6a64
lecture_expanded_tex: authority/wikiversity-bgk/unit-21/lecture-21-expanded.tex
lecture_expanded_tex_sha256: dc17c27ab323951d1301bb6c771d65ae3cc5f37f4631476145b61054e2926ff8
official_pdf: authority/artifacts/bgk-lecture-21-official.pdf
official_pdf_pages: 5
official_pdf_sha256: 31ddf1226d25837e8e79f15417008616f2d054337f06043feeea581b6d3ed606
official_pdf_metadata: authority/wikiversity-bgk/unit-21/official-pdfs-api.json
official_pdf_metadata_sha256: 4be79ab72566114ba54376bbb902cb00346bc9237e4d8ac988345b78cfc2a2ca
official_pdf_source_bytes: 60765
official_pdf_source_sha1: ca80c1b369883e1c6c9940ba58d42d1ed22e2746
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_pages: "186-189"
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revisions govern the text; the official 2020 PDFs are historical witnesses only."
media_credits: source/id-ID/media-credits-bgk-unit-21.md
media_credits_sha256: 07ef5ecaa38890028ebbc245b3511bfb3eb8a29b174c8802dd84a3492496d814
rights_ledger: authority/RIGHTS-bgk-unit-21.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-21.json
asset_closure_sha256: 5fd26087ca516efbb8cbc6823c3622338bd9272eb7ab1452c87ba41c6e28afdd
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDFs are authority witnesses, not the edition text; the Commons CC BY-SA 4.0 metadata and embedded CC-by-sa 3.0 notices are preserved without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 21: Normal Schemes {#br-bgk-2019-l21}

## Normal rings {#br-bgk-2019-l21-s01}

<!-- upstream_entity: Kommutativer Ring/Totaler Quotientenring/Definition -->

### Definition 21.1: total quotient ring {#br-bgk-2019-l21-def-01}

Let $R$ be a commutative ring and $S\subseteq R$ the set of all
non-zero-divisors in $R$. The localisation $R_S$ is called the *total quotient
ring* of $R$ and is denoted by

$$
Q(R).
$$

<!-- upstream_entity: Kommutativer Ring/Normal/Definition -->

### Definition 21.2: normal ring {#br-bgk-2019-l21-def-02}

A commutative ring is called *normal* if it is integrally closed in its
total quotient ring.

<!-- upstream_entity: Kommutativer Ring/Normalisierung/Definition -->

### Definition 21.3: normalisation {#br-bgk-2019-l21-def-03}

Let $R$ be a commutative ring and $Q(R)$ its total quotient ring.
The integral closure of $R$ in $Q(R)$ is called the *normalisation* of $R$.

<!-- upstream_entity: Achsenkreuz/Normalisierung/Beispiel -->

### Example 21.4: normalisation of the coordinate cross {#br-bgk-2019-l21-exm-01}

We determine the normalisation of the ring

$$
K[X,Y]/(XY)
$$

over a field $K$. The element $X+Y$ is a non-zero-divisor. For the element

$$
\frac{X-Y}{X+Y}\in Q(R)
$$

we have

$$
\left(\frac{X-Y}{X+Y}\right)^2
=\frac{(X-Y)^2}{(X+Y)^2}
=\frac{X^2+Y^2}{X^2+Y^2}
=1.
$$

Thus this element satisfies an equation of integral dependence and hence
belongs to the normalisation.

> **Editorial note - scope of the source example.** The source announces
> a determination of the normalisation, but the available passage only proves
> that $(X-Y)/(X+Y)$ is integral over $R$. This edition does not complete
> a calculation that the source does not supply. The source also switches to
> the notation $Q(R)$ without first assigning the symbol $R$ to the displayed ring.

## Discrete valuation rings {#br-bgk-2019-l21-s02}

<!-- upstream_entity: Kommutative Ringtheorie/Diskreter Bewertungsring/Definition -->

### Definition 21.5: discrete valuation ring {#br-bgk-2019-l21-def-04}

A *discrete valuation ring* $R$ is a principal ideal domain with exactly
one prime element up to association.

<!-- upstream_entity: Diskreter Bewertungsring/Ordnung/Definition -->

### Definition 21.6: order {#br-bgk-2019-l21-def-05}

Let $f\in R$, $f\ne0$, be an element of a discrete valuation ring
$R$ with prime element $p$. The number $n\in\mathbb N$ satisfying

$$
f=up^n,
$$

where $u$ is a unit, is called the *order* of $f$ and is denoted by

$$
\operatorname{ord}(f).
$$

<!-- upstream_entity: Diskreter Bewertungsring/Ordnungsfunktion/Erste Eigenschaften/Fakt -->

### Lemma 21.7: properties of the order {#br-bgk-2019-l21-lem-01}

Let $R$ be a discrete valuation ring with maximal ideal
$\mathfrak m=(p)$. The order map

$$
R\setminus\{0\}\longrightarrow\mathbb N,
\qquad
f\longmapsto\operatorname{ord}(f),
$$

has the following properties.

1. We have

   $$
   \operatorname{ord}(fg)
   =\operatorname{ord}(f)+\operatorname{ord}(g).
   $$

2. We have

   $$
   \operatorname{ord}(f+g)
   \geq\min\{\operatorname{ord}(f),\operatorname{ord}(g)\}.
   $$

3. We have $f\in\mathfrak m$ if and only if
   $\operatorname{ord}(f)\geq1$.
4. We have $f\in R^\times$ if and only if
   $\operatorname{ord}(f)=0$.

#### Proof {#br-bgk-2019-l21-lem-01-proof}

See [Exercise 21.7](worksheet-21.md#br-bgk-2019-w21-ex07).

> **Editorial note - domain of the order function.** The source defines
> $\operatorname{ord}$ on $R\setminus\{0\}$, but part 2 does not exclude
> $f+g=0$. The source statement is preserved; if $\operatorname{ord}(0)$
> is not defined, the inequality is meaningful only for $f+g\ne0$.

We quote the following characterisation theorem. In particular, it says that
one-dimensional normal local integral domains are discrete valuation rings,
and hence unique factorisation domains and regular. Consequently, for a
normal Noetherian integral domain $R$, all localisations at prime ideals
of height $1$ are discrete valuation rings.

> **Editorial note - Noetherian hypothesis.** The first sentence in the
> source omits the Noetherian hypothesis. Its conclusion is intended under
> that hypothesis, as stated explicitly in Theorem 21.8; normality and
> dimension one alone do not imply that a local domain is a discrete valuation ring.

<!-- upstream_entity: Diskrete Bewertungsringe/Charakterisierung/1/Fakt -->

### Theorem 21.8: characterisation of discrete valuation rings {#br-bgk-2019-l21-thm-01}

Let $R$ be a Noetherian local integral domain with exactly two prime ideals

$$
0\subset\mathfrak m.
$$

The following statements are equivalent.

1. $R$ is a discrete valuation ring.
2. $R$ is a principal ideal domain.
3. $R$ is a unique factorisation domain.
4. $R$ is normal.
5. $\mathfrak m$ is a principal ideal.

<!-- upstream_entity: Diskreter Bewertungsrin/K/Restklassenkörper/Ordnung/Fakt -->

### Lemma 21.9: order as a vector-space dimension {#br-bgk-2019-l21-lem-02}

Let $K$ be a field and $B$ a discrete valuation ring over $K$ whose
residue field is $K$. For every $f\in B$, $f\ne0$, the order of $f$
equals the dimension of $B/(f)$ as a vector space over $K$:

$$
\operatorname{ord}(f)=\dim_K(B/(f)).
$$

#### Proof {#br-bgk-2019-l21-lem-02-proof}

This follows from [Exercise 21.2](worksheet-21.md#br-bgk-2019-w21-ex02)
by induction on the order of $f$.

## Normal schemes {#br-bgk-2019-l21-s03}

<!-- upstream_entity: Normales Schema/Einführung/Textabschnitt -->

### Definition 21.10: normal scheme {#br-bgk-2019-l21-def-06}

A scheme $X$ is called *normal* if every local ring
$\mathcal O_x$, for $x\in X$, is a normal ring.

### Lemma 21.11: affine criteria for normality {#br-bgk-2019-l21-lem-03}

For a scheme $(X,\mathcal O_X)$, the following properties are equivalent.

1. $X$ is normal.
2. For every affine open subset $U=\operatorname{Spek}(R)$ of
   $X$, the ring $R$ is normal.
3. There is an affine open cover

   $$
   X=\bigcup_{i\in I}U_i,
   \qquad
   U_i=\operatorname{Spek}(R_i),
   $$

   with every $R_i$ a normal ring.

#### Proof {#br-bgk-2019-l21-lem-03-proof}

The implication $(2)\Rightarrow(3)$ is immediate. Suppose (3) holds.
For every point $x\in X$, there is therefore an affine open neighbourhood

$$
x\in U=\operatorname{Spek}(R)\subseteq X
$$

with $R$ normal. Here

$$
\mathcal O_x=R_{\mathfrak p}
$$

for a prime ideal $\mathfrak p$ of $R$. By
[Theorem 42.3 in Commutative Algebra](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Normal/Nenneraufnahme_ist_normal/Fakt),
$R_{\mathfrak p}$ is also normal.

> **Editorial note - directions of implication in the source.** The source
> states three equivalent properties and gives $(2)\Rightarrow(3)$ and
> $(3)\Rightarrow(1)$, but does not supply an argument for
> $(1)\Rightarrow(2)$. This edition does not invent an unavailable proof.

<!-- upstream_entity: Normaler noetherscher Bereich/Durchschnitt/Lokalisierungen zur Höhe 1/Fakt -->

### Theorem 21.12: intersection of height-one localisations {#br-bgk-2019-l21-thm-02}

Let $R$ be a normal Noetherian integral domain. Then

$$
R=\bigcap_{\mathfrak p}R_{\mathfrak p},
$$

where $\mathfrak p$ ranges over all prime ideals of height $1$ in $R$.

#### Proof {#br-bgk-2019-l21-thm-02-proof}

Let $f=g/h\in Q(R)$ and suppose that $f\notin R$. By
[Lemma 44.12 in Commutative Algebra](https://de.wikiversity.org/wiki/Noetherscher_Integrit%C3%A4tsbereich/Durchschnittseigenschaft/Assoziierte_Primideale/Fakt),
there is a prime ideal $\mathfrak p$ associated to a quotient ring by
a principal ideal such that

$$
f\notin R_{\mathfrak p}.
$$

Thus $\mathfrak p$ is the annihilator ideal of an element $x$ modulo
a principal ideal $(y)$. By localising, we may assume that $\mathfrak p$
is the maximal ideal of $R$. Consider the $R$-submodule

$$
N=\{q\in Q(R)\mid q\mathfrak p\subseteq R\}\subseteq Q(R).
$$

We have

$$
\mathfrak p\subseteq\mathfrak pN\subseteq R.
$$

Since $\mathfrak p$ is maximal, either

$$
\mathfrak p=\mathfrak pN
$$

or

$$
\mathfrak pN=R.
$$

In the first case,
[Lemma 41.7 in Commutative Algebra](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Ganzheit/Ganzes_Element/Charakterisierung/Fakt)
says that the elements of $N$ are integral over $R$. Normality of $R$
then gives $N=R$.
Since

$$
x\mathfrak p\subseteq(y),
$$

we also have

$$
\frac{x}{y}\mathfrak p\subseteq R,
$$

and hence

$$
\frac{x}{y}\in N=R,
$$

a contradiction. Thus the second case holds: $\mathfrak pN=R$.
There must therefore be elements $a\in\mathfrak p$ and $q\in N$ satisfying

$$
aq=1.
$$

For $b\in\mathfrak p$, we then have

$$
bq=\frac ba\in R.
$$

Thus $b\in(a)$, so $\mathfrak p=(a)$ is a principal ideal.
By [Theorem 21.8](#br-bgk-2019-l21-thm-01), $R$ is a discrete valuation
ring and $\mathfrak p$ has height $1$.

> **Editorial note - details implicit in the source proof.** The fraction
> $x/y$ need not equal $g/h$: the associated-prime description supplies a
> non-zero class of $x$ modulo $(y)$, which gives the required contradiction
> when $x/y\in R$. At the final step, the non-zero principal maximal ideal
> has height $1$ by the principal ideal theorem; this supplies the
> dimension hypothesis needed to apply Theorem 21.8.
