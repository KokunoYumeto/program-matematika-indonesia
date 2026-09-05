---
title: "Lecture 26 - Intersection Multiplicity"
stable_id: br-ak-2012-l26
language: en
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2012)/Vorlesung 26"
upstream_pageid: 50732
upstream_revid: 793526
upstream_timestamp: "2022-08-25T06:09:17Z"
upstream_mediawiki_sha1: 57845c7bb535d0cccde6d289409a8dbbe684f2d8
source_url: "https://de.wikiversity.org/w/index.php?oldid=793526"
authority_manifest: authority/wikiversity/unit-26/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 981fa3c86534514215c722b6d4f6d711c040a7829465f20ae18940373f94763c
lecture_xml: authority/wikiversity/unit-26/lecture-26.xml
lecture_xml_sha256: cc6a483e01e22db4262c3e400325ec22c4cf8750e3a1a8c11043398368f40ff9
lecture_expanded_tex: authority/wikiversity/unit-26/lecture-26-expanded.tex
lecture_expanded_tex_sha256: 567968794b07d9e045813a62921dc8b527e99f500807bff843bd7cb498ea8ee7
lecture_dependency_identity_rows_sha256: f1a064c0531f9079633a57009c565f20a0520a0ef10cb2336ad3b52aa2d331b8
license: "Current semantic course text and this translation: CC BY-SA 4.0. Intersect3.png: CC BY-SA 3.0. The official 2012 PDF file-description surface also records the legacy CC BY-SA 2.0 Germany route. No blanket relicensing claim is made."
source_component_license_route: "Semantic-site rights notice: CC BY-SA 4.0; Intersect3.png: CC BY-SA 3.0; official-PDF legacy file-description notice: CC BY-SA 2.0 Germany; official-PDF current print-version notice: CC BY-SA 4.0; no blanket relicensing claim."
license_evidence: "authority/UNIT_26_AUTHORITY_FREEZE.md; authority/RIGHTS-unit-26.csv; authority/ASSET_CLOSURE-unit-26.json"
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_semantic_entities: 21
source_corrections: 6
correction_ids: "AGC-CORR-0097; AGC-CORR-0098; AGC-CORR-0099; AGC-CORR-0100; AGC-CORR-0104; AGC-CORR-0106"
reader_media_positions: 1
---

# Lecture 26: Intersection Multiplicity {#br-ak-2012-l26}

## Intersection multiplicity {#br-ak-2012-l26-s01}

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Lokale und semilokale Beschreibung/Einführung/Textabschnitt -->

Let two plane algebraic curves

$$
C,D\subseteq\mathbb A_K^2
$$

be given, with no common component. By Theorem 4.8, the intersection $C\cap D$ consists of only finitely many points. We want to describe quantitatively how the two curves intersect at a point

$$
P\in C\cap D.
$$

For this purpose, it is useful to consider a slightly more general situation. We write

$$
C=V(F)
\qquad\text{and}\qquad
D=V(G),
$$

and allow prime factors to occur repeatedly in both $F$ and $G$. In other words, from now on we distinguish $V(F)$ from $V(F^n)$, although they are the same geometric object.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Restdimension ist endlich/Fakt -->

### Lemma 26.1: finite dimension of the quotient {#br-ak-2012-l26-lem-01}

Let $K$ be a field and let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common prime divisor. Let

$$
P\in V(F,G)
$$

and let

$$
R=K[X,Y]_{\mathfrak m_P}
$$

be the corresponding localisation. Then the quotient ring

$$
R/(F,G)
$$

is finite-dimensional as a vector space over $K$.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Restdimension ist endlich/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-lem-01-proof}

Let $\mathfrak m$ be the maximal ideal of $R$. Since $F$ and $G$ have no common divisor, there is no other prime ideal between $(F,G)$ and $\mathfrak m$ in $R$. Consequently, every nonunit in $R/(F,G)$ is nilpotent. Thus, for some $s$,

