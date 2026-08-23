#!/usr/bin/env python3
"""Validate a central release bundle before Zenodo upload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


EXPECTED_MIGRATIONS = {
    "dmoi4-id-0.1.0-to-interlanguage-v1.0.0": {
        "corpus": "Discrete Mathematics: An Open Introduction 4 — Bahasa Indonesia",
        "result": "lossless-zero-copy-pass",
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
}

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


def verify_source_zip(path: Path) -> dict:
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
    return {
        "entries": len(names),
        "manifest_entries": len(declared),
        "source_commit": manifest.get("source_commit"),
        "privacy_scan": "pass",
        "result": "pass",
    }


def verify_backend_zip(path: Path, package: Path) -> dict:
    prefix = "program-matematika-indonesia-backend-v1/"
    expected = {
        prefix + source.relative_to(package).as_posix(): source
        for source in package.rglob("*")
        if source.is_file()
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--record-id", required=True, type=int)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--release-dir", required=True, type=Path)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--output-report", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    version = args.version

    if not release.is_relative_to(root) or not backend.is_relative_to(root):
        raise ValueError("release and backend package must remain inside the project root")
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

    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    if not migration_receipts:
        raise ValueError("no complete-corpus migration receipts found")
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
        slug = path.parent.name.removesuffix("-v1")
        copied_receipt = release / f"{slug}-backend-v1-migration-receipt.json"
        if not copied_receipt.is_file() or copied_receipt.read_bytes() != path.read_bytes():
            raise ValueError(f"release migration receipt is absent or changed: {slug}")
    if set(receipt_documents) != set(EXPECTED_MIGRATIONS):
        raise ValueError("complete-corpus migration receipt identity set mismatch")

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
    if catalog.get("sourceCommit") != args.source_commit:
        raise ValueError("catalog sourceCommit does not equal the validated repository commit")
    if catalog["program"]["zenodo"] != f"https://doi.org/10.5281/zenodo.{args.record_id}":
        raise ValueError("catalog Zenodo DOI does not match reserved record")
    if catalog["counts"]["courseRoles"] != 40 or catalog["counts"]["unresolvedRoles"] != 0:
        raise ValueError("catalog course/source closure mismatch")

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

    backend_report_path = backend / "validation_report.json"
    backend_report = json.loads(backend_report_path.read_text(encoding="utf-8"))
    if backend_report["result"] != "pass" or backend_report["checks"]["deterministic_replay"]["result"] != "byte-identical":
        raise ValueError("backend validation report is not admitted")
    if backend_report["checks"]["record_count"] != catalog["program"]["backend"]["centralRecordCount"]:
        raise ValueError("catalog/backend record count mismatch")

    html_path = release / f"program-matematika-indonesia-v{version}.html"
    html = html_path.read_text(encoding="utf-8")
    for required in (
        f"10.5281/zenodo.{args.record_id}",
        f"v{version}",
        "40 korpus terpilih",
        "Semua peran sumber sudah dibekukan",
    ):
        if required not in html:
            raise ValueError(f"standalone HTML missing {required!r}")

    og_path = release / f"program-matematika-indonesia-og-v{version}.png"
    if not og_path.is_file() or og_path.read_bytes() != (root / "docs" / "og.png").read_bytes():
        raise ValueError("release social-preview image is absent or differs from the validated site image")

    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    zip_results = {
        "source": verify_source_zip(source_zip),
        "backend": verify_backend_zip(backend_zip, backend),
    }
    if zip_results["source"]["source_commit"] != args.source_commit:
        raise ValueError("source ZIP manifest is not bound to the validated repository commit")

    receipt_release_names = {
        f"{path.parent.name.removesuffix('-v1')}-backend-v1-migration-receipt.json"
        for path in migration_receipts
    }
    expected_release_names = {
        "BACKEND_CONVERGENCE_V1.md",
        "MIGRATION_HANDOFF_V1.md",
        f"RELEASE_NOTES_v{version}.md",
        "interlanguage-backend-migration-receipt-v1.schema.json",
        "interlanguage-math-backend-v1.schema.json",
        "interlanguage-source-format-profile-v1.schema.json",
        "program-matematika-indonesia-catalog-v1.schema.json",
        f"program-matematika-indonesia-catalog-v{version}.json",
        f"program-matematika-indonesia-og-v{version}.png",
        f"program-matematika-indonesia-v{version}.html",
        f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
        f"program-matematika-indonesia-backend-v1-v{version}.zip",
        f"program-matematika-indonesia-source-v{version}.zip",
        *receipt_release_names,
    }
    actual_release_names = {
        path.name
        for path in release.iterdir()
        if path.is_file() and path.name not in {"CHECKSUMS.sha256", output_report.name}
    }
    if actual_release_names != expected_release_names:
        missing = sorted(expected_release_names - actual_release_names)
        extra = sorted(actual_release_names - expected_release_names)
        raise ValueError(f"release inventory mismatch; missing={missing}; extra={extra}")

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
            "catalog_course_roles": 40,
            "catalog_unresolved_roles": 0,
            "catalog_schema_identity_and_bytes": "pass",
            "source_commit_binding": args.source_commit,
            "backend": backend_report["checks"],
            "complete_corpus_migrations": migration_result,
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
