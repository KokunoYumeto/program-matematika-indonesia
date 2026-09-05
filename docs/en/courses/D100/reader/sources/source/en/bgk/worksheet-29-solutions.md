---
title: "Public solutions and coverage of Worksheet 29"
stable_id: br-bgk-2019-w29-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
worksheet_url: "https://de.wikiversity.org/wiki/Kurs:B%C3%BCndel,_Garben_und_Kohomologie_(Osnabr%C3%BCck_2019-2020)/Arbeitsblatt_29"
worksheet_permalink: "https://de.wikiversity.org/w/index.php?title=Kurs:B%C3%BCndel,_Garben_und_Kohomologie_(Osnabr%C3%BCck_2019-2020)/Arbeitsblatt_29&oldid=1069438"
worksheet_upstream_pageid: 110238
worksheet_upstream_revid: 1069438
worksheet_upstream_timestamp: "2026-02-05T20:36:09Z"
worksheet_upstream_mediawiki_sha1: fe4fc776bdfd80cb3337cfb807de3168abe73d09
worksheet_frozen_revision_contributor: "Bocardodarapti"
worksheet_revision_timestamp_display: "21:36 CET, 5 February 2026"
upstream_map: authority/wikiversity-bgk/unit-29/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 1ee8ba36620cda1bb7b7da82f277d42c0284c0c3858f368d517fc0206c00889c
authority_manifest: authority/wikiversity-bgk/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 376380a874b545579d61c100d1f66eac11bad854d76f7e586b10cd621e7a54f7
candidate_evidence: authority/wikiversity-bgk/unit-29/worksheet-solution-candidates-api.json
candidate_evidence_sha256: c59b055e355a4622417b3bb3341b8c36221c7d5726348a62796cd9a43c8f4bda
solution_ex05_url: "https://de.wikiversity.org/wiki/Projektion_weg_von_Punkt/Ebene/Generischer_Grad/Aufgabe/L%C3%B6sung"
solution_ex05_permalink: "https://de.wikiversity.org/w/index.php?title=Projektion_weg_von_Punkt/Ebene/Generischer_Grad/Aufgabe/L%C3%B6sung&oldid=1096531"
solution_ex05_upstream_pageid: 96768
solution_ex05_upstream_revid: 1096531
solution_ex05_mediawiki_sha1: a29ee211b9f7695de50dab32bbf7d363844eded6
solution_ex05_frozen_revision_contributor: "Arbota"
solution_ex05_revision_timestamp_display: "11:05, 15 June 2026"
solution_ex05_xml: authority/wikiversity-bgk/unit-29/solution-ex05.xml
solution_ex05_xml_sha256: 119bb8ead8b4a00f4c0cd8c405d5b3b0248ba21a0264172e49604a4cf63b38e8
solution_ex05_html: authority/wikiversity-bgk/unit-29/solution-ex05.html
solution_ex05_html_sha256: 99bc2e356cdb143feea7f3d7d38afcc91128e99f9acf676ab5e44c087e634273
solution_ex12_url: "https://de.wikiversity.org/wiki/Projektive_Gerade/Rationale_Funktion/u%2Bu_invers/Aufgabe/L%C3%B6sung"
solution_ex12_permalink: "https://de.wikiversity.org/w/index.php?title=Projektive_Gerade/Rationale_Funktion/u%2Bu_invers/Aufgabe/L%C3%B6sung&oldid=1095413"
solution_ex12_upstream_pageid: 116035
solution_ex12_upstream_revid: 1095413
solution_ex12_mediawiki_sha1: 3a7d36bb78a33db5ca7e00800b142cd643302e61
solution_ex12_frozen_revision_contributor: "Arbota"
solution_ex12_revision_timestamp_display: "20:37, 14 June 2026"
solution_ex12_xml: authority/wikiversity-bgk/unit-29/solution-ex12.xml
solution_ex12_xml_sha256: 1c775f102fbbff3abebe06129a1bc963c64f3ff446163aff22fa6832390c6a0c
solution_ex12_html: authority/wikiversity-bgk/unit-29/solution-ex12.html
solution_ex12_html_sha256: c2a5f0a4a22795e0072ac6ccd96b18c5ea421347c266c390cf761c9196198b56
exercise_count: 15
public_solution_count: 2
public_solution_numbers: "5, 12"
negative_public_solution_count: 13
negative_solution_numbers: "1-4, 6-11, 13-15"
license: "The frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public solutions and coverage of Worksheet 29 {#br-bgk-2019-w29-solutions}

