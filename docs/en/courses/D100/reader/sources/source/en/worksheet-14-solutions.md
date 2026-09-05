---
title: "Public Solutions to Worksheet 14"
stable_id: br-ak-2025-2026-w14-solutions
language: en
upstream_map: authority/wikiversity/unit-14/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 0d223f7f3c56c4714736dfc6eb3dbd40dc8cd3cb30a05f66281a6f2b1b875dbe
public_solution_count: 2
upstream_solution_revisions: "Soal 14.2=1068085; Soal 14.7=1095255"
solution_xml_sha256: "02=1f46f16de8715afb59c5f3ac7ec9c47968093ba3ca322e8bbeb63098b63cd96d; 07=34fd3f0291c291b74dd0b6fcd35aa6bac54d56f2d3aabecdb2f25ff9d2d181f4"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 14 {#br-ak-2025-2026-w14-solutions}

At the frozen revision boundary, the source provides public solutions only
for Exercises 14.2 and 14.7. No additional solutions have been created for
this edition.

<!-- upstream_solution: Integritätsbereich/Faktoriell/K-Spektrum/Algebraische Abbildung/Eindeutige Darstellung/Aufgabe/Lösung; pageid=168430; revid=1068085 -->
<!-- upstream_solution_revid: 1068085 -->

## Solution to Exercise 14.2 {#br-ak-2025-2026-w14-sol-02}

> **Edition note:** If $U=\varnothing$, the fraction $0/1$ represents its
> unique function. The source's cover-combining argument below concerns
> the nonempty case.

Let

$$
U=\bigcup_{i\in I}D(H_i)
$$

with $I$ finite, and suppose that on each $D(H_i)$ the function $f$ has a
representation

$$
f=\frac{F_i}{H_i},
$$

meaning that

$$
f(Q)=\frac{F_i(Q)}{H_i(Q)}
\qquad\text{for every }Q\in D(H_i).
$$

On the intersection $D(H_i)\cap D(H_j)$ we have

$$
\frac{F_i(Q)}{H_i(Q)}
=f(Q)
=\frac{F_j(Q)}{H_j(Q)}.
$$

Thus

$$
H_j(Q)F_i(Q)-H_i(Q)F_j(Q)=0
$$

for every $Q\in D(H_i)\cap D(H_j)$. Consequently the element

$$
H_iH_j(H_jF_i-H_iF_j)
$$

induces the zero function on all of $K\!-\!\operatorname{Spek}(R)$. Since
$R$ is an integral domain and $K$ is algebraically closed, the identity
theorem gives

$$
H_iH_j(H_jF_i-H_iF_j)=0
$$

in $R$. After discarding empty members of the cover, $H_i$ and $H_j$ are
nonzero; since $R$ is an integral domain, it follows that

$$
H_jF_i-H_iF_j=0,
$$

and hence

$$
H_jF_i=H_iF_j.
$$

By unique prime factorisation, there are elements $A,B,C,D$ and a unit $u$
such that

$$
H_jF_i=(AB)(CD)=(u^{-1}AD)(uBC)=H_iF_j.
$$

Hence

$$
\frac{F_i}{H_i}
=\frac{uCD}{AD}
=\frac{uC}{A}
=\frac{uBC}{AB}
=\frac{F_j}{H_j}.
$$

The fractional representation $uC/A$ holds on $D(H_i)\cup D(H_j)$. In this
way we can combine two members of the cover and reduce the index set $I$.
Since $I$ is finite, repetition eventually produces a single fraction
$G/H$ valid on all of $U$. By cancelling common factors, we may choose
$G$ and $H$ with no common nonunit factor, and of course $U\subseteq D(H)$.

[Back to Exercise 14.2](#br-ak-2025-2026-w14-ex-02).

<!-- upstream_solution: Neilsche Parabel/Rationale Funktion mit Pol in (1,1)/Aufgabe/Lösung; pageid=94830; revid=1095255 -->
<!-- upstream_solution_revid: 1095255 -->

## Solution to Exercise 14.7 {#br-ak-2025-2026-w14-sol-07}

The maximal ideal corresponding to $P$ is $(X-1,Y-1)$. In the coordinate
ring

$$
R=K[X,Y]/(Y^2-X^3)
$$

we have

$$
X^2(X-1)=X^3-X^2=Y^2-X^2=(Y-X)(Y+X).
$$

We may therefore set, in the fraction field,

$$
f:=\frac{X^2}{Y-X}=\frac{X+Y}{X-1}.
$$

These representations define an algebraic function on

$$
D(Y-X,X-1)=D(Y-1,X-1)=C\setminus\{P\}.
$$

To show that this function is not defined on all of $C$, consider the map

$$
\begin{aligned}
\varphi:\mathbb A_K^1&\longrightarrow C,\\
t&\longmapsto(t^2,t^3).
\end{aligned}
$$

We have

$$
\varphi^{-1}(C\setminus\{P\})=\mathbb A_K^1\setminus\{1\}.
$$

The pullback of $f$ under this map is

$$
\frac{t^2+t^3}{t^2-1}
=\frac{t^2(1+t)}{(t+1)(t-1)}
=\frac{t^2}{t-1}.
$$

This function has a pole at $t=1$ and cannot be extended to an algebraic
function on the whole affine line. Hence $f$ cannot be extended
algebraically to all of $C$ either.

**Edition note:** in the final cancellation step, the source displays
$-t^2/(t-1)$. The factorisation on the preceding line gives $t^2/(t-1)$
without a minus sign. The pole at $t=1$ and the conclusion of the proof are
unchanged.

[Back to Exercise 14.7](#br-ak-2025-2026-w14-ex-07).
