#!/usr/bin/env python3
"""Validate and virtually adapt the complete R012 backend to common v1.

The owner edition exposes 19,048 canonical native records in fourteen primary
JSONL files.  ``exercise_solution_links.jsonl`` is an 82-row byte-identical
projection of rows already present in ``relations.jsonl`` and is verified but
not double-counted.  This adapter leaves every owner byte untouched and creates
exactly one strict common-backend record for every canonical native record.

Each common record embeds the complete canonical native record in a namespaced
extension.  The adapter therefore has an exact reverse extraction while also
exposing the native program, course, resource, editions, units, localized-unit
identities, concepts, segments, Indonesian segment variants, terms, assets,
relations, rights, QA events, artifacts, and corrections through common-v1
tables.  Only the compact migration receipt is written.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_VERSION = "0.1.0"
WORKFLOW = "program-matematika-indonesia/r012-applied-combinatorics-v1-migrator-1.0.0"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
NATIVE_EXTENSION = "interlanguage.r012-applied-combinatorics-native"

EXPECTED_RECORDS = 19_048
EXPECTED_DERIVED_RECORDS = 1
EXPECTED_COMMON_RECORDS = EXPECTED_RECORDS + EXPECTED_DERIVED_RECORDS
EXPECTED_PHYSICAL_ROWS = 19_130
EXPECTED_PROJECTION_ROWS = 82
EXPECTED_EXPORT_MANIFEST_BYTES = 2_170
EXPECTED_EXPORT_MANIFEST_SHA256 = "18f4fa6bf3cb37a5bb908d09b2c41c076eabb2cd36540862147d54b49533351e"
EXPECTED_SUMMARY_BYTES = 6_034
EXPECTED_SUMMARY_SHA256 = "138c1641ffe819269e1291d5dd98eb334ed5b8f4a3f5ec394dcaf56fdbb61117"
EXPECTED_FINAL_VALIDATION_BYTES = 6_664
EXPECTED_FINAL_VALIDATION_SHA256 = "0eb2e1c5215619af147d1ba0b278e944c152fd3337386565f7b70bff054287f1"
EXPECTED_NATIVE_SCHEMA_BYTES = 1_449
EXPECTED_NATIVE_SCHEMA_SHA256 = "1b2f8cd10ed52112a28ed3e33a10fa82a43ac9e1a4ca747d16573ebb67aecaf3"
EXPECTED_GITHUB_RECEIPT_BYTES = 6_857
EXPECTED_GITHUB_RECEIPT_SHA256 = "c57024e889bede0c7f7d41947dc0668a005c977a8d471b48bd3ef98a5c0e553e"
EXPECTED_ZENODO_RECEIPT_BYTES = 2_296
EXPECTED_ZENODO_RECEIPT_SHA256 = "b74c1d59b10cabec8b25318d450ed262b13e1a73ddc20742ce968fe3bf8419d7"
EXPECTED_FIGSHARE_RECEIPT_BYTES = 6_547
EXPECTED_FIGSHARE_RECEIPT_SHA256 = "443d08b394ae4b1fc3fa1f380ac430b0a0fdb579218ba24551bea95438f022a4"

SOURCE_EDITION = "r012-upstream-33b20df670d1"
TARGET_EDITION = "r012-id-draft-20260820"
BOOK_RIGHTS = "r012:rights:book-cc-by-sa-4.0"
SOURCE_COMMIT = "33b20df670d1f8d98266cd2f4a287a79b01649ea"
PUBLIC_COMMIT = "50cb1c9eae0273d7235494c747555be2b4e9f910"
PUBLIC_VERSION = "2026.08.22.2"

PRIMARY_JSONL = (
    "artifacts.jsonl",
    "assets.jsonl",
    "build_targets.jsonl",
    "concepts.jsonl",
    "corrections.jsonl",
    "program_course_resource_edition.jsonl",
    "qa_events.jsonl",
    "relations.jsonl",
    "rights.jsonl",
    "segment_locale_mappings.jsonl",
    "segments.jsonl",
    "terms.jsonl",
    "unit_locale_mappings.jsonl",
    "units.jsonl",
)

EXPECTED_NATIVE_TYPE_COUNTS = {
    "artifact": 10,
    "asset": 406,
    "concept": 701,
    "correction": 354,
    "course": 1,
    "edition": 2,
    "program": 1,
    "qa_event": 171,
    "relation": 6_334,
    "resource": 1,
    "rights": 6,
    "segment": 3_806,
    "segment_locale": 3_806,
    "term": 633,
    "unit": 1_408,
    "unit_locale": 1_408,
}

DIRECT_TYPES = {
    "artifact": ("artifacts", "artifact"),
    "asset": ("assets", "asset"),
    "concept": ("concepts", "concept"),
    "correction": ("corrections", "correction"),
    "course": ("courses", "course"),
    "edition": ("editions", "edition"),
    "program": ("programs", "program"),
    "qa_event": ("qa_events", "qa_event"),
    "relation": ("relations", "relation"),
    "resource": ("resources", "resource"),
    "rights": ("rights", "rights"),
    "segment": ("segments", "segment"),
    "segment_locale": ("segment_variants", "segment_variant"),
    "term": ("terms", "term"),
    "unit": ("units", "unit"),
    "unit_locale": ("aliases", "alias"),
}


def target_for(native: dict) -> tuple[str, str]:
    """Return the honest common table/type for one native record.

    Two native ``asset`` rows are build-only source/executable evidence and
    deliberately have no controlling rights component.  Mapping those rows to
    common ``assets`` would require a false rights default, so they are exposed
    as common artifacts instead.  Their exact native identity remains intact.
    """
    if native["record_type"] == "asset" and native.get("rights_component_id") is None:
        return "artifacts", "artifact"
    return DIRECT_TYPES[native["record_type"]]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical(value).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_file(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path.name}")
    if path.stat().st_size != expected_bytes:
        raise ValueError(f"{label} byte mismatch")
    if sha256_file(path) != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch")


def valid_sha256(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) else None


def valid_commit(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) else None


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def base(record_type: str, stable_key: str, recorded_at: str, status: str, **fields: Any) -> dict:
    return {
        "id": rid(record_type, stable_key),
        "record_type": record_type,
        "recorded_at": recorded_at,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": status or "native-recorded",
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def native_extension(record: dict, source_file: str, source_line: int) -> dict:
    return {
        NATIVE_EXTENSION: {
            "disposition": "direct-lossless-native-extension",
            "native_record": record,
            "native_record_id": record["id"],
            "native_record_sha256": sha256_bytes(canonical_bytes(record)),
            "native_source_file": f"backend/exports/{source_file}",
            "native_source_line": source_line,
            "source_schema": record["schema"],
            "source_schema_version": record["schema_version"],
        }
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_canonical_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    lines: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row_number, line in enumerate(handle, start=1):
            if not line.endswith("\n") or "\r" in line:
                raise ValueError(f"native JSONL newline failure: {path.name}:{row_number}")
            record = json.loads(line)
            if line != canonical(record) + "\n":
                raise ValueError(f"native JSONL is not canonical: {path.name}:{row_number}")
            records.append(record)
            lines.append(line)
    return records, lines


def verify_export_manifest(exports: Path) -> dict[str, dict]:
    manifest_path = exports / "BACKEND_EXPORT_MANIFEST.csv"
    exact_file(
        manifest_path,
        EXPECTED_EXPORT_MANIFEST_BYTES,
        EXPECTED_EXPORT_MANIFEST_SHA256,
        "native export manifest",
    )
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 23:
        raise ValueError("native export manifest row count mismatch")
    by_path: dict[str, dict] = {}
    for row in rows:
        relative = row["path"]
        if relative in by_path:
            raise ValueError(f"duplicate native export-manifest path: {relative}")
        path = exports / relative
        if not path.is_file():
            raise ValueError(f"native export-manifest member absent: {relative}")
        if path.stat().st_size != int(row["bytes"]) or sha256_file(path) != row["sha256"]:
            raise ValueError(f"native export-manifest identity mismatch: {relative}")
        by_path[relative] = row
    expected = set(PRIMARY_JSONL) | {
        "exercise_solution_links.jsonl",
        "AUTHORITY_REPOSITORY_MANIFEST.csv",
        "CONTROL_INPUT_MANIFEST.csv",
        "DECLARED_TARGET_SOURCE_CLOSURE.csv",
        "INCLUDE_EDGES.csv",
        "SOURCE_CLOSURE_MANIFEST.csv",
        "TARGET_ADDITIONS_MANIFEST.csv",
        "TARGET_DERIVATIVE_MANIFEST.csv",
        "summary.json",
    }
    if set(by_path) != expected:
        raise ValueError("native export-manifest member set mismatch")
    return by_path


def verify_native(owner_root: Path) -> tuple[list[dict], dict[str, tuple[str, int]], dict]:
    exports = owner_root / "backend" / "exports"
    manifest_rows = verify_export_manifest(exports)
    summary_path = exports / "summary.json"
    native_schema_path = owner_root / "backend" / "schemas" / "record-envelope.schema.json"
    final_validation_path = owner_root / "qa" / "FINAL_BACKEND_VALIDATION_20260822_2.json"
    github_path = owner_root / "qa" / "GITHUB_PUBLICATION_RECEIPT_20260822_2.json"
    zenodo_path = owner_root / "qa" / "ZENODO_PUBLICATION_RECEIPT_20260822_2.json"
    figshare_path = owner_root / "qa" / "FIGSHARE_READER_PUBLICATION_RECEIPT_20260822_2.json"

    exact_file(summary_path, EXPECTED_SUMMARY_BYTES, EXPECTED_SUMMARY_SHA256, "native summary")
    exact_file(native_schema_path, EXPECTED_NATIVE_SCHEMA_BYTES, EXPECTED_NATIVE_SCHEMA_SHA256, "native record schema")
    exact_file(
        final_validation_path,
        EXPECTED_FINAL_VALIDATION_BYTES,
        EXPECTED_FINAL_VALIDATION_SHA256,
        "native final validation",
    )
    exact_file(github_path, EXPECTED_GITHUB_RECEIPT_BYTES, EXPECTED_GITHUB_RECEIPT_SHA256, "GitHub receipt")
    exact_file(zenodo_path, EXPECTED_ZENODO_RECEIPT_BYTES, EXPECTED_ZENODO_RECEIPT_SHA256, "Zenodo receipt")
    exact_file(figshare_path, EXPECTED_FIGSHARE_RECEIPT_BYTES, EXPECTED_FIGSHARE_RECEIPT_SHA256, "Figshare receipt")

    native_schema = read_json(native_schema_path)
    Draft202012Validator.check_schema(native_schema)
    native_validator = Draft202012Validator(native_schema, format_checker=FormatChecker())

    records: list[dict] = []
    locations: dict[str, tuple[str, int]] = {}
    raw_primary_bytes = bytearray()
    counts: Counter[str] = Counter()
    for filename in PRIMARY_JSONL:
        rows, raw_lines = read_canonical_jsonl(exports / filename)
        for row_number, (record, raw_line) in enumerate(zip(rows, raw_lines, strict=True), start=1):
            errors = sorted(native_validator.iter_errors(record), key=lambda error: list(error.absolute_path))
            if errors:
                first = errors[0]
                raise ValueError(f"native schema failure {filename}:{row_number} {list(first.absolute_path)}: {first.message}")
            if record["schema_version"] != SOURCE_SCHEMA_VERSION:
                raise ValueError(f"native schema-version mismatch: {filename}:{row_number}")
            native_id = record["id"]
            if native_id in locations:
                raise ValueError(f"duplicate canonical native ID: {native_id}")
            locations[native_id] = (filename, row_number)
            records.append(record)
            raw_primary_bytes.extend(raw_line.encode("utf-8"))
            counts[record["record_type"]] += 1

    if len(records) != EXPECTED_RECORDS or len(locations) != EXPECTED_RECORDS:
        raise ValueError("canonical native record-count or ID-count mismatch")
    if dict(sorted(counts.items())) != EXPECTED_NATIVE_TYPE_COUNTS:
        raise ValueError(f"canonical native type-count mismatch: {dict(sorted(counts.items()))}")

    projection, _ = read_canonical_jsonl(exports / "exercise_solution_links.jsonl")
    relation_rows, _ = read_canonical_jsonl(exports / "relations.jsonl")
    expected_projection = [row for row in relation_rows if row.get("relation") in {"hints", "answers", "solves"}]
    if projection != expected_projection or len(projection) != EXPECTED_PROJECTION_ROWS:
        raise ValueError("exercise/solution projection is not the exact ordered relation projection")
    if len(records) + len(projection) != EXPECTED_PHYSICAL_ROWS:
        raise ValueError("physical JSONL row count mismatch")

    summary = read_json(summary_path)
    final_validation = read_json(final_validation_path)
    github = read_json(github_path)
    zenodo = read_json(zenodo_path)
    figshare = read_json(figshare_path)
    if summary.get("status") != "full-corpus-translation-and-release-closure-verified":
        raise ValueError("native summary is not at the completed boundary")
    if summary.get("publication_ready") is not True or summary.get("publication_blocker_count") != 0:
        raise ValueError("native summary is not publication-ready")
    export_counts = final_validation.get("export", {}).get("record_counts", {})
    if (
        final_validation.get("result") != "pass"
        or final_validation.get("publication_ready") is not True
        or export_counts.get("canonical_records") != EXPECTED_RECORDS
        or export_counts.get("canonical_ids") != EXPECTED_RECORDS
        or export_counts.get("physical_jsonl_rows_including_exercise_solution_projection") != EXPECTED_PHYSICAL_ROWS
        or export_counts.get("exercise_solution_projection_rows") != EXPECTED_PROJECTION_ROWS
        or final_validation.get("determinism_replay", {}).get("runs") != 2
        or final_validation.get("determinism_replay", {}).get("byte_identical") is not True
        or final_validation.get("export", {}).get("manifest", {}).get("sha256") != EXPECTED_EXPORT_MANIFEST_SHA256
    ):
        raise ValueError("native final-validation receipt does not close the admitted record boundary")
    if (
        github.get("result") != "pass"
        or github.get("version") != PUBLIC_VERSION
        or github.get("repository", {}).get("head_sha") != PUBLIC_COMMIT
        or github.get("release", {}).get("anonymous_public_byte_readback") != "pass"
        or zenodo.get("result") != "pass"
        or zenodo.get("anonymous_public_byte_readback") != "pass"
        or figshare.get("result") != "pass"
    ):
        raise ValueError("public preservation receipts do not close")

    source_payload = b"".join(
        (canonical(record) + "\n").encode("utf-8") for record in sorted(records, key=lambda row: row["id"])
    )
    diagnostics = {
        "canonical_source_jsonl_bytes": len(source_payload),
        "canonical_source_jsonl_sha256": sha256_bytes(source_payload),
        "native_type_counts": dict(sorted(counts.items())),
        "physical_primary_jsonl_bytes": len(raw_primary_bytes),
        "projection_bytes": (exports / "exercise_solution_links.jsonl").stat().st_size,
        "projection_sha256": sha256_file(exports / "exercise_solution_links.jsonl"),
        "export_manifest_rows": len(manifest_rows),
        "summary": summary,
        "final_validation": final_validation,
        "github": github,
        "zenodo": zenodo,
        "figshare": figshare,
    }
    return records, locations, diagnostics


def media_type_for(native: dict) -> str:
    if native.get("asset_type") == "build-target":
        return "application/vnd.interlanguage.build-target+json"
    locator = (
        native.get("asset_path")
        or native.get("path")
        or native.get("target_asset_path")
        or native.get("source_entry")
        or native.get("publication_path")
        or ""
    )
    suffix_overrides = {
        ".ptx": "application/xml",
        ".tex": "text/x-tex",
        ".md": "text/markdown",
        ".js": "text/javascript",
    }
    suffix = Path(locator).suffix.lower()
    return suffix_overrides.get(suffix) or mimetypes.guess_type(locator)[0] or "application/octet-stream"


def referenced_urns(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_urns(child, (*path, str(index)))
    elif isinstance(value, str) and value.startswith("urn:uuid:"):
        yield path, value


def build_backend(
    records: list[dict],
    locations: dict[str, tuple[str, int]],
    schema: dict,
    diagnostics: dict,
) -> tuple[dict, dict]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}

    def add(table: str, record: dict) -> str:
        tables[table].append(record)
        return record["id"]

    by_native = {record["id"]: record for record in records}
    id_map = {
        native_id: rid(target_for(record)[1], f"r012:native:{native_id}")
        for native_id, record in by_native.items()
    }
    external_reference_map = {
        "curriculum:course:B10": rid("course", "r012:external-prerequisite-course:B10")
    }

    def mapped(native_id: str | None) -> str | None:
        if native_id is None:
            return None
        if native_id in id_map:
            return id_map[native_id]
        if native_id in external_reference_map:
            return external_reference_map[native_id]
        raise ValueError(f"unmapped native reference: {native_id}")

    program_native = next(record for record in records if record["record_type"] == "program")
    resource_native = next(record for record in records if record["record_type"] == "resource")
    source_edition_native = by_native[SOURCE_EDITION]
    target_edition_native = by_native[TARGET_EDITION]
    source_edition_id = mapped(SOURCE_EDITION)
    target_edition_id = mapped(TARGET_EDITION)
    resource_id = mapped(resource_native["id"])
    rights_id = mapped(BOOK_RIGHTS)
    program_id = mapped(program_native["id"])
    root_units = [
        record
        for record in records
        if record["record_type"] == "unit" and record.get("parent_id") is None and record.get("unit_type") == "book"
    ]
    if len(root_units) != 1:
        raise ValueError("native root-book unit is not unique")
    root_unit_id = mapped(root_units[0]["id"])
    github = diagnostics["github"]
    source_archive_asset = next(
        item for item in github["release"]["assets"] if "CORRESPONDING_SOURCE" in item["filename"]
    )

    # One native prerequisite relation points from C70 to the curriculum-wide
    # B10 course, which intentionally lives outside the corpus export.  A
    # minimal, explicitly external course reference closes that real edge
    # without pretending B10 content belongs to R012.
    add(
        "courses",
        base(
            "course",
            "r012:external-prerequisite-course:B10",
            program_native["recorded_at"],
            "external-reference",
            course_key="B10",
            curriculum_source_locator="backend/exports/program_course_resource_edition.jsonl#prerequisite_course_ids",
            curriculum_source_sha256=EXPECTED_EXPORT_MANIFEST_SHA256,
            order_key="B10",
            outcome="",
            prerequisite_course_keys=[],
            program_id=program_id,
            resource_keys=[],
            role="external-prerequisite-reference",
            scope="",
            stage="B",
            title="",
            extensions={
                "interlanguage.r012-applied-combinatorics-derived": {
                    "native_external_id": "curriculum:course:B10",
                    "purpose": "Close the explicit native C70 prerequisite edge without claiming B10 corpus content inside R012.",
                }
            },
        ),
    )

    for native in records:
        native_type = native["record_type"]
        table, common_type = target_for(native)
        stable_key = f"r012:native:{native['id']}"
        common = base(common_type, stable_key, native["recorded_at"], native["status"])
        source_file, source_line = locations[native["id"]]
        common["extensions"] = native_extension(native, source_file, source_line)
        common["supersedes_id"] = mapped(native.get("supersedes"))

        if native_type == "program":
            common.update(
                curriculum_version=native.get("program_local_id") or "math-curriculum-id",
                locale=native.get("locale") or "id-ID",
                program_key=native.get("program_local_id") or native["id"],
                rights_id=rights_id,
                title=native.get("title") or "",
            )
        elif native_type == "course":
            common.update(
                course_key=native.get("course_local_id") or native["id"],
                curriculum_source_locator="backend/exports/program_course_resource_edition.jsonl",
                curriculum_source_sha256=EXPECTED_EXPORT_MANIFEST_SHA256,
                order_key=native.get("course_local_id") or native["id"],
                outcome=native.get("outcome") or "",
                prerequisite_course_keys=native.get("prerequisite_course_ids") or [],
                program_id=program_id,
                resource_keys=[resource_native.get("resource_id") or "R012"],
                role="curriculum-course",
                scope=native.get("scope") or "",
                stage=native.get("stage") or "",
                title=native.get("title") or "",
            )
        elif native_type == "resource":
            authors = native.get("authors") or []
            common.update(
                authority_policy=f"Official repository frozen at commit {SOURCE_COMMIT}",
                creator_name="; ".join(authors) if isinstance(authors, list) else str(authors),
                official_reader=native.get("reader"),
                official_repository=native.get("repository") or "",
                original_title=native.get("title") or "",
                resource_key=native.get("resource_id") or "R012",
                work_type="open textbook",
            )
        elif native_type == "edition":
            if native["id"] == SOURCE_EDITION:
                common.update(
                    archive_sha256=native.get("archive_sha256"),
                    commit_sha=native["commit"],
                    edition_kind="source-snapshot",
                    locale=native["locale"],
                    release_date=native.get("commit_timestamp", "")[:10] or None,
                    resource_id=resource_id,
                    rights_id=rights_id,
                    source_edition_id=None,
                    tree_sha=native.get("tree"),
                    vcs_ref=native.get("branch") or SOURCE_COMMIT,
                    vcs_type="git",
                    version_label=SOURCE_COMMIT[:12],
                )
            elif native["id"] == TARGET_EDITION:
                common.update(
                    archive_sha256=source_archive_asset["sha256"],
                    commit_sha=PUBLIC_COMMIT,
                    edition_kind="translated-derivative",
                    locale=native["locale"],
                    release_date="2026-08-22",
                    resource_id=resource_id,
                    rights_id=rights_id,
                    source_edition_id=source_edition_id,
                    tree_sha=None,
                    vcs_ref=PUBLIC_VERSION,
                    vcs_type="git",
                    version_label=PUBLIC_VERSION,
                )
                common["extensions"][NATIVE_EXTENSION]["public_capture"] = {
                    "github_commit": PUBLIC_COMMIT,
                    "github_release": github["release"]["url"],
                    "source_archive_sha256": source_archive_asset["sha256"],
                }
            else:
                raise ValueError(f"unexpected native edition: {native['id']}")
        elif native_type == "unit":
            common.update(
                first_edition_id=mapped(native["edition_id"]),
                identity_anchor=native.get("source_local_id") or native.get("source_xpath") or native["id"],
                identity_basis="native-pretext-xml-id" if native.get("source_local_id") else "native-source-path-xpath",
                resource_id=resource_id,
                rights_default_id=mapped(native["rights_component_id"]),
                source_label=native.get("title"),
                source_local_id=native.get("source_local_id"),
                source_path=native.get("source_path") or "",
                source_xml_path=native.get("source_xpath"),
                unit_kind=native.get("unit_type") or "unit",
            )
        elif native_type == "unit_locale":
            common.update(
                edition_id=mapped(native["target_edition_id"]),
                entity_id=mapped(native["source_unit_id"]),
                scheme="r012-unit-locale-native-id",
                scope=native.get("target_path") or "target-edition",
                unique_in_scope=True,
                value=native["id"],
            )
        elif native_type == "concept":
            common.update(
                concept_key=native.get("source_label") or native["id"],
                concept_scheme="r012-applied-combinatorics",
                definition_segment_id=None,
                parent_concept_id=None,
            )
        elif native_type == "segment":
            common.update(
                identity_anchor=native.get("source_xpath") or native["id"],
                ordinal=int(native.get("order") or 0),
                segment_kind=native.get("segment_type") or "segment",
                segmentation_profile="r012-pretext-segment-v1",
                unit_id=mapped(native["unit_id"]),
            )
        elif native_type == "segment_locale":
            payload = native.get("target_xml")
            if not isinstance(payload, str):
                payload = native.get("target_text")
            if not isinstance(payload, str):
                raise ValueError(f"localized segment has no string payload: {native['id']}")
            common.update(
                edition_id=mapped(native["target_edition_id"]),
                format="application/pretext+xml",
                locale=native["locale"],
                payload=payload,
                payload_sha256=sha256_bytes(payload.encode("utf-8")),
                rights_id=mapped(native["rights_component_id"]),
                role="translation",
                segment_id=mapped(native["source_segment_id"]),
                source_variant_id=None,
                translation_state=native["translation_state"],
            )
        elif native_type == "term":
            common.update(
                concept_id=mapped(native["concept_id"]),
                evidence=str(native.get("evidence") or ""),
                notes=native.get("scope") or "",
                preferred_form=native.get("preferred_term") or "",
                register=native.get("register") or "",
                scope_unit_id=root_unit_id,
                source_form="",
                source_locale="und",
                source_term_id=native["id"],
                target_locale=native.get("locale") or "id-ID",
                term_status=native["status"],
            )
            common["extensions"][NATIVE_EXTENSION]["source_form_disposition"] = (
                "The native glossary has no separate source-form field; common source_form is the empty sentinel and must not be interpreted as a witnessed English term."
            )
        elif native_type == "asset":
            if native.get("rights_component_id") is None:
                common.update(
                    artifact_kind=native.get("asset_type") or "build-evidence",
                    build_receipt="native build-only evidence; external dependency payloads not bundled",
                    bytes=int(native["bytes"]),
                    edition_id=mapped(native["edition_id"]),
                    locale=native.get("locale") or "zxx",
                    manifest_sha256=None,
                    public_uri=None,
                    sha256=valid_sha256(native.get("sha256")),
                    toolchain_id=str(native.get("dependency") or "native-r012-build-evidence"),
                    tree_sha256=None,
                )
                common["extensions"][NATIVE_EXTENSION]["common_table_disposition"] = (
                    "Mapped to artifact, not asset: the native row intentionally has no controlling rights component, so a common asset rights_default_id cannot be asserted."
                )
            else:
                locator = (
                    native.get("asset_path")
                    or native.get("path")
                    or native.get("target_asset_path")
                    or native.get("source_entry")
                    or native.get("publication_path")
                    or native["id"]
                )
                common.update(
                    asset_kind=native.get("asset_type") or "asset",
                    canonical_path_or_uri=locator,
                    media_type=media_type_for(native),
                    resource_id=resource_id,
                    rights_default_id=mapped(native["rights_component_id"]),
                )
        elif native_type == "relation":
            locator = {
                key: native[key]
                for key in ("authority", "source_path", "source_ref", "source_xpath", "target_ref")
                if key in native
            }
            common.update(
                assertion_method="explicit-owner-validated-native-relation",
                confidence="owner-validated",
                edition_id=mapped(native.get("edition_id")),
                from_id=mapped(native["source_id"]),
                ordinal=0,
                relation_type=native["relation"],
                source_locator=canonical(locator) if locator else "",
                strength="explicit",
                to_id=mapped(native["target_id"]),
            )
            common["extensions"][NATIVE_EXTENSION]["ordinal_disposition"] = (
                "The native relation has no semantic ordinal; common ordinal 0 is an unordered sentinel."
            )
        elif native_type == "rights":
            evidence = native.get("evidence")
            evidence_payload = canonical(evidence if evidence is not None else native)
            creators = native.get("creators") or []
            attribution = "; ".join(creators) if creators else native.get("copyright_notice") or ""
            common.update(
                assertion_status=native.get("component_status") or native.get("component_audit_state") or "native-recorded",
                attribution=attribution,
                authority=evidence_payload,
                change_notice="required" if native.get("change_notice_required") else "not stated by native record",
                license_expression=native.get("license_control_expression") or native.get("license") or "NOASSERTION",
                nonendorsement="required" if native.get("non_endorsement_required") else "not stated by native record",
                notice_locator=f"backend/exports/rights.jsonl#{native['id']}",
                notice_sha256=sha256_bytes(evidence_payload.encode("utf-8")),
                source_component_id=native.get("component_control_id") or native["id"],
                third_party_status=native.get("component_status") or "native-recorded",
            )
            common["extensions"][NATIVE_EXTENSION]["notice_hash_basis"] = "canonical UTF-8 bytes of the native evidence field"
        elif native_type == "qa_event":
            metrics = native.get("metrics") or {}
            common.update(
                input_hash=sha256_bytes(canonical_bytes(native)),
                method=native.get("qa_type") or "native-owner-QA",
                qa_type=native.get("qa_type") or "native-owner-QA",
                result=native.get("result") or native["status"],
                reviewer_kind="owner-lane-machine-validation",
                severity_p1=int(metrics.get("severity_p1", 0)),
                severity_p2=int(metrics.get("severity_p2", 0)),
                severity_p3=int(metrics.get("severity_p3", 0)),
                tool_name=native.get("workflow") or "codex-applied-combinatorics-id",
                tool_version=native.get("schema_version") or SOURCE_SCHEMA_VERSION,
                witness_locator=str(native.get("witness") or native.get("build_log") or "backend/exports/qa_events.jsonl"),
            )
            common["extensions"][NATIVE_EXTENSION]["severity_disposition"] = (
                "Zero denotes absence of native severity-count fields, not an independent re-review finding."
            )
        elif native_type == "artifact":
            artifact_bytes = native.get("bytes")
            if artifact_bytes is None:
                artifact_bytes = native.get("output_bytes") or native.get("manifest_payload_bytes")
            common.update(
                artifact_kind=native.get("artifact_type") or "artifact",
                build_receipt=str(native.get("build_log") or "native-r012-artifact-record"),
                bytes=int(artifact_bytes) if artifact_bytes is not None else None,
                edition_id=mapped(native["edition_id"]),
                locale=native.get("locale") or "und",
                manifest_sha256=valid_sha256(native.get("output_manifest_sha256")),
                public_uri=None,
                sha256=valid_sha256(native.get("sha256")),
                toolchain_id=str(native.get("toolchain") or "native-r012-artifact-record"),
                tree_sha256=None,
            )
        elif native_type == "correction":
            affected = native.get("affected_unit_ids") or ([native["affected_unit"]] if native.get("affected_unit") else [])
            target_sha = valid_sha256(native.get("target_file_sha256"))
            if target_sha is None:
                raise ValueError(f"native correction lacks target-file SHA-256: {native['id']}")
            common.update(
                affected_id=mapped(affected[0]) if affected else root_unit_id,
                binding_status=None,
                category=native.get("severity") or "native-correction",
                evidence_locator=canonical(
                    {
                        key: native[key]
                        for key in ("evidence", "source_locator", "source_path")
                        if key in native
                    }
                ),
                local_state=native["status"],
                original_payload_sha256=valid_sha256(native.get("source_file_sha256")),
                payload_hash_basis="native source_file_sha256 and target_file_sha256 fields",
                rationale="; ".join(
                    value for value in (native.get("summary"), native.get("target_action")) if value
                ),
                replacement_payload_sha256=target_sha,
                source_claim_id=None,
                source_edition_id=mapped(native["edition_id"]),
                source_record_id=None,
                upstream_disposition=native.get("upstream_disposition") or "not-submitted",
                upstream_url=None,
            )
        else:
            raise ValueError(f"unhandled native type: {native_type}")

        if common["id"] != id_map[native["id"]]:
            raise ValueError(f"identity derivation mismatch: {native['id']}")
        add(table, common)

    for rows in tables.values():
        rows.sort(key=lambda record: record["id"])
    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rid("dataset", "r012-applied-combinatorics-id-complete"),
        "dataset_version": f"r012-{PUBLIC_VERSION}+interlanguage-v1",
        "tables": dict(sorted(tables.items())),
    }

    recovered: list[dict] = []
    recovered_ids: set[str] = set()
    for rows in tables.values():
        for common in rows:
            payload = common.get("extensions", {}).get(NATIVE_EXTENSION)
            if payload is None:
                continue
            native = payload["native_record"]
            if native["id"] != payload["native_record_id"]:
                raise ValueError("native reverse identity mismatch")
            if sha256_bytes(canonical_bytes(native)) != payload["native_record_sha256"]:
                raise ValueError(f"native reverse checksum mismatch: {native['id']}")
            if native["id"] in recovered_ids:
                raise ValueError(f"native record recovered more than once: {native['id']}")
            recovered_ids.add(native["id"])
            recovered.append(native)
    expected_recovery = sorted(records, key=lambda record: record["id"])
    if sorted(recovered, key=lambda record: record["id"]) != expected_recovery:
        raise ValueError("exact native reverse extraction failed")

    mapping_payload = b"".join(
        f"{native_id}\t{id_map[native_id]}\n".encode("utf-8") for native_id in sorted(id_map)
    )
    mapping_counts = Counter(target_for(record)[0] for record in records)
    return backend, {
        "exact_reverse_extraction": len(recovered),
        "native_id_mapping_bytes": len(mapping_payload),
        "native_id_mapping_sha256": sha256_bytes(mapping_payload),
        "native_to_common_table_counts": dict(sorted(mapping_counts.items())),
    }


def validate_backend(backend: dict, schema: dict) -> dict:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(backend),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"common schema failure {list(first.absolute_path)}: {first.message}")
    records = sorted(
        [record for rows in backend["tables"].values() for record in rows],
        key=lambda record: (record["record_type"], record["id"]),
    )
    ids = [record["id"] for record in records]
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate common IDs: {duplicates[:10]}")
    known = set(ids)
    dangling = []
    for record in records:
        for field_path, value in referenced_urns(record):
            if field_path == ("id",):
                continue
            if value not in known:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling[:10]}")
    payload = b"".join((canonical(record) + "\n").encode("utf-8") for record in records)
    table_hashes = {}
    for name, rows in backend["tables"].items():
        table_payload = b"".join((canonical(row) + "\n").encode("utf-8") for row in rows)
        table_hashes[name] = {
            "records": len(rows),
            "virtual_jsonl_bytes": len(table_payload),
            "virtual_jsonl_sha256": sha256_bytes(table_payload),
        }
    return {
        "record_count": len(records),
        "table_count": len(backend["tables"]),
        "nonempty_table_count": sum(bool(rows) for rows in backend["tables"].values()),
        "table_counts": {name: len(rows) for name, rows in backend["tables"].items()},
        "table_hashes": table_hashes,
        "global_unique_ids": len(known),
        "foreign_key_closure": "pass",
        "strict_schema": "pass",
        "virtual_records_jsonl_bytes": len(payload),
        "virtual_records_jsonl_sha256": sha256_bytes(payload),
    }


def artifact(root: Path, path: Path, status: str, **fields: Any) -> dict:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "status": status,
        **fields,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--receipt-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    central_root = Path(__file__).resolve().parent.parent
    owner_root = args.corpus_root.resolve()
    schema_path = args.schema.resolve()
    receipt_schema_path = args.receipt_schema.resolve()
    output_path = args.output_receipt.resolve()
    try:
        output_path.relative_to(central_root)
    except ValueError as error:
        raise ValueError("the adapter may write only inside the central repository") from error
    if owner_root == central_root or output_path.is_relative_to(owner_root):
        raise ValueError("the owner lane is read-only")

    schema = read_json(schema_path)
    receipt_schema = read_json(receipt_schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(receipt_schema)

    first_records, first_locations, native = verify_native(owner_root)
    first_backend, first_mapping = build_backend(first_records, first_locations, schema, native)
    first_validation = validate_backend(first_backend, schema)
    if first_validation["record_count"] != EXPECTED_COMMON_RECORDS:
        raise ValueError("common target record count mismatch")

    second_records, second_locations, second_native = verify_native(owner_root)
    second_backend, second_mapping = build_backend(second_records, second_locations, schema, second_native)
    second_validation = validate_backend(second_backend, schema)
    first_bytes = canonical_bytes(first_backend)
    second_bytes = canonical_bytes(second_backend)
    if first_bytes != second_bytes or first_validation != second_validation or first_mapping != second_mapping:
        raise ValueError("two independent common-backend assemblies are not byte-identical")

    export_manifest_path = owner_root / "backend" / "exports" / "BACKEND_EXPORT_MANIFEST.csv"
    summary_path = owner_root / "backend" / "exports" / "summary.json"
    native_schema_path = owner_root / "backend" / "schemas" / "record-envelope.schema.json"
    final_validation_path = owner_root / "qa" / "FINAL_BACKEND_VALIDATION_20260822_2.json"
    github_path = owner_root / "qa" / "GITHUB_PUBLICATION_RECEIPT_20260822_2.json"
    zenodo_path = owner_root / "qa" / "ZENODO_PUBLICATION_RECEIPT_20260822_2.json"
    figshare_path = owner_root / "qa" / "FIGSHARE_READER_PUBLICATION_RECEIPT_20260822_2.json"

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "r012-applied-combinatorics-id-to-v1",
        "migration_mode": "lossless additive one-common-record-per-native-record adapter",
        "source": {
            "dataset_id": "R012/r012-upstream-33b20df670d1",
            "dataset_version": PUBLIC_VERSION,
            "schema_name": "modular-translation-backend record-envelope family",
            "schema_version": SOURCE_SCHEMA_VERSION,
            "resource_id": "R012",
            "authority_commit": SOURCE_COMMIT,
            "canonical_record_count": EXPECTED_RECORDS,
            "canonical_id_count": EXPECTED_RECORDS,
            "physical_jsonl_rows_including_projection": EXPECTED_PHYSICAL_ROWS,
            "exercise_solution_projection_rows": EXPECTED_PROJECTION_ROWS,
            "canonical_source_records_jsonl_bytes": native["canonical_source_jsonl_bytes"],
            "canonical_source_records_jsonl_sha256": native["canonical_source_jsonl_sha256"],
            "primary_jsonl_bytes": native["physical_primary_jsonl_bytes"],
            "native_type_counts": native["native_type_counts"],
            "export_manifest_path": "backend/exports/BACKEND_EXPORT_MANIFEST.csv",
            "export_manifest_bytes": export_manifest_path.stat().st_size,
            "export_manifest_sha256": sha256_file(export_manifest_path),
            "summary_path": "backend/exports/summary.json",
            "summary_bytes": summary_path.stat().st_size,
            "summary_sha256": sha256_file(summary_path),
            "native_schema_path": "backend/schemas/record-envelope.schema.json",
            "native_schema_bytes": native_schema_path.stat().st_size,
            "native_schema_sha256": sha256_file(native_schema_path),
            "final_validation_path": "qa/FINAL_BACKEND_VALIDATION_20260822_2.json",
            "final_validation_bytes": final_validation_path.stat().st_size,
            "final_validation_sha256": sha256_file(final_validation_path),
            "native_determinism_runs": 2,
            "native_determinism_result": "byte-identical",
        },
        "target": {
            "dataset_id": first_backend["dataset_id"],
            "dataset_version": first_backend["dataset_version"],
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "schema_path": "schemas/backend-v1.schema.json",
            "schema_bytes": schema_path.stat().st_size,
            "schema_sha256": sha256_file(schema_path),
            "record_count": first_validation["record_count"],
            "virtual_backend_json_bytes": len(first_bytes),
            "virtual_backend_json_sha256": sha256_bytes(first_bytes),
            "virtual_records_jsonl_bytes": first_validation["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
        },
        "transformation": {
            "classification": "additive reversible adapter",
            "common_identity_namespace": str(NAMESPACE),
            "common_identity_formula": "UUIDv5(namespace, record_type|r012:native:<native-id>)",
            "canonical_native_records_consumed": EXPECTED_RECORDS,
            "common_records_emitted": first_validation["record_count"],
            "derived_external_reference_records": EXPECTED_DERIVED_RECORDS,
            "native_ids_preserved_in_namespaced_extensions": EXPECTED_RECORDS,
            "native_payloads_preserved_byte-equivalently": EXPECTED_RECORDS,
            "changed_native_payload_fields": 0,
            "dropped_native_records": 0,
            "double_counted_projection_rows": 0,
            "projection_rows_verified_not_migrated_twice": EXPECTED_PROJECTION_ROWS,
            "exact_reverse_extraction": first_mapping["exact_reverse_extraction"],
            "native_id_mapping_bytes": first_mapping["native_id_mapping_bytes"],
            "native_id_mapping_sha256": first_mapping["native_id_mapping_sha256"],
            "native_to_common_table_counts": first_mapping["native_to_common_table_counts"],
        },
        "validation": {
            "result": "pass",
            "native_manifest_closure": "pass",
            "native_envelope_schema_rows": EXPECTED_RECORDS,
            "native_unique_ids": EXPECTED_RECORDS,
            "native_projection_identity": "pass",
            "native_two_clean_full_surface_replays": 2,
            "strict_common_backend_schema": "pass",
            "global_unique_common_ids": first_validation["global_unique_ids"],
            "foreign_key_closure": first_validation["foreign_key_closure"],
            "lossless_reverse_records": first_mapping["exact_reverse_extraction"],
            "two_independent_common_assemblies": "byte-identical",
            "public_preservation_receipts": "pass",
        },
        "coverage": {
            "native_records": EXPECTED_RECORDS,
            "target_records": first_validation["record_count"],
            "direct_record_coverage": "19048/19048",
            "derived_external_reference_records": EXPECTED_DERIVED_RECORDS,
            "source_and_target_segment_payload_identity": "preserved in exact native extensions; Indonesian target payload additionally exposed as common segment_variant",
            "units": EXPECTED_NATIVE_TYPE_COUNTS["unit"],
            "localized_unit_identities": EXPECTED_NATIVE_TYPE_COUNTS["unit_locale"],
            "segments": EXPECTED_NATIVE_TYPE_COUNTS["segment"],
            "localized_segments": EXPECTED_NATIVE_TYPE_COUNTS["segment_locale"],
            "relations": EXPECTED_NATIVE_TYPE_COUNTS["relation"],
            "exercise_solution_projection": "verified as a noncanonical projection of relations.jsonl",
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "mode": "virtual deterministic reconstruction",
            "target_materialized": False,
            "reason": "The exact admitted owner export plus this deterministic reversible adapter reconstructs the strict common backend twice without a redundant copy.",
            "owner_lane_modified": False,
            "adapter_script": "scripts/migrate-applied-combinatorics-backend-v1.py",
        },
        "public_artifacts": [
            artifact(
                owner_root,
                github_path,
                native["github"]["result"],
                release_url=native["github"]["release"]["url"],
                release_version=PUBLIC_VERSION,
                commit_sha=PUBLIC_COMMIT,
                anonymous_public_byte_readback=native["github"]["release"]["anonymous_public_byte_readback"],
            ),
            artifact(
                owner_root,
                zenodo_path,
                native["zenodo"]["result"],
                record=native["zenodo"]["record"],
                version_doi=native["zenodo"]["version_doi"],
                anonymous_public_byte_readback=native["zenodo"]["anonymous_public_byte_readback"],
            ),
            artifact(
                owner_root,
                figshare_path,
                native["figshare"]["result"],
                version_doi=native["figshare"]["figshare"]["doi"],
                anonymous_public_byte_readback=native["figshare"]["figshare"]["anonymous_public_byte_readback"],
            ),
        ],
        "credentials_recorded": False,
    }

    receipt_errors = sorted(
        Draft202012Validator(receipt_schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda error: list(error.absolute_path),
    )
    if receipt_errors:
        first = receipt_errors[0]
        raise ValueError(f"migration receipt schema failure {list(first.absolute_path)}: {first.message}")

    forbidden = "".join(chr(code) for code in (70, 108, 111, 114, 105, 115)).casefold()
    receipt_payload = canonical(receipt).casefold()
    if forbidden in receipt_payload:
        raise ValueError("private-name marker found in portable migration receipt")
    write_json(output_path, receipt)
    print(
        canonical(
            {
                "common_records": first_validation["record_count"],
                "foreign_key_closure": first_validation["foreign_key_closure"],
                "native_records": EXPECTED_RECORDS,
                "output_receipt": output_path.relative_to(central_root).as_posix(),
                "receipt_bytes": output_path.stat().st_size,
                "receipt_sha256": sha256_file(output_path),
                "result": "pass",
                "strict_schema": first_validation["strict_schema"],
                "two_run_identity": "byte-identical",
                "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
            }
        )
    )


if __name__ == "__main__":
    main()
