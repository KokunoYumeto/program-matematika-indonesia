---
title: "Lecture 15 - Affine and Quasi-affine Varieties, Local Rings, and Stalks"
stable_id: br-ak-2025-2026-l15
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 15"
upstream_pageid: 165904
upstream_revid: 1051357
upstream_timestamp: "2025-08-18T08:08:44Z"
upstream_mediawiki_sha1: 72949885b4a089a2f30ea68019ce98ea55d1939d
source_url: "https://de.wikiversity.org/w/index.php?oldid=1051357"
authority_manifest: authority/wikiversity/unit-15/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 86e394725e766838f01eb035ca53044c4d3b85ff20eb99f8fecda9c2a0156425
lecture_xml_sha256: 303749263b928e32c699cae0f7ebbccd419ec3455ec79eee6afb137a8a0887ca
lecture_expanded_tex_sha256: f369a5fb5de001525bb9fd50bf62df84c33fd02a3bc329dfc55874bb8a89d4e2
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-15.csv"
translation_status: complete
---

# Lecture 15: Affine and Quasi-affine Varieties, Local Rings, and Stalks {#br-ak-2025-2026-l15}

## Affine and quasi-affine varieties {#br-ak-2025-2026-l15-s01}

<!-- upstream_entity: Affine Varietät/Algebraisch abgeschlossener Körper/K-Punkte/Definition -->

### Definition: affine varieties {#br-ak-2025-2026-l15-def-01}

Let $K$ be an algebraically closed field and let $R$ be a $K$-algebra of
finite type. The $K$-spectrum

$$
V=K\!-\!\operatorname{Spek}(R),
$$

with every Zariski-open set $U\subseteq V$ equipped with the ring of
algebraic functions $\Gamma(U,\mathcal O)$, is called an *affine variety*.

An open subset of an affine variety, again with every open set equipped
with its structure ring, is called a *quasi-affine variety*. A quasi-affine
variety is covered by finitely many open sets of the form $D(f)$, each of
which is itself an affine variety. Some authors reserve the term variety
for irreducible $K$-spectra.

When $R$ is reduced, Theorem 14.9 ensures that no information is lost in

$$
V=K\!-\!\operatorname{Spek}(R),
$$

since the ring $R$ can be recovered as $\Gamma(V,\mathcal O)$. For arbitrary
$R$, the pointwise algebraic functions instead recover the reduction
$R_{\mathrm{red}}$; nilpotents are invisible on $K$-points. This is not possible
from the topological space alone.

> **Edition note.** The source states the recovery claim without reducedness.
> The qualification above records the hypothesis needed for the pointwise
> definition used here.

## Local rings {#br-ak-2025-2026-l15-s02}

For a given point $P$ in a $K$-spectrum, we are interested in all algebraic
functions defined at $P$ and admitting a rational representation on some
neighbourhood of $P$. These functions are defined on different
neighbourhoods, and in general there is no smallest neighbourhood on which all
algebraic functions defined at $P$ are simultaneously defined. We have a
system of rings

$$
\bigl(\Gamma(U,\mathcal O)\bigr)_{P\in U}
$$

that we want to understand geometrically and algebraically. It turns out
that this system has a meaningful limit—called a *direct limit* or
*colimit*—and that it agrees with the localisation $R_{\mathfrak m}$ at
the maximal ideal $\mathfrak m$ corresponding to $P$. We begin with the
algebraic terminology.

> **Edition note.** The source says unconditionally that there is no smallest
> neighbourhood. The qualification “in general” allows for isolated points,
> for which $\{P\}$ is a smallest neighbourhood of $P$.

<!-- upstream_entity: Kommutative Ringtheorie/Lokaler Ring/Definition -->

### Definition: local rings {#br-ak-2025-2026-l15-def-02}

A commutative ring $R$ is called *local* if it has exactly one maximal
ideal.

