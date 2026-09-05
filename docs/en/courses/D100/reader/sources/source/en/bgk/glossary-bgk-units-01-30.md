---
title: "Terminology Guide to Bundles, Sheaves and Cohomology"
stable_id: br-bgk-2019-glossary-01-30
language: en
source_course: "Bündel, Garben und Kohomologie (Osnabrück 2019-2020)"
source_author: "Holger Brenner"
editorial_scope: "Connective glossary for Units 1–30, adapted for English readers; not an addition to the source text"
license: "CC BY-SA 4.0 for this glossary and its connective notes; source-component licences remain in force as recorded in the edition credits"
translation_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
non_endorsement: "Independent edition and glossary; no endorsement by Holger Brenner, Wikiversity, the Wikimedia Foundation or the source institutions is implied."
---

# Terminology guide {#br-bgk-2019-glossary-01-30}

This guide connects German terms with their use in Units 1–30. It adapts
the independent Indonesian edition's connective glossary for English
readers. Synonymous translations do not denote new mathematical objects:
read them together with the definitions, hypotheses and notation in the
relevant unit. The preferred forms here support cross-unit searching
without changing formulae or wording inside source quotations.

## Objects that must be distinguished {#br-bgk-2019-glossary-01-30-objek}

| Source term | English equivalent | Reading guidance |
|---|---|---|
| *Bündel*; *Garbe*; *Prägarbe* | bundle; sheaf; presheaf | Bundle and sheaf are different source terms. The sheaf of sections of a bundle connects the two viewpoints. |
| *Halm*; *Faser* | stalk; fibre | For a sheaf of modules, the stalk at a point differs from the fibre obtained by passing to the residue field. |
| *Schnitt*; *Durchschnitt* | section; intersection | A section of a sheaf or bundle is not a set-theoretic intersection. When splitting a surjection, a section means a right inverse. |
| *Strukturgarbe*; *Modulgarbe* | structure sheaf; sheaf of modules | The scalar structure matters: an $\mathcal O_X$-module is a module over the structure sheaf. |
| *Homomorphismenmodul*; *Homomorphismengarbe* | module of homomorphisms; sheaf of homomorphisms | Unit 13 also uses **global homomorphism module** to distinguish $\operatorname{Hom}$ from the sheaf $\mathcal Hom$. |
| *Garbenmorphismus*; *Garbenhomomorphismus* | sheaf morphism; sheaf homomorphism | The second term emphasises the group or module structure being preserved; do not drop that structure from a statement. |
| *quasikohärent*; *kohärent* | quasi-coherent; coherent | Coherence includes additional finiteness conditions under the relevant definition; the two properties are not interchangeable. |
| *Hyperebene*; *Hyperfläche* | hyperplane; hypersurface | A hyperplane is linear, whereas a hypersurface may have degree greater than one. |

## Corresponding terms across units {#br-bgk-2019-glossary-01-30-varian}

| Source term | Preferred form and variants | Limits of meaning |
|---|---|---|
| *Vergarbung* | **sheafification**; forming the associated sheaf | The construction of the sheaf associated to a presheaf, not an arbitrary sheaf construction. |
| *Einheit*; *Einheitengarbe* | **unit**; **sheaf of units** | A unit is an element with a multiplicative inverse, not just the identity element $1$. “Unit 20” instead names a numbered part of the course. |
| *Rang* | **rank** | For a locally free sheaf or bundle, this means its rank, not its degree. |
| *Einschränkung*; *Restriktion* | **restriction** | Restricting an object or map to the specified subspace. In $\mathcal F|_U$, restriction is not a boundedness property. |
| *Restriktionsabbildung* | **restriction map** | Where the source emphasises the algebraic structure, use **restriction homomorphism**. |
| *Integritätsbereich* | **integral domain** | A nonzero commutative ring without zero divisors; “integral” here does not refer to integration. |
| *Restklassenring* | **quotient ring**; factor ring; residue-class ring | A ring modulo an ideal. Do not confuse this with *Quotientenkörper*, meaning **field of fractions**. |
| *Restklassenmodul*; *Restklassengruppe* | **quotient module**; **quotient group** | “Factor” and “residue-class” terminology may describe the same quotient construction. Modules, groups and rings must still be distinguished. |
| *Funktionenkörper* | **function field** | The Indonesian variants *lapangan fungsi* and *medan fungsi* denote the same field; a **vector field** is a different notion. |
| *Twist*; *getwistete Strukturgarbe* | **twist**; **twisted structure sheaf** | A degree twist or a twist by an invertible sheaf, not a geometric rotation or dualisation. |
| *glatt* | **smooth** | Geometric smoothness is not automatically the same as *regulär* (**regular**) without suitable hypotheses on the base. |
| *feine Monomgraduierung* | **fine monomial grading** | “Fine” means a more detailed grading, not geometric smoothness. |
| *welk*; *welke Garbe* | **flasque** or **flabby**; **flasque sheaf** | Every restriction map is surjective. *Azyklisch* means **acyclic**; acyclic and flasque are not synonyms. |
| *Überdeckung* | **cover**; covering | A family of subsets covering a space. “Open”, “affine” and “finite” remain mathematical qualifications. |
| *affine Standardüberdeckung* | **standard affine cover** | The cover used in the discussion of projective space; a standard cover is not an arbitrary cover. |
| *Überlagerung* | **covering map** | A covering-space map differs from a covering family of open sets. |
| *projektiv* | **projective** | The Indonesian spellings *projektif* and *proyektif* do not denote different objects; English uses projective in both courses. |
| *Einbettung* | **embedding** | Check the category and the properties of the map. An embedding of groups or modules does not automatically carry the properties of a scheme embedding. |
| *beringter Raum* | **ringed space** | A topological space equipped with a sheaf of rings. The earlier Indonesian wording *ruang berdering* has this defined meaning; *ruang bergelanggang* is that edition's preferred term. |

