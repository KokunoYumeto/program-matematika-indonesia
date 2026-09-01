# CLP v2.3.1 successor integration plan (read-only draft)

This is a bounded implementation plan for admitting the sealed CLP family package
once, binding it to B20/B30/B50/B60, and exposing its seven learner PDF actions.
It is deliberately a plan rather than a release: no existing generator, overlay,
generated output, owner tree, Git ref, or public record is changed by this file.

## Current boundary and source identities

The v0.62.16 release remains the public predecessor.  The checked-in successor
projection has now replayed and locally admitted the CLP package (9 packages,
13 bindings, 9 represented families; four of those bindings are CLP1–4).  The
four native CLP editions were already complete and public; only the central
successor publication/readback remains outstanding.  Preserve that distinction:

| input | identity to verify before admission |
| --- | --- |
| candidate package | `urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26`, adapter `0.1.0`, family `family-06-clp` |
| candidate ZIP | 545,418,367 bytes; SHA-256 `f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d` |
| build-A manifest | `build_a/manifest.json`, 31,266 bytes; SHA-256 `54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5` |
| sealed package tree | 70 members / 6,591,980,682 uncompressed bytes; full-tree SHA-256 `2e0f5db2b0e13c2f30bde9cf37128182e80d886ba53f1caafddad0aa43fff2e4` |
| candidate route authority | `research/CLP_LEARNER_ROUTE_EVIDENCE.json`, 28,779 bytes; SHA-256 `d806aee1d1ac177d9ad41844d847f5d4d1abf6895de47b6eedbb7c5e17c262e9` |
| candidate superseding audit | `CLP_FINAL_INDEPENDENT_PACKAGE_AUDIT_SUPERSEDING_20260901.json` (PASS, zero blocking defects) |
| dataset / extension | `urn:uuid:5276fa22-58b4-5bf8-b84b-3de141f617d5` / `urn:uuid:fb88c199-de1a-587b-9824-37fc25c797a0` |

The current predecessor authority that the next snapshot should name is
`v0.62.16`, GitHub source commit
`42a0656177376d5021a014f3e4d5ae6419d07ae5`, source tree
`aa648184b56242f1a234c72d55e0d6d44a317b6c`, Zenodo version DOI
`10.5281/zenodo.22231858`, concept DOI `10.5281/zenodo.22059707`, with
anonymous readback receipts `GITHUB_PUBLICATION_RECEIPT_v0.62.16.json`
(`pass_112_of_112`) and `PUBLICATION_RECEIPT_v0.62.16.json`
(`pass_100_of_100`).  These values come from the sealed intake status and must
be re-read, not copied from the older v0.62.14 overlay.

The candidate directory is under the workspace `outputs/` tree, outside this
project.  The successor builder must either stage the exact ZIP and manifest at
stable project-relative paths (recommended for public inventory), or use a
resolve-safe external intake path for local validation while emitting only the
staged project-relative path.  Never put a workspace path, `..`, a user path, or
credentials in a public JSON/receipt.

## Admission state machine

1. **Locally admitted, pending public successor (current):** the sole
   integrator has replayed the package/seal/manifest and route evidence.  The
   projection contains one CLP package row with
   `admission_state: "admitted_pending_release"`, null release URLs, and
   `public_replay_status: "pending_release_local_seal_verified"`, plus four
   bindings pointing at it.  “Pending” here means only public successor
   publication/readback; it does not mean CLP translation is unfinished.
2. **Published successor:** after the actual next central release is created and
   all public bytes are anonymously read back, change that same package to
   `published`, fill the real release and asset URLs, and set
   `public_replay_status: "published_public_asset_readback_verified"`.

Do not invent a release version or URL.  The schema requires a non-empty
`planned_release.central_release_version`, `planned_release.artifact_path`, and
URI `planned_release.public_url_after_release`; supply those only when the
successor release plan has an actual version and asset URL.  A queued handoff is
not itself an admission.

## v2 adapter index projection

`schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json` already supports a
shared package and multiple bindings; no schema change is needed for the package
or the four roles.  Add one package object to the successor builder (the exact
archive/manifest paths are resolved at build time):

