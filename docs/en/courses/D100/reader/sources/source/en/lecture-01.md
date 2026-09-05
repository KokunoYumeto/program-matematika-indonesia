---
title: "Lecture 1 — Plane Algebraic Curves"
stable_id: br-ak-2025-2026-l01
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 1"
upstream_pageid: 165889
upstream_revid: 1108084
upstream_timestamp: "2026-07-20T08:57:22Z"
upstream_mediawiki_sha1: sbohlbklicv2bb3w2dxf1d2h6qa1ogt
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_1?oldid=1108084"
license: "CC BY-SA 4.0 for translated course text; media retain component licences in authority/RIGHTS.csv"
translation_status: complete
---

# Lecture 1: Plane Algebraic Curves {#br-ak-2025-2026-l01}

## Plane algebraic curves {#br-ak-2025-2026-l01-s01}

What is an algebraic curve? For example, the objects shown in the following beautiful pictures.

![Graph of a linear function](authority/assets/Linear_function-250.png)

![Graph of a polynomial of degree four](authority/assets/Polynomialdeg4.png)

![Graph of a rational function](authority/assets/RationalDegree2byXedi.gif)

![Unit circle](authority/assets/Disk_1-250.png)

![Ellipse](authority/assets/Ellipse.svg)

![Curve with a cusp](authority/assets/Cusp-250.png)

![Example of an elliptic curve](authority/assets/Elliptic_curve_simple-250.png)

![Tschirnhausen cubic](authority/assets/Tschirnhausen_cubic-250.png)

![Kampyle of Eudoxus](authority/assets/Kampyle_Eudoxus-250.png)

![Conchoid of Pascal](authority/assets/Conchoid_of_Pascal.png)

![Bifolium](authority/assets/Bifolium.png)

![Limaçon](authority/assets/Limacon.png)

![Quadrifolium](authority/assets/Quadrifolium-250.png)

![Lemniscate of Bernoulli](authority/assets/Lemniscate_of_Bernoulli-250.png)

Of course, we can draw all sorts of things. The following curves are beautiful too, but they are not algebraic curves.

![Cycloid](authority/assets/Cicloide-250.png)

![Logarithmic spiral](authority/assets/Logarithmic_spiral-250.png)

![Sine graph](authority/assets/Sin-250.png)

![Quadratic Koch curve](authority/assets/Quadratic_Koch.png)

The word “algebraic” in *algebraic curve* comes from the requirement that only algebraic operations may be used in its definition: addition and multiplication, but not analytic processes such as taking limits, infinite sums, approximation, differentiation or integration. The maps allowed in our context are given by polynomials in several variables. The pictures above show plane algebraic curves defined by a polynomial in two variables. The first two pictures are *graphs* of a polynomial function in one variable; they are described by

$$
Y=P(X).
$$

In the first picture, $P(X)=X$ (so the polynomial is linear), whereas in the second the polynomial has a form such as

$$
P(X)=a_4X^4+a_3X^3+a_2X^2+a_1X+a_0,
$$

with coefficients $a_i$ in a field $K$. In algebraic geometry we fix a *base field* $K$. Important fields for us are the real numbers (the pictures are primarily to be understood in this sense) and the complex numbers $\mathbb C$. Such a graph is a simple object in that each value of $X$ has exactly one corresponding value of $Y$, namely the function value, which is also easy to calculate if we can calculate in the given field. In a certain sense, the graph is a “curved” copy of the base line, the $X$-axis.

Now consider the third picture. It is the graph of a *rational function*: we take two polynomials $P,Q$ in the variable $X$ and consider their quotient $P(X)/Q(X)$. This expression makes sense only where the denominator is nonzero. The rational function is undefined at the zeros of the denominator polynomial. If numerator and denominator vanish at the same point, cancellation sometimes gives the quotient a meaning there as well. If the denominator vanishes but the numerator does not, the undefined point is a *pole*: the real graph tends to $+\infty$ or $-\infty$. It is tempting to say that the rational function takes the value “infinity” at these points; in projective geometry this idea really does make sense, as we shall see later.

Because of these undefined points, however, the “graph equation” $Y=P(X)/Q(X)$ is not an ideal description of the curve. Multiplying by the denominator instead gives the condition, or *equation*,

$$
YQ(X)=P(X),
\qquad\text{or, more precisely,}\qquad
\{(x,y)\in K^2\mid yQ(x)=P(x)\},
$$

whose two sides are well-defined polynomials. The *set satisfying the equation* (or *solution set*) is uniquely defined. For an $x$ with $Q(x)=0$, the left-hand side is zero. If $P(x)\ne0$, there is no solution at this $x$, as in the picture; if $P(x)=0$, every value of $Y$ is allowed. In the latter case, the object therefore contains the line through $(x,0)$ perpendicular to the $X$-axis.

