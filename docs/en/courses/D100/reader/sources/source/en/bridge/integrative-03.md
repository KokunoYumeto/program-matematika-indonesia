---
title: "Integrative Problem 3: The Projective Line from Two Affine Charts"
stable_id: d100-bridge-integrative-03
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
  - "https://de.wikiversity.org/w/index.php?oldid=1003742"
---

# Integrative problem 3: the projective line from two affine charts {#d100-bridge-integrative-03}

This problem brings together gluing, the $\operatorname{Proj}$ construction,
local rings, and morphisms to affine schemes. The questions and their
solutions were independently written. The example of the projective line
constructed by gluing does already occur in Holger Brenner's course;
that source example is not claimed as a new discovery or answer.

## Problem {#d100-bridge-integrative-03-soal}

Let $k$ be any field. Take two charts

$$
U_0=\operatorname{Spec}(k[t]),\qquad
U_\infty=\operatorname{Spec}(k[s]).
$$

Glue $D(t)\subset U_0$ to $D(s)\subset U_\infty$ by the isomorphism
whose section homomorphism is

$$
\theta:k[s,s^{-1}]\longrightarrow k[t,t^{-1}],\qquad s\longmapsto t^{-1}.
$$

Call the result $P$.

1. Check the gluing data and prove that
   $P\cong\operatorname{Proj}(k[X_0,X_1])=\mathbb P^1_k$, with the
   standard grading $\deg X_0=\deg X_1=1$.
2. Identify the points $0$ and $\infty$, compute the stalk and residue
   field at each, and explain how the generic points of the two charts
   become a single generic point of $P$.
3. Compute the global section ring as compatible pairs of polynomials.
   Is either rational function $t$ or $t^{-1}$ a global section?
4. Prove that $P$ is not affine without using a theorem about properness
   or cohomology.
5. Determine all morphisms of schemes over $k$ from $P$ to
   $\mathbb A^1_k$. Explain concretely why two local formulas that look
   like coordinates do not automatically give a global morphism to the
   affine line.

## Complete solution {#d100-bridge-integrative-03-jawaban}

### 1. The transition and identification with Proj {#d100-bridge-integrative-03-a}

The homomorphism $\theta$ is well defined because $t^{-1}$ is a unit in
the Laurent ring. Its inverse sends $t\mapsto s^{-1}$. We therefore have
an isomorphism of schemes between the two open subsets. There are only
two charts; with the identity on each chart and the inverse transition,
the cocycle conditions involving repeated indices hold. The structure
sheaves are glued using pairs of sections that agree on the overlap,
as explained in integrative problem 2.

Write $R=k[X_0,X_1]$ with its standard grading. Its irrelevant ideal is
$R_+=(X_0,X_1)$. A point of $\operatorname{Proj}(R)$ is a homogeneous
prime ideal not containing $R_+$. At least one of $X_0,X_1$ therefore
lies outside that prime ideal, so

$$
\operatorname{Proj}(R)=D_+(X_0)\cup D_+(X_1).
$$

