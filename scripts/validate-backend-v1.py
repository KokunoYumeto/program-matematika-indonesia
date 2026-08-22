#!/usr/bin/env python3
"""Independently validate a common-backend v1 package and optional replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"{path}:{line_number}: missing LF terminator")
            if "\r" in line:
                raise ValueError(f"{path}:{line_number}: CR is not canonical")
            row = json.loads(line)
            if line[:-1] != canonical(row):
                raise ValueError(f"{path}:{line_number}: noncanonical JSON")
            rows.append(row)
    return rows


def read_lossless_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["id", "record_type", "record_json"]:
            raise ValueError(f"{path}: invalid CSV header {reader.fieldnames}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            record = json.loads(row["record_json"])
            if row["record_json"] != canonical(record):
                raise ValueError(f"{path}:{line_number}: noncanonical record_json")
            if row["id"] != record["id"] or row["record_type"] != record["record_type"]:
                raise ValueError(f"{path}:{line_number}: projection identity mismatch")
            rows.append(record)
        return rows


def inventory(package: Path, manifest: dict) -> None:
    declared = {entry["path"]: entry for entry in manifest["files"]}
    actual = {
        path.relative_to(package).as_posix(): path
        for path in package.rglob("*")
        if path.is_file() and path.name not in {"manifest.json", "validation_report.json"}
    }
    if set(declared) != set(actual):
        raise ValueError(
            f"manifest inventory mismatch missing={sorted(set(declared)-set(actual))} extra={sorted(set(actual)-set(declared))}"
        )
    for relative, entry in declared.items():
        path = actual[relative]
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"byte mismatch: {relative}")
        if sha256_file(path) != entry["sha256"]:
            raise ValueError(f"hash mismatch: {relative}")


def referenced_urns(value: object, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_urns(child, (*path, str(index)))
    elif isinstance(value, str) and value.startswith("urn:uuid:"):
        yield path, value


def validate_package(package: Path, schema_path: Path) -> dict:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    profile_path = package / "schema" / "source-format-profile-v1.schema.json"
    profile_schema = json.loads(profile_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(profile_schema)
    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    backend_path = package / "backend.json"
    backend = json.loads(backend_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(backend),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"schema failure at {list(first.absolute_path)}: {first.message}")

    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    inventory(package, manifest)

    table_names = sorted(backend["tables"])
    schema_tables = sorted(schema["properties"]["tables"]["properties"])
    if table_names != schema_tables:
        raise ValueError("backend table inventory does not match schema")

    all_rows: list[dict] = []
    table_counts: dict[str, int] = {}
    for table_name in table_names:
        expected = backend["tables"][table_name]
        jsonl_rows = read_jsonl(package / "data" / f"{table_name}.jsonl")
        csv_rows = read_lossless_csv(package / "csv" / f"{table_name}.csv")
        if expected != jsonl_rows or expected != csv_rows:
            raise ValueError(f"table projection round-trip mismatch: {table_name}")
        if expected != sorted(expected, key=lambda row: row["id"]):
            raise ValueError(f"table not ID-sorted: {table_name}")
        table_counts[table_name] = len(expected)
        all_rows.extend(expected)

    all_rows = sorted(all_rows, key=lambda row: (row["record_type"], row["id"]))
    if all_rows != read_jsonl(package / "records.jsonl"):
        raise ValueError("complete records.jsonl mismatch")
    if all_rows != read_lossless_csv(package / "records.csv"):
        raise ValueError("complete records.csv round-trip mismatch")

    ids = [row["id"] for row in all_rows]
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate IDs: {duplicates[:10]}")
    known = set(ids)
    validated_source_profiles = 0
    for row in all_rows:
        profile = row.get("extensions", {}).get("interlanguage.source-profile")
        if profile is not None:
            profile_validator.validate(profile)
            validated_source_profiles += 1
    dangling = []
    for row in all_rows:
        for field_path, value in referenced_urns(row):
            if field_path == ("id",):
                continue
            # source/supersession IDs may legitimately point to an immutable
            # predecessor package. All other canonical references must close.
            leaf = field_path[-1] if field_path else ""
            if leaf in {"supersedes_id", "source_edition_id", "source_revision_id", "source_variant_id", "source_occurrence_id"}:
                continue
            if value not in known:
                dangling.append({"record": row["id"], "path": "/".join(field_path), "value": value})
    if dangling:
        raise ValueError(f"dangling canonical references: {dangling[:10]}")

    if manifest["record_count"] != len(all_rows) or manifest["table_counts"] != table_counts:
        raise ValueError("manifest record/table counts mismatch")
    if manifest["dataset_id"] != backend["dataset_id"] or manifest["dataset_version"] != backend["dataset_version"]:
        raise ValueError("manifest dataset identity mismatch")

    return {
        "schema": "pass",
        "manifest_inventory": "pass",
        "jsonl_canonicalization": "pass",
        "csv_lossless_roundtrip": "pass",
        "global_id_uniqueness": "pass",
        "foreign_key_closure": "pass",
        "recognized_source_profile_validation": "pass",
        "recognized_source_profile_count": validated_source_profiles,
        "record_count": len(all_rows),
        "table_count": len(table_names),
        "nonempty_table_count": sum(bool(count) for count in table_counts.values()),
        "table_counts": table_counts,
        "backend_sha256": sha256_file(backend_path),
        "records_jsonl_sha256": sha256_file(package / "records.jsonl"),
        "records_csv_sha256": sha256_file(package / "records.csv"),
        "manifest_sha256": sha256_file(package / "manifest.json"),
    }


def compare_replay(package: Path, replay: Path) -> dict:
    ignored = {"validation_report.json"}
    first = {p.relative_to(package).as_posix(): p for p in package.rglob("*") if p.is_file() and p.name not in ignored}
    second = {p.relative_to(replay).as_posix(): p for p in replay.rglob("*") if p.is_file() and p.name not in ignored}
    if set(first) != set(second):
        raise ValueError("replay file inventory mismatch")
    mismatches = []
    for relative in sorted(first):
        if first[relative].stat().st_size != second[relative].stat().st_size or sha256_file(first[relative]) != sha256_file(second[relative]):
            mismatches.append(relative)
    if mismatches:
        raise ValueError(f"replay byte mismatch: {mismatches[:10]}")
    return {"result": "byte-identical", "file_count": len(first)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--replay-package", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    result = validate_package(args.package, args.schema)
    result["deterministic_replay"] = compare_replay(args.package, args.replay_package) if args.replay_package else {"result": "not_requested"}
    report = {
        "schema_name": "interlanguage-math-modular-backend-validation",
        "schema_version": "1.0.0",
        "package": args.package.name,
        "result": "pass",
        "checks": result,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(canonical(report))


if __name__ == "__main__":
    main()
