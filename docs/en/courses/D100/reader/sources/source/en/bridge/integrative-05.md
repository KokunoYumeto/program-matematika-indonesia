---
title: "Integrative Problem 5 — Why Morphisms Must Be Local on Stalks"
stable_id: d100-bridge-integrative-05
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

# Integrative problem 5: why morphisms must be local on stalks {#d100-bridge-integrative-05}

This is an independent synthesis problem and solution, not a new public
problem or solution by Holger Brenner. Its references are the
[definition of a scheme morphism](bgk-reader.html#br-bgk-2019-l10-def-04)
and [Theorem 10.9 on morphisms to affine schemes](bgk-reader.html#br-bgk-2019-l10-thm-01).

## Problem {#d100-bridge-integrative-05-soal}

All rings here are commutative, and all ring homomorphisms preserve the
identity. A homomorphism of local rings
$\alpha:(R,\mathfrak m)\to(S,\mathfrak n)$ is called *local* if
$\alpha^{-1}(\mathfrak n)=\mathfrak m$.

1. Given $\varphi:A\to B$, for $\mathfrak q\in\operatorname{Spec}B$
   set $\mathfrak p=\varphi^{-1}(\mathfrak q)$. Construct the stalk map
   $A_{\mathfrak p}\to B_{\mathfrak q}$ and prove that it is local.
   Describe the map of residue fields.
2. Now let $k$ be an algebraically closed field with
   $\operatorname{char}k\ne2$. For
   $f:\operatorname{Spec}k[t]\to\operatorname{Spec}k[s]$ given by
   $s\mapsto t^2$, compute the stalk and residue field maps at the
   origin, the scheme-theoretic fibre at $s=0$, and the fibre at $s=a\ne0$.
3. Compute the vector space map $(s)/(s)^2\to(t)/(t)^2$ induced at the
   origin. Explain why the residue field map alone does not capture
   this behaviour.
4. Take $Z=\operatorname{Spec}k(t)$ and $Y=\operatorname{Spec}k[t]$.
   Construct a morphism of *ringed spaces* $h:Z\to Y$ that sends the
   unique point of $Z$ to $(t)$ and induces the inclusion
   $k[t]\hookrightarrow k(t)$ on global sections. Prove that $h$ is not
   a morphism of locally ringed spaces. Compare it with the scheme
   morphism produced by the same ring inclusion.

In part 3, the maximal ideals and their squares are taken in the
respective local rings. Their quotients are the *cotangent* spaces at
the points; the tangent spaces are their duals over the residue fields.

## Complete solution {#d100-bridge-integrative-05-solusi}

### 1. Contraction of prime ideals determines the local map {#d100-bridge-integrative-05-solusi-01}

The ideal $\mathfrak p$ is prime because if $ab$ maps into
$\mathfrak q$, one of $\varphi(a),\varphi(b)$ belongs to the prime
ideal $\mathfrak q$. Moreover, $1\notin\mathfrak p$. The spectrum map

$$
f:\operatorname{Spec}B\longrightarrow\operatorname{Spec}A,
\qquad \mathfrak q\longmapsto\varphi^{-1}(\mathfrak q)
$$

is continuous because $f^{-1}(D(a))=D(\varphi(a))$.

If $s\notin\mathfrak p$, then $\varphi(s)\notin\mathfrak q$, so
$\varphi(s)$ is invertible in $B_{\mathfrak q}$. The universal property
of localisation therefore gives a homomorphism

$$
f^\#_{\mathfrak q}:A_{\mathfrak p}\longrightarrow B_{\mathfrak q},
\qquad \frac as\longmapsto\frac{\varphi(a)}{\varphi(s)}.
$$

This formula is well defined: the relation expressing equality of two
fractions remains valid after applying the homomorphism, and denominators
become units. By [Lemma 9.10](bgk-reader.html#br-bgk-2019-l09-lem-02),
this is the map between the stalks of the affine structure sheaves.

In a localisation at a prime ideal, a fraction belongs to the maximal
ideal if and only if its numerator belongs to the original prime ideal.
Thus

$$
\frac as\in
(f^\#_{\mathfrak q})^{-1}(\mathfrak qB_{\mathfrak q})
\quad\Longleftrightarrow\quad
\varphi(a)\in\mathfrak q
\quad\Longleftrightarrow\quad
a\in\mathfrak p.
$$

The inverse image of the maximal ideal is exactly
$\mathfrak pA_{\mathfrak p}$; hence the stalk map is local. Passing
to quotient rings gives

$$
\kappa(\mathfrak p)
=A_{\mathfrak p}/\mathfrak pA_{\mathfrak p}
\longrightarrow
B_{\mathfrak q}/\mathfrak qB_{\mathfrak q}
=\kappa(\mathfrak q).
$$

This map is injective: the kernel of an identity-preserving homomorphism
from one field to another is a proper ideal and must therefore be zero.
Its direction is opposite to that of the point map.

### 2. The squaring map and its scheme-theoretic fibres {#d100-bridge-integrative-05-solusi-02}

The inverse image of $(t)$ under $k[s]\to k[t]$ is $(s)$. The stalk
map at the origin is

$$
k[s]_{(s)}\longrightarrow k[t]_{(t)},\qquad
\frac{a(s)}{b(s)}\longmapsto\frac{a(t^2)}{b(t^2)},
\qquad b(0)\ne0.
$$

The denominator condition holds because $b(t^2)$ has value $b(0)\ne0$
at the origin. The residue field map is the identity $k\to k$.

At the point $s=a$, the residue field of the base is $k$, with $s$
acting as $a$. The fibre ring is therefore

$$
k[t]\otimes_{k[s]}k\cong k[t]/(t^2-a).
$$

For $a=0$, this is $k[t]/(t^2)$. It has one prime ideal, $(\bar t)$,
because every prime ideal must contain the nilpotent element $\bar t$.
But $\bar t\ne0$ and $\bar t^2=0$. Thus the fibre at the origin has
only one topological point, yet its structure ring contains a nonzero
nilpotent element. It is therefore nonreduced. The number of points
does not record this thickening.

If $a\ne0$, choose $b\in k$ with $b^2=a$. Its existence uses algebraic
closedness, and $b\ne0$. Since the characteristic is not $2$, the
elements $b$ and $-b$ are distinct and $2b$ is a unit. Evaluation gives

$$
k[t]/(t^2-a)\longrightarrow k\times k,
\qquad [g]\longmapsto(g(b),g(-b)).
$$

This map is surjective: the pair $(u,v)$ is the image of the polynomial

$$
u\frac{t+b}{2b}+v\frac{b-t}{2b}.
$$

Its kernel is zero. Indeed, a polynomial vanishing at $b$ and $-b$ is
divisible by the coprime factors $t-b$ and $t+b$, hence by $t^2-a$.
Thus this fibre consists of two reduced points, each with residue field $k$.

### 3. The lost infinitesimal direction {#d100-bridge-integrative-05-solusi-03}

Both cotangent spaces at the origin are one-dimensional over $k$, with
bases $[s]$ and $[t]$. The induced map satisfies

$$
[s]\longmapsto[t^2]=0\quad\text{in }(t)/(t)^2.
$$

Thus the cotangent map is zero. Its dual, the tangent space map from
the source point to the target point, is also zero. In contrast, the
residue field map is the identity.

There is no contradiction: the residue field remembers values at the
point, whereas $\mathfrak m/\mathfrak m^2$ remembers the linear terms
of functions vanishing there. Substitution $s=t^2$ preserves constants
but sends a linear term on the target to a term of order two on the source.

### 4. A ringed-space morphism that fails to be local {#d100-bridge-integrative-05-solusi-04}

The topological space $Z$ has one point $z$. Define $h(z)=(t)$. This
map is continuous because the inverse image of every open subset is
either $Z$ or the empty set.

For an open subset $V\subseteq Y$ containing $(t)$, define

$$
h_V^\#:\mathcal O_Y(V)
\longrightarrow k[t]_{(t)}\longrightarrow k(t)
$$

by taking the germ at $(t)$ and then including it in the fraction field.
If $(t)\notin V$, then $h^{-1}(V)=\varnothing$; use the unique
homomorphism $\mathcal O_Y(V)\to\mathcal O_Z(\varnothing)=0$.

These maps are compatible with restriction. For two open sets containing
$(t)$, taking the germ before or after restriction gives the same result.
If the smaller set does not contain $(t)$, both composites map to the
zero ring. We thus obtain a sheaf morphism
$\mathcal O_Y\to h_*\mathcal O_Z$, so $h$ is indeed a morphism of
ringed spaces.

However, its stalk map is the inclusion

$$
h_z^\#:k[t]_{(t)}\hookrightarrow k(t).
$$

Since the target is a field, its maximal ideal is zero. Its inverse
image is also zero, not the maximal ideal $(t)k[t]_{(t)}$ of the source.
Concretely, the nonunit $t$ in the source becomes a unit in the target.
Thus this map is not local.

On global sections, $h^\#$ is still the inclusion
$k[t]\hookrightarrow k(t)$. But the *scheme* morphism induced by this
inclusion sends the zero ideal of $k(t)$ to the zero ideal of $k[t]$,
the generic point of $Y$, not the origin.

This is the role of the locality condition: contraction of the maximal
ideal of the stalk must agree with the target point. Theorem 10.9 asserts
uniqueness in the category of locally ringed spaces; the example $h$
does not satisfy that hypothesis and therefore does not contradict the
theorem.

## Checks and common pitfalls {#d100-bridge-integrative-05-periksa}

- Check denominators before writing a stalk map: $s\notin\mathfrak p$
  must ensure $\varphi(s)\notin\mathfrak q$.
- A residue field is neither a stalk nor the full ring of a
  scheme-theoretic fibre. At the origin in this example, the residue field
  is $k$ but the fibre ring is $k[t]/(t^2)$.
- The characteristic-not-$2$ condition is used to distinguish $b$ from
  $-b$ and divide by $2b$; do not remove it.
- Equality of global section homomorphisms does not force equality of
  ringed-space morphisms when the locality condition on stalks is omitted.

## Sources and editorial status {#d100-bridge-integrative-05-sumber}

References: Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634),
Lemmas 9.10 and 9.12;
[Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733),
Definition 10.8, Theorem 10.9, and Corollary 10.10. The examples and
solutions here are editorial additions, not quotations of source solutions.

This independent material is licensed under **CC BY-SA 4.0**; the credits
and licences of source components are preserved. Production:
**OpenAI Codex gpt-5.6-sol, Ultra.** No human authorship or review of
these additions is claimed, and no endorsement by Holger Brenner,
Wikiversity, or the Wikimedia Foundation is implied.
