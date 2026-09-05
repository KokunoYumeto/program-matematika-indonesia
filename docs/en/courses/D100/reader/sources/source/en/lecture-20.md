---
title: "Lecture 20 - Normal Rings and Normalisation"
stable_id: br-ak-2025-2026-l20
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 20"
upstream_pageid: 165909
upstream_revid: 1112311
upstream_timestamp: "2026-08-21T09:10:26Z"
upstream_mediawiki_sha1: 74eb303dc659cb8131aaaee6948962210f063f4e
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112311"
authority_manifest: authority/wikiversity/unit-20/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b063e5edc556cd18598389083ea27ea7f255edfe2ae00e13ebf24de76e5b37d7
lecture_xml_sha256: 052aee339f49d9d2dfe7f71f50a17c5cc4f9f507eae70a2b8692a1dd5aa38e77
lecture_expanded_tex_sha256: 8d95abad821218ccc9a32b3b7d57f8696b57bb98991c707f4ef8e5a20a1bdecc
license: "CC BY-SA 4.0 for translated course text; the figure retains CC BY 2.5 component rights in authority/RIGHTS-unit-20.csv"
translation_status: complete
---

# Lecture 20: Normal Rings and Normalisation {#br-ak-2025-2026-l20}

## Normal rings and normalisation {#br-ak-2025-2026-l20-s01}

<!-- upstream_entity: Kommutative Ringtheorie/Ganzheit/Normal (ganz-abgeschlossen)/Definition -->

### Definition: normal integral domain {#br-ak-2025-2026-l20-def-01}

An integral domain is called *normal* if it is integrally closed in its field of fractions.

Unique factorisation domains provide important examples of normal rings.

<!-- upstream_entity: Kommutative Ringtheorie/Faktoriell/Normal/Fakt -->

### Theorem: unique factorisation domains are normal {#br-ak-2025-2026-l20-thm-01}

Let $R$ be a unique factorisation domain. Then $R$ is normal.

#### Proof {#br-ak-2025-2026-l20-thm-01-proof}

Let

$$
K=Q(R)
$$

be the field of fractions of $R$, and let $q\in K$ satisfy an equation of integral dependence

$$
q^n+r_{n-1}q^{n-1}+r_{n-2}q^{n-2}+\cdots+r_1q+r_0=0,
\qquad r_i\in R.
$$

Write

$$
q=\frac ab,
\qquad a,b\in R,
\qquad b\ne0,
$$

in lowest terms, so that $a$ and $b$ have no common prime divisor. We must show that $b$ is a unit in $R$, since then

$$
q=ab^{-1}\in R.
$$

Multiplying the equation of integral dependence above by $b^n$ gives, in $R$,

$$
a^n+(r_{n-1}b)a^{n-1}+(r_{n-2}b^2)a^{n-2}
+\cdots+(r_1b^{n-1})a+r_0b^n=0.
$$

If $b$ is not a unit, it has a prime divisor $p$. This element $p$ divides all the terms

$$
(r_{n-i}b^i)a^{n-i},
\qquad i\geq1,
$$

and hence also divides the first term $a^n$. Thus $p$ divides $a$, contradicting the assumption that $a$ and $b$ have no common prime divisor.

<!-- upstream_entity: Kommutative Ringtheorie/Normal/Nenneraufnahme ist normal/Fakt -->

### Lemma: localisations of normal integral domains are normal {#br-ak-2025-2026-l20-lem-01}

Let $R$ be a normal integral domain and $S\subseteq R$ a multiplicative system. Then the localisation $R_S$ is also normal.

#### Proof {#br-ak-2025-2026-l20-lem-01-proof}

See Exercise 20.6.

<!-- upstream_entity: Kommutative Ringtheorie/Ganzheit/Normalisierung für Integritätsbereich/Definition -->

### Definition: normalisation of an integral domain {#br-ak-2025-2026-l20-def-02}

