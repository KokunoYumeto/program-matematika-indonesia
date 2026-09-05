---
title: "BGK 26 Mastery Exercises - Čech Cohomology"
stable_id: d100-bridge-mastery-bgk-26
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision: 619292
source_manifest: authority/wikiversity-bgk/unit-26/UNIT_AUTHORITY_MANIFEST.json
source_manifest_sha256: 7ed3c9a3a480daeb4332e9de8ff2251e43d3a43845df5744ef16aabac5f2c6b4
new_solution_count: 3
selected_source_exercises: "26.2, 26.6, 26.8"
non_endorsement: "Independent editorial material; does not imply endorsement or human review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 26 mastery exercises {#d100-bridge-mastery-bgk-26}

The three exercises below come from Holger Brenner's course and Wikiversity contributions whose revision identities are preserved in the edition. **The following solutions are new editorial material, not public solutions by Brenner or translations of source solutions.** The source record stating that no public solutions exist remains applicable.

This new material was prepared by **OpenAI Codex gpt-5.6-sol, Ultra.** and is licensed under **CC BY-SA 4.0**. Source attribution and licences are preserved; no endorsement or human review by the author or source institutions is claimed.

## 1. Zeroth cohomology and the gluing axiom {#d100-bridge-mastery-bgk-26-new-01}

