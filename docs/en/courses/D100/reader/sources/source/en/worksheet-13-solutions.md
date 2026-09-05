---
title: "Public Solutions to Worksheet 13"
stable_id: br-ak-2025-2026-w13-solutions
language: en
upstream_map: authority/wikiversity/unit-13/ORDERED_EXERCISE_MAP.json
upstream_map_sha256: f954f09c996c8aa22f94ec826a1503b135a7b4fb9f9e0d5d6ff21f36a519e52a
public_solution_count: 14
upstream_solution_revisions: "Soal 13.3=1023890; 13.6=663088; 13.8=1112836; 13.9=1060069; 13.11=1023327; 13.14=1089391; 13.15=1029221; 13.17=1113410; 13.20=1095814; 13.21=1096486; 13.24=1060010; 13.27=1094892; 13.28=1089663; 13.31=1065090"
solution_xml_sha256: "03=71a4c039de6111f019e2580e0c9af5382450aee092e9e50f34e90368089b1f89; 06=f07fb1df932f9dadf9849fb8a656783d820cb343e5580bd003382cef9788ccac; 08=a2b47f3a63b65b38ae83c5d806aa60fb32a48e8e1d3f083e4f8896e42e61461d; 09=b8ff1918b646eff1d77c8a29cb6b97b6478294e35e0459dc952d3d49a8f7ea6e; 11=752330f95561989915091de492b4cda2fc75710d6b4ee121cef24d62771037a6; 14=d51c295e8174e7ce572b632aee9af39582111d2aa826878d71e420da65da33b0; 15=6e2790855ccbb62268be031dcfbe059c36b0cf4a13a5ad5e129de073975b06ed; 17=59ade099fbf3e862db3d7d0793152278471f697a80a04150e162768452d56e8d; 20=16e9149ead068dc694c59b8ceda85e798cdb480d013ec52bde116005a8581836; 21=34216c74192341aa62c099d3818cd5083057a4a407223dcee4157f894d352639; 24=a369cb91ccbce5c9c5854d7305b2fc8928e73fbfaafd6b5b0dc9f03b970c0c91; 27=f90da5c3fc81eb9c2eebd43131a6d432986c3bb1e0cd363dac6100343b7b3525; 28=7b2e1d5c6d658b72921d28bafef2757bc90683beefcc60091a8028dce3ccbfbd; 31=c1823799d3e16c30f8c13c9ae3ae79ac0ff88c0d89d223d751f1b6c8900bd30d"
license: "CC BY-SA 4.0"
translation_status: complete
---

```{=latex}
\clearpage
```

# Public Solutions to Worksheet 13 {#br-ak-2025-2026-w13-solutions}

At the frozen revision boundary, the source provides public solutions only
to Exercises 13.3, 13.6, 13.8, 13.9, 13.11, 13.14, 13.15, 13.17, 13.20,
13.21, 13.24, 13.27, 13.28, and 13.31. No additional solutions have been
created for this edition.

<!-- upstream_solution: Rationale Zahlen/Unterringe/Überabzählbar/Aufgabe/Lösung; pageid=86264; revid=1023890 -->
<!-- upstream_solution_revid: 1023890 -->

## Solution to Exercise 13.3 {#br-ak-2025-2026-w13-sol-03}

Let $T$ be a subset of the set of prime numbers. Since there are
infinitely many prime numbers, there are uncountably many choices of
$T$. Associate with $T$ the multiplicative system $M(T)$ consisting of
all integers whose prime factorisations contain only primes from $T$.
The localisation

$$
\mathbb Z_{M(T)}\subseteq\mathbb Q
$$

consists of all rational numbers that can be written with a denominator
whose prime factorisation uses only primes from $T$. Uniqueness of prime
factorisation in $\mathbb Z$ shows that these subrings are distinct for
distinct choices of $T$.