At the frozen official-page revisions, the source provides exactly two public solutions among the 15 exercises, namely those to Exercises 29.5 and 29.12. The other thirteen exercise pages only offer to create a new solution. The absence of a public solution page is not replaced by a fabricated solution.

## Solution to Exercise 29.5 {#br-bgk-2019-w29-sol-ex05}

We consider a line $V_+(L)$ through the point $P$ and its associated affine complement,

$$
D_+(L)\cong \mathbb A_K^2.
$$

Without loss of generality, take

$$
P=(1,0,0)
$$

and $L=Z$. We may therefore assume that we are considering the affine projection

$$
\mathbb A_K^2\cong D_+(Z)
\longrightarrow
\mathbb A_K^1\cong D_+(Z),
\qquad
(x,y)\longmapsto y,
$$

and an affine curve $V(F)$ of degree $d$. The term $X^d$ occurs in $F$, since otherwise $P\in C$. We regard the polynomial $F$ as

$$
F=G_dX^d+G_{d-1}X^{d-1}+\cdots+G_1X+G_0
\in K[Y][X]\subset K(Y)[X].
$$

Here $G_i\in K[Y]$, while $G_d$ is constant. Since the curve is irreducible, $G_0\ne0$ if $d\geq2$ (for $d=1$, the whole assertion is immediate). We must show that, for all but finitely many $y\in K$, the polynomial

$$
F(y)=G_d(y)X^d+G_{d-1}(y)X^{d-1}+\cdots+G_1(y)X+G_0(y)
$$

has $d$ distinct roots. Since $F\in K(Y)[X]$ is irreducible and we are in characteristic $0$, the polynomial $F$ is separable. Thus $F$ and $F'$ are coprime, where $F'$ denotes the formal derivative with respect to $X$. Hence there are $S,T\in K(Y)$ such that

$$
SF+TF'=1.
$$

This means that there are polynomials $A,B,C\in K[Y]$ satisfying

$$
AF+BF'=C
$$

with $C\ne0$. The polynomial $C$ has only finitely many roots. For $y\in K$ with $C(y)\ne0$, we have

$$
A(y)F(y)+B(y)F(y)'=C(y),
$$

which means that $F(y)$ and $F(y)'=F'(y)$ are coprime in $K[X]$. Hence $F(y)$ and its derivative $F(y)'$ have no common root, so no root of $F(y)$ is multiple.

## Solution to Exercise 29.12 {#br-bgk-2019-w29-sol-ex12}

1. The linear system is not complete, because $\Gamma(\mathbb P_K^1,\mathcal O_{\mathbb P_K^1}(2))$ contains three linearly independent sections, namely

   $$
   WZ,\qquad W^2,\qquad Z^2.
   $$

2. By definition, the morphism associated with a family of global sections is defined on the invertibility loci of those sections. These are $D_+(WZ)$ and $D_+(W^2+Z^2)$. On the first locus, the map is given by

   $$
   D_+(WZ)\cong \mathbb A_K^1\setminus\{(0)\}
   \longrightarrow
   D_+(X)\cong \mathbb A_K^1,
   $$

   with

   $$
   \frac{Y}{X}
   \longmapsto
   \frac{W^2+Z^2}{WZ}
   =\frac{W}{Z}+\frac{Z}{W}
   =u^{-1}+u.
   $$

   On the second locus, the map is given by (here $\mathrm i$ denotes a square root of $-1$)

   $$
   D_+(W^2+Z^2)
   \cong
   \mathbb P_K^1\setminus\{(1,\mathrm i),(1,-\mathrm i)\}
   \longrightarrow
   D_+(Y)\cong \mathbb A_K^1,
   $$

   with

   $$
   \frac{X}{Y}
   \longmapsto
   \frac{WZ}{W^2+Z^2}
   =\frac{1}{u+u^{-1}}
   =\frac{u}{u^2+1}.
   $$

3. The system is base-point-free, since the two sets $D_+(WZ)$ and $D_+(W^2+Z^2)$ cover the projective line. Indeed, if

   $$
   P\notin D_+(WZ)\cup D_+(W^2+Z^2),
   $$

   then initially one coordinate must be $0$, but then the second coordinate is also $0$.

4. The extension of function fields

   $$
   K(t)\subseteq K(u)
   $$

   is given by $t\mapsto u+u^{-1}$. Its degree is $2$, since $u$ satisfies the quadratic equation

   $$
   u^2-(u+u^{-1})u+1=0
   $$

   over $K(t)$. The extension cannot be the identity extension, since, for example, $u\mapsto u^{-1}$ gives a nontrivial automorphism of the field $K(u)$ over $K(t)$.

