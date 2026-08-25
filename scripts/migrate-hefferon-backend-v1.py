#!/usr/bin/env python3
"""Prove a deterministic zero-copy backend-v1 view of the Hefferon B40 corpus.

The owner lane remains authoritative and untouched.  This adapter independently
replays its frozen native manifest, canonical JSONL/CSV records, native-ID and
foreign-key closure, and completed public readback.  It then streams a strict
common-backend v1 projection twice.  The projection is never materialized; only
its deterministic crosswalk, table, and global digests are recorded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_NAME = "hefferon-modular-backend"
SOURCE_SCHEMA_VERSION = "0.5.2"
WORKFLOW_ID = "program-matematika-indonesia/hefferon-b40-v1-adapter-1.0.0"
NATIVE_EXTENSION = "interlanguage.hefferon-linear-algebra-native"
NAMESPACE = uuid.UUID("75d58d57-8e0a-5aca-bf46-f8be5729556c")

PUBLIC_RELEASE_TAG = "v2026.08.22"
PUBLIC_GITHUB_COMMIT = "e84ce2956a7304830c42eba70106f940fefee7c4"
PUBLIC_GITHUB_TREE = "b434745225bb3931d51d107d8d8e5c0c8707af5d"
PUBLIC_GITHUB_RELEASE = (
    "https://github.com/KokunoYumeto/hefferon-linear-algebra-id/releases/tag/v2026.08.22"
)
PUBLIC_GITHUB_DOWNLOAD_BASE = (
    "https://github.com/KokunoYumeto/hefferon-linear-algebra-id/releases/download/v2026.08.22"
)
PUBLIC_ZENODO_DOI = "10.5281/zenodo.22070458"
PUBLIC_ZENODO_RECORD_ID = 22_070_458
PUBLIC_ZENODO_RECORD = "https://zenodo.org/records/22070458"
PUBLIC_BACKEND_FILENAME = "HEFFERON_LINEAR_ALGEBRA_ID_MODULAR_BACKEND_2026.08.22.zip"
PUBLIC_BACKEND_BYTES = 6_118_023
PUBLIC_BACKEND_SHA256 = "e3d66b5d19c79bb10243ac552f16165da897d40615467696452e3a64d0b92df2"

EXPECTED_BACKEND_SCHEMA_BYTES = 126_423
EXPECTED_BACKEND_SCHEMA_SHA256 = (
    "3de8d107b1c75db0f8d60c42ef7e3488bc3fcc93f72e955def71a771475cf2b2"
)
EXPECTED_RECEIPT_SCHEMA_BYTES = 2_563
EXPECTED_RECEIPT_SCHEMA_SHA256 = (
    "0147b14972dd562805b3b5f76fac453a9f32a6d298827d3f588316d4a8f5ffe0"
)
EXPECTED_MANIFEST_BYTES = 2_154
EXPECTED_MANIFEST_SHA256 = (
    "4c79fad12bda1552f03d6dae7c962f4d7a51ff68b3dcef09e88c437bfe773fad"
)
EXPECTED_MANIFEST_MEMBERS = 15
EXPECTED_MANIFEST_MEMBER_BYTES = 53_242_574
EXPECTED_SOURCE_CLOSURE_DESCRIPTOR_SHA256 = (
    "e60fe57bd3117b9e31b6b7bd0568a4e8b1fbb007bb36d576df724bbfe607d88f"
)

FROZEN_PUBLIC_FILES = {
    "public-readback.json": (
        12_735,
        "ee1c663ce5302aeccc5e18d31853c84803b787f0dfe448a9b0a549991c2e3595",
    ),
    "public-readback.github.json": (
        10_717,
        "69c50314661456a0847d1d02b4f0368cda5d6017b0792a8ce4010bc3f3ac688b",
    ),
    "public-readback.zenodo.json": (
        2_623,
        "64bb39bc8510e136b88c2bd54b66cfc3682616c691446e66bc185012f0492644",
    ),
    "transaction-state.json": (
        4_496,
        "c5dece48a7d8454cb1470d5c361a7dd2329b861da58170b6928b5d99a4c4d8fe",
    ),
}
EXPECTED_ARTIFACT_SET_SHA256 = (
    "f3f2ca17cdaf5bdfff778feccf9db989d84a351b729bdcdce0a2e54b0ab6dff8"
)
EXPECTED_FINAL_INVENTORY_SHA256 = (
    "e9664132fc4e37ca13684ec5e7df65a83b1f888fc8d800f9a179e9bbd0eb906b"
)
EXPECTED_TRANSACTION_FINGERPRINT = (
    "6bb9e0f7e9952c903ab66520016067b06e0b36e1312e29239ae5fde5a7af68a0"
)
EXPECTED_REPOSITORY_SNAPSHOT_SHA256 = (
    "e371d0485b6ffba169e45ee60f8e2932a6ee18a8e3ff1dca0d009aa7954578bc"
)

ENTITY_EXPORTS = {
    "artifact": "artifacts.jsonl",
    "asset": "assets.jsonl",
    "concept": "concepts.jsonl",
    "correction": "corrections.jsonl",
    "course": "courses.jsonl",
    "edition": "authority.jsonl",
    "program": "programs.jsonl",
    "qa_event": "qa_events.jsonl",
    "relation": "relations.csv",
    "resource": "authority.jsonl",
    "rights": "rights.jsonl",
    "segment": "segments.jsonl",
    "term": "terminology.jsonl",
    "unit": "units.jsonl",
}

JSONL_EXPORT_TYPES = {
    "artifacts.jsonl": {"artifact"},
    "assets.jsonl": {"asset"},
    "authority.jsonl": {"edition", "resource"},
    "concepts.jsonl": {"concept"},
    "corrections.jsonl": {"correction"},
    "courses.jsonl": {"course"},
    "programs.jsonl": {"program"},
    "qa_events.jsonl": {"qa_event"},
    "rights.jsonl": {"rights"},
    "segments.jsonl": {"segment"},
    "terminology.jsonl": {"term"},
    "units.jsonl": {"unit"},
}

EXPECTED_RECORD_COUNTS_BY_FILE = {
    "artifacts.jsonl": 8,
    "assets.jsonl": 432,
    "authority.jsonl": 3,
    "concepts.jsonl": 114,
    "corrections.jsonl": 307,
    "courses.jsonl": 1,
    "programs.jsonl": 1,
    "qa_events.jsonl": 72,
    "relations.csv": 13_999,
    "rights.jsonl": 11,
    "segments.jsonl": 3_528,
    "terminology.jsonl": 114,
    "units.jsonl": 3_541,
}
EXPECTED_RECORD_COUNTS_BY_TYPE = {
    "artifact": 8,
    "asset": 432,
    "concept": 114,
    "correction": 307,
    "course": 1,
    "edition": 2,
    "program": 1,
    "qa_event": 72,
    "relation": 13_999,
    "resource": 1,
    "rights": 11,
    "segment": 3_528,
    "term": 114,
    "unit": 3_541,
}
EXPECTED_NATIVE_RECORDS = 22_131

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
    "term": ("terms", "term"),
    "unit": ("units", "unit"),
}

EXPECTED_MANIFEST_PATHS = set(JSONL_EXPORT_TYPES) | {
    "relations.csv",
    "interoperability.json",
    "source_closure.json",
}

RESOURCE_NATIVE_ID = "r005.hefferon-linear-algebra"
SOURCE_EDITION_NATIVE_ID = "r005.hefferon-linear-algebra.edition.df2262e"
TARGET_EDITION_NATIVE_ID = (
    "r005.hefferon-linear-algebra.edition.derivative.locale.id-id.df2262e"
)
DEFAULT_RIGHTS_NATIVE_ID = "r005.hefferon-linear-algebra.rights.core-dual-license"
ROOT_UNIT_NATIVE_ID = "r005.hefferon-linear-algebra.unit.work.main.textbook"

SCALAR_REFERENCE_FIELDS = {
    "answers_unit_id",
    "authorization_correction_id",
    "authority_exercise_unit_id",
    "derivative_edition_id",
    "edition_id",
    "parent_id",
    "parent_program_id",
    "parent_resource_id",
    "parent_source_edition_id",
    "parent_unit_id",
    "resource_id",
    "rights_id",
    "source_snapshot_artifact_id",
    "source_unit_id",
    "supersedes",
    "target_edition_id",
}
LIST_REFERENCE_FIELDS = {
    "affected_unit_ids",
    "concept_ids",
    "prerequisite_ids",
    "resource_ids",
    "segment_ids",
    "target_term_ids",
    "unit_ids",
}

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class NativeBinding:
    native_id: str
    native_record_sha256: str
    native_type: str
    source_file: str
    source_format: str
    target_id: str
    target_table: str


@dataclass
class NativeContext:
    backend_root: Path
    bindings: dict[str, NativeBinding]
    counts_by_file: dict[str, int]
    counts_by_type: dict[str, int]
    manifest: dict[str, Any]
    manifest_members: list[dict[str, Any]]
    native_records_stream_bytes: int
    native_records_stream_sha256: str
    public_assets_by_sha256: dict[str, str]
    public_evidence: dict[str, Any]
    term_to_concept: dict[str, str]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical(value).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        raise ValueError(
            f"{label} byte mismatch: expected {expected_bytes}, got {path.stat().st_size}"
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"{label} SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )


def read_canonical_json(path: Path, label: str) -> dict[str, Any]:
    payload = path.read_bytes()
    if b"\r" in payload or not payload.endswith(b"\n"):
        raise ValueError(f"{label} is not canonical LF-terminated UTF-8 JSON")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root is not an object")
    if payload != canonical_bytes(value) + b"\n":
        raise ValueError(f"{label} is not canonically serialized")
    return value


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root is not an object")
    return value


def iter_jsonl(path: Path, allowed_types: set[str]) -> Iterator[dict[str, Any]]:
    with path.open("rb") as handle:
        for row_number, raw_line in enumerate(handle, start=1):
            if not raw_line.endswith(b"\n") or b"\r" in raw_line:
                raise ValueError(f"{path.name} row {row_number} is not LF-terminated")
            if raw_line == b"\n":
                raise ValueError(f"{path.name} row {row_number} is blank")
            try:
                record = json.loads(raw_line[:-1].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"{path.name} row {row_number} is invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path.name} row {row_number} is not an object")
            if raw_line != canonical_bytes(record) + b"\n":
                raise ValueError(f"{path.name} row {row_number} is not canonical JSONL")
            if record.get("record_type") not in allowed_types:
                raise ValueError(
                    f"{path.name} row {row_number} has unexpected record_type "
                    f"{record.get('record_type')!r}"
                )
            yield record


def iter_relations(path: Path) -> Iterator[dict[str, str]]:
    with path.open("rb") as raw:
        saw_byte = False
        last_byte = b""
        while chunk := raw.read(1024 * 1024):
            saw_byte = True
            last_byte = chunk[-1:]
            if b"\r" in chunk:
                raise ValueError("relations.csv contains CR bytes")
        if not saw_byte or last_byte != b"\n":
            raise ValueError("relations.csv is not LF-terminated")

    digest = hashlib.sha256()
    serialized_bytes = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("relations.csv has missing or duplicate headers")

        def emit_csv_row(row: dict[str, str], include_header: bool = False) -> None:
            nonlocal serialized_bytes
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(
                stream, fieldnames=reader.fieldnames, lineterminator="\n"
            )
            if include_header:
                writer.writeheader()
            else:
                writer.writerow(row)
            payload = stream.getvalue().encode("utf-8")
            digest.update(payload)
            serialized_bytes += len(payload)

        emit_csv_row({}, include_header=True)
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"relations.csv row {row_number} has surplus fields")
            emit_csv_row(row)
            yield row

    if serialized_bytes != path.stat().st_size or digest.hexdigest() != sha256_file(path):
        raise ValueError("relations.csv is noncanonical or its parse is lossy")


def iter_source_file(
    backend_root: Path, source_file: str, record_type_filter: str | None = None
) -> Iterator[dict[str, Any]]:
    path = backend_root / source_file
    if source_file == "relations.csv":
        for record in iter_relations(path):
            yield record
        return
    for record in iter_jsonl(path, JSONL_EXPORT_TYPES[source_file]):
        if record_type_filter is None or record["record_type"] == record_type_filter:
            yield record


def native_identity(record: dict[str, Any], source_file: str) -> tuple[str, str]:
    if source_file == "relations.csv":
        native_id = record.get("relation_id")
        native_type = "relation"
    else:
        native_id = record.get("id")
        native_type = record.get("record_type")
    if not isinstance(native_id, str) or not native_id:
        raise ValueError(f"{source_file} record lacks a stable native ID")
    if native_type not in DIRECT_TYPES:
        raise ValueError(f"{native_id}: unsupported native type {native_type!r}")
    return native_id, native_type


def target_id(native_type: str, native_id: str) -> str:
    record_type = DIRECT_TYPES[native_type][1]
    stable_key = f"hefferon-id:{native_id}"
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def safe_member_path(backend_root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or Path(relative).name != relative:
        raise ValueError(f"unsafe owner manifest path: {relative!r}")
    candidate = (backend_root / relative).resolve()
    if candidate.parent != backend_root.resolve():
        raise ValueError(f"owner manifest path escapes backend root: {relative!r}")
    return candidate


def verify_schema_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, Any]:
    exact_file(path, expected_bytes, expected_sha256, path.name)
    schema = read_json(path, path.name)
    Draft202012Validator.check_schema(schema)
    return schema


def verify_public_evidence(owner_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    publication_root = owner_root / "publication"
    for name, (expected_bytes, expected_sha256) in FROZEN_PUBLIC_FILES.items():
        exact_file(
            publication_root / name,
            expected_bytes,
            expected_sha256,
            f"frozen publication evidence {name}",
        )

    combined = read_json(publication_root / "public-readback.json", "public readback")
    github = read_json(
        publication_root / "public-readback.github.json", "GitHub public readback"
    )
    zenodo = read_json(
        publication_root / "public-readback.zenodo.json", "Zenodo public readback"
    )
    state = read_json(publication_root / "transaction-state.json", "publication state")

    common_expected = {
        "artifact_set_sha256": EXPECTED_ARTIFACT_SET_SHA256,
        "final_inventory_sha256": EXPECTED_FINAL_INVENTORY_SHA256,
        "transaction_fingerprint": EXPECTED_TRANSACTION_FINGERPRINT,
    }
    for label, value in (
        ("combined public readback", combined),
        ("GitHub public readback", github),
        ("Zenodo public readback", zenodo),
        ("publication state", state),
    ):
        for key, expected in common_expected.items():
            if value.get(key) != expected:
                raise ValueError(f"{label} has stale {key}")

    if (
        combined.get("release_tag") != PUBLIC_RELEASE_TAG
        or not combined.get("all_release_bytes_verified")
        or not combined.get("combined_release_complete")
        or not combined.get("complete_metadata_and_doi_verified")
        or not combined.get("repository_snapshot_verified")
    ):
        raise ValueError("combined public readback is incomplete")
    # The platform receipts are deliberately partial observations made before the
    # final combined readback.  The transaction state binds both exact partial
    # hashes, and the later combined receipt is the closure witness.
    if (
        not github.get("all_github_release_bytes_verified")
        or github.get("combined_release_complete") is not False
        or not github.get("repository_snapshot_verified")
        or not zenodo.get("all_zenodo_release_bytes_verified")
        or zenodo.get("combined_release_complete") is not False
        or not zenodo.get("complete_metadata_and_doi_verified")
    ):
        raise ValueError("platform-specific public readback sequence is inconsistent")

    github_assets = {
        item["name"]: (item["bytes"], item["sha256"])
        for item in combined.get("github", {}).get("assets", [])
    }
    zenodo_assets = {
        item["name"]: (item["bytes"], item["sha256"])
        for item in combined.get("zenodo", {}).get("assets", [])
    }
    if len(github_assets) != 9 or github_assets != zenodo_assets:
        raise ValueError("GitHub and Zenodo public inventories are not exactly identical")
    if github_assets.get(PUBLIC_BACKEND_FILENAME) != (
        PUBLIC_BACKEND_BYTES,
        PUBLIC_BACKEND_SHA256,
    ):
        raise ValueError("public modular-backend archive identity mismatch")

    repository = combined.get("github", {}).get("repository", {})
    combined_zenodo = combined.get("zenodo", {})
    if (
        repository.get("commit_sha") != PUBLIC_GITHUB_COMMIT
        or repository.get("tree_sha") != PUBLIC_GITHUB_TREE
        or repository.get("repository_snapshot_sha256")
        != EXPECTED_REPOSITORY_SNAPSHOT_SHA256
        or combined_zenodo.get("doi") != PUBLIC_ZENODO_DOI
        or combined_zenodo.get("record_id") != PUBLIC_ZENODO_RECORD_ID
        or combined_zenodo.get("record_url") != PUBLIC_ZENODO_RECORD
    ):
        raise ValueError("combined public repository/DOI binding mismatch")
    if (
        not state.get("complete")
        or not state.get("github_release_public")
        or state.get("github_release_url") != PUBLIC_GITHUB_RELEASE
        or state.get("github_commit_sha") != PUBLIC_GITHUB_COMMIT
        or state.get("github_tree_sha") != PUBLIC_GITHUB_TREE
        or not state.get("zenodo_published")
        or state.get("zenodo_doi") != PUBLIC_ZENODO_DOI
        or state.get("zenodo_record_id") != PUBLIC_ZENODO_RECORD_ID
        or state.get("repository_snapshot_sha256")
        != EXPECTED_REPOSITORY_SNAPSHOT_SHA256
    ):
        raise ValueError("publication transaction state is incomplete or stale")
    for key, file_name in (
        ("anonymous_readback_sha256", "public-readback.json"),
        ("github_anonymous_readback_sha256", "public-readback.github.json"),
        ("zenodo_anonymous_readback_sha256", "public-readback.zenodo.json"),
    ):
        if state.get(key) != FROZEN_PUBLIC_FILES[file_name][1]:
            raise ValueError(f"publication transaction state does not bind {file_name}")

    assets_by_sha256 = {sha256: name for name, (_bytes, sha256) in github_assets.items()}
    evidence = {
        "artifact_set_sha256": EXPECTED_ARTIFACT_SET_SHA256,
        "backend_archive_bytes": PUBLIC_BACKEND_BYTES,
        "backend_archive_filename": PUBLIC_BACKEND_FILENAME,
        "backend_archive_sha256": PUBLIC_BACKEND_SHA256,
        "final_inventory_sha256": EXPECTED_FINAL_INVENTORY_SHA256,
        "github_commit": PUBLIC_GITHUB_COMMIT,
        "github_release": PUBLIC_GITHUB_RELEASE,
        "github_tree": PUBLIC_GITHUB_TREE,
        "public_asset_count": len(github_assets),
        "public_files": {
            name: {"bytes": size, "sha256": digest}
            for name, (size, digest) in sorted(FROZEN_PUBLIC_FILES.items())
        },
        "release_tag": PUBLIC_RELEASE_TAG,
        "repository_snapshot_sha256": EXPECTED_REPOSITORY_SNAPSHOT_SHA256,
        "transaction_fingerprint": EXPECTED_TRANSACTION_FINGERPRINT,
        "zenodo_doi": PUBLIC_ZENODO_DOI,
        "zenodo_record": PUBLIC_ZENODO_RECORD,
    }
    return evidence, assets_by_sha256


def validate_native_references(
    record: dict[str, Any], source_file: str, known_ids: set[str]
) -> int:
    native_id, _native_type = native_identity(record, source_file)
    checked = 0

    def require_known(field: str, value: Any) -> None:
        nonlocal checked
        if value in (None, ""):
            return
        if not isinstance(value, str) or value not in known_ids:
            raise ValueError(f"{native_id}: unresolved native reference {field}={value!r}")
        checked += 1

    for field in SCALAR_REFERENCE_FIELDS:
        if field in record:
            require_known(field, record[field])
    for field in LIST_REFERENCE_FIELDS:
        if field not in record:
            continue
        values = record[field]
        if not isinstance(values, list):
            raise ValueError(f"{native_id}: native reference field {field} is not a list")
        for value in values:
            require_known(field, value)
    path = record.get("path")
    if path is not None:
        if not isinstance(path, list):
            raise ValueError(f"{native_id}: native topology path is not a list")
        for value in path:
            require_known("path", value)
    target_variant = record.get("target_variant")
    if isinstance(target_variant, dict):
        require_known("target_variant.edition_id", target_variant.get("edition_id"))
    if source_file == "relations.csv":
        require_known("source_id", record.get("source_id"))
        require_known("target_id", record.get("target_id"))
    return checked


def verify_native_backend(
    owner_root: Path,
    backend_schema_path: Path,
    receipt_schema_path: Path,
) -> tuple[NativeContext, dict[str, Any], dict[str, Any]]:
    backend_schema = verify_schema_file(
        backend_schema_path,
        EXPECTED_BACKEND_SCHEMA_BYTES,
        EXPECTED_BACKEND_SCHEMA_SHA256,
    )
    receipt_schema = verify_schema_file(
        receipt_schema_path,
        EXPECTED_RECEIPT_SCHEMA_BYTES,
        EXPECTED_RECEIPT_SCHEMA_SHA256,
    )

    backend_root = owner_root / "backend"
    manifest_path = backend_root / "manifest.json"
    exact_file(
        manifest_path,
        EXPECTED_MANIFEST_BYTES,
        EXPECTED_MANIFEST_SHA256,
        "frozen owner manifest",
    )
    manifest = read_canonical_json(manifest_path, "owner manifest")
    if (
        manifest.get("schema") != SOURCE_SCHEMA_NAME
        or manifest.get("schema_version") != SOURCE_SCHEMA_VERSION
        or manifest.get("generated_file_count") != EXPECTED_MANIFEST_MEMBERS
    ):
        raise ValueError("owner manifest schema/count identity mismatch")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != EXPECTED_MANIFEST_MEMBERS:
        raise ValueError("owner manifest file inventory is malformed")
    declared = {entry.get("path"): entry for entry in entries}
    if len(declared) != len(entries) or set(declared) != EXPECTED_MANIFEST_PATHS:
        raise ValueError("owner manifest file set is incomplete, duplicate, or unexpected")
    declared_bytes = 0
    for relative, entry in sorted(declared.items()):
        path = safe_member_path(backend_root, relative)
        expected_bytes = entry.get("bytes")
        expected_sha256 = entry.get("sha256")
        if not isinstance(expected_bytes, int) or not isinstance(expected_sha256, str):
            raise ValueError(f"owner manifest member metadata is malformed: {relative}")
        exact_file(path, expected_bytes, expected_sha256, f"owner manifest member {relative}")
        declared_bytes += expected_bytes
    if declared_bytes != EXPECTED_MANIFEST_MEMBER_BYTES:
        raise ValueError("owner manifest member-byte closure mismatch")

    interoperability = read_canonical_json(
        backend_root / "interoperability.json", "owner interoperability envelope"
    )
    if (
        interoperability.get("schema") != SOURCE_SCHEMA_NAME
        or interoperability.get("schema_version") != SOURCE_SCHEMA_VERSION
        or interoperability.get("entity_exports") != ENTITY_EXPORTS
    ):
        raise ValueError("owner interoperability envelope is stale or lossy")

    source_closure = read_canonical_json(
        backend_root / "source_closure.json", "owner source closure"
    )
    declared_closure_sha256 = source_closure.get("closure_sha256")
    descriptor = dict(source_closure)
    descriptor.pop("closure_sha256", None)
    computed_closure_sha256 = sha256_bytes(canonical_bytes(descriptor))
    if (
        declared_closure_sha256 != EXPECTED_SOURCE_CLOSURE_DESCRIPTOR_SHA256
        or computed_closure_sha256 != EXPECTED_SOURCE_CLOSURE_DESCRIPTOR_SHA256
        or manifest.get("source_closure_sha256")
        != EXPECTED_SOURCE_CLOSURE_DESCRIPTOR_SHA256
    ):
        raise ValueError("owner source-closure semantic digest mismatch")

    public_evidence, assets_by_sha256 = verify_public_evidence(owner_root)

    bindings: dict[str, NativeBinding] = {}
    common_ids: set[str] = set()
    counts_by_file: Counter[str] = Counter()
    counts_by_type: Counter[str] = Counter()
    native_stream_hash = hashlib.sha256()
    native_stream_bytes = 0
    term_to_concept: dict[str, str] = {}

    for source_file in sorted(EXPECTED_RECORD_COUNTS_BY_FILE):
        for record in iter_source_file(backend_root, source_file):
            native_id, native_type = native_identity(record, source_file)
            if source_file != "relations.csv":
                if (
                    record.get("schema") != SOURCE_SCHEMA_NAME
                    or record.get("schema_version") != SOURCE_SCHEMA_VERSION
                ):
                    raise ValueError(f"{native_id}: native schema identity mismatch")
            else:
                if (
                    record.get("schema") != SOURCE_SCHEMA_NAME
                    or record.get("schema_version") != SOURCE_SCHEMA_VERSION
                ):
                    raise ValueError(f"{native_id}: native relation schema identity mismatch")
            if native_id in bindings:
                raise ValueError(f"duplicate native ID: {native_id}")
            table, _record_type = DIRECT_TYPES[native_type]
            common_id = target_id(native_type, native_id)
            if common_id in common_ids:
                raise ValueError(f"deterministic target-ID collision: {native_id}")
            common_ids.add(common_id)
            native_hash = sha256_bytes(canonical_bytes(record))
            bindings[native_id] = NativeBinding(
                native_id=native_id,
                native_record_sha256=native_hash,
                native_type=native_type,
                source_file=source_file,
                source_format="csv-row" if source_file == "relations.csv" else "jsonl-object",
                target_id=common_id,
                target_table=table,
            )
            counts_by_file[source_file] += 1
            counts_by_type[native_type] += 1
            descriptor_line = canonical_bytes(
                {"record": record, "source_file": source_file}
            ) + b"\n"
            native_stream_hash.update(descriptor_line)
            native_stream_bytes += len(descriptor_line)
            if native_type == "concept":
                for term_id in record.get("target_term_ids", []):
                    previous = term_to_concept.setdefault(term_id, native_id)
                    if previous != native_id:
                        raise ValueError(f"term has multiple native concept bindings: {term_id}")

    if dict(counts_by_file) != EXPECTED_RECORD_COUNTS_BY_FILE:
        raise ValueError(
            f"owner record counts by file changed: {dict(sorted(counts_by_file.items()))}"
        )
    if dict(counts_by_type) != EXPECTED_RECORD_COUNTS_BY_TYPE:
        raise ValueError(
            f"owner record counts by type changed: {dict(sorted(counts_by_type.items()))}"
        )
    if len(bindings) != EXPECTED_NATIVE_RECORDS or len(common_ids) != EXPECTED_NATIVE_RECORDS:
        raise ValueError("native/target unique-ID count mismatch")

    expected_identity_types = {
        RESOURCE_NATIVE_ID: "resource",
        SOURCE_EDITION_NATIVE_ID: "edition",
        TARGET_EDITION_NATIVE_ID: "edition",
        DEFAULT_RIGHTS_NATIVE_ID: "rights",
        ROOT_UNIT_NATIVE_ID: "unit",
    }
    for native_id, expected_type in expected_identity_types.items():
        binding = bindings.get(native_id)
        if binding is None or binding.native_type != expected_type:
            raise ValueError(f"required owner identity is absent or mistyped: {native_id}")

    known_ids = set(bindings)
    reference_count = 0
    observed_term_ids: set[str] = set()
    for source_file in sorted(EXPECTED_RECORD_COUNTS_BY_FILE):
        for record in iter_source_file(backend_root, source_file):
            reference_count += validate_native_references(record, source_file, known_ids)
            native_id, native_type = native_identity(record, source_file)
            if native_type == "term":
                observed_term_ids.add(native_id)
    if set(term_to_concept) != observed_term_ids:
        missing = sorted(observed_term_ids - set(term_to_concept))
        extra = sorted(set(term_to_concept) - observed_term_ids)
        raise ValueError(
            f"native term/concept crosswalk is incomplete: missing={missing[:3]}, extra={extra[:3]}"
        )

    context = NativeContext(
        backend_root=backend_root,
        bindings=bindings,
        counts_by_file=dict(sorted(counts_by_file.items())),
        counts_by_type=dict(sorted(counts_by_type.items())),
        manifest=manifest,
        manifest_members=[declared[name] for name in sorted(declared)],
        native_records_stream_bytes=native_stream_bytes,
        native_records_stream_sha256=native_stream_hash.hexdigest(),
        public_assets_by_sha256=assets_by_sha256,
        public_evidence=public_evidence,
        term_to_concept=term_to_concept,
    )
    context.public_evidence["native_reference_bindings_checked"] = reference_count
    return context, backend_schema, receipt_schema


def mapped(context: NativeContext, native_id: Any, field: str) -> str | None:
    if native_id in (None, ""):
        return None
    if not isinstance(native_id, str) or native_id not in context.bindings:
        raise ValueError(f"unmapped native reference in {field}: {native_id!r}")
    return context.bindings[native_id].target_id


def valid_sha256(value: Any) -> str | None:
    return value if isinstance(value, str) and SHA256_PATTERN.fullmatch(value) else None


def valid_commit(value: Any) -> str | None:
    return value if isinstance(value, str) and COMMIT_PATTERN.fullmatch(value) else None


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return canonical(value)


def recorded_at(recorded_on: Any) -> str:
    if not isinstance(recorded_on, str):
        raise ValueError(f"native recorded_on is not a string: {recorded_on!r}")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", recorded_on):
        return recorded_on + "T00:00:00Z"
    if re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        recorded_on,
    ):
        return recorded_on
    raise ValueError(f"native recorded_on cannot map to date-time: {recorded_on!r}")


def media_type(locator: str) -> str:
    suffix = Path(locator.split("#", 1)[0]).suffix.lower()
    return {
        ".asy": "text/plain",
        ".csv": "text/csv",
        ".eps": "application/postscript",
        ".gif": "image/gif",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".md": "text/markdown",
        ".mp": "text/plain",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".py": "text/x-python",
        ".sage": "text/plain",
        ".svg": "image/svg+xml",
        ".tex": "text/x-tex",
        ".txt": "text/plain",
        ".zip": "application/zip",
    }.get(suffix, "application/octet-stream")


def base_record(
    context: NativeContext,
    native: dict[str, Any],
    native_id: str,
    native_type: str,
    source_file: str,
) -> dict[str, Any]:
    binding = context.bindings[native_id]
    if binding.native_record_sha256 != sha256_bytes(canonical_bytes(native)):
        raise ValueError(f"native record changed between scan and transform: {native_id}")
    source_format = "csv-row" if source_file == "relations.csv" else "jsonl-object"
    if binding.source_file != source_file or binding.source_format != source_format:
        raise ValueError(f"native source binding changed between scan and transform: {native_id}")
    return {
        "extensions": {
            NATIVE_EXTENSION: {
                "disposition": "direct-lossless-native-extension",
                "native_record": native,
                "native_record_id": native_id,
                "native_record_sha256": binding.native_record_sha256,
                "source_file": source_file,
                "source_format": source_format,
                "source_schema": SOURCE_SCHEMA_NAME,
                "source_schema_version": SOURCE_SCHEMA_VERSION,
            }
        },
        "id": binding.target_id,
        "record_type": DIRECT_TYPES[native_type][1],
        "recorded_at": recorded_at(native.get("recorded_on")),
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": f"hefferon-id:{native_id}",
        "status": text(native.get("status"), "active") or "active",
        "supersedes_id": mapped(context, native.get("supersedes"), "supersedes"),
        "workflow_id": WORKFLOW_ID,
    }


def transform_record(
    context: NativeContext, native: dict[str, Any], source_file: str
) -> dict[str, Any]:
    native_id, native_type = native_identity(native, source_file)
    common = base_record(context, native, native_id, native_type, source_file)

    if native_type == "resource":
        common.update(
            authority_policy=(
                "Pinned upstream commit/tree plus exact completed public-byte readback; "
                "the owner-native record remains authoritative"
            ),
            creator_name=text(native.get("author")),
            official_reader=native.get("official_repository"),
            official_repository=text(native.get("official_repository")),
            original_title=text(native.get("source_title")),
            resource_key=native_id,
            work_type="open linear-algebra textbook, answer book, and Sage lab corpus",
        )
    elif native_type == "edition":
        derivative = native_id == TARGET_EDITION_NATIVE_ID
        commit = valid_commit(native.get("commit")) or valid_commit(native.get("source_commit"))
        if commit is None:
            raise ValueError(f"edition lacks an exact Git commit: {native_id}")
        common.update(
            archive_sha256=valid_sha256(native.get("archive_sha256")),
            commit_sha=commit,
            edition_kind=text(
                native.get("derivative_kind"),
                "published-Indonesian-translation" if derivative else "source-authority",
            ),
            locale=text(native.get("locale"), "id-ID" if derivative else "en"),
            release_date="2026-08-22" if derivative else None,
            resource_id=mapped(
                context, native.get("parent_resource_id"), "edition.parent_resource_id"
            ),
            rights_id=mapped(
                context,
                native.get("rights_id") or DEFAULT_RIGHTS_NATIVE_ID,
                "edition.rights_id",
            ),
            source_edition_id=mapped(
                context,
                native.get("parent_source_edition_id"),
                "edition.parent_source_edition_id",
            ),
            tree_sha=valid_commit(native.get("source_tree")),
            vcs_ref=text(native.get("tag") or commit),
            vcs_type="git",
            version_label=(
                PUBLIC_RELEASE_TAG if derivative else text(native.get("edition_statement"), commit)
            ),
        )
    elif native_type == "rights":
        notice_sha = valid_sha256(native.get("license_authority_sha256"))
        if notice_sha is None:
            notice_sha = sha256_bytes(canonical_bytes(native))
        change_notice = native.get("change_notice_required")
        common.update(
            assertion_status=text(native.get("third_party_status"), "native-rights-record"),
            attribution=text(native.get("attribution")),
            authority=text(native.get("license_authority_locator"), "native rights record"),
            change_notice=(
                "required"
                if change_notice is True
                else "not required" if change_notice is False else "not asserted"
            ),
            license_expression=text(
                native.get("selected_license_identifier") or native.get("license_choice"),
                "NOASSERTION",
            ),
            nonendorsement=text(native.get("non_endorsement")),
            notice_locator=text(
                native.get("license_authority_locator"), f"backend/rights.jsonl#{native_id}"
            ),
            notice_sha256=notice_sha,
            source_component_id=text(native.get("component_scope"), native_id),
            third_party_status=text(native.get("third_party_status"), "native-rights-record"),
        )
    elif native_type == "program":
        common.update(
            curriculum_version=text(native.get("version"), PUBLIC_RELEASE_TAG),
            locale=text(native.get("locale"), "id-ID"),
            program_key=text(native.get("curriculum_role"), "B40"),
            rights_id=mapped(context, native.get("rights_id"), "program.rights_id"),
            title="Aljabar Linear — Edisi Bahasa Indonesia",
        )
    elif native_type == "course":
        common.update(
            course_key=text(native.get("course_role"), "B40"),
            order_key=text(native.get("course_role"), "B40"),
            program_id=mapped(
                context, native.get("parent_program_id"), "course.parent_program_id"
            ),
            role=text(native.get("course_role"), "B40"),
            prerequisite_course_keys=[],
            resource_keys=[RESOURCE_NATIVE_ID],
            scope="complete textbook, worked answers, and Sage lab",
            title=text(native.get("target_title"), native.get("source_title", "Aljabar Linear")),
        )
    elif native_type == "unit":
        common.update(
            first_edition_id=mapped(context, native.get("edition_id"), "unit.edition_id"),
            identity_anchor=native_id,
            identity_basis="owner-native stable unit ID",
            resource_id=mapped(context, native.get("resource_id"), "unit.resource_id"),
            rights_default_id=mapped(context, native.get("rights_id"), "unit.rights_id"),
            source_label=(
                native.get("source_title")
                or native.get("target_title")
                or native.get("source_local_id")
            ),
            source_local_id=native.get("source_local_id"),
            source_path=text(native.get("source_locator")),
            source_xml_path=None,
            unit_kind=text(native.get("unit_kind"), "native-unit"),
        )
    elif native_type == "segment":
        common.update(
            identity_anchor=native_id,
            ordinal=int(native.get("order", 0)),
            segment_kind=text(
                native.get("projection_role") or native.get("provenance_kind"),
                "translation-segment",
            ),
            segmentation_profile="hefferon-modular-backend-v0.5.2",
            unit_id=mapped(
                context, native.get("parent_unit_id"), "segment.parent_unit_id"
            ),
        )
    elif native_type == "concept":
        common.update(
            concept_key=text(
                native.get("source_local_id") or native.get("canonical_source_term"), native_id
            ),
            concept_scheme="hefferon-linear-algebra-terminology-ledger-v1",
            definition_segment_id=None,
            parent_concept_id=None,
        )
    elif native_type == "term":
        concept_native_id = context.term_to_concept.get(native_id)
        if concept_native_id is None:
            raise ValueError(f"term lacks an exact native concept binding: {native_id}")
        common.update(
            concept_id=mapped(context, concept_native_id, "term.concept_id"),
            evidence=text(native.get("evidence")),
            notes=text(native.get("notes")),
            preferred_form=text(native.get("preferred")),
            register=text(native.get("register")),
            scope_unit_id=mapped(context, ROOT_UNIT_NATIVE_ID, "term.scope_unit_id"),
            source_form=text(native.get("source_term")),
            source_locale="en",
            source_term_id=native_id,
            target_locale=text(native.get("locale"), "id-ID"),
            term_status=text(
                native.get("ledger_status") or native.get("translation_state"), "admitted"
            ),
        )
    elif native_type == "correction":
        affected = native.get("affected_unit_ids") or []
        affected_native_id = affected[0] if affected else native.get("edition_id")
        original_payload = text(native.get("source_defect"))
        replacement_payload = text(native.get("target_correction"), original_payload)
        common.update(
            affected_id=mapped(context, affected_native_id, "correction.affected_id"),
            binding_status=text(native.get("affected_unit_mapping_status"), "native binding"),
            category=text(native.get("scope") or native.get("severity"), "native-correction"),
            evidence_locator=text(
                native.get("evidence") or native.get("source_locator"), "native correction record"
            ),
            local_state=text(
                native.get("ledger_status") or native.get("disposition"), native.get("status", "active")
            ),
            original_payload_sha256=sha256_bytes(original_payload.encode("utf-8")),
            payload_hash_basis="UTF-8 native source_defect and target_correction fields",
            rationale=text(native.get("rationale")),
            replacement_payload_sha256=sha256_bytes(replacement_payload.encode("utf-8")),
            source_edition_id=mapped(
                context, native.get("edition_id"), "correction.source_edition_id"
            ),
            upstream_disposition=text(
                native.get("upstream_report_disposition"), "not asserted"
            ),
            upstream_url=None,
        )
    elif native_type == "relation":
        common.update(
            assertion_method="owner-native explicit relation row",
            confidence="explicit",
            edition_id=mapped(context, native.get("edition_id"), "relation.edition_id"),
            from_id=mapped(context, native.get("source_id"), "relation.source_id"),
            ordinal=int(native.get("order") or 0),
            relation_type=text(native.get("relation_type")),
            source_locator=text(native.get("source_locator")),
            strength=text(native.get("status"), "asserted"),
            to_id=mapped(context, native.get("target_id"), "relation.target_id"),
        )
    elif native_type == "qa_event":
        witness = native.get("witness")
        common.update(
            input_hash=sha256_bytes(canonical_bytes(native)),
            method="frozen owner-native QA-event evidence",
            qa_type=text(native.get("qa_type"), "native-qa-event"),
            result=text(native.get("result"), native.get("status", "pass")),
            reviewer_kind="owner-native deterministic QA workflow",
            severity_p1=0,
            severity_p2=0,
            severity_p3=0,
            tool_name=text(native.get("responsible_workflow")),
            tool_version=text(native.get("schema_version")),
            witness_locator=text(native.get("source_locator") or witness, "native QA event"),
        )
        common["extensions"][NATIVE_EXTENSION]["severity_mapping"] = (
            "The owner-native QA record has no uniform P1/P2/P3 counters; required common "
            "counters are zero placeholders, not independent finding counts."
        )
    elif native_type == "asset":
        locator = text(
            native.get("target_locator")
            or native.get("source_locator")
            or native.get("declared_reference"),
            native_id,
        )
        common.update(
            asset_kind=text(native.get("asset_kind"), "native-asset"),
            canonical_path_or_uri=locator,
            media_type=media_type(locator),
            resource_id=mapped(context, native.get("resource_id"), "asset.resource_id"),
            rights_default_id=mapped(context, native.get("rights_id"), "asset.rights_id"),
        )
    elif native_type == "artifact":
        artifact_sha = valid_sha256(native.get("sha256"))
        build_receipt = text(native.get("build_receipt"), "not asserted by native artifact")
        toolchain = text(native.get("toolchain"), "not asserted by native artifact")
        public_name = context.public_assets_by_sha256.get(artifact_sha or "")
        public_uri = (
            f"{PUBLIC_GITHUB_DOWNLOAD_BASE}/{public_name}"
            if public_name
            else native.get("source_url")
        )
        common.update(
            artifact_kind=text(native.get("artifact_kind"), "native-artifact"),
            build_receipt=build_receipt,
            bytes=native.get("bytes"),
            edition_id=mapped(context, native.get("edition_id"), "artifact.edition_id"),
            locale=text(native.get("locale") or native.get("language"), "mul"),
            manifest_sha256=valid_sha256(native.get("manifest_sha256")),
            public_uri=public_uri,
            sha256=artifact_sha,
            toolchain_id=toolchain,
            tree_sha256=None,
        )
    else:
        raise ValueError(f"unhandled native type: {native_type}")

    if common["id"] != target_id(native_type, native_id):
        raise ValueError(f"target identity derivation mismatch: {native_id}")
    return common


def referenced_uuid_urns(value: Any, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
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


def native_sources_for_table(table: str) -> tuple[str, str] | None:
    matches = [
        (source_file, native_type)
        for native_type, (target_table, _record_type) in DIRECT_TYPES.items()
        if target_table == table
        for source_file in [ENTITY_EXPORTS[native_type]]
    ]
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError(f"target table has ambiguous native source: {table}")
    return matches[0]


def assemble_virtual(context: NativeContext, backend_schema: dict[str, Any]) -> dict[str, Any]:
    table_names = sorted(backend_schema["properties"]["tables"]["properties"])
    validators = {
        record_type: Draft202012Validator(
            backend_schema["$defs"][f"{record_type}_record"],
            format_checker=FormatChecker(),
        )
        for _table, record_type in DIRECT_TYPES.values()
    }
    empty_shell = {
        "$schema": "schema/backend-v1.schema.json",
        "dataset_id": target_id("resource", "hefferon-linear-algebra-id:dataset"),
        "dataset_version": "v2026.08.22+hefferon-v0.5.2+interlanguage-v1",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": {name: [] for name in table_names},
    }
    shell_errors = sorted(
        Draft202012Validator(backend_schema, format_checker=FormatChecker()).iter_errors(
            empty_shell
        ),
        key=lambda error: list(error.absolute_path),
    )
    if shell_errors:
        first = shell_errors[0]
        raise ValueError(f"common backend shell schema failure {list(first.absolute_path)}: {first.message}")

    known_common_ids = {binding.target_id for binding in context.bindings.values()}
    global_hash = hashlib.sha256()
    global_bytes = 0
    record_count = 0
    reverse_count = 0
    table_hashes: dict[str, dict[str, Any]] = {}
    table_counts: dict[str, int] = {}

    for table in table_names:
        table_hash = hashlib.sha256()
        table_bytes = 0
        table_count = 0
        source = native_sources_for_table(table)
        if source is not None:
            source_file, native_type_filter = source
            for native in iter_source_file(
                context.backend_root, source_file, native_type_filter
            ):
                native_id, native_type = native_identity(native, source_file)
                common = transform_record(context, native, source_file)
                errors = sorted(
                    validators[native_type].iter_errors(common),
                    key=lambda error: list(error.absolute_path),
                )
                if errors:
                    first = errors[0]
                    raise ValueError(
                        f"common record schema failure {native_id} "
                        f"{list(first.absolute_path)}: {first.message}"
                    )
                for field_path, value in referenced_uuid_urns(common):
                    if field_path == ("id",):
                        continue
                    if value not in known_common_ids:
                        raise ValueError(
                            f"common foreign-key closure failure {common['id']} "
                            f"{'/'.join(field_path)}={value}"
                        )
                extension = common["extensions"][NATIVE_EXTENSION]
                if (
                    extension["native_record_id"] != native_id
                    or extension["native_record"] != native
                    or extension["native_record_sha256"]
                    != sha256_bytes(canonical_bytes(native))
                ):
                    raise ValueError(f"exact native reverse binding failed: {native_id}")
                reverse_count += 1
                line = canonical_bytes(common) + b"\n"
                table_hash.update(line)
                global_hash.update(line)
                table_bytes += len(line)
                global_bytes += len(line)
                table_count += 1
                record_count += 1
        table_counts[table] = table_count
        table_hashes[table] = {
            "records": table_count,
            "virtual_jsonl_bytes": table_bytes,
            "virtual_jsonl_sha256": table_hash.hexdigest(),
        }

    if record_count != EXPECTED_NATIVE_RECORDS or reverse_count != EXPECTED_NATIVE_RECORDS:
        raise ValueError("virtual target is not one-to-one with native records")
    expected_nonempty_counts = {
        DIRECT_TYPES[native_type][0]: count
        for native_type, count in EXPECTED_RECORD_COUNTS_BY_TYPE.items()
    }
    if {name: count for name, count in table_counts.items() if count} != dict(
        sorted(expected_nonempty_counts.items())
    ):
        raise ValueError("target table counts do not reconcile with native record counts")

    crosswalk_hash = hashlib.sha256()
    crosswalk_bytes = 0
    for native_id in sorted(context.bindings):
        binding = context.bindings[native_id]
        line = canonical_bytes(
            {
                "disposition": "direct-lossless-native-extension",
                "source_file": binding.source_file,
                "source_record_id": native_id,
                "source_record_sha256": binding.native_record_sha256,
                "target_id": binding.target_id,
                "target_table": binding.target_table,
            }
        ) + b"\n"
        crosswalk_hash.update(line)
        crosswalk_bytes += len(line)

    descriptor = {
        "dataset_id": empty_shell["dataset_id"],
        "dataset_version": empty_shell["dataset_version"],
        "ordering": "target table name, then owner-native source order",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": table_hashes,
    }
    return {
        "common_foreign_key_closure": "pass",
        "crosswalk_bytes": crosswalk_bytes,
        "crosswalk_records": len(context.bindings),
        "crosswalk_sha256": crosswalk_hash.hexdigest(),
        "dataset_id": empty_shell["dataset_id"],
        "dataset_version": empty_shell["dataset_version"],
        "exact_native_reverse_bindings": reverse_count,
        "nonempty_table_count": sum(bool(count) for count in table_counts.values()),
        "record_count": record_count,
        "strict_dataset_shell_schema": "pass",
        "strict_streamed_record_schema": "pass",
        "table_count": len(table_names),
        "table_counts": table_counts,
        "table_hashes": table_hashes,
        "virtual_backend_descriptor_sha256": sha256_bytes(canonical_bytes(descriptor)),
        "virtual_records_jsonl_bytes": global_bytes,
        "virtual_records_jsonl_sha256": global_hash.hexdigest(),
    }


def portable_owner_path(relative: str) -> str:
    return f"../hefferon-linear-algebra-id/{relative}"


def build_receipt(context: NativeContext, result: dict[str, Any]) -> dict[str, Any]:
    manifest_files = [
        {"bytes": item["bytes"], "path": item["path"], "sha256": item["sha256"]}
        for item in context.manifest_members
    ]
    return {
        "coverage": {
            "canonical_native_csv": "pass",
            "canonical_native_jsonl": "pass",
            "common_foreign_key_closure": result["common_foreign_key_closure"],
            "course_role_id": "B40",
            "direct_native_records": EXPECTED_NATIVE_RECORDS,
            "edition_completion": "complete",
            "exact_reverse_extraction": result["exact_native_reverse_bindings"],
            "manifest_filename_size_sha256_closure": "pass",
            "manifest_member_bytes": EXPECTED_MANIFEST_MEMBER_BYTES,
            "manifest_members": EXPECTED_MANIFEST_MEMBERS,
            "native_foreign_key_closure": "pass",
            "native_record_counts": context.counts_by_type,
            "native_record_counts_by_file": context.counts_by_file,
            "native_record_count": EXPECTED_NATIVE_RECORDS,
            "native_unique_ids": len(context.bindings),
            "public_inventory_cross_platform_identity": "pass",
            "public_release_asset_count": context.public_evidence["public_asset_count"],
            "source_closure_descriptor_sha256": EXPECTED_SOURCE_CLOSURE_DESCRIPTOR_SHA256,
            "source_record_dispositions": {
                "direct-lossless-native-extension": EXPECTED_NATIVE_RECORDS
            },
        },
        "credentials_recorded": False,
        "materialization": {
            "reason": (
                "The exact published owner-native backend plus this deterministic reversible "
                "streaming adapter reconstruct the strict common backend twice without a "
                "redundant materialized projection."
            ),
            "script_path": "scripts/migrate-hefferon-backend-v1.py",
            "status": "not duplicated locally",
            "virtual_records_materialized": False,
        },
        "migration_id": "hefferon-linear-algebra-id-v2026.08.22-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-one-to-one-native-backend-adapter",
        "public_artifacts": [
            {
                "bytes": FROZEN_PUBLIC_FILES["public-readback.json"][0],
                "path": portable_owner_path("publication/public-readback.json"),
                "sha256": FROZEN_PUBLIC_FILES["public-readback.json"][1],
                "status": "published-and-anonymously-verified",
            },
            {
                "bytes": FROZEN_PUBLIC_FILES["transaction-state.json"][0],
                "path": portable_owner_path("publication/transaction-state.json"),
                "sha256": FROZEN_PUBLIC_FILES["transaction-state.json"][1],
                "status": "complete-publication-transaction",
            },
            {
                "bytes": PUBLIC_BACKEND_BYTES,
                "filename": PUBLIC_BACKEND_FILENAME,
                "github_url": f"{PUBLIC_GITHUB_DOWNLOAD_BASE}/{PUBLIC_BACKEND_FILENAME}",
                "sha256": PUBLIC_BACKEND_SHA256,
                "status": "published-and-cross-platform-byte-verified",
                "zenodo_url": (
                    f"https://zenodo.org/api/records/{PUBLIC_ZENODO_RECORD_ID}/files/"
                    f"{PUBLIC_BACKEND_FILENAME}/content"
                ),
            },
        ],
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": "1.0.0",
        "source": {
            "dataset_id": RESOURCE_NATIVE_ID,
            "dataset_version": PUBLIC_RELEASE_TAG,
            "manifest_bytes": EXPECTED_MANIFEST_BYTES,
            "manifest_member_bytes": EXPECTED_MANIFEST_MEMBER_BYTES,
            "manifest_members": manifest_files,
            "manifest_path": portable_owner_path("backend/manifest.json"),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "native_record_count": EXPECTED_NATIVE_RECORDS,
            "native_records_stream_bytes": context.native_records_stream_bytes,
            "native_records_stream_sha256": context.native_records_stream_sha256,
            "public_backend_archive": {
                "bytes": PUBLIC_BACKEND_BYTES,
                "filename": PUBLIC_BACKEND_FILENAME,
                "github_url": f"{PUBLIC_GITHUB_DOWNLOAD_BASE}/{PUBLIC_BACKEND_FILENAME}",
                "sha256": PUBLIC_BACKEND_SHA256,
                "zenodo_url": (
                    f"https://zenodo.org/api/records/{PUBLIC_ZENODO_RECORD_ID}/files/"
                    f"{PUBLIC_BACKEND_FILENAME}/content"
                ),
            },
            "public_evidence": context.public_evidence,
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": SOURCE_SCHEMA_VERSION,
        },
        "tables": result["table_hashes"],
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
            "crosswalk_records": result["crosswalk_records"],
            "crosswalk_serialization": (
                "canonical UTF-8 JSONL sorted by complete owner-native ID"
            ),
            "crosswalk_sha256": result["crosswalk_sha256"],
            "crosswalk_virtual_jsonl_bytes": result["crosswalk_bytes"],
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|hefferon-id:<native-id>)",
            "derived_records_materialized": False,
            "native_files_modified": 0,
            "native_id_extensions": EXPECTED_NATIVE_RECORDS,
            "native_ids_preserved_in_crosswalk": EXPECTED_NATIVE_RECORDS,
            "native_payload_fields_preserved": "all fields of all 22,131 native records",
            "native_records_modified": 0,
            "ordering_profile": "target table name, then owner-native source order",
            "record_disposition": (
                "one direct common record with a checksum-bound complete native extension"
            ),
        },
        "validation": {
            "common_backend_schema_result": "pass",
            "deterministic_receipt_assembly_equal": True,
            "deterministic_transform_runs": 2,
            "deterministic_virtual_assembly_equal": True,
            "first_and_second_record_count": result["record_count"],
            "first_and_second_virtual_records_jsonl_sha256": result[
                "virtual_records_jsonl_sha256"
            ],
            "native_manifest_replay": "pass",
            "native_record_closure": "pass",
            "owner_lane_mutated": False,
            "public_receipt_state_closure": "pass",
            "receipt_schema_bytes": EXPECTED_RECEIPT_SCHEMA_BYTES,
            "receipt_schema_sha256": EXPECTED_RECEIPT_SCHEMA_SHA256,
            "result": "pass",
            "strict_dataset_shell_schema": result["strict_dataset_shell_schema"],
            "strict_streamed_record_schema": result["strict_streamed_record_schema"],
        },
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
    payload = canonical(value).lower()
    markers = (
        "c:" + chr(92) + "users" + chr(92),
        "c:" + "/" + "users" + "/",
        "/" + "users" + "/",
        "file" + "://",
        "." + "codex" + "/",
        "." + "codex" + chr(92),
    )
    hits = [marker for marker in markers if marker in payload]
    if hits:
        raise ValueError(f"private path marker found in receipt: {hits}")


def portable_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    if temporary.read_bytes() != payload:
        raise ValueError("receipt temporary write replay failed")
    temporary.replace(path)


def main() -> None:
    script_path = Path(__file__).resolve()
    central_root = script_path.parent.parent
    default_owner = central_root.parent / "hefferon-linear-algebra-id"
    default_receipt = (
        central_root
        / "backend"
        / "migrations"
        / "hefferon-linear-algebra-id-v1"
        / "MIGRATION_RECEIPT.json"
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner-root", type=Path, default=default_owner)
    parser.add_argument(
        "--backend-schema",
        type=Path,
        default=central_root / "schemas" / "backend-v1.schema.json",
    )
    parser.add_argument(
        "--receipt-schema",
        type=Path,
        default=central_root / "schemas" / "backend-migration-receipt-v1.schema.json",
    )
    parser.add_argument("--receipt", type=Path, default=default_receipt)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="require an existing byte-identical receipt and do not rewrite it",
    )
    args = parser.parse_args()

    owner_root = args.owner_root.resolve()
    receipt_path = args.receipt.resolve()
    try:
        receipt_path.relative_to(central_root.resolve())
    except ValueError as exc:
        raise ValueError("receipt output must remain inside the central corpus root") from exc
    if owner_root.name != "hefferon-linear-algebra-id":
        raise ValueError("owner root must be the exact hefferon-linear-algebra-id lane")

    first_context, first_backend_schema, first_receipt_schema = verify_native_backend(
        owner_root, args.backend_schema.resolve(), args.receipt_schema.resolve()
    )
    first_result = assemble_virtual(first_context, first_backend_schema)
    first_receipt = build_receipt(first_context, first_result)
    validate_receipt(first_receipt, first_receipt_schema)
    privacy_scan(first_receipt)

    second_context, second_backend_schema, second_receipt_schema = verify_native_backend(
        owner_root, args.backend_schema.resolve(), args.receipt_schema.resolve()
    )
    second_result = assemble_virtual(second_context, second_backend_schema)
    second_receipt = build_receipt(second_context, second_result)
    validate_receipt(second_receipt, second_receipt_schema)
    privacy_scan(second_receipt)

    if first_result != second_result:
        raise ValueError("the two independently replayed virtual transforms differ")
    first_payload = pretty_bytes(first_receipt)
    second_payload = pretty_bytes(second_receipt)
    if first_payload != second_payload:
        raise ValueError("the two independently assembled receipt byte streams differ")

    if args.check_only:
        if not receipt_path.is_file():
            raise ValueError("check-only requested but the migration receipt is absent")
        if receipt_path.read_bytes() != first_payload:
            raise ValueError("existing migration receipt is not byte-identical to replay")
    else:
        write_atomic(receipt_path, first_payload)
    validate_receipt(read_json(receipt_path, "written migration receipt"), first_receipt_schema)
    if receipt_path.read_bytes() != first_payload:
        raise ValueError("written migration receipt differs from deterministic payload")

    summary = {
        "crosswalk_records": first_result["crosswalk_records"],
        "native_records": EXPECTED_NATIVE_RECORDS,
        "receipt": portable_path(receipt_path, central_root),
        "receipt_bytes": len(first_payload),
        "receipt_sha256": sha256_bytes(first_payload),
        "result": "pass",
        "target_records": first_result["record_count"],
        "virtual_records_jsonl_bytes": first_result["virtual_records_jsonl_bytes"],
        "virtual_records_jsonl_sha256": first_result[
            "virtual_records_jsonl_sha256"
        ],
    }
    print(canonical(summary))


if __name__ == "__main__":
    main()
