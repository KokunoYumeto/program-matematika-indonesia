---
title: "Public Solutions to Worksheet 6"
stable_id: br-ak-2025-2026-w06-solutions
language: en
upstream_map: authority/wikiversity/unit-06/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 24ad08b1cbd215a1142d66d4297a5ce177b610aaaadd4329d464b1febb8c4c2c
public_solution_count: 9
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 6 {#br-ak-2025-2026-w06-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 6.3, 6.4, 6.8, 6.9, 6.17, 6.18, 6.21, 6.22, and 6.25. No additional solutions have been created for this edition.

## Solution to Exercise 6.3 {#br-ak-2025-2026-w06-sol-03}

<!-- upstream_solution_revid: 1112350 -->

We calculate the first few monomials in $X$ and $Y$:

$$
X^0Y^0=1,
$$

$$
X=t^2+t,
$$

$$
Y=t^3,
$$

$$
XY=t^5+t^4,
$$

$$
X^2=t^4+2t^3+t^2,
$$

$$
Y^2=t^6,
$$

and

$$
X^3=t^6+3t^5+3t^4+t^3.
$$

We seek a nontrivial relation among these polynomials in $K[t]$. Since

$$
X^3-Y^2-Y=3t^5+3t^4=3XY,
$$

an algebraic relation for the image curve is

$$
X^3-Y^2-Y-3XY=0.
$$

For example, the point $(1,0)$ in the affine plane does not lie on the image curve, since

$$
1^3-0^2-0-3\cdot1\cdot0=1\ne0.
$$

[Back to Exercise 6.3](#br-ak-2025-2026-w06-ex-03).

## Solution to Exercise 6.4 {#br-ak-2025-2026-w06-sol-04}

<!-- upstream_solution_revid: 958133 -->

We calculate some monomials in $X$ and $Y$:

$$
X^0Y^0=1,
$$

$$
X=t^2+1,
$$

$$
X^2=t^4+2t^2+1,
$$

$$
X^3=t^6+3t^4+3t^2+1,
$$

and

$$
Y^2=t^6-2t^4+t^2.
$$

These are five polynomials containing only the powers $t^0,t^2,t^4,t^6$, so they must be linearly dependent. One linear relation is

$$
-Y^2+X^3-5X^2+8X-4=0.
$$

[Back to Exercise 6.4](#br-ak-2025-2026-w06-ex-04).

## Solution to Exercise 6.8 {#br-ak-2025-2026-w06-sol-08}

<!-- upstream_solution_revid: 1057120 -->

No such polynomial exists. Suppose

$$
F=\sum_{\alpha+\beta+\gamma=d}
a_{(\alpha,\beta,\gamma)}X^\alpha Y^\beta Z^\gamma
$$

is a homogeneous polynomial of degree $d$. The required equation would be

$$
F(S,T,ST)
=\sum_{\alpha+\beta+\gamma=d}
a_{(\alpha,\beta,\gamma)}
S^{\alpha+\gamma}T^{\beta+\gamma}
=0.
$$

Suppose two monomials in this sum are equal:

$$
S^{\alpha_1+\gamma_1}T^{\beta_1+\gamma_1}
=S^{\alpha_2+\gamma_2}T^{\beta_2+\gamma_2}.
$$

Then

$$
\alpha_1+\gamma_1=\alpha_2+\gamma_2
$$

and

$$
\beta_1+\gamma_1=\beta_2+\gamma_2.
$$

Adding the equations gives

$$
\alpha_1+\beta_1+2\gamma_1
=\alpha_2+\beta_2+2\gamma_2.
$$

Since

$$
\alpha_1+\beta_1+\gamma_1
=\alpha_2+\beta_2+\gamma_2=d,
$$

we obtain $\gamma_1=\gamma_2$, and then $\alpha_1=\alpha_2$ and $\beta_1=\beta_2$. Thus all the monomials $S^{\alpha+\gamma}T^{\beta+\gamma}$ in the sum above are pairwise distinct. For $F(S,T,ST)=0$, every coefficient $a_{(\alpha,\beta,\gamma)}$ must be zero. Hence $F=0$, contrary to the requirement of the exercise.

[Back to Exercise 6.8](#br-ak-2025-2026-w06-ex-08).

## Solution to Exercise 6.9 {#br-ak-2025-2026-w06-sol-09}

<!-- upstream_solution_revid: 1112838 -->

We use the homogenisations of equal degree

$$
H_1=T^2+S^2,
\qquad
H_2=S(T+S)=ST+S^2,
\qquad
H_3=ST.
$$

These give six monomials of degree $4$ in $S,T$. Since there are only five monomials of degree $4$ in two variables, a linear dependence must exist. Explicitly,

$$
F_1=H_1^2=T^4+2S^2T^2+S^4,
$$

$$
F_2=H_2^2=S^2T^2+2S^3T+S^4,
$$

$$
F_3=H_3^2=S^2T^2,
$$

$$
F_4=H_1H_2=ST^3+S^2T^2+S^3T+S^4,
$$

$$
F_5=H_1H_3=ST^3+S^3T,
$$

and

$$
F_6=H_2H_3=S^2T^2+S^3T.
$$

Since $T^4$ occurs only in $F_1$, we can seek a linear relation among $F_2,F_3,F_4,F_5,F_6$. Since $F_3$ is a monomial, we focus on the relevant monomials $ST^3,S^3T,S^4$ and on $F_2,F_4,F_5,F_6$. We have

$$
F_2-F_4+F_5-2F_6=-2S^2T^2.
$$

Thus

$$
F_2+2F_3-F_4+F_5-2F_6=0.
$$

Consequently,

$$
F(U,V,W)=V^2+2W^2-UV+UW-2VW
$$

is a homogeneous polynomial of degree $2$ that vanishes when $U,V,W$ are replaced by $H_1,H_2,H_3$, respectively. The corresponding equation, obtained by dividing $F(U,V,W)=0$ by $W^2$, is

$$
\left(\frac VW\right)^2+2
-\frac UW\frac VW+\frac UW-2\frac VW=0.
$$

After substituting $H_1,H_2,H_3$ and then setting $S=1$, the ratios $U/W$ and $V/W$ become the original rational functions. An annihilating polynomial is therefore

$$
Y^2-XY+X-2Y+2.
$$

As a direct check,

$$
\begin{aligned}
&\left(\frac{t+1}{t}\right)^2
-\frac{t^2+1}{t}\frac{t+1}{t}
+\frac{t^2+1}{t}
-2\frac{t+1}{t}+2\\
&=\frac{t^2+2t+1-(t^3+t^2+t+1)
+t^3+t-2t^2-2t+2t^2}{t^2}\\
&=0.
\end{aligned}
$$

[Back to Exercise 6.9](#br-ak-2025-2026-w06-ex-09).

## Solution to Exercise 6.17 {#br-ak-2025-2026-w06-sol-17}

<!-- upstream_solution_revid: 1096769 -->

1. From

   $$
   (x,y,z,w)
   =\bigl(p^2,p(1-p),(1-p)p,(1-p)^2\bigr)
   =\bigl(p^2,p-p^2,p-p^2,p^2-2p+1\bigr),
   $$

   we immediately obtain

   $$
   p=p^2+(p-p^2)=x+y.
   $$

   Thus the input variable can be reconstructed from the component polynomials, proving injectivity.

2. Clearly $y=z$, which gives a first equation and allows $z$ to be eliminated. Using

   $$
   u=p=x+y,
   $$

   we obtain

   $$
   y=u-u^2
   $$

   and

   $$
   w=u^2-2u+1.
   $$

   Thus $y$ and $w$ can also be eliminated, and the image is described completely by the three equations

   $$
   y-z=0,
   $$

   $$
   y-(x+y)+(x+y)^2=0,
   $$

   and

   $$
   w-(x+y)^2+2(x+y)-1=0.
   $$

[Back to Exercise 6.17](#br-ak-2025-2026-w06-ex-17).

## Solution to Exercise 6.18 {#br-ak-2025-2026-w06-sol-18}

<!-- upstream_solution_revid: 1024155 -->

1. From

   $$
   (x,y,z,w)
   =\bigl(pq,p(1-q),(1-p)q,(1-p)(1-q)\bigr)
   =\bigl(pq,p-pq,q-pq,pq-p-q+1\bigr),
   $$

   we immediately obtain

   $$
   p=pq+(p-pq)=x+y
   $$

   and

   $$
   q=pq+(q-pq)=x+z.
   $$

   Thus both input variables can be reconstructed, proving injectivity.

2. Using

   $$
   u=p=x+y,
   \qquad
   v=q=x+z,
   $$

   we obtain

   $$
   x=uv
   $$

   and

   $$
   w=uv-u-v+1.
   $$

   Thus $x$ and $w$ can be eliminated, and the image is described completely by the two equations

   $$
   x-(x+y)(x+z)=0
   $$

   and

   $$
   w-(x+y)(x+z)+(x+y)+(x+z)-1=0.
   $$

[Back to Exercise 6.18](#br-ak-2025-2026-w06-ex-18).

## Solution to Exercise 6.21 {#br-ak-2025-2026-w06-sol-21}

<!-- upstream_solution_revid: 1067921 -->

Let $d$ be the common degree of $G$ and $H$, and write

$$
G=\sum_{\nu\in\mathbb N^n}
a_\nu X^\nu Z^{d-|\nu|}
$$

and

$$
H=\sum_{\nu\in\mathbb N^n}
b_\nu X^\nu Z^{d-|\nu|}.
$$

Their dehomogenisations are

$$
\sum_{\nu\in\mathbb N^n}a_\nu X^\nu
\qquad\text{and}\qquad
\sum_{\nu\in\mathbb N^n}b_\nu X^\nu,
$$

which are equal by assumption. Hence $a_\nu=b_\nu$ for every $\nu$, and therefore the original polynomials are also equal.

[Back to Exercise 6.21](#br-ak-2025-2026-w06-ex-21).

## Solution to Exercise 6.22 {#br-ak-2025-2026-w06-sol-22}

<!-- upstream_solution_revid: 1096509 -->

Let

$$
F=F_d+F_{d-1}+\cdots+F_1+F_0
$$

and

$$
G=G_e+G_{e-1}+\cdots+G_1+G_0
$$

be polynomials of degrees $d$ and $e$, written in their homogeneous decompositions. Their homogenisations are

$$
\widehat F
=F_d+F_{d-1}Z+\cdots+F_1Z^{d-1}+F_0Z^d
$$

and

$$
\widehat G
=G_e+G_{e-1}Z+\cdots+G_1Z^{e-1}+G_0Z^e.
$$

Their product has the form

$$
\widehat F\,\widehat G
=\sum_{k=0}^{d+e}P_kZ^{d+e-k},
$$

where

$$
P_k=\sum_{i=0}^dF_iG_{k-i},
$$

with components whose indices lie outside the range understood to be zero. On the other hand,

$$
FG=\sum_{k=0}^{d+e}H_k
$$

has homogeneous components

$$
H_k=\sum_{i=0}^dF_iG_{k-i}.
$$

Therefore,

$$
\begin{aligned}
\widehat{FG}
&=\sum_{k=0}^{d+e}H_kZ^{d+e-k}\\
&=\sum_{k=0}^{d+e}
\left(\sum_{i=0}^dF_iG_{k-i}\right)Z^{d+e-k}\\
&=\sum_{k=0}^{d+e}P_kZ^{d+e-k}\\
&=\widehat F\,\widehat G.
\end{aligned}
$$

[Back to Exercise 6.22](#br-ak-2025-2026-w06-ex-22).

## Solution to Exercise 6.25 {#br-ak-2025-2026-w06-sol-25}

<!-- upstream_solution_revid: 1089645 -->

Division with remainder in the homogeneous case gives

$$
\begin{aligned}
&X^4+9X^3Y+7X^2Y^2+XY^3+8Y^4\\
&\quad=(X^3+5X^2Y)(X+4Y)
-13X^2Y^2+XY^3+8Y^4.
\end{aligned}
$$

Thus

$$
Q=X+4Y
$$

and

$$
R=-13X^2Y^2+XY^3+8Y^4.
$$

[Back to Exercise 6.25](#br-ak-2025-2026-w06-ex-25).
