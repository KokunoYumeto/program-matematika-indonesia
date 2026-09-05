---
title: "Lecture 13 - The open sets D(f), connectedness, and idempotent elements"
stable_id: br-ak-2025-2026-l13
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 13"
upstream_pageid: 165902
upstream_revid: 1112285
upstream_timestamp: "2026-08-21T08:10:43Z"
upstream_mediawiki_sha1: 21738279d828654cee2399253d3c1763db6476a6
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112285"
authority_manifest: authority/wikiversity/unit-13/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: dc86b4d124c7e775fb635a1f9672a8b8faadc4ff2259b0779f7bac6302d18848
lecture_xml_sha256: 400ee9f6816ba759171c717de302bced04a0445ce67afd2e0519f68c67f4559d
lecture_expanded_tex_sha256: f974398ce33ffc1b49b68dd15fdd2db5f701dcf8ecef893285e4d18d432a4e90
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-13.csv"
translation_status: complete
---

# Lecture 13: The open sets $D(f)$, connectedness, and idempotent elements {#br-ak-2025-2026-l13}

## The open sets $D(f)$ {#br-ak-2025-2026-l13-s01}

We shall show that the Zariski-open subsets

$$
D(f)\subseteq K\!-\!\operatorname{Spek}(R)
$$

are themselves homeomorphic to the $K$-spectrum of a $K$-algebra of finite
type. For this we need the notions of a multiplicative system and localisation.

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikatives System/Definition -->

### Definition: multiplicative system {#br-ak-2025-2026-l13-def-01}

Let $R$ be a commutative ring. A subset $S\subseteq R$ is called a
*multiplicative system* if it satisfies the following two properties:

1. $1\in S$;
2. if $f,g\in S$, then $fg\in S$.

<!-- upstream_entity: Kommutative Ringtheorie/Multiplikative Systeme/Potenzen eines Elementes/Beispiel -->

### Example: powers of an element {#br-ak-2025-2026-l13-exm-01}

Let $R$ be a commutative ring and $f\in R$. The powers

$$
\{f^n\mid n\in\mathbb N\}
$$

form a multiplicative system.

<!-- upstream_entity: Kommutative Ringtheorie/Nenneraufnahme für multiplikative Systeme in Integritätsbereiche/In Quotientenkörper/Definition -->

### Definition: localisation inside the field of fractions {#br-ak-2025-2026-l13-def-02}

Let $R$ be an integral domain and $S\subseteq R$ a multiplicative system
with $0\notin S$. The subring

$$
R_S:=\left\{\frac fg\mathrel{\Big|} f\in R,\ g\in S\right\}
\subseteq Q(R)
$$

is called the *localisation* of $R$ at $S$.

For localisation at a single element $f$, we simply write $R_f$ instead
of $R_{\{f^n\mid n\in\mathbb N\}}$. For the definition of localisation
for arbitrary commutative rings, see Exercise 13.1.

<!-- upstream_entity: Affine Varietäten/K-Spektrum/D(f) als K-Spek von R_f/Fakt -->

### Theorem: $D(f)$ as the $K$-spectrum of $R_f$ {#br-ak-2025-2026-l13-thm-01}

Let $K$ be a field, $R$ a $K$-algebra of finite type, and $f\in R$.
The Zariski-open set

$$
D(f)\subseteq K\!-\!\operatorname{Spek}(R)
$$

is naturally homeomorphic to $K\!-\!\operatorname{Spek}(R_f)$.

#### Proof {#br-ak-2025-2026-l13-thm-01-proof}

Consider the canonical $K$-algebra homomorphism

$$
\varphi:R\longrightarrow R_f
$$

and its spectrum map

$$
\begin{aligned}
\varphi^*:K\!-\!\operatorname{Spek}(R_f)&\longrightarrow
K\!-\!\operatorname{Spek}(R),\\
P&\longmapsto P\circ\varphi.
\end{aligned}
$$

By Theorem 12.7 this map is continuous. Since $f$ becomes a unit in $R_f$,
for every $P$ we have

$$
f(P\circ\varphi)=P(\varphi(f))\ne0.
$$

Thus the image of $\varphi^*$ lies in $D(f)$.

