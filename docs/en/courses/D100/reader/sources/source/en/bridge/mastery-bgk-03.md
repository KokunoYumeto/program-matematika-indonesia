---
title: "BGK Unit 3 Mastery Bank - Tensor Products and Stalks"
stable_id: d100-bridge-mastery-bgk-03
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision_contributor: "Bocardodarapti"
source_worksheet_revid: 619301
source_worksheet_url: "https://de.wikiversity.org/w/index.php?oldid=619301"
source_authority_manifest: authority/wikiversity-bgk/unit-03/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 60270cc7ba74a4ed744687ae18c3887eca8a2fff6bce48a819be102d4a619a5a
new_worked_solution_count: 2
selected_source_exercise_numbers: [3, 16]
existing_public_source_solution_count: 1
existing_public_source_solution_numbers: [1]
non_endorsement: "Independent editorial material; does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or the source institutions, nor human authorship or review."
---

# BGK Unit 3 mastery bank {#d100-bridge-mastery-bgk-03}

The problem statements come from Holger Brenner's course. The following
worked solutions and checking notes were prepared independently by **OpenAI
Codex gpt-5.6-sol, Ultra.**; they are not translations of public source
solutions. The source credits remain applicable, including **Bocardodarapti**
as the contributor to the frozen worksheet revision. This editorial material
is licensed under **CC BY-SA 4.0** and implies neither endorsement by the
author or source institutions nor human authorship or review.