$$
\mathfrak m^s\subseteq(F,G)\subseteq\mathfrak m.
$$

Hence there is a surjection

$$
R/\mathfrak m^s\longrightarrow R/(F,G).
$$

By Lemma 23.3 in the source numbering, the ring on the left is finite-dimensional over $K$. The ring on the right is therefore also finite-dimensional over $K$. $\square$

This lemma makes the following definition meaningful.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Restdimension/Definition -->

### Definition 26.2: intersection multiplicity {#br-ak-2012-l26-def-01}

Let $K$ be a field and let

$$
F,G\in K[X,Y]
$$

be two nonconstant polynomials with no common component, and let

$$
P\in V(F)\cap V(G)=V(F,G).
$$

The dimension

$$
\dim_K\left(K[X,Y]_{\mathfrak m_P}/(F,G)\right)
$$

is called the *intersection multiplicity* of the curves $V(F)$ and $V(G)$ at $P$. It is denoted by

$$
\operatorname{mult}_P(F,G)
\qquad\text{or}\qquad
\operatorname{mult}_P\bigl(V(F),V(G)\bigr).
$$

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Restdimension/Schnitt mit Gerade/Beispiel -->

### Example 26.3: intersection of a curve with a line {#br-ak-2012-l26-ex-01}

Let

$$
C=V(F)
$$

and a line

$$
L=V(cX+dY)
$$

in the affine plane $\mathbb A_K^2$ be given, where $L$ is not a component of $C$. Let

$$
P=(a,b)\in C\cap L.
$$

The quotient ring

$$
K[X,Y]_{\mathfrak m_P}/(F,cX+dY)
$$

can be computed by solving the linear equation for one of the variables. If $d\ne0$, substitute

$$
Y=-\frac cdX
$$

into $F$ to obtain the one-variable polynomial

$$
\widetilde F(X)=F\left(X,-\frac cdX\right).
$$

Thus

$$
K[X,Y]_{\mathfrak m_P}/(F,cX+dY)
\cong K[X]_{(X-a)}/(\widetilde F).
$$

If $d=0$, then $c\ne0$, so we solve for $X$ and obtain the analogous statement in $Y$, localised at $(Y-b)$. Equivalently, we may first form the one-variable quotient ring and then localise at the corresponding point.

Now suppose that $K$ is algebraically closed. In the case $d\ne0$, we have a factorisation

$$
\widetilde F=u(X-\lambda_1)^{\nu_1}\cdots
(X-\lambda_k)^{\nu_k},\qquad u\in K^\times.
$$

Since $P$ is a zero, we must have $a=\lambda_i$ for some $i$. On localising at $(X-a)$, all the other linear factors become units. The remaining factor gives a ring isomorphic to

$$
K[X]/(X-\lambda_i)^{\nu_i},
$$

which has dimension $\nu_i$ over $K$.

> **Editorial note - elimination cases and localisation.** The source immediately replaces $Y$ by $-(c/d)X$ without stating the condition $d\ne0$, and then writes $K[X]_P$. This edition separates the cases $d\ne0$ and $c\ne0$ and specifies the correct one-variable localisation ideal, namely $(X-a)$ or $(Y-b)$. The source also suppresses the nonzero leading coefficient in the factorisation of $\widetilde F$; the scalar $u$ is displayed here and, being a unit, does not affect the quotient or its dimension.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Schnitt mit Gerade/Abschätzung zur Multiplizität/Fakt -->

### Lemma 26.4: intersection with a line {#br-ak-2012-l26-lem-02}

Let $K$ be an algebraically closed field, let

$$
F=F_m+\cdots+F_d\in K[X,Y],
\qquad m\leq d,
$$

be the homogeneous decomposition of a polynomial, and let

$$
L=V(aX+bY)
$$

be a line through the origin $P$ which is not a component of $V(F)$. Then

