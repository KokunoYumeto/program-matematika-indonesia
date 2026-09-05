---
title: "Lecture 18 - Kähler Differentials"
stable_id: br-bgk-2019-l18
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 18"
upstream_pageid: 109022
upstream_revid: 1069569
upstream_timestamp: "2026-02-06T07:06:24Z"
upstream_mediawiki_sha1: 2278e6ac498280b0903b3eb4d27293a2647401b5
source_url: "https://de.wikiversity.org/w/index.php?oldid=1069569"
authority_manifest: authority/wikiversity-bgk/unit-18/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f0014846fe068d3b1bfd4488c1db66fdd6039fa2d70ff7b8a213875a56d39495
authority_manifest_status: "Complete terminal authority freeze; all 41 file records have been recomputed without mismatches."
lecture_xml: authority/wikiversity-bgk/unit-18/lecture-18.xml
lecture_xml_sha256: 6258ac16b73eb1dbf8c25cd6147c37f4cbab4cc5fe10319c5214951f7d54574e
lecture_expanded_tex: authority/wikiversity-bgk/unit-18/lecture-18-expanded.tex
lecture_expanded_tex_sha256: 36090ca8661261017db8076345b22126ae1d99c4df8efbc6480533775264b955
official_pdf: authority/artifacts/bgk-lecture-18-official.pdf
official_pdf_sha256: 95c36781fe3c5df56320e7cc7992ddff2a9c548e4099d811c768bc29c37ebfc9
official_pdf_status: "Local official PDF witness; 99,940 bytes, 9 pages, and upload SHA-1 eabef241ecf776d80e72491645cd93bfd5fcca1e have been verified."
official_pdf_metadata: authority/wikiversity-bgk/unit-18/official-pdfs-api.json
official_pdf_source_bytes: 99940
official_pdf_source_sha1: eabef241ecf776d80e72491645cd93bfd5fcca1e
older_course_pdf: authority/artifacts/bgk-course-official.pdf
older_course_pdf_sha256: 87655cf7e96dc0eaa185ca49a374dc9e25f4b739670495f423279aa332fce66c
authority_precedence: "The frozen semantic Wikiversity revision governs the text; the 2020 whole-course PDF is only a historical witness."
media_credits: source/id-ID/media-credits-bgk-unit-18.md
rights_ledger: authority/RIGHTS-bgk-unit-18.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-18.json
asset_closure_sha256: 33d6804e99934e11b06f7d05a732646e9371a51dd6fbbb35d642da28080caa77
license: "Frozen semantic course text and this translation: CC BY-SA 4.0. The PDF is an authority witness, not the edition text; the CC BY-SA 4.0 Commons metadata and embedded CC-by-sa 3.0 notice are retained without blanket relicensing."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 18: Kähler Differentials {#br-bgk-2019-l18}

## The module of Kähler differentials {#br-bgk-2019-l18-s01}

On a manifold $M$ there is a tangent bundle

$$
TM\longrightarrow M.
$$

Over a point $P\in M$, this consists of the tangent space $T_PM$, given by equivalence classes of differentiable curves

$$
[-\epsilon,\epsilon]\longrightarrow M
$$

through $P$. The tangent bundle is a real vector bundle over $M$ that is characteristic of the manifold and allows many invariants of the manifold to be defined. We wish to define a corresponding object for a scheme, say of finite type over a field. A direct transfer of the analytic concept is impossible, since there is no direct replacement for differentiable curves. We therefore approach the tangent bundle from another perspective.

A continuous or differentiable section of the tangent bundle over an open set $U\subseteq M$ is called a continuous or differentiable vector field. A vector field $F$ assigns to every point $P\in U$ a tangent vector

$$
F(P)\in T_PM.
$$

Differentiable functions on $M$ can be differentiated along a vector field $F$, again giving a function. We set

$$
(D_F(f))(P):=(D_{F(P)}f)(P),
$$

where $(D_{F(P)}f)(P)$ denotes the directional derivative of $f$ at $P$ in the direction $F(P)$. This directional derivative can be calculated in any chart; by the chain rule, the result does not depend on the chosen chart. If $M$ and $F$ are infinitely differentiable, we obtain a map

$$
D_F:C^\infty(U,\mathbb R)\longrightarrow C^\infty(U,\mathbb R),
\qquad f\longmapsto D_F(f).
$$

> **Editorial note — the vector field.** The source prints $F(P)=T_PM$; the edition uses the required membership relation $F(P)\in T_PM$. For the displayed map to take values in $C^\infty$, the vector field $F$, as well as $M$, must be smooth; this hypothesis is made explicit above.

This map is an $\mathbb R$-linear derivation in the sense of the following purely algebraic definition. Starting from derivations, we shall introduce the module of Kähler differentials and, dually, develop a tangent sheaf in the scheme-theoretic setting. This sheaf is locally free when the scheme has no singularities. In this lecture we consider the affine situation and omit proofs.

<!-- upstream_entity: Algebraische Derivation/Definition -->

### Definition 18.1: algebraic derivations {#br-bgk-2019-l18-def-01}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $M$ be an $A$-module. An $R$-linear map

$$
\delta:A\longrightarrow M
$$

satisfying

$$
\delta(ab)=a\delta(b)+b\delta(a)
$$

for all $a,b\in A$ is called an *$R$-derivation* with values in $M$.

The rule used here is called the *Leibniz rule*. Often $M=A$. For example, for the polynomial ring

$$
A=R[X_1,\ldots,X_n],
$$

the $i$th formal partial derivative

$$
\frac{\partial}{\partial X_i}
$$

is an $R$-derivation from $A$ to $A$. The set of derivations from $A$ to $M$ is naturally an $A$-module, denoted by

$$
\operatorname{Der}_R(A,M).
$$

<!-- upstream_entity: Kähler Differentiale/Universeller Modul/Definition -->

### Definition 18.2: the module of Kähler differentials {#br-bgk-2019-l18-def-02}

Let $R$ be a commutative ring and let $A$ be a commutative $R$-algebra. The $A$-module generated by all symbols $d(a)$, $a\in A$, subject to the identifications

$$
d(ab)=ad(b)+bd(a)\qquad\text{for all }a,b\in A
$$

and

$$
d(ra+sb)=rd(a)+sd(b)
\qquad\text{for all }r,s\in R\text{ and }a,b\in A,
$$

is called the *module of Kähler differentials* of $A$ over $R$. It is denoted by

$$
\Omega_{A/R}.
$$

In this construction, we start with the free $A$-module $F$ with basis $da$, $a\in A$, and take its quotient by the submodule generated by the elements

$$
d(ab)-ad(b)-bd(a)\qquad(a,b\in A)
$$

and

$$
d(ra+sb)-rd(a)-sd(b)
\qquad(r,s\in R\text{ and }a,b\in A).
$$

The map

$$
d:A\longrightarrow\Omega_{A/R},
\qquad a\longmapsto d(a)=da,
$$

is called the *universal derivation*. One checks immediately that it is indeed an $R$-derivation. The elements of $\Omega_{A/R}$ are called *algebraic differential forms*.

<!-- upstream_entity: Kähler-Differentiale/Universelle Eigenschaft/Fakt -->

### Lemma 18.3: the universal property {#br-bgk-2019-l18-lem-01}

Let $R$ be a commutative ring and let $A$ be a commutative $R$-algebra. The module of Kähler differentials $\Omega_{A/R}$ has the following universal property. For every $A$-module $M$ and every $R$-derivation

$$
\delta:A\longrightarrow M,
$$

there is a unique $A$-linear map

$$
\epsilon:\Omega_{A/R}\longrightarrow M
$$

satisfying $\epsilon\circ d=\delta$.

#### Proof {#br-bgk-2019-l18-lem-01-proof}

This proof was not presented in the lecture.

For every $da$, $a\in A$, we must have $\epsilon(da)=\delta(a)$. Since the elements $da$ generate $\Omega_{A/R}$ as an $A$-module, there can be at most one such homomorphism.

Let $F$ be the free module with basis $da$, $a\in A$. The assignment

$$
\widetilde\epsilon(da)=\delta(a)
$$

by the theorem on specifying a homomorphism on a basis, determines an $A$-module homomorphism

$$
\widetilde\epsilon:F\longrightarrow M.
$$

We have $\Omega_{A/R}=F/U$, where $U$ is the submodule generated by the elements expressing the Leibniz rule and linearity. Since $\delta$ is a derivation, $\widetilde\epsilon$ maps $U$ to $0$. The homomorphism theorem therefore gives a unique $A$-linear map

$$
\epsilon:\Omega_{A/R}\cong F/U\longrightarrow M
$$

with

$$
\epsilon(da)=\widetilde\epsilon(da)=\delta(a).
$$

Equivalently, this statement gives a natural $A$-module isomorphism

$$
\operatorname{Der}_R(A,M)
\cong\operatorname{Hom}_A(\Omega_{A/R},M).
$$

In particular,

$$
\operatorname{Der}_R(A,A)
\cong\operatorname{Hom}_A(\Omega_{A/R},A)
=\Omega_{A/R}^*,
$$

where the right-hand side is the dual module.

<!-- upstream_entity: Kähler-Differentiale/Elementare Eigenschaften/Fakt -->

### Lemma 18.4: elementary properties {#br-bgk-2019-l18-lem-02}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $\Omega_{A/R}$ be the module of Kähler differentials. The following properties hold.

1. $dr=0$ for all $r\in R$.

2. $\Omega_{A/R}$ can be described as the quotient of the free $A$-module with basis $da$, $a\in A$, by the submodule generated by the additivity relations $d(a+b)-da-db$, the Leibniz relations, and $dr$, $r\in R$.

3. If $A=R[x_1,\ldots,x_n]$, then $dx_i$, $i=1,\ldots,n$, form an $A$-module generating system for $\Omega_{A/R}$.

4. Let

   $$
   A=R[x_1,\ldots,x_n]
   =R[X_1,\ldots,X_n]/\mathfrak a.
   $$

   For a polynomial $F\in R[X_1,\ldots,X_n]$ and the associated element $f=F(x_1,\ldots,x_n)\in A$, the following relation holds in $\Omega_{A/R}$:

   $$
   df=
   \frac{\partial F}{\partial x_1}(x_1,\ldots,x_n)dx_1
   +\cdots+
   \frac{\partial F}{\partial x_n}(x_1,\ldots,x_n)dx_n,
   $$

   where $\partial F/\partial x_i$ denotes the $i$th partial derivation.

5. For a commutative diagram

   $$
   \begin{matrix}
   R&\longrightarrow&S\\
   \downarrow&&\downarrow\\
   A&\xrightarrow{\ \varphi\ }&B,
   \end{matrix}
   $$

   whose arrows are ring homomorphisms, there is a unique $A$-linear map

   $$
   \Omega_{A/R}\longrightarrow\Omega_{B/S},
   \qquad da\longmapsto d\varphi(a).
   $$

> **Editorial note — a missing family of relations.** The source lists only the Leibniz relations and $dr$ in part (2), but its proof immediately uses $d(ra+sb)=d(ra)+d(sb)$. Additivity is not supplied by those listed relations. This edition includes the additivity relations, as required by Definition 18.2 and by the proof.

#### Proof {#br-bgk-2019-l18-lem-02-proof}

This proof was not presented in the lecture.

1. Let $r\in R$. By $R$-linearity, $d(r1)=rd(1)$. By the product rule,

   $$
   d(1)=d(1\cdot1)=1d(1)+1d(1),
   $$

   so subtraction gives $d(1)=0$.

2. We show that the submodule $V$ in question equals the submodule $U$ generated by all Leibniz and linearity relations. By part (1), the inclusion $V\subseteq U$ is clear. For $a,b\in A$ and $r,s\in R$, modulo $V$ we have

   $$
   \begin{aligned}
   d(ra+sb)
   &=d(ra)+d(sb)\\
   &=rda+adr+sdb+bds\\
   &=rda+sdb,
   \end{aligned}
   $$

   so the linearity relations also belong to $V$.

3. This follows from linearity and the Leibniz rule.

4. Both sides are $R$-linear, so it suffices to prove the assertion for monomials. For monomials, it follows by induction on total degree.

5. Since $B$ is an $A$-algebra via $\varphi:A\to B$, the module $\Omega_{B/S}$ is also an $A$-module. The composite

   $$
   A\xrightarrow{\ \varphi\ }B
   \xrightarrow{\ d\ }\Omega_{B/S}
   $$

   is an $R$-derivation, as a direct calculation shows. By the universal property of $\Omega_{A/R}$, there is a unique $A$-linear map

   $$
   \widetilde\varphi:\Omega_{A/R}\longrightarrow\Omega_{B/S}
   $$

   with $d\varphi(a)=\widetilde\varphi(da)$.

<!-- upstream_entity: Polynomring/Kählermodul und Derivation/Beschreibung/Fakt -->

### Lemma 18.5: differentials of a polynomial ring {#br-bgk-2019-l18-lem-03}

Let $R$ be a commutative ring and let

$$
A=R[X_1,\ldots,X_n]
$$

be the polynomial ring in $n$ variables over $R$. Then the module of Kähler differentials is the free $A$-module with basis

$$
dX_1,dX_2,\ldots,dX_n.
$$

With respect to this basis, the universal derivation is given by

$$
\begin{aligned}
A&\longrightarrow AdX_1\oplus\cdots\oplus AdX_n,\\
F&\longmapsto dF
=\frac{\partial F}{\partial X_1}dX_1
+\cdots+
\frac{\partial F}{\partial X_n}dX_n.
\end{aligned}
$$

#### Proof {#br-bgk-2019-l18-lem-03-proof}

This proof was not presented in the lecture.

Let $G$ be the free $A$-module generated by the symbols $dX_i$. The map

$$
\varphi:G\longrightarrow\Omega_{A/R}
$$

sending the basis element $dX_i$ to the differential $dX_i$ is surjective by Lemma 18.4(3). The $i$th partial derivative

$$
\frac{\partial}{\partial X_i}:A\longrightarrow A,
\qquad F\longmapsto\frac{\partial F}{\partial X_i},
$$

is an $R$-derivation. The universal property of the module of differential forms therefore gives an $A$-linear map

$$
p_i:\Omega_{A/R}\longrightarrow A
$$

with $p_i\circ d=\partial/\partial X_i$. Here $p_i(dX_i)=1$ and $p_i(dX_j)=0$ for $j\ne i$. Together these maps give an $A$-linear map

$$
p=p_1\times\cdots\times p_n:
\Omega_{A/R}\longrightarrow A^n\cong G
$$

satisfying $p\circ\varphi=\operatorname{Id}_G$. Thus $\varphi$ is also injective.

In general, the module of Kähler differentials is not free.

<!-- upstream_entity: Kähler-Differentiale/Nenneraufnahme/Fakt -->

### Lemma 18.6: differentials and localisation {#br-bgk-2019-l18-lem-04}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $S\subseteq A$ be a multiplicative system. Then

$$
\Omega_{A_S/R}\cong(\Omega_{A/R})_S.
$$

#### Proof {#br-bgk-2019-l18-lem-04-proof}

See Exercise 18.19.

<!-- upstream_entity: Kähler-Differentiale/Relative Differentialsequenz/Fakt -->

### Lemma 18.7: the sequence of relative differentials {#br-bgk-2019-l18-lem-05}

Let $R$ be a commutative ring, let $A$ and $B$ be commutative $R$-algebras, and let

$$
\varphi:A\longrightarrow B
$$

be an $R$-algebra homomorphism. Then the sequence of $B$-modules

$$
\Omega_{A/R}\otimes_AB
\longrightarrow\Omega_{B/R}
\longrightarrow\Omega_{B/A}
\longrightarrow0
$$

is exact. Here $da\otimes b$ maps to $bd\varphi(a)$, while $db$ in $\Omega_{B/R}$ maps to $db$ in $\Omega_{B/A}$.

#### Proof {#br-bgk-2019-l18-lem-05-proof}

This proof was not presented in the lecture.

Surjectivity on the right is clear. For exactness at the second position, use the description in Lemma 18.4(2). The modules $\Omega_{B/A}$ and $\Omega_{B/R}$ have the same generating system and the same Leibniz relations. The module $\Omega_{B/A}$ is obtained from $\Omega_{B/R}$ precisely by killing the $B$-submodule generated by $da$, $a\in A$, making it $0$. This submodule is exactly the image of the map on the left.

## Kähler differentials and the Jacobian matrix {#br-bgk-2019-l18-s02}

<!-- upstream_entity: Kähler-Differentiale/Konormalensequenz/Fakt -->

### Lemma 18.8: the conormal sequence {#br-bgk-2019-l18-lem-06}

Let $R$ be a commutative ring, let $A$ be a commutative $R$-algebra, and let $I\subseteq A$ be an ideal with quotient ring $B=A/I$. Then the sequence of $B$-modules

$$
I/I^2\longrightarrow
\Omega_{A/R}\otimes_AB\longrightarrow
\Omega_{B/R}\longrightarrow0
$$

is exact. Here $a\in I$ maps to $da\otimes1$, while $da\otimes b$ maps to $bda$.

#### Proof {#br-bgk-2019-l18-lem-06-proof}

This proof was not presented in the lecture.

The $R$-linear map

$$
A\longrightarrow\Omega_{A/R},\qquad a\longmapsto da,
$$

can be restricted to the ideal $I\subseteq A$. Tensoring with $A/I$ and using Proposition 16.9 (Invariant Theory (Osnabrück 2025–2026)), part (2), gives the $A/I$-linear map

$$
I/I^2\cong I\otimes_AA/I
\longrightarrow\Omega_{A/R}\otimes_AA/I.
$$

Surjectivity of the map on the right is clear, since the $B$-module $\Omega_{B/R}$ is generated by $db$, $b\in B$, and these elements come from $da$, $a\in A$. An element $a\in I$ maps to $da$ and then to $0$ in $\Omega_{B/R}$, since $a$ itself becomes $0$ in $B$.

Now suppose that

$$
\omega\in\Omega_{A/R}\otimes_AB
$$

maps to $0$ in $\Omega_{B/R}$. We can write

$$
\omega
=\sum_{i=1}^n da_i\otimes b_i
=\sum_{i=1}^n da_i\otimes\bar c_i
$$

with $a_i,c_i\in A$. Since this element maps to $0$ in $\Omega_{B/R}$, the free $B$-module generated by the symbols $db$, $b\in B$, satisfies the relation

$$
\sum_{i=1}^n c_i\,da_i
=\sum_{j=1}^m h_j\omega_j,
$$

where $h_j\in B$ and the $\omega_j$ generate the relations for the module of Kähler differentials, namely relations of the form

$$
d(fg)=f\,dg+g\,df
$$

for $f,g\in B$, or

$$
d(rf+sg)=r\,df+s\,dg
$$

for $r,s\in R$ and $f,g\in B$. This free $B$-module is obtained from the free $A$-module generated by $da$, $a\in A$, by making the coefficients in $I$ and all $dI$ equal to $0$. Thus, in this free $A$-module,

$$
\sum_{i=1}^n c_i\,da_i-
\sum_{j=1}^m h_j\omega_j
=\sum_{k=1}^{\ell}m_k\,dn_k+du
$$

with $m_k\in I$, $n_k\in B$, and $u\in I$. In $\Omega_{A/R}\otimes_AB$, the term $\sum_{k=1}^{\ell}m_k\,dn_k$ becomes $0$ after tensoring. Hence there we indeed have

$$
\sum_{i=1}^n c_i\,da_i=du.
$$

> **Editorial note — gaps in the source proof.** The source's final tensor product is printed over $R$; it must be over $A$, as in the statement, and is corrected above. There are also gaps that this symbol change alone does not repair: the restriction of the $R$-linear derivation cannot simply be tensored as an $A$-linear map; the free-module discussion must identify symbols with the same image in $B$, not merely kill $dI$; and elements of $B$ used in the free $A$-module require lifts to $A$.
>
> A precise editorial justification is as follows. Put $E=\Omega_{A/R}\otimes_AB$. The map $I\to E$, $i\mapsto di\otimes1$, is $A$-linear by the Leibniz rule, since the terms with coefficient in $I$ vanish in $E$; it vanishes on $I^2$, giving $I/I^2\to E$. Let $N$ be its image. The formula $\bar a\mapsto da\otimes1$ defines an $R$-derivation $B\to E/N$, independent of the chosen lift. By the universal property, it induces an inverse to the natural map $E/N\to\Omega_{B/R}$. Thus $E/N\cong\Omega_{B/R}$, proving the stated exactness. This paragraph supplements, rather than silently replaces, the source argument.

<!-- upstream_entity: Kähler-Differentiale/Von endlichem Typ/Restklassendarstellung/Fakt -->

### Corollary 18.9: differentials of a quotient algebra {#br-bgk-2019-l18-cor-01}

Let $R$ be a commutative ring and let $A$ be a finitely generated commutative $R$-algebra, presented as

$$
A=R[X_1,\ldots,X_n]/(F_1,\ldots,F_k).
$$

Then

$$
\Omega_{A/R}
=\bigoplus_{i=1}^nAdX_i/(dF_1,\ldots,dF_k).
$$

#### Proof {#br-bgk-2019-l18-cor-01-proof}

This proof was not presented in the lecture.

This follows from Lemma 18.5 and Lemma 18.8.

<!-- upstream_entity: Kähler-Differentiale/Jacobi-Matrix/Kokern-Darstellung/Bemerkung -->

### Remark 18.10: presentation as the cokernel of the Jacobian matrix {#br-bgk-2019-l18-rem-01}

Let $R$ be a commutative ring and let $A$ be a finitely generated commutative $R$-algebra, presented as

$$
A=R[X_1,\ldots,X_n]/(F_1,\ldots,F_k).
$$

By Lemma 18.4(4),

$$
dF_j=
\frac{\partial F_j}{\partial X_1}dX_1
+\cdots+
\frac{\partial F_j}{\partial X_n}dX_n,
$$

and by Corollary 18.9 there is an exact sequence

$$
A^k\xrightarrow{\ M\ }A^n
\longrightarrow\Omega_{A/R}\longrightarrow0,
$$

where

$$
M=
\begin{pmatrix}
\dfrac{\partial F_1}{\partial X_1}&\cdots&
\dfrac{\partial F_k}{\partial X_1}\\
\vdots&\ddots&\vdots\\
\dfrac{\partial F_1}{\partial X_n}&\cdots&
\dfrac{\partial F_k}{\partial X_n}
\end{pmatrix}
$$

is the transpose of the Jacobian matrix, without evaluation at a point. The standard vectors $e_j$ map to $dX_j$, and the column vectors

$$
\begin{pmatrix}
\dfrac{\partial F_j}{\partial X_1}\\
\vdots\\
\dfrac{\partial F_j}{\partial X_n}
\end{pmatrix},
$$

representing the zero elements $dF_j$ are the images of the map defined by the matrix.

## Smoothness and regularity {#br-bgk-2019-l18-s03}

<!-- upstream_entity: Affin-algebraische Menge/Punkt/Lokale Dimension/Glatt/Partielle Ableitungen/Definition -->

### Definition 18.11: smooth points {#br-bgk-2019-l18-def-03}

Let $K$ be an algebraically closed field and let

$$
F_1,\ldots,F_s\in K[X_1,\ldots,X_n]
$$

be polynomials with associated affine algebraic set

$$
Y=V(F_1,\ldots,F_s)\subseteq\mathbb A_K^n.
$$

Let $P\in Y$ be a point such that $Y$ has dimension $d$ at $P$. The point $P$ is called a *smooth point* of $Y$ if the rank of the matrix

$$
\left(\frac{\partial F_i}{\partial X_j}\right)_{i,j}
$$

at $P$ is at least $n-d$. Otherwise, the point is called *singular*.

> **Editorial note — equations versus the reduced algebraic set.** This criterion concerns the scheme presented by the given equations. If $Y$ denotes the reduced algebraic set, the equations must generate its vanishing ideal; the source does not state this qualification. For instance, $X^2$ and $X$ have the same zero set but different Jacobian ranks at $0$. The same distinction applies to the local ring in Theorem 18.16.

For a $K$-algebra

$$
A=K[X_1,\ldots,X_n]/(f_1,\ldots,f_m)
$$

and a point

$$
P=(a_1,\ldots,a_n)\in V=V(f_1,\ldots,f_m)
$$

with associated maximal ideal $\mathfrak m_P\subseteq A$ and localisation

$$
R=A_{\mathfrak m_P}=\mathcal O_{V,P},
$$

we have

$$
\Omega_{R/K}=\Omega_{A/K}\otimes_AR.
$$

The tensor product

$$
\Omega_{R/K}\otimes_RK
=\Omega_{A/K}\otimes_AK
$$

associated with evaluation in the residue field

$$
A\longrightarrow A_{\mathfrak m_P}
\longrightarrow A_{\mathfrak m_P}/\mathfrak m_PA_{\mathfrak m_P}=K
$$

plays a special role. There is a direct connection with the dual of the extrinsic tangent space of $V$ at $P$. In other words, $\Omega_{R/K}\otimes_RK$ is naturally the cotangent space at $P$.

<!-- upstream_entity: Kähler-Differentiale/Gleichungen/Extrinsischer Kotangentialraum/Fakt -->

### Lemma 18.12: the extrinsic cotangent space {#br-bgk-2019-l18-lem-07}

Let $K$ be a field, let

$$
A=K[X_1,\ldots,X_n]/(f_1,\ldots,f_m)
$$

be a finitely generated $K$-algebra, and let

$$
P=(a_1,\ldots,a_n)\in V=V(f_1,\ldots,f_m)
$$

be a point of the associated zero locus, with maximal ideal $\mathfrak m_P\subseteq A$ and localisation

$$
R=A_{\mathfrak m_P}.
$$

Then the tangent space to $V$ at $P$ is canonically the dual vector space of $\Omega_{R/K}\otimes_RK$.

> **Editorial note — the maximal-ideal subscript.** The source introduces the maximal ideal $\mathfrak m_P$ but then writes $A_{\mathfrak m}$ in the residue-field display and in this lemma, without defining $\mathfrak m$. This edition consistently uses the already defined $\mathfrak m_P$.

#### Proof {#br-bgk-2019-l18-lem-07-proof}

This proof was not presented in the lecture.

By Remark 18.10, there is an exact sequence

$$
A^m\xrightarrow{\ M\ }A^n
\longrightarrow\Omega_{A/K}\longrightarrow0,
$$

where $M$ is the transpose of the Jacobian matrix of the $f_i$. Tensoring with the residue field $K$ gives an exact sequence of finite-dimensional $K$-vector spaces

$$
K^m\xrightarrow{\ M(P)\ }K^n
\longrightarrow\Omega_{A/K}\otimes_AK
\longrightarrow0.
$$

Its dual sequence is

$$
0\longrightarrow
(\Omega_{A/K}\otimes_AK)^*
\longrightarrow K^n
\xrightarrow{\ \operatorname{Jac}(P)\ }K^m,
$$

and is also exact. By the definition of the tangent space, the kernel of the Jacobian matrix at $P$ is the tangent space to $V$ at $P$.

> **Editorial note — unresolved source reference.** The source gives `Definition .` at this point. This edition does not invent a reference number and instead names the definition of the tangent space used in the argument.

<!-- upstream_entity: Lokaler Ring/Regulär/Erzeugeranzahl/Definition -->

### Definition 18.13: regular local rings {#br-bgk-2019-l18-def-04}

A Noetherian local ring $(R,\mathfrak m)$ of dimension $n$ is called *regular* if there are $n$ elements

$$
f_1,\ldots,f_n\in\mathfrak m
$$

generating the maximal ideal $\mathfrak m$.

<!-- upstream_entity: Kähler-Differentiale/Lokaler Ring/Kotangentialraum/Fakt -->

### Lemma 18.14: the maximal ideal and the cotangent space {#br-bgk-2019-l18-lem-08}

Let $K$ be a field and let $R$ be a local commutative $K$-algebra, such that the composite map

$$
K\longrightarrow R\longrightarrow R/\mathfrak m
$$

is an isomorphism. Then the map

$$
\mathfrak m/\mathfrak m^2
\longrightarrow\Omega_{R/K}\otimes_RR/\mathfrak m,
\qquad[f]\longmapsto df\otimes1,
$$

is an $R/\mathfrak m$-module isomorphism.

#### Proof {#br-bgk-2019-l18-lem-08-proof}

This proof was not presented in the lecture.

By Lemma 18.8, there is an exact sequence of $R/\mathfrak m$-module homomorphisms

$$
\mathfrak m/\mathfrak m^2
\longrightarrow\Omega_{R/K}\otimes_RR/\mathfrak m
\longrightarrow\Omega_{(R/\mathfrak m)/K}
\longrightarrow0.
$$

By assumption, $R/\mathfrak m=K$, hence $\Omega_{(R/\mathfrak m)/K}=0$. Thus the stated map is surjective. To prove injectivity, consider its $R/\mathfrak m$-dual map, namely

$$
\begin{aligned}
&\operatorname{Hom}_{R/\mathfrak m}
(\Omega_{R/K}\otimes_RR/\mathfrak m,R/\mathfrak m)\\
&\qquad\longrightarrow
\operatorname{Hom}_{R/\mathfrak m}
(\mathfrak m/\mathfrak m^2,R/\mathfrak m),
\qquad\varphi\longmapsto\varphi\circ d,
\end{aligned}
$$

and show that this is surjective, since we are dealing with vector spaces.

By Lemma 32.9 (Commutative Algebra) and Lemma 18.3, the homomorphism module on the left is isomorphic to

$$
\operatorname{Hom}_R(\Omega_{R/K},R/\mathfrak m)
\cong\operatorname{Der}_K(R,R/\mathfrak m).
$$

The composite assigns to a $K$-derivation $\delta:R\to R/\mathfrak m$ the map

$$
\mathfrak m/\mathfrak m^2\longrightarrow R/\mathfrak m,
\qquad[f]\longmapsto\delta(f).
$$

Now let

$$
\mathfrak m/\mathfrak m^2\longrightarrow R/\mathfrak m,
\qquad[f]\longmapsto\epsilon(f)
$$

be an $R/\mathfrak m$-module homomorphism. We must show that it comes from a derivation. For this, consider the map

$$
\delta:R\longrightarrow R/\mathfrak m,
\qquad f\longmapsto\epsilon(f-\bar f),
$$

where $\bar f$ is the value of $f$ in the residue field $R/\mathfrak m$, regarded again as an element of $R$ through the identification $K=R/\mathfrak m$. Thus $f-\bar f\in\mathfrak m$, and the map is well-defined. A direct verification, similar to the proof of Theorem 23.2 (Algebraic Curves (Osnabrück 2025–2026)), shows that it is a derivation. This derivation maps to $\epsilon$.

Without the assumption that the natural map from the base field to the residue field is an isomorphism, this assertion does not hold; see Exercise 18.23.

<!-- upstream_entity: Kähler-Differentiale/Gleichungen/Maximales Ideal/Extrinsischer Kotangentialraum/Bemerkung -->

### Remark 18.15: the tangent space and the maximal ideal {#br-bgk-2019-l18-rem-02}

In the situation of Lemma 18.12, we can directly relate the extrinsic tangent space, given as the kernel of the Jacobian matrix, to the dual of $\mathfrak m_P/\mathfrak m_P^2$. Let

$$
v=
\begin{pmatrix}
v_1\\
\vdots\\
v_n
\end{pmatrix}
\in T_PV
=\ker\bigl(\operatorname{Jac}(f_1,\ldots,f_m)_P\bigr).
$$

This vector defines a map

$$
\begin{aligned}
\mathfrak m_P&\longrightarrow K,\\
g&\longmapsto
(dg)_P
\begin{pmatrix}
v_1\\
\vdots\\
v_n
\end{pmatrix}
=v_1\partial_1g(P)+\cdots+v_n\partial_ng(P).
\end{aligned}
$$

In analytic language, a function $g$ is sent to the value at $P$ of its directional derivative in the direction $v$. The kernel condition ensures that functions in the ideal $(f_1,\ldots,f_m)$ map to $0$, so the map is well-defined on the maximal ideal of the quotient ring. By the product rule, $\mathfrak m_P^2$ also maps to $0$. Thus we obtain a $K$-linear map

$$
\mathfrak m_P/\mathfrak m_P^2\longrightarrow K.
$$

<!-- upstream_entity: Affine Varietät/Punkt/Jacobi-Matrix und regulär/Fakt -->

### Theorem 18.16: smooth points and regular local rings {#br-bgk-2019-l18-thm-01}

Let $K$ be an algebraically closed field and let

$$
P\in V(\mathfrak a)\subseteq\mathbb A_K^n
$$

be a point of the affine algebraic set defined by the ideal $\mathfrak a=(f_1,\ldots,f_m)$, with local ring

$$
R=\bigl(K[X_1,\ldots,X_n]/\mathfrak a\bigr)_{\mathfrak m_P}.
$$

Then $P$ is smooth if and only if $R$ is regular.

#### Proof {#br-bgk-2019-l18-thm-01-proof}

This proof was not presented in the lecture.

Without loss of generality, let $P$ be the origin. The corresponding maximal ideal in the polynomial ring is

$$
\mathfrak n=(X_1,\ldots,X_n),
$$

the associated maximal ideal in $K[X_1,\ldots,X_n]/\mathfrak a$ is

$$
\mathfrak r=\mathfrak n/\mathfrak a,
$$

and the associated maximal ideal in $R$ is

$$
\mathfrak m=\mathfrak m_P
=\mathfrak r\bigl(K[X_1,\ldots,X_n]/\mathfrak a\bigr)_{\mathfrak r}.
$$

Consider the $K$-linear map

$$
K[X_1,\ldots,X_n]\longrightarrow K^n,
\qquad
g\longmapsto
\bigl((\partial_1g)(P),\ldots,(\partial_ng)(P)\bigr).
$$

The variables $X_i$ map to the standard vectors $e_i$, so this map is surjective. An element

$$
g=c_0+c_1X_1+\cdots+c_nX_n+\text{higher-degree terms}
$$

maps to $(c_1,\ldots,c_n)$. A homogeneous element

$$
g\in\mathfrak n^2=K[X_1,\ldots,X_n]_{\geq2}
$$

has degree at least $2$ and therefore maps to $0$: partial differentiation reduces the degree by $1$, leaving an element of positive degree, which becomes $0$ on substituting the origin. This induces a $K$-linear map

$$
\mathfrak n/\mathfrak n^2\longrightarrow K^n
$$

which is bijective because the two spaces have the same vector space dimension.

By Lemma 22.4 (Algebraic Curves (Osnabrück 2025–2026)), we have

$$
\mathfrak r/\mathfrak r^2
\cong\mathfrak m/\mathfrak m^2.
$$

Under the surjective map

$$
\mathfrak n\longrightarrow\mathfrak r
\longrightarrow\mathfrak r/\mathfrak r^2,
$$

both $\mathfrak n^2$ and $\mathfrak a$ map to $0$, and its kernel is exactly $\mathfrak n^2+\mathfrak a$. There is therefore a $K$-linear bijection

$$
\mathfrak n/(\mathfrak n^2+\mathfrak a)
\longrightarrow\mathfrak r/\mathfrak r^2.
$$

Consider the maps

$$
K^m\xrightarrow{\ \operatorname{Jac}\ }K^n
\cong\mathfrak n/\mathfrak n^2
\longrightarrow\mathfrak n/(\mathfrak n^2+\mathfrak a).
$$

An element $[g]\in\mathfrak n/\mathfrak n^2$ maps to $0$ on the right exactly when the linear part of $g$ belongs to $\mathfrak n^2+\mathfrak a$. This means that, modulo $\mathfrak n^2$, there is an equation

$$
g=\sum_{i=1}^m h_if_i.
$$

Only the constant terms of the $h_i$ matter, so this is equivalent to the linear equation

$$
\begin{pmatrix}
(\partial_1g)(P)\\
\vdots\\
(\partial_ng)(P)
\end{pmatrix}
=\sum_{i=1}^m h_i
\begin{pmatrix}
(\partial_1f_i)(P)\\
\vdots\\
(\partial_nf_i)(P)
\end{pmatrix}.
$$

This holds exactly when the vector on the left lies in the image of the Jacobian matrix. Thus the image of the Jacobian matrix equals the kernel of the surjective map on the right. The dimension formula now gives

$$
\begin{aligned}
n
&=\operatorname{rank}(\operatorname{Jac})
+\dim_K\bigl(\mathfrak n/(\mathfrak n^2+\mathfrak a)\bigr)\\
&=\operatorname{rank}(\operatorname{Jac})
+\dim_K(\mathfrak m/\mathfrak m^2).
\end{aligned}
$$

Let $d$ be the dimension of $V(\mathfrak a)$ at $P$, equal to the dimension of the local ring $R$. By definition, $P$ is nonsingular exactly when

$$
n=\operatorname{rank}(\operatorname{Jac})+d.
$$

Thus this condition is equivalent to

$$
\dim_K(\mathfrak m/\mathfrak m^2)=d,
$$

which is the definition of a regular ring.

<!-- upstream_entity: Lokaler Ring/Restkörperbedingung/Regulär und Freier Kählermodul/Fakt -->

### Theorem 18.17: regularity and freeness of the module of differentials {#br-bgk-2019-l18-thm-02}

Let $K$ be a perfect field and let $(R,\mathfrak m)$ be a local ring obtained by localising a finitely generated $K$-algebra. Suppose that the natural map $K\to R/\mathfrak m$ is an isomorphism. Then $R$ is regular if and only if the module of Kähler differentials $\Omega_{R/K}$ is free and its rank equals the dimension of the ring.

> **Editorial note — hypotheses used in the proof.** The source says “a localisation” and that the residue field “is isomorphic” to $K$. Locality and the natural residue-field identification are made explicit here: these are the hypotheses needed for the stated use of Lemma 18.14 and Nakayama's lemma.

#### Proof {#br-bgk-2019-l18-thm-02-proof}

This proof was not presented in the lecture.

We use the natural $R/\mathfrak m$-isomorphism of Lemma 18.14,

$$
\mathfrak m/\mathfrak m^2
\longrightarrow\Omega_{R/K}\otimes_RR/\mathfrak m,
\qquad[f]\longmapsto df\otimes1.
$$

If $\Omega_{R/K}$ is a free $R$-module whose rank equals the dimension $d$, the same holds for the $R/\mathfrak m$-module $\Omega_{R/K}\otimes_RR/\mathfrak m$. In particular, $\mathfrak m/\mathfrak m^2$ is a $R/\mathfrak m$-vector space of dimension $d$. By definition, this means that $R$ is regular.

Conversely, regularity implies that $\mathfrak m/\mathfrak m^2$, and hence $\Omega_{R/K}\otimes_RR/\mathfrak m$, is a vector space of dimension $d$. By Nakayama's lemma, $\Omega_{R/K}$ is generated as an $R$-module by $d$ elements. By Theorem 21.5 (Singularity Theory (Osnabrück 2019)), the ring $R$ is an integral domain; denote its field of fractions by $Q(R)$. The transcendence degree of $Q(R)$ over $K$ equals the dimension of $R$ by Theorem 19.7 (Singularity Theory (Osnabrück 2019)). Since the module of Kähler differentials is compatible with localisation,

$$
\Omega_{R/K}\otimes_RQ(R)=\Omega_{Q(R)/K}.
$$

Since $K$ is perfect, the field extension $K\subseteq Q(R)$ is separably generated, although not finite. Thus $\Omega_{Q(R)/K}$ is a free $Q(R)$-module whose rank equals the transcendence degree.

In summary, the $R$-module $\Omega_{R/K}$ is generated by $d$ elements $\omega_1,\ldots,\omega_d$, and its tensor product with $Q(R)$ is a $Q(R)$-vector space of dimension $d$. Since these elements are linearly independent over $Q(R)$, they are also linearly independent over $R$. Hence they form a basis, and $\Omega_{R/K}$ is free of rank $d$.

> **Editorial note — module label and unresolved reference.** In the summary sentence the source names $\Omega_{Q(R)/K}$ as the $R$-module generated by the $d$ elements. The preceding application of Nakayama concerns $\Omega_{R/K}$, which is the module written here. The source also displays `Fakt *****` for the assertion about the separably generated extension; no unavailable reference number is invented.

Without the assumption that the base field is perfect, this assertion is false; see Exercise 18.24.

> **Editorial note — the cited exercise.** Exercise 18.24 has free differentials of rank $1$ over a field of dimension $0$, contrary to its printed nonfreeness claim. Moreover, its structural map from $K$ to the residue field is not an isomorphism. It therefore does not establish the source's preceding claim after removing only perfectness while retaining the other hypotheses. See the explicit diagnosis accompanying that exercise.

<!-- upstream_entity: Varietät/Glatt/Kählermodul/Lokal frei/Fakt -->

### Corollary 18.18: differentials on smooth varieties {#br-bgk-2019-l18-cor-02}

Let $V\subseteq\mathbb A_K^n$ be a connected smooth variety over a perfect field $K$, and let $R$ be the affine coordinate ring of $V$. Then the module of Kähler differentials $\Omega_{R/K}$ is locally free of constant rank $\dim(R)$ and, in particular, is a projective module.

#### Proof {#br-bgk-2019-l18-cor-02-proof}

This proof was not presented in the lecture.

This follows from Theorem 18.16, Theorem 18.17, Lemma 18.6, and Lemma 16.5.

<!-- upstream_entity: Zweidimensionale Sphäre/Kählermodul/Lokal frei/Nicht frei/Beispiel -->

### Example 18.19: the two-dimensional sphere {#br-bgk-2019-l18-exm-01}

Consider the real sphere

$$
S^2=\{(x,y,z)\mid x^2+y^2+z^2=1\}\subseteq\mathbb R^3
$$

with affine coordinate ring

$$
R=\mathbb R[X,Y,Z]/(X^2+Y^2+Z^2-1).
$$

By Corollary 18.9, the $R$-module of Kähler differentials is

$$
\Omega_{R/\mathbb R}
=RdX\oplus RdY\oplus RdZ/(XdX+YdY+ZdZ).
$$

A direct check shows that this real sphere is smooth. By Theorem 18.17, $\Omega_{R/\mathbb R}$ is therefore locally free of constant rank $2$. This can also be deduced directly from the presentation above; see Exercise 18.25. However, $\Omega_{R/\mathbb R}$ is not free. This is an algebraic version of the hairy ball theorem: the hairs on a sphere cannot be combed smoothly so that they all lie tangent to the sphere without forming a whorl.

For a polynomial map

$$
f:\mathbb A_K^n\longrightarrow\mathbb A_K^m
$$

with zero locus

$$
V=V(f_1,\ldots,f_m)\subseteq\mathbb A_K^n,
$$

the tangent space at a point $P\in V$ is

$$
\begin{aligned}
T_PV
&:=\ker\bigl(\operatorname{Jac}(f_1,\ldots,f_m)_P\bigr)\\
&=\{v\in\mathbb A_K^n\mid
\operatorname{Jac}(f_1,\ldots,f_m)_P(v)=0\}.
\end{aligned}
$$

If $P$ is a regular point of the map and the implicit function theorem applies, this is a linear subspace whose dimension equals the manifold dimension of $V$. This construction is extrinsic: it depends on the embedding of $V$ into affine space. We seek an intrinsic version of the tangent space depending only on $V$, or equivalently on its affine coordinate ring. For this purpose we introduce the module of Kähler differentials, which provides a dual version of the tangent space for every $R$-algebra $A$.
