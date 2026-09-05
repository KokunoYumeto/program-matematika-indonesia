---
title: "Solutions to Worksheet 2 — Affine Algebraic Sets and Ideals"
stable_id: br-ak-2025-2026-w02-solutions
language: en
upstream_solution_count: 9
upstream_solution_map: "authority/wikiversity/unit-02/ORDERED_EXERCISE_MAP.json"
license: CC BY-SA 4.0
translation_status: complete
---

# Solutions to Worksheet 2 {#br-ak-2025-2026-w02-solutions}

This section translates all nine public solutions linked from Worksheet 2 at
the source freeze. Their numbering and order follow the source exercises.
No additional solutions are supplied for exercises without a public solution
at that boundary.

## Solution to Exercise 2.2 {#br-ak-2025-2026-w02-sol-02}

<!-- upstream_solution_revid: 1096652 -->

A direction vector of the line is

$$
\begin{pmatrix}5\\-3\end{pmatrix}.
$$

Its equation therefore has the form

$$
3x+5y=c.
$$

Substituting either point gives $c=2$. Thus

$$
y=\frac{2-3x}{5}.
$$

Substituting this into the circle equation

$$
x^2+y^2=1
$$

gives

$$
x^2+\left(\frac{2-3x}{5}\right)^2=1,
$$

or

$$
x^2+\frac{4-12x+9x^2}{25}-1
=\frac{34}{25}x^2-\frac{12}{25}x-\frac{21}{25}=0.
$$

Normalising the equation gives

$$
x^2-\frac6{17}x-\frac{21}{34}=0.
$$

Consequently,

$$
\begin{aligned}
x_{1,2}
&=\frac{\frac6{17}\pm
\sqrt{\left(\frac6{17}\right)^2+4\cdot\frac{21}{34}}}{2}\\
&=\frac{\frac6{17}\pm
\sqrt{\left(\frac6{17}\right)^2+\frac{42}{17}}}{2}\\
&=\frac{6\pm\sqrt{6^2+714}}{34}\\
&=\frac{6\pm\sqrt{750}}{34}\\
&=\frac{6\pm5\sqrt{30}}{34},
\end{aligned}
$$

and

$$
\begin{aligned}
y_{1,2}
&=\frac{2-3x_{1,2}}5\\
&=\frac{2-3\left(\frac{6\pm5\sqrt{30}}{34}\right)}5\\
&=\frac{68-3(6\pm5\sqrt{30})}{170}\\
&=\frac{50\mp15\sqrt{30}}{170}\\
&=\frac{10\mp3\sqrt{30}}{34}.
\end{aligned}
$$

The intersection points are therefore

$$
\left(\frac{6+5\sqrt{30}}{34},\frac{10-3\sqrt{30}}{34}\right)
\quad\text{and}\quad
\left(\frac{6-5\sqrt{30}}{34},\frac{10+3\sqrt{30}}{34}\right).
$$

