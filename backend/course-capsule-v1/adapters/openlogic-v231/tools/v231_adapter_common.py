#!/usr/bin/env python3
"""Corpus-neutral deterministic helpers for backend-v2.3.1 lane adapters.

This module contains serialization and package-envelope mechanics only.  It
does not know any textbook title, course ID, owner path, translated prose, or
publication credential.  Corpus-specific builders must supply exact authority
facts and mapping policy.
"""

from __future__ import annotations

import csv
import hashlib
import json
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


TABLE_ORDER = [
    "owner_authorities",
    "datasets",
    "editions",
    "units",
    "course_unit_memberships",
    "native_bindings",
    "content_bindings",
    "relations",
    "rights",
    "rights_assignments",
    "artifacts",
    "build_recipes",
    "reader_surfaces",
    "routes",
    "search_documents",
    "adapter_profiles",
    "adapter_runs",
    "qa_events",
    "identity_crosswalks",
]

RECORD_TYPE_BY_TABLE = {
    "owner_authorities": "owner_authority",
    "datasets": "dataset",
    "editions": "edition",
    "units": "unit",
    "course_unit_memberships": "course_unit_membership",
    "native_bindings": "native_binding",
    "content_bindings": "content_binding",
    "relations": "relation",
    "rights": "rights",
    "rights_assignments": "rights_assignment",
    "artifacts": "artifact",
    "build_recipes": "build_recipe",
    "reader_surfaces": "reader_surface",
    "routes": "route",
    "search_documents": "search_document",
    "adapter_profiles": "adapter_profile",
    "adapter_runs": "adapter_run",
    "qa_events": "qa_event",
    "identity_crosswalks": "identity_crosswalk",
}

CAPABILITY_NAMES = [
    "structure_localization",
    "terminology",
    "mathematical_preservation",
    "assessment_support",
    "assets",
    "accessibility",
    "corrections",
    "computational_interactives",
    "publication",
    "research_support",
]

ROW_ENVELOPE_KEYS = {
    "dataset_id",
    "id",
    "normalized_state",
    "owner_authority_id",
    "owner_native_state",
    "payload",
    "record_type",
    "recorded_at",
    "semantic_key",
}


