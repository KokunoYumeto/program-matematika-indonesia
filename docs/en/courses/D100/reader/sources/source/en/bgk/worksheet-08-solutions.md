---
title: "Public Solutions and Coverage for Worksheet 8"
stable_id: br-bgk-2019-w08-solutions
language: en
source_course: "Kurs:Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
upstream_map: authority/wikiversity-bgk/unit-08/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 97c9bf59cae3e34263681875e74c4ad2f0626b87f19a6e0490d127ac4c921f1a
authority_manifest: authority/wikiversity-bgk/unit-08/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: cadebf48e67a54a238f4b22e0abf806fbf1f81821b6d012993739ecf50dd8d32
candidate_evidence: authority/wikiversity-bgk/unit-08/worksheet-solution-candidates-api.json
candidate_evidence_sha256: 7e83e1e34c1ff1ee8c6d30dbc90b984c5cbf5e410ecccb26aad6c9825c9143bf
solution_ex03_xml: authority/wikiversity-bgk/unit-08/solution-ex03.xml
solution_ex03_xml_sha256: 95631c033a53318f85076d46db80ee24662cf91b4caa50593862ffabb284c65a
solution_ex03_html: authority/wikiversity-bgk/unit-08/solution-ex03.html
solution_ex03_html_sha256: c9b41307429cea7a1e840940572f168e2f6a17cfb729aa12c01e29aabc4cac48
solution_ex03_upstream_title: "Kommutative Ringtheorie/Primideal/Charakterisierung mit Restklassenring/Fakt/Beweis/Aufgabe/Lösung"
solution_ex03_upstream_pageid: 86076
solution_ex03_upstream_revid: 485196
solution_ex03_upstream_timestamp: "2017-01-22T18:50:39Z"
solution_ex03_mediawiki_sha1: ea019f083d8af1fe044923f7dd6f86f675ee9624
solution_ex03_source_url: "https://de.wikiversity.org/w/index.php?oldid=485196"
solution_ex03_frozen_revision_contributor: "Bocardodarapti"
solution_ex04_xml: authority/wikiversity-bgk/unit-08/solution-ex04.xml
solution_ex04_xml_sha256: a5fbd50569e2cef3662039eb4bfd79cb96995eafb529543d67e7722d564cb9da
solution_ex04_html: authority/wikiversity-bgk/unit-08/solution-ex04.html
solution_ex04_html_sha256: ff35251b5ea2b7aaacdb81681a277e956eae5e4309873ae737d9266679e1c39c
solution_ex04_upstream_title: "Primideal/Charakterisierung als Kern nach Körper/Aufgabe/Lösung"
solution_ex04_upstream_pageid: 169650
solution_ex04_upstream_revid: 1112909
solution_ex04_upstream_timestamp: "2026-08-22T08:09:40Z"
solution_ex04_mediawiki_sha1: c7ed44201f6b8d4051a567567c5a54b411976815
solution_ex04_source_url: "https://de.wikiversity.org/w/index.php?oldid=1112909"
solution_ex04_frozen_revision_contributor: "Bocardodarapti"
solution_ex11_xml: authority/wikiversity-bgk/unit-08/solution-ex11.xml
solution_ex11_xml_sha256: 4522b73edc7e16b6abd0b81f3486eb10d3ef7f9a04e57142f9ef708691600e36
solution_ex11_html: authority/wikiversity-bgk/unit-08/solution-ex11.html
solution_ex11_html_sha256: 05ab4922040e2ada71b8cc1ac54a376bbdc5419f12a5523cdbae322f46d01a85
solution_ex11_upstream_title: "Integre endlich erzeugte Algebren/Lokaler Isomorphismus/In Umgebung/Aufgabe/Lösung"
solution_ex11_upstream_pageid: 21576
solution_ex11_upstream_revid: 1112864
solution_ex11_upstream_timestamp: "2026-08-21T18:05:32Z"
solution_ex11_mediawiki_sha1: 45f4d65002a1d754f687c2e62392bb1d3c90c456
solution_ex11_source_url: "https://de.wikiversity.org/w/index.php?oldid=1112864"
solution_ex11_frozen_revision_contributor: "Bocardodarapti"
exercise_count: 22
public_solution_count: 3
public_solution_numbers: "3, 4, 11"
negative_public_solution_count: 19
negative_solution_numbers: "1-2, 5-10, 12-22"
license: "Frozen semantic course text and this translation: CC BY-SA 4.0."
non_endorsement: "This independent English edition does not imply endorsement by the author, Wikiversity, the Wikimedia Foundation, or any source institution."
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
---

