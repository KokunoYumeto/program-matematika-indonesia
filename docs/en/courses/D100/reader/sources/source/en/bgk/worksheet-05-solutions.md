---
title: "Public Solutions and Coverage for Worksheet 5"
stable_id: br-bgk-2019-w05-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-05/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: b6bf28ef883ac91c07d0c50526ff655b2bcf7fc1b0d45773f0543092d463cadf
authority_manifest: authority/wikiversity-bgk/unit-05/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 328774ffd66341ba8841b86935037a043067202dd10916d3e0be5082faeac35e
candidate_evidence: authority/wikiversity-bgk/unit-05/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 8b7b0d65fa6670632c96c8ab95b48b732576ebc3db80007ce281c78fb9875d51
solution_ex05_xml: authority/wikiversity-bgk/unit-05/solution-ex05.xml
solution_ex05_xml_sha256: 95fa2f0799fb9bfbfe0d9475a42c061ea805618e25e31560a6004da4672c5c86
solution_ex05_html: authority/wikiversity-bgk/unit-05/solution-ex05.html
solution_ex05_html_sha256: 04c72e340da0acd5220449d60b5bc1d18e30d2808f549600b5288910de26d406
solution_ex05_upstream_title: "Garbe/Untergarbe/Halmweise Zugehörigkeit/Aufgabe/Lösung"
solution_ex05_upstream_pageid: 116432
solution_ex05_upstream_revid: 1112696
solution_ex05_upstream_timestamp: "2026-08-21T16:35:52Z"
solution_ex05_mediawiki_sha1: 0d2b14ff95268801b6ec1fdea9771b8e505725c8
solution_ex05_source_url: "https://de.wikiversity.org/w/index.php?oldid=1112696"
solution_ex05_frozen_revision_contributor: "Arbota"
exercise_count: 11
public_solution_count: 1
public_solution_numbers: "5"
negative_public_solution_count: 10
negative_solution_numbers: "1-4, 6-11"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage for Worksheet 5 {#br-bgk-2019-w05-solutions}

At the frozen revision boundary, the source provides exactly one public solution among the eleven exercises on Worksheet 5, namely the solution to Exercise 5.5. The frozen exercise map and candidate evidence record negative results for Exercises 5.1-5.4 and 5.6-5.11. No new solutions have been created for this edition.

## Source solution to Exercise 5.5 {#br-bgk-2019-w05-ex05-solution}

Membership in the stalk,

$$
t_P\in\mathcal F_P
$$

means that there are an open neighbourhood

$$
P\in U_P
$$

and a section

$$
s_P\in\mathcal F(U_P)\subseteq\mathcal G(U_P)
$$

whose germ at $P$ is $t_P$. Thus there is a smaller open neighbourhood

$$
P\in V_P\subseteq U_P
$$

such that the restrictions of $t$ and $s_P$, regarded as sections of $\mathcal G$, agree on $V_P$.

Thus there is an open cover

$$
X=\bigcup_{i\in I}V_i
$$

such that

$$
t|_{V_i}\in\mathcal F(V_i)\subseteq\mathcal G(V_i).
$$

These sections are compatible both as sections of $\mathcal G$ and as sections of $\mathcal F$. Therefore there is a section

$$
s\in\mathcal F(X)
$$

whose restriction to each $V_i$ is $t|_{V_i}$. Since a compatible family in a sheaf has a unique global realisation, we have

$$
s=t
$$

in $\mathcal G(X)$. Hence

$$
t\in\mathcal F(X).
$$

> **Editorial note - sections and germs.** The source says that the local sections “restrict to” the germ $t_P$. More precisely, the germ at $P$ of the local section $s_P$ equals $t_P$; the translation uses this correctly typed relation without changing the argument.

[Return to Exercise 5.5](#br-bgk-2019-w05-ex05).
