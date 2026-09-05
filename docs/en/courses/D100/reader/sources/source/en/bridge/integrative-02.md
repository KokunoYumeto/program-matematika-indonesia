---
title: "Integrative Problem 2: Affine Gluing and Compatibility"
stable_id: d100-bridge-integrative-02
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author_referenced: "Holger Brenner"
source_course_referenced: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_revision_urls:
  - "https://de.wikiversity.org/w/index.php?oldid=793634"
  - "https://de.wikiversity.org/w/index.php?oldid=1003733"
---

# Integrative problem 2: affine gluing and compatibility {#d100-bridge-integrative-02}

This synthesis problem and its solution were independently written; they are
not a problem or solution from Holger Brenner's source material. The aim is
to glue not only points but also structure sheaves, and to discover why
pairwise conditions alone are insufficient for three charts.

## Problem {#d100-bridge-integrative-02-soal}

Let $k$ be any field. Take

$$
U=\operatorname{Spec}(k[u,u^{-1}]),\qquad
V=\operatorname{Spec}(k[v,v^{-1}]),
$$

and the open subsets $W_U=D(1-u)\subset U$ and $W_V=D(1-v)\subset V$.
All morphisms below are morphisms of schemes over $k$.

1. Check that the homomorphism
   $\theta:k[v,v^{-1},(1-v)^{-1}]\to
   k[u,u^{-1},(1-u)^{-1}]$, $v\mapsto1-u$, gives an isomorphism
   $\varphi:W_U\to W_V$. Write down its inverse, including the images of
   the denominators.
2. Construct the glued space $X$ and its structure sheaf. Prove that
   $X\cong\mathbb A^1_k$, not merely as a set of points. Locate the points
   $t=0$ and $t=1$ in the two charts.
3. Compute $\Gamma(X,\mathcal O_X)$ from compatible pairs of sections.
   Which global section is given by $u$ on $U$ and $1-v$ on $V$?
   Why is the pair formally written as $1/u$ and $1/(1-v)$ not a pair of
   sections on the entirety of the two charts?
4. State the domain, inverse, and cocycle conditions for gluing three or
   more scheme charts. Explain the order of composition of the ring
   homomorphisms.
5. For three copies of $\mathbb A^1_k$ with coordinates $t_1,t_2,t_3$,
   take every proposed overlap to be the whole chart, and specify the
   transitions by $t_2=t_1$, $t_3=t_2+1$, and $t_3=t_1$.
   Pair each transition with its inverse. Prove that these data still
   cannot be realised as open charts with these transitions on one scheme.

## Complete solution {#d100-bridge-integrative-02-jawaban}

### 1. The isomorphism on the overlap {#d100-bridge-integrative-02-a}

