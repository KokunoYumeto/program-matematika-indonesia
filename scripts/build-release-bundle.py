#!/usr/bin/env python3
"""Build deterministic source and backend ZIPs for a central release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


FIXED_ZIP_TIME = (2026, 8, 22, 0, 0, 0)


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
    parser.add_argument("--release-dir", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    version = args.version

    copies = {
        root / "schemas" / "backend-v1.schema.json": release / "interlanguage-math-backend-v1.schema.json",
        root / "schemas" / "profiles" / "source-format-profile-v1.schema.json": release / "interlanguage-source-format-profile-v1.schema.json",
        root / "schemas" / "backend-migration-receipt-v1.schema.json": release / "interlanguage-backend-migration-receipt-v1.schema.json",
        root / "backend" / "BACKEND_CONVERGENCE_V1.md": release / "BACKEND_CONVERGENCE_V1.md",
        root / "backend" / "MIGRATION_HANDOFF_V1.md": release / "MIGRATION_HANDOFF_V1.md",
        backend / "validation_report.json": release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
    }
    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    if not migration_receipts:
        raise ValueError("no complete-corpus migration receipts found")
    for source in migration_receipts:
        slug = source.parent.name.removesuffix("-v1")
        copies[source] = release / f"{slug}-backend-v1-migration-receipt.json"
    for source, target in copies.items():
        shutil.copyfile(source, target)

    backend_entries = []
    for path in sorted(candidate for candidate in backend.rglob("*") if candidate.is_file()):
        relative = path.relative_to(backend).as_posix()
        backend_entries.append((f"program-matematika-indonesia-backend-v1/{relative}", path.read_bytes()))
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    backend_result = build_zip(backend_zip, backend_entries)

    source_roots = [
        ".openai/hosting.json",
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
        "public",
        "docs",
        "schemas/catalog-v1.schema.json",
        "schemas/backend-v1.schema.json",
        "schemas/backend-migration-receipt-v1.schema.json",
        "schemas/profiles/source-format-profile-v1.schema.json",
        "scripts/check-public-links.mjs",
        "scripts/export-release-catalog.mjs",
        "scripts/export-single-file-site.mjs",
        "scripts/sync-sites-public.mjs",
        "scripts/validate-static-site.mjs",
        "scripts/verify-http-bytes.mjs",
        "scripts/build-backend-v1-schema.py",
        "scripts/export-curriculum-backend-v1.py",
        "scripts/validate-backend-v1.py",
        "scripts/validate-migration-receipt-v1.py",
        "scripts/build-release-bundle.py",
        "scripts/validate-release-bundle.py",
        "backend/BACKEND_CONVERGENCE_V1.md",
        "backend/MIGRATION_HANDOFF_V1.md",
        "backend/v1/namespace.json",
    ]
    source_paths: list[Path] = []
    for relative in source_roots:
        source_paths.extend(files_under(root, relative))
    source_paths.extend(sorted((root / "scripts").glob("migrate-*-backend-v1.py")))
    source_paths.extend(migration_receipts)
    source_paths.extend(
        [
            release / f"program-matematika-indonesia-catalog-v{version}.json",
            release / f"RELEASE_NOTES_v{version}.md",
        ]
    )
    if len(source_paths) != len(set(source_paths)):
        raise ValueError("duplicate source ZIP path")

    entries: list[tuple[str, bytes]] = []
    manifest_files = []
    for path in sorted(source_paths):
        if path.is_relative_to(root):
            name = path.relative_to(root).as_posix()
        else:
            name = path.name
        if path.parent == release:
            name = path.name
        data = path.read_bytes()
        entries.append((name, data))
        manifest_files.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    source_manifest = {
        "schema_id": "program-matematika-indonesia/source-manifest/v2",
        "version": version,
        "source_commit": args.source_commit,
        "files": manifest_files,
    }
    entries.append(("SOURCE_MANIFEST.json", (json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")))
    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    source_result = build_zip(source_zip, entries)

    print(json.dumps({"backend_zip": backend_result, "source_zip": source_result}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
