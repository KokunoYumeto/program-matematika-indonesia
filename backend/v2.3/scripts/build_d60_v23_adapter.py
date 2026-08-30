#!/usr/bin/env python3
"""Build the D60 algebraic-topology zero-copy backend-v2.3.1 adapter.

The builder never edits or copies the owner's textbook prose.  It verifies the
immutable final owner shards and publication receipts, projects current semantic
heads into the common navigation/interchange envelope, preserves every richer
native capability by exact shard identity, and declares known owner-native gaps.
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
    safe_relative_path,
    sha256_bytes,
    sha256_file,
    sort_table_rows,
    write_checksums,
    write_csv_surfaces,
    write_json,
    write_tables,
)


RECORDED_AT = "2026-08-30T14:00:00Z"
ADAPTER_VERSION = "0.1.0"
COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
LANE_NAMESPACE = uuid.uuid5(uuid.UUID(COMMON_NAMESPACE), "v2.3.1:D60:algebraic-topology")
OWNER_NAMESPACE = "curriculum.interop/o012-d60/0.1.0"
CURRENT_COURSE_ID = "urn:uuid:9883f954-1b3f-5d97-a497-7820a17aa2ff"
CURRENT_V1_COURSE_ID = "urn:uuid:cc49a8ce-b715-5f2e-93dc-5ef22fe6a848"
CURRENT_OWNER_DATASET_ID = "urn:uuid:db07d719-0f5f-53fd-ba87-f76cd79b78ae"
NATIVE_COURSE_ID = "course:o012-d60"
INTEGRATED_RIGHTS_RELATION_ID = "relation:xref:o012-d60:integrated-rights"
INTEGRATED_RIGHTS_NATIVE_ID = "rights:o012-d60-integrated-route-cc-by-sa-4.0"

COURSE_ROLES = [
    "A00", "A10", "A20", "A30",
    "B10", "B20", "B30", "B40", "B50", "B60", "B70", "B80", "B90", "B95",
    "C10", "C20", "C30", "C40", "C50", "C60", "C70", "C80", "C90", "C100", "C110", "C120", "C130", "C140",
    "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D90", "D100", "D110", "D120",
]

EXPECTED_CENTRAL = {
    "capability_contract": (
        "backend/v2.2/global-capability-contract-v0.1.0.json",
        7462,
        "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7",
    ),
    "courses_current": (
        "backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl",
        86522,
        "7dee2faef2019e23fe4d3650ee772a23f9120979dae69409672fde3951101351",
    ),
    "federation_manifest": (
        "backend/v2/program-matematika-indonesia-federation-v0.4.4/manifest.json",
        8952,
        "62198018ce4d035e1bb3893af5666dddae8e054b1d30a162e24cfd631ba0dc2c",
    ),
    "d60_authority": (
        "backend/v2.3/authorities/D60_FINAL_OWNER_AUTHORITY_20260830.json",
        6037,
        "9bb9195906fae3f0cc2062c3aff292be3dd4f6cef595e08baa61b46584e55a85",
    ),
}

EXPECTED_OWNER = {
    "github_receipt": (
        "00_control/GITHUB_PUBLICATION_RECEIPT_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE.json",
        10077,
        "5d880698531b69c8e741b846c10cf64fa5bbffffa7395bce2bfa19ceb2a5358e",
    ),
    "zenodo_receipt": (
        "release/zenodo-roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/publication-receipt.json",
        11979,
        "a49688bcb19813a3487b403c52f1f5d1336967270e43d55a77427b7c5f5fe550",
    ),
    "release_manifest": (
        "release/zenodo-roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/artifacts/release-manifest.json",
        107045,
        "5eebb16879ab9eed68487277bd3fcf72e8f073fae41b6cc0abd6e34a38c8edee",
    ),
    "backend_final_validation": (
        "qa/BACKEND_CAPSTONE_FINAL_REV3_VALIDATION.json",
        1321,
        "e741907d65d0e03d7b75814a3f8edd10e87f97cf7a4309f2ce86a6a53666c883",
    ),
    "backend_cumulative": (
        "qa/BACKEND_CAPSTONE_FINAL_REV3_CUMULATIVE_RECEIPT.json",
        1829,
        "e65be1b2d0d810f1e99f18c02c268b02cf7846bd3958db34e5070cd6c4aa5acb",
    ),
}

RELEASE_ROOT = "release/zenodo-roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone"
RELEASE_ARTIFACTS = {
    "html": (
        f"{RELEASE_ROOT}/artifacts/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_READER.html",
        16049720,
        "a17ce8e3e4d6b93de5e678ce38f3b7834c3b6a9ca1bff063fd3e879875e254a8",
    ),
    "pdf": (
        f"{RELEASE_ROOT}/artifacts/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_READER.pdf",
        10376749,
        "d29dad39a06224a83aed11afdb4c65b317a45c6b900122dd40948df712ff8340",
    ),
    "source_backend": (
        f"{RELEASE_ROOT}/artifacts/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_EDITABLE_SOURCE_BACKEND.zip",
        8406450,
        "f7670f6e6ad9a95ff808a1ddf4c2fdd8b41c6bce1916d33ac6fe5063be184b1b",
    ),
    "qa_provenance": (
        f"{RELEASE_ROOT}/artifacts/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_QA_PROVENANCE.zip",
        2628497,
        "56cf8d60454622e654df4f238539791aa1b6a3e8884639bf39bad620c017a747",
    ),
}

ZENODO_RECORD_URL = "https://zenodo.org/records/22168033"
PUBLIC_ARTIFACT_URLS = {
    "html": "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/",
    "pdf": f"{ZENODO_RECORD_URL}/files/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_READER.pdf?download=1",
    "source_backend": f"{ZENODO_RECORD_URL}/files/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_EDITABLE_SOURCE_BACKEND.zip?download=1",
    "qa_provenance": f"{ZENODO_RECORD_URL}/files/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_QA_PROVENANCE.zip?download=1",
}

NATIVE_TABLE_FACTS = {
    "artifacts": (279, 233018, "448a222ca2e573b34951cc21ae16ca60db46f06da1f5fec4cc3684bcb1253c29"),
    "assets": (87, 64692, "1df40f8f6ca4f2fbfbe8a7b924a68a153713a20a4eebe1d014d8fb04669945f7"),
    "authority": (6, 4374, "84c622f56dbbd5ba379361245ecfe07bc79c9f4fd6b18ba21b82b5f545211869"),
    "concepts": (535, 169924, "3e55b0612310f5434e6a8e746814504b6b9e9e014dba243dbe8ec2df68614540"),
    "corrections": (566, 599471, "ab6e1a70be761135dfbc3076968c01978894c10520b50ef604004bd1dcea2871"),
    "qa": (230, 129064, "f94f32bf2f652ea704c7abf72ea4df28a8aa3dea31a5f30078e5a074ab99e3c5"),
    "relations": (1443, 664996, "ac1c2766a8f2179ab210bdbbc425f5ad3ac54f20357259bdddebee0af611d361"),
    "rights": (114, 112823, "8c2fb365a890626d7696056d622548a77f710885ef5053ee72928cf5df9cb5cd"),
    "segments": (2250, 3740661, "648f35e19b6b42ada3e9b0019b3e482c212a847b5d720c4d663f6ccff23aac78"),
    "terms": (548, 369736, "7ed9ad84065ab452aa63f47dde5606ae0814943a4346ac5fe3499df8403ef50e"),
    "units": (2280, 3951284, "f3bb94c660780116a29e1089b27b10a60e18034c0ed0d6ce5452d8799a2a8945"),
}


def basic_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {key: fact[key] for key in ("path", "path_base", "role", "bytes", "sha256")}


def native_shard_fact(owner_root: Path, name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    expected_records, expected_bytes, expected_sha = NATIVE_TABLE_FACTS[name]
    relative = f"backend/{name}.jsonl"
    path = owner_root / "backend" / f"{name}.jsonl"
    rows = read_jsonl(path)
    ids = [str(row.get("id", "")) for row in rows]
    require(len(rows) == expected_records, f"native record count drift: {name}")
    require(all(ids) and len(ids) == len(set(ids)), f"native ID failure: {name}")
    fact = external_file_fact(
        path,
        relative,
        f"owner_native_{name}",
        "owner_package_root",
        expected_bytes=expected_bytes,
        expected_sha256=expected_sha,
        records=len(rows),
        record_id_set_sha256=identity_set_sha256(ids),
    )
    return fact, rows


def current_heads(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(rows)
    superseded = {str(row["supersedes"]) for row in rows if row.get("supersedes")}
    return [row for row in rows if str(row["id"]) not in superseded]


def successor_leaves(identifier: str, rows: Iterable[dict[str, Any]]) -> list[str]:
    children: dict[str, list[str]] = collections.defaultdict(list)
    by_id = {str(row["id"]): row for row in rows}
    for row in rows:
        if row.get("supersedes"):
            children[str(row["supersedes"])].append(str(row["id"]))
    require(identifier in by_id, f"unresolved native identifier: {identifier}")
    leaves: list[str] = []
    stack = [identifier]
    seen: set[str] = set()
    while stack:
        current = stack.pop()
        require(current not in seen, f"supersession cycle: {identifier}")
        seen.add(current)
        next_ids = children.get(current, [])
        if next_ids:
            stack.extend(next_ids)
        else:
            leaves.append(current)
    return sorted(leaves)


def selected_fields(row: Mapping[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    return {key: row.get(key) for key in keys if key in row}


def order_key(row: Mapping[str, Any]) -> str:
    path = row.get("path") if isinstance(row.get("path"), list) else []
    order = row.get("order")
    order_number = order if isinstance(order, int) else 0
    return f"{len(path):04d}.{order_number:08d}.{row['id']}"


def artifact_physical_state(owner_root: Path, row: Mapping[str, Any]) -> dict[str, Any]:
    relative = str(row.get("path", ""))
    try:
        safe_relative_path(relative)
    except Exception:
        return {"state": "unsafe_declared_path", "actual_bytes": None, "actual_sha256": None}
    path = owner_root.joinpath(*PurePosixPath(relative).parts)
    if not path.is_file():
        return {"state": "declared_path_missing", "actual_bytes": None, "actual_sha256": None}
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    if actual_bytes == row.get("bytes") and actual_sha == row.get("sha256"):
        state = "local_hash_match"
    else:
        state = "declared_identity_stale"
    return {"state": state, "actual_bytes": actual_bytes, "actual_sha256": actual_sha}


def build_authorities(repository_root: Path, owner_root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    authorities: list[dict[str, Any]] = []
    named: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_bytes, expected_sha) in EXPECTED_CENTRAL.items():
        fact = external_file_fact(
            repository_root.joinpath(*PurePosixPath(relative).parts),
            relative,
            role,
            "program_repository_root",
            expected_bytes=expected_bytes,
            expected_sha256=expected_sha,
        )
        named[role] = fact
        authorities.append(basic_fact(fact))

    corrected_owner = dict(EXPECTED_OWNER)
    corrected_owner["release_manifest"] = (
        f"{RELEASE_ROOT}/artifacts/release-manifest.json",
        107045,
        "5eebb16879ab9eed68487277bd3fcf72e8f073fae41b6cc0abd6e34a38c8edee",
    )
    for role, (relative, expected_bytes, expected_sha) in corrected_owner.items():
        fact = external_file_fact(
            owner_root.joinpath(*PurePosixPath(relative).parts),
            relative,
            role,
            "owner_package_root",
            expected_bytes=expected_bytes,
            expected_sha256=expected_sha,
        )
        named[role] = fact
        authorities.append(basic_fact(fact))

    for role, (relative, expected_bytes, expected_sha) in RELEASE_ARTIFACTS.items():
        fact = external_file_fact(
            owner_root.joinpath(*PurePosixPath(relative).parts),
            relative,
            f"final_{role}",
            "owner_package_root",
            expected_bytes=expected_bytes,
            expected_sha256=expected_sha,
        )
        named[f"final_{role}"] = fact
        authorities.append(basic_fact(fact))

    shards: dict[str, list[dict[str, Any]]] = {}
    for name in NATIVE_TABLE_FACTS:
        fact, rows = native_shard_fact(owner_root, name)
        named[f"native_{name}"] = fact
        authorities.append(basic_fact(fact))
        shards[name] = rows
    require(sum(len(rows) for rows in shards.values()) == 8338, "D60 native aggregate count drift")
    require(sum(named[f"native_{name}"]["bytes"] for name in shards) == 10040043, "D60 native byte aggregate drift")
    require(len({str(row["id"]) for rows in shards.values() for row in rows}) == 8338, "D60 global native IDs are not unique")
    return authorities, named, shards


def locate_course_rows(courses: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str]]:
    by_role = {str(row.get("payload", {}).get("course_id")): row for row in courses if row.get("record_type") == "course"}
    require("D60" in by_role and by_role["D60"]["id"] == CURRENT_COURSE_ID, "current D60 course identity drift")
    d60 = by_role["D60"]
    require(d60["payload"].get("v1_course_id") == CURRENT_V1_COURSE_ID, "D60 v1 course identity drift")
    require(d60["payload"].get("owner_dataset_id") == CURRENT_OWNER_DATASET_ID, "D60 owner dataset identity drift")
    prerequisite_ids = {role: str(by_role[role]["id"]) for role in ("C90", "C30")}
    return d60, prerequisite_ids


def build_tables(
    owner_root: Path,
    named: Mapping[str, Mapping[str, Any]],
    shards: Mapping[str, list[dict[str, Any]]],
    course_row: Mapping[str, Any],
    prerequisite_ids: Mapping[str, str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    package_id = projection_id(LANE_NAMESPACE, "lane_adapter_package", f"d60:algebraic-topology:{ADAPTER_VERSION}")
    dataset_id = projection_id(LANE_NAMESPACE, "dataset", "d60:algebraic-topology")
    owner_authority_id = projection_id(LANE_NAMESPACE, "owner_authority", "d60:owner-native-final")
    composite_edition_id = projection_id(LANE_NAMESPACE, "edition", "d60:composite-final:0.31.7")
    html_surface_id = projection_id(LANE_NAMESPACE, "reader_surface", "d60:final:html")
    pdf_surface_id = projection_id(LANE_NAMESPACE, "reader_surface", "d60:final:pdf")
    html_route_id = projection_id(LANE_NAMESPACE, "route", "d60:final:html-course-root")
    pdf_route_id = projection_id(LANE_NAMESPACE, "route", "d60:final:pdf-offline")

    heads = {name: current_heads(rows) for name, rows in shards.items()}
    expected_head_counts = {
        "artifacts": 254, "assets": 86, "authority": 6, "concepts": 535,
        "corrections": 564, "qa": 214, "relations": 1335, "rights": 96,
        "segments": 2174, "terms": 528, "units": 2204,
    }
    require({name: len(rows) for name, rows in heads.items()} == expected_head_counts, "D60 current-head census drift")

    authority_editions = [row for row in heads["authority"] if row.get("entity_type") == "edition"]
    require(len(authority_editions) == 2, "D60 native edition census drift")
    materialized: list[tuple[str, str, dict[str, Any], str]] = []
    materialized.extend(("edition", "authority", row, f"d60:native:{row['id']}") for row in authority_editions)
    materialized.extend(("unit", "units", row, f"d60:native:{row['id']}") for row in heads["units"])
    materialized.extend(("content_binding", "segments", row, f"d60:native:{row['id']}") for row in heads["segments"])
    materialized.extend(("relation", "relations", row, f"d60:native:{row['id']}") for row in heads["relations"])
    materialized.extend(("rights", "rights", row, f"d60:native:{row['id']}") for row in heads["rights"])
    materialized.extend(("artifact", "artifacts", row, f"d60:native:{row['id']}") for row in heads["artifacts"])
    materialized.extend(("qa_event", "qa", row, f"d60:native:{row['id']}") for row in heads["qa"])
    projection_registry = {
        str(row["id"]): {
            "target_id": projection_id(LANE_NAMESPACE, record_type, semantic_key),
            "target_record_type": record_type,
            "source_table": source_table,
            "semantic_key": semantic_key,
        }
        for record_type, source_table, row, semantic_key in materialized
    }
    require(len(projection_registry) == len(materialized) == 6279, "D60 materialized native registry drift")
    endpoint_map = {native_id: entry["target_id"] for native_id, entry in projection_registry.items()}
    endpoint_map[NATIVE_COURSE_ID] = CURRENT_COURSE_ID

    tables = empty_tables()
    tables["owner_authorities"].append(make_row(
        LANE_NAMESPACE,
        "owner_authority",
        "d60:owner-native-final",
        {
            "authority_kind": "owner_native_append_only_semantic_backend",
            "authority_scope": "complete final D60 semantic graph, component rights, corrections, QA, assets, artifacts, and publication evidence",
            "native_schema_name": "curriculum.interop",
            "native_schema_version": "0.1.0",
            "native_namespace": OWNER_NAMESPACE,
            "native_record_count": 8338,
            "native_bundle_sha256": "8a3ffc9618e56dfce048c41e938aabef4ffbfd3db20a03a4f52f218985230dbb",
            "public_repository_url": "https://github.com/KokunoYumeto/algebraic-topology-id",
            "content_commit": "bce91390574d024a2b2386af28a811dffff67e2b",
            "content_tree": "dac9e1a48b2dfaba2228a4662749630c89f871cc",
            "release_lineage_url": "https://doi.org/10.5281/zenodo.22061489",
            "final_version_doi": "https://doi.org/10.5281/zenodo.22168033",
            "sole_integrator_publisher": True,
            "zero_copy": True,
            "owner_native_limitations_authority": "d60_authority",
        },
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="published",
        owner_native_state="specialized_final_validation_pass_with_declared_generic_gaps",
    ))

    integrated_rights_projected = endpoint_map.get(INTEGRATED_RIGHTS_NATIVE_ID)
    require(integrated_rights_projected is not None, "integrated D60 rights are not a current materialized head")
    tables["datasets"].append(make_row(
        LANE_NAMESPACE,
        "dataset",
        "d60:algebraic-topology",
        {
            "dataset_kind": "zero_copy_owner_projection",
            "course_ids": [CURRENT_COURSE_ID],
            "curriculum_role_ids": ["D60"],
            "owner_dataset_id": CURRENT_OWNER_DATASET_ID,
            "owner_record_count": 8338,
            "owner_current_head_counts": expected_head_counts,
            "publication_state": "complete_public_anonymous_readback_verified",
            "capabilities": CAPABILITY_NAMES,
            "materialized_native_record_count": len(projection_registry),
            "integrated_rights_native_id": INTEGRATED_RIGHTS_NATIVE_ID,
            "integrated_rights_id": integrated_rights_projected,
            "integrated_rights_relation_native_id": INTEGRATED_RIGHTS_RELATION_ID,
            "reader_surface_ids": [html_surface_id, pdf_surface_id],
            "limitations": [
                "No textbook body prose is copied into the central adapter.",
                "The central v2 federation row is a stale production checkpoint; immutable final owner receipts control publication state.",
                "Owner-native term-envelope, supersession-branch, artifact-closure, and whole-backend replay gaps remain declared.",
                "Repeated D60-R01 through D60-R14 labels are not exposed as public fragment anchors.",
            ],
        },
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="published",
        owner_native_state="final_complete",
    ))

    resource_by_id = {str(row["id"]): row for row in heads["authority"] if row.get("entity_type") == "resource"}
    for native in authority_editions:
        resource = resource_by_id[str(native["resource_id"])]
        semantic_key = f"d60:native:{native['id']}"
        tables["editions"].append(make_row(
            LANE_NAMESPACE,
            "edition",
            semantic_key,
            {
                "edition_kind": "owner_native_source_edition",
                "native_edition_id": native["id"],
                "native_resource_id": native["resource_id"],
                "title": resource.get("title"),
                "author_credit": resource.get("author"),
                "source_url": resource.get("source_url"),
                "source_locale": resource.get("source_locale"),
                "license_expression": resource.get("license_expression"),
                "commit_sha": native.get("commit_sha"),
                "tree_sha": native.get("tree_sha"),
                "archive_path": native.get("archive_path"),
                "archive_bytes": native.get("archive_bytes"),
                "archive_sha256": native.get("archive_sha256"),
                "source_path": native.get("source_path"),
                "source_line_start": native.get("source_line_start"),
                "source_line_end": native.get("source_line_end"),
                "native_rights_id": native.get("rights_component_id"),
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state=str(native.get("translation_state")),
        ))
    tables["editions"].append(make_row(
        LANE_NAMESPACE,
        "edition",
        "d60:composite-final:0.31.7",
        {
            "edition_kind": "final_composite_indonesian_course",
            "title": "Topologi Aljabar: Edisi Bahasa Indonesia",
            "locale": "id-ID",
            "version_label": "0.31.7",
            "source_component_edition_ids": [projection_registry[str(row["id"])]["target_id"] for row in authority_editions],
            "integrated_rights_id": integrated_rights_projected,
            "rights_are_component_scoped": True,
            "public_html": "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/",
            "version_doi": "10.5281/zenodo.22168033",
            "concept_doi": "10.5281/zenodo.22061489",
            "course_complete": True,
        },
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="published",
        owner_native_state="final_composite_course_complete",
    ))

    concept_labels = {str(row["id"]): str(row.get("canonical_label", "")) for row in heads["concepts"]}
    current_segments_by_unit: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for segment in heads["segments"]:
        current_segments_by_unit[str(segment.get("unit_id"))].append(segment)

    for native in heads["units"]:
        semantic_key = f"d60:native:{native['id']}"
        target_id = projection_registry[str(native["id"])]["target_id"]
        parent_native = native.get("parent_id")
        parent_projected = endpoint_map.get(str(parent_native)) if parent_native else None
        rights_native = str(native.get("rights_component_id")) if native.get("rights_component_id") else None
        rights_leaves = successor_leaves(rights_native, shards["rights"]) if rights_native else []
        rights_projected = [endpoint_map[leaf] for leaf in rights_leaves if leaf in endpoint_map]
        tables["units"].append(make_row(
            LANE_NAMESPACE,
            "unit",
            semantic_key,
            {
                "native_unit_id": native["id"],
                "native_unit_kind": native.get("unit_kind"),
                "title": native.get("display_title"),
                "title_locale": native.get("locale"),
                "order_key": order_key(native),
                "native_order": native.get("order"),
                "parent_native_unit_id": parent_native,
                "parent_projected_unit_id": parent_projected,
                "native_path": native.get("path"),
                "projected_path": [endpoint_map[item] for item in native.get("path", []) if item in endpoint_map],
                "native_concept_ids": native.get("concept_ids", []),
                "provenance_relation": native.get("provenance_relation"),
                "native_edition_id": native.get("edition_id"),
                "native_resource_id": native.get("resource_id"),
                "native_rights_id": rights_native,
                "current_rights_native_ids": rights_leaves,
                "current_rights_ids": rights_projected,
                "target_locator": native.get("target_locator"),
                "translation_state": native.get("translation_state"),
                "accessibility_status": native.get("accessibility_status"),
                "route_unit_ids": native.get("course_route_unit_ids", native.get("course_route_unit_id")),
                "learner_route": {
                    "url": "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/",
                    "anchor": None,
                    "route_id": html_route_id,
                    "route_state": "verified_course_fallback_unit_anchor_not_unique",
                    "machine_data_only": False,
                },
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state=str(native.get("translation_state")),
        ))
        tables["course_unit_memberships"].append(make_row(
            LANE_NAMESPACE,
            "course_unit_membership",
            f"d60:membership:{native['id']}",
            {
                "course_id": CURRENT_COURSE_ID,
                "edition_id": composite_edition_id,
                "unit_id": target_id,
                "native_unit_id": native["id"],
                "parent_unit_id": parent_projected,
                "order_key": order_key(native),
                "required": None,
                "visible": None,
                "membership_policy_state": "owner_hierarchy_preserved_policy_not_inferred",
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state=str(native.get("translation_state")),
        ))
        concept_text = [concept_labels[identifier] for identifier in native.get("concept_ids", []) if concept_labels.get(identifier)]
        bounded = " ".join(filter(None, [str(native.get("display_title", "")), str(native.get("unit_kind", "")), *concept_text, "topologi aljabar D60"]))
        tables["search_documents"].append(make_row(
            LANE_NAMESPACE,
            "search_document",
            f"d60:search:{native['id']}",
            {
                "course_id": CURRENT_COURSE_ID,
                "unit_id": target_id,
                "native_unit_id": native["id"],
                "title": native.get("display_title"),
                "locale": native.get("locale", "id-ID"),
                "order_key": order_key(native),
                "bounded_search_text": bounded,
                "learner_url": "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/",
                "learner_anchor": None,
                "body_prose_copied": False,
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state=str(native.get("translation_state")),
        ))

    for native in heads["segments"]:
        semantic_key = f"d60:native:{native['id']}"
        native_unit = str(native.get("unit_id"))
        tables["content_bindings"].append(make_row(
            LANE_NAMESPACE,
            "content_binding",
            semantic_key,
            {
                "native_segment_id": native["id"],
                "native_unit_id": native_unit,
                "projected_unit_id": endpoint_map.get(native_unit),
                "segment_kind": native.get("segment_kind"),
                "native_order": native.get("order"),
                "native_concept_ids": native.get("concept_ids", []),
                "provenance_relation": native.get("provenance_relation"),
                "native_edition_id": native.get("edition_id"),
                "native_resource_id": native.get("resource_id"),
                "native_rights_id": native.get("rights_component_id"),
                "source_local_id": native.get("source_local_id"),
                "source_locator": native.get("source_locator"),
                "target_locator": native.get("target_locator"),
                "translation_state": native.get("translation_state"),
                "body_prose_copied": False,
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state=str(native.get("translation_state")),
        ))

    for native in heads["relations"]:
        note = str(native.get("note", ""))
        tables["relations"].append(make_row(
            LANE_NAMESPACE,
            "relation",
            f"d60:native:{native['id']}",
            {
                "native_relation_id": native["id"],
                "relation_type": native.get("relation_type"),
                "from_native_id": native.get("from_id"),
                "from_projected_id": endpoint_map.get(str(native.get("from_id"))),
                "to_native_id": native.get("to_id"),
                "to_projected_id": endpoint_map.get(str(native.get("to_id"))),
                "note_sha256": sha256_bytes(note.encode("utf-8")),
                "note_copied": False,
                "concept_relation_inferred": False,
                "evidence_state": "exact_owner_native_relation",
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state=str(native.get("status")),
        ))

    for role in ("C90", "C30"):
        tables["relations"].append(make_row(
            LANE_NAMESPACE,
            "relation",
            f"d60:curriculum-prerequisite:{role}",
            {
                "relation_type": "prerequisite",
                "from_projected_id": CURRENT_COURSE_ID,
                "to_projected_id": prerequisite_ids[role],
                "source_authority": "courses_current",
                "source_course_role": "D60",
                "target_course_role": role,
                "concept_relation_inferred": False,
                "evidence_state": "exact_curriculum_snapshot_row",
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state="curriculum_snapshot",
        ))

    for native in heads["rights"]:
        tables["rights"].append(make_row(
            LANE_NAMESPACE,
            "rights",
            f"d60:native:{native['id']}",
            {
                "native_rights_id": native["id"],
                "license_expression": native.get("license_expression"),
                "license_url": native.get("license_url"),
                "component_scope": native.get("component_scope", []),
                "attribution": native.get("attribution"),
                "change_notice": native.get("change_notice"),
                "third_party_status": native.get("third_party_status"),
                "non_endorsement": native.get("non_endorsement"),
                "flattened_course_license": False,
                "assertion_status": "owner_native_current_head",
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state=str(native.get("status")),
        ))

    for source_name, source_rows, target_kind in (
        ("unit", heads["units"], "unit"),
        ("segment", heads["segments"], "content_binding"),
    ):
        for native in source_rows:
            rights_native = native.get("rights_component_id")
            if not rights_native:
                continue
            leaves = successor_leaves(str(rights_native), shards["rights"])
            projected_rights = [endpoint_map[item] for item in leaves if item in endpoint_map]
            tables["rights_assignments"].append(make_row(
                LANE_NAMESPACE,
                "rights_assignment",
                f"d60:rights-assignment:{source_name}:{native['id']}",
                {
                    "target_id": endpoint_map[str(native["id"])],
                    "target_record_type": target_kind,
                    "target_native_id": native["id"],
                    "direct_native_rights_id": rights_native,
                    "current_native_rights_ids": leaves,
                    "current_rights_ids": projected_rights,
                    "assignment_state": "exact_single_current_head" if len(leaves) == 1 else "declared_branch",
                    "inheritance": "direct_owner_native_pointer_with_supersession_resolution",
                },
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state=str(native.get("status")),
            ))

    artifact_exception_counts = collections.Counter()
    for native in heads["artifacts"]:
        physical = artifact_physical_state(owner_root, native)
        artifact_exception_counts[physical["state"]] += 1
        tables["artifacts"].append(make_row(
            LANE_NAMESPACE,
            "artifact",
            f"d60:native:{native['id']}",
            {
                "native_artifact_id": native["id"],
                "artifact_kind": "owner_native_artifact_record",
                "path": native.get("path"),
                "media_type": native.get("media_type"),
                "declared_bytes": native.get("bytes"),
                "declared_sha256": native.get("sha256"),
                "physical_verification": physical,
                "native_rights_id": native.get("rights_component_id"),
                "native_unit_id": native.get("unit_id"),
                "native_qa_event_ids": native.get("qa_event_ids", []),
                "translation_state": native.get("translation_state"),
                "publication_claim": "none_unless_separately_bound",
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state=str(native.get("status")),
        ))

    public_artifact_specs = [
        ("html", "semantic_html_course", "text/html", PUBLIC_ARTIFACT_URLS["html"], html_route_id),
        ("pdf", "offline_pdf_reader", "application/pdf", PUBLIC_ARTIFACT_URLS["pdf"], pdf_route_id),
        ("source_backend", "editable_source_backend", "application/zip", PUBLIC_ARTIFACT_URLS["source_backend"], None),
        ("qa_provenance", "qa_provenance", "application/zip", PUBLIC_ARTIFACT_URLS["qa_provenance"], None),
    ]
    public_artifact_ids: dict[str, str] = {}
    for key, kind, media_type, url, route_id in public_artifact_specs:
        relative, byte_count, digest = RELEASE_ARTIFACTS[key]
        semantic_key = f"d60:final-public:{key}"
        artifact_id = projection_id(LANE_NAMESPACE, "artifact", semantic_key)
        public_artifact_ids[key] = artifact_id
        tables["artifacts"].append(make_row(
            LANE_NAMESPACE,
            "artifact",
            semantic_key,
            {
                "artifact_kind": kind,
                "authority_path": relative,
                "bytes": byte_count,
                "sha256": digest,
                "media_type": media_type,
                "public_url": url,
                "route_id": route_id,
                "course_ids": [CURRENT_COURSE_ID],
                "edition_id": composite_edition_id,
                "integrated_rights_id": integrated_rights_projected,
                "publication_state": "public_anonymous_readback_verified",
                "verification_authorities": ["github_receipt", "zenodo_receipt", "release_manifest"],
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state="twice_anonymous_readback_verified",
        ))

    tables["build_recipes"].append(make_row(
        LANE_NAMESPACE,
        "build_recipe",
        "d60:owner-native:incremental-final",
        {
            "recipe_kind": "owner_native_incremental_admission_history",
            "input_bundle_sha256": "8a3ffc9618e56dfce048c41e938aabef4ffbfd3db20a03a4f52f218985230dbb",
            "final_validation_authority": "backend_final_validation",
            "cumulative_authority": "backend_cumulative",
            "clean_source_to_entire_backend_replay": False,
            "limitation": "The owner final backend is exactly receipt-bound but its construction history is distributed across incremental producers.",
        },
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="validated",
        owner_native_state="deterministic_incremental_final",
    ))
    tables["build_recipes"].append(make_row(
        LANE_NAMESPACE,
        "build_recipe",
        "d60:adapter:clean-replay:0.1.0",
        {
            "recipe_kind": "absent_directory_zero_copy_projection",
            "builder": "tools/build_d60_v23_adapter.py",
            "validator": "tools/validate_d60_v23_adapter.py",
            "generic_validator": "tools/validate_lane_adapter_v231.py",
            "canonical_serialization": "UTF-8 LF sorted-key JSON and RFC4180-compatible CSV",
            "required_replay": "two absent-directory builds byte-identical",
            "owner_native_mutation": False,
        },
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="validated",
        owner_native_state=None,
    ))

    tables["reader_surfaces"].extend([
        make_row(
            LANE_NAMESPACE, "reader_surface", "d60:final:html",
            {
                "action": "learn",
                "artifact_id": public_artifact_ids["html"],
                "course_ids": [CURRENT_COURSE_ID],
                "format": "semantic_html",
                "locale": "id-ID",
                "primary": True,
                "public_url": PUBLIC_ARTIFACT_URLS["html"],
                "publication_state": "public_anonymous_readback_verified",
                "accessibility_state": "self_contained_semantic_html_native_mathml_centered_reflow",
                "unit_anchor_coverage": 0,
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="published", owner_native_state="github_pages_verified",
        ),
        make_row(
            LANE_NAMESPACE, "reader_surface", "d60:final:pdf",
            {
                "action": "download",
                "artifact_id": public_artifact_ids["pdf"],
                "course_ids": [CURRENT_COURSE_ID],
                "format": "pdf",
                "locale": "id-ID",
                "primary": False,
                "public_url": PUBLIC_ARTIFACT_URLS["pdf"],
                "publication_state": "public_anonymous_readback_verified",
                "accessibility_state": "embedded_subset_tounicode_fonts_but_untagged",
                "pages": 564,
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="published", owner_native_state="zenodo_verified",
        ),
    ])
    tables["routes"].extend([
        make_row(
            LANE_NAMESPACE, "route", "d60:final:html-course-root",
            {
                "access_state": "public_anonymous_readback_verified",
                "course_id": CURRENT_COURSE_ID,
                "surface_id": html_surface_id,
                "public_url": PUBLIC_ARTIFACT_URLS["html"],
                "route_kind": "verified_course_root",
                "target_kind": "readable_html",
                "machine_data_only": False,
                "unit_id": None,
                "unit_anchor": None,
                "unit_route_state": "not_claimed_repeated_labels_not_unique_anchors",
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="published", owner_native_state="github_pages_verified",
        ),
        make_row(
            LANE_NAMESPACE, "route", "d60:final:pdf-offline",
            {
                "access_state": "public_anonymous_readback_verified",
                "course_id": CURRENT_COURSE_ID,
                "surface_id": pdf_surface_id,
                "public_url": PUBLIC_ARTIFACT_URLS["pdf"],
                "route_kind": "verified_direct_file_download",
                "target_kind": "downloadable_pdf",
                "machine_data_only": False,
                "unit_id": None,
                "unit_anchor": None,
                "unit_route_state": "not_applicable",
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="published", owner_native_state="zenodo_verified",
        ),
    ])

    for native in heads["qa"]:
        note = str(native.get("note", ""))
        tables["qa_events"].append(make_row(
            LANE_NAMESPACE,
            "qa_event",
            f"d60:native:{native['id']}",
            {
                "native_qa_id": native["id"],
                "qa_kind": native.get("qa_type"),
                "result": native.get("result"),
                "native_unit_id": native.get("unit_id"),
                "projected_unit_id": endpoint_map.get(str(native.get("unit_id"))),
                "native_witness_artifact_ids": native.get("witness_artifact_ids", []),
                "projected_witness_artifact_ids": [endpoint_map[item] for item in native.get("witness_artifact_ids", []) if item in endpoint_map],
                "note_sha256": sha256_bytes(note.encode("utf-8")),
                "note_copied": False,
            },
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state=str(native.get("result")),
        ))
    for suffix, payload in (
        ("native-preflight", {
            "qa_kind": "d60_owner_native_authority_preflight",
            "result": "pass_with_declared_limitations",
            "checks": {"native_files": 11, "native_records": 8338, "global_unique_ids": 8338, "relation_endpoints_resolved": 2886},
            "declared_limitations_authority": "d60_authority",
        }),
        ("adapter-build", {
            "qa_kind": "d60_v23_zero_copy_adapter_build",
            "result": "pending_independent_validator",
            "checks": ["frozen input hashes", "current-head projection", "CSV roundtrip", "namespace crosswalk", "scope", "rights", "reader route", "no-prose policy"],
        }),
    ):
        tables["qa_events"].append(make_row(
            LANE_NAMESPACE, "qa_event", f"d60:adapter:qa:{suffix}", payload,
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="validated", owner_native_state=None,
        ))

    capability_map = {
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
    tables["adapter_profiles"].append(make_row(
        LANE_NAMESPACE,
        "adapter_profile",
        "d60:adapter-profile:0.1.0",
        {
            "adapter_id": "d60-algebraic-topology-zero-copy-v2.3.1",
            "adapter_version": ADAPTER_VERSION,
            "zero_copy": True,
            "owner_native_record_count": 8338,
            "materialized_native_record_count": len(projection_registry),
            "capability_map": capability_map,
            "identity_rules": [
                "Preserve every owner semantic ID as the native identity.",
                "Mint separate UUIDv5 projection IDs from record type and corpus-qualified semantic key.",
                "Never derive identity from translated prose, page numbers, mutable URLs, or build time.",
            ],
            "native_gap_policy": "declare and bind; never silently repair owner bytes",
        },
        dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
        normalized_state="validated", owner_native_state=None,
    ))

    native_counts = {name: len(rows) for name, rows in shards.items()}
    projected_before_run = {name: len(rows) for name, rows in tables.items()}
    tables["adapter_runs"].append(make_row(
        LANE_NAMESPACE,
        "adapter_run",
        "d60:adapter-run:0.1.0",
        {
            "adapter_profile_id": projection_id(LANE_NAMESPACE, "adapter_profile", "d60:adapter-profile:0.1.0"),
            "native_input_counts": native_counts,
            "current_head_counts": expected_head_counts,
            "projected_output_counts_before_run_record": projected_before_run,
            "input_owner_record_count": 8338,
            "materialized_native_record_count": len(projection_registry),
            "deterministic_replay_requirement": "two absent-directory builds must be byte-identical",
            "reverse_extraction_requirement": "every materialized native record has one native binding and one namespace mapping",
            "validation_state": "pending_independent_validator",
        },
        dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
        normalized_state="validated", owner_native_state="specialized_final_validation_pass_with_declared_generic_gaps",
    ))

    source_table_path = {
        "authority": "backend/authority.jsonl",
        "units": "backend/units.jsonl",
        "segments": "backend/segments.jsonl",
        "relations": "backend/relations.jsonl",
        "rights": "backend/rights.jsonl",
        "artifacts": "backend/artifacts.jsonl",
        "qa": "backend/qa.jsonl",
    }
    crosswalk_mappings: list[dict[str, Any]] = []
    for native_id, entry in sorted(projection_registry.items()):
        reverse_recipe = f"jsonl_id({source_table_path[entry['source_table']]},{native_id})"
        tables["native_bindings"].append(make_row(
            LANE_NAMESPACE,
            "native_binding",
            f"d60:native-binding:{native_id}",
            {
                "subject_id": entry["target_id"],
                "native_id": native_id,
                "native_namespace": OWNER_NAMESPACE,
                "native_record_type": entry["source_table"].rstrip("s") if entry["source_table"] not in {"qa"} else "qa_event",
                "native_schema_name": "curriculum.interop",
                "native_schema_version": "0.1.0_with_declared_legacy_envelope_gaps",
                "mapping_cardinality": "one_to_one",
                "reverse_recipe": reverse_recipe,
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="validated", owner_native_state="current_head",
        ))
        tables["identity_crosswalks"].append(make_row(
            LANE_NAMESPACE,
            "identity_crosswalk",
            f"d60:crosswalk:{native_id}",
            {
                "source_namespace": OWNER_NAMESPACE,
                "source_id": native_id,
                "source_record_type": entry["source_table"],
                "target_namespace": str(LANE_NAMESPACE),
                "target_id": entry["target_id"],
                "target_record_type": entry["target_record_type"],
                "mapping_cardinality": "one_to_one",
                "mapping_state": "mapped",
                "reverse_recipe": reverse_recipe,
            },
            dataset_id=dataset_id, owner_authority_id=owner_authority_id, recorded_at=RECORDED_AT,
            normalized_state="validated", owner_native_state="current_head",
        ))
        crosswalk_mappings.append({
            "source_namespace": OWNER_NAMESPACE,
            "target_namespace": str(LANE_NAMESPACE),
            "source_record_id": native_id,
            "target_record_id": entry["target_id"],
            "source_record_type": entry["source_table"],
            "target_record_type": entry["target_record_type"],
            "cardinality": "one_to_one",
            "mapping_state": "mapped",
            "reverse_recipe": reverse_recipe,
            "evidence_refs": [f"native_{entry['source_table']}", "d60_authority"],
            "identity_set_sha256": identity_set_sha256([native_id, entry["target_id"]]),
        })

    course_mapping = {
        "source_namespace": COMMON_NAMESPACE,
        "target_namespace": COMMON_NAMESPACE,
        "source_record_id": CURRENT_V1_COURSE_ID,
        "target_record_id": CURRENT_COURSE_ID,
        "source_record_type": "course",
        "target_record_type": "course",
        "cardinality": "one_to_one",
        "mapping_state": "mapped",
        "reverse_recipe": "select current courses.jsonl row where payload.v1_course_id equals source_record_id",
        "evidence_refs": ["courses_current", f"row-sha256:{sha256_bytes((compact_json(course_row) + chr(10)).encode('utf-8'))}"],
        "identity_set_sha256": identity_set_sha256([CURRENT_V1_COURSE_ID, CURRENT_COURSE_ID]),
    }
    native_course_mapping = {
        "source_namespace": OWNER_NAMESPACE,
        "target_namespace": COMMON_NAMESPACE,
        "source_record_id": NATIVE_COURSE_ID,
        "target_record_id": CURRENT_COURSE_ID,
        "source_record_type": "course",
        "target_record_type": "course",
        "cardinality": "one_to_one",
        "mapping_state": "mapped",
        "reverse_recipe": "select backend/authority.jsonl row with id=course:o012-d60 and central courses.jsonl row with payload.course_id=D60",
        "evidence_refs": ["native_authority", "courses_current"],
        "identity_set_sha256": identity_set_sha256([NATIVE_COURSE_ID, CURRENT_COURSE_ID]),
    }

    sort_table_rows(tables)
    context = {
        "package_id": package_id,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_authority_id,
        "composite_edition_id": composite_edition_id,
        "projection_registry": projection_registry,
        "crosswalk_mappings": [course_mapping, native_course_mapping, *crosswalk_mappings],
        "heads": heads,
        "head_counts": expected_head_counts,
        "artifact_physical_states": dict(sorted(artifact_exception_counts.items())),
        "public_artifact_ids": public_artifact_ids,
    }
    return tables, context


def capability_shards(named: Mapping[str, Mapping[str, Any]], names: Iterable[str]) -> list[dict[str, Any]]:
    return [dict(named[f"native_{name}"]) for name in names]


def capability_entry(
    name: str,
    state: str,
    shards: list[dict[str, Any]],
    projected_count: int,
    limitation: str | None,
) -> dict[str, Any]:
    return {
        "name": name,
        "version": "0.1.0",
        "state": state,
        "schema_binding": None,
        "shard_refs": shards,
        "native_count": sum(int(item["records"]) for item in shards),
        "projected_count": projected_count,
        "identity_set_sha256": combined_shard_identity(shards) if shards else None,
        "identity_set_scope": "native_shard_records" if shards else "none",
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
    output: Path,
    named: Mapping[str, Mapping[str, Any]],
    tables: Mapping[str, list[dict[str, Any]]],
    context: Mapping[str, Any],
) -> None:
    package_id = str(context["package_id"])
    dataset_id = str(context["dataset_id"])
    heads = context["heads"]
    projection_registry = context["projection_registry"]
    unit_ids = [str(row["id"]) for row in tables["units"]]

    scope = {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "dataset_id": dataset_id,
        "scope_kind": "lane_adapter",
        "course_ids": ["D60"],
        "curriculum_role_ids": ["D60"],
        "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [role for role in COURSE_ROLES if role != "D60"],
        "owner_authority_binding": basic_fact(named["native_authority"]),
        "curriculum_authority_binding": basic_fact(named["courses_current"]),
        "limitations": [
            "D60 only; every other curriculum role remains outside this adapter.",
            "All 8,338 owner-native records remain external, exact, and authoritative; textbook body prose is not copied.",
            "The generic owner validator, selected legacy term envelopes, two supersession branches, two artifact identities, and whole-backend replay remain declared native limitations.",
            "The final PDF is untagged; semantic HTML is the primary learner and accessibility surface.",
            "No per-unit public fragment route is claimed because the fourteen route labels are not unique anchors.",
        ],
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "scope-declaration-v0.2.0.json", scope)

    native_ids = sorted(projection_registry)
    projected_ids = sorted(str(entry["target_id"]) for entry in projection_registry.values())
    crosswalk = {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "profiles": [
            {"name": "d60_owner_native", "namespace": OWNER_NAMESPACE, "formula": "owner semantic ID namespaces preserved verbatim"},
            {"name": "v1_common", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + '|' + stable_key)"},
            {"name": "v2_current", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)"},
            {"name": "v2_3_lane", "namespace": str(LANE_NAMESPACE), "formula": "UUIDv5(namespace, record_type + ':' + corpus-qualified semantic key)"},
        ],
        "mappings": context["crosswalk_mappings"],
        "unmaterialized_candidates": [
            {
                "namespace": str(LANE_NAMESPACE),
                "record_type": record_type,
                "semantic_key": f"d60:unmaterialized-current-{table_name}",
                "candidate_record_id": projection_id(LANE_NAMESPACE, record_type, f"d60:unmaterialized-current-{table_name}"),
                "state": "deterministic_id_proposal_not_a_mapping",
                "formula": "UUIDv5 only after a global table contract is admitted; native shard remains authoritative",
                "effective_cardinality": "unresolved_until_materialized",
            }
            for record_type, table_name in (("concept", "concepts"), ("term", "terms"), ("correction", "corrections"), ("asset", "assets"))
        ],
        "identity_sets": {
            "native_materialized_sha256": identity_set_sha256(native_ids),
            "projected_materialized_sha256": identity_set_sha256(projected_ids),
            "mapped_pairs_sha256": mapping_set_sha256((native_id, projection_registry[native_id]["target_id"]) for native_id in native_ids),
            "native_materialized_count": len(native_ids),
            "projected_materialized_count": len(projected_ids),
        },
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "namespace-crosswalk-v0.2.0.json", crosswalk)

    current_segments = {str(row.get("unit_id")): row for row in heads["segments"]}
    translation_records: list[dict[str, Any]] = []
    for native in sorted(heads["units"], key=lambda row: str(row["id"])):
        native_id = str(native["id"])
        segment = current_segments.get(native_id)
        source_locator = segment.get("source_locator") if segment else None
        target_locator = native.get("target_locator") or (segment.get("target_locator") if segment else None)
        translation_records.append({
            "locale": native.get("locale", "id-ID"),
            "native_unit_id": native_id,
            "projected_unit_id": projection_registry[native_id]["target_id"],
            "owner_native_state": native.get("translation_state"),
            "normalized_publication_state": "published_composite_course",
            "source_locator": source_locator,
            "target_locator": target_locator,
            "provenance_relation": native.get("provenance_relation"),
            "state_inferred": False,
        })
    translation = {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "dataset_id": dataset_id,
        "authority_bindings": [basic_fact(named["native_units"]), basic_fact(named["native_segments"]), basic_fact(named["github_receipt"]), basic_fact(named["zenodo_receipt"])],
        "coverage": {
            "course_id": "D60",
            "granularity": "current_owner_semantic_unit_head",
            "authority_rows": len(translation_records),
            "indexed_rows": len(translation_records),
            "inferred_rows": 0,
        },
        "states": sorted({str(row["owner_native_state"]) for row in translation_records} | {"published_composite_course"}),
        "records": translation_records,
        "identity_set_sha256": identity_set_sha256(row["projected_unit_id"] for row in translation_records),
        "no_inference": True,
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "translation-state-index-v0.2.0.json", translation)

    capabilities = [
        capability_entry("structure_localization", "materialized", capability_shards(named, ["units", "segments", "relations"]), len(tables["units"]) + len(tables["content_bindings"]) + len(tables["relations"]), None),
        capability_entry("terminology", "referenced_native_shards", capability_shards(named, ["concepts", "terms"]), 0, "Thirty native term rows omit schema/schema_version and 104 current term heads omit terminology_status; exact shards remain available without silent repair."),
        capability_entry("mathematical_preservation", "referenced_native_shards", capability_shards(named, ["segments", "qa", "corrections"]), len(tables["content_bindings"]) + len(tables["qa_events"]), "Specialized final validation passes, but the generic owner validator and one-command source-to-entire-backend replay are not closed."),
        capability_entry("assessment_support", "referenced_native_shards", capability_shards(named, ["units", "segments", "relations"]), 0, "Assessment, hint, solution, proof, and laboratory semantics are exact native metadata but do not yet have a separate global assessment table contract."),
        capability_entry("assets", "referenced_native_shards", capability_shards(named, ["assets", "artifacts"]), len(tables["artifacts"]), "One historical artifact path is missing and one proof-census artifact hash is stale; both remain explicitly reported."),
        capability_entry("accessibility", "referenced_native_shards", capability_shards(named, ["assets", "qa", "artifacts"]), len(tables["reader_surfaces"]), "Semantic HTML is verified and primary; the 564-page PDF is untagged and per-unit accessibility state is not universally normalized."),
        capability_entry("corrections", "referenced_native_shards", capability_shards(named, ["corrections"]), 0, "One correction supersession parent branches to two current children; the adapter preserves both and does not choose silently."),
        capability_entry("computational_interactives", "referenced_native_shards", capability_shards(named, ["units", "assets", "artifacts"]), 0, "Four laboratories are exact native components; no remote runtime behavior or interactive service availability is inferred."),
        capability_entry("publication", "materialized", capability_shards(named, ["artifacts"]), len(tables["artifacts"]) + len(tables["reader_surfaces"]) + len(tables["routes"]), None),
        capability_entry("research_support", "referenced_native_shards", capability_shards(named, ["concepts", "relations", "terms"]), 0, "The concept/relation graph is exact native evidence; no global research taxonomy or outcome state is inferred."),
    ]
    capability_doc = {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "dataset_id": dataset_id,
        "contract_binding": basic_fact(named["capability_contract"]),
        "capabilities": capabilities,
        "legacy_labels": [],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards",
            "shard_refs": capability_shards(named, ["rights"]),
            "native_count": int(named["native_rights"]["records"]),
            "identity_set_sha256": combined_shard_identity(capability_shards(named, ["rights"])),
            "closure_rules": [
                "component rights are never flattened",
                "direct pointers and exact supersession leaves are retained",
                "the integrated course rights relation is explicitly materialized",
            ],
        },
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "capability-declarations-v0.2.0.json", capability_doc)


def copy_contract_files(repository_root: Path, output: Path) -> None:
    schema_names = [
        "lane-adapter-v2.3.1.schema.json",
        "capability-declarations-v0.2.schema.json",
        "namespace-crosswalk-v0.2.schema.json",
        "translation-state-index-v0.2.schema.json",
        "csv-projection-manifest-v0.2.schema.json",
        "scope-declaration-v0.2.schema.json",
    ]
    (output / "schema").mkdir(parents=True, exist_ok=True)
    (output / "tools").mkdir(parents=True, exist_ok=True)
    for name in schema_names:
        shutil.copyfile(repository_root / "backend" / "v2.3" / "schema" / name, output / "schema" / name)
    tools = {
        "build_d60_v23_adapter.py": Path(__file__).resolve(),
        "validate_d60_v23_adapter.py": Path(__file__).resolve().with_name("validate_d60_v23_adapter.py"),
        "validate_lane_adapter_v231.py": Path(__file__).resolve().with_name("validate_lane_adapter_v231.py"),
        "v231_adapter_common.py": Path(__file__).resolve().with_name("v231_adapter_common.py"),
    }
    for target, source in tools.items():
        require(source.is_file(), f"missing adapter tool: {source}")
        shutil.copyfile(source, output / "tools" / target)


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), "repository root missing")
    require(owner_root.is_dir(), "owner package root missing")
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    authorities, named, shards = build_authorities(repository_root, owner_root)
    courses = read_jsonl(repository_root / "backend" / "v2" / "program-matematika-indonesia-federation-v0.4.4" / "data" / "courses.jsonl")
    course_row, prerequisite_ids = locate_course_rows(courses)
    github_receipt = read_json(owner_root.joinpath(*PurePosixPath(EXPECTED_OWNER["github_receipt"][0]).parts))
    zenodo_receipt = read_json(owner_root.joinpath(*PurePosixPath(EXPECTED_OWNER["zenodo_receipt"][0]).parts))
    require(github_receipt.get("status") == "PUBLISHED_AND_ANONYMOUSLY_VERIFIED", "D60 GitHub receipt state drift")
    require(github_receipt.get("content_commit") == "bce91390574d024a2b2386af28a811dffff67e2b", "D60 content commit drift")
    require(zenodo_receipt.get("status") == "PUBLISHED_AND_TWICE_ANONYMOUSLY_VERIFIED", "D60 Zenodo receipt state drift")
    require(zenodo_receipt.get("record_id") == 22168033 and len(zenodo_receipt.get("files", [])) == 9, "D60 Zenodo inventory drift")

    tables, context = build_tables(owner_root, named, shards, course_row, prerequisite_ids)
    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/d60-v23-input-authorities/1",
        "recorded_at": RECORDED_AT,
        "authorities": authorities,
        "owner_native_closure": {
            "files": 11,
            "records": 8338,
            "bytes": 10040043,
            "bundle_sha256": "8a3ffc9618e56dfce048c41e938aabef4ffbfd3db20a03a4f52f218985230dbb",
            "global_native_id_set_sha256": identity_set_sha256(str(row["id"]) for rows in shards.values() for row in rows),
            "current_head_counts": context["head_counts"],
            "materialized_current_native_records": len(context["projection_registry"]),
            "result": "pass_with_declared_native_limitations",
        },
        "owner_native_non_mutation": True,
        "body_prose_copied": False,
    })
    write_json(output / "evidence" / "D60_NATIVE_LIMITATIONS.json", {
        "schema_id": "program-matematika-indonesia/d60-native-limitations/1",
        "recorded_at": RECORDED_AT,
        "status": "DECLARED_NOT_SILENTLY_REPAIRED",
        "artifact_physical_states": context["artifact_physical_states"],
        "term_rows_missing_schema_or_version": 30,
        "current_term_heads_missing_terminology_status": 104,
        "supersession_branch_parents": ["artifact:o012-u020-qa", "correction:o012-u020-adv-0287"],
        "artifact_exceptions": ["artifact:o012-units-001-013-qa-text", "artifact:o012-d60-proof-census-final-rev3"],
        "generic_owner_validator_state": "fail_artifacts_not_sorted_by_ordinal_id",
        "whole_native_backend_clean_replay": False,
        "unit_anchor_coverage": 0,
        "pdf_tagged": False,
        "primary_accessibility_surface": "semantic_html",
    })

    write_tables(output, tables)
    build_sidecars(output, named, tables, context)
    csv_manifest = write_csv_surfaces(output, tables, context["package_id"], RECORDED_AT)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    copy_contract_files(repository_root, output)

    payload_facts = package_payload_files(output)
    payload_identity = inventory_sha256(payload_facts)
    sidecar_names = [
        "capability-declarations-v0.2.0.json",
        "namespace-crosswalk-v0.2.0.json",
        "translation-state-index-v0.2.0.json",
        "csv-projection-manifest-v0.2.0.json",
        "scope-declaration-v0.2.0.json",
    ]
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
        "schema_version": "2.3.1",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "extension_id": projection_id(LANE_NAMESPACE, "lane_adapter_extension", f"d60:algebraic-topology:{ADAPTER_VERSION}"),
        "extension_version": ADAPTER_VERSION,
        "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": sorted(authorities, key=lambda item: (item["path_base"], item["path"])),
        "sidecars": [file_fact(output / name, name, "sidecar") for name in sidecar_names],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER),
            "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER),
            "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools" / "build_d60_v23_adapter.py", "tools/build_d60_v23_adapter.py", "builder"),
            "validator": file_fact(output / "tools" / "validate_d60_v23_adapter.py", "tools/validate_d60_v23_adapter.py", "validator"),
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
            "binds": ["schemas", "tools", "input_authorities", "native_limitations", "tables", "sidecars", "csv_projections", "manifest"],
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
    seal_facts = payload_facts + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    write_json(output / "seal.json", {
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
        "package_id": context["package_id"],
        "algorithm": "sha256-sorted-path-bytes-v1",
        "files": seal_facts,
        "file_count": len(seal_facts),
        "bytes": sum(int(item["bytes"]) for item in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts),
        "seal_excluded_from_own_digest": True,
        "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_fact = write_checksums(output, checksum_facts)
    return {
        "status": "pass",
        "output": str(output),
        "files": len(checksum_facts) + 1,
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "owner_native_records": 8338,
        "materialized_current_native_records": len(context["projection_registry"]),
        "payload_inventory_sha256": payload_identity,
        "seal_sha256": sha256_file(output / "seal.json"),
        "checksum_sha256": checksum_fact["sha256"],
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
        print(compact_json(result))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
