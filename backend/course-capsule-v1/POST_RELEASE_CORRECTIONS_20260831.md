# Post-release integration corrections — 2026-08-31

The immutable v0.62.13 GitHub and Zenodo release remains public and unchanged.
Zenodo record 22207081 contains 100 files, 460,869,686 bytes, aggregate SHA-256
`fa645e4b54973bc750ec6734a3195e22a0ade1d38cbf7f6497c4c1cbab4103ec`.
It was anonymously reverified; the public source commit for that archived
snapshot is `4ab6eb6b270dc0a32512dad3f998653c336d8492`.

The subsequent live-source update corrects:

- Dynamic loading failure or pending filters no longer erase the forty
  server-rendered course links. The no-JavaScript catalog stays usable.
- All four summary figures are generated from the same capsule data: 40
  courses, 35 completed editions, five producing, 21 educator-indexed courses.
- Nineteen unindexed educator capabilities are `unknown`, not evidence that
  those materials have never been produced. Explicit authority statuses are
  preserved. Seventeen similarly unindexed alignment states become unknown.
- A workspace-relative C120 evidence locator is retained as provenance but
  not rendered as a public hyperlink. No replacement URL was invented.
- A partial delivery resource is labeled as a course part. In particular,
  D40's old chapter reader remains available beside its complete public PDF.
- D40's course wrapper points to the complete 679-page edition at record
  22184259. Its producer-level GitHub gap is not silently erased.
- The comparison index's current-role overlay is 35/5/31, matching the
  archived capsule snapshot. Its original 33-family comparative findings
  remain historical evidence. The archived index's 33/7/29 overlay is stale.
- Pattern and adapter index links are included in the generated Sites mirror.
- Explicit NDJSON headers apply in the local preview; production `_headers`
  use supported named placeholders. GitHub Pages' JSONL download uses
  octet-stream; the live browser consumes application/json.
- Native toggle-button semantics replace incomplete ARIA tab semantics.
  Methodology remains visible below the working course catalog.

Validation completed before publication includes two byte-identical capsule
builds, forty schema instances, seven layers each, 83-edge prerequisite DAG,
seven DOM-stub UI scenarios, three rejection/mutation tests, the complete
central prebuild/build, and 32 exact local HTTP/MIME checks. Browser clicking,
searching, filtering and evidence-label checks passed. Browser automation did
not produce native activation from Enter/Space despite focusing a native
button, so keyboard activation is not claimed as empirically verified.

This update implements course-level interfaces; it does not claim every
course-native capability exists or has been independently verified. Five
semantic adapters are evidenced; 35 other roles remain native-only. The
educator index covers 21 courses, with 19 unknown and one indexed course still
in progress. Unit-level normalization and complete native backend replay are
not implied by successful capsule generation.

The existing Sites project currently returns project-not-found. No substitute
project, duplicate release, access restriction, or production-task edit was
made. GitHub Pages is the current public website. A preservation successor for
these post-seal corrections remains separate from the immutable v0.62.13
transaction; do not misstate its archive as containing this newer source.
