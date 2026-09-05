---
title: "BGK 23 Mastery Exercises - Injectivity, Resolutions, and Flasque Sheaves"
stable_id: d100-bridge-mastery-bgk-23
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner and Wikiversity contributors"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_unit: 23
new_worked_solution_count: 3
source_exercise_numbers: "23.11, 23.13, 23.19"
source_authority_manifest: authority/wikiversity-bgk/unit-23/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 96fb36e19dd3e6dcef56149150ce09c238843bee08ff36503d87a55284113775
non_endorsement: "Independent editorial material; does not imply endorsement or review by the author or source institutions."
---

# BGK 23 mastery exercises {#d100-bridge-mastery-bgk-23}

The exercises below come from the course by Holger Brenner and Wikiversity contributors. The solutions and checking notes are **independent editorial material**, not public source solutions. The source freeze contains no public solution pages for these three exercises; this editorial addition does not change the negative result recorded in the source edition.

We write commutative group operations additively. A group $D$ is called divisible if, for every $n\geq1$, multiplication by $n$ on $D$ is surjective. An injective module must satisfy the extension property while preserving the specified scalar structure. The Indonesian term *flasid* means *flasque*, as in the lecture: all restriction maps of the sheaf are surjective.

## 1. Divisible as a group, but not injective as a module {#d100-bridge-mastery-bgk-23-new-01}

