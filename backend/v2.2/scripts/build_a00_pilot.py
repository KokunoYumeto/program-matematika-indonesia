#!/usr/bin/env python3
"""Build the deterministic zero-copy A00 lane package for backend v2.2."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from v22_common import (
    IDENTITY_FORMULA,
    IDENTITY_NAMESPACE,
    assert_hash_fact,
    canonical_json_bytes,
    combined_digest,
    envelope,
    file_fact,
    global_id,
    iter_jsonl,
    load_json,
    media_type_for,
    sha256_bytes,
    sha256_path,
    strip_sha256_prefix,
    write_bytes,
    write_json,
    write_jsonl,
)


V22_ROOT = Path(__file__).resolve().parent.parent
PROGRAM_ROOT = V22_ROOT.parent.parent
OWNER_ROOT = PROGRAM_ROOT.parent / "openstax-prealgebra"
PROFILE_SOURCE = V22_ROOT / "profiles" / "a00-lane-profile.json"
STATE_SOURCE = V22_ROOT / "state-vocabulary-v2.2.json"
SCHEMA_ROOT = V22_ROOT / "schema"
PACKAGE_NAME = "a00-openstax-prealgebra-v0.1.0"
DEFAULT_OUTPUT = V22_ROOT / "packages" / PACKAGE_NAME
RECORDED_AT = "2026-08-27T00:00:00Z"

TABLE_ORDER = [
    "owner_authorities",
    "datasets",
    "editions",
    "units",
    "course_unit_memberships",
    "native_bindings",
    "content_bindings",
    "relations",
    "rights",
    "rights_assignments",
    "artifacts",
    "build_recipes",
    "reader_surfaces",
    "routes",
    "search_documents",
    "adapter_profiles",
    "adapter_runs",
    "qa_events",
    "identity_crosswalks",
]

TABLE_RECORD_TYPES = {
    "owner_authorities": "owner_authority",
    "datasets": "dataset",
    "editions": "edition",
    "units": "unit",
    "course_unit_memberships": "course_unit_membership",
    "native_bindings": "native_binding",
    "content_bindings": "content_binding",
    "relations": "relation",
    "rights": "rights",
    "rights_assignments": "rights_assignment",
    "artifacts": "artifact",
    "build_recipes": "build_recipe",
    "reader_surfaces": "reader_surface",
    "routes": "route",
    "search_documents": "search_document",
    "adapter_profiles": "adapter_profile",
    "adapter_runs": "adapter_run",
    "qa_events": "qa_event",
    "identity_crosswalks": "identity_crosswalk",
}


def validate_json(instance: Any, schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{label}{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
            for error in errors[:20]
        )
        raise ValueError(rendered)


def binding_id(key: str) -> str:
    return global_id("content_binding", f"a00:prealgebra2e-volume:content:{key}")


def record_id(record_type: str, key: str) -> str:
    return global_id(record_type, f"a00:prealgebra2e-volume:{key}")


def external_path(expectation: dict[str, Any], owner_backend_root: Path) -> Path:
    bases = {
        "program_repository_root": PROGRAM_ROOT,
        "owner_repository_root": OWNER_ROOT,
        "owner_backend_root": owner_backend_root,
    }
    return bases[expectation["locator_base"]] / Path(expectation["path"])


def verify_profile_inputs(profile: dict[str, Any], owner_backend_root: Path) -> None:
    expectations = [
        profile["native_authority"]["manifest"],
        profile["native_authority"]["migration_receipt"],
        *profile["central_registry_inputs"],
    ]
    for expectation in expectations:
        path = external_path(expectation, owner_backend_root)
        assert_hash_fact(path, expectation["bytes"], expectation["sha256"])


def load_pilot_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    pilot_root = PROGRAM_ROOT / "backend" / "v2.1" / "pilots" / "a00-prealgebra"
    units = [row for row, _ in iter_jsonl(pilot_root / "units.jsonl")]
    search = {
        row["stable_unit_id"]: row
        for row, _ in iter_jsonl(pilot_root / "search.jsonl")
    }
    if len(units) != 75 or len(search) != 75:
        raise ValueError(f"A00 pilot count mismatch: units={len(units)} search={len(search)}")
    units.sort(key=lambda row: row["order_index"])
    return units, search


def scan_native_backend(
    owner_manifest: dict[str, Any],
    owner_backend_root: Path,
    module_native_ids: set[str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    views = sorted(
        (entry for entry in owner_manifest["files"] if entry.get("format") == "jsonl"),
        key=lambda entry: entry["path"],
    )
    if len(views) != 17:
        raise ValueError(f"expected 17 native JSONL views, found {len(views)}")

    seen_ids: set[bytes] = set()
    view_facts: list[dict[str, Any]] = []
    module_rows: dict[str, dict[str, Any]] = {}
    total_records = 0

    for declared in views:
        path = owner_backend_root / declared["path"]
        assert_hash_fact(path, declared["bytes"], declared["sha256"])
        id_digest_parts: list[bytes] = []
        first_id: str | None = None
        last_id: str | None = None
        count = 0
        for row, raw in iter_jsonl(path):
            if canonical_json_bytes(row) != raw:
                raise ValueError(f"noncanonical owner JSONL row in {path} at record {count + 1}")
            native_id = row.get("id")
            if not isinstance(native_id, str) or not native_id.startswith("urn:uuid:"):
                raise ValueError(f"missing native UUID in {path} at record {count + 1}")
            native_uuid = uuid.UUID(native_id.removeprefix("urn:uuid:")).bytes
            if native_uuid in seen_ids:
                raise ValueError(f"duplicate owner-native record ID: {native_id}")
            seen_ids.add(native_uuid)
            id_digest_parts.append((native_id + "\n").encode("ascii"))
            first_id = first_id or native_id
            last_id = native_id
            count += 1
            if declared["path"] == "content/units.jsonl" and native_id in module_native_ids:
                module_rows[native_id] = {
                    "bytes": len(raw),
                    "sha256": sha256_bytes(raw),
                    "row": row,
                }
        if count != declared["records"]:
            raise ValueError(
                f"native record count mismatch for {declared['path']}: {count} != {declared['records']}"
            )
        total_records += count
        view_facts.append(
            {
                "locator_base": "owner_backend_root",
                "path": declared["path"],
                "record_type": declared["record_type"],
                "records": count,
                "bytes": declared["bytes"],
                "sha256": strip_sha256_prefix(declared["sha256"]),
                "record_id_sequence_sha256": sha256_bytes(b"".join(id_digest_parts)),
                "first_record_id": first_id,
                "last_record_id": last_id,
                "canonical_jsonl": True,
            }
        )

    if total_records != owner_manifest["records_total"]:
        raise ValueError(f"native total mismatch: {total_records} != {owner_manifest['records_total']}")
    if set(module_rows) != module_native_ids:
        missing = sorted(module_native_ids - set(module_rows))
        raise ValueError(f"native module row closure failed; missing {missing}")

    id_set_sha256 = sha256_bytes(b"".join(sorted(seen_ids)))
    index = {
        "schema_id": "interlanguage/global-modular-mathematics-native-shard-index/2.2.0",
        "schema_version": "2.2.0",
        "dataset_key": "prealgebra2e-volume",
        "recorded_at": RECORDED_AT,
        "owner_native_manifest": {
            "bytes": 61129,
            "sha256": "e27b23f6bff5c56949e149af6decb8ecd9d7bf30ab049d65a5dd344e232b913d",
        },
        "record_count": total_records,
        "record_counts": owner_manifest["records_by_type"],
        "view_count": len(view_facts),
        "views": view_facts,
        "record_ids_unique": True,
        "native_record_id_set_sha256": id_set_sha256,
        "zero_copy": True,
        "reverse_recipe": "For every view, re-read the exact hash-bound JSONL bytes in order and select every row; for projected units select exactly one row by native UUID.",
    }
    return index, module_rows


def copy_runtime_files(output: Path) -> None:
    sources = {
        PROFILE_SOURCE: output / "profiles" / "a00-lane-profile.json",
        STATE_SOURCE: output / "state-vocabulary-v2.2.json",
        SCHEMA_ROOT / "record-v2.2.schema.json": output / "schema" / "record-v2.2.schema.json",
        SCHEMA_ROOT / "manifest-v2.2.schema.json": output / "schema" / "manifest-v2.2.schema.json",
        SCHEMA_ROOT / "lane-profile-v2.2.schema.json": output / "schema" / "lane-profile-v2.2.schema.json",
        SCHEMA_ROOT / "state-vocabulary-v2.2.schema.json": output / "schema" / "state-vocabulary-v2.2.schema.json",
        Path(__file__).resolve(): output / "tools" / "build_a00_pilot.py",
        Path(__file__).resolve().parent / "validate_v22_package.py": output / "tools" / "validate_v22_package.py",
        Path(__file__).resolve().parent / "v22_common.py": output / "tools" / "v22_common.py",
    }
    for source, target in sources.items():
        write_bytes(target, source.read_bytes())


def make_content_binding(
    *,
    key: str,
    dataset_id: str,
    owner_authority_id: str,
    state_profile_id: str,
    subject_id: str,
    role: str,
    locator_base: str,
    locator: str,
    evidence_state: str,
    media_type: str,
    bytes_value: int | None,
    sha256: str | None,
    selector_kind: str = "none",
    locale: str | None = None,
    provenance_binding_ids: list[str] | None = None,
    public_uri: str | None = None,
    selector: dict[str, Any] | None = None,
    upstream_commit: str | None = None,
    limitation: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "subject_id": subject_id,
        "role": role,
        "locator_base": locator_base,
        "locator": locator,
        "evidence_state": evidence_state,
        "media_type": media_type,
        "bytes": bytes_value,
        "sha256": sha256,
        "selector_kind": selector_kind,
        "locale": locale,
        "recorded_at": RECORDED_AT,
    }
    if public_uri is not None:
        payload["public_uri"] = public_uri
    if selector is not None:
        payload["selector"] = selector
    if upstream_commit is not None:
        payload["upstream_commit"] = upstream_commit
    if limitation is not None:
        payload["limitation"] = limitation
    return envelope(
        record_type="content_binding",
        semantic_key=f"a00:prealgebra2e-volume:content:{key}",
        dataset_id=dataset_id,
        owner_authority_id=owner_authority_id,
        recorded_at=RECORDED_AT,
        normalized_state="validated" if evidence_state != "verified_public" else "published",
        owner_native_state=None,
        state_profile=state_profile_id,
        provenance_binding_ids=provenance_binding_ids or [],
        payload=payload,
    )


def materialize_run(output: Path) -> dict[str, Any]:
    profile = load_json(PROFILE_SOURCE)
    state_vocabulary = load_json(STATE_SOURCE)
    validate_json(profile, load_json(SCHEMA_ROOT / "lane-profile-v2.2.schema.json"), "lane profile")
    validate_json(
        state_vocabulary,
        load_json(SCHEMA_ROOT / "state-vocabulary-v2.2.schema.json"),
        "state vocabulary",
    )
    if profile["recorded_at"] != RECORDED_AT:
        raise ValueError("A00 profile recorded_at is not the frozen build timestamp")

    owner_backend_root = OWNER_ROOT / profile["native_authority"]["backend_root"]
    verify_profile_inputs(profile, owner_backend_root)
    owner_manifest = load_json(owner_backend_root / "backend.volume.manifest.json")
    if owner_manifest["records_total"] != profile["expected_native"]["record_count"]:
        raise ValueError("owner manifest/profile native total mismatch")
    if owner_manifest["records_by_type"] != profile["expected_native"]["record_counts"]:
        raise ValueError("owner manifest/profile native per-type counts mismatch")

    pilot_units, pilot_search = load_pilot_rows()
    owner_modules = sorted(owner_manifest["modules"], key=lambda row: row["ordinal"])
    if [row["module_id"] for row in owner_modules] != [row["module_id"] for row in pilot_units]:
        raise ValueError("owner module order and v2.1 navigation pilot order differ")
    module_native_ids = {row["module_unit_id"] for row in owner_modules}

    copy_runtime_files(output)
    native_index, native_module_rows = scan_native_backend(
        owner_manifest, owner_backend_root, module_native_ids
    )
    write_json(output / "native-shard-index.json", native_index)

    identity_rows: list[dict[str, Any]] = []
    for view in native_index["views"]:
        identity_rows.append(
            {
                "kind": "native_shard_reference",
                "key": view["path"],
                "mapping_cardinality": "many_to_one",
                "native_locator": f"owner_backend_root:{view['path']}",
                "native_record_count": view["records"],
                "native_bytes": view["bytes"],
                "native_sha256": view["sha256"],
                "native_record_id_sequence_sha256": view["record_id_sequence_sha256"],
                "reverse_recipe": f"select every JSONL row in ordinal order from {view['path']}",
                "zero_copy": True,
            }
        )

    projected_units: list[dict[str, Any]] = []
    for owner_module, pilot_unit in zip(owner_modules, pilot_units, strict=True):
        unit_key = f"unit:{owner_module['module_id']}:{owner_module['module_unit_id'].removeprefix('urn:uuid:')}"
        projected_unit_id = record_id("unit", unit_key)
        native_fact = native_module_rows[owner_module["module_unit_id"]]
        identity_rows.append(
            {
                "kind": "projected_unit",
                "key": owner_module["module_id"],
                "mapping_cardinality": "one_to_one",
                "native_id": owner_module["module_unit_id"],
                "native_locator": f"owner_backend_root:content/units.jsonl#id={owner_module['module_unit_id']}",
                "native_row_bytes": native_fact["bytes"],
                "native_row_sha256": native_fact["sha256"],
                "projected_record_id": projected_unit_id,
                "projected_record_type": "unit",
                "reverse_recipe": f"jsonl_id(content/units.jsonl,{owner_module['module_unit_id']})",
                "zero_copy": True,
            }
        )
        projected_units.append(
            {
                "owner": owner_module,
                "pilot": pilot_unit,
                "search": pilot_search[pilot_unit["stable_unit_id"]],
                "native": native_fact,
                "unit_key": unit_key,
                "unit_id": projected_unit_id,
            }
        )
    identity_rows.sort(key=lambda row: (row["kind"], row["key"]))
    write_bytes(output / "identity-map.jsonl", b"".join(canonical_json_bytes(row) for row in identity_rows))

    loss_report = {
        "schema_id": "interlanguage/global-modular-mathematics-capability-loss-report/2.2.0",
        "schema_version": "2.2.0",
        "dataset_key": profile["dataset_key"],
        "recorded_at": RECORDED_AT,
        "capabilities": profile["capability_policy"],
        "unexplained_native_record_loss": 0,
        "native_records_copied": 0,
        "native_records_referenced": native_index["record_count"],
        "projected_navigation_units": len(projected_units),
        "assessment_semantics_inferred": False,
        "accessibility_state_upgraded": False,
        "result": "pass",
    }
    write_json(output / "capability-loss-report.json", loss_report)

    reverse_report = {
        "schema_id": "interlanguage/global-modular-mathematics-reverse-extraction-report/2.2.0",
        "schema_version": "2.2.0",
        "dataset_key": profile["dataset_key"],
        "recorded_at": RECORDED_AT,
        "native_view_count": native_index["view_count"],
        "native_record_count": native_index["record_count"],
        "native_record_id_set_sha256": native_index["native_record_id_set_sha256"],
        "projected_unit_bindings": len(projected_units),
        "one_to_one_unit_bindings": len(projected_units),
        "missing_native_selectors": 0,
        "ambiguous_native_selectors": 0,
        "byte_identical_native_view_replay": True,
        "exact_projected_selector_replay": True,
        "result": "pass",
    }
    write_json(output / "reverse-extraction-report.json", reverse_report)

    core_paths = [
        output / "native-shard-index.json",
        output / "identity-map.jsonl",
        output / "capability-loss-report.json",
        output / "reverse-extraction-report.json",
    ]
    core_facts = [
        file_fact(output, path, role="projection_core", media_type=media_type_for(path.name))
        for path in core_paths
    ]
    core_digest = combined_digest(core_facts)
    projection_inventory = {
        "schema_id": "interlanguage/global-modular-mathematics-projection-inventory/2.2.0",
        "schema_version": "2.2.0",
        "dataset_key": profile["dataset_key"],
        "recorded_at": RECORDED_AT,
        "files": sorted(core_facts, key=lambda item: item["path"]),
        "projection_digest_sha256": core_digest,
        "native_record_count": native_index["record_count"],
        "projected_navigation_unit_count": len(projected_units),
        "zero_copy": True,
    }
    write_json(output / "projection-inventory.json", projection_inventory)

    dataset_id = record_id("dataset", "dataset")
    owner_authority_id = record_id("owner_authority", "owner-authority")
    edition_id = record_id("edition", "edition:id-ID:0.2.7")
    rights_id = record_id("rights", "rights:bundle-default")
    adapter_profile_id = record_id("adapter_profile", "adapter-profile:0.1.0")
    adapter_run_id = record_id("adapter_run", "adapter-run:0.1.0")
    qa_event_id = record_id("qa_event", "qa:deterministic-zero-copy:0.1.0")
    package_id = global_id("package_ref", "a00:prealgebra2e-volume:v2.2:0.1.0")
    course_id = profile["external_record_ids"][0]
    state_profile_id = profile["state_profile_id"]

    owner_manifest_binding_id = binding_id("owner-native-manifest")
    profile_binding_id = binding_id("lane-profile")
    builder_binding_id = binding_id("builder-executable")
    validator_binding_id = binding_id("validator-executable")
    record_schema_binding_id = binding_id("record-schema")
    native_schema_binding_id = binding_id("native-record-schema")
    projection_inventory_binding_id = binding_id("projection-inventory")
    identity_map_binding_id = binding_id("identity-map")
    native_index_binding_id = binding_id("native-shard-index")
    loss_report_binding_id = binding_id("capability-loss-report")
    reverse_report_binding_id = binding_id("reverse-extraction-report")

    content_bindings: list[dict[str, Any]] = []

    def add_local_binding(
        key: str,
        subject_id: str,
        role: str,
        relative_path: str,
        *,
        locale: str | None = None,
        provenance: list[str] | None = None,
    ) -> str:
        path = output / relative_path
        content_bindings.append(
            make_content_binding(
                key=key,
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=subject_id,
                role=role,
                locator_base="package_root",
                locator=relative_path,
                evidence_state="verified_local",
                media_type=media_type_for(relative_path),
                bytes_value=path.stat().st_size,
                sha256=sha256_path(path),
                locale=locale,
                provenance_binding_ids=provenance,
            )
        )
        return binding_id(key)

    content_bindings.append(
        make_content_binding(
            key="owner-native-manifest",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            state_profile_id=state_profile_id,
            subject_id=dataset_id,
            role="manifest",
            locator_base="owner_backend_root",
            locator="backend.volume.manifest.json",
            evidence_state="verified_local",
            media_type="application/json",
            bytes_value=61129,
            sha256="e27b23f6bff5c56949e149af6decb8ecd9d7bf30ab049d65a5dd344e232b913d",
        )
    )
    add_local_binding("lane-profile", adapter_profile_id, "build_input", "profiles/a00-lane-profile.json", provenance=[owner_manifest_binding_id])
    add_local_binding("builder-executable", adapter_profile_id, "adapter_executable", "tools/build_a00_pilot.py", provenance=[profile_binding_id])
    add_local_binding("validator-executable", qa_event_id, "qa_evidence", "tools/validate_v22_package.py", provenance=[profile_binding_id])
    add_local_binding("record-schema", dataset_id, "schema", "schema/record-v2.2.schema.json", provenance=[profile_binding_id])
    add_local_binding("state-vocabulary", dataset_id, "schema", "state-vocabulary-v2.2.json", provenance=[profile_binding_id])
    add_local_binding("projection-inventory", adapter_run_id, "build_output", "projection-inventory.json", provenance=[builder_binding_id, owner_manifest_binding_id])
    add_local_binding("identity-map", adapter_run_id, "build_output", "identity-map.jsonl", provenance=[builder_binding_id, owner_manifest_binding_id])
    add_local_binding("native-shard-index", dataset_id, "build_output", "native-shard-index.json", provenance=[builder_binding_id, owner_manifest_binding_id])
    add_local_binding("capability-loss-report", adapter_run_id, "qa_evidence", "capability-loss-report.json", provenance=[builder_binding_id, profile_binding_id])
    add_local_binding("reverse-extraction-report", adapter_run_id, "qa_evidence", "reverse-extraction-report.json", provenance=[builder_binding_id, native_index_binding_id])

    native_schema = owner_manifest["record_schema"]
    content_bindings.append(
        make_content_binding(
            key="native-record-schema",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            state_profile_id=state_profile_id,
            subject_id=dataset_id,
            role="schema",
            locator_base="owner_repository_root",
            locator=native_schema["path_locator"],
            evidence_state="verified_local",
            media_type="application/schema+json",
            bytes_value=native_schema["bytes"],
            sha256=strip_sha256_prefix(native_schema["sha256"]),
            provenance_binding_ids=[owner_manifest_binding_id],
        )
    )

    for index, view in enumerate(native_index["views"], start=1):
        content_bindings.append(
            make_content_binding(
                key=f"native-view-{index:02d}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=dataset_id,
                role="native_record",
                locator_base="owner_backend_root",
                locator=view["path"],
                evidence_state="verified_local",
                media_type="application/x-ndjson",
                bytes_value=view["bytes"],
                sha256=view["sha256"],
                provenance_binding_ids=[owner_manifest_binding_id, native_index_binding_id],
            )
        )

    source_collection = owner_manifest["source_collection"]
    target_collection = owner_manifest["localized_collection"]
    source_collection_binding_id = binding_id("source-collection")
    target_collection_binding_id = binding_id("target-collection")
    for key, role, item, locale in (
        ("source-collection", "source", source_collection, "en-US"),
        ("target-collection", "target", target_collection, "id-ID"),
    ):
        content_bindings.append(
            make_content_binding(
                key=key,
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=edition_id,
                role=role,
                locator_base="owner_repository_root",
                locator=item["path_locator"],
                evidence_state="verified_local",
                media_type="application/xml",
                bytes_value=item["bytes"],
                sha256=strip_sha256_prefix(item["sha256"]),
                locale=locale,
                provenance_binding_ids=[owner_manifest_binding_id],
                upstream_commit=owner_manifest["edition_commit"],
            )
        )

    rights_view_binding_id = binding_id("native-view-14")
    pilot_rights_path = PROGRAM_ROOT / "backend" / "v2.1" / "pilots" / "a00-prealgebra" / "rights_accessibility.json"
    pilot_rights_binding_id = binding_id("pilot-rights-accessibility")
    content_bindings.append(
        make_content_binding(
            key="pilot-rights-accessibility",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            state_profile_id=state_profile_id,
            subject_id=rights_id,
            role="rights_evidence",
            locator_base="program_repository_root",
            locator="backend/v2.1/pilots/a00-prealgebra/rights_accessibility.json",
            evidence_state="verified_local",
            media_type="application/json",
            bytes_value=pilot_rights_path.stat().st_size,
            sha256=sha256_path(pilot_rights_path),
            provenance_binding_ids=[owner_manifest_binding_id],
        )
    )

    records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    records["owner_authorities"].append(
        envelope(
            record_type="owner_authority",
            semantic_key="a00:prealgebra2e-volume:owner-authority",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state="mathematically_reviewed",
            state_profile=state_profile_id,
            provenance_binding_ids=[owner_manifest_binding_id],
            payload={
                "owner_key": "openstax-prealgebra",
                "authority_kind": "repository_authority",
                "authority_locator": "owner_repository_root:openstax-prealgebra",
                "corpus_ids": ["prealgebra2e-volume"],
                "course_ids": [course_id],
                "native_schema_name": owner_manifest["schema_name"],
                "native_schema_version": owner_manifest["schema_version"],
                "native_manifest_binding_id": owner_manifest_binding_id,
                "authority_scope": "owner-native semantic corpus and edition lineage",
                "responsible_workflow": owner_manifest["responsible_workflow"],
                "public_repository_url": "https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID",
                "release_lineage_url": "https://doi.org/10.5281/zenodo.22070683",
                "sole_integrator_publisher": True,
            },
        )
    )

    records["editions"].append(
        envelope(
            record_type="edition",
            semantic_key="a00:prealgebra2e-volume:edition:id-ID:0.2.7",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state="mathematically_reviewed",
            state_profile=state_profile_id,
            provenance_binding_ids=[owner_manifest_binding_id, source_collection_binding_id, target_collection_binding_id],
            payload={
                "owner_authority_id": owner_authority_id,
                "locale": "id-ID",
                "title": "Prealjabar 2e — Edisi Bahasa Indonesia",
                "version_label": "0.2.7",
                "source_format": "CNXML/CollXML",
                "rights_id": rights_id,
                "source_binding_ids": [source_collection_binding_id],
                "target_binding_ids": [target_collection_binding_id],
                "upstream_commit": owner_manifest["edition_commit"],
                "edition_notes": "Proyeksi v2.2 tanpa salinan prosa; korpus native tetap otoritatif.",
            },
        )
    )

    records["rights"].append(
        envelope(
            record_type="rights",
            semantic_key="a00:prealgebra2e-volume:rights:bundle-default",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state="published",
            state_profile=state_profile_id,
            provenance_binding_ids=[rights_view_binding_id, pilot_rights_binding_id],
            payload={
                "license_expression": "CC BY-NC-SA 4.0",
                "access_state": "public",
                "redistribution": "allowed_with_license_terms",
                "adaptation": "allowed_with_license_terms",
                "attribution": True,
                "authority": "owner-native registry/rights.jsonl",
                "third_party_status": "18_component_exceptions_preserved_in_native_shard",
                "change_notice": True,
                "nonendorsement": False,
                "source_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                "component_exceptions": 18,
            },
        )
    )

    adapter_profile_payload = {
        "adapter_id": "a00-openstax-zero-copy-v2.2",
        "adapter_version": "0.1.0",
        "native_schema_name": owner_manifest["schema_name"],
        "native_schema_version": owner_manifest["schema_version"],
        "executable_binding_id": builder_binding_id,
        "input_view_mappings": [
            {"native_view": view["path"], "projection": "zero_copy_native_shard_reference"}
            for view in native_index["views"]
        ] + [
            {"native_view": "backend/v2.1/pilots/a00-prealgebra/units.jsonl", "projection": "learner_navigation_units_routes"},
            {"native_view": "backend/v2.1/pilots/a00-prealgebra/search.jsonl", "projection": "bounded_search_documents"},
        ],
        "identity_rules": [
            "Preserve owner-native UUIDs only as native identities; derive v2.2 IDs from record_type plus locale-neutral semantic key.",
            "Never derive identity from localized title, prose, route URL, page number, or build time.",
        ],
        "state_map": state_vocabulary["profiles"][0]["mappings"],
        "cardinality_rules": [
            "Each of the 75 visible module roots maps one-to-one to exactly one owner-native unit UUID.",
            "Each of the 17 owner JSONL views maps many native rows to one zero-copy shard reference.",
        ],
        "loss_policy": [entry["reason"] for entry in profile["capability_policy"] if entry["state"] in {"not_projected", "absent"}],
        "zero_copy": True,
        "source_profile_schema_binding_id": profile_binding_id,
        "native_schema_binding_id": native_schema_binding_id,
        "capability_map": {entry["name"]: entry["state"] for entry in profile["capability_policy"]},
        "known_limitations": profile["limitations"],
    }
    records["adapter_profiles"].append(
        envelope(
            record_type="adapter_profile",
            semantic_key="a00:prealgebra2e-volume:adapter-profile:0.1.0",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state=None,
            state_profile=state_profile_id,
            provenance_binding_ids=[profile_binding_id, builder_binding_id, owner_manifest_binding_id],
            payload=adapter_profile_payload,
        )
    )

    artifact_ids: list[str] = []
    surface_ids: list[str] = []
    route_ids: list[str] = []
    unit_ids: list[str] = []

    for projected in projected_units:
        owner_module = projected["owner"]
        pilot_unit = projected["pilot"]
        search_row = projected["search"]
        unit_id = projected["unit_id"]
        module_id = owner_module["module_id"]
        unit_ids.append(unit_id)

        native_binding_record_id = record_id("native_binding", f"native-binding:{module_id}")
        native_row_binding_id = binding_id(f"native-row:{module_id}")
        source_binding_id = binding_id(f"source-cnxml:{module_id}")
        target_binding_id = binding_id(f"target-cnxml:{module_id}")
        html_binding_id = binding_id(f"reader-html:{module_id}")

        content_bindings.append(
            make_content_binding(
                key=f"native-row:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=unit_id,
                role="native_record",
                locator_base="owner_backend_root",
                locator="content/units.jsonl",
                evidence_state="verified_local",
                media_type="application/x-ndjson",
                bytes_value=projected["native"]["bytes"],
                sha256=projected["native"]["sha256"],
                selector_kind="native_id",
                locale=None,
                provenance_binding_ids=[owner_manifest_binding_id, native_index_binding_id],
                selector={"native_id": owner_module["module_unit_id"]},
            )
        )
        content_bindings.append(
            make_content_binding(
                key=f"source-cnxml:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=unit_id,
                role="source",
                locator_base="upstream_frozen_commit",
                locator=pilot_unit["native_locator"]["source"],
                evidence_state="declared",
                media_type="application/xml",
                bytes_value=owner_module["source_bytes"],
                sha256=strip_sha256_prefix(owner_module["source_sha256"]),
                locale="en-US",
                provenance_binding_ids=[owner_manifest_binding_id],
                public_uri=pilot_unit["native_locator"]["source"],
                upstream_commit=owner_manifest["edition_commit"],
                limitation="Source bytes are hash-bound by the frozen owner witness manifest and are not copied into this package.",
            )
        )
        target_path = OWNER_ROOT / pilot_unit["native_locator"]["target"]
        assert_hash_fact(target_path, owner_module["target_bytes"], owner_module["target_sha256"])
        content_bindings.append(
            make_content_binding(
                key=f"target-cnxml:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=unit_id,
                role="target",
                locator_base="owner_repository_root",
                locator=pilot_unit["native_locator"]["target"],
                evidence_state="verified_local",
                media_type="application/xml",
                bytes_value=owner_module["target_bytes"],
                sha256=strip_sha256_prefix(owner_module["target_sha256"]),
                locale="id-ID",
                provenance_binding_ids=[owner_manifest_binding_id],
            )
        )

        html_locator = pilot_unit["learner_route"]["local_evidence_locator"]
        html_path = OWNER_ROOT / html_locator
        html_sha256 = pilot_unit["learner_route"]["local_evidence_sha256"]
        assert_hash_fact(html_path, html_path.stat().st_size, html_sha256)
        content_bindings.append(
            make_content_binding(
                key=f"reader-html:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                state_profile_id=state_profile_id,
                subject_id=unit_id,
                role="route_surface",
                locator_base="owner_repository_root",
                locator=html_locator,
                evidence_state="verified_local",
                media_type="text/html",
                bytes_value=html_path.stat().st_size,
                sha256=html_sha256,
                locale="id-ID",
                provenance_binding_ids=[owner_manifest_binding_id],
                public_uri=pilot_unit["learner_route"]["url"],
                limitation="Local route bytes are exact; anonymous public readback is inherited from the frozen v2.1 pilot evidence.",
            )
        )

        records["native_bindings"].append(
            envelope(
                record_type="native_binding",
                semantic_key=f"a00:prealgebra2e-volume:native-binding:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="validated",
                owner_native_state="identity_declared",
                state_profile=state_profile_id,
                provenance_binding_ids=[native_row_binding_id],
                payload={
                    "subject_id": unit_id,
                    "native_schema_name": owner_manifest["schema_name"],
                    "native_schema_version": owner_manifest["schema_version"],
                    "native_record_type": "unit",
                    "native_semantic_key": owner_module["module_unit_id"],
                    "native_locator": f"content/units.jsonl#id={owner_module['module_unit_id']}",
                    "record_binding_id": native_row_binding_id,
                    "mapping_cardinality": "one_to_one",
                    "reverse_recipe": f"jsonl_id(content/units.jsonl,{owner_module['module_unit_id']})",
                    "native_id": owner_module["module_unit_id"],
                    "owner_authority_id": owner_authority_id,
                    "native_parent_id": projected["native"]["row"].get("parent_id"),
                    "native_state": projected["native"]["row"].get("status"),
                },
            )
        )
        records["units"].append(
            envelope(
                record_type="unit",
                semantic_key=f"a00:prealgebra2e-volume:{projected['unit_key']}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state=pilot_unit["translation_state"],
                state_profile=state_profile_id,
                provenance_binding_ids=[native_row_binding_id, source_binding_id, target_binding_id],
                payload={
                    "edition_id": edition_id,
                    "native_binding_id": native_binding_record_id,
                    "identity_scope": "locale_neutral",
                    "unit_kind": pilot_unit["native_unit_kind"],
                    "title": pilot_unit["localized_title"],
                    "title_locale": "id-ID",
                    "source_binding_ids": [source_binding_id],
                    "target_binding_ids": [target_binding_id],
                    "content_availability": "native_hash_bound",
                    "rights_id": rights_id,
                    "learner_visibility": "visible",
                    "parent_native_unit_id": projected["native"]["row"].get("parent_id"),
                },
            )
        )
        records["course_unit_memberships"].append(
            envelope(
                record_type="course_unit_membership",
                semantic_key=f"a00:prealgebra2e-volume:membership:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state="mathematically_reviewed",
                state_profile=state_profile_id,
                provenance_binding_ids=[owner_manifest_binding_id],
                payload={
                    "course_id": course_id,
                    "edition_id": edition_id,
                    "unit_id": unit_id,
                    "ordinal": owner_module["ordinal"],
                    "order_path": str(owner_module["ordinal"]),
                    "depth": 0,
                    "membership_role": "module_root",
                    "required": True,
                    "visible": True,
                },
            )
        )

        build_recipe_id = record_id("build_recipe", f"build-recipe:html:{module_id}")
        artifact_id = record_id("artifact", f"artifact:html:{module_id}")
        surface_id = record_id("reader_surface", f"reader-surface:html:{module_id}")
        route_id = record_id("route", f"route:html:{module_id}")
        artifact_ids.append(artifact_id)
        surface_ids.append(surface_id)
        route_ids.append(route_id)

        records["build_recipes"].append(
            envelope(
                record_type="build_recipe",
                semantic_key=f"a00:prealgebra2e-volume:build-recipe:html:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="validated",
                owner_native_state="pass",
                state_profile=state_profile_id,
                provenance_binding_ids=[html_binding_id, builder_binding_id],
                payload={
                    "owner_authority_id": owner_authority_id,
                    "edition_id": edition_id,
                    "recipe_kind": "owner_native_html_reference",
                    "toolchain_binding_id": builder_binding_id,
                    "command_template": ["reference-owner-native-html", module_id],
                    "input_ids": [target_binding_id],
                    "output_artifact_ids": [artifact_id],
                    "deterministic": True,
                    "replay_evidence_binding_id": html_binding_id,
                    "network_policy": "offline",
                },
            )
        )
        records["artifacts"].append(
            envelope(
                record_type="artifact",
                semantic_key=f"a00:prealgebra2e-volume:artifact:html:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state="published",
                state_profile=state_profile_id,
                provenance_binding_ids=[html_binding_id],
                payload={
                    "owner_authority_id": owner_authority_id,
                    "edition_id": edition_id,
                    "course_ids": [course_id],
                    "artifact_kind": "semantic_html_module",
                    "locale": "id-ID",
                    "artifact_binding_id": html_binding_id,
                    "rights_id": rights_id,
                    "accessibility_profile": "semantic_html_available_native_accessibility_unknown",
                    "build_recipe_id": build_recipe_id,
                    "publication_state": "public",
                    "public_url": pilot_unit["learner_route"]["url"],
                    "route_ids": [route_id],
                },
            )
        )
        records["reader_surfaces"].append(
            envelope(
                record_type="reader_surface",
                semantic_key=f"a00:prealgebra2e-volume:reader-surface:html:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state="published",
                state_profile=state_profile_id,
                provenance_binding_ids=[html_binding_id],
                payload={
                    "locale": "id-ID",
                    "format": "semantic_html",
                    "action": "learn",
                    "artifact_id": artifact_id,
                    "course_ids": [course_id],
                    "publication_state": "public",
                    "accessibility_profile": "semantic_html_available_native_accessibility_unknown",
                    "primary": True,
                    "evidence_binding_ids": [html_binding_id],
                    "public_url": pilot_unit["learner_route"]["url"],
                    "local_path_binding_id": html_binding_id,
                },
            )
        )
        records["routes"].append(
            envelope(
                record_type="route",
                semantic_key=f"a00:prealgebra2e-volume:route:html:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state="published_owner_native_module_page",
                state_profile=state_profile_id,
                provenance_binding_ids=[html_binding_id],
                payload={
                    "course_id": course_id,
                    "surface_id": surface_id,
                    "route_kind": "exact_owner_native_module",
                    "path": f"/modules/{module_id}/index.html",
                    "access_state": "public",
                    "target_kind": "readable_html",
                    "machine_data_only": False,
                    "evidence_binding_ids": [html_binding_id],
                    "unit_id": unit_id,
                    "public_url": pilot_unit["learner_route"]["url"],
                    "checked_at": RECORDED_AT,
                    "limitation": "Anonymous public-readback state is inherited from the frozen v2.1 A00 pilot; local HTML bytes are verified here.",
                },
            )
        )
        records["search_documents"].append(
            envelope(
                record_type="search_document",
                semantic_key=f"a00:prealgebra2e-volume:search:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="published",
                owner_native_state="mathematically_reviewed",
                state_profile=state_profile_id,
                provenance_binding_ids=[target_binding_id, html_binding_id],
                payload={
                    "course_id": course_id,
                    "unit_id": unit_id,
                    "locale": "id-ID",
                    "title": search_row["title"],
                    "bounded_search_text": search_row["search_text"],
                    "order_key": search_row["order_key"],
                    "learner_route_id": route_id,
                    "source_record_ids": [owner_module["module_unit_id"]],
                    "breadcrumb_titles": [search_row["group_title"]] if search_row.get("group_title") else [],
                },
            )
        )
        records["identity_crosswalks"].append(
            envelope(
                record_type="identity_crosswalk",
                semantic_key=f"a00:prealgebra2e-volume:crosswalk:{module_id}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="validated",
                owner_native_state="identity_declared",
                state_profile=state_profile_id,
                provenance_binding_ids=[native_row_binding_id, identity_map_binding_id],
                payload={
                    "source_schema_name": owner_manifest["schema_name"],
                    "source_schema_version": owner_manifest["schema_version"],
                    "source_record_type": "unit",
                    "source_id": owner_module["module_unit_id"],
                    "target_record_type": "unit",
                    "target_id": unit_id,
                    "mapping_state": "mapped",
                    "mapping_cardinality": "one_to_one",
                    "adapter_run_id": adapter_run_id,
                    "reverse_recipe": f"jsonl_id(content/units.jsonl,{owner_module['module_unit_id']})",
                    "evidence_binding_ids": [native_row_binding_id, identity_map_binding_id],
                },
            )
        )

        for scope_role, target_id in (
            ("learner_visible_unit", unit_id),
            ("learner_artifact", artifact_id),
            ("learner_surface", surface_id),
        ):
            records["rights_assignments"].append(
                envelope(
                    record_type="rights_assignment",
                    semantic_key=f"a00:prealgebra2e-volume:rights-assignment:{scope_role}:{module_id}",
                    dataset_id=dataset_id,
                    owner_authority_id=owner_authority_id,
                    recorded_at=RECORDED_AT,
                    normalized_state="published",
                    owner_native_state="published",
                    state_profile=state_profile_id,
                    provenance_binding_ids=[rights_view_binding_id, pilot_rights_binding_id],
                    payload={
                        "rights_id": rights_id,
                        "target_id": target_id,
                        "scope_role": scope_role,
                        "precedence": 100,
                        "inheritance": "direct",
                        "assignment_state": "effective",
                        "evidence_binding_ids": [rights_view_binding_id, pilot_rights_binding_id],
                    },
                )
            )

    for ordinal, (left, right) in enumerate(zip(projected_units, projected_units[1:]), start=1):
        records["relations"].append(
            envelope(
                record_type="relation",
                semantic_key=f"a00:prealgebra2e-volume:relation:precedes:{left['owner']['module_id']}:{right['owner']['module_id']}",
                dataset_id=dataset_id,
                owner_authority_id=owner_authority_id,
                recorded_at=RECORDED_AT,
                normalized_state="validated",
                owner_native_state="identity_declared",
                state_profile=state_profile_id,
                provenance_binding_ids=[owner_manifest_binding_id],
                payload={
                    "edition_id": edition_id,
                    "relation_type": "precedes",
                    "from_endpoint": {"record_id": left["unit_id"]},
                    "to_endpoint": {"record_id": right["unit_id"]},
                    "assertion_method": "adapter_structural",
                    "evidence_binding_ids": [owner_manifest_binding_id],
                    "endpoint_state": "internal_closed",
                    "ordinal": ordinal,
                    "relation_scope": "course_navigation",
                },
            )
        )

    records["content_bindings"] = content_bindings

    projected_counts = {
        TABLE_RECORD_TYPES[table]: len(records.get(table, []))
        + (1 if table in {"datasets", "adapter_runs", "qa_events"} else 0)
        for table in TABLE_ORDER
    }
    records["adapter_runs"].append(
        envelope(
            record_type="adapter_run",
            semantic_key="a00:prealgebra2e-volume:adapter-run:0.1.0",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state="pass",
            state_profile=state_profile_id,
            provenance_binding_ids=[projection_inventory_binding_id, identity_map_binding_id, reverse_report_binding_id],
            payload={
                "adapter_profile_id": adapter_profile_id,
                "input_manifest_binding_id": owner_manifest_binding_id,
                "output_manifest_binding_id": projection_inventory_binding_id,
                "identity_map_binding_id": identity_map_binding_id,
                "build_a_sha256": core_digest,
                "build_b_sha256": core_digest,
                "deterministic_replay_result": "byte_identical",
                "reverse_extraction_result": "pass",
                "native_input_counts": owner_manifest["records_by_type"],
                "projected_output_counts": projected_counts,
                "loss_report_binding_id": loss_report_binding_id,
                "differential_report_binding_id": reverse_report_binding_id,
            },
        )
    )

    records["qa_events"].append(
        envelope(
            record_type="qa_event",
            semantic_key="a00:prealgebra2e-volume:qa:deterministic-zero-copy:0.1.0",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="validated",
            owner_native_state="pass",
            state_profile=state_profile_id,
            provenance_binding_ids=[reverse_report_binding_id, loss_report_binding_id],
            payload={
                "subject_ids": [dataset_id, adapter_run_id],
                "qa_kind": "v2_2_zero_copy_native_reverse_and_navigation",
                "result": "pass",
                "method": "schema, byte/hash, selector, mapping, reverse-extraction, and deterministic replay",
                "input_binding_ids": [owner_manifest_binding_id, profile_binding_id, identity_map_binding_id],
                "output_binding_id": projection_inventory_binding_id,
                "evidence_binding_ids": [reverse_report_binding_id, loss_report_binding_id, native_index_binding_id],
                "severity_p1": 0,
                "severity_p2": 0,
                "severity_p3": 0,
                "anonymous_readback_state": "inherited",
                "warnings": ["Network readback is inherited; exact local HTML bytes are independently verified."],
            },
        )
    )

    native_shard_id = global_id("shard_ref", "a00:prealgebra2e-volume:native-semantic")
    records["datasets"].append(
        envelope(
            record_type="dataset",
            semantic_key="a00:prealgebra2e-volume:dataset",
            dataset_id=dataset_id,
            owner_authority_id=owner_authority_id,
            recorded_at=RECORDED_AT,
            normalized_state="published",
            owner_native_state="mathematically_reviewed",
            state_profile=state_profile_id,
            provenance_binding_ids=[owner_manifest_binding_id, profile_binding_id],
            payload={
                "corpus_id": "prealgebra2e-volume",
                "course_ids": [course_id],
                "dataset_kind": "curriculum_owner",
                "native_schema_name": owner_manifest["schema_name"],
                "native_schema_version": owner_manifest["schema_version"],
                "manifest_binding_id": owner_manifest_binding_id,
                "adapter_profile_id": adapter_profile_id,
                "workflow_state": "published",
                "publication_state": "public",
                "capabilities": [entry["name"] for entry in profile["capability_policy"]],
                "record_counts": owner_manifest["records_by_type"],
                "content_shard_refs": [native_shard_id],
                "reader_surface_ids": sorted(surface_ids),
                "limitations": profile["limitations"],
            },
        )
    )

    missing_tables = [table for table in TABLE_ORDER if table not in records]
    if missing_tables:
        raise ValueError(f"missing required table materialization: {missing_tables}")

    record_schema = load_json(SCHEMA_ROOT / "record-v2.2.schema.json")
    all_ids: set[str] = set()
    all_semantic_keys: set[tuple[str, str]] = set()
    for table in TABLE_ORDER:
        for row in records[table]:
            validate_json(row, record_schema, f"{table}:{row['semantic_key']}")
            expected_id = global_id(row["record_type"], row["semantic_key"])
            if row["id"] != expected_id:
                raise ValueError(f"UUIDv5 mismatch for {row['semantic_key']}")
            if row["id"] in all_ids:
                raise ValueError(f"duplicate projected ID: {row['id']}")
            if (row["record_type"], row["semantic_key"]) in all_semantic_keys:
                raise ValueError(f"duplicate projected semantic key: {row['semantic_key']}")
            all_ids.add(row["id"])
            all_semantic_keys.add((row["record_type"], row["semantic_key"]))

    for table in TABLE_ORDER:
        write_jsonl(output / "tables" / f"{table}.jsonl", records[table])

    table_inventory: list[dict[str, Any]] = []
    record_counts: dict[str, int] = {}
    for table in TABLE_ORDER:
        path = output / "tables" / f"{table}.jsonl"
        record_type = TABLE_RECORD_TYPES[table]
        count = len(records[table])
        record_counts[record_type] = count
        table_inventory.append(
            {
                "table": table,
                "record_type": record_type,
                "path": f"tables/{table}.jsonl",
                "records": count,
                "bytes": path.stat().st_size,
                "sha256": sha256_path(path),
            }
        )

    materialized_paths = sorted(
        path for path in output.rglob("*") if path.is_file()
    )
    materialized_facts = [
        file_fact(output, path, role="replay_material", media_type=media_type_for(path.name))
        for path in materialized_paths
    ]
    materialized_digest = combined_digest(materialized_facts)

    return {
        "profile": profile,
        "owner_manifest": owner_manifest,
        "owner_backend_root": owner_backend_root,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_authority_id,
        "edition_id": edition_id,
        "rights_id": rights_id,
        "adapter_profile_id": adapter_profile_id,
        "adapter_run_id": adapter_run_id,
        "qa_event_id": qa_event_id,
        "package_id": package_id,
        "course_id": course_id,
        "state_profile_id": state_profile_id,
        "owner_manifest_binding_id": owner_manifest_binding_id,
        "profile_binding_id": profile_binding_id,
        "builder_binding_id": builder_binding_id,
        "projection_inventory_binding_id": projection_inventory_binding_id,
        "identity_map_binding_id": identity_map_binding_id,
        "native_index_binding_id": native_index_binding_id,
        "record_schema_binding_id": record_schema_binding_id,
        "native_shard_id": native_shard_id,
        "core_digest": core_digest,
        "materialized_digest": materialized_digest,
        "materialized_facts": materialized_facts,
        "table_inventory": table_inventory,
        "record_counts": record_counts,
        "record_count": sum(record_counts.values()),
        "surface_ids": surface_ids,
        "route_ids": route_ids,
        "unit_ids": unit_ids,
    }


def compare_runs(first: Path, second: Path) -> tuple[str, list[dict[str, Any]]]:
    first_files = sorted(path.relative_to(first).as_posix() for path in first.rglob("*") if path.is_file())
    second_files = sorted(path.relative_to(second).as_posix() for path in second.rglob("*") if path.is_file())
    if first_files != second_files:
        raise ValueError("two-run replay file inventories differ")
    facts: list[dict[str, Any]] = []
    for relative in first_files:
        left = first / relative
        right = second / relative
        left_bytes = left.read_bytes()
        right_bytes = right.read_bytes()
        if left_bytes != right_bytes:
            raise ValueError(f"two-run replay bytes differ: {relative}")
        facts.append(file_fact(first, left, role="replay_material", media_type=media_type_for(relative)))
    return combined_digest(facts), facts


def external_bound_file(expectation: dict[str, Any]) -> dict[str, Any]:
    return {
        "locator_base": expectation["locator_base"],
        "path": expectation["path"],
        "role": expectation["role"],
        "media_type": media_type_for(expectation["path"]),
        "bytes": expectation["bytes"],
        "sha256": expectation["sha256"],
    }


def create_manifest(output: Path, state: dict[str, Any], replay_digest: str) -> dict[str, Any]:
    profile = state["profile"]
    owner_manifest = state["owner_manifest"]
    local_files = []
    for path in sorted(path for path in output.rglob("*") if path.is_file()):
        relative = path.relative_to(output).as_posix()
        if relative in {"manifest.json", "validation-report.json", "seal.json"}:
            continue
        role = "record_table" if relative.startswith("tables/") else "package_support"
        if relative.startswith("schema/"):
            role = "schema"
        elif relative.startswith("tools/"):
            role = "executable"
        elif relative == "identity-map.jsonl":
            role = "identity_map"
        elif relative == "native-shard-index.json":
            role = "native_shard_index"
        local_files.append(file_fact(output, path, role=role, media_type=media_type_for(relative)))

    native_index_fact = next(fact for fact in local_files if fact["path"] == "native-shard-index.json")
    identity_map_fact = next(fact for fact in local_files if fact["path"] == "identity-map.jsonl")
    profile_fact = next(fact for fact in local_files if fact["path"] == "profiles/a00-lane-profile.json")
    builder_fact = next(fact for fact in local_files if fact["path"] == "tools/build_a00_pilot.py")
    record_schema_fact = next(fact for fact in local_files if fact["path"] == "schema/record-v2.2.schema.json")
    state_fact = next(fact for fact in local_files if fact["path"] == "state-vocabulary-v2.2.json")

    table_by_name = {item["table"]: item for item in state["table_inventory"]}
    learner_tables = ["units", "course_unit_memberships", "relations", "reader_surfaces", "routes", "search_documents"]
    shards = [
        {
            "shard_id": state["native_shard_id"],
            "shard_kind": "native_semantic",
            "record_types": sorted(owner_manifest["records_by_type"]),
            "course_ids": [state["course_id"]],
            "locale": None,
            "file": native_index_fact,
            "record_count": owner_manifest["records_total"],
        },
        {
            "shard_id": global_id("shard_ref", "a00:prealgebra2e-volume:identity-map"),
            "shard_kind": "identity_map",
            "record_types": ["identity_crosswalk", "native_binding"],
            "course_ids": [state["course_id"]],
            "locale": None,
            "file": identity_map_fact,
            "record_count": 92,
        },
    ]
    for table in learner_tables:
        inventory = table_by_name[table]
        shards.append(
            {
                "shard_id": global_id("shard_ref", f"a00:prealgebra2e-volume:navigation:{table}"),
                "shard_kind": "learner_navigation",
                "record_types": [inventory["record_type"]],
                "course_ids": [state["course_id"]],
                "locale": "id-ID",
                "file": {
                    "path": inventory["path"],
                    "role": "learner_navigation",
                    "media_type": "application/x-ndjson",
                    "bytes": inventory["bytes"],
                    "sha256": inventory["sha256"],
                },
                "record_count": inventory["records"],
            }
        )

    native_manifest_expectation = profile["native_authority"]["manifest"]
    migration_expectation = profile["native_authority"]["migration_receipt"]
    input_authorities = [
        external_bound_file(native_manifest_expectation),
        external_bound_file(migration_expectation),
        *(external_bound_file(item) for item in profile["central_registry_inputs"]),
    ]
    for view in load_json(output / "native-shard-index.json")["views"]:
        input_authorities.append(
            {
                "locator_base": "owner_backend_root",
                "path": view["path"],
                "role": "owner_native_jsonl_view",
                "media_type": "application/x-ndjson",
                "bytes": view["bytes"],
                "sha256": view["sha256"],
            }
        )

    base = next(item for item in input_authorities if item["role"] == "base_federation_manifest")
    capabilities = []
    for item in profile["capability_policy"]:
        capability = {
            "name": item["name"],
            "state": item["state"],
            "record_count": item["native_record_count"],
            "record_types": [],
        }
        if item["state"] in {"not_projected", "absent"}:
            capability["loss_reason"] = item["reason"]
        if item["name"] == "semantic_native":
            capability["record_types"] = sorted(owner_manifest["records_by_type"])
        elif item["name"] == "learner_navigation":
            capability["record_types"] = [TABLE_RECORD_TYPES[name] for name in learner_tables]
        elif item["name"] == "assets":
            capability["record_types"] = ["asset", "rights"]
        capabilities.append(capability)

    output_binding_ids = [
        state["projection_inventory_binding_id"],
        state["identity_map_binding_id"],
        state["native_index_binding_id"],
        binding_id("capability-loss-report"),
        binding_id("reverse-extraction-report"),
    ]
    manifest = {
        "$schema": "schema/manifest-v2.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-manifest/2.2.0",
        "schema_version": "2.2.0",
        "profile": "lane",
        "package_id": state["package_id"],
        "dataset_id": state["dataset_id"],
        "dataset_version": "0.1.0",
        "recorded_at": RECORDED_AT,
        "identity_namespace": str(IDENTITY_NAMESPACE),
        "identity_formula": IDENTITY_FORMULA,
        "base_federation": base,
        "record_schema": record_schema_fact,
        "state_vocabulary": state_fact,
        "capabilities": capabilities,
        "record_order": TABLE_ORDER,
        "record_count": state["record_count"],
        "record_counts": state["record_counts"],
        "table_inventory": state["table_inventory"],
        "shards": shards,
        "files": local_files,
        "input_authorities": sorted(input_authorities, key=lambda item: (item["locator_base"], item["path"], item["role"])),
        "adapter_profile": {
            "record_id": state["adapter_profile_id"],
            "profile_file": profile_fact,
            "executable": builder_fact,
        },
        "adapter_run": {
            "record_id": state["adapter_run_id"],
            "identity_map": identity_map_fact,
            "native_shard_index": native_index_fact,
        },
        "build": {
            "builder": builder_fact,
            "commands": [
                ["python", "-B", "tools/build_a00_pilot.py", "--output", "BUILD_A"],
                ["python", "-B", "tools/build_a00_pilot.py", "--output", "BUILD_B"],
                ["python", "-B", "tools/validate_v22_package.py", "PACKAGE_ROOT"],
            ],
            "input_binding_ids": sorted({state["owner_manifest_binding_id"], state["profile_binding_id"], state["builder_binding_id"]}),
            "output_binding_ids": sorted(output_binding_ids),
            "canonical_serialization": {
                "encoding": "UTF-8",
                "newline": "LF",
                "json_keys": "lexicographically_sorted",
                "jsonl_order": "record_type_then_semantic_key",
                "trailing_newline": True,
            },
            "deterministic_replay": "byte_identical",
            "build_a_sha256": replay_digest,
            "build_b_sha256": replay_digest,
        },
        "validation": {
            "schema": "pass",
            "canonical_serialization": "pass",
            "uuid5_identity": "pass",
            "semantic_key_uniqueness": "pass",
            "typed_foreign_keys": "pass",
            "state_normalization": "pass",
            "native_binding_closure": "pass",
            "relation_endpoint_policy": "pass",
            "source_target_binding": "pass",
            "zero_prose": "pass",
            "rights_closure": "pass",
            "accessibility_truthfulness": "pass",
            "capability_closure": "pass",
            "learner_route_policy": "pass",
            "adapter_reverse_extraction": "pass",
            "deterministic_replay": "pass",
            "aggregate_differential": "not_applicable",
            "anonymous_public_readback": "inherited",
        },
        "zero_copy_policy": {
            "owner_native_authoritative": True,
            "full_prose_centralized": False,
            "reversible_adapters": True,
            "learner_metadata_only": True,
            "allowed_central_fields": [
                "identity", "order", "titles", "hashes", "routes", "relations", "rights", "qa", "search_terms", "provenance", "publication"
            ],
        },
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1",
            "seal_file": "seal.json",
            "seal_excluded_from_own_digest": True,
            "binds": [
                "schemas", "state_vocabulary", "adapter", "builder", "input_authorities", "records", "shards", "identity_map", "manifest", "validation_report"
            ],
        },
        "limitations": profile["limitations"],
    }
    validate_json(manifest, load_json(SCHEMA_ROOT / "manifest-v2.2.schema.json"), "manifest")
    return manifest


def create_seal(output: Path, package_id: str) -> dict[str, Any]:
    facts = []
    for path in sorted(path for path in output.rglob("*") if path.is_file() and path.name != "seal.json"):
        facts.append(file_fact(output, path, role="sealed_file", media_type=media_type_for(path.name)))
    return {
        "schema_id": "interlanguage/global-modular-mathematics-package-seal/2.2.0",
        "schema_version": "2.2.0",
        "package_id": package_id,
        "recorded_at": RECORDED_AT,
        "algorithm": "sha256-sorted-path-bytes-v1",
        "seal_excluded_from_own_digest": True,
        "files": facts,
        "file_count": len(facts),
        "total_bytes": sum(fact["bytes"] for fact in facts),
        "sealed_digest_sha256": combined_digest(facts),
    }


def build(output: Path, replace: bool) -> dict[str, Any]:
    expected_parent = (V22_ROOT / "packages").resolve()
    resolved_output = output.resolve()
    if resolved_output.parent != expected_parent:
        raise ValueError(f"output must be an immediate child of {expected_parent}")
    if output.exists():
        if not replace:
            raise FileExistsError(f"output already exists: {output}; pass --replace")
        shutil.rmtree(output)

    with tempfile.TemporaryDirectory(prefix="v22-a00-build-a-") as first_temp, tempfile.TemporaryDirectory(prefix="v22-a00-build-b-") as second_temp:
        first = Path(first_temp) / PACKAGE_NAME
        second = Path(second_temp) / PACKAGE_NAME
        first_state = materialize_run(first)
        second_state = materialize_run(second)
        replay_digest, _ = compare_runs(first, second)
        if replay_digest != first_state["materialized_digest"] or replay_digest != second_state["materialized_digest"]:
            raise ValueError("two-run replay digest disagrees with independent materialization digests")
        shutil.copytree(first, output)

    manifest = create_manifest(output, first_state, replay_digest)
    write_json(output / "manifest.json", manifest)

    validator = Path(__file__).resolve().parent / "validate_v22_package.py"
    report_path = output / "validation-report.json"
    subprocess.run(
        [sys.executable, "-B", str(validator), str(output), "--skip-seal", "--report", str(report_path)],
        check=True,
    )
    seal = create_seal(output, first_state["package_id"])
    write_json(output / "seal.json", seal)
    subprocess.run([sys.executable, "-B", str(validator), str(output)], check=True)

    return {
        "result": "pass",
        "package": str(output),
        "package_id": first_state["package_id"],
        "native_records_referenced": first_state["owner_manifest"]["records_total"],
        "projected_records": first_state["record_count"],
        "tables": len(first_state["table_inventory"]),
        "two_run_replay_sha256": replay_digest,
        "manifest": {
            "bytes": (output / "manifest.json").stat().st_size,
            "sha256": sha256_path(output / "manifest.json"),
        },
        "validation_report": {
            "bytes": report_path.stat().st_size,
            "sha256": sha256_path(report_path),
        },
        "seal": {
            "bytes": (output / "seal.json").stat().st_size,
            "sha256": sha256_path(output / "seal.json"),
            "sealed_digest_sha256": seal["sealed_digest_sha256"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build(args.output, args.replace)
    except Exception as exc:
        print(json.dumps({"result": "fail", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
