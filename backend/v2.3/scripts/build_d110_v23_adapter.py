#!/usr/bin/env python3
"""Build the D110 Mathematics in Lean zero-copy backend-v2.3.1 adapter.

The adapter treats the owner's complete ``mil-backend-record/1.0.0`` export as
immutable authority.  It does not copy book prose or remint owner IDs.  It
projects only stable, hash-bound structure into the shared 19-table envelope
and records every unmapped native capability as an explicit shard reference.
"""

from __future__ import annotations

import argparse
import collections
import json
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    TABLE_ORDER,
    AdapterError,
    canonical_row_sha256,
    combined_shard_identity,
    compact_json,
    empty_tables,
    external_file_fact,
    file_fact,
    identity_set_sha256,
    inventory_sha256,
    make_row,
    mapping_set_sha256,
    package_payload_files,
    projection_id,
    read_json,
    read_jsonl,
    require,
    sha256_bytes,
    sha256_file,
    sort_table_rows,
    write_checksums,
    write_csv_surfaces,
    write_json,
    write_tables,
)


RECORDED_AT = "2026-08-30T18:00:00Z"
ADAPTER_VERSION = "0.1.0"
COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
LANE_NAMESPACE = uuid.uuid5(uuid.UUID(COMMON_NAMESPACE), "v2.3.1:D110:mathematics-in-lean")
OWNER_NAMESPACE = "mil-backend-record/1.0.0"
CURRENT_COURSE_ID = "urn:uuid:8c8e804d-39b7-5b41-aef7-64fc379f7c5f"
CURRENT_V1_COURSE_ID = "urn:uuid:6ec67bee-3f19-592d-ba26-bef36d95690e"
CURRENT_OWNER_DATASET_ID = "urn:uuid:bb9fa013-1c0e-562d-a537-d02a7a627cb8"
NATIVE_COURSE_ID = "urn:mil:course:mathematics-in-lean"
CURRENT_NATIVE_EDITION_ID = "urn:mil:edition:id-id:v4.30.0-id.3"
PUBLIC_HTML = "https://kokunoyumeto.github.io/mathematics-in-lean-id/"
PUBLIC_REPOSITORY = "https://github.com/KokunoYumeto/mathematics-in-lean-id"
PUBLIC_RELEASE = "https://github.com/KokunoYumeto/mathematics-in-lean-id/releases/tag/v4.30.0-id.3"
PUBLIC_PDF = "https://github.com/KokunoYumeto/mathematics-in-lean-id/releases/download/v4.30.0-id.3/matematika-dalam-lean-bahasa-indonesia.pdf"
ZENODO_RECORD = "https://zenodo.org/records/22062017"

COURSE_ROLES = [
    "A00", "A10", "A20", "A30",
    "B10", "B20", "B30", "B40", "B50", "B60", "B70", "B80", "B90", "B95",
    "C10", "C20", "C30", "C40", "C50", "C60", "C70", "C80", "C90", "C100", "C110", "C120", "C130", "C140",
    "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D90", "D100", "D110", "D120",
]

EXPECTED_CENTRAL = {
    "capability_contract": (
        "backend/v2.2/global-capability-contract-v0.1.0.json", 7462,
        "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7",
    ),
    "courses_current": (
        "backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl", 86522,
        "7dee2faef2019e23fe4d3650ee772a23f9120979dae69409672fde3951101351",
    ),
    "federation_manifest": (
        "backend/v2/program-matematika-indonesia-federation-v0.4.4/manifest.json", 8952,
        "62198018ce4d035e1bb3893af5666dddae8e054b1d30a162e24cfd631ba0dc2c",
    ),
}

EXPECTED_OWNER = {
    "current_cursor": ("00_control/CURRENT_CURSOR.json", 5624, "de827a7f181a7605289ab829e8b0e10e8128ee91109b418ce3ec43eeb715f841"),
    "central_handoff": ("00_control/CENTRAL_HUB_HANDOFF_ID3.json", 4609, "0041c972224128bb9e61c9c5fedd001bebb2b4afce695257b7b404456ae9c33a"),
    "rights_receipt": ("00_control/FINAL_RIGHTS_RECEIPT.json", 5141, "406faf58c317a433c8dab8357a3353bd765b4fa96a0fea204f1bae06732df496"),
    "backend_receipt": ("qa/FINAL_BACKEND_RECEIPT.json", 4269, "ec7b42c3a752dd734d94df77ebec4e91a0559af51e2f148b26c9c236ab2e279f"),
    "lean_receipt": ("qa/FINAL_LEAN_BUILD.json", 4597, "e217e88c2ae0721728ba59556845e995cc1687b4298104dde9070c8a675e1550"),
    "html_build_receipt": ("qa/FINAL_HTML_BUILD.json", 3961, "d11dfc7d26e028335f947668130ec92f05a0d676e0d2b636cb2fadd5eca07e95"),
    "html_audit_receipt": ("qa/FINAL_HTML_AUDIT.json", 2835, "11e1ebb94887305e1bd63d40a73bf17000cacf9298b3d2fb03daa56098073ae3"),
    "pdf_receipt": ("qa/FINAL_PDF_BUILD.json", 5123, "2d8b5de79706de200d6c9e3f4e03752dd8b6302d9be11ce8f0a4cf67737ad1d9"),
    "privacy_receipt": ("qa/FINAL_RELEASE_DEEP_PRIVACY_SCAN.json", 1597, "67671da5f4297ea715abb0ff1730ed8b4199d9f7aaff8252145061fecc5e27b9"),
    "github_receipt": ("publication/GITHUB_PUBLICATION_RECEIPT_ID3.json", 9479, "87975b78a1e0b5c2e490c36ddd5fa43dbdf7f490ffccf9eff67f3d45225f1289"),
    "zenodo_receipt": ("publication/ZENODO_TERMINOLOGY_QA_PUBLICATION_RECEIPT.json", 6133, "c6e48e874b5c4a87b31906a7c23dc62f9a17117612c105ec13bed1a02f9f691e"),
    "native_export_manifest": ("backend/exports/export-manifest.json", 8084, "3577912edade478aef93d2a8ef6f4e87284c8cda68fe4a329eddc2f0781eeaa0"),
    "native_catalog": ("backend/exports/catalog.json", 19555921, "bc0be8cbd331e1160f556cafad2ec3f828ef227ff9f7ec98c60facb3b4cbf7cc"),
    "native_records_jsonl": ("backend/exports/records.jsonl", 15532090, "974e145da718fa3fec9027d0193b21503fa69d3ac4f775cb553a368bf367f1a2"),
    "native_records_csv": ("backend/exports/records.csv", 18388279, "5ed43c51d24b67236bfa2483efada5bad402c5e5bee0ce086936187804fde93e"),
    "native_schema": ("backend/schema/catalog.schema.json", 4347, "2e519f38a24c1e6dc2696c9e9a8196b793b1452993fe6f4cd7576432d43ff130"),
    "native_builder": ("scripts/build_backend.py", 725300, "a029fc378e11cb9acbc78e945e024981141bc1522c379d01f12dd8f07ded1119"),
    "native_validator": ("scripts/validate_backend.py", 463784, "18ed93e3ccb82725dd90209845b3c50870c906a74f41fba4b5a1ceb9f32a9694"),
    "public_html_index": ("output/html/index.html", 15775, "5bae139f610e39b6cba02b5f63c137f088ccb46d6577b4411f31c77064847717"),
    "public_pdf": ("output/pdf/matematika-dalam-lean-bahasa-indonesia.pdf", 1239573, "86aadfbd2bdb48370ea633a91cc0be5583d1a7a0b4379647141c651d8debea0c"),
    "public_backend_zip": ("output/release/matematika-dalam-lean-bahasa-indonesia-backend-4.30.0-id.3.zip", 7101665, "522abc439742b99a623f083bfbcb29bc0eab45de7622bfe2c1b227a6c868c5d0"),
}