[Back to Exercise 13.3](#br-ak-2025-2026-w13-ex-03).

<!-- upstream_solution: Nenneraufnahme/Universelle Eigenschaft/Fakt/Beweis/Aufgabe/Lösung; pageid=126003; revid=663088 -->
<!-- upstream_solution_revid: 663088 -->

## Solution to Exercise 13.6 {#br-ak-2025-2026-w13-sol-06}

For the diagram of ring homomorphisms to commute, we must have

$$
\widetilde\varphi(1/s)=\varphi(s)^{-1}
$$

for $s\in S$, and hence

$$
\widetilde\varphi(a/s)=\varphi(a)\varphi(s)^{-1}.
$$

Thus there is at most one such ring homomorphism, and it must be given
by the last formula.

We need to show that this formula is well-defined. Let $a/s=b/t$ with
$s,t\in S$. This means that there is an $r\in S$ such that $rta=rsb$.
Then

$$
\varphi(r)\varphi(t)\varphi(a)
=\varphi(r)\varphi(s)\varphi(b).
$$

Multiplying both sides by the unit
$\varphi(r)^{-1}\varphi(t)^{-1}\varphi(s)^{-1}$ gives

$$
\varphi(a)\varphi(s)^{-1}
=\varphi(b)\varphi(t)^{-1}.
$$

As an example of verifying the homomorphism properties, for addition we obtain

$$
\begin{aligned}
\widetilde\varphi\!\left(\frac as+\frac bt\right)
&=\widetilde\varphi\!\left(\frac{at+bs}{st}\right)\\
&=\varphi(at+bs)\varphi(st)^{-1}\\
&=(\varphi(a)\varphi(t)+\varphi(s)\varphi(b))
  \varphi(s)^{-1}\varphi(t)^{-1}\\
&=\varphi(a)\varphi(s)^{-1}+\varphi(b)\varphi(t)^{-1}\\
&=\widetilde\varphi\!\left(\frac as\right)
 +\widetilde\varphi\!\left(\frac bt\right).
\end{aligned}
$$

[Back to Exercise 13.6](#br-ak-2025-2026-w13-ex-06).

<!-- upstream_solution: Polynomring zwei Variablen/Multiplikatives System/Eine Gleichung/Verträglichkeit/Aufgabe/Lösung; pageid=21362; revid=1112836 -->
<!-- upstream_solution_revid: 1112836 -->

## Solution to Exercise 13.8 {#br-ak-2025-2026-w13-sol-08}

All homomorphisms below are $R$-algebra homomorphisms and are uniquely
determined by the stated properties. The homomorphism $R\to R_S$
first induces

$$
R/(F)\longrightarrow R_S/(F).
$$

Since the image of $S$ in $R/(F)$ becomes units in $R_S/(F)$, the
universal property of localisation gives a homomorphism

$$
(R/(F))_S\longrightarrow R_S/(F),
\qquad
\frac{\bar r}{\bar s}\longmapsto\overline{\left(\frac rs\right)}.
$$

This map is surjective: every element on the right is represented by
$r/s$ with $s\in S$ and comes from $\bar r/\bar s$.

For injectivity, suppose that $\bar r/\bar s$ maps to $0$. Then
$r/s\in(F)R_S$, so $r/s=Fa/t$ for some $a\in R$ and $t\in S$.
Translating this equality back into $R$ gives

$$
tr=sFa.
$$

Thus $tr=0$ in $R/(F)$. Since $t\in S$, this gives $\bar r/\bar s=0$
in $(R/(F))_S$.

> **Edition note:** The source's cancellation in $R=K[X,Y]$ assumes
> $0\notin S$. If $0\in S$, both localised rings are zero and the
> asserted isomorphism is immediate; the displayed cross-multiplication
> argument is used only in the other case.

[Back to Exercise 13.8](#br-ak-2025-2026-w13-ex-08).

<!-- upstream_solution: Nenneraufnahme/Restklassenbildung/Vertauschbarkeit/Fakt/Beweis/Aufgabe/Lösung; pageid=167737; revid=1060069 -->
<!-- upstream_solution_revid: 1060069 -->

## Solution to Exercise 13.9 {#br-ak-2025-2026-w13-sol-09}

The ring homomorphism

$$
R\longrightarrow R_S/\mathfrak aR_S
$$

sends $\mathfrak a$ to $0$ and therefore induces a homomorphism

$$
R/\mathfrak a\longrightarrow R_S/\mathfrak aR_S.
$$

The universal property of localisation then induces

$$
(R/\mathfrak a)_S\longrightarrow R_S/\mathfrak aR_S,
\qquad
\frac{[r]}s\longmapsto\left[\frac rs\right].
$$

This formula immediately shows surjectivity. If the image $[r/s]$ is zero,
then $r/s\in\mathfrak aR_S$, and hence $r\in\mathfrak aR_S$. Thus there is
a $t\in S$ with $tr\in\mathfrak a$. Hence $[tr]=0$ in
$R/\mathfrak a$, and consequently $[r]/s=0$ in $(R/\mathfrak a)_S$.
The map is therefore also injective.

> **Edition note:** The source writes $[r/s]\in\mathfrak aR_S$ in the
> kernel argument. The ideal-membership statement concerns the
> representative $r/s$ in $R_S$, as made explicit above.

[Back to Exercise 13.9](#br-ak-2025-2026-w13-ex-09).

<!-- upstream_solution: Hilbertscher Nullstellensatz/Äquivalent/D(f) in D(g)/R g nach R f/Aufgabe/Lösung; pageid=21347; revid=1023327 -->
<!-- upstream_solution_revid: 1023327 -->

## Solution to Exercise 13.11 {#br-ak-2025-2026-w13-sol-11}

If (2) holds, we can in particular write

$$
\frac1g=\frac r{f^n},
\qquad\text{or equivalently}\qquad
f^n=rg.
$$

Thus $g$ divides a power of $f$, that is, $f\in\operatorname{rad}(g)$.
Conversely, if $f\in\operatorname{rad}(g)$, then $g$ is a unit in
$R_f$, and the universal property of localisation gives an $R$-algebra
homomorphism $R_g\to R_f$.

From $f\in\operatorname{rad}(g)$ it follows immediately that $f$
vanishes on $V(g)$, so $V(g)\subseteq V(f)$. If $K$ is algebraically
closed, the reverse implication follows from Hilbert's Nullstellensatz.
Since $D(f)\subseteq D(g)$ is equivalent to $V(g)\subseteq V(f)$, the
two statements in the exercise are equivalent.

> **Edition note:** The source's fraction argument applies directly when
> $f,g\ne0$. If $f=0$, both conditions hold because $D(0)=\varnothing$
> and $R_0$ is the zero ring. If $f\ne0$ and $g=0$, neither holds:
> $D(f)\ne\varnothing$ by the Nullstellensatz, and there is no unital
> homomorphism from the zero ring to the nonzero ring $R_f$.

For $K=\mathbb R$, take $R=K[X]$, $f=1$, and $g=X^2+1$. The polynomial
$g$ has no real zero, so

$$
V(g)=\varnothing=V(1)
$$

and $D(f)\subseteq D(g)$, but $g$ is not a unit in $R_f=R$.

**Edition note:** In the last example, the source displays
$V(g)=\mathbb A_{\mathbb R}^1=V(1)$. Both zero loci in question are
empty; the relation between the open sets remains as stated above.

[Back to Exercise 13.11](#br-ak-2025-2026-w13-ex-11).

<!-- upstream_solution: Endlich erzeugte integre K-Algebra/C/Nenneraufnahme/Kein maximales Ideal überlebt/Aufgabe/Lösung; pageid=21586; revid=1089391 -->
<!-- upstream_solution_revid: 1089391 -->

## Solution to Exercise 13.14 {#br-ak-2025-2026-w13-sol-14}

Take

$$
R=\mathbb C[X,Y]
$$

and let $S$ be the multiplicative system consisting of all products of
elements of the form $X-a$, $a\in\mathbb C$. The maximal ideals of $R$
have the form

$$
(X-a,Y-b).
$$

Thus every maximal ideal contains an element of $S$ and becomes the
unit ideal in $R_S$. However, $R_S$ is not a field: precisely the prime
elements $X-a$ are made into units, whereas other prime elements, such
as $Y$, are not.

[Back to Exercise 13.14](#br-ak-2025-2026-w13-ex-14).

<!-- upstream_solution: Integritätsbereich/Zusammenhängend/Aufgabe/Lösung; pageid=126687; revid=1029221 -->
<!-- upstream_solution_revid: 1029221 -->

## Solution to Exercise 13.15 {#br-ak-2025-2026-w13-sol-15}

An idempotent element $e$ satisfies

$$
e(1-e)=e-e^2=e-e=0.
$$

In a ring without zero divisors, this implies $e=1$ or $e=0$.

[Back to Exercise 13.15](#br-ak-2025-2026-w13-ex-15).

<!-- upstream_solution: Kommutativer Ring/nx und x^n ist 0/Aufgabe/Lösung; pageid=73634; revid=1113410 -->
<!-- upstream_solution_revid: 1113410 -->

## Solution to Exercise 13.17 {#br-ak-2025-2026-w13-sol-17}

Consider the residue class ring

$$
R=(\mathbb Z/n\mathbb Z)[X]/(X^n)
$$

and write $x$ for the residue class of $X$. The element $x$ is nonzero:
in the polynomial ring, $X$ cannot be a multiple of $X^n$ when $n\ge2$
for degree reasons. In $R$ we have $n=0$, so $ny=0$ for every $y\in R$,
in particular $nx=0$. Moreover, $x^n=0$ because the entire ideal $(X^n)$
is made zero when forming the quotient ring.

[Back to Exercise 13.17](#br-ak-2025-2026-w13-ex-17).

<!-- upstream_solution: Z/Restklassenring nach Primelementpotenz/Ist zusammenhängend/Aufgabe/Lösung; pageid=73535; revid=1095814 -->
<!-- upstream_solution_revid: 1095814 -->

## Solution to Exercise 13.20 {#br-ak-2025-2026-w13-sol-20}

Let $e\in\mathbb Z/(p^n)$ be idempotent. Choosing an integer
representative, the equation $e^2=e$ means that

$$
p^n\mid e(e-1).
$$

The integers $e$ and $e-1$ are coprime, so they cannot both be divisible
by $p$. Since $p^n$ divides their product, the whole factor $p^n$ must
divide either $e$ or $e-1$. Thus

$$
e=0\quad\text{or}\quad e=1
$$

in $\mathbb Z/(p^n)$.

**Edition note:** The source writes factorisations $e=bp^i$ and
$e-1=cp^j$ with $i+j=n$. These exponents may be chosen as divisibility
exponents; they need not be the exact $p$-adic valuations. The coprimality
argument above expresses the same step directly. For $n=0$, the conclusion
still holds, but $0=1$; see the note to Exercise 13.20.

[Back to Exercise 13.20](#br-ak-2025-2026-w13-ex-20).

<!-- upstream_solution: Polynom/Q X modulo X^4-1/Produkt von Körpern/Restklasse von X^3+X/Aufgabe/Lösung; pageid=25988; revid=1096486 -->
<!-- upstream_solution_revid: 1096486 -->

## Solution to Exercise 13.21 {#br-ak-2025-2026-w13-sol-21}

We have

$$
X^4-1=(X^2-1)(X^2+1)=(X+1)(X-1)(X^2+1).
$$

The polynomial $X^2+1\in\mathbb Q[X]$ is irreducible because it has
no rational root. Thus this is the prime factorisation, and the monic
factors above are pairwise nonassociate. The Chinese remainder theorem
for principal ideal domains gives

$$
\begin{aligned}
\mathbb Q[X]/(X^4-1)
&\cong \mathbb Q[X]/(X+1)
\times\mathbb Q[X]/(X-1)
\times\mathbb Q[X]/(X^2+1)\\
&\cong\mathbb Q\times\mathbb Q\times\mathbb Q[\mathrm i].
\end{aligned}
$$

The last isomorphism uses the substitutions $X\mapsto-1$, $X\mapsto1$,
and $\mathbb Q[X]/(X^2+1)\cong\mathbb Q[\mathrm i]$. The element
$X^3+X=X(X^2+1)$ maps under the three projections to $-2$, $2$, and $0$.
Its tuple is therefore

$$
(-2,2,0).
$$

[Back to Exercise 13.21](#br-ak-2025-2026-w13-ex-21).

<!-- upstream_solution: K-Algebren/K-Spektren/Disjunkte Realisierung/Aufgabe/Lösung; pageid=167734; revid=1060010 -->
<!-- upstream_solution_revid: 1060010 -->

## Solution to Exercise 13.24 {#br-ak-2025-2026-w13-sol-24}

Without loss of generality, suppose $m\ge n$. We can write

$$
B\cong
K[X_1,\ldots,X_n]/\mathfrak b
\cong
K[X_1,\ldots,X_m]/
\bigl(\mathfrak b+(X_{n+1},\ldots,X_m)\bigr).
$$

Denote this extended ideal by $\mathfrak b'$. The two $K$-spectra have
thus been realised as closed subsets of the same affine space. Use one
additional variable $Z$ to separate them, and consider

$$
C=
K[X_1,\ldots,X_m,Z]/
\bigl(Z(Z-1),\,Z\mathfrak a,\,(Z-1)\mathfrak b'\bigr).
$$

The $K$-spectrum of $C$ is the disjoint union of the two given spectra.
Indeed, the set

$$
V=V\bigl(Z(Z-1),\,Z\mathfrak a,\,(Z-1)\mathfrak b'\bigr)
\subseteq\mathbb A_K^{m+1}
$$

satisfies $Z=0$ or $Z=1$. The part with $Z=0$ is

$$
\begin{aligned}
V_0
&=V\bigl(Z,Z(Z-1),Z\mathfrak a,(Z-1)\mathfrak b'\bigr)\\
&=V\bigl(Z,-\mathfrak b'\bigr)\\
&\cong
K\!-\!\operatorname{Spek}
\left(K[X_1,\ldots,X_m,Z]/(Z,\mathfrak b')\right)\\
&\cong K\!-\!\operatorname{Spek}
\left(K[X_1,\ldots,X_n]/\mathfrak b\right)\\
&=K\!-\!\operatorname{Spek}(B),
\end{aligned}
$$

whereas the part with $Z=1$ is

$$
\begin{aligned}
V_1
&=V\bigl(Z-1,Z(Z-1),Z\mathfrak a,(Z-1)\mathfrak b'\bigr)\\
&=V\bigl(Z-1,Z\mathfrak a\bigr)\\
&\cong
K\!-\!\operatorname{Spek}
\left(K[X_1,\ldots,X_m,Z]/(Z-1,\mathfrak a)\right)\\
&\cong K\!-\!\operatorname{Spek}
\left(K[X_1,\ldots,X_m]/\mathfrak a\right)\\
&=K\!-\!\operatorname{Spek}(A).
\end{aligned}
$$

[Back to Exercise 13.24](#br-ak-2025-2026-w13-ex-24).

<!-- upstream_solution: Idempotente Elemente/Reduktion/Injektiv/Aufgabe/Lösung; pageid=94590; revid=1094892 -->
<!-- upstream_solution_revid: 1094892 -->

## Solution to Exercise 13.27 {#br-ak-2025-2026-w13-sol-27}

Let $e,f\in R$ be idempotent and suppose their images in the reduction
are equal. Then $e-f$ is nilpotent in $R$. Thus there is an
$n\in\mathbb N$ with

$$
(e-f)^n=0.
$$

We may take $n$ to be odd. By the binomial theorem, symmetry of binomial
coefficients, and idempotence, we obtain

$$
\begin{aligned}
0=(e-f)^n
&=\sum_{k=0}^{n}(-1)^{n-k}\binom nk e^kf^{n-k}\\
&=e^n-f^n+
\sum_{k=1}^{n-1}(-1)^{n-k}\binom nk e^kf^{n-k}\\
&=e-f+
\sum_{k=1}^{n-1}(-1)^{n-k}\binom nk e^kf^{n-k}\\
&=e-f+
\sum_{k=1}^{(n-1)/2}(-1)^{n-k}\binom nk
\left(e^kf^{n-k}-e^{n-k}f^k\right)\\
&=e-f+
\sum_{k=1}^{(n-1)/2}(-1)^{n-k}\binom nk(ef-ef)\\
&=e-f.
\end{aligned}
$$

Hence $e=f$.

> **Edition note:** The source omits the alternating signs in its binomial
> sums. The factors $(-1)^{n-k}$ above correct that omission. Since $n$
> is odd, the terms with indices $k$ and $n-k$ have opposite signs,
> which justifies the displayed pairing and cancellation.

[Back to Exercise 13.27](#br-ak-2025-2026-w13-ex-27).

<!-- upstream_solution: Idempotente Elemente/Modulo nilpotentes Element/Surjektiv/Aufgabe/Lösung; pageid=94592; revid=1089663 -->
<!-- upstream_solution_revid: 1089663 -->

## Solution to Exercise 13.28 {#br-ak-2025-2026-w13-sol-28}

Take a preimage $f\in R$ of $e$. Since $e$ is idempotent, the element

$$
c=f^2-f
$$

lies in $(n)$, so $c^2=0$. Consider

$$
g=f+c-2cf.
$$

This element also maps to $e$. Moreover,

$$
\begin{aligned}
g^2
&=(f+c-2cf)^2\\
&=f^2+c^2+4c^2f^2+2cf-4cf^2-4c^2f\\
&=f^2+2cf-4cf^2\\
&=f+c+2cf-4c(f+c)\\
&=f+c+2cf-4cf\\
&=f+c-2cf\\
&=g.
\end{aligned}
$$

Thus $g$ is an idempotent preimage of $e$.

[Back to Exercise 13.28](#br-ak-2025-2026-w13-ex-28).

<!-- upstream_solution: Kommutativer Ring/Ideal/Teilerfremd/Chinesischer Restsatz/Fakt/Beweis/Aufgabe/Lösung; pageid=168189; revid=1065090 -->
<!-- upstream_solution_revid: 1065090 -->

## Solution to Exercise 13.31 {#br-ak-2025-2026-w13-sol-31}

The general case follows from the case $n=2$, so it suffices to consider
two ideals $\mathfrak a$ and $\mathfrak b$. The natural map

$$
R\longrightarrow R/\mathfrak a\times R/\mathfrak b
$$

has kernel $\mathfrak a\cap\mathfrak b$. For comaximal ideals this
intersection equals the product $\mathfrak a\mathfrak b$. We therefore
obtain an injective ring homomorphism

$$
R/(\mathfrak a\mathfrak b)
\longrightarrow R/\mathfrak a\times R/\mathfrak b.
$$

To prove surjectivity, take $(r,s)$ on the right. Choose
$a\in\mathfrak a$ and $b\in\mathfrak b$ with $a+b=1$. The element

$$
r-ar+s-sb
$$

is a preimage of $(r,s)$. Modulo $\mathfrak a$, it becomes

$$
r-ar+s-sb=r+s-s(1-a)=r+s-s=r,
$$

and similarly modulo $\mathfrak b$ it becomes $s$.

[Back to Exercise 13.31](#br-ak-2025-2026-w13-ex-31).
