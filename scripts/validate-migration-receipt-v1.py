#!/usr/bin/env python3
"""Validate one or more corpus migration receipts against the common envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("receipts", nargs="+", type=Path)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    results = []
    for path in args.receipts:
        value = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
        if errors:
            first = errors[0]
            raise ValueError(f"{path}: {list(first.absolute_path)}: {first.message}")
        results.append(
            {
                "path": path.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "migration_id": value["migration_id"],
                "migration_mode": value["migration_mode"],
                "target_records": value["target"]["record_count"],
                "result": "pass"
            }
        )
    print(json.dumps({"schema": args.schema.as_posix(), "receipts": results, "result": "pass"}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
