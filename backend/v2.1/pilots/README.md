# Global backend v2.1 unit/search pilots

These four packages are additive, read-only projections of admitted
owner-native backends. They do not replace those backends or the v1/v2
federation. They prove a compact learner-navigation and search layer while
retaining the strongest native identity model of each edition.

Every package contains canonical JSONL for stable units, relations, and search;
a component-rights/accessibility summary; an exact manifest; and an
independently rerunnable validation report. The records contain bounded titles,
locators, hashes, and relations—not textbook prose.

| Course | Native strength retained | Units | Relations | Learner route boundary |
|---|---|---:|---:|---|
| A00 OpenStax Prealgebra | CNXML module identity, locale-neutral module/translation split, exact module order | 75 | 201 | 75 verified per-module pages |
| B10 Discrete Mathematics | Deep PreTeXt book/chapter/section/subsection graph and prerequisite evidence | 161 | 284 | published course root until clean per-unit routes exist |
| C100 Geometry | 154 structural units, 253 parent exercises, all 32 subparts, 247 unique hints, 253 independent solutions, exact HTML/PDF routes, source/target/solution bindings | 939 | 994 | byte-exact central semantic reader, 331-page solution PDF, and 20 chapter wrappers; public readback is a release gate |
| D20 Functional Analysis | Formula-, asset-, semantic-unit-, and route-rich owner backend projected to 19 learner roots | 19 | 686 | 17 proven owner chapter routes plus central wrappers |

C100 preserves all six owner-native component-rights records. Its CC BY-SA
main-course reader and independently authored CC BY-SA solution PDF are copied
exactly, while the separately licensed
Clemens/Snapp workbook and every excluded or unresolved component remain absent.
`route_materialization.json` is explicitly local-only; it is not public
readback evidence. D20's `route_gap_report.json` records actual public
observations, including the rejected short-route pattern.

An owner-adjacent checkout rebuilds C100 from exact primary bytes. The
standalone central source release does not duplicate that multi-repository
corpus; it instead validates the committed compact package and its complete
declared authority hashes. This distinction is explicit in the C100 manifest.

The common rule is therefore not “force every book into one flat schema.” It is:

1. keep the owner-native backend canonical;
2. assign stable identities at the edition's strongest safe granularity;
3. export a zero-prose compact projection for order, search, relations, routes,
   rights, provenance, accessibility, and exact source/target hashes;
4. declare whether relation endpoints are internal or an exact hash-bound
   external set;
5. present readable HTML as the learner surface and keep JSON as the secondary
   machine surface; and
6. require deterministic replay and anonymous public-byte readback before a
   materialized route becomes a published-route claim.

The strict `backend/v2.1/schema/federation-unit-*.schema.json` files describe a
different UUID-envelope contract. These four exploratory packages use the
separately identified
`interlanguage/global-backend-v2.1-unit-search-pilot/0.1.0` contract and are
validated by `validate_pilots.py`; release metadata must not claim otherwise.

Rebuild and validate from the program repository root:

```powershell
python -B backend/v2.1/pilots/build_all_pilots.py
python -B backend/v2.1/pilots/validate_pilots.py
node scripts/build-v21-learner-routes.mjs
node scripts/validate-v21-learner-routes.mjs
```

The additive educational-access planning layer is documented separately at
`backend/v2.1/planning/educational-access/README.md`.
