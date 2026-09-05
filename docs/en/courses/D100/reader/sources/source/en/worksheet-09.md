---
title: "Worksheet 9 - Noetherian Rings, Hilbert's Basis Theorem, and Modules"
stable_id: br-ak-2025-2026-w09
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Arbeitsblatt 9"
upstream_pageid: 165928
upstream_revid: 1059491
upstream_timestamp: "2025-11-21T13:53:14Z"
upstream_mediawiki_sha1: affd5b273368b8a02f7580671dc4b1431f7da9df
source_url: "https://de.wikiversity.org/w/index.php?oldid=1059491"
authority_manifest: authority/wikiversity/unit-09/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7cf7a956dffe854da9d021e3c74615573b91b5701d7e3b78a8f5f1aa45bfbc29
worksheet_xml_sha256: f38a6617a6a4a10acfa6863eeb99d3ae806385dedb5b6aaa72ba419e9a957196
worksheet_expanded_tex_sha256: af54baf45f10cb1394ac10a2cbf6d9fbf9cb30c113c7166a3751acce8723c7e1
exercise_map: authority/wikiversity/unit-09/ORDERED_EXERCISE_MAP.json
exercise_map_sha256: c906ba0b1073a162f7f55289c0f60114063d011756f1eb907bcf342336729495
license: "CC BY-SA 4.0"
translation_status: complete
---

# Worksheet 9 {#br-ak-2025-2026-w09}

## Practice exercises {#br-ak-2025-2026-w09-practice}

<!-- upstream_entity: Noethersche Ringe/Von endlichen Typ über Z/Beispiel/Aufgabe -->

### Exercise 9.1 {#br-ak-2025-2026-w09-ex-01}

Explain why the ring

$$
\mathbb Z[X,Y,Z,W]/\left(XY-ZW,\,5X^8-YZ^3+2WXY\right)
$$

is Noetherian.

<!-- upstream_entity: Kommutative Ringe/Idealtheorie/Aufsteigende Kette ist Ideal/Aufgabe -->

### Exercise 9.2 {#br-ak-2025-2026-w09-ex-02}

Let $R$ be a commutative ring and

$$
\mathfrak a_1\subseteq\mathfrak a_2\subseteq\mathfrak a_3\subseteq\cdots
$$

an ascending chain of ideals. Show that the union

$$
\bigcup_{n\in\mathbb N}\mathfrak a_n
$$

is also an ideal. Give a simple example showing that a union of ideals need not be an ideal in general.

<!-- upstream_entity: Noethersche Ringe/Produkt/Aufgabe -->

### Exercise 9.3 {#br-ak-2025-2026-w09-ex-03}

Show that the product $R\times S$ of Noetherian rings $R$ and $S$ is again Noetherian.

<!-- upstream_entity: Polynomring/2 Variablen/Erzeugendensysteme/Aufgabe -->

### Exercise 9.4 {#br-ak-2025-2026-w09-ex-04}

Let $K$ be a field. Show that in $K[X,Y]$ there is no upper bound on the number of generators in a minimal generating set of an ideal.

**Hint:** Consider the powers $(X,Y)^m$.

<!-- upstream_entity: Polynomring in unendlich vielen Variablen/Nicht noethersch/Kette und Erzeugung/Aufgabe -->

### Exercise 9.5 {#br-ak-2025-2026-w09-ex-05}

Let $K$ be a field and

$$
K[X_n,\,n\in\mathbb N]
$$

the polynomial ring over $K$ in infinitely many variables. Describe an ideal that is not finitely generated and an infinite strictly ascending chain of ideals in it.

<!-- upstream_entity: Noetherscher Ring/Unterring/Aufgabe -->

### Exercise 9.6 ★ {#br-ak-2025-2026-w09-ex-06}

Show that a subring

$$
R\subseteq S
$$

of a Noetherian ring need not be Noetherian.

<!-- upstream_entity: Nicht-noethersche Ringe/Beispiel/Reduktion ist Körper/Aufgabe -->

### Exercise 9.7 {#br-ak-2025-2026-w09-ex-07}

Give an example of a non-Noetherian ring whose reduction is a field.

<!-- upstream_entity: Noetherscher Ring/Ideal und Restklassenring/Aufgabe -->

### Exercise 9.8 {#br-ak-2025-2026-w09-ex-08}

