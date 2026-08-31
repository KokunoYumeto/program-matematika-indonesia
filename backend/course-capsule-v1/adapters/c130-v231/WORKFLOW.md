# C130 Operations Research v2.3.1 adapter workflow

## Purpose

This lane adapts the completed Indonesian Operations Research edition into the
common modular-backend contract without copying textbook prose into the central
backend. The owner repository remains authoritative for content, translation,
builds, rights, readers, corrections, and publication.

## Fixed scope

- Curriculum role: `C130` — Mathematical Programming / Operations Research.
- Corpus: R017 Book 1 plus the separately attributed O018 Pyomo + HiGHS
  adaptation already incorporated by the owner.
- Explicit exclusion: Book 2 / advanced optimization is not represented by
  this adapter and must not be inferred from the C130 binding.
- Owner root: `04_mirrors/id/open-optimization-or-book-id`.
- Common-backend version: `2.3.1`.

## Projection rules

1. Replay the frozen owner-native backend and publication evidence.
2. Preserve all 1,993 owner unit identities, all 5,525 segment identities as
   zero-copy native bindings, all 9,545 typed owner relations, and all 21
   component-rights records.
3. Mint only stable UUIDv5 projection identifiers; retain each owner-native ID
   and reversible mapping in payloads and crosswalks.
4. Do not centralize full source or target prose. Content bindings carry only
   paths, byte counts, hashes, line spans, locale/state, and topology metadata.
5. Keep learner routes truthful: repository, GitHub Pages landing page,
   666-page PDF, Zenodo, and published source/lab/backend packages. Do not
   claim native chapter HTML, unit/page anchors, or PDF/UA conformance.
6. Preserve component rights rather than flattening the mixed content, code,
   dependency, and third-party licenses into one license string.
7. Emit all 19 canonical JSONL tables, lossless CSV projections and aggregate
   `records.csv`, and the five v0.2.0 conformance sidecars.

## Deterministic gates

The adapter is deliverable only after two absent-directory builds are
byte-identical; generic and C130-specific validators pass; at least twelve
isolated negative probes are rejected; a separate read-only audit passes; the
ZIP member order is ordinal POSIX-path order with fixed metadata; the ZIP opens
and every member byte matches; and the manager handoff binds the final tree,
ZIP, reports, authorities, and integration boundary.

Central admission and central publication remain separate actions owned by the
program landing-site task. This candidate does not mutate the C130 owner tree or
the central repository.
