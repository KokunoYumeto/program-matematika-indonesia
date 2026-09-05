---
title: "Worksheet 22 - The Divisor Class Group"
stable_id: br-bgk-2019-w22
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 22"
upstream_pageid: 110230
upstream_revid: 1069409
upstream_timestamp: "2026-02-05T19:19:17Z"
upstream_mediawiki_sha1: 47f103239ec0db5780bf211ea257e727d72f3098
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069409"
authority_manifest: authority/wikiversity-bgk/unit-22/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 98e1716c4a8e95d42a19fd6a8b9efb04e222687e5bb6dc296ae42496baab1e39
worksheet_xml: authority/wikiversity-bgk/unit-22/worksheet-22.xml
worksheet_xml_sha256: bff3059aba572579c9352dd309b26129da7e1341aa8094b0a091366d919209da
worksheet_expanded_tex: authority/wikiversity-bgk/unit-22/worksheet-22-expanded.tex
worksheet_expanded_tex_sha256: 18dce8bae2bb05f3337d69cc93949e9b0d2867e3ef3eacd84fcff005e5908b64
official_pdf: authority/artifacts/bgk-worksheet-22-official.pdf
official_pdf_sha256: 2d0e27c819584ea8c4e1fcb4c46a6f7c51ba3bd3f1a8467832fdea9f7d85d10a
ordered_exercise_map: authority/wikiversity-bgk/unit-22/ORDERED_EXERCISE_MAP.json
ordered_exercise_map_sha256: 34c6c4f31bffe001aad01da4c0e553cdfd5d6c36dd354e9e8f6a90823b555d67
exercise_count: 20
public_solution_count: 1
public_solution_numbers: "19"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The official PDFs retain their recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete_semantic_authority_bound
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
rights_ledger: authority/RIGHTS-bgk-unit-22.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-22.json
asset_closure_sha256: e7bf39c238717349b7d2e02a8f05eb252fe6aa39199bce82a8c9f60d1b5ea718
---

# Worksheet 22: The Divisor Class Group {#br-bgk-2019-w22}

The star marks Exercise 22.19. The candidate-title checks recorded by QA
found that this is the only exercise with a public solution page.
The other nineteen candidate titles do not exist; this edition does not
invent new solutions.

<!-- upstream_entity: Ganze Zahlen/Hauptdivisor/1/Aufgabe -->

## Exercise 22.1 {#br-bgk-2019-w22-ex01}

Determine the principal divisor of

$$
\frac{1000}{333}
$$

on $\operatorname{Spek}(\mathbb Z)$.

<!-- upstream_entity: Projektive Gerade/Hauptdivisor/1/Aufgabe -->

## Exercise 22.2 {#br-bgk-2019-w22-ex02}

Determine the principal divisor of

$$
f=(t-3)^2(t-1)^{-5}t^2(t+2)^{-1}
$$

on the projective line

$$
\mathbb P_K^1=\operatorname{Proj}(K[X,Y]).
$$

<!-- upstream_entity: Projektive Gerade/Hauptdivisor/2/Aufgabe -->

## Exercise 22.3 {#br-bgk-2019-w22-ex03}

Determine the principal divisor of

$$
f=\frac{t}{t^2+1}
$$

on the projective line

$$
\mathbb P_K^1=\operatorname{Proj}(K[X,Y]),
\qquad t=\frac YX,
$$

for the fields $K=\mathbb R$ and $K=\mathbb C$.

<!-- upstream_entity: Projektive Gerade/Algebraisch abgeschlossen/Polynom/Hauptdivisor/Summe 0/Aufgabe -->

## Exercise 22.4 {#br-bgk-2019-w22-ex04}

Consider the projective line

$$
\mathbb P_K^1=\operatorname{Proj}(K[X,Y])
$$

over a field $K$, together with the affine line

$$
\mathbb A_K^1\subseteq\mathbb P_K^1
=D_+(X)\cup\{\infty\}
$$

whose ring of global sections is

$$
K\left[\frac YX\right]=K[t].
$$

Prove the following statements.

1. The principal divisor of a polynomial $P\in K[t]$ has no negative
   order (no pole) in $\mathbb A_K^1$.
2. The order of a polynomial $P\in K[t]$ at $\infty$ is the negative
   of the degree of $P$.
