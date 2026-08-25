#!/usr/bin/env python3
"""Build deterministic source and backend ZIPs for a central release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


FIXED_ZIP_TIME = (2026, 8, 22, 0, 0, 0)
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_zip(output: Path, entries: list[tuple[str, bytes]]) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(entries):
            zip_bytes(archive, name, data)
    expected = {name: data for name, data in entries}
    with zipfile.ZipFile(output) as archive:
        archive.testzip()
        names = archive.namelist()
        if names != sorted(expected):
            raise ValueError(f"ZIP inventory/order mismatch: {output}")
        for name, data in expected.items():
            if archive.read(name) != data:
                raise ValueError(f"ZIP byte mismatch: {output}:{name}")
    return {
        "path": output.as_posix(),
        "entries": len(entries),
        "uncompressed_bytes": sum(len(data) for _, data in entries),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "verification": "pass",
    }


def files_under(root: Path, relative: str) -> list[Path]:
    path = root / relative
    if path.is_file():
        return [path]
    return sorted(candidate for candidate in path.rglob("*") if candidate.is_file())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--backend-v2-package", required=True, type=Path)
    parser.add_argument("--backend-v2-validation-receipt", required=True, type=Path)
    parser.add_argument("--release-dir", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    backend_v2 = args.backend_v2_package.resolve()
    backend_v2_validation_receipt = args.backend_v2_validation_receipt.resolve()
    version = args.version

    copies = {
        root / "schemas" / "catalog-v1.schema.json": release / "program-matematika-indonesia-catalog-v1.schema.json",
        root / "schemas" / "backend-v1.schema.json": release / "interlanguage-math-backend-v1.schema.json",
        root / "schemas" / "profiles" / "source-format-profile-v1.schema.json": release / "interlanguage-source-format-profile-v1.schema.json",
        root / "schemas" / "backend-migration-receipt-v1.schema.json": release / "interlanguage-backend-migration-receipt-v1.schema.json",
        root / "backend" / "BACKEND_CONVERGENCE_V1.md": release / "BACKEND_CONVERGENCE_V1.md",
        root / "backend" / "MIGRATION_HANDOFF_V1.md": release / "MIGRATION_HANDOFF_V1.md",
        root / "backend" / "authority" / "curriculum-authority-v1.json": release / "curriculum-authority-v1.json",
        root / "docs" / "data" / "learner-read-model.json": release / "learner-read-model-v1.json",
        root / "schemas" / "v1" / "curriculum-authority-v1.schema.json": release / "curriculum-authority-v1.schema.json",
        root / "schemas" / "v1" / "learner-read-model-v1.schema.json": release / "learner-read-model-v1.schema.json",
        backend / "validation_report.json": release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
        backend_v2_validation_receipt: release / f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json",
    }
    for source_name, release_name in V2_RELEASE_FILES.items():
        copies[root / source_name] = release / release_name
    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    receipt_directories = {source.parent.name for source in migration_receipts}
    if receipt_directories != set(MIGRATION_RECEIPT_FILENAMES):
        raise ValueError("complete-corpus migration receipt directory identity set mismatch")
    for source in migration_receipts:
        copies[source] = release / MIGRATION_RECEIPT_FILENAMES[source.parent.name]
    for source, target in copies.items():
        shutil.copyfile(source, target)

    backend_entries = []
    for path in sorted(candidate for candidate in backend.rglob("*") if candidate.is_file()):
        relative = path.relative_to(backend).as_posix()
        backend_entries.append((f"program-matematika-indonesia-backend-v1/{relative}", path.read_bytes()))
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    backend_result = build_zip(backend_zip, backend_entries)

    backend_v2_entries = []
    for path in sorted(candidate for candidate in backend_v2.rglob("*") if candidate.is_file()):
        relative = path.relative_to(backend_v2).as_posix()
        backend_v2_entries.append(
            (f"program-matematika-indonesia-backend-v2/{relative}", path.read_bytes())
        )
    backend_v2_zip = release / f"program-matematika-indonesia-backend-v2-v{version}.zip"
    backend_v2_result = build_zip(backend_v2_zip, backend_v2_entries)

    source_roots = [
        ".openai/hosting.json",
        ".gitattributes",
        ".gitignore",
        "LICENSE",
        "README.md",
        "eslint.config.mjs",
        "next.config.ts",
        "package.json",
        "pnpm-lock.yaml",
        "pnpm-workspace.yaml",
        "tsconfig.json",
        "vite.config.ts",
        "app",
        # public/hub is a reproducible prebuild mirror of docs/ and is ignored by
        # Git. Include only the tracked public input; npm run prebuild recreates
        # the mirror byte-for-byte from the committed docs source.
        "public/favicon.svg",
        "docs",
        "schemas/catalog-v1.schema.json",
        "schemas/backend-v1.schema.json",
        "schemas/backend-migration-receipt-v1.schema.json",
        "schemas/profiles/source-format-profile-v1.schema.json",
        "schemas/v2/backend-migration-receipt-v2.schema.json",
        "schemas/v2/federation-package-v2.schema.json",
        "schemas/v2/federation-record-v2.schema.json",
        "schemas/v2/namespace-v2.json",
        "schemas/v2/pmi-release-policy-v2.json",
        "schemas/v1/curriculum-authority-v1.schema.json",
        "schemas/v1/learner-read-model-v1.schema.json",
        "scripts/check-public-links.mjs",
        "scripts/export-release-catalog.mjs",
        "scripts/seed-curriculum-authority.mjs",
        "scripts/advance-curriculum-authority.mjs",
        "scripts/admit-o004-v055.mjs",
        "scripts/build-learner-read-model.mjs",
        "scripts/validate-learner-read-model.mjs",
        "scripts/sync-public-schemas.mjs",
        "scripts/export-single-file-site.mjs",
        "scripts/build-learner-start-pdf.py",
        "scripts/sync-sites-public.mjs",
        "scripts/build-d20-learner-routes.mjs",
        "scripts/validate-static-site.mjs",
        "scripts/verify-http-bytes.mjs",
        "scripts/build-backend-v1-schema.py",
        "scripts/export-curriculum-backend-v1.py",
        "scripts/validate-backend-v1.py",
        "scripts/validate-migration-receipt-v1.py",
        "scripts/build-release-bundle.py",
        "scripts/validate-release-bundle.py",
        "scripts/write-release-checksums.py",
        "scripts/build-backend-v2-federation.py",
        "scripts/build-backend-v2-validation-receipt.py",
        "scripts/validate-backend-v2-federation.py",
        "tests/backend-v2/test_build_backend_v2_federation.py",
        "tests/backend-v2/test_validate_backend_v2_federation.py",
        "backend/BACKEND_CONVERGENCE_V1.md",
        "backend/MIGRATION_HANDOFF_V1.md",
        "backend/v1/namespace.json",
        "backend/authority",
        "backend/v2.1",
    ]
    source_paths: list[Path] = []
    for relative in source_roots:
        source_paths.extend(files_under(root, relative))
    source_paths.extend(sorted((root / "scripts").glob("migrate-*-backend-v1.py")))
    source_paths.extend(sorted((root / "scripts").glob("test-*-backend-v1.py")))
    source_paths.extend(
        path
        for path in files_under(root, "backend/migrations")
        if "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    source_paths.extend(
        [
            release / f"program-matematika-indonesia-catalog-v{version}.json",
            release / f"RELEASE_NOTES_v{version}.md",
        ]
    )
    tracked_paths = set(
        subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", args.source_commit],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    generated_catalog = release / f"program-matematika-indonesia-catalog-v{version}.json"
    source_paths = [
        path
        for path in source_paths
        if path == generated_catalog
        or path.relative_to(root).as_posix() in tracked_paths
    ]
    if len(source_paths) != len(set(source_paths)):
        raise ValueError("duplicate source ZIP path")

    entries: list[tuple[str, bytes]] = []
    manifest_files = []
    for path in sorted(source_paths):
        if not path.is_relative_to(root):
            raise ValueError(f"source ZIP input escapes project root: {path}")
        source_path = path.relative_to(root).as_posix()
        name = source_path
        if path.parent == release:
            name = path.name
        data = path.read_bytes()
        entries.append((name, data))
        manifest_files.append(
            {
                "path": name,
                "source_path": source_path,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    source_manifest = {
        "schema_id": "program-matematika-indonesia/source-manifest/v2",
        "version": version,
        "source_commit": args.source_commit,
        "files": manifest_files,
    }
    entries.append(("SOURCE_MANIFEST.json", (json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")))
    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    source_result = build_zip(source_zip, entries)

    print(
        json.dumps(
            {
                "backend_v1_zip": backend_result,
                "backend_v2_zip": backend_v2_result,
                "source_zip": source_result,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