$$
\operatorname{mult}_P\bigl(L,V(F)\bigr)
\geq m_P(F)=m.
$$

In other words, the intersection multiplicity of a curve with a line is at least the multiplicity of the curve at the intersection point. If $L$ is not a tangent to the curve, equality holds.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Schnitt mit Gerade/Abschätzung zur Multiplizität/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-lem-02-proof}

Set

$$
R=K[X,Y]_{(X,Y)}
\qquad\text{and}\qquad
H=aX+bY.
$$

Without loss of generality, suppose $b\ne0$, so that $H=0$ can be written as $Y=cX$ for some $c\in K$. If $b=0$, then $a\ne0$, and the same argument applies after interchanging $X$ and $Y$.

First suppose that $L$ is not a tangent to $V(F)$ at $P$, and hence $L$ is not a component of $V(F_m)$. Then

$$
R/(F,H)
\cong
K[X]_{(X)}/\bigl(F_m(X,cX)+\cdots+F_d(X,cX)\bigr).
$$

Since $F_m(X,cX)\ne0$, the polynomial generating the ideal can be written as $X^m u$ with $u$ a unit. The quotient ring therefore has dimension $m$ over $K$.

In the general case there is a least index $i$, with $m\leq i\leq d$, such that

$$
F_i(X,cX)\ne0.
$$

Such an index must exist, since otherwise $L$ would be a component of $V(F)$. By the same argument, the dimension of the quotient ring is $i\geq m$. $\square$

> **Editorial note - choice of coordinates in the proof.** The source assumes $b\ne0$ without explaining the other case. This edition states that the choice is without loss of generality, since for $b=0$ the variables $X$ and $Y$ can be interchanged.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Erste Eigenschaften/Fakt -->

### Lemma 26.5: basic properties {#br-ak-2012-l26-lem-03}

Let $K$ be an algebraically closed field, let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common component, and let $P\in\mathbb A_K^2$. Then the following hold:

1. $\operatorname{mult}_P(F,G)=0$ if and only if $P\notin V(F,G)$.
2. $\operatorname{mult}_P(F,G)=\operatorname{mult}_P(G,F)$.
3. Intersection multiplicity is unchanged by an affine change of variables.
4. If $F=F_1F_2$ and $F_2(P)\ne0$, then
   $$
   \operatorname{mult}_P(F,G)=\operatorname{mult}_P(F_1,G).
   $$
5. For every $H\in K[X,Y]$,
   $$
   \operatorname{mult}_P(F,G)
   =\operatorname{mult}_P(F,G+HF).
   $$

**Proof.** This is immediate.

The fourth assertion can also be phrased as follows: intersection multiplicity depends only on those components of $F$ and $G$ that pass through $P$.

![A circle and a curve tangent on the left and crossing transversely on the right](authority/assets/250px-Intersect3.png)

*One transverse and one nontransverse intersection. Image created by Michael Larsen and uploaded to Commons by Maksim; [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); local file: `authority/assets/250px-Intersect3.png`.*

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Transversaler Schnitt/Definition -->

### Definition 26.6: transverse intersection {#br-ak-2012-l26-def-02}

Let

$$
F,G\in K[X,Y]
\qquad\text{and}\qquad
P\in V(F,G).
$$

The curves $V(F)$ and $V(G)$ are said to *intersect transversely* at $P$ if $P$ is a smooth point of both curves and their tangent lines at $P$ are distinct.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Charakterisierung Transversaler Schnitt/Fakt -->

### Lemma 26.7: characterisation of transverse intersection {#br-ak-2012-l26-lem-04}

Let $K$ be a field and let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common component. Let

$$
P\in V(F,G)\subseteq\mathbb A_K^2
$$

be an intersection point. Then $V(F)$ and $V(G)$ intersect transversely at $P$ if and only if

