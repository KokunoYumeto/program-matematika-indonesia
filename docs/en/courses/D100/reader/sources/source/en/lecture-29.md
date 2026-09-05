---
title: "Lecture 29 - Projections and Parametrised Projective Curves"
stable_id: br-ak-2012-l29
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Bocardodarapti"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 29"
upstream_pageid: 51996
upstream_revid: 1069408
upstream_timestamp: "2026-02-05T19:18:37Z"
upstream_mediawiki_sha1: 6f0742211aeb307841634425937aad9037da51be
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069408"
authority_manifest: authority/wikiversity/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ec3b34ad387ae827ecaa365c4def3b0550f74b629d0db3873a7cc28dc0831bc5
lecture_xml: authority/wikiversity/unit-29/lecture-29.xml
lecture_xml_sha256: e5055632a6aa8119540cb5acccc0ba86a82b6d2bc88192b9ddd5a77aaea31d70
lecture_expanded_tex: authority/wikiversity/unit-29/lecture-29-expanded.tex
lecture_expanded_tex_sha256: 7c06a1dbb12904bd5f89427955ef8bdae5781e402522cd70f09a0c6e1ef1e784
license: "Current semantic course text and this translation: CC BY-SA 4.0. Unit 29 reader media retain their component-specific public-domain status as recorded in authority/RIGHTS-unit-29.csv. No blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; media component rights remain item-specific; official-PDF notices remain component-specific; no blanket relicensing claim."
license_evidence: "authority/UNIT_29_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-29.csv; authority/ASSET_CLOSURE-unit-29.json"
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 8
source_corrections: 7
correction_ids: "AGC-CORR-0126; AGC-CORR-0127; AGC-CORR-0128; AGC-CORR-0129; REVIEW-AK-26-30-C12; REVIEW-AK-26-30-C13; REVIEW-AK-26-30-C14"
reader_media_positions: 0
---

# Lecture 29: Projections and Parametrised Projective Curves {#br-ak-2012-l29}

## Projection away from a point {#br-ak-2012-l29-s01}

<!-- upstream_entity: Projektiver Raum/Projektion weg von einem Punkt/Definition -->

### Definition 29.1: projection away from a point {#br-ak-2012-l29-def-01}

The map

$$
\begin{aligned}
\mathbb P_K^n\setminus\{(1,0,\ldots,0)\}
&\longrightarrow \mathbb P_K^{n-1},\\
(x_0,x_1,\ldots,x_n)&\longmapsto(x_1,\ldots,x_n)
\end{aligned}
$$

is called the *projection away from the point* $(1,0,\ldots,0)$.

This map is a well-defined morphism outside the *centre* of projection $(1,0,\ldots,0)$. Each other point is sent to the point of $\mathbb P_K^{n-1}$ corresponding to the line through that point and the centre. Hence the map is surjective, and each fibre is a projective line with the centre removed, and thus an affine line. In other words, we have a so-called *line bundle* over $\mathbb P_K^{n-1}$.

This map extends the cone map

$$
\mathbb A_K^n\setminus\{0\}\longrightarrow\mathbb P_K^{n-1}
$$

to punctured projective space. The corresponding map can be defined for any centre; see Exercise 29.7.

## Maps to $\mathbb P_K^1$ {#br-ak-2012-l29-s02}

The following theorem gives a new version of Noether normalisation.

<!-- upstream_entity: Ebene projektive Kurve/Abbildung nach P^1 über Projektion von einem Punkt/Fakt -->

### Theorem 29.2: projecting a plane curve to $\mathbb P_K^1$ {#br-ak-2012-l29-thm-01}

Let $K$ be an algebraically closed field and let

$$
C\subseteq\mathbb P_K^2
$$

be a projective plane curve of degree $d$. Then there is a surjective morphism

$$
C\longrightarrow\mathbb P_K^1
$$

such that each fibre consists of at most $d$ points.

