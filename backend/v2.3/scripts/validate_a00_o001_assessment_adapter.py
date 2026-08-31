#!/usr/bin/env python3
"""Validate the additive A00/O001 assessment-route adapter semantically."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

import validate_lane_adapter_v231 as generic_validator
from v231_adapter_common import (
    AdapterError,
    ROW_ENVELOPE_KEYS,
    TABLE_ORDER,
    combined_shard_identity,
    compact_json,
    identity_set_sha256,
    read_json,
    read_jsonl,
    require,
    sha256_bytes,
    sha256_file,
    write_json,
)


A00_ROOT = "backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0"
O001_ROOT = "backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0"
A00_MANIFEST_SHA256 = "b196d0b851fa0f6b3b7972ab33b762898f3d577fbc26b6214542d6a5b10009af"
O001_MANIFEST_SHA256 = "5ed7b558ae1f621bef52b59be64df90dbf52c967c7e12e2fc9fc296309e2b19e"
EXPECTED_MODULE_UNIT_SHA256 = "dca9b8dfe1aad797315d6c7186665eedcdcd045bde8514ad91448b3484342dfe"
EXPECTED_NATIVE_UNION_SHA256 = "990cf0ffbb5e4ce67fd12ac4bba6111745fa193e026a2b3d8a05162bc48c3240"
EXPECTED_PATTERN_AUDIT_SHARDS_SHA256 = "ee21807297f7ac0b04c00ccbf7b3c1eae5ba9ff7bc48f20d0f236b389f259455"


class AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name.lower() == "id" and value is not None:
                self.ids[value] += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def path_from(root: Path, relative: str) -> Path:
    return root.joinpath(*PurePosixPath(relative).parts)


def validate_schema(instance: Any, schema: Mapping[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        first = errors[0]
        location = "/".join(str(item) for item in first.absolute_path) or "$"
        raise AdapterError(f"schema failure {label} at {location}: {first.message}")


def verify_declared_package(manifest_path: Path, expected_sha256: str) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    require(manifest_path.is_file(), f"missing sealed manifest: {manifest_path.name}")
    require(sha256_file(manifest_path) == expected_sha256, f"sealed manifest hash drift: {manifest_path.name}")
    manifest = read_json(manifest_path)
    entries = {str(row["path"]): row for row in manifest["files"]}
    require(len(entries) == len(manifest["files"]), f"duplicate declared member: {manifest_path.name}")
    for relative, row in entries.items():
        target = path_from(manifest_path.parent, relative)
        require(target.is_file(), f"missing sealed member: {relative}")
        require(target.stat().st_size == int(row["bytes"]), f"sealed member byte drift: {relative}")
        require(sha256_file(target) == str(row["sha256"]), f"sealed member hash drift: {relative}")
    return manifest, entries


def module_from_unit(row: Mapping[str, Any]) -> str:
    parts = str(row["semantic_key"]).split(":")
    require("unit" in parts, f"A00 unit semantic key drift: {row['semantic_key']}")
    module = parts[parts.index("unit") + 1]
    require(module.startswith("m") and module[1:].isdigit(), f"A00 unit module drift: {module}")
    return module


def validate_common_spine(package: Path, a00_package: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    total = 0
    for table_name in TABLE_ORDER:
        source_rows = read_jsonl(a00_package / "tables" / f"{table_name}.jsonl")
        projected_rows = read_jsonl(package / "tables" / f"{table_name}.jsonl")
        expected = [{key: row[key] for key in ROW_ENVELOPE_KEYS} for row in source_rows]
        expected.sort(key=lambda row: (str(row["semantic_key"]), str(row["id"])))
        require(projected_rows == expected, f"common A00 spine differs in {table_name}")
        tables[table_name] = projected_rows
        total += len(projected_rows)
    require(total == 1313, "common A00 spine is not exactly 1,313 records")
    require(len(tables["units"]) == len(tables["routes"]) == len(tables["reader_surfaces"]) == 75, "A00 navigation table count drift")
    module_pairs = [(module_from_unit(row), str(row["id"])) for row in tables["units"]]
    module_digest = sha256_bytes("".join(f"{module}\0{unit_id}\n" for module, unit_id in sorted(module_pairs)).encode("utf-8"))
    require(module_digest == EXPECTED_MODULE_UNIT_SHA256, "A00 module-to-unit mapping digest drift")
    return tables, {"records": total, "module_unit_mapping_sha256": module_digest}


def read_custom_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.reader(stream))


def validate_custom_csv(path: Path, rows: list[dict[str, Any]], label: str) -> None:
    csv_rows = read_custom_csv(path)
    require(csv_rows and csv_rows[0] == ["stable_id", "record_type", "canonical_record_json"], f"custom CSV header drift: {label}")
    require(len(csv_rows) - 1 == len(rows), f"custom CSV row count drift: {label}")
    for ordinal, (csv_row, row) in enumerate(zip(csv_rows[1:], rows, strict=True), 1):
        require(csv_row == [str(row["id"]), str(row["record_type"]), compact_json(row)], f"custom CSV roundtrip drift: {label}:{ordinal}")


def validate_no_prose_payload(rows: Iterable[Mapping[str, Any]]) -> None:
    forbidden = {"text", "body", "content", "formula", "math", "latex", "problem_text", "solution_text"}

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            require(not (set(value) & forbidden), f"forbidden prose/formula-bearing key: {sorted(set(value) & forbidden)}")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for row in rows:
        walk(row)


def module_registry(a00_tables: Mapping[str, list[dict[str, Any]]], owner_root: Path) -> dict[str, dict[str, Any]]:
    routes = {str(row["payload"]["unit_id"]): row for row in a00_tables["routes"]}
    surfaces = {str(row["id"]): row for row in a00_tables["reader_surfaces"]}
    bindings = {str(row["id"]): row for row in a00_tables["content_bindings"]}
    result: dict[str, dict[str, Any]] = {}
    for unit in a00_tables["units"]:
        module = module_from_unit(unit)
        route = routes[str(unit["id"])]
        surface = surfaces[str(route["payload"]["surface_id"])]
        evidence_ids = list(route["payload"]["evidence_binding_ids"])
        require(len(evidence_ids) == 1 and evidence_ids[0] in bindings, f"A00 route evidence drift: {module}")
        binding = bindings[evidence_ids[0]]
        html_relative = str(binding["payload"]["locator"])
        require(html_relative == f"output/html-id/modules/{module}/index.html", f"HTML path drift: {module}")
        html_path = path_from(owner_root, html_relative)
        require(html_path.is_file(), f"owner HTML missing: {module}")
        require(html_path.stat().st_size == int(binding["payload"]["bytes"]), f"owner HTML byte drift: {module}")
        require(sha256_file(html_path) == str(binding["payload"]["sha256"]), f"owner HTML hash drift: {module}")
        parser = AnchorCollector()
        parser.feed(html_path.read_text(encoding="utf-8"))
        parser.close()
        result[module] = {
            "unit": unit, "route": route, "surface": surface, "binding": binding,
            "html_relative": html_relative, "html_bytes": html_path.stat().st_size,
            "html_sha256": sha256_file(html_path), "anchors": parser.ids,
        }
    require(len(result) == 75, "HTML module registry count drift")
    return result


def validate_projection_row(
    projected: Mapping[str, Any],
    native: Mapping[str, Any],
    source_path: str,
    row_ordinal: int,
    module_record: Mapping[str, Any],
    fixed: Mapping[str, str],
    projected_type: str,
    native_type: str,
) -> None:
    require(projected["record_type"] == projected_type and native["record_type"] == native_type, "custom/native record type drift")
    require(projected["id"] == native["id"], f"owner-native ID changed: {native['id']}")
    owner_source = projected["owner_source"]
    require(owner_source == {"package_id": fixed["o001_package_id"], "table_path": source_path, "row_ordinal": row_ordinal}, f"owner-source locator drift: {native['id']}")
    ignored = {"record_type"}
    additions = {"a00_binding", "route", "owner_source", "mapping_state"}
    require({key: projected[key] for key in projected if key not in additions | ignored} == {key: native[key] for key in native if key not in ignored}, f"native structural metadata changed: {native['id']}")
    expected_a00 = {
        "course_id": fixed["course_id"], "edition_id": fixed["edition_id"],
        "owner_authority_id": fixed["owner_authority_id"], "unit_id": str(module_record["unit"]["id"]),
        "unit_rights_id": fixed["rights_id"],
        "component_rights_state": "preserved_in_sealed_A00_native_rights_shard_not_flattened",
        "reader_surface_id": str(module_record["surface"]["id"]),
        "route_id": str(module_record["route"]["id"]),
    }
    require(projected["a00_binding"] == expected_a00, f"A00 binding drift: {native['id']}")
    native_id = str(projected.get("native_id", projected.get("native_exercise_id")))
    require(module_record["anchors"].get(native_id, 0) == 1, f"HTML anchor cardinality drift: {native['id']}")
    module_url = str(module_record["route"]["payload"]["public_url"])
    expected_route = {
        "module_url": module_url, "fragment": native_id, "public_url": f"{module_url}#{native_id}",
        "target_kind": "readable_semantic_html_anchor",
        "html_evidence": {
            "owner_relative_path": module_record["html_relative"], "bytes": module_record["html_bytes"],
            "sha256": module_record["html_sha256"], "anchor_occurrences": 1,
        },
    }
    require(projected["route"] == expected_route, f"exact anchor route drift: {native['id']}")


def validate_custom_sidecars(
    package: Path,
    repository_root: Path,
    owner_root: Path,
    tables: Mapping[str, list[dict[str, Any]]],
    a00_manifest: Mapping[str, Any],
    o001_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    row_schema = read_json(package / "schema" / "assessment-route-binding-v0.1.schema.json")
    manifest_schema = read_json(package / "schema" / "assessment-capability-manifest-v0.1.schema.json")
    assessments = read_jsonl(package / "assessment-bindings-v0.1.0.jsonl")
    components = read_jsonl(package / "assessment-component-bindings-v0.1.0.jsonl")
    gaps = read_jsonl(package / "solution-gaps-v0.1.0.jsonl")
    require((len(assessments), len(components), len(gaps)) == (8105, 13345, 2865), "custom sidecar count drift")
    for label, rows in (("assessments", assessments), ("components", components), ("gaps", gaps)):
        for ordinal, row in enumerate(rows, 1):
            validate_schema(row, row_schema, f"{label}:{ordinal}")
    capability = read_json(package / "assessment-capability-v0.1.0.json")
    validate_schema(capability, manifest_schema, "assessment-capability-v0.1.0.json")

    source_root = path_from(repository_root, O001_ROOT)
    native_assessments = read_jsonl(source_root / "data" / "assessments.jsonl")
    native_components = read_jsonl(source_root / "data" / "assessment-components.jsonl")
    native_gaps = read_jsonl(source_root / "data" / "solution-gaps.jsonl")
    native_union = identity_set_sha256(str(row["id"]) for rows in (native_assessments, native_components, native_gaps) for row in rows)
    require(native_union == EXPECTED_NATIVE_UNION_SHA256, "O001 native union digest drift")
    native_combined_shards = combined_shard_identity([
        {
            "path": f"{O001_ROOT}/data/assessments.jsonl", "records": 8105,
            "record_id_set_sha256": identity_set_sha256(str(row["id"]) for row in native_assessments),
        },
        {
            "path": f"{O001_ROOT}/data/assessment-components.jsonl", "records": 13345,
            "record_id_set_sha256": identity_set_sha256(str(row["id"]) for row in native_components),
        },
        {
            "path": f"{O001_ROOT}/data/solution-gaps.jsonl", "records": 2865,
            "record_id_set_sha256": identity_set_sha256(str(row["id"]) for row in native_gaps),
        },
    ])
    require(native_combined_shards == EXPECTED_PATTERN_AUDIT_SHARDS_SHA256, "O001 combined-shard digest drift")
    require(capability["identity_sets"]["combined"] == native_union, "custom combined identity digest differs from O001")
    require(capability["module_unit_mapping_sha256"] == EXPECTED_MODULE_UNIT_SHA256, "custom module mapping digest drift")
    require(capability["pattern_audit_combined_shards_sha256"] == native_combined_shards, "pattern-audit combined-shard digest drift")

    a00_owner = tables["owner_authorities"][0]
    a00_dataset = tables["datasets"][0]
    a00_edition = tables["editions"][0]
    a00_rights = tables["rights"][0]
    fixed = {
        "course_id": str(a00_dataset["payload"]["course_ids"][0]),
        "edition_id": str(a00_edition["id"]), "owner_authority_id": str(a00_owner["id"]),
        "rights_id": str(a00_rights["id"]), "o001_package_id": str(o001_manifest["package_id"]),
    }
    modules = module_registry(tables, owner_root)
    for ordinal, (projected, native) in enumerate(zip(assessments, native_assessments, strict=True), 1):
        validate_projection_row(projected, native, "data/assessments.jsonl", ordinal, modules[str(native["module"])], fixed, "assessment_binding", "assessment")
    for ordinal, (projected, native) in enumerate(zip(components, native_components, strict=True), 1):
        validate_projection_row(projected, native, "data/assessment-components.jsonl", ordinal, modules[str(native["module"])], fixed, "assessment_component_binding", "assessment_component")
    for ordinal, (projected, native) in enumerate(zip(gaps, native_gaps, strict=True), 1):
        validate_projection_row(projected, native, "data/solution-gaps.jsonl", ordinal, modules[str(native["module"])], fixed, "solution_gap_binding", "solution_gap")
        require(projected["mapping_state"] == "explicit_absence_preserved_no_solution_invented", f"gap state drift: {projected['id']}")

    assessment_ids = {str(row["id"]) for row in native_assessments}
    require(all(str(row["assessment_id"]) in assessment_ids for row in native_components), "orphan component in O001")
    require(all(str(row["assessment_id"]) in assessment_ids for row in native_gaps), "orphan gap in O001")
    missing_assessments = {str(row["id"]) for row in native_assessments if row["solution_availability"] == "missing_source_and_target"}
    require(missing_assessments == {str(row["assessment_id"]) for row in native_gaps}, "solution-gap set is not exact")
    require(sum(row["component_kind"] == "statement" for row in native_components) == 8105, "statement count drift")
    require(sum(row["component_kind"] == "solution" for row in native_components) == 5240, "solution count drift")

    validate_custom_csv(package / "assessment-csv" / "assessment-bindings.csv", assessments, "assessments")
    validate_custom_csv(package / "assessment-csv" / "assessment-component-bindings.csv", components, "components")
    validate_custom_csv(package / "assessment-csv" / "solution-gaps.csv", gaps, "gaps")
    validate_no_prose_payload([*assessments, *components, *gaps])

    require(capability["counts"] == {
        "modules": 75, "assessments": 8105, "assessment_components": 13345,
        "solution_gaps": 2865, "statement_components": 8105, "solution_components": 5240,
        "exact_html_anchor_routes": 21450,
    }, "assessment capability counts drift")
    require(capability["loss_accounting"] == {
        "explicit_no_solution_gaps": 2865, "invented_solutions": 0,
        "unmapped_assessments": 0, "unmapped_components": 0, "missing_anchors": 0,
    }, "loss accounting drift")
    require(capability["component_rights_policy"] == {
        "native_component_exceptions": 18,
        "state": "preserved_in_sealed_A00_native_rights_shard_not_flattened",
    }, "component-rights exception policy was flattened or lost")
    capability_declarations = read_json(package / "capability-declarations-v0.2.0.json")
    assessment_declaration = next(row for row in capability_declarations["capabilities"] if row["name"] == "assessment_support")
    require(assessment_declaration["state"] == "referenced_native_shards", "assessment capability must remain referenced_native_shards")
    require(assessment_declaration["native_count"] == 24315 and assessment_declaration["projected_count"] == 0, "assessment native/projected counts drift")
    require(assessment_declaration["identity_set_sha256"] == EXPECTED_NATIVE_UNION_SHA256, "assessment capability identity digest drift")
    require(len(tables["units"]) == 75, "assessment/component was promoted to a common unit")
    common_ids = {str(row["id"]) for rows in tables.values() for row in rows}
    require(not (common_ids & assessment_ids), "assessment owner IDs appeared in common tables")
    require(not (common_ids & {str(row["id"]) for row in native_components}), "component owner IDs appeared in common tables")
    require(a00_manifest["record_count"] == 1313, "A00 sealed record count drift")
    return {
        "status": "PASS", "common_spine_records": 1313,
        "assessments": 8105, "assessment_components": 13345, "solution_gaps": 2865,
        "exact_html_anchor_routes": 21450, "missing_html_anchors": 0, "duplicate_html_anchors": 0,
        "navigation_units_promoted": 0, "mathematical_prose_or_formula_bodies_copied": 0,
        "module_unit_mapping_sha256": EXPECTED_MODULE_UNIT_SHA256,
        "native_union_sha256": native_union,
        "pattern_audit_combined_shards_sha256": EXPECTED_PATTERN_AUDIT_SHARDS_SHA256,
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    package = args.package.resolve()
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    require(package.is_dir() and repository_root.is_dir() and owner_root.is_dir(), "package/repository/owner root missing")

    generic_args = argparse.Namespace(
        package=package, repository_root=repository_root, owner_package_root=owner_root,
        require_authorities=True, build_a=args.build_a, build_b=args.build_b,
    )
    generic_report = generic_validator.validate_package(generic_args)
    a00_manifest, _ = verify_declared_package(path_from(repository_root, f"{A00_ROOT}/manifest.json"), A00_MANIFEST_SHA256)
    o001_manifest, _ = verify_declared_package(path_from(repository_root, f"{O001_ROOT}/manifest.json"), O001_MANIFEST_SHA256)
    tables, spine_report = validate_common_spine(package, path_from(repository_root, A00_ROOT))
    custom_report = validate_custom_sidecars(package, repository_root, owner_root, tables, a00_manifest, o001_manifest)
    report = {
        "schema_id": "program-matematika-indonesia/a00-o001-assessment-adapter-validation/1",
        "status": "PASS",
        "manifest": {"bytes": (package / "manifest.json").stat().st_size, "sha256": sha256_file(package / "manifest.json")},
        "generic_v2_3_1": generic_report,
        "common_spine": spine_report,
        "assessment_capability": custom_report,
    }
    if args.report is not None:
        write_json(args.report.resolve(), report)
    return report


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
        print(compact_json(validate(args)))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
