#!/usr/bin/env python3
"""Losslessly adapt the frozen complete R017/O018 Book 1 backend to common v1.

The owner lane remains read-only.  This adapter binds the exact id.5 native
backend, validates its schema and complete 32-file deterministic export, and
creates one strict common-v1 record for every native record.  Each direct
record carries the complete canonical native record in a namespaced extension,
so reverse extraction is exact.  Source and target text that exists in a
native combined segment is additionally exposed as a common segment_variant;
those variants are additive projections and are never counted as native rows.

Only the compact migration receipt is materialized.  The common backend is
assembled twice in memory and must be byte-identical on both independent runs.
"""

from __future__ import annotations

import argparse
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
SOURCE_SCHEMA_NAME = "interlanguage.modular-backend"
SOURCE_SCHEMA_VERSION = "0.1.0"
WORKFLOW = "program-matematika-indonesia/o018-c130-v1-migrator-1.0.0"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
NATIVE_EXTENSION = "interlanguage.o018-c130-r017-book1-native"
DERIVED_EXTENSION = "interlanguage.o018-c130-derived"

PUBLIC_VERSION = "2026.08.23-id.5"
PUBLIC_COMMIT = "a639b69cf84c4d4f60f7dcdb62dbeb5cfb153adc"
PUBLIC_TREE = "1ab559b3540d9362bc0333caf017acd9fe540a9c"
ZENODO_RECORD = "https://zenodo.org/records/22070653"
ZENODO_DOI = "10.5281/zenodo.22070653"
GITHUB_REPOSITORY = "https://github.com/KokunoYumeto/open-optimization-or-book-id"
GITHUB_RELEASE = f"{GITHUB_REPOSITORY}/releases/tag/v{PUBLIC_VERSION}"

R017_RESOURCE = "resource.r017.open-optimization-book"
O018_RESOURCE = "resource.o018.open-solver-lab"
OOOR_EXAMPLES_RESOURCE = "resource.external.open-optimization-or-examples"
PYOMO_GALLERY_RESOURCE = "resource.external.pyomo-gallery"
R017_SOURCE_EDITION = "edition.r017.upstream.1745df89"
R017_TARGET_EDITION = "edition.r017.id-id.draft"
O018_TARGET_EDITION = "edition.o018.id-id.draft"
OOOR_EXAMPLES_EDITION = "edition.external.ooor-examples.b924d2fe"
PYOMO_GALLERY_EDITION = "edition.external.pyomo-gallery.0c00b584"
R017_ROOT_UNIT = "unit.r017.book1"
R017_CONTENT_RIGHTS = "rights.r017.content"

EXPECTED_SOURCE_FILES = {
    "backend/dist/backend-v0.json": (
        26_022_240,
        "7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804",
    ),
    "backend/dist/manifest.json": (
        4_853,
        "f800590f07fafa47c7eb900dddc8cf99bbf5cb892218fa4ab1722677b7b2efa4",
    ),
    "backend/dist/SHA256SUMS.txt": (
        2_623,
        "1dabfdb58c910fc5c1e659356361c51056c6084a214f7b20583a42e9750e6515",
    ),
    "backend/schema/modular-backend-v0.schema.json": (
        12_923,
        "f786a22f386f0fead99a6788c7c7d76396739aeeb14d2ad5c75bf059cb1015ae",
    ),
    "00_control/CURRENT_CURSOR.json": (
        5_676,
        "a79969903d29a26872c78d1dd573aabdeefff9c08720e7a99dc5b7d8f0499f1c",
    ),
    "release/out/RELEASE-MANIFEST.json": (
        4_773,
        "c0bfe88be28ce19bd730e69fd3bc0ed88b73f076e3d7a1b61b205cbb4a96f376",
    ),
    "release/receipts/zenodo-publication-receipt-2026.08.23-id.5.json": (
        5_197,
        "3e20d2459f42824e57df29bd0937e2f526d9349da7d941c65cf7dcec3739feab",
    ),
    "release/receipts/github-publication-receipt.json": (
        239_332,
        "b888b35ab940f1418b4c74c1da06548bb4fedf8e5079240368608eec605cccf8",
    ),
}

EXPECTED_NATIVE_COUNTS = {
    "artifacts": 83,
    "assets": 346,
    "concepts": 128,
    "corrections": 94,
    "courses": 1,
    "editions": 5,
    "programs": 1,
    "qa_events": 101,
    "relations": 9_545,
    "resources": 4,
    "rights": 21,
    "segments": 5_525,
    "terms": 140,
    "units": 1_993,
}
EXPECTED_NATIVE_RECORDS = 17_987
EXPECTED_SOURCE_VARIANTS = 2_632
EXPECTED_TARGET_VARIANTS = 5_186
EXPECTED_DERIVED_VARIANTS = EXPECTED_SOURCE_VARIANTS + EXPECTED_TARGET_VARIANTS
EXPECTED_COMMON_RECORDS = EXPECTED_NATIVE_RECORDS + EXPECTED_DERIVED_VARIANTS

DIRECT_TYPES = {
    "artifacts": ("artifacts", "artifact"),
    "assets": ("assets", "asset"),
    "concepts": ("concepts", "concept"),
    "corrections": ("corrections", "correction"),
    "courses": ("courses", "course"),
    "editions": ("editions", "edition"),
    "programs": ("programs", "program"),
    "qa_events": ("qa_events", "qa_event"),
    "relations": ("relations", "relation"),
    "resources": ("resources", "resource"),
    "rights": ("rights", "rights"),
    "segments": ("segments", "segment"),
    "terms": ("terms", "term"),
    "units": ("units", "unit"),
}