3. Let
   $$
   D=\sum_P n_P\cdot P
   $$
   and let $K$ be algebraically closed. Then $D$ is a principal divisor
   if and only if
   $$
   \sum_Pn_P=0.
   $$

> **Editorial note - non-zero polynomial.** Parts 1 and 2 require $P\ne0$:
> the source defines principal divisors and finite orders only for non-zero functions.

<!-- upstream_entity: Projektiver Raum/Weildivisor/Graduierter Polynomring/Aufgabe -->

## Exercise 22.5 {#br-bgk-2019-w22-ex05}

Let

$$
\mathbb P_K^n
=\operatorname{Proj}(K[X_0,X_1,\ldots,X_n])
$$

be projective space over a field $K$. Show that effective Weil divisors
on $\mathbb P_K^n$ correspond to normalised homogeneous polynomials

$$
P\in K[X_0,X_1,\ldots,X_n].
$$

<!-- upstream_entity: Projektiver Raum/Hyperebenen/Linear äquivalent/Aufgabe -->

## Exercise 22.6 {#br-bgk-2019-w22-ex06}

Show that on projective space $\mathbb P_K^d$ over a field,
any two hyperplanes

$$
H_1=V_+(a_0X_0+a_1X_0+\cdots+a_dX_d)
$$

and

$$
H_2=V_+(b_0X_0+b_1X_0+\cdots+b_dX_d)
$$

are linearly equivalent.

> **Editorial note - repeated variable in the source.** Both source equations
> print $X_0$ in their first two terms. This edition preserves these
> formulas and does not silently change the second term.

<!-- upstream_entity: Projektiver Raum/Irreduzible Hyperfläche/Hyperebene/Linear äquivalent/Aufgabe -->

## Exercise 22.7 {#br-bgk-2019-w22-ex07}

Let

$$
V=V_+(F)\subseteq\mathbb P_K^d
$$

be an irreducible hypersurface of degree $d$ in projective space over a
field, viewed as an element of the divisor class group. Show that $V$
is linearly equivalent to $dH$, where $H$ denotes the class of a hyperplane.

<!-- upstream_entity: Projektiver Raum/Hyperebenen/Projektiver Raum/Aufgabe -->

## Exercise 22.8 {#br-bgk-2019-w22-ex08}

Show that the set of all hyperplanes in a projective space itself forms
a projective space of the same dimension.

<!-- upstream_entity: Projektiver Raum/Hyperebenen/Durch Punkte/Aufgabe -->

## Exercise 22.9 {#br-bgk-2019-w22-ex09}

Let $P_0,P_1,\ldots,P_N$ be (closed) points of projective space
$\mathbb P_K^N$ not all contained in any one hyperplane.
Let $0\leq r\leq N$.

1. Show that $P_0,P_1,\ldots,P_r$ are not contained in any projective
   subspace of dimension $<r$.
2. Show that the set of all hyperplanes containing the points
   $P_0,P_1,\ldots,P_r$ forms a projective subspace of dimension
   $N-1-r$ in the space of all hyperplanes.

> **Editorial note - rational points.** The dimension assertion requires
> the $P_i$ to be $K$-rational points, as is automatic over an algebraically
> closed field. Arbitrary closed points over a general field may impose
> more than one linear condition. For $r=N$, the set is empty, interpreted
> as projective dimension $-1$.

<!-- upstream_entity: Normales Schema/Kodimension 2/Divisorenklassengruppe/Aufgabe -->

## Exercise 22.10 {#br-bgk-2019-w22-ex10}

Let $X$ be a normal Noetherian integral scheme, and let $Z\subset X$
be a closed subset of codimension $\geq 2$. Show that the divisor class
groups of $X$ and $X\smallsetminus Z$ agree.

<!-- upstream_entity: Normales Schema/Offene Teilmenge/Divisoren/Einschränkung/Divisorenklassengruppe/Aufgabe -->

## Exercise 22.11 {#br-bgk-2019-w22-ex11}

Let $X$ be a normal Noetherian integral scheme, and let $U\subset X$
be an open subset. Show that omitting the prime divisors not meeting $U$
gives a surjective group homomorphism

$$
\operatorname{Div}(X)\longrightarrow\operatorname{Div}(U).
$$

Show that principal divisors map to principal divisors, so that there is
a surjective group homomorphism

