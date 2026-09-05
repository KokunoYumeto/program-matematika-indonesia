---
title: "Lecture 27 - Cohomology on projective schemes"
stable_id: br-bgk-2019-l27
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Vorlesung 27"
upstream_pageid: 109031
upstream_revid: 1070036
upstream_timestamp: "2026-02-06T08:44:57Z"
upstream_mediawiki_sha1: a18e6d008d7f2611f624cd1fae3c768a6c61585f
source_url: "https://de.wikiversity.org/w/index.php?oldid=1070036"
authority_manifest: authority/wikiversity-bgk/unit-27/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b6c2a7687ee2fcc20e6f2b5f58f1f97a665a8c1f9201d11308bb84f62a79c089
authority_manifest_status: "Complete terminal authority freeze; all 30 file records have been rehashed without mismatches."
official_pdf: authority/artifacts/bgk-lecture-27-official.pdf
official_pdf_sha256: 5b9a2585247113ae4f0d7d10c66124c4fba1831891abf3836f9939a47d9a3a99
official_pdf_source_bytes: 93474
official_pdf_source_sha1: d842b6fdfc2c226877f0eb2d5652738e3dd2e028
official_pdf_pages: 7
authority_precedence: "The frozen semantic Wikiversity revisions control the text; the official PDFs are historical witnesses, not replacements for the semantic revisions."
pdf_component_rights: "The Commons metadata CC BY-SA 4.0 and embedded CC-by-sa 3.0 notices are preserved without blanket relicensing."
media_credits: source/id-ID/media-credits-bgk-unit-27.md
media_credits_sha256: dc3afa2d1b2e7c78a604bb54965bc45e4c56058c7585341e927d0e8e4a03f406
rights_ledger: authority/RIGHTS-bgk-unit-27.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-27.json
asset_closure_sha256: 0eb449063c5dab73703a381246847c4deac31a20327bbe2a8a4c17b082e915ab
lecture_xml: authority/wikiversity-bgk/unit-27/lecture-27.xml
lecture_xml_sha256: d0ac75985445f09f76b9fc1d9d93a04b677e102979f9431c02a29afdd19c4ff7
lecture_expanded_tex: authority/wikiversity-bgk/unit-27/lecture-27-expanded.tex
lecture_expanded_tex_sha256: ee29b146c2ad0c14c25ea7c97662c294a2ec0424791999580bece98448531316
license: "The frozen semantic course text and this translation: CC BY-SA 4.0. Official PDFs retain the recorded component notices; no blanket relicensing is claimed."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Lecture 27: Cohomology on projective schemes {#br-bgk-2019-l27}

## Čech cohomology on the polynomial ring {#br-bgk-2019-l27-s01}

Let $R$ be a commutative ring and let

$$
A=R[X_1,\ldots,X_n]
$$

be the polynomial ring in $n$ variables over $R$. In particular, one may keep in mind the case where $R$ is a field. We consider the open set

$$
U=\mathbb A_R^n\setminus V(X_1,\ldots,X_n)
=D(X_1,\ldots,X_n)
=\bigcup_{i=1}^nD(X_i),
$$

and will use the displayed affine cover, with $D(X_i)=\operatorname{Spek}(A_{X_i})$. For an $A$-module $M$, the Čech complex of the sheaf $\widetilde M$ on $U$ with respect to this cover has the form

$$
\prod_{1\leq i\leq n}M_{X_i}
\longrightarrow
\prod_{1\leq i<j\leq n}M_{X_iX_j}
\longrightarrow
\prod_{1\leq i<j<k\leq n}M_{X_iX_jX_k}
\longrightarrow\cdots
\longrightarrow M_{X_1\cdots X_n}
\longrightarrow0.
$$

Thus

$$
\check C^p(D(X_i),\widetilde M)
=\prod_{1\leq i_0<i_1<\cdots<i_p\leq n}
M_{X_{i_0}\cdots X_{i_p}},
$$

> **Edition note—missing relation sign.** The frozen source displays `i_1<\cdots i_p`, with no further `<` before `i_p`. The missing relation sign has been restored above, since the product is indexed by strictly increasing tuples, as in the preceding two displayed terms of the Čech complex.

and the $p$th Čech cohomology is the homology of the complex written above. Componentwise, the maps are simply the canonical maps into the localisations: at each step one additional variable is admitted as a denominator. These maps also carry the signs specified in the definition of the Čech complex.

We will describe this complex more precisely for the structure sheaf, that is, for $M=A$. It is useful to split it into simpler complexes using the fine monomial grading by the group $\mathbb Z^n$. We begin with small dimensions.

<!-- upstream_entity: Polynomring/2/Cech-Kohomologie/Beispiel -->

### Example 27.1: two variables {#br-bgk-2019-l27-exm-01}

Let $A=R[X,Y]$. The Čech complex of the structure sheaf $\mathcal O_{\mathbb A_R^2}$ on $U=D(X)\cup D(Y)\subset\mathbb A_R^2$ is

$$
0\longrightarrow A_X\times A_Y
\longrightarrow A_{XY}\longrightarrow0.
$$

This complex is compatible with the fine monomial grading. The component corresponding to $(\alpha,\beta)\in\mathbb Z^2$ depends essentially on whether the two exponents are negative or nonnegative.

If $\alpha$ and $\beta$ are both nonnegative, the entire complex in that component is

$$
(A_X\times A_Y)_{(\alpha,\beta)}
=R\cdot X^\alpha Y^\beta\oplus R\cdot X^\alpha Y^\beta
\longrightarrow R\cdot X^\alpha Y^\beta\longrightarrow0.
$$

This complex is exact at the right-hand term, and the kernel at the left-hand term is isomorphic to $R\cdot X^\alpha Y^\beta$.

If $\alpha$ is negative and $\beta$ is nonnegative, or vice versa, the entire complex is

$$
(A_X\times A_Y)_{(\alpha,\beta)}
=R\cdot X^\alpha Y^\beta\oplus0
\longrightarrow R\cdot X^\alpha Y^\beta\longrightarrow0,
$$

and this complex is exact. If $\alpha$ and $\beta$ are both negative, the entire complex is

$$
(A_X\times A_Y)_{(\alpha,\beta)}
=0\oplus0\longrightarrow R\cdot X^\alpha Y^\beta\longrightarrow0,
$$

and the homology at the right-hand term is $R\cdot X^\alpha Y^\beta$. Consequently,

$$
\check H^0(D(X),D(Y),\mathcal O_{\mathbb A_R^2})
=\bigoplus_{(\alpha,\beta)\in\mathbb N^2}
R\cdot X^\alpha Y^\beta=A
$$

and

$$
\check H^1(D(X),D(Y),\mathcal O_{\mathbb A_R^2})
=\bigoplus_{(\alpha,\beta)\in\mathbb Z_-^2}
R\cdot X^\alpha Y^\beta.
$$

<!-- upstream_entity: Polynomring/3/Cech-Kohomologie/Beispiel -->

### Example 27.2: three variables {#br-bgk-2019-l27-exm-02}

Let $A=R[X,Y,Z]$. The Čech complex of the structure sheaf is

$$
0\longrightarrow A_X\times A_Y\times A_Z
\longrightarrow A_{XY}\times A_{XZ}\times A_{YZ}
\longrightarrow A_{XYZ}\longrightarrow0.
$$

This complex is compatible with the fine monomial grading. Here $\check H^0=A$, while $\check H^1=0$ (see Theorem 27.3), and $\check H^2$ is the free $R$-module with basis

$$
X^iY^jZ^k,
\qquad (i,j,k)\in\mathbb Z_-^3.
$$

<!-- upstream_entity: Polynomring/n/Cech-Kohomologie/Berechnung/Fakt -->

### Theorem 27.3: cohomology of the punctured cover {#br-bgk-2019-l27-thm-01}

Let $R$ be a commutative ring and let $A=R[X_1,\ldots,X_n]$ be the polynomial ring in $n\geq2$ variables over $R$. Then the Čech cohomology of the structure sheaf on the open set $U=D(X_1,\ldots,X_n)$ with respect to the cover $D(X_i)$, $i=1,\ldots,n$, is

$$
\check H^p(D(X_i),\mathcal O_{\mathbb A_R^n})
=
\begin{cases}
A,&p=0,\\
0,&1\leq p\leq n-2,\\
\displaystyle\bigoplus_{\alpha\in\mathbb Z_-^n}
R\cdot X^\alpha,&p=n-1.
\end{cases}
$$

#### Proof {#br-bgk-2019-l27-thm-01-proof}

We consider the Čech complex with the fine $\mathbb Z^n$-grading given by the monomials. For a fixed tuple

$$
\alpha=(\alpha_1,\ldots,\alpha_n)\in\mathbb Z^n,
$$

let $N=N_\alpha\subseteq\{1,\ldots,n\}$ be the set of indices with negative entries. For this $\alpha$,

$$
\begin{aligned}
\bigl(\check C^p(D(X_i),\mathcal O_{\mathbb A^n})\bigr)_\alpha
&=\left(
\prod_{1\leq i_0<i_1<\cdots<i_p\leq n}
A_{X_{i_0}X_{i_1}\cdots X_{i_p}}
\right)_\alpha\\
&=\prod_{\substack{N\subseteq L\\\#(L)=p+1}}
R\cdot e_L\\
&\cong
\prod_{\substack{J\subseteq\{1,\ldots,n\}\setminus N\\
\#(J)=p+1-\#(N)}}R\cdot e_J.
\end{aligned}
$$

The middle identification rests on the fact that the component of $A_{\prod_{i\in L}X_i}$ is $0$ when $N\nsubseteq L$ and is $R\cdot X^\alpha$ when $N\subseteq L$. The monomial $X^\alpha$ in this localisation corresponds to $e_L$. In the right-hand identification, $e_J$ corresponds to the basis element $e_L=e_{N\cup J}$.

Thus, after shifting degrees by $\#(N)-1$ and changing basis signs in the usual way, the complex at index $\alpha$ corresponds to an ascending binomial complex for the index set $\{1,\ldots,n\}\setminus N$ over the ring $R$ (rather than $\mathbb Z$). If $N\ne\varnothing$, its empty-set summand occurs in Čech degree $\#(N)-1$; only when $N=\varnothing$ would that summand occur in degree $-1$, and it is then absent from the Čech complex.

> **Edition note—empty-set summand.** The frozen source says without qualification that the corresponding binomial complex lacks the free summand indexed by the empty set. The component formula shows that this is true only for $N=\varnothing$; for nonempty $N$ the summand occurs in degree $\#(N)-1$. The degree shift and harmless basis-sign changes needed to identify the differentials have also been made explicit.

For $p=0$ and at least one negative exponent, there is at most one isolated $R\cdot X^\alpha$ on the right. Since $n\geq2$, however, this term does not map to $0$, and so contributes nothing to $H^0$. If all exponents are nonnegative, by contrast, the elements have the form

$$
(c_1X^\alpha,\ldots,c_nX^\alpha),
$$

and such an element maps to $0$ precisely when all coefficients $c_i\in R$ agree. The zeroth Čech cohomology is therefore the polynomial ring

$$
A=\bigoplus_{\alpha\in\mathbb N^n}R\cdot X^\alpha.
$$

Now let $p\geq1$. If $N\ne\{1,\ldots,n\}$, the situation is isomorphic to an ascending binomial complex on a nonempty index set. Its homology is therefore trivial by Appendix Lemma 8.11. Hence the homology is trivial for every $p$ between $1$ and $n-2$.

It remains to consider $p=n-1$ and $N=\{1,\ldots,n\}$. These are precisely the $\alpha$ with all exponents negative. The complex, corresponding to the ascending binomial complex on the empty set, is

$$
0\longrightarrow R\cdot X^\alpha\longrightarrow0.
$$

Therefore,

$$
H^{n-1}=\bigoplus_{\alpha\in\mathbb Z_-^n}R\cdot X^\alpha.
$$

## Cohomology on projective schemes {#br-bgk-2019-l27-s02}

<!-- upstream_entity: Projektiver Raum/Getwistete Strukturgarbe/Garbenkohomologie/Fakt -->

### Theorem 27.4: cohomology of twisted structure sheaves {#br-bgk-2019-l27-thm-02}

Let $R$ be a commutative ring, let $A=R[X_0,X_1,\ldots,X_d]$ be the polynomial ring in $d+1\geq2$ variables over $R$, and let

$$
\mathbb P_R^d=\operatorname{Proj}(A)
$$

be the associated projective space. Then the cohomology of the twisted structure sheaf $\mathcal O_{\mathbb P_R^d}(n)$ is

$$
\check H^p(\mathbb P_R^d,\mathcal O_{\mathbb P_R^d}(n))
=
\begin{cases}
A_n,&p=0,\\
0,&1\leq p\leq d-1,\\
\displaystyle
\bigoplus_{\substack{\alpha\in\mathbb Z_-^{d+1}\\
\sum_{j=1}^{d+1}\alpha_j=n}}
R\cdot X^\alpha,&p=d.
\end{cases}
$$

#### Proof {#br-bgk-2019-l27-thm-02-proof}

This follows from Theorem 27.3.

In particular, for the canonical sheaf $\mathcal O_{\mathbb P_R^d}(-d-1)$ (compare Corollary 19.10),

$$
H^d(\mathbb P_R^d,\mathcal O_{\mathbb P_R^d}(-d-1))
=RX_0^{-1}X_1^{-1}\cdots X_d^{-1}\cong R,
$$

and

$$
H^d(\mathbb P_R^d,\mathcal O_{\mathbb P_R^d}(n))=0
$$

for $n>-d-1$.

> **Edition note—index in the canonical generator.** The frozen source specifies the variables $X_0,\ldots,X_d$, but writes $X_n^{-1}$ as the final factor of the generator. The display above corrects that final index to $d$; its product then uses each of the $d+1$ variables exactly once and has degree $-d-1$.

<!-- upstream_entity: Projektiver Raum/Kohärente Garbe/Endlichkeitssatz/Fakt -->

### Theorem 27.5: finiteness of cohomology on projective space {#br-bgk-2019-l27-thm-03}

Let $\mathbb P_R^n$ be projective space over a Noetherian ring $R$, and let $\mathcal F$ be a coherent sheaf on $\mathbb P_R^n$. Then $H^i(\mathbb P_R^n,\mathcal F)$ is a finitely generated $R$-module.

#### Proof {#br-bgk-2019-l27-thm-03-proof}

For the twisted structure sheaves $\mathcal O_{\mathbb P_R^n}(\ell)$, the assertion follows from Theorem 27.4. It therefore also holds for finite direct sums of such sheaves.

We prove the general case by descending induction on the cohomological index $i$. If this index exceeds $n$, there is only trivial cohomology by Theorem 26.10. If $R$ has finite dimension, the same also follows from Theorem 25.12. This establishes the base case.

Suppose, then, that the assertion has been proved for some $i$ and every coherent sheaf. Let $\mathcal F$ be a coherent sheaf. By Theorem 15.13, there are a finite direct sum

$$
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^n}(\ell_j)
$$

and a surjective $\mathcal O_{\mathbb P_R^n}$-module homomorphism

$$
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^n}(\ell_j)
\longrightarrow\mathcal F.
$$

Let $\mathcal G$ be the kernel of this map; by Exercise 14.20, $\mathcal G$ is also coherent. The long exact cohomology sequence associated with the short exact sequence of sheaves

$$
0\longrightarrow\mathcal G\longrightarrow
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^n}(\ell_j)
\longrightarrow\mathcal F\longrightarrow0
$$

contains the portion

$$
\cdots\longrightarrow
H^{i-1}\!\left(\mathbb P_R^n,
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^n}(\ell_j)\right)
\xrightarrow{\epsilon}
H^{i-1}(\mathbb P_R^n,\mathcal F)
\xrightarrow{\delta}
H^i(\mathbb P_R^n,\mathcal G)
\longrightarrow\cdots.
$$

This gives a short exact sequence of $R$-modules

$$
0\longrightarrow\operatorname{im}\epsilon
=\ker\delta\longrightarrow
H^{i-1}(\mathbb P_R^n,\mathcal F)
\longrightarrow\operatorname{im}\delta\longrightarrow0.
$$

By the preceding observation and the induction hypothesis,

$$
H^{i-1}\!\left(\mathbb P_R^n,
\bigoplus_{j\in J}\mathcal O_{\mathbb P_R^n}(\ell_j)\right)
\quad\text{and}\quad
H^i(\mathbb P_R^n,\mathcal G)
$$

are finitely generated $R$-modules. Hence $\operatorname{im}\epsilon$ is finitely generated. Moreover, since $R$ is Noetherian, $\operatorname{im}\delta$, as a submodule of $H^i(\mathbb P_R^n,\mathcal G)$, is finitely generated by Theorem 10.4 in *Algebraic Curves (Osnabrück 2025-2026)*. By Lemma 23.2 in *Commutative Algebra*, $H^{i-1}(\mathbb P_R^n,\mathcal F)$ is likewise finitely generated.

> **Edition note—two inconsistencies in the source proof.** The source calls the displayed homomorphism an $\mathcal O_{\mathbb P_R^d}$-module homomorphism, although its source and target lie on $\mathbb P_R^n$; the index has been corrected to $n$. It also repeats finite generation of $\ker\delta=\operatorname{im}\epsilon$, whereas the second end term needed in the displayed short exact sequence is $\operatorname{im}\delta$. The proof above corrects that object and uses the stated Noetherian hypothesis to pass to the submodule $\operatorname{im}\delta\subseteq H^i(\mathbb P_R^n,\mathcal G)$.

<!-- upstream_entity: Projektive Varietät/Quasikohärente Garbe/Vorschub/Fakt -->

### Theorem 27.6: cohomology under a closed embedding {#br-bgk-2019-l27-thm-04}

Let $X$ be a projective scheme over a Noetherian ring $R$, with a closed embedding $X\subseteq\mathbb P_R^n$ in a projective space. Let $\mathcal G$ be a quasi-coherent sheaf on $X$, and let $j_*\mathcal G$ be its direct image sheaf. Then

$$
H^i(X,\mathcal G)=H^i(\mathbb P_R^n,j_*\mathcal G)
$$

for every $i$.

#### Proof {#br-bgk-2019-l27-thm-04-proof}

The direct image sheaf is again quasi-coherent. By Theorem 26.10, both sides can be computed using Čech cohomology for the standard affine cover $D_+(X_s)$ of projective space and the cover $X\cap D_+(X_s)$ of $X$. The resulting Čech complexes agree in their entirety, and hence so do their Čech cohomology groups.

<!-- upstream_entity: Projektive Varietät/Kohärente Garbe/Endlichkeitssatz/Fakt -->

### Theorem 27.7: finiteness of cohomology on projective schemes {#br-bgk-2019-l27-thm-05}

Let $X$ be a projective scheme over a Noetherian ring $R$ and let $\mathcal G$ be a coherent sheaf on $X$. Then $H^i(X,\mathcal G)$ is a finitely generated $R$-module.

#### Proof {#br-bgk-2019-l27-thm-05-proof}

This follows from Theorem 27.6 and Theorem 27.5.

Note that these are $R$-modules, not modules over the coordinate ring of $X$. In the most important case, where $R=K$ is a field, the cohomology groups are finite-dimensional vector spaces over $K$. Their dimensions are natural numbers associated with coherent sheaves on $X$ and, in a certain sense, characteristic of those sheaves. Taking the structure sheaf or the tangent sheaf on $X$ gives numbers, or invariants, characteristic of $X$ itself. In this context one uses the abbreviation

$$
h^i(\mathcal F)=\dim_K\bigl(H^i(X,\mathcal F)\bigr).
$$

For example, for a smooth projective curve $X$ over an algebraically closed field $K$, the vector-space dimension of $H^1(X,\mathcal O_X)$ is called the *genus* of the curve. This is its most important invariant. In the complex case, there is a direct connection with the topological shape of the curve as a one-dimensional complex manifold and a two-dimensional real manifold.

> **Edition note—source typo.** In the sentence about modules over the coordinate ring, the German source writes *Koordinatening*. The translation renders the intended term as “coordinate ring” without changing its mathematical content.

## The Euler characteristic {#br-bgk-2019-l27-s03}

<!-- upstream_entity: Projektives Schema/Körper/Garbe/Euler-Charakteristik/Definition -->

### Definition 27.8: the Euler characteristic {#br-bgk-2019-l27-def-01}

Let $X$ be a projective scheme over a field $K$. For a coherent sheaf $\mathcal G$, the number

$$
\chi(\mathcal G)
:=\sum_{i=0}^{\dim(X)}(-1)^ih^i(X,\mathcal G)
$$

is called the *Euler characteristic* of $\mathcal G$.

By Theorem 27.7, this expression is a well-defined integer. Since cohomology is $0$ above the dimension, the alternating sum could also be continued to infinity.

<!-- upstream_entity: Projektives Schema/Körper/Garbe/Euler-Charakteristik/Additivität/Fakt -->

### Lemma 27.9: additivity of the Euler characteristic {#br-bgk-2019-l27-lem-01}

Let $X$ be a projective scheme over a field $K$. The Euler characteristic of coherent sheaves on $X$ is additive in short exact sequences. In other words, for a short exact sequence of coherent sheaves

$$
0\longrightarrow\mathcal F\longrightarrow\mathcal G
\longrightarrow\mathcal H\longrightarrow0,
$$

we have

$$
\chi(\mathcal G)=\chi(\mathcal F)+\chi(\mathcal H).
$$

#### Proof {#br-bgk-2019-l27-lem-01-proof}

This follows from the associated long exact cohomology sequence, Theorem 25.12, and the dimension formula.
