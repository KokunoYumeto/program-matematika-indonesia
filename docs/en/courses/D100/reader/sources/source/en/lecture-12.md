---
title: "Lecture 12 - The K-spectrum and its functoriality"
stable_id: br-ak-2025-2026-l12
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 12"
upstream_pageid: 165901
upstream_revid: 1112280
upstream_timestamp: "2026-08-21T08:02:32Z"
upstream_mediawiki_sha1: 7273d05cc557ce9421f7cc42b6f70b8b28ba57e2
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112280"
authority_manifest: authority/wikiversity/unit-12/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 181ce377bd68639b12511a9b1402ca03fd76c6107325195d3aa51a81b7286559
lecture_xml_sha256: 5c7011a57a38a83222a6f5ea0001d00a5a811000510bea8ebcf00754457ec81d
lecture_expanded_tex_sha256: 1cbd13d735c9eade611094b6ab0eb7b3d1678abe589bb9b1e8b5a7d25d218b07
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-12.csv"
translation_status: complete
---

# Lecture 12: The $K$-spectrum and its functoriality {#br-ak-2025-2026-l12}

> “Born to see, appointed to behold.”
>
> — Johann Wolfgang von Goethe

## The $K$-spectrum {#br-ak-2025-2026-l12-s01}

![Black-and-white portrait of Alexander Grothendieck seated](authority/assets/Alexander_Grothendieck.jpg)