REFERENCE_KEYS = {
    "affected_ids",
    "affected_unit_ids",
    "additional_rights_component_ids",
    "asset_ids",
    "authority_manifest_artifact_id",
    "concept_id",
    "concept_ids",
    "correction_ids",
    "edition_id",
    "evidence_artifact_id",
    "evidence_unit_id",
    "from_id",
    "machine_backend_evidence_artifact_id",
    "parent_id",
    "prerequisite_concept_ids",
    "prerequisite_course_ids",
    "program_id",
    "replacement_asset_ids",
    "resource_id",
    "resource_ids",
    "rights_component_id",
    "rights_component_ids",
    "runtime_closure_evidence_artifact_id",
    "runtime_dependency_ids",
    "source_edition_id",
    "supersedes_id",
    "target_edition_id",
    "to_id",
    "topology_path",
    "unit_id",
    "wheel_artifact_id",
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical(value).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


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
        raise ValueError(f"missing {label}: {path}")
    if path.stat().st_size != expected_bytes:
        raise ValueError(f"{label} byte mismatch: {path.stat().st_size} != {expected_bytes}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch: {actual} != {expected_sha256}")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def valid_sha256(value: Any) -> str | None:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
        return value
    return None


def valid_commit(value: Any) -> str | None:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value):
        return value
    return None


