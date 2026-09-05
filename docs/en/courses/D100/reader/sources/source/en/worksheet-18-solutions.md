---
title: "Public Solutions to Worksheet 18"
stable_id: br-ak-2025-2026-w18-solutions
language: en
upstream_map: authority/wikiversity/unit-18/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 8b55ef14cccbcab93ba99882d16e0f9888780353f7290eff8e1d2d6cd6bc4cd9
public_solution_count: 5
upstream_solution_revisions: "Soal 18.3=959312; Soal 18.4=959372; Soal 18.10=1112399; Soal 18.11=1111901; Soal 18.15=1090073"
solution_xml_sha256: "03=d2aa3b5c46f63dbdecb3a62db121a935570696bd7c0dc1f34152eba4102fb44d; 04=b9cd383fbd20439b01122bc90b52acaa0ed68198299f74573e1c1511803ff512; 10=814e4ec7eba6c9095bd791de8e09ce91ed76cdd6bc7420478db4e6cf143b5b0b; 11=5732eddb9ae123354f8c3899aa1e88daa89e684432601e1e311c9e350f3f8a59; 15=34642c05983708afb0e21ce5072b5179ddb09a7bb70930ff1f74fb137a7fdf5d"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 18 {#br-ak-2025-2026-w18-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 18.3, 18.4, 18.10, 18.11, and 18.15. No additional solutions have been created for this edition.

<!-- upstream_solution: Monomiale Kurve/7,11,13,37/Geldfälscher/Aufgabe/Lösung; pageid=21336; revid=959312 -->
<!-- upstream_solution_revid: 959312 -->

## Solution to Exercise 18.3 {#br-ak-2025-2026-w18-sol-03}

We compute the sums that can be formed from the four numbers. We do this by adding multiples of $7$ to sums formed from the larger numbers. The multiples of $7$ are

$$
7,14,21,28,35,42,\ldots.
$$

Starting from $11$ gives

$$
11,18,25,32,39,46,\ldots.
$$

Starting from $13$ gives

$$
13,20,27,34,41,\ldots.
$$

Starting from $22=11+11$ gives

$$
22,29,36,43,\ldots,
$$

and starting from $24=11+13$ gives

$$
24,31,38,45,\ldots.
$$

We also add

$$
26=13+13,\qquad
33=11+11+11,\qquad
35=11+11+13,\qquad
37=11+13+13.
$$

The last equality also shows that the generator $37$ is redundant. We now have a gap-free sequence from $31$ to $37$, of length $7$, so every larger number also belongs to the monoid. The number $30$ does not belong to it. Hence the conductor is $31$, and $30$ is the largest amount that cannot be paid.

The multiplicity is the least positive number, namely $7$, and the embedding dimension is $3$ because $37$ is redundant. The gaps are

$$
1,2,3,4,5,6,8,9,10,12,15,16,17,19,23,30.
$$

Thus the degree of singularity is $16$; this is exactly the number of amounts that cannot be paid.

[Back to Exercise 18.3](#br-ak-2025-2026-w18-ex-03).

<!-- upstream_solution: Numerisches Monoid/4,7,17/Invarianten/Aufgabe/Lösung; pageid=21594; revid=959372 -->
<!-- upstream_solution_revid: 959372 -->

## Solution to Exercise 18.4 {#br-ak-2025-2026-w18-sol-04}

The monoid contains all multiples of $4$, namely

$$
4,8,12,16,20,24,\ldots.
$$

It also contains all sums of $7$ and a multiple of $4$,

$$
7,11,15,19,23,\ldots,
$$

all sums of $2\cdot7=14$ and a multiple of $4$,

$$
14,18,22,26,\ldots,
$$

and all sums of $3\cdot7=21$ and a multiple of $4$,

$$
21,25,\ldots.
$$

Thus all numbers from $18$ onwards are covered, since every residue class modulo $4$ has a representative in the monoid. Since the generator $17$ is also available, all numbers from $14$ onwards belong to the monoid. Hence the conductor is $14$.

The multiplicity is the least positive number in the monoid, namely $4$. The embedding dimension is $3$, since the generator $17$ cannot be omitted. The gaps are

$$
1,2,3,5,6,9,10,13,
$$

so the degree of singularity is $8$.

[Back to Exercise 18.4](#br-ak-2025-2026-w18-ex-04).

<!-- upstream_solution: Neilsche Parabel/(1,1)/Radikalbeschreibung/Aufgabe/Lösung; pageid=94833; revid=1112399 -->
<!-- upstream_solution_revid: 1112399 -->

## Solution to Exercise 18.10 {#br-ak-2025-2026-w18-sol-10}

Consider the injective ring homomorphism

$$
\begin{aligned}
\varphi:R&\longrightarrow\mathbb C[T],\\
X&\longmapsto T^2,\\
Y&\longmapsto T^3.
\end{aligned}
$$

The extension of the ideal $(X-1,Y-1)$ is

$$
(T^2-1,T^3-1)
=((T-1)(T+1),(T-1)(T^2+T+1)).
$$

The radical of this ideal is $(T-1)$, since $1$ is the only common root of the two polynomials. This also follows from the Nullstellensatz; in this case the corresponding ideals are in fact equal.

Suppose that $(X-1,Y-1)=\sqrt{(f)}$ for some $f\in R$. After extending to $\mathbb C[T]$, we must have

$$
\varphi(f)=c(T-1)^n
$$

for some $n\in\mathbb N_+$ and $c\in\mathbb C^\times$. The coefficient of $T$ in this polynomial is $cn(-1)^{n-1}\ne0$. However, every element in the image of $R$ has the form

$$
\varphi(f)=a_0+a_2T^2+a_3T^3+\cdots+a_dT^d,
$$

and therefore has no linear term. This is a contradiction.

**Edition note:** the source writes $\varphi(f)=(T-1)^n$ directly. Equality of radicals gives only a nonzero scalar multiple $c(T-1)^n$. This edition retains the argument with the necessary factor $c$; the linear coefficient remains nonzero.

[Back to Exercise 18.10](#br-ak-2025-2026-w18-ex-10).

<!-- upstream_solution: Neilsches Monoid/Werte in Z mod 9/Aufgabe/Lösung; pageid=167325; revid=1111901 -->
<!-- upstream_solution_revid: 1111901 -->

## Solution to Exercise 18.11 {#br-ak-2025-2026-w18-sol-11}

1. The elements

   $$
   1,2,4,5,7,8
   $$

   are units, since they are all relatively prime to $9$. The elements $0,3,6$ are nilpotent, since their squares are $0$ in $R$.

2. For a monoid homomorphism

   $$
   \pi:\mathbb N\longrightarrow R
   $$

   we must have $\pi(0)=1$. The homomorphism is uniquely determined by $\pi(1)$, and any element of $R$ can be chosen as this value. Thus

   $$
   \left|\operatorname{Mor}_{\mathrm{mon}}(\mathbb N,R)\right|=9.
   $$

3. Suppose that $\rho(2)$ is a unit. The only possible choice is

   $$
   \pi(1)=\rho(3)\rho(2)^{-1},
   $$

   since we must have

   $$
   \rho(3)=\pi(3)=\pi(2)\pi(1)=\rho(2)\pi(1).
   $$

   We check that this really defines a homomorphism from $\mathbb N$ to $R$. On all other numbers, $\pi$ is already fixed by $\rho$. We must check $\pi(i+j)=\pi(i)\pi(j)$ for every $i,j\in\mathbb N$. The cases in which one summand is $0$, or both summands are at least $2$, follow immediately because $\rho$ is a homomorphism. For $i=j=1$,

   $$
   \begin{aligned}
   \pi(1)\pi(1)
   &=\rho(3)\rho(2)^{-1}\rho(3)\rho(2)^{-1}\\
   &=\rho(3+3)\rho(2+2)^{-1}\rho(2)^{-1}\rho(2)\\
   &=\rho(6)\rho(6)^{-1}\rho(2)\\
   &=\rho(2)=\pi(2).
   \end{aligned}
   $$

   For $j\geq2$,

   $$
   \begin{aligned}
   \pi(1)\pi(j)
   &=\pi(1)\rho(j)\\
   &=\rho(3)\rho(2)^{-1}\rho(j)\\
   &=\rho(3+j)\rho(2)^{-1}\\
   &=\rho(1+j)\rho(2)\rho(2)^{-1}\\
   &=\rho(1+j)=\pi(1+j).
   \end{aligned}
   $$

4. If $\pi(1)$ is a unit, its entire image consists of units, so the restriction to $M\setminus\{0\}$ is not the zero function. If

   $$
   \pi(1)\in\{0,3,6\},
   $$

   then $\pi(2)=0$, and hence $\pi(i)=0$ for every $i\geq2$. Thus exactly these three choices give the required zero restriction.

5. By part 3, only homomorphisms $\rho$ with $\rho(2)$ nilpotent can fail to have an extension. In that case $\rho(3)$ is also nilpotent. If $\rho(3)$ were a unit, then

   $$
   \rho(3+3)=\rho(6)=\rho(2+2+2)
   $$

   would be a unit, and hence $\rho(2)$ would also be a unit, a contradiction.

   Conversely, choose arbitrary nilpotent elements as $\rho(2)$ and $\rho(3)$. We must then have $\rho(n)=0$ for every $n\geq4$, since every such number can be written as $n=2i+3j$ with $i+j\geq2$. Every such choice does indeed give a monoid homomorphism $M\to R$. It has an extension to $\mathbb N$ only when

   $$
   \rho(2)=\rho(3)=0.
   $$

   The other eight pairs of nilpotent values have no extension.

6. The six homomorphisms with $\rho(2)$ a unit, the eight nonextendible homomorphisms from part 5, and the one homomorphism that is zero on $M\setminus\{0\}$ give

   $$
   6+8+1=15
   $$

   elements of $\operatorname{Mor}_{\mathrm{mon}}(M,R)$.

[Back to Exercise 18.11](#br-ak-2025-2026-w18-ex-11).

<!-- upstream_solution: Monoidring/Homomorphismus/Spektrumsabbildung nicht surjektiv/Aufgabe/Lösung; pageid=94911; revid=1090073 -->
<!-- upstream_solution_revid: 1090073 -->

## Solution to Exercise 18.15 {#br-ak-2025-2026-w18-sol-15}

Consider the inclusion

$$
\mathbb N\subset\mathbb Z.
$$

For any field $K$, the map

$$
\varphi:\mathbb N\longrightarrow(K,\cdot,1)
$$

that sends $0$ to $1$ and every positive number to $0$ is a monoid homomorphism, and hence a point of $K\!-\!\operatorname{Spek}(K[\mathbb N])$. This homomorphism cannot be extended to a monoid homomorphism on all of $\mathbb Z$, since $1$ is invertible in $\mathbb Z$ and must therefore map to a unit. Thus the spectrum map induced by the inclusion above is not surjective.

[Back to Exercise 18.15](#br-ak-2025-2026-w18-ex-15).

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
