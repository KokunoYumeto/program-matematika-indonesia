---
title: "Capstone: Reading Stacks Tags and Proving a Neighbourhood Affine"
stable_id: d100-bridge-stacks-capstone
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_credit: "The Stacks Project Authors, downstream reference; Holger Brenner, BGK prerequisites. Source credits and rights remain in force."
non_endorsement: "Independent editorial material; no endorsement, authorship, or human review by the source authors or institutions is implied."
---

# One capstone: an affine neighbourhood containing zero and infinity {#d100-bridge-stacks-capstone}

The aim of this exercise is to find the correct statement, recover
hypotheses recorded on a preceding page, and fill one gap in a proof
with a calculation of your own. There is still just one object: the
projective line glued from two affine lines. This is one integrated
exercise, not a tag inventory or extra mastery-bank problems.

The following problem and solution were independently written. The
motivating example comes from **The Stacks Project Authors**; the
prerequisites on sheaves, localisation, and morphisms come from
**Holger Brenner**'s course. Stacks is used as a downstream reference,
not as a translated source lecture.

## Verified reading map {#d100-bridge-stacks-capstone-tag}

The following official pages were checked on **31 August 2026**. Use
tags as reference identities; chapter and lemma numbers displayed on
the pages help navigation but may change. A permanent tag is not a
frozen copy either: record the access date when reconstructing a source.

