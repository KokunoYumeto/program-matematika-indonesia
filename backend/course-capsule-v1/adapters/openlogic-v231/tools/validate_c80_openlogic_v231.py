#!/usr/bin/env python3
"""Validate generic and C80-specific invariants of the Open Logic adapter."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from v231_adapter_common import (
    TABLE_ORDER,
    AdapterError,
    compact_json,
    identity_set_sha256,
    read_json,
    read_jsonl,
    require,
    sha256_file,
    write_json,
)
from validate_lane_adapter_v231 import validate_package


V1_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
OWNER_NAMESPACE = "openlogic-olp-closure-id-v1"
LANE_NAMESPACE = "20b4a5f0-524a-5ef7-a271-7b188d658a4f"
PREVIEW_URL = "https://zenodo.org/records/21932787/preview/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf"

EXPECTED_COUNTS = {
    "owner_authorities": 1, "datasets": 1, "editions": 2, "units": 722,
    "course_unit_memberships": 722, "native_bindings": 722, "content_bindings": 722,
    "relations": 725, "rights": 1, "rights_assignments": 728, "artifacts": 4,
    "build_recipes": 0, "reader_surfaces": 1, "routes": 9, "search_documents": 722,
    "adapter_profiles": 1, "adapter_runs": 1, "qa_events": 1, "identity_crosswalks": 722,
}

EXPECTED_ARTIFACTS = {
    "00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf": (5593664, "bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a"),
    "01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip": (1580716, "492fd7369de367e2e748b0cbac8ba9a4c8c624f2a756a8943de445b9650283ed"),
    "02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip": (2000807, "273f790b9ddfaade9a6388c0d8cbd8b89006fca8f8c0da89cb2b5afcf1ae9441"),
    "03_OPENLOGIC_id_SHA256SUMS_OLP-0722.txt": (401, "d5b2f18fb24fd5469dafcb9ab91717b04a62d0fb437a68984b2c94ac254e9c60"),
}


def previous_v1_unit_id(closure_id: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(V1_NAMESPACE, f"unit|openlogic:{closure_id}"))


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def table_rows(package: Path) -> dict[str, list[dict[str, Any]]]:
    return {name: read_jsonl(package / "tables" / f"{name}.jsonl") for name in TABLE_ORDER}


def validate_c80_semantics(package: Path) -> dict[str, Any]:
    package = package.resolve()
    tables = table_rows(package)
    observed_counts = {name: len(tables[name]) for name in TABLE_ORDER}
    require(observed_counts == EXPECTED_COUNTS, f"C80 table counts drift: {observed_counts}")

    inventory = read_csv(package / "evidence" / "FINAL_INVENTORY_0722.csv")
    closure = read_csv(package / "evidence" / "STRUCTURAL_CLOSURE_MANIFEST_0722.csv")
    components = read_csv(package / "evidence" / "COMPONENT_COVERAGE.tsv", "\t")
    expected_ids = [f"OLP-{ordinal:04d}" for ordinal in range(1, 723)]
    require([row["closure_id"] for row in inventory] == expected_ids, "sealed inventory IDs/order drift")
    require([row["closure_id"] for row in closure] == expected_ids, "sealed closure IDs/order drift")
    require([row["component_id"] for row in components] == expected_ids, "sealed component IDs/order drift")
    closure_by_id = {row["closure_id"]: row for row in closure}
    component_by_id = {row["component_id"]: row for row in components}
    source_path_to_id = {row["source_path"]: row["closure_id"] for row in inventory}

    units_by_native: dict[str, dict[str, Any]] = {}
    for row in tables["units"]:
        payload = row["payload"]
        native_id = str(payload.get("native_unit_id"))
        require(native_id not in units_by_native, f"duplicate native unit: {native_id}")
        units_by_native[native_id] = row
    require(sorted(units_by_native) == expected_ids, "projected unit identity set is not OLP-0001..OLP-0722")

    source_bytes = target_bytes = reader_reachable = 0
    projected_by_native: dict[str, str] = {}
    for authority in inventory:
        closure_id = authority["closure_id"]
        detail = closure_by_id[closure_id]
        component = component_by_id[closure_id]
        row = units_by_native[closure_id]
        payload = row["payload"]
        projected_by_native[closure_id] = row["id"]
        require(payload["translation_state"] == "complete", f"unit translation state drift: {closure_id}")
        require(payload["previous_v1_unit_id"] == previous_v1_unit_id(closure_id), f"v1 unit crosswalk drift: {closure_id}")
        require(payload["native_locator"] == {
            "closure_id": closure_id, "source_path": authority["source_path"], "target_path": authority["target_path"]
        }, f"native locator drift: {closure_id}")
        for prefix in ("source", "target"):
            require(payload[f"{prefix}_sha256"] == authority[f"{prefix}_sha256"].lower(), f"{prefix} hash drift: {closure_id}")
            require(payload[f"{prefix}_bytes"] == int(authority[f"{prefix}_bytes"]), f"{prefix} bytes drift: {closure_id}")
            require(payload[f"{prefix}_lines"] == int(authority[f"{prefix}_lines"]), f"{prefix} lines drift: {closure_id}")
        require(payload["canonical_reader_reachable"] == (detail["canonical_reader_reachable"].lower() == "true"), f"reader state drift: {closure_id}")
        require(payload["localized_title"] is None, f"localized title invented: {closure_id}")
        require(payload["learner_route"]["anchor"] is None and payload["learner_route"]["url"] == PREVIEW_URL, f"unit learner route drift: {closure_id}")
        require(component["translation_status"] == "complete" and component["exact_coverage"] == "full source unit", f"component state drift: {closure_id}")
        require(component["artifact_sha256"].lower() == authority["target_sha256"].lower(), f"component hash drift: {closure_id}")
        source_bytes += int(authority["source_bytes"])
        target_bytes += int(authority["target_bytes"])
        reader_reachable += int(payload["canonical_reader_reachable"])
    require((source_bytes, target_bytes, reader_reachable) == (3051826, 3222301, 642), "C80 aggregate authority drift")

    membership_by_native = {row["payload"]["native_unit_id"]: row for row in tables["course_unit_memberships"]}
    native_binding_by_id = {row["payload"]["native_id"]: row for row in tables["native_bindings"]}
    content_by_native = {row["payload"]["native_unit_id"]: row for row in tables["content_bindings"]}
    search_by_native = {row["payload"]["native_unit_id"]: row for row in tables["search_documents"]}
    crosswalk_by_source = {row["payload"]["source_id"]: row for row in tables["identity_crosswalks"]}
    for ordinal, authority in enumerate(inventory, 1):
        closure_id = authority["closure_id"]
        projected_id = projected_by_native[closure_id]
        membership = membership_by_native[closure_id]["payload"]
        require(membership["ordinal"] == ordinal and membership["unit_id"] == projected_id, f"membership drift: {closure_id}")
        native = native_binding_by_id[closure_id]["payload"]
        require(native["native_namespace"] == OWNER_NAMESPACE and native["subject_id"] == projected_id, f"native binding drift: {closure_id}")
        content = content_by_native[closure_id]["payload"]
        require(content["zero_copy"] is True and content["content_included_in_adapter"] is False, f"zero-copy drift: {closure_id}")
        require(content["source"]["sha256"] == authority["source_sha256"].lower(), f"content source drift: {closure_id}")
        require(content["target"]["sha256"] == authority["target_sha256"].lower(), f"content target drift: {closure_id}")
        require(not ({"text", "content", "body", "prose", "formula", "proof"} & set(content)), f"content body leaked: {closure_id}")
        search = search_by_native[closure_id]["payload"]
        require(search["localized_title"] is None and search["learner_anchor"] is None and search["learner_url"] == PREVIEW_URL, f"search route/title drift: {closure_id}")
        crosswalk = crosswalk_by_source[closure_id]["payload"]
        require(crosswalk["target_id"] == projected_id and crosswalk["previous_v1_unit_id"] == previous_v1_unit_id(closure_id), f"identity crosswalk drift: {closure_id}")

    expected_relations: list[tuple[str, int, str]] = []
    for authority in inventory:
        detail = closure_by_id[authority["closure_id"]]
        imports = [value for value in detail.get("imports_resolved_ordered", "").split("|") if value]
        require(len(imports) == int(detail.get("import_count") or 0), f"sealed import count drift: {authority['closure_id']}")
        require(not detail.get("imports_unresolved"), f"sealed unresolved import: {authority['closure_id']}")
        for ordinal, target_path in enumerate(imports, 1):
            require(target_path in source_path_to_id, f"sealed import outside closure: {target_path}")
            expected_relations.append((authority["closure_id"], ordinal, source_path_to_id[target_path]))
    observed_relations = sorted(
        (row["payload"]["from_endpoint"]["native_id"], int(row["payload"]["ordinal"]), row["payload"]["to_endpoint"]["native_id"])
        for row in tables["relations"]
    )
    require(observed_relations == sorted(expected_relations) and len(observed_relations) == 725, "ordered import topology drift")
    require(all(row["payload"]["concept_relation_inferred"] is False for row in tables["relations"]), "concept relation inference introduced")

    rights = tables["rights"][0]["payload"]
    require(rights["license_expression"] == "CC-BY-4.0" and rights["flattened_course_license"] is False, "rights declaration drift")
    unit_ids = {row["id"] for row in tables["units"]}
    edition_ids = {row["id"] for row in tables["editions"]}
    artifact_ids = {row["id"] for row in tables["artifacts"]}
    assignment_targets = {row["payload"]["target_id"] for row in tables["rights_assignments"]}
    require(assignment_targets == unit_ids | edition_ids | artifact_ids, "rights assignment target closure drift")

    observed_artifacts = {
        row["payload"]["filename"]: (row["payload"]["bytes"], row["payload"]["sha256"])
        for row in tables["artifacts"]
    }
    require(observed_artifacts == EXPECTED_ARTIFACTS, "public artifact identity drift")
    surfaces = tables["reader_surfaces"]
    require(len(surfaces) == 1, "reader surface cardinality drift")
    surface = surfaces[0]["payload"]
    require(surface["format"] == "linked_pdf" and surface["pages"] == 1116 and surface["public_url"] == PREVIEW_URL, "reader surface drift")
    require(surface["unit_anchor_coverage"] == 0 and surface["primary"] is True, "reader anchor/primacy drift")
    for row in tables["routes"]:
        payload = row["payload"]
        require(payload["unit_id"] is None and payload["unit_anchor"] is None, "invented unit route")
        require("html" not in payload["route_kind"].lower() and "html" not in payload["target_kind"].lower(), "invented HTML route")
    require(any(row["payload"]["route_kind"] == "linked_pdf_preview" and row["payload"]["public_url"] == PREVIEW_URL for row in tables["routes"]), "verified learner PDF preview route missing")

    translation = read_json(package / "translation-state-index-v0.2.0.json")
    require(translation["coverage"] == {
        "authority_rows": 722, "course_id": "C80", "granularity": "complete_source_file_unit", "indexed_rows": 722, "inferred_rows": 0
    }, "translation coverage drift")
    require(translation["states"] == ["complete"] and translation["no_inference"] is True, "translation state inference/staleness")
    require([row["native_unit_id"] for row in translation["records"]] == expected_ids, "translation record order/identity drift")
    require(all(row["state"] == "complete" for row in translation["records"]), "non-complete translation state")

    namespace = read_json(package / "namespace-crosswalk-v0.2.0.json")
    require([profile["namespace"] for profile in namespace["profiles"]] == [OWNER_NAMESPACE, str(V1_NAMESPACE), LANE_NAMESPACE], "namespace profile drift")
    require(len(namespace["mappings"]) == 1445, "namespace mapping count drift")
    owner_mappings = [row for row in namespace["mappings"] if row["source_namespace"] == OWNER_NAMESPACE]
    v1_unit_mappings = [row for row in namespace["mappings"] if row["source_namespace"] == str(V1_NAMESPACE) and row["source_record_type"] == "unit"]
    course_mappings = [row for row in namespace["mappings"] if row["source_record_type"] == "course"]
    require(len(owner_mappings) == len(v1_unit_mappings) == 722 and len(course_mappings) == 1, "namespace mapping partition drift")
    require({row["source_record_id"] for row in owner_mappings} == set(expected_ids), "owner mapping identity drift")
    require({row["source_record_id"] for row in v1_unit_mappings} == {previous_v1_unit_id(value) for value in expected_ids}, "v1 mapping identity drift")

    capabilities = read_json(package / "capability-declarations-v0.2.0.json")
    state_by_name = {row["name"]: row["state"] for row in capabilities["capabilities"]}
    require(state_by_name == {
        "structure_localization": "materialized", "terminology": "referenced_native_shards",
        "mathematical_preservation": "referenced_native_shards", "assessment_support": "not_projected",
        "assets": "referenced_native_shards", "accessibility": "referenced_native_shards",
        "corrections": "referenced_native_shards", "computational_interactives": "not_projected",
        "publication": "materialized", "research_support": "referenced_native_shards",
    }, "capability state drift")
    scope = read_json(package / "scope-declaration-v0.2.0.json")
    require(scope["curriculum_role_ids"] == ["C80"] and scope["aggregate_conformance_claim"] is False, "scope drift")
    require(len(scope["unbound_curriculum_role_ids"]) == 39 and "C80" not in scope["unbound_curriculum_role_ids"], "unbound-role scope drift")

    table_bytes = b"".join((package / "tables" / f"{name}.jsonl").read_bytes() for name in TABLE_ORDER)
    require(b'"translated_file_present"' not in table_bytes and b'"missing"' not in table_bytes, "historical closure state leaked into current tables")
    require(b"00_OPENLOGIC_id_COMPLETE_READER_OLP-0722.pdf" not in table_bytes, "loose 934-page PDF drift leaked")

    return {
        "status": "PASS",
        "table_counts": observed_counts,
        "authority_units": 722,
        "reader_reachable": reader_reachable,
        "retained_non_reader": 722 - reader_reachable,
        "import_relations": len(observed_relations),
        "source_bytes": source_bytes,
        "target_bytes": target_bytes,
        "translation_rows": len(translation["records"]),
        "namespace_mappings": len(namespace["mappings"]),
        "rights_assignments": len(tables["rights_assignments"]),
        "routes": len(tables["routes"]),
        "native_html_claimed": False,
        "unit_or_page_anchors_claimed": False,
        "historical_translation_state_leaks": 0,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--owner-package-root", type=Path)
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
        semantic = validate_c80_semantics(args.package)
        report = {
            "schema_id": "program-matematika-indonesia/c80-openlogic-v231-validation/1.0.0",
            "status": "PASS",
            "package": {"manifest_bytes": (args.package / "manifest.json").stat().st_size, "manifest_sha256": sha256_file(args.package / "manifest.json")},
            "generic": generic,
            "c80_semantics": semantic,
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
