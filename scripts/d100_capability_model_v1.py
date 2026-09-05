"""Shared model and invariants for the D100 English capability adapter.

The adapter is deliberately zero-copy: the large native JSONL streams stay in
the algebraic-geometry repository.  Only stable identities, routes, counts and
support/provenance facts enter the common projection.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Iterator


CONTRACT = "course-learning-capability/1"
COURSE_ID = "D100"
LOCALE = "en"
DATASET_SHA256 = "0bce141ce2a5724f2cf63588d20741e4e1be35ef29a379aa064c0d43dc4913bc"
NATIVE_DATASET = f"d100-en-native-backend-index-v1@sha256:{DATASET_SHA256}"
SOURCE_COMMIT = "93dbf3b19907e9e13d42c8e342b449ebd0afc635"
PAGES_BASE = "https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/en/"
RELEASE_BASE = (
    "https://github.com/KokunoYumeto/algebraic-geometry-bridge-id/"
    "releases/download/en-v1.0.0/"
)
RELEASE_PAGE = (
    "https://github.com/KokunoYumeto/algebraic-geometry-bridge-id/"
    "releases/tag/en-v1.0.0"
)

EXPECTED_ENTITY_COUNTS = {
    "classical": {
        "artifact": 247,
        "asset": 101,
        "concept": 274,
        "correction": 159,
        "course": 1,
        "edition": 19,
        "exercise": 693,
        "program": 1,
        "qa_event": 65,
        "relation": 12053,
        "resource": 4,
        "rights": 106,
        "segment": 8162,
        "solution": 122,
        "term": 276,
        "unit": 1586,
    },
    "bgk": {
        "artifact": 595,
        "asset": 9,
        "concept": 620,
        "correction": 212,
        "course": 1,
        "edition": 39,
        "exercise": 495,
        "program": 1,
        "qa_event": 102,
        "relation": 10849,
        "resource": 32,
        "rights": 40,
        "segment": 7506,
        "solution": 25,
        "term": 629,
        "unit": 536,
    },
    "original": {
        "artifact": 32,
        "course": 1,
        "edition": 1,
        "exercise": 13,
        "qa_event": 6,
        "relation": 560,
        "resource": 198,
        "rights": 3,
        "segment": 161,
        "solution": 57,
        "unit": 32,
    },
}
EXPECTED_TOTAL_RECORDS = 46624
EXPECTED_NATIVE_UNITS = 2154
EXPECTED_SOURCE_UNITS = 60
EXPECTED_COMPANION_UNITS = 32
EXPECTED_PROJECTED_UNITS = 92
EXPECTED_SOURCE_EXERCISES = 1188
EXPECTED_COMPANION_EXERCISES = 13
EXPECTED_EXERCISES = 1201
EXPECTED_SOURCE_SOLUTIONS = 147
EXPECTED_COMPANION_EXERCISE_SOLUTIONS = 13
EXPECTED_COMPLETE_EXERCISE_SOLUTIONS = 160
EXPECTED_NEGATIVE_SOLUTIONS = 1041
EXPECTED_MASTERY_ITEMS = 57
EXPECTED_NEW_MASTERY_SOLUTIONS = 44
EXPECTED_EXISTING_MASTERY_SOLUTIONS = 13
EXPECTED_CONCENTRATED_UNITS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 23, 24, 25, 26, 27)
EXPECTED_PREREQUISITES = ("D70", "D80", "C90", "D60")
EXPECTED_NEGATIVE_FIXTURES = 14


class D100Error(ValueError):
    """A stable-code D100 adapter error."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            size += len(chunk)
            digest.update(chunk)
    return {"bytes": size, "sha256": digest.hexdigest()}


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        for row in rows:
            handle.write(canonical_json_line(row))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise D100Error(f"D100-JSONL-OBJECT:{path}:{line_number}")
            yield value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def load_bundle(output_root: Path) -> dict[str, Any]:
    return {
        "course": read_json(output_root / "data/course.json"),
        "capabilities": read_json(output_root / "data/capabilities.json"),
        "learning_map": read_json(output_root / "data/learning-map.json"),
        "units": read_jsonl(output_root / "data/units.jsonl"),
        "routes": read_jsonl(output_root / "data/routes.jsonl"),
        "mastery": read_jsonl(output_root / "data/mastery-routes.jsonl"),
        "ledgers": read_json(output_root / "data/ledger-references.json"),
        "public_evidence": read_json(output_root / "data/public-evidence.json"),
        "manifest": read_json(output_root / "manifest.json"),
    }


