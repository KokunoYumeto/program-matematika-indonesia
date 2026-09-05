---
title: "Lecture 29 - The genus of a curve"
stable_id: br-bgk-2019-l29
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 29"
upstream_pageid: 109033
upstream_revid: 1069570
upstream_timestamp: "2026-02-06T07:06:34Z"
upstream_mediawiki_sha1: 6c3afd8d6d4c0a4fac5ed90903c46b10ccab0aaa
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069570"
authority_manifest: authority/wikiversity-bgk/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 376380a874b545579d61c100d1f66eac11bad854d76f7e586b10cd621e7a54f7
lecture_xml: authority/wikiversity-bgk/unit-29/lecture-29.xml
lecture_xml_sha256: 2b6d1a6b75858ecfa71730685caa7499ec878ca4326208c9dfe38edbc2902a5b
lecture_expanded_tex: authority/wikiversity-bgk/unit-29/lecture-29-expanded.tex
lecture_expanded_tex_sha256: 019ac2495bb9c5b2347c44c0332a8212b2946953dbd1aa519e7248c53103f06c
official_pdf: authority/artifacts/bgk-lecture-29-official.pdf
official_pdf_sha256: d612185a0afbeddd66a3c434dddac48679c00947723565a2367c08d2bc76dd15
official_course_pdf: authority/artifacts/bgk-course-official.pdf
media_credits: source/id-ID/media-credits-bgk-unit-29.md
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain their own component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 29: The genus of a curve {#br-bgk-2019-l29}

## Smooth projective curves and their genus {#br-bgk-2019-l29-s01}

<!-- upstream_entity: Glatte projektive Kurve/Geschlecht/Erste Kohomologie/Definition -->
### Definition 29.1: genus {#br-bgk-2019-l29-def-01}

For a smooth projective curve $C$ over an algebraically closed field $K$, the number

$$
g:=\dim_K H^1(C,\mathcal O_C)
$$

is called the *genus* of the curve.

By Theorem 27.7, the dimension of $H^1(C,\mathcal O_C)$ is finite. Thus the genus of a curve is a natural number.

> **Source illustrations.** The following three surfaces illustrate genus one, two, and three through their number of handles. They occur in this order in the official lecture and retain their component public-domain status.

![A green torus with one handle, a surface of genus one](authority/assets/bgk-torus-illustration-500.png)

![A green double torus with two handles, a surface of genus two](authority/assets/bgk-double-torus-illustration-500.png)

![A green sphere-like surface with three handles, a surface of genus three](authority/assets/bgk-sphere-with-three-handles-500.png)

<!-- upstream_entity: Projektive Gerade/Kohomologisches Geschlecht/Beispiel -->
### Example 29.2 {#br-bgk-2019-l29-exa-02}

By Theorem 27.4, the genus of the projective line

$$
\mathbb P^1_K=\operatorname{Proj}(K[X,Y])
$$

is $0$.

<!-- upstream_entity: Elliptische Kurve/Geschlecht 1/Definition -->
### Definition 29.3: an elliptic curve {#br-bgk-2019-l29-def-03}

A smooth projective curve $C$ of genus $1$ over an algebraically closed field $K$ is called an *elliptic curve*.

<!-- upstream_entity: Glatte projektive Kurven/C/Kurzübersicht zur topologischen Gestalt/2/Bemerkung -->
### Remark 29.4 {#br-bgk-2019-l29-rem-04}

If the complex numbers $\mathbb C$ are chosen as the ground field, the genus of a smooth projective curve has a simple topological interpretation. Such a curve can be regarded as a compact one-dimensional complex manifold—a Riemann surface—and also as a compact oriented two-dimensional real manifold. Manifolds of the latter kind have a simple topological classification: each is homeomorphic to the surface of a sphere with $g$ handles attached. This number is called the topological genus of the real surface, and hence also of the curve.

It can be proved that the genus defined algebraically using the first cohomology of the structure sheaf agrees with this topological genus. The complex projective line is a two-dimensional sphere with no handles, so its topological genus is $0$. A surface of genus $1$ is a torus—like a tyre—homeomorphic to $S^1\times S^1$. Projective curves of genus $1$, namely elliptic curves, have this topological shape.

<!-- upstream_entity: Ebene projektive Kurve/Grad/Kohomologisches Geschlecht/Fakt -->
### Theorem 29.5 {#br-bgk-2019-l29-thm-05}

Let

$$
C=V_+(f)\subseteq\mathbb P^2_K
$$

be a projective plane curve of degree $d$ over an algebraically closed field $K$. Then

$$
\dim_K H^1(C,\mathcal O_C)=\frac{(d-1)(d-2)}{2}.
$$

#### Proof {#br-bgk-2019-l29-thm-05-proof}

Consider the short exact sequence (compare Exercise 13.23)

$$
0\longrightarrow\mathcal O_{\mathbb P^2_K}(-d)
\xrightarrow{\ f\ }
\mathcal O_{\mathbb P^2_K}
\longrightarrow\mathcal O_C\longrightarrow0
$$

of coherent sheaves on the projective plane. Here the structure sheaf $\mathcal O_C$ is regarded as a sheaf on the projective plane with support $C$. The relevant portion of the associated long exact cohomology sequence is

$$
H^1(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K})=0
\longrightarrow H^1(\mathbb P^2_K,\mathcal O_C)
\longrightarrow H^2(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(-d))
\longrightarrow H^2(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K})=0.
$$

