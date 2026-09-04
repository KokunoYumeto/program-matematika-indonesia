# Native-family public evidence routes: v0.62.13 local addendum

Recorded 2026-08-31. This is a bounded, metadata-only provenance audit of four frozen v0.62.13 files. The addendum is local next-step support outside the Site checkout. It was not published by this audit and must not be represented as an artifact already included in the v0.62.13 release. It is not a blocker for the independently handled release and does not supersede released bytes.

## Result

The comparison contains 33 native-family findings covering 40 unique curriculum roles. None of the 33 findings contains a claim-specific public source URL, artifact hash, or evidence locator. All instead inherit one shared unpublished audit-cursor reference.

A manual role join, reproduced deterministically by the companion script, exposes eight distinct hash-bound native backend-containing package URLs across seven roles and six families. These are metadata routes, not proof of current public availability, archive contents, historical finding support, or native replay.

| Measure | Result |
|---|---:|
| Native families / unique role bindings | 33 / 40 |
| Findings with claim-specific public citations | 0 |
| Findings missing claim-specific public citations | 33 |
| Unique native backend-containing package URLs | 8 |
| Package-covered roles / families | 7 / 6 |
| Roles / families lacking a native-package route in the four files | 33 / 27 |
| Backend packages with exposed byte counts | 2 |
| Backend packages with byte count null | 6 |
| Additional source-only ZIP / native release manifest | 1 / 1 |
| Central adapter rows, counted separately | 5 |
| Missing edition pointers / primary learner URLs | 0 / 0 |
| Network fetches / native backend replays performed | 0 / 0 |

The disjoint family classification is six with native-package routes, four with central-adapter routes but no native-package route, and 23 with only edition/repository/reader-level native pointers. Thus 27 is the count lacking native-package evidence; 23 is the edition-only count after separating the four adapter-only families. These denominators are not interchangeable.

Missing route evidence does not mean a missing, unpublished, or nonfunctional native artifact. No such negative claim is made.

## The eight native-package routes

The JSON index preserves exact URLs, SHA-256 values, exposed byte counts, and source JSON pointers. All capsule line references are one-based; pointers address the individual JSON object on that JSONL line.

| Role | Source location in course-capsules-v1.jsonl | Route identity | Exposed bytes |
|---|---|---|---:|
| A10 | Line 2, /layers/federation/components/1 | Zenodo 22163663; backend-core ZIP | null |
| B20 | Line 6, /layers/federation/components/1 | Zenodo 22164136; CLP1 backend ZIP | null |
| B50 | Line 9, /layers/federation/components/2 | Zenodo 22163372; CLP3 source-backend ZIP | null |
| D10 | Line 29, /layers/learner/portable_html | GitHub v1.0.0; Fremlin source-backend ZIP | 15167715 |
| D40 | Line 32, /layers/federation/components/1 and /layers/learner/portable_html | Zenodo 22184259; complete D40 ZIP | 9436983 |
| D40 | Line 32, /layers/federation/components/2 | Zenodo 22161412; Unit 14 source/backend ZIP | null |
| D60 | Line 34, /layers/federation/components/1 | Zenodo 22168033; editable-source-backend ZIP | null |
| D80 | Line 36, /layers/federation/components/1 | Zenodo 22167691; semantic-backend ZIP | null |

The two D40 references to the complete ZIP are one URL/hash identity, not two artifacts. D10 is indexed under a learner delivery field; its package filename indicates source/backend content, which was not inspected. The six covered families are A10, CLP, D10, D40, D60, and D80. CLP coverage is partial: B20 and B50 have package links, while B30 and B60 do not.

A10 also exposes a separate hash-bound source-only ZIP. D40 exposes a 92798-byte release manifest. These are useful provenance routes but are not added to the eight backend-package count.

## Evidence boundaries that remain separate

