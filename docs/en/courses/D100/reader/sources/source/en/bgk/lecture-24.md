---
title: "Lecture 24 - Right Derived Functors"
stable_id: br-bgk-2019-l24
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 24"
upstream_pageid: 109028
upstream_revid: 1003753
upstream_timestamp: "2025-06-08T16:37:44Z"
upstream_mediawiki_sha1: e320bcba4562078adb0a963725102422a19ce046
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003753"
authority_capture_identity: authority/wikiversity-bgk/unit-24/CAPTURE_IDENTITY.json
authority_capture_identity_sha256: 842c6963306e8d2f624a632554364d970b2d021300974752b7337b8e70b6f1f8
lecture_xml: authority/wikiversity-bgk/unit-24/lecture-24.xml
lecture_xml_sha256: 07145dbf2a9c0a27475b8a8a39f7099a1652d07e7ff9aedbad5c8eafb1f7aacd
lecture_expanded_tex: authority/wikiversity-bgk/unit-24/lecture-24-expanded.tex
lecture_expanded_tex_sha256: 57345576a2ae9403bcb2b0598be4420efaf09d0605ae34fb1ba5bec3188d84a8
official_pdf_inventory: authority/wikiversity-bgk/unit-24/official-pdfs-api.json
official_pdf_inventory_sha256: 303704d2786c8c83db4a4d3ee5104de5078c240f9245257d25437ec40f812bee
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "209-214"
media_credits: source/id-ID/media-credits-bgk-unit-24.md
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. This edition does not extend the rights in the PDFs or any of their components."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
authority_manifest: authority/wikiversity-bgk/unit-24/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b938d6366fb91058f9e35b1b3b7c4ba255f5f53a7860f9f0dc2b905f732b263b
official_pdf: authority/artifacts/bgk-lecture-24-official.pdf
official_pdf_sha256: 5f06a64aff74b064df8753ccdf2fe82358fd0f869f67a4df64082743d754a355
component_metadata: authority/commons-imageinfo-bgk-unit-24.json
component_metadata_sha256: 9b595f13f72a9416a587b97aa694b5655c538fa88ffbc69b54508da64c394f97
rights_ledger: authority/RIGHTS-bgk-unit-24.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-24.json
asset_closure_sha256: 1583dbc371fb9c97b43346d27b50e1e733424d89c4972cc1e6171e5c258c019b
media_credits_sha256: f3db5e0d70186a875db9c554930417bec4413b763f0cd4061f09a577288f440a
---

# Lecture 24: Right Derived Functors {#br-bgk-2019-l24}

## Abelian categories {#br-bgk-2019-l24-s01}

The notion of an abelian category is described abstractly by a list of
axioms, which we have collected in an appendix. The following four main
examples are important for us.

1. The category of abelian groups with group homomorphisms.
2. The category of $R$-modules over a commutative ring, with
   $R$-module homomorphisms.
3. The category of sheaves of abelian groups on a topological space $X$,
   with sheaf homomorphisms.
4. The category of $\mathcal O_X$-modules on a ringed space
   $(X,\mathcal O_X)$, with $\mathcal O_X$-module homomorphisms.

In each of these categories, the meaning of a short exact sequence or
an exact complex is clear. Moreover, in these categories every object
can be embedded in an injective object of the category, so injective
resolutions can also be constructed; see Corollary 23.8 and Lemma 23.13.
This property even deserves a name of its own.

<!-- upstream_entity: Abelsche Kategorie/Genügend viele injektive Objekte/Definition -->

### Definition 24.1: enough injective objects {#br-bgk-2019-l24-def-01}

An abelian category $\mathcal A$ is said to *have enough injective objects*
if, for every object $M\in\mathcal A$, there is an injective object $I$
and a monomorphism

$$
M\longrightarrow I.
$$

## Left exact additive functors {#br-bgk-2019-l24-s02}

<!-- upstream_entity: Kovarianter Funktor/Additive Kategorie/Additiv/Definition -->

### Definition 24.2: additive functor {#br-bgk-2019-l24-def-02}

Let $\mathcal A$ and $\mathcal B$ be additive categories.
A covariant functor

$$
F:\mathcal A\longrightarrow\mathcal B
$$

is called *additive* if, for objects $G,H\in\mathcal A$, the map

$$
\operatorname{Mor}(G,H)\longrightarrow
\operatorname{Mor}(F(G),F(H)),
\qquad \varphi\longmapsto F(\varphi),
$$

is a group homomorphism.

<!-- upstream_entity: Kovarianter Funktor/Abelsche Kategorie/Linksexakt/Definition -->

### Definition 24.3: left exact functor {#br-bgk-2019-l24-def-03}