| Official tag | Identity displayed when checked | Role in the exercise |
|---|---|---|
| [01HR](https://stacks.math.columbia.edu/tag/01HR) | Section 26.5, *Affine schemes* | Context for the spectrum construction with its sheaf. |
| [01HW](https://stacks.math.columbia.edu/tag/01HW) | Definition 26.5.5 | Meaning of an affine scheme as a locally ringed space. |
| [01HV](https://stacks.math.columbia.edu/tag/01HV) | Lemma 26.5.4 | Sections on principal opens and stalks. |
| [01JA](https://stacks.math.columbia.edu/tag/01JA) | Section 26.14, *Glueing schemes* | Complete hypotheses for gluing data. |
| [01JB](https://stacks.math.columbia.edu/tag/01JB) | Lemma 26.14.1 | Existence of the glued locally ringed space and its mapping properties. |
| [01JC](https://stacks.math.columbia.edu/tag/01JC) | Lemma 26.14.2 | Why gluing scheme pieces produces a scheme. |
| [01JE](https://stacks.math.columbia.edu/tag/01JE) | Example 26.14.4, *Projective line* | The example leaving an affine-neighbourhood proof to be supplied. |

All six candidate tags are relevant, but they are not interchangeable:
in particular, 01HW is not a gluing lemma. For the explicit assertion
about $\Gamma(D(f),\mathcal O)$ and stalks, the section reference 01HR
is sharpened to 01HV, linked directly from that section. No additional
tags outside this route are needed.

## Integrated problem {#d100-bridge-stacks-capstone-soal}

Take any field $k$, without assuming algebraic closedness or
characteristic zero. Put

$$
X_0=\operatorname{Spec}(k[x]),\qquad
X_\infty=\operatorname{Spec}(k[y]).
$$

Identify $D(x)\subseteq X_0$ with $D(y)\subseteq X_\infty$ through
the ring isomorphism

$$
k[y,y^{-1}]\longrightarrow k[x,x^{-1}],\qquad y\longmapsto x^{-1}.
$$

Write $P$ for the gluing. The point $0$ is represented by the ideal
$(x)$; the point $\infty$ by $(y)$. The point $1$ is represented by
$(x-1)$ or $(y-1)$. The final objective is to prove, as schemes, that

$$
U=P\setminus\{1\}\cong\operatorname{Spec}(k[s]),
\qquad s=\frac1{x-1}=\frac y{1-y},
$$

and to explain why $P$ itself is not affine. Work through the following
seven stages as one argument.

1. From the actual titles and statements, distinguish a definition,
   hypotheses, an existence lemma, a local lemma, and an example. What
   remains to be read when 01JB merely says that gluing data are given?
2. Write the directions of the space map and ring map, all domains,
   inverses, and the three-index conditions. Explain why $P$ is a scheme.
3. Compute $\Gamma(P,\mathcal O_P)$ and prove that $P$ is not affine
   without assuming that $k$ is infinite.
4. Show that $U$ is open and contains $0$ and $\infty$. Find the
   section rings on $A=U\cap X_0$ and $B=U\cap X_\infty$, then
   prove that the two formulas for $s$ agree.
5. Construct isomorphisms $A\cong D(s)$ and $B\cong D(s+1)$ in
   $\operatorname{Spec}(k[s])$, including inverse ring maps. Check
   their agreement on the overlap and finish the proof that $U$ is affine.
6. Determine the $s$ coordinates, local rings, and residue fields of
   $0$, $\infty$, and the generic point. Why must these three kinds
   of data not be interchanged?
7. Correct two false shortcuts: “its global section ring is a polynomial
   ring, so the space is affine” and “the gluing lemma ensures that every
   gluing of affine pieces is still affine”. Identify the part of the
   proof that actually closes each gap.

## Complete solution {#d100-bridge-stacks-capstone-jawaban}

### 1. Recovering a statement before using it {#d100-bridge-stacks-capstone-jawaban-01}

Tag 01HW gives a definition, not a theorem deducing affineness from
the global section ring. Tag 01JB uses the data described in the
introduction to 01JA. Reading the lemma page alone therefore does not
recover all its hypotheses. We need locally ringed spaces $X_i$,
open subsets $U_{ij}\subseteq X_i$, and isomorphisms
$\varphi_{ij}:U_{ij}\to U_{ji}$, with $U_{ii}=X_i$. For every $i,j,k$
we require

$$
\varphi_{ij}^{-1}(U_{ji}\cap U_{jk})=U_{ij}\cap U_{ik},
\qquad
\varphi_{jk}\circ\varphi_{ij}=\varphi_{ik}
\quad\text{on }U_{ij}\cap U_{ik}.
$$

The first equality gives the composite in the second equality the
correct domain. The conclusion of 01JB is still a locally ringed
space. The additional hypothesis that each piece is a scheme allows
01JC to be applied. Tag 01JE supplies a particular example, not a
substitute for the general hypotheses. This is the required chain of
source use, following the [introduction 01JA](https://stacks.math.columbia.edu/tag/01JA),
[Lemma 01JB](https://stacks.math.columbia.edu/tag/01JB), and
[Lemma 01JC](https://stacks.math.columbia.edu/tag/01JC).

### 2. Two pieces and gluing as a scheme {#d100-bridge-stacks-capstone-jawaban-02}

The space map $\varphi_{0\infty}:D(x)\to D(y)$ runs in the opposite
direction to $\varphi_{0\infty}^\#:k[y,y^{-1}]\to k[x,x^{-1}]$.
The inverse ring map sends $x\mapsto y^{-1}$; both composites are
identities on generators and therefore on the entire rings. Set
$U_{00}=X_0$, $U_{\infty\infty}=X_\infty$ with their identities,
and $U_{0\infty}=D(x)$, $U_{\infty0}=D(y)$.

With only two indices, every three-index condition reduces to an
identity or the inverse relations above. The image of $D(x)$ is exactly
$D(y)$, so the composition domains also agree. A ring isomorphism
induces a scheme isomorphism, not just a point map; this also follows
from [Brenner, Corollary 10.10](bgk-reader.html#br-bgk-2019-l10-cor-01).
Tag 01JB then provides the gluing and its open cover. Every point lies
in one of the affine pieces; this is the local reason in 01JC that
$P$ is a scheme. This construction is the projective line in
[Example 01JE](https://stacks.math.columbia.edu/tag/01JE).

### 3. Global does not mean affine {#d100-bridge-stacks-capstone-jawaban-03}

The sheaf condition gives

$$
\Gamma(P,\mathcal O_P)
=\{(f(x),g(y))\in k[x]\times k[y]:
f(x)=g(x^{-1})\text{ in }k[x,x^{-1}]\}.
$$

In the Laurent ring, the monomials $x^n$, $n\in\mathbb Z$, are
linearly independent over $k$. The left-hand side of the equation has
only nonnegative powers; the right-hand side has only nonpositive
powers. Equality forces all coefficients except that of power zero
to vanish. The two constants must agree, so
$\Gamma(P,\mathcal O_P)\cong k$.

If $P$ were affine, write $P\cong\operatorname{Spec}(R)$. The global
section formula in [01HV](https://stacks.math.columbia.edu/tag/01HV)
gives $R\cong k$, so $P$ would have only one point. Yet $0$ and
$\infty$ are distinct: neither lies in the region identified during
gluing. This is a contradiction. The proof also works over finite
fields; we are not counting only $k$-rational points and do not need
an argument that $P$ is infinite.

### 4. A section replacing the coordinate {#d100-bridge-stacks-capstone-jawaban-04}

The point $1$ is the same on both charts because the inverse of
$1\in k$ is still $1$. Its complement on each chart is a principal
open, so $U$ is open in the glued space, and

$$
A=D(x-1)\subseteq X_0,\qquad
B=D(y-1)\subseteq X_\infty,
$$

$$
\Gamma(A,\mathcal O)=k[x,(x-1)^{-1}],\qquad
\Gamma(B,\mathcal O)=k[y,(1-y)^{-1}].
$$

Using $1-y$ or $y-1$ does not change the localisation, since $-1$ is
a unit. The points $0$ and $\infty$ are not removed because $0\ne1$
in a field. On $A\cap B$, both $x$ and $x-1$ are invertible and
$y=x^{-1}$. Hence

$$
\frac{y}{1-y}
=\frac{x^{-1}}{1-x^{-1}}
=\frac1{x-1}.
$$

The two local sections are compatible, so the sheaf axiom gives a unique
section $s\in\Gamma(U,\mathcal O_U)$. This axiom is
[Brenner, Definition 4.1](bgk-reader.html#br-bgk-2019-l04-def-01);
the localisation formula is
[Lemma 9.12](bgk-reader.html#br-bgk-2019-l09-lem-03).

### 5. Proving affineness with two local inverses {#d100-bridge-stacks-capstone-jawaban-05}

Write $T=\operatorname{Spec}(k[s])$, with $s$ on this side an
indeterminate. The section just constructed determines a morphism
$h:U\to T$ through $k[s]\to\Gamma(U,\mathcal O_U)$. Its existence
and uniqueness use [Brenner, Theorem 10.9](bgk-reader.html#br-bgk-2019-l10-thm-01):
the source is a locally ringed space and the target is an affine scheme.

On $A$, the section $s=(x-1)^{-1}$ is a unit, so $h|_A$ factors
through $D(s)\subseteq T$. Its ring map and inverse are

$$
\begin{aligned}
k[s,s^{-1}]&\longrightarrow k[x,(x-1)^{-1}],
&s&\longmapsto (x-1)^{-1},\quad s^{-1}\longmapsto x-1,\\
k[x,(x-1)^{-1}]&\longrightarrow k[s,s^{-1}],
&x&\longmapsto 1+s^{-1},\quad (x-1)^{-1}\longmapsto s.
\end{aligned}
$$

Both composites are identities on generators; in particular,
$(1+s^{-1})-1=s^{-1}$. Thus $A\cong D(s)$. On $B$ we have
$s+1=(1-y)^{-1}$, so the following inverse pair gives
$B\cong D(s+1)$:

$$
\begin{aligned}
k[s,(s+1)^{-1}]&\longrightarrow k[y,(1-y)^{-1}],
&s&\longmapsto \frac y{1-y},\quad (s+1)^{-1}\longmapsto 1-y,\\
k[y,(1-y)^{-1}]&\longrightarrow k[s,(s+1)^{-1}],
&y&\longmapsto \frac s{s+1},\quad (1-y)^{-1}\longmapsto s+1.
\end{aligned}
$$

Here $1-s/(s+1)=1/(s+1)$; substitution on $y$ and $s$ also returns
the original generators. No division is by an element not already
inverted in the ring concerned.

The two opens of $T$ cover it: the ideal $(s,s+1)$ is the unit ideal
because $(s+1)-s=1$. Now check the overlap, not just two separate
formulas. On $D(s(s+1))$, the inverse of the first chart gives

$$
x=1+s^{-1}=\frac{s+1}{s},
$$

and the inverse of the second gives $y=s/(s+1)$. Both are units and
$xy=1$, exactly the transition relation forming $P$. Under
$A\cong D(s)$, the overlap $A\cap B=D(x(x-1))$ corresponds to
$D(s(s+1))$, because $s+1=x/(x-1)$. The same statement on $B$
follows from $s=y/(1-y)$.

Thus the two local inverses agree as morphisms to $U$ on the overlap.
They glue to $g:T\to U$. On the cover $D(s),D(s+1)$, the composite
$h\circ g$ is the identity; on the cover $A,B$, $g\circ h$ is the
identity. Equality of morphisms can be checked on an open cover: the
point maps and section pullbacks agree locally, hence globally by
uniqueness of gluing. Therefore $g=h^{-1}$ and

$$
U\cong\operatorname{Spec}(k[s]),
\qquad\Gamma(U,\mathcal O_U)\cong k[s].
$$

The order matters: here affineness is proved by a scheme isomorphism,
and the global section ring is obtained afterwards. This supplies the
details omitted in [Example 01JE](https://stacks.math.columbia.edu/tag/01JE).

### 6. Coordinates, germs, and values {#d100-bridge-stacks-capstone-jawaban-06}

At $0$, we have $x=0$, so $s=-1$; at $\infty$, we have $y=0$, so
$s=0$. The charts have the same generic point after gluing, since the
function-field isomorphism identifies $y=x^{-1}$. The isomorphism in
stage 5 gives the following table.

| Point of $U$ | Ideal of $k[s]$ | Local ring | Residue field |
|---|---|---|---|
| $0$ | $(s+1)$ | $k[s]_{(s+1)}$ | $k$ |
| $\infty$ | $(s)$ | $k[s]_{(s)}$ | $k$ |
| Generic $\eta$ | $(0)$ | $k(s)$ | $k(s)$ |

The stalk formula used applies to any prime point, not just closed
points; see [01HV](https://stacks.math.columbia.edu/tag/01HV). At $0$,
the element $s+1$ is a nonzero germ but has value zero after quotienting
by the maximal ideal. At $\eta$, the value of $s$ is a transcendental
element of $k(s)$, not a chosen member of $k$. Thus a coordinate as
a section, a germ as an element of a local ring, and a value as an
element of a residue field are different types of objects.

### 7. Checking the two shortcuts {#d100-bridge-stacks-capstone-jawaban-07}

A global section ring does not determine an arbitrary scheme. Already
in stage 3, $P$ and $\operatorname{Spec}(k)$ have isomorphic global
section rings but are not isomorphic schemes. To conclude that $U$
is affine, we genuinely need stage 5: correct domains, inverse ring
maps, agreement on the overlap, and a cover of all of $T$.

Likewise, the conclusion of 01JC is *scheme*, not *affine scheme*.
The object $P$ itself refutes that erroneous strengthening. Definition
01HW requires a global isomorphism to a spectrum; the existence of
affine charts alone only satisfies the definition of a scheme. No
finiteness, algebraic-closedness, or characteristic hypothesis on the
field is hidden in this calculation.

## Oral-proof rubric for self-study {#d100-bridge-stacks-capstone-rubrik}

Close the solution and explain one connected proof in about ten minutes,
writing down the necessary ring maps. Score each aspect 0 if you
cannot yet explain it, 1 if the idea is correct but one gap remains,
and 2 if all its requirements are met.

| Aspect | Requirements for a score of 2 |
|---|---|
| Source identity | Distinguish 01HW, 01JB, and 01JC, and find the hypotheses of 01JB in 01JA. |
| Domains and directions | Write $D(x)\to D(y)$ with the opposite-direction ring map and its inverse. |
| Global argument | Compute $\Gamma(P,\mathcal O_P)=k$ using Laurent polynomials and disprove affineness with two points. |
| Affine-neighbourhood proof | Give both pairs of inverse maps, show $D(s)\cup D(s+1)=T$, and check $xy=1$ on the overlap. |
| Object types and hypotheses | Distinguish sections, stalks, and residue fields, and explain why an arbitrary field suffices. |

A score of 8--10 indicates that you can reconstruct the main argument;
choose an aspect scored below 2 to revisit. A score of 4--7 suggests
repeating stages 4--5, writing out every localisation. A score of 0--3
suggests returning to the prerequisite bridge on sheaves and morphisms,
then redoing stages 1--2. This score is only a self-study diagnostic:
not a certification, not a claim of human review, and not a condition
for constructing, validating, or publishing the material.

## Credits and boundaries of the original layer {#d100-bridge-stacks-capstone-kredit}

The problem design, expanded proof, explanations of errors, and rubric
are an original editorial layer by **OpenAI Codex gpt-5.6-sol, Ultra.**,
licensed under **CC BY-SA 4.0**. Stacks examples and results remain
credited to **The Stacks Project Authors**, with their source rights
in force; this layer's licence does not relicense the Stacks website.
The Brenner references use
[Lecture 4, revision 1003714](https://de.wikiversity.org/w/index.php?oldid=1003714),
[Lecture 9, revision 793634](https://de.wikiversity.org/w/index.php?oldid=793634),
and [Lecture 10, revision 1003733](https://de.wikiversity.org/w/index.php?oldid=1003733).
Credits to Holger Brenner, contributors, and translations, and rights
of source components, are preserved. No endorsement, authorship, or
human review by source authors or institutions is implied.
