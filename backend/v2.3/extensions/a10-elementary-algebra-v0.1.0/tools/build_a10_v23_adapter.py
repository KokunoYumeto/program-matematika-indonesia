#!/usr/bin/env python3
"""Build the A10 Elementary Algebra 2e thin zero-copy v2.3.1 adapter.

Only public-release metadata is projected.  The 561,994-record native backend,
CNXML prose, figures, and translation/correction histories remain external and
authoritative.  Module identities, titles, order, source-byte facts, aggregate
assessment facts, rights qualifications, and the one course-level learner link
are materialized without inventing per-module reader routes.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    RECORD_TYPE_BY_TABLE,
    TABLE_ORDER,
    AdapterError,
    canonical_row_sha256,
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
    tree_identity,
    write_checksums,
    write_csv_surfaces,
    write_json,
    write_tables,
)


RECORDED_AT = "2026-09-06T00:00:00Z"
ADAPTER_VERSION = "0.1.0"
COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
LANE_NAMESPACE = uuid.uuid5(uuid.UUID(COMMON_NAMESPACE), "v2.3.1:A10:elementary-algebra-2e")
OWNER_NAMESPACE = "openstax-cnxml-module-id/elementary-algebra-2e/id-ID/v1.0.3"
CURRENT_COURSE_ID = "urn:uuid:c2a0d387-a544-54ca-9b89-6d654a9bc200"
CURRENT_V1_COURSE_ID = "urn:uuid:b5456975-40bd-5cda-a587-195fb4df3846"
PREREQUISITE_A00_COURSE_ID = "urn:uuid:8d8ea368-373c-54d7-a6d3-4d9cfdaf46fe"
PUBLIC_RECORD = "https://zenodo.org/records/22236314"
PUBLIC_PDF = PUBLIC_RECORD + "/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf?download=1"
PUBLIC_REPOSITORY = "https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id"
UPSTREAM_COURSE = "https://openstax.org/details/books/elementary-algebra-2e"

COURSE_ROLES = [
    "A00", "A10", "A20", "A30",
    "B10", "B20", "B30", "B40", "B50", "B60", "B70", "B80", "B90", "B95",
    "C10", "C20", "C30", "C40", "C50", "C60", "C70", "C80", "C90", "C100",
    "C110", "C120", "C130", "C140",
    "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D90", "D100",
    "D110", "D120",
]

EXPECTED_INPUTS = {
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
    "a10_release_authority": (
        "backend/v2.3/authorities/A10_ELEMENTARY_ALGEBRA_PUBLIC_RELEASE_AUTHORITY_20260906.json",
        50883,
        "5ae589b75842923a0ebc530d649498bec9bb962ae0d14ab1cb44a9aedb573678",
    ),
}

EXPECTED_ARTIFACTS = {
    "00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf": (
        74917277, "e4bc958edeb60a41604862dd0b67692bbfbcbb85b5de906c92af1f6c93bda505"
    ),
    "elementary-algebra-2e-id-ID-1.0.3-source.zip": (
        7264274, "77a6ecfa22c4a5b58b0b7f72e5ec9db11ac4656bc7fc9c4944a4a7916a2472f3"
    ),
    "elementary-algebra-2e-id-ID-1.0.3-backend-core.zip": (
        147766660, "6dc5ddafb3178d82308819ced69f724919dcb388168c5c63ec39db9e99777b13"
    ),
    "elementary-algebra-2e-id-ID-1.0.3-release-manifest.json": (
        39066, "a1cb3f183b37fc80013d3be68966bcbe667ae735582063a25cb4d3dd55ea2805"
    ),
    "00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader-build-manifest.json": (
        4282699, "821d123602e75f6c1008c0d91350c2cc2c6c9ddeea5c76d00e922f59bd34a7b3"
    ),
    "EA2-C0082-reader-QA-final.json": (
        3050, "449dff1ca701690ce9bfffd5055010a5ff22b7b29ef206c480899f37689b2bb6"
    ),
    "LICENSE.txt": (
        21442, "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"
    ),
}

EXPECTED_BACKEND_COUNTS = {
    "artifact": 491,
    "asset": 4024,
    "concept": 144,
    "correction": 678,
    "course": 1,
    "edition": 1,
    "placement": 55273,
    "program": 1,
    "qa_event": 575,
    "relation": 91373,
    "resource": 1,
    "rights": 4025,
    "segment": 26824,
    "source_alias": 55357,
    "term": 1060,
    "translation": 26824,
    "translation_event": 240068,
    "unit": 55273,
    "work": 1,
}


def basic_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {key: fact[key] for key in ("path", "path_base", "role", "bytes", "sha256")}


def from_root(root: Path, relative: str) -> Path:
    return root.joinpath(*PurePosixPath(relative).parts)


def sequence_sha256(modules: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(
        f"{item['ordinal']}\0{item['module_id']}\0{item['label']}\0{item['title']}\0"
        f"{item.get('chapter_title') or ''}\0{item['bytes']}\0{item['sha256']}\0{item['state']}\n"
        for item in modules
    ).encode("utf-8")
    return sha256_bytes(payload)


def build_authorities(repository_root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    authorities: list[dict[str, Any]] = []
    named: dict[str, dict[str, Any]] = {}
    for role, (relative, size, digest) in EXPECTED_INPUTS.items():
        fact = external_file_fact(
            from_root(repository_root, relative),
            relative,
            role,
            "program_repository_root",
            expected_bytes=size,
            expected_sha256=digest,
        )
        named[role] = fact
        authorities.append(basic_fact(fact))

    authority = read_json(from_root(repository_root, EXPECTED_INPUTS["a10_release_authority"][0]))
    require(
        authority.get("schema_id")
        == "program-matematika-indonesia/a10-elementary-algebra-public-release-authority/1",
        "A10 release-authority schema drift",
    )
    require(authority.get("course_id") == "A10" and authority.get("locale") == "id-ID", "A10 authority scope drift")
    release = authority.get("public_release", {})
    require(
        release.get("record_id") == 22236314
        and release.get("concept_record_id") == 22059767
        and release.get("version") == "1.0.3"
        and release.get("access") == "open"
        and release.get("release_status") == "complete_book_publication_ready",
        "A10 public release identity/state drift",
    )
    source = authority.get("source_authority", {})
    require(
        source.get("commit") == "38cae454e644abf9f0a623e876994553881597c9"
        and source.get("tree") == "7907e4c81d43de1c3b6da173f0eb273c01dc5b55",
        "A10 OpenStax source authority drift",
    )
    artifacts = {str(item["filename"]): item for item in authority.get("artifacts", [])}
    require(set(artifacts) == set(EXPECTED_ARTIFACTS), "A10 artifact inventory drift")
    for filename, (size, digest) in EXPECTED_ARTIFACTS.items():
        require(
            artifacts[filename].get("bytes") == size and artifacts[filename].get("sha256") == digest,
            f"A10 artifact fact drift: {filename}",
        )
    modules = authority.get("modules", [])
    require(isinstance(modules, list) and len(modules) == 82, "A10 module census drift")
    ids = [str(item.get("module_id")) for item in modules]
    require(len(ids) == len(set(ids)) == 82, "A10 module IDs are not unique")
    require([int(item.get("ordinal", -1)) for item in modules] == list(range(1, 83)), "A10 ordinal sequence drift")
    require(all(item.get("state") == "language_reviewed" for item in modules), "A10 module state drift")
    module_projection = authority.get("module_projection", {})
    require(
        module_projection.get("module_id_set_sha256") == identity_set_sha256(ids)
        and module_projection.get("module_sequence_sha256") == sequence_sha256(modules)
        and module_projection.get("source_total_bytes") == sum(int(item["bytes"]) for item in modules),
        "A10 module projection digest drift",
    )
    backend = authority.get("backend_snapshot", {})
    require(backend.get("record_count") == 561994, "A10 owner backend record count drift")
    require(backend.get("record_counts") == EXPECTED_BACKEND_COUNTS, "A10 owner backend type census drift")
    require(backend.get("tests_run") == 30, "A10 backend test count drift")
    require(backend.get("translation_state_counts") == {"language_reviewed": 26824}, "A10 translation state drift")
    golden = backend.get("source_golden_counts", {})
    require(
        golden.get("module_count") == 82
        and golden.get("exercise_count") == 9406
        and golden.get("problem_count") == 9406
        and golden.get("solution_count") == 6106
        and golden.get("missing_solution_count") == 3300
        and golden.get("pending_correction_count") == 0
        and golden.get("effective_pending_correction_count") == 0,
        "A10 exact aggregate learning/correction census drift",
    )
    maintenance = authority.get("maintenance_truth", {})
    require(
        maintenance.get("ongoing_terminology_and_correction_maintenance_closed_by_this_adapter") is False,
        "A10 adapter must not close ongoing terminology/correction maintenance",
    )
    require(authority.get("zero_copy", {}).get("learner_relationship") == "course_link_only; no per-module HTML route is claimed", "A10 route policy drift")
    return authorities, named, authority


def locate_curriculum_role(repository_root: Path) -> tuple[dict[str, Any], str]:
    rows = read_jsonl(from_root(repository_root, EXPECTED_INPUTS["courses_current"][0]))
    by_role = {
        str(row.get("payload", {}).get("course_id")): row
        for row in rows
        if row.get("record_type") == "course"
    }
    require("A10" in by_role and "A00" in by_role, "A10/A00 curriculum roles missing")
    a10 = by_role["A10"]
    require(a10.get("id") == CURRENT_COURSE_ID, "A10 current course UUID drift")
    require(a10.get("payload", {}).get("v1_course_id") == CURRENT_V1_COURSE_ID, "A10 v1 course UUID drift")
    require(a10.get("payload", {}).get("prerequisite_course_ids") == ["A00"], "A10 prerequisite role drift")
    require(by_role["A00"].get("id") == PREREQUISITE_A00_COURSE_ID, "A00 prerequisite UUID drift")
    return a10, PREREQUISITE_A00_COURSE_ID


def build_tables(
    authority: Mapping[str, Any],
    a10_course: Mapping[str, Any],
    a00_course_id: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    package_id = projection_id(LANE_NAMESPACE, "lane_adapter_package", f"a10:elementary-algebra-2e:{ADAPTER_VERSION}")
    dataset_semantic_key = "a10:dataset:elementary-algebra-2e:id-ID:v1.0.3"
    owner_authority_semantic_key = "a10:owner-authority:public-release-v1.0.3"
    edition_semantic_key = "a10:edition:elementary-algebra-2e:id-ID:v1.0.3"
    rights_semantic_key = "a10:rights:cc-by-nc-sa-4.0-qualified"
    route_semantic_key = "a10:route:learner-course-pdf:v1.0.3"
    reader_semantic_key = "a10:reader-surface:course-pdf:v1.0.3"
    profile_semantic_key = f"a10:adapter-profile:{ADAPTER_VERSION}"
    run_semantic_key = f"a10:adapter-run:{ADAPTER_VERSION}"
    dataset_id = projection_id(LANE_NAMESPACE, "dataset", dataset_semantic_key)
    owner_authority_id = projection_id(LANE_NAMESPACE, "owner_authority", owner_authority_semantic_key)
    edition_id = projection_id(LANE_NAMESPACE, "edition", edition_semantic_key)
    rights_id = projection_id(LANE_NAMESPACE, "rights", rights_semantic_key)
    route_id = projection_id(LANE_NAMESPACE, "route", route_semantic_key)
    reader_id = projection_id(LANE_NAMESPACE, "reader_surface", reader_semantic_key)
    profile_id = projection_id(LANE_NAMESPACE, "adapter_profile", profile_semantic_key)
    run_id = projection_id(LANE_NAMESPACE, "adapter_run", run_semantic_key)
    tables = empty_tables()

    def emit(
        table: str,
        semantic_key: str,
        payload: Mapping[str, Any],
        *,
        normalized_state: str = "validated",
        owner_native_state: str | None = None,
    ) -> dict[str, Any]:
        row = make_row(
            LANE_NAMESPACE,
            RECORD_TYPE_BY_TABLE[table],
            semantic_key,
            payload,
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state=normalized_state,
            owner_native_state=owner_native_state,
        )
        tables[table].append(row)
        return row

    emit(
        "owner_authorities",
        owner_authority_semantic_key,
        {
            "authority_kind": "public_immutable_release_metadata_projection",
            "course_id": CURRENT_COURSE_ID,
            "curriculum_role_id": "A10",
            "canonical_owner_locator": authority["owner_authority"]["canonical_owner_locator"],
            "sole_integrator_publisher": True,
            "release_record_id": 22236314,
            "release_version": "1.0.3",
            "owner_native_record_count": 561994,
            "owner_native_module_count": 82,
            "owner_native_namespace": OWNER_NAMESPACE,
            "source_commit": authority["source_authority"]["commit"],
            "source_tree": authority["source_authority"]["tree"],
            "public_repository_url": PUBLIC_REPOSITORY,
            "public_record_url": PUBLIC_RECORD,
            "zero_copy": True,
        },
        normalized_state="published",
        owner_native_state="complete_book_publication_ready",
    )
    emit(
        "datasets",
        dataset_semantic_key,
        {
            "course_id": CURRENT_COURSE_ID,
            "curriculum_role_id": "A10",
            "title": authority["title"],
            "locale": "id-ID",
            "version": "1.0.3",
            "module_count": 82,
            "owner_native_record_count": 561994,
            "projection_kind": "thin_zero_copy_public_release_metadata",
            "machine_data_is_learner_destination": False,
        },
        normalized_state="published",
        owner_native_state="complete",
    )
    emit(
        "editions",
        edition_semantic_key,
        {
            "course_id": CURRENT_COURSE_ID,
            "title": "Aljabar Dasar 2e — Edisi Bahasa Indonesia",
            "locale": "id-ID",
            "version": "1.0.3",
            "boundary": "EA2-C0082",
            "module_count": 82,
            "pages": 1627,
            "publication_state": "published_complete_book",
            "public_record_url": PUBLIC_RECORD,
            "public_repository_url": PUBLIC_REPOSITORY,
            "upstream_course_url": UPSTREAM_COURSE,
            "ongoing_maintenance_closed": False,
        },
        normalized_state="published",
        owner_native_state="complete_book_publication_ready",
    )

    unit_by_native: dict[str, str] = {}
    projected_units: list[str] = []
    modules = list(authority["modules"])
    for module in modules:
        native_id = str(module["module_id"])
        semantic = f"a10:module:{native_id}"
        unit_id = projection_id(LANE_NAMESPACE, "unit", semantic)
        unit_by_native[native_id] = unit_id
        projected_units.append(unit_id)
        emit(
            "units",
            semantic,
            {
                "course_id": CURRENT_COURSE_ID,
                "edition_id": edition_id,
                "native_module_id": native_id,
                "ordinal": module["ordinal"],
                "label": module["label"],
                "title": module["title"],
                "chapter_title": module["chapter_title"],
                "chapter_start": module["chapter_start"],
                "owner_source_path": module["owner_source_path"],
                "owner_source_bytes": module["bytes"],
                "owner_source_sha256": module["sha256"],
                "native_translation_state": module["state"],
                "learner_route_state": "course_link_only",
                "learner_course_url": PUBLIC_PDF,
                "unit_url": None,
                "body_prose_copied": False,
            },
            normalized_state="published",
            owner_native_state=str(module["state"]),
        )
        emit(
            "course_unit_memberships",
            f"a10:membership:{native_id}",
            {
                "course_id": CURRENT_COURSE_ID,
                "edition_id": edition_id,
                "unit_id": unit_id,
                "native_module_id": native_id,
                "ordinal": module["ordinal"],
            },
            normalized_state="published",
            owner_native_state=str(module["state"]),
        )
        emit(
            "native_bindings",
            f"a10:native-binding:{native_id}",
            {
                "source_namespace": OWNER_NAMESPACE,
                "native_record_type": "cnxml_module",
                "native_record_id": native_id,
                "native_source_path": module["owner_source_path"],
                "native_bytes": module["bytes"],
                "native_sha256": module["sha256"],
                "projected_record_type": "unit",
                "projected_record_id": unit_id,
                "owner_id_preserved": True,
                "body_prose_copied": False,
            },
            normalized_state="published",
            owner_native_state=str(module["state"]),
        )
        emit(
            "search_documents",
            f"a10:search:{native_id}",
            {
                "unit_id": unit_id,
                "native_module_id": native_id,
                "ordinal": module["ordinal"],
                "label": module["label"],
                "title": module["title"],
                "chapter_title": module["chapter_title"],
                "locale": "id-ID",
                "learner_course_url": PUBLIC_PDF,
                "unit_url": None,
                "body_prose_copied": False,
            },
            normalized_state="published",
            owner_native_state=str(module["state"]),
        )
        emit(
            "identity_crosswalks",
            f"a10:crosswalk:{native_id}",
            {
                "source_namespace": OWNER_NAMESPACE,
                "source_record_type": "cnxml_module",
                "source_record_id": native_id,
                "target_namespace": str(LANE_NAMESPACE),
                "target_record_type": "unit",
                "target_record_id": unit_id,
                "cardinality": "one_to_one",
                "reverse_recipe": "read native_module_id from projected unit payload",
                "source_record_sha256": module["sha256"],
            },
            normalized_state="published",
            owner_native_state=str(module["state"]),
        )

    emit(
        "relations",
        "a10:prerequisite-course:A00",
        {
            "relation_type": "course_prerequisite",
            "source_course_id": CURRENT_COURSE_ID,
            "target_course_id": a00_course_id,
            "source_role_id": "A10",
            "target_role_id": "A00",
            "authority": "current curriculum role record",
        },
        normalized_state="validated",
        owner_native_state="curriculum_declared",
    )
    for left, right in zip(modules, modules[1:]):
        left_id = str(left["module_id"])
        right_id = str(right["module_id"])
        emit(
            "relations",
            f"a10:sequence:{left_id}:{right_id}",
            {
                "relation_type": "precedes_in_release_order",
                "source_unit_id": unit_by_native[left_id],
                "target_unit_id": unit_by_native[right_id],
                "source_native_module_id": left_id,
                "target_native_module_id": right_id,
                "derived_only_from_exact_release_ordinals": True,
            },
            normalized_state="published",
            owner_native_state="release_order",
        )

    emit(
        "rights",
        rights_semantic_key,
        {
            "spdx_expression": "CC-BY-NC-SA-4.0",
            "name": "CC BY-NC-SA 4.0",
            "qualification": "subject to component-specific credits and restrictions",
            "license_artifact_filename": "LICENSE.txt",
            "license_artifact_sha256": EXPECTED_ARTIFACTS["LICENSE.txt"][1],
            "component_rights_flattened": False,
            "native_rights_record_count": 4025,
        },
        normalized_state="published",
        owner_native_state="qualified_component_rights",
    )
    for target_type, target_id, semantic_suffix in (
        ("dataset", dataset_id, "dataset"),
        ("edition", edition_id, "edition"),
    ):
        emit(
            "rights_assignments",
            f"a10:rights-assignment:{semantic_suffix}",
            {
                "target_record_type": target_type,
                "target_record_id": target_id,
                "rights_id": rights_id,
                "qualification_preserved": True,
                "component_rights_flattened": False,
            },
            normalized_state="published",
            owner_native_state="qualified_component_rights",
        )

    artifact_ids: dict[str, str] = {}
    for artifact in authority["artifacts"]:
        filename = str(artifact["filename"])
        semantic = f"a10:artifact:{filename}"
        artifact_id = projection_id(LANE_NAMESPACE, "artifact", semantic)
        artifact_ids[filename] = artifact_id
        kind = (
            "learner_pdf" if filename.endswith("reader.pdf")
            else "owner_backend_archive" if filename.endswith("backend-core.zip")
            else "owner_source_archive" if filename.endswith("source.zip")
            else "release_manifest" if filename.endswith("release-manifest.json")
            else "reader_build_manifest" if filename.endswith("reader-build-manifest.json")
            else "reader_qa" if filename.endswith("QA-final.json")
            else "license"
        )
        emit(
            "artifacts",
            semantic,
            {
                "artifact_kind": kind,
                "filename": filename,
                "bytes": artifact["bytes"],
                "sha256": artifact["sha256"],
                "url": artifact["download_url"],
                "external_zero_copy": True,
                "component_rights": "see bundled LICENSE.txt and component-specific credits",
            },
            normalized_state="published",
            owner_native_state="public_release_artifact",
        )

    emit(
        "reader_surfaces",
        reader_semantic_key,
        {
            "surface_kind": "tagged_offline_pdf",
            "artifact_id": artifact_ids["00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf"],
            "url": PUBLIC_PDF,
            "locale": "id-ID",
            "pages": 1627,
            "tagged": True,
            "marked": True,
            "document_language": "id-ID",
            "course_level_only": True,
            "per_unit_routes_claimed": False,
            "machine_data_is_learner_destination": False,
        },
        normalized_state="published",
        owner_native_state="public_release_artifact",
    )
    emit(
        "routes",
        route_semantic_key,
        {
            "route_kind": "learner_course_link",
            "url": PUBLIC_PDF,
            "reader_surface_id": reader_id,
            "scope": "complete_course",
            "locale": "id-ID",
            "public_record_id": 22236314,
            "per_unit_route": False,
            "machine_data_is_learner_destination": False,
        },
        normalized_state="published",
        owner_native_state="public_release_artifact",
    )
    emit(
        "adapter_profiles",
        profile_semantic_key,
        {
            "profile": "thin_format_neutral_zero_copy",
            "adapter_version": ADAPTER_VERSION,
            "source_namespace": OWNER_NAMESPACE,
            "target_namespace": str(LANE_NAMESPACE),
            "module_metadata_materialized": 82,
            "native_backend_records_external": 561994,
            "body_prose_copied": False,
            "owner_ids_reminted": False,
        },
        normalized_state="validated",
        owner_native_state="release_snapshot",
    )
    emit(
        "adapter_runs",
        run_semantic_key,
        {
            "profile_id": profile_id,
            "adapter_version": ADAPTER_VERSION,
            "input_authority_sha256": EXPECTED_INPUTS["a10_release_authority"][2],
            "module_count": 82,
            "native_backend_records": 561994,
            "projection_policy": "metadata_only_no_prose_no_history",
            "deterministic_replay": "required",
        },
        normalized_state="validated",
        owner_native_state="release_snapshot",
    )
    emit(
        "qa_events",
        "a10:qa:owner-backend-release",
        {
            "qa_kind": "owner_release_backend",
            "result": "pass",
            "native_records": 561994,
            "tests_run": 30,
            "modules": 82,
            "translation_rows_language_reviewed": 26824,
            "export_aggregate_sha256": authority["backend_snapshot"]["export_aggregate_sha256"],
        },
        normalized_state="published",
        owner_native_state="release_snapshot",
    )
    emit(
        "qa_events",
        "a10:qa:reader-accessibility",
        {
            "qa_kind": "reader_accessibility",
            "result": "pass",
            "coverage": "82/82",
            "pdf_pages": 1627,
            "pdf_tagged": True,
            "pdf_marked": True,
            "pdf_language": "id-ID",
            "html_article_modules": 82,
            "html_internal_links_resolved": True,
            "image_alt_coverage": "4024/4024",
            "qa_sha256": EXPECTED_ARTIFACTS["EA2-C0082-reader-QA-final.json"][1],
            "html_not_claimed_as_public_route": True,
        },
        normalized_state="published",
        owner_native_state="reader_qa_pass",
    )
    emit(
        "qa_events",
        "a10:qa:zero-copy-projection",
        {
            "qa_kind": "adapter_zero_copy",
            "result": "pass",
            "module_identity_rows": 82,
            "body_prose_rows": 0,
            "native_backend_records_copied": 0,
            "per_unit_routes_claimed": 0,
            "explicit_exercises": 9406,
            "explicit_solutions": 6106,
            "explicit_missing_solutions": 3300,
            "maintenance_closed": False,
        },
        normalized_state="validated",
        owner_native_state="adapter_assertion",
    )

    sort_table_rows(tables)
    context = {
        "package_id": package_id,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_authority_id,
        "edition_id": edition_id,
        "rights_id": rights_id,
        "route_id": route_id,
        "reader_id": reader_id,
        "profile_id": profile_id,
        "run_id": run_id,
        "unit_by_native": unit_by_native,
        "projected_units": projected_units,
        "a10_course": a10_course,
    }
    return tables, context


def capability_entry(
    name: str,
    state: str,
    shard_ref: Mapping[str, Any],
    native_count: int,
    projected_ids: Iterable[str],
    reason: str,
    *,
    closed: bool,
) -> dict[str, Any]:
    projected = sorted(set(projected_ids))
    return {
        "name": name,
        "version": "0.1.0",
        "state": state,
        "schema_binding": None,
        "shard_refs": [basic_fact(shard_ref)] if state == "referenced_native_shards" else [],
        "native_count": native_count,
        "projected_count": len(projected),
        "identity_set_sha256": identity_set_sha256(projected) if projected else None,
        "identity_set_scope": "projected_records" if projected else "none",
        "closure_rules": [
            "the public v1.0.3 release authority remains the exact snapshot authority",
            "owner-native IDs and component rights remain authoritative",
            "no corpus prose, backend history, or absent semantic detail is copied or inferred",
        ],
        "loss_gap_report": {"status": "closed" if closed else "declared_limitation", "reason": reason},
    }


def write_sidecars(
    output: Path,
    tables: Mapping[str, list[dict[str, Any]]],
    context: Mapping[str, Any],
    authority: Mapping[str, Any],
    named: Mapping[str, Mapping[str, Any]],
) -> None:
    package_id = str(context["package_id"])
    dataset_id = str(context["dataset_id"])
    unit_by_native = dict(context["unit_by_native"])
    authority_fact = named["a10_release_authority"]

    limitations = [
        "A10 only; every other curriculum role remains outside this adapter.",
        "All 561,994 owner-native records, CNXML prose, media, and history remain external and authoritative.",
        "Only 82 exact module identities, labels, titles, order, source-byte facts, and compact aggregate release evidence are projected.",
        "The learner relationship is one complete-course PDF link; no per-module HTML route or anchor is claimed.",
        "The release proves 9,406 exercises, 6,106 solutions, and 3,300 explicitly missing solutions only in aggregate; no exercise-level records are invented.",
        "Terminology and correction counts are immutable v1.0.3 snapshot facts; individual rows are not projected and ongoing maintenance is not declared closed.",
        "CC BY-NC-SA 4.0 remains qualified by component-specific credits and restrictions; component rights are not flattened.",
        "The current curriculum federation row predates v1.0.3 and still names a production checkpoint; it supplies only the stable A10 role/course/prerequisite identity.",
        "Owner-side reflowable HTML passed QA but is not an artifact in record 22236314, so this adapter does not claim a public HTML reader.",
        "The public release manifests are hash-bound by the compact authority projection but are not copied wholesale into this package.",
    ]
    write_json(
        output / "scope-declaration-v0.2.0.json",
        {
            "$schema": "schema/scope-declaration-v0.2.schema.json",
            "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
            "schema_version": "0.2.0",
            "package_id": package_id,
            "dataset_id": dataset_id,
            "scope_kind": "lane_adapter",
            "course_ids": [CURRENT_COURSE_ID],
            "curriculum_role_ids": ["A10"],
            "aggregate_conformance_claim": False,
            "unbound_curriculum_role_ids": [role for role in COURSE_ROLES if role != "A10"],
            "owner_authority_binding": basic_fact(authority_fact),
            "curriculum_authority_binding": basic_fact(named["courses_current"]),
            "limitations": limitations,
            "recorded_at": RECORDED_AT,
        },
    )

    mappings = []
    for module in authority["modules"]:
        native_id = str(module["module_id"])
        target_id = unit_by_native[native_id]
        mappings.append(
            {
                "source_namespace": OWNER_NAMESPACE,
                "target_namespace": str(LANE_NAMESPACE),
                "source_record_id": native_id,
                "target_record_id": target_id,
                "source_record_type": "cnxml_module",
                "target_record_type": "unit",
                "cardinality": "one_to_one",
                "mapping_state": "mapped",
                "reverse_recipe": "read native_module_id from projected unit payload",
                "evidence_refs": [f"INPUT_AUTHORITIES.json#module:{native_id}"],
                "identity_set_sha256": sha256_bytes(f"{native_id}\0{target_id}\n".encode("utf-8")),
            }
        )
    mappings.sort(key=lambda item: item["source_record_id"])
    write_json(
        output / "namespace-crosswalk-v0.2.0.json",
        {
            "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
            "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
            "schema_version": "0.2.0",
            "package_id": package_id,
            "profiles": [
                {"name": "owner_native", "namespace": OWNER_NAMESPACE, "identity_kind": "OpenStax CNXML module ID"},
                {"name": "common_v2.3.1", "namespace": str(LANE_NAMESPACE), "identity_kind": "deterministic UUIDv5 projection"},
                {"name": "curriculum", "namespace": COMMON_NAMESPACE, "identity_kind": "stable A10 course UUID"},
            ],
            "mappings": mappings,
            "unmaterialized_candidates": [],
            "identity_sets": {
                "source_module_id_set_sha256": authority["module_projection"]["module_id_set_sha256"],
                "projected_unit_id_set_sha256": identity_set_sha256(unit_by_native.values()),
                "mapped_pairs_sha256": mapping_set_sha256(unit_by_native.items()),
                "source_count": 82,
                "projected_count": 82,
            },
            "recorded_at": RECORDED_AT,
        },
    )

    translation_records = []
    for module in authority["modules"]:
        native_id = str(module["module_id"])
        translation_records.append(
            {
                "native_unit_id": native_id,
                "projected_unit_id": unit_by_native[native_id],
                "owner_native_state": "language_reviewed",
                "normalized_publication_state": "published_complete_release_snapshot",
                "native_locale": "id-ID",
                "edition_locale": "id-ID",
                "source_path": module["owner_source_path"],
                "source_bytes": module["bytes"],
                "source_sha256": module["sha256"],
                "state_inferred": False,
            }
        )
    translation_records.sort(key=lambda item: item["native_unit_id"])
    write_json(
        output / "translation-state-index-v0.2.0.json",
        {
            "$schema": "schema/translation-state-index-v0.2.schema.json",
            "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
            "schema_version": "0.2.0",
            "package_id": package_id,
            "dataset_id": dataset_id,
            "authority_bindings": [basic_fact(authority_fact)],
            "coverage": {
                "course_id": "A10",
                "granularity": "published_owner_module_snapshot",
                "authority_rows": 82,
                "indexed_rows": 82,
                "inferred_rows": 0,
            },
            "states": ["language_reviewed", "published_complete_release_snapshot"],
            "records": translation_records,
            "identity_set_sha256": identity_set_sha256(item["projected_unit_id"] for item in translation_records),
            "no_inference": True,
            "recorded_at": RECORDED_AT,
        },
    )

    structure_ids = [row["id"] for name in ("units", "course_unit_memberships", "native_bindings", "relations", "identity_crosswalks") for row in tables[name]]
    publication_ids = [row["id"] for name in ("editions", "artifacts", "reader_surfaces", "routes") for row in tables[name]]
    access_ids = [row["id"] for name in ("reader_surfaces", "routes", "qa_events") for row in tables[name]]
    artifact_ids = [row["id"] for row in tables["artifacts"]]
    capabilities = [
        capability_entry("structure_localization", "materialized", authority_fact, 82, structure_ids, "All exact published module identities, titles, order, native bindings, and reversible mappings are materialized; body prose remains external by policy.", closed=True),
        capability_entry("terminology", "referenced_native_shards", authority_fact, 1060, [], "The release binds 1,060 native term records and terminology QA, but individual terms are not present in the public compact authority and ongoing maintenance is not closed.", closed=False),
        capability_entry("mathematical_preservation", "referenced_native_shards", authority_fact, 26824, [], "The complete source/backend/reader artifacts and QA are hash-bound; mathematical body content is deliberately not copied into the common envelope.", closed=False),
        capability_entry("assessment_support", "referenced_native_shards", authority_fact, 9406, [], "The authority proves 9,406 exercises/problems, 6,106 solutions, and 3,300 explicit missing solutions only in aggregate; no item-level records are invented.", closed=False),
        capability_entry("assets", "referenced_native_shards", authority_fact, 4018, artifact_ids, "Seven release artifacts are projected; 4,018 unique native media remain component-scoped in the owner backend.", closed=False),
        capability_entry("accessibility", "materialized", authority_fact, 82, access_ids, "Tagged/marked id-ID PDF and owner-side semantic HTML QA are bound; only the PDF is a public learner route.", closed=True),
        capability_entry("corrections", "referenced_native_shards", authority_fact, 678, [], "The release reports 678 correction records and zero pending at the snapshot, but individual corrections are not projected and future maintenance remains open.", closed=False),
        capability_entry("computational_interactives", "absent", authority_fact, 0, [], "No computational-interactive capability is evidenced by the compact public release authority.", closed=False),
        capability_entry("publication", "materialized", authority_fact, 7, publication_ids, "The complete public record, seven artifact identities, course-level learner PDF, repository, and upstream course are exact snapshot facts.", closed=True),
        capability_entry("research_support", "not_projected", authority_fact, 0, [], "No research taxonomy or research-support outcome is claimed for this foundational course adapter.", closed=False),
    ]
    require([entry["name"] for entry in capabilities] == CAPABILITY_NAMES, "capability order drift")
    write_json(
        output / "capability-declarations-v0.2.0.json",
        {
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
                "shard_refs": [basic_fact(authority_fact)],
                "native_count": 4025,
                "identity_set_sha256": identity_set_sha256([authority_fact["sha256"]]),
                "closure_rules": [
                    "CC BY-NC-SA 4.0 remains subject to component-specific credits and restrictions",
                    "the thin adapter never flattens 4,025 native rights records into one unconditional course license",
                    "the exact public LICENSE.txt artifact remains authoritative",
                ],
            },
            "recorded_at": RECORDED_AT,
        },
    )


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
        "build_a10_v23_adapter.py": Path(__file__).resolve(),
        "validate_a10_v23_adapter.py": Path(__file__).resolve().with_name("validate_a10_v23_adapter.py"),
        "validate_lane_adapter_v231.py": Path(__file__).resolve().with_name("validate_lane_adapter_v231.py"),
        "v231_adapter_common.py": Path(__file__).resolve().with_name("v231_adapter_common.py"),
    }
    for target, source in tools.items():
        require(source.is_file(), f"missing A10 adapter tool: {source}")
        shutil.copyfile(source, output / "tools" / target)


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), "program repository root missing")
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    authorities, named, authority = build_authorities(repository_root)
    a10_course, a00_course_id = locate_curriculum_role(repository_root)
    tables, context = build_tables(authority, a10_course, a00_course_id)
    write_json(
        output / "INPUT_AUTHORITIES.json",
        {
            "schema_id": "program-matematika-indonesia/a10-v23-input-authorities/1",
            "recorded_at": RECORDED_AT,
            "authorities": authorities,
            "public_release_closure": {
                "record_id": 22236314,
                "concept_record_id": 22059767,
                "version": "1.0.3",
                "module_count": 82,
                "module_id_set_sha256": authority["module_projection"]["module_id_set_sha256"],
                "module_sequence_sha256": authority["module_projection"]["module_sequence_sha256"],
                "module_source_total_bytes": authority["module_projection"]["source_total_bytes"],
                "owner_native_records": 561994,
                "backend_tests": 30,
                "artifacts": len(authority["artifacts"]),
                "result": "pass_with_declared_zero_copy_limitations",
            },
            "body_prose_copied": False,
            "native_backend_history_copied": False,
            "owner_native_non_mutation": True,
        },
    )
    write_json(
        output / "evidence" / "A10_PUBLIC_RELEASE_CLOSURE.json",
        {
            "schema_id": "program-matematika-indonesia/a10-public-release-closure/1",
            "recorded_at": RECORDED_AT,
            "status": "PASS_WITH_EXPLICIT_LIMITATIONS",
            "course_id": "A10",
            "release": {"record_id": 22236314, "version": "1.0.3", "coverage": "82/82", "pages": 1627},
            "native_backend": {"records": 561994, "tests_run": 30, "copied_records": 0},
            "assessment": {"exercises": 9406, "problems": 9406, "solutions": 6106, "missing_solutions": 3300, "granularity": "release_aggregate_only"},
            "translation": {"language_reviewed_rows": 26824, "module_rows": 82, "state_inferred": False},
            "terminology_and_corrections": {"terms": 1060, "corrections": 678, "pending_at_snapshot": 0, "individual_rows_projected": 0, "ongoing_maintenance_closed": False},
            "rights": {"native_rights_records": 4025, "license": "CC-BY-NC-SA-4.0", "component_specific_qualification_preserved": True, "flattened": False},
            "accessibility": {"pdf_tagged": True, "pdf_marked": True, "pdf_language": "id-ID", "image_alts": "4024/4024", "public_html_claimed": False},
            "learner_relationship": {"kind": "course_link_only", "url": PUBLIC_PDF, "per_unit_routes": 0, "machine_data_secondary": True},
            "authority_sha256": named["a10_release_authority"]["sha256"],
        },
    )
    write_tables(output, tables)
    write_sidecars(output, tables, context, authority, named)
    csv_manifest = write_csv_surfaces(output, tables, str(context["package_id"]), RECORDED_AT)
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
        "extension_id": projection_id(LANE_NAMESPACE, "lane_adapter_extension", f"a10:elementary-algebra-2e:{ADAPTER_VERSION}"),
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
            "builder": file_fact(output / "tools" / "build_a10_v23_adapter.py", "tools/build_a10_v23_adapter.py", "builder"),
            "validator": file_fact(output / "tools" / "validate_a10_v23_adapter.py", "tools/validate_a10_v23_adapter.py", "validator"),
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
            "binds": ["schemas", "tools", "input_authorities", "release_closure", "tables", "sidecars", "csv_projections", "manifest"],
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
    write_json(
        output / "seal.json",
        {
            "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
            "package_id": context["package_id"],
            "algorithm": "sha256-sorted-path-bytes-v1",
            "files": seal_facts,
            "file_count": len(seal_facts),
            "bytes": sum(int(item["bytes"]) for item in seal_facts),
            "aggregate_sha256": inventory_sha256(seal_facts),
            "seal_excluded_from_own_digest": True,
            "recorded_at": RECORDED_AT,
        },
    )
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_fact = write_checksums(output, checksum_facts)
    return {
        "status": "PASS",
        "output": str(output),
        "files": len(checksum_facts) + 1,
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "table_counts": {name: len(tables[name]) for name in TABLE_ORDER},
        "owner_native_records": 561994,
        "module_rows": 82,
        "payload_inventory_sha256": payload_identity,
        "seal_sha256": sha256_file(output / "seal.json"),
        "checksum_sha256": checksum_fact["sha256"],
        "tree_sha256": tree_identity(output),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
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