**Source exercise:** [Exercise 26.2 in the reader](bgk-reader.html#br-bgk-2019-w26-ex02).
Exact identifier: `Cech-Kohomologie/0/Globale Auswertung/Aufgabe`; [source revision 1082005](https://de.wikiversity.org/w/index.php?oldid=1082005).
Its placement is frozen in Worksheet 26, revision 619292.

**Statement.** Let $X=\bigcup_{i\in I}U_i$ be an open cover of a topological space $X$, and $\mathcal G$ a sheaf of commutative groups on $X$. Prove that
$$
\check H^0(\mathcal U,\mathcal G)\cong\Gamma(X,\mathcal G).
$$
The equality in the source statement is read as the canonical identification by restriction of global sections, not literal equality of two set constructions.

**Editorial solution.** Order the index set as in [Definition 26.3](bgk-reader.html#br-bgk-2019-l26-def-01). The first two terms of the complex are
$$
\check C^0=\prod_i\Gamma(U_i,\mathcal G),\qquad
\check C^1=\prod_{i<j}\Gamma(U_i\cap U_j,\mathcal G).
$$
The first differential has components
$$
(\delta_0(s))_{ij}
=s_j|_{U_i\cap U_j}-s_i|_{U_i\cap U_j}.
$$
Since the complex used starts in degree $0$, no nonzero coboundaries enter degree $0$. Hence
$$
\check H^0(\mathcal U,\mathcal G)=\ker\delta_0.
$$

Define the homomorphism
$$
\rho:\Gamma(X,\mathcal G)\longrightarrow\check C^0,\qquad
t\longmapsto(t|_{U_i})_i.
$$
Two restrictions of the same section certainly agree on every intersection. Thus $\rho(t)\in\ker\delta_0$.

Conversely, take $(s_i)_i\in\ker\delta_0$. The equation $\delta_0(s)=0$ says exactly that
$$
s_i|_{U_i\cap U_j}=s_j|_{U_i\cap U_j}
$$
for all $i,j$. The sheaf gluing axiom gives a section $t\in\Gamma(X,\mathcal G)$ with $t|_{U_i}=s_i$ for every $i$. The uniqueness axiom ensures that this section is unique. Thus $\rho$ is surjective onto the kernel and also injective: if all restrictions of $t$ are zero, uniqueness of gluing forces $t=0$.

Restriction preserves addition. Gluing also preserves it, because the section gluing the family $(s_i+s'_i)$ is the sum of the two glued sections, again by uniqueness. Therefore $\rho$ is the required group isomorphism. This proof requires neither a finite cover, connectedness of the space, nor acyclicity.

**Check and pitfall.** For a single open set $U_1=X$, we have $\check C^1=0$ and immediately obtain $\check H^0=\Gamma(X,\mathcal G)$ (and, for this singleton cover, $\check H^1=0$). For a general cover, do not conclude that $\check H^1=0$ from the degree-$0$ argument: the sheaf axiom gives exactness in degree $0$, not automatically in every degree.

## 2. A constant sheaf on an irreducible space {#d100-bridge-mastery-bgk-26-new-02}

**Source exercise:** [Exercise 26.6 in the reader](bgk-reader.html#br-bgk-2019-w26-ex06).
Exact identifier: `Irreduzibler Raum/Konstante Garbe/Cech-Kohomologie/Aufgabe`; [source revision 1081578](https://de.wikiversity.org/w/index.php?oldid=1081578).
Its placement is frozen in Worksheet 26, revision 619292.

**Statement.** Let $X$ be an irreducible topological space and $\mathcal G=\underline G$ the constant sheaf associated to a commutative group $G$. Determine the Čech complex and its cohomology for a finite open cover $\mathcal U=(U_i)_{i\in I}$.

**Editorial solution.** We use the usual convention that an irreducible space is nonempty. If another convention allows the empty space, the case $X=\varnothing$ is separate: all section groups and cohomology groups are zero. Empty members of the cover may be removed without changing the complex, since every intersection involving them contributes the zero group.

Label the remaining cover indices $\{0,1,\ldots,m-1\}$, with $m\geq1$. In an irreducible space, any two nonempty open sets intersect. By induction, every finite intersection $U_J$ is also nonempty. Moreover, $U_J$ is irreducible: two nonempty relatively open subsets of it are two nonempty open subsets of $X$, so they intersect. In particular, $U_J$ is connected.

Sections of the constant sheaf $\underline G$ on an open set can be viewed as locally constant functions to $G$ equipped with the discrete topology. On a connected space such a function is constant: if two different values occurred, the preimage of one value and its complement would separate the space into two nonempty open sets. Thus
$$
\Gamma(U_J,\underline G)=G,
$$
and all restrictions between nonempty intersections are identities on $G$.

The complex is therefore
$$
0\longrightarrow G^m
\xrightarrow{\delta_0}G^{\binom m2}
\xrightarrow{\delta_1}\cdots
\xrightarrow{\delta_{m-2}}G
\longrightarrow0,
$$
with $G^m$ in degree $0$ and the last $G$ in degree $m-1$. Uniformly,
$$
\check C^q=G^{\binom m{q+1}},\qquad
(\delta_q s)_{i_0\ldots i_{q+1}}
=\sum_{r=0}^{q+1}(-1)^r
s_{i_0\ldots\widehat{i_r}\ldots i_{q+1}}.
$$
Terms with $q\geq m$ are zero. For $m=1$, the complex consists only of $G$ in degree $0$.

Zeroth cohomology is the diagonal
$$
\ker\delta_0=\{(g,\ldots,g):g\in G\}\cong G.
$$
To show that all positive cohomology vanishes, we give an explicit homotopy. For $q\geq1$, define $h_q:\check C^q\to\check C^{q-1}$ by
$$
(h_qs)_{i_0\ldots i_{q-1}}=
\begin{cases}
s_{0i_0\ldots i_{q-1}},&0\notin\{i_0,\ldots,i_{q-1}\},\\
0,&0\in\{i_0,\ldots,i_{q-1}\}.
\end{cases}
$$
Putting index $0$ first requires no additional restrictions: all the groups involved have been identified with $G$.

Check a tuple $L=(i_0<\cdots<i_q)$. If $0\in L$, the component $(h_{q+1}\delta_qs)_L$ is zero. In $(\delta_{q-1}h_qs)_L$, only the term omitting index $0$ is nonzero, and that term equals $s_L$.

If $0\notin L$, then
$$
(h_{q+1}\delta_qs)_L
=(\delta_qs)_{0i_0\ldots i_q}
=s_L+\sum_{r=0}^{q}(-1)^{r+1}s_{0,L\setminus\{i_r\}},
$$
whereas
$$
(\delta_{q-1}h_qs)_L
=\sum_{r=0}^{q}(-1)^r s_{0,L\setminus\{i_r\}}.
$$
The two alternating sums cancel. In both cases,
$$
\delta_{q-1}h_q+h_{q+1}\delta_q=\operatorname{id}_{\check C^q}.
$$
If $\delta_qs=0$, this equation gives $s=\delta_{q-1}(h_qs)$. Thus every positive-degree cocycle is a coboundary, and
$$
\boxed{\check H^0(\mathcal U,\underline G)\cong G,\qquad
\check H^q(\mathcal U,\underline G)=0\quad(q\geq1).}
$$

**Check and pitfall.** For $m=2$, the complex is $G\oplus G\to G$, $(a,b)\mapsto b-a$; the kernel is the diagonal and the image is all of $G$. Irreducibility is used to ensure that all intersections are nonempty and connected. Connectedness of $X$ alone does not ensure this. Also note the last degree $m-1$: the definition of $\check C^q$ uses $q+1$ indices, not $q$ indices.

## 3. Solving a cocycle on two affine open sets {#d100-bridge-mastery-bgk-26-new-03}

**Source exercise:** [Exercise 26.8 in the reader](bgk-reader.html#br-bgk-2019-w26-ex08).
Exact identifier: `Affines Schema/Zweierüberdeckung/Strukturgabe/Cech-Kohomologie/Aufgabe`; [source revision 1038046](https://de.wikiversity.org/w/index.php?oldid=1038046).
The spelling `Strukturgabe` in the source identifier is preserved. Its placement is frozen in Worksheet 26, revision 619292.

**Statement.** Let $R$ be a commutative ring and
$$
X=\operatorname{Spek}(R)=D(f)\cup D(g).
$$
Prove that
$$
\check H^1(\{D(f),D(g)\},\mathcal O_X)=0.
$$

**Editorial solution.** Ordering $D(f)$ before $D(g)$, the Čech complex of the structure sheaf is
$$
0\longrightarrow R_f\oplus R_g
\xrightarrow{\delta_0}R_{fg}\longrightarrow0,\qquad
\delta_0(a,b)=b-a.
$$
Here both terms on the right are restricted to $D(fg)$ before subtraction. There are no intersections with three indices, so every element of $R_{fg}$ is a cocycle and
$$
\check H^1=R_{fg}/\operatorname{im}\delta_0.
$$
We will explicitly write every cocycle as a coboundary.

The cover condition gives
$$
\varnothing=X\setminus(D(f)\cup D(g))=V(f,g).
$$
If the ideal $(f,g)$ were proper, it would be contained in a maximal ideal, giving a point of $V(f,g)$, a contradiction. Thus $(f,g)=R$. More generally, for every integer $N\geq1$, we have $V(f^N,g^N)=V(f,g)=\varnothing$, so there are $u,v\in R$ with
$$
u f^N+v g^N=1.
$$

Take $c\in R_{fg}$ and write
$$
c=\frac{r}{(fg)^N}
$$
for some $r\in R$ and $N\geq1$. Even an element with denominator of exponent zero can be written this way by multiplying numerator and denominator by $fg$. In $R_{fg}$, the equality above yields
$$
c=\frac{r(uf^N+vg^N)}{f^Ng^N}
=\frac{ur}{g^N}+\frac{vr}{f^N}.
$$
Define
$$
a=-\frac{vr}{f^N}\in R_f,\qquad
b=\frac{ur}{g^N}\in R_g.
$$
Then
$$
\delta_0(a,b)=b-a
=\frac{ur}{g^N}+\frac{vr}{f^N}=c.
$$
Thus $\delta_0$ is surjective and the quotient group is zero.

All equalities take place in localisations, so they require neither that $R$ be an integral domain nor that $f,g$ be non-zero-divisors. If $R$ is the zero ring, all modules in the complex are also zero and the conclusion remains valid.

**Check and pitfall.** For $R=\mathbb Z$, $f=2$, $g=3$, the identity $(-1)2+1\cdot3=1$ gives
$$
\frac16=-\frac13+\frac12
=\delta_0\!\left(-\frac12,-\frac13\right).
$$
If $D(f)\cup D(g)$ does not cover the whole spectrum, the equation $uf^N+vg^N=1$ is unavailable. For example, the cover of the punctured plane by $D(X)$ and $D(Y)$ does not satisfy this hypothesis on all of $\operatorname{Spek}(R[X,Y])$; Exercise 27.2 instead exhibits first cohomology that can be nonzero.
