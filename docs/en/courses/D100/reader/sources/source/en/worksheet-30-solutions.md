---
title: "Public Solutions to Worksheet 30"
stable_id: br-ak-2012-w30-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributors: "Exercise 30.3: Bocardodarapti; Exercise 30.4: Arbota"
upstream_map: authority/wikiversity/unit-30/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 7b6ed646202784b0ae03782e76e751336516d2dda0ed17ecf70500ea2d7a491e
authority_manifest: authority/wikiversity/unit-30/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: b990783fda97e721cc415740671e75c749400c408481ab88f4afd68f286d8b8a
candidate_evidence: authority/wikiversity/unit-30/worksheet-solution-candidates-api.json
public_solution_count: 2
negative_public_solution_count: 10
negative_solution_numbers: "1, 2, 5-12"
upstream_solution_revisions: "Exercise 30.3=1112942; Exercise 30.4=1106652"
solution_xml_sha256: "3=2657d734224c0681b15fd19b6dd1284f704e27b0eb3397e4cf7f91065f43ebcb; 4=1eb565f3f8ca6acd72b53a130427c18b1ca957b804b9ab7463d826396f8e9bd1"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain the component notices recorded in the Unit 30 rights ledger"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
correction_ids: "AGC-CORR-0134; AGC-CORR-0135"
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 30 {#br-ak-2012-w30-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 30.3 and 30.4. The frozen authority query reports the other ten candidate solution pages as absent. No additional solutions have been created for this edition.

<!-- upstream_solution: Ebene Kurven/Schnitt und Schnittmultiplizität/Y ist X^3 und Y^2 ist X^3/Aufgabe/Lösung; pageid=21320; revid=1112942 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1112942 -->

## Solution to Exercise 30.3 {#br-ak-2012-w30-sol-03}

The intersection points of the two curves in the complex affine plane are given by

$$
V(Y-X^3,\,Y^2-X^3).
$$

Thus an intersection point $(x,y)$ must satisfy

$$
y=x^3
\qquad\text{and}\qquad
y^2=x^3.
$$

Substituting the first equation into the second gives

$$
y(y-1)=0.
$$

Hence $y=0$ or $y=1$. The intersection points are therefore

$$
\{(0,0),(1,1),(\zeta,1),(\zeta^2,1)\},
$$

where $\zeta$ is a primitive cube root of unity. At the origin, the quotient ring is

$$
\begin{aligned}
\mathbb C[X,Y]_{(X,Y)}/(Y-X^3,Y^2-X^3)
&\cong \mathbb C[X]_{(X)}/(X^3,X^6-X^3)\\
&\cong \mathbb C[X]/(X^3).
\end{aligned}
$$

Its dimension as a complex vector space is $3$, so the intersection multiplicity at the origin is $3$.

To determine the multiplicities at the other three points, compute the gradients in the conventional coordinate order $(X,Y)$. For

$$
F=Y-X^3,
\qquad
G=Y^2-X^3,
$$

we obtain

$$
\nabla F=(-3x^2,1)
\qquad\text{and}\qquad
\nabla G=(-3x^2,2y)=(-3x^2,2).
$$

Since $x\ne0$, these two directions are linearly independent. Thus both curves are smooth and intersect transversely at the three points; each has intersection multiplicity $1$.

> **Source correction AGC-CORR-0134 - order of gradient components.** The source writes derivative components in the implicit order $(Y,X)$ in one part of the solution, unlike the convention $(X,Y)$ used elsewhere. This edition writes both gradients consistently in the order $(X,Y)$; the transversality test and its result are unchanged.

In projective space, we homogenise the two ideals. Thus we consider

$$
V_+(YZ^2-X^3)
\qquad\text{and}\qquad
V_+(Y^2Z-X^3).
$$

Setting $Z=0$ gives $X=0$, so the intersection point at infinity is $(0,1,0)$. The affine neighbourhood $D_+(Y)$ gives the equations

$$
Z^2-X^3
\qquad\text{and}\qquad
Z-X^3.
$$

At the origin of this chart, eliminating $Z$ again gives a local quotient of dimension $3$. Hence the intersection multiplicity at this point at infinity is also $3$. The sum of all intersection multiplicities is

$$
3+3\cdot1+3=9,
$$

in agreement with the product of the two curve degrees, $3\cdot3=9$.

<!-- upstream_solution: Ebene Kurven/Schnitt und Schnittmultiplizität/Y ist X^2 und Y^2 ist X^5/Aufgabe/Lösung; pageid=21596; revid=1106652 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1106652 -->

## Solution to Exercise 30.4 {#br-ak-2012-w30-sol-04}

Adding the two equations immediately gives the condition

$$
0=X-X^5=X(1-X^4).
$$

Thus the $x$-coordinate of an intersection point is $0$ or a fourth root of unity,

$$
x\in\{0,1,-1,i,-i\}.
$$

If $x=0$, we immediately obtain $y=0$. The local quotient ring can be written as

$$
\begin{aligned}
\mathbb C[X,Y]_{(X,Y)}/(X-Y^2,Y^2-X^5)
&\cong \mathbb C[Y]_{(Y)}/(Y^2-Y^{10})\\
&=\mathbb C[Y]_{(Y)}/\bigl(Y^2(1-Y^8)\bigr)\\
&\cong \mathbb C[Y]_{(Y)}/(Y^2).
\end{aligned}
$$

Since $1-Y^8$ is a unit in this local ring, the intersection multiplicity at $(0,0)$ is $2$.

> **Source correction AGC-CORR-0135 - localisation subscript.** In the middle line, the source prints $\mathbb C[Y]_Y$, which usually means inverting powers of $Y$ and cannot be the local ring at the origin. This edition retains the localisation specified in the preceding line, $\mathbb C[Y]_{(Y)}$, making the unit and local-length argument valid.

Now suppose $x$ is a fourth root of unity. Since $y^2=x$, the number $y$ is an eighth root of unity. If $\zeta$ is the first primitive eighth root of unity, the other eight intersection points are

$$
\begin{gathered}
(1,1),(1,-1),(i,\zeta),(i,-\zeta),\\
(-1,i),(-1,-i),(-i,\zeta^3),(-i,-\zeta^3).
\end{gathered}
$$

We show that the intersection is transverse at all eight points, so each intersection multiplicity is $1$. For

$$
F=X-Y^2,
\qquad
G=Y^2-X^5,
$$

the gradients are

$$
\nabla F=(1,-2Y)
\qquad\text{and}\qquad
\nabla G=(-5X^4,2Y).
$$

At each point $(x,y)$ above, $x\ne0$, so both curves are smooth. Since $x^4=1$, the second gradient has the form $(-5,2y)$. The two directions can be linearly dependent only if $-2y=-10y$, which is impossible because $y\ne0$ over $\mathbb C$. Thus all eight intersections are transverse.

Finally, consider the points at infinity. The homogenisation of the first equation is

$$
\widetilde F=XZ-Y^2,
$$

so the unique point at infinity on $\overline C=V_+(\widetilde F)$ is $(1,0,0)$. The homogenisation of the second equation is

$$
\widetilde G=Y^2Z^3-X^5,
$$

so the unique point at infinity on $\overline D=V_+(\widetilde G)$ is $(0,1,0)$. These points differ, so there is no additional intersection at infinity.

The total intersection multiplicity is therefore

$$
2+8\cdot1=10.
$$

Since the curves have degrees $2$ and $5$, this sum equals the product of their degrees, $2\cdot5=10$, as asserted by Bézout's Theorem.