#### Proof {#br-ak-2012-l29-thm-01-proof}

Choose a point

$$
P\in\mathbb P_K^2
$$

not lying on the curve. Such a point exists because, in particular, $K$ is infinite. Consider projection away from $P$; its restriction induces a morphism

$$
C\hookrightarrow\mathbb P_K^2\setminus\{P\}
\longrightarrow\mathbb P_K^1.
$$

The fibre of this morphism over a point

$$
Q\in\mathbb P_K^1,
$$

representing a direction at $P\in\mathbb P_K^2$ consists exactly of those points of the curve lying on the line determined by $Q$,

$$
G=V_+(aX+bY+cZ)\cong\mathbb P_K^1\subseteq\mathbb P_K^2.
$$

Thus the fibre over $Q$ can be described on $G$ by eliminating a variable from the curve equation

$$
C=V_+(F)
$$

using the line equation. The result is a nonzero homogeneous polynomial $\overline F$ in two variables of degree $d$; it cannot be zero, since then $P$ would lie on the curve. As we work over an algebraically closed field, $\overline F$ has at least one and at most $d$ zeros, all distinct from $P$. This proves surjectivity and the bound on the number of points in each fibre. $\square$

<!-- upstream_entity: Glatte projektive Kurven/Rationale Funktion als Morphismus nach P^1/Fakt -->

### Theorem 29.3: a rational function as a morphism to $\mathbb P_K^1$ {#br-ak-2012-l29-thm-02}

Let $K$ be a field and let

$$
C\subseteq\mathbb P_K^2
$$

be a smooth irreducible projective plane curve. Let

$$
D=C\cap D_+(Z)\cong K\!-\!\operatorname{Spek}(R)
$$

be an affine piece of this curve, and let

$$
q=\frac gh\in Q(R)
$$

be a rational function, with $g,h\in R$ and $h\ne0$. Then there is exactly one morphism

$$
\varphi:C\longrightarrow\mathbb P_K^1
$$

such that the diagram

$$
\begin{matrix}
D(h)&\stackrel{g/h}{\longrightarrow}&\mathbb A_K^1\cong D_+(s)\\
\downarrow&&\downarrow\\
C&\stackrel{\varphi}{\longrightarrow}&\mathbb P_K^1
\end{matrix}
$$

commutes.

Moreover, every genuine pole $P\in D$, meaning a point with $h(P)=0$ and $g(P)\ne0$, is mapped to the point at infinity $\infty\in\mathbb P_K^1$.

#### Proof {#br-ak-2012-l29-thm-02-proof}

First we define on $D$ an extension

$$
\varphi:D\longrightarrow\mathbb P_K^1
$$

of the rational function $g/h$. If $q=0$, the constant map with value $0$ is the required extension, so assume from now on that $q\ne0$. Take a point $P\in D$ on the curve. If $P\in D(h)$, there is nothing to do. Thus suppose $h(P)=0$.

> **Source correction REVIEW-AK-26-30-C12 - the zero rational function.** The source immediately writes $g/h=u\pi^n$ with $u$ a unit, which is possible only for a nonzero element of the function field. The theorem also permits $q=0$; the separate constant-map case above closes that gap without changing the nonzero case.

Since the curve is smooth, Theorem 23.6 shows that its local ring $B$ at $P$ is a discrete valuation ring. The quotient $g/h$ can therefore be written there as

$$
\frac gh=u\pi^n,
$$

with $u\in B^\times$, $n\in\mathbb Z$, and $\pi$ a uniformiser (a generator of the maximal ideal). There is an open neighbourhood

$$
P\in D(\psi)\subseteq D
$$

such that $\pi$ and $u$ are defined on $D(\psi)$ and $u$ is a unit there. If $n\geq0$, then

$$
\frac gh\in R_\psi,
$$

so the point of indeterminacy is removable even for a map to $\mathbb A_K^1$. If $n\leq0$, the reciprocal quotient

