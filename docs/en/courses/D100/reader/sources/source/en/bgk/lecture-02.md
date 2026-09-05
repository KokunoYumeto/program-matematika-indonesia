---
title: "Lecture 2 - Sections, the Hairy Ball Theorem, and Gluing Data"
stable_id: br-bgk-2019-l02
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 2"
upstream_pageid: 109004
upstream_revid: 1019972
upstream_timestamp: "2025-08-09T13:35:26Z"
upstream_mediawiki_sha1: d666b90510ef490f9a1d545df6394ebc55d5dcc5
source_url: "https://de.wikiversity.org/w/index.php?oldid=1019972"
authority_manifest: authority/wikiversity-bgk/unit-02/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a348b56811fe98266feff9108a21a436a9b8f07a343321feab7d9fbb3b75e64d
lecture_xml: authority/wikiversity-bgk/unit-02/lecture-02.xml
lecture_xml_sha256: 9e5823b1031d2d8877147923324a95a78ff255d00a840745fe6a83dddb749670
lecture_expanded_tex: authority/wikiversity-bgk/unit-02/lecture-02-expanded.tex
lecture_expanded_tex_sha256: ae973e45a0aa3228ac31a61dd71b995d7872bfaaf8adca164bd97bd045f000b3
official_pdf: authority/artifacts/bgk-lecture-02-official.pdf
official_pdf_sha256: b898d226f1b680d4fe08873402847c9580d05aca8ca430ea8e6cca466cbbc391
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF and media retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 2: Sections, the Hairy Ball Theorem, and Gluing Data {#br-bgk-2019-l02}

## Sections {#br-bgk-2019-l02-s01}

### Definition 2.1: continuous section {#br-bgk-2019-l02-def-01}

Let $X$ and $Y$ be topological spaces, and let

$$
p:Y\longrightarrow X
$$

be a continuous map. A *continuous section* of $p$ is a continuous map

$$
s:X\longrightarrow Y
$$

such that

$$
p\circ s=\operatorname{Id}_X.
$$

For example, we may think of $Y$ as a vector bundle over $X$. A section can exist only if $p$ is surjective, as is always the case for a vector bundle. A section is sometimes identified with its image; this causes no difficulty, since every section is injective. The *zero section* plays a special role: to each base point $P$, it assigns the zero vector in the vector space $V_P$. Sections of tangent bundles have a name of their own.

### Definition 2.2: vector field {#br-bgk-2019-l02-def-02}

Let $M$ be a differentiable manifold. A map

$$
F:M\longrightarrow TM
$$

satisfying

$$
F(P)\in T_PM
$$

for every point $P\in M$ is called a (time-independent) *vector field*.

## The hairy ball theorem {#br-bgk-2019-l02-s02}

> **Source illustration - `Hairy_ball_one_pole.jpg`.** A continuous vector field on the $2$-sphere must have at least one zero.

![A hairy ball with a single whorl at a pole, illustrating that a continuous tangent vector field on a sphere must have a zero](authority/assets/bgk-hairy-ball-one-pole-500.jpg)

### Theorem 2.3: the hairy ball theorem {#br-bgk-2019-l02-thm-01}

On the $2$-sphere, every continuous vector field

$$
f:S^2\longrightarrow TS^2
$$

has at least one zero.

In particular, the tangent bundle of the $2$-sphere is not trivial. There are various interpretations of this theorem. For example, it says that there is always a point on the Earth's surface where there is no wind, when the instantaneous horizontal wind is regarded as a continuous vector field. Similarly, it is impossible to lay all the spines of a hedgehog flat against its body.

### Remark 2.4: application to Example 1.2 {#br-bgk-2019-l02-rem-01}

The hairy ball theorem explains why the vector bundle $L$ from Example 1.2, over

$$
\mathbb R^3\setminus\{(0,0,0)\},
$$

has no continuous trivialisation. First,

$$
S^2\subset\mathbb R^3\setminus\{(0,0,0)\},
$$

so we can restrict $L$ to $S^2$. If $L$ itself were trivial, this restriction would also be trivial. But the restriction of $L$ to the unit sphere is the tangent bundle of the unit sphere. Indeed, the condition

$$
ru+sv+tw=0
$$

can be interpreted as an orthogonality relation, and the extrinsic tangent space at a point $(r,s,t)$ of the sphere is determined by this relation. If the tangent bundle were trivial, there would be two continuous vector fields $u$ and $v$ forming a basis of the tangent space at every point of the sphere. The hairy ball theorem, however, says that even a single vector field must have a zero, and $0$ cannot belong to a basis.

## Gluing data for topological spaces {#br-bgk-2019-l02-s03}

A vector bundle $V\to X$ is “assembled” from the trivial vector bundles $V|_{U_i}\to U_i$ for an open cover of $X$. The precise way these pieces are assembled determines the vector bundle, and can be described conveniently by gluing data. We first need gluing data for topological spaces in general.

The underlying question is: what must we know about an open cover

$$
X=\bigcup_{i\in I}U_i
$$

in order to reconstruct the space $X$? The short answer is that we need to know the $U_i$, the pairwise intersections $U_i\cap U_j$ as subsets both of $U_i$ and of $U_j$, how these two copies are identified, and a compatibility condition on the identifications involving each triple of sets.

> **Source illustration - `Inclusion-exclusion.svg`.** Three overlapping sets illustrate the need for a compatibility condition on triple intersections.

![Diagram of three overlapping circular sets, with the regions of intersection distinguished by colour](authority/assets/bgk-inclusion-exclusion-500.png)

### Definition 2.5: gluing data for topological spaces {#br-bgk-2019-l02-def-03}

*Gluing data* for topological spaces consist of:

1. a family of topological spaces $(U_i)_{i\in I}$;
2. for each pair $(i,j)$, an open subset

   $$
   U_{ij}\subseteq U_i,
   $$

   with $U_{ii}=U_i$;
3. for each pair $(i,j)$, a homeomorphism

   $$
   \varphi_{ji}:U_{ij}\longrightarrow U_{ji},
   $$

   with $\varphi_{ii}=\operatorname{Id}_{U_i}$;
4. for all $i,j,k\in I$, the *cocycle condition*

   $$
   \varphi_{kj}\circ\varphi_{ji}=\varphi_{ki}
   $$

   holds as an equality of maps from $U_{ik}\cap U_{ij}$ to $U_k$.

### Lemma 2.6: reconstructing a space from gluing data {#br-bgk-2019-l02-lem-01}

Suppose gluing data $(U_i)_{i\in I}$ for topological spaces are given. Then there exist a uniquely determined topological space $X$, an open cover

$$
X=\bigcup_{i\in I}V_i,
$$

and homeomorphisms

$$
\psi_i:U_i\longrightarrow V_i
$$

such that

$$
\psi_i(U_{ij})=V_i\cap V_j
$$

and

$$
\psi_i|_{U_{ij}}
=\psi_j|_{U_{ji}}\circ\varphi_{ji}.
$$

#### Proof {#br-bgk-2019-l02-lem-01-proof}

Let $Y$ be the disjoint union of the $U_i$. Define an equivalence relation $\sim$ on $Y$ by declaring $x_i\in U_i$ and $x_j\in U_j$ equivalent when

$$
x_i\in U_{ij},\qquad x_j\in U_{ji},\qquad
\varphi_{ji}(x_i)=x_j.
$$

The properties of an equivalence relation are ensured by the cocycle condition; see Exercise 2.14. Set

$$
X:=Y/{\sim}
$$

and equip $X$ with the quotient topology. The composites

$$
U_i\longrightarrow Y\longrightarrow X
$$

are the maps $\psi_i$, and the $V_i$ are their images. Thus $\psi_i:U_i\to V_i$ are homeomorphisms. For $x\in U_i$,

$$
\psi_i(x)\in V_j
$$

if and only if $x\in U_{ij}$, since precisely in this case $x$ is identified with $\varphi_{ji}(x)$. Hence

$$
\psi_i(U_{ij})=V_i\cap V_j.
$$

> **Editorial note - order of indices in the proof.** Under the convention in Definition 2.5, $\varphi_{ji}:U_{ij}\to U_{ji}$. In the preceding sentence, the source prints $\varphi_{ij}(x)$ for $x\in U_{ij}$, although the correctly typed map is $\varphi_{ji}(x)$. This edition displays the indices consistent with the domain and codomain in the proof and preserves the source form in this note.

Commutativity of the diagram

$$
\begin{array}{ccc}
U_{ij}&\stackrel{\varphi_{ji}}{\longrightarrow}&U_{ji}\\
&\searrow\psi_i&\downarrow\psi_j\\
&&V_i\cap V_j
\end{array}
$$

follows in the same way. $\square$

### Lemma 2.7: gluing continuous maps {#br-bgk-2019-l02-lem-02}

Suppose gluing data $(U_i)_{i\in I}$ for topological spaces are given. Let $Z$ be another topological space, and suppose continuous maps

$$
\theta_i:U_i\longrightarrow Z
$$

are given satisfying

$$
\theta_i|_{U_{ij}}
=\bigl(\theta_j|_{U_{ji}}\bigr)\circ\varphi_{ji}.
$$

Then there is a unique continuous map

$$
\theta:X\longrightarrow Z
$$

such that

$$
\theta|_{V_i}\circ\psi_i=\theta_i,
$$

where $X$ is the topological space determined by the gluing data as in Lemma 2.6, whose notation we also use.

> **Editorial note - ill-typed composition identity.** The source prints $(\psi_i)^{-1}\circ\theta|_{V_i}=\theta_i$, but this composition is not defined: $\theta|_{V_i}$ takes values in $Z$, whereas $(\psi_i)^{-1}$ has domain $V_i$. This edition displays the correctly typed identity $\theta|_{V_i}\circ\psi_i=\theta_i$ in the lemma and preserves the source form in this note.

#### Proof {#br-bgk-2019-l02-lem-02-proof}

See Exercise 2.18.

## Gluing data for vector bundles {#br-bgk-2019-l02-s04}

### Definition 2.8: gluing data for real vector bundles {#br-bgk-2019-l02-def-04}

*Gluing data* for a real vector bundle of rank $r$ over a topological space $X$ consist of:

1. an open cover

   $$
   X=\bigcup_{i\in I}U_i;
   $$

2. a family of real vector bundles of rank $r$,

   $$
   (E_i\longrightarrow U_i)_{i\in I};
   $$

3. for each pair $(i,j)$, an isomorphism of vector bundles

   $$
   \varphi_{ji}:E_i|_{U_i\cap U_j}
   \longrightarrow E_j|_{U_i\cap U_j}
   $$

   over $U_i\cap U_j$;
4. for all $i,j,k\in I$, the cocycle condition

   $$
   \varphi_{kj}\circ\varphi_{ji}=\varphi_{ki}
   $$

   holds as an equality of maps from $E_i|_{U_i\cap U_j\cap U_k}$ to $E_k|_{U_i\cap U_j\cap U_k}$.

### Remark 2.9: matrix description {#br-bgk-2019-l02-rem-02}

Typically, the vector bundles in item (2) of Definition 2.8 are trivial bundles over $U_i$, namely

$$
E_i=\mathbb R^r\times U_i.
$$

The isomorphisms in item (3) are then simply bijective linear maps

$$
\varphi_{ji}:\mathbb R^r\longrightarrow\mathbb R^r
$$

depending continuously on the base point in $U_i\cap U_j$. They can be described compactly as continuous maps

$$
\varphi_{ji}:U_i\cap U_j\longrightarrow
\operatorname{GL}_r(\mathbb R)
$$

into the general linear group. Thus an invertible $r\times r$ matrix is assigned continuously to each base point; continuity means that every matrix entry is a continuous function. This is called a *matrix description* of the bundle. The cocycle condition still applies.

### Lemma 2.10: gluing vector bundles {#br-bgk-2019-l02-lem-03}

Suppose gluing data $(E_i)_{i\in I}$ over a topological space

$$
X=\bigcup_{i\in I}U_i.
$$

are given. Then there exist a uniquely determined real vector bundle $E\to X$ and isomorphisms

$$
\psi_i:E_i\longrightarrow E|_{U_i}
$$

such that

$$
\psi_i|_{E_i|_{U_i\cap U_j}}
=\psi_j|_{E_j|_{U_i\cap U_j}}\circ\varphi_{ji}.
$$

#### Proof {#br-bgk-2019-l02-lem-03-proof}

The existence of a topological space $E$ with these properties follows from Lemma 2.6. The open sets to be glued are

$$
W_{ij}:=E_i|_{U_i\cap U_j},
$$

and the existence of a continuous map to $X$ follows from Lemma 2.7. Every fibre $E_x$ has a well-defined vector space structure inherited from $E_i$ for any open neighbourhood $x\in U_i$. Independence of the choice of $i$ follows because, for $x\in U_i\cap U_j$, the hypothesis supplies an isomorphism of vector bundles

$$
\varphi_{ji}:E_i|_{U_i\cap U_j}
\longrightarrow E_j|_{U_i\cap U_j},
$$

inducing a vector space isomorphism

$$
(E_i)_x\longrightarrow(E_j)_x.
$$

> **Editorial note - order of indices in the fibre isomorphism.** Definition 2.8 specifies $\varphi_{ji}:E_i|_{U_i\cap U_j}\to E_j|_{U_i\cap U_j}$. The source prints $\varphi_{ij}$ in the sentence of the proof whose map goes from $E_i$ to $E_j$. This edition displays $\varphi_{ji}$, consistent with the domain and codomain, in the proof and preserves the source form in this note.

$\square$

> **Source illustration - `Fiddler_crab_mobius_strip.gif`.** A Möbius strip, arising by reversing the fibre on one overlap component when two local trivialisations are glued.

![Animation of a crab making one circuit of a Möbius strip and returning with reversed orientation](authority/assets/bgk-fiddler-crab-mobius-strip.gif)

### Example 2.11: the Möbius strip from gluing data {#br-bgk-2019-l02-exa-01}

On the one-dimensional sphere

$$
S^1=\left\{(x,y)\in\mathbb R^2\mid x^2+y^2=1\right\},
$$

consider the open cover

$$
S^1=U\cup V,
$$

with

$$
U=S^1\setminus\{(0,1)\},
\qquad
V=S^1\setminus\{(0,-1)\}.
$$

We shall describe gluing data for a real vector bundle of rank $1$. Both open sets are homeomorphic to the real line. Their intersection is

$$
\begin{aligned}
U\cap V
&=S^1\setminus\{(0,1),(0,-1)\}\\
&=\left\{(x,y)\in S^1\mid x\ne0\right\}.
\end{aligned}
$$

This set is not connected, but is homeomorphic to two disjoint open real half-lines (or, equivalently, two real lines). Set

$$
L=U\times\mathbb R,
\qquad
M=V\times\mathbb R.
$$

Define an isomorphism

$$
\varphi:L|_{U\cap V}\longrightarrow M|_{U\cap V}
$$

by

$$
\varphi(x,y,t):=
\begin{cases}
(x,y,t),&x>0,\\
(x,y,-t),&x<0.
\end{cases}
$$

The map $\varphi$ is continuous because the two formulae apply on disjoint open sets. On one half, the fibre is mapped identically; on the other, it is reversed. In the sense of Remark 2.9, the continuous matrix description, constant on each component,

$$
\psi(x,y):=
\begin{cases}
(1),&x>0,\\
(-1),&x<0
\end{cases}
$$

holds on $U\cap V$. Since there are only two open sets, the cocycle condition is automatically satisfied. By Lemma 2.10, these gluing data determine a real vector bundle of rank $1$ on the sphere, called the *Möbius strip*.

### Example 2.12: an algebraic realisation of the Möbius strip {#br-bgk-2019-l02-exa-02}

We give a direct algebraic realisation of the Möbius strip in $\mathbb R^4$. Consider

$$
Y:=\left\{(x,y,z,w)\in\mathbb R^4\mathrel{\Big|}
x^2+y^2=1,\ (1-y)z=xw,\ xz=(1+y)w\right\}
$$

together with its natural projection to the one-dimensional sphere

$$
S^1=\left\{(x,y)\in\mathbb R^2\mid x^2+y^2=1\right\}=U\cup V,
$$

with

$$
U=S^1\setminus\{(0,1)\},
\qquad
V=S^1\setminus\{(0,-1)\}.
$$

We claim that $Y$ is a vector bundle of rank $1$ isomorphic to the Möbius strip. On $U$, we have $y\ne1$, so the second equation can be solved for $z$:

$$
z=\frac{x}{1-y}w.
$$

The third equation is then automatically satisfied, since

$$
xz=\frac{x}{1-y}xw
=\frac{x^2}{1-y}w
=\frac{1-y^2}{1-y}w
=(1+y)w.
$$

Similarly, on $V$ we have

$$
w=\frac{x}{1+y}z,
$$

and the other equation is automatically satisfied. Thus, over $U$ and $V$, $Y$ is a trivial vector bundle of rank $1$, with fibre variables $w$ and $z$, respectively. Its transition map on $U\cap V$ is given by

$$
\frac{x}{1-y}=\frac{1+y}{x},
$$

so one matrix description of this bundle is

$$
\left(\frac{x}{1-y}\right).
$$

Unlike the constant matrix in Example 2.11, this matrix depends explicitly on $(x,y)\in U\cap V$. Nevertheless, the two bundles are isomorphic. Using Exercise 2.21, take the nowhere-zero continuous functions $\sqrt{1-y}$ on $U$ and $\sqrt{1+y}$ on $V$. We obtain

> **Editorial note - undefined variable in the source.** The source prints $\sqrt{1-t}$ on $U$ and $\sqrt{1+t}$ on $V$, but there is no variable $t$ in this example. The calculation immediately following uses $y$ and uniquely determines the intended corrections as $\sqrt{1-y}$ and $\sqrt{1+y}$. This edition displays these correctly typed expressions in the text and discloses the normalisation here.

$$
\begin{aligned}
\frac{1}{\sqrt{1+y}}\cdot
\frac{x}{1-y}\cdot\sqrt{1-y}
&=\frac{1}{\sqrt{1+y}}\cdot\frac{x}{\sqrt{1-y}}\\
&=\frac{x}{\sqrt{1-y^2}}\\
&=\frac{x}{\sqrt{x^2}}\\
&=\frac{x}{|x|}\\
&=\pm1,
\end{aligned}
$$

depending on the sign of $x$. Hence the two bundles are isomorphic.

