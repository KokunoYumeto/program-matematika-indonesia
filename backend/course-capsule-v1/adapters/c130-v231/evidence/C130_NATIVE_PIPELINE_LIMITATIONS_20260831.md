# C130 owner-native pipeline limitations — 2026-08-31

This is a bounded, read-only audit of historical owner-generator code. It does
not invalidate the frozen backend byte identities or the public edition. It
does limit what the common adapter may claim without independently replaying
the underlying evidence.

## Verified limitations

### Archive/extraction equivalence is aggregate-only

`scripts/build_machine_backend_evidence.py` reads the submodule archive
inventory but compares the extracted tree only by total file count and total
uncompressed bytes. It does not compare member paths or per-file hashes and
does not exercise the ZIP members through `testzip()`. Equal counts and total
bytes therefore do not prove archive-to-extraction byte identity.

### Public-package evidence checks member names, not member bytes

The same script reduces the public source package to a set of ZIP member names.
Its witness rows record presence but do not compare each public member's bytes
or SHA-256 with the owner target, reject duplicate ZIP members, or exercise CRC
closure. The common adapter may reference the recorded public-package witness,
but it must not restate it as independently proven public byte identity.

### Authority hash guarding can be absent

An existing machine-evidence row is guarded only when its `source_sha256` value
is truthy. A missing or empty source digest therefore bypasses the comparison.
The v2.3.1 adapter must instead bind the complete native monolith, manifest and
checksum inventory as frozen external authorities and validate their current
bytes directly.

### Laboratory results are parsed but not reconciled

`scripts/update_backend_full_book.py` parses each `results.json` but does not
reconcile its values, exercise IDs, methods or result digest with the
verification receipt or `data.json`. Exercise-to-source relations are assigned
positionally from `exercise_order`, bounded only by a configured count.

### Laboratory QA pass rows can contradict receipt counters

The update script always emits four completed/pass QA events. Its functional
test witness formats the message as `tests/tests` while separately reporting
the receipt's failed-test count; unresolved exercises, zero runs, digest drift,
or `verified_count != exercise_count` do not themselves stop those emitted pass
records. Required asset relations are also created independently of a final
foreign-key closure check.

### Full-book closure claim is broader than the code establishes

The script emits a completed full-book QA event claiming fail-closed exporter
alignment and reference checks, but the shown update path enumerates source
structure and hard-coded mappings without itself replaying all target alignment
and reference invariants. It also replaces the Book-1 `concept_ids` list with
the union of a chapter table that covers only Chapters 10–15.

## Adapter treatment

- Preserve all 101 owner-native QA events and their exact native states as
  provenance; do not reinterpret them as independent v2.3.1 validation.
- Emit one separate adapter-build QA event covering only the checks actually
  replayed by the adapter.
- Bind owner artifacts, units, segments, relations and component rights by
  current bytes and reversible identifiers.
- Declare the owner-generator limitations in the capability loss/gap reports.
- Do not claim public-member byte identity, archive/extraction equivalence,
  laboratory semantic correctness, native HTML, unit anchors, or PDF/UA unless
  a separate deterministic replay proves that specific property.
- Keep the completed learner edition public and learner-facing; this audit is a
  provenance qualification, not an access restriction or publication hold.
