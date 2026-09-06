#!/usr/bin/env python3
"""Validate D30 source locks, zero-copy invariants, and deterministic replay."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from d30_capability_model_v1 import (
    AUTHORITATIVE_ORIGINALS,
    CONTENT_COMMIT,
    CONTRACT,
    COURSE_ID,
    EXPECTED_COUNTS,
    PAGES,
    SOURCE_INPUTS,
    file_identity,
    is_high_level,
    load_bundle,
    mutate_bundle,
    manifested_localized_title,
    read_csv,
    read_json,
    read_jsonl,
    validate_bundle,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = Path(r"C:\Users\Floris\Documents\interlanguage\04_mirrors\id\measure-theoretic-probability-stochastic-processes-id")
DEFAULT_OUTPUT = PROJECT / "backend/course-capsule-v1/adapters/d30-capability-v1"


class ValidationError(ValueError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValidationError(code)


def run_build(native: Path, output: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(PROJECT / "scripts/build_d30_capability_v1.py"), "--native", str(native), "--output", str(output)],
        cwd=PROJECT, capture_output=True, text=True, timeout=180,
    )
    if result.returncode:
        raise ValidationError("D30-REPLAY-BUILD:" + (result.stderr or result.stdout).strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    native = args.native.resolve()
    output = args.output.resolve()
    receipt_path = (args.receipt or output / "validation.json").resolve()

    manifest = read_json(output / "manifest.json")
    source_lock = read_json(output / "input/source-lock.json")
    bundle = load_bundle(output)
    errors = validate_bundle(bundle)
    require(not errors, ",".join(errors))

    require(manifest.get("course_id") == COURSE_ID and manifest.get("contract") == CONTRACT, "D30-MANIFEST-CONTRACT")
    require(manifest.get("zero_copy_native_bodies") is True and manifest.get("native_bodies_copied") is False and manifest.get("zero_copy") is True and manifest.get("public_state_changed") is False, "D30-MANIFEST-BOUNDARY")
    require(source_lock.get("input_count") == len(SOURCE_INPUTS) and [row["path"] for row in source_lock.get("inputs", [])] == list(SOURCE_INPUTS), "D30-SOURCE-LOCK-SET")
    for row in source_lock["inputs"]:
        require(file_identity(native / row["path"]) == {"bytes": row["bytes"], "sha256": row["sha256"]}, "D30-SOURCE-LOCK-DRIFT:" + row["path"])
    require(source_lock.get("native_repository", {}).get("reader_content_commit") == CONTENT_COMMIT, "D30-CONTENT-COMMIT")

    owner_entities = read_jsonl(native / "backend/entities.jsonl")
    owner_segments = read_jsonl(native / "backend/segments.jsonl")
    owner_relations = read_csv(native / "backend/relations.csv")
    require([row["native_id"] for row in bundle["record_index"]] == [row["id"] for row in owner_entities], "D30-NATIVE-ID-ORDER")
    require([row["native_id"] for row in bundle["segment_index"]] == [row["id"] for row in owner_segments], "D30-SEGMENT-ID-ORDER")
    require(
        [(row["relation_id"], row["relation_type"], row["source_id"], row["target_id"], row["status"]) for row in bundle["relations"]]
        == [(row["relation_id"], row["relation_type"], row["source_id"], row["target_id"], row["status"]) for row in owner_relations],
        "D30-RELATION-PROJECTION",
    )
    require(manifest.get("counts", {}).get("entities") == EXPECTED_COUNTS["entities"] and manifest.get("counts", {}).get("segments") == EXPECTED_COUNTS["segments"], "D30-MANIFEST-COUNTS")

    site_manifest = {row["path"]: row for row in read_csv(native / "build/site/PACKAGE_MANIFEST.csv")}
    learner_by_id = {row["native_id"]: row for row in bundle["learner_map"]["units"]}
    owner_high = [row for row in owner_entities if is_high_level(row)]
    require(len(owner_high) == EXPECTED_COUNTS["high_level_units"], "D30-LOCALIZED-TITLE-COUNT")
    for row in owner_high:
        expected_title, expected_source = manifested_localized_title(native, row, site_manifest)
        projected = learner_by_id.get(row["id"], {})
        require(projected.get("title") == expected_title and projected.get("title_source") == expected_source, "D30-LOCALIZED-TITLE:" + row["id"])
        shared_row = next((unit for unit in bundle["learning_map"]["units"] if unit["id"] == row["id"]), {})
        require(shared_row.get("title") == expected_title, "D30-SHARED-LOCALIZED-TITLE:" + row["id"])

    for item in manifest.get("outputs", []):
        require(file_identity(output / item["path"]) == {"bytes": item["bytes"], "sha256": item["sha256"]}, "D30-OUTPUT-DRIFT:" + item["path"])
    require(manifest.get("source_lock") == {"path": "input/source-lock.json", **file_identity(output / "input/source-lock.json")}, "D30-SOURCE-LOCK-MANIFEST")

    for view in ("views/D30.html", "views/D30-pengajar.html"):
        text = (output / view).read_text(encoding="utf-8")
        require('href="/en/"' in text and 'href="/id/"' in text, "D30-PROGRAM-BACKLINKS:" + view)
        require(PAGES in text and f"/tree/{CONTENT_COMMIT}" in text and "Pembaca publik" in text and "Sumber asli terkunci" in text, "D30-VIEW-PUBLIC-LINKS:" + view)
        require(all(row["url"] in text for row in AUTHORITATIVE_ORIGINALS) and "Sumber asli otoritatif" in text, "D30-AUTHORITATIVE-ORIGINALS:" + view)

    shared = bundle["learning_map"]
    require(set(shared) == {"contract", "course_id", "locale", "native_dataset", "source_catalog", "units", "prerequisite_routes", "labs", "environments", "artifacts", "sources", "external_relation_nodes", "limitations"}, "D30-SHARED-KEYS")
    require(all(set(row) == {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"} for row in shared["units"]), "D30-SHARED-UNIT-KEYS")
    require(all(row["href"].startswith(PAGES) for row in shared["units"]), "D30-SHARED-UNIT-ROUTES")

    negative_results = []
    for fixture_path in sorted((output / "fixtures/negative").glob("*.json")):
        fixture = read_json(fixture_path)
        mutated_errors = validate_bundle(mutate_bundle(bundle, fixture))
        passed = fixture["expected_error"] in mutated_errors
        negative_results.append({"case": fixture["case"], "expected_error": fixture["expected_error"], "observed_errors": mutated_errors, "result": "PASS" if passed else "FAIL"})
        require(passed, "D30-NEGATIVE-FIXTURE:" + fixture["case"])

    with tempfile.TemporaryDirectory(prefix="d30-capability-replay-a-") as temp_a, tempfile.TemporaryDirectory(prefix="d30-capability-replay-b-") as temp_b:
        replay_a = Path(temp_a) / "adapter"
        replay_b = Path(temp_b) / "adapter"
        run_build(native, replay_a)
        run_build(native, replay_b)
        replay_manifest = read_json(replay_a / "manifest.json")
        replay_paths = ["manifest.json", *[row["path"] for row in replay_manifest["outputs"]]]
        for relative in replay_paths:
            expected = (output / relative).read_bytes()
            require((replay_a / relative).read_bytes() == expected, "D30-REPLAY-COMMITTED-DRIFT:" + relative)
            require((replay_b / relative).read_bytes() == expected, "D30-REPLAY-TWO-BUILD-DRIFT:" + relative)

    checks = {
        "source_lock_exact": True,
        "native_entity_ids_exact": True,
        "native_segment_ids_exact": True,
        "native_relations_exact": True,
        "zero_copy": True,
        "component_rights_preserved": True,
        "public_hashes_exact": True,
        "public_reader_original_links": True,
        "localized_titles_manifest_hash_bound": True,
        "authoritative_originals_visible": True,
        "program_en_id_backlinks": True,
        "shared_contract_shape": True,
        "negative_fixtures": True,
        "two_builds_identical": True,
        "committed_bytes_identical": True,
    }
    receipt = {
        "schema": "d30-capability-validation/1", "course_id": COURSE_ID, "contract": CONTRACT, "result": "PASS",
        "manifest": {"path": "manifest.json", **file_identity(output / "manifest.json")},
        "source_lock": manifest["source_lock"], "counts": manifest["counts"], "checks": checks,
        "negative_fixtures": negative_results,
        "replay": {"two_builds_identical": True, "committed_bytes_identical": True, "files": len(manifest["outputs"]) + 1},
        "content_policy": manifest["content_policy"], "public_state_changed": False,
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"result": "PASS", "receipt": str(receipt_path), "manifest": receipt["manifest"], "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"D30 validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