$$
\frac hg=u^{-1}\pi^{-n}
$$

is defined on $D(\psi)$ as a map to $\mathbb A_K^1$. Using the “embedding with coordinates interchanged”

$$
\mathbb A_K^1\cong D_+(t)\hookrightarrow\mathbb P_K^1,
$$

we obtain a map to $\mathbb P_K^1$.

We must show that these two morphisms to the projective line agree wherever both are defined. These are the points $P$ where $g/h$ has neither a zero nor a pole. Compatibility follows because on an open neighbourhood

$$
P\in U
$$

there is a map

$$
\frac gh:U\longrightarrow
(\mathbb A_K^1)^\times=\mathbb A_K^1\setminus\{0\},
$$

and the diagram

$$
\begin{matrix}
(\mathbb A_K^1)^\times&\stackrel{i^{-1}}{\longrightarrow}&
\mathbb A_K^1\cong D_+(t)\\
\downarrow&&\downarrow\\
\mathbb A_K^1\cong D_+(s)&\longrightarrow&\mathbb P_K^1
\end{matrix}
$$

commutes. This gives a well-defined morphism on the affine piece $D$.

> **Source correction AGC-CORR-0127 - the object with zeros and poles.** The source refers to $\varphi$ in this sentence, although zeros and poles are properties of the rational function $g/h$. This edition displays the correct object without changing the overlap condition or the gluing diagram.

For an arbitrary point on the projective curve $C$ and an affine neighbourhood

$$
P\in D'\subseteq C,
$$

we are in the same situation, because

$$
D_+(h)\cap D'\ne\varnothing,
$$

so the rational function is defined on a nonempty open set, possibly with different numerator and denominator. The preceding argument therefore applies in the same way.

Uniqueness follows because, on every affine open set

$$
P\in U
$$

the intersection $U\cap D_+(h)$ is nonempty. A morphism from an integral variety to the affine line $\mathbb A_K^1$ is uniquely determined by its rational function. $\square$

<!-- upstream_entity: Projektive Gerade/Rationale Funktion/z nach 1/z/Beispiel -->

### Example 29.4: inversion on the projective line {#br-ak-2012-l29-ex-01}

The inversion map

$$
\begin{aligned}
\mathbb A_K^1\supset D(z)&\longrightarrow\mathbb A_K^1,\\
z&\longmapsto z^{-1}
\end{aligned}
$$

extends to a bijective morphism

$$
\begin{aligned}
\mathbb P_K^1&\longrightarrow\mathbb P_K^1,\\
(x,y)&\longmapsto(y,x).
\end{aligned}
$$

This follows directly from Theorem 29.3. Every point $z\ne0$ is sent to $1/z$, while zero is sent to the point at infinity $\infty$.

## Parametrised projective plane curves {#br-ak-2012-l29-s03}

Suppose a curve with rational parametrisation

$$
s\longmapsto
\left(\frac{\varphi_1(s)}{\psi(s)},
      \frac{\varphi_2(s)}{\psi(s)}\right).
$$

is given. In Theorem 6.11 we saw that its image satisfies an algebraic equation. In that theorem's proof we already used the homogenised parametrisation; it now reappears as a projective extension.

<!-- upstream_entity: Rationale Kurvenparametrisierung/Fortsetzung auf projektive Gerade/Fakt -->

### Theorem 29.5: projective extension of a rational parametrisation {#br-ak-2012-l29-thm-03}

Let $K$ be an infinite field, and let

$$
\begin{aligned}
\mathbb A_K^1\supseteq D(\psi)&\longrightarrow\mathbb A_K^2,\\
s&\longmapsto
\left(\frac{\varphi_1(s)}{\psi(s)},
      \frac{\varphi_2(s)}{\psi(s)}\right)
\end{aligned}
$$

be a rational parametrisation in reduced form, meaning that $\varphi_1,\varphi_2,\psi$ have no common divisor. Let $d$ be the largest degree of the polynomials involved, and let

