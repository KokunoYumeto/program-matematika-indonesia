# Interlanguage modular mathematics backend v1

Status: selected, implemented, and independently validated on 22 August 2026.

This is the common machine layer for the Bahasa Indonesia mathematics program. It does not replace any corpus's editable source, reader, release lineage, or source-format authority. It supplies one portable identity, topology, localization, rights, QA, artifact, and selection contract across those corpora.

## Decision

The admitted DMOI fourth-edition backend is the structural kernel. It is the only audited implementation that already combines all of the following at full-book scale:

- 163,583 normalized records in 32 tables;
- strict Draft 2020-12 schemas with `additionalProperties: false` for every entity type;
- UUIDv5 identity, aliases, occurrences, source and target variants, component rights rules and compiled assignments;
- dependency-closed portable modules and a selector by stable ID or qualified alias;
- canonical JSON, JSONL, and lossless CSV with full round-trip checks;
- two independent byte-identical regenerations.

The kernel is adopted as a base, not copied unchanged. Common v1 has 38 strict tables. The six additions close gaps proved by the other mature lanes:

1. `release_snapshots` separates immutable edition identity from mutable/public release boundaries. This fixes the edition/release conflation found in O016 and the stale build/publication state embedded in otherwise immutable TTNA localization rows.
2. `routes` and `route_members` represent learner paths across resources without pretending that a full edition's order and a curriculum route are the same object.
3. `alignments` records source/target, formula, structural, and accessibility alignment as first-class evidence. It admits the O008 formula map and O005 paired-segment evidence without embedding both languages in a neutral segment.
4. `build_recipes` preserves TTNA's exact command, input/output, environment, and verification evidence.
5. `experiments` preserves executable mathematical labs, scripts, notebooks, parameters, and expected-output bindings.

The common schema permits a namespaced `extensions` object, but all recognized editable-source topology is governed by the separate strict source-format profile schema. The v1 profile discriminates CNXML, PreTeXt, LaTeX, LyX, MediaWiki, and Pressbooks/HTML bindings.

## Evidence used

| Implementation | What it contributed | Principal evidence |
|---|---|---|
| DMOI fourth edition | structural kernel, 32 strict tables, aliases, occurrences, variants, rights compilation, portable modules | `discrete-mathematics-open-introduction-id/repo/backend/full/dmoi4-id/schema/backend-full.schema.json`; 55,313 B; SHA-256 `e1c7a9a05b8cf11d3fb318413019614be9e425270eac131105921323300204d8` |
| OpenStax Prealgebra | canonical-unit versus localized-unit split, independent expressions, aggregate relation closure, CNXML asset occurrences | `openstax-prealgebra/modular_backend/schemas/record.schema.json`; 33,515 B; SHA-256 `efdc6419dd826046b3c0aad1215db901700e1e11789b590dc3ca0ebee0aa35d5` |
| Tea Time Numerical Analysis | deterministic pack/merge, exact build/toolchain receipts, experiments, one-byte drift rejection, lossless open export | `tea-time-numerical-analysis-id/backend/exports/interoperability-v0/records.jsonl`; 28,172 records; SHA-256 `203ec965823817e79939f894f871ed6c0445534fbf3a6d06d1e0fa3566e16c79` |
| AATA | persistent birth/current identity crosswalk, source-frozen legal-text states, two nonduplicating course views, Sage evidence | `abstract-algebra-theory-and-applications-id/backend/v1/manifest.json`; 5,669 B; SHA-256 `312b5f7fcda24e7f0e1e430fa4a06d816abaae2fecc8655b37f0aa5d25c979be` |
| O016 algebraic geometry | authority closure for MediaWiki page/revision/transclusion graphs; proof that release snapshots and routes must be distinct | `algebraic-geometry-bridge-id/backend/units-01-05/record.schema.json`; 3,277 B; SHA-256 `0553c75a81cecd08ba39a5e67e1aa39ed0c90e9697d8deefb84f7eea09b42eef` |
| O008 functional analysis | formula alignments and rich LaTeX semantic/xref graph | `functional-analysis-erdman-id/backend/formula_map.jsonl`; 3,720,317 B; SHA-256 `1c34c2302d282a0304ce6d5ed27838da5d344e85c6c9950eedd296b88de49457` |
| O005 modeling | paired source/target hashes, complete mastery triples, notebooks, and project packets | `mathematical-modeling-nonlinear-dynamics-id/backend/units/CH01.mastery.json`; 29,810 B; SHA-256 `58f5c0aff94d3d6290775906ebfb4f81e9fafb50b31d60aa8b21080541c77a6d` |
| Hefferon Linear Algebra | active LaTeX closure and explicit exercise/answer relations; not admitted as current truth because its backend validator presently fails on a stale workflow identity | `hefferon-linear-algebra-id/backend/source_closure.json`; 139,853 B; SHA-256 `36cebbcb119fd46db6ae785ba5faced5a45a216da3323bcd3d218a4981bef806` |
| CLP1 | exact release/render evidence and the need to preserve PreTeXt and LaTeX as separate representations until a proved crosswalk exists | `clp1-differential-calculus-id/provenance/QA_RECEIPT.id-ID.json`; 2,674 B; SHA-256 `9965ea028073a23eadca995ddf86934d7167571e11a4d65aeba1f63fa2109988` |