Let $\mathcal A$ and $\mathcal B$ be abelian categories.
A covariant functor

$$
F:\mathcal A\longrightarrow\mathcal B
$$

is called *left exact* if it is additive and, for every short exact sequence

$$
0\longrightarrow A\longrightarrow B\longrightarrow C\longrightarrow 0
$$

in $\mathcal A$, the sequence

$$
0\longrightarrow F(A)\longrightarrow F(B)\longrightarrow F(C)
$$

is exact in $\mathcal B$.

Two functors with both of these properties will be important for us.

<!-- upstream_entity: Modul/Hom/Linksexakt und genügend Injektive/Beispiel -->

### Example 24.4: the Hom functor {#br-bgk-2019-l24-exm-01}

Let $R$ be a commutative ring and $A$ a fixed $R$-module.
The assignment taking each $R$-module $M$ to the module of homomorphisms

$$
\operatorname{Hom}_R(A,M)
$$

is left exact; see Exercise 24.1.

<!-- upstream_entity: Topologischer Raum/Garbe/Globale Auswertung/Linksexakt und genügend Injektive/Beispiel -->

### Example 24.5: the global sections functor {#br-bgk-2019-l24-exm-02}

Let $X$ be a topological space and $\mathcal A$ the category of sheaves
of abelian groups on $X$, with the assignment

$$
\mathcal G\longmapsto\Gamma(X,\mathcal G).
$$

Let

$$
\mathcal B=\operatorname{ABEL}
$$

be the category of abelian groups, and let $F$ be evaluation on all of $X$.
Then $\mathcal A$ has enough injective objects, and $F$ is a covariant,
additive, left exact functor. Left exactness follows from Lemma 6.8,
and the existence of enough injective sheaves follows from Lemma 23.13.

The assignments in the examples above are not right exact; see
Exercise 24.2 and Example 6.6. Among other things, the cohomology theories
we shall study will provide a theoretical account of this failure
of right exactness.

> **Edition note — scope of the right-exactness claim.** The source's
> statement is a general warning, not an assertion about every possible
> parameter or space. For example, `Hom(A,-)` is exact when `A` is
> projective, and global sections can be exact in special situations.

## Derived functors {#br-bgk-2019-l24-s03}

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Linksexakter Funktor/Rechtsabgeleiteter Funktor/Definition -->

### Definition 24.6: right derived functor {#br-bgk-2019-l24-def-04}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let

$$
F:\mathcal A\longrightarrow\mathcal B
$$

be a covariant, additive, left exact functor. The *$n$th right derived functor*

$$
R^nF:\mathcal A\longrightarrow\mathcal B,
\qquad n\in\mathbb N,
$$

is defined as follows. For an object $M\in\mathcal A$, take an injective
resolution $I^\bullet$ of $M$ and set

$$
R^nF(M):=H^n(F(I^\bullet)).
$$

For a homomorphism $\varphi:M\longrightarrow N$ in $\mathcal A$,
take an extension

$$
\widetilde\varphi:I^\bullet\longrightarrow J^\bullet,
$$

where $J^\bullet$ is an injective resolution of $N$, and set

$$
R^nF(\varphi):=
\bigl(H^n(\widetilde\varphi):H^n(F(I^\bullet))
\longrightarrow H^n(F(J^\bullet))\bigr),
$$

using the induced homomorphism on homology in the sense of
Lemma 8.5 of the Appendix.

> **Edition note — induced-map notation.** The printed source labels this
> map $H^n(\widetilde\varphi)$, although the displayed source and target are
> the cohomology of the complexes obtained after applying $F$; the intended
> map is therefore the one induced by $F(\widetilde\varphi)$. The proof of
> Theorem 24.7 later switches from superscript $H^n$ to subscript $H_n$ for
> the same construction. This edition preserves both printed conventions
> while making their relationship explicit.

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Rechtsabgeleiteter Funktor/Delta-Eigenschaften/Fakt -->

### Theorem 24.7: delta properties of right derived functors {#br-bgk-2019-l24-thm-01}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let
$F:\mathcal A\longrightarrow\mathcal B$ be a covariant, additive,
left exact functor, and let $R^nF$ denote its right derived functors.
The following properties hold.

1. $R^nF$ is a well-defined additive functor from $\mathcal A$
   to $\mathcal B$.
2. There is a natural isomorphism

   $$
   R^0F\cong F.
   $$

