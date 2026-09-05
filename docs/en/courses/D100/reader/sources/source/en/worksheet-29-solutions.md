---
title: "Public Solutions to Worksheet 29"
stable_id: br-ak-2012-w29-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributors: "Exercise 29.2: Arbota; Exercise 29.3: Arbota"
upstream_map: authority/wikiversity/unit-29/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 75b07cabcb83cc12a6fd1259017f7e169c0ded461e7b7c94e65f033b71d12bc9
authority_manifest: authority/wikiversity/unit-29/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: ec3b34ad387ae827ecaa365c4def3b0550f74b629d0db3873a7cc28dc0831bc5
candidate_evidence: authority/wikiversity/unit-29/worksheet-solution-candidates-api.json
public_solution_count: 2
negative_public_solution_count: 8
negative_solution_numbers: "1, 4-10"
upstream_solution_revisions: "Exercise 29.2=1094621; Exercise 29.3=1090273"
solution_xml_sha256: "2=2b468a1f7d9bebff884c001c3a475a212601b022896953c97e6a55026cf38f66; 3=50771bcf86505ee8429426f3488ef46af450a258629d4403a2bc16aa74abcaff"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain their component notices recorded in the Unit 29 rights ledger"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
correction_ids: "REVIEW-AK-26-30-C16; REVIEW-AK-26-30-C17"
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 29 {#br-ak-2012-w29-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 29.2 and 29.3. The frozen authority query reports the other eight candidate solution pages as absent. No additional solutions have been created for this edition.

<!-- upstream_solution: Ebene algebraische Kurven/Z mod 5/Einheitskreis und x^3-2y^2+3/Durchschnitt und unendlich ferne Punkte/Aufgabe/Lösung; pageid=21303; revid=1094621 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1094621 -->

## Solution to Exercise 29.2 {#br-ak-2012-w29-sol-02}

a. We add the two equations

$$
2X^2+2Y^2-2=0
\qquad\text{and}\qquad
X^3-2Y^2+3=0
$$

and obtain the condition

$$
X^3+2X^2+1=0.
$$

For the possible values $x=0,1,2,3,4$, substitution gives $1,4,2,1,2$, respectively. Thus this condition cannot be satisfied, so the intersection of the two curves in $\mathbb A_K^2$ is empty.

b. We seek the points in $\mathbb P_K^2$ satisfying simultaneously

$$
X^2+Y^2-Z^2=0
\qquad\text{and}\qquad
Z=0.
$$

This gives the condition

$$
X^2+Y^2=0.
$$

The squares in $\mathbb Z/(5)$ are $0,1,4$. The solution $(0,0,0)$ is not allowed, since it does not represent a projective point, and we obtain the solutions $(\pm1,\pm2)$ and $(\pm2,\pm1)$. Since we seek projective points, the first coordinate can be normalised to $1$, and the second must then be $2$ or $-2=3$. Hence there are two points at infinity,

$$
(1,2,0)
\qquad\text{and}\qquad
(1,3,0).
$$

c. The two equations

$$
X^3-2Y^2Z+3Z^3=0
\qquad\text{and}\qquad
Z=0
$$

immediately give $X^3=0$, and hence $X=0$. Thus the unique point at infinity is $(0,1,0)$.

d. Here, as throughout this exercise, $V$ and $V_+$ denote sets of $K$-rational zeros with their point-set Zariski topology. By definition, the projective closure is the Zariski closure. Since $V(X^2+Y^2-1)$ is a finite set of $K$-rational points, it is already closed and equals its closure. However, by part b, $V_+(X^2+Y^2-Z^2)$ contains additional points. The latter set is therefore not its projective closure.

> **Source-convention note REVIEW-AK-26-30-C16 - finite-field point sets.** The source's conclusion uses its classical $K$-point convention. It is not a claim that the scheme-theoretic projective closure of the affine conic is merely the finite set of its $K$-rational points.

<!-- upstream_solution: Projektive Gerade/K-Punkte/Lokale Ringe isomorph/Aufgabe/Lösung; pageid=21573; revid=1090273 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1090273 -->

## Solution to Exercise 29.3 {#br-ak-2012-w29-sol-03}

Every $K$-rational point $P\in\mathbb P_K^1$ lies on an affine line

$$
P\in\mathbb A_K^1=D_+(L)\subset\mathbb P_K^1,
$$

where $L$ is a homogeneous linear form. By translating on this affine line, we may further assume that the point in question is the origin. This can be done for every $K$-rational point and does not change its local ring. Therefore all these local rings are isomorphic to one another. The local ring at the origin of the affine line is the localisation

$$
K[X]_{(X)}.
$$
