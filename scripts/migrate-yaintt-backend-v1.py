#!/usr/bin/env python3
"""Validate and virtually adapt the complete R014 YAINTT backend to v1.

The completed edition already has a rich 5,272-record native backend.  This
program leaves that backend byte-identical, verifies its complete manifest and
payload closure, and assembles a strict common-backend view in memory.  Every
native record is reversibly retained in exactly one direct common record; the
additional records expose source/translation variants, LaTeX source bindings,
asset revisions, term variants, whole-book module membership, a build recipe,
and verified public release snapshots.  Only a compact receipt is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_NAME = "r014.backend.record"
SOURCE_SCHEMA_VERSION = "1.0.0"
WORKFLOW = "program-matematika-indonesia/yaintt-v1-migrator-1.0.0"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
NATIVE_EXTENSION = "interlanguage.yaintt-native"
DERIVED_EXTENSION = "interlanguage.yaintt-derived"
PROFILE_EXTENSION = "interlanguage.source-profile"

SOURCE_EDITION = "ttp.r014.edition.source.2014-05-07"
FINAL_EDITION = "ttp.r014.edition.id-id.boundary28-final"
SOURCE_RIGHTS = "rights.yaintt.text_and_author_assets"
FINAL_RIGHTS = "rights.yaintt.id-id.derivative.boundary28-r2"
ROOT_UNIT = "ttp.r014.unit.book"

DIRECT_TYPES = {
    "program": ("programs", "program"),
    "course": ("courses", "course"),
    "resource": ("resources", "resource"),
    "rights": ("rights", "rights"),
    "edition": ("editions", "edition"),
    "unit": ("units", "unit"),
    "segment": ("segments", "segment"),
    "concept": ("concepts", "concept"),
    "term": ("terms", "term"),
    "correction": ("corrections", "correction"),
    "relation": ("relations", "relation"),
    "qa_event": ("qa_events", "qa_event"),
    "asset": ("assets", "asset"),
    "artifact": ("artifacts", "artifact"),
}

REFERENCE_FIELDS = {
    "program": ["course_ids"],
    "course": ["resource_id", "resource_ids"],
    "resource": ["rights_id"],
    "edition": ["resource_id", "rights_id", "source_edition_id", "supersedes", "file_ids"],
    "unit": ["parent_unit_id", "edition_id", "rights_id", "qa_event_ids"],
    "segment": ["unit_id", "edition_id", "rights_id", "qa_event_ids"],
    "concept": ["prerequisite_concept_ids"],
    "term": ["concept_id"],
    "correction": ["affected_unit_ids"],
    "relation": ["subject_id", "object_id", "edition_id"],
    "qa_event": ["edition_id", "witness_ids"],
    "asset": ["edition_id", "resource_id", "rights_id", "dependency_ids"],
    "artifact": ["edition_id", "resource_id", "build_receipt_id"],
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


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def base(record_type: str, stable_key: str, recorded_at: str, status: str = "active", **fields: Any) -> dict:
    return {
        "id": rid(record_type, stable_key),
        "record_type": record_type,
        "recorded_at": recorded_at,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": status,
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def native_extension(record: dict) -> dict:
    return {
        NATIVE_EXTENSION: {
            "native_record": record,
            "native_record_id": record["record_id"],
            "native_record_sha256": sha256_bytes(canonical_bytes(record)),
            "source_schema": record["schema"],
            "source_schema_version": record["schema_version"],
        }
    }


def read_records(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    raw_lines: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"native JSONL line lacks LF terminator: {line_number}")
            record = json.loads(line)
            if line != canonical(record) + "\n":
                raise ValueError(f"native JSONL is not canonical at line {line_number}")
            records.append(record)
            raw_lines.append(line)
    return records, raw_lines


def as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def evidence_locator_and_hash(root: Path, record: dict) -> tuple[str, str]:
    evidence = record.get("evidence") or {}
    relative = evidence.get("path") or evidence.get("manifest")
    if relative:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"rights evidence is absent: {relative}")
        return relative, sha256_file(path)
    locator = evidence.get("source_url") or f"backend/records.jsonl#{record['record_id']}"
    return locator, sha256_bytes(canonical_bytes(evidence))


def verify_artifact_closure(root: Path, record: dict) -> tuple[int, int]:
    path = root / record["path"]
    manifest = record.get("file_manifest")
    if manifest:
        member_bytes = 0
        manifest_payload = bytearray()
        for member in manifest:
            member_path = root / member["path"]
            if not member_path.is_file():
                raise ValueError(f"artifact member is absent: {member['path']}")
            actual_bytes = member_path.stat().st_size
            actual_sha = sha256_file(member_path)
            if actual_bytes != member["bytes"] or actual_sha != member["sha256"]:
                raise ValueError(f"artifact member identity mismatch: {member['path']}")
            member_bytes += actual_bytes
            manifest_payload.extend(f"{member['path']}\t{member['bytes']}\t{member['sha256']}\n".encode("utf-8"))
        if member_bytes != record["bytes"] or sha256_bytes(bytes(manifest_payload)) != record["sha256"]:
            raise ValueError(f"artifact bundle identity mismatch: {record['record_id']}")
        return len(manifest), member_bytes
    if not path.is_file():
        raise ValueError(f"artifact is absent: {record['path']}")
    if path.stat().st_size != record["bytes"] or sha256_file(path) != record["sha256"]:
        raise ValueError(f"artifact identity mismatch: {record['record_id']}")
    return 1, record["bytes"]


def verify_native(root: Path, records: list[dict], raw_lines: list[str], manifest: dict, native_schema: dict) -> dict:
    backend = root / "backend"
    manifest_path = backend / "MANIFEST.json"
    checksum_text = (backend / "MANIFEST.sha256").read_text(encoding="utf-8").strip()
    expected_manifest_sha = checksum_text.split()[0]
    actual_manifest_sha = sha256_file(manifest_path)
    if expected_manifest_sha != actual_manifest_sha:
        raise ValueError("native MANIFEST.sha256 does not bind MANIFEST.json")

    manifest_bytes = 0
    for item in manifest["files"]:
        path = backend / item["path"]
        if not path.is_file():
            raise ValueError(f"manifest member is absent: {item['path']}")
        if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            raise ValueError(f"manifest member identity mismatch: {item['path']}")
        manifest_bytes += item["bytes"]

    validator = Draft202012Validator(native_schema, format_checker=FormatChecker())
    native_ids: list[str] = []
    native_counts: Counter[str] = Counter()
    segment_source_count = 0
    segment_target_count = 0
    segment_source_bytes = 0
    segment_target_bytes = 0
    asset_count = 0
    artifact_count = 0
    artifact_members = 0
    artifact_bytes = 0
    for index, record in enumerate(records, start=1):
        errors = list(validator.iter_errors(record))
        if errors:
            first = errors[0]
            raise ValueError(f"native schema failure row {index} {list(first.absolute_path)}: {first.message}")
        if record.get("schema") != SOURCE_SCHEMA_NAME or record.get("schema_version") != SOURCE_SCHEMA_VERSION:
            raise ValueError(f"unexpected native header: {record.get('record_id')}")
        native_ids.append(record["record_id"])
        native_counts[record["entity_class"]] += 1
        if record["entity_class"] == "segment":
            for expression in record["expressions"]:
                payload = expression["text_latex"].encode("utf-8")
                if sha256_bytes(payload) != expression["content_sha256"]:
                    raise ValueError(f"segment expression hash mismatch: {expression['expression_id']}")
                if expression["source_or_target"] == "source":
                    segment_source_count += 1
                    segment_source_bytes += len(payload)
                elif expression["source_or_target"] == "target":
                    segment_target_count += 1
                    segment_target_bytes += len(payload)
                else:
                    raise ValueError(f"unknown expression role: {expression['source_or_target']}")
        elif record["entity_class"] == "asset":
            asset_path = root / record["path"]
            if not asset_path.is_file() or asset_path.stat().st_size != record["bytes"] or sha256_file(asset_path) != record["sha256"]:
                raise ValueError(f"asset identity mismatch: {record['record_id']}")
            asset_count += 1
        elif record["entity_class"] == "artifact":
            members, bytes_verified = verify_artifact_closure(root, record)
            artifact_members += members
            artifact_bytes += bytes_verified
            artifact_count += 1

    duplicates = [value for value, count in Counter(native_ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate native IDs: {duplicates[:10]}")
    if dict(sorted(native_counts.items())) != dict(sorted(manifest["record_counts"].items())):
        raise ValueError("native record counts disagree with manifest")
    if len(records) != sum(manifest["record_counts"].values()):
        raise ValueError("native total record count disagrees with manifest")

    known = set(native_ids)
    missing_references: list[tuple[str, str, str]] = []
    for record in records:
        for field in REFERENCE_FIELDS.get(record["entity_class"], []):
            for value in as_list(record.get(field)):
                if value not in known:
                    missing_references.append((record["record_id"], field, value))
    if missing_references:
        raise ValueError(f"native foreign-key closure failure: {missing_references[:10]}")

    catalog = json.loads((backend / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("records") != records:
        raise ValueError("catalog.json records are not byte-semantic equivalents of records.jsonl")
    if catalog.get("record_counts") != manifest.get("record_counts"):
        raise ValueError("catalog.json record counts disagree with MANIFEST.json")
    raw_payload = "".join(raw_lines).encode("utf-8")
    if len(raw_payload) != (backend / "records.jsonl").stat().st_size or sha256_bytes(raw_payload) != sha256_file(backend / "records.jsonl"):
        raise ValueError("native JSONL reread identity mismatch")

    return {
        "manifest_file_count": len(manifest["files"]),
        "manifest_member_bytes": manifest_bytes,
        "manifest_sha256": actual_manifest_sha,
        "native_record_count": len(records),
        "native_record_counts": dict(sorted(native_counts.items())),
        "native_unique_ids": len(known),
        "native_foreign_key_closure": "pass",
        "canonical_native_jsonl": "pass",
        "catalog_exact_record_equivalence": "pass",
        "source_segment_variants": segment_source_count,
        "target_segment_variants": segment_target_count,
        "source_segment_payload_bytes": segment_source_bytes,
        "target_segment_payload_bytes": segment_target_bytes,
        "assets_verified": asset_count,
        "artifacts_verified": artifact_count,
        "artifact_members_verified": artifact_members,
        "artifact_member_bytes_verified": artifact_bytes,
    }


def line_byte_range(path: Path, start_line: int, end_line: int) -> tuple[int, int, str]:
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise ValueError(f"invalid line locator {path}:{start_line}-{end_line}")
    start = sum(len(line) for line in lines[: start_line - 1])
    end = sum(len(line) for line in lines[:end_line])
    return start, end, sha256_bytes(data[start:end])


def referenced_urns(value: Any, path: tuple[str, ...] = ()):
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
    root: Path,
    records: list[dict],
    manifest: dict,
    schema: dict,
    profile_schema: dict,
    publication: dict,
    figshare: dict,
) -> tuple[dict, dict]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}

    def add(table: str, record: dict) -> str:
        tables[table].append(record)
        return record["id"]

    by_native = {record["record_id"]: record for record in records}
    id_map = {
        record["record_id"]: rid(DIRECT_TYPES[record["entity_class"]][1], f"yaintt:{record['record_id']}")
        for record in records
    }

    def mapped(native_id: str | None, default: str | None = None) -> str | None:
        value = native_id if native_id is not None else default
        if value is None:
            return None
        if value not in id_map:
            raise ValueError(f"unmapped native reference: {value}")
        return id_map[value]

    program_native = next(record for record in records if record["entity_class"] == "program")
    resource_native = next(record for record in records if record["entity_class"] == "resource")
    program_id = mapped(program_native["record_id"])
    resource_id = mapped(resource_native["record_id"])
    source_edition_id = mapped(SOURCE_EDITION)
    final_edition_id = mapped(FINAL_EDITION)
    source_rights_id = mapped(SOURCE_RIGHTS)
    final_rights_id = mapped(FINAL_RIGHTS)
    root_unit_id = mapped(ROOT_UNIT)
    unbound_term_concept_key = "yaintt:r014:technical-unbound-term-concept"
    unbound_term_concept_id = rid("concept", unbound_term_concept_key)
    unbound_term_count = 0
    github = publication["github"]
    release_commit = github["commit_sha"]
    release_tag = github["tag"]
    release_date = publication["verified_at_utc"][:10]
    public_uri_by_sha = {
        item["sha256"]: item["download_url"]
        for item in github["assets"]
        if item.get("sha256") and item.get("download_url")
    }
    for item in publication["zenodo"]["files"]:
        if item.get("sha256") and item.get("content_url"):
            public_uri_by_sha.setdefault(item["sha256"], item["content_url"])

    for native in records:
        entity_class = native["entity_class"]
        table, record_type = DIRECT_TYPES[entity_class]
        stable_key = f"yaintt:{native['record_id']}"
        common = base(record_type, stable_key, native["created_at"], native["status"])
        common["extensions"] = native_extension(native)
        common["supersedes_id"] = mapped(native.get("supersedes"))

        if entity_class == "program":
            common.update(
                curriculum_version=native["program_code"],
                locale=native["locale"],
                program_key=native["program_code"],
                rights_id=final_rights_id,
                title=native["title"],
            )
        elif entity_class == "course":
            authority = program_native.get("curriculum_authority") or {}
            common.update(
                course_key=native["course_code"],
                curriculum_source_locator=authority.get("path", ""),
                curriculum_source_sha256=authority.get("source_sha256"),
                order_key=native["course_code"],
                outcome=native.get("outcome", ""),
                prerequisite_course_keys=native.get("prerequisite_course_ids", []),
                program_id=program_id,
                resource_keys=native.get("resource_ids", []),
                role=native.get("curriculum_status", "course_resource"),
                scope=native.get("scope", ""),
                stage=native.get("stage", ""),
                title=native.get("title", ""),
            )
        elif entity_class == "resource":
            authors = native.get("authors") or []
            creator_name = "; ".join(authors) if isinstance(authors, list) else str(authors)
            common.update(
                authority_policy=f"Frozen official-source snapshot {native.get('source_available_snapshot', '')}",
                creator_name=creator_name,
                official_reader=native.get("official_pdf_url"),
                official_repository=native.get("upstream_repository") or native.get("authority_url", ""),
                original_title=native["title"],
                resource_key=native["record_id"],
                work_type="open textbook",
            )
        elif entity_class == "rights":
            notice_locator, notice_sha = evidence_locator_and_hash(root, native)
            attribution = native.get("attribution") or ""
            if isinstance(attribution, list):
                attribution = "; ".join(attribution)
            common.update(
                assertion_status=native.get("rights_status", "native_rights_record"),
                attribution=attribution,
                authority=canonical(native.get("evidence") or {}),
                change_notice=native.get("change_notice") or "",
                license_expression=native.get("license") or "NOASSERTION",
                nonendorsement=native.get("non_endorsement") or "",
                notice_locator=notice_locator,
                notice_sha256=notice_sha,
                source_component_id=native["record_id"],
                third_party_status=native.get("rights_status", "native_rights_record"),
            )
        elif entity_class == "edition":
            rights = mapped(native.get("rights_id"), SOURCE_RIGHTS if native["record_id"] == SOURCE_EDITION else FINAL_RIGHTS)
            common.update(
                archive_sha256=None,
                commit_sha=release_commit,
                edition_kind=native["edition_kind"],
                locale=native["locale"],
                release_date=release_date if native["record_id"] == FINAL_EDITION else None,
                resource_id=resource_id,
                rights_id=rights,
                source_edition_id=mapped(native.get("source_edition_id")),
                tree_sha=github.get("tree_sha"),
                vcs_ref=release_tag,
                vcs_type="git",
                version_label=native.get("source_snapshot_id") or native.get("translated_through") or native["record_id"],
            )
            common["extensions"][NATIVE_EXTENSION]["public_capture_commit"] = release_commit
        elif entity_class == "unit":
            locator = native.get("source_locator") or {}
            common.update(
                first_edition_id=mapped(native["edition_id"]),
                identity_anchor=native.get("source_local_id") or native["record_id"],
                identity_basis=native.get("label_status", "native_r014_record_id"),
                resource_id=resource_id,
                rights_default_id=mapped(native["rights_id"]),
                source_label=native.get("source_local_id"),
                source_local_id=native.get("source_local_id"),
                source_path=locator.get("path") or native.get("path") or "",
                source_xml_path=None,
                unit_kind=native["unit_type"],
            )
        elif entity_class == "segment":
            common.update(
                identity_anchor=native.get("source_expression_id") or native.get("target_expression_id") or native["record_id"],
                ordinal=int(native["order"]),
                segment_kind=native["segment_kind"],
                segmentation_profile="r014-latex-segments-v1",
                unit_id=mapped(native["unit_id"]),
            )
        elif entity_class == "concept":
            common.update(
                concept_key=native["concept_code"],
                concept_scheme=native.get("taxonomy_path") or "r014-number-theory",
                definition_segment_id=None,
                parent_concept_id=None,
            )
        elif entity_class == "term":
            if native.get("concept_id") is None:
                unbound_term_count += 1
            common.update(
                concept_id=mapped(native.get("concept_id")) or unbound_term_concept_id,
                evidence=canonical(native.get("evidence") or {}),
                notes=native.get("scope") or "",
                preferred_form=native["target_term"],
                register=native.get("register") or "",
                scope_unit_id=root_unit_id,
                source_form=native["source_term"],
                source_locale="en",
                source_term_id=native["record_id"],
                target_locale=native["locale"],
                term_status=native["status"],
            )
        elif entity_class == "correction":
            affected = native.get("affected_unit_ids") or [ROOT_UNIT]
            common.update(
                affected_id=mapped(affected[0]),
                category=native["correction_type"],
                evidence_locator=canonical({"authority_locator": native.get("authority_locator"), "evidence": native.get("evidence")}),
                local_state=native.get("report_status") or "recorded",
                original_payload_sha256=sha256_bytes(native["source_text"].encode("utf-8")),
                payload_hash_basis="UTF-8 bytes of native source_text and target_text fields",
                rationale=native.get("rationale") or "",
                replacement_payload_sha256=sha256_bytes(native["target_text"].encode("utf-8")),
                source_claim_id=None,
                source_edition_id=source_edition_id,
                source_record_id=None,
                upstream_disposition=native.get("upstream_report_disposition") or native.get("report_status") or "not_submitted",
                upstream_url=None,
            )
        elif entity_class == "relation":
            common.update(
                assertion_method="native_r014_explicit_relation",
                confidence=native["confidence"],
                edition_id=mapped(native.get("edition_id")),
                from_id=mapped(native["subject_id"]),
                ordinal=int(native["relation_order"]),
                relation_type=native["predicate"],
                source_locator=canonical(native.get("evidence_locator")) if native.get("evidence_locator") is not None else "",
                strength=native["confidence"],
                to_id=mapped(native["object_id"]),
            )
        elif entity_class == "qa_event":
            evidence = native.get("evidence") or {}
            common.update(
                input_hash=sha256_bytes(canonical_bytes(native)),
                method=native.get("method") or "",
                qa_type=native["qa_type"],
                result=native["result"],
                reviewer_kind="native_r014_qa_record",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name=native["responsible_workflow"],
                tool_version=native["schema_version"],
                witness_locator=evidence.get("path") or canonical(evidence),
            )
            common["extensions"][NATIVE_EXTENSION]["severity_mapping"] = "Native record has no severity-count fields; required common fields are zero-valued and must not be read as an independent finding count."
        elif entity_class == "asset":
            common.update(
                asset_kind=native["role"],
                canonical_path_or_uri=native.get("path") or native.get("url") or "",
                media_type=native["mime_type"],
                resource_id=resource_id,
                rights_default_id=mapped(native["rights_id"]),
            )
        elif entity_class == "artifact":
            artifact_edition = mapped(native.get("edition_id"), FINAL_EDITION)
            common.update(
                artifact_kind=native["media_type"],
                build_receipt=native.get("build_receipt_id") or "native_r014_artifact_record",
                bytes=native.get("bytes"),
                edition_id=artifact_edition,
                locale=native["locale"],
                manifest_sha256=native["sha256"] if native.get("file_manifest") else None,
                public_uri=public_uri_by_sha.get(native.get("sha256")),
                sha256=native.get("sha256"),
                toolchain_id=native.get("toolchain") or "native_r014_artifact_record",
                tree_sha256=None,
            )
        else:
            raise ValueError(f"unhandled native class: {entity_class}")
        if common["id"] != id_map[native["record_id"]]:
            raise ValueError(f"identity derivation mismatch: {native['record_id']}")
        add(table, common)

    if unbound_term_count:
        add(
            "concepts",
            base(
                "concept",
                unbound_term_concept_key,
                manifest["generated_at"],
                concept_key="r014-technical-unbound-term-concept",
                concept_scheme="adapter-technical-placeholder",
                definition_segment_id=None,
                parent_concept_id=None,
                extensions={
                    DERIVED_EXTENSION: {
                        "purpose": "Required common-schema binding for native term records whose concept_id is explicitly null; this is not a mathematical taxonomy claim.",
                        "native_unbound_term_count": unbound_term_count,
                    }
                },
            ),
        )

    # Bind every exact LaTeX locator file to a common file and revision.
    locator_paths = sorted(
        {
            locator["path"]
            for native in records
            if native["entity_class"] == "segment"
            for locator in (native.get("source_locator"), native.get("target_locator"))
            if locator
        }
        | {"source/yaintt-id.tex"}
    )
    file_revision_by_path: dict[str, str] = {}
    source_revision_id: str | None = None

    def edition_for_path(relative: str) -> str:
        if relative == "authority/downloads/yaintt.tex":
            return source_edition_id
        if relative == "source/yaintt-id.tex":
            return final_edition_id
        match = re.search(r"boundary(\d+)(?:-r2)?/yaintt-id\.tex$", relative)
        if not match:
            raise ValueError(f"cannot bind locator path to edition: {relative}")
        boundary = match.group(1)
        native_edition = f"ttp.r014.edition.id-id.boundary{boundary}"
        if "boundary28-r2" in relative:
            native_edition = "ttp.r014.edition.id-id.boundary28-r2"
        return mapped(native_edition)

    for relative in locator_paths:
        path = root / relative
        data = path.read_bytes()
        file_key = f"yaintt:locator-file:{relative}"
        file_id = add(
            "files",
            base(
                "file",
                file_key,
                manifest["generated_at"],
                canonical_path=relative,
                media_type="text/x-tex",
                parse_mode="latex",
                resource_id=resource_id,
                role=(
                    "source_authority"
                    if relative.startswith("authority/")
                    else "current_translation_source"
                    if relative == "source/yaintt-id.tex"
                    else "translation_boundary_snapshot"
                ),
                extensions={DERIVED_EXTENSION: {"source_path": relative}},
            ),
        )
        revision_key = f"yaintt:locator-file-revision:{relative}:{sha256_bytes(data)}"
        revision_id = rid("file_revision", revision_key)
        if relative == "authority/downloads/yaintt.tex":
            source_revision_id = revision_id
        file_revision_by_path[relative] = revision_id
        add(
            "file_revisions",
            base(
                "file_revision",
                revision_key,
                manifest["generated_at"],
                actual_path=relative,
                bytes=len(data),
                edition_id=edition_for_path(relative),
                file_id=file_id,
                generated=not relative.startswith("authority/"),
                git_blob_sha1=git_blob_sha1(data),
                sha256=sha256_bytes(data),
                source_revision_id=None,
                extensions={DERIVED_EXTENSION: {"source_path": relative}},
            ),
        )
    if source_revision_id is None:
        raise ValueError("source authority file revision was not created")
    for revision in tables["file_revisions"]:
        if revision["actual_path"] != "authority/downloads/yaintt.tex":
            revision["source_revision_id"] = source_revision_id

    # Expose source and target text separately and attach strict LaTeX profiles.
    profile_count = 0
    source_variant_count = 0
    target_variant_count = 0
    raw_slice_exact_payload_count = 0
    for native in (record for record in records if record["entity_class"] == "segment"):
        expressions = {expression["source_or_target"]: expression for expression in native["expressions"]}
        source_variant_id_for_target = None
        for role in ("source", "target"):
            expression = expressions.get(role)
            if expression is None:
                continue
            locator = native.get(f"{role}_locator")
            if locator is None:
                raise ValueError(f"expression lacks locator: {expression['expression_id']}")
            relative = locator["path"]
            start, end, raw_sha = line_byte_range(root / relative, int(locator["start_line"]), int(locator["end_line"]))
            profile = {
                "active_source_path": relative,
                "authority_file_revision_id": file_revision_by_path[relative],
                "authority_path": relative,
                "format_profile": "latex",
                "identity_strategy": "target_only_localized_correction" if role == "target" and "source" not in expressions else "source_order",
                "profile_version": "1.0.0",
                "raw_end_byte": end,
                "raw_slice_sha256": raw_sha,
                "raw_start_byte": start,
            }
            Draft202012Validator(profile_schema, format_checker=FormatChecker()).validate(profile)
            profile_count += 1
            payload = expression["text_latex"]
            if sha256_bytes(payload.encode("utf-8")) != expression["content_sha256"]:
                raise ValueError(f"payload hash mismatch: {expression['expression_id']}")
            raw_slice = (root / relative).read_bytes()[start:end]
            if raw_slice == payload.encode("utf-8"):
                raw_slice_exact_payload_count += 1
            variant_key = f"yaintt:{expression['expression_id']}"
            variant_id = rid("segment_variant", variant_key)
            if role == "source":
                source_variant_id_for_target = variant_id
                source_variant_count += 1
            else:
                target_variant_count += 1
            add(
                "segment_variants",
                base(
                    "segment_variant",
                    variant_key,
                    native["created_at"],
                    edition_id=source_edition_id if role == "source" else mapped(native["edition_id"]),
                    format="text/x-tex",
                    locale=expression["locale"],
                    payload=payload,
                    payload_sha256=expression["content_sha256"],
                    rights_id=source_rights_id if role == "source" else mapped(native["rights_id"]),
                    role="source" if role == "source" else "translation",
                    segment_id=mapped(native["record_id"]),
                    source_variant_id=None if role == "source" else source_variant_id_for_target,
                    translation_state=expression["state"],
                    extensions={
                        PROFILE_EXTENSION: profile,
                        DERIVED_EXTENSION: {
                            "native_expression_id": expression["expression_id"],
                            "native_segment_id": native["record_id"],
                            "raw_slice_is_exact_payload": raw_slice == payload.encode("utf-8"),
                        },
                    },
                ),
            )

    # Make accepted and rejected native glossary variants queryable.
    term_variant_count = 0
    for native in (record for record in records if record["entity_class"] == "term"):
        for variant_kind, values in (("accepted_variant", native.get("variants") or []), ("rejected_form", native.get("rejected_forms") or [])):
            for ordinal, form in enumerate(values, start=1):
                key = f"yaintt:{native['record_id']}:{variant_kind}:{ordinal}:{form}"
                add(
                    "term_variants",
                    base(
                        "term_variant",
                        key,
                        native["created_at"],
                        form=form,
                        locale=native["locale"],
                        rationale=f"Native R014 {variant_kind.replace('_', ' ')}",
                        term_id=mapped(native["record_id"]),
                        variant_kind=variant_kind,
                        extensions={DERIVED_EXTENSION: {"native_term_id": native["record_id"], "native_ordinal": ordinal}},
                    ),
                )
                term_variant_count += 1

    # Assets already carry exact bytes and SHA-256; revisions expose those facts.
    for native in (record for record in records if record["entity_class"] == "asset"):
        key = f"yaintt:{native['record_id']}:revision:{native['sha256']}"
        add(
            "asset_revisions",
            base(
                "asset_revision",
                key,
                native["created_at"],
                asset_id=mapped(native["record_id"]),
                bytes=int(native["bytes"]),
                edition_id=mapped(native.get("edition_id"), SOURCE_EDITION),
                file_revision_id=None,
                sha256=native["sha256"],
                source_asset_revision_id=None,
                extensions={DERIVED_EXTENSION: {"native_asset_id": native["record_id"], "source_path": native["path"]}},
            ),
        )

    # The complete 548-unit topology is one independently movable module.
    module_key = "yaintt:r014:complete-book-module"
    module_id = add(
        "modules",
        base(
            "module",
            module_key,
            manifest["generated_at"],
            closure_profile="all 548 native R014 units in the complete boundary28-final edition",
            edition_id=final_edition_id,
            locale="id-ID",
            manifest_sha256=sha256_file(root / "backend" / "MANIFEST.json"),
            module_version="r014-boundary28-final",
            root_unit_id=root_unit_id,
            extensions={DERIVED_EXTENSION: {"native_work_id": resource_native["record_id"]}},
        ),
    )
    unit_records = sorted(
        (record for record in records if record["entity_class"] == "unit"),
        key=lambda record: (record.get("path") or "", record.get("order_key") or "", record["record_id"]),
    )
    for ordinal, native in enumerate(unit_records, start=1):
        key = f"yaintt:r014:complete-book-member:{native['record_id']}"
        add(
            "module_members",
            base(
                "module_member",
                key,
                manifest["generated_at"],
                entity_id=mapped(native["record_id"]),
                inclusion_reason="Member of the native complete-book unit topology",
                module_id=module_id,
                order_path=native.get("path") or native.get("order_key") or f"{ordinal:04d}",
                required=True,
                role=native["unit_type"],
                extensions={DERIVED_EXTENSION: {"native_unit_id": native["record_id"], "native_order": native["order"]}},
            ),
        )

    # Preserve the documented deterministic final-reader build as a common recipe.
    final_source_path = "source/yaintt-id.tex"
    final_pdf_native = next(
        record
        for record in records
        if record["entity_class"] == "artifact" and record["path"] == "output/YAINTT_ID.pdf"
    )
    build_md = root / "BUILD.md"
    build_key = "yaintt:r014:boundary28-final-reader-build"
    add(
        "build_recipes",
        base(
            "build_recipe",
            build_key,
            manifest["generated_at"],
            command=[
                "latex -interaction=nonstopmode -halt-on-error -no-shell-escape yaintt-id.tex",
                "bibtex yaintt-id",
                "latex -interaction=nonstopmode -halt-on-error -no-shell-escape yaintt-id.tex",
                "latex -interaction=nonstopmode -halt-on-error -no-shell-escape yaintt-id.tex",
                "makeindex yaintt-id.idx",
                "latex -interaction=nonstopmode -halt-on-error -no-shell-escape yaintt-id.tex",
                "latex -interaction=nonstopmode -halt-on-error -no-shell-escape yaintt-id.tex",
                "dvips -o yaintt-id.ps yaintt-id.dvi",
                "ps2pdf yaintt-id.ps yaintt-id.raw.pdf",
                "python scripts/finalize_pdf_deterministic.py source/yaintt-id.raw.pdf YAINTT_ID.pdf --source-sha256 b1dd2926dc8bfdb84c6a3b4605490a8d96b14c44d89653867160d701fa0f17db --boundary-id boundary28-final --expected-pages 138",
            ],
            edition_id=final_edition_id,
            environment={"source": "BUILD.md", "TEXINPUTS": "source/assets", "normalizer": "scripts/finalize_pdf_deterministic.py"},
            input_ids=[file_revision_by_path[final_source_path]],
            name="Build the deterministic complete Indonesian reader",
            output_ids=[mapped(final_pdf_native["record_id"])],
            resource_id=resource_id,
            verification={"bytes": final_pdf_native["bytes"], "pages": final_pdf_native["pages"], "sha256": final_pdf_native["sha256"]},
            working_directory="source",
            extensions={DERIVED_EXTENSION: {"build_md_bytes": build_md.stat().st_size, "build_md_sha256": sha256_file(build_md)}},
        ),
    )

    artifact_by_sha = {
        native["sha256"]: mapped(native["record_id"])
        for native in records
        if native["entity_class"] == "artifact" and native.get("sha256")
    }

    def public_artifact_ids(items: list[dict]) -> list[str]:
        return sorted({artifact_by_sha[item["sha256"]] for item in items if item.get("sha256") in artifact_by_sha})

    codeload = github["anonymous_codeload_archives"][release_commit]
    release_snapshots = [
        {
            "key": "github-v1.0.0",
            "archive_sha256": codeload["archive_sha256"],
            "artifact_ids": public_artifact_ids(github["assets"]),
            "commit_sha": release_commit,
            "publication_uri": github["release_url"],
            "release_version": github["tag"],
            "snapshot_kind": "public_github_release",
            "tree_sha": github.get("tree_sha"),
        },
        {
            "key": "zenodo-22052196",
            "archive_sha256": None,
            "artifact_ids": public_artifact_ids(publication["zenodo"]["files"]),
            "commit_sha": None,
            "publication_uri": publication["zenodo"]["record_url"],
            "release_version": publication["version"],
            "snapshot_kind": "public_zenodo_version",
            "tree_sha": None,
        },
        {
            "key": "figshare-33314736-v2",
            "archive_sha256": None,
            "artifact_ids": public_artifact_ids(figshare["figshare"]["files"]),
            "commit_sha": None,
            "publication_uri": figshare["figshare"]["article"]["url"],
            "release_version": f"v{figshare['figshare']['article']['version']}",
            "snapshot_kind": "public_figshare_book_version",
            "tree_sha": None,
        },
    ]
    for snapshot in release_snapshots:
        key = f"yaintt:r014:release:{snapshot['key']}"
        add(
            "release_snapshots",
            base(
                "release_snapshot",
                key,
                manifest["generated_at"],
                archive_sha256=snapshot["archive_sha256"],
                artifact_ids=snapshot["artifact_ids"],
                commit_sha=snapshot["commit_sha"],
                edition_id=final_edition_id,
                immutable=True,
                publication_uri=snapshot["publication_uri"],
                release_date=(
                    figshare["figshare"]["article"]["published_date"][:10]
                    if snapshot["snapshot_kind"] == "public_figshare_book_version"
                    else release_date
                ),
                release_version=snapshot["release_version"],
                snapshot_kind=snapshot["snapshot_kind"],
                tree_sha=snapshot["tree_sha"],
                status="published_verified",
                extensions={DERIVED_EXTENSION: {"native_publication_receipt": "publication/PUBLICATION_RECEIPT.json"}},
            ),
        )

    for rows in tables.values():
        rows.sort(key=lambda record: record["id"])
    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rid("dataset", "yaintt-id:r014-complete"),
        "dataset_version": "r014-1.0.0+interlanguage-v1",
        "tables": dict(sorted(tables.items())),
    }

    # A direct record can be reversed by extracting its frozen native extension.
    recovered = []
    for table, _ in DIRECT_TYPES.values():
        for record in tables[table]:
            payload = record.get("extensions", {}).get(NATIVE_EXTENSION)
            if payload is not None:
                native = payload["native_record"]
                if sha256_bytes(canonical_bytes(native)) != payload["native_record_sha256"]:
                    raise ValueError(f"native extension checksum mismatch: {payload['native_record_id']}")
                if native["record_id"] != payload["native_record_id"]:
                    raise ValueError("native extension identity mismatch")
                recovered.append(native)
    if sorted(recovered, key=lambda record: record["record_id"]) != sorted(records, key=lambda record: record["record_id"]):
        raise ValueError("exact native reverse extraction failed")

    id_mapping_payload = b"".join(
        f"{native_id}\t{id_map[native_id]}\n".encode("utf-8") for native_id in sorted(id_map)
    )
    diagnostics = {
        "direct_native_records": len(recovered),
        "exact_reverse_extraction": len(recovered),
        "native_id_mapping_bytes": len(id_mapping_payload),
        "native_id_mapping_sha256": sha256_bytes(id_mapping_payload),
        "source_segment_variants": source_variant_count,
        "target_segment_variants": target_variant_count,
        "strict_latex_profiles": profile_count,
        "raw_slice_exact_payload_count": raw_slice_exact_payload_count,
        "term_variants": term_variant_count,
        "native_terms_with_explicit_null_concept_binding": unbound_term_count,
        "asset_revisions": len(tables["asset_revisions"]),
        "locator_files": len(tables["files"]),
        "locator_file_revisions": len(tables["file_revisions"]),
        "module_units": len(tables["module_members"]),
        "release_snapshots": len(tables["release_snapshots"]),
    }
    return backend, diagnostics


def validate_backend(backend: dict, schema: dict, profile_schema: dict) -> dict:
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(backend)
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

    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    profiles = 0
    profile_revisions = []
    for record in records:
        profile = record.get("extensions", {}).get(PROFILE_EXTENSION)
        if profile is not None:
            profile_validator.validate(profile)
            profiles += 1
            profile_revisions.append(profile["authority_file_revision_id"])
    if any(value not in known for value in profile_revisions):
        raise ValueError("source-profile authority revision does not close")

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
        "strict_source_profiles": profiles,
        "virtual_records_jsonl_bytes": len(payload),
        "virtual_records_jsonl_sha256": sha256_bytes(payload),
    }


def receipt_artifact(root: Path, path: Path, status: str, **fields: Any) -> dict:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "status": status,
        **fields,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-profile-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    root = args.corpus_root.resolve()
    manifest_path = root / "backend" / "MANIFEST.json"
    records_path = root / "backend" / "records.jsonl"
    catalog_path = root / "backend" / "catalog.json"
    native_schema_path = root / "backend" / "schemas" / "record.schema.json"
    publication_path = root / "publication" / "PUBLICATION_RECEIPT.json"
    figshare_path = root / "publication" / "FIGSHARE_PUBLICATION_RECEIPT.json"
    backend_qa_path = root / "qa" / "BACKEND_QA.json"
    backend_determinism_path = root / "qa" / "BACKEND_DETERMINISM.json"
    terminology_path = root / "qa" / "INDONESIAN_TERMINOLOGY_QA.json"
    terminology_publication_path = root / "qa" / "INDONESIAN_TERMINOLOGY_QA_PUBLICATION.json"
    cursor_path = root / "00_control" / "CURRENT_CURSOR.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    native_schema = json.loads(native_schema_path.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    profile_schema = json.loads(args.source_profile_schema.read_text(encoding="utf-8"))
    publication = json.loads(publication_path.read_text(encoding="utf-8"))
    figshare = json.loads(figshare_path.read_text(encoding="utf-8"))
    backend_qa = json.loads(backend_qa_path.read_text(encoding="utf-8"))
    backend_determinism = json.loads(backend_determinism_path.read_text(encoding="utf-8"))
    terminology = json.loads(terminology_path.read_text(encoding="utf-8"))
    terminology_publication = json.loads(terminology_publication_path.read_text(encoding="utf-8"))
    cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(native_schema)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(profile_schema)

    first_records, first_lines = read_records(records_path)
    native_diagnostics = verify_native(root, first_records, first_lines, manifest, native_schema)
    if cursor["backend"]["records"] != len(first_records) or cursor["backend"]["sha256"] != sha256_file(records_path):
        raise ValueError("current cursor does not bind the native backend")
    if publication.get("status") != "public_bytes_verified":
        raise ValueError("primary public release receipt is not verified")
    if not figshare.get("figshare", {}).get("anonymous_byte_readback", {}).get("verified"):
        raise ValueError("Figshare anonymous byte readback is not verified")
    if (
        backend_qa.get("result") != "pass"
        or backend_qa.get("failures") != []
        or backend_qa.get("schema_validated_records") != len(first_records)
        or backend_qa.get("csv_projection_count") != manifest.get("csv_projection_count")
        or not backend_qa.get("xlsx", {}).get("csv_cell_matrices_equal")
        or backend_qa.get("xlsx", {}).get("formula_errors") != 0
    ):
        raise ValueError("native backend QA does not prove schema/CSV/XLSX closure")
    if (
        backend_determinism.get("result") != "pass"
        or backend_determinism.get("mismatches") != []
        or backend_determinism.get("final_records", {}).get("count") != len(first_records)
        or backend_determinism.get("final_records", {}).get("sha256") != sha256_file(records_path)
        or len(backend_determinism.get("runs", [])) != 2
    ):
        raise ValueError("native backend determinism receipt does not close")
    if not terminology.get("result", {}).get("human_and_source_credits_preserved"):
        raise ValueError("terminology QA does not prove credit preservation")
    if terminology_publication.get("status") != "github_public_anonymous_readback_verified":
        raise ValueError("terminology QA public readback is not verified")

    first, first_diagnostics = build_backend(root, first_records, manifest, schema, profile_schema, publication, figshare)
    first_validation = validate_backend(first, schema, profile_schema)

    second_records, second_lines = read_records(records_path)
    if second_lines != first_lines:
        raise ValueError("native JSONL changed between independent assemblies")
    second, second_diagnostics = build_backend(root, second_records, manifest, schema, profile_schema, publication, figshare)
    second_validation = validate_backend(second, schema, profile_schema)
    first_hash = sha256_bytes(canonical_bytes(first))
    second_hash = sha256_bytes(canonical_bytes(second))
    if first_hash != second_hash or first_diagnostics != second_diagnostics or first_validation != second_validation:
        raise ValueError("two independent common-backend assemblies are not byte-identical")

    public_artifacts = [
        receipt_artifact(
            root,
            backend_qa_path,
            backend_qa["result"],
            csv_projection_count=backend_qa["csv_projection_count"],
            xlsx_csv_cell_matrices_equal=backend_qa["xlsx"]["csv_cell_matrices_equal"],
            schema_validated_records=backend_qa["schema_validated_records"],
        ),
        receipt_artifact(
            root,
            backend_determinism_path,
            backend_determinism["result"],
            independent_native_runs=len(backend_determinism["runs"]),
            compared_backend_files=backend_determinism["compared_surfaces"]["backend"]["file_count"],
            mismatch_count=len(backend_determinism["mismatches"]),
        ),
        receipt_artifact(
            root,
            publication_path,
            publication["status"],
            github_repository=publication["github"]["repository_url"],
            github_commit=publication["github"]["commit_sha"],
            github_release=publication["github"]["release_url"],
            zenodo_record=publication["zenodo"]["record_url"],
            zenodo_version_doi=publication["zenodo"]["version_doi"],
            zenodo_concept_doi=publication["zenodo"]["concept_doi"],
        ),
        receipt_artifact(
            root,
            figshare_path,
            figshare["status"],
            figshare_article=figshare["figshare"]["article"]["url"],
            figshare_version_doi=figshare["figshare"]["article"]["doi"],
            anonymous_files_verified=figshare["figshare"]["anonymous_byte_readback"]["file_count"],
        ),
        receipt_artifact(
            root,
            terminology_path,
            terminology["status"],
            source=terminology["fallback_source"]["title"],
            pages=terminology["fallback_source"]["pages"],
            preferred_terms_changed=terminology["result"]["preferred_terms_changed"],
        ),
        receipt_artifact(
            root,
            terminology_publication_path,
            terminology_publication["status"],
            github_commit=terminology_publication["commit"],
            public_files_verified=terminology_publication["anonymous_verification"]["file_count"],
        ),
    ]

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "yaintt-r014-id-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-additive-native-backend-adapter",
        "source": {
            "dataset_id": manifest["schema"],
            "dataset_version": manifest["schema_version"],
            "work_id": cursor["work_id"],
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": SOURCE_SCHEMA_VERSION,
            "manifest_path": manifest_path.relative_to(root).as_posix(),
            "manifest_bytes": manifest_path.stat().st_size,
            "manifest_sha256": sha256_file(manifest_path),
            "records_path": records_path.relative_to(root).as_posix(),
            "records_bytes": records_path.stat().st_size,
            "records_sha256": sha256_file(records_path),
            "catalog_path": catalog_path.relative_to(root).as_posix(),
            "catalog_bytes": catalog_path.stat().st_size,
            "catalog_sha256": sha256_file(catalog_path),
            "record_count": len(first_records),
            "backend_qa_path": backend_qa_path.relative_to(root).as_posix(),
            "backend_qa_bytes": backend_qa_path.stat().st_size,
            "backend_qa_sha256": sha256_file(backend_qa_path),
            "backend_determinism_path": backend_determinism_path.relative_to(root).as_posix(),
            "backend_determinism_bytes": backend_determinism_path.stat().st_size,
            "backend_determinism_sha256": sha256_file(backend_determinism_path),
            "authority_sha256": manifest["authority_sha256"],
            "target_sha256": manifest["target_sha256"],
            "reader": manifest["canonical_reader"],
        },
        "target": {
            "dataset_id": first["dataset_id"],
            "dataset_version": first["dataset_version"],
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "schema_path": "schemas/backend-v1.schema.json",
            "schema_bytes": args.schema.stat().st_size,
            "schema_sha256": sha256_file(args.schema),
            "source_profile_schema_path": "schemas/profiles/source-format-profile-v1.schema.json",
            "source_profile_schema_bytes": args.source_profile_schema.stat().st_size,
            "source_profile_schema_sha256": sha256_file(args.source_profile_schema),
            "record_count": first_validation["record_count"],
            "table_count": first_validation["table_count"],
            "nonempty_table_count": first_validation["nonempty_table_count"],
            "virtual_records_jsonl_bytes": first_validation["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
            "canonical_backend_sha256": first_hash,
        },
        "coverage": {
            **native_diagnostics,
            **first_diagnostics,
            "reader_pages": manifest["canonical_reader"]["pdf"]["pages"],
            "reader_bytes": manifest["canonical_reader"]["pdf"]["bytes"],
            "reader_sha256": manifest["canonical_reader"]["pdf"]["sha256"],
            "indonesian_terminology_qa": terminology["status"],
            "model_provenance_present": terminology["result"]["provenance_model_identification"],
            "source_and_human_credits_preserved": terminology["result"]["human_and_source_credits_preserved"],
        },
        "transformation": {
            "native_records_modified": 0,
            "native_files_modified": 0,
            "native_ids_preserved_in_reversible_extensions": len(first_records),
            "native_payload_fields_preserved": "all fields of all 5,272 native records",
            "source_segment_payload_bytes_changed": 0,
            "target_segment_payload_bytes_changed": 0,
            "common_ids_added": first_validation["record_count"],
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "direct_identity_key": "native entity class plus exact native record_id",
            "derived_records_materialized": False,
        },
        "validation": {
            "result": "pass",
            "native_manifest_filename_size_sha256": "pass",
            "native_record_schema_rows": len(first_records),
            "native_catalog_exact_record_equivalence": "pass",
            "native_csv_projection_count": backend_qa["csv_projection_count"],
            "native_xlsx_csv_cell_matrices_equal": backend_qa["xlsx"]["csv_cell_matrices_equal"],
            "native_two_clean_full_surface_replays": len(backend_determinism["runs"]),
            "native_global_id_uniqueness": "pass",
            "native_foreign_key_closure": "pass",
            "native_asset_and_artifact_closure": "pass",
            "exact_native_reverse_extraction": len(first_records),
            "strict_common_backend_schema": "pass",
            "strict_source_profile_schema": "pass",
            "common_global_id_uniqueness": "pass",
            "common_foreign_key_closure": "pass",
            "two_independent_assemblies": "byte-identical",
            "first_canonical_backend_sha256": first_hash,
            "second_canonical_backend_sha256": second_hash,
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The complete admitted native package plus this deterministic reversible adapter reconstruct the strict common backend twice without a redundant materialized copy.",
            "script_path": "scripts/migrate-yaintt-backend-v1.py",
        },
        "public_artifacts": public_artifacts,
        "credentials_recorded": False,
    }
    write_json(args.output_receipt, receipt)
    print(
        canonical(
            {
                "result": "pass",
                "native_records": len(first_records),
                "target_records": first_validation["record_count"],
                "tables": first_validation["table_count"],
                "virtual_records_jsonl_bytes": first_validation["virtual_records_jsonl_bytes"],
                "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
                "canonical_backend_sha256": first_hash,
                "receipt": args.output_receipt.resolve().as_posix(),
                "receipt_sha256": sha256_file(args.output_receipt),
            }
        )
    )


if __name__ == "__main__":
    main()
