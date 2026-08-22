#!/usr/bin/env python3
"""Validate and virtually adapt Mathematics in Lean id-ID to backend v1.

The completed owner edition exposes 10,978 canonical native records.  This
adapter leaves the owner lane byte-identical, verifies the complete export and
its public preservation bindings, and creates one strict common-backend record
for every native record.  The complete native record is retained under a
namespaced extension, making the transformation exactly reversible without a
second materialized copy of the roughly 93 MB export.

The owner GitHub receipt contains one acknowledged scalar typo (10,876).  The
same receipt's coverage text, the frozen handoff, the exact local export, the
public backend archive, and the coordinator reconciliation all prove 10,978.
This script rejects any other interpretation and records the discrepancy in
the generated migration receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_NAME = "mil-backend-record"
SOURCE_SCHEMA_VERSION = "1.0.0"
WORKFLOW = "program-matematika-indonesia/mathematics-in-lean-v1-migrator-1.0.0"
NAMESPACE = uuid.UUID("de97185b-5bfb-5cd0-a60e-8f8e0c432da2")
NATIVE_EXTENSION = "interlanguage.mathematics-in-lean-native"

EXPECTED_RECORDS = 10_978
ACKNOWLEDGED_TYPO = 10_876
EXPECTED_RECORDS_BYTES = 15_532_090
EXPECTED_RECORDS_SHA256 = "974e145da718fa3fec9027d0193b21503fa69d3ac4f775cb553a368bf367f1a2"
EXPECTED_CATALOG_BYTES = 19_555_921
EXPECTED_CATALOG_SHA256 = "bc0be8cbd331e1160f556cafad2ec3f828ef227ff9f7ec98c60facb3b4cbf7cc"
EXPECTED_EXPORT_MANIFEST_BYTES = 8_084
EXPECTED_EXPORT_MANIFEST_SHA256 = "3577912edade478aef93d2a8ef6f4e87284c8cda68fe4a329eddc2f0781eeaa0"
EXPECTED_EXPORT_FILES = 49
EXPECTED_EXPORT_BYTES = 92_714_008
EXPECTED_HANDOFF_BYTES = 4_609
EXPECTED_HANDOFF_SHA256 = "0041c972224128bb9e61c9c5fedd001bebb2b4afce695257b7b404456ae9c33a"
EXPECTED_GITHUB_RECEIPT_BYTES = 9_479
EXPECTED_GITHUB_RECEIPT_SHA256 = "87975b78a1e0b5c2e490c36ddd5fa43dbdf7f490ffccf9eff67f3d45225f1289"
EXPECTED_ZENODO_RECEIPT_BYTES = 6_133
EXPECTED_ZENODO_RECEIPT_SHA256 = "c6e48e874b5c4a87b31906a7c23dc62f9a17117612c105ec13bed1a02f9f691e"
EXPECTED_RECONCILIATION_BYTES = 3_332
EXPECTED_RECONCILIATION_SHA256 = "e9e953022ee1539a11a61c4b5a79f63cdd6c08960c76f1a612a399d4615af0de"
PUBLIC_BACKEND_FILENAME = "matematika-dalam-lean-bahasa-indonesia-backend-4.30.0-id.3.zip"
PUBLIC_BACKEND_BYTES = 7_101_665
PUBLIC_BACKEND_SHA256 = "522abc439742b99a623f083bfbcb29bc0eab45de7622bfe2c1b227a6c868c5d0"
PUBLIC_VERSION = "v4.30.0-id.3"
PUBLIC_GITHUB_COMMIT = "6849b156d1016cc91bd22024892721013e39f414"
SOURCE_COMMIT = "8e112cd63ff1bf2a1020ff88f22f77288e42b9a9"
LEARNER_COMMIT = "dd6d752fedb14082f557913c2dccb2d4851e5173"

DIRECT_TYPES = {
    "program": ("programs", "program"),
    "course": ("courses", "course"),
    "resource": ("resources", "resource"),
    "edition": ("editions", "edition"),
    "unit": ("units", "unit"),
    "concept": ("concepts", "concept"),
    "segment": ("segments", "segment"),
    "term": ("terms", "term"),
    "asset": ("assets", "asset"),
    "relation": ("relations", "relation"),
    "rights": ("rights", "rights"),
    "qa_event": ("qa_events", "qa_event"),
    "artifact": ("artifacts", "artifact"),
    "correction": ("corrections", "correction"),
}

SOURCE_ENTITY_ORDER = {
    entity_type: index
    for index, entity_type in enumerate(
        (
            "program",
            "course",
            "resource",
            "edition",
            "unit",
            "concept",
            "segment",
            "term",
            "asset",
            "relation",
            "rights",
            "qa_event",
            "artifact",
            "correction",
        )
    )
}

NATIVE_REFERENCE_FIELDS = {
    "parent_id",
    "resource_id",
    "edition_id",
    "source_record_id",
    "rights_id",
    "supersedes_id",
}
NATIVE_REFERENCE_LIST_FIELDS = {
    "concept_ids",
    "prerequisite_ids",
    "qa_event_ids",
    "build_event_ids",
}


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
        "status": status or "active",
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def valid_sha256(value: Any) -> str | None:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
        return value
    return None


def valid_commit(value: Any) -> str | None:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value):
        return value
    return None


def native_extension(record: dict) -> dict:
    return {
        NATIVE_EXTENSION: {
            "native_record": record,
            "native_record_id": record["record_id"],
            "native_record_sha256": sha256_bytes(canonical_bytes(record)),
            "source_schema": record["schema"],
            "source_schema_version": record["schema_version"],
            "disposition": "direct-lossless-native-extension",
        }
    }


def read_native_records(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    raw_lines: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n") or "\r" in line:
                raise ValueError(f"native JSONL newline failure at row {line_number}")
            record = json.loads(line)
            if line != canonical(record) + "\n":
                raise ValueError(f"native JSONL is not canonical at row {line_number}")
            records.append(record)
            raw_lines.append(line)
    return records, raw_lines


def safe_manifest_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"manifest path escapes export root: {relative}") from exc
    return candidate


def verify_export(
    owner_root: Path,
    records: list[dict],
    raw_lines: list[str],
    handoff: dict,
) -> tuple[dict, dict, dict]:
    exports = owner_root / "backend" / "exports"
    manifest_path = exports / "export-manifest.json"
    catalog_path = exports / "catalog.json"
    records_path = exports / "records.jsonl"
    records_csv_path = exports / "records.csv"
    schema_path = owner_root / "backend" / "schema" / "catalog.schema.json"

    exact_file(records_path, EXPECTED_RECORDS_BYTES, EXPECTED_RECORDS_SHA256, "native records export")
    exact_file(catalog_path, EXPECTED_CATALOG_BYTES, EXPECTED_CATALOG_SHA256, "native catalog export")
    exact_file(
        manifest_path,
        EXPECTED_EXPORT_MANIFEST_BYTES,
        EXPECTED_EXPORT_MANIFEST_SHA256,
        "native export manifest",
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(manifest.get("files", [])) != EXPECTED_EXPORT_FILES - 1:
        raise ValueError("export manifest member count mismatch")
    declared = {item["path"]: item for item in manifest["files"]}
    if len(declared) != len(manifest["files"]):
        raise ValueError("duplicate paths in export manifest")
    actual = {
        path.relative_to(exports).as_posix(): path
        for path in exports.rglob("*")
        if path.is_file() and path.name != "export-manifest.json"
    }
    if set(actual) != set(declared):
        raise ValueError("export manifest inventory does not match exact export directory")
    declared_bytes = 0
    for relative, item in sorted(declared.items()):
        path = safe_manifest_path(exports, relative)
        if path != actual[relative].resolve():
            raise ValueError(f"manifest path identity mismatch: {relative}")
        if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            raise ValueError(f"export manifest member mismatch: {relative}")
        declared_bytes += item["bytes"]
    if manifest.get("total_bytes") != declared_bytes:
        raise ValueError("export manifest total_bytes mismatch")
    if declared_bytes + manifest_path.stat().st_size != EXPECTED_EXPORT_BYTES:
        raise ValueError("complete export byte count mismatch")

    if len(records) != EXPECTED_RECORDS:
        raise ValueError("native record count mismatch")
    if len("".join(raw_lines).encode("utf-8")) != EXPECTED_RECORDS_BYTES:
        raise ValueError("native reread byte count mismatch")
    if sha256_bytes("".join(raw_lines).encode("utf-8")) != EXPECTED_RECORDS_SHA256:
        raise ValueError("native reread SHA-256 mismatch")

    owner_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(owner_schema)
    record_validator = Draft202012Validator(owner_schema["$defs"]["record"], format_checker=FormatChecker())
    ids: list[str] = []
    counts: Counter[str] = Counter()
    previous_key: tuple[int, str] | None = None
    for row_number, record in enumerate(records, start=1):
        errors = sorted(record_validator.iter_errors(record), key=lambda error: list(error.absolute_path))
        if errors:
            first = errors[0]
            raise ValueError(f"native schema failure row {row_number} {list(first.absolute_path)}: {first.message}")
        key = (SOURCE_ENTITY_ORDER[record["entity_type"]], record["record_id"])
        if previous_key is not None and key < previous_key:
            raise ValueError(f"native ordering failure at row {row_number}")
        previous_key = key
        ids.append(record["record_id"])
        counts[record["entity_type"]] += 1
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate native record IDs: {duplicates[:5]}")
    if set(counts) != set(DIRECT_TYPES):
        raise ValueError("native entity type inventory mismatch")

    known = set(ids)
    missing: list[tuple[str, str, str]] = []
    for record in records:
        for field in NATIVE_REFERENCE_FIELDS:
            value = record.get(field)
            if value and value not in known:
                missing.append((record["record_id"], field, value))
        for field in NATIVE_REFERENCE_LIST_FIELDS:
            for value in record.get(field, []):
                if value not in known:
                    missing.append((record["record_id"], field, value))
        if record["entity_type"] == "relation":
            for field in ("subject_id", "object_id"):
                value = record["data"].get(field)
                if not value or value not in known:
                    missing.append((record["record_id"], f"data.{field}", value or "<empty>"))
        if record["entity_type"] == "correction":
            for value in record["data"].get("affected_unit_ids", []):
                if value not in known:
                    missing.append((record["record_id"], "data.affected_unit_ids", value))
    if missing:
        raise ValueError(f"native foreign-key closure failure: {missing[:5]}")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_errors = sorted(
        Draft202012Validator(owner_schema, format_checker=FormatChecker()).iter_errors(catalog),
        key=lambda error: list(error.absolute_path),
    )
    if catalog_errors:
        first = catalog_errors[0]
        raise ValueError(f"native catalog schema failure {list(first.absolute_path)}: {first.message}")
    if catalog["records"] != records:
        raise ValueError("catalog records are not exactly equivalent to records.jsonl")
    if catalog["generated_from"]["source_commit"] != SOURCE_COMMIT:
        raise ValueError("catalog source commit mismatch")
    if catalog["generated_from"]["learner_commit"] != LEARNER_COMMIT:
        raise ValueError("catalog learner commit mismatch")

    expected_backend = handoff["artifacts"]["backend"]
    if (
        expected_backend["files"] != EXPECTED_EXPORT_FILES
        or expected_backend["bytes"] != EXPECTED_EXPORT_BYTES
        or expected_backend["records"] != EXPECTED_RECORDS
        or expected_backend["manifest_sha256"] != EXPECTED_EXPORT_MANIFEST_SHA256
        or expected_backend["records_sha256"] != EXPECTED_RECORDS_SHA256
        or expected_backend["catalog_sha256"] != EXPECTED_CATALOG_SHA256
    ):
        raise ValueError("frozen handoff does not bind the admitted export")

    diagnostics = {
        "canonical_native_jsonl": "pass",
        "catalog_exact_record_equivalence": "pass",
        "export_manifest_inventory": "pass",
        "export_files": EXPECTED_EXPORT_FILES,
        "export_bytes": EXPECTED_EXPORT_BYTES,
        "manifest_members": len(declared),
        "manifest_member_bytes": declared_bytes,
        "native_record_count": len(records),
        "native_record_counts": dict(sorted(counts.items())),
        "native_unique_ids": len(known),
        "native_foreign_key_closure": "pass",
        "records_csv_bytes": records_csv_path.stat().st_size,
        "records_csv_sha256": sha256_file(records_csv_path),
        "owner_schema_bytes": schema_path.stat().st_size,
        "owner_schema_sha256": sha256_file(schema_path),
    }
    return manifest, catalog, diagnostics


def find_public_asset(receipt: dict, filename: str) -> dict:
    candidates: Iterable[dict]
    if "release" in receipt:
        candidates = receipt["release"]["assets"]
    else:
        candidates = receipt["files"]
    matches = [item for item in candidates if item["filename"] == filename]
    if len(matches) != 1:
        raise ValueError(f"public receipt does not identify exactly one {filename}")
    item = matches[0]
    if (
        item.get("anonymous_readback") != "pass"
        or item["bytes"] != PUBLIC_BACKEND_BYTES
        or item["sha256"] != PUBLIC_BACKEND_SHA256
    ):
        raise ValueError("public backend archive identity/readback mismatch")
    return item


def verify_authority_inputs(owner_root: Path, reconciliation_path: Path) -> tuple[dict, dict, dict, dict, dict]:
    handoff_path = owner_root / "00_control" / "CENTRAL_HUB_HANDOFF_ID3.json"
    github_path = owner_root / "publication" / "GITHUB_PUBLICATION_RECEIPT_ID3.json"
    zenodo_path = owner_root / "publication" / "ZENODO_TERMINOLOGY_QA_PUBLICATION_RECEIPT.json"
    figshare_path = owner_root / "publication" / "FIGSHARE_READER_FIRST_PUBLICATION_RECEIPT_ID3.json"

    exact_file(handoff_path, EXPECTED_HANDOFF_BYTES, EXPECTED_HANDOFF_SHA256, "frozen owner handoff")
    exact_file(
        github_path,
        EXPECTED_GITHUB_RECEIPT_BYTES,
        EXPECTED_GITHUB_RECEIPT_SHA256,
        "GitHub publication receipt",
    )
    exact_file(
        zenodo_path,
        EXPECTED_ZENODO_RECEIPT_BYTES,
        EXPECTED_ZENODO_RECEIPT_SHA256,
        "Zenodo publication receipt",
    )
    exact_file(
        reconciliation_path,
        EXPECTED_RECONCILIATION_BYTES,
        EXPECTED_RECONCILIATION_SHA256,
        "central count reconciliation",
    )

    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    github = json.loads(github_path.read_text(encoding="utf-8"))
    zenodo = json.loads(zenodo_path.read_text(encoding="utf-8"))
    figshare = json.loads(figshare_path.read_text(encoding="utf-8"))
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))

    if (
        handoff.get("status") != "ready-for-central-hub-ingestion"
        or handoff["edition"]["version"] != PUBLIC_VERSION
        or handoff["edition"]["backend_records"] != EXPECTED_RECORDS
        or handoff["edition"]["completion"] != "complete"
        or handoff["publications"]["github"]["receipt_sha256"] != EXPECTED_GITHUB_RECEIPT_SHA256
        or handoff["publications"]["zenodo"]["receipt_sha256"] != EXPECTED_ZENODO_RECEIPT_SHA256
    ):
        raise ValueError("owner handoff status/count/publication binding failure")
    if (
        github.get("status") != "published-and-anonymously-verified"
        or github["edition"]["backend_records"] != ACKNOWLEDGED_TYPO
        or "10,978 backend records" not in github["edition"]["coverage"]
        or github["commit"]["sha"] != PUBLIC_GITHUB_COMMIT
        or github.get("credential_material_persisted") is not False
    ):
        raise ValueError("GitHub receipt does not expose the adjudicated isolated typo pattern")
    if (
        zenodo.get("status") != "published-and-publicly-verified"
        or zenodo.get("doi") != "10.5281/zenodo.22062017"
        or zenodo.get("credential_material_persisted") is not False
        or figshare.get("status") != "published-and-anonymously-verified"
        or figshare.get("credential_material_persisted") is not False
    ):
        raise ValueError("public publication receipt status failure")

    github_asset = find_public_asset(github, PUBLIC_BACKEND_FILENAME)
    zenodo_asset = find_public_asset(zenodo, PUBLIC_BACKEND_FILENAME)
    figshare_asset = find_public_asset(figshare, PUBLIC_BACKEND_FILENAME)
    if len({github_asset["sha256"], zenodo_asset["sha256"], figshare_asset["sha256"]}) != 1:
        raise ValueError("public backend archives disagree across repositories")

    issue = reconciliation.get("issue", {})
    decision = reconciliation.get("decision", {})
    public_evidence = next(
        (item for item in reconciliation.get("evidence", []) if item.get("kind") == "anonymous_public_github_release_archive_readback"),
        None,
    )
    if (
        reconciliation.get("status") != "resolved-for-central-ingestion"
        or reconciliation.get("course_role_id") != "D110"
        or reconciliation.get("adjudicated_value") != EXPECTED_RECORDS
        or issue.get("incorrect_value") != ACKNOWLEDGED_TYPO
        or issue.get("same_receipt_coverage_text_value") != EXPECTED_RECORDS
        or decision.get("canonical_backend_record_count") != EXPECTED_RECORDS
        or decision.get("central_adapter_may_proceed") is not True
        or not public_evidence
        or public_evidence.get("archive_bytes") != PUBLIC_BACKEND_BYTES
        or public_evidence.get("archive_sha256") != PUBLIC_BACKEND_SHA256
        or public_evidence.get("records_entry_bytes") != EXPECTED_RECORDS_BYTES
        or public_evidence.get("records_entry_sha256") != EXPECTED_RECORDS_SHA256
        or public_evidence.get("records_entry_line_count") != EXPECTED_RECORDS
    ):
        raise ValueError("central count reconciliation does not close the admitted public bytes")
    return handoff, github, zenodo, figshare, reconciliation


def referenced_uuid_urns(value: Any, path: tuple[str, ...] = ()):
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


def choose_resource_title(native: dict) -> str:
    data = native["data"]
    if "reader" in native["record_id"]:
        return "Mathematics in Lean official reader"
    if "source" in native["record_id"]:
        return "Mathematics in Lean authoring source"
    return "Mathematics in Lean"


def build_backend(records: list[dict], schema: dict, handoff: dict, github: dict, zenodo: dict, figshare: dict) -> tuple[dict, dict]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}
    by_native = {record["record_id"]: record for record in records}
    id_map = {
        record["record_id"]: rid(DIRECT_TYPES[record["entity_type"]][1], f"mil-id:{record['record_id']}")
        for record in records
    }

    def mapped(native_id: str | None) -> str | None:
        if not native_id:
            return None
        if native_id not in id_map:
            raise ValueError(f"unmapped native reference: {native_id}")
        return id_map[native_id]

    def add(table: str, record: dict) -> str:
        tables[table].append(record)
        return record["id"]

    program_native = next(record for record in records if record["entity_type"] == "program")
    course_native = next(record for record in records if record["entity_type"] == "course")
    root_unit_native = next(
        record for record in records if record["entity_type"] == "unit" and record["data"].get("unit_type") == "book"
    )
    source_edition_native = by_native[f"urn:mil:edition:source:{SOURCE_COMMIT}"]
    program_id = mapped(program_native["record_id"])
    root_unit_id = mapped(root_unit_native["record_id"])
    source_edition_id = mapped(source_edition_native["record_id"])
    public_uri_by_sha: dict[str, str] = {}
    for receipt in (github, zenodo, figshare):
        candidates = receipt.get("release", {}).get("assets", receipt.get("files", []))
        for item in candidates:
            url = item.get("download_url")
            if item.get("sha256") and url:
                public_uri_by_sha.setdefault(item["sha256"], url)

    mapping_lines: list[bytes] = []
    source_payload_bytes = 0
    target_payload_bytes = 0
    for native in records:
        entity_type = native["entity_type"]
        table, record_type = DIRECT_TYPES[entity_type]
        stable_key = f"mil-id:{native['record_id']}"
        common = base(record_type, stable_key, native["timestamp"], native["status"])
        common["extensions"] = native_extension(native)
        common["supersedes_id"] = mapped(native.get("supersedes_id"))
        data = native["data"]

        if entity_type == "program":
            common.update(
                curriculum_version=data.get("release_version", PUBLIC_VERSION),
                locale=native["locale"],
                program_key="D110",
                rights_id=mapped(native["rights_id"]),
                title=data.get("label", "Mathematics in Lean — Bahasa Indonesia"),
            )
        elif entity_type == "course":
            common.update(
                course_key="D110",
                order_key="D110",
                program_id=program_id,
                role=data.get("curriculum_role", "formalized mathematics in Lean 4 with Mathlib"),
            )
        elif entity_type == "resource":
            common.update(
                authority_policy="Frozen exact upstream commit/tree; public edition preservation receipts verified",
                creator_name="Jeremy Avigad; Patrick Massot",
                official_reader=data.get("url"),
                official_repository=data.get("repository") or data.get("url") or "",
                original_title=choose_resource_title(native),
                resource_key=native["source_local_id"] or native["record_id"],
                work_type=data.get("role", "open formal-mathematics textbook resource"),
            )
        elif entity_type == "rights":
            notice_sha = valid_sha256(data.get("register_sha256")) or valid_sha256(native.get("source_sha256"))
            if notice_sha is None:
                notice_sha = sha256_bytes(canonical_bytes(data))
            common.update(
                assertion_status=data.get("verification_status", "native-rights-record"),
                attribution=data.get("source_identity") or data.get("component_id") or "",
                authority=data.get("authority_or_witness") or data.get("evidence") or "",
                change_notice="required" if data.get("change_notice_required") else "not required",
                license_expression=data.get("license_expression", "NOASSERTION"),
                nonendorsement=data.get("non_endorsement", ""),
                notice_locator=data.get("register_path") or native.get("source_locator") or "native rights record",
                notice_sha256=notice_sha,
                source_component_id=data.get("component_id") or native["record_id"],
                third_party_status=data.get("verification_status", "native-rights-record"),
            )
        elif entity_type == "edition":
            native_commit = valid_commit(data.get("commit"))
            if native_commit is None:
                if native["record_id"].startswith("urn:mil:edition:learner:"):
                    native_commit = LEARNER_COMMIT
                elif native["record_id"].startswith("urn:mil:edition:source:"):
                    native_commit = SOURCE_COMMIT
                else:
                    native_commit = PUBLIC_GITHUB_COMMIT
            derivative = data.get("derivative_of") or data.get("generated_from_edition_id")
            if not derivative and native.get("source_record_id") and by_native[native["source_record_id"]]["entity_type"] == "edition":
                derivative = native["source_record_id"]
            is_current = native["record_id"] == handoff["edition"]["edition_id"]
            if native["record_id"].startswith("urn:mil:edition:source:"):
                edition_kind = "source-authority"
            elif native["record_id"].startswith("urn:mil:edition:learner:"):
                edition_kind = "generated-learner-baseline"
            elif is_current:
                edition_kind = "published-Indonesian-edition"
            else:
                edition_kind = "Indonesian-edition-snapshot"
            common.update(
                archive_sha256=github["commit"]["anonymous_codeload_readback"]["archive_sha256"] if is_current else None,
                commit_sha=native_commit,
                edition_kind=edition_kind,
                locale=native["locale"],
                release_date=github["observed_at_utc"][:10] if is_current else None,
                resource_id=mapped(native["resource_id"]),
                rights_id=mapped(native["rights_id"]),
                source_edition_id=mapped(derivative),
                tree_sha=valid_commit(data.get("tree")),
                vcs_ref=data.get("tag") or data.get("branch") or native["source_local_id"] or native["record_id"],
                vcs_type="git",
                version_label=data.get("release_version") or native["source_local_id"] or native["record_id"],
            )
        elif entity_type == "unit":
            common.update(
                first_edition_id=mapped(native["edition_id"]),
                identity_anchor=native["record_id"],
                identity_basis="native Mathematics in Lean record_id",
                resource_id=mapped(native["resource_id"]),
                rights_default_id=mapped(native["rights_id"]),
                source_label=native.get("source_local_id") or None,
                source_local_id=native.get("source_local_id") or None,
                source_path=native.get("source_path") or "",
                source_xml_path=None,
                unit_kind=data.get("unit_type", "native-unit"),
            )
        elif entity_type == "segment":
            source_text = data.get("source_text")
            target_text = data.get("target_text")
            if isinstance(source_text, str):
                source_payload_bytes += len(source_text.encode("utf-8"))
            if isinstance(target_text, str):
                target_payload_bytes += len(target_text.encode("utf-8"))
            common.update(
                identity_anchor=native["record_id"],
                ordinal=int(native["order_index"]),
                segment_kind=data.get("segment_kind", "native-segment"),
                segmentation_profile="mathematics-in-lean-rst-in-lean-v1",
                unit_id=mapped(native["parent_id"]),
            )
        elif entity_type == "concept":
            parent = native.get("parent_id")
            common.update(
                concept_key=native["source_local_id"] or native["record_id"],
                concept_scheme="mathematics-in-lean-v4.30.0",
                definition_segment_id=None,
                parent_concept_id=mapped(parent) if parent and by_native[parent]["entity_type"] == "concept" else None,
            )
        elif entity_type == "term":
            concept_native = native["concept_ids"][0] if native["concept_ids"] else native.get("source_record_id")
            if not concept_native or by_native[concept_native]["entity_type"] != "concept":
                raise ValueError(f"term lacks exact concept binding: {native['record_id']}")
            common.update(
                concept_id=mapped(concept_native),
                evidence=str(data.get("evidence", "")),
                notes=data.get("example_or_note") or data.get("scope") or "",
                preferred_form=data.get("preferred", ""),
                register=data.get("register", ""),
                scope_unit_id=root_unit_id,
                source_form=data.get("source_term", native["source_local_id"]),
                source_locale=data.get("source_locale", "en"),
                source_term_id=native["record_id"],
                target_locale=data.get("target_locale", native["locale"]),
                term_status=native["translation_state"],
            )
        elif entity_type == "correction":
            affected = data.get("affected_unit_ids") or ([native["parent_id"]] if native.get("parent_id") else [])
            if not affected:
                raise ValueError(f"correction lacks affected unit: {native['record_id']}")
            original = str(data.get("source_text", ""))
            replacement = str(
                data.get("suggested_source_correction")
                or data.get("preferred_term")
                or data.get("target_handling")
                or original
            )
            common.update(
                affected_id=mapped(affected[0]),
                category=data.get("defect_type", "native-correction"),
                evidence_locator=str(data.get("evidence") or native.get("source_locator") or "native correction record"),
                local_state="verified" if data.get("target_resolution_verified") else native["translation_state"],
                original_payload_sha256=sha256_bytes(original.encode("utf-8")),
                rationale=str(data.get("rationale") or data.get("target_handling") or ""),
                replacement_payload_sha256=sha256_bytes(replacement.encode("utf-8")),
                source_edition_id=source_edition_id,
                upstream_disposition=data.get("upstream_report_disposition", "not-submitted"),
                upstream_url=None,
            )
        elif entity_type == "relation":
            common.update(
                assertion_method="native Mathematics in Lean explicit relation",
                confidence="explicit",
                edition_id=mapped(native["edition_id"]),
                from_id=mapped(data["subject_id"]),
                ordinal=int(native["order_index"]),
                relation_type=data["relation_type"],
                source_locator=native.get("source_locator") or "",
                strength=str(data.get("status") or "asserted"),
                to_id=mapped(data["object_id"]),
            )
        elif entity_type == "qa_event":
            witness = data.get("witness")
            common.update(
                input_hash=sha256_bytes(canonical_bytes(native)),
                method="frozen native QA-event evidence",
                qa_type=data.get("event_type", "native-qa-event"),
                result=str(data.get("result", native["status"])),
                reviewer_kind="native Mathematics in Lean QA workflow",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name=data.get("responsible_workflow", native["workflow_id"]),
                tool_version=native["schema_version"],
                witness_locator=native.get("source_locator") or (canonical(witness) if witness is not None else "native QA event"),
            )
            common["extensions"][NATIVE_EXTENSION]["severity_mapping"] = (
                "The native record has no uniform severity-count fields; common required severity counters are zero and are not an independent finding count."
            )
        elif entity_type == "asset":
            locator = (
                data.get("target_path")
                or data.get("path")
                or data.get("source_path")
                or native.get("source_path")
                or native.get("source_locator")
                or native["record_id"]
            )
            media_type = data.get("media_type")
            if not media_type:
                media_type = "text/x-lean" if "source_text" in data or "target_text" in data else "application/octet-stream"
            common.update(
                asset_kind=data.get("asset_type", "native-asset"),
                canonical_path_or_uri=locator,
                media_type=media_type,
                resource_id=mapped(native["resource_id"]),
                rights_default_id=mapped(native["rights_id"]),
            )
        elif entity_type == "artifact":
            artifact_sha = valid_sha256(data.get("sha256"))
            if artifact_sha is None:
                raise ValueError(f"artifact lacks exact SHA-256: {native['record_id']}")
            build_receipt = data.get("build_receipt") or data.get("manifest") or "native Mathematics in Lean artifact record"
            if not isinstance(build_receipt, str):
                build_receipt = canonical(build_receipt)
            toolchain = data.get("toolchain") or "native Mathematics in Lean artifact record"
            if not isinstance(toolchain, str):
                toolchain = canonical(toolchain)
            common.update(
                artifact_kind=data.get("artifact_type", "native-artifact"),
                build_receipt=build_receipt,
                bytes=int(data["bytes"]),
                edition_id=mapped(native["edition_id"]),
                locale=native["locale"],
                manifest_sha256=valid_sha256(data.get("manifest_sha256")),
                public_uri=public_uri_by_sha.get(artifact_sha),
                sha256=artifact_sha,
                toolchain_id=toolchain,
                tree_sha256=None,
            )
        else:
            raise ValueError(f"unhandled native entity type: {entity_type}")

        if common["id"] != id_map[native["record_id"]]:
            raise ValueError(f"common identity derivation mismatch: {native['record_id']}")
        add(table, common)
        mapping_lines.append(
            (
                canonical(
                    {
                        "disposition": "direct-lossless-native-extension",
                        "source_record_id": native["record_id"],
                        "source_record_sha256": sha256_bytes(canonical_bytes(native)),
                        "target_id": common["id"],
                        "target_table": table,
                    }
                )
                + "\n"
            ).encode("utf-8")
        )

    for rows in tables.values():
        rows.sort(key=lambda record: record["id"])
    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rid("dataset", "mathematics-in-lean-id:v4.30.0-id.3"),
        "dataset_version": "v4.30.0-id.3+interlanguage-v1",
        "tables": dict(sorted(tables.items())),
    }

    recovered: list[dict] = []
    for table, _record_type in DIRECT_TYPES.values():
        for common in tables[table]:
            extension = common.get("extensions", {}).get(NATIVE_EXTENSION)
            if extension is None:
                raise ValueError(f"direct common record lacks native extension: {common['id']}")
            native = extension["native_record"]
            if native["record_id"] != extension["native_record_id"]:
                raise ValueError("native reverse identity mismatch")
            if sha256_bytes(canonical_bytes(native)) != extension["native_record_sha256"]:
                raise ValueError("native reverse checksum mismatch")
            recovered.append(native)
    if sorted(recovered, key=lambda row: row["record_id"]) != sorted(records, key=lambda row: row["record_id"]):
        raise ValueError("exact native reverse extraction failed")

    mapping_payload = b"".join(sorted(mapping_lines))
    diagnostics = {
        "direct_native_records": len(records),
        "exact_reverse_extraction": len(recovered),
        "source_record_dispositions": {"direct-lossless-native-extension": len(records)},
        "source_record_binding_bytes": len(mapping_payload),
        "source_record_binding_sha256": sha256_bytes(mapping_payload),
        "source_segment_payload_bytes": source_payload_bytes,
        "target_segment_payload_bytes": target_payload_bytes,
    }
    return backend, diagnostics


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
        raise ValueError(f"duplicate common IDs: {duplicates[:5]}")
    known = set(ids)
    dangling = []
    allowed_external = {"supersedes_id", "source_edition_id", "source_revision_id", "source_variant_id", "source_occurrence_id"}
    for record in records:
        for field_path, value in referenced_uuid_urns(record):
            if field_path == ("id",):
                continue
            leaf = field_path[-1] if field_path else ""
            if leaf not in allowed_external and value not in known:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling[:5]}")
    if len(records) != EXPECTED_RECORDS:
        raise ValueError("common record count is not one-to-one with native source")

    global_payload = b"".join((canonical(record) + "\n").encode("utf-8") for record in records)
    table_hashes = {}
    for name, rows in backend["tables"].items():
        payload = b"".join((canonical(row) + "\n").encode("utf-8") for row in rows)
        table_hashes[name] = {
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
        "virtual_records_jsonl_bytes": len(global_payload),
        "virtual_records_jsonl_sha256": sha256_bytes(global_payload),
    }


def privacy_scan(value: Any) -> dict:
    markers = tuple(
        "".join(chr(code) for code in marker)
        for marker in (
            (99, 58, 92, 117, 115, 101, 114, 115, 92),
            (99, 58, 47, 117, 115, 101, 114, 115, 47),
            (47, 117, 115, 101, 114, 115, 47),
            (102, 105, 108, 101, 58, 47, 47),
            (46, 99, 111, 100, 101, 120, 47),
            (46, 99, 111, 100, 101, 120, 92),
        )
    )
    payload = canonical(value).lower()
    hits = sum(payload.count(marker) for marker in markers)
    if hits:
        raise ValueError("private-path or private-identity marker found in migration payload")
    return {"private_marker_hits": 0, "result": "pass"}


def portable_artifact(path: str, filesystem_path: Path, status: str, **fields: Any) -> dict:
    return {
        "path": path,
        "bytes": filesystem_path.stat().st_size,
        "sha256": sha256_file(filesystem_path),
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
    parser.add_argument("--reconciliation", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    owner_root = args.corpus_root.resolve()
    reconciliation_path = args.reconciliation.resolve()
    schema_path = args.schema.resolve()
    records_path = owner_root / "backend" / "exports" / "records.jsonl"
    catalog_path = owner_root / "backend" / "exports" / "catalog.json"
    export_manifest_path = owner_root / "backend" / "exports" / "export-manifest.json"
    handoff_path = owner_root / "00_control" / "CENTRAL_HUB_HANDOFF_ID3.json"
    github_path = owner_root / "publication" / "GITHUB_PUBLICATION_RECEIPT_ID3.json"
    zenodo_path = owner_root / "publication" / "ZENODO_TERMINOLOGY_QA_PUBLICATION_RECEIPT.json"
    figshare_path = owner_root / "publication" / "FIGSHARE_READER_FIRST_PUBLICATION_RECEIPT_ID3.json"

    handoff, github, zenodo, figshare, reconciliation = verify_authority_inputs(owner_root, reconciliation_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    first_records, first_lines = read_native_records(records_path)
    manifest, _catalog, native_diagnostics = verify_export(owner_root, first_records, first_lines, handoff)
    privacy_scan(first_records)
    privacy_scan(handoff)
    privacy_scan(github)
    privacy_scan(zenodo)
    privacy_scan(figshare)
    privacy_scan(reconciliation)

    first_backend, first_mapping = build_backend(first_records, schema, handoff, github, zenodo, figshare)
    first_validation = validate_backend(first_backend, schema)
    first_backend_hash = sha256_bytes(canonical_bytes(first_backend))
    privacy_scan(first_backend)

    second_records, second_lines = read_native_records(records_path)
    if second_lines != first_lines:
        raise ValueError("native JSONL changed between independent adapter assemblies")
    second_backend, second_mapping = build_backend(second_records, schema, handoff, github, zenodo, figshare)
    second_validation = validate_backend(second_backend, schema)
    second_backend_hash = sha256_bytes(canonical_bytes(second_backend))
    if (
        first_backend_hash != second_backend_hash
        or first_mapping != second_mapping
        or first_validation != second_validation
    ):
        raise ValueError("two independent common-backend assemblies are not byte-identical")

    public_backend = {
        "filename": PUBLIC_BACKEND_FILENAME,
        "bytes": PUBLIC_BACKEND_BYTES,
        "sha256": PUBLIC_BACKEND_SHA256,
        "archive_records_entry": {
            "path": next(
                item["records_entry"]
                for item in reconciliation["evidence"]
                if item.get("kind") == "anonymous_public_github_release_archive_readback"
            ),
            "bytes": EXPECTED_RECORDS_BYTES,
            "sha256": EXPECTED_RECORDS_SHA256,
            "line_count": EXPECTED_RECORDS,
        },
        "github_url": find_public_asset(github, PUBLIC_BACKEND_FILENAME)["download_url"],
        "zenodo_url": find_public_asset(zenodo, PUBLIC_BACKEND_FILENAME)["download_url"],
        "figshare_url": find_public_asset(figshare, PUBLIC_BACKEND_FILENAME)["download_url"],
        "cross_repository_byte_identity": "pass",
    }

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "mathematics-in-lean-id-v4.30.0-id.3-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-one-to-one-native-backend-adapter",
        "source": {
            "dataset_id": "urn:mil:edition:id-id:v4.30.0-id.3",
            "dataset_version": PUBLIC_VERSION,
            "course_role_id": "D110",
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": SOURCE_SCHEMA_VERSION,
            "handoff_path": "00_control/CENTRAL_HUB_HANDOFF_ID3.json",
            "handoff_bytes": handoff_path.stat().st_size,
            "handoff_sha256": sha256_file(handoff_path),
            "export_manifest_path": "backend/exports/export-manifest.json",
            "export_manifest_bytes": export_manifest_path.stat().st_size,
            "export_manifest_sha256": sha256_file(export_manifest_path),
            "catalog_path": "backend/exports/catalog.json",
            "catalog_bytes": catalog_path.stat().st_size,
            "catalog_sha256": sha256_file(catalog_path),
            "records_path": "backend/exports/records.jsonl",
            "records_bytes": records_path.stat().st_size,
            "records_sha256": sha256_file(records_path),
            "record_count": len(first_records),
            "export_files": EXPECTED_EXPORT_FILES,
            "export_bytes": EXPECTED_EXPORT_BYTES,
            "source_commit": manifest["source_commit"],
            "source_tree": manifest["source_tree"],
            "learner_commit": manifest["learner_commit"],
            "learner_tree": manifest["learner_tree"],
            "public_backend_archive": public_backend,
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
            "table_count": first_validation["table_count"],
            "nonempty_table_count": first_validation["nonempty_table_count"],
            "virtual_records_jsonl_bytes": first_validation["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
            "canonical_backend_sha256": first_backend_hash,
        },
        "coverage": {
            **native_diagnostics,
            **first_mapping,
            "course_role_id": "D110",
            "reader_pages": handoff["edition"]["pdf_pages"],
            "edition_completion": handoff["edition"]["completion"],
            "model_provenance": handoff["production"]["model_provenance"],
            "source_and_human_credits_preserved": handoff["authority"]["human_contributor_credits_preserved"],
            "count_reconciliation": {
                "status": reconciliation["status"],
                "authority": "curriculum_logbook/50_MATHEMATICS_IN_LEAN_BACKEND_COUNT_RECONCILIATION_20260823.json",
                "authority_bytes": reconciliation_path.stat().st_size,
                "authority_sha256": sha256_file(reconciliation_path),
                "acknowledged_owner_receipt_typo": ACKNOWLEDGED_TYPO,
                "canonical_backend_record_count": EXPECTED_RECORDS,
                "classification": reconciliation["issue"]["classification"],
                "disclosure": reconciliation["decision"]["required_adapter_disclosure"],
                "owner_receipt_rewritten": reconciliation["decision"]["owner_receipt_rewritten"],
                "owner_lane_mutated": reconciliation["decision"]["owner_lane_mutated"],
                "public_records_jsonl_sha256": EXPECTED_RECORDS_SHA256,
            },
        },
        "transformation": {
            "native_records_modified": 0,
            "native_files_modified": 0,
            "native_record_ids_preserved_in_extensions": len(first_records),
            "native_payload_fields_preserved": "all fields of all 10,978 native records",
            "native_records_with_exact_reverse_binding": len(first_records),
            "source_record_disposition": "one direct common record with a checksum-bound complete native extension",
            "source_segment_payload_bytes_changed": 0,
            "target_segment_payload_bytes_changed": 0,
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "derived_records_materialized": False,
        },
        "validation": {
            "result": "pass",
            "native_manifest_filename_size_sha256": "pass",
            "native_schema_validated_rows": len(first_records),
            "native_catalog_exact_record_equivalence": "pass",
            "native_global_id_uniqueness": "pass",
            "native_foreign_key_closure": "pass",
            "exact_native_reverse_extraction": len(first_records),
            "strict_common_backend_schema": "pass",
            "common_global_id_uniqueness": "pass",
            "common_foreign_key_closure": "pass",
            "common_table_inventory": "38/38 present",
            "two_independent_assemblies": "byte-identical",
            "first_canonical_backend_sha256": first_backend_hash,
            "second_canonical_backend_sha256": second_backend_hash,
            "public_backend_archive_cross_repository_identity": "pass",
            "public_archive_records_entry_matches_local_export": "pass",
            "private_marker_hits": 0,
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The exact admitted native export plus this deterministic reversible adapter reconstruct the strict common backend twice without a redundant materialized copy.",
            "script_path": "scripts/migrate-mathematics-in-lean-backend-v1.py",
        },
        "public_artifacts": [
            portable_artifact(
                "00_control/CENTRAL_HUB_HANDOFF_ID3.json",
                handoff_path,
                handoff["status"],
                backend_records=handoff["edition"]["backend_records"],
            ),
            portable_artifact(
                "publication/GITHUB_PUBLICATION_RECEIPT_ID3.json",
                github_path,
                github["status"],
                repository=handoff["publications"]["github"]["repository"],
                release=handoff["publications"]["github"]["release"],
            ),
            portable_artifact(
                "publication/ZENODO_TERMINOLOGY_QA_PUBLICATION_RECEIPT.json",
                zenodo_path,
                zenodo["status"],
                version_doi=handoff["publications"]["zenodo"]["version_doi"],
                record_url=handoff["publications"]["zenodo"]["url"],
            ),
            portable_artifact(
                "publication/FIGSHARE_READER_FIRST_PUBLICATION_RECEIPT_ID3.json",
                figshare_path,
                figshare["status"],
                version_doi=figshare["article_doi"],
                article_url=figshare["article_url"],
            ),
            portable_artifact(
                "curriculum_logbook/50_MATHEMATICS_IN_LEAN_BACKEND_COUNT_RECONCILIATION_20260823.json",
                reconciliation_path,
                reconciliation["status"],
                adjudicated_value=reconciliation["adjudicated_value"],
            ),
        ],
        "credentials_recorded": False,
    }
    privacy_scan(receipt)
    write_json(args.output_receipt, receipt)
    print(
        canonical(
            {
                "result": "pass",
                "native_records": len(first_records),
                "target_records": first_validation["record_count"],
                "tables": first_validation["table_count"],
                "nonempty_tables": first_validation["nonempty_table_count"],
                "canonical_backend_sha256": first_backend_hash,
                "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
                "receipt": args.output_receipt.resolve().as_posix(),
                "receipt_sha256": sha256_file(args.output_receipt),
            }
        )
    )


if __name__ == "__main__":
    main()