### Example: the hyperbola {#br-ak-2025-2026-l01-ex-01}

A typical and important example of a rational function is $Y=1/X$. Its graph is called a *hyperbola* $H$. Written without a denominator, the equation becomes

$$
XY=1,
\qquad\text{or}\qquad
H=\{(x,y)\mid xy=1\}.
$$

On $K^\times=K\setminus\{0\}$ this rational function is an ordinary function, with graph $H$, and it gives a “natural” bijection

$$
K^\times\longrightarrow H,
\qquad x\longmapsto\left(x,\frac1x\right).
$$

Thus $K^\times$ and $H$ are “equivalent” or “isomorphic” in a sense that will be made precise later.

Both descriptions have advantages. The description as $K^\times\subset K$ takes place on a line (if we think of $K=\mathbb R$), but the point $0$, which is a *limit point* of $K^\times$, does not belong to $K^\times$. In other words, $K^\times$ is not *closed*. The hyperbola, by contrast, is closed in $\mathbb R^2$; realising the object as a closed set therefore requires moving to a higher dimension. The question of what constitutes a good description of an algebraic-geometric object will recur throughout the course.

![Rectangular hyperbola](authority/assets/Rectangular_hyperbola-250.png)

In the real case, $K=\mathbb R$, the set $\mathbb R^\times$ (and likewise $H_{\mathbb R}$) consists of two disjoint “branches”, so it is not *connected*. In the complex case, $K=\mathbb C$, the set $\mathbb C^\times$ (and likewise $H_{\mathbb C}$) is a punctured real plane and is therefore connected. This is a typical phenomenon in algebraic geometry: important properties may depend on the base field. Nevertheless, properties that depend only on the defining equations and hold for their solution sets over every field have particular significance.

The fourth picture shows a *circle*, with equation

$$
K=\{(x,y)\mid x^2+y^2=r^2\},
$$

where $r$ denotes its radius. The picture already shows that this object cannot be the graph of a function, since on a graph each $x$-value is paired with exactly one $y$-value. There is no function $y=\varphi(x)$ satisfying

$$
K=\{(x,\varphi(x))\mid x\in\mathbb R\}.
$$

The question of whether an algebraic solution set can be realised as a graph is equivalent to asking whether its defining equation can be “solved” for $y$. In this example we can write

$$
y^2=r^2-x^2,
\qquad
y=\sqrt{r^2-x^2}=\sqrt{(r-x)(r+x)}.
$$

Is the circle a graph after all? There are two interpretations.

1. If we restrict ourselves to real numbers and positive square roots, the last step is not an equivalent transformation: we have “added” information that was not in the original equation. Taking the positive square root means restricting to the upper semicircle. Adding information or conditions makes the solution set smaller.

2. If instead $\sqrt{\phantom{x}}$ is understood to include all solutions—in the real case, both the positive and the negative square root, often written $\pm\sqrt{\phantom{x}}$—we have added no information, but we have not solved for a function either; we have only obtained what is sometimes called a “multivalued function”.

Both viewpoints are useful. The attempt to describe part of a geometric object, such as the upper arc, simply as a graph reappears in the implicit function theorem, power-series methods, parametrisations and local theory.

## Equations of the form $Y^2=G(X)$ {#br-ak-2025-2026-l01-s02}

![Cubic curves studied by Newton](authority/assets/Newtonbig.gif)

![Isaac Newton (1643–1727)](authority/assets/GodfreyKneller-IsaacNewton-1689.jpg)

A circle equation can be viewed as an equation of the form

$$
Y^2=G(X),
$$

where $G$ is a polynomial in the single variable $X$; for the circle, $G=-X^2+1$. This is not a graph, but the “square root” of a graph. More generally, allow $G(X)$ to be more complicated. The zero set (or *zero locus*) represents the square root $\sqrt{G(X)}$. For any chosen value $x$ of $X$, there are three possibilities for the corresponding real solutions $y$.

1. If $G(x)<0$, there is no solution.
2. If $G(x)=0$, there is exactly one solution, $y=0$.
3. If $G(x)>0$, there are two solutions, $y=\pm\sqrt{G(x)}$.

This also suggests how to visualise the real picture: for each $x$, calculate $G(x)$ and, if the radicand is nonnegative, mark the points $(x,\pm\sqrt{G(x)})$.

Over the complex numbers, we need distinguish only $G(x)=0$ from $G(x)\ne0$. If $G$ has degree two, the resulting curve is a *conic section*, a subject studied since antiquity (see Lecture 7).

Isaac Newton studied intensively the case in which $G(X)$ is a real cubic polynomial, that is, a polynomial of degree three. Even this collection of examples is already very rich.

![Examples of real elliptic curves](authority/assets/ECexamples01-330.png)

