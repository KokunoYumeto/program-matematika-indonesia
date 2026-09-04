"""Strict validator for the bounded D40 capability adapter.

This validator checks the locked native evidence, the zero-copy capability
projection, learner/educator identity use, manifest integrity, every negative
fixture, and two isolated byte-identical builds.  It uses only the Python
standard library and never rebuilds TeX, notebooks, or numerical experiments.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

from d40_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    D40Error,
    DIONNE_COMMIT,
    DIONNE_TREE,
    EXPECTED_EXECUTION_COUNTS,
    EXPECTED_KIND_COUNTS,
    EXPECTED_RIGHT_IDS,
    FENICSX_COMMIT,
    FENICSX_TREE,
    MANIFEST_URL,
    NATIVE_CORPUS_ID,
    PDF_IDENTITY,
    PDF_URL,
    RECORD_URL,
    RELEASE_MANIFEST_IDENTITY,
    ZIP_IDENTITY,
    ZIP_URL,
    apply_negative_mutation,
    expected_source_ids,
    expected_unit_ids,
    file_identity,
    load_bundle,
    read_json,
    read_jsonl,
    tree_identity,
    validate_bundle,
    write_json,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d40-capability-v1"
DEFAULT_NATIVE = PROJECT.parent / "partial-differential-equations-id"
BUILD_SCRIPT = PROJECT / "scripts/build_d40_capability_v1.py"

REQUIRED_INPUT_ROLES = {
    "completion_receipt",
    "terminology_ledger",
    "terminology_qa",
    "source_corrections",
    "terminology_witness",
    "dionne_objects",
    "complete_corpus",
    "complete_components",
    "complete_imports",
    "complete_objects",
    "complete_relations",
    "complete_rights",
    "complete_spans",
    "complete_checksums_json",
    "complete_checksums_csv",
    "final_backend_verification",
    "mastery_validation",
    "translation_qa",
    "html_build_receipt",
    "html_visual_qa",
    "pdf_visual_qa",
    "release_manifest",
    "release_receipt",
    "release_independent_verification",
    "publication_receipt",
    "public_readback",
    "component_license_boundaries",
    "public_pdf",
    "public_zip",
}

EXPECTED_OUTPUT_PATHS = {
    "data/capabilities.json",
    "data/course.json",
    "data/evidence.json",
    "data/execution.json",
    "data/learning-map.json",
    "data/rights.jsonl",
    "data/routes.jsonl",
    "data/theory-links.json",
    "data/units.jsonl",
    "views/D40-pengajar.html",
    "views/D40.html",
}

BACKEND_ROLE_BY_FILE = {
    "components.jsonl": "complete_components",
    "corpus.json": "complete_corpus",
    "imports.jsonl": "complete_imports",
    "objects.jsonl": "complete_objects",
    "relations.jsonl": "complete_relations",
    "rights.jsonl": "complete_rights",
    "spans.jsonl": "complete_spans",
}

PRIMARY_KINDS = set(EXPECTED_KIND_COUNTS)
EXECUTION_KINDS = {
    "executed_notebooks": "executed_solution_notebook",
    "execution_surfaces": "execution_surface",
    "required_cells": {"notebook_code_cell", "notebook_markdown_cell"},
    "source_nodes": "fenicsx_source_node",
}
PROJECTED_METADATA_KEYS = {
    "object_id",
    "parent_id",
    "kind",
    "component",
    "rights_id",
    "source_id",
    "source_path",
    "source_order",
    "node",
    "surface",
    "run_id",
    "cell_index",
    "cell_type",
    "jupytext_pair",
    "identity",
    "identities",
    "record_identity",
    "title",
    "locale_neutral_id",
    "verdict",
    "rights_scope",
}
EXPECTED_BACKEND_VERIFICATION_CHECKS = {
    "all_116_cells_have_exact_nonoverlapping_paired_python_spans",
    "all_lab_code_fences_exact_50",
    "all_object_identities_hash_and_bounds_exact",
    "all_parent_and_relation_endpoints_resolved",
    "all_span_entities_resolved",
    "all_span_hashes_and_locator_bounds_exact",
    "checksum_manifests_equivalent",
    "combined_hierarchy_acyclic",
    "component_rights_exact_and_distinct",
    "declared_prerequisites_exact_108",
    "dionne_endpoint_registry_hash_bound",
    "dionne_files_imported_without_modification",
    "dionne_receipt_binding_exact_refreshed_post_c502_c503",
    "direct_fenicsx_to_dionne_theory_crosslinks_exact_32",
    "executed_notebooks_and_outputs_remain_fenicsx_cc_by",
    "execution_artifacts_and_logs_exact_226",
    "execution_surfaces_exact_8",
    "fenicsx_admitted_source_nodes_exact_18",
    "frozen_static_pairing_and_code_parity_pass",
    "mastery_primary_roots_exact_68",
    "no_mutable_rights_qa_hash_cycle",
    "object_ids_unique_and_namespaces_disjoint",
    "output_inventory_exact_9_no_extra_entries",
    "output_receipt_hashes_bind_disk",
    "paired_source_relations_exact_5_including_nitsche",
    "producer_read_only_replay_pass",
    "producer_receipt_is_newer_than_superseded_f566f333",
    "relation_ids_unique",
    "required_notebook_cells_exact_116",
    "runtime_cache_log_rights_partition_exact",
    "runtime_rights_record_is_record_level_unasserted",
    "schema_and_verdict_exact",
    "span_ids_unique",
    "topology_receipt_and_corpus_exact",
}
EXPECTED_BACKEND_VERIFICATION_ERRORS = {
    "dangling_parents",
    "dangling_relations",
    "dangling_spans",
    "execution_surface_record_errors",
    "imported_file_errors",
    "invalid_object_identities",
    "invalid_spans",
    "output_binding_errors",
    "paired_python_identity_errors",
    "paired_python_overlap_errors",
    "paired_python_path_errors",
    "runtime_rights_missing",
    "runtime_rights_overbroad",
}
EXPECTED_RELEASE_CHECKS = {
    "component_license_boundaries",
    "deterministic_zip_metadata",
    "dionne_source_complete",
    "dual_backend_complete",
    "exact_seven_file_publication_inventory",
    "exact_title_and_existing_concept_lineage",
    "fenicsx_source_and_executed_complete",
    "manifest_zip_sha256_closure",
    "mastery_48_16_4_complete",
    "no_credentials_or_private_paths",
    "no_unsafe_duplicate_or_stale_release_identities",
    "offline_html_reference_closure",
    "pdf_structure",
    "producer_and_independent_receipt_bindings",
}
EXPECTED_READBACK_CHECKS = {
    "access_right_open",
    "all_byte_counts_match",
    "all_files_publicly_downloadable",
    "all_md5_match",
    "concept_alias_resolves_latest",
    "concept_doi",
    "concept_record_id",
    "credential_recorded",
    "credential_used",
    "doi",
    "exact_inventory",
    "inventory_count",
    "is_published_not_contradictory",
    "latest_version_endpoint",
    "local_vs_stream_sha256_match",
    "primary_pdf_public_with_pdf_signature",
    "published_status",
    "record_id",
    "submitted_flag",
    "version_relation_parent",
}
PUBLIC_FILE_IDENTITIES = {
    "PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf": PDF_IDENTITY,
    "D40_COMPLETE_ID_20260831.zip": ZIP_IDENTITY,
    "RELEASE_NOTES.md": {
        "bytes": 1_233,
        "sha256": "b3e6678c75aced1badfe1469d9b6618cfe12899ecace14473f3acd3d2ef85da3",
    },
    "COMPONENT_LICENSE_BOUNDARIES.json": {
        "bytes": 2_131,
        "sha256": "e95f98d79d5105e24d5c5808548b890dc8b14abd102bac2872a8d1519e85af4a",
    },
    "RELEASE_MANIFEST.json": RELEASE_MANIFEST_IDENTITY,
    "SHA256SUMS.txt": {
        "bytes": 30_839,
        "sha256": "14043e5c57e0e402ff2233fac9b40853fba65d30fb0962e6c964c7b38c4861c2",
    },
    "RELEASE_RECEIPT.json": {
        "bytes": 32_377,
        "sha256": "33287e8eefff35b7cc7362d77350e19f0ae99ed94cce5f1540c854a6f9c5df81",
    },
}
EXPECTED_NEGATIVE_FIXTURES = {
    "alter-public-pdf-hash": ("alter_public_pdf_hash", "D40-PUBLIC-PDF"),
    "alter-source-authority": ("alter_source_authority", "D40-SOURCE-AUTHORITY"),
    "blanket-license": ("blanket_license", "D40-BLANKET-LICENSE"),
    "claim-adapter-execution": ("claim_adapter_execution", "D40-ADAPTER-EXECUTION"),
    "claim-assistive-testing": ("claim_assistive_testing", "D40-PDF-TAGGED-CLAIM"),
    "claim-complete-tounicode": ("claim_complete_tounicode", "D40-PDF-TAGGED-CLAIM"),
    "claim-full-native-roundtrip": ("claim_full_native_roundtrip", "D40-NATIVE-ROUNDTRIP-CLAIM"),
    "claim-learner-roundtrip": ("claim_learner_roundtrip", "D40-NATIVE-ROUNDTRIP-CLAIM"),
    "claim-mathjax-only": ("claim_mathjax_only", "D40-HTML-MATH"),
    "claim-mathjax-runtime": ("claim_mathjax_runtime", "D40-HTML-MATH"),
    "claim-tagged-pdf": ("claim_tagged_pdf", "D40-PDF-TAGGED-CLAIM"),
    "close-queued-correction": ("close_queued_correction", "D40-CORRECTIONS"),
    "copy-dionne-object": ("copy_dionne_object", "D40-DIONNE-ZERO-COPY"),
    "direct-zip-member-url": ("direct_zip_member_url", "D40-ZIP-MEMBER-DIRECT-URL"),
    "drop-assessment": ("drop_assessment", "D40-COUNT-ASSESSMENT"),
    "drop-dionne-chapter": ("drop_dionne_chapter", "D40-DIONNE-CHAPTERS"),
    "drop-lab": ("drop_lab", "D40-COUNT-LABS"),
    "drop-practice": ("drop_practice", "D40-COUNT-PRACTICE"),
    "drop-required-cell": ("drop_required_cell", "D40-EXECUTION-CELLS"),
    "drop-rights-record": ("drop_rights_record", "D40-RIGHTS-SET"),
    "drop-support-relation": ("drop_support_relation", "D40-THEORY-SUPPORTS"),
    "duplicate-unit-id": ("duplicate_unit_id", "D40-UNIT-ID-DUPLICATE"),
    "embed-unit-body": ("embed_unit_body", "D40-PAYLOAD-EMBEDDED"),
    "embed-unit-source-code": ("embed_unit_source_code", "D40-UNIT-SHAPE"),
    "fabricate-native-unit-identity": ("fabricate_native_unit_identity", "D40-NATIVE-UNIT-ID-SET"),
    "runtime-rights-upgrade": ("runtime_rights_upgrade", "D40-RUNTIME-RIGHTS"),
}


def fail(code: str) -> None:
    raise D40Error(code)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_relative_path(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        fail(code)
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or pure.as_posix() != value
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        fail(code)
    return pure.as_posix()


def locked_file(native: Path, item: dict[str, Any]) -> Path:
    relative = safe_relative_path(item.get("path"), "D40-VALIDATE-LOCK-PATH")
    candidate = (native / relative).resolve()
    try:
        candidate.relative_to(native)
    except ValueError:
        fail("D40-VALIDATE-LOCK-PATH-ESCAPE:" + relative)
    return candidate


def verify_locked_inputs(
    native: Path,
    lock: dict[str, Any],
    allow_identity_only_public_artifacts: bool = False,
) -> dict[str, dict[str, Any]]:
    if (
        lock.get("schema") != "d40-capability-source-lock/1"
        or lock.get("course_id") != COURSE_ID
        or lock.get("owner_lane") != "O010"
        or lock.get("native_corpus_id") != NATIVE_CORPUS_ID
        or lock.get("contract_2_3_1_conformance") != "not_claimed"
    ):
        fail("D40-VALIDATE-LOCK-HEADER")
    inputs = lock.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        fail("D40-VALIDATE-LOCK-INPUTS")
    roles: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()
    for item in inputs:
        if not isinstance(item, dict):
            fail("D40-VALIDATE-LOCK-ROW")
        role = item.get("role")
        relative = safe_relative_path(item.get("path"), "D40-VALIDATE-LOCK-PATH")
        if not isinstance(role, str) or not role or role in roles:
            fail("D40-VALIDATE-LOCK-DUPLICATE-ROLE")
        if relative in seen_paths:
            fail("D40-VALIDATE-LOCK-DUPLICATE-PATH")
        if not isinstance(item.get("bytes"), int) or item["bytes"] < 0:
            fail("D40-VALIDATE-LOCK-BYTES:" + relative)
        if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", item["sha256"]):
            fail("D40-VALIDATE-LOCK-SHA256:" + relative)
        path = locked_file(native, item)
        may_be_identity_only = allow_identity_only_public_artifacts and role in {
            "public_pdf",
            "public_zip",
        }
        if (not path.is_file() and not may_be_identity_only) or (
            path.is_file()
            and file_identity(path)
            != {"bytes": item["bytes"], "sha256": item["sha256"]}
        ):
            fail("D40-VALIDATE-LOCK-DRIFT:" + relative)
        roles[role] = item
        seen_paths.add(relative)
    if set(roles) != REQUIRED_INPUT_ROLES:
        missing = sorted(REQUIRED_INPUT_ROLES - set(roles))
        extra = sorted(set(roles) - REQUIRED_INPUT_ROLES)
        fail(f"D40-VALIDATE-LOCK-ROLES:missing={missing}:extra={extra}")
    release = lock.get("public_release", {})
    if (
        release.get("record_url") != RECORD_URL
        or release.get("pdf_url") != PDF_URL
        or release.get("zip_url") != ZIP_URL
        or release.get("doi") != "10.5281/zenodo.22184259"
        or release.get("concept_doi") != "10.5281/zenodo.22059503"
        or release.get("access") != "open"
    ):
        fail("D40-VALIDATE-LOCK-PUBLIC-RELEASE")
    if lock.get("native_repository") != {
        "expected_sibling_directory": "partial-differential-equations-id",
        "dionne_commit": DIONNE_COMMIT,
        "dionne_tree": DIONNE_TREE,
        "fenicsx_commit": FENICSX_COMMIT,
        "fenicsx_tree": FENICSX_TREE,
    }:
        fail("D40-VALIDATE-LOCK-AUTHORITY")
    completion = read_json(role_path(native, roles, "completion_receipt"))
    if (
        completion.get("schema") != "o010-d40-final-completion-receipt-v1"
        or completion.get("verdict") != "PASS_O010_D40_COMPLETE_PUBLIC_READBACK_CLOSED"
        or completion.get("authority")
        != {
            "dionne_commit": DIONNE_COMMIT,
            "dionne_tree": DIONNE_TREE,
            "fenicsx_commit": FENICSX_COMMIT,
            "fenicsx_tree": FENICSX_TREE,
        }
    ):
        fail("D40-VALIDATE-COMPLETION-AUTHORITY")
    return roles


def role_path(native: Path, roles: dict[str, dict[str, Any]], role: str) -> Path:
    return locked_file(native, roles[role])


def verify_record_count(rows: list[Any], item: dict[str, Any], code: str) -> None:
    if "records" in item and len(rows) != item["records"]:
        fail(code)


def verify_backend_checksums(native: Path, roles: dict[str, dict[str, Any]]) -> None:
    expected = [
        {
            "path": filename,
            "bytes": roles[role]["bytes"],
            "sha256": roles[role]["sha256"],
        }
        for filename, role in sorted(BACKEND_ROLE_BY_FILE.items())
    ]
    checksums = read_json(role_path(native, roles, "complete_checksums_json"))
    if (
        checksums.get("schema") != "o010-d40-complete-backend-checksums-v1"
        or checksums.get("files") != expected
    ):
        fail("D40-VALIDATE-BACKEND-CHECKSUMS-JSON")
    csv_values = csv_rows(role_path(native, roles, "complete_checksums_csv"))
    expected_csv = [
        {"path": row["path"], "bytes": str(row["bytes"]), "sha256": row["sha256"]}
        for row in expected
    ]
    if csv_values != expected_csv:
        fail("D40-VALIDATE-BACKEND-CHECKSUMS-CSV")


def identity_members(row: dict[str, Any]) -> list[str]:
    identities: list[dict[str, Any]] = []
    if isinstance(row.get("identity"), dict):
        identities.append(row["identity"])
    if isinstance(row.get("identities"), list):
        identities.extend(item for item in row["identities"] if isinstance(item, dict))
    members = []
    for identity in identities:
        path = identity.get("path")
        if not isinstance(path, str) or not path.startswith("composite/"):
            fail("D40-VALIDATE-NATIVE-IDENTITY-PATH")
        members.append(
            safe_relative_path(
                path.removeprefix("composite/"),
                "D40-VALIDATE-NATIVE-IDENTITY-PATH",
            )
        )
    return sorted(set(members))


def grouped_children(objects: Iterable[dict[str, Any]], parent_id: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in objects:
        if row.get("parent_id") == parent_id:
            grouped[str(row.get("kind"))].append(str(row.get("object_id")))
    return {kind: sorted(ids) for kind, ids in sorted(grouped.items())}


def projected_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in row if key in PROJECTED_METADATA_KEYS}


def verify_units_against_native(
    objects: list[dict[str, Any]], bundle: dict[str, Any]
) -> dict[str, int]:
    primary = [row for row in objects if row.get("kind") in PRIMARY_KINDS]
    native_by_id = {row.get("object_id"): row for row in primary}
    if len(primary) != 68 or len(native_by_id) != 68:
        fail("D40-VALIDATE-NATIVE-PRIMARY-COUNT")
    kind_counts = Counter(str(row.get("kind")) for row in primary)
    if dict(kind_counts) != EXPECTED_KIND_COUNTS:
        fail("D40-VALIDATE-NATIVE-PRIMARY-KINDS")
    if set(native_by_id) != expected_unit_ids():
        fail("D40-VALIDATE-NATIVE-PRIMARY-IDS")
    if {row.get("source_id") for row in primary} != expected_source_ids():
        fail("D40-VALIDATE-NATIVE-SOURCE-IDS")

    projected = bundle["units"]
    projected_by_id = {row.get("unit_id"): row for row in projected}
    if len(projected) != 68 or set(projected_by_id) != set(native_by_id):
        fail("D40-VALIDATE-PROJECTED-PRIMARY-SET")
    all_objects_by_id = {row.get("object_id"): row for row in objects}
    for object_id, native_row in native_by_id.items():
        row = projected_by_id[object_id]
        if (
            row.get("native_object_id") != object_id
            or row.get("native_source_id") != native_row.get("source_id")
            or row.get("unit_type") != native_row.get("kind")
            or row.get("rights_id") != native_row.get("rights_id")
            or row.get("title_id") != native_row.get("title", {}).get("id")
            or row.get("native_parent_id") != native_row.get("parent_id")
            or row.get("native_identity")
            != (native_row.get("identities") or native_row.get("identity"))
            or row.get("content_embedded") is not False
            or row.get("archive_member_paths") != identity_members(native_row)
        ):
            fail("D40-VALIDATE-UNIT-PROJECTION:" + str(object_id))
        support = row.get("support_ids")
        if not isinstance(support, dict):
            fail("D40-VALIDATE-UNIT-SUPPORT:" + str(object_id))
        for kind, ids in support.items():
            if not isinstance(ids, list) or ids != sorted(ids) or len(ids) != len(set(ids)):
                fail("D40-VALIDATE-UNIT-SUPPORT:" + str(object_id))
            for child_id in ids:
                child = all_objects_by_id.get(child_id)
                if not child or child.get("parent_id") != object_id or child.get("kind") != kind:
                    fail("D40-VALIDATE-UNIT-SUPPORT:" + str(object_id))
        if support != grouped_children(objects, str(object_id)):
            fail("D40-VALIDATE-UNIT-SUPPORT-COVERAGE:" + str(object_id))
    return dict(kind_counts)


def verify_prerequisites(
    relations: list[dict[str, Any]], learning_map: dict[str, Any]
) -> None:
    native = [row for row in relations if row.get("relation") == "prerequisite_for"]
    if len(native) != 108 or len({row.get("relation_id") for row in native}) != 108:
        fail("D40-VALIDATE-NATIVE-PREREQUISITES")
    expected = {
        (row.get("relation_id"), row.get("source_id"), row.get("target_id"), row.get("evidence"))
        for row in native
    }
    projected_rows = learning_map.get("prerequisite_routes", [])
    projected = {
        (
            row.get("id", row.get("relation_id")),
            row.get("prerequisite", row.get("source_id")),
            row.get("unit", row.get("target_id")),
            row.get("native_evidence", row.get("evidence")),
        )
        for row in projected_rows
    }
    if len(projected_rows) != 108 or len(projected) != 108 or projected != expected:
        fail("D40-VALIDATE-PREREQUISITE-PROJECTION")


def support_record(
    status: str,
    source_anchor: str | None,
    label: str | None,
    href: str | None,
) -> dict[str, Any]:
    return {"status": status, "source_anchor": source_anchor, "label": label, "href": href}


def verify_learning_map_projection(
    relations: list[dict[str, Any]],
    roles: dict[str, dict[str, Any]],
    bundle: dict[str, Any],
) -> None:
    learning_map = bundle["learning_map"]
    units = bundle["units"]
    unit_ids = {row["unit_id"] for row in units}
    prerequisites = [row for row in relations if row.get("relation") == "prerequisite_for"]
    previous_by_target: dict[str, list[str]] = defaultdict(list)
    for relation in prerequisites:
        previous_by_target[relation["target_id"]].append(relation["source_id"])
    projected_map_units = learning_map.get("units", [])
    if [row.get("id") for row in projected_map_units] != [row["unit_id"] for row in units]:
        fail("D40-VALIDATE-LEARNING-MAP-ORDER")
    for unit, row in zip(units, projected_map_units):
        support = unit["support_ids"]
        if unit["unit_type"] == "practice_problem":
            hint = support_record("complete", support["hint"][0], "Petunjuk", ZIP_URL)
            check = support_record("not_present", None, None, None)
            solution = support_record("complete", support["solution"][0], "Solusi lengkap", ZIP_URL)
        elif unit["unit_type"] == "assessment_item":
            hint = support_record("not_present", None, None, None)
            check = support_record("complete", support["rubric"][0], "Rubrik", ZIP_URL)
            solution = support_record("complete", support["solution"][0], "Solusi lengkap", ZIP_URL)
        else:
            hint = support_record("not_present", None, None, None)
            validation_ids = support.get("lab_validation", [])
            check = (
                support_record("complete", validation_ids[0], "Validasi native", ZIP_URL)
                if validation_ids
                else support_record("not_present", None, None, None)
            )
            solution = support_record(
                "complete",
                support["lab_solution_document"][0],
                "Dokumen solusi",
                ZIP_URL,
            )
        exercise = {
            "id": unit["unit_id"],
            "unit_id": unit["unit_id"],
            "title": unit["title_id"],
            "kind": unit["unit_type"],
            "sequence": 1,
            "curriculum_status": "complete_native_record",
            "href": ZIP_URL,
            "hint": hint,
            "check": check,
            "solution": solution,
        }
        expected = {
            "id": unit["unit_id"],
            "title": unit["title_id"],
            "href": ZIP_URL,
            "sections": unit["archive_member_paths"],
            "objectives_href": None,
            "previous_units": sorted(set(previous_by_target[unit["unit_id"]])),
            "components": [
                {
                    "id": unit["unit_id"],
                    "source": "d40.source.mastery",
                    "license": "CC-BY-NC-SA-4.0",
                    "rights_id": unit["rights_id"],
                }
            ],
            "exercises": [exercise],
        }
        if row != expected:
            fail("D40-VALIDATE-LEARNING-MAP-UNIT:" + unit["unit_id"])

    executed_as = [row for row in relations if row.get("relation") == "executed_as"]
    if bundle["execution"].get("lab_execution_relations") != executed_as:
        fail("D40-VALIDATE-LAB-EXECUTION-RELATIONS")
    executed_by_lab: dict[str, list[str]] = defaultdict(list)
    for relation in executed_as:
        executed_by_lab[relation["source_id"]].append(relation["target_id"])
    expected_labs = [
        {
            "id": unit["unit_id"],
            "unit": unit["unit_id"],
            "environment": "d40.environment.preexecuted-fenicsx",
            "exercise_ids": [unit["unit_id"]],
            "artifact_ids": sorted(executed_by_lab[unit["unit_id"]]),
            "archive_member_paths": unit["archive_member_paths"],
        }
        for unit in units
        if unit["unit_type"] == "computational_lab"
    ]
    if learning_map.get("labs") != expected_labs:
        fail("D40-VALIDATE-LEARNING-MAP-LABS")
    expected_environments = [
        {
            "id": "d40.environment.preexecuted-fenicsx",
            "runtime_version": "captured_by_native_execution_receipt_not_replayed",
            "lock": {
                key: roles["final_backend_verification"][key]
                for key in ("path", "bytes", "sha256")
            },
        }
    ]
    if learning_map.get("environments") != expected_environments:
        fail("D40-VALIDATE-LEARNING-MAP-ENVIRONMENTS")

    expected_artifacts = [
        {
            "id": "d40.artifact.pdf",
            "kind": "complete-course-pdf",
            "path": PDF_URL,
            "availability": "direct_public_file",
            **PDF_IDENTITY,
        },
        {
            "id": "d40.artifact.zip",
            "kind": "complete-course-archive",
            "path": ZIP_URL,
            "availability": "direct_public_file",
            **ZIP_IDENTITY,
        },
        {
            "id": "d40.artifact.offline-html",
            "kind": "semantic-html-reader",
            "path": "reader/html/index.html",
            "availability": "public_zip_member_only",
            "container_url": ZIP_URL,
            "direct_online_url": None,
        },
    ]
    expected_artifacts.extend(
        {
            "id": row["object_id"],
            "kind": "executed-solution-notebook",
            "path": row["archive_member_path"],
            "availability": "public_zip_member_only",
            "container_url": ZIP_URL,
            "direct_online_url": None,
            "identity": row["identity"],
        }
        for row in bundle["execution"]["executed_notebooks"]
    )
    if learning_map.get("artifacts") != expected_artifacts:
        fail("D40-VALIDATE-LEARNING-MAP-ARTIFACTS")

    relevant = [
        row
        for row in relations
        if row.get("relation")
        in {"supports", "implemented_by", "executed_as", "computational_companion"}
        and (row.get("source_id") in unit_ids or row.get("target_id") in unit_ids)
    ]
    chapter_ids = {row["object_id"] for row in bundle["theory_links"]["chapters"]}
    expected_external = sorted(
        {
            endpoint
            for relation in relevant
            for endpoint in (relation["source_id"], relation["target_id"])
            if endpoint not in unit_ids
        }
        | chapter_ids
    )
    if learning_map.get("external_relation_nodes") != expected_external:
        fail("D40-VALIDATE-LEARNING-MAP-EXTERNAL-NODES")


def verify_routes(bundle: dict[str, Any]) -> None:
    units = {row["unit_id"]: row for row in bundle["units"]}
    routes = bundle["routes"]
    by_unit = {row.get("native_object_id"): row for row in routes}
    if len(routes) != 68 or len(by_unit) != 68 or set(by_unit) != set(units):
        fail("D40-VALIDATE-ROUTE-SET")
    for unit_id, unit in units.items():
        route = by_unit[unit_id]
        if route != {
            "schema": "d40-capability-route/1",
            "adapter_route_id": unit["access_route_id"],
            "native_object_id": unit_id,
            "native_source_id": unit["native_source_id"],
            "target_kind": "public_zip_download_with_member_locator",
            "access_url": ZIP_URL,
            "public_container": {
                "filename": "D40_COMPLETE_ID_20260831.zip",
                **ZIP_IDENTITY,
            },
            "member_paths": unit["archive_member_paths"],
            "member_url": None,
            "directly_addressable": False,
        }:
            fail("D40-VALIDATE-ROUTE-PROJECTION:" + unit_id)


def verify_theory_projection(
    native: Path,
    roles: dict[str, dict[str, Any]],
    relations: list[dict[str, Any]],
    theory_links: dict[str, Any],
) -> None:
    dionne_objects = read_jsonl(role_path(native, roles, "dionne_objects"))
    verify_record_count(
        dionne_objects,
        roles["dionne_objects"],
        "D40-VALIDATE-DIONNE-OBJECT-COUNT",
    )
    if len(dionne_objects) != 3920 or len({row.get("object_id") for row in dionne_objects}) != 3920:
        fail("D40-VALIDATE-DIONNE-OBJECTS")
    native_chapters = [projected_metadata(row) for row in dionne_objects if row.get("kind") == "chapter"]
    native_supports = [row for row in relations if row.get("relation") == "supports"]
    if len(native_chapters) != 14 or len(native_supports) != 130:
        fail("D40-VALIDATE-DIONNE-THEORY-NATIVE")
    if (
        theory_links.get("schema") != "d40-capability-theory-links/1"
        or theory_links.get("course_id") != COURSE_ID
        or theory_links.get("zero_copy") is not True
        or theory_links.get("native_bodies_copied") != 0
        or theory_links.get("dionne_objects_source")
        != {key: roles["dionne_objects"][key] for key in ("path", "bytes", "sha256")}
        or theory_links.get("chapters") != native_chapters
        or theory_links.get("supports_relations") != native_supports
        or theory_links.get("relationship_semantics")
        != "native many-to-many supports edges; no single-chapter assignment is inferred"
    ):
        fail("D40-VALIDATE-DIONNE-THEORY-PROJECTION")


def verify_execution_objects(objects: list[dict[str, Any]], execution: dict[str, Any]) -> None:
    expected_lengths = {
        "executed_notebooks": 4,
        "execution_surfaces": 8,
        "required_cells": 116,
        "source_nodes": 18,
    }
    for field, kind_spec in EXECUTION_KINDS.items():
        if isinstance(kind_spec, set):
            native = [row for row in objects if row.get("kind") in kind_spec]
        else:
            native = [row for row in objects if row.get("kind") == kind_spec]
        projected = execution.get(field, [])
        native_ids = {row.get("object_id") for row in native}
        projected_ids = {row.get("object_id") for row in projected}
        if (
            len(native) != expected_lengths[field]
            or len(projected) != expected_lengths[field]
            or len(native) != len(native_ids)
            or len(projected) != len(projected_ids)
            or projected_ids != native_ids
        ):
            fail("D40-VALIDATE-EXECUTION-PROJECTION:" + field)
        native_by_id = {row["object_id"]: row for row in native}
        for row in projected:
            source = native_by_id[row["object_id"]]
            projected_base = {
                key: value
                for key, value in row.items()
                if key not in {"archive_member_path", "direct_online_url"}
            }
            if projected_base != projected_metadata(source):
                fail("D40-VALIDATE-EXECUTION-PROJECTION:" + field)
            if field == "executed_notebooks":
                if (
                    not isinstance(row.get("archive_member_path"), str)
                    or row.get("direct_online_url") is not None
                ):
                    fail("D40-VALIDATE-EXECUTION-ARCHIVE-MEMBER")
            elif "archive_member_path" in row or "direct_online_url" in row:
                fail("D40-VALIDATE-EXECUTION-PROJECTION:" + field)
    cells = execution.get("required_cells", [])
    if Counter(row.get("kind") for row in cells) != Counter(
        {"notebook_code_cell": 54, "notebook_markdown_cell": 62}
    ):
        fail("D40-VALIDATE-EXECUTION-CELL-TYPES")
    if (
        execution.get("schema") != "d40-capability-execution-evidence/1"
        or execution.get("projection") != "metadata_only_preexecuted_evidence"
        or execution.get("adapter_execution_performed") is not False
        or execution.get("counts") != EXPECTED_EXECUTION_COUNTS
    ):
        fail("D40-VALIDATE-EXECUTION-HEADER")


def verify_native_semantics(
    native: Path, roles: dict[str, dict[str, Any]], bundle: dict[str, Any]
) -> dict[str, Any]:
    verify_backend_checksums(native, roles)
    completion = read_json(role_path(native, roles, "completion_receipt"))
    if (
        completion.get("schema") != "o010-d40-final-completion-receipt-v1"
        or completion.get("verdict") != "PASS_O010_D40_COMPLETE_PUBLIC_READBACK_CLOSED"
    ):
        fail("D40-VALIDATE-NATIVE-COMPLETION")
    corpus = read_json(role_path(native, roles, "complete_corpus"))
    components = read_jsonl(role_path(native, roles, "complete_components"))
    imports = read_jsonl(role_path(native, roles, "complete_imports"))
    objects = read_jsonl(role_path(native, roles, "complete_objects"))
    relations = read_jsonl(role_path(native, roles, "complete_relations"))
    rights = read_jsonl(role_path(native, roles, "complete_rights"))
    spans = read_jsonl(role_path(native, roles, "complete_spans"))
    for role, rows in (
        ("complete_components", components),
        ("complete_imports", imports),
        ("complete_objects", objects),
        ("complete_relations", relations),
        ("complete_rights", rights),
        ("complete_spans", spans),
    ):
        verify_record_count(rows, roles[role], "D40-VALIDATE-NATIVE-RECORD-COUNT:" + role)
    if (
        corpus.get("schema") != "o010-d40-complete-backend-v1"
        or corpus.get("corpus_id") != NATIVE_CORPUS_ID
        or corpus.get("status") != "complete"
        or corpus.get("rights_policy") != "record-level; no blanket license"
    ):
        fail("D40-VALIDATE-NATIVE-CORPUS")
    corpus_mastery = corpus.get("coverage", {}).get("mastery", {})
    corpus_fenicsx = corpus.get("coverage", {}).get("fenicsx", {})
    if (
        corpus_mastery.get("primary_count") != 68
        or set(corpus_mastery.get("primary_ids", [])) != expected_source_ids()
        or corpus_fenicsx.get("executed_notebooks") != 4
        or corpus_fenicsx.get("execution_surfaces") != 8
        or corpus_fenicsx.get("required_notebook_cells") != 116
        or corpus_fenicsx.get("code_cells") != 54
        or corpus_fenicsx.get("markdown_cells") != 62
    ):
        fail("D40-VALIDATE-NATIVE-COVERAGE")
    if len(objects) != 851 or len({row.get("object_id") for row in objects}) != 851:
        fail("D40-VALIDATE-NATIVE-OBJECTS")
    if len(relations) != 1638 or len({row.get("relation_id") for row in relations}) != 1638:
        fail("D40-VALIDATE-NATIVE-RELATIONS")
    if len(spans) != 1294 or len({row.get("span_id") for row in spans}) != 1294:
        fail("D40-VALIDATE-NATIVE-SPANS")
    if len(components) != 3 or len({row.get("component_id") for row in components}) != 3:
        fail("D40-VALIDATE-NATIVE-COMPONENTS")

    kind_counts = verify_units_against_native(objects, bundle)
    if (
        [row.get("native_source_id") for row in bundle["units"]]
        != corpus_mastery.get("primary_ids")
        or [row.get("projection_order") for row in bundle["units"]] != list(range(1, 69))
    ):
        fail("D40-VALIDATE-UNIT-PROJECTION-ORDER")
    verify_routes(bundle)
    verify_prerequisites(relations, bundle["learning_map"])
    verify_learning_map_projection(relations, roles, bundle)
    verify_execution_objects(objects, bundle["execution"])
    if (
        corpus_fenicsx.get("run_id") != "2026-08-31T012101+0000-c9684d397230"
        or bundle["execution"].get("run_id") != corpus_fenicsx.get("run_id")
    ):
        fail("D40-VALIDATE-EXECUTION-RUN-ID")
    verify_theory_projection(native, roles, relations, bundle["theory_links"])

    if len(rights) != 5 or {row.get("rights_id") for row in rights} != EXPECTED_RIGHT_IDS:
        fail("D40-VALIDATE-NATIVE-RIGHTS")
    if bundle["rights"] != rights:
        fail("D40-VALIDATE-RIGHTS-NOT-EXACT")

    dionne = next((row for row in imports if row.get("import_id") == "o010.d40.import.dionne-full"), None)
    if not dionne or (
        dionne.get("component_id") != "o010.d40.component.dionne"
        or dionne.get("object_count") != 3920
        or dionne.get("endpoint_ids_sha256")
        != "cd12f638f0a8b7cfb39630d16199c519a3103978372069bc1f8cb4223edfbfbd"
        or len(dionne.get("files", [])) != 10
    ):
        fail("D40-VALIDATE-NATIVE-DIONNE-IMPORT")
    projected_dionne = bundle["evidence"].get("dionne_import", {})
    for key in ("import_id", "component_id", "object_count", "endpoint_ids_sha256", "files", "receipt"):
        if key in projected_dionne and projected_dionne[key] != dionne.get(key):
            fail("D40-VALIDATE-DIONNE-IMPORT-PROJECTION")
    if projected_dionne.get("zero_copy") is not True or projected_dionne.get("native_records_copied") != 0:
        fail("D40-VALIDATE-DIONNE-ZERO-COPY")

    final_verification = read_json(role_path(native, roles, "final_backend_verification"))
    coverage = final_verification.get("coverage", {})
    topology = final_verification.get("topology", {})
    topology_kinds = topology.get("materialized_objects_by_kind", {})
    errors = final_verification.get("errors", {})
    checks = final_verification.get("checks", {})
    if (
        final_verification.get("schema")
        != "o010-d40-complete-backend-final-independent-verification-v1"
        or final_verification.get("verdict") != "PASS_FINAL_INDEPENDENT_D40_COMPLETE_BACKEND"
        or coverage.get("mastery_primary_roots") != 68
        or coverage.get("declared_prerequisites") != 108
        or coverage.get("imported_dionne_objects") != 3920
        or topology_kinds.get("executed_solution_notebook") != 4
        or coverage.get("execution_surfaces") != 8
        or coverage.get("required_notebook_cells") != 116
        or topology_kinds.get("notebook_code_cell") != 54
        or topology_kinds.get("notebook_markdown_cell") != 62
        or topology.get("rights_records") != 5
        or set(checks) != EXPECTED_BACKEND_VERIFICATION_CHECKS
        or any(value is not True for value in checks.values())
        or set(errors) != EXPECTED_BACKEND_VERIFICATION_ERRORS
        or any(value != [] for value in errors.values())
    ):
        fail("D40-VALIDATE-NATIVE-BACKEND-VERIFICATION")

    mastery = read_json(role_path(native, roles, "mastery_validation"))
    if mastery.get("verdict") != "PASS" or mastery.get("counts") != {
        "practice_files": 6,
        "practice_items": 48,
        "assessment_files": 2,
        "assessment_items": 16,
        "lab_files": 8,
        "lab_pairs": 4,
    }:
        fail("D40-VALIDATE-NATIVE-MASTERY")

    return {
        "materialized_objects": len(objects),
        "relations": len(relations),
        "spans": len(spans),
        "primary_kind_counts": kind_counts,
        "prerequisites": 108,
        "rights": len(rights),
        "dionne_imported_objects": dionne["object_count"],
    }


def verify_control_evidence(
    native: Path, roles: dict[str, dict[str, Any]], bundle: dict[str, Any]
) -> None:
    terms = csv_rows(role_path(native, roles, "terminology_ledger"))
    corrections = csv_rows(role_path(native, roles, "source_corrections"))
    terminology_qa = role_path(native, roles, "terminology_qa").read_text(
        encoding="utf-8"
    )
    terminology_qa_normalized = re.sub(r"\s+", " ", terminology_qa).strip()
    required_qa_markers = {
        "# QA terminologi Indonesia — saksi arXiv 2001.05854v1",
        "Putusan: **lulus; tidak ada perubahan istilah atau propagasi yang diperlukan**",
        "Ketidakhadiran itu dicatat sebagai tidak ada bukti, bukan bukti yang menolak pilihan Dionne.",
        "`controls/TERMINOLOGY.csv` dan Unit 01–03 tidak diubah oleh pemeriksaan ini.",
    }
    if any(marker not in terminology_qa_normalized for marker in required_qa_markers):
        fail("D40-VALIDATE-TERMINOLOGY-QA")
    verify_record_count(terms, roles["terminology_ledger"], "D40-VALIDATE-TERMINOLOGY-COUNT")
    verify_record_count(corrections, roles["source_corrections"], "D40-VALIDATE-CORRECTION-COUNT")
    if Counter(row.get("status") for row in terms) != Counter({"admitted": 492, "reserved": 3}):
        fail("D40-VALIDATE-TERMINOLOGY-STATUS")
    if {row.get("term_id") for row in terms if row.get("status") == "reserved"} != {
        "O010-T009",
        "O010-T010",
        "O010-T011",
    }:
        fail("D40-VALIDATE-TERMINOLOGY-RESERVED")
    if Counter(row.get("status") for row in corrections) != Counter({"applied": 499, "queued": 1}):
        fail("D40-VALIDATE-CORRECTION-STATUS")
    queued = [row for row in corrections if row.get("status") == "queued"]
    if len(queued) != 1 or queued[0].get("correction_id") != "O010-C002":
        fail("D40-VALIDATE-CORRECTION-QUEUED")

    witness = read_json(role_path(native, roles, "terminology_witness"))
    if witness.get("decision") != {
        **witness.get("decision", {}),
        "verdict": "PASS_NO_TERMINOLOGY_CHANGE_REQUIRED",
        "propagation_required": False,
    }:
        fail("D40-VALIDATE-TERMINOLOGY-WITNESS")
    translation = read_json(role_path(native, roles, "translation_qa"))
    if (
        translation.get("verdict") != "PASS"
        or translation.get("failures") != []
        or translation.get("reference_closure", {}).get("interpretation")
        != "Static regex excludes labels emitted by custom figure macros; the deterministic LaTeX build is the authoritative closure gate."
    ):
        fail("D40-VALIDATE-TRANSLATION-QA")

    projected_terms = bundle["evidence"].get("terminology", {})
    projected_corrections = bundle["evidence"].get("source_corrections", {})
    projected_translation = bundle["evidence"].get("translation_qa", {})
    if (
        projected_terms.get("record_count") != len(terms)
        or projected_terms.get("status_counts") != dict(Counter(row["status"] for row in terms))
        or projected_terms.get("reserved_term_ids", sorted(
            row["term_id"] for row in terms if row["status"] == "reserved"
        )) != sorted(row["term_id"] for row in terms if row["status"] == "reserved")
        or projected_terms.get("witness_verdict") != witness["decision"]["verdict"]
        or projected_terms.get("propagation_required") is not witness["decision"]["propagation_required"]
        or projected_terms.get("qa_receipt")
        != {
            key: roles["terminology_qa"][key]
            for key in ("path", "bytes", "sha256")
        }
    ):
        fail("D40-VALIDATE-TERMINOLOGY-PROJECTION")
    if (
        projected_corrections.get("record_count") != len(corrections)
        or projected_corrections.get("status_counts")
        != dict(Counter(row["status"] for row in corrections))
        or projected_corrections.get("queued_correction_ids") != ["O010-C002"]
    ):
        fail("D40-VALIDATE-CORRECTION-PROJECTION")
    if (
        projected_translation.get("verdict") != translation["verdict"]
        or projected_translation.get("reference_closure_authority") != "deterministic_latex_build"
        or projected_translation.get("static_regex_unresolved_are_not_build_failures") is not True
    ):
        fail("D40-VALIDATE-TRANSLATION-PROJECTION")


def walk_values(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def verify_public_and_accessibility(
    native: Path,
    roles: dict[str, dict[str, Any]],
    bundle: dict[str, Any],
    allow_identity_only_public_artifacts: bool = False,
) -> None:
    pdf_path = role_path(native, roles, "public_pdf")
    zip_path = role_path(native, roles, "public_zip")
    if {key: roles["public_pdf"].get(key) for key in ("bytes", "sha256")} != PDF_IDENTITY:
        fail("D40-VALIDATE-PDF-LOCK")
    if {key: roles["public_zip"].get(key) for key in ("bytes", "sha256")} != ZIP_IDENTITY:
        fail("D40-VALIDATE-ZIP-LOCK")
    if pdf_path.is_file() and file_identity(pdf_path) != PDF_IDENTITY:
        fail("D40-VALIDATE-PDF-IDENTITY")
    if zip_path.is_file() and file_identity(zip_path) != ZIP_IDENTITY:
        fail("D40-VALIDATE-ZIP-IDENTITY")
    if not allow_identity_only_public_artifacts and not pdf_path.is_file():
        fail("D40-VALIDATE-PDF-MISSING")
    if not allow_identity_only_public_artifacts and not zip_path.is_file():
        fail("D40-VALIDATE-ZIP-MISSING")

    html_build = read_json(role_path(native, roles, "html_build_receipt"))
    html_visual = read_json(role_path(native, roles, "html_visual_qa"))
    pdf_visual = read_json(role_path(native, roles, "pdf_visual_qa"))
    html_access = html_build.get("reader", {}).get("accessibility", {})
    if (
        html_build.get("verdict") != "PASS"
        or html_access.get("status") != "PASS_HTML_SEMANTICS"
        or html_access.get("mathml_elements") != 24_118
        or html_access.get("runtime_network_dependencies") != 0
        or html_visual.get("verdict") != "PASS_COMPLETE_HTML_VISUAL_QA_FINAL"
        or html_visual.get("reader_census", {}).get("mathml_elements") != 24_118
        or html_visual.get("reader_census", {}).get("runtime_network_dependencies") != 0
    ):
        fail("D40-VALIDATE-NATIVE-HTML-EVIDENCE")
    if (
        pdf_visual.get("verdict") != "PASS_FINAL_VISUAL_QA"
        or {key: pdf_visual.get("pdf", {}).get(key) for key in ("bytes", "sha256")} != PDF_IDENTITY
        or any(
            isinstance(value, dict)
            and any(key.lower() in {"tagged", "tagged_pdf", "pdf_ua", "pdf/ua"} for key in value)
            for value in walk_values(pdf_visual)
        )
    ):
        fail("D40-VALIDATE-NATIVE-PDF-EVIDENCE")

    release_manifest = read_json(role_path(native, roles, "release_manifest"))
    if file_identity(role_path(native, roles, "release_manifest")) != RELEASE_MANIFEST_IDENTITY:
        fail("D40-VALIDATE-RELEASE-MANIFEST-IDENTITY")
    archive_entries = {row.get("path") for row in release_manifest.get("entries", [])}
    if (
        release_manifest.get("schema") != "o010-d40-complete-release-manifest-v1"
        or release_manifest.get("entry_count") != 271
        or len(release_manifest.get("entries", [])) != 271
        or "reader/html/index.html" not in archive_entries
    ):
        fail("D40-VALIDATE-NATIVE-RELEASE-MANIFEST")

    release_receipt = read_json(role_path(native, roles, "release_receipt"))
    if (
        release_receipt.get("verdict") != "PASS_RELEASE_PACKAGE"
        or {key: release_receipt.get("archive", {}).get(key) for key in ("bytes", "sha256")}
        != ZIP_IDENTITY
        or {key: release_receipt.get("primary_pdf", {}).get(key) for key in ("bytes", "sha256")}
        != PDF_IDENTITY
    ):
        fail("D40-VALIDATE-NATIVE-RELEASE-RECEIPT")
    release_independent = read_json(role_path(native, roles, "release_independent_verification"))
    release_independent_checks = release_independent.get("checks", {})
    if (
        release_independent.get("verdict") != "PASS_INDEPENDENT_RELEASE_PACKAGE_VERIFICATION"
        or set(release_independent_checks) != EXPECTED_RELEASE_CHECKS
        or any(release_independent_checks[key] is not True for key in EXPECTED_RELEASE_CHECKS)
    ):
        fail("D40-VALIDATE-NATIVE-RELEASE-INDEPENDENT")

    publication = read_json(role_path(native, roles, "publication_receipt"))
    readback = read_json(role_path(native, roles, "public_readback"))
    readback_checks = readback.get("checks", {})
    if (
        publication.get("schema") != "o010-d40-complete-zenodo-publication-v1"
        or publication.get("publication_status") != "published"
        or publication.get("access_right") != "open"
        or publication.get("doi") != "10.5281/zenodo.22184259"
        or publication.get("conceptdoi") != "10.5281/zenodo.22059503"
        or publication.get("record_id") != 22_184_259
        or publication.get("public_record_url") != RECORD_URL
        or readback.get("authentication") != "none"
        or readback.get("verdict") != "PASS_INDEPENDENT_ANONYMOUS_PUBLIC_READBACK"
        or readback.get("file_count") != 7
        or len(readback.get("files", [])) != 7
        or readback.get("public_record_url") != RECORD_URL
        or set(readback_checks) != EXPECTED_READBACK_CHECKS
        or any(
            readback_checks[key] is not True
            for key in EXPECTED_READBACK_CHECKS - {"credential_recorded", "credential_used"}
        )
        or readback_checks.get("credential_recorded") is not False
        or readback_checks.get("credential_used") is not False
    ):
        fail("D40-VALIDATE-NATIVE-PUBLIC-READBACK")
    readback_rows = readback.get("files", [])
    public_by_name = {row.get("filename"): row for row in readback_rows}
    publication_rows = publication.get("files", [])
    publication_by_name = {row.get("filename"): row for row in publication_rows}
    if (
        len(public_by_name) != 7
        or set(public_by_name) != set(PUBLIC_FILE_IDENTITIES)
        or len(publication_rows) != 7
        or len(publication_by_name) != 7
        or set(publication_by_name) != set(PUBLIC_FILE_IDENTITIES)
    ):
        fail("D40-VALIDATE-NATIVE-PUBLIC-FILE-SET")
    for filename, identity in PUBLIC_FILE_IDENTITIES.items():
        url = f"https://zenodo.org/api/records/22184259/files/{filename}/content"
        row = public_by_name.get(filename, {})
        publication_row = publication_by_name.get(filename, {})
        if (
            row.get("canonical_anonymous_download_url") != url
            or {key: row.get("local", {}).get(key) for key in ("bytes", "sha256")} != identity
            or {key: row.get("anonymous_download", {}).get(key) for key in ("bytes", "sha256")}
            != identity
            or row.get("verdict") != "PASS_EXACT_PUBLIC_BYTES"
            or {key: publication_row.get(key) for key in ("bytes", "sha256")} != identity
            or publication_row.get("anonymous_readback") != "PASS"
        ):
            fail("D40-VALIDATE-NATIVE-PUBLIC-FILE:" + filename)

    boundaries = read_json(role_path(native, roles, "component_license_boundaries"))
    if (
        boundaries.get("schema") != "o010-d40-component-license-boundaries-v1"
        or boundaries.get("aggregation_license") is not None
        or len(boundaries.get("components", [])) != 5
        or len({row.get("id") for row in boundaries.get("components", [])}) != 5
    ):
        fail("D40-VALIDATE-NATIVE-LICENSE-BOUNDARIES")

    public_lineage = bundle["course"].get("public_lineage", {})
    direct = {
        value.get("url")
        for value in public_lineage.values()
        if isinstance(value, dict) and value.get("direct_public_file") is True
    }
    if direct != {PDF_URL, ZIP_URL}:
        fail("D40-VALIDATE-DIRECT-CONTENT-URLS")
    access = bundle["capabilities"].get("accessibility", {})
    offline = access.get("offline_html", {})
    pdf = access.get("pdf", {})
    if (
        offline.get("availability") != "public_zip_member_only"
        or offline.get("entrypoint") != "reader/html/index.html"
        or offline.get("direct_online_url") is not None
        or offline.get("mathml_elements") != html_access["mathml_elements"]
        or offline.get("runtime_network_dependencies") != html_access["runtime_network_dependencies"]
        or offline.get("runtime_mathjax_required") is not False
        or pdf.get("tagged_pdf_status") != "unknown_not_evidenced"
        or pdf.get("tagged_pdf_claimed") is not False
    ):
        fail("D40-VALIDATE-ACCESSIBILITY-PROJECTION")


class ViewFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.unit_ids: list[str] = []
        self.hrefs: list[str] = []
        self.sources: list[str] = []
        self.lang: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if values.get("data-unit-id"):
            self.unit_ids.append(str(values["data-unit-id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        for key in ("src", "action"):
            if values.get(key):
                self.sources.append(str(values[key]))


def is_archive_member_link(value: str, members: set[str]) -> bool:
    decoded = unquote(value).replace("\\", "/")
    parsed = urlsplit(decoded)
    path = parsed.path.lstrip("./")
    fragment = parsed.fragment.lstrip("./")
    return any(
        path == member
        or path.endswith("/" + member)
        or fragment == member
        or fragment.endswith("/" + member)
        for member in members
    )


def verify_views(output: Path, bundle: dict[str, Any]) -> None:
    learner = ViewFacts()
    learner.feed((output / "views/D40.html").read_text(encoding="utf-8"))
    learner.close()
    educator = ViewFacts()
    educator.feed((output / "views/D40-pengajar.html").read_text(encoding="utf-8"))
    educator.close()
    expected = {row["unit_id"] for row in bundle["units"]}
    for name, view in (("LEARNER", learner), ("EDUCATOR", educator)):
        if view.lang not in {"id", "id-ID"}:
            fail("D40-VALIDATE-" + name + "-LANG")
        if len(view.unit_ids) != 68 or len(set(view.unit_ids)) != 68 or set(view.unit_ids) != expected:
            fail("D40-VALIDATE-" + name + "-UNIT-IDENTITIES")
    members = {
        member
        for row in bundle["units"]
        for member in row.get("archive_member_paths", [])
    }
    members.add("reader/html/index.html")
    for view in (learner, educator):
        for link in view.hrefs + view.sources:
            if is_archive_member_link(link, members):
                fail("D40-VALIDATE-VIEW-ARCHIVE-MEMBER-URL")
    allowed_direct = {PDF_URL, ZIP_URL, RECORD_URL, MANIFEST_URL}
    direct_content = {
        link
        for view in (learner, educator)
        for link in view.hrefs + view.sources
        if urlsplit(link).scheme in {"http", "https"} and link.endswith("/content")
    }
    if not direct_content.issubset(allowed_direct) or not {PDF_URL, ZIP_URL}.issubset(
        set(learner.hrefs) | set(educator.hrefs)
    ):
        fail("D40-VALIDATE-VIEW-DIRECT-URLS")


def verify_manifest(
    native: Path,
    output: Path,
    lock: dict[str, Any],
    bundle: dict[str, Any],
) -> list[str]:
    manifest = bundle["manifest"]
    actual_output_paths = {
        path.relative_to(output).as_posix()
        for directory in (output / "data", output / "views")
        if directory.is_dir()
        for path in directory.rglob("*")
        if path.is_file()
    }
    if actual_output_paths != EXPECTED_OUTPUT_PATHS:
        fail("D40-VALIDATE-ADAPTER-OUTPUT-FILE-SET")
    if (
        manifest.get("schema") != "d40-capability-manifest/1"
        or manifest.get("course_id") != COURSE_ID
        or manifest.get("contract") != CONTRACT
        or manifest.get("contract_2_3_1_conformance") != "not_claimed"
        or manifest.get("public_release_status") != "unchanged_not_published_by_adapter"
    ):
        fail("D40-VALIDATE-MANIFEST-HEADER")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list):
        fail("D40-VALIDATE-MANIFEST-OUTPUTS")
    output_paths = [safe_relative_path(row.get("path"), "D40-VALIDATE-MANIFEST-PATH") for row in outputs]
    if len(output_paths) != len(set(output_paths)) or set(output_paths) != EXPECTED_OUTPUT_PATHS:
        fail("D40-VALIDATE-MANIFEST-FILE-SET")
    for row, relative in zip(outputs, output_paths):
        path = (output / relative).resolve()
        try:
            path.relative_to(output)
        except ValueError:
            fail("D40-VALIDATE-MANIFEST-PATH-ESCAPE")
        if not path.is_file() or file_identity(path) != {
            "bytes": row.get("bytes"),
            "sha256": row.get("sha256"),
        }:
            fail("D40-VALIDATE-MANIFEST-OUTPUT:" + relative)
    if manifest.get("inputs") != lock.get("inputs"):
        fail("D40-VALIDATE-MANIFEST-INPUTS")
    expected_tooling_paths = [
        "scripts/d40_capability_model_v1.py",
        "scripts/build_d40_capability_v1.py",
        "scripts/validate_d40_capability_v1.py",
        "scripts/package_d40_capability_v1.py",
        "backend/course-capsule-v1/adapters/d40-capability-v1/README.md",
        "backend/course-capsule-v1/adapters/d40-capability-v1/input/source-lock.json",
    ]
    expected_tooling_paths.extend(
        path.relative_to(PROJECT).as_posix()
        for path in sorted((ADAPTER / "fixtures/negative").glob("*.json"), key=lambda item: item.name)
    )
    tooling = manifest.get("tooling")
    if not isinstance(tooling, list) or [row.get("path") for row in tooling] != expected_tooling_paths:
        fail("D40-VALIDATE-MANIFEST-TOOLING-SET")
    for row in tooling:
        relative = safe_relative_path(row.get("path"), "D40-VALIDATE-MANIFEST-TOOLING-PATH")
        path = (PROJECT / relative).resolve()
        try:
            path.relative_to(PROJECT)
        except ValueError:
            fail("D40-VALIDATE-MANIFEST-TOOLING-ESCAPE")
        if not path.is_file() or row != {"path": relative, **file_identity(path)}:
            fail("D40-VALIDATE-MANIFEST-TOOLING:" + relative)
    payload_tree = tree_identity(output, output_paths)
    if manifest.get("output_tree_sha256") != payload_tree["sha256"]:
        fail("D40-VALIDATE-MANIFEST-TREE")

    generated = sorted(output_paths + ["manifest.json"])
    native_text = str(native.resolve()).casefold()
    native_slash = native_text.replace("\\", "/")
    drive_pattern = re.compile(r"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
    for relative in generated:
        text = (output / relative).read_text(encoding="utf-8")
        folded = text.casefold()
        if native_text in folded or native_slash in folded.replace("\\", "/") or drive_pattern.search(text):
            fail("D40-VALIDATE-ABSOLUTE-PATH-LEAK:" + relative)
    return generated


def isolated_build(
    native: Path,
    lock: Path,
    output: Path,
    allow_identity_only_public_artifacts: bool = False,
) -> None:
    command = [
        sys.executable,
        "-B",
        str(BUILD_SCRIPT),
        "--native-root",
        str(native),
        "--output-root",
        str(output),
        "--source-lock",
        str(lock),
    ]
    if allow_identity_only_public_artifacts:
        command.append("--allow-identity-only-public-artifacts")
    result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, timeout=120)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().replace(str(native), "<native-root>")
        fail("D40-VALIDATE-ISOLATED-BUILD:" + detail)


def compare_builds(
    native: Path,
    lock: Path,
    committed: Path,
    generated_paths: list[str],
    allow_identity_only_public_artifacts: bool = False,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d40-build-a-") as temp_a, tempfile.TemporaryDirectory(
        prefix="d40-build-b-"
    ) as temp_b:
        root_a = Path(temp_a)
        root_b = Path(temp_b)
        isolated_build(native, lock, root_a, allow_identity_only_public_artifacts)
        isolated_build(native, lock, root_b, allow_identity_only_public_artifacts)
        paths_a = sorted(path.relative_to(root_a).as_posix() for path in root_a.rglob("*") if path.is_file())
        paths_b = sorted(path.relative_to(root_b).as_posix() for path in root_b.rglob("*") if path.is_file())
        if paths_a != generated_paths or paths_b != generated_paths:
            fail("D40-VALIDATE-ISOLATED-FILE-SET")
        identity_a = tree_identity(root_a, paths_a)
        identity_b = tree_identity(root_b, paths_b)
        committed_identity = tree_identity(committed, generated_paths)
        if identity_a != identity_b:
            fail("D40-VALIDATE-ISOLATED-BYTE-IDENTITY")
        if identity_a != committed_identity:
            fail("D40-VALIDATE-COMMITTED-BUILD-DRIFT")
        return {
            "file_count": len(paths_a),
            "tree_sha256": identity_a["sha256"],
            "byte_identical": True,
        }


def run_negative_fixtures(bundle: dict[str, Any], fixture_root: Path) -> list[dict[str, str]]:
    paths = sorted(fixture_root.glob("*.json"), key=lambda item: item.name)
    expected_names = {f"{case_id}.json" for case_id in EXPECTED_NEGATIVE_FIXTURES}
    if {path.name for path in paths} != expected_names:
        fail("D40-VALIDATE-NEGATIVE-SET")
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in paths:
        fixture = read_json(path)
        if fixture.get("schema") != "d40-capability-negative-fixture/1":
            fail("D40-VALIDATE-NEGATIVE-SCHEMA:" + path.name)
        case_id = fixture.get("case_id")
        mutation = fixture.get("mutation")
        expected_error = fixture.get("expected_error")
        if not all(isinstance(value, str) and value for value in (case_id, mutation, expected_error)):
            fail("D40-VALIDATE-NEGATIVE-SHAPE:" + path.name)
        if (
            path.name != f"{case_id}.json"
            or EXPECTED_NEGATIVE_FIXTURES.get(case_id) != (mutation, expected_error)
        ):
            fail("D40-VALIDATE-NEGATIVE-CONTRACT:" + path.name)
        if case_id in seen:
            fail("D40-VALIDATE-NEGATIVE-DUPLICATE:" + case_id)
        seen.add(case_id)
        changed = apply_negative_mutation(bundle, mutation)
        errors = validate_bundle(changed)
        if expected_error not in errors:
            fail("D40-VALIDATE-NEGATIVE-NOT-REJECTED:" + case_id)
        results.append({"case_id": case_id, "expected_error": expected_error, "state": "rejected"})
    if seen != set(EXPECTED_NEGATIVE_FIXTURES):
        fail("D40-VALIDATE-NEGATIVE-COVERAGE")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=ADAPTER)
    parser.add_argument("--source-lock", type=Path, default=ADAPTER / "input/source-lock.json")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument(
        "--allow-identity-only-public-artifacts",
        action="store_true",
        help="Allow absent locked PDF/ZIP bytes when exact anonymous-readback evidence is present.",
    )
    args = parser.parse_args()
    native = args.native_root.resolve()
    output = args.output_root.resolve()
    lock_path = args.source_lock.resolve()
    receipt_path = (args.receipt or (output / "validation.json")).resolve()
    if (
        receipt_path.parent != output
        or receipt_path.name != "validation.json"
        or receipt_path.is_symlink()
    ):
        fail("D40-VALIDATE-RECEIPT-PATH")
    lock = read_json(lock_path)
    roles = verify_locked_inputs(native, lock, args.allow_identity_only_public_artifacts)
    bundle = load_bundle(output)
    semantic_errors = validate_bundle(bundle)
    if semantic_errors:
        fail("D40-VALIDATE-MODEL:" + ",".join(semantic_errors))
    native_summary = verify_native_semantics(native, roles, bundle)
    verify_control_evidence(native, roles, bundle)
    verify_public_and_accessibility(
        native,
        roles,
        bundle,
        args.allow_identity_only_public_artifacts,
    )
    verify_views(output, bundle)
    generated_paths = verify_manifest(native, output, lock, bundle)
    isolated = compare_builds(
        native,
        lock_path,
        output,
        generated_paths,
        args.allow_identity_only_public_artifacts,
    )
    negatives = run_negative_fixtures(bundle, ADAPTER / "fixtures/negative")
    receipt = {
        "schema": "d40-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "input_hashes_verified": sum(role_path(native, roles, role).is_file() for role in roles),
        "locked_input_identities_bound": len(roles),
        "identity_only_public_artifacts": (
            2 if args.allow_identity_only_public_artifacts else 0
        ),
        "public_artifact_validation_mode": (
            "identity_only_allowed" if args.allow_identity_only_public_artifacts else "local_bytes_required"
        ),
        "native_semantics": native_summary,
        "mastery_primary_roots": 68,
        "practice_problems": 48,
        "assessment_items": 16,
        "computational_labs": 4,
        "prerequisite_relations": 108,
        "rights_records": 5,
        "dionne_imported_objects": 3920,
        "dionne_chapters": 14,
        "native_supports_relations": 130,
        "native_bodies_copied": False,
        "full_native_roundtrip_claimed": False,
        "adapter_execution_performed": False,
        "execution": {
            "executed_notebooks": 4,
            "execution_surfaces": 8,
            "required_cells": 116,
            "code_cells": 54,
            "markdown_cells": 62,
        },
        "accessibility": {
            "offline_html_availability": "public_zip_member_only",
            "static_mathml_elements": 24_118,
            "runtime_network_dependencies": 0,
            "pdf_tagged_status": "unknown_not_evidenced",
        },
        "public_artifacts": {"pdf": PDF_IDENTITY, "zip": ZIP_IDENTITY},
        "learner_educator_shared_identity": True,
        "archive_members_linked_as_urls": False,
        "isolated_two_build_byte_identity": isolated,
        "negative_fixtures": negatives,
        "manifest_sha256": file_identity(output / "manifest.json")["sha256"],
        "public_state_changed": False,
    }
    write_json(receipt_path, receipt)
    print(
        json.dumps(
            {"state": "pass", "receipt": receipt_path.name, "tree_sha256": isolated["tree_sha256"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (
        D40Error,
        KeyError,
        ValueError,
        OSError,
        csv.Error,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"D40 validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
