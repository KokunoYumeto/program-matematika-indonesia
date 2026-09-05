---
title: "Lecture 6 - Polynomial and Rational Parametrisations"
stable_id: br-ak-2025-2026-l06
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 6"
upstream_pageid: 165895
upstream_revid: 1112253
upstream_timestamp: "2026-08-20T16:51:19Z"
upstream_mediawiki_sha1: 5b0f6515a3cd3c8079cef3862b8d182c6549dcf9
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_6?oldid=1112253"
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-06.csv"
translation_status: complete
---

# Lecture 6: Polynomial and Rational Parametrisations {#br-ak-2025-2026-l06}

## Polynomial parametrisations in the plane {#br-ak-2025-2026-l06-s01}

![A parametrised curve can be thought of as a trajectory of motion](authority/assets/Krivka_parametricky.png)

We now consider maps

$$
\varphi:\mathbb A_K^1\longrightarrow\mathbb A_K^2
$$

given by two polynomials in one variable

$$
P,Q\in K[T].
$$

The image of such a map lies in an affine algebraic curve, as the following theorem shows. We also speak of *parametrised curves*, or more precisely *polynomially parametrised curves*.

Here two ways of describing an algebraic curve compete. The points of a curve given by a curve equation are specified only implicitly. For each point of the plane, it is easy to check whether it lies on the curve, but in general it is difficult to find or explicitly specify points on the curve. A parametrised curve, by contrast, is given explicitly: for each point of the affine line, its image point can easily be calculated, giving the points of the curve explicitly. However, not every algebraic curve can be parametrised by polynomials.

### Theorem: an equation for a polynomially parametrised curve {#br-ak-2025-2026-l06-thm-01}

Let $K$ be a field and let $P,Q\in K[T]$ be polynomials. Then there is a polynomial

$$
F\in K[X,Y],\qquad F\ne0,
$$

such that

$$
F(P,Q)=0.
$$

In other words, the image of a polynomially parametrised curve lies in a plane algebraic curve

$$
C=V(F).
$$

If $K$ is infinite and $P,Q$ are not both constant, the Zariski closure of the image is an irreducible curve $C$.

#### Proof {#br-ak-2025-2026-l06-thm-01-proof}

*Edition note.* The source's degree argument below treats nonzero $P,Q$. If $P=0$, take $F=X$; if $Q=0$, take $F=Y$. Thus the zero-polynomial cases of the theorem are covered as well.

Let $d$ and $e$ be the degrees of $P$ and $Q$, respectively. Consider the monomials

$$
P^iQ^j.
$$

These are polynomials in $T$ of degree $di+ej$. For $i\le n$ and $j\le m$, there are $(n+1)(m+1)$ such monomials. They all lie in the $(dn+em+1)$-dimensional $K$-vector space spanned by

$$
1=T^0,T^1,T^2,\ldots,T^{dn+em}.
$$

If

$$
(n+1)(m+1)>dn+em+1,
$$

there must be a nontrivial linear dependence among the $P^iQ^j$. This gives a polynomial $F(X,Y)\ne0$ with $F(P,Q)=0$. The numerical condition above can be met by choosing $n,m$ sufficiently large.

From now on, let $K$ be infinite. By Lemma 3.10, the Zariski closure of the image

$$
B=\varphi(\mathbb A_K^1)
$$

is $V(\operatorname{Id}(B))$, and by Theorem 5.10 this set is irreducible. Since $K$ is infinite and the map is nonconstant, irreducibility also forces $V(\operatorname{Id}(B))$ to contain infinitely many points. By Lemma 4.3, $\operatorname{Id}(B)$ is a prime ideal; by the first part it contains an element

$$
F\in\operatorname{Id}(B),\qquad F\ne0.
$$

Since $K[X,Y]$ is a unique factorisation domain, a prime factor of $F$ also belongs to this ideal. We may therefore assume that $F$ is a prime polynomial. We have the inclusions

$$
B\subseteq\overline B
=V(\operatorname{Id}(B))
\subseteq V(F).
$$

For $H\in\operatorname{Id}(B)$, the set

$$
V(\operatorname{Id}(B))\subseteq V(H)\cap V(F)
$$

is infinite. By Theorem 4.8, $H$ and $F$ must have a common nonconstant factor. Since $F$ is prime, $H$ must be a multiple of $F$. Thus

$$
\operatorname{Id}(B)=(F).
$$

$\square$

### Example: eliminating the parameter {#br-ak-2025-2026-l06-ex-01}

Consider the curve given by the parametrisation

$$
x=t^2+t+1,
\qquad
y=2t^2+3t-1.
$$

We have

$$
x-1=t^2+t,
\qquad
y+1=2t^2+3t.
$$

A simple subtraction gives

$$
(y+1)-2(x-1)=3t-2t=t.
$$

Thus

$$
x-1=t^2+t=(y-2x+3)^2+(y-2x+3).
$$

Expanding gives the curve equation

$$
y^2+4x^2-4xy-15x+7y+13=0.
$$

