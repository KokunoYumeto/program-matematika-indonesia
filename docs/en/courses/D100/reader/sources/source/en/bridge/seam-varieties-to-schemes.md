---
title: "Prerequisite Bridge: From Varieties to Schemes"
stable_id: d100-bridge-seam
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_credit: "Holger Brenner, Bündel, Garben und Kohomologie; credits and rights of source components remain in force."
non_endorsement: "Independent editorial material; no endorsement, authorship, or human review by Holger Brenner, The Stacks Project Authors, or a source institution is implied."
---

# From varieties to schemes: what changes? {#d100-bridge-seam}

This bridge connects the starting point of a reader of classical
algebraic geometry with the language of sheaves and schemes. It is an
independently written bridge explanation, not a translation of an
additional lecture by Holger Brenner. The algebraic prerequisites are
prime and maximal ideals, quotient rings, and localisation. All rings
here are commutative with identity; ring homomorphisms preserve the
identity.

## 1. Coordinate rings are not discarded {#d100-bridge-seam-koordinat}

For the classical comparison in this section only, take an algebraically
closed field $k$ and a nonempty affine algebraic set $V\subseteq k^n$.
Its coordinate ring is

$$
A=k[V]=k[x_1,\ldots,x_n]/I(V),
$$

where $I(V)$ is the ideal of all polynomials vanishing on $V$. Then $A$
is reduced: if $f^m$ vanishes on $V$, every value $f(a)$ in the field
$k$ is also zero, so $f\in I(V)$. If the term *variety* in the source
requires irreducibility, impose that condition too; in that case $A$
is an integral domain. Reduced and integral domain are not synonyms.

The prerequisite theorem connecting algebra with classical points is
the Nullstellensatz: for an ideal $J\subseteq k[x_1,\ldots,x_n]$,
$I(V(J))=\sqrt J$, and maximal ideals have the form
$(x_1-a_1,\ldots,x_n-a_n)$ with $a_i\in k$. Consequently,

$$
a\in V\quad\longleftrightarrow\quad
\mathfrak m_a=\{f\in A:f(a)=0\}\in\operatorname{MaxSpec}(A).
$$

The scheme construction keeps the same $A$, but its space is

$$
X=\operatorname{Spec}(A)
=\{\mathfrak p\subset A:\mathfrak p\text{ is a prime ideal}\}.
$$

On this space, $V(J)=\{\mathfrak p:J\subseteq\mathfrak p\}$ is
closed, while the sets $D(f)=\{\mathfrak p:f\notin\mathfrak p\}$
form an open basis. On a spectrum, $V(J)$ denotes a set of prime
ideals; do not immediately read it as a set of tuples in $k^n$.

## 2. Closed points and generic points {#d100-bridge-seam-titik}

The closure of a point $\mathfrak p$ is $V(\mathfrak p)$: a closed
set $V(J)$ contains $\mathfrak p$ exactly when $J\subseteq\mathfrak p$.
Thus closed points are precisely maximal ideals. The classical comparison
above identifies $V$ with the subspace of closed points of $X$, not
with all of $X$.

For example, for $A=k[t]$ with $k$ algebraically closed, the points are
$(t-a)$, $a\in k$, and one extra point $\eta=(0)$. The closure of
$\eta$ is the entire spectrum. This point records the whole line as
one irreducible closed subspace; it is not a new number to be added
to $k$. More generally, $\mathfrak p$ is the generic point of
$V(\mathfrak p)$.

