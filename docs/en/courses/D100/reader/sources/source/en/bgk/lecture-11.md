---
title: "Lecture 11 - Irreducible Spaces and Noetherian Schemes"
stable_id: br-bgk-2019-l11
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 11"
upstream_pageid: 109015
upstream_revid: 1019976
upstream_timestamp: "2025-08-09T13:36:06Z"
upstream_mediawiki_sha1: dc9c24551d94791f407b85a6f32d01b16db66218
source_url: "https://de.wikiversity.org/w/index.php?oldid=1019976"
authority_manifest: authority/wikiversity-bgk/unit-11/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: c55c715d0a1bd3ef5b13ac96ccf38f9b5c261e87124c6da5ccc5984cb61deb09
lecture_xml: authority/wikiversity-bgk/unit-11/lecture-11.xml
lecture_xml_sha256: e9b4b62c76baa6de50115714db97c773a298cb9ec831d535b971c0f1836a67f5
lecture_expanded_tex: authority/wikiversity-bgk/unit-11/lecture-11-expanded.tex
lecture_expanded_tex_sha256: 96a022fe9c9c7f174e51fb55668f179713d052eb0c37c6e24fbd39550e6c27e7
official_pdf: authority/artifacts/bgk-lecture-11-official.pdf
official_pdf_sha256: 011e4366b05a93c260db17ab966ab28464afd5cbb9e8df8158dcf25eaa4b40ff
media_credits: source/id-ID/media-credits-bgk-unit-11.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 11: Irreducible Spaces and Noetherian Schemes {#br-bgk-2019-l11}

Compared with a metric space, a scheme has rather unusual topological properties, which we shall introduce here. We begin with irreducibility.

## Irreducible spaces {#br-bgk-2019-l11-s01}

<!-- upstream_entity: Topologie/Irreduzibler Raum/Definition -->

### Definition 11.1: irreducible space {#br-bgk-2019-l11-def-01}

A topological space $V$ is called *irreducible* if $V\ne\varnothing$ and there is no decomposition

$$
V=Y\cup Z
$$

with both $Y,Z\subsetneq V$ closed.

<!-- upstream_entity: Topologie/Irreduzibler Raum/Charakterisierung/Fakt -->

### Lemma 11.2: characterisation by intersections of open sets {#br-bgk-2019-l11-lem-01}

A nonempty topological space $X$ is irreducible if and only if, for any two nonempty open subsets $U,V\subseteq X$, the intersection $U\cap V$ is also nonempty.

#### Proof {#br-bgk-2019-l11-lem-01-proof}

This follows immediately from the definition. For the closed subsets $Y=X\setminus U$ and $Z=X\setminus V$, the equality $X=Y\cup Z$ holds precisely when $U\cap V=\varnothing$.

A subset $Y\subseteq X$ of a topological space $X$ is called irreducible if $Y$, equipped with the induced topology, is an irreducible topological space.

<!-- upstream_entity: Affines Schema/Irreduzible Teilmenge/Primideal/Fakt -->

### Lemma 11.3: irreducible closed subsets of the spectrum {#br-bgk-2019-l11-lem-02}

Let $R$ be a commutative ring and $\mathfrak a\subseteq R$ an ideal. The closed subset

$$
V(\mathfrak a)\subseteq\operatorname{Spek}(R)
$$

is irreducible if and only if the radical of $\mathfrak a$ is a prime ideal.

#### Proof {#br-bgk-2019-l11-lem-02-proof}

We may assume at once that $\mathfrak a$ is a radical ideal. Moreover, $\mathfrak a$ is not the unit ideal. If $V(\mathfrak a)$ is not irreducible, there is a nontrivial decomposition

$$
V(\mathfrak a)=Y\cup Z=V(\mathfrak b)\cup V(\mathfrak c),
$$

where we may assume that $\mathfrak b$ and $\mathfrak c$ are radical. This means that

$$
\mathfrak a=\mathfrak b\cap\mathfrak c.
$$

Since $V(\mathfrak b),V(\mathfrak c)\subsetneq V(\mathfrak a)$, Proposition 8.4(5) gives

$$
\mathfrak a\subsetneq\mathfrak b,
\qquad
\mathfrak a\subsetneq\mathfrak c.
$$

Thus there are $f\in\mathfrak b\setminus\mathfrak a$ and $g\in\mathfrak c\setminus\mathfrak a$. However,

$$
fg\in\mathfrak b\cap\mathfrak c=\mathfrak a,
$$

so $\mathfrak a$ is not a prime ideal.

Conversely, if $\mathfrak a$ is not a prime ideal, there are $f,g\notin\mathfrak a$ with $fg\in\mathfrak a$. Then

$$
D(fg)\subseteq D(\mathfrak a),
\qquad
D(fg)\cap V(\mathfrak a)=\varnothing.
$$

Since $\mathfrak a$ is radical, $f^n\notin\mathfrak a$ for every $n\in\mathbb N$. By Exercise 8.5, there is a prime ideal $\mathfrak p$ with

$$
f\notin\mathfrak p,
\qquad
\mathfrak a\subseteq\mathfrak p.
$$

Hence $D(f)\cap V(\mathfrak a)\ne\varnothing$, and the same holds for $D(g)$. Since

$$
D(f)\cap D(g)\cap V(\mathfrak a)
=D(fg)\cap V(\mathfrak a)=\varnothing,
$$

Lemma 11.2 shows that $V(\mathfrak a)$ is not irreducible.

Thus the correspondence

$$
\mathfrak p\longleftrightarrow V(\mathfrak p)
$$

relates prime ideals to irreducible closed subsets of the spectrum. Maximal ideals correspond to individual closed points, whereas minimal prime ideals correspond to the irreducible components of the spectrum discussed below.

<!-- upstream_entity: Topologischer Raum/Irreduzible Teilmenge/Generischer Punkt/Definition -->

### Definition 11.4: generic point {#br-bgk-2019-l11-def-02}

Let $X$ be a topological space and $Y\subseteq X$ an irreducible closed subset. A point $\eta\in Y$ is called a *generic point* of $Y$ if, for every open subset $U\subseteq X$,

$$
U\cap Y\ne\varnothing
\quad\Longleftrightarrow\quad
\eta\in U.
$$

<!-- upstream_entity: Schema/Irreduzible Teilmenge/Generischer Punkt/Fakt -->

### Lemma 11.5: existence and uniqueness of the generic point {#br-bgk-2019-l11-lem-03}

In a scheme $X$, every irreducible closed subset $Y\subseteq X$ has exactly one generic point.

#### Proof {#br-bgk-2019-l11-lem-03-proof}

By assumption, $Y$ is nonempty. Choose $P\in Y$ and an open affine neighbourhood

$$
P\in W=\operatorname{Spek}(R).
$$

Then $Y\cap W$ is an irreducible closed subset of the affine scheme $W$. By Lemma 11.3,

$$
Y\cap W=V(\mathfrak p)
$$

for some prime ideal $\mathfrak p\in W$. We claim that $\mathfrak p$ is the generic point of $Y$. If $U\subseteq X$ is open and $Y\cap U\ne\varnothing$, the irreducibility of $Y$ gives

$$
Y\cap U\cap W\ne\varnothing,
$$

and hence $\mathfrak p\in U$. The generic point is unique because it is uniquely determined as a point of the affine scheme $W$.

## Krull dimension {#br-bgk-2019-l11-s02}

<!-- upstream_entity: Topologischer Raum/Krulldimension/Definition -->

### Definition 11.6: Krull dimension of a topological space {#br-bgk-2019-l11-def-03}

For a topological space $X$, the maximum length of a chain of irreducible closed subsets

$$
X_0\subsetneq X_1\subsetneq\cdots\subsetneq X_{n-1}\subsetneq X_n
$$

in $X$ is called the *Krull dimension* of the space.

> **Editorial note - unbounded dimension.** The source says “maximum”. More generally, take the supremum of the lengths $n$ of these chains, allowing infinite dimension when the lengths are unbounded.

<!-- upstream_entity: Affines Schema/Krulldimension/Fakt -->

### Lemma 11.7: dimension of a ring and its spectrum {#br-bgk-2019-l11-lem-04}

The Krull dimension of a commutative ring $R$ equals the Krull dimension of its spectrum $\operatorname{Spek}(R)$.

#### Proof {#br-bgk-2019-l11-lem-04-proof}

The assertion follows from Lemma 11.3 and Proposition 8.4(5).

## Noetherian spaces {#br-bgk-2019-l11-s03}

<!-- upstream_entity: Topologischer Raum/Noethersch/Offene Mengen/Definition -->

### Definition 11.8: noetherian topological space {#br-bgk-2019-l11-def-04}

A topological space $X$ is called *noetherian* if every ascending chain of open subsets

$$
U_1\subseteq U_2\subseteq U_3\subseteq\cdots
$$

becomes stationary, that is, there is an $n$ such that

$$
U_n=U_{n+1}=U_{n+2}=\cdots.
$$

<!-- upstream_entity: Topologischer Raum/Noethersch/Quasikompakt/Fakt -->

### Lemma 11.9: characterisation by quasicompactness {#br-bgk-2019-l11-lem-05}

A topological space $X$ is noetherian if and only if every open subset of it is quasicompact.

#### Proof {#br-bgk-2019-l11-lem-05-proof}

Every open subset of a noetherian space is itself noetherian. For the forward implication, it therefore suffices to prove that $X$ is quasicompact. Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover, and suppose that it has no finite subcover. We can then construct an infinite strictly ascending chain of open subsets

$$
V_n=\bigcup_{i\in I_n}U_i,
$$

where each $I_n\subseteq I$ is finite, contradicting noetherianity.

Conversely, suppose that every open subset is quasicompact, and consider an ascending chain $U_k\subseteq U_{k+1}$. The set

$$
U=\bigcup_{k\in\mathbb N}U_k
$$

is open and quasicompact, so this cover has a finite subcover. Thus there is an index $n$ with $U_n=U_k$ for all $k\ge n$.

In a noetherian space, every nonempty collection of open sets (respectively, closed sets) has a maximal (respectively, minimal) element. This gives the proof principle of *noetherian induction*. To prove that a property $E$ holds for all closed subsets, suppose there are closed subsets that fail to satisfy $E$, and choose a minimal one. This subset must then lead to a contradiction. The principle is valid because an infinite descending chain can be constructed in any nonempty collection without a minimal element.

The proof of the following assertion gives a typical example of this proof principle.

<!-- upstream_entity: Topologischer Raum/Noethersch/Zerlegung in irreduzible Komponenten/Fakt -->

### Theorem 11.10: irreducible components {#br-bgk-2019-l11-thm-01}

Every noetherian topological space $X$ has a unique irredundant decomposition

$$
X=V_1\cup\cdots\cup V_k
$$

into irreducible closed subsets; *irredundant* means that no $V_i$ is contained in $V_j$ for $i\ne j$.

#### Proof {#br-bgk-2019-l11-thm-01-proof}

We prove existence by noetherian induction on the closed subsets of $X$. Suppose that not every closed subset has such a decomposition. Then there is a minimal subset, say $V\subseteq X$, without one. The set $V$ cannot be irreducible, so there is a nontrivial decomposition

$$
V=V_1\cup V_2.
$$

Since $V_1$ and $V_2$ are proper subsets of $V$, each has a finite expression as a union of irreducible closed subsets. Combining these two expressions gives a finite decomposition of $V$, a contradiction.

For uniqueness, let

$$
X=V_1\cup\cdots\cup V_k=W_1\cup\cdots\cup W_m
$$

be two decompositions into irreducible subsets, each without inclusion relations. Then

$$
\begin{aligned}
V_1
&=V_1\cap X\\
&=V_1\cap(W_1\cup\cdots\cup W_m)\\
&=(V_1\cap W_1)\cup\cdots\cup(V_1\cap W_m).
\end{aligned}
$$

Since $V_1$ is irreducible, there is a $j$ with $V_1\subseteq W_j$. By the same argument, there is an $i$ with $W_j\subseteq V_i$. Irredundancy forces $i=1$ and $V_1=W_j$. Each of the other $V_i$ occurs in the right-hand decomposition in the same way, so the decomposition is unique.

> **Editorial note - irredundancy condition.** The source statement says only “unique decomposition”, while its proof first requires “each without inclusion relations” when comparing two decompositions. This edition brings that necessary condition into the statement; the source components and argument are unchanged.

The subsets occurring in this decomposition are called the *irreducible components* of the space.

<!-- upstream_entity: Schema/Noethersch/Definition -->

### Definition 11.11: noetherian scheme {#br-bgk-2019-l11-def-05}

A scheme $X$ is called *noetherian* if it can be covered by finitely many affine schemes associated with noetherian rings.

In particular, the spectrum of a noetherian ring is a noetherian scheme.

<!-- upstream_entity: Noethersches Schema/Noetherscher Raum/Fakt -->

### Lemma 11.12: topology of a noetherian scheme {#br-bgk-2019-l11-lem-06}

A noetherian scheme is a noetherian topological space.

#### Proof {#br-bgk-2019-l11-lem-06-proof}

A finite union of noetherian spaces is again noetherian, so it suffices to consider the spectrum of a noetherian ring. By Lemma 11.9, we must show that every open subset

$$
U=D(\mathfrak a)\subseteq\operatorname{Spek}(R)
$$

is quasicompact. Since $R$ is noetherian,

$$
\mathfrak a=(f_1,\ldots,f_n),
$$

and Proposition 8.4(2) gives

$$
D(\mathfrak a)=D(f_1)\cup\cdots\cup D(f_n).
$$

Corollary 8.6 together with Proposition 8.11 says that each $D(f_i)$ is quasicompact, so their finite union is quasicompact as well.

These topological methods immediately give the following purely algebraic result.

<!-- upstream_entity: Noetherscher Ring/Minimale Primideale/Endlich/Fakt -->

### Lemma 11.13: finiteness of the minimal prime ideals {#br-bgk-2019-l11-lem-07}

A noetherian commutative ring has only finitely many minimal prime ideals.

#### Proof {#br-bgk-2019-l11-lem-07-proof}

See Exercise 11.15.

## Integral schemes {#br-bgk-2019-l11-s04}

<!-- upstream_entity: Beringter Raum/Reduziert/Offene Mengen/Definition -->

### Definition 11.14: reduced ringed space {#br-bgk-2019-l11-def-06}

A ringed space $(X,\mathcal O_X)$ is called *reduced* if, for every open subset $U\subseteq X$, the ring $\Gamma(U,\mathcal O_X)$ is reduced.

<!-- upstream_entity: Schema/Integer/Irreduzibel und reduziert/Definition -->

### Definition 11.15: integral scheme {#br-bgk-2019-l11-def-07}

A scheme $X$ is called *integral* if it is irreducible and reduced.

<!-- upstream_entity: Integres Schema/Injektive Restriktionen/Fakt -->

### Lemma 11.16: restrictions on an integral scheme are injective {#br-bgk-2019-l11-lem-08}

In an integral scheme, the restriction maps

$$
\Gamma(U,\mathcal O_X)\longrightarrow\Gamma(V,\mathcal O_X)
$$

are injective for all open $\varnothing\ne V\subseteq U\subseteq X$.

#### Proof {#br-bgk-2019-l11-lem-08-proof}

Let $0\ne f\in\Gamma(U,\mathcal O_X)$. The set

$$
U_f=\{P\in U\mid f(P)\ne0\}
$$

is open by Lemma 7.16 and is nonempty by reducedness. Since $X$ is irreducible, $U_f\cap V$ is nonempty as well. Thus the restriction of $f$ to $V$ is nonzero.

> **Editorial note - domain of the section.** The source calls the set above $X_f$ and writes $P\in X$, although $f$ is given only as a section on $U$. This edition writes $U_f$ and $P\in U$; the nonvanishing locus and the injectivity argument are unchanged.

<!-- upstream_entity: Irreduzibel/Restriktionsabbildung nicht injektiv/Beispiel -->

### Example 11.17: irreducibility alone is not enough {#br-bgk-2019-l11-exa-01}

Let $K$ be a field and

$$
R=K[X,Y]/(X^2,XY).
$$

The ideal $\mathfrak q=(X)$ is the only minimal prime ideal of $R$, so $\operatorname{Spek}(R)$ is irreducible. Since $Y\notin\mathfrak q$ and $XY=0$, the equality $X=0$ holds in the localisation $R_{\mathfrak q}$, and

$$
R_{\mathfrak q}=K[Y]_{(0)}=K(Y)
$$

is a field. The restriction map $R\to R_{\mathfrak q}$ is not injective. Moreover,

$$
D(X)=\varnothing,
$$

but the element $X$ is nonzero in the localisation $R_{(X,Y)}$.

<!-- upstream_entity: Integres Schema/Integritätsbereich/Fakt -->

### Lemma 11.18: rings of sections are integral domains {#br-bgk-2019-l11-lem-09}

In an integral scheme $X$, for every nonempty open subset $U\subseteq X$, the ring of sections $\Gamma(U,\mathcal O_X)$ is an integral domain.

#### Proof {#br-bgk-2019-l11-lem-09-proof}

Since $U$ is open and nonempty, there is a nonempty affine open subset

$$
V=\operatorname{Spek}(R)\subseteq U.
$$

By Lemma 11.16, it suffices to show that $R$ is an integral domain. Let $\mathfrak a$ be the nilradical of $R$. Since $V$ is irreducible as a consequence of the irreducibility of $X$, Lemma 11.3 says that $\mathfrak a$ is a prime ideal. Reducedness is a local property by Exercise 11.18, so $\mathfrak a=0$. Thus the zero ideal is prime, and $R$ is an integral domain.

> **Editorial note - source exercise number.** The source refers to Exercise 10.14, but frozen Worksheet 10 contains only six exercises. Frozen Exercise 11.18 states precisely the equivalence between reducedness of a ringed space and reducedness of all its stalks. This edition corrects the cross-reference to 11.18 and preserves the source's erroneous reference in this note.

<!-- upstream_entity: Integres Schema/Generischer Halm/Körper/Fakt -->

### Lemma 11.19: the generic stalk is a field {#br-bgk-2019-l11-lem-10}

For an integral scheme, the stalk of the structure sheaf at the generic point is a field.

#### Proof {#br-bgk-2019-l11-lem-10-proof}

The stalk can be computed from any nonempty affine open subset. Such a subset has the form

$$
U=\operatorname{Spek}(R),
$$

where $R$ is a commutative ring that is an integral domain by Lemma 11.18. The generic point corresponds to the zero ideal, and localisation at the zero ideal gives the fraction field of $R$.

<!-- upstream_entity: Integres Schema/Funktionenkörper/Definition -->

### Definition 11.20: function field {#br-bgk-2019-l11-def-08}

For an integral scheme $X$, the stalk of the structure sheaf at the generic point is called the *function field* of $X$.

In an integral scheme, the ring of sections on every nonempty open subset is a subring of the function field.
