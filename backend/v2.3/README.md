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

The B10 extension is a second lane proof, not a declaration that the other 38
course roles conform to v2.3.1.

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
