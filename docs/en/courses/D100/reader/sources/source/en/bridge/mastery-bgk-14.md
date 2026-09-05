---
title: "BGK 14 Mastery - Localisation and Global Sections"
stable_id: d100-bridge-mastery-bgk-14
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_author: "Holger Brenner"
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_unit: 14
source_worksheet_revision: 1005264
source_manifest: "authority/wikiversity-bgk/unit-14/UNIT_AUTHORITY_MANIFEST.json"
source_manifest_sha256: "c6d5c2fc64d18c759795a55c7ef618acfba3d112a58ac44ff2b3badcb133e038"
new_worked_solutions: 3
existing_source_solutions_counted: []
non_endorsement: "Independent editorial material; does not imply endorsement or human checking by the source author or source institutions."
---

# BGK 14 mastery: localisation and global sections {#d100-bridge-mastery-bgk-14}

The three exercises below come from Holger Brenner and the Wikiversity course contributors. Their solutions are independent editorial material, not public solutions by Brenner. The negative result of the search for public source solutions remains recorded; this supplementary material is not included in the source-solution corpus. The translated problem text and this editorial material remain under CC BY-SA 4.0. Production provenance: OpenAI Codex gpt-5.6-sol, Ultra. No endorsement by the source author or human checking is implied.

## New item 1: zero at a point, zero on a neighbourhood {#d100-bridge-mastery-bgk-14-new-01}

