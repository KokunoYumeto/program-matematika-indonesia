---
title: "Lecture 26 - Čech cohomology"
stable_id: br-bgk-2019-l26
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 26"
upstream_pageid: 109030
upstream_revid: 793619
upstream_timestamp: "2022-08-25T06:24:38Z"
upstream_mediawiki_sha1: 006e9f6caaf060c5ec70ba24ce3d86023c0d7521
source_url: "https://de.wikiversity.org/w/index.php?oldid=793619"
lecture_xml: authority/wikiversity-bgk/unit-26/lecture-26.xml
lecture_xml_sha256: 2cb61aa26b63d6dc928cc69098e21f7f47edc1ffdf7330a647324ccf66f177f0
lecture_expanded_tex: authority/wikiversity-bgk/unit-26/lecture-26-expanded.tex
lecture_expanded_tex_sha256: 7ea6ff36700d0e25bc150052db32b312c4328653d54009cf10ebfc4bef713a8b
official_pdf_metadata: authority/wikiversity-bgk/unit-26/official-pdfs-api.json
official_pdf_metadata_sha256: c209d22600d20ebfe6f1479b1b6a9a0f20295711dab60905e6d35039c3ca6262
official_course_pdf: authority/artifacts/bgk-course-official.pdf
official_course_pdf_bytes: 2104862
official_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
official_course_pdf_printed_pages: "223-231"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
media_credits: source/id-ID/media-credits-bgk-unit-26.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain the recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
authority_manifest: authority/wikiversity-bgk/unit-26/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7ed3c9a3a480daeb4332e9de8ff2251e43d3a43845df5744ef16aabac5f2c6b4
authority_manifest_status: "Complete terminal authority freeze; all 29 file records have been rehashed without mismatches."
official_pdf: authority/artifacts/bgk-lecture-26-official.pdf
official_pdf_sha256: 4420d1401134f2d5871c4c5252531425c9c49bbfdcad513f6fcfe20bdcce94f5
official_pdf_source_bytes: 109882
official_pdf_source_sha1: 9e1bc7da807404defd70ceeaf558e9e63a6024aa
official_pdf_status: "Local official PDF witness; byte identity, SHA-256, upload SHA-1, and component rights notices have been verified."
asset_closure: authority/ASSET_CLOSURE-bgk-unit-26.json
asset_closure_sha256: e9c1c7cf41349d4ae9d66f2e04cb9a214e5b453f41f536832a2af4103d55c1e3
media_rights: authority/RIGHTS-bgk-unit-26.csv
media_rights_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
media_credits_sha256: 3cfc1664f010b72c0ac540cbd35b74412a434788662fdc7c0f2a4cfe49abdcba
---

# Lecture 26: Čech cohomology {#br-bgk-2019-l26}

We ask whether a finite topological space, that is, a space with only finitely many points, can have nontrivial cohomology. If the space is discrete, so that every point is both open and closed, this is impossible because every sheaf on it is flasque. Nor can there be nontrivial cohomology on the spectrum of a discrete valuation ring—or, more generally, on a local space such as the spectrum of a local ring. Nevertheless, cohomology already occurs on a three-element space, as the following example shows.

<!-- upstream_entity: Endlicher Raum/3 Punkte/Einer generisch/Generisch Z/Kohomologie/Beispiel -->

### Example 26.1: cohomology on a three-point space {#br-bgk-2019-l26-exm-01}

We consider the topological space

$$
X=\{a,b,c\}
$$

with open sets

$$
\emptyset,\quad X,\quad U=\{a,c\},\quad V=\{b,c\},\quad
U\cap V=\{c\}.
$$

This space has two closed points $a$ and $b$, is irreducible, and has $c$ as its generic point. Apart from the empty set, its open sets form the inclusion diagram

$$
\begin{matrix}
X&\longleftarrow&U\\
\uparrow&&\uparrow\\
V&\longleftarrow&U\cap V.
\end{matrix}
$$

