---
title: "Lecture 8 - Mechanically Defined Algebraic Curves"
stable_id: br-ak-2025-2026-l08
language: en
upstream_title: "Kurs:Algebraische Kurven (Osnabrück 2025-2026)/Vorlesung 8"
upstream_pageid: 165897
upstream_revid: 1051293
upstream_timestamp: "2025-08-18T07:32:25Z"
upstream_mediawiki_sha1: f84804863234f9cbcd9f9c06f334e60a8bde42fa
source_url: "https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)/Vorlesung_8?oldid=1051293"
license: "CC BY-SA 4.0 for translated course text; media retain component rights in authority/RIGHTS-unit-08.csv"
translation_status: complete
---

# Lecture 8: Mechanically Defined Algebraic Curves {#br-ak-2025-2026-l08}

## Mechanically defined algebraic curves {#br-ak-2025-2026-l08-s01}

![Construction of a lemniscate](authority/assets/Lemniscate_Building.gif)

Let $S$ be a rigid rod (think of a mechanical machine component) with two fixed points

$$
P_1,P_2\in S
$$

(think of joints). This rod can move in the plane (that is, $\mathbb R^2$), subject to the condition that the two points remain on prescribed paths $B_1$ and $B_2$, respectively (think of rails). These paths can be quite simple, for example lines or circles. In a steam engine, a rotating wheel and a straight rail are coupled by a rod. How do we describe the resulting motion? What are the *allowed configurations of the system*? Since a configuration is determined by the positions of the two points, each specified by two plane coordinates, this is altogether a four-dimensional situation.

If we fix a point $P$ on the rod (for example, by marking it in colour), what does the *path of motion* (or *trajectory*) of that point in the plane look like?

In the extreme cases

$$
P=P_1
\qquad\text{and}\qquad
P=P_2,
$$

the trajectories are (usually proper) subsets of $B_1$ and $B_2$. For points between them, we expect a *continuous deformation* of one path into the other.

### [Situation: a mechanical rod linkage](https://de.wikiversity.org/wiki/Mechanische_ebene_Kurven/Stangenkoppelung/Bemerkung) {#br-ak-2025-2026-l08-sit-01}

Let $B_1$ and $B_2$ be two plane algebraic curves described by the equations $F_1=0$ and $F_2=0$, with

$$
F_1,F_2\in K[X,Y].
$$

Let $S$ be a “moving line” (a rod) with two points

$$
P_1,P_2\in S,
\qquad
P_1\ne P_2,
$$

at distance $d$ from one another. The *mechanical system* given by all positions of $S$ in the plane satisfying both

$$
P_1\in B_1
\qquad\text{and}\qquad
P_2\in B_2
$$

is described as follows.

A position of the rod in the plane is uniquely determined once the positions of its two points are specified (this does not yet account for the distance condition), hence by four variables

$$
(P_1,P_2)=(x_1,y_1,x_2,y_2).
$$

An *allowed configuration* must satisfy the following three algebraic conditions.

1. $F_1(x_1,y_1)=0$.

2. $F_2(x_2,y_2)=0$.

3. $(x_2-x_1)^2+(y_2-y_1)^2=d^2$ (the distance condition).

Thus we have three algebraic equations in four variables, so we expect the solution set to be a curve in $\mathbb A_K^4$. A point

$$
P\in S
$$

is described by its distance from $P_1$ or $P_2$. Since these points move in the mechanical system, we specify the *co-moving point* $P$ by

$$
P=P_1+u(P_2-P_1)
$$

(so the distance of $P$ from $P_1$ is $\lVert u(P_2-P_1)\rVert=\lvert ud\rvert$), and write its coordinates as

$$
\begin{aligned}
(x,y)
&=(x_1,y_1)+u(x_2-x_1,y_2-y_1)\\
&=(ux_2+(1-u)x_1,uy_2+(1-u)y_1).
\end{aligned}
$$

The entire mechanical system can then be expressed (by a linear transformation) in the four variables $x_1,y_1,x,y$. For $u\ne0$, substitute

$$
x_2=\frac{x-(1-u)x_1}{u}
\qquad\text{and}\qquad
y_2=\frac{y-(1-u)y_1}{u}
$$

into the equations. In the new variables, we obtain the three equations