3. For every short exact sequence

   $$
   0\longrightarrow A\longrightarrow B\longrightarrow C\longrightarrow 0
   $$

   in $\mathcal A$ and every $n\in\mathbb N$, there is a natural
   connecting homomorphism

   $$
   \delta^n:R^nF(C)\longrightarrow R^{n+1}F(A)
   $$

   such that there is an exact complex in $\mathcal B$,

   $$
   \begin{aligned}
   \ldots\longrightarrow R^{n-1}F(C)
   &\overset{\delta^{n-1}}{\longrightarrow}R^nF(A)
   \longrightarrow R^nF(B)\longrightarrow R^nF(C)\\
   &\overset{\delta^n}{\longrightarrow}R^{n+1}F(A)
   \longrightarrow R^{n+1}F(B)\longrightarrow\ldots .
   \end{aligned}
   $$

4. For a homomorphism of exact sequences

   $$
   \begin{matrix}
   0&\longrightarrow&A&\longrightarrow&B&\longrightarrow&C&\longrightarrow&0\\
   \downarrow&&\downarrow&&\downarrow&&\downarrow&&\downarrow\\
   0&\longrightarrow&A'&\longrightarrow&B'&\longrightarrow&C'&\longrightarrow&0,
   \end{matrix}
   $$

   the diagram

   $$
   \begin{matrix}
   R^nF(C)&\overset{\delta^n}{\longrightarrow}&R^{n+1}F(A)\\
   \downarrow&&\downarrow\\
   R^nF(C')&\overset{\delta^n}{\longrightarrow}&R^{n+1}F(A')
   \end{matrix}
   $$

   commutes.

#### Proof {#br-bgk-2019-l24-thm-01-proof}

1. To establish well-definedness, that is, independence of the chosen
   injective resolution, we give the proof when $\mathcal A$ is the
   category of $R$-modules; formulating the general case takes a little
   more work. Let

   $$
   0\longrightarrow N\longrightarrow L_0\longrightarrow L_1
   \longrightarrow\ldots
   $$

   and

   $$
   0\longrightarrow N\longrightarrow I_0\longrightarrow I_1
   \longrightarrow\ldots
   $$

   be injective resolutions of a module $N$. By Lemma 23.11,
   there are homomorphisms of chain complexes

   $$
   \varphi:L_\bullet\longrightarrow I_\bullet
   $$

   and

   $$
   \psi:I_\bullet\longrightarrow L_\bullet.
   $$

   By Lemma 23.12, the composites $\psi\circ\varphi$ and
   $\varphi\circ\psi$ are homotopic to the identity on $L_\bullet$
   and $I_\bullet$, respectively. By Lemma 8.9 of the Appendix, the
   same holds for the associated homomorphisms on the complexes
   $F(L_\bullet)$ and $F(I_\bullet)$. Thus for the induced homomorphisms
   on homology, the composite

   $$
   H_n(F(L_\bullet))
   \overset{H_n(\varphi)}{\longrightarrow}H_n(F(I_\bullet))
   \overset{H_n(\psi)}{\longrightarrow}H_n(F(L_\bullet))
   $$

   is the identity. Hence $H(\varphi)$ is a canonical isomorphism.
   Additivity always holds on homology by Lemma 8.5 of the Appendix.

2. Let $I^\bullet$ be an injective resolution of the object $M$.
   The homology in degree $0$ of the complex

   $$
   0\longrightarrow F(I^0)\longrightarrow F(I^1)
   \longrightarrow F(I^2)\longrightarrow\ldots
   $$

   is simply the kernel of the homomorphism

   $$
   F(I^0)\longrightarrow F(I^1).
   $$

   Since $F$ is left exact, this kernel equals $F(M)$.

3. By Lemma 9.9 of the Appendix, there is a commutative diagram

   $$
   \begin{matrix}
   &&0&&0&&0&&\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   0&\longrightarrow&A&\longrightarrow&B&\longrightarrow&C&\longrightarrow&0\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   0&\longrightarrow&I^0&\longrightarrow&J^0&\longrightarrow&K^0&\longrightarrow&0\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   0&\longrightarrow&I^1&\longrightarrow&J^1&\longrightarrow&K^1&\longrightarrow&0\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   &&\vdots&&\vdots&&\vdots&&
   \end{matrix}
   $$

   with exact rows and columns. Since every row except the initial
   sequence splits, for every $n\geq0$ we obtain a short exact sequence

   $$
   0\longrightarrow F(I^n)\longrightarrow F(J^n)
   \longrightarrow F(K^n)\longrightarrow0.
   $$

   Thus there is a commutative diagram

   $$
   \begin{matrix}
   0&\longrightarrow&F(I^{n-1})&\longrightarrow&F(J^{n-1})&\longrightarrow&F(K^{n-1})&\longrightarrow&0\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   0&\longrightarrow&F(I^n)&\longrightarrow&F(J^n)&\longrightarrow&F(K^n)&\longrightarrow&0\\
   &&\downarrow&&\downarrow&&\downarrow&&\\
   0&\longrightarrow&F(I^{n+1})&\longrightarrow&F(J^{n+1})&\longrightarrow&F(K^{n+1})&\longrightarrow&0
   \end{matrix}
   $$

   with exact rows. In such a situation, by Lemma 8.6 of the Appendix,
   there is a homomorphism from the kernel of

   $$
   F(K^{n-1})\longrightarrow F(K^n)
   $$

   to the kernel of

   $$
   F(I^n)\longrightarrow F(I^{n+1}),
   $$

   and hence also to $R^nF(A)$. The image of $F(K^{n-2})$ maps
   to $0$, so this induces a homomorphism

   $$
   R^{n-1}F(C)\longrightarrow R^nF(A).
   $$

   > **Edition note — target of the connecting construction.** The source
   > compresses the diagram chase when it says that there is a homomorphism
   > from the first kernel to the second kernel. Canonically, a cycle in
   > `F(K)` lifts to `F(J)`, its differential lies in the cycle kernel of
   > `F(I)`, and only its class modulo boundaries is independent of the
   > chosen lift. Thus the canonical target is the cohomology quotient
   > $R^nF(A)$, not in general the kernel itself; the fact that boundaries
   > map to zero is what makes the displayed connecting homomorphism well
   > defined.

