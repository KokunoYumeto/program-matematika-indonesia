---
title: "Public Solutions to Worksheet 3"
stable_id: br-ak-2025-2026-w03-solutions
language: en
upstream_map: authority/wikiversity/unit-03/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 0cd5be78df020c99ba2baefe4a39fffeb49268c266896f86679ca2b90ed259fb
public_solution_count: 2
license: CC BY-SA 4.0
translation_status: complete
---

# Public Solutions to Worksheet 3 {#br-ak-2025-2026-w03-solutions}

The source provides public solutions only to Exercises 3.11 and 3.13 at the
frozen revision boundary. No additional solutions have been created for this edition.

## Solution to Exercise 3.11 {#br-ak-2025-2026-w03-sol-11}

<!-- upstream_solution_revid: 1010523 -->

Suppose that $f^k=0$. Then

$$
\begin{aligned}
&(1+f)(1-f+f^2-f^3+f^4\pm\cdots\pm f^{k-1})\\
&=1-f+f^2-f^3+f^4\pm\cdots\pm f^{k-1}
  +f-f^2+f^3-f^4\mp\cdots\mp f^{k-1}\\
&=1.
\end{aligned}
$$

Thus the element

$$
1-f+f^2-f^3+f^4\pm\cdots\pm f^{k-1}
$$

is the inverse of $1+f$, so $1+f$ is a unit.

[Back to Exercise 3.11](#br-ak-2025-2026-w03-ex-11).

## Solution to Exercise 3.13 {#br-ak-2025-2026-w03-sol-13}

<!-- upstream_solution_revid: 1089748 -->

Let $\mathfrak a$ be a radical ideal and $f\in R/\mathfrak a$ nilpotent. Then

$$
f^r=0
$$

in $R/\mathfrak a$ for some $r$. Interpreted back in $R$, this means
$f^r\in\mathfrak a$, using the same letter for a representative. Since
$\mathfrak a$ is radical, $f\in\mathfrak a$, so $f=0$ in the quotient ring.
Thus the quotient ring is reduced.

Conversely, suppose that an ideal

$$
\mathfrak a\subseteq R
$$

has reduced quotient ring $R/\mathfrak a$. Suppose that
$f^r\in\mathfrak a$. Then the residue class of $f^r$ is $0$. Since the
quotient ring is reduced, the residue class of $f$ itself is already $0$.
This means that $f\in\mathfrak a$, so the ideal is radical.

[Back to Exercise 3.13](#br-ak-2025-2026-w03-ex-13).