No lane is treated as canonical merely because it is large. The DMOI kernel won because its strict model, complete corpus migration, portable selector, identity continuity, and lossless projections are all already proved. OpenStax is larger in raw bytes and unit count, but its schema contains A00/OpenStax-specific requirements. O016 has a clean common envelope but hides type semantics inside an unrestricted payload. TTNA and AATA are mature but use permissive generic schemas. O008's `schema.json` is an inventory rather than a validating schema. O005 currently validates only 3 of its 18 unit records. Hefferon's preserved projection is stale. CLP1 has no semantic backend yet.

## Canonical package contract

Every package contains:

```text
schema/backend-v1.schema.json
schema/namespace.json
schema/source-format-profile-v1.schema.json
data/<table>.jsonl
csv/<table>.csv
backend.json
records.jsonl
records.csv
manifest.json
validation_report.json
```

- `backend.json` is the complete 38-table object.
- Each `data/*.jsonl` table is sorted by stable UUID and uses UTF-8, LF, and canonical compact JSON.
- `records.jsonl` is the complete `(record_type, id)`-sorted projection.
- Every CSV row carries `id`, `record_type`, and canonical `record_json`; parsing `record_json` reconstructs the JSONL record exactly. Typed convenience columns may be added, but they are never the sole lossless representation.
- `manifest.json` binds each carried file by relative path, bytes, and SHA-256 and records table and total counts.
- The independent validator checks the Draft 2020-12 schema, inventory, hashes, JSON canonicalization, CSV round trip, global ID uniqueness, typed reference closure, and a second byte-identical export.

The 38 table types are:

`accessibility`, `aliases`, `alignments`, `artifact_members`, `artifacts`, `asset_revisions`, `assets`, `build_recipes`, `concepts`, `correction_bindings`, `correction_claims`, `corrections`, `courses`, `editions`, `experiments`, `file_revisions`, `files`, `interactives`, `module_members`, `modules`, `occurrences`, `placeholders`, `programs`, `qa_events`, `relations`, `release_snapshots`, `resources`, `rights`, `rights_assignments`, `rights_rule_members`, `rights_rules`, `route_members`, `routes`, `segment_variants`, `segments`, `term_variants`, `terms`, and `units`.

Exercises, hints, answers, solutions, proofs, theorems, formulas, projects, code blocks, datasets, and interactivities remain typed `unit_kind`, `segment_kind`, asset, or interactive records rather than corpus-specific top-level record types. Their semantic links are explicit relations such as `has_hint`, `has_answer`, `has_solution`, `contains`, `precedes`, `translates`, `aligns_formula`, `uses_asset`, and `depends_on`.

## Identity

The central namespace is `7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd`, derived once from the central concept DOI. New IDs are UUIDv5 over `record_type|stable_key`.

A corpus migration does not remint a proved existing ID. One-to-one mappings retain legacy UUIDs. A split creates deterministic child IDs under the corpus's existing namespace and writes aliases/crosswalks. Identity inputs are, in order:

1. resource authority;
2. frozen source edition;
3. source document or authority path;
4. a unique native ID or label;
5. otherwise a declared format-aware structural path or source-order anchor.

Translated wording, rendered pages, page numbers, current hashes, and publication state never define identity. Hashes bind a revision or payload; they do not replace semantic identity.

## Language, edition, and release rules

- A `unit` or `segment` is locale-neutral.
- Locale-bearing text is a `segment_variant`; whole-unit target topology is an `occurrence` or localized variant binding.
- `alignments` connect source and target variants without hiding one language inside the other.
- An `edition` is a stable source or derivative edition identity.
- A `release_snapshot` is an immutable published/build boundary. A new cumulative PDF or DOI version does not create a new edition.
- A `route` is a pedagogical path. It may span resources and editions. It never truncates the complete edition itself.
- Source-only, target-only, accessibility-added, source-frozen legal, and target-only correction states remain explicit; they are not forced into ordinary translated pairs.