```json
{
  "package_id": "urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26",
  "native_family_id": "family-06-clp",
  "proof_kind": "reversible_lane_adapter",
  "contract_version": "2.3.1",
  "adapter_version": "0.1.0",
  "admission_state": "admitted_pending_release",
  "release_url": null,
  "public_asset_url": null,
  "public_replay_status": "pending_release_local_seal_verified",
  "adopted_capabilities": [
    "stable_owner_native_identity",
    "reversible_identity_crosswalks",
    "typed_owner_relations",
    "rights_assignments",
    "translation_state_evidence",
    "lossless_jsonl_csv_projection",
    "learner_pdf_authority"
  ],
  "known_limitations": [
    "The four owner-native CLP profiles remain authoritative; the package is a thin, zero-copy projection.",
    "Learner routes are seven whole-file PDFs only; no native HTML, chapter/unit anchors, fragments, EPUB, or portable HTML are claimed.",
    "The adapter is course-link-only and does not claim that the owner readers consume central machine tables.",
    "No cross-profile semantic equivalence beyond the evidence-bound identity/lineage rows is claimed."
  ],
  "archive": { "path": "<staged project-relative ZIP>", "bytes": 545418367, "sha256": "f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d" },
  "manifest": { "path": "<staged project-relative build_a/manifest.json>", "bytes": 31266, "sha256": "54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5" },
  "canonical_records": 1201557,
  "native_records_preserved": 289473,
  "reversible_native_mappings": 285630,
  "additional_native_index_rows": 3843,
  "rights_assignments": 283778,
  "reader_pages": 4077,
  "unit_records": 53676,
  "relation_records": 138673,
  "namespace_mappings": 285630,
  "public_artifacts": 5059,
  "native_html_claimed": false,
  "unit_or_page_anchors_claimed": false,
  "jsonl_csv_table_pairs": 19,
  "owner_native_authoritative": true,
  "zero_copy": true,
  "dataset_id": "urn:uuid:5276fa22-58b4-5bf8-b84b-3de141f617d5",
  "extension_id": "urn:uuid:fb88c199-de1a-587b-9824-37fc25c797a0",
  "scope_note": "One shared CLP family package binds four owner-native course views; machine tables are secondary and learner delivery is whole-file PDF only.",
  "planned_release": {
    "central_release_version": "<actual successor version>",
    "artifact_path": "<same staged project-relative ZIP>",
    "public_url_after_release": "https://github.com/<owner>/<repo>/releases/download/<actual-version>/<asset>",
    "state": "planned_not_public"
  }
}
```

`public_artifacts` is the number of rows in CLP `tables/artifacts.jsonl` (5,059),
not the seven learner PDFs.  Do not assert `source_translation_pairs`,
`reader_reachable_units`, or `retained_non_reader_units` unless a corresponding
candidate table and invariant is explicitly replayed.

Add bindings in this order, all with the same `adapter_package_id` and
`native_family_id`:

| role | learner URL (default action) | `course_specific_route_count` |
| --- | --- | ---: |
| B20 | `https://zenodo.org/records/22183943/files/00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf?download=1` | 2 |
| B30 | `https://zenodo.org/records/22182941/files/CLP-2_Kalkulus_Integral_Bahasa_Indonesia_edisi_lengkap_2026-08-30.pdf?download=1` | 1 |
| B50 | `https://zenodo.org/records/22184443/files/CLP-3-Kalkulus-Multivariabel-Bahasa-Indonesia.pdf?download=1` | 2 |
| B60 | `https://zenodo.org/records/22105443/files/CLP-4-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1` | 2 |

Use `learner_runtime_relationship:
"course_link_only_no_adapter_consumption_claim"` for all four.  Do not add a
`central_learner_projection` until an actual `docs/` page exists; an invented
projection path fails the schema/public-byte gate.

Expected v2 summary while the package is pending (derived, never copied from
prose):

```text
curriculum_roles                         40
role_bindings                             13 (9 published + 4 pending)
distinct_adapter_packages                 9 (8 published + 1 pending)
represented_native_families                9
unbound_roles                             27
families_without_local_adapter            24
families_without_public_replay_complete   25
package_deduplicated_canonical_records  1,487,386
```

After public readback, only the publication-state partition changes:
`published_role_bindings=13`, `pending_role_bindings=0`,
`published_adapter_packages=9`, `pending_adapter_packages=0`, and
`families_without_public_replay_complete_adapter=24`.

## Seven-action learner sidecar

The v23 adapter schema intentionally has no learner-action array, and the
existing `learner-tools-v1` schema requires a local HTML `href`, page/resource/
evidence files, and forbids raw machine destinations.  Do not overload learner
tools with PDF rows.  Add a small, separately versioned sidecar generated
mechanically from `CLP_LEARNER_ROUTE_EVIDENCE.json`, for example:

