# O018/C130 complete-corpus adapter to common backend v1

This directory is an isolated, zero-copy migration for the frozen complete
R017/O018 Book 1 Indonesian corpus owned by
`04_mirrors/id/open-optimization-or-book-id`. The owner lane is read-only.

The adapter creates exactly one direct common-v1 record for every one of the
17,987 native records. Each direct record embeds the complete canonical native
record, its table/line locator, and its SHA-256 in the namespaced
`interlanguage.o018-c130-r017-book1-native` extension. Exact reverse extraction
must reconstruct every native table in its original order. It also emits 7,818
additive common `segment_variant` projections for every source or target text
payload physically present in the native combined-segment model. Those
projections are not counted as native records.

No redundant common-backend copy is stored. The script validates the exact
native backend, schema, JSONL tables, manifest, checksums, completion cursor,
and publication receipts; assembles and validates the strict common backend
twice; requires byte-identical replay; then writes only the compact receipt.

From the central repository root:

```powershell
python -B backend/migrations/o018-c130-id-v1/migrate_o018_c130_v1.py `
  --corpus-root C:\corpora\open-optimization-or-book-id `
  --schema schemas/backend-v1.schema.json `
  --receipt-schema schemas/backend-migration-receipt-v1.schema.json `
  --output-receipt backend/migrations/o018-c130-id-v1/MIGRATION_RECEIPT.json

python -B backend/migrations/o018-c130-id-v1/test_migration.py `
  --corpus-root C:\corpora\open-optimization-or-book-id
```

The common-v1 term contract requires one `scope_unit_id`, while the native
glossary explicitly scopes terms across the combined R017/O018 corpus. The
adapter uses the R017 Book 1 root as the common corpus-root sentinel and retains
the exact native scope string losslessly in every term extension. Native
unordered relations similarly use common ordinal `0` as an explicit sentinel.
