---
title: "Public Solutions to Worksheet 5"
stable_id: br-ak-2025-2026-w05-solutions
language: en
upstream_map: authority/wikiversity/unit-05/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: d7b9b302ea2a57199d9ff7940f6a8440d50abdc7e4fe1ccdfdd96f27686d84d5
public_solution_count: 4
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 5 {#br-ak-2025-2026-w05-solutions}

The source provides public solutions only to Exercises 5.3, 5.15, 5.19, and
5.20 at the frozen source revisions. No additional solutions have been
created for this edition.

## Solution to Exercise 5.3 {#br-ak-2025-2026-w05-sol-03}

<!-- upstream_solution_revid: 1068012 -->

Let

$$
F=\sum_{i=0}^n a_iX^iY^{n-i}.
$$

Its dehomogenisation is the one-variable polynomial

$$
\widetilde F=\sum_{i=0}^n a_iX^i.
$$

Write $m=\deg\widetilde F$ and suppose $\widetilde F\ne0$. Since the
field is algebraically closed, this polynomial has a factorisation

$$
\widetilde F=a_m\prod_{i=1}^m(X-c_i).
$$

Homogenising again gives the factorisation

$$
F=a_mY^{n-m}\prod_{i=1}^m(X-c_iY).
$$

If $\widetilde F=0$, then $F=0$, so the statement is immediate.

**Edition note:** The source formula places $a_n$ inside the product,
which would produce a factor $a_n^n$, and also tacitly assumes that
$\deg\widetilde F=n$. The formula above places the leading coefficient
$a_m$ once outside the product and includes the factor $Y^{n-m}$ required
when $m<n$.

[Back to Exercise 5.3](#br-ak-2025-2026-w05-ex-03).

## Solution to Exercise 5.15 {#br-ak-2025-2026-w05-sol-15}

<!-- upstream_solution_revid: 1028148 -->

1. Choose a sufficiently general linear form taking distinct values at the
   given points. We may therefore assume that coordinates have been chosen
   so that, for

   $$
   P_i=(a_i,b_i),
   $$

   all the first coordinates $a_i$ are distinct. Let

   $$
   F=(X-a_1)\cdots(X-a_n).
   $$

   By the interpolation theorem, choose a polynomial $H$ in the one variable
   $X$ with

   $$
   H(a_i)=b_i
   $$

   for $i=1,\ldots,n$. With $G=Y-H$, we obtain

   $$
   M=V(F)\cap V(G),
   $$

   expressing $M$ as the intersection of two curves.

2. Replace $F$ by

   $$
   F'=Y-H+F.
   $$

   Then

   $$
   V(G)\cap V(F')=V(G)\cap V(F)=M.
   $$

   Both curves are graphs and are therefore irreducible.

[Back to Exercise 5.15](#br-ak-2025-2026-w05-ex-15).

## Solution to Exercise 5.19 {#br-ak-2025-2026-w05-sol-19}

<!-- upstream_solution_revid: 1096503 -->

Let $K$ be an algebraically closed field. Consider the map

$$
\mathbb A_K^2\longrightarrow\mathbb A_K^1,
\qquad
(x,y)\longmapsto xy.
$$

The fibre over zero is the union of the coordinate axes,

$$
V(xy)=V(x)\cup V(y),
$$

which is reducible. The fibre over a point $\lambda\in K$ with
$\lambda\ne0$ is $V(xy-\lambda)$. It suffices to show that $xy-\lambda$ is
a prime polynomial. This follows from the isomorphism

$$
K[x,y]/(xy-\lambda)\longrightarrow K[u]_u,
\qquad
x\longmapsto u,
\qquad
y\longmapsto\lambda u^{-1},
$$

with inverse $u\mapsto x$. The universal properties of quotient rings and
localisation ensure that these maps really are inverse to one another.

[Back to Exercise 5.19](#br-ak-2025-2026-w05-ex-19).

## Solution to Exercise 5.20 {#br-ak-2025-2026-w05-sol-20}

<!-- upstream_solution_revid: 1096346 -->

1. For $n=2$, since

   $$
   (X-\lambda_1)(X-\lambda_2)
   =X^2-(\lambda_1+\lambda_2)X+\lambda_1\lambda_2,
   $$

   the map is

   $$
   \begin{aligned}
   \varphi:K^2&\longrightarrow K^2,\\
   (\lambda_1,\lambda_2)
   &\longmapsto(\lambda_1\lambda_2,-(\lambda_1+\lambda_2)).
   \end{aligned}
   $$

2. For $n=3$, since

   $$
   \begin{aligned}
   &(X-\lambda_1)(X-\lambda_2)(X-\lambda_3)\\
   &\quad=X^3-(\lambda_1+\lambda_2+\lambda_3)X^2
   +(\lambda_1\lambda_2+\lambda_1\lambda_3
   +\lambda_2\lambda_3)X-\lambda_1\lambda_2\lambda_3,
   \end{aligned}
   $$

   the map is

   $$
   \begin{aligned}
   \varphi:K^3&\longrightarrow K^3,\\
   (\lambda_1,\lambda_2,\lambda_3)
   &\longmapsto\bigl(-\lambda_1\lambda_2\lambda_3,
   \lambda_1\lambda_2+\lambda_1\lambda_3+\lambda_2\lambda_3,
   -(\lambda_1+\lambda_2+\lambda_3)\bigr).
   \end{aligned}
   $$

3. Fix $n\in\mathbb N_+$ and $0\le k\le n-1$. By distributivity, the
   coefficient $c_k$ of $\prod_{i=1}^n(X-\lambda_i)$ is

   $$
   \mathord{\pm}
   \sum_{1\le i_1<i_2<\cdots<i_{n-k}\le n}
   \lambda_{i_1}\lambda_{i_2}\cdots\lambda_{i_{n-k}},
   $$

   with sign determined by the parity of $n-k$. Thus every component function
   is polynomial.

4. A tuple $(\lambda_1,\ldots,\lambda_n)$ belongs to the fibre over the
   coefficient tuple $(c_0,\ldots,c_{n-1})$ precisely when

   $$
   \prod_{i=1}^n(X-\lambda_i)
   =\sum_{j=0}^{n-1}c_jX^j+X^n=P.
   $$

   In particular, all the $\lambda_i$ must be roots of $P$. Since a
   polynomial has only finitely many roots, there are only finitely many
   possible permutations.

5. The fibre over a tuple $(c_0,\ldots,c_{n-1})$ is empty precisely when
   the polynomial

   $$
   \sum_{j=0}^{n-1}c_jX^j+X^n
   $$

   does not split completely into linear factors.

6. Every fibre has at most $n!$ elements. If the polynomial given by the
   coefficient tuple splits completely and its distinct roots have
   multiplicities $m_1,\ldots,m_r$, the fibre consists of all orderings of
   those roots with those multiplicities, and hence has cardinality

   $$
   \frac{n!}{m_1!\cdots m_r!}.
   $$

   If the polynomial does not split completely, the fibre is empty. Thus
   the bound $n!$ is attained when $K$ contains $n$ distinct elements and
   the polynomial has $n$ distinct roots. In particular, for $K=\mathbb R$,
   the root tuple

   $$
   (1,2,3,\ldots,n)
   $$

   maps to a coefficient tuple whose fibre consists of all permutations of
   that root tuple.

   **Edition note:** The source calls $n!$ the maximum without restricting
   the field $K$. The multiplicity count above is an editorial clarification:
   in general, $n!$ is an upper bound, while equality requires at least $n$
   distinct elements in $K$. The example requested in the exercise is
   specifically for $K=\mathbb R$.

7. If $K$ is algebraically closed, every monic polynomial splits into monic
   linear factors. By part 5, each corresponding fibre is nonempty. Thus
   $\varphi$ is surjective.

[Back to Exercise 5.20](#br-ak-2025-2026-w05-ex-20).
