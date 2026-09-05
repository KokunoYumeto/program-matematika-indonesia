---
title: "Integrative Problem 4 — The Affine Line with Doubled Origin"
stable_id: d100-bridge-integrative-04
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_reference_author: "Holger Brenner"
source_reference_course: "Bündel, Garben und Kohomologie (Osnabrück 2019–2020)"
source_reference_revisions: "Lecture 9: 793634; Lecture 10: 1003733"
non_endorsement: "Independent editorial material; no endorsement by the source author or institution is implied."
---

# Integrative problem 4: the affine line with doubled origin {#d100-bridge-integrative-04}

This problem and solution were written as independent bridge material.
Their starting point is [Example 10.6 by Holger Brenner](bgk-reader.html#br-bgk-2019-l10-exa-01).
The discussion of fibres, failure of affineness, and the diagonal below
is an editorial development, not an additional public solution attributed
to Brenner.

## Problem {#d100-bridge-integrative-04-soal}

Let $k$ be a field; it need not be algebraically closed. Take two copies

$$
U_0=\operatorname{Spec}k[t_0],\qquad
U_1=\operatorname{Spec}k[t_1].
$$

Glue $D(t_0)\subset U_0$ to $D(t_1)\subset U_1$ by $t_0=t_1$.
Call the resulting scheme $X$, and call the two points arising from the
ideals $(t_0)$ and $(t_1)$ respectively $o_0$ and $o_1$. Write the common
coordinate on the overlap of the two charts as $t$.

1. Describe the glued structure sheaf. Compute
   $\Gamma(X,\mathcal O_X)$, the two stalks at $o_0,o_1$, and the stalk
   at the generic point. Does agreement of two stalks mean that the points
   are the same?
2. Construct the morphism $\pi:X\to\mathbb A_k^1$ given on each chart
   by the coordinate $t$. Compute the scheme-theoretic fibres at the
   origin and at the generic point. Prove that its global section
   homomorphism is an isomorphism, but $\pi$ is not a scheme isomorphism.
3. Prove that $X$ is not affine, although it has a cover by two affine
   schemes whose intersection is also affine.
4. For this problem, call a scheme over $k$ *separated* if its diagonal
   $\Delta:X\to X\times_kX$ is a closed immersion. By examining the
   chart $U_0\times_kU_1$, prove that $X$ is not separated.

Use the following affine facts with their hypotheses: for a commutative
ring $A$, [Lemma 9.10](bgk-reader.html#br-bgk-2019-l09-lem-02) gives
$\mathcal O_{\operatorname{Spec}A,\mathfrak p}=A_{\mathfrak p}$;
[Lemma 9.12](bgk-reader.html#br-bgk-2019-l09-lem-03) gives
$\Gamma(D(f),\mathcal O)=A_f$, including
$\Gamma(\operatorname{Spec}A,\mathcal O)=A$.

## Complete solution {#d100-bridge-integrative-04-solusi}

### 1. Gluing, sections, and stalks {#d100-bridge-integrative-04-solusi-01}

The identification of the open subsets uses the ring isomorphism
$k[t_0,t_0^{-1}]\cong k[t_1,t_1^{-1}]$. Its inverse is available;
with two charts there is no additional triple-overlap condition not
already determined by this isomorphism and the identities. For an open
subset $W\subseteq X$, the glued sheaf is given by

$$
\mathcal O_X(W)=
\left\{(s_0,s_1)\in
\mathcal O_{U_0}(W\cap U_0)\times
\mathcal O_{U_1}(W\cap U_1)
\ \middle|\
s_0|_{W\cap U_0\cap U_1}=s_1|_{W\cap U_0\cap U_1}
\right\}.
$$

Restriction is performed on both components. The sheaf axioms hold because
sections glue uniquely on each chart, and their agreement on the overlap
can then be checked locally. This sheaf restricts to the original affine
structure sheaf on $U_i$. Thus the two charts really make $X$ a scheme,
in accordance with [Definition 10.1](bgk-reader.html#br-bgk-2019-l10-def-01).

For $W=X$, the formula becomes

$$
\Gamma(X,\mathcal O_X)
=\{(f_0,f_1)\in k[t]\times k[t]
      \mid f_0=f_1\text{ in }k[t,t^{-1}]\}.
$$

The homomorphism $k[t]\to k[t,t^{-1}]$ is injective: if a polynomial
becomes zero, some power of $t$ annihilates it in the integral domain
$k[t]$, so the polynomial was already zero. The pairs above are therefore
exactly the pairs $(f,f)$, and

$$
\Gamma(X,\mathcal O_X)\cong k[t].
$$

The neighbourhood $U_i$ of $o_i$ gives

$$
\mathcal O_{X,o_0}\cong k[t]_{(t)},\qquad
\mathcal O_{X,o_1}\cong k[t]_{(t)},\qquad
\kappa(o_0)\cong\kappa(o_1)\cong k.
$$

The two chart generic points, corresponding to the zero ideals, lie in
$D(t)$ and glue to one point $\eta$. Its stalk is $k(t)$. The closure
of $\{\eta\}$ contains both charts, so $\eta$ is generic for all of $X$.

Nevertheless, $o_0\ne o_1$: neither belongs to the part being glued.
Indeed, the open set $U_0$ contains $o_0$ but not $o_1$. Isomorphic
stalks mean agreement of the type of local data, not identification of
points. Every global section $f$ has value $f(0)$ at both points, so
global sections do not distinguish this pair of points.

### 2. The morphism to the affine line and its fibres {#d100-bridge-integrative-04-solusi-02}

The maps $U_i\to\operatorname{Spec}k[t]$ arising from $t\mapsto t_i$
agree on the overlap. They therefore glue to $\pi$. On global sections,

$$
\pi^\#:k[t]\longrightarrow\Gamma(X,\mathcal O_X),\qquad
f\longmapsto(f,f),
$$

is the isomorphism just computed.

The scheme-theoretic fibre at the origin $0=(t)$ is obtained by taking
the fibre product with $\operatorname{Spec}k$. On each chart its ring is

$$
k[t_i]\otimes_{k[t]}k\cong k[t_i]/(t_i)\cong k.
$$

On the overlap, $t$ must be both invertible and zero, so the fibre ring
is the zero ring and its spectrum is empty. Hence

$$
X_0\cong\operatorname{Spec}k\ \amalg\ \operatorname{Spec}k.
$$

These are two reduced points, not a single point with nilpotent elements.
In contrast, over the generic point of the base, both chart fibres are
$\operatorname{Spec}k(t)$ and their overlap is also the whole of
$\operatorname{Spec}k(t)$. After gluing,

$$
X_{\eta_{\mathbb A^1}}\cong\operatorname{Spec}k(t).
$$

The morphism $\pi$ is not an isomorphism because it sends two distinct
points $o_0,o_1$ to the same point. Thus an isomorphism on global sections
alone is insufficient to recognise an isomorphism of general schemes.

### 3. Why the glued scheme is not affine {#d100-bridge-integrative-04-solusi-03}

Suppose $X$ were affine. For an affine scheme, the identification
$X\cong\operatorname{Spec}\Gamma(X,\mathcal O_X)$ follows from the
definition of an affine scheme and Lemma 9.12. Under this identification,
the morphism inducing the identity on the global section ring is an
isomorphism. Uniqueness of that morphism is also a case of
[Theorem 10.9](bgk-reader.html#br-bgk-2019-l10-thm-01): its source is
a locally ringed space and its target is affine.

Since $\pi^\#$ is an isomorphism, assuming that $X$ is affine forces
$\pi$ to be an isomorphism. This contradicts the two-point fibre at the
origin. Therefore $X$ is not affine.

An affine cover is a local condition in the definition of a scheme. It
does not say that all charts can be replaced by a single global affine
chart; the proof above exhibits precisely that failure.

### 4. A diagonal that is not closed {#d100-bridge-integrative-04-solusi-04}

The product of the two charts has ring

$$
k[t_0]\otimes_k k[t_1]\cong k[t_0,t_1],
$$

because giving two $k$-algebra homomorphisms from one-variable polynomial
rings amounts to choosing two commuting elements. Thus
$U_0\times_kU_1$ is an affine chart of $X\times_kX$.

A diagonal point in this cross-chart must come from a point of $X$
belonging to both $U_0$ and $U_1$, hence from $D(t)$. The diagonal ring
map on this chart is

$$
k[t_0,t_1]\longrightarrow k[t,t^{-1}],\qquad
t_0\longmapsto t,\quad t_1\longmapsto t.
$$

Consequently its image as a set of points is

$$
\Delta(X)\cap(U_0\times_kU_1)
=V(t_0-t_1)\cap D(t_0).
$$

The closed line $V(t_0-t_1)$ is isomorphic to $\operatorname{Spec}k[t]$.
The open subset $D(t)$ is dense in it: it contains the generic point,
the zero ideal of the integral domain $k[t]$. Thus the closure of this
image contains the point $(t_0,t_1)$, namely the pair $(o_0,o_1)$, but
that pair is not a diagonal point because $o_0\ne o_1$.

The intersection of the diagonal image with the cross-chart is therefore
not closed. If $\Delta$ were a closed immersion, this intersection
would have to be closed. This contradiction proves that $X$ is not
separated. The density argument uses the generic prime point, so it
remains valid when $k$ is a finite field.

## Checks and common pitfalls {#d100-bridge-integrative-04-periksa}

- The two origins have isomorphic stalks, but open neighbourhoods
  distinguish them. Do not call them the same point.
- The fibre at the origin consists of two reduced points. Do not replace
  it by $\operatorname{Spec}k[\varepsilon]/(\varepsilon^2)$.
- In checking the diagonal, the cross-chart $U_0\times_kU_1$ is crucial:
  the missing point is the pair of distinct origins.

## Sources and editorial status {#d100-bridge-integrative-04-sumber}

Source references: Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634),
especially Lemmas 9.10 and 9.12;
[Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733),
especially Definition 10.1, Example 10.6, and Theorem 10.9.

This independent bridge material and solution are licensed under
**CC BY-SA 4.0**. The credits and licences of source components remain
in force. Production: **OpenAI Codex gpt-5.6-sol, Ultra.** No human
authorship or review of these additions is claimed, and no endorsement
by Holger Brenner, Wikiversity, or the Wikimedia Foundation is implied.
