---
title: "Public Solutions to Worksheet 4"
stable_id: br-ak-2025-2026-w04-solutions
language: en
upstream_map: authority/wikiversity/unit-04/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: a6e2631e9b4156d5f32bf5f55c1a201987f9da9c41d247d51755fb8727079420
public_solution_count: 6
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 4 {#br-ak-2025-2026-w04-solutions}

The source provides public solutions only to Exercises 4.10, 4.11, 4.12,
4.14, 4.15, and 4.17 at the frozen revision boundary. No additional solutions
have been created for this edition.

## Solution to Exercise 4.10 {#br-ak-2025-2026-w04-sol-10}

<!-- upstream_solution_revid: 1067858 -->

We prove the isomorphism

$$
K[X,Y]/(Y-F,Y-G)\cong K[X]/(F-G).
$$

Consider the $K$-algebra homomorphism

$$
\varphi:K[X,Y]\longrightarrow K[X]/(F-G)
$$

that sends $X\mapsto X$ and $Y\mapsto F$. We have

$$
\varphi(Y-F)=F-F=0
$$

and

$$
\varphi(Y-G)=F-G=0.
$$

The homomorphism theorem for rings gives an induced $K$-algebra homomorphism

$$
\overline\varphi:
K[X,Y]/(Y-F,Y-G)\longrightarrow K[X]/(F-G).
$$

Now consider the $K$-algebra homomorphism

$$
\psi:K[X]\longrightarrow K[X,Y]/(Y-F,Y-G)
$$

with $X\mapsto X$. In the target ring,

$$
\psi(F-G)=F-G=(Y-G)-(Y-F)=0.
$$

This therefore induces a homomorphism

$$
\overline\psi:
K[X]/(F-G)\longrightarrow K[X,Y]/(Y-F,Y-G).
$$

Both compositions $\overline\psi\circ\overline\varphi$ and
$\overline\varphi\circ\overline\psi$ are the respective identity maps.

[Back to Exercise 4.10](#br-ak-2025-2026-w04-ex-10).

## Solution to Exercise 4.11 {#br-ak-2025-2026-w04-sol-11}

<!-- upstream_solution_revid: 1067949 -->

1. A circle equation has the form

   $$
   (X-a)^2+(Y-b)^2-c=0.
   $$

   Expanding, write

   $$
   F=X^2+Y^2+rX+sY+t
   $$

   and similarly

   $$
   G=X^2+Y^2+\widetilde rX+\widetilde sY+\widetilde t.
   $$

   Then

   $$
   H=F-G=(r-\widetilde r)X+(s-\widetilde s)Y
   +(t-\widetilde t).
   $$

   Since the circles are distinct, $H$ has degree $1$ or $0$. Moreover,

   $$
   (F,G)=(F,H),
   $$

   so their quotient rings are isomorphic.

2. Use the description from the first part:

   $$
   R=K[X,Y]/(F,H).
   $$

   If $H$ is a nonzero constant, $R$ is the zero ring. Otherwise $H$ is
   linear, so one variable can be expressed in terms of the other; say

   $$
   Y=\alpha X+\beta.
   $$

   Hence

   $$
   \begin{aligned}
   K[X,Y]/(F,H)
   &\cong K[X,Y]/(X^2+Y^2+rX+sY+t,\,Y-\alpha X-\beta)\\
   &\cong K[X]/\bigl(X^2+(\alpha X+\beta)^2+rX
     +s(\alpha X+\beta)+t\bigr)\\
   &\cong K[X]/(uX^2+vX+w).
   \end{aligned}
   $$

[Back to Exercise 4.11](#br-ak-2025-2026-w04-ex-11).

## Solution to Exercise 4.12 {#br-ak-2025-2026-w04-sol-12}

<!-- upstream_solution_revid: 1110006 -->

Consider the surjective evaluation homomorphism

$$
R[X]\longrightarrow R/(G_1,\ldots,G_n),
\qquad
X\longmapsto[r].
$$

The generator $F_0=X-r$ maps to $0$, and for $i\ge1$, the generator $F_i$
maps to $G_i=0$. The homomorphism theorem gives a surjective ring homomorphism

$$
\varphi:R[X]/\mathfrak a\longrightarrow R/(G_1,\ldots,G_n).
$$

It remains to prove injectivity. Suppose that

$$
P=a_0+a_1X+\cdots+a_mX^m\in R[X]
$$

maps to $0$ under $\varphi$. This means that

$$
P(r)=a_0+a_1r+\cdots+a_mr^m
\in(G_1,\ldots,G_n)
$$

in $R$. Furthermore,

$$
\begin{aligned}
P-P(r)
&=\sum_{i=0}^m a_iX^i-\sum_{i=0}^m a_ir^i\\
&=\sum_{i=0}^m a_i(X^i-r^i)\\
&=\sum_{i=1}^m a_i(X^i-r^i)\\
&=\sum_{i=1}^m (X-r)H_i,
\end{aligned}
$$

since $X^i-r^i$ is always divisible by $X-r$. Thus

$$
P-P(r)\in(X-r),
$$

and altogether

$$
P\in(X-r,G_1,\ldots,G_n).
$$

For suitable elements $B_i$, we also have

$$
F_i-G_i=F_i-F_i(r)=(X-r)B_i.
$$

Consequently,

$$
\begin{aligned}
P&\in(X-r,G_1,\ldots,G_n)\\
&=(X-r,F_1,\ldots,F_n)\\
&=\mathfrak a.
\end{aligned}
$$

Thus $\varphi$ is injective and is the required isomorphism.

[Back to Exercise 4.12](#br-ak-2025-2026-w04-ex-12).

## Solution to Exercise 4.14 {#br-ak-2025-2026-w04-sol-14}

<!-- upstream_solution_revid: 1075363 -->

For $p=2$, the statement can be checked directly. Suppose that $p\ge3$.
Write the equation as

$$
aX^2=-bY^2-c.
$$

Since $a$ and $b$ are units, the theorem on the number of quadratic residues
shows that the sets of values on the left and on the right each contain
$(p+1)/2$ elements. The field $\mathbb Z/(p)$ has only $p$ elements, so the
two sets cannot be disjoint. Thus there is a $d\in\mathbb Z/(p)$ that can
be written as

$$
d=aX^2=-bY^2-c
$$

for suitable $X,Y\in\mathbb Z/(p)$. This pair solves the original equation.

[Back to Exercise 4.14](#br-ak-2025-2026-w04-ex-14).

## Solution to Exercise 4.15 {#br-ak-2025-2026-w04-sol-15}

<!-- upstream_solution_revid: 1072981 -->

First let $\mathfrak a$ be a prime ideal. By the [characterisation of prime ideals by quotient rings](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Primideal/Charakterisierung_mit_Restklassenring/Fakt), $R/\mathfrak a$ is an integral
domain and therefore has a field of fractions $Q(R/\mathfrak a)$. The
composition of the canonical projection with the inclusion into this field,

$$
\varphi:R\longrightarrow Q(R/\mathfrak a),
\qquad
x\longmapsto[x],
$$

is a ring homomorphism to a field with

$$
\ker\varphi=\mathfrak a.
$$

Conversely, the kernel of a ring homomorphism

$$
\varphi:R\longrightarrow K
$$

is always an ideal, by the [kernel-ideal theorem](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Ringhomomorphismus/Kern_ist_Ideal/Fakt). If $ab\in\ker\varphi$, then

$$
0=\varphi(ab)=\varphi(a)\varphi(b).
$$

Since [a field is an integral domain](https://de.wikiversity.org/wiki/K%C3%B6rper/Integrit%C3%A4tsbereich/Fakt), $K$ has no zero divisors, so either $\varphi(a)=0$ or
$\varphi(b)=0$. Equivalently, $a\in\ker\varphi$ or $b\in\ker\varphi$.
Thus $\ker\varphi$ is a prime ideal.

**Edition note:** The source calls the map to $Q(R/\mathfrak a)$ the canonical projection. More precisely, it is the quotient projection followed by the inclusion into the field of fractions, as stated above.

[Back to Exercise 4.15](#br-ak-2025-2026-w04-ex-15).

## Solution to Exercise 4.17 {#br-ak-2025-2026-w04-sol-17}

<!-- upstream_solution_revid: 485196 -->

First let $\mathfrak p$ be a prime ideal. In particular,
$\mathfrak p\subsetneq R$, so $R/\mathfrak p$ is not the zero ring.
Suppose that $fg=0$ in $R/\mathfrak p$, with $f$ and $g$ represented by
elements of $R$. Then $fg\in\mathfrak p$, so $f\in\mathfrak p$ or
$g\in\mathfrak p$. In $R/\mathfrak p$, this means exactly that $f=0$ or
$g=0$. Thus $R/\mathfrak p$ is an integral domain.

Conversely, suppose that $R/\mathfrak p$ is an integral domain. This quotient
is not the zero ring, so $\mathfrak p\ne R$. If $f,g\notin\mathfrak p$,
their classes are both nonzero in $R/\mathfrak p$. Since the ring is an
integral domain, their product is nonzero. Hence

$$
fg\notin\mathfrak p.
$$

Taking the contrapositive, $fg\in\mathfrak p$ forces
$f\in\mathfrak p$ or $g\in\mathfrak p$. Thus $\mathfrak p$ is prime.

[Back to Exercise 4.17](#br-ak-2025-2026-w04-ex-17).
