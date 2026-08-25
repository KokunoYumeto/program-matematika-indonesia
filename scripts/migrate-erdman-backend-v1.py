#!/usr/bin/env python3
"""Prove a deterministic common-backend v1 view of the complete D20 edition.

The functional-analysis owner repository remains authoritative and untouched.
This adapter verifies its two exact manifests, every manifest member, the final
coordinator handoff, companion validation, and the frozen public release ZIP.
It then projects every owner-native JSONL row losslessly into the common schema
and adds only the common records needed for bilingual text, files, terminology,
external anchors, routes, and publication.  The 41,689-record result is virtual:
only a compact, independently replayable migration receipt is written here.
"""

from __future__ import annotations

import argparse
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
from typing import Any, Iterable, Iterator

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
RECEIPT_SCHEMA_NAME = "interlanguage-math-modular-backend-migration-receipt"
SOURCE_SCHEMA_NAME = "interlanguage-modular-math"
SOURCE_SCHEMA_VERSION = "0.1.0"
WORKFLOW_ID = "program-matematika-indonesia/erdman-d20-v1-adapter-1.0.0"
RECORDED_AT = "2026-08-25T00:00:00Z"
NATIVE_EXTENSION = "interlanguage.erdman-functional-analysis-native"
DERIVED_EXTENSION = "interlanguage.erdman-functional-analysis-derived"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")

EXPECTED_BACKEND_SCHEMA_BYTES = 126_423
EXPECTED_BACKEND_SCHEMA_SHA256 = (
    "3de8d107b1c75db0f8d60c42ef7e3488bc3fcc93f72e955def71a771475cf2b2"
)
EXPECTED_RECEIPT_SCHEMA_BYTES = 2_563
EXPECTED_RECEIPT_SCHEMA_SHA256 = (
    "0147b14972dd562805b3b5f76fac453a9f32a6d298827d3f588316d4a8f5ffe0"
)
EXPECTED_BASE_MANIFEST_BYTES = 5_684
EXPECTED_BASE_MANIFEST_SHA256 = (
    "06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc"
)
EXPECTED_BASE_MANIFEST_ROWS = 61
EXPECTED_BASE_MEMBER_BYTES = 16_787_048
EXPECTED_COMPANION_MANIFEST_BYTES = 1_073
EXPECTED_COMPANION_MANIFEST_SHA256 = (
    "9be0d071106f9ba38e00f50811a718c84102e4527ae507a8e51250bbd9bfb201"
)
EXPECTED_COMPANION_MANIFEST_ROWS = 11
EXPECTED_COMPANION_MEMBER_BYTES = 672_820
EXPECTED_COMPANION_VALIDATION_BYTES = 4_524
EXPECTED_COMPANION_VALIDATION_SHA256 = (
    "ee7ae54a5a069e22aabd9e2c76e16a5b8571736cf93a6298babd80730735312d"
)
EXPECTED_HANDOFF_BYTES = 9_475
EXPECTED_HANDOFF_SHA256 = (
    "b24ba7dab5f734b34e1d9e751633d4090d76b0be7227a9eae64809e5cf3878f9"
)
EXPECTED_PAGES_HANDOFF_BYTES = 5_396
EXPECTED_PAGES_HANDOFF_SHA256 = (
    "358c85fe070a987ac9b63a7f6a466441b4df382ebf3b02c00f72c23137aa8056"
)
EXPECTED_PAGES_RECEIPT_BYTES = 94_445
EXPECTED_PAGES_RECEIPT_SHA256 = (
    "054f3946bf59c29922f8b92f8ff0aa829d2eb3c2bb517d4bcbd0ecb8c5b90cee"
)
EXPECTED_RELEASE_ARCHIVE_BYTES = 3_793_368
EXPECTED_RELEASE_ARCHIVE_SHA256 = (
    "ac5b3ec1fe7c2cf0a17eacce29c920ca5976c0c7d15e37f0ba0476afe9c48e32"
)
EXPECTED_RELEASE_ARCHIVE_FILES = 306
EXPECTED_RELEASE_MANIFEST_BYTES = 33_975
EXPECTED_RELEASE_MANIFEST_SHA256 = (
    "b64481f03f4fccce117b73b46f7dba2dd505a86e895c29a50f10e975e390a706"
)
EXPECTED_RELEASE_MANIFEST_ROWS = 304
EXPECTED_RELEASE_METADATA_BYTES = 2_464
EXPECTED_RELEASE_METADATA_SHA256 = (
    "21592b1da22bbfcc6a280817ff097b63f825a9953f1436f927db4fc67bf97b49"
)
EXPECTED_GIT_COMMIT = "059bda086dfd6e6aa80f2077b2338c5d15039057"
EXPECTED_GIT_TREE = "77822a94a46d6422d9ed9c6b48e345229a4e7c05"
EXPECTED_PAGES_GIT_COMMIT = "8faf10ecd30a0e9497732ec487423dad4ab15c22"
EXPECTED_PAGES_GIT_TREE = "74036bb86f7ca940d0c400a45f18f7399e7a3d55"
PUBLIC_VERSION = "2026.08.25-backend-artifact-reconciliation"
PUBLIC_ZENODO_DOI = "10.5281/zenodo.22088947"
PUBLIC_ZENODO_RECORD = "https://zenodo.org/records/22088947"
PUBLIC_REPOSITORY = "https://github.com/KokunoYumeto/functional-analysis-erdman-id"
PUBLIC_HTML_READER_URL = "https://kokunoyumeto.github.io/functional-analysis-erdman-id/"
PUBLIC_HTML_COMPANION_URL = (
    "https://kokunoyumeto.github.io/functional-analysis-erdman-id/companion/"
)
PUBLIC_READER_FILENAME = (
    "analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf"
)
PUBLIC_READER_URL = (
    "https://zenodo.org/records/22088947/files/"
    + PUBLIC_READER_FILENAME
    + "?download=1"
)
EXPECTED_READER_BYTES = 2_838_207
EXPECTED_READER_SHA256 = (
    "6d4bbf02959e5afb5fd34e1118f91f026c293b0056ec7a0ecdc5e95944df5d85"
)

EXPECTED_NATIVE_RECORDS = 32_383
EXPECTED_AUXILIARY_INDEX_ROWS = 2_104
EXPECTED_LOGICAL_INPUT_ROWS = 34_487
EXPECTED_DERIVED_RECORDS = 9_306
EXPECTED_TARGET_RECORDS = 41_689
EXPECTED_EXTERNAL_ANCHORS = 68
EXPECTED_SEGMENTS = 2_196
EXPECTED_SEGMENT_VARIANTS = 4_392
EXPECTED_INDEX_ALIASES = 2_104
EXPECTED_TERM_NESTED_VARIANTS = 42
EXPECTED_SOURCE_TARGET_FILES = 18

EXPECTED_RECORD_COUNTS_BY_FILE = {
    "artifacts.jsonl": 217,
    "assets.jsonl": 3,
    "bridge_units.jsonl": 13,
    "companion_artifacts.jsonl": 70,
    "companion_components.jsonl": 4,
    "companion_html_routes.jsonl": 294,
    "companion_provenance.jsonl": 4,
    "companion_relations.jsonl": 826,
    "companion_surfaces.jsonl": 2,
    "concept_relations.jsonl": 22,
    "concepts.jsonl": 15,
    "corrections.jsonl": 286,
    "exercise_support.jsonl": 52,
    "formula_map.jsonl": 12_135,
    "html_assets.jsonl": 80,
    "html_routes.jsonl": 4_838,
    "html_surfaces.jsonl": 1,
    "o001_mastery.jsonl": 62,
    "o001_status.jsonl": 52,
    "qa_events.jsonl": 160,
    "relations.jsonl": 8_724,
    "resources.jsonl": 5,
    "rights.jsonl": 4,
    "segments.jsonl": 2_196,
    "semantic_units.jsonl": 1_867,
    "terminology_qa.jsonl": 7,
    "terminology.jsonl": 425,
    "units.jsonl": 19,
}

EXPECTED_TABLE_COUNTS = {
    "aliases": 7_236,
    "alignments": 14_331,
    "artifacts": 290,
    "assets": 83,
    "concepts": 425,
    "corrections": 286,
    "courses": 2,
    "editions": 2,
    "file_revisions": 36,
    "files": 36,
    "programs": 1,
    "qa_events": 217,
    "relations": 9_624,
    "release_snapshots": 1,
    "resources": 1,
    "rights": 4,
    "route_members": 17,
    "routes": 2,
    "segment_variants": 4_392,
    "segments": 2_196,
    "term_variants": 48,
    "terms": 426,
    "units": 2_033,
}

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
RECORD_TYPE_TO_TABLE = {value: key for key, value in TABLE_TO_RECORD_TYPE.items()}

FILE_COMMON_TYPE = {
    "artifacts.jsonl": "artifact",
    "assets.jsonl": "asset",
    "bridge_units.jsonl": "unit",
    "companion_artifacts.jsonl": "artifact",
    "companion_components.jsonl": "unit",
    "companion_html_routes.jsonl": "alias",
    "companion_provenance.jsonl": "qa_event",
    "companion_relations.jsonl": "relation",
    "companion_surfaces.jsonl": "artifact",
    "concept_relations.jsonl": "relation",
    "concepts.jsonl": "concept",
    "corrections.jsonl": "correction",
    "exercise_support.jsonl": "relation",
    "formula_map.jsonl": "alignment",
    "html_assets.jsonl": "asset",
    "html_routes.jsonl": "alias",
    "html_surfaces.jsonl": "artifact",
    "o001_mastery.jsonl": "unit",
    "o001_status.jsonl": "qa_event",
    "qa_events.jsonl": "qa_event",
    "relations.jsonl": "relation",
    "rights.jsonl": "rights",
    "segments.jsonl": "segment",
    "semantic_units.jsonl": "unit",
    "terminology.jsonl": "term",
    "units.jsonl": "unit",
}

PROGRAM_NATIVE_ID = "MATH-ID-D20"
COURSE_NATIVE_ID = "COURSE-D20"
RESOURCE_NATIVE_ID = "ERDMAN-FAOA"
SOURCE_EDITION_NATIVE_ID = "ERDMAN-FAOA-2015"
TARGET_EDITION_NATIVE_ID = "ERDMAN-FAOA-2015-ID"
ERDMAN_RIGHTS_NATIVE_ID = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ORIGINAL_RIGHTS_NATIVE_ID = "RIGHTS-ORIGINAL-CC-BY-SA-4.0"
SCOPE_UNIT_STABLE_KEY = "erdman:derived:unit:whole-edition-lexical-scope"
EXTERNAL_COURSE_NATIVE_ID = "COURSE-O007"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CHAPTER_ID_RE = re.compile(r"^(FAOA-2015-(?:PREFACE|CH\d{2}))")


@dataclass(frozen=True)
class NativeRow:
    source_file: str
    source_ordinal: int
    raw_line: bytes
    value: dict[str, Any]
    native_id: str
    native_type: str
    common_type: str
    stable_key: str
    target_id: str

    @property
    def raw_line_sha256(self) -> str:
        return sha256_bytes(self.raw_line)

    @property
    def canonical_native_sha256(self) -> str:
        return sha256_bytes(canonical_bytes(self.value))

    @property
    def tuple_key(self) -> tuple[str, int, str, str]:
        return (
            self.source_file,
            self.source_ordinal,
            self.native_type,
            self.native_id,
        )


@dataclass(frozen=True)
class FilePair:
    unit_native_id: str
    source_path: str
    source_bytes: int
    source_sha256: str
    target_path: str
    target_bytes: int
    target_sha256: str


