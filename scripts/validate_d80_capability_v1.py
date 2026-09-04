"""Strict validator for the bounded D80 capability adapter.

Checks native byte identities and counts, projected semantics, strict shared
contract shape, corrected-reader anchors, learner/educator identity use,
manifest integrity, ten negative fixtures, and two isolated byte-identical
builds.  Standard-library only; no TeX or publication actions.
"""

from __future__ import annotations

import argparse
import csv
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

from d80_capability_model_v1 import (
    BRIDGE_IDS,
    CONTRACT,
    EXPECTED_CORRECTION_STATUS_COUNTS,
    EXPECTED_NATIVE_STATUS_COUNTS,
    EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES,
    EXPECTED_TERM_DRIFT,
    MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES,
    PAGES_BASE,
    PAGES_HEAD,
    UNIT_001_ID,
    D80Error,
    apply_negative_mutation,
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
ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d80-capability-v1"
DEFAULT_NATIVE = PROJECT.parent / "methods-of-algebra-volume-2-id"
BUILD_SCRIPT = PROJECT / "scripts/build_d80_capability_v1.py"


def fail(code: str) -> None:
    raise D80Error(code)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_uri(value: Any, code: str) -> None:
    if not isinstance(value, str) or urlsplit(value).scheme not in {"http", "https"}:
        fail(code)


def verify_locked_inputs(native: Path, lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    roles: dict[str, dict[str, Any]] = {}
    for item in lock.get("inputs", []):
        if item["role"] in roles:
            fail("D80-VALIDATE-LOCK-DUPLICATE-ROLE")
        path = native / item["path"]
        if not path.is_file() or file_identity(path) != {"bytes": item["bytes"], "sha256": item["sha256"]}:
            fail("D80-VALIDATE-LOCK-DRIFT:" + item["path"])
        roles[item["role"]] = item
    if len(roles) != 20:
        fail(f"D80-VALIDATE-LOCK-ROLE-COUNT:{len(roles)}")
    return roles


def verify_native_semantics(native: Path, roles: dict[str, dict[str, Any]], bundle: dict[str, Any]) -> None:
    native_units = read_jsonl(native / roles["native_units"]["path"])
    if len(native_units) != 146 or len({row["unit_id"] for row in native_units}) != 146:
        fail("D80-VALIDATE-NATIVE-UNIT-COUNT")
    if [row["sequence"] for row in native_units] != list(range(1, 147)):
        fail("D80-VALIDATE-NATIVE-UNIT-SEQUENCE")
    if dict(sorted(Counter(row["status"] for row in native_units).items())) != EXPECTED_NATIVE_STATUS_COUNTS:
        fail("D80-VALIDATE-NATIVE-STATUS")
    native_001 = next(row for row in native_units if row["unit_id"] == UNIT_001_ID)
    if "target_path" in native_001 or "target_sha256" in native_001:
        fail("D80-VALIDATE-UNIT001-NATIVE-ROW")

    target_rows = csv_rows(native / roles["translation_target_manifest"]["path"])
    if len(target_rows) != 146 or len({row["path"] for row in target_rows}) != 146:
        fail("D80-VALIDATE-TARGET-MANIFEST")
    target_manifest = {row["path"]: row for row in target_rows}
    projected_native = {row["unit_id"]: row for row in bundle["units"] if row["unit_type"] == "translated_source_unit"}
    for row in target_rows:
        target = native / row["path"]
        expected = {"bytes": int(row["bytes"]), "sha256": row["sha256"]}
        if not target.is_file() or file_identity(target) != expected:
            fail("D80-VALIDATE-TARGET-DRIFT:" + row["path"])
    superseded_sequences: set[int] = set()
    for native_row in native_units:
        projected = projected_native.get(native_row["unit_id"])
        if not projected:
            fail("D80-VALIDATE-MISSING-PROJECTED-UNIT")
        if projected["owner_native_status"] != native_row["status"]:
            fail("D80-VALIDATE-STATUS-REWRITE")
        if projected["source_locator"]["slice_sha256"] != native_row["source_slice_sha256"]:
            fail("D80-VALIDATE-SOURCE-LOCATOR-DRIFT")
        target = projected["translation_target"]
        manifest_path = target["path"]
        manifest_row = target_manifest.get(manifest_path)
        if not manifest_row or target["sha256"] != manifest_row["sha256"] or target["bytes"] != int(manifest_row["bytes"]):
            fail("D80-VALIDATE-PROJECTED-TARGET-MANIFEST")
        sequence = native_row["sequence"]
        if sequence == 1:
            if (
                target.get("native_hash_state") != "missing_in_historical_checkpoint_051"
                or target.get("identity_authority") != "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv"
            ):
                fail("D80-VALIDATE-UNIT001-HISTORICAL-IDENTITY")
        elif native_row.get("target_sha256") != manifest_row["sha256"]:
            native_hash = native_row.get("target_sha256")
            expected_format = (
                "malformed_67_hex"
                if sequence in MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES
                else "sha256"
            )
            if (
                sequence not in EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES
                or target.get("native_unit_index_sha256") != native_hash
                or target.get("native_unit_index_hash_format") != expected_format
                or target.get("native_hash_state") != "superseded_historical_checkpoint_051"
                or target.get("identity_authority") != "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv"
            ):
                fail("D80-VALIDATE-HISTORICAL-TARGET-HASH")
            superseded_sequences.add(sequence)
        elif sequence in EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES:
            fail("D80-VALIDATE-HISTORICAL-TARGET-HASH-MISSING")
        elif any(
            key in target
            for key in (
                "native_unit_index_sha256",
                "native_unit_index_hash_format",
                "native_hash_state",
                "identity_authority",
            )
        ):
            fail("D80-VALIDATE-HISTORICAL-TARGET-HASH-BOUNDARY")
    if superseded_sequences != set(EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES):
        fail("D80-VALIDATE-HISTORICAL-TARGET-HASH-COUNT")

    segments = read_jsonl(native / roles["segment_ledger_reference"]["path"])
    if len(segments) != 6347 or len({row["segment_id"] for row in segments}) != 6347:
        fail("D80-VALIDATE-SEGMENTS")
    precision = Counter(row.get("source_span_precision", "exact") for row in segments)
    if precision.get("unit_slice", 0) != 1736 or 6347 - precision.get("unit_slice", 0) != 4611:
        fail("D80-VALIDATE-SEGMENT-PRECISION")

    terms = csv_rows(native / roles["term_ledger_reference"]["path"])
    term_control = csv_rows(native / roles["terminology_control_reference"]["path"])
    if len(terms) != 511 or Counter(row["status"] for row in terms) != Counter({"active": 423, "provisional": 88}):
        fail("D80-VALIDATE-TERMS")
    backend_terms = {row["concept_id"]: row["preferred_id"] for row in terms}
    control_terms = {row["concept_id"]: row["o013_o014_preferred_id"] for row in term_control}
    actual_drift = {key: (backend_terms[key], control_terms[key]) for key in EXPECTED_TERM_DRIFT}
    if actual_drift != EXPECTED_TERM_DRIFT:
        fail("D80-VALIDATE-TERM-DRIFT")

    alt_rows = csv_rows(native / roles["figure_alt_ledger_reference"]["path"])
    if len(alt_rows) != 829 or len({row["diagram_id"] for row in alt_rows}) != 829:
        fail("D80-VALIDATE-FIGURE-ALT")
    overrides = read_json(native / roles["diagram_override_ledger_reference"]["path"])["overrides"]
    if len(overrides) != 13 or not {row["diagram_id"] for row in overrides}.issubset({row["diagram_id"] for row in alt_rows}):
        fail("D80-VALIDATE-DIAGRAM-OVERRIDES")

    corrections = csv_rows(native / roles["source_correction_ledger_reference"]["path"])
    if dict(sorted(Counter(row["status"] for row in corrections).items())) != EXPECTED_CORRECTION_STATUS_COUNTS:
        fail("D80-VALIDATE-CORRECTIONS")
    pending = next(row for row in corrections if row["correction_id"] == "O014-O001")
    if pending["status"] != "observed_not_modified_pending_consolidated_review":
        fail("D80-VALIDATE-PENDING-CORRECTION")


def verify_shared_contract(learning_map: dict[str, Any]) -> None:
    top = {
        "contract",
        "course_id",
        "locale",
        "native_dataset",
        "source_catalog",
        "units",
        "prerequisite_routes",
        "labs",
        "environments",
        "artifacts",
        "sources",
        "external_relation_nodes",
        "limitations",
    }
    if set(learning_map) != top or learning_map["contract"] != CONTRACT or learning_map["course_id"] != "D80":
        fail("D80-VALIDATE-SHARED-CONTRACT-TOP")
    if not isinstance(learning_map["locale"], str) or len(learning_map["locale"]) < 2:
        fail("D80-VALIDATE-SHARED-CONTRACT-LOCALE")
    if not isinstance(learning_map["native_dataset"], str) or not learning_map["native_dataset"]:
        fail("D80-VALIDATE-SHARED-CONTRACT-DATASET")
    catalog = learning_map["source_catalog"]
    if set(catalog) != {"path", "bytes", "sha256", "url"} or catalog["bytes"] < 1 or not re.fullmatch(r"[a-f0-9]{64}", catalog["sha256"]):
        fail("D80-VALIDATE-SHARED-CONTRACT-CATALOG")
    require_uri(catalog["url"], "D80-VALIDATE-SHARED-CONTRACT-CATALOG-URL")
    unit_keys = {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"}
    exercise_keys = {"id", "unit_id", "title", "kind", "sequence", "curriculum_status", "href", "hint", "check", "solution"}
    support_keys = {"status", "source_anchor", "label", "href"}
    if not isinstance(learning_map["units"], list) or not learning_map["units"]:
        fail("D80-VALIDATE-SHARED-CONTRACT-UNITS")
    for unit in learning_map["units"]:
        if set(unit) != unit_keys:
            fail("D80-VALIDATE-SHARED-CONTRACT-UNIT-SHAPE")
        require_uri(unit["href"], "D80-VALIDATE-SHARED-CONTRACT-UNIT-URL")
        if unit["objectives_href"] is not None:
            require_uri(unit["objectives_href"], "D80-VALIDATE-SHARED-CONTRACT-OBJECTIVES-URL")
        if len(unit["sections"]) != len(set(unit["sections"])):
            fail("D80-VALIDATE-SHARED-CONTRACT-SECTIONS")
        for component in unit["components"]:
            if not {"id", "source", "license"}.issubset(component):
                fail("D80-VALIDATE-SHARED-CONTRACT-COMPONENT")
        for exercise in unit["exercises"]:
            if set(exercise) != exercise_keys or exercise["sequence"] < 1:
                fail("D80-VALIDATE-SHARED-CONTRACT-EXERCISE")
            require_uri(exercise["href"], "D80-VALIDATE-SHARED-CONTRACT-EXERCISE-URL")
            for support_name in ("hint", "check", "solution"):
                support = exercise[support_name]
                if set(support) != support_keys or support["status"] not in {"complete", "executable", "not_present", "pending"}:
                    fail("D80-VALIDATE-SHARED-CONTRACT-SUPPORT")
                if support["status"] in {"complete", "executable"}:
                    require_uri(support["href"], "D80-VALIDATE-SHARED-CONTRACT-SUPPORT-URL")
                elif support["href"] is not None:
                    fail("D80-VALIDATE-SHARED-CONTRACT-ABSENT-SUPPORT-URL")
    for route in learning_map["prerequisite_routes"]:
        if not {"id", "unit", "prerequisite", "required_for_course", "sections", "exercises", "href"}.issubset(route):
            fail("D80-VALIDATE-SHARED-CONTRACT-PREREQUISITE")
    for lab in learning_map["labs"]:
        if not {"id", "unit", "environment", "exercise_ids", "artifact_ids"}.issubset(lab):
            fail("D80-VALIDATE-SHARED-CONTRACT-LAB")
    for environment in learning_map["environments"]:
        if not {"id", "runtime_version", "lock"}.issubset(environment):
            fail("D80-VALIDATE-SHARED-CONTRACT-ENVIRONMENT")
    for artifact in learning_map["artifacts"]:
        if not {"id", "kind", "path"}.issubset(artifact):
            fail("D80-VALIDATE-SHARED-CONTRACT-ARTIFACT")
    for source in learning_map["sources"]:
        if not {"id", "role", "license", "identity"}.issubset(source):
            fail("D80-VALIDATE-SHARED-CONTRACT-SOURCE")
    if len(learning_map["external_relation_nodes"]) != len(set(learning_map["external_relation_nodes"])):
        fail("D80-VALIDATE-SHARED-CONTRACT-EXTERNAL-NODES")
    if not learning_map["limitations"] or not all(isinstance(value, str) for value in learning_map["limitations"]):
        fail("D80-VALIDATE-SHARED-CONTRACT-LIMITATIONS")


class ViewFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.unit_ids: list[str] = []
        self.fragment_ids: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("data-unit-id"):
            self.unit_ids.append(str(values["data-unit-id"]))
        if values.get("data-fragment-id"):
            self.fragment_ids.append(str(values["data-fragment-id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))


def verify_reader_and_views(native: Path, roles: dict[str, dict[str, Any]], output: Path, bundle: dict[str, Any]) -> None:
    reader = (native / roles["corrected_reader_entry"]["path"]).read_text(encoding="utf-8")
    ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', reader))
    if not all(route["target_anchor"] in ids for route in bundle["routes"]):
        fail("D80-VALIDATE-READER-UNIT-ANCHORS")
    if not all(fragment["target_anchor"] in ids for fragment in bundle["fragments"]):
        fail("D80-VALIDATE-READER-FRAGMENT-ANCHORS")
    if any(not route["target_url"].startswith(PAGES_BASE + "#") or route["reader_head"] != PAGES_HEAD for route in bundle["routes"]):
        fail("D80-VALIDATE-READER-ROUTE-AUTHORITY")

    learner = ViewFacts()
    learner.feed((output / "views/D80.html").read_text(encoding="utf-8"))
    educator = ViewFacts()
    educator.feed((output / "views/D80-pengajar.html").read_text(encoding="utf-8"))
    unit_ids = {row["unit_id"] for row in bundle["units"]}
    fragment_ids = {row["fragment_id"] for row in bundle["fragments"]}
    if len(learner.unit_ids) != 148 or set(learner.unit_ids) != unit_ids:
        fail("D80-VALIDATE-LEARNER-UNIT-IDENTITIES")
    if len(educator.unit_ids) != 148 or set(educator.unit_ids) != unit_ids:
        fail("D80-VALIDATE-EDUCATOR-UNIT-IDENTITIES")
    if len(learner.fragment_ids) != 32 or set(learner.fragment_ids) != fragment_ids:
        fail("D80-VALIDATE-LEARNER-FRAGMENT-IDENTITIES")
    required_hrefs = {row["target_url"] for row in bundle["routes"] + bundle["fragments"]}
    if not required_hrefs.issubset(set(learner.hrefs)):
        fail("D80-VALIDATE-LEARNER-HREFS")
    if not {row["target_url"] for row in bundle["routes"]}.issubset(set(educator.hrefs)):
        fail("D80-VALIDATE-EDUCATOR-HREFS")


def verify_manifest(output: Path, bundle: dict[str, Any]) -> list[str]:
    manifest = bundle["manifest"]
    expected_paths = [row["path"] for row in manifest["outputs"]]
    if len(expected_paths) != len(set(expected_paths)):
        fail("D80-VALIDATE-MANIFEST-DUPLICATE-OUTPUT")
    for row in manifest["outputs"]:
        path = output / row["path"]
        if not path.is_file() or file_identity(path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            fail("D80-VALIDATE-MANIFEST-OUTPUT:" + row["path"])
    if any(b"C:\\" in (output / relative).read_bytes() for relative in expected_paths + ["manifest.json"]):
        fail("D80-VALIDATE-ABSOLUTE-PATH-LEAK")
    return sorted(expected_paths + ["manifest.json"])


def isolated_build(native: Path, lock: Path, output: Path) -> None:
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
    result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, timeout=120)
    if result.returncode:
        fail("D80-VALIDATE-ISOLATED-BUILD:" + result.stderr.strip())


def compare_builds(native: Path, lock: Path, committed: Path, generated_paths: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d80-build-a-") as temp_a, tempfile.TemporaryDirectory(prefix="d80-build-b-") as temp_b:
        root_a = Path(temp_a)
        root_b = Path(temp_b)
        isolated_build(native, lock, root_a)
        isolated_build(native, lock, root_b)
        paths_a = sorted(path.relative_to(root_a).as_posix() for path in root_a.rglob("*") if path.is_file())
        paths_b = sorted(path.relative_to(root_b).as_posix() for path in root_b.rglob("*") if path.is_file())
        if paths_a != generated_paths or paths_b != generated_paths:
            fail("D80-VALIDATE-ISOLATED-FILE-SET")
        identity_a = tree_identity(root_a, paths_a)
        identity_b = tree_identity(root_b, paths_b)
        identity_committed = tree_identity(committed, generated_paths)
        if identity_a != identity_b:
            fail("D80-VALIDATE-ISOLATED-BYTE-IDENTITY")
        if identity_a != identity_committed:
            fail("D80-VALIDATE-COMMITTED-BUILD-DRIFT")
        return {"file_count": len(paths_a), "tree_sha256": identity_a["sha256"], "byte_identical": True}


def run_negative_fixtures(bundle: dict[str, Any], fixture_root: Path) -> list[dict[str, str]]:
    results = []
    seen: set[str] = set()
    for path in sorted(fixture_root.glob("*.json"), key=lambda item: item.name):
        fixture = read_json(path)
        if fixture.get("schema") != "d80-capability-negative-fixture/1":
            fail("D80-VALIDATE-NEGATIVE-SCHEMA:" + path.name)
        if fixture["case_id"] in seen:
            fail("D80-VALIDATE-NEGATIVE-DUPLICATE")
        seen.add(fixture["case_id"])
        mutated = apply_negative_mutation(bundle, fixture["mutation"])
        errors = validate_bundle(mutated)
        if fixture["expected_error"] not in errors:
            fail("D80-VALIDATE-NEGATIVE-NOT-REJECTED:" + fixture["case_id"])
        results.append({"case_id": fixture["case_id"], "expected_error": fixture["expected_error"], "state": "rejected"})
    if len(results) != 11:
        fail(f"D80-VALIDATE-NEGATIVE-COUNT:{len(results)}")
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
    bundle = load_bundle(output)
    semantic_errors = validate_bundle(bundle)
    if semantic_errors:
        fail("D80-VALIDATE-MODEL:" + ",".join(semantic_errors))
    verify_shared_contract(bundle["learning_map"])
    verify_native_semantics(native, roles, bundle)
    verify_reader_and_views(native, roles, output, bundle)
    generated_paths = verify_manifest(output, bundle)
    isolated = compare_builds(native, lock_path, output, generated_paths)
    negatives = run_negative_fixtures(bundle, output / "fixtures/negative")
    receipt = {
        "schema": "d80-capability-validation/1",
        "state": "pass",
        "course_id": "D80",
        "strict_shared_contract_shape": True,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "input_hashes_verified": len(roles),
        "translation_targets_verified": 146,
        "native_units": 146,
        "independent_mastery_bridges": 2,
        "corrected_reader_routes_verified": 148,
        "mastery_fragments_verified": 32,
        "reader_route_authority": "github_pages_corrected",
        "unit_001_manifest_repair_verified": True,
        "superseded_checkpoint_target_hashes_preserved": 50,
        "malformed_superseded_checkpoint_hashes_preserved": 1,
        "native_status_preserved_separately": True,
        "native_ledger_bodies_copied": False,
        "segment_precision_partition_verified": {"exact_source_span": 4611, "unit_slice": 1736},
        "terminology_disagreements_preserved": 2,
        "pending_correction_preserved": "O014-O001",
        "source_exercises": {"exercises": 194, "hints": 117, "answers": 0, "solutions": 0},
        "native_mathml_claimed": False,
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
    except (D80Error, KeyError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"D80 validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
