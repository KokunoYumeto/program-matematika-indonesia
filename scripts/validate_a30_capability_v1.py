"""Validate the A30 capability adapter and its zero-copy claim boundaries."""

from __future__ import annotations

import argparse
import copy
import tempfile
from pathlib import Path
from typing import Any

from a30_capability_model_v1 import (
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_CANONICAL_SHA256,
    PUBLIC_RECEIPT_PATH,
    UPSTREAM_COMMIT,
    UPSTREAM_TREE,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_canonical_jsonl,
    read_json,
    sha256_bytes,
    write_json,
)
from build_a30_capability_v1 import NEGATIVE_FIXTURES, build, render_educator, render_learner


JSONL_TO_KEY = {
    "data/chapter-index.jsonl": "chapter_index",
    "data/module-index.jsonl": "module_index",
    "data/exercise-index.jsonl": "exercise_index",
    "data/concept-index.jsonl": "concept_index",
    "data/pedagogical-relation-index.jsonl": "pedagogical_relation_index",
    "data/terms-index.jsonl": "terms_index",
    "data/corrections-index.jsonl": "corrections_index",
    "data/rights-index.jsonl": "rights_index",
}

JSON_TO_KEY = {
    "input/source-lock.json": "source_lock",
    "data/native-record-ledger.json": "native_record_ledger",
    "data/segment-state-summary.json": "segment_state_summary",
    "data/learner-map.json": "learner_map",
    "data/educator-map.json": "educator_map",
    "data/public-evidence.json": "public_evidence",
    "data/capabilities.json": "capabilities",
    "data/claim-boundary.json": "claim_boundary",
}


def _read_canonical_json(path: Path) -> Any:
    value = read_json(path)
    if path.read_bytes() != canonical_json_bytes(value):
        raise ValueError(f"Noncanonical JSON: {path}")
    return value


def load_adapter_bundle(adapter: Path) -> dict[str, Any]:
    bundle: dict[str, Any] = {}
    for relative, key in JSONL_TO_KEY.items():
        bundle[key] = read_canonical_jsonl(adapter / relative)
    for relative, key in JSON_TO_KEY.items():
        bundle[key] = _read_canonical_json(adapter / relative)
    return bundle


