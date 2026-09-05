---
title: "Lecture 25 - Sheaf Cohomology"
stable_id: br-bgk-2019-l25
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 25"
upstream_pageid: 109029
upstream_revid: 1003754
upstream_timestamp: "2025-06-08T16:38:19Z"
upstream_mediawiki_sha1: ca0f902e2615027938e7edf18cf1641135b671c2
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003754"
authority_manifest: authority/wikiversity-bgk/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f454cb2f8ada795015dcf78d4ad56a54107d9773705b7113a1ef1600b341e26d
authority_manifest_status: "Terminal authority freeze complete; all 33 file records have been recomputed without discrepancies."
lecture_xml: authority/wikiversity-bgk/unit-25/lecture-25.xml
lecture_xml_sha256: 43bf0cf4fea0330c8e10880c0e294f7faa2af3518ebeac27b52acd9c286f9ae6
lecture_expanded_tex: authority/wikiversity-bgk/unit-25/lecture-25-expanded.tex
lecture_expanded_tex_sha256: 6b21b42534b078a965f972c0571de6df58ef903764a6bc99c1dcf0b1f77ef215
official_pdf: authority/artifacts/bgk-lecture-25-official.pdf
official_pdf_sha256: f1de2ae26d338559fc894fdc3334bc62a5d1cf858ae5b96f66dc71b3b331c1af
official_pdf_source_bytes: 85771
official_pdf_source_sha1: 5080f80897bce4afc8bea685e72ef8288e9f559c
official_pdf_metadata: authority/wikiversity-bgk/unit-25/official-pdfs-api.json
official_pdf_metadata_sha256: f49c28f3f600974f8cd7bcf29377dbad5429e789769d0953fc28075adce5c767
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revisions govern the text; the official PDFs are retained as historical witnesses without overriding newer revisions."
media_credits: source/id-ID/media-credits-bgk-unit-25.md
media_credits_sha256: c0367344876a648ab7141eb306e6a9a02f14c47b3b57a03012073940f4297037
rights_ledger: authority/RIGHTS-bgk-unit-25.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-25.json
asset_closure_sha256: b897e839fc6999e5c149e1bf065a634b96246b563860d46f0a16ddb82ae1c9d5
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDFs are authority witnesses, not the edition text; the Commons CC BY-SA 4.0 metadata and embedded CC-by-sa 3.0 notices are preserved without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 25: Sheaf Cohomology {#br-bgk-2019-l25}

## Sheaf cohomology {#br-bgk-2019-l25-s01}

<!-- upstream_entity: Topologischer Raum/Garbe/Kohomologie/Definition -->

### Definition 25.1: sheaf cohomology {#br-bgk-2019-l25-def-01}

Let $\mathcal G$ be a sheaf of abelian groups on a topological space $X$.
The $n$th right derived functor of the global sections functor $\Gamma(X,-)$
is called the *$n$th sheaf cohomology* of $\mathcal G$ on $X$.
It is denoted by

$$
H^n(X,\mathcal G):=R^n\Gamma(X,\mathcal G).
$$

<!-- upstream_entity: Topologischer Raum/Garbe/Kohomologie/Grundlegende Eigenschaften/Fakt -->

### Corollary 25.2: basic properties of sheaf cohomology {#br-bgk-2019-l25-cor-01}

Let $X$ be a topological space. Sheaf cohomology has the following properties.

1. For every $n\in\mathbb N$, $H^n(X,-)$ is an additive functor from
   the category of sheaves of abelian groups on $X$ to the category
   of abelian groups.
2. There is a natural isomorphism
   $H^0(X,\mathcal G)\cong\Gamma(X,\mathcal G)$.
3. For a short exact sequence of sheaves

   $$
   0\longrightarrow\mathcal F\longrightarrow\mathcal G
   \longrightarrow\mathcal H\longrightarrow 0,
   $$

   there is a long exact cohomology sequence

   $$
   \begin{aligned}
   0&\longrightarrow\Gamma(X,\mathcal F)
   \longrightarrow\Gamma(X,\mathcal G)
   \longrightarrow\Gamma(X,\mathcal H)
   \longrightarrow H^1(X,\mathcal F)\\
   &\longrightarrow H^1(X,\mathcal G)
   \longrightarrow H^1(X,\mathcal H)
   \longrightarrow H^2(X,\mathcal F)
   \longrightarrow\cdots.
   \end{aligned}
   $$

#### Proof {#br-bgk-2019-l25-cor-01-proof}

This is a special case of Theorem 24.7.

Cohomology groups are generally difficult to compute.
Here are some basic approaches to calculation.

1. *Vanishing theorems:* one proves that the cohomology groups are $0$
   for certain spaces, sheaves, and indices. If a term in a long exact
   cohomology sequence is $0$, the preceding map is surjective and
   the following map is injective.
2. Instead of injective sheaves, one can use other acyclic sheaves,
   for example flasque sheaves.
3. $H^1$ can be interpreted as a group classifying certain geometric
   objects, for example the Picard group.
4. If the sheaves are modules on a ringed space, their cohomology groups
   also have a module structure over the ring of global sections
   $\Gamma(X,\mathcal O_X)$; see Lemma 25.5. If this ring is a field,
   as is the case in particular for connected projective varieties,
   the cohomology groups are even vector spaces. When finite,
   their dimensions are important invariants.
5. Cohomology on $X$ can be compared with cohomology on an open subset.
6. Sheaf cohomology can be compared with other cohomology theories:
   Čech cohomology, singular cohomology, and simplicial cohomology.

> **Edition note — scope of the projective-variety parenthesis.** The
> parenthetical statement uses “variety” in the usual reduced finite-type
> sense. It does not extend unchanged to arbitrary connected projective
> schemes: a connected non-reduced projective scheme can have a ring of
> global sections that is not a field.

<!-- upstream_entity: Topologischer Raum/Welke Garbe/Azyklisch/Fakt -->

### Lemma 25.3: flasque sheaves are acyclic {#br-bgk-2019-l25-lem-01}

A flasque sheaf $\mathcal G$ on a topological space $X$ is acyclic;
that is,

$$
H^n(X,\mathcal G)=0
$$

for $n\geq 1$.

#### Proof {#br-bgk-2019-l25-lem-01-proof}

By Lemma 23.13, there is an embedding of $\mathcal G$ in an injective
sheaf $\mathcal I$. Consider the associated short exact sequence of sheaves,

$$
0\longrightarrow\mathcal G\longrightarrow\mathcal I
\longrightarrow\mathcal I/\mathcal G\longrightarrow 0.
$$

By Lemma 23.16, $\mathcal I$ is flasque. Then by Lemma 23.15 (2),
the quotient sheaf $\mathcal I/\mathcal G$ is also flasque. Using
Theorem 24.8, the long exact cohomology sequence gives, on the one hand,

$$
0\longrightarrow\Gamma(X,\mathcal G)
\longrightarrow\Gamma(X,\mathcal I)
\longrightarrow\Gamma(X,\mathcal I/\mathcal G)
\longrightarrow H^1(X,\mathcal G)\longrightarrow 0,
$$

and, on the other hand,

$$
0\longrightarrow H^n(X,\mathcal I/\mathcal G)
\xrightarrow{\delta^n}H^{n+1}(X,\mathcal G)
\longrightarrow 0
$$

for $n\geq 1$. Since the map

$$
\Gamma(X,\mathcal I)\longrightarrow\Gamma(X,\mathcal I/\mathcal G)
$$

is surjective by Lemma 23.15 (1), the first segment shows that
$H^1(X,\mathcal G)=0$. This holds for every flasque sheaf.
Applying the second segment, which the source says is applied for $n=2$,
we obtain $H^2(X,\mathcal G)=0$, and so on.

> **Editorial note - index in the induction step.** The displayed formula
> relates $H^n(X,\mathcal I/\mathcal G)$ to $H^{n+1}(X,\mathcal G)$,
> so the conclusion about $H^2$ formally uses $n=1$. The printed source
> says $n=2$; this edition preserves the source's explanation and
> explicitly records the discrepancy.

<!-- upstream_entity: Topologischer Raum/Topologische Gruppe/Garbe/Welke Auflösung/Bemerkung -->

### Remark 25.4: first cohomology classes of the sheaf of continuous functions {#br-bgk-2019-l25-rem-01}

Let $G$ be a topological abelian group and $X$ a topological space.
Consider the sheaf of continuous maps to $G$, namely $C^0(-,G)$, with

$$
C^0(U,G)=\{f:U\longrightarrow G\text{ a map}\mid f\text{ continuous}\}.
$$

> **Edition note — group hypothesis.** The German source says only
> “topological group”. The displayed subtraction, quotient sheaf of groups,
> long exact sequence, and ordinary group-valued sheaf cohomology require
> `G` to be abelian. The discussion is read with that necessary hypothesis;
> it is not a claim about non-abelian first cohomology.

There is a natural inclusion of sheaves

$$
C^0(-,G)\subseteq\operatorname{Abb}(-,G),
$$

and therefore a short exact sequence of sheaves

$$
0\longrightarrow C^0(-,G)
\longrightarrow\operatorname{Abb}(-,G)
\longrightarrow\operatorname{Abb}(-,G)/C^0(-,G)
\longrightarrow 0.
$$

The sheaf of maps in the middle is flasque, since every map extends
to a larger set. Thus by Lemma 25.3,

$$
H^1(X,\operatorname{Abb}(-,G))=0,
$$

so the long exact cohomology sequence begins

$$
\begin{aligned}
0&\longrightarrow C^0(X,G)
\longrightarrow\operatorname{Abb}(X,G)
\longrightarrow\Gamma\bigl(X,\operatorname{Abb}(-,G)/C^0(-,G)\bigr)\\
&\longrightarrow H^1(X,C^0(-,G))\longrightarrow 0.
\end{aligned}
$$

Every first cohomology class of $C^0(-,G)$ is therefore represented by
a global element of the quotient sheaf $\operatorname{Abb}(-,G)/C^0(-,G)$.
Two such representatives define the same class precisely when their
difference comes from a map $X\to G$.

As for any quotient sheaf, by Lemma 5.9 (1), a global element is represented
by an open cover

$$
X=\bigcup_{i\in I}U_i
$$

and sections $f_i\in\Gamma(U_i,\operatorname{Abb}(-,G))$, that is,
maps $f_i:U_i\to G$, such that the differences

$$
f_i-f_j\big|_{U_i\cap U_j}
$$

come from the subsheaf, that is, are continuous functions on $U_i\cap U_j$.
By Lemma 5.9 (2), such an element comes from the left, and thus maps to
the trivial cohomology class, precisely when there is a function $f:X\to G$
such that

$$
g_i:=f_i-f\big|_{U_i}
$$

is continuous for every $i$. In that case, on $U_i\cap U_j$ we have

$$
g_i-g_j=f_i-f-(f_j-f)=f_i-f_j.
$$

Conversely, if there is a family of continuous functions $g_i$ on $U_i$
whose differences agree with the prescribed differences, then on $U_i$
we can define

$$
f:=f_i-g_i.
$$

Since these definitions agree on overlaps, they give a global function
on $X$. Thus the first cohomology group of the sheaf of continuous
functions is trivial precisely when for every family $(U_i,f_i)$
with continuous differences $f_i-f_j$, there is a family $(U_i,g_i)$
of continuous functions $g_i$ with the same differences.

<!-- upstream_entity: Beringter Raum/Modul/Garbenkohomologie/Modulstruktur/Fakt -->

### Lemma 25.5: the module structure on sheaf cohomology {#br-bgk-2019-l25-lem-02}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal M$ an
$\mathcal O_X$-module. Then the sheaf cohomology groups $H^i(X,\mathcal M)$
are naturally $\Gamma(X,\mathcal O_X)$-modules.

#### Proof {#br-bgk-2019-l25-lem-02-proof}

Every element $f\in\Gamma(X,\mathcal O_X)$ defines an
$\mathcal O_X$-module homomorphism

$$
f:\mathcal M\longrightarrow\mathcal M.
$$

On each open set $U\subseteq X$, the restriction of $f$ to
$\Gamma(U,\mathcal O_X)$ acts by scalar multiplication, namely

$$
\Gamma(U,\mathcal M)\longrightarrow\Gamma(U,\mathcal M),
\qquad s\longmapsto fs.
$$

Multiplication by $f$ is, in particular, a homomorphism of sheaves of
abelian groups. By functoriality of sheaf cohomology in Corollary 25.2,
it induces a group homomorphism

$$
H^n(f):H^n(X,\mathcal M)\longrightarrow H^n(X,\mathcal M).
$$

We must show that the map

$$
\Gamma(X,\mathcal O_X)\times H^n(X,\mathcal M)
\longrightarrow H^n(X,\mathcal M),
\qquad(f,c)\longmapsto H^n(f)(c),
$$

defines a module structure on $H^n(X,\mathcal M)$.
Since $H^n(f)$ is a group homomorphism, additivity in the module
variable is assured. By functoriality, $1$ maps to the identity,
first as a sheaf homomorphism and then in cohomology.
Compatibility with composition gives

$$
H^n(fg)=H^n(f)\circ H^n(g).
$$

For global ring elements $f,g$, scalar multiplication by $f+g$ at the
level of sheaves of modules is the sum of scalar multiplication by $f$
and by $g$. Since $H^n$ is an additive functor, we also have

$$
H^n(f+g)=H^n(f)+H^n(g).
$$

## Cohomology on schemes {#br-bgk-2019-l25-s02}

We now consider the cohomology of sheaves on schemes.

<!-- upstream_entity: Schema/Integer/Strukturgarbe/Funktionenkörper/Erste Kohomologie/Fakt -->

### Lemma 25.6: first cohomology via the function field {#br-bgk-2019-l25-lem-03}

Let $(X,\mathcal O_X)$ be an integral scheme with function field $K$,
viewed as the constant sheaf $\mathcal K$ on $X$. Then

$$
H^1(X,\mathcal O_X)
=\Gamma(X,\mathcal K/\mathcal O_X)
/\operatorname{im}\bigl(K\longrightarrow
\Gamma(X,\mathcal K/\mathcal O_X)\bigr).
$$

#### Proof {#br-bgk-2019-l25-lem-03-proof}

Since $X$ is in particular irreducible, the constant presheaf with value
$K$ is a sheaf. By Lemma 11.16, there is an injective sheaf homomorphism

$$
\mathcal O_X\longrightarrow\mathcal K,
$$

and hence a short exact sequence of sheaves

$$
0\longrightarrow\mathcal O_X\longrightarrow\mathcal K
\longrightarrow\mathcal K/\mathcal O_X\longrightarrow 0.
$$

The associated long exact cohomology sequence is

$$
\begin{aligned}
0&\longrightarrow\Gamma(X,\mathcal O_X)
\longrightarrow\Gamma(X,\mathcal K)
\longrightarrow\Gamma(X,\mathcal K/\mathcal O_X)\\
&\longrightarrow H^1(X,\mathcal O_X)
\longrightarrow H^1(X,\mathcal K)\longrightarrow\cdots.
\end{aligned}
$$

As a constant sheaf, $\mathcal K$ is flasque and hence acyclic
by Lemma 25.3. In particular,

$$
H^1(X,\mathcal K)=0.
$$

Thus $H^1(X,\mathcal O_X)$ is the cokernel of the preceding map.

<!-- upstream_entity: Affines Schema/Integer/Strukturgarbe/Funktionenkörper/Erste Kohomologie/Fakt -->

### Lemma 25.7: vanishing on integral affine schemes {#br-bgk-2019-l25-lem-04}

Let $R$ be an integral domain and

$$
\operatorname{Spek}(R)=(X,\mathcal O_X)
$$

the associated integral affine scheme. Then

$$
H^1(X,\mathcal O_X)=0.
$$

#### Proof {#br-bgk-2019-l25-lem-04-proof}

Consider the short exact sequence of $R$-modules

$$
0\longrightarrow R\longrightarrow K\longrightarrow K/R\longrightarrow 0
$$

and the associated sequence of quasi-coherent sheaves, exact by Lemma 14.9,

$$
0\longrightarrow\mathcal O_X\longrightarrow\widetilde K
\longrightarrow\widetilde{K/R}\longrightarrow 0.
$$

In particular,

$$
\widetilde{K/R}=\widetilde K/\mathcal O_X,
$$

and $\widetilde K$ is the constant sheaf of the function field.
Evaluating this sheaf sequence globally recovers the original sequence.
The result now follows from Lemma 25.6.

<!-- upstream_entity: Affine punktierte Ebene/Strukturgarbe/Erste Kohomologie/Beispiel -->

### Example 25.8: the punctured affine plane {#br-bgk-2019-l25-exm-01}

Consider the punctured affine plane

$$
U=\mathbb A_K^2\setminus\{(0,0)\}
$$

over a field $K$. We want to understand $H^1(U,\mathcal O_U)$ using
Lemma 25.7. Its function field is $K(X,Y)$; denote the associated
constant sheaf by $\mathcal Q$. The long exact cohomology sequence begins

$$
0\longrightarrow K[X,Y]\longrightarrow K(X,Y)
\longrightarrow\Gamma(U,\mathcal Q/\mathcal O_U)
\longrightarrow H^1(X,\mathcal O_U)\longrightarrow 0.
$$

> **Editorial note - space symbol in the source.** The printed source writes
> $H^1(X,\mathcal O_U)$ in the sequence above, although the example,
> evaluation, and other terms concern $U$. This edition preserves the
> source symbol and does not silently replace it.

We have $U=D(X)\cup D(Y)$. Consider sections of
$\Gamma(U,\mathcal Q/\mathcal O_U)$ of the form

$$
(D(X),X^\alpha Y^\beta;D(Y),0),
\qquad\alpha,\beta\in\mathbb Z.
$$

Such a section is specified on $D(X)$ by the rational function
$X^\alpha Y^\beta$ and on $D(Y)$ by the rational function $0$.
Their difference is simply $X^\alpha Y^\beta$, which belongs to the
structure sheaf on the intersection $D(X)\cap D(Y)=D(XY)$.
Thus we do obtain a section of the quotient sheaf; compare Lemma 5.9.

Depending on $\alpha$ and $\beta$, we determine whether this section
lies in the image. Equivalently, does it define the trivial element in
first cohomology? Coming from the left means that there is a rational
function $q\in K(X,Y)$ corresponding to the section. This means that
the differences on $D(X)$ and $D(Y)$ come from the structure sheaf,
so simultaneously

$$
q-X^\alpha Y^\beta\in\Gamma(D(X),\mathcal O_U)
$$

and

$$
q-0\in\Gamma(D(Y),\mathcal O_U).
$$

The second condition means

$$
q=\frac h{Y^n},
$$

while the first means

$$
\frac h{Y^n}-X^\alpha Y^\beta=\frac g{X^m}.
$$

The question is therefore whether the equation

$$
X^\alpha Y^\beta=\frac h{Y^n}-\frac g{X^m}
$$

has a solution with $g,h\in K[X,Y]$ and $m,n\in\mathbb N$.
If $\alpha\geq 0$ or $\beta\geq 0$, such a solution exists.
If $\alpha,\beta<0$, no solution is possible, since the right-hand side
equals

$$
\frac{hX^m-gY^n}{X^mY^n}.
$$

Multiplication by $X^mY^n$ shows the impossibility: the ideal
$(X^m,Y^n)$ contains only monomials divisible by one of its generators.

<!-- upstream_entity: Polynomring/Syzygiengarbe zu Variablen/Erste Kohomologie/Beispiel -->

### Example 25.9: cohomology of a syzygy sheaf {#br-bgk-2019-l25-exm-02}

We continue Example 16.9. Over the polynomial ring

$$
R=K[X_1,\ldots,X_n],\qquad n\geq 2,
$$

consider the short exact sequence

$$
0\longrightarrow\operatorname{Syz}(X_1,\ldots,X_n)
\longrightarrow R^n\longrightarrow(X_1,\ldots,X_n)
\longrightarrow 0.
$$

Restricting the associated sheaf sequence to the punctured space

$$
U=\mathbb A_K^n\setminus\{(0,\ldots,0)\}
$$

gives

$$
0\longrightarrow
\mathcal S
=\widetilde{\operatorname{Syz}(X_1,\ldots,X_n)}
\longrightarrow\mathcal O_U^n\longrightarrow\mathcal O_U
\longrightarrow 0.
$$

Evaluating this sheaf sequence on $U$ gives

$$
\begin{aligned}
0&\longrightarrow\operatorname{Syz}(X_1,\ldots,X_n)
\longrightarrow R^n\longrightarrow R
\longrightarrow H^1(U,\mathcal S)\\
&\longrightarrow H^1(U,\mathcal O_U^n)\longrightarrow.
\end{aligned}
$$

> **Editorial note - end of the exact sequence.** The printed source ends
> the sequence above with an arrow without displaying the next term.
> This edition preserves that printed ending and adds neither an ellipsis
> nor a term absent from the source.

Since the image of $R^n\to R$ is still the maximal ideal, this map
is not surjective. Therefore

$$
H^1(U,\mathcal S)\ne 0.
$$

<!-- upstream_entity: Schema/Integer/Einheitengarbe/Funktionenkörpergruppe/Erste Kohomologie/Fakt -->

### Lemma 25.10: first cohomology of the sheaf of units {#br-bgk-2019-l25-lem-05}

Let $(X,\mathcal O_X)$ be an integral scheme with function field $K$.
Let $\mathcal O_X^\times$ be the sheaf of units on $X$, and let
$\mathcal U$ be the constant sheaf with value $K^\times$. Then

$$
H^1(X,\mathcal O_X^\times)
=\Gamma(X,\mathcal U/\mathcal O_X^\times)
/\operatorname{im}\bigl(K^\times\longrightarrow
\Gamma(X,\mathcal U/\mathcal O_X^\times)\bigr).
$$

#### Proof {#br-bgk-2019-l25-lem-05-proof}

See Exercise 25.10.

We state the following important theorems without proof.

<!-- upstream_entity: Noethersches Schema/Affin/Kohomologisches Kriterium/Fakt -->

### Theorem 25.11: a cohomological criterion for affineness {#br-bgk-2019-l25-thm-01}

Let $X$ be a Noetherian scheme. The following properties are equivalent.

1. $X$ is an affine scheme.
2. For every quasi-coherent sheaf $\mathcal F$ on $X$, we have
   $H^i(X,\mathcal F)=0$.
3. For every coherent ideal sheaf $\mathcal I$ on $X$, we have
   $H^1(X,\mathcal I)=0$.

> **Edition note — omitted degree range.** In condition 2 the printed source
> leaves `i` unquantified. The standard criterion, and the only reading
> compatible with condition 1, is vanishing for every positive degree
> `i >= 1`; including degree zero would make the assertion false even for
> affine schemes.

<!-- upstream_entity: Noetherscher Raum/Dimension/Kohomologie/Verschwindungssatz/Fakt -->

### Theorem 25.12: vanishing above the dimension of the space {#br-bgk-2019-l25-thm-02}

Let $X$ be a Noetherian topological space of dimension $d$. Then

$$
H^i(X,\mathcal G)=0
$$

for $i>d$ and every sheaf of abelian groups $\mathcal G$.
