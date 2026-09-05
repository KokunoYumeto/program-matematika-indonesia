---
title: "Public Solutions to Worksheet 24"
stable_id: br-ak-2012-w24-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
upstream_map: authority/wikiversity/unit-24/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 250744d177bc2d5cf2a1cc506a99e05f1250c771de88b214a0e8d5cabfe7b9b8
authority_manifest: authority/wikiversity/unit-24/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 3731896a5980c565d9d69a2e01eee497f13b6f449f2f9c701fce726271c026a5
public_solution_count: 1
upstream_solution_revisions: "Exercise 24.4=1068135"
solution_xml_sha256: "04=7904b98444817d81659d24fafd37e9009c39547c891bce705b0ae4b37f0ec527"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain their recorded CC BY-SA 2.0 Germany notice"
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 1
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 24 {#br-ak-2012-w24-solutions}

At the frozen revision boundary, the source provides a public solution only
to Exercise 24.4. No additional solutions have been created for this edition.

<!-- upstream_solution: Potenzreihenring eine Variable/Abbildung der Lokalisierung an maximalen Ideal/Aufgabe/Lösung; pageid=168447; revid=1068135 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1068135 -->

## Solution to Exercise 24.4 {#br-ak-2012-w24-sol-04}

We start with the $K$-algebra homomorphism

$$
\begin{aligned}
K[T]&\longrightarrow K[[T]],\\
T&\longmapsto T.
\end{aligned}
$$

Every polynomial $P\in K[T]\setminus (T)$ has constant term

$$
P(0)\ne 0.
$$

By the unit criterion for the formal power series ring, $P$ is a unit in
$K[[T]]$. Since every element of the denominator set $K[T]\setminus (T)$
maps to a unit, the universal property of localisation gives a unique
$K$-algebra homomorphism

$$
K[T]_{(T)}\longrightarrow K[[T]].
$$

Explicitly, it is given by

$$
\frac{f}{P}\longmapsto fP^{-1}.
$$

*Edition note -- correction to the source solution:* After stating
$P\notin (T)$, the source displays only the symbol $\ne 0$ without a
left-hand side. The edition restores the required statement $P(0)\ne0$;
German spelling errors with no mathematical effect are also naturally
corrected in translation.

[Back to Exercise 24.4](#br-ak-2012-w24-ex-04)
