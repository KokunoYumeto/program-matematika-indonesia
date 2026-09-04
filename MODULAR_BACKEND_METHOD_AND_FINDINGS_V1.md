# From Independent Corpus Backends to a Shared Modular Curriculum Layer

## Purpose

The Indonesian mathematics program deliberately did not impose one backend design before translation began. Each corpus lane developed a course-native representation suited to its source format, pedagogical structure, production risks, and intended learner experience. The resulting variation was intentional: it allowed multiple approaches to stable identity, translation state, exercises, prerequisites, provenance, accessibility, deterministic rebuilding, and learner delivery to be tested against real books rather than designed only in the abstract.

The convergence step comes afterward. The objective is not to replace the native backends with one large universal database. It is to compare what the independent lanes actually produced, retain the strongest reusable patterns, and expose a small common capsule that a central curriculum, another language edition, or an offline learner interface can consume.

This was a comparative engineering audit, not a controlled scientific experiment. The corpora differed in subject, size, source format, completion stage, and intended use. No common implementation was imposed, no lane was manipulated for comparison, and family scores were omitted where numerical ranking would conceal those scope differences.

## Evidence boundary

The audited snapshot was bound to cursor 666,831 and its matching sidecar SHA-256 `3698288452C32FC518DB08F924D39DCE834E6726E60DB86B214DA6129EFBE279`. The coordinating registry was registry 181, 25,811 bytes, SHA-256 `2173F797C2BD494461E4FF04D3C5013F01A7BFF61E73E25C905884E51A67F652`.

The comparison used native manifests, validators, readers, current manager data, and public bytes. It was read-only: no production task was contacted or controlled, and no repository, publication, corpus, or access state was changed.

The program contains **40 curriculum roles**. **Thirty-two mapped owner tasks** cover 39 of them, while C80, Open Logic, is complete without a currently mapped task. Because the CLP, Lebl, and Judson implementations each serve several roles, those 40 roles produced **33 independent native implementation families**, not 40 separate schemas. The manager federation is an additional synthesis layer and is not counted as a thirty-fourth native family.

The comparison used ten axes:

- stable identity and granularity;
- typed semantic and prerequisite relations;
- source, target, provenance, rights, and correction evidence;
- translation state;
- assets and accessibility;
- deterministic replay;
- reversible exchange;
- learner and runtime use;
- demonstrated cross-course reuse;
- maintenance burden.

Record volume, schema validation, and central admission were not treated as proof of learner usefulness.

## Results from the 33 native backend families

1. **A00 — Prealgebra.** This lane produced a full locale-neutral and locale-specific curriculum graph with 519,678 records, a curated graph of 35 concepts and 76 prerequisite relations, exact evidence mappings, and a SQLite query layer. Two builds were byte-identical. It is the strongest pedagogical graph in the program, but no live learner interface had yet been shown to consume it at the audited snapshot. Its 1.84-GB backend plus 1.13-GB SQLite database also make it unsuitable as the minimum common layer.

2. **A10 — Elementary Algebra.** Its 452,387-record append-only history records translation and control events, explicit missing-solution states, UUIDv5 identities, and lossless JSONL/CSV exchange. It is the strongest whole-book lifecycle ledger. It is primarily a structural and production history rather than a learner-route graph, and retaining the full event history is expensive.

3. **A20 — Intermediate Algebra.** This design combines strict module projections, fixed-point selection, isolated two-build candidates, and fail-closed cursor-last admission and recovery. It provides the strongest transactional production safety. Its global export trails the live module state, however, and three overlay dialects fragment consumption.

4. **A30 — Precalculus.** This lane exposes practical consumer-specific JSON, JSONL, and CSV views joined by bilingual segment identities. It is convenient for exchange and downstream tools. Its generic payload containers weaken semantic typing, and the released aggregate trails current canonical work.

5. **B10 — Discrete Mathematics.** A strict graph is extended with exercise-closure packets containing explicit statement, hint, answer, and solution subtrees, rights data, and deterministic round-trip validation. The exercise-closure model is highly reusable. Normal prose remains comparatively coarse, duplication is substantial, and no learner runtime consumed the graph at the audited snapshot.

