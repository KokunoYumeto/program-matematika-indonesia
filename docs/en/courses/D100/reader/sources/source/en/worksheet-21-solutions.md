---
title: "Public Solutions to Worksheet 21"
stable_id: br-ak-2025-2026-w21-solutions
language: en
upstream_map: authority/wikiversity/unit-21/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 9329621bbdd62df63f01d7298dc2a4a65a296211db131f8d8730b7d308fd5f47
public_solution_count: 2
upstream_solution_revisions: "Soal 21.3=1068126; Soal 21.8=1113184"
solution_xml_sha256: "03=70d121ea8136ceefbc726198671bd03643ba84382f694a5aafa66272c522bdf9; 08=5821567b75632728c65045870c4aede0d84d7a39c0901c8320cfded033259b71"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 21 {#br-ak-2025-2026-w21-solutions}

At the frozen revision boundary, the source provides public solutions only for Exercises 21.3 and 21.8. Both are complete source bodies without wrapper transclusions. No additional solutions have been created for this edition.

<!-- upstream_solution: Diskreter Bewertungsring/Zwischenringe im Quotientenkörper/Aufgabe/Lösung; pageid=168446; revid=1068126 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1068126 -->

## Solution to Exercise 21.3 {#br-ak-2025-2026-w21-sol-03}

Let the maximal ideal of $R$ be

$$
\mathfrak m=(\pi).
$$

The field of fractions of $R$ is

$$
Q(R)=R_\pi,
$$

and every nonzero element of this field has the form

$$
u\pi^n,
\qquad u\in R^\times,\quad n\in\mathbb Z.
$$

Suppose

$$
R\subsetneq T\subseteq Q(R).
$$

Since the first inclusion is strict, there is an element

$$
u\pi^n\in T
$$

with $n<0$. Since $u$ is a unit in $R\subseteq T$, we also have $\pi^n\in T$. Moreover, $-n-1\geq0$, so

$$
\pi^{-1}=\pi^{-n-1}\pi^n\in T.
$$

Thus $R_\pi\subseteq T$. Together with $T\subseteq Q(R)=R_\pi$, this gives

$$
T=Q(R).
$$

Hence there is no proper intermediate ring between $R$ and its field of fractions.

[Back to Exercise 21.3](#br-ak-2025-2026-w21-ex-03).

<!-- upstream_solution: Bewertungstheorie/Körper mit diskreter Bewertung/Diskreter Bewertungsring/Aufgabe/Lösung; pageid=16847; revid=1113184 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1113184 -->

## Solution to Exercise 21.8 {#br-ak-2025-2026-w21-sol-08}

First we show that $R$ is a subring of the field $K$. By definition, $0\in R$. Since $\nu$ is a group homomorphism,

$$
\nu(1)=0,
$$

so $1\in R$. For $f,g\in R$, closure under multiplication is immediate if either element is zero. If $f$ and $g$ are nonzero, then

$$
\nu(fg)=\nu(f)+\nu(g)\geq0,
$$

so $fg\in R$. For addition, if either $f$ or $g$ is zero, or if $f+g=0$, closure is again immediate. In the remaining case, $f,g,f+g$ are all nonzero and the hypothesis gives

$$
\nu(f+g)\geq\min\{\nu(f),\nu(g)\}\geq0.
$$

Thus $f+g\in R$. Moreover,

$$
\nu(-1)+\nu(-1)
=\nu((-1)^2)
=\nu(1)
=0,
$$

so $\nu(-1)=0$ and $-1\in R$. Hence $R$ is also closed under negation and is a commutative ring.

Next we show that $R$ is local. Set

$$
\mathfrak m
:=
\{f\in K^\times\mid \nu(f)\geq1\}\cup\{0\}
\subseteq R.
$$

This set contains $0$. For $f,g\in\mathfrak m$, the cases involving zero or satisfying $f+g=0$ are immediate. Otherwise,

$$
\nu(f+g)\geq\min\{\nu(f),\nu(g)\}\geq1,
$$

so $f+g\in\mathfrak m$. For $f\in\mathfrak m$ and $g\in R$, the cases $f=0$ or $g=0$ are also immediate. If both are nonzero, then

$$
\nu(gf)=\nu(g)+\nu(f)\geq1,
$$

so $gf\in\mathfrak m$. Thus $\mathfrak m$ is an ideal.

The complement $R\setminus\mathfrak m$ consists exactly of the elements $h\in K^\times$ with

$$
\nu(h)=0.
$$

For such an element,

$$
\nu(h^{-1})=-\nu(h)=0,
$$

so $h^{-1}\in R$. Thus every element of $R\setminus\mathfrak m$ is a unit. Consequently $\mathfrak m$ is the unique maximal ideal and $R$ is local.

It remains to show that $R$ is a discrete valuation ring. Since $\nu$ is surjective, there is a $p\in K^\times$ with

$$
\nu(p)=1.
$$

In particular, $p\in R$. We show that $p$ is prime. For nonzero elements $x,y\in R$, the element $y$ is a multiple of $x$ exactly when

$$
\nu(y)\geq\nu(x),
$$

since this condition is equivalent to $y/x\in R$. Now suppose that $p\mid xy$ for $x,y\in R$. If $xy=0$, one factor is zero and is certainly a multiple of $p$. If $xy\ne0$, then

$$
1=\nu(p)\leq\nu(xy)=\nu(x)+\nu(y).
$$

Since $\nu(x)$ and $\nu(y)$ are nonnegative integers, either $\nu(x)\geq1$ or $\nu(y)\geq1$. By the divisibility criterion above, $p$ divides either $x$ or $y$. Thus $p$ is prime.

By the same argument, every nonzero element $x\in R$ with

$$
n=\nu(x)
$$

is associated to $p^n$. Indeed, $\nu(x/p^n)=0$, so $x/p^n$ is a unit in $R$. Thus $R$ is a principal ideal domain whose ideals are exactly $0$ and

$$
(p^n),
\qquad n\in\mathbb N.
$$

Hence $R$ is a discrete valuation ring.

**Edition note:** the source defines $\nu$ only on $K^\times$ but states the inequality for $\nu(f+g)$ without the condition $f+g\ne0$. Since $\nu(0)$ is undefined, this edition uses the inequality only when $f+g\ne0$ and handles zero sums separately; it does not extend $\nu$ to $0$.

[Back to Exercise 21.8](#br-ak-2025-2026-w21-ex-08).

---

**Edition provenance.** Translation and reader production: OpenAI Codex
gpt-5.6-sol, Ultra. Sources, authors, and component licences are retained
as stated in the metadata and the edition's rights files.
