---
title: "BGK 7 Mastery Exercises - Units and Residue Fields"
stable_id: d100-bridge-mastery-bgk-07
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_authority_manifest: authority/wikiversity-bgk/unit-07/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 001074c62cedb1efc988d3214416d2d86a02976d5b22dc272f4fe064e72dfc95
source_worksheet_revision: 618943
new_solution_count: 2
source_exercises: ["7.5", "7.16"]
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 7 mastery exercises {#d100-bridge-mastery-bgk-07}

The following two problem statements come from Holger Brenner's course on Wikiversity. The solutions and learning checks are new editorial material prepared independently by **OpenAI Codex gpt-5.6-sol, Ultra.** Neither is a public source solution: the frozen map records the absence of public solutions for Exercises 7.5 and 7.16. The [public solution to Exercise 7.14](bgk-reader.html#br-bgk-2019-w07-sol-ex14) remains a separate source solution and is not counted as new writing here.

This text is licensed under **CC BY-SA 4.0**; credits to Holger Brenner and the sources are preserved. No claim of human authorship, endorsement, or review is made for these editorial solutions. The Indonesian term *ruang bergelanggang*, rendered here as *ringed space*, denotes the same object as *ruang berdering* in the Indonesian translation of Unit 7, in accordance with the reader glossary; the definitions and hypotheses are unchanged.

## New item 1 - Brenner Exercise 7.5: the sheaf of units {#d100-bridge-mastery-bgk-07-new-01}

Source: [Exercise 7.5 in the BGK reader](bgk-reader.html#br-bgk-2019-w07-ex05).
Frozen entity: `Beringter Raum/Einheiten/Garbe/Aufgabe`, pageid `116370`, [revision `1081774`](https://de.wikiversity.org/w/index.php?oldid=1081774).
The exercise number follows [Worksheet 7, revision `618943`](https://de.wikiversity.org/w/index.php?oldid=618943).

### Source problem statement {#d100-bridge-mastery-bgk-07-new-01-problem}

Let $(X,\mathcal O_X)$ be a ringed space. Prove that the assignment

$$
U\longmapsto\mathcal O_X(U)^\times
=\bigl(\Gamma(U,\mathcal O_X)\bigr)^\times
$$

on open sets $U\subseteq X$, together with the natural restrictions, is a sheaf of commutative groups. This sheaf is denoted by $\mathcal O_X^\times$ and called the sheaf of units.

### Complete independent solution {#d100-bridge-mastery-bgk-07-new-01-solution}

For each $U$, the units of the commutative ring $\mathcal O_X(U)$ form a commutative group under **multiplication**, with identity $1_U$ and multiplicative inverses. Ring restriction homomorphisms preserve multiplication and the identity. Thus, if $s,t\in\mathcal O_X(U)$ satisfy $st=1_U$, then for $V\subseteq U$,

$$
(s|_V)(t|_V)=1_V.
$$

That is, restriction sends units to units and inverses to inverses. The identity and composition properties of restrictions are inherited from $\mathcal O_X$. The assignment therefore gives, to begin with, a presheaf of commutative groups.

To prove the sheaf property, take an open cover $U=\bigcup_i U_i$. If two units $s,t\in\mathcal O_X(U)^\times$ have equal restrictions on every $U_i$, the uniqueness property of the sheaf $\mathcal O_X$ gives $s=t$. This proves uniqueness of gluing.

For existence, take units $s_i\in\mathcal O_X(U_i)^\times$ satisfying

$$
s_i|_{U_i\cap U_j}=s_j|_{U_i\cap U_j}
\quad\text{for all }i,j.
$$

Since $\mathcal O_X$ is a sheaf, there is exactly one $s\in\mathcal O_X(U)$ with $s|_{U_i}=s_i$. However, we must still prove that $s$ is a unit, not merely a ring section.

Write $t_i=s_i^{-1}$. On $U_i\cap U_j$, the restrictions of $t_i$ and $t_j$ are inverses of the same element. Inverses in a group are unique, so

$$
t_i|_{U_i\cap U_j}=t_j|_{U_i\cap U_j}.
$$

Thus the $t_i$ glue to $t\in\mathcal O_X(U)$. Now $st$ and $1_U$ have equal restrictions to every $U_i$:

$$
(st)|_{U_i}=s_it_i=1_{U_i}=1_U|_{U_i}.
$$

Sheaf uniqueness gives $st=1_U$. Since the ring is commutative, also $ts=1_U$, so $s\in\mathcal O_X(U)^\times$ with inverse $t$. This proves existence of gluing within the presheaf of units itself.

On the empty set, the section ring of the sheaf has just one element; its unit group is also the one-element group. Thus the empty-cover axiom introduces no exception. All axioms for a sheaf of commutative groups are satisfied.

### Pitfall and check {#d100-bridge-mastery-bgk-07-new-01-check}

Gluing the $s_i$ merely as sections of $\mathcal O_X$ is not enough: one must glue **their inverses** to prove that the resulting section is a unit. Moreover, $\mathcal O_X^\times$ is not in general a subsheaf of the additive group $\mathcal O_X$. For example, $1$ and $-1$ are units in $\mathbb R$, but their sum $0$ is not a unit. The correct group operation in this exercise is multiplication.

## New item 2 - Brenner Exercise 7.16: the residue field of continuous functions {#d100-bridge-mastery-bgk-07-new-02}

Source: [Exercise 7.16 in the BGK reader](bgk-reader.html#br-bgk-2019-w07-ex16).
Frozen entity: `Topologischer Raum/Stetige Funktionen/Restekörper/Aufgabe`, pageid `112082`, [revision `848530`](https://de.wikiversity.org/w/index.php?oldid=848530).
The exercise number follows Worksheet 7, revision `618943`.

### Source problem statement {#d100-bridge-mastery-bgk-07-new-02-problem}

Let $X$ be a topological space with its sheaf of real-valued continuous functions $\mathcal C=C^0(-,\mathbb R)$. Prove that the residue field at each point $P\in X$ is $\mathbb R$, through the canonical evaluation isomorphism.

### Complete independent solution {#d100-bridge-mastery-bgk-07-new-02-solution}

Fix $P\in X$ and write $A:=\mathcal C_P$ for the stalk. Elements of $A$ are germs $[U,f]_P$, where $P\in U$ is open and $f:U\to\mathbb R$ is continuous. Two representatives give the same germ if their functions agree on a smaller open neighbourhood of $P$. Since that neighbourhood contains $P$, the two function values at $P$ agree. Thus evaluation

$$
\operatorname{ev}_P:A\longrightarrow\mathbb R,
\qquad [U,f]_P\longmapsto f(P)
$$

is well-defined. Addition and multiplication of germs are computed after restricting representatives to a common neighbourhood, so evaluation is a ring homomorphism preserving $1$. It is surjective: each $r\in\mathbb R$ is the value of the germ of the constant function $x\mapsto r$.

Its kernel is the ideal

$$
\mathfrak m_P:=\{[U,f]_P\in A\mid f(P)=0\}.
$$

To verify that this is the stalk's unique maximal ideal, we characterise all its units. If $f(P)\ne0$, the set

$$
W:=f^{-1}(\mathbb R\setminus\{0\})\subseteq U
$$

is an open neighbourhood of $P$. The function $g:W\to\mathbb R$, $g(x)=1/f(x)$, is continuous, since multiplicative inversion is continuous on $\mathbb R\setminus\{0\}$. Since $fg=1$ on $W$, the germ $[U,f]_P$ is a unit in $A$.

Conversely, if $a\in A$ is a unit with inverse $b$, applying evaluation to $ab=1$ gives

$$
\operatorname{ev}_P(a)\operatorname{ev}_P(b)=1.
$$

Hence $\operatorname{ev}_P(a)\ne0$. Therefore

$$
A^\times=A\setminus\mathfrak m_P.
$$

The ideal $\mathfrak m_P$ is proper because it does not contain the germ of the constant function $1$. The surjective evaluation homomorphism gives $A/\mathfrak m_P\cong\mathbb R$, so $\mathfrak m_P$ is maximal. If $\mathfrak n$ is another maximal ideal, it cannot contain a unit; since every element outside $\mathfrak m_P$ is a unit, $\mathfrak n\subseteq\mathfrak m_P$. Maximality of $\mathfrak n$ and properness of $\mathfrak m_P$ force $\mathfrak n=\mathfrak m_P$. This also proves that $A$ is a local ring.

By [Definition 7.13](bgk-reader.html#br-bgk-2019-l07-def-07), the residue field at $P$ is $\kappa(P)=A/\mathfrak m_P$. The required isomorphism is

$$
\begin{aligned}
\kappa(P)&\longrightarrow\mathbb R,\\
[U,f]_P+\mathfrak m_P&\longmapsto f(P).
\end{aligned}
$$

This formula is independent of both the germ representative and the quotient-class representative. Its inverse sends $r$ to the class of the germ of the constant function $r$. The first composite plainly returns $r$. For the other composite, $f-f(P)$ vanishes at $P$, so its germ lies in $\mathfrak m_P$; hence the class of the germ of $f$ equals that of the constant $f(P)$. Both composites are indeed identities.

No Hausdorff or manifold assumption on $X$ is required. The only properties used are continuity of real functions and the definition of a stalk. If $X$ is empty, the statement about every point holds vacuously.

### Pitfall and check {#d100-bridge-mastery-bgk-07-new-02-check}

The stalk $\mathcal C_P$ is not its residue field. For $X=\mathbb R$ and $P=0$, the germ of $x\mapsto x$ is nonzero: the function is not identically zero on any neighbourhood of $0$. Yet its image in $\kappa(0)$ is $0$, since its value at $0$ is zero. This example distinguishes information about a function **near a point**, retained by the stalk, from its value **at the point**, retained by the residue field.