def _tree_identity(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "validation.json" or relative.startswith(("build/", "publication/")):
            continue
        files.append(identity(path, display_path=relative))
    return {"files": files, "file_count": len(files), "tree_sha256": sha256_bytes(canonical_json_bytes(files))}


def _source_lock_errors(bundle: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return [] if bundle.get("source_lock") == expected.get("source_lock") else ["A30-SOURCE-LOCK"]


def _all_errors(bundle: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return sorted(set(projection_errors(bundle) + _source_lock_errors(bundle, expected)))


def _mutated(fixture_id: str, baseline: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(baseline)
    if fixture_id == "source-hash-drift":
        value["source_lock"]["inputs"][0]["sha256"] = "00" * 32
    elif fixture_id == "native-sequence-drift":
        value["native_record_ledger"]["id_sequence_sha256"] = "00" * 32
    elif fixture_id == "dropped-module":
        value["module_index"].pop()
    elif fixture_id == "dropped-exercise":
        value["exercise_index"].pop()
    elif fixture_id == "invented-solution":
        row = next(row for row in value["exercise_index"] if row["solution_id"] is None)
        row["solution_id"] = "urn:uuid:invented"
    elif fixture_id == "collapsed-segment-asymmetry":
        value["segment_state_summary"]["bucket_counts"] = {"id-ID|translated|active": 149955}
    elif fixture_id == "copied-source-text":
        value["learner_map"]["source_text"] = "forbidden source text"
    elif fixture_id == "copied-target-text":
        value["learner_map"]["target_text"] = "forbidden target text"
    elif fixture_id == "copied-body":
        value["learner_map"]["body"] = "forbidden native body"
    elif fixture_id == "invented-native-prerequisite":
        value["claim_boundary"]["native_course_prerequisites_invented"] = True
    elif fixture_id == "false-final-derivative-revision":
        value["claim_boundary"]["final_derivative_git_revision_claimed"] = True
    elif fixture_id == "invented-public-derivative-revision":
        value["public_evidence"]["repository"]["final_derivative_commit"] = "0" * 40
    elif fixture_id == "false-semantic-html":
        value["claim_boundary"]["indonesian_semantic_html_claimed"] = True
    elif fixture_id == "false-mathml":
        value["claim_boundary"]["indonesian_mathml_claimed"] = True
    elif fixture_id == "false-epub":
        value["claim_boundary"]["epub_claimed"] = True
    elif fixture_id == "false-portable-html":
        value["claim_boundary"]["portable_offline_html_claimed"] = True
    elif fixture_id == "false-pdfua":
        value["claim_boundary"]["pdf_ua_claimed"] = True
    elif fixture_id == "false-wcag":
        value["claim_boundary"]["wcag_conformance_claimed"] = True
    elif fixture_id == "false-labs":
        value["claim_boundary"]["interactive_labs_claimed"] = True
    elif fixture_id == "false-runtime":
        value["claim_boundary"]["learning_runtime_claimed"] = True
    elif fixture_id == "false-teacher-manual":
        value["claim_boundary"]["official_teacher_manual_claimed"] = True
    elif fixture_id == "false-exhaustive-exercise-routes":
        value["claim_boundary"]["exhaustive_exercise_pdf_destinations_claimed"] = True
    elif fixture_id == "injected-exercise-route":
        value["exercise_index"][0]["public_route"] = "https://example.invalid/"
    elif fixture_id == "false-standalone-raw-replay":
        value["claim_boundary"]["standalone_raw_replay_claimed"] = True
    elif fixture_id == "false-reversibility":
        value["claim_boundary"]["reversible_exchange_claimed"] = True
    elif fixture_id == "flattened-rights":
        value["rights_index"] = [{"id": "all"}]
    elif fixture_id == "bad-module-route":
        value["module_index"][0]["public_route"] = "https://example.invalid/"
    else:
        raise ValueError(f"Unknown A30 negative fixture: {fixture_id}")
    return value


def _fixture_declaration(fixture: tuple[str, str, str, Any, str]) -> dict[str, Any]:
    fixture_id, path, operation, value, expected = fixture
    declaration: dict[str, Any] = {
        "schema": "a30-negative-fixture/1",
        "fixture_id": fixture_id,
        "mutation": {"operation": operation, "path": path},
        "expected_error": expected,
    }
    if operation != "remove":
        declaration["mutation"]["value"] = value
    return declaration


def _validate_negative_fixtures(adapter: Path, baseline: dict[str, Any]) -> list[dict[str, Any]]:
    expected_index = {fixture[0]: fixture for fixture in NEGATIVE_FIXTURES}
    fixture_paths = sorted((adapter / "fixtures/negative").glob("*.json"))
    actual_ids: set[str] = set()
    results = []
    for path in fixture_paths:
        declaration = _read_canonical_json(path)
        fixture_id = declaration.get("fixture_id")
        fixture = expected_index.get(str(fixture_id))
        if fixture is None or declaration != _fixture_declaration(fixture):
            raise ValueError(f"A30 fixture declaration mismatch: {fixture_id}")
        actual_ids.add(str(fixture_id))
        expected_error = fixture[4]
        errors = _all_errors(_mutated(str(fixture_id), baseline), baseline)
        if expected_error not in errors:
            raise ValueError(f"A30 fixture {fixture_id} did not raise {expected_error}; got {errors}")
        results.append({"fixture_id": fixture_id, "expected_error": expected_error, "result": "rejected"})
    if actual_ids != set(expected_index):
        raise ValueError("A30 negative fixture inventory is incomplete")
    return sorted(results, key=lambda row: str(row["fixture_id"]))


def validate(
    native_root: Path,
    adapter: Path,
    *,
    receipt_path: Path = PUBLIC_RECEIPT_PATH,
    write_receipt: bool = True,
) -> dict[str, Any]:
    expected = derive_projection(native_root, receipt_path)
    committed = load_adapter_bundle(adapter)
    errors = _all_errors(committed, expected)
    if errors:
        raise ValueError(f"A30 adapter invariant failures: {errors}")
    for key in expected:
        if committed[key] != expected[key]:
            raise ValueError(f"A30 committed projection drift: {key}")

    source_receipt = _read_canonical_json(adapter / "input/public-native-readback.json")
    if source_receipt != read_json(receipt_path):
        raise ValueError("A30 committed public-native receipt drift")

    manifest = _read_canonical_json(adapter / "manifest.json")
    if manifest.get("course_id") != COURSE_ID or manifest.get("canonical_jsonl_sha256") != EXPECTED_CANONICAL_SHA256:
        raise ValueError("A30 manifest identity mismatch")
    expected_scripts = [
        "scripts/a30_capability_model_v1.py",
        "scripts/build_a30_capability_v1.py",
        "scripts/validate_a30_capability_v1.py",
        "scripts/package_a30_capability_v1.py",
        "scripts/verify_a30_native_public_v1.py",
    ]
    if manifest.get("tooling_scripts") != expected_scripts:
        raise ValueError("A30 manifest tooling inventory mismatch")
    for row in manifest.get("outputs", []):
        actual = identity(adapter / row["path"], display_path=row["path"])
        if actual != row:
            raise ValueError(f"A30 manifest output drift: {row['path']}")

    learner_html = (adapter / "views/A30.html").read_text(encoding="utf-8")
    educator_html = (adapter / "views/A30-pengajar.html").read_text(encoding="utf-8")
    if learner_html != render_learner(committed) or educator_html != render_educator(committed):
        raise ValueError("A30 views are not deterministic map projections")
    rendered_html = learner_html + educator_html
    if 'href="file:' in rendered_html or 'src="file:' in rendered_html or "C:\\" in rendered_html:
        raise ValueError("A30 views expose a local path")
    learner_missing = [row["module_id"] for row in committed["module_index"] if row["module_id"] not in learner_html]
    educator_missing = [row["module_id"] for row in committed["module_index"] if row["module_id"] not in educator_html]
    if learner_missing or educator_missing:
        raise ValueError(f"A30 views omit module identities: learner={learner_missing[:5]} educator={educator_missing[:5]}")

    negative_results = _validate_negative_fixtures(adapter, expected)
    with tempfile.TemporaryDirectory(prefix="a30-capability-validation-") as temp:
        temp_root = Path(temp)
        run_a = temp_root / "run-a"
        run_b = temp_root / "run-b"
        build(native_root, run_a, receipt_path)
        build(native_root, run_b, receipt_path)
        identity_a = _tree_identity(run_a)
        identity_b = _tree_identity(run_b)
        identity_committed = _tree_identity(adapter)
        if identity_a != identity_b or identity_a != identity_committed:
            raise ValueError("A30 two-run build identity mismatch")

    counts = committed["capabilities"]["counts"]
    receipt = {
        "schema": "a30-capability-validation/1",
        "course_id": COURSE_ID,
        "result": "pass",
        "upstream_source": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE},
        "final_derivative_revision_proved": False,
        "native_export": committed["source_lock"]["native_export"],
        "checks": {
            "canonical_machine_files": True,
            "committed_projection_matches_public_native": True,
            "component_specific_rights_preserved": True,
            "exercise_problem_identity_bijection": counts["exercises"],
            "solution_identity_boundary_preserved": {
                "with_solution_identity": counts["solution_identities"],
                "without_native_solution_support": counts["unsupported_exercises"],
            },
            "segment_state_asymmetry_preserved": counts["segment_state_bucket_counts"],
            "source_target_and_body_text_absent": True,
            "exercise_pdf_destinations_not_indexed": True,
            "public_source_receipt_state": source_receipt["state"],
            "public_source_assets": len(source_receipt["github_release"]["assets"]),
            "public_zenodo_assets": len(source_receipt["zenodo"]["assets"]),
            "final_derivative_git_commit_or_tree_not_claimed": True,
            "standalone_raw_replay_not_claimed": True,
            "two_run_build_identity": identity_a,
            "module_identities_rendered_for_learner": len(committed["module_index"]),
            "module_identities_rendered_for_educator": len(committed["module_index"]),
        },
        "counts": counts,
        "negative_fixtures": negative_results,
    }
    if write_receipt:
        write_json(adapter / "validation.json", receipt)
    else:
        validation_path = adapter / "validation.json"
        if not validation_path.is_file() or _read_canonical_json(validation_path) != receipt:
            raise ValueError("A30 committed validation receipt drift")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--receipt", type=Path, default=PUBLIC_RECEIPT_PATH)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    receipt = validate(
        args.native_root.resolve(),
        args.adapter.resolve(),
        receipt_path=args.receipt.resolve(),
        write_receipt=not args.no_write,
    )
    print(canonical_json_bytes({
        "state": receipt["result"],
        "course_id": COURSE_ID,
        "native_records": receipt["counts"]["native_records"],
        "modules": receipt["counts"]["modules"],
        "exercises": receipt["counts"]["exercises"],
        "negative_fixtures": len(receipt["negative_fixtures"]),
        "two_run_tree_sha256": receipt["checks"]["two_run_build_identity"]["tree_sha256"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
