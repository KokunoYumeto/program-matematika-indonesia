# D60 study and teaching navigator

This increment exposes the existing Algebraic Topology backend to learners and
teachers: search, stable unit selection, exact reading links, staged native
hint/answer/solution links, and local JSON/text plan export. It does not rewrite
the textbook. English and Indonesian are interface languages; the reading
content in this projection is Indonesian.

## Reproduction

From the program repository, run `npm run build:d60-surface`. The committed
reader witness and the existing v2.3 D60 unit/relation tables are sufficient.
No network or producer checkout is required for ordinary replay. Source
identities are verified before projection; two independent builds must match
the canonical outputs. Admission changes only D60 and preserves other flags.

To intentionally refresh the witness, run
`python -B scripts/intake-d60-reader-witness.py --native-root PATH --verify-public`.
It checks native-table hashes and compares the complete current public course
body with the local reader after CRLF normalization. The navigation wrapper,
historical reader identity, current reader identity and native identity remain
distinct. It extracts actual `source_local_id` values, never inferred suffixes.

## Boundaries

- 2,204 current native units; 2,166 exact unique anchors; 38 explicitly labelled
  full-course fallbacks. Current revisions are preserved without collapsing
  ambiguous historical branches.
- 266 exercises, four questions, eight proof checks. All 480 explicit
  hint/answer/solution relations have exact identity joins. Missing relationships
  mean unknown coverage, not absent solutions.
- Teacher alignment is exact selection and support mapping. No new syllabus,
  grading system, automatic prerequisite diagnosis or learning outcome is claimed.
- Full native build replay, terminology verification and complete course-level
  backend parity remain separate requirements; this increment does not certify them.
- Plans contain metadata and links, not an offline copy of the complete book.
  No personal data, tracking, browser storage or server submission is used.
- `tests.json` records negative fixtures and deterministic replay. Browser QA
  is recorded separately and is not inferred from the structural tests.