$$
\begin{aligned}
F_1(x_1,y_1)&=0,\\
F_2\left(
\frac{x-(1-u)x_1}{u},
\frac{y-(1-u)y_1}{u}
\right)&=0,\\
(x-x_1)^2+(y-y_1)^2&=u^2d^2.
\end{aligned}
$$

In principle, the trajectory corresponding to $P$ can be obtained by “eliminating” the variables $x_1$ and $y_1$ from this system, yielding an algebraic equation for $x$ and $y$. This is easier said than done, however; it is often more useful to simplify the system by skilful manipulation.

*Edition clarification.* Elimination gives polynomial equations satisfied by the trajectory, not necessarily an exact description of its real points. Real projections can require inequalities; the line-segment trajectories in the two-line example below illustrate this distinction.

### [Remark: a co-moving plane](https://de.wikiversity.org/wiki/Mechanische_ebene_Kurven/Stangenkoppelung/Mitbewegte_Ebene/Bemerkung) {#br-ak-2025-2026-l08-rem-01}

Sometimes we are also interested in the situation where an entire plane moves with the rod, and in the trajectories of points in that plane. This happens, for example, when further machine components are mounted on the rod. In that case, any point of the plane can be expressed relative to $P_1$ and $P_2$ as

$$
(x,y)
=(x_1,y_1)
+u(x_2-x_1,y_2-y_1)
+v(y_2-y_1,-x_2+x_1).
$$

Thus $P_1$ is taken as the origin of the moving plane, the line connecting it to $P_2$ as the first coordinate axis, and the perpendicular axis as the second coordinate axis.

The whole mechanical rod system is therefore described by four variables with three equations. Its visible operation, however—the motion of a fixed point $P$ on $S$—gives a trajectory in the affine plane.

We consider some examples.

## Two lines as paths {#br-ak-2025-2026-l08-s02}

### [Example: two lines as paths](https://de.wikiversity.org/wiki/Mechanische_ebene_Kurven/Stangenkoppelung/Zwei_Geraden/Beispiel) {#br-ak-2025-2026-l08-ex-01}

Let $L_1$ and $L_2$ be two lines in the real plane $\mathbb R^2$, and let $S$ be a moving line (a rod) with two points $P_1,P_2$ at distance $d$ from one another. The allowed configurations of the system are the positions of $S$ satisfying both

$$
P_1\in L_1
\qquad\text{and}\qquad
P_2\in L_2.
$$

Let the lines be specified by

$$
L_1=\{(x,y)\mid a_1x+b_1y=c_1\}
$$

and

$$
L_2=\{(x,y)\mid a_2x+b_2y=c_2\}.
$$