- Historical claims: source patterns /families/0 through /families/32 and methodology lines 36 through 100. Shared provenance is patterns /source_evidence, explicitly marked unpublished. A cursor hash is an identity check, not a public evidence route.
- Native packages: source-declared URLs and hashes only. No endpoint, archive member, validator, reconstruction, or replay was tested.
- Central adapters: five rows with exact asset URL/hash/bytes. Four declare public readback verified; A00 still declares pending release in the frozen adapter index. Those labels are retained, not upgraded.
- Learner use: only A00's central adapter declares direct consumption of adapter outputs. The other four explicitly declare course-link-only relationships. Primary learner URLs do not independently prove backend consumption.
- Receipt locators: three D20 capsule receipts point to private logbook-relative paths. Their values are omitted from the sanitized index; exact source JSON pointers, kinds, lengths, and hashes are retained. Repository-relative receipt paths are also not silently treated as resolved public URLs.

No adapter-admission claim is converted into a native-family replay claim. No published edition is treated as evidence that its underlying backend replays.

## Snapshot separation

The A10 comparison reports 452387 records while the capsule note reports 449680; no exact snapshot relationship is provided. B20's current edition record is 22183943 while its backend link is 22164136. B50's current edition is 22184443 while its backend link is 22163372. D40 exposes both Unit 14 and completed packages without assigning historical findings to either.

These are unresolved provenance relationships, not demonstrated artifact failures. Successor package metadata is not silently promoted to support historical numeric or engineering claims.

## Smallest useful next addition

The index supplies an additive evidence-route layer, not new owner backends or another adapter rollout. A future bounded extension can bind each historical claim to the exact audited snapshot, public artifact URL/hash/bytes, archive member or record, public validator/replay command, and sanitized result receipt.

Keep metadata availability, public readback, historical claim support, native replay, central adapter admission, and learner consumption as separate states. Fill missing routes from independently verified evidence when available; preserve null byte counts and explicit uncertainty otherwise. Missing human evidence or these provenance gaps impose no release hold.

## Reproduction and verification

The companion NATIVE_FAMILY_PUBLIC_EVIDENCE_REPLAY_V06213_20260831.ps1 reads exactly the four release inputs, checks their frozen byte counts and SHA-256 values, reconstructs all 33 families and 40 role bindings, resolves constructed JSON source pointers, and compares the result with the persisted JSON. It makes no network request and writes no file. Invoke it without arguments from PowerShell to verify; -Emit prints the reconstructed index to stdout.

The script derives the exact release directory relative to its logbook directory. Its default index target is the companion JSON in that same directory. No broad filesystem or repository scan is performed.

Source identities:

| Source | Bytes | SHA-256 |
|---|---:|---|
| modular-backend-pattern-index-v1.json | 41452 | 89436f3c319057a87aef82aae7e53f5a0c484193cd92a9c8e293f1b52198f391 |
| course-capsules-v1.jsonl | 226934 | 2c885781e9b69de6afdc2cbfe8e7d95d26ba97f0ffe571a12b4ec1ead575d6d1 |
| v23-adapter-index-v1.json | 11370 | 31e45fc3a852b1d1b7742ac66d5d919aa1d229feff408913951018451f755381 |
| MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md | 32070 | c30745104ae42a0f29aa3399bb4ef3415c413dba241b1ac494525759214e5536 |

Persisted verification passed on 2026-08-31: all four frozen source hashes matched, all 382 constructed JSON source pointers resolved, the JSON index matched deterministic reconstruction, and sanitization checks passed. The reconstruction again yielded 33 families, 40 unique roles, and eight native-package URLs covering six families. It performed zero writes, network fetches, or native replays.

Verified output identities (this note is intentionally not self-hashed):

| Output | Bytes | SHA-256 |
|---|---:|---|
| NATIVE_FAMILY_PUBLIC_EVIDENCE_INDEX_V06213_20260831.json | 223185 | a8eca1964dcd34ccf7a67a9e9fff1c3c9f061b1b8c74ff8974fe1f4053a173bb |
| NATIVE_FAMILY_PUBLIC_EVIDENCE_REPLAY_V06213_20260831.ps1 | 28670 | e1dfc2a425eda44c566e6e2c99bc4026ee0821f020ec1e63d302731b35f1233d |

Completed: bounded source identity checks, route extraction, classification, durable index, replay script, and persisted-index verification. The companion script can rerun the same bounded verification without changing state. Further public-byte or historical-claim work is a separate authorized step; this audit does not start it.
