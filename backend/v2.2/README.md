# Modular mathematics backend v2.2

This directory implements the first strict v2.2 lane package: A00 / OpenStax
Prealgebra 2e in Indonesian.

The package is deliberately zero-copy. The 519,678 canonical owner-native
records stay in the owner backend. The v2.2 package binds all 17 native JSONL
views by exact path, byte count, SHA-256, ordered record-ID digest, and reverse
recipe. It materializes only strict identity, binding, order, rights, QA,
search, and learner-route records.

Canonical output:

`packages/a00-openstax-prealgebra-v0.1.0`

Build and independently validate:

```powershell
python -B scripts/build_a00_pilot.py --output packages/a00-openstax-prealgebra-v0.1.0 --replace
python -B scripts/validate_v22_package.py packages/a00-openstax-prealgebra-v0.1.0
```

The builder performs two independent clean materializations and requires every
pre-manifest byte to match. The validator then replays the owner-native shard
index and all projected native selectors, validates the strict schemas and
state vocabulary, verifies foreign keys, rights, source/target bindings,
zero-prose policy, route truthfulness, the package manifest, and the
non-circular seal.

No owner file is edited by either command.

## Global federation contract

The A00 package is a proof of strict zero-copy reversibility, not a mandate that
every corpus imitate its module graph. The machine-readable global contract is
`global-capability-contract-v0.1.0.json`, validated by
`schema/global-capability-contract-v0.1.schema.json`. It separates:

1. owner-native authority;
2. the lane authority capsule;
3. optional semantic capability shards;
4. the compact learner-navigation shard;
5. the zero-copy global registry; and
6. the generated student site.

Semantic granularity, translation granularity, and learner-navigation
granularity are explicitly distinct. Capability absence or non-projection must
be recorded rather than hidden. JSON and repository artifacts are secondary
machine surfaces; the student-facing site and readable editions remain the
primary learner entry points.

The first additional owner-native capability shard is
`owner-native-shards/o001-a00-assessments-v0.1.0`. It inventories 8,105
explicit exercises, 13,345 statement/solution components, and 2,865 exact
source solution gaps without copying prose or formula bodies. It remains a
separate sealed shard until an aggregate adapter resolves its stable module IDs
to the sealed A00 lane units and rights records.