The three mastery items for Unit 3 comprise the two new editorial solutions
here to Exercises 3.3 and 3.16, together with the already translated [public
source solution to Exercise
3.1](bgk-reader.html#br-bgk-2019-w03-ex01-solution). Solution 3.1 continues to
count as a source solution and is not repeated here. The frozen source map
states that Exercises 3.3 and 3.16 have no public solutions.

The prerequisites used are the gluing data for the Möbius strip from Unit 2,
the definition of the tensor product of bundles, and the definitions of a
presheaf and a stalk in terms of germ classes. Neither the sheaf property
nor cohomology is required.

## New item 1 - The tensor square of the Möbius strip {#d100-bridge-mastery-bgk-03-new-01}

Source: [Exercise 3.3](bgk-reader.html#br-bgk-2019-w03-ex03).
Statement identifier: *Möbiusband/Tensorprodukt/Trivial/Aufgabe*.
Fixed witness: [revision 846097](https://de.wikiversity.org/w/index.php?oldid=846097),
source page 111727. The exercise number is determined by frozen worksheet revision 619301.

### Source statement {#d100-bridge-mastery-bgk-03-new-01-statement}

Show that the tensor product of the Möbius strip with itself is a trivial
line bundle.

### Complete editorial solution {#d100-bridge-mastery-bgk-03-new-01-solution}

Write $L\to S^1$ for the real line bundle of the Möbius strip, with

$$
S^1=\{(x,y)\in\mathbb R^2\mid x^2+y^2=1\}.
$$

Use the cover and gluing data from [Example
2.11](bgk-reader.html#br-bgk-2019-l02-exa-01):

$$
U=S^1\setminus\{(0,1)\},
\qquad
V=S^1\setminus\{(0,-1)\}.
$$

On $U\cap V$ we have $x\ne0$. If $t_U$ and $t_V$ are the fibre coordinates
in the two trivialisations, the transition convention is

$$
t_V=\varepsilon(x,y)t_U,
\qquad
\varepsilon(x,y)=
\begin{cases}
1,&x>0,\\
-1,&x<0.
\end{cases}
$$

The function $\varepsilon$ is continuous on the intersection, since its two
components are open and the formula is constant on each component.

By [Definition 3.2](bgk-reader.html#br-bgk-2019-l03-def-02), the transition
map of $L\otimes L$ is obtained by tensoring the two transition maps. On a
fibre, the map on pure tensors is

$$
a\otimes b\longmapsto
(\varepsilon a)\otimes(\varepsilon b)
=\varepsilon^2(a\otimes b)=a\otimes b.
$$

Pure tensors span the tensor product, so this map is the identity on all of
$\mathbb R\otimes_{\mathbb R}\mathbb R$. Under the linear identification
$a\otimes b\mapsto ab$, the fibre is $\mathbb R$, and the tensor-bundle
transition is always $1$, on both components of the intersection.

Here is the resulting global trivialisation. Let $e_U(p)$ and $e_V(p)$ be
the local basis vectors of $L_p$ with coordinate $1$ in their respective
charts. Since coordinates change according to the formula above, on the
intersection we have

$$
e_U(p)=\varepsilon(p)e_V(p).
$$

Hence

$$
e_U(p)\otimes e_U(p)
=\varepsilon(p)^2 e_V(p)\otimes e_V(p)
=e_V(p)\otimes e_V(p).
$$

Thus the following two rules define a single well-defined map:

$$
\begin{aligned}
\Phi:L\otimes L&\longrightarrow S^1\times\mathbb R,\\
a\,e_U(p)\otimes e_U(p)&\longmapsto(p,a)
\quad(p\in U),\\
a\,e_V(p)\otimes e_V(p)&\longmapsto(p,a)
\quad(p\in V).
\end{aligned}
$$

In each chart, $\Phi$ is a trivialisation, so it is continuous and a linear
bijection on every fibre. Its inverse is given by the two local formulas

$$
(p,a)\longmapsto a\,e_U(p)\otimes e_U(p),
\qquad
(p,a)\longmapsto a\,e_V(p)\otimes e_V(p),
$$

which are continuous and agree on the intersection. Local continuity on an
open cover gives global continuity in both directions. Thus $\Phi$ is an
isomorphism of line bundles, and

$$
L\otimes L\cong S^1\times\mathbb R.
$$

### Pitfalls and checks {#d100-bridge-mastery-bgk-03-new-01-check}

The tensor product is not the direct sum. The rank of $L\otimes L$ is
$1\cdot1=1$, whereas the rank of $L\oplus L$ is $1+1=2$. The calculation
$(-1)(-1)=1$ here is a calculation of **tensor-product transitions**, not a
new gluing instruction for a picture of the strip.

As a check, the local sections $e_U\otimes e_U$ and $e_V\otimes e_V$ agree
on the intersection and are nonzero in every fibre. Together they give a
nowhere-zero global continuous section. New item 1 for Unit 2 provides a
second check that this line bundle is trivial.

## New item 2 - Stalks of the product of two presheaves {#d100-bridge-mastery-bgk-03-new-02}

Source: [Exercise 3.16](bgk-reader.html#br-bgk-2019-w03-ex16).
Statement identifier: *Prägarbe/Produkt/Halm/Aufgabe*.
Fixed witness: [revision 1083990](https://de.wikiversity.org/w/index.php?oldid=1083990),
source page 111822. The exercise number comes from frozen worksheet revision 619301.

### Source statement {#d100-bridge-mastery-bgk-03-new-02-statement}

Let $\mathcal F$ and $\mathcal G$ be presheaves on a topological space $X$,
and let $\mathcal F\times\mathcal G$ be their product presheaf. Show that
for every point $P\in X$,

$$
(\mathcal F\times\mathcal G)_P
=\mathcal F_P\times\mathcal G_P.
$$

### Complete editorial solution {#d100-bridge-mastery-bgk-03-new-02-solution}

We prove the source equality by constructing a canonical bijection, meaning
a bijection independent of the choice of neighbourhoods or germ representatives.
There is no hypothesis that $\mathcal F$ or $\mathcal G$ is a sheaf; it is
enough that both are presheaves of sets.

On an open set $U$, the value of the product presheaf is
$\mathcal F(U)\times\mathcal G(U)$, and restriction is componentwise. For
$V\subseteq U$, the formula is

$$
(s,t)|_V=(s|_V,t|_V).
$$

The identity and composition properties of restrictions follow from those
of the two presheaves. Thus the product object is indeed a presheaf.

By [Definition 3.21](bgk-reader.html#br-bgk-2019-l03-def-15) and
[Definition 3.22](bgk-reader.html#br-bgk-2019-l03-def-16), a germ
$s_P\in\mathcal F_P$ is represented by a section $s\in\mathcal F(U)$ on
an open neighbourhood $U$ of $P$. Representatives $s\in\mathcal F(U)$ and
$s'\in\mathcal F(U')$ give the same germ exactly when there is an open
neighbourhood $W$ with $P\in W\subseteq U\cap U'$ and $s|_W=s'|_W$.

**The canonical map.** Define

$$
\Theta:(\mathcal F\times\mathcal G)_P
\longrightarrow\mathcal F_P\times\mathcal G_P,
\qquad
(s,t)_P\longmapsto(s_P,t_P).
$$

If the pairs $(s,t)$ and $(s',t')$ have the same germ, they agree after
restriction to some common neighbourhood. Their components also agree
there, so $s_P=s'_P$ and $t_P=t'_P$. Hence $\Theta$ is well-defined.

**Surjectivity.** Take any $(a,b)\in\mathcal F_P\times\mathcal G_P$.
Choose a representative $s\in\mathcal F(U)$ of $a$ and
$t\in\mathcal G(V)$ of $b$, with $P\in U$ and $P\in V$. They may not
yet have the same domain. Since $U\cap V$ is still an open neighbourhood
of $P$, we have a pair

$$
(s|_{U\cap V},t|_{U\cap V})
\in(\mathcal F\times\mathcal G)(U\cap V).
$$

The germ of this pair is sent by $\Theta$ to $(a,b)$: restriction to a
smaller neighbourhood does not change the germ. Thus $\Theta$ is surjective.

**Injectivity.** Suppose $(s,t)\in(\mathcal F\times\mathcal G)(U)$ and
$(s',t')\in(\mathcal F\times\mathcal G)(U')$ have the same image under
$\Theta$. This means

$$
s_P=s'_P,\qquad t_P=t'_P.
$$

The first equality gives an open neighbourhood
$P\in W_{\mathcal F}\subseteq U\cap U'$ with
$s|_{W_{\mathcal F}}=s'|_{W_{\mathcal F}}$. The second equality gives an
open neighbourhood $P\in W_{\mathcal G}\subseteq U\cap U'$ with
$t|_{W_{\mathcal G}}=t'|_{W_{\mathcal G}}$. Set

$$
W:=W_{\mathcal F}\cap W_{\mathcal G}.
$$

The set $W$ is still an open neighbourhood of $P$. Restricting once more
and using composition of restrictions, both equalities hold simultaneously
on $W$. Hence

$$
(s,t)|_W=(s|_W,t|_W)
=(s'|_W,t'|_W)=(s',t')|_W.
$$

Thus $(s,t)_P=(s',t')_P$, and $\Theta$ is injective. Together with
surjectivity, this proves the required canonical bijection.

Explicitly, its inverse sends the pair of germs $(s_P,t_P)$ to the germ
$(s|_{U\cap V},t|_{U\cap V})_P$. The injectivity just proved ensures
that the result is independent of the chosen representatives. Thus all
choices in the construction of the inverse have been checked.

### Pitfalls and checks {#d100-bridge-mastery-bgk-03-new-02-check}

Do not pair two representatives before making their domains agree. A section
on $U$ and a section on $V$ yield a section of the product only after both
have been restricted to $U\cap V$.

The decisive step is taking a **finite intersection** of neighbourhoods.
The intersection of two open neighbourhoods is still open and contains $P$.
The same proof does not automatically apply to infinite products, because
an infinite intersection of open neighbourhoods need not be open. To check
the inverse, starting with $(s,t)_P$ on one neighbourhood $U$ gives back
$(s|_U,t|_U)_P=(s,t)_P$; starting with $(s_P,t_P)$ gives back the two
original germs.
