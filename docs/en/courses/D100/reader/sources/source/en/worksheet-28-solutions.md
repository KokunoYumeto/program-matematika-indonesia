---
title: "Public Solutions to Worksheet 28"
stable_id: br-ak-2012-w28-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributors: "Exercise 28.10: Bocardodarapti"
upstream_map: authority/wikiversity/unit-28/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: c5aed5500f44a39bbe0a7a079792e0da11781a24a69c274d7170b0e2cdc1df40
authority_manifest: authority/wikiversity/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f2e34fc420c4beec300ea9e0accc52598e12c27f46c9022611996b1b43e29a99
public_solution_count: 1
negative_public_solution_count: 13
upstream_solution_revisions: "Exercise 28.10=1112869"
solution_xml_sha256: "10=b0ed23c137883f7304b18304e06b5fa5e02cce5ae81b966a5e23c428d84497be"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain their recorded CC BY-SA 2.0 Germany notice"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
correction_ids: "AGC-CORR-0122; REVIEW-AK-26-30-C08"
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 28 {#br-ak-2012-w28-solutions}

At the frozen revision boundary, the source provides a public solution only for Exercise 28.10. The frozen authority query reports the other thirteen candidate solution pages as absent. No additional solutions have been created for this edition.

<!-- upstream_solution: Ebene Kurve/y-x^3+x+2/Rationale Parametrisierung/Fortsetzung auf P^1/Aufgabe/Lösung; pageid=21591; revid=1112869 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1112869 -->

## Solution to Exercise 28.10 {#br-ak-2012-w28-sol-10}

Under the algebraically closed-field hypothesis stated in the reviewed exercise, an isomorphism is given by

$$
x\longmapsto(x,x^3-x-2)=(x,y).
$$

At the ring level, this map corresponds to the substitution homomorphism

$$
\begin{aligned}
K[X,Y]/(Y-X^3+X+2)&\longrightarrow K[X],\\
X&\longmapsto X,\\
Y&\longmapsto X^3-X-2.
\end{aligned}
$$

This homomorphism is well defined and surjective. Since $Y$ can be eliminated directly on the left, the source ring is isomorphic to $K[X]$. Thus the map is indeed an isomorphism of affine curves.

This isomorphism cannot be extended to an isomorphism with the projective line. The projective closure of the curve is

$$
\overline C
=
V_+(YZ^2-X^3+XZ^2+2Z^3).
$$

Exactly one point at infinity is added, namely $(0,1,0)$. In the affine neighbourhood $D_+(Y)$, this point becomes the origin on the affine curve

$$
V(Z^2-X^3+XZ^2+2Z^3).
$$

The origin has multiplicity two and is therefore not smooth.

> **Editorial bridge.** The lowest-degree term $Z^2$ explains this multiplicity two. Since the projective line is smooth, $\overline C$ is not isomorphic to $\mathbb P_K^1$.

> **Editorial note - singular/plural agreement.** The source uses a grammatical form referring to “points” but then gives exactly one point, $(0,1,0)$. The homogeneous equation also gives only that point. This edition translates the consistent mathematical meaning: exactly one point at infinity.