By [Situation 8.1](#br-ak-2025-2026-l08-sit-01), the allowed configurations are specified by three conditions

$$
\begin{aligned}
a_1x_1+b_1y_1&=c_1,\\
a_2x_2+b_2y_2&=c_2,\\
(x_2-x_1)^2+(y_2-y_1)^2&=d^2.
\end{aligned}
$$

The solution set of each linear equation is a three-dimensional affine subspace. The solution set of the third equation can be viewed as the product of a circle (in the variables $x_2-x_1$ and $y_2-y_1$) with an affine plane. This is a kind of cylinder, although its fibres are two-dimensional. How can we describe their common zero locus, and what trajectory does the mechanical system produce for a point

$$
P\in S?
$$

By a change of variables, we may assume that the first line is the $x$-axis, defined by

$$
y=0,
$$

while the other line is defined by

$$
ax+by=c.
$$

For the system, this gives the condition $y_1=0$, so $y_1$ can be eliminated. We then obtain a system with three variables $x_1,x_2,y_2$ and two conditions

$$
\begin{aligned}
(x_2-x_1)^2+y_2^2&=d^2,\\
ax_2+by_2&=c.
\end{aligned}
$$

**Parallel lines.**

![Parallel lines](authority/assets/Parallelle_lijnen.png)

If the second line is parallel to the first, then $a=0$, and the second equation can be solved for $y_2$, giving

$$
y_2=\frac cb=e
$$

(with $b\ne0$, since otherwise the equation does not define a line). The number $e$ is the distance between the parallel lines.

*Edition note.* This source wording and the comparisons below assume $e\ge0$, which can be arranged by reflecting the $y$-axis coordinate if necessary. Without that convention, the distance is $\lvert e\rvert$ and the three cases compare $\lvert e\rvert$ with $d$. We can now eliminate $y_2$ as well, leaving the single equation

$$
(x_2-x_1)^2+e^2=d^2,
$$

or

$$
(x_2-x_1)^2=d^2-e^2=(d-e)(d+e).
$$

If $e>d$, this has no solution (the constant distance between the parallel lines exceeds the coupling distance on the rod).

If $e=d$, we obtain the condition

$$
x_1=x_2.
$$

This corresponds to the situation in which the distance between the parallel lines equals the coupling distance. The only allowed configurations are those in which the rod is perpendicular to both lines. The solution set is therefore a line. For each point on the rod, the trajectory is simply another parallel line.

Now let $e<d$. Then

$$
x_2-x_1=\pm\sqrt{(d-e)(d+e)}.
$$

The solution set consists of two disjoint lines. These correspond to the two different ways of attaching the rod, which cannot be transformed into one another. The mechanical system therefore has two connected components. For a point on the rod, however, both attachments give the same trajectory: a parallel line that is, in a sense, traversed twice. Thus the solution set of the complete mechanical system consists of two parallel affine lines in four-dimensional affine space, whereas their trajectories for a fixed point form just one line.

**Nonparallel lines.**

Now consider the case where the two lines are not parallel. They then intersect, and the solution set cannot be empty. By a further translation (called a linear transformation in the source), we may assume that their intersection is the origin $(0,0)$. The second equation is then described by

$$
x_2=ey_2.
$$

We can therefore eliminate $x_2$, obtaining in the two variables $x_1,y_2$ the single equation

$$
(ey_2-x_1)^2+y_2^2=d^2.
$$

Thus the configuration space of the mechanical system lies in a plane (defined by $y_1=0$ and $x_2=ey_2$) and is described by a quadric. Taking $ey_2-x_1$ as a new variable shows that this is an ellipse (in coordinates $x_1,y_2$; in coordinates $ey_2-x_1,y_2$, it is a circle).

![An ellipse](authority/assets/Ellipse_tri.png)

What do the trajectories look like? Let $P$ be the point on the rod given by

$$
P_1+t(P_2-P_1).
$$

By the [description in Situation 8.1](#br-ak-2025-2026-l08-sit-01), $P$ has coordinates

$$
((1-t)x_1+tey_2,ty_2),
$$

subject to

$$
(ey_2-x_1)^2+y_2^2=d^2.
$$

In the extreme cases $t=0$ and $t=1$, the resulting solution sets are respectively $(x_1,0)$ (with arbitrary $x_1$) and $(ey_2,y_2)$ (with arbitrary $y_2$). The condition

$$
(ey_2-x_1)^2+y_2^2=d^2
$$

must still be satisfied: for a given $x_1$ (or $y_2$), the equation must have a solution in the other variable. Such a solution exists when $x_1$ (or $y_2$) is sufficiently small. Altogether, we obtain certain segments on the original lines. The points $P_1$ and $P_2$ must stay on their paths and cannot move arbitrarily far from the other line.

> **Edition note:** “Sufficiently small” in the source means small in absolute value. For $t=0$, minimising the left-hand side over $y_2$ gives the exact condition $|x_1|\le d\sqrt{1+e^2}$; for $t=1$, minimising over $x_1$ gives the exact condition $|y_2|\le d$.

So let

$$
t\ne0,1.
$$

The ansatz

$$
(x,y)=((1-t)x_1+tey_2,ty_2)
$$

gives

$$
y_2=\frac yt
$$

and

$$
x_1=\frac{x-tey_2}{1-t}=\frac{x-ey}{1-t}
$$

(so the preimage is uniquely determined). The equation then becomes

$$
\left(\frac{ey}{t}-\frac{x-ey}{1-t}\right)^2+\frac{y^2}{t^2}=d^2,
$$

which is again the equation of an ellipse.

## A line and a circle as paths {#br-ak-2025-2026-l08-s03}

We now consider a mechanical curve for which one path is a line and the second is a circle. This is the situation in a steam engine (in particular when the line passes through the centre of the circle).

![A steam engine in action](authority/assets/Steam_engine_in_action.gif)

Without loss of generality, we may assume that the line is given by

$$
y=0.
$$

The coordinates of the point on the line are then

$$
P_1=(x_1,y_1)=(x_1,0).
$$

We may assume that the circle has centre $(0,b)$ and radius $r$. The point on the circular path

$$
P_2=(x_2,y_2)
$$

satisfies

$$
x_2^2+(y_2-b)^2=r^2.
$$

Thus the entire mechanical system is described by the two conditions

$$
\begin{aligned}
x_2^2+(y_2-b)^2&=r^2,\\
(x_2-x_1)^2+y_2^2&=d^2,
\end{aligned}
$$

where $d$ again denotes the coupling distance. Looking at these equations in the coordinates $x_2,y_2$ and $x_2-x_1$ shows that they describe the intersection of two cylinders, as in [Example 4.6](https://de.wikiversity.org/wiki/Affine_Variet%C3%A4ten/Irreduzible_Teilmengen/Schnitt_von_zwei_gleichgro%C3%9Fen_Zylindern/Zwei_Kreise/Beispiel). Thus, in three suitable coordinates, the allowed rod configurations can be interpreted as the intersection of two cylinders. However, their radii need not agree, nor need their central axes intersect. Such an intersection and its associated trajectories can be quite complicated.

For the following examples, we need a lemma describing a simple *elimination situation*.

### [Lemma: elimination of two quadratic equations](https://de.wikiversity.org/wiki/Elimination/Zwei_quadratische_Gleichungen/Direkt/Fakt) {#br-ak-2025-2026-l08-lem-01}

Let $R$ be an [integral domain](https://de.wikiversity.org/wiki/Kommutative_Ringtheorie/Integrit%C3%A4tsbereich/Definition), and let

$$
F_1=a_1X^2+b_1X+c_1
\qquad\text{and}\qquad
F_2=a_2X^2+b_2X+c_2
$$

be two quadratic polynomials in one variable over $R$, with

$$
a_1\ne0,
$$

and with $(a_1,b_1)$ and $(a_2,b_2)$ linearly independent. Then the ideal

$$
(F_1,F_2)\cap R
$$

contains the element

$$
\begin{aligned}
&(a_2c_1-a_1c_2)^2\\
&\quad-b_1(-a_2c_1b_2-c_2a_2b_1+a_1b_2c_2)\\
&\quad+c_1(a_1b_2^2-2a_2b_1b_2).
\end{aligned}
$$

#### [Proof](https://de.wikiversity.org/wiki/Elimination/Zwei_quadratische_Gleichungen/Direkt/Fakt/Beweis2) {#br-ak-2025-2026-l08-lem-01-proof}

First we have

$$
a_2F_1-a_1F_2
=(a_2b_1-a_1b_2)X+a_2c_1-a_1c_2.
$$

*Edition supplement.* The source's substitution argument below does not by itself justify division inside an ideal. A direct identity supplies the justification. Put $A=a_2b_1-a_1b_2$, $B=a_2c_1-a_1c_2$, and let $E\in R$ denote the element displayed in the lemma. Expanding gives

$$
E=(a_2B-b_2A-a_2AX)F_1+(a_1AX+b_1A-a_1B)F_2.
$$

Thus $E\in(F_1,F_2)\cap R$ without any division. The following is the source's original calculation.

This gives the expression (this argument is not entirely correct, but can also be carried out more rigorously)

$$
X=-\frac{a_2c_1-a_1c_2}{a_2b_1-a_1b_2}.
$$

Substituting into $F_1$ and multiplying by the square of the denominator gives

$$
\begin{aligned}
&a_1(a_2c_1-a_1c_2)^2\\
&\quad-b_1(a_2c_1-a_1c_2)(a_2b_1-a_1b_2)\\
&\quad+c_1(a_2b_1-a_1b_2)^2.
\end{aligned}
$$

The second summand contains $-b_1a_2c_1a_2b_1$, and the third contains $c_1a_2^2b_1^2$; these two terms cancel. Every remaining monomial contains $a_1$. We can therefore cancel $a_1$, leaving

$$
\begin{aligned}
&(a_2c_1-a_1c_2)^2\\
&\quad-b_1(-a_2c_1b_2-c_2a_2b_1+a_1b_2c_2)\\
&\quad+c_1(a_1b_2^2-2a_2b_1b_2).
\end{aligned}
$$

$\square$

### [Example: the unit circle and a tangent line](https://de.wikiversity.org/wiki/Mechanisch_definierte_Kurven/Stangenkonfiguration/Kreis_und_tangentiale_Gerade/Beispiel) {#br-ak-2025-2026-l08-ex-02}

Consider the mechanical linkage defined by the unit circle and its tangent line at $(0,1)$, with coupling distance

$$
d=2.
$$

Thus the point on the straight path and the point on the circular path are

$$
P_1=(x_1,1)
\qquad\text{and}\qquad
P_2=(x_2,y_2),
$$

with the two conditions

$$
\begin{aligned}
x_2^2+y_2^2&=1,\\
(x_2-x_1)^2+(y_2-1)^2&=4.
\end{aligned}
$$

This is therefore the intersection of two cylinders, but with different radii and nonintersecting central axes. The difference of the equations is

$$
x_1^2-2x_1x_2-2y_2-2=0,
$$

which can replace one of them. This also shows that we can eliminate $y_2$, obtaining a system with one equation in two variables; see [Exercise 8.9](https://de.wikiversity.org/wiki/Mechanisch_definierte_Kurven/Stangenkonfiguration/Kreis_und_tangentiale_Gerade/Zweidimensionale_Interpretation/Aufgabe). The system is irreducible; see [Exercise 8.10](https://de.wikiversity.org/wiki/Mechanisch_definierte_Kurven/Stangenkonfiguration/Kreis_und_tangentiale_Gerade/Irreduzibel/Aufgabe).

The following two lines are of interest:

$$
G_1=V(x_2,y_2+1)
$$

and

$$
G_2=V(x_2-x_1,y_2+1).
$$

They intersect at the point

$$
P=(0,0,-1).
$$

The line $G_1$ lies on one cylinder and is tangent to the other, and conversely. Geometrically, the smaller cylinder punches a “bent figure eight” out of the larger cylinder, with $P$ as the crossing point of the figure eight.

![Intersection of two cylinders](authority/assets/Intersection_of_cylinders.jpg)

The allowed rod configurations can be obtained as follows. For each point of the circle, the rod has two possible positions, except at the circular-path point $(0,-1)$, where the straight-path point must be $(0,1)$.

Start with $(0,1)$ as the circular-path point and $(-2,1)$ as the straight-path point (so the rod lies to the left along the line), and let the circular-path point move clockwise around the circle. It pulls the straight-path point behind it until it reaches the bottom at $(0,-1)$. The rod is then the vertical diameter of the circle (the straight-path point is at $(0,1)$ and the circular-path point is at the bottom). The circular-path point then moves upwards along the left-hand arc, pushing the rod further to the right until the straight-path point reaches $(2,1)$.

The other possibility with $(0,1)$ as the circular-path point has the rod lying to the right along the line (with $(2,1)$ as the straight-path point). The circular-path point again moves clockwise. At first it pushes the straight-path point to the right until an extreme position is reached, where the rod is perpendicular to the circle at the circular-path point. It then pulls the straight-path point back to the left as the rod rises, until the rod occupies the vertical diameter of the circle. The circular-path point next moves upwards along the left-hand arc again, pushing the straight-path point leftwards to an extreme position, and finally pulling it back to $(-2,1)$.

In particular, the rod occupies the vertical diameter twice; this rod configuration therefore corresponds to the crossing point of the figure eight.

We now want to calculate the trajectory of the midpoint of the rod, namely

$$
\begin{aligned}
P
&=P_1+\frac12(P_2-P_1)\\
&=(x_1,1)+\frac12(x_2-x_1,y_2-1)\\
&=\left(\frac12x_1+\frac12x_2,\frac12y_2+\frac12\right)\\
&\mathrel{:=}(x,y).
\end{aligned}
$$

We seek an equation for $x$ and $y$, and introduce the variable

$$
z=\frac12x_1-\frac12x_2.
$$

Then

$$
x_1=x+z,\qquad x_2=x-z,\qquad y_2=2y-1,
$$

and the system in the new variables becomes

$$
(x-z)^2+(2y-1)^2=1
\qquad\text{and}\qquad
(-2z)^2+(2y-2)^2=4.
$$

The second equation can be written as

$$
z^2+(y-1)^2=1,
$$

or as

$$
z^2+y^2-2y=0.
$$

Expanding the first equation gives

$$
z^2-2zx+x^2+4y^2-4y=0.
$$

By [Lemma 8.4](#br-ak-2025-2026-l08-lem-01), with

$$
R=\mathbb R[x,y]
$$

and the additional variable $z$ (so $a_1=a_2=1$ and $b_1=0$), we obtain the equation

$$
\begin{aligned}
(c_1-c_2)^2+c_1b_2^2
&=(y^2-2y-x^2-4y^2+4y)^2+(y^2-2y)(2x)^2\\
&=(-3y^2+2y-x^2)^2+(y^2-2y)(2x)^2\\
&=9y^4+x^4+4y^2-12y^3+6x^2y^2-4x^2y\\
&\qquad+4x^2y^2-8x^2y\\
&=9y^4+10x^2y^2+x^4-12y^3-12x^2y+4y^2.
\end{aligned}
$$

This is a quartic (a curve of degree four) with two singularities.

![Figure for the exercise](authority/assets/Alg_Kurven_OS2008_Lsg8.10_v2.png)

### [Example: radius equal to the coupling distance](https://de.wikiversity.org/wiki/Mechanische_ebene_Kurven/Stangenkoppelung/Gerade_und_Kreis/Radius_ist_Koppelungsabstand/Beispiel) {#br-ak-2025-2026-l08-ex-03}

Consider the mechanical system consisting of the unit circle and the $x$-axis, with coupling distance

$$
d=1.
$$

The mechanical system is described by the two equations

$$
\begin{aligned}
x_2^2+y_2^2&=1,\\
(x_2-x_1)^2+y_2^2&=1.
\end{aligned}
$$

This is the intersection of two cylinders with equal radii and intersecting central axes, so we may use the results of [Example 4.6](https://de.wikiversity.org/wiki/Affine_Variet%C3%A4ten/Irreduzible_Teilmengen/Schnitt_von_zwei_gleichgro%C3%9Fen_Zylindern/Zwei_Kreise/Beispiel). There we showed that the intersection consists of two ellipses meeting at two points. This description must also reappear in the context of the mechanical system. Which rod configurations correspond to the first ellipse, which to the second, and which lie on both?

Let us survey the allowed configurations. If the line point (the point on the straight path) is the centre of the circle, every point of the circle is allowed as the circular-path point. The radial rays of the circle therefore form a family of allowed rod configurations, together making up one ellipse. The other ellipse corresponds to the configurations in which the straight-path point moves from $-2$ to $+2$, pushing the circular-path point ahead of it or pulling it behind on the upper or lower arc. Two rod configurations belong to both families: those with the circle's centre as the straight-path point and $(0,1)$ or $(0,-1)$ as the circular-path point. In such a configuration, the mechanical system can not only move forwards and backwards but also change direction in an essential way.

What do the trajectories of a point on the moving rod look like? The total trajectory is the union of the two trajectories corresponding to the two irreducible components of the system. How many self-intersection points are there?

For a point

$$
P=P_1+u(P_2-P_1)
$$

on the coupling rod, its coordinates are

$$
(z_1,z_2)=(x_1+u(x_2-x_1),uy_2).
$$

For $u=0$, the trajectory is the real interval $[-2,2]$, and for $u=1$, it is the unit circle. So now let

$$
u\ne0,1.
$$

The projection of the radial components of the system is simply a circle of radius $u$. The projection of the other ellipse is again an ellipse, which can intersect the circle in different ways.

*Edition note.* The radius is $\lvert u\rvert$ if negative $u$ is allowed. There is also a degenerate case omitted in the source: on the second component, $x_1=2x_2$, so $(z_1,z_2)=((2-u)x_2,uy_2)$ with $x_2^2+y_2^2=1$. For $u=2$, its image is the segment $\{0\}\times[-2,2]$, not an ellipse. For $u\ne0,2$, that component projects to a nondegenerate ellipse. See also [Exercise 8.23](https://de.wikiversity.org/wiki/Schnitt_von_zwei_Zylindern/Projektion_auf_Fl%C3%A4chen/Charakterisierung_der_Bilder/Aufgabe).
