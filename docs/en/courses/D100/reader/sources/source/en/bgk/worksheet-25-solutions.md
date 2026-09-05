---
title: "Public Solutions and Coverage of Worksheet 25"
stable_id: br-bgk-2019-w25-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
frozen_revision_contributor: "Arbota"
upstream_title: "Intervall/Intervallüberdeckung/2/Stetige Funktion/Differenz/Aufgabe/Lösung"
upstream_pageid: 125477
upstream_revid: 1096264
upstream_timestamp: "2026-06-15T08:23:34Z"
upstream_mediawiki_sha1: 4873a553ced30228b6d6eb2e1f1b247f181f488b
source_url: "https://de.wikiversity.org/w/index.php?oldid=1096264"
source_attribution: "im Wesentlichen Tarek Emmrich"
authority_manifest: authority/wikiversity-bgk/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f454cb2f8ada795015dcf78d4ad56a54107d9773705b7113a1ef1600b341e26d
authority_manifest_status: "Terminal authority freeze complete; all 33 file records have been recomputed without discrepancies."
solution_ex01_xml: authority/wikiversity-bgk/unit-25/solution-ex01.xml
solution_ex01_xml_sha256: ee5a739c70fdff70b2d4c037972c6091a92a0436a3c97a3a0deb93ae3ebf6b34
solution_ex01_html: authority/wikiversity-bgk/unit-25/solution-ex01.html
solution_ex01_html_sha256: 3cfb91666b17069c63a9256c5f0e27411cc802ff6419763f6922238cf43b6fc5
upstream_map: authority/wikiversity-bgk/unit-25/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 03b696f0c666352947f89c01a2c1ca0c1c5fb38bae0af77693cf21021b6b381b
candidate_evidence: authority/wikiversity-bgk/unit-25/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 37ce99c2c415ef9bc13592e6e9d0537322c4fcf0b83b3112f8b6d1796828c939
exercise_count: 13
public_solution_count: 1
public_solution_numbers: "1"
negative_public_solution_count: 12
negative_solution_numbers: "2-13"
media_credits: source/id-ID/media-credits-bgk-unit-25.md
media_credits_sha256: c0367344876a648ab7141eb306e6a9a02f14c47b3b57a03012073940f4297037
rights_ledger: authority/RIGHTS-bgk-unit-25.csv
rights_ledger_sha256: 87f9d56b1300a56ca68e4aa8f50e3d50ab622d7a4d05221089d49e1dba35981d
asset_closure: authority/ASSET_CLOSURE-bgk-unit-25.json
asset_closure_sha256: b897e839fc6999e5c149e1bf065a634b96246b563860d46f0a16ddb82ae1c9d5
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage of Worksheet 25 {#br-bgk-2019-w25-solutions}

At the frozen revision boundary, the source provides exactly one public
solution among the 13 exercises: the solution to Exercise 25.1.
The exercise map and candidate evidence record negative results for
Exercises 25.2--25.13. The absence of public solution pages is not
replaced by invented solutions.

<!-- upstream_entity: Intervall/Intervallüberdeckung/2/Stetige Funktion/Differenz/Aufgabe/Lösung -->

## Solution to Exercise 25.1 {#br-bgk-2019-w25-sol-ex01}

Let

$$
U=]a,b[
$$

and

$$
V=]c,d[
$$

with

$$
a<c<b<d.
$$

If the intersection is empty, the statement is trivial.
The outer endpoints may also belong to the intervals.

> **Edition note — scope of the published solution.** The source explicitly
> treats the nonempty, finite, strictly interlacing endpoint configuration
> displayed above. It does not spell out the nested, coincident-endpoint, or
> unbounded configurations allowed by the exercise; those cases require
> their own elementary reductions or cutoff choices.

Choose $\epsilon>0$ such that

$$
2\epsilon<b-c.
$$

Define

$$
g(x):=
\begin{cases}
f(x),&x\geq b-\epsilon,\\[2pt]
f(x)\dfrac{x-c-\epsilon}{b-c-2\epsilon},
&x\in]c+\epsilon,b-\epsilon[,\\[8pt]
0,&x\leq c+\epsilon,
\end{cases}
$$

and

$$
-h(x):=
\begin{cases}
0,&x\geq b-\epsilon,\\[2pt]
f(x)\dfrac{-x+b-\epsilon}{b-c-2\epsilon},
&x\in]c+\epsilon,b-\epsilon[,\\[8pt]
f(x),&x\leq c+\epsilon.
\end{cases}
$$

These functions are continuous because their values agree at the
transition points. For

$$
x\in]c+\epsilon,b-\epsilon[
$$

we have

$$
\begin{aligned}
g(x)-h(x)
&=f(x)\frac{x-c-\epsilon}{b-c-2\epsilon}
 +f(x)\frac{-x+b-\epsilon}{b-c-2\epsilon}\\
&=f(x)\frac{x-c-\epsilon-x+b-\epsilon}
{b-c-2\epsilon}\\
&=f(x).
\end{aligned}
$$

The same equation holds outside this interval.

The source solution credits “substantially Tarek Emmrich”.

## Frozen negative results {#br-bgk-2019-w25-solutions-negative}

There is no public solution page at the frozen revision for Exercises
25.2, 25.3, 25.4, 25.5, 25.6, 25.7, 25.8, 25.9, 25.10, 25.11, 25.12,
or 25.13. This statement records the candidate checks; it does not
assert that mathematical solutions do not exist.