def base(record_type: str, stable_key: str, native: dict, **fields: Any) -> dict:
    return {
        "id": rid(record_type, stable_key),
        "record_type": record_type,
        "recorded_at": native["recorded_at"],
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": native.get("status") or "native-recorded",
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def native_extension(native: dict, table: str, index: int) -> dict:
    return {
        NATIVE_EXTENSION: {
            "disposition": "direct-lossless-native-extension",
            "native_record": native,
            "native_record_id": native["id"],
            "native_record_sha256": sha256_bytes(canonical_bytes(native)),
            "native_source_file": f"backend/dist/jsonl/{table}.jsonl",
            "native_source_line": index + 1,
            "native_source_table": table,
            "native_source_table_index": index,
            "source_schema_name": native["schema_name"],
            "source_schema_version": native["schema_version"],
        }
    }


def iter_reference_values(value: Any, key: str | None = None) -> Iterable[str]:
    if key in REFERENCE_KEYS:
        if isinstance(value, str):
            yield value
            return
        if isinstance(value, list):
            for child in value:
                if isinstance(child, str):
                    yield child
            return
    if isinstance(value, dict):
        for child_key, child in value.items():
            yield from iter_reference_values(child, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from iter_reference_values(child, None)


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


def verify_manifest(owner_root: Path, manifest: dict) -> dict:
    dist = owner_root / "backend" / "dist"
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 30:
        raise ValueError("native backend manifest must contain exactly 30 data artifacts")
    manifest_rows: dict[str, dict] = {}
    total_bytes = 0
    for row in artifacts:
        relative = row["path"]
        if relative in manifest_rows:
            raise ValueError(f"duplicate native manifest path: {relative}")
        path = dist / relative
        exact_file(path, row["bytes"], row["sha256"], f"native manifest member {relative}")
        manifest_rows[relative] = row
        total_bytes += row["bytes"]

    checksum_rows: dict[str, str] = {}
    checksum_path = dist / "SHA256SUMS.txt"
    with checksum_path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n") or "\r" in line:
                raise ValueError(f"SHA256SUMS newline failure at row {line_number}")
            digest, relative = line[:-1].split("  ", 1)
            if relative in checksum_rows:
                raise ValueError(f"duplicate SHA256SUMS path: {relative}")
            checksum_rows[relative] = digest
    expected_checksums = {path: row["sha256"] for path, row in manifest_rows.items()}
    expected_checksums["manifest.json"] = sha256_file(dist / "manifest.json")
    if checksum_rows != expected_checksums:
        raise ValueError("SHA256SUMS and manifest closure differ")
    return {
        "declared_data_files": len(manifest_rows),
        "checksum_bound_files": len(checksum_rows),
        "generated_files_including_manifest_and_checksums": len(checksum_rows) + 1,
        "declared_data_bytes": total_bytes,
        "manifest_rows": manifest_rows,
    }


def verify_native(owner_root: Path) -> tuple[dict[str, list[dict]], dict]:
    for relative, (byte_count, digest) in EXPECTED_SOURCE_FILES.items():
        exact_file(owner_root / relative, byte_count, digest, relative)

    backend_path = owner_root / "backend" / "dist" / "backend-v0.json"
    schema_path = owner_root / "backend" / "schema" / "modular-backend-v0.schema.json"
    manifest_path = owner_root / "backend" / "dist" / "manifest.json"
    cursor_path = owner_root / "00_control" / "CURRENT_CURSOR.json"
    release_manifest_path = owner_root / "release" / "out" / "RELEASE-MANIFEST.json"
    backend = read_json(backend_path)
    native_schema = read_json(schema_path)
    manifest = read_json(manifest_path)
    cursor = read_json(cursor_path)
    release_manifest = read_json(release_manifest_path)

    Draft202012Validator.check_schema(native_schema)
    errors = sorted(
        Draft202012Validator(native_schema, format_checker=FormatChecker()).iter_errors(backend),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"native schema failure {list(first.absolute_path)}: {first.message}")
    if backend.get("schema_name") != SOURCE_SCHEMA_NAME or backend.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise ValueError("unexpected native backend profile")
    if backend.get("snapshot_at") != "2026-08-23T00:00:00+02:00":
        raise ValueError("unexpected native snapshot boundary")

    tables = {name: backend[name] for name in EXPECTED_NATIVE_COUNTS}
    counts = {name: len(rows) for name, rows in tables.items()}
    if counts != EXPECTED_NATIVE_COUNTS or sum(counts.values()) != EXPECTED_NATIVE_RECORDS:
        raise ValueError(f"native table-count mismatch: {counts}")

    ids: list[str] = []
    for table, rows in tables.items():
        for record in rows:
            ids.append(record["id"])
            if record["schema_version"] != SOURCE_SCHEMA_VERSION:
                raise ValueError(f"native record version mismatch: {record['id']}")
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate native IDs: {duplicates[:10]}")
    known_ids = set(ids)

    dangling: list[tuple[str, str]] = []
    for rows in tables.values():
        for record in rows:
            for reference in iter_reference_values(record):
                # Nested QA evidence also uses human-facing identifiers such
                # as ``CORR-CH10-*`` under a ``correction_ids`` key.  Those are
                # evidence-local labels, not backend entity IDs.  Native
                # entity IDs uniformly use a lower-case dotted prefix, so only
                # that stable-ID shape participates in this closure check.
                if reference not in known_ids and re.fullmatch(r"[a-z][a-z0-9_-]*\..+", reference):
                    dangling.append((record["id"], reference))
                    if len(dangling) >= 20:
                        break
            if len(dangling) >= 20:
                break
        if dangling:
            break
    if dangling:
        raise ValueError(f"native reference closure failure: {dangling}")

    framed_native = bytearray()
    jsonl_bytes = 0
    jsonl_hashes: dict[str, dict] = {}
    for table in sorted(tables):
        jsonl_path = owner_root / "backend" / "dist" / "jsonl" / f"{table}.jsonl"
        replay: list[dict] = []
        with jsonl_path.open("r", encoding="utf-8", newline="") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.endswith("\n") or "\r" in line:
                    raise ValueError(f"native JSONL newline failure: {table}:{line_number}")
                record = json.loads(line)
                if line != canonical(record) + "\n":
                    raise ValueError(f"native JSONL is not canonical: {table}:{line_number}")
                replay.append(record)
                framed_native.extend(f"{table}\t{line}".encode("utf-8"))
        if replay != tables[table]:
            raise ValueError(f"native JSONL does not reconstruct table: {table}")
        jsonl_bytes += jsonl_path.stat().st_size
        jsonl_hashes[table] = {
            "records": len(replay),
            "bytes": jsonl_path.stat().st_size,
            "sha256": sha256_file(jsonl_path),
        }

    source_variants = sum(isinstance(row.get("source_text"), str) for row in tables["segments"])
    target_variants = sum(isinstance(row.get("target_text"), str) for row in tables["segments"])
    if source_variants != EXPECTED_SOURCE_VARIANTS or target_variants != EXPECTED_TARGET_VARIANTS:
        raise ValueError("native segment payload count mismatch")
    for segment in tables["segments"]:
        if isinstance(segment.get("source_text"), str):
            if sha256_bytes(segment["source_text"].encode("utf-8")) != segment.get("source_content_sha256"):
                raise ValueError(f"source segment payload hash mismatch: {segment['id']}")
        if isinstance(segment.get("target_text"), str):
            if sha256_bytes(segment["target_text"].encode("utf-8")) != segment.get("target_content_sha256"):
                raise ValueError(f"target segment payload hash mismatch: {segment['id']}")

    manifest_diagnostics = verify_manifest(owner_root, manifest)
    if cursor.get("status") != "complete_book1_o018_id5_published_and_verified":
        raise ValueError("owner cursor is not at the complete id.5 boundary")
    if cursor.get("translation_cursor", {}).get("complete") is not True:
        raise ValueError("owner translation cursor is not complete")
    if cursor.get("current_artifacts", {}).get("backend", {}).get("sha256") != EXPECTED_SOURCE_FILES[
        "backend/dist/backend-v0.json"
    ][1]:
        raise ValueError("owner cursor backend identity mismatch")
    github = cursor.get("current_artifacts", {}).get("github", {})
    zenodo = cursor.get("current_artifacts", {}).get("zenodo", {})
    if github.get("commit_sha") != PUBLIC_COMMIT or github.get("tree_sha") != PUBLIC_TREE:
        raise ValueError("owner GitHub publication identity mismatch")
    if github.get("anonymous_readback") is not True or zenodo.get("anonymous_readback") is not True:
        raise ValueError("owner public readback is not closed")
    if zenodo.get("doi") != ZENODO_DOI:
        raise ValueError("owner Zenodo DOI mismatch")
    if release_manifest.get("version") != PUBLIC_VERSION or release_manifest.get("canonical_pdf", {}).get("pages") != 666:
        raise ValueError("owner release-manifest boundary mismatch")

    release_artifacts = {row["role"]: row for row in release_manifest["artifacts"]}
    if set(release_artifacts) != {"book1_pdf", "modular_backend", "o018_open_solver_labs", "translated_source"}:
        raise ValueError("owner primary release-artifact set mismatch")

    return tables, {
        "backend": backend,
        "cursor": cursor,
        "framed_native_bytes": len(framed_native),
        "framed_native_sha256": sha256_bytes(bytes(framed_native)),
        "jsonl_bytes": jsonl_bytes,
        "jsonl_hashes": jsonl_hashes,
        "manifest": manifest,
        "manifest_diagnostics": manifest_diagnostics,
        "release_artifacts": release_artifacts,
        "release_manifest": release_manifest,
    }


def media_type(native: dict) -> str:
    path = (
        native.get("target_path")
        or native.get("frozen_path")
        or native.get("source_path")
        or native.get("path")
        or ""
    )
    guessed, _ = mimetypes.guess_type(path)
    return guessed or "application/octet-stream"


def build_backend(
    native_tables: dict[str, list[dict]],
    schema: dict,
    diagnostics: dict,
    owner_root: Path,
) -> tuple[dict, dict]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}
    by_native = {
        record["id"]: record
        for table in sorted(native_tables)
        for record in native_tables[table]
    }
    native_table_by_id = {
        record["id"]: table
        for table in sorted(native_tables)
        for record in native_tables[table]
    }
    id_map = {
        native_id: rid(DIRECT_TYPES[native_table_by_id[native_id]][1], f"o018-c130:native:{native_id}")
        for native_id in by_native
    }

    def mapped(native_id: str | None) -> str | None:
        if native_id is None:
            return None
        try:
            return id_map[native_id]
        except KeyError as error:
            raise ValueError(f"unmapped native reference: {native_id}") from error

    def add(table: str, record: dict) -> str:
        tables[table].append(record)
        return record["id"]

    resources = {row["id"]: row for row in native_tables["resources"]}
    editions = {row["id"]: row for row in native_tables["editions"]}
    units = {row["id"]: row for row in native_tables["units"]}
    release_artifacts = diagnostics["release_artifacts"]
    release_manifest = diagnostics["release_manifest"]

    resource_rights = {
        resource_id: resource["rights_component_ids"][0]
        for resource_id, resource in resources.items()
    }

    def asset_resource(native: dict) -> str:
        if native.get("resource_id"):
            return native["resource_id"]
        identifier = native["id"]
        rights = native["rights_component_id"]
        if identifier.startswith("dependency.") or rights.startswith(("rights.o018.", "rights.pyomo.", "rights.highspy.", "rights.numpy.")):
            return O018_RESOURCE
        if rights == "rights.external.ooor-examples-policy":
            return OOOR_EXAMPLES_RESOURCE
        if rights == "rights.external.pyomo-gallery":
            return PYOMO_GALLERY_RESOURCE
        return R017_RESOURCE

    def artifact_edition(native: dict) -> str:
        marker = f"{native['id']} {native.get('path', '')}".lower()
        if "o018" in marker or "solver-lab" in marker:
            return O018_TARGET_EDITION
        if "pyomo-gallery" in marker:
            return PYOMO_GALLERY_EDITION
        if "ooor-examples" in marker or "open-optimization-or-examples" in marker:
            return OOOR_EXAMPLES_EDITION
        if "authority" in marker or marker.startswith("artifact.upstream"):
            return R017_SOURCE_EDITION
        return R017_TARGET_EDITION

    def rights_notice(native: dict, index: int) -> tuple[str, str, str]:
        license_file = native.get("license_file")
        claimed = valid_sha256(native.get("license_file_sha256"))
        if license_file:
            path = owner_root / license_file
            if not path.is_file():
                raise ValueError(f"rights notice file missing: {license_file}")
            actual = sha256_file(path)
            if claimed is not None and claimed != actual:
                raise ValueError(f"rights notice hash mismatch: {native['id']}")
            return license_file, actual, "exact notice-file bytes"
        locator = f"backend/dist/backend-v0.json#/rights/{index}"
        return locator, sha256_bytes(canonical_bytes(native)), "canonical UTF-8 native rights record"

    direct_common_ids: dict[str, str] = {}
    source_variant_ids: dict[str, str] = {}

    for table in sorted(native_tables):
        target_table, record_type = DIRECT_TYPES[table]
        for index, native in enumerate(native_tables[table]):
            stable_key = f"o018-c130:native:{native['id']}"
            common = base(record_type, stable_key, native)
            common["extensions"] = native_extension(native, table, index)
            common["supersedes_id"] = mapped(native.get("supersedes_id"))

            if table == "programs":
                common.update(
                    curriculum_version=native["version"],
                    locale=native["locale"],
                    program_key=native["id"],
                    rights_id=mapped(R017_CONTENT_RIGHTS),
                    title=native["title"],
                )
            elif table == "courses":
                common.update(
                    course_key="C130",
                    curriculum_source_locator="backend/dist/jsonl/courses.jsonl",
                    curriculum_source_sha256=diagnostics["jsonl_hashes"]["courses"]["sha256"],
                    order_key="C130",
                    outcome=native["curriculum_role"],
                    prerequisite_course_keys=native["prerequisite_course_ids"],
                    program_id=mapped(native["program_id"]),
                    resource_keys=native["resource_ids"],
                    role=native["curriculum_role"],
                    scope="Complete R017 Book 1 plus the separately attributed O018 open-solver laboratory; Book 2 is excluded.",
                    stage="C",
                    title=release_manifest["title"],
                )
            elif table == "resources":
                common.update(
                    authority_policy=(
                        f"Frozen official repository {native.get('repository_url')}"
                        if native.get("repository_url")
                        else "Owner-authored derivative resource frozen by the id.5 backend and public receipts"
                    ),
                    creator_name=native["creator"],
                    official_reader=native.get("reader_url"),
                    official_repository=native.get("repository_url") or "",
                    original_title=native["title"],
                    resource_key=native["id"],
                    work_type=native["resource_type"],
                )
            elif table == "editions":
                resource_id = native["resource_id"]
                target = native["id"] in {R017_TARGET_EDITION, O018_TARGET_EDITION}
                if native["id"] == R017_TARGET_EDITION:
                    archive_sha = release_artifacts["translated_source"]["sha256"]
                elif native["id"] == O018_TARGET_EDITION:
                    archive_sha = release_artifacts["o018_open_solver_labs"]["sha256"]
                else:
                    archive_sha = valid_sha256(native.get("archive_sha256"))
                common.update(
                    archive_sha256=archive_sha,
                    commit_sha=PUBLIC_COMMIT if target else valid_commit(native.get("commit")),
                    edition_kind="translated-derivative" if target else "source-snapshot",
                    locale=native["locale"],
                    release_date="2026-08-23" if target else native.get("authority_observed_at"),
                    resource_id=mapped(resource_id),
                    rights_id=mapped(resource_rights[resource_id]),
                    source_edition_id=mapped(native.get("source_edition_id")),
                    tree_sha=PUBLIC_TREE if target else valid_commit(native.get("tree")),
                    vcs_ref=f"v{PUBLIC_VERSION}" if target else native.get("branch") or native.get("commit") or "frozen-snapshot",
                    vcs_type="git",
                    version_label=PUBLIC_VERSION if target else (native.get("commit") or "frozen")[:12],
                )
                if common["commit_sha"] is None:
                    raise ValueError(f"edition lacks a valid commit binding: {native['id']}")
            elif table == "units":
                source_path = native.get("source_path") or "/".join(native["topology_path"])
                common.update(
                    first_edition_id=mapped(native["edition_id"]),
                    identity_anchor=native.get("source_local_id") or native["id"],
                    identity_basis=(
                        "native-source-local-id" if native.get("source_local_id") else "native-stable-topology-id"
                    ),
                    resource_id=mapped(native["resource_id"]),
                    rights_default_id=mapped(native["rights_component_id"]),
                    source_label=native.get("title_source"),
                    source_local_id=native.get("source_local_id"),
                    source_path=source_path,
                    source_xml_path=None,
                    unit_kind=native["unit_type"],
                )
            elif table == "segments":
                common.update(
                    identity_anchor=native.get("source_local_id") or native["id"],
                    ordinal=int(native["order"]),
                    segment_kind=native["segment_type"],
                    segmentation_profile="r017-o018-v0-combined-source-target-segment",
                    unit_id=mapped(native["unit_id"]),
                )
            elif table == "terms":
                common.update(
                    concept_id=mapped(native["concept_id"]),
                    evidence=native["evidence"],
                    notes=native["scope"],
                    preferred_form=native["preferred"],
                    register=native["register"],
                    scope_unit_id=mapped(R017_ROOT_UNIT),
                    source_form=native["source_term"],
                    source_locale=native["source_locale"],
                    source_term_id=native["id"],
                    target_locale=native["target_locale"],
                    term_status=native["status"],
                )
                common["extensions"][NATIVE_EXTENSION]["scope_projection"] = (
                    "Common v1 requires one scope unit; the R017 Book 1 root is used as the corpus-root sentinel, while the exact cross-R017/O018 scope remains in native_record.scope."
                )
            elif table == "concepts":
                common.update(
                    concept_key=native["id"],
                    concept_scheme="r017-o018-native-concept-v0",
                    definition_segment_id=None,
                    parent_concept_id=None,
                )
            elif table == "assets":
                common.update(
                    asset_kind=native["asset_type"],
                    canonical_path_or_uri=(
                        native.get("target_path")
                        or native.get("frozen_path")
                        or native.get("source_path")
                        or native["id"]
                    ),
                    media_type=media_type(native),
                    resource_id=mapped(asset_resource(native)),
                    rights_default_id=mapped(native["rights_component_id"]),
                )
            elif table == "relations":
                common.update(
                    assertion_method="explicit-owner-validated-native-relation",
                    confidence="owner-validated",
                    edition_id=None,
                    from_id=mapped(native["from_id"]),
                    ordinal=0,
                    relation_type=native["relation_type"],
                    source_locator=f"backend/dist/jsonl/relations.jsonl#{index + 1}",
                    strength="asserted",
                    to_id=mapped(native["to_id"]),
                )
                common["extensions"][NATIVE_EXTENSION]["ordinal_disposition"] = (
                    "Native relations are unordered; common ordinal 0 is an explicit unordered sentinel."
                )
            elif table == "rights":
                locator, notice_sha, hash_basis = rights_notice(native, index)
                common.update(
                    assertion_status=native["status"],
                    attribution=native["component_scope"],
                    authority=native.get("compatibility_note") or native["component_scope"],
                    change_notice="required" if native.get("changes_disclosed") else "not asserted by native record",
                    license_expression=native["license_expression"],
                    nonendorsement="required" if native.get("non_endorsement") else "not asserted by native record",
                    notice_locator=locator,
                    notice_sha256=notice_sha,
                    source_component_id=native["id"],
                    third_party_status=native["third_party_status"],
                )
                common["extensions"][NATIVE_EXTENSION]["notice_hash_basis"] = hash_basis
            elif table == "qa_events":
                common.update(
                    input_hash=sha256_bytes(canonical_bytes(native)),
                    method=native["qa_type"],
                    qa_type=native["qa_type"],
                    result=native["result"],
                    reviewer_kind="owner-lane-machine-validation",
                    severity_p1=0,
                    severity_p2=0,
                    severity_p3=0,
                    tool_name=native["responsible_workflow"],
                    tool_version=native["schema_version"],
                    witness_locator=(
                        native["witness"]
                        if isinstance(native["witness"], str)
                        else canonical(native["witness"])
                    ),
                )
                common["extensions"][NATIVE_EXTENSION]["severity_disposition"] = (
                    "Zero means the native QA event exposes no severity-count fields; it is not an independent re-review finding."
                )
            elif table == "artifacts":
                edition_id = artifact_edition(native)
                common.update(
                    artifact_kind=native["artifact_type"],
                    build_receipt=native["build_receipt"],
                    bytes=int(native["bytes"]) if native["bytes"] is not None else None,
                    edition_id=mapped(edition_id),
                    locale=editions[edition_id]["locale"],
                    manifest_sha256=valid_sha256(native.get("extracted_closure_sha256")),
                    public_uri=None,
                    sha256=valid_sha256(native["sha256"]),
                    toolchain_id=native["toolchain"],
                    tree_sha256=valid_sha256(native.get("extracted_closure_sha256")),
                )
                common["extensions"][NATIVE_EXTENSION]["edition_projection"] = edition_id
            elif table == "corrections":
                affected_native = native["affected_unit_ids"][0]
                affected_unit = units[affected_native]
                common.update(
                    affected_id=mapped(affected_native),
                    binding_status=None,
                    category=native["correction_type"],
                    evidence_locator=canonical(native["evidence"]),
                    local_state=native["status"],
                    original_payload_sha256=sha256_bytes(native["source_defect"].encode("utf-8")),
                    payload_hash_basis="UTF-8 bytes of native source_defect and target_action strings",
                    rationale=native["rationale"],
                    replacement_payload_sha256=sha256_bytes(native["target_action"].encode("utf-8")),
                    source_claim_id=None,
                    source_edition_id=mapped(affected_unit["edition_id"]),
                    source_record_id=None,
                    upstream_disposition=native["upstream_report_disposition"],
                    upstream_url=None,
                )
            else:
                raise ValueError(f"unhandled native table: {table}")

            if common["id"] != id_map[native["id"]]:
                raise ValueError(f"identity derivation mismatch: {native['id']}")
            add(target_table, common)
            direct_common_ids[native["id"]] = common["id"]

            if table == "segments" and isinstance(native.get("source_text"), str):
                variant_key = f"o018-c130:derived:{native['id']}:source"
                source_variant = base(
                    "segment_variant",
                    variant_key,
                    native,
                    edition_id=mapped(native["source_edition_id"]),
                    format="text/plain+tex-fragment",
                    locale=native["source_locale"],
                    payload=native["source_text"],
                    payload_sha256=native["source_content_sha256"],
                    rights_id=mapped(native["rights_component_id"]),
                    role="source",
                    segment_id=mapped(native["id"]),
                    source_variant_id=None,
                    translation_state="source_frozen",
                )
                source_variant["extensions"] = {
                    DERIVED_EXTENSION: {
                        "derivation": "exact native source_text projection",
                        "native_segment_id": native["id"],
                        "native_payload_field": "source_text",
                        "native_payload_sha256_field": "source_content_sha256",
                    }
                }
                add("segment_variants", source_variant)
                source_variant_ids[native["id"]] = source_variant["id"]

            if table == "segments" and isinstance(native.get("target_text"), str):
                variant_key = f"o018-c130:derived:{native['id']}:target"
                target_variant = base(
                    "segment_variant",
                    variant_key,
                    native,
                    edition_id=mapped(native["target_edition_id"]),
                    format="text/plain+tex-fragment",
                    locale=native["target_locale"],
                    payload=native["target_text"],
                    payload_sha256=native["target_content_sha256"],
                    rights_id=mapped(native["rights_component_id"]),
                    role="target",
                    segment_id=mapped(native["id"]),
                    source_variant_id=source_variant_ids.get(native["id"]),
                    translation_state=native["translation_state"],
                )
                target_variant["extensions"] = {
                    DERIVED_EXTENSION: {
                        "derivation": "exact native target_text projection",
                        "native_segment_id": native["id"],
                        "native_payload_field": "target_text",
                        "native_payload_sha256_field": "target_content_sha256",
                        "source_variant_disposition": (
                            "linked when source_text exists; null for explicit native target_projection records without an embedded source payload"
                        ),
                    }
                }
                add("segment_variants", target_variant)

    for rows in tables.values():
        rows.sort(key=lambda record: record["id"])

    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rid("dataset", "o018-c130-r017-book1-id-complete"),
        "dataset_version": f"{PUBLIC_VERSION}+interlanguage-v1",
        "tables": dict(sorted(tables.items())),
    }

    recovered: dict[str, list[dict | None]] = {
        table: [None] * len(rows) for table, rows in native_tables.items()
    }
    recovered_ids: set[str] = set()
    for rows in tables.values():
        for common in rows:
            envelope = common.get("extensions", {}).get(NATIVE_EXTENSION)
            if envelope is None:
                continue
            native = envelope["native_record"]
            if native["id"] != envelope["native_record_id"]:
                raise ValueError("native reverse identity mismatch")
            if sha256_bytes(canonical_bytes(native)) != envelope["native_record_sha256"]:
                raise ValueError(f"native reverse checksum mismatch: {native['id']}")
            if native["id"] in recovered_ids:
                raise ValueError(f"native record recovered more than once: {native['id']}")
            recovered_ids.add(native["id"])
            table = envelope["native_source_table"]
            index = envelope["native_source_table_index"]
            if recovered[table][index] is not None:
                raise ValueError(f"native table/index recovered more than once: {table}:{index}")
            recovered[table][index] = native
    if recovered != native_tables:
        raise ValueError("exact table-preserving native reverse extraction failed")

    mapping_payload = b"".join(
        f"{native_table_by_id[native_id]}\t{native_id}\t{id_map[native_id]}\n".encode("utf-8")
        for native_id in sorted(id_map)
    )
    direct_table_counts = Counter(DIRECT_TYPES[native_table_by_id[native_id]][0] for native_id in id_map)
    return backend, {
        "exact_reverse_extraction": len(recovered_ids),
        "native_id_mapping_bytes": len(mapping_payload),
        "native_id_mapping_sha256": sha256_bytes(mapping_payload),
        "native_to_common_table_counts": dict(sorted(direct_table_counts.items())),
        "direct_common_ids": len(direct_common_ids),
        "derived_source_variants": len(source_variant_ids),
        "derived_target_variants": sum(
            isinstance(row.get("target_text"), str) for row in native_tables["segments"]
        ),
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
        (record for rows in backend["tables"].values() for record in rows),
        key=lambda record: (record["record_type"], record["id"]),
    )
    ids = [record["id"] for record in records]
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate common IDs: {duplicates[:10]}")
    known = set(ids)
    dangling: list[dict] = []
    for record in records:
        for field_path, value in referenced_urns(record):
            if field_path == ("id",):
                continue
            if value not in known:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
                if len(dangling) >= 20:
                    break
        if dangling:
            break
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling}")

    virtual = b"".join((canonical(record) + "\n").encode("utf-8") for record in records)
    table_hashes: dict[str, dict] = {}
    for table, rows in backend["tables"].items():
        payload = b"".join((canonical(row) + "\n").encode("utf-8") for row in rows)
        table_hashes[table] = {
            "records": len(rows),
            "virtual_jsonl_bytes": len(payload),
            "virtual_jsonl_sha256": sha256_bytes(payload),
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
        "virtual_records_jsonl_bytes": len(virtual),
        "virtual_records_jsonl_sha256": sha256_bytes(virtual),
    }


