#!/usr/bin/env python3
"""Build the metadata-only D70 learner/educator capability adapter."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

from d70_capability_model_v1 import (
    BUNDLE_FILES,
    CENTRAL_CAPSULE_RECORD,
    CENTRAL_COVERAGE_RECORD,
    COURSE_ID,
    EXPECTED_COUNTS,
    EXPECTED_LI_ORDERS,
    NEGATIVE_CASES,
    PUBLIC_DOWNLOAD_BASE,
    PUBLIC_FILES,
    PUBLIC_RECORD,
    ROUTE_ROOT_MAP,
    SHARED_SCHEMA,
    SOURCE_CATALOG,
    canonical_json_compact,
    file_identity,
    read_json,
    sha256_bytes,
    tree_identity,
    validate_bundle,
    write_bytes,
    write_json,
    write_jsonl,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER_REL = Path("backend/course-capsule-v1/adapters/d70-capability-v1")
DEFAULT_ADAPTER = PROJECT / ADAPTER_REL
DEFAULT_NATIVE = PROJECT.parent / "metode-aljabar-jilid-1-id"
FROZEN_CAPSULE_REL = Path("input/pre-admission-course-capsule-D70.json")
FROZEN_COVERAGE_REL = Path("input/pre-admission-program-coverage-D70.json")
LI_COLLECTION_SHA256 = "409a767a5696d59540a19aa23c1f28e4a25c36660134dd12536b1a81c5ba4a5e"
LI_COLLECTION_BYTES = 7_516_806

EXTRA_INPUTS = (
    ("native_unit_schema", "backend/schema/open-math-corpus-unit.schema.v1.json", 21_358, "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3"),
    ("li_complete_freeze", "qa/LI_COMPLETE_TRANSLATION_FREEZE.json", 12_256, "52d23d06d68a3ea80b9ea691a5537e469dfecae338d21496642ad43142f66252"),
    ("li_complete_admission", "qa/LI_COMPLETE_ADMISSION_20260829.md", 4_270, "92cb39d59e45c470459481098feb73cb4a780cad7fe2cfd9fd5747487b0c4fd7"),
    ("complete_local_boundary", "qa/O013_COMPLETE_LOCAL_BOUNDARY_20260829.json", 4_284, "123a9e72227cfdab0814f2106b3dc81e0341e728bc0cb628934390e8ec1924cd"),
    ("terminology", "00_control/TERMINOLOGY.id-ID.csv", 106_102, "038aaa719c79ad0b775bf57a9a20d8954bd26eb97b1d9c1438a988b0a07b645f"),
    ("rights", "00_control/RIGHTS_COMPONENTS.csv", 2_032, "ba3602b730c0b8a54553c892e426cfa59862c23a9669daf00d2ceca6c8446a3a"),
    ("duncan_component", "repo/components/duncan/backend/duncan-component.json", 3_653_763, "14f74a3fd980e394a67facf54f2800056f753de1d462eb75a98ea5d52af195d5"),
    ("duncan_validation", "repo/components/duncan/backend/duncan-backend-validation.json", 3_060, "88c06fd72bb710585cebd5ec9264ec81c1da34e1e99e9722495451bd1521d3b2"),
    ("cring_component", "repo/components/cring/backend/cring-component.json", 2_195_455, "797e0fc6d56aedae63071f54fdb166fe892477e4614a7862b31de18877d3508b"),
    ("cring_validation", "repo/components/cring/backend/cring-backend-validation.json", 4_272, "7c5c964c734a6f1fce0ebec73d38e33848e56cc984e03b4620c9519d975ad229"),
    ("original_route", "repo/components/original/backend/o013-rute-pembelajar.json", 14_156, "05eb379f4cad172b6b5cb067845718d9b12b6b469a9b6ff71ba18511721461f8"),
    ("original_build_qa", "repo/components/original/qa/ORIGINAL_LAYER_BUILD_QA.json", 2_415, "5b97d574b977fdefaee6d2f92a11e70fda9c8b15cc55f6ed6f88674fe7861362"),
    ("aggregate_manifest", "publication/o013-aggregate-1.0.0/o013-aggregate-manifest.json", 8_406, "3f19fd77fe9b5d54b6efa6b3558f02c704f2e16504315444edcdfc7fd40c089c"),
    ("zenodo_public_readback", "qa/ZENODO_O013_AGGREGATE_1.0.0_METADATA_READBACK_20260829.json", 7_007, "05b08edb62c66d708b02c685f1c1650b3c82ccb853f2ff787c85096fdb0d5a23"),
    ("github_content_readback", "qa/PUBLICATION_GITHUB_O013_COMPLETE_CONTENT_READBACK.json", 40_967, "0de167a1e60451ee792941a0ffc43af00a4d72ed6282c299911256bafae3d594"),
    ("github_terminal_readback", "qa/PUBLICATION_GITHUB_O013_TERMINAL_RECEIPT_READBACK.json", 7_627, "1e139c929c0cba6c00e0c2591ec0ec584b10100390b60a4a2991eeaf12b4272e"),
)


def fail(message: str) -> None:
    raise SystemExit(message)


def json_record_identity(value: Any) -> dict[str, Any]:
    data = canonical_json_compact(value)
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def selected_central_records(project: Path) -> dict[str, Any]:
    capsule_path = project / "backend/course-capsule-v1/generated/course-capsules.jsonl"
    capsules = [json.loads(line) for line in capsule_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    capsule_matches = [x for x in capsules if x.get("course_id") == COURSE_ID]
    if len(capsule_matches) != 1:
        fail(f"D70 central capsule selector cardinality mismatch: {len(capsule_matches)}")
    capsule = capsule_matches[0]
    coverage_container = read_json(project / "backend/course-capsule-v1/generated/program-backend-coverage-v1.json")
    coverage_matches = [x for x in coverage_container.get("roles", []) if x.get("role_id") == COURSE_ID]
    if len(coverage_matches) != 1:
        fail(f"D70 central coverage selector cardinality mismatch: {len(coverage_matches)}")
    coverage = coverage_matches[0]
    capsule_identity = json_record_identity(capsule)
    coverage_identity = json_record_identity(coverage)
    if capsule_identity != CENTRAL_CAPSULE_RECORD:
        fail(f"D70 central capsule drift: {capsule_identity}")
    if coverage_identity != CENTRAL_COVERAGE_RECORD:
        fail(f"D70 central coverage drift: {coverage_identity}")
    schema_identity = file_identity(project / SHARED_SCHEMA["path"])
    if schema_identity != {"bytes": SHARED_SCHEMA["bytes"], "sha256": SHARED_SCHEMA["sha256"]}:
        fail(f"shared capability schema drift: {schema_identity}")
    return {"capsule": capsule, "coverage": coverage}


def li_files(native: Path) -> list[Path]:
    files = sorted((native / "backend/data").glob("*.json"), key=lambda p: p.name)
    if len(files) != 41:
        fail(f"expected 41 Li backend files, found {len(files)}")
    orders = [int(read_json(path)["unit"]["order"]) for path in files]
    if tuple(orders) != EXPECTED_LI_ORDERS:
        fail(f"Li order mismatch: {orders}")
    return files


def li_collection_identity(native: Path) -> dict[str, Any]:
    rows = []
    total = 0
    for path in li_files(native):
        identity = file_identity(path)
        relative = path.relative_to(native).as_posix()
        total += identity["bytes"]
        rows.append(f"{relative}|{identity['bytes']}|{identity['sha256']}\n")
    digest = sha256_bytes("".join(rows).encode("utf-8"))
    value = {"files": 41, "bytes": total, "sha256": digest, "serialization": "path|bytes|lowercase-sha256\\n; sorted paths"}
    if value["bytes"] != LI_COLLECTION_BYTES or value["sha256"] != LI_COLLECTION_SHA256:
        fail(f"Li collection identity mismatch: {value}")
    return value


def initialize_lock(native: Path, output: Path, project: Path) -> Path:
    lock_path = output / "input/source-lock.json"
    if lock_path.exists():
        fail(f"refusing to overwrite existing source lock: {lock_path}")
    central = selected_central_records(project)
    frozen_records = {
        "capsule": (FROZEN_CAPSULE_REL, central["capsule"], CENTRAL_CAPSULE_RECORD),
        "coverage": (FROZEN_COVERAGE_REL, central["coverage"], CENTRAL_COVERAGE_RECORD),
    }
    for _, (relative, value, expected_identity) in frozen_records.items():
        destination = output / relative
        data = canonical_json_compact(value)
        if {"bytes": len(data), "sha256": sha256_bytes(data)} != expected_identity:
            fail(f"central record changed before freeze: {relative.as_posix()}")
        if destination.exists():
            if destination.read_bytes() != data:
                fail(f"refusing to overwrite changed frozen central record: {destination}")
        else:
            write_bytes(destination, data)
    inputs: list[dict[str, Any]] = []
    for path in li_files(native):
        identity = file_identity(path)
        inputs.append({
            "role": f"li_unit_{read_json(path)['unit']['order']:03d}",
            "path": path.relative_to(native).as_posix(),
            **identity,
        })
    for role, relative, expected_bytes, expected_sha in EXTRA_INPUTS:
        path = native / relative
        identity = file_identity(path)
        if identity != {"bytes": expected_bytes, "sha256": expected_sha}:
            fail(f"frozen input drift for {relative}: {identity}")
        inputs.append({"role": role, "path": relative, **identity})
    lock = {
        "schema": "d70-capability-source-lock/1",
        "course_id": COURSE_ID,
        "owner_lane": "O013",
        "native_repository": {
            "expected_sibling_directory": native.name,
            **{k: PUBLIC_RECORD[k] for k in ("repository", "content_commit", "content_tree", "receipt_commit", "receipt_tree")},
        },
        "central_records": {
            "capsule": {"selector": {"course_id": COURSE_ID}, "frozen_path": FROZEN_CAPSULE_REL.as_posix(), **CENTRAL_CAPSULE_RECORD},
            "coverage": {"selector": {"role_id": COURSE_ID}, "frozen_path": FROZEN_COVERAGE_REL.as_posix(), **CENTRAL_COVERAGE_RECORD},
            "shared_schema": SHARED_SCHEMA,
        },
        "li_collection": li_collection_identity(native),
        "inputs": inputs,
        "input_count": len(inputs),
        "central_titles": {
            "capsule": central["capsule"]["course"]["title"],
            "coverage": central["coverage"]["title"],
        },
    }
    if len(inputs) != 57:
        fail(f"source lock must contain 57 inputs, found {len(inputs)}")
    write_json(lock_path, lock)
    return lock_path


def verify_lock(native: Path, project: Path, lock_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    lock = read_json(lock_path)
    if lock.get("schema") != "d70-capability-source-lock/1" or lock.get("course_id") != COURSE_ID:
        fail("wrong D70 source lock schema/course")
    central_locks = lock.get("central_records", {})
    if central_locks.get("capsule", {}).get("bytes") != CENTRAL_CAPSULE_RECORD["bytes"] or central_locks.get("capsule", {}).get("sha256") != CENTRAL_CAPSULE_RECORD["sha256"] or central_locks.get("capsule", {}).get("frozen_path") != FROZEN_CAPSULE_REL.as_posix():
        fail("source lock capsule identity mismatch")
    if central_locks.get("coverage", {}).get("bytes") != CENTRAL_COVERAGE_RECORD["bytes"] or central_locks.get("coverage", {}).get("sha256") != CENTRAL_COVERAGE_RECORD["sha256"] or central_locks.get("coverage", {}).get("frozen_path") != FROZEN_COVERAGE_REL.as_posix():
        fail("source lock coverage identity mismatch")
    adapter_root = lock_path.resolve().parent.parent
    frozen_capsule_path = adapter_root / FROZEN_CAPSULE_REL
    frozen_coverage_path = adapter_root / FROZEN_COVERAGE_REL
    for label, path, expected in (
        ("capsule", frozen_capsule_path, CENTRAL_CAPSULE_RECORD),
        ("coverage", frozen_coverage_path, CENTRAL_COVERAGE_RECORD),
    ):
        if not path.is_file() or file_identity(path) != expected:
            fail(f"frozen central {label} identity mismatch")
    frozen_capsule = read_json(frozen_capsule_path)
    frozen_coverage = read_json(frozen_coverage_path)
    if frozen_capsule.get("course_id") != COURSE_ID or frozen_coverage.get("role_id") != COURSE_ID:
        fail("frozen central record selector mismatch")
    schema_identity = file_identity(project / SHARED_SCHEMA["path"])
    if schema_identity != {"bytes": SHARED_SCHEMA["bytes"], "sha256": SHARED_SCHEMA["sha256"]}:
        fail(f"shared capability schema drift: {schema_identity}")
    current_li = li_files(native)
    expected_paths = {p.relative_to(native).as_posix() for p in current_li} | {x[1] for x in EXTRA_INPUTS}
    rows = lock.get("inputs", [])
    if lock.get("input_count") != 57 or len(rows) != 57:
        fail("D70 lock input count mismatch")
    paths = [x.get("path") for x in rows]
    roles = [x.get("role") for x in rows]
    if len(set(paths)) != 57 or len(set(roles)) != 57 or set(paths) != expected_paths:
        fail("D70 lock path/role inventory mismatch")
    by_role: dict[str, dict[str, Any]] = {}
    native_root = native.resolve()
    for row in rows:
        relative = Path(row["path"])
        resolved = (native / relative).resolve()
        if native_root not in resolved.parents:
            fail(f"locked input escapes producer root: {row['path']}")
        identity = file_identity(resolved)
        if identity != {"bytes": row.get("bytes"), "sha256": row.get("sha256")}:
            fail(f"locked input drift: {row['path']}")
        by_role[row["role"]] = row
    for role, relative, expected_bytes, expected_sha in EXTRA_INPUTS:
        if by_role.get(role) != {
            "role": role,
            "path": relative,
            "bytes": expected_bytes,
            "sha256": expected_sha,
        }:
            fail(f"hard-coded frozen input identity mismatch: {role}")
    if lock.get("li_collection") != li_collection_identity(native):
        fail("Li collection lock drift")
    return lock, by_role


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            fail(f"invalid CSV header: {path}")
        rows = list(reader)
    if any(None in row for row in rows):
        fail(f"surplus CSV fields: {path}")
    return rows


def public_url(name: str) -> str:
    return PUBLIC_DOWNLOAD_BASE + name + "/content"


def build_components(manifest: dict[str, Any], duncan: dict[str, Any], cring: dict[str, Any], route: dict[str, Any]) -> list[dict[str, Any]]:
    public = {x["component_id"]: x for x in manifest["files"] if x.get("component_id")}
    roles = {x["id"]: x for x in route["components"]}
    return [
        {
            "component_id": "O013-K01", "role": roles["O013-K01"]["role"], "title": roles["O013-K01"]["label"],
            "source_locale": "zh-Hans", "target_locale": "id-ID", "pages": public["O013-K01"]["pages"],
            "public_artifact": {"name": public["O013-K01"]["name"], "bytes": public["O013-K01"]["bytes"], "sha256": public["O013-K01"]["sha256"], "url": public_url(public["O013-K01"]["name"])},
            "selection_scope": "complete_volume_one", "rights_mode": "component_specific", "license_expression": public["O013-K01"]["license"], "blanket_license_claimed": False,
        },
        {
            "component_id": "O013-K02", "role": roles["O013-K02"]["role"], "title": roles["O013-K02"]["label"],
            "source_locale": duncan["component"]["locales"]["source"], "target_locale": duncan["component"]["locales"]["target"], "pages": public["O013-K02"]["pages"],
            "public_artifact": {"name": public["O013-K02"]["name"], "bytes": public["O013-K02"]["bytes"], "sha256": public["O013-K02"]["sha256"], "url": public_url(public["O013-K02"]["name"])},
            "selection_scope": "seven_complete_roots", "excluded_external_assignments": {"assignment_sheets": 6, "problems": 49, "partial_solutions": 1, "included": False},
            "rights_mode": "component_specific", "license_expression": public["O013-K02"]["license"], "blanket_license_claimed": False,
        },
        {
            "component_id": "O013-K03", "role": roles["O013-K03"]["role"], "title": roles["O013-K03"]["label"],
            "source_locale": cring["component"]["locales"]["source"], "target_locale": cring["component"]["locales"]["target"], "pages": public["O013-K03"]["pages"],
            "public_artifact": {"name": public["O013-K03"]["name"], "bytes": public["O013-K03"]["bytes"], "sha256": public["O013-K03"]["sha256"], "url": public_url(public["O013-K03"]["name"])},
            "selection_scope": "six_exact_spans_74_pages_not_full_work", "authority_span_records": cring["counts"]["authority_span_records"],
            "rights_mode": "component_specific", "license_expression": public["O013-K03"]["license"], "blanket_license_claimed": False,
        },
        {
            "component_id": "O013-K04", "role": "original-route-and-mastery", "title": route["unit"]["title"],
            "source_locale": "id-ID", "target_locale": "id-ID", "pages": public["O013-K04"]["pages"],
            "public_artifact": {"name": public["O013-K04"]["name"], "bytes": public["O013-K04"]["bytes"], "sha256": public["O013-K04"]["sha256"], "url": public_url(public["O013-K04"]["name"])},
            "selection_scope": "edition_original_route_diagnostics_and_mastery", "source_author_attribution": False,
            "rights_mode": "component_specific", "license_expression": public["O013-K04"]["license"], "blanket_license_claimed": False,
        },
    ]


def build_native_roots(native: Path, duncan: dict[str, Any], cring: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    li_docs: dict[str, dict[str, Any]] = {}
    for path in li_files(native):
        doc = read_json(path)
        unit = doc["unit"]
        li_docs[path.name] = doc
        titles = {x["language"]: x["text"] for x in unit["titles"]}
        rows.append({
            "native_root_id": unit["id"], "component_id": "O013-K01", "source_order": unit["order"],
            "source_local_id": unit["source_local_id"], "source_title": titles.get("zh-Hans"), "target_title": titles.get("id-ID"),
            "source_locale": unit["source_language"], "target_locale": unit["target_language"],
            "source_binding": unit["source_binding"], "target_binding": unit["target_binding"],
            "surface_counts": unit["surface_counts"], "rights_ids": unit["rights_component_ids"],
            "backend_record": {"path": path.relative_to(native).as_posix(), **file_identity(path)},
        })
    for root in duncan["roots"]:
        rows.append({
            "native_root_id": root["root_id"], "component_id": "O013-K02", "source_order": root["order"],
            "source_title": root["source_title"], "target_title": root["target_title"], "source_locale": "en", "target_locale": "id-ID",
            "source_binding": {"path": root["source_path"], "bytes": root["source_bytes"], "sha256": root["source_sha256"]},
            "target_binding": {"path": root["target_path"], "bytes": root["target_bytes"], "sha256": root["target_sha256"]},
            "counts": root["counts"], "prerequisite_native_root_ids": root["prerequisite_root_ids"],
        })
    for root in cring["roots"]:
        rows.append({
            "native_root_id": root["root_id"], "component_id": "O013-K03", "source_order": root["order"],
            "source_title": root["source_title"], "target_title": root["target_title"], "source_locale": "en", "target_locale": "id-ID",
            "authority_span": root["authority_span"],
            "target_binding": {"path": root["target_path"], "bytes": root["target_bytes"], "sha256": root["target_sha256"]},
            "counts": root["counts"], "repair_ids": root["repair_ids"],
        })
    return rows, li_docs


def route_rows(route: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    component_for = {"P": "O013-K01", "R": "O013-K02", "C": "O013-K03", "S": "O013-K04"}
    prerequisites = [
        {"id": x["id"], "route": "P", "label": x["label"], "evidence": x["evidence"], "requires": []}
        for x in route["prerequisites"]
    ]
    native_nodes = prerequisites + route["nodes"]
    rows: list[dict[str, Any]] = []
    units: list[dict[str, Any]] = []
    for node in native_nodes:
        code = node["route"]
        root_id = ROUTE_ROOT_MAP.get(node["id"])
        mapping_state = "component_level_only_unmapped" if code == "P" else ("adapter_derived_crosswalk" if root_id else "edition_original_route")
        row = {
            "id": node["id"], "route": code, "label": node["label"], "requires": node.get("requires", []),
            "component_id": "O013-K04", "authored_component_id": "O013-K04",
            "mapped_reader_component_id": component_for[code], "native_root_ids": [root_id] if root_id else [],
            "mapping_state": mapping_state,
            "mapping_provenance": "adapter_derived_crosswalk" if root_id else ("component_level_only_unmapped" if code == "P" else "native_edition_original"),
            "authorship": "edition_original_route_layer_not_source_component_authorship",
        }
        if "evidence" in node:
            row["evidence"] = node["evidence"]
        rows.append(row)
        units.append(dict(row))
    return units, rows


def build_relations(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    sequence = 0
    for route in routes:
        for dependency in route["requires"]:
            sequence += 1
            rows.append({"id": f"D70:requires:{sequence:03d}", "kind": "requires", "from": dependency, "to": route["id"], "provenance": "native_original_route"})
    return rows


def build_rights(native: Path, li_docs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    native_rights: dict[str, dict[str, Any]] = {}
    for doc in li_docs.values():
        for row in doc["rights"]:
            native_rights.setdefault(row["id"], row)
    if len(native_rights) != 5:
        fail(f"expected five native Li rights rows, found {len(native_rights)}")
    rows = [
        {"rights_id": row["id"], "component_id": "O013-K01", "native": True, "stable_key": row["stable_key"], "component": row["component"], "holder_or_source": row["holder_or_source"], "license": row["license"], "required_treatment": row["required_treatment"], "bindings": row["bindings"]}
        for row in sorted(native_rights.values(), key=lambda x: x["stable_key"])
    ]
    ledger = csv_rows(native / "00_control/RIGHTS_COMPONENTS.csv")
    if len(ledger) != 9:
        fail(f"rights ledger row count mismatch: {len(ledger)}")
    additions = (
        (5, "d70:rights:external-tex-packages", "O013-K01"),
        (6, "d70:rights:duncan", "O013-K02"),
        (7, "d70:rights:cring", "O013-K03"),
        (8, "d70:rights:original-route", "O013-K04"),
    )
    for index, rights_id, component_id in additions:
        source = ledger[index]
        rows.append({"rights_id": rights_id, "component_id": component_id, "native": False, **source})
    return rows


EXPLICIT_CORRECTION_RE = re.compile(r"O013-LI-U\d{3}-(?:READER-COR|COR|CLR|ED)-\d{3}")


def build_corrections(native: Path, li_docs: dict[str, dict[str, Any]], cring: dict[str, Any]) -> list[dict[str, Any]]:
    corrections: dict[str, dict[str, Any]] = {}
    for filename, doc in li_docs.items():
        record_text = json.dumps(doc, ensure_ascii=False, sort_keys=True)
        for correction_id in sorted(set(EXPLICIT_CORRECTION_RE.findall(record_text))):
            kind = (
                "reader_equation_number_continuity" if "-READER-COR-" in correction_id
                else "editorial_normalization" if "-ED-" in correction_id
                else "clarification" if "-CLR-" in correction_id
                else "source_correction"
            )
            matching_events = [
                event for event in doc["qa_events"]
                if correction_id in json.dumps(event, ensure_ascii=False, sort_keys=True)
            ]
            corrections.setdefault(correction_id, {
                "correction_id": correction_id, "component_id": "O013-K01",
                "kind": kind,
                "unit_backend_file": "backend/data/" + filename,
                "native_event_ids": sorted({event["id"] for event in matching_events}),
                "native_event_keys": sorted({event["stable_key"] for event in matching_events}),
                "witnesses": sorted({event["witness"] for event in matching_events}),
                "provenance": "native_li_unit_record",
            })
    if len(corrections) != 69:
        fail(f"expected 69 native named Li adjustment IDs, found {len(corrections)}")
    equation_adjustments = [
        {"correction_id": "urn:uuid:2cf9847b-7718-54e7-8f21-778d1a4785f7", "component_id": "O013-K01", "kind": "reader_equation_number_continuity", "unit_backend_file": "backend/data/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.json", "native_event_key": "qa/unit-013/equation-number-continuity", "witness": "qa/UNIT_013_EQUATION_NUMBER_CORRECTION_20260823.md", "provenance": "native_li_reader_qa"},
        {"correction_id": "d70:li-adjustment:unit-014-equation-numbering", "component_id": "O013-K01", "kind": "reader_equation_number_continuity", "unit_backend_file": "backend/data/unit-014-bab-2-fungtor-adjoin-dasar.json", "native_event_key": "qa/unit-014/equation-number-continuity", "witness": "qa/UNIT_014_EQUATION_NUMBERING_CORRECTION_20260823.md", "provenance": "native_li_reader_qa"},
    ]
    rows = [corrections[key] for key in sorted(corrections)] + equation_adjustments
    rows.extend({"correction_id": x["repair_id"], "component_id": "O013-K03", **x} for x in cring["repairs"])
    return rows


def build_capabilities(native: Path, li_docs: dict[str, dict[str, Any]], duncan: dict[str, Any], cring: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    scalar_exercises = sum(int(x["unit"]["surface_counts"]["exercises"]) for x in li_docs.values())
    scalar_hints = sum(int(x["unit"]["surface_counts"]["hints"]) for x in li_docs.values())
    freeze_path = native / "qa/LI_COMPLETE_TRANSLATION_FREEZE.json"
    freeze = read_json(freeze_path) if freeze_path.is_file() else None
    if freeze is None:
        fail("Li freeze unavailable")
    corpus_exercises = sum(int(x["target_topology"]["top_level_exercises"]) for x in freeze["files"])
    corpus_hints = sum(int(x["target_topology"]["hints"]) for x in freeze["files"])
    return {
        "schema": "d70-capability-declarations/1", "course_id": COURSE_ID,
        "federation": {"components": 4, "component_sovereignty_preserved": True, "zero_copy": True, "cross_component_route_nodes": 20},
        "li_corpus_truth": {"top_level_exercises": corpus_exercises, "hints": corpus_hints, "backend_scalar_exercises": scalar_exercises, "backend_scalar_hints": scalar_hints, "encoding_gap_units": [7, 18]},
        "source_support": {"exercises": corpus_exercises + duncan["counts"]["exercises"] + cring["counts"]["exercises"], "hints": corpus_hints + cring["counts"]["hints"], "answers": 0, "solutions": 0},
        "edition_original_support": {"diagnostics": len(route["diagnostics"]), "mastery_tasks": len(route["mastery"]), "mastery_hints": sum(len(x["hints"]) for x in route["mastery"]), "mastery_answers": sum(1 for x in route["mastery"] if x.get("answer"))},
        "learner": {"four_reader_routes": True, "seven_stage_route": True, "searchable_native_root_catalog": True, "answers_staged_in_closed_details": True, "native_semantic_bodies_embedded": False},
        "educator": {"dependency_graph": True, "diagnostic_gates": True, "mastery_completion_policy": True, "answer_key": True, "terminology_and_corrections": True, "component_rights": True, "shared_route_identities_with_learner": True},
        "accessibility": {"generated_navigation_html": True, "native_semantic_html": False, "native_epub": False, "native_mathml": False, "tagged_pdf_claimed": False, "complete_tounicode_claimed": False, "wcag_conformance_claimed": False, "assistive_technology_testing_claimed": False},
        "reproducibility": {"li_semantic_backend_build_visual_pass": True, "li_whole_reader_byte_replay": False, "duncan_backend_byte_replay": True, "cring_backend_byte_replay": True, "original_build_qa": True, "aggregate_source_zip_deterministic": True, "pdf_byte_replay": False, "full_native_roundtrip": False},
        "limitations": [
            "This adapter contains metadata, evidence, route text, diagnostics, and edition-original mastery only; it copies no native book body, formula, TeX, PDF, or source archive.",
            "P01-P06 map only to the Li component because the native route does not identify exact Li unit roots for them.",
            "The CRing component is six exact selected spans, not the complete CRing work.",
            "Duncan's six external assignment sheets, 49 problems, and partial solution are outside the pinned CC BY repository and remain excluded.",
            "The source components provide no answers or solutions; the eight mastery answers are separately attributed edition-original material.",
            "Generated HTML is metadata navigation, not a converted native semantic reader.",
            "No native EPUB, MathML, tagged PDF, complete ToUnicode, WCAG conformance, or assistive-technology user test is claimed.",
            "Li whole-reader byte replay and all PDF byte replay remain unproven; the full native roundtrip is therefore false.",
        ],
    }


def shared_learning_map(course: dict[str, Any], components: list[dict[str, Any]], units: list[dict[str, Any]], relations: list[dict[str, Any]], diagnostics: list[dict[str, Any]], mastery: list[dict[str, Any]], native_roots: list[dict[str, Any]], capabilities: dict[str, Any]) -> dict[str, Any]:
    component_map = {x["component_id"]: x for x in components}
    diagnostics_by_home: dict[str, list[dict[str, Any]]] = {}
    mastery_by_home: dict[str, list[dict[str, Any]]] = {}
    for diagnostic in diagnostics:
        diagnostics_by_home.setdefault(diagnostic["targets"][0], []).append(diagnostic)
    for task in mastery:
        mastery_by_home.setdefault(task["targets"][0], []).append(task)
    shared_units = []
    for unit in units:
        authored_component = component_map[unit["authored_component_id"]]
        mapped_component = component_map[unit["mapped_reader_component_id"]]
        component_url = mapped_component["public_artifact"]["url"]
        exercises = []
        for diagnostic in diagnostics_by_home.get(unit["id"], []):
            href = f"https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70.html#{diagnostic['id']}"
            exercises.append({
                "id": diagnostic["id"], "unit_id": unit["id"], "title": diagnostic["question"], "kind": "edition-original-entry-diagnostic",
                "sequence": len(exercises) + 1, "curriculum_status": "diagnostic_for_targets:" + ",".join(diagnostic["targets"]), "href": href,
                "hint": {"status": "not_present", "source_anchor": diagnostic["id"], "label": None, "href": None},
                "check": {"status": "complete", "source_anchor": diagnostic["id"] + "-A", "label": "Jawaban yang diharapkan", "href": href},
                "solution": {"status": "not_present", "source_anchor": "source-components", "label": None, "href": None},
            })
        for task in mastery_by_home.get(unit["id"], []):
            href = f"https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70.html#{task['id']}"
            exercises.append({
                "id": task["id"], "unit_id": unit["id"], "title": task["prompt"], "kind": "edition-original-mastery",
                "sequence": len(exercises) + 1, "curriculum_status": "required_or_pool_for_targets:" + ",".join(task["targets"]), "href": href,
                "hint": {"status": "complete", "source_anchor": task["id"] + ":hints", "label": "Dua petunjuk bertahap", "href": href},
                "check": {"status": "complete", "source_anchor": task["answer"]["id"], "label": "Jawaban pemeriksaan", "href": href},
                "solution": {"status": "not_present", "source_anchor": "source-components", "label": None, "href": None},
            })
        unit_components = [
            {"id": authored_component["component_id"], "source": authored_component["title"], "license": authored_component["license_expression"]}
        ]
        if mapped_component["component_id"] != authored_component["component_id"]:
            unit_components.append(
                {"id": mapped_component["component_id"], "source": mapped_component["title"], "license": mapped_component["license_expression"]}
            )
        shared_units.append({
            "id": unit["id"], "title": unit["label"], "href": component_url,
            "sections": unit["native_root_ids"],
            "objectives_href": f"https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70.html#{unit['id']}",
            "previous_units": unit["requires"],
            "components": unit_components,
            "exercises": exercises,
        })
    prereqs = [
        {"id": row["id"], "unit": row["to"], "prerequisite": row["from"], "required_for_course": True, "sections": [], "exercises": [], "href": f"https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70.html#{row['to']}"}
        for row in relations
    ]
    artifacts = []
    for index, name in enumerate(list(PUBLIC_FILES)[:5], start=1):
        artifacts.append({"id": f"D70:public:{index:02d}", "kind": "application/pdf" if name.endswith(".pdf") else "application/zip", "path": public_url(name), "bytes": PUBLIC_FILES[name][0], "sha256": PUBLIC_FILES[name][1]})
    sources = [{"id": x["component_id"], "role": x["role"], "license": x["license_expression"], "identity": x["public_artifact"]} for x in components]
    return {
        "contract": "course-learning-capability/1", "course_id": COURSE_ID, "locale": "id-ID",
        "native_dataset": "O013 four-component graduate-algebra federation", "source_catalog": SOURCE_CATALOG,
        "units": shared_units, "prerequisite_routes": prereqs, "labs": [], "environments": [], "artifacts": artifacts,
        "sources": sources, "external_relation_nodes": [x["native_root_id"] for x in native_roots],
        "limitations": capabilities["limitations"],
    }


def css() -> str:
    return """body{margin:0;background:#f5f1e8;color:#17221c;font:16px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px}a{color:#075f55}header{background:#173c34;color:#fff;padding:28px;border-radius:18px}header p{max-width:76ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.card,section{background:#fff;border:1px solid #d5d0c4;border-radius:14px;padding:18px;margin:18px 0}.pill{display:inline-block;background:#d8eee7;border-radius:999px;padding:3px 10px;margin:2px}table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}details{margin:.45rem 0;padding:.5rem;border:1px solid #d9d3c6;border-radius:8px}input{width:min(100%,38rem);padding:.7rem;border:1px solid #777;border-radius:8px}.muted{color:#59655f}.warning{background:#fff4cd;border-left:5px solid #bc7813;padding:12px}.sr-only{position:absolute;left:-10000px}@media(max-width:650px){main{padding:12px}table{display:block;overflow-x:auto}}"""


def learner_html(course: dict[str, Any], components: list[dict[str, Any]], units: list[dict[str, Any]], stages: list[dict[str, Any]], diagnostics: list[dict[str, Any]], mastery: list[dict[str, Any]], roots: list[dict[str, Any]], limitations: list[str]) -> str:
    esc = html.escape
    component_cards = "".join(f'<article class="card"><h3>{esc(x["component_id"])} · {esc(x["title"])}</h3><p>{x["pages"]} halaman · sumber {esc(x["source_locale"])}</p><p><a href="{esc(x["public_artifact"]["url"])}">Buka pembaca</a></p></article>' for x in components)
    unit_map = {x["id"]: x for x in units}
    stage_html = []
    for stage in stages:
        items = []
        for item in stage["items"]:
            label = unit_map.get(item, {}).get("label", item)
            items.append(f'<li><a href="#{esc(item)}">{esc(item)}</a> · {esc(label)}</li>')
        stage_html.append(f'<article class="card"><h3>{esc(stage["id"])} · {esc(stage["label"])}</h3><ol>{"".join(items)}</ol></article>')
    unit_html = "".join(f'<article class="card" id="{esc(x["id"])}"><h3>{esc(x["id"])} · {esc(x["label"])}</h3><p>Komponen {esc(x["component_id"])} · pemetaan {esc(x["mapping_state"])}</p><p>Prasyarat: {esc(", ".join(x["requires"]) or "tidak ada pada lapisan rute")}</p></article>' for x in units)
    diagnostic_html = "".join(f'<article class="card" id="{esc(x["id"])}"><h3>{esc(x["id"])} · sasaran {esc(", ".join(x["targets"]))}</h3><p>{esc(x["question"])}</p><details><summary>Periksa jawaban yang diharapkan</summary><p data-answer-id="{esc(x["id"])}-A">{esc(x["expected"])}</p></details></article>' for x in diagnostics)
    mastery_html = []
    for task in mastery:
        hints = "".join(f'<details><summary>Petunjuk {i}</summary><p data-hint-id="{esc(h["id"])}">{esc(h["text"])}</p></details>' for i, h in enumerate(task["hints"], start=1))
        answer = f'<details><summary>Jawaban ringkas</summary><p data-answer-id="{esc(task["answer"]["id"])}">{esc(task["answer"]["text"])}</p></details>'
        mastery_html.append(f'<article class="card" id="{esc(task["id"])}"><h3>{esc(task["id"])} · {esc(", ".join(task["targets"]))}</h3><p>{esc(task["prompt"])}</p>{hints}{answer}</article>')
    root_rows = "".join(f'<tr data-root-row data-search="{esc((x["native_root_id"]+" "+str(x.get("target_title") or "")+" "+x["component_id"]).lower())}"><td>{esc(x["component_id"])}</td><td>{esc(x["native_root_id"])}</td><td>{esc(str(x.get("target_title") or ""))}</td><td>{esc(x["source_locale"])}</td></tr>' for x in roots)
    limitation_html = "".join(f"<li>{esc(x)}</li>" for x in limitations)
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D70 · Aljabar Pascasarjana</title><style>{css()}</style></head><body><main>
<header><p class="pill">D70 · 716 halaman · 4 komponen</p><h1>{esc(course['title'])}</h1><p>{esc(course['purpose'])}</p><p><a style="color:#d8fff1" href="D70-pengajar.html">Tampilan pengajar</a></p></header>
<section><h2>Empat pembaca, satu rute</h2><p>Komponen tetap mandiri dalam hak, bahasa sumber, dan provenans. Halaman ini menyatukan navigasi—bukan menyalin isi buku.</p><div class="grid">{component_cards}</div></section>
<section><h2>Tujuh tahap belajar</h2><div class="grid">{"".join(stage_html)}</div></section>
<section><h2>Simpul rute</h2><div class="grid">{unit_html}</div></section>
<section><h2>Diagnostik awal</h2><p class="muted">Jawaban disembunyikan sampai dibuka.</p><div class="grid">{diagnostic_html}</div></section>
<section><h2>Tugas penguasaan</h2><p class="muted">Dua petunjuk dan jawaban setiap tugas disajikan bertahap.</p><div class="grid">{"".join(mastery_html)}</div></section>
<section><h2>Katalog 54 akar native</h2><label for="root-search">Cari judul, ID, atau komponen</label><br><input id="root-search" type="search" autocomplete="off"><p id="root-count" aria-live="polite">54 akar</p><table><thead><tr><th>Komponen</th><th>ID native</th><th>Judul</th><th>Bahasa sumber</th></tr></thead><tbody>{root_rows}</tbody></table></section>
<section class="warning"><h2>Batas bukti</h2><ul>{limitation_html}</ul></section>
<script>(()=>{{const q=document.getElementById('root-search'),rows=[...document.querySelectorAll('[data-root-row]')],count=document.getElementById('root-count');q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();let n=0;for(const r of rows){{const show=!v||r.dataset.search.includes(v);r.hidden=!show;if(show)n++}}count.textContent=n+' akar';}})}})();</script>
</main></body></html>"""


def educator_html(course: dict[str, Any], components: list[dict[str, Any]], units: list[dict[str, Any]], relations: list[dict[str, Any]], diagnostics: list[dict[str, Any]], mastery: list[dict[str, Any]], policies: dict[str, Any], rights: list[dict[str, Any]], terminology: list[dict[str, Any]], corrections: list[dict[str, Any]], evidence: dict[str, Any], limitations: list[str]) -> str:
    esc = html.escape
    rel_rows = "".join(f"<tr><td>{esc(x['from'])}</td><td>{esc(x['to'])}</td><td>{esc(x['provenance'])}</td></tr>" for x in relations)
    diag_rows = "".join(f"<tr><td>{esc(x['id'])}</td><td>{esc(', '.join(x['targets']))}</td><td>{esc(x['question'])}</td><td>{esc(x['expected'])}</td></tr>" for x in diagnostics)
    mastery_rows = "".join(f"<tr><td>{esc(x['id'])}</td><td>{esc(', '.join(x['targets']))}</td><td>{esc(x['prompt'])}</td><td>{esc(x['answer']['text'])}</td></tr>" for x in mastery)
    rights_rows = "".join(f"<tr><td>{esc(x['rights_id'])}</td><td>{esc(x['component_id'])}</td><td>{esc(x.get('license',''))}</td><td>{esc(x.get('required_treatment',''))}</td></tr>" for x in rights)
    limitation_html = "".join(f"<li>{esc(x)}</li>" for x in limitations)
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D70 · Panduan Pengajar</title><style>{css()}</style></head><body><main>
<header><p class="pill">D70 · tampilan pengajar</p><h1>{esc(course['title'])}</h1><p>Graf dependensi, diagnostik, jawaban, penguasaan, istilah, koreksi, hak komponen, dan batas bukti dengan identitas yang sama seperti tampilan pelajar.</p><p><a style="color:#d8fff1" href="D70.html">Tampilan pelajar</a></p></header>
<section><h2>Ringkasan terverifikasi</h2><div class="grid"><article class="card"><strong>4</strong><br>komponen / 716 halaman</article><article class="card"><strong>54</strong><br>akar native</article><article class="card"><strong>20 / 36</strong><br>simpul / dependensi</article><article class="card"><strong>690</strong><br>istilah: 689 diterima, 1 provisional</article><article class="card"><strong>{len(corrections)}</strong><br>penyesuaian: {sum(x['component_id']=='O013-K01' for x in corrections)} Li, {sum(x['component_id']=='O013-K03' for x in corrections)} CRing</article></div></section>
<section><h2>Graf dependensi</h2><table><thead><tr><th>Dari</th><th>Ke</th><th>Provenans</th></tr></thead><tbody>{rel_rows}</tbody></table></section>
<section><h2>Kunci diagnostik dan gerbang</h2><table><thead><tr><th>ID</th><th>Sasaran</th><th>Pertanyaan</th><th>Jawaban</th></tr></thead><tbody>{diag_rows}</tbody></table><pre>{esc(json.dumps(policies['diagnostic_policy'], ensure_ascii=False, indent=2))}</pre></section>
<section><h2>Penguasaan dan kebijakan penyelesaian</h2><table><thead><tr><th>ID</th><th>Sasaran</th><th>Tugas</th><th>Jawaban</th></tr></thead><tbody>{mastery_rows}</tbody></table><pre>{esc(json.dumps(policies['completion'], ensure_ascii=False, indent=2))}</pre></section>
<section><h2>Istilah dan koreksi</h2><p>Istilah: {len(terminology)}; diterima {sum(x['status']=='admitted' for x in terminology)}; provisional {sum(x['status']=='provisional' for x in terminology)}. Koreksi: {len(corrections)}; Li {sum(x['component_id']=='O013-K01' for x in corrections)}; CRing {sum(x['component_id']=='O013-K03' for x in corrections)}.</p><p>Istilah provisional tetap: <strong>valuation → valuasi</strong> (Bab 10).</p></section>
<section><h2>Hak per komponen</h2><table><thead><tr><th>ID</th><th>Komponen</th><th>Lisensi</th><th>Perlakuan</th></tr></thead><tbody>{rights_rows}</tbody></table></section>
<section><h2>Identitas publik</h2><p>GitHub commit {esc(evidence['content_commit'])}; Zenodo DOI {esc(evidence['doi'])}; sembilan berkas / {evidence['total_bytes']:,} byte, seluruh byte dibaca balik anonim.</p></section>
<section class="warning"><h2>Batas bukti</h2><ul>{limitation_html}</ul></section>
</main></body></html>"""