## Terms in the later units {#br-bgk-2019-glossary-01-30-lanjutan}

| Source term | Equivalent and guidance |
|---|---|
| *Kähler-Differentiale*; *Tangentialgarbe*; *Kotangentialgarbe* | **Kähler differentials**; **tangent sheaf**; **cotangent sheaf**. Preserve the distinctions among a sheaf, a module and a bundle. |
| *kanonische Garbe*; *antikanonische Garbe* | **canonical sheaf**; **anticanonical sheaf**. Do not omit the prefix anti-. |
| *Syzygiengarbe* | **syzygy sheaf**. The Indonesian spellings *syzygy* and *sizigi* refer to the same relation construction. |
| *Weildivisor*; *Hauptdivisor* | **Weil divisor**; **principal divisor**. A divisor here is a geometric object, not a divisor of an integer. |
| *Nullstellendivisor*; *Polstellendivisor* | The **divisor of zeros** and **divisor of poles** of a function. The former records zeros; it need not itself be the zero divisor. |
| *injektive Auflösung*; *rechtsabgeleiteter Funktor* | **injective resolution**; **right-derived functor**. A resolution is the whole complex, not a single injective map. |
| *Čech-Kohomologie*; *Čech-Kozykel*; *Čech-Koränder* | **Čech cohomology**; **Čech cocycles**; **Čech coboundaries**. Cohomology classes are cocycles modulo coboundaries. |
| *lange exakte Kohomologiesequenz* | **long exact cohomology sequence**; long exact sequence in cohomology. Both word orders retain the requirement of **exactness**. |
| *kurze exakte Sequenz* | **short exact sequence**. A sequence is not an *Ordnung*, an order in order theory. |
| *lineares System*; *volles lineares System*; *basispunktfrei* | **linear system**; **complete linear system**; **base-point-free**. Completeness and base-point-freeness are different properties. |
| *Verzweigungsindex*; *Verzweigungsordnung* | **ramification index**; **ramification order**. Unit 29 explains the naming difference between witnesses; both refer there to the same local ramification exponent. |
| *Serre-Dualität*; *Euler-Charakteristik*; *Satz von Riemann-Roch* | **Serre duality**; **Euler characteristic**; **Riemann–Roch theorem**. The names do not replace the hypotheses or the scope of the source statements. |

## Notation and origin of this guide {#br-bgk-2019-glossary-01-30-notasi}

Prose terminology does not change source notation. For example, an
**image** may still be written with the source operator `bild`, and the
word **spectrum** does not require replacing `Spek` by `Spec` inside a
formula. Differences in indices, equality signs, isomorphisms and
hypotheses are not vocabulary variants.

This connective guide is based on Holger Brenner's course and the
terminology decisions of the Indonesian edition, adapted to English.
AI-assisted preparation: **OpenAI Codex gpt-5.6-sol, Ultra.** This
connective text is licensed under **CC BY-SA 4.0**; every source component
retains its own credits and licence. This is not an official guide from
the source author or institutions and does not imply their endorsement.