Both vanishings follow from Theorem 27.4. By the same theorem, the space

$$
H^2(\mathbb P^2_K,\mathcal O_{\mathbb P^2_K}(-d))
$$

has a basis consisting of all monomials $x^iy^jz^k$ whose exponents are all negative and satisfy $i+j+k=-d$. Thus we must count tuples $(\alpha,\beta,\gamma)$ of degree $d-3$. By Exercise 12.4, their number is

$$
\binom{d-3+2}{2}=\binom{d-1}{2}=\frac{(d-1)(d-2)}{2}.
$$

By Theorem 27.6, $H^1(\mathbb P^2_K,\mathcal O_C)=H^1(C,\mathcal O_C)$, which proves the assertion. $\square$

> **Edition note (PDF witness).** The official 2020 PDF witness still refers to Exercise 11.4; the frozen semantic revision controlling this edition has updated the reference to Exercise 12.4.

In the smooth case, this theorem gives a formula for computing the genus of a plane curve:

| $d$ | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|
| $g$ | 0 | 0 | 1 | 3 | 6 |

For $d=1$, we obtain a projective line of genus $0$. For $d=2$, we obtain a projective plane quadric—a conic section—which also has genus $0$ and is indeed isomorphic to the projective line. For $d=3$, the genus is $1$, so the curve is elliptic. It can be proved that every elliptic curve can be realised as a plane cubic curve. It is by no means obvious that there are smooth projective curves of every genus. By Theorem 29.5, not all can be realised as plane curves.

<!-- upstream_entity: Glatte projektive Kurve/Kohomologisches Geschlecht/Differentialformen/Serre-Dualität/Bemerkung -->
### Remark 29.6 {#br-bgk-2019-l29-rem-06}

The cohomologically defined genus of a smooth projective curve agrees with the vector-space dimension of the global sections of its canonical sheaf. In dimension one, the canonical sheaf is the sheaf of Kähler differentials $\Omega_{C\mid K}$, that is, the cotangent sheaf, dual to the tangent sheaf. Thus

$$
\dim_K H^1(C,\mathcal O_C)
=\dim_K\Gamma(C,\omega_C).
$$

For plane curves this is immediate. By Theorem 29.5, the genus is $(d-1)(d-2)/2$. Corollary 19.12 gives $\omega_C\cong\mathcal O_C(d-3)$, and by Exercise 27.10 the dimension of $\Gamma(C,\mathcal O_C(d-3))$ is also $(d-1)(d-2)/2$.