$$
\widehat{\varphi_1},\quad\widehat{\varphi_2},\quad\widehat\psi
$$

be their homogenisations with respect to the new variable $t$. Each of $H_1,H_2,H_3$ is obtained from the corresponding homogenisation by multiplication by a suitable power of $t$, so that all three have degree $d$.

Then $H_1,H_2,H_3$ define a morphism

$$
\begin{aligned}
H:\mathbb P_K^1&\longrightarrow\mathbb P_K^2,\\
(s,t)&\longmapsto\bigl(H_1(s,t),H_2(s,t),H_3(s,t)\bigr),
\end{aligned}
$$

such that the diagram

$$
\begin{matrix}
\mathbb A_K^1\supseteq D(\psi)&\longrightarrow&
\mathbb A_K^2\cong D_+(Z)\\
\downarrow&&\downarrow\\
\mathbb P_K^1&\stackrel{H}{\longrightarrow}&\mathbb P_K^2
\end{matrix}
$$

commutes. Moreover, the image of $H$ lies on the projective closure of the affine image curve.

> **Source-condition note REVIEW-AK-26-30-C13 - infinitude of the base field.** The source does not state this hypothesis, but its proof uses the assertion that a finite open subset of $\mathbb P_K^1$ is empty. For the source's topology on $K$-points this requires $K$ to be infinite; it fails over a finite field, where every subset of $\mathbb P_K^1$ is finite.

#### Proof {#br-ak-2012-l29-thm-03-proof}

By Exercise 29.6, the map $H$ is well defined on all of $\mathbb P_K^1$, since $\varphi_1,\varphi_2,\psi$ have no common divisor. For commutativity, it suffices to note that a point

$$
s\in D(\psi)\subseteq\mathbb A_K^1
$$

is sent, on the one hand, through $(s,1)$ to

$$
\bigl(H_1(s,1),H_2(s,1),H_3(s,1)\bigr)
=\bigl(\varphi_1(s),\varphi_2(s),\psi(s)\bigr),
$$

and, on the other hand, to

$$
\left(\frac{\varphi_1(s)}{\psi(s)},
      \frac{\varphi_2(s)}{\psi(s)},1\right)
=\bigl(\varphi_1(s),\varphi_2(s),\psi(s)\bigr)
$$

as a projective point.

For the additional assertion, let $C$ be the affine closure of the image and let

$$
\overline C\subseteq\mathbb P_K^2
$$

be its projective closure. Consider the open complement

$$
U=\mathbb P_K^2\setminus\overline C.
$$

Since the map is continuous, the inverse image $H^{-1}(U)$ is open in $\mathbb P_K^1$ and can contain only points of $\mathbb P_K^1\setminus D(\psi)$. But a finite open subset of the projective line must be empty. $\square$

<!-- upstream_entity: Ebene projektive Kurve/Graph eines Polynoms in einer Variable/Singularität im Unendlichen/Fakt -->

### Theorem 29.6: projective closure of the graph of a polynomial {#br-ak-2012-l29-thm-04}

Let $K$ be an algebraically closed field and let

$$
F\in K[X]
$$

be a polynomial in one variable of degree $d\geq1$. The projective closure $C$ of the graph

$$
V(Y-F(X))
$$

is described by

$$
V_+\bigl(YZ^{d-1}-\widehat F(X,Z)\bigr),
$$

where $\widehat F(X,Z)$ is the homogenisation of $F$. If $d=1$ and $F=aX+b$, then $C$ has one additional point, the smooth point $(1,a,0)$. If $d\geq2$, the additional point is $(0,1,0)$, which is singular when $d\geq3$. For $d\geq2$, this point at infinity has multiplicity $d-1$.

> **Source correction AGC-CORR-0128 - projective zero-locus operator.** The source prints $V$ for a homogeneous equation in $\mathbb P_K^2$. This edition uses $V_+$, in keeping with the projective ambient space and the notation of the subsequent proof.