```json
{
  "$schema": "https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-reader-actions-v1.schema.json",
  "schema_id": "interlanguage/learner-reader-actions/v1",
  "schema_version": "1.0.0",
  "snapshot_id": "<successor adapter snapshot id>",
  "locale": "id-ID",
  "source": { "path": "<repo-relative route evidence>", "bytes": 28779, "sha256": "d806aee1d1ac177d9ad41844d847f5d4d1abf6895de47b6eedbb7c5e17c262e9" },
  "actions": [
    {
      "action_id": "B20:reader:textbook",
      "course_id": "B20",
      "order": 1,
      "label": "B20 — Buku teks (442 halaman)",
      "role": "textbook",
      "format": "application/pdf",
      "scope": "whole_course",
      "pages": 442,
      "bytes": 4997608,
      "sha256": "e0466ca75b793aed64e2c356014233d9e85072b077a3b2d3344926835c408ec2",
      "url": "https://zenodo.org/records/22183943/files/00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf?download=1",
      "state": "verified",
      "route_granularity": "whole_file_only",
      "evidence": { "kind": "receipt_bound_anonymous_public_readback", "locator": "https://zenodo.org/records/22183943", "status": "pass_receipt_bound" }
    }
  ],
  "summary": { "course_count": 4, "action_count": 7, "pages": 4077, "bytes": 35639691 }
}
```

The `actions` array contains the seven rows in family/course order: B20
textbook+problembook, B30 combined, B50 textbook+problembook, and B60
textbook+problembook.  Copy the exact `pages`, `bytes`, `sha256`, license,
filename, and URL from the route evidence; never derive page ranges or anchors.
If a fresh anonymous network readback has not run in this transaction, retain
`verification_scope: "pass_receipt_bound"` (or use `available_unverified`) rather
than claiming a new network check.  The postpublication validator must fetch
all seven URLs anonymously and upgrade the receipt to exact public-byte
readback.

Recommended generated/public projections (all from this sidecar, never hand
edited):

* `backend/course-capsule-v1/generated/learner-reader-actions-v1.json`
* `docs/data/course-capsule-v1/learner-reader-actions-v1.json`
* `docs/learner-reader-actions.js` (a tiny map keyed by course ID)

The sidecar can remain outside the seven-layer capsule to avoid changing the
immutable `course-capsule-v1.schema.json`.  If product requirements later place
actions inside each capsule, add an optional `reader_actions` property to the
learner-layer schema and update every schema/peer-replay validator together;
do not add an unrecognized property to current capsules.

The sidecar schema should be strict (`additionalProperties: false`): require a
unique `action_id`, `course_id` matching `B20|B30|B50|B60`, positive `order`,
`pages`, and `bytes`, a 64-hex `sha256`, an HTTPS `url`,
`format: "application/pdf"`, `route_granularity: "whole_file_only"`, and an
evidence object.  Enforce the summary totals (4 courses, 7 actions, 4,077
pages, 35,639,691 bytes) in the validator rather than trusting copied prose.

## File-level successor edits (do not apply in this draft)

* `scripts/build-modular-backend-snapshots-v2.mjs` (current constants and
  package assembly around lines 8–77, 93–124, 195–444, role/order assertions
  446–494): add candidate paths and stream-hash the large ZIP; construct the
  one package/four rows above; derive all counts; add CLP source/route evidence,
  family-06 bindings, and contribution features; set `snapshot.supersedes` to
  the actual current v0.62.16 authority (not the stale v0.62.14 predecessor).
  Do not load the 545 MB ZIP into the existing `sourceBytes` map.
* `scripts/validate-modular-backend-snapshots-v2.py` (hard-coded identities and
  counts around lines 12–22, 42–49, 138–206, 258–340): validate the staged
  candidate archive by streaming, assert package sharing/metrics/route counts,
  calculate the pending/public partitions, and update receipt prose from
  “nine roles/eight packages” to the derived values.  Keep v1 compatibility
  index checks separate.
* `backend/course-capsule-v1/authority/integration-overrides-v1.json` (current
  semantic adapter map around lines 320–526): add B20/B30/B50/B60 semantic
  adapter evidence only after sanitized manifest/validation receipts have been
  staged under the repo.  A candidate `outputs/` path must not leak into a
  public capsule.  Use `verified` only for evidence actually replayed; central
  package publication state is tracked in v2 independently.
