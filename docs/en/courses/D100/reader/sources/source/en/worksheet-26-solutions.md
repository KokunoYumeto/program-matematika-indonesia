---
title: "Public Solutions to Worksheet 26"
stable_id: br-ak-2012-w26-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributors: "Exercise 26.4: Bocardodarapti"
upstream_map: authority/wikiversity/unit-26/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: efa1d77d8b594a24078097f3595c0ae8078d9735dfe7d2b3abb05392d7340423
authority_manifest: authority/wikiversity/unit-26/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 981fa3c86534514215c722b6d4f6d711c040a7829465f20ae18940373f94763c
public_solution_count: 1
upstream_solution_revisions: "Exercise 26.4=1112503"
solution_xml_sha256: "04=d80e1ff03f562cdde8bfc9776ff56a7d1dfd364cf2c819d9d3187a5e91528ec0"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain their recorded CC BY-SA 2.0 Germany notice"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 1
correction_ids: "AGC-CORR-0102"
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 26 {#br-ak-2012-w26-solutions}

At the frozen revision boundary, the source provides a public solution only for Exercise 26.4. The frozen authority query reports the other ten candidate solution pages as absent. No additional solutions have been created for this edition.

<!-- upstream_solution: Kartesisches Blatt/Schnittmultiplizität im Nullpunkt/Mit jeder Geraden/Aufgabe/Lösung; pageid=21344; revid=1112503 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1112503 -->

## Solution to Exercise 26.4 {#br-ak-2012-w26-sol-04}

If a line does not pass through the origin, its intersection multiplicity with the folium at the origin is zero. Thus it suffices to consider lines through the origin. These can all be written as

$$
V(Y-aX),\qquad a\in K,
$$

or as the vertical line $V(X)$.

For $a=0$, that is, the line $V(Y)$, the quotient ring is

$$
\begin{aligned}
K[X,Y]_{(X,Y)}/(Y,X^3+Y^3-3XY)
&\cong K[X]_{(X)}/(X^3).
\end{aligned}
$$

This ring has dimension $3$ over $K$, so the intersection multiplicity is $3$. Since the equation of the folium is symmetric in $X$ and $Y$, the same result holds for the line $V(X)$.

Now take a line $V(Y-aX)$ with $a\ne0$. Then

$$
\begin{aligned}
K[X,Y]_{(X,Y)}/(Y-aX,X^3+Y^3-3XY)
&\cong K[X]_{(X)}/(X^3+a^3X^3-3aX^2)\\
&=K[X]_{(X)}/\left(X^2\bigl(-3a+(1+a^3)X\bigr)\right).
\end{aligned}
$$

Since $\operatorname{char}(K)\ne3$ and $a\ne0$, the factor

$$
-3a+(1+a^3)X
$$

is a unit in $K[X]_{(X)}$. Hence the quotient ring is isomorphic to

$$
K[X]_{(X)}/(X^2),
$$

which has dimension $2$. Thus the lines $V(X)$ and $V(Y)$ have intersection multiplicity $3$ at the origin, whereas every other line through the origin has intersection multiplicity $2$.

> **Editorial note - list of lines through the origin.** The source states that these lines have the form $V(Y-aX)$ or $V(Y)$, thereby listing $V(Y)$ twice and omitting the vertical line $V(X)$. The source's next step itself treats $V(X)$ by symmetry. This edition restores the intended list: $V(Y-aX)$ for $a\in K$, together with $V(X)$. The source also leaves the number after “$K$-dimension” blank in the $V(Y)$ case; the displayed quotient has basis $1,X,X^2$, so the dimension $3$ supplied here agrees with the source's stated multiplicity.

[Back to Exercise 26.4](#br-ak-2012-w26-ex-04)