Conversely, take $Q\in D(f)$. Thus $Q:R\to K$ is a $K$-algebra
homomorphism with $Q(f)\ne0$. The element $Q(f)$ is a unit in $K$. By
the universal property of localisation (see Exercise 13.6), $Q$ extends
to a homomorphism $R_f\to K$. This extension is the required preimage,
so $\varphi^*$ is surjective as a map to $D(f)$.

To prove injectivity, let $P_1,P_2:R_f\to K$ be two $K$-algebra
homomorphisms whose composites with $R\to R_f$ agree. For $r\in R$
and $s\in\mathbb N$ we have

$$
P_1\!\left(\frac r{f^s}\right)
=P_1(rf^{-s})
=P_1(r)P_1(f^s)^{-1},
$$

and the same formula holds for $P_2$. Since their values on $R$ agree,
we obtain $P_1=P_2$.

Finally, the Zariski-open sets of $K\!-\!\operatorname{Spek}(R_f)$
are covered by sets $D(g)$ with $g\in R_f$. Since $f$ is a unit in
$R_f$, we may take $g\in R$. This set $D(g)$ equals

$$
(\varphi^*)^{-1}(D(gf)),
$$

where $D(gf)$ on the right is an open set in
$K\!-\!\operatorname{Spek}(R)$. Thus the bijection above is a homeomorphism.

<!-- upstream_entity: Affine Varietäten/K-Spektrum/D(f) als K-Spek von R_f/Bemerkung -->

### Remark: a closed realisation of $D(f)$ {#br-ak-2025-2026-l13-rem-01}

Theorem 13.4 says in particular that the open set

$$
D(f)\subseteq K\!-\!\operatorname{Spek}(R)
$$

is itself the $K$-spectrum of a $K$-algebra of finite type, namely
$R_f$, which is generated over $R$ by $1/f$. Since

$$
R_f\cong R[T]/(Tf-1)
$$

(see Exercise 13.4), it can be realised as a closed set in an affine
space. If

$$
R=K[X_1,\ldots,X_n]/\mathfrak a,
$$

then the surjective ring homomorphism

$$
K[X_1,\ldots,X_n,T]
\longrightarrow
\bigl(K[X_1,\ldots,X_n]/\mathfrak a\bigr)[T]
\longrightarrow
\frac{\bigl(K[X_1,\ldots,X_n]/\mathfrak a\bigr)[T]}{(Tf-1)}
\cong R_f
$$

gives a closed embedding of $D(f)$ into $\mathbb A_K^{n+1}$ by
Proposition 12.8(3). If $\psi$ is the composite inclusion

$$
D(f)\subseteq K\!-\!\operatorname{Spek}(R)\subseteq\mathbb A_K^n,
$$

this closed embedding can also be viewed as

$$
\psi\times\frac1f:
D(f)\longrightarrow\mathbb A_K^n\times\mathbb A_K^1.
$$

Here the product of varieties appears again.

<!-- upstream_entity: Affine Varietäten/K-Spektrum/Punktierte affine Gerade als Hyperbel/Beispiel -->

### Example: the punctured affine line as a hyperbola {#br-ak-2025-2026-l13-exm-02}

Continuing Remark 13.5, consider the open set

$$
D(X)=\{P\in\mathbb A_K^1\mid P\ne0\}\subset\mathbb A_K^1.
$$

This set is called the *punctured affine line*. On it, $X$ is invertible,
so the rational function $1/X$ is defined. Together with the open
inclusion $D(X)\subseteq\mathbb A_K^1$, this function gives a closed inclusion

$$
\begin{aligned}
D(X)&\longrightarrow V(XY-1)\subseteq\mathbb A_K^2,\\
x&\longmapsto\left(x,\frac1x\right).
\end{aligned}
$$

Its image is a hyperbola closed in the affine plane. Thus the punctured
affine line and this hyperbola are homeomorphic; the corresponding rings,

$$
K[X]_X=K[X,X^{-1}]
\qquad\text{and}\qquad
K[X,Y]/(XY-1),
$$

are also isomorphic.

![Two branches of the hyperbola y equals one over x in the coordinate plane](authority/assets/Hyperbola_one_over_x.svg)

