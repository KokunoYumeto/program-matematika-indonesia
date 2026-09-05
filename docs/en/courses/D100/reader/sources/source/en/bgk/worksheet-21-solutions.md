---
title: "Public Solutions and Coverage of Worksheet 21"
stable_id: br-bgk-2019-w21-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-21/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 69b9ecd0120626c3e4c8dc018862869b13316fa3e6c76edf5954807dcff6af65
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
authority_manifest: authority/wikiversity-bgk/unit-21/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 684637decc945c94137670f7c4238110b4a4c395287cf985b3f69adceedd9ef7
authority_manifest_status: "Terminal authority freeze complete; all 35 file records have been recomputed without discrepancies."
unit_capture_identity: authority/wikiversity-bgk/unit-21/CAPTURE_IDENTITY.json
unit_capture_identity_sha256: 869931efce9e3df0e42984b2db28fc367f93f113a8d632175ac0f9d7414cb791
candidate_evidence: authority/wikiversity-bgk/unit-21/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 19b8384f8a3e37828a2b5ae32f2e58809b7ac6169c6bff1b8f1649b4e4880782
solution_ex03_xml: authority/wikiversity-bgk/unit-21/solution-ex03.xml
solution_ex03_xml_sha256: 60fe2ce05a77cb26b8a5162a83d84a19730d7c3a047a8dfe3669a1f3f04b173f
solution_ex03_html: authority/wikiversity-bgk/unit-21/solution-ex03.html
solution_ex03_html_sha256: 78c5585f8e37afd8ad778659c80e8c0660a030a120c83c66c385ceda173996ec
solution_ex03_upstream_pageid: 168446
solution_ex03_upstream_revid: 1068126
solution_ex03_mediawiki_sha1: 2d751f629b7f48f92fc66b6815e702cb8293fd55
solution_ex03_frozen_revision_contributor: "Bocardodarapti"
solution_ex09_xml: authority/wikiversity-bgk/unit-21/solution-ex09.xml
solution_ex09_xml_sha256: 200f8252ec7abdbfa21215b1c20a0831046313dc323c2c47a93a8c076ffede3c
solution_ex09_html: authority/wikiversity-bgk/unit-21/solution-ex09.html
solution_ex09_html_sha256: 0d7f1aacadc6e39aed85e68f89217d7c78783f040dbd7ecb5612e67cb5cd4ca8
solution_ex09_upstream_pageid: 16847
solution_ex09_upstream_revid: 1113184
solution_ex09_mediawiki_sha1: 605715141b55061b2efc433f9bd039e84ec8fde0
solution_ex09_frozen_revision_contributor: "Arbota"
solution_ex10_xml: authority/wikiversity-bgk/unit-21/solution-ex10.xml
solution_ex10_xml_sha256: 9143a82da55b84ca3a4e3fdb436657ff0f60f8ff80eb01671bc0403771b74a41
solution_ex10_html: authority/wikiversity-bgk/unit-21/solution-ex10.html
solution_ex10_html_sha256: 9edb9f6dfee387bc9a8d04ab6933942c0839f10756eef96cf6b4905b7e4aa151
solution_ex10_upstream_pageid: 133994
solution_ex10_upstream_revid: 708101
solution_ex10_mediawiki_sha1: 35379260e96277d6323ce216cff7ac09a7a72b7f
solution_ex10_frozen_revision_contributor: "Bocardodarapti"
exercise_count: 13
public_solution_count: 3
public_solution_numbers: "3, 9, 10"
negative_public_solution_count: 10
negative_solution_numbers: "1-2, 4-8, 11-13"
media_credits: source/id-ID/media-credits-bgk-unit-21.md
media_credits_sha256: 07ef5ecaa38890028ebbc245b3511bfb3eb8a29b174c8802dd84a3492496d814
rights_ledger: authority/RIGHTS-bgk-unit-21.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-21.json
asset_closure_sha256: 5fd26087ca516efbb8cbc6823c3622338bd9272eb7ab1452c87ba41c6e28afdd
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 21 {#br-bgk-2019-w21-solutions}

At the frozen revision boundary, the source provides exactly three public
solutions among the 13 exercises: those for Exercises 21.3, 21.9, and 21.10.
The exercise map and candidate evidence record negative results for Exercises
21.1--21.2, 21.4--21.8, and 21.11--21.13. The absence of a public solution
page is not replaced by an invented solution.

<!-- upstream_solution: Diskreter Bewertungsring/Zwischenringe im Quotientenkörper/Aufgabe/Lösung; pageid=168446; revid=1068126 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1068126 -->

## Solution to Exercise 21.3 {#br-bgk-2019-w21-sol-ex03}

Let the maximal ideal of $R$ be

$$
\mathfrak m=(\pi).
$$

The field of fractions of $R$ is

$$
Q(R)=R_\pi,
$$

and every non-zero element of this field has the form

$$
u\pi^n,
\qquad
u\in R^\times,
\quad
n\in\mathbb Z.
$$

Let

$$
R\subset T\subseteq Q(R).
$$

Then there is an element

$$
u\pi^n\in T
$$

with $n<0$. But we then also have $\pi^n\in T$ and

$$
\pi^{-1}=\pi^{-n-1}\pi^n\in T.
$$

Thus $T=Q(R)$.

[Back to Exercise 21.3](worksheet-21.md#br-bgk-2019-w21-ex03).

<!-- upstream_solution: Bewertungstheorie/Körper mit diskreter Bewertung/Diskreter Bewertungsring/Aufgabe/Lösung; pageid=16847; revid=1113184 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1113184 -->

## Solution to Exercise 21.9 {#br-bgk-2019-w21-sol-ex09}

We first show that $R$ is a subring of the field $K$. We have

$$
0\in R.
$$

Since $\nu$ is a group homomorphism, we must have

$$
\nu(1)=0.
$$

For elements $f,g\in R$, we have

$$
\nu(f),\nu(g)\geq0,
$$

and, since $\nu$ is a group homomorphism,

$$
\nu(f\cdot g)=\nu(f)+\nu(g)\geq0,
$$

as well as, by hypothesis,

$$
\nu(f+g)\geq\min\{\nu(f),\nu(g)\}\geq0.
$$

Thus $R$ is closed under multiplication and addition. Furthermore,

$$
\nu(-1)+\nu(-1)
=\nu((-1)^2)
=\nu(1)
=0,
$$

so $\nu(-1)=0$ and $-1\in R$. Hence $R$ is also closed under taking
negatives and is a commutative ring.

Next, $R$ must be a local ring. We claim that

$$
\mathfrak m
:=\{f\in K^\times\mid\nu(f)\geq1\}\cup\{0\}
\subseteq R
$$

is its only maximal ideal. This set contains $0$, and since

$$
\nu(f+g)\geq\min\{\nu(f),\nu(g)\}\geq1,
$$

it is closed under addition. For $f\in\mathfrak m$ and $g\in R$, we have

$$
\nu(f)\geq1
\qquad\text{and}\qquad
\nu(g)\geq0,
$$

and hence

$$
\nu(gf)=\nu(g)+\nu(f)\geq1,
$$

so the set is closed under multiplication by elements of $R$.
Thus $\mathfrak m$ is an ideal.

The complement $R\setminus\mathfrak m$ consists exactly of the elements
$h\in K$ with

$$
\nu(h)=0.
$$

For such an element,

$$
\nu(h^{-1})=-\nu(h)=0,
$$

so $h^{-1}\in R$. All elements of $R\setminus\mathfrak m$ are therefore
units. Consequently, $\mathfrak m$ is a maximal ideal.

It remains to show that $R$ is a discrete valuation ring.
Take $p\in K$ with

$$
\nu(p)=1.
$$

Such an element exists because $\nu$ is assumed surjective.
We show that $p$ is a prime element. In general, for $x,y\in R$,
the element $y$ is a multiple of $x$ precisely when

$$
\nu(y)\geq\nu(x),
$$

since this condition is equivalent to $y/x\in R$. Now suppose that
$p\mid xy$ for $x,y\in R$. Then

$$
1=\nu(p)\leq\nu(xy)=\nu(x)+\nu(y).
$$

Thus $\nu(x)\geq1$ or $\nu(y)\geq1$, so one of $x$ and $y$ is a multiple
of $p$. Hence $p$ is a prime element.

By the same argument, every non-zero element $x\in R$ with

$$
n=\nu(x)
$$

is associated to $p^n$. Thus $R$ is a principal ideal domain with exactly
the ideals

$$
0
\qquad\text{and}\qquad
(p^n),
\quad n\in\mathbb N.
$$

> **Editorial note - domain of the valuation.** The source defines $\nu$
> only on $K^\times$, but in the solution it evaluates $\nu(f)$, $\nu(f+g)$,
> $\nu(gf)$, and $\nu(xy)$ for elements stated only to belong to $R$,
> although $0\in R$. This edition preserves the source proof without adding
> the convention $\nu(0)=\infty$ or separating the zero cases.

[Back to Exercise 21.9](worksheet-21.md#br-bgk-2019-w21-ex09).

<!-- upstream_solution: Ebene algebraische Kurve/Glatter Punkt/Lokaler Ring ist diskreter Bewertungsring/Fakt/Beweis/Aufgabe/Lösung; pageid=133994; revid=708101 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=708101 -->

## Solution to Exercise 21.10 {#br-bgk-2019-w21-sol-ex10}

First, $R$ is a Noetherian local ring which, by the
[source fact about components at a smooth point](https://de.wikiversity.org/wiki/Ebene_algebraische_Kurve/Glatter_Punkt/Liegt_nur_auf_einer_Komponente/Fakt),
is an integral domain. Its only prime ideals are therefore the zero ideal and
the maximal ideal $\mathfrak m_P$. We shall show that this maximal ideal
is principal.

We may assume that $P$ is the origin and write $F$ as

$$
F=F_d+\cdots+F_1
$$

with $F_1\ne0$. Such a form exists because $P$ is smooth. By a change of
variables, we can arrange that

$$
F_1=Y.
$$

In $F$, we can collect the isolated powers of $X$, namely the monomials
not involving $Y$, and factor $Y$ out of the remaining terms.
The equation $F=0$ can then be written as

$$
Y(1+G)=XH(X),
$$

where

$$
G\in(X,Y).
$$

The element $1+G$ is a unit in $K[X,Y]_{(X,Y)}$, and therefore also in
the local ring of the curve at the origin,

$$
R=K[X,Y]_{(X,Y)}/(F).
$$

Thus in $R$ we have the relation

$$
Y=\frac{H}{1+G}X.
$$

The maximal ideal in the local ring $R$ is therefore generated by $X$ alone.
By [Theorem 21.8](lecture-21.md#br-bgk-2019-l21-thm-01), $R$ is a discrete
valuation ring.

[Back to Exercise 21.10](worksheet-21.md#br-bgk-2019-w21-ex10).

## Frozen negative results {#br-bgk-2019-w21-solutions-negative}

There is no public solution page at the frozen revision for Exercises 21.1,
21.2, 21.4, 21.5, 21.6, 21.7, 21.8, 21.11, 21.12, or 21.13. This statement
records the candidate checks; it does not assert that mathematical solutions
do not exist.