[Lemma 12.9](bgk-reader.html#br-bgk-2019-l12-lem-03) states that for a
commutative graded ring and a homogeneous element $f$ of nonzero degree,
$D_+(f)$ is the affine scheme $\operatorname{Spec}((R_f)_0)$. Here $X_0$
and $X_1$ satisfy those hypotheses. Every degree-zero monomial in
$R_{X_0}$ has the form $X_1^j/X_0^j$ for $j\geq0$, so

$$
(R_{X_0})_0=k[X_1/X_0]=k[t].
$$

Similarly, $(R_{X_1})_0=k[X_0/X_1]=k[s]$. On the overlap, the two
coordinates are reciprocal:

$$
t=X_1/X_0,\qquad s=X_0/X_1,\qquad st=1,
\qquad (R_{X_0X_1})_0=k[t,t^{-1}].
$$

Thus the charts and transition isomorphism on $\operatorname{Proj}(R)$
are exactly the gluing data defining $P$. The isomorphisms from the two
charts agree on the overlap and glue to an isomorphism of locally ringed
spaces. Their local inverses also agree, so the result is an isomorphism
of schemes $P\cong\mathbb P^1_k$.

### 2. Two special points and the generic point {#d100-bridge-integrative-03-b}

On rational points, chart $U_0$ sends $t=a$ to $[1:a]$. Chart $U_\infty$
sends $s=b$ to $[b:1]$. Hence

$$
0=[1:0],\qquad \infty=[0:1].
$$

The point $0$ is the ideal $(t)$ in $U_0$ and does not lie in the
overlap $D(t)$. The point $\infty$ is the ideal $(s)$ in $U_\infty$
and does not lie in the overlap $D(s)$. Thus these are distinct points.
The notation $[a:b]$ with $a,b\in k$ describes points rational over $k$,
not all points of the projective spectrum when $k$ is not algebraically
closed.

Taking a stalk is unchanged by restricting the space to an open
neighbourhood containing the point. By
[Lemma 9.10](bgk-reader.html#br-bgk-2019-l09-lem-02),

$$
\mathcal O_{P,0}=k[t]_{(t)},\qquad
\mathcal O_{P,\infty}=k[s]_{(s)},\qquad
\kappa(0)=k=\kappa(\infty).
$$

For instance, elements of $k[s]_{(s)}$ are fractions $f(s)/g(s)$ with
$g(0)\ne0$, and its residue field is obtained by evaluation at $s=0$.
This is different from replacing the whole stalk by $k$.

The zero ideal of $k[t]$ lies in $D(t)$, and the zero ideal of $k[s]$
lies in $D(s)$. The Laurent isomorphism identifies them. Call the
resulting point $\eta$. Its closure contains all of $U_0$ because $(0)$
is generic in the spectrum of the domain $k[t]$; its closure also
contains all of $U_\infty$. Hence $\overline{\{\eta\}}=P$. Its stalk is

$$
\mathcal O_{P,\eta}=k(t)=k(s),\qquad s=t^{-1}.
$$

This field is the function field of $P$ and also the residue field at
$\eta$. The identification comes from the transition, not from choosing
two different generic points on the same scheme.

### 3. Global sections and rational functions {#d100-bridge-integrative-03-c}

The sheaf property identifies global sections with pairs

$$
\Gamma(P,\mathcal O_P)
\cong\{(f(t),g(s))\in k[t]\times k[s]:
f(t)=g(t^{-1})\text{ in }k[t,t^{-1}]\}.
$$

If $f(t)=\sum_{i\geq0}a_it^i$ and
$g(t^{-1})=\sum_{j\geq0}b_jt^{-j}$, uniqueness of Laurent polynomial
coefficients forces $a_i=0$ for $i>0$, $b_j=0$ for $j>0$, and $a_0=b_0$.
This uniqueness follows by multiplying the equation by a sufficiently
large power of $t$ and using uniqueness of ordinary polynomial
coefficients. Thus

$$
\Gamma(P,\mathcal O_P)\cong k,
\qquad a\longleftrightarrow(a,a).
$$

The rational function $t$ is regular on $U_0$, but becomes $s^{-1}$ on
the other chart. It does not belong to $k[s]_{(s)}$: if
$s^{-1}=f(s)/g(s)$ with $g(0)\ne0$, then $g(s)=sf(s)$, which implies
$g(0)=0$, a contradiction. Thus $t$ has a pole at $\infty$ and is not
a global section. Interchanging the charts shows that $t^{-1}=s$ has
a pole at $0$ and is likewise not a global section.

It is important that this computation uses the **structure sheaf**, not
all rational functions $k(t)$. The function field is not the global
section ring.

### 4. The glued scheme is not affine {#d100-bridge-integrative-03-d}

Suppose $P\cong\operatorname{Spec}(A)$ for a commutative ring $A$.
For an affine scheme, [Lemma 9.12](bgk-reader.html#br-bgk-2019-l09-lem-03)
gives $A\cong\Gamma(P,\mathcal O_P)\cong k$. Since $k$ is a field,
$\operatorname{Spec}(k)$ has exactly one point, the zero ideal. Yet $P$
has at least two distinct points, $0$ and $\infty$. This contradiction
shows that $P$ is not affine.

Thus having a cover by affine schemes is much weaker than being affine.
What fails if we try to reconstruct $P$ solely from its global sections
is that the chart and sheaf gluing information is lost.

### 5. Morphisms to the affine line {#d100-bridge-integrative-03-e}

[Theorem 10.9](bgk-reader.html#br-bgk-2019-l10-thm-01) applies to a
locally ringed space $Z$ and an affine target $\operatorname{Spec}(R)$:
a homomorphism $R\to\Gamma(Z,\mathcal O_Z)$ determines exactly one
morphism of locally ringed spaces. We apply it to the scheme $Z=P$
and $R=k[T]$.

Since the required morphisms are **over $k$**, the ring homomorphism
must be a $k$-algebra homomorphism

$$
k[T]\longrightarrow\Gamma(P,\mathcal O_P)=k.
$$

Every such homomorphism is determined by one element $a\in k$, the
image of $T$, and conversely substitution $T\mapsto a$ always gives
one. The corresponding morphism is the composite

$$
P\longrightarrow\operatorname{Spec}(k)
\longrightarrow\mathbb A^1_k,
$$

where the second arrow is the rational point $(T-a)$. Thus all morphisms
$P\to\mathbb A^1_k$ over $k$ are these constant morphisms.

Locally, one might wish to send $T$ to $t$ on $U_0$. To agree on the
overlap, the image of $T$ on $U_\infty$ would have to be $s^{-1}$.
But $s^{-1}$ is not a section on the whole of $U_\infty$, as proved in
part 3. If one instead chooses $T\mapsto s$, the two sections are
defined on their respective charts but do not agree on the overlap:
$t$ differs from $t^{-1}$ as an element of $k[t,t^{-1}]$. Satisfying
only one of local regularity and agreement on the overlap is not enough.

## Quick checks and pitfalls {#d100-bridge-integrative-03-check}

- The transition relation is $st=1$, not $s=t$. Changing it changes
  the gluing data.
- $\Gamma(P,\mathcal O_P)=k$ does not say that every stalk is $k$, or
  that $P$ has only one point.
- Over an arbitrary field, do not identify all closed points with
  points valued in $k$.
- In the conclusion about constant morphisms, the condition “over $k$”
  explains why the homomorphism on constants is the identity.

## Material provenance and licence {#d100-bridge-integrative-03-provenance}

References: Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634),
[Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733),
and [Lecture 12, revision 1003742](https://de.wikiversity.org/w/index.php?oldid=1003742).
The contributor to the frozen revisions is recorded as Bocardodarapti.
In particular, source Example 10.7 and the standard cover in Example
12.10 provide prerequisites; the integrative problem and its complete
worked solution here form an independent editorial layer, not a
retranslation of a public source solution.
Production: OpenAI Codex gpt-5.6-sol, Ultra.
This new material is licensed under CC BY-SA 4.0; all credits and licences
of source components remain in force. No human authorship or review is
claimed, and no endorsement by the source author or institution is implied.
