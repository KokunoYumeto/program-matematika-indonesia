#!/usr/bin/env python3
"""Validate D70 native evidence, projections, learner/teacher views, and replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from build_d70_capability_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    PROJECT,
    SCRIPT as BUILD_SCRIPT,
    csv_rows,
    li_files,
    verify_lock,
)
from d70_capability_model_v1 import (
    BUNDLE_FILES,
    EXPECTED_COMPONENT_IDS,
    EXPECTED_COUNTS,
    EXPECTED_DIAGNOSTIC_IDS,
    EXPECTED_LI_ORDERS,
    EXPECTED_MASTERY_IDS,
    EXPECTED_ROUTE_IDS,
    EXPECTED_STAGE_IDS,
    NEGATIVE_CASES,
    PUBLIC_FILES,
    PUBLIC_RECORD,
    apply_negative_mutation,
    canonical_json,
    canonical_json_line,
    file_identity,
    load_bundle,
    read_json,
    read_jsonl,
    tree_identity,
    validate_bundle,
    write_json,
)


SCRIPT = Path(__file__).resolve()


def fail(message: str) -> None:
    raise SystemExit(message)


def require_uri(value: Any, label: str) -> None:
    if not isinstance(value, str):
        fail(f"{label} is not a URI string")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail(f"{label} is not an absolute HTTP(S) URI: {value!r}")


def verify_native_semantics(native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    docs = [read_json(path) for path in li_files(native)]
    orders = tuple(doc["unit"]["order"] for doc in docs)
    unit_ids = [doc["unit"]["id"] for doc in docs]
    if orders != EXPECTED_LI_ORDERS or len(set(unit_ids)) != 41:
        fail("native Li unit order/identity mismatch")
    scalar_exercises = sum(doc["unit"]["surface_counts"]["exercises"] for doc in docs)
    scalar_hints = sum(doc["unit"]["surface_counts"]["hints"] for doc in docs)
    rights_ids = {row["id"] for doc in docs for row in doc["rights"]}
    if scalar_exercises != 142 or scalar_hints != 49 or len(rights_ids) != 5:
        fail("native Li scalar/rights truth mismatch")
    freeze = read_json(native / roles["li_complete_freeze"]["path"])
    corpus_exercises = sum(row["target_topology"]["top_level_exercises"] for row in freeze["files"])
    corpus_hints = sum(row["target_topology"]["hints"] for row in freeze["files"])
    if freeze.get("result") != "pass" or corpus_exercises != 161 or corpus_hints != 51:
        fail("frozen Li corpus truth mismatch")
    duncan = read_json(native / roles["duncan_component"]["path"])
    duncan_validation = read_json(native / roles["duncan_validation"]["path"])
    cring = read_json(native / roles["cring_component"]["path"])
    cring_validation = read_json(native / roles["cring_validation"]["path"])
    route = read_json(native / roles["original_route"]["path"])
    original = read_json(native / roles["original_build_qa"]["path"])
    if len(duncan["roots"]) != 7 or duncan_validation.get("result") != "PASS" or duncan_validation.get("counts") != duncan.get("counts"):
        fail("Duncan native backend mismatch")
    if len(cring["roots"]) != 6 or len(cring["repairs"]) != 9 or len(cring["original_bridge_records"]) != 3 or cring_validation.get("result") != "PASS" or cring_validation.get("counts") != cring.get("counts"):
        fail("CRing native backend mismatch")
    if len(route["prerequisites"]) != 6 or len(route["nodes"]) != 14 or sum(len(x["requires"]) for x in route["nodes"]) != 36:
        fail("native route-node/dependency mismatch")
    if len(route["study_sequence"]) != 7 or sum(len(x["items"]) for x in route["study_sequence"]) != 36:
        fail("native route-stage mismatch")
    if len(route["diagnostics"]) != 8 or sum(len(x["targets"]) for x in route["diagnostics"]) != 14 or sum(x["points"] for x in route["diagnostics"]) != 8:
        fail("native diagnostic mismatch")
    if len(route["mastery"]) != 8 or sum(len(x["targets"]) for x in route["mastery"]) != 13 or sum(len(x["hints"]) for x in route["mastery"]) != 16 or sum(bool(x.get("answer")) for x in route["mastery"]) != 8:
        fail("native mastery mismatch")
    if original.get("result") != "pass" or original.get("source_author_attribution_claimed") is not False:
        fail("native edition-original provenance mismatch")
    terms = csv_rows(native / roles["terminology"]["path"])
    if len(terms) != 690 or sum(x["status"] == "admitted" for x in terms) != 689 or sum(x["status"] == "provisional" for x in terms) != 1:
        fail("native terminology counts mismatch")
    if [x for x in terms if x["status"] == "provisional"] != [{"source_term": "valuation", "target_term": "valuasi", "status": "provisional", "scope": "chapter 10", "note": "Confirm in chapter context."}]:
        fail("native provisional valuation identity mismatch")
    zenodo = read_json(native / roles["zenodo_public_readback"]["path"])
    public_files = {x["name"]: (x["bytes"], x["sha256"]) for x in zenodo["files"]}
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
        or len(zenodo.get("files", [])) != 9
        or public_files != PUBLIC_FILES
    ):
        fail("native public readback mismatch")
    return {
        "li_units": 41,
        "li_corpus_exercises": corpus_exercises,
        "li_corpus_hints": corpus_hints,
        "li_backend_scalar_exercises": scalar_exercises,
        "li_backend_scalar_hints": scalar_hints,
        "duncan_roots": 7,
        "cring_roots": 6,
        "public_files": len(public_files),
    }


def verify_shared_contract(learning: dict[str, Any]) -> None:
    required = {"contract", "course_id", "locale", "native_dataset", "source_catalog", "units", "prerequisite_routes", "labs", "environments", "artifacts", "sources", "external_relation_nodes", "limitations"}
    if set(learning) != required:
        fail(f"shared contract key mismatch: {sorted(set(learning) ^ required)}")
    if learning["contract"] != "course-learning-capability/1" or learning["course_id"] != "D70" or learning["locale"] != "id-ID":
        fail("shared contract identity mismatch")
    unit_ids = [x["id"] for x in learning["units"]]
    if tuple(unit_ids) != EXPECTED_ROUTE_IDS or len(set(unit_ids)) != 20:
        fail("shared unit identity mismatch")
    exercise_ids: list[str] = []
    for unit in learning["units"]:
        if set(unit) != {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"}:
            fail(f"shared unit shape mismatch: {unit.get('id')}")
        require_uri(unit["href"], f"unit {unit['id']} href")
        require_uri(unit["objectives_href"], f"unit {unit['id']} objectives")
        for exercise in unit["exercises"]:
            exercise_ids.append(exercise["id"])
            require_uri(exercise["href"], f"exercise {exercise['id']} href")
            for key in ("hint", "check", "solution"):
                support = exercise[key]
                if support["status"] in {"complete", "executable"}:
                    require_uri(support["href"], f"exercise {exercise['id']} {key}")
                elif support["href"] is not None:
                    fail(f"absent support has a URL: {exercise['id']} {key}")
        component_ids = {component["id"] for component in unit["components"]}
        if "O013-K04" not in component_ids:
            fail(f"route authorship component missing from shared unit: {unit['id']}")
    if len(exercise_ids) != 16 or len(set(exercise_ids)) != 16 or set(exercise_ids) != set(EXPECTED_DIAGNOSTIC_IDS) | set(EXPECTED_MASTERY_IDS):
        fail("shared diagnostic/mastery identity mismatch")
    if len(learning["prerequisite_routes"]) != 36:
        fail("shared prerequisite route count mismatch")
    for route in learning["prerequisite_routes"]:
        require_uri(route["href"], f"prerequisite {route['id']}")
    for artifact in learning["artifacts"]:
        require_uri(artifact["path"], f"artifact {artifact['id']}")
    if len(set(learning["external_relation_nodes"])) != 54:
        fail("shared native-root identity mismatch")


class ViewFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.details_stack: list[bool] = []
        self.answer_ids: list[str] = []
        self.hint_ids: list[str] = []
        self.unstaged: list[str] = []
        self.root_rows = 0
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        keys = [key for key, _ in attrs]
        if len(keys) != len(set(keys)):
            fail(f"duplicate HTML attribute in <{tag}>")
        values = dict(attrs)
        if tag == "details":
            self.details_stack.append("open" in values)
        identity = values.get("id")
        if identity:
            if identity in self.ids:
                self.duplicate_ids.add(identity)
            self.ids.add(identity)
        if "data-root-row" in values:
            self.root_rows += 1
        for attr in ("href", "src"):
            if values.get(attr):
                self.urls.append(values[attr] or "")
        for attr, target in (("data-answer-id", self.answer_ids), ("data-hint-id", self.hint_ids)):
            if values.get(attr):
                target.append(values[attr] or "")
                if not self.details_stack or self.details_stack[-1] is True:
                    self.unstaged.append(values[attr] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "details":
            if not self.details_stack:
                fail("unbalanced details element")
            self.details_stack.pop()


def verify_views(output: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    learner_path = output / "views/D70.html"
    teacher_path = output / "views/D70-pengajar.html"
    learner_text = learner_path.read_text(encoding="utf-8")
    teacher_text = teacher_path.read_text(encoding="utf-8")
    parser = ViewFacts()
    parser.feed(learner_text)
    parser.close()
    if parser.details_stack or parser.duplicate_ids or parser.unstaged:
        fail(f"learner staged-disclosure/HTML identity failure: {parser.unstaged} {parser.duplicate_ids}")
    if len(parser.answer_ids) != 16 or len(set(parser.answer_ids)) != 16 or len(parser.hint_ids) != 16 or len(set(parser.hint_ids)) != 16:
        fail("learner answer/hint disclosure cardinality mismatch")
    if parser.root_rows != 54 or "addEventListener('input'" not in learner_text:
        fail("learner searchable root catalog mismatch")
    for component_id in EXPECTED_COMPONENT_IDS:
        if component_id not in learner_text or component_id not in teacher_text:
            fail(f"component missing from generated views: {component_id}")
    for route_id in EXPECTED_ROUTE_IDS:
        if route_id not in learner_text:
            fail(f"route missing from learner view: {route_id}")
    for diagnostic_id in EXPECTED_DIAGNOSTIC_IDS:
        if diagnostic_id not in learner_text or diagnostic_id not in teacher_text:
            fail(f"diagnostic missing from views: {diagnostic_id}")
    for mastery_id in EXPECTED_MASTERY_IDS:
        if mastery_id not in learner_text or mastery_id not in teacher_text:
            fail(f"mastery missing from views: {mastery_id}")
    if "689 diterima, 1 provisional" not in teacher_text or "71 Li, 9 CRing" not in teacher_text:
        fail("educator terminology/correction summary mismatch")
    combined_view_text = learner_text + "\n" + teacher_text
    forbidden_patterns = (
        ("windows-user-profile", re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.IGNORECASE)),
        ("file-uri", re.compile(r"file://", re.IGNORECASE)),
        ("api-token", re.compile(r"api_token", re.IGNORECASE)),
        ("bearer-credential", re.compile(r"bearer\s+", re.IGNORECASE)),
        ("authorization-header", re.compile(r"authorization:", re.IGNORECASE)),
    )
    for label, pattern in forbidden_patterns:
        if pattern.search(combined_view_text):
            fail(f"private/local marker in generated views: {label}")
    return {"learner_answers_staged": len(parser.answer_ids), "learner_hints_staged": len(parser.hint_ids), "native_root_rows": parser.root_rows}


def expected_output_paths() -> list[str]:
    return sorted(
        [relative for relative, _ in BUNDLE_FILES.values()]
        + ["views/D70.html", "views/D70-pengajar.html", "README.md"]
        + [f"fixtures/negative/{case_id}.json" for case_id in NEGATIVE_CASES]
    )


def verify_manifest(output: Path) -> dict[str, Any]:
    manifest = read_json(output / "manifest.json")
    if (
        manifest.get("schema") != "d70-capability-manifest/1"
        or manifest.get("course_id") != "D70"
        or manifest.get("contract") != "course-learning-capability/1"
    ):
        fail("manifest identity mismatch")
    if manifest.get("content_policy") != "metadata_and_evidence_only" or manifest.get("zero_copy_native_bodies") is not True or manifest.get("full_native_roundtrip_claimed") is not False or manifest.get("public_state_changed") is not False:
        fail("manifest policy mismatch")
    paths = expected_output_paths()
    records = manifest.get("outputs", [])
    if [x.get("path") for x in records] != paths or len({x.get("path") for x in records}) != len(paths):
        fail("manifest output inventory mismatch")
    for row in records:
        if file_identity(output / row["path"]) != {"bytes": row.get("bytes"), "sha256": row.get("sha256")}:
            fail(f"manifest output identity mismatch: {row['path']}")
    actual_payload = sorted(
        path.relative_to(output).as_posix()
        for root in (output / "data", output / "views", output / "fixtures/negative")
        for path in root.rglob("*") if path.is_file()
    ) + (["README.md"] if (output / "README.md").is_file() else [])
    if sorted(actual_payload) != paths:
        fail("unexpected/missing committed adapter payload")
    if manifest.get("counts") != EXPECTED_COUNTS or manifest.get("output_tree") != tree_identity(output, paths):
        fail("manifest count/tree mismatch")
    tooling = {x.get("path"): (x.get("bytes"), x.get("sha256")) for x in manifest.get("tooling", [])}
    expected_tooling = {}
    for name in ("d70_capability_model_v1.py", "build_d70_capability_v1.py", "validate_d70_capability_v1.py", "package_d70_capability_v1.py"):
        path = PROJECT / "scripts" / name
        identity = file_identity(path)
        expected_tooling[f"scripts/{name}"] = (identity["bytes"], identity["sha256"])
    if tooling != expected_tooling:
        fail("manifest tooling identity mismatch")
    return manifest


def verify_canonical_files(output: Path) -> None:
    for _, (relative, kind) in BUNDLE_FILES.items():
        path = output / relative
        if kind == "json":
            if path.read_bytes() != canonical_json(read_json(path)):
                fail(f"noncanonical JSON: {relative}")
        else:
            rows = read_jsonl(path)
            expected = b"".join(canonical_json_line(row) for row in rows)
            if path.read_bytes() != expected:
                fail(f"noncanonical JSONL: {relative}")


def run_negative_fixtures(bundle: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    files = sorted(root.glob("*.json"), key=lambda path: path.name)
    if {path.stem for path in files} != set(NEGATIVE_CASES):
        fail("negative fixture inventory mismatch")
    results = []
    for path in files:
        fixture = read_json(path)
        case_id = fixture.get("case_id")
        expected = list(NEGATIVE_CASES.get(case_id, ()))
        if fixture != {"schema": "d70-negative-fixture/1", "case_id": case_id, "mutation": case_id, "expected_errors": expected}:
            fail(f"negative fixture declaration mismatch: {path.name}")
        errors = validate_bundle(apply_negative_mutation(bundle, case_id))
        if errors != expected:
            fail(f"negative fixture result mismatch {case_id}: expected {expected}, got {errors}")
        results.append({"case_id": case_id, "errors": errors, "result": "PASS"})
    return results


def isolated_build(native: Path, lock: Path, output: Path) -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        [sys.executable, "-B", str(BUILD_SCRIPT), "--native", str(native), "--output", str(output), "--lock", str(lock)],
        cwd=PROJECT, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120,
    )
    if process.returncode != 0:
        fail(f"isolated D70 build failed: {process.stderr or process.stdout}")


def compare_replay(native: Path, lock: Path, committed: Path) -> dict[str, Any]:
    paths = expected_output_paths() + ["manifest.json"]
    with tempfile.TemporaryDirectory(prefix="d70-replay-a-") as first_dir, tempfile.TemporaryDirectory(prefix="d70-replay-b-") as second_dir:
        first = Path(first_dir) / "adapter"
        second = Path(second_dir) / "adapter"
        isolated_build(native, lock, first)
        isolated_build(native, lock, second)
        for relative in paths:
            committed_bytes = (committed / relative).read_bytes()
            first_bytes = (first / relative).read_bytes()
            second_bytes = (second / relative).read_bytes()
            if committed_bytes != first_bytes or first_bytes != second_bytes:
                fail(f"deterministic replay mismatch: {relative}")
        return {"files": len(paths), "tree": tree_identity(first, paths), "two_builds_identical": True, "committed_bytes_identical": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    native = args.native.resolve()
    output = args.output.resolve()
    lock = args.lock.resolve() if args.lock else output / "input/source-lock.json"
    receipt = args.receipt.resolve() if args.receipt else output / "validation.json"
    if receipt == output / "manifest.json" or receipt in [output / relative for relative in expected_output_paths()]:
        fail("validation receipt may not overwrite adapter input/output")
    _, roles = verify_lock(native, PROJECT, lock)
    native_summary = verify_native_semantics(native, roles)
    bundle = load_bundle(output)
    if bundle["course"].get("prerequisites") != ["C40", "B40"] or bundle["course"].get("outcome") != "Memasuki literatur aljabar pascasarjana dengan penguasaan konstruksi universal dan bukti struktural.":
        fail("frozen central course semantics were not projected")
    errors = validate_bundle(bundle)
    if errors:
        fail("D70 bundle validation failed: " + ", ".join(errors))
    verify_shared_contract(bundle["learning_map"])
    view_summary = verify_views(output, bundle)
    verify_canonical_files(output)
    manifest = verify_manifest(output)
    negative_results = run_negative_fixtures(bundle, output / "fixtures/negative")
    replay = compare_replay(native, lock, output)
    validation = {
        "schema": "d70-capability-validation/1", "course_id": "D70",
        "contract": "course-learning-capability/1", "result": "PASS",
        "content_policy": "metadata_and_evidence_only", "public_state_changed": False,
        "checks": {
            "source_lock_57_files": True, "central_record_locks": True, "native_semantics": True,
            "four_component_rights_boundary": True, "li_corpus_vs_backend_counts_preserved": True,
            "twenty_route_nodes_and_thirty_six_edges": True, "diagnostic_and_mastery_identity": True,
            "terminology_and_corrections": True, "zero_copy": True, "shared_contract": True,
            "learner_staged_disclosure": True, "educator_alignment": True,
            "negative_fixtures_33": True, "two_build_replay": True,
        },
        "counts": EXPECTED_COUNTS, "native": native_summary, "views": view_summary,
        "negative_fixtures": negative_results, "replay": replay,
        "manifest": {"path": "manifest.json", **file_identity(output / "manifest.json")},
        "source_lock": {"path": "input/source-lock.json", **file_identity(lock)},
        "limitations": bundle["capabilities"]["limitations"],
    }
    write_json(receipt, validation)
    print(json.dumps({"result": "PASS", "receipt": str(receipt), "identity": file_identity(receipt)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
