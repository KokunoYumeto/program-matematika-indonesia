---
title: "Lecture 1 - Parameter-Dependent Systems of Linear Equations and Vector Bundles"
stable_id: br-bgk-2019-l01
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 1"
upstream_pageid: 109003
upstream_revid: 1069568
upstream_timestamp: "2026-02-06T07:06:14Z"
upstream_mediawiki_sha1: 6e619f166a640629f33e73ac518faff6daff2810
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069568"
authority_manifest: authority/wikiversity-bgk/unit-01/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ad271f5ad69f9990dbe3082c22f8c52b7a4c58494c8f6614350078535d4f2ba1
lecture_xml: authority/wikiversity-bgk/unit-01/lecture-01.xml
lecture_xml_sha256: 68d7783afc1c1353c3298638f150095dad79c2424c356bc09bc50c023ab86392
lecture_expanded_tex: authority/wikiversity-bgk/unit-01/lecture-01-expanded.tex
lecture_expanded_tex_sha256: 7b22065d36d75d01385aabd97edd6e5416f817e1ebf96af9543023242135c77d
official_pdf: authority/artifacts/bgk-lecture-01-official.pdf
official_pdf_sha256: be4103eb7f4631f300c8f5f895de82094d0cd5ffac603eff9d5c7b77aef3d3ce
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. Official PDF and media retain their recorded component notices; no blanket relicensing claim is made."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 1: Parameter-Dependent Systems of Linear Equations and Vector Bundles {#br-bgk-2019-l01}

## Parameter-dependent systems of linear equations {#br-bgk-2019-l01-s01}

Consider the real linear equation

$$
7u-5v+2w=0.
$$

Its solution set

$$
L=\left\{(u,v,w)\in\mathbb R^3\mid 7u-5v+2w=0\right\}
\subset\mathbb R^3
$$

is a two-dimensional real vector subspace of $\mathbb R^3$. Solving such a linear equation means, among other things, finding a basis for $L$. In this case, for example,

$$
L=\left\langle
\begin{pmatrix}5\\7\\0\end{pmatrix},
\begin{pmatrix}2\\0\\-7\end{pmatrix}
\right\rangle.
$$

The methods of solution are largely independent of the particular coefficients of the linear equation, although we shall see below the limitations of this statement. If we replace specific numbers by coefficients depending functionally on parameters, we may ask how the solution space varies with those parameters. For example, consider the linear equation depending on a parameter $s$,

$$
7u-5v+(s^2-3s-10)w=0.
$$

For each $s$, the solution space $L_s$ depends on $s$, but remains a two-dimensional subspace,

$$
L_s\subset\mathbb R^3.
$$

In other words, the solution space is a plane moving through space as $s$ varies. We may ask for which values of $s$ the vector

$$
\begin{pmatrix}5\\-3\\8\end{pmatrix}
$$

is a solution, that is, belongs to $L_s$. We may also ask whether there are distinct parameters $s,t$ for which

$$
L_s=L_t
$$

as subspaces of $\mathbb R^3$; whether the solution space always has a basis of the form

$$
\left\langle
\begin{pmatrix}a\\b\\0\end{pmatrix},
\begin{pmatrix}c\\0\\d\end{pmatrix}
\right\rangle;
$$

or whether there is always a solution vector of the form

$$
\begin{pmatrix}1\\0\\e\end{pmatrix}.
$$

Recall that the algorithm for solving systems of linear equations, Gaussian elimination, branches when certain coefficients are $0$ or become $0$ during the algorithm. The equation

$$
7u-5v+0w=0
$$

has solution space

$$
\left\langle
\begin{pmatrix}5\\7\\0\end{pmatrix},
\begin{pmatrix}0\\0\\1\end{pmatrix}
\right\rangle
$$

and contains no vector of the form $\begin{pmatrix}1&0&e\end{pmatrix}^{\mathsf T}$. Since $s=-2$ and $s=5$ are the roots of the quadratic polynomial $s^2-3s-10$, at these two parameter values the parametrised equation above becomes

$$
7u-5v+0w=0.
$$

Thus, for these two values, $L_s$ contains no vector of the form $\begin{pmatrix}1&0&e\end{pmatrix}^{\mathsf T}$. For all other parameter values, the solution space contains the vector