$$
\operatorname{DKG}(X)\longrightarrow\operatorname{DKG}(U).
$$

<!-- upstream_entity: Normales Schema/Punkt/Divisoren/Einschränkung/Divisorenklassengruppe/Aufgabe -->

## Exercise 22.12 {#br-bgk-2019-w22-ex12}

Let $X$ be a normal Noetherian integral scheme, and let $x\in X$
be a point. Show that omitting the prime divisors not passing through
$x$ gives a surjective group homomorphism

$$
\operatorname{Div}(X)
\longrightarrow\operatorname{Div}(\mathcal O_{X,x}).
$$

Show that principal divisors map to principal divisors, so that there is
a surjective group homomorphism

$$
\operatorname{DKG}(X)
\longrightarrow\operatorname{DKG}(\mathcal O_{X,x}).
$$

<!-- upstream_entity: Projektiver Raum/Hyperfläche/Divisor/Invertierbare Untergarbe/Aufgabe -->

## Exercise 22.13 {#br-bgk-2019-w22-ex13}

Let

$$
D
=\sum_Ya_Y\cdot Y
=\sum_ja_j\cdot Y_j
=\sum_ja_j\cdot V_+(G_j)
$$

be a Weil divisor of projective space $\mathbb P_K^d$, where the prime
divisors involved are described by homogeneous prime elements

$$
G_j\in K[X_0,X_1,\ldots,X_d].
$$

Consider the polynomial

$$
G:=\prod_jG_j^{a_j}
$$

of degree

$$
\delta=\sum_ja_j\operatorname{grad}(G_j).
$$

Show that its associated invertible subsheaf $\mathcal L_D$ of the
function-field sheaf, in the sense of Theorem 22.9, agrees with the
realisation of the twisted structure sheaf

$$
\mathcal O_{\mathbb P_K^d}(-\delta)
$$

by multiplication by $G$ from Example 20.9.

> **Editorial note - the word “polynomial” in the source.** The source calls
> $G:=\prod_jG_j^{a_j}$ a polynomial, although the coefficients $a_j$
> of a general Weil divisor may be negative. This edition preserves the
> source terminology and formula without assuming the divisor is effective.

In the following exercises, for a divisor $D$ we work with

$$
\mathcal O_X(D)=-\mathcal L_D.
$$

Thus, for an open subset $U\subseteq X$,

$$
\mathcal O_X(D)(U)
=\{f\in K\mid\operatorname{ord}_Y(f)\geq-D
\text{ for all }Y\in U\}.
$$

> **Editorial note - the convention printed in the source.** The source
> writes $\mathcal O_X(D)=-\mathcal L_D$ and compares
> $\operatorname{ord}_Y(f)$ directly with $-D$, without naming the
> divisor coefficient. This edition preserves that notation.
> Here the minus sign means the inverse invertible sheaf,
> $\mathcal O_X(D)=\mathcal L_{-D}\cong\mathcal L_D^\vee$, not
> pointwise negation of its sections. The inequality means
> $\operatorname{ord}_Y(f)\geq-a_Y$ for prime divisors meeting $U$;
> the zero section is included separately, as in the note to Theorem 22.9.

<!-- upstream_entity: Projektives Schema/Lokal faktoriell/Divisor/Linear äquivalente effektive Divisoren/Aufgabe -->

## Exercise 22.14 {#br-bgk-2019-w22-ex14}

Let $X$ be a locally factorial projective integral scheme over an
algebraically closed field $K$, and let $D$ be a Weil divisor on $X$
with associated sheaf $\mathcal O_X(D)$. Show that there is a natural
correspondence between effective Weil divisors linearly equivalent to $D$
and non-trivial global sections of $\mathcal O_X(D)$, where sections are
identified if they differ only by scaling.

<!-- upstream_entity: Lokal faktorielles integres Schema/Invertierbare Garbe/Schnitt/Nullstelle/Divisor/Isomorphie/Aufgabe -->

## Exercise 22.15 {#br-bgk-2019-w22-ex15}

Let $X$ be a locally factorial Noetherian integral scheme and $\mathcal L$
an invertible subsheaf of the constant function-field sheaf. Let

$$
s\in\Gamma(X,\mathcal L)
$$

be a non-trivial section. Show that the zero locus of $s$, namely

$$
Z(s)=X\smallsetminus X_s,
$$

