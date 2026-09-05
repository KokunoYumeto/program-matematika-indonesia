---
title: "Public Solutions to Worksheet 20"
stable_id: br-ak-2025-2026-w20-solutions
language: en
upstream_map: authority/wikiversity/unit-20/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: c74da7b0627cf8c8c694c0a9f20e94b0c7dc00ecd6c95b72ad21ae4a6c5c07ea
public_solution_count: 8
upstream_solution_revisions: "Soal 20.1=612937; Soal 20.3=1113196; Soal 20.4=1054377; Soal 20.5=1090115; Soal 20.12=1112402; Soal 20.13=1095226; Soal 20.14=1096447; Soal 20.17=1096446"
solution_xml_sha256: "01=adde79e2be2fd065988d87a4679d4b1da19c7adc757b2a3359a8d724c6b013b0; 03=94c1fde92ccb9f23400663f673eafa555e7194c89a9427f11c3c9cfed923df66; 04=804783e2895604f6748c0e47fa40799d384a5c5c3eea9488557c93954acf6a54; 05=32953ecdbf24d53fdd469f25c78110aee88485b4b3f7877429e30097a6139b9a; 12=96f81c667ecc03e7e8685821049a66aa24146255456d281e92d8ffe6a0b85b76; 13=801eb06d552df3563f8e70d53fa673fad0e0e88ee2c35b959c366c25fbf14af4; 14=fd17e6d973a3b495694a25b252368ebffd43cf66cdb4d236707638f658c53b9b; 17=116baccffca81eab52df1ee1a543d4d982c63359f24de407a13cbbd4a7fb318c"
transcluded_proof_revisions: "Soal 20.1=1108353; Soal 20.4=1101325"
transcluded_proof_xml_sha256: "01=2af64ad5502d186551fbe405a788f7ac04384bc68a8e0652f6675f92311918e9; 04=045c7318d21d5469bf7ab7f4b368fbcb469292746db573f737bf00b65b2f2a4d"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 20 {#br-ak-2025-2026-w20-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 20.1, 20.3, 20.4, 20.5, 20.12, 20.13, 20.14, and 20.17. The solutions to Exercises 20.1 and 20.4 are wrapper pages transcluding separate proof bodies; this edition includes those frozen proof bodies in full. No additional solutions have been created for this edition.

<!-- upstream_solution: Quadratwurzel/2/Irrational/Fakt/Beweis/Aufgabe/Lösung; pageid=114792; revid=612937 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=612937 -->
<!-- upstream_transcluded_proof: Quadratwurzel/2/Irrational/Fakt/Beweis; pageid=111327; revid=1108353 -->
<!-- upstream_transcluded_proof_url: https://de.wikiversity.org/w/index.php?oldid=1108353 -->

## Solution to Exercise 20.1 {#br-ak-2025-2026-w20-sol-01}

We assume that there is a rational number whose square is $2$ and derive a contradiction. Thus suppose that

$$
x\in\mathbb Q
$$

and

$$
x^2=2.
$$

Every rational number can be written as a fraction with integer numerator and denominator. We may therefore write

$$
x=\frac ab.
$$

We may also assume that the fraction is in lowest terms, so that $a$ and $b$ have no nontrivial common divisor. This choice merely simplifies the representation and is not the assumption we intend to refute. In fact, we only need at least one of $a$ and $b$ to be odd: if both are even, we can divide both by $2$ and continue as necessary.

The equation $x^2=2$ means

$$
x^2=\left(\frac ab\right)^2=\frac{a^2}{b^2}=2.
$$

Multiplying by $b^2$ gives an equation in $\mathbb Z$ (indeed, in $\mathbb N$),

$$
2b^2=a^2.
$$

Thus $a^2$ is even, being a multiple of $2$. Consequently $a$ itself is even, since the square of an odd number is odd. We can therefore write

$$
a=2c
$$

for some $c\in\mathbb Z$. Substituting into the equation above gives

$$
2b^2=(2c)^2=2^2c^2.
$$

Dividing by $2$, we obtain

$$
b^2=2c^2.
$$

For the same reason, $b^2$, and hence $b$, is also even. This contradicts our choice that $a$ and $b$ are not both even.

[Back to Exercise 20.1](#br-ak-2025-2026-w20-ex-01).

<!-- upstream_solution: Primfaktorzerlegung/3 Wurzel 9/Irrational/Aufgabe/Lösung; pageid=25178; revid=1113196 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1113196 -->

## Solution to Exercise 20.3 {#br-ak-2025-2026-w20-sol-03}

Suppose that there is a representation

$$
9^{1/3}=\frac ab
$$

with $a,b\in\mathbb N_+$. If $a$ and $b$ have a common divisor at least $2$, we can cancel it. Thus we may assume that $a$ and $b$ are relatively prime. Cubing the original equation gives

$$
9=\frac{a^3}{b^3},
$$

or

$$
3^2b^3=a^3.
$$

This number has a unique prime factorisation. Since $3$ occurs in it, $3\mid a^3$; as $3$ is prime, also $3\mid a$. Hence the exponent of $3$ in the prime factorisation on the right is at least $3$. On the other hand, because $a$ and $b$ are relatively prime, $b$ is not divisible by $3$, so the exponent of $3$ on the left is exactly $2$. This is a contradiction.

[Back to Exercise 20.3](#br-ak-2025-2026-w20-ex-03).

<!-- upstream_solution: Kommutative Ringtheorie/Z ist normal/Wurzeln aus ganzen Zahlen sind irrational/Fakt/Beweis/Aufgabe/Lösung; pageid=166918; revid=1054377 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1054377 -->
<!-- upstream_transcluded_proof: Kommutative Ringtheorie/Z ist normal/Wurzeln aus ganzen Zahlen sind irrational/Fakt/Beweis; pageid=14442; revid=1101325 -->
<!-- upstream_transcluded_proof_url: https://de.wikiversity.org/w/index.php?oldid=1101325 -->

## Solution to Exercise 20.4 {#br-ak-2025-2026-w20-sol-04}

The number

$$
n=p_1^{\alpha_1}\cdots p_r^{\alpha_r}
$$

cannot have a $k$th root in $\mathbb Z$, since in a $k$th power all prime-factor exponents are multiples of $k$, whereas by hypothesis this does not hold for all the $\alpha_i$.

Since $\mathbb Z$ is a unique factorisation domain, it is normal. Therefore there cannot be an

$$
x\in Q(\mathbb Z)=\mathbb Q
$$

with

$$
x^k=n.
$$

Thus the real number $n^{1/k}$ is irrational.

[Back to Exercise 20.4](#br-ak-2025-2026-w20-ex-04).

<!-- upstream_solution: Normaler integrer Ring/Nenneraufnahme an einem Element ist normal/Aufgabe/Lösung; pageid=21367; revid=1090115 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1090115 -->

## Solution to Exercise 20.5 {#br-ak-2025-2026-w20-sol-05}

Let

$$
q\in Q(R)=Q(R_f)
$$

be an element of the field of fractions satisfying an equation of integral dependence over $R_f$. Thus there is an equation

$$
q^n+g_{n-1}q^{n-1}+\cdots+g_1q+g_0=0,
\qquad g_i\in R_f.
$$

Each $g_i$ can be written as a fraction whose denominator is a power of $f$. We can choose one fixed power $f^k$ as a common denominator. Increasing $k$ if necessary, we may also assume that $k$ is a multiple of $n$.

Multiplying the equation by $f^{kn}$ gives

$$
(f^kq)^n
+g_{n-1}f^k(f^kq)^{n-1}
+\cdots
+g_1f^{k(n-1)}(f^kq)
+f^{kn}g_0=0.
$$

All coefficients in this equation lie in $R$. It is therefore an equation of integral dependence for $f^kq$ over $R$. Since $R$ is normal, we obtain $f^kq\in R$, and hence

$$
q=\frac b{f^k}\in R_f
$$

for some $b\in R$. Thus the localisation $R_f$ is also normal.

[Back to Exercise 20.5](#br-ak-2025-2026-w20-ex-05).

<!-- upstream_solution: Y^2-X^4/Monoidring/Aufgabe/Lösung; pageid=95141; revid=1112402 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1112402 -->

## Solution to Exercise 20.12 {#br-ak-2025-2026-w20-sol-12}

1. We have

   $$
   Y^2-X^4=(Y-X^2)(Y+X^2),
   $$

   so the curve is reducible.

2. Consider the monoid $M$ with two generators $e,f$ and the single relation

   $$
   2f=4e.
   $$

   Then

   $$
   \mathbb C[M]\cong\mathbb C[X,Y]/(Y^2-X^4).
   $$

3. Take

   $$
   e=(1,1)\in\mathbb N\times\mathbb Z/(2)
   $$

   and

   $$
   f=(2,1)\in\mathbb N\times\mathbb Z/(2).
   $$

   We have $2f=4e$. All other relations are multiples of this one. Indeed, if

   $$
   af=be,
   \qquad a,b\in\mathbb N,
   $$

   then comparing the first coordinates gives $b=2a$, while comparing the second coordinates requires $a$ to be even.

[Back to Exercise 20.12](#br-ak-2025-2026-w20-ex-12).

<!-- upstream_solution: Monoid/Einheit/Teilmenge von NxZ mod n/Aufgabe/Lösung; pageid=95147; revid=1095226 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1095226 -->

## Solution to Exercise 20.13 {#br-ak-2025-2026-w20-sol-13}

Let

$$
m=(r,s)\in M.
$$

If $m$ is a unit in $M$, it is certainly also a unit in $\mathbb N\times\mathbb Z/(n)$, since its inverse in $M$ belongs to that larger monoid.

Conversely, suppose that $m$ is a unit in $\mathbb N\times\mathbb Z/(n)$. We must first have $r=0$. For

$$
m=(0,s),
\qquad 0\leq s<n,
$$

its inverse in $\mathbb N\times\mathbb Z/(n)$ is

$$
(0,n-s)=(0,-s).
$$

But

$$
(n-1)(0,s)=(0,(n-1)s)=(0,-s).
$$

Since $(0,s)\in M$ and $M$ is closed under addition, this inverse also belongs to $M$. Hence $m$ is a unit in $M$.

[Back to Exercise 20.13](#br-ak-2025-2026-w20-ex-13).

<!-- upstream_solution: NxZ mod n/C/Komponenten/Aufgabe/Lösung; pageid=95161; revid=1096447 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1096447 -->

## Solution to Exercise 20.14 {#br-ak-2025-2026-w20-sol-14}

We have

$$
\begin{aligned}
\mathbb C[M]
&\cong \mathbb C[S,T]/(S^n-1)\\
&\cong \mathbb C[T][S]/(S^n-1)\\
&\cong \mathbb C[T][S]\Big/\left(\prod_{\zeta^n=1}(S-\zeta)\right)\\
&\cong \left(\mathbb C[S]\Big/\left(\prod_{\zeta^n=1}(S-\zeta)\right)\right)[T],
\end{aligned}
$$

where $\zeta$ runs through all $n$ complex roots of unity. Furthermore,

$$
\mathbb C[S]\Big/\left(\prod_{\zeta^n=1}(S-\zeta)\right)
\cong\mathbb C^n,
$$

with the isomorphism given by

$$
S\longmapsto(\zeta_0,\zeta_1,\ldots,\zeta_{n-1}).
$$

Consequently,

$$
\left(\mathbb C[S]\Big/\left(\prod_{\zeta^n=1}(S-\zeta)\right)\right)[T]
\cong\mathbb C^n[T]
\cong(\mathbb C[T])^n
$$

is a product ring of $n$ polynomial rings $\mathbb C[T]$. Therefore its $\mathbb C$-spectrum is the disjoint union of $n$ copies of

$$
\operatorname{Spec}_{\mathbb C}(\mathbb C[T])
\cong\mathbb A^1_{\mathbb C}.
$$

Each of these affine lines is irreducible.

**Edition note:** in the three products, the source uses the dummy index $\eta$ in $\prod_\eta(S-\zeta)$, whereas the factors and explanatory prose use $\zeta$. This edition transparently makes the indexing consistent as $\prod_{\zeta^n=1}(S-\zeta)$.

[Back to Exercise 20.14](#br-ak-2025-2026-w20-ex-14).

<!-- upstream_solution: Numerisches Monoid/Singularitätsgrad/Ringkette/Aufgabe/Lösung; pageid=95576; revid=1096446 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1096446 -->

## Solution to Exercise 20.17 {#br-ak-2025-2026-w20-sol-17}

The degree of singularity $\delta$ is the number of gaps of $M$ in $\mathbb N$. This equals

$$
\dim_K(R^{\mathrm{norm}}/R)
=\dim_K(K[T]/K[M]).
$$

1. In a chain of monoids

   $$
   M=M_0\subsetneq M_1\subsetneq M_2\subsetneq\cdots
   \subsetneq M_n=\mathbb N,
   $$

   at least one element must be added at each step. Hence $n\leq\delta$. Conversely, define $M_{i+1}$ successively by adjoining to $M_i$ the largest element not yet in $M_i$. The result is still a monoid and has exactly one more element than $M_i$. This procedure produces a chain of length $\delta$, as required.

2. This chain of length $\delta$ gives a chain of $K$-algebras

   $$
   K[M]=K[M_0]\subsetneq K[M_1]\subsetneq K[M_2]\subsetneq\cdots
   \subsetneq K[M_\delta]=K[\mathbb N].
   $$

   All these inclusions are strict: if $m\in M_{i+1}\setminus M_i$, then

   $$
   T^m\in K[M_{i+1}]\setminus K[M_i].
   $$

   The next part gives the general reason that no longer chain exists.

3. The algebra chain in part 2 is, in particular, a chain of vector subspaces over $K$. Since

   $$
   \dim_K(K[\mathbb N]/K[M])=\delta,
   $$

   there can be no longer chain of vector subspaces: these chains correspond to chains in the quotient vector space $K[\mathbb N]/K[M]$, and in a vector space of dimension $\delta$, the maximum length of a chain of strict inclusions is $\delta$.

**Edition note:** in step 2 the source writes $T^m\in M_{i+1}\setminus M_i$. Since the $M_i$ consist of exponents, the correctly typed relation is $m\in M_{i+1}\setminus M_i$, which then gives $T^m\in K[M_{i+1}]\setminus K[M_i]$. This edition states that implication explicitly.

[Back to Exercise 20.17](#br-ak-2025-2026-w20-ex-17).

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
