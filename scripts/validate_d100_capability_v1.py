"""Strict validator for the D100 English course-learning capability adapter.

Validation is read-only except for the requested validation receipt. Native
JSONL streams are processed line by line; no TeX, publication or shared
authority operation is performed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from d100_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DATASET_SHA256,
    EXPECTED_CONCENTRATED_UNITS,
    EXPECTED_ENTITY_COUNTS,
    EXPECTED_EXERCISES,
    EXPECTED_NEGATIVE_FIXTURES,
    EXPECTED_NEGATIVE_SOLUTIONS,
    EXPECTED_PROJECTED_UNITS,
    EXPECTED_SOURCE_EXERCISES,
    EXPECTED_SOURCE_SOLUTIONS,
    EXPECTED_TOTAL_RECORDS,
    LOCALE,
    NATIVE_DATASET,
    D100Error,
    apply_negative_mutation,
    file_identity,
    iter_jsonl,
    load_bundle,
    read_json,
    tree_identity,
    validate_bundle,
    write_json,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d100-capability-v1"
DEFAULT_NATIVE = PROJECT.parent / "algebraic-geometry-bridge-id"
BUILD_SCRIPT = PROJECT / "scripts/build_d100_capability_v1.py"
EXPECTED_ROLES = {
    "index_manifest", "index_dataset",
    "classical_manifest", "classical_record_schema", "classical_records",
    "bgk_manifest", "bgk_record_schema", "bgk_records",
    "original_manifest", "original_record_schema", "original_records",
    "classical_input", "bgk_input", "original_input",
    "translation_qa", "reader_qa", "github_publication", "release_bindings",
    "github_release_manifest",
}


def fail(code: str) -> None:
    raise D100Error(code)


def require_uri(value: Any, code: str) -> None:
    if not isinstance(value, str) or urlsplit(value).scheme not in {"http", "https"}:
        fail(code)


def verify_locked_inputs(native: Path, lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if lock.get("schema") != "d100-capability-source-lock/1" or lock.get("course_id") != COURSE_ID or lock.get("locale") != LOCALE:
        fail("D100-VALIDATE-LOCK-SCHEMA")
    roles: dict[str, dict[str, Any]] = {}
    for row in lock.get("inputs", []):
        role = row.get("role")
        if role in roles:
            fail("D100-VALIDATE-LOCK-DUPLICATE-ROLE")
        path = native / str(row.get("path"))
        if not path.is_file() or file_identity(path) != {"bytes": row.get("bytes"), "sha256": row.get("sha256")}:
            fail("D100-VALIDATE-LOCK-DRIFT:" + str(row.get("path")))
        roles[str(role)] = row
    if set(roles) != EXPECTED_ROLES:
        fail("D100-VALIDATE-LOCK-ROLE-SET")
    return roles


def role_path(native: Path, roles: dict[str, dict[str, Any]], role: str) -> Path:
    return native / roles[role]["path"]


def verify_control_receipts(native: Path, roles: dict[str, dict[str, Any]]) -> None:
    index = read_json(role_path(native, roles, "index_dataset"))
    if index.get("schema") != "d100-en-native-backend-index-v1" or index.get("status") != "PASS":
        fail("D100-VALIDATE-INDEX")
    if {row["lane"]: row["entity_counts"] for row in index["lanes"]} != EXPECTED_ENTITY_COUNTS:
        fail("D100-VALIDATE-INDEX-COUNTS")
    if file_identity(role_path(native, roles, "index_dataset")) != {"bytes": 3984, "sha256": DATASET_SHA256}:
        fail("D100-VALIDATE-INDEX-IDENTITY")
    translation = read_json(role_path(native, roles, "translation_qa"))
    coverage = translation.get("coverage", {})
    if (
        translation.get("status") != "PASS"
        or translation.get("target_count") != 274
        or coverage.get("exercise_count") != 1188
        or coverage.get("public_solution_count") != 147
        or coverage.get("negative_solution_count") != 1041
        or coverage.get("terminal_bridge_file_count") != 32
    ):
        fail("D100-VALIDATE-TRANSLATION-QA")
    reader = read_json(role_path(native, roles, "reader_qa"))
    if reader.get("status") != "PASS" or not any("974 PDF pages" in item for item in reader.get("checks", [])):
        fail("D100-VALIDATE-READER-QA")
    publication = read_json(role_path(native, roles, "github_publication"))
    verification = publication.get("verification", {})
    if (
        publication.get("status") != "PASS"
        or publication.get("release", {}).get("asset_count") != 13
        or verification.get("anonymous_raw_files") != "PASS_768_OF_768"
        or verification.get("anonymous_release_inventory_and_assets") != "PASS_13_OF_13"
        or verification.get("anonymous_pages") != "PASS_474_OF_474"
    ):
        fail("D100-VALIDATE-PUBLICATION-QA")
    bindings = read_json(role_path(native, roles, "release_bindings"))
    if [row.get("page_count") for row in bindings.get("readers", [])] != [504, 381, 89]:
        fail("D100-VALIDATE-READER-PAGES")


def native_facts(native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    for lane in ("classical", "bgk", "original"):
        counts: Counter[str] = Counter()
        ids: set[str] = set()
        projected_unit_ids: set[str] = set()
        exercise_ids: set[str] = set()
        solution_ids: set[str] = set()
        linked_solution_ids: set[str] = set()
        typed_solves: list[tuple[str, str]] = []
        independent: dict[str, str] = {}
        existing_mastery: set[str] = set()
        provisional_terms = 0
        human_claims: set[bool] = set()
        for row in iter_jsonl(role_path(native, roles, f"{lane}_records")):
            entity = str(row.get("entity_class"))
            stable_id = str(row.get("stable_id"))
            if stable_id in ids:
                fail(f"D100-VALIDATE-NATIVE-DUPLICATE:{lane}:{stable_id}")
            ids.add(stable_id)
            counts[entity] += 1
            payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
            path = str(row.get("path"))
            if entity == "unit" and row.get("language") == "en":
                if lane == "classical" and re.fullmatch(r"source/en/(lecture|worksheet)-\d{2}(-solutions)?\.md", path):
                    projected_unit_ids.add(stable_id)
                elif lane == "bgk" and re.fullmatch(r"source/en/bgk/(lecture|worksheet)-\d{2}(-solutions)?\.md", path):
                    projected_unit_ids.add(stable_id)
                elif lane == "original" and path.startswith("source/en/bridge/"):
                    projected_unit_ids.add(stable_id)
            elif entity == "exercise":
                exercise_ids.add(stable_id)
            elif entity == "solution":
                solution_ids.add(stable_id)
                exercise_id = payload.get("exercise_id")
                if lane in {"bgk", "original"} and isinstance(exercise_id, str):
                    linked_solution_ids.add(exercise_id)
            elif entity == "relation":
                relation_type = payload.get("relation_type") or payload.get("predicate")
                if relation_type == "solves":
                    typed_solves.append((str(payload.get("subject_id")), str(payload.get("object_id"))))
                elif relation_type == "independently_solves_source_problem":
                    independent[str(payload.get("subject_id"))] = str(payload.get("object_id"))
            elif entity == "resource" and isinstance(payload.get("source_reference"), dict) and payload["source_reference"].get("role") == "existing_public_source_solution":
                existing_mastery.add(stable_id)
            elif entity == "term" and row.get("status") == "provisional":
                provisional_terms += 1
            elif entity == "qa_event" and "human_review_claimed" in payload:
                human_claims.add(bool(payload["human_review_claimed"]))
        actual_counts = dict(sorted(counts.items()))
        if actual_counts != EXPECTED_ENTITY_COUNTS[lane]:
            fail("D100-VALIDATE-NATIVE-COUNTS:" + lane)
        if lane == "classical":
            linked_solution_ids = {
                obj for subject, obj in typed_solves if subject in solution_ids and obj in exercise_ids
            }
        facts[lane] = {
            "counts": actual_counts,
            "projected_unit_ids": projected_unit_ids,
            "exercise_ids": exercise_ids,
            "linked_solution_ids": linked_solution_ids,
            "independent": independent,
            "existing_mastery": existing_mastery,
            "provisional_terms": provisional_terms,
            "human_claims": human_claims,
        }
    if sum(sum(row["counts"].values()) for row in facts.values()) != EXPECTED_TOTAL_RECORDS:
        fail("D100-VALIDATE-NATIVE-TOTAL")
    if {lane: len(facts[lane]["exercise_ids"]) for lane in facts} != {"classical": 693, "bgk": 495, "original": 13}:
        fail("D100-VALIDATE-NATIVE-EXERCISES")
    if {lane: len(facts[lane]["linked_solution_ids"]) for lane in facts} != {"classical": 122, "bgk": 25, "original": 13}:
        fail("D100-VALIDATE-NATIVE-SOLUTIONS")
    if len(facts["original"]["independent"]) != 44 or len(facts["original"]["existing_mastery"]) != 13:
        fail("D100-VALIDATE-NATIVE-MASTERY")
    if facts["classical"]["provisional_terms"] != 4:
        fail("D100-VALIDATE-NATIVE-PROVISIONAL-TERMS")
    if facts["original"]["human_claims"] != {False}:
        fail("D100-VALIDATE-HUMAN-CLAIM")
    return facts


def verify_projection_against_native(bundle: dict[str, Any], facts: dict[str, Any]) -> None:
    learning_map = bundle["learning_map"]
    section_ids = {section for unit in learning_map["units"] for section in unit["sections"]}
    expected_sections = set().union(*(facts[lane]["projected_unit_ids"] for lane in facts))
    if section_ids != expected_sections:
        fail("D100-VALIDATE-NATIVE-SECTION-PROJECTION")
    exercises = [exercise for unit in learning_map["units"] for exercise in unit["exercises"]]
    projected_exercise_ids = {row["id"] for row in exercises}
    expected_exercise_ids = set().union(*(facts[lane]["exercise_ids"] for lane in facts))
    if projected_exercise_ids != expected_exercise_ids:
        fail("D100-VALIDATE-NATIVE-EXERCISE-PROJECTION")
    source_complete_ids = {
        row["id"] for row in exercises
        if row["curriculum_status"] == "source" and row["solution"]["status"] == "complete"
    }
    expected_source_complete = facts["classical"]["linked_solution_ids"] | facts["bgk"]["linked_solution_ids"]
    if source_complete_ids != expected_source_complete:
        fail("D100-VALIDATE-SOURCE-SOLUTION-PROJECTION")
    mastery_ids = {row["item_id"] for row in bundle["mastery"]}
    expected_mastery = set(facts["original"]["independent"]) | facts["original"]["existing_mastery"]
    if mastery_ids != expected_mastery:
        fail("D100-VALIDATE-MASTERY-PROJECTION")


def verify_shared_contract(value: dict[str, Any]) -> None:
    top = {
        "contract", "course_id", "locale", "native_dataset", "source_catalog", "units",
        "prerequisite_routes", "labs", "environments", "artifacts", "sources",
        "external_relation_nodes", "limitations",
    }
    if set(value) != top or value["contract"] != CONTRACT or value["course_id"] != COURSE_ID or value["locale"] != LOCALE or value["native_dataset"] != NATIVE_DATASET:
        fail("D100-VALIDATE-SHARED-CONTRACT-TOP")
    catalog = value["source_catalog"]
    if set(catalog) != {"path", "bytes", "sha256", "url"} or catalog["bytes"] < 1 or not re.fullmatch(r"[a-f0-9]{64}", catalog["sha256"]):
        fail("D100-VALIDATE-SHARED-CONTRACT-CATALOG")
    require_uri(catalog["url"], "D100-VALIDATE-SHARED-CONTRACT-CATALOG-URL")
    unit_keys = {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"}
    exercise_keys = {"id", "unit_id", "title", "kind", "sequence", "curriculum_status", "href", "hint", "check", "solution"}
    support_keys = {"status", "source_anchor", "label", "href"}
    if len(value["units"]) != EXPECTED_PROJECTED_UNITS:
        fail("D100-VALIDATE-SHARED-CONTRACT-UNITS")
    for unit in value["units"]:
        if set(unit) != unit_keys:
            fail("D100-VALIDATE-SHARED-CONTRACT-UNIT-SHAPE")
        require_uri(unit["href"], "D100-VALIDATE-SHARED-CONTRACT-UNIT-URL")
        if unit["objectives_href"] is not None:
            fail("D100-VALIDATE-SHARED-CONTRACT-OBJECTIVES")
        for component in unit["components"]:
            if not {"id", "source", "license"}.issubset(component):
                fail("D100-VALIDATE-SHARED-CONTRACT-COMPONENT")
        for exercise in unit["exercises"]:
            if set(exercise) != exercise_keys or not isinstance(exercise["sequence"], int) or exercise["sequence"] < 1:
                fail("D100-VALIDATE-SHARED-CONTRACT-EXERCISE")
            require_uri(exercise["href"], "D100-VALIDATE-SHARED-CONTRACT-EXERCISE-URL")
            for name in ("hint", "check", "solution"):
                support = exercise[name]
                if set(support) != support_keys or support["status"] not in {"complete", "executable", "not_present", "pending"}:
                    fail("D100-VALIDATE-SHARED-CONTRACT-SUPPORT")
                if support["status"] in {"complete", "executable"}:
                    require_uri(support["href"], "D100-VALIDATE-SHARED-CONTRACT-SUPPORT-URL")
                elif support["href"] is not None:
                    fail("D100-VALIDATE-SHARED-CONTRACT-ABSENT-SUPPORT-URL")
    if len(value["prerequisite_routes"]) != 5:
        fail("D100-VALIDATE-SHARED-CONTRACT-PREREQUISITE-COUNT")
    for route in value["prerequisite_routes"]:
        if not {"id", "unit", "prerequisite", "required_for_course", "sections", "exercises", "href"}.issubset(route):
            fail("D100-VALIDATE-SHARED-CONTRACT-PREREQUISITE")
        require_uri(route["href"], "D100-VALIDATE-SHARED-CONTRACT-PREREQUISITE-URL")
    if value["labs"] or value["environments"]:
        fail("D100-VALIDATE-SHARED-CONTRACT-LABS")
    for artifact in value["artifacts"]:
        if not {"id", "kind", "path"}.issubset(artifact):
            fail("D100-VALIDATE-SHARED-CONTRACT-ARTIFACT")
        require_uri(artifact["path"], "D100-VALIDATE-SHARED-CONTRACT-ARTIFACT-URL")
    for source in value["sources"]:
        if not {"id", "role", "license", "identity"}.issubset(source):
            fail("D100-VALIDATE-SHARED-CONTRACT-SOURCE")
    if len(value["external_relation_nodes"]) != len(set(value["external_relation_nodes"])) or not value["limitations"]:
        fail("D100-VALIDATE-SHARED-CONTRACT-LIMITATIONS")


class ViewFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.unit_ids: list[str] = []
        self.exercise_ids: list[str] = []
        self.mastery_ids: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("data-unit-id"):
            self.unit_ids.append(str(values["data-unit-id"]))
        if values.get("data-exercise-id"):
            self.exercise_ids.append(str(values["data-exercise-id"]))
        if values.get("data-mastery-id"):
            self.mastery_ids.append(str(values["data-mastery-id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))


def verify_views(output: Path, bundle: dict[str, Any]) -> None:
    expected_units = {row["unit_id"] for row in bundle["units"]}
    expected_exercises = {row["id"] for unit in bundle["learning_map"]["units"] for row in unit["exercises"]}
    expected_mastery = {row["item_id"] for row in bundle["mastery"]}
    expected_routes = {row["target_url"] for row in bundle["units"]}
    for name in ("D100.html", "D100-pengajar.html"):
        parser = ViewFacts()
        parser.feed((output / "views" / name).read_text(encoding="utf-8"))
        if len(parser.unit_ids) != EXPECTED_PROJECTED_UNITS or set(parser.unit_ids) != expected_units:
            fail("D100-VALIDATE-VIEW-UNITS:" + name)
        if len(parser.exercise_ids) != EXPECTED_EXERCISES or set(parser.exercise_ids) != expected_exercises:
            fail("D100-VALIDATE-VIEW-EXERCISES:" + name)
        if len(parser.mastery_ids) != 57 or set(parser.mastery_ids) != expected_mastery:
            fail("D100-VALIDATE-VIEW-MASTERY:" + name)
        if not expected_routes.issubset(set(parser.hrefs)):
            fail("D100-VALIDATE-VIEW-ROUTES:" + name)


def verify_manifest(output: Path, bundle: dict[str, Any]) -> list[str]:
    manifest = bundle["manifest"]
    paths = [row["path"] for row in manifest.get("outputs", [])]
    if len(paths) != len(set(paths)):
        fail("D100-VALIDATE-MANIFEST-DUPLICATE-OUTPUT")
    for row in manifest["outputs"]:
        target = output / row["path"]
        if not target.is_file() or file_identity(target) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            fail("D100-VALIDATE-MANIFEST-OUTPUT:" + row["path"])
    for relative in paths + ["manifest.json"]:
        data = (output / relative).read_bytes()
        if b"C:\\" in data or b"C:/Users/" in data:
            fail("D100-VALIDATE-ABSOLUTE-PATH-LEAK")
    return sorted(paths + ["manifest.json"])


def isolated_build(native: Path, lock: Path, output: Path) -> None:
    command = [
        sys.executable, "-B", str(BUILD_SCRIPT),
        "--native-root", str(native), "--output-root", str(output),
        "--source-lock", str(lock),
    ]
    result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, timeout=240)
    if result.returncode:
        fail("D100-VALIDATE-ISOLATED-BUILD:" + result.stderr.strip())


def compare_builds(native: Path, lock: Path, committed: Path, generated_paths: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d100-build-a-") as temp_a, tempfile.TemporaryDirectory(prefix="d100-build-b-") as temp_b:
        root_a = Path(temp_a)
        root_b = Path(temp_b)
        isolated_build(native, lock, root_a)
        isolated_build(native, lock, root_b)
        paths_a = sorted(path.relative_to(root_a).as_posix() for path in root_a.rglob("*") if path.is_file())
        paths_b = sorted(path.relative_to(root_b).as_posix() for path in root_b.rglob("*") if path.is_file())
        if paths_a != generated_paths or paths_b != generated_paths:
            fail("D100-VALIDATE-ISOLATED-FILE-SET")
        identity_a = tree_identity(root_a, paths_a)
        identity_b = tree_identity(root_b, paths_b)
        identity_committed = tree_identity(committed, generated_paths)
        if identity_a != identity_b:
            fail("D100-VALIDATE-ISOLATED-BYTE-IDENTITY")
        if identity_a != identity_committed:
            fail("D100-VALIDATE-COMMITTED-BUILD-DRIFT")
        return {"file_count": len(paths_a), "tree_sha256": identity_a["sha256"], "byte_identical": True}


def run_negative_fixtures(bundle: dict[str, Any], root: Path) -> list[dict[str, str]]:
    results = []
    seen: set[str] = set()
    for path in sorted(root.glob("*.json"), key=lambda item: item.name):
        fixture = read_json(path)
        if fixture.get("schema") != "d100-capability-negative-fixture/1":
            fail("D100-VALIDATE-NEGATIVE-SCHEMA:" + path.name)
        case_id = fixture.get("case_id")
        if case_id in seen:
            fail("D100-VALIDATE-NEGATIVE-DUPLICATE")
        seen.add(str(case_id))
        errors = validate_bundle(apply_negative_mutation(bundle, fixture["mutation"]))
        if fixture["expected_error"] not in errors:
            fail("D100-VALIDATE-NEGATIVE-NOT-REJECTED:" + str(case_id))
        results.append({"case_id": str(case_id), "expected_error": fixture["expected_error"], "state": "rejected"})
    if len(results) != EXPECTED_NEGATIVE_FIXTURES:
        fail(f"D100-VALIDATE-NEGATIVE-COUNT:{len(results)}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=ADAPTER)
    parser.add_argument("--source-lock", type=Path, default=ADAPTER / "input/source-lock.json")
    parser.add_argument("--receipt", type=Path, default=ADAPTER / "validation.json")
    args = parser.parse_args()
    native = args.native_root.resolve()
    output = args.output_root.resolve()
    lock_path = args.source_lock.resolve()
    lock = read_json(lock_path)
    roles = verify_locked_inputs(native, lock)
    verify_control_receipts(native, roles)
    bundle = load_bundle(output)
    errors = validate_bundle(bundle)
    if errors:
        fail("D100-VALIDATE-MODEL:" + ",".join(errors))
    verify_shared_contract(bundle["learning_map"])
    facts = native_facts(native, roles)
    verify_projection_against_native(bundle, facts)
    verify_views(output, bundle)
    generated_paths = verify_manifest(output, bundle)
    isolated = compare_builds(native, lock_path, output, generated_paths)
    negatives = run_negative_fixtures(bundle, output / "fixtures/negative")
    receipt = {
        "schema": "d100-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "central_course_truth_locale": "id-ID",
        "strict_shared_contract_shape": True,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "input_hashes_verified": len(roles),
        "native_record_rows_streamed": EXPECTED_TOTAL_RECORDS,
        "projected_units": EXPECTED_PROJECTED_UNITS,
        "source_exercises": EXPECTED_SOURCE_EXERCISES,
        "source_solutions": EXPECTED_SOURCE_SOLUTIONS,
        "negative_source_solution_states": EXPECTED_NEGATIVE_SOLUTIONS,
        "companion_exercises_and_solutions": 13,
        "mastery_route": {"items": 57, "new_editorial_solutions": 44, "existing_public_source_solution_references": 13, "units": list(EXPECTED_CONCENTRATED_UNITS)},
        "native_bodies_copied": False,
        "central_id_id_truth_rewritten": False,
        "native_mathml_claimed": False,
        "wcag_claimed": False,
        "zenodo_public_readback_claimed": False,
        "learner_educator_shared_identity": True,
        "isolated_two_build_byte_identity": isolated,
        "negative_fixtures": negatives,
        "manifest_sha256": file_identity(output / "manifest.json")["sha256"],
        "public_state_changed": False,
    }
    write_json(args.receipt.resolve(), receipt)
    print(json.dumps({"state": "pass", "receipt": str(args.receipt.resolve()), "tree_sha256": isolated["tree_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (D100Error, KeyError, TypeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"D100 validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