$$
\begin{pmatrix}
1\\[2pt]0\\[2pt]-\dfrac{7}{s^2-3s-10}
\end{pmatrix}.
$$

A certain aspect of the solution space therefore itself depends functionally on the parameter.

It is natural to study the dependence of a linear equation or a system of linear equations on parameters in two stages. In the first stage, the coefficients of the equations themselves are treated as variables, or *universal parameters*, and we study how the solution spaces vary with them. In particular, we want to understand qualitative jumps in the behaviour of the solution spaces. In the second stage, we impose additional, more or less restrictive conditions on the universal parameters, or allow them to depend functionally on other parameters.

### Example 1.1: one equation in two variables {#br-bgk-2019-l01-exa-01}

Consider the general real linear equation

$$
su+tv=0
$$

in the variables $u,v$ and parameters $s,t$, which serve as indeterminate coefficients. We want to understand the solution space

$$
L_{(s,t)}=\left\{(u,v)\mid su+tv=0\right\}\subseteq\mathbb R^2
$$

as a function of the parameters $(s,t)$. An extreme case occurs at $(s,t)=(0,0)$: every $(u,v)$ satisfies the equation, so the solution space is the whole two-dimensional space $\mathbb R^2$. If $(s,t)\ne(0,0)$, the solution space is one-dimensional, and a basis vector for this solution line is

$$
\begin{pmatrix}t\\-s\end{pmatrix}.
$$

Thus, over the parameter space $\mathbb R^2\setminus\{(0,0)\}$, the solution space has the uniform description

$$
L_{(s,t)}=
\left\{c\begin{pmatrix}t\\-s\end{pmatrix}\mathrel{\Big|}c\in\mathbb R\right\}.
$$

A more compact interpretation is obtained by considering the total solution space

$$
L=\left\{(s,t,u,v)\mid su+tv=0\right\}\subseteq\mathbb R^4.
$$

Note that $L$ is not a linear subspace of $\mathbb R^4$. The solution space for a particular parameter value $(s,t)$ is obtained by intersecting $L$ with the affine plane $(s,t)\times\mathbb R^2$. Under the total projection

$$
L\longrightarrow\mathbb R^2\times\mathbb R^2
\stackrel{p_{s,t}}{\longrightarrow}\mathbb R^2,
\qquad (s,t,u,v)\longmapsto(s,t),
$$

$L_{(s,t)}$ is the fibre over $(s,t)$. The total solution space displays both the variation of the solution lines with the parameter and their degeneration into a solution plane over the origin. The behaviour away from the parameter origin is described by the restriction

$$
L'=L\setminus\bigl(\{(0,0)\}\times\mathbb R^2\bigr)
=p^{-1}\!\left(\mathbb R^2\setminus\{(0,0)\}\right)
\longrightarrow\mathbb R^2\setminus\{(0,0)\}.
$$

Each fibre of this restricted projection is a one-dimensional solution space. Moreover, there is a bijection

$$
\begin{aligned}
\left(\mathbb R^2\setminus\{(0,0)\}\right)\times\mathbb R
&\longrightarrow L',\\
(s,t;c)&\longmapsto(s,t,ct,-cs),
\end{aligned}
$$

which is linear for each parameter $(s,t)$. On the left is the direct product of the base space $\mathbb R^2\setminus\{(0,0)\}$ and the fibre $\mathbb R$, which is independent of the base point. On the right is a family of varying lines in $\mathbb R^2$, but the bijection translates one description into the other.

> **Editorial note - order of factors and base space.** In the definition of $L'$, the source prints $\mathbb R^2\times(0,0)$, whereas equality with $p^{-1}(\mathbb R^2\setminus\{(0,0)\})$ requires removing the fibre over the origin, namely $\{(0,0)\}\times\mathbb R^2$. The source prose subsequently prints $\mathbb R^2\times(0,0)$ again as the base space, whereas the domain of the immediately preceding bijection is $\mathbb R^2\setminus\{(0,0)\}$. This edition follows the two displayed maps and explicitly records the discrepancy.

### Example 1.2: one equation in three variables {#br-bgk-2019-l01-exa-02}

Consider the general real linear equation

