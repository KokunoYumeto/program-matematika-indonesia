---
title: "Public Solutions to Worksheet 10"
stable_id: br-ak-2025-2026-w10-solutions
language: en
upstream_map: authority/wikiversity/unit-10/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 972e36256d128916533a33be1d2feedfdecbd133a0dbba96193a85477cf7e92c
public_solution_count: 6
upstream_solution_revisions: "Soal 10.1=1028855; Soal 10.6=1068028; Soal 10.9=1068729; Soal 10.16=536882; Soal 10.17=743216; Soal 10.20=1112824"
solution_ex01_xml_sha256: 31c3ede05c3c48f6874d9438be3268fb23fb82e34d86e86019b7d88943b35860
solution_ex06_xml_sha256: 876565809f57d44a1c7721ec1ca3a591f1236a4dad869558c871c14d7602a97f
solution_ex09_xml_sha256: 7f2d29f86b768f7b953873e092ab3da83f6c4cc7c7a87a343fa574463d6591c8
solution_ex16_xml_sha256: 20633a9d709de29027a543a08d402f7daaa76326cc624dcce6d14763bb0b620d
solution_ex17_xml_sha256: b7db71351f962f7a6621fd23a555ce07f7afbb07cc81a34aed96368acf885ca1
solution_ex20_xml_sha256: 8969cca31d81d18bf98bb7ea9b008e8e15d169caf0037312a45c9c91f13d9557
license: "CC BY-SA 4.0"
translation_status: complete
---

# Public Solutions to Worksheet 10 {#br-ak-2025-2026-w10-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 10.1, 10.6, 10.9, 10.16, 10.17, and 10.20. No additional
solutions have been created for this edition.

<!-- upstream_solution: Endliche Algebra über Körper/Kommutativ/Einheit und Nichtnullteiler/Aufgabe/Lösung; pageid=94256; revid=1028855 -->
<!-- upstream_solution_revid: 1028855 -->

## Solution to Exercise 10.1 {#br-ak-2025-2026-w10-sol-01}

If $f$ is a unit, there is a $g\in A$ with $gf=1$. From $fh=0$ we immediately obtain

$$
h=gfh=g0=0.
$$

Thus $f$ is a non-zero-divisor.

Conversely, if $f$ is a non-zero-divisor, consider the $K$-linear multiplication map

$$
\mu_f:A\longrightarrow A,
\qquad h\longmapsto fh.
$$

This map is injective. Since $A$ is finite as a module over the field $K$,
it is a finite-dimensional $K$-vector space. An injective endomorphism of
a finite-dimensional vector space is also surjective. In particular, there
is a $g\in A$ with $fg=1$. This means that $f$ is a unit.

