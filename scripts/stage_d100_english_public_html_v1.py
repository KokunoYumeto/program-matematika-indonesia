#!/usr/bin/env python3
"""Stage the complete D100 English readers into the central student site."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from validate_d100_english_public_html_v1 import (
    DEFAULT_DESTINATION,
    DEFAULT_MANIFEST,
    DEFAULT_RECEIPT,
    DEFAULT_SOURCE,
    CENTRAL_PROGRAM_HREF,
    EXPECTED_AGGREGATE_SHA256,
    EXPECTED_BYTES,
    EXPECTED_FILES,
    EXPECTED_INVENTORY_BYTES,
    EXPECTED_INVENTORY_SHA256,
    EXPECTED_PUBLIC_MANIFEST_BYTES,
    EXPECTED_PUBLIC_MANIFEST_SHA256,
    REPO_ROOT,
    SOURCE_COMMIT,
    SOURCE_TREE,
    aggregate_sha256,
    centralized_payload,
    expected_destination_inventory,
    inventory,
    sha256_file,
    validate,
    validate_destination_overlay,
    validate_links,
    validate_pinned_git_tree,
    validate_receipt,
    validate_source_inventory,
)


SOURCE_REPOSITORY = "https://github.com/KokunoYumeto/algebraic-geometry-bridge-id"
SOURCE_HOSTED_READER = "https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/en/"
SOURCE_ZENODO = "https://doi.org/10.5281/zenodo.22340270"
SOURCE_RELEASE_TAG = "en-v1.0.0"
CENTRAL_READER = "https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/reader/"


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def stage_reader(source: Path, destination: Path, manifest_path: Path) -> str:
    source_facts = inventory(source)
    expected_facts = expected_destination_inventory(source)
    if destination.exists():
        destination_facts = inventory(destination)
        if destination_facts == expected_facts:
            return "already_navigation_exact"
        if not manifest_path.is_file():
            raise ValueError("existing D100 English destination differs and has no lane-owned manifest")
        prior = json.loads(manifest_path.read_text(encoding="utf-8"))
        if prior.get("reader", {}).get("files") != [fact.as_dict() for fact in destination_facts]:
            raise ValueError("existing D100 English destination is not bound by its prior mirror manifest")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".d100-en-reader-stage-", dir=destination.parent))
    backup = destination.parent / ".d100-en-reader-previous"
    if backup.exists():
        shutil.rmtree(temporary)
        raise ValueError(f"stale bounded D100 English backup must be inspected first: {backup}")
    try:
        for fact in source_facts:
            source_path = source.joinpath(*fact.path.split("/"))
            target_path = temporary.joinpath(*fact.path.split("/"))
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(centralized_payload(fact.path, source_path.read_bytes()))
        if inventory(temporary) != expected_facts:
            raise ValueError("temporary D100 English reader navigation projection differs")
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
    return "copied_with_navigation_overlay"


def build_manifest(source: Path, destination: Path) -> dict[str, object]:
    facts, public_manifest, _source_inventory = validate_source_inventory(source)
    git_tree = validate_pinned_git_tree(source, facts)
    destination_facts, transformations = validate_destination_overlay(source, destination)
    links = validate_links(destination, destination_facts, require_program_navigation=True)
    return {
        "schema": "d100-english-reader-mirror-manifest-v1",
        "course_id": "D100",
        "locale": "en",
        "status": "complete-central-reader-with-navigation-overlay",
        "title": "Algebraic Geometry: Curves, Sheaves and Schemes — Independent English Edition",
        "source_authority": {
            "repository_url": SOURCE_REPOSITORY,
            "hosted_reader_url": SOURCE_HOSTED_READER,
            "zenodo_version_doi": SOURCE_ZENODO,
            "release_tag": SOURCE_RELEASE_TAG,
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
            "git_tree_validation": git_tree,
            "public_manifest": {
                "path": "public-manifest.json",
                "schema": public_manifest["schema"],
                "bytes": EXPECTED_PUBLIC_MANIFEST_BYTES,
                "sha256": EXPECTED_PUBLIC_MANIFEST_SHA256,
            },
            "sha256_inventory": {
                "path": "sha256-inventory.json",
                "bytes": EXPECTED_INVENTORY_BYTES,
                "sha256": EXPECTED_INVENTORY_SHA256,
            },
        },
        "reader": {
            "public_url": CENTRAL_READER,
            "entrypoint": "reader/index.html",
            "routes": [
                "reader/index.html",
                "reader/ak.html",
                "reader/bgk.html",
                "reader/companion.html",
            ],
            "file_count": len(destination_facts),
            "bytes": sum(fact.bytes for fact in destination_facts),
            "html_routes": 4,
            "aggregate_sha256": aggregate_sha256(destination_facts),
            "files": [fact.as_dict() for fact in destination_facts],
        },
        "central_navigation_overlay": {
            "program_home_href": CENTRAL_PROGRAM_HREF,
            "placement": ["after_skip_link", "before_footer_close"],
            "html_entrypoints": sorted(
                str(row["path"])
                for row in transformations
                if str(row["path"]).endswith(".html")
            ),
            "transformed_file_count": len(transformations),
            "transformations": transformations,
            "mathematical_body_rewritten": False,
        },
        "validation": {
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
            "source_files_byte_preserved": len(facts) - len(transformations),
            "source_inventory_closure_preserved": True,
            "unsafe_paths": 0,
            "symlinks": 0,
            "local_links": links,
        },
        "rights": {
            "boundary": "component-specific",
            "course_text_and_english_derivative": "CC-BY-SA-4.0 with attribution and change notices",
            "third_party_media": "component-specific rights preserved in reader/rights/authority",
            "build_and_qa_code": "MIT where stated by the source edition",
            "frozen_notice": "reader/rights/LICENSE.md",
            "central_clarification": "../RIGHTS_AND_ATTRIBUTION.md",
            "umbrella_relicensing_claimed": False,
        },
        "provenance": {
            "model": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "operation": "central hosting of an already completed English edition with a deterministic program-navigation shell",
            "source_authorship_preserved": True,
            "endorsement_claimed": False,
        },
        "replay": {
            "command": "python -B scripts/stage_d100_english_public_html_v1.py",
            "validation_command": "python -B scripts/validate_d100_english_public_html_v1.py",
            "network_required": False,
            "semantic_body_rewritten": False,
            "navigation_shell_added": True,
        },
    }


def build_receipt(
    source: Path,
    destination: Path,
    manifest_path: Path,
    validation: dict[str, object],
) -> dict[str, object]:
    facts = inventory(destination)
    stager = Path(__file__).resolve()
    validator = stager.with_name("validate_d100_english_public_html_v1.py")
    return {
        "schema": "d100-english-reader-mirror-receipt-v1",
        "status": "pass",
        "course_id": "D100",
        "locale": "en",
        "operation": "idempotent_stage_or_verify_with_navigation_overlay",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "hosted_reader": SOURCE_HOSTED_READER,
            "zenodo_version_doi": SOURCE_ZENODO,
            "release_tag": SOURCE_RELEASE_TAG,
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
            "file_count": EXPECTED_FILES,
            "bytes": EXPECTED_BYTES,
            "aggregate_sha256": EXPECTED_AGGREGATE_SHA256,
            "public_manifest_sha256": EXPECTED_PUBLIC_MANIFEST_SHA256,
            "sha256_inventory_sha256": EXPECTED_INVENTORY_SHA256,
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
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
            "source_inventory_closure_preserved": True,
            "component_rights_preserved": True,
            "local_render_dependencies_complete": True,
            "portable_subdirectory_links": True,
            "every_reader_entrypoint_links_to_program_home": True,
            "every_reader_html_document_links_to_program_home": True,
            "semantic_body_rewritten": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    manifest_path = args.manifest.resolve()
    receipt_path = args.receipt.resolve()
    try:
        if destination != DEFAULT_DESTINATION.resolve():
            raise ValueError("bounded D100 English stager may write only the canonical central reader path")
        if manifest_path != DEFAULT_MANIFEST.resolve() or receipt_path != DEFAULT_RECEIPT.resolve():
            raise ValueError("D100 English mirror controls must use the exact canonical paths")
        if manifest_path == receipt_path:
            raise ValueError("D100 English mirror manifest and receipt paths must differ")
        source_facts, _public_manifest, _source_inventory = validate_source_inventory(source)
        validate_pinned_git_tree(source, source_facts)
        validate_links(source, source_facts)
        action = stage_reader(source, destination, manifest_path)
        manifest = build_manifest(source, destination)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(json_bytes(manifest))
        validation = validate(source, destination, manifest_path)
        receipt = build_receipt(source, destination, manifest_path, validation)
        receipt_path.write_bytes(json_bytes(receipt))
        final_validation = validate(source, destination, manifest_path)
        validate_receipt(receipt_path, source, destination, manifest_path, final_validation)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, shutil.Error) as error:
        print(f"D100 English public HTML staging: FAIL: {error}", file=sys.stderr)
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
