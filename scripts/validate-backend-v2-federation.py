#!/usr/bin/env python3
"""Strictly validate a phase-one Program Matematika Indonesia v2 federation.

The validator deliberately treats the generated package as an untrusted byte
artifact.  It validates syntax and schema before checking projections,
identities, references, learner routes, publication evidence, and deterministic
replay.  It never edits the package; the CLI may write a report only to the
explicit ``--report`` path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
import uuid
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker


NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
ID_FORMULA = "record_type:semantic_key"
CSV_HEADER = ["record_type", "semantic_key", "id", "record_json"]
PRIMARY_ACTION_ORDER = ["learn", "html", "pdf", "epub", "offline"]
SECONDARY_ACTION_ORDER = ["source", "repository", "doi", "backend"]
ACTION_ORDER = PRIMARY_ACTION_ORDER + SECONDARY_ACTION_ORDER
ACTION_RANK = {value: index for index, value in enumerate(ACTION_ORDER)}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_ID_RE = re.compile(
    r"^(?:codex://threads/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"
)
TABLE_TYPES = {
    "datasets": "dataset",
    "programs": "program",
    "courses": "course",
    "reader_surfaces": "reader_surface",
    "web_routes": "web_route",
    "publication_events": "publication_event",
    "qa_events": "qa_event",
    "identity_crosswalks": "identity_crosswalk",
}
TYPE_TABLES = {value: key for key, value in TABLE_TYPES.items()}
RECORD_REFERENCE_RULES = {
    "dataset": {
        "reader_surface_ids": "reader_surface",
        "qa_receipt_ids": "qa_event",
        "public_readback_receipt_id": "qa_event",
    },
    "program": {"course_ids": "course"},
    "course": {
        "program_id": "program",
        "owner_dataset_id": "dataset",
        "web_route_id": "web_route",
    },
    "publication_event": {"dataset_ids": "dataset"},
}
COURSE_KEY_REFERENCE_FIELDS = {
    "dataset": {"course_ids"},
    "course": {"prerequisite_course_ids", "prerequisite_course_keys"},
    "reader_surface": {"course_ids"},
    "web_route": {"course_ids"},
    "publication_event": {"course_ids"},
}
AVAILABLE_STATES = {
    "available",
    "catalog_declared",
    "public",
    "published",
    "public_readback_verified",
    "readback_verified",
    "published_and_readback_verified",
    "verified",
    "current",
}
NONPUBLIC_STATES = {
    "planned",
    "not_published",
    "unavailable",
    "draft",
    "future",
    "not_materialized",
}
PUBLICATION_STATES = {
    "published",
    "public",
    "released",
    "verified",
    "readback_verified",
    "public_readback_verified",
    "published_and_readback_verified",
}


class ValidationFailure(ValueError):
    """One or more independently actionable package validation failures."""

    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationFailure([f"duplicate JSON key:{key}"])
        result[key] = value
    return result


def _strict_text(path: Path, *, require_lf_terminator: bool = True) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValidationFailure([f"UTF-8 BOM forbidden:{path}"])
    if b"\r" in data:
        raise ValidationFailure([f"CR/CRLF forbidden:{path}"])
    if require_lf_terminator and data and not data.endswith(b"\n"):
        raise ValidationFailure([f"missing LF terminator:{path}"])
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationFailure([f"invalid UTF-8:{path}:{exc}"]) from exc


def load_json(path: Path, *, canonical_required: bool) -> Any:
    text = _strict_text(path)
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except ValidationFailure:
        raise
    except json.JSONDecodeError as exc:
        raise ValidationFailure([f"invalid JSON:{path}:{exc}"]) from exc
    if canonical_required and text != canonical(value) + "\n":
        raise ValidationFailure([f"noncanonical JSON:{path}"])
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    text = _strict_text(path)
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line:
            raise ValidationFailure([f"blank JSONL line:{path}:{line_number}"])
        try:
            row = json.loads(line, object_pairs_hook=_reject_duplicate_pairs)
        except ValidationFailure:
            raise
        except json.JSONDecodeError as exc:
            raise ValidationFailure([f"invalid JSONL:{path}:{line_number}:{exc}"]) from exc
        if not isinstance(row, dict):
            raise ValidationFailure([f"JSONL row is not an object:{path}:{line_number}"])
        if line != canonical(row):
            raise ValidationFailure([f"noncanonical JSONL:{path}:{line_number}"])
        rows.append(row)
    return rows


def load_lossless_csv(path: Path) -> list[dict[str, Any]]:
    text = _strict_text(path)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != CSV_HEADER:
        raise ValidationFailure([f"invalid CSV header:{path}:{reader.fieldnames!r}"])
    rows: list[dict[str, Any]] = []
    for line_number, csv_row in enumerate(reader, start=2):
        if None in csv_row or any(value is None for value in csv_row.values()):
            raise ValidationFailure([f"malformed CSV row:{path}:{line_number}"])
        try:
            row = json.loads(csv_row["record_json"], object_pairs_hook=_reject_duplicate_pairs)
        except ValidationFailure:
            raise
        except json.JSONDecodeError as exc:
            raise ValidationFailure([f"invalid CSV record_json:{path}:{line_number}:{exc}"]) from exc
        if csv_row["record_json"] != canonical(row):
            raise ValidationFailure([f"noncanonical CSV record_json:{path}:{line_number}"])
        for field in ("record_type", "semantic_key", "id"):
            if csv_row[field] != row.get(field):
                raise ValidationFailure([f"CSV identity mismatch:{path}:{line_number}:{field}"])
        rows.append(row)
    return rows


def safe_relative_path(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationFailure([f"invalid relative path:{label}:{value!r}"])
    if value != unicodedata.normalize("NFC", value):
        raise ValidationFailure([f"non-NFC relative path:{label}:{value!r}"])
    if (
        "\\" in value
        or "\x00" in value
        or re.match(r"^[A-Za-z]:", value)
        or value.startswith("//")
        or any(ord(char) < 32 for char in value)
    ):
        raise ValidationFailure([f"unsafe relative path:{label}:{value!r}"])
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValidationFailure([f"unsafe relative path:{label}:{value!r}"])
    if pure.as_posix() != value:
        raise ValidationFailure([f"noncanonical relative path:{label}:{value!r}"])
    return value


def _resolve_inside(root: Path, relative: str, *, label: str) -> Path:
    path = root.joinpath(*PurePosixPath(relative).parts)
    root_resolved = root.resolve()
    try:
        path.resolve().relative_to(root_resolved)
    except ValueError as exc:
        raise ValidationFailure([f"path escapes root:{label}:{relative}"]) from exc
    return path


def _validate_file_facts(
    facts: Any,
    *,
    root: Path,
    label: str,
    require_exact_inventory: bool,
    inventory_exclusions: set[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(facts, list):
        raise ValidationFailure([f"{label} must be an array"])
    declared: dict[str, dict[str, Any]] = {}
    casefolded: dict[str, str] = {}
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            raise ValidationFailure([f"{label}[{index}] is not an object"])
        relative = safe_relative_path(fact.get("path"), label=f"{label}[{index}]")
        folded = relative.casefold()
        if relative in declared or folded in casefolded:
            raise ValidationFailure([f"duplicate/case-colliding file fact:{label}:{relative}"])
        casefolded[folded] = relative
        declared[relative] = fact
        if not isinstance(fact.get("bytes"), int) or fact["bytes"] < 0:
            raise ValidationFailure([f"invalid byte count:{label}:{relative}"])
        if not isinstance(fact.get("sha256"), str) or not SHA256_RE.fullmatch(fact["sha256"]):
            raise ValidationFailure([f"invalid SHA-256:{label}:{relative}"])
        path = _resolve_inside(root, relative, label=label)
        if not path.is_file() or path.is_symlink():
            raise ValidationFailure([f"missing or symlinked declared file:{label}:{relative}"])
        if path.stat().st_size != fact["bytes"]:
            raise ValidationFailure([f"byte mismatch:{label}:{relative}"])
        if sha256_file(path) != fact["sha256"]:
            raise ValidationFailure([f"hash mismatch:{label}:{relative}"])
        if path.suffix.lower() in {".json", ".jsonl", ".csv"}:
            _strict_text(path)
            if path.suffix.lower() == ".json":
                load_json(path, canonical_required=False)

    if require_exact_inventory:
        actual: dict[str, Path] = {}
        actual_casefolded: dict[str, str] = {}
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in inventory_exclusions:
                continue
            if path.is_symlink():
                raise ValidationFailure([f"symlinked package file forbidden:{relative}"])
            folded = relative.casefold()
            if folded in actual_casefolded:
                raise ValidationFailure([f"case-colliding physical files:{actual_casefolded[folded]}:{relative}"])
            actual_casefolded[folded] = relative
            actual[relative] = path
        if set(declared) != set(actual):
            raise ValidationFailure(
                [
                    "manifest inventory mismatch:"
                    f"missing={sorted(set(declared) - set(actual))}:"
                    f"extra={sorted(set(actual) - set(declared))}"
                ]
            )
    return declared


def _validate_source_facts(
    facts: Any,
    source_roots: list[Path],
    locator_roots: dict[str, Path] | None = None,
) -> int:
    if not isinstance(facts, list):
        raise ValidationFailure(["source_facts must be an array"])
    seen: set[str] = set()
    validated = 0
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            raise ValidationFailure([f"source_facts[{index}] is not an object"])
        relative = safe_relative_path(fact.get("path"), label=f"source_facts[{index}]")
        if relative in seen:
            raise ValidationFailure([f"duplicate source fact:{relative}"])
        seen.add(relative)
        if not isinstance(fact.get("bytes"), int) or fact["bytes"] < 0:
            raise ValidationFailure([f"invalid source byte count:{relative}"])
        if not isinstance(fact.get("sha256"), str) or not SHA256_RE.fullmatch(fact["sha256"]):
            raise ValidationFailure([f"invalid source SHA-256:{relative}"])
        locator_base = fact.get("locator_base")
        if locator_base is not None:
            if not locator_roots or locator_base not in locator_roots:
                raise ValidationFailure([f"unknown or unbound source locator_base:{locator_base}:{relative}"])
            selected_roots = [locator_roots[locator_base]]
        else:
            selected_roots = source_roots
        if not selected_roots:
            continue
        candidates = [
            _resolve_inside(root, relative, label="source_evidence")
            for root in selected_roots
        ]
        matches = [path for path in candidates if path.is_file() and not path.is_symlink()]
        if not matches:
            raise ValidationFailure([f"source fact missing or symlinked:{relative}"])
        matching_bytes = [
            path
            for path in matches
            if path.stat().st_size == fact["bytes"] and sha256_file(path) == fact["sha256"]
        ]
        if not matching_bytes:
            raise ValidationFailure([f"source fact byte/hash mismatch:{relative}"])
        if len({path.read_bytes() for path in matching_bytes}) != 1:
            raise ValidationFailure([f"ambiguous non-identical source fact resolution:{relative}"])
        validated += 1
    return validated


def _validate_bound_file_fact(fact: Any, roots: list[Path], *, label: str) -> int:
    if not isinstance(fact, dict):
        raise ValidationFailure([f"{label} must be a bound-file object"])
    core = {key: fact.get(key) for key in ("path", "bytes", "sha256")}
    return _validate_source_facts([core], roots)


def _validate_build_and_schema_bindings(
    envelope: dict[str, Any],
    *,
    roots: list[Path],
    package_schema_path: Path,
    record_schema_path: Path | None,
) -> int:
    checked = 0
    for field in ("namespace_document", "release_policy_profile"):
        if field in envelope:
            checked += _validate_bound_file_fact(envelope[field], roots, label=field)
    build = envelope.get("build")
    if build is not None:
        if not isinstance(build, dict):
            raise ValidationFailure(["build binding must be an object"])
        builder_path = build.get("builder_path")
        builder_sha = build.get("builder_sha256")
        if not isinstance(builder_path, str) or not isinstance(builder_sha, str):
            raise ValidationFailure(["build binding lacks builder path/hash"])
        builder_fact = {"path": builder_path, "bytes": None, "sha256": builder_sha}
        # Builder bindings intentionally omit bytes; resolve and hash directly.
        relative = safe_relative_path(builder_path, label="build.builder_path")
        matches = [
            _resolve_inside(root, relative, label="build.builder_path")
            for root in roots
        ]
        matches = [path for path in matches if path.is_file() and not path.is_symlink()]
        if roots and not matches:
            raise ValidationFailure([f"builder source missing:{relative}"])
        if matches and not any(sha256_file(path) == builder_sha for path in matches):
            raise ValidationFailure([f"builder source hash mismatch:{relative}"])
        checked += int(bool(matches))
        records_sha = envelope.get("records_sha256")
        for field in ("build_a_records_sha256", "build_b_records_sha256"):
            if build.get(field) != records_sha:
                raise ValidationFailure([f"build replay hash mismatch:{field}"])
        if build.get("deterministic_replay") != "pass":
            raise ValidationFailure(["build does not declare deterministic replay pass"])

    bindings = envelope.get("validation_bindings")
    if bindings is not None:
        if not isinstance(bindings, dict):
            raise ValidationFailure(["validation_bindings must be an object"])
        if bindings.get("package_schema_sha256") != sha256_file(package_schema_path):
            raise ValidationFailure(["package schema binding hash mismatch"])
        if record_schema_path is None:
            raise ValidationFailure(["record schema binding exists but no record schema was supplied"])
        if bindings.get("record_schema_sha256") != sha256_file(record_schema_path):
            raise ValidationFailure(["record schema binding hash mismatch"])
        checked += 2
    return checked


def _validate_record_evidence_bindings(
    records: list[dict[str, Any]],
    *,
    roots: list[Path],
    locator_roots: dict[str, Path],
) -> dict[str, int]:
    pairs = (
        ("evidence_locator", "evidence_sha256"),
        ("migration_receipt_locator", "migration_receipt_sha256"),
        ("adapter_locator", "adapter_sha256"),
        ("package_manifest_locator", "package_manifest_sha256"),
        ("source_records_locator", "source_records_sha256"),
        ("catalog_locator", "catalog_sha256"),
    )
    local = 0
    deferred_native_or_remote = 0
    for row in records:
        payload = row["payload"]
        for locator_field, hash_field in pairs:
            locator = payload.get(locator_field)
            digest = payload.get(hash_field)
            if locator is None and digest is None:
                continue
            if locator is None or digest is None:
                raise ValidationFailure(
                    [f"locator/hash not paired:{row['semantic_key']}:{locator_field}:{hash_field}"]
                )
            if not isinstance(locator, str) or not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                raise ValidationFailure([f"invalid locator/hash binding:{row['semantic_key']}:{locator_field}"])
            if "://" in locator or locator.startswith("owner-native:"):
                deferred_native_or_remote += 1
                continue
            relative = safe_relative_path(locator, label=f"{row['semantic_key']}:{locator_field}")
            if relative.startswith("curriculum_logbook/") and "coordinator_logbook_root" in locator_roots:
                selected_roots = [locator_roots["coordinator_logbook_root"]]
            elif "program_repository_root" in locator_roots:
                selected_roots = [locator_roots["program_repository_root"]]
            else:
                selected_roots = roots
            if not selected_roots:
                deferred_native_or_remote += 1
                continue
            candidates = [
                _resolve_inside(root, relative, label=f"{row['semantic_key']}:{locator_field}")
                for root in selected_roots
            ]
            matches = [
                path
                for path in candidates
                if path.is_file() and not path.is_symlink() and sha256_file(path) == digest
            ]
            if not matches:
                raise ValidationFailure(
                    [f"record evidence locator/hash mismatch:{row['semantic_key']}:{locator_field}:{relative}"]
                )
            local += 1

    programs = [row for row in records if row["record_type"] == "program"]
    catalog_hashes = {
        row["payload"].get("catalog_sha256")
        for row in programs
        if isinstance(row["payload"].get("catalog_sha256"), str)
    }
    for row in records:
        if (
            row["record_type"] == "course"
            and "source_catalog_sha256" in row["payload"]
            and row["payload"].get("source_catalog_sha256") not in catalog_hashes
        ):
            raise ValidationFailure([f"course source catalog binding mismatch:{row['semantic_key']}"])
    return {
        "local_hash_bindings_replayed": local,
        "native_or_remote_bindings_deferred": deferred_native_or_remote,
    }


def _status_map(table_statuses: Any) -> dict[str, dict[str, Any]]:
    if isinstance(table_statuses, dict):
        source_items = []
        for table, raw in table_statuses.items():
            if not isinstance(raw, dict):
                raise ValidationFailure([f"table_statuses.{table} is not an object"])
            status = dict(raw)
            status["table_name"] = table
            if "count" in status:
                status["record_count"] = status["count"]
            source_items.append(status)
    elif isinstance(table_statuses, list):
        source_items = table_statuses
    else:
        raise ValidationFailure(["table_statuses must be an object or array"])
    result: dict[str, dict[str, Any]] = {}
    for index, status in enumerate(source_items):
        if not isinstance(status, dict):
            raise ValidationFailure([f"table_statuses[{index}] is not an object"])
        table = status.get("table_name")
        if table not in TABLE_TYPES:
            raise ValidationFailure([f"undeclared table status:{table!r}"])
        if table in result:
            raise ValidationFailure([f"duplicate table status:{table}"])
        if status.get("record_type") != TABLE_TYPES[table]:
            raise ValidationFailure([f"table status record_type mismatch:{table}"])
        if not isinstance(status.get("materialized"), bool):
            raise ValidationFailure([f"table status materialized is not boolean:{table}"])
        if not isinstance(status.get("record_count"), int) or status["record_count"] < 0:
            raise ValidationFailure([f"invalid table status count:{table}"])
        result[table] = status
    if set(result) != set(TABLE_TYPES):
        raise ValidationFailure(
            [f"table status inventory mismatch:missing={sorted(set(TABLE_TYPES)-set(result))}"]
        )
    return result


def _validate_hash_fields(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if (key == "sha256" or key.endswith("_sha256")) and child is not None:
                if not isinstance(child, str) or not SHA256_RE.fullmatch(child):
                    raise ValidationFailure([f"invalid SHA-256 field:{'/'.join((*path, key))}"])
            _validate_hash_fields(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_hash_fields(child, (*path, str(index)))


def _validate_record_shape(row: Any, table: str, index: int) -> None:
    if not isinstance(row, dict):
        raise ValidationFailure([f"record is not an object:{table}:{index}"])
    if set(row) != {"id", "record_type", "semantic_key", "payload"}:
        raise ValidationFailure([f"record field inventory mismatch:{table}:{index}:{sorted(row)}"])
    if row["record_type"] != TABLE_TYPES[table]:
        raise ValidationFailure([f"record type/table mismatch:{table}:{index}"])
    key = row["semantic_key"]
    if (
        not isinstance(key, str)
        or not key
        or key != key.strip()
        or key != unicodedata.normalize("NFC", key)
        or any(ord(char) < 32 for char in key)
    ):
        raise ValidationFailure([f"invalid typed semantic_key:{table}:{index}:{key!r}"])
    if not isinstance(row["payload"], dict):
        raise ValidationFailure([f"record payload is not an object:{table}:{key}"])
    expected = f"urn:uuid:{uuid.uuid5(NAMESPACE, row['record_type'] + ':' + key)}"
    if row["id"] != expected:
        raise ValidationFailure([f"UUIDv5 mismatch:{row['record_type']}:{key}"])
    _validate_hash_fields(row)


def _iter_reference_values(value: Any) -> Iterable[str]:
    if value is None:
        return
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, list):
        for child in value:
            if not isinstance(child, str):
                raise ValidationFailure([f"reference array contains non-string:{child!r}"])
            yield child
        return
    raise ValidationFailure([f"reference field has invalid value:{value!r}"])


def _walk_fields(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield (*path, key), key, child
            yield from _walk_fields(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_fields(child, (*path, str(index)))


def _validate_references(records: list[dict[str, Any]]) -> int:
    by_id = {row["id"]: row for row in records}
    by_typed_key = {(row["record_type"], row["semantic_key"]): row for row in records}
    courses_by_key = {
        row["payload"].get("course_id", row["semantic_key"]): row
        for row in records
        if row["record_type"] == "course"
    }
    checked = 0
    for row in records:
        payload = row["payload"]
        for field, expected_type in RECORD_REFERENCE_RULES.get(row["record_type"], {}).items():
            if field not in payload or payload[field] is None:
                continue
            for reference in _iter_reference_values(payload[field]):
                target = by_id.get(reference)
                if target is None:
                    raise ValidationFailure(
                        [f"dangling typed foreign key:{row['semantic_key']}:{field}:{reference}"]
                    )
                if target["record_type"] != expected_type:
                    raise ValidationFailure(
                        [f"foreign key type mismatch:{row['semantic_key']}:{field}:{expected_type}"]
                    )
                checked += 1
        for field in COURSE_KEY_REFERENCE_FIELDS.get(row["record_type"], set()):
            if field not in payload:
                continue
            for reference in _iter_reference_values(payload[field]):
                if reference not in courses_by_key:
                    raise ValidationFailure(
                        [f"dangling course-key reference:{row['semantic_key']}:{field}:{reference}"]
                    )
                checked += 1
        if row["record_type"] == "qa_event":
            for reference in _iter_reference_values(payload.get("subject_ids", [])):
                if reference not in by_id:
                    raise ValidationFailure([f"dangling QA subject:{row['semantic_key']}:{reference}"])
                checked += 1
        if row["record_type"] == "identity_crosswalk":
            target_type = payload.get("v2_record_type")
            target_key = payload.get("v2_semantic_key")
            target_id = payload.get("v2_id")
            if not all(isinstance(item, str) and item for item in (target_type, target_key, target_id)):
                raise ValidationFailure([f"invalid identity crosswalk target:{row['semantic_key']}"])
            expected = f"urn:uuid:{uuid.uuid5(NAMESPACE, target_type + ':' + target_key)}"
            if target_id != expected:
                raise ValidationFailure([f"identity crosswalk target UUID mismatch:{row['semantic_key']}"])
            materialized = by_typed_key.get((target_type, target_key))
            if materialized is not None and materialized["id"] != target_id:
                raise ValidationFailure([f"identity crosswalk materialized target mismatch:{row['semantic_key']}"])
            checked += 1
    return checked


def normalize_url(value: Any, *, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or value != unicodedata.normalize("NFC", value)
        or any(ord(char) < 32 for char in value)
    ):
        raise ValidationFailure([f"invalid URL:{label}:{value!r}"])
    parts = urlsplit(value)
    if parts.scheme.lower() not in {"https", "http"} or not parts.netloc:
        raise ValidationFailure([f"URL is not absolute HTTP(S):{label}:{value!r}"])
    if parts.username is not None or parts.password is not None:
        raise ValidationFailure([f"URL credentials forbidden:{label}:{value!r}"])
    host = parts.hostname.lower() if parts.hostname else ""
    port = parts.port
    netloc = host
    if port is not None and not ((parts.scheme.lower() == "https" and port == 443) or (parts.scheme.lower() == "http" and port == 80)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), netloc, path, parts.query, parts.fragment))


def _field(payload: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload[name]
    return default


def _state(payload: dict[str, Any]) -> str:
    value = _field(payload, "availability_state", "publication_state", "state", "status", default="")
    return value.lower() if isinstance(value, str) else ""


def _course_ref(payload: dict[str, Any]) -> str | None:
    value = _field(payload, "course_id", "course_record_id", "course_key")
    return value if isinstance(value, str) else None


def _resolve_course(
    reference: str | None,
    courses_by_id: dict[str, dict[str, Any]],
    courses_by_key: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if reference is None:
        return None
    return courses_by_id.get(reference) or courses_by_key.get(reference)


def _validate_learner_routes(tables: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    courses = tables["courses"]
    surfaces = tables["reader_surfaces"]
    routes = tables["web_routes"]
    courses_by_id = {row["id"]: row for row in courses}
    courses_by_key: dict[str, dict[str, Any]] = {}
    for row in courses:
        courses_by_key[row["semantic_key"]] = row
        course_key = row["payload"].get("course_id")
        if isinstance(course_key, str):
            if course_key in courses_by_key and courses_by_key[course_key] is not row:
                raise ValidationFailure([f"duplicate course key:{course_key}"])
            courses_by_key[course_key] = row
    surfaces_by_course: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for surface in surfaces:
        payload = surface["payload"]
        course_references = payload.get("course_ids")
        if course_references is None:
            course_references = [_course_ref(payload)]
        if not isinstance(course_references, list) or not course_references:
            raise ValidationFailure([f"reader surface has no course references:{surface['semantic_key']}"])
        actions = payload.get("actions")
        if actions is None:
            actions = [_field(payload, "action", "action_type", "format")]
        if not isinstance(actions, list) or not actions or any(action not in ACTION_RANK for action in actions):
            raise ValidationFailure([f"invalid learner actions:{surface['semantic_key']}:{actions!r}"])
        ranks = [ACTION_RANK[action] for action in actions]
        if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
            raise ValidationFailure([f"reader surface actions violate bound order:{surface['semantic_key']}"])
        if bool(_field(payload, "primary", "is_primary", default=False)) and "learn" not in actions:
            raise ValidationFailure([f"non-learn reader surface cannot be primary:{surface['semantic_key']}"])
        url = _field(payload, "url", "href", "learner_url")
        normalize_url(url, label=f"reader_surface:{surface['semantic_key']}")
        for reference in course_references:
            course = _resolve_course(reference, courses_by_id, courses_by_key)
            if course is None:
                raise ValidationFailure([f"reader surface course missing:{surface['semantic_key']}:{reference}"])
            surfaces_by_course[course["id"]].append(surface)

    learner_surface_count = 0
    artifact_surface_bindings = 0
    for course in courses:
        payload = course["payload"]
        learner_start = normalize_url(
            _field(payload, "learner_start_url"), label=f"course:{course['semantic_key']}:learner_start_url"
        )
        artifact_matrix = payload.get("artifact_matrix")
        if not isinstance(artifact_matrix, dict):
            raise ValidationFailure([f"course lacks artifact matrix:{course['semantic_key']}"])
        matrix_keys = set(artifact_matrix)
        if matrix_keys != set(ACTION_ORDER):
            raise ValidationFailure([f"course artifact matrix action inventory mismatch:{course['semantic_key']}"])
        if normalize_url(artifact_matrix.get("learn"), label=f"course:{course['semantic_key']}:artifact_matrix.learn") != learner_start:
            raise ValidationFailure([f"course learner_start/artifact_matrix.learn mismatch:{course['semantic_key']}"])
        for action, value in artifact_matrix.items():
            if value is not None:
                normalized_artifact = normalize_url(
                    value, label=f"course:{course['semantic_key']}:artifact_matrix.{action}"
                )
                matching = [
                    row
                    for row in surfaces_by_course.get(course["id"], [])
                    if action
                    in (
                        row["payload"].get("actions")
                        or [_field(row["payload"], "action", "action_type", "format")]
                    )
                    and normalize_url(
                        _field(row["payload"], "url", "href", "learner_url"),
                        label=f"reader_surface:{row['semantic_key']}",
                    )
                    == normalized_artifact
                ]
                if not matching:
                    raise ValidationFailure(
                        [f"artifact matrix action lacks matching reader surface:{course['semantic_key']}:{action}"]
                    )
                artifact_surface_bindings += 1
        candidate_surfaces = [
            row
            for row in surfaces_by_course.get(course["id"], [])
            if _state(row["payload"]) not in NONPUBLIC_STATES
        ]
        learner_surfaces = [
            row
            for row in candidate_surfaces
            if "learn" in (row["payload"].get("actions") or [_field(row["payload"], "action", "action_type", "format")])
            and normalize_url(
                _field(row["payload"], "url", "href", "learner_url"),
                label=f"reader_surface:{row['semantic_key']}",
            )
            == learner_start
        ]
        if not learner_surfaces:
            raise ValidationFailure([f"course has no matching available learn surface:{course['semantic_key']}"])
        learner_surface_count += len(learner_surfaces)

    seen_paths: dict[str, str] = {}
    seen_public_urls: dict[str, str] = {}
    routes_by_id = {row["id"]: row for row in routes}
    for route in routes:
        payload = route["payload"]
        path_value = _field(payload, "path", "route")
        if isinstance(path_value, str) and path_value.startswith("/"):
            normalized_path = path_value.rstrip("/") or "/"
            if normalized_path in seen_paths:
                raise ValidationFailure([f"duplicate web route path:{normalized_path}:{seen_paths[normalized_path]}:{route['semantic_key']}"])
            seen_paths[normalized_path] = route["semantic_key"]
        state = _state(payload)
        public_url = _field(payload, "public_url", "url", "route_url", "href")
        if state in NONPUBLIC_STATES:
            if public_url is not None:
                raise ValidationFailure([f"planned/unpublished route exposes public_url:{route['semantic_key']}"])
        elif public_url is not None:
            normalized_url = normalize_url(public_url, label=f"web_route:{route['semantic_key']}")
            if normalized_url in seen_public_urls:
                raise ValidationFailure([f"duplicate web route URL:{normalized_url}:{seen_public_urls[normalized_url]}:{route['semantic_key']}"])
            seen_public_urls[normalized_url] = route["semantic_key"]
        course_references = payload.get("course_ids")
        if course_references is None:
            reference = _course_ref(payload)
            course_references = [] if reference is None else [reference]
        for reference in course_references:
            if _resolve_course(reference, courses_by_id, courses_by_key) is None:
                raise ValidationFailure([f"web route course missing:{route['semantic_key']}:{reference}"])

    for course in courses:
        payload = course["payload"]
        route_id = payload.get("web_route_id")
        route = routes_by_id.get(route_id)
        if route is None:
            raise ValidationFailure([f"course web_route_id missing:{course['semantic_key']}:{route_id}"])
        course_key = payload.get("course_id", course["semantic_key"])
        route_courses = route["payload"].get("course_ids", [])
        if course_key not in route_courses:
            raise ValidationFailure([f"course not present in bound web route:{course['semantic_key']}"])
        public_url = route["payload"].get("public_url")
        if public_url is None:
            raise ValidationFailure([f"course-bound current web route is not public:{course['semantic_key']}"])
        if normalize_url(payload.get("web_route_root"), label=f"course:{course_key}:web_route_root") != normalize_url(
            public_url, label=f"web_route:{route['semantic_key']}:public_url"
        ):
            raise ValidationFailure([f"course web_route_root mismatch:{course['semantic_key']}"])
        fallback = route["payload"].get("learner_fallback_url")
        if fallback is not None and normalize_url(fallback, label=f"web_route:{route['semantic_key']}:fallback") != normalize_url(
            payload.get("learner_start_url"), label=f"course:{course_key}:learner_start_url"
        ):
            raise ValidationFailure([f"course learner fallback mismatch:{course['semantic_key']}"])
        if payload.get("unit_route_state") in {"not_published", "planned_not_published"}:
            if route["payload"].get("unit_route_state") not in {"not_published", "planned_not_published"}:
                raise ValidationFailure([f"planned unit route state mismatch:{course['semantic_key']}"])

    return {
        "course_count": len(courses),
        "matching_learn_surfaces": learner_surface_count,
        "artifact_surface_bindings": artifact_surface_bindings,
        "web_routes": len(routes),
    }


def _course_prerequisites(row: dict[str, Any]) -> list[str]:
    payload = row["payload"]
    value = _field(payload, "prerequisite_course_ids", "prerequisite_course_keys", default=[])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValidationFailure([f"invalid prerequisite list:{row['semantic_key']}"])
    return value


def _validate_prerequisite_dag(courses: list[dict[str, Any]]) -> int:
    by_id = {row["id"]: row for row in courses}
    by_key = {row["semantic_key"]: row for row in courses}
    by_key.update(
        {
            row["payload"]["course_id"]: row
            for row in courses
            if isinstance(row["payload"].get("course_id"), str)
        }
    )
    adjacency: dict[str, list[str]] = {}
    for row in courses:
        resolved: list[str] = []
        for value in _course_prerequisites(row):
            target = by_id.get(value) or by_key.get(value)
            if target is None:
                raise ValidationFailure([f"missing prerequisite course:{row['semantic_key']}:{value}"])
            resolved.append(target["id"])
        if len(resolved) != len(set(resolved)):
            raise ValidationFailure([f"duplicate prerequisite:{row['semantic_key']}"])
        adjacency[row["id"]] = resolved

    colors: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        state = colors.get(node, 0)
        if state == 1:
            cycle = " -> ".join([*stack, node])
            raise ValidationFailure([f"prerequisite cycle:{cycle}"])
        if state == 2:
            return
        colors[node] = 1
        for target in adjacency[node]:
            visit(target, [*stack, node])
        colors[node] = 2

    for node in adjacency:
        visit(node, [])
    return sum(len(values) for values in adjacency.values())


def _owner_task_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = TASK_ID_RE.fullmatch(value)
    return match.group(1) if match else None


def _validate_dataset_authority_and_profile(
    envelope: dict[str, Any], tables: dict[str, list[dict[str, Any]]]
) -> dict[str, int]:
    datasets = tables["datasets"]
    task_owners: set[str] = set()
    corpus_count = 0
    research_count = 0
    for row in datasets:
        payload = row["payload"]
        role = _field(payload, "dataset_kind", "dataset_role", "role", "profile")
        is_research_support = role in {"research_support", "research-support"}
        owner = _field(
            payload,
            "canonical_owner_locator",
            "canonical_owner_id",
            "canonical_owner_authority",
        )
        if not is_research_support and (
            not isinstance(owner, str)
            or not owner.strip()
            or any(ord(char) < 32 for char in owner)
        ):
            raise ValidationFailure([f"missing/invalid canonical owner authority:{row['semantic_key']}"])
        # A release/repository URI is valid owner authority (notably C80), so
        # task-shaped ownership is deliberately not required per dataset.
        if isinstance(owner, str) and "://" in owner:
            parts = urlsplit(owner)
            if parts.scheme not in {"https", "codex"} or not parts.netloc:
                raise ValidationFailure([f"invalid owner authority URI:{row['semantic_key']}:{owner}"])
        task_id = _owner_task_id(owner)
        if task_id:
            task_owners.add(task_id)
        if role in {"curriculum", "curriculum_corpus", "curriculum_owner", "corpus"}:
            corpus_count += 1
        elif is_research_support:
            research_count += 1

    schema_name = str(envelope.get("schema_name", envelope.get("schema_id", "")))
    profile = envelope.get("release_policy_profile", {})
    is_pmi = schema_name.startswith("interlanguage/program-matematika-indonesia") or schema_name.startswith(
        "interlanguage/global-modular-mathematics-federation-package/"
    ) or (
        isinstance(profile, dict) and profile.get("profile_id") == "program-matematika-indonesia-phase-one"
    )
    if is_pmi:
        if len(tables["courses"]) != 40:
            raise ValidationFailure([f"PMI course count mismatch:{len(tables['courses'])}:expected=40"])
        if len(datasets) != 34:
            raise ValidationFailure([f"PMI dataset count mismatch:{len(datasets)}:expected=34"])
        if corpus_count != 33:
            raise ValidationFailure([f"PMI curriculum-owner dataset count mismatch:{corpus_count}:expected=33"])
        if research_count != 1:
            raise ValidationFailure([f"PMI research-support dataset count mismatch:{research_count}:expected=1"])
        if len(task_owners) != 32:
            raise ValidationFailure([f"PMI nonempty task-owner count mismatch:{len(task_owners)}:expected=32"])
    return {
        "datasets": len(datasets),
        "curriculum_owner_datasets": corpus_count,
        "research_support_datasets": research_count,
        "distinct_task_owners": len(task_owners),
    }


def _readback_pass(payload: dict[str, Any]) -> bool:
    direct = _field(payload, "public_readback_result", "readback_result")
    if direct == "pass":
        return True
    nested = _field(payload, "public_readback", "readback")
    return isinstance(nested, dict) and _field(nested, "result", "status") == "pass"


def _validate_publication_and_rights(tables: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    published = 0
    readback = 0
    published_datasets = 0
    for dataset in tables["datasets"]:
        payload = dataset["payload"]
        state = _state(payload)
        if state in PUBLICATION_STATES:
            published_datasets += 1
            if not payload.get("reader_surface_ids"):
                raise ValidationFailure([f"published dataset lacks reader surfaces:{dataset['semantic_key']}"])
            if payload.get("migration_validation_result") not in {"pass", "not_applicable"}:
                raise ValidationFailure([f"published dataset lacks passing migration evidence:{dataset['semantic_key']}"])
            manifest_url = _field(payload, "package_manifest_url", "manifest_url")
            manifest_locator = _field(payload, "package_manifest_locator", "manifest_locator")
            manifest_sha = _field(payload, "package_manifest_sha256", "manifest_sha256")
            if manifest_url is not None:
                normalize_url(manifest_url, label=f"dataset:{dataset['semantic_key']}:manifest")
            if manifest_sha is not None and (not isinstance(manifest_sha, str) or not SHA256_RE.fullmatch(manifest_sha)):
                raise ValidationFailure([f"published dataset invalid manifest hash:{dataset['semantic_key']}"])
            if manifest_sha is not None and manifest_url is None and not isinstance(manifest_locator, str):
                raise ValidationFailure([f"published dataset manifest hash lacks locator:{dataset['semantic_key']}"])
            receipt_locator = payload.get("migration_receipt_locator")
            receipt_sha = payload.get("migration_receipt_sha256")
            if manifest_sha is None and not (
                isinstance(receipt_locator, str)
                and isinstance(receipt_sha, str)
                and SHA256_RE.fullmatch(receipt_sha)
            ):
                raise ValidationFailure([f"published dataset lacks manifest or migration-receipt binding:{dataset['semantic_key']}"])

    for event in tables["publication_events"]:
        payload = event["payload"]
        state = _state(payload)
        if state not in PUBLICATION_STATES:
            continue
        published += 1
        public_url = _field(payload, "public_url", "url", "record_url")
        normalize_url(public_url, label=f"publication_event:{event['semantic_key']}")
        artifacts = _field(payload, "artifacts", "files", default=[])
        if artifacts:
            if not isinstance(artifacts, list):
                raise ValidationFailure([f"published event artifact inventory invalid:{event['semantic_key']}"])
            for index, artifact in enumerate(artifacts):
                if not isinstance(artifact, dict):
                    raise ValidationFailure([f"published artifact is not an object:{event['semantic_key']}:{index}"])
                if not isinstance(artifact.get("bytes"), int) or artifact["bytes"] < 0:
                    raise ValidationFailure([f"published artifact invalid bytes:{event['semantic_key']}:{index}"])
                if not isinstance(artifact.get("sha256"), str) or not SHA256_RE.fullmatch(artifact["sha256"]):
                    raise ValidationFailure([f"published artifact invalid hash:{event['semantic_key']}:{index}"])
                if "url" in artifact:
                    normalize_url(artifact["url"], label=f"publication_event:{event['semantic_key']}:artifact:{index}")
        else:
            artifact_count = payload.get("artifact_count")
            total_bytes = payload.get("total_bytes")
            if artifact_count is not None and (not isinstance(artifact_count, int) or artifact_count < 0):
                raise ValidationFailure([f"published event invalid artifact_count:{event['semantic_key']}"])
            if total_bytes is not None and (not isinstance(total_bytes, int) or total_bytes < 0):
                raise ValidationFailure([f"published event invalid total_bytes:{event['semantic_key']}"])
        evidence_locator = payload.get("evidence_locator")
        evidence_sha = payload.get("evidence_sha256")
        if not isinstance(evidence_locator, str) or not evidence_locator:
            raise ValidationFailure([f"published event lacks evidence locator:{event['semantic_key']}"])
        if not isinstance(evidence_sha, str) or not SHA256_RE.fullmatch(evidence_sha):
            raise ValidationFailure([f"published event lacks evidence hash:{event['semantic_key']}"])
        if _readback_pass(payload) or "readback" in state:
            readback += 1
            if payload.get("evidence_kind") not in {
                None,
                "anonymous_public_readback",
                "public_readback",
            }:
                raise ValidationFailure([f"readback-verified event has wrong evidence kind:{event['semantic_key']}"])
    return {
        "published_datasets": published_datasets,
        "published_events": published,
        "readback_bound_events": readback,
        "rights_gate": "delegated_to_hash_bound_native_package_or_migration_receipt",
    }


def _validate_tables_and_projections(
    package: Path,
    envelope: dict[str, Any],
    statuses: dict[str, dict[str, Any]],
    record_validator: Draft202012Validator | None,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, int]]:
    embedded_tables = envelope.get("tables")
    if embedded_tables is not None and not isinstance(embedded_tables, dict):
        raise ValidationFailure(["tables must be an object when embedded"])
    materialized = {name for name, status in statuses.items() if status["materialized"]}
    declared_materialized = envelope.get("materialized_tables")
    if declared_materialized is not None and (
        not isinstance(declared_materialized, list) or set(declared_materialized) != materialized
    ):
        raise ValidationFailure(["materialized_tables does not match table_statuses"])
    if embedded_tables is not None and set(embedded_tables) != materialized:
        raise ValidationFailure(
            [f"materialized table inventory mismatch:declared={sorted(materialized)}:embedded={sorted(embedded_tables)}"]
        )
    tables: dict[str, list[dict[str, Any]]] = {}
    table_counts: dict[str, int] = {}
    all_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for table in sorted(materialized):
        status = statuses[table]
        jsonl_relative = status.get("jsonl_file") or f"data/{table}.jsonl"
        csv_relative = status.get("csv_file") or f"csv/{table}.csv"
        jsonl_path = _resolve_inside(
            package,
            safe_relative_path(jsonl_relative, label=f"table_statuses.{table}.jsonl_file"),
            label=f"table_statuses.{table}.jsonl_file",
        )
        csv_path = _resolve_inside(
            package,
            safe_relative_path(csv_relative, label=f"table_statuses.{table}.csv_file"),
            label=f"table_statuses.{table}.csv_file",
        )
        rows = load_jsonl(jsonl_path)
        if not rows:
            raise ValidationFailure([f"empty emitted table:{table}"])
        if embedded_tables is not None and embedded_tables[table] != rows:
            raise ValidationFailure([f"embedded table/JSONL mismatch:{table}"])
        if statuses[table]["record_count"] != len(rows):
            raise ValidationFailure([f"table status count mismatch:{table}"])
        expected_rows = sorted(rows, key=lambda row: (row.get("record_type", ""), row.get("semantic_key", "")))
        if rows != expected_rows:
            raise ValidationFailure([f"table is not canonical semantic-key sorted:{table}"])
        for index, row in enumerate(rows):
            _validate_record_shape(row, table, index)
            pair = (row["record_type"], row["semantic_key"])
            if pair in seen_pairs:
                raise ValidationFailure([f"duplicate typed semantic key:{pair[0]}:{pair[1]}"])
            if row["id"] in seen_ids:
                raise ValidationFailure([f"duplicate record ID:{row['id']}"])
            seen_ids.add(row["id"])
            seen_pairs.add(pair)
            if record_validator is not None:
                schema_errors = sorted(
                    record_validator.iter_errors(row),
                    key=lambda error: [str(item) for item in error.absolute_path],
                )
                if schema_errors:
                    first = schema_errors[0]
                    raise ValidationFailure(
                        [
                            f"record schema failure:{table}:{row['semantic_key']}:"
                            f"{list(first.absolute_path)}:{first.message}"
                        ]
                    )
        csv_rows = load_lossless_csv(csv_path)
        if csv_rows != rows:
            raise ValidationFailure([f"table CSV lossless round-trip mismatch:{table}"])
        tables[table] = rows
        table_counts[table] = len(rows)
        all_records.extend(rows)

    for table, status in statuses.items():
        if not status["materialized"]:
            if status["record_count"] != 0:
                raise ValidationFailure([f"unmaterialized table has nonzero declared count:{table}"])
            jsonl_relative = status.get("jsonl_file")
            csv_relative = status.get("csv_file")
            if jsonl_relative is not None or csv_relative is not None:
                raise ValidationFailure([f"unmaterialized table declares projection paths:{table}"])
            if (package / "data" / f"{table}.jsonl").exists() or (package / "csv" / f"{table}.csv").exists():
                raise ValidationFailure([f"unmaterialized table emitted:{table}"])

    expected_all = sorted(all_records, key=lambda row: (row["record_type"], row["semantic_key"]))
    if all_records != expected_all:
        # Tables sort independently; aggregate authority has its own global order.
        all_records = expected_all
    records_file = safe_relative_path(envelope.get("records_file"), label="records_file")
    records_path = _resolve_inside(package, records_file, label="records_file")
    aggregate_jsonl = load_jsonl(records_path)
    if aggregate_jsonl != expected_all:
        raise ValidationFailure(["aggregate records.jsonl mismatch or noncanonical order"])
    csv_file = safe_relative_path(envelope.get("lossless_csv_file", "records.csv"), label="lossless_csv_file")
    csv_path = _resolve_inside(package, csv_file, label="lossless_csv_file")
    aggregate_csv = load_lossless_csv(csv_path)
    if aggregate_csv != expected_all:
        raise ValidationFailure(["aggregate records.csv lossless round-trip mismatch"])
    if envelope.get("records_sha256") != sha256_file(records_path):
        raise ValidationFailure(["records_sha256 mismatch"])
    if "records_bytes" in envelope and envelope["records_bytes"] != records_path.stat().st_size:
        raise ValidationFailure(["records_bytes mismatch"])
    if "lossless_csv_sha256" in envelope and envelope["lossless_csv_sha256"] != sha256_file(csv_path):
        raise ValidationFailure(["lossless_csv_sha256 mismatch"])
    if "lossless_csv_bytes" in envelope and envelope["lossless_csv_bytes"] != csv_path.stat().st_size:
        raise ValidationFailure(["lossless_csv_bytes mismatch"])
    if envelope.get("record_count") != len(expected_all):
        raise ValidationFailure(["record_count mismatch"])
    if envelope.get("record_counts") != table_counts:
        raise ValidationFailure(["record_counts mismatch"])
    return tables, expected_all, table_counts


def validate_package(
    package: Path,
    schema_path: Path,
    *,
    source_root: Path | None = None,
    source_roots: list[Path] | None = None,
    locator_roots: dict[str, Path] | None = None,
    record_schema_path: Path | None = None,
    replay_package: Path | None = None,
) -> dict[str, Any]:
    package = package.resolve()
    if not package.is_dir():
        raise ValidationFailure([f"package directory missing:{package}"])
    schema = load_json(schema_path.resolve(), canonical_required=False)
    Draft202012Validator.check_schema(schema)
    if record_schema_path is None:
        candidate = schema_path.resolve().with_name("federation-record-v2.schema.json")
        record_schema_path = candidate if candidate.is_file() else None
    record_validator: Draft202012Validator | None = None
    if record_schema_path is not None:
        record_schema = load_json(record_schema_path.resolve(), canonical_required=False)
        Draft202012Validator.check_schema(record_schema)
        record_validator = Draft202012Validator(record_schema, format_checker=FormatChecker())
    envelope_path = package / "federation.json"
    manifest_path = package / "manifest.json"
    envelope = load_json(envelope_path, canonical_required=True)
    manifest = load_json(manifest_path, canonical_required=True)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(envelope),
        key=lambda error: [str(item) for item in error.absolute_path],
    )
    if errors:
        first = errors[0]
        raise ValidationFailure([f"schema failure at {list(first.absolute_path)}:{first.message}"])

    namespace_value = envelope.get("identity_namespace", envelope.get("namespace_uuid"))
    formula_value = envelope.get("identity_formula", envelope.get("id_formula"))
    if namespace_value != str(NAMESPACE):
        raise ValidationFailure(["identity namespace mismatch"])
    if formula_value not in {ID_FORMULA, "UUIDv5(global_namespace, record_type + ':' + semantic_key)"}:
        raise ValidationFailure(["identity formula mismatch"])
    serialization = envelope.get("canonical_serialization")
    if not isinstance(serialization, dict) or serialization.get("encoding") != "UTF-8" or _field(
        serialization, "newline", "line_endings"
    ) != "LF":
        raise ValidationFailure(["canonical_serialization must pin UTF-8 and LF"])

    if not isinstance(manifest, dict) or "files" not in manifest:
        raise ValidationFailure(["manifest missing files inventory"])
    manifest_files = _validate_file_facts(
        manifest["files"],
        root=package,
        label="manifest.files",
        require_exact_inventory=True,
        inventory_exclusions={"manifest.json", "validation_report.json"},
    )
    envelope_files = _validate_file_facts(
        envelope.get("files"),
        root=package,
        label="federation.files",
        require_exact_inventory=False,
        inventory_exclusions=set(),
    )
    forbidden_self_inventory = {"federation.json", "manifest.json", "validation_report.json"} & set(envelope_files)
    if forbidden_self_inventory:
        raise ValidationFailure([f"envelope self/report inventory forbidden:{sorted(forbidden_self_inventory)}"])
    if not set(envelope_files).issubset(manifest_files):
        raise ValidationFailure(["envelope file inventory is not a manifest subset"])
    for relative, fact in envelope_files.items():
        other = manifest_files[relative]
        if fact.get("bytes") != other.get("bytes") or fact.get("sha256") != other.get("sha256"):
            raise ValidationFailure([f"envelope/manifest file fact mismatch:{relative}"])

    statuses = _status_map(envelope.get("table_statuses"))
    expected_projection_files = {
        safe_relative_path(envelope.get("records_file"), label="records_file"),
        safe_relative_path(envelope.get("lossless_csv_file", "records.csv"), label="lossless_csv_file"),
    }
    for table, status in statuses.items():
        if status["materialized"]:
            expected_projection_files.add(
                safe_relative_path(
                    status.get("jsonl_file") or f"data/{table}.jsonl",
                    label=f"table_statuses.{table}.jsonl_file",
                )
            )
            expected_projection_files.add(
                safe_relative_path(
                    status.get("csv_file") or f"csv/{table}.csv",
                    label=f"table_statuses.{table}.csv_file",
                )
            )
    if set(envelope_files) != expected_projection_files:
        raise ValidationFailure(
            [
                "envelope projection inventory mismatch:"
                f"missing={sorted(expected_projection_files-set(envelope_files))}:"
                f"extra={sorted(set(envelope_files)-expected_projection_files)}"
            ]
        )
    tables, records, table_counts = _validate_tables_and_projections(
        package, envelope, statuses, record_validator
    )
    if manifest.get("record_count") != len(records) or manifest.get("record_counts") != table_counts:
        raise ValidationFailure(["manifest record/table counts mismatch"])
    for field in ("dataset_id", "dataset_version"):
        if manifest.get(field) != envelope.get(field):
            raise ValidationFailure([f"manifest/envelope identity mismatch:{field}"])

    references = _validate_references(records)
    prerequisites = _validate_prerequisite_dag(tables["courses"])
    learner = _validate_learner_routes(tables)
    owner_profile = _validate_dataset_authority_and_profile(envelope, tables)
    publication = _validate_publication_and_rights(tables)
    roots = [root.resolve() for root in (source_roots or [])]
    if source_root is not None:
        roots.append(source_root.resolve())
    roots = list(dict.fromkeys(roots))
    resolved_locator_roots = {
        key: value.resolve() for key, value in (locator_roots or {}).items()
    }
    for root in resolved_locator_roots.values():
        if root not in roots:
            roots.append(root)
    source_facts = _validate_source_facts(
        envelope.get("source_evidence", envelope.get("source_facts")),
        roots,
        resolved_locator_roots,
    )
    bound_files = _validate_build_and_schema_bindings(
        envelope,
        roots=roots,
        package_schema_path=schema_path.resolve(),
        record_schema_path=record_schema_path.resolve() if record_schema_path else None,
    )
    record_evidence = _validate_record_evidence_bindings(
        records,
        roots=roots,
        locator_roots=resolved_locator_roots,
    )
    _validate_hash_fields(envelope)
    _validate_hash_fields(manifest)

    replay = {"result": "not_requested"}
    if replay_package is not None:
        replay = compare_packages(package, replay_package.resolve())
    return {
        "schema_validation": "pass",
        "canonical_json": "pass",
        "canonical_jsonl": "pass",
        "lossless_csv_roundtrip": "pass",
        "manifest_inventory": "pass",
        "table_materialization": "pass",
        "uuidv5_and_typed_semantic_keys": "pass",
        "typed_foreign_keys": "pass",
        "learner_routes": "pass",
        "prerequisite_dag": "pass",
        "rights_publication_readback": "pass",
        "record_schema_validation": "pass" if record_validator is not None else "not_supplied",
        "source_fact_replay": "pass" if roots else "structure_only",
        "record_count": len(records),
        "table_counts": table_counts,
        "typed_foreign_key_count": references,
        "prerequisite_edge_count": prerequisites,
        "source_fact_count_replayed": source_facts,
        "bound_file_count_replayed": bound_files,
        "record_evidence": record_evidence,
        "learner": learner,
        "owner_profile": owner_profile,
        "publication": publication,
        "federation_sha256": sha256_file(envelope_path),
        "manifest_sha256": sha256_file(manifest_path),
        "records_jsonl_sha256": sha256_file(package / envelope["records_file"]),
        "records_csv_sha256": sha256_file(package / "records.csv"),
        "deterministic_replay": replay,
    }


def compare_packages(first: Path, second: Path) -> dict[str, Any]:
    ignored = {"validation_report.json"}
    first_files = {
        path.relative_to(first).as_posix(): path
        for path in first.rglob("*")
        if path.is_file() and path.relative_to(first).as_posix() not in ignored
    }
    second_files = {
        path.relative_to(second).as_posix(): path
        for path in second.rglob("*")
        if path.is_file() and path.relative_to(second).as_posix() not in ignored
    }
    if set(first_files) != set(second_files):
        raise ValidationFailure(
            [
                "replay inventory mismatch:"
                f"missing={sorted(set(first_files)-set(second_files))}:"
                f"extra={sorted(set(second_files)-set(first_files))}"
            ]
        )
    mismatches = [
        relative
        for relative in sorted(first_files)
        if first_files[relative].stat().st_size != second_files[relative].stat().st_size
        or sha256_file(first_files[relative]) != sha256_file(second_files[relative])
    ]
    if mismatches:
        raise ValidationFailure([f"replay byte mismatch:{mismatches[:10]}"])
    return {"result": "byte-identical", "file_count": len(first_files)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument(
        "--source-root",
        action="append",
        type=Path,
        help="Allowed root for source_evidence paths; repeat for explicitly mixed authorities",
    )
    parser.add_argument("--program-repository-root", type=Path)
    parser.add_argument("--coordinator-logbook-root", type=Path)
    parser.add_argument("--record-schema", type=Path)
    parser.add_argument("--replay-package", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        checks = validate_package(
            args.package,
            args.schema,
            source_roots=args.source_root,
            locator_roots={
                key: value
                for key, value in {
                    "program_repository_root": args.program_repository_root,
                    "coordinator_logbook_root": args.coordinator_logbook_root,
                }.items()
                if value is not None
            },
            record_schema_path=args.record_schema,
            replay_package=args.replay_package,
        )
        report = {
            "schema_name": "interlanguage/program-matematika-indonesia-backend-v2-validation",
            "schema_version": "1.0.0",
            "package": args.package.name,
            "result": "pass",
            "checks": checks,
            "errors": [],
        }
        exit_code = 0
    except (ValidationFailure, OSError, ValueError) as exc:
        failures = exc.errors if isinstance(exc, ValidationFailure) else [str(exc)]
        report = {
            "schema_name": "interlanguage/program-matematika-indonesia-backend-v2-validation",
            "schema_version": "1.0.0",
            "package": args.package.name,
            "result": "fail",
            "checks": {},
            "errors": failures,
        }
        exit_code = 1
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(canonical(report))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