def build_receipt(
    owner_root: Path,
    schema_path: Path,
    receipt_schema_path: Path,
) -> dict:
    schema = read_json(schema_path)
    receipt_schema = read_json(receipt_schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(receipt_schema)
    if sha256_file(schema_path) != "3de8d107b1c75db0f8d60c42ef7e3488bc3fcc93f72e955def71a771475cf2b2":
        raise ValueError("common backend schema drift")
    if sha256_file(receipt_schema_path) != "0147b14972dd562805b3b5f76fac453a9f32a6d298827d3f588316d4a8f5ffe0":
        raise ValueError("migration receipt schema drift")

    first_native, first_diagnostics = verify_native(owner_root)
    first_backend, first_mapping = build_backend(first_native, schema, first_diagnostics, owner_root)
    first_validation = validate_backend(first_backend, schema)
    if first_validation["record_count"] != EXPECTED_COMMON_RECORDS:
        raise ValueError("common target record count mismatch")

    second_native, second_diagnostics = verify_native(owner_root)
    second_backend, second_mapping = build_backend(second_native, schema, second_diagnostics, owner_root)
    second_validation = validate_backend(second_backend, schema)
    first_bytes = canonical_bytes(first_backend)
    second_bytes = canonical_bytes(second_backend)
    if (
        first_bytes != second_bytes
        or first_mapping != second_mapping
        or first_validation != second_validation
        or first_diagnostics["framed_native_sha256"] != second_diagnostics["framed_native_sha256"]
    ):
        raise ValueError("two independent native/common assemblies are not byte-identical")

    publication_files = [
        "00_control/CURRENT_CURSOR.json",
        "release/out/RELEASE-MANIFEST.json",
        "release/receipts/zenodo-publication-receipt-2026.08.23-id.5.json",
        "release/receipts/github-publication-receipt.json",
    ]
    release_artifacts = first_diagnostics["release_artifacts"]
    public_artifacts = []
    for role in ("book1_pdf", "modular_backend", "o018_open_solver_labs", "translated_source"):
        artifact = release_artifacts[role]
        filename = artifact["file_name"]
        public_artifacts.append(
            {
                "role": role,
                "name": filename,
                "bytes": artifact["bytes"],
                "sha256": artifact["sha256"],
                "github_uri": f"{GITHUB_REPOSITORY}/releases/download/v{PUBLIC_VERSION}/{filename}",
                "zenodo_uri": f"{ZENODO_RECORD}/files/{filename}?download=1",
                "status": "owner receipts prove anonymous byte/hash readback",
            }
        )

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "o018-c130-r017-book1-id5-to-interlanguage-v1",
        "migration_mode": "lossless additive one-common-record-per-native-record adapter with exact segment-variant projections",
        "source": {
            "dataset_id": "R017/O018-C130-book1-id-ID",
            "dataset_version": PUBLIC_VERSION,
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": SOURCE_SCHEMA_VERSION,
            "completion": "complete_book1_o018_id5_published_and_verified",
            "course_role_id": "C130",
            "native_backend_path": "backend/dist/backend-v0.json",
            "native_backend_bytes": EXPECTED_SOURCE_FILES["backend/dist/backend-v0.json"][0],
            "native_backend_sha256": EXPECTED_SOURCE_FILES["backend/dist/backend-v0.json"][1],
            "native_schema_path": "backend/schema/modular-backend-v0.schema.json",
            "native_schema_bytes": EXPECTED_SOURCE_FILES["backend/schema/modular-backend-v0.schema.json"][0],
            "native_schema_sha256": EXPECTED_SOURCE_FILES["backend/schema/modular-backend-v0.schema.json"][1],
            "native_manifest_path": "backend/dist/manifest.json",
            "native_manifest_bytes": EXPECTED_SOURCE_FILES["backend/dist/manifest.json"][0],
            "native_manifest_sha256": EXPECTED_SOURCE_FILES["backend/dist/manifest.json"][1],
            "native_sha256sums_path": "backend/dist/SHA256SUMS.txt",
            "native_sha256sums_bytes": EXPECTED_SOURCE_FILES["backend/dist/SHA256SUMS.txt"][0],
            "native_sha256sums_sha256": EXPECTED_SOURCE_FILES["backend/dist/SHA256SUMS.txt"][1],
            "native_record_count": EXPECTED_NATIVE_RECORDS,
            "native_table_counts": EXPECTED_NATIVE_COUNTS,
            "native_jsonl_bytes": first_diagnostics["jsonl_bytes"],
            "canonical_path_framed_native_bytes": first_diagnostics["framed_native_bytes"],
            "canonical_path_framed_native_sha256": first_diagnostics["framed_native_sha256"],
            "native_export_closure": first_diagnostics["manifest_diagnostics"],
            "authority_commit": "1745df89b608899f66983834fa4ec8c8910d18ff",
            "authority_tree": "209d5de696ebac4e5921b73d6b6b2f539fc23d1c",
            "authority_archive_sha256": "4bee88ed3af700b16d5643a3c18b9846244d3467eec7f4fb1f009a782b9143fc",
            "github_commit": PUBLIC_COMMIT,
            "github_tree": PUBLIC_TREE,
            "github_release": GITHUB_RELEASE,
            "zenodo_doi": ZENODO_DOI,
            "publication_authority_files": {
                relative: {
                    "bytes": EXPECTED_SOURCE_FILES[relative][0],
                    "sha256": EXPECTED_SOURCE_FILES[relative][1],
                }
                for relative in publication_files
            },
            "scope_note": "The frozen corpus is complete R017 Book 1 plus its separately attributed O018 open-solver laboratory. It does not claim Book 2 or broader advanced-optimization coverage.",
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
            "common_identity_formula": "UUIDv5(namespace, record_type|o018-c130:native:<native-id>)",
            "canonical_native_records_consumed": EXPECTED_NATIVE_RECORDS,
            "direct_common_records_emitted": EXPECTED_NATIVE_RECORDS,
            "derived_segment_variant_records": EXPECTED_DERIVED_VARIANTS,
            "common_records_emitted": first_validation["record_count"],
            "native_ids_preserved_in_namespaced_extensions": EXPECTED_NATIVE_RECORDS,
            "native_payloads_preserved_byte_equivalently": EXPECTED_NATIVE_RECORDS,
            "changed_native_payload_fields": 0,
            "dropped_native_records": 0,
            "exact_reverse_extraction": first_mapping["exact_reverse_extraction"],
            "native_id_mapping_bytes": first_mapping["native_id_mapping_bytes"],
            "native_id_mapping_sha256": first_mapping["native_id_mapping_sha256"],
            "native_to_common_table_counts": first_mapping["native_to_common_table_counts"],
            "source_segment_variants": first_mapping["derived_source_variants"],
            "target_segment_variants": first_mapping["derived_target_variants"],
            "segment_payload_policy": "Exact native source_text/target_text bytes and their verified SHA-256 values are projected; the complete combined segment remains in the direct native extension.",
        },
        "validation": {
            "result": "pass",
            "native_schema_validation": "pass",
            "native_manifest_and_sha256sums_closure": "pass",
            "native_jsonl_exact_table_reconstruction": "pass",
            "native_foreign_key_closure": "pass",
            "native_unique_ids": EXPECTED_NATIVE_RECORDS,
            "native_two_clean_full_surface_reads": 2,
            "strict_common_backend_schema": "pass",
            "global_unique_common_ids": first_validation["global_unique_ids"],
            "common_foreign_key_closure": first_validation["foreign_key_closure"],
            "lossless_reverse_records": first_mapping["exact_reverse_extraction"],
            "two_independent_common_assemblies": "byte-identical",
            "public_preservation_receipts": "pass",
            "receipt_schema_sha256": sha256_file(receipt_schema_path),
        },
        "coverage": {
            "native_records": EXPECTED_NATIVE_RECORDS,
            "direct_record_coverage": f"{EXPECTED_NATIVE_RECORDS}/{EXPECTED_NATIVE_RECORDS}",
            "native_table_count": len(EXPECTED_NATIVE_COUNTS),
            "common_table_count": first_validation["table_count"],
            "nonempty_common_tables": first_validation["nonempty_table_count"],
            "units": EXPECTED_NATIVE_COUNTS["units"],
            "segments": EXPECTED_NATIVE_COUNTS["segments"],
            "source_segment_payloads": EXPECTED_SOURCE_VARIANTS,
            "target_segment_payloads": EXPECTED_TARGET_VARIANTS,
            "relations": EXPECTED_NATIVE_COUNTS["relations"],
            "assets": EXPECTED_NATIVE_COUNTS["assets"],
            "artifacts": EXPECTED_NATIVE_COUNTS["artifacts"],
            "concepts": EXPECTED_NATIVE_COUNTS["concepts"],
            "terms": EXPECTED_NATIVE_COUNTS["terms"],
            "rights": EXPECTED_NATIVE_COUNTS["rights"],
            "corrections": EXPECTED_NATIVE_COUNTS["corrections"],
            "qa_events": EXPECTED_NATIVE_COUNTS["qa_events"],
            "reader_pages": 666,
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "decision": "zero-copy virtual common dataset; retain the stronger frozen native backend and regenerate the strict common stream deterministically on demand",
            "owner_backend_modified": False,
            "source_or_target_payload_bytes_modified": 0,
        },
        "public_artifacts": public_artifacts,
        "credentials_recorded": False,
    }

    receipt_errors = sorted(
        Draft202012Validator(receipt_schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda error: list(error.absolute_path),
    )
    if receipt_errors:
        first = receipt_errors[0]
        raise ValueError(f"receipt schema failure {list(first.absolute_path)}: {first.message}")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--receipt-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    migration_root = Path(__file__).resolve().parent
    owner_root = args.corpus_root.resolve()
    output_path = args.output_receipt.resolve()
    try:
        output_path.relative_to(migration_root)
    except ValueError as error:
        raise ValueError("the adapter may write only inside its O018-specific migration directory") from error
    if output_path.is_relative_to(owner_root):
        raise ValueError("the frozen owner lane is read-only")

    receipt = build_receipt(
        owner_root,
        args.schema.resolve(),
        args.receipt_schema.resolve(),
    )
    payload = pretty_bytes(receipt)
    if args.check:
        if not output_path.is_file():
            raise ValueError(f"missing migration receipt for --check: {output_path}")
        existing = output_path.read_bytes()
        if existing != payload:
            raise ValueError(
                f"migration receipt replay mismatch: {sha256_bytes(existing)} != {sha256_bytes(payload)}"
            )
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)

    print(
        canonical(
            {
                "common_records": receipt["target"]["record_count"],
                "direct_native_records": EXPECTED_NATIVE_RECORDS,
                "mode": "check" if args.check else "write",
                "receipt": output_path.name,
                "receipt_bytes": len(payload),
                "receipt_sha256": sha256_bytes(payload),
                "result": "pass",
            }
        )
    )


if __name__ == "__main__":
    main()
