#!/usr/bin/env python3
"""Bounded independent verifier for the Prealgebra 2e migration receipt.

This verifier intentionally does not enumerate, parse, or hash the complete
1.84 GB native backend. It validates the checked-in proof envelope, re-hashes
its small frozen authorities, and independently scans the exact 62 MB native
unit view needed to prove the external-target edge class.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


MIGRATION_ID = "prealgebra2e-r001-id-v0.2.7-to-interlanguage-v1.0.0"
NATIVE_RECORDS = 519_678
DERIVED_RECORDS = 3_368
TARGET_RECORDS = 523_046
NULL_RECOVERIES = 98
COLLECTION_STRUCTURAL_RECORDS = 12
COLLECTION_SEGMENTS = 12
COLLECTION_SOURCE_EXPRESSIONS = 12
COLLECTION_TARGET_EXPRESSIONS = 12
COLLXML_BINDINGS = 60
TARGET_ONLY_CORRECTION_SEGMENTS = 408
TARGET_ONLY_CORRECTION_EXPRESSIONS = 408
EXTERNAL_TARGET_UNITS = 183
EXTERNAL_TARGET_INVENTORY_BYTES = 50_765
EXTERNAL_TARGET_INVENTORY_SHA256 = "eba43c47aac8b1227c06b33b7fe9d34ea13381eed6d12dd43aa7d7e2eafc1e12"

RECEIPT_SCHEMA_REL = Path("schemas/backend-migration-receipt-v1.schema.json")
ADAPTER_PROFILE_REL = Path(
    "backend/migrations/prealgebra2e-id-v1/ADAPTER_PROFILE.json"
)
MIGRATION_SCRIPT_REL = Path("scripts/migrate-prealgebra2e-backend-v1.py")

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|//|\\\\\?\\)")
PRIVATE_POSIX_RE = re.compile(r"^/(?:home|root|Users|private|var/folders)/", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(
    r"(?:github_pat_|gh[pousr]_[A-Za-z0-9]|\bBearer\s+[A-Za-z0-9]|"
    r"(?:access[_-]?token|api[_-]?key|password|client[_-]?secret)\s*[:=])",
    re.IGNORECASE,
)
SENSITIVE_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "bearer",
    "client_secret",
    "password",
    "private_key",
    "secret",
    "token",
}


class Audit:
    def __init__(self) -> None:
        self.assertions = 0

    def require(self, condition: bool, message: str) -> None:
        self.assertions += 1
        if not condition:
            raise ValueError(message)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.require(actual == expected, f"{label}: {actual!r} != {expected!r}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def verify_external_target_view(
    path: Path,
    declared: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    actual = file_fact(path, declared["path"], audit)
    audit.equal(actual["bytes"], declared["bytes"], "external-target view bytes")
    audit.equal(
        actual["sha256"],
        plain_sha256(declared["sha256"], "external-target view SHA-256", audit),
        "external-target view SHA-256",
    )
    inventory: list[dict[str, str]] = []
    ids: set[str] = set()
    locators: set[str] = set()
    source_keys: set[str] = set()
    content_hashes: set[str] = set()
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            audit.require(raw.endswith(b"\n") and not raw.endswith(b"\r\n"), f"unit view line ending changed at {line_number}")
            row = json.loads(raw)
            if row.get("unit_type") != "external_target":
                continue
            record_id = row.get("id")
            locator = row.get("source_locator")
            source_key = row.get("source_key")
            content_hash = row.get("content_hash")
            audit.require(isinstance(record_id, str), "external-target ID is absent")
            parsed_id = uuid.UUID(record_id.removeprefix("urn:uuid:"))
            audit.equal(parsed_id.version, 5, f"external-target UUID version {record_id}")
            audit.require(isinstance(locator, str), f"external-target locator absent: {record_id}")
            parsed = urllib.parse.urlsplit(locator)
            audit.require(
                parsed.scheme == "https"
                and bool(parsed.hostname)
                and parsed.username is None
                and parsed.password is None,
                f"external-target locator is not absolute credential-free HTTPS: {record_id}",
            )
            audit.equal(source_key, f"external-target:{locator}", f"external-target source key {record_id}")
            audit.equal(
                content_hash,
                f"sha256:{hashlib.sha256(locator.encode('utf-8')).hexdigest()}",
                f"external-target content hash {record_id}",
            )
            audit.equal(row.get("order_path"), None, f"external-target order path {record_id}")
            audit.equal(row.get("parent_id"), None, f"external-target parent {record_id}")
            audit.equal(row.get("source_local_id"), None, f"external-target local ID {record_id}")
            audit.require(record_id not in ids, f"duplicate external-target ID: {record_id}")
            audit.require(locator not in locators, f"duplicate external-target locator: {locator}")
            audit.require(source_key not in source_keys, f"duplicate external-target source key: {source_key}")
            audit.require(content_hash not in content_hashes, f"duplicate external-target content hash: {content_hash}")
            ids.add(record_id)
            locators.add(locator)
            source_keys.add(source_key)
            content_hashes.add(content_hash)
            inventory.append(
                {
                    "content_hash": content_hash,
                    "id": record_id,
                    "source_key": source_key,
                    "source_locator": locator,
                }
            )
    audit.equal(len(inventory), EXTERNAL_TARGET_UNITS, "live external-target count")
    payload = canonical_bytes(sorted(inventory, key=lambda item: item["id"]))
    audit.equal(len(payload), EXTERNAL_TARGET_INVENTORY_BYTES, "live external-target inventory bytes")
    audit.equal(
        hashlib.sha256(payload).hexdigest(),
        EXTERNAL_TARGET_INVENTORY_SHA256,
        "live external-target inventory SHA-256",
    )
    return {
        **actual,
        "records": len(inventory),
        "canonical_inventory_bytes": len(payload),
        "canonical_inventory_sha256": hashlib.sha256(payload).hexdigest(),
    }


def load_object(path: Path, label: str, audit: Audit) -> dict[str, Any]:
    audit.require(path.is_file(), f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    audit.require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def relative_path(value: Any, label: str, audit: Audit) -> Path:
    audit.require(isinstance(value, str) and bool(value), f"{label} is not a path string")
    audit.require(
        not WINDOWS_ABSOLUTE_RE.match(value) and not value.startswith("/"),
        f"{label} is not portable: {value!r}",
    )
    path = Path(value)
    audit.require(".." not in path.parts, f"{label} contains parent traversal: {value!r}")
    return path


def confined(root: Path, value: Any, label: str, audit: Audit) -> Path:
    relative = relative_path(value, label, audit)
    candidate = (root / relative).resolve()
    audit.require(
        candidate == root or root in candidate.parents,
        f"{label} resolves outside its declared root",
    )
    return candidate


def file_fact(path: Path, portable: str, audit: Audit) -> dict[str, Any]:
    audit.require(path.is_file(), f"missing frozen file: {portable}")
    return {
        "path": portable,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def assert_file_fact(
    candidate: Any,
    actual: dict[str, Any],
    label: str,
    audit: Audit,
) -> None:
    audit.require(isinstance(candidate, dict), f"{label} fact is not an object")
    for key in ("path", "bytes", "sha256"):
        audit.require(key in candidate, f"{label} fact omits {key}")
    audit.equal(candidate["path"], actual["path"], f"{label} path")
    audit.equal(candidate["bytes"], actual["bytes"], f"{label} bytes")
    audit.equal(candidate["sha256"], actual["sha256"], f"{label} sha256")
    audit.require(SHA256_RE.fullmatch(candidate["sha256"]) is not None, f"{label} SHA-256 format")


def plain_sha256(value: Any, label: str, audit: Audit) -> str:
    audit.require(isinstance(value, str), f"{label} is not a string")
    digest = value.removeprefix("sha256:")
    audit.require(SHA256_RE.fullmatch(digest) is not None, f"{label} is not SHA-256")
    return digest


def scan_portability_and_credentials(value: Any, path: str, audit: Audit) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
            if normalized == "credentials_recorded":
                audit.require(child is False, f"{path}.{key} must be false")
            elif normalized in SENSITIVE_KEYS:
                audit.require(child in (None, False, "", []), f"credential-bearing key at {path}.{key}")
            scan_portability_and_credentials(child, f"{path}.{key}", audit)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            scan_portability_and_credentials(child, f"{path}[{index}]", audit)
        return
    if isinstance(value, str):
        audit.require(
            WINDOWS_ABSOLUTE_RE.match(value) is None
            and PRIVATE_POSIX_RE.match(value) is None
            and not value.lower().startswith("file:" + "//"),
            f"private absolute path at {path}",
        )
        audit.require(SECRET_VALUE_RE.search(value) is None, f"credential-like value at {path}")


def verify(args: argparse.Namespace) -> dict[str, Any]:
    audit = Audit()
    hub = args.hub_root.resolve()
    corpus = args.corpus_root.resolve()
    receipt_path = args.expected_receipt.resolve()
    audit.require(hub.is_dir(), "hub root is not a directory")
    audit.require(corpus.is_dir(), "corpus root is not a directory")

    schema_path = hub / RECEIPT_SCHEMA_REL
    profile_path = hub / ADAPTER_PROFILE_REL
    migration_script_path = hub / MIGRATION_SCRIPT_REL
    schema = load_object(schema_path, "migration receipt schema", audit)
    profile = load_object(profile_path, "adapter profile", audit)
    receipt = load_object(receipt_path, "expected migration receipt", audit)

    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    audit.require(
        not schema_errors,
        "receipt schema validation failed: "
        + (schema_errors[0].message if schema_errors else "unknown error"),
    )

    audit.equal(profile.get("migration_id"), MIGRATION_ID, "profile migration ID")
    audit.equal(receipt.get("migration_id"), MIGRATION_ID, "receipt migration ID")
    audit.equal(
        profile.get("schema_name"),
        "interlanguage-prealgebra2e-common-backend-adapter-profile",
        "profile schema name",
    )
    audit.equal(profile.get("schema_version"), "1.0.0", "profile schema version")

    expected = profile.get("expected")
    audit.require(isinstance(expected, dict), "profile expected-count block is absent")
    for key, frozen in (
        ("native_records", NATIVE_RECORDS),
        ("common_derived_records", DERIVED_RECORDS),
        ("target_records", TARGET_RECORDS),
        ("target_only_localized_correction_units", NULL_RECOVERIES),
        ("source_collection_structural_units", COLLECTION_STRUCTURAL_RECORDS),
        ("target_collection_structural_occurrences", COLLECTION_STRUCTURAL_RECORDS),
        ("source_collection_segments", COLLECTION_SEGMENTS),
        ("source_collection_expressions", COLLECTION_SOURCE_EXPRESSIONS),
        ("target_collection_expressions", COLLECTION_TARGET_EXPRESSIONS),
        ("common_collxml_bindings", COLLXML_BINDINGS),
        ("target_only_correction_segments", TARGET_ONLY_CORRECTION_SEGMENTS),
        ("target_only_correction_expressions", TARGET_ONLY_CORRECTION_EXPRESSIONS),
        ("external_target_units", EXTERNAL_TARGET_UNITS),
        ("external_target_inventory_bytes", EXTERNAL_TARGET_INVENTORY_BYTES),
        ("external_target_inventory_sha256", EXTERNAL_TARGET_INVENTORY_SHA256),
    ):
        audit.equal(expected.get(key), frozen, f"profile expected.{key}")
    audit.equal(NATIVE_RECORDS + DERIVED_RECORDS, TARGET_RECORDS, "frozen record arithmetic")

    views = profile.get("source", {}).get("views")
    audit.require(isinstance(views, list) and bool(views), "profile source views are absent")
    audit.require(
        all(isinstance(view, dict) and isinstance(view.get("records"), int) for view in views),
        "profile source view counts are invalid",
    )
    audit.equal(sum(view["records"] for view in views), NATIVE_RECORDS, "profile native view sum")

    profile_source = profile["source"]
    backend_root = confined(corpus, profile_source["backend_root"], "profile backend root", audit)
    admission_path = confined(
        corpus,
        profile["frozen_authority"]["admission"]["path"],
        "profile admission path",
        audit,
    )
    handoff_path = confined(
        corpus,
        profile["frozen_authority"]["handoff"]["path"],
        "profile handoff path",
        audit,
    )
    manifest_path = confined(
        corpus,
        profile["frozen_authority"]["backend_manifest"]["path"],
        "profile manifest path",
        audit,
    )
    expected_manifest_path = (backend_root / relative_path(
        profile_source["manifest_path"], "profile source manifest path", audit
    )).resolve()
    audit.equal(manifest_path, expected_manifest_path, "owner manifest path binding")

    admission_fact = file_fact(
        admission_path,
        profile["frozen_authority"]["admission"]["path"],
        audit,
    )
    handoff_fact = file_fact(
        handoff_path,
        profile["frozen_authority"]["handoff"]["path"],
        audit,
    )
    manifest_fact = file_fact(
        manifest_path,
        profile["frozen_authority"]["backend_manifest"]["path"],
        audit,
    )
    adapter_fact = file_fact(profile_path, ADAPTER_PROFILE_REL.as_posix(), audit)
    migration_script_fact = file_fact(
        migration_script_path,
        MIGRATION_SCRIPT_REL.as_posix(),
        audit,
    )

    assert_file_fact(
        profile["frozen_authority"]["admission"], admission_fact, "profile admission", audit
    )
    assert_file_fact(
        profile["frozen_authority"]["handoff"], handoff_fact, "profile handoff", audit
    )
    assert_file_fact(
        profile["frozen_authority"]["backend_manifest"],
        manifest_fact,
        "profile owner manifest",
        audit,
    )

    source = receipt.get("source")
    target = receipt.get("target")
    coverage = receipt.get("coverage")
    transformation = receipt.get("transformation")
    validation = receipt.get("validation")
    materialization = receipt.get("materialization")
    tables = receipt.get("tables")
    for label, value in (
        ("receipt source", source),
        ("receipt target", target),
        ("receipt coverage", coverage),
        ("receipt transformation", transformation),
        ("receipt validation", validation),
        ("receipt materialization", materialization),
        ("receipt tables", tables),
    ):
        audit.require(isinstance(value, dict), f"{label} is not an object")

    assert_file_fact(source["admission"], admission_fact, "receipt admission", audit)
    assert_file_fact(source["handoff"], handoff_fact, "receipt handoff", audit)
    receipt_manifest_fact = {
        "path": source.get("manifest_path"),
        "bytes": source.get("manifest_bytes"),
        "sha256": source.get("manifest_sha256"),
    }
    manifest_relative_to_backend = {
        **manifest_fact,
        "path": profile_source["manifest_path"],
    }
    assert_file_fact(
        receipt_manifest_fact,
        manifest_relative_to_backend,
        "receipt owner manifest",
        audit,
    )
    assert_file_fact(source["adapter_profile"], adapter_fact, "receipt adapter profile", audit)
    audit.equal(
        materialization.get("adapter_profile_path"),
        ADAPTER_PROFILE_REL.as_posix(),
        "materialization adapter profile path",
    )
    audit.equal(
        materialization.get("script_path"),
        MIGRATION_SCRIPT_REL.as_posix(),
        "materialization migration script path",
    )
    assert_file_fact(
        materialization.get("migration_script"),
        migration_script_fact,
        "receipt migration script",
        audit,
    )

    manifest = load_object(manifest_path, "owner backend manifest", audit)
    admission = load_object(admission_path, "owner admission", audit)
    audit.equal(manifest.get("records_total"), NATIVE_RECORDS, "owner manifest records")
    audit.equal(manifest.get("module_count"), expected["module_references"], "owner manifest modules")
    admitted_backend = admission.get("accepted_artifacts", {}).get("backend")
    audit.require(isinstance(admitted_backend, dict), "owner admission backend block is absent")
    audit.equal(admitted_backend.get("records"), NATIVE_RECORDS, "admission backend records")
    audit.equal(admitted_backend.get("manifest_bytes"), manifest_fact["bytes"], "admission manifest bytes")
    audit.equal(admitted_backend.get("manifest_sha256"), manifest_fact["sha256"], "admission manifest SHA-256")
    audit.equal(
        admitted_backend.get("canonical_tree_sha256"),
        profile["frozen_authority"]["accepted_backend_tree_sha256"],
        "admission/profile backend tree binding",
    )
    audit.equal(
        admitted_backend.get("input_fingerprint_sha256"),
        profile["frozen_authority"]["accepted_input_fingerprint_sha256"],
        "admission/profile input fingerprint binding",
    )
    audit.equal(
        source.get("accepted_tree_sha256"),
        admitted_backend.get("canonical_tree_sha256"),
        "receipt accepted backend tree",
    )
    audit.equal(
        source.get("input_fingerprint_sha256"),
        admitted_backend.get("input_fingerprint_sha256"),
        "receipt input fingerprint",
    )

    unit_view_path = next(
        view["path"] for view in views if view.get("native_record_type") == "unit"
    )
    unit_view_declared = next(
        item for item in manifest["files"] if item.get("path") == unit_view_path
    )
    external_target_view_fact = verify_external_target_view(
        confined(backend_root, unit_view_path, "external-target native unit view", audit),
        unit_view_declared,
        audit,
    )

    collection_receipt = coverage.get("collection_xml_authorities")
    audit.require(isinstance(collection_receipt, dict), "receipt collection authorities are absent")
    collection_facts: dict[str, dict[str, Any]] = {}
    for receipt_label, manifest_label, stable_key_label in (
        ("source_collection", "source_collection", "source_collection_revision_stable_key"),
        ("target_collection", "localized_collection", "target_collection_revision_stable_key"),
    ):
        declared = manifest.get(manifest_label)
        audit.require(isinstance(declared, dict), f"manifest {manifest_label} is absent")
        locator = declared.get("path_locator")
        live_path = confined(corpus, locator, f"manifest {manifest_label} path", audit)
        actual = file_fact(live_path, locator, audit)
        declared_digest = plain_sha256(
            declared.get("sha256"), f"manifest {manifest_label} SHA-256", audit
        )
        audit.equal(declared.get("bytes"), actual["bytes"], f"manifest {manifest_label} bytes")
        audit.equal(declared_digest, actual["sha256"], f"manifest {manifest_label} SHA-256")
        assert_file_fact(
            collection_receipt.get(receipt_label),
            actual,
            f"receipt {receipt_label}",
            audit,
        )
        stable_key = profile.get("derived", {}).get(stable_key_label)
        audit.require(
            isinstance(stable_key, str) and stable_key.endswith(f":{actual['sha256']}"),
            f"profile {stable_key_label} is not bound to the live CollXML SHA-256",
        )
        collection_facts[receipt_label] = actual

    for key, actual in (
        ("record_count", NATIVE_RECORDS),
        ("inventory_files_including_manifest", expected["native_files_including_manifest"]),
        ("inventory_bytes_including_manifest", expected["native_bytes_including_manifest"]),
    ):
        audit.equal(source.get(key), actual, f"receipt source.{key}")
    for mapping_label in ("record_counts", "view_counts"):
        mapping = source.get(mapping_label)
        audit.require(isinstance(mapping, dict), f"receipt source.{mapping_label} is absent")
        audit.require(
            all(isinstance(count, int) and count >= 0 for count in mapping.values()),
            f"receipt source.{mapping_label} contains invalid counts",
        )
        audit.equal(sum(mapping.values()), NATIVE_RECORDS, f"receipt source.{mapping_label} sum")

    for actual, frozen, label in (
        (coverage.get("native_records"), NATIVE_RECORDS, "coverage native records"),
        (coverage.get("native_records_reversibly_embedded"), NATIVE_RECORDS, "coverage reversible records"),
        (coverage.get("common_derived_records"), DERIVED_RECORDS, "coverage derived records"),
        (transformation.get("direct_common_records"), NATIVE_RECORDS, "transformation direct records"),
        (transformation.get("derived_common_records"), DERIVED_RECORDS, "transformation derived records"),
        (target.get("record_count"), TARGET_RECORDS, "target records"),
    ):
        audit.equal(actual, frozen, label)
    audit.equal(
        transformation.get("native_uuid5_ids_preserved"),
        NATIVE_RECORDS,
        "transformation native UUIDv5 preservation",
    )

    audit.require(bool(tables), "receipt has no common-backend table facts")
    table_total = 0
    nonempty_tables = 0
    for table_name, table in tables.items():
        audit.require(isinstance(table_name, str) and bool(table_name), "invalid table name")
        audit.require(isinstance(table, dict), f"table fact is not an object: {table_name}")
        records = table.get("records")
        byte_count = table.get("virtual_jsonl_bytes")
        digest = table.get("virtual_jsonl_sha256")
        audit.require(isinstance(records, int) and records >= 0, f"invalid record count: {table_name}")
        audit.require(isinstance(byte_count, int) and byte_count >= 0, f"invalid byte count: {table_name}")
        audit.require(isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None, f"invalid SHA-256: {table_name}")
        table_total += records
        nonempty_tables += int(records > 0)
    audit.equal(table_total, TARGET_RECORDS, "sum of table record counts")
    audit.equal(target.get("table_count"), len(tables), "target table count")
    audit.equal(target.get("nonempty_table_count"), nonempty_tables, "target nonempty table count")

    first_backend = validation.get("first_canonical_backend_sha256")
    second_backend = validation.get("second_canonical_backend_sha256")
    first_virtual = validation.get("first_virtual_records_jsonl_sha256")
    second_virtual = validation.get("second_virtual_records_jsonl_sha256")
    for digest, label in (
        (first_backend, "first canonical assembly SHA-256"),
        (second_backend, "second canonical assembly SHA-256"),
        (first_virtual, "first virtual JSONL SHA-256"),
        (second_virtual, "second virtual JSONL SHA-256"),
    ):
        audit.require(isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None, label)
    audit.equal(first_backend, second_backend, "two canonical assembly hashes")
    audit.equal(first_backend, target.get("canonical_backend_sha256"), "target canonical assembly hash")
    audit.equal(first_virtual, second_virtual, "two virtual JSONL assembly hashes")
    audit.equal(first_virtual, target.get("virtual_records_jsonl_sha256"), "target virtual JSONL hash")
    audit.equal(
        validation.get("two_independent_streaming_assemblies"),
        "byte-identical",
        "two-assembly disposition",
    )

    audit.equal(
        validation.get("exact_native_reverse_extraction"),
        NATIVE_RECORDS,
        "exact native reverse count",
    )
    audit.equal(
        validation.get("byte_identical_native_reverse_extractions"),
        NATIVE_RECORDS,
        "byte-identical native reverse count",
    )
    audit.equal(
        validation.get("native_null_canonical_unit_ids_recovered"),
        NULL_RECOVERIES,
        "native null recovery count",
    )
    audit.equal(
        coverage.get("target_only_localized_correction_units"),
        NULL_RECOVERIES,
        "coverage target-only null count",
    )
    target_only_projection = transformation.get("target_only_localized_correction_projection")
    audit.require(isinstance(target_only_projection, dict), "target-only projection block is absent")
    audit.equal(target_only_projection.get("native_records"), NULL_RECOVERIES, "target-only native count")
    audit.equal(target_only_projection.get("derived_technical_units"), NULL_RECOVERIES, "target-only derived count")
    audit.equal(
        target_only_projection.get("native_segments_without_source_locator"),
        TARGET_ONLY_CORRECTION_SEGMENTS,
        "target-only null-locator segment count",
    )
    audit.equal(
        target_only_projection.get("target_expressions_without_source_variant"),
        TARGET_ONLY_CORRECTION_EXPRESSIONS,
        "target-only source-less expression count",
    )

    audit.equal(
        coverage.get("source_collection_structural_units"),
        COLLECTION_STRUCTURAL_RECORDS,
        "source collection structural count",
    )
    audit.equal(
        coverage.get("target_collection_structural_occurrences"),
        COLLECTION_STRUCTURAL_RECORDS,
        "target collection structural count",
    )
    audit.equal(coverage.get("source_collection_segments"), COLLECTION_SEGMENTS, "source collection segment count")
    audit.equal(
        coverage.get("source_collection_expressions"),
        COLLECTION_SOURCE_EXPRESSIONS,
        "source collection expression count",
    )
    audit.equal(
        coverage.get("target_collection_expressions"),
        COLLECTION_TARGET_EXPRESSIONS,
        "target collection expression count",
    )
    audit.equal(coverage.get("common_collxml_bindings"), COLLXML_BINDINGS, "common CollXML binding count")
    audit.equal(
        coverage.get("target_only_correction_segments"),
        TARGET_ONLY_CORRECTION_SEGMENTS,
        "target-only correction segment count",
    )
    audit.equal(
        coverage.get("target_only_correction_expressions"),
        TARGET_ONLY_CORRECTION_EXPRESSIONS,
        "target-only correction expression count",
    )
    audit.equal(
        coverage.get("external_target_units"),
        EXTERNAL_TARGET_UNITS,
        "external-target unit count",
    )
    audit.equal(
        coverage.get("external_target_inventory_bytes"),
        EXTERNAL_TARGET_INVENTORY_BYTES,
        "external-target inventory bytes",
    )
    audit.equal(
        coverage.get("external_target_inventory_sha256"),
        EXTERNAL_TARGET_INVENTORY_SHA256,
        "external-target inventory SHA-256",
    )
    audit.equal(
        transformation.get("external_target_unit_mapping"),
        "direct unit projection with preserved unique HTTPS source_path and no false XML profile",
        "external-target mapping declaration",
    )
    external_target_proof = coverage.get("external_target_proof")
    audit.require(isinstance(external_target_proof, dict), "external-target proof block is absent")
    for key, expected_value in (
        ("records", EXTERNAL_TARGET_UNITS),
        ("unique_ids", EXTERNAL_TARGET_UNITS),
        ("unique_locators", EXTERNAL_TARGET_UNITS),
        ("unique_source_keys", EXTERNAL_TARGET_UNITS),
        ("unique_content_hashes", EXTERNAL_TARGET_UNITS),
        ("content_hash_equals_sha256_utf8_locator", EXTERNAL_TARGET_UNITS),
        ("absolute_https_without_userinfo", EXTERNAL_TARGET_UNITS),
        ("source_xml_path_null", EXTERNAL_TARGET_UNITS),
        ("source_profile_extensions", 0),
        ("canonical_inventory_bytes", EXTERNAL_TARGET_INVENTORY_BYTES),
        ("canonical_inventory_sha256", EXTERNAL_TARGET_INVENTORY_SHA256),
    ):
        audit.equal(
            external_target_proof.get(key), expected_value, f"external-target proof {key}"
        )
    collection_projection = transformation.get("collection_xml_projection")
    audit.require(isinstance(collection_projection, dict), "collection projection block is absent")
    audit.equal(
        collection_projection.get("source_structural_units"),
        COLLECTION_STRUCTURAL_RECORDS,
        "collection projection source count",
    )
    audit.equal(
        collection_projection.get("target_structural_occurrences"),
        COLLECTION_STRUCTURAL_RECORDS,
        "collection projection target count",
    )
    audit.equal(collection_projection.get("source_segments"), COLLECTION_SEGMENTS, "collection projection segment count")
    audit.equal(
        collection_projection.get("source_expressions"),
        COLLECTION_SOURCE_EXPRESSIONS,
        "collection projection source-expression count",
    )
    audit.equal(
        collection_projection.get("target_expressions"),
        COLLECTION_TARGET_EXPRESSIONS,
        "collection projection target-expression count",
    )
    audit.equal(
        collection_projection.get("common_collxml_bindings"),
        COLLXML_BINDINGS,
        "collection projection CollXML binding count",
    )
    audit.equal(
        validation.get("common_collxml_bindings"),
        COLLXML_BINDINGS,
        "validation CollXML binding count",
    )
    audit.equal(
        validation.get("source_and_target_collection_xml_authority_binding"),
        "pass",
        "collection authority validation",
    )

    scan_portability_and_credentials(profile, "profile", audit)
    scan_portability_and_credentials(receipt, "receipt", audit)
    audit.equal(receipt.get("credentials_recorded"), False, "receipt credentials flag")

    return {
        "assertions": audit.assertions,
        "authority_files_rehashed": 8,
        "collection_source_sha256": collection_facts["source_collection"]["sha256"],
        "collection_target_sha256": collection_facts["target_collection"]["sha256"],
        "derived_records": DERIVED_RECORDS,
        "migration_id": MIGRATION_ID,
        "migration_script_sha256": migration_script_fact["sha256"],
        "full_native_backend_materialized_or_scanned": False,
        "targeted_native_view_scanned": external_target_view_fact,
        "native_records": NATIVE_RECORDS,
        "receipt_bytes": receipt_path.stat().st_size,
        "receipt_sha256": sha256_file(receipt_path),
        "result": "pass",
        "target_records": TARGET_RECORDS,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Independently validate the bounded Prealgebra 2e common-backend "
            "migration receipt without scanning or materializing the complete native "
            "backend; the exact native unit view is scanned for external-target proof."
        )
    )
    value.add_argument("--hub-root", required=True, type=Path)
    value.add_argument("--corpus-root", required=True, type=Path)
    value.add_argument("--expected-receipt", required=True, type=Path)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        result = verify(args)
    except Exception as exc:
        print(
            json.dumps(
                {"error": f"{type(exc).__name__}: {exc}", "result": "fail"},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