$$
\operatorname{mult}_P\bigl(V(F),V(G)\bigr)=1.
$$

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Charakterisierung Transversaler Schnitt/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-lem-04-proof}

Let

$$
R=K[X,Y]_{\mathfrak m_P}
$$

be the local ring of the plane at $P$. First suppose that the intersection is transverse. Both curves are smooth at $P$, and by Lemma 23.2 in the source numbering,

$$
B=R/(F)
$$

is a discrete valuation ring. Since the tangent lines are distinct, after a change of coordinates we may assume that the tangent to $V(F)$ is $V(Y)$ and the tangent to $V(G)$ is $V(X)$. In $B$, the element $X$ is a local uniformiser. Since

$$
G=X+H,
\qquad H\in\mathfrak m_P^2,
$$

the element $G$ is also a local uniformiser in $B$. Hence

$$
B/(G)=K,
$$

and the intersection multiplicity is one.

Conversely, suppose that

$$
\dim_K R/(F,G)=1.
$$

Since $P$ is a $K$-rational point, this quotient is the residue field $K$. Its maximal ideal therefore vanishes, or equivalently,

$$
(F,G)=\mathfrak m_P
$$

in $R$. Passing to the quotient modulo $\mathfrak m_P^2$, the linear terms of $F$ and $G$ generate the two-dimensional cotangent space $\mathfrak m_P/\mathfrak m_P^2$. Both linear terms are therefore nonzero and linearly independent. Thus both curves are smooth at $P$, and the kernels of the two linear forms, namely their tangent lines, are distinct. The intersection is therefore transverse. $\square$

> **Editorial note - correction to the converse proof.** The source deduces smoothness of both curves by citing Lemma 26.4. However, that lemma concerns only the intersection of a curve with a line, and so does not justify the asserted conclusion for two arbitrary polynomials. Moreover, Lemma 26.4 is stated over an algebraically closed field, whereas Lemma 26.7 is stated over an arbitrary field. This edition replaces that step with a direct argument in $\mathfrak m_P/\mathfrak m_P^2$, valid for the $K$-rational point in the statement.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Summenformel für Schnittmultiplizität/Fakt -->

### Theorem 26.8: additivity formula {#br-ak-2012-l26-thm-01}

Let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common prime divisor, with factorisations

$$
F=\prod_{i=1}^{m}F_i^{\nu_i}
\qquad\text{and}\qquad
G=\prod_{j=1}^{n}G_j^{\mu_j}.
$$

Then, for every $P\in\mathbb A_K^2$,

$$
\operatorname{mult}_P(F,G)
=\sum_{i,j}\nu_i\mu_j\operatorname{mult}_P(F_i,G_j).
$$

Away from intersection points, the multiplicities on both sides are understood to be zero, as in Lemma 26.5.

> **Editorial note - quantification of the point.** The source displays $P$ in the formula without introducing or quantifying it. This edition states that the identity holds for every $P\in\mathbb A_K^2$, with the zero convention outside the intersection.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Summenformel für Schnittmultiplizität/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-thm-01-proof}

By induction, it suffices to prove the special case $F=F_1F_2$. Set

$$
R=K[X,Y]_{\mathfrak m_P}.
$$

Since

$$
(F_1F_2,G)\subseteq(F_2,G),
$$

there is a surjective map

$$
R/(F_1F_2,G)\longrightarrow R/(F_2,G).
$$

On the other hand, multiplication by $F_2$ induces an $R$-module homomorphism

$$
R/(F_1,G)\longrightarrow R/(F_1F_2,G).
$$

We claim that there is a short exact sequence

$$
0\longrightarrow R/(F_1,G)
\mathop{\longrightarrow}^{\cdot F_2}
R/(F_1F_2,G)
\longrightarrow R/(F_2,G)
\longrightarrow0.
$$

Surjectivity of the right-hand map is clear, as is the fact that the composition of the two maps is zero. Suppose a class $z\in R/(F_1F_2,G)$ maps to zero on the right. In $R$ we can write

