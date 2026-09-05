"""Build the bounded D100 English course-learning capability adapter.

Large native JSONL files are streamed.  The generated adapter is a zero-copy
identity and navigation projection; it never copies mathematical bodies.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

from d100_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DATASET_SHA256,
    EXPECTED_COMPANION_EXERCISES,
    EXPECTED_COMPANION_UNITS,
    EXPECTED_CONCENTRATED_UNITS,
    EXPECTED_ENTITY_COUNTS,
    EXPECTED_EXERCISES,
    EXPECTED_EXISTING_MASTERY_SOLUTIONS,
    EXPECTED_MASTERY_ITEMS,
    EXPECTED_NEGATIVE_SOLUTIONS,
    EXPECTED_NEW_MASTERY_SOLUTIONS,
    EXPECTED_PREREQUISITES,
    EXPECTED_PROJECTED_UNITS,
    EXPECTED_SOURCE_EXERCISES,
    EXPECTED_SOURCE_SOLUTIONS,
    EXPECTED_SOURCE_UNITS,
    EXPECTED_TOTAL_RECORDS,
    LOCALE,
    NATIVE_DATASET,
    PAGES_BASE,
    RELEASE_BASE,
    RELEASE_PAGE,
    SOURCE_COMMIT,
    D100Error,
    canonical_json,
    file_identity,
    iter_jsonl,
    load_bundle,
    read_json,
    sha256_bytes,
    validate_bundle,
    write_bytes,
    write_json,
    write_jsonl,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
DEFAULT_NATIVE = PROJECT.parent / "algebraic-geometry-bridge-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d100-capability-v1"

INPUT_SPECS = (
    ("index_manifest", "backend/english/release-en-v1.0.0/index/MANIFEST.json"),
    ("index_dataset", "backend/english/release-en-v1.0.0/index/common.dataset.json"),
    ("classical_manifest", "backend/english/release-en-v1.0.0/classical/MANIFEST.json"),
    ("classical_record_schema", "backend/english/release-en-v1.0.0/classical/record.schema.json"),
    ("classical_records", "backend/english/release-en-v1.0.0/classical/records.jsonl"),
    ("bgk_manifest", "backend/english/release-en-v1.0.0/bgk/MANIFEST.json"),
    ("bgk_record_schema", "backend/english/release-en-v1.0.0/bgk/record.schema.json"),
    ("bgk_records", "backend/english/release-en-v1.0.0/bgk/records.jsonl"),
    ("original_manifest", "backend/english/release-en-v1.0.0/original/MANIFEST.json"),
    ("original_record_schema", "backend/english/release-en-v1.0.0/original/record.schema.json"),
    ("original_records", "backend/english/release-en-v1.0.0/original/records.jsonl"),
    ("classical_input", "backend/english/inputs/classical.json"),
    ("bgk_input", "backend/english/inputs/bgk.json"),
    ("original_input", "backend/english/inputs/original.json"),
    ("translation_qa", "qa/english/TRANSLATION_INTEGRATION_QA.json"),
    ("reader_qa", "qa/english/READER_QA_RELEASE_GATE.json"),
    ("github_publication", "qa/english/GITHUB_PUBLICATION_EN_V1_SUMMARY.json"),
    ("release_bindings", "00_control/english/RELEASE_BINDINGS_EN_V2.json"),
    ("github_release_manifest", "00_control/english/GITHUB_RELEASE_MANIFEST_EN_V3.json"),
)

EXPECTED_INPUT_SHAPES = {
    "classical": {"contract_inputs": 4, "english_source_order": 120, "field_translations": 1521, "historical_source_paths": 16, "native_inputs": 3, "sources": 120, "block_bindings": 849, "supplemental_sources": 0},
    "bgk": {"contract_inputs": 4, "english_source_order": 122, "field_translations": 7389, "historical_source_paths": 8, "native_inputs": 3, "sources": 121, "block_bindings": 1111, "supplemental_sources": 1},
    "original": {"contract_inputs": 5, "english_source_order": 32, "field_translations": 58, "historical_source_paths": 0, "native_inputs": 3, "sources": 32, "block_bindings": 0, "supplemental_sources": 0},
}


def fail(code: str) -> None:
    raise D100Error(code)


def refresh_source_lock(native: Path, path: Path) -> dict[str, Any]:
    inputs = []
    for role, relative in INPUT_SPECS:
        target = native / relative
        if not target.is_file():
            fail("D100-LOCK-MISSING:" + relative)
        inputs.append({"role": role, "path": relative, **file_identity(target)})
    lock = {
        "schema": "d100-capability-source-lock/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "native_release": "en-v1.0.0",
        "inputs": inputs,
    }
    write_json(path, lock)
    return lock


def verify_lock(native: Path, lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if lock.get("schema") != "d100-capability-source-lock/1" or lock.get("course_id") != COURSE_ID or lock.get("locale") != LOCALE:
        fail("D100-LOCK-SCHEMA")
    roles: dict[str, dict[str, Any]] = {}
    for row in lock.get("inputs", []):
        role = row.get("role")
        if role in roles:
            fail("D100-LOCK-DUPLICATE-ROLE")
        target = native / str(row.get("path"))
        if not target.is_file() or file_identity(target) != {"bytes": row.get("bytes"), "sha256": row.get("sha256")}:
            fail("D100-LOCK-DRIFT:" + str(row.get("path")))
        roles[str(role)] = row
    if set(roles) != {role for role, _ in INPUT_SPECS}:
        fail("D100-LOCK-ROLE-SET")
    return roles


def input_path(native: Path, roles: dict[str, dict[str, Any]], role: str) -> Path:
    return native / roles[role]["path"]


def verify_control_inputs(native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    index = read_json(input_path(native, roles, "index_dataset"))
    if index.get("schema") != "d100-en-native-backend-index-v1" or index.get("status") != "PASS" or index.get("language") != "en":
        fail("D100-INDEX-STATUS")
    index_counts = {row["lane"]: row["entity_counts"] for row in index.get("lanes", [])}
    if index_counts != EXPECTED_ENTITY_COUNTS:
        fail("D100-INDEX-COUNTS")
    if file_identity(input_path(native, roles, "index_dataset")) != {"bytes": 3984, "sha256": DATASET_SHA256}:
        fail("D100-INDEX-IDENTITY")

    manifests = {}
    for lane in ("classical", "bgk", "original"):
        manifest = read_json(input_path(native, roles, f"{lane}_manifest"))
        manifests[lane] = manifest
        if (
            manifest.get("schema") != "ag-bridge-english-backend-adapter-manifest-v1"
            or manifest.get("lane") != lane
            or manifest.get("language") != "en"
            or manifest.get("status") != "translated_final_frozen_adapter_checks_pass"
            or manifest.get("publication_status") != "not_a_build_or_publication_or_common_migration_receipt"
            or manifest.get("counts") != EXPECTED_ENTITY_COUNTS[lane]
        ):
            fail("D100-LANE-MANIFEST:" + lane)

    input_maps = {}
    for lane in ("classical", "bgk", "original"):
        value = read_json(input_path(native, roles, f"{lane}_input"))
        input_maps[lane] = value
        if value.get("schema") != "ag-bridge-english-backend-input-v2" or value.get("lane") != lane:
            fail("D100-INPUT-MAP-SCHEMA:" + lane)
        actual = {key: len(value.get(key, [])) for key in EXPECTED_INPUT_SHAPES[lane]}
        if actual != EXPECTED_INPUT_SHAPES[lane]:
            fail("D100-INPUT-MAP-COUNTS:" + lane)

    translation = read_json(input_path(native, roles, "translation_qa"))
    coverage = translation.get("coverage", {})
    if (
        translation.get("schema") != "d100-en-translation-integration-qa-v1"
        or translation.get("status") != "PASS"
        or translation.get("deterministic") is not True
        or translation.get("target_count") != 274
        or translation.get("translation_packet_count") != 18
        or translation.get("review_receipt_count") != 15
        or coverage.get("exercise_count") != 1188
        or coverage.get("public_solution_count") != 147
        or coverage.get("negative_solution_count") != 1041
        or coverage.get("terminal_bridge_file_count") != 32
    ):
        fail("D100-TRANSLATION-QA")

    reader = read_json(input_path(native, roles, "reader_qa"))
    if reader.get("schema") != "d100-en-reader-qa-v1" or reader.get("status") != "PASS":
        fail("D100-READER-QA")
    publication = read_json(input_path(native, roles, "github_publication"))
    if (
        publication.get("schema") != "d100-english-github-publication-summary-v1"
        or publication.get("status") != "PASS"
        or publication.get("commit") != SOURCE_COMMIT
        or publication.get("release", {}).get("tag") != "en-v1.0.0"
        or publication.get("release", {}).get("asset_count") != 13
        or publication.get("verification", {}).get("anonymous_raw_files") != "PASS_768_OF_768"
        or publication.get("verification", {}).get("anonymous_release_inventory_and_assets") != "PASS_13_OF_13"
        or publication.get("verification", {}).get("anonymous_pages") != "PASS_474_OF_474"
    ):
        fail("D100-GITHUB-PUBLICATION-QA")
    bindings = read_json(input_path(native, roles, "release_bindings"))
    github_manifest = read_json(input_path(native, roles, "github_release_manifest"))
    readers = bindings.get("readers", [])
    if [row.get("page_count") for row in readers] != [504, 381, 89] or sum(row.get("page_count", 0) for row in readers) != 974:
        fail("D100-READER-PAGES")
    assets = github_manifest.get("assets", [])
    if (
        github_manifest.get("schema") != "ag-bridge-english-github-release-v1"
        or github_manifest.get("release", {}).get("tag") != "en-v1.0.0"
        or github_manifest.get("release", {}).get("draft") is not False
        or github_manifest.get("release", {}).get("prerelease") is not False
        or len(assets) != 13
        or sum(row.get("bytes", 0) for row in assets) != 79927072
    ):
        fail("D100-RELEASE-MANIFEST")
    return {
        "index": index,
        "manifests": manifests,
        "input_maps": input_maps,
        "translation": translation,
        "reader": reader,
        "publication": publication,
        "bindings": bindings,
        "github_manifest": github_manifest,
    }


def _small_title(payload: dict[str, Any]) -> str | None:
    for key in ("title", "title_markdown"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return re.sub(r"\s+", " ", value.strip())
    return None


def scan_lane(path: Path, lane: str) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    term_status: Counter[str] = Counter()
    correction_status: Counter[str] = Counter()
    rights_licenses: Counter[str] = Counter()
    unit_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exercises: list[dict[str, Any]] = []
    solutions: dict[str, dict[str, Any]] = {}
    solves: list[tuple[str, str]] = []
    independent: dict[str, str] = {}
    existing_mastery: list[dict[str, Any]] = []
    seen: set[str] = set()
    human_review_claims: set[bool] = set()
    for row in iter_jsonl(path):
        entity = str(row.get("entity_class"))
        stable_id = str(row.get("stable_id"))
        counts[entity] += 1
        language_counts[str(row.get("language"))] += 1
        if stable_id in seen:
            fail(f"D100-NATIVE-DUPLICATE-ID:{lane}:{stable_id}")
        seen.add(stable_id)
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if entity == "unit":
            unit_by_path[str(row.get("path"))].append(
                {
                    "stable_id": stable_id,
                    "parent_id": row.get("parent_id"),
                    "path": row.get("path"),
                    "order": row.get("order") if isinstance(row.get("order"), int) else 0,
                    "language": row.get("language"),
                    "title": _small_title(payload),
                    "unit_type": payload.get("unit_type"),
                    "heading_level": payload.get("heading_level"),
                }
            )
        elif entity == "exercise":
            exercises.append(
                {
                    "stable_id": stable_id,
                    "parent_id": row.get("parent_id"),
                    "path": row.get("path"),
                    "order": row.get("order") if isinstance(row.get("order"), int) else 0,
                    "source_locator": row.get("source_locator"),
                    "title": _small_title(payload),
                    "exercise_number": payload.get("exercise_number"),
                    "family": payload.get("family"),
                }
            )
        elif entity == "solution":
            solutions[stable_id] = {
                "stable_id": stable_id,
                "parent_id": row.get("parent_id"),
                "path": row.get("path"),
                "order": row.get("order") if isinstance(row.get("order"), int) else 0,
                "source_locator": row.get("source_locator"),
                "title": _small_title(payload),
                "exercise_id": payload.get("exercise_id"),
            }
        elif entity == "relation":
            relation_type = payload.get("relation_type") or payload.get("predicate")
            if relation_type == "solves":
                solves.append((str(payload.get("subject_id")), str(payload.get("object_id"))))
            elif relation_type == "independently_solves_source_problem":
                independent[str(payload.get("subject_id"))] = str(payload.get("object_id"))
        elif entity == "resource" and isinstance(payload.get("source_reference"), dict) and payload["source_reference"].get("role") == "existing_public_source_solution":
            reference = payload["source_reference"]
            existing_mastery.append(
                {
                    "stable_id": stable_id,
                    "unit": int(reference["unit"]),
                    "anchor": reference["external_stable_id"],
                    "title": str(payload.get("title") or reference["external_stable_id"]),
                }
            )
        elif entity == "term":
            term_status[str(row.get("status"))] += 1
        elif entity == "correction":
            correction_status[str(row.get("status"))] += 1
        elif entity == "rights":
            license_value = payload.get("license") or payload.get("spdx") or row.get("status") or "unspecified"
            rights_licenses[str(license_value)] += 1
        elif entity == "qa_event" and "human_review_claimed" in payload:
            human_review_claims.add(bool(payload["human_review_claimed"]))
    actual_counts = dict(sorted(counts.items()))
    if actual_counts != EXPECTED_ENTITY_COUNTS[lane]:
        fail("D100-STREAM-ENTITY-COUNTS:" + lane)
    return {
        "counts": actual_counts,
        "language_counts": dict(sorted(language_counts.items())),
        "unit_by_path": unit_by_path,
        "exercises": exercises,
        "solutions": solutions,
        "solves": solves,
        "independent": independent,
        "existing_mastery": existing_mastery,
        "term_status": dict(sorted(term_status.items())),
        "correction_status": dict(sorted(correction_status.items())),
        "rights_licenses": dict(sorted(rights_licenses.items())),
        "human_review_claims": sorted(human_review_claims),
        "record_rows": sum(counts.values()),
    }


def public_url(lane: str, anchor: str) -> str:
    page = {"classical": "ak.html", "bgk": "bgk.html", "original": "companion.html"}[lane]
    return f"{PAGES_BASE}{page}#{quote(anchor, safe='-._~:')}"


def source_paths(lane: str, number: int) -> tuple[str, str, str]:
    if lane == "classical":
        return (
            f"source/en/lecture-{number:02d}.md",
            f"source/en/worksheet-{number:02d}.md",
            f"source/en/worksheet-{number:02d}-solutions.md",
        )
    return (
        f"source/en/bgk/lecture-{number:02d}.md",
        f"source/en/bgk/worksheet-{number:02d}.md",
        f"source/en/bgk/worksheet-{number:02d}-solutions.md",
    )


def root_id(lane: str, number: int, kind: str) -> str:
    if lane == "classical":
        prefix = "br-ak-2025-2026" if number <= 23 else "br-ak-2012"
        suffix = {"lecture": f"l{number:02d}", "worksheet": f"w{number:02d}", "solutions": f"w{number:02d}-solutions"}[kind]
        return f"{prefix}-{suffix}"
    suffix = {"lecture": f"l{number:02d}", "worksheet": f"w{number:02d}", "solutions": f"w{number:02d}-solutions"}[kind]
    return f"br-bgk-2019-{suffix}"


def _solution_maps(scans: dict[str, dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {"classical": {}, "bgk": {}, "original": {}}
    classical = scans["classical"]
    exercise_ids = {row["stable_id"] for row in classical["exercises"]}
    for subject, obj in classical["solves"]:
        if subject in classical["solutions"] and obj in exercise_ids:
            result["classical"][obj] = classical["solutions"][subject]
    for lane in ("bgk", "original"):
        exercise_ids = {row["stable_id"] for row in scans[lane]["exercises"]}
        for solution in scans[lane]["solutions"].values():
            exercise_id = solution.get("exercise_id")
            if exercise_id in exercise_ids:
                result[lane][str(exercise_id)] = solution
    if {lane: len(rows) for lane, rows in result.items()} != {"classical": 122, "bgk": 25, "original": 13}:
        fail("D100-SOLUTION-LINK-COUNTS")
    return result


def support_missing(anchor: str, label: str) -> dict[str, Any]:
    return {"status": "not_present", "source_anchor": anchor, "label": label, "href": None}


def exercise_projection(
    lane: str,
    unit_id: str,
    unit_number: int | None,
    rows: list[dict[str, Any]],
    solutions: dict[str, dict[str, Any]],
    negative_anchor: str,
) -> list[dict[str, Any]]:
    projected = []
    for sequence, row in enumerate(sorted(rows, key=lambda item: (item["order"], item["stable_id"])), 1):
        stable_id = row["stable_id"]
        anchor = str(row.get("parent_id") or str(row.get("source_locator", "")).split("#")[-1] or stable_id)
        if lane == "classical":
            number = row.get("exercise_number")
            title = f"Exercise {unit_number}.{number}" if number is not None else f"Exercise {stable_id}"
            kind = "classical_source_exercise"
            curriculum_status = "source"
        elif lane == "bgk":
            title = row.get("title") or f"BGK exercise {unit_number}.{sequence}"
            kind = "bgk_source_exercise"
            curriculum_status = "source"
        else:
            title = row.get("title") or stable_id
            kind = "editorial_capstone" if "capstone" in stable_id else "editorial_integrative_problem"
            curriculum_status = "editorial_companion"
        solution = solutions.get(stable_id)
        if solution:
            solution_anchor = str(solution.get("parent_id") or str(solution.get("source_locator", "")).split("#")[-1] or solution["stable_id"])
            solution_support = {
                "status": "complete",
                "source_anchor": solution["stable_id"],
                "label": "Complete public solution",
                "href": public_url(lane, solution_anchor),
            }
        else:
            solution_support = support_missing(negative_anchor, "No public source solution")
        projected.append(
            {
                "id": stable_id,
                "unit_id": unit_id,
                "title": title,
                "kind": kind,
                "sequence": sequence,
                "curriculum_status": curriculum_status,
                "href": public_url(lane, anchor),
                "hint": support_missing(stable_id, "No separate native hint entity proven"),
                "check": support_missing(stable_id, "No separate native check entity proven"),
                "solution": solution_support,
            }
        )
    return projected


def build_source_unit(
    lane: str,
    number: int,
    sequence: int,
    scan: dict[str, Any],
    solution_map: dict[str, dict[str, Any]],
    previous: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = source_paths(lane, number)
    unit_id = f"D100:{'AK' if lane == 'classical' else 'BGK'}:{number:02d}"
    section_rows = []
    for path in paths:
        section_rows.extend(row for row in scan["unit_by_path"].get(path, []) if row.get("language") == "en")
    sections = [row["stable_id"] for row in sorted(section_rows, key=lambda item: (paths.index(item["path"]), item["order"], item["stable_id"]))]
    roots = [root_id(lane, number, kind) for kind in ("lecture", "worksheet", "solutions")]
    if not all(root in sections for root in roots):
        fail(f"D100-SOURCE-ROOT:{lane}:{number}")
    worksheet = paths[1]
    rows = [row for row in scan["exercises"] if row.get("path") == worksheet]
    projected_exercises = exercise_projection(lane, unit_id, number, rows, solution_map, roots[2])
    title_candidates = [row["title"] for row in section_rows if row.get("title")]
    volume = "Algebraic Curves" if lane == "classical" else "Bundles, Sheaves and Cohomology"
    title = f"{volume} · Unit {number}"
    if title_candidates:
        first = title_candidates[0]
        if first.lower() not in title.lower():
            title = f"{title}: {first}"
    components = [
        {"id": root, "source": path, "license": "per-native-rights-record"}
        for root, path in zip(roots, paths)
    ]
    map_unit = {
        "id": unit_id,
        "title": title,
        "href": public_url(lane, roots[0]),
        "sections": sections,
        "objectives_href": None,
        "previous_units": previous,
        "components": components,
        "exercises": projected_exercises,
    }
    unit = {
        "schema": "d100-capability-unit/1",
        "unit_id": unit_id,
        "unit_type": "source_course_unit",
        "lane": lane,
        "locale": LOCALE,
        "sequence": sequence,
        "source_unit_number": number,
        "title_en": title,
        "target_url": map_unit["href"],
        "previous_units": previous,
        "native_component_ids": roots,
        "native_section_count": len(sections),
        "exercise_count": len(projected_exercises),
        "complete_solution_count": sum(row["solution"]["status"] == "complete" for row in projected_exercises),
    }
    return unit, map_unit


def build_companion_units(
    scan: dict[str, Any],
    source_order: list[dict[str, Any]],
    solution_map: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units = []
    map_units = []
    previous: list[str] = []
    for offset, source in enumerate(source_order, 61):
        path = source["path"]
        candidates = [row for row in scan["unit_by_path"].get(path, []) if row.get("language") == "en"]
        if len(candidates) != 1:
            fail("D100-COMPANION-UNIT-PATH:" + path)
        native = candidates[0]
        unit_id = native["stable_id"]
        unit_type = "editorial_mastery_bank" if native.get("unit_type") == "mastery_bank" else "editorial_connective_section"
        exercise_rows = [row for row in scan["exercises"] if row.get("path") == path]
        exercises = exercise_projection("original", unit_id, None, exercise_rows, solution_map, unit_id)
        title = native.get("title") or unit_id
        map_unit = {
            "id": unit_id,
            "title": title,
            "href": public_url("original", unit_id),
            "sections": [unit_id],
            "objectives_href": None,
            "previous_units": previous.copy(),
            "components": [{"id": unit_id, "source": path, "license": "per-native-rights-record"}],
            "exercises": exercises,
        }
        units.append(
            {
                "schema": "d100-capability-unit/1",
                "unit_id": unit_id,
                "unit_type": unit_type,
                "lane": "original",
                "locale": LOCALE,
                "sequence": offset,
                "title_en": title,
                "target_url": map_unit["href"],
                "previous_units": previous.copy(),
                "native_component_ids": [unit_id],
                "native_section_count": 1,
                "exercise_count": len(exercises),
                "complete_solution_count": sum(row["solution"]["status"] == "complete" for row in exercises),
            }
        )
        map_units.append(map_unit)
        previous = [unit_id]
    return units, map_units


def build_mastery(scan: dict[str, Any], solution_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    matched_exercise_solutions = {row["stable_id"] for row in solution_map.values()}
    rows = []
    for stable_id, resource_id in scan["independent"].items():
        solution = scan["solutions"].get(stable_id)
        if not solution or stable_id in matched_exercise_solutions:
            fail("D100-MASTERY-SOLUTION-IDENTITY:" + stable_id)
        match = re.search(r"mastery-bgk-(\d{2})", str(solution.get("path")))
        if not match:
            fail("D100-MASTERY-UNIT:" + stable_id)
        unit = int(match.group(1))
        anchor = str(solution.get("parent_id") or str(solution.get("source_locator", "")).split("#")[-1] or stable_id)
        rows.append(
            {
                "schema": "d100-mastery-route-item/1",
                "item_id": stable_id,
                "bgk_unit": unit,
                "kind": "new_editorial_solution",
                "source_authorship": "editorial",
                "source_problem_resource_id": resource_id,
                "source_solution_anchor": None,
                "title": solution.get("title") or stable_id,
                "href": public_url("original", anchor),
            }
        )
    for resource in scan["existing_mastery"]:
        rows.append(
            {
                "schema": "d100-mastery-route-item/1",
                "item_id": resource["stable_id"],
                "bgk_unit": resource["unit"],
                "kind": "existing_public_source_solution_reference",
                "source_authorship": "source",
                "source_problem_resource_id": None,
                "source_solution_anchor": resource["anchor"],
                "title": resource["title"],
                "href": public_url("bgk", resource["anchor"]),
            }
        )
    rows.sort(key=lambda row: (row["bgk_unit"], row["kind"], row["item_id"]))
    per_unit: Counter[int] = Counter(row["bgk_unit"] for row in rows)
    if (
        len(rows) != EXPECTED_MASTERY_ITEMS
        or sum(row["kind"] == "new_editorial_solution" for row in rows) != EXPECTED_NEW_MASTERY_SOLUTIONS
        or sum(row["kind"] == "existing_public_source_solution_reference" for row in rows) != EXPECTED_EXISTING_MASTERY_SOLUTIONS
        or set(per_unit) != set(EXPECTED_CONCENTRATED_UNITS)
        or any(value != 3 for value in per_unit.values())
    ):
        fail("D100-MASTERY-COUNTS")
    seen_unit: Counter[int] = Counter()
    for sequence, row in enumerate(rows, 1):
        seen_unit[row["bgk_unit"]] += 1
        row["sequence"] = sequence
        row["sequence_in_unit"] = seen_unit[row["bgk_unit"]]
    return rows


def build_routes(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routes = [
        {
            "schema": "d100-capability-route/1",
            "route_id": f"D100:route:unit:{row['unit_id']}",
            "route_type": "unit",
            "unit_id": row["unit_id"],
            "target_url": row["target_url"],
        }
        for row in units
    ]
    full_ids = [f"D100:AK:{number:02d}" for number in range(1, 31)] + [f"D100:BGK:{number:02d}" for number in range(1, 31)]
    routes.append({"schema": "d100-capability-route/1", "route_id": "D100:route:full-60", "route_type": "course_sequence", "unit_ids": full_ids})
    routes.append({"schema": "d100-capability-route/1", "route_id": "D100:route:bgk-19", "route_type": "concentrated_mastery", "source_units": list(EXPECTED_CONCENTRATED_UNITS), "unit_ids": [f"D100:BGK:{number:02d}" for number in EXPECTED_CONCENTRATED_UNITS]})
    routes.append({"schema": "d100-capability-route/1", "route_id": "D100:route:companion-32", "route_type": "editorial_companion", "unit_ids": [row["unit_id"] for row in units if row["lane"] == "original"]})
    return routes


def build_public_evidence(control: dict[str, Any]) -> dict[str, Any]:
    assets = []
    for row in control["github_manifest"]["assets"]:
        name = row["name"]
        assets.append(
            {
                "name": name,
                "bytes": row["bytes"],
                "sha256": row["sha256"],
                "content_type": row["content_type"],
                "url": RELEASE_BASE + quote(name),
            }
        )
    return {
        "schema": "d100-capability-public-evidence/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "github": {
            "commit": SOURCE_COMMIT,
            "release_tag": "en-v1.0.0",
            "release_url": RELEASE_PAGE,
            "anonymous_verification": "verified",
            "raw_files": "768/768",
            "release_assets": "13/13",
            "pages_resources": "474/474",
        },
        "zenodo": {
            "reservation_or_declaration_observed": True,
            "anonymous_public_readback": False,
            "claim_boundary": "No Zenodo publication or public-byte claim is made by this adapter.",
        },
        "readers": [
            {
                "book": row["book"],
                "page_count": row["page_count"],
                "name": row["output_name"],
                "bytes": row["input"]["bytes"],
                "sha256": row["input"]["sha256"],
                "url": RELEASE_BASE + quote(row["output_name"]),
            }
            for row in control["bindings"]["readers"]
        ],
        "release_assets": assets,
    }


def build_ledgers(scans: dict[str, dict[str, Any]], roles: dict[str, dict[str, Any]], control: dict[str, Any], section_count: int) -> dict[str, Any]:
    manifests = control["manifests"]
    return {
        "schema": "d100-capability-ledger-references/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "projection": "reference_only",
        "native_bodies_copied": False,
        "strict_source_profile_promoted": False,
        "entity_counts": {lane: scans[lane]["counts"] for lane in ("classical", "bgk", "original")},
        "total_record_rows": sum(scans[lane]["record_rows"] for lane in scans),
        "native_unit_records": sum(scans[lane]["counts"].get("unit", 0) for lane in scans),
        "projected_native_section_ids": section_count,
        "correction_records": sum(scans[lane]["counts"].get("correction", 0) for lane in scans),
        "term_records": sum(scans[lane]["counts"].get("term", 0) for lane in scans),
        "rights_records": sum(scans[lane]["counts"].get("rights", 0) for lane in scans),
        "classical_provisional_terms": scans["classical"]["term_status"].get("provisional", 0),
        "term_status_counts": {lane: scans[lane]["term_status"] for lane in scans},
        "correction_status_counts": {lane: scans[lane]["correction_status"] for lane in scans},
        "rights_license_counts": {lane: scans[lane]["rights_licenses"] for lane in scans},
        "language_counts": {lane: scans[lane]["language_counts"] for lane in scans},
        "profiles": [
            {
                "lane": lane,
                "records": {"path": roles[f"{lane}_records"]["path"], "bytes": roles[f"{lane}_records"]["bytes"], "sha256": roles[f"{lane}_records"]["sha256"]},
                "current_edition_native_id": manifests[lane]["common"]["current_edition_native_id"],
                "native_id_count": manifests[lane]["common"]["native_id_count"],
                "global_id_count": manifests[lane]["common"]["closure"]["global_id_count"],
                "native_reverse_equal": manifests[lane]["common"]["native_reverse_equal"],
                "profile_bound": manifests[lane]["common"].get("profile_bound", 0),
                "strict_source_profile": "not_promoted",
            }
            for lane in ("classical", "bgk", "original")
        ],
        "native_record_envelope": "ag-bridge-backend-record/1.0.0",
        "record_classes": sorted({entity for counts in EXPECTED_ENTITY_COUNTS.values() for entity in counts}),
    }


def build_course() -> dict[str, Any]:
    return {
        "schema": "d100-capability-course/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "central_course_truth_locale": "id-ID",
        "central_locale_rewritten": False,
        "contract_2_3_1_conformance": "not_claimed",
        "title_en": "Algebraic Geometry: Curves, Sheaves and Schemes",
        "native_dataset": NATIVE_DATASET,
        "source_course_units": 60,
        "companion_navigation_units": 32,
        "architecture": "30 classical units followed by 30 BGK units; companion remains a separate nonduplicating view",
        "release": {"tag": "en-v1.0.0", "commit": SOURCE_COMMIT, "url": RELEASE_PAGE},
        "current_editions": {
            "classical": "edition.algebraic-geometry-bridge-id.units-01-30.2026-08-28",
            "bgk": "edition.bgk-id.units-01-30.2026-08-31",
            "original": "edition.d100.original-bridge.2026-08-31",
        },
    }


def build_capabilities() -> dict[str, Any]:
    return {
        "schema": "d100-capability-summary/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "unit_navigation": {"source_course_units": 60, "companion_units": 32, "full_route": True, "concentrated_route_units": 19},
        "exercise_bank": {"source_exercises": 1188, "companion_exercises": 13, "total_exercises": 1201},
        "solution_coverage": {"source_solutions": 147, "negative_source_solution_states": 1041, "companion_exercise_solutions": 13},
        "mastery_route": {"items": 57, "new_editorial_solutions": 44, "existing_public_source_solution_references": 13},
        "concepts": 894,
        "terms": 905,
        "corrections": 371,
        "rights": {"records": 149, "per_component": True, "blanket_license_claimed": False},
        "accessibility": {"responsive_reader_qa": True, "native_mathml": False, "wcag_conformance_claimed": False, "tagged_pdf_claimed": False, "assistive_technology_user_tested": False},
        "labs": {"count": 0, "runtime_environments": 0},
        "human_review_claimed": False,
        "deterministic_native_translation_qa": True,
        "deterministic_adapter_replay": True,
    }


def build_learning_map(map_units: list[dict[str, Any]], public: dict[str, Any]) -> dict[str, Any]:
    prerequisites = [
        {
            "id": f"route:D100:prerequisite:{course}",
            "unit": "D100:AK:01",
            "prerequisite": course,
            "required_for_course": True,
            "sections": [],
            "exercises": [],
            "href": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/{course}/",
        }
        for course in EXPECTED_PREREQUISITES
    ]
    prerequisites.append(
        {
            "id": "route:D100:AK-before-BGK",
            "unit": "D100:BGK:01",
            "prerequisite": "D100:AK:30",
            "required_for_course": True,
            "sections": [],
            "exercises": [],
            "href": public_url("bgk", "br-bgk-2019-l01"),
        }
    )
    artifacts = [
        {"id": f"artifact:github-release:{index:02d}", "kind": row["content_type"], "path": row["url"]}
        for index, row in enumerate(public["release_assets"], 1)
    ]
    limitations = [
        "This is an English-release adapter; it does not rewrite or complete the central id-ID course truth.",
        "The projection is zero-copy and cannot reconstruct native mathematical bodies or bytes.",
        "Native stable identities are preserved as components and sections; 60 adapter aggregate IDs are collection identities, not renamed native records.",
        "The 44 new mastery solutions are editorial material, not source-authored solutions; 13 mastery items only reference existing public source solutions.",
        "Exactly 1,041 source exercises have an explicit no-public-source-solution state.",
        "Rights remain per native record and component; no course-wide umbrella licence is asserted.",
        "Native reverse equality does not establish strict source-profile reversibility, which is not claimed.",
        "Responsive rendering is verified, but native MathML, tagged PDF, WCAG conformance and assistive-technology user testing are not claimed.",
        "No human review, executable labs or runtime environments are claimed.",
        "The Stacks Project is a downstream reference, not translated source material.",
        "GitHub and Pages public readback is verified; Zenodo reservation or declaration evidence is not treated as anonymous public-byte readback.",
    ]
    return {
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "native_dataset": NATIVE_DATASET,
        "source_catalog": {
            "path": "backend/english/release-en-v1.0.0/index/common.dataset.json",
            "bytes": 3984,
            "sha256": DATASET_SHA256,
            "url": f"https://raw.githubusercontent.com/KokunoYumeto/algebraic-geometry-bridge-id/{SOURCE_COMMIT}/backend/english/release-en-v1.0.0/index/common.dataset.json",
        },
        "units": map_units,
        "prerequisite_routes": prerequisites,
        "labs": [],
        "environments": [],
        "artifacts": artifacts,
        "sources": [
            {"id": "source:classical-brenner", "role": "translated_source_volume", "license": "per-native-rights-record", "identity": "edition.algebraic-geometry-bridge-id.units-01-30.2026-08-28"},
            {"id": "source:bgk-brenner-wikiversity", "role": "translated_source_volume", "license": "per-native-rights-record", "identity": "edition.bgk-id.units-01-30.2026-08-31"},
            {"id": "source:d100-original-companion", "role": "independent_editorial_companion", "license": "per-native-rights-record", "identity": "edition.d100.original-bridge.2026-08-31"},
            {"id": "source:stacks-project", "role": "downstream_reference", "license": "external-reference-rights-retained", "identity": "The Stacks Project"},
        ],
        "external_relation_nodes": ["D70", "D80", "C90", "D60", "Stacks Project"],
        "limitations": limitations,
    }


def style() -> str:
    return """
