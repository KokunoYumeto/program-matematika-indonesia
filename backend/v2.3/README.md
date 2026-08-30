# Backend modular global v2.3

Backend v2.3 is an additive interoperability layer. It does not replace the
student-facing HTML, PDF, or EPUB readers, and it does not replace any corpus
owner's source, terminology, rights, correction, build, or publication
authority.

## Admitted packages

### Legacy A00 conformance package v0.1.1

The first admitted implementation is
`program-matematika-indonesia-backend-v2.3-conformance-v0.1.1.zip`, published
with central release v0.62.6. Its exact scope is the frozen A00 OpenStax
Prealgebra v2.2 package plus the bound O001 assessment shard. It makes no
aggregate 40-role conformance claim and changes no learner reader.

The package contains 48 members and projects 25,795 canonical records into 24
per-table CSV files plus one global `records.csv`. It preserves the predecessor
v1 and v2.2 archives byte-for-byte, exposes 980 evidence-backed workflow-state
records in 17 groups, declares exactly ten canonical capabilities, and records
three namespace-crosswalk rows: one exact mapping and two explicitly unresolved
relations.

The four versioned Draft 2020-12 schemas admitted by that package are published
at the exact URLs declared by their `$id` fields:

- `capability-declarations-v0.1.0.schema.json`;
- `conformance-manifest-v0.1.0.schema.json`;
- `namespace-crosswalk-v0.1.0.schema.json`; and
- `translation-state-index-v0.1.0.schema.json`.

Their public copies must remain byte-identical to the corresponding `schema/`
members in the admitted archive.

### Corpus-neutral B10 lane adapter v0.2.0

The second admitted implementation is the B10 Discrete Mathematics lane
adapter at `extensions/b10-dmoi-v0.2.0`. It implements adapter contract 2.3.1
without copying the textbook body or changing the owner's 163,583 native
records. The extension contains 57 files / 4,789,912 bytes and 1,264 canonical
records. Of these, 606 are the compact, already admitted unit, relation, and
search projection; the remaining records bind course identity, source
occurrences and translation variants, rights, accessibility, namespace
crosswalks, capabilities, and explicit scope.

The adapter preserves 161 reversible owner-to-projected unit mappings, 284
relations including the current B10-to-A30 prerequisite, 161 metadata-only
search documents, 161 evidence-bound translation-state rows, five rights
components, and 235 accessibility records. Nineteen JSONL tables have nineteen
lossless per-table CSV projections plus one global `records.csv`. Two isolated
builds, a post-copy canonical replay, and independent semantic and release-
envelope audits pass. The canonical learner route remains the owner's readable
course page:
<https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/>.

The six corpus-neutral Draft 2020-12 schemas for this adapter family are:

- `lane-adapter-v2.3.1.schema.json`;
- `capability-declarations-v0.2.schema.json`;
- `namespace-crosswalk-v0.2.schema.json`;
- `translation-state-index-v0.2.schema.json`;
- `csv-projection-manifest-v0.2.schema.json`; and
- `scope-declaration-v0.2.schema.json`.

### Corpus-neutral D60 lane adapter v0.1.0

The third admitted implementation is the D60 Algebraic Topology lane adapter
at `extensions/d60-algebraic-topology-v0.1.0`, distributed with central release
v0.62.10. It projects the final owner-bound v0.31.7 edition without copying
reader prose and without replacing the owner's 8,338 native backend records.
The canonical learner route remains the owner's readable HTML page:
<https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/>.

The adapter contains 27,642 canonical records covering 2,204 stable units,
2,174 content bindings, 2,204 evidence-bound translation-state rows, 1,337
relations, 96 component-rights declarations, 4,378 rights assignments, 258
artifacts, and 216 QA records. It proves 6,279 reversible materialized-native
mappings plus two explicitly scoped namespace rows. Nineteen JSONL tables have
nineteen lossless per-table CSV projections plus one global `records.csv`.
Two isolated builds, canonical-copy replay, packaged-validator replay, and ZIP
replay are byte-identical. Component rights remain unflattened and native
limitations remain explicit; the adapter does not upgrade missing native
anchors or replay evidence into invented conformance.

### Corpus-neutral D110 lane adapter v0.1.0

The fourth admitted implementation is the D110 Mathematics in Lean lane
adapter at `extensions/d110-mathematics-in-lean-v0.1.0`, distributed with
central release v0.62.11. It projects the complete Indonesian id.3 edition
without copying reader prose and without replacing the owner's 10,978 native
backend records. The canonical learner route remains the owner's semantic HTML
course:
<https://kokunoyumeto.github.io/mathematics-in-lean-id/>.

The adapter contains 41,460 canonical records in nineteen JSONL tables with
nineteen lossless per-table CSV projections plus one global `records.csv`. It
binds 1,213 source/target content pairs, 2,177 evidence-bound translation-state
rows, 9,272 reversible materialized-native mappings, 1,706 additional native
records by exact shard hash, and 9,272 component-rights assignments. Two
isolated builds, canonical-copy replay, packaged-validator replay, and
deterministic ZIP replay are byte-identical. Native `urn:mil:*` identities,
explicit prerequisite relations, draft asset states, and the distinction
between learner exercises and intentional solution demonstrations containing
Lean `sorry` remain explicit; an untagged PDF remains secondary to semantic
HTML.

### Corpus-neutral D20 lane adapter v0.1.0

The fifth admitted implementation is the D20 Functional Analysis lane adapter
at `extensions/d20-functional-analysis-v0.1.0`, prepared for distribution with
central release v0.62.12. It projects the complete owner edition and its
additive learner companion without copying the reader prose or replacing the
owner's 32,383 native records. The canonical learner route remains the central
course wrapper, which links the owner HTML reader, companion reader, PDF, and
preservation record:
<https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/>.

The adapter contains 138,894 canonical records in nineteen JSONL tables with
nineteen lossless per-table CSV projections plus one global `records.csv`. It
binds 4,161 translation-state rows, 16,260 source/target content bindings,
12,135 formula-alignment records, 9,572 typed relations, 5,136 learner routes,
32,383 reversible native bindings and crosswalks, 2,104 additional native index
rows, and four separately preserved rights components. Two isolated builds,
all 59 frozen authority replays, structural coverage, reverse extraction,
privacy checks, JSONL/CSV round trips, and deterministic ZIP replay pass. The
case-sensitive native identities `exam_dual_C0` and `exam_dual_c0`, anchor-only
routes, and external endpoints remain explicit rather than being normalized
away.

A00, B10, D20, D60, and D110 are five lane proofs. They are not a declaration
that the other 35 course roles conform to v2.3.1.

## Design proposal retained separately

The following six older files under `schema/` remain an unadmitted design
proposal retained for historical comparison:

- `backend-v2.3-extension.schema.json`;
- `capability-declarations-v0.1.schema.json`;
- `csv-projection-manifest-v0.1.schema.json`;
- `namespace-crosswalk-v0.1.schema.json`;
- `scope-declaration-v0.1.schema.json`; and
- `translation-state-index-v0.1.schema.json`.

They document a possible successor contract, but they are not the schemas that
validate the admitted v0.1.1 package and must not be presented as such.

## Boundary

JSON, JSONL, and CSV are machine exchange surfaces. Students should enter
through the program landing page and each course's readable HTML, PDF, or EPUB
route. Future v2.3 lane packages may be admitted only after owner-bound source,
terminology, mathematical-preservation, asset, rights, accessibility, build,
and publication evidence passes deterministic validation and anonymous public
readback.
