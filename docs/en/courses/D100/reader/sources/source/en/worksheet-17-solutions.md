---
title: "Public Solutions to Worksheet 17"
stable_id: br-ak-2025-2026-w17-solutions
language: en
upstream_map: authority/wikiversity/unit-17/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: f329f9d1a6fc2e862009acd4761ed8289da2cf4c8b42e057db275642c05a700e
public_solution_count: 4
upstream_solution_revisions: "Soal 17.3=1068109; Soal 17.12=1090071; Soal 17.31=1090074; Soal 17.32=1090075"
solution_xml_sha256: "03=bf3b5ded9092bb12d4122ad46b5e37fd250bee2f36bc8709118fcfb128e59d2f; 12=d9cf94dfdb7f48983599c1ee8780ef83e2018e64b6a5146f30659534a33e5a41; 31=4ff966c557cc67bc3bd5292598370ec87b6f65f8d00e515b9a66118c33b7a878; 32=6ea35355e869b4f3eda794d1faf1e079b57d066a9b304b753d6ac8571f574b02"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 17 {#br-ak-2025-2026-w17-solutions}

At the frozen revision boundary, the source provides public solutions
only for Exercises 17.3, 17.12, 17.31, and 17.32. No additional solutions
have been created for this edition.

<!-- upstream_solution: Z mod 3/Gruppenring/Rechenbeispiel/1/Aufgabe/Lösung; pageid=168445; revid=1068109 -->
<!-- upstream_solution_revid: 1068109 -->

## Solution to Exercise 17.3 {#br-ak-2025-2026-w17-sol-03}

In $\mathbb Z/(7)[\mathbb Z/(3)]$, coefficients are calculated modulo
$7$ and exponents of $T$ modulo $3$. Thus

$$
\begin{aligned}
&(3T^0-2T^1+5T^2)(4T^0-6T^1+5T^2)\\
&=(3T^0+5T^1+5T^2)(4T^0+T^1+5T^2)\\
&=5T^0+3T^1+T^2+6T^1+5T^2+4T^0
  +6T^2+5T^0+4T^1\\
&=6T+5T^2.
\end{aligned}
$$

[Back to Exercise 17.3](#br-ak-2025-2026-w17-ex-03).

<!-- upstream_solution: Monoid/Einheit/Ring/Umkehrung/Aufgabe/Lösung; pageid=95159; revid=1090071 -->
<!-- upstream_solution_revid: 1090071 -->

## Solution to Exercise 17.12 {#br-ak-2025-2026-w17-sol-12}

If $m$ is a unit in $M$, there is an $n\in M$ with

$$
m+n=0.
$$

Then

$$
T^mT^n=T^{m+n}=T^0=1,
$$

so $T^m$ is a unit in the monoid ring.

Conversely, suppose $T^m$ is a unit in the monoid ring. There is an element

$$
P=\sum_{n\in E}a_nT^n
$$

with finite support $E\subseteq M$, all displayed coefficients
$a_n\in K$ nonzero, and

$$
T^mP=\sum_{n\in E}a_nT^{m+n}=1.
$$

The coefficient of $T^0$ on the left is $1$, so there is at least one
$n\in E$ such that

$$
m+n=0.
$$

Thus $m$ has an inverse in $M$.

**Edition note:** the source passes directly to the assertion that all
exponents $m+n$ equal zero. The argument above first uses the coefficient
of $T^0$ to obtain one such $n$, which already proves that $m$ is a unit.
Translation by $m$ is then bijective, so the source's stronger assertion
also follows. This ordering avoids assuming cancellation prematurely.

[Back to Exercise 17.12](#br-ak-2025-2026-w17-ex-12).

<!-- upstream_solution: Monoidring/Q geq 0/Über K/Teiler von X/Aufgabe/Lösung; pageid=72875; revid=1090074 -->
<!-- upstream_solution_revid: 1090074 -->

## Solution to Exercise 17.31 {#br-ak-2025-2026-w17-sol-31}

The divisors of $X$ are exactly the elements of the form

$$
aX^q,
\qquad a\ne0,
\qquad q\in\mathbb Q_{\geq0},
\qquad q\leq1.
$$

Every such element is indeed a divisor, since

$$
(aX^q)(a^{-1}X^{1-q})
=X^qX^{1-q}
=X^{q+1-q}
=X.
$$

Conversely, let

$$
P=a_{q_1}X^{q_1}+a_{q_2}X^{q_2}+\cdots+a_{q_n}X^{q_n},
\qquad
0\leq q_1<q_2<\cdots<q_n,
$$

be a divisor of $X$. There is then a

$$
Q=b_{r_1}X^{r_1}+b_{r_2}X^{r_2}+\cdots+b_{r_m}X^{r_m},
\qquad
0\leq r_1<r_2<\cdots<r_m,
$$

with all displayed coefficients nonzero and $PQ=X$. The lowest- and
highest-exponent terms in the product are

$$
a_{q_1}b_{r_1}X^{q_1+r_1}
\quad\text{and}\quad
a_{q_n}b_{r_m}X^{q_n+r_m};
$$

both are nonzero. For $PQ=X$, we must have

$$
q_1+r_1=q_n+r_m=1.
$$

Since the exponents are strictly ordered, this is possible only if
$n=m=1$. Thus $P=aX^q$ with $0\leq q\leq1$, as claimed.

**Edition note:** in the final extreme term, the source prints
$a_{q_n}b_{r_n}$, although the support of $Q$ has $m$ terms and the next
line itself uses $r_m$. This edition displays the terminal index
$a_{q_n}b_{r_m}$.

[Back to Exercise 17.31](#br-ak-2025-2026-w17-ex-31).

<!-- upstream_solution: Monoidring/Q/Über K/Einheiten/Aufgabe/Lösung; pageid=72879; revid=1090075 -->
<!-- upstream_solution_revid: 1090075 -->

## Solution to Exercise 17.32 {#br-ak-2025-2026-w17-sol-32}

The units are exactly the elements of the form

$$
aX^q,
\qquad a\ne0,
\qquad q\in\mathbb Q.
$$

Such an element is a unit because

$$
(aX^q)(a^{-1}X^{-q})
=X^qX^{-q}
=X^{q-q}
=X^0
=1.
$$

Conversely, let

$$
P=a_{q_1}X^{q_1}+a_{q_2}X^{q_2}+\cdots+a_{q_n}X^{q_n},
\qquad
q_1<q_2<\cdots<q_n,
$$

be a unit. There is a

$$
Q=b_{r_1}X^{r_1}+b_{r_2}X^{r_2}+\cdots+b_{r_m}X^{r_m},
\qquad
r_1<r_2<\cdots<r_m,
$$

with all displayed coefficients nonzero and $PQ=1$. The lowest- and
highest-exponent terms in the product are

$$
a_{q_1}b_{r_1}X^{q_1+r_1}
\quad\text{and}\quad
a_{q_n}b_{r_m}X^{q_n+r_m},
$$

and both are nonzero. For the product to equal $1$, we must have

$$
q_1+r_1=q_n+r_m=0.
$$

The strict ordering of the exponents forces $n=m=1$. Thus $P=aX^q$.

[Back to Exercise 17.32](#br-ak-2025-2026-w17-ex-32).
