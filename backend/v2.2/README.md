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