A sheaf of commutative groups on $X$ is specified by assigning groups and restriction homomorphisms to these subsets and checking the compatibility condition. We consider the sheaf $\mathcal F$ given by

$$
\begin{matrix}
0&\longrightarrow&0\\
\downarrow&&\downarrow\\
0&\longrightarrow&\mathbb Z.
\end{matrix}
$$

This sheaf embeds in the constant sheaf $\mathcal G$ (with identity maps)

$$
\begin{matrix}
\mathbb Z&\longrightarrow&\mathbb Z\\
\downarrow&&\downarrow\\
\mathbb Z&\longrightarrow&\mathbb Z.
\end{matrix}
$$

Edition note: the source calls the constant sheaf in this sentence `\mathcal F`, but immediately afterwards uses `\mathcal G/\mathcal F` and `\Gamma(X,\mathcal G)`. This edition uses `\mathcal G` for the constant sheaf to keep the two sheaves' roles distinct.

The quotient sheaf $\mathcal G/\mathcal F$ is given by

$$
\begin{matrix}
\mathbb Z\times\mathbb Z&\xrightarrow{\ p_2\ }&\mathbb Z\\
{p_1}\downarrow&&\downarrow\\
\mathbb Z&\longrightarrow&0.
\end{matrix}
$$

The values on $U\cap V$, $U$, and $V$ are obtained directly by taking quotients; sheafification has no effect. On $X$ we obtain the product $\mathbb Z\times\mathbb Z$, since sections on $U$ and $V$ are automatically compatible. Thus the global map

$$
\Gamma(X,\mathcal G)=\mathbb Z
\longrightarrow
\Gamma(X,\mathcal G/\mathcal F)=\mathbb Z\times\mathbb Z
$$

is not surjective. The long exact cohomology sequence instead has the form

$$
0\longrightarrow 0\longrightarrow\mathbb Z
\longrightarrow\mathbb Z\times\mathbb Z
\xrightarrow{\ \delta\ }
H^1(X,\mathcal F)=\mathbb Z\longrightarrow 0.
$$

The map at the front is $n\mapsto(n,n)$, and the one at the back is $(r,s)\mapsto(r-s)$; the latter follows from exactness.

An important question in the opposite direction is whether the cohomology of a complicated topological space can be captured and computed using finite data. In many situations this is indeed possible by means of Čech cohomology, which refers to a finite open cover together with all its intersections.

<!-- upstream_entity: Invertierbare Garbe/Übergangsabbildung/Motivation für Cech-Kohomologie/2/Beispiel -->

### Example 26.2: gluing data as a Čech complex {#br-bgk-2019-l26-exm-02}

We continue Remark 20.2. Let $(X,\mathcal O_X)$ be a ringed space, and suppose we are interested in invertible sheaves on $X$, specifically those admitting trivialisations with respect to a fixed open cover

$$
X=\bigcup_{i\in I}U_i.
$$

These invertible sheaves correspond to collections of data

$$
\left(
U_i,
r_{ij}\in\Gamma(U_i\cap U_j,\mathcal O_X^\times)
\ \text{with}\
r_{kj}\,r_{ki}^{-1}\,r_{ji}=1
\ \text{in}\
\Gamma(U_i\cap U_j\cap U_k,\mathcal O_X^\times)
\right).
$$

Such a collection of data must, however, be regarded as trivial if there are elements

$$
s_i\in\Gamma(U_i,\mathcal O_X^\times)
$$

with

$$
s_i\,s_j^{-1}=r_{ij}
$$

for all $i,j$. This entire situation can be expressed by the complex

$$
\prod_{i\in I}\Gamma(U_i,\mathcal O_X^\times)
\longrightarrow
\prod_{i<j}\Gamma(U_i\cap U_j,\mathcal O_X^\times)
\longrightarrow
\prod_{i<j<k}\Gamma(U_i\cap U_j\cap U_k,\mathcal O_X^\times),
$$

after fixing a total order on $I$. The first map is given by

$$
(s_i)\longmapsto(s_j s_i^{-1})_{i<j},
$$

and the second by

