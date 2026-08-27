#!/usr/bin/env python3
"""Validate and authority-replay the O001/A00 assessment inventory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            raise ValueError(f"blank JSONL line: {path}:{line_number}")
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"non-object JSONL row: {path}:{line_number}")
        rows.append(row)
    return rows


def import_builder(package_root: Path):
    path = package_root / "tools/build_o001_a00_assessments.py"
    spec = importlib.util.spec_from_file_location("o001_a00_builder", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load builder module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_checksums(package_root: Path) -> dict[str, Any]:
    checksum_path = package_root / "CHECKSUMS.sha256"
    checksum_bytes = checksum_path.read_bytes()
    rows = []
    for line in checksum_bytes.decode("utf-8").splitlines():
        digest, separator, relative_path = line.partition("  ")
        if separator != "  " or len(digest) != 64 or not relative_path:
            raise ValueError(f"invalid checksum line: {line!r}")
        rows.append((relative_path, digest))
    if [path for path, _ in rows] != sorted(path for path, _ in rows):
        raise ValueError("checksum paths are not canonically sorted")
    if len({path for path, _ in rows}) != len(rows):
        raise ValueError("duplicate checksum path")
    for relative_path, digest in rows:
        path = package_root / relative_path
        if not path.is_file() or sha256_bytes(path.read_bytes()) != digest:
            raise ValueError(f"checksum mismatch: {relative_path}")
    actual_bound = sorted(
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_file()
        and path.relative_to(package_root).as_posix()
        not in {"CHECKSUMS.sha256", "seal.json"}
    )
    if actual_bound != [path for path, _ in rows]:
        raise ValueError("checksum inventory does not close over package files")
    seal = load_json(package_root / "seal.json")
    if seal["bound_paths"] != actual_bound:
        raise ValueError("seal bound paths mismatch")
    if seal["bound_file_count"] != len(actual_bound):
        raise ValueError("seal file count mismatch")
    if seal["checksum_manifest_bytes"] != len(checksum_bytes):
        raise ValueError("seal checksum-manifest byte count mismatch")
    if seal["checksum_manifest_sha256"] != sha256_bytes(checksum_bytes):
        raise ValueError("seal checksum-manifest hash mismatch")
    total = sum((package_root / path).stat().st_size for path in actual_bound)
    if seal["bound_total_bytes"] != total:
        raise ValueError("seal bound byte count mismatch")
    return {
        "bound_file_count": len(actual_bound),
        "bound_total_bytes": total,
        "checksum_manifest_bytes": len(checksum_bytes),
        "checksum_manifest_sha256": sha256_bytes(checksum_bytes),
    }


def validate(owner_root: Path, package_root: Path) -> dict[str, Any]:
    manifest = load_json(package_root / "manifest.json")
    if canonical_json_bytes(manifest) != (package_root / "manifest.json").read_bytes():
        raise ValueError("manifest is not canonical JSON")
    seal_result = verify_checksums(package_root)
    builder = import_builder(package_root)
    if manifest["package_id"] != builder.PACKAGE_ID:
        raise ValueError("package ID mismatch")
    if manifest["authority"]["source_commit"] != builder.SOURCE_COMMIT:
        raise ValueError("source commit mismatch")

    schema = load_json(package_root / "schema/assessment-inventory-v1.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    rows = {
        "assessments": load_jsonl(package_root / "data/assessments.jsonl"),
        "assessment_components": load_jsonl(
            package_root / "data/assessment-components.jsonl"
        ),
        "solution_gaps": load_jsonl(package_root / "data/solution-gaps.jsonl"),
        "module_summaries": load_jsonl(package_root / "summaries/modules.jsonl"),
    }
    for table in (
        "assessments",
        "assessment_components",
        "solution_gaps",
        "module_summaries",
    ):
        for index, row in enumerate(rows[table]):
            errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
            if errors:
                raise ValueError(
                    f"schema failure {table}[{index}]: "
                    + "; ".join(error.message for error in errors[:5])
                )

    modules, authority = builder.read_authority(owner_root)
    replay = builder.build_records(modules)
    if authority != manifest["authority"]:
        raise ValueError("live authority replay differs from manifest")
    for table, relative_path in {
        "assessments": "data/assessments.jsonl",
        "assessment_components": "data/assessment-components.jsonl",
        "solution_gaps": "data/solution-gaps.jsonl",
        "module_summaries": "summaries/modules.jsonl",
    }.items():
        expected_bytes = builder.canonical_jsonl_bytes(replay[table])
        if expected_bytes != (package_root / relative_path).read_bytes():
            raise ValueError(f"authority replay byte mismatch: {relative_path}")

    all_ids = []
    for table in ("assessments", "assessment_components", "solution_gaps"):
        all_ids.extend(row["id"] for row in rows[table])
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("stable IDs are not globally unique")
    assessment_ids = {row["id"] for row in rows["assessments"]}
    component_counts: dict[str, dict[str, int]] = {
        assessment_id: {"statement": 0, "solution": 0}
        for assessment_id in assessment_ids
    }
    for row in rows["assessment_components"]:
        if row["assessment_id"] not in assessment_ids:
            raise ValueError(f"orphan assessment component: {row['id']}")
        component_counts[row["assessment_id"]][row["component_kind"]] += 1
    for row in rows["assessments"]:
        actual = component_counts[row["id"]]
        if actual["statement"] != row["problem_component_count"]:
            raise ValueError(f"problem-component closure mismatch: {row['id']}")
        if actual["solution"] != row["solution_component_count"]:
            raise ValueError(f"solution-component closure mismatch: {row['id']}")

    expected_gap_assessments = {
        row["id"]
        for row in rows["assessments"]
        if row["solution_availability"] == "missing_source_and_target"
    }
    actual_gap_assessments = {row["assessment_id"] for row in rows["solution_gaps"]}
    if expected_gap_assessments != actual_gap_assessments:
        raise ValueError("solution-gap set is not exact")

    counts = {
        "assessment_components": len(rows["assessment_components"]),
        "assessments": len(rows["assessments"]),
        "modules": len(rows["module_summaries"]),
        "problems": sum(
            row["native_tag"] == "problem" for row in rows["assessment_components"]
        ),
        "solutions": sum(
            row["native_tag"] == "solution" for row in rows["assessment_components"]
        ),
        "solution_gaps": len(rows["solution_gaps"]),
    }
    if counts != manifest["counts"] or counts != builder.EXPECTED:
        raise ValueError(f"count mismatch: {counts}")
    if manifest["projection_contract"]["sealed_v22_package_mutated"] is not False:
        raise ValueError("sealed-package mutation policy mismatch")

    report = load_json(package_root / "validation-report.json")
    if report["validation_state"] != "pass" or report["counts"] != counts:
        raise ValueError("validation report mismatch")
    return {
        "authority_replay": "pass",
        "counts": counts,
        "json_schema": "pass",
        "package_root": package_root.name,
        "seal": seal_result,
        "solution_gap_exact_set": "pass",
        "stable_id_uniqueness": "pass",
        "validation_state": "pass",
        "zero_prose": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", required=True, type=Path)
    parser.add_argument("--package-root", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.owner_root.resolve(), args.package_root.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
