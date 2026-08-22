#!/usr/bin/env python3
"""Validate and describe a zero-copy common-backend v1 view of R015.

The native Tea Time Numerical Analysis backend remains authoritative and is
never rewritten.  This program validates the complete native export, projects
it into the common v1 record model twice, and writes only a sanitized migration
receipt.  The virtual JSONL itself is deliberately not materialized.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


COMMON_NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
WORKFLOW_ID = "tea-time-common-backend-v1-adapter"
UUID5_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

TABLE_BY_RECORD_TYPE = {
    "accessibility": "accessibility",
    "alias": "aliases",
    "alignment": "alignments",
    "artifact_member": "artifact_members",
    "artifact": "artifacts",
    "asset_revision": "asset_revisions",
    "asset": "assets",
    "build_recipe": "build_recipes",
    "concept": "concepts",
    "correction_binding": "correction_bindings",
    "correction_claim": "correction_claims",
    "correction": "corrections",
    "course": "courses",
    "edition": "editions",
    "experiment": "experiments",
    "file_revision": "file_revisions",
    "file": "files",
    "interactive": "interactives",
    "module_member": "module_members",
    "module": "modules",
    "occurrence": "occurrences",
    "placeholder": "placeholders",
    "program": "programs",
    "qa_event": "qa_events",
    "relation": "relations",
    "release_snapshot": "release_snapshots",
    "resource": "resources",
    "rights": "rights",
    "rights_assignment": "rights_assignments",
    "rights_rule_member": "rights_rule_members",
    "rights_rule": "rights_rules",
    "route_member": "route_members",
    "route": "routes",
    "segment_variant": "segment_variants",
    "segment": "segments",
    "term_variant": "term_variants",
    "term": "terms",
    "unit": "units",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_identity(path: Path, relative_to: Path | None = None) -> dict[str, Any]:
    return {
        "path": path.relative_to(relative_to).as_posix() if relative_to else path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_id(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(COMMON_NAMESPACE, record_type + '|' + stable_key)}"


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return canonical_json(value)


def first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return default


def native_extension(native: dict[str, Any]) -> dict[str, Any]:
    return {"ttna.native": native}


def generated_extension(kind: str, evidence: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"kind": kind, "identity_namespace": str(COMMON_NAMESPACE)}
    if evidence is not None:
        payload["evidence"] = evidence
    return {"ttna.adapter": payload}


def common_base(
    record_type: str,
    stable_key: str,
    recorded_at: str,
    *,
    record_id: str | None = None,
    native: dict[str, Any] | None = None,
    status: str = "admitted",
    workflow_id: str = WORKFLOW_ID,
    supersedes_id: str | None = None,
) -> dict[str, Any]:
    if record_id is None:
        record_id = generated_id(record_type, stable_key)
    if not UUID5_RE.fullmatch(record_id):
        raise ValueError(f"not a UUIDv5 URN: {record_id}")
    return {
        "id": record_id,
        "record_type": record_type,
        "recorded_at": recorded_at,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": status or "admitted",
        "supersedes_id": supersedes_id if UUID5_RE.fullmatch(supersedes_id or "") else None,
        "workflow_id": workflow_id or WORKFLOW_ID,
        "extensions": native_extension(native) if native is not None else generated_extension(record_type),
    }


def get_timestamp(native: dict[str, Any], fallback: str) -> str:
    value = native.get("timestamp")
    if isinstance(value, str) and value:
        return value
    return fallback


def input_snapshot(paths: Iterable[Path], root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(set(paths), key=lambda p: p.as_posix()):
        if not path.is_file():
            raise FileNotFoundError(path)
        result[path.relative_to(root).as_posix()] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return result


def verify_native_export(
    lane_root: Path,
    native_schema_path: Path,
    lane_manifest_path: Path,
    export_manifest_path: Path,
    jsonl_path: Path,
    csv_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    native_schema = load_json(native_schema_path)
    lane_manifest = load_json(lane_manifest_path)
    export_manifest = load_json(export_manifest_path)
    raw_jsonl = jsonl_path.read_bytes()
    if raw_jsonl.startswith(b"\xef\xbb\xbf") or b"\r" in raw_jsonl:
        raise ValueError("native JSONL is not BOM-free UTF-8/LF")
    if not raw_jsonl.endswith(b"\n"):
        raise ValueError("native JSONL lacks the final LF")

    manifest_outputs = {entry["path"]: entry for entry in export_manifest["outputs"]}
    for filename, path in (("records.jsonl", jsonl_path), ("records.csv", csv_path)):
        expected = manifest_outputs[filename]
        if path.stat().st_size != expected["bytes"] or sha256_file(path) != expected["sha256"]:
            raise ValueError(f"native export identity mismatch: {filename}")
    source_manifest = export_manifest["source_manifest"]
    if (
        lane_manifest_path.stat().st_size != source_manifest["bytes"]
        or sha256_file(lane_manifest_path) != source_manifest["sha256"]
    ):
        raise ValueError("native lane manifest does not match export manifest")
    record_schema = export_manifest["record_schema"]
    if (
        native_schema_path.stat().st_size != record_schema["bytes"]
        or sha256_file(native_schema_path) != record_schema["sha256"]
    ):
        raise ValueError("native record schema does not match export manifest")

    validator = Draft202012Validator(native_schema, format_checker=FormatChecker())
    records: list[dict[str, Any]] = []
    ids: set[str] = set()
    type_counts: Counter[str] = Counter()
    raw_lines = raw_jsonl.splitlines(keepends=True)
    previous_id = ""
    for line_no, raw_line in enumerate(raw_lines, 1):
        if not raw_line.endswith(b"\n"):
            raise ValueError(f"non-LF native record at line {line_no}")
        record = json.loads(raw_line)
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        if errors:
            raise ValueError(f"native schema failure at line {line_no}: {errors[0].message}")
        expected_line = canonical_bytes(record) + b"\n"
        if expected_line != raw_line:
            raise ValueError(f"native JSONL is not canonical at line {line_no}")
        record_id = record["id"]
        if record_id in ids:
            raise ValueError(f"duplicate native ID: {record_id}")
        if record_id < previous_id:
            raise ValueError("native JSONL is not ordered by ID")
        if not UUID5_RE.fullmatch(record_id):
            raise ValueError(f"native ID is not UUIDv5: {record_id}")
        ids.add(record_id)
        previous_id = record_id
        type_counts[record["record_type"]] += 1
        records.append(record)

    if len(records) != export_manifest["total_unique_records"]:
        raise ValueError("native record count differs from export manifest")
    if dict(sorted(type_counts.items())) != dict(sorted(export_manifest["record_counts"].items())):
        raise ValueError("native record-type counts differ from export manifest")

    with csv_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(records):
        raise ValueError("native CSV record count differs from JSONL")
    for index, (row, record) in enumerate(zip(rows, records), 1):
        if row.get("id") != record["id"] or row.get("record_type") != record["record_type"]:
            raise ValueError(f"native CSV identity mismatch at row {index}")
        if canonical_json(json.loads(row["record_json"])) != canonical_json(record):
            raise ValueError(f"native CSV semantic mismatch at row {index}")

    unresolved: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, str) and value.startswith("urn:uuid:") and value not in ids:
            unresolved.add(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)

    for record in records:
        walk(record)
    if unresolved:
        raise ValueError(f"native foreign-key closure failed for {len(unresolved)} UUIDs")

    return records, {
        "record_count": len(records),
        "record_counts": dict(sorted(type_counts.items())),
        "unique_ids": len(ids),
        "unresolved_uuid_references": 0,
        "canonical_jsonl": True,
        "csv_round_trip": True,
        "lane_manifest": file_identity(lane_manifest_path, lane_root),
        "record_schema": file_identity(native_schema_path, lane_root),
        "jsonl": file_identity(jsonl_path, lane_root),
        "csv": file_identity(csv_path, lane_root),
        "export_manifest": file_identity(export_manifest_path, lane_root),
        "exporter": export_manifest.get("exporter"),
        "native_schema_id": native_schema.get("$id"),
        "lane_manifest_schema_id": lane_manifest.get("schema_id"),
    }


def verify_payload_files(
    lane_root: Path, records: list[dict[str, Any]]
) -> tuple[list[Path], dict[str, Any]]:
    input_paths: list[Path] = []
    source_files = [r for r in records if r["record_type"] == "source_file"]
    source_bytes = target_bytes = 0
    source_entries: list[dict[str, Any]] = []
    target_entries: list[dict[str, Any]] = []
    for record in source_files:
        for side in ("source", "target"):
            rel = record[f"{side}_path"]
            path = lane_root / rel
            expected_bytes = record[f"{side}_bytes"]
            expected_sha = record[f"{side}_sha256"]
            if not path.is_file():
                raise FileNotFoundError(path)
            actual_bytes = path.stat().st_size
            actual_sha = sha256_file(path)
            if actual_bytes != expected_bytes or actual_sha != expected_sha:
                raise ValueError(f"{side} file identity mismatch: {rel}")
            input_paths.append(path)
            entry = {"path": rel, "bytes": actual_bytes, "sha256": actual_sha}
            if side == "source":
                source_bytes += actual_bytes
                source_entries.append(entry)
            else:
                target_bytes += actual_bytes
                target_entries.append(entry)

    asset_version_paths = 0
    asset_version_bytes = 0
    asset_version_entries: list[dict[str, Any]] = []
    for record in (r for r in records if r["record_type"] == "asset_version"):
        rel = record.get("source_path")
        if not rel:
            raise ValueError(f"asset version lacks source_path: {record['id']}")
        path = lane_root / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        expected_bytes = record.get("source_bytes")
        expected_sha = record.get("source_sha256")
        actual_bytes = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_bytes != expected_bytes or actual_sha != expected_sha:
            raise ValueError(f"asset-version source identity mismatch: {rel}")
        input_paths.append(path)
        asset_version_paths += 1
        asset_version_bytes += actual_bytes
        asset_version_entries.append({"path": rel, "bytes": actual_bytes, "sha256": actual_sha})
        master_rel = record.get("provenance_master_path")
        if master_rel:
            master = lane_root / master_rel
            if not master.is_file():
                raise FileNotFoundError(master)
            if (
                master.stat().st_size != record.get("provenance_master_bytes")
                or sha256_file(master) != record.get("provenance_master_sha256")
            ):
                raise ValueError(f"asset provenance-master identity mismatch: {master_rel}")
            input_paths.append(master)

    artifact_entries: list[dict[str, Any]] = []
    for record in (r for r in records if r["record_type"] == "artifact"):
        path = lane_root / record["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != record["bytes"] or sha256_file(path) != record["sha256"]:
            raise ValueError(f"artifact identity mismatch: {record['path']}")
        input_paths.append(path)
        artifact_entries.append(
            {"path": record["path"], "bytes": record["bytes"], "sha256": record["sha256"]}
        )

    source_set = b"".join(canonical_bytes(item) + b"\n" for item in sorted(source_entries, key=lambda x: x["path"]))
    target_set = b"".join(canonical_bytes(item) + b"\n" for item in sorted(target_entries, key=lambda x: x["path"]))
    asset_set = b"".join(canonical_bytes(item) + b"\n" for item in sorted(asset_version_entries, key=lambda x: x["path"]))
    artifact_set = b"".join(canonical_bytes(item) + b"\n" for item in sorted(artifact_entries, key=lambda x: x["path"]))
    return input_paths, {
        "source_files": len(source_entries),
        "source_bytes": source_bytes,
        "source_identity_set_sha256": sha256_bytes(source_set),
        "target_files": len(target_entries),
        "target_bytes": target_bytes,
        "target_identity_set_sha256": sha256_bytes(target_set),
        "asset_version_files": asset_version_paths,
        "asset_version_bytes": asset_version_bytes,
        "asset_version_identity_set_sha256": sha256_bytes(asset_set),
        "artifacts": len(artifact_entries),
        "artifact_identity_set_sha256": sha256_bytes(artifact_set),
        "changed_source_or_target_files": 0,
    }


def find_primary_rights(records: list[dict[str, Any]]) -> str:
    for record in records:
        if record["record_type"] == "rights" and record.get("spdx_expression") == "CC-BY-SA-4.0":
            return record["id"]
    raise ValueError("no primary CC-BY-SA-4.0 rights record")


def byte_offsets(path: Path, locator: dict[str, Any]) -> tuple[int, int]:
    lines = path.read_bytes().splitlines(keepends=True)
    start_line = int(locator.get("start_line", locator.get("line", 1)))
    end_line = int(locator.get("end_line", start_line))
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise ValueError(f"invalid line locator for {path.name}: {start_line}-{end_line}")
    return sum(map(len, lines[: start_line - 1])), sum(map(len, lines[:end_line]))


def source_profile(
    lane_root: Path,
    source_file: dict[str, Any],
    file_revision_id: str,
    path_key: str,
    locator: dict[str, Any],
    protected_tokens: list[dict[str, Any]],
    ert_sha256: str | None,
) -> dict[str, Any]:
    rel = source_file[path_key]
    if rel.lower().endswith(".tex"):
        start, end = byte_offsets(lane_root / rel, locator)
        return {
            "format_profile": "latex",
            "profile_version": "1.0.0",
            "authority_file_revision_id": file_revision_id,
            "authority_path": rel,
            "identity_strategy": "source_order",
            "active_source_path": rel,
            "include_stack": [],
            "macro_context_sha256": None,
            "conditional_state": "unknown",
            "environment": locator.get("tex_context"),
            "label": None,
            "references": [],
            "external_documents": [],
            "aux_dependencies": [],
            "includegraphics_resolution": None,
            "toolchain_dependencies": [],
            "raw_start_byte": start,
            "raw_end_byte": end,
            "raw_slice_sha256": sha256_bytes((lane_root / rel).read_bytes()[start:end]),
        }
    return {
        "format_profile": "lyx",
        "profile_version": "1.0.0",
        "authority_file_revision_id": file_revision_id,
        "authority_path": rel,
        "identity_strategy": "source_order",
        "layout": str(locator.get("layout", "unknown")),
        "layout_ordinal": int(locator.get("layout_ordinal", 0)),
        "inset_ordinal": locator.get("ert_ordinal"),
        "protected_token_sha256": [
            item["sha256"] for item in protected_tokens if SHA256_RE.fullmatch(item.get("sha256", ""))
        ],
        "ert_sha256": ert_sha256 if SHA256_RE.fullmatch(ert_sha256 or "") else None,
        "formula_sha256": None,
    }


def clean_public_boundary(
    lane_root: Path,
    records: list[dict[str, Any]],
    lane_manifest_path: Path,
    current_state_path: Path,
    current_cursor_path: Path,
    publication_state_path: Path,
    publication_receipt_path: Path,
) -> dict[str, Any]:
    current_state = load_json(current_state_path)
    current_cursor = load_json(current_cursor_path)
    publication_state = load_json(publication_state_path)
    publication_receipt = load_json(publication_receipt_path)
    manifest_sha = sha256_file(lane_manifest_path)
    final_artifacts = [
        r for r in records if r["record_type"] == "artifact" and r.get("status") == "release_final"
    ]
    if len(final_artifacts) != 1:
        raise ValueError("expected exactly one native release_final artifact")
    final_artifact = final_artifacts[0]
    final_path = lane_root / final_artifact["path"]
    final_sha = sha256_file(final_path)

    failures: list[str] = []
    if current_state.get("backend", {}).get("manifest_sha256") != manifest_sha:
        failures.append("CURRENT_STATE backend manifest")
    if current_cursor.get("current_backend_manifest_sha256") != manifest_sha:
        failures.append("CURRENT_CURSOR backend manifest")
    if current_state.get("build", {}).get("indonesian_candidate", {}).get("sha256") != final_sha:
        failures.append("CURRENT_STATE final PDF")
    if current_cursor.get("current_pdf_sha256") != final_sha:
        failures.append("CURRENT_CURSOR final PDF")
    receipt_sha = sha256_file(publication_receipt_path)
    if current_state.get("publication", {}).get("publication_receipt_sha256") != receipt_sha:
        failures.append("CURRENT_STATE publication receipt")
    if publication_state.get("publication_receipt_sha256") != receipt_sha:
        failures.append("PUBLICATION_STATE publication receipt")
    if not current_state.get("publication", {}).get("published") or not publication_state.get("published"):
        failures.append("public completion state")

    zenodo = publication_receipt.get("zenodo", {})
    github = publication_receipt.get("github", {})
    zenodo_hashes = {entry.get("sha256") for entry in zenodo.get("files", [])}
    github_hashes = {
        entry.get("sha256") for entry in github.get("github_release", {}).get("assets", [])
    }
    if final_sha not in zenodo_hashes:
        failures.append("Zenodo final PDF readback")
    if final_sha not in github_hashes:
        failures.append("GitHub final PDF readback")
    if "anonymously_verified" not in str(zenodo.get("status", "")):
        failures.append("Zenodo anonymous verification")
    if "anonymously_verified" not in str(github.get("status", "")):
        failures.append("GitHub anonymous verification")
    if failures:
        raise RuntimeError(
            "migration timing gate is not clean; pending fields: " + ", ".join(failures)
        )

    return {
        "recorded_at": publication_receipt.get("last_verified_at")
        or publication_receipt.get("recorded_at"),
        "version": publication_receipt["release"]["version"],
        "tag": publication_receipt["release"]["tag"],
        "release_date": str(zenodo.get("published_at", ""))[:10] or None,
        "zenodo": zenodo,
        "github": github,
        "publication_state": publication_state,
        "current_state": current_state,
        "current_cursor": current_cursor,
        "final_artifact": final_artifact,
        "publication_receipt_sha256": receipt_sha,
    }


def build_common_dataset(
    lane_root: Path,
    records: list[dict[str, Any]],
    common_schema: dict[str, Any],
    profile_schema: dict[str, Any],
    boundary: dict[str, Any],
    lane_manifest_sha: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    recorded_at = boundary["recorded_at"]
    if not isinstance(recorded_at, str) or not recorded_at:
        raise ValueError("public receipt has no deterministic recorded_at")
    version = boundary["version"]
    by_id = {r["id"]: r for r in records}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["record_type"]].append(record)
    edition = grouped["edition"][0]
    resource = grouped["resource"][0]
    course = grouped["course"][0]
    program = grouped["program"][0]
    edition_id = edition["id"]
    resource_id = resource["id"]
    primary_rights_id = find_primary_rights(records)
    source_files = {r["id"]: r for r in grouped["source_file"]}
    segments = {r["id"]: r for r in grouped["segment"]}

    all_records: list[dict[str, Any]] = []
    native_map: dict[str, str] = {}
    rights_requests: set[tuple[str, str, str]] = set()

    def add(record: dict[str, Any], native_id: str | None = None) -> dict[str, Any]:
        all_records.append(record)
        if native_id is not None:
            if native_id in native_map:
                raise ValueError(f"native record mapped twice: {native_id}")
            native_map[native_id] = record["id"]
        return record

    def request_rights(target_id: str, ids: Iterable[str], role: str) -> None:
        for rights_id in ids:
            if UUID5_RE.fullmatch(rights_id or ""):
                rights_requests.add((target_id, rights_id, role))

    public_commit = boundary["github"].get("public_main_commit_at_release") or boundary["github"].get(
        "release_commit"
    )
    public_tag = boundary["tag"]
    source_zip = next(
        (
            item
            for item in boundary["zenodo"].get("files", [])
            if str(item.get("filename", "")).lower().endswith("source-backend.zip")
        ),
        None,
    )
    archive_sha = source_zip.get("sha256") if source_zip else None

    # Native authority records.
    for native in grouped["resource"]:
        base = common_base(
            "resource",
            f"ttna:native:resource:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            authority_policy="official repository pinned by commit/tree/archive evidence",
            creator_name=native.get("author", ""),
            official_reader=boundary["current_state"].get("upstream", {}).get("site"),
            official_repository=native.get("authority_url", ""),
            original_title=native.get("title", ""),
            resource_key=native.get("resource_local_id", ""),
            work_type="open_textbook",
        )
        add(base, native["id"])

    for native in grouped["rights"]:
        authority_rel = native.get("authority_path", "")
        authority_path = lane_root / authority_rel
        if not authority_path.is_file():
            raise FileNotFoundError(authority_path)
        base = common_base(
            "rights",
            f"ttna:native:rights:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            assertion_status=first_nonempty(native.get("maintenance_status"), default="verified_from_authority_file"),
            attribution=native.get("attribution", ""),
            authority=authority_rel,
            change_notice="required" if native.get("modification_notice_required") else "not_declared",
            license_expression=native.get("spdx_expression", ""),
            nonendorsement="not_declared",
            notice_locator=authority_rel,
            notice_sha256=sha256_file(authority_path),
            source_component_id=first_nonempty(native.get("scope"), default=native["id"]),
            third_party_status=(
                "source_work_component"
                if native.get("spdx_expression") in {"CC-BY-SA-4.0", "GPL-3.0-or-later"}
                else "third_party_component"
            ),
        )
        add(base, native["id"])

    for native in grouped["edition"]:
        base = common_base(
            "edition",
            f"ttna:native:edition:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status="public",
        )
        base.update(
            archive_sha256=archive_sha,
            commit_sha=public_commit,
            edition_kind="Indonesian translation and adaptation",
            locale=native.get("target_locale", "id-ID"),
            release_date=boundary["release_date"],
            resource_id=native["resource_id"],
            rights_id=primary_rights_id,
            source_edition_id=None,
            tree_sha=None,
            vcs_ref=public_tag,
            vcs_type="git",
            version_label=version,
        )
        add(base, native["id"])
        request_rights(base["id"], [primary_rights_id], "edition_default")

    for native in grouped["program"]:
        base = common_base(
            "program",
            f"ttna:native:program:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "active"),
            workflow_id=native.get("responsible_workflow", WORKFLOW_ID),
            supersedes_id=native.get("supersession_pointer"),
        )
        base.update(
            curriculum_version=first_nonempty(native.get("curriculum_version"), default="unknown"),
            locale=native.get("locale", "id-ID"),
            program_key=first_nonempty(native.get("program_local_id"), default="unknown:r015-envelope"),
            rights_id=primary_rights_id,
            title=first_nonempty(native.get("title"), default=""),
        )
        add(base, native["id"])
        request_rights(base["id"], [primary_rights_id], "program_default")

    for native in grouped["course"]:
        base = common_base(
            "course",
            f"ttna:native:course:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "active"),
            workflow_id=native.get("responsible_workflow", WORKFLOW_ID),
            supersedes_id=native.get("supersession_pointer"),
        )
        base.update(
            course_key=native.get("course_local_id", ""),
            order_key=native.get("course_local_id", ""),
            program_id=native["program_id"],
            role=first_nonempty(native.get("curriculum_role"), default="unknown_not_present_in_native_evidence"),
            title=native.get("title"),
            prerequisite_course_keys=[],
            curriculum_source_locator=as_text(native.get("evidence")),
        )
        add(base, native["id"])

    # Each bilingual native source-file record becomes its preserved source
    # revision plus deterministic source/target file identities and target revision.
    source_file_base_ids: dict[str, str] = {}
    target_file_base_ids: dict[str, str] = {}
    target_revision_ids: dict[str, str] = {}
    for native in grouped["source_file"]:
        source_key = f"ttna:file:source:{native['source_path']}"
        target_key = f"ttna:file:target:{native['target_path']}"
        source_file_id = generated_id("file", source_key)
        target_file_id = generated_id("file", target_key)
        target_revision_key = f"ttna:file-revision:target:{native['id']}"
        target_revision_id = generated_id("file_revision", target_revision_key)
        source_file_base_ids[native["id"]] = source_file_id
        target_file_base_ids[native["id"]] = target_file_id
        target_revision_ids[native["id"]] = target_revision_id
        media = "text/x-tex" if native["source_path"].lower().endswith(".tex") else "application/x-lyx"
        parse_mode = "latex" if media == "text/x-tex" else "lyx"
        right_ids = native.get("rights_ids") or [native.get("rights_id")]

        source_file_record = common_base("file", source_key, recorded_at, record_id=source_file_id)
        source_file_record["extensions"] = generated_extension(
            "source_file_identity", {"native_source_file_id": native["id"]}
        )
        source_file_record.update(
            canonical_path=native["source_path"],
            media_type=media,
            parse_mode=parse_mode,
            resource_id=resource_id,
            role="source_" + native.get("role", "file"),
        )
        add(source_file_record)
        request_rights(source_file_id, right_ids, "source_file")

        target_file_record = common_base("file", target_key, recorded_at, record_id=target_file_id)
        target_file_record["extensions"] = generated_extension(
            "target_file_identity", {"native_source_file_id": native["id"]}
        )
        target_file_record.update(
            canonical_path=native["target_path"],
            media_type=media,
            parse_mode=parse_mode,
            resource_id=resource_id,
            role="target_" + native.get("role", "file"),
        )
        add(target_file_record)
        request_rights(target_file_id, right_ids, "target_file")

        source_revision = common_base(
            "file_revision",
            f"ttna:native:source-file:{native['id']}",
            recorded_at,
            record_id=native["id"],
            native=native,
        )
        source_revision.update(
            actual_path=native["source_path"],
            bytes=native["source_bytes"],
            edition_id=native["edition_id"],
            file_id=source_file_id,
            generated=False,
            git_blob_sha1=None,
            sha256=native["source_sha256"],
            source_revision_id=None,
        )
        add(source_revision, native["id"])
        request_rights(source_revision["id"], right_ids, "source_file_revision")

        target_revision = common_base(
            "file_revision", target_revision_key, recorded_at, record_id=target_revision_id
        )
        target_revision["extensions"] = generated_extension(
            "target_file_revision", {"native_source_file_id": native["id"]}
        )
        target_revision.update(
            actual_path=native["target_path"],
            bytes=native["target_bytes"],
            edition_id=native["edition_id"],
            file_id=target_file_id,
            generated=True,
            git_blob_sha1=None,
            sha256=native["target_sha256"],
            source_revision_id=native["id"],
        )
        add(target_revision)
        request_rights(target_revision_id, right_ids, "target_file_revision")

    # Native units plus one explicit lexical-scope unit required by common terms.
    for native in grouped["unit"]:
        source_file = source_files[native["source_file_id"]]
        right_ids = native.get("rights_ids") or [native.get("rights_id")]
        base = common_base(
            "unit",
            f"ttna:native:unit:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            first_edition_id=native["edition_id"],
            identity_anchor=first_nonempty(native.get("source_local_id"), default=native["id"]),
            identity_basis="native source-local identity and declared source order",
            resource_id=resource_id,
            rights_default_id=next((x for x in right_ids if x), primary_rights_id),
            source_label=native.get("source_title"),
            source_local_id=native.get("source_local_id"),
            source_path=source_file["source_path"],
            source_xml_path=None,
            unit_kind=native.get("kind", "unit"),
        )
        add(base, native["id"])
        request_rights(base["id"], right_ids, "unit")

    lexical_scope_key = "ttna:unit:terminology-scope"
    lexical_scope_id = generated_id("unit", lexical_scope_key)
    lexical_scope = common_base("unit", lexical_scope_key, recorded_at, record_id=lexical_scope_id)
    lexical_scope["extensions"] = generated_extension(
        "terminology_scope", {"authority_path": "00_control/TERMINOLOGY.csv"}
    )
    lexical_scope.update(
        first_edition_id=edition_id,
        identity_anchor="00_control/TERMINOLOGY.csv",
        identity_basis="adapter scope for native global terminology records",
        resource_id=resource_id,
        rights_default_id=primary_rights_id,
        source_label="terminology scope",
        source_local_id="ttna.terminology",
        source_path="00_control/TERMINOLOGY.csv",
        source_xml_path=None,
        unit_kind="terminology_scope",
    )
    add(lexical_scope)
    request_rights(lexical_scope_id, [primary_rights_id], "terminology_scope")

    # Locale-neutral segments and separate source/target variants.
    source_variant_ids: dict[str, str] = {}
    for native in grouped["segment"]:
        source_file = source_files[native["source_file_id"]]
        profile = source_profile(
            lane_root,
            source_file,
            native["source_file_id"],
            "source_path",
            native.get("source_locator", {}),
            native.get("protected_tokens", []),
            native.get("source_ert_sha256"),
        )
        base = common_base(
            "segment",
            f"ttna:native:segment:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base["extensions"]["interlanguage.source-profile"] = profile
        base.update(
            identity_anchor=canonical_json(
                {
                    "source_file_id": native["source_file_id"],
                    "source_locator": native.get("source_locator"),
                }
            ),
            ordinal=int(native.get("order", 0)),
            segment_kind=native.get("semantic_slot", "segment"),
            segmentation_profile="ttna-lyx-layout-and-tex-reader-fragment-v1",
            unit_id=native["unit_id"],
        )
        add(base, native["id"])
        request_rights(base["id"], [native["rights_id"]], "segment")

        variant_key = f"ttna:segment-variant:source:{native['id']}"
        variant_id = generated_id("segment_variant", variant_key)
        source_variant_ids[native["id"]] = variant_id
        variant = common_base("segment_variant", variant_key, recorded_at, record_id=variant_id)
        variant["extensions"] = generated_extension(
            "source_segment_variant", {"native_segment_id": native["id"]}
        )
        variant["extensions"]["interlanguage.source-profile"] = profile
        variant.update(
            edition_id=native["edition_id"],
            format="latex" if source_file["source_path"].lower().endswith(".tex") else "lyx",
            locale=native.get("source_locale", "en-US"),
            payload=native.get("source_text", ""),
            payload_sha256=native["source_text_sha256"],
            rights_id=native["rights_id"],
            role="source",
            segment_id=native["id"],
            source_variant_id=None,
            translation_state=native.get("translation_state", "source_frozen"),
        )
        add(variant)
        request_rights(variant_id, [native["rights_id"]], "source_segment_variant")

    for native in grouped["localization"]:
        source_segment = segments[native["segment_id"]]
        source_file = source_files[source_segment["source_file_id"]]
        profile = source_profile(
            lane_root,
            source_file,
            target_revision_ids[source_segment["source_file_id"]],
            "target_path",
            native.get("target_locator", {}),
            native.get("protected_tokens", []),
            native.get("target_ert_sha256"),
        )
        base = common_base(
            "segment_variant",
            f"ttna:native:localization:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("publication_state", "admitted"),
        )
        base["extensions"]["interlanguage.source-profile"] = profile
        base.update(
            edition_id=source_segment["edition_id"],
            format="latex" if source_file["target_path"].lower().endswith(".tex") else "lyx",
            locale=native.get("locale", "id-ID"),
            payload=native.get("target_text", ""),
            payload_sha256=native["target_text_sha256"],
            rights_id=source_segment["rights_id"],
            role="translation",
            segment_id=native["segment_id"],
            source_variant_id=source_variant_ids[native["segment_id"]],
            translation_state=first_nonempty(
                native.get("workflow_state"), native.get("language_state"), default="translated"
            ),
        )
        add(base, native["id"])
        request_rights(base["id"], [source_segment["rights_id"]], "target_segment_variant")

        align_key = f"ttna:alignment:{native['segment_id']}:{native['id']}"
        alignment = common_base("alignment", align_key, recorded_at)
        alignment.update(
            alignment_kind="source_segment_variant_to_indonesian_segment_variant",
            assertion_method="native segment_id plus exact source/target hashes",
            confidence="exact",
            evidence_locator=canonical_json(native.get("target_locator", {})),
            source_id=source_variant_ids[native["segment_id"]],
            source_locale=source_segment.get("source_locale", "en-US"),
            source_sha256=native.get("source_segment_sha256"),
            target_id=native["id"],
            target_locale=native.get("locale", "id-ID"),
            target_sha256=native.get("target_text_sha256"),
        )
        add(alignment)

    # Native concepts and deterministic lexical concepts for otherwise
    # unbound native terms.  This does not assert broader mathematical ontology.
    denotes = {
        r["from_id"]: r["to_id"]
        for r in grouped["relation"]
        if r.get("relation") == "denotes"
    }
    defined_by = {
        r["from_id"]: r["to_id"]
        for r in grouped["relation"]
        if r.get("relation") == "defined_by"
    }
    for native in grouped["concept"]:
        base = common_base(
            "concept",
            f"ttna:native:concept:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "admitted"),
            workflow_id=native.get("responsible_workflow", WORKFLOW_ID),
            supersedes_id=native.get("supersession_pointer"),
        )
        base.update(
            concept_key=native.get("concept_local_id", native["id"]),
            concept_scheme="ttna-interoperability-v0",
            definition_segment_id=defined_by.get(native["id"]),
            parent_concept_id=None,
        )
        add(base, native["id"])

    lexical_concept_ids: dict[str, str] = {}
    for native in grouped["term"]:
        concept_id = denotes.get(native["id"])
        if concept_id is None:
            concept_key = f"ttna:lexical-concept:{native['id']}"
            concept_id = generated_id("concept", concept_key)
            lexical_concept_ids[native["id"]] = concept_id
            concept = common_base("concept", concept_key, recorded_at, record_id=concept_id)
            concept["extensions"] = generated_extension(
                "lexical_concept_only",
                {"native_term_id": native["id"], "ontology_assertion": False},
            )
            concept.update(
                concept_key=native.get("source_term_id", native["id"]),
                concept_scheme="ttna-native-lexical-term-v1",
                definition_segment_id=None,
                parent_concept_id=None,
            )
            add(concept)
        base = common_base(
            "term",
            f"ttna:native:term:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "accepted"),
        )
        base.update(
            concept_id=concept_id,
            evidence=as_text(native.get("evidence")),
            notes="",
            preferred_form=native.get("preferred", ""),
            register=native.get("scope", "global"),
            scope_unit_id=lexical_scope_id,
            source_form=native.get("source_term", ""),
            source_locale=native.get("source_locale", "en-US"),
            source_term_id=native.get("source_term_id", native["id"]),
            target_locale=native.get("locale", "id-ID"),
            term_status=native.get("status", "accepted"),
        )
        add(base, native["id"])
        for kind, values in (("alternate", native.get("variants", [])), ("rejected", native.get("rejected", []))):
            for ordinal, form in enumerate(values, 1):
                key = f"ttna:term-variant:{native['id']}:{kind}:{ordinal}:{form}"
                variant = common_base("term_variant", key, recorded_at)
                variant.update(
                    form=form,
                    locale=native.get("locale", "id-ID"),
                    rationale="preserved from native terminology record",
                    term_id=native["id"],
                    variant_kind=kind,
                )
                add(variant)

    for native in grouped["asset"]:
        right_id = native.get("rights_id", primary_rights_id)
        base = common_base(
            "asset",
            f"ttna:native:asset:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            asset_kind=first_nonempty(native.get("role"), native.get("component_name"), default="asset"),
            canonical_path_or_uri=native.get("logical_path", ""),
            media_type=native.get("media_type", "application/octet-stream"),
            resource_id=native.get("resource_id", resource_id),
            rights_default_id=right_id,
        )
        add(base, native["id"])
        request_rights(base["id"], [right_id], "asset")

    source_asset_revision = {
        r["from_id"]: r["to_id"]
        for r in grouped["relation"]
        if r.get("relation") in {"documented_revision_of", "normalized_equivalent_to"}
        and by_id.get(r.get("to_id"), {}).get("record_type") == "asset_version"
    }
    for native in grouped["asset_version"]:
        base = common_base(
            "asset_revision",
            f"ttna:native:asset-version:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            asset_id=native["asset_id"],
            bytes=native["source_bytes"],
            edition_id=native["edition_id"],
            file_revision_id=None,
            sha256=native["source_sha256"],
            source_asset_revision_id=source_asset_revision.get(native["id"]),
        )
        add(base, native["id"])
        request_rights(base["id"], [native.get("rights_id")], "asset_revision")

    for native in grouped["build_recipe"]:
        base = common_base(
            "build_recipe",
            f"ttna:native:build-recipe:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            command=list(native.get("command", [])),
            edition_id=native.get("edition_id"),
            environment={},
            input_ids=list(native.get("input_asset_version_ids", [])),
            name=native.get("name", ""),
            output_ids=list(native.get("output_asset_version_ids", [])),
            resource_id=native.get("resource_id"),
            verification=native.get("verification", {}),
            working_directory=native.get("working_directory", ""),
        )
        add(base, native["id"])
        request_rights(base["id"], [native.get("rights_id")], "build_recipe")

    for native in grouped["experiment"]:
        right_ids = native.get("rights_ids", [])
        base = common_base(
            "experiment",
            f"ttna:native:experiment:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            edition_id=native["edition_id"],
            expected_output_segment_ids=list(native.get("expected_output_segment_ids", [])),
            instruction_segment_ids=list(native.get("instruction_segment_ids", [])),
            invocation=native.get("invocation", ""),
            kind=native.get("kind", ""),
            parameter_segment_ids=list(native.get("parameter_evidence_segment_ids", [])),
            resource_id=native["resource_id"],
            result_mode=native.get("result_mode", "specified"),
            rights_id=next((x for x in right_ids if x), primary_rights_id),
            runner_asset_revision_ids=list(native.get("runner_asset_version_ids", [])),
            source_file_revision_id=native.get("source_file_id"),
            unit_id=native["unit_id"],
        )
        add(base, native["id"])
        request_rights(base["id"], right_ids, "experiment")

    # Open correction observations are represented honestly as QA evidence,
    # not as operational replacement records requiring invented payload hashes.
    for native in grouped["correction"]:
        canonical_native = canonical_bytes(native)
        severity = str(native.get("severity", "")).upper()
        base = common_base(
            "qa_event",
            f"ttna:native:correction-observation:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "recorded"),
            workflow_id=native.get("responsible_workflow", WORKFLOW_ID),
            supersedes_id=native.get("supersession_pointer"),
        )
        base.update(
            input_hash=sha256_bytes(canonical_native),
            method="native adverse-ledger observation; no replacement payload asserted",
            qa_type="native_correction_observation",
            result=native.get("status", "recorded"),
            reviewer_kind="source_evidence_workflow",
            severity_p1=1 if severity == "P1" else 0,
            severity_p2=1 if severity == "P2" else 0,
            severity_p3=1 if severity == "P3" else 0,
            tool_name=native.get("schema_id", "ttna-correction-v1"),
            tool_version=native.get("schema_version", "1.0.0"),
            witness_locator=first_nonempty(native.get("source_locator"), native.get("evidence"), default=""),
        )
        add(base, native["id"])

    for native in grouped["qa_event"]:
        checks = native.get("checks", [])
        p_counts = Counter(str(item.get("severity", "")).upper() for item in checks if isinstance(item, dict))
        base = common_base(
            "qa_event",
            f"ttna:native:qa-event:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            input_hash=sha256_bytes(canonical_bytes(native)),
            method="native QA event preserved losslessly in extension",
            qa_type=native.get("qa_type", "native_qa"),
            result=native.get("result", "recorded"),
            reviewer_kind="native_workflow",
            severity_p1=p_counts.get("P1", 0),
            severity_p2=p_counts.get("P2", 0),
            severity_p3=p_counts.get("P3", 0),
            tool_name=native.get("schema_id", "ttna-qa-v1"),
            tool_version=native.get("schema_version", "1.0.0"),
            witness_locator=as_text(native.get("witness")),
        )
        add(base, native["id"])

    for native in grouped["artifact"]:
        build_receipt = native.get("build_receipt", {})
        public_uri = None
        if native["sha256"] == boundary["final_artifact"]["sha256"]:
            public_uri = boundary["zenodo"].get("record_url")
        base = common_base(
            "artifact",
            f"ttna:native:artifact:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
            status=native.get("status", "recorded"),
            workflow_id=native.get("responsible_workflow", WORKFLOW_ID),
            supersedes_id=native.get("supersession_pointer"),
        )
        base.update(
            artifact_kind=first_nonempty(native.get("artifact_role"), native.get("media_type"), default="artifact"),
            build_receipt=build_receipt.get("path", "") if isinstance(build_receipt, dict) else as_text(build_receipt),
            bytes=native.get("bytes"),
            edition_id=native["edition_id"],
            locale=native.get("locale", ""),
            manifest_sha256=build_receipt.get("sha256") if isinstance(build_receipt, dict) else None,
            public_uri=public_uri,
            sha256=native.get("sha256"),
            toolchain_id="ttna-native-build-toolchain",
            tree_sha256=None,
        )
        add(base, native["id"])
        request_rights(base["id"], native.get("rights_ids", []), "artifact")

    for native in grouped["relation"]:
        base = common_base(
            "relation",
            f"ttna:native:relation:{native['id']}",
            get_timestamp(native, recorded_at),
            record_id=native["id"],
            native=native,
        )
        base.update(
            assertion_method=first_nonempty(native.get("match_kind"), default="native typed relation"),
            confidence="exact_native_assertion",
            edition_id=edition_id,
            from_id=native["from_id"],
            ordinal=int(native.get("order", 0)),
            relation_type=native.get("relation", "related_to"),
            source_locator=as_text(
                {
                    key: native[key]
                    for key in ("asset_line_range", "evidence_segment_ids", "declared_function", "normalization_id")
                    if key in native
                }
            ),
            strength="declared",
            to_id=native["to_id"],
        )
        add(base, native["id"])

    # One complete-corpus module and ordered native unit membership.
    root_unit_ids = course.get("root_unit_ids", [])
    if not root_unit_ids:
        raise ValueError("native course has no root unit")
    module_key = f"ttna:module:complete-corpus:{version}"
    module_id = generated_id("module", module_key)
    module = common_base("module", module_key, recorded_at, record_id=module_id, status="public")
    module["extensions"] = generated_extension(
        "complete_native_corpus_module", {"native_lane_manifest_sha256": lane_manifest_sha}
    )
    module.update(
        closure_profile="all native units; relations and dependent records close in virtual stream",
        course_id=course["id"],
        description="Complete native R015 unit closure",
        edition_id=edition_id,
        locale="id-ID",
        manifest_sha256=lane_manifest_sha,
        module_kind="complete_corpus",
        module_version=version,
        root_unit_id=root_unit_ids[0],
        title=boundary["current_state"].get("work", {}).get("translated_title", ""),
    )
    add(module)
    for ordinal, native in enumerate(sorted(grouped["unit"], key=lambda r: (r.get("order", 0), r["id"])), 1):
        key = f"ttna:module-member:{module_id}:{native['id']}"
        member = common_base("module_member", key, recorded_at)
        member.update(
            entity_id=native["id"],
            inclusion_reason="native unit in complete corpus",
            module_id=module_id,
            order_path=f"{int(native.get('order', 0)):06d}:{native.get('source_local_id', native['id'])}",
            required=True,
            role=native.get("kind", "unit"),
        )
        add(member)

    # Public release snapshot, only after the clean-boundary gate proves the
    # same final artifact on both named public repositories.
    release_key = f"ttna:release-snapshot:{version}"
    release = common_base("release_snapshot", release_key, recorded_at, status="public")
    release["extensions"] = generated_extension(
        "public_release_snapshot",
        {
            "zenodo_record_id": boundary["zenodo"].get("record_id"),
            "github_release_id": boundary["github"].get("github_release", {}).get("release_id"),
        },
    )
    release.update(
        archive_sha256=archive_sha,
        artifact_ids=[boundary["final_artifact"]["id"]],
        commit_sha=public_commit,
        edition_id=edition_id,
        immutable=True,
        publication_uri=boundary["zenodo"].get("record_url"),
        release_date=boundary["release_date"],
        release_version=version,
        snapshot_kind="public_release",
        tree_sha=None,
    )
    add(release)

    # Materialize explicit rights bindings requested above.
    for precedence, (target_id, rights_id, role) in enumerate(sorted(rights_requests), 1):
        key = f"ttna:rights-assignment:{target_id}:{rights_id}:{role}"
        assignment = common_base("rights_assignment", key, recorded_at)
        assignment.update(
            assignment_status="verified_from_native_record",
            inheritance="explicit_or_native_component_scope",
            precedence=precedence,
            rights_id=rights_id,
            scope_role=role,
            target_id=target_id,
        )
        add(assignment)

    native_ids = {r["id"] for r in records}
    if set(native_map) != native_ids:
        missing = sorted(native_ids - set(native_map))
        raise ValueError(f"native mapping is incomplete: {len(missing)} IDs missing")
    if any(native_map[key] != key for key in native_map):
        raise ValueError("one or more native IDs changed during mapping")

    ids = [r["id"] for r in all_records]
    if len(ids) != len(set(ids)):
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        raise ValueError(f"duplicate common IDs: {duplicates[:3]}")
    id_set = set(ids)
    unresolved: set[str] = set()

    def walk_common(value: Any) -> None:
        if isinstance(value, str) and value.startswith("urn:uuid:") and value not in id_set:
            unresolved.add(value)
        elif isinstance(value, list):
            for item in value:
                walk_common(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk_common(item)

    for record in all_records:
        walk_common(record)
    if unresolved:
        raise ValueError(f"common foreign-key closure failed for {len(unresolved)} UUIDs")

    table_names = list(common_schema["properties"]["tables"]["required"])
    tables = {name: [] for name in table_names}
    for record in sorted(all_records, key=lambda r: (r["id"], r["record_type"])):
        table = TABLE_BY_RECORD_TYPE[record["record_type"]]
        tables[table].append(record)
    dataset_id = generated_id("dataset", "tea-time-numerical-analysis-id:common-backend-v1")
    dataset = {
        "$schema": "schema/backend-v1.schema.json",
        "dataset_id": dataset_id,
        "dataset_version": f"{version}+common-backend-v1.1",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": tables,
    }

    validator = Draft202012Validator(common_schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(dataset), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        raise ValueError(
            f"common schema failure at {'/'.join(map(str, first.absolute_path))}: {first.message}"
        )
    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    profiles = []
    for record in all_records:
        profile = record.get("extensions", {}).get("interlanguage.source-profile")
        if profile is not None:
            errors = sorted(profile_validator.iter_errors(profile), key=lambda e: list(e.absolute_path))
            if errors:
                raise ValueError(
                    f"source profile failure for {record['id']}: {errors[0].message}"
                )
            profiles.append(profile)

    ordered_records = sorted(all_records, key=lambda r: (r["id"], r["record_type"]))
    virtual_bytes = b"".join(canonical_bytes(record) + b"\n" for record in ordered_records)
    return dataset, {
        "record_count": len(all_records),
        "table_counts": {name: len(tables[name]) for name in sorted(tables)},
        "virtual_bytes": len(virtual_bytes),
        "virtual_sha256": sha256_bytes(virtual_bytes),
        "native_ids_preserved": len(native_map),
        "native_ids_changed": 0,
        "generated_records": len(all_records) - len(native_map),
        "source_profiles": len(profiles),
        "source_profile_counts": dict(
            sorted(Counter(profile["format_profile"] for profile in profiles).items())
        ),
        "unresolved_uuid_references": 0,
        "global_id_unique": True,
        "dataset_id": dataset_id,
        "dataset_version": dataset["dataset_version"],
    }


def public_artifacts(boundary: dict[str, Any]) -> list[dict[str, Any]]:
    result = [
        {
            "repository": "GitHub",
            "url": boundary["github"].get("repository_url"),
            "release_url": boundary["github"].get("github_release", {}).get("url"),
            "tag": boundary["tag"],
            "commit": boundary["github"].get("public_main_commit_at_release")
            or boundary["github"].get("release_commit"),
            "anonymous_readback": "pass",
        },
        {
            "repository": "Zenodo",
            "url": boundary["zenodo"].get("record_url"),
            "version_doi": boundary["zenodo"].get("version_doi"),
            "concept_doi": boundary["zenodo"].get("concept_doi"),
            "files": [
                {
                    "filename": item.get("filename"),
                    "bytes": item.get("bytes"),
                    "sha256": item.get("sha256"),
                }
                for item in boundary["zenodo"].get("files", [])
            ],
            "anonymous_readback": "pass",
        },
    ]
    figshare = boundary["publication_state"].get("figshare_record")
    if isinstance(figshare, dict) and figshare.get("url"):
        result.append(
            {
                "repository": "Figshare",
                "url": figshare.get("url"),
                "doi": figshare.get("doi"),
                "version": figshare.get("version"),
                "anonymous_readback": figshare.get("anonymous_public_readback"),
            }
        )
    return result


def main() -> int:
    script_path = Path(__file__).resolve()
    hub_root = script_path.parents[1]
    default_lane = hub_root.parent / "tea-time-numerical-analysis-id"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane-root", type=Path, default=default_lane)
    parser.add_argument("--schema", type=Path, default=hub_root / "schemas/backend-v1.schema.json")
    parser.add_argument(
        "--profile-schema",
        type=Path,
        default=hub_root / "schemas/profiles/source-format-profile-v1.schema.json",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=hub_root / "backend/migrations/tea-time-id-v1/MIGRATION_RECEIPT.json",
    )
    args = parser.parse_args()
    lane_root = args.lane_root.resolve()
    common_schema_path = args.schema.resolve()
    profile_schema_path = args.profile_schema.resolve()
    receipt_path = args.receipt.resolve()

    native_schema_path = lane_root / "backend/schema/record.schema.json"
    lane_manifest_path = lane_root / "backend/manifests/lane_manifest.json"
    export_root = lane_root / "backend/exports/interoperability-v0"
    export_manifest_path = export_root / "manifest.json"
    jsonl_path = export_root / "records.jsonl"
    csv_path = export_root / "records.csv"
    current_state_path = lane_root / "00_control/CURRENT_STATE.json"
    current_cursor_path = lane_root / "00_control/CURRENT_CURSOR.json"
    publication_state_path = lane_root / "00_control/PUBLICATION_STATE.json"
    publication_receipt_path = lane_root / "publication/PUBLICATION_RECEIPT.json"

    records, native_validation = verify_native_export(
        lane_root,
        native_schema_path,
        lane_manifest_path,
        export_manifest_path,
        jsonl_path,
        csv_path,
    )
    payload_paths, payload_closure = verify_payload_files(lane_root, records)
    boundary = clean_public_boundary(
        lane_root,
        records,
        lane_manifest_path,
        current_state_path,
        current_cursor_path,
        publication_state_path,
        publication_receipt_path,
    )
    common_schema = load_json(common_schema_path)
    profile_schema = load_json(profile_schema_path)

    control_paths = [
        native_schema_path,
        lane_manifest_path,
        export_manifest_path,
        jsonl_path,
        csv_path,
        current_state_path,
        current_cursor_path,
        publication_state_path,
        publication_receipt_path,
    ]
    before = input_snapshot(control_paths + payload_paths, lane_root)
    dataset_a, target_a = build_common_dataset(
        lane_root,
        records,
        common_schema,
        profile_schema,
        boundary,
        native_validation["lane_manifest"]["sha256"],
    )
    dataset_b, target_b = build_common_dataset(
        lane_root,
        records,
        common_schema,
        profile_schema,
        boundary,
        native_validation["lane_manifest"]["sha256"],
    )
    after = input_snapshot(control_paths + payload_paths, lane_root)
    if before != after:
        raise RuntimeError("native inputs changed during the two-run migration proof")
    if canonical_bytes(dataset_a) != canonical_bytes(dataset_b) or target_a != target_b:
        raise RuntimeError("the two independently assembled virtual datasets differ")

    common_schema_identity = file_identity(common_schema_path, hub_root)
    profile_schema_identity = file_identity(profile_schema_path, hub_root)
    script_identity = file_identity(script_path, hub_root)
    native_counts = native_validation["record_counts"]
    target_counts = {k: v for k, v in target_a["table_counts"].items() if v}
    public = public_artifacts(boundary)
    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": "1.0.0",
        "migration_id": "tea-time-numerical-analysis-id-v1",
        "migration_mode": "additive_zero_copy_virtual_adapter",
        "source": {
            "corpus_id": "R015",
            "course_id": "C110",
            "locale": "id-ID",
            "native_backend": native_validation,
            "payload_closure": payload_closure,
            "public_release": {
                "version": boundary["version"],
                "tag": boundary["tag"],
                "publication_receipt_sha256": boundary["publication_receipt_sha256"],
                "final_artifact_id": boundary["final_artifact"]["id"],
                "final_artifact_bytes": boundary["final_artifact"]["bytes"],
                "final_artifact_sha256": boundary["final_artifact"]["sha256"],
            },
        },
        "target": {
            "dataset_id": target_a["dataset_id"],
            "dataset_version": target_a["dataset_version"],
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "record_count": target_a["record_count"],
            "schema_sha256": common_schema_identity["sha256"],
            "virtual_records_jsonl_bytes": target_a["virtual_bytes"],
            "virtual_records_jsonl_sha256": target_a["virtual_sha256"],
        },
        "transformation": {
            "classification": "additive adapter over a stronger native LyX backend",
            "adapter": script_identity,
            "identity_namespace": str(COMMON_NAMESPACE),
            "identity_formula": "UUIDv5(namespace, record_type|stable_key)",
            "native_ids_preserved": target_a["native_ids_preserved"],
            "native_ids_changed": target_a["native_ids_changed"],
            "native_payload_fields_changed": 0,
            "generated_common_records": target_a["generated_records"],
            "source_profile_schema": profile_schema_identity,
            "source_profiles": target_a["source_profiles"],
            "source_profile_counts": target_a["source_profile_counts"],
            "native_type_mapping": {
                "artifact": "artifact",
                "asset": "asset",
                "asset_version": "asset_revision",
                "build_recipe": "build_recipe",
                "concept": "concept",
                "correction": "qa_event (observation; no invented replacement payload)",
                "course": "course",
                "edition": "edition",
                "experiment": "experiment",
                "localization": "segment_variant",
                "program": "program",
                "qa_event": "qa_event",
                "relation": "relation",
                "resource": "resource",
                "rights": "rights",
                "segment": "segment plus generated source segment_variant",
                "source_file": "source file_revision plus generated source/target files and target file_revision",
                "term": "term plus generated lexical concept when no native denotes relation",
                "unit": "unit",
            },
        },
        "validation": {
            "result": "pass",
            "native_schema": "pass",
            "common_schema": "pass",
            "strict_source_profile_schema": "pass",
            "canonical_native_jsonl": "pass",
            "lossless_native_csv_round_trip": "pass",
            "native_global_id_uniqueness": "pass",
            "native_foreign_key_closure": "pass",
            "common_global_id_uniqueness": "pass",
            "common_foreign_key_closure": "pass",
            "native_input_stability_across_runs": "pass",
            "deterministic_virtual_assembly_runs": 2,
            "deterministic_virtual_assembly_equal": True,
            "public_release_timing_gate": "pass",
            "source_and_target_payload_byte_changes": 0,
        },
        "coverage": {
            "native_records": native_validation["record_count"],
            "native_record_types": len(native_counts),
            "native_record_counts": native_counts,
            "native_ids_represented": target_a["native_ids_preserved"],
            "native_ids_omitted": 0,
            "source_files_verified": payload_closure["source_files"],
            "target_files_verified": payload_closure["target_files"],
            "asset_version_files_verified": payload_closure["asset_version_files"],
            "artifacts_verified": payload_closure["artifacts"],
        },
        "tables": target_counts,
        "materialization": {
            "decision": "receipt_only_zero_copy_virtual_stream",
            "native_backend_remains_authoritative": True,
            "virtual_records_materialized": False,
            "reason": "avoid duplicating a complete stronger native backend while proving deterministic common-v1 interoperability",
        },
        "public_artifacts": public,
        "credentials_recorded": False,
    }

    receipt_schema_path = hub_root / "schemas/backend-migration-receipt-v1.schema.json"
    receipt_schema = load_json(receipt_schema_path)
    errors = sorted(
        Draft202012Validator(receipt_schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(
            f"receipt schema failure at {'/'.join(map(str, first.absolute_path))}: {first.message}"
        )
    receipt_bytes = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_bytes(receipt_bytes)
    reread = receipt_path.read_bytes()
    if reread != receipt_bytes or load_json(receipt_path) != receipt:
        raise RuntimeError("receipt readback differs from emitted bytes")

    summary = {
        "result": "pass",
        "receipt": receipt_path.relative_to(hub_root).as_posix(),
        "receipt_bytes": len(receipt_bytes),
        "receipt_sha256": sha256_bytes(receipt_bytes),
        "native_records": native_validation["record_count"],
        "target_records": target_a["record_count"],
        "virtual_records_jsonl_bytes": target_a["virtual_bytes"],
        "virtual_records_jsonl_sha256": target_a["virtual_sha256"],
        "table_counts": target_counts,
        "deterministic_runs": 2,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