@dataclass
class Snapshot:
    owner_root: Path
    backend_root: Path
    rows: list[NativeRow]
    rows_by_file: dict[str, list[NativeRow]]
    rows_by_native_id: dict[str, list[NativeRow]]
    primary_by_native_id: dict[str, NativeRow]
    index_rows: list[dict[str, str]]
    index_raw_rows: list[bytes]
    external_ids: list[str]
    file_pairs: list[FilePair]
    source_revision_by_unit: dict[str, str]
    target_revision_by_unit: dict[str, str]
    manifest_facts: dict[str, Any]
    public_evidence: dict[str, Any]
    native_stream_bytes: int
    native_stream_sha256: str
    auxiliary_stream_bytes: int
    auxiliary_stream_sha256: str
    handoff: dict[str, Any]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical(value).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_file(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    payload = path.read_bytes()
    if len(payload) != expected_bytes:
        raise ValueError(
            f"{label} byte mismatch: expected {expected_bytes}, got {len(payload)}"
        )
    actual = sha256_bytes(payload)
    if actual != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch: expected {expected_sha256}, got {actual}")
    return payload


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return canonical(value)


def valid_sha256(value: Any) -> str | None:
    return value if isinstance(value, str) and SHA256_RE.fullmatch(value) else None


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, record_type + '|' + stable_key)}"


def native_stable_key(source_file: str, native_type: str, native_id: str) -> str:
    return f"erdman:{source_file}:{native_type}:{native_id}"


def safe_relative(relative: str) -> PurePosixPath:
    value = PurePosixPath(relative)
    if (
        not relative
        or value.is_absolute()
        or any(part in ("", ".", "..") for part in value.parts)
        or "\\" in relative
        or re.match(r"^[A-Za-z]:", relative)
    ):
        raise ValueError(f"unsafe relative path: {relative!r}")
    return value


def resolve_under(root: Path, relative: str) -> Path:
    value = safe_relative(relative)
    candidate = root.joinpath(*value.parts).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError(f"path escapes authority root: {relative!r}")
    return candidate


def parse_manifest(
    path: Path,
    expected_bytes: int,
    expected_sha256: str,
    expected_rows: int,
    expected_member_bytes: int,
    backend_root: Path,
    label: str,
) -> list[dict[str, Any]]:
    payload = exact_file(path, expected_bytes, expected_sha256, label)
    if b"\r" in payload or not payload.endswith(b"\n"):
        raise ValueError(f"{label} is not LF-terminated UTF-8 CSV")
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    if reader.fieldnames != ["relative_path", "bytes", "sha256"]:
        raise ValueError(f"{label} headers changed: {reader.fieldnames}")
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    total_bytes = 0
    for ordinal, row in enumerate(reader, start=1):
        if None in row:
            raise ValueError(f"{label} row {ordinal} has surplus fields")
        relative = row["relative_path"]
        if relative in seen:
            raise ValueError(f"{label} has duplicate member: {relative}")
        seen.add(relative)
        try:
            size = int(row["bytes"])
        except ValueError as exc:
            raise ValueError(f"{label} row {ordinal} has invalid bytes") from exc
        digest = row["sha256"]
        if not SHA256_RE.fullmatch(digest):
            raise ValueError(f"{label} row {ordinal} has invalid SHA-256")
        member = resolve_under(backend_root, relative)
        exact_file(member, size, digest, f"{label} member {relative}")
        entries.append({"bytes": size, "path": relative, "sha256": digest})
        total_bytes += size
    if len(entries) != expected_rows or total_bytes != expected_member_bytes:
        raise ValueError(
            f"{label} closure mismatch: rows={len(entries)}, bytes={total_bytes}"
        )
    return entries


