---
title: "Lecture 17 - Monoid Rings and Groups of Differences"
stable_id: br-ak-2025-2026-l17
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 17"
upstream_pageid: 165906
upstream_revid: 1112301
upstream_timestamp: "2026-08-21T08:52:16Z"
upstream_mediawiki_sha1: da4e92351c0197e66d117d85306d1578900dc81b
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112301"
authority_manifest: authority/wikiversity/unit-17/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: c6747335c58fb3b4303cf3095705df7f991143f79d2d3598582a1cc8c99bef1a
lecture_xml_sha256: 27edcd8d46ff9a0d3b04e3b7996caec8b5b73076a7717499b6219d2e65edb09d
lecture_expanded_tex_sha256: 6afb4b6a5e3db0455481dcb68af9b8ecdff5d42d979f53399b41830108c00084
license: "CC BY-SA 4.0 for translated course text; official PDF rights are recorded in authority/ASSET_CLOSURE-unit-17.json"
translation_status: complete
---

# Lecture 17: Monoid Rings and Groups of Differences {#br-ak-2025-2026-l17}

Having developed the theory sufficiently far, we now turn to a broad
class of examples: monoid rings.

## Monoid rings {#br-ak-2025-2026-l17-s01}

<!-- upstream_entity: Kommutative Ringtheorie/Monoidringe/Definition -->

### Definition: monoid rings {#br-ak-2025-2026-l17-def-01}

Let $M$ be a commutative monoid written additively and let $R$ be a
commutative ring. The *monoid ring* $R[M]$ is constructed as follows.
As an $R$-module,

$$
R[M]=\bigoplus_{m\in M}Re_m,
$$

that is, $R[M]$ is the free module with basis

$$
(e_m)_{m\in M}.
$$

Multiplication on basis elements is defined by

$$
e_m\cdot e_k:=e_{m+k}
$$

and extended distributively to all of $R[M]$. The identity $0\in M$
determines the multiplicative identity

$$
1=e_0.
$$

<!-- upstream_entity: Kommutative Ringtheorie/Monoidringe/Grundeigenschaften/Bemerkung -->

### Remark: the form of elements and multiplication {#br-ak-2025-2026-l17-rem-01}

Every element of a monoid ring has a unique expression

$$
f=\sum_{m\in\widetilde M}a_me_m,
$$

where $\widetilde M\subseteq M$ is finite and $a_m\in R$. Addition is
componentwise, while multiplication is explicitly given by

$$
\begin{aligned}
fg
&=\left(\sum_{m\in\widetilde M}a_me_m\right)
  \left(\sum_{k\in\overline M}b_ke_k\right)\\
&=\sum_{\ell\in M}
  \left(\sum_{\substack{m+k=\ell\\m\in\widetilde M,\ k\in\overline M}}
  a_mb_k\right)e_\ell.
\end{aligned}
$$

Only finitely many $\ell$ occur, and each inner sum is also finite. This
is what distributive extension means in the definition above.

It is customary to write $X^m$ in place of $e_m$, where $X$ is a
suggestive symbol reminiscent of a variable. The rule

$$
X^mX^k=X^{m+k}
$$

resembles the corresponding rule for polynomial rings. Indeed, polynomial
rings are special cases of monoid rings, and this notation comes from
that case. A full proof that the construction really gives a ring with
associative and distributive multiplication also works as in the
polynomial-ring case. Usually we simply write

$$
\sum_{m\in M}a_mX^m,
$$

with almost all $a_m=0$. Elements of the form $X^m$ are called
*monomials*. The map

$$
\begin{aligned}
M&\longrightarrow R[M],\\
m&\longmapsto X^m
\end{aligned}
$$

is a monoid homomorphism, using the multiplicative monoid structure on
the right.

A monoid ring is naturally an $R$-algebra: an element $f\in R$, regarded
in $R[M]$, is

$$
f=f\cdot1=fX^0.
$$

