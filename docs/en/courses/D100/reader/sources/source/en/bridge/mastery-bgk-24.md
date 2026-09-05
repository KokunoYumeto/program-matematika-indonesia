---
title: "BGK 24 Mastery Exercises - Hom and Ext"
stable_id: d100-bridge-mastery-bgk-24
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_worksheet_revision: 991890
source_authority_manifest: authority/wikiversity-bgk/unit-24/UNIT_AUTHORITY_MANIFEST.json
source_authority_manifest_sha256: b938d6366fb91058f9e35b1b3b7c4ba255f5f53a7860f9f0dc2b905f732b263b
new_worked_solution_count: 3
source_exercise_numbers: "24.1,24.3,24.4"
non_endorsement: "Independent editorial material; does not imply endorsement or review by Holger Brenner, source contributors, Wikiversity, or the Wikimedia Foundation."
---

# BGK 24 mastery exercises: Hom and Ext {#d100-bridge-mastery-bgk-24}

The following three exercises come from Holger Brenner's course. The solutions here are new editorial material, not public source solutions or translations of the author's work. The source worksheet and its record of the absence of public solutions are preserved. This sequence connects left exactness of $\operatorname{Hom}$, the property of projective modules, and a nonzero $\operatorname{Ext}^1$ computation.

## Source Exercise 24.1: left exactness of Hom {#d100-bridge-mastery-bgk-24-new-01}