def read_json_exact(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> dict[str, Any]:
    payload = exact_file(path, expected_bytes, expected_sha256, label)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root is not an object")
    return value


def verify_schema(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, Any]:
    payload = exact_file(path, expected_bytes, expected_sha256, path.name)
    schema = json.loads(payload.decode("utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def verify_release_archive(path: Path) -> dict[str, Any]:
    exact_file(
        path,
        EXPECTED_RELEASE_ARCHIVE_BYTES,
        EXPECTED_RELEASE_ARCHIVE_SHA256,
        "frozen D20 public release archive",
    )
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        file_infos = [info for info in infos if not info.is_dir()]
        if len(file_infos) != EXPECTED_RELEASE_ARCHIVE_FILES:
            raise ValueError(
                f"release archive file count changed: {len(file_infos)}"
            )
        names: set[str] = set()
        casefold_names: set[str] = set()
        for info in file_infos:
            name = info.filename
            safe_relative(name)
            if name in names or name.casefold() in casefold_names:
                raise ValueError(f"release archive duplicate/case collision: {name}")
            names.add(name)
            casefold_names.add(name.casefold())
        corrupt = archive.testzip()
        if corrupt is not None:
            raise ValueError(f"release archive CRC failure: {corrupt}")
        roots = {PurePosixPath(name).parts[0] for name in names}
        if len(roots) != 1:
            raise ValueError("release archive does not have one frozen root")
        root = next(iter(roots))
        manifest_name = f"{root}/RELEASE_MANIFEST.csv"
        metadata_name = f"{root}/RELEASE_METADATA.json"
        if manifest_name not in names or metadata_name not in names:
            raise ValueError("release archive lacks embedded manifest/metadata")
        manifest_payload = archive.read(manifest_name)
        metadata_payload = archive.read(metadata_name)
        if (
            len(manifest_payload) != EXPECTED_RELEASE_MANIFEST_BYTES
            or sha256_bytes(manifest_payload) != EXPECTED_RELEASE_MANIFEST_SHA256
            or len(metadata_payload) != EXPECTED_RELEASE_METADATA_BYTES
            or sha256_bytes(metadata_payload) != EXPECTED_RELEASE_METADATA_SHA256
        ):
            raise ValueError("embedded release manifest/metadata identity changed")
        if b"\r" in manifest_payload or not manifest_payload.endswith(b"\n"):
            raise ValueError("embedded release manifest is not canonical LF CSV")
        reader = csv.DictReader(io.StringIO(manifest_payload.decode("utf-8"), newline=""))
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            raise ValueError("embedded release manifest headers changed")
        rows = list(reader)
        if len(rows) != EXPECTED_RELEASE_MANIFEST_ROWS:
            raise ValueError("embedded release manifest row count changed")
        declared_names: set[str] = set()
        for ordinal, row in enumerate(rows, start=1):
            relative = row["path"]
            safe_relative(relative)
            full = f"{root}/{relative}"
            if full not in names or full in declared_names:
                raise ValueError(f"embedded release member missing/duplicate: {relative}")
            declared_names.add(full)
            payload = archive.read(full)
            if len(payload) != int(row["bytes"]) or sha256_bytes(payload) != row["sha256"]:
                raise ValueError(f"embedded release member mismatch: {relative}")
        expected_names = declared_names | {manifest_name, metadata_name}
        if names != expected_names:
            extra = sorted(names - expected_names)
            missing = sorted(expected_names - names)
            raise ValueError(f"release archive inventory mismatch extra={extra[:3]} missing={missing[:3]}")
        metadata = json.loads(metadata_payload.decode("utf-8"))
        required_metadata = {
            "base_backend_manifest_sha256": EXPECTED_BASE_MANIFEST_SHA256,
            "companion_backend_manifest_sha256": EXPECTED_COMPANION_MANIFEST_SHA256,
            "git_commit": EXPECTED_GIT_COMMIT,
            "git_tree": EXPECTED_GIT_TREE,
            "overall_status": "complete",
            "primary_reader_bytes": EXPECTED_READER_BYTES,
            "primary_reader_sha256": EXPECTED_READER_SHA256,
        }
        for key, expected in required_metadata.items():
            if metadata.get(key) != expected:
                raise ValueError(f"release metadata has stale {key}")
    return {
        "bytes": EXPECTED_RELEASE_ARCHIVE_BYTES,
        "embedded_file_count": EXPECTED_RELEASE_ARCHIVE_FILES,
        "embedded_manifest_bytes": EXPECTED_RELEASE_MANIFEST_BYTES,
        "embedded_manifest_rows": EXPECTED_RELEASE_MANIFEST_ROWS,
        "embedded_manifest_sha256": EXPECTED_RELEASE_MANIFEST_SHA256,
        "embedded_metadata_bytes": EXPECTED_RELEASE_METADATA_BYTES,
        "embedded_metadata_sha256": EXPECTED_RELEASE_METADATA_SHA256,
        "path": "qa/release-backend-artifact-reconciliation/" + path.name,
        "sha256": EXPECTED_RELEASE_ARCHIVE_SHA256,
        "zip_crc_and_path_safety": "pass",
    }


def common_type_for(source_file: str, native_type: str) -> str:
    if source_file == "resources.jsonl":
        if native_type not in {"program", "course", "resource", "edition"}:
            raise ValueError(f"resources.jsonl has unexpected type {native_type}")
        return native_type
    if source_file == "terminology_qa.jsonl":
        return "qa_event" if native_type == "terminology_qa_provenance" else "term_variant"
    if source_file not in FILE_COMMON_TYPE:
        raise ValueError(f"unmapped owner JSONL file: {source_file}")
    return FILE_COMMON_TYPE[source_file]


def normalize_source_path(value: str) -> str:
    if "/" not in value:
        return f"source/upstream/{value}"
    return value


def parse_index_csv(path: Path) -> tuple[list[dict[str, str]], list[bytes], int, str]:
    payload = path.read_bytes()
    if b"\r" in payload or not payload.endswith(b"\n"):
        raise ValueError("index_terms.csv is not canonical LF UTF-8 CSV")
    expected_headers = [
        "id",
        "parent_segment_id",
        "source_order",
        "source_line",
        "source_index_tex",
        "target_line",
        "target_index_tex",
        "source_sha256",
        "target_sha256",
        "locale",
    ]
    text_stream = io.StringIO(payload.decode("utf-8"), newline="")
    reader = csv.DictReader(text_stream)
    if reader.fieldnames != expected_headers:
        raise ValueError(f"index_terms.csv headers changed: {reader.fieldnames}")
    rows = list(reader)
    if len(rows) != EXPECTED_AUXILIARY_INDEX_ROWS:
        raise ValueError(f"index_terms.csv row count changed: {len(rows)}")
    raw_rows: list[bytes] = []
    for row in rows:
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=expected_headers, lineterminator="\n")
        writer.writerow(row)
        raw_rows.append(stream.getvalue().encode("utf-8"))
    descriptor_hash = hashlib.sha256()
    descriptor_bytes = 0
    for ordinal, (row, raw) in enumerate(zip(rows, raw_rows), start=1):
        line = canonical_bytes(
            {
                "canonical_row_sha256": sha256_bytes(canonical_bytes(row)),
                "raw_row_sha256": sha256_bytes(raw),
                "row": row,
                "source_file": "index_terms.csv",
                "source_ordinal": ordinal,
            }
        ) + b"\n"
        descriptor_hash.update(line)
        descriptor_bytes += len(line)
    return rows, raw_rows, descriptor_bytes, descriptor_hash.hexdigest()


def make_file_pairs(owner_root: Path, unit_rows: list[NativeRow]) -> list[FilePair]:
    pairs: list[FilePair] = []
    seen_source: set[str] = set()
    seen_target: set[str] = set()
    for row in unit_rows:
        value = row.value
        if not value.get("source_path") or not value.get("target_path"):
            continue
        source_path = normalize_source_path(text(value["source_path"]))
        target_path = text(value["target_path"])
        pair = FilePair(
            unit_native_id=row.native_id,
            source_path=source_path,
            source_bytes=int(value["source_bytes"]),
            source_sha256=text(value["source_sha256"]),
            target_path=target_path,
            target_bytes=int(value["target_bytes"]),
            target_sha256=text(value["target_sha256"]),
        )
        if pair.source_path in seen_source or pair.target_path in seen_target:
            raise ValueError(f"duplicate chapter source/target file path: {row.native_id}")
        seen_source.add(pair.source_path)
        seen_target.add(pair.target_path)
        exact_file(
            resolve_under(owner_root, pair.source_path),
            pair.source_bytes,
            pair.source_sha256,
            f"source TeX for {row.native_id}",
        )
        exact_file(
            resolve_under(owner_root, pair.target_path),
            pair.target_bytes,
            pair.target_sha256,
            f"target TeX for {row.native_id}",
        )
        pairs.append(pair)
    pairs.sort(key=lambda pair: pair.unit_native_id)
    if len(pairs) != EXPECTED_SOURCE_TARGET_FILES:
        raise ValueError(f"source/target TeX closure changed: {len(pairs)}")
    return pairs


def load_snapshot(owner_root: Path, archive_path: Path) -> Snapshot:
    backend_root = owner_root / "backend"
    base_entries = parse_manifest(
        backend_root / "BACKEND_MANIFEST.csv",
        EXPECTED_BASE_MANIFEST_BYTES,
        EXPECTED_BASE_MANIFEST_SHA256,
        EXPECTED_BASE_MANIFEST_ROWS,
        EXPECTED_BASE_MEMBER_BYTES,
        backend_root,
        "base backend manifest",
    )
    companion_entries = parse_manifest(
        backend_root / "COMPANION_BACKEND_MANIFEST.csv",
        EXPECTED_COMPANION_MANIFEST_BYTES,
        EXPECTED_COMPANION_MANIFEST_SHA256,
        EXPECTED_COMPANION_MANIFEST_ROWS,
        EXPECTED_COMPANION_MEMBER_BYTES,
        backend_root,
        "companion backend manifest",
    )
    duplicate_manifest_paths = {entry["path"] for entry in base_entries} & {
        entry["path"] for entry in companion_entries
    }
    if duplicate_manifest_paths:
        raise ValueError(f"base/companion manifest overlap: {sorted(duplicate_manifest_paths)}")

    companion_validation = read_json_exact(
        owner_root / "qa" / "COMPANION_BACKEND_VALIDATION.json",
        EXPECTED_COMPANION_VALIDATION_BYTES,
        EXPECTED_COMPANION_VALIDATION_SHA256,
        "companion backend validation",
    )
    if companion_validation.get("result") != "pass" and companion_validation.get("status") != "pass":
        raise ValueError("companion backend validation is not a passing witness")
    handoff = read_json_exact(
        owner_root / "provenance" / "O008_COORDINATOR_HANDOFF_FINAL.json",
        EXPECTED_HANDOFF_BYTES,
        EXPECTED_HANDOFF_SHA256,
        "final D20 coordinator handoff",
    )
    if (
        handoff.get("status") != "complete"
        or handoff.get("publication", {}).get("zenodo", {}).get("version_doi")
        != PUBLIC_ZENODO_DOI
        or handoff.get("publication", {})
        .get("github", {})
        .get("backend_artifact_reconciliation_commit")
        != EXPECTED_GIT_COMMIT
    ):
        raise ValueError("final D20 handoff is incomplete or stale")
    pages_handoff = read_json_exact(
        owner_root / "provenance" / "GITHUB_PAGES_DEPLOYMENT_HANDOFF.json",
        EXPECTED_PAGES_HANDOFF_BYTES,
        EXPECTED_PAGES_HANDOFF_SHA256,
        "D20 GitHub Pages deployment handoff",
    )
    pages_receipt = read_json_exact(
        owner_root / "provenance" / "GITHUB_PAGES_PUBLICATION_RECEIPT.json",
        EXPECTED_PAGES_RECEIPT_BYTES,
        EXPECTED_PAGES_RECEIPT_SHA256,
        "D20 GitHub Pages publication receipt",
    )
    readback_by_url = {
        row.get("url"): row
        for row in pages_receipt.get("required_url_readback", [])
        if isinstance(row, dict) and isinstance(row.get("url"), str)
    }
    primary_readback = readback_by_url.get(PUBLIC_HTML_READER_URL)
    if (
        pages_handoff.get("schema") != "o008.github-pages.deployment-handoff.v1"
        or pages_handoff.get("status") != "complete"
        or pages_handoff.get("central_hub_ingestion", {}).get("primary_reader_url")
        != PUBLIC_HTML_READER_URL
        or pages_handoff.get("central_hub_ingestion", {}).get("secondary_reader_url")
        != PUBLIC_HTML_COMPANION_URL
        or pages_handoff.get("deployment", {}).get("commit") != EXPECTED_PAGES_GIT_COMMIT
        or pages_handoff.get("deployment", {}).get("tree") != EXPECTED_PAGES_GIT_TREE
        or pages_handoff.get("verification", {})
        .get("anonymous_public_readback", {})
        .get("result")
        != "pass"
        or pages_handoff.get("verification", {})
        .get("publication_receipt", {})
        .get("sha256")
        != EXPECTED_PAGES_RECEIPT_SHA256
        or pages_receipt.get("result") != "pass"
        or pages_receipt.get("credential_material_recorded") is not False
        or pages_receipt.get("repository", {}).get("commit") != EXPECTED_PAGES_GIT_COMMIT
        or pages_receipt.get("repository", {}).get("tree") != EXPECTED_PAGES_GIT_TREE
        or pages_receipt.get("pages", {}).get("root") != PUBLIC_HTML_READER_URL
        or pages_receipt.get("public_file_readback", {}).get(
            "all_files_match_manifest_and_tracked_sources"
        )
        is not True
        or pages_receipt.get("public_file_readback", {}).get("file_count") != 128
        or not isinstance(primary_readback, dict)
        or primary_readback.get("http_status") != 200
        or not isinstance(primary_readback.get("sha256"), str)
    ):
        raise ValueError("D20 GitHub Pages public-reader evidence is incomplete or stale")
    archive_evidence = verify_release_archive(archive_path)

    manifest_paths = {entry["path"] for entry in base_entries + companion_entries}
    expected_jsonl = set(EXPECTED_RECORD_COUNTS_BY_FILE)
    if not expected_jsonl <= manifest_paths:
        raise ValueError(
            f"owner manifests omit JSONL authority files: {sorted(expected_jsonl - manifest_paths)}"
        )
    if "index_terms.csv" not in manifest_paths:
        raise ValueError("owner manifests omit index_terms.csv")

    rows: list[NativeRow] = []
    rows_by_file: dict[str, list[NativeRow]] = {}
    rows_by_native_id: dict[str, list[NativeRow]] = defaultdict(list)
    counts_by_file: Counter[str] = Counter()
    common_ids: set[str] = set()
    native_stream_hash = hashlib.sha256()
    native_stream_bytes = 0

    for source_file in sorted(expected_jsonl):
        path = backend_root / source_file
        file_rows: list[NativeRow] = []
        with path.open("rb") as stream:
            for ordinal, raw_line in enumerate(stream, start=1):
                if raw_line == b"\n" or not raw_line.endswith(b"\n") or b"\r" in raw_line:
                    raise ValueError(f"{source_file} row {ordinal} is not canonical LF JSONL")
                try:
                    value = json.loads(raw_line[:-1].decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"{source_file} row {ordinal} is invalid JSON: {exc}") from exc
                if not isinstance(value, dict):
                    raise ValueError(f"{source_file} row {ordinal} is not a JSON object")
                if value.get("schema") not in (None, SOURCE_SCHEMA_NAME) or value.get(
                    "schema_version"
                ) not in (None, SOURCE_SCHEMA_VERSION):
                    raise ValueError(f"{source_file} row {ordinal} has stale native schema")
                native_id = value.get("id")
                native_type = value.get("record_type")
                if not isinstance(native_id, str) or not native_id:
                    raise ValueError(f"{source_file} row {ordinal} lacks native ID")
                if not isinstance(native_type, str) or not native_type:
                    raise ValueError(f"{source_file} row {ordinal} lacks native type")
                common_type = common_type_for(source_file, native_type)
                stable_key = native_stable_key(source_file, native_type, native_id)
                target_id = rid(common_type, stable_key)
                if target_id in common_ids:
                    raise ValueError(f"deterministic common ID collision: {stable_key}")
                common_ids.add(target_id)
                native_row = NativeRow(
                    source_file=source_file,
                    source_ordinal=ordinal,
                    raw_line=raw_line,
                    value=value,
                    native_id=native_id,
                    native_type=native_type,
                    common_type=common_type,
                    stable_key=stable_key,
                    target_id=target_id,
                )
                rows.append(native_row)
                file_rows.append(native_row)
                rows_by_native_id[native_id].append(native_row)
                counts_by_file[source_file] += 1
                descriptor = canonical_bytes(
                    {
                        "canonical_native_sha256": native_row.canonical_native_sha256,
                        "native_id": native_id,
                        "native_record_type": native_type,
                        "raw_line_sha256": native_row.raw_line_sha256,
                        "source_file": source_file,
                        "source_ordinal": ordinal,
                    }
                ) + b"\n"
                native_stream_hash.update(descriptor)
                native_stream_bytes += len(descriptor)
        rows_by_file[source_file] = file_rows

    if dict(sorted(counts_by_file.items())) != EXPECTED_RECORD_COUNTS_BY_FILE:
        raise ValueError(f"native record census changed: {dict(sorted(counts_by_file.items()))}")
    if len(rows) != EXPECTED_NATIVE_RECORDS:
        raise ValueError(f"native record total changed: {len(rows)}")

    primary_by_native_id: dict[str, NativeRow] = {}
    duplicate_raw_ids = 0
    for native_id, candidates in rows_by_native_id.items():
        non_alias = [row for row in candidates if row.common_type != "alias"]
        if len(non_alias) > 1:
            raise ValueError(f"raw native ID has multiple non-route owners: {native_id}")
        primary_by_native_id[native_id] = non_alias[0] if non_alias else sorted(
            candidates, key=lambda row: row.tuple_key
        )[0]
        duplicate_raw_ids += len(candidates) - 1
        if len(candidates) > 1 and any(row.common_type != "alias" for row in candidates) is False:
            raise ValueError(f"raw native ID collision lacks a primary carrier: {native_id}")
    if duplicate_raw_ids != 4_161:
        raise ValueError(f"native route-ID overlap count changed: {duplicate_raw_ids}")

    relation_refs: set[str] = set()
    for source_file in ("relations.jsonl", "concept_relations.jsonl", "companion_relations.jsonl"):
        for row in rows_by_file[source_file]:
            relation_refs.add(text(row.value.get("from_id")))
            relation_refs.add(text(row.value.get("to_id")))
    for row in rows_by_file["exercise_support.jsonl"]:
        relation_refs.add(text(row.value.get("exercise_unit_id")))
        relation_refs.add(text(row.value.get("original_solution_id")))
    external_ids = sorted(
        value for value in relation_refs if value and value not in primary_by_native_id
    )
    if (
        len(external_ids) != EXPECTED_EXTERNAL_ANCHORS
        or external_ids.count(EXTERNAL_COURSE_NATIVE_ID) != 1
        or sum(value.startswith("ERDMAN-FAOA-BIB-") for value in external_ids) != 55
        or sum(value.startswith("ERDMAN-FAOA-2015-LABEL-") for value in external_ids) != 12
    ):
        raise ValueError(f"external relation-anchor census changed: {external_ids[:5]}")

    index_path = backend_root / "index_terms.csv"
    index_rows, index_raw_rows, auxiliary_bytes, auxiliary_sha = parse_index_csv(index_path)
    if sha256_file(index_path) != "8b79780b1d25cf3e6c0863bb04d19360891b5c48c34e69bb8dea9d47b1e0fd6b":
        raise ValueError("index_terms.csv authority hash changed")

    file_pairs = make_file_pairs(owner_root, rows_by_file["units.jsonl"])
    source_revision_by_unit: dict[str, str] = {}
    target_revision_by_unit: dict[str, str] = {}
    for pair in file_pairs:
        source_file_key = f"erdman:derived:file:en:{pair.source_path}"
        target_file_key = f"erdman:derived:file:id-ID:{pair.target_path}"
        source_revision_by_unit[pair.unit_native_id] = rid(
            "file_revision", source_file_key + ":revision"
        )
        target_revision_by_unit[pair.unit_native_id] = rid(
            "file_revision", target_file_key + ":revision"
        )

    public_evidence = {
        "archive": archive_evidence,
        "companion_validation": {
            "bytes": EXPECTED_COMPANION_VALIDATION_BYTES,
            "path": "qa/COMPANION_BACKEND_VALIDATION.json",
            "sha256": EXPECTED_COMPANION_VALIDATION_SHA256,
        },
        "git_commit": EXPECTED_GIT_COMMIT,
        "git_tree": EXPECTED_GIT_TREE,
        "handoff": {
            "bytes": EXPECTED_HANDOFF_BYTES,
            "path": "provenance/O008_COORDINATOR_HANDOFF_FINAL.json",
            "sha256": EXPECTED_HANDOFF_SHA256,
        },
        "html_reader": {
            "companion_url": PUBLIC_HTML_COMPANION_URL,
            "deployment_commit": EXPECTED_PAGES_GIT_COMMIT,
            "deployment_handoff": {
                "bytes": EXPECTED_PAGES_HANDOFF_BYTES,
                "path": "provenance/GITHUB_PAGES_DEPLOYMENT_HANDOFF.json",
                "sha256": EXPECTED_PAGES_HANDOFF_SHA256,
            },
            "deployment_tree": EXPECTED_PAGES_GIT_TREE,
            "publication_receipt": {
                "bytes": EXPECTED_PAGES_RECEIPT_BYTES,
                "path": "provenance/GITHUB_PAGES_PUBLICATION_RECEIPT.json",
                "sha256": EXPECTED_PAGES_RECEIPT_SHA256,
            },
            "readback": {
                "bytes": primary_readback["bytes"],
                "http_status": primary_readback["http_status"],
                "sha256": primary_readback["sha256"],
            },
            "result": "pass",
            "url": PUBLIC_HTML_READER_URL,
        },
        "repository": PUBLIC_REPOSITORY,
        "reader": {
            "bytes": EXPECTED_READER_BYTES,
            "filename": PUBLIC_READER_FILENAME,
            "sha256": EXPECTED_READER_SHA256,
            "url": PUBLIC_READER_URL,
        },
        "zenodo_doi": PUBLIC_ZENODO_DOI,
        "zenodo_record": PUBLIC_ZENODO_RECORD,
    }
    manifest_facts = {
        "base": {
            "bytes": EXPECTED_BASE_MANIFEST_BYTES,
            "member_bytes": EXPECTED_BASE_MEMBER_BYTES,
            "members": EXPECTED_BASE_MANIFEST_ROWS,
            "path": "backend/BACKEND_MANIFEST.csv",
            "sha256": EXPECTED_BASE_MANIFEST_SHA256,
        },
        "companion": {
            "bytes": EXPECTED_COMPANION_MANIFEST_BYTES,
            "member_bytes": EXPECTED_COMPANION_MEMBER_BYTES,
            "members": EXPECTED_COMPANION_MANIFEST_ROWS,
            "path": "backend/COMPANION_BACKEND_MANIFEST.csv",
            "sha256": EXPECTED_COMPANION_MANIFEST_SHA256,
        },
    }
    return Snapshot(
        owner_root=owner_root,
        backend_root=backend_root,
        rows=rows,
        rows_by_file=rows_by_file,
        rows_by_native_id=dict(rows_by_native_id),
        primary_by_native_id=primary_by_native_id,
        index_rows=index_rows,
        index_raw_rows=index_raw_rows,
        external_ids=external_ids,
        file_pairs=file_pairs,
        source_revision_by_unit=source_revision_by_unit,
        target_revision_by_unit=target_revision_by_unit,
        manifest_facts=manifest_facts,
        public_evidence=public_evidence,
        native_stream_bytes=native_stream_bytes,
        native_stream_sha256=native_stream_hash.hexdigest(),
        auxiliary_stream_bytes=auxiliary_bytes,
        auxiliary_stream_sha256=auxiliary_sha,
        handoff=handoff,
    )


class Builder:
    def __init__(self, snapshot: Snapshot, schema: dict[str, Any]) -> None:
        self.snapshot = snapshot
        self.schema = schema
        schema_tables = set(schema["properties"]["tables"]["required"])
        if schema_tables != set(TABLE_TO_RECORD_TYPE):
            raise ValueError("common backend table inventory changed")
        self.tables: dict[str, list[dict[str, Any]]] = {
            name: [] for name in sorted(TABLE_TO_RECORD_TYPE)
        }
        self.claimed_native: set[tuple[str, int, str, str]] = set()
        self.generated_records = 0
        self.segment_payload_checks = 0
        self.index_roundtrip_checks = 0

    def base(
        self,
        record_type: str,
        stable_key: str,
        *,
        status: str = "admitted",
        extensions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": rid(record_type, stable_key),
            "record_type": record_type,
            "recorded_at": RECORDED_AT,
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "stable_key": stable_key,
            "status": status,
            "supersedes_id": None,
            "workflow_id": WORKFLOW_ID,
        }
        if extensions:
            result["extensions"] = extensions
        return result

    def native_base(self, row: NativeRow, *, status: str = "admitted") -> dict[str, Any]:
        if row.tuple_key in self.claimed_native:
            raise ValueError(f"native row claimed twice: {row.tuple_key}")
        self.claimed_native.add(row.tuple_key)
        extension = {
            NATIVE_EXTENSION: {
                "canonical_native_sha256": row.canonical_native_sha256,
                "native_id": row.native_id,
                "native_record": row.value,
                "native_record_type": row.native_type,
                "raw_line_sha256": row.raw_line_sha256,
                "source_ordinal": row.source_ordinal,
                "source_path": f"backend/{row.source_file}",
            }
        }
        record = self.base(row.common_type, row.stable_key, status=status, extensions=extension)
        if record["id"] != row.target_id:
            raise ValueError(f"native target ID derivation changed: {row.tuple_key}")
        return record

    def derived_base(
        self,
        record_type: str,
        stable_key: str,
        projection_kind: str,
        sources: Iterable[str],
        *,
        extra: dict[str, Any] | None = None,
        status: str = "admitted",
    ) -> dict[str, Any]:
        extension = {
            DERIVED_EXTENSION: {
                "projection_kind": projection_kind,
                "source_identities": sorted(set(sources)),
            }
        }
        if extra:
            extension[DERIVED_EXTENSION].update(extra)
        self.generated_records += 1
        return self.base(record_type, stable_key, status=status, extensions=extension)

    def add(self, table: str, record: dict[str, Any]) -> None:
        if record.get("record_type") != TABLE_TO_RECORD_TYPE[table]:
            raise ValueError(f"record type/table mismatch: {table}/{record.get('record_type')}")
        if record.get("id") != rid(record["record_type"], record["stable_key"]):
            raise ValueError(f"UUIDv5 identity mismatch: {record.get('stable_key')}")
        self.tables[table].append(record)

    def raw_id(self, native_id: Any, field: str, *, fallback: str | None = None) -> str:
        if isinstance(native_id, str) and native_id in self.snapshot.primary_by_native_id:
            return self.snapshot.primary_by_native_id[native_id].target_id
        if isinstance(native_id, str) and native_id in self.snapshot.external_ids:
            if native_id == EXTERNAL_COURSE_NATIVE_ID:
                return rid("course", f"erdman:derived:external-course:{native_id}")
            return rid("unit", f"erdman:derived:external-anchor:{native_id}")
        if fallback is not None:
            return fallback
        raise ValueError(f"unresolved native reference {field}={native_id!r}")

    def direct(self, row: NativeRow) -> dict[str, Any]:
        value = row.value
        record = self.native_base(
            row,
            status=(
                "complete"
                if row.native_id
                in {PROGRAM_NATIVE_ID, COURSE_NATIVE_ID, SOURCE_EDITION_NATIVE_ID, TARGET_EDITION_NATIVE_ID}
                else "admitted"
            ),
        )
        source_locator = f"backend/{row.source_file}#L{row.source_ordinal}"
        resource_id = self.raw_id(RESOURCE_NATIVE_ID, "resource")
        source_edition_id = self.raw_id(SOURCE_EDITION_NATIVE_ID, "source edition")
        target_edition_id = self.raw_id(TARGET_EDITION_NATIVE_ID, "target edition")
        erdman_rights_id = self.raw_id(ERDMAN_RIGHTS_NATIVE_ID, "Erdman rights")
        original_rights_id = self.raw_id(ORIGINAL_RIGHTS_NATIVE_ID, "original rights")

        if row.common_type == "program":
            record.update(
                curriculum_version=PUBLIC_VERSION,
                locale="id-ID",
                program_key=text(value.get("curriculum_role"), "O008/D20"),
                rights_id=erdman_rights_id,
                title=text(value.get("title"), "Analisis Fungsional"),
            )
        elif row.common_type == "course":
            record.update(
                course_key="D20",
                order_key="D20",
                program_id=self.raw_id(value.get("program_id"), "course.program_id"),
                role="O008/D20",
                prerequisite_course_keys=["O007"],
                resource_keys=[RESOURCE_NATIVE_ID],
                scope="complete 17-chapter source text with mastery and spectral/SVD companions",
                stage="advanced undergraduate / graduate transition",
                title=text(value.get("title_id_ID"), "Analisis Fungsional"),
            )
        elif row.common_type == "resource":
            record.update(
                authority_policy=(
                    "Frozen official source bytes, exact owner manifests, completed public-byte "
                    "readback, and reversible common-backend adapter"
                ),
                creator_name=text(value.get("author"), "John M. Erdman"),
                official_reader=(
                    "https://web.pdx.edu/~erdman/FAOA/"
                    "functional_analysis_operator_algebras_pdf.pdf"
                ),
                official_repository=text(value.get("official_home"), "https://web.pdx.edu/~erdman/"),
                original_title=text(value.get("title")),
                resource_key=RESOURCE_NATIVE_ID,
                work_type="open functional-analysis and operator-algebras textbook",
            )
        elif row.common_type == "edition":
            derivative = row.native_id == TARGET_EDITION_NATIVE_ID
            record.update(
                archive_sha256=(
                    EXPECTED_RELEASE_ARCHIVE_SHA256
                    if derivative
                    else valid_sha256(value.get("source_archive_sha256"))
                ),
                commit_sha=EXPECTED_GIT_COMMIT,
                edition_kind=(
                    "complete-Indonesian-translation-and-bounded-companion"
                    if derivative
                    else "frozen-source-authority"
                ),
                locale="id-ID" if derivative else "en",
                release_date="2026-08-25" if derivative else "2015-10-04",
                resource_id=self.raw_id(value.get("resource_id"), "edition.resource_id"),
                rights_id=self.raw_id(
                    value.get("rights_id") or ERDMAN_RIGHTS_NATIVE_ID,
                    "edition.rights_id",
                ),
                source_edition_id=(
                    self.raw_id(value.get("source_edition_id"), "edition.source_edition_id")
                    if derivative
                    else None
                ),
                tree_sha=EXPECTED_GIT_TREE,
                vcs_ref=EXPECTED_GIT_COMMIT,
                vcs_type="git",
                version_label=PUBLIC_VERSION if derivative else text(value.get("version"), "2015-10-04"),
            )
        elif row.common_type == "rights":
            change_required = value.get("change_notice_required")
            nonendorsement = value.get("nonendorsement")
            record.update(
                assertion_status="frozen-owner-native-rights-record",
                attribution=text(value.get("attribution"), text(value.get("applies_to"), row.native_id)),
                authority=text(value.get("source"), source_locator),
                change_notice=(
                    "required" if change_required is True else "not asserted"
                ),
                license_expression=text(value.get("license"), "NOASSERTION"),
                nonendorsement=text(nonendorsement, "No endorsement is implied."),
                notice_locator=text(value.get("source"), source_locator),
                notice_sha256=row.canonical_native_sha256,
                source_component_id=text(value.get("applies_to"), row.native_id),
                third_party_status=text(value.get("target_disposition"), "explicit component rights"),
            )
        elif row.common_type == "unit":
            companion = row.source_file in {
                "bridge_units.jsonl",
                "companion_components.jsonl",
                "o001_mastery.jsonl",
            } or row.native_type == "original_companion"
            rights_native = value.get("rights_id")
            if not rights_native and isinstance(value.get("rights_ids"), list):
                rights_native = value["rights_ids"][0] if value["rights_ids"] else None
            if not rights_native:
                rights_native = ORIGINAL_RIGHTS_NATIVE_ID if companion else ERDMAN_RIGHTS_NATIVE_ID
            path_value = (
                value.get("source_path")
                or value.get("component_source_path")
                or value.get("path")
                or source_locator
            )
            if row.source_file == "units.jsonl" and isinstance(path_value, str):
                path_value = normalize_source_path(path_value) if path_value.endswith(".tex") else path_value
            record.update(
                first_edition_id=(target_edition_id if companion else self.raw_id(
                    value.get("edition_id") or SOURCE_EDITION_NATIVE_ID,
                    "unit.first_edition_id",
                )),
                identity_anchor=row.native_id,
                identity_basis="owner-native stable semantic ID",
                resource_id=resource_id,
                rights_default_id=self.raw_id(rights_native, "unit.rights_default_id"),
                source_label=(
                    value.get("target_title")
                    or value.get("title")
                    or value.get("title_tex")
                    or value.get("source_title_tex")
                ),
                source_local_id=row.native_id,
                source_path=text(path_value),
                source_xml_path=None,
                unit_kind=text(value.get("unit_kind"), row.native_type),
            )
        elif row.common_type == "segment":
            record.update(
                identity_anchor=row.native_id,
                ordinal=int(value.get("order", row.source_ordinal)),
                segment_kind=text(value.get("segment_role"), "translation-segment"),
                segmentation_profile="erdman-line-bound-hash-anchored-v0.1.0",
                unit_id=self.raw_id(value.get("parent_id"), "segment.unit_id"),
            )
        elif row.common_type == "concept":
            record.update(
                concept_key=row.native_id,
                concept_scheme="erdman-functional-analysis-owner-lexicon-v0.1.0",
                definition_segment_id=None,
                parent_concept_id=None,
            )
        elif row.common_type == "term":
            if value.get("concept_id"):
                concept_id = self.raw_id(value["concept_id"], "term.concept_id")
            else:
                concept_id = rid("concept", f"erdman:derived:concept-for-term:{row.native_id}")
            introduced = value.get("introduced_in_unit")
            scope_unit = (
                self.raw_id(introduced, "term.scope_unit_id")
                if introduced
                else rid("unit", SCOPE_UNIT_STABLE_KEY)
            )
            record.update(
                concept_id=concept_id,
                evidence=text(value.get("evidence"), source_locator),
                notes=text(value.get("scope")),
                preferred_form=text(value.get("preferred")),
                register=text(value.get("register"), "mathematical Indonesian"),
                scope_unit_id=scope_unit,
                source_form=text(value.get("source_term")),
                source_locale="en",
                source_term_id=row.native_id,
                target_locale=text(value.get("locale"), "id-ID"),
                term_status="admitted",
            )
        elif row.common_type == "term_variant":
            if row.native_type == "future_domain_term_variant":
                term_id = rid("term", "erdman:derived:future-term:TERM-WEAKLY-MEASURABLE")
            else:
                term_id = self.raw_id(value.get("term_id"), "term_variant.term_id")
            forms = value.get("variants")
            form = " / ".join(map(str, forms)) if isinstance(forms, list) and forms else text(
                value.get("preferred"), row.native_id
            )
            record.update(
                form=form,
                locale=text(value.get("locale"), "id-ID"),
                rationale=text(value.get("scope") or value.get("evidence_basis"), source_locator),
                term_id=term_id,
                variant_kind=text(value.get("variant_state"), "recognition-evidence-carrier"),
            )
        elif row.common_type == "alignment":
            match = CHAPTER_ID_RE.match(row.native_id)
            if match is None:
                raise ValueError(f"formula row lacks chapter prefix: {row.native_id}")
            unit_native_id = match.group(1)
            source_hashes = value.get("source_sha256") or []
            target_hashes = value.get("target_sha256") or []
            source_hash = (
                source_hashes[0]
                if len(source_hashes) == 1
                else sha256_bytes(canonical_bytes(source_hashes)) if source_hashes else None
            )
            target_hash = (
                target_hashes[0]
                if len(target_hashes) == 1
                else sha256_bytes(canonical_bytes(target_hashes)) if target_hashes else None
            )
            record.update(
                alignment_kind="mathematical-formula-preservation",
                assertion_method=text(value.get("alignment"), "owner-native formula map"),
                confidence="exact-hash-anchored",
                evidence_locator=source_locator,
                source_id=self.snapshot.source_revision_by_unit[unit_native_id],
                source_locale="en",
                source_sha256=source_hash,
                target_id=self.snapshot.target_revision_by_unit[unit_native_id],
                target_locale="id-ID",
                target_sha256=target_hash,
            )
        elif row.common_type == "relation":
            if row.source_file == "exercise_support.jsonl":
                from_native = value.get("exercise_unit_id")
                to_native = value.get("original_solution_id")
                relation_type = "exercise-supported-by-original-solution"
                ordinal = int(value.get("source_exercise_order", row.source_ordinal))
            else:
                from_native = value.get("from_id")
                to_native = value.get("to_id")
                relation_type = text(value.get("relation_type"), row.native_type)
                ordinal = int(value.get("ordinal", row.source_ordinal))
            record.update(
                assertion_method="explicit owner-native relation carrier",
                confidence="explicit",
                edition_id=target_edition_id,
                from_id=self.raw_id(from_native, "relation.from_id"),
                ordinal=ordinal,
                relation_type=relation_type,
                source_locator=source_locator,
                strength="asserted",
                to_id=self.raw_id(to_native, "relation.to_id"),
            )
        elif row.common_type == "asset":
            path_value = (
                value.get("path")
                or value.get("target_path")
                or value.get("source_path")
                or row.native_id
            )
            rights_native = (
                value.get("rights_id")
                or value.get("rendering_component_rights_id")
                or ERDMAN_RIGHTS_NATIVE_ID
            )
            record.update(
                asset_kind=text(value.get("asset_kind"), row.native_type),
                canonical_path_or_uri=text(path_value),
                media_type=media_type(text(path_value)),
                resource_id=resource_id,
                rights_default_id=self.raw_id(rights_native, "asset.rights_default_id"),
            )
        elif row.common_type == "correction":
            unit_native_id = text(value.get("unit_id"))
            pair = next(
                (candidate for candidate in self.snapshot.file_pairs if candidate.unit_native_id == unit_native_id),
                None,
            )
            if pair is None:
                raise ValueError(f"correction lacks enclosing chapter file: {row.native_id}")
            original = valid_sha256(value.get("source_normalized_snippet_sha256"))
            replacement = valid_sha256(value.get("target_normalized_snippet_sha256"))
            fallback = original is None or replacement is None
            original = original or pair.source_sha256
            replacement = replacement or pair.target_sha256
            record.update(
                affected_id=self.raw_id(unit_native_id, "correction.affected_id"),
                category=text(value.get("correction_type"), "source-correction"),
                evidence_locator=text(value.get("source_locator"), source_locator),
                local_state=text(value.get("target_disposition"), "corrected"),
                original_payload_sha256=original,
                payload_hash_basis=(
                    "enclosing-unit-file fallback for missing snippet hashes"
                    if fallback
                    else "normalized source and target snippet hashes"
                ),
                rationale=text(value.get("summary") or value.get("decision"), "owner-admitted correction"),
                replacement_payload_sha256=replacement,
                source_edition_id=source_edition_id,
                upstream_disposition=text(value.get("upstream_report"), "not contacted"),
                upstream_url=None,
            )
        elif row.common_type == "qa_event":
            record.update(
                input_hash=row.canonical_native_sha256,
                method="frozen owner-native QA/provenance carrier",
                qa_type=text(value.get("qa_type"), row.native_type),
                result=text(
                    value.get("result")
                    or value.get("validation_state")
                    or value.get("admission_state"),
                    "pass",
                ),
                reviewer_kind="owner-native deterministic workflow",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name=text(value.get("model") or value.get("creation_agent") or value.get("responsible_workflow"), "Codex"),
                tool_version=SOURCE_SCHEMA_VERSION,
                witness_locator=text(value.get("witness") or value.get("qa_report_path"), source_locator),
            )
        elif row.common_type == "artifact":
            artifact_hash = valid_sha256(value.get("sha256"))
            if artifact_hash is None and value.get("site_inventory_sha256"):
                artifact_hash = valid_sha256(value.get("site_inventory_sha256"))
            artifact_bytes = value.get("bytes")
            if artifact_bytes is None:
                artifact_bytes = value.get("site_bytes")
            public_uri = PUBLIC_READER_URL if artifact_hash == EXPECTED_READER_SHA256 else None
            record.update(
                artifact_kind=text(value.get("artifact_kind") or value.get("surface_kind"), row.native_type),
                build_receipt=text(value.get("qa_receipt_id") or value.get("validation_state"), "owner-native build evidence"),
                bytes=int(artifact_bytes) if artifact_bytes is not None else None,
                edition_id=target_edition_id,
                locale=text(value.get("locale"), "id-ID"),
                manifest_sha256=valid_sha256(value.get("site_manifest_sha256")),
                public_uri=public_uri,
                sha256=artifact_hash,
                toolchain_id=text(value.get("toolchain"), "owner-native deterministic toolchain"),
                tree_sha256=None,
            )
        elif row.common_type == "alias":
            entity_native = value.get("target_stable_id") or row.native_id
            entity_id = self.raw_id(
                entity_native,
                "alias.entity_id",
                fallback=target_edition_id,
            )
            record.update(
                edition_id=target_edition_id,
                entity_id=entity_id,
                scheme="semantic-html-route",
                scope=text(value.get("output_path") or value.get("route"), "edition reader"),
                unique_in_scope=True,
                value=text(value.get("href"), row.native_id),
            )
        else:
            raise ValueError(f"unhandled direct common type: {row.common_type}")
        return record

    def build_direct_records(self) -> None:
        for row in self.snapshot.rows:
            table = RECORD_TYPE_TO_TABLE[row.common_type]
            self.add(table, self.direct(row))

    def build_files(self) -> None:
        resource_id = self.raw_id(RESOURCE_NATIVE_ID, "file.resource_id")
        source_edition_id = self.raw_id(SOURCE_EDITION_NATIVE_ID, "file source edition")
        target_edition_id = self.raw_id(TARGET_EDITION_NATIVE_ID, "file target edition")
        for pair in self.snapshot.file_pairs:
            source_key = f"erdman:derived:file:en:{pair.source_path}"
            target_key = f"erdman:derived:file:id-ID:{pair.target_path}"
            source_file = self.derived_base(
                "file",
                source_key,
                "chapter-source-file",
                [pair.unit_native_id],
                extra={"authority_sha256": pair.source_sha256},
            )
            source_file.update(
                canonical_path=pair.source_path,
                media_type="text/x-tex",
                parse_mode="latex",
                resource_id=resource_id,
                role="source-text",
            )
            self.add("files", source_file)
            target_file = self.derived_base(
                "file",
                target_key,
                "chapter-target-file",
                [pair.unit_native_id],
                extra={"authority_sha256": pair.target_sha256},
            )
            target_file.update(
                canonical_path=pair.target_path,
                media_type="text/x-tex",
                parse_mode="latex",
                resource_id=resource_id,
                role="Indonesian-translated-text",
            )
            self.add("files", target_file)

            source_revision_key = source_key + ":revision"
            source_revision = self.derived_base(
                "file_revision",
                source_revision_key,
                "chapter-source-file-revision",
                [pair.unit_native_id],
            )
            source_revision.update(
                actual_path=pair.source_path,
                bytes=pair.source_bytes,
                edition_id=source_edition_id,
                file_id=source_file["id"],
                generated=False,
                git_blob_sha1=None,
                sha256=pair.source_sha256,
                source_revision_id=None,
            )
            self.add("file_revisions", source_revision)
            target_revision = self.derived_base(
                "file_revision",
                target_key + ":revision",
                "chapter-target-file-revision",
                [pair.unit_native_id],
            )
            target_revision.update(
                actual_path=pair.target_path,
                bytes=pair.target_bytes,
                edition_id=target_edition_id,
                file_id=target_file["id"],
                generated=False,
                git_blob_sha1=None,
                sha256=pair.target_sha256,
                source_revision_id=source_revision["id"],
            )
            self.add("file_revisions", target_revision)

    def build_external_and_scope_units(self) -> None:
        program_id = self.raw_id(PROGRAM_NATIVE_ID, "external course program")
        resource_id = self.raw_id(RESOURCE_NATIVE_ID, "external unit resource")
        source_edition_id = self.raw_id(SOURCE_EDITION_NATIVE_ID, "external unit edition")
        rights_id = self.raw_id(ERDMAN_RIGHTS_NATIVE_ID, "external unit rights")
        external_course = self.derived_base(
            "course",
            f"erdman:derived:external-course:{EXTERNAL_COURSE_NATIVE_ID}",
            "external-prerequisite-course-anchor",
            [EXTERNAL_COURSE_NATIVE_ID],
        )
        external_course.update(
            course_key="O007",
            order_key="O007",
            program_id=program_id,
            role="external prerequisite anchor",
            prerequisite_course_keys=[],
            resource_keys=[],
            scope="typed prerequisite anchor only; content lives in its own corpus lane",
            title="Analisis Real / Analisis Lanjut prerequisite",
        )
        self.add("courses", external_course)
        for native_id in self.snapshot.external_ids:
            if native_id == EXTERNAL_COURSE_NATIVE_ID:
                continue
            anchor = self.derived_base(
                "unit",
                f"erdman:derived:external-anchor:{native_id}",
                (
                    "bibliography-anchor"
                    if native_id.startswith("ERDMAN-FAOA-BIB-")
                    else "source-label-anchor"
                ),
                [native_id],
            )
            anchor.update(
                first_edition_id=source_edition_id,
                identity_anchor=native_id,
                identity_basis="typed materialization of an explicit owner-native relation endpoint",
                resource_id=resource_id,
                rights_default_id=rights_id,
                source_label=native_id,
                source_local_id=native_id,
                source_path=(
                    "source/upstream/bibliography"
                    if native_id.startswith("ERDMAN-FAOA-BIB-")
                    else "source/upstream/label-anchor"
                ),
                source_xml_path=None,
                unit_kind=(
                    "bibliography-entry-anchor"
                    if native_id.startswith("ERDMAN-FAOA-BIB-")
                    else "source-label-anchor"
                ),
            )
            self.add("units", anchor)
        scope_unit = self.derived_base(
            "unit",
            SCOPE_UNIT_STABLE_KEY,
            "whole-edition-lexical-scope",
            ["backend/terminology.jsonl"],
        )
        scope_unit.update(
            first_edition_id=self.raw_id(TARGET_EDITION_NATIVE_ID, "scope edition"),
            identity_anchor="ERDMAN-FAOA-2015-ID-WHOLE-EDITION-LEXICAL-SCOPE",
            identity_basis="common-backend terminology scope required by schema",
            resource_id=resource_id,
            rights_default_id=rights_id,
            source_label="Whole edition lexical scope",
            source_local_id=None,
            source_path="backend/terminology.jsonl",
            source_xml_path=None,
            unit_kind="edition-lexical-scope",
        )
        self.add("units", scope_unit)

    @staticmethod
    def payload_from_locator(
        path: Path,
        line_start: int,
        byte_count: int,
        expected_sha256: str,
    ) -> tuple[str, str]:
        raw = path.read_bytes()
        views = [("raw-newlines", raw)]
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if normalized != raw:
            views.append(("normalized-newlines", normalized))
        candidates: dict[bytes, set[str]] = defaultdict(set)
        for mode, view in views:
            starts = [0]
            starts.extend(match.end() for match in re.finditer(b"\n", view))
            if line_start < 1 or line_start > len(starts):
                continue
            line_offset = starts[line_start - 1]
            next_line_offset = (
                starts[line_start] if line_start < len(starts) else len(view)
            )
            # Native segments can begin after a TeX anchor on the same physical
            # line.  The ledger records the line, byte count, and digest rather
            # than a byte offset, so replay every possible byte start within the
            # declared first line and require one distinct digest match.
            for start in range(line_offset, next_line_offset + 1):
                payload = view[start : start + byte_count]
                if len(payload) == byte_count and sha256_bytes(payload) == expected_sha256:
                    candidates[payload].add(mode)
        if len(candidates) != 1:
            raise ValueError(
                f"segment payload recovery failed {path.name}:{line_start} "
                f"bytes={byte_count} sha={expected_sha256} candidates={len(candidates)}"
            )
        payload, modes = next(iter(candidates.items()))
        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"segment payload is not UTF-8: {path.name}:{line_start}") from exc
        return decoded, "+".join(sorted(modes))

    def build_segment_projections(self) -> None:
        source_edition_id = self.raw_id(SOURCE_EDITION_NATIVE_ID, "segment source edition")
        target_edition_id = self.raw_id(TARGET_EDITION_NATIVE_ID, "segment target edition")
        for row in self.snapshot.rows_by_file["segments.jsonl"]:
            value = row.value
            segment_id = row.target_id
            rights_id = self.raw_id(value.get("rights_id"), "segment variant rights")
            source_path = text(value.get("source_path"))
            target_path = text(value.get("target_path"))
            source_payload, source_mode = self.payload_from_locator(
                resolve_under(self.snapshot.owner_root, source_path),
                int(value["source_line_start"]),
                int(value["source_bytes"]),
                text(value["source_sha256"]),
            )
            target_payload, target_mode = self.payload_from_locator(
                resolve_under(self.snapshot.owner_root, target_path),
                int(value["target_line_start"]),
                int(value["target_bytes"]),
                text(value["target_sha256"]),
            )
            source_key = row.stable_key + ":variant:en"
            target_key = row.stable_key + ":variant:id-ID"
            source_variant = self.derived_base(
                "segment_variant",
                source_key,
                "source-segment-payload",
                [row.stable_key],
                extra={"newline_basis": source_mode},
            )
            source_variant.update(
                edition_id=source_edition_id,
                format="text/x-tex",
                locale="en",
                payload=source_payload,
                payload_sha256=sha256_bytes(source_payload.encode("utf-8")),
                rights_id=rights_id,
                role="source",
                segment_id=segment_id,
                source_variant_id=None,
                translation_state="source-authority",
            )
            self.add("segment_variants", source_variant)
            target_variant = self.derived_base(
                "segment_variant",
                target_key,
                "Indonesian-segment-payload",
                [row.stable_key],
                extra={"newline_basis": target_mode},
            )
            target_variant.update(
                edition_id=target_edition_id,
                format="text/x-tex",
                locale="id-ID",
                payload=target_payload,
                payload_sha256=sha256_bytes(target_payload.encode("utf-8")),
                rights_id=rights_id,
                role="translation",
                segment_id=segment_id,
                source_variant_id=source_variant["id"],
                translation_state=text(value.get("translation_state"), "admitted"),
            )
            self.add("segment_variants", target_variant)
            alignment = self.derived_base(
                "alignment",
                row.stable_key + ":alignment",
                "bilingual-segment-alignment",
                [row.stable_key],
            )
            alignment.update(
                alignment_kind="source-to-Indonesian-segment",
                assertion_method="exact owner line/byte/hash locator replay",
                confidence="exact",
                evidence_locator=f"backend/segments.jsonl#L{row.source_ordinal}",
                source_id=source_variant["id"],
                source_locale="en",
                source_sha256=source_variant["payload_sha256"],
                target_id=target_variant["id"],
                target_locale="id-ID",
                target_sha256=target_variant["payload_sha256"],
            )
            self.add("alignments", alignment)
            self.segment_payload_checks += 2

    def build_lexicon_projections(self) -> None:
        term_rows = self.snapshot.rows_by_file["terminology.jsonl"]
        missing_concept_rows = [row for row in term_rows if not row.value.get("concept_id")]
        if len(missing_concept_rows) != 409:
            raise ValueError(f"term-derived concept census changed: {len(missing_concept_rows)}")
        for row in missing_concept_rows:
            concept = self.derived_base(
                "concept",
                f"erdman:derived:concept-for-term:{row.native_id}",
                "term-concept-anchor",
                [row.stable_key],
            )
            concept.update(
                concept_key=row.native_id,
                concept_scheme="erdman-term-derived-concept-anchor-v1",
                definition_segment_id=None,
                parent_concept_id=None,
            )
            self.add("concepts", concept)

        future_qa_row = next(
            row
            for row in self.snapshot.rows_by_file["terminology_qa.jsonl"]
            if row.native_type == "future_domain_term_variant"
        )
        future_concept = self.derived_base(
            "concept",
            "erdman:derived:future-concept:TERM-WEAKLY-MEASURABLE",
            "future-domain-concept-anchor",
            [future_qa_row.stable_key],
            status="future-candidate",
        )
        future_concept.update(
            concept_key="TERM-WEAKLY-MEASURABLE",
            concept_scheme="erdman-future-domain-terminology-v1",
            definition_segment_id=None,
            parent_concept_id=None,
        )
        self.add("concepts", future_concept)
        future_term = self.derived_base(
            "term",
            "erdman:derived:future-term:TERM-WEAKLY-MEASURABLE",
            "future-domain-term-anchor",
            [future_qa_row.stable_key],
            status="future-candidate",
        )
        future_term.update(
            concept_id=future_concept["id"],
            evidence=text(future_qa_row.value.get("evidence_basis"), "bounded terminology QA"),
            notes=text(future_qa_row.value.get("scope")),
            preferred_form=text(future_qa_row.value.get("preferred")),
            register="future-domain recognition candidate",
            scope_unit_id=rid("unit", SCOPE_UNIT_STABLE_KEY),
            source_form=text(future_qa_row.value.get("source_term")),
            source_locale="en",
            source_term_id="TERM-WEAKLY-MEASURABLE",
            target_locale="id-ID",
            term_status=text(future_qa_row.value.get("variant_state")),
        )
        self.add("terms", future_term)

        nested_count = 0
        for row in term_rows:
            term_id = row.target_id
            for kind, field in (("accepted-recognition", "variants"), ("rejected", "rejected")):
                values = row.value.get(field) or []
                if not isinstance(values, list):
                    raise ValueError(f"term {row.native_id} {field} is not a list")
                for ordinal, form in enumerate(values, start=1):
                    stable_key = (
                        f"erdman:derived:term-variant:{row.native_id}:{field}:{ordinal}:{form}"
                    )
                    variant = self.derived_base(
                        "term_variant",
                        stable_key,
                        "nested-owner-term-variant",
                        [row.stable_key],
                    )
                    variant.update(
                        form=text(form),
                        locale="id-ID",
                        rationale=(
                            "owner-listed recognition variant"
                            if field == "variants"
                            else "owner-listed rejected alternative"
                        ),
                        term_id=term_id,
                        variant_kind=kind,
                    )
                    self.add("term_variants", variant)
                    nested_count += 1
        if nested_count != EXPECTED_TERM_NESTED_VARIANTS:
            raise ValueError(f"nested terminology variant census changed: {nested_count}")

    def build_index_aliases(self) -> None:
        target_edition_id = self.raw_id(TARGET_EDITION_NATIVE_ID, "index alias edition")
        seen_ids: set[str] = set()
        for ordinal, (row, raw) in enumerate(
            zip(self.snapshot.index_rows, self.snapshot.index_raw_rows), start=1
        ):
            native_id = row.get("id")
            parent = row.get("parent_segment_id")
            if not native_id or native_id in seen_ids:
                raise ValueError(f"index alias ID missing/duplicate at row {ordinal}")
            seen_ids.add(native_id)
            stable_key = f"erdman:derived:index-alias:{ordinal}:{native_id}"
            alias = self.derived_base(
                "alias",
                stable_key,
                "translated-index-entry-alias",
                [native_id, parent or ""],
                extra={
                    "canonical_row_sha256": sha256_bytes(canonical_bytes(row)),
                    "csv_row": row,
                    "raw_row_sha256": sha256_bytes(raw),
                    "source_ordinal": ordinal,
                },
            )
            alias.update(
                edition_id=target_edition_id,
                entity_id=self.raw_id(parent, "index alias parent segment"),
                scheme="translated-book-index",
                scope=text(parent),
                unique_in_scope=False,
                value=text(row.get("target_index_tex")),
            )
            self.add("aliases", alias)
            extension = alias["extensions"][DERIVED_EXTENSION]
            if extension["csv_row"] != row or extension["raw_row_sha256"] != sha256_bytes(raw):
                raise ValueError(f"index alias round-trip failed at row {ordinal}")
            self.index_roundtrip_checks += 1

    def build_routes(self) -> None:
        course_row = next(
            row for row in self.snapshot.rows_by_file["resources.jsonl"] if row.native_id == COURSE_NATIVE_ID
        )
        program_id = self.raw_id(PROGRAM_NATIVE_ID, "route program")
        course_id = self.raw_id(COURSE_NATIVE_ID, "route course")
        route_specs = [
            (
                "core",
                "D20 core",
                "Eight-chapter core path",
                course_row.value.get("core_unit_ids") or [],
            ),
            (
                "advanced",
                "D20 advanced continuation",
                "Nine-chapter advanced continuation path",
                course_row.value.get("advanced_continuation_unit_ids") or [],
            ),
        ]
        if [len(spec[3]) for spec in route_specs] != [8, 9]:
            raise ValueError("course core/advanced route membership changed")
        for route_key, title, description, members in route_specs:
            stable_key = f"erdman:derived:route:{route_key}"
            route = self.derived_base(
                "route",
                stable_key,
                "course-learning-route",
                [course_row.stable_key],
            )
            route.update(
                course_id=course_id,
                description=description,
                locale="id-ID",
                program_id=program_id,
                route_key=f"D20-{route_key}",
                route_kind="curriculum path",
                title=title,
                version_label=PUBLIC_VERSION,
            )
            self.add("routes", route)
            for ordinal, native_unit_id in enumerate(members, start=1):
                member = self.derived_base(
                    "route_member",
                    f"{stable_key}:member:{ordinal}:{native_unit_id}",
                    "course-learning-route-member",
                    [course_row.stable_key, native_unit_id],
                )
                member.update(
                    entity_id=self.raw_id(native_unit_id, "route member unit"),
                    inclusion_reason="owner-native course route declaration",
                    order_path=f"{ordinal:02d}",
                    ordinal=ordinal - 1,
                    required=True,
                    role=route_key,
                    route_id=route["id"],
                )
                self.add("route_members", member)

    def build_release_snapshot(self) -> None:
        artifact_ids = sorted(
            record["id"]
            for record in self.tables["artifacts"]
            if record.get("sha256") == EXPECTED_READER_SHA256
        )
        if len(artifact_ids) != 2:
            raise ValueError(f"final reader artifact carrier count changed: {len(artifact_ids)}")
        snapshot = self.derived_base(
            "release_snapshot",
            "erdman:derived:release-snapshot:2026.08.25-backend-artifact-reconciliation",
            "immutable-public-release-snapshot",
            [EXPECTED_HANDOFF_SHA256, EXPECTED_RELEASE_ARCHIVE_SHA256],
        )
        snapshot.update(
            archive_sha256=EXPECTED_RELEASE_ARCHIVE_SHA256,
            artifact_ids=artifact_ids,
            commit_sha=EXPECTED_GIT_COMMIT,
            edition_id=self.raw_id(TARGET_EDITION_NATIVE_ID, "snapshot edition"),
            immutable=True,
            publication_uri=PUBLIC_ZENODO_RECORD,
            release_date="2026-08-25",
            release_version=PUBLIC_VERSION,
            snapshot_kind="GitHub-and-Zenodo-public-byte-bound-release",
            tree_sha=EXPECTED_GIT_TREE,
        )
        self.add("release_snapshots", snapshot)

    def build(self) -> dict[str, list[dict[str, Any]]]:
        self.build_direct_records()
        self.build_files()
        self.build_external_and_scope_units()
        self.build_segment_projections()
        self.build_lexicon_projections()
        self.build_index_aliases()
        self.build_routes()
        self.build_release_snapshot()
        if len(self.claimed_native) != EXPECTED_NATIVE_RECORDS:
            raise ValueError(
                f"native claim closure failed: {len(self.claimed_native)}/{EXPECTED_NATIVE_RECORDS}"
            )
        if self.generated_records != EXPECTED_DERIVED_RECORDS:
            raise ValueError(
                f"derived projection census failed: {self.generated_records}/{EXPECTED_DERIVED_RECORDS}"
            )
        if self.segment_payload_checks != EXPECTED_SEGMENT_VARIANTS:
            raise ValueError("segment payload reconstruction closure failed")
        if self.index_roundtrip_checks != EXPECTED_INDEX_ALIASES:
            raise ValueError("index CSV round-trip closure failed")
        for table in self.tables:
            self.tables[table].sort(key=lambda record: record["id"])
        return self.tables


def media_type(locator: str) -> str:
    suffix = PurePosixPath(locator.split("#", 1)[0]).suffix.lower()
    overrides = {
        ".css": "text/css",
        ".csv": "text/csv",
        ".gif": "image/gif",
        ".html": "text/html",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".js": "text/javascript",
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".tex": "text/x-tex",
        ".txt": "text/plain",
        ".zip": "application/zip",
    }
    return overrides.get(suffix) or mimetypes.guess_type(locator)[0] or "application/octet-stream"


def referenced_uuid_urns(
    value: Any, path: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_uuid_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_uuid_urns(child, (*path, str(index)))
    elif isinstance(value, str) and value.startswith("urn:uuid:"):
        yield path, value


def validate_and_hash(
    snapshot: Snapshot,
    tables: dict[str, list[dict[str, Any]]],
    schema: dict[str, Any],
) -> dict[str, Any]:
    empty_shell = {
        "$schema": "schema/backend-v1.schema.json",
        "dataset_id": rid("resource", "erdman-functional-analysis-id:dataset"),
        "dataset_version": PUBLIC_VERSION + "+erdman-v0.1.0+interlanguage-v1",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": {name: [] for name in sorted(TABLE_TO_RECORD_TYPE)},
    }
    shell_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(empty_shell),
        key=lambda error: list(error.absolute_path),
    )
    if shell_errors:
        first = shell_errors[0]
        raise ValueError(
            f"common backend shell schema failure {list(first.absolute_path)}: {first.message}"
        )
    validators = {
        record_type: Draft202012Validator(
            schema["$defs"][f"{record_type}_record"], format_checker=FormatChecker()
        )
        for record_type in set(TABLE_TO_RECORD_TYPE.values())
    }
    all_records = [record for table in sorted(tables) for record in tables[table]]
    all_ids = {record["id"] for record in all_records}
    all_stable_keys = {record["stable_key"] for record in all_records}
    if len(all_ids) != len(all_records) or len(all_stable_keys) != len(all_records):
        raise ValueError("common global ID or stable-key uniqueness failed")
    if len(all_records) != EXPECTED_TARGET_RECORDS:
        raise ValueError(f"common record total changed: {len(all_records)}")
    observed_counts = {table: len(records) for table, records in tables.items() if records}
    if observed_counts != EXPECTED_TABLE_COUNTS:
        raise ValueError(f"common table census changed: {observed_counts}")

    direct_reverse = 0
    derived_count = 0
    table_hashes: dict[str, dict[str, Any]] = {}
    global_digest = hashlib.sha256()
    global_bytes = 0
    crosswalk_digest = hashlib.sha256()
    crosswalk_bytes = 0
    crosswalk_records = 0

    native_by_tuple = {row.tuple_key: row for row in snapshot.rows}
    for table in sorted(tables):
        table_digest = hashlib.sha256()
        table_bytes = 0
        for record in tables[table]:
            errors = sorted(
                validators[record["record_type"]].iter_errors(record),
                key=lambda error: list(error.absolute_path),
            )
            if errors:
                first = errors[0]
                raise ValueError(
                    f"common record schema failure {record['stable_key']} "
                    f"{list(first.absolute_path)}: {first.message}"
                )
            for field_path, value in referenced_uuid_urns(record):
                if field_path == ("id",):
                    continue
                if value not in all_ids:
                    raise ValueError(
                        f"common FK closure failed {record['stable_key']} "
                        f"{'/'.join(field_path)}={value}"
                    )
            extensions = record.get("extensions", {})
            native = extensions.get(NATIVE_EXTENSION)
            derived = extensions.get(DERIVED_EXTENSION)
            if native is not None:
                tuple_key = (
                    native.get("source_path", "").removeprefix("backend/"),
                    native.get("source_ordinal"),
                    native.get("native_record_type"),
                    native.get("native_id"),
                )
                row = native_by_tuple.get(tuple_key)
                if (
                    row is None
                    or native.get("native_record") != row.value
                    or native.get("raw_line_sha256") != row.raw_line_sha256
                    or native.get("canonical_native_sha256")
                    != row.canonical_native_sha256
                ):
                    raise ValueError(f"exact native reverse extraction failed: {tuple_key}")
                direct_reverse += 1
                crosswalk = {
                    "disposition": "direct-lossless-native-extension",
                    "source_file": row.source_file,
                    "source_native_id": row.native_id,
                    "source_native_type": row.native_type,
                    "source_ordinal": row.source_ordinal,
                    "source_raw_line_sha256": row.raw_line_sha256,
                    "target_id": record["id"],
                    "target_table": table,
                }
            elif derived is not None:
                derived_count += 1
                crosswalk = {
                    "disposition": "additive-deterministic-common-projection",
                    "projection_kind": derived.get("projection_kind"),
                    "source_identities": derived.get("source_identities", []),
                    "target_id": record["id"],
                    "target_table": table,
                }
            else:
                raise ValueError(f"common record lacks native or derived provenance: {record['id']}")
            line = canonical_bytes(record) + b"\n"
            table_digest.update(line)
            global_digest.update(line)
            table_bytes += len(line)
            global_bytes += len(line)
            crosswalk_line = canonical_bytes(crosswalk) + b"\n"
            crosswalk_digest.update(crosswalk_line)
            crosswalk_bytes += len(crosswalk_line)
            crosswalk_records += 1
        table_hashes[table] = {
            "records": len(tables[table]),
            "virtual_jsonl_bytes": table_bytes,
            "virtual_jsonl_sha256": table_digest.hexdigest(),
        }
    if direct_reverse != EXPECTED_NATIVE_RECORDS or derived_count != EXPECTED_DERIVED_RECORDS:
        raise ValueError(
            f"direct/derived closure mismatch: direct={direct_reverse}, derived={derived_count}"
        )
    if crosswalk_records != EXPECTED_TARGET_RECORDS:
        raise ValueError("crosswalk record closure failed")

    exercise_rows = snapshot.rows_by_file["exercise_support.jsonl"]
    solution_ids = {
        row.native_id for row in snapshot.rows_by_file["o001_mastery.jsonl"]
    }
    if len(exercise_rows) != 52 or any(
        row.value.get("original_solution_id") not in solution_ids for row in exercise_rows
    ):
        raise ValueError("52/52 exercise-support to solution closure failed")
    descriptor = {
        "dataset_id": empty_shell["dataset_id"],
        "dataset_version": empty_shell["dataset_version"],
        "ordering": "common table name, then common UUIDv5 ID",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": table_hashes,
    }
    return {
        "common_foreign_key_closure": "pass",
        "crosswalk_bytes": crosswalk_bytes,
        "crosswalk_records": crosswalk_records,
        "crosswalk_sha256": crosswalk_digest.hexdigest(),
        "dataset_id": empty_shell["dataset_id"],
        "dataset_version": empty_shell["dataset_version"],
        "derived_records": derived_count,
        "exact_native_reverse_extraction": direct_reverse,
        "nonempty_table_count": len(observed_counts),
        "record_count": len(all_records),
        "strict_dataset_shell_schema": "pass",
        "strict_streamed_record_schema": "pass",
        "table_count": len(tables),
        "table_counts": {table: len(records) for table, records in tables.items()},
        "table_hashes": table_hashes,
        "virtual_backend_descriptor_sha256": sha256_bytes(canonical_bytes(descriptor)),
        "virtual_records_jsonl_bytes": global_bytes,
        "virtual_records_jsonl_sha256": global_digest.hexdigest(),
    }


def build_receipt(
    snapshot: Snapshot,
    result: dict[str, Any],
    backend_schema_path: Path,
) -> dict[str, Any]:
    return {
        "schema_name": RECEIPT_SCHEMA_NAME,
        "schema_version": "1.0.0",
        "migration_id": "erdman-functional-analysis-id-2026.08.25-to-interlanguage-v1.0.0",
        "migration_mode": (
            "lossless-zero-copy-native-record-adapter-with-additive-common-projections"
        ),
        "source": {
            "auxiliary_index_rows": EXPECTED_AUXILIARY_INDEX_ROWS,
            "auxiliary_index_stream_bytes": snapshot.auxiliary_stream_bytes,
            "auxiliary_index_stream_sha256": snapshot.auxiliary_stream_sha256,
            "dataset_id": "O008/D20",
            "dataset_version": PUBLIC_VERSION,
            "logical_input_rows": EXPECTED_LOGICAL_INPUT_ROWS,
            "manifest_files": snapshot.manifest_facts,
            "native_record_count": EXPECTED_NATIVE_RECORDS,
            "native_record_counts_by_file": EXPECTED_RECORD_COUNTS_BY_FILE,
            "native_records_stream_bytes": snapshot.native_stream_bytes,
            "native_records_stream_sha256": snapshot.native_stream_sha256,
            "public_evidence": snapshot.public_evidence,
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": SOURCE_SCHEMA_VERSION,
        },
        "target": {
            "dataset_id": result["dataset_id"],
            "dataset_version": result["dataset_version"],
            "nonempty_table_count": result["nonempty_table_count"],
            "record_count": result["record_count"],
            "schema_bytes": EXPECTED_BACKEND_SCHEMA_BYTES,
            "schema_name": SCHEMA_NAME,
            "schema_path": "schemas/backend-v1.schema.json",
            "schema_sha256": EXPECTED_BACKEND_SCHEMA_SHA256,
            "schema_version": SCHEMA_VERSION,
            "table_count": result["table_count"],
            "virtual_backend_descriptor_sha256": result[
                "virtual_backend_descriptor_sha256"
            ],
            "virtual_records_jsonl_bytes": result["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": result["virtual_records_jsonl_sha256"],
        },
        "transformation": {
            "crosswalk_bytes": result["crosswalk_bytes"],
            "crosswalk_records": result["crosswalk_records"],
            "crosswalk_sha256": result["crosswalk_sha256"],
            "derived_common_records": EXPECTED_DERIVED_RECORDS,
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "direct_native_records": EXPECTED_NATIVE_RECORDS,
            "exact_reverse_extraction": EXPECTED_NATIVE_RECORDS,
            "native_payload_fields_preserved": "all fields of all 32,383 native records",
            "native_records_modified": 0,
            "projection_ledger": {
                "bilingual_segment_alignments": 2_196,
                "bilingual_segment_variants": 4_392,
                "external_relation_anchors": 68,
                "file_and_revision_records": 72,
                "future_concept_term_and_lexical_scope": 3,
                "index_aliases": 2_104,
                "release_snapshots": 1,
                "routes_and_members": 19,
                "term_concept_anchors": 409,
                "term_variants_from_native_term_lists": 42,
            },
        },
        "validation": {
            "common_foreign_key_closure": result["common_foreign_key_closure"],
            "common_global_id_uniqueness": EXPECTED_TARGET_RECORDS,
            "common_global_stable_key_uniqueness": EXPECTED_TARGET_RECORDS,
            "common_table_inventory": "38/38 present",
            "exact_native_reverse_extraction": EXPECTED_NATIVE_RECORDS,
            "exercise_solution_support_closure": "52/52 pass",
            "index_csv_roundtrip": "2104/2104 pass",
            "native_manifest_closure": "72/72 members pass",
            "native_route_id_overlap_handling": "4161 intentional route overlaps pass",
            "owner_lane_mutated": False,
            "private_marker_hits": 0,
            "public_archive_crc_path_manifest_metadata_and_member_replay": "pass",
            "result": "pass",
            "segment_payload_reconstruction": "4392/4392 pass",
            "strict_common_backend_schema": "pass",
            "two_independent_assemblies": "byte-identical",
            "two_independent_authority_reads": 2,
        },
        "coverage": {
            "advanced_continuation_chapters": 9,
            "core_chapters": 8,
            "course_role_id": "D20",
            "reader_pages": 298,
            "selected_reader_work_solutions": 10,
            "source_exercise_solutions": 52,
            "spectral_svd_bridge_units": 13,
            "source_preface_and_chapters": 18,
        },
        "tables": result["table_hashes"],
        "materialization": {
            "reason": (
                "The exact frozen owner backend and deterministic reversible adapter reconstruct "
                "the strict common backend without duplicating 41,689 records."
            ),
            "script_path": "scripts/migrate-erdman-backend-v1.py",
            "status": "virtual records not duplicated locally",
            "virtual_records_materialized": False,
        },
        "public_artifacts": [
            {
                "bytes": EXPECTED_READER_BYTES,
                "kind": "complete learner PDF",
                "sha256": EXPECTED_READER_SHA256,
                "url": PUBLIC_READER_URL,
            },
            {
                "bytes": EXPECTED_RELEASE_ARCHIVE_BYTES,
                "kind": "source, backend, and semantic HTML release archive",
                "sha256": EXPECTED_RELEASE_ARCHIVE_SHA256,
                "url": (
                    "https://zenodo.org/records/22088947/files/"
                    "functional-analysis-erdman-id-2026.08.25-backend-artifact-reconciliation-"
                    "source-backend-html.zip?download=1"
                ),
            },
        ],
        "credentials_recorded": False,
    }


def validate_receipt(receipt: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"receipt schema failure {list(first.absolute_path)}: {first.message}")


def privacy_scan(value: Any) -> None:
    serialized = canonical(value).lower()
    forbidden = (
        "authorization: bearer",
        "access_token",
        "api_token",
        "github_pat_",
        "zenodo_token",
    )
    hits = [marker for marker in forbidden if marker in serialized]
    if hits:
        raise ValueError(f"receipt privacy scan failed: {hits}")


def write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    if temporary.read_bytes() != payload:
        raise ValueError("atomic receipt temporary-file readback mismatch")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parents[1]
    default_owner = repo_root.parent / "functional-analysis-erdman-id"
    parser.add_argument("--owner-root", type=Path, default=default_owner)
    parser.add_argument(
        "--source-archive",
        type=Path,
        default=(
            default_owner
            / "qa"
            / "release-backend-artifact-reconciliation"
            / "functional-analysis-erdman-id-2026.08.25-backend-artifact-reconciliation-"
            "source-backend-html.zip"
        ),
    )
    parser.add_argument(
        "--backend-schema", type=Path, default=repo_root / "schemas" / "backend-v1.schema.json"
    )
    parser.add_argument(
        "--receipt-schema",
        type=Path,
        default=repo_root / "schemas" / "backend-migration-receipt-v1.schema.json",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=(
            repo_root
            / "backend"
            / "migrations"
            / "erdman-functional-analysis-id-v1"
            / "MIGRATION_RECEIPT.json"
        ),
    )
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    owner_root = args.owner_root.resolve()
    archive_path = args.source_archive.resolve()
    backend_schema_path = args.backend_schema.resolve()
    receipt_schema_path = args.receipt_schema.resolve()
    receipt_path = args.receipt.resolve()
    backend_schema = verify_schema(
        backend_schema_path,
        EXPECTED_BACKEND_SCHEMA_BYTES,
        EXPECTED_BACKEND_SCHEMA_SHA256,
    )
    receipt_schema = verify_schema(
        receipt_schema_path,
        EXPECTED_RECEIPT_SCHEMA_BYTES,
        EXPECTED_RECEIPT_SCHEMA_SHA256,
    )

    first_snapshot = load_snapshot(owner_root, archive_path)
    first_tables = Builder(first_snapshot, backend_schema).build()
    first_result = validate_and_hash(first_snapshot, first_tables, backend_schema)
    first_receipt = build_receipt(first_snapshot, first_result, backend_schema_path)
    validate_receipt(first_receipt, receipt_schema)
    privacy_scan(first_receipt)
    first_payload = pretty_bytes(first_receipt)
    del first_tables, first_snapshot

    second_snapshot = load_snapshot(owner_root, archive_path)
    second_tables = Builder(second_snapshot, backend_schema).build()
    second_result = validate_and_hash(second_snapshot, second_tables, backend_schema)
    second_receipt = build_receipt(second_snapshot, second_result, backend_schema_path)
    validate_receipt(second_receipt, receipt_schema)
    privacy_scan(second_receipt)
    second_payload = pretty_bytes(second_receipt)
    if first_result != second_result or first_payload != second_payload:
        raise ValueError("two complete independent authority reads/assemblies are not byte-identical")

    if args.check_only:
        if not receipt_path.is_file() or receipt_path.read_bytes() != first_payload:
            raise ValueError(f"check-only receipt mismatch: {receipt_path}")
    else:
        write_atomic(receipt_path, first_payload)
        if receipt_path.read_bytes() != first_payload:
            raise ValueError("written receipt readback mismatch")
    print(
        canonical(
            {
                "crosswalk_sha256": first_result["crosswalk_sha256"],
                "mode": "check-only" if args.check_only else "write",
                "native_records": EXPECTED_NATIVE_RECORDS,
                "receipt_bytes": len(first_payload),
                "receipt_path": str(receipt_path),
                "receipt_sha256": sha256_bytes(first_payload),
                "result": "pass",
                "target_records": first_result["record_count"],
                "virtual_records_jsonl_sha256": first_result[
                    "virtual_records_jsonl_sha256"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
