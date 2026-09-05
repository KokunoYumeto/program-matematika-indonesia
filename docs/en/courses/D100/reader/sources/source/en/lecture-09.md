---
title: "Lecture 9 - Noetherian Rings, Hilbert's Basis Theorem, and Modules"
stable_id: br-ak-2025-2026-l09
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 9"
upstream_pageid: 165898
upstream_revid: 1112241
upstream_timestamp: "2026-08-20T16:29:07Z"
upstream_mediawiki_sha1: 2a702891ae21267751c7900639ef3828faf949c2
source_url: "https://de.wikiversity.org/w/index.php?oldid=1112241"
authority_manifest: authority/wikiversity/unit-09/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7cf7a956dffe854da9d021e3c74615573b91b5701d7e3b78a8f5f1aa45bfbc29
lecture_xml_sha256: 9094f97a84c8e4b46e42b993adfa31847aeb375536d16f4c39b6f35109e68e6a
lecture_expanded_tex_sha256: ae15977cb7189b8cdc2992d70193dd503725da41ad881ae1c68a681af3446e3d
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-09.csv"
translation_status: complete
---

# Lecture 9: Noetherian Rings, Hilbert's Basis Theorem, and Modules {#br-ak-2025-2026-l09}

## Noetherian rings {#br-ak-2025-2026-l09-s01}

