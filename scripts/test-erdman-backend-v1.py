#!/usr/bin/env python3
"""Independent executable test for the D20 common-backend v1 adapter."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("erdman_backend_v1_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Erdman adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_failure(action, label: str) -> None:
    try:
        action()
    except (ValueError, RuntimeError):
        return
    raise RuntimeError(f"mutation test did not fail closed: {label}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--hub-root", type=Path, default=repo_root)
    parser.add_argument(
        "--owner-root",
        type=Path,
        default=repo_root.parent / "functional-analysis-erdman-id",
    )
    parser.add_argument(
        "--expected-receipt",
        type=Path,
        default=(
            repo_root
            / "backend"
            / "migrations"
            / "erdman-functional-analysis-id-v1"
            / "MIGRATION_RECEIPT.json"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hub_root = args.hub_root.resolve()
    owner_root = args.owner_root.resolve()
    receipt = args.expected_receipt.resolve()
    adapter_path = hub_root / "scripts" / "migrate-erdman-backend-v1.py"
    adapter = load_adapter(adapter_path)

    command = [
        sys.executable,
        "-B",
        str(adapter_path),
        "--owner-root",
        str(owner_root),
        "--receipt",
        str(receipt),
        "--check-only",
    ]
    completed = subprocess.run(
        command,
        cwd=hub_root,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout.strip())
    if (
        result.get("result") != "pass"
        or result.get("native_records") != adapter.EXPECTED_NATIVE_RECORDS
        or result.get("target_records") != adapter.EXPECTED_TARGET_RECORDS
    ):
        raise RuntimeError(f"adapter check-only summary changed: {result}")

    receipt_value = json.loads(receipt.read_text(encoding="utf-8"))
    if (
        receipt_value.get("validation", {}).get("result") != "pass"
        or receipt_value.get("target", {}).get("record_count")
        != adapter.EXPECTED_TARGET_RECORDS
        or receipt_value.get("transformation", {}).get("exact_reverse_extraction")
        != adapter.EXPECTED_NATIVE_RECORDS
    ):
        raise RuntimeError("written D20 migration receipt is stale")

    expect_failure(lambda: adapter.safe_relative("../escape"), "parent path")
    expect_failure(lambda: adapter.safe_relative("C:/escape"), "drive path")
    expect_failure(
        lambda: adapter.privacy_scan({"access_token": "hidden"}),
        "credential marker",
    )

    first_segment = json.loads(
        (owner_root / "backend" / "segments.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    source_path = owner_root / first_segment["source_path"]
    with tempfile.TemporaryDirectory(prefix="erdman-v1-mutation-") as directory:
        mutated = Path(directory) / "mutated.tex"
        payload = bytearray(source_path.read_bytes())
        payload[0] ^= 1
        mutated.write_bytes(payload)
        expect_failure(
            lambda: adapter.Builder.payload_from_locator(
                mutated,
                int(first_segment["source_line_start"]),
                int(first_segment["source_bytes"]),
                first_segment["source_sha256"],
            ),
            "segment payload mutation",
        )

    print(
        json.dumps(
            {
                "adapter_check_only": "pass",
                "mutation_tests": 4,
                "native_records": adapter.EXPECTED_NATIVE_RECORDS,
                "receipt_sha256": adapter.sha256_file(receipt),
                "result": "pass",
                "target_records": adapter.EXPECTED_TARGET_RECORDS,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