* `scripts/build-course-capsules-v1.mjs` (effective-course merge 142–153,
  delivery 162–205, semantic adapter 287–291, manifest 387–444): consume the
  four semantic-adapter overrides and optionally add sidecar identity/counts to
  the manifest.  Keep course publication totals at 40/35/5.  Merge any B20/B50
  problem-book supplement correction by ID while preserving untouched
  supplements; the current shallow spread replaces the entire `supplements`
  array.  Regenerate after the change.
* `scripts/sync-course-capsules-v1.mjs` (mappings 9–31 and fallback renderer
  147–165): copy the sidecar and render its PDF actions before tools, offline,
  EPUB, repository, DOI, and release links.  Add identity/summary checks and
  include the sidecar in the public logical-file inventory.
* `docs/app.js` (imports 1–20 and `actionLinks` 150–181): consume the generated
  sidecar map and insert the seven CLP PDF actions immediately after the learner
  entry.  Use the sidecar URL/hash as the effective route source; do not let a
  mutable overlay silently win over a newer capsule/sidecar.
* `scripts/build-static-course-fallback.mjs` (imports 1–10, card 24–35): use
  the same effective catalog and sidecar.  The current script writes only
  `docs/index.html`; the offline `docs/peta-belajar-luring.html` is another
  generated surface and must be regenerated from the same data or explicitly
  checked for drift.
* `docs/live-course-publications.js`: create a successor overlay with explicit
  `snapshot_id`, `as_of`, and source hash.  Update B20/B50 historical record
  links and add B60 metadata if the overlay remains a runtime input.  Keep old
  overlay files as historical releases; never mutate an immutable release in
  place.  `materializeLiveCourses` currently shallow-spreads rows and only
  validates IDs (around lines 757–775), so add a generated drift check against
  the effective capsule/sidecar.
* `scripts/build-learner-read-model.mjs` / `validate-learner-read-model.mjs`:
  do not patch the immutable v0.62.0 read model.  Either generate a full
  successor read model from the authority or keep the CLP sidecar as a separate
  effective-publication projection with its own hash and validator.

## Stale-link and overlay traps

* Generated capsules already carry current B20/B30/B50/B60 primary PDFs, while
  `docs/live-course-publications.js` still contains B20 record 22164136 and B50
  record 22163372; the static `docs/index.html` fallback also contains those
  historical URLs.  A runtime that imports the overlay wins over the capsule.
* `native-package-references-v1.json` replaces backend/source ZIP components but
  does not replace the B20/B50 problem-book supplement entries.  Preserve old
  records as history if needed, but point effective learner/educator links at
  the route-evidence records and retain their hashes.
* The legacy v1 adapter index (five rows) is a compatibility artifact.  Do not
  silently add CLP there while updating v2; otherwise old validators and release
  lineage become ambiguous.
* Only A00, C30, and C40 currently declare
  `directly_consumes_adapter_outputs`; the four CLP rows are course-link-only.
  Counting all 13 bindings as runtime consumers would overstate integration.
* The candidate's original independent audit has a historical transient FAIL
  for `tools/__pycache__`; the superseding hygiene audit is the current PASS.
  A later `.v231-validator-*/record-index.sqlite3` outside the sealed inventory
  must be excluded from the ZIP and either removed by the candidate owner or
  documented as outside the handoff before accepting a broad cleanliness claim.

## Deterministic validation and publication sequence

1. Re-read live v0.62.16 authority/index and hash every staged candidate input.
2. Stream-validate ZIP size/hash/member inventory; replay build-A and the
   superseding hygiene receipt without loading the ZIP wholesale.
3. Generate the sidecar from route evidence; assert seven unique action IDs,
   four course IDs, exact page/byte/hash totals, PDF format, whole-file scope,
   and no anchor claims.
4. Build the successor v2 index and pattern/feature/comparison evidence; derive
   all summary counts and assert one shared CLP package for four bindings.
5. Build capsules and both learner fallbacks from the same effective catalog;
   run schema, peer-byte, stale-overlay, credential-scan, and no-machine-link
   checks.
6. Sync the sidecar and generated projections to `docs/`; run site/static/read
   model validators and compare all generated hashes.
7. Only after the user-authorized release transaction, publish one nonduplicate
   successor through the existing GitHub/Zenodo lineage.  Immediately perform
   anonymous readback of the site, adapter asset, route sidecar, and all seven
   PDF URLs; persist a sanitized receipt and then mark the package published.
