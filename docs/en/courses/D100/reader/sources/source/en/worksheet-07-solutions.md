---
title: "Public Solutions to Worksheet 7"
stable_id: br-ak-2025-2026-w07-solutions
language: en
upstream_map: authority/wikiversity/unit-07/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 8dfcc09854b47d83eaf9179462449a0a1fa307a3a72e5d1f252cfce35858e0e1
public_solution_count: 3
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 7 {#br-ak-2025-2026-w07-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 7.10, 7.11, and 7.22. No additional solutions have been created for this edition.

## Solution to Exercise 7.10 {#br-ak-2025-2026-w07-sol-10}

<!-- upstream_solution_revid: 1113188 -->

The equation

$$
4X^2+3Y^2=9
$$

is equivalent to

$$
\left(\frac{2}{3}X\right)^2
+\left(\frac{1}{\sqrt{3}}Y\right)^2
=1
=\widetilde X^2+\widetilde Y^2.
$$

Thus, over $\mathbb R$,

$$
\widetilde X=\frac{2}{3}X,
\qquad
\widetilde Y=\frac{1}{\sqrt{3}}Y
$$

is an affine-linear transformation.

For the case $\mathbb Q$, we set

$$
\widetilde X=aX+bY+c
$$

and

$$
\widetilde Y=dX+eY+f
$$

with coefficients $a,b,c,d,e,f\in\mathbb Q$. We obtain

$$
\begin{aligned}
\widetilde X^2+\widetilde Y^2
&=(aX+bY+c)^2+(dX+eY+f)^2\\
&=(a^2+d^2)X^2+(b^2+e^2)Y^2
  +2(ab+de)XY+H(X,Y),
\end{aligned}
$$

where $H\in\mathbb Q[X,Y]$ and $\deg H\le 1$.

> **Edition note:** The source immediately compares coefficients at this step. The justification is that an affine equivalence maps the unique centre of either quadric to the unique centre of the other, so $c=f=0$. After normalising the pullback equation to have constant term $-1$, the two quadratic polynomials defining the same locus coincide; comparing the coefficients of $Y^2$ then gives the following equation.

With this justification, we must have

$$
b^2+e^2=\frac{1}{3}
\quad\Longleftrightarrow\quad
3(b^2+e^2)=1.
$$

Clearing denominators puts the equation in the form

$$
3(r^2+s^2)=t^2,
$$

with $r,s,t\in\mathbb Z$. We will show that this equation has no nontrivial integer solution. Since the left-hand side is a multiple of $3$, we obtain $3\mid t$, so $9\mid t^2$. Consequently, $3\mid(r^2+s^2)$. In $\mathbb Z/(3)$, the equation $r^2+s^2=0$ holds exactly when $r=0$ and $s=0$. Hence $9\mid(r^2+s^2)$, and both sides of the equation can be divided by $9$. Now set

$$
r'=\frac r3,
\qquad
s'=\frac s3,
\qquad
t'=\frac t3.
$$

An infinite descent completes the proof.

[Back to Exercise 7.10](#br-ak-2025-2026-w07-ex-10).

## Solution to Exercise 7.11 {#br-ak-2025-2026-w07-sol-11}

<!-- upstream_solution_revid: 1112940 -->

The distance from $P=(x,y)$ to the origin is $\sqrt{x^2+y^2}$, while the perpendicular distance to the line $x=1$ is $\lvert x-1\rvert$. The proportionality is expressed by

$$
\frac{d(P,F)}{d(P,G)}=\sqrt e.
$$

Thus

$$
\sqrt{x^2+y^2}
=\sqrt e\,\lvert x-1\rvert
\quad\text{or, equivalently,}\quad
x^2+y^2=e(x-1)^2.
$$

Consequently,

$$
(1-e)x^2+y^2+2ex-e=0
$$

is an algebraic equation for a curve containing every point satisfying the condition. If $e=1$, the equation becomes

$$
y^2+2ex-e=0
\quad\text{or}\quad
x=-\frac{1}{2e}y^2+\frac{1}{2},
$$

so the curve is a parabola in this case. Henceforth let $e\ne1$. The general equation can be rewritten as

$$
x^2+\frac{1}{1-e}y^2+\frac{2e}{1-e}x-\frac{e}{1-e}=0
$$

and, by completing the square, brought into the form

$$
\left(x+\frac{e}{1-e}\right)^2
+\frac{1}{1-e}y^2
-\frac{e^2}{(1-e)^2}
-\frac{e}{1-e}
=0.
$$

We write this as

$$
\begin{aligned}
\left(x+\frac{e}{1-e}\right)^2+\frac{1}{1-e}y^2
&=\frac{e^2}{(1-e)^2}+\frac{e}{1-e}\\
&=\frac{e^2-e^2+e}{(1-e)^2}\\
&=:c>0.
\end{aligned}
$$

The factor $\frac{1}{1-e}$ is positive for $e<1$ and negative for $e>1$. In the first case, a change of coordinates gives an equation of the form

$$
\widetilde x^2+\widetilde y^2=c,
$$

that is, an ellipse. In the second case, we obtain

$$
\widetilde x^2-\widetilde y^2=c,
$$

that is, a hyperbola.

[Back to Exercise 7.11](#br-ak-2025-2026-w07-ex-11).

## Solution to Exercise 7.22 {#br-ak-2025-2026-w07-sol-22}

<!-- upstream_solution_revid: 1095499 -->

We translate the point $(1,2)$ to the origin by introducing new variables

$$
U=X-1
$$

and

$$
V=Y-2.
$$

The equation then becomes

$$
\begin{aligned}
X^2+Y^2-5
&=(U+1)^2+(V+2)^2-5\\
&=U^2+V^2+2U+4V.
\end{aligned}
$$

Write the translated curve as

$$
\widetilde C=V\left(U^2+V^2+2U+4V\right).
$$

The parametrisation formulas using the line $V=1$ give

$$
P_1=-t(2t+4),
$$

$$
P_2=-(2t+4),
$$

and

$$
Q=t^2+1.
$$

The parametrisation is therefore given by

$$
\mathbb Q\longrightarrow \widetilde C\subset\mathbb A^2_{\mathbb Q},
\qquad
t\longmapsto
\left(
\frac{-t(2t+4)}{t^2+1},
\frac{-(2t+4)}{t^2+1}
\right).
$$

> **Edition note:** The source denotes the intermediate curve in coordinates $(U,V)$ by the same symbol $C$ as the original curve. The symbol $\widetilde C$ is used here to distinguish the translation step from the formulas after translating back.

This gives a parametrisation for the original equation:

$$
X
=-t\frac{2t+4}{t^2+1}+1
=\frac{-t^2-4t+1}{t^2+1}
$$

and

$$
Y
=\frac{-(2t+4)}{t^2+1}+2
=\frac{2t^2-2t-2}{t^2+1}.
$$

[Back to Exercise 7.22](#br-ak-2025-2026-w07-ex-22).
