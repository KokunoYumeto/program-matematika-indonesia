---
title: "Public Solutions to Worksheet 8"
stable_id: br-ak-2025-2026-w08-solutions
language: en
upstream_map: authority/wikiversity/unit-08/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 000ee8da757d92c581bb49a4d0e5a23b06393d5af3028f2f97c979fabcf4553d
public_solution_count: 2
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 8 {#br-ak-2025-2026-w08-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 8.9 and 8.17. No additional solutions have been created for this edition.

## Solution to Exercise 8.9 {#br-ak-2025-2026-w08-sol-09}

<!-- upstream_solution_revid: 1096407 -->

With

$$
P_1=(x_1,1)
\qquad\text{and}\qquad
P_2=(x_2,y_2),
$$

we obtain the two conditions

$$
x_2^2+y_2^2=1
$$

and

$$
(x_2-x_1)^2+(y_2-1)^2=4.
$$

Subtracting the first equation from the second gives

$$
\begin{aligned}
0
&=(x_2-x_1)^2+(y_2-1)^2-4-(x_2^2+y_2^2-1)\\
&=x_2^2+x_1^2-2x_1x_2+y_2^2-2y_2+1-4-x_2^2-y_2^2+1\\
&=x_1^2-2x_1x_2-2y_2-2.
\end{aligned}
$$

Together with the unit-circle equation, this equation is equivalent to the original system. From the new second equation, we can eliminate $y_2$ using

$$
y_2=\frac12x_1^2-x_1x_2-1.
$$

Thus the system can be described in $x_1$ and $x_2$ alone, as the zero locus of the polynomial

$$
\begin{aligned}
x_2^2+y_2^2-1
&=x_2^2+\left(\frac12x_1^2-x_1x_2-1\right)^2-1\\
&=x_2^2+\frac14x_1^4+x_1^2x_2^2+1-x_1^3x_2-x_1^2+2x_1x_2-1\\
&=\frac14x_1^4-x_1^3x_2+x_1^2x_2^2-x_1^2+2x_1x_2+x_2^2.
\end{aligned}
$$

[Back to Exercise 8.9](#br-ak-2025-2026-w08-ex-09).

## Solution to Exercise 8.17 {#br-ak-2025-2026-w08-sol-17}

<!-- upstream_solution_revid: 1096408 -->

1. Let

   $$
   P_1=(x_1,y_1)
   $$

   be the point on the circle and

   $$
   P_2=(x_2,0)
   $$

   the point on the $x$-axis. The equations are

   $$
   x_1^2+(y_1-2)^2=1
   $$

   and

   $$
   (x_1-x_2)^2+y_1^2=d^2.
   $$

2. Write

   $$
   f_1=x_1^2+(y_1-2)^2-1
      =x_1^2+y_1^2-4y_1+3
   $$

   and

   $$
   f_2=(x_1-x_2)^2+y_1^2-d^2
      =x_1^2+x_2^2-2x_1x_2+y_1^2-d^2.
   $$

   The Jacobian matrix with respect to $(x_1,x_2,y_1)$ is

   $$
   \begin{pmatrix}
   2x_1 & 0 & 2y_1-4\\
   2x_1-2x_2 & 2x_2-2x_1 & 2y_1
   \end{pmatrix}.
   $$

   Depending on $d$, we must determine at which points the linear map $\mathbb R^3\to\mathbb R^2$ given by this matrix is surjective, that is, has rank $2$. Its rank is not $2$ exactly when every pair of columns is linearly dependent, or equivalently when all $2\times2$ minors vanish. After removing the common factor $4$, the three polynomials are

   $$
   x_1(x_2-x_1),
   \qquad
   (y_1-2)(x_2-x_1),
   \qquad
   x_1y_1-(x_1-x_2)(y_1-2).
   $$

   If $x_1\ne0$, we must have $x_1=x_2$ and $y_1=0$. But this is not a point of the system. Thus $x_1=0$. If $x_2\ne0$, we must have $y_1=2$, which does not satisfy the first equation of the system. Hence $x_2=0$. The system's equations then give

   $$
   (y_1-2)^2=1
   \qquad\text{and}\qquad
   y_1^2=d^2.
   $$

   The first equation forces $y_1=1$ or $y_1=3$, so $d=1$ or $d=3$. Thus the system is regular at every point exactly when $d\ne1,3$.

3. For $d=1$, the calculation above shows that $(0,0,1)$ is the only critical point; indeed it is the only point of the system, which explains the singularity.

   For $d=3$, the point $(0,0,3)$ is the only critical point of the system. It is a crossing point, since the rod can move in four directions there: both coordinates $(x_1,x_2)$ in the positive direction, both in the negative direction, or in either of the two mixed directions.

[Back to Exercise 8.17](#br-ak-2025-2026-w08-ex-17).

---

**Source navigation:** [Worksheet 8](#br-ak-2025-2026-w08) - [Lecture 8](#br-ak-2025-2026-l08)