6. **CLP — B20, B30, B50, and B60.** The four CLP roles share a source-bound incremental registry using native identifiers, direct-text hashes, declared topology deltas, marker-bound LaTeX variants, and fail-closed drift checks. The machinery is proven in real production and release work. It has generated 622,836,943 bytes, models almost no pedagogical prerequisites, and had no learner backend consumer at the audited snapshot.

7. **B40 — Linear Algebra.** The backend records finely hashed CNXML text and attribute slots, explicit problem, solution, and asset relations, and accessibility slots. It forms a good translation packet. XPath-ordinal identities are fragile under source restructuring, and reverse reconstruction of CNXML has not been demonstrated.

8. **Lebl — B70, C10, C20, and C50.** A shared UUID and alias catalog models the family and explicitly distinguishes hint-only and no-answer states, with exact checks against legacy locators. Its absence modeling is unusually honest. All 432 segments are headings rather than reusable prose units, and retained micro-checkpoint history dominates the infrastructure.

9. **B80 — Mathematical Computing.** This operational course catalog connects executable mastery units, exercises, artifacts, and prerequisite routes, and those structures are consumed in learner QA. It is the strongest executable learner-native model. Its implementation is a monolithic hard-coded JSON structure and lacks a reversible common exchange format.

10. **B90 — Probability.** Stable URNs are represented in compact JSONL with lossless CSV and a public-safe projection that excludes English authority text exactly. It provides the best redaction and exchange discipline. The structural graph is shallow, and a stale parallel public export creates ambiguity.

11. **B95 — Statistics.** This is a rich incremental graph of 10,102 records with explicit translation states and a byte-preserved predecessor. It demonstrates real reuse. One inherited invalid `deferred` state prevents clean full-schema replay. The 399,020,415-byte, 948-file system—including 910 evidence files—imposes severe ceremony while learner delivery remains PDF-based.

12. **C30 and C40 — Judson Abstract Algebra.** One 3,323-unit graph generates two nonduplicating course views and carries 6,505 typed relations, persistent birth and current identities, `source_frozen` state, corrections, and deterministic self-contained exchange. This is the strongest canonical reuse pattern. The two course selectors are not exposed as distinct learner navigation, and important semantics depend on custom verification beyond the permissive envelope schema.

13. **C60 — Number Theory.** A broad bilingual entity and event graph includes concepts, prerequisites, corrections, rights, and numerous reversible projections. It is substantive and deterministic. JSON, CSV, and XLSX duplication plus extensive evidence increase maintenance cost, while TeX still drives the learner reader.

14. **C70 — Applied Combinatorics.** Exact parallel source and target PreTeXt graphs contain 19,048 records and a strong concept and prerequisite model. The system is portable and deterministic. Its source and reader inventories are large, exporter and validator maintenance is demanding, and one mapping remained queued at the terminal release boundary.

15. **C80 — Open Logic.** The completed edition is a 722-module TeX overlay with an exact distinction between 642 reader modules and 80 retained-source modules, a frozen import closure, and complete evidence. It provides excellent preservation-oriented unitization. It is not a normalized semantic backend, has no course navigation or HTML delivery, and its toolchain pinning remains incomplete.

16. **C90 — Topology.** Per-prompt statement, hint, answer, and solution manifests feed mastery modules that are directly consumed in a collapsible self-study reader. This is one of the clearest demonstrations that backend structure can drive learner experience. Chapter-by-chapter schema drift and the lack of one clean reversible graph limit global reuse.

17. **C100 — Geometry.** A compact additive catalog of units, exercises, hints, and figures directly builds semantic HTML and EPUB. Accessibility metadata is operational rather than decorative. Status fields remain permissive and ad hoc, and a drift between two local records and three public relations weakens reproducibility.

