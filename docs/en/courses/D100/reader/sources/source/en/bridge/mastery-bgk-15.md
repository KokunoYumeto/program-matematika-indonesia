---
title: "BGK 15 Mastery Exercises - Sheaves on Projective Schemes"
stable_id: d100-bridge-mastery-bgk-15
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner and Wikiversity contributors"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_unit: 15
new_worked_solution_count: 3
source_exercise_numbers: "15.7, 15.12, 15.13"
source_authority_manifest: authority/wikiversity-bgk/unit-15/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: 72d54d10452a64b9702bfd56edf58a716a04a0185b77d8b2cd029dd7fbb88b95
non_endorsement: "Independent editorial material; does not imply endorsement or review by the author or source institutions."
---

# BGK 15 mastery exercises {#d100-bridge-mastery-bgk-15}

The following three exercises come from the course by Holger Brenner and Wikiversity contributors. The complete solutions and checking notes are **independent editorial material**, not public source solutions or translations of Brenner's solutions. Within the frozen source scope, none of the three exercises has a public solution page. This addition does not change that record.

This material uses the source notation: $\widehat M$ is the sheaf on $\operatorname{Proj}(R)$ associated to a graded module $M$; this notation is distinguished from $\widetilde M$ on the affine spectrum.

## 1. Different modules, the same projective sheaf {#d100-bridge-mastery-bgk-15-new-01}