4. See Exercise 24.5.

The map $\delta$ is also called the *connecting homomorphism*.

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Rechtsabgeleiteter Funktor/Injektives Objekt/Fakt -->

### Theorem 24.8: injective objects are acyclic {#br-bgk-2019-l24-thm-02}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let
$F:\mathcal A\longrightarrow\mathcal B$ be a covariant, additive,
left exact functor. For every injective object $I$ of $\mathcal A$
and every $n\geq1$, the right derived functors satisfy

$$
R^nF(I)=0.
$$

#### Proof {#br-bgk-2019-l24-thm-02-proof}

This is immediate, since we can use the injective resolution

$$
I_0=I\longrightarrow0\longrightarrow0\longrightarrow\ldots .
$$

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Rechtsabgeleiteter Funktor/Azyklisches Objekt/Definition -->

### Definition 24.9: acyclic object {#br-bgk-2019-l24-def-05}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let
$F:\mathcal A\longrightarrow\mathcal B$ be a covariant, additive,
left exact functor. An object $Z$ of $\mathcal A$ is called *acyclic*
(with respect to $F$) if for every $n\geq1$ the right derived functors satisfy

$$
R^nF(Z)=0.
$$

By Theorem 24.8, every injective object is acyclic.

<!-- upstream_entity: Abelsche Kategorie/Genügend Injektive/Rechtsabgeleiteter Funktor/Kurze exakte Sequenz/Azyklisches Objekt in Mitte/Fakt -->

### Corollary 24.10: dimension shifting through an acyclic object {#br-bgk-2019-l24-cor-01}

Let $\mathcal A$ and $\mathcal B$ be abelian categories, with
$\mathcal A$ having enough injective objects. Let
$F:\mathcal A\longrightarrow\mathcal B$ be a covariant, additive,
left exact functor. Let $A$ be an object of $\mathcal A$ and suppose

$$
0\longrightarrow A\longrightarrow Z
$$

is exact, with $Z$ an acyclic object. Then

$$
R^1F(A)=F(Z/A)/\operatorname{bild}(F(Z))
$$

and

$$
R^nF(A)=R^{n-1}F(Z/A)
$$

for $n\geq2$.

#### Proof {#br-bgk-2019-l24-cor-01-proof}

Consider the short exact sequence

$$
0\longrightarrow A\longrightarrow Z\longrightarrow Z/A\longrightarrow0.
$$

The statements follow from the long exact sequence, since by hypothesis
the middle terms satisfy $R^nF(Z)=0$.

<!-- upstream_entity: Modul/Extmoduln/Rechtsderiviert/Definition -->

### Definition 24.11: the Ext functor {#br-bgk-2019-l24-def-06}

Let $R$ be a commutative ring and $M$ an $R$-module.
The right derived functors of

$$
N\longmapsto\operatorname{Hom}_R(M,N)
$$

(from the category of $R$-modules to itself) are called the *Ext functors*
and are denoted by

$$
\operatorname{Ext}^n(M,N).
$$

By definition, to compute the Ext modules we must take an injective
resolution of the second module,

$$
0\longrightarrow N\longrightarrow I_0\longrightarrow I_1
\longrightarrow I_2\longrightarrow\ldots,
$$

and then determine the homology of the complex

$$
\operatorname{Hom}(M,I_{n-1})\longrightarrow
\operatorname{Hom}(M,I_n)\longrightarrow
\operatorname{Hom}(M,I_{n+1}).
$$
