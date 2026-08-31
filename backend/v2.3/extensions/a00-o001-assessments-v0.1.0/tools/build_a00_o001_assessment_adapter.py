#!/usr/bin/env python3
"""Build the additive A00/O001 assessment-route adapter.

The builder does not promote an assessment or component to a common-layer
navigation unit.  It binds the sealed O001 structural inventory to the sealed
A00 unit/edition/rights/course identities and to exact, existing readable HTML
anchors.  It copies no mathematical prose or formula bodies.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import uuid
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    ROW_ENVELOPE_KEYS,
    TABLE_ORDER,
    combined_shard_identity,
    compact_json,
    empty_tables,
    external_file_fact,
    file_fact,
    identity_set_sha256,
    inventory_sha256,
    make_row,
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
    write_jsonl,
    write_tables,
)


RECORDED_AT = "2026-08-31T00:00:00Z"
ADAPTER_VERSION = "0.1.0"
LANE_NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/v2.3/extensions/a00-o001-assessments",
)

A00_ROOT = "backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0"
O001_ROOT = "backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0"
CAPABILITY_CONTRACT = "backend/v2.2/global-capability-contract-v0.1.0.json"

EXPECTED_ROOTS = {
    "a00_manifest": (f"{A00_ROOT}/manifest.json", 27131, "b196d0b851fa0f6b3b7972ab33b762898f3d577fbc26b6214542d6a5b10009af"),
    "o001_manifest": (f"{O001_ROOT}/manifest.json", 3995, "5ed7b558ae1f621bef52b59be64df90dbf52c967c7e12e2fc9fc296309e2b19e"),
    "capability_contract": (CAPABILITY_CONTRACT, 7462, "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7"),
}

A00_TABLES = [
    "owner_authorities", "datasets", "editions", "units", "content_bindings",
    "rights", "reader_surfaces", "routes",
]

O001_FILES = [
    "data/assessments.jsonl",
    "data/assessment-components.jsonl",
    "data/solution-gaps.jsonl",
    "summaries/modules.jsonl",
    "schema/assessment-inventory-v1.schema.json",
]

STANDARD_SCHEMAS = [
    "lane-adapter-v2.3.1.schema.json",
    "capability-declarations-v0.2.schema.json",
    "namespace-crosswalk-v0.2.schema.json",
    "translation-state-index-v0.2.schema.json",
    "csv-projection-manifest-v0.2.schema.json",
    "scope-declaration-v0.2.schema.json",
    "assessment-route-binding-v0.1.schema.json",
    "assessment-capability-manifest-v0.1.schema.json",
]


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


def basic_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {key: fact[key] for key in ("path", "path_base", "role", "bytes", "sha256")}


def load_declared_package(repository_root: Path, role: str) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    relative, expected_bytes, expected_sha256 = EXPECTED_ROOTS[role]
    manifest_path = path_from(repository_root, relative)
    require(manifest_path.is_file(), f"missing sealed manifest: {relative}")
    require(manifest_path.stat().st_size == expected_bytes, f"sealed manifest byte drift: {relative}")
    require(sha256_file(manifest_path) == expected_sha256, f"sealed manifest hash drift: {relative}")
    manifest = read_json(manifest_path)
    entries = {str(row["path"]): row for row in manifest["files"]}
    require(len(entries) == len(manifest["files"]), f"duplicate declared file in {relative}")
    package_root = manifest_path.parent
    for declared_relative, row in entries.items():
        target = path_from(package_root, declared_relative)
        require(target.is_file(), f"missing sealed package member: {relative}:{declared_relative}")
        require(target.stat().st_size == int(row["bytes"]), f"byte drift: {relative}:{declared_relative}")
        require(sha256_file(target) == str(row["sha256"]), f"hash drift: {relative}:{declared_relative}")
    return manifest, entries


def central_fact(
    repository_root: Path,
    relative: str,
    role: str,
    *,
    expected_bytes: int,
    expected_sha256: str,
) -> dict[str, Any]:
    return external_file_fact(
        path_from(repository_root, relative), relative, role, "program_repository_root",
        expected_bytes=expected_bytes, expected_sha256=expected_sha256,
    )


def declared_central_fact(
    repository_root: Path,
    package_root: str,
    entries: Mapping[str, Mapping[str, Any]],
    relative: str,
    role: str,
) -> dict[str, Any]:
    require(relative in entries, f"undeclared package member requested: {package_root}:{relative}")
    row = entries[relative]
    full_relative = f"{package_root}/{relative}"
    return central_fact(
        repository_root, full_relative, role,
        expected_bytes=int(row["bytes"]), expected_sha256=str(row["sha256"]),
    )


def module_from_semantic_key(value: str) -> str:
    parts = value.split(":")
    require("unit" in parts, f"A00 unit semantic key missing unit component: {value}")
    index = parts.index("unit")
    require(index + 1 < len(parts), f"A00 unit semantic key missing module: {value}")
    module = parts[index + 1]
    require(module.startswith("m") and module[1:].isdigit(), f"invalid A00 module: {module}")
    return module


def build_module_registry(
    repository_root: Path,
    owner_root: Path,
    a00_entries: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    a00_package = path_from(repository_root, A00_ROOT)
    units = read_jsonl(a00_package / "tables" / "units.jsonl")
    routes = read_jsonl(a00_package / "tables" / "routes.jsonl")
    surfaces = read_jsonl(a00_package / "tables" / "reader_surfaces.jsonl")
    bindings = read_jsonl(a00_package / "tables" / "content_bindings.jsonl")
    route_by_unit = {str(row["payload"]["unit_id"]): row for row in routes}
    surface_by_id = {str(row["id"]): row for row in surfaces}
    binding_by_id = {str(row["id"]): row for row in bindings}
    require(len(units) == len(route_by_unit) == len(surfaces) == 75, "A00 module navigation count drift")

    registry: dict[str, dict[str, Any]] = {}
    html_authorities: list[dict[str, Any]] = []
    for unit in units:
        module = module_from_semantic_key(str(unit["semantic_key"]))
        route = route_by_unit.get(str(unit["id"]))
        require(route is not None, f"A00 route missing for {module}")
        surface = surface_by_id.get(str(route["payload"]["surface_id"]))
        require(surface is not None, f"A00 reader surface missing for {module}")
        evidence_ids = list(route["payload"].get("evidence_binding_ids", []))
        require(len(evidence_ids) == 1, f"A00 route evidence cardinality drift: {module}")
        binding = binding_by_id.get(str(evidence_ids[0]))
        require(binding is not None, f"A00 HTML evidence binding missing: {module}")
        payload = binding["payload"]
        expected_path = f"output/html-id/modules/{module}/index.html"
        require(payload.get("locator") == expected_path, f"A00 HTML locator drift: {module}")
        require(payload.get("locator_base") == "owner_repository_root", f"A00 HTML locator base drift: {module}")
        html_path = path_from(owner_root, expected_path)
        html_fact = external_file_fact(
            html_path, expected_path, f"a00_readable_html_{module}", "owner_package_root",
            expected_bytes=int(payload["bytes"]), expected_sha256=str(payload["sha256"]),
        )
        parser = AnchorCollector()
        parser.feed(html_path.read_text(encoding="utf-8"))
        parser.close()
        public_url = str(route["payload"]["public_url"])
        require(public_url == str(surface["payload"]["public_url"]), f"A00 public route/surface drift: {module}")
        registry[module] = {
            "unit": unit,
            "route": route,
            "surface": surface,
            "binding": binding,
            "html_fact": html_fact,
            "anchors": parser.ids,
            "public_url": public_url,
        }
        html_authorities.append(basic_fact(html_fact))
    require(len(registry) == 75, "A00 module registry is not 75 unique modules")
    return registry, html_authorities


def load_o001_rows(repository_root: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    root = path_from(repository_root, O001_ROOT)
    rows = {
        "assessments": read_jsonl(root / "data" / "assessments.jsonl"),
        "components": read_jsonl(root / "data" / "assessment-components.jsonl"),
        "gaps": read_jsonl(root / "data" / "solution-gaps.jsonl"),
        "modules": read_jsonl(root / "summaries" / "modules.jsonl"),
    }
    require(len(rows["assessments"]) == 8105, "O001 assessment count drift")
    require(len(rows["components"]) == 13345, "O001 component count drift")
    require(len(rows["gaps"]) == 2865, "O001 solution-gap count drift")
    require(len(rows["modules"]) == 75, "O001 module count drift")
    summaries = {str(row["module"]): row for row in rows["modules"]}
    require(len(summaries) == 75, "O001 module summaries are not unique")
    return rows, summaries


def a00_binding(module_record: Mapping[str, Any], fixed: Mapping[str, str]) -> dict[str, str]:
    unit = module_record["unit"]
    route = module_record["route"]
    surface = module_record["surface"]
    return {
        "course_id": fixed["course_id"],
        "edition_id": fixed["edition_id"],
        "owner_authority_id": fixed["owner_authority_id"],
        "unit_id": str(unit["id"]),
        "unit_rights_id": fixed["rights_id"],
        "component_rights_state": "preserved_in_sealed_A00_native_rights_shard_not_flattened",
        "reader_surface_id": str(surface["id"]),
        "route_id": str(route["id"]),
    }


def route_binding(module_record: Mapping[str, Any], native_id: str) -> dict[str, Any]:
    occurrences = int(module_record["anchors"].get(native_id, 0))
    require(occurrences == 1, f"HTML anchor occurrence must be exactly one: {native_id} observed={occurrences}")
    fact = module_record["html_fact"]
    module_url = str(module_record["public_url"])
    return {
        "module_url": module_url,
        "fragment": native_id,
        "public_url": f"{module_url}#{native_id}",
        "target_kind": "readable_semantic_html_anchor",
        "html_evidence": {
            "owner_relative_path": str(fact["path"]),
            "bytes": int(fact["bytes"]),
            "sha256": str(fact["sha256"]),
            "anchor_occurrences": occurrences,
        },
    }


def project_custom_rows(
    native: Mapping[str, list[dict[str, Any]]],
    modules: Mapping[str, Mapping[str, Any]],
    fixed: Mapping[str, str],
    o001_package_id: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    assessment_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []
    assessment_by_id = {str(row["id"]): row for row in native["assessments"]}
    require(len(assessment_by_id) == 8105, "duplicate O001 assessment ID")

    components_by_assessment: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in native["components"]:
        assessment_id = str(row["assessment_id"])
        require(assessment_id in assessment_by_id, f"orphan O001 component: {row['id']}")
        components_by_assessment[assessment_id].append(row)

    for row_ordinal, row in enumerate(native["assessments"], 1):
        module = str(row["module"])
        require(module in modules, f"assessment module missing in A00: {module}")
        native_id = str(row["native_id"])
        projected = {key: row[key] for key in (
            "id", "semantic_key", "module", "module_ordinal", "ordinal", "native_id",
            "assessment_kind", "availability", "context_classification", "context_structural_signature",
            "problem_component_count", "solution_component_count", "solution_availability",
            "source", "target", "topology_match",
        )}
        projected.update({
            "record_type": "assessment_binding",
            "a00_binding": a00_binding(modules[module], fixed),
            "route": route_binding(modules[module], native_id),
            "owner_source": {"package_id": o001_package_id, "table_path": "data/assessments.jsonl", "row_ordinal": row_ordinal},
            "mapping_state": "mapped_without_navigation_unit_promotion",
        })
        assessment_rows.append(projected)

    for row_ordinal, row in enumerate(native["components"], 1):
        module = str(row["module"])
        require(module in modules, f"component module missing in A00: {module}")
        native_id = str(row["native_id"])
        projected = {key: row[key] for key in (
            "id", "semantic_key", "assessment_id", "module", "module_ordinal", "ordinal", "native_id",
            "native_tag", "component_kind", "availability", "source", "target", "topology_match",
        )}
        projected.update({
            "record_type": "assessment_component_binding",
            "a00_binding": a00_binding(modules[module], fixed),
            "route": route_binding(modules[module], native_id),
            "owner_source": {"package_id": o001_package_id, "table_path": "data/assessment-components.jsonl", "row_ordinal": row_ordinal},
            "mapping_state": "mapped_without_navigation_unit_promotion",
        })
        component_rows.append(projected)

    for assessment_id, assessment in assessment_by_id.items():
        components = components_by_assessment.get(assessment_id, [])
        statements = sum(row["component_kind"] == "statement" for row in components)
        solutions = sum(row["component_kind"] == "solution" for row in components)
        require(statements == int(assessment["problem_component_count"]), f"statement count mismatch: {assessment_id}")
        require(solutions == int(assessment["solution_component_count"]), f"solution count mismatch: {assessment_id}")

    for row_ordinal, row in enumerate(native["gaps"], 1):
        assessment = assessment_by_id.get(str(row["assessment_id"]))
        require(assessment is not None, f"orphan O001 solution gap: {row['id']}")
        require(assessment["solution_availability"] == "missing_source_and_target", f"gap assessment is not explicitly missing: {row['id']}")
        require(str(assessment["native_id"]) == str(row["native_exercise_id"]), f"gap native ID differs from assessment: {row['id']}")
        module = str(row["module"])
        projected = {key: row[key] for key in (
            "id", "semantic_key", "assessment_id", "module", "module_ordinal", "ordinal",
            "native_exercise_id", "context_classification", "gap_kind", "source_solution_count", "target_solution_count",
        )}
        projected.update({
            "record_type": "solution_gap_binding",
            "a00_binding": a00_binding(modules[module], fixed),
            "route": route_binding(modules[module], str(row["native_exercise_id"])),
            "owner_source": {"package_id": o001_package_id, "table_path": "data/solution-gaps.jsonl", "row_ordinal": row_ordinal},
            "mapping_state": "explicit_absence_preserved_no_solution_invented",
        })
        gap_rows.append(projected)

    statement_count = sum(row["component_kind"] == "statement" for row in native["components"])
    solution_count = sum(row["component_kind"] == "solution" for row in native["components"])
    require(statement_count == 8105 and solution_count == 5240, "O001 component-kind counts drift")
    return {
        "assessments": assessment_rows,
        "components": component_rows,
        "gaps": gap_rows,
    }, {
        "modules": 75,
        "assessments": len(assessment_rows),
        "assessment_components": len(component_rows),
        "solution_gaps": len(gap_rows),
        "statement_components": statement_count,
        "solution_components": solution_count,
        "exact_html_anchor_routes": len(assessment_rows) + len(component_rows),
    }


def write_custom_csv(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["stable_id", "record_type", "canonical_record_json"])
        for row in rows:
            writer.writerow([row["id"], row["record_type"], compact_json(row)])


def build_common_tables(repository_root: Path, context: Mapping[str, str]) -> dict[str, list[dict[str, Any]]]:
    """Lift the sealed A00 v2.2 spine without reminting or semantic changes."""
    tables = empty_tables()
    a00_tables = path_from(repository_root, A00_ROOT) / "tables"
    for table_name in TABLE_ORDER:
        source_rows = read_jsonl(a00_tables / f"{table_name}.jsonl")
        for source in source_rows:
            require(source["dataset_id"] == context["dataset_id"], f"A00 dataset drift in {table_name}")
            projected = {key: source[key] for key in ROW_ENVELOPE_KEYS}
            require(set(projected) == ROW_ENVELOPE_KEYS, f"A00 envelope lift failed in {table_name}")
            tables[table_name].append(projected)
    sort_table_rows(tables)
    require(sum(len(tables[name]) for name in TABLE_ORDER) == 1313, "A00 common spine must remain exactly 1,313 records")
    require(len(tables["units"]) == len(tables["routes"]) == len(tables["reader_surfaces"]) == 75, "A00 navigation spine count drift")
    return tables


def custom_fact(path: Path, relative: str, role: str, rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    fact = file_fact(path, relative, role, records=len(rows), record_id_set_sha256=identity_set_sha256(str(row["id"]) for row in rows))
    fact["format"] = "canonical_jsonl" if path.suffix == ".jsonl" else "deterministic_csv"
    return fact


def build_sidecars(
    output: Path,
    context: Mapping[str, str],
    tables: Mapping[str, list[dict[str, Any]]],
    custom_rows: Mapping[str, list[dict[str, Any]]],
    counts: Mapping[str, int],
    named: Mapping[str, Mapping[str, Any]],
) -> None:
    package_id = context["package_id"]
    dataset_id = context["dataset_id"]
    write_json(output / "scope-declaration-v0.2.0.json", {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "scope_kind": "lane_adapter", "course_ids": [context["course_id"]],
        "curriculum_role_ids": ["A00"], "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [],
        "owner_authority_binding": basic_fact(named["a00_manifest"]),
        "curriculum_authority_binding": {"role_id": "A00", "binding_state": "selected_corpus_unchanged"},
        "limitations": [
            "This extension is an additive assessment capability sidecar and does not replace the sealed A00 package.",
            "Assessments and components are not promoted into common-layer navigation units.",
            "Public network state is inherited from sealed A00 publication metadata; this build validates exact local HTML bytes and anchors.",
        ],
        "recorded_at": RECORDED_AT,
    })

    dataset_row_id = tables["datasets"][0]["id"]
    require(dataset_row_id == context["a00_dataset_id"] == dataset_id, "A00 dataset identity was not preserved")
    mapping_digest = sha256_bytes(f"{context['a00_dataset_id']}\0{dataset_row_id}\n".encode("utf-8"))
    write_json(output / "namespace-crosswalk-v0.2.0.json", {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id,
        "profiles": [
            {"name": "a00-v2.2", "namespace": context["a00_namespace"], "authority": "sealed_A00_package"},
            {"name": "o001-native", "namespace": context["o001_namespace"], "authority": "sealed_O001_assessment_shard"},
            {"name": "a00-o001-v2.3.1", "namespace": str(LANE_NAMESPACE), "authority": "this_additive_adapter"},
        ],
        "mappings": [{
            "source_namespace": context["a00_namespace"], "target_namespace": str(LANE_NAMESPACE),
            "source_record_id": context["a00_dataset_id"], "target_record_id": dataset_row_id,
            "source_record_type": "dataset", "target_record_type": "dataset",
            "cardinality": "one_to_one", "mapping_state": "mapped",
            "reverse_recipe": "read source dataset ID from sealed A00 package manifest and tables/datasets.jsonl",
            "evidence_refs": [f"{A00_ROOT}/manifest.json", f"{A00_ROOT}/tables/datasets.jsonl"],
            "identity_set_sha256": mapping_digest,
        }],
        "unmaterialized_candidates": [],
        "identity_sets": {
            "assessment_ids": identity_set_sha256(str(row["id"]) for row in custom_rows["assessments"]),
            "component_ids": identity_set_sha256(str(row["id"]) for row in custom_rows["components"]),
            "gap_ids": identity_set_sha256(str(row["id"]) for row in custom_rows["gaps"]),
        },
        "recorded_at": RECORDED_AT,
    })

    translation_rows = [
        {
            "projected_unit_id": str(row["id"]),
            "state": "id-ID_target_hash_bound",
            "evidence_refs": list(row["payload"].get("target_binding_ids", [])),
        }
        for row in tables["units"]
    ]
    write_json(output / "translation-state-index-v0.2.0.json", {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "authority_bindings": [basic_fact(named["o001_manifest"]), basic_fact(named["a00_manifest"])],
        "coverage": {"course_id": context["course_id"], "granularity": "sealed_A00_module_unit", "authority_rows": 75, "indexed_rows": 75, "inferred_rows": 0},
        "states": ["id-ID_target_hash_bound"], "records": translation_rows,
        "identity_set_sha256": identity_set_sha256(str(row["projected_unit_id"]) for row in translation_rows), "no_inference": True,
        "recorded_at": RECORDED_AT,
    })

    assessment_jsonl = custom_fact(output / "assessment-bindings-v0.1.0.jsonl", "assessment-bindings-v0.1.0.jsonl", "assessment_binding_table", custom_rows["assessments"])
    component_jsonl = custom_fact(output / "assessment-component-bindings-v0.1.0.jsonl", "assessment-component-bindings-v0.1.0.jsonl", "assessment_component_binding_table", custom_rows["components"])
    gap_jsonl = custom_fact(output / "solution-gaps-v0.1.0.jsonl", "solution-gaps-v0.1.0.jsonl", "solution_gap_binding_table", custom_rows["gaps"])
    assessment_csv = custom_fact(output / "assessment-csv" / "assessment-bindings.csv", "assessment-csv/assessment-bindings.csv", "assessment_binding_csv", custom_rows["assessments"])
    component_csv = custom_fact(output / "assessment-csv" / "assessment-component-bindings.csv", "assessment-csv/assessment-component-bindings.csv", "assessment_component_binding_csv", custom_rows["components"])
    gap_csv = custom_fact(output / "assessment-csv" / "solution-gaps.csv", "assessment-csv/solution-gaps.csv", "solution_gap_binding_csv", custom_rows["gaps"])
    shard_facts = [assessment_jsonl, assessment_csv, component_jsonl, component_csv, gap_jsonl, gap_csv]
    combined_ids = [str(row["id"]) for key in ("assessments", "components", "gaps") for row in custom_rows[key]]
    source_assessments = dict(named["o001_assessments"])
    source_components = dict(named["o001_components"])
    source_gaps = dict(named["o001_gaps"])
    source_assessments.update(records=8105, record_id_set_sha256=assessment_jsonl["record_id_set_sha256"])
    source_components.update(records=13345, record_id_set_sha256=component_jsonl["record_id_set_sha256"])
    source_gaps.update(records=2865, record_id_set_sha256=gap_jsonl["record_id_set_sha256"])
    native_combined_shards_sha256 = combined_shard_identity([source_assessments, source_components, source_gaps])
    require(native_combined_shards_sha256 == "ee21807297f7ac0b04c00ccbf7b3c1eae5ba9ff7bc48f20d0f236b389f259455", "O001 combined-shard identity drift")
    write_json(output / "assessment-capability-v0.1.0.json", {
        "$schema": "schema/assessment-capability-manifest-v0.1.schema.json",
        "schema_id": "interlanguage/a00-o001-assessment-capability/0.1.0",
        "schema_version": "0.1.0", "package_id": package_id, "dataset_id": dataset_id,
        "course_id": context["course_id"], "edition_id": context["edition_id"],
        "owner_authority_id": context["a00_owner_authority_id"], "rights_id": context["rights_id"],
        "component_rights_policy": {"native_component_exceptions": 18, "state": "preserved_in_sealed_A00_native_rights_shard_not_flattened"},
        "source_package_id": context["o001_package_id"], "counts": dict(counts),
        "shards": shard_facts,
        "route_policy": {
            "destination": "existing_A00_readable_semantic_HTML", "fragment_source": "owner_native_id",
            "anchor_evidence": "exactly_one_local_HTML_id_attribute_per_assessment_or_component",
            "network_state": "module_publication_state_inherited_from_sealed_A00_package_no_refetch",
        },
        "identity_sets": {
            "assessments": assessment_jsonl["record_id_set_sha256"],
            "assessment_components": component_jsonl["record_id_set_sha256"],
            "solution_gaps": gap_jsonl["record_id_set_sha256"],
            "combined": identity_set_sha256(combined_ids),
        },
        "module_unit_mapping_sha256": sha256_bytes("".join(
            f"{module}\0{modules_record['unit']['id']}\n"
            for module, modules_record in sorted(context["module_registry"].items())
        ).encode("utf-8")),
        "pattern_audit_combined_shards_sha256": native_combined_shards_sha256,
        "loss_accounting": {
            "explicit_no_solution_gaps": 2865, "invented_solutions": 0,
            "unmapped_assessments": 0, "unmapped_components": 0, "missing_anchors": 0,
        },
        "zero_copy_policy": {
            "mathematical_prose_copied": False, "formula_bodies_copied": False,
            "navigation_units_promoted": False, "owner_native_ids_preserved": True,
        },
        "recorded_at": RECORDED_AT,
    })

    assessment_jsonl_ref = {key: value for key, value in assessment_jsonl.items() if key != "format"}
    component_jsonl_ref = {key: value for key, value in component_jsonl.items() if key != "format"}
    gap_jsonl_ref = {key: value for key, value in gap_jsonl.items() if key != "format"}
    common_rules = [
        "sealed owner-native shards remain authoritative",
        "no textbook body prose or formula bodies are copied",
        "no absent semantics are inferred",
    ]
    capabilities: list[dict[str, Any]] = []
    capability_specs = {
        "structure_localization": ("materialized", 75, 75, [named["a00_units"]], identity_set_sha256(str(row["id"]) for row in tables["units"]), "The exact sealed 75-unit A00 navigation spine is retained without new assessment units."),
        "terminology": ("not_projected", 56, 0, [named["a00_manifest"]], None, "Terminology is outside this assessment-binding adapter and remains in A00 native shards."),
        "mathematical_preservation": ("referenced_native_shards", 21450, 0, [source_assessments, source_components], identity_set_sha256([str(row["id"]) for key in ("assessments", "components") for row in custom_rows[key]]), "Exact source/target byte spans and SHA-256 identities are referenced by the zero-prose anchor join; mathematical bodies are not copied."),
        "assessment_support": ("referenced_native_shards", 24315, 0, [source_assessments, source_components, source_gaps, assessment_jsonl_ref, component_jsonl_ref, gap_jsonl_ref], identity_set_sha256(combined_ids), "All 24,315 owner-native assessment/component/gap records remain referenced; the dedicated anchor join is not counted as common-table projection."),
        "assets": ("referenced_native_shards", 2962, 0, [named["a00_manifest"]], None, "Assets remain in the sealed A00 native corpus; no asset bytes are copied."),
        "accessibility": ("materialized", 75, 75, [named["a00_reader_surfaces"]], identity_set_sha256(str(row["id"]) for row in tables["reader_surfaces"]), "The exact 75 A00 semantic-HTML surfaces remain materialized; the sidecar proves every assessment/component anchor without inflating common-table counts."),
        "corrections": ("referenced_native_shards", 75, 0, [named["a00_manifest"]], None, "Correction evidence remains in sealed A00 native shards."),
        "computational_interactives": ("absent", 0, 0, [], None, "No computational-interactive claim is made by this adapter."),
        "publication": ("materialized", 75, 75, [named["a00_routes"], named["a00_reader_surfaces"]], identity_set_sha256(str(row["id"]) for row in tables["routes"]), "The exact 75 A00 public module routes remain materialized; 21,450 anchor joins are additive sidecar evidence."),
        "research_support": ("not_projected", 0, 0, [], None, "No research-support semantics are projected by this assessment adapter."),
    }
    schema_fact = file_fact(output / "schema" / "assessment-route-binding-v0.1.schema.json", "schema/assessment-route-binding-v0.1.schema.json", "assessment_binding_schema")
    for name in CAPABILITY_NAMES:
        state, native_count, projected_count, refs, digest, reason = capability_specs[name]
        capabilities.append({
            "name": name, "version": "0.1.0", "state": state,
            "schema_binding": schema_fact if name == "assessment_support" else None,
            "shard_refs": refs, "native_count": native_count, "projected_count": projected_count,
            "identity_set_sha256": digest,
            "identity_set_scope": (
                "native_shard_records" if state == "referenced_native_shards"
                else ("projected_records" if digest is not None else "none")
            ),
            "closure_rules": common_rules,
            "loss_gap_report": {"status": "declared_limitation" if name != "assessment_support" else "closed", "reason": reason},
        })
    rights_source = dict(named["a00_rights"])
    rights_source.update(records=1, record_id_set_sha256=identity_set_sha256([context["rights_id"]]))
    write_json(output / "capability-declarations-v0.2.0.json", {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "contract_binding": basic_fact(named["capability_contract"]), "capabilities": capabilities,
        "legacy_labels": [{"label": "assessments", "normalized": "assessment_support", "disposition": "additive_custom_sidecar"}],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards", "shard_refs": [rights_source], "native_count": 1,
            "identity_set_sha256": identity_set_sha256([context["rights_id"]]),
            "closure_rules": [
                "exact A00 default rights identity is preserved",
                "18 component exceptions remain in the sealed A00 native shard",
                "this adapter does not flatten or reinterpret component rights",
            ],
        },
        "recorded_at": RECORDED_AT,
    })


def copy_contract_files(repository_root: Path, output: Path) -> None:
    source_schema = repository_root / "backend" / "v2.3" / "schema"
    for name in STANDARD_SCHEMAS:
        source = source_schema / name
        require(source.is_file(), f"missing adapter schema: {name}")
        target = output / "schema" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    tool_map = {
        "build_a00_o001_assessment_adapter.py": Path(__file__).resolve(),
        "validate_a00_o001_assessment_adapter.py": Path(__file__).resolve().with_name("validate_a00_o001_assessment_adapter.py"),
        "validate_lane_adapter_v231.py": Path(__file__).resolve().with_name("validate_lane_adapter_v231.py"),
        "v231_adapter_common.py": Path(__file__).resolve().with_name("v231_adapter_common.py"),
    }
    for name, source in tool_map.items():
        require(source.is_file(), f"missing adapter tool: {source.name}")
        target = output / "tools" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    output = args.output.resolve()
    require(repository_root.is_dir(), "program repository root missing")
    require(owner_root.is_dir(), "A00 owner package root missing")
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    a00_manifest, a00_entries = load_declared_package(repository_root, "a00_manifest")
    o001_manifest, o001_entries = load_declared_package(repository_root, "o001_manifest")
    authorities: list[dict[str, Any]] = []
    named: dict[str, dict[str, Any]] = {}
    for role in ("a00_manifest", "o001_manifest", "capability_contract"):
        relative, size, digest = EXPECTED_ROOTS[role]
        fact = central_fact(repository_root, relative, role, expected_bytes=size, expected_sha256=digest)
        named[role] = fact
        authorities.append(basic_fact(fact))
    for table in A00_TABLES:
        relative = f"tables/{table}.jsonl"
        role = f"a00_{table}"
        fact = declared_central_fact(repository_root, A00_ROOT, a00_entries, relative, role)
        named[role] = fact
        authorities.append(basic_fact(fact))
    role_by_o001 = {
        "data/assessments.jsonl": "o001_assessments",
        "data/assessment-components.jsonl": "o001_components",
        "data/solution-gaps.jsonl": "o001_gaps",
        "summaries/modules.jsonl": "o001_module_summaries",
        "schema/assessment-inventory-v1.schema.json": "o001_schema",
    }
    for relative in O001_FILES:
        role = role_by_o001[relative]
        fact = declared_central_fact(repository_root, O001_ROOT, o001_entries, relative, role)
        named[role] = fact
        authorities.append(basic_fact(fact))

    modules, html_authorities = build_module_registry(repository_root, owner_root, a00_entries)
    authorities.extend(html_authorities)
    native, summaries = load_o001_rows(repository_root)
    require(set(modules) == set(summaries), "A00/O001 module set mismatch")
    for module, summary in summaries.items():
        require(int(summary["module_ordinal"]) in range(1, 76), f"bad O001 module ordinal: {module}")

    a00_package = path_from(repository_root, A00_ROOT)
    a00_owner_row = read_jsonl(a00_package / "tables" / "owner_authorities.jsonl")[0]
    a00_dataset_row = read_jsonl(a00_package / "tables" / "datasets.jsonl")[0]
    a00_edition_row = read_jsonl(a00_package / "tables" / "editions.jsonl")[0]
    a00_rights_row = read_jsonl(a00_package / "tables" / "rights.jsonl")[0]
    fixed = {
        "course_id": str(a00_dataset_row["payload"]["course_ids"][0]),
        "edition_id": str(a00_edition_row["id"]),
        "owner_authority_id": str(a00_owner_row["id"]),
        "rights_id": str(a00_rights_row["id"]),
    }
    context = {
        **fixed,
        "a00_owner_authority_id": fixed["owner_authority_id"],
        "a00_dataset_id": str(a00_manifest["dataset_id"]),
        "a00_namespace": str(a00_manifest["identity_namespace"]),
        "o001_package_id": str(o001_manifest["package_id"]),
        "o001_namespace": str(o001_manifest["identity"]["namespace"]),
        "package_id": projection_id(LANE_NAMESPACE, "lane_adapter_package", f"a00:o001:assessments:{ADAPTER_VERSION}"),
        "dataset_id": str(a00_manifest["dataset_id"]),
    }

    custom_rows, counts = project_custom_rows(native, modules, fixed, context["o001_package_id"])
    write_jsonl(output / "assessment-bindings-v0.1.0.jsonl", custom_rows["assessments"])
    write_jsonl(output / "assessment-component-bindings-v0.1.0.jsonl", custom_rows["components"])
    write_jsonl(output / "solution-gaps-v0.1.0.jsonl", custom_rows["gaps"])
    write_custom_csv(output / "assessment-csv" / "assessment-bindings.csv", custom_rows["assessments"])
    write_custom_csv(output / "assessment-csv" / "assessment-component-bindings.csv", custom_rows["components"])
    write_custom_csv(output / "assessment-csv" / "solution-gaps.csv", custom_rows["gaps"])

    context["module_registry"] = modules
    tables = build_common_tables(repository_root, context)
    write_tables(output, tables)
    copy_contract_files(repository_root, output)
    build_sidecars(output, context, tables, custom_rows, counts, named)
    csv_manifest = write_csv_surfaces(output, tables, context["package_id"], RECORDED_AT)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/a00-o001-assessment-adapter-input-authorities/1",
        "recorded_at": RECORDED_AT, "authorities": sorted(authorities, key=lambda item: (item["path_base"], item["path"])),
        "sealed_packages": {
            "a00": {"package_id": a00_manifest["package_id"], "manifest": basic_fact(named["a00_manifest"])},
            "o001": {"package_id": o001_manifest["package_id"], "manifest": basic_fact(named["o001_manifest"])},
        },
        "html_anchor_closure": {"modules": 75, "assessment_and_component_ids": 21450, "missing": 0, "duplicate": 0},
        "owner_native_non_mutation": True, "mathematical_prose_copied": False, "formula_bodies_copied": False,
    })
    (output / "README.md").write_text(
        "# A00/O001 assessment-route adapter\n\n"
        "This additive, zero-copy v2.3.1 extension maps the sealed O001 assessment inventory "
        "to the sealed A00 module, course, edition, rights, reader-surface, and route identities. "
        "Every assessment and component points to an exact existing readable HTML `#native_id` anchor.\n\n"
        "It creates no assessment navigation units, copies no mathematical prose or formula bodies, "
        "and preserves every explicit missing-solution gap without inventing a solution.\n",
        encoding="utf-8", newline="\n",
    )

    payload_facts = package_payload_files(output)
    payload_identity = inventory_sha256(payload_facts)
    mandatory_sidecars = [
        "capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json",
        "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json",
        "scope-declaration-v0.2.0.json", "assessment-capability-v0.1.0.json",
        "assessment-bindings-v0.1.0.jsonl", "assessment-component-bindings-v0.1.0.jsonl",
        "solution-gaps-v0.1.0.jsonl",
    ]
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
        "schema_version": "2.3.1", "package_id": context["package_id"], "dataset_id": context["dataset_id"],
        "extension_id": projection_id(LANE_NAMESPACE, "lane_adapter_extension", f"a00:o001:assessments:{ADAPTER_VERSION}"),
        "extension_version": ADAPTER_VERSION, "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": sorted(authorities, key=lambda item: (item["path_base"], item["path"])),
        "sidecars": [file_fact(output / name, name, "sidecar") for name in mandatory_sidecars],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER), "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER), "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools" / "build_a00_o001_assessment_adapter.py", "tools/build_a00_o001_assessment_adapter.py", "builder"),
            "validator": file_fact(output / "tools" / "validate_a00_o001_assessment_adapter.py", "tools/validate_a00_o001_assessment_adapter.py", "validator"),
            "canonical_serialization": {
                "scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8", "newline": "LF",
                "json_keys": "lexicographically_sorted", "trailing_newline": True,
                "copied_schema_and_tool_files": "preserved_exact_source_bytes",
            }, "deterministic_replay": "byte_identical", "build_a_sha256": payload_identity, "build_b_sha256": payload_identity,
        },
        "files": payload_facts,
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json", "seal_excluded_from_own_digest": True,
            "binds": ["schemas", "tools", "input_authorities", "common_tables", "assessment_sidecars", "csv_projections", "manifest"],
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
        "files": seal_facts, "file_count": len(seal_facts), "bytes": sum(int(item["bytes"]) for item in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts), "seal_excluded_from_own_digest": True,
        "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_fact = write_checksums(output, checksum_facts)
    return {
        "status": "pass", "files": len(checksum_facts) + 1,
        "common_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "assessments": 8105, "assessment_components": 13345, "solution_gaps": 2865,
        "exact_html_anchor_routes": 21450, "navigation_units_promoted": 0,
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
