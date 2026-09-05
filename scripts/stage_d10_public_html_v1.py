#!/usr/bin/env python3
"""Stage D10 with its frozen body and a deterministic central navigation shell."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from validate_d10_public_html_v1 import (
    DEFAULT_DESTINATION,
    DEFAULT_MANIFEST,
    DEFAULT_PACKAGE_ROOT,
    DEFAULT_SOURCE,
    CENTRAL_PROGRAM_HREF,
    EXPECTED_ARCHIVE_BYTES,
    EXPECTED_ARCHIVE_SHA256,
    aggregate_sha256,
    centralized_payload,
    expected_destination_inventory,
    inventory,
    sha256_file,
    validate,
    validate_destination_overlay,
    validate_expected_reader_identity,
    validate_local_links,
    validate_native_manifest,
)
from central_surface_navigation_overlay_v1 import (
    inventory_without_central_surface_overlay,
    remove_central_surface_overlays_in_tree,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
COURSE_ROOT = REPO_ROOT / "docs" / "id-ID" / "courses" / "D10"
RECEIPT_PATH = COURSE_ROOT / "D10_READER_MIRROR_RECEIPT_V1.json"
SOURCE_ARCHIVE = (
    REPO_ROOT.parent
    / "curriculum_logbook"
    / "d10-capability-v1-stage"
    / "fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0-source-backend.zip"
)
SOURCE_ARCHIVE_URL = (
    "https://github.com/KokunoYumeto/fremlin-measure-theory-id/releases/download/"
    "v1.0.0/fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0-source-backend.zip"
)
SOURCE_REPOSITORY_URL = "https://github.com/KokunoYumeto/fremlin-measure-theory-id"
SOURCE_ZENODO_URL = "https://zenodo.org/records/22181780"
SOURCE_SUBTREE = (
    "fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0/output/"
    "fondasi-teori-ukuran-v1-v2-complete-id/html"
)


def deterministic_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def safe_replace_reader(source: Path, destination: Path) -> str:
    source_facts = inventory(source)
    expected_facts = expected_destination_inventory(source)
    validate_expected_reader_identity(source_facts)
    if destination.exists():
        destination_facts = inventory_without_central_surface_overlay(
            destination, inventory(destination)
        )
        if destination_facts == expected_facts:
            stripped = remove_central_surface_overlays_in_tree(destination)
            return f"already_navigation_exact_central_overlays_removed_{stripped}"
        # Only replace a prior artifact owned by this deterministic staging lane.
        if not DEFAULT_MANIFEST.is_file():
            raise ValueError(
                "destination differs from source and has no prior D10 mirror manifest; "
                "refusing to overwrite an unproven directory"
            )
        prior = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        if prior.get("reader", {}).get("files") != [
            fact.as_dict() for fact in destination_facts
        ]:
            raise ValueError(
                "existing D10 destination is not bound by its prior mirror manifest"
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".d10-reader-stage-", dir=destination.parent))
    backup = destination.parent / ".d10-reader-previous"
    if backup.exists():
        shutil.rmtree(temporary)
        raise ValueError(f"stale bounded backup must be inspected first: {backup}")
    try:
        for fact in source_facts:
            source_path = source / Path(*fact.path.split("/"))
            target_path = temporary / Path(*fact.path.split("/"))
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(centralized_payload(fact.path, source_path.read_bytes()))
        staged_facts = inventory(temporary)
        if staged_facts != expected_facts:
            raise ValueError("temporary D10 reader navigation projection differs")
        if destination.exists():
            destination.rename(backup)
        temporary.rename(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if destination.exists() and backup.exists():
            shutil.rmtree(destination)
            backup.rename(destination)
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return "copied_with_navigation_overlay"


def copy_licences(package_root: Path) -> list[dict[str, object]]:
    bindings = [
        (
            package_root / "LICENSE",
            COURSE_ROOT / "licenses" / "Design-Science-License.txt",
            "LicenseRef-Design-Science-License",
        ),
        (
            package_root / "LICENSE-CC0-1.0.txt",
            COURSE_ROOT / "licenses" / "CC0-1.0.txt",
            "CC0-1.0",
        ),
        (
            package_root / "THIRD_PARTY_LICENSES" / "MathJax-3.2.2-Apache-2.0.txt",
            COURSE_ROOT / "licenses" / "MathJax-3.2.2-Apache-2.0.txt",
            "Apache-2.0",
        ),
    ]
    result: list[dict[str, object]] = []
    for source, target, identifier in bindings:
        if not source.is_file():
            raise ValueError(f"source component licence is missing: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha256_file(target) != sha256_file(source):
            raise ValueError(f"existing component licence differs; refusing overwrite: {target}")
        if not target.exists():
            shutil.copyfile(source, target)
        result.append(
            {
                "identifier": identifier,
                "path": target.relative_to(REPO_ROOT).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": sha256_file(target),
                "byte_exact_to_public_source_package": True,
            }
        )
    return result


def build_manifest(
    source: Path,
    destination: Path,
    package_root: Path,
    archive: Path,
    licences: list[dict[str, object]],
) -> dict[str, object]:
    facts, transformations = validate_destination_overlay(source, destination)
    source_facts = inventory(source)
    native_manifest = validate_native_manifest(source, source_facts)
    links = validate_local_links(destination, facts)
    return {
        "schema": "d10-reader-mirror-manifest-v1",
        "course_id": "D10",
        "locale": "id-ID",
        "status": "complete-public-reader-with-navigation-overlay",
        "source_authority": {
            "release": "v1.0.0",
            "repository_url": SOURCE_REPOSITORY_URL,
            "zenodo_record_url": SOURCE_ZENODO_URL,
            "source_archive": {
                "filename": archive.name,
                "bytes": archive.stat().st_size,
                "sha256": sha256_file(archive),
                "url": SOURCE_ARCHIVE_URL,
            },
            "source_subtree": SOURCE_SUBTREE,
            "native_manifest": native_manifest,
        },
        "reader": {
            "entrypoint": "reader/index.html",
            "download": (
                "reader/_downloads/"
                "fondasi-teori-ukuran-jilid-1-dan-jilid-2-lengkap-id.pdf"
            ),
            "file_count": len(facts),
            "bytes": sum(fact.bytes for fact in facts),
            "html_routes": sum(fact.path.endswith(".html") for fact in facts),
            "aggregate_sha256": aggregate_sha256(facts),
            "files": [fact.as_dict() for fact in facts],
        },
        "central_navigation_overlay": {
            "program_home_href": CENTRAL_PROGRAM_HREF,
            "placement": [
                "after_skip_link",
                "root_contents_closure_after_main_open",
                "before_footer_close",
            ],
            "scope": "every_html_document",
            "root_contents_links_added": [
                "pendahuluan-umum/index.html",
                "konkordansi/index.html",
                "referensi/index.html",
            ],
            "transformed_file_count": len(transformations),
            "transformations": transformations,
            "mathematical_body_rewritten": False,
        },
        "validation": {
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
            "source_files_byte_preserved": len(source_facts) - len(transformations),
            "unsafe_paths": 0,
            "symlinks": 0,
            "local_links": links,
        },
        "rights": {
            "umbrella_license": None,
            "boundary": "component-specific",
            "fremlin_derived_material": "LicenseRef-Design-Science-License",
            "independently_authored_metadata_and_tooling": "CC0-1.0",
            "bundled_mathjax_3_2_2": "Apache-2.0",
            "attribution": "D. H. Fremlin, Measure Theory, Volumes 1–2",
            "modification_notice": (
                "Complete Indonesian adaptation and reflow reader; publication date "
                "recorded by the source release as 30 August 2026."
            ),
            "component_licences": licences,
        },
        "replay": {
            "command": "python -B scripts/stage_d10_public_html_v1.py",
            "validation_command": "python -B scripts/validate_d10_public_html_v1.py",
            "network_required": False,
            "semantic_body_rewritten": False,
            "navigation_shell_added": True,
        },
    }


def build_receipt(
    source: Path,
    destination: Path,
    archive: Path,
    manifest_path: Path,
    validation: dict[str, object],
) -> dict[str, object]:
    stager = Path(__file__).resolve()
    validator = stager.with_name("validate_d10_public_html_v1.py")
    facts = inventory(destination)
    return {
        "schema": "d10-reader-mirror-receipt-v1",
        "status": "pass",
        "course_id": "D10",
        "locale": "id-ID",
        "staging_operation": "idempotent_stage_or_verify_with_navigation_overlay",
        "source": {
            "public_archive_url": SOURCE_ARCHIVE_URL,
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": sha256_file(archive),
            "subtree": SOURCE_SUBTREE,
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
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
            "native_reader_closure_preserved": True,
            "component_licences_preserved": True,
            "local_render_dependencies_complete": True,
            "portable_subdirectory_links": True,
            "network_required_to_render_math": False,
            "every_reader_entrypoint_links_to_program_home": True,
            "every_reader_html_document_links_to_program_home": True,
            "every_reader_html_document_is_inbound_reachable_from_contents": True,
            "semantic_body_rewritten": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--package-root", type=Path, default=DEFAULT_PACKAGE_ROOT)
    parser.add_argument("--archive", type=Path, default=SOURCE_ARCHIVE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=RECEIPT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    package_root = args.package_root.resolve()
    archive = args.archive.resolve()
    manifest_path = args.manifest.resolve()
    receipt_path = args.receipt.resolve()
    try:
        if destination != DEFAULT_DESTINATION.resolve():
            raise ValueError("this bounded stager may write only the canonical D10 reader path")
        if manifest_path.parent != COURSE_ROOT.resolve() or receipt_path.parent != COURSE_ROOT.resolve():
            raise ValueError("D10 manifest and receipt must remain directly under the D10 course root")
        if not archive.is_file():
            raise ValueError(f"frozen public source archive is missing: {archive}")
        if archive.stat().st_size != EXPECTED_ARCHIVE_BYTES:
            raise ValueError("frozen source archive byte count changed")
        if sha256_file(archive) != EXPECTED_ARCHIVE_SHA256:
            raise ValueError("frozen source archive SHA-256 changed")

        source_facts = inventory(source)
        validate_expected_reader_identity(source_facts)
        validate_native_manifest(source, source_facts)
        validate_local_links(source, source_facts, require_program_navigation=False)
        staging_action = safe_replace_reader(source, destination)
        licences = copy_licences(package_root)

        manifest = build_manifest(source, destination, package_root, archive, licences)
        manifest_path.write_bytes(deterministic_json_bytes(manifest))
        validation = validate(source, destination, package_root, manifest_path)
        receipt = build_receipt(
            source, destination, archive, manifest_path, validation
        )
        receipt_path.write_bytes(deterministic_json_bytes(receipt))

        # Receipt is outside the reader closure; run the independent validator again
        # after all generated files have reached their final bytes.
        final_validation = validate(source, destination, package_root, manifest_path)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"D10 public HTML staging: FAIL: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "pass",
                "staging_action": staging_action,
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
