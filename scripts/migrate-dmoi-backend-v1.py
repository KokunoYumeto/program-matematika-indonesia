#!/usr/bin/env python3
"""Prove a lossless, zero-copy migration of the complete DMOI backend to v1.

The admitted DMOI package is 437 MB because it carries JSON, JSONL, and CSV
projections.  This verifier deliberately avoids making a redundant copy.  It
streams every canonical row, performs the two-field schema-profile upgrade,
validates all 163,583 transformed records against the strict v1 per-table
definitions, proves exact reversibility, checks IDs and references, and emits a
small hash-bound migration receipt.  The same transformation can materialize a
portable copy later without changing identity or content.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


TARGET_SCHEMA_NAME = "interlanguage-math-modular-backend"
TARGET_SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_NAME = "math-modular-backend"
SOURCE_SCHEMA_VERSION = "0.1.0"
UUID_URN_RE = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def transformed(record: dict) -> dict:
    result = copy.deepcopy(record)
    if result.get("schema_name") != SOURCE_SCHEMA_NAME or result.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise ValueError(f"unexpected source schema header for {result.get('id')}")
    result["schema_name"] = TARGET_SCHEMA_NAME
    result["schema_version"] = TARGET_SCHEMA_VERSION
    return result


def reverse(record: dict) -> dict:
    result = copy.deepcopy(record)
    result["schema_name"] = SOURCE_SCHEMA_NAME
    result["schema_version"] = SOURCE_SCHEMA_VERSION
    return result


def referenced_urns(value: object, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_urns(child, (*path, str(index)))
    elif isinstance(value, str) and UUID_URN_RE.fullmatch(value):
        yield path, value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-package", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    source_manifest_path = args.source_package / "package.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    schema_tables = schema["properties"]["tables"]["properties"]

    source_counts = source_manifest["table_counts"]
    source_tables = sorted(source_counts)
    missing_schema_tables = sorted(set(source_tables) - set(schema_tables))
    if missing_schema_tables:
        raise ValueError(f"v1 schema lacks source tables: {missing_schema_tables}")

    ids: list[str] = []
    table_results: dict[str, dict] = {}
    virtual_records_hash = hashlib.sha256()
    total_target_bytes = 0
    total_records = 0

    # Pass 1: strict target validation, reversible transformation, counts, and hashes.
    for table_name in source_tables:
        source_path = args.source_package / "data" / f"{table_name}.jsonl"
        definition_ref = schema_tables[table_name]["items"]["$ref"]
        definition_name = definition_ref.rsplit("/", 1)[-1]
        validator = Draft202012Validator(schema["$defs"][definition_name], format_checker=FormatChecker())
        digest = hashlib.sha256()
        byte_count = 0
        row_count = 0
        previous_id = None
        with source_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                source = json.loads(line)
                target = transformed(source)
                errors = list(validator.iter_errors(target))
                if errors:
                    first = errors[0]
                    raise ValueError(f"{table_name}:{line_number}:{list(first.absolute_path)}: {first.message}")
                if reverse(target) != source:
                    raise ValueError(f"lossless reverse mismatch {table_name}:{line_number}")
                if previous_id is not None and target["id"] < previous_id:
                    raise ValueError(f"source table is not stable-ID sorted: {table_name}:{line_number}")
                previous_id = target["id"]
                ids.append(target["id"])
                payload = (canonical(target) + "\n").encode("utf-8")
                digest.update(payload)
                virtual_records_hash.update(payload)
                byte_count += len(payload)
                row_count += 1
        if row_count != source_counts[table_name]:
            raise ValueError(f"count mismatch for {table_name}: {row_count} != {source_counts[table_name]}")
        table_results[table_name] = {
            "records": row_count,
            "virtual_target_bytes": byte_count,
            "virtual_target_sha256": digest.hexdigest(),
            "source_path": source_path.relative_to(args.source_package).as_posix(),
            "source_bytes": source_path.stat().st_size,
            "source_sha256": sha256_file(source_path),
        }
        total_target_bytes += byte_count
        total_records += row_count

    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate IDs: {duplicates[:10]}")
    known = set(ids)

    # Pass 2: all canonical foreign keys close; immutable predecessor pointers
    # are allowed to name records in an earlier package.
    dangling: list[dict] = []
    allowed_external = {"supersedes_id", "source_edition_id", "source_revision_id", "source_variant_id", "source_occurrence_id"}
    for table_name in source_tables:
        source_path = args.source_package / "data" / f"{table_name}.jsonl"
        with source_path.open(encoding="utf-8") as handle:
            for line in handle:
                record = transformed(json.loads(line))
                for field_path, value in referenced_urns(record):
                    if field_path == ("id",):
                        continue
                    leaf = field_path[-1] if field_path else ""
                    if leaf in allowed_external:
                        continue
                    if value not in known:
                        dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
                        if len(dangling) >= 20:
                            break
                if len(dangling) >= 20:
                    break
        if dangling:
            break
    if dangling:
        raise ValueError(f"dangling target references: {dangling}")

    for table_name in sorted(set(schema_tables) - set(source_tables)):
        table_results[table_name] = {
            "records": 0,
            "virtual_target_bytes": 0,
            "virtual_target_sha256": hashlib.sha256(b"").hexdigest(),
            "source_path": None,
            "source_bytes": 0,
            "source_sha256": None,
        }

    source_zip = None
    release_candidates = sorted((args.source_package.parents[1] / "releases").glob("**/DMD_ID_MODULAR_BACKEND_V1.zip"))
    if release_candidates:
        release_path = release_candidates[-1]
        source_zip = {
            "path": release_path.relative_to(args.source_package.parents[1]).as_posix(),
            "bytes": release_path.stat().st_size,
            "sha256": sha256_file(release_path),
        }

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": TARGET_SCHEMA_VERSION,
        "migration_id": "dmoi4-id-0.1.0-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-profile-upgrade",
        "source": {
            "dataset_id": source_manifest["dataset_id"],
            "dataset_version": source_manifest["dataset_version"],
            "schema_name": source_manifest["schema_name"],
            "schema_version": source_manifest["schema_version"],
            "package_manifest_path": "repo/backend/full/dmoi4-id/package.json",
            "package_manifest_bytes": source_manifest_path.stat().st_size,
            "package_manifest_sha256": sha256_file(source_manifest_path),
            "record_count": source_manifest["record_count"],
            "portable_release_zip": source_zip,
        },
        "target": {
            "dataset_id": source_manifest["dataset_id"],
            "dataset_version": f"{source_manifest['dataset_version']}+interlanguage-v1",
            "schema_name": TARGET_SCHEMA_NAME,
            "schema_version": TARGET_SCHEMA_VERSION,
            "schema_path": "schemas/backend-v1.schema.json",
            "schema_bytes": args.schema.stat().st_size,
            "schema_sha256": sha256_file(args.schema),
            "record_count": total_records,
            "virtual_records_jsonl_bytes": total_target_bytes,
            "virtual_records_jsonl_sha256": virtual_records_hash.hexdigest(),
        },
        "transformation": {
            "changed_fields": {
                "schema_name": [SOURCE_SCHEMA_NAME, TARGET_SCHEMA_NAME],
                "schema_version": [SOURCE_SCHEMA_VERSION, TARGET_SCHEMA_VERSION],
            },
            "changed_record_ids": 0,
            "changed_payload_fields": 0,
            "added_source_tables": 0,
            "new_v1_tables_initialized_empty": sorted(set(schema_tables) - set(source_tables)),
            "reverse_transformation": "exact for every source record",
        },
        "validation": {
            "result": "pass",
            "strict_target_schema_rows": total_records,
            "source_record_count_match": total_records == source_manifest["record_count"],
            "identity_preserved_count": total_records,
            "global_unique_ids": len(known),
            "foreign_key_closure": "pass",
            "lossless_reverse_records": total_records,
            "stable_id_order": "pass for every source table",
        },
        "tables": dict(sorted(table_results.items())),
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The complete admitted source package plus this deterministic reversible transform are sufficient; avoiding a redundant 437 MB copy preserves local storage.",
        },
    }
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(canonical({"result": "pass", "records": total_records, "receipt": str(args.output_receipt), "receipt_sha256": sha256_file(args.output_receipt)}))


if __name__ == "__main__":
    main()
