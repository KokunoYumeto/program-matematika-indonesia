#!/usr/bin/env python3
"""Validate generic and C130-specific invariants of the operations-research adapter.

The C130 package is intentionally zero-copy.  This validator therefore replays
the exact owner-native backend from ``--owner-package-root`` while separately
inspecting every package table and sidecar.  A package cannot pass from counts,
schemas, or a prior generic-validation receipt alone.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    TABLE_ORDER,
    AdapterError,
    compact_json,
    identity_set_sha256,
    mapping_set_sha256,
    projection_id,
    read_json,
    read_jsonl,
    require,
    sha256_bytes,
    sha256_file,
    write_json,
)
from validate_lane_adapter_v231 import validate_package


RECORDED_AT = "2026-08-31T00:00:00Z"
ROLE_ID = "C130"
PREVIOUS_COMMON_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
PRIOR_V1_MAPPING_BYTES = 2_231_498
PRIOR_V1_MAPPING_SHA256 = "7eab936794df7157467b646f97519889a1c6fdeb6b4222e1ecb1d1df9a8ee51a"
PRIOR_V1_DIRECT_TYPES = {
    "artifacts": "artifact", "assets": "asset", "concepts": "concept",
    "corrections": "correction", "courses": "course", "editions": "edition",
    "programs": "program", "qa_events": "qa_event", "relations": "relation",
    "resources": "resource", "rights": "rights", "segments": "segment",
    "terms": "term", "units": "unit",
}
ALL_CURRICULUM_ROLES = {
    "A00", "A10", "A20", "A30",
    "B10", "B20", "B30", "B40", "B50", "B60", "B70", "B80", "B90", "B95",
    "C10", "C20", "C30", "C40", "C50", "C60", "C70", "C80", "C90", "C100", "C110", "C120", "C130", "C140",
    "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D90", "D100", "D110", "D120",
}

OWNER_COUNTS = {
    "artifacts": 83,
    "assets": 346,
    "concepts": 128,
    "corrections": 94,
    "courses": 1,
    "editions": 5,
    "programs": 1,
    "qa_events": 101,
    "relations": 9545,
    "resources": 4,
    "rights": 21,
    "segments": 5525,
    "terms": 140,
    "units": 1993,
}

EXPECTED_TABLE_COUNTS = {
    "owner_authorities": 1,
    "datasets": 1,
    "editions": 5,
    "units": 1993,
    "course_unit_memberships": 1993,
    "native_bindings": 5525,
    "content_bindings": 5525,
    "relations": 9545,
    "rights": 21,
    "rights_assignments": 7634,
    "artifacts": 83,
    "build_recipes": 0,
    "reader_surfaces": 1,
    "routes": 7,
    "search_documents": 1993,
    "adapter_profiles": 1,
    "adapter_runs": 1,
    "qa_events": 102,
    "identity_crosswalks": 17273,
}

EXPECTED_RELATION_TYPES = {
    "adapts": 175,
    "answers": 13,
    "contains": 2006,
    "corrects": 119,
    "depends-on": 360,
    "evidenced-by": 117,
    "exercises": 550,
    "generated-as": 2,
    "generated-by": 13,
    "illustrates": 3701,
    "implemented-by": 126,
    "precedes": 1783,
    "prerequisite": 160,
    "realized-by": 10,
    "reproduces": 1,
    "solves": 388,
    "supersedes": 2,
    "translates": 1,
    "verifies": 18,
}

EXPECTED_UNIT_TRANSLATION_STATES = {
    "built": 2,
    "language_reviewed": 1,
    "mathematically_reviewed": 104,
    "source_frozen": 225,
    "structurally_verified": 897,
    "translated": 763,
    "visually_checked": 1,
}

EXPECTED_SEGMENT_TRANSLATION_STATES = {
    "source_frozen": 339,
    "structurally_verified": 2893,
    "translated": 2293,
}

EXPECTED_SEGMENT_RELATIONSHIPS = {
    "locally_authored_adaptation": 339,
    "target_native_correction": 9,
    "translation": 2293,
    "translation_target_projection": 2884,
}

EXPECTED_CAPABILITY_STATES = {
    "structure_localization": "materialized",
    "terminology": "referenced_native_shards",
    "mathematical_preservation": "referenced_native_shards",
    "assessment_support": "referenced_native_shards",
    "assets": "referenced_native_shards",
    "accessibility": "referenced_native_shards",
    "corrections": "referenced_native_shards",
    "computational_interactives": "referenced_native_shards",
    "publication": "materialized",
    "research_support": "referenced_native_shards",
}

OWNER_AUTHORITY_FACTS = {
    "backend/dist/backend-v0.json": (26022240, "7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804"),
    "backend/dist/manifest.json": (4853, "f800590f07fafa47c7eb900dddc8cf99bbf5cb892218fa4ab1722677b7b2efa4"),
    "backend/dist/SHA256SUMS.txt": (2623, "1dabfdb58c910fc5c1e659356361c51056c6084a214f7b20583a42e9750e6515"),
    "00_control/CURRENT_CURSOR.json": (5676, "a79969903d29a26872c78d1dd573aabdeefff9c08720e7a99dc5b7d8f0499f1c"),
    "qa/release-package-report.json": (5130, "ae2e905782c099db7d1c177255fbbc6f07146caa2c3cacf2293498cdac3b308f"),
    "release/out/RELEASE-MANIFEST.json": (4773, "c0bfe88be28ce19bd730e69fd3bc0ed88b73f076e3d7a1b61b205cbb4a96f376"),
    "release/out/SHA256SUMS.txt": (1200, "d582ad7eca87ca91687c7f278b7ee7ac1603cc724bf8c4b95bb53bd93262e32d"),
    "release/receipts/zenodo-publication-receipt-2026.08.23-id.5.json": (
        5197,
        "3e20d2459f42824e57df29bd0937e2f526d9349da7d941c65cf7dcec3739feab",
    ),
    "release/receipts/github-publication-receipt.json": (
        239332,
        "b888b35ab940f1418b4c74c1da06548bb4fedf8e5079240368608eec605cccf8",
    ),
    "qa/github-publication-plan.json": (158378, "288013dc2c0565d4eac070834e5462efc5b5c2747604d83fef4f6f3bb56e617a"),
}

LIMITATIONS_AUTHORITY_PATH = (
    "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/"
    "backend_adapters/c130_operations_research_v231_candidate/research/"
    "C130_NATIVE_PIPELINE_LIMITATIONS_20260831.md"
)
LIMITATIONS_AUTHORITY_FACT = (
    3720,
    "e73edc9413411b1594a07f646cc11011853d9548a87a28f7b1985aa8f74b99c0",
)

PROGRAM_AUTHORITY_FACTS = {
    "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/198_FULL_LIVE_OWNER_REGISTRY_AUTHORITY_CORRECTION_20260831.json": (
        32625,
        "69b853222d77ecd0873e832a00c74bffaa8cc11d5f6c1490138135a7f89e7fee",
    ),
    "04_mirrors/id/program-matematika-indonesia-v06213/backend/v2.2/global-capability-contract-v0.1.0.json": (
        7462,
        "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7",
    ),
    LIMITATIONS_AUTHORITY_PATH: LIMITATIONS_AUTHORITY_FACT,
    "04_mirrors/id/program-matematika-indonesia-v06213/releases/v0.62.13/o018-c130-id-backend-v1-migration-receipt.json": (
        22647,
        "cd591df3833862551d5bbcdcfa6a1c6f22414504110b1e9fae38162dedc1ca5f",
    ),
}

STALE_RELEASE_REPORT_SHA256 = "a17c5eef4c721bb49de834a33bf0c3561b0dc3393957155692e2ffccc6509ec4"
CURRENT_RELEASE_REPORT_SHA256 = "ae2e905782c099db7d1c177255fbbc6f07146caa2c3cacf2293498cdac3b308f"

REPOSITORY_URL = "https://github.com/KokunoYumeto/open-optimization-or-book-id"
PAGES_URL = "https://kokunoyumeto.github.io/open-optimization-or-book-id/"
ZENODO_URL = "https://zenodo.org/records/22070653"

PUBLIC_DOWNLOADS = {
    "pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf": {
        "bytes": 26425739,
        "sha256": "daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49",
        "url": PAGES_URL + "downloads/pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf",
        "route_token": "pdf",
    },
    "pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip": {
        "bytes": 20087323,
        "sha256": "55d62c53401938eb5dbc12d3f4116ce68181bd90c9f94fda1434fe20f5196914",
        "url": PAGES_URL + "downloads/pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip",
        "route_token": "source",
    },
    "pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip": {
        "bytes": 527596,
        "sha256": "99628dcdd4984c8a3b763862dc88b06bca8bf15d47dbf1db863cfe46b2a1e592",
        "url": PAGES_URL + "downloads/pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip",
        "route_token": "lab",
    },
    "pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip": {
        "bytes": 6535806,
        "sha256": "7cd76333b3433518f4d983d6775412aba9fd99e1f6b9a35a89528e6994830c56",
        "url": PAGES_URL + "downloads/pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip",
        "route_token": "backend",
    },
}

EXPECTED_ROUTE_URLS = {
    REPOSITORY_URL,
    PAGES_URL,
    ZENODO_URL,
    *(fact["url"] for fact in PUBLIC_DOWNLOADS.values()),
}

OWNER_ENVELOPE_KEYS = {
    "id",
    "recorded_at",
    "responsible_workflow",
    "schema_name",
    "schema_version",
    "status",
    "supersedes_id",
}
PROSE_FIELDS = {
    "body",
    "formula",
    "fragment_xml",
    "full_text",
    "html",
    "proof",
    "prose",
    "source_text",
    "target_text",
    "text",
}

DIRECT_MAPPING_SPECS = {
    "edition": ("editions", "edition"),
    "unit": ("units", "unit"),
    "segment": ("segments", "native_binding"),
    "relation": ("relations", "relation"),
    "right": ("rights", "rights"),
    "artifact": ("artifacts", "artifact"),
    "qa_event": ("qa_events", "qa_event"),
}


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def _contains_exact_mapping(value: Any, expected: Mapping[str, Any]) -> bool:
    return any(all(candidate.get(key) == item for key, item in expected.items()) for candidate in _walk_mappings(value))


def _string_blob(value: Any) -> str:
    return compact_json(value).lower()


def _fact_at(root: Path, relative: str) -> dict[str, Any]:
    pure = PurePosixPath(relative)
    require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe authority path: {relative}")
    path = root.joinpath(*pure.parts)
    require(path.is_file(), f"missing authority: {relative}")
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _require_fact(root: Path, relative: str, expected: tuple[int, str]) -> dict[str, Any]:
    fact = _fact_at(root, relative)
    require((fact["bytes"], fact["sha256"]) == expected, f"authority fact drift: {relative}")
    return fact


def _parse_checksum_rows(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for ordinal, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        require(len(line) > 66 and line[64:66] == "  ", f"malformed owner checksum row {ordinal}: {path}")
        digest, relative = line[:64], line[66:]
        require(len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest), f"bad owner checksum digest: {path}:{ordinal}")
        pure = PurePosixPath(relative)
        require(not pure.is_absolute() and ".." not in pure.parts and "\\" not in relative, f"unsafe checksum path: {relative}")
        rows.append((digest, relative))
    require(len(rows) == len({relative for _, relative in rows}), f"duplicate checksum path: {path}")
    return rows


def _owner_record_sha256(row: Mapping[str, Any]) -> str:
    return sha256_bytes(compact_json(row).encode("utf-8"))


def _prior_v1_identity_facts(backend: Mapping[str, Any]) -> dict[str, Any]:
    native_table_by_id: dict[str, str] = {}
    prior_id_by_native_id: dict[str, str] = {}
    for collection in sorted(PRIOR_V1_DIRECT_TYPES):
        for row in backend[collection]:
            native_id = str(row["id"])
            require(native_id not in native_table_by_id, f"duplicate owner-native ID across collections: {native_id}")
            native_table_by_id[native_id] = collection
            record_type = PRIOR_V1_DIRECT_TYPES[collection]
            prior_id_by_native_id[native_id] = "urn:uuid:" + str(
                uuid.uuid5(PREVIOUS_COMMON_NAMESPACE, f"{record_type}|o018-c130:native:{native_id}")
            )
    require(len(prior_id_by_native_id) == 17_987, "prior-v1 native identity cardinality drift")
    mapping_payload = b"".join(
        f"{native_table_by_id[native_id]}\t{native_id}\t{prior_id_by_native_id[native_id]}\n".encode("utf-8")
        for native_id in sorted(prior_id_by_native_id)
    )
    require((len(mapping_payload), sha256_bytes(mapping_payload)) == (PRIOR_V1_MAPPING_BYTES, PRIOR_V1_MAPPING_SHA256), "prior-v1 mapping receipt replay drift")
    return {
        "native_table_by_id": native_table_by_id,
        "prior_id_by_native_id": prior_id_by_native_id,
        "all_prior_ids_sha256": identity_set_sha256(prior_id_by_native_id.values()),
        "native_to_prior_pairs_sha256": mapping_set_sha256(prior_id_by_native_id.items()),
    }


def _native_rights_references(collection: str, row: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    singular = row.get("rights_component_id")
    plural = list(row.get("rights_component_ids") or [])
    require(not (singular and plural), f"mixed singular/plural rights fields: {collection}:{row['id']}")
    if singular:
        refs.append({"source_field": "rights_component_id", "source_ordinal": 0, "assignment_role": "primary", "native_rights_id": str(singular)})
    for ordinal, right_id in enumerate(row.get("additional_rights_component_ids") or []):
        refs.append({"source_field": "additional_rights_component_ids", "source_ordinal": ordinal, "assignment_role": "additional", "native_rights_id": str(right_id)})
    for ordinal, right_id in enumerate(plural):
        refs.append({"source_field": "rights_component_ids", "source_ordinal": ordinal, "assignment_role": "declared_component", "native_rights_id": str(right_id)})
    keys = [(ref["source_field"], ref["source_ordinal"], ref["native_rights_id"]) for ref in refs]
    require(len(keys) == len(set(keys)), f"duplicate rights reference: {collection}:{row['id']}")
    return refs


def _derive_owner_rights_assignments(backend: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for collection in ("units", "segments", "artifacts", "resources", "assets"):
        for owner in backend[collection]:
            for ref in _native_rights_references(collection, owner):
                rows.append({"owner_collection": collection, "native_target_id": str(owner["id"]), **ref})
    return rows


def _rights_assignment_identity(row: Mapping[str, Any]) -> str:
    return "\0".join((
        str(row["owner_collection"]), str(row["native_target_id"]), str(row["source_field"]),
        f"{int(row['source_ordinal']):04d}", str(row["assignment_role"]), str(row["native_rights_id"]),
    ))


def _payload_metadata(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("native_metadata", "owner_metadata"):
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            return nested
    return payload


def _required(payload: Mapping[str, Any], key: str, label: str) -> Any:
    require(key in payload, f"missing {key}: {label}")
    return payload[key]


def _assert_no_prose_fields(value: Any, label: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(str(key).lower() not in PROSE_FIELDS, f"full-prose field {key}: {label}")
            _assert_no_prose_fields(child, label)
    elif isinstance(value, list):
        for child in value:
            _assert_no_prose_fields(child, label)


def _assert_native_metadata(
    payload: Mapping[str, Any],
    native: Mapping[str, Any],
    label: str,
    *,
    omitted: set[str] | None = None,
) -> None:
    metadata = _payload_metadata(payload)
    omitted = (omitted or set()) | OWNER_ENVELOPE_KEYS
    for key, expected in native.items():
        if key in omitted:
            continue
        if key in payload:
            require(payload[key] == expected, f"conflicting top-level native metadata ({key}): {label}")
        require(key in metadata, f"native metadata field omitted ({key}): {label}")
        require(metadata[key] == expected, f"native metadata drift ({key}): {label}")


def _native_index(rows: Iterable[Mapping[str, Any]], label: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        native_id = str(row.get("id"))
        require(native_id and native_id != "None", f"missing owner ID: {label}")
        require(native_id not in result, f"duplicate owner ID: {label}:{native_id}")
        result[native_id] = row
    return result


def _projected_index(rows: Iterable[Mapping[str, Any]], label: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        payload = row["payload"]
        require("native_id" in payload, f"missing native_id: {label}:{row['id']}")
        native_id = str(payload["native_id"])
        require(native_id not in result, f"duplicate projected native_id: {label}:{native_id}")
        result[native_id] = row
    return result


def _verify_direct_projection(
    rows: list[dict[str, Any]],
    native_rows: list[dict[str, Any]],
    collection: str,
    *,
    omitted: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    native = _native_index(native_rows, collection)
    projected = _projected_index(rows, collection)
    require(set(projected) == set(native) and len(rows) == len(native), f"direct {collection} identity closure drift")
    for native_id, owner_row in native.items():
        row = projected[native_id]
        payload = row["payload"]
        require(payload.get("native_collection") == collection, f"native collection drift: {collection}:{native_id}")
        require(payload.get("owner_record_sha256") == _owner_record_sha256(owner_row), f"owner row hash drift: {collection}:{native_id}")
        require(row["owner_native_state"] == owner_row.get("status"), f"owner native state drift: {collection}:{native_id}")
        _assert_native_metadata(payload, owner_row, f"{collection}:{native_id}", omitted=omitted)
    return projected


def _find_named_fact(value: Any, filename: str, expected: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    matches: list[Mapping[str, Any]] = []
    for item in _walk_mappings(value):
        name = item.get("name", item.get("file_name", item.get("path")))
        if name == filename or str(name).endswith("/" + filename):
            if item.get("bytes") == expected["bytes"] and item.get("sha256") == expected["sha256"]:
                matches.append(item)
    return matches


def _load_and_validate_owner(owner_root: Path) -> dict[str, Any]:
    owner_root = owner_root.resolve()
    require(owner_root.is_dir(), f"owner package root missing: {owner_root}")
    authority_facts = {relative: _require_fact(owner_root, relative, expected) for relative, expected in OWNER_AUTHORITY_FACTS.items()}

    backend_root = owner_root / "backend" / "dist"
    backend_manifest = read_json(backend_root / "manifest.json")
    require(backend_manifest.get("schema_name") == "interlanguage.artifact-manifest", "owner backend manifest schema drift")
    manifest_facts = backend_manifest.get("artifacts")
    require(isinstance(manifest_facts, list) and len(manifest_facts) == 30, "owner backend manifest must contain exactly 30 payload artifacts")
    manifest_by_path = {str(fact["path"]): fact for fact in manifest_facts}
    require(len(manifest_by_path) == 30, "duplicate owner backend manifest path")
    for relative, fact in manifest_by_path.items():
        observed = _fact_at(backend_root, relative)
        require(observed["bytes"] == fact["bytes"] and observed["sha256"] == fact["sha256"], f"owner backend artifact drift: {relative}")

    checksum_rows = _parse_checksum_rows(backend_root / "SHA256SUMS.txt")
    checksum_map = {relative: digest for digest, relative in checksum_rows}
    expected_checksum_map = {relative: str(fact["sha256"]) for relative, fact in manifest_by_path.items()}
    expected_checksum_map["manifest.json"] = OWNER_AUTHORITY_FACTS["backend/dist/manifest.json"][1]
    require(checksum_map == expected_checksum_map and len(checksum_rows) == 31, "owner backend checksum closure drift")

    backend = read_json(backend_root / "backend-v0.json")
    expected_top_keys = set(OWNER_COUNTS) | {"schema_name", "schema_version", "snapshot_at"}
    require(set(backend) == expected_top_keys, f"owner backend collection surface drift: {sorted(backend)}")
    require(backend["schema_name"] == "interlanguage.modular-backend" and backend["schema_version"] == "0.1.0", "owner backend schema/version drift")
    observed_counts = {name: len(backend[name]) for name in OWNER_COUNTS}
    require(observed_counts == OWNER_COUNTS, f"owner backend cardinality drift: {observed_counts}")

    for collection in OWNER_COUNTS:
        jsonl_relative = f"jsonl/{collection}.jsonl"
        require(jsonl_relative in manifest_by_path, f"owner JSONL shard absent from manifest: {collection}")
        jsonl_rows = read_jsonl(backend_root / jsonl_relative, require_canonical=False)
        require(jsonl_rows == backend[collection], f"owner monolith/JSONL disagreement: {collection}")

    all_native: dict[str, str] = {}
    for collection in OWNER_COUNTS:
        if collection == "relations":
            continue
        for native_id in _native_index(backend[collection], collection):
            require(native_id not in all_native, f"owner global ID collision: {native_id}")
            all_native[native_id] = collection
    for relation in backend["relations"]:
        require(relation["from_id"] in all_native, f"dangling owner relation from endpoint: {relation['id']}")
        require(relation["to_id"] in all_native, f"dangling owner relation to endpoint: {relation['id']}")

    require(Counter(row["locale"] for row in backend["units"]) == {"id-ID": 1205, "mul": 788}, "owner unit locale distribution drift")
    require(Counter(row["translation_state"] for row in backend["units"]) == EXPECTED_UNIT_TRANSLATION_STATES, "owner unit translation-state distribution drift")
    require(Counter(row["translation_state"] for row in backend["segments"]) == EXPECTED_SEGMENT_TRANSLATION_STATES, "owner segment translation-state distribution drift")
    require(Counter(row["source_target_relationship"] for row in backend["segments"]) == EXPECTED_SEGMENT_RELATIONSHIPS, "owner segment source/target distribution drift")
    require(Counter(row["relation_type"] for row in backend["relations"]) == EXPECTED_RELATION_TYPES, "owner typed-relation distribution drift")

    release_root = owner_root / "release" / "out"
    release_manifest = read_json(release_root / "RELEASE-MANIFEST.json")
    release_artifacts = {row["file_name"]: row for row in release_manifest.get("artifacts", [])}
    require(set(release_artifacts) == set(PUBLIC_DOWNLOADS), "owner release primary artifact set drift")
    for filename, expected in PUBLIC_DOWNLOADS.items():
        row = release_artifacts[filename]
        require((row["bytes"], row["sha256"]) == (expected["bytes"], expected["sha256"]), f"owner release artifact drift: {filename}")

    release_checksum_rows = _parse_checksum_rows(release_root / "SHA256SUMS.txt")
    release_checksum_map = {relative: digest for digest, relative in release_checksum_rows}
    actual_release_files = {
        path.name: sha256_file(path)
        for path in release_root.iterdir()
        if path.is_file() and path.name != "SHA256SUMS.txt"
    }
    require(release_checksum_map == actual_release_files and len(release_checksum_rows) == 12, "owner release checksum closure drift")

    cursor = read_json(owner_root / "00_control" / "CURRENT_CURSOR.json")
    require(cursor["translation_cursor"] == {
        "admitted_through": "unit.r017.book1.backmatter",
        "o018_admitted_through": "unit.o018.book1.complete",
        "translated_pending_admission": [],
        "o018_pending_admission": [],
        "translation_in_progress": [],
        "remaining_translation": [],
        "complete": True,
    }, "owner translation cursor drift")
    require({key: cursor["backend"][key] for key in ("units", "segments", "relations", "artifacts", "assets", "concepts", "terms", "rights", "corrections", "qa_events")} == {
        key: OWNER_COUNTS[key] for key in ("units", "segments", "relations", "artifacts", "assets", "concepts", "terms", "rights", "corrections", "qa_events")
    }, "owner cursor backend counts drift")
    cursor_pdf = cursor["current_artifacts"]["final_pdf"]
    require((cursor_pdf["bytes"], cursor_pdf["pages"], cursor_pdf["sha256"], cursor_pdf["tagged"]) == (
        PUBLIC_DOWNLOADS["pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf"]["bytes"],
        666,
        PUBLIC_DOWNLOADS["pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf"]["sha256"],
        False,
    ), "owner PDF identity/tagging drift")
    cursor_report = cursor["current_artifacts"]["release"]
    require(cursor_report["qa_report"] == "qa/release-package-report.json", "owner cursor release-report path drift")
    require(cursor_report["qa_report_sha256"] == STALE_RELEASE_REPORT_SHA256, "expected stale cursor digest is absent")
    require(STALE_RELEASE_REPORT_SHA256 != CURRENT_RELEASE_REPORT_SHA256, "stale/current release-report digests unexpectedly equal")

    zenodo = read_json(owner_root / "release" / "receipts" / "zenodo-publication-receipt-2026.08.23-id.5.json")
    require((zenodo["record_id"], zenodo["record_url"], zenodo["doi"], zenodo["concept_doi"]) == (
        22070653,
        ZENODO_URL,
        "10.5281/zenodo.22070653",
        "10.5281/zenodo.22059794",
    ), "Zenodo identity drift")
    zenodo_files = {row["name"]: row for row in zenodo["files"]}
    require(len(zenodo_files) == zenodo["file_count"] == 13, "Zenodo file cardinality drift")
    for filename, digest in release_checksum_map.items():
        require(filename in zenodo_files, f"Zenodo release file missing: {filename}")
        local_path = release_root / filename
        require((zenodo_files[filename]["bytes"], zenodo_files[filename]["sha256"], zenodo_files[filename]["anonymous_readback"]) == (
            local_path.stat().st_size,
            digest,
            True,
        ), f"Zenodo file readback drift: {filename}")
    sums = zenodo_files.get("SHA256SUMS.txt")
    require(sums is not None and (sums["bytes"], sums["sha256"]) == OWNER_AUTHORITY_FACTS["release/out/SHA256SUMS.txt"], "Zenodo checksum-file identity drift")
    expected_zenodo_checks = {
        "exact_inventory": True,
        "all_public_bytes_match_local_sha256": True,
        "anonymous_readback": True,
        "credential_in_url": False,
        "credential_material_persisted": False,
        "concept_lineage_exact": True,
        "direct_predecessor_exact": True,
        "title_version_language_license_exact": True,
        "release_manifest_and_checksums_exact": True,
    }
    require(zenodo["checks"] == expected_zenodo_checks, "Zenodo receipt check-state drift")

    plan = read_json(owner_root / "qa" / "github-publication-plan.json")
    github = read_json(owner_root / "release" / "receipts" / "github-publication-receipt.json")
    require(plan.get("expected_owner") == "KokunoYumeto" and plan.get("repository_name") == "open-optimization-or-book-id", "GitHub plan repository identity drift")
    require(REPOSITORY_URL in compact_json(github), "GitHub receipt repository URL drift")
    require(PAGES_URL in compact_json(github), "GitHub receipt Pages URL drift")
    for document, label in ((plan, "GitHub plan"), (github, "GitHub receipt")):
        report_matches = _find_named_fact(document, "qa/release-package-report.json", {"bytes": 5130, "sha256": CURRENT_RELEASE_REPORT_SHA256})
        require(report_matches, f"{label} does not independently bind the current release report")
        for filename, expected in PUBLIC_DOWNLOADS.items():
            facts = _find_named_fact(document, filename, expected)
            require(facts, f"{label} public artifact fact missing: {filename}")
    for filename, expected in PUBLIC_DOWNLOADS.items():
        pages_matches = [
            item for item in _find_named_fact(github, filename, expected)
            if item.get("url") == expected["url"]
        ]
        require(pages_matches, f"GitHub receipt lacks exact Pages download URL/fact: {filename}")

    return {
        "backend": backend,
        "backend_manifest": backend_manifest,
        "backend_manifest_by_path": manifest_by_path,
        "authority_facts": authority_facts,
        "cursor": cursor,
        "release_manifest": release_manifest,
        "release_checksum_map": release_checksum_map,
        "zenodo": zenodo,
        "github_plan": plan,
        "github_receipt": github,
        "all_native_types": all_native,
    }


def _validate_input_authorities(
    package: Path,
    manifest: Mapping[str, Any],
    owner_root: Path,
    repository_root: Path,
) -> dict[str, Any]:
    inputs = read_json(package / "INPUT_AUTHORITIES.json")
    facts = inputs.get("authorities")
    require(isinstance(facts, list), "INPUT_AUTHORITIES authorities missing")
    expected = {
        relative: ("owner_package_root", *value)
        for relative, value in OWNER_AUTHORITY_FACTS.items()
    }
    expected.update({
        relative: ("program_repository_root", *value)
        for relative, value in PROGRAM_AUTHORITY_FACTS.items()
    })

    def normalize(rows: Iterable[Mapping[str, Any]], label: str) -> dict[str, tuple[str, int, str]]:
        result: dict[str, tuple[str, int, str]] = {}
        for row in rows:
            relative = str(row["path"])
            require(relative not in result, f"duplicate {label} authority: {relative}")
            result[relative] = (str(row["path_base"]), int(row["bytes"]), str(row["sha256"]))
        return result

    observed_inputs = normalize(facts, "input")
    observed_manifest = normalize(manifest["authorities"], "manifest")
    require(observed_inputs == expected, f"C130 input-authority set drift: {observed_inputs}")
    require(observed_manifest == expected, "manifest/input authority disagreement")
    for relative, fact in OWNER_AUTHORITY_FACTS.items():
        _require_fact(owner_root, relative, fact)
    for relative, fact in PROGRAM_AUTHORITY_FACTS.items():
        _require_fact(repository_root, relative, fact)

    stale_disclosures = []
    for item in _walk_mappings(inputs):
        blob = _string_blob(item)
        if STALE_RELEASE_REPORT_SHA256 in blob and CURRENT_RELEASE_REPORT_SHA256 in blob:
            stale_disclosures.append(item)
    require(stale_disclosures, "stale cursor/current release-report mismatch is not disclosed")
    disclosure_blob = "\n".join(_string_blob(item) for item in stale_disclosures)
    require("stale" in disclosure_blob and "qa/release-package-report.json" in disclosure_blob, "release-report mismatch is not explicitly classified stale")
    require("qa/github-publication-plan.json" in disclosure_blob and "release/receipts/github-publication-receipt.json" in disclosure_blob, "independent current release-report witnesses are not disclosed")
    return {"authority_files": len(expected), "stale_release_report_disclosed": True}


def _validate_projection_ids(tables: Mapping[str, list[dict[str, Any]]], lane_namespace: str) -> None:
    namespace = uuid.UUID(lane_namespace)
    for table_name in TABLE_ORDER:
        for row in tables[table_name]:
            expected = projection_id(namespace, row["record_type"], row["semantic_key"])
            require(row["id"] == expected, f"non-deterministic projected ID: {table_name}:{row['semantic_key']}")


def _validate_unit_cluster(
    tables: Mapping[str, list[dict[str, Any]]],
    backend: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    units = _verify_direct_projection(tables["units"], backend["units"], "units")
    native_units = _native_index(backend["units"], "units")
    for native_id, row in units.items():
        owner = native_units[native_id]
        payload = row["payload"]
        projected_parent = units[owner["parent_id"]]["id"] if owner.get("parent_id") else None
        if "projected_parent_id" in payload:
            require(payload["projected_parent_id"] == projected_parent, f"projected parent drift: {native_id}")
        learner = payload.get("learner_route")
        if learner is not None:
            require(isinstance(learner, Mapping), f"bad unit learner route: {native_id}")
            require(learner.get("anchor") is None and learner.get("unit_anchor") is None and learner.get("page_anchor") is None, f"invented unit/page anchor: {native_id}")
            require(learner.get("url", learner.get("public_url")) in EXPECTED_ROUTE_URLS, f"unverified unit learner URL: {native_id}")

    memberships: dict[str, dict[str, Any]] = {}
    ordinals: set[int] = set()
    for row in tables["course_unit_memberships"]:
        payload = row["payload"]
        native_id = str(_required(payload, "native_unit_id", "course membership"))
        require(native_id not in memberships and native_id in units, f"membership identity drift: {native_id}")
        projected_id = payload.get("projected_unit_id", payload.get("unit_id"))
        require(projected_id == units[native_id]["id"], f"membership projected-unit drift: {native_id}")
        require(payload.get("curriculum_role_id", payload.get("course_id")) == ROLE_ID, f"membership course-role drift: {native_id}")
        ordinal = int(_required(payload, "ordinal", f"membership:{native_id}"))
        require(ordinal not in ordinals, f"duplicate membership ordinal: {ordinal}")
        ordinals.add(ordinal)
        memberships[native_id] = row
    require(set(memberships) == set(units) and ordinals == set(range(1, 1994)), "one-to-one unit membership/order closure drift")

    search: dict[str, dict[str, Any]] = {}
    for row in tables["search_documents"]:
        payload = row["payload"]
        native_id = str(_required(payload, "native_unit_id", "search document"))
        require(native_id not in search and native_id in units, f"search identity drift: {native_id}")
        projected_id = payload.get("projected_unit_id", payload.get("unit_id"))
        require(projected_id == units[native_id]["id"], f"search projected-unit drift: {native_id}")
        require(payload.get("learner_anchor") is None and payload.get("unit_anchor") is None and payload.get("page_anchor") is None, f"invented search anchor: {native_id}")
        learner_url = payload.get("learner_url", payload.get("public_url"))
        require(learner_url in EXPECTED_ROUTE_URLS, f"unverified search learner URL: {native_id}")
        _assert_no_prose_fields(payload, f"search:{native_id}")
        search[native_id] = row
    require(set(search) == set(units), "one-to-one search-document closure drift")
    return units, search


def _validate_segments(
    tables: Mapping[str, list[dict[str, Any]]],
    backend: Mapping[str, Any],
    units: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    native_segments = _native_index(backend["segments"], "segments")
    bindings = _projected_index(tables["native_bindings"], "native_bindings")
    require(set(bindings) == set(native_segments), "native segment-binding identity closure drift")
    for native_id, owner in native_segments.items():
        row = bindings[native_id]
        payload = row["payload"]
        require(payload.get("native_collection") == "segments", f"segment native collection drift: {native_id}")
        require(payload.get("native_record_type") == "segment", f"segment native record type drift: {native_id}")
        require(payload.get("owner_record_sha256") == _owner_record_sha256(owner), f"segment binding owner hash drift: {native_id}")
        require(payload.get("native_unit_id") == owner["unit_id"], f"segment binding owner unit drift: {native_id}")
        require(payload.get("projected_unit_id") == units[owner["unit_id"]]["id"], f"segment binding projected unit drift: {native_id}")
        require(row["owner_native_state"] == owner["status"], f"segment binding native state drift: {native_id}")

    content: dict[str, dict[str, Any]] = {}
    for row in tables["content_bindings"]:
        payload = row["payload"]
        native_id = str(payload.get("native_id", payload.get("native_segment_id")))
        require(native_id and native_id != "None", f"content binding lacks native segment ID: {row['id']}")
        require(native_id not in content and native_id in native_segments, f"content binding identity drift: {native_id}")
        owner = native_segments[native_id]
        require(payload.get("native_id") == native_id, f"content binding canonical native_id drift: {native_id}")
        require(payload.get("native_collection") == "segments", f"content binding native collection drift: {native_id}")
        require(payload.get("owner_record_sha256") == _owner_record_sha256(owner), f"content binding owner hash drift: {native_id}")
        require(payload.get("native_unit_id") == owner["unit_id"], f"content binding owner unit drift: {native_id}")
        require(payload.get("projected_unit_id") == units[owner["unit_id"]]["id"], f"content binding projected unit drift: {native_id}")
        require(payload.get("content_included_in_adapter") is False and payload.get("full_text_included") is False, f"content centralized in adapter: {native_id}")
        require(row["owner_native_state"] == owner["status"], f"content binding native state drift: {native_id}")
        _assert_no_prose_fields(payload, f"content_binding:{native_id}")
        _assert_native_metadata(payload, owner, f"segments:{native_id}", omitted={"source_text", "target_text"})
        content[native_id] = row
    require(set(content) == set(native_segments), "zero-copy content-binding closure drift")
    require(Counter(row["payload"]["translation_state"] for row in content.values()) == EXPECTED_SEGMENT_TRANSLATION_STATES, "projected segment translation-state drift")
    require(Counter(row["payload"]["source_target_relationship"] for row in content.values()) == EXPECTED_SEGMENT_RELATIONSHIPS, "projected segment relationship drift")
    return bindings, content


def _validate_relations_and_rights(
    tables: Mapping[str, list[dict[str, Any]]],
    backend: Mapping[str, Any],
    units: Mapping[str, Mapping[str, Any]],
    segment_bindings: Mapping[str, Mapping[str, Any]],
    artifacts: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    relations = _verify_direct_projection(tables["relations"], backend["relations"], "relations")
    require(Counter(row["payload"]["relation_type"] for row in relations.values()) == EXPECTED_RELATION_TYPES, "projected typed-relation distribution drift")
    rights = _verify_direct_projection(tables["rights"], backend["rights"], "rights")

    projection_maps = {"units": units, "segments": segment_bindings, "artifacts": artifacts}
    target_record_types = {"units": "unit", "segments": "native_binding", "artifacts": "artifact"}
    expected_assignments: dict[tuple[str, str, str, int, str, str], tuple[str, str, str]] = {}
    for collection in ("units", "segments", "artifacts"):
        for owner in backend[collection]:
            native_id = str(owner["id"])
            for ref in _native_rights_references(collection, owner):
                right_id = ref["native_rights_id"]
                key = (
                    collection, native_id, ref["source_field"], int(ref["source_ordinal"]),
                    ref["assignment_role"], right_id,
                )
                require(key not in expected_assignments, f"duplicate derived component-right assignment: {key}")
                expected_assignments[key] = (
                    str(projection_maps[collection][native_id]["id"]),
                    str(rights[right_id]["id"]),
                    target_record_types[collection],
                )
    require(len(expected_assignments) == 7634, "derived projected component-right assignment cardinality drift")

    collection_by_target_type = {value: key for key, value in target_record_types.items()}
    observed: dict[tuple[str, str, str, int, str, str], tuple[str, str, str]] = {}
    for row in tables["rights_assignments"]:
        payload = row["payload"]
        native_target = str(_required(payload, "native_target_id", "rights assignment"))
        native_right = str(_required(payload, "native_rights_id", f"rights assignment:{native_target}"))
        role = str(_required(payload, "assignment_role", f"rights assignment:{native_target}"))
        source_field = str(_required(payload, "source_field", f"rights assignment:{native_target}"))
        source_ordinal = int(_required(payload, "source_ordinal", f"rights assignment:{native_target}"))
        target_record_type = str(_required(payload, "target_record_type", f"rights assignment:{native_target}"))
        require(target_record_type in collection_by_target_type, f"unknown rights-assignment target type: {target_record_type}")
        key = (collection_by_target_type[target_record_type], native_target, source_field, source_ordinal, role, native_right)
        require(key not in observed, f"duplicate component-right assignment: {key}")
        observed[key] = (
            str(_required(payload, "target_id", f"rights assignment:{key}")),
            str(_required(payload, "rights_id", f"rights assignment:{key}")),
            target_record_type,
        )
    require(observed == expected_assignments, "exact component-right assignment closure drift")
    return relations, rights


def _validate_artifacts_and_qa(
    tables: Mapping[str, list[dict[str, Any]]],
    backend: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    artifacts = _verify_direct_projection(tables["artifacts"], backend["artifacts"], "artifacts")
    owner_qa_ids = {row["id"] for row in backend["qa_events"]}
    owner_rows = [row for row in tables["qa_events"] if row["payload"].get("native_id") in owner_qa_ids]
    adapter_rows = [row for row in tables["qa_events"] if row["payload"].get("native_id") not in owner_qa_ids]
    owner_qa = _verify_direct_projection(owner_rows, backend["qa_events"], "qa_events")
    for native_id, row in owner_qa.items():
        payload = row["payload"]
        require(payload.get("qa_origin") == "owner_native_provenance", f"owner QA relabeled as adapter validation: {native_id}")
        require(payload.get("independent_adapter_validation", False) is False, f"owner QA independent-validation overclaim: {native_id}")
    require(len(adapter_rows) == 1, "exactly one adapter-generated QA event is required")
    adapter = adapter_rows[0]
    payload = adapter["payload"]
    require(payload.get("qa_origin") == "adapter_generated", "adapter QA provenance drift")
    require(payload.get("qa_type") == "adapter_build" and payload.get("result") == "pass", "adapter-build QA result/type drift")
    require(adapter["owner_native_state"] is None, "adapter QA incorrectly claims an owner-native state")
    require(_contains_exact_mapping(payload, EXPECTED_TABLE_COUNTS), "adapter QA does not bind exact table counts")
    adapter_blob = _string_blob(payload)
    require(LIMITATIONS_AUTHORITY_FACT[1] in adapter_blob or LIMITATIONS_AUTHORITY_PATH.lower() in adapter_blob, "adapter QA omits native-pipeline limitations evidence")
    return artifacts, owner_qa, adapter


def _validate_rights_assignment_closure_sidecar(
    package: Path,
    manifest: Mapping[str, Any],
    sidecar: Mapping[str, Any],
    capabilities: Mapping[str, Any],
    backend: Mapping[str, Any],
    rights: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    rows = _derive_owner_rights_assignments(backend)
    counts = dict(sorted(Counter(row["owner_collection"] for row in rows).items()))
    require(counts == {"artifacts": 70, "assets": 346, "resources": 9, "segments": 5525, "units": 2039}, "owner rights-assignment distribution drift")
    materialized = [row for row in rows if row["owner_collection"] in {"units", "segments", "artifacts"}]
    referenced_only = [row for row in rows if row["owner_collection"] in {"resources", "assets"}]
    require((len(rows), len(materialized), len(referenced_only)) == (7989, 7634, 355), "owner rights-assignment partition drift")
    expected_summary = {
        "by_collection": counts,
        "total": len(rows),
        "materialized_total": len(materialized),
        "referenced_only_total": len(referenced_only),
        "identity_set_sha256": identity_set_sha256(_rights_assignment_identity(row) for row in rows),
        "materialized_identity_set_sha256": identity_set_sha256(_rights_assignment_identity(row) for row in materialized),
        "referenced_only_identity_set_sha256": identity_set_sha256(_rights_assignment_identity(row) for row in referenced_only),
    }
    require(sidecar.get("schema_id") == "program-matematika-indonesia/c130-owner-rights-assignment-closure/0.1.0", "rights sidecar schema drift")
    require(sidecar.get("counts") == expected_summary, "rights sidecar summary/hash drift")
    require(sidecar.get("owner_backend_binding", {}).get("sha256") == OWNER_AUTHORITY_FACTS["backend/dist/backend-v0.json"][1], "rights sidecar owner authority drift")
    require(sidecar.get("materialized_projection") == {
        "table": "tables/rights_assignments.jsonl",
        "records": 7634,
        "target_types": {"artifact": 70, "native_binding": 5525, "unit": 2039},
        "state": "canonical_v2_3_1_rows",
    }, "rights sidecar materialized projection drift")

    expected_referenced_rows = [
        {
            **row,
            "projected_rights_id": rights[row["native_rights_id"]]["id"],
            "projected_target_id": None,
            "state": "owner_native_assignment_preserved_target_type_not_projected_in_v2_3_1",
        }
        for row in referenced_only
    ]
    expected_referenced_rows.sort(key=lambda row: (
        row["owner_collection"], row["native_target_id"], row["source_field"], row["source_ordinal"], row["native_rights_id"]
    ))
    referenced = sidecar.get("referenced_only_projection", {})
    require(referenced.get("records") == 355 and referenced.get("target_collections") == {"assets": 346, "resources": 9}, "rights sidecar referenced-only counts drift")
    require(referenced.get("assignments") == expected_referenced_rows, "rights sidecar referenced-only assignment closure drift")
    require("no target ids were invented" in str(referenced.get("reason", "")).lower(), "rights sidecar does not disclose unprojected target treatment")

    no_assignment_artifacts = sorted(
        str(row["id"]) for row in backend["artifacts"] if not _native_rights_references("artifacts", row)
    )
    require(sidecar.get("artifacts_without_native_rights_assignment") == {
        "records": 31,
        "native_artifact_ids": no_assignment_artifacts,
        "identity_set_sha256": identity_set_sha256(no_assignment_artifacts),
        "state": "preserved_as_owner_native_absence_not_inferred",
    }, "rights sidecar explicit artifact absence drift")
    require(sidecar.get("all_21_rights_identities_materialized") is True and sidecar.get("flattened_license_claim") is False, "rights sidecar flattening/materialization claim drift")
    require({row["native_rights_id"] for row in rows} == set(rights), "not all owner rights identities participate in the assignment closure")

    path = package / "rights-assignment-closure-v0.1.0.json"
    expected_fact = {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest_facts = {str(row["path"]): row for row in manifest["sidecars"]}
    require(path.name in manifest_facts, "rights sidecar absent from package manifest")
    require(all(manifest_facts[path.name].get(key) == value for key, value in expected_fact.items()), "rights sidecar manifest fact drift")
    shard_facts = {str(row["path"]): row for row in capabilities["rights_cross_cutting"]["shard_refs"]}
    require(path.name in shard_facts, "rights sidecar absent from cross-cutting capability binding")
    require(all(shard_facts[path.name].get(key) == value for key, value in expected_fact.items()), "rights sidecar capability fact drift")
    require(capabilities["rights_cross_cutting"]["native_count"] == 21, "rights cross-cutting identity count drift")
    closure_blob = _string_blob(capabilities["rights_cross_cutting"]["closure_rules"])
    for token in ("7,634", "355", "resource", "asset"):
        require(token.lower() in closure_blob, f"rights capability closure disclosure missing: {token}")
    return {"native_assignments": 7989, "materialized_assignments": 7634, "referenced_only_assignments": 355, "rights_identities": 21}


def _validate_routes_and_surfaces(tables: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    surfaces = tables["reader_surfaces"]
    require(len(surfaces) == 1, "C130 requires exactly one PDF reader surface")
    surface = surfaces[0]["payload"]
    pdf = PUBLIC_DOWNLOADS["pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf"]
    surface_url = surface.get("public_url", surface.get("url"))
    require(surface_url == pdf["url"], "reader-surface PDF URL drift")
    require((surface.get("pages"), surface.get("bytes"), surface.get("sha256")) == (666, pdf["bytes"], pdf["sha256"]), "reader-surface PDF identity drift")
    require("pdf" in str(surface.get("format", "")).lower(), "reader surface is not PDF")
    require(surface.get("primary") is True and surface.get("tagged") is False, "reader primacy/tagging drift")
    require(surface.get("unit_anchor_coverage", 0) == 0 and surface.get("page_anchor_coverage", 0) == 0, "invented reader anchors")
    require(surface.get("pdf_ua_claimed", False) is False, "PDF/UA claim introduced")
    require(surface.get("pdf_ua_verified", False) is False, "PDF/UA verification claim introduced")
    require(surface.get("pdf_ua_conformance") in (None, False, "none", "not_claimed"), "PDF/UA conformance claim introduced")

    observed_urls: dict[str, Mapping[str, Any]] = {}
    for row in tables["routes"]:
        payload = row["payload"]
        url = str(payload.get("public_url", payload.get("url")))
        require(url not in observed_urls, f"duplicate learner route URL: {url}")
        observed_urls[url] = payload
        require(payload.get("unit_id") is None and payload.get("projected_unit_id") is None, f"invented unit route: {url}")
        require(payload.get("unit_anchor") is None and payload.get("page_anchor") is None and payload.get("anchor") is None, f"invented unit/page anchor: {url}")
        require(payload.get("native_html_available", False) is False, f"native chapter HTML overclaim: {url}")
        kind_blob = f"{payload.get('route_kind', '')} {payload.get('target_kind', '')}".lower()
        require(not ("html" in kind_blob and ("chapter" in kind_blob or "unit" in kind_blob or "native" in kind_blob)), f"invented native chapter HTML route: {url}")
    require(set(observed_urls) == EXPECTED_ROUTE_URLS, f"honest learner-route set drift: {set(observed_urls)}")

    route_tokens = {
        REPOSITORY_URL: "repository",
        PAGES_URL: "pages",
        ZENODO_URL: "zenodo",
        **{fact["url"]: fact["route_token"] for fact in PUBLIC_DOWNLOADS.values()},
    }
    for url, token in route_tokens.items():
        payload = observed_urls[url]
        kind_blob = f"{payload.get('route_kind', '')} {payload.get('target_kind', '')}".lower()
        require(token in kind_blob, f"route kind does not identify {token}: {url}")
    for filename, expected in PUBLIC_DOWNLOADS.items():
        payload = observed_urls[expected["url"]]
        require(payload.get("filename", payload.get("name")) == filename, f"route filename drift: {filename}")
        require((payload.get("bytes"), payload.get("sha256")) == (expected["bytes"], expected["sha256"]), f"route artifact fact drift: {filename}")
    return {"reader_surfaces": 1, "routes": len(observed_urls), "native_chapter_html": False, "anchors": 0, "pdf_ua_claimed": False}


def _validate_namespace_and_crosswalk(
    tables: Mapping[str, list[dict[str, Any]]],
    namespace: Mapping[str, Any],
    direct: Mapping[str, Mapping[str, Mapping[str, Any]]],
    backend: Mapping[str, Any],
) -> str:
    mappings = namespace["mappings"]
    require(len(mappings) == 34546, "namespace mapping cardinality drift")
    target_namespaces = {str(row["target_namespace"]) for row in mappings}
    source_namespaces = {str(row["source_namespace"]) for row in mappings}
    require(len(target_namespaces) == 1 and len(source_namespaces) == 2, "namespace partition drift")
    target_namespace = next(iter(target_namespaces))
    uuid.UUID(target_namespace)
    require(str(PREVIOUS_COMMON_NAMESPACE) in source_namespaces and target_namespace not in source_namespaces, "prior-v1/lane namespace partition drift")
    owner_namespaces = source_namespaces - {str(PREVIOUS_COMMON_NAMESPACE)}
    require(len(owner_namespaces) == 1, "owner backend namespace drift")
    owner_namespace = next(iter(owner_namespaces))

    expected_owner: dict[tuple[str, str], tuple[str, str]] = {}
    for source_type, (collection, target_type) in DIRECT_MAPPING_SPECS.items():
        for native_id, row in direct[collection].items():
            expected_owner[(source_type, native_id)] = (target_type, row["id"])
    require(len(expected_owner) == 17273, "derived owner namespace mapping cardinality drift")

    prior = _prior_v1_identity_facts(backend)
    expected_prior: dict[tuple[str, str], tuple[str, str]] = {}
    for (_, native_id), (target_type, target_id) in expected_owner.items():
        collection = prior["native_table_by_id"][native_id]
        prior_type = PRIOR_V1_DIRECT_TYPES[collection]
        expected_prior[(prior_type, prior["prior_id_by_native_id"][native_id])] = (target_type, target_id)
    require(len(expected_prior) == 17273, "derived prior-v1 namespace mapping cardinality drift")

    expected = {
        **{(owner_namespace, source_type, source_id): target for (source_type, source_id), target in expected_owner.items()},
        **{(str(PREVIOUS_COMMON_NAMESPACE), source_type, source_id): target for (source_type, source_id), target in expected_prior.items()},
    }
    require(len(expected) == 34546, "combined namespace mapping cardinality drift")

    observed: dict[tuple[str, str, str], tuple[str, str]] = {}
    for mapping in mappings:
        key = (str(mapping["source_namespace"]), str(mapping["source_record_type"]), str(mapping["source_record_id"]))
        require(key not in observed, f"duplicate namespace source mapping: {key}")
        require(mapping.get("cardinality") == "one_to_one" and mapping.get("mapping_state") == "mapped", f"non-one-to-one namespace mapping: {key}")
        require(mapping.get("owner_id_reminted", False) is False, f"owner ID remint claim: {key}")
        require(str(mapping["target_namespace"]) == target_namespace, f"namespace mapping target partition drift: {key}")
        observed[key] = (str(mapping["target_record_type"]), str(mapping["target_record_id"]))
    require(observed == expected, "exact owner-to-projection namespace closure drift")

    profiles = namespace.get("profiles", [])
    profile_namespaces = {str(row["namespace"]) for row in profiles}
    require({owner_namespace, str(PREVIOUS_COMMON_NAMESPACE), target_namespace}.issubset(profile_namespaces), "owner/prior/lane namespace profiles missing")
    prior_profiles = [row for row in profiles if str(row.get("namespace")) == str(PREVIOUS_COMMON_NAMESPACE)]
    require(len(prior_profiles) == 1, "prior-v1 namespace profile cardinality drift")
    prior_profile = prior_profiles[0]
    require(prior_profile.get("name") == "c130_prior_common_v1_materialized", "prior-v1 profile misclassified")
    require((prior_profile.get("materialized_records"), prior_profile.get("mapped_to_v2_3_1"), prior_profile.get("not_projected_in_v2_3_1")) == (17987, 17273, 714), "prior-v1 profile coverage drift")
    require("o018-c130:native:" in str(prior_profile.get("formula")) and "uuidv5" in str(prior_profile.get("formula")).lower(), "prior-v1 profile formula drift")

    projected_native_ids = {native_id for _, native_id in expected_owner}
    unprojected_prior_rows = [
        {
            "native_collection": prior["native_table_by_id"][native_id],
            "native_record_id": native_id,
            "prior_v1_record_type": PRIOR_V1_DIRECT_TYPES[prior["native_table_by_id"][native_id]],
            "prior_v1_record_id": prior["prior_id_by_native_id"][native_id],
            "state": "materialized_in_prior_v1_not_projected_in_v2_3_1",
        }
        for native_id in sorted(set(prior["prior_id_by_native_id"]) - projected_native_ids)
    ]
    require(len(unprojected_prior_rows) == 714, "prior-v1 unprojected partition drift")
    unprojected_by_collection = dict(sorted(Counter(row["native_collection"] for row in unprojected_prior_rows).items()))
    require(unprojected_by_collection == {"assets": 346, "concepts": 128, "corrections": 94, "courses": 1, "programs": 1, "resources": 4, "terms": 140}, "prior-v1 unprojected distribution drift")

    identity_sets = namespace.get("identity_sets", {})
    expected_identity_sets = {
        "owner_direct_records_sha256": identity_set_sha256(native_id for _, native_id in expected_owner),
        "projected_direct_records_sha256": identity_set_sha256(target_id for _, target_id in expected_owner.values()),
        "prior_v1_all_records_sha256": prior["all_prior_ids_sha256"],
        "prior_v1_projected_records_sha256": identity_set_sha256(source_id for _, source_id in expected_prior),
        "prior_v1_unprojected_records_sha256": identity_set_sha256(row["prior_v1_record_id"] for row in unprojected_prior_rows),
        "prior_v1_native_to_prior_pairs_sha256": prior["native_to_prior_pairs_sha256"],
        "prior_v1_projected_to_v2_3_1_pairs_sha256": mapping_set_sha256((source_id, target_id) for (_, source_id), (_, target_id) in expected_prior.items()),
        "prior_v1_unprojected_owner_to_prior_pairs_sha256": mapping_set_sha256((row["native_record_id"], row["prior_v1_record_id"]) for row in unprojected_prior_rows),
        "prior_v1_mapping_payload_bytes": PRIOR_V1_MAPPING_BYTES,
        "prior_v1_mapping_payload_sha256": PRIOR_V1_MAPPING_SHA256,
        "prior_v1_materialized_records": 17987,
        "prior_v1_projected_records": 17273,
        "prior_v1_unprojected_records": 714,
        "prior_v1_unprojected_by_collection": unprojected_by_collection,
        "prior_v1_unprojected_identity_rows": unprojected_prior_rows,
        "mapped_pairs_sha256": mapping_set_sha256((str(row["source_record_id"]), str(row["target_record_id"])) for row in mappings),
        "owner_to_v2_3_1_mappings": 17273,
        "prior_v1_to_v2_3_1_mappings": 17273,
        "mapped_records": 34546,
    }
    require(identity_sets == expected_identity_sets, "namespace identity-set/lineage evidence drift")

    table_crosswalk: dict[tuple[str, str], tuple[str, str]] = {}
    for row in tables["identity_crosswalks"]:
        payload = row["payload"]
        source_type = str(_required(payload, "source_record_type", "identity crosswalk"))
        source_id = str(payload.get("source_record_id", payload.get("source_id")))
        target_type = str(_required(payload, "target_record_type", f"identity crosswalk:{source_id}"))
        target_id = str(payload.get("target_record_id", payload.get("target_id")))
        key = (source_type, source_id)
        require(key not in table_crosswalk, f"duplicate identity-crosswalk source: {key}")
        require(payload.get("source_namespace") == owner_namespace and payload.get("target_namespace") == target_namespace, f"identity-crosswalk namespace drift: {key}")
        require(payload.get("owner_id_reminted", False) is False, f"identity-crosswalk owner remint: {key}")
        table_crosswalk[key] = (target_type, target_id)
    require(table_crosswalk == expected_owner, "identity-crosswalk table/owner namespace sidecar drift")
    return target_namespace


def _validate_translation_sidecar(
    translation: Mapping[str, Any],
    backend: Mapping[str, Any],
    units: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    coverage = translation["coverage"]
    require(coverage["course_id"] == ROLE_ID, "translation sidecar course drift")
    require(coverage["authority_rows"] == coverage["indexed_rows"] == 1993, "translation sidecar coverage drift")
    require(coverage["inferred_rows"] == 0 and translation["no_inference"] is True, "translation sidecar infers state")
    owner_units = _native_index(backend["units"], "units")
    records: dict[str, Mapping[str, Any]] = {}
    for record in translation["records"]:
        native_id = str(record["native_unit_id"])
        require(native_id not in records and native_id in owner_units, f"translation record identity drift: {native_id}")
        owner = owner_units[native_id]
        require(record["projected_unit_id"] == units[native_id]["id"], f"translation projected unit drift: {native_id}")
        require(record["state"] == owner["translation_state"] and record["locale"] == owner["locale"], f"translation state/locale drift: {native_id}")
        require(record.get("owner_record_sha256") == _owner_record_sha256(owner), f"translation owner hash drift: {native_id}")
        records[native_id] = record
    require(set(records) == set(owner_units), "one-to-one translation-state closure drift")
    require(Counter(row["state"] for row in records.values()) == EXPECTED_UNIT_TRANSLATION_STATES, "translation sidecar state distribution drift")
    require(translation["identity_set_sha256"] == identity_set_sha256(row["id"] for row in units.values()), "translation identity-set digest drift")
    return {"records": len(records), "states": dict(sorted(Counter(row["state"] for row in records.values()).items()))}


def _validate_capabilities_and_scope(
    capabilities: Mapping[str, Any],
    scope: Mapping[str, Any],
    owner_manifest_by_path: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    by_name = {str(row["name"]): row for row in capabilities["capabilities"]}
    require({name: row["state"] for name, row in by_name.items()} == EXPECTED_CAPABILITY_STATES, "C130 capability-state drift")
    for name, native_count in (("terminology", 268), ("assets", 346), ("corrections", 94)):
        row = by_name[name]
        require(row["native_count"] == native_count and row["projected_count"] == 0, f"referenced-only capability count drift: {name}")

    required_unprojected_shards = {
        "jsonl/programs.jsonl",
        "jsonl/courses.jsonl",
        "jsonl/resources.jsonl",
        "jsonl/concepts.jsonl",
        "jsonl/terms.jsonl",
        "jsonl/assets.jsonl",
        "jsonl/corrections.jsonl",
    }
    observed_shards: set[str] = set()
    for row in by_name.values():
        for fact in row.get("shard_refs", []):
            path = str(fact["path"])
            normalized = path.removeprefix("backend/dist/")
            if path == "backend/dist/backend-v0.json":
                native_fact = owner_manifest_by_path.get(normalized)
                require(native_fact is not None, "owner monolith absent from native manifest")
                require((fact["bytes"], fact["sha256"]) == (native_fact["bytes"], native_fact["sha256"]), "capability monolith fact drift")
                observed_shards |= required_unprojected_shards
            elif normalized in owner_manifest_by_path:
                native_fact = owner_manifest_by_path[normalized]
                require((fact["bytes"], fact["sha256"]) == (native_fact["bytes"], native_fact["sha256"]), f"capability shard fact drift: {path}")
                observed_shards.add(normalized)
            else:
                raise AdapterError(f"capability references an unknown native shard: {path}")
    require(required_unprojected_shards.issubset(observed_shards), "owner-native program/course/resource/concept/term/asset/correction shards silently dropped")

    capability_blob = _string_blob(capabilities)
    for phrase in ("aggregate-only", "names", "not reconciled", "provenance"):
        require(phrase in capability_blob, f"owner-generator limitation absent from capability loss/gap reports: {phrase}")
    require(LIMITATIONS_AUTHORITY_FACT[1] in capability_blob or LIMITATIONS_AUTHORITY_PATH.lower() in capability_blob, "capabilities do not bind native-pipeline limitations evidence")

    require(scope["curriculum_role_ids"] == [ROLE_ID] and scope["aggregate_conformance_claim"] is False, "C130 scope/aggregate claim drift")
    require(len(scope["course_ids"]) == 1, "C130 scope course cardinality drift")
    require(len(scope["unbound_curriculum_role_ids"]) == 39 and set(scope["unbound_curriculum_role_ids"]) == ALL_CURRICULUM_ROLES - {ROLE_ID}, "C130 unbound-role closure drift")
    scope_blob = _string_blob(scope)
    for phrase in ("prose", "native html", "anchor", "pdf/ua"):
        require(phrase in scope_blob, f"scope limitation missing: {phrase}")
    return {"states": EXPECTED_CAPABILITY_STATES, "unprojected_shards": len(required_unprojected_shards)}


def _validate_control_tables(
    tables: Mapping[str, list[dict[str, Any]]],
    backend: Mapping[str, Any],
) -> dict[str, Any]:
    authority_payload = tables["owner_authorities"][0]["payload"]
    require(_contains_exact_mapping(authority_payload, {
        "path": "backend/dist/backend-v0.json",
        "bytes": OWNER_AUTHORITY_FACTS["backend/dist/backend-v0.json"][0],
        "sha256": OWNER_AUTHORITY_FACTS["backend/dist/backend-v0.json"][1],
    }), "owner-authority table does not bind the native monolith")
    require(_contains_exact_mapping(authority_payload, OWNER_COUNTS), "owner-authority table omits exact native cardinalities")

    dataset_payload = tables["datasets"][0]["payload"]
    require(_contains_exact_mapping(dataset_payload, OWNER_COUNTS), "dataset table omits exact owner cardinalities")
    require(ROLE_ID.lower() in _string_blob(dataset_payload), "dataset is not bound to C130")

    profile = tables["adapter_profiles"][0]["payload"]
    require(ROLE_ID.lower() in _string_blob(profile), "adapter profile role drift")
    require(profile.get("zero_copy") is True, "adapter profile zero-copy state drift")
    require(profile.get("capability_map") == EXPECTED_CAPABILITY_STATES, "adapter profile capability map drift")
    require(profile.get("owner_native_unit_count") == 1993 and profile.get("owner_native_segment_count") == 5525, "adapter profile owner cardinality drift")

    run_row = tables["adapter_runs"][0]
    run = run_row["payload"]
    require(_contains_exact_mapping(run, EXPECTED_TABLE_COUNTS), "adapter run omits exact table counts")
    require(run_row["owner_native_state"] == "pass", "adapter run is not pass")
    run_blob = _string_blob(run)
    require(CURRENT_RELEASE_REPORT_SHA256 in run_blob and STALE_RELEASE_REPORT_SHA256 in run_blob and "stale" in run_blob, "adapter run silently treats stale release-report cursor as current")

    require(tables["build_recipes"] == [], "C130 adapter invents a common build recipe")
    return {"owner_authorities": 1, "datasets": 1, "profiles": 1, "runs": 1, "build_recipes": 0}


def _validate_no_claim_leaks(
    package: Path,
    tables: Mapping[str, list[dict[str, Any]]],
    sidecars: Iterable[Mapping[str, Any]],
) -> None:
    for table_name in TABLE_ORDER:
        for row in tables[table_name]:
            payload = row["payload"]
            if table_name not in {"rights", "artifacts", "qa_events"}:
                _assert_no_prose_fields(payload, f"{table_name}:{row['id']}")
            blob = _string_blob(payload)
            if STALE_RELEASE_REPORT_SHA256 in blob:
                require("stale" in blob, f"stale release-report digest presented without disclosure: {table_name}:{row['id']}")
            for key in ("pdf_ua_verified", "pdf_ua_claimed"):
                for item in _walk_mappings(payload):
                    require(item.get(key, False) is False, f"PDF/UA claim leaked: {table_name}:{row['id']}:{key}")
            for item in _walk_mappings(payload):
                require(item.get("pdf_ua_conformance") in (None, False, "none", "not_claimed"), f"PDF/UA conformance leaked: {table_name}:{row['id']}")

    for sidecar in sidecars:
        for item in _walk_mappings(sidecar):
            require(item.get("pdf_ua_verified", False) is False and item.get("pdf_ua_claimed", False) is False, "PDF/UA claim leaked into sidecar")
            require(item.get("pdf_ua_conformance") in (None, False, "none", "not_claimed"), "PDF/UA conformance leaked into sidecar")

    manifest = read_json(package / "manifest.json")
    forbidden_suffixes = {".pdf", ".html", ".htm", ".tex", ".qmd"}
    for fact in manifest["files"]:
        path = str(fact["path"]).lower()
        require(Path(path).suffix not in forbidden_suffixes, f"owner prose/reader bytes centralized in package: {path}")
        require(not path.endswith("backend-v0.json") and "/jsonl/segments.jsonl" not in path, f"owner prose monolith/shard centralized in package: {path}")


def _discover_repository_root(package: Path) -> Path | None:
    """Find only the exact limitations authority by bounded ancestor ascent."""

    seen: set[Path] = set()
    for start in (Path(__file__).resolve().parent, package.resolve()):
        for candidate in (start, *start.parents):
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate.joinpath(*PurePosixPath(LIMITATIONS_AUTHORITY_PATH).parts).is_file():
                return candidate
    return None


def validate_c130_semantics(
    package: Path,
    owner_package_root: Path | None = None,
    repository_root: Path | None = None,
    require_authorities: bool = False,
) -> dict[str, Any]:
    """Replay exact C130 owner authority and validate the package semantics."""

    package = package.resolve()
    require(package.is_dir(), f"package directory missing: {package}")
    require(owner_package_root is not None, "--owner-package-root is required for fail-closed C130 semantic replay")
    if repository_root is None:
        repository_root = _discover_repository_root(package)
    require(repository_root is not None, "repository root could not be established for the native-pipeline limitations authority")
    owner_root = owner_package_root.resolve()
    repo_root = repository_root.resolve()
    require(owner_root.is_dir(), f"owner package root missing: {owner_root}")
    require(repo_root.is_dir(), f"repository root missing: {repo_root}")

    manifest = read_json(package / "manifest.json")
    owner = _load_and_validate_owner(owner_root)
    authority_report = _validate_input_authorities(package, manifest, owner_root, repo_root)
    tables = {name: read_jsonl(package / "tables" / f"{name}.jsonl") for name in TABLE_ORDER}
    observed_counts = {name: len(rows) for name, rows in tables.items()}
    require(observed_counts == EXPECTED_TABLE_COUNTS, f"C130 table counts drift: {observed_counts}")

    scope = read_json(package / "scope-declaration-v0.2.0.json")
    namespace = read_json(package / "namespace-crosswalk-v0.2.0.json")
    translation = read_json(package / "translation-state-index-v0.2.0.json")
    capabilities = read_json(package / "capability-declarations-v0.2.0.json")
    rights_closure = read_json(package / "rights-assignment-closure-v0.1.0.json")
    csv_manifest = read_json(package / "csv-projection-manifest-v0.2.0.json")

    units, _ = _validate_unit_cluster(tables, owner["backend"])
    segment_bindings, _ = _validate_segments(tables, owner["backend"], units)
    artifacts, owner_qa, adapter_qa = _validate_artifacts_and_qa(tables, owner["backend"])
    relations, rights = _validate_relations_and_rights(tables, owner["backend"], units, segment_bindings, artifacts)
    editions = _verify_direct_projection(tables["editions"], owner["backend"]["editions"], "editions")

    direct = {
        "editions": editions,
        "units": units,
        "segments": segment_bindings,
        "relations": relations,
        "rights": rights,
        "artifacts": artifacts,
        "qa_events": owner_qa,
    }
    lane_namespace = _validate_namespace_and_crosswalk(tables, namespace, direct, owner["backend"])
    _validate_projection_ids(tables, lane_namespace)
    translation_report = _validate_translation_sidecar(translation, owner["backend"], units)
    capability_report = _validate_capabilities_and_scope(capabilities, scope, owner["backend_manifest_by_path"])
    rights_closure_report = _validate_rights_assignment_closure_sidecar(
        package, manifest, rights_closure, capabilities, owner["backend"], rights
    )
    route_report = _validate_routes_and_surfaces(tables)
    control_report = _validate_control_tables(tables, owner["backend"])

    require(csv_manifest["table_order"] == TABLE_ORDER, "CSV sidecar table order drift")
    csv_counts = {entry["table"]: entry["records"] for entry in csv_manifest["tables"]}
    require(csv_counts == EXPECTED_TABLE_COUNTS, "CSV sidecar C130 table cardinalities drift")
    require(csv_manifest["records_csv"]["records"] == sum(EXPECTED_TABLE_COUNTS.values()), "CSV sidecar aggregate record count drift")
    _validate_no_claim_leaks(package, tables, (scope, namespace, translation, capabilities, rights_closure, csv_manifest))

    return {
        "status": "PASS",
        "authority": {
            **authority_report,
            "owner_backend_files": 32,
            "owner_backend_counts": OWNER_COUNTS,
            "owner_backend_sha256": OWNER_AUTHORITY_FACTS["backend/dist/backend-v0.json"][1],
        },
        "table_counts": observed_counts,
        "units": len(units),
        "native_segment_bindings": len(segment_bindings),
        "typed_relations": len(relations),
        "relation_types": EXPECTED_RELATION_TYPES,
        "rights": len(rights),
        "rights_assignments": len(tables["rights_assignments"]),
        "rights_assignment_closure": rights_closure_report,
        "owner_artifacts": len(artifacts),
        "owner_qa_provenance_rows": len(owner_qa),
        "adapter_build_qa_rows": 1 if adapter_qa else 0,
        "identity_crosswalks": len(tables["identity_crosswalks"]),
        "translation": translation_report,
        "capabilities": capability_report,
        "learner_routes": route_report,
        "control_tables": control_report,
        "full_prose_centralized": False,
        "native_chapter_html_claimed": False,
        "unit_or_page_anchors_claimed": False,
        "pdf_ua_claimed": False,
        "stale_owner_cursor_treated_current": False,
        "require_authorities_requested": require_authorities,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--require-authorities", action="store_true")
    parser.add_argument("--build-a", type=Path)
    parser.add_argument("--build-b", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        generic = validate_package(SimpleNamespace(
            package=args.package,
            repository_root=args.repository_root,
            owner_package_root=args.owner_package_root,
            require_authorities=args.require_authorities,
            build_a=args.build_a,
            build_b=args.build_b,
        ))
        semantic = validate_c130_semantics(
            args.package,
            owner_package_root=args.owner_package_root,
            repository_root=args.repository_root,
            require_authorities=args.require_authorities,
        )
        report = {
            "schema_id": "program-matematika-indonesia/c130-operations-research-v231-validation/1.0.0",
            "status": "PASS",
            "recorded_at": RECORDED_AT,
            "package": {
                "manifest_bytes": (args.package / "manifest.json").stat().st_size,
                "manifest_sha256": sha256_file(args.package / "manifest.json"),
            },
            "generic": generic,
            "c130_semantics": semantic,
        }
        if args.report:
            write_json(args.report, report)
        print(compact_json(report))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