$$
z=AF_2+BG.
$$

Thus $AF_2$ represents the same class in $R/(F_1F_2,G)$, and that class comes from the left.

Now suppose a class $w\in R/(F_1,G)$ maps to zero under multiplication by $F_2$. In $R$ this means

$$
wF_2=CF_1F_2+DG,
$$

or

$$
(w-CF_1)F_2=DG.
$$

Since $F$ and $G$ have no common prime divisor, neither do $F_2$ and $G$. Hence $F_2$ divides $D$, giving

$$
w-CF_1=\widetilde D G.
$$

Thus $w=0$ in $R/(F_1,G)$, and the left-hand map is injective.

Additivity of dimension in short exact sequences now gives

$$
\begin{aligned}
\operatorname{mult}_P(F_1F_2,G)
&=\dim_K R/(F_1F_2,G)\\
&=\dim_K R/(F_1,G)+\dim_K R/(F_2,G)\\
&=\operatorname{mult}_P(F_1,G)+\operatorname{mult}_P(F_2,G).
\end{aligned}
$$

Induction over all factors of $F$ and $G$ proves the formula. $\square$

<!-- upstream_entity: Noetherscher Nulldimensionaler Ring/Produktdarstellung/Fakt -->

### Theorem 26.9: product decomposition of a zero-dimensional Noetherian ring {#br-ak-2012-l26-thm-02}

Let $R$ be a commutative Noetherian ring with only finitely many prime ideals

$$
\mathfrak m_1,\ldots,\mathfrak m_n,
$$

all of which are maximal. Then there is a canonical isomorphism

$$
R\cong R_{\mathfrak m_1}\times\cdots\times R_{\mathfrak m_n}.
$$

<!-- upstream_entity: Noetherscher Nulldimensionaler Ring/Produktdarstellung/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-thm-02-proof}

These maximal ideals are also the minimal prime ideals. Their intersection,

$$
\mathfrak a=\bigcap_i\mathfrak m_i,
$$

therefore consists entirely of nilpotent elements. Since $R$ is Noetherian, there is an $s$ such that

$$
\mathfrak a^s=0.
$$

For each $i$, consider the localisation

$$
R\longrightarrow R_{\mathfrak m_i}.
$$

We claim that this localisation is isomorphic to

$$
R/\mathfrak a_i,
\qquad
\mathfrak a_i:=\mathfrak m_i^s.
$$

Since

$$
\prod_i\mathfrak m_i\subseteq\bigcap_i\mathfrak m_i,
$$

we obtain

$$
\left(\prod_i\mathfrak m_i\right)^s
\subseteq
\left(\bigcap_i\mathfrak m_i\right)^s,
$$

and hence

$$
\mathfrak a_1\cdots\mathfrak a_n=0.
$$

Take $i=1$. For every $j\ne1$, there is an element

$$
g_j\in\mathfrak m_j
\qquad\text{with}\qquad
g_j\notin\mathfrak m_1.
$$

For every $f\in\mathfrak a_1$, we have

$$
fg_2^s\cdots g_n^s=0.
$$

Since $g_2^s\cdots g_n^s\notin\mathfrak m_1$, this element becomes a unit after localisation. Thus $f$ maps to zero, and we obtain a ring homomorphism

$$
R/\mathfrak a_1\longrightarrow R_{\mathfrak m_1}.
$$

The right-hand side is also a localisation of the quotient ring on the left. Distinct maximal ideals are pairwise comaximal, and this remains true of their powers. Hence $\mathfrak a_1$ is contained only in $\mathfrak m_1$. Thus $R/\mathfrak a_1$ is itself a zero-dimensional local ring, so the map above is an isomorphism. The same argument applies for every $i$.

The original map can therefore be written as

$$
R\longrightarrow\prod_{i=1}^{n}R/\mathfrak a_i.
$$

