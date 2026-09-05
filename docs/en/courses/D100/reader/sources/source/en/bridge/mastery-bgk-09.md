---
title: "BGK 9 Mastery Exercises: Localisation and Intermediate Rings"
stable_id: d100-bridge-mastery-bgk-09
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_revision_contributor: "Marymay0609"
source_url: "https://de.wikiversity.org/w/index.php?oldid=612139"
source_manifest: authority/wikiversity-bgk/unit-09/UNIT_AUTHORITY_MANIFEST.json
source_manifest_sha256: 553255a52a560f0c4e14cf761409077d2b6788f2f8c9ace3e65b52743bfa3254
non_endorsement: "Independent material; does not imply endorsement by the author or source institutions."
---

# BGK 9 mastery exercises {#d100-bridge-mastery-bgk-09}

The problem statements come from Holger Brenner's course, *Bündel, Garben und Kohomologie*, worksheet revision 612139; revision contributor credit: Marymay0609. The following three solutions are **independent editorial material**, not public solutions by Brenner or translations of source solutions. Prepared by OpenAI Codex gpt-5.6-sol, Ultra. Licensed under CC BY-SA 4.0; no endorsement by the author or source institutions is implied.

## 1. Localisation as a quotient ring {#d100-bridge-mastery-bgk-09-new-01}

**Source:** [Exercise 9.4](bgk-reader.html#br-bgk-2019-w09-ex04), [worksheet revision 612139](https://de.wikiversity.org/w/index.php?oldid=612139).
Exact identifier: `Kommutative Ringtheorie/Nenneraufnahme/Ein Element/Restklassendarstellung/Aufgabe`; source page `19608`, [fixed revision 1098291](https://de.wikiversity.org/w/index.php?oldid=1098291).

**Brenner's exercise.** For a commutative ring $R$ and $f\in R$, prove the $R$-algebra isomorphism

$$
R_f\cong R[T]/(Tf-1).
$$

**Independent solution.** Write $A=R[T]/(Tf-1)$ and let $t$ be the class of $T$. In $A$ we have $tf=1$, so the image of $f$ is a unit with inverse $t$. Define

$$
\alpha:R_f\longrightarrow A,\qquad a/f^n\longmapsto a t^n.
$$

This map is well-defined even if $R$ has zero divisors. Indeed, if $a/f^n=b/f^m$, there is $k\ge0$ with $f^k(f^m a-f^n b)=0$ in $R$. After mapping to $A$, multiply by $t^{k+m+n}$; this gives $at^n=bt^m$. The formulas for addition and multiplication of fractions directly show that $\alpha$ is an $R$-algebra homomorphism.

Conversely, evaluation $R[T]\to R_f$ at $T=f^{-1}$ annihilates $Tf-1$. It therefore induces

$$
\beta:A\longrightarrow R_f,\qquad t\longmapsto 1/f.
$$

The composite $\beta\alpha$ sends every $a/f^n$ back to $a/f^n$. The composite $\alpha\beta$ fixes the image of every element of $R$ and fixes $t$. Since these elements generate $A$ as a ring, $\alpha\beta=\operatorname{id}_A$. Thus the homomorphisms are inverse to each other.

**Check.** If $f=0$, the ideal $(Tf-1)$ is all of $R[T]$ and both sides are the zero ring. Do not assume that $R\to R_f$ is injective; the proof above does not require that assumption.

## 2. When does a localisation vanish? {#d100-bridge-mastery-bgk-09-new-02}

**Source:** [Exercise 9.6](bgk-reader.html#br-bgk-2019-w09-ex06), [worksheet revision 612139](https://de.wikiversity.org/w/index.php?oldid=612139).
Exact identifier: `Nenneraufnahme/f/Nilpotent/Aufgabe`; source page `94310`, [fixed revision 1045587](https://de.wikiversity.org/w/index.php?oldid=1045587).

**Brenner's exercise.** For a commutative ring $R$ and $f\in R$, prove that $f$ is nilpotent exactly when $R_f$ is the zero ring.

**Independent solution.** If $f^n=0$ for some $n\ge1$, the image of $f$ in $R_f$ is invertible. Multiply $f^n=0$ by the inverse $f^{-n}$ in $R_f$ to obtain $1=0$. Every element $u$ then satisfies $u=u\cdot1=u\cdot0=0$, so $R_f$ is the zero ring.

Conversely, if $R_f$ is the zero ring, the fractions $1/1$ and $0/1$ are equal. The definition of equality in a localisation gives $k\ge0$ such that $f^k(1-0)=0$ in $R$. If $k\ge1$, this is exactly nilpotence. If $k=0$, then $1=0$ in $R$; in that case $R$ itself is zero and $f=0$ is also nilpotent. Both directions have been proved.

**Check.** In $R=K[\varepsilon]/(\varepsilon^2)$, localisation at $\varepsilon$ is indeed zero although $R$ is not the zero ring. In contrast, $R=\mathbb Z/6\mathbb Z$ and $f=2$ give a nonzero localisation: the map $R\to\mathbb F_3$ sends $2$ to a unit and extends to $R_f$. Thus “zero divisor” cannot replace “nilpotent”.

## 3. Intermediate rings over a principal ideal domain {#d100-bridge-mastery-bgk-09-new-03}

**Source:** [Exercise 9.8](bgk-reader.html#br-bgk-2019-w09-ex08), [worksheet revision 612139](https://de.wikiversity.org/w/index.php?oldid=612139).
Exact identifier: `Hauptidealbereich/Zwischenring in Quotientenkörper/Ist Nenneraufnahme/Aufgabe`; source page `20756`, [fixed revision 1061311](https://de.wikiversity.org/w/index.php?oldid=1061311).

**Brenner's exercise.** Let $R$ be a principal ideal domain, $Q$ its field of fractions, and $R\subseteq S\subseteq Q$ an intermediate ring. Prove that $S$ is a localisation of $R$.

**Independent solution.** Take the multiplicative set

$$
M=\{b\in R\setminus\{0\}:1/b\in S\}.
$$

This set contains $1$, and if $b,c\in M$, then $1/(bc)=(1/b)(1/c)\in S$. Since all elements of $M$ are nonzero, we can regard $M^{-1}R$ as a subring of $Q$. The definition of $M$ directly gives $M^{-1}R\subseteq S$.

For the converse, take $q\in S$ and write $q=a/b$ with $b\ne0$. Since $R$ is a principal ideal domain, dividing numerator and denominator by a generator of the ideal $(a,b)$ allows us to choose $a,b$ with $(a,b)=R$. There are then $u,v\in R$ with

$$
ua+vb=1.
$$

Divide this equality by $b$ in $Q$. We obtain

$$
1/b=u(a/b)+v=uq+v\in S.
$$

Thus $b\in M$ and $q=a/b\in M^{-1}R$. Since $q$ was arbitrary, $S=M^{-1}R$ as subrings of $Q$, not merely as abstractly isomorphic rings.

**Check.** The key step is the Bézout identity $ua+vb=1$ for a reduced fraction. Unique factorisation alone does not guarantee this identity; do not replace the principal ideal domain hypothesis without an additional proof.
