#!/usr/bin/env python3
"""Build and prove the zero-copy Judson -> common-backend v1 adapter.

The adapter is intentionally non-materializing.  It reads the frozen,
published 2026.08.21.1 SOURCE_BACKEND archive, validates its complete package
and native backend closure, constructs a common-schema dataset in memory, and
hashes the canonical virtual record stream.  Native corpus files are never
modified.  The only persistent output is the sanitized migration receipt.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import mimetypes
import re
import uuid
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


SCRIPT_PATH = Path(__file__).resolve()
CENTRAL_ROOT = SCRIPT_PATH.parent.parent
LANE_ROOT = CENTRAL_ROOT.parent / "abstract-algebra-theory-and-applications-id"
RELEASE_VERSION = "2026.08.21.1"
RELEASE_TAG = f"v{RELEASE_VERSION}"
RELEASE_DIR = LANE_ROOT / "releases" / f"v{RELEASE_VERSION}"
SOURCE_ARCHIVE_NAME = (
    "ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_"
    f"{RELEASE_VERSION}_SOURCE_BACKEND.zip"
)
SOURCE_ARCHIVE = RELEASE_DIR / SOURCE_ARCHIVE_NAME
PUBLICATION_RECEIPT = (
    LANE_ROOT / "00_control" / f"PUBLICATION_RECEIPT_{RELEASE_VERSION}.json"
)
COMMON_SCHEMA_PATH = CENTRAL_ROOT / "schemas" / "backend-v1.schema.json"
PROFILE_SCHEMA_PATH = (
    CENTRAL_ROOT / "schemas" / "profiles" / "source-format-profile-v1.schema.json"
)
RECEIPT_SCHEMA_PATH = (
    CENTRAL_ROOT / "schemas" / "backend-migration-receipt-v1.schema.json"
)
OUTPUT_PATH = (
    CENTRAL_ROOT
    / "backend"
    / "migrations"
    / "judson-id-v1"
    / "MIGRATION_RECEIPT.json"
)

COMMON_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
COMMON_SCHEMA_NAME = "interlanguage-math-modular-backend"
COMMON_SCHEMA_VERSION = "1.0.0"
WORKFLOW_ID = "R009"
NATIVE_PREFIX = "backend/v1/"
NATIVE_SCHEMA_REL = "schema/interlanguage-modular-record.schema.json"
NATIVE_MANIFEST_REL = "manifest.json"

EXPECTED_ARCHIVE_SHA256 = (
    "b8fd064e92c2c3e39abbb47cfb2909d071fca47007e286c26e9a0341c31c800c"
)
EXPECTED_PACKAGE_MANIFEST_SHA256 = (
    "86538cabf51b9a5a12f219e104d8adc1380b435073d8fb0a6cfdbf70581cd3c6"
)
EXPECTED_BACKEND_MANIFEST_SHA256 = (
    "312b5f7fcda24e7f0e1e430fa4a06d816abaae2fecc8655b37f0aa5d25c979be"
)
EXPECTED_AUTHORITY_CLOSURE_SHA256 = (
    "a7e6a243ebcf8836fe9c60df5fe6e6f743de7b519cedd3daee45d115e34e36b1"
)
EXPECTED_UPSTREAM_COMMIT = "043274d5dead03ff007a461ffe4c2b8477be1248"
EXPECTED_UPSTREAM_TREE = "3a95c40d7f904793a7a9f2c359a6c19ff79295cb"

UUID5_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


TABLE_TO_RECORD_TYPE = {
    "accessibility": "accessibility",
    "aliases": "alias",
    "alignments": "alignment",
    "artifact_members": "artifact_member",
    "artifacts": "artifact",
    "asset_revisions": "asset_revision",
    "assets": "asset",
    "build_recipes": "build_recipe",
    "concepts": "concept",
    "correction_bindings": "correction_binding",
    "correction_claims": "correction_claim",
    "corrections": "correction",
    "courses": "course",
    "editions": "edition",
    "experiments": "experiment",
    "file_revisions": "file_revision",
    "files": "file",
    "interactives": "interactive",
    "module_members": "module_member",
    "modules": "module",
    "occurrences": "occurrence",
    "placeholders": "placeholder",
    "programs": "program",
    "qa_events": "qa_event",
    "relations": "relation",
    "release_snapshots": "release_snapshot",
    "resources": "resource",
    "rights": "rights",
    "rights_assignments": "rights_assignment",
    "rights_rule_members": "rights_rule_member",
    "rights_rules": "rights_rule",
    "route_members": "route_member",
    "routes": "route",
    "segment_variants": "segment_variant",
    "segments": "segment",
    "term_variants": "term_variant",
    "terms": "term",
    "units": "unit",
}


@dataclass(frozen=True)
class NativeRow:
    path: str
    row_number: int
    raw: bytes
    value: dict[str, Any]

    @property
    def locator(self) -> str:
        return f"{NATIVE_PREFIX}{self.path}#L{self.row_number}"

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def generated_id(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(COMMON_NAMESPACE, record_type + '|' + stable_key)}"


def native_reference(row: NativeRow) -> dict[str, Any]:
    return {
        "bytes": len(row.raw),
        "line_sha256": row.sha256,
        "locator": row.locator,
        "native_id": row.value.get("id"),
        "native_record_type": row.value.get("record_type"),
    }


def media_type(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    overrides = {
        ".css": "text/css",
        ".csv": "text/csv",
        ".js": "text/javascript",
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".ptx": "application/xml",
        ".tex": "application/x-tex",
        ".tsv": "text/tab-separated-values",
        ".xml": "application/xml",
        ".xsl": "application/xslt+xml",
        ".xslt": "application/xslt+xml",
    }
    return overrides.get(suffix) or mimetypes.guess_type(path)[0] or "application/octet-stream"


def parse_mode(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    return {
        ".css": "css",
        ".csv": "csv",
        ".js": "javascript",
        ".json": "json",
        ".jsonl": "jsonl",
        ".ptx": "pretext_xml",
        ".svg": "svg_xml",
        ".tex": "latex",
        ".tsv": "tsv",
        ".xml": "pretext_xml",
        ".xsl": "xslt",
        ".xslt": "xslt",
    }.get(suffix, "binary")


def as_target_archive_path(native_path: str) -> str:
    return native_path[5:] if native_path.startswith("repo/") else native_path


def required_paths() -> None:
    required = [
        SOURCE_ARCHIVE,
        PUBLICATION_RECEIPT,
        COMMON_SCHEMA_PATH,
        PROFILE_SCHEMA_PATH,
        RECEIPT_SCHEMA_PATH,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing required input(s): {missing}")


def validate_publication_receipt() -> tuple[dict[str, Any], dict[str, Any]]:
    raw = PUBLICATION_RECEIPT.read_bytes()
    receipt = json.loads(raw)
    if receipt.get("version") != RELEASE_VERSION:
        raise RuntimeError("publication receipt version mismatch")
    if not receipt.get("publication_complete") or not receipt.get("verification_complete"):
        raise RuntimeError("frozen publication receipt is not complete and verified")
    derivative = receipt["derivative"]
    if derivative["tag"] != RELEASE_TAG:
        raise RuntimeError("publication tag mismatch")
    if derivative["parent_commit"] != EXPECTED_UPSTREAM_COMMIT:
        raise RuntimeError("publication parent commit mismatch")
    if receipt["backend"]["manifest_sha256"] != EXPECTED_BACKEND_MANIFEST_SHA256:
        raise RuntimeError("publication backend manifest mismatch")
    if (
        receipt["backend"]["source_package_manifest_sha256"]
        != EXPECTED_PACKAGE_MANIFEST_SHA256
    ):
        raise RuntimeError("publication package-manifest mismatch")

    assets = receipt["release"]["assets"]
    if len(assets) != receipt["release"]["asset_count"]:
        raise RuntimeError("publication asset count mismatch")

    checked_assets: list[dict[str, Any]] = []
    total_bytes = 0
    source_archive_hash: str | None = None
    for item in assets:
        local_path = RELEASE_DIR / item["name"]
        if not local_path.is_file():
            raise RuntimeError(f"missing frozen release asset: {item['name']}")
        actual_bytes = local_path.stat().st_size
        if actual_bytes != item["bytes"]:
            raise RuntimeError(f"release asset byte mismatch: {item['name']}")
        if local_path == SOURCE_ARCHIVE and source_archive_hash is not None:
            actual_sha = source_archive_hash
        else:
            actual_sha = sha256_file(local_path)
            if local_path == SOURCE_ARCHIVE:
                source_archive_hash = actual_sha
        if actual_sha != item["sha256"]:
            raise RuntimeError(f"release asset SHA-256 mismatch: {item['name']}")
        checked_assets.append(
            {
                "bytes": actual_bytes,
                "name": item["name"],
                "sha256": actual_sha,
            }
        )
        total_bytes += actual_bytes

    if total_bytes != receipt["release"]["asset_total_bytes"]:
        raise RuntimeError("release asset total byte mismatch")
    if source_archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("source/backend archive hash mismatch")

    evidence = {
        "asset_count": len(checked_assets),
        "asset_total_bytes": total_bytes,
        "derivative_commit": derivative["commit"],
        "derivative_repository": derivative["repository"],
        "derivative_tree": derivative["tree"],
        "github_release": receipt["release"]["url"],
        "publication_receipt_bytes": len(raw),
        "publication_receipt_sha256": sha256_bytes(raw),
        "tag": derivative["tag"],
        "tag_object": derivative["tag_object"],
        "verified_at": receipt["verified_at"],
        "zenodo_concept_doi": receipt["zenodo"]["concept_doi"],
        "zenodo_doi": receipt["zenodo"]["doi"],
        "zenodo_record": receipt["zenodo"]["record_url"],
    }
    return receipt, {"assets": checked_assets, **evidence}


def verify_source_archive() -> dict[str, Any]:
    archive_bytes = SOURCE_ARCHIVE.stat().st_size
    archive_sha = sha256_file(SOURCE_ARCHIVE)
    if archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("frozen source/backend archive SHA-256 mismatch")

    with zipfile.ZipFile(SOURCE_ARCHIVE) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise RuntimeError("duplicate names in frozen source/backend archive")

        package_manifest_raw = archive.read("PACKAGE_MANIFEST.csv")
        if sha256_bytes(package_manifest_raw) != EXPECTED_PACKAGE_MANIFEST_SHA256:
            raise RuntimeError("package manifest SHA-256 mismatch")
        package_rows = list(
            csv.DictReader(io.StringIO(package_manifest_raw.decode("utf-8"), newline=""))
        )
        package_by_path = {row["path"]: row for row in package_rows}
        expected_package_paths = set(names) - {"PACKAGE_MANIFEST.csv"}
        if set(package_by_path) != expected_package_paths:
            missing = sorted(expected_package_paths - set(package_by_path))
            extra = sorted(set(package_by_path) - expected_package_paths)
            raise RuntimeError(
                f"package manifest inventory mismatch; missing={missing}, extra={extra}"
            )

        checked_uncompressed_bytes = 0
        for info in infos:
            data = archive.read(info.filename)  # read also enforces the ZIP CRC
            if len(data) != info.file_size:
                raise RuntimeError(f"ZIP member byte mismatch: {info.filename}")
            checked_uncompressed_bytes += len(data)
            if info.filename == "PACKAGE_MANIFEST.csv":
                continue
            row = package_by_path[info.filename]
            if int(row["bytes"]) != len(data):
                raise RuntimeError(f"package row byte mismatch: {info.filename}")
            if row["sha256"] != sha256_bytes(data):
                raise RuntimeError(f"package row SHA-256 mismatch: {info.filename}")

        backend_manifest_raw = archive.read(NATIVE_PREFIX + NATIVE_MANIFEST_REL)
        backend_manifest_sha = sha256_bytes(backend_manifest_raw)
        if backend_manifest_sha != EXPECTED_BACKEND_MANIFEST_SHA256:
            raise RuntimeError("backend manifest SHA-256 mismatch")
        manifest_pointer = archive.read(NATIVE_PREFIX + "manifest.sha256").decode("ascii")
        if manifest_pointer != f"{backend_manifest_sha}  manifest.json\n":
            raise RuntimeError("backend manifest pointer mismatch")
        backend_manifest = json.loads(backend_manifest_raw)
        if backend_manifest["upstream_commit"] != EXPECTED_UPSTREAM_COMMIT:
            raise RuntimeError("backend upstream commit mismatch")
        if backend_manifest["upstream_tree"] != EXPECTED_UPSTREAM_TREE:
            raise RuntimeError("backend upstream tree mismatch")
        if (
            backend_manifest["authority_closure_manifest_sha256"]
            != EXPECTED_AUTHORITY_CLOSURE_SHA256
        ):
            raise RuntimeError("backend authority-closure hash mismatch")

        manifest_files = {entry["path"]: entry for entry in backend_manifest["files"]}
        expected_backend_paths = {
            NATIVE_PREFIX + path for path in manifest_files
        } | {
            NATIVE_PREFIX + "README.md",
            NATIVE_PREFIX + "manifest.json",
            NATIVE_PREFIX + "manifest.sha256",
        }
        actual_backend_paths = {name for name in names if name.startswith(NATIVE_PREFIX)}
        if actual_backend_paths != expected_backend_paths:
            missing = sorted(expected_backend_paths - actual_backend_paths)
            extra = sorted(actual_backend_paths - expected_backend_paths)
            raise RuntimeError(
                f"backend closure mismatch; missing={missing}, extra={extra}"
            )

        for rel_path, entry in manifest_files.items():
            data = archive.read(NATIVE_PREFIX + rel_path)
            if len(data) != entry["bytes"]:
                raise RuntimeError(f"backend byte mismatch: {rel_path}")
            if sha256_bytes(data) != entry["sha256"]:
                raise RuntimeError(f"backend SHA-256 mismatch: {rel_path}")
            rows = entry.get("rows")
            if rows is None:
                continue
            if rel_path.endswith(".jsonl"):
                actual_rows = len(data.splitlines())
            elif rel_path.endswith(".csv"):
                actual_rows = sum(
                    1
                    for _ in csv.reader(
                        io.StringIO(data.decode("utf-8"), newline="")
                    )
                )
            else:
                raise RuntimeError(f"unknown row-counted backend format: {rel_path}")
            if actual_rows != rows:
                raise RuntimeError(f"backend row-count mismatch: {rel_path}")

        authority_raw = archive.read("authority/AUTHORITY_SOURCE_CLOSURE_MANIFEST.tsv")
        if sha256_bytes(authority_raw) != EXPECTED_AUTHORITY_CLOSURE_SHA256:
            raise RuntimeError("authority source-closure manifest mismatch")

    return {
        "archive_bytes": archive_bytes,
        "archive_entries": len(names),
        "archive_sha256": archive_sha,
        "archive_uncompressed_bytes": checked_uncompressed_bytes,
        "authority_closure_manifest_bytes": len(authority_raw),
        "authority_closure_manifest_sha256": sha256_bytes(authority_raw),
        "backend_file_count": len(expected_backend_paths),
        "backend_manifest_bytes": len(backend_manifest_raw),
        "backend_manifest_entries": len(manifest_files),
        "backend_manifest_sha256": backend_manifest_sha,
        "package_manifest_bytes": len(package_manifest_raw),
        "package_manifest_entries": len(package_rows),
        "package_manifest_sha256": sha256_bytes(package_manifest_raw),
        "zip_crc_and_inventory_result": "pass",
    }


def load_native_rows(
    archive: zipfile.ZipFile,
    backend_manifest: dict[str, Any],
    native_schema: dict[str, Any],
) -> tuple[dict[str, list[NativeRow]], dict[str, Any]]:
    rows_by_path: dict[str, list[NativeRow]] = {}
    aggregate = hashlib.sha256()
    aggregate_bytes = 0
    total_rows = 0
    native_validator = Draft202012Validator(
        native_schema, format_checker=FormatChecker()
    )
    native_schema_validated = 0
    augmentation_rows = 0
    noncanonical_augmentation_rows = 0
    all_ids: list[str] = []
    primary_ids: list[str] = []

    for entry in sorted(backend_manifest["files"], key=lambda item: item["path"]):
        rel_path = entry["path"]
        if not rel_path.endswith(".jsonl"):
            continue
        data = archive.read(NATIVE_PREFIX + rel_path)
        if not data.endswith(b"\n") or b"\r\n" in data:
            raise RuntimeError(f"non-canonical JSONL line ending: {rel_path}")
        raw_lines = data[:-1].split(b"\n") if data else []
        parsed_rows: list[NativeRow] = []
        ids_in_file: list[str] = []
        aggregate.update(rel_path.encode("utf-8") + b"\0")
        aggregate.update(data)
        aggregate_bytes += len(rel_path.encode("utf-8")) + 1 + len(data)
        for row_number, raw_line in enumerate(raw_lines, start=1):
            value = json.loads(raw_line)
            is_augmentation = value.get("record_type") in {
                "segment_disposition",
                "term_disposition",
            }
            if canonical_json_bytes(value) != raw_line and not is_augmentation:
                raise RuntimeError(f"non-canonical JSON object: {rel_path}#{row_number}")
            if canonical_json_bytes(value) != raw_line and is_augmentation:
                noncanonical_augmentation_rows += 1
            row = NativeRow(rel_path, row_number, raw_line, value)
            parsed_rows.append(row)
            native_id = value.get("id")
            if not isinstance(native_id, str) or not UUID5_RE.fullmatch(native_id):
                raise RuntimeError(f"invalid native UUIDv5: {row.locator}")
            ids_in_file.append(native_id)
            all_ids.append(native_id)
            if is_augmentation:
                augmentation_rows += 1
            else:
                errors = sorted(
                    native_validator.iter_errors(value), key=lambda err: list(err.path)
                )
                if errors:
                    raise RuntimeError(
                        f"native schema failure at {row.locator}: {errors[0].message}"
                    )
                native_schema_validated += 1
                primary_ids.append(native_id)
        if ids_in_file != sorted(ids_in_file):
            raise RuntimeError(f"native JSONL is not ID-sorted: {rel_path}")
        if len(parsed_rows) != entry["rows"]:
            raise RuntimeError(f"native JSONL row-count mismatch: {rel_path}")
        rows_by_path[rel_path] = parsed_rows
        total_rows += len(parsed_rows)

    if total_rows != 24733:
        raise RuntimeError(f"unexpected native JSONL row count: {total_rows}")
    if len(primary_ids) != len(set(primary_ids)):
        duplicates = sorted(
            key for key, count in Counter(primary_ids).items() if count > 1
        )
        raise RuntimeError(f"duplicate primary native IDs: {duplicates[:10]}")

    duplicate_occurrences = sum(count - 1 for count in Counter(all_ids).values())
    if duplicate_occurrences != augmentation_rows:
        raise RuntimeError("native augmentation-ID overlap count mismatch")

    source_segments = {
        row.value["id"]: row.value
        for row in rows_by_path["text/segments.en-US.jsonl"]
    }
    edition_segments = {
        row.value["id"]: row.value
        for row in rows_by_path["text/segments.edition.id-ID.jsonl"]
    }
    translations = rows_by_path["text/translations.id-ID.jsonl"]
    translation_segment_ids = [row.value["segment_id"] for row in translations]
    if len(translation_segment_ids) != len(set(translation_segment_ids)):
        raise RuntimeError("multiple target translations for a source segment")
    if set(translation_segment_ids) != set(source_segments):
        raise RuntimeError("source/target segment closure mismatch")
    for row in translations:
        source = source_segments[row.value["segment_id"]]
        if row.value["source_sha256"] != source["source_sha256"]:
            raise RuntimeError(f"translation source hash mismatch: {row.locator}")
        if row.value["target_fragment_xml"] is None:
            if (
                row.value["state"] != "source_frozen"
                or row.value["target_sha256"] is not None
                or row.value["content_locale"] != source["source_locale"]
            ):
                raise RuntimeError(f"invalid source-frozen target: {row.locator}")
        elif (
            sha256_bytes(row.value["target_fragment_xml"].encode("utf-8"))
            != row.value["target_sha256"]
        ):
            raise RuntimeError(f"target payload hash mismatch: {row.locator}")
    for row in rows_by_path["text/segments.en-US.jsonl"]:
        if sha256_bytes(row.value["source_fragment_xml"].encode("utf-8")) != row.value[
            "source_sha256"
        ]:
            raise RuntimeError(f"source payload hash mismatch: {row.locator}")
    for row in rows_by_path["text/segments.edition.id-ID.jsonl"]:
        if sha256_bytes(row.value["source_fragment_xml"].encode("utf-8")) != row.value[
            "source_sha256"
        ]:
            raise RuntimeError(f"edition payload hash mismatch: {row.locator}")

    unit_ids = {
        row.value["id"] for row in rows_by_path["topology/units.jsonl"]
    }
    concept_ids = {
        row.value["id"] for row in rows_by_path["lexicon/concepts.jsonl"]
    }
    course_ids = {
        row.value["id"] for row in rows_by_path["courses/courses.jsonl"]
    }
    edition_ids = {
        row.value["id"] for row in rows_by_path["authority/editions.jsonl"]
    }
    resource_ids = {
        row.value["id"] for row in rows_by_path["authority/resources.jsonl"]
    }
    rights_ids = {
        row.value["id"] for row in rows_by_path["rights/rights.jsonl"]
    }

    def require_subset(actual: Iterable[str], expected: set[str], label: str) -> None:
        missing = set(actual) - expected
        if missing:
            raise RuntimeError(f"native foreign-key failure {label}: {sorted(missing)[:10]}")

    require_subset(
        (
            row.value["unit_id"]
            for path in ["text/segments.en-US.jsonl", "text/segments.edition.id-ID.jsonl"]
            for row in rows_by_path[path]
        ),
        unit_ids,
        "segment.unit_id",
    )
    require_subset(
        (row.value["unit_id"] for row in rows_by_path["identity/id-map.jsonl"]),
        unit_ids,
        "id_map.unit_id",
    )
    require_subset(
        (row.value["unit_id"] for row in rows_by_path["courses/course-units.jsonl"]),
        unit_ids,
        "course_unit.unit_id",
    )
    require_subset(
        (row.value["course_id"] for row in rows_by_path["courses/course-units.jsonl"]),
        course_ids,
        "course_unit.course_id",
    )
    require_subset(
        (row.value["concept_id"] for row in rows_by_path["lexicon/concept-units.jsonl"]),
        concept_ids,
        "concept_unit.concept_id",
    )
    require_subset(
        (row.value["unit_id"] for row in rows_by_path["lexicon/concept-units.jsonl"]),
        unit_ids,
        "concept_unit.unit_id",
    )
    require_subset(
        (row.value["concept_id"] for row in rows_by_path["lexicon/terms.id-ID.jsonl"]),
        concept_ids,
        "term.concept_id",
    )
    require_subset(
        (row.value["unit_id"] for row in rows_by_path["code/sage-cells.jsonl"]),
        unit_ids,
        "sage_cell.unit_id",
    )
    require_subset(
        (
            affected
            for row in rows_by_path["corrections/corrections.jsonl"]
            for affected in row.value["affected_unit_ids"]
        ),
        unit_ids,
        "correction.affected_unit_ids",
    )
    require_subset(
        (
            parent
            for row in rows_by_path["topology/units.jsonl"]
            if (parent := row.value.get("parent_id")) is not None
        ),
        unit_ids,
        "unit.parent_id",
    )
    require_subset(
        (
            endpoint
            for row in rows_by_path["topology/relations.jsonl"]
            for endpoint in (row.value["from_id"], row.value["to_id"])
        ),
        set(primary_ids),
        "relation endpoints",
    )
    require_subset(
        (row.value["edition_id"] for row in rows_by_path["authority/source-files.jsonl"]),
        edition_ids,
        "source_file.edition_id",
    )
    require_subset(
        (row.value["edition_id"] for row in rows_by_path["edition/source-deltas.id-ID.jsonl"]),
        edition_ids,
        "source_delta.edition_id",
    )
    require_subset(
        (row.value["edition_id"] for row in rows_by_path["artifacts/artifacts.jsonl"]),
        edition_ids,
        "artifact.edition_id",
    )
    require_subset(
        (row.value["resource_id"] for row in rows_by_path["authority/editions.jsonl"]),
        resource_ids,
        "edition.resource_id",
    )
    require_subset(
        (row.value["rights_id"] for row in rows_by_path["authority/editions.jsonl"]),
        rights_ids,
        "edition.rights_id",
    )

    segment_dispositions = rows_by_path["state/segment-dispositions.id-ID.jsonl"]
    term_dispositions = rows_by_path["state/term-dispositions.id-ID.jsonl"]
    if {row.value["segment_id"] for row in segment_dispositions} - set(source_segments):
        raise RuntimeError("segment-disposition closure failure")
    term_ids = {row.value["id"] for row in rows_by_path["lexicon/terms.id-ID.jsonl"]}
    if {row.value["term_id"] for row in term_dispositions} - term_ids:
        raise RuntimeError("term-disposition closure failure")

    return rows_by_path, {
        "augmentation_rows": augmentation_rows,
        "canonical_primary_jsonl": True,
        "global_primary_id_duplicates": 0,
        "jsonl_bytes_with_path_framing": aggregate_bytes,
        "jsonl_record_count": total_rows,
        "jsonl_stream_sha256": aggregate.hexdigest(),
        "native_schema_validated_rows": native_schema_validated,
        "noncanonical_augmentation_rows": noncanonical_augmentation_rows,
        "primary_record_count": len(primary_ids),
        "segment_dispositions": len(segment_dispositions),
        "source_segment_count": len(source_segments),
        "target_translation_count": len(translations),
        "term_dispositions": len(term_dispositions),
        "translation_state_counts": dict(
            sorted(Counter(row.value["state"] for row in translations).items())
        ),
    }


class DatasetBuilder:
    def __init__(
        self,
        rows: dict[str, list[NativeRow]],
        common_schema: dict[str, Any],
        profile_schema: dict[str, Any],
        publication: dict[str, Any],
        public_evidence: dict[str, Any],
        archive: zipfile.ZipFile,
    ) -> None:
        self.rows = rows
        self.common_schema = common_schema
        self.profile_schema = profile_schema
        self.publication = publication
        self.public_evidence = public_evidence
        self.archive = archive
        self.tables: dict[str, list[dict[str, Any]]] = {
            table: [] for table in TABLE_TO_RECORD_TYPE
        }
        self.claimed_native_rows: set[tuple[str, int]] = set()
        self.generated_identity_basis: dict[str, tuple[str, str]] = {}
        self.profile_count = 0

        self.resource_row = self.rows["authority/resources.jsonl"][0]
        self.resource_id = self.resource_row.value["id"]
        self.rights_row = self.rows["rights/rights.jsonl"][0]
        self.rights_id = self.rights_row.value["id"]
        editions = self.rows["authority/editions.jsonl"]
        self.source_edition_row = next(row for row in editions if "revision_sha" in row.value)
        self.target_edition_row = next(row for row in editions if "source_edition_id" in row.value)
        self.source_edition_id = self.source_edition_row.value["id"]
        self.target_edition_id = self.target_edition_row.value["id"]
        unit_rows = self.rows["topology/units.jsonl"]
        root_rows = [row for row in unit_rows if row.value.get("parent_id") is None]
        if len(root_rows) != 1:
            raise RuntimeError("Judson native unit graph must have exactly one root")
        self.root_unit_id = root_rows[0].value["id"]
        self.unit_by_id = {row.value["id"]: row.value for row in unit_rows}

    def add(self, table: str, record: dict[str, Any], generated: bool = False) -> None:
        expected_record_type = TABLE_TO_RECORD_TYPE[table]
        if record.get("record_type") != expected_record_type:
            raise RuntimeError(f"record type/table mismatch for {table}")
        if generated:
            expected = generated_id(record["record_type"], record["stable_key"])
            if record["id"] != expected:
                raise RuntimeError(f"generated identity formula mismatch: {record['id']}")
            self.generated_identity_basis[record["id"]] = (
                record["record_type"],
                record["stable_key"],
            )
        self.tables[table].append(record)

    def claim(self, row: NativeRow) -> dict[str, Any]:
        key = (row.path, row.row_number)
        if key in self.claimed_native_rows:
            raise RuntimeError(f"native row claimed more than once: {row.locator}")
        self.claimed_native_rows.add(key)
        return native_reference(row)

    def extensions(
        self,
        row: NativeRow | None = None,
        profile: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if row is not None:
            result["judson.native"] = self.claim(row)
        if profile is not None:
            result["interlanguage.source-profile"] = profile
            self.profile_count += 1
        if extra:
            result.update(extra)
        return result

    @staticmethod
    def common_base(
        *,
        record_type: str,
        record_id: str,
        stable_key: str,
        recorded_at: str,
        status: str,
        supersedes_id: str | None,
        extensions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": record_id,
            "record_type": record_type,
            "recorded_at": recorded_at,
            "schema_name": COMMON_SCHEMA_NAME,
            "schema_version": COMMON_SCHEMA_VERSION,
            "stable_key": stable_key,
            "status": status,
            "supersedes_id": supersedes_id,
            "workflow_id": WORKFLOW_ID,
        }
        if extensions:
            result["extensions"] = extensions
        return result

    def generated_base(
        self,
        *,
        record_type: str,
        stable_key: str,
        recorded_at: str,
        status: str = "active",
        extensions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.common_base(
            record_type=record_type,
            record_id=generated_id(record_type, stable_key),
            stable_key=stable_key,
            recorded_at=recorded_at,
            status=status,
            supersedes_id=None,
            extensions=extensions,
        )

    def native_base(
        self,
        row: NativeRow,
        *,
        record_type: str,
        stable_key: str,
        profile: dict[str, Any] | None = None,
        extra_extensions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        extensions = self.extensions(row=row, profile=profile, extra=extra_extensions)
        return self.common_base(
            record_type=record_type,
            record_id=row.value["id"],
            stable_key=stable_key,
            recorded_at=row.value["recorded_at"],
            status=row.value["status"],
            supersedes_id=row.value.get("supersedes_id"),
            extensions=extensions,
        )

    def source_authority_path(self, source_path: str) -> str:
        return (
            f"authority/upstream-{EXPECTED_UPSTREAM_COMMIT[:8]}/"
            f"aata-{EXPECTED_UPSTREAM_COMMIT}/src/{source_path}"
        )

    def pretext_profile(
        self,
        *,
        revision_id: str,
        authority_path: str,
        structural_xpath: str,
        identity_strategy: str,
        native_xml_id: str | None = None,
        label: str | None = None,
        division_kind: str | None = None,
    ) -> dict[str, Any]:
        return {
            "authority_file_revision_id": revision_id,
            "authority_path": authority_path,
            "division_kind": division_kind,
            "format_profile": "pretext",
            "identity_strategy": identity_strategy,
            "label": label,
            "native_xml_id": native_xml_id,
            "profile_version": "1.0.0",
            "structural_xpath": structural_xpath,
        }

    def build_authority(self) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        resource = self.resource_row.value
        resource_record = self.native_base(
            self.resource_row,
            record_type="resource",
            stable_key="judson:resource:aata",
        )
        resource_record.update(
            {
                "authority_policy": "pinned Git commit, tree, and complete source-closure manifest",
                "creator_name": "; ".join(resource["creators"]),
                "official_reader": resource["homepage"],
                "official_repository": resource["upstream_repo"],
                "original_title": resource["title"],
                "resource_key": "R009-JUDSON-AATA",
                "work_type": "open textbook",
            }
        )
        self.add("resources", resource_record)

        rights = self.rights_row.value
        change_notice = rights["copyright"]["modified_version_notice_en"]
        rights_record = self.native_base(
            self.rights_row,
            record_type="rights",
            stable_key="judson:rights:gfdl-1.3-or-later",
        )
        rights_record.update(
            {
                "assertion_status": "verified",
                "attribution": "; ".join(rights["copyright"]["original_holders"]),
                "authority": "repo/COPYING and repo/src/gfdl.xml",
                "change_notice": change_notice,
                "license_expression": rights["license_expression"],
                "nonendorsement": "No endorsement by the source contributors is asserted.",
                "notice_locator": rights["license_source_path"],
                "notice_sha256": rights["license_source_sha256"],
                "source_component_id": self.resource_id,
                "third_party_status": "component notices and upstream provenance preserved",
            }
        )
        self.add("rights", rights_record)

        source = self.source_edition_row.value
        source_edition = self.native_base(
            self.source_edition_row,
            record_type="edition",
            stable_key=f"judson:edition:source:{source['revision_sha']}",
        )
        source_edition.update(
            {
                "archive_sha256": source["archive_sha256"],
                "commit_sha": source["revision_sha"],
                "edition_kind": "source",
                "locale": "en-US",
                "release_date": None,
                "resource_id": source["resource_id"],
                "rights_id": source["rights_id"],
                "source_edition_id": None,
                "tree_sha": source["tree_sha"],
                "vcs_ref": source["revision_url"],
                "vcs_type": source["vcs"],
                "version_label": source["revision_sha"],
            }
        )
        self.add("editions", source_edition)

        target = self.target_edition_row.value
        derivative = self.publication["derivative"]
        target_edition = self.native_base(
            self.target_edition_row,
            record_type="edition",
            stable_key=f"judson:edition:id-ID:{RELEASE_VERSION}",
        )
        target_edition.update(
            {
                "archive_sha256": EXPECTED_ARCHIVE_SHA256,
                "commit_sha": derivative["commit"],
                "edition_kind": "translation",
                "locale": target["locale"],
                "release_date": self.publication["zenodo"]["published_at"],
                "resource_id": target["resource_id"],
                "rights_id": target["rights_id"],
                "source_edition_id": target["source_edition_id"],
                "tree_sha": derivative["tree"],
                "vcs_ref": derivative["tag"],
                "vcs_type": "git",
                "version_label": RELEASE_VERSION,
            }
        )
        self.add("editions", target_edition)

        source_file_revision_by_path: dict[str, str] = {}
        source_file_id_by_path: dict[str, str] = {}
        target_file_revision_by_actual_path: dict[str, str] = {}

        for row in self.rows["authority/source-files.jsonl"]:
            value = row.value
            authority_path = self.source_authority_path(value["path"])
            data = self.archive.read(authority_path)
            if len(data) != value["bytes"] or sha256_bytes(data) != value["sha256"]:
                raise RuntimeError(f"source-file payload mismatch: {value['path']}")
            stable_key = f"judson:file:{value['path']}"
            file_record = self.native_base(
                row, record_type="file", stable_key=stable_key
            )
            file_record.update(
                {
                    "canonical_path": value["path"],
                    "media_type": media_type(value["path"]),
                    "parse_mode": parse_mode(value["path"]),
                    "resource_id": self.resource_id,
                    "role": "source_authority",
                }
            )
            self.add("files", file_record)
            source_file_id_by_path[value["path"]] = value["id"]

            revision_key = f"judson:file-revision:source:{value['id']}:{self.source_edition_id}"
            revision = self.generated_base(
                record_type="file_revision",
                stable_key=revision_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "judson.adapter": {
                        "generated_from_native_file_id": value["id"],
                        "native_locator": row.locator,
                    }
                },
            )
            revision.update(
                {
                    "actual_path": authority_path,
                    "bytes": value["bytes"],
                    "edition_id": self.source_edition_id,
                    "file_id": value["id"],
                    "generated": False,
                    "git_blob_sha1": None,
                    "sha256": value["sha256"],
                    "source_revision_id": None,
                }
            )
            self.add("file_revisions", revision, generated=True)
            source_file_revision_by_path[value["path"]] = revision["id"]

        for row in self.rows["edition/source-deltas.id-ID.jsonl"]:
            value = row.value
            actual_path = as_target_archive_path(value["path"])
            data = self.archive.read(actual_path)
            if len(data) != value["bytes"] or sha256_bytes(data) != value["sha256"]:
                raise RuntimeError(f"target-file payload mismatch: {actual_path}")
            source_path = actual_path[4:] if actual_path.startswith("src/") else None
            source_file_id = source_file_id_by_path.get(source_path or "")
            if source_file_id is None:
                file_key = f"judson:file:target-only:{actual_path}"
                file_id = generated_id("file", file_key)
                target_file = self.generated_base(
                    record_type="file",
                    stable_key=file_key,
                    recorded_at=value["recorded_at"],
                    extensions={
                        "judson.adapter": {
                            "classification": "target-only or non-authority-closure file identity",
                            "native_source_delta_id": value["id"],
                        }
                    },
                )
                target_file.update(
                    {
                        "canonical_path": actual_path,
                        "media_type": media_type(actual_path),
                        "parse_mode": parse_mode(actual_path),
                        "resource_id": self.resource_id,
                        "role": "target_edition",
                    }
                )
                self.add("files", target_file, generated=True)
            else:
                file_id = source_file_id

            revision = self.native_base(
                row,
                record_type="file_revision",
                stable_key=f"judson:file-revision:target:{file_id}:{self.target_edition_id}",
            )
            revision.update(
                {
                    "actual_path": actual_path,
                    "bytes": value["bytes"],
                    "edition_id": value["edition_id"],
                    "file_id": file_id,
                    "generated": False,
                    "git_blob_sha1": None,
                    "sha256": value["sha256"],
                    "source_revision_id": source_file_revision_by_path.get(source_path or ""),
                }
            )
            self.add("file_revisions", revision)
            target_file_revision_by_actual_path[actual_path] = value["id"]

        return (
            source_file_revision_by_path,
            source_file_id_by_path,
            target_file_revision_by_actual_path,
        )

    def build_assets(
        self,
        target_file_revision_by_actual_path: dict[str, str],
    ) -> dict[str, str]:
        revision_by_asset: dict[str, str] = {}
        for row in self.rows["assets/assets.jsonl"]:
            value = row.value
            data = self.archive.read(value["path"])
            if len(data) != value["bytes"] or sha256_bytes(data) != value["sha256"]:
                raise RuntimeError(f"asset payload mismatch: {value['path']}")
            asset = self.native_base(
                row,
                record_type="asset",
                stable_key=f"judson:asset:{value['path']}",
            )
            asset.update(
                {
                    "asset_kind": value["kind"],
                    "canonical_path_or_uri": value["path"],
                    "media_type": media_type(value["path"]),
                    "resource_id": self.resource_id,
                    "rights_default_id": value["rights_id"],
                }
            )
            self.add("assets", asset)

            revision_key = f"judson:asset-revision:{value['id']}:{self.target_edition_id}"
            revision = self.generated_base(
                record_type="asset_revision",
                stable_key=revision_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "judson.adapter": {
                        "generated_from_native_asset_id": value["id"],
                        "native_locator": row.locator,
                    }
                },
            )
            revision.update(
                {
                    "asset_id": value["id"],
                    "bytes": value["bytes"],
                    "edition_id": self.target_edition_id,
                    "file_revision_id": target_file_revision_by_actual_path.get(value["path"]),
                    "sha256": value["sha256"],
                    "source_asset_revision_id": None,
                }
            )
            self.add("asset_revisions", revision, generated=True)
            revision_by_asset[value["id"]] = revision["id"]
        return revision_by_asset

    def build_curriculum(self) -> tuple[dict[str, str], list[str]]:
        program_row = self.rows["program/programs.jsonl"][0]
        program = self.native_base(
            program_row,
            record_type="program",
            stable_key="judson:program:bahasa-indonesia-mathematics",
        )
        program.update(
            {
                "curriculum_version": program_row.value["version"],
                "locale": program_row.value["locale"],
                "program_key": "program-matematika-id",
                "rights_id": self.rights_id,
                "title": program_row.value["title"],
            }
        )
        self.add("programs", program)

        course_rows = self.rows["courses/courses.jsonl"]
        code_by_id = {row.value["id"]: row.value["code"] for row in course_rows}
        route_by_course: dict[str, str] = {}
        for order, row in enumerate(sorted(course_rows, key=lambda r: r.value["code"]), start=1):
            value = row.value
            course = self.native_base(
                row,
                record_type="course",
                stable_key=f"judson:course:{value['code']}",
            )
            course.update(
                {
                    "course_key": value["code"],
                    "order_key": f"{order:02d}",
                    "program_id": value["program_id"],
                    "role": value["role"],
                    "prerequisite_course_keys": [
                        code_by_id[item] for item in value["prerequisite_course_ids"]
                    ],
                    "resource_keys": ["R009-JUDSON-AATA"],
                    "scope": value["selection_policy"],
                    "stage": "upper-division undergraduate",
                    "title": value["title"],
                }
            )
            self.add("courses", course)

            route_key = f"judson:route:{value['code']}:{RELEASE_VERSION}"
            route = self.generated_base(
                record_type="route",
                stable_key=route_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "judson.adapter": {
                        "native_course_id": value["id"],
                        "selection_policy": value["selection_policy"],
                    }
                },
            )
            route.update(
                {
                    "course_id": value["id"],
                    "description": value["selection_policy"],
                    "locale": value["locale"],
                    "program_id": value["program_id"],
                    "route_key": value["code"],
                    "route_kind": "canonical_chapter_view",
                    "title": value["title"],
                    "version_label": RELEASE_VERSION,
                }
            )
            self.add("routes", route, generated=True)
            route_by_course[value["id"]] = route["id"]

        for row in self.rows["courses/course-units.jsonl"]:
            value = row.value
            member = self.native_base(
                row,
                record_type="route_member",
                stable_key=f"judson:route-member:{value['course_id']}:{value['sequence']:04d}",
            )
            member.update(
                {
                    "entity_id": value["unit_id"],
                    "inclusion_reason": value["render"],
                    "order_path": f"{value['sequence']:04d}",
                    "ordinal": value["sequence"],
                    "required": value["membership_role"] == "core",
                    "role": value["membership_role"],
                    "route_id": route_by_course[value["course_id"]],
                }
            )
            self.add("route_members", member)

        return route_by_course, list(code_by_id)

    def build_units_and_occurrences(
        self,
        source_file_revision_by_path: dict[str, str],
    ) -> dict[str, str]:
        occurrence_by_unit: dict[str, str] = {}
        for row in self.rows["topology/units.jsonl"]:
            value = row.value
            revision_id = source_file_revision_by_path[value["source_path"]]
            strategy = (
                "native_id"
                if value.get("source_xml_id")
                else "native_label"
                if value.get("source_label")
                else "structural_path"
            )
            profile = self.pretext_profile(
                revision_id=revision_id,
                authority_path=self.source_authority_path(value["source_path"]),
                structural_xpath=value["source_xpath"],
                identity_strategy=strategy,
                native_xml_id=value.get("source_xml_id"),
                label=value.get("source_label"),
                division_kind=value["kind"],
            )
            unit = self.native_base(
                row,
                record_type="unit",
                stable_key=f"judson:unit:{value['id']}",
                profile=profile,
            )
            anchor = (
                value.get("source_xml_id")
                or value.get("source_label")
                or f"{value['source_path']}#{value['source_xpath']}"
            )
            unit.update(
                {
                    "first_edition_id": value["edition_id"],
                    "identity_anchor": anchor,
                    "identity_basis": value["identity_method"],
                    "resource_id": value["resource_id"],
                    "rights_default_id": value["rights_id"],
                    "source_label": value.get("source_label"),
                    "source_local_id": value.get("source_xml_id"),
                    "source_path": value["source_path"],
                    "source_xml_path": value["source_xpath"],
                    "unit_kind": value["kind"],
                }
            )
            self.add("units", unit)

            occurrence_key = f"judson:occurrence:source:{value['id']}:{self.source_edition_id}"
            occurrence_by_unit[value["id"]] = generated_id("occurrence", occurrence_key)

        for row in self.rows["topology/units.jsonl"]:
            value = row.value
            profile = self.pretext_profile(
                revision_id=source_file_revision_by_path[value["source_path"]],
                authority_path=self.source_authority_path(value["source_path"]),
                structural_xpath=value["source_xpath"],
                identity_strategy=(
                    "native_id"
                    if value.get("source_xml_id")
                    else "native_label"
                    if value.get("source_label")
                    else "structural_path"
                ),
                native_xml_id=value.get("source_xml_id"),
                label=value.get("source_label"),
                division_kind=value["kind"],
            )
            occurrence_key = f"judson:occurrence:source:{value['id']}:{self.source_edition_id}"
            occurrence = self.generated_base(
                record_type="occurrence",
                stable_key=occurrence_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "interlanguage.source-profile": profile,
                    "judson.adapter": {"native_unit_id": value["id"]},
                },
            )
            self.profile_count += 1
            occurrence.update(
                {
                    "edition_id": self.source_edition_id,
                    "file_revision_id": source_file_revision_by_path[value["source_path"]],
                    "locale": "en-US",
                    "order_path": f"{value['preorder_index']:08d}",
                    "parent_occurrence_id": occurrence_by_unit.get(value.get("parent_id")),
                    "reader_visibility": "canonical",
                    "sibling_ordinal": value["ordinal"],
                    "source_occurrence_id": None,
                    "subtree_sha256": value["source_c14n_sha256"],
                    "translation_state": "source_authority",
                    "unit_id": value["id"],
                    "xml_path": value["source_xpath"],
                }
            )
            self.add("occurrences", occurrence, generated=True)
        return occurrence_by_unit

    def build_text(
        self,
        source_file_revision_by_path: dict[str, str],
        target_file_revision_by_actual_path: dict[str, str],
    ) -> dict[str, str]:
        disposition_by_segment = {
            row.value["segment_id"]: row
            for row in self.rows["state/segment-dispositions.id-ID.jsonl"]
        }
        source_variant_by_segment: dict[str, str] = {}
        source_row_by_segment: dict[str, NativeRow] = {}

        for row in self.rows["text/segments.en-US.jsonl"]:
            value = row.value
            source_row_by_segment[value["id"]] = row
            profile = self.pretext_profile(
                revision_id=source_file_revision_by_path[value["source_path"]],
                authority_path=self.source_authority_path(value["source_path"]),
                structural_xpath=value["source_xpath"],
                identity_strategy="structural_path",
                division_kind=value["role"],
            )
            extra: dict[str, Any] = {}
            disposition = disposition_by_segment.get(value["id"])
            if disposition is not None:
                extra["judson.segment-disposition"] = self.claim(disposition)
            segment = self.native_base(
                row,
                record_type="segment",
                stable_key=f"judson:segment:{value['id']}",
                profile=profile,
                extra_extensions=extra,
            )
            segment.update(
                {
                    "identity_anchor": f"{value['source_path']}#{value['source_xpath']}:{value['ordinal']}",
                    "ordinal": value["ordinal"],
                    "segment_kind": value["role"],
                    "segmentation_profile": "judson-pretext-xml-block-v1",
                    "unit_id": value["unit_id"],
                }
            )
            self.add("segments", segment)

            variant_key = f"judson:segment-variant:source:{value['id']}:{self.source_edition_id}"
            variant = self.generated_base(
                record_type="segment_variant",
                stable_key=variant_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "interlanguage.source-profile": profile,
                    "judson.adapter": {"native_segment_id": value["id"]},
                },
            )
            self.profile_count += 1
            variant.update(
                {
                    "edition_id": self.source_edition_id,
                    "format": "pretext_xml_fragment",
                    "locale": value["source_locale"],
                    "payload": value["source_fragment_xml"],
                    "payload_sha256": value["source_sha256"],
                    "rights_id": value["rights_id"],
                    "role": value["role"],
                    "segment_id": value["id"],
                    "source_variant_id": None,
                    "translation_state": "source_authority",
                }
            )
            self.add("segment_variants", variant, generated=True)
            source_variant_by_segment[value["id"]] = variant["id"]

        for row in self.rows["text/segments.edition.id-ID.jsonl"]:
            value = row.value
            actual_path = f"src/{value['source_path']}"
            revision_id = target_file_revision_by_actual_path[actual_path]
            profile = self.pretext_profile(
                revision_id=revision_id,
                authority_path=actual_path,
                structural_xpath=value["source_xpath"],
                identity_strategy="target_only_localized_correction",
                division_kind=value["role"],
            )
            segment = self.native_base(
                row,
                record_type="segment",
                stable_key=f"judson:segment:edition-authored:{value['id']}",
                profile=profile,
            )
            segment.update(
                {
                    "identity_anchor": f"{actual_path}#{value['source_xpath']}:{value['ordinal']}",
                    "ordinal": value["ordinal"],
                    "segment_kind": value["role"],
                    "segmentation_profile": "judson-pretext-edition-authored-v1",
                    "unit_id": value["unit_id"],
                }
            )
            self.add("segments", segment)

            variant_key = f"judson:segment-variant:edition-authored:{value['id']}"
            variant = self.generated_base(
                record_type="segment_variant",
                stable_key=variant_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "interlanguage.source-profile": profile,
                    "judson.adapter": {"native_edition_segment_id": value["id"]},
                },
            )
            self.profile_count += 1
            variant.update(
                {
                    "edition_id": self.target_edition_id,
                    "format": "pretext_xml_fragment",
                    "locale": value["content_locale"],
                    "payload": value["source_fragment_xml"],
                    "payload_sha256": value["source_sha256"],
                    "rights_id": value["rights_id"],
                    "role": value["role"],
                    "segment_id": value["id"],
                    "source_variant_id": None,
                    "translation_state": "edition_authored",
                }
            )
            self.add("segment_variants", variant, generated=True)

        for row in self.rows["text/translations.id-ID.jsonl"]:
            value = row.value
            source_row = source_row_by_segment[value["segment_id"]]
            source = source_row.value
            profile = self.pretext_profile(
                revision_id=source_file_revision_by_path[source["source_path"]],
                authority_path=self.source_authority_path(source["source_path"]),
                structural_xpath=source["source_xpath"],
                identity_strategy="structural_path",
                division_kind=source["role"],
            )
            variant = self.native_base(
                row,
                record_type="segment_variant",
                stable_key=f"judson:segment-variant:target:{value['id']}",
                profile=profile,
            )
            variant.update(
                {
                    "edition_id": self.target_edition_id,
                    "format": "pretext_xml_fragment",
                    "locale": value["content_locale"],
                    "payload": (
                        value["target_fragment_xml"]
                        if value["target_fragment_xml"] is not None
                        else source["source_fragment_xml"]
                    ),
                    "payload_sha256": (
                        value["target_sha256"]
                        if value["target_sha256"] is not None
                        else value["source_sha256"]
                    ),
                    "rights_id": source["rights_id"],
                    "role": source["role"],
                    "segment_id": value["segment_id"],
                    "source_variant_id": source_variant_by_segment[value["segment_id"]],
                    "translation_state": value["state"],
                }
            )
            self.add("segment_variants", variant)

            alignment_key = f"judson:alignment:{value['segment_id']}:{value['id']}"
            alignment = self.generated_base(
                record_type="alignment",
                stable_key=alignment_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "judson.adapter": {
                        "native_translation_id": value["id"],
                        "native_locator": row.locator,
                    }
                },
            )
            alignment.update(
                {
                    "alignment_kind": "direct_segment_translation",
                    "assertion_method": "native segment_id and source_sha256 binding",
                    "confidence": "exact",
                    "evidence_locator": row.locator,
                    "source_id": source_variant_by_segment[value["segment_id"]],
                    "source_locale": source["source_locale"],
                    "source_sha256": value["source_sha256"],
                    "target_id": value["id"],
                    "target_locale": value["content_locale"],
                    "target_sha256": (
                        value["target_sha256"]
                        if value["target_sha256"] is not None
                        else value["source_sha256"]
                    ),
                }
            )
            self.add("alignments", alignment, generated=True)

        return source_variant_by_segment

    def build_lexicon(self) -> None:
        term_rows = self.rows["lexicon/terms.id-ID.jsonl"]
        term_by_concept = {row.value["concept_id"]: row.value for row in term_rows}
        dispositions = {
            row.value["term_id"]: row
            for row in self.rows["state/term-dispositions.id-ID.jsonl"]
        }

        for row in self.rows["lexicon/concepts.jsonl"]:
            value = row.value
            term = term_by_concept.get(value["id"])
            concept = self.native_base(
                row,
                record_type="concept",
                stable_key=f"judson:concept:{value['id']}",
            )
            concept.update(
                {
                    "concept_key": term["source_term"] if term else value["id"],
                    "concept_scheme": "judson-explicit-source-term",
                    "definition_segment_id": None,
                    "parent_concept_id": None,
                }
            )
            self.add("concepts", concept)

        for row in term_rows:
            value = row.value
            extra: dict[str, Any] = {}
            disposition = dispositions.get(value["id"])
            if disposition is not None:
                extra["judson.term-disposition"] = self.claim(disposition)
            term = self.native_base(
                row,
                record_type="term",
                stable_key=f"judson:term:{value['id']}",
                extra_extensions=extra,
            )
            notes = value.get("state_reason") or ""
            if disposition is not None:
                notes = disposition.value.get("reason") or notes
            term.update(
                {
                    "concept_id": value["concept_id"],
                    "evidence": "; ".join(value.get("evidence", [])),
                    "notes": notes,
                    "preferred_form": value["preferred"],
                    "register": value["register"],
                    "scope_unit_id": self.root_unit_id,
                    "source_form": value["source_term"],
                    "source_locale": "en-US",
                    "source_term_id": f"judson-source-term:{value['concept_id']}",
                    "target_locale": value["locale"],
                    "term_status": value["state"],
                }
            )
            self.add("terms", term)

            candidates: dict[str, tuple[str, str]] = {}
            for form in value.get("variants", []):
                if form != value["preferred"]:
                    candidates[form] = ("accepted", "native accepted variant")
            for form in value.get("rejected_forms", []):
                if form != value["preferred"] and form not in candidates:
                    candidates[form] = ("rejected", "native rejected form")
            if disposition is not None:
                for form in disposition.value.get("variants", []):
                    if form != value["preferred"]:
                        candidates[form] = (
                            "accepted",
                            disposition.value.get("reason", "native disposition variant"),
                        )
            for form, (kind, rationale) in sorted(candidates.items()):
                stable_key = f"judson:term-variant:{value['id']}:{kind}:{form}"
                variant = self.generated_base(
                    record_type="term_variant",
                    stable_key=stable_key,
                    recorded_at=value["recorded_at"],
                    extensions={"judson.adapter": {"native_term_id": value["id"]}},
                )
                variant.update(
                    {
                        "form": form,
                        "locale": value["locale"],
                        "rationale": rationale,
                        "term_id": value["id"],
                        "variant_kind": kind,
                    }
                )
                self.add("term_variants", variant, generated=True)

        for row in self.rows["lexicon/concept-units.jsonl"]:
            value = row.value
            relation = self.native_base(
                row,
                record_type="relation",
                stable_key=f"judson:concept-unit:{value['id']}",
            )
            relation.update(
                {
                    "assertion_method": value["confidence"],
                    "confidence": value["confidence"],
                    "edition_id": self.source_edition_id,
                    "from_id": value["concept_id"],
                    "ordinal": value["ordinal"],
                    "relation_type": "concept_occurs_in_unit",
                    "source_locator": value["evidence_locator"],
                    "strength": "explicit",
                    "to_id": value["unit_id"],
                }
            )
            self.add("relations", relation)

    def build_relations_and_aliases(self) -> None:
        for row in self.rows["topology/relations.jsonl"]:
            value = row.value
            relation = self.native_base(
                row,
                record_type="relation",
                stable_key=f"judson:relation:{value['id']}",
            )
            relation.update(
                {
                    "assertion_method": value["provenance"],
                    "confidence": value["confidence"],
                    "edition_id": self.source_edition_id,
                    "from_id": value["from_id"],
                    "ordinal": value["ordinal"],
                    "relation_type": value["type"],
                    "source_locator": row.locator,
                    "strength": "curated" if value["provenance"] == "curated" else "derived",
                    "to_id": value["to_id"],
                }
            )
            self.add("relations", relation)

        for row in self.rows["identity/id-map.jsonl"]:
            value = row.value
            alias_value = (
                value.get("source_xml_id")
                or value.get("source_label")
                or f"{value['birth_source_path']}#{value['birth_xpath']}"
            )
            alias = self.native_base(
                row,
                record_type="alias",
                stable_key=f"judson:alias:{value['id']}",
            )
            alias.update(
                {
                    "edition_id": self.source_edition_id,
                    "entity_id": value["unit_id"],
                    "scheme": value["identity_method"],
                    "scope": value["birth_source_path"],
                    "unique_in_scope": True,
                    "value": alias_value,
                }
            )
            self.add("aliases", alias)

    def build_experiments(
        self,
        source_file_revision_by_path: dict[str, str],
    ) -> None:
        for row in self.rows["code/sage-cells.jsonl"]:
            value = row.value
            unit = self.unit_by_id[value["unit_id"]]
            experiment = self.native_base(
                row,
                record_type="experiment",
                stable_key=f"judson:experiment:sage:{value['id']}",
            )
            experiment.update(
                {
                    "edition_id": self.target_edition_id,
                    "expected_output_segment_ids": [],
                    "instruction_segment_ids": [],
                    "invocation": value["toolchain_id"],
                    "kind": "sage",
                    "parameter_segment_ids": [],
                    "resource_id": self.resource_id,
                    "result_mode": value["runtime_validation"],
                    "rights_id": self.rights_id,
                    "runner_asset_revision_ids": [],
                    "source_file_revision_id": source_file_revision_by_path[
                        unit["source_path"]
                    ],
                    "unit_id": value["unit_id"],
                }
            )
            self.add("experiments", experiment)

    def build_corrections_and_qa(self) -> None:
        source_file_sha = {
            row.value["path"]: row.value["sha256"]
            for row in self.rows["authority/source-files.jsonl"]
        }
        target_file_sha = {
            as_target_archive_path(row.value["path"]): row.value["sha256"]
            for row in self.rows["edition/source-deltas.id-ID.jsonl"]
        }
        for row in self.rows["corrections/corrections.jsonl"]:
            value = row.value
            if not value["affected_unit_ids"]:
                raise RuntimeError(f"incomplete native correction: {row.locator}")
            replacement_hash = value.get("target_c14n_sha256")
            original_hash = value.get("authority_c14n_sha256")
            payload_hash_basis = "canonical corrected subtree"
            if replacement_hash is None:
                replacement_hash = target_file_sha.get(f"src/{value['source_path']}")
                original_hash = original_hash or source_file_sha.get(value["source_path"])
                payload_hash_basis = (
                    "whole-file SHA-256 fallback; the native topology correction "
                    "does not assert a subtree hash"
                )
            if replacement_hash is None:
                raise RuntimeError(f"correction has no defensible replacement hash: {row.locator}")
            correction = self.native_base(
                row,
                record_type="correction",
                stable_key=f"judson:correction:{value['id']}",
            )
            correction.update(
                {
                    "affected_id": value["affected_unit_ids"][0],
                    "category": value["classification"],
                    "evidence_locator": value["affected_locator"],
                    "local_state": value["action"],
                    "original_payload_sha256": original_hash,
                    "payload_hash_basis": payload_hash_basis,
                    "rationale": value["reason"],
                    "replacement_payload_sha256": replacement_hash,
                    "source_edition_id": self.source_edition_id,
                    "upstream_disposition": (
                        "high-confidence upstream defect recorded; no contact performed"
                        if value.get("upstream_defect")
                        else "local edition correction; no upstream contact"
                    ),
                    "upstream_url": None,
                }
            )
            self.add("corrections", correction)

        for row in self.rows["qa/qa-events.jsonl"]:
            value = row.value
            witness = value.get("witness", {})
            input_hash = next(
                (
                    item
                    for key, item in sorted(witness.items())
                    if key.endswith("sha256")
                    and isinstance(item, str)
                    and re.fullmatch(r"[0-9a-f]{64}", item)
                ),
                row.sha256,
            )
            event = self.native_base(
                row,
                record_type="qa_event",
                stable_key=f"judson:qa-event:{value['id']}",
            )
            event.update(
                {
                    "input_hash": input_hash,
                    "method": "native deterministic verification event",
                    "qa_type": value["qa_type"],
                    "result": value["result"],
                    "reviewer_kind": "automated",
                    "severity_p1": 0,
                    "severity_p2": 0,
                    "severity_p3": 0,
                    "tool_name": "Judson native backend verifier",
                    "tool_version": "1.0.0",
                    "witness_locator": row.locator,
                }
            )
            self.add("qa_events", event)

    def build_artifacts_and_publication(self) -> dict[str, str]:
        public_asset_by_sha = {
            item["sha256"]: item for item in self.public_evidence["assets"]
        }
        native_artifact_by_sha: dict[str, str] = {}
        for row in self.rows["artifacts/artifacts.jsonl"]:
            value = row.value
            is_tree = value["format"].endswith("tree")
            public_item = public_asset_by_sha.get(value["sha256"])
            public_uri = None
            if public_item is not None:
                public_uri = (
                    self.publication["zenodo"]["record_url"]
                    + "/files/"
                    + public_item["name"]
                    + "?download=1"
                )
            artifact = self.native_base(
                row,
                record_type="artifact",
                stable_key=f"judson:artifact:{value['id']}",
            )
            artifact.update(
                {
                    "artifact_kind": value["format"],
                    "build_receipt": value["command"],
                    "bytes": value["bytes"],
                    "edition_id": value["edition_id"],
                    "locale": value["locale"],
                    "manifest_sha256": value["sha256"] if is_tree else None,
                    "public_uri": public_uri,
                    "sha256": None if is_tree else value["sha256"],
                    "toolchain_id": value.get("toolchain_lock_sha256") or "official-witness",
                    "tree_sha256": value["sha256"] if is_tree else None,
                }
            )
            self.add("artifacts", artifact)
            native_artifact_by_sha[value["sha256"]] = value["id"]

            recipe_key = f"judson:build-recipe:{value['id']}"
            recipe = self.generated_base(
                record_type="build_recipe",
                stable_key=recipe_key,
                recorded_at=value["recorded_at"],
                extensions={
                    "judson.adapter": {
                        "native_artifact_id": value["id"],
                        "native_locator": row.locator,
                    }
                },
            )
            recipe.update(
                {
                    "command": [value["command"]],
                    "edition_id": value["edition_id"],
                    "environment": {
                        key: str(item)
                        for key, item in {
                            "source_date_epoch": value.get("source_date_epoch"),
                            "toolchain_lock_sha256": value.get("toolchain_lock_sha256"),
                        }.items()
                        if item is not None
                    },
                    "input_ids": [value["edition_id"]],
                    "name": f"Judson {value['format']} production witness",
                    "output_ids": [value["id"]],
                    "resource_id": self.resource_id,
                    "verification": {
                        "native_sha256": value["sha256"],
                        "runtime_limitation": value.get("runtime_validation"),
                    },
                    "working_directory": "repo",
                }
            )
            self.add("build_recipes", recipe, generated=True)

        common_artifact_by_name: dict[str, str] = {}
        for item in self.public_evidence["assets"]:
            existing_id = native_artifact_by_sha.get(item["sha256"])
            if existing_id is not None:
                common_artifact_by_name[item["name"]] = existing_id
                continue
            key = f"judson:public-artifact:{RELEASE_VERSION}:{item['name']}"
            artifact = self.generated_base(
                record_type="artifact",
                stable_key=key,
                recorded_at=self.public_evidence["verified_at"],
                status="published",
                extensions={
                    "judson.publication-evidence": {
                        "publication_receipt_sha256": self.public_evidence[
                            "publication_receipt_sha256"
                        ],
                        "release_tag": RELEASE_TAG,
                    }
                },
            )
            artifact.update(
                {
                    "artifact_kind": "published_release_file",
                    "build_receipt": f"00_control/PUBLICATION_RECEIPT_{RELEASE_VERSION}.json",
                    "bytes": item["bytes"],
                    "edition_id": self.target_edition_id,
                    "locale": "id-ID",
                    "manifest_sha256": None,
                    "public_uri": (
                        self.publication["zenodo"]["record_url"]
                        + "/files/"
                        + item["name"]
                        + "?download=1"
                    ),
                    "sha256": item["sha256"],
                    "toolchain_id": "frozen-publication-receipt",
                    "tree_sha256": None,
                }
            )
            self.add("artifacts", artifact, generated=True)
            common_artifact_by_name[item["name"]] = artifact["id"]

        artifact_ids = [
            common_artifact_by_name[item["name"]]
            for item in self.public_evidence["assets"]
        ]
        derivative = self.publication["derivative"]
        publication_targets = [
            ("github", self.publication["release"]["url"]),
            ("zenodo", self.publication["zenodo"]["record_url"]),
        ]
        for kind, uri in publication_targets:
            stable_key = f"judson:release-snapshot:{kind}:{RELEASE_VERSION}"
            snapshot = self.generated_base(
                record_type="release_snapshot",
                stable_key=stable_key,
                recorded_at=self.public_evidence["verified_at"],
                status="published_verified",
                extensions={
                    "judson.publication-evidence": {
                        "publication_receipt_sha256": self.public_evidence[
                            "publication_receipt_sha256"
                        ]
                    }
                },
            )
            snapshot.update(
                {
                    "archive_sha256": EXPECTED_ARCHIVE_SHA256,
                    "artifact_ids": artifact_ids,
                    "commit_sha": derivative["commit"],
                    "edition_id": self.target_edition_id,
                    "immutable": True,
                    "publication_uri": uri,
                    "release_date": self.publication["zenodo"]["published_at"],
                    "release_version": RELEASE_VERSION,
                    "snapshot_kind": kind,
                    "tree_sha": derivative["tree"],
                }
            )
            self.add("release_snapshots", snapshot, generated=True)
        return common_artifact_by_name

    def build_rights_assignments(self) -> None:
        recorded_at = self.rights_row.value["recorded_at"]
        targets = [
            (self.resource_id, "resource_default", 0),
            (self.source_edition_id, "source_edition", 10),
            (self.target_edition_id, "translated_edition", 20),
        ]
        for target_id, role, precedence in targets:
            stable_key = f"judson:rights-assignment:{self.rights_id}:{target_id}"
            assignment = self.generated_base(
                record_type="rights_assignment",
                stable_key=stable_key,
                recorded_at=recorded_at,
                extensions={"judson.adapter": {"native_rights_id": self.rights_id}},
            )
            assignment.update(
                {
                    "assignment_status": "active",
                    "inheritance": "default",
                    "precedence": precedence,
                    "rights_id": self.rights_id,
                    "scope_role": role,
                    "target_id": target_id,
                }
            )
            self.add("rights_assignments", assignment, generated=True)

    def build(self) -> tuple[dict[str, Any], dict[str, Any]]:
        (
            source_file_revision_by_path,
            _source_file_id_by_path,
            target_file_revision_by_actual_path,
        ) = self.build_authority()
        self.build_assets(target_file_revision_by_actual_path)
        self.build_curriculum()
        self.build_units_and_occurrences(source_file_revision_by_path)
        self.build_text(
            source_file_revision_by_path,
            target_file_revision_by_actual_path,
        )
        self.build_lexicon()
        self.build_relations_and_aliases()
        self.build_experiments(source_file_revision_by_path)
        self.build_corrections_and_qa()
        common_artifact_by_name = self.build_artifacts_and_publication()
        self.build_rights_assignments()

        all_native_rows = {
            (row.path, row.row_number)
            for path_rows in self.rows.values()
            for row in path_rows
        }
        if self.claimed_native_rows != all_native_rows:
            missing = sorted(all_native_rows - self.claimed_native_rows)
            extra = sorted(self.claimed_native_rows - all_native_rows)
            raise RuntimeError(
                f"native row mapping is not exact; missing={missing[:10]}, extra={extra[:10]}"
            )

        for table in self.tables:
            self.tables[table].sort(key=lambda item: item["id"])
        dataset = {
            "$schema": "schema/backend-v1.schema.json",
            "dataset_id": generated_id(
                "dataset", "judson:R009:id-ID:common-backend-v1"
            ),
            "dataset_version": RELEASE_VERSION + "+adapter.1",
            "schema_name": COMMON_SCHEMA_NAME,
            "schema_version": COMMON_SCHEMA_VERSION,
            "tables": self.tables,
        }
        return dataset, {
            "common_artifact_by_name": common_artifact_by_name,
            "generated_record_count": len(self.generated_identity_basis),
            "native_rows_losslessly_referenced": len(self.claimed_native_rows),
            "profile_binding_count": self.profile_count,
            "preserved_native_id_count": sum(
                1
                for records in self.tables.values()
                for record in records
                if record["id"] not in self.generated_identity_basis
            ),
        }


def validate_common_dataset(
    dataset: dict[str, Any],
    common_schema: dict[str, Any],
    profile_schema: dict[str, Any],
) -> dict[str, Any]:
    common_validator = Draft202012Validator(
        common_schema, format_checker=FormatChecker()
    )
    errors = sorted(common_validator.iter_errors(dataset), key=lambda err: list(err.path))
    if errors:
        error = errors[0]
        raise RuntimeError(
            "common schema failure at "
            + "/".join(str(part) for part in error.absolute_path)
            + f": {error.message}"
        )

    profile_validator = Draft202012Validator(
        profile_schema, format_checker=FormatChecker()
    )
    profile_count = 0
    records: list[dict[str, Any]] = []
    table_counts: dict[str, int] = {}
    for table, table_records in dataset["tables"].items():
        table_counts[table] = len(table_records)
        records.extend(table_records)
        for record in table_records:
            profile = record.get("extensions", {}).get("interlanguage.source-profile")
            if profile is None:
                continue
            profile_errors = sorted(
                profile_validator.iter_errors(profile), key=lambda err: list(err.path)
            )
            if profile_errors:
                raise RuntimeError(
                    f"source-profile failure for {record['id']}: {profile_errors[0].message}"
                )
            profile_count += 1

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
        raise RuntimeError(f"common global-ID collision: {duplicates[:10]}")
    if any(not UUID5_RE.fullmatch(item) for item in ids):
        raise RuntimeError("common output contains a non-UUIDv5 record ID")

    all_ids = set(ids)

    def check_ref(record: dict[str, Any], field: str) -> None:
        value = record.get(field)
        if value is not None and value not in all_ids:
            raise RuntimeError(
                f"foreign-key failure: {record['record_type']}.{field}={value}"
            )

    def check_refs(record: dict[str, Any], field: str) -> None:
        for value in record.get(field, []):
            if value not in all_ids:
                raise RuntimeError(
                    f"foreign-key failure: {record['record_type']}.{field}[]={value}"
                )

    scalar_refs = {
        "alias": ["edition_id", "entity_id"],
        "alignment": ["source_id", "target_id"],
        "artifact": ["edition_id"],
        "asset": ["resource_id", "rights_default_id"],
        "asset_revision": [
            "asset_id",
            "edition_id",
            "file_revision_id",
            "source_asset_revision_id",
        ],
        "build_recipe": ["edition_id", "resource_id"],
        "concept": ["definition_segment_id", "parent_concept_id"],
        "correction": ["affected_id", "source_edition_id"],
        "course": ["program_id"],
        "edition": ["resource_id", "rights_id", "source_edition_id"],
        "experiment": [
            "edition_id",
            "resource_id",
            "rights_id",
            "source_file_revision_id",
            "unit_id",
        ],
        "file": ["resource_id"],
        "file_revision": ["edition_id", "file_id", "source_revision_id"],
        "occurrence": [
            "edition_id",
            "file_revision_id",
            "parent_occurrence_id",
            "source_occurrence_id",
            "unit_id",
        ],
        "program": ["rights_id"],
        "relation": ["edition_id", "from_id", "to_id"],
        "release_snapshot": ["edition_id"],
        "rights_assignment": ["rights_id", "target_id"],
        "route": ["course_id", "program_id"],
        "route_member": ["entity_id", "route_id"],
        "segment": ["unit_id"],
        "segment_variant": [
            "edition_id",
            "rights_id",
            "segment_id",
            "source_variant_id",
        ],
        "term": ["concept_id", "scope_unit_id"],
        "term_variant": ["term_id"],
        "unit": ["first_edition_id", "resource_id", "rights_default_id"],
    }
    array_refs = {
        "build_recipe": ["input_ids", "output_ids"],
        "experiment": [
            "expected_output_segment_ids",
            "instruction_segment_ids",
            "parameter_segment_ids",
            "runner_asset_revision_ids",
        ],
        "release_snapshot": ["artifact_ids"],
    }
    for record in records:
        check_ref(record, "supersedes_id")
        for field in scalar_refs.get(record["record_type"], []):
            check_ref(record, field)
        for field in array_refs.get(record["record_type"], []):
            check_refs(record, field)

    stream_digest = hashlib.sha256()
    stream_bytes = 0
    for table in sorted(dataset["tables"]):
        for record in dataset["tables"][table]:
            line = canonical_json_bytes(record) + b"\n"
            stream_digest.update(line)
            stream_bytes += len(line)
    dataset_bytes = canonical_json_bytes(dataset)
    return {
        "common_schema_error_count": 0,
        "dataset_canonical_json_bytes": len(dataset_bytes),
        "dataset_canonical_json_sha256": sha256_bytes(dataset_bytes),
        "foreign_key_errors": 0,
        "global_id_collisions": 0,
        "profile_binding_count": profile_count,
        "profile_schema_error_count": 0,
        "record_count": len(records),
        "table_counts": table_counts,
        "virtual_records_jsonl_bytes": stream_bytes,
        "virtual_records_jsonl_sha256": stream_digest.hexdigest(),
    }


def run_virtual_build(
    publication: dict[str, Any],
    public_evidence: dict[str, Any],
    common_schema: dict[str, Any],
    profile_schema: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    with zipfile.ZipFile(SOURCE_ARCHIVE) as archive:
        backend_manifest = json.loads(archive.read(NATIVE_PREFIX + NATIVE_MANIFEST_REL))
        native_schema = json.loads(archive.read(NATIVE_PREFIX + NATIVE_SCHEMA_REL))
        rows, native_validation = load_native_rows(
            archive, backend_manifest, native_schema
        )
        builder = DatasetBuilder(
            rows,
            common_schema,
            profile_schema,
            publication,
            public_evidence,
            archive,
        )
        dataset, mapping = builder.build()
        common_validation = validate_common_dataset(
            dataset, common_schema, profile_schema
        )
    return native_validation, mapping, common_validation


def make_public_artifacts(
    publication: dict[str, Any],
    public_evidence: dict[str, Any],
    common_artifact_by_name: dict[str, str],
) -> list[dict[str, Any]]:
    release_url = publication["release"]["url"]
    zenodo_url = publication["zenodo"]["record_url"]
    return [
        {
            "bytes": item["bytes"],
            "common_artifact_id": common_artifact_by_name[item["name"]],
            "github_uri": release_url.replace("/tag/", "/download/")
            + "/"
            + item["name"],
            "name": item["name"],
            "sha256": item["sha256"],
            "zenodo_uri": zenodo_url + "/files/" + item["name"] + "?download=1",
        }
        for item in public_evidence["assets"]
    ]


def main() -> None:
    required_paths()
    common_schema_raw = COMMON_SCHEMA_PATH.read_bytes()
    profile_schema_raw = PROFILE_SCHEMA_PATH.read_bytes()
    receipt_schema_raw = RECEIPT_SCHEMA_PATH.read_bytes()
    common_schema = json.loads(common_schema_raw)
    profile_schema = json.loads(profile_schema_raw)
    receipt_schema = json.loads(receipt_schema_raw)

    publication, public_evidence = validate_publication_receipt()
    archive_evidence = verify_source_archive()

    first_native, first_mapping, first_common = run_virtual_build(
        publication, public_evidence, common_schema, profile_schema
    )
    second_native, second_mapping, second_common = run_virtual_build(
        publication, public_evidence, common_schema, profile_schema
    )
    if first_native != second_native:
        raise RuntimeError("native validation changed between deterministic runs")
    if first_mapping != second_mapping:
        raise RuntimeError("mapping summary changed between deterministic runs")
    if first_common != second_common:
        raise RuntimeError("common virtual dataset changed between deterministic runs")

    common_schema_sha = sha256_bytes(common_schema_raw)
    profile_schema_sha = sha256_bytes(profile_schema_raw)
    receipt_schema_sha = sha256_bytes(receipt_schema_raw)
    if common_schema_sha != "3de8d107b1c75db0f8d60c42ef7e3488bc3fcc93f72e955def71a771475cf2b2":
        raise RuntimeError("common backend schema is not the frozen v1 schema")
    if profile_schema_sha != "2bb1429c36236329be94d58205b6123a0266a1e111277e3d303692ca8430e271":
        raise RuntimeError("source-format profile is not the frozen v1 schema")

    table_counts = first_common["table_counts"]
    receipt = {
        "coverage": {
            "authority_source_files": 92,
            "common_records": first_common["record_count"],
            "generated_common_ids": first_mapping["generated_record_count"],
            "native_augmentation_rows_folded_losslessly": first_native[
                "augmentation_rows"
            ],
            "native_backend_files": archive_evidence["backend_file_count"],
            "native_jsonl_records": first_native["jsonl_record_count"],
            "native_primary_records": first_native["primary_record_count"],
            "native_rows_losslessly_referenced": first_mapping[
                "native_rows_losslessly_referenced"
            ],
            "preserved_native_ids": first_mapping["preserved_native_id_count"],
            "source_segments": first_native["source_segment_count"],
            "strict_pretext_profile_bindings": first_common[
                "profile_binding_count"
            ],
            "target_translations": first_native["target_translation_count"],
            "translation_states": first_native["translation_state_counts"],
        },
        "credentials_recorded": False,
        "materialization": {
            "common_csv_materialized": False,
            "common_jsonl_materialized": False,
            "decision": "zero-copy virtual dataset; retain the stronger native backend and regenerate the common stream deterministically on demand",
            "native_backend_modified": False,
            "native_csv_projections": "hash, byte, row-count, and package-inventory verified; no common CSV projection emitted",
            "source_or_target_payload_bytes_modified": 0,
        },
        "migration_id": f"judson-id-v1-{RELEASE_VERSION}",
        "migration_mode": "additive zero-copy adapter over a frozen published native backend",
        "public_artifacts": make_public_artifacts(
            publication,
            public_evidence,
            first_mapping["common_artifact_by_name"],
        ),
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": "1.0.0",
        "source": {
            "archive": {
                "bytes": archive_evidence["archive_bytes"],
                "entries": archive_evidence["archive_entries"],
                "name": SOURCE_ARCHIVE_NAME,
                "sha256": archive_evidence["archive_sha256"],
                "uncompressed_bytes": archive_evidence[
                    "archive_uncompressed_bytes"
                ],
            },
            "authority": {
                "closure_manifest_sha256": archive_evidence[
                    "authority_closure_manifest_sha256"
                ],
                "commit": EXPECTED_UPSTREAM_COMMIT,
                "official_repository": "https://github.com/twjudson/aata",
                "tree": EXPECTED_UPSTREAM_TREE,
            },
            "backend_manifest": {
                "bytes": archive_evidence["backend_manifest_bytes"],
                "entries": archive_evidence["backend_manifest_entries"],
                "sha256": archive_evidence["backend_manifest_sha256"],
            },
            "dataset_id": "R009-JUDSON-id-ID",
            "dataset_version": RELEASE_VERSION,
            "locale": "id-ID",
            "native_jsonl": {
                "canonical_primary_records": first_native[
                    "canonical_primary_jsonl"
                ],
                "noncanonical_key_order_augmentation_rows": first_native[
                    "noncanonical_augmentation_rows"
                ],
                "path_framed_bytes": first_native[
                    "jsonl_bytes_with_path_framing"
                ],
                "record_count": first_native["jsonl_record_count"],
                "sha256": first_native["jsonl_stream_sha256"],
            },
            "native_schema_name": "interlanguage.modular",
            "native_schema_version": "1.0.0",
            "package_manifest": {
                "bytes": archive_evidence["package_manifest_bytes"],
                "entries": archive_evidence["package_manifest_entries"],
                "sha256": archive_evidence["package_manifest_sha256"],
            },
            "public_release": {
                "github": public_evidence["github_release"],
                "repository": public_evidence["derivative_repository"],
                "repository_commit": public_evidence["derivative_commit"],
                "repository_tree": public_evidence["derivative_tree"],
                "tag": public_evidence["tag"],
                "tag_object": public_evidence["tag_object"],
                "zenodo_concept_doi": public_evidence["zenodo_concept_doi"],
                "zenodo_doi": public_evidence["zenodo_doi"],
                "zenodo_record": public_evidence["zenodo_record"],
            },
            "publication_receipt": {
                "bytes": public_evidence["publication_receipt_bytes"],
                "path": f"00_control/PUBLICATION_RECEIPT_{RELEASE_VERSION}.json",
                "sha256": public_evidence["publication_receipt_sha256"],
            },
            "scope_note": "This adapter binds only the immutable, anonymously verified 2026.08.21.1 release; it makes no claim about later unpublished lane bytes.",
            "title": "Abstract Algebra: Theory and Applications / Indonesian edition",
            "workflow_id": WORKFLOW_ID,
        },
        "tables": {
            table: {"record_count": table_counts[table]}
            for table in sorted(table_counts)
        },
        "target": {
            "dataset_canonical_json_bytes": first_common[
                "dataset_canonical_json_bytes"
            ],
            "dataset_canonical_json_sha256": first_common[
                "dataset_canonical_json_sha256"
            ],
            "dataset_id": generated_id(
                "dataset", "judson:R009:id-ID:common-backend-v1"
            ),
            "dataset_version": RELEASE_VERSION + "+adapter.1",
            "record_count": first_common["record_count"],
            "schema_name": COMMON_SCHEMA_NAME,
            "schema_sha256": common_schema_sha,
            "schema_version": COMMON_SCHEMA_VERSION,
            "source_format_profile_schema_sha256": profile_schema_sha,
            "virtual_records_jsonl_bytes": first_common[
                "virtual_records_jsonl_bytes"
            ],
            "virtual_records_jsonl_sha256": first_common[
                "virtual_records_jsonl_sha256"
            ],
        },
        "transformation": {
            "adapter_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
            "generated_id_formula": "UUIDv5(7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd, record_type|stable_key)",
            "identity_policy": "all globally unique native UUIDv5 IDs preserved; 250 colliding disposition rows folded by exact frozen row locator and hash; only additive records receive common-namespace UUIDv5 IDs",
            "locale_policy": "locale-neutral segments are distinct from en-US and id-ID segment_variants",
            "mapping": {
                "concept_units": "relations",
                "course_units": "route_members under generated course routes",
                "id_map": "aliases",
                "native_segments": "segments plus generated source variants",
                "sage_cells": "experiments",
                "source_deltas": "target file_revisions",
                "source_files": "files plus generated source file_revisions",
                "translations": "target segment_variants plus generated alignments",
            },
            "native_bytes_policy": "zero-copy references bind every native JSONL row by frozen archive, path, row, byte count, and SHA-256; package and backend manifests bind all non-record files",
            "native_record_ids_changed": 0,
            "source_format_profile": "strict pretext profile v1",
        },
        "validation": {
            "common_schema_errors": first_common["common_schema_error_count"],
            "deterministic_runs": 2,
            "deterministic_virtual_streams_identical": True,
            "foreign_key_errors": first_common["foreign_key_errors"],
            "global_id_collisions": first_common["global_id_collisions"],
            "native_schema_validated_rows": first_native[
                "native_schema_validated_rows"
            ],
            "package_crc_inventory_and_hashes": archive_evidence[
                "zip_crc_and_inventory_result"
            ],
            "payload_hash_errors": 0,
            "profile_schema_errors": first_common["profile_schema_error_count"],
            "public_asset_count": public_evidence["asset_count"],
            "public_asset_total_bytes": public_evidence["asset_total_bytes"],
            "public_assets_local_hash_readback": "pass",
            "receipt_schema_sha256": receipt_schema_sha,
            "result": "pass",
            "source_target_segment_closure": "4466 source segments / 4466 target variants / zero missing or duplicate bindings",
        },
    }

    receipt_errors = sorted(
        Draft202012Validator(
            receipt_schema, format_checker=FormatChecker()
        ).iter_errors(receipt),
        key=lambda err: list(err.path),
    )
    if receipt_errors:
        raise RuntimeError(f"migration receipt schema failure: {receipt_errors[0].message}")

    receipt_bytes = pretty_json_bytes(receipt)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(receipt_bytes)
    reread = OUTPUT_PATH.read_bytes()
    if reread != receipt_bytes:
        raise RuntimeError("migration receipt readback mismatch")
    print(
        json.dumps(
            {
                "common_record_count": first_common["record_count"],
                "generated_common_ids": first_mapping["generated_record_count"],
                "native_jsonl_records": first_native["jsonl_record_count"],
                "output": str(OUTPUT_PATH),
                "preserved_native_ids": first_mapping["preserved_native_id_count"],
                "receipt_bytes": len(receipt_bytes),
                "receipt_sha256": sha256_bytes(receipt_bytes),
                "virtual_records_jsonl_bytes": first_common[
                    "virtual_records_jsonl_bytes"
                ],
                "virtual_records_jsonl_sha256": first_common[
                    "virtual_records_jsonl_sha256"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
