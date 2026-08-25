# Global modular backend status — v0.55.0

Status date: 25 August 2026  
Release: [Program Matematika Indonesia v0.55.0](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.55.0)  
Student entry: [Program Matematika Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/)

This is the current backend status document. `BACKEND_CONVERGENCE_V1.md`
remains the historical decision record for choosing the common-v1 kernel. The
backend exists to serve readable courses and reusable translation workflows;
JSON, JSONL, CSV, schemas, hashes, and receipts are secondary machine surfaces,
never the student's starting page.

## Architecture in force

```text
owner-native editable corpus and backend
  -> lossless common-v1 adapter
  -> compact federation-v2 registry
  -> deterministic learner read model
  -> generated course map and learner actions
```

The owner-native package remains canonical. The central program does not
flatten CNXML, PreTeXt, LaTeX, LyX, MediaWiki, Pressbooks/HTML, notebooks, or
their rights models into a lossy universal source format. It stores stable
identity, typed crosswalks, routes, release and QA evidence, then projects the
small subset needed by learners.

## What the corpus implementations contributed

| Implementation | Strength retained by the common design |
|---|---|
| DMOI / PreTeXt | Strict normalized graph, occurrences, aliases, component-rights compilation, and dependency-closed module selection |
| OpenStax Prealgebra | Clean separation of canonical units, locale-neutral segments, localized expressions, and asset occurrences |
| OpenStax Intermediate Algebra | Recursive XML AST, QName and attribute fidelity, plus protected formulas, media, and links |
| OpenStax Precalculus | Explicit exercise–hint–answer–solution relations and rights/quarantine states |
| CLP | Immutable batches, exact selectors, typed content/math/topology deltas, and deterministic replay |
| Applied Combinatorics | XPath/C14N/hash crosswalks and protected-math delta evidence |
| Lebl family | Readable semantic keys combined with deterministic UUIDv5 projections |
| Point-set topology | Strong statement, hint, answer, and solution closure |
| Functional Analysis | First-class formula alignments and semantic HTML route records |
| Mathematical Computing | Broad HTML/PDF/EPUB/source/offline/notebook delivery matrix |
| Modeling and nonlinear dynamics | Mastery tasks, projects, notebooks, localized variants, and alignments |
| Algebraic-geometry bridge | Revision, transclusion, asset, rights, exercise, and public-solution closure for remotely assembled works |

No implementation wins merely by being large. Common v1 preserves the strict
parts that actually survived full-corpus validation; corpus-specific semantics
stay in owner profiles or namespaced extensions.

## Verified v0.55 state

Common v1 is the preservation and interoperability kernel:

- 38 strict tables with closed schemas;
- 2,122 records and stable UUIDv5 identity;
- canonical JSONL and lossless CSV;
- 84-entry package;
- byte-identical 83-file replay;
- aliases, crosswalks, locale-neutral segments, localized variants, routes,
  alignments, build recipes, experiments, rights, corrections, and release
  snapshots;
- 13 admitted complete-corpus migration receipts representing 926,171 target
  records without copying owner-native content into the center.

Federation v2.0.0, dataset
`program-matematika-indonesia-federation-v0.3.0`, is the compact global
envelope:

| Record type | Count |
|---|---:|
| datasets | 34 |
| programs | 1 |
| courses | 40 |
| reader surfaces | 128 |
| web routes | 41 |
| publication events | 52 |
| QA events | 16 |
| identity crosswalks | 2,122 |
| **total** | **2,434** |

Validation proves 3,159 typed foreign keys, 82 prerequisite edges in an acyclic
graph, UUIDv5/semantic-key consistency, lossless CSV round trips, canonical
JSONL, and two byte-identical 20-file builds. The learner model has 40 course
cards, 17 published roles, 13 dedicated HTML readers, and three hash-bound
public-readback overlays. A learner action may not point to JSON, JSONL, or CSV.

## Educational-access and compute research

The central backend also registers one research-support dataset rather than
pretending that research evidence is a mathematics course. Its native
`educational-access-v0.1.0` package contains 490 records:

- 169 language profiles;
- 94 recommendations;
- 69 evidence sources;
- 46 manager-coverage records;
- 40 curriculum resources;
- 32 asset sources;
- 14 accessibility interventions;
- 14 bridge surfaces;
- 10 research workstreams;
- 2 research projects.

