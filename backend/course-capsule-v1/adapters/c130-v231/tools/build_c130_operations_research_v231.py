#!/usr/bin/env python3
"""Build the deterministic zero-prose C130 operations-research v2.3.1 adapter."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    TABLE_ORDER,
    compact_json,
    empty_tables,
    external_file_fact,
    file_fact,
    identity_set_sha256,
    inventory_sha256,
    make_row,
    mapping_set_sha256,
    package_payload_files,
    parse_checksum_file,
    projection_id,
    read_json,
    read_jsonl,
    require,
    sha256_bytes,
    sha256_file,
    sort_table_rows,
    write_csv_surfaces,
    write_json,
    write_tables,
)


RECORDED_AT = "2026-08-31T00:00:00Z"
ADAPTER_VERSION = "0.1.0"
LANE_NAMESPACE = uuid.UUID("4ed39c18-4c79-5b53-aecf-8369dba64a02")
PREVIOUS_COMMON_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
OWNER_NAMESPACE = "open-optimization-or-book-id/backend-v0/2026-08-23"
COURSE_ROLE = "C130"
COURSE_TITLE = "Pemrograman Matematis dan Riset Operasi — Buku 1"

PRIOR_V1_DIRECT_TYPES = {
    "artifacts": "artifact",
    "assets": "asset",
    "concepts": "concept",
    "corrections": "correction",
    "courses": "course",
    "editions": "edition",
    "programs": "program",
    "qa_events": "qa_event",
    "relations": "relation",
    "resources": "resource",
    "rights": "rights",
    "segments": "segment",
    "terms": "term",
    "units": "unit",
}
PRIOR_V1_MAPPING_BYTES = 2_231_498
PRIOR_V1_MAPPING_SHA256 = "7eab936794df7157467b646f97519889a1c6fdeb6b4222e1ecb1d1df9a8ee51a"

OWNER_COUNTS = {
    "programs": 1,
    "courses": 1,
    "resources": 4,
    "editions": 5,
    "units": 1993,
    "segments": 5525,
    "concepts": 128,
    "terms": 140,
    "assets": 346,
    "rights": 21,
    "corrections": 94,
    "qa_events": 101,
    "artifacts": 83,
    "relations": 9545,
}

RELATION_TYPE_COUNTS = {
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

SEGMENT_STATE_COUNTS = {
    "source_frozen": 339,
    "translated": 2293,
    "structurally_verified": 2893,
}

SEGMENT_RELATIONSHIP_COUNTS = {
    "locally_authored_adaptation": 339,
    "translation": 2293,
    "target_native_correction": 9,
    "translation_target_projection": 2884,
}

ALL_ROLES = [
    "A00", "A10", "A20", "A30", "B10", "B20", "B30", "B40", "B50",
    "B60", "B70", "B80", "B90", "B95", "C10", "C20", "C30", "C40",
    "C50", "C60", "C70", "C80", "C90", "C100", "C110", "C120",
    "C130", "C140", "D10", "D20", "D30", "D40", "D50", "D60",
    "D70", "D80", "D90", "D100", "D110", "D120",
]

OWNER_AUTHORITIES = {
    "backend": ("backend/dist/backend-v0.json", 26022240, "7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804", "owner_backend_monolith"),
    "backend_manifest": ("backend/dist/manifest.json", 4853, "f800590f07fafa47c7eb900dddc8cf99bbf5cb892218fa4ab1722677b7b2efa4", "owner_backend_manifest"),
    "backend_checksums": ("backend/dist/SHA256SUMS.txt", 2623, "1dabfdb58c910fc5c1e659356361c51056c6084a214f7b20583a42e9750e6515", "owner_backend_checksums"),
    "cursor": ("00_control/CURRENT_CURSOR.json", 5676, "a79969903d29a26872c78d1dd573aabdeefff9c08720e7a99dc5b7d8f0499f1c", "owner_cursor"),
    "release_report": ("qa/release-package-report.json", 5130, "ae2e905782c099db7d1c177255fbbc6f07146caa2c3cacf2293498cdac3b308f", "live_release_report"),
    "release_manifest": ("release/out/RELEASE-MANIFEST.json", 4773, "c0bfe88be28ce19bd730e69fd3bc0ed88b73f076e3d7a1b61b205cbb4a96f376", "owner_release_manifest"),
    "release_checksums": ("release/out/SHA256SUMS.txt", 1200, "d582ad7eca87ca91687c7f278b7ee7ac1603cc724bf8c4b95bb53bd93262e32d", "owner_release_checksums"),
    "zenodo_receipt": ("release/receipts/zenodo-publication-receipt-2026.08.23-id.5.json", 5197, "3e20d2459f42824e57df29bd0937e2f526d9349da7d941c65cf7dcec3739feab", "zenodo_publication_receipt"),
    "github_receipt": ("release/receipts/github-publication-receipt.json", 239332, "b888b35ab940f1418b4c74c1da06548bb4fedf8e5079240368608eec605cccf8", "github_publication_receipt"),
    "github_plan": ("qa/github-publication-plan.json", 158378, "288013dc2c0565d4eac070834e5462efc5b5c2747604d83fef4f6f3bb56e617a", "github_publication_plan"),
}

PROGRAM_AUTHORITIES = {
    "registry_overlay": (
        "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/198_FULL_LIVE_OWNER_REGISTRY_AUTHORITY_CORRECTION_20260831.json",
        32625,
        "69b853222d77ecd0873e832a00c74bffaa8cc11d5f6c1490138135a7f89e7fee",
        "curriculum_registry_overlay",
    ),
    "capability_contract": (
        "04_mirrors/id/program-matematika-indonesia-v06213/backend/v2.2/global-capability-contract-v0.1.0.json",
        7462,
        "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7",
        "capability_contract",
    ),
    "native_pipeline_limitations": (
        "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/c130_operations_research_v231_candidate/research/C130_NATIVE_PIPELINE_LIMITATIONS_20260831.md",
        3720,
        "e73edc9413411b1594a07f646cc11011853d9548a87a28f7b1985aa8f74b99c0",
        "native_pipeline_limitations",
    ),
    "prior_v1_migration_receipt": (
        "04_mirrors/id/program-matematika-indonesia-v06213/releases/v0.62.13/o018-c130-id-backend-v1-migration-receipt.json",
        22647,
        "cd591df3833862551d5bbcdcfa6a1c6f22414504110b1e9fae38162dedc1ca5f",
        "prior_v1_migration_receipt",
    ),
}

OWNER_ENVELOPE_KEYS = {
    "id", "recorded_at", "responsible_workflow", "schema_name", "schema_version",
    "status", "supersedes_id",
}


def owner_record_sha256(row: Mapping[str, Any]) -> str:
    return sha256_bytes(compact_json(row).encode("utf-8"))


def owner_metadata(row: Mapping[str, Any], *, omitted: set[str] | None = None) -> dict[str, Any]:
    excluded = OWNER_ENVELOPE_KEYS | (omitted or set())
    return {key: copy.deepcopy(value) for key, value in row.items() if key not in excluded}


def direct_owner_payload(
    row: Mapping[str, Any],
    collection: str,
    *,
    omitted: set[str] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "native_id": row["id"],
        "native_collection": collection,
        "owner_record_sha256": owner_record_sha256(row),
        "native_metadata": owner_metadata(row, omitted=omitted),
    }
    if extra:
        payload.update(copy.deepcopy(dict(extra)))
    return payload


def native_id_set(rows: Iterable[Mapping[str, Any]]) -> str:
    return identity_set_sha256(str(row["id"]) for row in rows)


def prior_v1_identity_facts(backend: Mapping[str, Any]) -> dict[str, Any]:
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
    require(len(mapping_payload) == PRIOR_V1_MAPPING_BYTES, "prior-v1 mapping payload byte drift")
    require(sha256_bytes(mapping_payload) == PRIOR_V1_MAPPING_SHA256, "prior-v1 mapping payload hash drift")
    return {
        "native_table_by_id": native_table_by_id,
        "prior_id_by_native_id": prior_id_by_native_id,
        "mapping_payload_bytes": len(mapping_payload),
        "mapping_payload_sha256": sha256_bytes(mapping_payload),
        "all_prior_ids_sha256": identity_set_sha256(prior_id_by_native_id.values()),
        "native_to_prior_pairs_sha256": mapping_set_sha256(prior_id_by_native_id.items()),
    }


def native_rights_references(collection: str, row: Mapping[str, Any]) -> list[dict[str, Any]]:
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
    reference_keys = [(ref["source_field"], ref["source_ordinal"], ref["native_rights_id"]) for ref in refs]
    require(len(reference_keys) == len(set(reference_keys)), f"duplicate rights reference: {collection}:{row['id']}")
    return refs


def derive_owner_rights_assignments(backend: Mapping[str, Any]) -> list[dict[str, Any]]:
    collections = ("units", "segments", "artifacts", "resources", "assets")
    rows: list[dict[str, Any]] = []
    for collection in collections:
        for row in backend[collection]:
            for ref in native_rights_references(collection, row):
                rows.append({
                    "owner_collection": collection,
                    "native_target_id": str(row["id"]),
                    **ref,
                })
    return rows


def rights_assignment_identity(row: Mapping[str, Any]) -> str:
    return "\0".join((
        str(row["owner_collection"]),
        str(row["native_target_id"]),
        str(row["source_field"]),
        f"{int(row['source_ordinal']):04d}",
        str(row["assignment_role"]),
        str(row["native_rights_id"]),
    ))


def owner_rights_assignment_facts(backend: Mapping[str, Any]) -> dict[str, Any]:
    rows = derive_owner_rights_assignments(backend)
    counts = dict(sorted(Counter(row["owner_collection"] for row in rows).items()))
    materialized = [row for row in rows if row["owner_collection"] in {"units", "segments", "artifacts"}]
    referenced_only = [row for row in rows if row["owner_collection"] in {"resources", "assets"}]
    require(counts == {"units": 2039, "segments": 5525, "artifacts": 70, "resources": 9, "assets": 346}, "owner rights-assignment distribution drift")
    require(len(rows) == 7_989 and len(materialized) == 7_634 and len(referenced_only) == 355, "owner rights-assignment closure drift")
    return {
        "by_collection": counts,
        "total": len(rows),
        "materialized_total": len(materialized),
        "referenced_only_total": len(referenced_only),
        "identity_set_sha256": identity_set_sha256(rights_assignment_identity(row) for row in rows),
        "materialized_identity_set_sha256": identity_set_sha256(rights_assignment_identity(row) for row in materialized),
        "referenced_only_identity_set_sha256": identity_set_sha256(rights_assignment_identity(row) for row in referenced_only),
    }


def public_url(filename: str) -> str:
    return "https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/" + filename


def build_authorities(repository_root: Path, owner_root: Path) -> dict[str, dict[str, Any]]:
    authorities: dict[str, dict[str, Any]] = {}
    for key, (relative, size, digest, role) in OWNER_AUTHORITIES.items():
        authorities[key] = external_file_fact(
            owner_root / Path(relative), relative, role, "owner_package_root",
            expected_bytes=size, expected_sha256=digest,
        )
    for key, (relative, size, digest, role) in PROGRAM_AUTHORITIES.items():
        authorities[key] = external_file_fact(
            repository_root / Path(relative), relative, role, "program_repository_root",
            expected_bytes=size, expected_sha256=digest,
        )
    return authorities


def verify_owner_backend(owner_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    dist = owner_root / "backend" / "dist"
    backend = read_json(dist / "backend-v0.json")
    for name, count in OWNER_COUNTS.items():
        require(isinstance(backend.get(name), list), f"owner collection missing: {name}")
        require(len(backend[name]) == count, f"owner count drift: {name}")
        ids = [str(row["id"]) for row in backend[name]]
        require(len(ids) == len(set(ids)), f"duplicate owner IDs: {name}")
        if (dist / "jsonl" / f"{name}.jsonl").is_file():
            require(read_jsonl(dist / "jsonl" / f"{name}.jsonl") == backend[name], f"owner JSONL/monolith drift: {name}")

    require(Counter(row["relation_type"] for row in backend["relations"]) == Counter(RELATION_TYPE_COUNTS), "owner relation-type drift")
    require(Counter(row["translation_state"] for row in backend["segments"]) == Counter(SEGMENT_STATE_COUNTS), "owner segment-state drift")
    require(Counter(row["source_target_relationship"] for row in backend["segments"]) == Counter(SEGMENT_RELATIONSHIP_COUNTS), "owner segment-relationship drift")
    require(Counter(row["locale"] for row in backend["units"]) == Counter({"id-ID": 1205, "mul": 788}), "owner unit-locale drift")

    manifest = read_json(dist / "manifest.json")
    manifest_paths = [str(row["path"]) for row in manifest["artifacts"]]
    require(len(manifest_paths) == 30 and len(manifest_paths) == len(set(manifest_paths)), "owner manifest inventory drift")
    for fact in manifest["artifacts"]:
        path = dist / Path(str(fact["path"]))
        require(path.is_file(), f"owner manifest target missing: {fact['path']}")
        require(path.stat().st_size == int(fact["bytes"]), f"owner manifest byte drift: {fact['path']}")
        require(sha256_file(path) == fact["sha256"], f"owner manifest hash drift: {fact['path']}")
    checksum_rows = parse_checksum_file(dist / "SHA256SUMS.txt")
    require({relative for _, relative in checksum_rows} == set(manifest_paths) | {"manifest.json"}, "owner checksum closure drift")
    for digest, relative in checksum_rows:
        require(sha256_file(dist / Path(relative)) == digest, f"owner checksum mismatch: {relative}")

    release = read_json(owner_root / "release" / "out" / "RELEASE-MANIFEST.json")
    cursor = read_json(owner_root / "00_control" / "CURRENT_CURSOR.json")
    zenodo = read_json(owner_root / "release" / "receipts" / "zenodo-publication-receipt-2026.08.23-id.5.json")
    require(release["canonical_pdf"] == {
        "bytes": 26425739,
        "pages": 666,
        "path": "output/book1-pdf/book1-id.pdf",
        "qa_report": "qa/book1-final-qa-report.json",
        "qa_report_sha256": "d914ab157350571779a9e4bca62a1b02031560ccda19f00b08c4d61fda5b15b0",
        "sha256": "daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49",
    }, "canonical PDF identity drift")
    require(release["accessibility"]["pdf_ua_claim"] is False and release["accessibility"]["tagged_pdf"] is False, "PDF accessibility claim drift")
    require(cursor["translation_cursor"]["complete"] is True and not cursor["translation_cursor"]["remaining_translation"], "owner translation is not complete")
    require(zenodo["status"] == "published_and_anonymously_verified" and zenodo["file_count"] == 13, "Zenodo public evidence drift")
    require(all(row["anonymous_readback"] for row in zenodo["files"]), "Zenodo anonymous readback drift")
    return backend, manifest, release, cursor


def copy_static_inputs(output: Path) -> dict[str, dict[str, Any]]:
    source_root = Path(__file__).resolve().parent
    candidate_root = source_root.parent
    schema_root = candidate_root / "schema"
    output.mkdir(parents=True, exist_ok=False)
    (output / "schema").mkdir()
    (output / "tools").mkdir()
    (output / "evidence").mkdir()
    schema_names = [
        "lane-adapter-v2.3.1.schema.json",
        "capability-declarations-v0.2.schema.json",
        "namespace-crosswalk-v0.2.schema.json",
        "translation-state-index-v0.2.schema.json",
        "csv-projection-manifest-v0.2.schema.json",
        "scope-declaration-v0.2.schema.json",
    ]
    tool_names = [
        "build_c130_operations_research_v231.py",
        "validate_c130_operations_research_v231.py",
        "run_c130_negative_probes.py",
        "validate_lane_adapter_v231.py",
        "v231_adapter_common.py",
        "package_lane_adapter_v231.py",
    ]
    for name in schema_names:
        require((schema_root / name).is_file(), f"required schema missing: {name}")
        shutil.copyfile(schema_root / name, output / "schema" / name)
    for name in tool_names:
        require((source_root / name).is_file(), f"required tool missing: {name}")
        shutil.copyfile(source_root / name, output / "tools" / name)
    shutil.copyfile(candidate_root / "WORKFLOW.md", output / "WORKFLOW.md")
    evidence_names = [
        "C130_NATIVE_AUTHORITY_AUDIT_20260831.md",
        "C130_NATIVE_PIPELINE_LIMITATIONS_20260831.md",
    ]
    facts: dict[str, dict[str, Any]] = {}
    for name in evidence_names:
        source = candidate_root / "research" / name
        require(source.is_file(), f"required research evidence missing: {name}")
        target = output / "evidence" / name
        shutil.copyfile(source, target)
        facts[name] = file_fact(target, f"evidence/{name}", "adapter_research_evidence")
    return facts


def build_tables(
    backend: Mapping[str, Any],
    release: Mapping[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    package_id = projection_id(LANE_NAMESPACE, "package", "c130-operations-research-v231:0.1.0")
    dataset_id = projection_id(LANE_NAMESPACE, "dataset", "course:C130")
    owner_id = projection_id(LANE_NAMESPACE, "owner_authority", "open-optimization-or-book-id")
    extension_id = projection_id(LANE_NAMESPACE, "lane_adapter_extension", "c130-operations-research:0.1.0")
    tables = empty_tables()

    def add(
        table: str,
        record_type: str,
        semantic_key: str,
        payload: Mapping[str, Any],
        *,
        normalized_state: str = "validated",
        owner_native_state: str | None = None,
    ) -> dict[str, Any]:
        row = make_row(
            LANE_NAMESPACE,
            record_type,
            semantic_key,
            payload,
            dataset_id=dataset_id,
            owner_authority_id=owner_id,
            recorded_at=RECORDED_AT,
            normalized_state=normalized_state,
            owner_native_state=owner_native_state,
        )
        tables[table].append(row)
        return row

    add(
        "owner_authorities",
        "owner_authority",
        "owner:open-optimization-or-book-id",
        {
            "authority_kind": "external_owner_native_backend",
            "course_role": COURSE_ROLE,
            "owner_backend": {
                "path": "backend/dist/backend-v0.json",
                "bytes": 26022240,
                "sha256": "7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804",
            },
            "owner_counts": OWNER_COUNTS,
            "repository": "https://github.com/KokunoYumeto/open-optimization-or-book-id",
            "pages": "https://kokunoyumeto.github.io/open-optimization-or-book-id/",
            "version_doi": "10.5281/zenodo.22070653",
            "concept_doi": "10.5281/zenodo.22059794",
            "owner_native_authoritative": True,
            "owner_tree_mutated": False,
        },
        normalized_state="external_authority",
        owner_native_state="complete_public",
    )
    dataset_row = add(
        "datasets",
        "dataset",
        "course:C130",
        {
            "course_id": COURSE_ROLE,
            "title": COURSE_TITLE,
            "locale": "id-ID",
            "corpus_scope": "R017 Book 1 plus separately attributed O018 Pyomo+HiGHS adaptation",
            "explicit_exclusions": ["R017 Book 2", "advanced optimization"],
            "zero_copy": True,
            "machine_surfaces_secondary": True,
            "owner_counts": OWNER_COUNTS,
        },
        normalized_state="complete_public_owner_projection",
        owner_native_state="complete",
    )
    require(dataset_row["id"] == dataset_id, "dataset identity drift")

    direct_maps: dict[str, dict[str, str]] = {
        "edition": {},
        "unit": {},
        "segment": {},
        "relation": {},
        "rights": {},
        "artifact": {},
        "qa_event": {},
    }
    mapping_specs: list[dict[str, str]] = []

    def register(kind: str, native_id: str, target_type: str, target_id: str) -> None:
        require(native_id not in direct_maps[kind], f"duplicate direct map: {kind}:{native_id}")
        direct_maps[kind][native_id] = target_id
        mapping_specs.append({
            "source_record_type": "right" if kind == "rights" else kind,
            "source_record_id": native_id,
            "target_record_type": target_type,
            "target_record_id": target_id,
        })

    for native in backend["editions"]:
        row = add(
            "editions",
            "edition",
            f"owner-edition:{native['id']}",
            direct_owner_payload(native, "editions"),
            normalized_state="projected_owner_native",
            owner_native_state=native.get("status"),
        )
        register("edition", native["id"], "edition", row["id"])

    projected_unit_ids = {
        native["id"]: projection_id(LANE_NAMESPACE, "unit", f"owner-unit:{native['id']}")
        for native in backend["units"]
    }
    for ordinal, native in enumerate(backend["units"], start=1):
        unit_payload = direct_owner_payload(
            native,
            "units",
            extra={
                "projected_edition_id": direct_maps["edition"].get(str(native.get("edition_id"))),
                "projected_parent_id": projected_unit_ids.get(str(native.get("parent_id"))),
            },
        )
        row = add(
            "units",
            "unit",
            f"owner-unit:{native['id']}",
            unit_payload,
            normalized_state="projected_zero_copy",
            owner_native_state=native.get("status"),
        )
        require(row["id"] == projected_unit_ids[native["id"]], "unit precomputed identity drift")
        register("unit", native["id"], "unit", row["id"])
        add(
            "course_unit_memberships",
            "course_unit_membership",
            f"C130:{native['id']}",
            {
                "course_id": COURSE_ROLE,
                "curriculum_role_id": COURSE_ROLE,
                "projected_unit_id": row["id"],
                "native_unit_id": native["id"],
                "parent_projected_unit_id": projected_unit_ids.get(str(native.get("parent_id"))),
                "ordinal": ordinal,
                "order": native.get("order"),
                "topology_order_path": native.get("topology_order_path"),
            },
            normalized_state="materialized_membership",
            owner_native_state=native.get("status"),
        )
        title = native.get("title_target") or native.get("title_source") or native["id"]
        add(
            "search_documents",
            "search_document",
            f"unit-search:{native['id']}",
            {
                "course_id": COURSE_ROLE,
                "projected_unit_id": row["id"],
                "native_unit_id": native["id"],
                "locale": native.get("locale"),
                "unit_type": native.get("unit_type"),
                "title": title,
                "search_text": title,
                "learner_url": "https://kokunoyumeto.github.io/open-optimization-or-book-id/",
                "body_text_included": False,
            },
            normalized_state="bounded_title_index",
            owner_native_state=native.get("status"),
        )

    for native in backend["segments"]:
        metadata = direct_owner_payload(
            native,
            "segments",
            omitted={"source_text", "target_text"},
            extra={
                "native_record_type": "segment",
                "native_unit_id": native.get("unit_id"),
                "projected_unit_id": projected_unit_ids.get(str(native.get("unit_id"))),
                "full_prose_centralized": False,
            },
        )
        native_row = add(
            "native_bindings",
            "native_binding",
            f"owner-segment:{native['id']}",
            metadata,
            normalized_state="referenced_native_shard",
            owner_native_state=native.get("status"),
        )
        register("segment", native["id"], "native_binding", native_row["id"])
        add(
            "content_bindings",
            "content_binding",
            f"owner-segment-content:{native['id']}",
            direct_owner_payload(
                native,
                "segments",
                omitted={"source_text", "target_text"},
                extra={
                "native_binding_id": native_row["id"],
                "native_unit_id": native.get("unit_id"),
                "projected_unit_id": projected_unit_ids.get(str(native.get("unit_id"))),
                "translation_state": native.get("translation_state"),
                "source_target_relationship": native.get("source_target_relationship"),
                "content_included_in_adapter": False,
                "full_text_included": False,
                "full_prose_centralized": False,
                "source_text_present": False,
                "target_text_present": False,
                },
            ),
            normalized_state="hash_bound_zero_copy",
            owner_native_state=native.get("status"),
        )

    for native in backend["relations"]:
        row = add(
            "relations",
            "relation",
            f"owner-relation:{native['id']}",
            direct_owner_payload(native, "relations", extra={
                "relation_type": native["relation_type"],
                "from_owner_native_id": native["from_id"],
                "to_owner_native_id": native["to_id"],
                "owner_evidenced": True,
                "conceptually_inferred": False,
            }),
            normalized_state="projected_owner_relation",
            owner_native_state=native.get("status"),
        )
        register("relation", native["id"], "relation", row["id"])

    for native in backend["rights"]:
        row = add(
            "rights",
            "rights",
            f"owner-rights:{native['id']}",
            direct_owner_payload(native, "rights"),
            normalized_state="projected_component_rights",
            owner_native_state=native.get("status"),
        )
        register("rights", native["id"], "rights", row["id"])

    rights_assignments = 0
    for native in backend["units"]:
        for ref in native_rights_references("units", native):
            rights_native_id = ref["native_rights_id"]
            require(rights_native_id in direct_maps["rights"], f"unit rights target missing: {rights_native_id}")
            add(
                "rights_assignments",
                "rights_assignment",
                f"unit:{native['id']}:{ref['source_field']}:{ref['source_ordinal']}:{rights_native_id}",
                {
                    "native_target_id": native["id"],
                    "native_rights_id": rights_native_id,
                    "assignment_role": ref["assignment_role"],
                    "source_field": ref["source_field"],
                    "source_ordinal": ref["source_ordinal"],
                    "target_id": projected_unit_ids[native["id"]],
                    "rights_id": direct_maps["rights"][rights_native_id],
                    "target_record_type": "unit",
                },
                normalized_state="projected_rights_assignment",
                owner_native_state=native.get("status"),
            )
            rights_assignments += 1
    for native in backend["segments"]:
        refs = native_rights_references("segments", native)
        require(len(refs) == 1, f"segment rights field cardinality drift: {native['id']}")
        ref = refs[0]
        rights_native_id = ref["native_rights_id"]
        require(rights_native_id in direct_maps["rights"], f"segment rights target missing: {rights_native_id}")
        add(
            "rights_assignments",
            "rights_assignment",
            f"segment:{native['id']}:{rights_native_id}",
            {
                "native_target_id": native["id"],
                "native_rights_id": rights_native_id,
                "assignment_role": ref["assignment_role"],
                "source_field": ref["source_field"],
                "source_ordinal": ref["source_ordinal"],
                "target_id": direct_maps["segment"][native["id"]],
                "rights_id": direct_maps["rights"][rights_native_id],
                "target_record_type": "native_binding",
            },
            normalized_state="projected_rights_assignment",
            owner_native_state=native.get("status"),
        )
        rights_assignments += 1
    release_files = {
        item["file_name"]: item for item in list(release["artifacts"]) + list(release["supporting_files"])
    }
    for native in backend["artifacts"]:
        basename = Path(str(native.get("path") or "")).name
        payload = direct_owner_payload(native, "artifacts")
        if basename in release_files:
            payload["public_release_member"] = release_files[basename]
            payload["public_url"] = public_url(basename)
        row = add(
            "artifacts",
            "artifact",
            f"owner-artifact:{native['id']}",
            payload,
            normalized_state="referenced_native_artifact",
            owner_native_state=native.get("status"),
        )
        register("artifact", native["id"], "artifact", row["id"])

    for native in backend["artifacts"]:
        for ref in native_rights_references("artifacts", native):
            rights_native_id = ref["native_rights_id"]
            require(rights_native_id in direct_maps["rights"], f"artifact rights target missing: {rights_native_id}")
            add(
                "rights_assignments",
                "rights_assignment",
                f"artifact:{native['id']}:{ref['source_field']}:{ref['source_ordinal']}:{rights_native_id}",
                {
                    "native_target_id": native["id"],
                    "native_rights_id": rights_native_id,
                    "assignment_role": ref["assignment_role"],
                    "source_field": ref["source_field"],
                    "source_ordinal": ref["source_ordinal"],
                    "target_id": direct_maps["artifact"][native["id"]],
                    "rights_id": direct_maps["rights"][rights_native_id],
                    "target_record_type": "artifact",
                },
                normalized_state="projected_rights_assignment",
                owner_native_state=native.get("status"),
            )
            rights_assignments += 1
    require(rights_assignments == 7634, "projected rights-assignment closure drift")

    route_definitions = [
        ("learner-landing", "pages_learner_landing", "https://kokunoyumeto.github.io/open-optimization-or-book-id/", 1, False),
        ("linked-pdf", "linked_pdf", public_url("pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf"), 2, False),
        ("repository", "source_repository", "https://github.com/KokunoYumeto/open-optimization-or-book-id", 3, False),
        ("zenodo-record", "zenodo_preservation_record", "https://zenodo.org/records/22070653", 4, False),
        ("source-archive", "editable_source_download", public_url("pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip"), 5, True),
        ("labs-archive", "computational_labs_download", public_url("pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip"), 6, True),
        ("backend-archive", "owner_backend_download", public_url("pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip"), 7, True),
    ]
    route_ids: dict[str, str] = {}
    public_downloads = {
        "pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf": (26425739, "daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49"),
        "pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip": (20087323, "55d62c53401938eb5dbc12d3f4116ce68181bd90c9f94fda1434fe20f5196914"),
        "pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip": (527596, "99628dcdd4984c8a3b763862dc88b06bca8bf15d47dbf1db863cfe46b2a1e592"),
        "pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip": (6535806, "7cd76333b3433518f4d983d6775412aba9fd99e1f6b9a35a89528e6994830c56"),
    }
    for key, route_kind, url, priority, machine_secondary in route_definitions:
        filename = next((name for name in public_downloads if public_url(name) == url), None)
        artifact_fact = public_downloads.get(filename) if filename else None
        row = add(
            "routes",
            "route",
            f"C130:{key}",
            {
                "course_id": COURSE_ROLE,
                "route_kind": route_kind,
                "url": url,
                "learner_priority": priority,
                "machine_secondary": machine_secondary,
                "native_html": False,
                "native_html_available": False,
                "unit_anchor": None,
                "page_anchor": None,
                **({"filename": filename, "bytes": artifact_fact[0], "sha256": artifact_fact[1]} if artifact_fact else {}),
            },
            normalized_state="verified_public_route",
            owner_native_state="published_and_anonymously_verified",
        )
        route_ids[key] = row["id"]
    add(
        "reader_surfaces",
        "reader_surface",
        "C130:linked-pdf-reader",
        {
            "course_id": COURSE_ROLE,
            "format": "linked_pdf",
            "public_url": public_url("pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf"),
            "route_id": route_ids["linked-pdf"],
            "landing_route_id": route_ids["learner-landing"],
            "pages": 666,
            "bytes": 26425739,
            "sha256": "daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49",
            "locale": "id-ID",
            "primary": True,
            "tagged": False,
            "unit_anchor_coverage": 0,
            "page_anchor_coverage": 0,
            "pdf_ua_claimed": False,
            "pdf_ua_verified": False,
            "pdf_ua_conformance": "not_claimed",
            "native_html": False,
            "unit_anchors": False,
            "page_anchors": False,
            "tagged_pdf": False,
            "pdf_ua_claim": False,
            "machine_data_primary": False,
        },
        normalized_state="verified_linked_reader",
        owner_native_state="published_and_anonymously_verified",
    )

    add(
        "adapter_profiles",
        "adapter_profile",
        "c130-zero-copy-v2.3.1",
        {
            "contract": "2.3.1",
            "course_id": COURSE_ROLE,
            "owner_native_authoritative": True,
            "full_prose_centralized": False,
            "owner_ids_reminted": False,
            "aggregate_conformance_claim": False,
            "machine_data_is_learner_destination": False,
            "machine_surfaces_secondary": True,
            "zero_copy": True,
            "capability_map": {
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
            },
            "owner_native_unit_count": 1993,
            "owner_native_segment_count": 5525,
        },
    )
    add(
        "adapter_runs",
        "adapter_run",
        "c130-build-2026-08-31",
        {
            "adapter_version": ADAPTER_VERSION,
            "course_id": COURSE_ROLE,
            "owner_counts": OWNER_COUNTS,
            "table_counts": {
                "owner_authorities": 1, "datasets": 1, "editions": 5, "units": 1993,
                "course_unit_memberships": 1993, "native_bindings": 5525,
                "content_bindings": 5525, "relations": 9545, "rights": 21,
                "rights_assignments": 7634, "artifacts": 83, "build_recipes": 0,
                "reader_surfaces": 1, "routes": 7, "search_documents": 1993,
                "adapter_profiles": 1, "adapter_runs": 1, "qa_events": 102,
                "identity_crosswalks": 17273,
            },
            "stale_owner_cursor_release_report_sha256": "a17c5eef4c721bb49de834a33bf0c3561b0dc3393957155692e2ffccc6509ec4",
            "current_live_release_report_sha256": "ae2e905782c099db7d1c177255fbbc6f07146caa2c3cacf2293498cdac3b308f",
            "stale_cursor_treatment": "disclosed_not_rewritten",
            "source_reports_trusted_without_replay": False,
            "owner_tree_mutated": False,
        },
        owner_native_state="pass",
    )

    for native in backend["qa_events"]:
        row = add(
            "qa_events",
            "qa_event",
            f"owner-qa:{native['id']}",
            direct_owner_payload(native, "qa_events", extra={
                "qa_origin": "owner_native_provenance",
                "independent_adapter_validation": False,
            }),
            normalized_state="referenced_native_provenance",
            owner_native_state=native.get("status"),
        )
        register("qa_event", native["id"], "qa_event", row["id"])
    add(
        "qa_events",
        "qa_event",
        "adapter-build-replay",
        {
            "qa_origin": "adapter_generated",
            "qa_type": "adapter_build",
            "result": "pass",
            "table_counts": {
                "owner_authorities": 1, "datasets": 1, "editions": 5, "units": 1993,
                "course_unit_memberships": 1993, "native_bindings": 5525,
                "content_bindings": 5525, "relations": 9545, "rights": 21,
                "rights_assignments": 7634, "artifacts": 83, "build_recipes": 0,
                "reader_surfaces": 1, "routes": 7, "search_documents": 1993,
                "adapter_profiles": 1, "adapter_runs": 1, "qa_events": 102,
                "identity_crosswalks": 17273,
            },
            "authority_counts_replayed": OWNER_COUNTS,
            "relation_type_counts_replayed": RELATION_TYPE_COUNTS,
            "owner_manifest_and_checksums_replayed": True,
            "full_prose_centralized": False,
            "limitations_evidence": {
                "path": "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/c130_operations_research_v231_candidate/research/C130_NATIVE_PIPELINE_LIMITATIONS_20260831.md",
                "bytes": 3720,
                "sha256": "e73edc9413411b1594a07f646cc11011853d9548a87a28f7b1985aa8f74b99c0",
            },
        },
        normalized_state="adapter_validated",
        owner_native_state=None,
    )

    for spec in mapping_specs:
        add(
            "identity_crosswalks",
            "identity_crosswalk",
            f"owner:{spec['source_record_type']}:{spec['source_record_id']}",
            {
                "source_namespace": OWNER_NAMESPACE,
                "target_namespace": str(LANE_NAMESPACE),
                **spec,
                "cardinality": "one_to_one",
                "mapping_state": "mapped",
                "reverse_recipe": "resolve exact owner-native ID from frozen backend-v0.json and deterministic semantic key",
            },
            normalized_state="reversible_mapping",
            owner_native_state="frozen_owner_identity",
        )

    sort_table_rows(tables)
    expected_table_counts = {
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
    require({name: len(tables[name]) for name in TABLE_ORDER} == expected_table_counts, "projected table count drift")
    global_projected_ids = [str(row["id"]) for name in TABLE_ORDER for row in tables[name]]
    require(len(global_projected_ids) == len(set(global_projected_ids)), "duplicate projected IDs across tables")
    require(len(mapping_specs) == 17273, "direct identity mapping count drift")
    context = {
        "package_id": package_id,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_id,
        "extension_id": extension_id,
        "projected_unit_ids": projected_unit_ids,
        "direct_maps": direct_maps,
        "mapping_specs": mapping_specs,
        "route_ids": route_ids,
        "table_counts": expected_table_counts,
    }
    return tables, context


def build_namespace_sidecar(backend: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    prior = prior_v1_identity_facts(backend)
    mappings: list[dict[str, Any]] = []
    for spec in context["mapping_specs"]:
        mappings.append({
            "source_namespace": OWNER_NAMESPACE,
            "target_namespace": str(LANE_NAMESPACE),
            "source_record_id": spec["source_record_id"],
            "target_record_id": spec["target_record_id"],
            "source_record_type": spec["source_record_type"],
            "target_record_type": spec["target_record_type"],
            "cardinality": "one_to_one",
            "mapping_state": "mapped",
            "reverse_recipe": "resolve exact owner-native ID from frozen backend-v0.json and deterministic semantic key",
            "evidence_refs": ["owner_backend_monolith", "owner_backend_manifest", "owner_backend_checksums"],
            "identity_set_sha256": identity_set_sha256([spec["source_record_id"], spec["target_record_id"]]),
        })
    for spec in context["mapping_specs"]:
        native_id = spec["source_record_id"]
        collection = prior["native_table_by_id"][native_id]
        prior_id = prior["prior_id_by_native_id"][native_id]
        mappings.append({
            "source_namespace": str(PREVIOUS_COMMON_NAMESPACE),
            "target_namespace": str(LANE_NAMESPACE),
            "source_record_id": prior_id,
            "target_record_id": spec["target_record_id"],
            "source_record_type": PRIOR_V1_DIRECT_TYPES[collection],
            "target_record_type": spec["target_record_type"],
            "cardinality": "one_to_one",
            "mapping_state": "mapped",
            "reverse_recipe": "resolve the exact prior-v1 UUID from the frozen owner-native ID, migration receipt, and published UUIDv5 formula",
            "evidence_refs": ["prior_v1_migration_receipt", "owner_backend_monolith"],
            "identity_set_sha256": identity_set_sha256([prior_id, spec["target_record_id"]]),
        })

    projected_native_ids = {spec["source_record_id"] for spec in context["mapping_specs"]}
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
    require(unprojected_by_collection == {
        "assets": 346, "concepts": 128, "corrections": 94, "courses": 1,
        "programs": 1, "resources": 4, "terms": 140,
    }, "prior-v1 unprojected type distribution drift")
    return {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "profiles": [
            {
                "name": "c130_owner_native_v0",
                "namespace": OWNER_NAMESPACE,
                "formula": "literal owner-native IDs frozen in backend-v0.json",
            },
            {
                "name": "c130_prior_common_v1_materialized",
                "namespace": str(PREVIOUS_COMMON_NAMESPACE),
                "formula": "UUIDv5(namespace, record_type + '|' + 'o018-c130:native:' + native_id)",
                "migration_receipt": "04_mirrors/id/program-matematika-indonesia-v06213/releases/v0.62.13/o018-c130-id-backend-v1-migration-receipt.json",
                "materialized_records": 17987,
                "mapped_to_v2_3_1": 17273,
                "not_projected_in_v2_3_1": 714,
            },
            {
                "name": "c130_v2_3_lane",
                "namespace": str(LANE_NAMESPACE),
                "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)",
            },
        ],
        "mappings": mappings,
        "unmaterialized_candidates": [{
            "namespace": str(LANE_NAMESPACE),
            "record_type": "course",
            "semantic_key": "course:C130",
            "candidate_record_id": projection_id(LANE_NAMESPACE, "course", "course:C130"),
            "state": "deterministic_id_proposal_not_a_mapping",
            "formula": "UUIDv5(lane_namespace, 'course:course:C130')",
            "effective_cardinality": "unresolved_until_materialized",
        }],
        "identity_sets": {
            "owner_direct_records_sha256": identity_set_sha256(spec["source_record_id"] for spec in context["mapping_specs"]),
            "projected_direct_records_sha256": identity_set_sha256(spec["target_record_id"] for spec in context["mapping_specs"]),
            "prior_v1_all_records_sha256": prior["all_prior_ids_sha256"],
            "prior_v1_projected_records_sha256": identity_set_sha256(
                prior["prior_id_by_native_id"][spec["source_record_id"]] for spec in context["mapping_specs"]
            ),
            "prior_v1_unprojected_records_sha256": identity_set_sha256(
                row["prior_v1_record_id"] for row in unprojected_prior_rows
            ),
            "prior_v1_native_to_prior_pairs_sha256": prior["native_to_prior_pairs_sha256"],
            "prior_v1_projected_to_v2_3_1_pairs_sha256": mapping_set_sha256(
                (prior["prior_id_by_native_id"][spec["source_record_id"]], spec["target_record_id"])
                for spec in context["mapping_specs"]
            ),
            "prior_v1_unprojected_owner_to_prior_pairs_sha256": mapping_set_sha256(
                (row["native_record_id"], row["prior_v1_record_id"]) for row in unprojected_prior_rows
            ),
            "prior_v1_mapping_payload_bytes": prior["mapping_payload_bytes"],
            "prior_v1_mapping_payload_sha256": prior["mapping_payload_sha256"],
            "prior_v1_materialized_records": 17987,
            "prior_v1_projected_records": 17273,
            "prior_v1_unprojected_records": 714,
            "prior_v1_unprojected_by_collection": unprojected_by_collection,
            "prior_v1_unprojected_identity_rows": unprojected_prior_rows,
            "mapped_pairs_sha256": mapping_set_sha256(
                (row["source_record_id"], row["target_record_id"]) for row in mappings
            ),
            "owner_to_v2_3_1_mappings": 17273,
            "prior_v1_to_v2_3_1_mappings": 17273,
            "mapped_records": len(mappings),
        },
        "recorded_at": RECORDED_AT,
    }


def build_translation_sidecar(
    backend: Mapping[str, Any],
    context: Mapping[str, Any],
    authority: Mapping[str, Any],
) -> dict[str, Any]:
    records = []
    for native in backend["units"]:
        records.append({
            "native_unit_id": native["id"],
            "projected_unit_id": context["projected_unit_ids"][native["id"]],
            "locale": native.get("locale"),
            "state": native.get("translation_state"),
            "owner_status": native.get("status"),
            "owner_record_sha256": owner_record_sha256(native),
            "state_source": "frozen_owner_backend_v0_unit_row",
            "edition_native_id": native.get("edition_id"),
            "parent_native_id": native.get("parent_id"),
        })
    records.sort(key=lambda row: row["native_unit_id"])
    states = sorted({str(row["state"]) for row in records})
    return {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "authority_bindings": [dict(authority)],
        "coverage": {
            "course_id": COURSE_ROLE,
            "granularity": "owner_native_semantic_unit",
            "authority_rows": len(backend["units"]),
            "indexed_rows": len(records),
            "inferred_rows": 0,
        },
        "states": states,
        "records": records,
        "identity_set_sha256": identity_set_sha256(row["projected_unit_id"] for row in records),
        "no_inference": True,
        "recorded_at": RECORDED_AT,
    }


def build_rights_assignment_closure_sidecar(
    backend: Mapping[str, Any],
    context: Mapping[str, Any],
    authority: Mapping[str, Any],
) -> dict[str, Any]:
    rows = derive_owner_rights_assignments(backend)
    summary = owner_rights_assignment_facts(backend)
    materialized = [row for row in rows if row["owner_collection"] in {"units", "segments", "artifacts"}]
    referenced_only = [row for row in rows if row["owner_collection"] in {"resources", "assets"}]
    sidecar_rows: list[dict[str, Any]] = []
    for row in referenced_only:
        right_id = row["native_rights_id"]
        require(right_id in context["direct_maps"]["rights"], f"referenced-only rights identity missing: {right_id}")
        sidecar_rows.append({
            **row,
            "projected_rights_id": context["direct_maps"]["rights"][right_id],
            "projected_target_id": None,
            "state": "owner_native_assignment_preserved_target_type_not_projected_in_v2_3_1",
        })
    sidecar_rows.sort(key=lambda row: (
        row["owner_collection"], row["native_target_id"], row["source_field"], row["source_ordinal"], row["native_rights_id"]
    ))
    no_assignment_artifacts = sorted(
        str(row["id"]) for row in backend["artifacts"] if not native_rights_references("artifacts", row)
    )
    require(len(sidecar_rows) == 355 and len(no_assignment_artifacts) == 31, "rights sidecar partition drift")
    return {
        "schema_id": "program-matematika-indonesia/c130-owner-rights-assignment-closure/0.1.0",
        "schema_version": "0.1.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "owner_backend_binding": dict(authority),
        "counts": summary,
        "materialized_projection": {
            "table": "tables/rights_assignments.jsonl",
            "records": len(materialized),
            "target_types": {"unit": 2039, "native_binding": 5525, "artifact": 70},
            "state": "canonical_v2_3_1_rows",
        },
        "referenced_only_projection": {
            "records": len(sidecar_rows),
            "target_collections": {"assets": 346, "resources": 9},
            "reason": "v2.3.1 has no materialized resource or asset target table; no target IDs were invented",
            "assignments": sidecar_rows,
        },
        "artifacts_without_native_rights_assignment": {
            "records": len(no_assignment_artifacts),
            "native_artifact_ids": no_assignment_artifacts,
            "identity_set_sha256": identity_set_sha256(no_assignment_artifacts),
            "state": "preserved_as_owner_native_absence_not_inferred",
        },
        "all_21_rights_identities_materialized": True,
        "flattened_license_claim": False,
        "recorded_at": RECORDED_AT,
    }


def capability_entry(
    name: str,
    state: str,
    native_ids: Iterable[str],
    projected_ids: Iterable[str],
    shard_refs: list[dict[str, Any]],
    closure_rule: str,
    limitation: str | None,
) -> dict[str, Any]:
    native = list(native_ids)
    projected = list(projected_ids)
    identity_values = projected if projected else native
    return {
        "name": name,
        "version": "0.1.0",
        "state": state,
        "schema_binding": None,
        "shard_refs": shard_refs,
        "native_count": len(native),
        "projected_count": len(projected),
        "identity_set_sha256": identity_set_sha256(identity_values) if identity_values else None,
        "identity_set_scope": "projected_records" if projected else "native_shard_records" if native else "none",
        "closure_rules": [closure_rule],
        "loss_gap_report": {
            "status": "declared_limitation" if limitation else "closed",
            "reason": limitation or "The declared capability projection is closed over the frozen authority.",
        },
    }


def build_capability_sidecar(
    backend: Mapping[str, Any],
    tables: Mapping[str, list[dict[str, Any]]],
    context: Mapping[str, Any],
    authorities: Mapping[str, Mapping[str, Any]],
    evidence: Mapping[str, Mapping[str, Any]],
    rights_closure_fact: Mapping[str, Any],
) -> dict[str, Any]:
    owner_shard = [dict(authorities["backend"])]
    limitations_fact = dict(authorities["native_pipeline_limitations"])
    capabilities = [
        capability_entry(
            "structure_localization", "materialized",
            [row["id"] for row in backend["units"]] + [row["id"] for row in backend["relations"]],
            [row["id"] for row in tables["units"]] + [row["id"] for row in tables["relations"]],
            [],
            "All 1,993 owner units and all 9,545 typed owner relations are materialized without conceptual inference.",
            None,
        ),
        capability_entry(
            "terminology", "referenced_native_shards",
            [row["id"] for row in backend["terms"]] + [row["id"] for row in backend["concepts"]], [], owner_shard,
            "The 140 owner-native term records and 128 concept records remain authority-bound in the owner backend.",
            "Term and concept records are not normalized into dedicated v2.3.1 tables; consumers follow the frozen owner shard.",
        ),
        capability_entry(
            "mathematical_preservation", "referenced_native_shards",
            [row["id"] for row in backend["qa_events"]], [], owner_shard,
            "Owner QA provenance is preserved exactly and kept separate from adapter validation.",
            "Historical generator evidence is aggregate-only; archive members are not reconciled byte-for-byte, public packages are compared by names, and provenance claims are not restated as independent adapter replay. Limitations authority: " + limitations_fact["path"] + " SHA-256 " + limitations_fact["sha256"],
        ),
        capability_entry(
            "assessment_support", "referenced_native_shards",
            [row["id"] for row in backend["units"] if row.get("unit_type") in {"exercise", "solution", "answer", "answer_collection", "solutions_manual", "solutions_manual_collection", "tryit", "learningcheckpoint"}],
            [row["id"] for row in tables["units"] if row["payload"].get("unit_type") in {"exercise", "solution", "answer", "answer_collection", "solutions_manual", "solutions_manual_collection", "tryit", "learningcheckpoint"}],
            owner_shard,
            "Assessment units remain in the common structural projection and their bodies remain owner-native.",
            "Exercise, solution, answer and checkpoint bodies are zero-copy references rather than centralized prose.",
        ),
        capability_entry(
            "assets", "referenced_native_shards",
            [row["id"] for row in backend["assets"]], [], owner_shard,
            "All 346 asset identities remain frozen in the owner backend and segment references are preserved.",
            "Asset bytes are not duplicated into the common adapter.",
        ),
        capability_entry(
            "accessibility", "referenced_native_shards",
            ["owner-release-accessibility"], [row["id"] for row in tables["reader_surfaces"]],
            owner_shard,
            "The linked Indonesian PDF and learner landing route are materialized with exact accessibility disclosures.",
            "The PDF is untagged and no PDF/UA, native chapter HTML, unit-anchor or page-anchor claim is made.",
        ),
        capability_entry(
            "corrections", "referenced_native_shards",
            [row["id"] for row in backend["corrections"]], [], owner_shard,
            "All 94 owner correction records remain authority-bound.",
            "The common adapter has no dedicated correction table and does not reinterpret open-by-design correction states.",
        ),
        capability_entry(
            "computational_interactives", "referenced_native_shards",
            [row["id"] for row in backend["units"] if "lab" in str(row.get("unit_type", "")) or row.get("unit_type") in {"interactive_source", "executable_mode", "computational_witness"}],
            [row["id"] for row in tables["units"] if "lab" in str(row["payload"].get("unit_type", "")) or row["payload"].get("unit_type") in {"interactive_source", "executable_mode", "computational_witness"}],
            owner_shard,
            "O018 computational units and their typed relations remain structurally projected; the full labs archive is learner-downloadable.",
            "Laboratory result semantics are not independently recomputed or reconciled by this zero-copy adapter; the native-pipeline limitations provenance is bound at " + limitations_fact["path"] + " SHA-256 " + limitations_fact["sha256"],
        ),
        capability_entry(
            "publication", "materialized",
            [row["id"] for row in backend["artifacts"]],
            [row["id"] for row in tables["artifacts"] + tables["reader_surfaces"] + tables["routes"]],
            owner_shard,
            "All 83 owner artifacts are projected and seven truthful learner/preservation/download routes are materialized.",
            None,
        ),
        capability_entry(
            "research_support", "referenced_native_shards",
            [row["id"] for row in backend["concepts"]] + [row["id"] for row in backend["resources"]],
            [], owner_shard,
            "Owner concepts, resources, provenance and workflow limitations remain frozen external evidence.",
            "Concept/resource records are not normalized into dedicated common tables in this adapter version.",
        ),
    ]
    require([row["name"] for row in capabilities] == CAPABILITY_NAMES, "capability order drift")
    return {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "contract_binding": dict(authorities["capability_contract"]),
        "capabilities": capabilities,
        "legacy_labels": [],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards",
            "shard_refs": [dict(authorities["backend"]), dict(authorities["release_manifest"]), dict(rights_closure_fact)],
            "native_count": len(backend["rights"]),
            "identity_set_sha256": native_id_set(backend["rights"]),
            "closure_rules": [
                "All 21 component-rights identities are materialized; 7,634 unit, segment, and artifact assignments are projected, while 355 resource/asset assignments remain hash-bound in the frozen owner-native shards.",
                "Primary content, code, runtime and third-party rights remain separate and are never flattened.",
            ],
        },
        "recorded_at": RECORDED_AT,
    }


def build_scope_sidecar(
    context: Mapping[str, Any],
    authorities: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "scope_kind": "lane_adapter",
        "course_ids": [COURSE_ROLE],
        "curriculum_role_ids": [COURSE_ROLE],
        "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [role for role in ALL_ROLES if role != COURSE_ROLE],
        "owner_authority_binding": dict(authorities["backend"]),
        "curriculum_authority_binding": dict(authorities["registry_overlay"]),
        "limitations": [
            "C130 only; the other 39 curriculum roles remain outside this adapter.",
            "R017 Book 2 and advanced optimization are explicitly excluded.",
            "Owner-native prose, formulas, exercises, solutions, assets, corrections and term bodies remain external authority.",
            "The learner surface is a Pages landing page plus linked 666-page PDF; native HTML, chapter HTML, and unit/page anchors are absent.",
            "The PDF is untagged and no PDF/UA claim is made.",
            "Historical owner-generator limitations are disclosed and are not converted into independent adapter validation claims.",
        ],
        "recorded_at": RECORDED_AT,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), f"program repository root missing: {repository_root}")
    require(owner_root.is_dir(), f"owner package root missing: {owner_root}")
    require(output != repository_root and output != owner_root, "refusing to build over an authority root")
    if output.exists():
        require(args.replace, "output exists; pass --replace")
        require(output.is_dir(), "replacement output is not a directory")
        shutil.rmtree(output)

    authorities = build_authorities(repository_root, owner_root)
    backend, owner_manifest, release, cursor = verify_owner_backend(owner_root)
    evidence = copy_static_inputs(output)
    tables, context = build_tables(backend, release)
    table_facts = write_tables(output, tables)

    collection_summary = {
        name: {
            "records": len(backend[name]),
            "owner_id_set_sha256": native_id_set(backend[name]),
        }
        for name in OWNER_COUNTS
    }
    write_json(output / "OWNER_NATIVE_IDENTITY_SUMMARY.json", {
        "schema_id": "program-matematika-indonesia/c130-owner-native-identity-summary/1.0.0",
        "course_id": COURSE_ROLE,
        "owner_backend": authorities["backend"],
        "collections": collection_summary,
        "relation_type_counts": RELATION_TYPE_COUNTS,
        "segment_translation_state_counts": SEGMENT_STATE_COUNTS,
        "segment_source_target_relationship_counts": SEGMENT_RELATIONSHIP_COUNTS,
        "unit_locale_counts": {"id-ID": 1205, "mul": 788},
        "rights_assignment_counts": owner_rights_assignment_facts(backend),
        "owner_manifest_files": len(owner_manifest["artifacts"]),
        "owner_manifest_inventory_sha256": inventory_sha256(owner_manifest["artifacts"]),
        "owner_cursor_metadata_lag": {
            "cursor_release_report_sha256": cursor["current_artifacts"]["release"]["qa_report_sha256"],
            "live_release_report_sha256": authorities["release_report"]["sha256"],
            "cursor_upstream_issue": cursor["publication"]["upstream_issue"],
            "treatment": "disclosed_not_rewritten",
        },
        "full_prose_centralized": False,
        "recorded_at": RECORDED_AT,
    })
    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/c130-operations-research-v231-input-authorities/1.0.0",
        "course_id": COURSE_ROLE,
        "authorities": [authorities[key] for key in sorted(authorities)],
        "owner_backend_collection_counts": OWNER_COUNTS,
        "owner_backend_collection_identities": collection_summary,
        "release_identity": {
            "edition_id": release["edition_id"],
            "version": release["version"],
            "canonical_pdf": release["canonical_pdf"],
            "public_repository": "https://github.com/KokunoYumeto/open-optimization-or-book-id",
            "public_pages": "https://kokunoyumeto.github.io/open-optimization-or-book-id/",
            "version_doi": "10.5281/zenodo.22070653",
            "concept_doi": "10.5281/zenodo.22059794",
        },
        "known_owner_metadata_lag": {
            "cursor_release_report_sha256": cursor["current_artifacts"]["release"]["qa_report_sha256"],
            "live_release_report_sha256": authorities["release_report"]["sha256"],
            "stale_authority_path": "00_control/CURRENT_CURSOR.json",
            "live_report_path": "qa/release-package-report.json",
            "independent_live_witnesses": [
                "qa/github-publication-plan.json",
                "release/receipts/github-publication-receipt.json",
            ],
            "classification": "stale cursor metadata; live release report retained",
            "cursor_upstream_issue": cursor["publication"]["upstream_issue"],
            "later_issue_recorded_elsewhere": 3,
            "owner_controls_mutated": False,
        },
        "credentials_recorded": False,
        "private_absolute_paths_recorded": False,
        "owner_native_non_mutation": True,
        "recorded_at": RECORDED_AT,
    })

    scope = build_scope_sidecar(context, authorities)
    write_json(output / "scope-declaration-v0.2.0.json", scope)
    crosswalk = build_namespace_sidecar(backend, context)
    write_json(output / "namespace-crosswalk-v0.2.0.json", crosswalk)
    translation = build_translation_sidecar(backend, context, authorities["backend"])
    write_json(output / "translation-state-index-v0.2.0.json", translation)
    rights_closure = build_rights_assignment_closure_sidecar(backend, context, authorities["backend"])
    write_json(output / "rights-assignment-closure-v0.1.0.json", rights_closure)
    rights_closure_fact = file_fact(
        output / "rights-assignment-closure-v0.1.0.json",
        "rights-assignment-closure-v0.1.0.json",
        "owner_rights_assignment_closure_sidecar",
    )
    csv_sidecar = write_csv_surfaces(output, tables, context["package_id"], RECORDED_AT)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_sidecar)
    capability = build_capability_sidecar(backend, tables, context, authorities, evidence, rights_closure_fact)
    write_json(output / "capability-declarations-v0.2.0.json", capability)

    payload_facts = package_payload_files(output)
    payload_identity = inventory_sha256(payload_facts)
    sidecar_names = [
        "capability-declarations-v0.2.0.json",
        "namespace-crosswalk-v0.2.0.json",
        "translation-state-index-v0.2.0.json",
        "rights-assignment-closure-v0.1.0.json",
        "csv-projection-manifest-v0.2.0.json",
        "scope-declaration-v0.2.0.json",
    ]
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
        "schema_version": "2.3.1",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "extension_id": context["extension_id"],
        "extension_version": ADAPTER_VERSION,
        "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": [authorities[key] for key in sorted(authorities)],
        "sidecars": [file_fact(output / name, name, "sidecar") for name in sidecar_names],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER),
            "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER),
            "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools" / "build_c130_operations_research_v231.py", "tools/build_c130_operations_research_v231.py", "builder"),
            "validator": file_fact(output / "tools" / "validate_c130_operations_research_v231.py", "tools/validate_c130_operations_research_v231.py", "validator"),
            "canonical_serialization": {
                "scope": "builder_generated_json_jsonl_and_csv_only",
                "encoding": "UTF-8",
                "newline": "LF",
                "json_keys": "lexicographically_sorted",
                "trailing_newline": True,
                "copied_schema_and_tool_files": "preserved_exact_source_bytes",
            },
            "deterministic_replay": "byte_identical",
            "build_a_sha256": payload_identity,
            "build_b_sha256": payload_identity,
        },
        "files": payload_facts,
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1",
            "seal_file": "seal.json",
            "seal_excluded_from_own_digest": True,
            "binds": [
                "schemas", "tools", "input_authorities", "evidence", "tables",
                "sidecars", "csv_projections", "manifest",
            ],
        },
        "zero_copy_policy": {
            "owner_native_authoritative": True,
            "full_prose_centralized": False,
            "owner_ids_reminted": False,
            "aggregate_conformance_claim": False,
            "machine_data_is_learner_destination": False,
            "machine_surfaces_secondary": True,
        },
    }
    write_json(output / "manifest.json", manifest)
    manifest_fact = file_fact(output / "manifest.json", "manifest.json", "package_manifest")
    seal_facts = payload_facts + [manifest_fact]
    write_json(output / "seal.json", {
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
        "package_id": context["package_id"],
        "algorithm": "sha256-sorted-path-bytes-v1",
        "files": seal_facts,
        "file_count": len(seal_facts),
        "bytes": sum(int(row["bytes"]) for row in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts),
        "seal_excluded_from_own_digest": True,
        "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [manifest_fact]
    checksum_facts.sort(key=lambda item: str(item["path"]))
    checksum_text = "".join(f"{fact['sha256']}  {fact['path']}\n" for fact in checksum_facts)
    (output / "PACKAGE_CHECKSUMS.sha256").write_text(checksum_text, encoding="utf-8", newline="\n")

    return {
        "status": "pass",
        "output": str(output),
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "table_counts": context["table_counts"],
        "payload_files": len(payload_facts),
        "payload_inventory_sha256": payload_identity,
        "seal_sha256": sha256_file(output / "seal.json"),
        "checksum_sha256": sha256_file(output / "PACKAGE_CHECKSUMS.sha256"),
        "owner_authorities_replayed": len(OWNER_AUTHORITIES),
        "program_authorities_replayed": len(PROGRAM_AUTHORITIES),
        "owner_tree_mutated": False,
        "full_prose_centralized": False,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = build(args)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(compact_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
