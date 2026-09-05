---
title: "BGK Unit 2 Mastery Bank - Sections and Trivialisations"
stable_id: d100-bridge-mastery-bgk-02
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision_contributor: "Bocardodarapti"
source_worksheet_revid: 602852
source_worksheet_url: "https://de.wikiversity.org/w/index.php?oldid=602852"
source_authority_manifest: authority/wikiversity-bgk/unit-02/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: a348b56811fe98266feff9108a21a436a9b8f07a343321feab7d9fbb3b75e64d
new_worked_solution_count: 2
selected_source_exercise_numbers: [1, 2]
existing_public_source_solution_count: 1
existing_public_source_solution_numbers: [4]
non_endorsement: "Independent editorial material; does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or the source institutions, nor human authorship or review."
---

# BGK Unit 2 mastery bank {#d100-bridge-mastery-bgk-02}

The problem statements below come from Holger Brenner's course. The worked
solutions and checking notes were prepared independently by **OpenAI Codex
gpt-5.6-sol, Ultra.**; they are not translations of Brenner's public solutions.
The author and source-contributor credits remain applicable, including
**Bocardodarapti** as the contributor to the frozen worksheet revision. This
editorial material is licensed under **CC BY-SA 4.0** and implies neither
endorsement by the author or source institutions nor human authorship or review.