In the general case, Serre duality applies. Among other things, it states that for a locally free sheaf $\mathcal F$ on a smooth projective curve $C$, the cohomology group $H^1(C,\omega_C)$ is a one-dimensional $K$-vector space, and the natural map

$$
\operatorname{Hom}(\mathcal F,\omega_C)
\times H^1(C,\mathcal F)
\longrightarrow H^1(C,\omega_C)\cong K
$$

gives a perfect duality. In other words, $\operatorname{Hom}(\mathcal F,\omega_C)$ and $H^1(C,\mathcal F)$ are dual to one another and in particular have the same dimension. For the structure sheaf $\mathcal F=\mathcal O_C$, the equality $\operatorname{Hom}(\mathcal O_C,\omega_C)=\Gamma(C,\omega_C)$ from Theorem 13.10 gives the duality between $H^1(C,\mathcal O_C)$ and $\Gamma(C,\omega_C)$.

> **Edition note (source).** In the corresponding Hom display, the frozen source has the malformed nested expression `\mathcal{\mathcal O_C}`. The intended structure sheaf $\mathcal O_C$ is displayed above.

## Divisors on curves {#br-bgk-2019-l29-s02}

On a smooth projective curve $C$, as on any one-dimensional normal scheme, a Weil divisor is simply a formal sum

$$
\sum_{P\in C} n_P\,P
$$

over closed points $P$. In this case, those points are the prime divisors, that is, the irreducible closed subsets of codimension $1$. The coefficients satisfy $n_P\in\mathbb Z$, and only finitely many are nonzero. By Corollary 22.11, the divisor class group agrees with the Picard group.

We will discuss how divisors on curves behave under morphisms. A morphism between two irreducible curves is either constant or has dense image. A nonconstant morphism $\varphi:C_1\to C_2$ induces an extension of function fields

$$
Q(C_2)\subseteq Q(C_1).
$$

First we show that an element of the function field of a smooth curve can be regarded as a morphism to the projective line. In general, for a nonconstant element $q$ of the function field of a normal scheme $X$, the principal divisor $\operatorname{div}(q)$ can be decomposed into the divisor of zeros and the divisor of poles, with positive coefficients. These two effective divisors are linearly equivalent and, in the locally factorial case by Exercise 22.15, correspond to sections of the associated invertible sheaf $\mathcal O_X(\text{divisor of zeros}(q))$. The results of the preceding lecture show that these two sections determine a morphism to the projective line on an open set $U\subseteq X$. The following result is stronger for smooth curves: the domain of definition is the entire curve.

> **Edition note (PDF witness).** The official 2020 PDF witness still refers to Exercise 22.13; the frozen semantic revision controlling this edition has updated the reference to Exercise 22.15.

<!-- upstream_entity: Glatte Kurve/Rationale Funktion/Morphismus/Fakt -->
### Lemma 29.7 {#br-bgk-2019-l29-lem-07}

Let $C$ be a smooth irreducible curve over an algebraically closed field $K$, and let $Q$ be its function field. Every rational function $q\in Q$ naturally determines a morphism

$$
q:C\longrightarrow\mathbb P^1_K.
$$

#### Proof {#br-bgk-2019-l29-lem-07-proof}

Let

$$
U:=\{P\in C\mid q\in\mathcal O_{C,P}\}
$$

be the domain of definition of $q$ as a function to the affine line. If $q=0$, the constant map with image $(1,0)$ proves the assertion. Hence assume $q\ne0$ and let

$$
V:=\{P\in C\mid q^{-1}\in\mathcal O_{C,P}\}
$$

be the domain of definition of $q^{-1}$. We have $C=U\cup V$, since every $\mathcal O_{C,P}$ is a discrete valuation ring and there $q=\pi^n u$ for a unit $u\in\mathcal O_{C,P}$, a local parameter $\pi\in\mathcal O_{C,P}$, and $n\in\mathbb Z$. By Corollary 10.12, there are a morphism

