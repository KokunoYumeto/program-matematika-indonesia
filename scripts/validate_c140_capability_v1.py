"""Validate the complete C140/C5 zero-copy capability adapter."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from build_c140_capability_v1 import NEGATIVE_FIXTURES, build, render_educator, render_learner
from c140_capability_model_v1 import (
    BOUNDARY_ID,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_COUNTS,
    GITHUB_RECEIPT,
    PAGES_RECEIPT,
    ZENODO_RECEIPT,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    forbidden_content_paths,
    identity,
    projection_errors,
    read_json,
    sha256_bytes,
    write_json,
)


JSONL_TO_KEY = {
    "data/document-index.jsonl": "documents",
    "data/penn-unit-index.jsonl": "penn_units",
    "data/penn-segment-index.jsonl": "penn_segments",
    "data/penn-terms-index.jsonl": "penn_terms",
    "data/penn-corrections-index.jsonl": "penn_corrections",
    "data/random-entity-index.jsonl": "random_entities",
    "data/random-relation-index.jsonl": "random_relations",
    "data/random-terms-index.jsonl": "random_terms",
    "data/random-adverse-index.jsonl": "random_adverse",
    "data/companion-entity-index.jsonl": "companion_entities",
    "data/companion-relation-index.jsonl": "companion_relations",
    "data/rights-index.jsonl": "rights_index",
}

JSON_TO_KEY = {
    "input/source-lock.json": "source_lock",
    "data/learner-map.json": "learner_map",
    "data/educator-map.json": "educator_map",
    "data/public-evidence.json": "public_evidence",
    "data/capabilities.json": "capabilities",
    "data/claim-boundary.json": "claim_boundary",
}


def _read_canonical_json(path: Path) -> Any:
    value = read_json(path)
    if path.read_bytes() != canonical_json_bytes(value):
        raise ValueError(f"C140 noncanonical JSON: {path}")
    return value


def _read_canonical_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if not data.endswith(b"\n"):
        raise ValueError(f"C140 JSONL is not LF terminated: {path}")
    rows = [json.loads(line.decode("utf-8")) for line in data.splitlines() if line]
    if any(not isinstance(row, dict) for row in rows) or data != canonical_jsonl_bytes(rows):
        raise ValueError(f"C140 JSONL is not canonical: {path}")
    return rows


def load_adapter_bundle(adapter: Path) -> dict[str, Any]:
    bundle: dict[str, Any] = {}
    for relative, key in JSONL_TO_KEY.items():
        bundle[key] = _read_canonical_jsonl(adapter / relative)
    for relative, key in JSON_TO_KEY.items():
        bundle[key] = _read_canonical_json(adapter / relative)
    return bundle


def _tree_identity(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "validation.json" or relative.startswith("build/"):
            continue
        files.append(identity(path, display_path=relative))
    return {"files": files, "file_count": len(files), "tree_sha256": sha256_bytes(canonical_json_bytes(files))}


def _mutated(fixture_id: str, baseline: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(baseline)
    if fixture_id == "source-lock-drift":
        value["source_lock"]["inputs"][0]["sha256"] = "00" * 32
    elif fixture_id == "dropped-document":
        value["documents"].pop()
    elif fixture_id == "altered-penn-unit-id":
        value["penn_units"][0]["id"] = value["penn_units"][1]["id"]
    elif fixture_id == "copied-source-text":
        value["random_entities"][0]["source_text"] = "forbidden native body"
    elif fixture_id == "copied-solution-body":
        value["educator_map"]["solved_problems"][0]["solution_body"] = "forbidden solution"
    elif fixture_id == "flattened-rights":
        value["rights_index"] = [{"id": "all", "license": "CC-BY-SA-4.0"}]
    elif fixture_id == "collapsed-random-witness":
        target = next(row for row in value["rights_index"] if row["id"] == "c140.rights.random-credits-witness")
        target["license"] = "CC-BY-2.0"
    elif fixture_id == "restricted-public-access":
        value["public_evidence"]["zenodo"]["access_right"] = "restricted"
    elif fixture_id == "false-uniform-pdf":
        value["claim_boundary"]["single_uniform_pdf_claimed"] = True
    elif fixture_id == "false-wcag":
        value["claim_boundary"]["wcag_conformance_claimed"] = True
    elif fixture_id == "bad-public-route":
        value["documents"][0]["public_page"]["url"] = value["documents"][1]["public_page"]["url"]
    elif fixture_id == "copied-native-body-count":
        value["claim_boundary"]["native_bodies_copied"] = 1
    else:
        raise ValueError(f"Unknown C140 negative fixture: {fixture_id}")
    return value


def _all_errors(bundle: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors = projection_errors(bundle)
    if bundle.get("source_lock") != expected.get("source_lock"):
        errors.append("C140-SOURCE-LOCK")
    return sorted(set(errors))


def _validate_negative_fixtures(adapter: Path, baseline: dict[str, Any]) -> list[dict[str, Any]]:
    expected = dict(NEGATIVE_FIXTURES)
    paths = sorted((adapter / "fixtures/negative").glob("*.json"))
    actual: set[str] = set()
    results: list[dict[str, Any]] = []
    for path in paths:
        fixture = _read_canonical_json(path)
        fixture_id = fixture.get("fixture_id")
        expected_error = expected.get(fixture_id)
        if expected_error is None or fixture.get("expected_error") != expected_error:
            raise ValueError(f"C140 fixture declaration mismatch: {fixture_id}")
        actual.add(fixture_id)
        errors = _all_errors(_mutated(fixture_id, baseline), baseline)
        if expected_error not in errors:
            raise ValueError(f"C140 fixture {fixture_id} did not raise {expected_error}; got {errors}")
        results.append({"fixture_id": fixture_id, "expected_error": expected_error, "result": "rejected"})
    if actual != set(expected):
        raise ValueError("C140 negative fixture inventory is incomplete")
    return sorted(results, key=lambda row: row["fixture_id"])


def _expected_projection_files() -> set[str]:
    return set(JSONL_TO_KEY) | set(JSON_TO_KEY) | {
        "input/github-release-readback.json",
        "input/github-pages-readback.json",
        "input/zenodo-readback.json",
        "views/C140.html",
        "views/C140-pengajar.html",
        "views/capabilities.json",
        "README.md",
    } | {f"fixtures/negative/{fixture_id}.json" for fixture_id, _ in NEGATIVE_FIXTURES}


def validate(native_root: Path, adapter: Path, *, write_receipt: bool = True) -> dict[str, Any]:
    expected = derive_projection(native_root)
    committed = load_adapter_bundle(adapter)
    errors = _all_errors(committed, expected)
    if errors:
        raise ValueError(f"C140 adapter invariant failures: {errors}")

    for key in set(JSON_TO_KEY.values()) | set(JSONL_TO_KEY.values()):
        if canonical_json_bytes(committed.get(key)) != canonical_json_bytes(expected.get(key)):
            raise ValueError(f"C140 committed projection drift: {key}")

    for adapter_name, producer_name in (
        ("input/github-release-readback.json", GITHUB_RECEIPT),
        ("input/github-pages-readback.json", PAGES_RECEIPT),
        ("input/zenodo-readback.json", ZENODO_RECEIPT),
    ):
        if (adapter / adapter_name).read_bytes() != (native_root / producer_name).read_bytes():
            raise ValueError(f"C140 primary receipt was not preserved byte-for-byte: {producer_name}")

    manifest = _read_canonical_json(adapter / "manifest.json")
    if manifest.get("course_id") != COURSE_ID or manifest.get("boundary_id") != BOUNDARY_ID:
        raise ValueError("C140 manifest identity mismatch")
    declared = {row["path"] for row in manifest.get("outputs", [])}
    expected_paths = _expected_projection_files()
    if declared != expected_paths:
        raise ValueError(f"C140 manifest output inventory drift: {sorted(declared ^ expected_paths)}")
    for row in manifest.get("outputs", []):
        if identity(adapter / row["path"], display_path=row["path"]) != row:
            raise ValueError(f"C140 manifest output drift: {row['path']}")
    if manifest.get("counts") != EXPECTED_COUNTS:
        raise ValueError("C140 manifest count drift")
    if manifest.get("projection", {}).get("native_bodies_copied") is not False:
        raise ValueError("C140 manifest falsely claims native bodies")

    if (adapter / "views/capabilities.json").read_bytes() != (adapter / "data/capabilities.json").read_bytes():
        raise ValueError("C140 capabilities view drift")
    learner_html = (adapter / "views/C140.html").read_text(encoding="utf-8")
    educator_html = (adapter / "views/C140-pengajar.html").read_text(encoding="utf-8")
    if learner_html != render_learner(expected) or educator_html != render_educator(expected):
        raise ValueError("C140 HTML views are not deterministic projections")
    rendered_html = learner_html + educator_html
    if "source_text" in rendered_html or "solution_body" in rendered_html or "forbidden native body" in rendered_html:
        raise ValueError("C140 views expose native body markers")
    if any(row["document_id"] not in learner_html for row in committed["documents"]):
        raise ValueError("C140 learner view omits a document identity")
    if any(row["id"] not in educator_html for row in committed["educator_map"]["solved_problems"]):
        raise ValueError("C140 educator view omits a solved-problem identity")
    if any(row["id"] not in educator_html for row in committed["educator_map"]["rubrics"]):
        raise ValueError("C140 educator view omits a rubric identity")
    if forbidden_content_paths(committed):
        raise ValueError("C140 projected JSON contains a forbidden content key")

    negative_results = _validate_negative_fixtures(adapter, expected)
    with tempfile.TemporaryDirectory(prefix="c140-capability-validation-") as temp:
        temp_root = Path(temp)
        run_a = temp_root / "run-a"
        run_b = temp_root / "run-b"
        build(native_root, run_a)
        build(native_root, run_b)
        identity_a = _tree_identity(run_a)
        identity_b = _tree_identity(run_b)
        identity_committed = _tree_identity(adapter)
        if identity_a != identity_b or identity_a != identity_committed:
            raise ValueError("C140 two-run build identity mismatch")

    validation = {
        "schema": "c140-capability-validation/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "result": "pass",
        "counts": EXPECTED_COUNTS,
        "checks": {
            "fresh_projection_matches_native": True,
            "complete_54_document_boundary": True,
            "stable_entity_id_closure": True,
            "canonical_machine_files": True,
            "three_primary_public_receipts_preserved_byte_for_byte": True,
            "all_54_public_routes_have_anonymous_http_200_hash_evidence": True,
            "component_rights_preserved_without_flattening": True,
            "native_bodies_absent": True,
            "learner_and_educator_views_complete": True,
            "two_run_build_identity": identity_a,
            "negative_fixtures_rejected": len(negative_results),
        },
        "negative_fixtures": negative_results,
    }
    if write_receipt:
        write_json(adapter / "validation.json", validation)
    return validation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = validate(args.native_root.resolve(), args.adapter.resolve(), write_receipt=not args.no_write)
    print(canonical_json_bytes({
        "state": result["result"],
        "course_id": COURSE_ID,
        "documents": result["counts"]["public_documents"],
        "stable_entity_ids": result["counts"]["stable_entity_ids"],
        "negative_fixtures": len(result["negative_fixtures"]),
        "tree_sha256": result["checks"]["two_run_build_identity"]["tree_sha256"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