Thus $R$ is also called the *base ring* of the monoid ring. Monoid rings
are already interesting when the base ring is a field.

<!-- upstream_entity: Kommutative Monoidringe/Polynomring als Monoidring (mehrere Variablen)/Beispiel -->

### Example: polynomial rings {#br-ak-2025-2026-l17-exa-01}

Let $n$ be a natural number and let

$$
M=\mathbb N^n.
$$

Thus $M$ is the direct product of $n$ copies of the natural numbers.

Every $k\in\mathbb N^n$ is an $n$-tuple $k=(k_1,\ldots,k_n)$ with
$k_i\in\mathbb N$, and can be written as

$$
(k_1,\ldots,k_n)
=k_1(1,0,\ldots,0)+\cdots+k_n(0,\ldots,0,1).
$$

Writing

$$
X_i=X^{e_i}=X^{(0,\ldots,0,1,0,\ldots,0)}
$$

for the monomial corresponding to the $i$th basis element, we obtain

$$
X^k=X_1^{k_1}X_2^{k_2}\cdots X_n^{k_n}.
$$

Thus the monoid ring of $\mathbb N^n$ over $R$ is precisely the
polynomial ring in $n$ variables. In particular,

$$
R[\mathbb N]=R[X].
$$

The monoid ring of the trivial monoid $\{0\}$ is the base ring itself.

<!-- upstream_entity: Kommutative Monoidringe/Laurentring als Monoidring (mehrere Variablen)/Beispiel -->

### Example: Laurent rings {#br-ak-2025-2026-l17-exa-02}

Let $n$ be a natural number and let

$$
M=\mathbb Z^n.
$$

Thus $M$ is the direct product of $n$ copies of the integers.

The monoid $M$ is the free abelian group of rank $n$. Every
$k\in\mathbb Z^n$ is an $n$-tuple $k=(k_1,\ldots,k_n)$ with
$k_i\in\mathbb Z$, which can be written as

$$
(k_1,\ldots,k_n)
=k_1(1,0,\ldots,0)+\cdots+k_n(0,\ldots,0,1).
$$

As in Example 17.3, the corresponding monomial can be written uniquely as

$$
X^k=X_1^{k_1}X_2^{k_2}\cdots X_n^{k_n},
\qquad X_i=X^{e_i}.
$$

Hence

$$
R[M]
=R[X_1,\ldots,X_n,X_1^{-1},\ldots,X_n^{-1}].
$$

This ring is isomorphic to the localisation of the polynomial ring at the
product of all the variables:

$$
R[M]
=R[X_1,\ldots,X_n,X_1^{-1},\ldots,X_n^{-1}]
=R[X_1,\ldots,X_n]_{X_1\cdots X_n}.
$$

It is called the *Laurent ring* in $n$ variables over $R$.

## The universal property of monoid rings {#br-ak-2025-2026-l17-s02}

<!-- upstream_entity: Kommutative Monoidringe/Universelle Eigenschaft für R-Algebren mit Monoidabbildung/Fakt -->

### Theorem: the universal property {#br-ak-2025-2026-l17-thm-01}

Let $R$ be a commutative ring, let $M$ be a commutative monoid, let $B$
be a commutative $R$-algebra, and let

$$
\varphi:M\longrightarrow(B,\cdot,1)
$$

be a monoid homomorphism. Then there is exactly one $R$-algebra
homomorphism

$$
\widetilde\varphi:R[M]\longrightarrow B
$$

making the following diagram commute:

$$
\begin{matrix}
M&\longrightarrow&R[M]\\
&\searrow&\downarrow\widetilde\varphi\\
&&B.
\end{matrix}
$$

#### Proof {#br-ak-2025-2026-l17-thm-01-proof}

An $R$-module homomorphism

$$
\widetilde\varphi:R[M]\longrightarrow B
$$

is determined by the images of the basis elements $(X^m)_{m\in M}$. The
diagram commutes exactly when