$$
q:U\longrightarrow\mathbb A^1_K
=\operatorname{Spec}K\!\left[\frac YX\right]
\cong D_+(X)\subseteq\mathbb P^1_K
$$

and a morphism

$$
q^{-1}:V\longrightarrow\mathbb A^1_K
=\operatorname{Spec}K\!\left[\frac XY\right]
\cong D_+(Y)\subseteq\mathbb P^1_K.
$$

These correspond to the substitution homomorphisms $Y/X\mapsto q$ and $X/Y\mapsto q^{-1}$. On $U\cap V$ the two morphisms agree, so they glue to a morphism to the projective line. $\square$

> **Edition note (source).** The source defines $V$ only when $q\ne0$ but then uses $V$ as though it existed for every $q$. The trivial case $q=0$ has been separated above; the gluing argument then applies under the stated assumption $q\ne0$.

<!-- upstream_entity: Diskrete Bewertungsringe/Verzweigungsordnung/Definition -->
### Definition 29.8: ramification index {#br-bgk-2019-l29-def-08}

For an injective ring homomorphism $R\subseteq S$ between discrete valuation rings, the order in $S$ of a local uniformiser of $R$ is called the *ramification index* of the extension.

The ramification order is denoted by $\operatorname{Ram}(S\mid R)$. If $\varphi:C_1\to C_2$ is a nonconstant morphism between smooth curves over an algebraically closed field, then for each closed point $Q\in C_1$ with image point $\varphi(Q)\in C_2$ there is an extension of discrete valuation rings

$$
\mathcal O_{C_2,\varphi(Q)}\subseteq\mathcal O_{C_1,Q}.
$$

The corresponding ramification order is also called the ramification order of $\varphi$ at $Q$ and is denoted by $\operatorname{Ram}(Q\mid\varphi(Q))$.

> **Edition note (source and PDF witness).** The frozen semantic revision uses *Verzweigungsindex* (“ramification index”) in the definition, then *Verzweigungsordnung* (“ramification order”) in the following paragraph. The official 2020 PDF witness also uses *Verzweigungsordnung* in the definition. This edition explicitly preserves the terminology difference between the witnesses.

<!-- upstream_entity: Glatte Kurven/Morphismus/Zurückgezogener Divisor/Definition -->
### Definition 29.9: pullback of a Weil divisor {#br-bgk-2019-l29-def-09}

Let $\varphi:C_1\to C_2$ be a nonconstant morphism between smooth curves over an algebraically closed field, and let

$$
D=\sum_P a_P\,P
$$

be a Weil divisor on $C_2$. The Weil divisor

$$
\varphi^*D
:=\sum_{Q\in C_1}
\operatorname{Ram}(Q\mid\varphi(Q))a_{\varphi(Q)}\,Q
$$

is called the *pullback Weil divisor*.

For a single point $P\in C_2$, the pullback divisor is

$$
\sum_{Q\in\varphi^{-1}(P)}
\operatorname{Ram}(Q\mid P)\,Q.
$$

Thus it is essentially the fibre over $P$, but ramification points—points with ramification order at least $2$—are counted with multiplicity according to their orders.

<!-- upstream_entity: Glatte Kurve/Morphismus/Zurückgezogener Divisor/Hauptdivisor/Fakt -->
### Lemma 29.10 {#br-bgk-2019-l29-lem-10}

Let $\varphi:C_1\to C_2$ be a nonconstant morphism between smooth irreducible curves over an algebraically closed field, and let

$$
D=\sum_P a_P\,P=\operatorname{div}(q)
$$

be a principal divisor on $C_2$, with $q\in Q(C_2)$ and $q\ne0$. Then $\varphi^*(D)$ agrees with the principal divisor of $q\in Q(C_1)$ on $C_1$.

#### Proof {#br-bgk-2019-l29-lem-10-proof}

Since $\varphi$ is nonconstant, there is a field extension $Q(C_2)\subseteq Q(C_1)$. For every $Q\in C_1$, there is a commutative diagram of injective homomorphisms

