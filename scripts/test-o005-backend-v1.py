#!/usr/bin/env python3
"""Independent deterministic-replay test for the O005/C120 v1 adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-root", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--expected-receipt", required=True, type=Path)
    args = parser.parse_args()

    hub = args.hub_root.resolve()
    corpus = args.corpus_root.resolve()
    script = hub / "scripts/migrate-o005-backend-v1.py"
    validator = hub / "scripts/validate-migration-receipt-v1.py"
    schema = hub / "schemas/backend-v1.schema.json"
    receipt_schema = hub / "schemas/backend-migration-receipt-v1.schema.json"
    expected = args.expected_receipt.resolve()

    with tempfile.TemporaryDirectory(prefix="o005-v1-replay-") as temporary:
        root = Path(temporary)
        outputs = [root / "first.json", root / "second.json"]
        summaries = []
        for output in outputs:
            completed = run(
                [
                    sys.executable,
                    "-B",
                    str(script),
                    "--corpus-root",
                    str(corpus),
                    "--schema",
                    str(schema),
                    "--receipt-schema",
                    str(receipt_schema),
                    "--output-receipt",
                    str(output),
                ],
                hub,
            )
            summaries.append(json.loads(completed.stdout))
            run(
                [
                    sys.executable,
                    "-B",
                    str(validator),
                    "--schema",
                    str(receipt_schema),
                    str(output),
                ],
                hub,
            )
        first = outputs[0].read_bytes()
        second = outputs[1].read_bytes()
        checked_in = expected.read_bytes()
        if first != second:
            raise ValueError("independent receipt replays are not byte-identical")
        if first != checked_in:
            raise ValueError("checked-in receipt differs from independent deterministic replay")
        if summaries[0] != summaries[1]:
            raise ValueError("independent migration summaries differ")
        receipt = json.loads(first)
        print(
            json.dumps(
                {
                    "result": "pass",
                    "independent_replays": 2,
                    "receipt_bytes": len(first),
                    "receipt_sha256": sha256(first),
                    "migration_script_sha256": sha256(script.read_bytes()),
                    "target_records": receipt["target"]["record_count"],
                    "native_records": receipt["source"]["native_record_count"],
                    "native_backend_files": receipt["source"]["backend_file_count"],
                    "native_backend_bytes": receipt["source"]["backend_bytes"],
                    "canonical_backend_sha256": receipt["target"]["canonical_backend_sha256"],
                    "virtual_records_jsonl_sha256": receipt["target"]["virtual_records_jsonl_sha256"],
                    "receipt_schema": "pass twice",
                    "checked_in_receipt_identity": "pass",
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )


if __name__ == "__main__":
    main()