:root{color-scheme:light dark;--bg:#f6f2e8;--ink:#211b17;--card:#fffaf0;--line:#b99b6b;--accent:#6b2f22;--ok:#1d6a45;--muted:#6f655d}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:2rem}header{border-bottom:3px solid var(--accent);margin-bottom:1rem}.lede{font-size:1.1rem;max-width:78ch}.facts,.controls{display:flex;gap:.7rem;flex-wrap:wrap;margin:1rem 0}.badge{border:1px solid var(--line);border-radius:999px;padding:.25rem .65rem;background:var(--card)}input,select{font:inherit;padding:.5rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:1rem}.card{background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:1rem}.id{font:12px ui-monospace,monospace;overflow-wrap:anywhere}.ok{color:var(--ok)}.missing{color:var(--muted)}details{margin:.6rem 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:var(--card)}th,td{border:1px solid var(--line);padding:.45rem;text-align:left;vertical-align:top}.warning{border-left:5px solid var(--accent);padding:.7rem 1rem;background:var(--card)}a{color:var(--accent)}[hidden]{display:none!important}@media(prefers-color-scheme:dark){:root{--bg:#171411;--ink:#f4ead7;--card:#241f1a;--line:#806846;--accent:#f0a58c;--ok:#83d6ab;--muted:#b9aa9d}}
"""


def exercise_list(unit: dict[str, Any], educator: bool = False) -> str:
    rows = []
    for exercise in unit["exercises"]:
        solution = exercise["solution"]
        solution_html = (
            f'<a class="ok" href="{html.escape(solution["href"], quote=True)}">complete solution</a>'
            if solution["status"] == "complete"
            else '<span class="missing">no public source solution</span>'
        )
        tag = "tr" if educator else "li"
        if educator:
            rows.append(
                f'<tr data-exercise-id="{html.escape(exercise["id"], quote=True)}"><td class="id">{html.escape(exercise["id"])}</td><td>{html.escape(exercise["title"])}</td><td>{html.escape(exercise["curriculum_status"])}</td><td><a href="{html.escape(exercise["href"], quote=True)}">problem</a></td><td>{solution_html}</td></tr>'
            )
        else:
            rows.append(
                f'<li data-exercise-id="{html.escape(exercise["id"], quote=True)}"><a href="{html.escape(exercise["href"], quote=True)}">{html.escape(exercise["title"])}</a> · {solution_html}</li>'
            )
    return "".join(rows)


def learner_html(course: dict[str, Any], map_units: list[dict[str, Any]], unit_rows: list[dict[str, Any]], mastery: list[dict[str, Any]]) -> str:
    meta = {row["unit_id"]: row for row in unit_rows}
    cards = []
    for unit in map_units:
        row = meta[unit["id"]]
        exercises = exercise_list(unit)
        details = f'<details><summary>{len(unit["exercises"])} exercises</summary><ol>{exercises}</ol></details>' if unit["exercises"] else "<p>No exercise entity in this navigation unit.</p>"
        cards.append(
            f'<article class="card" data-unit-id="{html.escape(unit["id"], quote=True)}" data-lane="{row["lane"]}" data-kind="{row["unit_type"]}"><p class="id">{html.escape(unit["id"])}</p><h2><a href="{html.escape(unit["href"], quote=True)}">{html.escape(unit["title"])}</a></h2><p>{row["native_section_count"]} native section identities · {row["exercise_count"]} exercises · {row["complete_solution_count"]} complete solutions</p>{details}</article>'
        )
    mastery_items = "".join(
        f'<li data-mastery-id="{html.escape(row["item_id"], quote=True)}"><a href="{html.escape(row["href"], quote=True)}">BGK {row["bgk_unit"]}: {html.escape(row["title"])}</a> · {html.escape(row["kind"])}</li>'
        for row in mastery
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D100 · English learner hub</title><style>{style()}</style></head><body><main>
<header><p>D100 · locale=en · zero-copy common adapter</p><h1>{html.escape(course['title_en'])}</h1><p class="lede">A verified identity-and-route projection over the complete 30-unit classical volume, complete 30-unit BGK volume, and separate 32-unit editorial companion. The central id-ID course truth is not rewritten.</p></header>
<div class="facts"><span class="badge">60 source-course units</span><span class="badge">32 companion units</span><span class="badge">1,201 exercises</span><span class="badge">160 complete exercise solutions</span><span class="badge">1,041 explicit negative states</span></div>
<p><a href="D100-pengajar.html">Educator evidence view</a> · <a href="{RELEASE_PAGE}">English release assets</a> · <a href="{PAGES_BASE}">Native English reader hub</a></p>
<div class="controls"><label>Search <input id="q" type="search" autocomplete="off"></label><label>Volume <select id="lane"><option value="">All</option><option value="classical">Classical</option><option value="bgk">BGK</option><option value="original">Companion</option></select></label><label>Kind <select id="kind"><option value="">All</option><option value="source_course_unit">Source-course unit</option><option value="editorial_mastery_bank">Mastery bank</option><option value="editorial_connective_section">Connective section</option></select></label></div>
<div id="units" class="grid">{''.join(cards)}</div>
<section><h2>Concentrated 19-unit mastery route</h2><p>Fifty-seven items: 44 new editorial solutions and 13 references to existing public source solutions. These are not added to the source-exercise count.</p><ol>{mastery_items}</ol></section>
<section class="warning"><h2>Claim boundary</h2><p>No native MathML, tagged-PDF, WCAG, assistive-technology user testing, human review, executable lab, blanket licence, strict source-profile reversibility, or Zenodo public-byte readback claim is made.</p></section>
</main><script>const q=document.querySelector('#q'),lane=document.querySelector('#lane'),kind=document.querySelector('#kind'),cards=[...document.querySelectorAll('[data-unit-id]')];function f(){{const s=q.value.toLowerCase();for(const c of cards)c.hidden=!!((lane.value&&c.dataset.lane!==lane.value)||(kind.value&&c.dataset.kind!==kind.value)||(s&&!c.textContent.toLowerCase().includes(s)))}}q.addEventListener('input',f);lane.addEventListener('change',f);kind.addEventListener('change',f);</script></body></html>"""


def educator_html(course: dict[str, Any], map_units: list[dict[str, Any]], unit_rows: list[dict[str, Any]], mastery: list[dict[str, Any]], ledgers: dict[str, Any]) -> str:
    map_by_id = {row["id"]: row for row in map_units}
    unit_lines = []
    exercise_lines = []
    for row in unit_rows:
        unit = map_by_id[row["unit_id"]]
        components = ", ".join(unit_id for unit_id in row["native_component_ids"])
        unit_lines.append(
            f'<tr data-unit-id="{html.escape(row["unit_id"], quote=True)}"><td>{row["sequence"]}</td><td class="id">{html.escape(row["unit_id"])}</td><td>{html.escape(row["lane"])}</td><td>{html.escape(row["unit_type"])}</td><td>{row["native_section_count"]}</td><td>{row["exercise_count"]}</td><td>{row["complete_solution_count"]}</td><td class="id">{html.escape(components)}</td><td><a href="{html.escape(row["target_url"], quote=True)}">open</a></td></tr>'
        )
        exercise_lines.append(exercise_list(unit, educator=True))
    mastery_lines = "".join(
        f'<tr data-mastery-id="{html.escape(row["item_id"], quote=True)}"><td>{row["sequence"]}</td><td>{row["bgk_unit"]}</td><td class="id">{html.escape(row["item_id"])}</td><td>{html.escape(row["kind"])}</td><td>{html.escape(row["source_authorship"])}</td><td><a href="{html.escape(row["href"], quote=True)}">open</a></td></tr>'
        for row in mastery
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D100 · Educator evidence view</title><style>{style()}</style></head><body><main>
<header><p>D100 · educator alignment · locale=en</p><h1>{html.escape(course['title_en'])}</h1><p class="lede">This view consumes the same 92 unit identities and 1,201 exercise identities as the learner hub while exposing source/companion separation, support provenance, rights boundaries and native ledger counts.</p></header><p><a href="D100.html">Back to learner hub</a></p>
<section><h2>Native boundary</h2><p>{ledgers['total_record_rows']:,} streamed native rows; {ledgers['native_unit_records']:,} native unit records; {ledgers['correction_records']:,} corrections; {ledgers['term_records']:,} terms; {ledgers['rights_records']:,} rights records. Bodies remain in the native backend.</p></section>
<section class="warning"><h2>Solution and authorship boundary</h2><p>Source exercises: 1,188. Public source solutions: 147. Explicit no-public-source-solution states: 1,041. Companion integrative/capstone exercises: 13 with 13 complete solutions. The separate mastery route has 44 editorial solutions and 13 existing-source-solution references.</p></section>
<h2>Unit alignment</h2><div class="scroll"><table><thead><tr><th>#</th><th>ID</th><th>Lane</th><th>Kind</th><th>Sections</th><th>Exercises</th><th>Solutions</th><th>Native roots</th><th>Route</th></tr></thead><tbody>{''.join(unit_lines)}</tbody></table></div>
<h2>Mastery route provenance</h2><div class="scroll"><table><thead><tr><th>#</th><th>BGK</th><th>ID</th><th>Kind</th><th>Authorship</th><th>Route</th></tr></thead><tbody>{mastery_lines}</tbody></table></div>
<h2>Exercise support matrix</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Problem</th><th>Solution</th></tr></thead><tbody>{''.join(exercise_lines)}</tbody></table></div>
</main></body></html>"""


def tooling_inventory(project: Path, adapter: Path) -> list[dict[str, Any]]:
    paths = [
        project / "scripts/d100_capability_model_v1.py",
        project / "scripts/build_d100_capability_v1.py",
        project / "scripts/validate_d100_capability_v1.py",
        adapter / "README.md",
        adapter / "input/source-lock.json",
    ]
    paths.extend(sorted((adapter / "fixtures/negative").glob("*.json"), key=lambda item: item.name))
    result = []
    for path in paths:
        if not path.is_file():
            fail("D100-TOOLING-MISSING:" + str(path))
        result.append({"path": path.relative_to(project).as_posix(), **file_identity(path)})
    return result


def build(native: Path, output: Path, lock_path: Path) -> dict[str, Any]:
    lock = read_json(lock_path)
    roles = verify_lock(native, lock)
    control = verify_control_inputs(native, roles)
    scans = {
        lane: scan_lane(input_path(native, roles, f"{lane}_records"), lane)
        for lane in ("classical", "bgk", "original")
    }
    if sum(scan["record_rows"] for scan in scans.values()) != EXPECTED_TOTAL_RECORDS:
        fail("D100-NATIVE-ROW-TOTAL")
    solution_maps = _solution_maps(scans)

    units: list[dict[str, Any]] = []
    map_units: list[dict[str, Any]] = []
    for number in range(1, 31):
        previous = [] if number == 1 else [f"D100:AK:{number - 1:02d}"]
        unit, map_unit = build_source_unit("classical", number, number, scans["classical"], solution_maps["classical"], previous)
        units.append(unit)
        map_units.append(map_unit)
    for number in range(1, 31):
        previous = ["D100:AK:30"] if number == 1 else [f"D100:BGK:{number - 1:02d}"]
        unit, map_unit = build_source_unit("bgk", number, 30 + number, scans["bgk"], solution_maps["bgk"], previous)
        units.append(unit)
        map_units.append(map_unit)
    companion_units, companion_map_units = build_companion_units(
        scans["original"], control["input_maps"]["original"]["english_source_order"], solution_maps["original"]
    )
    units.extend(companion_units)
    map_units.extend(companion_map_units)
    if len(units) != EXPECTED_PROJECTED_UNITS:
        fail("D100-PROJECTED-UNIT-COUNT")

    exercises = [exercise for unit in map_units for exercise in unit["exercises"]]
    source_exercises = [row for row in exercises if row["curriculum_status"] == "source"]
    companion_exercises = [row for row in exercises if row["curriculum_status"] == "editorial_companion"]
    source_solutions = [row for row in source_exercises if row["solution"]["status"] == "complete"]
    negatives = [row for row in source_exercises if row["solution"]["status"] == "not_present"]
    if (
        len(exercises) != EXPECTED_EXERCISES
        or len(source_exercises) != EXPECTED_SOURCE_EXERCISES
        or len(companion_exercises) != EXPECTED_COMPANION_EXERCISES
        or len(source_solutions) != EXPECTED_SOURCE_SOLUTIONS
        or len(negatives) != EXPECTED_NEGATIVE_SOLUTIONS
        or any(row["solution"]["status"] != "complete" for row in companion_exercises)
    ):
        fail("D100-PROJECTED-EXERCISE-COUNTS")

    mastery = build_mastery(scans["original"], solution_maps["original"])
    routes = build_routes(units)
    public = build_public_evidence(control)
    section_count = len({section for unit in map_units for section in unit["sections"]})
    ledgers = build_ledgers(scans, roles, control, section_count)
    course = build_course()
    capabilities = build_capabilities()
    learning_map = build_learning_map(map_units, public)

    write_json(output / "data/course.json", course)
    write_json(output / "data/capabilities.json", capabilities)
    write_json(output / "data/learning-map.json", learning_map)
    write_jsonl(output / "data/units.jsonl", units)
    write_jsonl(output / "data/routes.jsonl", routes)
    write_jsonl(output / "data/mastery-routes.jsonl", mastery)
    write_json(output / "data/ledger-references.json", ledgers)
    write_json(output / "data/public-evidence.json", public)
    write_bytes(output / "views/D100.html", learner_html(course, map_units, units, mastery).encode("utf-8"))
    write_bytes(output / "views/D100-pengajar.html", educator_html(course, map_units, units, mastery, ledgers).encode("utf-8"))

    generated_paths = [
        "data/capabilities.json",
        "data/course.json",
        "data/learning-map.json",
        "data/ledger-references.json",
        "data/mastery-routes.jsonl",
        "data/public-evidence.json",
        "data/routes.jsonl",
        "data/units.jsonl",
        "views/D100-pengajar.html",
        "views/D100.html",
    ]
    outputs = [{"path": relative, **file_identity(output / relative)} for relative in generated_paths]
    output_tree_sha256 = sha256_bytes(b"".join(canonical_json(row) for row in sorted(outputs, key=lambda row: row["path"])))
    manifest = {
        "schema": "d100-capability-manifest/1",
        "contract": CONTRACT,
        "contract_projection_path": "data/learning-map.json",
        "contract_2_3_1_conformance": "not_claimed",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "central_course_truth_locale": "id-ID",
        "native_family": "algebraic_geometry",
        "native_release": "en-v1.0.0",
        "counts": {
            "native_record_rows": 46624,
            "native_unit_records": 2154,
            "source_course_units": 60,
            "companion_units": 32,
            "projected_units": 92,
            "source_exercises": 1188,
            "companion_exercises": 13,
            "source_solutions": 147,
            "companion_exercise_solutions": 13,
            "negative_source_solutions": 1041,
            "mastery_route_items": 57,
            "new_editorial_mastery_solutions": 44,
            "existing_public_mastery_source_solutions": 13,
        },
        "projection": {
            "zero_copy": True,
            "native_ids_preserved": True,
            "aggregate_unit_ids_are_adapter_collection_identities": True,
            "native_bodies_copied": False,
            "strict_source_profile_reversibility_claimed": False,
            "central_id_id_truth_rewritten": False,
            "public_state_changed": False,
        },
        "inputs": lock["inputs"],
        "tooling": tooling_inventory(PROJECT, DEFAULT_ADAPTER),
        "outputs": outputs,
        "output_tree_sha256": output_tree_sha256,
        "public_release_status": "unchanged_verified_github_pages_reference_only",
    }
    write_json(output / "manifest.json", manifest)
    semantic_errors = validate_bundle(load_bundle(output))
    if semantic_errors:
        fail("D100-BUILT-MODEL-INVALID:" + ",".join(semantic_errors))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--source-lock", type=Path, default=DEFAULT_ADAPTER / "input/source-lock.json")
    parser.add_argument("--refresh-source-lock", action="store_true")
    args = parser.parse_args()
    native = args.native_root.resolve()
    output = args.output_root.resolve()
    lock_path = args.source_lock.resolve()
    if args.refresh_source_lock:
        refresh_source_lock(native, lock_path)
    if not lock_path.is_file():
        fail("D100-SOURCE-LOCK-MISSING")
    manifest = build(native, output, lock_path)
    print(json.dumps({"state": "pass", "course_id": COURSE_ID, "locale": LOCALE, "output_root": str(output), "output_tree_sha256": manifest["output_tree_sha256"], "counts": manifest["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (D100Error, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"D100 build failed: {exc}", file=sys.stderr)
        sys.exit(1)