For a nonzero commutative ring, equivalently, the complement of the group of
units of $R$ is closed under addition. The simplest local rings are fields.
Every local ring $R$ with maximal ideal $\mathfrak m$ has a quotient
$R/\mathfrak m$ that is a field, called its *residue field*. We shall soon see that every
point of a $K$-spectrum has an associated local ring describing the
“local appearance” of the variety at that point algebraically.

> **Edition note.** The source omits the nonzero-ring qualification in the
> additive characterisation. For the zero ring the nonunit set is empty and
> hence additively closed, although there is no maximal ideal.

<!-- upstream_entity: Kommutative Ringtheorie/Lokalisierung für Primideal/Definition -->

### Definition: localisation at a prime ideal {#br-ak-2025-2026-l15-def-03}

Let $R$ be a commutative ring and let $\mathfrak p$ be a prime ideal. The
localisation at the multiplicative system

$$
S=R\setminus\mathfrak p
$$

is called the *localisation* of $R$ at $\mathfrak p$ and is denoted by
$R_{\mathfrak p}$. Thus

$$
R_{\mathfrak p}
=\left\{\frac fg\mathrel{\Big|}f\in R,\ g\notin\mathfrak p\right\}.
$$

The following theorem explains this terminology.

<!-- upstream_entity: Kommutative Ringtheorie/Lokalisierung/Lokaler Ring/Fakt -->

### Theorem: localisation at a prime ideal is local {#br-ak-2025-2026-l15-thm-01}

Let $R$ be a commutative ring and let $\mathfrak p$ be a prime ideal in
$R$. Then $R_{\mathfrak p}$ is a local ring with maximal ideal

$$
\mathfrak pR_{\mathfrak p}
=\left\{\frac fg\mathrel{\Big|}f\in\mathfrak p,\ g\notin\mathfrak p\right\}.
$$

#### Proof {#br-ak-2025-2026-l15-thm-01-proof}

The displayed set is indeed an ideal in

$$
R_{\mathfrak p}
=\left\{\frac fg\mathrel{\Big|}f\in R,\ g\notin\mathfrak p\right\}.
$$

We show that the complement of $\mathfrak pR_{\mathfrak p}$ consists only
of units, so this ideal must be maximal. Let

$$
q=\frac fg\in R_{\mathfrak p}
$$

but suppose $q\notin\mathfrak pR_{\mathfrak p}$. Then
$f,g\notin\mathfrak p$, so the reciprocal fraction $g/f$ also belongs to
the localisation.

## Fraction fields and function fields {#br-ak-2025-2026-l15-s03}

If $R$ is an integral domain, its fraction field is the localisation at
the zero prime ideal. We now show that for the associated irreducible
affine variety $K\!-\!\operatorname{Spek}(R)$, every algebraic function
naturally belongs to the fraction field.

<!-- upstream_entity: K-Spektrum/Integritätsbereich/Algebraische Funktion ist Element im Quotientenkörper/Fakt -->

### Lemma: algebraic functions as elements of the fraction field {#br-ak-2025-2026-l15-lem-01}

Let $K$ be an algebraically closed field, let $R$ be a $K$-algebra of
finite type that is an integral domain, and let

$$
\varnothing\ne U\subseteq K\!-\!\operatorname{Spek}(R)
$$

be an open subset. There is a uniquely determined injective $R$-algebra
homomorphism

$$
\Gamma(U,\mathcal O)\longrightarrow Q(R).
$$

In particular, every algebraic function defined on a nonempty open set $U$
is an element of the fraction field $Q(R)$.

#### Proof {#br-ak-2025-2026-l15-lem-01-proof}

Take $P\in U$ and suppose that the algebraic function $f$ is given on a
neighbourhood of $P$ by

$$
f=G/H,
\qquad G,H\in R,
\qquad H\ne0.
$$

The fraction $G/H$ can immediately be regarded as an element of the
fraction field. Let $Q\in U$ be another point with a representation

$$
f=G'/H'.
$$

By Lemma 14.8, since $R$ is an integral domain,

$$
GH'=G'H
$$

