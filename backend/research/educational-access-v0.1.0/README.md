# Educational-access research federation

This additive package lets the modular curriculum backend serve the existing
educational-access and marginal-intelligibility research without pretending
that research records are mathematics course units. It contains 490 typed,
stable records across ten materialized tables, with lossless JSONL and CSV
projections, exact source facts, foreign-key checks, and a public compact JSON
projection at `docs/data/educational-access.json`.

Seven future tables are deliberately declared but not emitted: population
cells, curriculum-unit mappings, compute observations, cost scenarios, ranking
runs, ranking items, and impact snapshots. Their absence means “active research
not yet materialized,” never zero evidence or a fabricated result.

The package is a frozen release snapshot. The validator always verifies its
schema, manifest, hashes, UUIDv5 identities, projections, foreign keys, public
catalog, and portable public asset locators. It also reports whether the current
mutable workspace still matches the captured source facts. Use
`--require-live-source-replay` immediately after rebuilding when that stronger
current-workspace equality is required; a later source change does not
retroactively invalidate an already frozen package.

```powershell
python -B scripts/build-educational-access-federation-v1.py
python -B scripts/validate-educational-access-federation-v1.py --require-live-source-replay
```
