"""Validate the B95 zero-copy capability adapter.

Validation is intentionally bounded to the B95 adapter and its external native
evidence.  It does not alter the producer checkout, central course records, or
publication state.
"""

from __future__ import annotations

import argparse
import copy
import tempfile
from pathlib import Path
from typing import Any

from b95_capability_model_v1 import (
    BOUNDARY_ID,
    CHAPTER_PAGE_STARTS,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_RECORD_COUNTS,
    EXPECTED_UNIT_KINDS,
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
from build_b95_capability_v1 import NEGATIVE_FIXTURES, build, render_educator, render_learner


JSONL_TO_KEY = {
    "data/native-record-index.jsonl": "native_record_index",
    "data/unit-index.jsonl": "unit_index",
    "data/exercise-index.jsonl": "exercise_index",
    "data/concept-index.jsonl": "concept_index",
    "data/relation-index.jsonl": "relation_index",
    "data/terms-index.jsonl": "terms_index",
    "data/corrections-index.jsonl": "corrections_index",
    "data/rights-index.jsonl": "rights_index",
    "data/segment-index.jsonl": "segment_index",
    "data/localization-index.jsonl": "localization_index",
    "data/evidence-index.jsonl": "evidence_index",
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
        raise ValueError(f"B95 noncanonical JSON: {path}")
    return value


def _read_canonical_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    data = path.read_bytes()
    if not data.endswith(b"\n"):
        raise ValueError(f"B95 JSONL is not LF terminated: {path}")
    for number, line in enumerate(data.splitlines(), 1):
        if not line:
            continue
        row = read_json_line(line, path, number)
        if line != canonical_json_bytes_compact(row):
            raise ValueError(f"B95 noncanonical JSONL row {number}: {path}")
        rows.append(row)
    return rows


def read_json_line(line: bytes, path: Path, number: int) -> dict[str, Any]:
    import json

    try:
        value = json.loads(line.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser error is enough
        raise ValueError(f"B95 invalid JSONL row {number}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"B95 JSONL row is not an object {number}: {path}")
    return value


def canonical_json_bytes_compact(value: Any) -> bytes:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


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
    return {
        "files": files,
        "file_count": len(files),
        "tree_sha256": sha256_bytes(canonical_json_bytes(files)),
    }


def _mutated(fixture_id: str, baseline: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(baseline)
    if fixture_id == "hash-drift":
        value["source_lock"]["inputs"][0]["sha256"] = "00" * 32
    elif fixture_id == "altered-native-id":
        value["native_record_index"][0]["id"] = "urn:b95:changed"
    elif fixture_id == "dropped-native-id":
        value["native_record_index"].pop()
    elif fixture_id == "copied-body":
        value["learner_map"]["body"] = "forbidden native body"
    elif fixture_id == "copied-segment-text":
        value["claim_boundary"]["target_segment_text_copied"] = 1
    elif fixture_id == "false-solutions":
        value["claim_boundary"]["answer_or_solution_bodies_copied"] = 1
    elif fixture_id == "false-semantic-html":
        value["public_evidence"]["reader"]["semantic_html_established"] = True
    elif fixture_id == "false-wcag":
        value["claim_boundary"]["wcag_conformance_claimed"] = True
    elif fixture_id == "false-reversibility":
        value["claim_boundary"]["reversible_exchange_claimed"] = True
    elif fixture_id == "flattened-rights":
        value["rights_index"] = [{"id": "all"}]
    elif fixture_id == "public-access-drift":
        value["public_evidence"]["zenodo"]["access_right"] = "restricted"
    elif fixture_id == "bad-chapter-route":
        value["learner_map"]["chapters"][0]["public_route"] = "https://example.invalid/"
    else:
        raise ValueError(f"Unknown B95 negative fixture: {fixture_id}")
    return value


def _all_errors(bundle: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors = projection_errors(bundle)
    if bundle.get("source_lock") != expected.get("source_lock"):
        errors.append("B95-SOURCE-LOCK")
    return sorted(set(errors))


def _validate_negative_fixtures(adapter: Path, baseline: dict[str, Any]) -> list[dict[str, Any]]:
    expected_index = {fixture[0]: fixture[4] for fixture in NEGATIVE_FIXTURES}
    fixture_paths = sorted((adapter / "fixtures/negative").glob("*.json"))
    actual_ids: set[str] = set()
    results: list[dict[str, Any]] = []
    for path in fixture_paths:
        fixture = _read_canonical_json(path)
        fixture_id = fixture.get("fixture_id")
        actual_ids.add(fixture_id)
        expected_error = expected_index.get(fixture_id)
        if expected_error is None or fixture.get("expected_error") != expected_error:
            raise ValueError(f"B95 fixture declaration mismatch: {fixture_id}")
        errors = _all_errors(_mutated(fixture_id, baseline), baseline)
        if expected_error not in errors:
            raise ValueError(f"B95 fixture {fixture_id} did not raise {expected_error}; got {errors}")
        results.append({"fixture_id": fixture_id, "expected_error": expected_error, "result": "rejected"})
    if actual_ids != set(expected_index):
        raise ValueError("B95 negative fixture inventory is incomplete")
    return sorted(results, key=lambda row: row["fixture_id"])


def _expected_projection_files() -> set[str]:
    return set(JSONL_TO_KEY) | set(JSON_TO_KEY) | {
        "input/public-native-readback.json",
        "data/release-inventory.json",
        "views/B95.html",
        "views/B95-pengajar.html",
        "views/capabilities.json",
        "README.md",
    } | {f"fixtures/negative/{fixture[0]}.json" for fixture in NEGATIVE_FIXTURES}


def validate(native_root: Path, adapter: Path, *, write_receipt: bool = True) -> dict[str, Any]:
    expected = derive_projection(native_root)
    committed = load_adapter_bundle(adapter)
    errors = _all_errors(committed, expected)
    if errors:
        raise ValueError(f"B95 adapter invariant failures: {errors}")

    # Every emitted projection must match a fresh derivation exactly.
    for key in set(JSON_TO_KEY.values()) | set(JSONL_TO_KEY.values()):
        # JSON round-tripping turns integer map keys (the chapter page map)
        # into strings.  Compare canonical JSON identities so that this
        # representation detail cannot look like semantic drift.
        if canonical_json_bytes(committed.get(key)) != canonical_json_bytes(expected.get(key)):
            raise ValueError(f"B95 committed projection drift: {key}")

    completion_receipt = native_root / "qa/b039-publication/R011-B039_FINAL_COMPLETION_RECEIPT.json"
    receipt_path = adapter / "input/public-native-readback.json"
    if receipt_path.read_bytes() != completion_receipt.read_bytes():
        raise ValueError("B95 public-native completion receipt was not preserved byte-for-byte")

    manifest = _read_canonical_json(adapter / "manifest.json")
    if manifest.get("course_id") != COURSE_ID or manifest.get("boundary_id") != BOUNDARY_ID:
        raise ValueError("B95 manifest identity mismatch")
    declared = {row["path"] for row in manifest.get("outputs", [])}
    expected_paths = _expected_projection_files()
    if declared != expected_paths:
        raise ValueError(f"B95 manifest output inventory drift: {sorted(declared ^ expected_paths)}")
    for row in manifest.get("outputs", []):
        actual = identity(adapter / row["path"], display_path=row["path"])
        if actual != row:
            raise ValueError(f"B95 manifest output drift: {row['path']}")
    if manifest.get("counts") != expected["capabilities"]["counts"]:
        raise ValueError("B95 manifest count drift")
    if manifest.get("projection", {}).get("native_bodies_copied") is not False:
        raise ValueError("B95 manifest falsely claims native bodies")

    # JSON object keys are strings on disk even though the model's page-start
    # map uses integer keys.  Compare the normalized mapping explicitly so
    # this check tests the values rather than Python's key-type detail.
    toc = committed["public_evidence"].get("reader", {}).get("chapter_toc_page_starts", {})
    try:
        normalized_toc = {int(key): value for key, value in toc.items()}
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("B95 chapter TOC page-start map is not an object") from exc
    if normalized_toc != CHAPTER_PAGE_STARTS:
        raise ValueError("B95 chapter TOC page-start map drift")

    # The duplicate capabilities view is intentionally identical to data JSON.
    if (adapter / "views/capabilities.json").read_bytes() != (adapter / "data/capabilities.json").read_bytes():
        raise ValueError("B95 capabilities view drift")
    learner_html = (adapter / "views/B95.html").read_text(encoding="utf-8")
    educator_html = (adapter / "views/B95-pengajar.html").read_text(encoding="utf-8")
    if learner_html != render_learner(expected) or educator_html != render_educator(expected):
        raise ValueError("B95 HTML views are not deterministic projections")
    rendered_html = learner_html + educator_html
    if 'href="file:' in rendered_html or 'src="file:' in rendered_html or "C:\\" in rendered_html:
        raise ValueError("B95 views expose a local filesystem path")
    if "source_text" in rendered_html or "target_text" in rendered_html or "forbidden native body" in rendered_html:
        raise ValueError("B95 views expose native body markers")
    missing_unit_ids = [row["id"] for row in committed["unit_index"] if row["id"] not in educator_html]
    if missing_unit_ids:
        raise ValueError(f"B95 educator view omits unit identities: {missing_unit_ids[:5]}")

    if forbidden_content_paths(committed):
        raise ValueError("B95 projected JSON contains a forbidden content key")
    negative_results = _validate_negative_fixtures(adapter, expected)

    # Two fresh builds in temporary, bounded directories prove deterministic
    # output without touching the producer or central generated files.
    with tempfile.TemporaryDirectory(prefix="b95-capability-validation-") as temp:
        temp_root = Path(temp)
        run_a = temp_root / "run-a"
        run_b = temp_root / "run-b"
        build(native_root, run_a)
        build(native_root, run_b)
        identity_a = _tree_identity(run_a)
        identity_b = _tree_identity(run_b)
        identity_committed = _tree_identity(adapter)
        if identity_a != identity_b or identity_a != identity_committed:
            raise ValueError("B95 two-run build identity mismatch")

    checks = {
        "canonical_machine_files": True,
        "fresh_projection_matches_native": True,
        "canonical_export_hashes_bound": True,
        "public_completion_receipt_preserved_byte_for_byte": True,
        "component_rights_preserved": len(committed["rights_index"]) == 80,
        "native_bodies_absent": True,
        "public_github_zenodo_readback_preserved": True,
        "public_reader_pages": 462,
        "two_run_build_identity": identity_a,
        "negative_fixtures_rejected": len(negative_results),
        "expected_record_counts": EXPECTED_RECORD_COUNTS,
        "expected_unit_kinds": EXPECTED_UNIT_KINDS,
    }
    validation = {
        "schema": "b95-capability-validation/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "result": "pass",
        "checks": checks,
        "counts": committed["capabilities"]["counts"],
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
    print(canonical_json_bytes({"state": result["result"], "course_id": COURSE_ID, "negative_fixtures": len(result["negative_fixtures"]), "tree_sha256": result["checks"]["two_run_build_identity"]["tree_sha256"]}).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