Source: [BGK Exercise 14.3](bgk-reader.html#br-bgk-2019-w14-ex03), identifier `Kommutativer Ring/Modul/Endlich erzeugter/0 in Punkt/Umgebung/Aufgabe`, [revision 1039028](https://de.wikiversity.org/w/index.php?oldid=1039028).

### Source exercise {#d100-bridge-mastery-bgk-14-new-01-problem}

Let $R$ be a commutative ring and $M$ a finitely generated $R$-module. If $\mathfrak p\in\operatorname{Spek}(R)$ satisfies $M_{\mathfrak p}=0$, prove that there is $f\notin\mathfrak p$ with $M_f=0$.

### Independent solution {#d100-bridge-mastery-bgk-14-new-01-solution}

Choose generators $m_1,\ldots,m_r$ for $M$. If $M=0$, the choice $f=1$ already gives the conclusion. For each generator in the general case, the assumption $M_{\mathfrak p}=0$ gives

$$
\frac{m_i}{1}=0\quad\text{in }M_{\mathfrak p}.
$$

By the definition of equality in module localisation at the multiplicative set $R\setminus\mathfrak p$, there is $s_i\notin\mathfrak p$ such that $s_i m_i=0$ in $M$. Take

$$
f=s_1s_2\cdots s_r.
$$

Since $\mathfrak p$ is prime and contains none of the $s_i$, we have $f\notin\mathfrak p$. For every $i$,

$$
fm_i=\left(\prod_{j\ne i}s_j\right)(s_i m_i)=0.
$$

Every element of $M$ is a linear combination of the $m_i$, so $fM=0$. In $M_f$, the element $f$ becomes a unit. For any fraction $m/f^k\in M_f$,

$$
\frac{m}{f^k}=\frac{fm}{f^{k+1}}=0.
$$

Hence $M_f=0$. The principal open $D(f)$ contains $\mathfrak p$ because $f\notin\mathfrak p$. In sheaf language, further localisation at any point $\mathfrak q\in D(f)$ is also zero, so $\widetilde M|_{D(f)}=0$. This explains the geometric meaning of the neighbourhood found.

### Checks and common mistakes {#d100-bridge-mastery-bgk-14-new-01-check}

Finiteness is used to form one product $f$ annihilating all generators. The proof has no Noetherian or integral domain hypothesis. Without finiteness, a common denominator can fail to exist: for $M=\mathbb Q/\mathbb Z$ and $\mathfrak p=(0)\subset\mathbb Z$, we have $M_{(0)}=0$ because every class is annihilated by a nonzero integer. However, for $f\ne0$, choose a prime number $\ell$ not dividing $f$. The class $1/\ell+\mathbb Z$ remains nonzero after localisation at $f$, since none of the $f^k/\ell$ are integers. Thus $M_f\ne0$ for every such choice.

## New item 2: locally surjective, but not the unit ideal globally {#d100-bridge-mastery-bgk-14-new-02}

Source: [BGK Exercise 14.10](bgk-reader.html#br-bgk-2019-w14-ex10), identifier `Punktierte Ebene/Festlegungssatz/Kein Einheitsideal/Surjektiv/Aufgabe`, [revision 1081689](https://de.wikiversity.org/w/index.php?oldid=1081689).

### Source exercise {#d100-bridge-mastery-bgk-14-new-02-problem}

Let $K$ be a field and $U=\mathbb A_K^2\setminus\{(0,0)\}$ the punctured affine plane, with its structure sheaf $\mathcal O_U$. Give global sections $s_1,s_2\in\Gamma(U,\mathcal O_U)$ such that $(s_1,s_2)$ is not the unit ideal, but the homomorphism of sheaves of modules

$$
\mathcal O_U^2\longrightarrow\mathcal O_U,
\qquad e_i\longmapsto s_i,
$$

is surjective. Here $\mathcal O_U$ is the restriction of the affine plane's structure sheaf, also denoted by $\mathcal O_X$ in the source exercise.

### Independent solution {#d100-bridge-mastery-bgk-14-new-02-solution}

Take $R=K[X,Y]$ and regard the origin as the maximal ideal $(X,Y)$. Since a prime ideal containing $X$ and $Y$ must equal $(X,Y)$,

$$
U=D(X)\cup D(Y).
$$

We will use the restrictions of the coordinate functions $s_1=X$ and $s_2=Y$.

**Computing the global section ring.** By the description of structure-sheaf sections on principal opens, which is also the case $M=R$ of [Lemma 14.5](bgk-reader.html#br-bgk-2019-l14-lem-03),

$$
\Gamma(D(X),\mathcal O_U)=R_X,\qquad
\Gamma(D(Y),\mathcal O_U)=R_Y.
$$

The intersection is $D(XY)$, with section ring $R_{XY}$. All these rings are subrings of the field of fractions $K(X,Y)$. The sheaf gluing axiom gives

$$
\Gamma(U,\mathcal O_U)=R_X\cap R_Y
\quad\text{inside }K(X,Y).
$$

We prove that this intersection is exactly $R$. If

$$
\frac a{X^m}=\frac b{Y^n},\qquad a,b\in R,
$$

then $aY^n=bX^m$. The element $X$ is prime in $R$, since $R/(X)=K[Y]$ is an integral domain, and $X$ does not divide $Y$. Hence $X^m$ divides $a$, by repeatedly applying primality of $X$. Thus $a/X^m\in R$. The inclusion $R\subseteq R_X\cap R_Y$ is clear, so

$$
\Gamma(U,\mathcal O_U)=K[X,Y].
$$

**The global ideal is not the unit ideal.** In this ring, the ideal generated by $s_1$ and $s_2$ is $(X,Y)$, which is proper because $R/(X,Y)\cong K\ne0$. Concretely, there are no polynomials $a,b$ with $aX+bY=1$: substituting $X=Y=0$ would give $0=1$. This substitution merely tests an identity in the polynomial ring; we are not putting the origin back into $U$.

**The sheaf homomorphism is surjective.** The map to check is

$$
\varphi(a,b)=Xa+Yb.
$$

On any open $V\subseteq D(X)$, the function $X$ has an inverse, so every $t\in\mathcal O_U(V)$ has a preimage $(X^{-1}t,0)$. This formula is compatible with restrictions and gives a right inverse to $\varphi|_{D(X)}$. On $D(Y)$, a right inverse is $t\mapsto(0,Y^{-1}t)$. Since $D(X)$ and $D(Y)$ cover $U$, every target section can be lifted locally; equivalently, the map on each stalk is surjective. Thus $\varphi$ is a surjection of sheaves of modules.

In contrast, the map on global sections is

$$
R^2\longrightarrow R,\qquad(a,b)\longmapsto Xa+Yb,
$$

whose image is $(X,Y)$ and does not contain $1$. This is the required example.

### Checks and common mistakes {#d100-bridge-mastery-bgk-14-new-02-check}

The two local right inverses need not agree on the intersection; indeed, there is no global right inverse lifting $1$. Sheaf surjectivity means the existence of *local* lifts, not surjectivity on sections over every open set. This computation works over any field $K$ and uses all prime points of the scheme, not just its rational points.

## New item 3: change of scalars and the tensor–Hom adjunction {#d100-bridge-mastery-bgk-14-new-03}

Source: [BGK Exercise 14.15](bgk-reader.html#br-bgk-2019-w14-ex15), identifier `Ringwechsel/Vorgezogener und zurückgezogener Modul/Homomorphismus/Aufgabe`, [revision 1039630](https://de.wikiversity.org/w/index.php?oldid=1039630).

### Source exercise {#d100-bridge-mastery-bgk-14-new-03-problem}

Let $\theta:A\to B$ be a homomorphism of commutative rings, $M$ an $A$-module, and $N$ a $B$-module. Write $N'$ for $N$ viewed as an $A$-module through $\theta$. Prove the natural group isomorphism

$$
\operatorname{Hom}_B(M\otimes_A B,N)
\cong\operatorname{Hom}_A(M,N').
$$

### Independent solution {#d100-bridge-mastery-bgk-14-new-03-solution}

The scalar structure on $N'$ is $a\cdot n=\theta(a)n$. Define the first map by evaluating on tensors whose second factor is $1$:

$$
\Phi(f)(m)=f(m\otimes1).
$$

This map is additive in $m$. For $a\in A$,

$$
\begin{aligned}
\Phi(f)(am)
&=f(am\otimes1)\\
&=f(m\otimes\theta(a))\\
&=\theta(a)f(m\otimes1)\\
&=a\cdot\Phi(f)(m).
\end{aligned}
$$

Thus $\Phi(f)$ is an $A$-module homomorphism from $M$ to $N'$.

For the reverse direction, given $g\in\operatorname{Hom}_A(M,N')$, we want to define

$$
\Psi(g)(m\otimes b)=b\,g(m).
$$

The map $(m,b)\mapsto b g(m)$ is additive in each variable. It is also $A$-balanced, since

$$
b\,g(am)=b\theta(a)g(m)=(\theta(a)b)g(m).
$$

The universal property of the tensor product therefore gives exactly one additive map $M\otimes_A B\to N$ with this formula. It is $B$-linear: for $c\in B$,

$$
\Psi(g)(m\otimes cb)=cb\,g(m)
=c\,\Psi(g)(m\otimes b).
$$

Since pure tensors generate $M\otimes_A B$ as an additive group, this check proves linearity on all elements.

The two constructions are inverse. For $g$,

$$
\Phi(\Psi(g))(m)=\Psi(g)(m\otimes1)=g(m).
$$

For $f$, $B$-linearity gives

$$
\Psi(\Phi(f))(m\otimes b)
=b f(m\otimes1)
=f(m\otimes b).
$$

Equality on pure tensors extends to the whole tensor product. The formulas also respect addition of $f$ and of $g$, so they genuinely give a group isomorphism, not merely a bijection of sets.

Finally, naturality can be checked without choosing a basis. If $u:M_1\to M$ is an $A$-module homomorphism and $v:N\to N_1$ a $B$-module homomorphism, then for every $m_1\in M_1$,

$$
\begin{aligned}
\Phi\bigl(v\circ f\circ(u\otimes\operatorname{id}_B)\bigr)(m_1)
&=v\bigl(f(u(m_1)\otimes1)\bigr)\\
&=(v\circ\Phi(f)\circ u)(m_1).
\end{aligned}
$$

Thus the isomorphism is compatible with changing $M$ and $N$ through homomorphisms, exactly as the word *natural* means.

### Checks and common mistakes {#d100-bridge-mastery-bgk-14-new-03-check}

On the right, linearity uses the $A$-structure on $N'$ through $\theta$; do not assume that $M$ is already a $B$-module. A formula on tensors must satisfy the balancing relation before it can be declared well-defined. The proof makes no finiteness, freeness, or flatness assumptions on the modules.
