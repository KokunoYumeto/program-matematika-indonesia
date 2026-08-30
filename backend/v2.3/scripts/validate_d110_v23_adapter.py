#!/usr/bin/env python3
"""Independently validate the D110 Mathematics in Lean v2.3.1 adapter."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from v231_adapter_common import (
    CAPABILITY_NAMES,
    TABLE_ORDER,
    AdapterError,
    canonical_row_sha256,
    identity_set_sha256,
    mapping_set_sha256,
    projection_id,
    read_json,
    read_jsonl,
    require,
    sha256_file,
    write_json,
)
from validate_lane_adapter_v231 import validate_package as validate_generic_package


COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
LANE_NAMESPACE = uuid.uuid5(uuid.UUID(COMMON_NAMESPACE), "v2.3.1:D110:mathematics-in-lean")
OWNER_NAMESPACE = "mil-backend-record/1.0.0"
CURRENT_COURSE_ID = "urn:uuid:8c8e804d-39b7-5b41-aef7-64fc379f7c5f"
CURRENT_OWNER_DATASET_ID = "urn:uuid:bb9fa013-1c0e-562d-a537-d02a7a627cb8"
NATIVE_COURSE_ID = "urn:mil:course:mathematics-in-lean"
CURRENT_NATIVE_EDITION_ID = "urn:mil:edition:id-id:v4.30.0-id.3"
PUBLIC_HTML = "https://kokunoyumeto.github.io/mathematics-in-lean-id/"
PUBLIC_PDF = "https://github.com/KokunoYumeto/mathematics-in-lean-id/releases/download/v4.30.0-id.3/matematika-dalam-lean-bahasa-indonesia.pdf"

NATIVE_COUNTS = {
    "artifact": 182,
    "asset": 800,
    "concept": 326,
    "correction": 249,
    "course": 1,
    "edition": 6,
    "program": 1,
    "qa_event": 186,
    "relation": 5471,
    "resource": 3,
    "rights": 37,
    "segment": 1213,
    "term": 326,
    "unit": 2177,
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

EXPECTED_TABLE_COUNTS = {
    "owner_authorities": 1,
    "datasets": 1,
    "editions": 6,
    "units": 2177,
    "course_unit_memberships": 2177,
    "native_bindings": 9272,
    "content_bindings": 1213,
    "relations": 5475,
    "rights": 37,
    "rights_assignments": 9272,
    "artifacts": 185,
    "build_recipes": 3,
    "reader_surfaces": 2,
    "routes": 2,
    "search_documents": 2177,
    "adapter_profiles": 1,
    "adapter_runs": 1,
    "qa_events": 186,
    "identity_crosswalks": 9272,
}


def load_tables(package: Path) -> dict[str, list[dict[str, Any]]]:
    return {name: read_jsonl(package / "tables" / f"{name}.jsonl") for name in TABLE_ORDER}


def recursively_forbidden_prose_keys(value: Any, location: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "body", "body_text", "textbook_prose", "source_prose", "target_prose",
                "source_text", "target_text", "solution_text", "proof_text",
            }:
                failures.append(f"{location}.{key}")
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for ordinal, child in enumerate(value):
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}[{ordinal}]"))
    return failures


def native_relation_endpoints(row: dict[str, Any]) -> list[str]:
    data = row.get("data") if isinstance(row.get("data"), dict) else {}
    keys = (
        "subject_id", "object_id", "source_unit_id", "declaration_id", "exercise_id",
        "solution_id", "dependency_unit_id", "dependency_solution_id", "support_id", "code_asset_id",
    )
    return [str(data[key]) for key in keys if data.get(key)]


def validate_specific(args: argparse.Namespace) -> dict[str, Any]:
    package = args.package.resolve()
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    generic_args = SimpleNamespace(
        package=package,
        repository_root=repository_root,
        owner_package_root=owner_root,
        require_authorities=True,
        build_a=args.build_a,
        build_b=args.build_b,
    )
    generic = validate_generic_package(generic_args)
    require(generic["status"] == "PASS", "generic v2.3.1 validation did not pass")
    require(generic["extension_version"] == "0.1.0", "unexpected D110 adapter version")
    require(generic["sidecars"]["scope_roles"] == ["D110"], "adapter scope is not exactly D110")

    tables = load_tables(package)
    observed_counts = {name: len(tables[name]) for name in TABLE_ORDER}
    require(observed_counts == EXPECTED_TABLE_COUNTS, f"D110 canonical table census drift: {observed_counts}")
    require(sum(observed_counts.values()) == 41460, "D110 canonical aggregate drift")

    # Rebuild the complete owner-native census directly from the frozen export.
    native: dict[str, list[dict[str, Any]]] = {}
    all_native: dict[str, dict[str, Any]] = {}
    all_ids: list[str] = []
    for entity_type, expected_count in NATIVE_COUNTS.items():
        rows = read_jsonl(owner_root / "backend" / "exports" / "entities" / f"{entity_type}.jsonl")
        require(len(rows) == expected_count, f"owner-native count drift: {entity_type}")
        require(all(row.get("entity_type") == entity_type for row in rows), f"owner-native type drift: {entity_type}")
        for row in rows:
            native_id = str(row.get("record_id") or "")
            require(native_id and native_id not in all_native, f"duplicate owner-native ID: {native_id}")
            all_native[native_id] = row
            all_ids.append(native_id)
        native[entity_type] = rows
    require(len(all_native) == 10978, "owner-native aggregate drift")
    rights_ids = {str(row["rights_id"]) for row in native["rights"]}
    require(len(rights_ids) == 37, "native rights census drift")
    require(all(str(row.get("rights_id") or "") in rights_ids for rows in native.values() for row in rows), "unresolved native rights pointer")
    relation_endpoint_count = 0
    for relation in native["relation"]:
        endpoints = native_relation_endpoints(relation)
        relation_endpoint_count += len(endpoints)
        require(all(endpoint in all_native for endpoint in endpoints), f"unresolved relation endpoint: {relation['record_id']}")

    authorities = read_json(package / "INPUT_AUTHORITIES.json")
    closure = authorities["owner_native_closure"]
    require(closure == {
        "bytes": 92714008,
        "entity_counts": NATIVE_COUNTS,
        "export_manifest_sha256": "3577912edade478aef93d2a8ef6f4e87284c8cda68fe4a329eddc2f0781eeaa0",
        "files_including_export_manifest": 49,
        "global_native_id_set_sha256": identity_set_sha256(all_ids),
        "materialized_native_records": 9272,
        "records": 10978,
        "result": "pass_with_declared_native_limitations",
        "rights_pointer_resolution": "10978_of_10978",
    }, "D110 input-authority closure drift")
    require(authorities["owner_native_non_mutation"] is True and authorities["body_prose_copied"] is False, "zero-copy authority claim drift")

    # All canonical IDs must be reproducible from the admitted D110 namespace.
    for table_name, rows in tables.items():
        for row in rows:
            require(row["id"] == projection_id(LANE_NAMESPACE, row["record_type"], row["semantic_key"]), f"projected UUID formula drift: {table_name}:{row['semantic_key']}")

    bindings = tables["native_bindings"]
    binding_native_ids = [str(row["payload"]["native_record_id"]) for row in bindings]
    require(len(binding_native_ids) == len(set(binding_native_ids)) == 9272, "native binding bijection failure")
    expected_materialized = {
        str(row["record_id"])
        for entity_type, rows in native.items()
        if entity_type in PROJECTED_NATIVE_TYPES
        for row in rows
    }
    require(set(binding_native_ids) == expected_materialized, "materialized native coverage drift")
    projected_ids = {row["id"] for rows in tables.values() for row in rows}
    target_ids: list[str] = []
    for row in bindings:
        payload = row["payload"]
        native_id = str(payload["native_record_id"])
        native_row = all_native[native_id]
        expected_type = PROJECTED_NATIVE_TYPES[str(native_row["entity_type"])]
        expected_semantic = f"d110:native:{native_id}"
        expected_target = projection_id(LANE_NAMESPACE, expected_type, expected_semantic)
        require(payload["projected_record_type"] == expected_type, f"native target type drift: {native_id}")
        require(payload["projected_record_id"] == expected_target in projected_ids, f"native target identity drift: {native_id}")
        require(payload["native_record_sha256"] == canonical_row_sha256(native_row), f"native row digest drift: {native_id}")
        require(payload["body_prose_copied"] is False, f"native binding copied prose: {native_id}")
        target_ids.append(expected_target)
    require(len(target_ids) == len(set(target_ids)) == 9272, "projected native target collision")

    crosswalks = tables["identity_crosswalks"]
    crosswalk_sources = [str(row["payload"]["source_record_id"]) for row in crosswalks]
    crosswalk_targets = [str(row["payload"]["target_record_id"]) for row in crosswalks]
    require(crosswalk_sources == binding_native_ids or set(crosswalk_sources) == set(binding_native_ids), "crosswalk/native-binding source drift")
    require(set(crosswalk_targets) == set(target_ids), "crosswalk/native-binding target drift")
    require(all(row["payload"]["source_namespace"] == OWNER_NAMESPACE and row["payload"]["cardinality"] == "one_to_one" for row in crosswalks), "crosswalk reversibility drift")
    sidecar_crosswalk = read_json(package / "namespace-crosswalk-v0.2.0.json")
    mappings = [row for row in sidecar_crosswalk["mappings"] if row["source_namespace"] == OWNER_NAMESPACE]
    require(len(mappings) == 9272, "namespace sidecar mapping count drift")
    require({row["source_record_id"] for row in mappings} == set(binding_native_ids), "namespace sidecar identity drift")
    require(sidecar_crosswalk["identity_sets"]["mapped_pairs_sha256"] == mapping_set_sha256(zip(binding_native_ids, target_ids)), "namespace pair-set digest drift")

    # Content is locator/hash-only; segment prose remains in the owner package.
    content = tables["content_bindings"]
    require(len(content) == len(native["segment"]) == 1213, "segment binding census drift")
    segment_ids = {str(row["record_id"]) for row in native["segment"]}
    require({str(row["payload"]["native_segment_id"]) for row in content} == segment_ids, "segment binding identity drift")
    require(all(row["payload"]["body_prose_copied"] is False for row in content), "content binding copied prose")
    require(all(row["payload"].get("source_text_sha256") and row["payload"].get("target_text_sha256") for row in content), "segment hash binding incomplete")
    forbidden: list[str] = []
    for table_name, rows in tables.items():
        for ordinal, row in enumerate(rows, 1):
            forbidden.extend(recursively_forbidden_prose_keys(row, f"tables/{table_name}.jsonl:{ordinal}"))
    require(not forbidden, f"forbidden prose fields in zero-copy adapter: {forbidden[:3]}")
    require(all(row["payload"]["body_prose_copied"] is False for row in tables["search_documents"]), "search projection copied body prose")

    # Rights remain component-scoped; every materialized native projection gets its direct pointer.
    rights = tables["rights"]
    require(len(rights) == 37 and all(row["payload"]["flattened_course_license"] is False for row in rights), "rights flattening or census drift")
    rights_assignments = tables["rights_assignments"]
    require(len(rights_assignments) == 9272, "rights assignment census drift")
    require({row["payload"]["target_native_id"] for row in rights_assignments} == expected_materialized, "rights assignment native coverage drift")
    projected_rights_ids = {row["id"] for row in rights}
    require(all(row["payload"]["current_rights_id"] in projected_rights_ids for row in rights_assignments), "projected rights pointer failure")

    # Native states and known source-side gaps are preserved, not normalized away.
    owner_states = {
        str(row.get("translation_state") or row.get("status") or "recorded")
        for entity_type, rows in native.items()
        if entity_type in PROJECTED_NATIVE_TYPES
        for row in rows
    }
    binding_states = {str(row["owner_native_state"]) for row in bindings}
    require(binding_states == owner_states, "owner-native state vocabulary drift")
    draft_count = sum(1 for entity_type in ("asset", "artifact") for row in native[entity_type] if row.get("translation_state") == "draft")
    require(draft_count == 90, "native draft census drift")
    require(sum(1 for row in native["unit"] if row.get("locale") == "und" and row.get("language") == "zxx") == 2177, "native unit locale/language gap drift")
    require(sum(1 for row in native["unit"] if row.get("prerequisite_ids")) == 0, "native prerequisite-array gap drift")
    require(sum(1 for row in native["relation"] if row.get("data", {}).get("relation_type") == "prerequisite") == 596, "native prerequisite relation census drift")

    translation = read_json(package / "translation-state-index-v0.2.0.json")
    require(translation["coverage"] == {
        "authority_rows": 2177,
        "course_id": "D110",
        "granularity": "owner_native_unit_record",
        "indexed_rows": 2177,
        "inferred_rows": 0,
    }, "translation coverage drift")
    require(translation["no_inference"] is True and len(translation["records"]) == 2177, "translation state index drift")
    require(all(row["state_inferred"] is False and row["native_locale"] == "und" and row["native_language"] == "zxx" for row in translation["records"]), "translation-state inference or locale rewrite")
    require(translation["identity_set_sha256"] == identity_set_sha256(row["projected_unit_id"] for row in translation["records"]), "translation identity-set drift")

    limitations = read_json(package / "evidence" / "D110_NATIVE_LIMITATIONS.json")
    require(limitations["native_unit_locale"] == "und" and limitations["native_unit_language"] == "zxx", "native locale limitation missing")
    require(limitations["native_prerequisite_relation_records"] == 596 and limitations["native_unit_prerequisite_array_rows_nonempty"] == 0, "prerequisite limitation missing")
    require(limitations["pdf_tagged"] is False and limitations["primary_accessibility_surface"] == "semantic_html", "accessibility limitation missing")
    require(limitations["native_asset_artifact_draft_records"] == 90, "draft-state limitation missing")
    require(limitations["github_receipt_stale_backend_records_scalar"] == 10876 and limitations["authoritative_backend_records"] == 10978, "stale receipt limitation missing")

    # Exact learner-facing public route remains primary; machine data is secondary.
    surfaces = {row["payload"]["surface_kind"]: row["payload"] for row in tables["reader_surfaces"]}
    require(set(surfaces) == {"semantic_html", "offline_pdf"}, "reader surface census drift")
    require(surfaces["semantic_html"]["url"] == PUBLIC_HTML and surfaces["semantic_html"]["primary_learner_surface"] is True, "HTML learner route drift")
    require(surfaces["offline_pdf"]["url"] == PUBLIC_PDF and surfaces["offline_pdf"]["pages"] == 219 and surfaces["offline_pdf"]["tagged"] is False, "PDF route/accessibility drift")
    routes = {row["payload"]["route_kind"]: row["payload"] for row in tables["routes"]}
    require(routes["learner_course_root"]["url"] == PUBLIC_HTML and routes["learner_course_root"]["verified"] is True, "learner route state drift")
    require(routes["offline_pdf_download"]["url"] == PUBLIC_PDF and routes["offline_pdf_download"]["verified"] is True, "PDF route state drift")
    require(all(row["payload"]["learner_anchor"] is None for row in tables["search_documents"]), "invented per-unit route")

    capability = read_json(package / "capability-declarations-v0.2.0.json")
    require([row["name"] for row in capability["capabilities"]] == CAPABILITY_NAMES, "capability names/order drift")
    gap_states = {row["name"]: row["loss_gap_report"]["status"] for row in capability["capabilities"]}
    require(gap_states == {
        "structure_localization": "closed",
        "terminology": "declared_limitation",
        "mathematical_preservation": "declared_limitation",
        "assessment_support": "declared_limitation",
        "assets": "declared_limitation",
        "accessibility": "declared_limitation",
        "corrections": "declared_limitation",
        "computational_interactives": "declared_limitation",
        "publication": "closed",
        "research_support": "declared_limitation",
    }, "capability truth table drift")

    return {
        "schema_id": "program-matematika-indonesia/d110-v2.3.1-adapter-validation/1",
        "status": "PASS",
        "generic_validation": generic,
        "owner_native": {
            "files_including_export_manifest": 49,
            "records": 10978,
            "global_id_set_sha256": identity_set_sha256(all_ids),
            "rights_pointers_resolved": 10978,
            "relation_endpoints_replayed": relation_endpoint_count,
        },
        "adapter": {
            "canonical_records": 41460,
            "materialized_native_bijections": 9272,
            "unmaterialized_native_records_hash_bound_by_shard": 1706,
            "translation_rows": 2177,
            "content_hash_bindings": 1213,
            "rights_assignments": 9272,
            "csv_roundtrip": "PASS",
            "body_prose_copied": False,
            "component_rights_flattened": False,
            "learner_route": PUBLIC_HTML,
        },
        "limitations_preserved": gap_states,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--build-a", type=Path)
    parser.add_argument("--build-b", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = validate_specific(args)
        if args.report:
            write_json(args.report, report)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
