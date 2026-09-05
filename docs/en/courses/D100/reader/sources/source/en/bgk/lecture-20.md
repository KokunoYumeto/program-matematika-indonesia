---
title: "Lecture 20 - The Picard Group"
stable_id: br-bgk-2019-l20
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 20"
upstream_pageid: 109024
upstream_revid: 1070035
upstream_timestamp: "2026-02-06T08:44:37Z"
upstream_mediawiki_sha1: 69eee548900d7b7e00c3b3bd10e297a700800a89
source_url: "https://de.wikiversity.org/w/index.php?oldid=1070035"
authority_manifest: authority/wikiversity-bgk/unit-20/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a59a4536a441cfdbcd579525119112156fcc5dc8041ba97d4834e18db55cd658
authority_manifest_status: "Complete terminal authority freeze; all 32 file records have been recomputed without mismatches."
lecture_xml: authority/wikiversity-bgk/unit-20/lecture-20.xml
lecture_xml_sha256: 89f2acd9ed5baf48e76b4bedda9767e45546a9b9e725417401879012b277593b
lecture_expanded_tex: authority/wikiversity-bgk/unit-20/lecture-20-expanded.tex
lecture_expanded_tex_sha256: d6da653cd6ac86d23ed59507119788b38091b953ef26202512d3ce668c587e82
official_pdf: authority/artifacts/bgk-lecture-20-official.pdf
official_pdf_sha256: fae4d603a9f8f19f106c0e4e0c5960076c112796ec0d14dfb7f1e9e0c8c01cd9
official_pdf_status: "Local official PDF witness; 96,088 bytes, 7 pages, and upload SHA-1 21addd9a85777481565a4bb28602c5f64fb9d966 have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-20/official-pdfs-api.json
official_pdf_source_bytes: 96088
official_pdf_source_sha1: 21addd9a85777481565a4bb28602c5f64fb9d966
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
media_credits: source/id-ID/media-credits-bgk-unit-20.md
rights_ledger: authority/RIGHTS-bgk-unit-20.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-20.json
asset_closure_sha256: 2cdfc5e32e86b5f704f1f00f6d5690166967464fbe2c6474086e28e470463b40
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 20: The Picard Group {#br-bgk-2019-l20}

## The Picard group {#br-bgk-2019-l20-s01}

<!-- upstream_entity: Beringter Raum/Picardgruppe/Definition -->

### Definition 20.1: the Picard group {#br-bgk-2019-l20-def-01}

For a ringed space $(X,\mathcal O_X)$, the set of isomorphism classes of invertible sheaves on $X$, with tensor product as the operation, the dual sheaf as inverse, and the structure sheaf as identity, is called the *Picard group* of $X$. It is denoted by

$$
\operatorname{Pic}(X).
$$

The following discussion of the gluing data of an invertible sheaf connects with Exercise 2.19 on the one hand and anticipates Čech cohomology on the other.

<!-- upstream_entity: Invertierbare Garbe/Übergangsabbildung/Datensatz/Bemerkung -->

### Remark 20.2: transition data as a cocycle {#br-bgk-2019-l20-rem-01}

Let $(X,\mathcal O_X)$ be a ringed space and let $\mathcal L$ be an invertible sheaf on $X$. This means that there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

and trivialisations

$$
\varphi_i:\mathcal L|_{U_i}
\longrightarrow\mathcal O_X|_{U_i}.
$$

For two open sets $U_i,U_j$, the transition maps on $U_i\cap U_j$ are

$$
\varphi_i|_{U_i\cap U_j}
\circ
\varphi_j^{-1}|_{U_i\cap U_j}
:
\mathcal O_X|_{U_i\cap U_j}
\longrightarrow
\mathcal O_X|_{U_i\cap U_j}.
$$

These isomorphisms are given, compare Exercise 13.8, by multiplication by units

$$
r_{ij}\in\Gamma(U_i\cap U_j,\mathcal O_X^\times).
$$

Since these data come from a single invertible sheaf $\mathcal L$, the cocycle condition holds:

$$
r_{kj}r_{ji}=r_{ki},
$$

which can also be written as

$$
r_{kj}r_{ki}^{-1}r_{ji}=1.
$$

Conversely, such a collection of data determines an invertible sheaf by gluing.

If the invertible sheaf is trivial, there is a global $\mathcal O_X$-module isomorphism

$$
\psi:\mathcal O_X\longrightarrow\mathcal L.
$$

On $U_i$ we have the isomorphisms

$$
\mathcal O_X|_{U_i}
\xrightarrow{\ \psi|_{U_i}\ }
\mathcal L|_{U_i}
\xrightarrow{\ \varphi_i\ }
\mathcal O_X|_{U_i},
$$

which are entirely determined by units

$$
s_i\in\Gamma(U_i,\mathcal O_X^\times).
$$

These units satisfy

$$
s_i s_j^{-1}
=(\varphi_i\circ\psi)\circ(\varphi_j\circ\psi)^{-1}
=r_{ij}
$$

for all $i,j$. Conversely, if units $s_i$ realising this relation are given, then

$$
\psi|_{U_i}:=\varphi_i^{-1}\circ s_i
$$

defines compatible module isomorphisms on $U_i$, which therefore glue to a global isomorphism between $\mathcal O_X$ and $\mathcal L$.

Thus an invertible sheaf can be identified with a collection of data $(U_i,r_{ij})$ satisfying the conditions above, called a *cocycle*; such data are regarded as trivial if there are units $s_i$ with

$$
r_{ij}=s_i s_j^{-1}.
$$

<!-- upstream_entity: Invertierbare Garbe/Übergangsabbildung/Datensatz/Vorzeichenproblem/Bemerkung -->

### Remark 20.3: the sign issue in the cocycle description {#br-bgk-2019-l20-rem-02}

The identification in Remark 20.2 between invertible sheaves and cocycles in the sheaf of units is not canonical, owing to a sign issue. It depends on whether the local trivialisations of the invertible sheaf with the structure sheaf are taken in the direction

$$
\varphi_i:\mathcal L|_{U_i}\longrightarrow\mathcal O_X|_{U_i}
$$

or in the opposite direction, and on how the index set is ordered.

<!-- upstream_entity: Invertierbare Garbe/Übergangsabbildung/Datensatz/Multiplikation/Bemerkung -->

### Remark 20.4: tensor products of transition data {#br-bgk-2019-l20-rem-03}

Tensoring invertible sheaves $\mathcal L$ and $\mathcal L'$ can be carried out at the level of the data in Remark 20.2. Pass to a common refinement of the covers, so that both sheaves have trivialisations with respect to one cover $U_i$, $i\in I$. The data

$$
r_{ij}\cdot r'_{ij}
$$

then describe the tensor product.

> **Editorial note — the second transition datum.** The source prints $r_{i'j}$ in this formula. The transition datum of the second invertible sheaf must instead be $r'_{ij}$: the cover indices remain $i,j$, while the prime distinguishes the second sheaf. This edition uses that notation explicitly.

From now on, we restrict our attention to schemes.

<!-- upstream_entity: Lokaler Ring/Picardgruppe/Trivial/Fakt -->

### Lemma 20.5: the Picard group of a local ring {#br-bgk-2019-l20-lem-01}

For a local ring $R$, the Picard group of $\operatorname{Spek}(R)$ is trivial.

#### Proof {#br-bgk-2019-l20-lem-01-proof}

This is trivial.

<!-- upstream_entity: Integres Schema/Invertierbar/Einbettung in Funktionenkörper/Fakt -->

### Lemma 20.6: embedding in the function field sheaf {#br-bgk-2019-l20-lem-02}

Let $(X,\mathcal O_X)$ be an integral scheme. Every invertible sheaf on $X$ is isomorphic to an $\mathcal O_X$-submodule of the constant function field sheaf.

#### Proof {#br-bgk-2019-l20-lem-02-proof}

Let $K$ be the function field of $X$ and let $\mathcal K$ be the associated sheaf. For an invertible sheaf $\mathcal L$, the stalk at the generic point $\eta$ is a one-dimensional vector space over $K$. Fix a $K$-isomorphism

$$
\mathcal L_\eta=\mathcal K_\eta=K.
$$

For every open set $U\subseteq X$, there is a natural map

$$
\Gamma(U,\mathcal L)
\longrightarrow\mathcal L_\eta
\longrightarrow K.
$$

These maps are injective, compare the proof of Lemma 11.16, and define a submodule of $\mathcal K$.

<!-- upstream_entity: Integres Schema/Invertierbarer Untermodul/Beschreibung/Bemerkung -->

### Remark 20.7: describing invertible submodules {#br-bgk-2019-l20-rem-04}

An invertible submodule $\mathcal L$ of the constant function field sheaf is given by an open cover $U_i$, $i\in I$, of $X$, together with nonzero elements $q_i\in Q(X)$ satisfying

$$
\frac{q_i}{q_j}
\in\left(\Gamma(U_i\cap U_j,\mathcal O_X)\right)^\times.
$$

Using a trivialising cover $U_i$, we have

$$
\mathcal L|_{U_i}\cong q_i\mathcal O_{U_i},
$$

and the transition maps on intersections imply that the quotient $q_i/q_j$ must be a unit. Conversely, if such data $(U_i,q_i)$ are given, then

$$
q_i\mathcal O_{U_i}\subseteq\mathcal Q_{U_i}
$$

is a trivial subsheaf that determines an invertible subsheaf on $X$.

Another perspective is provided by the exact sequence of sheaves

$$
0\longrightarrow\mathcal O_X^\times
\longrightarrow\mathcal Q^\times
\longrightarrow\mathcal Q^\times/\mathcal O_X^\times
\longrightarrow0.
$$

By Lemma 5.9, the data described above are the global sections of the quotient sheaf $\mathcal Q^\times/\mathcal O_X^\times$.

> **Editorial note — the function-field symbol.** The source writes $q_i\in Q$ after denoting the function field by $K$ in the preceding proof. This edition uses the unambiguous notation $Q(X)$, consistent with the function-field sheaf $\mathcal Q$.

<!-- upstream_entity: Integres affines Schema/Invertierbar/Ideal/Fakt -->

### Lemma 20.8: realisation as an ideal sheaf {#br-bgk-2019-l20-lem-03}

Let $R$ be an integral domain. Every invertible sheaf on

$$
X=\operatorname{Spek}(R)
$$

is isomorphic to an ideal sheaf.

#### Proof {#br-bgk-2019-l20-lem-03-proof}

By Lemma 20.6, we may assume at once that we have an invertible submodule

$$
L\subseteq K
$$

of the field of fractions $K=Q(R)$. By Theorem 16.2, invertibility means that there is a family

$$
f_1,\ldots,f_k\in R
$$

such that

$$
L_{f_i}\cong R_{f_i}\cdot q_i
$$

with $q_i\in K\setminus\{0\}$. Let $b$ be a common denominator for all the $q_i$. The multiplication map

$$
K\longrightarrow K,
\qquad q\longmapsto qb,
$$

which is an $R$-module isomorphism of $K$, sends the submodule $L$ to an isomorphic submodule $L'$. On the given cover, $L'$ is a submodule of the structure sheaf, and hence an ideal.

In general, there are many ways to realise an invertible sheaf as a subsheaf of the function field sheaf. Indeed, a new realisation is obtained from a given one simply by multiplying by an element $f\in K$.

<!-- upstream_entity: Projektiver Raum/Getwistete Strukturgarben/Untergarbe/Funktionenkörper/Beispiel -->

### Example 20.9: twisted structure sheaves inside the function field sheaf {#br-bgk-2019-l20-exm-01}

On projective space $\mathbb P_K^d$ over a field $K$, a twisted structure sheaf $\mathcal O_{\mathbb P_K^d}(\ell)$ can be embedded in the function field sheaf $\mathcal Q$ as follows. Let

$$
G\in K(X_0,\ldots,X_d)_{-\ell}
$$

be a homogeneous element of degree $-\ell$. On every open set $U\subseteq\mathbb P_K^d$, the natural map

$$
\Gamma\!\left(U,\mathcal O_{\mathbb P_K^d}(\ell)\right)
\longrightarrow Q(\mathbb P_K^d),
\qquad s\longmapsto sG,
$$

is a realisation as a submodule.

> **Editorial note — the space and variable indices.** The source names the space $\mathbb P_K^d$ but writes the rational function field with variables $X_0,\ldots,X_n$. This edition uses $X_0,\ldots,X_d$ to match the stated projective space.

<!-- upstream_entity: Integres Schema/Invertierbare Untergarben/Tensorierung und Produkt/Fakt -->

### Lemma 20.10: tensor products and products of subsheaves {#br-bgk-2019-l20-lem-04}

Let $X$ be an integral scheme and let

$$
\mathcal L,\mathcal M\subseteq\mathcal Q
$$

be invertible subsheaves of the constant sheaf $\mathcal Q$ associated with the function field $Q(X)$. Then

$$
\mathcal L\otimes\mathcal M\cong\mathcal L\cdot\mathcal M,
$$

where $\mathcal L\cdot\mathcal M$ denotes the subsheaf of $\mathcal Q$ whose stalk at each point $P\in X$ is generated by all products $fg$ with $f\in\mathcal L_P$ and $g\in\mathcal M_P$.

#### Proof {#br-bgk-2019-l20-lem-04-proof}

For the field of fractions $Q$ of an integral domain $R$, natural multiplication gives

$$
Q\otimes_RQ=Q.
$$

Hence on an integral scheme there is an isomorphism

$$
\mathcal Q\otimes_{\mathcal O_X}\mathcal Q\cong\mathcal Q.
$$

Thus there is a natural homomorphism

$$
\mathcal L\otimes_{\mathcal O_X}\mathcal M
\longrightarrow\mathcal Q
$$

given by multiplication. Since $\mathcal L$ and $\mathcal M$ are invertible, this map is locally, and hence globally, an isomorphism onto its image sheaf.

## The Picard group in the factorial case {#br-bgk-2019-l20-s02}

<!-- upstream_entity: Faktorieller Integritätsbereich/Exponent/Lokalisierung/Fakt -->

### Lemma 20.11: reading prime exponents after localisation {#br-bgk-2019-l20-lem-05}

Let $R$ be a unique factorisation domain. The following statements hold.

1. For $f\in R$, $f\ne0$, we have

   $$
   (f)R_{(p)}=(p^s)
   $$

   if and only if $p$ occurs with exponent $s$ in the prime factorisation of $f$.

2. Two principal ideals $(f)$ and $(g)$ agree if and only if, for every prime element $p$, the ideals

   $$
   (f)R_{(p)}
   \quad\text{and}\quad
   (g)R_{(p)}
   $$

   agree in the localisation $R_{(p)}$.

#### Proof {#br-bgk-2019-l20-lem-05-proof}

See Exercise 20.4.

<!-- upstream_entity: Integres affines Schema/Faktoriell/Picardgruppe/Fakt -->

### Theorem 20.12: the Picard group of a unique factorisation domain {#br-bgk-2019-l20-thm-01}

The Picard group of a unique factorisation domain is trivial.

#### Proof {#br-bgk-2019-l20-thm-01-proof}

Let $I\subseteq R$ be an invertible ideal, and let

$$
X=\bigcup_{i=1}^nD(f_i)
$$

be an open cover such that $IR_{f_i}$ is a principal ideal. In particular, for every prime element $p$, the ideal

$$
I_{(p)}\subseteq R_{(p)}
$$

is principal and hence has the form $(p^{s_p})$, since $R_{(p)}$ is a discrete valuation ring. Only finitely many of the $s_p$ are nonzero. Indeed, an element $g\in I$, $g\ne0$, has only finitely many prime divisors, while for every other prime element $q$, the element $g$ is a unit in $R_{(q)}$.

> **Editorial note — element versus ideal.** The source says that the ideal $I_{(p)}$ has the form $p^{s_p}$. Parentheses are supplied here because the object is the principal ideal $(p^{s_p})$, not the element $p^{s_p}$.

We claim that $I$ equals the principal ideal generated by

$$
h=\prod_pp^{s_p}.
$$

Since equality of ideals can be tested locally on a cover, we may argue in $R_{f_i}$. The assertion then follows from Lemma 20.11.

<!-- upstream_entity: Integres affines Schema/Noethersch/Faktoriell/Offene Teilmenge/Picardgruppe/Fakt -->

### Lemma 20.13: the Picard group of an open set in the factorial case {#br-bgk-2019-l20-lem-06}

Let $R$ be a Noetherian unique factorisation domain and let $U\subseteq\operatorname{Spek}(R)$ be an open subset. Then the Picard group of $U$ is trivial.

#### Proof {#br-bgk-2019-l20-lem-06-proof}

Write

$$
U=D(f_1,\ldots,f_n).
$$

We proceed by induction on $n$; the base case follows from Theorem 20.12. Thus we may assume that $\mathcal L$ is trivial on

$$
D(f_1,\ldots,f_{n-1}).
$$

By Remark 20.2, the invertible sheaf is determined by a unit over

$$
D(f_1,\ldots,f_{n-1})\cap D(f_n).
$$

By Theorem 9.8, in the factorial case the structure sheaf, and hence also the sheaf of units, is particularly simple: an element $h\in R$ is a unit on $U$ exactly when

$$
U\subseteq D(h).
$$

More generally, after viewing sections inside $Q(R)^\times$, units on open sets have the form

$$
h=u p_1^{r_1}\cdots p_s^{r_s},
$$

where the $p_j\in R$ are prime elements, $u$ is a unit in $R$, and $r_j\in\mathbb Z$. The element $h$ is a unit on

$$
D(f_1,\ldots,f_{n-1})\cap D(f_n)
=D(f_1f_n,\ldots,f_{n-1}f_n)
$$

exactly when the $p_j$ that occur, namely those with exponent $r_j\ne0$, divide the $f_if_n$. This means that $p_j$ divides $f_n$ or divides all the elements $f_1,\ldots,f_{n-1}$. In either case, $h$ can be written as a product of a unit on $D(f_1,\ldots,f_{n-1})$ and a unit on $D(f_n)$. These units can be used to trivialise the sheaf.

> **Editorial note — the ambient group of units.** The source first declares $h\in R$ and then allows negative prime exponents. Such expressions belong in the fraction field. This edition explicitly views the units as elements of $Q(R)^\times$; the factorisation argument is otherwise unchanged.

<!-- upstream_entity: Integres Schema/Noethersch/Offene Teilmenge/Lokal faktoriell/Picardgruppe/Fortsetzung/Fakt -->

### Corollary 20.14: extending invertible sheaves {#br-bgk-2019-l20-cor-01}

Let $(X,\mathcal O_X)$ be a Noetherian integral scheme and let $U\subseteq X$ be an open subset. Suppose that for every point $P\in X\setminus U$, the local ring $\mathcal O_{X,P}$ is factorial. Then every invertible sheaf $\mathcal L$ on $U$ extends to an invertible sheaf on $X$.

#### Proof {#br-bgk-2019-l20-cor-01-proof}

If $U$ is empty, the structure sheaf on $X$ is an extension, so assume that $U$ is nonempty. Let $\mathcal L$ be an invertible sheaf on $U$ and let $P\in X\setminus U$. Choose an affine open neighbourhood

$$
W=\operatorname{Spek}(R)
$$

of $P$, where $P$ corresponds to the prime ideal $\mathfrak p$. By hypothesis, $R_{\mathfrak p}$ is factorial. Consider the injective scheme morphisms

$$
\operatorname{Spek}(R_{\mathfrak p})
\longrightarrow W\longrightarrow X.
$$

The open set $U$ has nonempty intersection with $W$ and with $\operatorname{Spek}(R_{\mathfrak p})$; write the latter intersection as

$$
V\subseteq\operatorname{Spek}(R_{\mathfrak p}),
$$

since the generic point of $X$ corresponds to the zero ideal of $R_{\mathfrak p}$. The pullback of $\mathcal L$ to $V$ is trivial by Lemma 20.13. Choose a trivialisation there. Since invertible sheaves and their isomorphisms are finitely presented data, after shrinking around $P$ this trivialisation descends from the localisation to an isomorphism over the overlap with an open neighbourhood

$$
P\in D(f)=W'\subseteq W.
$$

Thus $\mathcal L$ on $U$ can be glued to the trivial invertible sheaf on $W'$ along $U\cap W'$, giving an extension to $U\cup W'$. We can therefore successively replace the open set by a strictly larger open set on which an extension exists. By Noetherianity, this process ends at the whole space.

> **Editorial note — descent and the set operation in the source proof.** The source introduces modules over $R_{\mathfrak p}$ and $R$ without supplying the required descent comparison, then says that an extension has been found on $U\cap W'$ and immediately enlarges the open set. The edition makes the finite-presentation descent and gluing step explicit and uses the required union $U\cup W'$; the overlap on which the sheaves are identified remains $U\cap W'$.

Under the hypotheses above, the natural restriction homomorphism

$$
\operatorname{Pic}(X)\longrightarrow\operatorname{Pic}(U)
$$

is therefore surjective.

<!-- upstream_entity: An-Singularität/Picardgruppe/Beispiel -->

### Example 20.15: the Picard group of a punctured $A_n$ singularity {#br-bgk-2019-l20-exm-02}

Consider the commutative ring

$$
R=K[X,Y,Z]/(XY-Z^n)
$$

over a field $K$, with maximal ideal

$$
\mathfrak m=(X,Y,Z),
$$

and open set

$$
U=D(X,Y)=D(X)\cup D(Y)
=\operatorname{Spek}(R)\setminus\{\mathfrak m\}
\subseteq\operatorname{Spek}(R).
$$

We have

$$
R_X\cong K[X,X^{-1},Z]
$$

via $Y=Z^n/X$. This ring is a unique factorisation domain; hence, by Theorem 20.12, all invertible sheaves on $D(X)$ are trivial, and likewise on $D(Y)$. Furthermore,

$$
R_{XY}=R_Z\cong K[X,X^{-1},Z,Z^{-1}].
$$

Thus an invertible sheaf on $U$ is determined by an isomorphism

$$
K[X,X^{-1},Z,Z^{-1}]
\cong\mathcal O_U|_{D(XY)}
\longrightarrow
K[X,X^{-1},Z,Z^{-1}]
\cong\mathcal O_U|_{D(XY)},
$$

which in turn corresponds to a unit in $K[X,X^{-1},Z,Z^{-1}]$. Let

$$
cX^iZ^j
$$

be such a unit. Units coming from $R_X$ or $R_Y$, and multiplicative combinations of them, give a trivial invertible sheaf by Remark 20.2. The quotient group consists of

$$
Z^j,
\qquad j=0,1,\ldots,n-1,
$$

so the Picard group of $U$ is $\mathbb Z/(n)$.

<!-- upstream_entity: Projektive Gerade/Picardgruppe/Beispiel -->

### Example 20.16: the Picard group of the projective line {#br-bgk-2019-l20-exm-03}

Consider the projective line $\mathbb P_K^1$ over a field $K$ with its standard cover

$$
\mathbb P_K^1=D_+(X)\cup D_+(Y),
$$

consisting of the two affine lines

$$
D_+(X)
=\operatorname{Spek}\!\left(K\left[\frac YX\right]\right)
\cong\mathbb A_K^1
$$

and

$$
D_+(Y)
=\operatorname{Spek}\!\left(K\left[\frac XY\right]\right)
\cong\mathbb A_K^1.
$$

By Theorem 20.12 and Remark 20.2, the Picard group of the projective line can be calculated by taking the units in

$$
\Gamma\!\left(D_+(XY),\mathcal O_{\mathbb P_K^1}\right)
=K\left[\frac XY,\frac YX\right]
$$

modulo the units on the two affine pieces. This gives the group

$$
\left\{\left(\frac XY\right)^k\mathrel{\middle|}k\in\mathbb Z\right\},
$$

so the Picard group is isomorphic to $\mathbb Z$.

The last assertion holds more generally for projective space $\mathbb P_K^d$ with $d\geq1$; see Theorem 22.12.
