#!/usr/bin/env python3
"""Build a deterministic version-bound global backend-v2.2 validation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


A00_RELATIVE = Path("backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0")
ASSESSMENT_RELATIVE = Path(
    "backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0"
)
GLOBAL_CONTRACT_RELATIVE = Path("backend/v2.2/global-capability-contract-v0.1.0.json")
GLOBAL_CONTRACT_SCHEMA_RELATIVE = Path(
    "backend/v2.2/schema/global-capability-contract-v0.1.schema.json"
)
ASSESSMENT_EXPECTED = {
    "file_count": 12,
    "total_bytes": 19057785,
    "aggregate_sha256": "5d7c3da1a1b3c33b4f79306fec08a31ebc8f557188f1ec0c088e267e0d9ce222",
}
UUID5_URN_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def tree_identity(root: Path) -> dict:
    facts = []
    for path in (candidate for candidate in root.rglob("*") if candidate.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        data = path.read_bytes()
        facts.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": sha256(data),
            }
        )
    facts.sort(key=lambda row: (row["path"].casefold(), row["path"]))
    digest = sha256(
        "".join(
            f"{row['sha256']}  {row['bytes']}  {row['path']}\n" for row in facts
        ).encode("utf-8")
    )
    return {
        "file_count": len(facts),
        "total_bytes": sum(row["bytes"] for row in facts),
        "aggregate_sha256": digest,
        "files": facts,
    }


def run_json(command: list[str], cwd: Path) -> tuple[bytes, object]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
    )
    output = result.stdout.strip()
    if not output:
        raise ValueError(f"validator emitted no JSON: {command}")
    return output, json.loads(output.decode("utf-8"))


def replay(command: list[str], cwd: Path) -> dict:
    first_bytes, first = run_json(command, cwd)
    second_bytes, second = run_json(command, cwd)
    if first_bytes != second_bytes or first != second:
        raise ValueError(f"validator output is not deterministic: {command}")
    return {
        "runs": 2,
        "stdout_sha256": sha256(first_bytes),
        "result": first,
    }


def validate_assessment_uuid5(package: Path) -> int:
    checked = 0
    for relative in (
        "data/assessments.jsonl",
        "data/assessment-components.jsonl",
        "data/solution-gaps.jsonl",
    ):
        for line_number, line in enumerate(
            (package / relative).read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            row = json.loads(line)
            for field in ("id", "assessment_id"):
                if field not in row:
                    continue
                if not UUID5_URN_RE.fullmatch(row[field]):
                    raise ValueError(
                        f"assessment inventory {relative}:{line_number} has non-UUIDv5 {field}"
                    )
                checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--owner-root", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    owner_root = args.owner_root.resolve()
    output = args.output.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ValueError("--source-commit must be a lowercase 40-hex Git object ID")
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        raise ValueError("--version must be a semantic version")
    if not args.recorded_at.endswith("Z") or "T" not in args.recorded_at:
        raise ValueError("--recorded-at must be an explicit UTC timestamp")

    a00 = (root / A00_RELATIVE).resolve()
    assessment = (root / ASSESSMENT_RELATIVE).resolve()
    global_contract_path = (root / GLOBAL_CONTRACT_RELATIVE).resolve()
    global_contract_schema_path = (root / GLOBAL_CONTRACT_SCHEMA_RELATIVE).resolve()
    a00_identity = tree_identity(a00)
    assessment_identity = tree_identity(assessment)
    for key, expected in ASSESSMENT_EXPECTED.items():
        if assessment_identity[key] != expected:
            raise ValueError(f"assessment shard {key} mismatch")
    global_contract = json.loads(global_contract_path.read_text(encoding="utf-8"))
    global_contract_schema = json.loads(
        global_contract_schema_path.read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(global_contract_schema)
    errors = sorted(
        Draft202012Validator(global_contract_schema).iter_errors(global_contract),
        key=lambda error: list(error.path),
    )
    if errors:
        raise ValueError(f"global capability contract schema failure: {errors[0].message}")

    a00_replay = replay(
        [
            sys.executable,
            "-B",
            str(root / "backend/v2.2/scripts/validate_v22_package.py"),
            str(a00),
        ],
        root,
    )
    if a00_replay["result"].get("result") != "pass":
        raise ValueError("sealed A00 v2.2 package validation failed")

    assessment_replay = replay(
        [
            sys.executable,
            "-B",
            str(assessment / "tools/validate_o001_a00_assessments.py"),
            "--owner-root",
            str(owner_root),
            "--package-root",
            str(assessment),
        ],
        root,
    )
    if assessment_replay["result"].get("validation_state") != "pass":
        raise ValueError("O001/A00 assessment inventory validation failed")
    assessment_uuid5_ids = validate_assessment_uuid5(assessment)

    receipt = {
        "schema_id": "program-matematika-indonesia/backend-v2.2-global-validation-receipt/v1",
        "version": args.version,
        "source_commit": args.source_commit,
        "recorded_at": args.recorded_at,
        "result": "pass",
        "credentials_recorded": False,
        "canonical_package": {
            "path": A00_RELATIVE.as_posix(),
            "file_count": a00_identity["file_count"],
            "total_bytes": a00_identity["total_bytes"],
            "aggregate_sha256": a00_identity["aggregate_sha256"],
            "package_id": a00_replay["result"]["package_id"],
        },
        "owner_native_assessment_inventory": {
            "path": ASSESSMENT_RELATIVE.as_posix(),
            "file_count": assessment_identity["file_count"],
            "total_bytes": assessment_identity["total_bytes"],
            "aggregate_sha256": assessment_identity["aggregate_sha256"],
            "package_id": "urn:uuid:0b253fa5-067e-55b5-8248-cc528b0b4bd1",
            "counts": assessment_replay["result"]["counts"],
            "zero_prose": assessment_replay["result"]["zero_prose"],
            "uuid5_ids_checked": assessment_uuid5_ids,
        },
        "global_capability_contract": {
            "contract": {
                "path": GLOBAL_CONTRACT_RELATIVE.as_posix(),
                "bytes": global_contract_path.stat().st_size,
                "sha256": sha256(global_contract_path.read_bytes()),
            },
            "schema": {
                "path": GLOBAL_CONTRACT_SCHEMA_RELATIVE.as_posix(),
                "bytes": global_contract_schema_path.stat().st_size,
                "sha256": sha256(global_contract_schema_path.read_bytes()),
            },
            "schema_validation": "pass",
            "layers": len(global_contract["layers"]),
            "capability_profiles": len(global_contract["capability_profiles"]),
            "validation_gates": len(global_contract["validation_gates"]),
        },
        "deterministic_replay": {
            "a00_package": {
                "runs": a00_replay["runs"],
                "stdout_sha256": a00_replay["stdout_sha256"],
            },
            "assessment_inventory": {
                "runs": assessment_replay["runs"],
                "stdout_sha256": assessment_replay["stdout_sha256"],
            },
        },
        "checks": [
            {"gate": "sealed_a00_package", "result": "pass"},
            {"gate": "owner_native_assessment_authority_replay", "result": "pass"},
            {"gate": "assessment_json_schema", "result": "pass"},
            {"gate": "assessment_solution_gap_exact_set", "result": "pass"},
            {"gate": "assessment_stable_id_uniqueness", "result": "pass"},
            {"gate": "assessment_uuid5_identity", "result": "pass"},
            {"gate": "assessment_zero_prose", "result": "pass"},
            {"gate": "global_capability_contract_schema", "result": "pass"},
            {"gate": "two_run_validator_replay", "result": "pass"},
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_json(receipt))
    print(
        json.dumps(
            {
                "path": str(output),
                "bytes": output.stat().st_size,
                "sha256": sha256(output.read_bytes()),
                "result": "pass",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
