---
title: "Public Solutions to Worksheet 16"
stable_id: br-ak-2025-2026-w16-solutions
language: en
upstream_map: authority/wikiversity/unit-16/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 835029f5f5f46dea23486bd62edec6f4ab64667192c44504fee3af259e5b5266
public_solution_count: 6
upstream_solution_revisions: "Soal 16.1=1068100; Soal 16.10=1067953; Soal 16.11=1094645; Soal 16.12=1112750; Soal 16.13=1089809; Soal 16.15=1096228"
solution_xml_sha256: "01=420fa066280c15a83372541ece706d0e5ec995f1aa1c0266510da72582beda97; 10=730f7926be80a253bc8167f3f349a66e788ac8d689437791490bf93d68c8d797; 11=98d614f4acfbf8dcaea8e637ad6a18375546274f6d4ee20df9163ebe46e7de0a; 12=4cbfdb0498bda3335528ebd078b592eea736da509ed6f0be8e6ce4f4b8b9cc61; 13=b5e3335a35c26d85b544cd4a755256ba1696af3f1d766495f4239d1a7c739a62; 15=41008ef3351d2d28fb88f1c1c2fb3e1b3580ddc40884547a7bb4ddaf0995d248"
license: "CC BY-SA 4.0; the image in Solution 16.12 remains CC BY-SA 3.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 16 {#br-ak-2025-2026-w16-solutions}

At the frozen revision boundary, the source provides public solutions
only for Exercises 16.1, 16.10, 16.11, 16.12, 16.13, and 16.15. No
additional solutions have been created for this edition. Solution 16.13
is retained only as far as it is actually available in the source; that
boundary is explained where it occurs.

<!-- upstream_solution: Zariski-Filter/Irreduzibler Filter ist durch D(f) bestimmt/Aufgabe/Lösung; pageid=168442; revid=1068100 -->
<!-- upstream_solution_revid: 1068100 -->

## Solution to Exercise 16.1 {#br-ak-2025-2026-w16-sol-01}

Let $F$ be an irreducible filter. For every $U\in F$, write

$$
U=D(f_1)\cup\cdots\cup D(f_k).
$$

Since $F$ is irreducible, at least one $D(f_i)$ belongs to $F$. Since

$$
D(f_i)\subseteq U,
$$

the open sets of the form $D(f)$ belonging to $F$ generate the filter.