5. Take $(x,y)\in\mathbb P_K^1$, and first suppose that both coordinates are nonzero. We use the affine description above, namely the map

   $$
   \mathbb A_K^1\setminus\{0\}
   \longrightarrow
   \mathbb A_K^1,
   \qquad
   u\longmapsto u+u^{-1}.
   $$

   The inverse image of a point $b$ consists of the solutions of $u+u^{-1}=b$, that is,

   $$
   u^2-bu+1=0,
   $$

   so

   $$
   u=\pm\frac12\sqrt{b^2-4}+\frac b2.
   $$

   Let $b\ne2,-2$, and let $a$ be an inverse image of $b$. For the local ring homomorphism

   $$
   K[t]_{(t-b)}\longrightarrow K[u]_{(u-a)},
   \qquad
   t\longmapsto u+u^{-1},
   $$

   we have

   $$
   t-b
   =u+u^{-1}-b
   =\frac1u(u^2-bu+1)
   =\frac1u(u-a^{-1})(u-a).
   $$

   The factor $\frac1u(u-a^{-1})$ is a unit, since $a\ne a^{-1}$ when $b\ne2,-2$, while $u-a$ is a uniformiser in $K[u]_{(u-a)}$. The ramification order is therefore $1$. For

   $$
   b=2,-2,
   $$

   there is only the inverse image $1$, respectively $-1$. For the local ring homomorphism

   $$
   K[t]_{(t-2)}\longrightarrow K[u]_{(u-1)},
   $$

   we have

   $$
   t-2
   =u+u^{-1}-2
   =\frac1u(u^2-2u+1)
   =\frac1u(u-1)^2,
   $$

   and the ramification order is $2$. The same holds for $b=-2$.

   The inverse image of zero in $D_+(X)$, namely $(1,0)$ (or $(Y)$), consists of $(W-\mathrm iZ)$ and $(W+\mathrm iZ)$. The local ring homomorphism is

   $$
   K[t]_{(t)}\longrightarrow K[u]_{(u-\mathrm i)},
   $$

   and since

   $$
   t=u+u^{-1}
   =\frac1u(u^2+1)
   =\frac1u(u+\mathrm i)(u-\mathrm i),
   $$

   the ramification order is $1$. The inverse image of the point at infinity, namely $(0,1)$ or $(X)$, consists of $(1,0)$ and $(0,1)$. The local ring homomorphism is, on the one hand,

   $$
   K[t^{-1}]_{(t^{-1})}\longrightarrow K[u]_{(u)},
   $$

   with

   $$
   t^{-1}=\frac{u}{u^2+1},
   $$

   so its ramification index is $1$, and, on the other hand,

   $$
   K[t^{-1}]_{(t^{-1})}
   \longrightarrow
   K[u^{-1}]_{(u^{-1})},
   $$

   with

   $$
   t^{-1}
   =\frac{u}{u^2+1}
   =\frac{u\cdot u^{-2}}{(u^2+1)\cdot u^{-2}}
   =\frac{u^{-1}}{1+u^{-2}},
   $$

   and this also has ramification order $1$.

   > **Edition note (source).** For a root $a$ of $u^2-bu+1$, the other root is $a^{-1}$, so the source's factorisation $(u+a)(u-a)$ has been corrected to $(u-a^{-1})(u-a)$. The source also calls the point $(0,1)$ the ideal $(Y)$ immediately after using the convention identifying $(Y)$ with $(1,0)$; it has been corrected to $(X)$.

6. We need to determine the principal divisor of $u+u^{-1}$ on the projective line. If

   $$
   u=0,\infty,
   $$

   there is a pole, in each case of order $1$. Elsewhere $u+u^{-1}$ is defined and has two simple roots, $\mathrm i$ and $-\mathrm i$. Its principal divisor is therefore, in coordinate notation viewed from the affine line $D_+(W)$,

   $$
   1\cdot(\mathrm i)+1\cdot(-\mathrm i)
   -1\cdot(0)-1\cdot(\infty),
   $$

   or, expressed in terms of homogeneous prime ideals of height $1$,

   $$
   1\cdot(W-\mathrm iZ)+1\cdot(W+\mathrm iZ)
   -1\cdot(W)-1\cdot(Z).
   $$

## Frozen negative results {#br-bgk-2019-w29-solutions-negative}

There are no public solution pages at the checked exercise-page revisions for Exercises 29.1, 29.2, 29.3, 29.4, 29.6, 29.7, 29.8, 29.9, 29.10, 29.11, 29.13, 29.14, or 29.15. On each of these pages, the solution control reads “Eine Lösung erstellen” (“Create a solution”). This statement records the result of checking the official links, not a claim that mathematical solutions do not exist.
