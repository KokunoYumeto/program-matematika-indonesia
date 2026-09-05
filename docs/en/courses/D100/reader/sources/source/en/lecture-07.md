---
title: "Lecture 7 - Conic Sections and Quadrics"
stable_id: br-ak-2025-2026-l07
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 7"
upstream_pageid: 165896
upstream_revid: 1057689
upstream_timestamp: "2025-11-04T10:20:33Z"
upstream_mediawiki_sha1: 482eacab21b84870389c23a5faac8493768fd522
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_7?oldid=1057689"
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-07.csv"
translation_status: complete
---

# Lecture 7: Conic Sections and Quadrics {#br-ak-2025-2026-l07}

## Conic sections and quadrics {#br-ak-2025-2026-l07-s01}

![The standard cone](authority/assets/DoubleCone.png)

The *standard cone* in three-dimensional affine space is given by the homogeneous equation

$$
Z^2=X^2+Y^2.
$$

One can picture this by thinking of $z$ as specifying the radius of a circle (*edition clarification:* over $\mathbb R$, the radius is $\lvert z\rvert$, not a negative $z$) in the plane parallel to the $x$-$y$ plane through the point $(0,0,z)$. Every intersection of this cone with an affine plane $E$ is called a *conic section*.

![Sections of the standard cone by affine planes](authority/assets/Conic_sections.svg)

### [Definition: conic section](https://de.wikiversity.org/wiki/Algebraische_Kurven/Kegelschnitt_mit_Standardkegel/Definition) {#br-ak-2025-2026-l07-def-01}

A *conic section* $C$ is the intersection of the standard cone $V(Z^2-X^2-Y^2)$ with an affine plane $V(aX+bY+cZ+d)$, where $a,b,c$ are not all zero; thus

$$
C=V(Z^2-X^2-Y^2)\cap V(aX+bY+cZ+d).
$$

