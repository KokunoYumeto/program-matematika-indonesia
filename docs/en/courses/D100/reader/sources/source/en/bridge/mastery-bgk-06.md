---
title: "BGK 6 Mastery Exercises - Exactness and Sheaf Operations"
stable_id: d100-bridge-mastery-bgk-06
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_authority_manifest: authority/wikiversity-bgk/unit-06/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 69a10e682e853c6f386afbc68438605846e5096220b21bd1e827c07633a79244
source_worksheet_revision: 900086
new_solution_count: 3
source_exercises: ["6.4", "6.9", "6.13"]
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 6 mastery exercises {#d100-bridge-mastery-bgk-06}

The following three problem statements come from Holger Brenner's course on Wikiversity. The complete solutions and learning checks are new editorial material prepared independently by **OpenAI Codex gpt-5.6-sol, Ultra.** These are not translated public solutions by Brenner: the frozen source map records the absence of public solutions for all three exercises. Their mathematical statements and hypotheses are unchanged.

This text is licensed under **CC BY-SA 4.0**, with source credits preserved. No claim of human authorship, endorsement, or review is made for these editorial solutions. The learning sequence moves from sections on open sets to stalks and then to sheaf morphisms.

## New item 1 - Brenner Exercise 6.4: a split sequence {#d100-bridge-mastery-bgk-06-new-01}

Source: [Exercise 6.4 in the BGK reader](bgk-reader.html#br-bgk-2019-w06-ex04).
Frozen entity: `Topologische Gruppen/Spaltende Sequenz/Garbenversion/Aufgabe`, pageid `112025`, [revision `1050308`](https://de.wikiversity.org/w/index.php?oldid=1050308).
The exercise number follows [Worksheet 6, revision `900086`](https://de.wikiversity.org/w/index.php?oldid=900086).

### Source problem statement {#d100-bridge-mastery-bgk-06-new-01-problem}

Let $F$ and $H$ be commutative topological groups, $G=F\times H$ with the product topology, and

$$
0\longrightarrow F\longrightarrow G\longrightarrow H\longrightarrow0
$$

the associated product short exact sequence. Prove that, for every topological space $X$, there is a short exact sequence of sheaves

$$
0\longrightarrow C^0(-,F)\longrightarrow C^0(-,G)
\longrightarrow C^0(-,H)\longrightarrow0,
$$

and that the rightmost map remains surjective after global evaluation on $X$.

### Complete independent solution {#d100-bridge-mastery-bgk-06-new-01-solution}

Use additive notation for all three groups. The inclusion and projection in question are $j(a)=(a,0_H)$ and $p(a,b)=b$. For each open $U\subseteq X$, define

$$
\begin{aligned}
j_U:C^0(U,F)&\longrightarrow C^0(U,G),&
j_U(a)(x)&=(a(x),0_H),\\
p_U:C^0(U,G)&\longrightarrow C^0(U,H),&
p_U(b)(x)&=p(b(x)).
\end{aligned}
$$

Both maps are group homomorphisms. They also produce continuous functions, since the inclusion $j$ and projection $p$ are continuous. Composition with a fixed function commutes with restriction to an open set, so the families $j_U,p_U$ are presheaf morphisms.

The presheaf $C^0(-,F)$ is a sheaf: local functions agreeing on intersections determine exactly one function on their union, and that function is continuous because continuity can be tested on an open cover. The same argument applies to $G$ and $H$. Thus these are indeed sheaf morphisms.

Now check exactness for every $U$. If $j_U(a)=0$, then $(a(x),0_H)=(0_F,0_H)$ for every $x\in U$, so $a=0$; hence $j_U$ is injective. The composite $p_Uj_U$ is zero. Conversely, if $p_U(b)=0$, each $b(x)$ has the form $(a(x),0_H)$. The function $a=\operatorname{pr}_F\circ b$ is continuous and $j_U(a)=b$. Thus

$$
\ker p_U=\operatorname{im}j_U.
$$

For surjectivity, take any $h\in C^0(U,H)$ and set

$$
\sigma_U(h)(x):=(0_F,h(x)).
$$

This function is continuous, and $p_U\sigma_U(h)=h$. The family $\sigma_U$ itself is compatible with restrictions. Thus $\sigma$ is a sheaf morphism with $p\sigma=\operatorname{Id}$: the sheaf sequence even splits. Every section in the kernel comes from a section on the left, and every section on the right has a preimage on the same open set; this proves sheaf exactness, not just a formal statement about a complex.

In particular, for $U=X$, the formula $h\mapsto(x\mapsto(0_F,h(x)))$ gives a right inverse on global sections. Hence

$$
C^0(X,G)\longrightarrow C^0(X,H)
$$

is surjective, as required. The entire argument also applies to $U=\varnothing$, when the group of maps has just one element.

### Pitfall and check {#d100-bridge-mastery-bgk-06-new-01-check}

In general, surjectivity of a sheaf morphism guarantees only local preimages, not global ones. Here the decisive extra step is the existence of **a single global right inverse** $H\to F\times H$, $h\mapsto(0_F,h)$. Check directly that $\sigma_U(h)|_V=\sigma_V(h|_V)$ for $V\subseteq U$; this is why the splittings on all open sets constitute a sheaf splitting.

## New item 2 - Brenner Exercise 6.9: pushforward from a point {#d100-bridge-mastery-bgk-06-new-02}

Source: [Exercise 6.9 in the BGK reader](bgk-reader.html#br-bgk-2019-w06-ex09).
Frozen entity: `Topologischer Raum/Punkt/Vorschub/Wolkenkratzergarbe/Aufgabe`, pageid `112028`, [revision `1084500`](https://de.wikiversity.org/w/index.php?oldid=1084500).
The exercise number follows Worksheet 6, revision `900086`.

### Source problem statement {#d100-bridge-mastery-bgk-06-new-02-problem}

Let $X$ be a topological space, $P\in X$, and $i:\{P\}\to X$ the inclusion. For a sheaf of commutative groups $\mathcal F$ on $\{P\}$, describe $i_*\mathcal F$ on the open sets of $X$. Determine its stalks when $P$ is a closed point.

### Complete independent solution {#d100-bridge-mastery-bgk-06-new-02-solution}

Write $A:=\mathcal F(\{P\})$. Since $\mathcal F$ is a sheaf of groups, $\mathcal F(\varnothing)=0$: the gluing condition for the empty cover gives exactly one section on the empty set. These two open sets give all the sheaf data on a one-point space.

By [Definition 6.9](bgk-reader.html#br-bgk-2019-l06-def-04), for open $U\subseteq X$,

$$
(i_*\mathcal F)(U)=\mathcal F(i^{-1}(U))
=\begin{cases}
A,&P\in U,\\
0,&P\notin U.
\end{cases}
$$

If $V\subseteq U$, there are three possibilities. If $P\in V$, both section groups are $A$ and the restriction is the identity $A\to A$. If $P\in U$ but $P\notin V$, the restriction is the unique homomorphism $A\to0$. If $P\notin U$, the restriction is $0\to0$. The possibility $P\notin U$ but $P\in V$ cannot occur. Thus the entire restriction structure is determined. This pushforward is a sheaf by [Lemma 6.10](bgk-reader.html#br-bgk-2019-l06-lem-05), which applies to every continuous map and every sheaf on its domain.

At $P$, every open neighbourhood contains $P$. All the groups forming the stalk are $A$, and all restriction homomorphisms are identities. The map $A\to(i_*\mathcal F)_P$ sends $a$ to the germ of the section $a$ on $X$. It is surjective because every germ representative comes from a copy of $A$, and injective because restrictions never identify two distinct elements. Thus

$$
(i_*\mathcal F)_P\cong A.
$$

Now suppose $\{P\}$ is closed and take $Q\ne P$. The set $X\setminus\{P\}$ is open and contains $Q$. Every open neighbourhood $U$ of $Q$ can be shrunk to $U\cap(X\setminus\{P\})$. On that smaller neighbourhood, the pushforward section group is zero. Consequently every germ representative at $Q$ becomes zero after restriction, so

$$
(i_*\mathcal F)_Q=0\qquad(Q\ne P).
$$

Thus, for a closed point $P$, this sheaf has stalk $A$ only at $P$ and zero stalk at every other point. This is the skyscraper sheaf with value $A$ at $P$.

### Pitfall and check {#d100-bridge-mastery-bgk-06-new-02-check}

Do not drop the hypothesis that $P$ is closed when concluding that the stalks away from $P$ are zero. If $Q$ lies in the closure of $\{P\}$, every open neighbourhood of $Q$ contains $P$, so the same stalk computation instead gives $A$. The zero-stalk proof uses **a neighbourhood of $Q$ not containing $P$**, not merely $Q\ne P$.

## New item 3 - Brenner Exercise 6.13: the pullback–pushforward morphism bijection {#d100-bridge-mastery-bgk-06-new-03}

Source: [Exercise 6.13 in the BGK reader](bgk-reader.html#br-bgk-2019-w06-ex13).
Frozen entity: `Topologische Räume/Stetige Abbildung/Rückzug und Vorschub/Morphismen/Aufgabe`, pageid `116425`, [revision `1081982`](https://de.wikiversity.org/w/index.php?oldid=1081982).
The exercise number follows Worksheet 6, revision `900086`.

### Source problem statement {#d100-bridge-mastery-bgk-06-new-03-problem}

Let $\varphi:X\to Y$ be continuous, $\mathcal F$ a sheaf on $X$, and $\mathcal G$ a sheaf on $Y$. Prove that there is a natural bijection

$$
\operatorname{Hom}_X(\varphi^{-1}\mathcal G,\mathcal F)
\cong
\operatorname{Hom}_Y(\mathcal G,\varphi_*\mathcal F).
$$

### Complete independent solution {#d100-bridge-mastery-bgk-06-new-03-solution}

We construct both directions, then check that they are inverse to each other. The argument first applies to sheaves of sets. If the sheaves carry commutative group structures, all maps constructed from the original homomorphisms remain homomorphisms, so the same proof applies in that category.

By [Definition 6.12](bgk-reader.html#br-bgk-2019-l06-def-05), the pullback presheaf is

$$
\mathcal P(U):=
\operatorname*{colim}_{\substack{V\subseteq Y\text{ open}\\
U\subseteq\varphi^{-1}(V)}}\mathcal G(V).
$$

Write a representative of a colimit element as $[V,s]$, with $s\in\mathcal G(V)$. Restriction to $U'\subseteq U$ retains the representative $[V,s]$. Two representatives are equal when their restrictions agree on a smaller open set still containing $\varphi(U)$. By [Definition 6.13](bgk-reader.html#br-bgk-2019-l06-def-06), $\varphi^{-1}\mathcal G=\mathcal P^a$, the sheafification of $\mathcal P$. Write $\lambda:\mathcal P\to\mathcal P^a$ for the canonical map.

We use the universal property of sheafification: every presheaf morphism $\mathcal P\to\mathcal F$, with $\mathcal F$ already a sheaf, extends uniquely to a morphism $\mathcal P^a\to\mathcal F$. The reason is that sections of $\mathcal P^a$ are locally represented by sections of $\mathcal P$; the images of these representatives agree locally on intersections, so they glue to exactly one section of $\mathcal F$. Equality of germs ensures independence of the choice of representatives or cover.

**From right to left.** Given $\theta:\mathcal G\to\varphi_*\mathcal F$, define

$$
\alpha_U:\mathcal P(U)\longrightarrow\mathcal F(U),
\qquad
[V,s]\longmapsto\theta_V(s)|_U.
$$

The formula has the correct types because $\theta_V(s)\in\mathcal F(\varphi^{-1}(V))$ and $U\subseteq\varphi^{-1}(V)$. If two representatives become equal after restriction to $W\subseteq V\cap V'$ with $U\subseteq\varphi^{-1}(W)$, compatibility of $\theta$ with restrictions shows that the two images in $\mathcal F(U)$ agree. Thus the formula is well-defined. Restriction from $U$ to $U'$ also commutes with the formula, so $\alpha$ is a presheaf morphism. The universal property gives exactly one

$$
\psi_\theta:\varphi^{-1}\mathcal G\longrightarrow\mathcal F,
\qquad \psi_\theta\lambda=\alpha.
$$

**From left to right.** Given $\psi:\varphi^{-1}\mathcal G\to\mathcal F$, every $s\in\mathcal G(V)$ determines an element $[V,s]$ of $\mathcal P(\varphi^{-1}(V))$. Set

$$
(\theta_\psi)_V(s):=
\psi_{\varphi^{-1}(V)}
\bigl(\lambda_{\varphi^{-1}(V)}([V,s])\bigr)
\in\mathcal F(\varphi^{-1}(V)).
$$

If $W\subseteq V$, the representative $[V,s]$ restricted to $\varphi^{-1}(W)$ equals $[W,s|_W]$ in the colimit. Since $\lambda$ and $\psi$ respect restrictions, this formula gives a sheaf morphism $\theta_\psi:\mathcal G\to\varphi_*\mathcal F$.

**The two constructions are inverse.** Start with $\theta$. For $s\in\mathcal G(V)$, the first construction satisfies

$$
(\theta_{\psi_\theta})_V(s)
=\alpha_{\varphi^{-1}(V)}([V,s])
=\theta_V(s).
$$

Thus it returns exactly $\theta$. Conversely, start with $\psi$ and construct $\theta_\psi$. For a representative $[V,s]\in\mathcal P(U)$, compatibility with restrictions gives

$$
\begin{aligned}
\alpha_U([V,s])
&=(\theta_\psi)_V(s)|_U\\
&=\psi_U\bigl(\lambda_U([V,s])\bigr).
\end{aligned}
$$

Hence the new morphism $\psi_{\theta_\psi}$ and $\psi$ agree after composition with $\lambda$. Uniqueness in the universal property of sheafification gives $\psi_{\theta_\psi}=\psi$.

Finally, this bijection is natural. If $u:\mathcal F\to\mathcal F'$ and $v:\mathcal G'\to\mathcal G$ are sheaf morphisms, the formulas on representatives give, respectively,

$$
\theta_{u\circ\psi}=(\varphi_*u)\circ\theta_\psi,
\qquad
\theta_{\psi\circ\varphi^{-1}v}=\theta_\psi\circ v.
$$

The first equality simply applies $u$ to the image of a section; the second replaces $[V,s']$ by $[V,v_V(s')]$. Thus the bijection commutes with postcomposition in $\mathcal F$ and precomposition in $\mathcal G$. This is the entire naturality claim and completes the proof of the required bijection.

### Pitfall and check {#d100-bridge-mastery-bgk-06-new-03-check}

Do not replace $\varphi^{-1}\mathcal G(U)$ by the single value $\mathcal G(\varphi(U))$: the image $\varphi(U)$ need not be open, and the colimit presheaf must still be sheafified. In every formula, check where a section lives before restricting it. The condition $U\subseteq\varphi^{-1}(V)$ is exactly what makes $\theta_V(s)|_U$ legitimate.
