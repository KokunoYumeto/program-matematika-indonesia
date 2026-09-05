---
title: "BGK 10 Mastery Exercises: Quasi-Affineness and Morphisms over a Base"
stable_id: d100-bridge-mastery-bgk-10
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_revision_contributor: "Marymay0609"
source_url: "https://de.wikiversity.org/w/index.php?oldid=612138"
source_manifest: authority/wikiversity-bgk/unit-10/UNIT_AUTHORITY_MANIFEST.json
source_manifest_sha256: a8b6384c316086dde5825b6c776289f93a1a2c4a4654bac57148f9e25a6f197f
non_endorsement: "Independent material; does not imply endorsement by the author or source institutions."
---

# BGK 10 mastery exercises {#d100-bridge-mastery-bgk-10}

The exercises come from Holger Brenner's course, *Bündel, Garben und Kohomologie*, worksheet revision 612138; revision contributor credit: Marymay0609. The following three solutions are **independent editorial material**, not public solutions by Brenner or translations of source solutions. Prepared by OpenAI Codex gpt-5.6-sol, Ultra. Licensed under CC BY-SA 4.0; no endorsement by the author or source institutions is implied.

## 1. Quasi-affine but not affine {#d100-bridge-mastery-bgk-10-new-01}

**Source:** [Exercise 10.1](bgk-reader.html#br-bgk-2019-w10-ex01), [worksheet revision 612138](https://de.wikiversity.org/w/index.php?oldid=612138).
Exact identifier: `Quasiaffines Schema/Nicht affin/Aufgabe`; source page `112256`, [fixed revision 847500](https://de.wikiversity.org/w/index.php?oldid=847500).

**Brenner's exercise.** Give an example of a quasi-affine scheme that is not affine.

**Independent solution.** Choose any field $K$, write $A=K[x,y]$, and take

$$
U=\operatorname{Spek}(A)\setminus\{(x,y)\}=D(x)\cup D(y).
$$

The last equality holds because the only prime ideal containing $x$ and $y$ is the maximal ideal $(x,y)$. As an open subset of an affine scheme, $U$ is quasi-affine. We will show that $U$ is not affine by computing its global sections.

The structure sheaf on the cover $D(x),D(y)$ gives

$$
\Gamma(U,\mathcal O_U)=A_x\cap A_y\subseteq K(x,y).
$$

Indeed, a section is a pair of elements of $A_x,A_y$ agreeing in $A_{xy}$; all these maps are injective because $A$ is an integral domain. If $a/x^m=b/y^n$ lies in the intersection, then $y^n a=x^m b$. In the unique factorisation domain $K[x,y]$, $x$ is prime and does not divide $y$, so $x^m$ divides $a$. Hence $a/x^m\in A$. The reverse inclusion is clear, so $\Gamma(U,\mathcal O_U)=A$ and the restriction map from $A$ is the identity under this identification.

Suppose $U$ were affine. The inclusion $j:U\to\operatorname{Spek}(A)$ would be a morphism between two affine schemes inducing an isomorphism on global sections. It would have to be an isomorphism: apply [Theorem 10.9](bgk-reader.html#br-bgk-2019-l10-thm-01) to the inverse of the global homomorphism to construct an inverse morphism; uniqueness in the theorem ensures that both composites are identities. But $j$ is not surjective, since $(x,y)$ is not in its image. This is a contradiction.

**Check.** The space $U$ is even quasi-compact, being a union of two affine open sets. Thus the failure of affineness in this example is not caused by a failure of quasi-compactness.

## 2. Quasi-affine but not quasi-compact {#d100-bridge-mastery-bgk-10-new-02}

**Source:** [Exercise 10.2](bgk-reader.html#br-bgk-2019-w10-ex02), [worksheet revision 612138](https://de.wikiversity.org/w/index.php?oldid=612138).
Exact identifier: `Quasiaffines Schema/Nicht quasikompakt/Aufgabe`; source page `112258`, [fixed revision 847501](https://de.wikiversity.org/w/index.php?oldid=847501).

**Brenner's exercise.** Give an example of a quasi-affine scheme that is not quasi-compact.

**Independent solution.** For a field $K$, take the polynomial ring in infinitely many variables

$$
A=K[x_1,x_2,x_3,\ldots],\qquad
U=\bigcup_{i\ge1}D(x_i)\subseteq\operatorname{Spek}(A).
$$

Each polynomial still involves only finitely many variables. The set $U$ is open in an affine scheme, hence quasi-affine by [Definition 10.4](bgk-reader.html#br-bgk-2019-l10-def-02).

The open cover $\{D(x_i)\}_{i\ge1}$ has no finite subcover. To prove this, take any finite index set $F\subset\mathbb N_{\ge1}$ and choose $j\notin F$. The ideal

$$
\mathfrak p_F=(x_i:i\in F)
$$

is prime because the quotient ring $A/\mathfrak p_F$ is the polynomial ring over $K$ in the remaining variables, which is an integral domain. The element $x_j$ does not belong to $\mathfrak p_F$, so $\mathfrak p_F\in D(x_j)\subseteq U$. In contrast, every $x_i$ with $i\in F$ belongs to $\mathfrak p_F$, so $\mathfrak p_F\notin\bigcup_{i\in F}D(x_i)$. Thus no finite choice covers $U$. This is the failure of quasi-compactness.

**Check.** A single open cover without a finite subcover suffices to prove that a space is not quasi-compact. Merely saying “the cover is infinite” is not enough, since an infinite cover may still have a finite subcover.

## 3. Morphisms over a base and algebra homomorphisms {#d100-bridge-mastery-bgk-10-new-03}

**Source:** [Exercise 10.6](bgk-reader.html#br-bgk-2019-w10-ex06), [worksheet revision 612138](https://de.wikiversity.org/w/index.php?oldid=612138).
Exact identifier: `Algebrahomomorphismus/Basisschema/Morphismus/Aufgabe`; source page `112315`, [fixed revision 1082198](https://de.wikiversity.org/w/index.php?oldid=1082198).

**Brenner's exercise.** For a commutative ring $R$ and commutative $R$-algebras $A,B$, prove that an $R$-algebra homomorphism $A\to B$ is the same data as a scheme morphism $\operatorname{Spek}(B)\to\operatorname{Spek}(A)$ over $\operatorname{Spek}(R)$.

**Independent solution.** Write the algebra structure maps as $\alpha:R\to A$ and $\beta:R\to B$, and the scheme structure morphisms as $p_A$ and $p_B$. By [Theorem 10.9](bgk-reader.html#br-bgk-2019-l10-thm-01), applied to the locally ringed space $\operatorname{Spek}(B)$ and affine target $\operatorname{Spek}(A)$, every ring homomorphism $\varphi:A\to B$ determines exactly one morphism $\psi$ with global homomorphism $\psi^\#=\varphi$. Conversely, global sections of any $\psi$ give that homomorphism; uniqueness in the theorem shows that the two operations are inverse to each other.

It remains to prove that the conditions involving the base correspond. By definition, $\varphi$ is an $R$-algebra homomorphism if and only if

$$
\varphi\circ\alpha=\beta.
$$

The composite $p_A\circ\psi$ has global homomorphism $\varphi\circ\alpha$, whereas $p_B$ has global homomorphism $\beta$. Both morphisms have affine target $\operatorname{Spek}(R)$. Again, uniqueness in Theorem 10.9 gives the equivalence

$$
\varphi\circ\alpha=\beta
\quad\Longleftrightarrow\quad
p_A\circ\psi=p_B.
$$

The condition on the right says exactly that $\psi$ is a morphism over $\operatorname{Spek}(R)$. Thus the general correspondence restricts to the required bijection, with ring arrows pointing in the opposite direction to scheme arrows.

**Check.** Commutativity of the maps on points alone is not enough. For example, complex conjugation gives a ring automorphism of $\mathbb C$ and a scheme automorphism of $\operatorname{Spek}(\mathbb C)$; its topological map is the identity on a one-point space, but it is not a morphism over $\operatorname{Spek}(\mathbb C)$ with the identity base structure, since it does not fix every scalar.