def _add(errors: list[str], condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)


def _exercise_rows(learning_map: dict[str, Any]) -> list[dict[str, Any]]:
    return [exercise for unit in learning_map.get("units", []) for exercise in unit.get("exercises", [])]


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Return stable semantic error codes without touching the native corpus."""

    errors: list[str] = []
    course = bundle["course"]
    capabilities = bundle["capabilities"]
    learning_map = bundle["learning_map"]
    units = bundle["units"]
    routes = bundle["routes"]
    mastery = bundle["mastery"]
    ledgers = bundle["ledgers"]
    public = bundle["public_evidence"]
    manifest = bundle["manifest"]

    _add(errors, course.get("schema") == "d100-capability-course/1", "D100-COURSE-SCHEMA")
    _add(errors, "contract" not in course, "D100-CONTRACT-COLLISION")
    _add(errors, course.get("course_id") == COURSE_ID and course.get("locale") == LOCALE, "D100-COURSE-IDENTITY")
    _add(errors, course.get("central_course_truth_locale") == "id-ID", "D100-CENTRAL-LOCALE-BOUNDARY")
    _add(errors, course.get("contract_2_3_1_conformance") == "not_claimed", "D100-V231-CLAIM")
    _add(errors, course.get("release", {}).get("tag") == "en-v1.0.0", "D100-RELEASE-IDENTITY")
    _add(errors, course.get("source_course_units") == 60, "D100-STALE-BGK-BOUNDARY")

    unit_ids = [row.get("unit_id") for row in units]
    source_units = [row for row in units if row.get("unit_type") == "source_course_unit"]
    mastery_units = [row for row in units if row.get("unit_type") == "editorial_mastery_bank"]
    connective_units = [row for row in units if row.get("unit_type") == "editorial_connective_section"]
    _add(errors, len(units) == EXPECTED_PROJECTED_UNITS, "D100-UNIT-COUNT")
    _add(errors, len(set(unit_ids)) == len(unit_ids), "D100-UNIT-ID-DUPLICATE")
    _add(errors, [row.get("sequence") for row in units] == list(range(1, 93)), "D100-UNIT-SEQUENCE")
    _add(errors, len(source_units) == 60 and len(mastery_units) == 17 and len(connective_units) == 15, "D100-UNIT-TYPE-COUNTS")
    _add(errors, all(row.get("locale") == "en" for row in units), "D100-UNIT-LOCALE")

    required_map_keys = {
        "contract", "course_id", "locale", "native_dataset", "source_catalog", "units",
        "prerequisite_routes", "labs", "environments", "artifacts", "sources",
        "external_relation_nodes", "limitations",
    }
    _add(errors, set(learning_map) == required_map_keys, "D100-LEARNING-MAP-SHAPE")
    _add(
        errors,
        learning_map.get("contract") == CONTRACT
        and learning_map.get("course_id") == COURSE_ID
        and learning_map.get("locale") == LOCALE
        and learning_map.get("native_dataset") == NATIVE_DATASET,
        "D100-LEARNING-MAP-CONTRACT",
    )
    catalog = learning_map.get("source_catalog", {})
    _add(
        errors,
        catalog.get("bytes") == 3984
        and catalog.get("sha256") == DATASET_SHA256
        and catalog.get("path") == "backend/english/release-en-v1.0.0/index/common.dataset.json",
        "D100-SOURCE-CATALOG",
    )
    map_units = learning_map.get("units", [])
    _add(errors, len(map_units) == EXPECTED_PROJECTED_UNITS, "D100-LEARNING-MAP-UNIT-COUNT")
    _add(errors, {row.get("id") for row in map_units} == set(unit_ids), "D100-LEARNING-MAP-UNIT-IDS")
    unit_keys = {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"}
    exercise_keys = {"id", "unit_id", "title", "kind", "sequence", "curriculum_status", "href", "hint", "check", "solution"}
    support_keys = {"status", "source_anchor", "label", "href"}
    section_ids: list[str] = []
    for unit in map_units:
        _add(errors, set(unit) == unit_keys, "D100-LEARNING-MAP-UNIT-SHAPE")
        _add(errors, isinstance(unit.get("href"), str) and unit["href"].startswith("https://"), "D100-UNIT-HREF")
        _add(errors, unit.get("objectives_href") is None, "D100-OBJECTIVES-CLAIM")
        sections = unit.get("sections", [])
        _add(errors, len(sections) == len(set(sections)), "D100-NATIVE-SECTION-ID-DUPLICATE")
        section_ids.extend(sections)
        for component in unit.get("components", []):
            _add(errors, {"id", "source", "license"}.issubset(component), "D100-COMPONENT-SHAPE")
            _add(errors, component.get("license") == "per-native-rights-record", "D100-BLANKET-LICENSE")
        for exercise in unit.get("exercises", []):
            _add(errors, set(exercise) == exercise_keys, "D100-EXERCISE-SHAPE")
            _add(errors, exercise.get("unit_id") == unit.get("id"), "D100-EXERCISE-UNIT")
            _add(errors, isinstance(exercise.get("href"), str) and exercise["href"].startswith("https://"), "D100-EXERCISE-HREF")
            for support_name in ("hint", "check", "solution"):
                support = exercise.get(support_name, {})
                _add(errors, set(support) == support_keys, "D100-SUPPORT-SHAPE")
                state = support.get("status")
                _add(errors, state in {"complete", "executable", "not_present", "pending"}, "D100-SUPPORT-STATE")
                _add(errors, (state in {"complete", "executable"}) == isinstance(support.get("href"), str), "D100-SUPPORT-HREF")
    _add(errors, len(section_ids) == len(set(section_ids)), "D100-NATIVE-SECTION-GLOBAL-DUPLICATE")

    exercises = _exercise_rows(learning_map)
    exercise_ids = [row.get("id") for row in exercises]
    source_exercises = [row for row in exercises if row.get("curriculum_status") == "source"]
    companion_exercises = [row for row in exercises if row.get("curriculum_status") == "editorial_companion"]
    complete_source = [row for row in source_exercises if row.get("solution", {}).get("status") == "complete"]
    complete_companion = [row for row in companion_exercises if row.get("solution", {}).get("status") == "complete"]
    negative = [row for row in source_exercises if row.get("solution", {}).get("status") == "not_present"]
    _add(errors, len(exercises) == EXPECTED_EXERCISES and len(set(exercise_ids)) == EXPECTED_EXERCISES, "D100-EXERCISE-COUNT")
    _add(errors, len(source_exercises) == EXPECTED_SOURCE_EXERCISES, "D100-SOURCE-EXERCISE-COUNT")
    _add(errors, len(companion_exercises) == EXPECTED_COMPANION_EXERCISES, "D100-COMPANION-EXERCISE-COUNT")
    _add(errors, len(complete_source) == EXPECTED_SOURCE_SOLUTIONS, "D100-SOURCE-SOLUTION-COUNT")
    _add(errors, len(complete_companion) == EXPECTED_COMPANION_EXERCISE_SOLUTIONS, "D100-COMPANION-SOLUTION-COUNT")
    _add(errors, len(negative) == EXPECTED_NEGATIVE_SOLUTIONS, "D100-NEGATIVE-SOLUTION-COUNT")
    _add(errors, all(row["hint"]["status"] == "not_present" and row["check"]["status"] == "not_present" for row in exercises), "D100-HINT-CHECK-CLAIM")

    route_ids = [row.get("route_id") for row in routes]
    _add(errors, len(routes) == 95 and len(set(route_ids)) == 95, "D100-ROUTE-COUNT")
    full = next((row for row in routes if row.get("route_id") == "D100:route:full-60"), {})
    concentrated = next((row for row in routes if row.get("route_id") == "D100:route:bgk-19"), {})
    companion_route = next((row for row in routes if row.get("route_id") == "D100:route:companion-32"), {})
    _add(errors, len(full.get("unit_ids", [])) == 60, "D100-FULL-ROUTE")
    _add(errors, concentrated.get("source_units") == list(EXPECTED_CONCENTRATED_UNITS), "D100-CONCENTRATED-ROUTE")
    _add(errors, len(companion_route.get("unit_ids", [])) == 32, "D100-COMPANION-ROUTE")

    mastery_ids = [row.get("item_id") for row in mastery]
    new_mastery = [row for row in mastery if row.get("kind") == "new_editorial_solution"]
    existing_mastery = [row for row in mastery if row.get("kind") == "existing_public_source_solution_reference"]
    per_unit = {unit: 0 for unit in EXPECTED_CONCENTRATED_UNITS}
    for row in mastery:
        if row.get("bgk_unit") in per_unit:
            per_unit[row["bgk_unit"]] += 1
    _add(errors, len(mastery) == EXPECTED_MASTERY_ITEMS and len(set(mastery_ids)) == EXPECTED_MASTERY_ITEMS, "D100-MASTERY-COUNT")
    _add(errors, len(new_mastery) == 44, "D100-EDITORIAL-MASTERY-COUNT")
    _add(errors, len(existing_mastery) == 13, "D100-EXISTING-MASTERY-COUNT")
    _add(errors, set(per_unit) == set(EXPECTED_CONCENTRATED_UNITS) and all(value == 3 for value in per_unit.values()), "D100-MASTERY-ROUTE-COVERAGE")
    _add(errors, all(row.get("source_authorship") == "editorial" for row in new_mastery), "D100-EDITORIAL-MASTERY-RETYPE")

    counts = ledgers.get("entity_counts", {})
    _add(errors, counts == EXPECTED_ENTITY_COUNTS, "D100-NATIVE-ENTITY-COUNTS")
    _add(errors, ledgers.get("total_record_rows") == EXPECTED_TOTAL_RECORDS, "D100-NATIVE-RECORD-TOTAL")
    _add(errors, ledgers.get("native_unit_records") == EXPECTED_NATIVE_UNITS, "D100-NATIVE-UNIT-TOTAL")
    _add(errors, ledgers.get("correction_records") == 371 and ledgers.get("term_records") == 905 and ledgers.get("rights_records") == 149, "D100-LEDGER-COUNTS")
    _add(errors, ledgers.get("classical_provisional_terms") == 4, "D100-PROVISIONAL-TERMS")
    _add(errors, ledgers.get("native_bodies_copied") is False, "D100-LEDGER-ZERO-COPY")
    _add(errors, ledgers.get("strict_source_profile_promoted") is False, "D100-STRICT-SOURCE-PROFILE")

    access = capabilities.get("accessibility", {})
    _add(errors, access.get("native_mathml") is False and access.get("wcag_conformance_claimed") is False and access.get("tagged_pdf_claimed") is False and access.get("assistive_technology_user_tested") is False, "D100-ACCESSIBILITY-CLAIM")
    _add(errors, capabilities.get("labs", {}).get("count") == 0, "D100-LAB-CLAIM")
    _add(errors, capabilities.get("rights", {}).get("blanket_license_claimed") is False, "D100-BLANKET-LICENSE")
    _add(errors, capabilities.get("human_review_claimed") is False, "D100-HUMAN-REVIEW-CLAIM")
    _add(errors, learning_map.get("labs") == [] and learning_map.get("environments") == [], "D100-LAB-ENVIRONMENT")

    stacks = next((row for row in learning_map.get("sources", []) if row.get("id") == "source:stacks-project"), {})
    _add(errors, stacks.get("role") == "downstream_reference", "D100-STACKS-SOURCE-ROLE")
    _add(errors, set(EXPECTED_PREREQUISITES).issubset(set(learning_map.get("external_relation_nodes", []))), "D100-PREREQUISITES")
    _add(errors, public.get("github", {}).get("anonymous_verification") == "verified", "D100-GITHUB-PUBLIC-EVIDENCE")
    _add(errors, public.get("zenodo", {}).get("anonymous_public_readback") is False, "D100-ZENODO-PUBLIC-CLAIM")
    _add(errors, len(public.get("release_assets", [])) == 13, "D100-PUBLIC-ASSET-COUNT")

    manifest_counts = manifest.get("counts", {})
    _add(errors, manifest.get("contract") == CONTRACT and manifest.get("course_id") == COURSE_ID, "D100-MANIFEST-CONTRACT")
    _add(errors, manifest.get("contract_projection_path") == "data/learning-map.json", "D100-MANIFEST-PROJECTION")
    _add(errors, manifest.get("contract_2_3_1_conformance") == "not_claimed", "D100-MANIFEST-V231")
    _add(
        errors,
        manifest_counts.get("source_course_units") == 60
        and manifest_counts.get("companion_units") == 32
        and manifest_counts.get("source_exercises") == 1188
        and manifest_counts.get("source_solutions") == 147
        and manifest_counts.get("negative_source_solutions") == 1041
        and manifest_counts.get("new_editorial_mastery_solutions") == 44,
        "D100-MANIFEST-COUNTS",
    )
    return sorted(set(errors))


def apply_negative_mutation(bundle: dict[str, Any], mutation: str) -> dict[str, Any]:
    changed = copy.deepcopy(bundle)
    if mutation == "duplicate_native_id":
        changed["learning_map"]["units"][0]["sections"].append(changed["learning_map"]["units"][0]["sections"][0])
    elif mutation == "drop_record_count":
        changed["ledgers"]["entity_counts"]["classical"]["exercise"] -= 1
    elif mutation == "stale_bgk_unit_06_boundary":
        changed["course"]["source_course_units"] = 36
    elif mutation == "collapse_source_and_companion_units":
        changed["units"][60]["unit_type"] = "source_course_unit"
    elif mutation == "claim_all_source_solutions":
        row = next(row for row in _exercise_rows(changed["learning_map"]) if row["curriculum_status"] == "source" and row["solution"]["status"] == "not_present")
        row["solution"] = {"status": "complete", "source_anchor": row["solution"]["source_anchor"], "label": "Invented", "href": row["href"]}
    elif mutation == "drop_negative_solution_state":
        row = next(row for row in _exercise_rows(changed["learning_map"]) if row["solution"]["status"] == "not_present")
        row["solution"]["status"] = "pending"
    elif mutation == "retype_editorial_mastery_as_source":
        row = next(row for row in changed["mastery"] if row["kind"] == "new_editorial_solution")
        row["source_authorship"] = "source"
    elif mutation == "inflate_exercise_count_with_mastery":
        exemplar = copy.deepcopy(changed["learning_map"]["units"][0]["exercises"][0])
        exemplar["id"] = changed["mastery"][0]["item_id"]
        changed["learning_map"]["units"][0]["exercises"].append(exemplar)
    elif mutation == "promote_strict_source_profile":
        changed["ledgers"]["strict_source_profile_promoted"] = True
    elif mutation == "blanket_license":
        changed["capabilities"]["rights"]["blanket_license_claimed"] = True
    elif mutation == "native_mathml_wcag_claim":
        changed["capabilities"]["accessibility"]["native_mathml"] = True
    elif mutation == "claim_zenodo_public_readback":
        changed["public_evidence"]["zenodo"]["anonymous_public_readback"] = True
    elif mutation == "stacks_as_translated_source":
        source = next(row for row in changed["learning_map"]["sources"] if row["id"] == "source:stacks-project")
        source["role"] = "translated_source"
    elif mutation == "nonempty_lab_environment":
        changed["learning_map"]["labs"] = [{"id": "invented", "unit": "D100:BGK:01", "environment": "invented", "exercise_ids": [], "artifact_ids": []}]
    else:
        raise D100Error(f"D100-UNKNOWN-NEGATIVE-MUTATION:{mutation}")
    return changed


def tree_identity(root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    rows = []
    for relative in sorted(relative_paths):
        rows.append({"path": relative.replace("\\", "/"), **file_identity(root / relative)})
    return {"files": rows, "sha256": sha256_bytes(b"".join(canonical_json_line(row) for row in rows))}