[Back to Exercise 16.1](#br-ak-2025-2026-w16-ex-01).

<!-- upstream_solution: K-Spektrum/Bijektiv stetig, nicht homöomorph/Aufgabe/Lösung; pageid=168403; revid=1067953 -->
<!-- upstream_solution_revid: 1067953 -->

## Solution to Exercise 16.10 {#br-ak-2025-2026-w16-sol-10}

Consider the affine line $\mathbb A_K^1$ and the punctured line

$$
Y=\mathbb A_K^1\setminus\{0\},
$$

which is affine because it can be realised as a hyperbola. Consider the
disjoint union

$$
Z=Y\uplus\{P\}
$$

with one additional point. There is a natural morphism

$$
Z\longrightarrow\mathbb A_K^1
$$

that is the open inclusion on $Y$ and sends $P$ to the origin. This map
is bijective. However, $\{P\}$ is open on the left but not on the right.
Thus the inverse map is not continuous.

[Back to Exercise 16.10](#br-ak-2025-2026-w16-ex-10).

<!-- upstream_solution: Einheitskreis/Punktepaar/Automorphismus/Aufgabe/Lösung; pageid=95397; revid=1094645 -->
<!-- upstream_solution_revid: 1094645 -->

## Solution to Exercise 16.11 {#br-ak-2025-2026-w16-sol-11}

It suffices to give, for $(1,0)$ and $P=(a,b)\in V$, an automorphism of
the circle taking $(1,0)$ to $P$. The required automorphism from $P$ to
$Q$ is then obtained by composing maps of this kind and, where necessary,
their inverses.

Consider the bijective linear map

$$
\varphi:K^2\longrightarrow K^2
$$

given by the matrix

$$
\begin{pmatrix}
a&-b\\
b&a
\end{pmatrix}.
$$

It sends $(1,0)$ to $(a,b)$. A point $(x,y)\in V$ maps to

$$
(ax-by,bx+ay).
$$

For the image point we have

$$
\begin{aligned}
(ax-by)^2+(bx+ay)^2
&=a^2x^2-2abxy+b^2y^2+b^2x^2+2abxy+a^2y^2\\
&=(a^2+b^2)x^2+(a^2+b^2)y^2\\
&=x^2+y^2\\
&=1.
\end{aligned}
$$

Thus the image point again lies on the circle, and $\varphi$ induces an
algebraic map $V\to V$. The linear map with matrix

$$
\begin{pmatrix}
a&b\\
-b&a
\end{pmatrix}
$$

gives the inverse morphism. We therefore obtain an automorphism.

**Edition note:** in the second term on the first line of the calculation,
the source writes $(bx+ax)^2$. Both the map just defined and the expansion
on the following line require $(bx+ay)^2$, which is displayed here.

[Back to Exercise 16.11](#br-ak-2025-2026-w16-ex-11).

<!-- upstream_solution: Achsenkreuz/Drei Geraden in Ebene/Beziehung/Aufgabe/Lösung; pageid=95122; revid=1112750 -->
<!-- upstream_solution_revid: 1112750 -->

## Solution to Exercise 16.12 {#br-ak-2025-2026-w16-sol-12}

1. We have

   $$
   V=V(XY,XZ,YZ)
   =V(X,Y)\cup V(X,Z)\cup V(Y,Z),
   $$

   the union of the three coordinate axes in three-dimensional affine space.

   ![Three coordinate axes meeting at the origin](authority/assets/Draft0-500.png)

   *Sketch of the union of the three coordinate axes. Kalan,
   [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Source
   details are given in the Unit 16 media credits.*

   **Edition note:** the source displays $V(XY)\cup V(XZ)\cup V(YZ)$ on
   the right. That union is not the common zero locus of the three
   polynomials and does not consist only of the three axes. This edition
   displays the component decomposition matching the left-hand side and
   the source's following sentence.

2. The linear map

   $$
   K^3\longrightarrow K^2
   $$

   given, with respect to the standard bases, by the matrix

   $$
   \begin{pmatrix}
   1&0&1\\
   0&1&1
   \end{pmatrix}
   $$

   is the identity on the $XY$-plane and sends the $Z$-axis to the main
   diagonal in that plane. Thus the image of the union of the axes lies
   entirely in

   $$
   W=V(ST(S-T)),
   $$

   giving a morphism

   $$
   \varphi:V\longrightarrow W.
   $$

   This morphism is bijective because each of the lines involved is
   mapped bijectively to one of the lines.

3. Algebraically, there is a $K$-algebra homomorphism

   $$
   K[S,T]/(ST(S-T))
   \longrightarrow
   K[X,Y,Z]/(XY,XZ,YZ),
   $$

   with

   $$
   S\longmapsto X+Z,
   \qquad
   T\longmapsto Y+Z.
   $$

   It induces a homomorphism of localisations

   $$
   \bigl(K[S,T]/(ST(S-T))\bigr)_{S+T}
   \longrightarrow
   \bigl(K[X,Y,Z]/(XY,XZ,YZ)\bigr)_{X+Y+2Z}.
   $$

   The intersection of $V(S+T)$, respectively $V(X+Y+2Z)$, with each of
   the three lines consists only of the origin, using
   $\operatorname{char}(K)\ne2$. Thus both localisations describe the
   complement of the origin.

   In the variables

   $$
   A=X+Z,
   \qquad
   B=Y+Z,
   $$

   the ring on the right can be written as

   $$
   K[A,B,Z,(A+B)^{-1}]
   \big/
   \bigl((A-Z)Z,(B-Z)Z,(A-Z)(B-Z)\bigr).
   $$

   In this ring,

   $$
   \begin{aligned}
   2AB
   &=2Z(A+B)-2Z^2\\
   &=2Z(A+B)-AZ-BZ\\
   &=Z(A+B),
   \end{aligned}
   $$

   so

   $$
   Z=\frac{2AB}{A+B}.
   $$

   Thus $Z$ can be eliminated. Since

   $$
   A-Z
   =A-\frac{2AB}{A+B}
   =\frac{A^2+AB-2AB}{A+B}
   =\frac{A^2-AB}{A+B},
   $$

   the ideal generators become

   $$
   (A-Z)Z
   =\frac{A^2-AB}{A+B}\,\frac{2AB}{A+B}
   =\frac{2A^2B(A-B)}{(A+B)^2},
   $$

   $$
   (B-Z)Z
   =-\frac{2AB^2(A-B)}{(A+B)^2},
   $$

   and

   $$
   \begin{aligned}
   (A-Z)(B-Z)
   &=\frac{A^2-AB}{A+B}\,
     \frac{B^2-AB}{A+B}\\
   &=\frac{2A^2B^2-AB^3-A^3B}{(A+B)^2}.
   \end{aligned}
   $$

   **Edition note:** the source prints a positive sign before the
   fraction for $(B-Z)Z$. The displayed substitution gives a negative
   sign. Changing the sign does not change the generated ideal, but the
   algebraic equality is displayed here with the correct sign.

   Since $A+B$ and $2$ are units, the first two generators give

   $$
   A^3B=A^2B^2=AB^3,
   $$

   so the third generator is redundant. Moreover,

   $$
   AB(A-B)(A+B)=AB(A^2-B^2)
   $$

   belongs to the ideal. Since $A+B$ is a unit, $AB(A-B)$ also belongs
   to the ideal; conversely, it generates the same ideal. Thus the map
   given by $S\mapsto A$ and $T\mapsto B$ is an isomorphism on the
   complement of the origin.

[Back to Exercise 16.12](#br-ak-2025-2026-w16-ex-12).

<!-- upstream_solution: Kreisgleichung/Morphismus/2 zu 1/Aufgabe/Lösung; pageid=95083; revid=1089809 -->
<!-- upstream_solution_revid: 1089809 -->

## Solution to Exercise 16.13 {#br-ak-2025-2026-w16-sol-13}

There is a morphism

$$
V(Z^2+W^2-1)\longrightarrow\mathbb A_K^2.
$$

It therefore suffices to check that its image satisfies the circle
equation. Indeed,

$$
\begin{aligned}
X^2+Y^2
&=(Z^2-W^2)^2+4Z^2W^2\\
&=(Z^2-(1-Z^2))^2+4Z^2(1-Z^2)\\
&=(2Z^2-1)^2+4Z^2(1-Z^2)\\
&=4Z^4-4Z^2+1+4Z^2-4Z^4\\
&=1.
\end{aligned}
$$

**Source-solution boundary:** the frozen public solution stops after
proving that the image satisfies the circle equation. It does not prove
the second assertion of the exercise, that every fibre consists of two
points. This edition does not invent a continuation absent from the source.

[Back to Exercise 16.13](#br-ak-2025-2026-w16-ex-13).

<!-- upstream_solution: Gruppenvarietät/K-Algebra Homomorphismus für Addition/Aufgabe/Lösung; pageid=21349; revid=1096228 -->
<!-- upstream_solution_revid: 1096228 -->

## Solution to Exercise 16.15 {#br-ak-2025-2026-w16-sol-15}

Consider the substitution homomorphism

$$
\begin{aligned}
K[X]&\longrightarrow K[Y,Z],\\
X&\longmapsto Y+Z.
\end{aligned}
$$

The induced map of spectra is

$$
\begin{aligned}
\mathbb A_K^2\cong K^2&\longrightarrow\mathbb A_K^1\cong K,\\
(y,z)&\longmapsto y+z.
\end{aligned}
$$

This is exactly addition on $K$.

[Back to Exercise 16.15](#br-ak-2025-2026-w16-ex-15).