Let $R$ be an integral domain with field of fractions $Q(R)$. The integral closure of $R$ in $Q(R)$ is called the *normalisation* of $R$.

By Corollary 19.10, the normalisation is a subring of the field of fractions. It is a nontrivial fact that if $R$ is of finite type over a field, then its normalisation is also of finite type.

## Normalisation of monoid rings {#br-ak-2025-2026-l20-s02}

We shall discuss when monoid rings are normal and how their normalisations can be described. First we need conditions ensuring that a monoid ring over an integral domain is again an integral domain.

<!-- upstream_entity: Kommutatives Monoid/Torsionsfrei/Definition -->

### Definition: torsion-free monoid {#br-ak-2025-2026-l20-def-03}

A commutative monoid $M$ is called *torsion-free* if, for $m,n\in M$ and a positive integer $r\in\mathbb N_+$, the equality

$$
rm=rn
$$

always implies

$$
m=n.
$$

<!-- upstream_entity: Kommutative Monoidringe/Monoid mit Kürzungsregel und torsionsfrei/Grundring integer/Integer/Fakt -->

### Theorem: torsion-free monoid rings are integral domains {#br-ak-2025-2026-l20-thm-02}

Let $R$ be an integral domain and $M$ a torsion-free commutative monoid satisfying the cancellation law. Then the monoid ring $R[M]$ is an integral domain.

#### Proof {#br-ak-2025-2026-l20-thm-02-proof}

First,

$$
M\subseteq\Gamma(M),
$$

where $\Gamma(M)$ is the group of differences of $M$. Hence

$$
R[M]\subseteq R[\Gamma(M)]
$$

is a subring, so it suffices to prove the statement for $R[\Gamma(M)]$. Since $M$ is torsion-free, Exercise 20.10 shows that $\Gamma(M)$ is also torsion-free. Thus we may assume that $M$ itself is a torsion-free commutative group.

Suppose

$$
\left(\sum_{m\in M}a_mX^m\right)
\left(\sum_{m\in M}b_mX^m\right)=0.
$$

All but finitely many coefficients in these two sums are zero. Hence the entire calculation takes place in a finitely generated subgroup $U$ of the torsion-free group $M$. By the structure theorem for finitely generated torsion-free commutative groups,

$$
U\cong\mathbb Z^n.
$$

Thus we may even assume that $M=\mathbb Z^n$. In this case $R[M]$ is a localisation of a polynomial ring over an integral domain, and is therefore an integral domain.

Without the cancellation law, a monoid ring over an integral domain can have zero divisors.

<!-- upstream_entity: Kommutative Monoidringe/Grundring integer/Monoidring nicht integer/Beispiel -->

### Example: zero divisors without cancellation {#br-ak-2025-2026-l20-exa-01}

Let $M$ be a monoid containing two distinct elements $m$ and $n$ with

$$
m+n=n+n.
$$

Without cancellation, this equation does not imply $m=n$. In the monoid ring over any integral domain $R$ we have

$$
X^m-X^n\ne0
\qquad\text{and}\qquad
X^n\ne0,
$$

but

$$
(X^m-X^n)X^n
=X^{m+n}-X^{n+n}
=X^{2n}-X^{2n}
=0.
$$

<!-- upstream_entity: Kommutative Monoidtheorie/Normalisierung in Differenzengruppe und normal/Definition -->

### Definition: normalisation of a monoid {#br-ak-2025-2026-l20-def-04}

Let $M$ be a torsion-free commutative monoid satisfying the cancellation law, with group of differences $\Gamma(M)$. The submonoid

$$
\widetilde M
=\{m\in\Gamma(M)\mid
\text{there is }r\in\mathbb N_+\text{ with }rm\in M\}
$$

is called the *normalisation* of $M$.

<!-- upstream_entity: Kommutative Monoidtheorie/Normalisierung/Monoid und Monoidring/Fakt -->

### Theorem: normalisation of a monoid ring {#br-ak-2025-2026-l20-thm-03}