Since the ideals $\mathfrak a_i$ are pairwise comaximal, the Chinese Remainder Theorem says that this map is an isomorphism. $\square$

<!-- upstream_entity: Ebene algebraische Kurve/Schnitt von Kurven ohne gemeinsame Komponente/Beschreibung als Produktring/Fakt -->

### Corollary 26.10: the global quotient as a product of local rings {#br-ak-2012-l26-cor-01}

Let $K$ be an algebraically closed field and let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common prime divisor. Let

$$
P_1,\ldots,P_n\in\mathbb A_K^2
$$

be all the points of $V(F,G)$, with corresponding maximal ideals $\mathfrak m_1,\ldots,\mathfrak m_n$ in $K[X,Y]$. Then there is a canonical isomorphism

$$
K[X,Y]/(F,G)
\cong
\prod_{i=1}^{n}\left(K[X,Y]_{\mathfrak m_i}/(F,G)\right).
$$

<!-- upstream_entity: Ebene algebraische Kurve/Schnitt von Kurven ohne gemeinsame Komponente/Beschreibung als Produktring/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-cor-01-proof}

Since $F$ and $G$ have no common prime divisor, the ideal $(F,G)$ is contained in only finitely many prime ideals, all of them maximal. Consequently the quotient ring

$$
K[X,Y]/(F,G)
$$

satisfies the hypotheses of Theorem 26.9. Since $K$ is algebraically closed, these maximal ideals correspond bijectively to the intersection points of $V(F)$ and $V(G)$. This gives the asserted isomorphism. $\square$

> **Editorial note - ring symbol in the proof.** The source writes $R/(F,G)$ in this proof without defining $R$. From the corollary's statement and the application of Theorem 26.9, the intended ring is $K[X,Y]/(F,G)$; this edition writes it explicitly.

<!-- upstream_entity: Ebene algebraische Kurve/Schnittmultiplizität/Summe der Multiplizitäten ist Restklassendimension/Fakt -->

### Theorem 26.11: sum of intersection multiplicities {#br-ak-2012-l26-thm-03}

Let $K$ be an algebraically closed field and let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common prime divisor. Then

$$
\dim_K\bigl(K[X,Y]/(F,G)\bigr)
=\sum_P\operatorname{mult}_P(F,G),
$$

where the sum runs over all points $P\in V(F,G)$.

<!-- upstream_entity: Ebene algebraische Kurve/Schnittmultiplizität/Summe der Multiplizitäten ist Restklassendimension/Fakt/Beweis -->

#### Proof {#br-ak-2012-l26-thm-03-proof}

This follows directly from the isomorphism proved in Corollary 26.10, since the dimension of a finite product of vector spaces is the sum of the dimensions of its factors. $\square$

Finally, we record without proof the following theorem, which gives a bound relating intersection multiplicity to the multiplicities of the two curves.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Abschätzung von Schnittmultiplizität und Multiplizität/Fakt -->

### Theorem 26.12: lower bound for intersection multiplicity {#br-ak-2012-l26-thm-04}

Let

$$
F,G\in K[X,Y]
$$

be two polynomials with no common component and let

$$
P\in V(F,G).
$$

Then

$$
\operatorname{mult}_P(F,G)
\geq m_P(F)\,m_P(G).
$$

> **Editorial note - finiteness hypothesis.** The source does not state that $F$ and $G$ must have no common component. Without this condition, the local quotient in the definition of intersection multiplicity can be infinite-dimensional. This edition adds the hypothesis already governing the entire discussion in this lecture.

<!-- upstream_entity: Ebene algebraische Kurven/Schnittmultiplizität/Abschätzung von Schnittmultiplizität und Multiplizität/Fakt/Beweisverweis -->

#### Proof reference {#br-ak-2012-l26-thm-04-proof-reference}

See Fulton, *Algebraic Curves*, Chapter III.3.