in $R$. Thus the element of the fraction field is well defined. The
resulting map is clearly a ring homomorphism and makes the diagram

$$
\begin{matrix}
R &&\\
\downarrow & \searrow &\\
\Gamma(U,\mathcal O)&\longrightarrow&Q(R)
\end{matrix}
$$

commute. These properties also determine the map uniquely: algebraic
functions arising from elements of $R$ must map to those same elements in
the fraction field, so the image of every fraction is determined.

For injectivity, if $G/H=0$ in the fraction field, then $G=0$, and the
corresponding function is zero on $D(H)$. For another representation
$G'/H'$ of the same function, the relation above again gives $G'=0$;
the function is therefore zero on all of $U$.

Uniqueness also immediately shows that for two open sets $U\subseteq U'$
the diagram

$$
\begin{matrix}
\Gamma(U',\mathcal O)&&\\
\downarrow&\searrow&\\
\Gamma(U,\mathcal O)&\longrightarrow&Q(R)
\end{matrix}
$$

commutes, with the restriction homomorphism on the left. From now on, in
the integral-domain case we identify an algebraic function with its
corresponding element of the fraction field.

## Topological filters and their stalks {#br-ak-2025-2026-l15-s04}

The result of the preceding section says that the fraction field can be
obtained as an ordered union of all rings of sections
$\Gamma(U,\mathcal O)$ as $U$ ranges over the nonempty open sets. A similar
construction can be made for suitably structured systems of open sets in
general. For this we need the concept of a filter.

<!-- upstream_entity: Topologie/Topologischer Filter/Definition -->

### Definition: topological filters {#br-ak-2025-2026-l15-def-04}

Let $X$ be a topological space. A system $F$ of open subsets of $X$ is
called a *topological filter* if, for open sets $U,V$, the following hold:

1. $X\in F$;
2. if $U\in F$ and $U\subseteq V$, then $V\in F$;
3. if $U,V\in F$, then $U\cap V\in F$.

![Four concentric grey circles on a transparent background](authority/assets/Concentric_Circles.svg)

*Schematic depiction of a neighbourhood filter; Andreas Pietzowski,
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0). Source
details are given in the Unit 15 media credits.*

<!-- upstream_entity: Topologische Filter/Umgebungsfilter/Definition -->

### Definition: neighbourhood filters {#br-ak-2025-2026-l15-def-05}

Let $X$ be a topological space and let $M\subseteq X$. The system

$$
\mathcal U(M)
=\{U\subseteq X\mid U\text{ is open and }M\subseteq U\}
$$

is called the *neighbourhood filter* of $M$.

This is clearly a topological filter. In particular, a point $P\in X$ has
a neighbourhood filter $\mathcal U(P)$ consisting of all its open
neighbourhoods.

Suppose that two open neighbourhoods $U_1,U_2$ of $P$ and two algebraic
functions

$$
f_1\in\Gamma(U_1,\mathcal O),
\qquad
f_2\in\Gamma(U_2,\mathcal O)
$$

are given. Initially their sum $f_1+f_2$—and likewise their product—makes
no sense because their domains differ. In the integral-domain case we can
regard both as elements of the fraction field and add them there.
Alternatively, we can pass to the intersection $U_1\cap U_2$, which is
also an open neighbourhood of $P$, and add the restrictions of the two
functions there. The important property of a filter is that together with
any two of its open sets it contains their intersection, with the
inclusions

$$
U_1\cap U_2\subseteq U_1,U_2
$$

and the corresponding restriction maps

$$
\Gamma(U_1,\mathcal O),\Gamma(U_2,\mathcal O)
\longrightarrow\Gamma(U_1\cap U_2,\mathcal O).
$$

This observation is made precise by the concepts of a directed set and a
directed system.

<!-- upstream_entity: Ordnungstheorie/Gerichtete Menge/Definition -->

### Definition: directed sets {#br-ak-2025-2026-l15-def-06}

