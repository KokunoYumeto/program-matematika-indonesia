---
title: "BGK 27 Mastery Exercises - Projective Cohomology"
stable_id: d100-bridge-mastery-bgk-27
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision: 1070033
source_manifest: authority/wikiversity-bgk/unit-27/UNIT_AUTHORITY_MANIFEST.json
source_manifest_sha256: b6c2a7687ee2fcc20e6f2b5f58f1f97a665a8c1f9201d11308bb84f62a79c089
new_solution_count: 3
selected_source_exercises: "27.2, 27.6, 27.10"
non_endorsement: "Independent editorial material; does not imply endorsement or human review by Holger Brenner, Wikiversity, the Wikimedia Foundation, or the source institutions."
---

# BGK 27 mastery exercises {#d100-bridge-mastery-bgk-27}

The following exercises come from Holger Brenner and Wikiversity contributions frozen in the edition. **Their solutions are new editorial material, not public solutions by Brenner or translations of source solutions.** The source files recording the absence of public solutions are unchanged.

New material prepared by **OpenAI Codex gpt-5.6-sol, Ultra.** Licence: **CC BY-SA 4.0**, with source credits and licences preserved. No endorsement or human review by the author or source institutions is claimed. Each exercise is solved using material up to Unit 27.

## 1. Three monomial components in the Čech complex {#d100-bridge-mastery-bgk-27-new-01}

