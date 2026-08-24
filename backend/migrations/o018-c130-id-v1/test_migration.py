#!/usr/bin/env python3
"""Independent command-level checks for the frozen O018/C130 v1 adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


EXPECTED_NATIVE_RECORDS = 17_987
EXPECTED_DERIVED_VARIANTS = 7_818
EXPECTED_COMMON_RECORDS = 25_805


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    line = completed.stdout.strip().splitlines()[-1]
    return json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    central_root = here.parents[2]
    receipt = here / "MIGRATION_RECEIPT.json"
    adapter = here / "migrate_o018_c130_v1.py"
    schema = central_root / "schemas" / "backend-v1.schema.json"
    receipt_schema = central_root / "schemas" / "backend-migration-receipt-v1.schema.json"
    validator = central_root / "scripts" / "validate-migration-receipt-v1.py"

    replay = run(
        [
            sys.executable,
            "-B",
            str(adapter),
            "--corpus-root",
            str(args.corpus_root.resolve()),
            "--schema",
            str(schema),
            "--receipt-schema",
            str(receipt_schema),
            "--output-receipt",
            str(receipt),
            "--check",
        ],
        central_root,
    )
    if replay.get("result") != "pass" or replay.get("common_records") != EXPECTED_COMMON_RECORDS:
        raise ValueError(f"adapter replay failed: {replay}")

    envelope = run(
        [
            sys.executable,
            "-B",
            str(validator),
            "--schema",
            str(receipt_schema),
            str(receipt),
        ],
        central_root,
    )
    if envelope.get("result") != "pass":
        raise ValueError(f"receipt envelope validation failed: {envelope}")

    value = json.loads(receipt.read_text(encoding="utf-8"))
    assertions = {
        "native_record_count": value["source"]["native_record_count"] == EXPECTED_NATIVE_RECORDS,
        "direct_reverse_count": value["validation"]["lossless_reverse_records"] == EXPECTED_NATIVE_RECORDS,
        "derived_segment_variants": value["transformation"]["derived_segment_variant_records"] == EXPECTED_DERIVED_VARIANTS,
        "common_record_count": value["target"]["record_count"] == EXPECTED_COMMON_RECORDS,
        "native_schema": value["validation"]["native_schema_validation"] == "pass",
        "native_manifest": value["validation"]["native_manifest_and_sha256sums_closure"] == "pass",
        "native_jsonl_replay": value["validation"]["native_jsonl_exact_table_reconstruction"] == "pass",
        "common_schema": value["validation"]["strict_common_backend_schema"] == "pass",
        "common_foreign_keys": value["validation"]["common_foreign_key_closure"] == "pass",
        "two_assemblies": value["validation"]["two_independent_common_assemblies"] == "byte-identical",
        "owner_lane_unchanged": value["materialization"]["owner_backend_modified"] is False,
        "credentials_absent": value["credentials_recorded"] is False,
    }
    failed = sorted(name for name, passed in assertions.items() if not passed)
    if failed:
        raise ValueError(f"receipt semantic assertions failed: {failed}")
    print(
        json.dumps(
            {
                "assertions": len(assertions),
                "common_records": EXPECTED_COMMON_RECORDS,
                "receipt_bytes": receipt.stat().st_size,
                "receipt_sha256": sha256_file(receipt),
                "result": "pass",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
