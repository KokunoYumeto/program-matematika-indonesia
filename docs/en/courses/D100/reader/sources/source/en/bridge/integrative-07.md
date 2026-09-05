---
title: "Integrative Problem 7 - Quasicoherent Sheaves, Localisation, and Fibres"
stable_id: d100-bridge-integrative-07
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_context_author: "Holger Brenner"
source_context: "Bündel, Garben und Kohomologie, Lecture 14; revision 1019980"
source_context_url: "https://de.wikiversity.org/w/index.php?oldid=1019980"
non_endorsement: "Independent editorial problem and solution; no authorship or endorsement by the source author or institution is implied."
---

# Integrative problem 7: quasicoherent sheaves, localisation, and fibres {#d100-bridge-integrative-07}

The problem and solution below are independently written editorial material,
not a public problem or solution attributed to Holger Brenner. They build
on [Lemma 14.4 on stalks](bgk-reader.html#br-bgk-2019-l14-lem-02),
[Lemma 14.5 on sections over principal opens](bgk-reader.html#br-bgk-2019-l14-lem-03),
and [Lemma 14.9 on exactness](bgk-reader.html#br-bgk-2019-l14-lem-05)
in Brenner's course. All these lemmas apply to modules over commutative
rings; the ring used here satisfies this hypothesis.

## Problem statement {#d100-bridge-integrative-07-problem}

Let $k$ be any field, $A=k[t]$, and

$$
X=\operatorname{Spec}(A),\qquad
T=A/(t^2),\qquad M=A\oplus T,\qquad \mathcal F=\widetilde M.
$$

Use the cover $U=D(t)$ and $V=D(1-t)$ of $X$.

1. Compute the sections of $\mathcal F$ on $X,U,V,U\cap V$, including
   the restriction maps. Explain how compatible sections on $U$ and $V$
   determine exactly one global section.
2. Determine the stalks and fibres of $\mathcal F$ at $p=(t)$ and at
   the generic point $\eta=(0)$. Is $\mathcal F$ quasicoherent, coherent,
   or locally free around $p$?
3. Prove that
   $$
   0\longrightarrow A/(t)\xrightarrow{\,j\,}T
   \xrightarrow{\,q\,}A/(t)\longrightarrow0,
   \qquad j(\bar a)=\overline{ta},\quad q(\bar b)=\bar b,
   $$
   is exact but does not split as a sequence of $A$-modules. Compare
   the effects of localisation and of taking the fibre at $p$.

Here the fibre of a sheaf of modules at $x$ means
$\mathcal F(x)=\mathcal F_x\otimes_{\mathcal O_{X,x}}\kappa(x)$,
not its stalk $\mathcal F_x$.

## Complete solution {#d100-bridge-integrative-07-solution}

### Sections and gluing {#d100-bridge-integrative-07-sections}

Since $t+(1-t)=1$, no prime ideal contains both elements. Thus
$D(t)\cup D(1-t)=X$, while their intersection is $D(t(1-t))$.
By Lemma 14.5, sections over every principal open are obtained by
localising $M$.

In $T_t$, the element $t$ is both invertible and square-zero;
consequently $1=0$ and $T_t=0$. In contrast, in $T$ we have

$$
(1-t)(1+t)=1-t^2=1.
$$

Since $1-t$ already acts invertibly on $T$, localisation at $1-t$
does not change that module. With this identification we obtain

$$
\begin{aligned}
\Gamma(X,\mathcal F)&=A\oplus T,\\
\Gamma(U,\mathcal F)&=A_t,\\
\Gamma(V,\mathcal F)&=A_{1-t}\oplus T,\\
\Gamma(U\cap V,\mathcal F)&=A_{t(1-t)}.
\end{aligned}
$$

Restriction from $X$ to $U$ sends $(a,\tau)$ to $a/1$ and kills the
torsion component. Restriction to $V$ sends it to $(a/1,\tau)$. From
$U$ to the overlap, we localise further at $1-t$. From $V$ to the
overlap, we localise the first component at $t$ and send the $T$
component to zero.

Thus $a\in A_t$ and $(b,\tau)\in A_{1-t}\oplus T$ form a compatible
pair exactly when $a=b$ in $A_{t(1-t)}$. All these rings lie in the
fraction field $k(t)$. If

$$
\frac{f}{t^r}=\frac{g}{(1-t)^s},
$$

then $(1-t)^s f=t^r g$. The polynomials $t^r$ and $(1-t)^s$ are
coprime in $k[t]$, so $t^r$ divides $f$. The common fraction is therefore
actually a polynomial $h\in A$. This proves

$$
A_t\cap A_{1-t}=A\quad\text{inside }k(t).
$$

The original pair glues to $(h,\tau)\in A\oplus T$. Uniqueness follows
from uniqueness of $h$ and the fact that restriction $T\to T_{1-t}$ is
an isomorphism. For example, the section $t+1$ on $U$ and the section
$(t+1,\overline{1+t})$ on $V$ glue to $(t+1,\overline{1+t})$ on $X$.

### Stalks are not fibres {#d100-bridge-integrative-07-stalks-fibers}

Write $A_{(t)}$ for localisation at the complement of $(t)$. Every
polynomial with nonzero constant term acts invertibly on $T$: modulo
$t^2$, it has the form $a+bt$ with $a\ne0$, and its inverse is
$a^{-1}-ba^{-2}t$. Hence

$$
\mathcal F_p=M_{(t)}
\cong A_{(t)}\oplus A/(t^2).
$$

The residue field $\kappa(p)$ is $k$. Taking the fibre gives

$$
\mathcal F(p)
\cong M_{(t)}/tM_{(t)}
\cong k\oplus k.
$$

At the generic point, $\mathcal O_{X,\eta}=k(t)$ and $t$ is already
invertible. Thus

$$
\mathcal F_\eta\cong k(t),\qquad
\kappa(\eta)=k(t),\qquad
\mathcal F(\eta)\cong k(t).
$$

As the sheaf associated to an $A$-module, $\mathcal F$ is quasicoherent.
The module $M$ has two generators and $A=k[t]$ is Noetherian, so
$\mathcal F$ is also coherent. This agrees with
[Definition 14.11 of quasicoherence](bgk-reader.html#br-bgk-2019-l14-def-02)
and [Definition 14.12 of coherence](bgk-reader.html#br-bgk-2019-l14-def-03),
with the additional finiteness condition for coherence.

However, $\mathcal F$ is not locally free around $p$. The element
$(0,\bar1)\in M_{(t)}$ is nonzero and annihilated by $t^2\ne0$.
A free module over the integral domain $A_{(t)}$ has no such torsion:
multiplication by a nonzero element is injective in each coordinate.
If $\mathcal F$ were locally free on a neighbourhood of $p$, its stalk
at $p$ would be free, contradicting this observation. On $D(t)$, by
contrast, this sheaf is free of rank one.

### Exactness, localisation, and loss of injectivity on fibres {#d100-bridge-integrative-07-exactness}

The map $j$ is well defined because replacing $a$ by $a+tc$ changes
$ta$ only by $t^2c$. If $j(\bar a)=0$, then $ta\in(t^2)$, so
$a\in(t)$ and $\bar a=0$. Thus $j$ is injective. The map $q$ is
surjective, with kernel $(t)/(t^2)$, exactly the image of $j$. The
sequence is exact.

Suppose there were an $A$-linear map $s:A/(t)\to T$ with $q\circ s$
the identity. Then $s(\bar1)$ would have to be
$\overline{1+ct}$ for some $c\in k$. Linearity with respect to $t$
requires

$$
t\,s(\bar1)=s(t\bar1)=s(0)=0.
$$

But $t\overline{1+ct}=\bar t\ne0$ in $T$. This contradiction proves
that the sequence does not split.

Localisation preserves exactness. After localising at $t$, all three
modules become zero. After localising at $A\setminus(t)$, the sequence
remains the same nonsplit exact sequence on stalks at $p$. By Lemma
14.9, the associated sheaves also form a short exact sequence.

Taking fibres differs from localising. Tensoring with
$\kappa(p)=A/(t)$ produces

$$
k\xrightarrow{\,0\,}k\xrightarrow{\,\mathrm{id}\,}k
\longrightarrow0.
$$

The first map is zero because its generator was sent to $\bar t$,
which becomes zero after quotienting $T$ by $tT$. The second map is
the identity because the class $\bar1$ still maps to $\bar1$. The
tensor sequence remains exact at the last two terms, but its first map
is no longer injective. There is no contradiction: tensoring is generally
only right exact, whereas localisation is exact.

## Checks and pitfalls {#d100-bridge-integrative-07-check}

The two fibre dimensions are $2$ at $p$ and $1$ at $\eta$; both are
consistent with torsion disappearing after $t$ is inverted. The torsion
component must not be discarded on $D(1-t)$, since that open set contains
$p$. The statement that exactness of a sheaf sequence can be checked
on **stalks** cannot be replaced by a statement that all maps on
**fibres** must remain injective.

## Provenance and usage rights {#d100-bridge-integrative-07-provenance}

Theory reference: Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 14, revision 1019980](https://de.wikiversity.org/w/index.php?oldid=1019980).
This bridge problem, its calculations, and its solution are independent
editorial material licensed under CC BY-SA 4.0. Production: OpenAI Codex
gpt-5.6-sol, Ultra. No human authorship or review is claimed, and no
endorsement by the source author or institution is implied.
