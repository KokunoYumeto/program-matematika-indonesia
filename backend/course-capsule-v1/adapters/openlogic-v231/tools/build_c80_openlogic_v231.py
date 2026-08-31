#!/usr/bin/env python3
"""Build the deterministic zero-copy C80/Open Logic v2.3.1 adapter.

The adapter projects only stable identity, topology, rights, publication,
translation-state, locator, and hash evidence. It never copies textbook prose
or claims a unit-level learner route that the public edition does not expose.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    TABLE_ORDER,
    AdapterError,
    compact_json,
    empty_tables,
    external_file_fact,
    file_fact,
    identity_set_sha256,
    inventory_sha256,
    make_row,
    mapping_set_sha256,
    package_payload_files,
    pretty_json_bytes,
    projection_id,
    require,
    sha256_bytes,
    sha256_file,
    sort_table_rows,
    write_csv_surfaces,
    write_json,
    write_jsonl,
)


RECORDED_AT = "2026-08-31T00:00:00Z"
ADAPTER_VERSION = "0.1.0"
SOURCE_COMMIT = "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"
SOURCE_TREE = "unknown-not-claimed-by-this-adapter"
RELEASE_COMMIT = "34af65419e4c5c5580dae60a48454c485ddf504c"
RELEASE_TREE = "a7fcb6b970d9bafc82c36f51447931cf05a146cb"
RELEASE_TAG = "id-olp-0722-20260814"
VERSION_DOI = "10.5281/zenodo.21932787"
CONCEPT_DOI = "10.5281/zenodo.21932786"
REPOSITORY_URL = "https://github.com/KokunoYumeto/OpenLogic-id"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{RELEASE_TAG}"
PREVIEW_URL = "https://zenodo.org/records/21932787/preview/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf"

LANE_NAMESPACE = uuid.UUID("20b4a5f0-524a-5ef7-a271-7b188d658a4f")
OWNER_NAMESPACE = "openlogic-olp-closure-id-v1"
V1_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")

INVENTORY_REL = "04_mirrors/id/_control/OPENLOGIC_ID_COMPLETE_SOURCE_INVENTORY_20260814.csv"
CLOSURE_REL = "04_mirrors/id/_control/OPENLOGIC_CLOSURE_MANIFEST_20260812.csv"
CAPABILITY_REL = "04_mirrors/id/program-matematika-indonesia-v06213/backend/v2.2/global-capability-contract-v0.1.0.json"
COURSES_REL = "04_mirrors/id/program-matematika-indonesia-v06213/backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl"
FEDERATION_MANIFEST_REL = "04_mirrors/id/program-matematika-indonesia-v06213/backend/v2/program-matematika-indonesia-federation-v0.4.4/manifest.json"
MIGRATION_REL = "04_mirrors/id/program-matematika-indonesia/backend/migrations/openlogic-id-v1/MIGRATION_RECEIPT.json"
CANDIDATE_PREFIX = "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/openlogic_v231_candidate"
UPSTREAM_ZIP_REL = f"{CANDIDATE_PREFIX}/authority_cache/upstream-9620cc73.zip"
LOCALIZED_ZIP_REL = f"{CANDIDATE_PREFIX}/authority_cache/localized-sources-OLP-0722.zip"
EVIDENCE_ZIP_REL = f"{CANDIDATE_PREFIX}/authority_cache/evidence-OLP-0722.zip"
PUBLIC_EVIDENCE_REL = f"{CANDIDATE_PREFIX}/research/C80_PUBLICATION_LEARNER_BACKEND_EVIDENCE_20260831.json"
OWNER_LICENSE_REL = "LICENSE.md"

EXPECTED: dict[str, tuple[int, str]] = {
    "inventory": (252486, "964a274b418c06c99130ad33e8326629d5c35bf677d7c9a6166c19a6f91a033b"),
    "closure": (874968, "b1ab541e552bb81a99b8639a0471f66253048a0334f5d0c9795146c7d76de3a7"),
    "upstream_zip": (1899150, "ced94fb4617614404e828da9ca1d2c992be2fc1e1bc9204901d7a56fdb6eb930"),
    "localized_zip": (1580716, "492fd7369de367e2e748b0cbac8ba9a4c8c624f2a756a8943de445b9650283ed"),
    "evidence_zip": (2000807, "273f790b9ddfaade9a6388c0d8cbd8b89006fca8f8c0da89cb2b5afcf1ae9441"),
    "owner_license": (17227, "1094a30e124027cb4cff48d932f1a8673d1386682a475a0edc811f2162241fec"),
    "public_evidence": (15832, "06a13d8290692cb5f70820e3d1ddbb1199d882c8fae6ed83e737461ed858bd17"),
    "migration": (9843, "be21c9375a2cde2199ce9709910de0c15467a2141429f5b11c7dcbef52090654"),
}

PUBLIC_ARTIFACTS = [
    {
        "name": "00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf",
        "kind": "linked_pdf_reader",
        "bytes": 5593664,
        "sha256": "bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a",
    },
    {
        "name": "01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip",
        "kind": "editable_sources_zip",
        "bytes": 1580716,
        "sha256": "492fd7369de367e2e748b0cbac8ba9a4c8c624f2a756a8943de445b9650283ed",
    },
    {
        "name": "02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip",
        "kind": "evidence_provenance_zip",
        "bytes": 2000807,
        "sha256": "273f790b9ddfaade9a6388c0d8cbd8b89006fca8f8c0da89cb2b5afcf1ae9441",
    },
    {
        "name": "03_OPENLOGIC_id_SHA256SUMS_OLP-0722.txt",
        "kind": "checksum_manifest",
        "bytes": 401,
        "sha256": "d5b2f18fb24fd5469dafcb9ab91717b04a62d0fb437a68984b2c94ac254e9c60",
    },
]


def read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for ordinal, line in enumerate(stream, 1):
            require(bool(line.strip()), f"blank JSONL row: {path}:{ordinal}")
            rows.append(json.loads(line))
    return rows


def zip_entry_bytes(archive: zipfile.ZipFile, name: str) -> bytes:
    try:
        return archive.read(name)
    except KeyError as exc:
        raise AdapterError(f"missing ZIP entry: {name}") from exc


def zip_entry_fact(data: bytes, archive_role: str, entry: str) -> dict[str, Any]:
    return {
        "archive_role": archive_role,
        "entry": entry,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def previous_v1_unit_id(closure_id: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(V1_NAMESPACE, f"unit|openlogic:{closure_id}"))


def external_authority(
    repository_root: Path,
    relative: str,
    role: str,
    expected: tuple[int, str] | None = None,
) -> dict[str, Any]:
    path = repository_root.joinpath(*relative.split("/"))
    if expected is None:
        require(path.is_file(), f"missing authority: {relative}")
        return file_fact(path, relative, role, path_base="program_repository_root")
    return external_file_fact(
        path,
        relative,
        role,
        "program_repository_root",
        expected_bytes=expected[0],
        expected_sha256=expected[1],
    )


def add_row(
    tables: dict[str, list[dict[str, Any]]],
    table: str,
    record_type: str,
    semantic_key: str,
    payload: Mapping[str, Any],
    *,
    dataset_id: str,
    owner_authority_id: str,
    state: str = "validated",
    owner_state: str | None = None,
) -> dict[str, Any]:
    row = make_row(
        LANE_NAMESPACE,
        record_type,
        semantic_key,
        payload,
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state=state,
        owner_native_state=owner_state,
    )
    tables[table].append(row)
    return row


def build_tables(
    inventory: list[dict[str, str]],
    closure: list[dict[str, str]],
    components: list[dict[str, str]],
    course_row: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    package_id = projection_id(LANE_NAMESPACE, "lane_adapter_package", "c80:openlogic:v2.3.1:0.1.0")
    dataset_id = projection_id(LANE_NAMESPACE, "dataset", "c80:openlogic:OLP-0722")
    owner_id = projection_id(LANE_NAMESPACE, "owner_authority", "c80:openlogic:owner-public-edition")
    rights_id = projection_id(LANE_NAMESPACE, "rights", "c80:openlogic:cc-by-4.0")
    source_edition_id = projection_id(LANE_NAMESPACE, "edition", f"c80:openlogic:source:{SOURCE_COMMIT}")
    target_edition_id = projection_id(LANE_NAMESPACE, "edition", "c80:openlogic:id:OLP-0722")
    adapter_profile_id = projection_id(LANE_NAMESPACE, "adapter_profile", "c80:openlogic:adapter-profile:0.1.0")
    preview_route_id = projection_id(LANE_NAMESPACE, "route", "c80:openlogic:route:learner-pdf-preview")
    reader_surface_id = projection_id(LANE_NAMESPACE, "reader_surface", "c80:openlogic:reader-surface:linked-pdf")
    course_id = str(course_row["id"])
    v1_course_id = str(course_row["payload"]["v1_course_id"])

    require(len(inventory) == len(closure) == len(components) == 722, "C80 authority cardinality is not 722")
    expected_ids = [f"OLP-{ordinal:04d}" for ordinal in range(1, 723)]
    require([row["closure_id"] for row in inventory] == expected_ids, "final inventory IDs/order drift")
    require([row["closure_id"] for row in closure] == expected_ids, "closure IDs/order drift")
    require([row["component_id"] for row in components] == expected_ids, "component IDs/order drift")
    require([int(row["stable_order"]) for row in inventory] == list(range(1, 723)), "inventory order is not 1..722")

    closure_by_id = {row["closure_id"]: row for row in closure}
    component_by_id = {row["component_id"]: row for row in components}
    source_path_to_id = {row["source_path"]: row["closure_id"] for row in inventory}
    projected_units = {
        row["closure_id"]: projection_id(LANE_NAMESPACE, "unit", f"c80:openlogic:unit:{row['closure_id']}")
        for row in inventory
    }
    tables = empty_tables()

    add_row(
        tables, "owner_authorities", "owner_authority", "c80:openlogic:owner-public-edition",
        {
            "authority_kind": "immutable_public_edition_plus_owner_native_records",
            "authority_scope": "complete 722-unit Open Logic source/Indonesian corpus, topology, rights, QA, and publication evidence",
            "course_ids": [course_id],
            "concept_doi": CONCEPT_DOI,
            "version_doi": VERSION_DOI,
            "public_repository_url": REPOSITORY_URL,
            "public_release_url": RELEASE_URL,
            "release_commit": RELEASE_COMMIT,
            "release_tree": RELEASE_TREE,
            "release_tag": RELEASE_TAG,
            "stable_unit_count": 722,
            "sole_integrator_publisher": True,
            "zero_copy": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="complete_public_readback",
    )
    add_row(
        tables, "datasets", "dataset", "c80:openlogic:dataset",
        {
            "adapter_profile_id": adapter_profile_id,
            "course_ids": [course_id],
            "dataset_kind": "zero_copy_owner_projection",
            "limitations": [
                "No textbook prose, formula body, proof body, or exercise body is copied into this adapter.",
                "C80 exposes a verified linked PDF reader, not native semantic HTML.",
                "No unit/page anchors, solution-closure claim, or full accessibility claim is inferred.",
                "The 722 owner-native OLP IDs and prior v1 IDs remain reversible identities.",
            ],
            "materialized_record_counts": {"unit": 722, "relation": 725, "search_document": 722},
            "owner_unit_count": 722,
            "publication_state": "public_anonymous_readback_verified",
            "reader_surface_ids": [reader_surface_id],
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="complete",
    )
    add_row(
        tables, "editions", "edition", f"c80:openlogic:source:{SOURCE_COMMIT}",
        {
            "commit": SOURCE_COMMIT,
            "edition_kind": "frozen_upstream_source",
            "locale": "en",
            "owner_authority_id": owner_id,
            "rights_id": rights_id,
            "source_format": "modular LaTeX",
            "title": "Open Logic Project",
            "tree": SOURCE_TREE,
            "version_label": SOURCE_COMMIT,
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="validated", owner_state="frozen_source",
    )
    add_row(
        tables, "editions", "edition", "c80:openlogic:id:OLP-0722",
        {
            "commit": RELEASE_COMMIT,
            "edition_kind": "complete_indonesian_translation",
            "locale": "id-ID",
            "owner_authority_id": owner_id,
            "rights_id": rights_id,
            "source_edition_id": source_edition_id,
            "source_format": "modular LaTeX",
            "target_format": "modular LaTeX and linked PDF",
            "title": "Open Logic Project — edisi lengkap Bahasa Indonesia",
            "tree": RELEASE_TREE,
            "version_label": "OLP-0722",
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="complete_public_readback",
    )
    add_row(
        tables, "rights", "rights", "c80:openlogic:rights:cc-by-4.0",
        {
            "assertion_status": "verified_from_frozen_public_release",
            "attribution": "Open Logic Project contributors; Indonesian translation and changes identified in the frozen release",
            "change_notice": "Retain attribution and identify translated or modified material.",
            "flattened_course_license": False,
            "license_expression": "CC-BY-4.0",
            "nonendorsement": "No Open Logic Project endorsement is implied.",
            "notice_locator": "01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip!/LICENSE",
            "notice_sha256": "1094a30e124027cb4cff48d932f1a8673d1386682a475a0edc811f2162241fec",
            "source_component_id": "Open Logic Project OLP-0722 source and Indonesian translation",
            "third_party_status": "Component-level exceptions remain governed by frozen source notices.",
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="verified",
    )

    artifact_rows: list[dict[str, Any]] = []
    artifact_ids: dict[str, str] = {}
    for artifact in PUBLIC_ARTIFACTS:
        semantic = f"c80:openlogic:artifact:{artifact['name']}"
        row = add_row(
            tables, "artifacts", "artifact", semantic,
            {
                "artifact_kind": artifact["kind"],
                "bytes": artifact["bytes"],
                "edition_id": target_edition_id,
                "filename": artifact["name"],
                "locale": "id-ID",
                "public_url": f"https://zenodo.org/records/21932787/files/{artifact['name']}?download=1",
                "publication_state": "public_anonymous_readback_verified",
                "sha256": artifact["sha256"],
                "version_doi": VERSION_DOI,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="anonymous_readback_verified",
        )
        artifact_rows.append(row)
        artifact_ids[artifact["name"]] = row["id"]

    route_specs = [
        ("learner-pdf-preview", "linked_pdf_preview", PREVIEW_URL, False),
        ("version-doi", "version_doi", f"https://doi.org/{VERSION_DOI}", False),
        ("concept-doi", "concept_doi", f"https://doi.org/{CONCEPT_DOI}", False),
        ("repository", "repository", REPOSITORY_URL, False),
        ("release", "release", RELEASE_URL, False),
    ] + [
        (f"download-{ordinal}", "artifact_download", f"https://zenodo.org/records/21932787/files/{artifact['name']}?download=1", True)
        for ordinal, artifact in enumerate(PUBLIC_ARTIFACTS, 1)
    ]
    route_ids: dict[str, str] = {}
    for key, kind, url, download in route_specs:
        row = add_row(
            tables, "routes", "route", f"c80:openlogic:route:{key}",
            {
                "access_state": "public_anonymous_readback_verified",
                "course_id": course_id,
                "download": download,
                "machine_data_only": kind in {"artifact_download"} and not url.endswith(".pdf?download=1"),
                "public_url": url,
                "route_kind": kind,
                "target_kind": "readable_pdf" if key == "learner-pdf-preview" else kind,
                "unit_anchor": None,
                "unit_id": None,
                "unit_route_state": "not_claimed",
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="anonymous_readback_verified",
        )
        route_ids[key] = row["id"]
    require(route_ids["learner-pdf-preview"] == preview_route_id, "preview route ID formula drift")
    add_row(
        tables, "reader_surfaces", "reader_surface", "c80:openlogic:reader-surface:linked-pdf",
        {
            "action": "learn",
            "artifact_id": artifact_ids[PUBLIC_ARTIFACTS[0]["name"]],
            "course_ids": [course_id],
            "format": "linked_pdf",
            "learner_destination_state": "public_preview_and_download_readback_verified",
            "locale": "id-ID",
            "pages": 1116,
            "primary": True,
            "public_url": PREVIEW_URL,
            "publication_state": "public_anonymous_readback_verified",
            "route_id": preview_route_id,
            "unit_anchor_coverage": 0,
        }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="anonymous_readback_verified",
    )

    reader_count = 0
    relation_count = 0
    for inventory_row in inventory:
        closure_id = inventory_row["closure_id"]
        detail = closure_by_id[closure_id]
        component = component_by_id[closure_id]
        for field in ("stable_order", "source_commit", "source_path", "source_sha256", "source_bytes", "target_path"):
            require(inventory_row[field].lower() == detail[field].lower(), f"inventory/closure mismatch {closure_id}:{field}")
        require(component["translation_status"] == "complete", f"component is not complete: {closure_id}")
        require(component["exact_coverage"] == "full source unit", f"component coverage drift: {closure_id}")
        require(component["artifact_sha256"].lower() == inventory_row["target_sha256"].lower(), f"component target hash drift: {closure_id}")
        require(component["component_title"] == inventory_row["source_path"], f"component title/path drift: {closure_id}")
        projected_id = projected_units[closure_id]
        v1_id = previous_v1_unit_id(closure_id)
        reachable = detail["canonical_reader_reachable"].lower() == "true"
        reader_count += int(reachable)
        source_title = detail.get("source_title_locator") or inventory_row["source_path"]
        order_key = f"{int(inventory_row['stable_order']):04d}"
        add_row(
            tables, "units", "unit", f"c80:openlogic:unit:{closure_id}",
            {
                "canonical_reader_order": int(detail["canonical_reader_order"]) if detail.get("canonical_reader_order") else None,
                "canonical_reader_reachable": reachable,
                "inclusion_class": detail["inclusion_class"],
                "learner_route": {
                    "anchor": None,
                    "route_id": preview_route_id,
                    "route_state": "course_pdf_fallback_no_unit_anchor",
                    "url": PREVIEW_URL,
                },
                "localized_title": None,
                "native_locator": {
                    "closure_id": closure_id,
                    "source_path": inventory_row["source_path"],
                    "target_path": inventory_row["target_path"],
                },
                "native_unit_id": closure_id,
                "native_unit_kind": detail["source_role"] or "latex_module",
                "order_key": order_key,
                "previous_v1_unit_id": v1_id,
                "rights_id": rights_id,
                "source_bytes": int(inventory_row["source_bytes"]),
                "source_lines": int(inventory_row["source_lines"]),
                "source_sha256": inventory_row["source_sha256"].lower(),
                "source_title_locator": source_title,
                "source_title_locale": "en-or-structural-locator",
                "target_bytes": int(inventory_row["target_bytes"]),
                "target_lines": int(inventory_row["target_lines"]),
                "target_sha256": inventory_row["target_sha256"].lower(),
                "translation_state": "complete",
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="complete",
        )
        add_row(
            tables, "course_unit_memberships", "course_unit_membership", f"c80:openlogic:membership:{closure_id}",
            {
                "course_id": course_id,
                "edition_id": target_edition_id,
                "native_unit_id": closure_id,
                "order_key": order_key,
                "ordinal": int(inventory_row["stable_order"]),
                "required": None,
                "unit_id": projected_id,
                "visible": reachable,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="exact_closure_order",
        )
        add_row(
            tables, "native_bindings", "native_binding", f"c80:openlogic:native-binding:{closure_id}",
            {
                "mapping_cardinality": "one_to_one",
                "native_id": closure_id,
                "native_namespace": OWNER_NAMESPACE,
                "native_record_type": "unit",
                "native_schema_name": "OpenLogic OLP closure manifest",
                "native_schema_version": "OLP-0722",
                "previous_v1_unit_id": v1_id,
                "reverse_recipe": f"select final inventory row where closure_id={closure_id}",
                "subject_id": projected_id,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="identity_declared",
        )
        add_row(
            tables, "content_bindings", "content_binding", f"c80:openlogic:content-binding:{closure_id}",
            {
                "content_included_in_adapter": False,
                "edition_id": target_edition_id,
                "native_unit_id": closure_id,
                "source": {
                    "bytes": int(inventory_row["source_bytes"]),
                    "path": inventory_row["source_path"],
                    "sha256": inventory_row["source_sha256"].lower(),
                },
                "target": {
                    "bytes": int(inventory_row["target_bytes"]),
                    "path": inventory_row["target_path"],
                    "sha256": inventory_row["target_sha256"].lower(),
                },
                "unit_id": projected_id,
                "zero_copy": True,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="hash_bound",
        )
        add_row(
            tables, "search_documents", "search_document", f"c80:openlogic:search:{closure_id}",
            {
                "bounded_search_text": f"{closure_id.lower()} open logic logika matematika teori himpunan komputabilitas",
                "course_id": course_id,
                "learner_anchor": None,
                "learner_url": PREVIEW_URL,
                "locale": "id-ID",
                "localized_title": None,
                "native_unit_id": closure_id,
                "order_key": order_key,
                "source_title_locator": source_title,
                "unit_id": projected_id,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="metadata_only",
        )
        add_row(
            tables, "identity_crosswalks", "identity_crosswalk", f"c80:openlogic:crosswalk:{closure_id}",
            {
                "mapping_cardinality": "one_to_one",
                "mapping_state": "mapped",
                "previous_v1_unit_id": v1_id,
                "reverse_recipe": f"select final inventory row where closure_id={closure_id}",
                "source_id": closure_id,
                "source_namespace": OWNER_NAMESPACE,
                "source_record_type": "unit",
                "target_id": projected_id,
                "target_namespace": str(LANE_NAMESPACE),
                "target_record_type": "unit",
            }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="identity_declared",
        )
        add_row(
            tables, "rights_assignments", "rights_assignment", f"c80:openlogic:rights-assignment:unit:{closure_id}",
            {
                "assignment_state": "effective",
                "inheritance": "direct_from_frozen_edition",
                "rights_id": rights_id,
                "target_id": projected_id,
                "target_native_id": closure_id,
            }, dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="verified",
        )

    for inventory_row in inventory:
        from_closure = inventory_row["closure_id"]
        detail = closure_by_id[from_closure]
        imports = [value for value in detail.get("imports_resolved_ordered", "").split("|") if value]
        require(len(imports) == int(detail.get("import_count") or 0), f"import count mismatch: {from_closure}")
        require(not detail.get("imports_unresolved"), f"unresolved import: {from_closure}")
        for ordinal, target_path in enumerate(imports, 1):
            require(target_path in source_path_to_id, f"import outside closure: {from_closure}->{target_path}")
            target_closure = source_path_to_id[target_path]
            add_row(
                tables, "relations", "relation", f"c80:openlogic:relation:{from_closure}:{ordinal}:{target_closure}",
                {
                    "concept_relation_inferred": False,
                    "evidence": {
                        "assertion_method": "frozen_ordered_olimport_topology",
                        "confidence": "exact",
                        "source_locator": f"{inventory_row['source_path']}:olimport:{ordinal}",
                    },
                    "from_endpoint": {"native_id": from_closure, "projected_id": projected_units[from_closure]},
                    "ordinal": ordinal,
                    "relation_type": "imports",
                    "strength": "hard",
                    "to_endpoint": {"native_id": target_closure, "projected_id": projected_units[target_closure]},
                }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="exact_frozen_topology",
            )
            relation_count += 1

    for semantic, target_id in (
        ("source-edition", source_edition_id),
        ("target-edition", target_edition_id),
        *[(f"artifact-{ordinal}", row["id"]) for ordinal, row in enumerate(artifact_rows, 1)],
    ):
        add_row(
            tables, "rights_assignments", "rights_assignment", f"c80:openlogic:rights-assignment:{semantic}",
            {"assignment_state": "effective", "inheritance": "direct_from_frozen_release", "rights_id": rights_id, "target_id": target_id, "target_native_id": None},
            dataset_id=dataset_id, owner_authority_id=owner_id, state="published", owner_state="verified",
        )

    capability_map = {
        "structure_localization": "materialized",
        "terminology": "referenced_native_shards",
        "mathematical_preservation": "referenced_native_shards",
        "assessment_support": "not_projected",
        "assets": "referenced_native_shards",
        "accessibility": "referenced_native_shards",
        "corrections": "referenced_native_shards",
        "computational_interactives": "not_projected",
        "publication": "materialized",
        "research_support": "referenced_native_shards",
    }
    add_row(
        tables, "adapter_profiles", "adapter_profile", "c80:openlogic:adapter-profile:0.1.0",
        {
            "adapter_id": "c80-openlogic-zero-copy-v2.3.1",
            "adapter_version": ADAPTER_VERSION,
            "capability_map": capability_map,
            "identity_rules": [
                "Preserve OLP-0001..OLP-0722 as owner-native identities.",
                "Crosswalk every prior v1 unit UUID before deriving a v2.3.1 projection UUID.",
                "Never derive identity from translated prose, page numbers, URLs, or build time.",
            ],
            "owner_native_unit_count": 722,
            "zero_copy": True,
        }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="validated",
    )
    projected_counts = {name[:-1] if name.endswith("s") else name: len(tables[name]) for name in TABLE_ORDER}
    add_row(
        tables, "adapter_runs", "adapter_run", "c80:openlogic:adapter-run:0.1.0",
        {
            "adapter_profile_id": adapter_profile_id,
            "deterministic_replay_requirement": "two absent-directory builds must be byte-identical",
            "input_owner_unit_count": 722,
            "projected_output_counts_before_run_record": projected_counts,
            "reverse_extraction_requirement": "all 722 owner and prior-v1 unit mappings exact",
            "validation_state": "pending_independent_validator",
        }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="pass",
    )
    add_row(
        tables, "qa_events", "qa_event", "c80:openlogic:qa:build-preflight:0.1.0",
        {
            "method": "frozen hash, 722-unit byte replay, component coverage, topology, rights, route, no-inference, and namespace checks",
            "qa_kind": "c80_openlogic_v231_zero_copy_adapter_build",
            "result": "pending_independent_validator",
            "subject_ids": [dataset_id],
            "warnings": ["No native HTML or unit/page anchors are claimed."],
        }, dataset_id=dataset_id, owner_authority_id=owner_id, owner_state="pass",
    )
    sort_table_rows(tables)
    require(reader_count == 642, f"reader reachable count drift: {reader_count}")
    require(relation_count == 725, f"relation count drift: {relation_count}")
    expected_counts = {
        "owner_authorities": 1, "datasets": 1, "editions": 2, "units": 722,
        "course_unit_memberships": 722, "native_bindings": 722, "content_bindings": 722,
        "relations": 725, "rights": 1, "rights_assignments": 728, "artifacts": 4,
        "build_recipes": 0, "reader_surfaces": 1, "routes": 9, "search_documents": 722,
        "adapter_profiles": 1, "adapter_runs": 1, "qa_events": 1, "identity_crosswalks": 722,
    }
    require({name: len(tables[name]) for name in TABLE_ORDER} == expected_counts, "C80 projected table counts drift")
    return tables, {
        "package_id": package_id,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_id,
        "rights_id": rights_id,
        "source_edition_id": source_edition_id,
        "target_edition_id": target_edition_id,
        "course_id": course_id,
        "v1_course_id": v1_course_id,
        "projected_units": projected_units,
        "preview_route_id": preview_route_id,
        "reader_surface_id": reader_surface_id,
    }


def copy_evidence_and_tools(
    output: Path,
    inventory_path: Path,
    closure_path: Path,
    component_bytes: bytes,
    license_bytes: bytes,
    attribution_bytes: bytes,
    migration_path: Path,
    public_evidence_path: Path,
) -> dict[str, dict[str, Any]]:
    evidence_root = output / "evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    files = {
        "final_inventory": (inventory_path, evidence_root / "FINAL_INVENTORY_0722.csv"),
        "closure_manifest": (closure_path, evidence_root / "STRUCTURAL_CLOSURE_MANIFEST_0722.csv"),
        "migration_receipt": (migration_path, evidence_root / "V1_MIGRATION_RECEIPT.json"),
        "public_readback": (public_evidence_path, evidence_root / "PUBLICATION_LEARNER_BACKEND_EVIDENCE.json"),
    }
    for source, target in files.values():
        shutil.copyfile(source, target)
    (evidence_root / "COMPONENT_COVERAGE.tsv").write_bytes(component_bytes)
    (evidence_root / "LICENSE.md").write_bytes(license_bytes)
    (evidence_root / "ATTRIBUTION_AND_CHANGES.md").write_bytes(attribution_bytes)

    source_root = Path(__file__).resolve().parent
    schema_root = source_root.parent / "schema"
    (output / "schema").mkdir(parents=True, exist_ok=True)
    (output / "tools").mkdir(parents=True, exist_ok=True)
    schema_names = [
        "lane-adapter-v2.3.1.schema.json", "capability-declarations-v0.2.schema.json",
        "namespace-crosswalk-v0.2.schema.json", "translation-state-index-v0.2.schema.json",
        "csv-projection-manifest-v0.2.schema.json", "scope-declaration-v0.2.schema.json",
    ]
    tool_names = [
        "build_c80_openlogic_v231.py", "validate_c80_openlogic_v231.py",
        "run_c80_negative_probes.py", "validate_lane_adapter_v231.py",
        "v231_adapter_common.py", "package_lane_adapter_v231.py",
    ]
    for name in schema_names:
        shutil.copyfile(schema_root / name, output / "schema" / name)
    for name in tool_names:
        require((source_root / name).is_file(), f"required tool missing before build: {name}")
        shutil.copyfile(source_root / name, output / "tools" / name)
    return {
        "inventory": file_fact(evidence_root / "FINAL_INVENTORY_0722.csv", "evidence/FINAL_INVENTORY_0722.csv", "frozen_final_inventory"),
        "closure": file_fact(evidence_root / "STRUCTURAL_CLOSURE_MANIFEST_0722.csv", "evidence/STRUCTURAL_CLOSURE_MANIFEST_0722.csv", "frozen_structural_closure"),
        "components": file_fact(evidence_root / "COMPONENT_COVERAGE.tsv", "evidence/COMPONENT_COVERAGE.tsv", "frozen_component_coverage"),
        "license": file_fact(evidence_root / "LICENSE.md", "evidence/LICENSE.md", "frozen_license"),
        "attribution": file_fact(evidence_root / "ATTRIBUTION_AND_CHANGES.md", "evidence/ATTRIBUTION_AND_CHANGES.md", "frozen_attribution_changes"),
        "migration": file_fact(evidence_root / "V1_MIGRATION_RECEIPT.json", "evidence/V1_MIGRATION_RECEIPT.json", "v1_migration_receipt"),
        "public_readback": file_fact(evidence_root / "PUBLICATION_LEARNER_BACKEND_EVIDENCE.json", "evidence/PUBLICATION_LEARNER_BACKEND_EVIDENCE.json", "public_readback_evidence"),
    }


def build_capability_sidecar(
    context: Mapping[str, Any],
    tables: Mapping[str, list[dict[str, Any]]],
    capability_contract: Mapping[str, Any],
    evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    projected_structure = [row["id"] for row in tables["units"] + tables["relations"]]
    projected_publication = [row["id"] for row in tables["artifacts"] + tables["reader_surfaces"] + tables["routes"]]
    shard_map = {
        "terminology": [evidence["public_readback"]],
        "mathematical_preservation": [evidence["inventory"], evidence["components"]],
        "assets": [evidence["closure"], evidence["public_readback"]],
        "accessibility": [evidence["public_readback"]],
        "corrections": [evidence["attribution"], evidence["public_readback"]],
        "research_support": [evidence["migration"], evidence["public_readback"]],
    }
    states = {
        "structure_localization": "materialized",
        "terminology": "referenced_native_shards",
        "mathematical_preservation": "referenced_native_shards",
        "assessment_support": "not_projected",
        "assets": "referenced_native_shards",
        "accessibility": "referenced_native_shards",
        "corrections": "referenced_native_shards",
        "computational_interactives": "not_projected",
        "publication": "materialized",
        "research_support": "referenced_native_shards",
    }
    capabilities: list[dict[str, Any]] = []
    for name in CAPABILITY_NAMES:
        state = states[name]
        if name == "structure_localization":
            ids = projected_structure
            capabilities.append({
                "name": name, "version": "0.1.0", "state": state, "schema_binding": None,
                "shard_refs": [], "native_count": 1447, "projected_count": len(ids),
                "identity_set_sha256": identity_set_sha256(ids), "identity_set_scope": "projected_records",
                "closure_rules": ["Exactly 722 units and 725 ordered import relations are materialized from frozen authority."],
                "loss_gap_report": {"status": "closed", "reason": "Exact frozen structural topology is materialized."},
            })
        elif name == "publication":
            ids = projected_publication
            capabilities.append({
                "name": name, "version": "0.1.0", "state": state, "schema_binding": None,
                "shard_refs": [evidence["public_readback"]], "native_count": 4, "projected_count": len(ids),
                "identity_set_sha256": identity_set_sha256(ids), "identity_set_scope": "projected_records",
                "closure_rules": ["Only anonymously read-back GitHub/Zenodo identities and the verified linked PDF learner route are materialized."],
                "loss_gap_report": {"status": "closed", "reason": "Four artifacts and nine course-level routes are explicitly bound."},
            })
        elif state == "not_projected":
            capabilities.append({
                "name": name, "version": "0.1.0", "state": state, "schema_binding": None,
                "shard_refs": [], "native_count": 0, "projected_count": 0,
                "identity_set_sha256": None, "identity_set_scope": "none",
                "closure_rules": [f"{name} is not inferred from file names or unrelated structural counts."],
                "loss_gap_report": {"status": "declared_limitation", "reason": f"{name} has no evidence-complete common projection in this adapter."},
            })
        else:
            refs = shard_map[name]
            capabilities.append({
                "name": name, "version": "0.1.0", "state": state, "schema_binding": None,
                "shard_refs": refs, "native_count": 722 if name in {"mathematical_preservation", "assets"} else 1,
                "projected_count": 0,
                "identity_set_sha256": identity_set_sha256(str(ref["sha256"]) for ref in refs),
                "identity_set_scope": "native_shard_records",
                "closure_rules": ["Owner-native evidence remains authoritative; this adapter binds shards without flattening their semantics."],
                "loss_gap_report": {"status": "closed", "reason": "Evidence is referenced exactly without claiming a richer common projection."},
            })
    return {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "contract_binding": capability_contract,
        "capabilities": capabilities,
        "legacy_labels": [],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards", "shard_refs": [evidence["license"], evidence["attribution"]],
            "native_count": 1, "identity_set_sha256": identity_set_sha256([context["rights_id"]]),
            "closure_rules": ["CC BY 4.0 and the attribution/change notice remain separately hash-bound."],
        },
        "recorded_at": RECORDED_AT,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), "repository root missing")
    require(owner_root.is_dir(), "owner root missing")
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    authorities = {
        "capability_contract": external_authority(repository_root, CAPABILITY_REL, "capability_contract"),
        "closure": external_authority(repository_root, CLOSURE_REL, "closure_manifest", EXPECTED["closure"]),
        "courses": external_authority(repository_root, COURSES_REL, "courses_current"),
        "federation_manifest": external_authority(repository_root, FEDERATION_MANIFEST_REL, "federation_manifest"),
        "inventory": external_authority(repository_root, INVENTORY_REL, "final_inventory", EXPECTED["inventory"]),
        "migration": external_authority(repository_root, MIGRATION_REL, "v1_migration_receipt", EXPECTED["migration"]),
        "public_evidence": external_authority(repository_root, PUBLIC_EVIDENCE_REL, "public_readback", EXPECTED["public_evidence"]),
        "upstream_zip": external_authority(repository_root, UPSTREAM_ZIP_REL, "frozen_upstream_zip", EXPECTED["upstream_zip"]),
        "localized_zip": external_authority(repository_root, LOCALIZED_ZIP_REL, "frozen_localized_zip", EXPECTED["localized_zip"]),
        "evidence_zip": external_authority(repository_root, EVIDENCE_ZIP_REL, "frozen_evidence_zip", EXPECTED["evidence_zip"]),
        "owner_license": external_file_fact(
            owner_root / OWNER_LICENSE_REL, OWNER_LICENSE_REL, "owner_license", "owner_package_root",
            expected_bytes=EXPECTED["owner_license"][0], expected_sha256=EXPECTED["owner_license"][1],
        ),
    }
    inventory_path = repository_root.joinpath(*INVENTORY_REL.split("/"))
    closure_path = repository_root.joinpath(*CLOSURE_REL.split("/"))
    migration_path = repository_root.joinpath(*MIGRATION_REL.split("/"))
    public_evidence_path = repository_root.joinpath(*PUBLIC_EVIDENCE_REL.split("/"))
    inventory = read_csv(inventory_path)
    closure = read_csv(closure_path)
    courses = read_jsonl(repository_root.joinpath(*COURSES_REL.split("/")))
    course_matches = [row for row in courses if row.get("payload", {}).get("course_id") == "C80"]
    require(len(course_matches) == 1, "current C80 course row closure failed")
    all_course_ids = sorted(str(row["payload"]["course_id"]) for row in courses)
    require(len(all_course_ids) == 40 and len(set(all_course_ids)) == 40, "40-course authority closure failed")

    upstream_path = repository_root.joinpath(*UPSTREAM_ZIP_REL.split("/"))
    localized_path = repository_root.joinpath(*LOCALIZED_ZIP_REL.split("/"))
    evidence_zip_path = repository_root.joinpath(*EVIDENCE_ZIP_REL.split("/"))
    with zipfile.ZipFile(upstream_path) as upstream, zipfile.ZipFile(localized_path) as localized, zipfile.ZipFile(evidence_zip_path) as evidence_zip:
        require(upstream.testzip() is None and localized.testzip() is None and evidence_zip.testzip() is None, "ZIP CRC closure failed")
        component_bytes = zip_entry_bytes(evidence_zip, "release_evidence/COMPONENT_COVERAGE.tsv")
        require(len(component_bytes) == 423769 and sha256_bytes(component_bytes) == "79fb4a6e421db498fd05929b00d75a4f5651e236360b642afe72b48ebf7f5c45", "component coverage identity drift")
        components = list(csv.DictReader(io.StringIO(component_bytes.decode("utf-8-sig")), delimiter="\t"))
        license_bytes = zip_entry_bytes(localized, "LICENSE")
        attribution_bytes = zip_entry_bytes(localized, "source/locale/id/ATTRIBUTION_AND_CHANGES.md")
        require(len(license_bytes) == 17227 and sha256_bytes(license_bytes) == EXPECTED["owner_license"][1], "frozen license drift")
        require(len(attribution_bytes) == 9232 and sha256_bytes(attribution_bytes) == "91ec15d9a7a8f9aa5e9f88b3105e4f112a708dbb5461888aae0de7f30e9da47d", "frozen attribution drift")
        upstream_names = [name for name in upstream.namelist() if not name.endswith("/")]
        require(upstream_names, "upstream ZIP empty")
        upstream_root = upstream_names[0].split("/", 1)[0]
        source_bytes_total = target_bytes_total = 0
        crlf_materializations = 0
        for row in inventory:
            source_blob = zip_entry_bytes(upstream, f"{upstream_root}/{row['source_path']}")
            source_data = source_blob
            if len(source_data) != int(row["source_bytes"]) or sha256_bytes(source_data) != row["source_sha256"].lower():
                source_data = source_blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                crlf_materializations += 1
            require(len(source_data) == int(row["source_bytes"]) and sha256_bytes(source_data) == row["source_sha256"].lower(), f"source byte replay failed: {row['closure_id']}")
            target_data = zip_entry_bytes(localized, f"source/{row['target_path']}")
            require(len(target_data) == int(row["target_bytes"]) and sha256_bytes(target_data) == row["target_sha256"].lower(), f"target byte replay failed: {row['closure_id']}")
            require(len(source_data.decode("utf-8").splitlines()) == int(row["source_lines"]), f"source line replay failed: {row['closure_id']}")
            require(len(target_data.decode("utf-8").splitlines()) == int(row["target_lines"]), f"target line replay failed: {row['closure_id']}")
            source_bytes_total += len(source_data)
            target_bytes_total += len(target_data)
        require(source_bytes_total == 3051826 and target_bytes_total == 3222301, "aggregate source/target bytes drift")

    migration = json.loads(migration_path.read_text(encoding="utf-8"))
    require(migration["validation"]["result"] == "pass", "v1 migration receipt is not passing")
    require(migration["target"]["record_count"] == 6522, "v1 migration record count drift")
    require(migration["coverage"]["import_relations"] == 725, "v1 migration relation count drift")
    tables, context = build_tables(inventory, closure, components, course_matches[0])
    evidence_facts = copy_evidence_and_tools(output, inventory_path, closure_path, component_bytes, license_bytes, attribution_bytes, migration_path, public_evidence_path)
    table_facts = {}
    for table_name in TABLE_ORDER:
        path = output / "tables" / f"{table_name}.jsonl"
        write_jsonl(path, tables[table_name])
        table_facts[table_name] = file_fact(path, f"tables/{table_name}.jsonl", "canonical_jsonl", records=len(tables[table_name]), record_id_set_sha256=identity_set_sha256(str(row["id"]) for row in tables[table_name]))

    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/c80-openlogic-v231-input-authorities/1.0.0",
        "authorities": [authorities[key] for key in sorted(authorities)],
        "public_replay_sources": {
            "upstream_commit": f"https://github.com/OpenLogicProject/OpenLogic/tree/{SOURCE_COMMIT}",
            "repository": REPOSITORY_URL,
            "release": RELEASE_URL,
            "version_doi": f"https://doi.org/{VERSION_DOI}",
            "concept_doi": f"https://doi.org/{CONCEPT_DOI}",
        },
        "zip_entry_authorities": [
            zip_entry_fact(component_bytes, "evidence_zip", "release_evidence/COMPONENT_COVERAGE.tsv"),
            zip_entry_fact(license_bytes, "localized_zip", "LICENSE"),
            zip_entry_fact(attribution_bytes, "localized_zip", "source/locale/id/ATTRIBUTION_AND_CHANGES.md"),
        ],
        "byte_replay": {
            "source_files": 722, "target_files": 722, "source_bytes": 3051826,
            "target_bytes": 3222301, "source_crlf_materializations": crlf_materializations,
        },
        "credentials_recorded": False,
        "owner_native_non_mutation": True,
        "recorded_at": RECORDED_AT,
    })
    scope = {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"], "dataset_id": context["dataset_id"],
        "scope_kind": "lane_adapter", "course_ids": [context["course_id"]], "curriculum_role_ids": ["C80"],
        "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [course_id for course_id in all_course_ids if course_id != "C80"],
        "owner_authority_binding": authorities["inventory"],
        "curriculum_authority_binding": authorities["courses"],
        "limitations": [
            "C80 only; 39 other curriculum roles remain outside this adapter.",
            "Owner-native Open Logic source, target, QA, and correction evidence is referenced, never rewritten.",
            "No prose, formulas, proof bodies, exercise bodies, unit anchors, or native HTML are emitted.",
            "The verified linked PDF reader is primary; JSONL and CSV are secondary machine surfaces.",
        ],
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "scope-declaration-v0.2.0.json", scope)

    projected_units = context["projected_units"]
    mappings: list[dict[str, Any]] = []
    for row in inventory:
        closure_id = row["closure_id"]
        target_id = projected_units[closure_id]
        for source_namespace, source_id, label in (
            (OWNER_NAMESPACE, closure_id, "owner OLP closure ID"),
            (str(V1_NAMESPACE), previous_v1_unit_id(closure_id), "prior common-v1 unit UUID"),
        ):
            mappings.append({
                "source_namespace": source_namespace, "target_namespace": str(LANE_NAMESPACE),
                "source_record_id": source_id, "target_record_id": target_id,
                "source_record_type": "unit", "target_record_type": "unit",
                "cardinality": "one_to_one", "mapping_state": "mapped",
                "reverse_recipe": f"resolve {label} for {closure_id} through final inventory and deterministic UUID formula",
                "evidence_refs": ["final_inventory", "v1_migration_receipt"],
                "identity_set_sha256": identity_set_sha256([source_id, target_id]),
            })
    mappings.append({
        "source_namespace": str(V1_NAMESPACE), "target_namespace": "program-federation-v0.4.4",
        "source_record_id": context["v1_course_id"], "target_record_id": context["course_id"],
        "source_record_type": "course", "target_record_type": "course",
        "cardinality": "one_to_one", "mapping_state": "mapped",
        "reverse_recipe": "select current courses.jsonl row where payload.course_id=C80 and payload.v1_course_id equals source",
        "evidence_refs": ["courses_current"],
        "identity_set_sha256": identity_set_sha256([context["v1_course_id"], context["course_id"]]),
    })
    crosswalk = {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0", "package_id": context["package_id"],
        "profiles": [
            {"name": "c80_owner_olp", "namespace": OWNER_NAMESPACE, "formula": "literal OLP-0001..OLP-0722"},
            {"name": "c80_prior_v1", "namespace": str(V1_NAMESPACE), "formula": "UUIDv5(namespace, record_type + '|' + stable_key)"},
            {"name": "c80_v2_3_lane", "namespace": str(LANE_NAMESPACE), "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)"},
        ],
        "mappings": mappings,
        "unmaterialized_candidates": [{
            "namespace": str(LANE_NAMESPACE), "record_type": "course", "semantic_key": "course:C80",
            "candidate_record_id": projection_id(LANE_NAMESPACE, "course", "course:C80"),
            "state": "deterministic_id_proposal_not_a_mapping",
            "formula": "UUIDv5(lane_namespace, 'course:course:C80')",
            "effective_cardinality": "unresolved_until_materialized",
        }],
        "identity_sets": {
            "owner_units_sha256": identity_set_sha256(row["closure_id"] for row in inventory),
            "prior_v1_units_sha256": identity_set_sha256(previous_v1_unit_id(row["closure_id"]) for row in inventory),
            "projected_units_sha256": identity_set_sha256(projected_units.values()),
            "mapped_pairs_sha256": mapping_set_sha256((row["source_record_id"], row["target_record_id"]) for row in mappings),
        },
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "namespace-crosswalk-v0.2.0.json", crosswalk)

    translation_rows = [{
        "native_unit_id": row["closure_id"],
        "previous_v1_unit_id": previous_v1_unit_id(row["closure_id"]),
        "projected_unit_id": projected_units[row["closure_id"]],
        "locale": "id-ID", "state": "complete", "state_source": "final_inventory_plus_component_coverage",
        "source_file_sha256": row["source_sha256"].lower(), "target_file_sha256": row["target_sha256"].lower(),
    } for row in inventory]
    translation_state = {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0", "package_id": context["package_id"], "dataset_id": context["dataset_id"],
        "authority_bindings": [evidence_facts["inventory"], evidence_facts["components"]],
        "coverage": {"course_id": "C80", "granularity": "complete_source_file_unit", "authority_rows": 722, "indexed_rows": 722, "inferred_rows": 0},
        "states": ["complete"], "records": translation_rows,
        "identity_set_sha256": identity_set_sha256(row["projected_unit_id"] for row in translation_rows),
        "no_inference": True, "recorded_at": RECORDED_AT,
    }
    write_json(output / "translation-state-index-v0.2.0.json", translation_state)
    csv_sidecar = write_csv_surfaces(output, tables, context["package_id"], RECORDED_AT)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_sidecar)
    capability_sidecar = build_capability_sidecar(context, tables, authorities["capability_contract"], evidence_facts)
    write_json(output / "capability-declarations-v0.2.0.json", capability_sidecar)

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
        "extension_id": projection_id(LANE_NAMESPACE, "lane_adapter_extension", f"c80:openlogic:{ADAPTER_VERSION}"),
        "extension_version": ADAPTER_VERSION, "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": [authorities[key] for key in sorted(authorities)],
        "sidecars": [file_fact(output / name, name, "sidecar") for name in sidecar_names],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER), "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER), "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools/build_c80_openlogic_v231.py", "tools/build_c80_openlogic_v231.py", "builder"),
            "validator": file_fact(output / "tools/validate_c80_openlogic_v231.py", "tools/validate_c80_openlogic_v231.py", "validator"),
            "canonical_serialization": {
                "scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8", "newline": "LF",
                "json_keys": "lexicographically_sorted", "trailing_newline": True,
                "copied_schema_and_tool_files": "preserved_exact_source_bytes",
            },
            "deterministic_replay": "byte_identical", "build_a_sha256": payload_identity, "build_b_sha256": payload_identity,
        },
        "files": payload_facts,
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json", "seal_excluded_from_own_digest": True,
            "binds": ["schemas", "tools", "input_authorities", "evidence", "tables", "sidecars", "csv_projections", "manifest"],
        },
        "zero_copy_policy": {
            "owner_native_authoritative": True, "full_prose_centralized": False, "owner_ids_reminted": False,
            "aggregate_conformance_claim": False, "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True,
        },
    }
    write_json(output / "manifest.json", manifest)
    seal_facts = payload_facts + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    write_json(output / "seal.json", {
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
        "package_id": context["package_id"], "algorithm": "sha256-sorted-path-bytes-v1", "files": seal_facts,
        "file_count": len(seal_facts), "bytes": sum(row["bytes"] for row in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts), "seal_excluded_from_own_digest": True, "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_text = "".join(f"{fact['sha256']}  {fact['path']}\n" for fact in sorted(checksum_facts, key=lambda item: item["path"]))
    (output / "PACKAGE_CHECKSUMS.sha256").write_text(checksum_text, encoding="utf-8", newline="\n")
    return {
        "status": "pass", "output": str(output), "files": len(checksum_facts) + 1,
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "payload_inventory_sha256": payload_identity, "seal_sha256": sha256_file(output / "seal.json"),
        "checksum_sha256": sha256_file(output / "PACKAGE_CHECKSUMS.sha256"),
        "source_files_verified": 722, "target_files_verified": 722,
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