This layer supports decisions about which language, curriculum portfolio,
accessibility derivative, and translation workload should be funded next. Its
evidence and scoring records remain native and hash-bound. The learner-facing
program should expose readable strategy summaries and selected portfolio
results, while the global federation stores only the dataset identity,
provenance, rights, version, public route, and QA/publication state. A future
research shard may expose typed language, workload, portfolio, evidence, and
recommendation summaries without mixing them into course prerequisites or
unit content.

## What is still missing

Federation v2 is deliberately phase one. It materializes only eight global
record types; 2,122 of its 2,434 rows are identity crosswalks. The following
learner-value layer is not yet globally materialized:

1. stable course units, order, and table-of-contents membership;
2. localized unit titles, objectives, reader anchors, and learner URLs;
3. exercise, hint, answer, solution, theorem, proof, prerequisite, and support
   relations;
4. search shards and terminology shards;
5. per-surface rights, accessibility, publication, and anonymous-readback
   evidence;
6. typed owner authority and release snapshots;
7. real course and unit routes instead of `planned_not_published` placeholders.

Current delivery gaps are explicit rather than hidden: 13 of 40 courses have a
dedicated HTML reader, 23 have a PDF action, 29 have an offline action, and no
uniform unit-route layer is published. The central course-card anchor remains a
fallback, not evidence that a full reader exists.

## Correct phase-two shape

Phase two should be additive and zero-copy. It must not replace v0.3.0 in
place. A v2.1 package should add these typed records:

- `owner_authorities`
- `editions`
- `release_snapshots`
- `units`
- `unit_memberships`
- `occurrences`
- `segments`
- `segment_variants`
- `terms`
- `term_variants`
- `relations`
- `assets`
- `rights`
- `rights_assignments`
- `artifacts`
- `routes`
- `route_members`
- `build_recipes`
- `qa_bindings`
- `research_profiles`

The default course-content shard should remain compact. Each unit needs only:

- stable global and owner-native identity;
- course and edition membership plus ordinal;
- localized title and optional learning objective;
- native source locator and source/target hashes;
- learner URL or stable reader anchor;
- prerequisite/support relations;
- exercise/hint/answer/solution availability summary;
- rights and accessibility summary;
- publication and anonymous-readback status.

Full prose, full formula maps, images, notebooks, and giant owner backends stay
in the edition repository. A separate search shard carries normalized terms,
titles, objectives, aliases, and learner URLs. This keeps the central site fast
without throwing away owner semantics.

## Implementation order

1. Freeze v2.1 schemas and state vocabulary; preserve owner-native values as
   provenance while normalizing `producing`, `published`, and partial-release
   synonyms globally.
2. Pilot unit and search shards on three structurally different completed
   corpora: A00 CNXML, B10 PreTeXt, and D20 LaTeX/formula alignment.
3. Generate real `/id-ID/courses/<course>/units/<slug>/` routes. Existing HTML
   readers use stable anchors; PDF/offline-only editions receive an accessible
   HTML contents wrapper with PDF fallback.
4. Import owner publication receipts as typed per-surface publication and QA
   events. A catalog link and a byte-verified public artifact must remain
   different states.
5. Materialize learning-support, formula-preservation, component-rights, and
   accessibility profiles before lower-value metadata.
6. Add typed owner-authority and release-snapshot records; internal task
   locators never become public learner URLs.
7. Add a non-circular final `SEAL.json` binding schemas, builder, federation,
   manifest, validation report, and release receipt.
8. Project the educational-access research dataset to a separate readable
   strategy surface and research shard, not into the course graph.

## Invariants

- One canonical owner/integrator/publisher per corpus.
- Helpers return immutable, hash-bound semantic packets only.
- No arbitrary page split, theorem/proof split, or exercise/solution split.
- Owner-native source and backend remain authoritative.
- Global adapters are additive, deterministic, and reversible.
- Machine records never replace a readable student surface.
- A public claim requires access, rights, and anonymous-byte evidence.
- Every published course or unit route resolves to readable HTML, a stable
  reader anchor, or an accessible wrapper with a clearly labeled download.

This is the target against which subsequent backend releases and owner
migrations should be evaluated.
