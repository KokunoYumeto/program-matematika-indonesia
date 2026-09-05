---
title: "Public Solutions to Worksheet 23"
stable_id: br-ak-2025-2026-w23-solutions
language: en
upstream_map: authority/wikiversity/unit-23/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: fdfec83fe1ef4f0d87eca194f2991805cd69ff2af070b73ef83c0ba1c9d1e4c4
authority_manifest: authority/wikiversity/unit-23/UNIT_AUTHORITY_MANIFEST.json
authority_manifest_sha256: f7ee49a4bfa589b831c1fdb69e6f091ac1762d9da019a133670e4e0d723d34ae
public_solution_count: 2
upstream_solution_revisions: "Exercise 23.4=1090216; Exercise 23.5=1096444"
solution_xml_sha256: "04=56b03cddd25d14146c8934076599108a3cbf927f6696e7aaed9612b3fed40bea; 05=549cbd738a19c67071ca964c1bfa55e472c8ae592b01e8ce88b2a62114924300"
license: "CC BY-SA 4.0"
translation_status: complete
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_corrections: 2
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 23 {#br-ak-2025-2026-w23-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 23.4 and 23.5. No additional solutions have been created for
this edition.

<!-- upstream_solution: Polynomring/2/Multiplizität/Multiplikation/Aufgabe/Lösung; pageid=95515; revid=1090216 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1090216 -->

## Solution to Exercise 23.4 {#br-ak-2025-2026-w23-sol-04}

Write $S=K[X,Y]$. Since the lowest homogeneous term of $F$ has degree $m$,
we have $F\in\mathfrak m^m$. To prove well-definedness, let
$G\in\mathfrak m^{n-m}$. Then

$$
FG\in\mathfrak m^m\mathfrak m^{n-m}=\mathfrak m^n.
$$

Thus the $S$-module map

$$
S\xrightarrow{\,\cdot F\,}S
\longrightarrow S/\mathfrak m^n
$$

vanishes on $\mathfrak m^{n-m}$. By the universal property of quotient
modules, it induces an $S$-module homomorphism

$$
S/\mathfrak m^{n-m}
\xrightarrow{\,\cdot F\,}
S/\mathfrak m^n.
$$

To prove injectivity, suppose that the class of $G$ maps to zero, so that
$FG\in\mathfrak m^n$. Assume $G\notin\mathfrak m^{n-m}$. If $q$ is the
degree of the lowest nonzero homogeneous term $G_q$ of $G$, then

$$
q<n-m.
$$

The lowest homogeneous term of $FG$ is $F_mG_q$. Since $K[X,Y]$ is an
integral domain and $F_m,G_q\ne0$, we have

$$
F_mG_q\ne0,
\qquad
\deg(F_mG_q)=m+q<n.
$$

Hence $FG\notin\mathfrak m^n$, a contradiction. Thus
$G\in\mathfrak m^{n-m}$ and its class is zero. The induced homomorphism is
injective. $\square$

*Edition note -- correction to the source solution:* The source says that
$FG$ has a monomial of degree “less than $m$”; the required bound is less
than $n$. The argument using the lowest homogeneous term $F_mG_q$ above
also rules out cancellation. Since multiplication by $F$ is generally not
a ring homomorphism, the factorisation uses the universal property of
quotient *modules*.

[Back to Exercise 23.4](#br-ak-2025-2026-w23-ex-04)

<!-- upstream_solution: Numerisches Monoid/N ab e/Hilbert-Funktion/Aufgabe/Lösung; pageid=95541; revid=1096444 -->
<!-- upstream_solution_url: https://de.wikiversity.org/w/index.php?oldid=1096444 -->

## Solution to Exercise 23.5 {#br-ak-2025-2026-w23-sol-05}

1. We claim that

   $$
   nM_+=\mathbb N_{\ge ne}.
   $$

   Membership $k\in nM_+$ means that there are
   $m_1,\ldots,m_n\in M_+=\mathbb N_{\ge e}$ with

   $$
   k=m_1+\cdots+m_n.
   $$

   Since $m_j\ge e$ for every $j$, we obtain $k\ge ne$. Conversely, if
   $k\ge ne$, then

   $$
   k=(n-1)e+m,
   \qquad m:=k-(n-1)e\ge e.
   $$

   The right-hand side is a sum of $n$ elements of $M_+$, so $k\in nM_+$.

2. We obtain

   $$
   M\setminus nM_+
   =M\setminus\mathbb N_{\ge ne}
   =\{0,e,e+1,\ldots,ne-1\}.
   $$

   Therefore

   $$
   \#(M\setminus nM_+)=ne-e+1=(n-1)e+1.
   $$

3. The ideal $\mathfrak m^n$ is the monomial ideal $K[nM_+]$. Localisation
   does not change this finite-dimensional quotient, and there are
   isomorphisms of $K$-vector spaces

   $$
   \begin{aligned}
   R/\mathfrak m^n
   &\cong K[M]/K[nM_+]\\
   &\cong
   \operatorname{span}_K
   \{T^m\mid m\in M\setminus nM_+\}.
   \end{aligned}
   $$

   Hence

   $$
   \dim_K(R/\mathfrak m^n)=(n-1)e+1.
   $$

*Edition note -- correction to the source solution:* In the first part,
the source writes $n_j\ge e$ after introducing $m_1,\ldots,m_n$; the correct
notation is $m_j\ge e$. In the third part, the source notation identifies
the quotient with $K[M\setminus nM_+]$, as though the complement defined a
monoid ring. The edition states the correct objects: the quotient by the
monomial ideal $K[nM_+]$ and the vector space with monomial basis indexed
by its complement.

[Back to Exercise 23.5](#br-ak-2025-2026-w23-ex-05)
