---
title: "Public Solutions to Worksheet 12"
stable_id: br-ak-2025-2026-w12-solutions
language: en
upstream_map: authority/wikiversity/unit-12/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: a37f874ffa17dd35ed4375f2956786793e475fcd5e2ded0333207c546e7e91db
public_solution_count: 2
upstream_solution_revisions: "Soal 12.6=1068040; Soal 12.12=1089724"
solution_ex06_xml_sha256: 501ac61733a2cb317b0195407b74729e5f09beace36a9da8764708e036ea11c6
solution_ex12_xml_sha256: e59d798d41b83bf59e9fb4931a5f122ffb538ee3f8341669ab8b07db9a632894
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 12 {#br-ak-2025-2026-w12-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 12.6 and 12.12. No additional solutions have been created for
this edition.

<!-- upstream_solution: K-Spektrum/Algebraisch abgeschlossen/K-Punkt und maximales Ideal/Aufgabe/Lösung; pageid=168418; revid=1068040 -->
<!-- upstream_solution_revid: 1068040 -->

## Solution to Exercise 12.6 {#br-ak-2025-2026-w12-sol-06}

A $K$-point is a $K$-algebra homomorphism

$$
\varphi:A\longrightarrow K.
$$

Since $A$ is a $K$-algebra, this homomorphism is surjective. Its kernel
is a maximal ideal of $A$. Since $A$ is of finite type over an
algebraically closed field, the theorem that maximal ideals in an algebra
of finite type over an algebraically closed field are point ideals applies.
Thus the residue field at every maximal ideal equals $K$.

**Edition note:** The exercise names the algebra $R$, whereas the source
solution uses $A$. The source solution's notation $A$ is retained here.

[Back to Exercise 12.6](#br-ak-2025-2026-w12-ex-06).

<!-- upstream_solution: K-Spektrum/Einheitsideal und leere Nullstellenmenge/Nilpotent und ganze Nullstellenmenge/Aufgabe/Lösung; pageid=21584; revid=1089724 -->
<!-- upstream_solution_revid: 1089724 -->

## Solution to Exercise 12.12 {#br-ak-2025-2026-w12-sol-12}

If $\mathfrak a$ is the unit ideal, then $V(\mathfrak a)=\varnothing$,
because $1$ vanishes at no point. The converse holds if $K$ is
algebraically closed. Indeed, from

$$
V(1)\subseteq V(\mathfrak a)
$$

—since both sets are empty—Hilbert's Nullstellensatz immediately gives

$$
1=1^n\in\mathfrak a.
$$

For $K=\mathbb R$, the converse fails. The polynomial

$$
F=X^2+1
$$

is not a unit, but its zero locus is empty.

If $\mathfrak a$ is nilpotent, then every element of it is nilpotent
and therefore vanishes under every ring homomorphism to a field, since
fields are reduced. For an algebraically closed ground field, the
converse again holds. If $V(\mathfrak a)=X$, then for each
$f\in\mathfrak a$ we have

$$
V(\mathfrak a)\subseteq V(f)=X=V(0).
$$

By Hilbert's Nullstellensatz, this implies

$$
f^n=0,
$$

so $f$ is nilpotent. In a Noetherian ring, this also implies that the
ideal $\mathfrak a$ itself is nilpotent.

Over a finite field, this converse fails. For $K=\mathbb F_2$, the polynomial

$$
X^2-X\in K[X]
$$

is not nilpotent, but vanishes at both points—that is, at all points—of $K$.

[Back to Exercise 12.12](#br-ak-2025-2026-w12-ex-12).