For a commutative ring $R$, the principal open subset $D(f)$ is an affine
scheme with section ring $R_f$; see
[Lemma 9.12](bgk-reader.html#br-bgk-2019-l09-lem-03) and
[Lemma 9.13](bgk-reader.html#br-bgk-2019-l09-lem-04). Thus the rings of
the two overlaps are exactly those written in the problem.

In the target ring of $\theta$, both $1-u$ and $u$ are units. The
substitution $v\mapsto1-u$ therefore extends uniquely by

$$
v^{-1}\longmapsto(1-u)^{-1},\qquad
(1-v)^{-1}\longmapsto u^{-1}.
$$

Its inverse sends $u\mapsto1-v$, $u^{-1}\mapsto(1-v)^{-1}$, and
$(1-u)^{-1}\mapsto v^{-1}$. Both composites fix every generator. By
[Corollary 10.10](bgk-reader.html#br-bgk-2019-l10-cor-01), this ring
isomorphism gives an isomorphism of schemes $\varphi:W_U\to W_V$.
On points valued in a field extension, the transition reads $v=1-u$.
The section homomorphism $\varphi^\#$ runs from the ring of chart $V$
to the ring of chart $U$, not the other way round.

### 2. The glued space and sheaf {#d100-bridge-integrative-02-b}

As a topological space, take the disjoint union $U\amalg V$ and identify
$p\in W_U$ with $\varphi(p)\in W_V$. The quotient topology makes both
charts open subsets. Indeed, for an open subset $G\subset U$, its
saturation in the disjoint union is $G\amalg\varphi(G\cap W_U)$, which
is open because $\varphi$ is a homeomorphism between open subsets.
No two distinct points within chart $U$ are identified, and the same
holds for $V$.

For an open subset $O\subset X$, write $O_U$ and $O_V$ for its inverse
images in the two charts. Define

$$
\mathcal O_X(O)=
\left\{(a,b)\in\mathcal O_U(O_U)\times\mathcal O_V(O_V):
a|_{O_U\cap W_U}
=\varphi^\#\bigl(b|_{O_V\cap W_V}\bigr)\right\}.
$$

Restriction is performed componentwise. This is indeed a sheaf: compatible
local sections glue uniquely on each chart by the sheaf properties of
$\mathcal O_U$ and $\mathcal O_V$; equality on the overlap can be checked
locally and therefore remains valid after gluing. The restriction of this
sheaf to $U$ is isomorphic to $\mathcal O_U$: a section on chart $U$
uniquely determines a section on the part of chart $V$ identified with it
through $\varphi$. The same argument applies to $V$. Every point
therefore has an affine neighbourhood with the correct structure sheaf.
By [Definition 10.1](bgk-reader.html#br-bgk-2019-l10-def-01), $X$ is a scheme.

Now take the affine line with coordinate $t$. The homomorphisms

$$
k[t]\longrightarrow k[u,u^{-1}],\quad t\longmapsto u,
\qquad
k[t]\longrightarrow k[v,v^{-1}],\quad t\longmapsto1-v
$$

give isomorphisms $U\cong D(t)$ and $V\cong D(1-t)$. On the overlap,
the two formulas agree because $u=1-v$. The sets $D(t)$ and $D(1-t)$
cover $\operatorname{Spec}(k[t])$: a prime ideal cannot contain both $t$
and $1-t$, since their sum is $1$. Their intersection is $D(t(1-t))$,
exactly the image of $W_U$ and $W_V$.

Thus the map $X\to\mathbb A^1_k$ is a bijection whose restriction to
each chart is a homeomorphism onto an open subset. It is a homeomorphism,
and its sheaf homomorphism is an isomorphism on both charts. Sheaf
isomorphisms can be checked on an open cover, so this map is an
isomorphism of schemes.

The point $t=0$ is not in $U=D(t)$; it appears in $V$ as the ideal
$(v-1)$. The point $t=1$ appears in $U$ as $(u-1)$ and is not in
$V=D(1-t)$. These two points are not glued to one another.

### 3. The global section ring as matching pairs {#d100-bridge-integrative-02-c}

Use the coordinate $t=u=1-v$ on the overlap. The rings of the two charts
can be regarded as subrings of the fraction field $k(t)$:

$$
\Gamma(U,\mathcal O_U)=k[t,t^{-1}],\qquad
\Gamma(V,\mathcal O_V)=k[t,(1-t)^{-1}].
$$

Since all maps to the overlap ring are injective, the matching-pair
condition amounts to taking the intersection of these two subrings.
Suppose an element of the intersection can be written as

$$
\frac{a(t)}{t^m}=\frac{b(t)}{(1-t)^n},\qquad m,n\geq0.
$$

Then $(1-t)^na(t)=t^mb(t)$. The polynomials $t^m$ and $(1-t)^n$ are
coprime in the principal ideal domain $k[t]$, so $t^m$ divides $a(t)$.
The first fraction is a polynomial. Conversely, every polynomial belongs
to both rings. Therefore

$$
\Gamma(X,\mathcal O_X)
=k[t,t^{-1}]\cap k[t,(1-t)^{-1}]
=k[t].
$$

The pair $(u,1-v)$ gives the global polynomial $t$. On the other hand,
$1/u$ is indeed a section on $U$, but $1/(1-v)$ does not belong to
$k[v,v^{-1}]$. To prove this, suppose $1/(1-v)=p(v)/v^N$. Then
$v^N=(1-v)p(v)$, which, after substituting $v=1$, gives $1=0$. Thus this
formula is not regular at $v=1$, the point $t=0$. Formal agreement on an
overlap alone does not turn a rational function into a section on a whole
chart.

### 4. Gluing and cocycle conditions {#d100-bridge-integrative-02-d}

For a family of schemes $U_i$, choose open subsets $U_{ij}\subseteq U_i$
and scheme isomorphisms $\varphi_{ij}:U_{ij}\to U_{ji}$. The complete
conditions we use are:

1. $U_{ii}=U_i$ and $\varphi_{ii}=\operatorname{id}_{U_i}$.
2. $\varphi_{ji}=\varphi_{ij}^{-1}$.
3. For every $i,j,k$,
   $\varphi_{ij}(U_{ij}\cap U_{ik})=U_{ji}\cap U_{jk}$,
   and on the domain $U_{ij}\cap U_{ik}$ we have
   $\varphi_{jk}\circ\varphi_{ij}=\varphi_{ik}$.

The first part of condition 3 ensures that the composite has the correct
domain. The second is the cocycle condition: changing charts through $j$
or directly to $k$ gives the same identification, including on the
structure sheaves.

These conditions make the relation $p\sim\varphi_{ij}(p)$ reflexive,
symmetric, and transitive. In particular, no further identifications
arise that merge distinct points in the same chart. As in part 2,
isomorphisms between open subsets make the map from each chart to the
quotient space an open immersion. The glued sheaf is obtained from
families of matching sections; the sheaf property and local affine
structure are checked on each chart. This explains why the data produce
a scheme, without requiring the resulting scheme to be affine or separated.

If the overlaps used are affine, write $\lambda_{ij}=\varphi_{ij}^{\#}$
for the ring homomorphism running from chart $j$ to chart $i$. After all
sections have been restricted to the same triple overlap, the cocycle
condition reads

$$
\lambda_{ij}\circ\lambda_{jk}=\lambda_{ik}.
$$

This order is the reverse of that of the space maps
$\varphi_{jk}\circ\varphi_{ij}$. When a triple overlap is not affine,
the underlying equality is still an equality of sheaf morphisms there;
do not replace it with an unjustified statement about a single global
coordinate ring.

### 5. Inverse pairs are not enough {#d100-bridge-integrative-02-e}

In the three-chart example, the route $1\to2\to3$ gives

$$
t_3=t_2+1=t_1+1,
$$

whereas the direct route $1\to3$ gives $t_3=t_1$. These morphisms differ:
they send the rational point $t_1=0$ to $t_3=1$ and $t_3=0$, respectively.
This holds over every field because $0\ne1$.

Suppose there were chart immersions $j_i:U_i\to X$ realising these
transitions. The transitions $1\to2$ and $2\to3$ would give
$j_1(0)=j_2(0)=j_3(1)$, while the transition $1\to3$ would give
$j_1(0)=j_3(0)$. Thus $j_3(0)=j_3(1)$, contradicting the injectivity of
the open immersion $j_3$. Adding all inverse transitions does not repair
this failure. One can still form a quotient space by the generated
equivalence relation, but the chart maps to that space are not the
required immersions.

## Quick checks and pitfalls {#d100-bridge-integrative-02-check}

- Check denominators: $v\mapsto1-u$ must send every element being
  inverted to a unit.
- Check cocycle domains before writing a composition equation.
- Gluing schemes requires isomorphisms of structure sheaves, not merely
  bijections of points or agreement of rational functions on part of a region.
- The result in part 2 is affine because these charts reconstruct a cover
  of $\mathbb A^1_k$, not because every gluing of affine charts produces
  an affine scheme.

## Material provenance and licence {#d100-bridge-integrative-02-provenance}

Prerequisites are referenced from Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634)
and [Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733).
The contributor to the frozen revisions is recorded as Bocardodarapti.
The example of the cover $D(t),D(1-t)$, the synthesis questions, the
cocycle counterexample, and the solution here are independent editorial
material, not a renamed public source solution.
Production: OpenAI Codex gpt-5.6-sol, Ultra.
The new material is licensed under CC BY-SA 4.0, with the credits and
licences of source components preserved. No human authorship or review
is claimed, and no endorsement by the source author or institution is implied.