[Back to Exercise 2.2](#br-ak-2025-2026-w02-ex-02).

## Solution to Exercise 2.6 {#br-ak-2025-2026-w02-sol-06}

<!-- upstream_solution_revid: 1096317 -->

The unit circle is the solution set of

$$
x^2+y^2=1,
$$

while $K$ is the solution set of

$$
(x-1)^2+y^2=x^2-2x+1+y^2=4.
$$

Subtracting the first equation from the second gives

$$
-2x+1=3,
$$

so $x=-1$. The unit circle equation then gives $y=0$. The only intersection
point is therefore $(-1,0)$, which indeed satisfies both equations.

[Back to Exercise 2.6](#br-ak-2025-2026-w02-ex-06).

## Solution to Exercise 2.7 {#br-ak-2025-2026-w02-sol-07}

<!-- upstream_solution_revid: 1096561 -->

We seek the solutions of the system

$$
x^2+xy+3y^2=3
$$

and

$$
2x^2-xy+y^2=4.
$$

Adding the two equations gives

$$
3x^2+4y^2=7,
$$

while twice the first equation minus the second gives

$$
3xy+5y^2=2.
$$

From the latter equation,

$$
x=\frac{2-5y^2}{3y};
$$

there is certainly no solution with $y=0$. Substituting this expression for
$x$ into the preceding equation gives

$$
3\left(\frac{2-5y^2}{3y}\right)^2+4y^2=7.
$$

Multiplication by $3y^2$ yields

$$
\begin{aligned}
0
&=(2-5y^2)^2+12y^4-21y^2\\
&=4-20y^2+25y^4+12y^4-21y^2\\
&=37y^4-41y^2+4.
\end{aligned}
$$

This is a biquadratic equation.

**Edition note:** The frozen public solution stops here, without giving the intersection coordinates.

[Back to Exercise 2.7](#br-ak-2025-2026-w02-ex-07).

## Solution to Exercise 2.8 {#br-ak-2025-2026-w02-sol-08}

<!-- upstream_solution_revid: 1096094 -->

The standard parabola is given by

$$
y=x^2,
$$

and the unit circle by

$$
x^2+y^2=1.
$$

The intersection points must satisfy both equations simultaneously. Using the
first equation to replace $x^2$ in the second, we obtain

$$
y^2+y-1=0.
$$

Thus

$$
y=\frac{-1\pm\sqrt{1+4}}2=\frac{-1\pm\sqrt5}{2}.
$$

The negative sign gives no real value of $x$, so

$$
y=\frac{-1+\sqrt5}{2},
\qquad
x=\pm\sqrt{\frac{-1+\sqrt5}{2}}.
$$

The two intersection points are

$$
\left(-\sqrt{\frac{-1+\sqrt5}{2}},\frac{-1+\sqrt5}{2}\right)
$$

and

$$
\left(\sqrt{\frac{-1+\sqrt5}{2}},\frac{-1+\sqrt5}{2}\right).
$$

[Back to Exercise 2.8](#br-ak-2025-2026-w02-ex-08).

## Solution to Exercise 2.9 {#br-ak-2025-2026-w02-sol-09}

<!-- upstream_solution_revid: 1096689 -->

1. **Edition note:** The frozen source leaves the sketch item blank.

2. We have

   $$
   \begin{aligned}
   K
   &=\{(x,y)\in\mathbb R^2\mid(y-1)^2+x^2=1\}\\
   &=\{(x,y)\in\mathbb R^2\mid y^2-2y+1+x^2=1\}\\
   &=\{(x,y)\in\mathbb R^2\mid y^2-2y+x^2=0\}.
   \end{aligned}
   $$

3. We seek the common solution set of the two equations

   $$
   y=x^2
   $$

   and

   $$
   y^2-2y+x^2=0.
   $$

   Replacing $x^2$ by $y$ in the second equation gives

   $$
   0=y^2-2y+y=y^2-y=y(y-1).
   $$

   Thus $y=0$ or $y=1$. This gives the three intersection points
   $(0,0)$, $(1,1)$, and $(-1,1)$.

4. The circle equation

   $$
   y^2-2y+x^2=0
   $$

   is equivalent to

   $$
   y^2-2y=-x^2,
   $$

   and hence to

   $$
   (y-1)^2=1-x^2.
   $$

   Therefore

   $$
   y=1\pm\sqrt{1-x^2}.
   $$

   The lower semicircle is the graph of the function

   $$
   [-1,1]\longrightarrow\mathbb R,
   \qquad x\longmapsto1-\sqrt{1-x^2}.
   $$

5. We claim that on $[-1,1]$ the parabola lies above the lower semicircle.
   We must show that

   $$
   x^2\ge1-\sqrt{1-x^2}.
   $$

   This is equivalent to

   $$
   \sqrt{1-x^2}\ge1-x^2.
   $$

   Since both sides are non-negative on this interval, this is equivalent to

   $$
   1-x^2\ge(1-x^2)^2=1+x^4-2x^2.
   $$

   The last inequality is equivalent to $x^4-x^2\le0$, and then to
   $x^2-1\le0$, which holds because $x\in[-1,1]$.

**Edition note:** The source calls both sides positive on $[-1,1]$. They are non-negative and vanish at the endpoints; non-negativity is the condition needed for squaring.

[Back to Exercise 2.9](#br-ak-2025-2026-w02-ex-09).

## Solution to Exercise 2.11 {#br-ak-2025-2026-w02-sol-11}

<!-- upstream_solution_revid: 1094978 -->

1. Let

   $$
   A=\begin{pmatrix}X_1&X_2\\X_3&X_4\end{pmatrix}
   \qquad\text{and}\qquad
   B=\begin{pmatrix}Y_1&Y_2\\Y_3&Y_4\end{pmatrix}.
   $$

   Then

   $$
   AB=
   \begin{pmatrix}X_1&X_2\\X_3&X_4\end{pmatrix}
   \begin{pmatrix}Y_1&Y_2\\Y_3&Y_4\end{pmatrix}
   =\begin{pmatrix}
   X_1Y_1+X_2Y_3&X_1Y_2+X_2Y_4\\
   X_3Y_1+X_4Y_3&X_3Y_2+X_4Y_4
   \end{pmatrix}
   $$

   and

   $$
   BA=
   \begin{pmatrix}Y_1&Y_2\\Y_3&Y_4\end{pmatrix}
   \begin{pmatrix}X_1&X_2\\X_3&X_4\end{pmatrix}
   =\begin{pmatrix}
   X_1Y_1+X_3Y_2&X_2Y_1+X_4Y_2\\
   X_1Y_3+X_3Y_4&X_2Y_3+X_4Y_4
   \end{pmatrix}.
   $$

   These product matrices are equal precisely when all four corresponding
   entries agree, that is, when

   $$
   X_1Y_1+X_2Y_3=X_1Y_1+X_3Y_2,
   $$

   $$
   X_1Y_2+X_2Y_4=X_2Y_1+X_4Y_2,
   $$

   $$
   X_3Y_1+X_4Y_3=X_1Y_3+X_3Y_4,
   $$

   and

   $$
   X_3Y_2+X_4Y_4=X_2Y_3+X_4Y_4.
   $$

   Thus the set is an affine variety. The first and fourth equations are
   equivalent to each other and to

   $$
   X_2Y_3=X_3Y_2.
   $$

   The commuting matrices are therefore described by the system

   $$
   X_2Y_3=X_3Y_2,
   $$

   $$
   X_1Y_2+X_2Y_4=X_2Y_1+X_4Y_2,
   $$

   $$
   X_3Y_1+X_4Y_3=X_1Y_3+X_3Y_4.
   $$

2. The identity matrix $E_2$ commutes with every matrix. Hence $(A,E_2)$ is
   a preimage of $A$.

3. We seek the matrices

   $$
   B=\begin{pmatrix}Y_1&Y_2\\Y_3&Y_4\end{pmatrix}
   $$

   that satisfy the preceding system for

   $$
   A=\begin{pmatrix}X_1&X_2\\X_3&X_4\end{pmatrix}
   =\begin{pmatrix}1&1\\0&0\end{pmatrix}.
   $$

   The conditions become

   $$
   Y_3=0,
   \qquad
   Y_2+Y_4=Y_1,
   \qquad
   0=Y_3,
   $$

   and the third condition can be omitted. The inverse image of the given matrix is

   $$
   \left\{
   \left(
   \begin{pmatrix}1&1\\0&0\end{pmatrix},
   \begin{pmatrix}Y_2+Y_4&Y_2\\0&Y_4\end{pmatrix}
   \right)
   \;\middle|\;Y_2,Y_4\in K
   \right\}.
   $$

[Back to Exercise 2.11](#br-ak-2025-2026-w02-ex-11).

## Solution to Exercise 2.15 {#br-ak-2025-2026-w02-sol-15}

<!-- upstream_solution_revid: 1089351 -->

First we prove $\mathfrak b\subseteq\mathfrak a$ by showing that every
generator of $\mathfrak b$ is $0$ in the quotient ring modulo $\mathfrak a$.
In that ring,

$$
\begin{aligned}
X^2+Y^2
&=(2Z^2-1)^2+4Z^2W^2\\
&=(2Z^2-1)^2+4Z^2(1-Z^2)\\
&=4Z^4-4Z^2+1+4Z^2-4Z^4\\
&=1.
\end{aligned}
$$

Moreover,

$$
\begin{aligned}
YW
&=2ZW^2\\
&=2Z(1-Z^2)\\
&=Z(2-2Z^2)\\
&=Z(1-2Z^2+1)\\
&=Z(1-X),
\end{aligned}
$$

and

$$
\begin{aligned}
W(1+X)
&=W(2Z^2)\\
&=2WZ^2\\
&=ZY.
\end{aligned}
$$

The inclusion $\mathfrak c\subseteq\mathfrak b$ is clear, since one generator
has been omitted.

Finally, we prove $\mathfrak a\subseteq\mathfrak c$ by showing that the
generators of $\mathfrak a$ are $0$ in the quotient ring modulo $\mathfrak c$.
In this ring,

$$
ZX=Z-YW
\qquad\text{and}\qquad
WX=YZ-W.
$$

Consequently,

$$
\begin{aligned}
X
&=X\cdot1\\
&=X(Z^2+W^2)\\
&=Z^2-ZYW+YZW-W^2\\
&=Z^2-W^2\\
&=2Z^2-1,
\end{aligned}
$$

and

$$
\begin{aligned}
Y
&=Y\cdot1\\
&=Y(Z^2+W^2)\\
&=WXZ+WZ+ZW-ZXW\\
&=2ZW.
\end{aligned}
$$

[Back to Exercise 2.15](#br-ak-2025-2026-w02-ex-15).

## Solution to Exercise 2.16 {#br-ak-2025-2026-w02-sol-16}

<!-- upstream_solution_revid: 1112335 -->

1. Clearly $(1,1)$ is a zero of $F$.

2. We have

   $$
   \begin{aligned}
   F\cdot(X^2+Y^2+1)
   ={}&(X^4Y^2+X^2Y^4-3X^2Y^2+1)(X^2+Y^2+1)\\
   ={}&X^6Y^2+X^4Y^4-3X^4Y^2+X^2
   +X^4Y^4+X^2Y^6-3X^2Y^4+Y^2\\
   &+X^4Y^2+X^2Y^4-3X^2Y^2+1\\
   ={}&2X^4Y^4+X^6Y^2+X^2Y^6-2X^4Y^2-2X^2Y^4
   -3X^2Y^2+X^2+Y^2+1.
   \end{aligned}
   $$

   For the other side,

   $$
   (X^2Y-Y)^2+(XY^2-X)^2+(X^2Y^2-1)^2
   +\frac14(XY^3-X^3Y)^2
   +\frac34(XY^3+X^3Y-2XY)^2,
   $$

   we calculate the coefficient of each monomial. Only even degrees occur,
   and the highest degree is $8$. Only the last three summands contribute at
   that degree, and the only monomials are $X^6Y^2$, $X^4Y^4$, and $X^2Y^6$:

   $$
   X^6Y^2:\quad\frac14+\frac34=1,
   $$

   $$
   X^4Y^4:\quad1+\frac14(-2)+\frac34(2)=2,
   $$

   $$
   X^2Y^6:\quad\frac14+\frac34=1.
   $$

   In degree $6$, only $X^4Y^2$ and $X^2Y^4$ occur:

   $$
   X^4Y^2:\quad1+\frac34(-4)=-2,
   $$

   $$
   X^2Y^4:\quad1+\frac34(-4)=-2.
   $$

   In degree $4$, only $X^2Y^2$ occurs:

   $$
   X^2Y^2:\quad-2-2-2+\frac34(4)=-3.
   $$

   In degree $2$, the coefficients of $X^2$ and $Y^2$ are both $1$.
   In degree $0$, the coefficient of $1$ is also $1$. Thus the two sides agree.

3. Dividing the identity in part (2) by $X^2+Y^2+1$ in the field of fractions
   of $K[X,Y]$, we obtain

   $$
   \begin{aligned}
   F=\frac{1}{X^2+Y^2+1}\Big(& (X^2Y-Y)^2+(XY^2-X)^2
   +(X^2Y^2-1)^2\\
   &+\frac14(XY^3-X^3Y)^2
   +\frac34(XY^3+X^3Y-2XY)^2\Big).
   \end{aligned}
   $$

   Since $X^2+Y^2+1$ has no real zero, this identity also holds as an identity
   of functions $\mathbb R^2\to\mathbb R$. Squares are never negative, and
   all coefficients of the squares involved are positive. Hence the function
   is non-negative at every point.

**Edition note:** The source's introductory sentence for degree $2$ mentions only $X^2$, but its coefficient list includes both $X^2$ and $Y^2$. The wording above follows that list and the displayed expansion.

[Back to Exercise 2.16](#br-ak-2025-2026-w02-ex-16).

## Solution to Exercise 2.20 {#br-ak-2025-2026-w02-sol-20}

<!-- upstream_solution_revid: 1096251 -->

To prove the inclusion $\subseteq$, take $f\in(I+J)^n$. Since a product of
ideals consists of all sums of products, we can write

$$
f=f_1+f_2+\cdots+f_k,
$$

where

$$
f_\ell=c_{\ell1}c_{\ell2}\cdots c_{\ell n},
$$

with $c_{\ell r}\in I+J$. In turn,

$$
c_{\ell r}=a_{\ell r}+b_{\ell r}
$$

with $a_{\ell r}\in I$ and $b_{\ell r}\in J$. Thus

$$
f_\ell=(a_{\ell1}+b_{\ell1})(a_{\ell2}+b_{\ell2})
\cdots(a_{\ell n}+b_{\ell n}).
$$

Expanding this product by distributivity gives a sum of products with $n$
factors each: $s$ factors belong to $I$ and $n-s$ to $J$. Each summand
therefore belongs to the right-hand side, as do each $f_\ell$ and finally $f$.

To prove the inclusion $\supseteq$, it suffices to show

$$
I^sJ^{n-s}\subseteq(I+J)^n
$$

for every $s$. Since $I,J\subseteq I+J$, we immediately have

$$
I^sJ^{n-s}
\subseteq(I+J)^s(I+J)^{n-s}
=(I+J)^n.
$$

[Back to Exercise 2.20](#br-ak-2025-2026-w02-ex-20).
