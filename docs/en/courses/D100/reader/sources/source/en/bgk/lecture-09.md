---
title: "Lecture 9 - Affine Schemes"
stable_id: br-bgk-2019-l09
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 9"
upstream_pageid: 109013
upstream_revid: 793634
upstream_timestamp: "2022-08-25T06:26:48Z"
upstream_mediawiki_sha1: e8ee1bb24612aeb7a7b059301e772f069cfa487b
source_url: "https://de.wikiversity.org/w/index.php?oldid=793634"
authority_manifest: authority/wikiversity-bgk/unit-09/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 553255a52a560f0c4e14cf761409077d2b6788f2f8c9ace3e65b52743bfa3254
lecture_xml: authority/wikiversity-bgk/unit-09/lecture-09.xml
lecture_xml_sha256: 0efcc67ed9799e4941d199ac7f4fbab2d8b80334600b1c12f6c1437025d52fc2
lecture_expanded_tex: authority/wikiversity-bgk/unit-09/lecture-09-expanded.tex
lecture_expanded_tex_sha256: 96e87e8b5a9d845a14e47d2b6c1941cf349cad0c35f417f3979d255a9214c656
official_pdf: authority/artifacts/bgk-lecture-09-official.pdf
official_pdf_sha256: 83f58ee5ec71549c5fb5c2ccb7e119bd697ac3e3e04ca6f6c88f2ae0b379cc14
media_credits: source/id-ID/media-credits-bgk-unit-09.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF witnesses retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 9: Affine Schemes {#br-bgk-2019-l09}

Let

$$
X=\operatorname{Spek}(R)
$$

be the spectrum of a commutative ring $R$, equipped with the Zariski
topology. If $R$ is a field, its spectrum consists of just one point,
the zero ideal, which is also maximal. Viewed this way, the spectrum
alone contains very little information. Thus the contravariant functor

$$
\begin{aligned}
\{\text{commutative rings}\}&\longrightarrow
\{\text{topological spaces}\},\\
R&\longmapsto\operatorname{Spek}(R)
\end{aligned}
$$

loses information. We shall enrich the spectrum with additional structure
so that the original ring can be reconstructed from it. To do this, we
define a structure sheaf on the spectrum. The spectrum together with this
structure sheaf is a meaningful geometrisation of the ring: a ringed
space.

> **Edition note — two typos in the source introduction.** The source
> writes `dass Spektrum` and `zusätztlichen`. The translation normalises these
> to “the spectrum” and “additional”; no mathematical content is changed.

## The structure sheaf on the spectrum {#br-bgk-2019-l09-s01}

<!-- upstream_entity: Spektrum/Prägarbe/Beispiel -->

### Example 9.1: the presheaf of localisations {#br-bgk-2019-l09-exa-01}

Let $X=\operatorname{Spek}(R)$ be the spectrum of a commutative ring $R$.
On $X$, define a presheaf of commutative rings by setting, for every open
set $U\subseteq X$,

$$
\mathcal P(U):=\operatorname*{colim}_{U\subseteq D(f)}R_f,
$$

with the natural ring homomorphisms

$$
R_f\longrightarrow R_g
$$

for

$$
U\subseteq D(g)\subseteq D(f).
$$

Together with these natural homomorphisms, this assignment is a presheaf.
We have

$$
\mathcal P(D(f))=R_f,
\qquad
\mathcal P(X)=R.
$$

For the second equality, the directed system has the terminal object
$X=D(1)$, so the resulting ring is $R_1=R$.

> **Edition note — terminal object in the source.** When deducing
> $\mathcal P(X)=R$, the source writes the terminal object as
> `D(f)`. Here it is written explicitly as $X=D(1)$; the colimit
> construction is unchanged.

The stalk of this presheaf at a point $\mathfrak p\in X$ is

$$
\begin{aligned}
\operatorname*{colim}_{\mathfrak p\in U}\mathcal P(U)
&=\operatorname*{colim}_{\mathfrak p\in D(f)}\mathcal P(D(f))\\
&=\operatorname*{colim}_{f\notin\mathfrak p}R_f\\
&=R_{\mathfrak p}.
\end{aligned}
$$

This presheaf is not a sheaf. Its sheafification is the structure sheaf
on the spectrum.

<!-- upstream_entity: Affines Schema/Spektrum/Strukturgarbe/Definition -->

### Definition 9.2: structure sheaf {#br-bgk-2019-l09-def-01}

Let $X=\operatorname{Spek}(R)$ be the spectrum of a commutative ring $R$.
The *structure sheaf* on $X$ is the assignment taking each open set
$U\subseteq X$ to the commutative ring

$$
\Gamma(U,\mathcal O_X)
=\left\{
(s_{\mathfrak p})_{\mathfrak p\in U}
\in\prod_{\mathfrak p\in U}R_{\mathfrak p}
\ \middle|\
\begin{array}{l}
\text{for every }\mathfrak p\in U\text{ there are }a,b\in R\text{ with}\\
\mathfrak p\in D(b)\subseteq U\text{ and }
s_{\mathfrak q}=\dfrac{a}{b}\text{ in }R_{\mathfrak q}\\
\text{for every }\mathfrak q\in D(b)
\end{array}
\right\}.
$$

For each inclusion $U\subseteq U'$, the restriction homomorphism is the
natural projection from the family indexed by $U'$ to the family indexed
by $U$.

<!-- upstream_entity: Spektrum/Strukturgarbe/Garbe/Fakt -->

### Lemma 9.3: the structure sheaf is indeed a sheaf {#br-bgk-2019-l09-lem-01}

The structure sheaf $\mathcal O_X$ on the spectrum
$X=\operatorname{Spek}(R)$ of a commutative ring $R$ is a sheaf of
commutative rings.

#### Proof {#br-bgk-2019-l09-lem-01-proof}

The definition above is precisely the sheafification of the presheaf in
Example 9.1. The only difference in presentation is that the compatibility
condition is formulated using basic neighbourhoods $D(b)$ instead of
arbitrary open neighbourhoods.

<!-- upstream_entity: Spektrum/Strukturgarbe/Definition -->

### Definition 9.4: affine scheme {#br-bgk-2019-l09-def-02}

The spectrum

$$
X=\operatorname{Spek}(R)
$$

of a commutative ring $R$, together with its structure sheaf
$\mathcal O_X$, is called the *affine scheme* associated with $R$.

An element

$$
q\in\Gamma(U,\mathcal O_X)
$$

is called an algebraic function defined on $U$. The terms *rational
function* and *regular function* are also used in this context.

## Sections as local functions {#br-bgk-2019-l09-s02}

<!-- upstream_entity: Integritätsbereich/Spektrum/Strukturgarbe direkt/Bemerkung -->

### Remark 9.5: the case of an integral domain {#br-bgk-2019-l09-rem-01}

If $R$ is an integral domain, its structure sheaf has a particularly
simple description. For an open set $U\subseteq X$,

$$
\Gamma(U,\mathcal O_X)
=\bigcap_{\mathfrak p\in U}R_{\mathfrak p},
$$

where the intersection is taken in the field of fractions $Q(R)$, in
which all the localisations $R_{\mathfrak p}$ are subrings. Thus the
functions on $U$ are precisely the rational elements of $Q(R)$ defined
at every point of $U$. By Lemma 12.4 in the Commutative Algebra course,

$$
\Gamma(X,\mathcal O_X)
=\bigcap_{\mathfrak p\in X}R_{\mathfrak p}
=R.
$$

Similarly,

$$
\Gamma(D(f),\mathcal O_X)
=\bigcap_{\mathfrak p\in D(f)}R_{\mathfrak p}
=R_f.
$$

If there is an open cover

$$
U=\bigcup_{i\in I}D(f_i),
$$

then

$$
\Gamma(U,\mathcal O_X)
=\bigcap_{\mathfrak p\in U}R_{\mathfrak p}
=\bigcap_{i\in I}\left(
\bigcap_{\mathfrak p\in D(f_i)}R_{\mathfrak p}
\right)
=\bigcap_{i\in I}R_{f_i}.
$$

> **Edition note — the empty open set.** The intersection description in
> this remark assumes $U\ne\varnothing$. For $U=\varnothing$, the sheaf
> assigns the zero ring, whereas the set-theoretic intersection of the
> empty family of subrings of $Q(R)$ would be $Q(R)$. The source does not
> state this exception.

> **Edition note — cross-reference numbers in different witnesses.** The
> frozen semantic witness refers to Lemma 12.4 in Commutative Algebra,
> whereas the older terminal PDF prints Lemma 16.4. The edition follows
> the authoritative semantic revision and records the difference without
> conflating the witnesses.

<!-- upstream_entity: Achsenkreuz/Punktiert/Globale Funktion/Beispiel -->

### Example 9.6: a function on two punctured lines {#br-bgk-2019-l09-exa-02}

Consider

$$
R=K[X,Y]/(XY)
$$

over a field $K$. On the open set

$$
U=D(X,Y)=D(X)\cup D(Y)
=\operatorname{Spec}(R)\setminus\{(X,Y)\},
$$

the function that takes the value $0$ on the punctured line

$$
V(X)\cap U=D(Y)
$$

and the value $1$ on the punctured line

$$
V(Y)\cap U=D(X)
$$

is an algebraic function. This assignment specifies an element
$s_{\mathfrak p}\in R_{\mathfrak p}$ for every prime ideal
$\mathfrak p\in U$. If

$$
\mathfrak p\in V(X)\cap U=D(Y),
$$

its fractional representation is

$$
0=\frac{0}{Y};
$$

whereas if

$$
\mathfrak p\in V(Y)\cap U=D(X),
$$

its representation is

$$
1=\frac{X}{X}.
$$

The source changes from the operator $\operatorname{Spek}$ to
$\operatorname{Spec}$ in this display; both forms are retained as source
notation for the spectrum of a ring.

<!-- upstream_entity: Integritätsbereich/Affines Schema/Rationale Funktion/Nennerideal/Bemerkung -->

### Remark 9.7: denominator ideal {#br-bgk-2019-l09-rem-02}

Let $R$ be an integral domain with field of fractions $Q(R)$, and let
$q\in Q(R)$ be a rational function. There is a largest open set
$U\subseteq\operatorname{Spek}(R)$ on which $q$ is defined. It is

$$
U=D(\mathfrak a),
$$

where the *denominator ideal* is

$$
\mathfrak a=\{r\in R\mid rq\in R\}.
$$

If $q\in R_{\mathfrak p}$, then

$$
q=\frac{s}{r}
$$

with $r\notin\mathfrak p$. Since $r$ belongs to the denominator ideal,
we obtain $\mathfrak p\in D(\mathfrak a)$. Reading this argument backwards
gives the converse implication. In particular, $D(f)$ is the largest
domain of definition of $1/f$.

<!-- upstream_entity: Spektrum/Faktorieller Bereich/Prägarbe/Strukturgarbe/Fakt -->

### Theorem 9.8: unique factorisation domains {#br-bgk-2019-l09-thm-01}

Let $R$ be a unique factorisation domain. Then, for open sets
$U\subseteq\operatorname{Spek}(R)$, the assignment

$$
U\longmapsto\operatorname*{colim}_{U\subseteq D(f)}R_f
$$

agrees with the structure sheaf on $\operatorname{Spek}(R)$.

#### Proof {#br-bgk-2019-l09-thm-01-proof}

This assignment is a presheaf of commutative rings whose sheafification
is the structure sheaf. It therefore suffices to prove that, in the
unique factorisation case, the presheaf is already a sheaf.

Take a nonzero element

$$
q\in\Gamma(U,\mathcal O_X)\subseteq Q(R).
$$

Since $R$ is a unique factorisation domain, there is a reduced
representation

$$
q=\frac{a}{f}.
$$

We claim that $U\subseteq D(f)$. Take $\mathfrak p\in U$. Since $q$ is
defined on $U$, Remark 9.5 gives a representation

$$
q=\frac{b}{g}=\frac{a}{f}
$$

with $g\notin\mathfrak p$. Thus

$$
fb=ag
$$

in $R$. Every prime factor of $f$ divides $ag$ but not $a$, so it must
divide $g$. Hence the radical of $(f)$ contains the radical of $(g)$, and

$$
\mathfrak p\in D(g)\subseteq D(f).
$$

Thus the section $q$ already comes from $R_f$ on a principal open set
containing $U$, as required.

This applies in particular to polynomial rings, and hence to affine
space.

<!-- upstream_entity: Standardquadrik/Globale Funktion/Beispiel -->

### Example 9.9: a section that appears only after sheafification {#br-bgk-2019-l09-exa-03}

Consider the integral domain

$$
R=K[X,Y,Z,W]/(WX-ZY)
$$

over a field $K$, and set

$$
U:=D(X,Y)\subseteq\operatorname{Spek}(R).
$$

By Remark 9.5,

$$
q=\frac{Z}{X}=\frac{W}{Y}
$$

is an algebraic function defined on $U$, so
$q\in\Gamma(U,\mathcal O_X)$. However, apart from units, there is no
element $f\in R$ with

$$
(X,Y)\subseteq(f),
$$

since $X$ and $Y$ are irreducible. Consequently, $q$ is not a section
over $U$ of the presheaf in Example 9.1, but it is a section of its
sheafification.

> **Edition note — symbol for the open set in the source.** The source
> introduces $D(X,Y)$ as an open set, then uses the symbol $U$ without
> defining the equality. The edition writes $U:=D(X,Y)$ explicitly;
> no new mathematical object is added.

## Local properties and principal open sets {#br-bgk-2019-l09-s03}

<!-- upstream_entity: Affines Schema/Punkt/Halm/Lokalisierung/Fakt -->

### Lemma 9.10: stalks are localisations {#br-bgk-2019-l09-lem-02}

Let $(X,\mathcal O_X)$ be the affine scheme associated with a commutative
ring $R$, and let $x\in X$ be the point corresponding to a prime ideal
$\mathfrak p$. Then the stalk of the structure sheaf is

$$
\mathcal O_x=R_{\mathfrak p}.
$$

#### Proof {#br-bgk-2019-l09-lem-02-proof}

This follows from Example 9.1 and Lemma 5.2(2).

<!-- upstream_entity: Affines Schema/Lokal beringt/Fakt -->

### Corollary 9.11: affine schemes are locally ringed {#br-bgk-2019-l09-cor-01}

Every affine scheme is a locally ringed space.

#### Proof {#br-bgk-2019-l09-cor-01-proof}

This follows immediately from Lemma 9.10 and Theorem 12.3 in the
Commutative Algebra course.

> **Edition note — cross-reference numbers in different witnesses.** The
> semantic witness refers to Theorem 12.3 in Commutative Algebra, whereas
> the older terminal PDF prints Theorem 16.3. As in Remark 9.5, the
> edition follows the semantic authority.

<!-- upstream_entity: Affines Schema/Hauptmenge/Nenneraufnahme/Fakt -->

### Lemma 9.12: sections on principal open sets {#br-bgk-2019-l09-lem-03}

Let $(X,\mathcal O_X)$ be the affine scheme associated with a commutative
ring $R$, and let $f\in R$. Then

$$
\Gamma(D(f),\mathcal O_X)=R_f.
$$

In particular,

$$
\Gamma(X,\mathcal O_X)=R.
$$

#### Proof {#br-bgk-2019-l09-lem-03-proof}

We first prove the special case of $X$. There is a natural ring
homomorphism

$$
R\longrightarrow\Gamma(X,\mathcal O_X).
$$

It is injective because whether an element is zero can be checked
locally; compare Appendix Lemma 1.1. To prove surjectivity, take
$q\in\Gamma(X,\mathcal O_X)$. There are an open cover

$$
X=\bigcup_{i\in I}U_i=\bigcup_{i\in I}D(f_i)
$$

and elements

$$
q_i=\frac{a_i}{f_i^{k_i}}
$$

which agree as sections on

$$
D(f_i)\cap D(f_j)=D(f_if_j),
$$

that is, as elements of $R_{f_if_j}$. By Corollary 8.6, we may assume
that $I$ is finite. We may also replace all $k_i$ by their maximum $k$;
of course, this changes the local numerators $a_i$ as well.

The compatibility

$$
\frac{a_i}{f_i^k}=\frac{a_j}{f_j^k}
$$

means that there are equations

$$
(f_if_j)^m a_i f_j^k=(f_if_j)^m a_j f_i^k
$$

in $R$, where $m$ is chosen as a maximum valid for all pairs. By
Proposition 8.4(2),(4), the elements $f_i$, $i\in I$, generate the unit
ideal. The same holds for the $f_i^{m+k}$, so there are $g_i\in R$ with

$$
1=\sum_{i\in I}g_if_i^{m+k}.
$$

Set

$$
a:=\sum_{i\in I}g_ia_if_i^m.
$$

Then

$$
\begin{aligned}
af_j^{m+k}
&=\left(\sum_{i\in I}g_ia_if_i^m\right)f_j^{m+k}\\
&=\sum_{i\in I}g_i(f_if_j)^m a_i f_j^k\\
&=\sum_{i\in I}g_i(f_if_j)^m a_j f_i^k\\
&=a_jf_j^m\left(\sum_{i\in I}g_if_i^{m+k}\right)\\
&=a_jf_j^m.
\end{aligned}
$$

Consequently,

$$
a=\frac{a_j}{f_j^k}=q_j
$$

in $R_{f_j}$. Thus the section is represented by a single ring element
$a\in R$.

The situation on $D(f)$ is the same case with $R_f$ taken as the new
ring. Hence $\Gamma(D(f),\mathcal O_X)=R_f$.

<!-- upstream_entity: Affines Schema/Hauptmenge/Affin/Fakt -->

### Lemma 9.13: principal open sets are affine schemes {#br-bgk-2019-l09-lem-04}

Let $(X,\mathcal O_X)$ be the affine scheme associated with a commutative
ring $R$, and let $f\in R$. Then, via the canonical map on spectra,

$$
D(f)=\operatorname{Spec}(R_f)
$$

as ringed spaces.

#### Proof {#br-bgk-2019-l09-lem-04-proof}

By Proposition 8.11(3), the canonical ring homomorphism

$$
R\longrightarrow R_f
$$

induces an open embedding

$$
\operatorname{Spek}(R_f)\longrightarrow
D(f)\subseteq\operatorname{Spek}(R).
$$

By Lemma 9.12, the ring of sections on both sides is $R_f$. The same
holds for every open set $D(g)\subseteq D(f)$. Thus the structure
sheaves on both sides are identified, giving an isomorphism of ringed
spaces.

> **Edition note — equality via canonical identification.** The source
> statement writes $D(f)=\operatorname{Spec}(R_f)$, while its proof
> constructs an open embedding and an isomorphism of ringed spaces. The
> edition retains the source display and explicitly states that the
> equality uses the canonical identification. The alternation between
> `Spek`/`Spec` is also retained.
