---
title: "Public Solutions to Worksheet 19"
stable_id: br-ak-2025-2026-w19-solutions
language: en
upstream_map: authority/wikiversity/unit-19/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: f75bcc8e564cef327687b486bb074fa8c799b065994f4a1d79e7abf2b78b30dd
public_solution_count: 2
upstream_solution_revisions: "Soal 19.4=1089525; Soal 19.12=1089395"
solution_xml_sha256: "04=d7bb006cf095c0f6bd86d7690802bf62956452bc2d6f739b1c3005325828981a; 12=c1f14a69bfcc5cc33d7f2b50a07abf49163fa04631cfcd5cd083cea81a62f3c5"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 19 {#br-ak-2025-2026-w19-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 19.4 and 19.12. No additional solutions have been created for this edition.

<!-- upstream_solution: Ganze Erweiterung/Integritätsbereich/Nichteinheit bleibt Nichteinheit/Aufgabe/Lösung; pageid=17225; revid=1089525 -->
<!-- upstream_solution_revid: 1089525 -->

## Solution to Exercise 19.4 {#br-ak-2025-2026-w19-sol-04}

Let $s\in S$ be the inverse of $f$, so that $fs=1$. Since $S$ is integral over $R$, there is an equation of integral dependence for $s$, say

$$
s^n+a_{n-1}s^{n-1}+\cdots+a_1s+a_0=0,
\qquad a_i\in R.
$$

Multiplying this equation by $f^n$ gives

$$
(fs)^n+a_{n-1}f(fs)^{n-1}+\cdots+a_1f^{n-1}(fs)+a_0f^n=0,
$$

or, since $fs=1$,

$$
1+a_{n-1}f+\cdots+a_1f^{n-1}+a_0f^n=0.
$$

Factoring out $f$ gives

$$
1+f\left(a_{n-1}+\cdots+a_1f^{n-2}+a_0f^{n-1}\right)=0,
$$

and hence

$$
f\left(-a_{n-1}-\cdots-a_1f^{n-2}-a_0f^{n-1}\right)=1.
$$

The expression in parentheses belongs to $R$. Thus $f$ also has an inverse in $R$.

[Back to Exercise 19.4](#br-ak-2025-2026-w19-ex-04).

<!-- upstream_solution: Endliche Erweiterung/KX/Explizit/Relation über X invers/Aufgabe/Lösung; pageid=134951; revid=1089395 -->
<!-- upstream_solution_revid: 1089395 -->

## Solution to Exercise 19.12 {#br-ak-2025-2026-w19-sol-12}

Multiply the given equation of integral dependence by $X^{-kn}$. In the field of fractions $Q$ of the quotient ring defining $R$, we obtain

$$
Y^nX^{-kn}+\sum_{i=0}^{n-1}P_iY^iX^{-kn}=0.
$$

Here

$$
Y^nX^{-kn}=(YX^{-k})^n
$$

and

$$
\begin{aligned}
P_iY^iX^{-kn}
&=P_iY^iX^{-ki}X^{-k(n-i)}\\
&=(YX^{-k})^iP_iX^{-k(n-i)}.
\end{aligned}
$$

The condition on $k$ ensures that

$$
P_iX^{-k(n-i)}
$$

is a polynomial in $X^{-1}$. Thus the resulting equation is a monic equation of integral dependence of degree $n$ for $YX^{-k}$ over $K[X^{-1}]$.

Since $R$ is an integral domain, the original defining polynomial is irreducible. After the invertible change of variable over $K(X)$, the resulting monic polynomial is irreducible in $K[X^{-1}][Z]$, where $Z$ is a formal variable subsequently mapped to $YX^{-k}$.

**Edition note:** the source calls this equation irreducible “in $K[X^{-1},YX^{-k}]$”. In that quotient algebra the relation is zero; the appropriate polynomial ring in which to state irreducibility is $K[X^{-1}][Z]$. This edition clarifies the ambient polynomial ring and formal variable; the claim is not needed for either of the two requested conclusions.

We have

$$
K[X^{-1}][YX^{-k}]\subseteq Q.
$$

The field of fractions of the left-hand side contains $X$ as the inverse of $X^{-1}$, and then contains

$$
Y=(YX^{-k})X^k.
$$

Its field of fractions therefore contains $K(X,Y)=Q$. The reverse inclusion is clear from the inclusion above, so the two fields of fractions are equal.

[Back to Exercise 19.12](#br-ak-2025-2026-w19-ex-12).

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
