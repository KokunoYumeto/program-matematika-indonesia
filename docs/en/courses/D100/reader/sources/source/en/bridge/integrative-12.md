---
title: "Integrative Problem 12 — Source Navigation and Reconstruction of Hypotheses"
stable_id: d100-bridge-integrative-12
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_credit: "Theoretical foundations: Holger Brenner, Bündel, Garben und Kohomologie, Lectures 26–27; frozen-revision contributions retain the credits in the source reader."
non_endorsement: "Independent AI-generated material; not human-authored or human-reviewed, and no endorsement by the source author or institution is implied."
---

# Integrative problem 12: source navigation and reconstruction of hypotheses {#d100-bridge-integrative-12}

This is an independently written mathematical navigation problem, not an
exercise from Holger Brenner's source material. Its aim is to turn an
overly broad argument into a correct statement by tracing results and
hypotheses in the frozen source. All necessary information is supplied
below; no new web search is needed.

## Reading material and source identities {#d100-bridge-integrative-12-sumber}

Use the following four locations in the BGK reader. The theorem numbers
in the text and the suffixes of digital IDs do not always agree.

| Result | Translation location | Frozen semantic-entity revision |
|---|---|---|
| Theorem 26.10: Čech comparison | [br-bgk-2019-l26-thm-01](bgk-reader.html#br-bgk-2019-l26-thm-01) | [1088414](https://de.wikiversity.org/w/index.php?oldid=1088414) |
| Theorem 27.5: finiteness on projective space | [br-bgk-2019-l27-thm-03](bgk-reader.html#br-bgk-2019-l27-thm-03) | [1088405](https://de.wikiversity.org/w/index.php?oldid=1088405) |
| Theorem 27.7: finiteness on projective schemes | [br-bgk-2019-l27-thm-05](bgk-reader.html#br-bgk-2019-l27-thm-05) | [1088399](https://de.wikiversity.org/w/index.php?oldid=1088399) |
| Definition 27.8: Euler characteristic | [br-bgk-2019-l27-def-01](bgk-reader.html#br-bgk-2019-l27-def-01) | [1091410](https://de.wikiversity.org/w/index.php?oldid=1091410) |

The parent lecture-page revisions are
[793619 for Lecture 26](https://de.wikiversity.org/w/index.php?oldid=793619)
and [1070036 for Lecture 27](https://de.wikiversity.org/w/index.php?oldid=1070036).
The parent pages include other entities by transclusion. The complete
identity of the frozen edition therefore also includes those entity
revisions, the manifest, and the expanded text.

## Problem {#d100-bridge-integrative-12-soal}

Consider the following proposed argument, which is deliberately incorrect:

> Let $R$ be a commutative ring,
> $X=\operatorname{Proj}(R[X_0,\ldots,X_N]/\mathfrak a)$ with
> $\mathfrak a$ homogeneous, and let $\mathcal F$ be quasicoherent.
> The standard affine cover computes cohomology, so all
> $H^q(X,\mathcal F)$ are finite-dimensional over $R$.
> Consequently $\sum_q(-1)^q\dim_RH^q(X,\mathcal F)$ is always
> an integer-valued Euler characteristic.

1. Separate the claims about computing cohomology, finite generation of
   modules, and vector space dimension. Find the correct hypotheses
   and exact source for each claim.
2. Test the finiteness claim on $X=\mathbb P_K^1$ and
   $\mathcal F=\bigoplus_{j\geq0}\mathcal O_X$. Test the use of the
   word “dimension” when $R=\mathbb Z$ and
   $\mathcal F=\mathcal O_{\mathbb P_{\mathbb Z}^1}$.
3. In the induction step of the proof of Theorem 27.5, suppose we are
   given $\mathcal E=\bigoplus_{j=1}^r\mathcal O(\ell_j)$ with $r$
   finite, a surjection $\mathcal E\to\mathcal F$, and coherent kernel
   $\mathcal G$. For an integer $q\geq1$, suppose $R$ is Noetherian
   and both $H^{q-1}(\mathcal E)$ and $H^q(\mathcal G)$ are finitely
   generated. Reconstruct the step proving finite generation of
   $H^{q-1}(\mathcal F)$, checking the image and kernel of each map.
4. Explain why the parent-page revision alone does not fix the entire
   lecture content. What can and cannot be proved by a source SHA-256 hash?

## Solution {#d100-bridge-integrative-12-penyelesaian}

### 1. Three claims with three scopes {#d100-bridge-integrative-12-jawab-01}

First, Theorem 26.10 applies to a projective scheme over a commutative
ring $R$ and a quasicoherent sheaf $\mathcal F$. Its conclusion is
agreement of sheaf cohomology with Čech cohomology for the standard
affine cover, not finite generation of modules. In this cover, every
nonempty intersection is $D_+(\prod X_i)$ and is affine. Quasicoherence
allows the vanishing of positive cohomology on those affine intersections
to be used.

For an embedding in $\mathbb P_R^N$, this Čech complex has no terms
of degree greater than $N$. Thus it gives $H^q(X,\mathcal F)=0$ for
$q>N$. But having only finitely many terms in a complex does not mean
that each term or its cohomology is finitely generated.

Second, Theorem 27.7 requires $R$ to be Noetherian, $X$ projective over
$R$, and $\mathcal F$ coherent. Its conclusion is that
$H^q(X,\mathcal F)$ is a finitely generated $R$-module. Theorem 27.5
gives the same conclusion when $X=\mathbb P_R^N$. The word
“quasicoherent” in the proposed argument must be strengthened to
“coherent” to apply this result.

Third, to use $\dim_K$ as vector space dimension, take $R=K$ to be
a field. A field is automatically Noetherian. For $X$ projective over
$K$ and $\mathcal F$ coherent, finite generation of modules becomes
finite dimensionality of vector spaces. Definition 27.8 then gives

$$
\chi(X,\mathcal F)=
\sum_{q=0}^{\dim X}(-1)^q\dim_KH^q(X,\mathcal F).
$$

The source definition uses the vanishing of cohomology above the
dimension. To ensure that the infinite sum is actually finite, the
bound $q>N$ from the Čech complex also suffices in this setting with
a fixed embedding. No algebraic-closedness hypothesis on $K$ is needed.

The corrected statement, briefly, is: *on a projective scheme over a
field, a coherent sheaf has finite-dimensional cohomology and only
finitely many nonzero cohomology groups; the alternating sum of their
dimensions is its Euler characteristic*. Computing through Čech
cohomology is a proof tool, not a substitute for the finiteness hypotheses.

### 2. Two tests separating the hypotheses {#d100-bridge-integrative-12-jawab-02}

On $U_0=\operatorname{Spec}(K[t])$ and
$U_1=\operatorname{Spec}(K[t^{-1}])$, the sheaf
$\mathcal F=\bigoplus_{j\geq0}\mathcal O_X$ is associated to a free
module of infinite rank. It is quasicoherent but not coherent: its
stalk at the generic point, $\bigoplus_{j\geq0}K(t)$, is not finitely
generated.

Sections on each chart are tuples of finite support. A matching pair
on the overlap uses only finitely many indices in total, since there
are two charts. For each index, the gluing equation is
$a_j(t)=b_j(t^{-1})$, so both polynomials must be constant. Consequently

$$
H^0(X,\mathcal F)=\bigoplus_{j\geq0}K.
$$

This has infinite dimension. Theorem 26.10 still applies, but Theorem
27.7 cannot be applied to this sheaf. This is a concrete example showing
that quasicoherence is insufficient for the finiteness conclusion on
a projective scheme.

Now use $\mathbb P_{\mathbb Z}^1$. Matching polynomial pairs again give

$$
H^0(\mathbb P_{\mathbb Z}^1,\mathcal O)
=\mathbb Z[t]\cap\mathbb Z[t^{-1}]
=\mathbb Z.
$$

This module is generated by $1$, in accordance with the finiteness
theorem, since $\mathbb Z$ is Noetherian and $\mathcal O$ is coherent.
However, $\mathbb Z$ is not a field, so “vector space dimension over
$\mathbb Z$” is undefined. Module rank can be discussed separately,
but replacing dimension with rank is not a literal application of
Definition 27.8 and must not be introduced without defining a new
invariant.

### 3. Recovering the image–kernel step {#d100-bridge-integrative-12-jawab-03}

The given short exact sequence is

$$
0\longrightarrow\mathcal G\longrightarrow\mathcal E
\longrightarrow\mathcal F\longrightarrow0.
$$

The relevant part of its long exact cohomology sequence is

$$
H^{q-1}(\mathcal E)\xrightarrow{\epsilon}
H^{q-1}(\mathcal F)\xrightarrow{\delta}
H^q(\mathcal G).
$$

Exactness means $\ker\delta=\operatorname{im}\epsilon$. The first
isomorphism theorem gives a short exact sequence

$$
0\longrightarrow\operatorname{im}\epsilon
\longrightarrow H^{q-1}(\mathcal F)
\longrightarrow\operatorname{im}\delta
\longrightarrow0.
$$

The last term is the **image of $\delta$**, not $\ker\delta$.
The translated source [proof of Theorem 27.5](bgk-reader.html#br-bgk-2019-l27-thm-03-proof)
retains two inconsistencies already flagged by edition notes: the
ambient index $\mathbb P_R^d$ in one place although the space under
discussion is $\mathbb P_R^N$ after renaming the indices; and a
repeated assertion about finite generation of the kernel where finite
generation of the image of $\delta$ is needed. The reconstruction
below is an independent explanation, not a silent alteration of the
frozen text.

The module $\operatorname{im}\epsilon$ is a quotient of
$H^{q-1}(\mathcal E)$ and is therefore finitely generated: the image
of a finite generating set still generates. The module
$\operatorname{im}\delta$ is a submodule of $H^q(\mathcal G)$.
Since $R$ is Noetherian, a submodule of a finitely generated module is
also finitely generated. To recall why, first prove the claim for a
submodule $M\subseteq R^d$ by induction on $d$: projection to the
last coordinate has image a finitely generated ideal, while its kernel
is a submodule of $R^{d-1}$. Generators of the kernel together with
lifts of generators of the image generate $M$. For an arbitrary
finitely generated module, take a surjection from $R^d$ and apply this
result to the inverse image of the submodule in question. Thus
$\operatorname{im}\delta$ is finitely generated. This is where the
Noetherian hypothesis is used.

Take generators $a_1,\ldots,a_s$ of $\operatorname{im}\epsilon$ and
$b_1,\ldots,b_t$ of $\operatorname{im}\delta$. Choose lifts
$\widetilde b_i$ in $H^{q-1}(\mathcal F)$. For every $v$ in the middle
module, write $\delta(v)=\sum_i r_i b_i$. Then
$v-\sum_i r_i\widetilde b_i\in\ker\delta=\operatorname{im}\epsilon$,
so it is a combination of $a_1,\ldots,a_s$. The finite set

$$
a_1,\ldots,a_s,\widetilde b_1,\ldots,\widetilde b_t
$$

therefore generates $H^{q-1}(\mathcal F)$. All sheaf maps in this step
are on the same ambient space $\mathbb P_R^N$. For this subproblem,
the existence of $\mathcal E$, coherence of $\mathcal G$, and the two
cohomological finiteness statements are given data; the argument does
not assume that they follow merely from exactness.

### 4. Source identity is not a theorem certificate {#d100-bridge-integrative-12-jawab-04}

Parent revision 1070036 of Lecture 27 dates from 6 February 2026. In
its frozen material, the Theorem 27.5 entity has revision 1088405,
dated 30 May 2026, and [its proof entity](https://de.wikiversity.org/w/index.php?oldid=1101592)
has revision 1101592, dated 17 June 2026. This does not mean that the
parent page changed on those latter two dates: the entities it includes
have their own revision histories. Opening the parent revision alone
does not reliably reconstruct the entire transclusion closure used by
the edition.

To identify the reading material, record the course title, result
number, reader ID, parent-page revision, statement or proof entity
revision, and the identities of the manifest and expanded text. In
the freeze used by this problem, the SHA-256 hash of the expanded
Lecture 27 text is

$$
\begin{gathered}
\text{ee29b146c2ad0c14c25ea7c97662c294a2}\\
\text{ec0424791999580bece98448531316}.
\end{gathered}
$$

Join the two lines without spaces to obtain one 64-digit hexadecimal
hash. A matching hash ties the check to the same bytes as the recorded
identity; it is not proof that every mathematical argument in those
bytes is correct. The image–kernel inconsistency in the preceding
part must still be resolved through exactness and module algebra.
Conversely, a correct mathematical repair must not be reported as
though it were an exact quotation from the source revision.

## Self-check and material provenance {#d100-bridge-integrative-12-periksa}

A complete answer distinguishes four things: the cover that computes
cohomology, the finiteness conditions, the scalars that allow vector
space dimension, and the identity of the referenced text. A quick test:
if “coherent” is removed, the infinite direct-sum example defeats
finiteness; if “field” is removed, vector space dimension notation is
not automatically meaningful.

This independent problem, bridge exposition, and solution: CC BY-SA 4.0.
Model provenance: OpenAI Codex gpt-5.6-sol, Ultra. The credits to Holger
Brenner and revision contributors, and the licences of source components,
remain in force. No human authorship or review is claimed, and this
material implies no endorsement by the source author or institution.
