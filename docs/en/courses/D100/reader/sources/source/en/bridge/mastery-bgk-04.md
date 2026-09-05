---
title: "BGK 4 Mastery Bank - Gluing and Stalks"
stable_id: d100-bridge-mastery-bgk-04
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_pageid: 110209
source_worksheet_revid: 1003857
source_worksheet_url: "https://de.wikiversity.org/w/index.php?oldid=1003857"
source_authority_manifest: authority/wikiversity-bgk/unit-04/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 3f26616ff7e9f4ac0d5bb0e64ad8435fefc18e32e4c91b16d780d4346498f680
new_solution_count: 3
source_exercise_numbers: "4.1, 4.2, 4.9"
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 4 mastery bank: gluing and stalks {#d100-bridge-mastery-bgk-04}

The following problem statements come from Holger Brenner's course. The complete solutions, explanations, and brief checks are new editorial material prepared by **OpenAI Codex gpt-5.6-sol, Ultra.**, not translated source solutions. In the Unit 4 freeze, there are no public source solutions for these three selected exercises. Credits to the author and source contributors remain applicable; this text does not claim human authorship or review. The problem statements are unchanged. This material is licensed under **CC BY-SA 4.0**.

The main prerequisite is [Definition 4.1 on sheaves](bgk-reader.html#br-bgk-2019-l04-def-01): sections that agree locally are equal, and a family of sections agreeing on intersections has a unique gluing. For a sheaf of sets, $\mathcal F(\varnothing)$ has exactly one element; for a sheaf of groups, this value is the trivial group. Both include the empty cover in the sheaf axiom.

## New solution 1 - The product of two sheaves, Exercise 4.1 {#d100-bridge-mastery-bgk-04-new-01}

Source: [Exercise 4.1 in the reader](bgk-reader.html#br-bgk-2019-w04-ex01), identifier `Garbe/Produkt/Aufgabe`, page `111820`, [fixed revision 1082920](https://de.wikiversity.org/w/index.php?oldid=1082920). The exercise number follows Worksheet 4, revision `1003857`; the identity of the transcluded exercise page is recorded separately in the Unit 4 manifest.

**Brenner's problem statement.** Let $\mathcal F$ and $\mathcal G$ be sheaves on a topological space $X$. Prove that the assignment

$$
\mathcal H(U):=\mathcal F(U)\times\mathcal G(U)
$$

with the natural product maps as restrictions defines a sheaf on $X$.

**Independent editorial solution.** For open sets $V\subseteq U$, define

$$
\rho^{\mathcal H}_{U,V}(s,t)
:=\bigl(\rho^{\mathcal F}_{U,V}(s),
        \rho^{\mathcal G}_{U,V}(t)\bigr).
$$

Restriction from $U$ to itself is the identity. If $W\subseteq V\subseteq U$, then for every pair $(s,t)$,

$$
\rho^{\mathcal H}_{V,W}\rho^{\mathcal H}_{U,V}(s,t)
=\bigl(s|_W,t|_W\bigr)
=\rho^{\mathcal H}_{U,W}(s,t).
$$

Thus $\mathcal H$ is, to begin with, a presheaf.

Take an open cover $U=\bigcup_{i\in I}U_i$. If two pairs $(s,t),(s',t')\in\mathcal H(U)$ have equal restrictions to every $U_i$, equality of pairs means

$$
s|_{U_i}=s'|_{U_i},\qquad t|_{U_i}=t'|_{U_i}
$$

for every $i$. The local equality axiom for $\mathcal F$ gives $s=s'$, and the same axiom for $\mathcal G$ gives $t=t'$. Hence the pairs are equal.

Now take a compatible family $(s_i,t_i)\in\mathcal H(U_i)$. Compatibility on $U_i\cap U_j$ means precisely the two systems of equalities

$$
s_i|_{U_i\cap U_j}=s_j|_{U_i\cap U_j},\qquad
t_i|_{U_i\cap U_j}=t_j|_{U_i\cap U_j}.
$$

The sheaf property of $\mathcal F$ gives a unique $s\in\mathcal F(U)$ restricting to all the $s_i$. Likewise, there is a unique $t\in\mathcal G(U)$ restricting to all the $t_i$. The pair $(s,t)\in\mathcal H(U)$ glues the original family and is unique by the local equality property just proved.

Finally, $\mathcal H(\varnothing)$ is a product of two singleton sets and is therefore a singleton. Thus the empty cover also satisfies the axiom. Both sheaf conditions hold for every cover, and $\mathcal H$ is a sheaf.

**Pitfall and check.** Here the product is taken on each open set, with componentwise restrictions. Specifying the sets $\mathcal F(U)\times\mathcal G(U)$ alone does not specify a presheaf. As a check, the two projections $(s,t)\mapsto s$ and $(s,t)\mapsto t$ commute with restrictions precisely because of the definition above.

## New solution 2 - Sections on two disjoint pieces, Exercise 4.2 {#d100-bridge-mastery-bgk-04-new-02}

Source: [Exercise 4.2 in the reader](bgk-reader.html#br-bgk-2019-w04-ex02), identifier `Garbe/Unzusammenhängender Raum/Produkt/Aufgabe`, page `111900`, [fixed revision 1082921](https://de.wikiversity.org/w/index.php?oldid=1082921). The exercise number follows Worksheet 4, revision `1003857`.

**Brenner's problem statement.** Let $\mathcal G$ be a sheaf on a disconnected topological space decomposed as

$$
X=U\mathbin{\uplus}V,
$$

where $U,V$ are open, nonempty, and disjoint. Show that

$$
\mathcal G(X)=\mathcal G(U)\times\mathcal G(V).
$$

**Independent editorial solution.** The equality in the statement is a canonical identification through restriction. The map to be proved bijective is

$$
R:\mathcal G(X)\longrightarrow\mathcal G(U)\times\mathcal G(V),
\qquad s\longmapsto(s|_U,s|_V).
$$

If $R(s)=R(t)$, then $s|_U=t|_U$ and $s|_V=t|_V$. Since $U,V$ cover $X$, the local equality axiom gives $s=t$. Thus $R$ is injective.

For surjectivity, choose any pair $(a,b)\in\mathcal G(U)\times\mathcal G(V)$. The only intersection on which a comparison is needed is $U\cap V=\varnothing$. The two restrictions

$$
a|_{\varnothing},\ b|_{\varnothing}\in\mathcal G(\varnothing)
$$

are automatically equal, since $\mathcal G(\varnothing)$ is a singleton. Thus $(a,b)$ is a compatible family on the cover $\{U,V\}$. The gluing axiom gives a section $s\in\mathcal G(X)$ with $s|_U=a$ and $s|_V=b$. Therefore $R(s)=(a,b)$, so $R$ is surjective.

The inverse of $R$ sends $(a,b)$ to its unique gluing. No additional choice enters this construction; that is why the identification is canonical. If $\mathcal G$ is a sheaf of groups or rings, restrictions are homomorphisms, so $R$ is also an isomorphism for that algebraic structure, not merely a bijection of sets.

**Pitfall and check.** For a cover whose members are not disjoint, not every pair of sections can be glued. The permissible pairs must satisfy $a|_{U\cap V}=b|_{U\cap V}$. In this exercise the condition is automatic because the intersection is empty, not because gluing ignores compatibility. Nor does the statement literally identify sections with pairs before the map $R$ has been specified.

## New solution 3 - The skyscraper sheaf, Exercise 4.9 {#d100-bridge-mastery-bgk-04-new-03}

Source: [Exercise 4.9 in the reader](bgk-reader.html#br-bgk-2019-w04-ex09), identifier `Wolkenkratzergarbe/Gruppe/Garbeneigenschaft/Aufgabe`, page `139888`, [fixed revision 1081969](https://de.wikiversity.org/w/index.php?oldid=1081969). The exercise number follows Worksheet 4, revision `1003857`. The German typo in the source's final instruction does not change the mathematical statement.

**Brenner's problem statement.** Let $X$ be a topological space, $P\in X$, and $G$ a commutative group. For each open set $U\subseteq X$, set

$$
\mathcal G(U)=
\begin{cases}
G,&P\in U,\\
0,&P\notin U.
\end{cases}
$$

With the natural restrictions, prove that $\mathcal G$ is a sheaf of commutative groups, determine $\mathcal G_P$, and, if $P$ is closed, determine $\mathcal G_Q$ for every $Q\ne P$.

**Independent editorial solution.** For $V\subseteq U$, the restriction $\rho_{U,V}$ is the identity $G\to G$ if $P\in V$; the unique homomorphism $G\to0$ if $P\in U$ but $P\notin V$; and the identity of the trivial group $0\to0$ if $P\notin U$. The case $P\notin U$ but $P\in V$ cannot occur. These three cases immediately give the identity restriction and composition laws: once a restriction is zero, every subsequent restriction remains zero. Thus $\mathcal G$ is a presheaf of commutative groups.

Take an open cover $U=\bigcup_{i\in I}U_i$. If $P\notin U$, all the groups $\mathcal G(U)$, $\mathcal G(U_i)$, and those on intersections are trivial. There is only one possible compatible family, and its gluing is unique. This also includes $U=\varnothing$.

If $P\in U$, there is at least one index $i_0$ with $P\in U_{i_0}$. Take a compatible family $g_i\in\mathcal G(U_i)$. For every $i$ with $P\in U_i$, the point $P$ also belongs to $U_i\cap U_{i_0}$. Both restrictions to this intersection are identities on $G$, so compatibility gives

$$
g_i=g_{i_0}\quad\text{in }G.
$$

For indices with $P\notin U_i$, the section $g_i$ must be zero. Thus $g:=g_{i_0}\in G=\mathcal G(U)$ restricts to every $g_i$: via the identity on pieces containing $P$, and via $G\to0$ on the others. This gluing is unique, because restriction to $U_{i_0}$ is the identity. The same uniqueness argument shows that two sections over $U$ agreeing locally are equal. Hence $\mathcal G$ is a sheaf of commutative groups.

For the stalk at $P$, every open neighbourhood $W$ of $P$ has $\mathcal G(W)=G$, and all restrictions between such neighbourhoods are identities. Concretely, a germ represented by $g\in G$ on a neighbourhood is determined only by $g$: two representatives give the same germ exactly when those elements of $G$ agree. Hence

$$
\mathcal G_P\cong G.
$$

Finally, suppose $P$ is closed and $Q\ne P$. The set $X\setminus\{P\}$ is open and contains $Q$. Every germ at $Q$ can be represented by a section on an open neighbourhood $W$ of $Q$. After restriction to the smaller neighbourhood

$$
W\cap\bigl(X\setminus\{P\}\bigr),
$$

the section lies in the zero group. Thus every germ at $Q$ is zero, and

$$
\mathcal G_Q=0\qquad(Q\ne P,\ P\text{ closed}).
$$

**Pitfall and check.** The hypothesis that $P$ is closed is needed in the last step, not in constructing the sheaf. If every neighbourhood of $Q$ instead contains $P$, all the groups used to form the stalk at $Q$ are $G$ with identity restrictions, so that stalk is also isomorphic to $G$. Do not assume that every point of a topological space is closed. As another check, when $G=0$, the entire sheaf and all its stalks are indeed zero.