A nonempty ordered set $(I,\preccurlyeq)$ is called *directedly ordered*, or
simply *directed*, if for every $i,j\in I$ there is a $k\in I$ such that

$$
i,j\preccurlyeq k.
$$

> **Edition note.** The source does not require $I$ to be nonempty. The
> standard convention is used here; it is also needed below for a colimit of
> groups to carry a group structure.

We regard a topological filter as a set ordered by inclusion. Its
intersection property makes it directed; the direction of the order is

$$
\preccurlyeq\;=\;\supseteq.
$$

<!-- upstream_entity: Geordnetes und gerichtetes System/Von Mengen/Definition -->

### Definition: ordered and directed systems {#br-ak-2025-2026-l15-def-07}

Let $(I,\preccurlyeq)$ be an ordered index set. A family of sets

$$
M_i,\qquad i\in I,
$$

is called an *ordered system of sets* if:

1. $\varphi_{ii}=\operatorname{id}_{M_i}$ for every $i\in I$;
2. for $i\preccurlyeq j$ there is a map $\varphi_{ij}:M_i\to M_j$;
3. for $i\preccurlyeq j\preccurlyeq k$ we have

   $$
   \varphi_{ik}=\varphi_{jk}\circ\varphi_{ij}.
   $$

> **Edition note.** The identity-map axiom is part of the usual definition
> and is added explicitly; the source states only the transition maps and
> their composition law.

If the index set is also directed, the family is called a *directed
system of sets*.

If all the $M_i$ are groups (or rings) and all maps between them are group
homomorphisms (or ring homomorphisms), we speak of an ordered or directed
system of groups (or rings).

<!-- upstream_entity: Geordnetes System/Von Mengen/Kolimes/Definition -->

### Definition: colimits {#br-ak-2025-2026-l15-def-08}

Let $(M_i)_{i\in I}$ be a directed system of sets. The set

$$
\operatorname{colim}_{i\in I}M_i
=\left(\biguplus_{i\in I}M_i\right)\!\big/\!\sim
$$

is called the *colimit* (also the *direct limit* or *inductive limit*) of
the system. Here $\sim$ is the equivalence relation declaring two elements
$m\in M_i$ and $n\in M_j$ equivalent if there is a $k\in I$ with
$i,j\preccurlyeq k$ and

$$
\varphi_{ik}(m)=\varphi_{jk}(n).
$$

In particular, $s_i\in M_i$ is equivalent to its image
$\varphi_{ik}(s_i)\in M_k$ for every $i\preccurlyeq k$.

**Edition note:** in the last sentence the source writes $s_i\in M$,
although the system defines only the sets $M_i$. This edition supplies
the required index, $s_i\in M_i$.

For a directed system of groups (or rings), the colimit of sets above can
also be given a group (or ring) structure. Two elements of the colimit
represented by $s_i\in M_i$ and $s_j\in M_j$ can be replaced by their
images in some $M_k$ with $i,j\preccurlyeq k$, and the operation is then
defined in $M_k$; see Exercise 15.23.

Our principal example is the directed system of rings

$$
\Gamma(U,\mathcal O),\qquad U\in F,
$$

directed by a topological filter. Its colimit has a name of its own.

<!-- upstream_entity: Quasiaffine Varietät/Topologischer Filter/Halm der Strukturgarbe/Definition -->

### Definition: the stalk at a filter {#br-ak-2025-2026-l15-def-09}

Let $(V,\mathcal O)$ be a quasi-affine variety and let $F$ be a topological
filter in $V$. The colimit

$$
\mathcal O_F
=\operatorname{colim}_{U\in F}\Gamma(U,\mathcal O)
$$

is called the *stalk* of $\mathcal O$ at $F$.

The stalk at the neighbourhood filter of a point $P$ is also called the
stalk at $P$ and is denoted by $\mathcal O_P$.

<!-- upstream_entity: K-Spektrum/Algebraisch abgeschlossen/Punkt/Halm ist Lokalisierung/Fakt -->

### Theorem: the stalk at a point is a localisation {#br-ak-2025-2026-l15-thm-02}