[Back to Exercise 10.1](#br-ak-2025-2026-w10-ex-01).

<!-- upstream_solution: Kommutativer Ring/Ideale/Chinesischer Restsatz/Kurze exakte Sequenz/Aufgabe/Lösung; pageid=168416; revid=1068028 -->
<!-- upstream_solution_revid: 1068028 -->

## Solution to Exercise 10.6 {#br-ak-2025-2026-w10-sol-06}

Choose a representative $r\in R$ of a class in $R/(I\cap J)$ that maps to $(r,r)=0$ in $R/I\times R/J$.
Both components are $0$, so $r\in I$ and $r\in J$. Thus $r\in I\cap J$,
and hence the class of $r$ on the left is $0$. The map on the left is
therefore injective.

The composite map is given by

$$
r\longmapsto(r,r)\longmapsto r-r,
$$

so it is the zero map. Conversely, if $(s,t)$ maps to $0$ on the right,
then $s-t\in I+J$. Say

$$
s-t=a+b,
\qquad a\in I,\quad b\in J.
$$

Then

$$
s-a=t+b
$$

in $R$. This element also represents $(s,t)$, so $(s,t)$ comes from the
left. Surjectivity of the last map follows immediately by choosing $t=0$.

[Back to Exercise 10.6](#br-ak-2025-2026-w10-ex-06).

<!-- upstream_solution: Kurze exakte Sequenz/Modul/Duale Sequenz/Aufgabe/Lösung; pageid=168494; revid=1068729 -->
<!-- upstream_solution_revid: 1068729 -->

## Solution to Exercise 10.9 {#br-ak-2025-2026-w10-sol-09}

Surjectivity of the map $M\to N$ immediately implies that the map

$$
N^*\longrightarrow M^*
$$

is injective: an $R$-linear map $N\to R$ whose composite with $M\to N$
is the zero map must itself be the zero map.

Since the composite $L\to M\to N$ is the zero map, the same holds for
the corresponding dual map.

It remains to show that a linear form $f\in M^*$ that maps to $0$ in
$L^*$ comes from a dual form in $N^*$. This condition says that the
restriction of $f$ to the submodule $L\subseteq M$ is the zero map. In
other words, $L$ is contained in the kernel of $f$. By the homomorphism
theorem, there is an induced homomorphism

$$
\widetilde f:M/L\longrightarrow R
$$

whose composite with $M\to M/L$ equals $f$. Since $M/L\cong N$, this is
the desired statement.

[Back to Exercise 10.9](#br-ak-2025-2026-w10-ex-09).

<!-- upstream_solution: Kommutative Ringtheorie/f nicht nilpotent/Existenz von Primidealen/Fakt/Beweis/Aufgabe/Lösung; pageid=95372; revid=536882 -->
<!-- upstream_solution_revid: 536882 -->

## Solution to Exercise 10.16 {#br-ak-2025-2026-w10-sol-16}

Consider the set of ideals

$$
\mathcal M=
\left\{\mathfrak a\text{ an ideal}\mid
f^r\notin\mathfrak a\text{ for every }r\right\}.
$$

This set is nonempty because it contains the zero ideal. Moreover,
$\mathcal M$ is inductively ordered by inclusion. Indeed, if the
$\mathfrak a_i$, $i\in I$, form a totally ordered subset of $\mathcal M$,
then their union is also an ideal containing no power of $f$. By Zorn's
lemma, $\mathcal M$ therefore has a maximal element.

We claim that every such maximal element, say $\mathfrak p$, is a prime
ideal. Take $g,h\in R$ with $gh\in\mathfrak p$, and suppose that
$g,h\notin\mathfrak p$. Then there are strict inclusions

$$
\mathfrak p\subsetneq\mathfrak p+(g),
\qquad
\mathfrak p\subsetneq\mathfrak p+(h).
$$

Since $\mathfrak p$ is maximal in $\mathcal M$, neither ideal on the
right belongs to $\mathcal M$. Thus there are $r,s\in\mathbb N$ such that

$$
f^r\in\mathfrak p+(g)
\qquad\text{and}\qquad
f^s\in\mathfrak p+(h).
$$

But multiplying these two relations gives the contradiction

$$
f^{r+s}\in\mathfrak p+(gh)\subseteq\mathfrak p.
$$

Thus $\mathfrak p$ is prime and, by the definition of $\mathcal M$,
$f\notin\mathfrak p$.

[Back to Exercise 10.16](#br-ak-2025-2026-w10-ex-16).

<!-- upstream_solution: Kommutative Ringtheorie/Ideale/Radikal ist Durchschnitt von Primidealen/Aufgabe/Lösung; pageid=140640; revid=743216 -->
<!-- upstream_solution_revid: 743216 -->

## Solution to Exercise 10.17 {#br-ak-2025-2026-w10-sol-17}

*Edition note.* The source directly equates ideals in $R$ with ideals in $R/\mathfrak a$. The argument below makes the required inverse-image correspondence explicit.

Let $\mathfrak a\subseteq R$ be a radical ideal. Then
$\mathfrak a=\sqrt{\mathfrak a}$. The nilradical of $R/\mathfrak a$ is
the intersection of all prime ideals in this quotient ring. Under the
correspondence between ideals of $R/\mathfrak a$ and ideals of $R$
containing $\mathfrak a$, this gives

$$
\sqrt{\mathfrak a}
=\bigcap_{\substack{\mathfrak p\supseteq\mathfrak a\\
                    \mathfrak p\text{ prime}}}\mathfrak p.
$$

Since $\mathfrak a=\sqrt{\mathfrak a}$, we obtain

$$
\mathfrak a
=\bigcap_{\substack{\mathfrak p\supseteq\mathfrak a\\
                    \mathfrak p\text{ prime}}}\mathfrak p.
$$

[Back to Exercise 10.17](#br-ak-2025-2026-w10-ex-17).

<!-- upstream_solution: Hilbertscher Nullstellensatz/Algebraisch/Z/Endlicher Körper/Aufgabe/Lösung; pageid=94501; revid=1112824 -->
<!-- upstream_solution_revid: 1112824 -->

## Solution to Exercise 10.20 {#br-ak-2025-2026-w10-sol-20}

Consider the composite map

$$
\mathbb Z\xrightarrow{\varphi}A\longrightarrow A/\mathfrak m=L,
$$

which is also of finite type. The inverse image
$\varphi^{-1}(\mathfrak m)$ is a prime ideal in $\mathbb Z$, so it is
either $(0)$ or $(p)$ for a prime number $p$.

In the first case there is a factorisation

$$
\mathbb Z\longrightarrow\mathbb Q\longrightarrow L.
$$

By Hilbert's Nullstellensatz, $L$ is finite over $\mathbb Q$, and by
Lemma 10.5, $\mathbb Q$ would then have to be finitely generated over
$\mathbb Z$, which is not the case. Thus the first case is impossible.

Consequently, the second case holds and there is a factorisation

$$
\mathbb Z\longrightarrow\mathbb Z/(p)\longrightarrow L.
$$

By Hilbert's Nullstellensatz, $L$ is finite over the finite field
$\mathbb Z/(p)$, so $L$ itself is finite.

[Back to Exercise 10.20](#br-ak-2025-2026-w10-ex-20).