Consider the case $G(X)=X^3$, the object described by

$$
\{(x,y)\mid y^2=x^3\}.
$$

This object is called *Neil's parabola*. A new phenomenon appears here: the origin is different from all the other points. We call it a *singularity*; the other points, by contrast, are called *smooth* or *nonsingular*. Giving a precise definition is part of this course. As a first, imprecise formulation, a curve near a smooth point looks, in suitable coordinates, like the possibly rotated graph of a differentiable function. The singularity of Neil's parabola is called a *cusp*—the source uses the German words *Spitze* and *Kuspe*, both meaning a pointed tip. By contrast, the singularity in the eighth picture is a *crossing point* or *double point*.

In the seventh picture at the beginning, and in the picture above, we also see zero loci of the form $Y^2=G(X)$ with $G(X)$ of degree three. What must $G(X)$ look like to produce such a curve? The last examples also show that the presence of a singularity depends on the precise form of $G(X)$.

Let us stay with Neil's parabola $C$. If $t$ is any real or complex number, the point with coordinates

$$
(x,y)=(t^2,t^3)
$$

always lies on Neil's parabola, since $(t^2)^3=t^6=(t^3)^2$. Conversely, one can show (see [Exercise 1.6](https://de.wikiversity.org/wiki/Neilsche_Parabel/Bildbeschreibung_durch_Gleichung/Aufgabe)) that every point of Neil's parabola has this form: for each $(x,y)$ satisfying $y^2=x^3$, there is exactly one $t$ with $(x,y)=(t^2,t^3)$. The map

$$
\mathbb R\longrightarrow C,
\qquad t\longmapsto(t^2,t^3),
$$

is called a (bijective polynomial) *parametrisation* of Neil's parabola. Determining which algebraic curves admit a polynomial parametrisation is a nontrivial question. A smooth curve of the form $Y^2=G(X)$ with $\deg G=3$ has no such parametrisation. In elementary number theory, we learn that all *Pythagorean triples* can be written in a simple uniform form; see [Theorem 10.6 (Number Theory, Osnabrück 2025)](https://de.wikiversity.org/wiki/Pythagoreische_Tripel/Parametrische_Charakterisierung/Fakt). An equivalent statement is the existence of a rational parametrisation of the rational unit circle; see [Theorem 10.4](https://de.wikiversity.org/wiki/Einheitskreis/Rationale_Parametrisierung/Fakt). We shall discuss this in greater generality in [Theorem 7.6](https://de.wikiversity.org/wiki/Quadrik_in_zwei_Variablen/Rationale_Parametrisierung/Fakt).

We now come to the first general definition.

### Definition: affine plane algebraic curve {#br-ak-2025-2026-l01-def-01}

Let $K$ be a field. An *affine plane algebraic curve* over $K$ is the zero locus $V(F)\subseteq K^2$ of a nonconstant polynomial $F$ in two variables, that is,

$$
F=\sum_{0\le i,j\le m}a_{ij}X^iY^j
\qquad (a_{ij}\in K).
$$

In other words,

$$
V(F)=\left\{(x,y)\in K^2\;\middle|\;
F(x,y)=\sum_{0\le i,j\le m}a_{ij}x^iy^j=0\right\}.
$$

The following favourite polynomials in the variables $X$ and $Y$ were suggested in class:

1. $X^2-Y^2$;
2. $2X+4Y+3$;
3. $X^2+Y^2-3$;
4. $X^2+Y^2$;
5. $5X^2+12Y^2-26$;
6. $3X^2-15Y^2-3$;
7. $X^3+Y^3+XY$;
8. $X^3-4Y^2-XY$;
9. $X^4$;
10. $X^2Y^2-X^2$.

The corresponding zero loci $V(F)$ vary in how difficult they are to understand. By the difference-of-squares identity,

$$
X^2-Y^2=(X+Y)(X-Y),
$$

and a product of two field elements is zero exactly when one factor is zero. This zero locus is therefore simply the union of the two diagonals: a union of two affine lines. The zero locus of $2X+4Y+3$ is the solution set of this linear equation, an affine line. The real zero locus of $X^2+Y^2-3$ is a circle centred at the origin with radius $\sqrt3$. By contrast, the real zero locus of $X^2+Y^2$ consists only of the origin $(0,0)$; over $\mathbb C$ the situation is different. The zero locus of $5X^2+12Y^2-26$ is an ellipse with axes parallel to the coordinate axes, whereas the zero locus of $3X^2-15Y^2-3$ is a compressed hyperbola.

We shall discuss and classify the zero loci of quadratic polynomials in detail in Lecture 7. The two polynomials $X^3+Y^3+XY$ and $X^3-4Y^2-XY$ have degree $3$ and are much harder to understand. The first question is whether their curves are smooth or have singularities. The zero locus $V(X^4)$ equals $V(X)$ and is therefore the $y$-axis. The last polynomial factors as