$$
\widetilde\varphi(X^m)=\varphi(m).
$$

This condition determines the map uniquely and immediately makes it an
$R$-module homomorphism. We need only check multiplication. First,

$$
\widetilde\varphi(1)
=\widetilde\varphi(X^0)
=\varphi(0)
=1.
$$

Moreover,

$$
\begin{aligned}
\widetilde\varphi(X^mX^k)
&=\widetilde\varphi(X^{m+k})\\
&=\varphi(m+k)\\
&=\varphi(m)\varphi(k)\\
&=\widetilde\varphi(X^m)\widetilde\varphi(X^k).
\end{aligned}
$$

Thus the map respects multiplication on monomials. For

$$
f=\sum_{m\in M}a_mX^m,
\qquad
g=\sum_{k\in M}b_kX^k,
$$

with finite support, we obtain

$$
\begin{aligned}
\widetilde\varphi(fg)
&=\widetilde\varphi\!\left(
  \sum_{\ell\in M}\left(\sum_{m+k=\ell}a_mb_k\right)X^\ell
  \right)\\
&=\sum_{\ell\in M}\left(\sum_{m+k=\ell}a_mb_k\right)
  \varphi(\ell)\\
&=\sum_{m,k\in M}a_mb_k\varphi(m)\varphi(k)\\
&=\left(\sum_{m\in M}a_m\varphi(m)\right)
  \left(\sum_{k\in M}b_k\varphi(k)\right)\\
&=\widetilde\varphi(f)\widetilde\varphi(g).
\end{aligned}
$$

Consequently $\widetilde\varphi$ is a ring homomorphism.

<!-- upstream_entity: Kommutative Monoidringe/Funktorialität im Monoid/Fakt -->

### Corollary: functoriality in the monoid {#br-ak-2025-2026-l17-cor-01}

Let $R$ be a commutative ring, let $M,N$ be commutative monoids, and let

$$
\varphi:M\longrightarrow N
$$

be a monoid homomorphism. It induces an $R$-algebra homomorphism

$$
\begin{aligned}
\widetilde\varphi:R[M]&\longrightarrow R[N],\\
X^m&\longmapsto X^{\varphi(m)}.
\end{aligned}
$$

#### Proof {#br-ak-2025-2026-l17-cor-01-proof}

Apply Theorem 17.5 to the $R$-algebra $B=R[N]$ and the composite monoid
homomorphism

$$
M\stackrel{\varphi}{\longrightarrow}N\longrightarrow R[N].
$$

<!-- upstream_entity: Kommutative Monoidringe/Universelle Eigenschaft für R-Algebren mit Monoidabbildung/Polynomring als Spezialfall/Bemerkung -->

### Remark: substitution from a polynomial algebra {#br-ak-2025-2026-l17-rem-02}

A family $(m_i)_{i\in I}$ in a monoid $M$ determines a monoid homomorphism

$$
\mathbb N^{(I)}\longrightarrow M
$$

sending the $i$th basis element $e_i$ to $m_i$. When
$I=\{1,\ldots,n\}$ is finite, Corollary 17.6 gives an $R$-algebra
homomorphism

$$
R[\mathbb N^n]=R[X_1,\ldots,X_n]\longrightarrow R[M].
$$

This is the substitution homomorphism given by

$$
X_i\longmapsto X^{m_i}.
$$

<!-- upstream_entity: Kommutative Monoidringe/R-wertige Punkte/Definition -->

### Definition: ring-valued points {#br-ak-2025-2026-l17-def-02}

For a commutative monoid $M$ and a commutative ring $R$, a monoid
homomorphism

$$
M\longrightarrow(R,\cdot,1)
$$

is called an *$R$-valued point* of $M$.

<!-- upstream_entity: Kommutative Monoidringe/R-wertige Punkte/Bemerkung -->

### Remark: monoid points and the $K$-spectrum {#br-ak-2025-2026-l17-rem-03}