### Example: a curve with one self-intersection {#br-ak-2025-2026-l06-ex-02}

![A cubic curve with a double point](authority/assets/Cubic_with_double_point.svg)

Consider the map $\mathbb A_K^1\to\mathbb A_K^2$ given by

$$
P=t^2-1,
\qquad
Q=t^3-t=t(t^2-1).
$$

*Edition note.* The source's two-branch description assumes $\operatorname{char}K\ne2$. In characteristic $2$, $1=-1$, so there is only one parameter value over $(0,0)$ and the self-intersection conclusion below does not apply; the displayed algebraic identities remain valid.

Both parameter values $t=\pm1$ give the point $(0,0)$. For every other value $t\ne\pm1$, we can write

$$
t=\frac{t^3-t}{t^2-1}=\frac{Q(t)}{P(t)}.
$$

Thus the parameter $t$ can be reconstructed from its image, which means that the map is injective away from those two values. The image curve therefore intersects itself at exactly one point.

To determine the curve equation, write $x=t^2-1$ and $y=t^3-t$. Then

$$
t^2=x+1
$$

and

$$
\begin{aligned}
y^2
&=t^2(t^2-1)^2\\
&=t^2x^2\\
&=(x+1)x^2\\
&=x^3+x^2.
\end{aligned}
$$

The polynomial describing the curve is therefore

$$
Y^2-X^3-X^2.
$$

## Rational parametrisations {#br-ak-2025-2026-l06-s02}

Consider a rational function

$$
Y=\frac{P}{Q},
\qquad
P,Q\in K[T].
$$

This immediately gives a new form of parametrisation through the map

$$
\begin{aligned}
\mathbb A_K^1\supseteq D(Q)&\longrightarrow\mathbb A_K^2,\\
t&\longmapsto\left(t,\frac{P(t)}{Q(t)}\right).
\end{aligned}
$$

Here $D(Q)$ is the domain of definition of the map, namely

$$
D(Q)=\mathbb A_K^1\setminus V(Q),
$$

consisting of all points where the denominator polynomial $Q$ is nonzero. This map clearly reaches every point of the graph of the rational function, so, like a polynomial parametrisation, it provides an explicit description of the curve. To describe curves, it is therefore natural to allow parametrisations whose component functions are rational as well.

### Definition: rational parametrisation {#br-ak-2025-2026-l06-def-01}

Two rational functions

$$
\varphi_1=\frac{P_1}{Q_1},
\qquad
\varphi_2=\frac{P_2}{Q_2},
$$

with

$$
P_1,P_2,Q_1,Q_2\in K[T],
\qquad
Q_1,Q_2\ne0,
$$

are called a *rational parametrisation* of the algebraic curve

$$
C=V(F),
\qquad
F\in K[X,Y]\text{ nonconstant},
$$

if

$$
F(\varphi_1(T),\varphi_2(T))=0
$$

and the pair $(\varphi_1,\varphi_2)$ is nonconstant.

The equality in this definition is understood in the rational function field $K(T)$. If $K$ is infinite, this is equivalent to the equality holding for every $t\in K$ where the denominators allow the functions to be defined.

### Definition: rational curve {#br-ak-2025-2026-l06-def-02}

A plane algebraic curve

$$
C=V(F)
$$

is called *rational* if it is irreducible and has a rational parametrisation.

The following simple example shows that rational functions can parametrise more curves than polynomials can. However, we should already mention that this difference disappears again in the context of projective geometry.

### Example: the hyperbola {#br-ak-2025-2026-l06-ex-03}

Consider the hyperbola

$$
H=V(XY-1).
$$

We claim that it has no polynomial parametrisation. For two polynomials $P(t)$ and $Q(t)$, the condition that their image always lie on $H$ is

$$
P(t)Q(t)=1
\quad\text{for every }t\in\mathbb A_K^1,
$$

or that $P(t)Q(t)=1$ in the polynomial ring $K[t]$. These conditions are equivalent over an infinite field; over a finite field, the second identity is the appropriate condition. This identity means that $P$ and $Q$ are inverses of one another, so both are units. The only units in a polynomial ring are the nonzero constants. Thus both polynomials are constant, the map they define is constant, and there is no polynomial parametrisation.

By contrast,

$$
\begin{aligned}
\mathbb A_K^1\setminus\{0\}&\longrightarrow\mathbb A_K^2,\\
t&\longmapsto\left(t,\frac1t\right)
\end{aligned}
$$

is a rational parametrisation of the hyperbola.

We want to show that the image of a nonconstant rational map always satisfies an algebraic equation, and thus always gives a rational parametrisation of an algebraic curve. In the polynomial case, an algebraic equation followed from a counting argument: the number of monomials in two variables grows faster with the degree than the number of monomials in one variable. We will use a similar argument together with an additional trick, *homogenisation*. This makes an inhomogeneous situation homogeneous by adding another variable (that is the price we have to pay). Here we use this process purely algebraically, but behind it lies the interplay between affine and projective geometry.

### Definition: homogenisation {#br-ak-2025-2026-l06-def-03}

Let

