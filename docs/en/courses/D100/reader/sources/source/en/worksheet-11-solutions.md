---
title: "Public Solutions to Worksheet 11"
stable_id: br-ak-2025-2026-w11-solutions
language: en
upstream_map: authority/wikiversity/unit-11/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 6298bafd7656e4653b504706b437e89de7faa92a75fac10c31d51ad9644a20cf
public_solution_count: 2
upstream_solution_revisions: "Soal 11.6=1094883; Soal 11.7=1112854"
solution_ex06_xml_sha256: 51f80c3d46d2a7fd2637618a6e762f0ec0398a6010a0e0e9733796277b2e652d
solution_ex07_xml_sha256: aaa033e15eaf2c7115bd7f6c301b8646a96d1be86fc046da40e77ad21bca97c9
license: "CC BY-SA 4.0"
translation_status: complete
---

# Public Solutions to Worksheet 11 {#br-ak-2025-2026-w11-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 11.6 and 11.7. No additional solutions have been created for
this edition.

<!-- upstream_solution: Hilbertscher Nullstellensatz/Ebene algebraische Kurven/R und C/1/Aufgabe/Lösung; pageid=94452; revid=1094883 -->
<!-- upstream_solution_revid: 1094883 -->

## Solution to Exercise 11.6 {#br-ak-2025-2026-w11-sol-06}

1. The only real point of $V(X^2+Y^2)$ is the origin $(0,0)$, and this
   point lies on $V(X^2-Y^3)$. Thus

   $$
   V(X^2+Y^2)\subseteq V(X^2-Y^3)
   \subseteq\mathbb A_{\mathbb R}^2.
   $$

2. The corresponding inclusion does not hold over the complex numbers.
   For example,

   $$
   (1,\mathrm i)\in V(X^2+Y^2),
   $$

   but since $1\ne\mathrm i^3$, this point does not lie on $V(X^2-Y^3)$.

3. Suppose that $X^2-Y^3$ belonged to the radical of $(X^2+Y^2)$ in
   $\mathbb R[X,Y]$. After extending scalars, the same would immediately
   hold in $\mathbb C[X,Y]$. But the next part shows that this is not the case.

4. From part (2) and the easy direction of Hilbert's Nullstellensatz, it
   follows that $X^2-Y^3$ does not belong to the radical of $(X^2+Y^2)$ in
   $\mathbb C[X,Y]$.

[Back to Exercise 11.6](#br-ak-2025-2026-w11-ex-06).

<!-- upstream_solution: Hilbertscher Nullstellensatz/C/Linearkombination mit Funktionen/Aufgabe/Lösung; pageid=168417; revid=1112854 -->
<!-- upstream_solution_revid: 1112854 -->

## Solution to Exercise 11.7 {#br-ak-2025-2026-w11-sol-07}

We claim that

$$
V(f_1,\ldots,f_k)\subseteq V(f).
$$

Once this claim is proved, Hilbert's Nullstellensatz says that $f$ belongs
to the radical of $(f_1,\ldots,f_k)$.

Let

$$
P=(x_1,\ldots,x_n)\in\mathbb C^n
$$

and suppose that $P\in V(f_1,\ldots,f_k)$. This means that $f_i(P)=0$
for every $i$. Then

$$
\begin{aligned}
f(P)
&=(g_1f_1+\cdots+g_kf_k)(P)\\
&=g_1(P)f_1(P)+\cdots+g_k(P)f_k(P)\\
&=0.
\end{aligned}
$$

Thus $P\in V(f)$, proving the claim.

[Back to Exercise 11.7](#br-ak-2025-2026-w11-ex-07).
