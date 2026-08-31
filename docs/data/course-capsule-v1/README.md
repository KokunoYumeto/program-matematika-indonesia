# Open course capsule v1

This is the reduced interoperability contract for the forty-role Indonesian
mathematics program. It is learner-directed and open. A producer task,
repository, or maintainer is an operational custodian, not an owner of the
course or its learners.

The capsule does not replace a course-native canonical source or backend. It
provides a small, deterministic index over that representation so a course can
be navigated, taught, rebuilt, remixed, and connected to the global curriculum
without copying its full prose, formula graph, source tree, or historical QA
archive.

## Seven required layers

Every capsule contains all seven interfaces:

1. `curriculum` — course identity, outcomes, prerequisites, route identity, and
   the state of unit-level identity.
2. `translation` — source/target locale, terminology, rights, corrections, and
   translation-ledger capability.
3. `production` — build, deterministic replay, repository, edition, DOI, and
   release state.
4. `learner` — online, PDF, EPUB, portable HTML, accessibility, other
   learner-delivery capabilities, and verified human-facing learner tools.
5. `educator` — outcome/evidence maps, diagnostics, lesson and pacing plans,
   worked examples, exercises, staged support, assessments, rubrics,
   misconceptions/interventions, activities/labs, accommodations, and remix
   selectors.
6. `federation` — primary work, donors, supplements, editions, and course views
   linked without copying their content.
7. `interoperability` — the capsule mapping itself and any deeper semantic
   adapter, with course-native identity preservation and explicit scope.

All layers are mandatory, but unsupported capabilities are recorded honestly as
`not_yet_produced`, `not_applicable`, or `unknown`. A large empty table is not a
substitute for evidence.

## Authority and public access

- Course-native sources/backends remain canonical.
- Learner and educator views share stable course, unit, concept, exercise, and
  artifact identities when those identities are available.
- Rights and license records preserve attribution and remix compatibility; they
  never impose an access restriction.
- The capsule forbids private, restricted, embargoed, or download-disabled
  access states.
- JSONL is the canonical exchange. CSV, SQLite, Parquet, or search indexes are
  optional generated views for concrete consumers.
- No personal profile paths, credentials, tokens, or private task metadata may
  enter a public capsule.

## Generated artifacts

`generated/course-capsules.jsonl` contains one canonical JSON object per role,
sorted by curriculum role. `generated/manifest.json` binds all inputs and the
JSONL output. `validation/VALIDATION_RECEIPT.json` records independent structural,
graph, public-access, evidence, canonicalization, and two-build replay checks.

The first version is intentionally course-level. Unit-level crosswalks and
educator resources can be added without changing course identities or copying
course-native content.

`backend/authority/learner-tools-v1.json` is an exact build input. Every
capsule carries a `layers.learner.tools` array: it is empty when no tool has
been admitted and otherwise preserves the authority row byte-for-byte at the
JSON-value level. A tool's `href` must lead to a readable HTML interface;
machine resources and validation evidence remain bound file facts, never the
student-facing destination.
