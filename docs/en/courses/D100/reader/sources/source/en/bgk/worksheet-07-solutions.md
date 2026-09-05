---
title: "Public-Solution Coverage for Worksheet 7"
stable_id: br-bgk-2019-w07-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-07/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 309a1478ffcc6b7fdd02ddb72f29dca37d9d9ca8756737e7723d9bae148365c0
authority_manifest: authority/wikiversity-bgk/unit-07/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 001074c62cedb1efc988d3214416d2d86a02976d5b22dc272f4fe064e72dfc95
candidate_evidence: authority/wikiversity-bgk/unit-07/worksheet-solution-candidates-api.json
candidate_evidence_sha256: c4c95e9dc35a731c42e5f2fd007fcd6d84c22c8836c6c179bbb257c7698a0ad4
exercise_count: 21
public_solution_count: 1
negative_public_solution_count: 20
negative_solution_numbers: "1-13,15-21"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: source_scope_complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Public-Solution Coverage for Worksheet 7 {#br-bgk-2019-w07-solutions}

At the frozen revision boundary, the source provides exactly one public
solution, for Exercise 7.14. The other twenty solution candidates
(Exercises 7.1–7.13 and 7.15–7.21) have status *missing* in the query
evidence; no new solutions have been created for this edition.

<!-- upstream_entity: Lokaler Ring/Restklassenring/Einheiten surjektiv/Aufgabe/Lösung -->

## Solution to Exercise 7.14 {#br-bgk-2019-w07-sol-ex14}

If $\mathfrak a=R$, the quotient ring is the zero ring and the assertion
is clear. Thus assume $\mathfrak a\subseteq\mathfrak m$, where
$\mathfrak m$ is the unique maximal ideal of the local ring $R$.

Take $r\in R$ representing a unit in $(R/\mathfrak a)^\times$, and take
$s\in R$ such that

$$
rs=1\quad\text{in }R/\mathfrak a.
$$

This means

$$
rs-1\in\mathfrak a\subseteq\mathfrak m
$$

in $R$. If $r$ were not a unit, then $rs\in\mathfrak m$, and hence

$$
1=(1-rs)+rs\in\mathfrak m,
$$

a contradiction. Thus $r$ itself is a unit in $R$, and every unit in
$R/\mathfrak a$ has a preimage that is a unit. Consequently,

$$
R^\times\longrightarrow(R/\mathfrak a)^\times
$$

is surjective.

No public solutions for the other twenty exercises may be supplied or
treated as implicit; the exercise map and candidate evidence remain the
record of source coverage.