```{=latex}
\clearpage
```

# Public Solutions and Coverage for Worksheet 8 {#br-bgk-2019-w08-solutions}

At the frozen revision boundary, the source provides exactly three public
solutions among the 22 exercises on Worksheet 8: those for Exercises 8.3,
8.4, and 8.11. The frozen exercise map and candidate evidence record
negative results for Exercises 8.1-8.2, 8.5-8.10, and 8.12-8.22. No new
solutions have been created for this edition.

## Source solution to Exercise 8.3 {#br-bgk-2019-w08-ex03-solution}

First, let $\mathfrak p$ be a prime ideal. In particular,

$$
\mathfrak p\subsetneq R,
$$

so the quotient ring $R/\mathfrak p$ is not the zero ring. Suppose
$fg=0$ in $R/\mathfrak p$, where $f$ and $g$ are represented by elements
of $R$. Then $fg\in\mathfrak p$, so $f\in\mathfrak p$ or
$g\in\mathfrak p$. In $R/\mathfrak p$, this means precisely that $f=0$
or $g=0$.

Conversely, suppose $R/\mathfrak p$ is an integral domain. It is not the
zero ring, so $\mathfrak p\ne R$. Take $f,g\notin\mathfrak p$. Then
$f,g\ne0$ in $R/\mathfrak p$ and, since this ring is an integral domain,

$$
fg\ne0
$$

in $R/\mathfrak p$. Thus $fg\notin\mathfrak p$, proving that
$\mathfrak p$ is prime.

## Source solution to Exercise 8.4 {#br-bgk-2019-w08-ex04-solution}

First, let $\mathfrak a$ be a prime ideal. Then $R/\mathfrak a$ is an
integral domain, so its field of fractions

$$
Q(R/\mathfrak a)
$$

exists. The canonical projection followed by inclusion into the field of
fractions,

$$
\begin{aligned}
\varphi:R&\longrightarrow Q(R/\mathfrak a),\\
x&\longmapsto[x],
\end{aligned}
$$

is therefore a ring homomorphism to a field with

$$
\ker\varphi=\mathfrak a.
$$

Conversely, the kernel of a ring homomorphism

$$
\varphi:R\longrightarrow K
$$

is always an ideal. If $ab\in\ker\varphi$, then

$$
0=\varphi(ab)=\varphi(a)\varphi(b).
$$

Since the field $K$ has no zero divisors, we obtain $\varphi(a)=0$ or
$\varphi(b)=0$. This is equivalent to $a\in\ker\varphi$ or
$b\in\ker\varphi$. Thus $\ker\varphi$ is a prime ideal.

## Source solution to Exercise 8.11 {#br-bgk-2019-w08-ex11-solution}

We first show that, for a suitable $f\in R$, the map

$$
R_f\longrightarrow S_{\varphi(f)}
$$

is surjective. Take a set of $K$-algebra generators $x_1,\ldots,x_n$ for
$S$. Since the local map in the hypothesis is surjective, there are
elements

$$
y_i=\frac{r_i}{g_i},
\qquad g_i\notin\mathfrak m,
$$

with $\varphi(y_i)=x_i$ in $S_{\mathfrak n}$. This means
$y_ig_i=r_i$ for $i=1,\ldots,n$. With

$$
f=g_1\cdots g_n,
$$

all the $y_i$ can be written over the common denominator $f$, so
$y_i\in R_f$. The map $R_f\to S_{\varphi(f)}$ is surjective because a
set of generators lies in its image and the denominators $\varphi(f)^n$
are the images of $f^n$.

We claim that this map is also injective. Suppose $q\in R_f$ maps to zero.
Then $q$ is also zero in $S_{\mathfrak n}$ and comes from
$q\in R_{\mathfrak m}$. Since the local map is an isomorphism, $q=0$ in
$R_{\mathfrak m}$. Since $R$ is an integral domain by hypothesis, this
also gives $q=0$ in $R_f$. Thus the map is injective and hence an
isomorphism.