$$
ru+sv+tw=0
$$

in the variables $u,v,w$ and parameters $r,s,t$, which serve as indeterminate coefficients. We want to understand the solution space

$$
L_{(r,s,t)}=
\left\{(u,v,w)\mid ru+sv+tw=0\right\}\subseteq\mathbb R^3
$$

as a function of the parameters $(r,s,t)$. At $(r,s,t)=(0,0,0)$, the solution space is the whole of $\mathbb R^3$. If $(r,s,t)\ne(0,0,0)$, it is two-dimensional. We exclude the origin from the parameter space and consider the total solution space

$$
\begin{aligned}
L={}&\left\{(r,s,t,u,v,w)\mathrel{\Big|}
ru+sv+tw=0, (r,s,t)\ne(0,0,0)\right\}\\
&\subseteq\left(\mathbb R^3\setminus\{(0,0,0)\}\right)\times\mathbb R^3,
\end{aligned}
$$

together with the projection $p$ to $\mathbb R^3\setminus\{(0,0,0)\}$. The fibre of $p$ over a particular parameter $(r,s,t)$ is the solution space $L_{(r,s,t)}$ of the equation determined by that parameter tuple.

> **Editorial note - notation for the origin and scope of the product.** In this inclusion the source prints $\mathbb R^3\setminus\{0,0,0\}\times\mathbb R^3$, without writing the origin as a tuple or using parentheses to separate the base space from the fibre factor. The projection in the next sentence uniquely determines the intended meaning. This edition writes $(\mathbb R^3\setminus\{(0,0,0)\})\times\mathbb R^3$.

Can we give a basis for each solution space that depends on the parameters in an explicit computational and algebraic way? Since we have removed the origin,

$$
\mathbb R^3\setminus\{(0,0,0)\}
=\{(r,s,t)\mid r\ne0\}\cup
\{(r,s,t)\mid s\ne0\}\cup
\{(r,s,t)\mid t\ne0\}.
$$

The base space can therefore be written as a union of three open sets. Over the open set $r\ne0$, for example, a basis is given by

$$
(s,-r,0)\quad\text{and}\quad(t,0,-r).
$$

The condition $r\ne0$ ensures that the two vectors are linearly independent. Indeed, the two vectors are well-defined solutions everywhere, but when $r=0$ they lose their linear independence and hence do not form a basis everywhere. In any case, the map

$$
\begin{aligned}
\{(r,s,t)\mid r\ne0\}\times\mathbb R^2
&\longrightarrow L|_{\{(r,s,t)\mid r\ne0\}},\\
(r,s,t;c,d)&\longmapsto\bigl(r,s,t;\,c(s,-r,0)+d(t,0,-r)\bigr)
\end{aligned}
$$

is a computationally simple bijection between the product of the base space with $\mathbb R^2$ and the solution space over $\{(r,s,t)\mid r\ne0\}$.

> **Editorial note - base coordinates.** The source writes only the fibre vector on the right-hand side of this map. Since its codomain is the total space $L$, the unchanged base coordinates $(r,s,t)$ are displayed here as well.

We now ask whether it is possible to give, globally on all of $\mathbb R^3\setminus\{(0,0,0)\}$, a basis of the solution space that varies with the base point. The question is whether there exist two functions $u(r,s,t)$ and $v(r,s,t)$ with values in $\mathbb R^3$ that always form a basis of the corresponding fibre, and in particular belong to it. With no further conditions on $u$ and $v$, this is possible by a case-by-case definition. However, it is no longer possible if both functions are required to be continuous. By continuity, the global functions $u$ and $v$ are already determined by their values on the dense open set

$$
U=\{(r,s,t)\mid r\ne0\}
\subseteq\mathbb R^3\setminus\{(0,0,0)\}.
$$

Using the basis over $U$ given above, we can write

$$
u=\alpha(r,s,t)\begin{pmatrix}s\\-r\\0\end{pmatrix}
+\beta(r,s,t)\begin{pmatrix}t\\0\\-r\end{pmatrix}
$$

and

$$
v=\gamma(r,s,t)\begin{pmatrix}s\\-r\\0\end{pmatrix}
+\delta(r,s,t)\begin{pmatrix}t\\0\\-r\end{pmatrix},
$$