**Exercise source:** [Exercise 15.7](bgk-reader.html#br-bgk-2019-w15-ex07), ID br-bgk-2019-w15-ex07. Source entity *Graduierter Ring/Moduln/Realisierung auf Proj/Aufgabe*, [revision 1081620](https://de.wikiversity.org/w/index.php?oldid=1081620).

**Problem statement.** Let $R$ be a $\mathbb Z$-graded ring and $Y=\operatorname{Proj}(R)$. Show that nonisomorphic graded $R$-modules can give isomorphic sheaves of $\mathcal O_Y$-modules.

**Editorial solution.** The word *can* asks for an example of this phenomenon. Take a field $K$ and the standard graded ring

$$
R=K[X_0,X_1],\qquad Y=\mathbb P_K^1.
$$

Define three graded modules

$$
T=R/(X_0,X_1),\qquad M=R,\qquad N=R\oplus T.
$$

The module $T$ is isomorphic to $K$ in degree $0$, with all other graded components zero. Hence

$$
\dim_K M_0=1,\qquad \dim_K N_0=2.
$$

A graded module isomorphism preserves every graded component, so $M$ and $N$ are not isomorphic as graded modules. They remain nonisomorphic even after forgetting the grading: $N$ has a nonzero element $(0,\overline 1)$ annihilated by $X_0$, whereas multiplication by $X_0$ in the integral domain $R=M$ is injective.

Now consider the standard cover

$$
Y=D_+(X_0)\cup D_+(X_1).
$$

Since $X_iT=0$, the localisation $T_{X_i}$ is the zero module. Indeed, $X_i$ is invertible in this localised module, so every $t/1$ satisfies

$$
\frac t1=X_i^{-1}\frac{X_it}{1}=0.
$$

By [Lemma 15.3(2)](bgk-reader.html#br-bgk-2019-l15-lem-02), the sheaf $\widehat T$ on $D_+(X_i)$ is associated to $(T_{X_i})_0=0$. Thus $\widehat T$ is zero on both members of the cover, and therefore on all of $Y$.

The projection $\pi:N\to R$, $(r,t)\mapsto r$, induces a morphism $\widehat\pi:\widehat N\to\widehat R$. On each $D_+(X_i)$, this morphism comes from the isomorphism

$$
(N_{X_i})_0
=(R_{X_i})_0\oplus(T_{X_i})_0
=(R_{X_i})_0.
$$

Its local inverse comes from $r\mapsto(r,0)$, so these inverses are compatible on the intersection. Hence

$$
\widehat N\cong\widehat R=\mathcal O_Y=\widehat M.
$$

This is the required pair. The component $T$ is visible in the graded module but disappears in every localisation used by the projective cover.

**Check and pitfall.** Do not conclude that $T=0$ merely because $\widehat T=0$. In this example $\overline1\in T$ is clearly nonzero. What vanish are all the $(T_{X_i})_0$. This example proves the possibility requested by the exercise; it does not say that all different modules have the same sheaf.

## 2. Ten cubic sections on the projective plane {#d100-bridge-mastery-bgk-15-new-02}

**Exercise source:** [Exercise 15.12](bgk-reader.html#br-bgk-2019-w15-ex12), ID br-bgk-2019-w15-ex12. Source entity *Getwistete Strukturgarbe/Projektive Ebene/Grad 3/Basis/Aufgabe*, [revision 659923](https://de.wikiversity.org/w/index.php?oldid=659923).

**Problem statement.** For a field $K$, give an explicit basis of

$$
\Gamma\bigl(\mathbb P_K^2,\mathcal O_{\mathbb P_K^2}(3)\bigr)
$$

as a vector space over $K$, then determine its dimension.

**Editorial solution.** [Example 15.5](bgk-reader.html#br-bgk-2019-l15-exm-01) applies to projective space of dimension at least one over a field. With $d=2$ and $\ell=3$, it gives the identification

$$
\Gamma\bigl(\mathbb P_K^2,\mathcal O_{\mathbb P_K^2}(3)\bigr)
\cong K[X_0,X_1,X_2]_3.
$$

The right-hand side is the space of homogeneous polynomials of total degree $3$. Its monomials correspond to triples of nonnegative integers $(a_0,a_1,a_2)$ satisfying $a_0+a_1+a_2=3$. The complete list gives the basis

$$
\begin{aligned}
\mathcal B=\{&X_0^3,\ X_1^3,\ X_2^3,\\
&X_0^2X_1,\ X_0^2X_2,\ X_1^2X_0,\\
&X_1^2X_2,\ X_2^2X_0,\ X_2^2X_1,\\
&X_0X_1X_2\}.
\end{aligned}
$$

There are three exponent patterns: $(3,0,0)$ with its three placements; $(2,1,0)$ with its six placements; and $(1,1,1)$. Thus the list has $3+6+1=10$ members.

To prove that the list is indeed a basis, not merely a set of ten sections, take a homogeneous polynomial $F$ of degree $3$. Its monomial expansion writes $F$ as a linear combination of members of $\mathcal B$. If a linear combination of members of $\mathcal B$ is zero, every monomial coefficient must vanish, since monomial expansions in a polynomial ring are unique. Thus these elements are linearly independent and span the whole space. Therefore

$$
\dim_K\Gamma\bigl(\mathbb P_K^2,\mathcal O_{\mathbb P_K^2}(3)\bigr)=10.
$$

Locally on $D_+(X_i)$, a polynomial $F$ can be written as

$$
F=\left(\frac{F}{X_i^3}\right)X_i^3.
$$

Here $F/X_i^3$ is a regular function of degree zero, while $X_i^3$ is a local generator of the sheaf $\mathcal O(3)$. This expression explains how the homogeneous polynomial represents a section and why the global identification above does not claim that $F$ is an ordinary global regular function on $\mathbb P_K^2$.

**Check and pitfall.** The counting formula $\binom{3+2}{2}=10$ checks the number. Do not include monomials of lower degree: the degree is exactly $3$, not at most $3$. The argument does not divide by $2$ or $3$, so it remains valid in every characteristic.

## 3. Tensoring two twists adds their degrees {#d100-bridge-mastery-bgk-15-new-03}

**Exercise source:** [Exercise 15.13](bgk-reader.html#br-bgk-2019-w15-ex13), ID br-bgk-2019-w15-ex13. Source entity *Projektives Spektrum/Getwistete Strukturgarben/Tensorierung/Aufgabe*, [revision 1097158](https://de.wikiversity.org/w/index.php?oldid=1097158).

**Problem statement.** Let $R$ be a standard graded commutative ring and $Y=\operatorname{Proj}(R)$. For $\ell,m\in\mathbb Z$, prove

$$
\mathcal O_Y(\ell)\otimes_{\mathcal O_Y}\mathcal O_Y(m)
\cong\mathcal O_Y(\ell+m).
$$

**Editorial solution.** If $Y$ is empty, the statement holds immediately for sheaves on the empty space. Otherwise, choose degree-one generators $x_i$ of $R$ as an algebra over $R_0$. The sets $U_i=D_+(x_i)$ cover $Y$. Write $A_i=(R_{x_i})_0$, so $U_i=\operatorname{Spek}(A_i)$.

With the lecture's shift convention, the sheaf $\mathcal O_Y(n)$ on $U_i$ is associated to the module

$$
(R_{x_i})_n=A_i x_i^n.
$$

This equality holds for every $n\in\mathbb Z$, including $n<0$: $x_i$ is invertible in $R_{x_i}$, and dividing a degree-$n$ element by $x_i^n$ gives a degree-zero element. Thus $x_i^n$ is a basis of this free rank-one module on a nonempty chart. This is the trivialisation in [Lemma 15.6](bgk-reader.html#br-bgk-2019-l15-lem-03).

Multiplication in the graded localised ring defines the map

$$
\begin{aligned}
\mu_i:(A_ix_i^\ell)\otimes_{A_i}(A_ix_i^m)
&\longrightarrow A_ix_i^{\ell+m},\\
(a x_i^\ell)\otimes(b x_i^m)&\longmapsto abx_i^{\ell+m}.
\end{aligned}
$$

This map is $A_i$-linear and respects the tensor relation $(ca x_i^\ell)\otimes(bx_i^m)=(a x_i^\ell)\otimes(cb x_i^m)$. Its inverse is explicitly

$$
\nu_i(c x_i^{\ell+m})=(c x_i^\ell)\otimes x_i^m.
$$

The composite $\mu_i\nu_i$ is the identity. Conversely,

$$
\nu_i\mu_i((a x_i^\ell)\otimes(bx_i^m))
=(abx_i^\ell)\otimes x_i^m
=(a x_i^\ell)\otimes(bx_i^m),
$$

so $\nu_i\mu_i$ is also the identity. Passing to associated sheaves gives the desired isomorphism on $U_i$.

We must still check that these local isomorphisms glue. On $U_i\cap U_j$, the element $x_j/x_i$ is a degree-zero unit, and the local bases are related by

$$
x_j^n=\left(\frac{x_j}{x_i}\right)^n x_i^n.
$$

For the tensor product, the change-of-basis factor is $(x_j/x_i)^\ell(x_j/x_i)^m=(x_j/x_i)^{\ell+m}$, exactly the change-of-basis factor for the target sheaf. Thus $\mu_i$ and $\mu_j$ give the same map on the intersection. They glue to a global morphism

$$
\mu:\mathcal O_Y(\ell)\otimes_{\mathcal O_Y}\mathcal O_Y(m)
\longrightarrow\mathcal O_Y(\ell+m).
$$

This morphism is an isomorphism on an open cover, hence a global isomorphism.

**Check and pitfall.** Taking $m=-\ell$ gives $\mathcal O_Y(\ell)\otimes\mathcal O_Y(-\ell)\cong\mathcal O_Y$. The argument uses invertibility of $x_i$ only *on the chart* $D_+(x_i)$, not an assumption that $x_i$ is a global unit. Standard grading provides the cover by degree-one elements; this hypothesis cannot be dropped from the proof.

## Origin and licence of the supplement {#d100-bridge-mastery-bgk-15-credit}

The problem statements remain credited to Holger Brenner and Wikiversity contributors through the source identities above. Editorial solutions prepared by **OpenAI Codex gpt-5.6-sol, Ultra.** This supplement is licensed under **CC BY-SA 4.0**. It is not an official publication or a set of solutions reviewed by the source author, and it implies no endorsement by the author, Wikiversity, or the Wikimedia Foundation.