$$
(r_{ij})\longmapsto(r_{jk}r_{ik}^{-1}r_{ij}).
$$

An element in the middle belongs to the kernel of the second map precisely when it satisfies the cocycle condition, and belongs to the image of the first precisely when it represents the trivial invertible sheaf.

## Čech cohomology {#br-bgk-2019-l26-s01}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$. For a subset $J\subseteq I$, we set

$$
U_J:=\bigcap_{i\in J}U_i.
$$

If $J\subseteq L\subseteq I$, then $U_L\subseteq U_J$. For a sheaf $\mathcal G$ of commutative groups on $X$, we consider the values $\mathcal G(U_J)$ for the various $J$; to $J\subseteq L$ there corresponds the restriction map

$$
\mathcal G(U_J)\longrightarrow\mathcal G(U_L).
$$

For $s\in\mathcal G(U_J)$, we use the abbreviation

$$
s|_L=s|_{U_L},
$$

and often write simply $s$. We fix a well-ordering on $I$ (the case of finite $I$ is the one mainly needed). We can now define the Čech complex and Čech cohomology, an important tool for computing sheaf cohomology.

<!-- upstream_entity: Garbe/Überdeckung/Cech-Komplex/Definition -->

### Definition 26.3: the Čech complex {#br-bgk-2019-l26-def-01}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$, and let $\mathcal G$ be a sheaf of commutative groups on $X$. For $k\in\mathbb N$, set