By Theorem 17.5, an $R$-valued point of $M$ is equivalent to an
$R$-algebra homomorphism from $R[M]$ to $R$. This terminology is
especially common when the base ring is a field $K$. In that case,

$$
\begin{aligned}
K\!-\!\operatorname{Spek}(K[M])
&=\operatorname{Hom}^{\mathrm{alg}}_K(K[M],K)\\
&=\operatorname{Mor}_{\mathrm{mon}}(M,K)\\
&=\{K\text{-valued points of }M\}.
\end{aligned}
$$

Thus the $K$-spectrum already has a simple, purely multiplicative
description at the monoid level. As we shall see, this means that the
$K$-spectra of monoid rings generally have much clearer descriptions than
spectra of rings in general. Nevertheless, the monoid ring remains
indispensable for defining the Zariski topology and the sheaf of algebraic
functions on $K\!-\!\operatorname{Spek}(K[M])$.

<!-- upstream_entity: Kommutative Monoidringe/K-wertige Punkte/Gleichungen/Bemerkung -->

### Remark: generators and binomial relations {#br-ak-2025-2026-l17-rem-04}

A commutative monoid is often described by finitely many generators
$e_1,\ldots,e_r$ together with binomial relations of the form

$$
n_1e_1+\cdots+n_re_r=m_1e_1+\cdots+m_re_r,
\qquad n_i,m_i\in\mathbb N.
$$

A $K$-valued point

$$
\varphi:M\longrightarrow K
$$

is uniquely determined by $a_i=\varphi(e_i)$. For every binomial relation
holding in $M$, these values must satisfy

$$
a_1^{n_1}\cdots a_r^{n_r}
=a_1^{m_1}\cdots a_r^{m_r}.
$$

<!-- upstream_entity: Kommutative Monoidringe/Funktorialität im Monoid/Surjektivität/Fakt -->

### Lemma: injectivity and surjectivity {#br-ak-2025-2026-l17-lem-01}

Let $R$ be a nonzero commutative ring, let $M,N$ be commutative monoids,
and let

$$
\varphi:M\longrightarrow N
$$

be a monoid homomorphism. The map $\varphi$ is injective (respectively,
surjective) if and only if the associated $R$-algebra homomorphism

$$
\widetilde\varphi:R[M]\longrightarrow R[N]
$$

is injective (respectively, surjective).

#### Proof {#br-ak-2025-2026-l17-lem-01-proof}

Suppose $\varphi$ is injective and

$$
\widetilde\varphi\!\left(\sum_{m\in M}a_mX^m\right)
=\sum_{m\in M}a_mX^{\varphi(m)}=0.
$$

Since all the $\varphi(m)$ are distinct, every $a_m=0$. Conversely, if
$\varphi$ is not injective, take $m\ne k$ with $\varphi(m)=\varphi(k)$.
Then

$$
\widetilde\varphi(X^m)=\widetilde\varphi(X^k),
\qquad X^m\ne X^k,
$$

so $\widetilde\varphi$ is not injective.

If $\varphi$ is surjective, then for any element
$\sum_{n\in N}a_nX^n\in R[N]$, choose a preimage $m_n\in M$ of $n$.
The element $\sum_{n\in N}a_nX^{m_n}$ is a preimage of it. Conversely,
if $n\in N$ is not in the image of $\varphi$, the nonzero monomial $X^n$
cannot be in the image of $\widetilde\varphi$.

<!-- upstream_entity: Kommutative Monoidringe/Erzeugendensystem für Monoid und Polynomring/Fakt -->

### Corollary: generating sets {#br-ak-2025-2026-l17-cor-02}

Let $R$ be a nonzero commutative ring, let $M$ be a commutative monoid,
and let $(m_i)_{i\in I}$ be a family of elements of $M$. The family
$(m_i)_{i\in I}$ generates $M$ as a monoid if and only if
$(X^{m_i})_{i\in I}$ generates $R[M]$ as an $R$-algebra.

