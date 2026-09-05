---
title: "Lecture 8 - The Spectrum of a Commutative Ring"
stable_id: br-bgk-2019-l08
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 8"
upstream_pageid: 109012
upstream_revid: 793632
upstream_timestamp: "2022-08-25T06:26:28Z"
upstream_mediawiki_sha1: dedf36ef3494817e0d35ddb9ff305a5adedd92d7
source_url: "https://de.wikiversity.org/w/index.php?oldid=793632"
authority_manifest: authority/wikiversity-bgk/unit-08/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: cadebf48e67a54a238f4b22e0abf806fbf1f81821b6d012993739ecf50dd8d32
lecture_xml: authority/wikiversity-bgk/unit-08/lecture-08.xml
lecture_xml_sha256: fc38c16bb3a748d8db389bb0984152c9e8f1313c7f4d1a73ea799778669470bd
lecture_expanded_tex: authority/wikiversity-bgk/unit-08/lecture-08-expanded.tex
lecture_expanded_tex_sha256: 926cd9ff6e41b384d89b2b63e9c1f7dab7d37dca34a864bd1fd045b6a565db11
official_pdf: authority/artifacts/bgk-lecture-08-official.pdf
official_pdf_sha256: 4907b8a1438d786d326667256e9b4c3f8124f4b170d53c782a5f58f68cc09727
media_credits: source/id-ID/media-credits-bgk-unit-08.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs and source media retain their respective component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 8: The Spectrum of a Commutative Ring {#br-bgk-2019-l08}

So far we have considered ringed spaces whose underlying space was, in a
certain sense, given first: an arbitrary topological space, a real
manifold, or a complex manifold. From these spaces arose natural sheaves
of commutative rings, namely the sheaves of continuous, differentiable, or
holomorphic functions. Their individual elements were familiar as
functions, but the rings themselves were generally very large and
difficult to grasp as a whole.

Conversely, we may ask to what extent every commutative ring can be
obtained as the ring of global sections of a ringed space, or whether
there is a ringed space that reflects the properties of the ring
particularly well and helps us understand it. We shall answer these
questions positively in this lecture and the next. The resulting ringed
spaces are also the local building blocks of algebraic geometry.

## The spectrum of a commutative ring {#br-bgk-2019-l08-s01}

<!-- upstream_entity: Kommutativer Ring/Spektrum/Definition -->

### Definition 8.1: spectrum {#br-bgk-2019-l08-def-01}

For a commutative ring $R$, the set of all prime ideals of $R$ is called
the *spectrum* of $R$ and is denoted by

$$
\operatorname{Spek}(R).
$$

It is also called an *affine scheme*.

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Definition -->

### Definition 8.2: Zariski topology {#br-bgk-2019-l08-def-02}

On the spectrum of a commutative ring $R$, the *Zariski topology* is
defined by declaring the sets

$$
D(T):=\{\mathfrak p\in\operatorname{Spek}(R)\mid
T\not\subseteq\mathfrak p\}
$$

to be open for every subset $T\subseteq R$.

For a one-element subset $T=\{f\}$, we write $D(f)$ instead of
$D(\{f\})$.

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Ist Topologie/Fakt -->

### Lemma 8.3: the Zariski topology is indeed a topology {#br-bgk-2019-l08-lem-01}

The Zariski topology on the spectrum $\operatorname{Spek}(R)$ of a
commutative ring $R$ is indeed a topology.

#### Proof {#br-bgk-2019-l08-lem-01-proof}

We have

$$
D(0)=\varnothing,
\qquad
D(1)=\operatorname{Spek}(R),
$$

since every prime ideal contains $0$ and no prime ideal contains $1$.

For an arbitrary family of subsets $T_i\subseteq R$, $i\in I$, we have

$$
\bigcup_{i\in I}D(T_i)
=D\!\left(\bigcup_{i\in I}T_i\right).
$$

The inclusion from left to right is clear, since
$T_i\subseteq\bigcup_{i\in I}T_i$ and $S\subseteq T$ always implies
$D(S)\subseteq D(T)$. For the reverse inclusion, take

$$
\mathfrak p\in D\!\left(\bigcup_{i\in I}T_i\right).
$$

There is $f\in\bigcup_{i\in I}T_i$ with $f\notin\mathfrak p$. Thus there
is $i\in I$ with $f\in T_i$, and consequently $\mathfrak p\in D(T_i)$.

For a finite family $T_1,\ldots,T_n\subseteq R$, we have

$$
\bigcap_{i=1}^{n}D(T_i)=D(T_1\cdots T_n),
$$

where $T_1\cdots T_n$ is the set of all products $f_1\cdots f_n$ with
$f_i\in T_i$. The inclusion from right to left is clear. For the reverse
inclusion, suppose $\mathfrak p\in D(T_i)$ for every $i=1,\ldots,n$.
Then there are $f_i\in T_i$ with $f_i\notin\mathfrak p$. Since
$\mathfrak p$ is prime, $f_1\cdots f_n\notin\mathfrak p$, so
$\mathfrak p\in D(T_1\cdots T_n)$.

We always regard the spectrum as a topological space. The prime ideals
are the points of this space. To emphasise the geometric viewpoint, we
often write

$$
X=\operatorname{Spek}(R),\qquad x\in X,
$$

and denote the prime ideal represented by $x$ by $\mathfrak p_x$.

The complements of the open sets, that is, the closed sets in the Zariski
topology, are denoted by

$$
V(T)=\{\mathfrak p\in\operatorname{Spek}(R)\mid T\subseteq\mathfrak p\}.
$$

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Erste Eigenschaften/Fakt -->

### Proposition 8.4: first properties of the Zariski topology {#br-bgk-2019-l08-prop-01}

For the spectrum $X=\operatorname{Spek}(R)$ of a commutative ring $R$, the
following properties hold.

1. $D(T)=D(\mathfrak a)$, where $\mathfrak a$ is the ideal generated by
   $T$ (or its radical). Thus, to describe the open sets, it suffices to
   consider the radical ideals of $R$.
2. For a family of ideals $\mathfrak a_i\subseteq R$, $i\in I$,

   $$
   \bigcup_{i\in I}D(\mathfrak a_i)
   =D\!\left(\sum_{i\in I}\mathfrak a_i\right).
   $$

3. For a finite family of ideals $\mathfrak a_i\subseteq R$,
   $i=1,\ldots,n$,

   $$
   \bigcap_{i=1}^{n}D(\mathfrak a_i)
   =D\!\left(\bigcap_{i=1}^{n}\mathfrak a_i\right)
   =D(\mathfrak a_1\cdots\mathfrak a_n).
   $$

4. $D(\mathfrak a)=X$ if and only if $\mathfrak a$ is the unit ideal.
5. $D(\mathfrak a)\subseteq D(\mathfrak b)$ if and only if
   $\mathfrak a\subseteq\operatorname{rad}(\mathfrak b)$.
6. The spectrum is empty if and only if $R$ is the zero ring.
7. $D(\mathfrak a)=\varnothing$ if and only if $\mathfrak a$ contains only
   nilpotent elements.
8. The open sets $D(f)$, $f\in R$, form a basis for the topology.
9. A family of open sets $D(\mathfrak a_i)$, $i\in I$, covers $X$ if and
   only if the ideals $\mathfrak a_i$ together generate the unit ideal.

#### Proof {#br-bgk-2019-l08-prop-01-proof}

(1) The inclusion $D(T)\subseteq D(\mathfrak a)$ is clear. For the reverse
inclusion, argue by contraposition and suppose $\mathfrak p\notin D(T)$.
Then $T\subseteq\mathfrak p$, and hence

$$
\mathfrak a\subseteq\operatorname{rad}(\mathfrak a)
\subseteq\mathfrak p,
$$

since a prime ideal is radical. Thus
$\mathfrak p\notin D(\operatorname{rad}(\mathfrak a))$.

(2) and (3) follow from (1) and the proof of Lemma 8.3.

(4) If $\mathfrak a$ is not the unit ideal, then by Exercise 8.1 there is
a maximal ideal $\mathfrak m$ with $\mathfrak a\subseteq\mathfrak m$.
Consequently, $\mathfrak m\notin D(\mathfrak a)$.

(5) The implication from right to left is clear. For the converse, suppose

$$
\mathfrak a\not\subseteq\operatorname{rad}(\mathfrak b).
$$

Then there is $f\in\mathfrak a$ with $f^n\notin\mathfrak b$ for every
$n\in\mathbb N$. Applying Exercise 8.5 to the multiplicative system
$\{f^n\mid n\in\mathbb N\}$ gives a prime ideal
$\mathfrak p\supseteq\mathfrak b$ with $f\notin\mathfrak p$. Thus
$\mathfrak p\in D(\mathfrak a)$ but $\mathfrak p\notin D(\mathfrak b)$.

> **Edition note — missing source reference number.** The source TeX
> witness displays `*****` at this reference. The frozen HTML links instead
> to an exercise titled “the radical is the intersection of prime ideals”,
> whose course reference-number page is missing. Worksheet Exercise 8.5
> proves exactly the existence statement required here when applied to
> $M=\{f^n\mid n\in\mathbb N\}$; the internal reference above is therefore
> an explicit editorial application, not a recovered source number.

(6) The zero ring has no prime ideals. Every nonzero commutative ring has
a maximal ideal by Exercise 8.1.

(7) Every prime ideal contains all nilpotent elements, so
$V(\mathfrak a)=X$ for such an ideal. Conversely, if $\mathfrak a$
contains a nonnilpotent element $f$, then by Exercise 8.5 there is a prime
ideal $\mathfrak p$ with $f\notin\mathfrak p$. Hence
$\mathfrak p\in D(f)\subseteq D(\mathfrak a)$.

(8) This follows directly from

$$
D(\mathfrak a)=\bigcup_{f\in\mathfrak a}D(f).
$$

(9) follows from (2) and (4).

> **Edition note — duplicated word in the source.** The last sentence of
> the source proof reads the equivalent of “follows from and (2) and (4)”.
> The duplicated conjunction is normalised; the mathematical references
> remain (2) and (4).

<!-- upstream_entity: Kommutativer Ring/Spektrum/Abschluss/Fakt -->

### Proposition 8.5: closure in the spectrum {#br-bgk-2019-l08-prop-02}

For the spectrum $X=\operatorname{Spek}(R)$ of a commutative ring $R$:

1. the closure of a subset $T\subseteq X$ is

   $$
   V\!\left(\bigcap_{x\in T}\mathfrak p_x\right);
   $$

2. the closure of a point $x\in X$ is $V(\mathfrak p_x)$;
3. a point $x\in\operatorname{Spek}(R)$ is closed if and only if
   $\mathfrak p_x$ is a maximal ideal.

#### Proof {#br-bgk-2019-l08-prop-02-proof}

(1) For $y\in T$, we have

$$
y\in V(\mathfrak p_y)
\subseteq V\!\left(\bigcap_{x\in T}\mathfrak p_x\right),
$$

so the set on the right is a closed set containing $T$. Take a prime
ideal $\mathfrak q$ with

$$
\mathfrak q\in V\!\left(\bigcap_{x\in T}\mathfrak p_x\right),
\qquad
\bigcap_{x\in T}\mathfrak p_x\subseteq\mathfrak q.
$$

To show that $\mathfrak q$ belongs to the closure of $T$, it suffices to
show that $T$ meets every open neighbourhood of $\mathfrak q$. Suppose
$\mathfrak q\in D(f)$, that is, $f\notin\mathfrak q$. Then
$f\notin\bigcap_{x\in T}\mathfrak p_x$, so there is $x\in T$ with
$f\notin\mathfrak p_x$. Thus $\mathfrak p_x\in D(f)$ and
$T\cap D(f)\ne\varnothing$.

(2) is a special case of (1), and (3) follows from (2).

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Quasikompaktheit/Fakt -->

### Corollary 8.6: spectra are quasi-compact {#br-bgk-2019-l08-cor-01}

The spectrum $X=\operatorname{Spek}(R)$ of every commutative ring $R$ is
quasi-compact.

#### Proof {#br-bgk-2019-l08-cor-01-proof}

By Proposition 8.4(9),

$$
X=\bigcup_{i\in I}D(\mathfrak a_i)
$$

if and only if the ideals $\mathfrak a_i$, $i\in I$, together generate
the unit ideal. The ideal generated by this family consists of all finite
sums $f_1+\cdots+f_n$ with $f_j\in\mathfrak a_{i_j}$. Thus, if the unit
ideal is generated, there are a finite selection
$\{i_1,\ldots,i_n\}\subseteq I$ and elements
$f_j\in\mathfrak a_{i_j}$ with

$$
\sum_{j=1}^{n}f_j=1.
$$

Consequently,

$$
X=D(1)=\bigcup_{j=1}^{n}D(f_j)
=\bigcup_{j=1}^{n}D(\mathfrak a_{i_j}),
$$

giving a finite subcover.

A spectrum is Hausdorff only in special circumstances. In general, two
points of a spectrum cannot be separated by open neighbourhoods.

<!-- upstream_entity: Körper/Spektrum/Beispiel -->

### Example 8.7: the spectrum of a field {#br-bgk-2019-l08-exa-01}

A field has only two ideals: the unit ideal $K$, which is not prime, and
the zero ideal $0$, which is prime. Thus the spectrum of a field consists
of a single point.

<!-- upstream_entity: Z/Spektrum/Beispiel -->

### Example 8.8: the spectrum of the integers {#br-bgk-2019-l08-exa-02}

The prime ideals of $\mathbb Z$ are the maximal ideals $(p)$, where $p$
is a prime number, together with the zero ideal $0$. The maximal ideals
form the closed points of $\operatorname{Spek}(\mathbb Z)$. The zero ideal
is an additional, nonclosed point. The only closed set containing this
point is the whole space. Apart from the whole space, the closed sets of
$\operatorname{Spek}(\mathbb Z)$ are the finite subsets of maximal ideals.

We picture $\operatorname{Spek}(\mathbb Z)$ as an imagined line: the prime
numbers lie discretely along it, while the zero ideal is drawn as a thick
point representing the whole line.

> **Source illustration unavailable.** The source declares
> `File:Spektrum_von_Z._xcf`, but the official Commons API returns it as
> *missing*, the source HTML displays broken media, and the official PDF
> contains no image binary. The complete source caption reads: “This is how
> one imagines the spectrum of $\mathbb Z$. The connecting lines are meant
> to convey that it is a one-dimensional object. The zero ideal is drawn in
> bold to indicate that it is a dense point.” The edition preserves this
> caption and its accessible descriptive meaning without claiming to have
> recovered the image.
> The source names Bocardodarapti as the creator and gives the licence
> label CC-by-sa 4.0; these declarations are retained independently of the
> unavailable image binary.

<!-- upstream_entity: Polynomring über Körper/Spektrum/Beispiel -->

### Example 8.9: the spectrum of a polynomial ring {#br-bgk-2019-l08-exa-03}

For the polynomial ring

$$
R=K[X_1,\ldots,X_n]
$$

over a field $K$, the so-called point ideals give a useful geometric
picture of $\operatorname{Spek}(R)$. A point ideal has the form

$$
(X_1-a_1,X_2-a_2,\ldots,X_n-a_n)
$$

for a fixed tuple $a=(a_1,a_2,\ldots,a_n)\in K^n$. This ideal is the
kernel of the $K$-algebra homomorphism

$$
\begin{aligned}
\varphi_a:R&\longrightarrow K,\\
X_i&\longmapsto a_i,
\end{aligned}
$$

and is therefore maximal. This assignment defines an injective map

$$
K^n\longrightarrow\operatorname{Spek}(R).
$$

If $K$ is algebraically closed, this map even accounts for all maximal
ideals of $R$. We therefore picture the spectrum of the polynomial ring
in $n$ variables as affine space, but it also contains additional,
nonclosed points that are harder to visualise. For a polynomial
$f\in K[X_1,\ldots,X_n]$, the set $V(f)\cap K^n$ has a concrete
interpretation:

$$
a\in V(f)\cap K^n
\quad\Longleftrightarrow\quad
f(a_1,\ldots,a_n)=0.
$$

## Functorial properties {#br-bgk-2019-l08-s02}

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Funktorialität/Fakt -->

### Proposition 8.10: functoriality of the spectrum {#br-bgk-2019-l08-prop-03}

Let

$$
\varphi:R\longrightarrow S
$$

be a ring homomorphism between commutative rings. Then:

1. the assignment

   $$
   \begin{aligned}
   \varphi^*:\operatorname{Spek}(S)&\longrightarrow\operatorname{Spek}(R),\\
   \mathfrak p&\longmapsto\varphi^*(\mathfrak p)
   :=\varphi^{-1}(\mathfrak p)
   \end{aligned}
   $$

   is well-defined and continuous;
2. for every ideal $\mathfrak a\subseteq R$,

   $$
   (\varphi^*)^{-1}(D(\mathfrak a))=D(\mathfrak a S);
   $$

3. for another ring homomorphism $\psi:S\to T$,

   $$
   (\psi\circ\varphi)^*=\varphi^*\circ\psi^*.
   $$

#### Proof {#br-bgk-2019-l08-prop-03-proof}

By Exercise 8.9, the map is well-defined. To prove continuity, it suffices
to prove (2). We argue using closed sets. For a prime ideal
$\mathfrak q\in\operatorname{Spek}(S)$, we have

$$
\varphi^*(\mathfrak q)\in V(\mathfrak a)
$$

if and only if $\mathfrak a\subseteq\varphi^{-1}(\mathfrak q)$. This is
equivalent to $\varphi(\mathfrak a)\subseteq\mathfrak q$, and also to
$\mathfrak aS\subseteq\mathfrak q$. Statement (3) is immediate.

The continuous map introduced above is called the *map on spectra*
associated with the given ring homomorphism. For a subring $R\subseteq S$,
it is simply

$$
\mathfrak p\longmapsto\mathfrak p\cap R,
$$

also called *contraction* of a prime ideal.

<!-- upstream_entity: Kommutativer Ring/Spektrum/Zariski-Topologie/Abgeschlossene und offene Teilmengen/Fakt -->

### Proposition 8.11: closed and open subsets {#br-bgk-2019-l08-prop-04}

Let $R$ be a commutative ring. Then:

1. for an ideal $\mathfrak a\subseteq R$ and the quotient map

   $$
   q:R\longrightarrow R/\mathfrak a,
   $$

   the map on spectra

   $$
   q^*:\operatorname{Spek}(R/\mathfrak a)
   \longrightarrow\operatorname{Spek}(R)
   $$

   is a closed embedding with image $V(\mathfrak a)$;
2. for a multiplicative system $M\subseteq R$, the map associated with
   the canonical map

   $$
   \iota:R\longrightarrow R_M
   $$

   is an injective map

   $$
   \iota^*:\operatorname{Spek}(R_M)
   \longrightarrow\operatorname{Spek}(R),
   $$

   whose image consists of the prime ideals of $R$ disjoint from $M$;
3. for $f\in R$, the map associated with

   $$
   \iota:R\longrightarrow R_f
   $$

   is an open embedding

   $$
   \iota^*:\operatorname{Spek}(R_f)
   \longrightarrow\operatorname{Spek}(R)
   $$

   with image $D(f)$.

#### Proof {#br-bgk-2019-l08-prop-04-proof}

(1) follows from Exercise 8.6. The prime ideals of $R/\mathfrak a$
correspond to the prime ideals of $R$ containing $\mathfrak a$ via

$$
\mathfrak p\longmapsto q^{-1}(\mathfrak p).
$$

Thus the map is bijective onto the stated image. For an ideal
$\mathfrak b\subseteq R/\mathfrak a$ and a prime ideal
$\mathfrak p\subseteq R/\mathfrak a$, we have
$\mathfrak b\subseteq\mathfrak p$ if and only if, under the quotient
correspondence,

$$
q^{-1}(\mathfrak b)\subseteq q^{-1}(\mathfrak p)
$$

in $R$. Thus the image of $V(\mathfrak b)$ is
$V(q^{-1}(\mathfrak b))$, which is closed.

> **Edition note — quotient correspondence notation.** The source writes
> $q^{-1}(\mathfrak p)=\mathfrak p+\mathfrak a$ and likewise uses
> $\mathfrak b+\mathfrak a$, although $\mathfrak p$ and $\mathfrak b$ here
> are ideals of $R/\mathfrak a$, while $\mathfrak a$ is an ideal of $R$.
> The inverse-image notation above states the same correspondence without
> adding ideals that belong to different rings.

(2) See Exercise 8.7.

(3) For a prime ideal $\mathfrak p$ and an element $f\in R$,
$f\notin\mathfrak p$ holds if and only if $\mathfrak p$ is disjoint from
the multiplicative system

$$
\{f^n\mid n\in\mathbb N\}.
$$

By (2), the map is injective with image $D(f)$. The same argument,
applied to $g\in R$ and $g/1\in R_f$, shows that the image of

$$
D(g)\subseteq\operatorname{Spek}(R_f)
$$

is $D(fg)$, and is therefore open.

<!-- upstream_entity: Kommutativer Ring/Spektrumsabbildung/Faser/Fakt -->

### Lemma 8.12: fibres of the map on spectra {#br-bgk-2019-l08-lem-02}

Let $\varphi:R\to S$ be a ring homomorphism between commutative rings,
and let

$$
\begin{aligned}
\varphi^*:\operatorname{Spek}(S)&\longrightarrow\operatorname{Spek}(R),\\
\mathfrak p&\longmapsto\varphi^*(\mathfrak p)
\end{aligned}
$$

be the associated map on spectra. Its fibre over a prime ideal
$\mathfrak q\in\operatorname{Spek}(R)$ is

$$
\operatorname{Spek}\!\left(
(S/\mathfrak qS)_{\varphi(R\setminus\mathfrak q)}
\right).
$$

In other words, this fibre consists of all prime ideals
$\mathfrak p\in\operatorname{Spek}(S)$ satisfying

$$
\mathfrak qS\subseteq\mathfrak p,
\qquad
\mathfrak p\cap\varphi(R\setminus\mathfrak q)=\varnothing.
$$

#### Proof {#br-bgk-2019-l08-lem-02-proof}

By Proposition 8.11, it suffices to prove the second formulation. For a
prime ideal $\mathfrak p\subseteq S$, we have

$$
\varphi^{-1}(\mathfrak p)=\mathfrak q
$$

if and only if both

$$
\varphi(\mathfrak q)\subseteq\mathfrak p
\quad\text{and}\quad
\varphi(R\setminus\mathfrak q)\subseteq S\setminus\mathfrak p.
$$

The first condition is equivalent to $\mathfrak qS\subseteq\mathfrak p$,
and the second is equivalent to

$$
\varphi(R\setminus\mathfrak q)\cap\mathfrak p=\varnothing.
$$

In particular, the fibre of a map on spectra over a point is itself the
spectrum of a ring. If $\mathfrak m$ is maximal, its fibre is

$$
\operatorname{Spek}(S/\mathfrak mS),
$$

since $\mathfrak mS\subseteq\mathfrak p$ immediately gives
$\mathfrak m\subseteq\varphi^{-1}(\mathfrak p)$, and maximality forces
equality. If $R$ is an integral domain and the point is the zero ideal,
there is no need to consider the extension ideal; the fibre is simply
described by

$$
\operatorname{Spek}\!\left(S_{\varphi(R\setminus\{0\})}\right).
$$

<!-- upstream_entity: Kommutativer Ring/Spektrumsabbildung/Faser ist leer/Fakt -->

### Corollary 8.13: criterion for an empty fibre {#br-bgk-2019-l08-cor-02}

Let $\varphi:R\to S$ be a ring homomorphism between commutative rings,
and let $\varphi^*:\operatorname{Spek}(S)\to\operatorname{Spek}(R)$ be
the associated map on spectra. The fibre over a prime ideal
$\mathfrak q\in\operatorname{Spek}(R)$ is empty if and only if

$$
\mathfrak qS\cap\varphi(R\setminus\mathfrak q)\ne\varnothing.
$$

#### Proof {#br-bgk-2019-l08-cor-02-proof}

This follows from Lemma 8.12 and Proposition 8.4(6).