#### Proof {#br-ak-2012-l29-thm-04-proof}

The equation of the projective closure follows directly from Corollary 28.10. To determine the intersection of $C$ with the projective line $V_+(Z)$ at infinity, set $Z=0$ in the equation.

If $d=1$, the curve equation is the line equation

$$
V_+(Y-aX-bZ),
$$

and its intersection with $V_+(Z)$ gives the unique point $(1,a,0)$. If $d\geq2$, the curve equation is

$$
V_+\bigl(
YZ^{d-1}-s_dX^d-s_{d-1}X^{d-1}Z-\cdots-s_0Z^d
\bigr),
$$

with $s_d\ne0$. Setting $Z=0$ leaves

$$
V_+(-s_dX^d),
$$

so $X=0$. This gives the unique point at infinity $(0,1,0)$.

To compute the multiplicity, consider the affine equation of the curve on $D_+(Y)$. Setting $Y=1$ gives the affine equation

$$
V\bigl(
Z^{d-1}-s_dX^d-s_{d-1}X^{d-1}Z-\cdots-s_0Z^d
\bigr),
$$

and in these coordinates $(0,1,0)$ becomes the origin. Hence its multiplicity is $d-1$, with the unique tangent line given by $Z=0$. If $d\geq3$, the multiplicity is at least $2$, so the point is singular. $\square$

> **Source correction AGC-U29-SRC-001 / AGC-CORR-0126 - undefined symbol in the singularity bound.** In the last sentence of the proof, the source prints $g\geq3$, although no quantity $g$ is defined in this theorem. The degree defined and used throughout the calculation is $d$; this edition therefore displays the intended bound as $d\geq3$ and explicitly retains the multiplicity argument $d-1\geq2$.

The theorem can be understood as follows. If $d\geq2$, the point $(0,1,0)$ is the unique point at infinity and represents the direction of the $y$-axis. The line at infinity $V_+(Z)$ is the unique tangent line at this point.

> **Source correction REVIEW-AK-26-30-C14 - direction versus asymptote.** The source calls the $y$-axis the graph's only asymptote. The projective point $(0,1,0)$ records the direction of that axis, not an affine asymptotic line; in the usual affine sense a polynomial graph of degree at least two has no linear asymptote. The source's valid tangent-line statement is retained.

The normalisation of $C$ is $\mathbb P_K^1$. By Theorem 29.5, applied to the affine parametrisation of the graph

$$
\begin{aligned}
\mathbb A_K^1&\longrightarrow
\mathbb A_K^1\times\mathbb A_K^1
=\mathbb A_K^2\cong D_+(Z)\subset\mathbb P_K^2,\\
x&\longmapsto(x,F(x))=(x,F(x),1),
\end{aligned}
$$

the normalisation map is given by

$$
\begin{aligned}
\mathbb P_K^1&\longrightarrow C\subset\mathbb P_K^2,\\
(x,t)&\longmapsto\bigl(xt^{d-1},\widehat F(x,t),t^d\bigr).
\end{aligned}
$$

The point at infinity $(1,0)$ is sent to

$$
(0,s_d,0)=(0,1,0).
$$

<!-- upstream_entity: Ebene projektive Kurve/Graph einer rationalen Funktion in einer Variable/Singularität im Unendlichen/Fakt -->

### Theorem 29.7: projective closure of the graph of a rational function {#br-ak-2012-l29-thm-05}

Let $K$ be an algebraically closed field, and let

$$
G,H\in K[X]
$$

be polynomials in one variable of degrees $d,e\geq1$, respectively, with no common root. Let $H\ne0$ and let

$$
F(X)=\frac{G(X)}{H(X)}
$$

be the corresponding rational function. Let $\widehat G(X,Z)$ and $\widehat H(X,Z)$ be their respective homogenisations. If $d>e$, the projective closure $C$ of the graph of $F(X)$ is described by