#### Proof {#br-ak-2025-2026-l17-cor-02-proof}

The family $(m_i)_{i\in I}$ generates $M$ exactly when the monoid
homomorphism

$$
\mathbb N^{(I)}\longrightarrow M
$$

is surjective. By Lemma 17.11, this is equivalent to surjectivity of

$$
\begin{aligned}
R[X_i\mid i\in I]&\longrightarrow R[M],\\
X_i&\longmapsto X^{m_i},
\end{aligned}
$$

which says precisely that the $X^{m_i}$ generate $R[M]$ as an $R$-algebra.

<!-- upstream_entity: Kommutative Monoidringe/Funktorialität im Ring/Fakt -->

### Corollary: functoriality in the base ring {#br-ak-2025-2026-l17-cor-03}

Let $R$ be a commutative ring, let $S$ be an $R$-algebra, and let $M$ be
a commutative monoid. There is a natural $R$-algebra homomorphism

$$
\begin{aligned}
R[M]&\longrightarrow S[M],\\
\sum_{m\in M}a_mX^m&\longmapsto\sum_{m\in M}a_mX^m,
\end{aligned}
$$

where coefficients from $R$ are viewed through the structure map $R\to S$.

#### Proof {#br-ak-2025-2026-l17-cor-03-proof}

Apply Theorem 17.5 to the $R$-algebra $S[M]$ and the natural monoid
homomorphism $M\to S[M]$.

## The group of differences of a monoid {#br-ak-2025-2026-l17-s03}

We want to know when a monoid ring is an integral domain (which is possible
only when the base ring is an integral domain) and how its fraction field
can then be described. In the fraction field, every nonzero element must
be invertible, in particular the monomials $X^m$. It is therefore natural
to look for an additive group containing $M$.

**Edition note:** after consistently using $X^m$ for monomials, the source
prints $T^m$ in the last sentence. This edition retains the notation $X^m$
established in this lecture.

<!-- upstream_entity: Kommutative Monoidtheorie/Differenzengruppe zu Monoid/Definition -->

### Definition: the group of differences {#br-ak-2025-2026-l17-def-03}

Let $M$ be a commutative monoid. The set of *formal differences*

$$
\Gamma(M)=\{m-n\mid m,n\in M\}
$$

is equipped with addition

$$
(m_1-n_1)+(m_2-n_2)
:=(m_1+m_2)-(n_1+n_2)
$$

and the identification

$$
m_1-n_1=m_2-n_2
$$

whenever there is a $u\in M$ such that

$$
u+m_1+n_2=u+m_2+n_1.
$$

The resulting object $\Gamma(M)$ is called the *group of differences* of $M$.

Exercise 17.13 asks the reader to show that it really is a group. The
construction is modelled on the construction of fraction fields, with
multiplicative notation replaced by additive notation. The construction
of the group of differences is actually more elementary. For example,

$$
\Gamma(\mathbb N)=\mathbb Z.
$$

There is a natural monoid homomorphism

$$
\begin{aligned}
M&\longrightarrow\Gamma(M),\\
m&\longmapsto m-0.
\end{aligned}
$$

We usually write simply $m$ for $m-0$. This map need not be injective,
because the extra element $u$ may occur in the identification above, and
this cannot be avoided. We now characterise the monoids for which that
extra element is unnecessary.

<!-- upstream_entity: Kommutative Monoidtheorie/Monoid mit Kürzungsregel/Definition -->

### Definition: the cancellation law {#br-ak-2025-2026-l17-def-04}

A commutative monoid $M$ is said to satisfy the *cancellation law* (or to
be a *cancellative monoid*) if

$$
m+n=m+k,
\qquad m,n,k\in M,
$$

always implies $n=k$.

For such a monoid, the map $M\to\Gamma(M)$ is injective; see Exercise 17.16.

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
