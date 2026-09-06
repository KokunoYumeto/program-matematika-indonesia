"""Validate the D90 capability adapter and its zero-copy claim boundaries."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from build_d90_capability_v1 import (
    NEGATIVE_FIXTURES,
    build,
    render_educator,
    render_learner,
)
from d90_capability_model_v1 import (
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_PUBLIC_IDENTITIES,
    RELEASE_COMMIT,
    RELEASE_TREE,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    identity,
    native_git_identity,
    projection_errors,
    read_canonical_jsonl,
    read_json,
    sha256_bytes,
    write_json,
)


JSONL_TO_KEY = {
    "data/native-record-index.jsonl": "native_record_index",
    "data/rights-index.jsonl": "rights_index",
    "data/corrections-index.jsonl": "corrections_index",
    "data/terms-index.jsonl": "terms_index",
    "data/shared-learning-surfaces.jsonl": "shared_surfaces",
    "data/staged-relations.jsonl": "staged_relations",
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
        if relative in {"validation.json", "build/PACKET_BUILD_RECEIPT.json"} or relative.startswith("build/"):
            continue
        files.append(identity(path, display_path=relative))
    return {
        "files": files,
        "file_count": len(files),
        "tree_sha256": sha256_bytes(canonical_json_bytes(files)),
    }


def _source_lock_errors(
    bundle: dict[str, Any], expected: dict[str, Any]
) -> list[str]:
    return [] if bundle.get("source_lock") == expected.get("source_lock") else ["D90-SOURCE-LOCK"]


def _all_errors(bundle: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return sorted(set(projection_errors(bundle) + _source_lock_errors(bundle, expected)))


def _mutated(fixture_id: str, baseline: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(baseline)
    if fixture_id == "hash-drift":
        value["source_lock"]["inputs"][1]["sha256"] = "00" * 32
    elif fixture_id == "altered-native-id":
        value["native_record_index"][0]["id"] = "program.d90.changed"
    elif fixture_id == "dropped-native-id":
        value["native_record_index"].pop()
    elif fixture_id == "collapsed-absence-states":
        for row in value["native_record_index"]:
            row.pop("presence", None)
    elif fixture_id == "flattened-rights":
        for row in value["rights_index"]:
            row["component_id"] = "component.all"
    elif fixture_id == "bad-anchor":
        value["shared_surfaces"][0]["public_anchor"] = "https://example.invalid/#lost"
    elif fixture_id == "copied-body":
        value["learner_map"]["body"] = "forbidden native body"
    elif fixture_id == "false-lab-completion":
        value["claim_boundary"]["lab_completion_claimed"] = True
    elif fixture_id == "false-accessibility":
        value["public_evidence"]["accessibility"]["wcag_conformance_claimed"] = True
    elif fixture_id == "false-reversibility":
        value["claim_boundary"]["reversible_exchange_claimed"] = True
    elif fixture_id == "false-live-results":
        value["claim_boundary"]["learner_result_instances"] = 1
    elif fixture_id == "false-universal-solution-coverage":
        value["claim_boundary"]["full_solution_coverage_beyond_observed_records_claimed"] = True
    elif fixture_id == "case-key-collapsed":
        value["capabilities"]["case_sensitive_key_caveat"]["collisions"] = []
    else:
        raise ValueError(f"Unknown D90 negative fixture: {fixture_id}")
    return value


def _validate_negative_fixtures(
    adapter: Path, baseline: dict[str, Any]
) -> list[dict[str, Any]]:
    expected_index = {fixture[0]: fixture[4] for fixture in NEGATIVE_FIXTURES}
    fixture_paths = sorted((adapter / "fixtures/negative").glob("*.json"))
    actual_ids: set[str] = set()
    results = []
    for path in fixture_paths:
        fixture = _read_canonical_json(path)
        fixture_id = fixture["fixture_id"]
        actual_ids.add(fixture_id)
        expected = expected_index.get(fixture_id)
        if expected is None or fixture.get("expected_error") != expected:
            raise ValueError(f"D90 fixture declaration mismatch: {fixture_id}")
        errors = _all_errors(_mutated(fixture_id, baseline), baseline)
        if expected not in errors:
            raise ValueError(
                f"D90 fixture {fixture_id} did not raise {expected}; got {errors}"
            )
        results.append(
            {"fixture_id": fixture_id, "expected_error": expected, "result": "rejected"}
        )
    if actual_ids != set(expected_index):
        raise ValueError("D90 negative fixture inventory is incomplete")
    return sorted(results, key=lambda row: row["fixture_id"])


def validate(native_root: Path, adapter: Path, *, write_receipt: bool = True) -> dict[str, Any]:
    expected = derive_projection(native_root)
    committed = load_adapter_bundle(adapter)
    errors = _all_errors(committed, expected)
    if errors:
        raise ValueError(f"D90 adapter invariant failures: {errors}")

    for key in expected:
        if committed[key] != expected[key]:
            raise ValueError(f"D90 committed projection drift: {key}")

    manifest = _read_canonical_json(adapter / "manifest.json")
    if manifest.get("course_id") != COURSE_ID:
        raise ValueError("D90 manifest identity mismatch")
    for row in manifest.get("outputs", []):
        actual = identity(adapter / row["path"], display_path=row["path"])
        if actual != row:
            raise ValueError(f"D90 manifest output drift: {row['path']}")

    learner_html = (adapter / "views/D90.html").read_text(encoding="utf-8")
    educator_html = (adapter / "views/D90-pengajar.html").read_text(encoding="utf-8")
    if learner_html != render_learner(committed) or educator_html != render_educator(committed):
        raise ValueError("D90 views are not deterministic map projections")
    if "file:" in learner_html + educator_html or "C:\\" in learner_html + educator_html:
        raise ValueError("D90 views expose a local path")
    projected_html = learner_html + educator_html
    missing_view_ids = [
        row["id"]
        for row in committed["shared_surfaces"]
        if row["id"] not in projected_html
    ]
    if missing_view_ids:
        raise ValueError(
            f"D90 learner/educator views omit shared identities: {missing_view_ids}"
        )

    negative_results = _validate_negative_fixtures(adapter, expected)
    with tempfile.TemporaryDirectory(prefix="d90-capability-validation-") as temp:
        temp_root = Path(temp)
        run_a = temp_root / "run-a"
        run_b = temp_root / "run-b"
        build(native_root, run_a)
        build(native_root, run_b)
        identity_a = _tree_identity(run_a)
        identity_b = _tree_identity(run_b)
        identity_committed = _tree_identity(adapter)
        if identity_a != identity_b or identity_a != identity_committed:
            raise ValueError("D90 two-run build identity mismatch")

    public = committed["public_evidence"]["zenodo"]["files"]
    public_by_name = {row["filename"]: row for row in public}
    expected_public = {
        "backend-records-2026.08.28-integrated.jsonl": EXPECTED_PUBLIC_IDENTITIES["backend_jsonl"],
        "backend-records-2026.08.28-integrated.csv": EXPECTED_PUBLIC_IDENTITIES["backend_csv"],
        "backend-schema.json": EXPECTED_PUBLIC_IDENTITIES["backend_schema"],
        "D90-O015-optimisasi-lanjut-analisis-konveks-id.html": EXPECTED_PUBLIC_IDENTITIES["integrated_html"],
        "D90-O015-optimisasi-lanjut-analisis-konveks-id.pdf": EXPECTED_PUBLIC_IDENTITIES["integrated_pdf"],
        "D90-O015-optimisasi-lanjut-analisis-konveks-id.epub": EXPECTED_PUBLIC_IDENTITIES["integrated_epub"],
    }
    for name, expected_identity in expected_public.items():
        actual = public_by_name.get(name, {})
        if {key: actual.get(key) for key in ("bytes", "sha256")} != expected_identity:
            raise ValueError(f"D90 public identity mismatch: {name}")

    receipt = {
        "schema": "d90-capability-validation/1",
        "course_id": COURSE_ID,
        "result": "pass",
        "native_release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE},
        "native_git_identity": native_git_identity(native_root),
        "checks": {
            "canonical_machine_files": True,
            "committed_projection_matches_native": True,
            "component_specific_rights_preserved": True,
            "content_bodies_absent": True,
            "csv_jsonl_lossless_native_receipt_preserved": True,
            "public_anchor_observations": 438,
            "public_hash_receipts_preserved": len(expected_public),
            "two_run_build_identity": identity_a,
        },
        "counts": committed["capabilities"]["counts"],
        "negative_fixtures": negative_results,
    }
    if write_receipt:
        write_json(adapter / "validation.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    receipt = validate(
        args.native_root.resolve(), args.adapter.resolve(), write_receipt=not args.no_write
    )
    print(
        canonical_json_bytes(
            {
                "state": receipt["result"],
                "course_id": COURSE_ID,
                "native_records": receipt["counts"]["native_records"],
                "original03_surfaces": receipt["counts"]["original03_surfaces"],
                "negative_fixtures": len(receipt["negative_fixtures"]),
                "two_run_tree_sha256": receipt["checks"]["two_run_build_identity"]["tree_sha256"],
            }
        ).decode("utf-8"),
        end="",
    )


if __name__ == "__main__":
    main()
