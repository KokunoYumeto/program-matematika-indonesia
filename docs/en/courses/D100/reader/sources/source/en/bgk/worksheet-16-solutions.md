---
title: "Public Solutions and Coverage of Worksheet 16"
stable_id: br-bgk-2019-w16-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-16/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: da420bada3728eb5f3fcf0a6c0ed7e75c1dd792b9ed99f1579a5acf7e7500526
candidate_evidence: authority/wikiversity-bgk/unit-16/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 022a9d9912991339073c1768b0ac14ff886b6bbb9c601778ce683a6d9f5a98a7
solution_ex12_xml: authority/wikiversity-bgk/unit-16/solution-ex12.xml
solution_ex12_xml_sha256: 5846949d3b2dfe2fded281049b697bf4ac487fda315cba1733bd6990d6116962
solution_ex12_html: authority/wikiversity-bgk/unit-16/solution-ex12.html
solution_ex12_html_sha256: 3fde47f35e393471a3562d81dea554f11a6310c9181f76a6b418bea0f59985a7
solution_ex12_upstream_pageid: 107941
solution_ex12_upstream_revid: 591672
solution_ex12_upstream_timestamp: "2019-06-20T16:42:13Z"
solution_ex12_mediawiki_sha1: 0da5c45323d18a3127fffa8cce7ce5730dc803b0
solution_ex12_frozen_revision_contributor: "Bocardodarapti"
solution_ex12_source_url: "https://de.wikiversity.org/w/index.php?oldid=591672"
course_authority_manifest: authority/wikiversity-bgk/course/COURSE_AUTHORITY_MANIFEST.json
course_authority_manifest_sha256: ea0bf346e261db8ed80b7565f7746e95c79e0c376d25d9fbce5d96879dff7dd8
exercise_count: 23
public_solution_count: 1
public_solution_numbers: "12"
negative_public_solution_count: 22
negative_solution_numbers: "1-11, 13-23"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
source_binding_status: "verified_solution_xml_html_and_candidate_topology_without_unit_manifest"
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 16 {#br-bgk-2019-w16-solutions}

At the frozen revision boundary, the source provides exactly one public solution among the 23 exercises: the solution to Exercise 16.12. The exercise map and candidate evidence record negative results for Exercises 16.1–16.11 and 16.13–16.23. Missing public solution pages are not replaced by invented solutions.

## Solution to Exercise 16.12 {#br-bgk-2019-w16-sol-ex12}

First suppose that $M$ is projective. Since $M$ has a generating system $v_i$, $i\in I$, there is a surjective $R$-module homomorphism

$$
\theta:R^{(I)}\longrightarrow M.
$$

Projectivity, applied to the identity

$$
\operatorname{Id}:M\longrightarrow M,
$$

shows that there is a module homomorphism

$$
\psi:M\longrightarrow R^{(I)}
$$

with

$$
\theta\circ\psi=\operatorname{Id}_M.
$$

This means that

$$
R^{(I)}=M\oplus\operatorname{kern}\theta.
$$

Conversely, suppose that

$$
M\oplus N=F
$$

is free. Given a surjective $R$-module homomorphism

$$
\theta:A\longrightarrow B
$$

and a module homomorphism

$$
\varphi:M\longrightarrow B,
$$

apply the result for free modules to

$$
\varphi\circ p_M:F\longrightarrow B.
$$

We obtain a homomorphism

$$
\rho:F\longrightarrow A
$$

with

$$
\varphi\circ p_M=\theta\circ\rho.
$$

The restriction of $\rho$ to $M$ has the required property, since

$$
\begin{aligned}
\theta\circ(\rho\circ i_M)
&=(\theta\circ\rho)\circ i_M\\
&=(\varphi\circ p_M)\circ i_M\\
&=\varphi\circ(p_M\circ i_M)\\
&=\varphi.
\end{aligned}
$$

## Frozen negative results {#br-bgk-2019-w16-solutions-negative}

There is no public solution page at the frozen revision for Exercises 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10, 16.11, 16.13, 16.14, 16.15, 16.16, 16.17, 16.18, 16.19, 16.20, 16.21, 16.22, or 16.23. This records the outcome of checking candidates; it does not claim that mathematical solutions do not exist.
