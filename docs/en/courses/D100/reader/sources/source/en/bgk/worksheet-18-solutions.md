---
title: "Public Solutions and Coverage of Worksheet 18"
stable_id: br-bgk-2019-w18-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-18/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 2d687492b05ef02025dd2d7e53e3bf76c8034f69e26047f9ba72d9d1a1a5f79f
authority_manifest: authority/wikiversity-bgk/unit-18/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f0014846fe068d3b1bfd4488c1db66fdd6039fa2d70ff7b8a213875a56d39495
authority_manifest_status: "Complete terminal authority freeze; all 41 file records have been recomputed without mismatches."
candidate_evidence: authority/wikiversity-bgk/unit-18/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 7ada688c356cb81d39b079f6d1c324f8078a6abcf747dd6006f3849a0114f986
solution_ex06_xml: authority/wikiversity-bgk/unit-18/solution-ex06.xml
solution_ex06_xml_sha256: 854ea0b9b4936ca92d8b0eda85416d8b75d4c6c3c6c8f81098e925edc5f8c66a
solution_ex06_html: authority/wikiversity-bgk/unit-18/solution-ex06.html
solution_ex06_html_sha256: deb091d9a73a5e5e4ec860262563c71286c9537b71486c89eaba86d2f65b0c14
solution_ex06_upstream_pageid: 97286
solution_ex06_upstream_revid: 1089197
solution_ex06_mediawiki_sha1: e287c8fd850dd6f8436e3ccccd55f44c99caaba2
solution_ex06_frozen_revision_contributor: "Arbota"
solution_ex17_xml: authority/wikiversity-bgk/unit-18/solution-ex17.xml
solution_ex17_xml_sha256: ff0bfe9a0c8ffb9f30894a9be0760df33861eaf36d522385ada16b7867d68259
solution_ex17_html: authority/wikiversity-bgk/unit-18/solution-ex17.html
solution_ex17_html_sha256: a44a7cafa8023bd19ed317ca61634ad46713e7c02a3097d1db48ceddaf80118b
solution_ex17_upstream_pageid: 168357
solution_ex17_upstream_revid: 1067492
solution_ex17_mediawiki_sha1: 5783f50ea07e67c0fa1410c823567a1b94587578
solution_ex17_frozen_revision_contributor: "Bocardodarapti"
solution_ex18_xml: authority/wikiversity-bgk/unit-18/solution-ex18.xml
solution_ex18_xml_sha256: 6fb30ca7ec5528d807df353c606eaf5dbc4b1ef8c7b77850800b7e4a2885a682
solution_ex18_html: authority/wikiversity-bgk/unit-18/solution-ex18.html
solution_ex18_html_sha256: 12d35213e0c5902ef8f1c2f460bd7ea00a9e292e4ff4c9ba4d2834d74d413683
solution_ex18_upstream_pageid: 107075
solution_ex18_upstream_revid: 1095075
solution_ex18_mediawiki_sha1: 39e0ceb2a0858e08b48a34a486c37de4a1745783
solution_ex18_frozen_revision_contributor: "Arbota"
exercise_count: 25
public_solution_count: 3
public_solution_numbers: "6, 17, 18"
negative_public_solution_count: 22
negative_solution_numbers: "1-5, 7-16, 19-25"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 18 {#br-bgk-2019-w18-solutions}

At the frozen revision boundary, the source provides exactly three public solutions among the 25 exercises: the solutions to Exercises 18.6, 18.17, and 18.18. The exercise map and candidate evidence record negative results for Exercises 18.1–18.5, 18.7–18.16, and 18.19–18.25. Missing public solution pages are not replaced by invented solutions.

## Solution to Exercise 18.6 {#br-bgk-2019-w18-sol-ex06}

We have

$$
\begin{aligned}
[\delta,\mu_g](x)
&=(\delta\circ\mu_g-\mu_g\circ\delta)(x)\\
&=\delta(gx)-g\delta(x)\\
&=g\delta(x)+x\delta(g)-g\delta(x)\\
&=x\delta(g).
\end{aligned}
$$

Thus $[\delta,\mu_g]$ is multiplication by $\delta(g)$.

## Solution to Exercise 18.17 {#br-bgk-2019-w18-sol-ex17}

The monoid ring $R[M]$ has $R$-basis

$$
T^m,\qquad m\in M.
$$

The tensor product of free modules has as a basis all tensor products of elements of the two bases. Thus

$$
T^{(m,n)},\qquad(m,n)\in M\times N,
$$

is a basis of $R[M\times N]$, while

$$
T^m\otimes T^n,\qquad m\in M,\ n\in N,
$$

is a basis of $R[M]\otimes R[N]$. Hence the assignment on bases

$$
T^{(m,n)}\longleftrightarrow T^m\otimes T^n
$$

directly gives an $R$-module isomorphism. Under this assignment,

$$
T^{(0,0)}=1
$$

corresponds to

$$
T^0\otimes T^0=1\otimes1=1.
$$

Moreover,

$$
T^{(m_1,n_1)}\cdot T^{(m_2,n_2)}
=T^{(m_1+m_2,n_1+n_2)}
$$

corresponds to the element

$$
\begin{aligned}
T^{m_1}\otimes T^{n_1}\cdot T^{m_2}\otimes T^{n_2}
&=(T^{m_1}\cdot T^{m_2})\otimes(T^{n_1}\cdot T^{n_2})\\
&=T^{m_1+m_2}\otimes T^{n_1+n_2}.
\end{aligned}
$$

Thus the assignment also respects multiplication and is an $R$-algebra isomorphism.

## Solution to Exercise 18.18 {#br-bgk-2019-w18-sol-ex18}

For $a\in A$ and $s\in S$, we have

$$
\begin{aligned}
0=da
&=d\left(\frac as\cdot s\right)\\
&=\frac as\,ds+s\,d\left(\frac as\right)\\
&=s\,d\left(\frac as\right).
\end{aligned}
$$

Since $s$ is a unit in $A_S$, it follows that

$$
d\left(\frac as\right)=0.
$$

## Frozen negative results {#br-bgk-2019-w18-solutions-negative}

There is no public solution page at the frozen revision for Exercises 18.1, 18.2, 18.3, 18.4, 18.5, 18.7, 18.8, 18.9, 18.10, 18.11, 18.12, 18.13, 18.14, 18.15, 18.16, 18.19, 18.20, 18.21, 18.22, 18.23, 18.24, or 18.25. This records the outcome of checking candidates; it does not claim that mathematical solutions do not exist.

