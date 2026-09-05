---
title: "Solutions to Worksheet 1 — Algebraic Curves"
stable_id: br-ak-2025-2026-w01-solutions
language: en
upstream_solution_count: 7
upstream_solution_map: "authority/wikiversity/worksheet-01-solutions/ORDERED_EXERCISE_MAP.json"
license: CC BY-SA 4.0
translation_status: complete
---

# Solutions to Worksheet 1 {#br-ak-2025-2026-w01-solutions}

This section translates the seven public solutions linked from Worksheet 1.
Their numbering and order follow the source exercises. No additional solutions
are supplied for exercises without a public solution at the frozen source revision.

## Solution to Exercise 1.4 {#br-ak-2025-2026-w01-sol-04}

<!-- upstream_solution_revid: 1094618 -->

1. $(5,3)$ is an integer solution.

2. We have

   $$
   \begin{aligned}
   \left(\frac{383}{1000}\right)^2
   -\left(\frac{129}{100}\right)^3+2
   &=\frac{146\,689}{1\,000\,000}
     -\frac{2\,146\,689}{1\,000\,000}+2\\
   &=\frac{146\,689-2\,146\,689}{1\,000\,000}+2\\
   &=\frac{-2\,000\,000}{1\,000\,000}+2\\
   &=-2+2\\
   &=0.
   \end{aligned}
   $$

