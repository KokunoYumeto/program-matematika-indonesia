---
title: "Public Solutions to Worksheet 22"
stable_id: br-ak-2025-2026-w22-solutions
language: en
upstream_map: authority/wikiversity/unit-22/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: d4b1d1f0a08de69d6fb7da513b8bce9ebaf697d5dad51632d0db063925d05f1e
public_solution_count: 9
upstream_solution_revisions: "Exercise 22.5=971273; Exercise 22.6=1067646; Exercise 22.9=1067974; Exercise 22.10=1067981; Exercise 22.12=1096085; Exercise 22.14=958122; Exercise 22.15=1089314; Exercise 22.16=1089323; Exercise 22.18=1094625"
solution_xml_sha256: "05=87338c889aad1ab68dc84d26c1d1d3e87786e3a856b2336ad88214e3fc24865d; 06=2f2912b1c2a934f58904cc198db011f2a981322f5858f95376c677cfffabca3a; 09=5d141458a1d3e0c8ee28730993263299cc7e82d7ce6a2287c4c1ee745840c1ca; 10=739b5ce54439877c6f8bced7ee413374eadb8df77f1df2f0b92180e2e5beb926; 12=7c112582720b0695d98642cb498502a99159e33fb53b718e3233a7cf10e4c5c7; 14=68bcfe6fe279f0a5f0e41a138ddaab9e29a95271f66d8591e570d0263fd93af7; 15=a09ce8c91da266cdf44ff73fbdde6710965c2b39c82531d6e473e65bfe034e82; 16=5de4d530da5eec27a612859cd8bfe4c9f714fcd0e1dd9fbdb53555532e9c9da7; 18=946fd900982637115aaf775bb264bc1a30838342f03ef5c73c0ac0376379edd8"
solution_ex09_transclusion: "proof pageid=84110; proof revid=1101009; json_sha256=6fdee6cc2b0b469aad230fc3094543e94c09bba93f3211986f7705c90e672aaa"
license: "CC BY-SA 4.0"
translation_status: complete
source_corrections: 2
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 22 {#br-ak-2025-2026-w22-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 22.5, 22.6, 22.9, 22.10, 22.12, 22.14, 22.15, 22.16, and
22.18. No additional solutions have been created for this edition. The
solution to Exercise 22.9 transcludes a proof page; the text below translates
the actual proof body from the frozen recursive transclusion closure.

<!-- upstream_solution: Homogenes Polynom/Partielle Ableitung/Dehomogenisierung/Aufgabe/Lösung; pageid=96914; revid=971273 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=971273 -->

## Solution to Exercise 22.5 {#br-ak-2025-2026-w22-sol-05}

1. Since both processes are linear, it suffices to consider a monomial

   $$
   X_1^{\nu_1}X_2^{\nu_2}X_3^{\nu_3}\cdots X_n^{\nu_n},
   $$

   differentiating with respect to $X_1$ and dehomogenising with respect to
   $X_2$. Its partial derivative is

   $$
   \nu_1X_1^{\nu_1-1}X_2^{\nu_2}X_3^{\nu_3}\cdots X_n^{\nu_n},
   $$

   and dehomogenisation gives

   $$
   \nu_1X_1^{\nu_1-1}X_3^{\nu_3}\cdots X_n^{\nu_n}.
   $$

   If we dehomogenise first, we obtain

   $$
   X_1^{\nu_1}X_3^{\nu_3}\cdots X_n^{\nu_n},
   $$

   whose partial derivative likewise gives

   $$
   \nu_1X_1^{\nu_1-1}X_3^{\nu_3}\cdots X_n^{\nu_n}.
   $$

2. Consider $X_1$. Differentiating with respect to $X_1$ gives $1$, which
   is unchanged by dehomogenisation. If we first dehomogenise with respect
   to $X_1$, we obtain $1$, whose derivative is $0$.

[Back to Exercise 22.5](#br-ak-2025-2026-w22-ex-05).

<!-- upstream_solution: Homogenes Polynom/Darstellung mit formalen partiellen Ableitungen/Aufgabe/Lösung; pageid=168373; revid=1067646 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1067646 -->

## Solution to Exercise 22.6 {#br-ak-2025-2026-w22-sol-06}

Since partial differentiation and multiplication by a variable are linear,
it suffices to prove the statement for a monomial. Thus let

$$
H=X_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n}.
$$

Then

$$
\begin{aligned}
X_1\frac{\partial H}{\partial X_1}+\cdots+
X_n\frac{\partial H}{\partial X_n}
&=\nu_1X_1\cdot X_1^{\nu_1-1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n} \\
&\quad+\nu_2X_2\cdot X_1^{\nu_1}\cdot X_2^{\nu_2-1}\cdots X_n^{\nu_n}
+\cdots \\
&\quad+\nu_nX_n\cdot X_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n-1} \\
&=\nu_1X_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n}
+\nu_2X_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n}
+\cdots \\
&\quad+\nu_nX_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n} \\
&=(\nu_1+\nu_2+\cdots+\nu_n)
X_1^{\nu_1}\cdot X_2^{\nu_2}\cdots X_n^{\nu_n}.
\end{aligned}
$$

