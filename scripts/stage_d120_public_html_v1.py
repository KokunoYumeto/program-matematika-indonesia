#!/usr/bin/env python3
"""Stage the complete D120 reader into the central site without rewriting it."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from validate_d120_public_html_v1 import (
    DEFAULT_ARCHIVE,
    DEFAULT_DESTINATION,
    DEFAULT_MANIFEST,
    DEFAULT_RECEIPT,
    DEFAULT_SOURCE,
    EXPECTED_ARCHIVE_BYTES,
    EXPECTED_ARCHIVE_SHA256,
    REPO_ROOT,
    aggregate_sha256,
    inventory,
    release_manifest,
    sha256_file,
    validate,
    validate_frozen_identity,
    validate_links,
    validate_receipt,
)


COURSE_ROOT = REPO_ROOT / "docs" / "id-ID" / "courses" / "D120"
SOURCE_REPOSITORY = "https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id"
SOURCE_ZENODO = "https://zenodo.org/records/22073823"
SOURCE_ARCHIVE_URL = (
    "https://zenodo.org/records/22073823/files/"
    "o017-d120-id-2026.08.24-reader-html.zip?download=1"
)
SOURCE_COMMIT = "cea42b799b038fcac6f9762386d2e8eecd5b1372"
SOURCE_TREE = "01af08fa5170a128c19962b72c7bf6a96428a65e"


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def stage_reader(source: Path, destination: Path, manifest_path: Path) -> str:
    source_facts = inventory(source)
    if destination.exists():
        destination_facts = inventory(destination)
        if destination_facts == source_facts:
            return "already_byte_exact"
        if not manifest_path.is_file():
            raise ValueError("existing D120 destination differs and has no lane-owned manifest")
        prior = json.loads(manifest_path.read_text(encoding="utf-8"))
        if prior.get("reader", {}).get("files") != [fact.as_dict() for fact in destination_facts]:
            raise ValueError("existing D120 destination is not bound by its prior mirror manifest")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".d120-reader-stage-", dir=destination.parent))
    backup = destination.parent / ".d120-reader-previous"
    if backup.exists():
        shutil.rmtree(temporary)
        raise ValueError(f"stale bounded D120 backup must be inspected first: {backup}")
    try:
        for fact in source_facts:
            source_path = source.joinpath(*fact.path.split("/"))
            target_path = temporary.joinpath(*fact.path.split("/"))
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
        if inventory(temporary) != source_facts:
            raise ValueError("temporary D120 reader copy is not byte-identical")
        if destination.exists():
            destination.rename(backup)
        temporary.rename(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if backup.exists():
            if destination.exists():
                shutil.rmtree(destination)
            backup.rename(destination)
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return "copied_byte_exact"


def build_manifest(source: Path, destination: Path, archive: Path) -> dict[str, object]:
    release = release_manifest(archive)
    facts = validate_frozen_identity(destination, release)
    links = validate_links(destination, facts)
    return {
        "schema": "d120-reader-mirror-manifest-v1",
        "course_id": "D120",
        "locale": "id-ID",
        "status": "complete-local-reader-mirror",
        "source_authority": {
            "release": "2026.08.24",
            "repository_url": SOURCE_REPOSITORY,
            "zenodo_record_url": SOURCE_ZENODO,
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
            "archive": {
                "filename": archive.name,
                "url": SOURCE_ARCHIVE_URL,
                "bytes": archive.stat().st_size,
                "sha256": sha256_file(archive),
            },
            "release_manifest": {
                "schema": release["schema"],
                "file_count": release["file_count"],
                "total_uncompressed_bytes": release["total_uncompressed_bytes"],
            },
        },
        "reader": {
            "entrypoint": "reader/index.html",
            "file_count": len(facts),
            "bytes": sum(fact.bytes for fact in facts),
            "html_routes": sum(fact.path.endswith(".html") for fact in facts),
            "aggregate_sha256": aggregate_sha256(facts),
            "files": [fact.as_dict() for fact in facts],
        },
        "validation": {
            "source_destination_byte_identity": inventory(source) == facts,
            "unsafe_paths": 0,
            "symlinks": 0,
            "local_links": links,
        },
        "rights": {
            "boundary": "component-specific",
            "reader_and_delivery_expression": "CC-BY-SA-4.0",
            "bounded_method_donors": "CC-BY-4.0 with attribution and change notices",
            "original_scripts_config_and_schema": "MIT",
            "factual_manifest_data": "CC0-1.0",
            "bundled_components": "preserved in reader/LICENSES.md and reader/THIRD_PARTY_NOTICES.md",
            "umbrella_relicensing_claimed": False,
        },
        "replay": {
            "command": "python -B scripts/stage_d120_public_html_v1.py",
            "validation_command": "python -B scripts/validate_d120_public_html_v1.py",
            "network_required": False,
            "semantic_body_rewritten": False,
        },
    }


def build_receipt(
    source: Path,
    destination: Path,
    archive: Path,
    manifest_path: Path,
    validation: dict[str, object],
) -> dict[str, object]:
    facts = inventory(destination)
    stager = Path(__file__).resolve()
    validator = stager.with_name("validate_d120_public_html_v1.py")
    return {
        "schema": "d120-reader-mirror-receipt-v1",
        "status": "pass",
        "course_id": "D120",
        "locale": "id-ID",
        "operation": "idempotent_byte_exact_stage_or_verify",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "zenodo": SOURCE_ZENODO,
            "archive_url": SOURCE_ARCHIVE_URL,
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": sha256_file(archive),
            "file_count": len(inventory(source)),
        },
        "destination": {
            "path": destination.relative_to(REPO_ROOT).as_posix(),
            "entrypoint": destination.joinpath("index.html").relative_to(REPO_ROOT).as_posix(),
            "file_count": len(facts),
            "bytes": sum(fact.bytes for fact in facts),
            "aggregate_sha256": aggregate_sha256(facts),
        },
        "manifest": {
            "path": manifest_path.relative_to(REPO_ROOT).as_posix(),
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
        },
        "scripts": [
            {
                "path": stager.relative_to(REPO_ROOT).as_posix(),
                "bytes": stager.stat().st_size,
                "sha256": sha256_file(stager),
            },
            {
                "path": validator.relative_to(REPO_ROOT).as_posix(),
                "bytes": validator.stat().st_size,
                "sha256": sha256_file(validator),
            },
        ],
        "validation": validation,
        "invariants": {
            "source_destination_byte_identity": True,
            "release_manifest_closure_preserved": True,
            "component_rights_preserved": True,
            "local_render_dependencies_complete": True,
            "portable_subdirectory_links": True,
            "semantic_body_rewritten": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    archive = args.archive.resolve()
    manifest_path = args.manifest.resolve()
    receipt_path = args.receipt.resolve()
    try:
        if destination != DEFAULT_DESTINATION.resolve():
            raise ValueError("bounded D120 stager may write only the canonical central reader path")
        if manifest_path != DEFAULT_MANIFEST.resolve() or receipt_path != DEFAULT_RECEIPT.resolve():
            raise ValueError("D120 mirror controls must use the exact canonical paths")
        if manifest_path == receipt_path:
            raise ValueError("D120 mirror manifest and receipt paths must differ")
        if archive.stat().st_size != EXPECTED_ARCHIVE_BYTES or sha256_file(archive) != EXPECTED_ARCHIVE_SHA256:
            raise ValueError("frozen D120 archive identity changed")
        release = release_manifest(archive)
        source_facts = validate_frozen_identity(source, release)
        validate_links(source, source_facts)
        action = stage_reader(source, destination, manifest_path)
        manifest = build_manifest(source, destination, archive)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(json_bytes(manifest))
        validation = validate(source, destination, archive, manifest_path)
        receipt = build_receipt(source, destination, archive, manifest_path, validation)
        receipt_path.write_bytes(json_bytes(receipt))
        final_validation = validate(source, destination, archive, manifest_path)
        validate_receipt(receipt_path, source, destination, archive, manifest_path, final_validation)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"D120 public HTML staging: FAIL: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "staging_action": action,
                "reader": final_validation["reader"],
                "manifest": {
                    "path": manifest_path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": manifest_path.stat().st_size,
                    "sha256": sha256_file(manifest_path),
                },
                "receipt": {
                    "path": receipt_path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": receipt_path.stat().st_size,
                    "sha256": sha256_file(receipt_path),
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
