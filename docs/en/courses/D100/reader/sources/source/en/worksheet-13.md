---
title: "Worksheet 13 - Localisation, connectedness, and idempotent elements"
stable_id: br-ak-2025-2026-w13
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 13"
upstream_pageid: 165932
upstream_revid: 1065092
upstream_timestamp: "2026-01-15T10:23:01Z"
upstream_mediawiki_sha1: 20d30f0f2a09974c436262bbe20c0fab3fa34faa
source_url: "https://de.wikiversity.org/w/index.php?oldid=1065092"
authority_manifest: authority/wikiversity/unit-13/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: dc86b4d124c7e775fb635a1f9672a8b8faadc4ff2259b0779f7bac6302d18848
worksheet_xml_sha256: 1882e3d182183429492f2a2d942797e85a5c970c160c7fae461ba14d51e1f0aa
worksheet_expanded_tex_sha256: 353bf5a5b4742d09274f33b3865f70714982be04fc32e22f4d484fa9aa64ba7b
exercise_map: authority/wikiversity/unit-13/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: f954f09c996c8aa22f94ec826a1503b135a7b4fb9f9e0d5d6ff21f36a519e52a
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 13 {#br-ak-2025-2026-w13}

## Practice exercises {#br-ak-2025-2026-w13-practice}

<!-- upstream_entity: Nenneraufnahme/Mit Nullteilern/Begriff/Aufgabe -->

### Exercise 13.1 {#br-ak-2025-2026-w13-ex-01}

Let $R$ be a commutative ring and $S\subseteq R$ a multiplicative system.
The localisation $R_S$ is defined step by step as follows. First, let $M$
be the set of formal fractions with denominator in $S$, namely

$$
M=\left\{\frac rs\mathrel{\Big|}r\in R,\ s\in S\right\}.
$$

Show that

$$
\frac rs\sim\frac{r'}{s'}
\quad\Longleftrightarrow\quad
\text{there is }t\in S\text{ with }trs'=tr's
$$

defines an equivalence relation on $M$. Denote its set of equivalence
classes by $R_S$. Define a ring structure on $R_S$ and a ring
homomorphism $R\to R_S$.

<!-- upstream_entity: Nenneraufnahme/Ist Unterring/Umkehrung/Aufgabe -->

### Exercise 13.2 {#br-ak-2025-2026-w13-ex-02}

Let $R$ be an integral domain and $S\subseteq R$ a multiplicative system
with $0\notin S$.

1. Show that the localisation

   $$
   R_S:=\left\{\frac fg\mathrel{\Big|}f\in R,\ g\in S\right\}
   \subseteq Q(R)
   $$

   is a subring of $Q(R)$.
2. Show that not every subring of $Q(R)$ is a localisation.

<!-- upstream_entity: Rationale Zahlen/Unterringe/Überabzählbar/Aufgabe -->

### Exercise 13.3 ★ {#br-ak-2025-2026-w13-ex-03}

Show that the field of rational numbers $\mathbb Q$ has uncountably many subrings.

<!-- upstream_entity: Kommutative Ringtheorie/Nenneraufnahme/Ein Element/Restklassendarstellung/Aufgabe -->

### Exercise 13.4 {#br-ak-2025-2026-w13-ex-04}

Let $R$ be a commutative ring and $f\in R$, with localisation $R_f$.
Prove the $R$-algebra isomorphism

$$
R_f\cong R[T]/(Tf-1).
$$

<!-- upstream_entity: Nenneraufnahme/f/Nilpotent/Aufgabe -->

### Exercise 13.5 {#br-ak-2025-2026-w13-ex-05}

Let $R$ be a commutative ring, $f\in R$, and $R_f$ the corresponding
localisation. Show that $f$ is nilpotent if and only if $R_f$ is the zero ring.

In the following exercises on localisation, you may assume, if you wish,
that the rings involved are integral domains.

<!-- upstream_entity: Nenneraufnahme/Universelle Eigenschaft/Fakt/Beweis/Aufgabe -->

### Exercise 13.6 ★ {#br-ak-2025-2026-w13-ex-06}

Let $R,A$ be commutative rings, $S\subseteq R$ a multiplicative system, and

$$
\varphi:R\longrightarrow A
$$

a ring homomorphism such that $\varphi(s)$ is a unit in $A$ for every
$s\in S$. Show that there is a unique ring homomorphism

$$
\widetilde\varphi:R_S\longrightarrow A
$$

extending $\varphi$.

<!-- upstream_entity: Nenneraufnahme/Verhalten von Primidealen/Aufgabe -->

### Exercise 13.7 {#br-ak-2025-2026-w13-ex-07}

Let $R$ be a commutative ring and $S\subseteq R$ a multiplicative system.
Show that the prime ideals of $R_S$ correspond precisely to the prime
ideals of $R$ disjoint from $S$.

<!-- upstream_entity: Polynomring zwei Variablen/Multiplikatives System/Eine Gleichung/Verträglichkeit/Aufgabe -->

### Exercise 13.8 ★ {#br-ak-2025-2026-w13-ex-08}

Let $K$ be a field, $R=K[X,Y]$, $S\subseteq R$ a multiplicative system,
and $F\in R$. Show that there is a unique $R$-algebra isomorphism

$$
(R/(F))_S\cong (R_S)/(F),
$$

where the localisation on the left is taken at the image of $S$ in $R/(F)$.

<!-- upstream_entity: Nenneraufnahme/Restklassenbildung/Vertauschbarkeit/Fakt/Beweis/Aufgabe -->

### Exercise 13.9 ★ {#br-ak-2025-2026-w13-ex-09}

Let $R$ be a commutative ring, $\mathfrak a\subseteq R$ an ideal, and
$S\subseteq R$ a multiplicative system. Show that there is a natural
ring isomorphism

$$
(R/\mathfrak a)_S\cong R_S/\mathfrak aR_S,
$$

where the localisation on the left is taken at the image of $S$ in
$R/\mathfrak a$.

<!-- upstream_entity: Kommutative Ringtheorie/K-Spektren/Algebraisch abgeschlossen/Nenneraufnahme zu einem Element/Faktorisierungsverhalten/Aufgabe -->

### Exercise 13.10 {#br-ak-2025-2026-w13-ex-10}

Let $K$ be an algebraically closed field, $R,S$ commutative $K$-algebras
of finite type, $f\in R$, and

$$
\varphi:R\longrightarrow S
$$

a $K$-algebra homomorphism. Show that the spectrum map $\varphi^*$
factors through $D(f)$ if and only if $\varphi(f)$ is a unit in $S$.

<!-- upstream_entity: Hilbertscher Nullstellensatz/Äquivalent/D(f) in D(g)/R g nach R f/Aufgabe -->

### Exercise 13.11 ★ {#br-ak-2025-2026-w13-ex-11}

Let $K$ be an algebraically closed field and $R$ a $K$-algebra of finite
type that is an integral domain. For $f,g\in R$, show that the following
statements are equivalent:

1. $D(f)\subseteq D(g)$;
2. there is an $R$-algebra homomorphism $R_g\to R_f$.

Also show that this equivalence fails for $K=\mathbb R$.

The following exercise uses the notion of a saturated multiplicative
system. A multiplicative system $S$ in a commutative ring $R$ is called
*saturated* if the following holds: whenever $g\in R$ divides some
$f\in S$, we also have $g\in S$.

<!-- upstream_entity: Multiplikatives System/Saturiert/Urbild der Einheitengruppe/Aufgabe -->

### Exercise 13.12 {#br-ak-2025-2026-w13-ex-12}

Let $A,B$ be commutative rings and $\varphi:A\to B$ a ring
homomorphism. Show that the inverse image

$$
\varphi^{-1}(B^\times)
$$

of the unit group is a saturated multiplicative system in $A$.

<!-- upstream_entity: Kommutative Ringtheorie/Nichtnullteiler/Sind saturiertes multiplikatives System/Aufgabe -->

### Exercise 13.13 {#br-ak-2025-2026-w13-ex-13}

Let $R$ be a commutative ring. Show that the set of all non-zero-divisors
in $R$ forms a saturated multiplicative system.

<!-- upstream_entity: Endlich erzeugte integre K-Algebra/C/Nenneraufnahme/Kein maximales Ideal überlebt/Aufgabe -->

### Exercise 13.14 ★ {#br-ak-2025-2026-w13-ex-14}

Give an example of a $\mathbb C$-algebra $R$ of finite type that is an
integral domain, and a multiplicative system $S\subseteq R$, $0\notin S$,
such that $R_S$ is not a field, but every maximal ideal of $R$ becomes
the unit ideal in $R_S$.

<!-- upstream_entity: Integritätsbereich/Zusammenhängend/Aufgabe -->

### Exercise 13.15 ★ {#br-ak-2025-2026-w13-ex-15}

Show that every integral domain is a connected ring.

<!-- upstream_entity: Kommutative Ringtheorie/Idempotent und nilpotent/Ist null/Aufgabe -->

### Exercise 13.16 {#br-ak-2025-2026-w13-ex-16}

Let $R$ be a commutative ring and $f\in R$. If $f$ is both nilpotent and
idempotent, show that $f=0$.

<!-- upstream_entity: Kommutativer Ring/nx und x^n ist 0/Aufgabe -->

### Exercise 13.17 ★ {#br-ak-2025-2026-w13-ex-17}

For every $n\ge2$, give a commutative ring $R$ and an element
$x\in R$, $x\ne0$, satisfying

$$
nx=0
\qquad\text{and}\qquad
x^n=0.
$$

<!-- upstream_entity: Kommutativer Ring/Idempotentes Element/Nenneraufnahme und Restklassenring/Aufgabe -->

### Exercise 13.18 {#br-ak-2025-2026-w13-ex-18}

Let $R$ be a commutative ring and $e\in R$ an idempotent element. Show
that there is a natural ring isomorphism

$$
R_e\cong R/(1-e).
$$

This shows once again that $D(e)$ is both open and closed.

<!-- upstream_entity: Kommutative Ringtheorie/Produktring/R_1 x 0 ist Hauptideal/Aufgabe -->

### Exercise 13.19 {#br-ak-2025-2026-w13-ex-19}

Let $R,S$ be commutative rings. Show that the subset $R\times0$ of the
product ring $R\times S$ is a principal ideal.

<!-- upstream_entity: Z/Restklassenring nach Primelementpotenz/Ist zusammenhängend/Aufgabe -->

### Exercise 13.20 ★ {#br-ak-2025-2026-w13-ex-20}

Let $p\in\mathbb Z$ be a prime number and $n\in\mathbb N$. Show that
the residue class ring $\mathbb Z/(p^n)$ has only the two trivial
idempotents, $0$ and $1$.

> **Edition note:** To have two distinct idempotents one needs $n\ge1$.
> The source allows $n\in\mathbb N$; at $n=0$ the quotient is the zero
> ring, in which $0=1$ is its only element.

<!-- upstream_entity: Polynom/Q X modulo X^4-1/Produkt von Körpern/Restklasse von X^3+X/Aufgabe -->

### Exercise 13.21 ★ {#br-ak-2025-2026-w13-ex-21}

Write the residue class ring

$$
\mathbb Q[X]/(X^4-1)
$$

as a product of fields involving only $\mathbb Q$ and $\mathbb Q[\mathrm i]$.
Write the residue class of $X^3+X$ as a tuple in this product decomposition.

<!-- upstream_entity: Polynomring K X/Produkt von Linearfaktoren/Restklassenring/Aufgabe -->

### Exercise 13.22 {#br-ak-2025-2026-w13-ex-22}

Let $K$ be a field, $a_1,\ldots,a_n\in K$ distinct elements, and

$$
F=(X-a_1)\cdots(X-a_n)\in K[X].
$$

Show that the residue class ring $K[X]/(F)$ is isomorphic to the product ring $K^n$.

<!-- upstream_entity: Polynomring K X/Algebraisch abgeschlossen/Restklassenring/Struktur/Aufgabe -->

### Exercise 13.23 {#br-ak-2025-2026-w13-ex-23}

Let $K$ be an algebraically closed field. Show that, for every nonzero
polynomial $F\in K[X]$, its residue class ring has the structure

$$
K[X]/(F)
\cong
K[T]/(T^{n_1})\times\cdots\times K[T]/(T^{n_r}).
$$

Also show that

$$
\deg(F)=n_1+\cdots+n_r.
$$

<!-- upstream_entity: K-Algebren/K-Spektren/Disjunkte Realisierung/Aufgabe -->

### Exercise 13.24 ★ {#br-ak-2025-2026-w13-ex-24}

Let $K$ be a field and

$$
A=K[X_1,\ldots,X_m]/\mathfrak a,
\qquad
B=K[Y_1,\ldots,Y_n]/\mathfrak b
$$

$K$-algebras of finite type. Set

$$
\ell=\max(m,n).
$$

Show that the $K$-spectrum of the product ring $A\times B$ can be
realised as a closed subset of $\mathbb A_K^{\ell+1}$.

<!-- upstream_entity: Topologie/Zusammenhang/Nicht zusammenhängend/Nichttriviale stetige idempotente Abbildungen/Aufgabe -->

### Exercise 13.25 {#br-ak-2025-2026-w13-ex-25}

Let $X$ be a nonempty disconnected topological space. Show that there
is a continuous function

$$
f:X\longrightarrow\mathbb R,
\qquad f\ne0,1,
$$

where $\mathbb R$ has the metric topology, that is idempotent in the
ring of continuous functions on $X$.

<!-- upstream_entity: Funktionenring/Disjunkte Zerlegung/Produktring/Aufgabe -->

### Exercise 13.26 {#br-ak-2025-2026-w13-ex-26}

Let $X$ be a topological space with a disjoint decomposition

$$
X=U\mathbin{\uplus}V
$$

into open subsets $U,V\subseteq X$. Show that the natural map

$$
\begin{aligned}
C(X,\mathbb R)&\longrightarrow C(U,\mathbb R)\times C(V,\mathbb R),\\
f&\longmapsto(f|_U,f|_V)
\end{aligned}
$$

is bijective.

<!-- upstream_entity: Idempotente Elemente/Reduktion/Injektiv/Aufgabe -->

### Exercise 13.27 ★ {#br-ak-2025-2026-w13-ex-27}

Let $R$ be a commutative ring with reduction $S$. Show that the map
sending each idempotent of $R$ to its residue class in $S$ is injective.

<!-- upstream_entity: Idempotente Elemente/Modulo nilpotentes Element/Surjektiv/Aufgabe -->

### Exercise 13.28 ★ {#br-ak-2025-2026-w13-ex-28}

Let $R$ be a commutative ring with an element $n\in R$ such that
$n^2=0$, and let

$$
S=R/(n).
$$

Show that every idempotent element $e$ of $S$ has an idempotent preimage in $R$.

<!-- upstream_entity: Reduktion/Noetherscher Ring/Induktionsschritt/Aufgabe -->

### Exercise 13.29 {#br-ak-2025-2026-w13-ex-29}

Let $R$ be a Noetherian commutative ring with reduction $S$. Show that
there is a sequence of commutative rings $R_i$, $1\le i\le n$, and
surjective ring homomorphisms

$$
\varphi_i:R_i\longrightarrow R_{i+1}
$$

such that the composite map

$$
R=R_0\longrightarrow R_1\longrightarrow\cdots
\longrightarrow R_{n-1}\longrightarrow R_n=S
$$

is the reduction map, and each $\varphi_i$ is the quotient homomorphism
$R_i\to R_i/(x_i)$ for some $x_i\in R_i$ with $x_i^2=0$.

**Edition note:** The source writes the domain and codomain of the last
quotient homomorphism as $R\to R/(x_i)$; the notation
$R_i\to R_i/(x_i)$ above follows the context of the sequence and the
element $x_i\in R_i$.

<!-- upstream_entity: Idempotente Elemente/Reduktion/Surjektiv/Aufgabe -->

### Exercise 13.30 {#br-ak-2025-2026-w13-ex-30}

Let $R$ be a commutative ring with reduction $S$. Show that the map
sending each idempotent of $R$ to its residue class in $S$ is surjective.

The following statement is a version of the Chinese remainder theorem.

<!-- upstream_entity: Kommutativer Ring/Ideal/Teilerfremd/Chinesischer Restsatz/Fakt/Beweis/Aufgabe -->

### Exercise 13.31 ★ {#br-ak-2025-2026-w13-ex-31}

Let $R$ be a commutative ring and let $\mathfrak a_j$, $j=1,\ldots,n$,
be ideals satisfying

$$
\mathfrak a_i+\mathfrak a_j=R
$$

for all $i\ne j$. Show that

$$
R/(\mathfrak a_1\cdots\mathfrak a_n)
\cong
R/\mathfrak a_1\times\cdots\times R/\mathfrak a_n.
$$

## Exercises for submission {#br-ak-2025-2026-w13-submit}

<!-- upstream_entity: Hauptidealbereich/Zwischenring in Quotientenkörper/Ist Nenneraufnahme/Aufgabe -->

### Exercise 13.32 (4 points) {#br-ak-2025-2026-w13-ex-32}

Let $R$ be a principal ideal domain with field of fractions $Q=Q(R)$.
Show that every intermediate ring

$$
R\subseteq S\subseteq Q
$$

is a localisation.

<!-- upstream_entity: Algebraische Kurve/y^2 ist x^3+x^2/D(x)/Abgeschlossene Realisierungen/Aufgabe -->

### Exercise 13.33 (5 points: 1+2+1+1) {#br-ak-2025-2026-w13-ex-33}

Consider the curve $C$ given by

$$
Y^2=X^3+X^2
$$

(see Example 6.3) and the open set $U=D(X)\subseteq C$.

1. Find a closed realisation of $U$ in $\mathbb A_K^3$.
2. Show that there is also a closed realisation in $\mathbb A_K^2$.
3. Is $U$ isomorphic to an open subset of the affine line?
4. Sketch the image curve under the map

   $$
   \begin{aligned}
   U&\longrightarrow\mathbb A_{\mathbb R}^2,\\
   (x,y)&\longmapsto\left(\frac1x,y\right).
   \end{aligned}
   $$

<!-- upstream_entity: Ebene algebraische Kurven/Parallele Geraden und Achsenkreuz/Abbildung geometrisch und algebraisch/Aufgabe -->

### Exercise 13.34 (4 points) {#br-ak-2025-2026-w13-ex-34}

Consider the union $V$ of two parallel lines and the union $W$ of the
coordinate axes. Describe a surjective map between $V$ and $W$ that is
as natural as possible—decide in which direction—both geometrically
and algebraically. Is there also a surjective polynomial map in the
opposite direction?

<!-- upstream_entity: Restklassenringe (Z)/Z/175/nilpotent idempotent/Aufgabe -->

### Exercise 13.35 (3 points) {#br-ak-2025-2026-w13-ex-35}

Determine all nilpotent elements and all idempotent elements of $\mathbb Z/(175)$.

<!-- upstream_entity: Ebene algebraische Kurven/x^2+y^2-1 und y-x^2/Schnitt als Produktring/Aufgabe -->

### Exercise 13.36 (4 points) {#br-ak-2025-2026-w13-ex-36}

Let $K$ be an algebraically closed field. Consider the intersection of
the two algebraic curves

$$
V(X^2+Y^2-1)
\qquad\text{and}\qquad
V(Y-X^2).
$$

Identify the residue class ring

$$
R=K[X,Y]/(X^2+Y^2-1,\,Y-X^2)
$$

with a product ring, and describe the quotient map $K[X,Y]\to R$ using
this identification. Determine preimages in $K[X,Y]$ for all the
idempotents of that product ring.

<!-- upstream_entity: Kommutative Ringtheorie/Nulldimensionale Algebra/Reduziert/Aufgabe -->

### Exercise 13.37 (6 points) {#br-ak-2025-2026-w13-ex-37}

Let $K$ be a field and $A$ a finite-dimensional reduced $K$-algebra.
Show that $A$ is a finite direct product of finite field extensions of $K$.

**Hint.** You may use without proof that $A$ has only finitely many prime ideals.
