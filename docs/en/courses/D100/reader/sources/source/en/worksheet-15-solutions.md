---
title: "Public Solutions to Worksheet 15"
stable_id: br-ak-2025-2026-w15-solutions
language: en
upstream_map: authority/wikiversity/unit-15/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: 3c8c41458f5418ff858a58748ba4b23bc0a8cb34d9c386c155806b4482760470
public_solution_count: 4
upstream_solution_revisions: "Soal 15.6=663110; Soal 15.9=1095144; Soal 15.19=1112864; Soal 15.22=1089392"
solution_xml_sha256: "06=20af89ec50341df835441e3b0c06a80ca6ad7c015bbcd31a3c25e0567476ca7c; 09=b11c0433de7913559f0081546f223982afc420b66da100fd2c1da072ef9488ba; 19=7a9835691cd557c0cb97717e3ad86be45cb2ffd9ee20e6da501446f964b07d0b; 22=926741a153722186dfd4e1c4e99ef24f2021a8e10e242fb8224083cb0628cec5"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 15 {#br-ak-2025-2026-w15-solutions}

At the frozen revision boundary, the source provides public solutions
only for Exercises 15.6, 15.9, 15.19, and 15.22. No additional solutions
have been created for this edition.

<!-- upstream_solution: Kommutative Ringtheorie/Primideal/Restekörper als Quotientenring/Fakt/Beweis/Aufgabe/Lösung; pageid=126006; revid=663110 -->
<!-- upstream_solution_revid: 663110 -->

## Solution to Exercise 15.6 {#br-ak-2025-2026-w15-sol-06}

Consider the commutative diagram of ring homomorphisms

$$
\begin{array}{ccccc}
R&\longrightarrow&R/\mathfrak p&\longrightarrow&Q(R/\mathfrak p)\\
\downarrow&&\downarrow_{\varphi}&&\downarrow_{\psi}\\
R_{\mathfrak p}&\longrightarrow&R_{\mathfrak p}/\mathfrak pR_{\mathfrak p}
&=&R_{\mathfrak p}/\mathfrak pR_{\mathfrak p}.
\end{array}
$$

The maps $\varphi$ and $\psi$ are to be constructed. Under the ring
homomorphism

$$
R\longrightarrow R_{\mathfrak p}/\mathfrak pR_{\mathfrak p},
$$

the prime ideal $\mathfrak p$ maps to zero, giving an induced
homomorphism $\varphi$. The map $\varphi$ sends every nonzero element

$$
[r]\in R/\mathfrak p,
\qquad [r]\ne0,
$$

represented by $r\notin\mathfrak p$, to a unit. By the universal property
of localisation, $\varphi$ therefore extends to the fraction field:

$$
\psi:Q(R/\mathfrak p)
\longrightarrow R_{\mathfrak p}/\mathfrak pR_{\mathfrak p}.
$$

As a ring homomorphism between fields, $\psi$ is injective. Every element
of the residue field on the right can be represented by a fraction $r/s$
in $R_{\mathfrak p}$ with $s\notin\mathfrak p$. It is the image of

$$
\frac{[r]}{[s]}\in Q(R/\mathfrak p),
$$

since $[s]\ne0$. Thus $\psi$ is also surjective, and is an isomorphism.

[Back to Exercise 15.6](#br-ak-2025-2026-w15-ex-06).

<!-- upstream_solution: Lokaler Ring/Restklassenring/Einheiten surjektiv/Aufgabe/Lösung; pageid=95358; revid=1095144 -->
<!-- upstream_solution_revid: 1095144 -->

## Solution to Exercise 15.9 {#br-ak-2025-2026-w15-sol-09}

If $\mathfrak a=R$, the quotient is the zero ring and the statement is
clear. We therefore suppose that

$$
\mathfrak a\subseteq\mathfrak m,
$$

where $\mathfrak m$ is the unique maximal ideal of $R$.

Let $r\in R$ represent a unit in $R/\mathfrak a$, and choose $s\in R$
such that

$$
rs=1\quad\text{in }R/\mathfrak a.
$$

This means that

$$
rs-1\in\mathfrak a\subseteq\mathfrak m.
$$

If $r$ were not a unit, then $r\in\mathfrak m$ and hence
$rs\in\mathfrak m$. But this would give the contradiction

$$
1=(1-rs)+rs\in\mathfrak m.
$$

Thus $r$ itself is a unit. Every unit in $R/\mathfrak a$ therefore has a
unit preimage in $R$.

[Back to Exercise 15.9](#br-ak-2025-2026-w15-ex-09).

<!-- upstream_solution: Integre endlich erzeugte Algebren/Lokaler Isomorphismus/In Umgebung/Aufgabe/Lösung; pageid=21576; revid=1112864 -->
<!-- upstream_solution_revid: 1112864 -->

## Solution to Exercise 15.19 {#br-ak-2025-2026-w15-sol-19}

We first show that the map

$$
R_f\longrightarrow S_{\varphi(f)}
$$

is surjective for a suitable $f\in R$. Choose a set of $K$-algebra
generators $x_1,\ldots,x_n$ for $S$. By surjectivity of the local map,
there are elements

$$
y_i=\frac{r_i}{g_i}\in R_{\mathfrak m},
\qquad g_i\notin\mathfrak m,
$$

so that $y_i g_i=r_i$ in $R_{\mathfrak m}$, and with
$\varphi(y_i)=x_i$ in $S_{\mathfrak n}$. The last equality means
that for some $h_i\notin\mathfrak n$ we have

$$
h_i\bigl(\varphi(r_i)-\varphi(g_i)x_i\bigr)=0
$$

in $S$. Since $S$ is an integral domain and $h_i\ne0$, it follows that

$$
\varphi(r_i)=\varphi(g_i)x_i
$$

in $S$.

Set

$$
f=g_1\cdots g_n.
$$

Since every $g_i\notin\mathfrak m$ and $\mathfrak m$ is prime, we have
$f\notin\mathfrak m$. All the $y_i$ can be written over the common
denominator $f$, so $y_i\in R_f$. Thus every generator $x_i$ belongs to
the image of $R_f\to S_{\varphi(f)}$. The inverse denominator powers
$\varphi(f)^{-k}$ are also images of the inverse powers $f^{-k}$ in $R_f$.
The map is therefore
surjective.

**Edition note:** the source immediately deduces surjectivity from the
equalities in $S_{\mathfrak n}$ without writing out the cancellation of
$h_i$ above. That step is valid precisely because $S$ is assumed to be an
integral domain; this edition makes the dependence explicit without
changing the argument.

We now prove injectivity. Suppose $q\in R_f$ maps to zero. Its image is
then also zero in $S_{\mathfrak n}$, and $q$ comes from an element of
$R_{\mathfrak m}$. Since the local map is an isomorphism, $q=0$ in
$R_{\mathfrak m}$. Since $R$ is an integral domain, this also implies
$q=0$ in $R_f$. The map is therefore injective and, together with
surjectivity, an isomorphism.

[Back to Exercise 15.19](#br-ak-2025-2026-w15-ex-19).

<!-- upstream_solution: Endlich erzeugte integre K-Algebra/Definitionsort im K-Spektrum ist offen/Aufgabe/Lösung; pageid=21588; revid=1089392 -->
<!-- upstream_solution_revid: 1089392 -->

## Solution to Exercise 15.22 {#br-ak-2025-2026-w15-sol-22}

We show that every point $P$ with $q\in\mathcal O_P$ has an open
neighbourhood on which the same property holds at every point. The set in
the exercise is then a union of these open neighbourhoods and hence open.

The local ring at $P$ has the form

$$
\mathcal O_P=R_{\mathfrak m}
$$

for a maximal ideal $\mathfrak m$ in $R$. Membership
$q\in R_{\mathfrak m}$ means that

$$
q=\frac rf
$$

with $f\notin\mathfrak m$. Hence $P\in D(f)$, so $D(f)$ is an open
neighbourhood of $P$. For every $P'\in D(f)$, the element $f$ is again an
allowable denominator. Thus $q\in\mathcal O_{P'}$ for every $P'\in D(f)$,
as required.

[Back to Exercise 15.22](#br-ak-2025-2026-w15-ex-22).