This is the required statement, since the sum of the exponents is the
degree of the monomial.

[Back to Exercise 22.6](#br-ak-2025-2026-w22-ex-06).

<!-- upstream_solution: Ebene algebraische Kurve/Glatter Punkt/Liegt nur auf einer Komponente/Fakt/Beweis/Aufgabe/Lösung; pageid=168407; revid=1067974 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1067974 -->
<!-- frozen_transclusion: Ebene algebraische Kurve/Glatter Punkt/Liegt nur auf einer Komponente/Fakt/Beweis; pageid=84110; revid=1101009 -->

## Solution to Exercise 22.9 {#br-ak-2025-2026-w22-sol-09}

Since $P$ is a smooth point of the curve, we may assume without loss of
generality that

$$
\frac{\partial F}{\partial X}(P)\neq0.
$$

By the product rule,

$$
\begin{aligned}
\frac{\partial F}{\partial X}(P)
&=\frac{\partial(F_1\cdots F_n)}{\partial X}(P) \\
&=\sum_{k=1}^n
F_1(P)\cdots F_{k-1}(P)\cdot
\frac{\partial F_k}{\partial X}(P)\cdot
F_{k+1}(P)\cdots F_n(P).
\end{aligned}
$$

Now suppose that

$$
P\in C_i\cap C_j
$$

for $i\neq j$, that is,

$$
F_i(P)=F_j(P)=0.
$$

Every product in the sum above would then have a zero factor, so

$$
\frac{\partial F}{\partial X}(P)=0,
$$

contrary to the smoothness of $P$.

[Back to Exercise 22.9](#br-ak-2025-2026-w22-ex-09).

<!-- upstream_solution: Ebene algebraische Kurven/Einheitskreis/Bestimme Tangente/Aufgabe/Lösung; pageid=168408; revid=1067981 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1067981 -->

## Solution to Exercise 22.10 {#br-ak-2025-2026-w22-sol-10}

The defining polynomial is

$$
X^2+Y^2-1,
$$

and its partial derivatives are $2X$ and $2Y$. Since the characteristic is
assumed not to be $2$ and the origin is not on the circle, the curve is
smooth. By the remark on the tangent-line equation at a smooth point in
Lecture 22, at a point $(a,b)$ on the circle the tangent-line equation is

$$
2a(X-a)+2b(Y-b)=0.
$$

After dividing by $2$, this can be written as

$$
aX+bY-a^2-b^2=aX+bY-1=0.
$$

**Edition note — source correction.** The source prints only the left-hand
expressions while calling them “tangent-line equations”. This edition
restores the equality to zero that makes them actual equations.

[Back to Exercise 22.10](#br-ak-2025-2026-w22-ex-10).

<!-- upstream_solution: Ebene Kurve/-2x^3+3x^2y-y+2/3 \sqrt(1/3)/C/Singularitäten/Aufgabe/Lösung; pageid=21571; revid=1096085 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1096085 -->

## Solution to Exercise 22.12 {#br-ak-2025-2026-w22-sol-12}

Let $F$ be the defining polynomial. Its partial derivatives are

$$
\frac{\partial F}{\partial X}=-6X^2+6XY
\quad\text{and}\quad
\frac{\partial F}{\partial Y}=3X^2-1.
$$

Set both polynomials equal to zero. The second equation gives
$x^2=\frac13$, hence

$$
x=\pm\sqrt{\frac13}.
$$

In the first equation we can factor out the nonzero factor $6X$, so we
must have $x=y$. Thus

$$
y=\pm\sqrt{\frac13}.
$$

For $x=y$, the curve equation becomes

$$
x^3-x+\frac23\sqrt{\frac13}=0.
$$

At $x=\sqrt{\frac13}$, the left-hand side has value

$$
\frac13\sqrt{\frac13}-\sqrt{\frac13}
+\frac23\sqrt{\frac13}=0,
$$

so

$$
\left(\sqrt{\frac13},\sqrt{\frac13}\right)
$$

is a point on the curve. By contrast, at $x=y=-\sqrt{\frac13}$ we obtain

$$
-\frac13\sqrt{\frac13}+\sqrt{\frac13}
+\frac23\sqrt{\frac13}
=\frac43\sqrt{\frac13}\neq0,
$$

so this is not a point on the curve. The curve's only singularity is
therefore

$$
\left(\sqrt{\frac13},\sqrt{\frac13}\right).
$$

[Back to Exercise 22.12](#br-ak-2025-2026-w22-ex-12).

<!-- upstream_solution: Ebene algebraische Kurve/x^3+xy^2/C/Singularitäten/Aufgabe/Lösung; pageid=21319; revid=958122 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=958122 -->

## Solution to Exercise 22.14 {#br-ak-2025-2026-w22-sol-14}

Clearly,

$$
X(X+\mathrm iY)(X-\mathrm iY)
$$

is a factorisation of the polynomial into prime factors. To determine the
singular points, we examine the partial derivatives:

$$
\frac{\partial F}{\partial X}=3X^2+Y^2
\quad\text{and}\quad
\frac{\partial F}{\partial Y}=2XY.
$$

These both vanish precisely when $(x,y)=(0,0)$. Since this point also
satisfies the curve equation, it is the singular point of the curve. The
defining polynomial is already homogeneous of degree $3$, so the
multiplicity is $3$. The tangent lines are therefore given by

$$
V(X),\qquad V(X+\mathrm iY),\qquad V(X-\mathrm iY).
$$

[Back to Exercise 22.14](#br-ak-2025-2026-w22-ex-14).

<!-- upstream_solution: Ebene algebraische Kurve/y^4+x^3+3xy^2+2x^2y/C/Multiplizität und Tangenten/Aufgabe/Lösung; pageid=21569; revid=1089314 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1089314 -->

## Solution to Exercise 22.15 {#br-ak-2025-2026-w22-sol-15}

The multiplicity is the degree of the lowest-degree homogeneous component,
namely $3$. To determine the tangent lines, we must factor
$X^3+3XY^2+2X^2Y$ into linear factors. We have

$$
X^3+3XY^2+2X^2Y=X(X^2+3Y^2+2XY).
$$

Furthermore,

$$
\begin{aligned}
X^2+3Y^2+2XY
&=(X+Y)^2-Y^2+3Y^2 \\
&=(X+Y)^2+2Y^2 \\
&=(X+Y+\sqrt2\,\mathrm iY)(X+Y-\sqrt2\,\mathrm iY).
\end{aligned}
$$

The tangent lines are thus

$$
X=0
$$

(the $Y$-axis), and

$$
X=-(1+\sqrt2\,\mathrm i)Y
\quad\text{and}\quad
X=(-1+\sqrt2\,\mathrm i)Y.
$$

[Back to Exercise 22.15](#br-ak-2025-2026-w22-ex-15).

<!-- upstream_solution: Ebene Kurve/v^3+u^2v-2uv+2u^2-4u-2v/Bestimme Singularität/Aufgabe/Lösung; pageid=21307; revid=1089323 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1089323 -->

## Solution to Exercise 22.16 {#br-ak-2025-2026-w22-sol-16}

The following source computation uses the edition's hypotheses in Exercise
22.16, namely $\operatorname{char}(K)\notin\{2,3\}$ and $\sqrt3\in K$.

Let

$$
F=V^3+U^2V-2UV+2U^2-4U-2V.
$$

Then

$$
\frac{\partial F}{\partial U}=2UV-2V+4U-4
\quad\text{and}\quad
\frac{\partial F}{\partial V}=3V^2+U^2-2U-2.
$$

The first equation gives the following condition for a singular point:

$$
V(U-1)=-2U+2,
\qquad\text{or}\qquad
V=\frac{-2U+2}{U-1},
$$

where the latter form requires $U\neq1$. We therefore first consider the
case $U=1$. The first partial derivative is then zero regardless of $V$,
while the second gives the condition

$$
3V^2+1-2-2=0,
\qquad V^2=1,
\qquad V=\pm1.
$$

The curve equation gives

$$
V^3+V-2V-2V-2=V^3-3V-2=0,
$$

which is satisfied by $V=-1$. Therefore

$$
P=(1,-1)
$$

is a singular point of the curve.

In the new variables $X=U-1$ and $Y=V+1$, the point $P$ becomes the origin.
Substituting $U=X+1$ and $V=Y-1$ transforms the curve equation into

$$
\begin{aligned}
&(Y-1)^3+(X+1)^2(Y-1)-2(X+1)(Y-1) \\
&\qquad+2(X+1)^2-4(X+1)-2(Y-1) \\
&=Y^3-3Y^2+3Y-1+(X^2+2X+1)(Y-1) \\
&\qquad-2XY+2X-2Y+2+2X^2+4X+2-4X-4-2Y+2 \\
&=Y^3-3Y^2+3Y-1+X^2Y+2XY+Y-X^2-2X-1 \\
&\qquad-2XY+2X-2Y+2+2X^2+4X+2-4X-4-2Y+2 \\
&=Y^3+X^2Y-3Y^2+X^2.
\end{aligned}
$$

Thus the lowest-degree homogeneous component is

$$
X^2-3Y^2=(X-\sqrt3Y)(X+\sqrt3Y).
$$

The multiplicity is therefore two, and the two tangent lines through the
singular point are described by

$$
X=\pm\sqrt3Y.
$$

[Back to Exercise 22.16](#br-ak-2025-2026-w22-ex-16).

<!-- upstream_solution: Ebene Kurven/Lokale Diffeomorphie/Beispiel/1/Aufgabe/Lösung; pageid=95189; revid=1094625 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1094625 -->

## Solution to Exercise 22.18 {#br-ak-2025-2026-w22-sol-18}

The partial derivative of the first polynomial with respect to $X$ is

$$
5X^4-3X^2+2Y,
$$

whose value at the specified point is

$$
4\neq0.
$$

The partial derivative of the second polynomial with respect to $X$ is

$$
4X^3-6XY^2+5,
$$

whose value at the specified point is

$$
5\neq0.
$$

Both curves are therefore smooth at these points. By the implicit function
theorem, each is locally diffeomorphic to an open real interval, so they
are locally diffeomorphic to one another.

[Back to Exercise 22.18](#br-ak-2025-2026-w22-ex-18).

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are preserved
as stated in the metadata and the edition's rights files.