$$
X^2Y^2-X^2=X^2(Y^2-1)=X^2(Y-1)(Y+1),
$$

so it is easy to understand. Its zero locus is the union of three lines: the $y$-axis and two lines parallel to the $x$-axis.

We shall prove a lemma that immediately shows why the four nonalgebraic curves pictured above are not algebraic.

### Lemma: intersection with a line {#br-ak-2025-2026-l01-lem-01}

Let $C$ be an affine plane algebraic curve and $L$ a line in $K^2$.

**Then $C\cap L$ is either the whole line $L$ or a finite set of points.**

#### Proof {#br-ak-2025-2026-l01-lem-01-proof}

By definition, a plane algebraic curve $C=V(F)$ is always the zero locus of a polynomial $F$ in two variables. Suppose the line $L$ is given by

$$
aX+bY+c=0.
$$

Without loss of generality, assume $a\ne0$. Solving for $X$ gives $X=\alpha Y+\beta$. An intersection point $P\in C\cap L$ must satisfy both $F(P)=0$ and the line equation. Using the line equation, replace $X$ in $F$ by $\alpha Y+\beta$. This turns $F$ into a polynomial in the single variable $Y$, which we call $\widetilde F$.

Now $P\in C\cap L$ is equivalent to $P\in L$ and $\widetilde F(P)=0$. Thus the intersection is described by $\widetilde F$. If $\widetilde F=0$, the whole line is the intersection. If $\widetilde F\ne0$, [Corollary 19.9 (Linear Algebra, Osnabrück 2024–2025)](https://de.wikiversity.org/wiki/Polynomring_(K%C3%B6rper)/Nullstellen/Anzahl/Fakt) says that it has only finitely many zeros. $\square$

For the four nonalgebraic examples above, there are lines meeting the curves in infinitely many points. The curves are therefore not algebraic.

## Polynomial rings {#br-ak-2025-2026-l01-s03}

After these introductory examples, we fix some terminology that is probably already familiar.

### Definition: polynomial ring in one variable {#br-ak-2025-2026-l01-def-02}

The *polynomial ring* over a commutative ring $R$ consists of all *polynomials*

$$
P=a_0+a_1X+a_2X^2+\cdots+a_nX^n,
$$

with $a_i\in R$ for $i=0,\ldots,n$ and $n\in\mathbb N$, equipped with componentwise addition and multiplication defined by extending the following rule distributively:

$$
X^n\cdot X^m:=X^{n+m}.
$$
From this definition we can also define polynomial rings in several variables. Set

$$
K[X,Y]:=(K[X])[Y],
\qquad
K[X,Y,Z]:=(K[X,Y])[Z],
$$

and so on. A polynomial in $n$ variables has the form

$$
F=\sum_{(\nu_1,\ldots,\nu_n)}
a_{(\nu_1,\ldots,\nu_n)}X_1^{\nu_1}\cdots X_n^{\nu_n}.
$$

The sum runs over a finite family of *exponent tuples* $(\nu_1,\ldots,\nu_n)$. Expressions of the form $X_1^{\nu_1}\cdots X_n^{\nu_n}$ are also called *monomials*. A polynomial is usually abbreviated as $F=\sum_\nu a_\nu X^\nu$. Multiplying two monomials means adding their exponent tuples:

$$
\left(X_1^{\nu_1}\cdots X_n^{\nu_n}\right)
\left(X_1^{\mu_1}\cdots X_n^{\mu_n}\right)
:=X_1^{\nu_1+\mu_1}\cdots X_n^{\nu_n+\mu_n}.
$$

In algebraic geometry, the case of greatest interest to us is when the base ring $R$ is a field. Algebraic geometry studies the shape of zero loci of polynomials in several variables. We shall see later that the relationship between algebraic and geometric properties is particularly strong when the base field is algebraically closed.

### Definition: algebraically closed field {#br-ak-2025-2026-l01-def-03}

A field $K$ is called *algebraically closed* if every nonconstant polynomial $F\in K[X]$ has a zero in $K$.

![Carl Friedrich Gauss (1777–1855)](authority/assets/Carl_Friedrich_Gauss.jpg)

The *fundamental theorem of algebra* was first proved by Gauss.

### Theorem: fundamental theorem of algebra {#br-ak-2025-2026-l01-thm-01}

The field of complex numbers $\mathbb C$ is **algebraically closed**.

#### Proof {#br-ak-2025-2026-l01-thm-01-proof}

We shall not prove this theorem here. Its proofs use topological or analytic methods. $\square$

---

**Source navigation:** [course](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)) · [Lecture 2](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_2) · [worksheet for this lecture](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Arbeitsblatt_1)