*Alexander Grothendieck (1928–2014); photograph: Konrad Jacobs, Oberwolfach
Photo Collection/MFO; [CC BY-SA 2.0 de](https://creativecommons.org/licenses/by-sa/2.0/de/deed.en).*

How are affine algebraic sets and their coordinate rings related? Meaningful
answers can be expected only for infinite ground fields, because in the
finite case there are too few points. A satisfactory theory even requires
us to restrict ourselves to algebraically closed fields, or else—and this
is the viewpoint of scheme theory developed by Alexander Grothendieck—to
consider not only $K$-points, but also maximal ideals and prime ideals as points.

A first important question is the following. A $K$-algebra $R$ of finite
type has several representations, generally on an equal footing, as a
quotient ring of a polynomial algebra; say,

$$
K[X_1,\ldots,X_n]/\mathfrak a
\cong R
\cong K[X_1,\ldots,X_m]/\mathfrak b.
$$

These two representations give the zero loci

$$
V(\mathfrak a)\subseteq\mathbb A_K^n
\qquad\text{and}\qquad
V(\mathfrak b)\subseteq\mathbb A_K^m.
$$

How are these two zero loci related?

<!-- upstream_entity: Affin-algebraische Mengen/Isomorphe Algebren und Nullstellengebilde/Polynomring in einer Variablen als Gerade, eingebettete Gerade und Graph/Beispiel -->

### Example: three representations of the affine line {#br-ak-2025-2026-l12-exm-01}

Consider the polynomial ring in one variable

$$
R=K[T].
$$

The first object corresponding to it is the affine line $\mathbb A_K^1$.
But $R$ can also be obtained in quite different ways as a quotient ring of
a polynomial algebra in several variables. For example, let

$$
a\in K,\qquad a\ne0,
$$

and consider the quotient ring $K[X,Y]/(aY+bX)$. As a $K$-algebra, this
ring is isomorphic to $R$, as shown by the map

$$
\begin{aligned}
K[X,Y]/(aY+bX)&\longrightarrow K[T],\\
X&\longmapsto T,\\
Y&\longmapsto-\frac baT.
\end{aligned}
$$

The corresponding zero locus,

$$
V(aY+bX)\subset\mathbb A_K^2,
$$

is simply the line in the affine plane described by the equation

$$
Y=-\frac baX.
$$

Another way to represent the polynomial ring in one variable as a quotient
ring is

$$
K[X,Y]/(Y-P(X)),
$$

where $P(X)$ is an arbitrary polynomial in the single variable $X$. The
ring homomorphism

$$
\begin{aligned}
K[X,Y]/(Y-P(X))&\longrightarrow K[T],\\
X&\longmapsto T,\\
Y&\longmapsto P(T)
\end{aligned}
$$

again shows that there is an isomorphism with the polynomial ring in one
variable. The corresponding zero locus is simply the graph of $P(X)$.

![Black horizontal line](authority/assets/Lineline.jpg)

*Horizontal line; Astur1, public domain.*

![Graph of a red straight line in a Cartesian coordinate system](authority/assets/250px-Lineair-cartesiaans.png)

*Graph of a linear function in Cartesian coordinates; MADe, [CC BY-SA
3.0](http://creativecommons.org/licenses/by-sa/3.0/).*

![Red graph of a polynomial of degree five](authority/assets/120px-Polynomialdeg5.png)

*Graph of a polynomial of degree five; Derbeth, [CC BY-SA
3.0](http://creativecommons.org/licenses/by-sa/3.0/).*

The point of this example is that all three geometric objects are zero
loci for different quotient-ring presentations of $K[T]$. From the
viewpoint of algebraic geometry, they are three equally valid
representations of the affine line, even though they “look” different.
In algebraic geometry we must look at them in a way that makes them look
the same. What we see are merely different embeddings of the “actual,
true” geometric object intrinsically associated with a $K$-algebra:
the $K$-spectrum.

<!-- upstream_entity: Endlich erzeugte K-Algebren/K-Spektrum mit Zariski-Topologie/Definition -->

### Definition: the $K$-spectrum {#br-ak-2025-2026-l12-def-01}

For a commutative $K$-algebra $R$ of finite type, the set of all
$K$-algebra homomorphisms

$$
\operatorname{Hom}_K(R,K)
$$

is called the *$K$-spectrum* of $R$ and is denoted by

$$
K\!-\!\operatorname{Spek}(R).
$$

We regard the elements of the $K$-spectrum $K\!-\!\operatorname{Spek}(R)$
as points and usually denote them by $P$, although by definition they are
maps, namely $K$-algebra homomorphisms from $R$ to $K$. For a ring element
$f\in R$, we then write $f(P)$ rather than $P(f)$ for the value of $f$
under the ring homomorphism denoted by $P$. Indeed, it is not unusual to
regard a point as an evaluation of functions defined in some neighbourhood
of that point.

The $K$-spectrum is again equipped with a Zariski topology. For an ideal
$\mathfrak a\subseteq R$—or even an arbitrary subset of $R$—we declare
the subset

$$
V(\mathfrak a)
=\left\{P\in K\!-\!\operatorname{Spek}(R)
\mid f(P)=0\ \text{for all }f\in\mathfrak a\right\}
$$

to be closed. This does indeed define a topology; see Exercise 12.8. Its
open complement is denoted by $D(\mathfrak a)$.

<!-- upstream_entity: Polynomring über Körper/Punkte im affinen Raum und K-Algebra-Homomorphismen/Identifizierung/Fakt -->

### Lemma: points of affine space as homomorphisms {#br-ak-2025-2026-l12-lem-01}

Let $K$ be a field and $K[X_1,\ldots,X_n]$ the polynomial ring in $n$
variables. The $K$-algebra homomorphisms from $K[X_1,\ldots,X_n]$ to $K$
are naturally in bijection with the points of affine space

$$
\mathbb A_K^n=K^n.
$$

The point $(a_1,\ldots,a_n)$ corresponds to the substitution homomorphism
$X_i\mapsto a_i$. In other words,

$$
K\!-\!\operatorname{Spek}\bigl(K[X_1,\ldots,X_n]\bigr)
=\mathbb A_K^n.
$$

#### Proof {#br-ak-2025-2026-l12-lem-01-proof}

A $K$-algebra homomorphism is always determined by a set of $K$-algebra
generators. Thus the values on the variables $X_i$ determine a
$K$-algebra homomorphism from $K[X_1,\ldots,X_n]$ to $K$. Such a
substitution homomorphism is defined by $X_i\mapsto a_i$, and every
choice of values $(a_1,\ldots,a_n)$ is allowed here.

<!-- upstream_entity: Endlich erzeugte K-Algebren/K-Spektrum/von K ist Punkt/Beispiel -->

### Example: the $K$-spectrum of $K$ {#br-ak-2025-2026-l12-exm-02}

The $K$-spectrum of the $K$-algebra $K$ consists of a single point: the identity

$$
\operatorname{id}:K\longrightarrow K
$$

is the only $K$-algebra homomorphism from $K$ to $K$. In general there
may be other field automorphisms of $K$, but these are not $K$-algebra
homomorphisms.

The following theorem is crucial: it establishes a bijective relationship
between the $K$-spectrum of $R$ and the zero locus arising from a
quotient-ring presentation of $R$.

<!-- upstream_entity: Endlich erzeugte K-Algebren/K-Spektrum/Isomorph zu Einbettung/Fakt -->

### Theorem: the $K$-spectrum and zero loci {#br-ak-2025-2026-l12-thm-01}

Let $K$ be a field and $R$ a finitely generated commutative $K$-algebra
with $K$-spectrum $K\!-\!\operatorname{Spek}(R)$. Let

$$
R=K[X_1,\ldots,X_n]/\mathfrak a
$$

be a quotient-ring presentation of $R$, with quotient homomorphism

$$
\varphi:K[X_1,\ldots,X_n]\longrightarrow R
$$

and corresponding zero locus $V(\mathfrak a)\subseteq\mathbb A_K^n$.
The map

$$
\begin{aligned}
K\!-\!\operatorname{Spek}(R)&\longrightarrow\mathbb A_K^n,\\
P&\longmapsto P\circ\varphi
\end{aligned}
$$

gives a bijection between $K\!-\!\operatorname{Spek}(R)$ and
$V(\mathfrak a)$, and this bijection is a homeomorphism for the Zariski
topology.

#### Proof {#br-ak-2025-2026-l12-thm-01-proof}

First, the map above is well-defined because the composite

$$
P\circ\varphi:
K[X_1,\ldots,X_n]
\xrightarrow{\varphi}K[X_1,\ldots,X_n]/\mathfrak a
\cong R\xrightarrow{P}K
$$

defines a $K$-algebra homomorphism from the polynomial ring to $K$. By
Lemma 12.3, this is the substitution homomorphism at some
$(a_1,\ldots,a_n)$ and can be identified with the corresponding point of
affine space; explicitly,

$$
a_i=P\bigl(\varphi(X_i)\bigr).
$$

Since $P\circ\varphi$ factors through $R$, the ideal $\mathfrak a$ maps
to $0$. Thus the image point

$$
P\circ\varphi=(a_1,\ldots,a_n)
$$

lies in $V(\mathfrak a)$. We therefore obtain a map

$$
\begin{aligned}
K\!-\!\operatorname{Spek}(R)&\longrightarrow
V(\mathfrak a)\subseteq\mathbb A_K^n,\\
P&\longmapsto P\circ\varphi,
\end{aligned}
$$

which remains to be proved bijective.

Let $P_1,P_2\in K\!-\!\operatorname{Spek}(R)$ be two distinct points.
They are distinct $K$-algebra homomorphisms. Since a $K$-algebra
homomorphism is determined by its values on a set of $K$-algebra
generators, they must differ on at least one image of a variable. The
corresponding coordinate values therefore also differ, so
$P_1\circ\varphi\ne P_2\circ\varphi$. Thus the map is injective.

For surjectivity, let $(a_1,\ldots,a_n)\in V(\mathfrak a)$. The
corresponding $K$-algebra homomorphism,

$$
\begin{aligned}
K[X_1,\ldots,X_n]&\longrightarrow K,\\
X_i&\longmapsto a_i,
\end{aligned}
$$

annihilates every $F\in\mathfrak a$. Hence this ring homomorphism
factors through $K[X_1,\ldots,X_n]/\mathfrak a$. The resulting
homomorphism is the required preimage in $K\!-\!\operatorname{Spek}(R)$.

For the topological assertion, take $G\in R$, a preimage
$\widetilde G\in K[X_1,\ldots,X_n]$, and a point
$P\in K\!-\!\operatorname{Spek}(R)$ with image point
$\widetilde P=P\circ\varphi\in V(\mathfrak a)$. Then

$$
G(P)=P(G)=P\bigl(\varphi(\widetilde G)\bigr)
=(P\circ\varphi)(\widetilde G)
=\widetilde G(\widetilde P),
$$

so zero loci on the two sides also correspond. The bijection is therefore
a homeomorphism.

This theorem says that every $K$-spectrum of a $K$-algebra $R$ of finite
type can be identified with a Zariski-closed subset of some
$\mathbb A_K^n$. Such an identification is called a *closed embedding*.

<!-- upstream_entity: Endlich erzeugte K-Algebren/Nullenstellengebilde zu verschiedenen Restklassendarstellungen sind isomorph/über K-Spektrum/Fakt -->

### Corollary: topological independence of the presentation {#br-ak-2025-2026-l12-cor-01}

Let $K$ be a field and $R$ a finitely generated commutative $K$-algebra
with two quotient-ring presentations

$$
R\cong K[X_1,\ldots,X_n]/\mathfrak a
\qquad\text{and}\qquad
R\cong K[X_1,\ldots,X_m]/\mathfrak b,
$$

and corresponding zero loci

$$
V(\mathfrak a)\subseteq\mathbb A_K^n
\qquad\text{and}\qquad
V(\mathfrak b)\subseteq\mathbb A_K^m.
$$

With their induced Zariski topologies, these two zero loci are homeomorphic.

#### Proof {#br-ak-2025-2026-l12-cor-01-proof}

By Theorem 12.5, both zero loci are homeomorphic to
$K\!-\!\operatorname{Spek}(R)$, and hence also to each other.

If $R$ is the zero ring, its $K$-spectrum is empty. If $K$ is not
algebraically closed, the spectrum of other rings can also be empty.
However, if $K$ is algebraically closed and $R\ne0$, the spectrum is
nonempty. Under this assumption there is again a Hilbert Nullstellensatz;
see Exercise 12.10.

## The $K$-spectrum as a functor {#br-ak-2025-2026-l12-s02}

<!-- upstream_entity: Affine Varietäten/K-Spektren als Funktor/Fakt -->

### Theorem: the spectrum map {#br-ak-2025-2026-l12-thm-02}

Let $K$ be a field, let $R$ and $S$ be commutative $K$-algebras of finite
type, and let

$$
\varphi:R\longrightarrow S
$$

be a $K$-algebra homomorphism. It induces a map

$$
\begin{aligned}
\varphi^*:K\!-\!\operatorname{Spek}(S)&\longrightarrow
K\!-\!\operatorname{Spek}(R),\\
P&\longmapsto P\circ\varphi.
\end{aligned}
$$

This map is continuous for the Zariski topology.

#### Proof {#br-ak-2025-2026-l12-thm-02-proof}

The existence of the map is clear: to the $K$-algebra homomorphism
$P:S\to K$ we assign the composite

$$
R\xrightarrow{\varphi}S\xrightarrow{P}K.
$$

The inverse image of the open set
$D(f)\subseteq K\!-\!\operatorname{Spek}(R)$ is

$$
\begin{aligned}
(\varphi^*)^{-1}(D(f))
&=\{P\in K\!-\!\operatorname{Spek}(S)
       \mid\varphi^*(P)\in D(f)\}\\
&=\{P\in K\!-\!\operatorname{Spek}(S)
       \mid P\circ\varphi\in D(f)\}\\
&=\{P\in K\!-\!\operatorname{Spek}(S)
       \mid(P\circ\varphi)(f)\ne0\}\\
&=\{P\in K\!-\!\operatorname{Spek}(S)
       \mid P(\varphi(f))\ne0\}\\
&=D(\varphi(f)).
\end{aligned}
$$

Thus inverse images of open sets are again open, and the map is continuous.

The map $\varphi^*$ introduced in Theorem 12.7 is called the *spectrum
map* associated with $\varphi$.

<!-- upstream_entity: Endlich erzeugte K-Algebren/K-Spektren als Funktor/Verschiedene Homomorphismen/Fakt -->

### Proposition: some forms of spectrum maps {#br-ak-2025-2026-l12-prop-01}

Let $K$ be a field and $\varphi:R\to S$ a $K$-algebra homomorphism
between $K$-algebras of finite type, with associated spectrum map
$\varphi^*$. The following statements hold.

1. For a $K$-algebra homomorphism $P:R\to K$, the induced spectrum map
   $P^*$ is the map taking the unique point

   $$
   \{\operatorname{id}\}=K\!-\!\operatorname{Spek}(K)
   $$

   to the point $P\in K\!-\!\operatorname{Spek}(R)$.
2. The substitution homomorphism defined by $F\in R$,

   $$
   \begin{aligned}
   \varphi:K[T]&\longrightarrow R,\\
   T&\longmapsto F,
   \end{aligned}
   $$

   induces the spectrum map

   $$
   \begin{aligned}
   \varphi^*:K\!-\!\operatorname{Spek}(R)&\longrightarrow
   K\!-\!\operatorname{Spek}(K[T])=\mathbb A_K^1,\\
   P&\longmapsto F(P).
   \end{aligned}
   $$
3. If $\varphi:R\to S$ is surjective, then the spectrum map

   $$
   \varphi^*:K\!-\!\operatorname{Spek}(S)\longrightarrow
   K\!-\!\operatorname{Spek}(R)
   $$

   is a closed embedding with image $V(\ker\varphi)$.
4. The spectrum map associated with a surjective map

   $$
   K[X_1,\ldots,X_n]\longrightarrow S
   $$

   agrees with the map

   $$
   \varphi^*:K\!-\!\operatorname{Spek}(S)\longrightarrow
   K\!-\!\operatorname{Spek}(K[X_1,\ldots,X_n])
   \cong\mathbb A_K^n
   $$

   defined in Theorem 12.5.
5. Let $F_i\in K[X_1,\ldots,X_n]$ for $i=1,\ldots,m$, and let

   $$
   \begin{aligned}
   \varphi:K[Y_1,\ldots,Y_m]&\longrightarrow K[X_1,\ldots,X_n],\\
   Y_i&\longmapsto F_i
   \end{aligned}
   $$

   be the associated substitution homomorphism. Under the identification
   in Lemma 12.3, the spectrum map

   $$
   \varphi^*:\mathbb A_K^n
   =K\!-\!\operatorname{Spek}(K[X_1,\ldots,X_n])
   \longrightarrow
   \mathbb A_K^m
   =K\!-\!\operatorname{Spek}(K[Y_1,\ldots,Y_m])
   $$

   agrees with the direct polynomial map

   $$
   (x_1,\ldots,x_n)\longmapsto
   \bigl(F_1(x_1,\ldots,x_n),\ldots,F_m(x_1,\ldots,x_n)\bigr).
   $$

#### Proof {#br-ak-2025-2026-l12-prop-01-proof}

(1) follows from $\operatorname{id}\circ P=P$.

For (2), under the composite

$$
K[T]\xrightarrow{\varphi}R\xrightarrow{P}K,
$$

$T$ is sent to $P(F)=F(P)$.

(3) rests on considerations similar to those in the proof of Theorem
12.5; these also prove (4). For (5), see Exercise 12.18.

Statement (2) says in particular that the elements of the ring $R$ can
be regarded as functions from the $K$-spectrum
$K\!-\!\operatorname{Spek}(R)$ to $\mathbb A_K^1$. Thus we have
introduced a geometric object that realises ring elements as functions.

## Further properties of the $K$-spectrum {#br-ak-2025-2026-l12-s03}

<!-- upstream_entity: Affine Varietäten/K-Spektren/Polynomring und affine Gerade/Fakt -->

### Lemma: adjoining one variable {#br-ak-2025-2026-l12-lem-02}

Let $K$ be a field and $R$ a finitely generated commutative $K$-algebra.
Then there is a natural bijection

$$
K\!-\!\operatorname{Spek}(R[X])
\cong K\!-\!\operatorname{Spek}(R)\times\mathbb A_K^1.
$$

#### Proof {#br-ak-2025-2026-l12-lem-02-proof}

A $K$-algebra homomorphism $R[T]\to K$ induces a $K$-algebra
homomorphism $R\to K$, while $T$ maps to a particular element $a\in K$.
Conversely, these two data uniquely determine a $K$-algebra homomorphism
$R[T]\to K$.

Warning: the statement above gives only a natural bijection at the level
of points. If the product set on the right is equipped with the product
topology, this bijection need not be a homeomorphism with the Zariski topology
on the left. In particular, for an infinite field $K$,

$$
\mathbb A_K^2=\mathbb A_K^1\times\mathbb A_K^1,
$$

but the Zariski topology on the affine plane is not the product of the
Zariski topology on the affine line with itself.

> **Edition note:** The source states the failure of homeomorphism without
> qualification. The general statement is “need not”: for example, when
> $R=K$ the bijection is a homeomorphism. The affine-plane counterexample
> requires $K$ infinite; over a finite field all these finite $K$-spectra
> are discrete.

### Remark: products via tensor products {#br-ak-2025-2026-l12-rem-01}

If

$$
X=K\!-\!\operatorname{Spek}(R)
\qquad\text{and}\qquad
Y=K\!-\!\operatorname{Spek}(S),
$$

then the product set $X\times Y$ can also be represented as the
$K$-spectrum of a $K$-algebra, namely

$$
X\times Y\cong
K\!-\!\operatorname{Spek}(R\otimes_K S),
$$

where $\otimes$ denotes the tensor product. We shall not discuss this in
detail. To give some intuition, however, take

$$
R=K[X_1,\ldots,X_n]/\mathfrak a
\qquad\text{and}\qquad
S=K[Y_1,\ldots,Y_m]/\mathfrak b.
$$

Then

$$
R\otimes_K S
\cong
K[X_1,\ldots,X_n,Y_1,\ldots,Y_m]/(\mathfrak a+\mathfrak b).
$$

With this *ad hoc* definition, it is not yet clear that the result is
independent of the chosen quotient-ring presentations.
