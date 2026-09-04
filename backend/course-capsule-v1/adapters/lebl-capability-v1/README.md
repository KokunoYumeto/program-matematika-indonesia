# Lebl shared learning capability

This adapter connects B70 Differential Equations, C10 Real Analysis I, C20 Real
Analysis II and C50 Complex Analysis to the existing Lebl family. It preserves
native identities rather than translating or replacing the books.

Learners can navigate four Indonesian PDFs and find exercise records with their
source identities and support evidence. Teachers can select those same records
and copy a plan containing source/translation selectors, learner links and
honest solution states. The terminology register retains preferred terms,
alternatives, rejected forms and evidence without imposing a universal canon.

## Design and evidence

- Contract: `lebl-learning-capability/1`, not a claim of 2.3.1 compliance.
- 5,932 unit records, 2,203 exercise records, 827 terms, four PDFs/1,415 pages.
  Editorial and logical units overlap; these are not distinct workload counts.
- 541 typed support links; all source completeness states remain unchanged.
  An unknown solution state does not become complete because a link exists.
- C20 includes sequence-of-functions and metric-space material in Volume I,
  as well as Volume II. The two-volume exercise bank is not an assertion that
  every exercise is required for C20.
- PDF links use unique matching ancestor headings; they are not verified
  exercise page coordinates. Unmatched records link to the book.
- `native-evidence-binding.json` binds frozen metadata and the line index to an
  independently reread, pinned public native stream. The historical PDF and
  TeX-entrypoint observations are separately identified.
- The manifest and learning map distinguish intake losses from capability
  losses. Uncopied metadata remains in frozen intake or the pinned original.
  No complete native roundtrip, source-span replay, book rebuild, visual review,
  PDF accessibility certification or linguistic certification is claimed.

## Reproduce

With Node 22, Python 3 and `jsonschema` available, run from the project root:

    node scripts/build-lebl-capability-v1.mjs
    python -B scripts/validate-lebl-capability-v1.py

Ordinary builds verify the existing source binding offline. Do not rerun the
original importer or overwrite frozen intake. The separate `--bind` operation
is create-once and downloads only the pinned dataset and record stream.

Validation checks schema, all retained identities and promised fields, exact
support-evidence unions, generated teacher-plan attributes, five source-binding
mutations, model/support mutations, actual shipped filter/planner behavior,
local links and two isolated byte-identical builds.

Open `docs/backend/lebl/B70.html` (or C10/C20/C50), `*-pengajar.html` for the
teacher tools, and `istilah.html` for terminology. Navigation can be saved
locally; linked PDFs require separate downloads. No learner data is collected.

The complete 40-role modular backend remains in progress. This is a bounded,
tested capability integration, not overall program completion.
