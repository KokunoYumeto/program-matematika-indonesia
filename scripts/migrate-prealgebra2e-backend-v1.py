#!/usr/bin/env python3
"""Stream the frozen R001 Prealgebra 2e backend into common-backend v1.

The owner lane is immutable.  This adapter validates the complete native
inventory, preserves every native UUIDv5 and payload in a reversible extension,
and computes two byte-identical virtual common-backend assemblies.  It writes
only a bounded migration receipt; it never materializes the roughly 1.84 GB
native backend or the larger normalized stream in the central repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import re
import urllib.parse
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
WORKFLOW = "program-matematika-indonesia/prealgebra2e-r001-v1-migrator-1.0.0"
NATIVE_EXTENSION = "interlanguage.prealgebra2e-native"
DERIVED_EXTENSION = "interlanguage.prealgebra2e-derived"
PROFILE_EXTENSION = "interlanguage.source-profile"
COLLXML_EXTENSION = "interlanguage.prealgebra2e-collxml-binding"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


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


def strip_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    raw = value.removeprefix("sha256:")
    if not re.fullmatch(r"[0-9a-f]{64}", raw):
        raise ValueError(f"invalid SHA-256 value: {value}")
    return raw


def git_blob_sha1_from_digest_only() -> None:
    """Document that a Git blob hash cannot be inferred from only SHA-256/size."""
    return None


def rid(namespace: uuid.UUID, record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(namespace, f'{record_type}|{stable_key}')}"


def portable(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def iter_urns(value: Any, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
    if isinstance(value, str) and value.startswith("urn:uuid:"):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_urns(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_urns(child, path + (str(index),))


def verify_uuid5(value: str) -> None:
    if not value.startswith("urn:uuid:"):
        raise ValueError(f"record ID is not a UUID URN: {value}")
    parsed = uuid.UUID(value.removeprefix("urn:uuid:"))
    if parsed.version != 5:
        raise ValueError(f"record ID is not UUIDv5: {value}")


def file_fact(path: Path, relative: str) -> dict[str, Any]:
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def iter_native(path: Path, expected_type: str) -> Iterator[tuple[str, dict[str, Any], int, bytes]]:
    previous_id: str | None = None
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.endswith(b"\n") or raw.endswith(b"\r\n"):
                raise ValueError(f"native JSONL must use a single LF terminator: {path}:{line_number}")
            try:
                value = json.loads(raw[:-1].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid native JSONL: {path}:{line_number}: {exc}") from exc
            if canonical_bytes(value) + b"\n" != raw:
                raise ValueError(f"native JSONL is not canonical: {path}:{line_number}")
            if value.get("record_type") != expected_type:
                raise ValueError(
                    f"native record type mismatch: {path}:{line_number}: "
                    f"{value.get('record_type')} != {expected_type}"
                )
            record_id = value.get("id")
            if not isinstance(record_id, str):
                raise ValueError(f"native record lacks string ID: {path}:{line_number}")
            if previous_id is not None and record_id <= previous_id:
                raise ValueError(f"native view is not strictly ID-sorted: {path}:{line_number}")
            previous_id = record_id
            yield record_id, value, line_number, raw


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def module_from_locator(locator: str | None) -> str | None:
    if not locator:
        return None
    match = re.search(r"(?:^|/)modules/(m\d+)/index\.cnxml", locator)
    return match.group(1) if match else None


def xpath_from_locator(locator: str, module_id: str, fallback: str | None) -> str:
    marker = f"modules/{module_id}/index.cnxml"
    if marker not in locator:
        return fallback or ""
    tail = locator.split(marker, 1)[1]
    if not tail or tail.startswith("#"):
        return fallback or tail
    return tail if tail.startswith("/") else f"/{tail}"


def collection_xpath_from_locator(locator: str, collection_path: str) -> str:
    marker = f"{collection_path}/"
    if not locator.startswith(marker):
        raise ValueError(f"locator is outside the collection XML authority: {locator}")
    structural_xpath = locator[len(collection_path) :]
    if not structural_xpath.startswith("/"):
        raise ValueError(f"collection XML locator has no absolute structural path: {locator}")
    return structural_xpath


def last_ordinal(path: str | None) -> int:
    matches = re.findall(r"\[(\d+)\]", path or "")
    return int(matches[-1]) if matches else 0


def native_extension(
    native: dict[str, Any], view_path: str, line_number: int, raw: bytes
) -> dict[str, Any]:
    return {
        NATIVE_EXTENSION: {
            "native_record": native,
            "native_record_id": native["id"],
            "native_record_path": view_path,
            "native_line_number": line_number,
            "native_line_sha256": sha256_bytes(raw),
            "source_schema": native["schema_name"],
            "source_schema_version": native["schema_version"],
        }
    }


def direct_base(
    native: dict[str, Any],
    record_type: str,
    view_path: str,
    line_number: int,
    raw: bytes,
    default_time: str,
) -> dict[str, Any]:
    return {
        "id": native["id"],
        "record_type": record_type,
        "recorded_at": native.get("event_time") or default_time,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": f"prealgebra2e:{native['record_type']}:{native['id']}",
        "status": native.get("status") or "active",
        "supersedes_id": native.get("supersedes"),
        "workflow_id": WORKFLOW,
        "extensions": native_extension(native, view_path, line_number, raw),
    }


def derived_base(
    namespace: uuid.UUID,
    record_type: str,
    stable_key: str,
    recorded_at: str,
    **fields: Any,
) -> dict[str, Any]:
    return {
        "id": rid(namespace, record_type, stable_key),
        "record_type": record_type,
        "recorded_at": recorded_at,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": "active",
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def verify_frozen_authority(corpus_root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    facts: dict[str, dict[str, Any]] = {}
    for label in ("admission", "handoff", "backend_manifest"):
        expected = profile["frozen_authority"][label]
        path = corpus_root / expected["path"]
        if not path.is_file():
            raise ValueError(f"missing frozen authority file: {expected['path']}")
        actual = file_fact(path, expected["path"])
        if actual != expected:
            raise ValueError(f"frozen authority mismatch for {label}: {actual} != {expected}")
        facts[label] = actual

    admission_path = corpus_root / profile["frozen_authority"]["admission"]["path"]
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    handoff_path = corpus_root / profile["frozen_authority"]["handoff"]["path"]
    handoff = handoff_path.read_text(encoding="utf-8")
    backend_root = corpus_root / profile["source"]["backend_root"]
    manifest_path = backend_root / profile["source"]["manifest_path"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if admission["schema"] != "interlanguage-central-hub-admission":
        raise ValueError("unexpected owner admission schema")
    if admission["ownership"]["owned_course_ids"] != [profile["course_role"]]:
        raise ValueError("owner admission course scope is not exactly R001")
    if admission["ownership"]["owned_curriculum_bands"] != [profile["curriculum_band"]]:
        raise ValueError("owner admission curriculum scope is not exactly A00")
    if admission["ownership"]["excluded_sibling_corpora"] != profile["no_overlap"]["excluded_corpora"]:
        raise ValueError("owner admission sibling exclusion set changed")
    handoff_scope_tokens = [
        profile["course_role"],
        profile["curriculum_band"],
        *(name.removeprefix("OpenStax ") for name in profile["no_overlap"]["excluded_corpora"]),
    ]
    for token in handoff_scope_tokens:
        if token not in handoff:
            raise ValueError(f"owner handoff omits required scope token: {token}")

    expected = profile["expected"]
    backend_admission = admission["accepted_artifacts"]["backend"]
    if (
        backend_admission["schema_version"] != expected["owner_backend_schema_version"]
        or backend_admission["records"] != expected["native_records"]
        or backend_admission["files"] != expected["native_files_including_manifest"]
        or backend_admission["bytes"] != expected["native_bytes_including_manifest"]
        or backend_admission["manifest_sha256"] != facts["backend_manifest"]["sha256"]
        or backend_admission["canonical_tree_sha256"]
        != profile["frozen_authority"]["accepted_backend_tree_sha256"]
        or backend_admission["input_fingerprint_sha256"]
        != profile["frozen_authority"]["accepted_input_fingerprint_sha256"]
    ):
        raise ValueError("owner admission backend facts do not match the adapter profile")
    if manifest["schema_name"] != expected["native_schema_name"] or manifest["schema_version"] != expected["native_schema_version"]:
        raise ValueError("native manifest schema identity changed")
    if manifest["course_role"] != profile["course_role"] or manifest["locale"] != profile["target_locale"]:
        raise ValueError("native manifest course/locale scope changed")
    if manifest["records_total"] != expected["native_records"] or manifest["module_count"] != expected["module_references"]:
        raise ValueError("native manifest record/module count changed")

    collection_files: dict[str, dict[str, Any]] = {}
    for label, manifest_key in (
        ("source_collection", "source_collection"),
        ("target_collection", "localized_collection"),
    ):
        declared = manifest[manifest_key]
        path = corpus_root / declared["path_locator"]
        if not path.is_file():
            raise ValueError(f"live collection XML authority is absent: {declared['path_locator']}")
        actual = {
            "path": declared["path_locator"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        expected_collection = {
            "path": declared["path_locator"],
            "bytes": declared["bytes"],
            "sha256": strip_sha256(declared["sha256"]),
        }
        if actual != expected_collection:
            raise ValueError(f"live collection XML authority mismatch: {actual} != {expected_collection}")
        collection_files[label] = actual

    inventory = []
    declared_bytes = 0
    for entry in manifest["files"]:
        path = backend_root / entry["path"]
        if not path.is_file():
            raise ValueError(f"native manifest member is absent: {entry['path']}")
        actual = {
            "path": entry["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        declared = {
            "path": entry["path"],
            "bytes": entry["bytes"],
            "sha256": strip_sha256(entry["sha256"]),
        }
        if actual != declared:
            raise ValueError(f"native manifest member mismatch: {actual} != {declared}")
        inventory.append(actual)
        declared_bytes += actual["bytes"]
    if len(inventory) + 1 != expected["native_files_including_manifest"]:
        raise ValueError("native manifest inventory file count changed")
    if declared_bytes + manifest_path.stat().st_size != expected["native_bytes_including_manifest"]:
        raise ValueError("native manifest inventory byte count changed")

    source_witness_path = backend_root / profile["source"]["source_witness_path"]
    target_witness_path = backend_root / profile["source"]["target_witness_path"]
    source_witness = {row["module"]: row for row in load_tsv(source_witness_path)}
    target_witness = {row["module"]: row for row in load_tsv(target_witness_path)}
    modules = {row["module_id"]: row for row in manifest["modules"]}
    if set(source_witness) != set(modules) or set(target_witness) != set(modules):
        raise ValueError("source/target witness module sets do not match the manifest")
    for module_id, row in modules.items():
        source = source_witness[module_id]
        target = target_witness[module_id]
        # The emitted manifest binds module bytes/hashes and the target-witness
        # table binds the portable path.  Keep that witnessed path in the
        # in-memory adapter context; the owner manifest itself remains untouched.
        row["target_locator"] = target["path"]
        if (
            int(source["bytes"]) != row["source_bytes"]
            or source["sha256"] != strip_sha256(row["source_sha256"])
            or int(target["bytes"]) != row["target_bytes"]
            or target["sha256"] != strip_sha256(row["target_sha256"])
        ):
            raise ValueError(f"module witness mismatch: {module_id}")

    inventory_binding = sha256_bytes(canonical_bytes(sorted(inventory, key=lambda item: item["path"])))
    return {
        "admission": admission,
        "handoff": handoff,
        "manifest": manifest,
        "backend_root": backend_root,
        "manifest_path": manifest_path,
        "authority_facts": facts,
        "inventory": inventory,
        "inventory_binding_sha256": inventory_binding,
        "source_witness": source_witness,
        "target_witness": target_witness,
        "modules": modules,
        "collection_files": collection_files,
    }


def verify_native_records(
    authority: dict[str, Any],
    profile: dict[str, Any],
    native_schema: dict[str, Any],
) -> dict[str, Any]:
    backend_root: Path = authority["backend_root"]
    manifest = authority["manifest"]
    validator = Draft202012Validator(native_schema, format_checker=FormatChecker())
    known_ids: set[str] = set()
    referenced_ids: set[str] = set()
    counts: Counter[str] = Counter()
    view_counts: dict[str, int] = {}
    view_line_bytes: dict[str, int] = {}
    segment_meta: dict[str, dict[str, Any]] = {}
    concept_meta: dict[str, dict[str, Any]] = {}
    course_native: dict[str, Any] | None = None
    artifact_by_module: dict[str, dict[str, Any]] = {}
    asset_revision_keys: list[tuple[str, str]] = []
    target_only_localized_units: list[dict[str, Any]] = []
    source_collection_structural_units = 0
    target_collection_structural_occurrences = 0
    source_collection_pairs: dict[str, tuple[str, str, str]] = {}
    target_collection_pairs: dict[str, tuple[str, str, str]] = {}
    collection_segment_ids: set[str] = set()
    source_collection_expression_segment_ids: set[str] = set()
    target_collection_expression_segment_ids: set[str] = set()
    target_only_correction_segment_ids: set[str] = set()
    target_only_correction_expression_segment_ids: set[str] = set()
    external_target_unit_ids: set[str] = set()
    external_target_locators: set[str] = set()
    external_target_source_keys: set[str] = set()
    external_target_content_hashes: set[str] = set()
    external_target_inventory: list[dict[str, str]] = []
    null_concept_terms = 0
    native_validation_count = 0

    for view in profile["source"]["views"]:
        relative = view["path"]
        path = backend_root / relative
        count = 0
        line_bytes = 0
        for record_id, native, line_number, raw in iter_native(path, view["native_record_type"]):
            try:
                validator.validate(native)
            except Exception as exc:
                raise ValueError(f"native schema failure: {relative}:{line_number}: {exc}") from exc
            verify_uuid5(record_id)
            if record_id in known_ids:
                raise ValueError(f"duplicate native ID: {record_id}")
            known_ids.add(record_id)
            for _, value in iter_urns(native):
                referenced_ids.add(value)
            counts[native["record_type"]] += 1
            count += 1
            line_bytes += len(raw)
            native_validation_count += 1

            if native["record_type"] == "segment":
                segment_meta[record_id] = {
                    "owner_unit_id": native["owner_unit_id"],
                    "rights_component_id": native["rights_component_id"],
                    "source_key": native["source_key"],
                    "source_locator": native["source_locator"],
                    "source_module_sha256": strip_sha256(native["source_module_sha256"]),
                }
                source_locator = native.get("source_locator")
                source_collection_locator = manifest["source_collection"]["path_locator"]
                if source_locator and source_locator.startswith(f"{source_collection_locator}/"):
                    collection_segment_ids.add(record_id)
                elif source_locator is None:
                    if (
                        native.get("identity_scope") != "localized_correction"
                        or native.get("locale") != profile["target_locale"]
                        or native.get("source_expression_id") is not None
                        or native.get("source_expression_state") != "absent_in_frozen_source"
                        or not native.get("source_key", "").startswith("segment:cnxml:")
                    ):
                        raise ValueError(f"unrecognized null-source segment class: {record_id}")
                    target_only_correction_segment_ids.add(record_id)
            elif native["record_type"] == "expression":
                segment_id = native["segment_id"]
                segment = segment_meta.get(segment_id)
                if segment is None:
                    raise ValueError(f"expression precedes or lacks segment metadata: {record_id}")
                if native["locale"] == profile["source_locale"]:
                    source_locator = segment.get("source_locator")
                    source_collection_locator = manifest["source_collection"]["path_locator"]
                    if source_locator and source_locator.startswith(f"{source_collection_locator}/"):
                        if segment_id in source_collection_expression_segment_ids:
                            raise ValueError(f"duplicate source collection expression: {segment_id}")
                        source_collection_expression_segment_ids.add(segment_id)
                elif native["locale"] == profile["target_locale"]:
                    target_locator = native.get("target_locator")
                    target_collection_locator = manifest["localized_collection"]["path_locator"]
                    if target_locator and target_locator.startswith(f"{target_collection_locator}/"):
                        if segment_id in target_collection_expression_segment_ids:
                            raise ValueError(f"duplicate target collection expression: {segment_id}")
                        target_collection_expression_segment_ids.add(segment_id)
                    if segment_id in target_only_correction_segment_ids:
                        module_id = module_from_locator(target_locator or "")
                        module = authority["modules"].get(module_id or "")
                        source_key_match = re.match(r"^segment:cnxml:(m\d+)", segment["source_key"])
                        if (
                            native.get("source_expression_id") is not None
                            or module is None
                            or source_key_match is None
                            or source_key_match.group(1) != module_id
                            or strip_sha256(native.get("source_module_sha256"))
                            != strip_sha256(segment["source_module_sha256"])
                            or strip_sha256(native.get("source_module_sha256"))
                            != strip_sha256(module["source_sha256"])
                            or strip_sha256(native.get("target_module_sha256"))
                            != strip_sha256(module["target_sha256"])
                        ):
                            raise ValueError(
                                f"target-only correction expression has invalid CNXML authority: {record_id}"
                            )
                        if segment_id in target_only_correction_expression_segment_ids:
                            raise ValueError(f"duplicate target-only correction expression: {segment_id}")
                        target_only_correction_expression_segment_ids.add(segment_id)
            elif native["record_type"] == "concept":
                concept_meta[record_id] = native
            elif native["record_type"] == "course":
                course_native = native
            elif native["record_type"] == "artifact":
                if native["module_id"] in artifact_by_module:
                    raise ValueError(f"duplicate module artifact: {native['module_id']}")
                artifact_by_module[native["module_id"]] = native
            elif native["record_type"] == "asset":
                asset_revision_keys.append((record_id, strip_sha256(native["sha256"]) or ""))
            elif native["record_type"] == "unit":
                collection_locator = manifest["source_collection"]["path_locator"]
                if native["source_locator"].startswith(f"{collection_locator}/"):
                    source_collection_structural_units += 1
                    if strip_sha256(native["source_collection_sha256"]) != strip_sha256(
                        manifest["source_collection"]["sha256"]
                    ):
                        raise ValueError(f"source collection unit hash binding changed: {record_id}")
                    source_collection_pairs[record_id] = (
                        native["source_key"], native["order_path"], native["unit_type"]
                    )
                elif native["unit_type"] == "external_target":
                    locator = native["source_locator"]
                    source_key = native["source_key"]
                    content_hash = strip_sha256(native["content_hash"])
                    parsed_locator = urllib.parse.urlsplit(locator)
                    if (
                        parsed_locator.scheme != "https"
                        or not parsed_locator.hostname
                        or parsed_locator.username is not None
                        or parsed_locator.password is not None
                        or source_key != f"external-target:{locator}"
                        or content_hash != sha256_bytes(locator.encode("utf-8"))
                        or native.get("order_path") is not None
                        or native.get("parent_id") is not None
                        or native.get("source_local_id") is not None
                    ):
                        raise ValueError(f"external-target unit invariant changed: {record_id}")
                    if locator in external_target_locators:
                        raise ValueError(f"duplicate external-target locator: {locator}")
                    if source_key in external_target_source_keys:
                        raise ValueError(f"duplicate external-target source key: {source_key}")
                    if content_hash in external_target_content_hashes:
                        raise ValueError(f"duplicate external-target content hash: {content_hash}")
                    external_target_unit_ids.add(record_id)
                    external_target_locators.add(locator)
                    external_target_source_keys.add(source_key)
                    external_target_content_hashes.add(content_hash or "")
                    external_target_inventory.append(
                        {
                            "content_hash": native["content_hash"],
                            "id": record_id,
                            "source_key": source_key,
                            "source_locator": locator,
                        }
                    )
            elif native["record_type"] == "localized_unit":
                collection_locator = manifest["localized_collection"]["path_locator"]
                if native["target_locator"].startswith(f"{collection_locator}/"):
                    target_collection_structural_occurrences += 1
                    if (
                        strip_sha256(native["source_module_sha256"])
                        != strip_sha256(manifest["source_collection"]["sha256"])
                        or strip_sha256(native["target_module_sha256"])
                        != strip_sha256(manifest["localized_collection"]["sha256"])
                    ):
                        raise ValueError(f"localized collection occurrence hash binding changed: {record_id}")
                    canonical_unit_id = native.get("canonical_unit_id")
                    if not canonical_unit_id:
                        raise ValueError(f"localized collection occurrence lacks a canonical unit: {record_id}")
                    if canonical_unit_id in target_collection_pairs:
                        raise ValueError(f"duplicate localized collection structural pairing: {canonical_unit_id}")
                    target_collection_pairs[canonical_unit_id] = (
                        native["source_key"], native["order_path"], native["unit_type"]
                    )
                if native.get("canonical_unit_id") is None:
                    target_only_localized_units.append(
                        {
                            "native_occurrence_id": record_id,
                            "localized_unit_state": native["localized_unit_state"],
                            "source_key": native["source_key"],
                            "target_locator": native["target_locator"],
                            "order_path": native.get("order_path"),
                            "resource_id": native["resource_id"],
                            "rights_component_id": native["rights_component_id"],
                            "unit_type": native["unit_type"],
                        }
                    )
            elif native["record_type"] == "term" and native.get("concept_id") is None:
                null_concept_terms += 1

        if count != view["records"]:
            raise ValueError(f"native view count mismatch: {relative}: {count} != {view['records']}")
        if manifest["records_by_view"].get(relative) != count:
            raise ValueError(f"native manifest view count mismatch: {relative}")
        view_counts[relative] = count
        view_line_bytes[relative] = line_bytes

    dangling = sorted(referenced_ids - known_ids)
    if dangling:
        raise ValueError(f"native foreign-key closure failure: {dangling[:10]}")
    if len(known_ids) != profile["expected"]["native_records"]:
        raise ValueError("native global record count changed")
    if dict(sorted(counts.items())) != dict(sorted(manifest["records_by_type"].items())):
        raise ValueError("native record type counts differ from the manifest")
    if manifest["deduplication"]["unique_records"] != len(known_ids):
        raise ValueError("native deduplication count differs from the emitted views")
    if course_native is None:
        raise ValueError("native course record is absent")

    identity = profile["identity"]
    for label in ("source_edition_id", "program_id", "course_id", "resource_id", "default_rights_id", "root_collection_unit_id"):
        if identity[label] not in known_ids:
            raise ValueError(f"profile identity is absent from native records: {label}")
    if len(segment_meta) != profile["expected"]["native_records"] - (
        profile["expected"]["native_records"] - manifest["records_by_type"]["segment"]
    ):
        raise ValueError("native segment metadata count changed")
    if len(concept_meta) != profile["expected"]["concepts"]:
        raise ValueError("native concept metadata count changed")
    if len(target_only_localized_units) != profile["expected"]["target_only_localized_correction_units"]:
        raise ValueError("target-only localized correction unit count changed")
    if any(item["localized_unit_state"] != "target_only_localized_correction" for item in target_only_localized_units):
        raise ValueError("null canonical_unit_id occurs outside the admitted target-only correction class")
    if source_collection_structural_units != profile["expected"]["source_collection_structural_units"]:
        raise ValueError("source collection structural unit count changed")
    if target_collection_structural_occurrences != profile["expected"]["target_collection_structural_occurrences"]:
        raise ValueError("target collection structural occurrence count changed")
    if source_collection_pairs != target_collection_pairs:
        raise ValueError("source/target collection structural pairings changed")
    if len(collection_segment_ids) != profile["expected"]["source_collection_segments"]:
        raise ValueError("source collection segment count changed")
    if source_collection_expression_segment_ids != collection_segment_ids:
        raise ValueError("source collection expression pairing changed")
    if (
        len(source_collection_expression_segment_ids)
        != profile["expected"]["source_collection_expressions"]
    ):
        raise ValueError("source collection expression count changed")
    if target_collection_expression_segment_ids != collection_segment_ids:
        raise ValueError("target collection expression pairing changed")
    if (
        len(target_collection_expression_segment_ids)
        != profile["expected"]["target_collection_expressions"]
    ):
        raise ValueError("target collection expression count changed")
    if (
        len(target_only_correction_segment_ids)
        != profile["expected"]["target_only_correction_segments"]
    ):
        raise ValueError("target-only correction segment count changed")
    if target_only_correction_expression_segment_ids != target_only_correction_segment_ids:
        raise ValueError("target-only correction expression pairing changed")
    if (
        len(target_only_correction_expression_segment_ids)
        != profile["expected"]["target_only_correction_expressions"]
    ):
        raise ValueError("target-only correction expression count changed")
    if len(external_target_unit_ids) != profile["expected"]["external_target_units"]:
        raise ValueError("external-target unit count changed")
    external_target_inventory_bytes = canonical_bytes(
        sorted(external_target_inventory, key=lambda item: item["id"])
    )
    if (
        len(external_target_inventory_bytes)
        != profile["expected"]["external_target_inventory_bytes"]
        or sha256_bytes(external_target_inventory_bytes)
        != profile["expected"]["external_target_inventory_sha256"]
    ):
        raise ValueError("external-target canonical inventory changed")

    modules = authority["modules"]
    if set(artifact_by_module) != set(modules):
        raise ValueError("localized module artifact set does not equal the 75-module manifest set")
    for module_id, module in modules.items():
        artifact = artifact_by_module[module_id]
        if (
            artifact["path"] != module["target_locator"]
            or artifact["bytes"] != module["target_bytes"]
            or strip_sha256(artifact["sha256"]) != strip_sha256(module["target_sha256"])
            or artifact["target_bytes"] != module["target_bytes"]
            or strip_sha256(artifact["target_sha256"]) != strip_sha256(module["target_sha256"])
        ):
            raise ValueError(f"localized artifact does not bind the module witness: {module_id}")

    expected = profile["expected"]
    curriculum = manifest["curriculum_mapping"]
    asset_closure = manifest["asset_closure"]
    ledger = manifest["terminology_and_adverse_ledger"]
    if (
        curriculum["concepts"] != expected["concepts"]
        or curriculum["mapped_source_objective_items"] != expected["source_objective_mappings"]
        or curriculum["localized_overlay"]["localized_objective_accounting"]["localized_objective_items"]
        != expected["localized_objective_occurrences"]
        or curriculum["concept_prerequisite_relations"] != expected["prerequisite_edges"]
        or asset_closure["files"] != expected["assets"]
        or asset_closure["occurrences"] != expected["asset_occurrences"]
        or asset_closure["bytes"] != expected["asset_bytes"]
        or ledger["records"] != expected["correction_ledger_records"]
        or ledger["terms"] != expected["correction_ledger_terms"]
        or ledger["corrections"] != expected["correction_ledger_corrections"]
    ):
        raise ValueError("native curriculum/asset/correction coverage changed")
    validation = manifest["validation"]
    required_native_proofs = (
        "all_record_ids_unique",
        "all_references_resolved",
        "all_translates_relations_resolved",
        "canonical_unit_identity_set_verified",
        "csv_round_trip_verified",
        "localized_unit_overlay_semantics_verified",
        "neutral_curation_contains_no_target_locale_fields",
        "second_full_build_byte_identical",
        "shared_curriculum_records_are_locale_invariant",
        "sqlite_projection_verified",
    )
    if any(validation.get(key) is not True for key in required_native_proofs):
        raise ValueError("native manifest no longer asserts every required owner proof")

    return {
        "known_ids": known_ids,
        "counts": dict(sorted(counts.items())),
        "view_counts": dict(sorted(view_counts.items())),
        "view_line_bytes": dict(sorted(view_line_bytes.items())),
        "segment_meta": segment_meta,
        "concept_meta": concept_meta,
        "course_native": course_native,
        "artifact_by_module": artifact_by_module,
        "asset_revision_keys": sorted(asset_revision_keys),
        "target_only_localized_units": sorted(
            target_only_localized_units, key=lambda item: item["native_occurrence_id"]
        ),
        "source_collection_structural_units": source_collection_structural_units,
        "target_collection_structural_occurrences": target_collection_structural_occurrences,
        "collection_segment_ids": sorted(collection_segment_ids),
        "source_collection_expression_segment_ids": sorted(
            source_collection_expression_segment_ids
        ),
        "target_collection_expression_segment_ids": sorted(
            target_collection_expression_segment_ids
        ),
        "target_only_correction_segment_ids": sorted(target_only_correction_segment_ids),
        "target_only_correction_expression_segment_ids": sorted(
            target_only_correction_expression_segment_ids
        ),
        "external_target_unit_ids": sorted(external_target_unit_ids),
        "external_target_inventory_bytes": len(external_target_inventory_bytes),
        "external_target_inventory_sha256": sha256_bytes(external_target_inventory_bytes),
        "null_concept_terms": null_concept_terms,
        "native_validation_count": native_validation_count,
        "native_reference_count": len(referenced_ids),
    }


def prepare_context(
    authority: dict[str, Any],
    native: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    namespace = uuid.UUID(profile["identity"]["namespace_uuid"])
    manifest = authority["manifest"]
    event_time = manifest["event_time"]
    derived = profile["derived"]
    source_collection_digest = strip_sha256(manifest["source_collection"]["sha256"])
    target_collection_digest = strip_sha256(manifest["localized_collection"]["sha256"])
    if not derived["source_collection_revision_stable_key"].endswith(f":{source_collection_digest}"):
        raise ValueError("source collection revision identity is not content-addressed")
    if not derived["target_collection_revision_stable_key"].endswith(f":{target_collection_digest}"):
        raise ValueError("target collection revision identity is not content-addressed")
    target_edition_id = rid(namespace, "edition", derived["target_edition_stable_key"])
    unbound_term_concept_id = rid(namespace, "concept", derived["unbound_term_concept_stable_key"])
    volume_module_id = rid(namespace, "module", derived["volume_module_stable_key"])
    build_recipe_id = rid(namespace, "build_recipe", derived["build_recipe_stable_key"])
    release_snapshot_id = rid(namespace, "release_snapshot", derived["release_snapshot_stable_key"])
    collection_file_id = rid(namespace, "file", derived["collection_file_stable_key"])
    source_collection_revision_id = rid(
        namespace, "file_revision", derived["source_collection_revision_stable_key"]
    )
    target_collection_revision_id = rid(
        namespace, "file_revision", derived["target_collection_revision_stable_key"]
    )

    source_revision_by_module: dict[str, str] = {}
    target_revision_by_module: dict[str, str] = {}
    file_by_module: dict[str, str] = {}
    module_member_ids: list[str] = []
    for module_id, row in authority["modules"].items():
        file_key = f"prealgebra2e:cnxml-file:{module_id}"
        file_by_module[module_id] = rid(namespace, "file", file_key)
        source_key = f"prealgebra2e:cnxml-file-revision:{module_id}:en-US:{strip_sha256(row['source_sha256'])}"
        target_key = f"prealgebra2e:cnxml-file-revision:{module_id}:id-ID:{strip_sha256(row['target_sha256'])}"
        source_revision_by_module[module_id] = rid(namespace, "file_revision", source_key)
        target_revision_by_module[module_id] = rid(namespace, "file_revision", target_key)
        member_key = f"prealgebra2e:module-member:{module_id}"
        module_member_ids.append(rid(namespace, "module_member", member_key))

    asset_revision_ids = {
        asset_id: rid(
            namespace,
            "asset_revision",
            f"prealgebra2e:asset-revision:{asset_id}:{digest}",
        )
        for asset_id, digest in native["asset_revision_keys"]
    }
    target_only_unit_by_occurrence = {
        item["native_occurrence_id"]: rid(
            namespace,
            "unit",
            f"prealgebra2e:technical-target-only-unit:{item['native_occurrence_id']}",
        )
        for item in native["target_only_localized_units"]
    }
    derived_ids = {
        target_edition_id,
        unbound_term_concept_id,
        volume_module_id,
        build_recipe_id,
        release_snapshot_id,
        collection_file_id,
        source_collection_revision_id,
        target_collection_revision_id,
        *file_by_module.values(),
        *source_revision_by_module.values(),
        *target_revision_by_module.values(),
        *module_member_ids,
        *asset_revision_ids.values(),
        *target_only_unit_by_occurrence.values(),
    }
    if derived_ids & native["known_ids"]:
        raise ValueError("derived common ID collides with a native ID")
    for value in derived_ids:
        verify_uuid5(value)

    return {
        "namespace": namespace,
        "event_time": event_time,
        "target_edition_id": target_edition_id,
        "unbound_term_concept_id": unbound_term_concept_id,
        "volume_module_id": volume_module_id,
        "build_recipe_id": build_recipe_id,
        "release_snapshot_id": release_snapshot_id,
        "collection_file_id": collection_file_id,
        "source_collection_revision_id": source_collection_revision_id,
        "target_collection_revision_id": target_collection_revision_id,
        "file_by_module": file_by_module,
        "source_revision_by_module": source_revision_by_module,
        "target_revision_by_module": target_revision_by_module,
        "asset_revision_ids": asset_revision_ids,
        "target_only_unit_by_occurrence": target_only_unit_by_occurrence,
        "derived_ids": derived_ids,
        "known_common_ids": native["known_ids"] | derived_ids,
        "native": native,
        "authority": authority,
        "profile": profile,
    }


def cnxml_profile(
    context: dict[str, Any],
    module_id: str,
    locale: str,
    locator: str,
    structural_xpath: str,
    native_xml_id: str | None,
) -> dict[str, Any]:
    authority = context["authority"]
    manifest = authority["manifest"]
    if locale == context["profile"]["source_locale"]:
        revision_id = context["source_revision_by_module"][module_id]
        authority_path = authority["source_witness"][module_id]["url"]
        collection_path = manifest["source_collection"]["path_locator"]
    elif locale == context["profile"]["target_locale"]:
        revision_id = context["target_revision_by_module"][module_id]
        authority_path = authority["target_witness"][module_id]["path"]
        collection_path = manifest["localized_collection"]["path_locator"]
    else:
        raise ValueError(f"unsupported CNXML profile locale: {locale}")
    return {
        "authority_file_revision_id": revision_id,
        "authority_path": authority_path,
        "collection_path": collection_path,
        "document_id": module_id,
        "format_profile": "cnxml",
        "identity_strategy": "native_id" if native_xml_id else "structural_path",
        "native_xml_id": native_xml_id,
        "profile_version": "1.0.0",
        "structural_xpath": structural_xpath,
        "xref_scope": "not_applicable",
        "xref_fragment": None,
        "mathml_xpath": None,
        "media_occurrence_path": None,
    }


def collxml_binding(
    context: dict[str, Any],
    locale: str,
    locator: str,
    structural_xpath: str,
) -> dict[str, Any]:
    manifest = context["authority"]["manifest"]
    if locale == context["profile"]["source_locale"]:
        authority_file_revision_id = context["source_collection_revision_id"]
        authority_path = manifest["source_collection"]["path_locator"]
    elif locale == context["profile"]["target_locale"]:
        authority_file_revision_id = context["target_collection_revision_id"]
        authority_path = manifest["localized_collection"]["path_locator"]
    else:
        raise ValueError(f"unsupported CollXML binding locale: {locale}")
    if not locator.startswith(f"{authority_path}/"):
        raise ValueError(f"CollXML locator is outside its locale authority: {locator}")
    return {
        "authority_file_revision_id": authority_file_revision_id,
        "authority_path": authority_path,
        "format_profile": "collxml",
        "identity_strategy": "structural_path",
        "locale": locale,
        "profile_version": "1.0.0",
        "structural_xpath": structural_xpath,
    }


def adapt_native(
    native: dict[str, Any],
    view_path: str,
    line_number: int,
    raw: bytes,
    context: dict[str, Any],
) -> dict[str, Any]:
    profile = context["profile"]
    identity = profile["identity"]
    authority = context["authority"]
    admission = authority["admission"]
    manifest = authority["manifest"]
    event_time = context["event_time"]
    native_type = native["record_type"]
    type_map = {
        "program": "program",
        "course": "course",
        "resource": "resource",
        "edition": "edition",
        "rights": "rights",
        "unit": "unit",
        "localized_unit": "occurrence",
        "segment": "segment",
        "expression": "segment_variant",
        "concept": "concept",
        "term": "term",
        "relation": "relation",
        "asset": "asset",
        "artifact": "artifact",
        "correction": "correction",
        "qa_event": "qa_event",
    }
    common = direct_base(native, type_map[native_type], view_path, line_number, raw, event_time)

    if native_type == "program":
        common.update(
            curriculum_version="A00/R001-owner-backend-v0.2.5",
            locale=profile["target_locale"],
            program_key="openstax-prealgebra-2e",
            rights_id=identity["default_rights_id"],
            title=native.get("name") or "OpenStax Prealgebra 2e",
        )
    elif native_type == "course":
        common.update(
            course_key=native["curriculum_course_code"],
            curriculum_source_locator=native["mapping_source_path"],
            curriculum_source_sha256=strip_sha256(native["mapping_source_sha256"]),
            order_key=native["curriculum_course_code"],
            outcome=native["curriculum_outcome_en_us"],
            prerequisite_course_keys=native["prerequisite_ids"],
            program_id=native["program_id"],
            resource_keys=native["resource_codes"],
            role=native["curriculum_role"],
            scope=native["curriculum_scope_en_us"],
            stage="complete",
            title=native["curriculum_label_en_us"],
        )
    elif native_type == "resource":
        common.update(
            authority_policy=f"Frozen git commit {manifest['edition_commit']}",
            creator_name="OpenStax; Rice University",
            official_reader=None,
            official_repository=f"https://github.com/{native['authority']}",
            original_title=admission["edition"]["source_title"],
            resource_key=native["authority"],
            work_type="open textbook",
        )
    elif native_type == "edition":
        common.update(
            archive_sha256=None,
            commit_sha=native["authority_value"],
            edition_kind="source",
            locale=profile["source_locale"],
            release_date=None,
            resource_id=native["resource_id"],
            rights_id=identity["default_rights_id"],
            source_edition_id=None,
            tree_sha=None,
            vcs_ref=native["authority_value"],
            vcs_type="git",
            version_label=native["authority_value"],
        )
    elif native_type == "rights":
        component_state = native.get("rights_statement_state")
        if native.get("license"):
            license_expression = native["license"]
        elif component_state == "public_domain_declared":
            license_expression = "Public-Domain"
        else:
            license_expression = "NOASSERTION"
        attribution = native.get("source_credit_text") or "OpenStax; Rice University"
        notice_locator = native.get("curation_source_path") or f"registry/rights.jsonl#{native['id']}"
        notice_sha = strip_sha256(native.get("curation_source_sha256")) or sha256_bytes(canonical_bytes(native))
        common.update(
            assertion_status=component_state or "bundle_default_asserted",
            attribution=attribution,
            authority=native.get("curation_source_path") or admission["edition"]["source_repository"],
            change_notice="Adaptasi Bahasa Indonesia dibantu AI; perubahan dari sumber asli dipertahankan sebagai overlay.",
            license_expression=license_expression,
            nonendorsement="Adaptasi ini tidak disahkan oleh OpenStax.",
            notice_locator=notice_locator,
            notice_sha256=notice_sha,
            source_component_id=native.get("asset_id") or native["id"],
            third_party_status=component_state or native["rights_component_scope"],
        )
    elif native_type == "unit":
        locator = native["source_locator"]
        module_id = module_from_locator(locator)
        source_xml_path = None
        if module_id:
            source_xml_path = xpath_from_locator(locator, module_id, native.get("order_path"))
            common["extensions"][PROFILE_EXTENSION] = cnxml_profile(
                context,
                module_id,
                profile["source_locale"],
                locator,
                source_xml_path,
                native.get("source_local_id"),
            )
        elif locator.startswith(f"{context['authority']['manifest']['source_collection']['path_locator']}/"):
            collection_path = context["authority"]["manifest"]["source_collection"]["path_locator"]
            source_xml_path = collection_xpath_from_locator(locator, collection_path)
            if native.get("order_path") != source_xml_path:
                raise ValueError(f"source collection unit structural path changed: {native['id']}")
            common["extensions"][COLLXML_EXTENSION] = collxml_binding(
                context, profile["source_locale"], locator, source_xml_path
            )
        elif (
            native["unit_type"] == "external_target"
            and locator.startswith("https://")
            and native["source_key"] == f"external-target:{locator}"
            and native.get("order_path") is None
            and native.get("parent_id") is None
            and native.get("source_local_id") is None
        ):
            source_xml_path = None
        else:
            raise ValueError(f"unit has no recognized source XML authority: {native['id']}")
        common.update(
            first_edition_id=identity["source_edition_id"],
            identity_anchor=native["source_key"],
            identity_basis=(
                "native OpenStax external-target URL key and frozen HTTPS locator"
                if native["unit_type"] == "external_target"
                else "native OpenStax XML key and frozen structural locator"
            ),
            resource_id=native["resource_id"],
            rights_default_id=native["rights_component_id"],
            source_label=native.get("source_local_id"),
            source_local_id=native.get("source_local_id"),
            source_path=locator,
            source_xml_path=source_xml_path,
            unit_kind=native["unit_type"],
        )
    elif native_type == "localized_unit":
        locator = native["target_locator"]
        module_id = module_from_locator(locator)
        if module_id is not None:
            structural_xpath = xpath_from_locator(locator, module_id, native.get("order_path"))
            file_revision_id = context["target_revision_by_module"][module_id]
            reader_visibility = "native localized CNXML structure"
            common["extensions"][PROFILE_EXTENSION] = cnxml_profile(
                context,
                module_id,
                profile["target_locale"],
                locator,
                structural_xpath,
                native.get("source_local_id"),
            )
        elif locator.startswith(f"{context['authority']['manifest']['localized_collection']['path_locator']}/"):
            collection_path = context["authority"]["manifest"]["localized_collection"]["path_locator"]
            structural_xpath = collection_xpath_from_locator(locator, collection_path)
            if native.get("order_path") != structural_xpath:
                raise ValueError(f"localized collection occurrence structural path changed: {native['id']}")
            file_revision_id = context["target_collection_revision_id"]
            reader_visibility = "native localized collection XML structure"
            common["extensions"][COLLXML_EXTENSION] = collxml_binding(
                context, profile["target_locale"], locator, structural_xpath
            )
        else:
            raise ValueError(f"localized unit has no recognized target XML authority: {native['id']}")
        common.update(
            edition_id=context["target_edition_id"],
            file_revision_id=file_revision_id,
            locale=native["locale"],
            order_path=native.get("order_path") or structural_xpath,
            parent_occurrence_id=native.get("parent_id"),
            reader_visibility=reader_visibility,
            sibling_ordinal=last_ordinal(native.get("order_path")),
            source_occurrence_id=None,
            subtree_sha256=strip_sha256(native["content_hash"]),
            translation_state=native["translation_state"],
            unit_id=(
                native["canonical_unit_id"]
                or context["target_only_unit_by_occurrence"].get(native["id"])
            ),
            xml_path=structural_xpath,
        )
    elif native_type == "segment":
        locator = native["source_locator"]
        module_id = module_from_locator(locator)
        if module_id is not None:
            structural_xpath = xpath_from_locator(locator, module_id, None)
            common["extensions"][PROFILE_EXTENSION] = cnxml_profile(
                context,
                module_id,
                profile["source_locale"],
                locator,
                structural_xpath,
                None,
            )
        elif locator is not None and locator.startswith(f"{manifest['source_collection']['path_locator']}/"):
            structural_xpath = collection_xpath_from_locator(
                locator, manifest["source_collection"]["path_locator"]
            )
            common["extensions"][COLLXML_EXTENSION] = collxml_binding(
                context, profile["source_locale"], locator, structural_xpath
            )
        elif (
            locator is None
            and native.get("identity_scope") == "localized_correction"
            and native.get("locale") == profile["target_locale"]
            and native.get("source_expression_id") is None
            and native.get("source_expression_state") == "absent_in_frozen_source"
        ):
            structural_xpath = native["source_key"]
        else:
            raise ValueError(f"segment has no recognized source XML authority: {native['id']}")
        common.update(
            identity_anchor=native["source_key"],
            ordinal=last_ordinal(structural_xpath),
            segment_kind=native["slot"],
            segmentation_profile=(
                "openstax-cnxml-target-only-correction-v0.2.5"
                if locator is None
                else "openstax-cnxml-text-slots-v0.2.5"
            ),
            unit_id=native["owner_unit_id"],
        )
    elif native_type == "expression":
        segment = context["native"]["segment_meta"].get(native["segment_id"])
        if segment is None:
            raise ValueError(f"expression has no segment metadata: {native['id']}")
        if native["locale"] == profile["source_locale"]:
            locator = segment["source_locator"]
            module_id = module_from_locator(locator)
            edition_id = identity["source_edition_id"]
            source_variant_id = None
            role = "source"
            collection_path = manifest["source_collection"]["path_locator"]
        elif native["locale"] == profile["target_locale"]:
            locator = native["target_locator"]
            module_id = module_from_locator(locator)
            edition_id = context["target_edition_id"]
            source_variant_id = native["source_expression_id"]
            role = "translation"
            collection_path = manifest["localized_collection"]["path_locator"]
        else:
            raise ValueError(f"unexpected expression locale: {native['locale']}")
        if module_id is not None:
            structural_xpath = xpath_from_locator(locator, module_id, None)
            common["extensions"][PROFILE_EXTENSION] = cnxml_profile(
                context,
                module_id,
                native["locale"],
                locator,
                structural_xpath,
                None,
            )
        elif locator.startswith(f"{collection_path}/"):
            structural_xpath = collection_xpath_from_locator(locator, collection_path)
            common["extensions"][COLLXML_EXTENSION] = collxml_binding(
                context, native["locale"], locator, structural_xpath
            )
        else:
            raise ValueError(f"expression has no recognized XML authority: {native['id']}")
        common.update(
            edition_id=edition_id,
            format="text/plain",
            locale=native["locale"],
            payload=native["text"],
            payload_sha256=strip_sha256(native["text_sha256"]),
            rights_id=segment["rights_component_id"],
            role=role,
            segment_id=native["segment_id"],
            source_variant_id=source_variant_id,
            translation_state=native["translation_state"],
        )
    elif native_type == "concept":
        common.update(
            concept_key=native["concept_key"],
            concept_scheme="program-matematika-indonesia/A00",
            definition_segment_id=None,
            parent_concept_id=None,
        )
    elif native_type == "term":
        concept_id = native.get("concept_id") or context["unbound_term_concept_id"]
        concept = context["native"]["concept_meta"].get(native.get("concept_id"))
        course = context["native"]["course_native"]
        preferred = native.get("preferred_term") or native.get("localized_label") or ""
        source_form = native.get("source_term")
        if source_form is None and concept is not None:
            source_form = concept["label_en_us"]
        if source_form is None and native.get("term_kind") == "course_metadata":
            source_form = course["curriculum_label_en_us"]
        evidence = native.get("evidence_basis") or canonical(
            {
                "path": native.get("overlay_source_path"),
                "sha256": native.get("overlay_source_sha256"),
            }
        )
        notes = native.get("risk_or_adverse_detail") or native.get("localized_definition") or native.get("localized_scope") or ""
        common.update(
            concept_id=concept_id,
            evidence=evidence,
            notes=notes,
            preferred_form=preferred,
            register=native.get("term_kind") or native.get("ledger_kind") or "terminology",
            scope_unit_id=identity["root_collection_unit_id"],
            source_form=source_form or "",
            source_locale=profile["source_locale"],
            source_term_id=native.get("source_record_id") or f"source-term:{native['id']}",
            target_locale=native.get("locale") or profile["target_locale"],
            term_status=native.get("ledger_status") or native.get("translation_state") or native["status"],
        )
    elif native_type == "relation":
        qualifier = native.get("qualifier")
        if qualifier == profile["target_locale"] or qualifier == "en-US>id-ID":
            edition_id = context["target_edition_id"]
        elif qualifier == profile["source_locale"]:
            edition_id = identity["source_edition_id"]
        else:
            edition_id = None
        common.update(
            assertion_method="native openstax-foundations explicit relation",
            confidence="owner-validated",
            edition_id=edition_id,
            from_id=native["subject_id"],
            ordinal=0,
            relation_type=native["predicate"],
            source_locator=qualifier or "",
            strength="asserted",
            to_id=native["object_id"],
        )
    elif native_type == "asset":
        common.update(
            asset_kind="reader asset",
            canonical_path_or_uri=native["canonical_path"],
            media_type=native["mime_type"],
            resource_id=native["resource_id"],
            rights_default_id=native["rights_component_id"],
        )
    elif native_type == "artifact":
        common.update(
            artifact_kind=native["artifact_type"],
            build_receipt="backend.volume.manifest.json#workflow/artifacts.jsonl",
            bytes=native["bytes"],
            edition_id=context["target_edition_id"],
            locale=native["locale"],
            manifest_sha256=None,
            public_uri=None,
            sha256=strip_sha256(native["sha256"]),
            toolchain_id=(
                f"{manifest['toolchain']['path_locator']}@"
                f"{strip_sha256(manifest['toolchain']['sha256'])}"
            ),
            tree_sha256=None,
        )
    elif native_type == "correction":
        affected = native.get("affected_unit_ids") or [identity["root_collection_unit_id"]]
        original = native.get("source_issue") or ""
        replacement = native.get("target_decision") or ""
        common.update(
            affected_id=affected[0],
            binding_status="native affected_unit_ids",
            category=native["ledger_kind"],
            evidence_locator=native["source_locator"],
            local_state=native["correction_state"],
            original_payload_sha256=sha256_bytes(original.encode("utf-8")),
            payload_hash_basis="UTF-8 bytes of native source_issue and target_decision fields",
            rationale=f"{native.get('evidence_basis', '')} {native.get('risk_or_adverse_detail', '')}".strip(),
            replacement_payload_sha256=sha256_bytes(replacement.encode("utf-8")),
            source_claim_id=None,
            source_edition_id=identity["source_edition_id"],
            # The optional common field is constrained to the legacy DMD claim
            # namespace; the exact OSPA owner ID remains in the native extension.
            source_record_id=None,
            upstream_disposition=native["upstream_report_disposition"],
            upstream_url=None,
        )
    elif native_type == "qa_event":
        common.update(
            input_hash=sha256_bytes(canonical_bytes(native)),
            method=canonical(native.get("checks") or []),
            qa_type=native["qa_kind"],
            result=native["result"],
            reviewer_kind="frozen owner-lane verifier",
            severity_p1=0,
            severity_p2=0,
            severity_p3=0,
            tool_name=native["responsible_workflow"],
            tool_version=native["schema_version"],
            witness_locator=native.get("receipt_path") or "backend.volume.manifest.json#validation",
        )
    else:
        raise ValueError(f"unhandled native record type: {native_type}")
    return common


def static_derived_records(context: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    profile = context["profile"]
    identity = profile["identity"]
    derived = profile["derived"]
    authority = context["authority"]
    manifest = authority["manifest"]
    admission = authority["admission"]
    namespace = context["namespace"]
    event_time = context["event_time"]
    records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    records["editions"].append(
        derived_base(
            namespace,
            "edition",
            derived["target_edition_stable_key"],
            event_time,
            archive_sha256=None,
            commit_sha=admission["publication"]["github"]["main_commit"],
            edition_kind="localized derivative",
            locale=profile["target_locale"],
            release_date="2026-08-23",
            resource_id=identity["resource_id"],
            rights_id=identity["default_rights_id"],
            source_edition_id=identity["source_edition_id"],
            tree_sha=None,
            vcs_ref="prealgebra-2e-id-ID-v0.2.7",
            vcs_type="git",
            version_label=profile["expected"]["release_version"],
            extensions={
                DERIVED_EXTENSION: {
                    "admission_id": admission["admission_id"],
                    "owner_backend_schema_version": manifest["schema_version"],
                    "translation_state": admission["edition"]["translation_state"],
                }
            },
        )
    )
    records["concepts"].append(
        derived_base(
            namespace,
            "concept",
            derived["unbound_term_concept_stable_key"],
            event_time,
            concept_key="prealgebra2e.adapter.unbound_terms",
            concept_scheme="adapter-technical-binding",
            definition_segment_id=None,
            parent_concept_id=None,
            extensions={
                DERIVED_EXTENSION: {
                    "purpose": "Required common-schema binding for native terminology/course-metadata records whose concept_id is explicitly null; not a mathematical taxonomy claim.",
                    "native_unbound_term_count": context["native"]["null_concept_terms"],
                }
            },
        )
    )

    for item in context["native"]["target_only_localized_units"]:
        native_occurrence_id = item["native_occurrence_id"]
        unit_key = f"prealgebra2e:technical-target-only-unit:{native_occurrence_id}"
        locator = item["target_locator"]
        module_id = module_from_locator(locator)
        if module_id is None:
            raise ValueError(f"target-only localized correction lacks CNXML module: {native_occurrence_id}")
        structural_xpath = xpath_from_locator(locator, module_id, item.get("order_path"))
        records["units"].append(
            derived_base(
                namespace,
                "unit",
                unit_key,
                event_time,
                first_edition_id=context["target_edition_id"],
                identity_anchor=item["source_key"],
                identity_basis="technical structural binding for owner-declared target_only_localized_correction; no semantic taxonomy claim",
                resource_id=item["resource_id"],
                rights_default_id=item["rights_component_id"],
                source_label=None,
                source_local_id=None,
                source_path=locator,
                source_xml_path=structural_xpath,
                unit_kind=item["unit_type"],
                extensions={
                    DERIVED_EXTENSION: {
                        "native_occurrence_id": native_occurrence_id,
                        "native_canonical_unit_id": None,
                        "projection_class": "target_only_localized_correction",
                        "semantic_claim": "none; schema-binding unit only",
                    },
                    PROFILE_EXTENSION: cnxml_profile(
                        context,
                        module_id,
                        profile["target_locale"],
                        locator,
                        structural_xpath,
                        None,
                    ),
                },
            )
        )

    source_collection = manifest["source_collection"]
    target_collection = manifest["localized_collection"]
    records["files"].append(
        derived_base(
            namespace,
            "file",
            derived["collection_file_stable_key"],
            event_time,
            canonical_path=source_collection["path_locator"],
            media_type="application/xml",
            parse_mode="collxml",
            resource_id=identity["resource_id"],
            role="source/target collection XML authority",
            extensions={
                DERIVED_EXTENSION: {
                    "source_collection_path": source_collection["path_locator"],
                    "target_collection_path": target_collection["path_locator"],
                }
            },
        )
    )
    records["file_revisions"].append(
        derived_base(
            namespace,
            "file_revision",
            derived["source_collection_revision_stable_key"],
            event_time,
            actual_path=source_collection["path_locator"],
            bytes=source_collection["bytes"],
            edition_id=identity["source_edition_id"],
            file_id=context["collection_file_id"],
            generated=False,
            git_blob_sha1=git_blob_sha1_from_digest_only(),
            sha256=strip_sha256(source_collection["sha256"]),
            source_revision_id=None,
            extensions={DERIVED_EXTENSION: {"authority": "owner backend manifest source_collection"}},
        )
    )
    records["file_revisions"].append(
        derived_base(
            namespace,
            "file_revision",
            derived["target_collection_revision_stable_key"],
            event_time,
            actual_path=target_collection["path_locator"],
            bytes=target_collection["bytes"],
            edition_id=context["target_edition_id"],
            file_id=context["collection_file_id"],
            generated=True,
            git_blob_sha1=git_blob_sha1_from_digest_only(),
            sha256=strip_sha256(target_collection["sha256"]),
            source_revision_id=context["source_collection_revision_id"],
            extensions={
                DERIVED_EXTENSION: {
                    "authority": "owner backend manifest localized_collection",
                    "translation_state": "mathematically_reviewed",
                }
            },
        )
    )

    for module_id, module in authority["modules"].items():
        file_key = f"prealgebra2e:cnxml-file:{module_id}"
        file_id = context["file_by_module"][module_id]
        records["files"].append(
            derived_base(
                namespace,
                "file",
                file_key,
                event_time,
                canonical_path=f"modules/{module_id}/index.cnxml",
                media_type="application/xml",
                parse_mode="cnxml",
                resource_id=identity["resource_id"],
                role="source/target CNXML authority",
                extensions={DERIVED_EXTENSION: {"module_id": module_id}},
            )
        )
        source_digest = strip_sha256(module["source_sha256"])
        source_key = f"prealgebra2e:cnxml-file-revision:{module_id}:en-US:{source_digest}"
        records["file_revisions"].append(
            derived_base(
                namespace,
                "file_revision",
                source_key,
                event_time,
                actual_path=f"metadata/source-witness-manifest.tsv#{module_id}",
                bytes=module["source_bytes"],
                edition_id=identity["source_edition_id"],
                file_id=file_id,
                generated=False,
                git_blob_sha1=git_blob_sha1_from_digest_only(),
                sha256=source_digest,
                source_revision_id=None,
                extensions={
                    DERIVED_EXTENSION: {
                        "authority_url": authority["source_witness"][module_id]["url"],
                        "witness_path": profile["source"]["source_witness_path"],
                    }
                },
            )
        )
        target_digest = strip_sha256(module["target_sha256"])
        target_key = f"prealgebra2e:cnxml-file-revision:{module_id}:id-ID:{target_digest}"
        records["file_revisions"].append(
            derived_base(
                namespace,
                "file_revision",
                target_key,
                event_time,
                actual_path=module["target_locator"],
                bytes=module["target_bytes"],
                edition_id=context["target_edition_id"],
                file_id=file_id,
                generated=True,
                git_blob_sha1=git_blob_sha1_from_digest_only(),
                sha256=target_digest,
                source_revision_id=context["source_revision_by_module"][module_id],
                extensions={
                    DERIVED_EXTENSION: {
                        "witness_path": profile["source"]["target_witness_path"],
                        "translation_state": "mathematically_reviewed",
                    }
                },
            )
        )

    records["modules"].append(
        derived_base(
            namespace,
            "module",
            derived["volume_module_stable_key"],
            event_time,
            closure_profile="one complete corpus with 75 ordered OpenStax CNXML module references",
            course_id=identity["course_id"],
            description="Prealgebra 2e complete Indonesian volume; module references are not separate books.",
            edition_id=context["target_edition_id"],
            locale=profile["target_locale"],
            manifest_sha256=authority["authority_facts"]["backend_manifest"]["sha256"],
            module_kind="complete textbook volume",
            module_version=manifest["schema_version"],
            root_unit_id=identity["root_collection_unit_id"],
            title=admission["edition"]["title"],
            extensions={DERIVED_EXTENSION: {"module_reference_count": manifest["module_count"]}},
        )
    )
    for module_id, module in authority["modules"].items():
        member_key = f"prealgebra2e:module-member:{module_id}"
        records["module_members"].append(
            derived_base(
                namespace,
                "module_member",
                member_key,
                event_time,
                entity_id=module["module_unit_id"],
                inclusion_reason="frozen source collection order",
                module_id=context["volume_module_id"],
                order_path=f"/{int(module['ordinal']):04d}",
                required=True,
                role="source module root",
                extensions={DERIVED_EXTENSION: {"native_module_id": module_id, "ordinal": module["ordinal"]}},
            )
        )

    records["build_recipes"].append(
        derived_base(
            namespace,
            "build_recipe",
            derived["build_recipe_stable_key"],
            event_time,
            command=manifest["build_command_argv"],
            edition_id=context["target_edition_id"],
            environment={
                "toolchain_locator": manifest["toolchain"]["path_locator"],
                "toolchain_sha256": strip_sha256(manifest["toolchain"]["sha256"]),
                "python": manifest["toolchain"]["versions"]["python"]["version"],
                "jsonschema": manifest["toolchain"]["versions"]["jsonschema"]["version"],
                "sqlite": manifest["toolchain"]["versions"]["sqlite"]["library_version"],
                "platform": canonical(manifest["toolchain"]["versions"]["platform"]),
            },
            input_ids=[identity["source_edition_id"], identity["resource_id"]],
            name="OpenStax Prealgebra 2e deterministic volume backend build",
            output_ids=[context["volume_module_id"]],
            resource_id=identity["resource_id"],
            verification=manifest["validation"],
            working_directory=manifest["build_working_directory_locator"],
            extensions={
                DERIVED_EXTENSION: {
                    "build_script": manifest["build_script"],
                    "input_fingerprint_sha256": profile["frozen_authority"]["accepted_input_fingerprint_sha256"],
                    "complete_owner_toolchain": manifest["toolchain"],
                }
            },
        )
    )
    records["release_snapshots"].append(
        derived_base(
            namespace,
            "release_snapshot",
            derived["release_snapshot_stable_key"],
            event_time,
            archive_sha256=None,
            artifact_ids=[],
            commit_sha=admission["publication"]["github"]["main_commit"],
            edition_id=context["target_edition_id"],
            immutable=True,
            publication_uri=admission["publication"]["github"]["release_url"],
            release_date="2026-08-23",
            release_version=profile["expected"]["release_version"],
            snapshot_kind="owner release and anonymous readback witness",
            tree_sha=None,
            extensions={
                DERIVED_EXTENSION: {
                    "github_state": admission["publication"]["github"]["state"],
                    "zenodo_concept_doi": admission["publication"]["zenodo"]["concept_doi"],
                    "zenodo_version_doi": admission["publication"]["zenodo"]["version_doi"],
                    "owner_remaining_gate": admission["publication"]["remaining_gate"],
                }
            },
        )
    )
    for rows in records.values():
        rows.sort(key=lambda row: row["id"])
    return dict(records)


def iter_adapted_view(
    context: dict[str, Any], view: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    path = context["authority"]["backend_root"] / view["path"]
    for _, native, line_number, raw in iter_native(path, view["native_record_type"]):
        yield adapt_native(native, view["path"], line_number, raw, context)


def iter_asset_revisions(context: dict[str, Any]) -> Iterator[dict[str, Any]]:
    view = next(item for item in context["profile"]["source"]["views"] if item["native_record_type"] == "asset")
    path = context["authority"]["backend_root"] / view["path"]
    namespace = context["namespace"]
    for _, native, _, _ in iter_native(path, "asset"):
        digest = strip_sha256(native["sha256"])
        key = f"prealgebra2e:asset-revision:{native['id']}:{digest}"
        yield derived_base(
            namespace,
            "asset_revision",
            key,
            context["event_time"],
            asset_id=native["id"],
            bytes=native["bytes"],
            edition_id=context["target_edition_id"],
            file_revision_id=None,
            sha256=digest,
            source_asset_revision_id=None,
            extensions={
                DERIVED_EXTENSION: {
                    "native_asset_id": native["id"],
                    "closure_state": native["closure_state"],
                    "occurrences": native["occurrences"],
                }
            },
        )


def records_for_table(
    table: str,
    context: dict[str, Any],
    static: dict[str, list[dict[str, Any]]],
) -> Iterator[dict[str, Any]]:
    iterators: list[Iterable[dict[str, Any]]] = []
    views = [view for view in context["profile"]["source"]["views"] if view["common_table"] == table]
    iterators.extend(iter_adapted_view(context, view) for view in views)
    if table == "asset_revisions":
        # Only 2,962 compact derived rows: sort by the newly derived UUIDv5,
        # because native asset-ID order does not imply derived revision-ID order.
        iterators.append(iter(sorted(iter_asset_revisions(context), key=lambda row: row["id"])))
    if table in static:
        iterators.append(iter(static[table]))
    if not iterators:
        return
    yield from heapq.merge(*iterators, key=lambda row: row["id"])


def record_type_by_table(schema: dict[str, Any]) -> dict[str, str]:
    result = {}
    for table, table_schema in schema["properties"]["tables"]["properties"].items():
        definition = table_schema["items"]["$ref"].rsplit("/", 1)[-1]
        result[table] = schema["$defs"][definition]["properties"]["record_type"]["const"]
    return result


def validators_by_table(schema: dict[str, Any]) -> dict[str, Draft202012Validator]:
    validators = {}
    for table, table_schema in schema["properties"]["tables"]["properties"].items():
        definition = table_schema["items"]["$ref"].rsplit("/", 1)[-1]
        record_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": f"#/$defs/{definition}",
        }
        validators[table] = Draft202012Validator(record_schema, format_checker=FormatChecker())
    return validators


def backend_metadata(context: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    namespace = context["namespace"]
    return {
        "$schema": schema["$id"],
        "dataset_id": rid(namespace, "dataset", "prealgebra2e:R001:id-ID:v0.2.7:common-v1"),
        "dataset_version": "0.2.7+owner-backend-0.2.5+interlanguage-v1",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
    }


def assemble_once(
    context: dict[str, Any],
    schema: dict[str, Any],
    profile_schema: dict[str, Any],
) -> dict[str, Any]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    type_by_table = record_type_by_table(schema)
    validators = validators_by_table(schema)
    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    static = static_derived_records(context)
    metadata = backend_metadata(context, schema)
    known = context["known_common_ids"]

    backend_hash = hashlib.sha256()
    backend_bytes = 0

    def feed(data: bytes) -> None:
        nonlocal backend_bytes
        backend_hash.update(data)
        backend_bytes += len(data)

    feed(b"{")
    for index, key in enumerate(sorted(metadata)):
        if index:
            feed(b",")
        feed(canonical_bytes(key))
        feed(b":")
        feed(canonical_bytes(metadata[key]))
    feed(b',"tables":{')

    table_hashes: dict[str, dict[str, Any]] = {}
    actual_ids: set[str] = set()
    stable_keys: set[str] = set()
    referenced_ids: set[str] = set()
    native_extensions = 0
    exact_native_reverse_extractions = 0
    native_null_canonical_unit_ids_recovered = 0
    source_profiles = 0
    collxml_bindings = 0
    profile_locales: Counter[str] = Counter()
    total_records = 0
    previous_record_type: str | None = None

    for table_index, table in enumerate(table_names):
        if table_index:
            feed(b",")
        feed(canonical_bytes(table))
        feed(b":[")
        table_digest = hashlib.sha256()
        table_bytes = 0
        table_records = 0
        previous_id: str | None = None
        first = True
        for record in records_for_table(table, context, static):
            record_id = record["id"]
            if previous_id is not None and record_id <= previous_id:
                raise ValueError(f"common table is not strictly ID-sorted: {table}: {record_id}")
            previous_id = record_id
            if record_id not in known:
                raise ValueError(f"unexpected common ID: {record_id}")
            if record_id in actual_ids:
                raise ValueError(f"duplicate common ID: {record_id}")
            actual_ids.add(record_id)
            stable_key = record["stable_key"]
            if stable_key in stable_keys:
                raise ValueError(f"duplicate common stable key: {stable_key}")
            stable_keys.add(stable_key)
            try:
                validators[table].validate(record)
            except Exception as exc:
                raise ValueError(f"common schema failure: {table}/{record_id}: {exc}") from exc
            if record["record_type"] != type_by_table[table]:
                raise ValueError(f"common table/type mismatch: {table}/{record_id}")
            if previous_record_type is not None and record["record_type"] < previous_record_type:
                # This is informational only: table order is schema-key order, while
                # the independent virtual JSONL pass below uses record-type order.
                pass
            previous_record_type = record["record_type"]
            for path, value in iter_urns(record):
                if path == ("id",):
                    continue
                referenced_ids.add(value)
            extensions = record.get("extensions") or {}
            if NATIVE_EXTENSION in extensions:
                native_extensions += 1
                native_payload = extensions[NATIVE_EXTENSION]
                recovered_line = canonical_bytes(native_payload["native_record"]) + b"\n"
                if sha256_bytes(recovered_line) != native_payload["native_line_sha256"]:
                    raise ValueError(f"native reverse projection is not byte-identical: {record_id}")
                exact_native_reverse_extractions += 1
                recovered_native = native_payload["native_record"]
                if (
                    recovered_native.get("record_type") == "localized_unit"
                    and "canonical_unit_id" in recovered_native
                    and recovered_native["canonical_unit_id"] is None
                ):
                    native_null_canonical_unit_ids_recovered += 1
            if PROFILE_EXTENSION in extensions:
                try:
                    profile_validator.validate(extensions[PROFILE_EXTENSION])
                except Exception as exc:
                    raise ValueError(f"source-profile failure: {table}/{record_id}: {exc}") from exc
                revision_id = extensions[PROFILE_EXTENSION]["authority_file_revision_id"]
                if revision_id not in known:
                    raise ValueError(f"source-profile authority revision does not close: {record_id}")
                source_profiles += 1
                if record.get("locale"):
                    profile_locales[record["locale"]] += 1
            if COLLXML_EXTENSION in extensions:
                binding = extensions[COLLXML_EXTENSION]
                if set(binding) != {
                    "authority_file_revision_id",
                    "authority_path",
                    "format_profile",
                    "identity_strategy",
                    "locale",
                    "profile_version",
                    "structural_xpath",
                }:
                    raise ValueError(f"CollXML binding keyset changed: {record_id}")
                if (
                    binding["format_profile"] != "collxml"
                    or binding["identity_strategy"] != "structural_path"
                    or binding["profile_version"] != "1.0.0"
                    or binding["authority_file_revision_id"] not in known
                    or not binding["structural_xpath"].startswith("/")
                ):
                    raise ValueError(f"invalid CollXML binding: {record_id}")
                collxml_bindings += 1

            line = canonical_bytes(record) + b"\n"
            table_digest.update(line)
            table_bytes += len(line)
            if not first:
                feed(b",")
            feed(line[:-1])
            first = False
            table_records += 1
            total_records += 1
        feed(b"]")
        table_hashes[table] = {
            "records": table_records,
            "virtual_jsonl_bytes": table_bytes,
            "virtual_jsonl_sha256": table_digest.hexdigest(),
        }
    feed(b"}}")

    if actual_ids != known:
        missing = sorted(known - actual_ids)
        extra = sorted(actual_ids - known)
        raise ValueError(f"common ID inventory mismatch; missing={missing[:10]} extra={extra[:10]}")
    dangling = sorted(referenced_ids - known)
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling[:10]}")
    if native_extensions != context["profile"]["expected"]["native_records"]:
        raise ValueError("not every native record was retained in one common extension")
    if exact_native_reverse_extractions != native_extensions:
        raise ValueError("exact native reverse extraction count differs from native extension count")
    if collxml_bindings != context["profile"]["expected"]["common_collxml_bindings"]:
        raise ValueError("common CollXML binding count changed")
    if (
        native_null_canonical_unit_ids_recovered
        != context["profile"]["expected"]["target_only_localized_correction_units"]
    ):
        raise ValueError("target-only native null reverse-projection count changed")

    virtual_digest = hashlib.sha256()
    virtual_bytes = 0
    virtual_records = 0
    for table in sorted(table_names, key=lambda name: (type_by_table[name], name)):
        for record in records_for_table(table, context, static):
            line = canonical_bytes(record) + b"\n"
            virtual_digest.update(line)
            virtual_bytes += len(line)
            virtual_records += 1
    if virtual_records != total_records:
        raise ValueError("virtual JSONL record count differs from canonical backend record count")

    return {
        "canonical_backend_bytes": backend_bytes,
        "canonical_backend_sha256": backend_hash.hexdigest(),
        "record_count": total_records,
        "table_count": len(table_names),
        "nonempty_table_count": sum(item["records"] > 0 for item in table_hashes.values()),
        "table_hashes": table_hashes,
        "virtual_records_jsonl_bytes": virtual_bytes,
        "virtual_records_jsonl_sha256": virtual_digest.hexdigest(),
        "native_extensions": native_extensions,
        "exact_native_reverse_extractions": exact_native_reverse_extractions,
        "native_null_canonical_unit_ids_recovered": native_null_canonical_unit_ids_recovered,
        "source_profiles": source_profiles,
        "source_profile_locales": dict(sorted(profile_locales.items())),
        "collxml_bindings": collxml_bindings,
        "global_unique_ids": len(actual_ids),
        "global_unique_stable_keys": len(stable_keys),
        "referenced_ids": len(referenced_ids),
        "foreign_key_closure": "pass",
        "strict_schema": "pass",
        "strict_source_profiles": "pass",
    }


def receipt_artifact(root: Path, path: Path, status: str, **fields: Any) -> dict[str, Any]:
    return {
        "path": portable(path, root),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "status": status,
        **fields,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-profile-schema", required=True, type=Path)
    parser.add_argument("--receipt-schema", required=True, type=Path)
    parser.add_argument("--adapter-profile", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    corpus_root = args.corpus_root.resolve()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    profile_schema = json.loads(args.source_profile_schema.read_text(encoding="utf-8"))
    receipt_schema = json.loads(args.receipt_schema.read_text(encoding="utf-8"))
    adapter_profile = json.loads(args.adapter_profile.read_text(encoding="utf-8"))
    for schema_value in (schema, profile_schema, receipt_schema):
        Draft202012Validator.check_schema(schema_value)
    if adapter_profile.get("schema_name") != "interlanguage-prealgebra2e-common-backend-adapter-profile":
        raise ValueError("unexpected adapter profile schema")

    authority = verify_frozen_authority(corpus_root, adapter_profile)
    native_schema_path = authority["backend_root"] / adapter_profile["source"]["native_schema_path"]
    native_schema = json.loads(native_schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(native_schema)
    native = verify_native_records(authority, adapter_profile, native_schema)
    context = prepare_context(authority, native, adapter_profile)

    first = assemble_once(context, schema, profile_schema)
    second = assemble_once(context, schema, profile_schema)
    if first != second:
        raise ValueError("two independent streaming common-backend assemblies are not byte-identical")
    expected_derived_records = adapter_profile["expected"]["common_derived_records"]
    expected_target_records = adapter_profile["expected"]["target_records"]
    if len(context["derived_ids"]) != expected_derived_records:
        raise ValueError(
            f"derived record count mismatch: {len(context['derived_ids'])} != {expected_derived_records}"
        )
    if adapter_profile["expected"]["native_records"] + expected_derived_records != expected_target_records:
        raise ValueError("frozen native/derived/target record arithmetic is inconsistent")
    if first["record_count"] != expected_target_records:
        raise ValueError(
            f"target record count mismatch: {first['record_count']} != {expected_target_records}"
        )

    admission = authority["admission"]
    manifest = authority["manifest"]
    backend_root = authority["backend_root"]
    manifest_path = authority["manifest_path"]
    adapter_profile_fact = {
        "path": portable(args.adapter_profile, args.adapter_profile.parents[3]),
        "bytes": args.adapter_profile.stat().st_size,
        "sha256": sha256_file(args.adapter_profile),
    }
    native_schema_fact = {
        "path": adapter_profile["source"]["native_schema_path"],
        "bytes": native_schema_path.stat().st_size,
        "sha256": sha256_file(native_schema_path),
    }
    direct_native = adapter_profile["expected"]["native_records"]
    derived_count = len(context["derived_ids"])
    release = admission["publication"]

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": adapter_profile["migration_id"],
        "migration_mode": "lossless-zero-copy-streaming-additive-native-backend-adapter",
        "source": {
            "dataset_id": manifest["volume_id"],
            "dataset_version": manifest["schema_version"],
            "course_role": manifest["course_role"],
            "curriculum_band": adapter_profile["curriculum_band"],
            "schema_name": manifest["schema_name"],
            "schema_version": manifest["schema_version"],
            "backend_root": adapter_profile["source"]["backend_root"],
            "manifest_path": adapter_profile["source"]["manifest_path"],
            "manifest_bytes": manifest_path.stat().st_size,
            "manifest_sha256": sha256_file(manifest_path),
            "record_schema": native_schema_fact,
            "record_count": direct_native,
            "record_counts": native["counts"],
            "view_counts": native["view_counts"],
            "view_jsonl_bytes": native["view_line_bytes"],
            "inventory_files_including_manifest": len(authority["inventory"]) + 1,
            "inventory_bytes_including_manifest": sum(item["bytes"] for item in authority["inventory"])
            + manifest_path.stat().st_size,
            "inventory_binding_sha256": authority["inventory_binding_sha256"],
            "accepted_tree_sha256": adapter_profile["frozen_authority"]["accepted_backend_tree_sha256"],
            "input_fingerprint_sha256": adapter_profile["frozen_authority"]["accepted_input_fingerprint_sha256"],
            "admission": authority["authority_facts"]["admission"],
            "handoff": authority["authority_facts"]["handoff"],
            "adapter_profile": adapter_profile_fact,
            "source_commit": manifest["edition_commit"],
            "target_locale": manifest["locale"],
            "owner_translation_state": admission["edition"]["translation_state"],
        },
        "target": {
            **backend_metadata(context, schema),
            "schema_path": portable(args.schema, args.schema.parents[1]),
            "schema_bytes": args.schema.stat().st_size,
            "schema_sha256": sha256_file(args.schema),
            "source_profile_schema_path": portable(
                args.source_profile_schema, args.source_profile_schema.parents[2]
            ),
            "source_profile_schema_bytes": args.source_profile_schema.stat().st_size,
            "source_profile_schema_sha256": sha256_file(args.source_profile_schema),
            "record_count": first["record_count"],
            "table_count": first["table_count"],
            "nonempty_table_count": first["nonempty_table_count"],
            "virtual_records_jsonl_bytes": first["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": first["virtual_records_jsonl_sha256"],
            "canonical_backend_bytes": first["canonical_backend_bytes"],
            "canonical_backend_sha256": first["canonical_backend_sha256"],
        },
        "coverage": {
            "native_records": direct_native,
            "native_record_counts": native["counts"],
            "native_unique_uuid5_ids": len(native["known_ids"]),
            "native_schema_validations": native["native_validation_count"],
            "native_reference_ids": native["native_reference_count"],
            "native_records_reversibly_embedded": first["native_extensions"],
            "common_source_profiles": first["source_profiles"],
            "common_source_profile_locales": first["source_profile_locales"],
            "common_collxml_bindings": first["collxml_bindings"],
            "common_derived_records": derived_count,
            "module_references": manifest["module_count"],
            "one_complete_volume_not_separate_books": True,
            "concepts": manifest["curriculum_mapping"]["concepts"],
            "source_objective_mappings": manifest["curriculum_mapping"]["mapped_source_objective_items"],
            "localized_objective_occurrences": manifest["curriculum_mapping"]["localized_overlay"][
                "localized_objective_accounting"
            ]["localized_objective_items"],
            "prerequisite_edges": manifest["curriculum_mapping"]["concept_prerequisite_relations"],
            "prerequisite_graph_acyclic": manifest["validation"]["concept_dag_acyclic_and_endpoints_resolved"],
            "assets": manifest["asset_closure"]["files"],
            "asset_occurrences": manifest["asset_closure"]["occurrences"],
            "asset_bytes": manifest["asset_closure"]["bytes"],
            "correction_ledger": manifest["terminology_and_adverse_ledger"],
            "unbound_native_terms_bound_to_adapter_technical_concept": native["null_concept_terms"],
            "target_only_localized_correction_units": len(native["target_only_localized_units"]),
            "target_only_unit_identity_rule": adapter_profile["derived"][
                "target_only_unit_identity_rule"
            ],
            "target_only_projection_is_structural_only": True,
            "source_collection_structural_units": native["source_collection_structural_units"],
            "target_collection_structural_occurrences": native[
                "target_collection_structural_occurrences"
            ],
            "source_collection_segments": len(native["collection_segment_ids"]),
            "source_collection_expressions": len(
                native["source_collection_expression_segment_ids"]
            ),
            "target_collection_expressions": len(
                native["target_collection_expression_segment_ids"]
            ),
            "target_only_correction_segments": len(
                native["target_only_correction_segment_ids"]
            ),
            "target_only_correction_expressions": len(
                native["target_only_correction_expression_segment_ids"]
            ),
            "external_target_units": len(native["external_target_unit_ids"]),
            "external_target_inventory_bytes": native["external_target_inventory_bytes"],
            "external_target_inventory_sha256": native[
                "external_target_inventory_sha256"
            ],
            "external_target_proof": {
                "records": len(native["external_target_unit_ids"]),
                "unique_ids": len(native["external_target_unit_ids"]),
                "unique_locators": len(native["external_target_unit_ids"]),
                "unique_source_keys": len(native["external_target_unit_ids"]),
                "unique_content_hashes": len(native["external_target_unit_ids"]),
                "content_hash_equals_sha256_utf8_locator": len(
                    native["external_target_unit_ids"]
                ),
                "absolute_https_without_userinfo": len(native["external_target_unit_ids"]),
                "source_xml_path_null": len(native["external_target_unit_ids"]),
                "source_profile_extensions": 0,
                "canonical_inventory_bytes": native["external_target_inventory_bytes"],
                "canonical_inventory_sha256": native[
                    "external_target_inventory_sha256"
                ],
            },
            "collection_xml_authorities": authority["collection_files"],
            "locale_neutral_shared_curriculum": manifest["validation"][
                "shared_curriculum_records_are_locale_invariant"
            ],
            "localized_text_is_overlay_only": True,
            "source_and_component_rights_preserved": True,
            "no_overlap_scope": adapter_profile["no_overlap"],
            "authority_adjudication": {
                "correction_ledger": {
                    "controlling_facts": "admission JSON plus emitted backend manifest and records",
                    "controlling_records": 95,
                    "controlling_corrections": 75,
                    "handoff_prose_records": 94,
                    "handoff_prose_corrections": 74,
                    "disposition": "handoff prose is stale; no owner bytes were rewritten",
                },
                "github_release_asset_count": {
                    "controlling_facts": "admission JSON",
                    "admission_count": 7,
                    "handoff_prose_count": 6,
                    "disposition": "handoff prose is stale; central adapter binds the admission JSON",
                },
            },
        },
        "transformation": {
            "owner_files_modified": 0,
            "native_records_modified": 0,
            "native_payload_fields_modified": 0,
            "native_ids_changed": 0,
            "native_uuid5_ids_preserved": direct_native,
            "direct_common_records": direct_native,
            "derived_common_records": derived_count,
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "localized_unit_mapping": "occurrence",
            "source_and_target_expression_mapping": "segment_variant",
            "source_and_target_cnxml_binding": "strict interlanguage.source-profile plus derived module file revisions",
            "external_target_unit_mapping": "direct unit projection with preserved unique HTTPS source_path and no false XML profile",
            "collection_xml_projection": {
                "source_structural_units": native["source_collection_structural_units"],
                "target_structural_occurrences": native[
                    "target_collection_structural_occurrences"
                ],
                "source_segments": len(native["collection_segment_ids"]),
                "source_expressions": len(native["source_collection_expression_segment_ids"]),
                "target_expressions": len(native["target_collection_expression_segment_ids"]),
                "common_collxml_bindings": first["collxml_bindings"],
                "derived_file_records": 1,
                "derived_file_revision_records": 2,
                "profile_disposition": "native-exact CollXML extension plus common file/revision binding; no CNXML profile mislabeling",
                "semantic_invention": False,
                "native_payloads_preserved_in_reversible_extensions": True,
            },
            "target_only_localized_correction_projection": {
                "native_records": len(native["target_only_localized_units"]),
                "derived_technical_units": len(native["target_only_localized_units"]),
                "native_segments_without_source_locator": len(
                    native["target_only_correction_segment_ids"]
                ),
                "target_expressions_without_source_variant": len(
                    native["target_only_correction_expression_segment_ids"]
                ),
                "identity_rule": adapter_profile["derived"]["target_only_unit_identity_rule"],
                "semantic_invention": False,
                "native_null_preserved_in_reversible_extension": True,
            },
            "derived_records_materialized": False,
        },
        "validation": {
            "result": "pass",
            "frozen_admission_size_sha256": "pass",
            "frozen_handoff_size_sha256": "pass",
            "native_manifest_size_sha256": "pass",
            "native_all_48_declared_members_size_sha256": "pass",
            "native_inventory_files_including_manifest": len(authority["inventory"]) + 1,
            "native_inventory_bytes_including_manifest": sum(item["bytes"] for item in authority["inventory"])
            + manifest_path.stat().st_size,
            "native_schema_records": native["native_validation_count"],
            "native_canonical_jsonl": "pass",
            "native_per_view_id_order": "strict ascending",
            "native_global_id_uniqueness": "pass",
            "native_foreign_key_closure": "pass",
            "native_csv_round_trip_owner_proof": "pass",
            "native_sqlite_projection_owner_proof": "pass",
            "native_second_full_build_owner_proof": "byte-identical",
            "strict_common_backend_schema": "pass",
            "strict_source_profile_schema": "pass",
            "common_collxml_bindings": first["collxml_bindings"],
            "common_global_id_uniqueness": "pass",
            "common_global_stable_key_uniqueness": "pass",
            "common_foreign_key_closure": "pass",
            "common_table_inventory": f"{first['table_count']}/{first['table_count']} present",
            "exact_native_reverse_extraction": direct_native,
            "byte_identical_native_reverse_extractions": first[
                "exact_native_reverse_extractions"
            ],
            "native_null_canonical_unit_ids_recovered": first[
                "native_null_canonical_unit_ids_recovered"
            ],
            "source_and_target_collection_xml_authority_binding": "pass",
            "two_independent_streaming_assemblies": "byte-identical",
            "first_canonical_backend_sha256": first["canonical_backend_sha256"],
            "second_canonical_backend_sha256": second["canonical_backend_sha256"],
            "first_virtual_records_jsonl_sha256": first["virtual_records_jsonl_sha256"],
            "second_virtual_records_jsonl_sha256": second["virtual_records_jsonl_sha256"],
        },
        "tables": first["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The exact 1.84 GB owner backend plus this bounded streaming adapter reconstruct the strict common backend twice; no redundant record materialization is written.",
            "script_path": "scripts/migrate-prealgebra2e-backend-v1.py",
            "migration_script": file_fact(
                Path(__file__).resolve(), "scripts/migrate-prealgebra2e-backend-v1.py"
            ),
            "adapter_profile_path": "backend/migrations/prealgebra2e-id-v1/ADAPTER_PROFILE.json",
            "owner_lane": "read-only",
        },
        "public_artifacts": [
            receipt_artifact(
                corpus_root,
                corpus_root / adapter_profile["frozen_authority"]["admission"]["path"],
                "frozen owner admission",
                admission_id=admission["admission_id"],
            ),
            receipt_artifact(
                corpus_root,
                corpus_root / adapter_profile["frozen_authority"]["handoff"]["path"],
                "frozen owner handoff",
            ),
            receipt_artifact(
                backend_root,
                manifest_path,
                "admitted owner backend v0.2.5",
                records=manifest["records_total"],
            ),
            {
                "kind": "zenodo release identity",
                "status": "owner reports anonymous full-byte readback PASS",
                "concept_doi": release["zenodo"]["concept_doi"],
                "version_doi": release["zenodo"]["version_doi"],
                "record_id": release["zenodo"]["version_record_id"],
            },
            {
                "kind": "github release identity",
                "status": release["github"]["state"],
                "release_url": release["github"]["release_url"],
                "pages_url": release["github"]["pages_url"],
                "commit": release["github"]["main_commit"],
                "release_asset_bytes": release["github"]["release_asset_bytes"],
                "pages_files": release["github"]["pages_files"],
                "pages_bytes": release["github"]["pages_bytes"],
            },
        ],
        "credentials_recorded": False,
    }

    Draft202012Validator(receipt_schema, format_checker=FormatChecker()).validate(receipt)
    write_json(args.output_receipt, receipt)
    print(
        canonical(
            {
                "result": "pass",
                "native_records": direct_native,
                "derived_records": derived_count,
                "target_records": first["record_count"],
                "tables": first["table_count"],
                "nonempty_tables": first["nonempty_table_count"],
                "virtual_records_jsonl_bytes": first["virtual_records_jsonl_bytes"],
                "virtual_records_jsonl_sha256": first["virtual_records_jsonl_sha256"],
                "canonical_backend_sha256": first["canonical_backend_sha256"],
                "receipt": args.output_receipt.resolve().as_posix(),
                "receipt_sha256": sha256_file(args.output_receipt),
            }
        )
    )


if __name__ == "__main__":
    main()
