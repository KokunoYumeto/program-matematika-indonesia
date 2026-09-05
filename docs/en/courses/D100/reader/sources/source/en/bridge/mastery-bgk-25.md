---
title: "BGK 25 Mastery Exercises - Local Representatives and First Cohomology"
stable_id: d100-bridge-mastery-bgk-25
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision: 613127
source_authority_manifest: authority/wikiversity-bgk/unit-25/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: f454cb2f8ada795015dcf78d4ad56a54107d9773705b7113a1ef1600b341e26d
new_worked_solution_count: 2
source_exercise_numbers: "25.2,25.10"
existing_source_solution_counted: "25.1"
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, source contributors, Wikiversity, or the Wikimedia Foundation."
---

# BGK 25 mastery exercises: local representatives and first cohomology {#d100-bridge-mastery-bgk-25}

The following two solutions are new editorial material for Holger Brenner's exercises, not public source solutions. Together with the [public solution to Exercise 25.1](bgk-reader.html#br-bgk-2019-w25-sol-ex01), they form three mastery items for Unit 25. That public solution remains in its original place and retains its source attribution “essentially Tarek Emmrich”; it is neither copied nor counted as new editorial work.

## Source Exercise 25.2: gluing representatives modulo continuous functions {#d100-bridge-mastery-bgk-25-new-01}