def readme_text() -> str:
    return """# D70 thin capability adapter\n\nThis adapter federates the four native O013 components without copying their book bodies. It preserves native identities, component rights, source locales, exact selection boundaries, route dependencies, diagnostic/mastery provenance, terminology state, correction records, public byte identities, and explicit accessibility/replay limits.\n\nLearners receive a seven-stage route, staged diagnostics/mastery support, four public reader destinations, and a searchable 54-root catalog. Educators receive the same route identities plus dependency, answer, policy, correction, terminology, rights, and evidence views.\n\nThe adapter does **not** claim native HTML, EPUB, MathML, tagged PDF, complete ToUnicode, WCAG conformance, assistive-technology testing, PDF byte replay, or a complete native roundtrip.\n"""


def tooling_inventory(project: Path) -> list[dict[str, Any]]:
    names = ["d70_capability_model_v1.py", "build_d70_capability_v1.py", "validate_d70_capability_v1.py", "package_d70_capability_v1.py"]
    rows = []
    for name in names:
        path = project / "scripts" / name
        rows.append({"path": f"scripts/{name}", **file_identity(path)})
    return rows


def build(native: Path, output: Path, lock_path: Path, project: Path = PROJECT) -> dict[str, Any]:
    lock, roles = verify_lock(native, project, lock_path)
    lock_adapter = lock_path.resolve().parent.parent
    frozen_capsule = read_json(lock_adapter / FROZEN_CAPSULE_REL)
    duncan = read_json(native / roles["duncan_component"]["path"])
    duncan_validation = read_json(native / roles["duncan_validation"]["path"])
    cring = read_json(native / roles["cring_component"]["path"])
    cring_validation = read_json(native / roles["cring_validation"]["path"])
    route = read_json(native / roles["original_route"]["path"])
    original_qa = read_json(native / roles["original_build_qa"]["path"])
    manifest = read_json(native / roles["aggregate_manifest"]["path"])
    zenodo = read_json(native / roles["zenodo_public_readback"]["path"])
    github_content = read_json(native / roles["github_content_readback"]["path"])
    github_terminal = read_json(native / roles["github_terminal_readback"]["path"])
    if duncan_validation.get("result") != "PASS" or cring_validation.get("result") != "PASS" or original_qa.get("result") != "pass":
        fail("native component validation is not passing")
    if (
        zenodo.get("result") != "PASS"
        or zenodo.get("public_access") is not True
        or zenodo.get("anonymous_api_readback") is not True
        or zenodo.get("anonymous_full_file_readback") is not True
        or zenodo.get("record_id") != PUBLIC_RECORD["record_id"]
        or zenodo.get("doi") != PUBLIC_RECORD["doi"]
        or zenodo.get("concept_doi") != PUBLIC_RECORD["concept_doi"]
        or zenodo.get("file_count") != PUBLIC_RECORD["file_count"]
        or zenodo.get("total_bytes") != PUBLIC_RECORD["total_bytes"]
    ):
        fail("Zenodo public readback is not exact/pass")
    public_from_receipt = {x["name"]: (x["bytes"], x["sha256"]) for x in zenodo["files"]}
    if public_from_receipt != PUBLIC_FILES:
        fail("Zenodo public file identity mismatch")
    if not github_content.get("all_match") or not github_terminal.get("all_match") or github_content.get("commit") != PUBLIC_RECORD["content_commit"] or github_content.get("tree") != PUBLIC_RECORD["content_tree"] or github_terminal.get("commit") != PUBLIC_RECORD["receipt_commit"] or github_terminal.get("tree") != PUBLIC_RECORD["receipt_tree"]:
        fail("GitHub public readback identity mismatch")

    components = build_components(manifest, duncan, cring, route)
    native_roots, li_docs = build_native_roots(native, duncan, cring)
    units, routes = route_rows(route)
    relations = build_relations(routes)
    stages = route["study_sequence"]
    diagnostics = route["diagnostics"]
    mastery = route["mastery"]
    policies = {"schema": "d70-capability-policies/1", "diagnostic_policy": route["diagnostic_policy"], "completion": route["completion"]}
    rights = build_rights(native, li_docs)
    terminology = [{"term_id": f"D70:term:{i:04d}", **row} for i, row in enumerate(csv_rows(native / roles["terminology"]["path"]), start=1)]
    corrections = build_corrections(native, li_docs, cring)
    original_bridges = [{**row, "component_id": "O013-K03", "authorship": "adapter_or_edition_original_not_source_author"} for row in cring["original_bridge_records"]]
    capabilities = build_capabilities(native, li_docs, duncan, cring, route)
    frozen_course = frozen_capsule["course"]
    course = {
        "schema": "d70-course/1", "course_id": COURSE_ID, "title": frozen_course["title"],
        "topic": frozen_course["topic"], "level": frozen_course["level"], "state": frozen_course["state"],
        "purpose": frozen_course["purpose"], "outcome": frozen_course["outcome"], "prerequisites": frozen_course["prerequisites"],
        "locale": frozen_capsule["locale"], "pages": 716, "component_ids": [x["component_id"] for x in components],
        "route_ids": [x["id"] for x in units], "aggregate_license": "component_specific", "zero_copy": True,
        "public_repository": PUBLIC_RECORD["repository"], "public_doi": PUBLIC_RECORD["doi"],
    }
    evidence = {
        "schema": "d70-capability-evidence/1", **PUBLIC_RECORD,
        "public_readback_result": "PASS", "anonymous_full_file_readback": True,
        "public_files": [{"name": name, "bytes": value[0], "sha256": value[1], "url": public_url(name)} for name, value in PUBLIC_FILES.items()],
        "li_collection": lock["li_collection"], "source_lock": {"path": "input/source-lock.json", **file_identity(lock_path)},
        "native_validation": {
            "duncan": {"result": duncan_validation["result"], "artifact_regeneration_byte_identical": duncan_validation["checks"]["artifact_regeneration_byte_identical"]},
            "cring": {"result": cring_validation["result"], "artifact_regeneration_byte_identical": cring_validation["checks"]["artifact_regeneration_byte_identical"]},
            "original": {"result": original_qa["result"], "deterministic_byte_replay": False},
        },
        "central_record_locks": lock["central_records"],
    }
    learning = shared_learning_map(course, components, units, relations, diagnostics, mastery, native_roots, capabilities)
    bundle = {
        "course": course, "components": components, "native_roots": native_roots, "units": units,
        "routes": routes, "relations": relations, "stages": stages, "diagnostics": diagnostics, "mastery": mastery,
        "policies": policies, "rights": rights, "terminology": terminology, "corrections": corrections,
        "original_bridges": original_bridges, "capabilities": capabilities, "evidence": evidence, "learning_map": learning,
    }
    errors = validate_bundle(bundle)
    if errors:
        fail("D70 generated bundle failed invariants: " + ", ".join(errors))
    for key, (relative, kind) in BUNDLE_FILES.items():
        if kind == "jsonl":
            write_jsonl(output / relative, bundle[key])
        else:
            write_json(output / relative, bundle[key])
    write_bytes(output / "views/D70.html", learner_html(course, components, units, stages, diagnostics, mastery, native_roots, capabilities["limitations"]).encode("utf-8"))
    write_bytes(output / "views/D70-pengajar.html", educator_html(course, components, units, relations, diagnostics, mastery, policies, rights, terminology, corrections, evidence, capabilities["limitations"]).encode("utf-8"))
    write_bytes(output / "README.md", readme_text().encode("utf-8"))
    for case_id, expected_errors in NEGATIVE_CASES.items():
        write_json(output / f"fixtures/negative/{case_id}.json", {"schema": "d70-negative-fixture/1", "case_id": case_id, "mutation": case_id, "expected_errors": list(expected_errors)})
    manifest_paths = [relative for relative, _ in BUNDLE_FILES.values()] + ["views/D70.html", "views/D70-pengajar.html", "README.md"] + [f"fixtures/negative/{x}.json" for x in NEGATIVE_CASES]
    output_rows = [{"path": relative, **file_identity(output / relative)} for relative in sorted(manifest_paths)]
    manifest_record = {
        "schema": "d70-capability-manifest/1", "course_id": COURSE_ID,
        "contract": "course-learning-capability/1",
        "content_policy": "metadata_and_evidence_only", "zero_copy_native_bodies": True,
        "full_native_roundtrip_claimed": False, "public_state_changed": False,
        "source_lock": {"path": "input/source-lock.json", **file_identity(lock_path)},
        "outputs": output_rows, "tooling": tooling_inventory(project), "counts": EXPECTED_COUNTS,
        "output_tree": tree_identity(output, manifest_paths),
    }
    write_json(output / "manifest.json", manifest_record)
    return manifest_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--initialize-lock", action="store_true")
    args = parser.parse_args()
    native = args.native.resolve()
    output = args.output.resolve()
    lock_path = args.lock.resolve() if args.lock else output / "input/source-lock.json"
    if args.initialize_lock:
        lock_path = initialize_lock(native, output, PROJECT)
    if not lock_path.is_file():
        fail(f"source lock missing: {lock_path}; run once with --initialize-lock")
    manifest = build(native, output, lock_path, PROJECT)
    print(json.dumps({"result": "PASS", "manifest": manifest}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
