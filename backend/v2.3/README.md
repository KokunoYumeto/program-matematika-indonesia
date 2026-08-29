# Backend modular global v2.3

Backend v2.3 is an additive interoperability extension. It does not replace,
rewrite, or relax backend v2.2, the A00 owner-native backend, or any previously
published learner edition. The first extension is deliberately limited to the
A00 OpenStax Prealgebra lane. It restores deterministic CSV projections, makes
capability declarations conform to the ten-name global contract, binds the
otherwise distinct identity namespaces, and exposes only translation states
that already have owner evidence.

The student-facing HTML, PDF, and EPUB routes remain the primary entry points.
JSON, JSONL, and CSV are secondary machine surfaces. No file in this directory
is a learner destination and no centralized record may displace owner-native
prose, formulas, exercises, solutions, assets, rights, corrections, or build
authority.

## Authority and scope

The A00 extension binds, without mutating:

- base v2.2 package `urn:uuid:023b0035-f385-5188-920b-2130aa61f815`;
- dataset `urn:uuid:2afd6e58-418c-5b1b-b690-53f4ec9bffdf`;
- v2 federation course `urn:uuid:8d8ea368-373c-54d7-a6d3-4d9cfdaf46fe`;
- 75 owner-native module roots and their 75 v2.2 projected unit records;
- the frozen v2.1 A00 translation evidence, whose 75 states are all
  `mathematically_reviewed` and include exact source and target hashes; and
- the O001 assessment shard only as referenced assessment evidence, never as
  copied common records.

The extension declares `scope_kind = lane_extension`,
`aggregate_conformance_claim = false`, and exactly one admitted curriculum
role, `A00`. The other 39 curriculum roles remain unbound. This pilot therefore
must never be presented as global 40-role backend conformance.

The frozen curriculum-scope authority is federation v0.4.4
(`courses.jsonl`, 86,522 bytes, SHA-256
`7dee2faef2019e23fe4d3650ee772a23f9120979dae69409672fde3951101351`).
The O001 assessment package remains referenced, with 8,105 assessments,
5,240 explicit solutions, 2,865 declared solution gaps, and module-to-common-
unit resolution explicitly deferred. None of those records is silently
materialized into this extension.

## Three identity profiles

The three profiles are intentionally distinct and must not be collapsed:

| Profile | Namespace | UUIDv5 name formula |
| --- | --- | --- |
| `v1_central` | `7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd` | `record_type + '|' + stable_key` |
| `v2_federation` | `7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd` | `record_type + ':' + semantic_key` |
| `v2_2_lane` | `0e4d7b37-6108-5065-b08f-d1098697cc02` | `record_type + ':' + semantic_key` |

The shared namespace of v1 and v2 federation does not make their identifiers
interchangeable because their name formulas differ. The A00 legacy relationship
is explicitly many-to-one:

- v1 course `urn:uuid:191e7406-4239-506b-95d6-bb0fdec738cb`;
- v1 curriculum-role unit `urn:uuid:18f7091c-b314-5eab-b254-269c50ccca0c`;
- v2 federation course `urn:uuid:8d8ea368-373c-54d7-a6d3-4d9cfdaf46fe`.

No direct v1-to-v2.2-lane course mapping may be invented. The extension binds
the 75 existing owner-native-to-v2.2 unit crosswalks rather than minting or
duplicating owner identifiers.

## Contract files

The `schema/` directory contains six Draft 2020-12 schemas:

- `backend-v2.3-extension.schema.json` validates the extension manifest and its
  bindings, deterministic build, validation, learner-route, and seal policies;
- `capability-declarations-v0.1.schema.json` requires exactly the ten canonical
  capability names and preserves the three legacy labels only as declared
  composites or aliases;
- `namespace-crosswalk-v0.1.schema.json` binds all 75 existing unit mappings and
  the exact two-to-one legacy course relationship while prohibiting a fabricated
  lane-local course bridge;
- `csv-projection-manifest-v0.1.schema.json` binds 19 per-table CSV files plus
  `records.csv`, all with the exact header
  `stable_id,record_type,canonical_record_json`;
- `translation-state-index-v0.1.schema.json` admits exactly the 75 evidenced
  module-root states and forbids segment-level inference; and
- `scope-declaration-v0.1.schema.json` makes the A00-only, zero-copy,
  non-aggregate boundary machine-verifiable.

An implementation package is expected under
`extensions/a00-openstax-prealgebra-v0.1.0/`. It must contain a manifest, the
five typed sidecars, deterministic CSV projections, validation evidence, and a
non-circular seal. Schema and tool copies used for a sealed build must be bound
by exact byte count and SHA-256.

## Capability truth

Every extension contains exactly these ten declarations:

1. `structure_localization` — referenced owner-native structure, with the 75
   learner-navigation roots materialized;
2. `terminology` — referenced owner-native terminology;
3. `mathematical_preservation` — referenced owner-native evidence;
4. `assessment_support` — referenced O001 assessment shard, not materialized in
   the common extension;
5. `assets` — referenced owner-native assets and rights;
6. `accessibility` — absent as a typed owner-native capability; weaker semantic
   HTML evidence is recorded separately and may not upgrade the state;
7. `corrections` — referenced owner-native corrections;
8. `computational_interactives` — absent;
9. `publication` — materialized publication and learner-route metadata; and
10. `research_support` — absent.

`semantic_native` and `learner_navigation` remain legacy composite labels only.
`assessments` is an explicit alias of `assessment_support`. They are not extra
canonical capabilities.

## Deterministic projections

The v2.2 JSONL table order is authoritative. Each of the 19 source tables is
projected in source-row order to `csv/<table>.csv`; `records.csv` concatenates
tables in manifest order. Every CSV has the exact three-column header above.
`canonical_record_json` is the exact canonical single-line JSON record, not a
lossy field selection. UTF-8, LF, RFC 4180 quoting, and a final LF are required.
CSV-to-JSONL reconstruction must reproduce every source line, and a clean
rebuild must reproduce every CSV byte.

Translation-state projection is module-root only. It matches each v2.1 A00 row
to the v2.2 unit and source/target content bindings using stable module and unit
identities. It does not infer states for segments, expressions, terms, or other
owner-native records.

## Validation and release boundary

A valid extension proves authority hashes, all six schemas, the exact ten-name
capability set, UUID recomputation under the correct profile, crosswalk
cardinality and reverse closure, 20 CSV round trips, 75 evidenced translation
states, unchanged v2.2 bytes, inherited formula/rights/asset/route closure, two
byte-identical clean builds, and a non-circular seal. Public release additionally
requires anonymous byte readback. A local build may record public readback as
`not_run`; it may not claim a public state from that value.

The admitted A00 package at
`extensions/a00-openstax-prealgebra-v0.1.0/` contains 36 files. Its mandatory
validator rebuilds the package twice in fresh directories, compares every
clean-build byte, then compares the canonical package while excluding only the
seal-excluded `validation-report.json`. The current clean-build identity is
`3e76736676d1f10f5a2b2a8dc76ea0a7b8d5586890a34339493f90002125ab0e`;
the 35-file sealed/payload identity is
`8ec7ef0f31b73e8cfd93b243ad691410e03532951bdff4663c0287740fae9b52`.

Backend v2.3 remains additive until other lanes independently emit equivalent
owner-bound extensions. Aggregate conformance requires explicit admission of
every intended lane and is outside this A00 pilot.
