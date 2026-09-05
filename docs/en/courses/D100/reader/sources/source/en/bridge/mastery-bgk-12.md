---
title: "BGK 12 Mastery - Reading the Projective Spectrum"
stable_id: d100-bridge-mastery-bgk-12
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_unit: 12
source_worksheet_revision: 660098
source_manifest: "authority/wikiversity-bgk/unit-12/UNIT_AUTHORITY_MANIFEST.json"
source_manifest_sha256: "0e83f8718364e1d902dbe961cbf142cc7fb61e4ebfc7537f24488d508334e914"
new_worked_solutions: 1
existing_source_solutions_counted: ["12.5", "12.10"]
non_endorsement: "Independent editorial material; does not imply endorsement or human checking by the source author or source institutions."
---

# BGK 12 mastery: reading the projective spectrum {#d100-bridge-mastery-bgk-12}

The exercise in this section comes from Holger Brenner and the Wikiversity course contributors. The following solution was independently written for this edition; it is not a public solution by Brenner and does not replace the source's record that no solution is available. The translated problem text and this editorial material remain under CC BY-SA 4.0. Production provenance: OpenAI Codex gpt-5.6-sol, Ultra. No endorsement by the source author or human checking is implied.

The three mastery items for Unit 12 comprise the new solution below and [source solution 12.5](bgk-reader.html#br-bgk-2019-w12-sol-ex05) and [source solution 12.10](bgk-reader.html#br-bgk-2019-w12-sol-ex10). Both source solutions retain their source-solution status and are not rewritten here.

## New item 1: the coordinate cross yields two projective points {#d100-bridge-mastery-bgk-12-new-01}

Source: [BGK Exercise 12.8](bgk-reader.html#br-bgk-2019-w12-ex08), identifier `Achsenkreuz/Projektives Spektrum/Aufgabe`, [revision 1082163](https://de.wikiversity.org/w/index.php?oldid=1082163). This statement uses the standard grading and an arbitrary field $K$, without assuming that $K$ is algebraically closed.

### Source exercise {#d100-bridge-mastery-bgk-12-new-01-problem}

Determine the projective spectrum of the coordinate cross

$$
\operatorname{Spek}(K[X,Y]/(XY))
$$

with the standard grading.

### Independent solution {#d100-bridge-mastery-bgk-12-new-01-solution}

Write

$$
A=K[X,Y]/(XY),\qquad x=\overline X,\qquad y=\overline Y.
$$

The degrees of $x$ and $y$ are one, so the irrelevant ideal is $A_+=(x,y)$. We seek all homogeneous prime ideals not containing $(x,y)$, together with their scheme structure.

**Determining the points.** For every prime ideal $\mathfrak p$ of $A$, the equality $xy=0$ gives $x\in\mathfrak p$ or $y\in\mathfrak p$. A prime ideal that is a point of $\operatorname{Proj}(A)$ cannot contain both. Suppose $x\in\mathfrak p$ but $y\notin\mathfrak p$. In

$$
A/(x)\cong K[y],
$$

the ideal $\mathfrak p/(x)$ is a homogeneous prime ideal not containing $y$. The only such ideal is $(0)$: every nonzero homogeneous polynomial in one variable has the form $cy^d$; if a proper homogeneous ideal contains such an element, then $d>0$, and primality forces $y$ into the ideal. Hence $\mathfrak p=(x)$. Interchanging $x$ and $y$, the other case gives $\mathfrak p=(y)$. Thus the set of points is exactly

$$
\operatorname{Proj}(A)=\{(x),(y)\}.
$$

This argument determines all homogeneous prime points, not just points already expressed in $K$-coordinates.

**Determining the scheme structure.** The standard opens $D_+(x)$ and $D_+(y)$ cover the projective spectrum. Since $x$ becomes a unit in $A_x$, the equation $xy=0$ forces $y=0$. Therefore

$$
A_x\cong K[x,x^{-1}],\qquad (A_x)_0=K.
$$

[Lemma 12.9](bgk-reader.html#br-bgk-2019-l12-lem-03), for the homogeneous element $x$ of degree one, gives

$$
D_+(x)\cong\operatorname{Spek}(K).
$$

Likewise, $D_+(y)\cong\operatorname{Spek}(K)$. Their intersection is empty, since a prime ideal cannot omit both $x$ and $y$ when $xy=0$. Hence

$$
\operatorname{Proj}(K[X,Y]/(XY))
\cong\operatorname{Spek}(K)\amalg\operatorname{Spek}(K).
$$

The point $(y)$ belongs to $D_+(x)$ and has coordinates $[1:0]$; the point $(x)$ belongs to $D_+(y)$ and has coordinates $[0:1]$. Each point is both open and closed, its local ring is $K$, and there is no hidden nilpotent structure. As an additional check, the global section ring is $K\times K$, since sections on the two disjoint components can be chosen independently.

### Checks and common mistakes {#d100-bridge-mastery-bgk-12-new-01-check}

The ideal $(x,y)$ represents the origin of the affine coordinate cross, but is not a point of the projective spectrum because it contains the irrelevant ideal. Each affine axis, on the other hand, contributes one projective point, not a projective line. The answer does not depend on $K$ being algebraically closed: the coordinate ring of each affine open is already exactly $K$.