[Back to Exercise 1.4](#br-ak-2025-2026-w01-ex-04).

## Solution to Exercise 1.5 {#br-ak-2025-2026-w01-sol-05}

<!-- upstream_solution_revid: 1096326 -->

Consider the intersection of the curve with the line $V(X-Y)$, imposing the
additional condition $X=Y$. Substituting $Y=X$ into the curve equation gives

$$
X^3-X^3+4X^2-2X^2+X+3=2X^2+X+3=0.
$$

The quadratic formula gives

$$
X=-\frac14\pm\sqrt{-\frac{23}{16}}
  =-\frac14\pm\frac{\sqrt{23}}4i.
$$

Therefore

$$
\left(\frac{-1+\sqrt{23}\,i}{4},
      \frac{-1+\sqrt{23}\,i}{4}\right)
$$

is a point on the curve.

[Back to Exercise 1.5](#br-ak-2025-2026-w01-ex-05).

## Solution to Exercise 1.12 {#br-ak-2025-2026-w01-sol-12}

<!-- upstream_solution_revid: 1094741 -->

Choose the line

$$
G=V(Y+1).
$$

To calculate $C\cap G$, substitute the equation $Y=-1$, which holds on $G$,
into the curve equation. This gives

$$
0=X^3+(-1)^3+1=X^3.
$$

The only solution is $X=0$, so $(0,-1)$ is the unique intersection point of
$G$ and $C$.

[Back to Exercise 1.12](#br-ak-2025-2026-w01-ex-12).

## Solution to Exercise 1.13 {#br-ak-2025-2026-w01-sol-13}

<!-- upstream_solution_revid: 1096436 -->

Every line in the plane has an equation

$$
ax+by=c,
$$

where $a$ and $b$ are not both zero. If the line passes through $(1,1)$,
then $a+b=c$.

If $b=0$, the line is $x=1$ and has the further intersection point $(1,-1)$
with the curve. Hence assume $b\ne0$. Solving the line equation for $y$ gives

$$
y=rx+s,
\qquad s=1-r.
$$

On this line, the curve equation becomes

$$
\begin{aligned}
0
&=y^2-x^3\\
&=(rx+(1-r))^2-x^3\\
&=-x^3+r^2x^2+2r(1-r)x+(1-r)^2.
\end{aligned}
$$

Since $x=1$ is a zero, we can factor out $x-1$:

$$
-x^3+r^2x^2+2r(1-r)x+(1-r)^2
=(x-1)\bigl(-x^2-(1-r^2)x-(1-r)^2\bigr).
$$

After multiplication by $-1$, the quadratic factor on the right is monic of
degree $2$, so it has roots in $\mathbb C$. We must show that at least one
additional root differs from $1$. Evaluating the displayed quadratic factor
at $x=1$ gives

$$
-1-(1-r^2)-(1-r)^2=-3+r^2+2r-r^2=2r-3.
$$

If $r\ne\frac32$, then $1$ is not a root of that quadratic factor. It remains
to consider $r=\frac32$. In this case,

$$
x^2+(1-r^2)x+(1-r)^2
=x^2-\frac54x+\frac14
=(x-1)\left(x-\frac14\right),
$$

so there is another root, $x=\frac14$. Thus every line through $(1,1)$ meets
Neil's parabola in at least one further point.

**Edition note:** The source calls the displayed quadratic factor monic, although its leading coefficient is $-1$. The clarification above makes the multiplication by $-1$ explicit; its roots are unchanged.

[Back to Exercise 1.13](#br-ak-2025-2026-w01-ex-13).

## Solution to Exercise 1.14 {#br-ak-2025-2026-w01-sol-14}

<!-- upstream_solution_revid: 1096438 -->

Substitute $y^2=x^3$ into the circle equation to obtain

$$
x^3+x^2-1=0.
$$

At $x=1$ the polynomial has value $1$, whereas at $x=0.5$ it has a negative
value. By the intermediate value theorem it has a root $x_0$ in $[0.5,1]$.
Since $x_0^3$ is positive, its real square root

$$
y_0=\sqrt{x_0^3}
$$

exists, and $(x_0,y_0)$ is a real intersection point.

To approximate $x_0$ numerically, calculate

$$
(0.7)^3+(0.7)^2-1
<0.49+0.49-1<0
$$

and

$$
\begin{aligned}
(0.8)^3+(0.8)^2-1
&=0.64\cdot0.8+0.64-1\\
&>0.48+0.64-1>0.
\end{aligned}
$$

Thus an intersection point exists whose $x$-coordinate lies in $[0.7,0.8]$.

**Edition note:** The source ends the second estimate with $0.48+0.64-1=0$. This edition uses the correct inequality $0.48+0.64-1>0$.

[Back to Exercise 1.14](#br-ak-2025-2026-w01-ex-14).

## Solution to Exercise 1.20 {#br-ak-2025-2026-w01-sol-20}

<!-- upstream_solution_revid: 1089682 -->

Let $a\in R$ be a unit. There is a $b\in R$ with $ab=1$, and the same
identity holds in the polynomial ring. Hence

$$
R^\times\subseteq R[X]^\times.
$$

Conversely, let

$$
P=\sum_{i=0}^d a_iX^i,
\qquad a_d\ne0,
$$

be a unit in $R[X]$. Then there is a polynomial

$$
Q=\sum_{j=0}^e b_jX^j,
\qquad b_e\ne0,
$$

with $PQ=1$. Since $R$ is an integral domain, $a_db_e\ne0$, and the product
has the form

$$
a_db_eX^{d+e}+\text{terms of lower degree}.
$$

Because $PQ=1$, we must have $d+e=0$ and $a_db_e=1$. Thus $P$ is a constant
unit. Consequently the units of $R[X]$ are precisely the units of $R$.

[Back to Exercise 1.20](#br-ak-2025-2026-w01-ex-20).

## Solution to Exercise 1.21 {#br-ak-2025-2026-w01-sol-21}

<!-- upstream_solution_revid: 1054755 -->

Suppose $K$ is algebraically closed and $F\in K[X]$ is nonconstant. We prove
by induction on $n=\deg F$ that $F$ factors into linear factors.

For $n=1$, we have $F=a_1X+a_0$, so $F$ is already a single linear factor.
Assume every polynomial $G\in K[X]$ of degree $n-1$ factors into linear
factors. Since $K$ is algebraically closed, $F$ has a root $x_0$. We can
therefore write

$$
F=G\cdot(X-x_0)
$$

for a polynomial $G\in K[X]$ of degree $n-1$. This degree assertion follows
directly from the fact that a field is also an integral domain and a slight
adaptation of the proof in Exercise 8. By the induction hypothesis, $G$
factors into linear factors, so $G\cdot(X-x_0)$ does too. Hence every
nonconstant polynomial $F\in K[X]$ factors into linear factors.

Conversely, if every nonconstant polynomial factors into linear factors,
each has a root represented by one of its linear factors. Thus $K$ is
algebraically closed.

**Edition note:** “Exercise 8” is an unlinked reference in the frozen source and does not identify Exercise 1.8 of this worksheet. The degree assertion used here is $\deg(G(X)(X-x_0))=\deg G+1$ over a field; no renumbered source reference is inferred.

[Back to Exercise 1.21](#br-ak-2025-2026-w01-ex-21).
