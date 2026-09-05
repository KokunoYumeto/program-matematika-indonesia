---
title: "BGK 13 Mastery - Stalks, Matrices, and Invertible Sheaves"
stable_id: d100-bridge-mastery-bgk-13
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_unit: 13
source_worksheet_revision: 1003881
source_manifest: "authority/wikiversity-bgk/unit-13/UNIT_AUTHORITY_MANIFEST.json"
source_manifest_sha256: "792935b01daf0a2ee22decd78d3f9ccb8d95719c628cdd306b66405ea1427282"
new_worked_solutions: 3
existing_source_solutions_counted: []
non_endorsement: "Independent editorial material; does not imply endorsement or human checking by the source author or source institutions."
---

# BGK 13 mastery: stalks, matrices, and invertible sheaves {#d100-bridge-mastery-bgk-13}

All three exercises come from Holger Brenner and the Wikiversity course contributors. All solutions below are independent editorial material, not public solutions by Brenner. The frozen source provides no public solutions for these three exercises; that historical status is unchanged. The translated problem text and this editorial material remain under CC BY-SA 4.0. Production provenance: OpenAI Codex gpt-5.6-sol, Ultra. No endorsement by the source author or human checking is implied.

The Indonesian term *ruang bergelanggang*, rendered here as *ringed space*, follows the edition glossary and denotes the object called *ruang berdering* in the Indonesian source translation. This change in terminology does not add a requirement that the stalk rings be local.

## New item 1: the module structure on a stalk {#d100-bridge-mastery-bgk-13-new-01}