$$
\check C^k(\mathcal U,\mathcal G)
=
\prod_{\{J\mid \#(J)=k+1\}}\mathcal G(U_J),
$$

and define group homomorphisms

$$
\delta_k:\check C^k(\mathcal U,\mathcal G)
\longrightarrow
\check C^{k+1}(\mathcal U,\mathcal G),
\qquad
s=(s_J)_J\longmapsto
\delta_k(s)=(\delta_k(s)_L)_L,
$$

by

$$
(\delta_k(s))_L
=\sum_{\ell=0}^{k+1}(-1)^\ell
s_{L\setminus\{i_\ell\}}|_{U_L},
$$

where $L=\{i_0,i_1,\ldots,i_{k+1}\}$ is written in the order induced from $I$. The complex

$$
\check C^\bullet(\mathcal U,\mathcal G)
=
\bigl(\check C^k(\mathcal U,\mathcal G),\ k\geq 0,\ \delta_k\bigr)
$$

is called the *Čech complex* of the sheaf $\mathcal G$ with respect to this cover.

For $k=0$, we have

$$
\check C^0(\mathcal U,\mathcal G)
=\prod_{i\in I}\mathcal G(U_i),
$$

and, if $I$ is finite and nonempty, for $k=\#(I)-1$ we have

$$
\check C^k(\mathcal U,\mathcal G)
=
\mathcal G\!\left(\bigcap_{i\in I}U_i\right).
$$

Edition note: the source writes $k=\#(I)$ for the last term and $k>\#(I)$ for vanishing. The convention $\#(J)=k+1$ instead gives last degree $\#(I)-1$ and vanishing for $k\geq\#(I)$. In the differential above, the source's shorthand has also been made explicit: take the indicated component and restrict it to $U_L$.

If $I$ is finite and $k\geq\#(I)$, the index set for $\check C^k(\mathcal U,\mathcal G)$ is empty, and this term is $0$. For negative $k$, the complex is likewise defined to be $0$. For a cover consisting of two open sets $U$ and $V$, the complex is

$$
0\longrightarrow
\Gamma(U,\mathcal G)\times\Gamma(V,\mathcal G)
\longrightarrow
\Gamma(U\cap V,\mathcal G)
\longrightarrow 0.
$$

For a cover consisting of three open sets $U,V,W$, the complex is

$$
\begin{aligned}
0\longrightarrow{}&
\Gamma(U,\mathcal G)\times\Gamma(V,\mathcal G)\times
\Gamma(W,\mathcal G)\\
\longrightarrow{}&
\Gamma(V\cap W,\mathcal G)\times
\Gamma(U\cap W,\mathcal G)\times
\Gamma(U\cap V,\mathcal G)\\
\longrightarrow{}&
\Gamma(U\cap V\cap W,\mathcal G)
\longrightarrow 0.
\end{aligned}
$$

To understand the homomorphisms, it is useful even in these cases to use the numbered names $U_1,U_2,U_3$.

<!-- upstream_entity: Garbe/Überdeckung/Cech-Komplex/Ist Komplex/Fakt -->

### Lemma 26.4: the Čech complex is indeed a complex {#br-bgk-2019-l26-lem-01}

The Čech complex is indeed a complex.

#### Proof {#br-bgk-2019-l26-lem-01-proof}

Let $(s_J)_J\in\check C^k(\mathcal U,\mathcal G)$ be a tuple. For a fixed index set

$$
L=\{i_0,i_1,\ldots,i_k,i_{k+1},i_{k+2}\},
$$

we obtain

$$
\begin{aligned}
(\delta(\delta s))_L
&=\sum_{p=0}^{k+2}(-1)^p(\delta s)|_{L\setminus\{i_p\}}\\
&=\sum_{p=0}^{k+2}(-1)^p
\left(
\sum_{q=0}^{p-1}(-1)^q
s|_{(L\setminus\{i_p\})\setminus\{i_q\}}
+
\sum_{q=p+1}^{k+2}(-1)^{q+1}
s|_{(L\setminus\{i_p\})\setminus\{i_q\}}
\right)\\
&=\sum_{0\leq p<q\leq k+2}(-1)^{p+q}
\left(
s|_{L\setminus\{i_p,i_q\}}
-s|_{L\setminus\{i_p,i_q\}}
\right)\\
&=0.
\end{aligned}
$$

Note that the sign inside the parentheses depends on the position of $i_q$ in $L\setminus\{i_p\}$. Here each displayed $s|_{L\setminus\{i_p,i_q\}}$ means the component $s_{L\setminus\{i_p,i_q\}}$ restricted to $U_L$; the same convention applies to $\delta s$.

Edition note: the source ends the second inner sum at $k+1$ and indexes the final sum by an undefined $J$. Since $L$ has $k+3$ elements, the corrected bound is $k+2$, with one cancelling pair for each $0\leq p<q\leq k+2$.

<!-- upstream_entity: Garbe/Überdeckung/Cech-Kohomologie/Definition -->

### Definition 26.5: Čech cohomology {#br-bgk-2019-l26-def-02}

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover of a topological space $X$, and let $\mathcal G$ be a sheaf of commutative groups on $X$. For $k\in\mathbb N$, the *$k$th Čech cohomology*

$$
\check H^k(\mathcal U,\mathcal G)
$$

is defined to be the $k$th homology of the Čech complex $\check C^\bullet(\mathcal U,\mathcal G)$.

As with the homology of any complex, at each position we form the quotient group of the kernel modulo the image. Elements of the $k$th kernel are also called *Čech cocycles*, and elements of the $k$th image are also called *Čech coboundaries*. The element of the $k$th Čech cohomology associated with a Čech cocycle is also called a *Čech cohomology class*. The zeroth Čech cohomology group is simply $\mathcal G(X)$, as follows directly from the sheaf property; see Exercise 26.2.

<!-- upstream_entity: Kreis/Überdeckung/Möbiuszykel/Komplexe stetige Trivialisierung/Beispiel -->

### Example 26.6: cocycles on the circle {#br-bgk-2019-l26-exm-03}

On the circle, we consider the cover by two open circular arcs, each homeomorphic to a real interval,

$$
S^1=U\cup V,
$$

whose intersection

$$
U\cap V=S\cup T
$$

is a union of two intervals. We consider several sheaves of commutative groups, written multiplicatively. Let $h$ be the function on $U\cap V$ with constant value $1$ on $S$ and value $-1$ on $T$. This is a nontrivial Čech cocycle for the sheaf of locally constant functions with values in the group of units $K^\times$ of a field $K$ of characteristic different from $2$. The same holds for the sheaf of continuous functions with values in $\mathbb K^\times$, where $\mathbb K=\mathbb R$ or $\mathbb C$.

This cocycle defines a trivial Čech cohomology class in

$$
\check H^1(\{U,V\},\mathcal G)
$$

if and only if there are functions—locally constant or continuous, as appropriate—

$$
f:U\longrightarrow K^\times,
\qquad
g:V\longrightarrow K^\times
$$

with $h=fg^{-1}$. In the locally constant case this is impossible, because locally constant functions on the connected arcs $U$ and $V$ are constant; consequently $fg^{-1}$ is also constant and hence differs from $h$. It is likewise impossible for the sheaf of nowhere-zero continuous real-valued functions. In this case, $f$ and $g$ have constant signs, so the sign of $fg^{-1}$ agrees with that of $h$ on exactly one interval of the intersection. The corresponding nontrivial first Čech cohomology class,

$$
[h]\in\check H^1(\{U,V\},C^0(-,\mathbb R^\times)),
$$

represents the Möbius strip over the unit circle.

In the complex case, by contrast, $h$ can be written as the quotient of two nowhere-zero continuous complex-valued functions. We can take $g=1$ and choose $f$ to have constant value $1$ on $S$, constant value $-1$ on $T$, and, in between—that is, on $U\setminus(S\cup T)$—to take values continuously along the complex unit circle.

Edition note: the source omits the exclusion of characteristic $2$, where $h=1$ is trivial, and reverses “trivial” and “nontrivial” in the coboundary criterion. Both points are corrected above. In the real case it is the signs, not necessarily the function values, that agree on exactly one component. The source's set-difference braces have been replaced by parentheses.

<!-- upstream_entity: Quasiaffines Schema/Modul/Cech-Komplex/Beispiel -->

### Example 26.7: the Čech complex for a module on a quasi-affine scheme {#br-bgk-2019-l26-exm-04}

For a commutative ring $R$ and elements $f_1,\ldots,f_n\in R$ generating an ideal $\mathfrak a$, there is an open cover

$$
D(\mathfrak a)=\bigcup_{i=1}^nD(f_i)
$$

of the quasi-affine scheme $D(\mathfrak a)\subseteq\operatorname{Spek}(R)$. For an $R$-module $M$, the Čech complex of the module sheaf $\widetilde M$ on $D(\mathfrak a)$ can be written down directly, without considering the sheafification process. By Lemma 14.5, on the relevant open sets we have

$$
\Gamma\!\left(
D\!\left(\prod_{i\in J}f_i\right),\widetilde M
\right)
=M_{\prod_{i\in J}f_i}.
$$

The Čech complex is therefore

$$
0\longrightarrow
\prod_{1\leq i\leq n}M_{f_i}
\longrightarrow
\prod_{1\leq i<j\leq n}M_{f_if_j}
\longrightarrow
\prod_{1\leq i<j<k\leq n}M_{f_if_jf_k}
\longrightarrow\cdots.
$$

Computing the homology of this complex is generally still difficult, but it is now purely a problem in commutative algebra.

## Čech cohomology and sheaf cohomology {#br-bgk-2019-l26-s02}

We now discuss situations in which Čech cohomology for certain covers agrees with the “actual” sheaf cohomology, defined using injective resolutions.

<!-- upstream_entity: Cech-Kohomologie/Abgeleitete Kohomologie/Endliche azyklische Überdeckung/Übereinstimmung/Fakt -->

### Lemma 26.8: first Čech cohomology and sheaf cohomology {#br-bgk-2019-l26-lem-02}

Let $\mathcal F$ be a sheaf of commutative groups on a topological space $X$, and let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover with

$$
H^1(U_i,\mathcal F)=0
\qquad\text{and}\qquad
H^1(U_i\cap U_j,\mathcal F)=0
$$

for all $i,j$. Then

$$
\check H^1(U_i,\mathcal F)=H^1(X,\mathcal F).
$$

#### Proof {#br-bgk-2019-l26-lem-02-proof}

Let $\mathcal F\subseteq\mathcal I$ be an embedding in an injective sheaf, and let

$$
0\longrightarrow\mathcal F\longrightarrow\mathcal I
\longrightarrow\mathcal H\longrightarrow 0
$$

be the associated short exact sequence. By the long exact cohomology sequence—see Corollary 25.2 (3)—and Theorem 24.8, we have

$$
H^1(X,\mathcal F)
=
\Gamma(X,\mathcal H)
/
\operatorname{bild}\bigl(
\Gamma(X,\mathcal I)\longrightarrow\Gamma(X,\mathcal H)
\bigr).
$$

We first define a homomorphism

$$
\Gamma(X,\mathcal H)
\longrightarrow
\check H^1(U_i,\mathcal F).
$$

A section $t\in\Gamma(X,\mathcal H)$ determines restrictions $t_i=t|_{U_i}$. Since $H^1(U_i,\mathcal F)=0$, there are

$$
s_i\in\Gamma(U_i,\mathcal I)
$$

mapping to $t_i$. For $i<j$, the elements

$$
r_{ij}:=s_i-s_j
$$

map to $0$ in $\Gamma(U_i\cap U_j,\mathcal H)$, so

$$
r_{ij}\in\Gamma(U_i\cap U_j,\mathcal F).
$$

For indices $i<j<k$, we have

$$
r_{ij}-r_{ik}+r_{jk}
=s_i-s_j-(s_i-s_k)+s_j-s_k=0.
$$

Thus the cocycle condition holds. The family $(r_{ij})_{i<j}$ is a Čech cocycle and defines an element of $\check H^1(U_i,\mathcal F)$. This assignment is independent of the choice of $s_i$ and is a group homomorphism; see Exercise 26.5.

Now let $t\in\Gamma(X,\mathcal H)$ be the image of a global element $s\in\Gamma(X,\mathcal I)$. We can take $s_i=s|_{U_i}$, so all the $r_{ij}$ constructed from $t$ are $0$. Such an element therefore maps to $0$. By Theorem 47.4 (Linear Algebra (Osnabrück 2024-2025)), we obtain a factorisation

$$
H^1(X,\mathcal F)
=
\Gamma(X,\mathcal H)
/
\operatorname{bild}\bigl(
\Gamma(X,\mathcal I)\longrightarrow\Gamma(X,\mathcal H)
\bigr)
\longrightarrow
\check H^1(U_i,\mathcal F).
$$

Conversely, suppose we are given a first Čech cocycle of $\mathcal F$, represented by

$$
(r_{ij})_{i<j}\in\prod_{i<j}\Gamma(U_i\cap U_j,\mathcal F)
$$

with $r_{ij}-r_{ik}+r_{jk}=0$ on triple intersections.

Edition note: the source extends each $r_{ij}$ to a global section of the flasque sheaf $\mathcal I$ and sets $s_i=r_{i1}$. Arbitrary extensions need not preserve the cocycle relations outside the original intersections. The following compatible construction repairs that step. The preceding quotient also corrects the source's target $\Gamma(X,\mathcal I)$ to $\Gamma(X,\mathcal H)$, and the tuple's ambient group is written as a product.

Set $r_{ji}=-r_{ij}$ and $r_{ii}=0$. Using the fixed well-ordering of $I$, construct $s_i\in\Gamma(U_i,\mathcal I)$ successively, with $s_i-s_j=r_{ij}$ on overlaps. At stage $i$, the sections $s_j+r_{ij}$ on $U_i\cap U_j$, for $j<i$, agree on their overlaps by the cocycle relation. They therefore glue on $U_i\cap\bigcup_{j<i}U_j$. Flasqueness extends this section to $U_i$; call the extension $s_i$. At the first stage take $s_i=0$. This construction, including limit stages, gives

$
s_i-s_j=r_{ij}\quad\text{on }U_i\cap U_j.
$

The elements $s_i$ determine elements

$$
t_i\in\Gamma(U_i,\mathcal H).
$$

Since their differences come from $\mathcal F$, these are compatible and determine a global element

$$
t\in\Gamma(X,\mathcal H).
$$

Via the connecting homomorphism $\delta$, this determines a cohomology class

$$
\delta(t)\in H^1(X,\mathcal F).
$$

If the Čech cocycle $r_{ij}$ is represented by other elements $s_i'\in\Gamma(U_i,\mathcal I)$, then the elements $s_i-s_i'$, $i\in I$, are compatible because

$$
(s_i-s_i')-(s_j-s_j')
=s_i-s_j-(s_i'-s_j')
=r_{ij}-r_{ij}=0,
$$

and determine a global element of $\Gamma(X,\mathcal I)$. Hence the difference between the two representations maps to $0$ in $H^1(X,\mathcal F)$. Altogether we obtain a well-defined map

$$
\check Z^1(U_i,\mathcal F)
\longrightarrow
H^1(X,\mathcal F)
=
\Gamma(X,\mathcal H)
/
\operatorname{bild}\bigl(
\Gamma(X,\mathcal I)\longrightarrow\Gamma(X,\mathcal H)
\bigr).
$$

Now suppose the Čech cocycle determines the zero class in first Čech cohomology. By definition, there are elements

$$
r_i\in\Gamma(U_i,\mathcal F)
$$

with

$$
r_i-r_j=r_{ij}.
$$

Regard these as local sections of $\mathcal I$ on $U_i$; the $r_i$ can directly play the role of the $s_i$ above. (Edition note: no global extensions are needed here, or for the alternative representatives $s_i'$.) Then all $t_i$ are $0$, so their image in $H^1(X,\mathcal F)$ is also $0$. Thus there is a map

$$
\check H^1(U_i,\mathcal F)
\longrightarrow
H^1(X,\mathcal F).
$$

This is a group homomorphism and is inverse to the map constructed previously.

<!-- upstream_entity: Cech-Kohomologie/Abgeleitete Kohomologie/Endliche azyklische Überdeckung/Verbindender Homomorphismus/Übereinstimmung/Fakt -->

### Lemma 26.9: comparison using an acyclic resolution {#br-bgk-2019-l26-lem-03}

Let $\mathcal F=\mathcal F_0$ be a sheaf of commutative groups on a topological space $X$, and suppose an acyclic resolution $\mathcal Z^\bullet$ of $\mathcal F$ is given, with associated short exact sequences

$$
0\longrightarrow\mathcal F_n
\longrightarrow\mathcal Z_n
\longrightarrow\mathcal F_{n+1}
\longrightarrow 0.
$$

Let

$$
X=\bigcup_{i\in I}U_i
$$

be an open cover with

$$
H^k\!\left(\bigcap_{i\in J}U_i,\mathcal F_n\right)=0
$$

for all nonempty subsets $J\subseteq I$, all $n\in\mathbb N$, and all $k\in\mathbb N_+$. Then

$$
\check H^k(U_i,\mathcal F)=H^k(X,\mathcal F).
$$

#### Proof {#br-bgk-2019-l26-lem-03-proof}

We use induction on $k$, simultaneously for all $n$. The case $k=1$ was treated in Lemma 26.8, and the following argument follows that lemma. We consider the short exact sequence

$$
0\longrightarrow\mathcal F
\longrightarrow\mathcal Z_0
\longrightarrow\mathcal F_1=\mathcal H
\longrightarrow 0
$$

together with the isomorphisms

$$
H^k(X,\mathcal F)
=H^{k-1}(X,\mathcal H)
=\check H^{k-1}(U_i,\mathcal H).
$$

The left-hand isomorphism comes from the connecting homomorphism and the acyclicity of $\mathcal Z_0$, and the right-hand one from the induction hypothesis applied to $\mathcal H$. It therefore remains to show that there is an isomorphism

$$
\check H^{k-1}(U_i,\mathcal H)
=\check H^k(U_i,\mathcal F).
$$

A class on the left is represented by a tuple

$$
(t_J)\in
\prod_{\#(J)=k}\Gamma(U_J,\mathcal H)
$$

subject to the condition

$$
\sum_{\ell=0}^{k}(-1)^\ell
t_{L\setminus\{i_\ell\}}=0
$$

for all $(k+1)$-element subsets $L\subseteq I$. Since the cover is acyclic for $\mathcal F$, there is a tuple

$$
(s_J)\in
\prod_{\#(J)=k}\Gamma(U_J,\mathcal Z_0)
$$

mapping to $(t_J)$. This in turn determines a tuple of differences $(r_L)$, where $L$ ranges over the $(k+1)$-element subsets of $I$, by

$$
r_L:=\sum_{\ell=0}^{k}(-1)^\ell
s_{L\setminus\{i_\ell\}}.
$$

Since $s_J$ maps to $t_J$, the condition above implies that all $r_L$ map to $0$. Thus

$$
(r_L)_L\in
\prod_{\#(L)=k+1}\Gamma(U_L,\mathcal F).
$$

Further considerations show that this tuple is a cocycle, that the map is well-defined, and that it is a bijective group homomorphism.

Edition note: the induction step is for $k>1$; degree $0$ is the sheaf axiom. In the source's two sums over a $(k+1)$-element set, $k+1$ has been corrected to $k$, the first exponent $i$ to $\ell$, and the lifting product's $\#(J)=n,\mathcal Z$ to $\#(J)=k,\mathcal Z_0$. Restrictions to $U_L$ are understood. To justify the abbreviated bijectivity step without an extra assumption on the chosen acyclic resolution, one may compute with an injective resolution instead. Its terms are flasque and have exact augmented Čech complexes. The successive cokernels are acyclic on every finite nonempty cover intersection, by the long exact sequence and the assumed acyclicity of $\mathcal F$. The resulting degreewise exact short sequences of Čech complexes give the asserted connecting isomorphism. This also supplies the induction argument for the stated comparison.

<!-- upstream_entity: Projektives Schema/Quasikohärente Garbe/Azyklische Überdeckung/Cech-Kohomologie/Fakt -->

### Theorem 26.10: cohomology on projective schemes {#br-bgk-2019-l26-thm-01}

Let $(X,\mathcal O_X)$ be a projective scheme over a commutative ring $R$, and let $\mathcal F$ be a quasi-coherent module on $X$. Then the sheaf cohomology of $\mathcal F$ agrees with Čech cohomology for the affine cover by the sets $D_+(X_i)$.

#### Proof {#br-bgk-2019-l26-thm-01-proof}

Let $X_0,X_1,\ldots,X_n$ be the variables of the homogeneous coordinate ring of the projective scheme $X$, so that

$$
X=\operatorname{Proj}(R[X_0,X_1,\ldots,X_n]/\mathfrak a).
$$

All intersections

$$
\bigcap_{i\in J}D_+(X_i)
=D_+\!\left(\prod_{i\in J}X_i\right)
$$

are affine by Lemma 12.9. For $\mathcal F$, there is a flasque quasi-coherent sheaf $\mathcal Z$ with a short exact sequence

$$
0\longrightarrow\mathcal F
\longrightarrow\mathcal Z
\longrightarrow\mathcal H
\longrightarrow 0.
$$

By Exercise 14.21, the quotient sheaf is again quasi-coherent. By Theorem 25.11, quasi-coherent sheaves on affine schemes have no cohomology. We can therefore apply Lemma 26.9.

Edition note: for the arbitrary base ring stated here, the comparison need not rely on the source's unproved existence of a flasque quasi-coherent embedding. Take an injective resolution in sheaves of abelian groups. Its terms are flasque, and its successive cokernels are acyclic on every finite nonempty affine intersection by Theorem 25.11 and the long exact cohomology sequence. Lemma 26.9 then applies, without requiring the injective terms or the cokernels to be quasi-coherent.

The same assertion holds for quasi-affine schemes. The decisive property is that intersections of affine subsets are again affine. This often holds, but not for every scheme.