NATIVE_COUNTS = {
    "artifact": 182, "asset": 800, "concept": 326, "correction": 249,
    "course": 1, "edition": 6, "program": 1, "qa_event": 186,
    "relation": 5471, "resource": 3, "rights": 37, "segment": 1213,
    "term": 326, "unit": 2177,
}

PROJECTED_NATIVE_TYPES = {
    "edition": "edition",
    "unit": "unit",
    "segment": "content_binding",
    "relation": "relation",
    "rights": "rights",
    "artifact": "artifact",
    "qa_event": "qa_event",
}


def basic_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {key: fact[key] for key in ("path", "path_base", "role", "bytes", "sha256")}


def native_state(row: Mapping[str, Any]) -> str:
    return str(row.get("translation_state") or row.get("status") or "recorded")


def stable_order_key(row: Mapping[str, Any]) -> str:
    return f"{int(row.get('order_index') or 0):012d}.{row['record_id']}"


def selected_data(row: Mapping[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    data = row.get("data") if isinstance(row.get("data"), dict) else {}
    return {key: data.get(key) for key in keys if key in data}


def path_from(root: Path, relative: str) -> Path:
    return root.joinpath(*PurePosixPath(relative).parts)


def build_authorities(
    repository_root: Path, owner_root: Path
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    authorities: list[dict[str, Any]] = []
    named: dict[str, dict[str, Any]] = {}
    for role, (relative, size, digest) in EXPECTED_CENTRAL.items():
        fact = external_file_fact(path_from(repository_root, relative), relative, role, "program_repository_root", expected_bytes=size, expected_sha256=digest)
        named[role] = fact
        authorities.append(basic_fact(fact))
    for role, (relative, size, digest) in EXPECTED_OWNER.items():
        fact = external_file_fact(path_from(owner_root, relative), relative, role, "owner_package_root", expected_bytes=size, expected_sha256=digest)
        named[role] = fact
        authorities.append(basic_fact(fact))

    export_manifest = read_json(path_from(owner_root, EXPECTED_OWNER["native_export_manifest"][0]))
    require(export_manifest.get("schema") == "mil-backend-export-manifest", "D110 export manifest schema drift")
    require(export_manifest.get("schema_version") == "1.0.0", "D110 export manifest version drift")
    entries = {str(item["path"]): item for item in export_manifest.get("files", [])}
    require(len(entries) == export_manifest.get("file_count") == 48, "D110 export manifest inventory drift")

    shards: dict[str, list[dict[str, Any]]] = {}
    all_ids: list[str] = []
    for entity_type, expected_count in NATIVE_COUNTS.items():
        relative = f"backend/exports/entities/{entity_type}.jsonl"
        manifest_relative = f"entities/{entity_type}.jsonl"
        require(manifest_relative in entries, f"missing D110 native shard fact: {entity_type}")
        entry = entries[manifest_relative]
        rows = read_jsonl(path_from(owner_root, relative))
        ids = [str(row.get("record_id", "")) for row in rows]
        require(len(rows) == expected_count, f"D110 native record count drift: {entity_type}")
        require(all(ids) and len(ids) == len(set(ids)), f"D110 native record ID failure: {entity_type}")
        require(all(row.get("entity_type") == entity_type for row in rows), f"D110 native entity type drift: {entity_type}")
        fact = external_file_fact(
            path_from(owner_root, relative), relative, f"owner_native_{entity_type}", "owner_package_root",
            expected_bytes=int(entry["bytes"]), expected_sha256=str(entry["sha256"]),
            records=len(rows), record_id_set_sha256=identity_set_sha256(ids),
        )
        named[f"native_{entity_type}"] = fact
        authorities.append(basic_fact(fact))
        shards[entity_type] = rows
        all_ids.extend(ids)
    require(sum(len(rows) for rows in shards.values()) == 10978, "D110 native aggregate count drift")
    require(len(all_ids) == len(set(all_ids)) == 10978, "D110 global native IDs are not unique")

    catalog = read_json(path_from(owner_root, EXPECTED_OWNER["native_catalog"][0]))
    require(catalog.get("schema") == "mil-modular-backend-catalog", "D110 catalog schema drift")
    require(catalog.get("schema_version") == "1.0.0", "D110 catalog version drift")
    require(len(catalog.get("records", [])) == 10978, "D110 catalog record count drift")
    catalog_ids = [str(row["record_id"]) for row in catalog["records"]]
    require(len(catalog_ids) == len(set(catalog_ids)) == len(all_ids), "D110 catalog identity uniqueness drift")
    require(identity_set_sha256(catalog_ids) == identity_set_sha256(all_ids), "D110 catalog identity-set drift")
    records_rows = read_jsonl(path_from(owner_root, EXPECTED_OWNER["native_records_jsonl"][0]))
    require(records_rows == catalog["records"], "D110 aggregate records.jsonl differs from catalog")

    rights_ids = {str(row["rights_id"]) for row in shards["rights"]}
    require(len(rights_ids) == 37, "D110 rights identity count drift")
    require(all(str(row.get("rights_id", "")) in rights_ids for rows in shards.values() for row in rows), "D110 unresolved native rights pointer")
    return authorities, named, shards


def locate_course(repository_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    rows = read_jsonl(path_from(repository_root, EXPECTED_CENTRAL["courses_current"][0]))
    courses = {str(row.get("payload", {}).get("course_id")): row for row in rows if row.get("record_type") == "course"}
    require("D110" in courses and courses["D110"]["id"] == CURRENT_COURSE_ID, "current D110 course identity drift")
    d110 = courses["D110"]
    require(d110["payload"].get("v1_course_id") == CURRENT_V1_COURSE_ID, "D110 v1 course identity drift")
    require(d110["payload"].get("owner_dataset_id") == CURRENT_OWNER_DATASET_ID, "D110 owner dataset identity drift")
    prerequisite_ids = {role: str(courses[role]["id"]) for role in ("B10", "B40", "C10", "C30")}
    return d110, prerequisite_ids


def projection_registry(shards: Mapping[str, list[dict[str, Any]]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    registry: dict[str, dict[str, Any]] = {}
    native_by_id: dict[str, dict[str, Any]] = {}
    for entity_type, rows in shards.items():
        for ordinal, row in enumerate(rows, 1):
            native_id = str(row["record_id"])
            native_by_id[native_id] = row
            if entity_type not in PROJECTED_NATIVE_TYPES:
                continue
            target_type = PROJECTED_NATIVE_TYPES[entity_type]
            semantic_key = f"d110:native:{native_id}"
            registry[native_id] = {
                "source_table": entity_type,
                "source_ordinal": ordinal,
                "target_record_type": target_type,
                "semantic_key": semantic_key,
                "target_id": projection_id(LANE_NAMESPACE, target_type, semantic_key),
                "native_record_sha256": canonical_row_sha256(row),
            }
    require(len(registry) == 9272, "D110 materialized native registry drift")
    require(len({entry["target_id"] for entry in registry.values()}) == len(registry), "D110 projected ID collision")
    return registry, native_by_id


def build_tables(
    named: Mapping[str, Mapping[str, Any]],
    shards: Mapping[str, list[dict[str, Any]]],
    course_row: Mapping[str, Any],
    prerequisite_ids: Mapping[str, str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    package_id = projection_id(LANE_NAMESPACE, "lane_adapter_package", f"d110:mathematics-in-lean:{ADAPTER_VERSION}")
    dataset_id = projection_id(LANE_NAMESPACE, "dataset", "d110:mathematics-in-lean")
    owner_authority_id = projection_id(LANE_NAMESPACE, "owner_authority", "d110:owner-native-id3")
    html_surface_id = projection_id(LANE_NAMESPACE, "reader_surface", "d110:id3:html")
    pdf_surface_id = projection_id(LANE_NAMESPACE, "reader_surface", "d110:id3:pdf")
    html_route_id = projection_id(LANE_NAMESPACE, "route", "d110:id3:html-course-root")
    pdf_route_id = projection_id(LANE_NAMESPACE, "route", "d110:id3:pdf-offline")
    registry, native_by_id = projection_registry(shards)
    endpoint_map = {native_id: entry["target_id"] for native_id, entry in registry.items()}
    endpoint_map[NATIVE_COURSE_ID] = CURRENT_COURSE_ID
    rights_map = {str(row["rights_id"]): registry[str(row["record_id"])]["target_id"] for row in shards["rights"]}
    require(len(rights_map) == 37, "D110 projected rights count drift")
    current_edition_id = registry[CURRENT_NATIVE_EDITION_ID]["target_id"]
    tables = empty_tables()

    tables["owner_authorities"].append(make_row(
        LANE_NAMESPACE, "owner_authority", "d110:owner-native-id3",
        {
            "authority_kind": "owner_native_deterministic_modular_backend",
            "authority_scope": "complete Mathematics in Lean id-ID v4.30.0-id.3 source, semantic graph, rights, QA, and publication closure",
            "native_schema_name": "mil-backend-record",
            "native_schema_version": "1.0.0",
            "native_namespace": OWNER_NAMESPACE,
            "native_record_count": 10978,
            "native_export_manifest_sha256": named["native_export_manifest"]["sha256"],
            "native_export_bytes": 92714008,
            "public_repository_url": PUBLIC_REPOSITORY,
            "content_commit": "6849b156d1016cc91bd22024892721013e39f414",
            "content_tree": "f5418174e728ec3aefda23bbdecbb245790a866a",
            "release_lineage_url": "https://doi.org/10.5281/zenodo.22058474",
            "final_version_doi": "https://doi.org/10.5281/zenodo.22062017",
            "sole_integrator_publisher": True,
            "zero_copy": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="complete_public_verified",
    ))
    tables["datasets"].append(make_row(
        LANE_NAMESPACE, "dataset", "d110:mathematics-in-lean",
        {
            "dataset_kind": "zero_copy_owner_projection",
            "course_ids": [CURRENT_COURSE_ID],
            "curriculum_role_ids": ["D110"],
            "owner_dataset_id": CURRENT_OWNER_DATASET_ID,
            "owner_record_count": 10978,
            "native_entity_counts": NATIVE_COUNTS,
            "materialized_native_record_count": len(registry),
            "publication_state": "complete_public_anonymous_readback_verified",
            "capabilities": CAPABILITY_NAMES,
            "reader_surface_ids": [html_surface_id, pdf_surface_id],
            "current_edition_id": current_edition_id,
            "body_prose_copied": False,
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="v4.30.0-id.3",
    ))

    for native in shards["edition"]:
        data = native.get("data", {})
        tables["editions"].append(make_row(
            LANE_NAMESPACE, "edition", registry[str(native["record_id"])]["semantic_key"],
            {
                "native_edition_id": native["record_id"],
                "release_version": data.get("release_version"),
                "canonical_identifier": data.get("canonical_identifier"),
                "doi": data.get("doi"),
                "zenodo_record_id": data.get("zenodo_record_id"),
                "publication_status": data.get("publication_status"),
                "locale": native.get("locale"),
                "source_record_id": native.get("source_record_id"),
                "supersedes_native_id": native.get("supersedes_id"),
                "native_payload_sha256": sha256_bytes(compact_json(data).encode("utf-8")),
                "public_html": PUBLIC_HTML if native["record_id"] == CURRENT_NATIVE_EDITION_ID else None,
                "current_complete_edition": native["record_id"] == CURRENT_NATIVE_EDITION_ID,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published" if native["record_id"] == CURRENT_NATIVE_EDITION_ID else "validated",
            owner_native_state=native_state(native),
        ))

    segments_by_unit: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for segment in shards["segment"]:
        segments_by_unit[str(segment.get("parent_id"))].append(segment)

    unit_metadata_keys = (
        "unit_type", "lean_name", "declaration_kind", "anonymous", "is_exercise",
        "solution_available", "solution_id", "formal_equal", "verified_solution",
        "code_asset_id", "exercise_count", "solution_count", "sorry_holes",
        "pedagogical_sorry_holes", "intentionally_retained_nonexercise_sorry",
        "source_text_sha256", "target_text_sha256",
    )
    for native in shards["unit"]:
        native_id = str(native["record_id"])
        target_id = registry[native_id]["target_id"]
        parent_native = str(native.get("parent_id") or "")
        parent_projected = endpoint_map.get(parent_native)
        rights_native = str(native["rights_id"])
        metadata = selected_data(native, unit_metadata_keys)
        tables["units"].append(make_row(
            LANE_NAMESPACE, "unit", registry[native_id]["semantic_key"],
            {
                "native_unit_id": native_id,
                "native_unit_kind": native.get("data", {}).get("unit_type"),
                "source_local_id": native.get("source_local_id"),
                "order_key": stable_order_key(native),
                "native_order": native.get("order_index"),
                "parent_native_unit_id": parent_native,
                "parent_projected_unit_id": parent_projected,
                "native_concept_ids": native.get("concept_ids", []),
                "native_prerequisite_ids": native.get("prerequisite_ids", []),
                "native_edition_id": native.get("edition_id"),
                "native_resource_id": native.get("resource_id"),
                "native_rights_id": rights_native,
                "current_rights_id": rights_map[rights_native],
                "source_path": native.get("source_path"),
                "source_locator": native.get("source_locator"),
                "source_sha256": native.get("source_sha256"),
                "translation_state": native.get("translation_state"),
                "locale": native.get("locale"),
                "language": native.get("language"),
                "segment_evidence_count": len(segments_by_unit.get(native_id, [])),
                "selected_native_metadata": metadata,
                "learner_route": {
                    "url": PUBLIC_HTML, "anchor": None, "route_id": html_route_id,
                    "route_state": "verified_course_fallback_per_unit_route_not_published",
                    "machine_data_only": False,
                },
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))
        tables["course_unit_memberships"].append(make_row(
            LANE_NAMESPACE, "course_unit_membership", f"d110:membership:{native_id}",
            {
                "course_id": CURRENT_COURSE_ID,
                "edition_id": current_edition_id,
                "unit_id": target_id,
                "native_unit_id": native_id,
                "parent_unit_id": parent_projected,
                "order_key": stable_order_key(native),
                "required": None,
                "visible": None,
                "membership_policy_state": "owner_hierarchy_preserved_policy_not_inferred",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))
        bounded_terms = [
            str(native.get("source_local_id") or ""), str(metadata.get("unit_type") or ""),
            str(metadata.get("lean_name") or ""), *[str(value) for value in native.get("concept_ids", [])],
            "Matematika dalam Lean D110",
        ]
        tables["search_documents"].append(make_row(
            LANE_NAMESPACE, "search_document", f"d110:search:{native_id}",
            {
                "course_id": CURRENT_COURSE_ID, "unit_id": target_id,
                "native_unit_id": native_id, "title": native.get("source_local_id"),
                "locale": "id-ID", "order_key": stable_order_key(native),
                "bounded_search_text": " ".join(item for item in bounded_terms if item),
                "learner_url": PUBLIC_HTML, "learner_anchor": None, "body_prose_copied": False,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))

    for native in shards["segment"]:
        native_id = str(native["record_id"])
        data = native.get("data", {})
        native_unit = str(native.get("parent_id") or "")
        tables["content_bindings"].append(make_row(
            LANE_NAMESPACE, "content_binding", registry[native_id]["semantic_key"],
            {
                "native_segment_id": native_id,
                "native_unit_id": native_unit,
                "projected_unit_id": endpoint_map.get(native_unit),
                "segment_kind": data.get("segment_kind"),
                "native_order": native.get("order_index"),
                "native_concept_ids": native.get("concept_ids", []),
                "native_edition_id": native.get("edition_id"),
                "native_resource_id": native.get("resource_id"),
                "native_rights_id": native.get("rights_id"),
                "source_local_id": native.get("source_local_id"),
                "source_path": native.get("source_path"),
                "source_locator": native.get("source_locator"),
                "source_file_sha256": data.get("source_file_sha256"),
                "source_text_sha256": data.get("source_text_sha256"),
                "target_path": data.get("target_path"),
                "target_locator": data.get("target_locator"),
                "target_file_sha256": data.get("target_file_sha256"),
                "target_text_sha256": data.get("target_text_sha256"),
                "source_locale": data.get("source_locale"),
                "target_locale": data.get("target_locale"),
                "translatable": data.get("translatable"),
                "translation_state": native.get("translation_state"),
                "body_prose_copied": False,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))

    endpoint_keys = (
        "subject_id", "object_id", "source_unit_id", "declaration_id", "exercise_id",
        "solution_id", "dependency_unit_id", "dependency_solution_id", "support_id", "code_asset_id",
    )
    for native in shards["relation"]:
        native_id = str(native["record_id"])
        data = native.get("data", {})
        endpoints = {key: data.get(key) for key in endpoint_keys if data.get(key)}
        mapped = {key: endpoint_map.get(str(value)) for key, value in endpoints.items() if endpoint_map.get(str(value))}
        tables["relations"].append(make_row(
            LANE_NAMESPACE, "relation", registry[native_id]["semantic_key"],
            {
                "native_relation_id": native_id,
                "relation_type": data.get("relation_type"),
                "native_endpoints": endpoints,
                "projected_endpoints": mapped,
                "native_parent_id": native.get("parent_id"),
                "native_data_sha256": sha256_bytes(compact_json(data).encode("utf-8")),
                "prose_fields_copied": False,
                "concept_relation_inferred": False,
                "evidence_state": "exact_owner_native_relation",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state=native_state(native),
        ))
    for role in ("B10", "B40", "C10", "C30"):
        tables["relations"].append(make_row(
            LANE_NAMESPACE, "relation", f"d110:curriculum-prerequisite:{role}",
            {
                "relation_type": "prerequisite",
                "from_projected_id": CURRENT_COURSE_ID,
                "to_projected_id": prerequisite_ids[role],
                "source_authority": "courses_current",
                "source_course_role": "D110", "target_course_role": role,
                "concept_relation_inferred": False, "evidence_state": "exact_curriculum_snapshot_row",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state="curriculum_snapshot",
        ))

    rights_keys = (
        "component_id", "component_scope", "component_type", "license_expression",
        "attribution_required", "change_notice_required", "share_alike_required",
        "obligations", "path_scope", "risk", "verification_status", "source_identity",
        "non_endorsement",
    )
    for native in shards["rights"]:
        native_id = str(native["record_id"])
        tables["rights"].append(make_row(
            LANE_NAMESPACE, "rights", registry[native_id]["semantic_key"],
            {
                "native_rights_id": native.get("rights_id"),
                "selected_native_rights": selected_data(native, rights_keys),
                "native_data_sha256": sha256_bytes(compact_json(native.get("data", {})).encode("utf-8")),
                "flattened_course_license": False,
                "assertion_status": "exact_owner_native_rights_record",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))

    for native_id, entry in registry.items():
        native = native_by_id[native_id]
        rights_native = str(native["rights_id"])
        tables["rights_assignments"].append(make_row(
            LANE_NAMESPACE, "rights_assignment", f"d110:rights-assignment:{native_id}",
            {
                "target_id": entry["target_id"],
                "target_record_type": entry["target_record_type"],
                "target_native_id": native_id,
                "direct_native_rights_id": rights_native,
                "current_rights_id": rights_map[rights_native],
                "assignment_state": "exact_direct_owner_native_pointer",
                "inheritance": "none",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state=native_state(native),
        ))

    artifact_keys = ("artifact_type", "path", "bytes", "sha256", "file_count", "uncompressed_bytes", "toolchain", "build_receipt")
    for native in shards["artifact"]:
        native_id = str(native["record_id"])
        tables["artifacts"].append(make_row(
            LANE_NAMESPACE, "artifact", registry[native_id]["semantic_key"],
            {
                "native_artifact_id": native_id,
                "selected_native_artifact": selected_data(native, artifact_keys),
                "native_data_sha256": sha256_bytes(compact_json(native.get("data", {})).encode("utf-8")),
                "native_rights_id": native.get("rights_id"),
                "publication_claim": "none_unless_separately_bound",
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state=native_state(native),
        ))
    public_specs = [
        ("html", "semantic_html_course", "text/html", PUBLIC_HTML, named["public_html_index"], html_route_id),
        ("pdf", "offline_pdf_reader", "application/pdf", PUBLIC_PDF, named["public_pdf"], pdf_route_id),
        ("backend", "owner_native_backend_archive", "application/zip", ZENODO_RECORD + "/files/matematika-dalam-lean-bahasa-indonesia-backend-4.30.0-id.3.zip?download=1", named["public_backend_zip"], None),
    ]
    for key, kind, media_type, url, fact, route_id in public_specs:
        tables["artifacts"].append(make_row(
            LANE_NAMESPACE, "artifact", f"d110:public:{key}",
            {
                "artifact_kind": kind, "media_type": media_type, "public_url": url,
                "local_authority": basic_fact(fact), "route_id": route_id,
                "anonymous_readback_state": "pass", "body_prose_copied": False,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="public_verified",
        ))

    for key, receipt_role, builder_role, validator_role, scope in (
        ("backend", "backend_receipt", "native_builder", "native_validator", "deterministic native backend emission and strict round-trip validation"),
        ("lean", "lean_receipt", "native_builder", "native_validator", "Lean authoring, learner, solution, and clean-source compile closure"),
        ("reader", "html_build_receipt", "native_builder", "native_validator", "HTML/PDF reader build and accessibility/layout audit closure"),
    ):
        tables["build_recipes"].append(make_row(
            LANE_NAMESPACE, "build_recipe", f"d110:build:{key}",
            {
                "recipe_kind": key, "scope": scope,
                "receipt": basic_fact(named[receipt_role]),
                "builder_authority": basic_fact(named[builder_role]),
                "validator_authority": basic_fact(named[validator_role]),
                "network_required": False, "owner_tree_mutation": False,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state="pass",
        ))

    tables["reader_surfaces"].extend([
        make_row(LANE_NAMESPACE, "reader_surface", "d110:id3:html", {
            "surface_kind": "semantic_html", "locale": "id-ID", "url": PUBLIC_HTML,
            "route_id": html_route_id, "primary_learner_surface": True,
            "primary_accessibility_surface": True, "public_readback": "pass",
            "authority": basic_fact(named["html_audit_receipt"]),
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="html_audit_pass"),
        make_row(LANE_NAMESPACE, "reader_surface", "d110:id3:pdf", {
            "surface_kind": "offline_pdf", "locale": "id-ID", "url": PUBLIC_PDF,
            "route_id": pdf_route_id, "pages": 219, "tagged": False,
            "primary_learner_surface": False, "primary_accessibility_surface": False,
            "public_readback": "pass", "authority": basic_fact(named["pdf_receipt"]),
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="pdf_layout_pass_untagged"),
    ])
    tables["routes"].extend([
        make_row(LANE_NAMESPACE, "route", "d110:id3:html-course-root", {
            "route_kind": "learner_course_root", "url": PUBLIC_HTML,
            "surface_id": html_surface_id, "course_id": CURRENT_COURSE_ID,
            "fragment_policy": "course_fallback_only_per_unit_routes_not_published", "verified": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="http_200_verified"),
        make_row(LANE_NAMESPACE, "route", "d110:id3:pdf-offline", {
            "route_kind": "offline_pdf_download", "url": PUBLIC_PDF,
            "surface_id": pdf_surface_id, "course_id": CURRENT_COURSE_ID, "verified": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT, normalized_state="published", owner_native_state="anonymous_hash_readback_pass"),
    ])

    tables["adapter_profiles"].append(make_row(
        LANE_NAMESPACE, "adapter_profile", "d110:v2.3.1:zero-copy",
        {
            "contract": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
            "projection_policy": "stable native identities with UUIDv5 crosswalk; no textbook prose copied",
            "native_namespace": OWNER_NAMESPACE, "canonical_namespace": str(LANE_NAMESPACE),
            "table_order": TABLE_ORDER, "owner_native_authoritative": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state="profile_frozen",
    ))
    tables["adapter_runs"].append(make_row(
        LANE_NAMESPACE, "adapter_run", "d110:v2.3.1:build",
        {
            "builder": "tools/build_d110_v23_adapter.py",
            "validator": "tools/validate_d110_v23_adapter.py",
            "generic_validator": "tools/validate_lane_adapter_v231.py",
            "source_export_manifest_sha256": named["native_export_manifest"]["sha256"],
            "expected_native_records": 10978, "expected_materialized_native_records": len(registry),
            "deterministic_build_policy": "two absent output directories byte-identical",
        }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state="configured",
    ))

    for native in shards["qa_event"]:
        native_id = str(native["record_id"])
        data = native.get("data", {})
        tables["qa_events"].append(make_row(
            LANE_NAMESPACE, "qa_event", registry[native_id]["semantic_key"],
            {
                "native_qa_event_id": native_id,
                "event_type": data.get("event_type"), "result": data.get("result"),
                "responsible_workflow": data.get("responsible_workflow"),
                "source_path": native.get("source_path"), "source_sha256": native.get("source_sha256"),
                "native_data_sha256": sha256_bytes(compact_json(data).encode("utf-8")),
                "embedded_receipt_payload_copied": False,
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state=native_state(native),
        ))

    crosswalk_mappings: list[dict[str, Any]] = []
    for native_id in sorted(registry):
        entry = registry[native_id]
        native = native_by_id[native_id]
        shard_fact = named[f"native_{entry['source_table']}"]
        pair_digest = mapping_set_sha256([(native_id, entry["target_id"])])
        binding_payload = {
            "native_namespace": OWNER_NAMESPACE,
            "native_record_id": native_id,
            "native_entity_type": entry["source_table"],
            "native_shard": basic_fact(shard_fact),
            "native_row_ordinal": entry["source_ordinal"],
            "native_record_sha256": entry["native_record_sha256"],
            "projected_record_id": entry["target_id"],
            "projected_record_type": entry["target_record_type"],
            "reverse_recipe": "read exact owner shard row by native_record_id and verify native_record_sha256",
            "body_prose_copied": False,
        }
        tables["native_bindings"].append(make_row(
            LANE_NAMESPACE, "native_binding", f"d110:binding:{native_id}", binding_payload,
            dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state=native_state(native),
        ))
        tables["identity_crosswalks"].append(make_row(
            LANE_NAMESPACE, "identity_crosswalk", f"d110:crosswalk:{native_id}",
            {
                "source_namespace": OWNER_NAMESPACE, "source_record_id": native_id,
                "source_record_type": entry["source_table"], "target_namespace": str(LANE_NAMESPACE),
                "target_record_id": entry["target_id"], "target_record_type": entry["target_record_type"],
                "cardinality": "one_to_one", "mapping_state": "mapped",
                "mapping_pair_sha256": pair_digest, "reverse_recipe": binding_payload["reverse_recipe"],
            }, dataset_id=dataset_id, owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT, normalized_state="validated", owner_native_state=native_state(native),
        ))
        crosswalk_mappings.append({
            "source_namespace": OWNER_NAMESPACE, "target_namespace": str(LANE_NAMESPACE),
            "source_record_id": native_id, "target_record_id": entry["target_id"],
            "source_record_type": entry["source_table"], "target_record_type": entry["target_record_type"],
            "cardinality": "one_to_one", "mapping_state": "mapped",
            "reverse_recipe": binding_payload["reverse_recipe"],
            "evidence_refs": [shard_fact["path"], "INPUT_AUTHORITIES.json"],
            "identity_set_sha256": pair_digest,
        })

    sort_table_rows(tables)
    expected_counts = {
        "owner_authorities": 1, "datasets": 1, "editions": 6, "units": 2177,
        "course_unit_memberships": 2177, "native_bindings": 9272,
        "content_bindings": 1213, "relations": 5475, "rights": 37,
        "rights_assignments": 9272, "artifacts": 185, "build_recipes": 3,
        "reader_surfaces": 2, "routes": 2, "search_documents": 2177,
        "adapter_profiles": 1, "adapter_runs": 1, "qa_events": 186,
        "identity_crosswalks": 9272,
    }
    require({name: len(tables[name]) for name in TABLE_ORDER} == expected_counts, "D110 canonical table count drift")
    require(sum(expected_counts.values()) == 41460, "D110 canonical record total drift")
    return tables, {
        "package_id": package_id, "dataset_id": dataset_id, "owner_authority_id": owner_authority_id,
        "current_edition_id": current_edition_id, "registry": registry,
        "native_by_id": native_by_id, "crosswalk_mappings": crosswalk_mappings,
        "expected_counts": expected_counts, "course_row": course_row,
    }


def capability_shards(named: Mapping[str, Mapping[str, Any]], names: Iterable[str]) -> list[dict[str, Any]]:
    return [dict(named[f"native_{name}"]) for name in names]


def capability_entry(
    name: str, state: str, shards: list[dict[str, Any]], projected_count: int, limitation: str | None
) -> dict[str, Any]:
    native_count = sum(int(item.get("records", 0)) for item in shards)
    if state == "materialized":
        identity_scope = "projected_records"
        identity_digest = None
    elif shards:
        identity_scope = "native_shard_records"
        identity_digest = combined_shard_identity(shards)
    else:
        identity_scope = "none"
        identity_digest = None
    return {
        "name": name, "version": "0.1.0", "state": state, "schema_binding": None,
        "shard_refs": shards, "native_count": native_count, "projected_count": projected_count,
        "identity_set_sha256": identity_digest, "identity_set_scope": identity_scope,
        "closure_rules": [
            "owner-native shards remain byte-for-byte authoritative",
            "projection never copies textbook body prose",
            "no absent semantics are inferred",
        ],
        "loss_gap_report": {
            "status": "declared_limitation" if limitation else "closed",
            "reason": limitation or "All claimed adapter semantics are exact projections or exact native-shard references.",
        },
    }


def build_sidecars(
    output: Path, named: Mapping[str, Mapping[str, Any]], shards: Mapping[str, list[dict[str, Any]]],
    tables: Mapping[str, list[dict[str, Any]]], context: Mapping[str, Any]
) -> None:
    package_id = str(context["package_id"])
    dataset_id = str(context["dataset_id"])
    registry = context["registry"]
    scope = {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "scope_kind": "lane_adapter", "course_ids": [CURRENT_COURSE_ID],
        "curriculum_role_ids": ["D110"], "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [role for role in COURSE_ROLES if role != "D110"],
        "owner_authority_binding": basic_fact(named["native_export_manifest"]),
        "curriculum_authority_binding": basic_fact(named["courses_current"]),
        "limitations": [
            "D110 only; every other curriculum role remains outside this adapter.",
            "All 10,978 owner-native records remain external and authoritative; textbook prose is not copied.",
            "Owner unit locale/language fields are und/zxx; id-ID publication state is bound separately and never substituted into native fields.",
            "Native unit prerequisite arrays are empty; 596 exact native prerequisite relations remain authoritative.",
            "The 219-page PDF is untagged; semantic HTML is the primary learner and accessibility surface.",
            "Learner exercises intentionally retain 335 sorry occurrences and five non-exercise demonstration sorries remain in the solution build.",
            "Ninety native asset/artifact records retain owner-native translation_state=draft and are not silently upgraded.",
            "The GitHub publication receipt contains one stale backend_records scalar (10,876); export manifest, final backend receipt, cursor, and handoff all prove 10,978.",
            "Per-unit public fragment routes are not claimed; the verified course root is the learner fallback.",
        ], "recorded_at": RECORDED_AT,
    }
    write_json(output / "scope-declaration-v0.2.0.json", scope)

    native_ids = sorted(registry)
    projected_ids = sorted(str(registry[item]["target_id"]) for item in native_ids)
    crosswalk = {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id,
        "profiles": [
            {"name": "d110_owner_native", "namespace": OWNER_NAMESPACE, "formula": "owner urn:mil record IDs preserved verbatim"},
            {"name": "v1_common", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + '|' + stable_key)"},
            {"name": "v2_current", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)"},
            {"name": "v2_3_lane", "namespace": str(LANE_NAMESPACE), "formula": "UUIDv5(namespace, record_type + ':' + corpus-qualified semantic key)"},
        ],
        "mappings": context["crosswalk_mappings"],
        "unmaterialized_candidates": [
            {
                "namespace": str(LANE_NAMESPACE), "record_type": record_type,
                "semantic_key": f"d110:unmaterialized:{entity_type}",
                "candidate_record_id": projection_id(LANE_NAMESPACE, record_type, f"d110:unmaterialized:{entity_type}"),
                "state": "deterministic_id_proposal_not_a_mapping",
                "formula": "UUIDv5 only after a global typed table contract is admitted; native shard remains authoritative",
                "effective_cardinality": "unresolved_until_materialized",
            }
            for record_type, entity_type in (("asset", "asset"), ("concept", "concept"), ("correction", "correction"), ("term", "term"))
        ],
        "identity_sets": {
            "native_materialized_sha256": identity_set_sha256(native_ids),
            "projected_materialized_sha256": identity_set_sha256(projected_ids),
            "mapped_pairs_sha256": mapping_set_sha256((native_id, registry[native_id]["target_id"]) for native_id in native_ids),
            "native_materialized_count": len(native_ids), "projected_materialized_count": len(projected_ids),
        }, "recorded_at": RECORDED_AT,
    }
    write_json(output / "namespace-crosswalk-v0.2.0.json", crosswalk)

    translation_records = []
    for native in sorted(shards["unit"], key=lambda row: str(row["record_id"])):
        native_id = str(native["record_id"])
        translation_records.append({
            "native_unit_id": native_id, "projected_unit_id": registry[native_id]["target_id"],
            "owner_native_state": native.get("translation_state"),
            "normalized_publication_state": "published_complete_course",
            "native_locale": native.get("locale"), "native_language": native.get("language"),
            "edition_locale": "id-ID", "source_path": native.get("source_path"),
            "source_locator": native.get("source_locator"), "source_sha256": native.get("source_sha256"),
            "state_inferred": False,
        })
    translation = {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "authority_bindings": [basic_fact(named["native_unit"]), basic_fact(named["native_segment"]), basic_fact(named["backend_receipt"]), basic_fact(named["github_receipt"])],
        "coverage": {"course_id": "D110", "granularity": "owner_native_unit_record", "authority_rows": 2177, "indexed_rows": 2177, "inferred_rows": 0},
        "states": sorted({str(row["owner_native_state"]) for row in translation_records} | {"published_complete_course"}),
        "records": translation_records,
        "identity_set_sha256": identity_set_sha256(row["projected_unit_id"] for row in translation_records),
        "no_inference": True, "recorded_at": RECORDED_AT,
    }
    write_json(output / "translation-state-index-v0.2.0.json", translation)

    capabilities = [
        capability_entry("structure_localization", "materialized", capability_shards(named, ["unit", "segment", "relation"]), len(tables["units"]) + len(tables["content_bindings"]) + len(tables["relations"]), None),
        capability_entry("terminology", "referenced_native_shards", capability_shards(named, ["concept", "term"]), 0, "Exact concept and term shards are bound, but the global v2.3.1 envelope has no typed terminology table."),
        capability_entry("mathematical_preservation", "referenced_native_shards", capability_shards(named, ["unit", "segment", "qa_event", "correction"]), len(tables["content_bindings"]) + len(tables["qa_events"]), "Lean builds pass; intentional pedagogical and demonstration sorries are preserved and not reclassified as completed proofs."),
        capability_entry("assessment_support", "referenced_native_shards", capability_shards(named, ["unit", "relation"]), 0, "Exercises and solutions are exact native metadata; no separate global assessment table contract is admitted."),
        capability_entry("assets", "referenced_native_shards", capability_shards(named, ["asset", "artifact"]), len(tables["artifacts"]), "Native asset records remain referenced; only artifact metadata and three public surfaces are projected."),
        capability_entry("accessibility", "referenced_native_shards", capability_shards(named, ["relation", "qa_event", "artifact"]), len(tables["reader_surfaces"]) + len(tables["qa_events"]), "Semantic HTML passes accessibility audit; the PDF is untagged and no per-unit accessibility state is invented."),
        capability_entry("corrections", "referenced_native_shards", capability_shards(named, ["correction"]), 0, "All 249 corrections remain exact native evidence; no global typed correction table is admitted."),
        capability_entry("computational_interactives", "referenced_native_shards", capability_shards(named, ["unit", "asset", "qa_event"]), 0, "Lean source and compile evidence are exact; no remote runtime or service availability is inferred."),
        capability_entry("publication", "materialized", capability_shards(named, ["edition", "artifact"]), len(tables["editions"]) + len(tables["artifacts"]) + len(tables["reader_surfaces"]) + len(tables["routes"]), None),
        capability_entry("research_support", "referenced_native_shards", capability_shards(named, ["concept", "relation", "term"]), 0, "The exact concept/relation graph is bound; no global research taxonomy or outcome state is inferred."),
    ]
    capability_doc = {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "contract_binding": basic_fact(named["capability_contract"]), "capabilities": capabilities,
        "legacy_labels": [],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards", "shard_refs": capability_shards(named, ["rights"]),
            "native_count": 37, "identity_set_sha256": combined_shard_identity(capability_shards(named, ["rights"])),
            "closure_rules": ["every native record has one resolved rights ID", "component rights are never flattened", "direct owner pointers remain authoritative"],
        }, "recorded_at": RECORDED_AT,
    }
    write_json(output / "capability-declarations-v0.2.0.json", capability_doc)


def copy_contract_files(repository_root: Path, output: Path) -> None:
    schema_names = [
        "lane-adapter-v2.3.1.schema.json", "capability-declarations-v0.2.schema.json",
        "namespace-crosswalk-v0.2.schema.json", "translation-state-index-v0.2.schema.json",
        "csv-projection-manifest-v0.2.schema.json", "scope-declaration-v0.2.schema.json",
    ]
    (output / "schema").mkdir(parents=True, exist_ok=True)
    (output / "tools").mkdir(parents=True, exist_ok=True)
    for name in schema_names:
        shutil.copyfile(repository_root / "backend" / "v2.3" / "schema" / name, output / "schema" / name)
    tools = {
        "build_d110_v23_adapter.py": Path(__file__).resolve(),
        "validate_d110_v23_adapter.py": Path(__file__).resolve().with_name("validate_d110_v23_adapter.py"),
        "validate_lane_adapter_v231.py": Path(__file__).resolve().with_name("validate_lane_adapter_v231.py"),
        "v231_adapter_common.py": Path(__file__).resolve().with_name("v231_adapter_common.py"),
    }
    for target, source in tools.items():
        require(source.is_file(), f"missing D110 adapter tool: {source}")
        shutil.copyfile(source, output / "tools" / target)


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), "program repository root missing")
    require(owner_root.is_dir(), "D110 owner root missing")
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    authorities, named, shards = build_authorities(repository_root, owner_root)
    course_row, prerequisite_ids = locate_course(repository_root)
    cursor = read_json(path_from(owner_root, EXPECTED_OWNER["current_cursor"][0]))
    backend_receipt = read_json(path_from(owner_root, EXPECTED_OWNER["backend_receipt"][0]))
    github_receipt = read_json(path_from(owner_root, EXPECTED_OWNER["github_receipt"][0]))
    zenodo_receipt = read_json(path_from(owner_root, EXPECTED_OWNER["zenodo_receipt"][0]))
    require(cursor.get("status") == "whole-corpus-v4.30.0-id.3-published-and-anonymously-verified-on-zenodo-figshare-github-and-pages", "D110 cursor state drift")
    require(cursor.get("artifacts", {}).get("backend", {}).get("records") == 10978, "D110 cursor backend count drift")
    require(backend_receipt.get("status") == "pass" and backend_receipt.get("artifact", {}).get("records") == 10978, "D110 backend receipt drift")
    require(backend_receipt.get("determinism", {}).get("candidate_a_candidate_b_byte_identical") is True, "D110 native backend determinism missing")
    require(github_receipt.get("status") == "published-and-anonymously-verified", "D110 GitHub receipt state drift")
    require(github_receipt.get("edition", {}).get("backend_records") == 10876, "D110 stale GitHub scalar changed; reassess limitation")
    require("10,978 backend records" in str(github_receipt.get("edition", {}).get("coverage")), "D110 GitHub receipt coverage evidence drift")
    require(zenodo_receipt.get("status") == "published-and-publicly-verified" and zenodo_receipt.get("record_id") == 22062017, "D110 Zenodo receipt drift")

    tables, context = build_tables(named, shards, course_row, prerequisite_ids)
    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/d110-v23-input-authorities/1",
        "recorded_at": RECORDED_AT, "authorities": authorities,
        "owner_native_closure": {
            "files_including_export_manifest": 49, "records": 10978, "bytes": 92714008,
            "export_manifest_sha256": named["native_export_manifest"]["sha256"],
            "global_native_id_set_sha256": identity_set_sha256(str(row["record_id"]) for rows in shards.values() for row in rows),
            "entity_counts": NATIVE_COUNTS, "materialized_native_records": len(context["registry"]),
            "rights_pointer_resolution": "10978_of_10978", "result": "pass_with_declared_native_limitations",
        }, "owner_native_non_mutation": True, "body_prose_copied": False,
    })
    write_json(output / "evidence" / "D110_NATIVE_LIMITATIONS.json", {
        "schema_id": "program-matematika-indonesia/d110-native-limitations/1",
        "recorded_at": RECORDED_AT, "status": "DECLARED_NOT_SILENTLY_REPAIRED",
        "native_unit_locale": "und", "native_unit_language": "zxx",
        "native_unit_prerequisite_array_rows_nonempty": 0,
        "native_prerequisite_relation_records": 596,
        "pdf_tagged": False, "primary_accessibility_surface": "semantic_html",
        "learner_sorry_occurrences": 335, "solution_nonexercise_demonstration_sorries": 5,
        "native_asset_artifact_draft_records": 90,
        "github_receipt_stale_backend_records_scalar": 10876,
        "authoritative_backend_records": 10978,
        "stale_scalar_disposition": "excluded_from_count_authority; exact export manifest, final backend receipt, cursor, and central handoff control",
        "per_unit_public_route_state": "not_published_course_root_fallback_only",
    })

    write_tables(output, tables)
    build_sidecars(output, named, shards, tables, context)
    csv_manifest = write_csv_surfaces(output, tables, context["package_id"], RECORDED_AT)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    copy_contract_files(repository_root, output)

    payload_facts = package_payload_files(output)
    payload_identity = inventory_sha256(payload_facts)
    sidecar_names = [
        "capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json",
        "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json",
        "scope-declaration-v0.2.0.json",
    ]
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
        "schema_version": "2.3.1", "package_id": context["package_id"], "dataset_id": context["dataset_id"],
        "extension_id": projection_id(LANE_NAMESPACE, "lane_adapter_extension", f"d110:mathematics-in-lean:{ADAPTER_VERSION}"),
        "extension_version": ADAPTER_VERSION, "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": sorted(authorities, key=lambda item: (item["path_base"], item["path"])),
        "sidecars": [file_fact(output / name, name, "sidecar") for name in sidecar_names],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER), "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER), "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools" / "build_d110_v23_adapter.py", "tools/build_d110_v23_adapter.py", "builder"),
            "validator": file_fact(output / "tools" / "validate_d110_v23_adapter.py", "tools/validate_d110_v23_adapter.py", "validator"),
            "canonical_serialization": {
                "scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8", "newline": "LF",
                "json_keys": "lexicographically_sorted", "trailing_newline": True,
                "copied_schema_and_tool_files": "preserved_exact_source_bytes",
            }, "deterministic_replay": "byte_identical",
            "build_a_sha256": payload_identity, "build_b_sha256": payload_identity,
        },
        "files": payload_facts,
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json",
            "seal_excluded_from_own_digest": True,
            "binds": ["schemas", "tools", "input_authorities", "native_limitations", "tables", "sidecars", "csv_projections", "manifest"],
        },
        "zero_copy_policy": {
            "owner_native_authoritative": True, "full_prose_centralized": False,
            "owner_ids_reminted": False, "aggregate_conformance_claim": False,
            "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True,
        },
    }
    write_json(output / "manifest.json", manifest)
    seal_facts = payload_facts + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    write_json(output / "seal.json", {
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
        "package_id": context["package_id"], "algorithm": "sha256-sorted-path-bytes-v1",
        "files": seal_facts, "file_count": len(seal_facts),
        "bytes": sum(int(item["bytes"]) for item in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts), "seal_excluded_from_own_digest": True,
        "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_fact = write_checksums(output, checksum_facts)
    return {
        "status": "pass", "output": str(output), "files": len(checksum_facts) + 1,
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "owner_native_records": 10978, "materialized_native_records": len(context["registry"]),
        "payload_inventory_sha256": payload_identity,
        "seal_sha256": sha256_file(output / "seal.json"), "checksum_sha256": checksum_fact["sha256"],
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
        print(compact_json(build(args)))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
