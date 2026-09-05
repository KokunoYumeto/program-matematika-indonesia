---
title: "Public Solutions and Coverage of Worksheet 22"
stable_id: br-bgk-2019-w22-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-22/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 34c6c4f31bffe001aad01da4c0e553cdfd5d6c36dd354e9e8f6a90823b555d67
authority_manifest: authority/wikiversity-bgk/unit-22/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 98e1716c4a8e95d42a19fd6a8b9efb04e222687e5bb6dc296ae42496baab1e39
candidate_evidence: authority/wikiversity-bgk/unit-22/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 20deb2ae2dbcfc9762afe05c51e10816d622799878b5be494be1c5de48ada343
solution_ex19_xml: authority/wikiversity-bgk/unit-22/solution-ex19.xml
solution_ex19_xml_sha256: 212720ed6ce5afff922d7a9133eba31df4e73c730eb32b4ac9d2a99177fc6cbc
solution_ex19_html: authority/wikiversity-bgk/unit-22/solution-ex19.html
solution_ex19_html_sha256: 09396548f95821022f71f47f343c5373d4e8270f177e2834423091da3d56c5f6
solution_ex19_upstream_title: "Fermat-Kubik/Projektiv/Disjunkte Geraden/Aufgabe/Lösung"
solution_ex19_upstream_pageid: 115918
solution_ex19_upstream_revid: 1089477
solution_ex19_upstream_timestamp: "2026-05-31T10:35:22Z"
solution_ex19_mediawiki_sha1: 4394016a5f0bad50ae7047a33f765ed1650e2e54
solution_ex19_frozen_revision_contributor: "Arbota"
solution_ex19_source_url: "https://de.wikiversity.org/w/index.php?oldid=1089477"
exercise_count: 20
public_solution_count: 1
public_solution_numbers: "19"
negative_public_solution_count: 19
negative_solution_numbers: "1-18, 20"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete_semantic_authority_bound
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
rights_ledger: authority/RIGHTS-bgk-unit-22.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-22.json
asset_closure_sha256: e7bf39c238717349b7d2e02a8f05eb252fe6aa39199bce82a8c9f60d1b5ea718
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 22 {#br-bgk-2019-w22-solutions}

The candidate-title checks recorded by QA, based on the sequence of
20 exercises in the frozen worksheet revision, found exactly one public
solution page: the solution to Exercise 22.19. The results were negative
for Exercises 22.1--22.18 and 22.20. The absence of a public solution
page is not replaced by an invented solution.

## Solution to Exercise 22.19 {#br-bgk-2019-w22-sol-ex19}

We write the defining equation as

$$
\begin{aligned}
F
&=X^3-Z^3+Y^3-W^3\\
&=(X-Z)(X-\zeta Z)(X-\zeta^2Z)
 +(Y-W)(Y-\zeta W)(Y-\zeta^2W),
\end{aligned}
$$

where $\zeta$ is a third root of unity. Thus, for example,

$$
F\in(X-Z,Y-W)
$$

and

$$
F\in(X-\zeta Z,Y-\zeta W).
$$

Hence

$$
L_1=V_+(X-Z,Y-W),
\qquad
L_2=V_+(X-\zeta Z,Y-\zeta W)
\subseteq V_+(F).
$$

As intersections of two distinct projective planes, $L_1$ and $L_2$
are lines. Their intersection is

$$
\begin{aligned}
L_1\cap L_2
&=V_+(X-Z,Y-W),\ L_2\cap V_+(X-\zeta Z,Y-\zeta W)\\
&=V_+(X-Z,Y-W,X-\zeta Z,Y-\zeta W)\\
&=V_+(X-Z,X-\zeta Z,Y-W,Y-\zeta W)\\
&=V_+(X,Z,Y,W)\\
&=\varnothing.
\end{aligned}
$$

> **Editorial note - first line of the intersection chain.** The first line
> of the source display prints a comma, repeats $L_2$, and then writes
> a second intersection. This edition preserves that line as in the source;
> the subsequent lines give the combined ideal yielding the empty intersection.
> The root $\zeta$ must be primitive, so $\zeta\ne1$; otherwise the two
> lines coincide and the factorisation is invalid in characteristic
> different from $3$. Such a root exists under the exercise's hypotheses.

## Negative candidate-check results {#br-bgk-2019-w22-solutions-negative}

Those candidate checks found no public solution page for Exercises 22.1,
22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10, 22.11,
22.12, 22.13, 22.14, 22.15, 22.16, 22.17, 22.18, or 22.20.
This statement records the candidate checks; it does not assert that
mathematical solutions do not exist.