where $\alpha,\beta,\gamma,\delta$ are continuous real-valued functions on $U$. We cannot expect these coefficient functions to be defined on all of $\mathbb R^3$, so the argument in the continuous case becomes more complicated. The result will follow from Theorem 2.3; see Remark 2.4.

For now, we therefore restrict attention to rational functions whose denominators may contain a power of $r$, that is, rational functions on $U$. Consider

$$
\begin{aligned}
u
&=\alpha\begin{pmatrix}s\\-r\\0\end{pmatrix}
+\beta\begin{pmatrix}t\\0\\-r\end{pmatrix}\\
&=\frac{P}{r^m}\begin{pmatrix}s\\-r\\0\end{pmatrix}
+\frac{Q}{r^n}\begin{pmatrix}t\\0\\-r\end{pmatrix},
\end{aligned}
$$

where $P,Q$ are polynomials and factors of $r$ have been cancelled wherever possible. Since $u$ as a whole is defined on all of $\mathbb R^3$, the exponent $m$, and likewise $n$, is at most $1$; otherwise $u$ would have a pole. For $m=n=1$, the first component gives a polynomial equation of the form

$$
rN+sP+tQ=0,
\qquad N,P,Q\in\mathbb R[r,s,t].
$$

In this case, the relevant idea being the Koszul resolution,

$$
(N,P,Q)=A(-s,r,0)+B(t,0,-r)+C(0,t,-s)
$$

for polynomials $A,B,C\in\mathbb R[r,s,t]$. Similarly, $v$ has a representation in terms of $(N',P',Q')$ and $(A',B',C')$. Write

$$
X=\mathbb R^3\setminus\{(0,0,0)\}
$$

and consider the map

$$
\begin{aligned}
\varphi:X\times\mathbb R^3&\longrightarrow L\subseteq X\times\mathbb R^3,\\
(r,s,t;a,b,c)&\longmapsto
(r,s,t;\,a(-s,r,0)+b(t,0,-r)+c(0,t,-s)).
\end{aligned}
$$

Under this map, the polynomial tuples $(-A,-B,-C)$ and $(-A',-B',-C')$, viewed as maps $X\to X\times\mathbb R^3$, are sent to $u$ and $v$. By assumption, $u$ and $v$ form a basis of every fibre of $L$, so $(A,B,C)$ and $(A',B',C')$ are linearly independent at every point. The tuple $(t,s,-r)$ is sent by $\varphi$ to $0$ in every fibre. Therefore,