18. **C110 — Numerical Analysis.** The native Tea Time backend contributes deterministic pack and merge operations, experiment records, exact toolchain receipts, one-byte drift rejection, and lossless open export. The manager comparison contains 28,172 records. It offers the strongest reproducible-experiment pattern, but uses a generic permissive schema and had no demonstrated shared runtime at the audited snapshot. Later helper-packet work is separate evidence and must not replace this native interpretation.

19. **C120 — Modeling and Nonlinear Dynamics.** Paired source and target hashes, mastery triples, notebooks, and project packets support modeling-specific composition. The manager adapter maps 4,941 native records and reconstructs 81 files. Earlier native validator coverage was incomplete, and the latest readable task boundary concerned a revoked helper assignment, so universal portability has not been established.

20. **C130 — Operations Research.** A complete locale-neutral graph contains 1,993 units, 5,525 segments, 9,545 relations, prerequisites, exercises, and executable lab adaptations. It is among the best general course models and demonstrates real reuse. The typed graph and evidence layer are large, and no reverse importer exists.

21. **C140 — Mathematical Statistics.** The course federates a Penn spine, a donor component, and an original companion while preserving separate rights. Staged problems, simulations, mastery metadata, and byte-identical cumulative reuse are strong. Prerequisites and objectives remain embedded in Markdown rather than graph relations, and lesson and checkpoint machinery is heavy.

22. **D10 — Measure and Integration.** An exact bilingual source-topology catalog carries raw source and target TeX, hashes, rights, and deterministic JSONL/CSV replay. Its archival fidelity is excellent. Many projections and version chains are empty, pedagogical prerequisites are nearly absent, and the current backend exceeds the public release represented by the audit snapshot.

23. **D20 — Functional Analysis.** An immutable scholarly base is extended through an additive learner companion overlay containing formula alignment, solutions, HTML routes, and accessible SVGs. It provides the strongest overlay and state pattern and demonstrates genuine learner use. The implementation contains many chapter-specific scripts and formula or structural rows, while prerequisite modeling remains thin.

24. **D30 — Stochastic Processes.** A generic typed course graph joins donor sources, outcomes, labs, programs, assets, rights, and activities. It is the most portable outcomes-and-labs model and carries useful pedagogical relations. The learner site shares identifiers but did not consume the backend at the audited snapshot, and the exporter and artifact footprint are large.

25. **D40 — Partial Differential Equations.** An append-only TeX document graph uses label-derived stable identities and proves byte-identical predecessor prefixes and cross-reference snapshots. It provides excellent release-lineage evidence. It has no formal schema, models source topology rather than learning semantics, retains both legacy and current backends, and carries substantial cumulative receipt weight.

26. **D50 — Differential Geometry.** An append-only provenance topology distinguishes official answers, missing answers, original repairs, rights, corrections, and reader anchors. Its absence and provenance discipline are strong, and the source package is reproducible. The graph is dominated by QA, artifact, and ordering history, and README hashes are stale.

27. **D60 — Algebraic Topology.** Eleven typed locale-neutral JSONL streams cover concepts, hints, solutions, proofs, rights, and routes. This is a strong general interoperable stream design with verified learner routes. Duplicated units and segments plus 566 correction records create synchronization cost, and the compact Zenodo archive alone does not constitute a build tree.

28. **D70 — Graduate Algebra.** Li, Duncan, CRing, and original material retain component-sovereign backends while supporting a real cross-component learner route. This is a strong rights-preserving federation with branching mastery navigation. It also creates four dialects, repeated rights and prerequisite data, labeling defects, and four separate PDFs instead of one integrated learner corpus.

29. **D80 — Category and Homological Methods.** Lean source-span, terminology, and alternative-text ledgers record precise evidence, and the HTML reader actually consumes the alternative descriptions. The accessibility contribution is concrete. Semantics are sparse and ad hoc, some states are stale, and public replay is not self-contained.

30. **D90 — Advanced Optimization.** Definitions, proofs, labs, assessments, solutions, and a capstone share stable identities in an integrated course-object graph. It provides a strong assessable-course design and real multi-format delivery. Evidence for reversible or external reuse remains limited, and the release occupies 100 files.