class AdapterError(RuntimeError):
    """A deterministic adapter invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdapterError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def canonical_row_bytes(row: Mapping[str, Any]) -> bytes:
    return (compact_json(row) + "\n").encode("utf-8")


def canonical_row_sha256(row: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_row_bytes(row))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pretty_json_bytes(value))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_jsonl(path: Path, *, require_canonical: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        for ordinal, line in enumerate(stream, 1):
            require(bool(line.strip()), f"blank JSONL row: {path}:{ordinal}")
            row = json.loads(line)
            require(isinstance(row, dict), f"non-object JSONL row: {path}:{ordinal}")
            if require_canonical:
                require(compact_json(row) == line.rstrip("\r\n"), f"non-canonical JSONL row: {path}:{ordinal}")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical_row_bytes(row) for row in rows))


def safe_relative_path(value: str) -> str:
    pure = PurePosixPath(value)
    require(bool(value), "empty relative path")
    require(not pure.is_absolute(), f"absolute path is forbidden: {value}")
    require(".." not in pure.parts, f"parent traversal is forbidden: {value}")
    require("\\" not in value, f"non-POSIX separator in package path: {value}")
    return pure.as_posix()


def file_fact(
    path: Path,
    relative: str,
    role: str,
    *,
    path_base: str = "package_root",
    records: int | None = None,
    record_id_set_sha256: str | None = None,
) -> dict[str, Any]:
    require(path.is_file(), f"missing file for fact: {path}")
    result: dict[str, Any] = {
        "path": safe_relative_path(relative),
        "path_base": path_base,
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if records is not None:
        result["records"] = records
    if record_id_set_sha256 is not None:
        result["record_id_set_sha256"] = record_id_set_sha256
    return result


def external_file_fact(
    path: Path,
    relative: str,
    role: str,
    path_base: str,
    *,
    expected_bytes: int,
    expected_sha256: str,
    records: int | None = None,
    record_id_set_sha256: str | None = None,
) -> dict[str, Any]:
    fact = file_fact(
        path,
        relative,
        role,
        path_base=path_base,
        records=records,
        record_id_set_sha256=record_id_set_sha256,
    )
    require(fact["bytes"] == expected_bytes, f"authority byte drift: {role}")
    require(fact["sha256"] == expected_sha256, f"authority hash drift: {role}")
    return fact


def projection_id(namespace: uuid.UUID, record_type: str, semantic_key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(namespace, f"{record_type}:{semantic_key}"))


def identity_set_sha256(values: Iterable[str]) -> str:
    return sha256_bytes("".join(value + "\n" for value in sorted(set(values))).encode("utf-8"))


def mapping_set_sha256(pairs: Iterable[tuple[str, str]]) -> str:
    return sha256_bytes("".join(f"{left}\0{right}\n" for left, right in sorted(set(pairs))).encode("utf-8"))


def inventory_sha256(facts: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(
        f"{item['path']}\0{item['bytes']}\0{item['sha256']}\n"
        for item in sorted(facts, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    return sha256_bytes(payload)


def combined_shard_identity(shards: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(
        f"{item['path']}\0{item.get('records', 0)}\0{item.get('record_id_set_sha256', '')}\n"
        for item in sorted(shards, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    return sha256_bytes(payload)


def make_row(
    namespace: uuid.UUID,
    record_type: str,
    semantic_key: str,
    payload: Mapping[str, Any],
    *,
    dataset_id: str,
    owner_authority_id: str,
    recorded_at: str,
    normalized_state: str = "validated",
    owner_native_state: str | None = None,
) -> dict[str, Any]:
    row = {
        "dataset_id": dataset_id,
        "id": projection_id(namespace, record_type, semantic_key),
        "normalized_state": normalized_state,
        "owner_authority_id": owner_authority_id,
        "owner_native_state": owner_native_state,
        "payload": dict(payload),
        "record_type": record_type,
        "recorded_at": recorded_at,
        "semantic_key": semantic_key,
    }
    require(set(row) == ROW_ENVELOPE_KEYS, "internal row envelope drift")
    return row


def empty_tables() -> dict[str, list[dict[str, Any]]]:
    return {name: [] for name in TABLE_ORDER}


def sort_table_rows(tables: Mapping[str, list[dict[str, Any]]]) -> None:
    for table_name in TABLE_ORDER:
        tables[table_name].sort(key=lambda row: (str(row["semantic_key"]), str(row["id"])))


def write_tables(output: Path, tables: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, dict[str, Any]]:
    facts: dict[str, dict[str, Any]] = {}
    for table_name in TABLE_ORDER:
        rows = list(tables[table_name])
        expected_type = RECORD_TYPE_BY_TABLE[table_name]
        for row in rows:
            require(set(row) == ROW_ENVELOPE_KEYS, f"bad row envelope in {table_name}")
            require(row["record_type"] == expected_type, f"record type/table mismatch in {table_name}")
        path = output / "tables" / f"{table_name}.jsonl"
        write_jsonl(path, rows)
        facts[table_name] = file_fact(
            path,
            f"tables/{table_name}.jsonl",
            "canonical_jsonl",
            records=len(rows),
            record_id_set_sha256=identity_set_sha256(str(row["id"]) for row in rows),
        )
    return facts


def write_csv_surfaces(
    output: Path,
    tables: Mapping[str, Sequence[Mapping[str, Any]]],
    package_id: str,
    recorded_at: str,
) -> dict[str, Any]:
    csv_root = output / "csv"
    csv_root.mkdir(parents=True, exist_ok=True)
    table_entries: list[dict[str, Any]] = []
    global_rows: list[list[str]] = []
    for table_name in TABLE_ORDER:
        rows = list(tables[table_name])
        jsonl_path = output / "tables" / f"{table_name}.jsonl"
        csv_path = csv_root / f"{table_name}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["stable_id", "record_type", "canonical_record_json"])
            for ordinal, row in enumerate(rows, 1):
                canonical = compact_json(row)
                writer.writerow([row["id"], row["record_type"], canonical])
                global_rows.append(
                    [f"tables/{table_name}.jsonl", str(ordinal), str(row["id"]), str(row["record_type"]), canonical]
                )
        reconstructed = "".join(
            row[4] + "\n" for row in global_rows if row[0] == f"tables/{table_name}.jsonl"
        ).encode("utf-8")
        require(reconstructed == jsonl_path.read_bytes(), f"CSV/JSONL round-trip failed: {table_name}")
        table_entries.append(
            {
                "table": table_name,
                "records": len(rows),
                "source_jsonl": file_fact(jsonl_path, f"tables/{table_name}.jsonl", "canonical_jsonl"),
                "csv": file_fact(csv_path, f"csv/{table_name}.csv", "deterministic_csv"),
                "roundtrip_sha256": sha256_bytes(reconstructed),
                "roundtrip_state": "pass",
            }
        )
    global_rows.sort(key=lambda row: (row[3], row[2], row[0], int(row[1])))
    records_path = output / "records.csv"
    with records_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["source_jsonl_path", "source_row_ordinal", "stable_id", "record_type", "canonical_record_json"])
        writer.writerows(global_rows)
    records_fact = file_fact(records_path, "records.csv", "deterministic_global_csv")
    csv_facts = [entry["csv"] for entry in table_entries] + [records_fact]
    return {
        "$schema": "schema/csv-projection-manifest-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-csv-projection-manifest/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "source_tables": "tables/*.jsonl",
        "header": ["stable_id", "record_type", "canonical_record_json"],
        "table_order": TABLE_ORDER,
        "tables": table_entries,
        "records_csv": {
            **records_fact,
            "records": len(global_rows),
            "roundtrip_sha256": sha256_bytes("".join(row[4] + "\n" for row in global_rows).encode("utf-8")),
        },
        "aggregate_sha256": inventory_sha256(csv_facts),
        "canonical_serialization": {
            "encoding": "UTF-8",
            "newline": "LF",
            "csv_dialect": "RFC4180-compatible quoting",
            "record_terminator": "LF",
            "table_row_order": "source_jsonl_order",
            "aggregate_table_order": "record_type_then_stable_id_then_source_path_then_ordinal",
            "canonical_record_json": "exact_source_jsonl_record",
            "trailing_newline": True,
            "roundtrip": "csv_to_jsonl_to_csv_byte_identical",
        },
        "recorded_at": recorded_at,
    }


def package_payload_files(output: Path) -> list[dict[str, Any]]:
    excluded = {"manifest.json", "PACKAGE_CHECKSUMS.sha256"}
    facts: list[dict[str, Any]] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        relative = path.relative_to(output).as_posix()
        if relative in excluded:
            continue
        facts.append(file_fact(path, relative, "package_payload"))
    return facts


def write_checksums(output: Path, facts: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(facts, key=lambda item: str(item["path"]))
    text = "".join(f"{item['sha256']}  {item['path']}\n" for item in ordered)
    path = output / "PACKAGE_CHECKSUMS.sha256"
    path.write_text(text, encoding="utf-8", newline="\n")
    return file_fact(path, "PACKAGE_CHECKSUMS.sha256", "package_checksums")


def assert_file_fact(root: Path, fact: Mapping[str, Any]) -> None:
    relative = safe_relative_path(str(fact["path"]))
    path = root.joinpath(*PurePosixPath(relative).parts)
    require(path.is_file(), f"missing fact target: {relative}")
    require(path.stat().st_size == fact["bytes"], f"byte mismatch: {relative}")
    require(sha256_file(path) == fact["sha256"], f"hash mismatch: {relative}")


def parse_checksum_file(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for ordinal, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        require(len(line) >= 67 and line[64:66] == "  ", f"malformed checksum line {ordinal}")
        digest, relative = line[:64], line[66:]
        require(len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest), f"bad digest at line {ordinal}")
        safe_relative_path(relative)
        rows.append((digest, relative))
    require(len(rows) == len({relative for _, relative in rows}), "duplicate checksum paths")
    require(rows == sorted(rows, key=lambda item: item[1]), "checksum paths are not sorted")
    return rows


def tree_identity(root: Path, *, excluded: set[str] | None = None) -> str:
    excluded = excluded or set()
    facts = [
        file_fact(path, path.relative_to(root).as_posix(), "tree_member")
        for path in sorted(item for item in root.rglob("*") if item.is_file())
        if path.relative_to(root).as_posix() not in excluded
    ]
    return inventory_sha256(facts)