$$
(A,B,C),\qquad(A',B',C'),\qquad(t,s,-r)
$$

form a basis of $\mathbb R^3$ at every point: $(t,s,-r)$ cannot be a linear combination of the first two tuples, since applying $\varphi$ would then give a nontrivial relation between $u$ and $v$. However, the determinant of the matrix

$$
\begin{pmatrix}
A&B&C\\
A'&B'&C'\\
t&s&-r
\end{pmatrix}
$$

is a polynomial combination of the variables $r,s,t$, and so is not a unit in the polynomial ring. In the real case, we cannot yet conclude that this determinant has a real zero in $X$; for example, it might have the form $r^2+s^2+t^2$. However, if we replace $\mathbb R$ by $\mathbb C$, the algebraic argument is unchanged, and we can conclude that the determinant has a zero in

$$
X_{\mathbb C}=\mathbb C^3\setminus\{(0,0,0)\}.
$$

Thus such a global basis cannot exist at every point.

> **Editorial note - sign of the lifted tuples.** The source says that $(A,B,C)$ and $(A',B',C')$ map to $u$ and $v$. With its displayed convention $rN+sP+tQ=0$, however, $u=-(N,P,Q)$, and similarly for $v$. Negating the two coefficient tuples gives the stated lifts. The linear-independence and determinant argument is unchanged.

### Example 1.3: two equations in three variables {#br-bgk-2019-l01-exa-03}

Consider the general real system of linear equations

$$
au+bv+cw=0
$$

and

$$
du+ev+fw=0
$$

in the variables $u,v,w$ and parameters $a,b,c,d,e,f$, which serve as indeterminate coefficients of the system. If the parameters are sufficiently general, or more precisely, if there is no linear relation between the two equations, then the solution space

$$
L_{(a,b,c,d,e,f)}=
\left\{(u,v,w)\mathrel{\Big|}
au+bv+cw=0\ \text{and}\ du+ev+fw=0\right\}
\subseteq\mathbb R^3
$$

is a line. Under this condition, the parameters therefore determine a family of varying lines in $\mathbb R^3$. The relevant parameter space for this family of lines is

$$
P=\left\{(a,b,c,d,e,f)\mathrel{\Big|}
(a,b,c)\ \text{and}\ (d,e,f)\ \text{linearly independent}\right\}.
$$

Altogether, we obtain the total solution space

$$
\begin{aligned}
L=\{&(a,b,c,d,e,f,u,v,w)\mid
au+bv+cw=0\ \text{and}\ du+ev+fw=0\}\\
&\subseteq P\times\mathbb R^3,
\end{aligned}
$$

together with its projection to $P$.

Can this line, or a basis element of it, be specified globally as a function of the parameters? Viewing the two equations as orthogonality relations, we seek a nonzero vector perpendicular to both constraint vectors

$$
\begin{pmatrix}a\\b\\c\end{pmatrix}
\quad\text{and}\quad
\begin{pmatrix}d\\e\\f\end{pmatrix}.
$$

Their cross product has this property, namely

$$
\begin{pmatrix}
bf-ce\\
-af+cd\\
ae-bd
\end{pmatrix}.
$$

For the properties of the cross product used here, the source refers to Lemma 33.3 in *Lineare Algebra (Osnabrück 2024-2025)*.

Thus there is a bijection

$$
\begin{aligned}
P\times\mathbb R&\longrightarrow L,\\
(a,b,c,d,e,f;s)&\longmapsto
(a,b,c,d,e,f;s(bf-ce),s(-af+cd),s(ae-bd)).
\end{aligned}
$$

> **Editorial note - two coordinate names in the source.** The source displays the second constraint vector as $(e,f,g)$, although the system and parameter space define it as $(d,e,f)$. In the final map, the source also prints the middle component as $-af+ce$, whereas the cross product printed immediately before it gives $-af+cd$. This edition uses $(d,e,f)$ and $-af+cd$, which can be verified directly from the two equations, while recording both source typographical errors.

In Examples 1.1 and 1.3 there are *global polynomial trivialisations*: polynomial functions translate the complicated geometric object into the simple object $P\times\mathbb R$, where $P$ is the base space. By contrast, such a global trivialisation is impossible in Example 1.2, although local trivialisations exist over the three specified open sets. Geometric objects of this kind are called vector bundles.

## Real vector bundles {#br-bgk-2019-l01-s02}

### Definition 1.4: real vector bundle {#br-bgk-2019-l01-def-01}

Let $X$ be a topological space and $r\in\mathbb N$. A *real vector bundle of rank $r$* is a topological space $V$ together with a continuous map

$$
p:V\longrightarrow X
$$

such that every fibre $p^{-1}(x)$ is an $r$-dimensional real vector space, and there is an open cover

$$
X=\bigcup_{i\in I}U_i
$$

together with homeomorphisms over $U_i$,

$$
\varphi_i:p^{-1}(U_i)\longrightarrow U_i\times\mathbb R^r,
$$

which induce a linear isomorphism on each fibre,

$$
(\varphi_i)_x:p^{-1}(x)\longrightarrow\mathbb R^r.
$$

The space $V$ is also called the *total space*, and $X$ the *base space* of the vector bundle. The fibre over $x$ is often denoted by

$$
V_x=p^{-1}(x).
$$

In the examples above, $X$ is the relevant parameter space, namely the locus of parameters for which the solution spaces have minimal dimension. This dimension is the rank $r$ in the definition above: respectively, $1,2,1$. In the first and third examples, the open cover consists only of the base space itself; these two bundles have a global trivialisation. In the second example, there is a cover by three open sets over which trivialisations have been given.

In the homeomorphism

$$
p^{-1}(U)\longrightarrow U\times\mathbb R^r,
$$

the right-hand side carries the product topology, $\mathbb R^r$ its natural Euclidean topology, and $p^{-1}(U)$ the topology induced from $V$. Thus every fibre $V_x$ carries the natural topology of a finite-dimensional real vector space. A homeomorphism *over $U$* means that the diagram

$$
\begin{array}{ccc}
p^{-1}(U)&\stackrel{\varphi}{\longrightarrow}&U\times\mathbb R^r\\
&\searrow p&\downarrow\operatorname{pr}_1\\
&&U
\end{array}
$$

commutes.

> **Editorial note - rank symbol in the diagram.** The source diagram prints $U\times\mathbb R^n$, whereas the definition and all surrounding formulae specify the rank as $r$. This edition displays $\mathbb R^r$.

The product $X\times\mathbb R^r$ is a vector bundle called the *trivial vector bundle*.

### Lemma 1.5: restriction of a vector bundle {#br-bgk-2019-l01-lem-01}

Let

$$
p:V\longrightarrow X
$$

be a real vector bundle over a topological space $X$. For every open set $W\subseteq X$, the restriction

$$
p^{-1}(W)\longrightarrow W
$$

is also a vector bundle.

#### Proof {#br-bgk-2019-l01-lem-01-proof}

Simply restrict the fibrewise linear homeomorphisms

$$
\varphi_i:p^{-1}(U_i)\longrightarrow U_i\times\mathbb R^r
$$

to

$$
\varphi_i|_{W\cap U_i}:
p^{-1}(W\cap U_i)\longrightarrow(W\cap U_i)\times\mathbb R^r.
$$

$\square$

The restriction of a vector bundle to each $U_i$ is trivial. Thus every vector bundle is locally trivial.

### Definition 1.6: homomorphism of vector bundles {#br-bgk-2019-l01-def-02}

Let $E$ and $F$ be real vector bundles over a topological space $X$. A *homomorphism of vector bundles*

$$
\varphi:E\longrightarrow F
$$

is a continuous map over $X$ such that, for every $x\in X$, the induced map

$$
\varphi_x:E_x\longrightarrow F_x
$$

is $\mathbb R$-linear.

### Definition 1.7: isomorphism of vector bundles {#br-bgk-2019-l01-def-03}

Let $E$ and $F$ be real vector bundles over a topological space $X$. A homomorphism of vector bundles

$$
\varphi:E\longrightarrow F
$$

is called an *isomorphism* if there is a homomorphism

$$
\psi:F\longrightarrow E
$$

whose composition with $\varphi$, in either order, is the identity map.

## The tangent bundle of a manifold {#br-bgk-2019-l01-s03}

We now discuss another particularly important vector bundle, present on every manifold: the tangent bundle.

Every point $P\in M$ of a manifold has a tangent space $T_PM$. The tangent space is an $n$-dimensional vector space, where $n$ is the dimension of the manifold. Its elements are tangent vectors, or “infinitesimal directions” at that point. Initially, tangent directions at two distinct points have nothing to do with one another: their definitions depend only on arbitrarily small open neighbourhoods of the respective points, and the Hausdorff property allows these neighbourhoods to be chosen disjoint.

The picture for an open set $V\subseteq\mathbb R^n$ is quite different. For every $Q\in V$, the tangent space $T_QV$ can be identified naturally with the ambient vector space $\mathbb R^n$. A vector $v\in\mathbb R^n$ is assigned the tangent vector determined by the linear curve $t\mapsto Q+tv$. Since this identification applies at every point, there is a direct parallelism between the tangent spaces for

$$
Q\in V\subseteq\mathbb R^n.
$$

A manifold is covered by open sets diffeomorphic to open subsets of Euclidean space. It is therefore natural to expect that its various tangent spaces are not completely isolated. The concept of the tangent bundle brings all the tangent spaces together and reflects their local interconnection.

> **Source illustration - `Tangent_bundle.svg`.** Two visualisations of the tangent bundle of a circle. In the upper picture, the tangent space at each point $P$ of the circle is placed tangentially to the circle and realised as a one-dimensional affine subspace of $\mathbb R^2$. This embedding creates intersections that do not exist in the tangent bundle itself, since the base point $P$ must also be taken into account. In the lower picture, the tangent spaces are arranged in parallel over the points of the circle, producing a cylinder.

![Diagram of the tangent bundle, with tangent spaces as fibres over the points of a manifold](authority/assets/bgk-tangent-bundle-500.png)

### Definition 1.8: the tangent bundle as a disjoint union {#br-bgk-2019-l01-def-04}

Let $M$ be a differentiable manifold. The set

$$
TM=\biguplus_{P\in M}T_PM,
$$

together with the projection map

$$
\begin{aligned}
\pi:TM&\longrightarrow M,\\
(P,v)&\longmapsto P,
\end{aligned}
$$

is called the *tangent bundle* of $M$.

A point $u\in TM$ always has a base point $P\in M$ and is an element of the tangent space $T_PM$. It is usually written $(P,v)$ with $P\in M$ and $v\in T_PM$. For an open set $V\subseteq\mathbb R^n$,

$$
TV=V\times\mathbb R^n,
$$

so it is a product space. This does not hold for an arbitrary manifold. Initially, the tangent bundle merely takes the disjoint union of the various tangent spaces, without identifying different tangent spaces with one another. However, the topology we shall shortly put on the tangent bundle adds a “neighbourhood structure” between the tangent spaces.

### Definition 1.9: tangent map {#br-bgk-2019-l01-def-05}

Let $M$ and $N$ be differentiable manifolds and

$$
\varphi:M\longrightarrow N
$$

a differentiable map. Let $TM$ and $TN$ be the corresponding tangent bundles. The *tangent map*

$$
T(\varphi):TM\longrightarrow TN
$$

is the disjoint union of the tangent maps at the individual points, namely

$$
T(\varphi)=\biguplus_{P\in M}T_P(\varphi).
$$

### Example 1.10: local trivialisation from a chart {#br-bgk-2019-l01-exa-04}

Let $M$ be a differentiable manifold and

$$
\alpha:U\longrightarrow V
$$

a chart, where $V\subseteq\mathbb R^n$ is open. The chart induces a natural bijection

$$
\begin{aligned}
T(\alpha^{-1}):TV=V\times\mathbb R^n&\longrightarrow TU,\\
(Q,v)&\longmapsto
\left(\alpha^{-1}(Q),[s\mapsto\alpha^{-1}(Q+sv)]\right).
\end{aligned}
$$

Here $s$ ranges over a real interval $I$ chosen so that $Q+sv\in V$ (compare Lemma 77.5 in *Analysis (Osnabrück 2014-2016)*). Since $V\times\mathbb R^n$ is a product of topological spaces,

$$
TV=V\times\mathbb R^n
$$

is itself a topological space. It is natural to transfer this topology to $TU$, and then construct a topology on the whole tangent bundle $TM$.

### Definition 1.11: topology of the tangent bundle {#br-bgk-2019-l01-def-06}

Let $M$ be a differentiable manifold of dimension $n$ and

$$
TM=\biguplus_{P\in M}T_PM
$$

its tangent bundle, with projection

$$
\begin{aligned}
\pi:TM&\longrightarrow M,\\
(P,v)&\longmapsto P.
\end{aligned}
$$

Equip the tangent bundle with the following topology: a subset $W\subseteq TM$ is open if and only if, for every chart

$$
\alpha:U\longrightarrow V,
$$

the set

$$
T(\alpha)\left(W\cap\pi^{-1}(U)\right)
$$

is open in $V\times\mathbb R^n$.

In particular, for every open set $U\subseteq M$, the inverse image

$$
\pi^{-1}(U)=TU\subseteq TM
$$

is open; in other words, the projection $\pi$ is continuous. With these conventions, the tangent bundle of a differentiable manifold is a real vector bundle. If

$$
M=\bigcup_{i\in I}U_i
$$

is an open cover by sets $U_i$ homeomorphic to open sets $V_i\subseteq\mathbb R^n$, then the charts

$$
\alpha_i:U_i\longrightarrow V_i
$$

directly provide trivialisations

$$
TM|_{U_i}=TU_i
\stackrel{T(\alpha_i)}{\longrightarrow}
TV_i=V_i\times\mathbb R^n.
$$

A remarkable number of properties of a manifold are reflected in properties of its tangent bundle. The tangent bundle may be trivial even when $M$ is not homeomorphic to an open subset of $\mathbb R^n$.
