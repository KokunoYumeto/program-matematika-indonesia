---
title: "Integrative Problem 11 — A Classical Conic and Its Scheme"
stable_id: d100-bridge-integrative-11
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_credit: "Theoretical foundations: Holger Brenner, Algebraische Kurven, Lecture 28, and Bündel, Garben und Kohomologie, Lectures 12 and 27; frozen-revision contributions retain the credits in the source reader."
non_endorsement: "Independent AI-generated material; not human-authored or human-reviewed, and no endorsement by the source author or institution is implied."
---

# Integrative problem 11: a classical conic and its scheme {#d100-bridge-integrative-11}

This problem and solution are independent material, not a source problem
by Holger Brenner. The classical comparison starts from
[Lemma 28.2 on affine charts](https://de.wikiversity.org/w/index.php?oldid=1102391)
and [Definition 28.3 of regular functions](https://de.wikiversity.org/w/index.php?oldid=1104711)
in Lecture 28 of *Algebraische Kurven*. Their translation IDs are
br-ak-2012-l28-lem-01 and br-ak-2012-l28-def-02, respectively.
On the scheme side, use [BGK Lemma 12.9](bgk-reader.html#br-bgk-2019-l12-lem-03)
and [BGK Lemma 12.17](bgk-reader.html#br-bgk-2019-l12-lem-05): Proj
charts are spectra of degree-zero components of localisations, computed
by dehomogenisation.

## Problem {#d100-bridge-integrative-11-soal}

Let $K$ be an algebraically closed field of arbitrary characteristic.
Distinguish

$$
C_{\mathrm{kl}}
=\{[x:y:z]\in\mathbb P^2(K)\mid xz-y^2=0\}
$$

with its Zariski topology and classical regular functions from the scheme

$$
C=\operatorname{Proj}(A),
\qquad A=K[X,Y,Z]/(XZ-Y^2).
$$

1. Compute the charts $U_X=D_+(X)$ and $U_Z=D_+(Z)$ and the gluing
   on their overlap. Prove that they cover the entire scheme, not just
   its $K$-points.
2. Prove that $\nu:\mathbb P_K^1\to C$, given on points by
   $[u:v]\mapsto[u^2:uv:v^2]$, is a scheme isomorphism.
3. List the closed points and generic point of $C$. Compute the stalks
   of the structure sheaf and their residue fields, and compare them
   with the classical local rings. Determine $\Gamma(C,\mathcal O_C)$.
4. Determine the scheme-theoretic intersection with the line $Z=0$ and
   explain what information is lost if only the set of intersection
   points is retained.
5. Explain why $A$ is not the global function ring of $C$ and why
   $\nu^*\mathcal O_C(1)\cong\mathcal O_{\mathbb P_K^1}(2)$.

## Solution {#d100-bridge-integrative-11-penyelesaian}

### 1. Two charts and one inversion {#d100-bridge-integrative-11-jawab-01}

Lemma 12.17 applies because $A$ is standard graded with a homogeneous
relation of degree two. On $U_X$, put $t=Y/X$ and $z=Z/X$. Then

$$
(A_X)_0=K[t,z]/(z-t^2)\cong K[t].
$$

On $U_Z$, put $s=Y/Z$ and $x=X/Z$. Then

$$
(A_Z)_0=K[s,x]/(x-s^2)\cong K[s].
$$

If a homogeneous prime ideal $\mathfrak p$ contains $X$ and $Z$, the
relation $Y^2=XZ$ forces it to contain $Y$. It contains the irrelevant
ideal $(X,Y,Z)$ and is therefore not a Proj point. Thus $U_X$ and
$U_Z$ cover every scheme point.

On $U_X$, the condition $Z\ne0$ means invertibility of $t^2$, which
is equivalent to invertibility of $t$. Since

$$
s=\frac YZ=\frac{Y/X}{Z/X}=\frac{t}{t^2}=t^{-1},
$$

the overlap is $\operatorname{Spec}(K[t,t^{-1}])$, and the gluing
homomorphism is determined by $s\mapsto t^{-1}$.

### 2. An isomorphism, not merely a bijection on points {#d100-bridge-integrative-11-jawab-02}

On the chart $u\ne0$ of $\mathbb P_K^1$, the coordinate is $v/u$.
The formula for $\nu$ gives $t=Y/X=v/u$ and $Z/X=(v/u)^2$. Thus
the chart map is the isomorphism $K[t]\to K[v/u]$, $t\mapsto v/u$.
On the chart $v\ne0$, the corresponding map is $K[s]\to K[u/v]$,
$s\mapsto u/v$.

These maps are compatible on the overlap because both gluings use
inversion. The local maps and their inverses therefore glue to mutually
inverse scheme morphisms. This proves that $\nu$ is a scheme
isomorphism without deducing it merely from a bijection on closed points.

The inverse formula on classical points is $[1:t]$ on $U_X$ and
$[s:1]$ on $U_Z$. Both are regular in their charts, so they also give
an isomorphism of classical varieties. No step divides by $2$; the
result remains valid in characteristic two.

### 3. Points, stalks, and functions {#d100-bridge-integrative-11-jawab-03}

Since $K$ is algebraically closed, the prime ideals of $K[t]$ are $(0)$
and $(t-a)$ for $a\in K$. All closed points of $C$ are therefore

$$
P_a=[1:a:a^2]\quad(a\in K),
\qquad P_\infty=[0:0:1].
$$

The homogeneous prime ideals representing them in $A$ are
$(Y-aX,Z-a^2X)$ and $(X,Y)$. The generic points of the charts, namely
the zero ideals of $K[t]$ and $K[s]$, are identified on the overlap.
The result is one generic point $\eta$ of $C$, whose closure is all
of $C$.

To see that the zero ideal of $A$ is indeed prime, map $X,Y,Z$ to
$u^2,uv,v^2$ in $K[u,v]$. Modulo $XZ-Y^2$, every polynomial has a
representative $B(X,Z)+YC(X,Z)$. Monomials in the image of the first
term have both exponents even; those in the image of the second have
both exponents odd. Distinct monomials in either group remain distinct,
so this map has zero kernel. Thus $A$ is an integral domain, and
$\eta$ is represented by $(0)$ in Proj. The chart argument also shows
that there are no other points.

The local rings and residue fields are

$$
\begin{aligned}
\mathcal O_{C,P_a}&=K[t]_{(t-a)},&
\kappa(P_a)&=K,\\
\mathcal O_{C,P_\infty}&=K[s]_{(s)},&
\kappa(P_\infty)&=K,\\
\mathcal O_{C,\eta}&=K(t),&
\kappa(\eta)&=K(t).
\end{aligned}
$$

For example, the stalk at $P_a$ contains fractions $f(t)/g(t)$ with
$g(a)\ne0$; the map to the residue field evaluates them at $a$. A
stalk is not its residue field: the element $t-a$ is nonzero in
$K[t]_{(t-a)}$ but has zero image in $K$.

The classical definition of a regular function gives the same local
ring at each $P_a$ and $P_\infty$. What the scheme adds is the generic
point as an actual point, not a replacement of the local rings at
classical points. The topology on the closed-point set, as a subspace
of $C$, agrees with the classical topology: on both charts, closed
sets are defined by the same polynomial equations. The classical space
itself has no generic point.

Global sections of the structure sheaf are pairs $f(t)\in K[t]$,
$g(s)\in K[s]$ with $f(t)=g(t^{-1})$ on the overlap. In the Laurent
ring, the first polynomial has only nonnegative exponents and the second
only nonpositive exponents. Hence

$$
\Gamma(C,\mathcal O_C)
=K[t]\cap K[t^{-1}]=K.
$$

The same calculation applies to classical global regular functions.

### 4. Intersection with the tangent line {#d100-bridge-integrative-11-jawab-04}

For $Z=0$, the conic relation gives $Y^2=0$. Every prime on the
intersection contains $Y$ and cannot also contain $X$; hence the whole
intersection lies in $U_X$. The line equation there is $z=0$, while
on the conic $z=t^2$. Thus the scheme-theoretic intersection is

$$
C\cap V_+(Z)=\operatorname{Spec}(K[t]/(t^2)).
$$

The classical intersection point set is just $\{P_0\}$. The intersection
scheme has length two, since the classes of $1,t$ are linearly independent
and $t^2=0$ with $t\ne0$. This nilpotent structure is invisible in
the one-point set.

This does not mean that the conic is singular. On chart $U_X$, the
equation $z-t^2$ has partial derivative $1$ with respect to $z$; the
chart itself is isomorphic to the affine line. The line equation $z=0$
vanishes to order two along the parameter $t$, thus recording tangency.
The same argument remains valid in characteristic two.

### 5. Homogeneous degree does not give global functions {#d100-bridge-integrative-11-jawab-05}

The ring $A$ is graded and contains homogeneous coordinates of positive
degree. Multiplying all coordinates of a point by $\lambda$ multiplies
the values of $X,Y,Z$ by $\lambda$; these coordinates therefore do not
define $K$-valued functions on projective points. They are sections of
$\mathcal O_C(1)$. Regular functions, in contrast, locally use homogeneous
fractions of degree zero. Since $\Gamma(C,\mathcal O_C)=K$, the two
rings are plainly different.

The frames of $\mathcal O_C(1)$ on $U_X$ and $U_Z$ are $X$ and $Z$,
with $Z=t^2X$ on the overlap. Their pullbacks to $\mathbb P_K^1$ have
frames $u^2$ and $v^2$ and transition $v^2=(v/u)^2u^2$. These are
exactly the gluing data for $\mathcal O_{\mathbb P_K^1}(2)$.

As a numerical check, its global sections are represented by polynomials
in $t$ of degree at most two, with basis $1,t,t^2$. The Čech complex
has cokernel

$$
K[t,t^{-1}]\big/\bigl(K[t]+t^2K[t^{-1}]\bigr)=0,
$$

since the two subspaces together contain every Laurent monomial. Thus
$h^0(\mathcal O_C(1))=3$, $h^1(\mathcal O_C(1))=0$, and
$\chi(\mathcal O_C(1))=3$, in accordance with
[BGK Theorem 27.4](bgk-reader.html#br-bgk-2019-l27-thm-02). The degree
two of the conic is visible in the pulled-back twist, although the
conic as a scheme is isomorphic to the projective line.

## Checks and material provenance {#d100-bridge-integrative-11-periksa}

Algebraic closedness is used to identify all closed points with
$K$-valued points. The chart calculations, scheme isomorphism, and
length-two intersection hold over any field. Three objects that must
not be confused are the homogeneous coordinate ring, the global section
ring, and the function field.

The frozen parent revision of classical Lecture 28 is
[1052516](https://de.wikiversity.org/w/index.php?oldid=1052516);
that of BGK Lecture 12 is
[1003742](https://de.wikiversity.org/w/index.php?oldid=1003742).
The BGK entities on [Proj charts](https://de.wikiversity.org/w/index.php?oldid=1102161)
and [dehomogenisation](https://de.wikiversity.org/w/index.php?oldid=1088624)
have their own frozen identities. This independent problem, bridge
exposition, and solution: CC BY-SA 4.0. Model provenance:
OpenAI Codex gpt-5.6-sol, Ultra. The credits to Holger Brenner and
revision contributors, and the licences of source components, remain
in force; no human authorship or review, or endorsement by the source
author, is claimed.
