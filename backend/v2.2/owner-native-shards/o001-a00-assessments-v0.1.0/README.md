# O001 / A00 owner-native assessment inventory

This deterministic shard inventories the explicit CNXML `exercise`, `problem`,
and `solution` nodes in the frozen OpenStax Prealgebra 2e English source and its
Bahasa Indonesia target. It contains **no mathematical prose, formula bodies,
titles, answers, or solution text**. It records only stable IDs, module/order,
explicit tag/class context, exact byte spans, subtree sizes and SHA-256 hashes,
source/target presence, topology, and solution-availability gaps.

The English source bytes are replayed only with the exact narrow command
`git show 38cae454e644abf9f0a623e876994553881597c9:modules/<module>/index.cnxml`.
Both source and target document bytes must match the two frozen owner witness
manifests before any record is emitted. The owner repository is read-only.

## Files

- `data/assessments.jsonl`: one stable assessment row per explicit exercise.
- `data/assessment-components.jsonl`: problem nodes projected as `statement`
  components and solution nodes projected as `solution` components.
- `data/solution-gaps.jsonl`: exact exercises for which neither source nor
  target contains an explicit solution node.
- `summaries/modules.jsonl`: exact source/target document bindings, structural
  counts, and context counts for each of the 75 modules.
- `manifest.json`: authority, counts, projection contract, and file inventory.
- `CHECKSUMS.sha256` and `seal.json`: a non-circular package seal. The checksum
  file binds every content file including the manifest, but excludes itself and
  the seal. The seal binds the checksum file and excludes itself.

## Projection into common backend v2.2

This is an owner-native O001 infrastructure shard, not a mutation of the sealed
`a00-openstax-prealgebra-v0.1.0` package. A later aggregate adapter resolves each
`module` to that package's existing navigation `unit_id`, then projects:

- each `assessment` row to the optional v2.2 `assessments` capability;
- each `problem` row to `assessment_components.component_kind=statement`;
- each `solution` row to `assessment_components.component_kind=solution`;
- source/target byte-span hashes to content/native bindings;
- the explicit missing-solution rows to capability-loss/gap reporting.

The stable UUIDv5 IDs may be retained. Rights IDs, learner routes, and unit IDs
must be resolved from the sealed A00 lane package at integration time rather
than guessed here. No assessment content is promoted to a learner-navigation
unit, and no missing solution is invented.

## Replay

From this package directory:

```powershell
python -B tools/build_o001_a00_assessments.py --owner-root <openstax-prealgebra> --output <build-dir>
python -B tools/validate_o001_a00_assessments.py --owner-root <openstax-prealgebra> --package-root <build-dir>
```

Two builds from the same frozen inputs must be byte-identical for every file.