Source: [BGK Exercise 13.5](bgk-reader.html#br-bgk-2019-w13-ex05), identifier `Beringter Raum/Modul/Halm/Aufgabe`, [revision 1082395](https://de.wikiversity.org/w/index.php?oldid=1082395).

### Source exercise {#d100-bridge-mastery-bgk-13-new-01-problem}

Let $\mathcal F$ be an $\mathcal O_X$-module on a ringed space $(X,\mathcal O_X)$. Prove that, for every $P\in X$, the stalk $\mathcal F_P$ is an $\mathcal O_{X,P}$-module.

### Independent solution {#d100-bridge-mastery-bgk-13-new-01-solution}

An element $a_P\in\mathcal O_{X,P}$ is represented by a section $a\in\mathcal O_X(U)$ on an open neighbourhood $U$ of $P$. Likewise, $s_P\in\mathcal F_P$ has a representative $s\in\mathcal F(V)$ for some open neighbourhood $V$ of $P$. We define

$$
a_Ps_P:=\bigl((a|_{U\cap V})(s|_{U\cap V})\bigr)_P.
$$

The multiplication on the right is defined because $\mathcal F(U\cap V)$ is a module over $\mathcal O_X(U\cap V)$.

We must check that the result is independent of the representatives. Suppose $a'$ is another representative of $a_P$ and $s'$ another representative of $s_P$. Equality of germs means that on a neighbourhood $W_a$ of $P$, the restrictions of $a$ and $a'$ agree, and on a neighbourhood $W_s$, the restrictions of $s$ and $s'$ agree. Intersect these neighbourhoods with all the representative domains. On this intersection, the two products agree. Compatibility of scalar multiplication with restrictions, which is part of [Definition 13.5](bgk-reader.html#br-bgk-2019-l13-def-03), ensures that the original two products determine the same germ. Thus the operation is well-defined.

Addition on $\mathcal F_P$ is constructed in the same way: restrict two representatives to a common neighbourhood, then add them. The abelian group axioms hold because each axiom involves only finitely many representatives; they can all be restricted to a common neighbourhood where the axiom already holds in $\mathcal F(W)$.

The same method proves the module axioms. For $a_P,b_P\in\mathcal O_{X,P}$ and $s_P,t_P\in\mathcal F_P$, choose representatives of all of them on a single $W$. The axioms for the section module on $W$ give

$$
\begin{aligned}
(a_P+b_P)s_P&=a_Ps_P+b_Ps_P,\\
a_P(s_P+t_P)&=a_Ps_P+a_Pt_P,\\
(a_Pb_P)s_P&=a_P(b_Ps_P),\\
1_Ps_P&=s_P.
\end{aligned}
$$

Hence $\mathcal F_P$ has a natural $\mathcal O_{X,P}$-module structure. No assumption that the ringed space is locally ringed is required.

### Checks and common mistakes {#d100-bridge-mastery-bgk-13-new-01-check}

Multiplication of representatives with different domains must be preceded by restriction to a common neighbourhood. Nor is the stalk $\mathcal F_P$ the fibre: on a locally ringed space, the fibre defined in [Definition 13.8](bgk-reader.html#br-bgk-2019-l13-def-06) is $\mathcal F_P\otimes_{\mathcal O_{X,P}}\kappa(P)$, which still requires a change of scalars to the residue field.

## New item 2: unit determinants and isomorphisms of free sheaves {#d100-bridge-mastery-bgk-13-new-02}

Source: [BGK Exercise 13.10](bgk-reader.html#br-bgk-2019-w13-ex10), identifier `Beringter Raum/Freier Modul/Festlegungssatz/Determinante/Isomorphismus/Aufgabe`, [revision 1097130](https://de.wikiversity.org/w/index.php?oldid=1097130).

### Source exercise {#d100-bridge-mastery-bgk-13-new-02-problem}

Let $(X,\mathcal O_X)$ be a ringed space and

$$
s_i=(s_{i1},\ldots,s_{in})\in\Gamma(X,\mathcal O_X)^n,
\qquad 1\leq i\leq n.
$$

Prove that $\det(s_{ij})$ is a unit in $\Gamma(X,\mathcal O_X)$ if and only if the associated homomorphism

$$
\varphi:\mathcal O_X^n\longrightarrow\mathcal O_X^n,
\qquad e_i\longmapsto s_i,
$$

is an isomorphism.

### Independent solution {#d100-bridge-mastery-bgk-13-new-02-solution}

Write $R=\Gamma(X,\mathcal O_X)$ and $A=(s_{ij})$. [Theorem 13.10](bgk-reader.html#br-bgk-2019-l13-thm-02) ensures that these sections determine exactly one homomorphism of sheaves of modules. If coordinate vectors are written as columns, its matrix is $B=A^{\mathsf T}$, since the $i$th column contains the coordinates of $\varphi(e_i)=s_i$. In particular, $\det B=\det A$.

Suppose $d=\det A$ is a unit in $R$. The adjugate identity for matrices over a commutative ring gives

$$
B\operatorname{adj}(B)=\operatorname{adj}(B)B=dI_n.
$$

Hence the matrix

$$
C=d^{-1}\operatorname{adj}(B)\in M_n(R)
$$

satisfies $BC=CB=I_n$. The entries of $C$ are global sections. Restricting them to each open $U$ gives a $\Gamma(U,\mathcal O_X)$-module homomorphism on $\Gamma(U,\mathcal O_X)^n$. These homomorphisms are compatible with restrictions and therefore determine a sheaf homomorphism $\psi:\mathcal O_X^n\to\mathcal O_X^n$. The matrix identities remain valid after restriction, so $\varphi\psi=\psi\varphi=\operatorname{id}$. Thus $\varphi$ is an isomorphism.

Conversely, suppose $\varphi$ is an isomorphism of sheaves of modules with inverse $\psi$. Evaluating both composites on $X$ gives inverse $R$-module homomorphisms on $R^n$. The matrix of $\psi_X$ in the standard basis is some $C\in M_n(R)$, so

$$
BC=CB=I_n.
$$

Taking determinants gives

$$
\det A\cdot\det C=\det B\cdot\det C=1.
$$

Hence $\det A$ is a unit, with inverse $\det C$. Both directions have been proved without treating the global section ring as a field.

### Checks and common mistakes {#d100-bridge-mastery-bgk-13-new-02-check}

The condition is a *unit* determinant, not merely a nonzero determinant. The matrix $(2)$ over $\mathbb Z$, for example, is not invertible over $\mathbb Z$. The transpose above merely records the row/column convention; transposition does not change the determinant. The converse uses an already existing sheaf inverse, not an assumption that any isomorphism on global sections gives an isomorphism of arbitrary sheaves.

## New item 3: the dual of an invertible sheaf {#d100-bridge-mastery-bgk-13-new-03}

Source: [BGK Exercise 13.16](bgk-reader.html#br-bgk-2019-w13-ex16), identifier `Beringter Raum/Invertierbare Garben/Duale Garbe/Invertierbar/Aufgabe`, [revision 1082386](https://de.wikiversity.org/w/index.php?oldid=1082386).

### Source exercise {#d100-bridge-mastery-bgk-13-new-03-problem}

Let $\mathcal L$ be an invertible sheaf on a ringed space $(X,\mathcal O_X)$. Prove that the dual sheaf

$$
\mathcal L^*=\mathcal Hom(\mathcal L,\mathcal O_X)
$$

is also invertible.

### Independent solution {#d100-bridge-mastery-bgk-13-new-03-solution}

By [Definition 13.17](bgk-reader.html#br-bgk-2019-l13-def-12), there is an open cover $X=\bigcup_iU_i$ with $\mathcal L|_{U_i}\cong\mathcal O_X|_{U_i}$. Choose a local basis $e_i\in\mathcal L(U_i)$ corresponding to the section $1$ under this trivialisation. For each open $V\subseteq U_i$, every section of $\mathcal L(V)$ is uniquely written as $b e_i|_V$, with $b\in\mathcal O_X(V)$.

A dual section on $V$ is not merely a function on global sections: by [Definition 13.13](bgk-reader.html#br-bgk-2019-l13-def-09), it is a homomorphism of sheaves of modules

$$
\lambda:\mathcal L|_V\longrightarrow\mathcal O_X|_V.
$$

This homomorphism determines an element $a=\lambda_V(e_i|_V)\in\mathcal O_X(V)$. Conversely, each $a\in\mathcal O_X(V)$ determines such a homomorphism: on each $W\subseteq V$, define

$$
\lambda^a_W(b e_i|_W)=b(a|_W).
$$

Uniqueness of representation in the basis $e_i|_W$ makes this formula well-defined. It is $\mathcal O_X(W)$-linear and compatible with every restriction. The two constructions are inverse. Moreover, when $V$ is restricted to a smaller open set, evaluation on $e_i$ and the construction of $\lambda^a$ restrict in the same way. Thus we obtain an isomorphism of *sheaves* of modules

$$
\mathcal L^*|_{U_i}\cong\mathcal O_X|_{U_i}.
$$

The same cover $\{U_i\}$ therefore shows that $\mathcal L^*$ is locally free of rank one, that is, invertible.

We can also check its transition maps. On $U_i\cap U_j$, write $e_j=g_{ij}e_i$, with $g_{ij}$ a unit. If $e_i^*$ is the dual basis sending $e_i$ to $1$, then

$$
e_j^*=g_{ij}^{-1}e_i^*,
$$

because $(g_{ij}^{-1}e_i^*)(g_{ij}e_i)=1$. Thus the dual transitions are also multiplication by units, as invertibility requires.

### Checks and common mistakes {#d100-bridge-mastery-bgk-13-new-03-check}

The proof chooses a basis only on each $U_i$, not a global basis. Invertibility of $\mathcal L^*$ does not say that the sheaf is globally trivial. Also distinguish the sheaf $\mathcal Hom(\mathcal L,\mathcal O_X)$ from a homomorphism module formed only from the two modules of global sections: the local computation above uses homomorphisms on all smaller open sets.