Source: [Exercise 24.1 in the BGK reader](bgk-reader.html#br-bgk-2019-w24-ex01), entity `Modul/Homomorphismenmodul/Kovariant/Linksexakt/Aufgabe`, [revision 1081675](https://de.wikiversity.org/w/index.php?oldid=1081675), page 114118. The exercise is preserved without changing its hypotheses.

### Problem statement {#d100-bridge-mastery-bgk-24-new-01-soal}

Let $R$ be a commutative ring, $A$ an $R$-module, and

$$
0\longrightarrow L\xrightarrow{i}M\xrightarrow{p}N\longrightarrow0
$$

a short exact sequence of $R$-modules. Prove that the sequence

$$
0\longrightarrow\operatorname{Hom}_R(A,L)
\xrightarrow{i_*}\operatorname{Hom}_R(A,M)
\xrightarrow{p_*}\operatorname{Hom}_R(A,N)
$$

is exact. Here $i_*(f)=i\circ f$ and $p_*(g)=p\circ g$.

### Complete editorial solution {#d100-bridge-mastery-bgk-24-new-01-solusi}

First, $i_*$ is injective. If $i\circ f=0$, then for every $a\in A$ we have $i(f(a))=0$. Since $i$ is injective, $f(a)=0$ for every $a$, so $f=0$.

Next, $p\circ i=0$ gives

$$
p_*(i_*(f))=p\circ i\circ f=0.
$$

Thus $\operatorname{im}(i_*)\subseteq\ker(p_*)$. For the reverse inclusion, take $g:A\to M$ with $p\circ g=0$. Every $g(a)$ lies in $\ker(p)=\operatorname{im}(i)$. Since $i$ is injective, there is exactly one element $f(a)\in L$ such that $i(f(a))=g(a)$. This defines a map $f:A\to L$.

The map is linear. For $a,a'\in A$ and $r\in R$,

$$
\begin{aligned}
i(f(a+a'))&=g(a+a')=g(a)+g(a')=i(f(a)+f(a')),\\
i(f(ra))&=g(ra)=rg(a)=i(rf(a)).
\end{aligned}
$$

Injectivity of $i$ gives $f(a+a')=f(a)+f(a')$ and $f(ra)=rf(a)$. Hence $f\in\operatorname{Hom}_R(A,L)$ and $g=i_*(f)$. Thus $\ker(p_*)=\operatorname{im}(i_*)$, as required.

### Check and pitfall {#d100-bridge-mastery-bgk-24-new-01-periksa}

The requested sequence has no $0$ on the right. Surjectivity of $p$ does not guarantee that every map $A\to N$ lifts to $M$. The proof only lifts maps whose images already lie in $\ker(p)$ to the module $L$; that differs from lifting maps to $N$.

## Source Exercise 24.3: a projective module in the first argument {#d100-bridge-mastery-bgk-24-new-02}

Source: [Exercise 24.3 in the BGK reader](bgk-reader.html#br-bgk-2019-w24-ex03), entity `Projektiver Modul/Extmoduln/Aufgabe`, [revision 1039771](https://de.wikiversity.org/w/index.php?oldid=1039771), page 114115. The definition used is [Definition 24.11](bgk-reader.html#br-bgk-2019-l24-def-06).

### Problem statement {#d100-bridge-mastery-bgk-24-new-02-soal}

Let $R$ be a commutative ring, $P$ a projective $R$-module, and $M$ an $R$-module. Prove that

$$
\operatorname{Ext}_R^n(P,M)=0\qquad(n\geq1).
$$

### Complete editorial solution {#d100-bridge-mastery-bgk-24-new-02-solusi}

Take an injective resolution of the second argument,

$$
0\longrightarrow M\longrightarrow I^0\xrightarrow{d^0}I^1
\xrightarrow{d^1}I^2\longrightarrow\cdots.
$$

By definition, $\operatorname{Ext}_R^n(P,M)=H^n(\operatorname{Hom}_R(P,I^\bullet))$. We show directly that every positive-degree cocycle is a coboundary.

Fix $n\geq1$ and take a homomorphism $f:P\to I^n$ that is a cocycle, meaning $d^n\circ f=0$. With $Z^n=\ker(d^n)$, the map $f$ factors through a homomorphism $\bar f:P\to Z^n$. Exactness of the resolution gives a surjection

$$
\bar d^{\,n-1}:I^{n-1}\longrightarrow Z^n,
\qquad u\longmapsto d^{n-1}(u).
$$

Projectivity of $P$ means that homomorphisms from $P$ can be lifted through every surjection. Thus there is $g:P\to I^{n-1}$ with $\bar d^{\,n-1}\circ g=\bar f$. Including $Z^n$ into $I^n$, we obtain

$$
d^{n-1}\circ g=f.
$$

Thus $f$ is indeed a coboundary. Since every cocycle has this form, the quotient of cocycles by coboundaries is zero in every degree $n\geq1$. This is the required statement.

### Check and pitfall {#d100-bridge-mastery-bgk-24-new-02-periksa}

It is $P$, the first argument, that must be projective; the injective resolution is still taken of $M$, the second argument. We do not assert that $P$ is injective. Nor does the conclusion hold in degree zero: for example, $\operatorname{Ext}_R^0(R,M)=\operatorname{Hom}_R(R,M)\cong M$ can be nonzero.

## Source Exercise 24.4: Ext classes detected modulo k {#d100-bridge-mastery-bgk-24-new-03}

Source: [Exercise 24.4 in the BGK reader](bgk-reader.html#br-bgk-2019-w24-ex04), entity `Extmodul/1/Z mod k und Z/Nicht 0/Aufgabe`, [revision 1107271](https://de.wikiversity.org/w/index.php?oldid=1107271), page 114122. The computation below proves the source's nonvanishing conclusion and also determines the group; the hypothesis $k\geq2$ is unchanged.

### Problem statement {#d100-bridge-mastery-bgk-24-new-03-soal}

Using the short exact sequence

$$
0\longrightarrow\mathbb Z\xrightarrow{\,\cdot k\,}\mathbb Z
\longrightarrow\mathbb Z/(k)\longrightarrow0,
$$

prove that $\operatorname{Ext}_{\mathbb Z}^1(\mathbb Z/(k),\mathbb Z)$ is nonzero for $k\geq2$.

### Complete editorial solution {#d100-bridge-mastery-bgk-24-new-03-solusi}

Write $A=\mathbb Z/(k)$ and take an injective resolution

$$
0\longrightarrow\mathbb Z\xrightarrow{\iota}I^0
\xrightarrow{d^0}I^1\xrightarrow{d^1}I^2\longrightarrow\cdots.
$$

We will construct an isomorphism

$$
\mathbb Z/(k)\xrightarrow{\ \sim\ }
H^1(\operatorname{Hom}_{\mathbb Z}(A,I^\bullet))
=\operatorname{Ext}_{\mathbb Z}^1(A,\mathbb Z).
$$

For $n\in\mathbb Z$, define a homomorphism from the subgroup $k\mathbb Z\subseteq\mathbb Z$ to $I^0$ by $k\mapsto\iota(n)$. Injectivity of $I^0$ extends it to a homomorphism $\mathbb Z\to I^0$. If the image of $1$ is $y$, then $ky=\iota(n)$. Since $d^0\iota=0$, the element $d^0y$ is killed by $k$. Hence there is a homomorphism

$$
f_n:A\longrightarrow I^1,\qquad \overline{1}\longmapsto d^0y.
$$

The equality $d^1d^0=0$ shows that $f_n$ is a cocycle. Set $\delta(n)=[f_n]$. If $y'$ is another choice, $k(y-y')=0$, so $b:A\to I^0$, $b(\overline1)=y-y'$, is well-defined. The difference $f_n-f'_n=d^0\circ b$ is a coboundary. Thus $\delta(n)$ is independent of the choice of $y$. Choosing $y+y'$ for $n+n'$ also shows that $\delta$ is additive.

Now compute its kernel. If $n=km$, we may take $y=\iota(m)$; then $f_n=0$ and $k\mathbb Z\subseteq\ker\delta$. Conversely, suppose $\delta(n)=0$. There is $b:A\to I^0$ with $f_n=d^0\circ b$. For $b_0=b(\overline1)$ we have $kb_0=0$ and $d^0(y-b_0)=0$. Exactness of the resolution gives $y-b_0=\iota(m)$ for some $m\in\mathbb Z$. Multiply by $k$:

$$
\iota(n)=ky=kb_0+k\iota(m)=\iota(km).
$$

Since $\iota$ is injective, $n=km$. Thus $\ker\delta=k\mathbb Z$.

Finally, $\delta$ is surjective. A cocycle $f:A\to I^1$ is determined by $z=f(\overline1)$ with $kz=0$ and $d^1z=0$. Exactness of the resolution gives $z=d^0y$ for some $y\in I^0$. Now $d^0(ky)=kz=0$, so $ky=\iota(n)$ for some integer $n$. The construction above yields $f_n=f$. Thus every cohomology class lies in the image of $\delta$.

The first isomorphism theorem gives

$$
\operatorname{Ext}_{\mathbb Z}^1(\mathbb Z/(k),\mathbb Z)
\cong\mathbb Z/(k).
$$

The class $\overline1$ is nonzero when $k\geq2$, so this Ext group is nonzero. The inclusion $k\mathbb Z\subseteq\mathbb Z$ used in the construction is precisely the image of the map $\cdot k$ in the source's short exact sequence.

### Check and pitfall {#d100-bridge-mastery-bgk-24-new-03-periksa}

Do not apply a long exact sequence in the first argument of Ext without explaining why: the lecture's definition uses a resolution of the second argument. The cocycle computation above works directly with that definition. Also check $k=1$: the result is the zero group, so the bound $k\geq2$ is genuinely needed for the source's conclusion.

## Origin and licence of the material {#d100-bridge-mastery-bgk-24-kredit}

Exercises: Holger Brenner and Wikiversity contributors at the linked revisions, from *Bündel, Garben und Kohomologie (Osnabrück 2019-2020)*. Solutions and mastery notes: independently prepared editorial material by OpenAI Codex gpt-5.6-sol, Ultra. This material is licensed under CC BY-SA 4.0; the attribution and licences of source components remain applicable. There is no claim that these new solutions were written or reviewed by the source author, and no endorsement by the author, contributors, Wikiversity, or the Wikimedia Foundation is implied.