**Exercise source:** [Exercise 23.11](bgk-reader.html#br-bgk-2019-w23-ex11), ID br-bgk-2019-w23-ex11. Source entity *Modul/Divisible Gruppe/Nicht injektiv/Aufgabe*, [revision 837979](https://de.wikiversity.org/w/index.php?oldid=837979).

**Problem statement.** Give an example of a commutative ring $R$ and an $R$-module $M$ that is not injective, although $M$ is divisible as a commutative group.

**Editorial solution.** Take

$$
R=\mathbb Q[X],\qquad M=R.
$$

The additive group of $M$ is divisible: for every polynomial $f(X)\in\mathbb Q[X]$ and every integer $n\geq1$, the polynomial $f(X)/n$ still has rational coefficients and satisfies $n(f/n)=f$. This statement uses only addition and multiplication by integers.

To test injectivity as an $R$-module, consider the ideal inclusion $XR\subseteq R$ and the map

$$
\varphi:XR\longrightarrow M,\qquad Xf(X)\longmapsto f(X).
$$

This map is well-defined because the representation $Xf$ determines $f$ uniquely: $X$ is not a zero divisor in $\mathbb Q[X]$. For $a,f\in R$, we have $\varphi(aXf)=af=a\varphi(Xf)$, so $\varphi$ is indeed $R$-linear.

If $M$ were injective, [Definition 23.1](bgk-reader.html#br-bgk-2019-l23-def-01) would give an $R$-linear extension

$$
\psi:R\longrightarrow M,\qquad \psi|_{XR}=\varphi.
$$

Write $p(X)=\psi(1)$. By linearity, every $a\in R$ satisfies $\psi(a)=a p(X)$. In particular,

$$
1=\varphi(X)=\psi(X)=X p(X).
$$

This is impossible in $\mathbb Q[X]$: the right-hand side has constant term zero, whereas the left-hand side has constant term one. Hence $\varphi$ has no $R$-linear extension, so $M$ is not injective as an $R$-module.

**Check and pitfall.** Dividing coefficients by an integer $n$ is a legitimate operation in $M$; dividing the polynomial $1$ by $X$ is not. [Lemma 23.5](bgk-reader.html#br-bgk-2019-l23-lem-03) identifies divisibility with injectivity for commutative groups, that is, $\mathbb Z$-modules. It does not identify divisibility of the additive group with injectivity over an arbitrary larger ring $R$.

## 2. An injective resolution of length one for every commutative group {#d100-bridge-mastery-bgk-23-new-02}

**Exercise source:** [Exercise 23.13](bgk-reader.html#br-bgk-2019-w23-ex13), ID br-bgk-2019-w23-ex13. Source entity *Kommutative Gruppe/Kurze injektive Auflösung/Aufgabe*, [revision 1039002](https://de.wikiversity.org/w/index.php?oldid=1039002).

**Problem statement.** Prove that every commutative group $G$ has an injective resolution of the form

$$
0\longrightarrow G\longrightarrow I_0\longrightarrow I_1
\longrightarrow0.
$$

**Editorial solution.** We give a construction and check its exactness. Choose a generating set $S$ for $G$; the set of all elements of $G$ itself may be used. There is a surjection

$$
p:F=\mathbb Z^{(S)}\longrightarrow G
$$

sending the basis vector $e_s$ to the generator $s$. Write $H=\ker p$. The first isomorphism theorem gives $G\cong F/H$.

Embed $F$ in the rational vector space

$$
V=\mathbb Q^{(S)}.
$$

Parentheses in the superscript denote a **direct sum**: each vector has only finitely many nonzero coordinates. We can divide such a vector by every positive integer without changing its finite-support property. Thus the additive group of $V$ is divisible.

Since $H\subseteq F\subseteq V$, set

$$
I_0=V/H,\qquad I_1=V/F.
$$

Both groups are divisible. Explicitly, for a class $v+H\in V/H$ and $n\geq1$, the class $(v/n)+H$ satisfies $n((v/n)+H)=v+H$; the same argument applies modulo $F$. By [Lemma 23.5](bgk-reader.html#br-bgk-2019-l23-lem-03), every divisible commutative group is injective as a $\mathbb Z$-module. Hence $I_0$ and $I_1$ are injective in the category being used.

Define

$$
\begin{aligned}
j:F/H&\longrightarrow V/H,& f+H&\longmapsto f+H,\\
d:V/H&\longrightarrow V/F,& v+H&\longmapsto v+F.
\end{aligned}
$$

Both maps are well-defined because $H\subseteq F$. The map $j$ is injective: if the image of $f+H$ is zero in $V/H$, then $f\in H$, so the original class is zero in $F/H$. The map $d$ is surjective, since every class $v+F$ has preimage $v+H$.

Finally,

$$
\begin{aligned}
\ker d
&=\{v+H\in V/H\mid v\in F\}\\
&=F/H=\operatorname{im}j.
\end{aligned}
$$

Under the identification $G\cong F/H$, we obtain the short exact sequence

$$
0\longrightarrow G\xrightarrow{j}I_0\xrightarrow{d}I_1
\longrightarrow0
$$

with both terms $I_0,I_1$ injective, exactly as required.

**Check and pitfall.** For $G=\mathbb Z$, the construction can be chosen as $0\to\mathbb Z\to\mathbb Q\to\mathbb Q/\mathbb Z\to0$. This sequence need not split: injectivity of $I_0$ does not force its subgroup $G$ to be a direct summand. [Lemma 23.6](bgk-reader.html#br-bgk-2019-l23-lem-04) asserts splitting when the **left-hand term** of a short exact sequence is injective, not merely its middle term. The exercise's result is also specific to commutative groups; it is not a bound on the length of injective resolutions for modules over an arbitrary commutative ring.

## 3. The sheaf of all functions is flasque {#d100-bridge-mastery-bgk-23-new-03}

**Exercise source:** [Exercise 23.19](bgk-reader.html#br-bgk-2019-w23-ex19), ID br-bgk-2019-w23-ex19. Source entity *Kommutative Gruppe/Abbildungen/Garbe/Welk/Aufgabe*, [revision 1081885](https://de.wikiversity.org/w/index.php?oldid=1081885).

**Problem statement.** Let $G$ be a commutative group and $X$ a topological space. Prove that the sheaf

$$
\mathcal F(U)=\operatorname{Abb}(U,G)
$$

on $X$ is flasque. The notation $\operatorname{Abb}(U,G)$ means all set maps from $U$ to $G$, with no continuity requirement.

**Editorial solution.** Addition on $\mathcal F(U)$ is pointwise, and for open $U\subseteq V$ the restriction map is $r_{V,U}(s)=s|_U$. This is a group homomorphism and plainly satisfies the identity and composition compatibility of restrictions.

First check the sheaf property. Let $U=\bigcup_{i\in I}U_i$ be an open cover, and let functions $s_i:U_i\to G$ agree on each intersection $U_i\cap U_j$. For $x\in U$, choose an $i$ with $x\in U_i$ and set $s(x)=s_i(x)$. Agreement on intersections ensures that this value is independent of the choice of $i$. Thus $s:U\to G$ restricts to $s_i$ on each $U_i$. A function with this property is unique, since every point of $U$ lies in some $U_i$. On the empty set there is just one function $\varnothing\to G$, as the sheaf axiom requires. Thus $\mathcal F$ is indeed a sheaf of commutative groups.

Now take open sets $U\subseteq V$ and a section $s\in\mathcal F(U)$. With $0_G$ the identity element of $G$, define the function

$$
\widetilde s:V\longrightarrow G,\qquad
\widetilde s(x)=
\begin{cases}
s(x),&x\in U,\\
0_G,&x\in V\setminus U.
\end{cases}
$$

Since $\mathcal F(V)$ contains **all** functions, $\widetilde s$ is a legitimate section; we do not need $V\setminus U$ to be open. Clearly $r_{V,U}(\widetilde s)=s$. Thus every section on $U$ extends to $V$, so $r_{V,U}$ is surjective.

The argument applies to every $U\subseteq V$, including $U=\varnothing$. By [Definition 23.14](bgk-reader.html#br-bgk-2019-l23-def-04), $\mathcal F$ is flasque.

**Check and pitfall.** Extension by zero above even gives a group-homomorphism right inverse to each restriction. However, the same method does not automatically work for a sheaf of **continuous functions**: assigning zero outside $U$ can destroy continuity at the boundary of $U$. For example, $x\mapsto1/x$ on $(0,1)\subseteq\mathbb R$ has no real-valued continuous extension to all of $\mathbb R$. The absence of a continuity requirement in $\operatorname{Abb}(U,G)$ is an essential part of the proof.

## Origin and licence of the supplement {#d100-bridge-mastery-bgk-23-credit}

The problem statements and cited lecture results are credited to Holger Brenner and Wikiversity contributors. Editorial solutions prepared by **OpenAI Codex gpt-5.6-sol, Ultra.** This supplementary material is licensed under **CC BY-SA 4.0**. It claims no review or endorsement by the source author, Wikiversity, the Wikimedia Foundation, or source institutions.
