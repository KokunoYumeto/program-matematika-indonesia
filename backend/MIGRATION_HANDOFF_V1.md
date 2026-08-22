# Common-backend v1 migration handoff

This is an additive interoperability handoff. It does **not** restart a
translation, change a corpus's selected architecture, rename admitted units,
replace its native backend, or delay an in-flight unit/publication transaction.

## Frozen contract

- Public repository: <https://github.com/KokunoYumeto/program-matematika-indonesia>
- Frozen tag: `v0.41.0`
- Tagged commit: `3efd67eb52dc7c5749d1c1bbc741a7970cd2ba46`
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
- Open Logic OLP-0722 Indonesian: deterministic zero-copy reconstruction from
  722 frozen English files, 722 Indonesian files, their exact manifests, 725
  import relations, and the existing GitHub/Zenodo release; 6,522 validated v1
  records with no source or target payload-byte changes.

These proofs establish the contract. They are not instructions to overwrite a
lane's stronger native representation.