$$
\begin{CD}
\mathcal O_{C_2,\varphi(Q)} @>>> \mathcal O_{C_1,Q}\\
@VVV @VVV\\
Q(C_2) @>>> Q(C_1),
\end{CD}
$$

with discrete valuation rings in the first row. If $q=u\pi_2^n$, where $u\in\mathcal O_{C_2,\varphi(Q)}$ is a unit and $\pi_2$ is a local uniformiser, the source writes

$$
q=u\pi_2^n
=u\bigl(u'\pi_1^{\operatorname{Ram}(Q\mid\varphi(Q))}\bigr)^n
=u(u')^n\pi_1^{n\operatorname{Ram}(Q\mid\varphi(Q))},
$$

where $\pi_1$ is a local uniformiser of $\mathcal O_{C_1,Q}$. This proves the assertion. $\square$

> **Edition note (source and PDF witness).** The frozen semantic revision uses the argument order $\operatorname{Ram}(Q\mid\varphi(Q))$ above, whereas the official 2020 PDF witness reverses it to $\operatorname{Ram}(\varphi(Q)\mid Q)$. This edition follows the frozen semantic revision. When expanding $(u'\pi_1^e)^n$, both witnesses write the unit factor $u'$ instead of $(u')^n$; that exponent has been corrected above.

<!-- upstream_entity: Glatte Kurve/Rationale Funktion/Morphismus nach P^1/Hauptdivisor/Fakt -->
### Corollary 29.11 {#br-bgk-2019-l29-cor-11}

Let $C$ be a smooth irreducible curve over an algebraically closed field $K$, let $Q$ be its function field, and let $q\in Q\setminus K$. For the associated morphism

$$
q:C\longrightarrow\mathbb P^1_K
$$

we have

$$
q^*((0)-(\infty))=\operatorname{div}(q).
$$

#### Proof {#br-bgk-2019-l29-cor-11-proof}

The function field of the projective line $\mathbb P^1_K=\operatorname{Proj}(K[X,Y])$ is $K(t)$, with $t=Y/X$. The extension of function fields is given by

$$
K(t)\longrightarrow Q(C),\qquad t\longmapsto q.
$$

The principal divisor of $t$ is $(0)-(\infty)=(Y)-(X)$, using two descriptions of the points. The assertion therefore follows from Lemma 29.10. $\square$

## The degree of a divisor {#br-bgk-2019-l29-s03}

<!-- upstream_entity: Glatte projektive Kurve/Weildivisor/Grad/Definition -->
### Definition 29.12 {#br-bgk-2019-l29-def-12}

Let $C$ be a smooth projective curve over an algebraically closed field $K$. The degree of a Weil divisor $D=\sum_{P\in C}n_P P$ is defined as

$$
\deg(D):=\sum_{P\in C}n_P.
$$

<!-- upstream_entity: Glatte projektive Kurve/Hauptdivisor/Grad 0/Fakt -->
### Theorem 29.13 {#br-bgk-2019-l29-thm-13}

Let $C$ be a smooth projective curve over an algebraically closed field $K$. Every principal divisor has degree $0$.

This theorem is stated without proof. Consequently, the group homomorphism

$$
\operatorname{Div}(C)\longrightarrow\mathbb Z,
\qquad D\longmapsto\deg(D),
$$

factors through the divisor class group of $C$. The following definition therefore makes sense.

<!-- upstream_entity: Glatte projektive Kurve/Invertierbare Garbe/Grad/Definition -->
### Definition 29.14 {#br-bgk-2019-l29-def-14}

Let $C$ be a smooth projective curve over an algebraically closed field $K$. The degree of an invertible sheaf $\mathcal L$ on $C$ is defined as the degree of an associated Weil divisor.

“Associated” means that a divisor $D$ corresponds to the invertible sheaf $\mathcal O_C(D)$; in particular, effective divisors correspond to sections of this sheaf.