$$
V_+\bigl(\widehat H(X,Z)YZ^{d-e-1}-\widehat G(X,Z)\bigr),
$$

whereas if $d\leq e$, it is described by

$$
V_+\bigl(\widehat H(X,Z)Y-\widehat G(X,Z)Z^{e-d+1}\bigr).
$$

#### Proof {#br-ak-2012-l29-thm-05-proof}

The affine description of the curve is

$$
V(YH-G).
$$

By Corollary 28.10, the projective closure is described by the homogenisation of $YH-G$. This is determined by the larger of the degrees of $YH$ and $G$; the summand of smaller degree must be “filled out” with a suitable power of $Z$. This yields the two equations above. $\square$

## Monomial projective curves {#br-ak-2012-l29-s04}

For the monomial plane curve

$$
s\longmapsto(s^e,s^d)=(x,y)
$$

with coprime exponents $e>d$, Theorem 29.5 gives the monomial projective curve

$$
(s,t)\longmapsto(s^e,s^dt^{e-d},t^e).
$$

On the open set $D_+(t)$ this is the original map, whereas on $D_+(s)$ it becomes the affine map

$$
t\longmapsto(t^{e-d},t^e).
$$

<!-- upstream_entity: Ebene projektive monomiale Kurve/Singularität/Gesamtmultiplizität/Fakt -->

### Theorem 29.8: singularities of monomial projective curves {#br-ak-2012-l29-thm-06}

Let $e>d$ be coprime. For the monomial projective plane curve of degree $e$

$$
C:\quad(s,t)\longmapsto\bigl(s^e,s^dt^{e-d},t^e\bigr),
$$

the following statements hold.

1. The curve is described by the homogeneous equation of degree $e$

   $$
   Y^e=X^dZ^{e-d}.
   $$

2. The curve is smooth at all points other than $(0,0,1)$ and $(1,0,0)$.

3. The curve has multiplicity $d$ at $(0,0,1)$ and multiplicity $e-d$ at $(1,0,0)$.

4. If $e\geq3$, the curve is not smooth.

#### Proof {#br-ak-2012-l29-thm-06-proof}

1. The affine equation is $X^d-Y^e$. By Corollary 28.10, the projective closure is described by its homogenisation, namely

   $$
   V_+\bigl(X^dZ^{e-d}-Y^e\bigr).
   $$

   > **Source correction AGC-CORR-0129 - projective zero-locus operator.** The source prints $V$ for the homogenisation defining the closure in $\mathbb P_K^2$; this edition uses $V_+$. The affine loci below retain $V$.

2. On the affine curve

   $$
   V(X^d-Y^e)\subseteq\mathbb A_K^2\subseteq\mathbb P_K^2,
   $$

   by the current source's [normalisation result for affine monomial curves](https://de.wikiversity.org/wiki/Affine_Kurven/Monomiale_Kurvenabbildung/Ist_Normalisierung/Fakt), only the origin—corresponding to the projective point $(0,0,1)$—can fail to be smooth. Points of the curve outside $D_+(Z)$ are obtained by setting $Z=0$ in the equation. This forces $Y=0$, leaving only the point $(1,0,0)$.

   > **Semantic-source note REVIEW-AK-26-30-C15.** The expanded 2012 witness cites Theorem 20.12 here; the frozen current proof instead links to the named normalisation result above. This edition preserves the current source target and the unchanged smoothness conclusion.

3. Multiplicity at a point is a local property. The point $(0,0,1)$ corresponds to the origin on the affine monomial curve

   $$
   V(X^d-Y^e),
   $$

   which, by Corollary 23.8, has multiplicity equal to the smaller exponent, namely $d$. The point $(1,0,0)$ lies in $D_+(X)$, where the affine equation is

   $$
   V(Y^e-Z^{e-d}).
   $$

   Its multiplicity is again the smaller exponent, namely $e-d$.

4. This follows from item 3. $\square$
