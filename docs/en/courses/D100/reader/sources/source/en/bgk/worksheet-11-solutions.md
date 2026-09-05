---
title: "Public Solutions and Coverage of Worksheet 11"
stable_id: br-bgk-2019-w11-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-11/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 44c6b2f4a86976163360cf7d0b0b60e39334ec54336e8483249431039365c161
authority_manifest: authority/wikiversity-bgk/unit-11/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: c55c715d0a1bd3ef5b13ac96ccf38f9b5c261e87124c6da5ccc5984cb61deb09
candidate_evidence: authority/wikiversity-bgk/unit-11/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 18795e45391de20c07918171f5dadf47b6ea04fde24113964d3461eddfe801c4
solution_ex09_xml: authority/wikiversity-bgk/unit-11/solution-ex09.xml
solution_ex09_xml_sha256: c1a8e3d35f3aed5ffe5e37f8f36bf009d1b17d0b4034d2ccbbe69bd6e82ace94
solution_ex09_html: authority/wikiversity-bgk/unit-11/solution-ex09.html
solution_ex09_html_sha256: 3cc9ed5fb74ba0f1fae953a479aaecd48eaf8664b2cb15ea5e8aab17d4954b2e
solution_ex09_upstream_pageid: 46303
solution_ex09_upstream_revid: 1106651
solution_ex09_mediawiki_sha1: de4c7d8f5839897ae9b847696318aa8d64677481
solution_ex09_frozen_revision_contributor: "Arbota"
solution_ex13_xml: authority/wikiversity-bgk/unit-11/solution-ex13.xml
solution_ex13_xml_sha256: 9a03466ce3c08e5afe63c17c7584c7fa863c2e1a3e208eba3bcf7b52d37ef10b
solution_ex13_html: authority/wikiversity-bgk/unit-11/solution-ex13.html
solution_ex13_html_sha256: 95fe2bf8bacce3a9b38c34e509f8c1c67a1452d0ea47471a2d77df9ae19d8f26
solution_ex13_upstream_pageid: 112468
solution_ex13_upstream_revid: 1089753
solution_ex13_mediawiki_sha1: c20228f9acca9fdea22e7c0c2f3b6c89f1905031
solution_ex13_frozen_revision_contributor: "Arbota"
solution_ex14_xml: authority/wikiversity-bgk/unit-11/solution-ex14.xml
solution_ex14_xml_sha256: 50e0903c021187f4476febca48565085083f3ed6215351084be9bdf7e963d0ce
solution_ex14_html: authority/wikiversity-bgk/unit-11/solution-ex14.html
solution_ex14_html_sha256: af692e48d0804abe49a6d40dcb4696c5a1197d26a36c71953e046be1878b5f96
solution_ex14_upstream_pageid: 112464
solution_ex14_upstream_revid: 1089757
solution_ex14_mediawiki_sha1: a866b421baa8b504355e926d0dea7a39f6cbbe09
solution_ex14_frozen_revision_contributor: "Arbota"
exercise_count: 19
public_solution_count: 3
public_solution_numbers: "9, 13, 14"
negative_public_solution_count: 16
negative_solution_numbers: "1-8, 10-12, 15-19"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 11 {#br-bgk-2019-w11-solutions}

At the frozen revision boundary, the source provides exactly three public solutions among the 19 exercises, namely those for Exercises 11.9, 11.13, and 11.14. The exercise map and candidate evidence record negative results for Exercises 11.1-11.8, 11.10-11.12, and 11.15-11.19. No new solutions have been created for this edition.

## Source solution to Exercise 11.9 {#br-bgk-2019-w11-ex09-solution}

> **Editorial note - dimension zero.** The source's coordinate construction below applies when $n\geq1$. If $n=0$, the required chain consists simply of $M_0=M$.

Choose a point $P\in M$ and an open coordinate neighbourhood $P\in U$ together with a chart

$$
\alpha:U\longrightarrow V\subseteq\mathbb R^n,
$$

where $V=B(0,3)$ is the open ball centred at $0$ with radius $3$ and $\alpha(P)=0$. For $i=0,\ldots,n-1$, set

$$
B_i=\left\{
x\in V\ \middle|\
(x_1-1)^2+x_2^2+\cdots+x_n^2=1,
\ x_{i+2}=\cdots=x_n=0
\right\}.
$$

Thus $B_{n-1}$ is the sphere centred at $(1,0,\ldots,0)$ with radius $1$, while $B_{n-2}$ is its “equator” defined by $x_n=0$, and so on. The set $B_i$ is obtained from $B_{i+1}$ by adding the equation $x_{i+2}=0$. We therefore have a descending chain of closed subsets

$$
B_{n-1}\supseteq B_{n-2}\supseteq\cdots\supseteq B_1\supseteq B_0,
$$

and

$$
B_0=\{(0,0,\ldots,0),(2,0,\ldots,0)\}.
$$

We can regard $B_i$ as the fibre over the origin of the map

$$
\begin{aligned}
\varphi_i:V&\longrightarrow\mathbb R^{n-i},\\
(x_1,\ldots,x_n)&\longmapsto
\bigl((x_1-1)^2+x_2^2+\cdots+x_n^2-1,
x_{i+2},\ldots,x_n\bigr).
\end{aligned}
$$

Its Jacobian matrix is

$$
D\varphi_i(x)=
\begin{pmatrix}
2x_1-2&2x_2&\cdots&2x_{i+1}&2x_{i+2}&\cdots&2x_n\\
0&0&\cdots&0&1&\cdots&0\\
\vdots&\vdots&&\vdots&&\ddots&\vdots\\
0&0&\cdots&0&0&\cdots&1
\end{pmatrix}.
$$

The rank of this matrix is less than $n-i$ only if

$$
x_1=1,
\qquad
x_2=\cdots=x_{i+1}=0,
$$

and such a point does not lie on $B_i$. Thus $\varphi_i$ is regular along the fibre $B_i$. By the implicit function theorem, $B_i$ is a closed submanifold of $V$ of dimension $i$.

Now set

$$
M_i=\alpha^{-1}(B_i)
\quad(0\le i\le n-1),
\qquad
M_n=M.
$$

Since each $B_i$ is compact, $M_i$ is also closed in $M$. Being a closed submanifold is a local property, so all the $M_i$ are closed submanifolds of $M$ of the required dimensions.

> **Editorial note - index bounds and the source's two points.** The source solution initially defines $B_i$ and $M_i$ only for $i=1,\ldots,n-1$, but then uses $B_0$ and a chain requiring $M_0$. This edition includes $i=0$ in both ranges. The source also states that $B_0$ consists of the points $(\pm1,0,\ldots,0)$; substitution into the equation of the sphere centred at $(1,0,\ldots,0)$ gives the correct points $(0,0,\ldots,0)$ and $(2,0,\ldots,0)$. The formulae, rank calculation, and submanifold construction are otherwise preserved.

## Source solution to Exercise 11.13 {#br-bgk-2019-w11-ex13-solution}

Since the spectrum is quasicompact, we may assume that $I$ is finite. By Proposition 8.4(9), the elements $f_i$ generate the unit ideal.

Let $(a_j)_{j\in J}$ be a generating system for the ideal $\mathfrak a$. Viewed in $R_{f_i}$, it also generates $\mathfrak aR_{f_i}$. For each $i$, a finite subsystem suffices; since $I$ is finite, the union of the required index sets is a finite subset $J_0\subseteq J$. Thus $(a_j)_{j\in J_0}$ generates every $\mathfrak aR_{f_i}$.

We claim that these elements already generate $\mathfrak a$. Let $b\in\mathfrak a$. For each $i$, there is an equality in $R_{f_i}$

$$
b=\sum_{j\in J_0}\frac{c_{ij}}{f_i^{n_{ij}}}a_j.
$$

Clearing denominators gives an equality in $R$ of the form

$$
f_i^{m_i}b=\sum_{j\in J_0}d_{ij}a_j.
$$

Since the sets $D(f_i^{m_i})=D(f_i)$ still cover the spectrum, there are $g_i\in R$ with

$$
\sum_{i\in I}g_if_i^{m_i}=1.
$$

Consequently,

$$
\begin{aligned}
b
&=b\left(\sum_{i\in I}g_if_i^{m_i}\right)\\
&=\sum_{i\in I}g_i b f_i^{m_i}\\
&=\sum_{i\in I}g_i\left(\sum_{j\in J_0}d_{ij}a_j\right)\\
&=\sum_{j\in J_0}\left(\sum_{i\in I}g_id_{ij}\right)a_j.
\end{aligned}
$$

Thus every $b\in\mathfrak a$ is a linear combination of $(a_j)_{j\in J_0}$, so $\mathfrak a$ is finitely generated.

## Source solution to Exercise 11.14 {#br-bgk-2019-w11-ex14-solution}

Clearly, if $R$ is a noetherian ring, then $X=\operatorname{Spek}(R)$ is a noetherian scheme.

Conversely, suppose that $X$ is a noetherian scheme. Choose a finite affine cover

$$
X=\bigcup_{i\in I}U_i,
\qquad
U_i=\operatorname{Spek}(R_i),
$$

with each $R_i$ a noetherian ring. Since $U_i$ is open in $X=\operatorname{Spek}(R)$ and quasicompact, for each $i$ there are finitely many $f_{ij}\in R$ such that

$$
U_i=\bigcup_{j\in J_i}D_X(f_{ij}).
$$

If

$$
\rho_i:R=\Gamma(X,\mathcal O_X)
\longrightarrow R_i=\Gamma(U_i,\mathcal O_X)
$$

is the restriction, then

$$
D_X(f_{ij})=D_{U_i}(\rho_i(f_{ij})).
$$

The ring of sections on this principal open subset is therefore

$$
R_{f_{ij}}
\cong (R_i)_{\rho_i(f_{ij})},
$$

which is noetherian as a localisation of a noetherian ring. Combining all $i$ and $j$, we obtain a finite principal open cover

$$
X=\bigcup_{k=1}^N D(g_k)
$$

with every $R_{g_k}$ noetherian. For any ideal $\mathfrak a\subseteq R$, each ideal $\mathfrak aR_{g_k}$ is finitely generated. Exercise 11.13 now shows that $\mathfrak a$ is finitely generated. Hence every ideal of $R$ is finitely generated, and $R$ is noetherian.

> **Editorial note - notation in the source solution.** The source solution writes $U_i=\bigcup_{j\in J_i}D(f_j)$, with the index $i$ subsequently disappearing, uses $f_j\in R$, then places $\rho(f_j)$ in the ring of sections of an undefined set $U$ and writes a localisation with only the subscript $f$. This edition explicitly writes $f_{ij}$, the restriction $\rho_i:R\to R_i$, and the isomorphism $R_{f_{ij}}\cong(R_i)_{\rho_i(f_{ij})}$. These are the data used in the source argument; no new hypothesis is introduced.