Let $R$ be a commutative ring and $\mathfrak a\subset R$ a proper ideal with quotient ring $R/\mathfrak a$. Give an example showing that $\mathfrak a$ can be finitely generated and $R/\mathfrak a$ Noetherian even though $R$ itself is not Noetherian.

<!-- upstream_entity: Hilbertscher Basissatz/Normiertes Polynom/Idealkette/Aufgabe -->

### Exercise 9.9 {#br-ak-2025-2026-w09-ex-09}

Let $R$ be a commutative ring and $\mathfrak b\subseteq R[X]$ an ideal containing at least one monic polynomial. What does this imply for the chain of ideals in $R$ constructed in the proof of Hilbert's basis theorem?

<!-- upstream_entity: Hilbertscher Basissatz/Konstante Idealkette/Aufgabe -->

### Exercise 9.10 {#br-ak-2025-2026-w09-ex-10}

Let $R$ be a commutative ring. Characterise the ideals

$$
\mathfrak b\subseteq R[X]
$$

for which the chain of ideals in $R$ constructed in the proof of Hilbert's basis theorem is constant.

<!-- upstream_entity: Hilbertscher Basissatz/Maximales Ideal/Potenzen/Idealkette/Aufgabe -->

### Exercise 9.11 {#br-ak-2025-2026-w09-ex-11}

Let $K$ be a field and $R=K[X]$ the polynomial ring over $K$. For the ideals

$$
\mathfrak b_m=(X,Y)^m\subseteq R[Y]=K[X,Y],
$$

determine the chain of ideals in $R$ constructed in the proof of Hilbert's basis theorem. When does it become stationary?

<!-- upstream_entity: Hilbertscher Basissatz/Z/(6,6x^2+2x+3,3x^3+5,2x^5+x-4,4x^7-3x)/Bestimme Idealkette/Aufgabe -->

### Exercise 9.12 {#br-ak-2025-2026-w09-ex-12}

For the ideal

$$
I=\left(6,\,6x^2+2x+3,\,3x^3+5,\,2x^5+x-4,\,4x^7-3x\right)
$$

in $\mathbb Z[x]$, determine the chain of ideals constructed in the proof of Hilbert's basis theorem and the corresponding generating set for $I$. Write the generators above as linear combinations of the constructed generating set.

<!-- upstream_entity: Endlich erzeugte Algebra/Endliches Teilsystem/Aufgabe -->

### Exercise 9.13 ★ {#br-ak-2025-2026-w09-ex-13}

Let $R$ be a commutative ring and $A$ a commutative $R$-algebra. Suppose $A$ is generated over $R$ by the family $a_i\in A$ ($i\in I$). Prove that if $A$ is finitely generated, then it is also generated by a finite subfamily of the $a_i$.

<!-- upstream_entity: Affiner Raum/Ab- und Aufsteigungseigenschaften/Endlicher Körper/Länge/Aufgabe -->

### Exercise 9.14 {#br-ak-2025-2026-w09-ex-14}

Consider ascending and descending chains of affine algebraic sets in $\mathbb A_K^n$ and of ideals in $K[X_1,\ldots,X_n]$. Show the following.

1. For a finite field, every ascending chain

   $$
   V_0\subseteq V_1\subseteq V_2\subseteq\cdots
   $$

   of affine algebraic sets becomes stationary.
2. For an infinite field and $n\geq1$, not every ascending chain of affine algebraic sets

   $$
   V_0\subseteq V_1\subseteq V_2\subseteq\cdots
   $$

   becomes stationary.
3. For any field and $n\geq1$, not every descending chain of ideals

   $$
   \mathfrak a_0\supseteq\mathfrak a_1\supseteq\mathfrak a_2\supseteq\cdots
   $$

   becomes stationary.
4. For an infinite field and $n\geq1$, there are strictly descending chains of affine algebraic sets of arbitrary length.

<!-- upstream_entity: Reelle Zahlen/Kein noetherscher Raum/Aufgabe -->

### Exercise 9.15 {#br-ak-2025-2026-w09-ex-15}

Show that the set $\mathbb R$ of real numbers with its metric topology is not a Noetherian topological space.

<!-- upstream_entity: Kommutative Algebra/Abelsche Gruppe/Z-Modul/Aufgabe -->

### Exercise 9.16 {#br-ak-2025-2026-w09-ex-16}

Let $G$ be a commutative group. Show that there is exactly one way to give $G$ the structure of a $\mathbb Z$-module. Thus commutative groups and $\mathbb Z$-modules are equivalent objects.

