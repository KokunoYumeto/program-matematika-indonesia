#!/usr/bin/env python3
"""Validate any corpus-neutral backend-v2.3.1 lane-adapter package."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from v231_adapter_common import (
    CAPABILITY_NAMES,
    RECORD_TYPE_BY_TABLE,
    ROW_ENVELOPE_KEYS,
    TABLE_ORDER,
    AdapterError,
    assert_file_fact,
    compact_json,
    identity_set_sha256,
    inventory_sha256,
    parse_checksum_file,
    read_json,
    read_jsonl,
    require,
    safe_relative_path,
    sha256_bytes,
    sha256_file,
    tree_identity,
    write_json,
)


SIDECAR_SCHEMAS = {
    "capability-declarations-v0.2.0.json": "capability-declarations-v0.2.schema.json",
    "namespace-crosswalk-v0.2.0.json": "namespace-crosswalk-v0.2.schema.json",
    "translation-state-index-v0.2.0.json": "translation-state-index-v0.2.schema.json",
    "csv-projection-manifest-v0.2.0.json": "csv-projection-manifest-v0.2.schema.json",
    "scope-declaration-v0.2.0.json": "scope-declaration-v0.2.schema.json",
}

TEXT_SUFFIXES = {".json", ".jsonl", ".csv", ".md", ".py", ".txt", ".sha256"}
SECRET_PATTERNS = [
    ("absolute_windows_user_path", re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE)),
    ("github_classic_token", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("github_fine_grained_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("authorization_bearer_header", re.compile(r"Authorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/-]{16,}", re.IGNORECASE)),
    ("zenodo_access_token_query", re.compile(r"access_token=[A-Za-z0-9._~-]{16,}", re.IGNORECASE)),
]


def fact_path(root: Path, fact: Mapping[str, Any]) -> Path:
    relative = safe_relative_path(str(fact["path"]))
    return root.joinpath(*PurePosixPath(relative).parts)


def validate_schema(instance: Any, schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "$"
        raise AdapterError(f"schema failure {label} at {location}: {first.message}")


def validate_external_fact(
    fact: Mapping[str, Any],
    repository_root: Path | None,
    owner_root: Path | None,
    require_authorities: bool,
) -> bool:
    base = fact.get("path_base")
    if base == "package_root":
        return True
    root = repository_root if base == "program_repository_root" else owner_root if base == "owner_package_root" else None
    if root is None:
        require(not require_authorities, f"root not supplied for authority: {base}:{fact['path']}")
        return False
    assert_file_fact(root, fact)
    return True


def validate_manifest_files(package: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    declared = manifest["files"]
    require(isinstance(declared, list) and declared, "manifest files are empty")
    declared_paths = [safe_relative_path(str(fact["path"])) for fact in declared]
    require(len(declared_paths) == len(set(declared_paths)), "duplicate manifest file paths")
    for fact in declared:
        require(fact.get("path_base", "package_root") == "package_root", f"manifest payload is not package-root based: {fact['path']}")
        assert_file_fact(package, fact)
    actual = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path.relative_to(package).as_posix() not in {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}
    }
    require(set(declared_paths) == actual, "manifest payload inventory differs from physical package")
    payload_identity = inventory_sha256(declared)
    require(manifest["build"]["build_a_sha256"] == payload_identity, "build A digest does not bind manifest payload")
    require(manifest["build"]["build_b_sha256"] == payload_identity, "build B digest does not bind manifest payload")
    return {"files": len(declared), "bytes": sum(int(fact["bytes"]) for fact in declared), "sha256": payload_identity}


def validate_seal_and_checksums(package: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    seal = read_json(package / "seal.json")
    require(seal.get("algorithm") == "sha256-sorted-path-bytes-v1", "unsupported seal algorithm")
    require(seal.get("seal_excluded_from_own_digest") is True, "seal self-exclusion missing")
    require(seal.get("package_id") == manifest["package_id"], "seal package ID mismatch")
    seal_facts = seal.get("files")
    require(isinstance(seal_facts, list), "seal files missing")
    manifest_fact = {
        "path": "manifest.json",
        "bytes": (package / "manifest.json").stat().st_size,
        "sha256": sha256_file(package / "manifest.json"),
    }
    expected = {
        str(fact["path"]): (int(fact["bytes"]), str(fact["sha256"]))
        for fact in list(manifest["files"]) + [manifest_fact]
    }
    observed = {str(fact["path"]): (int(fact["bytes"]), str(fact["sha256"])) for fact in seal_facts}
    require(observed == expected, "seal inventory differs from manifest payload plus manifest")
    for fact in seal_facts:
        assert_file_fact(package, fact)
    require(seal.get("file_count") == len(seal_facts), "seal file count mismatch")
    require(seal.get("bytes") == sum(int(fact["bytes"]) for fact in seal_facts), "seal byte aggregate mismatch")
    require(seal.get("aggregate_sha256") == inventory_sha256(seal_facts), "seal aggregate mismatch")

    checksum_rows = parse_checksum_file(package / "PACKAGE_CHECKSUMS.sha256")
    expected_checksum_paths = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path.relative_to(package).as_posix() != "PACKAGE_CHECKSUMS.sha256"
    }
    require({relative for _, relative in checksum_rows} == expected_checksum_paths, "checksum inventory differs from physical package")
    for digest, relative in checksum_rows:
        path = package.joinpath(*PurePosixPath(relative).parts)
        require(sha256_file(path) == digest, f"checksum mismatch: {relative}")
    return {
        "seal_files": len(seal_facts),
        "seal_sha256": sha256_file(package / "seal.json"),
        "checksum_entries": len(checksum_rows),
        "checksums_sha256": sha256_file(package / "PACKAGE_CHECKSUMS.sha256"),
    }


def validate_tables(package: Path, dataset_id: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    global_ids: set[str] = set()
    semantic_pairs: set[tuple[str, str]] = set()
    record_counts: dict[str, int] = {}
    for table_name in TABLE_ORDER:
        path = package / "tables" / f"{table_name}.jsonl"
        require(path.is_file(), f"missing canonical table: {table_name}")
        rows = read_jsonl(path)
        expected_type = RECORD_TYPE_BY_TABLE[table_name]
        for ordinal, row in enumerate(rows, 1):
            require(set(row) == ROW_ENVELOPE_KEYS, f"bad row envelope: {table_name}:{ordinal}")
            require(row["record_type"] == expected_type, f"record type mismatch: {table_name}:{ordinal}")
            require(row["dataset_id"] == dataset_id, f"dataset mismatch: {table_name}:{ordinal}")
            require(isinstance(row["payload"], dict), f"non-object payload: {table_name}:{ordinal}")
            require(str(row["id"]).startswith("urn:uuid:"), f"non-UUID projected ID: {table_name}:{ordinal}")
            require(row["id"] not in global_ids, f"duplicate projected ID: {row['id']}")
            require((expected_type, str(row["semantic_key"])) not in semantic_pairs, f"duplicate semantic key: {table_name}:{ordinal}")
            global_ids.add(str(row["id"]))
            semantic_pairs.add((expected_type, str(row["semantic_key"])))
        tables[table_name] = rows
        record_counts[table_name] = len(rows)
    return tables, {
        "records": sum(record_counts.values()),
        "global_ids": len(global_ids),
        "record_counts": record_counts,
        "identity_set_sha256": identity_set_sha256(global_ids),
    }


def validate_csv(package: Path, tables: Mapping[str, list[dict[str, Any]]], csv_manifest: Mapping[str, Any]) -> dict[str, Any]:
    require(csv_manifest["table_order"] == TABLE_ORDER, "CSV table order drift")
    entries = csv_manifest["tables"]
    require([entry["table"] for entry in entries] == TABLE_ORDER, "CSV table entries drift")
    global_expected: list[list[str]] = []
    csv_facts: list[Mapping[str, Any]] = []
    for entry in entries:
        table_name = entry["table"]
        jsonl_path = package / "tables" / f"{table_name}.jsonl"
        csv_path = package / "csv" / f"{table_name}.csv"
        assert_file_fact(package, entry["source_jsonl"])
        assert_file_fact(package, entry["csv"])
        with csv_path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        require(rows and rows[0] == ["stable_id", "record_type", "canonical_record_json"], f"CSV header mismatch: {table_name}")
        body = rows[1:]
        require(len(body) == len(tables[table_name]) == entry["records"], f"CSV row count mismatch: {table_name}")
        reconstructed: list[str] = []
        for ordinal, (csv_row, record) in enumerate(zip(body, tables[table_name], strict=True), 1):
            require(len(csv_row) == 3, f"CSV width mismatch: {table_name}:{ordinal}")
            require(csv_row[0] == record["id"] and csv_row[1] == record["record_type"], f"CSV identity mismatch: {table_name}:{ordinal}")
            require(csv_row[2] == compact_json(record), f"CSV canonical JSON mismatch: {table_name}:{ordinal}")
            reconstructed.append(csv_row[2] + "\n")
            global_expected.append([f"tables/{table_name}.jsonl", str(ordinal), csv_row[0], csv_row[1], csv_row[2]])
        reconstructed_bytes = "".join(reconstructed).encode("utf-8")
        require(reconstructed_bytes == jsonl_path.read_bytes(), f"CSV round trip mismatch: {table_name}")
        require(entry["roundtrip_sha256"] == sha256_bytes(reconstructed_bytes), f"CSV roundtrip digest mismatch: {table_name}")
        require(entry["roundtrip_state"] == "pass", f"CSV roundtrip state mismatch: {table_name}")
        csv_facts.append(entry["csv"])

    global_expected.sort(key=lambda row: (row[3], row[2], row[0], int(row[1])))
    with (package / "records.csv").open("r", encoding="utf-8", newline="") as stream:
        global_rows = list(csv.reader(stream))
    require(global_rows and global_rows[0] == ["source_jsonl_path", "source_row_ordinal", "stable_id", "record_type", "canonical_record_json"], "global CSV header mismatch")
    require(global_rows[1:] == global_expected, "global CSV rows differ from canonical table projection")
    records_fact = csv_manifest["records_csv"]
    assert_file_fact(package, records_fact)
    require(records_fact["records"] == len(global_expected), "global CSV record count mismatch")
    require(records_fact["roundtrip_sha256"] == sha256_bytes("".join(row[4] + "\n" for row in global_expected).encode("utf-8")), "global CSV roundtrip digest mismatch")
    csv_facts.append(records_fact)
    require(csv_manifest["aggregate_sha256"] == inventory_sha256(csv_facts), "CSV aggregate digest mismatch")
    return {"tables": len(entries), "records": len(global_expected), "roundtrip": "pass"}


def validate_sidecars(package: Path, manifest: Mapping[str, Any], tables: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    package_id = manifest["package_id"]
    dataset_id = manifest["dataset_id"]
    schema_root = package / "schema"
    sidecars: dict[str, Any] = {}
    for filename, schema_name in SIDECAR_SCHEMAS.items():
        instance = read_json(package / filename)
        validate_schema(instance, schema_root / schema_name, filename)
        require(instance["package_id"] == package_id, f"sidecar package ID mismatch: {filename}")
        if "dataset_id" in instance:
            require(instance["dataset_id"] == dataset_id, f"sidecar dataset ID mismatch: {filename}")
        sidecars[filename] = instance

    capability = sidecars["capability-declarations-v0.2.0.json"]
    names = [row["name"] for row in capability["capabilities"]]
    require(names == CAPABILITY_NAMES, "capability names/order drift")
    require(len(set(names)) == 10, "duplicate capability names")

    scope = sidecars["scope-declaration-v0.2.0.json"]
    require(scope["aggregate_conformance_claim"] is False, "aggregate conformance claim must remain false")
    require(scope["scope_kind"] == "lane_adapter", "scope is not lane-adapter")
    require(scope["course_ids"] and scope["curriculum_role_ids"], "lane scope is empty")

    crosswalk = sidecars["namespace-crosswalk-v0.2.0.json"]
    projected_ids = {row["id"] for rows in tables.values() for row in rows}
    materialized_types = set(RECORD_TYPE_BY_TABLE.values())
    pairs: set[tuple[str, str, str, str]] = set()
    for mapping in crosswalk["mappings"]:
        key = (
            mapping["source_namespace"],
            mapping["source_record_id"],
            mapping["target_namespace"],
            mapping["target_record_id"],
        )
        require(key not in pairs, "duplicate namespace mapping")
        pairs.add(key)
        if mapping["target_record_type"] in materialized_types:
            require(mapping["target_record_id"] in projected_ids, f"crosswalk target is not materialized: {mapping['target_record_id']}")

    translation = sidecars["translation-state-index-v0.2.0.json"]
    records = translation["records"]
    require(translation["coverage"]["indexed_rows"] == len(records), "translation indexed-row count mismatch")
    require(translation["coverage"]["inferred_rows"] == 0 and translation["no_inference"] is True, "translation index infers state")
    projected_unit_ids = {row["id"] for row in tables["units"]}
    indexed_ids = [str(row["projected_unit_id"]) for row in records]
    require(len(indexed_ids) == len(set(indexed_ids)), "duplicate translation-state unit IDs")
    require(set(indexed_ids).issubset(projected_unit_ids), "translation index references unmaterialized units")
    require(translation["identity_set_sha256"] == identity_set_sha256(indexed_ids), "translation identity-set digest mismatch")

    return {
        "capabilities": len(names),
        "namespace_mappings": len(crosswalk["mappings"]),
        "translation_rows": len(records),
        "scope_roles": scope["curriculum_role_ids"],
        "csv": validate_csv(package, tables, sidecars["csv-projection-manifest-v0.2.0.json"]),
    }


def validate_no_leaks(package: Path) -> dict[str, Any]:
    scanned = 0
    for path in sorted(item for item in package.rglob("*") if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise AdapterError(f"text-like file is not UTF-8: {path.relative_to(package).as_posix()}") from exc
        scanned += 1
        for label, pattern in SECRET_PATTERNS:
            require(not pattern.search(text), f"privacy/credential pattern {label}: {path.relative_to(package).as_posix()}")
    return {"text_files_scanned": scanned, "credential_or_local_path_hits": 0}


def validate_package(args: argparse.Namespace) -> dict[str, Any]:
    package = args.package.resolve()
    require(package.is_dir(), f"package directory missing: {package}")
    manifest = read_json(package / "manifest.json")
    schema_path = package / "schema" / "lane-adapter-v2.3.1.schema.json"
    validate_schema(manifest, schema_path, "manifest.json")
    require(manifest["schema_version"] == "2.3.1", "wrong adapter contract")
    require(manifest["zero_copy_policy"] == {
        "owner_native_authoritative": True,
        "full_prose_centralized": False,
        "owner_ids_reminted": False,
        "aggregate_conformance_claim": False,
        "machine_data_is_learner_destination": False,
        "machine_surfaces_secondary": True,
    }, "zero-copy policy drift")

    manifest_payload = validate_manifest_files(package, manifest)
    authority_checked = 0
    for fact in manifest["authorities"]:
        if fact.get("path_base") == "package_root":
            assert_file_fact(package, fact)
            authority_checked += 1
        elif validate_external_fact(fact, args.repository_root, args.owner_package_root, args.require_authorities):
            authority_checked += 1
    assert_file_fact(package, manifest["scope_declaration"])
    for fact in manifest["sidecars"]:
        assert_file_fact(package, fact)
    assert_file_fact(package, manifest["csv_projection"]["manifest"])
    assert_file_fact(package, manifest["build"]["builder"])
    assert_file_fact(package, manifest["build"]["validator"])

    tables, table_report = validate_tables(package, manifest["dataset_id"])
    require(manifest["csv_projection"]["record_count"] == table_report["records"], "manifest record count mismatch")
    require(manifest["csv_projection"]["table_csv_count"] == len(TABLE_ORDER), "manifest CSV table count mismatch")
    sidecar_report = validate_sidecars(package, manifest, tables)
    seal_report = validate_seal_and_checksums(package, manifest)
    privacy_report = validate_no_leaks(package)

    deterministic_report: dict[str, Any] = {"supplied": False}
    if args.build_a or args.build_b:
        require(args.build_a is not None and args.build_b is not None, "both --build-a and --build-b are required")
        build_a = args.build_a.resolve()
        build_b = args.build_b.resolve()
        identity_a = tree_identity(build_a)
        identity_b = tree_identity(build_b)
        require(identity_a == identity_b, "full A/B package trees are not byte-identical")
        require(identity_a == tree_identity(package), "validated package differs from supplied A/B builds")
        deterministic_report = {"supplied": True, "tree_sha256": identity_a, "byte_identical": True}

    return {
        "schema_id": "program-matematika-indonesia/generic-v2.3.1-adapter-validation/1",
        "status": "PASS",
        "package_id": manifest["package_id"],
        "dataset_id": manifest["dataset_id"],
        "extension_id": manifest["extension_id"],
        "extension_version": manifest["extension_version"],
        "manifest": {"bytes": (package / "manifest.json").stat().st_size, "sha256": sha256_file(package / "manifest.json")},
        "manifest_payload": manifest_payload,
        "authorities": {"declared": len(manifest["authorities"]), "locally_replayed": authority_checked},
        "tables": table_report,
        "sidecars": sidecar_report,
        "seal": seal_report,
        "privacy": privacy_report,
        "deterministic_ab": deterministic_report,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--owner-package-root", type=Path)
    parser.add_argument("--require-authorities", action="store_true")
    parser.add_argument("--build-a", type=Path)
    parser.add_argument("--build-b", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = validate_package(args)
        if args.report:
            write_json(args.report, report)
        print(compact_json(report))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