In the next few lectures, we will further develop the algebraic side of algebraic geometry. Our first aim is to show that if $R$ is a Noetherian ring, then the polynomial ring $R[X]$ is also Noetherian (Hilbert's basis theorem). This also holds when adjoining several (finitely many) variables, in particular for polynomial rings in finitely many variables over a field. We recall the notion of a Noetherian ring.

<!-- upstream_entity: Kommutative Ringtheorie/Theorie der noetherschen kommutativen Ringe/Textabschnitt -->

### Definition: Noetherian ring {#br-ak-2025-2026-l09-def-01}

A commutative ring $R$ is called *Noetherian* if every ideal in it is finitely generated.

<!-- upstream_entity: Kommutative Ringtheorie/Noethersche Ringe/Äquivalente Formulierungen/Fakt -->

### Proposition: characterisation of Noetherian rings {#br-ak-2025-2026-l09-prop-01}

For a commutative ring $R$, the following statements are equivalent.

1. $R$ is Noetherian.
2. Every ascending chain of ideals

   $$
   \mathfrak a_1\subseteq\mathfrak a_2\subseteq\mathfrak a_3\subseteq\cdots
   $$

   becomes *stationary*; that is, there is an $n$ such that

   $$
   \mathfrak a_n=\mathfrak a_{n+1}=\cdots.
   $$

#### Proof {#br-ak-2025-2026-l09-prop-01-proof}

**(1) $\Rightarrow$ (2).** Let

$$
\mathfrak a_1\subseteq\mathfrak a_2\subseteq\mathfrak a_3\subseteq\cdots
$$

be an ascending chain of ideals in $R$. Consider its union

$$
\mathfrak a=\bigcup_{n\in\mathbb N}\mathfrak a_n,
$$

which is again an ideal in $R$. Since $R$ is Noetherian, $\mathfrak a$ is finitely generated, say

$$
\mathfrak a=(f_1,\ldots,f_k).
$$

All the $f_i$ lie in the union of the ideals $\mathfrak a_n$. Since these ideals form an ascending chain, there is an $n$ such that

$$
f_1,\ldots,f_k\in\mathfrak a_n.
$$

Then, for every $m\geq0$,

$$
(f_1,\ldots,f_k)\subseteq\mathfrak a_n
\subseteq\mathfrak a_{n+m}
\subseteq\bigcup_{n\in\mathbb N}\mathfrak a_n
\subseteq(f_1,\ldots,f_k).
$$

All these inclusions must be equalities, so the chain is stationary from $n$ onwards.

**(2) $\Rightarrow$ (1).** Let $\mathfrak a$ be an ideal in $R$. Suppose $\mathfrak a$ is not finitely generated. We can successively construct an infinite strictly ascending chain of ideals

$$
\mathfrak a_1\subset\mathfrak a_2\subset\cdots\subseteq\mathfrak a,
$$

where each $\mathfrak a_n$ is finitely generated. Suppose we have already constructed

$$
\mathfrak a_1\subset\mathfrak a_2\subset\cdots\subset\mathfrak a_n
\subseteq\mathfrak a.
$$

Since $\mathfrak a_n$ is finitely generated but $\mathfrak a$ is not, the inclusion $\mathfrak a_n\subseteq\mathfrak a$ is strict. Thus there is an element

$$
f_{n+1}\in\mathfrak a,\qquad f_{n+1}\notin\mathfrak a_n.
$$

The ideal

$$
\mathfrak a_{n+1}:=\mathfrak a_n+(f_{n+1})
$$

strictly extends the chain. This contradicts (2).

<!-- upstream_entity: Noetherscher Ring/Kommutativ/Restklassenring/Noethersch/Fakt -->

### Lemma: quotients of Noetherian rings {#br-ak-2025-2026-l09-lem-01}

If $R$ is Noetherian, every quotient ring $R/\mathfrak b$ is also Noetherian.

#### Proof {#br-ak-2025-2026-l09-lem-01-proof}

Let $\mathfrak a\subseteq R/\mathfrak b$ be an ideal and let $\widetilde{\mathfrak a}\subseteq R$ be its preimage ideal. By assumption this is finitely generated, say

$$
\widetilde{\mathfrak a}=(f_1,\ldots,f_n).
$$

The residue classes of these generators, $\bar f_1,\ldots,\bar f_n$, form a generating set for the ideal $\mathfrak a$. Indeed, for $\bar g\in\mathfrak a$, we have in $R$

$$
g=\sum_{i=1}^n r_i f_i,
$$

and hence in $R/\mathfrak b$

$$
\bar g=\sum_{i=1}^n\bar r_i\,\bar f_i.
$$

## Hilbert's basis theorem {#br-ak-2025-2026-l09-s02}

Like many fundamental results in commutative algebra, Hilbert's basis theorem, to which we now turn, goes back to David Hilbert, specifically his 1890 paper *Ueber die Theorie der algebraischen Formen* (“On the Theory of Algebraic Forms”).

![David Hilbert (1862–1943)](authority/assets/David_Hilbert_1886.jpg)

*David Hilbert (1862–1943); unknown creator (1886), Commons, public domain.*

<!-- upstream_entity: Kommutative Ringtheorie/Hilbertscher Basissatz/Fakt -->

### Hilbert's basis theorem {#br-ak-2025-2026-l09-thm-01}

If $R$ is Noetherian, the polynomial ring $R[X]$ is also Noetherian.

#### Proof {#br-ak-2025-2026-l09-thm-01-proof}

Let $\mathfrak b$ be an ideal in the polynomial ring $R[X]$. For $n\in\mathbb N$, define an ideal $\mathfrak a_n$ in $R$ by

$$
\mathfrak a_n=\left\{c\in R\mid\text{there is }F\in\mathfrak b\text{ with }
F=cX^n+c_{n-1}X^{n-1}+\cdots+c_1X+c_0\right\}.
$$

Thus $\mathfrak a_n$ consists of all leading coefficients of degree-$n$ polynomials in $\mathfrak b$. Clearly $\mathfrak a_n$ is an ideal in $R$ (here we allow $0$ as a leading coefficient). Moreover,

$$
\mathfrak a_n\subseteq\mathfrak a_{n+1},
$$

since a polynomial $F$ of degree $n$ with leading coefficient $c$ can be multiplied by $X$ to give a polynomial of degree $n+1$ with the same leading coefficient. Since $R$ is Noetherian, this ascending chain of ideals becomes stationary; choose $n$ such that

$$
\mathfrak a_n=\mathfrak a_{n+1}=\cdots.
$$

For each $i\leq n$, choose a finite generating set

$$
\mathfrak a_i=(c_{i1},\ldots,c_{ik_i}),
$$

and choose corresponding polynomials

$$
F_{ij}=c_{ij}X^i+\text{ terms of lower degree}
$$

in $\mathfrak b$ (which exist by the definition of $\mathfrak a_i$).

We claim that $\mathfrak b$ is generated by all the polynomials

$$
\left\{F_{ij}\mid 0\leq i\leq n,\ 1\leq j\leq k_i\right\}.
$$

For each $G\in\mathfrak b$, we prove by induction on its degree that it can be written as an $R[X]$-linear combination of these $F_{ij}$.

*Edition note.* The source says “$R$-linear combination” here. The factors $X^{d-i}$ in the final induction step show that $R[X]$ is intended; the assertion is finite ideal generation, not finite generation as an $R$-module.

If $G$ is constant, that is, $G\in R$, this is clear. Let $G$ have degree $d$, and suppose the statement has been proved for smaller degrees. Write

$$
G=cX^d+c_{d-1}X^{d-1}+\cdots+c_1X+c_0.
$$

We have $c\in\mathfrak a_d$, so $c$ is an $R$-linear combination of the $c_{ij}$ with $0\leq i\leq n$ and $1\leq j\leq k_i$. If $d\leq n$, then $c$ can be written as an $R$-linear combination of the $c_{dj}$, say

$$
c=\sum_{j=1}^{k_d}r_jc_{dj}.
$$

Thus

$$
G-\sum_{j=1}^{k_d}r_jF_{dj}\in\mathfrak b
$$

has smaller degree, so the induction hypothesis applies. If $d>n$, then

$$
c=\sum_{i=0,\ldots,n,\,j=1,\ldots,k_i}r_{ij}c_{ij}.
$$

Therefore

$$
G-\sum_{i=0,\ldots,n,\,j=1,\ldots,k_i}r_{ij}X^{d-i}F_{ij}
$$

also belongs to $\mathfrak b$ and has smaller degree. This completes the induction, so $\mathfrak b$ is finitely generated.

<!-- upstream_entity: Kommutative Ringtheorie/Hilbertscher Basissatz/Endliche viele Variablen/Fakt -->

### Corollary: finitely many variables {#br-ak-2025-2026-l09-cor-01}

If $R$ is Noetherian, then

$$
R[X_1,\ldots,X_n]
$$

is also Noetherian.

#### Proof {#br-ak-2025-2026-l09-cor-01-proof}

Apply Hilbert's basis theorem inductively along the chain

$$
R\subset R[X_1]\subset (R[X_1])[X_2]=R[X_1,X_2]
\subset (R[X_1,X_2])[X_3]=R[X_1,X_2,X_3]
\subset\cdots\subset R[X_1,\ldots,X_n].
$$

<!-- upstream_entity: Kommutative Ringtheorie/Polynomring über Körper/Endliche viele Variablen/Noethersch/Fakt -->

### Corollary: polynomial rings over fields {#br-ak-2025-2026-l09-cor-02}

If $K$ is a field, then $K[X_1,\ldots,X_n]$ is Noetherian.

#### Proof {#br-ak-2025-2026-l09-cor-02-proof}

This is a special case of Corollary 9.5.

In particular, Hilbert's basis theorem means that every closed subvariety

$$
V\subseteq\mathbb A_K^n
$$

of affine space can be described by finitely many polynomials. Thus every algebraic zero locus is already the zero locus of finitely many polynomials.

<!-- upstream_entity: Hilbertscher Basisatz/Affin-algebraische Menge als Faser über 0 einer Abbildung/Fakt -->

### Corollary: a fibre over the origin {#br-ak-2025-2026-l09-cor-03}

Let $V\subseteq\mathbb A_K^n$ be an affine algebraic set. Then there is a map

$$
\varphi:\mathbb A_K^n\longrightarrow\mathbb A_K^m
$$

whose components are given by polynomials

$$
F_i\in K[X_1,\ldots,X_n],\qquad
\varphi=(F_1,\ldots,F_m),
$$

such that $V$ is the preimage of the origin

$$
0\in\mathbb A_K^m.
$$

#### Proof {#br-ak-2025-2026-l09-cor-03-proof}

Let $\mathfrak a$ be an ideal describing $V$, so

$$
V=V(\mathfrak a).
$$

By Hilbert's basis theorem, there are

$$
F_1,\ldots,F_m\in K[X_1,\ldots,X_n]
$$

with $\mathfrak a=(F_1,\ldots,F_m)$. Then

$$
V=V(\mathfrak a)=V(F_1)\cap\cdots\cap V(F_m).
$$

Combine these polynomials into a map

$$
\varphi=(F_1,\ldots,F_m):\mathbb A_K^n\longrightarrow\mathbb A_K^m.
$$

We have $\varphi(P)=0$ exactly when all its component functions vanish, which happens exactly when $P\in V(F_i)$ for every $i$; thus $V=\varphi^{-1}(0)$.

<!-- upstream_entity: Kommutative Ringtheorie/Algebra von endlichem Typ/Definition -->

### Definition: algebra of finite type {#br-ak-2025-2026-l09-def-02}

Let $R$ be a commutative ring. An $R$-algebra $A$ is called *of finite type* (or *finitely generated*) if it has the form

$$
A=R[X_1,\ldots,X_n]/\mathfrak a.
$$

Thus a finitely generated $R$-algebra has a presentation as a quotient ring of a polynomial algebra over $R$ in finitely many variables. Such a presentation is by no means unique.

<!-- upstream_entity: Kommutative Ringtheorie/Algebra von endlichem Typ/Körper/Noethersch/Fakt -->

### Corollary: finite-type algebras over a Noetherian ring {#br-ak-2025-2026-l09-cor-04}

If $R$ is Noetherian, every $R$-algebra of finite type is also Noetherian. In particular, for a field $K$, every $K$-algebra of finite type is Noetherian.

#### Proof {#br-ak-2025-2026-l09-cor-04-proof}

This follows from Corollary 9.5 and Lemma 9.3.

## Decomposition into irreducible components {#br-ak-2025-2026-l09-s03}

Hilbert's basis theorem implies that every ascending chain of ideals

$$
\mathfrak a_1\subseteq\mathfrak a_2\subseteq\mathfrak a_3\subseteq\cdots
$$

in $K[X_1,\ldots,X_n]$ becomes stationary. For descending chains of affine algebraic subsets of affine space, this has the following consequence.

<!-- upstream_entity: Affine Varietäten/Zariski-Topologie ist noethersch/Fakt -->

### Theorem: the Zariski topology is Noetherian {#br-ak-2025-2026-l09-thm-02}

In affine space $\mathbb A_K^n$, every descending sequence of closed sets

$$
V_1\supseteq V_2\supseteq\cdots
$$

becomes stationary.

#### Proof {#br-ak-2025-2026-l09-thm-02-proof}

Let

$$
V_1\supseteq V_2\supseteq\cdots
$$

be a descending chain of affine algebraic subsets of $\mathbb A_K^n$. By Lemma 3.7, their corresponding vanishing ideals satisfy

$$
\operatorname{Id}(V_i)\subseteq\operatorname{Id}(V_{i+1}).
$$

By Corollary 9.6, this chain of ideals becomes stationary, say for $i\geq i_0$. By Lemma 3.8(3),

$$
V_i=V(\operatorname{Id}(V_i)).
$$

Hence, for $i\geq i_0$,

$$
V_i=V(\operatorname{Id}(V_i))
=V(\operatorname{Id}(V_{i+1}))=V_{i+1},
$$

so the descending chain becomes stationary.

Taking complements, it follows that every ascending chain of Zariski-open sets in affine space also becomes stationary. Such a topology is called *Noetherian* (more generally, a partial order in which every ascending chain becomes stationary is called Noetherian). In a Noetherian space, every nonempty collection of open sets (or closed sets) has a maximal (or minimal) element. This is useful as a proof principle called *Noetherian induction*: to prove that a property $E$ holds for all closed subsets, consider the collection of closed subsets that do not satisfy $E$. We want to show that this collection is empty; if it were nonempty, it would have a minimal element, which we then lead to a contradiction. The validity of the principle rests on the fact that a nonempty set with no minimal element allows an infinite descending chain to be constructed. A typical example of this principle is the following theorem.

<!-- upstream_entity: Affin-algebraische Teilmengen/Zerlegung in irreduzible Komponenten/Fakt -->

### Theorem: decomposition into irreducible components {#br-ak-2025-2026-l09-thm-03}

Every affine algebraic set $V\subseteq\mathbb A_K^n$ has a unique decomposition

$$
V=V_1\cup\cdots\cup V_k
$$

into irreducible sets $V_i$ such that

$$
V_i\not\subseteq V_j\qquad\text{for }i\ne j.
$$

*Edition clarification.* The components in this statement are closed affine algebraic subsets, as required by the source's proof using closed decompositions. Uniqueness is up to reordering. For the empty set, the decomposition is the empty union.

#### Proof of existence (Noetherian induction) {#br-ak-2025-2026-l09-thm-03-existence}

Suppose not every affine algebraic set has such a decomposition. Then there is a minimal set, say $V$, without such a decomposition. The set $V$ cannot be irreducible, so it has a nontrivial decomposition

$$
V=V_1\cup V_2.
$$

Since $V_1$ and $V_2$ are proper subsets of $V$, each has a finite expression as a union of irreducible sets. Combining these expressions gives a finite expression for $V$, a contradiction.

#### Proof of uniqueness {#br-ak-2025-2026-l09-thm-03-uniqueness}

Let

$$
V=V_1\cup\cdots\cup V_k=W_1\cup\cdots\cup W_m
$$

be two decompositions into irreducible sets (with no inclusions within either decomposition). We have

$$
V_1=V_1\cap V
=V_1\cap(W_1\cup\cdots\cup W_m)
=(V_1\cap W_1)\cup\cdots\cup(V_1\cap W_m).
$$

Since $V_1$ is irreducible, $V_1\subseteq W_j$ for some $j$. By the same argument, $W_j\subseteq V_i$ for some $i$, whence $i=1$ and $V_1=W_j$. Similarly, $V_2$ and so on reappear in the decomposition on the right, so the decomposition is unique.

The sets $V_1,\ldots,V_k$ in this theorem are called the *irreducible components* of $V$.

## Modules {#br-ak-2025-2026-l09-s04}

<!-- upstream_entity: Modultheorie (kommutative Algebra)/Einführung/Textabschnitt -->

### Definition: module {#br-ak-2025-2026-l09-def-03}

Let $R$ be a commutative ring and

$$
M=(M,+,0)
$$

an additively written commutative group. We call $M$ an *$R$-module* if an operation

$$
R\times M\longrightarrow M,\qquad(r,v)\longmapsto rv=r\cdot v,
$$

called *scalar multiplication*, is specified and satisfies the following axioms (for arbitrary $r,s\in R$ and $u,v\in M$):

$$
\begin{aligned}
r(su)&=(rs)u,\\
r(u+v)&=(ru)+(rv),\\
(r+s)u&=(ru)+(su),\\
1u&=u.
\end{aligned}
$$

<!-- upstream_entity: Modultheorie (kommutative Algebra)/Untermodul/Definition -->

### Definition: submodule {#br-ak-2025-2026-l09-def-04}

Let $R$ be a commutative ring and $M$ an $R$-module. A subset

$$
U\subseteq M
$$

is called an *$R$-submodule* if it is a subgroup of $(M,0,+)$ and $ru\in U$ for every $u\in U$ and $r\in R$.

<!-- upstream_entity: Modultheorie (kommutative Algebra)/Erzeugendensystem/Definition -->

### Definition: a generating set for a module {#br-ak-2025-2026-l09-def-05}

Let $R$ be a commutative ring and $M$ an $R$-module. A family

$$
v_i\in M\qquad(i\in I)
$$

is called a *generating set* for $M$ if every $v\in M$ has an expression

$$
v=\sum_{i\in J}r_iv_i,
$$

where $J\subseteq I$ is finite and $r_i\in R$.

<!-- upstream_entity: Kommutative Algebra/Modultheorie/Endlicher Modul/Definition -->

### Definition: finitely generated module {#br-ak-2025-2026-l09-def-06}

Let $R$ be a commutative ring and $M$ an $R$-module. The module $M$ is called *finitely generated* (or *finite*) if it has a finite generating set $v_i$ ($i\in I$), that is, one with a finite index set.

A commutative ring $R$ itself is naturally an $R$-module if ring multiplication is interpreted as scalar multiplication. Its ideals are exactly the $R$-submodules of $R$. For ideals, the notions of an *ideal generating set* and a *module generating set* coincide. A vector space is simply a module over a field.
