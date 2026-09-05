---
title: "Public Solutions to Worksheet 9"
stable_id: br-ak-2025-2026-w09-solutions
language: en
upstream_map: authority/wikiversity/unit-09/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: c906ba0b1073a162f7f55289c0f60114063d011756f1eb907bcf342336729495
public_solution_count: 3
upstream_solution_revisions: "Soal 9.6=1107958; Soal 9.13=1059490; Soal 9.18=1112817"
solution_ex06_xml_sha256: f9e6a938ce01a3bd784f5d1a68bb1c0ab1790f9f8d78baebd319ec23e949a626
solution_ex13_xml_sha256: 382b85fe25d73ac31562c00ffdddbd030784a795c80b59425855b45fbc73edc6
solution_ex18_xml_sha256: 47b1095efe3e91a251c3f77a2ddaa93a51c821e335138a16849a90150368696b
license: "CC BY-SA 4.0"
translation_status: complete
---

# Public Solutions to Worksheet 9 {#br-ak-2025-2026-w09-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 9.6, 9.13, and 9.18. No additional solutions have been created for this edition.

<!-- upstream_solution: Noetherscher Ring/Unterring/Aufgabe/Lösung; pageid=100296; revid=1107958 -->
<!-- upstream_solution_revid: 1107958 -->

## Solution to Exercise 9.6 {#br-ak-2025-2026-w09-sol-06}

Consider

$$
S=K[X,Y]
$$

as the polynomial ring in two variables over a field $K$. By Corollary 9.6, this ring is Noetherian. Within it, consider the subring

$$
R=\{Xg(X,Y)+c\mid g\in K[X,Y],\ c\in K\}
$$

and the chain of ideals in that subring

$$
\mathfrak a_n=(X,XY,\ldots,XY^n).
$$

For every $n\in\mathbb N$, we have

$$
XY^{n+1}\in\mathfrak a_{n+1}\setminus\mathfrak a_n,
$$

so the chain does not become stationary. By Proposition 9.2, $R$ is therefore not Noetherian.

[Back to Exercise 9.6](#br-ak-2025-2026-w09-ex-06).

<!-- upstream_solution: Endlich erzeugte Algebra/Endliches Teilsystem/Aufgabe/Lösung; pageid=167639; revid=1059490 -->
<!-- upstream_solution_revid: 1059490 -->

## Solution to Exercise 9.13 {#br-ak-2025-2026-w09-sol-13}

We have

$$
A=R[f_1,\ldots,f_n]\subseteq R[a_i,\ i\in I].
$$

Each $f_j$ can be written as a polynomial expression in the elements of the family $a_i$, with coefficients in $R$. For each $j$, only finitely many $a_i$ occur. Hence all the generators $f_j$ belong to

$$
R[a_i,\ i\in I']
$$

for some finite subfamily $I'\subseteq I$. Thus

$$
A=R[f_1,\ldots,f_n]\subseteq R[a_i,\ i\in I']
\subseteq A,
$$

and therefore $A=R[a_i,\ i\in I']$.

[Back to Exercise 9.13](#br-ak-2025-2026-w09-ex-13).

<!-- upstream_solution: Modul/Kommutativer Ring/Allgemeines Distributivgesetz/Aufgabe/Lösung; pageid=94177; revid=1112817 -->
<!-- upstream_solution_revid: 1112817 -->

## Solution to Exercise 9.18 {#br-ak-2025-2026-w09-sol-18}

We prove the statement by double induction on $k,n\geq1$. The cases

$$
(k,n)=(1,1),\qquad(1,2),\qquad(2,1)
$$

are immediately clear or follow directly from the module axioms.

For $k=1$ and arbitrary $n$, we prove the statement by induction on $n$, with the base case supplied by the preceding observation. Suppose the statement has been proved for some $n$, and let $n+1$ vectors $v_1,\ldots,v_n,v_{n+1}\in V$ be given. Using the case $(1,2)$ and the induction hypothesis, we obtain

$$
\begin{aligned}
s\cdot\left(\sum_{j=1}^{n+1}v_j\right)
&=s\cdot\left(\sum_{j=1}^{n}v_j+v_{n+1}\right)\\
&=s\cdot\left(\sum_{j=1}^{n}v_j\right)+sv_{n+1}\\
&=\sum_{1\leq j\leq n}s\cdot v_j+sv_{n+1}\\
&=\sum_{1\leq j\leq n+1}s\cdot v_j.
\end{aligned}
$$

Now consider the statement for fixed $k$ and arbitrary $n$. For $k=1$, it has already been proved. Suppose it has been proved for some fixed $k$. Let scalars

$$
s_1,\ldots,s_k,s_{k+1}\in R
$$

and vectors

$$
v_1,\ldots,v_n\in V
$$

be given. Using the cases $(2,1)$ and $(1,n)$ and the induction hypothesis, we obtain

$$
\begin{aligned}
\left(\sum_{i=1}^{k+1}s_i\right)\!\cdot
 \left(\sum_{j=1}^{n}v_j\right)
&=\left(\sum_{i=1}^{k}s_i+s_{k+1}\right)\!\cdot
 \left(\sum_{j=1}^{n}v_j\right)\\
&=\left(\sum_{i=1}^{k}s_i\right)\!\cdot
 \left(\sum_{j=1}^{n}v_j\right)
 +s_{k+1}\cdot\left(\sum_{j=1}^{n}v_j\right)\\
&=\sum_{1\leq i\leq k,\,1\leq j\leq n}s_i\cdot v_j
 +\sum_{j=1}^{n}s_{k+1}\cdot v_j\\
&=\sum_{1\leq i\leq k+1,\,1\leq j\leq n}s_i\cdot v_j.
\end{aligned}
$$

[Back to Exercise 9.18](#br-ak-2025-2026-w09-ex-18).
