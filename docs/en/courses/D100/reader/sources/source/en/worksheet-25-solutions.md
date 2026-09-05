---
title: "Public Solutions to Worksheet 25"
stable_id: br-ak-2012-w25-solutions
language: en
source_course: "Algebraische Kurven (Osnabrück 2012)"
source_author: "Holger Brenner"
frozen_revision_contributors: "Exercise 25.1: Bocardodarapti; Exercise 25.2: Arbota"
upstream_map: authority/wikiversity/unit-25/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 1a887b81de9ccf9707e1e4835e477f9c9fb4a4358ab697242b17fd29873e8370
authority_manifest: authority/wikiversity/unit-25/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: 7cafbca7b5fd080529c2019967647ef8ffa823539b2113caaf0ad65e56d6afc1
public_solution_count: 2
upstream_solution_revisions: "Exercise 25.1=1112930; Exercise 25.2=1022975"
solution_xml_sha256: "01=39ac23016a2014f255207ba743a8537d2e0744a7aa3d624e16cd2de1f5bf4ad5; 02=74a2d210868885487a9091acf5735ff97fb8a1809f697440bb87083584df6570"
license: "CC BY-SA 4.0 for the frozen semantic source; official 2012 PDF witnesses retain their recorded CC BY-SA 2.0 Germany notice"
no_blanket_relicensing_claim: true
independent_derivative_non_endorsement: true
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 0
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 25 {#br-ak-2012-w25-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 25.1 and 25.2. The frozen authority query records the other
eleven candidate solution pages as absent. No additional solutions have
been created for this edition.

<!-- upstream_solution: Ebene algebraische Kurve/Potenzreihenansatz/x^3+y^2-xy+x/Nullpunkt/Aufgabe/Lösung; pageid=21296; revid=1112930 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1112930 -->

## Solution to Exercise 25.1 {#br-ak-2012-w25-sol-01}

We make the ansatz

$$
X=F(Y)=\sum_{i=0}^{\infty}a_iY^i
$$

and determine the coefficients $a_0,\ldots,a_6$ from the condition

$$
\left(\sum_{i=0}^{\infty}a_iY^i\right)^3
+Y^2
-\left(\sum_{i=0}^{\infty}a_iY^i\right)Y
+\left(\sum_{i=0}^{\infty}a_iY^i\right)
=0.
$$

Since the power series must approximate the curve at the origin, we must
have

$$
a_0=0.
$$

For $Y^1$, the coefficient condition is

$$
a_1=0,
$$

since the first three summands in the equation contribute nothing. For
$Y^2$, we obtain

$$
1+a_2=0,
\qquad\text{hence}\qquad
a_2=-1.
$$

This deals with the second summand $Y^2$. For $Y^3$, we obtain

$$
-a_2+a_3=0,
\qquad\text{hence}\qquad
a_3=a_2=-1.
$$

For $Y^4$, we obtain

$$
-a_3+a_4=0,
\qquad\text{hence}\qquad
a_4=a_3=-1,
$$

and for $Y^5$,

$$
-a_4+a_5=0,
\qquad\text{hence}\qquad
a_5=a_4=-1.
$$

At $Y^6$, the first summand must be included for the first time. We obtain

$$
a_2^3-a_5+a_6=0,
\qquad\text{hence}\qquad
a_6=a_5-a_2^3=-1-(-1)^3=0.
$$

[Back to Exercise 25.1](#br-ak-2012-w25-ex-01)

<!-- upstream_solution: Ebene algebraische Kurve/Potenzreihenansatz/x^2y+x^2+y^2-5xy+y/Nullpunkt/Aufgabe/Lösung; pageid=21581; revid=1022975 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1022975 -->

## Solution to Exercise 25.2 {#br-ak-2012-w25-sol-02}

We make the ansatz

$$
Y=F(X)=\sum_{n=0}^{\infty}a_nX^n
$$

(and $X=X$), and determine the coefficients successively by comparing
coefficients of powers of $X$. Since the solution must pass through the
origin, we require $a_0=0$.

$$
X^1:\qquad a_1=0.
$$

$$
X^2:\qquad 1+a_2=0,
\qquad\text{hence}\qquad a_2=-1.
$$

$$
X^3:\qquad -5a_2+a_3=0,
\qquad\text{hence}\qquad a_3=-5.
$$

$$
X^4:\qquad a_2+a_2^2-5a_3+a_4=0,
\qquad\text{hence}\qquad a_4=5a_3=-25.
$$

$$
\begin{aligned}
X^5:\qquad
a_3+2a_2a_3-5a_4+a_5&=0,\\
a_5&=-a_3-2a_2a_3+5a_4\\
&=5-10-125\\
&=-130.
\end{aligned}
$$

The initial terms of the power series are therefore

$$
F=-X^2-5X^3-25X^4-130X^5+\ldots.
$$

[Back to Exercise 25.2](#br-ak-2012-w25-ex-02)
