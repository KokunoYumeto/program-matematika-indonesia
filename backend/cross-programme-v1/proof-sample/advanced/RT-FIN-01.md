# Representations and complete reducibility

*Written by GPT-6.1 Sol (OpenAI) in Codex, Ultra setting, October 2026. Self-checked by the AI that wrote it. Public domain (CC0).*

A symmetry can permute coordinates, rotate a plane, or act on a space of functions. A representation puts these actions into one language: each group element becomes an invertible linear map. The first problem is to find smaller spaces that all these maps preserve. The next problem is to decide whether those spaces can be separated into independent pieces.

For a finite group over the complex numbers, both questions have a clean answer. Every representation splits into irreducible pieces. Their isomorphism classes and multiplicities are determined by the representation, although the individual summands need not be. We will prove this using averaging and Schur's lemma, and see exactly what changes over the real numbers or in positive characteristic.

The prerequisites are [Linear Algebra](https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-B40), [Abstract Algebra I](https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-C30), and [Abstract Algebra II](https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-C40). We assume vector spaces, bases, eigenvalues, inner products, groups and quotient groups, and the definitions of fields and algebras. The specific facts used without proof are listed near the end.

Basic references are [Stacks], [Gruson–Serganova], [Artin], and [Schur]. [Clanker Stacks](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html) is an edition of the [official Stacks project](https://stacks.math.columbia.edu/) with AI-proposed corrections and AI-written additions, not reviewed by the Stacks project's maintainers. All the representation-theoretic arguments needed here are given below.

Throughout, \(G\) is finite and representations are finite-dimensional over a field \(k\). An irreducible representation is always nonzero. Complex inner products are linear in their first variable.

## 1. Turning symmetry into linear algebra

A **representation** on \(V\) is a homomorphism

\[
\rho:G\longrightarrow\operatorname{GL}_k(V).
\]

Thus \(\rho(gh)=\rho(g)\rho(h)\), \(\rho(1)=1_V\), and \(\rho(g^{-1})=\rho(g)^{-1}\). We often write \(gv\) for \(\rho(g)v\). Its dimension is \(\dim_k V\). It is **faithful** when \(\rho\) is injective.

Choosing a basis gives matrices for every \(\rho(g)\). Changing that basis conjugates all the matrices by the same invertible matrix. The representation is the action itself; a matrix list records it in chosen coordinates.

### Maps and invariant spaces

An **intertwiner** \(f:V\to W\) is a linear map satisfying

\[
f(\rho_V(g)v)=\rho_W(g)f(v)\qquad(g\in G).
\]

The vector space of these maps is \(\operatorname{Hom}_G(V,W)\). An invertible intertwiner is an isomorphism of representations. The algebra \(\operatorname{End}_G(V)\) consists of the operators commuting with every \(\rho(g)\), with multiplication given by composition.

A subspace \(U\subseteq V\) is **invariant** if \(gU\subseteq U\) for every \(g\). Applying the same condition to \(g^{-1}\) gives \(gU=U\). Restriction therefore gives a representation on \(U\). There is also a quotient representation

\[
g(v+U)=gv+U.
\]

This is well-defined because \(v-v'\in U\) implies \(gv-gv'\in U\). The quotient map is an intertwiner. Kernels and images of intertwiners are invariant: if \(f(v)=0\), then \(f(gv)=gf(v)=0\); and \(gf(v)=f(gv)\) belongs to the image.

The direct sum has action \(g(v,w)=(gv,gw)\). An internal decomposition \(V=U\oplus W\) into invariant spaces gives block diagonal matrices in a basis assembled from bases of \(U\) and \(W\). An invariant subspace alone gives only a block triangular form. The off-diagonal block is the obstruction to finding an invariant complement.

A nonzero representation is **irreducible** if its only invariant subspaces are \(0\) and itself. It is **completely reducible** if it is a direct sum of irreducibles. The zero representation is the empty direct sum.

### A supply of examples

The trivial representation on \(k\) has \(gv=v\). Any homomorphism \(\lambda:G\to k^\times\) gives a one-dimensional representation by \(gv=\lambda(g)v\), and every one-dimensional representation arises this way after choosing a nonzero basis vector. A commutator \(ghg^{-1}h^{-1}\) has image \(1\), since \(k^\times\) is abelian. Hence these homomorphisms are exactly the homomorphisms from \(G^{\mathrm{ab}}=G/[G,G]\) to \(k^\times\). We call them one-dimensional characters.

For \(S_n\), the determinant of a permutation matrix gives the sign representation: even permutations act by \(1\), odd permutations by \(-1\). In characteristic \(2\) these scalars coincide, so sign becomes trivial.

If \(X\) is a finite \(G\)-set, let \(k[X]\) have basis \((e_x)_{x\in X}\), with \(ge_x=e_{gx}\). The action law on \(X\) proves the representation law. In coordinates indexed by \(X\),

\[
(gv)_x=v_{g^{-1}x}.
\]

The inverse is necessary: the coordinate at \(x\) comes from the basis vector moved to \(x\). Taking \(X=G\) with left multiplication gives the **left regular representation**.

For the natural action of \(S_n\) on \(\mathbb C^n\), set

\[
L=\mathbb C(1,\ldots,1),\qquad
A=\{(z_1,\ldots,z_n):\textstyle\sum_i z_i=0\}.
\]

Both spaces are invariant, \(L\) is trivial, and

\[
z=\frac{\sum_i z_i}{n}(1,\ldots,1)
 +\left(z-\frac{\sum_i z_i}{n}(1,\ldots,1)\right)
\]

proves \(\mathbb C^n=L\oplus A\). The representation on \(A\) is called the **standard representation**. Its irreducibility for \(n\geq2\) will be established in Exercise 1.

For a geometric example, let

\[
D_n=\langle r,s:r^n=s^2=1,\ srs=r^{-1}\rangle,
\qquad n\geq3,
\]

where \(D_n\) has order \(2n\). On \(\mathbb R^2\), take

\[
R=\begin{pmatrix}\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta\end{pmatrix},\qquad
S=\begin{pmatrix}1&0\\0&-1\end{pmatrix},\qquad
\theta=\frac{2\pi}{n}.
\]

Rotation by \(n\theta\) is the identity, \(S^2=I\), and multiplying the matrices gives \(SRS=R^{-1}\). Thus \(r\mapsto R\), \(s\mapsto S\) defines a representation. The same matrices act on \(\mathbb R^2\otimes_{\mathbb R}\mathbb C\cong\mathbb C^2\). On this complex plane, \(R\) has the two distinct eigenlines spanned by \((1,-i)\) and \((1,i)\). The reflection exchanges those lines. Any invariant line for the whole group would have to be one of the rotation eigenlines, but neither is reflection-stable. The complex representation of \(D_n\) is therefore irreducible.

### The group algebra viewpoint

The **group algebra** \(k[G]\) has basis \((g)_{g\in G}\), with multiplication extended bilinearly from the group law:

\[
\left(\sum_g a_g g\right)\left(\sum_h b_h h\right)
=\sum_{g,h}a_gb_h(gh).
\]

Associativity and the identity follow from those of \(G\). A representation extends to a unital left module by

\[
\left(\sum_g a_g g\right)v=\sum_g a_g\rho(g)v.
\]

The representation law verifies the module law. Conversely, on a unital \(k[G]\)-module, multiplication by \(g\) is invertible with inverse multiplication by \(g^{-1}\). These operators form a representation. The two constructions undo each other. Intertwiners are exactly module homomorphisms, and invariant subspaces are exactly submodules. In particular, an irreducible representation is a simple \(k[G]\)-module. The regular representation is \(k[G]\) acting on itself on the left.

## 2. Averaging separates invariant pieces

An arbitrary inner product need not respect a given complex action. A finite group lets us repair that by averaging all its translates.

**Proposition 2.1 (invariant inner products).** Every complex representation of \(G\) preserves a positive definite Hermitian inner product. With respect to an orthonormal basis for that inner product, all its matrices are unitary.

**Proof.** Choose any positive definite Hermitian inner product \((\ ,\ )_0\), linear in its first variable. Define

\[
\langle v,w\rangle
=\frac1{|G|}\sum_{g\in G}(gv,gw)_0.
\]

Each summand is linear in \(v\), conjugate-linear in \(w\), and Hermitian. If \(v\neq0\), all \(gv\) are nonzero, so each \((gv,gv)_0\) is positive. Their average is positive. For \(h\in G\),

\[
\langle hv,hw\rangle
=\frac1{|G|}\sum_{g\in G}(ghv,ghw)_0
=\langle v,w\rangle,
\]

because \(g\mapsto gh\) permutes \(G\). Choose an orthonormal basis. Preservation of its standard Hermitian form says that each matrix \(M_g\) satisfies \(M_g^*M_g=I\). This proves the last assertion. \(\square\)

If \(U\) is invariant, its orthogonal complement for this form is invariant too. Indeed, for \(v\in U^\perp\) and \(u\in U\),

\[
\langle hv,u\rangle=\langle v,h^{-1}u\rangle=0.
\]

The linear algebra decomposition \(V=U\oplus U^\perp\) is therefore a decomposition of representations. This already proves splitting over \(\mathbb C\). To obtain the result over other fields, average a linear map instead of a positive form.

*Reference:* [Artin, Theorem 10.3.6].

**Lemma 2.2 (averaging maps).** Suppose the scalar \(|G|\cdot1_k\) is invertible. For representations \(V,W\), the operator

\[
\mathcal R(f)=\frac1{|G|}\sum_{g\in G}
\rho_W(g)f\rho_V(g^{-1})
\qquad(f\in\operatorname{Hom}_k(V,W))
\]

is a linear projection from \(\operatorname{Hom}_k(V,W)\) onto \(\operatorname{Hom}_G(V,W)\).

**Proof.** Conjugating the summands by \(h\), in the sense of composing on the left with \(\rho_W(h)\) and on the right with \(\rho_V(h^{-1})\), replaces \(g\) by \(hg\). Thus \(\rho_W(h)\mathcal R(f)=\mathcal R(f)\rho_V(h)\). Its image consists of intertwiners. If \(f\) is already an intertwiner, every summand equals \(f\), so \(\mathcal R(f)=f\). These two statements give \(\mathcal R^2=\mathcal R\) and the asserted image. \(\square\)

**Theorem 2.3 (Maschke).** Suppose \(k\) has characteristic zero, or characteristic \(p>0\) with \(p\nmid |G|\). Every invariant subspace of a representation over \(k\) has an invariant complement. Every such representation is completely reducible.

**Proof.** Let \(U\subseteq V\) be invariant. Extend a basis of \(U\) to a basis of \(V\), and let \(p_0:V\to V\) fix the basis vectors in \(U\) and send the additional ones to zero. It is a projection onto \(U\). The scalar \(|G|\) is invertible under the hypothesis. Put

\[
P=\mathcal R(p_0)=\frac1{|G|}\sum_g\rho(g)p_0\rho(g^{-1}).
\]

Lemma 2.2 makes \(P\) an intertwiner. Each summand maps \(V\) into \(U\), because \(U\) is invariant. For \(u\in U\), it sends \(u\) to \(u\), because \(g^{-1}u\in U\) and \(p_0\) fixes \(U\). Consequently \(P(V)\subseteq U\) and \(P|_U=1_U\). It follows that \(P(V)=U\) and \(P^2=P\).

The kernel is invariant because \(P\) intertwines. For any \(v\in V\),

\[
v=Pv+(v-Pv),\qquad Pv\in U,\quad v-Pv\in\ker P.
\]

The intersection \(U\cap\ker P\) is zero since \(P\) fixes \(U\). Thus \(V=U\oplus\ker P\).

For complete reducibility, induct on \(\dim V\). The zero case is the empty sum. A nonzero \(V\) has an invariant subspace \(S\) of least positive dimension, which is irreducible. Split it off by the first part. The complement has smaller dimension, so induction decomposes it into irreducibles. \(\square\)

*Reference:* [Gruson–Serganova, Chapter 1, Theorem 3.3 and Proposition 3.12].

The proof uses more than equivariance of \(P\). An average of arbitrary idempotent operators need not be idempotent. For example, let the generator of \(C_2\) swap the coordinates of \(\mathbb C^2\), and let \(p_0=\operatorname{diag}(1,0)\). Its conjugate is \(\operatorname{diag}(0,1)\), so its group average is \(\tfrac12I\), whose square is \(\tfrac14I\). Here idempotence follows because the average has image in the invariant space \(U\) and fixes \(U\).

**Lemma 2.4 (the meaning of complete reducibility).** For a finite-dimensional representation, complete reducibility is equivalent to every invariant subspace having an invariant complement.

**Proof.** The reverse implication follows by the dimension induction just used; that argument needs no assumption on \(G\) or \(k\) once complements exist. For the forward implication, write \(V=S_1\oplus\cdots\oplus S_r\) with all \(S_j\) irreducible, and fix an invariant subspace \(U\). Choose a subset \(J\subseteq\{1,\ldots,r\}\) maximal with

\[
U\cap T=0,\qquad T=\bigoplus_{j\in J}S_j.
\]

If \(i\notin J\), maximality gives a nonzero vector in \(U\cap(T\oplus S_i)\). Its \(S_i\)-component is nonzero, since \(U\cap T=0\). Hence \(S_i\cap(U+T)\neq0\). This intersection is invariant, so irreducibility gives \(S_i\subseteq U+T\). This holds for all missing summands, proving \(V=U+T\). By construction the sum is direct. \(\square\)

### Where the characteristic enters

Let \(G=C_p=\langle t\rangle\) over \(\mathbb F_p\), and let

\[
\rho(t)=J=\begin{pmatrix}1&1\\0&1\end{pmatrix}=I+N.
\]

Here \(N^2=0\), so \(J^m=I+mN\) for every nonnegative integer \(m\), by induction. In particular \(J^p=I\), so this defines a representation. The line \(U=\mathbb F_p e_1\) is invariant.

Any complementary line is spanned by \(v=ae_1+be_2\) with \(b\neq0\). If it were invariant, \(Jv=cv\) for a scalar \(c\). Comparing second coordinates gives \(c=1\). Comparing first coordinates then gives \(a+b=a\), contradicting \(b\neq0\). Thus \(U\) has no invariant complement.

The quotient \(V/U\) and the subrepresentation \(U\) are both trivial. The representation nevertheless fails to be their direct sum. Knowing the subspace and quotient does not determine whether an extension splits. In this example \(|G|=p=0\) in the field, so the averaging division is unavailable.

## 3. Irreducible pieces and the maps between them

**Theorem 3.1 (Schur's lemma).** Let \(S,T\) be irreducible representations over \(k\).

1. Every intertwiner \(S\to T\) is zero or an isomorphism.
2. The algebra \(\operatorname{End}_G(S)\) is a division algebra over \(k\).
3. If \(k\) is algebraically closed, \(\operatorname{End}_G(S)=k\,1_S\).

**Proof.** For a nonzero intertwiner \(f:S\to T\), its invariant kernel cannot be \(S\), so it is zero. Its invariant image is nonzero, so it is all of \(T\). Hence \(f\) is bijective. Its inverse also intertwines: the identity \(f\rho_S(g)=\rho_T(g)f\) gives \(\rho_S(g)f^{-1}=f^{-1}\rho_T(g)\). In particular every nonzero endomorphism is invertible in the endomorphism algebra, proving the first two assertions.

For the third, take \(a\in\operatorname{End}_G(S)\). Since \(S\neq0\) is finite-dimensional and \(k\) is algebraically closed, \(a\) has an eigenvalue \(\lambda\in k\). The endomorphism \(a-\lambda1_S\) has nonzero kernel and therefore cannot be an isomorphism. The first assertion makes it zero. Thus \(a=\lambda1_S\). Scalar maps always intertwine, giving equality. \(\square\)

Schur's lemma does not require the characteristic hypothesis in Maschke's theorem. It controls maps between representations already known to be irreducible.

*References:* [Schur, §2, statements I–II]; [Stacks, Tag 0746](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html#brauer-lemma-simple-module) for the division-ring statement for simple modules.

### Abelian groups

**Corollary 3.2.** Every irreducible representation of a finite abelian group over an algebraically closed field is one-dimensional. In particular this holds when the characteristic does not divide the group order.

**Proof.** If \(G\) is abelian, each operator \(\rho(g)\) commutes with every \(\rho(h)\), so it lies in \(\operatorname{End}_G(S)\). Theorem 3.1 makes each operator scalar. Every one-dimensional subspace of \(S\) is then invariant. Irreducibility forces \(\dim S=1\). Conversely, a one-dimensional representation is irreducible because a line has no nonzero proper subspace. \(\square\)

The dimension assertion survives in the excluded characteristics; complete reducibility may fail there. These are different conclusions.

*Reference:* [Schur, §2, statement III].

### A real irreducible that splits over the complex numbers

Let the generator of \(C_3\) act on \(\mathbb R^2\) by

\[
R=\begin{pmatrix}-\tfrac12&-\tfrac{\sqrt3}{2}\\
\tfrac{\sqrt3}{2}&-\tfrac12\end{pmatrix}.
\]

Its characteristic polynomial is \(x^2+x+1\), which has no real root. An invariant real line would give a real eigenvector, so this representation is irreducible. On \(\mathbb C^2\), however, the vectors \((1,-i)\) and \((1,i)\) have eigenvalues \(\zeta=e^{2\pi i/3}\) and \(\zeta^{-1}\). They span two invariant lines, giving a decomposition into two distinct one-dimensional representations.

Write

\[
K=\begin{pmatrix}0&-1\\1&0\end{pmatrix},\qquad
R=-\tfrac12I+\tfrac{\sqrt3}{2}K.
\]

The commuting algebra is \(\{aI+bK:a,b\in\mathbb R\}\cong\mathbb C\); the calculation is in Exercise 2. Thus the scalar conclusion of Schur's lemma would be false over \(\mathbb R\), even though the division-algebra conclusion remains true.

## 4. What is unique in a decomposition?

From now through this section, assume \(k\) is algebraically closed and \(|G|\) is invertible in \(k\). Maschke gives

\[
V\cong\bigoplus_{i=1}^r S_i^{\oplus m_i},
\]

where the \(S_i\) are pairwise nonisomorphic irreducibles and \(m_i>0\).

**Corollary 4.1 (multiplicities).** For each irreducible \(S\), its multiplicity in \(V\) is

\[
m_S=\dim_k\operatorname{Hom}_G(S,V).
\]

Consequently the irreducible isomorphism classes occurring in \(V\), and their multiplicities, are independent of the decomposition.

**Proof.** Taking components of a map into a finite direct sum gives

\[
\operatorname{Hom}_G(S,V)
\cong\bigoplus_i\operatorname{Hom}_G(S,S_i)^{\oplus m_i}.
\]

Schur's lemma says that a term is zero unless \(S\cong S_i\). If they are isomorphic, composing with one fixed isomorphism identifies that term with \(\operatorname{End}_G(S)=k\). Thus its dimension is exactly the number of copies of \(S\). The left-hand space depends only on \(S\) and \(V\), proving independence. \(\square\)

Over a field that is not algebraically closed, the same argument, for a completely reducible \(V\), gives instead

\[
\dim_k\operatorname{Hom}_G(S,V)
=m_S\dim_k\operatorname{End}_G(S).
\]

For the real rotation representation in the preceding example, \(S=V\) has multiplicity \(1\), but \(\operatorname{Hom}_G(S,V)\) has real dimension \(2\). The distinction is essential.

The individual irreducible subspaces are usually not determined. For instance, in \(S\oplus S\), every graph \(\{(v,av):v\in S\}\), \(a\in k\), is another subrepresentation isomorphic to \(S\). We need a larger subspace that includes all copies of the same type.

Define the **isotypic component** of type \(S\) by

\[
V[S]=\sum_{f\in\operatorname{Hom}_G(S,V)}\operatorname{im}f.
\]

This is an invariant subspace defined without selecting a decomposition. A nonzero \(f\) is injective by the kernel argument in Schur's lemma, so its image is a copy of \(S\). Conversely, an isomorphism from \(S\) onto any copy of \(S\) in \(V\), followed by inclusion, is such a map.

**Proposition 4.2 (isotypic decomposition).** In any decomposition of \(V\) into irreducibles, \(V[S]\) is exactly the direct sum of the summands isomorphic to \(S\). Hence

\[
V=\bigoplus_{[S]}V[S],
\]

with only finitely many nonzero components. The subspaces \(V[S]\) and the projections onto them along the other components are canonical. Every intertwiner \(a:V\to V'\) sends \(V[S]\) into \(V'[S]\).

**Proof.** Fix a decomposition \(V=\bigoplus_j T_j\), with component projections \(\pi_j\). For \(f:S\to V\), the map \(\pi_jf\) intertwines. If \(T_j\not\cong S\), Schur's lemma makes it zero. Thus every such image lies in the sum of the summands of type \(S\). Each summand of that type is itself the image of an intertwiner from \(S\), proving the reverse inclusion. Grouping the summands by type proves the direct sum formula.

Because \(V[S]\) was defined intrinsically, all these grouped subspaces are independent of the decomposition. The direct sum determines a unique linear projection \(e_S\) with image \(V[S]\) and kernel the sum of the other components. Both subspaces are invariant, so the projection intertwines. Finally \(af:S\to V'\) intertwines for every \(f:S\to V\); summing its images proves \(a(V[S])\subseteq V'[S]\). \(\square\)

Thus uniqueness has two levels. Multiplicities are unique numbers. Isotypic components are unique subspaces. Splitting a component into its individual copies requires choices. The projection \(e_S\) commutes with every equivariant endomorphism, since all such endomorphisms preserve every component.

## 5. A cyclic regular representation worked out

Let \(G=C_n=\langle t\rangle\) over \(\mathbb C\), let \(\omega=e^{2\pi i/n}\), and use the basis \(e_j=t^j\), \(0\leq j<n\), of \(\mathbb C[C_n]\). Indices are read modulo \(n\). The regular action is \(te_j=e_{j+1}\).

For \(0\leq a<n\), define

\[
v_a=\sum_{j=0}^{n-1}\omega^{-aj}e_j.
\]

Reindexing with \(\ell=j+1\) gives

\[
tv_a=\sum_\ell\omega^{-a(\ell-1)}e_\ell
=\omega^av_a.
\]

Each \(v_a\) is nonzero, since its \(e_0\)-coefficient is \(1\). The \(n\) eigenvalues \(\omega^a\) are distinct, so the eigenvectors are independent. They therefore form a basis, and

\[
\mathbb C[C_n]=\bigoplus_{a=0}^{n-1}\mathbb C v_a,
\qquad \lambda_a(t^j)=\omega^{aj}.
\]

Every one-dimensional character is on this list: its value at \(t\) has \(n\)th power \(1\), and that value determines it. Corollary 3.2 shows that these are all the irreducibles. Each occurs once in the regular representation.

For \(n=4\), this gives eigenvalues \(1,i,-1,-i\). In the order \(e_0,e_1,e_2,e_3\), the corresponding vectors are

\[
(1,1,1,1),\quad(1,-i,-1,i),\quad
(1,-1,1,-1),\quad(1,i,-1,-i).
\]

This example prepares for “Fourier analysis on finite abelian groups,” which develops character orthogonality, inversion, and duality. Here the calculation serves to identify the irreducible pieces of a concrete representation. For arbitrary finite groups, [Characters and the orthogonality relations](RT-FIN-02.md) will provide numerical methods for finding multiplicities.

## 6. Exercises with complete solutions

Try each exercise before reading its solution. The last two use Schur's lemma to turn structural questions into questions about scalars and projections.

### Exercise 1 — Easy: the standard representation

Show that the permutation representation of \(S_n\) on \(\mathbb C^n\) is the direct sum of the trivial representation and the standard representation. Prove that the standard representation is irreducible for \(n\geq2\).

**Solution.** Coordinate permutations preserve both \(L=\mathbb C(1,\ldots,1)\) and \(A=\{z:\sum_i z_i=0\}\). The decomposition in Section 1 shows their sum is all of \(\mathbb C^n\). If \(c(1,\ldots,1)\in A\), then \(nc=0\), so \(c=0\). Hence the sum is direct and \(L\) is trivial.

Let \(0\neq U\subseteq A\) be invariant, and choose \(z\in U\setminus\{0\}\). Not all its coordinates are equal: otherwise the sum-zero condition would make it zero. Choose \(i,j\) with \(z_i\neq z_j\). Then

\[
z-(ij)z=(z_i-z_j)(e_i-e_j)\in U.
\]

Thus \(e_i-e_j\in U\). Permuting indices gives every \(e_a-e_b\in U\). The vectors \(e_a-e_n\), \(1\leq a<n\), span \(A\), since any \(z\in A\) equals \(\sum_{a<n}z_a(e_a-e_n)\). Therefore \(U=A\), proving irreducibility. For \(n=2\), \(A\) is the sign line. For \(n=1\), \(A=0\), so it is not irreducible under our convention.

### Exercise 2 — Easy: a real commuting algebra

Compute \(\operatorname{End}_{C_3}(\mathbb R^2)\) for the rotation representation in Section 3, and identify it as a real algebra.

**Solution.** Since \(R=-\tfrac12I+\tfrac{\sqrt3}{2}K\), a real matrix commutes with \(R\) exactly when it commutes with \(K\). For \(B=\begin{pmatrix}u&v\\w&x\end{pmatrix}\),

\[
BK=\begin{pmatrix}v&-u\\x&-w\end{pmatrix},\qquad
KB=\begin{pmatrix}-w&-x\\u&v\end{pmatrix}.
\]

Equality says \(x=u\) and \(w=-v\). Thus \(B=aI+bK\) for real \(a,b\). Since \(K^2=-I\), the map \(a+bi\mapsto aI+bK\) is a bijective real-linear map preserving multiplication and the identity. It is an algebra isomorphism from \(\mathbb C\) onto the commuting algebra. Explicitly, for \((a,b)\neq(0,0)\),

\[
(aI+bK)^{-1}=\frac{aI-bK}{a^2+b^2}.
\]

This directly verifies the division-algebra conclusion.

### Exercise 3 — Medium: splitting and characteristic

Show that Maschke's conclusion fails for \(C_p\) over \(\mathbb F_p\), including \(p=2\). Explain why it holds for every finite group over every field of characteristic zero.

**Solution.** Use \(J=I+N\) from Section 2. The formula \(J^p=I+pN=I\) holds also for \(p=2\). A line complementary to \(\mathbb F_p e_1\) has a generator \(ae_1+be_2\), \(b\neq0\). Invariance would give \(Jv=cv\); the second coordinate forces \(c=1\), and the first forces \(b=0\), a contradiction. Lemma 2.4 therefore also shows that this representation is not completely reducible.

In a characteristic-zero field, a positive integer times \(1_k\) is nonzero. Every nonzero element of a field is invertible, so \(|G|^{-1}\) exists for every finite \(G\). Theorem 2.3 applies. This argument requires neither algebraic closure nor an inner product.

### Exercise 4 — Medium: a restriction on the centre

Prove that a finite group admitting a faithful irreducible complex representation has cyclic centre.

**Solution.** Let \(\rho:G\to\operatorname{GL}(V)\) be faithful and irreducible. For \(z\in Z(G)\), \(\rho(z)\) commutes with every group operator. Schur's lemma gives \(\rho(z)=\lambda(z)I\). The map \(\lambda:Z(G)\to\mathbb C^\times\) is a homomorphism, and it is injective: \(\lambda(z)=1\) implies \(\rho(z)=I\), hence \(z=1\) by faithfulness.

Let \(H=\lambda(Z(G))\). It is finite. Choose a positive integer \(N\) divisible by the orders of all its elements. Then every element of \(H\) is an \(N\)th root of unity, so \(H\subseteq\langle e^{2\pi i/N}\rangle\). To see explicitly how the elementary cyclic-group fact applies, let

\[
B=\{m\in\mathbb Z:e^{2\pi im/N}\in H\}.
\]

This is a subgroup of \(\mathbb Z\) containing \(N\mathbb Z\). By the subgroup theorem for \(\mathbb Z\), \(B=d\mathbb Z\) for some positive \(d\). Consequently \(H\) is generated by \(e^{2\pi id/N}\). The injection identifies \(Z(G)\) with this cyclic group. Faithfulness is used precisely in making the scalar homomorphism injective.

### Exercise 5 — Hard: an isotypic projection

Let \(V\) be a complex representation and \(W\subseteq V\) irreducible. Show that its isotypic component is the sum of all subrepresentations isomorphic to \(W\). Construct an ordinary linear projection whose group average has that entire component as its image.

**Solution.** Write \(S\) for the sum of all copies of \(W\) in \(V\). It is invariant. Every nonzero map \(W\to V\) is injective, and every copy is the image of such a map. Thus \(S=\sum_f\operatorname{im}f\). In fact, if \(f_1,\ldots,f_m\) is a basis of \(\operatorname{Hom}_G(W,V)\), then \(S=\sum_{a=1}^m\operatorname{im}f_a\): the image of any linear combination of these maps lies in that sum.

Choose an irreducible decomposition \(V=\bigoplus_j T_j\). For every \(f:W\to V\), its component in \(T_j\not\cong W\) is zero by Schur's lemma. Hence \(S\) is contained in the sum of the \(T_j\) isomorphic to \(W\). Each such summand is a copy of \(W\), so equality holds. This identifies \(S\) with the isotypic component and shows it is independent of the chosen decomposition.

Extend a basis of \(S\) to a basis of \(V\), and let \(q_0\) be the projection onto \(S\) given by that basis. Set

\[
Q=\frac1{|G|}\sum_g\rho(g)q_0\rho(g^{-1}).
\]

As in the proof of Maschke, \(Q\) intertwines, maps into \(S\), and fixes \(S\). Therefore \(Q^2=Q\) and \(\operatorname{im}Q=S\). Its kernel is invariant. More precisely, if \(T_j\not\cong W\), each component of \(Q|_{T_j}:T_j\to S\) in a decomposition of \(S\) into copies of \(W\) vanishes by Schur's lemma. Thus \(Q\) is zero on every other isotypic component. It is the canonical isotypic projection from Proposition 4.2, regardless of the initial basis choice.

A projection onto \(W\) alone would not do this when \(S\neq W\). Every conjugate of that projection still maps into the invariant space \(W\) and fixes \(W\); its average has image exactly \(W\). To project onto the whole isotypic component, the initial projection must have that whole component as its image.

## 7. What this lesson does not prove

The linear algebra and elementary algebra facts below are assumed from the prerequisites. The references specify them independently of any later representation-theory lesson.

- An independent set in a finite-dimensional vector space extends to a basis [Artin, Proposition 3.4.16(a)]. Eigenvalues are roots of the characteristic polynomial [Artin, Corollary 4.5.9]. Over an algebraically closed field such a polynomial of positive degree has a root; over \(\mathbb C\) the eigenvalue conclusion is [Artin, Proposition 4.5.14(b)]. Eigenvectors with distinct eigenvalues are independent [Artin, Proposition 4.6.5].
- A finite-dimensional positive definite Hermitian space has an orthonormal basis by Gram–Schmidt [Artin, §8.4, Gram–Schmidt procedure], and \(V=U\oplus U^\perp\) for every subspace \(U\) [Artin, Corollary 8.5.1]. We use the convention linear in the first variable; [Artin] uses the conjugate convention.
- A quotient by a normal subgroup is a group with its canonical quotient homomorphism [Artin, Theorem 2.12.2]. Every subgroup of \(\mathbb Z\) is \(d\mathbb Z\), including the zero case [Artin, Theorem 2.3.3]. The characteristic of a field is zero or a prime [Artin, Lemma 3.2.10].

Two general algebra results provide context, but none of our finite-group proofs depends on them.

- For a finite-dimensional unital \(k\)-algebra \(A\), a simple module exists if \(A\neq0\); every nonzero unital \(A\)-module contains a simple submodule; every simple \(A\)-module is finite-dimensional over \(k\); and its endomorphism ring is a division ring [Stacks, Tag 0746](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html#brauer-lemma-simple-module). Here “simple” means nonzero with no nonzero proper submodule.
- The Brauer group of an algebraically closed field is zero [Stacks, Tag 074M](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html#brauer-lemma-brauer-algebraically-closed). Its proof establishes that a finite-dimensional central division algebra over such a field is the field itself. The general theory of central simple algebras is outside this lesson.

“Groups with operators” treats complete reducibility and isotypic components for modules in greater generality. “Semisimple rings and Wedderburn's theorem” treats the structure of general semisimple rings. Here averaging gives the finite-group splitting theorem directly, and Schur's lemma supplies exactly the uniqueness statements needed for representations.

## References

- **[Stacks]** The Stacks project, *Brauer groups*, [Tag 0746](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html#brauer-lemma-simple-module) and [Tag 074M](https://kokunoyumeto.github.io/stacks-zh-hans-cn/en/brauer.html#brauer-lemma-brauer-algebraically-closed), read in Clanker Stacks.
- **[Schur]** I. Schur, *Neue Begründung der Theorie der Gruppencharaktere*, Sitzungsberichte der Preussischen Akademie der Wissenschaften, Physikalisch-Mathematische Klasse, 1905, §2, statements I–III. Reprinted as work 7 in *Gesammelte Abhandlungen*, edited by A. Brauer and H. Rohrbach, Springer, 1973.
- **[Gruson–Serganova]** C. Gruson and V. Serganova, *A Journey Through Representation Theory: From Finite Groups to Quivers via Algebras*, Universitext, Springer, 2018, Chapter 1, §§1–3.
- **[Artin]** M. Artin, *Algebra*, second edition, Pearson, 2011, §§10.1–10.3 and 10.7; the prerequisite results are located individually above.