31. **D100 — Algebraic Geometry.** A 60-unit authority graph yields a 19-unit learner route as a nonduplicating view, clearly separating edition, release snapshot, and route. This distinction is architecturally important. The corpus and terminal replay remain incomplete, and synchronization costs are high.

32. **D110 — Mathematics in Lean.** An executable proof-aligned graph preserves Lean modules, declarations, and imports while localizing prose. A 3,438-job compiler check serves as a semantic replay oracle for a deterministic 10,978-record backend. This is uniquely strong verification, but the specialized toolchain and 92.7-MB backend limit general reuse.

33. **D120 — Research Reproducibility.** A preserved content backend is paired with a locale-neutral semantic and assessment wrapper, localized text, renderer locators, learner-claim state, explicit prerequisites, and immutable relations. Its separation and reversibility are excellent, and it supports accessible HTML. Parallel wrappers and ledgers make it overbuilt for a course with zero live learner instances at the audited snapshot.

## What the decentralized workflow established

The comparison did not identify one backend that should replace every other backend. It identified distinct patterns that solve different classes of problem:

- A00 shows the value of an explicit concept and prerequisite graph.
- A10, A20, D40, and D50 show how append-only state, transactional admission, lineage, and absence records protect long-running production.
- Judson and D100 show how one canonical corpus can yield multiple nonduplicating curriculum views.
- B10 and C90 show that exercises should preserve the structure of statements, hints, answers, and solutions rather than flattening them into prose.
- B80, C90, C100, D60, D70, and D90 demonstrate that backend records become valuable when learner navigation or assessment actually consumes them.
- B90 demonstrates disciplined public-safe projection and reversible exchange.
- C110, C120, D30, and D110 show that experiments, notebooks, programs, and formal proofs require richer capability-specific records.
- C140 and D70 show that component rights and provenance must survive federation.
- D20 shows how an immutable scholarly edition can receive an additive learner layer without duplicating or silently rewriting the base.
- B40, C100, D20, and D80 show that accessibility data must be attached to stable content or asset identities and consumed by delivery formats.
- D110 shows that, where a formal compiler exists, it can provide a stronger semantic replay check than ordinary schema validation.

The program therefore benefits from the deliberate sequence it followed: independent course implementations first, comparative synthesis second, and common interfaces only after real patterns and failure modes are visible.

The following table distinguishes patterns merely observed in native work from capabilities actually adopted by the central layer:

| Capability | Native exemplars | Global treatment | Current status |
|---|---|---|---|
| Stable identities and nonduplicating views | Judson, D100 | Required capsule core | Implemented for all 40 course capsules |
| Structured exercise components | B10, C90 | Optional assessment shard bound to stable units | Demonstrated by the A00/O001 adapter and learner navigator |
| Public-safe reversible projection | B90 | Required adapter and release discipline | Adopted by nine role bindings through eight accepted 2.3.1 packages |
| Learner delivery | B80, C90, C100, D20, D60, D70, D90 | Learner-surface and delivery records | Partially consumed by the central site |
| Component rights federation | C140, D70 | Required unflattened provenance and rights layer | Adopted by capsule and adapter contracts |
| Accessibility metadata | B40, C100, D20, D80 | Stable content/asset bindings consumed by delivery formats | Partial; not yet uniform across all families |
| Experiments and formal proof | C110, D110 | Optional capability shards and replay oracles | Demonstrated; intentionally not mandatory for every course |

## Manager layer at the audited snapshot

At the audited snapshot, the central native-v1 representation contained 2,122 records across 38 tables, of which only 20 were nonempty. It functioned mainly as a 40-course catalog.

Federation v2 contained 2,490 registry records, 34 datasets, 2,122 crosswalks, 164 learner surfaces, 43 routes, and 69 publication events. It deliberately copied no native course prose.

At the audited snapshot, only B10, D60, and D110 implemented contract 2.3.1. A00 was a separate legacy proof, even though the documentation then labeled all four implementations as 2.3.1. At that same snapshot, the live learner application did not consume the federation or these backend packages; it imported only `courses.js`, `live-course-publications.js`, and `learner-state.js`.