If $k$ is not algebraically closed, closed points need not be valued
in $k$. For example, $(t^2+1)$ is a maximal ideal of $\mathbb R[t]$
with residue field $\mathbb R[t]/(t^2+1)\cong\mathbb C$. Always
specify the base field before identifying closed points with
$k$-rational points. The topological foundation is found in
[Brenner, Proposition 8.5](bgk-reader.html#br-bgk-2019-l08-prop-02).

## 3. From functions to sheaf sections {#d100-bridge-seam-seksi}

A presheaf $\mathcal F$ assigns an object $\mathcal F(U)$ to every
open set and restriction maps to smaller open sets. Identity restrictions
must be identities, and successive restriction must equal direct
restriction. A sheaf adds two conditions: sections that are locally
equal are equal; local sections agreeing on every overlap have exactly
one gluing. This is the content needed from
[Brenner, Definition 4.1](bgk-reader.html#br-bgk-2019-l04-def-01).

For $X=\operatorname{Spec}(A)$, the structure sheaf $\mathcal O_X$
is determined on the open basis by

$$
\Gamma(D(f),\mathcal O_X)=A_f,
\qquad
\Gamma(X,\mathcal O_X)=A.
$$

The denominator $f$ may be inverted precisely where it does not belong
to the prime ideal of the point. On a general open set, a section is
represented by compatible local fractions; do not require one
denominator to work on the entire open set. The basis formula and its
restrictions hold for any commutative ring, including rings with zero
divisors; see [Brenner, Lemma 9.12](bgk-reader.html#br-bgk-2019-l09-lem-03)
and [Stacks, tag 01HV](https://stacks.math.columbia.edu/tag/01HV).

The term *function* remains useful, but *section* emphasises that the
object belongs to a sheaf on an open set. On a general scheme, a
section is not merely a list of values in one fixed field.

## 4. Stalks, local rings, residue fields, and fibres {#d100-bridge-seam-lokal}

The stalk $\mathcal F_{\mathfrak p}$ records germs of sections around
$\mathfrak p$: two representatives agree if their restrictions agree
on some smaller neighbourhood. For the structure sheaf,

$$
\mathcal O_{X,\mathfrak p}=A_{\mathfrak p},
\qquad
\mathfrak m_{\mathfrak p}=\mathfrak pA_{\mathfrak p},
\qquad
\kappa(\mathfrak p)
=A_{\mathfrak p}/\mathfrak pA_{\mathfrak p}
\cong\operatorname{Frac}(A/\mathfrak p).
$$

The local ring records all germs, whereas the residue field records only
values at the point. Evaluation is the composite
$\mathcal O_X(U)\to\mathcal O_{X,\mathfrak p}\to\kappa(\mathfrak p)$
for $\mathfrak p\in U$. The affine line illustrates the difference:

| Point of $\operatorname{Spec}(k[t])$ | Local ring | Residue field |
|---|---|---|
| $\eta=(0)$ | $k(t)$ | $k(t)$ |
| $(t-a)$, $a\in k$ | $k[t]_{(t-a)}$ | $k$ |

At $a$, the germ $t-a$ is nonzero in the local ring, but its value in
the residue field is zero. For a sheaf of modules $\mathcal F$, the
fibre at the point is
$\mathcal F_{\mathfrak p}\otimes_{\mathcal O_{X,\mathfrak p}}
\kappa(\mathfrak p)$, not the stalk itself. For example, the stalk
of $\mathcal O_X$ at $a$ is $k[t]_{(t-a)}$, while its fibre is $k$.
This sheaf fibre must also be distinguished from the fibre of a scheme
morphism. See [Brenner, Definition 3.22](bgk-reader.html#br-bgk-2019-l03-def-16),
[Definition 7.13](bgk-reader.html#br-bgk-2019-l07-def-07), and
[Lemma 9.10](bgk-reader.html#br-bgk-2019-l09-lem-02).

## 5. Why nilpotents must not be silently removed {#d100-bridge-seam-nilpoten}

Take any field $k$ and $B=k[\varepsilon]/(\varepsilon^2)$. Every
prime ideal contains $\varepsilon$, so $\operatorname{Spec}(B)$ has
only the point $(\varepsilon)$. Its topological space is the same as
the one-point space $\operatorname{Spec}(k)$, but their global section
rings differ: they are $B$ and $k$, respectively. The section
$\varepsilon$ is nonzero, although its value in the only residue field
is zero. Thus even all point values need not determine a section.

A ring is *reduced* if it has no nonzero nilpotents; a scheme is reduced
if all its local rings are reduced. The scheme $\operatorname{Spec}(B)$
above is nonreduced because $B$ itself is local and $\varepsilon\ne0$
in it. Replacing a ring $A$ by $A_{\mathrm{red}}=A/\sqrt{(0)}$ preserves
the topological space of its spectrum: all prime ideals contain
$\sqrt{(0)}$, and the prime-ideal correspondence for the quotient
preserves closed sets. Its structure sheaf can nevertheless change,
as the example $B$ shows. This is the information lost if geometry is
remembered only as the zero set of equations.

## 6. Gluing objects and pulling back sections {#d100-bridge-seam-morfisme}

A ringed space is a pair $(X,\mathcal O_X)$; it is *locally ringed*
if every stalk of its structure sheaf is a local ring. A scheme is a
space locally isomorphic to a spectrum with its structure sheaf. Here
*isomorphic* concerns both space and sheaf, not merely a homeomorphism.

To construct a scheme from pieces $X_i$, specify open subsets
$U_{ij}\subseteq X_i$ and isomorphisms
$\varphi_{ij}:U_{ij}\to U_{ji}$. Besides identities and inverses,
on every triple overlap the domains must agree and
$\varphi_{jk}\circ\varphi_{ij}=\varphi_{ik}$ must hold. Gluing points
alone is insufficient: the structure sheaves must also be glued by
the same isomorphisms. Every point then still has an affine neighbourhood.
This local condition does not ensure that the entire glued space is
affine. The source definition is
[Brenner, Definition 10.1](bgk-reader.html#br-bgk-2019-l10-def-01);
the capstone that follows examines a global example.

A scheme morphism $f:X\to Y$ consists of a continuous map and a
sheaf map

$$
f^\#: \mathcal O_Y\longrightarrow f_*\mathcal O_X,
\qquad
(f_*\mathcal O_X)(V)=\mathcal O_X(f^{-1}(V)),
$$

inducing at every $x$ a local homomorphism
$\mathcal O_{Y,f(x)}\to\mathcal O_{X,x}$. Local means that the inverse
image of the target maximal ideal is the source maximal ideal. This
is not merely an extra condition on the point map; it connects that
map with pullback of sections. Compare
[Brenner, Definition 7.15](bgk-reader.html#br-bgk-2019-l07-def-09).

In the affine case, $\alpha:A\to B$ gives a map in the opposite
direction, $f:\operatorname{Spec}(B)\to\operatorname{Spec}(A)$, with
$f(\mathfrak q)=\alpha^{-1}(\mathfrak q)$. Indeed,
$f^{-1}(D(a))=D(\alpha(a))$, and the section map is
$A_a\to B_{\alpha(a)}$. On stalks, the map
$A_{\alpha^{-1}(\mathfrak q)}\to B_{\mathfrak q}$ is local because
a numerator belongs to the source prime ideal exactly when its image
belongs to $\mathfrak q$. Existence and uniqueness of this morphism
are [Brenner, Corollary 10.10](bgk-reader.html#br-bgk-2019-l10-cor-01).
For geometry over $k$, use $k$-algebra homomorphisms, not ring
homomorphisms that forget the base structure.

## A short orientation check with answers {#d100-bridge-seam-uji}

Is $(0)$ on the affine line closed? No: its closure is the whole line.
Is $t$ zero as a germ at $(t)$? No; only its evaluation is zero.
Must two schemes with one-point topological spaces be isomorphic? No:
$\operatorname{Spec}(k)$ and
$\operatorname{Spec}(k[\varepsilon]/(\varepsilon^2))$ have different
section rings. Is it correct to replace the direction $A\to B$ with
$\operatorname{Spec}(A)\to\operatorname{Spec}(B)$? No; the spectrum
direction is reversed. These four answers test four main transitions;
they do not add counted exercises to the mastery bank.

## Provenance, rights, and source route {#d100-bridge-seam-asal}

This explanation was produced by **OpenAI Codex gpt-5.6-sol, Ultra.**
and is licensed under **CC BY-SA 4.0** as an original editorial layer.
Definitions and results referenced from *Bündel, Garben und Kohomologie*
remain credited to **Holger Brenner**; contributor and translation
credits and source-component rights are unchanged. The frozen-version
references used are
[Lecture 3, revision 793623](https://de.wikiversity.org/w/index.php?oldid=793623),
[Lecture 4, revision 1003714](https://de.wikiversity.org/w/index.php?oldid=1003714),
[Lecture 7, revision 1003731](https://de.wikiversity.org/w/index.php?oldid=1003731),
[Lecture 8, revision 793632](https://de.wikiversity.org/w/index.php?oldid=793632),
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634),
and [Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733).
Stacks is a downstream reference by The Stacks Project Authors, not
a lecture source translated here; its rights remain separately in
force. No endorsement, authorship, or human review by source authors
or institutions is implied.
