---
title: "Integrative Problem 10 — Euler Characteristic and a Thickened Point"
stable_id: d100-bridge-integrative-10
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_credit: "Theoretical foundations: Holger Brenner, Bündel, Garben und Kohomologie, Lectures 26–27; frozen-revision contributions retain the credits in the source reader."
non_endorsement: "Independent AI-generated material; not human-authored or human-reviewed, and no endorsement by the source author or institution is implied."
---

# Integrative problem 10: Euler characteristic and a thickened point {#d100-bridge-integrative-10}

The following problem and solution were independently written; they are
not a source problem or solution by Holger Brenner. The foundations used
are [Theorem 26.10](bgk-reader.html#br-bgk-2019-l26-thm-01),
[Theorem 27.4](bgk-reader.html#br-bgk-2019-l27-thm-02),
[Definition 27.8](bgk-reader.html#br-bgk-2019-l27-def-01), and
[Lemma 27.9](bgk-reader.html#br-bgk-2019-l27-lem-01) in the BGK
translation. The source statement of
[additivity](https://de.wikiversity.org/w/index.php?oldid=1088413)
applies to short exact sequences of coherent sheaves on a projective
scheme over a field.

## Problem {#d100-bridge-integrative-10-soal}

Let $K$ be any field, $X=\mathbb P_K^1$ with coordinates $[X_0:X_1]$,
$m\geq1$, and $n\in\mathbb Z$. Write $P=[1:0]$ and

$$
Z=\operatorname{Proj}\bigl(K[X_0,X_1]/(X_1^m)\bigr),
\qquad i:Z\hookrightarrow X.
$$

The notation $\mathcal O_Z(n)$ means $i^*\mathcal O_X(n)$.

1. Prove that multiplication by $X_1^m$ gives a short exact sequence
   $0\to\mathcal O_X(n-m)\to\mathcal O_X(n)\to
   i_*\mathcal O_Z(n)\to0$. Determine the ring of $Z$ on the chart
   containing it.
2. Compute $h^0$ and $h^1$ of all three sheaves, and their Euler
   characteristics. Explain why all higher cohomology vanishes.
3. For the cover $U_0=D_+(X_0)$ and $U_1=D_+(X_1)$, determine the
   connecting homomorphism
   $\delta:H^0(Z,\mathcal O_Z(n))\to H^1(X,\mathcal O_X(n-m))$.
   Determine when restriction of global sections to $Z$ is surjective.
4. Work out the case $m=3$, $n=0$ explicitly. Explain why the length
   of $Z$, rather than its number of topological points, occurs in the
   Euler formula.

## Solution {#d100-bridge-integrative-10-penyelesaian}

### 1. Exactness on two charts {#d100-bridge-integrative-10-jawab-01}

On $U_0$ use $t=X_1/X_0$; on $U_1$ use $s=X_0/X_1=t^{-1}$.
Write the local frames of $\mathcal O_X(r)$ as $e_0^{(r)}=X_0^r$ and
$e_1^{(r)}=X_1^r$ for every $r\in\mathbb Z$. For $r<0$, this notation
denotes a frame of an invertible sheaf, not a global polynomial. On the
overlap, $e_1^{(r)}=t^r e_0^{(r)}$.

In these frames, multiplication by $X_1^m$ is given by

$$
K[t]\xrightarrow{\ t^m\ }K[t]\quad\text{on }U_0,
\qquad
K[s]\xrightarrow{\ 1\ }K[s]\quad\text{on }U_1.
$$

The first map is injective because $K[t]$ is an integral domain; the
second is an isomorphism. Their quotients are $K[t]/(t^m)$ and $0$,
respectively. They are compatible on the overlap, since $t$ is a unit
there. Thus the required sheaf sequence is exact. All its sheaves are
coherent: the first two are locally free of rank one, while the quotient
has a finite presentation on these Noetherian charts.

The scheme $Z$ lies entirely in $U_0$, and

$$
Z=\operatorname{Spec}(K[t]/(t^m)).
$$

Its only prime ideal is $(t)$, so its topological space has only the
point $P$. However, $1,t,\ldots,t^{m-1}$ form a basis of its ring as
a vector space over $K$.

### 2. Cohomology and Euler characteristic {#d100-bridge-integrative-10-jawab-02}

Theorem 26.10 applies because $X$ is projective over $K$ and the sheaves
above are quasicoherent. In the frame $e_0^{(r)}$, the Čech complex for
$\mathcal O_X(r)$ has differential

$$
K[t]\oplus K[t^{-1}]
\longrightarrow K[t,t^{-1}],
\qquad
(a,b)\longmapsto t^r b-a.
$$

This uses the sign convention $s_1-s_0$. There are no terms of degree
two or higher. The kernel identifies with $K[t]\cap t^rK[t^{-1}]$,
while the cokernel is

$$
K[t,t^{-1}]\big/\bigl(K[t]+t^rK[t^{-1}]\bigr).
$$

For the kernel, the available monomials are exactly $t^j$ with
$0\leq j\leq r$. For the cokernel, the surviving monomials are exactly
$t^j$ with $r<j<0$. Linear independence of Laurent monomials gives

$$
h^0(\mathcal O_X(r))=\max(r+1,0),
\qquad
h^1(\mathcal O_X(r))=\max(-r-1,0),
\qquad
H^q(\mathcal O_X(r))=0\quad(q\geq2).
$$

This calculation is also the case $d=1$ of Theorem 27.4. Hence
$\chi(\mathcal O_X(r))=r+1$ for every integer $r$, including $r<0$.

The frame $e_0^{(n)}$ trivialises $\mathcal O_Z(n)$. The Čech complex
for $i_*\mathcal O_Z(n)$ has only the term $K[t]/(t^m)$ in degree zero:
its values on $U_1$ and on the overlap are zero. Therefore

$$
h^0(i_*\mathcal O_Z(n))=m,\qquad
H^q(X,i_*\mathcal O_Z(n))=0\quad(q>0),
\qquad
\chi(i_*\mathcal O_Z(n))=m.
$$

On $Z$ itself the result is the same: its topological space has one
point, so the global section functor equals the stalk functor at that
point and is exact. Its positive cohomology therefore vanishes. The
additivity formula now becomes the identity

$$
\underbrace{n+1}_{\chi(\mathcal O_X(n))}
=
\underbrace{n-m+1}_{\chi(\mathcal O_X(n-m))}
+\underbrace{m}_{\chi(i_*\mathcal O_Z(n))}.
$$

Why does additivity follow from exactness? The cohomology sequence ends as

$$
0\to H^0(\mathcal O_X(n-m))\to H^0(\mathcal O_X(n))
\to H^0(\mathcal O_Z(n))
\xrightarrow{\delta}H^1(\mathcal O_X(n-m))
\to H^1(\mathcal O_X(n))\to0.
$$

In a finite exact sequence of finite-dimensional vector spaces, the
dimension of each term is the sum of the dimensions of the incoming
and outgoing images. The alternating sum cancels every image dimension
twice with opposite signs. The result is exactly the Euler formula
above, not additivity of $h^0$ alone.

### 3. The connecting homomorphism {#d100-bridge-integrative-10-jawab-03}

Represent a section on $Z$ uniquely by
$q(t)=\sum_{r=0}^{m-1}c_rt^r$. Lift it to $q(t)e_0^{(n)}$ on $U_0$
and to $0$ on $U_1$. The Čech difference of the two lifts is
$-q(t)e_0^{(n)}$. Dividing by the multiplier $t^m$ gives

$$
\delta([q])=[-t^{-m}q(t)]
\quad\text{in}\quad
\frac{K[t,t^{-1}]}
{K[t]+t^{\,n-m}K[t^{-1}]}.
$$

Changing the lifts changes this representative by a coboundary. In
particular, replacing $q$ by $q+t^ma$ adds $-a\in K[t]$, so its class
does not change.

The class $\delta([t^r])$ is nonzero exactly when $n-m<r-m<0$, that
is, $r>n$ for $0\leq r<m$. These nonzero classes are linearly
independent. Consequently

$$
\dim\ker\delta=\min\bigl(m,\max(n+1,0)\bigr),
\qquad
\dim\operatorname{im}\delta
=m-\min\bigl(m,\max(n+1,0)\bigr).
$$

This is also visible directly: for $n\geq0$, global sections of
$\mathcal O_X(n)$ are polynomials in $t$ of degree at most $n$, and
restriction to $Z$ takes their classes modulo $t^m$. For $n<0$ there
are no nonzero global sections. Restriction is surjective exactly when
$n\geq m-1$.

### 4. One point of length three {#d100-bridge-integrative-10-jawab-04}

For $m=3$ and $n=0$, the global sequence is

$$
0\longrightarrow K
\xrightarrow{\,a\mapsto(a,0,0)\,}K^3
\xrightarrow{\ (a,b,c)\mapsto(-b,-c)\ }K^2
\longrightarrow0,
$$

with basis $1,t,t^2$ of $K[t]/(t^3)$ and basis $[t^{-2}],[t^{-1}]$
of $H^1(\mathcal O_X(-3))$. Thus $t$ and $t^2$ are sections on $Z$
that cannot extend to global functions on $X$. The Euler formula gives

$$
1=(-2)+3.
$$

The filtration
$K[t]/(t^3)\supset(t)/(t^3)\supset(t^2)/(t^3)\supset0$ has three
successive quotients isomorphic to $K$; its length is three. In general,
the filtration by powers of $t$ has $m$ such quotients. Euler
characteristic records the dimension of sections and therefore counts
this length $m$, not merely the single point of the topological space.

## Checks and material provenance {#d100-bridge-integrative-10-periksa}

Surjectivity of sheaves is checked locally; surjectivity on global
sections is measured by $\delta$ and must not be inferred automatically.
No assumption that $K$ is algebraically closed is needed, since $P$ is
an explicitly specified rational point.

Holger Brenner's BGK Lectures 26 and 27 use the frozen parent revisions
[793619](https://de.wikiversity.org/w/index.php?oldid=793619) and
[1070036](https://de.wikiversity.org/w/index.php?oldid=1070036).
The revision of the cohomology formula entity used is
[1102393](https://de.wikiversity.org/w/index.php?oldid=1102393);
other transclusion identities remain those in the edition's frozen
manifest. This independent problem, bridge exposition, and solution:
CC BY-SA 4.0. Model provenance: OpenAI Codex gpt-5.6-sol, Ultra.
The credits and licences of source components remain in force; no human
authorship or review, or endorsement by the source author, is claimed.