The theory of conic sections is a classical subject, on which [Apollonius of Perga](https://de.wikipedia.org/wiki/Apollonios_von_Perge) already wrote a treatise. Since the plane is given by an equation

$$
aX+bY+cZ+d=0,
$$

we can solve linearly for one variable and obtain a new equation in two variables for the conic section. This is an affine-linear substitution of variables, so the new equation also has degree two.

We therefore consider *affine quadrics* in two variables in general.

### [Definition: a quadric in two variables](https://de.wikiversity.org/wiki/Ebene_algebraische_Kurven/Quadrik_in_zwei_Variablen/Polynom_und_Nullstelle/Definition) {#br-ak-2025-2026-l07-def-02}

A polynomial of the form

$$
F=\alpha X^2+\beta XY+\gamma Y^2+\delta X+\epsilon Y+\eta,
\qquad
\alpha,\beta,\gamma,\delta,\epsilon,\eta\in K,
$$

where at least one of the coefficients $\alpha,\beta,\gamma$ is nonzero, is called a *quadratic form in two variables* (over $K$), or a *quadric in two variables*. The corresponding zero locus

$$
V(F)\subseteq\mathbb A_K^2
$$

is also called a *quadric*.

*Terminology note.* Here the source uses “quadratic form” for a possibly inhomogeneous degree-two polynomial. In the usual homogeneous sense, the quadratic form is only $\alpha X^2+\beta XY+\gamma Y^2$.

We want to know how many different types of quadrics there are. The answer depends on the ground field. We must also specify which notion of equivalence we wish to use. For two quadrics

$$
F,G\in K[X,Y],
$$

the following notions of equivalence are worth investigating.

1. $F$ and $G$ are *affinely equivalent* as polynomials: there is a (bijective) affine-linear change of variables

   $$
   \begin{aligned}
   \varphi:K[X,Y]&\longrightarrow K[X,Y],\\
   X&\longmapsto rX+sY+t,\\
   Y&\longmapsto \widetilde rX+\widetilde sY+\widetilde t,
   \end{aligned}
   $$

   such that $G=\varphi(F)$.

2. The principal ideals $(F)$ and $(G)$ are *affinely equivalent*: there is a (bijective) affine-linear change of variables $\varphi$ such that

   $$
   (G)=(\varphi(F)).
   $$

3. The quotient rings

   $$
   K[X,Y]/(F)\qquad\text{and}\qquad K[X,Y]/(G)
   $$

   are isomorphic as [$K$-algebras](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Algebra/Ringhomomorphismus/Definition).

4. The zero loci $V(F)$ and $V(G)$ are [affine-linearly equivalent](https://de.wikiversity.org/wiki/Affin-algebraische_Mengen/Affin-linear_%C3%A4quivalent/Definition).

The first notion is stronger than the second, and the second is stronger than the last two. An essential difference between (1) and (2) is that in (2) we may always multiply by a unit (which does not change the zero locus either). Over a field that is not algebraically closed, equivalence in (4) can be very coarse, since all $F$ with an empty zero locus are equivalent in the sense of (4).

For $K=\mathbb R$ and $K=\mathbb C$, we are also interested in whether the corresponding zero loci have the same topological properties. Here we will consider the different notions of equivalence for two quadrics $F$ and $G$ in parallel, but our main interest is in (2).

### [Lemma: first reduction of affine quadrics](https://de.wikiversity.org/wiki/Affine_Quadriken_in_zwei_Variablen/Erste_Reduktion/Fakt) {#br-ak-2025-2026-l07-lem-01}

Let $K$ be a [field](https://de.wikiversity.org/wiki/K%C3%B6rpertheorie_%28Algebra%29/K%C3%B6rper/Direkt/Definition) of [characteristic](https://de.wikiversity.org/wiki/K%C3%B6rpertheorie_%28Algebra%29/Charakteristik/1/Definition) $\ne2$, and let

$$
F=\alpha X^2+\beta XY+\gamma Y^2+\delta X+\epsilon Y+\eta
$$

be a quadric. Then there is a [change of variables](https://de.wikiversity.org/wiki/Affiner_Raum/Lineare_Variablentransformation/Definition) in the affine plane such that, in the new variables, the transformed polynomial has the form

$$
G=\gamma Y^2+H(X),
\qquad
H(X)=aX^2+bX+c,
$$

with $\gamma\ne0$. If $a\ne0$, we can arrange that $b=0$.

Over an [algebraically closed field](https://de.wikiversity.org/wiki/K%C3%B6rpertheorie_%28Algebra%29/Algebraisch_abgeschlossen/Definition), we can arrange that $\gamma=1$ by a change of variables.

If we are interested in the generated ideal or the zero locus, we can also arrange that $\gamma=1$ by division.

#### [Proof](https://de.wikiversity.org/wiki/Affine_Quadriken_in_zwei_Variablen/Erste_Reduktion/Fakt/Beweis) {#br-ak-2025-2026-l07-lem-01-proof}

First we reduce to the case $\gamma\ne0$. If $\gamma=0$ and $\alpha\ne0$, we may interchange $X$ and $Y$. If $\alpha=\gamma=0$, then $\beta\ne0$. In this case, the change

$$
X\longmapsto X+Y,
\qquad
Y\longmapsto Y,
$$

makes the coefficient of $Y^2$ nonzero. Henceforth we therefore assume that $\gamma\ne0$.

We write the polynomial as

$$
\gamma Y^2+(\beta X+\epsilon)Y+\widetilde H(X),
$$

where $\widetilde H$ is a polynomial in $X$ of degree $\le2$. Completing the square gives

$$
\gamma\left(Y+\frac{\beta X+\epsilon}{2\gamma}\right)^2
+\widetilde H(X)-\frac{(\beta X+\epsilon)^2}{4\gamma}.
$$

In the new variables

$$
Y+\frac{\beta X+\epsilon}{2\gamma}
\qquad\text{and}\qquad
X,
$$

the equation has the form

$$
G=\gamma Y^2+H(X),
\qquad
H(X)=aX^2+bX+c.
$$

If $K$ is algebraically closed, $\gamma$ has a square root, so $Y\mapsto Y/\sqrt\gamma$ makes the coefficient equal to $1$. The other additional assertion is clear. $\square$

## Classification of real and complex quadrics {#br-ak-2025-2026-l07-s02}

### [Example: classification of real quadrics](https://de.wikiversity.org/wiki/Affine_Quadriken_in_zwei_Variablen/Reell/Klassifizierung/Beispiel) {#br-ak-2025-2026-l07-ex-01}

Let $K=\mathbb R$. We want to classify real quadrics, mainly with respect to affine-linear equivalence of their generated principal ideals. In other words, we may make affine changes of variables and divide by $-1$. By [Lemma 7.3](#br-ak-2025-2026-l07-lem-01), we may assume that the defining equation has the form

$$
Y^2=aX^2+bX+c.
$$

If $a=b=0$, the change $Y\mapsto\sqrt cY$ for $c>0$, or $Y\mapsto\sqrt{-c}Y$ for $c<0$, followed by division by $\pm c$, lets us make the right-hand side equal to $1$, $-1$, or $0$.

If $a=0$ and $b\ne0$, we may take $bX+c$ as a new variable and obtain the equation

$$
Y^2=X.
$$

Now let $a\ne0$. The change $X\mapsto X/\sqrt a$ or $X\mapsto X/\sqrt{-a}$ lets us arrange that $a=\pm1$. Completing the square makes $b=0$. If $c=0$, we can transform the equation into

$$
Y^2=\pm X^2.
$$

So let $c\ne0$. By the simultaneous change

$$
X\longmapsto uX,
\qquad
Y\longmapsto uY,
\qquad
u=\sqrt{\pm c},
$$

followed by division, we can arrange that $c=\pm1$. The remaining possibilities to consider are therefore

$$
Y^2=\pm X^2\pm1,
$$

where the two equations

$$
Y^2-X^2=\pm1
$$

are equivalent to one another.

We now know that every real quadric can be brought into one of the following nine forms.

I. $Y^2=0$. This is a *double line*.

II. $Y^2=1$. This means $Y=\pm1$, giving *two parallel lines*.

III. $Y^2=-1$. This locus is *empty*.

IV. $Y^2=X$. This is a *parabola*.

V. $Y^2=X^2$. This means $(Y-X)(Y+X)=0$, giving *two intersecting lines*.

VI. $Y^2=-X^2$. The only solution is the *point* $(0,0)$.

VII. $Y^2=X^2+1$. This means $(Y-X)(Y+X)=1$, giving a *hyperbola*.

VIII. $Y^2=-X^2+1$. This is a *unit circle*.

IX. $Y^2=-X^2-1$. This locus is again *empty*.

Are these nine types all different from one another? That depends on the notion of equivalence used. Types III and IX are both empty, and thus have identical zero loci. On the other hand, the corresponding quotient rings

$$
\mathbb R[X,Y]/(Y^2+1)
\qquad\text{and}\qquad
\mathbb R[X,Y]/(X^2+Y^2+1)
$$

are not isomorphic, and over the complex numbers their zero loci are not the same. We therefore regard them as different here too. Apart from this exception, the zero loci are usually already different for topological reasons. For example, the unit circle is [compact](https://de.wikiversity.org/wiki/Topologie/Grundbegriffe/Kompaktheit/%C3%9Cberdeckungskompakt/Definition), the hyperbola is noncompact with two connected components, and the parabola is noncompact with one connected component, and so on.

However, the double line and the parabola are the same in the real topology, as are the hyperbola and the two parallel lines. In each pair, the quotient rings differ; in the second pair, the complex versions also differ. For example, $K[X,Y]/(Y^2)$ is not reduced, whereas

$$
K[X,Y]/(Y^2-X)\cong K[Y]
$$

is an integral domain. The complex hyperbola is connected because it is isomorphic to

$$
\mathbb C^\times=\mathbb C\setminus\{0\},
$$

that is, to the punctured complex line $\mathbb A_{\mathbb C}^1\setminus\{0\}$.

The following images show the rotation and translation of a quadric.

![First stage of a principal-axis transformation of a quadric](authority/assets/Hauptachsentransformation1.png)

![Second stage of a principal-axis transformation of a quadric](authority/assets/Hauptachsentransformation2.png)

![Third stage of a principal-axis transformation of a quadric](authority/assets/Hauptachsentransformation3.png)

### [Example: classification of complex quadrics](https://de.wikiversity.org/wiki/Affine_Quadriken_in_zwei_Variablen/Komplex/Klassifizierung/Beispiel) {#br-ak-2025-2026-l07-ex-02}

Let $K=\mathbb C$. We want to classify complex quadrics. By [Lemma 7.3](#br-ak-2025-2026-l07-lem-01), we may assume that the defining equation has the form

$$
Y^2=aX^2+bX+c.
$$

If $a=b=0$ and $c=0$, we retain the equation $Y^2=0$. If $a=b=0$ and $c\ne0$, scaling the variable $Y$ and dividing by a nonzero constant lets us make the equation $Y^2=1$.

If $a=0$ and $b\ne0$, we may take $bX+c$ as a new variable and obtain the equation

$$
Y^2=X.
$$

Now let $a\ne0$. The change $X\mapsto X/\sqrt a$ lets us arrange that $a=1$. Completing the square makes $b=0$. Finally, a simultaneous change $X\mapsto uX$, $Y\mapsto uY$, followed by division, lets us arrange that $c=1$ if $c\ne0$; if $c=0$, the form $Y^2=X^2$ is retained.

> **Edition note:** In both normalisation steps above, the source uses scaling or division requiring $c\ne0$ without separating the case $c=0$. This edition makes the distinction explicit: $c=0$ gives form I when $a=b=0$, and form IV, $Y^2=X^2$, when $a\ne0$.

We now know that every complex quadric can be brought into one of the following five forms.

I. $Y^2=0$. This is a *double line*.

II. $Y^2=1$. This means $Y=\pm1$, giving *two parallel complex lines*.

III. $Y^2=X$. This is a *complex parabola*.

IV. $Y^2=X^2$. This means $(Y-X)(Y+X)=0$, giving *two complex lines* intersecting at one point.

V. $Y^2=X^2+1$. This means $(Y-X)(Y+X)=1$, giving a *complex hyperbola*.

In the complex topology, Types I and III are a complex affine line, hence a real plane, and therefore topologically the same. Speaking of a “complex plane” is dangerous in algebraic geometry, since it may mean $\mathbb C$ or $\mathbb C^2$. Their quotient rings differ, however, so they are listed as distinct types. Apart from that pair, all types differ in the complex topology. Besides the real plane, we have the punctured complex affine line (the hyperbola, topologically a punctured real plane), two disjoint lines, and two lines intersecting at a point.

The classification of complex quadrics in the last example holds over every algebraically closed field of characteristic $\ne2$.

## Parametrisation of quadrics {#br-ak-2025-2026-l07-s03}

In elementary number theory, we learn how to obtain all Pythagorean triples systematically. The reason is that the unit circle has a parametrisation by rational functions. Generalising [Exercise 1.28](https://de.wikiversity.org/wiki/Einheitskreis/Rationale_Parametrisierung/Funktionaler_Ausdruck/Aufgabe), we now show that every irreducible quadric can be parametrised rationally.

### [Theorem: rational parametrisation of quadrics](https://de.wikiversity.org/wiki/Quadrik_in_zwei_Variablen/Rationale_Parametrisierung/Fakt) {#br-ak-2025-2026-l07-thm-01}

Let

$$
C=V(F)
$$

be a quadric in two variables, that is,

$$
F=\alpha X^2+\beta XY+\gamma Y^2+\delta X+\epsilon Y+\eta,
$$

with $\alpha,\beta,\gamma$ not all zero. Suppose that there is at least one point on the quadric. Then there are polynomials

$$
P_1,P_2,Q\in K[T],
\qquad
Q\ne0,
$$

such that the image of the rational map

$$
\begin{aligned}
\mathbb A_K^1\supseteq D(Q)&\longrightarrow\mathbb A_K^2,\\
t&\longmapsto
\left(\frac{P_1(t)}{Q(t)},\frac{P_2(t)}{Q(t)}\right)
\end{aligned}
$$

lies in $C$.

If $C$ has at least two points, the map is nonconstant and injective apart from finitely many exceptions.

*Edition note.* Over a finite field, “nonconstant” here refers to the pair of rational functions in $K(T)$, not necessarily to the induced function on the finite set $D(Q)(K)$. As the source's final remark explains, that set can even be empty.

If $C$ is also [irreducible](https://de.wikiversity.org/wiki/Affine_Variet%C3%A4ten/Affin-algebraische_Mengen/Irreduzibel/Definition), the map is surjective apart from finitely many exceptions. In particular, an irreducible quadric with at least two points is a [rational curve](https://de.wikiversity.org/wiki/Ebene_algebraische_Kurven/Rationale_Kurve/Definition).

#### [Proof](https://de.wikiversity.org/wiki/Quadrik_in_zwei_Variablen/Rationale_Parametrisierung/Fakt/Beweis) {#br-ak-2025-2026-l07-thm-01-proof}

By a change of variables, we can arrange that $\alpha\ne0$. We can then divide by $\alpha$ and assume that $\alpha=1$. By translation, we may assume that the origin $0=(0,0)$ lies on the curve. Then $\eta=0$. If the quadric consists of two intersecting lines, we can translate so that the origin is not their intersection point (but still lies on one of the lines).

The idea is, for a point

$$
H=(t,1),
$$

to consider the line through $0$ and $H$ and its intersection with $C$. This intersection consists of at most two points (unless it is the whole line). Since $0$ is one of those points, the other point that must exist is uniquely determined.

So let $H=(t,1)$ be given. The line through $H$ and $0$ consists of all points

$$
(at,a),
\qquad
a\in K.
$$

Its intersection points with $C$ are obtained by substituting $(x,y)=(at,a)$ into $F$ and solving for $a$. Substitution gives the condition

$$
F(at,a)=(at)^2+\beta(at\,a)+\gamma a^2+\delta at+\epsilon a.
$$

The solution $a=0$ corresponds to the origin, which we already know. The second solution is

$$
a_2=\frac{-\delta t-\epsilon}{t^2+\beta t+\gamma}.
$$

This expression is defined if

$$
Q(t)=t^2+\beta t+\gamma\ne0,
$$

which excludes at most two values of $t$. The point on $C$ corresponding to $a_2$ is

$$
\begin{aligned}
a_2(t,1)
&=(a_2t,a_2)\\
&=\left(
t\frac{-\delta t-\epsilon}{t^2+\beta t+\gamma},
\frac{-\delta t-\epsilon}{t^2+\beta t+\gamma}
\right).
\end{aligned}
$$

We must therefore set

$$
P_1=-t(\delta t+\epsilon),
\qquad
P_2=-\delta t-\epsilon.
$$

This map is well-defined on the Zariski-open set $D(Q)$ (and that set is nonempty as soon as the field has at least three elements).

From now on, suppose that $C$ has at least two points. If $\delta=\epsilon=0$, then $F$ has the form

$$
F=X^2+\beta XY+\gamma Y^2.
$$

Since we assumed that $C$ has at least two points, $F$ is a product of two homogeneous linear forms (monic in $X$). If $F$ is the square of a linear form, geometrically we simply have a “double line”, which can be parametrised bijectively directly. Otherwise, $F$ is the product of two distinct homogeneous linear forms, and both corresponding lines pass through the origin, which we have excluded. Thus in this case $\delta$ and $\epsilon$ cannot both be $0$.

We therefore need only consider the situation in which $\delta t+\epsilon$ is not the zero polynomial. It follows that the map on its domain of definition is injective apart from finitely many exceptions, since if $\delta t+\epsilon\ne0$, the preimage $t$ can be reconstructed from the image using

$$
t=\frac{P_1}{Q}\cdot\frac{Q}{P_2}.
$$

To show that the map is surjective apart from finitely many exceptions, we need the assumption that $C$ is irreducible. In particular, this means that $C$ is not the union of two lines. Let $P\in C$ have nonzero $y$-coordinate (there are at most two points with zero $y$-coordinate). Then the line through $P$ and $0$ intersects the parametrising line $V(Y-1)$ at a point

$$
H=(t,1).
$$

Apart from finitely many values of $t$, the map is defined at this point $H$, and $P$ is then its image point. By irreducibility, only finitely many points of $C$ lie on the exceptional lines; thus almost all points are reached. $\square$

![Portrait of an unidentified man, formerly misidentified as Johannes Kepler](authority/assets/Portrait_Confused_With_Johannes_Kepler_1610.jpg)

> **Translator's note:** The frozen source displays the file `Johannes Kepler 1610.jpg` with a caption identifying the sitter as Kepler. The available Commons file is now titled `Portrait Confused With Johannes Kepler 1610.jpg` and identifies the sitter as an unidentified man formerly misidentified as Kepler. The local asset name and caption have been adjusted transparently.

The nonsingular conic sections are also the trajectories of celestial bodies. The possible celestial trajectories were first described by [Johannes Kepler](https://de.wikipedia.org/wiki/Johannes_Kepler). The underlying law states that at each instant, acceleration is proportional to the gravitational force between the central point mass (the star, the Sun) and the moving point mass (the planet, the comet). The attractive force itself depends on the two masses and the square of their distance. There are “bound” orbits (ellipses) and “unbound” orbits (parabolas, hyperbolas).

A circle and an ellipse can be transformed into one another by a linear change of variables. Note that rational parametrisations are not “physical parametrisations”. The latter truly describe the motion: the parameter is time, and the derivative at a given time is the instantaneous velocity. Rational parametrisations “only” describe the trajectory. As is well known, the circle is traversed uniformly (at constant speed) by

$$
(x,y)=(\cos t,\sin t).
$$

![Elliptic orbit](authority/assets/Elliptic_orbit.gif)

![Parabolic orbit](authority/assets/Parabolic_orbit.gif)

![Hyperbolic orbit](authority/assets/Hyperbolic_orbit.gif)

### [Remark: the domain of a quadric parametrisation](https://de.wikiversity.org/wiki/Quadrik_in_zwei_Variablen/Rationale_Parametrisierung/Bemerkung) {#br-ak-2025-2026-l07-rem-01}

The parametrisation of a quadric does not depend on the ground field, since the expressions defining the map are always the same. Over a finite field, however, the domain of definition of a rational map can be empty. Passing to a larger finite field $\mathbb F_q$ always gives the map a nonempty domain of definition.

Geometrically, the gaps in the domain of the parametrisation arise because the connecting lines constructed in the proof of [Theorem 7.6](#br-ak-2025-2026-l07-thm-01) have no other intersection with the quadric besides the origin; or, conversely, the entire line lies on the quadric (which can happen only in the reducible case or for a double line). The exceptional points of the quadric that do not lie in the image are the points on the $x$-axis (in particular the origin) and, in the reducible case, the points on the line lying entirely on the quadric and passing through the origin.