*Graph of the hyperbola $y=1/x$; Ktims, [CC BY-SA
3.0](http://creativecommons.org/licenses/by-sa/3.0/).*

## Connectedness and idempotent elements {#br-ak-2025-2026-l13-s02}

We want to understand how connectedness of an affine algebraic set is
reflected in its coordinate ring, and how its connected components can be
characterised. The following example shows that a satisfactory theory
cannot be expected over a field that is not algebraically closed.

<!-- upstream_entity: Ebene algebraische Kurven/Reell/X^2+Y^2-2 und X^2+2Y^2-1/Zusammenhangseigenschaft/Beispiel -->

### Example: connectedness can change after a field extension {#br-ak-2025-2026-l13-exm-03}

As in Example 11.5, consider the two algebraic curves

$$
V_1=V(X^2+Y^2-2)
\quad\text{and}\quad
V_2=V(X^2+2Y^2-1)\subseteq\mathbb A_K^2.
$$

Their intersection is described by the ideal

$$
(X^2+Y^2-2,\,X^2+2Y^2-1)
=(Y^2+1,\,X^2-3).
$$

For $K=\mathbb R$ we have $V_1\cap V_2=\varnothing$. Consequently,

$$
V=V_1\cup V_2
$$

is disconnected; $V_1$ and $V_2$ are both its irreducible components and
its connected components. The coordinate ring of $V$ is

$$
\mathbb R[X,Y]/\bigl((X^2+Y^2-2)(X^2+2Y^2-1)\bigr).
$$

One might expect the function on $V$ that is constantly $1$ on $V_1$ and
constantly $0$ on $V_2$ to occur in the coordinate ring. This is not so.
The reason is that, after extending scalars to the complex numbers,
$V_{\mathbb C}$ is connected. Hence the complex coordinate ring has only
trivial idempotents, and this property passes to the real coordinate ring.

<!-- upstream_entity: Kommutative Ringtheorie/Idempotentes Element/Definition -->

### Definition: idempotent element {#br-ak-2025-2026-l13-def-03}

An element $e$ of a commutative ring is called *idempotent* if

$$
e^2=e.
$$

The elements $0$ and $1$ are idempotent.

<!-- upstream_entity: Kommutative Ringtheorie/Produktring/Definition -->

### Definition: product ring {#br-ak-2025-2026-l13-def-04}

Let $R_1,\ldots,R_n$ be commutative rings. The product

$$
R_1\times\cdots\times R_n,
$$

with componentwise addition and multiplication, is called the *product
ring* of the $R_i$, $i=1,\ldots,n$.

A product ring has many idempotents, namely elements each of whose
components is either $0$ or $1$.

<!-- upstream_entity: Kommutative Ringtheorie/Zusammenhängender Ring/Definition -->

### Definition: connected ring {#br-ak-2025-2026-l13-def-05}

A commutative ring $R$ is called *connected* if it has exactly two
idempotent elements, namely $0\ne1$.

![One unbroken red shape and two separate green shapes](authority/assets/Connected_and_disconnected_spaces2.svg)

*A connected topological space (red) and a disconnected space (green);
Dbc334, public domain.*

<!-- upstream_entity: Topologische Grundbegriffe/Zusammenhängender Raum/Definition -->

### Definition: connected topological space {#br-ak-2025-2026-l13-def-06}

A topological space $X$ is called *connected* if exactly two subsets of
$X$—namely $\varnothing$ and the whole space $X\ne\varnothing$—are both
open and closed.

The empty set and the whole space are always both open and closed. Such
sets are also called *boundaryless* or *clopen*. The empty topological
space is not considered connected, since it has only one subset that is
both open and closed.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektrum/Produktring/Fakt -->

### Lemma: the $K$-spectrum of a product ring {#br-ak-2025-2026-l13-lem-01}

Let $K$ be a field and $R_1,R_2$ $K$-algebras of finite type. For
$R=R_1\times R_2$ there is a natural homeomorphism

$$
K\!-\!\operatorname{Spek}(R_1\times R_2)
\cong
K\!-\!\operatorname{Spek}(R_1)
\mathbin{\uplus}
K\!-\!\operatorname{Spek}(R_2).
$$

The embeddings from right to left are induced by the projections
$R\to R_i$, $i=1,2$.

#### Proof {#br-ak-2025-2026-l13-lem-01-proof}

The projection $R_1\times R_2\to R_1$ is a $K$-algebra homomorphism
and, by Proposition 12.8(3), induces a continuous map—indeed, a closed embedding—

$$
K\!-\!\operatorname{Spek}(R_1)
\longrightarrow K\!-\!\operatorname{Spek}(R_1\times R_2).
$$

The same holds for $R_2$. Together, the two maps give a continuous map
from the disjoint union on the right to the left-hand side.

Take $P\in K\!-\!\operatorname{Spek}(R_1\times R_2)$, that is, a
$K$-algebra homomorphism $P:R_1\times R_2\to K$. Let

$$
e_1=(1,0),\qquad e_2=(0,1).
$$

Since $e_1+e_2=1$ and $e_1e_2=0$, exactly one of these elements maps
under $P$ to $0$, and the other to $1$. If, say, $e_1$ maps to $0$,
then $R_1\times0$ maps to $0$ as well. Thus $P$ factors through one of
the projections. This proves surjectivity.

For injectivity, take two distinct points in the disjoint union. If they
lie in the same component, their images remain distinct because the map
on that component is a closed embedding. If they lie in different
components, their values on $e_1$ are $0$ and $1$, respectively, so they
are also distinct as points of the spectrum of the product.

This bijective map is a homeomorphism because the two closed embeddings
combine to form a closed map.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektrum/Algebraisch abgeschlossen/Idempotente Elemente und randlose Mengen/Fakt -->

### Theorem: idempotent elements and clopen subsets {#br-ak-2025-2026-l13-thm-02}

Let $K$ be an algebraically closed field and $R$ a reduced commutative
$K$-algebra of finite type. The map

$$
e\longmapsto D(e)
$$

gives a bijection between the idempotent elements of $R$ and the subsets
of $K\!-\!\operatorname{Spek}(R)$ that are both open and closed.

#### Proof {#br-ak-2025-2026-l13-thm-02-proof}

First,

$$
D(e)=V(1-e)
$$

is both open and closed. This follows from

$$
D(e)\cup D(1-e)=D(1)=K\!-\!\operatorname{Spek}(R)
$$

and

$$
D(e)\cap D(1-e)=D(e(1-e))=D(e-e^2)=D(0)=\varnothing.
$$

Thus the map is well-defined.

Let $e_1,e_2$ be idempotents with

$$
U=D(e_1)=D(e_2).
$$

An idempotent in a field can take only the values $0$ and $1$. Thus both
$e_1$ and $e_2$ take the value $1$ on $U$ and $0$ outside $U$. They have
the same value at every point. The identity theorem for reduced algebras
over an algebraically closed field gives $e_1=e_2$. This proves injectivity.

Now let $U=D(\mathfrak a)$ be both open and closed. There is another ideal
$\mathfrak b$ with

$$
D(\mathfrak a)\cup D(\mathfrak b)
=K\!-\!\operatorname{Spek}(R),
\qquad
D(\mathfrak a)\cap D(\mathfrak b)=\varnothing.
$$

By Corollary 11.12, $\mathfrak a$ and $\mathfrak b$ together generate
the unit ideal. Thus there are $a\in\mathfrak a$ and $b\in\mathfrak b$
with $a+b=1$. Since

$$
D(a)\cap D(b)=D(ab)=\varnothing,
$$

Exercise 12.11 says that $ab$ is nilpotent. The ring $R$ is reduced, so
$ab=0$. Consequently,

$$
a=a\cdot1=a(a+b)=a^2+ab=a^2,
$$

so $a$ is idempotent. Since $D(a)\subseteq D(\mathfrak a)$,
$D(b)\subseteq D(\mathfrak b)$, and
$D(a)\cup D(b)=K\!-\!\operatorname{Spek}(R)$, we obtain

$$
U=D(\mathfrak a)=D(a).
$$

This proves surjectivity.

It follows that, over an algebraically closed field, a reduced
$K$-algebra $R$ of finite type is connected if and only if
$K\!-\!\operatorname{Spek}(R)$ is connected.

The last statement also holds without the reducedness assumption, since
idempotent elements correspond bijectively after passing to the reduction;
see Exercises 13.27 and 13.30.
