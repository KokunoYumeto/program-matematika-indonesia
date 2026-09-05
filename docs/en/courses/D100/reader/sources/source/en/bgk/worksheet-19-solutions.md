---
title: "Public Solutions and Coverage of Worksheet 19"
stable_id: br-bgk-2019-w19-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-19/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 93905796d627d6ce9fe5926808e2589c25c4513ca38d14c9099ca91693805af6
authority_manifest: authority/wikiversity-bgk/unit-19/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ffd4e79d12cd6fd63836cb6d7fd17e5dc6481f3befaeb50efeb9a47c4cc70512
authority_manifest_status: "Complete terminal authority freeze; all 33 file records have been recomputed without mismatches."
candidate_evidence: authority/wikiversity-bgk/unit-19/worksheet-solution-candidates-api.json
candidate_evidence_sha256: d9b99cc424669d15e6f102d9686c35671bc38e41b29038df005917e521b03818
solution_ex10_xml: authority/wikiversity-bgk/unit-19/solution-ex10.xml
solution_ex10_xml_sha256: fe7f9ec06548c912ca89c776efd32da8e8b69dfe7c74dfebe09ea4f2d809c7c5
solution_ex10_html: authority/wikiversity-bgk/unit-19/solution-ex10.html
solution_ex10_html_sha256: b2719ae26824d23d3cedeadd2eaa364dd32f6e952d8cde8ee5a4db154e56ce7b
solution_ex10_upstream_pageid: 116008
solution_ex10_upstream_revid: 1094743
solution_ex10_mediawiki_sha1: e3b3f8d7c95285e6d294f385eda15f3a5d27ec6c
solution_ex10_frozen_revision_contributor: "Arbota"
exercise_count: 12
public_solution_count: 1
public_solution_numbers: "10"
negative_public_solution_count: 11
negative_solution_numbers: "1-9, 11-12"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 19 {#br-bgk-2019-w19-solutions}

At the frozen source boundary, there is exactly one public solution among the 12 exercises: the solution to Exercise 19.10. The exercise map and candidate evidence record negative results for Exercises 19.1–19.9, 19.11, and 19.12. Missing public solution pages are not replaced by invented solutions.

## Solution to Exercise 19.10 {#br-bgk-2019-w19-sol-ex10}

Using the curve equation and the relation

$$
X^2\,dX+Y^2\,dY+Z^2\,dZ=0,
$$

we obtain

$$
\begin{aligned}
\frac{X^2}{Y^2}\,d\!\left(\frac ZX\right)
&=\frac{X^2}{Y^2}\cdot\frac{X\,dZ-Z\,dX}{X^2}\\
&=\frac{X^3Z^2\,dZ-X^2Z^3\,dX}{X^2Y^2Z^2}\\
&=\frac{-X^3(X^2\,dX+Y^2\,dY)+X^2(X^3+Y^3)\,dX}
{X^2Y^2Z^2}\\
&=\frac{-X^3Y^2\,dY+X^2Y^3\,dX}{X^2Y^2Z^2}\\
&=\frac{Y^2}{Z^2}\cdot\frac{-X\,dY+Y\,dX}{Y^2}\\
&=\frac{Y^2}{Z^2}\,d\!\left(\frac XY\right).
\end{aligned}
$$

By symmetry, the remaining equalities hold as well.

> **Editorial note — the source-solution boundary.** The frozen public solution proves that the local forms agree, but it contains no separate argument that the resulting global form is nonzero, although Exercise 19.10 also asks for nontriviality. That missing step is disclosed here; no continuation is invented.

## Frozen negative results {#br-bgk-2019-w19-solutions-negative}

There is no public solution page at the frozen source boundary for Exercises 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9, 19.11, or 19.12. This records the outcome of checking candidates; it does not claim that mathematical solutions do not exist.