is naturally an effective Weil divisor $D$ on $X$ such that

$$
\mathcal L\cong\mathcal O_X(D).
$$

<!-- upstream_entity: Projektiver Raum/Effektiver Divisor/Funktion/Glatte Kurve/Induzierter Divisor/Schnitt/Aufgabe -->

## Exercise 22.16 {#br-bgk-2019-w22-ex16}

Let

$$
F=F_1^{a_1}\cdots F_r^{a_r}
$$

be the prime factorisation of a homogeneous polynomial

$$
F\in K[X_0,X_1,\ldots,X_d]
$$

of degree $e$ over an algebraically closed field $K$, with homogeneous
prime polynomials $F_j$, and let

$$
D=\sum_{j=1}^n a_jV_+(F_j)
$$

be the associated Weil divisor on projective space $\mathbb P_K^d$.
Prove the following statements.

1. Every effective Weil divisor on projective space can be represented
   in this form, uniquely up to scaling.
2. Set-theoretically,
   $$
   V_+(F)=\bigcup_{j=1}^nV_+(F_i).
   $$
3. Let $C\subseteq\mathbb P_K^d$ be a smooth projective curve not
   contained in $V_+(F)$. Then $D$ induces a Weil divisor $D|_C$
   on the curve $C$ by taking, at each point $P\in C$, the order of
   $F$ in $\mathcal O_{C,P}$.
4. The restricted invertible sheaf $\mathcal O_{\mathbb P_K^d}(e)|_C$
   is isomorphic to the invertible sheaf on $C$ associated to $D|_C$.
   Thus
   $$
   \mathcal O_{\mathbb P_K^d}(D)|_C
   =\mathcal O_C(D|_C).
   $$
5. Linearly equivalent divisors on projective space induce linearly
   equivalent divisors on the curve.

> **Editorial note - indices in the source.** The source factorisation uses
> $r$ factors, whereas the sum and union use the bound $n$; in the union,
> the running index is $j$ but the term is printed as $F_i$.
> All these indices are preserved as in the source.
> In part 3, “the order of $F$” means the order of the local equation
> $F/X_i^e$ on a chart with $X_i(P)\ne0$. The homogeneous polynomial
> itself is a section of $\mathcal O(e)$, not a function in
> $\mathcal O_{C,P}$. Changing such a chart multiplies the local equation
> by a unit, so its order is well defined.

<!-- upstream_entity: Projektiver Raum/Effektiver Divisor/Kurve/Durchschnitt/Aufgabe -->

## Exercise 22.17 {#br-bgk-2019-w22-ex17}

Let $D$ be an effective Weil divisor in projective space $\mathbb P_K^d$
with at least one positive component. Show that $D$ has non-empty
intersection with every projective curve $C\subseteq\mathbb P_K^d$.

Use the fact that $D_+(f)$ is affine and a projective curve is not affine.

In particular, two curves in the projective plane always have non-empty
intersection. For smooth curves, one can also use Exercise 22.16.
This property by no means holds on all projective surfaces, as the
following examples show.

<!-- upstream_entity: Standardquadrik/Projektiv/Disjunkte Geraden/Aufgabe -->

## Exercise 22.18 {#br-bgk-2019-w22-ex18}

Show that the projective surface

$$
V_+(XY-ZW)\subseteq\mathbb P_K^3
$$

contains disjoint lines, viewed as objects in projective space.

<!-- upstream_entity: Fermat-Kubik/Projektiv/Disjunkte Geraden/Aufgabe -->

## Exercise 22.19 ★ {#br-bgk-2019-w22-ex19}

Show that the projective surface

$$
V_+(X^3+Y^3-Z^3-W^3)\subseteq\mathbb P_K^3
$$

of degree $3$ over an algebraically closed field $K$ of characteristic
$\ne 3$ contains disjoint lines, viewed as objects in projective space.

<!-- upstream_entity: Projektive Ebene/Konzentrische Kreise/Schnittpunkte/Aufgabe -->

## Exercise 22.20 {#br-bgk-2019-w22-ex20}

Let $C_1$ and $C_2$ be two concentric circles in $\mathbb R^2$
centred at $(0,0)$. Determine their intersection points, viewing the
circles as projective curves, in the projective plane $\mathbb P_{\mathbb C}^2$.