On the audit’s coarse manager rubric, portability was 2/4, learner use 2/4, reproducibility 3/4, and complexity burden 4/4. Those values describe the manager synthesis at that snapshot, not the quality of the individual course backends.

## Implementation after the audit — 2026-08-30

The central implementation has advanced since the audited snapshot. It now generates a learner-delivery sidecar from validated central data. The learner interface consumes that sidecar to display delivery-capability badges, offer verified download actions, and filter courses with verified portable offline HTML. This is a concrete connection between machine-facing delivery metadata and the human-facing curriculum interface; it does not retroactively change the findings for the earlier snapshot.

D20 Functional Analysis was subsequently admitted through a deterministic 2.3.1 adapter after all named gates passed. The admitted package contains 138,894 canonical records, preserves 32,383 native records through reversible bindings and crosswalks, carries 2,104 additional native index rows, and exposes 19 lossless JSONL/CSV table pairs. All 59 frozen authorities, reverse extraction, structural coverage, rights separation, identity preservation, privacy checks, and deterministic ZIP replay passed. This post-audit admission does not retroactively change the audited snapshot; it records the next verified convergence result.

## A00 assessment convergence after the audit — 2026-08-31

The A00 legacy-label defect has now been resolved additively. A contract-2.3.1 successor reuses the exact 1,313-record A00 course spine and leaves the 24,315-record O001 assessment shard authoritative. It does not inflate the common schema by pretending that exercises, solution components, or no-solution records are curriculum units. Instead, three capability-specific sidecars bind 8,105 assessments, 13,345 statement/solution components, and 2,865 explicit solution gaps to the existing 75 module identities and readable Indonesian HTML routes.

This is the first direct learner-facing use of the assessment backend. A generated **Latihan & diagnosis** page lets students filter the 8,105 exercises by module, category, and availability of an explicit source solution, then opens the exact exercise or solution anchor in the owner reader. The join key is `(module, native_id)`, never `native_id` alone: 867 fragment strings recur across modules. All 21,450 assessment/component anchors resolve exactly once; no mathematical prose or formula bodies are copied into the central adapter; and the 2,865 absent solutions remain visibly absent rather than being invented.

The implementation demonstrates the intended global workflow in miniature: independent native design first, comparative audit second, a thin interoperable adapter third, and a learner surface generated only from verified public routes. Ninety-one frozen authorities replay, the 19 common JSONL tables round-trip to 19 CSV views, two isolated full package builds are byte-identical, and the generic plus A00-specific validators pass. The old A00 conformance package remains public as predecessor evidence, while A00 itself is no longer counted as a legacy-only proof.

## Current successor results — 2026-08-31

| Measure | Current result |
|---|---:|
| Curriculum roles with selected corpora or frozen original specifications | 40/40 |
| Roles with complete public editions | 35 |
| Roles still in production | 5: A20, A30, B95, C140, D100 |
| Native implementation families compared | 33 |
| Accepted contract-2.3.1 role bindings | 9 through 8 packages: A00, B10, C30, C40, C80, C130, D20, D60, D110 |
| Native families without a public-replay-complete 2.3.1 adapter | 28 |

The learner application now consumes validated delivery data for course actions, format badges, offline-package filters, and the one-file curriculum navigator. Course capsules expose learner tools directly: A00 consumes its assessment adapter through a searchable exercise page; C30 and C40 consume two nonduplicating course views over one Judson graph; C80 binds all 722 Open Logic source/translation identities to its 1,116-page reader; and C130 exposes seven validated routes to its course-native landing and 666-page reader. These are concrete uses of backend data, but they remain a partial convergence result rather than a claim that all 33 native families have been normalized.

D30/O009 also reached a terminal public edition during successor assembly. Its open Zenodo record contains six files totaling 48,733,779 bytes; the 447-page PDF, five declared payload checksums, and public HTML route were independently read back.

