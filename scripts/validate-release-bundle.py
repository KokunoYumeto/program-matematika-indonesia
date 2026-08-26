#!/usr/bin/env python3
"""Validate a central release bundle before Zenodo upload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


EXPECTED_MIGRATIONS = {
    "dmoi4-id-0.1.0-to-interlanguage-v1.0.0": {
        "corpus": "Discrete Mathematics: An Open Introduction 4 — Bahasa Indonesia",
        "result": "lossless-zero-copy-pass",
    },
    "erdman-functional-analysis-id-2026.08.25-to-interlanguage-v1.0.0": {
        "corpus": "Erdman — Functional Analysis and Operator Algebras, Bahasa Indonesia",
        "result": "lossless-zero-copy-virtual-adapter-pass",
    },
    "hefferon-linear-algebra-id-v2026.08.22-to-interlanguage-v1.0.0": {
        "corpus": "Hefferon — Linear Algebra, Bahasa Indonesia v2026.08.22",
        "result": "lossless-zero-copy-one-to-one-native-backend-adapter-pass",
    },
    "o002-b80-id-2026.08.22.1-to-interlanguage-v1.0.0": {
        "corpus": "Komputasi Matematis dan Eksperimen yang Dapat Direproduksi — Bahasa Indonesia",
        "result": "lossless-zero-copy-one-to-one-native-catalog-adapter-pass",
    },
    "openlogic-id-olp-0722-to-interlanguage-v1.0.0": {
        "corpus": "Open Logic Project — OLP-0722, Bahasa Indonesia",
        "result": "deterministic-zero-copy-pass",
    },
    "judson-id-v1-2026.08.21.1": {
        "corpus": "Judson — Abstract Algebra: Theory and Applications, Bahasa Indonesia",
        "result": "additive-zero-copy-pass",
    },
    "yaintt-r014-id-to-interlanguage-v1.0.0": {
        "corpus": "Yet Another Introductory Number Theory Textbook, Bahasa Indonesia",
        "result": "lossless-additive-adapter-pass",
    },
    "r012-applied-combinatorics-id-to-v1": {
        "corpus": "Keller–Trotter — Applied Combinatorics, Bahasa Indonesia",
        "result": "lossless-additive-one-common-record-per-native-record-pass",
    },
    "mathematics-in-lean-id-v4.30.0-id.3-to-interlanguage-v1.0.0": {
        "corpus": "Mathematics in Lean — Bahasa Indonesia v4.30.0-id.3",
        "result": "lossless-zero-copy-one-to-one-pass",
    },
    "prealgebra2e-r001-id-v0.2.7-to-interlanguage-v1.0.0": {
        "corpus": "OpenStax Prealgebra 2e — Bahasa Indonesia v0.2.7",
        "result": "lossless-streaming-zero-copy-adapter-pass",
    },
    "o005-c120-id-v1.01-complete-r5-to-interlanguage-v1.0.0": {
        "corpus": "Lega v1.01 — Pemodelan Matematis, Bahasa Indonesia",
        "result": "lossless-replayable-zero-copy-adapter-pass",
    },
    "o018-c130-r017-book1-id5-to-interlanguage-v1": {
        "corpus": "Open Optimization Book 1 + laboratorium Pyomo/HiGHS O018, Bahasa Indonesia",
        "result": "lossless-zero-copy-one-to-one-plus-segment-variant-projection-pass",
    },
    "tea-time-numerical-analysis-id-v1": {
        "corpus": "Tea Time Numerical Analysis — Bahasa Indonesia v3.0-id.2-r1",
        "result": "additive-zero-copy-virtual-adapter-pass",
    },
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

EXPECTED_V2_COUNTS = {
    "datasets": 34,
    "programs": 1,
    "courses": 40,
    "reader_surfaces": 128,
    "web_routes": 41,
    "publication_events": 52,
    "qa_events": 16,
    "identity_crosswalks": 2122,
}
EXPECTED_V2_RECORD_COUNT = sum(EXPECTED_V2_COUNTS.values())
EXPECTED_FEDERATION_VERSION = "0.3.0"
EXPECTED_FEDERATION_DATASET_VERSION = "program-matematika-indonesia-federation-v0.3.0"

PRIVATE_BYTE_MARKERS = (
    bytes([70, 108, 111, 114, 105, 115]).lower(),
    bytes([99, 58, 92, 117, 115, 101, 114, 115, 92]),
    bytes([99, 58, 47, 117, 115, 101, 114, 115, 47]),
    bytes([47, 117, 115, 101, 114, 115, 47]),
    bytes([46, 99, 111, 100, 101, 120, 47, 97, 116, 116, 97, 99, 104, 109, 101, 110, 116, 115]),
    bytes([102, 105, 108, 101, 58, 47, 47]),
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


def assert_public_bytes(label: str, data: bytes) -> None:
    lowered = data.lower()
    if any(marker in lowered for marker in PRIVATE_BYTE_MARKERS):
        raise ValueError(f"private or credential-bearing marker in public artifact: {label}")


def verify_source_zip(
    path: Path,
    root: Path,
    source_commit: str,
    allowed_generated_source_paths: set[str],
) -> dict:
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
        manifest_bytes = archive.read("SOURCE_MANIFEST.json")
        assert_public_bytes("source ZIP:SOURCE_MANIFEST.json", manifest_bytes)
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema_id") != "program-matematika-indonesia/source-manifest/v2":
            raise ValueError("source ZIP manifest schema is not v2")
        declared = {entry["path"]: entry for entry in manifest["files"]}
        actual = set(names) - {"SOURCE_MANIFEST.json"}
        if set(declared) != actual:
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


def verify_backend_zip(path: Path, package: Path, prefix: str) -> dict:
    expected = {
        prefix + source.relative_to(package).as_posix(): source
        for source in package.rglob("*")
        if source.is_file()
        and not (
            prefix == "program-matematika-indonesia-backend-v2.1/"
            and ("__pycache__" in source.parts or source.suffix == ".pyc")
        )
    }
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"backend ZIP CRC failure: {bad}")
        if set(archive.namelist()) != set(expected):
            raise ValueError("backend ZIP inventory mismatch")
        for name, source in expected.items():
            data = archive.read(name)
            if data != source.read_bytes():
                raise ValueError(f"backend ZIP entry mismatch: {name}")
            assert_public_bytes(f"backend ZIP:{name}", data)
    return {"entries": len(expected), "privacy_scan": "pass", "result": "pass"}


def verify_v21_deterministic_receipt(path: Path, root: Path, version: str, source_commit: str) -> dict:
    receipt = json.loads(path.read_text(encoding="utf-8"))
    expected_identity = {
        "schema_id": "program-matematika-indonesia/backend-v2.1-deterministic-replay-receipt/v1",
        "version": version,
        "source_commit": source_commit,
        "replay_count": 2,
        "result": "pass",
    }
    for key, expected in expected_identity.items():
        if receipt.get(key) != expected:
            raise ValueError(f"v2.1 deterministic receipt {key} mismatch")
    roots = [
        "backend/v2.1/pilots/a00-prealgebra",
        "backend/v2.1/pilots/b10-dmoi",
        "backend/v2.1/pilots/c100-geometry",
        "backend/v2.1/pilots/d20-functional-analysis",
        "backend/v2.1/planning/educational-access",
        "backend/research/educational-access-v0.1.0",
        "docs/id-ID/courses/C100",
        "docs/id-ID/courses/D20",
    ]
    explicit = [
        "docs/data/unit-route-C100-v2.1.json",
        "docs/data/unit-route-D20-v2.1.json",
        "docs/data/unit-route-v2.1.json",
        "docs/data/unit-routes-v2.1.json",
        "docs/data/educational-access.json",
        "schemas/educational-access-federation-v1.schema.json",
    ]
    paths: set[Path] = set()
    for relative in roots:
        paths.update(candidate for candidate in (root / relative).rglob("*") if candidate.is_file())
    paths.update(root / relative for relative in explicit)
    facts = [
        {
            "path": item.relative_to(root).as_posix(),
            "bytes": item.stat().st_size,
            "sha256": sha256_file(item),
        }
        for item in sorted(paths)
        if "__pycache__" not in item.parts and item.suffix != ".pyc"
    ]
    encoded = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    aggregate_sha256 = hashlib.sha256(encoded).hexdigest()
    if receipt.get("files") != facts or receipt.get("aggregate_sha256") != aggregate_sha256:
        raise ValueError("v2.1 deterministic receipt no longer matches exact release inputs")
    return {
        "aggregate_sha256": aggregate_sha256,
        "files": len(facts),
        "receipt_bytes": path.stat().st_size,
        "receipt_sha256": sha256_file(path),
        "replays": 2,
        "result": "pass",
    }


def verify_v1_immutable_archive(path: Path, copied_validation_report: Path) -> dict:
    if not path.is_file() or sha256_file(path) != EXPECTED_V1_ARCHIVE_SHA256:
        raise ValueError("immutable backend-v1 archive identity mismatch")
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"immutable backend-v1 archive CRC failure: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            not name.startswith(EXPECTED_V1_ARCHIVE_PREFIX) or name.endswith("/")
            for name in names
        ):
            raise ValueError("immutable backend-v1 archive inventory is unsafe")
        members = {
            name.removeprefix(EXPECTED_V1_ARCHIVE_PREFIX): archive.read(name)
            for name in names
        }
    if len(members) != 84:
        raise ValueError("immutable backend-v1 archive must contain exactly 84 files")
    for relative, expected_sha256 in EXPECTED_V1_PACKAGE_PINS.items():
        data = members.get(relative)
        if data is None or hashlib.sha256(data).hexdigest() != expected_sha256:
            raise ValueError(f"immutable backend-v1 identity mismatch: {relative}")

    manifest = json.loads(members["manifest.json"].decode("utf-8"))
    if manifest.get("record_count") != 2122:
        raise ValueError("immutable backend-v1 manifest record count is not 2,122")
    declared = {entry["path"]: entry for entry in manifest.get("files", [])}
    if set(members) != set(declared) | {"manifest.json", "validation_report.json"}:
        raise ValueError("immutable backend-v1 package inventory mismatch")
    for relative, entry in declared.items():
        data = members[relative]
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"immutable backend-v1 manifest member mismatch: {relative}")
        assert_public_bytes(f"immutable backend-v1:{relative}", data)
    report_bytes = members["validation_report.json"]
    if not copied_validation_report.is_file() or copied_validation_report.read_bytes() != report_bytes:
        raise ValueError("release backend-v1 validation report differs from immutable archive")
    report = json.loads(report_bytes.decode("utf-8"))
    if report.get("result") != "pass" or report.get("checks", {}).get("deterministic_replay", {}).get("result") != "byte-identical":
        raise ValueError("immutable backend-v1 validation report is not admitted")
    if report.get("checks", {}).get("record_count") != 2122:
        raise ValueError("immutable backend-v1 validation report record count is not 2,122")
    return {
        "record_count": 2122,
        "manifest_members": len(declared),
        "pinned_identities": EXPECTED_V1_PACKAGE_PINS,
        "archive_bytes": path.stat().st_size,
        "archive_sha256": sha256_file(path),
        "entries": len(members),
        "privacy_scan": "pass",
        "result": "pass",
    }


def verify_v2_receipt(
    receipt_path: Path,
    package: Path,
    root: Path,
) -> dict:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("result") != "pass" or receipt.get("credentials_recorded") is not False:
        raise ValueError("backend-v2 validation receipt is not an admitted credential-free pass")

    canonical = receipt.get("canonical_package", {})
    manifest_path = package / "manifest.json"
    records_jsonl_path = package / "records.jsonl"
    records_csv_path = package / "records.csv"
    federation_path = package / "federation.json"
    expected_package_facts = {
        "path": package.relative_to(root).as_posix(),
        "file_count": 20,
        "total_bytes": sum(
            path.stat().st_size
            for path in package.rglob("*")
            if path.is_file() and path.name != "validation_report.json"
        ),
        "record_count": EXPECTED_V2_RECORD_COUNT,
        "table_counts": EXPECTED_V2_COUNTS,
        "records_jsonl": {
            "bytes": records_jsonl_path.stat().st_size,
            "sha256": sha256_file(records_jsonl_path),
        },
        "records_csv": {
            "bytes": records_csv_path.stat().st_size,
            "sha256": sha256_file(records_csv_path),
        },
        "federation_json": {
            "bytes": federation_path.stat().st_size,
            "sha256": sha256_file(federation_path),
        },
        "manifest_json": {
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
        },
    }
    for key, expected in expected_package_facts.items():
        if canonical.get(key) != expected:
            raise ValueError(f"backend-v2 validation receipt canonical-package mismatch: {key}")

    expected_implementation = {
        "builder": "scripts/build-backend-v2-federation.py",
        "validator": "scripts/validate-backend-v2-federation.py",
        "receipt_builder": "scripts/build-backend-v2-validation-receipt.py",
    }
    implementation = receipt.get("implementation", {})
    for role, relative in expected_implementation.items():
        source = root / relative
        fact = implementation.get(role, {})
        if (
            fact.get("path") != relative
            or fact.get("bytes") != source.stat().st_size
            or fact.get("sha256") != sha256_file(source)
        ):
            raise ValueError(f"backend-v2 validation receipt implementation mismatch: {role}")

    negative_suite = receipt.get("negative_fixture_suite", {})
    if negative_suite != {
        "command": "python -B -m unittest discover -s tests/backend-v2 -p test_*.py -v",
        "tests_run": 23,
        "tests_passed": 23,
        "tests_failed": 0,
        "result": "pass",
    }:
        raise ValueError("backend-v2 validation receipt negative-fixture suite is stale")

    d20_path = root / "backend" / "migrations" / "erdman-functional-analysis-id-v1" / "MIGRATION_RECEIPT.json"
    d20_receipt = json.loads(d20_path.read_text(encoding="utf-8"))
    d20_admission = receipt.get("d20_admission", {})
    if (
        d20_admission.get("receipt_path")
        != "backend/migrations/erdman-functional-analysis-id-v1/MIGRATION_RECEIPT.json"
        or d20_admission.get("receipt_bytes") != d20_path.stat().st_size
        or d20_admission.get("receipt_sha256") != sha256_file(d20_path)
        or d20_admission.get("native_records") != 32383
        or d20_admission.get("auxiliary_index_rows") != 2104
        or d20_admission.get("target_records") != 41689
        or d20_admission.get("html_reader_url")
        != "https://kokunoyumeto.github.io/functional-analysis-erdman-id/"
        or d20_admission.get("html_reader_public_readback_sha256")
        != d20_receipt["source"]["public_evidence"]["html_reader"]["readback"]["sha256"]
    ):
        raise ValueError("backend-v2 validation receipt D20 admission is stale")

    schemas = {row.get("path"): row for row in receipt.get("schemas", [])}
    expected_schema_paths = {
        relative for relative in V2_RELEASE_FILES if relative.startswith("schemas/v2/")
    }
    if set(schemas) != expected_schema_paths:
        raise ValueError("backend-v2 validation receipt schema identity set mismatch")
    for relative in sorted(expected_schema_paths):
        source = root / relative
        fact = schemas[relative]
        if fact.get("bytes") != source.stat().st_size or fact.get("sha256") != sha256_file(source):
            raise ValueError(f"backend-v2 validation receipt schema mismatch: {relative}")
    return {
        "record_count": canonical["record_count"],
        "table_counts": canonical["table_counts"],
        "implementation_bindings": len(expected_implementation),
        "schema_bindings": len(expected_schema_paths),
        "result": "pass",
    }


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
    parser.add_argument("--coordinator-logbook-root", required=True, type=Path)
    parser.add_argument("--output-report", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    backend_v2 = args.backend_v2_package.resolve()
    backend_v2_validation_receipt = args.backend_v2_validation_receipt.resolve()
    coordinator_logbook_root = args.coordinator_logbook_root.resolve()
    version = args.version

    if (
        not release.is_relative_to(root)
        or not backend.is_relative_to(root)
        or not backend_v2.is_relative_to(root)
    ):
        raise ValueError("release and backend packages must remain inside the project root")
    if not coordinator_logbook_root.is_dir():
        raise ValueError("coordinator logbook root must be an existing directory")
    if not backend_v2_validation_receipt.is_file():
        raise ValueError("backend-v2 validation receipt input does not exist")
    output_report = args.output_report.resolve()
    if output_report.parent != release:
        raise ValueError("local validation report must be written directly inside the release directory")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ValueError("source commit must be a full lowercase Git SHA-1")
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if current_head != args.source_commit:
        raise ValueError("source commit does not equal the currently validated repository HEAD")

    static = subprocess.run(
        ["node", str(root / "scripts" / "validate-static-site.mjs")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    static_result = json.loads(static.stdout)

    learner_projection = subprocess.run(
        ["node", str(root / "scripts" / "validate-learner-read-model.mjs")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    learner_projection_result = json.loads(learner_projection.stdout)
    if (
        learner_projection_result.get("status") != "pass"
        or learner_projection_result.get("course_count") != 40
        or learner_projection_result.get("published_course_count") != 17
        or learner_projection_result.get("public_readback_overlay_count") != 3
        or learner_projection_result.get("deterministic_replay") != "byte-identical"
    ):
        raise ValueError("learner read-model validation or deterministic replay failed")

    backend_v2_tests = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests/backend-v2",
            "-p",
            "test_*.py",
            "-v",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    backend_v2_test_output = backend_v2_tests.stdout + backend_v2_tests.stderr
    if not re.search(r"Ran 23 tests? in ", backend_v2_test_output) or "OK" not in backend_v2_test_output:
        raise ValueError("backend-v2 executable test suite did not prove exactly 23 passing tests")

    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    receipt_directories = {path.parent.name for path in migration_receipts}
    if receipt_directories != set(MIGRATION_RECEIPT_FILENAMES):
        raise ValueError("complete-corpus migration receipt directory identity set mismatch")
    migrations = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts" / "validate-migration-receipt-v1.py"),
            "--schema",
            str(root / "schemas" / "backend-migration-receipt-v1.schema.json"),
            *[str(path) for path in migration_receipts],
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    migration_result = json.loads(migrations.stdout)

    receipt_documents = {}
    for path in migration_receipts:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        migration_id = receipt["migration_id"]
        if migration_id in receipt_documents:
            raise ValueError(f"duplicate migration ID: {migration_id}")
        receipt_documents[migration_id] = receipt
        receipt_filename = MIGRATION_RECEIPT_FILENAMES[path.parent.name]
        copied_receipt = release / receipt_filename
        if not copied_receipt.is_file() or copied_receipt.read_bytes() != path.read_bytes():
            raise ValueError(f"release migration receipt is absent or changed: {receipt_filename}")
    if set(receipt_documents) != set(EXPECTED_MIGRATIONS):
        raise ValueError("complete-corpus migration receipt identity set mismatch")
    migration_target_records = sum(receipt["target"]["record_count"] for receipt in receipt_documents.values())
    if len(receipt_documents) != 13 or migration_target_records != 926171:
        raise ValueError("complete-corpus migration proof boundary must contain thirteen receipts and 926,171 target records")

    catalog_path = release / f"program-matematika-indonesia-catalog-v{version}.json"
    catalog_schema_path = release / "program-matematika-indonesia-catalog-v1.schema.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_schema = json.loads(catalog_schema_path.read_text(encoding="utf-8"))
    expected_schema_uri = f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-catalog-v1.schema.json"
    if catalog.get("$schema") != expected_schema_uri or catalog_schema.get("$id") != expected_schema_uri:
        raise ValueError("catalog schema reference and schema identity are not bound to this release")
    if catalog_schema_path.read_bytes() != (root / "schemas" / "catalog-v1.schema.json").read_bytes():
        raise ValueError("release catalog schema is not byte-identical to the validated root schema")
    Draft202012Validator(catalog_schema, format_checker=FormatChecker()).validate(catalog)
    authority_path = root / "backend" / "authority" / "curriculum-authority-v1.json"
    authority_schema_path = root / "schemas" / "v1" / "curriculum-authority-v1.schema.json"
    read_model_path = root / "docs" / "data" / "learner-read-model.json"
    read_model_schema_path = root / "schemas" / "v1" / "learner-read-model-v1.schema.json"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority_schema = json.loads(authority_schema_path.read_text(encoding="utf-8"))
    read_model = json.loads(read_model_path.read_text(encoding="utf-8"))
    read_model_schema = json.loads(read_model_schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(authority_schema, format_checker=FormatChecker()).validate(authority)
    Draft202012Validator(read_model_schema, format_checker=FormatChecker()).validate(read_model)
    phase_two_release_copies = {
        "curriculum-authority-v1.json": authority_path,
        "learner-read-model-v1.json": read_model_path,
        "curriculum-authority-v1.schema.json": authority_schema_path,
        "learner-read-model-v1.schema.json": read_model_schema_path,
        "federation-unit-package-v2.1.schema.json": root / "backend" / "v2.1" / "schema" / "federation-unit-package-v2.1.schema.json",
        "federation-unit-record-v2.1.schema.json": root / "backend" / "v2.1" / "schema" / "federation-unit-record-v2.1.schema.json",
    }
    for release_name, source in phase_two_release_copies.items():
        copied = release / release_name
        if not copied.is_file() or copied.read_bytes() != source.read_bytes():
            raise ValueError(f"phase-two release artifact is absent or changed: {release_name}")
    if (root / "docs" / "data" / "curriculum-authority-v1.json").read_bytes() != authority_path.read_bytes():
        raise ValueError("public curriculum authority is not byte-identical to canonical authority")
    if read_model.get("program") != catalog.get("program"):
        raise ValueError("learner read-model program metadata differs from release catalog")
    if catalog.get("sourceCommit") != args.source_commit:
        raise ValueError("catalog sourceCommit does not equal the validated repository commit")
    if catalog["program"]["zenodo"] != f"https://doi.org/10.5281/zenodo.{args.record_id}":
        raise ValueError("catalog Zenodo DOI does not match reserved record")
    if catalog["counts"]["courseRoles"] != 40 or catalog["counts"]["unresolvedRoles"] != 0:
        raise ValueError("catalog course/source closure mismatch")
    expected_completed_role_ids = [
        "A00", "B10", "B40", "B80", "B90", "C10", "C30", "C40", "C60", "C70", "C80", "C100", "C110", "C120", "C130", "D20", "D110"
    ]
    expected_completed_record_dois = [
        "10.5281/zenodo.22070683",
        "10.5281/zenodo.22060439",
        "10.5281/zenodo.22070458",
        "10.5281/zenodo.22053905",
        "10.5281/zenodo.22062144",
        "10.5281/zenodo.22082567",
        "10.5281/zenodo.22062449",
        "10.5281/zenodo.22052196",
        "10.5281/zenodo.22062005",
        "10.5281/zenodo.21932787",
        "10.5281/zenodo.22054086",
        "10.5281/zenodo.22070943",
        "10.5281/zenodo.22070653",
        "10.5281/zenodo.22088947",
        "10.5281/zenodo.22062017",
        "10.5281/zenodo.22102628",
    ]
    if catalog["counts"].get("completedPublicCourseRoles") != 17:
        raise ValueError("catalog completed-public course-role count is not 17")
    if catalog["counts"].get("completedPublicRecords") != 16:
        raise ValueError("catalog completed-public record count is not 16")
    if catalog["program"].get("completedPublicCourseRoleIds") != expected_completed_role_ids:
        raise ValueError("catalog completed-public course-role identities are not the current canonical set")
    if catalog["program"].get("completedPublicRecordDois") != expected_completed_record_dois:
        raise ValueError("catalog completed-public DOI identities are not the current canonical set")
    published_role_ids = [course["id"] for course in catalog["courses"] if course["state"] == "published"]
    if published_role_ids != expected_completed_role_ids:
        raise ValueError("catalog published course states do not match completed-public role identities")
    courses_by_id = {course["id"]: course for course in catalog["courses"]}
    expected_lebl_repository = "https://github.com/KokunoYumeto/lebl-mathematics-family-id"
    expected_b40_repository = "https://github.com/KokunoYumeto/hefferon-linear-algebra-id"
    expected_lebl_edition = "https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.24.u336"
    a30_note = courses_by_id["A30"].get("note", "")
    if (
        courses_by_id["A30"].get("state") != "production"
        or not all(token in a30_note for token in ("HP-A30-001", "m49369", "m49371", "m49372", "m49374", "m49384", "owner-QA", "belum terintegrasi atau diterbitkan"))
    ):
        raise ValueError("A30 does not preserve the manager-clean, non-integrated HP-A30-001 boundary")
    b30_note = courses_by_id["B30"].get("note", "")
    if (
        courses_by_id["B30"].get("state") != "production"
        or courses_by_id["B30"].get("zenodo") != "https://doi.org/10.5281/zenodo.22077325"
        or courses_by_id["B30"].get("edition") != "https://zenodo.org/records/22077325/files/CLP-2_Kalkulus_Integral_Bahasa_Indonesia_checkpoint_2026-08-24_s2.1.pdf?download=1"
        or not all(token in b30_note for token in ("WIP.9/CP0047-R1", "674 halaman", "863e9c5709ff961b3ba09f93da973a8188849d81a4e9680900e1d66a58232bd6", "105.047", "HP-CLP2-001/002", "belum lengkap"))
    ):
        raise ValueError("B30 does not preserve the exact verified CLP WIP.9 boundary")
    if (
        courses_by_id["C10"].get("zenodo") != "https://doi.org/10.5281/zenodo.22082567"
        or courses_by_id["C10"].get("edition") != expected_lebl_edition
        or courses_by_id["C10"].get("repository") != expected_lebl_repository
        or "334 halaman" not in courses_by_id["C10"].get("note", "")
        or "336 unit" not in courses_by_id["C10"].get("note", "")
    ):
        raise ValueError("C10 does not point to the exact verified Lebl U336 edition")
    if (
        courses_by_id["B40"].get("state") != "published"
        or courses_by_id["B40"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070458"
        or courses_by_id["B40"].get("repository") != expected_b40_repository
    ):
        raise ValueError("B40 does not point to the exact verified Hefferon edition")
    if (
        courses_by_id["A00"].get("state") != "published"
        or courses_by_id["A00"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070683"
        or courses_by_id["A00"].get("repository") != "https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID"
    ):
        raise ValueError("A00 does not point to the exact verified Prealgebra 2e v0.2.7 edition")
    if (
        courses_by_id["C120"].get("state") != "published"
        or courses_by_id["C120"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070943"
        or courses_by_id["C120"].get("repository") != "https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id"
    ):
        raise ValueError("C120 does not point to the exact verified modeling edition")
    if (
        courses_by_id["C130"].get("state") != "published"
        or courses_by_id["C130"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070653"
        or courses_by_id["C130"].get("repository") != "https://github.com/KokunoYumeto/open-optimization-or-book-id"
    ):
        raise ValueError("C130 does not point to the exact verified operations-research edition")
    if (
        courses_by_id["C20"].get("state") != "production"
        or courses_by_id["C20"].get("zenodo") != "https://doi.org/10.5281/zenodo.22082567"
        or courses_by_id["C20"].get("edition") != expected_lebl_edition
        or courses_by_id["C20"].get("repository") != expected_lebl_repository
        or "198 halaman" not in courses_by_id["C20"].get("note", "")
        or "semua 11 latihan" not in courses_by_id["C20"].get("note", "")
        or "78543d4e8087e68589e8f15d0a3a969b3282247c7c9c2cdcb6f658dfa4b68e4f" not in courses_by_id["C20"].get("note", "")
    ):
        raise ValueError("C20 is not preserved as the exact production-state U336 WIP")
    for role_id, expected_units in (("B70", "15 unit"), ("C50", "50 unit")):
        course = courses_by_id[role_id]
        if (
            course.get("state") != "production"
            or course.get("edition") != expected_lebl_edition
            or course.get("zenodo") != "https://doi.org/10.5281/zenodo.22082567"
            or course.get("repository") != expected_lebl_repository
            or expected_units not in course.get("note", "")
            or "belum lengkap" not in course.get("note", "")
        ):
            raise ValueError(f"{role_id} does not preserve its exact partial U336 evidence")
    c100 = courses_by_id["C100"]
    if (
        c100.get("state") != "published"
        or c100.get("zenodo") != "https://doi.org/10.5281/zenodo.22102628"
        or c100.get("edition") != "https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_SPINE_COMPLETE.pdf?download=1"
        or not all(token in c100.get("corpus", "") for token in ("Bidang Euklides", "kursus utama", "Bahasa Indonesia", "lengkap"))
        or not all(token in c100.get("note", "") for token in ("253 solusi", "enam unit", "empat pemeriksaan", "dua capstone", "HTML semantik", "EPUB", "Clemens/Snapp", "lini terpisah"))
    ):
        raise ValueError("C100 does not preserve the verified rights-clean complete main course and separately licensed workbook boundary")
    if (
        courses_by_id["C140"].get("state") != "production"
        or courses_by_id["C140"].get("zenodo") != "https://doi.org/10.5281/zenodo.22071140"
        or courses_by_id["C140"].get("repository") != "https://github.com/KokunoYumeto/mathematical-statistics-id"
        or courses_by_id["C140"].get("edition") != "https://zenodo.org/records/22071140/files/00_statistika-matematis-id-reader-2026.08.23.16.pdf?download=1"
    ):
        raise ValueError("C140 does not preserve the verified incomplete Random checkpoint 16")
    if (
        courses_by_id["D20"].get("state") != "published"
        or courses_by_id["D20"].get("zenodo") != "https://doi.org/10.5281/zenodo.22088947"
        or courses_by_id["D20"].get("repository") != "https://github.com/KokunoYumeto/functional-analysis-erdman-id"
        or courses_by_id["D20"].get("reader") != "https://kokunoyumeto.github.io/functional-analysis-erdman-id/"
        or courses_by_id["D20"].get("edition") != "https://zenodo.org/records/22088947/files/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf?download=1"
        or not all(token in courses_by_id["D20"].get("note", "") for token in ("298 halaman", "17 bab", "52 solusi", "10 solusi", "13 unit"))
    ):
        raise ValueError("D20 does not preserve the verified complete Erdman edition and public HTML reader")
    if (
        courses_by_id["D30"].get("state") != "production"
        or courses_by_id["D30"].get("zenodo") != "https://doi.org/10.5281/zenodo.22074332"
        or courses_by_id["D30"].get("edition") != "https://zenodo.org/api/records/22074332/files/00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_20.pdf/content"
        or courses_by_id["D30"].get("repository") != "https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id"
        or "223 halaman" not in courses_by_id["D30"].get("note", "")
    ):
        raise ValueError("D30 does not preserve the verified incomplete checkpoint-20 boundary")
    if (
        courses_by_id["D40"].get("state") != "production"
        or courses_by_id["D40"].get("zenodo") != "https://doi.org/10.5281/zenodo.22086227"
        or courses_by_id["D40"].get("edition") != "https://zenodo.org/records/22086227/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_09.pdf?download=1"
        or "8 simpul FEniCSx (7 wajib + 1 pengayaan)" not in courses_by_id["D40"].get("corpus", "")
        or not all(token in courses_by_id["D40"].get("note", "") for token in ("Unit 09", "77 halaman", "4.414.297 byte", "f2869bc0c38153d2223a03e8dccc85c306cefdc4eea15f9fe6a560a6d1f7ce91", "klasifikasi selesai"))
    ):
        raise ValueError("D40 does not preserve the verified Unit-09 boundary and eight-node FEniCSx architecture")
    if (
        courses_by_id["D50"].get("state") != "production"
        or courses_by_id["D50"].get("zenodo") != "https://doi.org/10.5281/zenodo.22073928"
        or courses_by_id["D50"].get("edition") != "https://zenodo.org/api/records/22073928/files/geometri-diferensial-manifold-mulus-hingga-unit-10-id.pdf/content"
        or "165 halaman" not in courses_by_id["D50"].get("note", "")
        or "Unit 11–13" not in courses_by_id["D50"].get("note", "")
        or "belum diterbitkan" not in courses_by_id["D50"].get("note", "")
    ):
        raise ValueError("D50 does not preserve the verified incomplete Unit-10 boundary")
    if (
        courses_by_id["D60"].get("state") != "production"
        or courses_by_id["D60"].get("zenodo") != "https://doi.org/10.5281/zenodo.22084021"
        or courses_by_id["D60"].get("edition") != "https://zenodo.org/api/records/22084021/files/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_READER.pdf/content"
        or courses_by_id["D60"].get("repository") != "https://github.com/KokunoYumeto/algebraic-topology-id"
        or not all(token in courses_by_id["D60"].get("note", "") for token in ("Roberts Kuliah 1–30 lengkap", "Fomberg §§1.1–1.2", "362 halaman", "2.322.978 byte", "fb81f2b2c0f73c17c4e3be4eaae164eaeaeb0c4ff0661580acfc7aa9b6d5f749", "masih diproduksi"))
    ):
        raise ValueError("D60 does not preserve the verified Roberts-30 plus Fomberg-1.1-1.2 boundary")
    d70_corpus = courses_by_id["D70"].get("corpus", "")
    d70_note = courses_by_id["D70"].get("note", "")
    if (
        courses_by_id["D70"].get("state") != "production"
        or not all(token in d70_corpus for token in ("Wen-Wei Li", "Alexander Duncan", "CC BY 4.0", "CRing/GFDL", "penghubung dan solusi asli"))
        or "Etingof/MIT tetap referensi saja" not in d70_note
        or "lembar tugas eksternal dikecualikan" not in d70_note
    ):
        raise ValueError("D70 does not preserve the selected Li-Duncan-CRing architecture")
    d90_corpus = courses_by_id["D90"].get("corpus", "")
    d90_note = courses_by_id["D90"].get("note", "")
    if (
        courses_by_id["D90"].get("state") != "production"
        or courses_by_id["D90"].get("zenodo") != "https://doi.org/10.5281/zenodo.22077419"
        or courses_by_id["D90"].get("edition") != "https://zenodo.org/records/22077419/files/D90-MIT-10-kuliah-6-irisan-tertutup-dan-hiperbidang-id.pdf?download=1"
        or courses_by_id["D90"].get("repository") != "https://github.com/KokunoYumeto/advanced-optimization-convex-analysis-id"
        or not all(token in d90_corpus for token in ("Habring arXiv 2607.11664v1", "CC BY 4.0", "Becker", "MIT", "KKT", "stokastik", "variasional", "solusi asli"))
        or not all(token in d90_note for token in ("MIT 6.253 dan Royer", "pendamping", "bukan spine kanonik", "MIT L10", "10 halaman", "3b01d57e8e8a7d7887f36cfdc205d1b68d1d007a152bd8e0cd75479628e1abc0", "L11 masih lokal"))
    ):
        raise ValueError("D90 does not preserve the Habring-Becker spine and exact public MIT-L10 companion boundary")
    if (
        courses_by_id["D100"].get("state") != "production"
        or courses_by_id["D100"].get("zenodo") != "https://doi.org/10.5281/zenodo.22077441"
        or courses_by_id["D100"].get("edition") != "https://zenodo.org/records/22077441/files/kurva-aljabar-id-unit-15.pdf?download=1"
        or courses_by_id["D100"].get("repository") != "https://github.com/KokunoYumeto/algebraic-geometry-bridge-id"
        or not all(token in courses_by_id["D100"].get("note", "") for token in ("Unit 1–15", "267 halaman", "6.502.255 byte", "e56aae414a9d7e252485d06e7da790fae9bf972514c8fe47fc31d26eddd3699c", "Unit 16–18", "bukan rilis publik", "Unit 19", "belum didispatch"))
    ):
        raise ValueError("D100 does not preserve the public Unit-15, local Unit-16-18, and frozen-not-dispatched Unit-19 distinction")

    expected_catalog_migrations = []
    for migration_id, metadata in EXPECTED_MIGRATIONS.items():
        expected_catalog_migrations.append(
            {
                "corpus": metadata["corpus"],
                "recordCount": receipt_documents[migration_id]["target"]["record_count"],
                "result": metadata["result"],
            }
        )
    actual_catalog_migrations = catalog["program"]["backend"]["completeCorpusMigrations"]
    if sorted(actual_catalog_migrations, key=lambda row: row["corpus"]) != sorted(expected_catalog_migrations, key=lambda row: row["corpus"]):
        raise ValueError("catalog migration claims do not match the validated receipt identities and counts")

    expected_federation_v2 = {
        "version": EXPECTED_FEDERATION_VERSION,
        "status": "validated",
        "recordCount": EXPECTED_V2_RECORD_COUNT,
        "datasetCount": 34,
        "courseCount": 40,
        "learnerSurfaceCount": EXPECTED_V2_COUNTS["reader_surfaces"],
        "webRouteCount": 41,
        "identityCrosswalkCount": 2122,
        "package": f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-backend-v2-v{version}.zip?download=1",
        "packageSchema": f"https://zenodo.org/records/{args.record_id}/files/federation-package-v2.schema.json?download=1",
        "recordSchema": f"https://zenodo.org/records/{args.record_id}/files/federation-record-v2.schema.json?download=1",
        "validationReceipt": f"https://zenodo.org/records/{args.record_id}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json?download=1",
    }
    if catalog["program"]["backend"].get("federationV2") != expected_federation_v2:
        raise ValueError("catalog federation-v2 claim does not match the exact validated release boundary")
    expected_federation_v21 = {
        "version": "2.1.0",
        "status": "pilot_validated",
        "pilot_courses": ["A00", "B10", "C100", "D20"],
        "pilot_units": 1194,
        "pilot_relations": 2165,
        "route_wrapper_course": "D20",
        "route_wrapper_courses": ["C100", "D20"],
        "educational_access_planning": {
            "schema_id": "interlanguage/global-backend-v2.1-educational-access-planning/0.1.0",
            "dataset_id": "planning:educational-access:v2.1:0.1.0",
            "status": "validated",
            "curriculum_unit_count": 29,
            "portfolio_count": 13,
            "portfolio_relation_count": 10,
            "adaptation_depth_count": 5,
            "accessibility_derivative_count": 8,
            "compute_assumption_count": 12,
            "compute_scenario_count": 3,
        },
        "packageSchema": f"https://zenodo.org/records/{args.record_id}/files/federation-unit-package-v2.1.schema.json?download=1",
        "recordSchema": f"https://zenodo.org/records/{args.record_id}/files/federation-unit-record-v2.1.schema.json?download=1",
        "package": f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip?download=1",
    }
    if catalog["program"]["backend"].get("federationV21") != expected_federation_v21:
        raise ValueError("catalog federation-v2.1 claim does not match the exact validated pilot boundary")
    expected_educational_access_research = {
        "version": "0.1.0",
        "status": "frozen_validated",
        "record_count": 490,
        "materialized_table_count": 10,
        "declared_unmaterialized_table_count": 7,
        "publicCatalog": "https://kokunoyumeto.github.io/program-matematika-indonesia/data/educational-access.json",
        "schema": "https://kokunoyumeto.github.io/program-matematika-indonesia/schema/educational-access-federation-v1.schema.json",
        "sourcePackage": f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-source-v{version}.zip?download=1",
    }
    if catalog["program"]["backend"].get("educationalAccessResearch") != expected_educational_access_research:
        raise ValueError("catalog educational-access research federation claim is not the frozen 490-record boundary")
    expected_learner_read_model = {
        "version": "1.0.0",
        "status": "validated",
        "courseCount": 40,
        "prerequisiteEdgeCount": 82,
        "authority": f"https://zenodo.org/records/{args.record_id}/files/curriculum-authority-v1.json?download=1",
        "authoritySchema": f"https://zenodo.org/records/{args.record_id}/files/curriculum-authority-v1.schema.json?download=1",
        "readModel": f"https://zenodo.org/records/{args.record_id}/files/learner-read-model-v1.json?download=1",
        "readModelSchema": f"https://zenodo.org/records/{args.record_id}/files/learner-read-model-v1.schema.json?download=1",
        "validationReceipt": f"https://zenodo.org/records/{args.record_id}/files/LOCAL_RELEASE_VALIDATION_v{version}.json?download=1",
        "publicEndpoint": "https://kokunoyumeto.github.io/program-matematika-indonesia/data/learner-read-model.json",
    }
    if catalog["program"]["backend"].get("learnerReadModelV1") != expected_learner_read_model:
        raise ValueError("catalog learner-read-model claim does not match the exact validated release boundary")
    if read_model.get("summary", {}).get("published_course_count") != 17:
        raise ValueError("learner read-model published-course count is not 17")
    if read_model.get("summary", {}).get("readback_overlay_count") != 3:
        raise ValueError("learner read-model readback overlay count is not 3")

    if catalog["program"]["backend"]["centralRecordCount"] != 2122:
        raise ValueError("central backend record count must remain exactly 2,122")
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    v1_immutable_result = verify_v1_immutable_archive(
        backend_zip,
        release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
    )

    copied_v2_receipt = release / f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json"
    if (
        not copied_v2_receipt.is_file()
        or copied_v2_receipt.read_bytes() != backend_v2_validation_receipt.read_bytes()
    ):
        raise ValueError("release backend-v2 validation receipt is absent or changed")
    for source_name, release_name in V2_RELEASE_FILES.items():
        source = root / source_name
        copied = release / release_name
        if not copied.is_file() or copied.read_bytes() != source.read_bytes():
            raise ValueError(f"release backend-v2 support file is absent or changed: {release_name}")
    v2_receipt_result = verify_v2_receipt(backend_v2_validation_receipt, backend_v2, root)

    with tempfile.TemporaryDirectory(prefix="pmi-backend-v2-replay-") as temporary:
        replay_package = Path(temporary) / EXPECTED_FEDERATION_DATASET_VERSION
        replay_coordinator_root = Path(temporary) / "coordinator"
        replay_coordinator_root.mkdir(parents=True, exist_ok=True)
        federation_document = json.loads((backend_v2 / "federation.json").read_text(encoding="utf-8"))
        recorded_command = federation_document.get("build", {}).get("command")
        expected_prefix = ["python", "-B", "scripts/build-backend-v2-federation.py"]
        if not isinstance(recorded_command, list) or recorded_command[:3] != expected_prefix:
            raise ValueError("backend-v2 does not record the expected portable replay command")
        if recorded_command.count("<PROGRAM_REPOSITORY_ROOT>") != 1 or recorded_command.count("<COORDINATOR_LOGBOOK_ROOT>") != 1 or recorded_command.count("<OUTPUT>") != 1:
            raise ValueError("backend-v2 replay command placeholders are missing or duplicated")
        replay_command = [
            str(root / "scripts" / "build-backend-v2-federation.py") if value == expected_prefix[2]
            else str(root) if value == "<PROGRAM_REPOSITORY_ROOT>"
            else str(replay_coordinator_root) if value == "<COORDINATOR_LOGBOOK_ROOT>"
            else str(replay_package) if value == "<OUTPUT>"
            else value
            for value in recorded_command
        ]
        # The v0.3.0 receipt was recorded with a redundant
        # ``curriculum_logbook/`` prefix on coordinator-relative inputs. Keep
        # those immutable locator strings in the replay metadata, while
        # staging the three exact files under a temporary root where the
        # recorded paths resolve.
        coordinator_relative_flags = {
            "--site-readback-relative",
            "--contract-relative",
            "--role-map-relative",
        }
        for index, value in enumerate(recorded_command[:-1]):
            if value not in coordinator_relative_flags:
                continue
            candidate = recorded_command[index + 1]
            source_relative = candidate.removeprefix("curriculum_logbook/")
            source = coordinator_logbook_root / source_relative
            target = replay_coordinator_root / candidate
            if not source.is_file():
                raise ValueError(f"recorded coordinator replay input is missing: {source}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        replay_command[0] = sys.executable
        replay_build = subprocess.run(
            replay_command,
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        replay_build_result = json.loads(replay_build.stdout)
        v2_validation = subprocess.run(
            [
                sys.executable,
                "-B",
                str(root / "scripts" / "validate-backend-v2-federation.py"),
                "--package",
                str(backend_v2),
                "--schema",
                str(root / "schemas" / "v2" / "federation-package-v2.schema.json"),
                "--record-schema",
                str(root / "schemas" / "v2" / "federation-record-v2.schema.json"),
                "--program-repository-root",
                str(root),
                "--coordinator-logbook-root",
                str(replay_coordinator_root),
                "--replay-package",
                str(replay_package),
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        v2_validation_result = json.loads(v2_validation.stdout)
    if replay_build_result.get("record_count") != EXPECTED_V2_RECORD_COUNT:
        raise ValueError(f"fresh backend-v2 replay did not build exactly {EXPECTED_V2_RECORD_COUNT:,} records")
    v2_checks = v2_validation_result.get("checks", {})
    if (
        v2_validation_result.get("result") != "pass"
        or v2_checks.get("record_count") != EXPECTED_V2_RECORD_COUNT
        or v2_checks.get("table_counts") != EXPECTED_V2_COUNTS
        or v2_checks.get("deterministic_replay")
        != {"result": "byte-identical", "file_count": 20}
    ):
        raise ValueError("backend-v2 independent validation or fresh deterministic replay failed")

    html_path = release / f"program-matematika-indonesia-v{version}.html"
    html = html_path.read_text(encoding="utf-8")
    learner_html_path = release / f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html"
    if learner_html_path.read_bytes() != html_path.read_bytes():
        raise ValueError("human-first standalone HTML is not byte-identical to the validated compatibility filename")
    learner_pdf_path = release / f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf"
    learner_pdf = learner_pdf_path.read_bytes()
    if not learner_pdf.startswith(b"%PDF-") or not learner_pdf.rstrip().endswith(b"%%EOF"):
        raise ValueError("human-first PDF is not a structurally recognizable PDF")
    if b"https://kokunoyumeto.github.io/program-matematika-indonesia/" not in learner_pdf:
        raise ValueError("human-first PDF does not contain the clickable learner-site URI")
    for required in (
        f"10.5281/zenodo.{args.record_id}",
        f"v{version}",
        "40 korpus terpilih",
        "Produksi yang belum selesai tetap dilabeli dengan jelas",
        "Mulai belajar — buka 40 mata kuliah",
    ):
        if required not in html:
            raise ValueError(f"standalone HTML missing {required!r}")

    og_path = release / f"program-matematika-indonesia-og-v{version}.png"
    if not og_path.is_file() or og_path.read_bytes() != (root / "docs" / "og.png").read_bytes():
        raise ValueError("release social-preview image is absent or differs from the validated site image")

    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    backend_v2_zip = release / f"program-matematika-indonesia-backend-v2-v{version}.zip"
    backend_v21_zip = release / f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip"
    generated_catalog_source_path = (
        f"releases/v{version}/program-matematika-indonesia-catalog-v{version}.json"
    )
    zip_results = {
        "source": verify_source_zip(
            source_zip,
            root,
            args.source_commit,
            {generated_catalog_source_path},
        ),
        "backend_v1": v1_immutable_result,
        "backend_v2": verify_backend_zip(
            backend_v2_zip,
            backend_v2,
            "program-matematika-indonesia-backend-v2/",
        ),
        "backend_v21": verify_backend_zip(
            backend_v21_zip,
            root / "backend" / "v2.1",
            "program-matematika-indonesia-backend-v2.1/",
        ),
    }
    if zip_results["source"]["source_commit"] != args.source_commit:
        raise ValueError("source ZIP manifest is not bound to the validated repository commit")
    v21_replay_receipt_name = f"GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v{version}.json"
    v21_replay_result = verify_v21_deterministic_receipt(
        release / v21_replay_receipt_name,
        root,
        version,
        args.source_commit,
    )

    receipt_release_names = set(MIGRATION_RECEIPT_FILENAMES.values())
    expected_release_names = {
        "BACKEND_CONVERGENCE_V1.md",
        "MIGRATION_HANDOFF_V1.md",
        f"RELEASE_NOTES_v{version}.md",
        "interlanguage-backend-migration-receipt-v1.schema.json",
        "backend-migration-receipt-v2.schema.json",
        "build-backend-v2-federation.py",
        "build-backend-v2-validation-receipt.py",
        "federation-package-v2.schema.json",
        "federation-record-v2.schema.json",
        "interlanguage-math-backend-v1.schema.json",
        "interlanguage-source-format-profile-v1.schema.json",
        "namespace-v2.json",
        "pmi-release-policy-v2.json",
        "program-matematika-indonesia-catalog-v1.schema.json",
        "curriculum-authority-v1.json",
        "curriculum-authority-v1.schema.json",
        "learner-read-model-v1.json",
        "learner-read-model-v1.schema.json",
        f"program-matematika-indonesia-catalog-v{version}.json",
        f"program-matematika-indonesia-og-v{version}.png",
        f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf",
        f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html",
        f"program-matematika-indonesia-v{version}.html",
        f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
        f"program-matematika-indonesia-backend-v1-v{version}.zip",
        f"program-matematika-indonesia-backend-v2-v{version}.zip",
        f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip",
        "federation-unit-package-v2.1.schema.json",
        "federation-unit-record-v2.1.schema.json",
        f"program-matematika-indonesia-source-v{version}.zip",
        f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json",
        v21_replay_receipt_name,
        "validate-backend-v2-federation.py",
        *receipt_release_names,
    }
    if len(expected_release_names) != 46:
        raise ValueError(
            f"release tooling expected-name set contains {len(expected_release_names)} payloads; expected 46"
        )
    actual_release_names = {
        path.name
        for path in release.iterdir()
        if path.is_file() and path.name not in {"CHECKSUMS.sha256", output_report.name}
    }
    if actual_release_names != expected_release_names:
        missing = sorted(expected_release_names - actual_release_names)
        extra = sorted(actual_release_names - expected_release_names)
        raise ValueError(f"release inventory mismatch; missing={missing}; extra={extra}")
    expected_learner_first = [
        f"00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.pdf",
        f"01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v{version}.html",
    ]
    if sorted(actual_release_names)[:2] != expected_learner_first:
        raise ValueError("release inventory is not lexically learner-first (00 PDF, then 01 HTML)")

    files = []
    for path in sorted(candidate for candidate in release.iterdir() if candidate.is_file() and candidate.name in expected_release_names):
        assert_public_bytes(f"release:{path.name}", path.read_bytes())
        files.append({"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})

    report = {
        "schema_id": "program-matematika-indonesia/local-release-validation/v2",
        "version": version,
        "reserved_zenodo_record_id": args.record_id,
        "result": "pass",
        "checks": {
            "static_site": static_result,
            "catalog_draft_2020_12": "pass",
            "catalog_course_roles": catalog["counts"]["courseRoles"],
            "catalog_unresolved_roles": catalog["counts"]["unresolvedRoles"],
            "catalog_completed_public_course_roles": catalog["counts"]["completedPublicCourseRoles"],
            "catalog_completed_public_records": catalog["counts"]["completedPublicRecords"],
            "catalog_schema_identity_and_bytes": "pass",
            "curriculum_authority_schema": "pass",
            "learner_read_model_schema": "pass",
            "learner_read_model_projection": learner_projection_result,
            "phase_two_public_artifacts": {
                name: {"bytes": source.stat().st_size, "sha256": sha256_file(source)}
                for name, source in phase_two_release_copies.items()
            },
            "source_commit_binding": args.source_commit,
            "backend": backend_report["checks"],
            "backend_v1_immutable_package": v1_immutable_result,
            "backend_v2_validation_receipt": v2_receipt_result,
            "backend_v21_deterministic_replay_receipt": v21_replay_result,
            "backend_v2_executable_tests": {"tests_run": 23, "tests_passed": 23, "result": "pass"},
            "backend_v2_independent_validation": v2_validation_result,
            "backend_v2_fresh_replay_build": {
                "record_count": replay_build_result["record_count"],
                "record_counts": replay_build_result["record_counts"],
            },
            "complete_corpus_migrations": migration_result,
            "complete_corpus_migration_target_records": migration_target_records,
            "migration_claim_cross_check": "pass",
            "release_inventory": {"files_before_report": len(files), "result": "exact"},
            "privacy_scan": "pass",
            "zip_verification": zip_results,
            "standalone_html": "pass",
            "github_transport": "available_for_bounded_push_after_release_validation",
        },
        "files_before_checksum": files,
    }
    report_bytes = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    assert_public_bytes("local release validation report", report_bytes)
    output_report.write_bytes(report_bytes)
    print(json.dumps({"result": "pass", "report": str(output_report), "sha256": sha256_file(output_report)}, sort_keys=True))


if __name__ == "__main__":
    main()