Let $M$ be a torsion-free commutative monoid satisfying the cancellation law, with group of differences $\Gamma(M)$ and normalisation

$$
M\subseteq\widetilde M\subseteq\Gamma(M).
$$

Let $R$ be a normal integral domain. Then the normalisation of the monoid ring $R[M]$ is the monoid ring

$$
R[\widetilde M].
$$

In particular, the monoid ring of a normal monoid over a normal ring is itself normal.

#### Proof {#br-ak-2025-2026-l20-thm-03-proof}

First,

$$
R[M]\subseteq R[\widetilde M]
\subseteq R[\Gamma(M)]
\subseteq Q(R)[\Gamma(M)]
\subseteq Q(R[M]).
$$

Take $m\in\widetilde M$ with

$$
m=n-k,
\qquad n,k\in M,
$$

and with

$$
rm=\underbrace{m+\cdots+m}_{r\text{ times}}\in M.
$$

Then

$$
T^m=\frac{T^n}{T^k}
$$

is an element of the field of fractions, while

$$
(T^m)^r\in R[M].
$$

Thus $T^m$ satisfies a pure equation of integral dependence over $R[M]$ and belongs to the normalisation of $R[M]$. Hence

$$
R[\widetilde M]\subseteq R[M]^{\operatorname{norm}}.
$$

**Edition note:** in the last two formulas the source changes the base ring from $R$ to $K$, although the theorem and the entire argument specify $R$. This edition consistently retains $R$. The source also prints $rm=M$ in the defining condition; by the definition of $\widetilde M$, the required relation, displayed here, is $rm\in M$.

For the reverse inclusion, we can replace $M$ by $\widetilde M$ and thus restrict attention to the case in which $M$ is normal. First one proves that, for a torsion-free commutative group $G$, the group ring $R[G]$ is normal. This follows from the fact that a polynomial ring over a normal domain is again normal. It remains to show that $R[M]$ is integrally closed in $R[\Gamma(M)]$.

An element

$$
q\in R[\Gamma(M)]
$$

> **Edition note — brackets in the group ring.** The frozen source writes
> $R(\Gamma(M))$ in this line. In keeping with the specified ambient ring,
> this edition uses $R[\Gamma(M)]$; the argument is unchanged.

and its equation of integral dependence lie in the monoid ring of a finitely generated subgroup

$$
U\subseteq\Gamma(M).
$$

We may therefore assume

$$
\Gamma(M)=\mathbb Z^n.
$$

At this point some convex geometry enters, which we shall not develop. In any case, a normal submonoid

$$
M\subseteq\mathbb Z^n
$$

can be expressed as the intersection of $\mathbb Z^n$ with a polyhedral cone in $\mathbb Q^n$ or $\mathbb R^n$. By Gordan's lemma, this cone is in turn a finite intersection of half-spaces $H_i$.

**Edition note:** the finite polyhedral-cone argument in this paragraph requires $M$ to be finitely generated, a hypothesis not stated in the source theorem. For the stated generality, take an integral element $q=a/b$ and let $N\subseteq M$ be the finitely generated submonoid containing the supports of $a$, $b$, and of the coefficients of an integral equation for $q$. The affine case gives $q\in R[\widetilde N]$, while normality of $M$ gives $\widetilde N\subseteq M$. Thus the theorem's conclusion is unchanged, but the displayed finite intersection is justified only after this finite reduction.

A half-space $H$ is specified by a linear map

$$
p:V=\mathbb R^n\longrightarrow\mathbb R
$$

through

$$
H=p^{-1}(\mathbb R_+).
$$

Thus $M$ is a finite intersection

$$
M=\bigcap_{i\in I}M_i,
\qquad
M_i=p_i^{-1}(\mathbb N),
$$

with

$$
M_i\cong\mathbb N\times\mathbb Z^{n-1}.
$$

Consequently,

$$
R[M]=\bigcap_{i\in I}R[M_i]
$$

is normal by Exercise 20.7, since each