Source: [Exercise 25.2 in the BGK reader](bgk-reader.html#br-bgk-2019-w25-ex02), entity `Intervall/Intervallüberdeckung/2/Funktionen modulo stetige Funktionen/Global surjektiv/Aufgabe`, [revision 1096998](https://de.wikiversity.org/w/index.php?oldid=1096998), page 114224. No adaptation has been made to the exercise's hypotheses.

### Problem statement {#d100-bridge-mastery-bgk-25-new-01-soal}

Let $I\subseteq\mathbb R$ be a real interval and $I=U\cup V$, where $U,V$ are intervals relatively open in $I$. Consider the short exact sequence of sheaves

$$
0\longrightarrow C^0(-,\mathbb R)
\longrightarrow\operatorname{Abb}(-,\mathbb R)
\longrightarrow\mathcal Q\longrightarrow0,
\qquad
\mathcal Q=\operatorname{Abb}(-,\mathbb R)/C^0(-,\mathbb R).
$$

A section $q\in\Gamma(I,\mathcal Q)$ is represented on $U$ by $s:U\to\mathbb R$ and on $V$ by $t:V\to\mathbb R$. Prove that $q$ has a representative given by a map $r:I\to\mathbb R$. The notation $\operatorname{Abb}$ means all maps; $s,t,r$ are not required to be continuous.

### Complete editorial solution {#d100-bridge-mastery-bgk-25-new-01-solusi}

Write $W=U\cap V$. Since $s$ and $t$ represent restrictions of the same section $q$, the image of $s|_W-t|_W$ in $\mathcal Q(W)$ is zero. Exactness at the middle sheaf shows that

$$
f:=s|_W-t|_W\in C^0(W,\mathbb R).
$$

This step can also be read directly locally: every point of $W$ has a neighbourhood on which $s-t$ is continuous; continuity is a local property, so $s-t$ is continuous on all of $W$. We are not assuming that evaluation on global sections preserves all sheaf surjections.

The result of [Exercise 25.1 and its source solution](bgk-reader.html#br-bgk-2019-w25-sol-ex01) gives continuous functions $g:U\to\mathbb R$ and $h:V\to\mathbb R$ with

$$
f=g|_W-h|_W.
$$

Here $h$ denotes the function on $V$. In the public source solution, the second piecewise formula defines $-h$, not $h$; with that sign convention the displayed decomposition is exactly $f=g|_W-h|_W$. If one interval is contained in the other, the decomposition can be taken directly as $g=f,h=0$ when $U\subseteq V$, or $g=0,h=-f$ when $V\subseteq U$. If $W$ is empty, use $g=h=0$. Thus the boundary cases require no additional hypothesis on the cover.

Define maps on the two members of the cover by

$$
r_U=s-g,\qquad r_V=t-h.
$$

On the intersection,

$$
r_U|_W-r_V|_W
=(s|_W-t|_W)-(g|_W-h|_W)=f-f=0.
$$

Thus the formula

$$
r(x)=
\begin{cases}
s(x)-g(x),&x\in U,\\
t(x)-h(x),&x\in V
\end{cases}
$$

is well-defined and gives a map $I\to\mathbb R$. The difference $r|_U-s=-g$ is continuous, so $r|_U$ and $s$ have the same image in $\mathcal Q(U)$. Likewise, $r|_V-t=-h$ is continuous. Thus the global image of $r$ and the section $q$ agree on the cover $U,V$; the uniqueness axiom of the sheaf $\mathcal Q$ says they agree on $I$.

### Check and pitfall {#d100-bridge-mastery-bgk-25-new-01-periksa}

What is glued is $s-g$ and $t-h$, not $s$ and $t$ themselves. The minus signs matter: the condition $s-t=g-h$ gives exactly $s-g=t-h$. Moreover, $\mathcal Q$ is the quotient in the category of sheaves; in general, $\mathcal Q(I)$ must not be identified from the outset with $\operatorname{Abb}(I,\mathbb R)/C^0(I,\mathbb R)$. The existence of a global representative in the situation of this exercise is precisely what must be proved.

## Source Exercise 25.10: the sheaf of units and the function field {#d100-bridge-mastery-bgk-25-new-02}

Source: [Exercise 25.10 in the BGK reader](bgk-reader.html#br-bgk-2019-w25-ex10), entity `Schema/Integer/Einheitengarbe/Funktionenkörpergruppe/Erste Kohomologie/Fakt/Beweis/Aufgabe`, [revision 1082082](https://de.wikiversity.org/w/index.php?oldid=1082082), page 114519. This supplies an editorial proof of the result stated as [Lemma 25.10](bgk-reader.html#br-bgk-2019-l25-lem-05).

### Problem statement {#d100-bridge-mastery-bgk-25-new-02-soal}

Let $(X,\mathcal O_X)$ be an integral scheme with function field $K$. Let $\mathcal O_X^\times$ be the sheaf of units and $\mathcal U$ the constant sheaf with value $K^\times$. Prove the identification

$$
H^1(X,\mathcal O_X^\times)
\cong
\frac{\Gamma(X,\mathcal U/\mathcal O_X^\times)}
{\operatorname{im}\bigl(K^\times\longrightarrow
\Gamma(X,\mathcal U/\mathcal O_X^\times)\bigr)}.
$$

The symbol $=$ in the source statement denotes this natural identification. Unit groups are written multiplicatively; their identity element is $1$.

### Complete editorial solution {#d100-bridge-mastery-bgk-25-new-02-solusi}

Since $X$ is integral, its underlying topological space is irreducible and all rings of nonempty affine charts are integral domains. There is a generic point $\eta$ with $\mathcal O_{X,\eta}=K$. Every nonempty open set contains $\eta$ and is irreducible, hence also connected. Consequently a locally constant function with values in $K^\times$ on a nonempty open set is constant. Thus

$$
\Gamma(V,\mathcal U)=K^\times\quad\text{for }V\ne\varnothing,
\qquad
\Gamma(\varnothing,\mathcal U)=\{1\}.
$$

Every restriction between two nonempty open sets is the identity on $K^\times$; restriction to the empty set is also surjective. Thus $\mathcal U$ is flasque. By [Lemma 25.3](bgk-reader.html#br-bgk-2019-l25-lem-01), flasque sheaves are acyclic, and in particular $H^1(X,\mathcal U)=0$.

Evaluation at the generic point gives an embedding $\mathcal O_X^\times\hookrightarrow\mathcal U$. To see injectivity, on an integral affine chart $\operatorname{Spek}(R)$, sections on principal opens lie in localisations $R_f\subseteq K$. Two sections equal as elements of $K$ agree on every such chart, and hence as sheaf sections. A unit section has an inverse also mapping into $K$, so its image lies in $K^\times$. This map is compatible with restrictions.

Write $\mathcal D=\mathcal U/\mathcal O_X^\times$, the quotient sheaf of abelian groups. We obtain a short exact sequence of sheaves

$$
1\longrightarrow\mathcal O_X^\times
\longrightarrow\mathcal U\longrightarrow\mathcal D
\longrightarrow1.
$$

The groups are commutative because they come from units in commutative rings. Thus [Corollary 25.2](bgk-reader.html#br-bgk-2019-l25-cor-01) applies. The beginning of the long exact cohomology sequence is

$$
\Gamma(X,\mathcal O_X^\times)
\longrightarrow K^\times
\xrightarrow{\alpha}\Gamma(X,\mathcal D)
\xrightarrow{\delta}H^1(X,\mathcal O_X^\times)
\longrightarrow H^1(X,\mathcal U)=0.
$$

Exactness at $H^1(X,\mathcal O_X^\times)$ makes $\delta$ surjective. Exactness at $\Gamma(X,\mathcal D)$ says $\ker\delta=\operatorname{im}\alpha$. The first isomorphism theorem for abelian groups now gives the required identification.

The local meaning of the result can be explained without changing the computation. A section $d\in\Gamma(X,\mathcal D)$ has local representatives $q_i\in K^\times$ on a cover by nonempty open sets $(V_i)$, with

$$
q_i/q_j\in\mathcal O_X^\times(V_i\cap V_j).
$$

The class $\delta(d)$ is zero exactly when a single $q\in K^\times$ represents $d$ on the entire space. Locally this means

$$
q_i/q\in\mathcal O_X^\times(V_i)\qquad\text{for every }i.
$$

Thus quotienting by the image of $K^\times$ disregards changes of all local representatives by the same nonzero rational function. This does not require that rational function to be a global regular unit.

### Check and pitfall {#d100-bridge-mastery-bgk-25-new-02-periksa}

A constant sheaf is not flasque on an arbitrary topological space. The proof here uses irreducibility of $X$ to ensure that every nonempty open set is connected. Nor should the denominator $\operatorname{im}(K^\times)$ be replaced by all of $\Gamma(X,\mathcal D)$, since that would erase the cohomological obstruction being computed. If $X=\operatorname{Spek}(K)$ is a single point, then $\mathcal O_X^\times=\mathcal U$, $\mathcal D$ is trivial, and both sides are indeed zero as abelian groups.

## Origin and licence of the material {#d100-bridge-mastery-bgk-25-kredit}

Source exercises and results: Holger Brenner and Wikiversity contributors at the linked revisions. Public solution 25.1 retains its source attribution to Tarek Emmrich and does not become new work in this file. The two supplementary solutions and mastery notes were prepared independently by OpenAI Codex gpt-5.6-sol, Ultra. This material is licensed under CC BY-SA 4.0; attribution and licences of source components are preserved. No claim of human authorship or review is made for these new solutions, and no endorsement by the source author, contributors, Wikiversity, or the Wikimedia Foundation is implied.