Let $R$ be a reduced commutative algebra of finite type over an
algebraically closed field $K$. Let

$$
P\in K\!-\!\operatorname{Spek}(R)
$$

be a point with corresponding maximal ideal $\mathfrak m\subseteq R$.
There is a natural isomorphism of $R$-algebras

$$
R_{\mathfrak m}\longrightarrow\mathcal O_P.
$$

#### Proof {#br-ak-2025-2026-l15-thm-02-proof}

The stalk $\mathcal O_P$ has a unique $R$-algebra structure because the
whole space belongs to the filter. If $F\in R$ and $F\notin\mathfrak m$,
then $1/F$ is defined on the open neighbourhood $D(F)$ of $P$. There we
have $F\cdot(1/F)=1$, so $F$ becomes a unit in the colimit. By the
universal property of localisation, there is an $R$-algebra homomorphism

$$
R_{\mathfrak m}\longrightarrow\mathcal O_P.
$$

We prove that this map is bijective. First take $f\in\mathcal O_P$. This
element is represented by an algebraic function

$$
f\in\Gamma(U,\mathcal O),
\qquad P\in U.
$$

In particular, $f$ has a rational representation at $P$: on $D(H)$ we have

$$
f=G/H,
\qquad P\in D(H).
$$

The last condition means $H(P)\ne0$, or equivalently
$H\notin\mathfrak m$. Thus $G/H\in R_{\mathfrak m}$ and maps to $f$.
This proves surjectivity.

For injectivity, take $G/H$ with $H\notin\mathfrak m$ and suppose its
image in the stalk is zero. This means that $G/H$ is the zero function on
some open neighbourhood $U$ of $P$. We may choose

$$
P\in D(H')\subseteq U\cap D(H)
$$

and, by Corollary 14.10, write on that set, explicitly taking $G'=0$,

$$
G/H=G'/H'=0.
$$

By Lemma 14.8,

$$
H(H')^2G=0
$$

in $R$. Since $H$ and $H'$ become units in $R_{\mathfrak m}$, we obtain
$G/H=0$ in the localisation.

<!-- upstream_entity: K-Spektrum/Integritätsbereich/Durchschnitt von lokalen Ringen/Fakt -->

### Lemma: sections as an intersection of local rings {#br-ak-2025-2026-l15-lem-02}

Let $K$ be an algebraically closed field, let $R$ be a $K$-algebra of
finite type that is an integral domain, and let

$$
U\subseteq K\!-\!\operatorname{Spek}(R)
$$

be a nonempty open set. Then

$$
\Gamma(U,\mathcal O)=\bigcap_{P\in U}\mathcal O_P,
$$

where the intersection is taken inside the fraction field $Q(R)$.

> **Edition note.** The source allows $U=\varnothing$, but then the section
> ring is not represented by an intersection of subrings of $Q(R)$. The
> nonempty hypothesis is therefore necessary for this formulation.

#### Proof {#br-ak-2025-2026-l15-lem-02-proof}

For every $P\in U$ there are injective ring homomorphisms

$$
\Gamma(U,\mathcal O)\longrightarrow\mathcal O_P
\longrightarrow Q(R).
$$

Consequently there is an injective ring homomorphism

$$
\Gamma(U,\mathcal O)
\longrightarrow\bigcap_{P\in U}\mathcal O_P.
$$

Conversely, let $f\in Q(R)$ belong to the intersection on the right. For
every $P\in U$ there is a representation $f=G/H$ with

$$
P\in D(H)\subseteq U.
$$

This says precisely that $f$ is an algebraic function on $U$.

<!-- upstream_entity: Quasiaffine Varietäten/Irreduzibel/Funktionenkörper/Definition -->

### Definition: function fields {#br-ak-2025-2026-l15-def-10}

Let $V$ be an irreducible quasi-affine variety. The stalk $\mathcal O_V$
at the filter of all nonempty open sets in $V$ is a field, called the
*function field* of $V$.

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
