# Attribution and change notice

## Original work

**The Open Logic Text** and the Open Logic Project source corpus are by
[The Open Logic Project](https://openlogicproject.org/people/). The official
source repository is <https://github.com/OpenLogicProject/OpenLogic>. The source
used for this Indonesian adaptation is frozen at commit
`9620cc73f9c8e0ad003c514a5d3748f29611c4c0`.

The original is licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
The repository's full licence text remains at `LICENSE.md`.

## Adaptation

This maintained mirror translates the frozen English corpus into Bahasa
Indonesia (`id-ID`). It changes reader-facing prose, headings, theorem and
problem language, captions, navigation, metadata, and localized automatic
labels. It preserves mathematical formulas, identifiers, source paths, LaTeX
structure, labels, references, citations, proof structure, and assets except
where an exact source defect is explicitly corrected and ledgered.

The current checkpoint covers every ordered closure unit `OLP-0001` through
`OLP-0722` (722/722 files) at the frozen source commit. It is the complete
Indonesian adaptation of that declared frozen closure. This completeness claim
does not imply Open Logic Project endorsement, native-speaker certification,
or coverage of later upstream commits.

Exact source corrections currently include:

- the natural-number convention is made explicit as including zero;
- an undefined branch carrier is replaced by the declared carrier;
- a subtree premise is made nonempty to agree with the source's tree
  definition;
- an undefined identity symbol is replaced by `\Id{\Nat}`;
- a reflexive-closure symbol is renamed locally to avoid collision with the
  source's transitive-closure notation;
- a modular-equivalence variable scope, a square-root zero case, and a
  left-inverse empty-domain counterexample are repaired.
- Size-of-sets pairing, diagonalization, reduction, variable, and duplicate-
  label defects are repaired at exact paths.
- Arithmetization repairs rational-subtraction orientation, the nonempty-set
  premise in a supremum proof, real-zero notation, and exact Cauchy-appendix
  type/exposition defects.
- Infinite Sets repairs the malformed intermediate Schröder--Bernstein
  consequent and supplies the omitted range-inclusion argument.
- Propositional syntax and semantics repair formation-sequence identity and
  index scope, a fixed-formula rebinding, implication punctuation, and the
  direction of semantic consequence.
- The Proof Systems overview repairs sequent endpoints, tableau rule labels,
  finite-assumption quantification, and the scope of axiomatic derivability.
- Sequent Calculus repairs four exchange-side labels, two omitted De Morgan
  negations, a mismatched-context conjunction proof, two soundness sequents,
  and two proof-system descriptions.
- Natural Deduction repairs quantifier-rule scope and eigenvariable wording,
  several proof-rule labels and side conditions, valuation-versus-structure
  scope, an omitted negation-elimination case, and malformed identity syntax.
- Tableaux repairs the chapter's editorial scope; distinguishes first-order
  structures from propositional valuations; makes the closed-term condition
  explicit; repairs malformed signed-formula, tableau-branch, compactness,
  consistency, quantifier-soundness, and identity-rule expressions; and
  corrects exact line references, indices, polarity signs, and metavariable
  drift where the frozen source conflicts with its own rules or proof context.
- Axiomatic Deduction repairs formula markers and axiom references; restores
  closed-term and QR eigenconstant conditions; separates propositional from
  first-order carriers; and corrects deduction-theorem, compactness, soundness,
  and identity claims where the frozen source conflicts with its own rule
  statements or proof obligations.
- Completeness repairs closed-term carriers and quantifier ranges, Henkin and
  Lindenbaum scope, Truth-Lemma matrices, quotient representatives, compactness
  edge cases, and the expanded-language carrier used in downward
  Löwenheim--Skolem. Two upstream proof-scope/statement-precision risks remain
  expressly preserved rather than silently altered.
- The First-Order Logic introduction repairs malformed quantifier scopes and
  brackets, predicate-versus-constant arity, an out-of-domain assignment
  example, and an `\Atom` delimiter. Seven broader exposition risks remain
  preserved verbatim for the eventual concise upstream report.
- First-Order Logic syntax repairs a malformed tag closure, unmatched or
  misplaced delimiters, formation-sequence indices and induction measures,
  language subscripts, and syntactic-identity notation. It also localizes the
  reader-facing induction-case labels and substitution side-condition token.
- First-Order Logic semantics repairs arity-neutral function interpretation,
  malformed satisfaction clauses and delimiters, variable and witness indices,
  assignment bases, duplicate carriers, extensionality premises, and exact
  free-variable conditions. One Indonesian exclusive-alternative construction
  was corrected independently; two low-priority upstream clarification
  candidates remain explicitly preserved.
- Theories and Their Models repairs a missing strict-order qualifier, one bare
  object-language variable marker, two missing formula parentheses, and one
  malformed prose clause. The Indonesian chapter title and pure-set
  predication were independently clarified; valid uppercase token syntax was
  preserved and the contrary audit findings explicitly retracted.
- Beyond First-Order Logic repairs an atomic relation-variable macro, restores
  the declared postfix successor in the injectivity axiom, and restores the
  declared binder type in the higher-order lambda explanation. It preserves
  without silent repair a duplicate expanded intuitionistic schema and an
  irrational-power witness whose irrationality is not established locally.
  Three earlier concerns about iterated-binder ellipsis, the comprehension
  restriction, and the S5 frame presentation were explicitly retracted.
- Model Theory Basics requires nonempty substructure domains; restores
  predicate/function argument scope, the primed-structure interpretation, and
  a missing parenthesis in the isomorphism proof; corrects back-and-forth
  parity, free-variable and sequence-length scope, and finite-type wording; and
  closes the omitted empty-map and already-in-domain DLO proof cases. It also
  corrects one duplicated Indonesian phrase, three false `bertempat` arity
  surfaces, three raw `-structure` fallbacks, and three token/adjective-order
  surfaces. The parameterized-definability and partial-function-definedness
  risks remain preserved; three false positives are explicitly retracted.
- Models of Arithmetic corrects missing proof-code variables, false converses
  about nonstandard elements, incomplete compactness/countability reasoning,
  zero-predecessor and largest-block claims, an invalid transferred bijection,
  and the scope of Tennenbaum's theorem. It preserves exact informal-typing
  and stale-metadata risks for later upstream reporting.
- Interpolation and Lindstr\"om correct primed-language constructions,
  malformed language and satisfaction notation, wrong transported carriers,
  sentence/formula mismatches, negated-satisfaction syntax, finite
  representative selection, and the missing normal-logic hypothesis. The
  retained minimal-union compatibility gap remains explicitly adverse.
- Recursive Functions and Computability Theory correct projection and
  recursion indices, sequence/tree boundary cases, diagonal and normal-form
  variables, reduction directions, and partial-function equalities. The
  Indonesian locale now renders `computably enumerable` as `terenumerasi
  secara komputabel`; mathematical/program identifiers remain invariant.
- Final render review corrected three duplicated synthetic cross-reference
  labels and one missing paragraph boundary. These are adaptation/build
  corrections, not upstream mathematical changes.
- Turing Machines and Incompleteness repair exact transition/configuration,
  coding, binder, index, proof-predicate, representability, consistency,
  theorem-scope, citation, and partial-equality defects where the frozen source
  conflicts with its own definitions or proofs. Uncertain sequence/path,
  aggregate-QR, beta-remainder, formula-notation, existential-scope,
  meta-constant, and coded-relation issues remain explicitly adverse for the
  bounded post-closure upstream report rather than being silently rewritten.

The full adverse history and evidence are in
`TERMINOLOGY_AND_ADVERSE_LEDGER.csv` and the dated independent-review receipts.

This adaptation is independent. Open Logic Project has not endorsed, certified,
or sponsored it, and no such endorsement is implied.

No DOI has been minted for this incomplete checkpoint. The durable
language-and-corpus DOI architecture is recorded in
`..\..\..\_control\INDONESIAN_CORPUS_DOI_AND_DISCOVERABILITY_PROTOCOL_20260813.md`;
minting begins only after complete-draft closure at 722/722.
