# Judson C30/C40 v2.3.1 adapter candidate

This is a local, not-admitted candidate. It neither changes an existing public
release nor claims public adapter admission, learner consumption, full native
backend replay, fresh public-byte verification, unit anchors, accessibility
conformance, or Sage/Lean execution. Generic package validation and native
semantic/replay audits are separate operations. No network is used by the builder.

## Frozen public inputs

Download the public [SOURCE_BACKEND.zip](https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_SOURCE_BACKEND.zip?download=1)
as `SOURCE_BACKEND.zip`. Required byte count: **69,370,499**. Required SHA-256:

`0aa85116679703b632333f4003b3373f42bb7b282c3719bea3731257c0fe55e0`

The builder rejects any other archive bytes. It reads native rows directly from
that archive, not a mutable source checkout or owner control directory. Its native
`backend/v1/manifest.json` must be 5,669 bytes with SHA-256:

`4294d16f96ea7fa405d6841e308e7c90c08152a2c7eb6cefe45a44e5b705bcd1`

The included `frozen-central` files are exact copies of the central capability
contract and released v0.62.13 course capsules, not successor metadata:

- `backend/v2.2/global-capability-contract-v0.1.0.json`: 7,462 bytes,
  `f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7`.
- `releases/v0.62.13/course-capsules-v1.jsonl`: 226,934 bytes,
  `2c885781e9b69de6afdc2cbfe8e7d95d26ba97f0ffe571a12b4ec1ead575d6d1`.

The capsules originated in the public
[central v0.62.13 release](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.13).
The two generic tools and six schemas are copied byte-for-byte, with their expected
identities pinned in the builder. They are never patched or weakened. A third,
separate read-only chapter-route replayer is also copied exactly.

The supplemental `frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json` is 47,314
bytes, SHA-256 `3f22e70fff457fc96dc44c2cb4930ae25a0ab401fb6ad0a3387ed8d98e2d84c4`.
It is candidate evidence, not an artifact asserted to be in a prior public release.
The builder hash-checks it and checks every route against native chapter membership,
course, unit, source path and sequence. Its deterministic offline object hash is
`cd5e0dd51e5889c007bc28cf5afb19a70dfa496816d49f17fcb072faa64a88a4`.

## Offline reproducible build

Use Python 3 with `jsonschema` installed. Run these commands from this candidate
root (or from either generated package root); all paths are portable examples:

Generated records use the frozen deterministic build-snapshot stamp
`2026-08-31T13:32:05Z`, sampled before these final builds. This is not an individual
live-probe time. The builder rejects a snapshot stamp earlier than the bound route
document's creation time; the original dated live observations remain unchanged.

```text
python -B tools/build_judson_candidate.py --source-zip SOURCE_BACKEND.zip --output build-a
python -B tools/build_judson_candidate.py --source-zip SOURCE_BACKEND.zip --output build-b
python -B tools/validate_lane_adapter_v231.py --package build-a --build-a build-a --build-b build-b --report generic-package-validation.json
```

Outputs must be new directories: the builder never overwrites an existing build.
The final validator command checks both full package trees, schema/CSV round trips,
crosswalk targets, seals and privacy patterns. Without authority-root arguments,
it does **not** recheck external authority bytes; inspect its `authorities` counts.

For authority-byte validation, safely extract the exact public ZIP into a fresh
`native-authority` directory and use the unchanged generic validator:

```text
python -B -m zipfile -e SOURCE_BACKEND.zip native-authority
python -B tools/validate_lane_adapter_v231.py --package build-a --repository-root frozen-central --owner-package-root native-authority --require-authorities --build-a build-a --build-b build-b --report generic-authority-validation.json
```

`native-authority/backend/v1/manifest.json` must exist. The generic validator
rechecks every external fact declared by the candidate: the native manifest, all
37 files bound by that manifest, and the two frozen central files. Its field
`locally_replayed` means fact-byte/hash validation, **not execution of the native
backend builder, Sage or reader builds**. This candidate has no private workspace
dependency. Keep reports outside sealed package directories.