This unit counts three mastery items: two new editorial solutions to Exercises
2.1 and 2.2, and the already translated [public source solution to Exercise
2.4](bgk-reader.html#br-bgk-2019-w02-ex04-solution). Solution 2.4 continues to
count as a source solution and is neither copied nor labelled as new editorial
work here. Neither selected exercise has a public solution in the frozen source map.

The prerequisites are the definitions of a real vector bundle and local
trivialisation, and [Definition 2.1 on continuous
sections](bgk-reader.html#br-bgk-2019-l02-def-01). The base space is not assumed
to be Hausdorff.

## New item 1 - Nowhere-zero sections and triviality of line bundles {#d100-bridge-mastery-bgk-02-new-01}

Source: [Exercise 2.1](bgk-reader.html#br-bgk-2019-w02-ex01).
Statement identifier: *Reelles Geradenbündel/Trivial/Nullstellenfreier Schnitt/Aufgabe*.
Fixed witness: [revision 1048817](https://de.wikiversity.org/w/index.php?oldid=1048817),
source page 111598. The exercise number is determined by frozen worksheet
revision 602852; the revision of the transcluded statement is recorded separately above.

### Source statement {#d100-bridge-mastery-bgk-02-new-01-statement}

Show that a real line bundle $L\to X$ over a topological space $X$ is trivial
if and only if it has a continuous section that is nowhere zero.

### Complete editorial solution {#d100-bridge-mastery-bgk-02-new-01-solution}

Write the bundle projection as $p:L\to X$. Each fibre $L_x=p^{-1}(x)$ is a
one-dimensional real vector space. The nowhere-zero condition means
$s(x)\ne0_x$ in each fibre, not avoidance of a single zero point common to the
whole total space.

**First direction.** If the bundle is trivial, there is a bundle isomorphism

$$
\tau:L\longrightarrow X\times\mathbb R
$$

that preserves the base point and is linear on each fibre. Set
$s(x):=\tau^{-1}(x,1)$. This map is continuous as the composite of
$x\mapsto(x,1)$ and $\tau^{-1}$. Since $\tau$ is over $X$, we have
$p(s(x))=x$, so $s$ is a section. The linear isomorphism
$\tau_x:L_x\to\mathbb R$ sends $0_x$ to $0$, whereas
$\tau_x(s(x))=1$. Thus the section is nowhere zero.

**Conversely.** Let $s$ be a nowhere-zero continuous section. Define

$$
\Phi:X\times\mathbb R\longrightarrow L,
\qquad \Phi(x,t)=t\,s(x).
$$

Since $s(x)$ is a basis of the one-dimensional space $L_x$, the map
$t\mapsto t\,s(x)$ is a linear isomorphism $\mathbb R\to L_x$. Thus
$\Phi$ is bijective and linear on each fibre. We must still prove that
$\Phi$ and its inverse are continuous; a continuous bijection alone is not
enough to give a bundle isomorphism.

Take any local trivialisation

$$
\tau_U:p^{-1}(U)\longrightarrow U\times\mathbb R
$$

with $U\subseteq X$ open. In these coordinates, the section $s$ has the form

$$
\tau_U(s(x))=(x,a(x)),\qquad x\in U,
$$

for a continuous function $a:U\to\mathbb R$. Its continuity follows from
that of $\tau_U\circ s|_U$ and the second-coordinate projection. Since $s$
is nowhere zero, $a(x)\ne0$ throughout $U$. In these coordinates, $\Phi$
and its inverse are given by

$$
(x,t)\longmapsto(x,t\,a(x)),
\qquad
(x,b)\longmapsto\left(x,\frac{b}{a(x)}\right).
$$

Both formulas are continuous: multiplication in $\mathbb R$ is continuous,
and $x\mapsto1/a(x)$ is continuous because $a$ is nowhere zero. The sets
$U\times\mathbb R$ form an open cover of the domain of $\Phi$, while the
sets $p^{-1}(U)$ form an open cover of the domain of its inverse. Continuity
on an open cover gives global continuity in both directions.

Hence $\Phi$ is a bundle isomorphism $X\times\mathbb R\cong L$, and $L$
is trivial. Both directions have been proved.

### Pitfalls and checks {#d100-bridge-mastery-bgk-02-new-01-check}

Choosing a nonzero vector separately in every fibre does not yet produce a
**continuous** section. It is continuity that ensures the coordinate function
$a$ and the inverse trivialisation are continuous. Check the inverse formula
in one chart using

$$
\frac{t\,a(x)}{a(x)}=t,
\qquad
\frac{b}{a(x)}\,a(x)=b.
$$

Rank one is used precisely when a single nonzero vector is declared to be a
basis. In higher rank, a single nowhere-zero section does not by itself
trivialise the whole bundle.

## New item 2 - The image of a section is a closed subspace {#d100-bridge-mastery-bgk-02-new-02}

Source: [Exercise 2.2](bgk-reader.html#br-bgk-2019-w02-ex02).
Statement identifier: *Reelles Vektorbündel/Schnitt/Abgeschlossene Teilmenge/Aufgabe*.
Fixed witness: [revision 1048838](https://de.wikiversity.org/w/index.php?oldid=1048838),
source page 111631. The exercise number comes from frozen worksheet revision 602852.

### Source statement {#d100-bridge-mastery-bgk-02-new-02-statement}

Let $s:X\to V$ be a continuous section of a real vector bundle $p:V\to X$
over a topological space $X$. Show that the image $s(X)\subseteq V$ is a
closed subset homeomorphic to $X$.

### Complete editorial solution {#d100-bridge-mastery-bgk-02-new-02-solution}

**Homeomorphism with the base.** If $s(x)=s(y)$, apply $p$ and use
$p\circ s=\operatorname{Id}_X$ to obtain $x=y$. Thus the map

$$
\bar s:X\longrightarrow s(X),\qquad x\longmapsto s(x),
$$

is bijective. It is continuous for the subspace topology on $s(X)$: if $O$
is open in $V$, then $\bar s^{-1}(O\cap s(X))=s^{-1}(O)$ is open in $X$.
Its inverse is the continuous restriction

$$
p|_{s(X)}:s(X)\longrightarrow X.
$$

Indeed, $p(s(x))=x$, and if $v=s(x)\in s(X)$, then
$s(p(v))=s(x)=v$. Hence $\bar s$ is a homeomorphism.

**Closedness in the total space.** Take a local trivialisation

$$
\tau_U:p^{-1}(U)\longrightarrow U\times\mathbb R^r.
$$

There is a continuous map $f:U\to\mathbb R^r$ with
$\tau_U(s(x))=(x,f(x))$. Moreover,

$$
s(X)\cap p^{-1}(U)=s(U),
$$

because $s(x)\in p^{-1}(U)$ exactly when $x=p(s(x))\in U$. Therefore
$\tau_U(s(U))$ is the graph

$$
\operatorname{Graph}(f)
=\{(x,v)\in U\times\mathbb R^r\mid v=f(x)\}.
$$

The map

$$
h:U\times\mathbb R^r\longrightarrow\mathbb R^r,
\qquad h(x,v)=v-f(x)
$$

is continuous. Since $\{0\}$ is closed in $\mathbb R^r$, this graph is
the closed subset

$$
\operatorname{Graph}(f)=h^{-1}(\{0\})
$$

of $U\times\mathbb R^r$. Via the homeomorphism $\tau_U$, it follows
that $s(X)\cap p^{-1}(U)$ is closed in $p^{-1}(U)$.

The sets $p^{-1}(U)$ from all the trivialisations form an open cover of
$V$. On each such set,

$$
(V\setminus s(X))\cap p^{-1}(U)
$$

is open in $p^{-1}(U)$, hence also open in $V$. Their union is
$V\setminus s(X)$. Thus the complement of $s(X)$ is open, and $s(X)$ is
closed in $V$.

### Pitfalls and checks {#d100-bridge-mastery-bgk-02-new-02-check}

Do not infer closedness from $p\circ s=\operatorname{Id}_X$ alone. For
general continuous maps, this identity gives a topological embedding, but
does not by itself give a closed image. Here the proof uses the local model
$U\times\mathbb R^r$ and the closedness of $\{0\}$ in a real vector
space. The base space $X$ need not be Hausdorff.

As a check, if $s$ is the zero section, then $f=0$ and $h(x,v)=v$. The
local statement becomes the closedness of $U\times\{0\}$, exactly as expected.
