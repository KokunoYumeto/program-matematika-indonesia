# Common-backend v1 migration handoff

This is an additive interoperability handoff. It does **not** restart a
translation, change a corpus's selected architecture, rename admitted units,
replace its native backend, or delay an in-flight unit/publication transaction.

## Frozen contract

- Public repository: <https://github.com/KokunoYumeto/program-matematika-indonesia>
- Frozen tag: `v0.42.0`
- Tagged commit: `98334fed7e1f0af81f7901d2b565348260b16b0e`
- Backend schema: `schemas/backend-v1.schema.json`, 126,423 bytes, SHA-256
  `3de8d107b1c75db0f8d60c42ef7e3488bc3fcc93f72e955def71a771475cf2b2`
- Source-format profile schema:
  `schemas/profiles/source-format-profile-v1.schema.json`, 12,228 bytes,
  SHA-256
  `2bb1429c36236329be94d58205b6123a0266a1e111277e3d303692ca8430e271`
- Identity namespace: `7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd`; identity formula
  `UUIDv5(namespace, record_type|stable_key)`.

## Timing gate

Finish and freeze the lane's current unit, build, or publication transaction
first. Begin the adapter only at a boundary where the native manifest, reader,
backend, source cursor, public receipt, and hashes agree. If that boundary is
not clean, record the adapter as pending; do not interrupt production to make
it look current.

## One-time Indonesian field-terminology QA at the same boundary

Before scaling further translation after this boundary, perform one evidence-
based terminology comparison for the corpus's mathematical field. Prefer a
reasonably representative Indonesian-language arXiv work with a downloadable
source package; unpack it and inspect the actual TeX terminology. If no
suitable Indonesian arXiv source with downloadable TeX exists, inspect a
representative Indonesian-language DOCX or PDF elsewhere and record that
fallback honestly. Do not infer terminology from titles or abstracts alone.

Compare the witnessed field terms with the edition glossary and translated
text. Decide differences from mathematical meaning, consistency, and actual
Indonesian field convention. Propagate only justified corrections through the
already admitted material, then rerun the lane's normal structural, math,
language, build, and reader gates. Emit one sanitized
`TERMINOLOGY_QA_RECEIPT.json` identifying the source, downloaded evidence and
hash, terms compared, decisions, changed files, and replay result. Preserve all
source, author, and human-contributor credits. Add this exact model provenance
to the edition/repository/release metadata: `OpenAI Codex gpt-5.6-sol, Ultra`.
This QA requirement is additive and must not overwrite corpus authority.

## Required migration behavior

1. Freeze the exact native input package, schema/version, record count, source
   and target identities, public release identity, and cryptographic hashes.
2. Classify the operation honestly:
   - a lossless header/profile upgrade when native records already conform;
   - an additive adapter when native tables carry equivalent facts under a
     different shape;
   - a deterministic source/target reconstruction when the frozen release has
     manifests and payloads but no materialized backend.
3. Preserve every native ID that already meets the common identity invariant.
   When new UUIDv5 IDs are required, derive them only from source authority,
   edition, native identifier, structural path, or declared source order—never
   translated wording, page number, layout, mutable publication state, or a
   content hash alone.
4. Keep locale-neutral `segments` separate from `segment_variants`. Bind each
   format-specific identity through the strict source-profile extension
   (`cnxml`, `pretext`, `latex`, `lyx`, `mediawiki`, or `html_pressbooks`).
5. Preserve component rights, rights assignments, source/target revisions,
   exercise/answer/solution relations, build recipes, QA evidence, artifacts,
   release snapshots, routes, and alignments whenever the native lane has them.
   Do not invent absent evidence.
6. Validate strict schema conformance, deterministic ordering, global ID
   uniqueness, foreign-key closure, canonical JSONL, and lossless CSV if those
   projections are materialized. For a zero-copy adapter, assemble and validate
   the complete virtual record stream twice and bind its byte count/SHA-256.
7. Emit one sanitized `MIGRATION_RECEIPT.json` conforming to
   `schemas/backend-migration-receipt-v1.schema.json`. It must identify source,
   target, transformation, record/table counts, validation results, public
   artifacts, materialization decision, and hashes without credentials.
8. Return only the frozen receipt/path and public release handoff to root.
   Root consumes it read-only into the central catalog. Do not create a new DOI
   concept or duplicate repository solely for an adapter.

## Completed proofs

- DMOI 4 Indonesian: 163,583 records, 32 source tables, exact reverse, zero
  changed IDs and zero changed payload fields.
- B80 mathematical computing Indonesian: all 326 native catalog entries are
  checksum-bound and exactly reversible; eight derived rights records and five
  external-reference anchors yield 339 strict common records across 38 tables.
- Open Logic OLP-0722 Indonesian: deterministic zero-copy reconstruction from
  722 frozen English files, 722 Indonesian files, their exact manifests, 725
  import relations, and the existing GitHub/Zenodo release; 6,522 validated v1
  records with no source or target payload-byte changes.
- Judson abstract algebra Indonesian: additive zero-copy adapter over the
  immutable public `v2026.08.21.1` source/backend archive; 24,733 native rows
  yield 36,978 validated common records, with 24,483 native IDs preserved and
  two byte-identical virtual streams.
- Yet Another Introductory Number Theory Textbook Indonesian: 5,272 native
  records reverse exactly from 6,967 validated common records; all native
  projections, assets, artifacts, reader evidence, and three public snapshots
  remain bound, with two byte-identical virtual streams.
- Mathematics in Lean Indonesian v4.30.0-id.3: 10,978 native records map
  one-to-one to 10,978 common records and reverse exactly; 38/38 tables are
  present, 14 are populated, two complete executions emit the identical
  receipt, and public GitHub/Zenodo/Figshare archive identity is bound. The
  receipt explicitly adjudicates the isolated 10,876 owner-receipt typo from
  the public `records.jsonl` bytes without rewriting the owner lane.
- Applied Combinatorics Indonesian: 19,048 unique native records map one-to-one
  and reverse exactly; one explicit B10 external-prerequisite stub yields
  19,049 strict common records with complete foreign-key closure.
- OpenStax Prealgebra 2e Indonesian v0.2.7: all 519,678 owner-native records
  reverse byte-identically from the zero-copy stream; 3,368 deterministic
  records yield 523,046 strict common records across 38 tables. Two independent
  assemblies agree exactly. The proof explicitly closes 75 CNXML modules, 60
  CollXML bindings, 98 target-only structural units, 408 target-only correction
  segments, and 183 unique HTTPS external targets without inventing XML
  authority. Receipt SHA-256: `50093021475d3757ab71395d5bf34f672c18a6714122093b040021c18f333152`.
- Mathematical Modeling and Nonlinear Dynamics Indonesian: 4,941 direct native
  records, six common anchors, 81 exact file anchors, 7,553 derived segment
  variants, and 3,448 translation alignments yield 16,029 strict common records
  across all 38 tables. Two independent authority reads and assemblies are
  byte-identical, and the native backend and logical records reverse exactly.
- Open Optimization OR-Book Indonesian: all 17,987 native records project
  directly and reverse exactly; 7,818 derived source/target segment variants
  yield 25,805 strict common records. Native payload bytes are unchanged,
  foreign keys close, and two independent common assemblies agree.

These proofs establish the contract. They are not instructions to overwrite a
lane's stronger native representation.