The chapter witness can be independently replayed offline with the copied route
replayer, the exact [public WEB.zip](https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_WEB.zip?download=1)
(27,339,920 bytes; SHA-256 `cb27ec5671b7e2378da0754a607125b43367ba6eca473d3dc11afd307313a7c1`)
and [RELEASE_MANIFEST.json](https://zenodo.org/records/22062449/files/RELEASE_MANIFEST.json?download=1)
(2,445 bytes; SHA-256 `19edcfb1223be1a5b416598e0a3224bb99df91dbff8929ea853cb8b31e3365ee`):

```text
python -B tools/replay_judson_two_course_learner_routes.py --web-zip WEB.zip --native-backend native-authority/backend/v1 --release-manifest RELEASE_MANIFEST.json --check frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json
```

This optional independent witness replay verifies all 23 real chapter HTML members,
titles, TOC links, chapter IDs and hashes (1,830,695 HTML bytes) without repeating
historical HTTP observations. The main candidate builder consumes the already
frozen witness, not a mutable live website or newly downloaded WEB archive.

## Exact scope and evidence

- One canonical table of all 3,323 native units; separate native IDs remain
  unchanged and UUIDv5 projection IDs are linked by explicit crosswalks.
- All 6,505 typed native relations, including non-unit endpoints. The endpoint
  index binds the native namespace, record type, ZIP member and exact JSONL row.
- The exact two native course selectors and 23 native chapter memberships.
  `course-views.json` follows native parent topology without duplicating unit
  records: C30 has 2,014 units; C40 has 1,279; 30 remain outside both selectors.
- All 3,323 birth/current mappings, including aliases, matching state, selectors,
  native IDs and source hashes. Selector changes do not mint a replacement native
  identity, and translated titles/prose never participate in ID generation.
- All 4,466 exact source/translation segment pairs: 4,150 `translated` and 316
  `source_frozen`. Pair bindings preserve the exact source/translation record IDs,
  source hashes, raw target hashes, locale and reason. The 316 native null target
  hashes stay null. Separate preservation hashes cite explicit segment dispositions
  or the exact source-preserved-path policy; they are not invented translation
  target fields or independent target-byte replay results.
- Unit translation states aggregate only directly attached native pairs, preserving
  the state set and `mixed` / `no-segment-evidence`. Unit `status=active` and
  `xml_lang` are not treated as translation completion. Three edition-authored
  Indonesian segments are separately referenced, not fabricated translation pairs.
- Exactly 81 source-frozen segments are operative English GFDL text. Other frozen
  segments include bibliography titles, names, Sage labels and answer-label-only
  material; the candidate never labels all 316 as legal text.
- Modified edition `GFDL-1.3-or-later`, upstream `GFDL-1.2-or-later`, and the
  operative English GFDL 1.3 preservation policy remain distinct. Complete native
  legal notices and richer metadata remain referenced in their original shards.

Native evidence objects specify a ZIP `member`, a one-based `jsonl_row_ordinal`,
`json_pointer` within that row (the empty string denotes the row root), unchanged `native_id`, exact line byte count and
SHA-256 (including the original line ending). Member byte/hash facts are bound by
the native manifest. `tables/identity_crosswalks.jsonl` preserves birth/current
selectors; `namespace-crosswalk-v0.2.0.json` supplies explicit namespace mappings.
No textbook prose, formula XML fragments or executable Sage code is centralized.

Structure/localization metadata is materialized. Terminology, richer mathematical
preservation, assessment, assets, corrections, computation, publication and
historical QA are explicitly native-shard references. Accessibility is not
projected. Capability native counts count the full specified shard rows, not a
fabricated exercise/completeness count. No `structured_exercise_closure` label is
claimed. A missing central capability is not a defect assertion about the native
course.

Candidate learner routes include the two whole-course fallbacks from the frozen
capsules and 23 chapter URLs linked to exact native/projected chapter IDs, native
sequence, Indonesian titles and frozen WEB archive members. C30 has 15 chapter
routes; C40 has 8. Course views reference the same route and unit IDs.

The frozen route evidence records 23 anonymous HTTP 200 responses on 2026-08-31,
but **0 of 23 matched the frozen chapter bytes**. Offline edition identity and dated
live reachability therefore remain separate. Live URLs remain usable with an
explicit version warning; no current live edition identity, semantic equivalence,
descendant-unit anchor, or direct runtime learner-consumption claim follows.
This candidate performed no network check. The two capsule fallbacks retain their
original `available_unverified` state. Nothing here restricts or modifies public
access or asserts a defect in the owner course.

`BUILD_SUMMARY.json` records recomputed counts. Package seals bind only the
generated projection and its exact frozen metadata/tools. Separate root-owned
native replay receipts, where present outside these packages, are not rewritten,
incorporated, or silently promoted to candidate capability claims.
