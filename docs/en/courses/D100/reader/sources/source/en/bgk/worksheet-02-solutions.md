---
title: "Public Solutions for Worksheet 2"
stable_id: br-bgk-2019-w02-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-02/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 4e0633e8c35ea5a2fddd0b63a0bb67fdd6af93f11a55f3a2eae10eae0d25a10a
authority_manifest: authority/wikiversity-bgk/unit-02/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: a348b56811fe98266feff9108a21a436a9b8f07a343321feab7d9fbb3b75e64d
candidate_evidence: authority/wikiversity-bgk/unit-02/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 5051d800bed72fe432757012033319ca30c14503254f16d0d385f9a0a3c82ad2
solution_ex04_xml: authority/wikiversity-bgk/unit-02/solution-ex04.xml
solution_ex04_xml_sha256: 6f326a59a4289d17ac6aee485706faa81d641d994ddda72bd463053eec4b71b1
solution_ex04_html: authority/wikiversity-bgk/unit-02/solution-ex04.html
solution_ex04_html_sha256: 8cf7b19c9693b1817e5699b32703545716fb35dfa713b9f6129758dbe0bf0e7f
solution_ex04_upstream_title: "Stetiges Vektorfeld/S^2/Nur eine Nullstelle/Aufgabe/Lösung"
solution_ex04_upstream_pageid: 77727
solution_ex04_upstream_revid: 1096699
solution_ex04_upstream_timestamp: "2026-06-15T09:32:35Z"
solution_ex04_upstream_mediawiki_sha1: 64a726dc965e322b03e5eb0797f109cb45ab5125
solution_ex04_source_url: "https://de.wikiversity.org/w/index.php?oldid=1096699"
solution_ex04_frozen_revision_contributor: "Arbota"
exercise_count: 27
public_solution_count: 1
public_solution_numbers: "4"
negative_public_solution_count: 26
negative_solution_numbers: "1-3, 5-27"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: source_scope_complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions for Worksheet 2 {#br-bgk-2019-w02-solutions}

At the frozen authority boundary, the source provides exactly one public solution among the 27 exercises on Worksheet 2, namely the solution to Exercise 2.4. The frozen exercise map records negative results for Exercises 2.1-2.3 and 2.5-2.27. No new solutions have been created for this edition.

## Source solution to Exercise 2.4 {#br-bgk-2019-w02-ex04-solution}

On $\mathbb R^2$, consider the continuous vector field $F$ given by

$$
F(x,y)=\frac{1}{1+x^2+y^2}e_1.
$$

This field is nowhere zero and continuous. We transport it by stereographic projection to

$$
\mathbb R^2\cong S^2\setminus\{N\}
$$

and extend it at the north pole by the value

$$
0\in T_NS^2.
$$

We claim that this vector field is continuous. Let $(P_n)$ be a sequence on $S^2$ converging to $N$. We may immediately assume that $P_n\ne N$ for all $n$. The image of this sequence in the chart is

$$
P_n'=(x_n,y_n).
$$

Since $P_n$ converges to the north pole, $\lVert P_n'\rVert$ diverges to $\infty$. Hence the sequence

$$
F(P_n')=F(x_n,y_n)
=\frac{1}{1+x_n^2+y_n^2}e_1
$$

converges to $0$.

> **Editorial note - the source formula is undefined at the origin.** The source defines $F$ on all of $\mathbb R^2$ by $F(x,y)=(x^2+y^2)^{-1}e_1$, but this expression is undefined at $(0,0)$. Thus the assertion that $F$ is continuous and nowhere zero on the entire plane is false as printed. This edition displays the minimal correction $F(x,y)=(1+x^2+y^2)^{-1}e_1$: this function is continuous and nowhere zero on all of $\mathbb R^2$, tends to $0$ as $\lVert(x,y)\rVert\to\infty$, and, after being pushed forward by inverse stereographic projection, also tends to the zero vector at the north pole (the differential of that inverse projection remains bounded and even decays at infinity). The change therefore repairs the local defect without altering the structure of the source argument; the source form is preserved in this note. In the limiting expression, the source also prints $x,y$ without subscripts; this edition displays $x_n,y_n$ to match the sequence just defined. The source also duplicates the verb *sei* in the sentence introducing $(P_n)$; that typographical repetition is omitted in the translation and recorded here.