## Rights and authority rules

Rights are component-specific and compiled through assignments. A hub selection record does not relicense the selected book. The central program's original descriptions and metadata are CC BY 4.0; hub software and schemas are MIT. Each corpus, asset, imported component, runtime dependency, service boundary, and legally required source-frozen passage retains its own record and authority notice.

Editable sources remain authoritative. The source-format profile preserves CNXML collection/document paths and MathML, PreTeXt XIncludes and exercise subdivisions, active LaTeX include/macro/AUX topology, LyX layouts/insets/ERT, MediaWiki page/revision/transclusion closure, and Pressbooks HTML/notebook/project bindings. A generic backend projection is never permission to discard those sources.

## Implemented proof packages

### Central 40-course catalog

`backend/v1/program-matematika-indonesia-v0.41.0` is the first native common-v1 package:

- 38 declared tables, 20 non-empty;
- 2,122 records;
- 40 courses and 40 selected-corpus resource statements;
- 40 course-role units;
- 200 locale-neutral description segments plus 200 original `id-ID` variants;
- eight topic concepts;
- 442 typed relations;
- one full-program route with 40 route members;
- explicit edition and release-snapshot separation;
- two component rights records and 1,060 compiled rights assignments;
- byte-identical second export, strict schema pass, exact CSV round trip, global uniqueness, and reference closure.

The public course corpora remain external, authority-bound resources; their source files are not copied into this small central package.

### Complete corpus migrations

The complete 163,583-record DMOI backend has passed a lossless zero-copy migration to v1. Every source row was streamed, transformed, validated against the matching v1 strict definition, reversed exactly, and checked for global identity and foreign-key closure. The migration changes only `schema_name` and `schema_version`; it changes zero record IDs and zero payload fields. The six new v1 tables initialize empty until the lane has evidence for them.

The result is recorded at `backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json`. A redundant 437 MB local copy was deliberately not made: the admitted source package plus the deterministic migration program and hash-bound receipt can materialize exactly the same target package.

Three further complete-corpus proofs use the same nonduplicating contract:

- Open Logic OLP-0722 reconstructs 6,522 strict records from 722 frozen source
  and 722 frozen Indonesian modules with zero source/target payload-byte changes.
- Judson abstract algebra adapts the immutable public `v2026.08.21.1` backend:
  24,733 native rows yield 36,978 common records while 24,483 native IDs remain
  unchanged.
- Yet Another Introductory Number Theory Textbook reverses exactly from 6,967
  common records to all 5,272 native records and preserves its complete
  manifest, projections, assets, artifacts, reader, QA, and public snapshots.

Each proof was assembled twice with byte-identical virtual records and has its
own schema-valid receipt under `backend/migrations/`.

## Corpus migration order

1. DMOI: admitted by the completed zero-copy proof.
2. Open Logic OLP-0722: admitted by the completed deterministic reconstruction.
3. Judson AATA: admitted from the immutable public `v2026.08.21.1` backend.
4. YAIN number theory: admitted by the completed reversible additive adapter.
5. TTNA: adapter implemented but fail-closed until the terminology-corrected
   release and public receipts bind the same bytes.
6. OpenStax Prealgebra: preserve existing IDs; map canonical units, localized units, expressions, rights, assets, and relations; move A00-specific curriculum fields to an extension/profile.
7. O008: map formula evidence to alignment records and core/advanced arrays to route members; leave queued O001 solution references external until solution content exists.
8. O005: split paired segments into neutral segments plus `en` and `id-ID` variants; promote every mastery problem, hint, answer/check, solution/rubric, notebook, project, dataset, correction, right, and build witness to typed records.
9. O016: convert cumulative "editions" to release snapshots; add stable Brenner/BGK source and Indonesian derivative editions; add the complete edition and 19-unit learner routes; demote Napkin to an optional reference.
10. Hefferon: regenerate the stale backend under the current workflow and require its own validator to pass before migration.
11. CLP: build an active-LaTeX-closure exporter and preserve the English PreTeXt tree as a separate source representation until individual crosswalks are proved.

Migration is additive. Existing public packages stay immutable, and no lane is allowed to claim common-v1 conformance until its exported bytes pass the common validator.
