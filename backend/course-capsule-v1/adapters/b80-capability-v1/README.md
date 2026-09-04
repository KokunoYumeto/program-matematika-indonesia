# B80 native learning capability adapter

This adapter adopts Mathematical Computing's existing learning design instead
of replacing its Quarto source or executable laboratories. It preserves all
326 native catalog records: 14 units, 75 exercises, four laboratories, four
prerequisite routes, component rights, artifact identities, environments,
relations, and historical metadata. The catalog is a metadata/learning graph,
not a copy of the course reader.

## What people can use

- `docs/backend/b80/B80.html`: searchable exercises, unit navigation, and links
  to native hints, checks, and solutions.
- `docs/backend/b80/B80-pengajar.html`: unit order, source learning objectives,
  the same exercise identities, laboratory requirements and prerequisite paths.
- `docs/backend/b80/learning-map.json`: the structured data used by both views.

The three prerequisite-dependent exercises are enrichment, not required B80
completion. Native Python/SageMath execution is not moved into the browser.
The page is portable navigation, not an offline copy of the linked lessons.
English translation is not included or implied.

## Rebuild and validation

From the central checkout, run `npm run build:b80-capability`. This runs the
adapter builder, independent native-schema/HTML/identity validation, two clean
isolated builds, mutation tests, and the all-40 course-capsule checks. Validation
creates `validation.json`; the builder alone is not a release command.

Normal builds require only the frozen `input/` files and published scripts, not
the native producer directory. The separate intake script is used only when
intentionally refreshing that frozen input. It anonymously verifies the public
catalog and every declared section/exercise anchor on all fourteen unit pages.
The receipt records page byte counts and hashes without copying the reader.

## Exchange and scope

`exchange/shape.json` and `exchange/records.jsonl` preserve native table names,
array order, IDs, scalar values (including signed zero), null/absence distinctions,
and payloads. The inverse is independently checked after serialization. No
native type is relabeled as a generic curriculum unit merely to inflate counts.

Contract: `course-learning-capability/1`, using `native-catalog-exchange/1`.
This is not an assertion of contract-2.3.1 conformance. Scientific experiment
receipts remain native evidence; the adapter does not claim to rerun them.
Public release verification is recorded separately from local validation.

Text metadata retains CC BY-SA 4.0 and code retains MIT as declared in the
native catalog. Component source roles and their distinct rights remain intact.