$$
R[M_i]\cong R[\mathbb N\times\mathbb Z^{n-1}]
$$

is normal.

<!-- upstream_entity: Monoidringe/Dimension zwei/Whitney Regenschirm/X^2Y-Z^2/Beispiel -->

### Example: the Whitney umbrella {#br-ak-2025-2026-l20-exa-02}

![A bluish-grey Whitney umbrella surface intersecting itself in three-dimensional space](authority/assets/Whitney_unbrella.png)

*The Whitney umbrella. Claudio Rocchini,
[CC BY 2.5](https://creativecommons.org/licenses/by/2.5/). The source's
inline licence label differs from the options available in the Commons
metadata; the frozen rights details are recorded in the Unit 20 media credits.*

Consider the algebraic surface given by the equation

$$
X^2Z=Y^2.
$$

We shall view it as the surface associated with a monoid ring. Set

$$
M=\langle(1,0),(1,1),(0,2)\rangle\subseteq\mathbb N^2.
$$

Since

$$
(1,1)-(1,0)=(0,1),
$$

its group of differences is $\mathbb Z^2$. Moreover,

$$
2(0,1)=(0,2)\in M,
$$

so $\mathbb N^2$ is the normalisation of $M$. The three generators give a surjective monoid homomorphism

$$
\begin{aligned}
\mathbb N^3&\longrightarrow M,\\
e_i&\longmapsto m_i.
\end{aligned}
$$

Geometrically, the monomial map

$$
\mathbb N^3\longrightarrow M\subseteq\mathbb N^2
$$

corresponds to the map

$$
\begin{aligned}
\mathbb A_K^2&\longrightarrow
K\!-\!\operatorname{Spek}(K[M])\hookrightarrow\mathbb A_K^3,\\
(s,t)&\longmapsto(s,st,t^2).
\end{aligned}
$$

Under this monoid homomorphism,

$$
2e_1+e_3\longmapsto(2,2)
\qquad\text{and}\qquad
2e_2\longmapsto(2,2).
$$

This gives the equation

$$
X^2Z=Y^2,
$$

which can of course also be read directly from the parametrisation.

**Edition note:** the source prints that both elements map to $(1,1)$. With the displayed generators, both map to $(2,2)$. This edition transparently corrects these coordinates; the relation $X^2Z=Y^2$ is unchanged.

The defining equation can also be written as

$$
Z=\left(\frac YX\right)^2.
$$

Thus, starting from $K[X,Y]$, we adjoin the square of $Y/X$.

<!-- upstream_entity: Monoidringe/Dimension zwei/Standardkegel/Z^2-XY/Monoid und Bewertungen/Beispiel -->

### Example: the standard monomial cone {#br-ak-2025-2026-l20-exa-03}

Consider the submonoid

$$
M=\langle(1,0),(-1,2),(0,1)\rangle\subseteq\mathbb Z^2.
$$

Its associated monoid ring satisfies

$$
K[M]\cong K[X,Y,Z]/(Z^2-XY).
$$

We claim that the monoid is normal, that is, equal to its normalisation. The two generators $(1,0)$ and $(-1,2)$ each determine a line in $\mathbb R^2$, and the monoid consists of all lattice points inside the cone determined by these lines. The lattice points in this cone are given by the two conditions

$$
\{(s,t)\in\mathbb Z^2\mid t\geq0\text{ and }t\geq-2s\}.
$$

A point in this set with $s\geq0$ plainly belongs to $M$. Now let $(s,t)$ be a point of the set with $s<0$. By the second linear condition, we can write

$$
(s,t)=-s(-1,2)+(t+2s)(0,1),
$$

and this point belongs to $M$ because $t+2s\geq0$.

The two lines also immediately describe $M$ as

$$
M=M_1\cap M_2,
$$

with

$$
M_1=\{(s,t)\in\mathbb Z^2\mid t\geq0\}
\cong\mathbb Z\times\mathbb N
$$

and

$$
M_2=\{(s,t)\in\mathbb Z^2\mid t\geq-2s\}
\cong\mathbb Z\times\mathbb N.
$$

The second identification comes from the $\mathbb Z$-basis $(-1,2),(0,1)$. This explicit description shows that the associated monoid ring is normal.

## Monomial curves and normalisation {#br-ak-2025-2026-l20-s03}

Later we shall see that an algebraic curve is normal if and only if it is nonsingular. For monomial curves, the normalisation is easy to describe.

<!-- upstream_entity: Affine Kurven/Monomiale Kurvenabbildung/Ist Normalisierung/Fakt -->

### Theorem: normalisation of a monomial curve {#br-ak-2025-2026-l20-thm-04}

Let

$$
M\subseteq\mathbb N
$$

be a submonoid generated by relatively prime numbers $e_1,\ldots,e_n$, and let

$$
K[M]\subseteq K[T]
$$

be the associated extension of monoid rings. Then $K[T]$ is the normalisation of $K[M]$.

In other words, the monomial map

$$
\mathbb A_K^1\longrightarrow K\!-\!\operatorname{Spek}(K[M])
$$

is a normalisation.

#### Proof {#br-ak-2025-2026-l20-thm-04-proof}

We have

$$
K[M]=K[T^{e_1},\ldots,T^{e_n}]\subseteq K[T].
$$

Since the exponents are relatively prime, they generate $1$. Multiplicatively, this means that there is a monomial in these powers, allowing negative exponents, that equals $T$. Thus $T$ is a quotient of elements of $K[M]$, and the two fields of fractions are equal.

On the other hand, $T$ satisfies an equation of integral dependence over $K[M]$, for example

$$
X^{e_1}-T^{e_1}=0.
$$

Here $X$ is the polynomial variable, whereas $T^{e_1}$ is a coefficient in $K[M]$. Since $K[T]$ is normal—indeed, it is a unique factorisation domain because it is a principal ideal domain—it is the normalisation of $K[M]$.

**Edition note:** the source uses $T$ both for the polynomial variable and for the element being tested, adding the qualification “read correctly”. This edition distinguishes them by naming the polynomial variable $X$; the mathematical content is unchanged.

Monomial curves thus provide many examples in which normalisation is a bijection at the level of $K$-spectra. The map is also a homeomorphism for the Zariski topology, which is very simple in the curve case. Nevertheless, it would be wrong to regard the two curves as identical. If $e_i\ne1$ for every $i$, normalisation is not a bijection at the ring level. In algebraic geometry, we must not look only at the set-theoretic or topological shape of the zero locus; we must not forget the underlying rings and equations. The difference is also visible in the embedded situation, where Neil's parabola has a cusp.

Normalisation gives a new interpretation of the degree of singularity of a monomial curve.

<!-- upstream_entity: Numerische Halbgruppe/Teilerfremde Erzeuger/Singularitätsgrad/Beziehung zur Normalisierung/Fakt -->

### Lemma: degree of singularity as a dimension of the normalisation quotient {#br-ak-2025-2026-l20-lem-02}

Let $M\subseteq\mathbb N$ be a numerical monoid defined by relatively prime generators. Let

$$
R=K[M]
$$

be its associated monoid ring and

$$
R^{\operatorname{norm}}=K[T]
$$

its normalisation. Then

$$
\delta(M)=\dim_K\bigl(R^{\operatorname{norm}}/R\bigr).
$$

#### Proof {#br-ak-2025-2026-l20-lem-02-proof}

The normalisation has the $K$-basis

$$
\{T^m\mid m\in\mathbb N\},
$$

whereas the monoid ring $K[M]$ has the $K$-basis

$$
\{T^m\mid m\in M\}.
$$

Thus the quotient vector space

$$
K[T]/K[M]
$$

has the $K$-basis

$$
\{T^m\mid m\in\mathbb N\setminus M\}.
$$

The dimension of the quotient vector space is the number of elements in a basis, namely the number of gaps in $M$. This is precisely the degree of singularity of $M$.

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