**Source exercise:** [Exercise 27.2 in the reader](bgk-reader.html#br-bgk-2019-w27-ex02).
Exact identifier: `Polynomring/2/Cech-Komplex/Monom/Aufgabe`; [source revision 1037476](https://de.wikiversity.org/w/index.php?oldid=1037476).
Its placement is frozen in Worksheet 27, revision 1070033.

**Statement.** Let $A=R[X,Y]$ for a commutative ring $R$. Determine the Čech complex of the structure sheaf for the standard cover of the punctured plane for the monomials $X^2Y^3$, $X^5Y^{-4}$, and $X^{-3}Y^{-6}$. Determine its homology in each case.

**Editorial solution.** The space being covered is
$$
U=\operatorname{Spek}(A)\setminus V(X,Y)=D(X)\cup D(Y),
$$
not the whole affine plane. Ordering $D(X)$ before $D(Y)$, the complex is
$$
0\longrightarrow A_X\oplus A_Y
\xrightarrow{\delta_0}A_{XY}\longrightarrow0,\qquad
\delta_0(a,b)=b-a.
$$
The cohomological degrees of the two nonzero terms are $0$ and $1$. The homology requested in the source exercise is computed with this cohomological grading.

Write
$$
A_X=R[X,X^{-1},Y],\quad
A_Y=R[X,Y,Y^{-1}],\quad
A_{XY}=R[X,X^{-1},Y,Y^{-1}].
$$
The differential preserves each exponent pair. For a monomial $m=X^\alpha Y^\beta$, the component in $A_X$ exists exactly when $\beta\geq0$; the component in $A_Y$ exists exactly when $\alpha\geq0$. The component in $A_{XY}$ always exists. Each existing component is the free module $Rm$ on one generator, even if $R$ has zero divisors.

**Case $m=X^2Y^3$.** This monomial occurs in all three localisations, so its component complex is
$$
0\longrightarrow Rm\oplus Rm
\xrightarrow{(am,bm)\mapsto(b-a)m}Rm\longrightarrow0.
$$
The differential's kernel is the diagonal $\{(am,am):a\in R\}$. The map is surjective, since $cm$ is the image of $(0,cm)$. Thus
$$
\check H^0_{(2,3)}\cong Rm,\qquad \check H^1_{(2,3)}=0.
$$
There are no terms in other degrees.

**Case $m=X^5Y^{-4}$.** The exponent of $Y$ is negative, so this monomial does not occur in $A_X$. It occurs in $A_Y$ and $A_{XY}$, so its complex is
$$
0\longrightarrow 0\oplus Rm
\xrightarrow{(0,bm)\mapsto bm}Rm\longrightarrow0.
$$
The differential is an isomorphism. Therefore
$$
\check H^0_{(5,-4)}=0,\qquad \check H^1_{(5,-4)}=0.
$$

**Case $m=X^{-3}Y^{-6}$.** Both exponents are negative. This monomial occurs in neither $A_X$ nor $A_Y$, but does occur in $A_{XY}$. Its complex is
$$
0\longrightarrow0\longrightarrow Rm\longrightarrow0,
$$
with $Rm$ in degree $1$. Hence
$$
\check H^0_{(-3,-6)}=0,\qquad
\check H^1_{(-3,-6)}\cong Rm.
$$
If $R\ne0$, the monomial class is nonzero.

**Check and pitfall.** The element $X^{-3}Y^{-6}$ cannot be written as a sum of Laurent polynomials from $A_X$ and $A_Y$: every monomial from $A_X$ has nonnegative $Y$-exponent, and every monomial from $A_Y$ has nonnegative $X$-exponent. Uniqueness of coefficients in the Laurent basis proves this without assuming that $R$ is a field. Do not add $A$ as a new degree-$0$ term: the Čech complex of this cover already starts with $A_X\oplus A_Y$.

## 2. The module structure on monomials with all exponents negative {#d100-bridge-mastery-bgk-27-new-02}

**Source exercise:** [Exercise 27.6 in the reader](bgk-reader.html#br-bgk-2019-w27-ex06).
Exact identifier: `Polynomring/Höchste lokale Kohomologie/Modulstruktur/Direkt/Aufgabe`; [source revision 1083806](https://de.wikiversity.org/w/index.php?oldid=1083806).
Its placement is frozen in Worksheet 27, revision 1070033.

**Statement.** Let $K$ be a field and $A=K[X_1,\ldots,X_d]$. On the vector space
$$
H=K\left\langle
X^\nu=X_1^{\nu_1}\cdots X_d^{\nu_d}:\nu_j\leq-1
\text{ for every }j
\right\rangle,
$$
define a natural $A$-module structure.

**Editorial solution.** We explain the case $d\geq1$, with variables present as in the exercise. Every element of $H$ is a finite linear combination of the displayed monomials. Ordinary Laurent multiplication by $X_i$ does not always stay in $H$: if $\nu_i=-1$, the result has exponent $0$. The required module action must annihilate results leaving the negative-exponent region.

For $i=1,\ldots,d$, define a linear operator $T_i:H\to H$ on the basis by
$$
T_i(X^\nu)=
\begin{cases}
X^{\nu+e_i},&\nu_i\leq-2,\\
0,&\nu_i=-1,
\end{cases}
$$
where $e_i$ has $i$th component $1$ and all other components $0$. These operators commute. Indeed, for $i\ne j$, increasing the $i$th exponent does not change whether the $j$th exponent is still permitted. If either of $\nu_i,\nu_j$ equals $-1$, both composites annihilate the monomial. If both are at most $-2$, both composites yield $X^{\nu+e_i+e_j}$.

Since all $T_i$ commute, for $p=\sum_{\alpha\in\mathbb N^d}c_\alpha X^\alpha\in A$ we may set
$$
p\cdot h=\sum_\alpha c_\alpha T_1^{\alpha_1}\cdots T_d^{\alpha_d}(h).
$$
This sum is finite. The map $A\to\operatorname{End}_K(H)$ sending $X_i$ to $T_i$ preserves addition, multiplication, and the identity. Consequently
$$
(p+q)\cdot h=p\cdot h+q\cdot h,\qquad
p\cdot(h+h')=p\cdot h+p\cdot h',\qquad
(pq)\cdot h=p\cdot(q\cdot h),\qquad 1\cdot h=h.
$$
These are all the required module conditions. The formula on a single monomial is
$$
p\cdot X^\nu
=
\sum_{\substack{\alpha\in\mathbb N^d\\
\nu_j+\alpha_j\leq-1\ \text{for all }j}}
c_\alpha X^{\nu+\alpha}.
$$
Thus all terms acquiring at least one nonnegative exponent are discarded.

To see why this action is natural, consider the Laurent module
$$
L=K[X_1^{\pm1},\ldots,X_d^{\pm1}]
$$
and the following $A$-submodule:
$$
N=\sum_{i=1}^d
K[X_1^{\pm1},\ldots,X_{i-1}^{\pm1},X_i,
X_{i+1}^{\pm1},\ldots,X_d^{\pm1}].
$$
Each summand is an $A$-submodule: multiplication by a polynomial does not turn a nonnegative $i$th exponent into a negative one. The module $N$ is spanned exactly by the Laurent monomials having at least one nonnegative exponent. Since all Laurent monomials form a $K$-basis of $L$, the classes of monomials with all exponents negative form a basis of $L/N$. Thus there is a vector-space isomorphism
$$
H\longrightarrow L/N,\qquad X^\nu\longmapsto[X^\nu].
$$
The action defined above is exactly the quotient $A$-action on $L/N$: a monomial leaving the negative region enters $N$ and becomes zero. This also connects the construction with the top cohomology component computed in the lecture.

**Check and pitfall.** For $d=2$,
$$
X_1\cdot(X_1^{-1}X_2^{-2})=0,\qquad
X_2\cdot(X_1^{-1}X_2^{-2})=X_1^{-1}X_2^{-1}.
$$
Although each $X_i$ is invertible in the Laurent ring $L$, its action on $H$ is not an invertible operator. We form the quotient as an $A$-module, not as a module over the entire Laurent ring. If $d=0$ is allowed, the empty-product convention gives $A=H=K$ with the usual scalar action.

## 3. Global sections on a plane curve {#d100-bridge-mastery-bgk-27-new-03}

**Source exercise:** [Exercise 27.10 in the reader](bgk-reader.html#br-bgk-2019-w27-ex10).
Exact identifier: `Projektive Ebene/Kurve/Getwistete Strukturgabe zu d-3/Globale Schnitte/Aufgabe`; [source revision 1097429](https://de.wikiversity.org/w/index.php?oldid=1097429).
The spelling `Strukturgabe` in the source identifier is preserved. Its placement is frozen in Worksheet 27, revision 1070033.

**Statement.** Let $C=V_+(f)\subset\mathbb P_K^2$ be a projective plane curve of degree $d$ over a field $K$. Using the long exact cohomology sequence associated to
$$
0\longrightarrow\mathcal O_{\mathbb P_K^2}(-3)
\xrightarrow{f}\mathcal O_{\mathbb P_K^2}(d-3)
\longrightarrow\mathcal O_C(d-3)\longrightarrow0
$$
and Theorem 27.4, prove that
$$
\dim_KH^0(C,\mathcal O_C(d-3))=\frac{(d-1)(d-2)}2.
$$

**Editorial solution.** Write $S=K[X,Y,Z]$ and $P=\mathbb P_K^2$. The statement that the curve is given by $f$ means that $f$ is a nonzero homogeneous polynomial of degree $d\geq1$. Neither algebraic closedness of $K$ nor smoothness of $C$ is required for this computation.

Let $i:C\hookrightarrow P$ be the closed immersion. In the sequence of sheaves on $P$, the final term written $\mathcal O_C(d-3)$ means $i_*\mathcal O_C(d-3)$. This notation distinguishes the space on which the sheaf is defined without changing the exercise.

As a check on the given short sequence, multiplication by $f$ gives an exact sequence of graded modules
$$
0\longrightarrow S(-3)
\xrightarrow{f}S(d-3)
\longrightarrow(S/(f))(d-3)\longrightarrow0.
$$
The first map is injective because $S$ is an integral domain and $f\ne0$. Localising on standard charts, taking degree-zero parts, and gluing gives the sheaf sequence in the exercise.

The beginning of the corresponding long exact cohomology sequence is
$$
\begin{aligned}
0\longrightarrow{}&H^0(P,\mathcal O_P(-3))
\longrightarrow H^0(P,\mathcal O_P(d-3))\\
\longrightarrow{}&H^0(C,\mathcal O_C(d-3))
\longrightarrow H^1(P,\mathcal O_P(-3)).
\end{aligned}
$$
The identification of global sections in the pushforward term follows directly from the definition: $\Gamma(P,i_*\mathcal O_C(d-3))=\Gamma(C,\mathcal O_C(d-3))$.

[Theorem 27.4](bgk-reader.html#br-bgk-2019-l27-thm-02), with projective-space dimension equal to $2$, gives
$$
H^0(P,\mathcal O_P(n))\cong S_n,\qquad
H^1(P,\mathcal O_P(n))=0
$$
for every integer $n$. Here $S_n=0$ for $n<0$. The Čech computation in that theorem computes sheaf cohomology by [Theorem 26.10](bgk-reader.html#br-bgk-2019-l26-thm-01): $P$ is a projective scheme and $\mathcal O_P(n)$ is quasicoherent, with the standard affine cover.

In particular,
$$
H^0(P,\mathcal O_P(-3))=0,\qquad
H^1(P,\mathcal O_P(-3))=0.
$$
Exactness of the sequence above then gives an isomorphism
$$
S_{d-3}\ \cong\ H^0(C,\mathcal O_C(d-3)).
$$
Thus it remains only to count homogeneous monomials.

If $d\geq3$, write $m=d-3\geq0$. A basis of $S_m$ consists of monomials $X^aY^bZ^c$ with $a,b,c\geq0$ and $a+b+c=m$. For each $a$ there are $m-a+1$ pairs $(b,c)$, so
$$
\dim_KS_m
=\sum_{a=0}^m(m-a+1)
=\frac{(m+1)(m+2)}2
=\frac{(d-1)(d-2)}2.
$$
If $d=1$ or $d=2$, then $d-3<0$ and $S_{d-3}=0$. The formula on the right is also zero for both degrees. This covers all $d\geq1$ and proves the conclusion.

**Check and pitfall.** For a cubic curve ($d=3$), the resulting space has dimension $1$, represented by constant polynomials. For a quartic curve ($d=4$), its dimension is $3$, represented by $X,Y,Z$. Surjectivity of restriction on global sections is not automatic from sheaf surjectivity: here it follows from $H^1(P,\mathcal O_P(-3))=0$. The connection with global differential forms requires the smoothness hypothesis mentioned in the introduction to the source exercise; the dimension computation above does not add that hypothesis.
