#!/usr/bin/env python3
"""Validate a central release bundle from its live authority and sealed inputs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


EXPECTED_MIGRATIONS = {
    "dmoi4-id-0.1.0-to-interlanguage-v1.0.0": "lossless-zero-copy-pass",
    "erdman-functional-analysis-id-2026.08.25-to-interlanguage-v1.0.0": "lossless-zero-copy-virtual-adapter-pass",
    "hefferon-linear-algebra-id-v2026.08.22-to-interlanguage-v1.0.0": "lossless-zero-copy-one-to-one-native-backend-adapter-pass",
    "o002-b80-id-2026.08.22.1-to-interlanguage-v1.0.0": "lossless-zero-copy-one-to-one-native-catalog-adapter-pass",
    "openlogic-id-olp-0722-to-interlanguage-v1.0.0": "deterministic-zero-copy-pass",
    "judson-id-v1-2026.08.21.1": "additive-zero-copy-pass",
    "yaintt-r014-id-to-interlanguage-v1.0.0": "lossless-additive-adapter-pass",
    "r012-applied-combinatorics-id-to-v1": "lossless-additive-one-common-record-per-native-record-pass",
    "mathematics-in-lean-id-v4.30.0-id.3-to-interlanguage-v1.0.0": "lossless-zero-copy-one-to-one-pass",
    "prealgebra2e-r001-id-v0.2.7-to-interlanguage-v1.0.0": "lossless-streaming-zero-copy-adapter-pass",
    "o005-c120-id-v1.01-complete-r5-to-interlanguage-v1.0.0": "lossless-replayable-zero-copy-adapter-pass",
    "o018-c130-r017-book1-id5-to-interlanguage-v1": "lossless-zero-copy-one-to-one-plus-segment-variant-projection-pass",
    "tea-time-numerical-analysis-id-v1": "additive-zero-copy-virtual-adapter-pass",
}

MIGRATION_RECEIPT_FILENAMES = {
    "applied-combinatorics-id-v1": "applied-combinatorics-id-backend-v1-migration-receipt.json",
    "dmoi4-id-v1": "dmoi4-id-backend-v1-migration-receipt.json",
    "erdman-functional-analysis-id-v1": "erdman-functional-analysis-id-backend-v1-migration-receipt.json",
    "hefferon-linear-algebra-id-v1": "hefferon-linear-algebra-id-backend-v1-migration-receipt.json",
    "judson-id-v1": "judson-id-backend-v1-migration-receipt.json",
    "mathematics-in-lean-id-v1": "mathematics-in-lean-id-backend-v1-migration-receipt.json",
    "o002-b80-id-v1": "o002-b80-id-backend-v1-migration-receipt.json",
    "o005-c120-id-v1": "o005-c120-id-backend-v1-migration-receipt.json",
    "o018-c130-id-v1": "o018-c130-id-backend-v1-migration-receipt.json",
    "openlogic-id-v1": "openlogic-id-backend-v1-migration-receipt.json",
    "prealgebra2e-id-v1": "prealgebra2e-id-backend-v1-migration-receipt.json",
    "tea-time-id-v1": "tea-time-id-backend-v1-migration-receipt.json",
    "yaintt-id-v1": "yaintt-id-backend-v1-migration-receipt.json",
}

V2_RELEASE_FILES = {
    "schemas/v2/backend-migration-receipt-v2.schema.json": "backend-migration-receipt-v2.schema.json",
    "schemas/v2/federation-package-v2.schema.json": "federation-package-v2.schema.json",
    "schemas/v2/federation-record-v2.schema.json": "federation-record-v2.schema.json",
    "schemas/v2/namespace-v2.json": "namespace-v2.json",
    "schemas/v2/pmi-release-policy-v2.json": "pmi-release-policy-v2.json",
    "scripts/build-backend-v2-federation.py": "build-backend-v2-federation.py",
    "scripts/build-backend-v2-validation-receipt.py": "build-backend-v2-validation-receipt.py",
    "scripts/validate-backend-v2-federation.py": "validate-backend-v2-federation.py",
}

EXPECTED_V1_PACKAGE_PINS = {
    "manifest.json": "8fe45cfb07e47e9596a4d3088beadcd8287ec2f089a62db990bd4fd70f079997",
    "records.jsonl": "e563e13336701e2d3b2110debe4074b168f53f8fd3757e36fe25d36043db7783",
    "validation_report.json": "b742dbcc65c9511fa3d208a001d1f4a33ca38d04d0178f3e964d043c09534b42",
}
EXPECTED_V1_ARCHIVE_SHA256 = "a6451613d0e1960f614314da2c5361ddfb749cd09bf147539ccc5d172abd6866"
EXPECTED_V1_ARCHIVE_PREFIX = "program-matematika-indonesia-backend-v1/"
FIXED_ZIP_TIME = (2026, 8, 22, 0, 0, 0)

PRIVATE_BYTE_MARKERS = (
    bytes([70, 108, 111, 114, 105, 115]).lower(),
    b"c:" + b"\\users\\",
    b"c:" + b"/us" + b"ers/",
    b"/us" + b"ers/",
    b".codex" + b"/attachments",
    b"file:" + b"//",
    b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md",
    b"zenodo " + b"token.md",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def v22_archive_filename(version: str) -> str:
    return (
        f"program-matematika-indonesia-backend-v2.2-pilot-v{version}.zip"
        if version == "0.59.0"
        else f"program-matematika-indonesia-backend-v2.2-v{version}.zip"
    )


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document is not an object: {path}")
    return value


def assert_public_bytes(label: str, data: bytes) -> None:
    lowered = data.lower()
    if any(marker in lowered for marker in PRIVATE_BYTE_MARKERS):
        raise ValueError(f"private or credential-bearing marker in public artifact: {label}")


def file_fact(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def package_files(package: Path) -> list[Path]:
    if not package.is_dir():
        raise ValueError(f"package directory does not exist: {package}")
    return sorted(
        path
        for path in package.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def verify_source_zip(
    path: Path,
    root: Path,
    source_commit: str,
    allowed_generated_source_paths: set[str],
) -> dict[str, Any]:
    tracked_paths = set(
        subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", source_commit],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    commit_bound_entries = 0
    generated_entries = 0
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"source ZIP CRC failure: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)) or names != sorted(names):
            raise ValueError("source ZIP inventory is duplicated or nondeterministically ordered")
        manifest_bytes = archive.read("SOURCE_MANIFEST.json")
        assert_public_bytes("source ZIP:SOURCE_MANIFEST.json", manifest_bytes)
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema_id") != "program-matematika-indonesia/source-manifest/v2":
            raise ValueError("source ZIP manifest schema is not v2")
        declared = {entry["path"]: entry for entry in manifest["files"]}
        if set(declared) != set(names) - {"SOURCE_MANIFEST.json"}:
            raise ValueError("source ZIP manifest inventory mismatch")
        for name, entry in declared.items():
            data = archive.read(name)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError(f"source ZIP entry mismatch: {name}")
            assert_public_bytes(f"source ZIP:{name}", data)
            source_path = entry.get("source_path")
            if not isinstance(source_path, str) or not source_path or source_path.startswith("/") or ".." in Path(source_path).parts:
                raise ValueError(f"source ZIP entry has no portable source_path: {name}")
            if source_path in tracked_paths:
                committed = subprocess.run(
                    ["git", "show", f"{source_commit}:{source_path}"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                ).stdout
                if committed != data:
                    raise ValueError(f"source ZIP entry differs from source commit: {source_path}")
                commit_bound_entries += 1
            elif source_path in allowed_generated_source_paths:
                generated_entries += 1
            else:
                raise ValueError(f"source ZIP entry is neither commit-bound nor admitted generated output: {source_path}")
    return {
        "entries": len(names),
        "manifest_entries": len(declared),
        "source_commit": manifest.get("source_commit"),
        "commit_bound_entries": commit_bound_entries,
        "admitted_generated_entries": generated_entries,
        "privacy_scan": "pass",
        "result": "pass",
    }


def verify_backend_zip(path: Path, package: Path, prefix: str) -> dict[str, Any]:
    expected = {prefix + source.relative_to(package).as_posix(): source for source in package_files(package)}
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"backend ZIP CRC failure: {bad}")
        names = archive.namelist()
        if names != sorted(names) or set(names) != set(expected):
            raise ValueError(f"backend ZIP inventory/order mismatch: {path.name}")
        for name, source in expected.items():
            data = archive.read(name)
            if data != source.read_bytes():
                raise ValueError(f"backend ZIP entry mismatch: {name}")
            assert_public_bytes(f"backend ZIP:{name}", data)
    return {"entries": len(expected), "privacy_scan": "pass", "result": "pass"}


def verify_v1_immutable_archive(path: Path, copied_validation_report: Path) -> dict[str, Any]:
    if not path.is_file() or sha256_file(path) != EXPECTED_V1_ARCHIVE_SHA256:
        raise ValueError("immutable backend-v1 archive identity mismatch")
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"immutable backend-v1 archive CRC failure: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(not name.startswith(EXPECTED_V1_ARCHIVE_PREFIX) or name.endswith("/") for name in names):
            raise ValueError("immutable backend-v1 archive inventory is unsafe")
        members = {name.removeprefix(EXPECTED_V1_ARCHIVE_PREFIX): archive.read(name) for name in names}
    for relative, expected_sha256 in EXPECTED_V1_PACKAGE_PINS.items():
        data = members.get(relative)
        if data is None or hashlib.sha256(data).hexdigest() != expected_sha256:
            raise ValueError(f"immutable backend-v1 identity mismatch: {relative}")
    manifest = json.loads(members["manifest.json"].decode("utf-8"))
    declared = {entry["path"]: entry for entry in manifest.get("files", [])}
    if set(members) != set(declared) | {"manifest.json", "validation_report.json"}:
        raise ValueError("immutable backend-v1 package inventory mismatch")
    for relative, entry in declared.items():
        data = members[relative]
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"immutable backend-v1 manifest member mismatch: {relative}")
        assert_public_bytes(f"immutable backend-v1:{relative}", data)
    report_bytes = members["validation_report.json"]
    if copied_validation_report.read_bytes() != report_bytes:
        raise ValueError("release backend-v1 validation report differs from immutable archive")
    report = json.loads(report_bytes)
    if report.get("result") != "pass" or report.get("checks", {}).get("deterministic_replay", {}).get("result") != "byte-identical":
        raise ValueError("immutable backend-v1 validation report is not admitted")
    if manifest.get("record_count") != report.get("checks", {}).get("record_count"):
        raise ValueError("immutable backend-v1 record counts disagree")
    return {
        "record_count": manifest["record_count"],
        "manifest_members": len(declared),
        "archive_bytes": path.stat().st_size,
        "archive_sha256": sha256_file(path),
        "entries": len(members),
        "result": "pass",
    }


def verify_manifest_inventory(package: Path) -> dict[str, Any]:
    manifest_path = package / "manifest.json"
    manifest = load_json(manifest_path)
    declared = {row["path"]: row for row in manifest.get("files", [])}
    actual = {
        path.relative_to(package).as_posix(): path
        for path in package_files(package)
        if path.name not in {"manifest.json", "validation_report.json"}
    }
    if set(declared) != set(actual):
        raise ValueError("backend-v2 manifest inventory differs from package")
    for relative, path in actual.items():
        row = declared[relative]
        if row.get("bytes") != path.stat().st_size or row.get("sha256") != sha256_file(path):
            raise ValueError(f"backend-v2 manifest fact mismatch: {relative}")
    record_counts = manifest.get("record_counts")
    if not isinstance(record_counts, dict) or not record_counts:
        raise ValueError("backend-v2 manifest has no table counts")
    if manifest.get("record_count") != sum(record_counts.values()):
        raise ValueError("backend-v2 manifest record count is not the sum of tables")
    return manifest


def run_backend_v2_tests(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests/backend-v2", "-p", "test_*.py", "-v"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    match = re.search(r"Ran (\d+) tests? in ", output)
    if match is None or not re.search(r"\nOK\s*$", output):
        raise ValueError("backend-v2 executable test suite did not finish cleanly")
    count = int(match.group(1))
    return {"tests_run": count, "tests_passed": count, "tests_failed": 0, "result": "pass"}


def verify_v2_receipt(receipt_path: Path, package: Path, root: Path, tests: dict[str, Any]) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    if receipt.get("result") != "pass" or receipt.get("credentials_recorded") is not False:
        raise ValueError("backend-v2 validation receipt is not a credential-free pass")
    manifest = verify_manifest_inventory(package)
    files = package_files(package)
    canonical_files = [path for path in files if path.name != "validation_report.json"]
    canonical = receipt.get("canonical_package", {})
    expected_path = package.relative_to(root).as_posix()
    if canonical.get("path") != expected_path:
        raise ValueError("backend-v2 validation receipt package path mismatch")
    if canonical.get("file_count") != len(canonical_files):
        raise ValueError("backend-v2 validation receipt package file_count mismatch")
    content_bytes = sum(path.stat().st_size for path in canonical_files)
    if canonical.get("total_bytes") != content_bytes:
        raise ValueError("backend-v2 validation receipt package total_bytes mismatch")
    if canonical.get("record_count") != manifest["record_count"] or canonical.get("table_counts") != manifest["record_counts"]:
        raise ValueError("backend-v2 validation receipt record counts mismatch")
    named_facts = {
        "records_jsonl": package / "records.jsonl",
        "records_csv": package / "records.csv",
        "federation_json": package / "federation.json",
        "manifest_json": package / "manifest.json",
    }
    for key, path in named_facts.items():
        if canonical.get(key) != file_fact(path):
            raise ValueError(f"backend-v2 validation receipt fact mismatch: {key}")
    for role, fact in receipt.get("implementation", {}).items():
        source = root / fact.get("path", "")
        if not source.is_file() or fact.get("bytes") != source.stat().st_size or fact.get("sha256") != sha256_file(source):
            raise ValueError(f"backend-v2 implementation binding mismatch: {role}")
    for fact in receipt.get("schemas", []):
        source = root / fact.get("path", "")
        if not source.is_file() or fact.get("bytes") != source.stat().st_size or fact.get("sha256") != sha256_file(source):
            raise ValueError(f"backend-v2 schema binding mismatch: {fact.get('path')}")
    negative = receipt.get("negative_fixture_suite", {})
    for key, expected in tests.items():
        if negative.get(key) != expected:
            raise ValueError(f"backend-v2 test receipt mismatch: {key}")
    replay = receipt.get("independent_root_replay", {})
    if replay.get("file_count") != len(canonical_files):
        raise ValueError("backend-v2 replay file count mismatch")
    for key, value in replay.items():
        if key != "file_count" and value not in {"pass", "byte-identical"}:
            raise ValueError(f"backend-v2 replay check is not passing: {key}")
    source_fact_count = len(manifest.get("source_inputs", []))
    if receipt.get("profile_assertions", {}).get("source_facts_replayed") != source_fact_count:
        raise ValueError("backend-v2 source-fact replay count is stale")
    return {
        "record_count": manifest["record_count"],
        "table_counts": manifest["record_counts"],
        "implementation_bindings": len(receipt.get("implementation", {})),
        "schema_bindings": len(receipt.get("schemas", [])),
        "source_facts_replayed": source_fact_count,
        "tests": tests,
        "result": "pass",
    }


def verify_v21_deterministic_receipt(path: Path, root: Path, version: str, source_commit: str) -> dict[str, Any]:
    receipt = load_json(path)
    for key, expected in {
        "schema_id": "program-matematika-indonesia/backend-v2.1-deterministic-replay-receipt/v1",
        "version": version,
        "source_commit": source_commit,
        "replay_count": 2,
        "result": "pass",
    }.items():
        if receipt.get(key) != expected:
            raise ValueError(f"v2.1 deterministic receipt {key} mismatch")
    facts = []
    for row in receipt.get("files", []):
        source = root / row.get("path", "")
        if not source.is_file() or row.get("bytes") != source.stat().st_size or row.get("sha256") != sha256_file(source):
            raise ValueError(f"v2.1 deterministic receipt file mismatch: {row.get('path')}")
        facts.append(row)
    encoded = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    aggregate = hashlib.sha256(encoded).hexdigest()
    if receipt.get("aggregate_sha256") != aggregate:
        raise ValueError("v2.1 deterministic receipt aggregate mismatch")
    return {"files": len(facts), "aggregate_sha256": aggregate, "replays": 2, "result": "pass"}


def find_bound_facts(value: Any) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if {"path", "bytes", "sha256"}.issubset(value):
            facts.append(value)
        for nested in value.values():
            facts.extend(find_bound_facts(nested))
    elif isinstance(value, list):
        for nested in value:
            facts.extend(find_bound_facts(nested))
    return facts


def verify_v22_package(
    input_package: Path,
    validation_receipt: Path,
    release: Path,
    root: Path,
    version: str,
    source_commit: str,
) -> tuple[Path, dict[str, Any]]:
    canonical = input_package if input_package.parent.name == "packages" else validation_receipt.parent
    release_root = input_package.parent.parent if input_package.parent.name == "packages" and input_package.parent.parent.name == "v2.2" else input_package
    if not canonical.is_relative_to(release_root):
        raise ValueError("backend-v2.2 canonical package is outside its release root")
    manifest = load_json(canonical / "manifest.json")
    seal = load_json(canonical / "seal.json")
    receipt = load_json(validation_receipt)
    if manifest.get("schema_id") != "interlanguage/global-modular-mathematics-backend-manifest/2.2.0":
        raise ValueError("backend-v2.2 manifest schema mismatch")
    if seal.get("schema_id") != "interlanguage/global-modular-mathematics-package-seal/2.2.0":
        raise ValueError("backend-v2.2 seal schema mismatch")
    receipt_schema = receipt.get("schema_id")
    if receipt.get("result") != "pass":
        raise ValueError("backend-v2.2 validation report is not a pass")
    if receipt.get("source_commit") != source_commit:
        raise ValueError("backend-v2.2 validation report source commit mismatch")
    if receipt_schema == "interlanguage/global-modular-mathematics-validation-report/2.2.0":
        if receipt.get("package_id") != manifest.get("package_id") or receipt.get("dataset_id") != manifest.get("dataset_id"):
            raise ValueError("backend-v2.2 package identities disagree")
    elif receipt_schema == "program-matematika-indonesia/backend-v2.2-global-validation-receipt/v1":
        if receipt.get("credentials_recorded") is not False:
            raise ValueError("backend-v2.2 global validation receipt is not credential-free")
        declared = receipt.get("canonical_package", {})
        canonical_files = package_files(canonical)
        facts = [
            {
                "path": path.relative_to(canonical).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in canonical_files
        ]
        facts.sort(key=lambda row: (row["path"].casefold(), row["path"]))
        aggregate = hashlib.sha256(
            "".join(
                f'{row["sha256"]}  {row["bytes"]}  {row["path"]}\n'
                for row in facts
            ).encode("utf-8")
        ).hexdigest()
        if (
            receipt.get("version") != version
            or declared.get("path") != canonical.relative_to(root).as_posix()
            or declared.get("package_id") != manifest.get("package_id")
            or declared.get("file_count") != len(facts)
            or declared.get("total_bytes") != sum(row["bytes"] for row in facts)
            or declared.get("aggregate_sha256") != aggregate
        ):
            raise ValueError("backend-v2.2 global validation receipt package identity mismatch")
    else:
        raise ValueError("backend-v2.2 validation report schema is not admitted")
    if tuple(int(part) for part in version.split(".")) >= (0, 60, 0):
        if receipt_schema != "program-matematika-indonesia/backend-v2.2-global-validation-receipt/v1":
            raise ValueError("v0.60+ requires the global backend-v2.2 validation receipt")
        required_gates = {
            "sealed_a00_package",
            "owner_native_assessment_authority_replay",
            "assessment_json_schema",
            "assessment_solution_gap_exact_set",
            "assessment_stable_id_uniqueness",
            "assessment_uuid5_identity",
            "assessment_zero_prose",
            "global_capability_contract_schema",
            "two_run_validator_replay",
        }
        gates = {
            row.get("gate"): row.get("result")
            for row in receipt.get("checks", [])
            if isinstance(row, dict)
        }
        missing_or_failing = sorted(
            gate for gate in required_gates if gates.get(gate) != "pass"
        )
        assessment_receipt = receipt.get("owner_native_assessment_inventory", {})
        contract_receipt = receipt.get("global_capability_contract", {})
        if missing_or_failing:
            raise ValueError(
                f"backend-v2.2 global receipt gates are missing or failing: {missing_or_failing}"
            )
        if assessment_receipt.get("uuid5_ids_checked") != 40525:
            raise ValueError("backend-v2.2 assessment UUIDv5 check count mismatch")
        if contract_receipt.get("schema_validation") != "pass":
            raise ValueError("backend-v2.2 capability contract schema gate is not a pass")
    check_results = {row.get("result") for row in receipt.get("checks", [])}
    if not receipt.get("checks") or not check_results.issubset({"pass", "inherited", "not_applicable"}):
        raise ValueError("backend-v2.2 validation report contains a non-admitted gate")
    files = package_files(release_root)
    lowered = [path.relative_to(release_root).as_posix().lower() for path in files]
    layers = {
        "schema": any("schema/" in name and name.endswith(".schema.json") for name in lowered),
        "state_vocabulary": any("state-vocabulary" in name and name.endswith(".json") for name in lowered),
        "profile": any("profile" in name and name.endswith(".json") for name in lowered),
        "adapter": any("adapter" in name for name in lowered),
        "builder": any("build" in name for name in lowered),
        "validator": any("validat" in name for name in lowered),
        "sealed_pilot": any("packages/" in name and name.endswith("seal.json") for name in lowered),
    }
    if not all(layers.values()):
        raise ValueError(f"backend-v2.2 release layers are incomplete: {layers}")
    sealed_paths = {
        path.relative_to(canonical).as_posix(): path
        for path in package_files(canonical)
        if path.name != "seal.json"
    }
    declared_seal = {row["path"]: row for row in seal.get("files", [])}
    if set(declared_seal) != set(sealed_paths):
        raise ValueError("backend-v2.2 seal inventory differs from canonical package")
    for relative, source in sealed_paths.items():
        row = declared_seal[relative]
        if row.get("bytes") != source.stat().st_size or row.get("sha256") != sha256_file(source):
            raise ValueError(f"backend-v2.2 seal fact mismatch: {relative}")
    if seal.get("file_count") != len(sealed_paths) or seal.get("total_bytes") != sum(path.stat().st_size for path in sealed_paths.values()):
        raise ValueError("backend-v2.2 seal aggregate counts mismatch")
    digest_lines = "".join(
        f'{declared_seal[path]["sha256"]}  {declared_seal[path]["bytes"]}  {path}\n'
        for path in sorted(declared_seal)
    ).encode("utf-8")
    if seal.get("sealed_digest_sha256") != hashlib.sha256(digest_lines).hexdigest():
        raise ValueError("backend-v2.2 seal aggregate SHA-256 mismatch")
    for fact in find_bound_facts({"manifest": manifest, "seal": seal, "receipt": receipt}):
        relative = Path(fact["path"])
        if not isinstance(fact.get("bytes"), int) or fact["bytes"] < 0 or not re.fullmatch(r"[0-9a-f]{64}", fact.get("sha256", "")):
            raise ValueError(f"backend-v2.2 bound fact is malformed: {fact.get('path')}")
        if fact.get("locator_base") == "owner_backend_root":
            # Zero-copy owner-native evidence is intentionally not bundled. Its
            # exact identity is replayed by the sealed package validator.
            continue
        candidates = (
            [root / relative]
            if fact.get("locator_base") == "program_repository_root"
            else [canonical / relative, release_root / relative, root / relative]
        )
        source = next((path for path in candidates if path.is_file()), None)
        if source is None:
            raise ValueError(f"backend-v2.2 bound file is absent: {fact['path']}")
        if fact["bytes"] != source.stat().st_size or fact["sha256"] != sha256_file(source):
            raise ValueError(f"backend-v2.2 bound file mismatch: {fact['path']}")
    copied_receipt = release / f"GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v{version}.json"
    if copied_receipt.read_bytes() != validation_receipt.read_bytes():
        raise ValueError("release backend-v2.2 validation receipt differs from canonical receipt")
    zip_path = release / v22_archive_filename(version)
    zip_result = verify_backend_zip(zip_path, release_root, "program-matematika-indonesia-backend-v2.2/")
    archive_receipt_path = release / f"GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v{version}.json"
    archive_receipt = load_json(archive_receipt_path)
    if (
        archive_receipt.get("schema_id") != "program-matematika-indonesia/backend-v2.2-archive-receipt/v1"
        or archive_receipt.get("version") != version
        or archive_receipt.get("result") != "pass"
        or archive_receipt.get("replay_count") != 2
        or archive_receipt.get("credentials_recorded") is not False
    ):
        raise ValueError("backend-v2.2 archive receipt is not a deterministic credential-free pass")
    archive = archive_receipt.get("archive", {})
    if archive.get("bytes") != zip_path.stat().st_size or archive.get("sha256") != sha256_file(zip_path) or archive.get("entries") != zip_result["entries"]:
        raise ValueError("backend-v2.2 archive receipt ZIP identity mismatch")
    expected_members = {
        f"program-matematika-indonesia-backend-v2.2/{path.relative_to(release_root).as_posix()}": file_fact(path)
        for path in files
    }
    actual_members = {row["path"]: {"bytes": row["bytes"], "sha256": row["sha256"]} for row in archive_receipt.get("members", [])}
    if actual_members != expected_members:
        raise ValueError("backend-v2.2 archive receipt member inventory mismatch")
    return release_root, {
        "manifest": file_fact(canonical / "manifest.json"),
        "seal": file_fact(canonical / "seal.json"),
        "validation_receipt": file_fact(validation_receipt),
        "archive_receipt": file_fact(archive_receipt_path),
        "zip": zip_result,
        "layers": layers,
        "counts": receipt.get("counts"),
        "result": "pass",
    }


def verify_assessment_inventory_archive(
    release: Path,
    claim: dict[str, Any],
    record_id: int,
    version: str,
) -> dict[str, Any]:
    filename = "o001-a00-assessments-v0.1.0.zip"
    expected_counts = {
        "assessment_components": 13345,
        "assessments": 8105,
        "modules": 75,
        "problems": 8105,
        "solution_gaps": 2865,
        "solutions": 5240,
    }
    expected_claim = {
        "version": "0.1.0",
        "status": "owner_native_validated_zero_prose",
        "roleId": "O001",
        "courseId": "A00",
        "packageId": "urn:uuid:0b253fa5-067e-55b5-8248-cc528b0b4bd1",
        "counts": expected_counts,
        "projectionState": "owner_native_shard_ready_adapter_not_materialized",
    }
    for key, expected in expected_claim.items():
        if claim.get(key) != expected:
            raise ValueError(f"O001/A00 assessment claim differs: {key}")
    assert_central_url(claim.get("package"), record_id, filename)
    expected_github = (
        f"https://github.com/KokunoYumeto/program-matematika-indonesia/"
        f"releases/download/v{version}/{filename}"
    )
    if claim.get("githubPackage") != expected_github:
        raise ValueError("O001/A00 assessment GitHub package URL differs")
    archive_path = release / filename
    prefix = "o001-a00-assessments-v0.1.0/"
    package_manifest = None
    archive_entries: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"O001/A00 assessment ZIP CRC failure: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            name.endswith("/")
            or not name.startswith(prefix)
            or "\\" in name
            or ".." in Path(name).parts
            for name in names
        ):
            raise ValueError("O001/A00 assessment ZIP inventory is unsafe")
        facts = []
        # The sealed shard identity was produced from Windows Path ordering,
        # which is case-insensitive. Reproduce that order when hashing ZIP
        # members so README.md remains after manifest.json, as in the seal.
        for name in sorted(names, key=lambda value: (value.casefold(), value)):
            data = archive.read(name)
            archive_entries.append((name, data))
            if name == f"{prefix}manifest.json":
                package_manifest = json.loads(data.decode("utf-8"))
            facts.append(
                {
                    "path": name.removeprefix(prefix),
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
    aggregate = hashlib.sha256(
        "".join(
            f"{row['sha256']}  {row['bytes']}  {row['path']}\n" for row in facts
        ).encode("utf-8")
    ).hexdigest()
    canonical = claim.get("canonicalPackage", {})
    if (
        canonical.get("path")
        != "backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0"
        or canonical.get("fileCount") != 12
        or canonical.get("bytes") != 19057785
        or canonical.get("aggregateSha256")
        != "5d7c3da1a1b3c33b4f79306fec08a31ebc8f557188f1ec0c088e267e0d9ce222"
        or len(facts) != canonical["fileCount"]
        or sum(row["bytes"] for row in facts) != canonical["bytes"]
        or aggregate != canonical["aggregateSha256"]
    ):
        raise ValueError("O001/A00 assessment archive aggregate differs")
    if (
        not isinstance(package_manifest, dict)
        or package_manifest.get("package_id") != expected_claim["packageId"]
        or package_manifest.get("counts") != expected_counts
        or package_manifest.get("zero_prose_policy", {}).get("copied_formula_bodies") is not False
        or package_manifest.get("zero_prose_policy", {}).get("copied_mathematical_prose") is not False
    ):
        raise ValueError("O001/A00 assessment package manifest differs")
    by_path = {row["path"]: row for row in facts}
    for key in ("manifest", "checksum", "seal"):
        binding = canonical.get(key, {})
        actual = by_path.get(binding.get("path"))
        if not actual or actual["bytes"] != binding.get("bytes") or actual["sha256"] != binding.get("sha256"):
            raise ValueError(f"O001/A00 assessment archive binding differs: {key}")
    def replay_zip() -> bytes:
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            for name, data in sorted(archive_entries):
                info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(
                    info,
                    data,
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        return output.getvalue()

    replay_a = replay_zip()
    replay_b = replay_zip()
    if replay_a != replay_b or replay_a != archive_path.read_bytes():
        raise ValueError("O001/A00 assessment ZIP bytes are not deterministic")
    return {
        "path": filename,
        "entries": len(facts),
        "uncompressed_bytes": sum(row["bytes"] for row in facts),
        "aggregate_sha256": aggregate,
        "bytes": archive_path.stat().st_size,
        "sha256": sha256_file(archive_path),
        "verification": "pass-byte-deterministic",
    }


def verify_central_evidence(
    admission_input: Path,
    readback_input: Path,
    reservation_input: Path | None,
    release: Path,
    version: str,
    record_id: int,
    root: Path,
) -> tuple[dict[str, Any], set[str]]:
    sources = [admission_input, readback_input] + ([reservation_input] if reservation_input else [])
    for source in sources:
        assert source is not None
        copied = release / source.name
        if copied.read_bytes() != source.read_bytes():
            raise ValueError(f"central evidence copy differs from input: {source.name}")
        assert_public_bytes(f"central evidence:{source.name}", copied.read_bytes())
    admission = load_json(admission_input)
    readback = load_json(readback_input)
    if admission.get("schema_id") != "program-matematika-indonesia/central-release-admission-manifest/v1" or admission.get("target_release") != version:
        raise ValueError("central admission manifest release/schema mismatch")
    workspace_root = root.parents[2]
    for fact in admission.get("inputs", []):
        relative = Path(fact.get("path", ""))
        source = admission_input.parent / relative if len(relative.parts) == 1 else workspace_root / relative
        if not source.is_file() or fact.get("bytes") != source.stat().st_size or fact.get("sha256") != sha256_file(source):
            raise ValueError(f"central admission input binding mismatch: {fact.get('path')}")
    admissions = admission.get("admissions", [])
    supplements = admission.get("supplements", [])
    summary = admission.get("summary", {})
    if version == "0.60.0":
        infrastructure = admission.get("infrastructure_admissions", [])
        valid_primary = all(
            isinstance(row.get("record"), int)
            and row.get("doi") == f"10.5281/zenodo.{row['record']}"
            and str(row.get("learner_route", "")).startswith("https://")
            and isinstance(row.get("primary_artifact", {}).get("bytes"), int)
            and row["primary_artifact"]["bytes"] > 0
            and re.fullmatch(r"[0-9a-f]{64}", row["primary_artifact"].get("sha256", ""))
            for row in admissions
        )
        valid_infrastructure = all(
            row.get("zero_prose") is True
            and isinstance(row.get("files"), int)
            and row["files"] > 0
            and isinstance(row.get("bytes"), int)
            and row["bytes"] > 0
            and re.fullmatch(r"[0-9a-f]{64}", row.get("aggregate_sha256", ""))
            for row in infrastructure
        )
        if (
            len({row.get("course_id") for row in admissions}) != len(admissions)
            or summary.get("refreshed_course_routes") != len(admissions)
            or summary.get("new_html_readers")
            != sum(isinstance(row.get("central_html_reader"), dict) for row in admissions)
            or summary.get("new_owner_native_backend_shards") != len(infrastructure)
            or summary.get("completed_public_course_roles_before")
            != summary.get("completed_public_course_roles_after")
            or summary.get("honest_global_backend_state")
            != "phase_release_not_global_migration_complete"
            or not valid_primary
            or not valid_infrastructure
        ):
            raise ValueError("v0.60 central admission summary is not derivable from its rows")
    elif (
        len({row.get("course_id") for row in admissions}) != len(admissions)
        or summary.get("admitted_primary_course_routes") != len(admissions)
        or summary.get("admitted_partial_courses") != sum(row.get("state_after") != "published" for row in admissions)
        or summary.get("admitted_newly_complete_courses") != sum(row.get("state_after") == "published" for row in admissions)
        or summary.get("admitted_separate_supplements") != len(supplements)
        or summary.get("admitted_primary_selected_route_bytes") != sum(row.get("bytes", -1) for row in admissions)
        or summary.get("supplement_selected_route_bytes") != sum(row.get("bytes", -1) for row in supplements)
    ):
        raise ValueError("central admission summary is not derivable from its rows")
    binding = readback.get("source_admission_manifest", {})
    if (
        readback.get("schema_id") != "program-matematika-indonesia/owner-reader-public-readback/v1"
        or readback.get("result") != "pass"
        or binding.get("bytes") != admission_input.stat().st_size
        or binding.get("sha256") != sha256_file(admission_input)
    ):
        raise ValueError("owner-reader readback does not bind the supplied admission manifest")
    routes = readback.get("routes", [])
    if readback.get("route_count") != len(routes) or readback.get("total_bytes") != sum(row.get("bytes", -1) for row in routes):
        raise ValueError("owner-reader readback aggregate mismatch")
    for row in routes:
        if row.get("http_status") != 200 or row.get("content_type") != "text/html" or row.get("bytes", 0) <= 0 or not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", "")):
            raise ValueError(f"owner-reader row is not a complete HTTP/hash proof: {row.get('course_id')}")
    allowed_route_courses = {row.get("course_id") for row in admissions}
    if version in {"0.60.0", "0.61.0"}:
        live_authority = load_json(root / "backend/authority/curriculum-authority-v1.json")
        allowed_route_courses = {
            row.get("id") for row in live_authority.get("catalog", {}).get("courses", [])
        }
    if not {row.get("course_id") for row in routes}.issubset(allowed_route_courses):
        raise ValueError("owner-reader evidence references a course outside the admitted curriculum")
    result: dict[str, Any] = {
        "admission": file_fact(admission_input),
        "owner_reader_readback": file_fact(readback_input),
        "owner_html_routes": len(routes),
    }
    if reservation_input:
        reservation = load_json(reservation_input)
        if (
            reservation.get("schema_id") != "program-matematika-indonesia/zenodo-version-reservation/v1"
            or reservation.get("program_version") != version
            or reservation.get("reserved_version", {}).get("draft_record_id") != record_id
            or reservation.get("reserved_version", {}).get("visibility_intent") != "public_open"
            or reservation.get("authorization_route", {}).get("credential_material_recorded") is not False
        ):
            raise ValueError("Zenodo reservation evidence does not match this public release")
        result["reservation"] = file_fact(reservation_input)
    generated = {f"releases/v{version}/{source.name}" for source in sources if source is not None}
    return result, generated


def assert_central_url(url: str, record_id: int, filename: str) -> None:
    expected = f"https://zenodo.org/records/{record_id}/files/{filename}"
    if not isinstance(url, str) or not url.startswith(expected):
        raise ValueError(f"central release URL is not bound to record {record_id}: {filename}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--record-id", required=True, type=int)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--release-dir", required=True, type=Path)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--backend-v2-package", required=True, type=Path)
    parser.add_argument("--backend-v2-validation-receipt", required=True, type=Path)
    parser.add_argument("--backend-v22-package", required=True, type=Path)
    parser.add_argument("--backend-v22-validation-receipt", required=True, type=Path)
    parser.add_argument("--admission-manifest", required=True, type=Path)
    parser.add_argument("--owner-reader-readback", required=True, type=Path)
    parser.add_argument("--reservation-receipt", type=Path)
    parser.add_argument("--coordinator-logbook-root", required=True, type=Path)
    parser.add_argument("--output-report", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    backend_v2 = args.backend_v2_package.resolve()
    backend_v2_receipt = args.backend_v2_validation_receipt.resolve()
    backend_v22 = args.backend_v22_package.resolve()
    backend_v22_receipt = args.backend_v22_validation_receipt.resolve()
    admission = args.admission_manifest.resolve()
    owner_readback = args.owner_reader_readback.resolve()
    reservation = args.reservation_receipt.resolve() if args.reservation_receipt else None
    output_report = args.output_report.resolve()
    version = args.version

    for label, path in {
        "release": release,
        "backend-v1": backend,
        "backend-v2": backend_v2,
        "backend-v2.2": backend_v22,
    }.items():
        if not path.is_relative_to(root):
            raise ValueError(f"{label} must remain inside the project root")
    if not args.coordinator_logbook_root.resolve().is_dir():
        raise ValueError("coordinator logbook root must exist")
    if output_report.parent != release:
        raise ValueError("validation report must be written directly inside the release directory")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ValueError("source commit must be a full lowercase Git SHA-1")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    if head != args.source_commit:
        raise ValueError("source commit differs from the validated repository HEAD")

    static_result = json.loads(subprocess.run(
        ["node", str(root / "scripts" / "validate-static-site.mjs")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout)
    learner_result = json.loads(subprocess.run(
        ["node", str(root / "scripts" / "validate-learner-read-model.mjs")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout)
    if static_result.get("status") != "pass" or learner_result.get("status") != "pass" or learner_result.get("deterministic_replay") != "byte-identical":
        raise ValueError("static site or learner projection validation failed")

    migration_paths = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    if {path.parent.name for path in migration_paths} != set(MIGRATION_RECEIPT_FILENAMES):
        raise ValueError("complete-corpus migration receipt directory set mismatch")
    migration_result = json.loads(subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts" / "validate-migration-receipt-v1.py"),
            "--schema",
            str(root / "schemas" / "backend-migration-receipt-v1.schema.json"),
            *[str(path) for path in migration_paths],
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout)
    migration_docs = {load_json(path)["migration_id"]: load_json(path) for path in migration_paths}
    if set(migration_docs) != set(EXPECTED_MIGRATIONS):
        raise ValueError("complete-corpus migration receipt identity set mismatch")
    for migration_id in EXPECTED_MIGRATIONS:
        if migration_docs[migration_id].get("validation", {}).get("result") != "pass":
            raise ValueError(f"migration receipt is not a validation pass: {migration_id}")
    for path in migration_paths:
        copied = release / MIGRATION_RECEIPT_FILENAMES[path.parent.name]
        if copied.read_bytes() != path.read_bytes():
            raise ValueError(f"migration receipt release copy differs: {copied.name}")

    catalog_path = release / f"program-matematika-indonesia-catalog-v{version}.json"
    catalog_schema_path = release / "program-matematika-indonesia-catalog-v1.schema.json"
    catalog = load_json(catalog_path)
    catalog_schema = load_json(catalog_schema_path)
    expected_schema_url = f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-catalog-v1.schema.json"
    if catalog.get("$schema") != expected_schema_url or catalog_schema.get("$id") != expected_schema_url:
        raise ValueError("catalog and schema are not bound to the reserved release record")
    if catalog_schema_path.read_bytes() != (root / "schemas" / "catalog-v1.schema.json").read_bytes():
        raise ValueError("release catalog schema differs from the validated root schema")
    Draft202012Validator(catalog_schema, format_checker=FormatChecker()).validate(catalog)

    authority_path = root / "backend" / "authority" / "curriculum-authority-v1.json"
    authority_schema_path = root / "schemas" / "v1" / "curriculum-authority-v1.schema.json"
    read_model_path = root / "docs" / "data" / "learner-read-model.json"
    read_model_schema_path = root / "schemas" / "v1" / "learner-read-model-v1.schema.json"
    authority = load_json(authority_path)
    authority_schema = load_json(authority_schema_path)
    read_model = load_json(read_model_path)
    read_model_schema = load_json(read_model_schema_path)
    Draft202012Validator(authority_schema, format_checker=FormatChecker()).validate(authority)
    Draft202012Validator(read_model_schema, format_checker=FormatChecker()).validate(read_model)
    if authority.get("catalog") != catalog:
        raise ValueError("release catalog differs from canonical curriculum authority")
    if catalog.get("sourceCommit") != args.source_commit:
        raise ValueError("catalog sourceCommit differs from validated HEAD")
    program = catalog.get("program", {})
    courses = catalog.get("courses", [])
    if program.get("version") != version:
        raise ValueError("catalog program version differs from requested release")
    if program.get("zenodo") != f"https://doi.org/10.5281/zenodo.{args.record_id}":
        raise ValueError("catalog DOI differs from reserved release record")
    if authority.get("lineage", {}).get("transition", {}).get("to_version") != version or authority.get("lineage", {}).get("transition", {}).get("zenodo_record_id") != args.record_id:
        raise ValueError("authority transition is not bound to this release")

    course_ids = [course.get("id") for course in courses]
    if len(course_ids) != len(set(course_ids)):
        raise ValueError("catalog course IDs are duplicated")
    unresolved = [course["id"] for course in courses if course.get("state") == "unresolved"]
    published = [course["id"] for course in courses if course.get("state") == "published"]
    counts = catalog.get("counts", {})
    expected_counts = {
        "courseRoles": len(courses),
        "selectedCorpusRoles": len(courses) - len(unresolved),
        "unresolvedRoles": len(unresolved),
        "completedPublicCourseRoles": len(published),
        "completedPublicRecords": len(program.get("completedPublicRecordDois", [])),
    }
    if counts != expected_counts:
        raise ValueError(f"catalog counts are not derivable from current authority: {counts} != {expected_counts}")
    if program.get("unresolvedRoleIds") != unresolved or program.get("completedPublicCourseRoleIds") != published:
        raise ValueError("program role lists differ from course states")
    if len(set(program.get("completedPublicRecordDois", []))) != counts["completedPublicRecords"]:
        raise ValueError("completed public record DOI list contains duplicates")
    if read_model.get("program") != program or read_model.get("summary", {}).get("course_count") != len(courses) or read_model.get("summary", {}).get("published_course_count") != len(published):
        raise ValueError("learner model summary/program differs from current catalog")
    if read_model.get("summary", {}).get("readback_overlay_count") != len(authority.get("public_readback_overlays", [])):
        raise ValueError("learner model overlay count differs from authority")

    release_copies = {
        "curriculum-authority-v1.json": authority_path,
        "learner-read-model-v1.json": read_model_path,
        "curriculum-authority-v1.schema.json": authority_schema_path,
        "learner-read-model-v1.schema.json": read_model_schema_path,
        "federation-unit-package-v2.1.schema.json": root / "backend/v2.1/schema/federation-unit-package-v2.1.schema.json",
        "federation-unit-record-v2.1.schema.json": root / "backend/v2.1/schema/federation-unit-record-v2.1.schema.json",
    }
    for release_name, source in release_copies.items():
        if (release / release_name).read_bytes() != source.read_bytes():
            raise ValueError(f"release authority/model copy differs: {release_name}")
    if (root / "docs/data/curriculum-authority-v1.json").read_bytes() != authority_path.read_bytes():
        raise ValueError("public curriculum authority differs from canonical authority")

    actual_catalog_migrations = program.get("backend", {}).get("completeCorpusMigrations", [])
    if len(actual_catalog_migrations) != len(migration_docs):
        raise ValueError("catalog migration claim count differs from validated receipt count")
    unmatched_claims = list(actual_catalog_migrations)
    for migration_id, doc in migration_docs.items():
        matches = [
            row
            for row in unmatched_claims
            if row.get("recordCount") == doc["target"]["record_count"]
            and row.get("result") == EXPECTED_MIGRATIONS[migration_id]
            and isinstance(row.get("corpus"), str)
            and row["corpus"].strip()
        ]
        if len(matches) != 1:
            raise ValueError(f"catalog has no unique claim for migration {migration_id}")
        unmatched_claims.remove(matches[0])
    if unmatched_claims:
        raise ValueError("catalog contains migration claims with no validated receipt")
    migration_target_records = sum(doc["target"]["record_count"] for doc in migration_docs.values())

    v2_tests = run_backend_v2_tests(root)
    v2_manifest = verify_manifest_inventory(backend_v2)
    v2_receipt_result = verify_v2_receipt(backend_v2_receipt, backend_v2, root, v2_tests)
    v2_claim = program["backend"]["federationV2"]
    claim_counts = {
        "recordCount": v2_manifest["record_count"],
        "datasetCount": v2_manifest["record_counts"]["datasets"],
        "courseCount": v2_manifest["record_counts"]["courses"],
        "learnerSurfaceCount": v2_manifest["record_counts"]["reader_surfaces"],
        "webRouteCount": v2_manifest["record_counts"]["web_routes"],
        "identityCrosswalkCount": v2_manifest["record_counts"]["identity_crosswalks"],
        "publicationEventCount": v2_manifest["record_counts"]["publication_events"],
        "qaEventCount": v2_manifest["record_counts"]["qa_events"],
    }
    for key, expected in claim_counts.items():
        if v2_claim.get(key) != expected:
            raise ValueError(f"catalog federation-v2 count mismatch: {key}")
    if v2_claim.get("version") not in v2_manifest.get("dataset_version", "") or v2_claim.get("status") != "validated":
        raise ValueError("catalog federation-v2 version/status mismatch")
    for key, filename in {
        "package": f"program-matematika-indonesia-backend-v2-v{version}.zip",
        "packageSchema": "federation-package-v2.schema.json",
        "recordSchema": "federation-record-v2.schema.json",
        "validationReceipt": f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json",
    }.items():
        assert_central_url(v2_claim.get(key), args.record_id, filename)

    copied_v2_receipt = release / f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json"
    if copied_v2_receipt.read_bytes() != backend_v2_receipt.read_bytes():
        raise ValueError("release backend-v2 receipt differs from input")
    for source_name, release_name in V2_RELEASE_FILES.items():
        if (release / release_name).read_bytes() != (root / source_name).read_bytes():
            raise ValueError(f"release backend-v2 support file differs: {release_name}")

    v21_claim = program["backend"]["federationV21"]
    if v21_claim.get("status") != "pilot_validated" or not v21_claim.get("pilot_courses") or not v21_claim.get("pilot_units"):
        raise ValueError("catalog federation-v2.1 claim is incomplete")
    for key, filename in {
        "packageSchema": "federation-unit-package-v2.1.schema.json",
        "recordSchema": "federation-unit-record-v2.1.schema.json",
        "package": f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip",
    }.items():
        assert_central_url(v21_claim.get(key), args.record_id, filename)

    v22_root, v22_result = verify_v22_package(
        backend_v22,
        backend_v22_receipt,
        release,
        root,
        version,
        args.source_commit,
    )
    v22_claim = program["backend"].get("federationV22")
    if not isinstance(v22_claim, dict) or "validated" not in str(v22_claim.get("status", "")):
        raise ValueError("catalog has no validated backend-v2.2 claim")
    if "package" in v22_claim:
        assert_central_url(v22_claim["package"], args.record_id, v22_archive_filename(version))
    if "validationReceipt" in v22_claim:
        assert_central_url(v22_claim["validationReceipt"], args.record_id, f"GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v{version}.json")
    if "archiveReceipt" in v22_claim:
        assert_central_url(v22_claim["archiveReceipt"], args.record_id, f"GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v{version}.json")
    assessment_result = None
    if tuple(int(part) for part in version.split(".")) >= (0, 60, 0):
        contract_claim = program["backend"].get("capabilityContractV1")
        if not isinstance(contract_claim, dict):
            raise ValueError("catalog has no global capability-contract claim")
        contract_paths = {
            "contract": root / "backend/v2.2/global-capability-contract-v0.1.0.json",
            "schema": root / "backend/v2.2/schema/global-capability-contract-v0.1.schema.json",
        }
        for key, filename in {
            "contract": "global-capability-contract-v0.1.0.json",
            "schema": "global-capability-contract-v0.1.schema.json",
        }.items():
            assert_central_url(contract_claim.get(key), args.record_id, filename)
            if (release / filename).read_bytes() != contract_paths[key].read_bytes():
                raise ValueError(f"global capability-contract release file differs: {filename}")
        contract = load_json(contract_paths["contract"])
        contract_schema = load_json(contract_paths["schema"])
        Draft202012Validator.check_schema(contract_schema)
        contract_errors = sorted(
            Draft202012Validator(
                contract_schema,
                format_checker=FormatChecker(),
            ).iter_errors(contract),
            key=lambda error: list(error.absolute_path),
        )
        if contract_errors:
            raise ValueError(
                f"global capability-contract schema failure: {contract_errors[0].message}"
            )
        for key, filename in {
            "githubContract": "global-capability-contract-v0.1.0.json",
            "githubSchema": "global-capability-contract-v0.1.schema.json",
        }.items():
            expected = (
                f"https://github.com/KokunoYumeto/program-matematika-indonesia/"
                f"releases/download/v{version}/{filename}"
            )
            if contract_claim.get(key) != expected:
                raise ValueError(f"global capability-contract GitHub URL differs: {key}")
        assessment_claim = program["backend"].get("assessmentInventoryV1")
        if not isinstance(assessment_claim, dict):
            raise ValueError("catalog has no O001/A00 assessment-inventory claim")
        assessment_result = verify_assessment_inventory_archive(
            release,
            assessment_claim,
            args.record_id,
            version,
        )

    learner_claim = program["backend"]["learnerReadModelV1"]
    if learner_claim.get("courseCount") != len(courses) or learner_claim.get("prerequisiteEdgeCount") != sum(len(course.get("prerequisites", [])) for course in courses):
        raise ValueError("learner read-model backend claim counts are stale")
    for key, filename in {
        "authority": "curriculum-authority-v1.json",
        "authoritySchema": "curriculum-authority-v1.schema.json",
        "readModel": "learner-read-model-v1.json",
        "readModelSchema": "learner-read-model-v1.schema.json",
        "validationReceipt": f"LOCAL_RELEASE_VALIDATION_v{version}.json",
    }.items():
        assert_central_url(learner_claim.get(key), args.record_id, filename)
    assert_central_url(program["backend"]["educationalAccessResearch"]["sourcePackage"], args.record_id, f"program-matematika-indonesia-source-v{version}.zip")

    surface_ids = set()
    course_id_set = set(course_ids)
    for overlay in authority.get("public_readback_overlays", []):
        if overlay.get("surface_id") in surface_ids:
            raise ValueError("duplicate public readback surface ID")
        surface_ids.add(overlay.get("surface_id"))
        if overlay.get("course_id") not in course_id_set or overlay.get("effective_publication_state") != "public" or overlay.get("bytes", 0) <= 0 or not re.fullmatch(r"[0-9a-f]{64}", overlay.get("sha256", "")):
            raise ValueError(f"invalid public readback overlay: {overlay.get('surface_id')}")

    central_evidence, generated_evidence_paths = verify_central_evidence(
        admission,
        owner_readback,
        reservation,
        release,
        version,
        args.record_id,
        root,
    )

    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    v1_result = verify_v1_immutable_archive(
        backend_zip,
        release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
    )
    v21_receipt_name = f"GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v{version}.json"
    v21_result = verify_v21_deterministic_receipt(release / v21_receipt_name, root, version, args.source_commit)

    html_path = release / f"program-matematika-indonesia-v{version}.html"
    learner_html_path = release / f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html"
    if learner_html_path.read_bytes() != html_path.read_bytes():
        raise ValueError("learner-first HTML differs from compatibility HTML")
    html = html_path.read_text(encoding="utf-8")
    for required in (
        f"10.5281/zenodo.{args.record_id}",
        f"v{version}",
        f"{len(courses)} korpus terpilih",
        "produksi yang belum selesai tetap dilabeli dengan jelas",
        f"Mulai belajar — buka {len(courses)} mata kuliah",
    ):
        if required not in html:
            raise ValueError(f"standalone HTML is missing {required!r}")
    learner_pdf = (release / f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf").read_bytes()
    if not learner_pdf.startswith(b"%PDF-") or not learner_pdf.rstrip().endswith(b"%%EOF") or program["website"].encode() not in learner_pdf:
        raise ValueError("learner-first PDF is malformed or lacks the learner-site URI")
    og_path = release / f"program-matematika-indonesia-og-v{version}.png"
    if og_path.read_bytes() != (root / "docs/og.png").read_bytes():
        raise ValueError("release social preview differs from validated site image")

    generated_catalog = f"releases/v{version}/program-matematika-indonesia-catalog-v{version}.json"
    allowed_generated = {generated_catalog, *generated_evidence_paths}
    zip_results = {
        "source": verify_source_zip(
            release / f"program-matematika-indonesia-source-v{version}.zip",
            root,
            args.source_commit,
            allowed_generated,
        ),
        "backend_v1": v1_result,
        "backend_v2": verify_backend_zip(
            release / f"program-matematika-indonesia-backend-v2-v{version}.zip",
            backend_v2,
            "program-matematika-indonesia-backend-v2/",
        ),
        "backend_v21": verify_backend_zip(
            release / f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip",
            root / "backend/v2.1",
            "program-matematika-indonesia-backend-v2.1/",
        ),
        "backend_v22": v22_result["zip"],
    }
    if assessment_result is not None:
        zip_results["assessment_inventory"] = assessment_result
    if zip_results["source"]["source_commit"] != args.source_commit:
        raise ValueError("source ZIP is not bound to validated HEAD")

    expected_release_names = {
        "BACKEND_CONVERGENCE_V1.md",
        "MIGRATION_HANDOFF_V1.md",
        f"RELEASE_NOTES_v{version}.md",
        "interlanguage-backend-migration-receipt-v1.schema.json",
        *V2_RELEASE_FILES.values(),
        "interlanguage-math-backend-v1.schema.json",
        "interlanguage-source-format-profile-v1.schema.json",
        "program-matematika-indonesia-catalog-v1.schema.json",
        "curriculum-authority-v1.json",
        "curriculum-authority-v1.schema.json",
        "learner-read-model-v1.json",
        "learner-read-model-v1.schema.json",
        "global-capability-contract-v0.1.0.json",
        "global-capability-contract-v0.1.schema.json",
        "federation-unit-package-v2.1.schema.json",
        "federation-unit-record-v2.1.schema.json",
        f"program-matematika-indonesia-catalog-v{version}.json",
        f"program-matematika-indonesia-og-v{version}.png",
        f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf",
        f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html",
        f"program-matematika-indonesia-v{version}.html",
        f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
        f"program-matematika-indonesia-backend-v1-v{version}.zip",
        f"program-matematika-indonesia-backend-v2-v{version}.zip",
        f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip",
        v22_archive_filename(version),
        f"program-matematika-indonesia-source-v{version}.zip",
        f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json",
        v21_receipt_name,
        f"GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v{version}.json",
        f"GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v{version}.json",
        *MIGRATION_RECEIPT_FILENAMES.values(),
        admission.name,
        owner_readback.name,
    }
    if assessment_result is not None:
        expected_release_names.add("o001-a00-assessments-v0.1.0.zip")
    if reservation:
        expected_release_names.add(reservation.name)
    actual_release_names = {
        path.name
        for path in release.iterdir()
        if path.is_file() and path.name not in {"CHECKSUMS.sha256", output_report.name}
    }
    if actual_release_names != expected_release_names:
        raise ValueError(
            f"release inventory mismatch; missing={sorted(expected_release_names - actual_release_names)}; extra={sorted(actual_release_names - expected_release_names)}"
        )
    learner_first = [
        f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf",
        f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html",
    ]
    if sorted(actual_release_names)[:2] != learner_first:
        raise ValueError("release inventory is not lexically learner-first")

    files = []
    for path in sorted(release / name for name in expected_release_names):
        assert_public_bytes(f"release:{path.name}", path.read_bytes())
        files.append({"name": path.name, **file_fact(path)})
    report = {
        "schema_id": "program-matematika-indonesia/local-release-validation/v3",
        "version": version,
        "reserved_zenodo_record_id": args.record_id,
        "result": "pass",
        "checks": {
            "static_site": static_result,
            "catalog_draft_2020_12": "pass",
            "catalog_counts": counts,
            "catalog_schema_identity_and_bytes": "pass",
            "curriculum_authority_schema": "pass",
            "learner_read_model_schema": "pass",
            "learner_read_model_projection": learner_result,
            "phase_two_public_artifacts": {name: file_fact(source) for name, source in release_copies.items()},
            "source_commit_binding": args.source_commit,
            "backend_v1_immutable_package": v1_result,
            "backend_v2_validation_receipt": v2_receipt_result,
            "backend_v21_deterministic_replay_receipt": v21_result,
            "backend_v22": v22_result,
            "assessment_inventory": assessment_result,
            "complete_corpus_migrations": migration_result,
            "complete_corpus_migration_target_records": migration_target_records,
            "central_evidence": central_evidence,
            "release_inventory": {"files_before_report": len(files), "result": "exact"},
            "privacy_scan": "pass",
            "zip_verification": zip_results,
            "standalone_html": "pass",
        },
        "files_before_checksum": files,
    }
    report_bytes = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    assert_public_bytes("local release validation report", report_bytes)
    output_report.write_bytes(report_bytes)
    print(json.dumps({"result": "pass", "report": str(output_report), "sha256": sha256_file(output_report)}, sort_keys=True))


if __name__ == "__main__":
    main()
