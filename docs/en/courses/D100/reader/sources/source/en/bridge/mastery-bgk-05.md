---
title: "BGK 5 Mastery Bank - Sheafification and Quotient Stalks"
stable_id: d100-bridge-mastery-bgk-05
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_pageid: 110210
source_worksheet_revid: 619386
source_worksheet_url: "https://de.wikiversity.org/w/index.php?oldid=619386"
source_authority_manifest: authority/wikiversity-bgk/unit-05/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 328774ffd66341ba8841b86935037a043067202dd10916d3e0be5082faeac35e
new_solution_count: 2
source_exercise_numbers: "5.2, 5.11"
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 5 mastery bank: sheafification and quotient stalks {#d100-bridge-mastery-bgk-05}

The following problem statements come from Holger Brenner's course. The complete solutions, explanations, and brief checks are new editorial material prepared by **OpenAI Codex gpt-5.6-sol, Ultra.**, not translated source solutions. Credits to the author and source contributors remain applicable; this text does not claim human authorship or review. No endorsement by the author or source institutions is implied. This material is licensed under **CC BY-SA 4.0**.

Unit 5 already has a [public source solution to Exercise 5.5](bgk-reader.html#br-bgk-2019-w05-ex05-solution). That solution continues to count as a source solution and is not recreated here. The two new solutions below, to Exercises 5.2 and 5.11, complete the three mastery items for Unit 5. Both problem statements are preserved.

The notation $s_P$ denotes the germ of a section $s$ at $P$, while $\mathcal F_P$ is the stalk of the presheaf or sheaf $\mathcal F$. Equality of two germs means that their representatives agree after restriction to a sufficiently small open neighbourhood; they need not already agree on their original neighbourhoods.

## New solution 1 - The universal property of sheafification, Exercise 5.2 {#d100-bridge-mastery-bgk-05-new-01}

Source: [Exercise 5.2 in the reader](bgk-reader.html#br-bgk-2019-w05-ex02), identifier `Prägarbe/Vergarbung/Universelle Eigenschaft/Aufgabe`, page `111906`, [fixed revision 1083991](https://de.wikiversity.org/w/index.php?oldid=1083991). The exercise number follows Worksheet 5, revision `619386`; the revision of the transcluded exercise page is recorded separately in the Unit 5 manifest.

**Brenner's problem statement.** Let $\mathcal F$ be a presheaf on a topological space $X$, and let $\widetilde{\mathcal F}$ be its sheafification. For every presheaf morphism $\psi:\mathcal F\to\mathcal G$ to a sheaf $\mathcal G$, prove that there is exactly one morphism

$$
\widetilde\psi:\widetilde{\mathcal F}\longrightarrow\mathcal G
$$

factoring $\psi$ through the canonical morphism $\eta:\mathcal F\to\widetilde{\mathcal F}$. That is, $\widetilde\psi\circ\eta=\psi$.

**Independent editorial solution.** We construct the component $\widetilde\psi_U$ for each open set $U$, then prove that all components commute with restrictions. Use [Definition 5.1](bgk-reader.html#br-bgk-2019-l05-def-01): a section $\sigma\in\widetilde{\mathcal F}(U)$ is a family of germs $(\sigma_P)_{P\in U}$ locally arising from sections of $\mathcal F$. Thus there is an open cover $U=\bigcup_iU_i$ and $s_i\in\mathcal F(U_i)$ with

$$
\sigma|_{U_i}=\eta_{U_i}(s_i),
\qquad
(s_i)_Q=\sigma_Q\quad(Q\in U_i).
$$

We want to glue the sections

$$
t_i:=\psi_{U_i}(s_i)\in\mathcal G(U_i).
$$

To check compatibility, take $Q\in U_i\cap U_j$. The germs $(s_i)_Q$ and $(s_j)_Q$ agree. Since $\psi$ commutes with restrictions, it induces a stalk map $\psi_Q$, so

$$
(t_i)_Q=\psi_Q((s_i)_Q)
=\psi_Q((s_j)_Q)=(t_j)_Q.
$$

By [Lemma 4.4, the stalkwise test for equality of sections](bgk-reader.html#br-bgk-2019-l04-lem-01), applied to the sheaf $\mathcal G$ over $U_i\cap U_j$, we obtain

$$
t_i|_{U_i\cap U_j}=t_j|_{U_i\cap U_j}.
$$

Since $\mathcal G$ is a sheaf, the family $(t_i)$ has a unique gluing $t\in\mathcal G(U)$. Define $\widetilde\psi_U(\sigma):=t$.

This construction is independent of the cover or local representatives. Indeed, suppose $(V_j,r_j)$ is another choice of representatives for $\sigma$. At each point $Q\in U_i\cap V_j$, we have $(s_i)_Q=(r_j)_Q=\sigma_Q$. The same stalk argument gives

$$
\psi_{U_i}(s_i)|_{U_i\cap V_j}
=\psi_{V_j}(r_j)|_{U_i\cap V_j}.
$$

The two glued sections have equal restrictions on the refinement cover $\{U_i\cap V_j\}_{i,j}$ of $U$. Local uniqueness in $\mathcal G$ shows that the results are equal. Thus $\widetilde\psi_U$ is well-defined.

Now take an open set $W\subseteq U$. The restriction $\sigma|_W$ is represented by $s_i|_{U_i\cap W}$ on the cover $\{U_i\cap W\}_i$. Since $\psi$ is a presheaf morphism,

$$
\psi_{U_i\cap W}(s_i|_{U_i\cap W})
=\psi_{U_i}(s_i)|_{U_i\cap W}.
$$

Thus $\widetilde\psi_W(\sigma|_W)$ and $\widetilde\psi_U(\sigma)|_W$ have equal local restrictions. Uniqueness of gluing gives

$$
\widetilde\psi_W(\sigma|_W)
=\widetilde\psi_U(\sigma)|_W.
$$

Hence this family of components is a sheaf morphism.

To check the factorisation, take $s\in\mathcal F(U)$. The section $\eta_U(s)$ has representative $s$ on all of $U$, so the construction with the one-member cover gives

$$
\widetilde\psi_U(\eta_U(s))=\psi_U(s).
$$

Thus $\widetilde\psi\circ\eta=\psi$.

For uniqueness, suppose $\theta:\widetilde{\mathcal F}\to\mathcal G$ is another morphism with $\theta\circ\eta=\psi$. For a section $\sigma$ and the local representatives $s_i$ above, naturality of $\theta$ gives

$$
\theta_U(\sigma)|_{U_i}
=\theta_{U_i}(\eta_{U_i}(s_i))
=\psi_{U_i}(s_i)
=\widetilde\psi_U(\sigma)|_{U_i}.
$$

The sections are equal by the sheaf property of $\mathcal G$. This holds for all $U$ and $\sigma$, so $\theta=\widetilde\psi$. For $U=\varnothing$, both sheaves take singleton values, so the component and all its identities are also unique. The complete proof does not assume that $\mathcal F$ is already a sheaf.

**Pitfall and check.** Do not define $\widetilde\psi_U$ only on sections coming from $\eta_U(\mathcal F(U))$: $\eta_U$ need not be surjective. Representatives are available locally, and it is the sheaf property of the *target* $\mathcal G$ that permits gluing. If $\mathcal F$ is already a sheaf, $\eta$ is an isomorphism by [Lemma 5.2(4)](bgk-reader.html#br-bgk-2019-l05-lem-01); the formula above then gives $\widetilde\psi=\psi\circ\eta^{-1}$, as expected.

## New solution 2 - Stalks of a quotient sheaf, Exercise 5.11 {#d100-bridge-mastery-bgk-05-new-02}

Source: [Exercise 5.11 in the reader](bgk-reader.html#br-bgk-2019-w05-ex11), identifier `Garben von Gruppen/Untergarbe/Quotientengarbe/Halm/Aufgabe`, page `112024`, [fixed revision 1082924](https://de.wikiversity.org/w/index.php?oldid=1082924). The exercise number follows Worksheet 5, revision `619386`.

**Brenner's problem statement.** Let $\mathcal G$ be a sheaf of commutative groups, $\mathcal F\subseteq\mathcal G$ a subsheaf of groups, and $\mathcal G/\mathcal F$ its quotient sheaf. Prove that, for every point $P\in X$,

$$
(\mathcal G/\mathcal F)_P=\mathcal G_P/\mathcal F_P.
$$

**Independent editorial solution.** This equality means a canonical group isomorphism. We must not replace the quotient sheaf by the quotient of sections on each open set. Following [Definition 5.8](bgk-reader.html#br-bgk-2019-l05-def-05), first form the presheaf of groups

$$
\mathcal Q(U):=\mathcal G(U)/\mathcal F(U),
\qquad
\rho^{\mathcal Q}_{U,V}([g]):=[g|_V].
$$

These restrictions are well-defined: if $g-h\in\mathcal F(U)$, then $g|_V-h|_V\in\mathcal F(V)$ because $\mathcal F$ is a subsheaf. The quotient sheaf is $\widetilde{\mathcal Q}$. By [Lemma 5.2(2)](bgk-reader.html#br-bgk-2019-l05-lem-01), which applies to every presheaf, the canonical map induces an isomorphism

$$
\mathcal Q_P\xrightarrow{\ \sim\ }
\widetilde{\mathcal Q}_P
=(\mathcal G/\mathcal F)_P.
$$

It therefore suffices to determine $\mathcal Q_P$.

The quotient homomorphisms on each open set form a presheaf morphism $q:\mathcal G\to\mathcal Q$. On stalks, it gives

$$
q_P:\mathcal G_P\longrightarrow\mathcal Q_P,
\qquad
g_P\longmapsto[g]_P.
$$

If two sections $g\in\mathcal G(U)$ and $h\in\mathcal G(V)$ represent the same germ at $P$, they agree on some open neighbourhood $P\in W\subseteq U\cap V$. Their quotient classes then also agree in $\mathcal Q(W)$, so the formula for $q_P$ is independent of the representative. Addition of germs is computed after shrinking to a common neighbourhood; since every $q_U$ is a homomorphism, so is $q_P$.

The map $q_P$ is surjective. Every element $\xi\in\mathcal Q_P$ has a representative $a\in\mathcal Q(U)$ on some open neighbourhood $U$ of $P$. By the definition of a quotient group, there is $g\in\mathcal G(U)$ with $a=[g]$. Thus $\xi=[g]_P=q_P(g_P)$.

Next, the inclusion $\mathcal F\subseteq\mathcal G$ induces a stalk inclusion $\mathcal F_P\subseteq\mathcal G_P$, by [Lemma 4.5](bgk-reader.html#br-bgk-2019-l04-lem-02). We show that this subgroup is exactly the kernel of $q_P$.

If $g_P\in\ker q_P$, then $[g]_P=0$ in $\mathcal Q_P$. By the definition of equality of germs, there is an open neighbourhood $W$ of $P$, contained in the domain of the representative $g$, such that

$$
[g|_W]=0\quad\text{in }\mathcal G(W)/\mathcal F(W).
$$

This means precisely that $g|_W\in\mathcal F(W)$, so the original germ $g_P$ belongs to $\mathcal F_P$. Conversely, every element of $\mathcal F_P$ has a representative $f\in\mathcal F(W)$. The image of $f$ in $\mathcal Q(W)$ is zero, so $q_P(f_P)=0$. Thus

$$
\ker q_P=\mathcal F_P.
$$

The first isomorphism theorem for commutative groups now gives the explicit isomorphism

$$
\mathcal G_P/\mathcal F_P\xrightarrow{\ \sim\ }\mathcal Q_P,
\qquad
g_P+\mathcal F_P\longmapsto[g]_P.
$$

Composing it with the sheafification isomorphism yields

$$
\mathcal G_P/\mathcal F_P
\xrightarrow{\ \sim\ }(\mathcal G/\mathcal F)_P,
$$

giving the required canonical identification. The construction uses a representative on a sufficiently small neighbourhood; it makes no claim that a global representative is always available.

**Pitfall and check.** The germ equality $[g]_P=0$ means that there is a neighbourhood $W$ with $g|_W\in\mathcal F(W)$; it does not immediately mean that $g\in\mathcal F(U)$ on its original domain. Sheafification can change global sections but not stalks. As boundary checks, if $\mathcal F=0$, the formula gives the stalk $\mathcal G_P$; if $\mathcal F=\mathcal G$, both sides are the zero group.