D40 subsequently reached a terminal public edition as well. Its open record contains seven anonymously read-back files totaling 13,989,998 bytes, a 679-page Indonesian PDF, a 72-file offline HTML reader, an executed FEniCSx companion, 48 solved problems, 16 assessment items, four laboratories, and two semantic backends. Together with B30's later terminal public edition, this advances the current program split to 35 complete roles and 5 in production (A20, A30, B95, C140, and D100) without changing the historical audit snapshot above.

The D30 learner route also demonstrates the delivery rule adopted globally. Its public Pages entry point is 10,351 bytes with SHA-256 `417e580082b32178e99a9923c8d0fa13ae21fdb767edb8eb85a38d6b6a9f7bc9`, exactly equal to `reader/index.html` inside the verified 163-entry offline ZIP. The capsule therefore makes semantic HTML the primary learner action, preserves the 447-page PDF as an edition download, and exposes the dependency-free HTML ZIP for intermittent connectivity. Machine records prove those identities but remain secondary to the readable route.

The adapter inventory now states a `learner_runtime_relationship` for every admitted proof. A00, C30, C40, C80, and C130 directly consume adapter-derived mappings; C30 and C40 intentionally share one archive, manifest, and native graph. B10, D20, D60, and D110 expose verified course routes without claiming that their readers consume the central adapter tables. Each row also records adopted capabilities, known limitations, an exact public asset URL, and public-replay state. This prevents a course link from being mistaken for runtime integration and makes later convergence auditable rather than rhetorical.

## Recommended common architecture

The common layer should be a thin, hash-bound and receipt-bound capsule placed over each course-native backend. It should not require every course to abandon its source-oriented graph, append-only ledger, executable proof model, experiment records, or learner companion.

The mandatory capsule should expose:

1. course, edition, release, and route identity;
2. stable unit identities and aliases;
3. localized variants without duplicating language-neutral structure;
4. typed semantic relations and prerequisites;
5. translation state, provenance, component rights, and corrections;
6. learner surfaces, educator support/evidence, assets, and accessibility metadata;
7. manifest, build, validation, and public-readback receipts.

Canonical exchange should use JSONL plus cryptographic hashes. CSV, SQLite, and Parquet should be optional generated views, not parallel authorities that must be synchronized manually.

Capabilities that do not apply to every course should remain optional shards:

- formula-alignment records;
- experiments and notebooks;
- formal proof and compiler-aligned records;
- source-format topology such as TeX, PreTeXt, or CNXML structure.

Terminology is concept-first rather than a global word-replacement table. A
canonical policy records stable concept identities, preferred forms, permitted
register-specific variants, source/context evidence, and unresolved evidence
requirements. Existing native concordances remain bounded witnesses; the
central policy does not claim that one term has been harmonized across all
courses without field-specific evidence.

This approach preserves the useful diversity of the 33 implementations while giving every course the same minimum open interfaces.

## Learner-facing and machine-facing layers

The machine-facing backend and the learner-facing curriculum should be connected but not conflated.

The machine-facing layer should preserve exact identities, relations, localized variants, provenance, rights, correction history, accessibility metadata, and reproducibility receipts. It should support cross-language transformation, auditing, reconstruction, and curriculum assembly.

The learner-facing layer should expose understandable course titles, prerequisites, completion-aware routes, available editions, HTML or other accessible readers, exercises, hints, solutions, downloads, and offline options. It should be generated from the capsule and current public receipts, but learners should not be expected to navigate raw JSON, registries, or evidence ledgers.

The educator-facing layer should expose syllabi or course maps, learning
outcomes, prerequisite evidence, exercise/solution coverage, correction and
terminology evidence, accessibility notes, and reproducible source/build
routes. Missing material stays explicitly unknown or in progress rather than
being inferred from the existence of a textbook.

The central hub should automatically ingest current course release receipts and construct learner routes from actually public units. Planned routes must remain visibly planned; they must never be presented as available merely because their identifiers exist in a backend.

## Audited-snapshot limitations and unresolved successor gaps

At the audited snapshot, the central comparison found these consistency problems. Each item is labeled with its successor status so historical evidence is not mistaken for current truth:

- **Resolved in the successor:** course-native, overlay, and frozen-model counts disagreed at 29/11, 28/12, and 21/19. Current receipt-bound evidence yields 35 complete and 5 in production (A20, A30, B95, C140, and D100).
- **Resolved in the successor:** C20 was stale, 13 successor labels did not reflect current state, and the B50 repository was absent.
- **Partially resolved:** only 19 of the 28 then-published roles had explicit HTML. Current learner delivery records more public HTML, but HTML and offline formats are not yet uniform across all roles.
- **Partially resolved:** unit-level routes were planned rather than public. Several course routes are now public and A00 has 21,450 verified exercise/component anchors; other families remain course-level or planned.
- **Open:** a public clone cannot yet replay every accepted and future adapter without external course or logbook roots. Each adapter must close this independently.
- **Resolved in the successor:** A00 was incorrectly presented alongside the three actual 2.3.1 implementations. Its 2026-08-31 successor adapter and learner navigator close that specific defect without rewriting the historical snapshot.
- **Partially resolved:** the learner application did not consume federation or capability packages. It now consumes learner-delivery and learner-tool sidecars, while broader capsule capability consumption remains unfinished.

The post-audit learner-delivery implementation resolves only part of that final interface gap. It does not by itself resolve every publication-state discrepancy, missing reader, stale course record, adapter replay dependency, or native-family limitation.

The native families also retain their documented local limitations: stale exports, schema drift, missing reverse importers, overlarge evidence histories, thin prerequisites, public/local drift, or non-self-contained replay. These should remain visible rather than being concealed by central admission.

No corpus-selection failure, custody conflict, duplicate-production emergency, public-access loss, or public-byte emergency was found at the audited snapshot.

One audit-only recursive fan-out briefly exceeded the intended 20-agent limit. Its descendants were interrupted, after which the root audit and ten bounded top-level auditors completed the evidence groups. This did not affect application tasks or public artifacts.

## Completed, underway, and recurring integration work

The global implementation continues additively.

- **Completed:** a small seven-layer course-capsule contract and capability vocabulary now cover all 40 roles while allowing course-specific extensions.

- **Published and publicly read back for thirteen role bindings through nine packages:** A00, B10, B20, B30, B50, B60, C30, C40, C80, C130, D20, D60, and D110 preserve native identities through explicit crosswalks and thin adapters. C30 and C40 are two course views over one Judson package; B20/B30/B50/B60 retain four distinct native profiles inside one CLP package. They do not rewrite course-native backends or copy entire corpora into the manager.

- **Remaining integration capability:** 24 of the 33 native families do not yet have a common adapter with full public readback. This is an adapter-coverage denominator, not a claim that those textbooks remain untranslated. Future adapters should adopt only useful capabilities and preserve native limitations rather than flattening them.

The v0.62.17 CLP delta is public on [GitHub](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.17) and [Zenodo](https://zenodo.org/records/22303203). Anonymous readback verified all 121 GitHub assets and all 100 Zenodo files. Its seven Indonesian PDF routes cover 4,077 pages across four already-complete native calculus editions. Current publication evidence is in the root v0.62.17 receipts; the immutable release source remains pinned to its original commit, while the additive postpublication overlay records thirteen published bindings and zero pending adapter bindings.

- **Underway:** expand learner consumption of capsule-derived routes, public HTML, offline packages, EPUB/PDF delivery, exercise components, and accessibility support. Planned units remain excluded from completion claims.

- **Underway:** make every accepted adapter reproducible from the public central release. A public clone must contain its source, schemas, crosswalks, manifests, validation commands, and all non-corpus evidence needed to replay the central projection without private roots.

- **Current release duty:** publish this evolving methodology, capsule schema, capability shards, adapter inventory, comparison results, and validation receipts in the established central DOI lineage. Every version preserves its predecessor and names the native families that passed the capsule and public-replay gates.

- **Recurring:** re-audit native work as it matures. Independent innovation remains useful; global convergence adopts demonstrated capabilities without forcing every book into the largest or most specialized backend.
