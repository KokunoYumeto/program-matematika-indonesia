---
title: "Lecture 23 - Injective Modules"
stable_id: br-bgk-2019-l23
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 23"
upstream_pageid: 109027
upstream_revid: 1003752
upstream_timestamp: "2025-06-08T16:35:51Z"
upstream_mediawiki_sha1: 9425b65cf4737b7bb6ef15e87d9c2a637ff93d28
source_url: "https://de.wikiversity.org/w/index.php?oldid=1003752"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
capture_identity: authority/wikiversity-bgk/unit-23/CAPTURE_IDENTITY.json
capture_identity_sha256: de194d9895b48db11613225072c9995377499c2c7ebf0a010de54bd3e4756c63
authority_manifest: authority/wikiversity-bgk/unit-23/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 96fb36e19dd3e6dcef56149150ce09c238843bee08ff36503d87a55284113775
authority_manifest_status: complete
official_pdf: authority/artifacts/bgk-lecture-23-official.pdf
official_pdf_sha256: dd1ea1b0f25c2d1b3988910761a2c0c4c217a5f8d4cfd8d0d0913c9078a84c3d
official_pdf_status: verified_source_bytes_and_upload_sha1
official_pdf_metadata: authority/wikiversity-bgk/unit-23/official-pdfs-api.json
official_pdf_source_bytes: 88712
official_pdf_source_sha1: 58050b993430d2f097b0c024871af997a3ff95d5
authority_precedence: "The frozen semantic revisions govern the text; the older official PDFs remain distinct supplementary witnesses."
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_bytes: 2104862
official_course_pdf_pages: 265
official_course_pdf_unit_pages: "200-209"
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
lecture_xml: authority/wikiversity-bgk/unit-23/lecture-23.xml
lecture_xml_sha256: db8e794226d9a120bf5eaa62009150a98ea0497160b6cfaa81e8cc070e1b9ca7
lecture_expanded_tex: authority/wikiversity-bgk/unit-23/lecture-23-expanded.tex
lecture_expanded_tex_sha256: dc5e24384944dc71f71640858e6418dcb3bf29aee6a731eb4f507f833857756a
media_credits: source/id-ID/media-credits-bgk-unit-23.md
rights_ledger: authority/RIGHTS-bgk-unit-23.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-23.json
asset_closure_sha256: 00673ca97e9a0caeca0bdf9bc02b1e18881dc5576ce2a9285cf904c503c189a7
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 23: Injective Modules {#br-bgk-2019-l23}

## Injective modules {#br-bgk-2019-l23-s01}

<!-- upstream_entity: Kommutativer Ring/Injektiver Modul/Definition -->

### Definition 23.1: injective module {#br-bgk-2019-l23-def-01}

Let $R$ be a commutative ring. An $R$-module $I$ is called *injective*
if, for every $R$-module $M$, every submodule $N\subseteq M$, and every
$R$-module homomorphism

$$
\varphi:N\longrightarrow I
$$

there is an extension

$$
\widetilde\varphi:M\longrightarrow I.
$$

Over a field, every vector space is injective. Indeed, every vector
subspace of a vector space has a direct complement, and the linear map
can be extended arbitrarily on that complement.
For $R=\mathbb Z$, the situation is already more complicated.

<!-- upstream_entity: Kommutative Gruppe/Divisibel/Definition -->

### Definition 23.2: divisible group {#br-bgk-2019-l23-def-02}

An abelian group $G$ is called *divisible* if, for every
$n\in\mathbb N_+$ and every $g\in G$, there is an $h\in G$ with

$$
g=nh.
$$

The group $\mathbb Z$ itself is not divisible. In contrast, $\mathbb Q$
is divisible as an abelian group, since for every $n\in\mathbb N_+$
the multiplication map

$$
\mathbb Q\longrightarrow\mathbb Q,\qquad x\longmapsto nx,
$$

is surjective: we can divide by $n$, which explains the name *divisible*.

<!-- upstream_entity: Divisible Gruppe/Grundlegende Eigenschaften/Fakt -->

### Lemma 23.3: quotient groups of divisible groups {#br-bgk-2019-l23-lem-01}

If $D$ is a divisible group, every quotient group $D/H$ is also divisible.

#### Proof {#br-bgk-2019-l23-lem-01-proof}

Let $n\in\mathbb N_+$. For every $d\in D$ there is an $e\in D$
with $d=ne$. Then in $D/H$ we also have

$$
[d]=n[e].
$$

<!-- upstream_entity: Kommutative Gruppe/Einbettung in divisible Gruppe/Fakt -->

### Lemma 23.4: embedding in a divisible group {#br-bgk-2019-l23-lem-02}

For every abelian group $G$, there is a divisible group $D$ with
$G\subseteq D$.

#### Proof {#br-bgk-2019-l23-lem-02-proof}

We write

$$
G=\mathbb Z^{(J)}/H
$$

for a suitable index set $J$ indexing a system of generators of $G$.
The free abelian group $\mathbb Z^{(J)}$ embeds in the divisible group
$\mathbb Q^{(J)}$. There is therefore an embedding

$$
G\subseteq\mathbb Q^{(J)}/H,
$$

and the group on the right is divisible by Lemma 23.3.

We state the following result without proof.

<!-- upstream_entity: Kommutative Gruppe/Injektiv/Divisibel/Fakt -->

### Lemma 23.5: divisible if and only if injective {#br-bgk-2019-l23-lem-03}

An abelian group $G$ is divisible if and only if $G$ is injective.

<!-- upstream_entity: Injektiver Modul/Kurze exakte Sequenz/Spaltung/Fakt -->

### Lemma 23.6: short exact sequences containing an injective module {#br-bgk-2019-l23-lem-04}

Let $I$ be an injective module over a commutative ring $R$.
Every short exact sequence of $R$-modules

$$
0\longrightarrow I\longrightarrow B\longrightarrow C\longrightarrow 0
$$

splits.

#### Proof {#br-bgk-2019-l23-lem-04-proof}

The identity $\operatorname{Id}_I:I\to I$ has an extension
$\varphi:B\to I$. This map gives the splitting.

<!-- upstream_entity: Kommutative Algebren/Injektiver Modul/Beziehung/Fakt -->

### Lemma 23.7: change of rings for injective modules {#br-bgk-2019-l23-lem-05}

Let $R$ be a commutative ring, $S$ a commutative $R$-algebra, and $I$
an injective $R$-module. Then the $S$-module

$$
\operatorname{Hom}_R(S,I)
$$

is also injective.

#### Proof {#br-bgk-2019-l23-lem-05-proof}

Let $A\subseteq B$ be $S$-modules and let

$$
\varphi:A\longrightarrow\operatorname{Hom}_R(S,I),
\qquad
a\longmapsto\varphi_a,
$$

be an $S$-module homomorphism. Explicitly, this means that

$$
\varphi_a(s)=\varphi_{as}(1).
$$

View $A$ and $B$ as $R$-modules and consider the composite
$R$-module homomorphism

$$
A\xrightarrow{\ \varphi\ }
\operatorname{Hom}_R(S,I)
\xrightarrow{\ \theta\mapsto\theta(1)\ }I.
$$

Since $I$ is injective as an $R$-module, this composite has an
$R$-linear extension

$$
\widetilde\varphi:B\longrightarrow I.
$$

We claim that the map

$$
B\longrightarrow\operatorname{Hom}_R(S,I),
\qquad
b\longmapsto\bigl(s\longmapsto\widetilde\varphi(sb)\bigr),
$$

is an $S$-module homomorphism. First, the composite map

$$
S\xrightarrow{\ 1\mapsto b\ }B
\xrightarrow{\ \widetilde\varphi\ }I
$$

clearly belongs to $\operatorname{Hom}_R(S,I)$. The overall assignment
is $S$-linear by the $S$-module structure on $\operatorname{Hom}_R(S,I)$.
For $a\in A$ we have

$$
\widetilde\varphi(sa)=\varphi_{as}(1)=\varphi_a(s),
$$

so the map is indeed an extension.

## Injective resolutions {#br-bgk-2019-l23-s02}

<!-- upstream_entity: Kommutativer Ring/Modul/Injektiver Modul/Fakt -->

### Corollary 23.8: embedding a module in an injective module {#br-bgk-2019-l23-cor-01}

For an $R$-module $M$ over a commutative ring $R$, there is an
injective module $I$ with $M\subseteq I$.

#### Proof {#br-bgk-2019-l23-cor-01-proof}

By Lemma 23.4, for the abelian group $M$ there is a divisible group $D$
and an embedding $M\subseteq D$. By Lemma 23.5, $D$ is an injective
$\mathbb Z$-module. Lemma 23.7 then says that the $R$-module

$$
\operatorname{Hom}_{\mathbb Z}(R,D)
$$

is also injective. The source displays the commutative diagram

$$
\begin{matrix}
M&\longrightarrow&D\\
\downarrow&&\downarrow\\
\operatorname{Hom}_{\mathbb Z}(R,M)
&\longrightarrow&
\operatorname{Hom}_{\mathbb Z}(R,D).
\end{matrix}
$$

The left vertical map is given by

$$
v\longmapsto\bigl(r\longmapsto rv\bigr),
$$

and the bottom horizontal map is induced by the embedding $M\hookrightarrow D$.
Both are injective $R$-module homomorphisms. Their composite gives
the $R$-submodule

$$
M\subseteq\operatorname{Hom}_{\mathbb Z}(R,D).
$$

> **Editorial note - right vertical arrow in the source diagram.** The source
> also states that the right vertical arrow is given by
> $v\mapsto(r\mapsto rv)$. However, the stated data make $D$ only a
> divisible abelian group, not an $R$-module, so that arrow is not defined
> without additional structure. The conclusion needs only the well-defined
> left vertical and bottom horizontal arrows above. This edition preserves
> the source diagram but uses the composite of those two arrows for the
> resulting embedding.

<!-- upstream_entity: Kommutativer Ring/Modul/Injektive Auflösung/Definition -->

### Definition 23.9: injective resolution {#br-bgk-2019-l23-def-03}

An *injective resolution* of an $R$-module $M$ over a commutative
ring $R$ is an exact complex of $R$-modules

$$
0\longrightarrow M\longrightarrow I_0\longrightarrow I_1
\longrightarrow I_2\longrightarrow\cdots,
$$

where $I_n$ is injective for every $n\geq 0$.

<!-- upstream_entity: Kommutativer Ring/Modul/Injektive Auflösung/Fakt -->

### Lemma 23.10: existence of injective resolutions {#br-bgk-2019-l23-lem-06}

Every $R$-module $M$ over a commutative ring $R$ has an injective resolution.

#### Proof {#br-bgk-2019-l23-lem-06-proof}

By Corollary 23.8, there is an injective module $I_0$ with $M\subseteq I_0$.
Similarly, for the quotient module $I_0/M$ there is an injective module
$I_1$ with $I_0/M\subseteq I_1$, and so on.

<!-- upstream_entity: Modul/Injektive Auflösung/Komplex/Anfangshomomorphismus/Fakt -->

### Lemma 23.11: extending an initial homomorphism to complexes {#br-bgk-2019-l23-lem-07}

Let $L$ and $M$ be $R$-modules over a commutative ring $R$. Let

$$
0\longrightarrow L\longrightarrow L_0\longrightarrow L_1
\longrightarrow\cdots
$$

be an exact complex,

$$
0\longrightarrow M\longrightarrow I_0\longrightarrow I_1
\longrightarrow\cdots
$$

an injective resolution, and

$$
\varphi:L\longrightarrow M
$$

an $R$-module homomorphism. Then there are $R$-module homomorphisms

$$
\varphi_n:L_n\longrightarrow I_n
$$

commuting with the homomorphisms in the two complexes.

#### Proof {#br-bgk-2019-l23-lem-07-proof}

We prove the existence of the commuting homomorphisms by induction on $n$.
Since $L\subseteq L_0$ and $I_0$ is injective, the homomorphism
$L\to M\subseteq I_0$ has a commuting extension

$$
\varphi_0:L_0\longrightarrow I_0.
$$

This establishes the base case. Now suppose the homomorphisms through
$\varphi_n$ already exist. Consider the commutative diagram

$$
\begin{matrix}
L_{n-1}&\longrightarrow&L_n&\longrightarrow&L_{n+1}\\
\downarrow\scriptstyle{\varphi_{n-1}}&&
\downarrow\scriptstyle{\varphi_n}&&\downarrow\\
I_{n-1}&\longrightarrow&I_n&\longrightarrow&I_{n+1},
\end{matrix}
$$

where the right vertical arrow remains to be constructed.
There is an injection

$$
L_n/\operatorname{bild}L_{n-1}\longrightarrow L_{n+1}.
$$

By commutativity, all of $L_{n-1}$ maps to zero in $I_{n+1}$.
Thus there is a homomorphism

$$
L_n/\operatorname{bild}L_{n-1}\longrightarrow I_{n+1},
$$

and this homomorphism has an extension to $L_{n+1}$.

In general, there are several homomorphisms of chain complexes in the
situation above. Nevertheless, they are homotopic to one another.

<!-- upstream_entity: Modul/Exakter Komplex und injektive Auflösung/Homotopie/Fakt -->

### Lemma 23.12: uniqueness up to homotopy {#br-bgk-2019-l23-lem-08}

Let $M$ be an $R$-module over a commutative ring $R$. Let

$$
0\longrightarrow M\longrightarrow L_0\longrightarrow L_1
\longrightarrow\cdots
$$

be an exact complex and let

$$
0\longrightarrow M\longrightarrow I_0\longrightarrow I_1
\longrightarrow\cdots
$$

be a complex in which all the modules $I_n$ are injective. If

$$
\varphi,\psi:L_\bullet\longrightarrow I_\bullet
$$

are homomorphisms of chain complexes, then $\varphi$ and $\psi$ are homotopic.

> **Editorial note - common initial map.** The source leaves implicit that
> $\varphi$ and $\psi$ extend the same map on the initial module $M$
> (in particular, the identity when comparing resolutions of $M$).
> This condition is needed for the induction at $n=0$; arbitrary chain
> maps need not be homotopic.

#### Proof {#br-bgk-2019-l23-lem-08-proof}

We define the homotopy maps inductively,

$$
\Theta_n:L_{n+1}\longrightarrow I_n
$$

and set

$$
\Theta_{-1}:L_0\longrightarrow M=I_{-1}
$$

to be the zero map. Note that $M$ is not injective in general.
Suppose the homotopy maps through $\Theta_{n-1}$ have already been
constructed. We have the diagram

$$
\begin{matrix}
L_{n-1}&\xrightarrow{\ d_n\ }&L_n&
\xrightarrow{\ d_{n+1}\ }&L_{n+1}\\
\downarrow&&\downarrow&&\downarrow\\
I_{n-1}&\xrightarrow{\ e_n\ }&I_n&
\xrightarrow{\ e_{n+1}\ }&I_{n+1},
\end{matrix}
$$

together with the diagonal map $\Theta_{n-1}:L_n\to I_{n-1}$, and

$$
\varphi_{n-1}-\psi_{n-1}
=e_{n-1}\circ\Theta_{n-2}+\Theta_{n-1}\circ d_n.
$$

Consider the homomorphism

$$
\varphi_n-\psi_n-e_n\circ\Theta_{n-1}
$$

from $L_n$ to $I_n$. For $x\in L_{n-1}$ we have

$$
\begin{aligned}
&(\varphi_n-\psi_n-e_n\circ\Theta_{n-1})(d_n(x))\\
&\quad=(\varphi_n-\psi_n)(d_n(x))
 -(e_n\circ\Theta_{n-1})(d_n(x))\\
&\quad=(\varphi_n-\psi_n)(d_n(x))
 -e_n(\Theta_{n-1}(d_n(x)))\\
&\quad=(\varphi_n-\psi_n)(d_n(x))
 -e_n\bigl(-e_{n-1}(\Theta_{n-2}(x))
 +\varphi_{n-1}(x)-\psi_{n-1}(x)\bigr)\\
&\quad=\varphi_n(d_n(x))-\psi_n(d_n(x))
 -e_n(\varphi_{n-1}(x))+e_n(\psi_{n-1}(x))\\
&\quad=\varphi_n(d_n(x))-e_n(\varphi_{n-1}(x))
 -\psi_n(d_n(x))+e_n(\psi_{n-1}(x))\\
&\quad=0,
\end{aligned}
$$

since $\varphi$ and $\psi$ commute with the differentials.
Thus $\varphi_n-\psi_n-e_n\circ\Theta_{n-1}$ maps the image of $d_n$
to zero. We obtain an induced homomorphism

$$
L_n/\operatorname{bild}d_n\longrightarrow I_n.
$$

Since the complex $L_\bullet$ is exact, there is an injective map

$$
L_n/\operatorname{bild}d_n\longrightarrow L_{n+1}.
$$

Since $I_n$ is injective, we obtain an extension

$$
-\Theta_n:L_{n+1}\longrightarrow I_n.
$$

We therefore have

$$
\varphi_n-\psi_n-e_n\circ\Theta_{n-1}
=-\Theta_n\circ d_{n+1}.
$$

> **Editorial note - sign in the source proof.** The final two displays
> introduce $-\Theta_n$, whereas the induction hypothesis uses a plus
> sign. Choose the extension as $\Theta_n$ instead. The resulting identity
> is $\varphi_n-\psi_n=e_n\circ\Theta_{n-1}
> +\Theta_n\circ d_{n+1}$, consistent with the preceding induction.

## Injective and flasque sheaves {#br-bgk-2019-l23-s03}

By definition, an injective module is characterised by the existence of
homomorphisms in certain situations. There is therefore a corresponding
notion of an *injective object* in any category in which one can speak
of injective homomorphisms. The usual setting is that of additive or
abelian categories; see the appendices. The category of sheaves of abelian
groups on a topological space, and the category of sheaves of modules
on a ringed space, are such abelian categories. We essentially proved this
in Lectures 5 and 6. We now show that in this setting too, a sheaf can
be embedded in an injective sheaf.

<!-- upstream_entity: Beringter Raum/Modulgarbe/Einbettung/Injektive Garbe/Fakt -->

### Lemma 23.13: embedding a sheaf of modules in an injective sheaf {#br-bgk-2019-l23-lem-09}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal M$ an
$\mathcal O_X$-module. There is an injective sheaf of modules
$\mathcal I$ on $X$ with $\mathcal M\subseteq\mathcal I$.

#### Proof {#br-bgk-2019-l23-lem-09-proof}

For every sheaf of modules $\mathcal M$, the map

$$
\mathcal M\longrightarrow\prod_{x\in X}i_*\mathcal M_x
$$

is an injective $\mathcal O_X$-module homomorphism. Here, for $x\in X$,
$i_*\mathcal M_x$ is the pushforward of the $\mathcal O_{X,x}$-module
$\mathcal M_x$, viewed as a sheaf on $\{x\}$, along the embedding

$$
i:\{x\}\longrightarrow X.
$$

By Corollary 23.8, for $\mathcal M_x$ there is an injective
$\mathcal O_{X,x}$-module $I_x$ at $x$. Set

$$
\mathcal I:=\prod_{x\in X}i_*I_x.
$$

We thus obtain inclusions of $\mathcal O_X$-modules

$$
\mathcal M\longrightarrow
\prod_{x\in X}i_*\mathcal M_x
\longrightarrow
\prod_{x\in X}i_*I_x.
$$

We must show that $\mathcal I$ is injective. Let
$\mathcal F\subseteq\mathcal G$ be $\mathcal O_X$-modules and suppose
we are given an $\mathcal O_X$-module homomorphism

$$
\varphi:\mathcal F\longrightarrow\mathcal I.
$$

By Exercise 3.18 and Lemma 4.3 of the Appendix, this corresponds to
an element

$$
(\varphi_x)\in
\prod_{x\in X}
\operatorname{Hom}_{\mathcal O_X}(\mathcal F,i_*I_x)
=
\prod_{x\in X}
\operatorname{Hom}_{\mathcal O_{X,x}}(\mathcal F_x,I_x).
$$

Each $\varphi_x$ has an extension
$\widetilde\varphi_x:\mathcal G_x\to I_x$, and these combine to give
an extension

$$
\widetilde\varphi:\mathcal G\longrightarrow\mathcal I.
$$

Injective sheaves are closely related to flasque sheaves.
The latter are often easier to work with computationally.

<!-- upstream_entity: Topologischer Raum/Welke Garbe/Definition -->

### Definition 23.14: flasque sheaf {#br-bgk-2019-l23-def-04}

A sheaf $\mathcal G$ on a topological space is called *flasque* if
for every pair of open subsets $U\subseteq V$, the restriction map

$$
\mathcal G(V)\longrightarrow\mathcal G(U)
$$

is surjective.

For a flasque sheaf, the restriction map

$$
\mathcal G(V)\longrightarrow\mathcal G(U)
$$

is thus surjective for arbitrary open subsets $U\subseteq V$.

<!-- upstream_entity: Topologischer Raum/Welke Garben/Grundlegende Eigenschaften/Fakt -->

### Lemma 23.15: basic properties of flasque sheaves {#br-bgk-2019-l23-lem-10}

Let $X$ be a topological space and

$$
0\longrightarrow\mathcal F\longrightarrow\mathcal G
\longrightarrow\mathcal H\longrightarrow 0
$$

a short exact sequence of sheaves of abelian groups.
The following properties hold.

1. If $\mathcal F$ is flasque, then the map on global sections

   $$
   \Gamma(X,\mathcal G)\longrightarrow\Gamma(X,\mathcal H)
   $$

   is surjective.

2. If $\mathcal F$ and $\mathcal G$ are flasque, then $\mathcal H$
   is also flasque.

#### Proof {#br-bgk-2019-l23-lem-10-proof}

For (1), let $t\in\Gamma(X,\mathcal H)$ be given. We use Zorn's lemma
and consider the set

$$
\mathcal M=
\{(U,s)\mid U\subseteq X\text{ open},\
s\in\Gamma(U,\mathcal G),\
s\longmapsto t|_U\}.
$$

We order $\mathcal M$ by setting

$$
(U,s)\preccurlyeq(U',s')
$$

if $U\subseteq U'$ and $s'$ extends $s$. By the sheaf property,
every chain has an upper bound. Zorn's lemma therefore gives a maximal
element $(U,s)$ of $\mathcal M$. We must show that $U=X$.

Suppose $U\ne X$ and take $x\notin U$. Since the sheaf morphism
$\mathcal G\to\mathcal H$ is surjective, there is an open neighbourhood
$x\in V$ and a section $r\in\Gamma(V,\mathcal G)$ mapping to $t|_V$.
Consequently,

$$
s|_{U\cap V}-r|_{U\cap V}
$$

maps to zero and belongs to $\Gamma(U\cap V,\mathcal F)$.
Since $\mathcal F$ is flasque, there is a section

$$
z\in\Gamma(X,\mathcal F)
$$

whose restriction to $U\cap V$ is
$s|_{U\cap V}-r|_{U\cap V}$. Replace $r$ with

$$
r'=r+z|_V.
$$

This element still maps to $t|_V$, and

$$
s|_{U\cap V}-r'|_{U\cap V}=z|_V-z|_V=0.
$$

Thus $s$ and $r'$, as sections of $\mathcal G$ over $U$ and $V$
respectively, agree on the overlap and determine a section

$$
s'\in\Gamma(U\cup V,\mathcal G)
$$

mapping to $t$. This contradicts the maximality of $U$.

> **Editorial note - the sheaf containing the glued section.** The frozen
> source prints $s'\in\Gamma(U\cup V,\mathcal F)$. However, $s$ and $r'$
> have just been specified as sections of $\mathcal G$, and the glued
> section must map to $t\in\Gamma(X,\mathcal H)$. The argument therefore
> requires $s'\in\Gamma(U\cup V,\mathcal G)$, as used above.
> This edition explicitly records that change of symbol and leaves the
> rest of the proof unchanged.
> In the preceding cancellation display, both copies of $z|_V$ must
> also be restricted to $U\cap V$, where the left-hand side is defined.

Statement (2) follows from (1).

<!-- upstream_entity: Beringter Raum/Modul/Injektiv/Welk/Fakt -->

### Lemma 23.16: injective sheaves are flasque {#br-bgk-2019-l23-lem-11}

Let $(X,\mathcal O_X)$ be a ringed space and $\mathcal I$ an injective
$\mathcal O_X$-module. Then $\mathcal I$ is flasque.

#### Proof {#br-bgk-2019-l23-lem-11-proof}

Let $U\subseteq X$ be an open subset. Consider the presheaf

$$
\mathcal P(V):=
\begin{cases}
\mathcal O_X(V),&\text{if }V\subseteq U,\\
0,&\text{otherwise},
\end{cases}
$$

and denote its sheafification by $\mathcal O_U$. By Lemma 5.2 (4),
the natural presheaf homomorphism $\mathcal P\to\mathcal O_X$ induces
a sheaf homomorphism

$$
\mathcal O_U\longrightarrow\mathcal O_X.
$$

This homomorphism is injective. Moreover,

$$
\operatorname{Hom}(\mathcal O_U,\mathcal I)
=\Gamma(U,\mathcal I).
$$

Since $\mathcal I$ is injective, each element here extends to an element of

$$
\operatorname{Hom}(\mathcal O_X,\mathcal I)
=\Gamma(X,\mathcal I).
$$

This means that the restriction map

$$
\Gamma(X,\mathcal I)\longrightarrow\Gamma(U,\mathcal I)
$$

is surjective.
