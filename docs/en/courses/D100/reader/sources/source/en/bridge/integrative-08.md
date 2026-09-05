---
title: "Integrative Problem 8 - A Čech Calculation with Signs and Quotient Classes"
stable_id: d100-bridge-integrative-08
language: en
content_origin: independent_editorial_material
status: independently_reviewed_complete
license: "CC BY-SA 4.0"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
source_context_author: "Holger Brenner"
source_context: "Bündel, Garben und Kohomologie, Lecture 25 revision 1003754 and Lecture 26 revision 793619"
source_context_urls:
  - "https://de.wikiversity.org/w/index.php?oldid=1003754"
  - "https://de.wikiversity.org/w/index.php?oldid=793619"
non_endorsement: "Independent editorial problem and solution; no authorship or endorsement by the source author or institution is implied."
---

# Integrative problem 8: a Čech calculation with signs and quotient classes {#d100-bridge-integrative-08}

This problem and solution were independently written to synthesise
localisation methods and Čech cohomology. The referenced theory is Holger
Brenner's: [Definition 26.3](bgk-reader.html#br-bgk-2019-l26-def-01),
[Example 26.7](bgk-reader.html#br-bgk-2019-l26-exm-04), and
[Lemma 26.8](bgk-reader.html#br-bgk-2019-l26-lem-02). This is not an
addition to the public solutions of the source worksheet.

## Problem statement {#d100-bridge-integrative-08-problem}

Let $k$ be any field and $R=k[x,y,z]$. Take

$$
X=\operatorname{Spec}(R)\setminus V(x,y),\qquad
U_0=D(x),\qquad U_1=D(y).
$$

Thus the entire line defined by $x=y=0$ is removed, not just a single
point. We work with the structure sheaf $\mathcal O_X$ and the index
order $0<1$.

1. Write down the Čech complex, including the signs of its differential.
   Compute $\check H^0$ and $\check H^1$ as modules over $k[z]$.
2. Determine the normal representative of the class given by
   $$
   c=\frac{z}{xy}+\frac{1}{x^2y}+\frac{x^2}{y^3}+\frac{y}{x^4}.
   $$
   Show explicitly which terms are coboundaries.
3. Explain why the quotient for $\check H^1$ is a quotient module, not
   a quotient ring. Determine whether the class $z/(xy)$ is zero; then
   determine its image in the calculation obtained by setting $z=0$.
4. Check the hypotheses identifying $\check H^1$ with
   $H^1(X,\mathcal O_X)$, and conclude that $X$ is not affine even
   though $\Gamma(X,\mathcal O_X)=R$.

## Complete solution {#d100-bridge-integrative-08-solution}

### The complex and its signs {#d100-bridge-integrative-08-complex}

The intersection is $U_0\cap U_1=D(xy)$. By the description of sections
through localisation, the complex is

$$
0\longrightarrow R_x\oplus R_y
\xrightarrow{\,\delta^0\,}R_{xy}
\longrightarrow0,
\qquad \delta^0(a,b)=b-a.
$$

Both terms on the right of the formula are taken after restriction to
$D(xy)$. The sign comes from
$(\delta^0s)_{01}=s_1|_{01}-s_0|_{01}$, following the order $0<1$.
Since the cover has only two members, $\check C^2=0$; every element
of $R_{xy}$ is therefore a degree-one cocycle.

To recall the convention, for three ordered cover members $0<1<2$,
the next differential would be

$$
(\delta^1c)_{012}=c_{12}|_{012}-c_{02}|_{012}+c_{01}|_{012}.
$$

Substituting $c_{ij}=s_j-s_i$ gives
$(s_2-s_1)-(s_2-s_0)+(s_1-s_0)=0$. This explains the sign cancellation;
for our cover there is no degree-two term to compute.

### The kernel and quotient module {#d100-bridge-integrative-08-quotient}

The three localisation rings can be viewed as subrings of the Laurent
polynomial ring

$$
R_{xy}=k[z][x,x^{-1},y,y^{-1}].
$$

As a $k[z]$-module, this last ring has a monomial basis $x^i y^j$ with
$(i,j)\in\mathbb Z^2$. Every element is a **finite** linear combination
of these monomials. In $R_x$, the exponent of $y$ must be nonnegative;
in $R_y$, the exponent of $x$ must be nonnegative. Uniqueness of Laurent
expressions gives

$$
R_x\cap R_y=k[z][x,y]=R.
$$

Thus the kernel of $\delta^0$ consists of pairs $(f,f)$, $f\in R$, and

$$
\check H^0(\{U_0,U_1\},\mathcal O_X)\cong R.
$$

The image of $\delta^0$ is $R_x+R_y$: the minus sign does not change
the generated submodule because $R_x$ is closed under negation. This
submodule consists exactly of combinations of monomials with at least
one of $i,j$ nonnegative. Hence

$$
\begin{aligned}
\check H^1(\{U_0,U_1\},\mathcal O_X)
&=R_{xy}/(R_x+R_y)\\
&\cong\bigoplus_{a\geq1,\ b\geq1}k[z]\,[x^{-a}y^{-b}].
\end{aligned}
$$

A normal representative exists by discarding all monomials whose $x$
or $y$ exponent is nonnegative. Its uniqueness follows from uniqueness
of Laurent coefficients: a combination of monomials with both exponents
negative cannot equal a combination of monomials in the complementary
set. Thus this is not merely a generating list but a genuine basis of
a free module over $k[z]$.

### Reducing the given cocycle {#d100-bridge-integrative-08-representative}

Set

$$
a=-\frac{y}{x^4}\in R_x,\qquad
b=\frac{x^2}{y^3}\in R_y.
$$

Our chosen sign convention gives

$$
\delta^0(a,b)=\frac{x^2}{y^3}+\frac{y}{x^4}.
$$

Therefore

$$
[c]=\left[\frac{z}{xy}+\frac{1}{x^2y}\right]
=z[x^{-1}y^{-1}]+[x^{-2}y^{-1}].
$$

This is the required normal representative. Its class is nonzero: the
coefficient of the basis element $[x^{-2}y^{-1}]$ is $1$, nonzero over
any field. This remains true in characteristic two; the sign convention
is still valid, although negation coincides with the identity.

### Why this is not a quotient ring {#d100-bridge-integrative-08-module-not-ring}

The submodule $R_x+R_y$ is stable under multiplication by $R$, but is
not an ideal of $R_{xy}$. It contains $1$ but does not contain $1/(xy)$.
An ideal containing $1$ must be the whole ring. Thus the quotient
notation above must be read as a quotient of $R$-modules, or in
particular of $k[z]$-modules, not as a quotient ring of $R_{xy}$.

An example of using the correct module structure is

$$
xy\,[x^{-1}y^{-1}]=[1]=0
$$

even though $[x^{-1}y^{-1}]\ne0$. This does not mean that arbitrary
classes can be multiplied using multiplication in $R_{xy}$; that
multiplication does not descend to this quotient.

The class $z[x^{-1}y^{-1}]$ is nonzero because its coefficient $z$ is
nonzero in $k[z]$ and the module above is free over $k[z]$. Substitution
$z=0$ defines a map from our complex to the complex

$$
0\longrightarrow k[x,y]_x\oplus k[x,y]_y
\longrightarrow k[x,y]_{xy}\longrightarrow0.
$$

The map is compatible with $b-a$, so it induces a cohomology map
replacing every coefficient $f(z)$ by $f(0)$. The image of
$z[x^{-1}y^{-1}]$ is zero, whereas the image of $[c]$ is
$[x^{-2}y^{-1}]$, still nonzero. This conclusion follows directly
from the complexes; no unproved cohomology base-change theorem is needed.

### From Čech to sheaf cohomology {#d100-bridge-integrative-08-sheaf-cohomology}

The spaces $U_0$, $U_1$, and $U_0\cap U_1$ are affine, with rings
$R_x$, $R_y$, and $R_{xy}$. All three are integral domains, being
localisations of the integral domain $k[x,y,z]$. The restriction of
$\mathcal O_X$ to each open is its structure sheaf.
[Lemma 25.7](bgk-reader.html#br-bgk-2019-l25-lem-04) therefore gives

$$
H^1(U_0,\mathcal O_X)=H^1(U_1,\mathcal O_X)
=H^1(U_0\cap U_1,\mathcal O_X)=0.
$$

The hypotheses of [Lemma 26.8](bgk-reader.html#br-bgk-2019-l26-lem-02)
hold, so the $\check H^1$ computed above equals $H^1(X,\mathcal O_X)$.
In particular, this group is nonzero.

As a nonempty open subset of the integral scheme $\operatorname{Spec}(R)$,
$X$ is integral. If $X$ were affine, its coordinate ring would be an
integral domain and Lemma 25.7 would force $H^1(X,\mathcal O_X)=0$,
contradicting the class $[x^{-1}y^{-1}]$ we found. Thus $X$ is not
affine. The identity $\Gamma(X,\mathcal O_X)=R$ remains true, since
global sections form the kernel of the Čech complex by the sheaf gluing
property. The global section ring alone does not recover this nonaffine
scheme.

## Checks and pitfalls {#d100-bridge-integrative-08-check}

A denominator containing both $x$ and $y$ does not automatically yield
a nonzero class: after cancellation, both exponents must genuinely be
negative. The order $0<1$ fixes the sign $b-a$. Using $a-b$ consistently
gives an isomorphic complex, but mixing the conventions spoils the
representative calculation. The statement about sheaf $H^1$ is used
only after the comparison hypotheses have been checked.

## Provenance and usage rights {#d100-bridge-integrative-08-provenance}

Theory references: Holger Brenner, *Bündel, Garben und Kohomologie*,
[Lecture 25, revision 1003754](https://de.wikiversity.org/w/index.php?oldid=1003754)
and [Lecture 26, revision 793619](https://de.wikiversity.org/w/index.php?oldid=793619).
This independent editorial problem and solution are licensed under
CC BY-SA 4.0. Production: OpenAI Codex gpt-5.6-sol, Ultra. No human
authorship or review, or endorsement by the source author, is claimed.