$$
F\in K[X_1,\ldots,X_n],
\qquad
F\ne0,
$$

be a polynomial with homogeneous decomposition

$$
F=\sum_{i=0}^dF_i,
$$

and let $Z$ be an additional variable. The homogeneous polynomial of degree $d$

$$
\widehat F
=\sum_{i=0}^dF_iZ^{d-i}
\in K[X_1,\ldots,X_n,Z]
$$

is called the *homogenisation* of $F$.

The original polynomial can be recovered from its homogenisation by setting the additional variable $Z=1$. This process is called *dehomogenisation*.

### Lemma: a homogeneous relation for three homogeneous polynomials {#br-ak-2025-2026-l06-lem-01}

Let

$$
P_1,P_2,P_3\in K[S,T]
$$

be three homogeneous polynomials of the same degree. Then there is a homogeneous polynomial

$$
F\in K[X,Y,Z],
\qquad
F\ne0,
$$

such that

$$
F(P_1,P_2,P_3)=0.
$$

#### Proof {#br-ak-2025-2026-l06-lem-01-proof}

This follows from a counting argument similar to the proof of Theorem 6.1; see Exercise 6.7. $\square$

### Example: a monomial relation {#br-ak-2025-2026-l06-ex-04}

Consider the map

$$
(S,T)\longmapsto(S^2,T^2,ST)=(X,Y,Z),
$$

given by homogeneous polynomials, indeed by monomials. An algebraic relation for its image is easy to find:

$$
Z^2=(ST)^2=S^2T^2=XY.
$$

Thus the image lies in $V(Z^2-XY)$. See also Exercise 6.29.

### Theorem: the image of a rational map satisfies an algebraic equation {#br-ak-2025-2026-l06-thm-02}

Suppose two rational functions

$$
\varphi_1=\frac{P_1}{Q_1},
\qquad
\varphi_2=\frac{P_2}{Q_2},
$$

with $P_1,P_2,Q_1,Q_2\in K[T]$, $Q_1,Q_2\ne0$, are given and are not both constant. Then there is a nonconstant polynomial $F\in K[X,Y]$ such that

$$
F(\varphi_1(T),\varphi_2(T))=0.
$$

Thus $\varphi_1$ and $\varphi_2$ define a rational parametrisation.

#### Proof {#br-ak-2025-2026-l06-thm-02-proof}

By passing to a common denominator, we may assume that the rational map is given by

$$
\varphi_1=\frac{P_1}{Q},
\qquad
\varphi_2=\frac{P_2}{Q},
$$

with $P_1,P_2,Q\in K[T]$ and $Q\ne0$. Let

$$
H'_1,H'_2,H'_3\in K[T,S]
$$

be the homogenisations of these three polynomials with the new variable $S$, and let $e$ be their largest degree. *Edition note:* if a numerator is zero, set its $H'_i$ and $H_i$ to zero and take $e$ over the nonzero polynomials; the degree formula below is applied only to nonzero $H'_i$. The zero polynomial is homogeneous of the required degree. Set

$$
H_i=S^{e-\deg(H'_i)}H'_i.
$$

The polynomials $H_1,H_2,H_3$ all have degree $e$, while their dehomogenisations at $S=1$ remain $P_1,P_2,Q$. By Lemma 6.8, there is a homogeneous polynomial

$$
F\in K[U,V,W],
\qquad
F\ne0,
$$

of degree $d$ in $U,V,W$, such that

$$
F(H_1,H_2,H_3)=0.
$$

Now consider

$$
\frac1{W^d}F(U,V,W)
=F\left(\frac UW,\frac VW,\frac WW\right),
$$

which is a polynomial in the two rational functions $U/W$ and $V/W$. The homogeneity of $F$ is crucial for this step. Substituting the three homogeneous polynomials gives

$$
0=F\left(\frac{H_1}{H_3},\frac{H_2}{H_3},1\right).
$$

This is an equality in the fraction field of $K[S,T]$. Setting $S=1$, that is, dehomogenising, and writing

$$
G(X,Y)=F(X,Y,1),
$$

we obtain a nonzero polynomial $G\in K[X,Y]$ such that

$$
0=G\left(\frac{P_1}{Q},\frac{P_2}{Q}\right),
$$

which is an equation for the two original rational functions. $\square$

![The cissoid of Diocles (black in the image) can be parametrised rationally](authority/assets/Dioklova_kisoida.png)

### Remark: local differentiable parametrisations {#br-ak-2025-2026-l06-rem-01}

We can go a step further and ask whether there are other ways to describe an algebraic curve

$$
C=V(F)
$$

by a map $\varphi:K\to K^2$, allowing $\varphi$ to belong to a larger class of functions. An important result here is the implicit function theorem. For $K=\mathbb R$ or $K=\mathbb C$, it says that if the two partial derivatives of $F$ do not both vanish at a point of the curve, then there is an infinitely differentiable, indeed analytic, map describing the curve in a small open neighbourhood of that point. An algebraic version of the implicit function theorem reappears in the power-series approach that we will discuss later.
