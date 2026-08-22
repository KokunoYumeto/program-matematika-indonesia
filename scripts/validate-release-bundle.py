#!/usr/bin/env python3
"""Validate a central release bundle before Zenodo upload."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"source ZIP CRC failure: {bad}")
        names = archive.namelist()
        manifest = json.loads(archive.read("SOURCE_MANIFEST.json"))
        declared = {entry["path"]: entry for entry in manifest["files"]}
        actual = set(names) - {"SOURCE_MANIFEST.json"}
        if set(declared) != actual:
            raise ValueError("source ZIP manifest inventory mismatch")
        for name, entry in declared.items():
            data = archive.read(name)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError(f"source ZIP entry mismatch: {name}")
    return {"entries": len(names), "manifest_entries": len(declared), "result": "pass"}


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
            if archive.read(name) != source.read_bytes():
                raise ValueError(f"backend ZIP entry mismatch: {name}")
    return {"entries": len(expected), "result": "pass"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--record-id", required=True, type=int)
    parser.add_argument("--release-dir", required=True, type=Path)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--output-report", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    version = args.version

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

    catalog_path = release / f"program-matematika-indonesia-catalog-v{version}.json"
    catalog_schema_path = release / "program-matematika-indonesia-catalog-v1.schema.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_schema = json.loads(catalog_schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(catalog_schema, format_checker=FormatChecker()).validate(catalog)
    if catalog["program"]["zenodo"] != f"https://doi.org/10.5281/zenodo.{args.record_id}":
        raise ValueError("catalog Zenodo DOI does not match reserved record")
    if catalog["counts"]["courseRoles"] != 40 or catalog["counts"]["unresolvedRoles"] != 0:
        raise ValueError("catalog course/source closure mismatch")

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

    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    zip_results = {
        "source": verify_source_zip(source_zip),
        "backend": verify_backend_zip(backend_zip, backend),
    }

    files = []
    for path in sorted(candidate for candidate in release.iterdir() if candidate.is_file() and candidate.name not in {"CHECKSUMS.sha256", args.output_report.name}):
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
            "backend": backend_report["checks"],
            "complete_corpus_migrations": migration_result,
            "zip_verification": zip_results,
            "standalone_html": "pass",
            "github_transport": "available_for_bounded_push_after_release_validation",
        },
        "files_before_checksum": files,
    }
    args.output_report.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result": "pass", "report": str(args.output_report), "sha256": sha256_file(args.output_report)}, sort_keys=True))


if __name__ == "__main__":
    main()
