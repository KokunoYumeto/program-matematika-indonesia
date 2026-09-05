---
title: "Public solutions and coverage of Worksheet 28"
stable_id: br-bgk-2019-w28-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
worksheet_upstream_title: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)/Arbeitsblatt 28"
worksheet_upstream_pageid: 110237
worksheet_upstream_revid: 793599
worksheet_upstream_parentid: 619250
worksheet_upstream_timestamp: "2022-08-25T06:21:18Z"
worksheet_upstream_mediawiki_sha1: ea85b787c20468bfd111f5afe6022adb84c3e3d7
worksheet_export_sha1_base36: re7oxf3napk67u971f3615hmym46jfb
worksheet_frozen_revision_contributor: "Arbota"
worksheet_frozen_revision_contributor_id: 36910
worksheet_url: "https://de.wikiversity.org/wiki/Kurs:B%C3%BCndel,_Garben_und_Kohomologie_(Osnabr%C3%BCck_2019-2020)/Arbeitsblatt_28"
worksheet_revision_url: "https://de.wikiversity.org/w/index.php?oldid=793599"
upstream_map: authority/wikiversity-bgk/unit-28/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 00380c3c1746989c8e7e12a8058732b96cd631c88a22750de4b174a5c884755e
authority_manifest: authority/wikiversity-bgk/unit-28/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 1ab20936afe74fcfdde3318452f2211f2458911ff0a77c554fba894de49f4b9f
candidate_evidence: authority/wikiversity-bgk/unit-28/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 807394ba76bba601f12d945c2cfbc3bc6579d4db2d2be826e071fa3158765166
selection_rule: "For each official exercise-page title, the literal candidate '<exercise>/Lösung' is checked directly; the absence of a visible worksheet link is not used as negative evidence."
solution_ex06_upstream_title: "Ebene/Drei Vektoren/Transformierbar/Aufgabe/Lösung"
solution_ex06_url: "https://de.wikiversity.org/wiki/Ebene/Drei_Vektoren/Transformierbar/Aufgabe/L%C3%B6sung"
solution_ex06_revision_url: "https://de.wikiversity.org/w/index.php?title=Ebene/Drei_Vektoren/Transformierbar/Aufgabe/L%C3%B6sung&oldid=1096087"
solution_ex06_upstream_pageid: 97324
solution_ex06_upstream_revid: 1096087
solution_ex06_mediawiki_sha1: d6a97c258f8c8bb412ae9882f3cadb995feace03
solution_ex06_frozen_revision_contributor: "Arbota"
solution_ex06_revision_timestamp: "2026-06-15T07:54:14Z"
solution_ex06_revision_timestamp_display: "09:54, 15 June 2026"
solution_ex06_xml: authority/wikiversity-bgk/unit-28/solution-ex06.xml
solution_ex06_xml_sha256: e06231e25c906968a28314cea9fbb24a305ffa1bd539fa43b5bd99dfe5f936bb
solution_ex06_html: authority/wikiversity-bgk/unit-28/solution-ex06.html
solution_ex06_html_sha256: a98d8bd5d73123530002aac1f0846e96435293214c215afbd686d62344fac3d7
exercise_count: 14
candidate_page_count: 14
existing_candidate_count: 1
missing_candidate_count: 13
public_solution_count: 1
public_solution_numbers: "6"
negative_public_solution_count: 13
negative_solution_numbers: "1-5, 7-14"
license: "The frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public solutions and coverage of Worksheet 28 {#br-bgk-2019-w28-solutions}

For each of the 14 official exercise-page titles, the literal candidate page `<exercise>/Lösung` was checked directly. This check found exactly one public solution page, namely the solution to Exercise 28.6. The other thirteen candidates led to the official page-creation view stating that the page did not yet exist. The absence of a visible link on the worksheet page was not used as negative evidence.

## Solution to Exercise 28.6 {#br-bgk-2019-w28-sol-ex06}

Since $v_1,v_2$ and $w_1,w_2$ are bases, the theorem on specifying a linear map on a basis gives a bijective linear map

$$
\psi:V\longrightarrow V
$$

with

$$
\psi(v_1)=w_1
\qquad\text{and}\qquad
\psi(v_2)=w_2.
$$

Under $\psi$, the assumptions of pairwise linear independence remain valid.

Replacing the first family by its image under $\psi$ and renaming the common basis, we therefore only need to consider two families of vectors of the form $v_1,v_2,y$ and $v_1,v_2,z$. Let

$$
y=av_1+bv_2
$$

and

$$
z=cv_1+dv_2.
$$

Here

$$
a,b,c,d\ne 0,
$$

since otherwise $y$, respectively $z$, would be linearly dependent with one of the $v_i$. We now consider the linear map $\phi$ given by

$$
v_1\longmapsto \frac ca v_1
\qquad\text{and}\qquad
v_2\longmapsto \frac db v_2.
$$

Then

$$
\begin{aligned}
\phi(y)
&=\phi(av_1+bv_2)\\
&=a\phi(v_1)+b\phi(v_2)\\
&=a\frac ca v_1+b\frac db v_2\\
&=cv_1+dv_2\\
&=z.
\end{aligned}
$$

Thus $\phi$ satisfies the required condition in the reduced situation, and $\phi\circ\psi$ satisfies it for the original two families.

> **Edition note (source).** The source solution introduces a map $\psi$ but writes its two basis values with the symbol $\phi$, and it does not name the final composition. The notation and the composition have been made explicit above. The source also writes $cv_1+bv_2=z$ in the last line, although it previously specified $z=cv_1+dv_2$; the second coefficient has therefore been corrected to $d$.

## Negative results established by direct candidate checks {#br-bgk-2019-w28-solutions-negative}

The literal candidate pages `<exercise>/Lösung` do not exist at the checked boundary for Exercises 28.1, 28.2, 28.3, 28.4, 28.5, 28.7, 28.8, 28.9, 28.10, 28.11, 28.12, 28.13, and 28.14. Each candidate URL led to the official page-creation view stating “Diese Seite existiert noch nicht” (“This page does not yet exist”). This statement records source-page coverage, not a claim that mathematical solutions do not exist.