<!-- upstream_entity: Kommutative Algebren/Moduldefinition und Ringhomomorphismus/Äquivalenz/Aufgabe -->

### Exercise 9.17 {#br-ak-2025-2026-w09-ex-17}

Let $R$ and $A$ be commutative rings. Show that $A$ is an $R$-algebra if and only if $A$ is an $R$-module additionally satisfying

$$
r(ab)=(ra)b\qquad\text{for all }r\in R,\ a,b\in A.
$$

<!-- upstream_entity: Modul/Kommutativer Ring/Allgemeines Distributivgesetz/Aufgabe -->

### Exercise 9.18 ★ {#br-ak-2025-2026-w09-ex-18}

Let $V$ be a module over the commutative ring $R$. Let

$$
s_1,\ldots,s_k\in R\qquad\text{and}\qquad v_1,\ldots,v_n\in V.
$$

Prove that

$$
\left(\sum_{i=1}^k s_i\right)\!\cdot
\left(\sum_{j=1}^n v_j\right)
=\sum_{1\leq i\leq k,\,1\leq j\leq n}s_i\cdot v_j.
$$

<!-- upstream_entity: Lineare Abbildung/Moduln/Bild und Urbild/Untermoduln/Fakt/Beweis/Aufgabe -->

### Exercise 9.19 {#br-ak-2025-2026-w09-ex-19}

Let $R$ be a commutative ring, $M$ and $N$ two $R$-modules, and $\varphi:M\to N$ a module homomorphism. Prove the following statements.

1. If $S\subseteq M$ is an $R$-submodule, then its image $\varphi(S)$ is a submodule of $N$.
2. In particular, the image of the map

   $$
   \operatorname{bild}\varphi=\varphi(M)
   $$

   is a submodule of $N$.
3. If $T\subseteq N$ is a submodule, then the preimage

   $$
   \varphi^{-1}(T)
   $$

   is a submodule of $M$.
4. In particular, the kernel

   $$
   \varphi^{-1}(0)
   $$

   is a submodule of $M$.

## Exercises for submission {#br-ak-2025-2026-w09-submit}

<!-- upstream_entity: Idealtheorie (kommutative Algebra)/Ideale im Restklassenring/Korrespondenz/Aufgabe -->

### Exercise 9.20 (3 points) {#br-ak-2025-2026-w09-ex-20}

Let $R$ be a commutative ring and $\mathfrak a$ an ideal with quotient ring

$$
S=R/\mathfrak a.
$$

Show that the ideals of $S$ correspond uniquely to the ideals of $R$ containing $\mathfrak a$. Show that the same holds for prime ideals, radical ideals, and maximal ideals.

<!-- upstream_entity: Kommutative Ringtheorie/Noetherscher Bereich/Zerlegung in irreduzible Elemente/Aufgabe -->

### Exercise 9.21 (4 points) {#br-ak-2025-2026-w09-ex-21}

Let $R$ be a Noetherian integral domain. Show that every nonzero nonunit of $R$ can be written as a product of irreducible elements.

*Edition note.* The source says “every element”. Zero and units must be excluded from that formulation; equivalently, every nonzero element is a unit times a finite product of irreducibles, with the empty product allowed.

<!-- upstream_entity: Algebren von endlichem Typ/Q ist nicht über Z/Aufgabe -->

### Exercise 9.22 (4 points) {#br-ak-2025-2026-w09-ex-22}

Show that $\mathbb Q$ is not an algebra of finite type over $\mathbb Z$.

<!-- upstream_entity: Endlich erzeugte Algebra/Zwei Variablen über Körper/Nicht endlich erzeugte Unteralgebra/Finde/Aufgabe -->

### Exercise 9.23 (4 points) {#br-ak-2025-2026-w09-ex-23}

Let $K$ be a field and $A=K[X,Y]$. Find a $K$-subalgebra of $A$ that is not finitely generated.

<!-- upstream_entity: Hilbertscher Basissatz/Z/(10,6x^2+8,4x^3-12)/Bestimme Idealkette/Aufgabe -->

### Exercise 9.24 (4 points) {#br-ak-2025-2026-w09-ex-24}

For the ideal

$$
I=\left(10,\,6x^2+8,\,4x^3-12\right)
$$

in $\mathbb Z[x]$, determine the chain of ideals constructed in the proof of Hilbert's basis theorem and the corresponding generating set for $I$. Write the original generators as linear combinations of the constructed generating set.
