#!/usr/bin/env python3
"""Independent profile-driven validator for modular mathematics v2.2 lane packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from v22_common import (
    IDENTITY_FORMULA,
    IDENTITY_NAMESPACE,
    SHA256_RE,
    canonical_json_bytes,
    combined_digest,
    file_fact,
    global_id,
    iter_jsonl,
    load_json,
    media_type_for,
    resolve_locator,
    sha256_bytes,
    sha256_path,
    strip_sha256_prefix,
    write_json,
)


REQUIRED_TABLES = [
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

MACHINE_ROUTE_RE = re.compile(r"(?:localhost|127\.0\.0\.1|\.(?:jsonl?|csv)(?:[?#]|$)|/api(?:/|$))")


def schema_errors(instance: Any, schema: dict[str, Any], label: str) -> list[str]:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{label}{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
        for error in errors
    ]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def package_roots(package_root: Path) -> tuple[Path, Path, Path]:
    package_root = package_root.resolve()
    try:
        v22_root = package_root.parents[1]
        program_root = package_root.parents[3]
    except IndexError as exc:
        raise ValueError(f"package path is too shallow: {package_root}") from exc
    if v22_root.name != "v2.2" or v22_root.parent.name != "backend":
        raise ValueError(f"package is not under backend/v2.2/packages: {package_root}")
    owner_root = program_root.parent / "openstax-prealgebra"
    return v22_root, program_root, owner_root


def load_tables(
    package_root: Path,
    manifest: dict[str, Any],
    record_schema: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    records_by_id: dict[str, dict[str, Any]] = {}
    semantic_keys: set[tuple[str, str]] = set()
    inventory_by_table = {entry["table"]: entry for entry in manifest["table_inventory"]}
    require(manifest["record_order"] == REQUIRED_TABLES, "manifest record_order differs from required lane table order", errors)
    require(set(inventory_by_table) == set(REQUIRED_TABLES), "table inventory does not close over required tables", errors)

    for table in REQUIRED_TABLES:
        inventory = inventory_by_table.get(table)
        if inventory is None:
            continue
        path = package_root / inventory["path"]
        if not path.is_file():
            errors.append(f"missing table file: {inventory['path']}")
            continue
        require(path.stat().st_size == inventory["bytes"], f"table byte mismatch: {table}", errors)
        require(sha256_path(path) == inventory["sha256"], f"table hash mismatch: {table}", errors)
        rows: list[dict[str, Any]] = []
        previous: tuple[str, str] | None = None
        try:
            for line_number, (row, raw) in enumerate(iter_jsonl(path), start=1):
                if canonical_json_bytes(row) != raw:
                    errors.append(f"noncanonical JSONL row: {inventory['path']}:{line_number}")
                row_errors = schema_errors(row, record_schema, f"{inventory['path']}:{line_number}")
                errors.extend(row_errors[:10])
                key = (row.get("record_type", ""), row.get("semantic_key", ""))
                if previous is not None and key <= previous:
                    errors.append(f"JSONL record order is not strictly increasing: {inventory['path']}:{line_number}")
                previous = key
                if row.get("record_type") != inventory["record_type"]:
                    errors.append(f"record type mismatch in {inventory['path']}:{line_number}")
                if isinstance(row.get("record_type"), str) and isinstance(row.get("semantic_key"), str):
                    expected_id = global_id(row["record_type"], row["semantic_key"])
                    if row.get("id") != expected_id:
                        errors.append(f"UUIDv5 mismatch: {row.get('semantic_key')}")
                if row.get("id") in records_by_id:
                    errors.append(f"duplicate projected record ID: {row.get('id')}")
                else:
                    records_by_id[row.get("id")] = row
                if key in semantic_keys:
                    errors.append(f"duplicate projected semantic key: {key}")
                semantic_keys.add(key)
                rows.append(row)
        except Exception as exc:
            errors.append(str(exc))
        require(len(rows) == inventory["records"], f"table record count mismatch: {table}", errors)
        tables[table] = rows

    actual_counts = {inventory_by_table[table]["record_type"]: len(tables.get(table, [])) for table in REQUIRED_TABLES if table in inventory_by_table}
    require(actual_counts == manifest["record_counts"], "manifest record_counts differ from table rows", errors)
    require(sum(actual_counts.values()) == manifest["record_count"], "manifest record_count differs from table sum", errors)
    return tables, records_by_id


def verify_manifest_files(package_root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    declared = {entry["path"]: entry for entry in manifest["files"]}
    actual_paths = sorted(
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_file() and path.relative_to(package_root).as_posix() not in {"manifest.json", "validation-report.json", "seal.json"}
    )
    require(sorted(declared) == actual_paths, "manifest local file inventory is incomplete or has extras", errors)
    for relative, fact in declared.items():
        path = package_root / relative
        if not path.is_file():
            continue
        require(path.stat().st_size == fact["bytes"], f"manifest file bytes mismatch: {relative}", errors)
        require(sha256_path(path) == fact["sha256"], f"manifest file hash mismatch: {relative}", errors)
    replay_digest = combined_digest(manifest["files"])
    require(manifest["build"]["build_a_sha256"] == replay_digest, "build A digest does not match materialized package files", errors)
    require(manifest["build"]["build_b_sha256"] == replay_digest, "build B digest does not match materialized package files", errors)


def verify_external_inputs(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    *,
    package_root: Path,
    program_root: Path,
    owner_root: Path,
    owner_backend_root: Path,
    errors: list[str],
) -> None:
    for item in manifest["input_authorities"]:
        try:
            path = resolve_locator(
                item["locator_base"],
                item["path"],
                package_root=package_root,
                program_root=program_root,
                owner_root=owner_root,
                owner_backend_root=owner_backend_root,
            )
        except Exception as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"missing external input: {item['locator_base']}:{item['path']}")
            continue
        require(path.stat().st_size == item["bytes"], f"external input bytes mismatch: {item['path']}", errors)
        require(sha256_path(path) == item["sha256"], f"external input hash mismatch: {item['path']}", errors)

    expected_profile_inputs = [
        profile["native_authority"]["manifest"],
        profile["native_authority"]["migration_receipt"],
        *profile["central_registry_inputs"],
    ]
    actual_keys = {(item["locator_base"], item["path"], item["sha256"]) for item in manifest["input_authorities"]}
    for item in expected_profile_inputs:
        require(
            (item["locator_base"], item["path"], item["sha256"]) in actual_keys,
            f"profile authority absent from manifest input_authorities: {item['path']}",
            errors,
        )


def scan_native_for_validation(
    package_root: Path,
    owner_backend_root: Path,
    owner_manifest: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, tuple[int, str]], dict[tuple[str, str], tuple[int, str, dict[str, Any]]]]:
    native_index = load_json(package_root / "native-shard-index.json")
    require(native_index["record_count"] == owner_manifest["records_total"], "native shard total differs from owner manifest", errors)
    require(native_index["record_counts"] == owner_manifest["records_by_type"], "native shard per-type counts differ from owner manifest", errors)
    require(native_index["view_count"] == 17, "native shard index does not contain 17 JSONL views", errors)
    view_by_path = {view["path"]: view for view in native_index["views"]}
    owner_views = {
        entry["path"]: entry
        for entry in owner_manifest["files"]
        if entry.get("format") == "jsonl"
    }
    require(set(view_by_path) == set(owner_views), "native shard view set differs from owner manifest", errors)

    file_cache: dict[str, tuple[int, str]] = {}
    selector_cache: dict[tuple[str, str], tuple[int, str, dict[str, Any]]] = {}
    seen_ids: set[bytes] = set()
    total = 0
    for relative in sorted(view_by_path):
        view = view_by_path[relative]
        path = owner_backend_root / relative
        if not path.is_file():
            errors.append(f"missing native JSONL view: {relative}")
            continue
        size = path.stat().st_size
        digest = sha256_path(path)
        file_cache[relative] = (size, digest)
        require(size == view["bytes"], f"native view bytes mismatch: {relative}", errors)
        require(digest == view["sha256"], f"native view hash mismatch: {relative}", errors)
        declared = owner_views[relative]
        require(size == declared["bytes"], f"native view bytes differ from owner manifest: {relative}", errors)
        require(digest == strip_sha256_prefix(declared["sha256"]), f"native view hash differs from owner manifest: {relative}", errors)
        id_digest = bytearray()
        first_id = None
        last_id = None
        count = 0
        try:
            for row, raw in iter_jsonl(path):
                if canonical_json_bytes(row) != raw:
                    errors.append(f"noncanonical owner-native row: {relative}:{count + 1}")
                native_id = row.get("id")
                if not isinstance(native_id, str):
                    errors.append(f"missing owner-native ID: {relative}:{count + 1}")
                    continue
                try:
                    native_uuid = uuid.UUID(native_id.removeprefix("urn:uuid:")).bytes
                except Exception:
                    errors.append(f"invalid owner-native UUID: {relative}:{count + 1}")
                    continue
                if native_uuid in seen_ids:
                    errors.append(f"duplicate owner-native ID: {native_id}")
                seen_ids.add(native_uuid)
                id_digest.extend((native_id + "\n").encode("ascii"))
                first_id = first_id or native_id
                last_id = native_id
                count += 1
                if relative == "content/units.jsonl":
                    selector_cache[(relative, native_id)] = (len(raw), sha256_bytes(raw), row)
        except Exception as exc:
            errors.append(str(exc))
        total += count
        require(count == view["records"], f"native view record count mismatch: {relative}", errors)
        require(sha256_bytes(bytes(id_digest)) == view["record_id_sequence_sha256"], f"native ID sequence digest mismatch: {relative}", errors)
        require(first_id == view["first_record_id"], f"native first ID mismatch: {relative}", errors)
        require(last_id == view["last_record_id"], f"native last ID mismatch: {relative}", errors)
    require(total == native_index["record_count"], "native reverse record total mismatch", errors)
    require(sha256_bytes(b"".join(sorted(seen_ids))) == native_index["native_record_id_set_sha256"], "native record ID set digest mismatch", errors)
    return file_cache, selector_cache


def verify_content_bindings(
    tables: dict[str, list[dict[str, Any]]],
    *,
    package_root: Path,
    program_root: Path,
    owner_root: Path,
    owner_backend_root: Path,
    native_file_cache: dict[str, tuple[int, str]],
    selector_cache: dict[tuple[str, str], tuple[int, str, dict[str, Any]]],
    errors: list[str],
) -> None:
    for record in tables["content_bindings"]:
        payload = record["payload"]
        state = payload["evidence_state"]
        if state in {"unavailable", "not_applicable"}:
            require(payload["bytes"] is None and payload["sha256"] is None, f"null evidence contract failed: {record['semantic_key']}", errors)
            continue
        if state == "declared":
            require(isinstance(payload["bytes"], int), f"declared binding lacks bytes: {record['semantic_key']}", errors)
            require(isinstance(payload["sha256"], str) and SHA256_RE.fullmatch(payload["sha256"]), f"declared binding lacks SHA-256: {record['semantic_key']}", errors)
            require(bool(payload.get("limitation")), f"declared binding lacks limitation: {record['semantic_key']}", errors)
            continue
        if state == "verified_public":
            require(payload.get("public_uri", "").startswith("https://"), f"verified public binding lacks HTTPS URI: {record['semantic_key']}", errors)
            continue
        if state != "verified_local":
            errors.append(f"unknown evidence state: {record['semantic_key']}")
            continue

        locator_base = payload["locator_base"]
        locator = payload["locator"]
        selector_kind = payload["selector_kind"]
        if locator_base == "owner_backend_root" and selector_kind == "none" and locator in native_file_cache:
            actual_bytes, actual_sha = native_file_cache[locator]
        elif locator_base == "owner_backend_root" and selector_kind == "native_id":
            native_id = payload.get("selector", {}).get("native_id")
            fact = selector_cache.get((locator, native_id))
            if fact is None:
                errors.append(f"native selector does not resolve exactly once: {record['semantic_key']}")
                continue
            actual_bytes, actual_sha, _ = fact
        else:
            try:
                path = resolve_locator(
                    locator_base,
                    locator,
                    package_root=package_root,
                    program_root=program_root,
                    owner_root=owner_root,
                    owner_backend_root=owner_backend_root,
                )
            except Exception as exc:
                errors.append(f"{record['semantic_key']}: {exc}")
                continue
            if not path.is_file():
                errors.append(f"verified local binding is missing: {record['semantic_key']}")
                continue
            actual_bytes, actual_sha = path.stat().st_size, sha256_path(path)
        require(actual_bytes == payload["bytes"], f"content binding bytes mismatch: {record['semantic_key']}", errors)
        require(actual_sha == payload["sha256"], f"content binding hash mismatch: {record['semantic_key']}", errors)


def collect_ids(value: Any) -> Iterable[str]:
    if isinstance(value, str) and value.startswith("urn:uuid:"):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from collect_ids(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from collect_ids(item)


def verify_foreign_keys(
    tables: dict[str, list[dict[str, Any]]],
    records_by_id: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    profile: dict[str, Any],
    errors: list[str],
) -> None:
    content_ids = {row["id"] for row in tables["content_bindings"]}
    external_ids = set(profile["external_record_ids"])
    shard_ids = {row["shard_id"] for row in manifest["shards"]}
    package_id = manifest["package_id"]
    allowed_nonrecords = external_ids | shard_ids | {package_id}
    all_ids = set(records_by_id)

    for row in records_by_id.values():
        require(row["dataset_id"] in all_ids, f"dataset_id is not internal: {row['semantic_key']}", errors)
        require(row["owner_authority_id"] in all_ids, f"owner_authority_id is not internal: {row['semantic_key']}", errors)
        for binding in row["provenance_binding_ids"]:
            require(binding in content_ids, f"provenance binding is not a content binding: {row['semantic_key']} -> {binding}", errors)

    checks: dict[str, list[tuple[str, str]]] = {
        "owner_authorities": [("native_manifest_binding_id", "content")],
        "datasets": [("manifest_binding_id", "content"), ("adapter_profile_id", "record")],
        "editions": [("owner_authority_id", "record"), ("rights_id", "record")],
        "units": [("edition_id", "record"), ("native_binding_id", "record"), ("rights_id", "record")],
        "course_unit_memberships": [("course_id", "external"), ("edition_id", "record"), ("unit_id", "record")],
        "native_bindings": [("subject_id", "record"), ("record_binding_id", "content")],
        "content_bindings": [("subject_id", "record")],
        "rights_assignments": [("rights_id", "record"), ("target_id", "record")],
        "artifacts": [("owner_authority_id", "record"), ("edition_id", "record"), ("artifact_binding_id", "content"), ("rights_id", "record"), ("build_recipe_id", "record")],
        "build_recipes": [("owner_authority_id", "record"), ("edition_id", "record"), ("toolchain_binding_id", "content"), ("replay_evidence_binding_id", "content")],
        "reader_surfaces": [("artifact_id", "record")],
        "routes": [("course_id", "external"), ("surface_id", "record"), ("unit_id", "record")],
        "search_documents": [("course_id", "external"), ("unit_id", "record"), ("learner_route_id", "record")],
        "adapter_profiles": [("executable_binding_id", "content")],
        "adapter_runs": [("adapter_profile_id", "record"), ("input_manifest_binding_id", "content"), ("output_manifest_binding_id", "content"), ("identity_map_binding_id", "content")],
        "qa_events": [("output_binding_id", "content")],
        "identity_crosswalks": [("target_id", "record"), ("adapter_run_id", "record")],
    }
    for table, field_checks in checks.items():
        for row in tables[table]:
            payload = row["payload"]
            for field, kind in field_checks:
                value = payload.get(field)
                if value is None:
                    continue
                if kind == "record":
                    require(value in all_ids, f"dangling record FK: {row['semantic_key']}:{field}", errors)
                elif kind == "content":
                    require(value in content_ids, f"dangling content FK: {row['semantic_key']}:{field}", errors)
                elif kind == "external":
                    require(value in external_ids, f"undeclared external FK: {row['semantic_key']}:{field}", errors)

    list_fields = {
        "editions": ["source_binding_ids", "target_binding_ids"],
        "units": ["source_binding_ids", "target_binding_ids", "correction_ids", "artifact_ids"],
        "relations": ["evidence_binding_ids"],
        "rights_assignments": ["evidence_binding_ids"],
        "artifacts": ["course_ids", "route_ids"],
        "build_recipes": ["input_ids", "output_artifact_ids"],
        "reader_surfaces": ["course_ids", "evidence_binding_ids"],
        "routes": ["evidence_binding_ids"],
        "adapter_runs": [],
        "qa_events": ["subject_ids", "input_binding_ids", "evidence_binding_ids"],
        "identity_crosswalks": ["evidence_binding_ids"],
    }
    for table, fields in list_fields.items():
        for row in tables[table]:
            for field in fields:
                for value in row["payload"].get(field, []):
                    if field == "course_ids":
                        require(value in external_ids, f"undeclared course ID: {row['semantic_key']}:{field}", errors)
                    elif field in {"source_binding_ids", "target_binding_ids", "evidence_binding_ids", "input_binding_ids"}:
                        require(value in content_ids, f"dangling binding list FK: {row['semantic_key']}:{field}", errors)
                    else:
                        require(value in all_ids, f"dangling record list FK: {row['semantic_key']}:{field}", errors)

    for relation in tables["relations"]:
        for endpoint_name in ("from_endpoint", "to_endpoint"):
            endpoint = relation["payload"][endpoint_name]
            if "record_id" in endpoint:
                require(endpoint["record_id"] in all_ids, f"dangling relation endpoint: {relation['semantic_key']}", errors)
            else:
                require(endpoint["external_native_binding_id"] in external_ids, f"undeclared external relation endpoint: {relation['semantic_key']}", errors)


def verify_state_mapping(
    records_by_id: dict[str, dict[str, Any]],
    state_vocabulary: dict[str, Any],
    profile: dict[str, Any],
    errors: list[str],
) -> None:
    normalized = set(state_vocabulary["normalized_states"])
    state_profile = next((row for row in state_vocabulary["profiles"] if row["id"] == profile["state_profile_id"]), None)
    require(state_profile is not None, "lane state profile is absent from state vocabulary", errors)
    if state_profile is None:
        return
    mapping = state_profile["mappings"]
    for row in records_by_id.values():
        require(row["normalized_state"] in normalized, f"unknown normalized state: {row['semantic_key']}", errors)
        require(row["state_profile"] == state_profile["id"], f"wrong state profile: {row['semantic_key']}", errors)
        native_state = row["owner_native_state"]
        if native_state is None:
            continue
        require(native_state in mapping, f"unmapped owner-native state: {row['semantic_key']} -> {native_state}", errors)
        if native_state in mapping:
            require(mapping[native_state] == row["normalized_state"], f"incorrect normalized state: {row['semantic_key']}", errors)


def verify_a00_semantics(
    tables: dict[str, list[dict[str, Any]]],
    profile: dict[str, Any],
    program_root: Path,
    errors: list[str],
) -> None:
    expected = profile["expected_navigation"]
    require(len(tables["units"]) == expected["visible_units"], "visible unit count mismatch", errors)
    require(len(tables["course_unit_memberships"]) == expected["memberships"], "membership count mismatch", errors)
    require(len(tables["relations"]) == expected["relations"], "navigation relation count mismatch", errors)
    require(len(tables["search_documents"]) == expected["search_documents"], "search count mismatch", errors)
    require(len(tables["routes"]) == expected["routes"], "route count mismatch", errors)

    units_by_id = {row["id"]: row for row in tables["units"]}
    memberships = sorted(tables["course_unit_memberships"], key=lambda row: row["payload"]["ordinal"])
    require([row["payload"]["ordinal"] for row in memberships] == list(range(1, 76)), "membership ordinals are not exactly 1..75", errors)
    membership_units = [row["payload"]["unit_id"] for row in memberships]
    require(len(set(membership_units)) == 75 and set(membership_units) == set(units_by_id), "membership/unit bijection failed", errors)

    relations = sorted(tables["relations"], key=lambda row: row["payload"]["ordinal"])
    expected_edges = list(zip(membership_units, membership_units[1:]))
    actual_edges = [
        (row["payload"]["from_endpoint"].get("record_id"), row["payload"]["to_endpoint"].get("record_id"))
        for row in relations
    ]
    require(actual_edges == expected_edges, "precedes relation chain differs from membership order", errors)

    pilot_root = program_root / "backend" / "v2.1" / "pilots" / "a00-prealgebra"
    pilot_units = [row for row, _ in iter_jsonl(pilot_root / "units.jsonl")]
    pilot_by_native = {row["native_unit_id"]: row for row in pilot_units}
    pilot_search = {row["stable_unit_id"]: row for row, _ in iter_jsonl(pilot_root / "search.jsonl")}
    native_bindings = {row["payload"]["subject_id"]: row for row in tables["native_bindings"]}
    crosswalks = {row["payload"]["target_id"]: row for row in tables["identity_crosswalks"]}
    routes = {row["payload"]["unit_id"]: row for row in tables["routes"]}
    search_documents = {row["payload"]["unit_id"]: row for row in tables["search_documents"]}
    require(set(native_bindings) == set(units_by_id), "native binding/unit bijection failed", errors)
    require(set(crosswalks) == set(units_by_id), "crosswalk/unit bijection failed", errors)
    require(set(routes) == set(units_by_id), "route/unit bijection failed", errors)
    require(set(search_documents) == set(units_by_id), "search/unit bijection failed", errors)

    title_pattern = re.compile(profile["zero_prose_policy"]["allowed_unit_title_pattern"])
    search_pattern = re.compile(profile["zero_prose_policy"]["allowed_search_text_pattern"])
    for unit_id, unit in units_by_id.items():
        binding = native_bindings[unit_id]
        require(binding["payload"]["mapping_cardinality"] == "one_to_one", f"unit mapping is not one-to-one: {unit['semantic_key']}", errors)
        native_id = binding["payload"]["native_id"]
        pilot = pilot_by_native.get(native_id)
        require(pilot is not None, f"projected unit lacks frozen pilot row: {unit['semantic_key']}", errors)
        if pilot is None:
            continue
        require(unit["payload"]["title"] == pilot["localized_title"], f"unit title differs from admitted metadata: {unit['semantic_key']}", errors)
        require(bool(title_pattern.fullmatch(unit["payload"]["title"])), f"unit title violates zero-prose profile: {unit['semantic_key']}", errors)
        route = routes[unit_id]
        require(route["payload"]["public_url"] == pilot["learner_route"]["url"], f"route URL differs from pilot: {unit['semantic_key']}", errors)
        require(route["payload"]["machine_data_only"] is False, f"learner route is machine-only: {unit['semantic_key']}", errors)
        require(route["payload"]["target_kind"] == "readable_html", f"learner route target is not HTML: {unit['semantic_key']}", errors)
        require(route["payload"]["public_url"].startswith("https://"), f"learner route is not HTTPS: {unit['semantic_key']}", errors)
        require(not MACHINE_ROUTE_RE.search(route["payload"]["public_url"]), f"learner route points to machine data: {unit['semantic_key']}", errors)
        search = search_documents[unit_id]
        expected_search = pilot_search[native_id]
        require(search["payload"]["title"] == expected_search["title"], f"search title differs from pilot: {unit['semantic_key']}", errors)
        require(search["payload"]["bounded_search_text"] == expected_search["search_text"], f"search text differs from pilot: {unit['semantic_key']}", errors)
        require(bool(search_pattern.fullmatch(search["payload"]["bounded_search_text"])), f"search text violates zero-prose profile: {unit['semantic_key']}", errors)
        crosswalk = crosswalks[unit_id]
        require(crosswalk["payload"]["source_id"] == native_id, f"crosswalk native ID mismatch: {unit['semantic_key']}", errors)
        require(crosswalk["payload"]["mapping_cardinality"] == "one_to_one", f"crosswalk cardinality mismatch: {unit['semantic_key']}", errors)


def recursively_find_forbidden(value: Any, forbidden: set[str], path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                hits.append(f"{path}.{key}")
            hits.extend(recursively_find_forbidden(child, forbidden, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(recursively_find_forbidden(child, forbidden, f"{path}[{index}]"))
    return hits


def verify_zero_prose(tables: dict[str, list[dict[str, Any]]], profile: dict[str, Any], errors: list[str]) -> None:
    forbidden = set(profile["zero_prose_policy"]["forbidden_field_names"])
    for table, rows in tables.items():
        for row in rows:
            hits = recursively_find_forbidden(row["payload"], forbidden)
            for hit in hits:
                errors.append(f"forbidden prose field in {row['semantic_key']}: {hit}")


def verify_rights_and_accessibility(tables: dict[str, list[dict[str, Any]]], errors: list[str]) -> None:
    rights_by_id = {row["id"]: row for row in tables["rights"]}
    effective: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for assignment in tables["rights_assignments"]:
        if assignment["payload"]["assignment_state"] == "effective":
            effective[assignment["payload"]["target_id"]].append(assignment)
    targets = [
        *(row["id"] for row in tables["units"] if row["payload"]["learner_visibility"] == "visible"),
        *(row["id"] for row in tables["artifacts"]),
        *(row["id"] for row in tables["reader_surfaces"]),
    ]
    for target in targets:
        require(len(effective[target]) == 1, f"effective rights do not resolve exactly once: {target}", errors)
        if effective[target]:
            require(effective[target][0]["payload"]["rights_id"] in rights_by_id, f"effective rights target unknown record: {target}", errors)
    for surface in tables["reader_surfaces"]:
        require(
            surface["payload"]["accessibility_profile"] == "semantic_html_available_native_accessibility_unknown",
            f"accessibility claim is stronger than A00 native evidence: {surface['semantic_key']}",
            errors,
        )


def verify_identity_map_and_projection(package_root: Path, tables: dict[str, list[dict[str, Any]]], errors: list[str]) -> tuple[int, str]:
    rows = []
    path = package_root / "identity-map.jsonl"
    previous = None
    for row, raw in iter_jsonl(path):
        require(canonical_json_bytes(row) == raw, "identity map is not canonical JSONL", errors)
        key = (row["kind"], row["key"])
        require(previous is None or key > previous, "identity map order is not strictly increasing", errors)
        previous = key
        rows.append(row)
    shard_rows = [row for row in rows if row["kind"] == "native_shard_reference"]
    unit_rows = [row for row in rows if row["kind"] == "projected_unit"]
    require(len(shard_rows) == 17, "identity map native shard row count mismatch", errors)
    require(len(unit_rows) == 75, "identity map projected unit row count mismatch", errors)
    require(all(row["zero_copy"] is True for row in rows), "identity map contains a copied mapping", errors)
    require(all(row["mapping_cardinality"] == "one_to_one" for row in unit_rows), "identity map unit cardinality is not one-to-one", errors)
    projected_ids = {row["projected_record_id"] for row in unit_rows}
    require(projected_ids == {row["id"] for row in tables["units"]}, "identity map projected unit set differs from unit table", errors)

    inventory = load_json(package_root / "projection-inventory.json")
    core_facts = inventory["files"]
    for fact in core_facts:
        target = package_root / fact["path"]
        require(target.is_file(), f"projection inventory file is missing: {fact['path']}", errors)
        if target.is_file():
            require(target.stat().st_size == fact["bytes"], f"projection inventory byte mismatch: {fact['path']}", errors)
            require(sha256_path(target) == fact["sha256"], f"projection inventory hash mismatch: {fact['path']}", errors)
    core_digest = combined_digest(core_facts)
    require(core_digest == inventory["projection_digest_sha256"], "projection inventory digest mismatch", errors)
    adapter_run = tables["adapter_runs"][0]
    require(adapter_run["payload"]["build_a_sha256"] == core_digest, "adapter run build A digest mismatch", errors)
    require(adapter_run["payload"]["build_b_sha256"] == core_digest, "adapter run build B digest mismatch", errors)
    require(adapter_run["payload"]["deterministic_replay_result"] == "byte_identical", "adapter run replay state failed", errors)
    require(adapter_run["payload"]["reverse_extraction_result"] == "pass", "adapter reverse extraction state failed", errors)
    return len(rows), core_digest


def verify_seal(package_root: Path, manifest: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    path = package_root / manifest["seal_policy"]["seal_file"]
    if not path.is_file():
        errors.append("seal.json is missing")
        return None
    seal = load_json(path)
    required_keys = {
        "schema_id", "schema_version", "package_id", "recorded_at", "algorithm",
        "seal_excluded_from_own_digest", "files", "file_count", "total_bytes", "sealed_digest_sha256",
    }
    require(set(seal) == required_keys, "seal top-level field set is not exact", errors)
    require(seal.get("schema_id") == "interlanguage/global-modular-mathematics-package-seal/2.2.0", "seal schema_id mismatch", errors)
    require(seal.get("package_id") == manifest["package_id"], "seal package_id mismatch", errors)
    require(seal.get("algorithm") == "sha256-sorted-path-bytes-v1", "seal algorithm mismatch", errors)
    actual_paths = sorted(path.relative_to(package_root).as_posix() for path in package_root.rglob("*") if path.is_file() and path.name != "seal.json")
    declared_paths = sorted(fact["path"] for fact in seal.get("files", []))
    require(actual_paths == declared_paths, "seal file inventory is incomplete or has extras", errors)
    for fact in seal.get("files", []):
        target = package_root / fact["path"]
        if target.is_file():
            require(target.stat().st_size == fact["bytes"], f"seal byte mismatch: {fact['path']}", errors)
            require(sha256_path(target) == fact["sha256"], f"seal hash mismatch: {fact['path']}", errors)
    require(seal.get("file_count") == len(seal.get("files", [])), "seal file_count mismatch", errors)
    require(seal.get("total_bytes") == sum(fact["bytes"] for fact in seal.get("files", [])), "seal total_bytes mismatch", errors)
    require(seal.get("sealed_digest_sha256") == combined_digest(seal.get("files", [])), "seal digest mismatch", errors)
    return seal


def validate_package(package_root: Path, skip_seal: bool) -> dict[str, Any]:
    package_root = package_root.resolve()
    v22_root, program_root, owner_root = package_roots(package_root)
    errors: list[str] = []

    manifest = load_json(package_root / "manifest.json")
    record_schema = load_json(package_root / "schema" / "record-v2.2.schema.json")
    manifest_schema = load_json(package_root / "schema" / "manifest-v2.2.schema.json")
    lane_profile_schema = load_json(package_root / "schema" / "lane-profile-v2.2.schema.json")
    state_schema = load_json(package_root / "schema" / "state-vocabulary-v2.2.schema.json")
    profile = load_json(package_root / "profiles" / "a00-lane-profile.json")
    state_vocabulary = load_json(package_root / "state-vocabulary-v2.2.json")

    errors.extend(schema_errors(manifest, manifest_schema, "manifest"))
    errors.extend(schema_errors(profile, lane_profile_schema, "lane profile"))
    errors.extend(schema_errors(state_vocabulary, state_schema, "state vocabulary"))
    require(manifest.get("profile") == "lane", "manifest is not a lane package", errors)
    require(manifest.get("identity_namespace") == str(IDENTITY_NAMESPACE), "identity namespace mismatch", errors)
    require(manifest.get("identity_formula") == IDENTITY_FORMULA, "identity formula mismatch", errors)

    owner_backend_root = owner_root / profile["native_authority"]["backend_root"]
    owner_manifest = load_json(owner_backend_root / "backend.volume.manifest.json")
    verify_manifest_files(package_root, manifest, errors)
    verify_external_inputs(
        manifest,
        profile,
        package_root=package_root,
        program_root=program_root,
        owner_root=owner_root,
        owner_backend_root=owner_backend_root,
        errors=errors,
    )
    tables, records_by_id = load_tables(package_root, manifest, record_schema, errors)
    native_file_cache, selector_cache = scan_native_for_validation(
        package_root, owner_backend_root, owner_manifest, errors
    )
    verify_content_bindings(
        tables,
        package_root=package_root,
        program_root=program_root,
        owner_root=owner_root,
        owner_backend_root=owner_backend_root,
        native_file_cache=native_file_cache,
        selector_cache=selector_cache,
        errors=errors,
    )
    verify_foreign_keys(tables, records_by_id, manifest, profile, errors)
    verify_state_mapping(records_by_id, state_vocabulary, profile, errors)
    verify_a00_semantics(tables, profile, program_root, errors)
    verify_zero_prose(tables, profile, errors)
    verify_rights_and_accessibility(tables, errors)
    identity_map_rows, core_digest = verify_identity_map_and_projection(package_root, tables, errors)

    loss_report = load_json(package_root / "capability-loss-report.json")
    reverse_report = load_json(package_root / "reverse-extraction-report.json")
    require(loss_report.get("result") == "pass", "capability loss report failed", errors)
    require(loss_report.get("unexplained_native_record_loss") == 0, "unexplained native record loss is nonzero", errors)
    require(loss_report.get("native_records_copied") == 0, "zero-copy policy violated", errors)
    require(loss_report.get("native_records_referenced") == profile["expected_native"]["record_count"], "capability report native count mismatch", errors)
    require(reverse_report.get("result") == "pass", "reverse extraction report failed", errors)
    require(reverse_report.get("native_record_count") == profile["expected_native"]["record_count"], "reverse extraction native count mismatch", errors)
    require(reverse_report.get("one_to_one_unit_bindings") == 75, "reverse extraction unit cardinality mismatch", errors)

    seal = None if skip_seal else verify_seal(package_root, manifest, errors)
    result = "pass" if not errors else "fail"
    checks = [
        {"gate": "G0_schema_and_manifest", "result": result, "evidence": "Draft 2020-12 schemas, exact table inventory, and strict payloads"},
        {"gate": "G1_authority_and_byte_binding", "result": result, "evidence": "All local and external declared inputs matched exact bytes/SHA-256"},
        {"gate": "G2_identity_and_native_mapping", "result": result, "evidence": "UUIDv5, semantic keys, 75 one-to-one module bindings, and 17 native shard references"},
        {"gate": "G3_structure_and_relations", "result": result, "evidence": "75 ordered memberships and exact 74-edge precedence chain"},
        {"gate": "G4_source_target_and_semantic_preservation", "result": result, "evidence": "75 source witnesses, 75 target byte checks, and zero-prose projection"},
        {"gate": "G5_capability_closure", "result": result, "evidence": "Native capabilities referenced or explicitly loss-accounted"},
        {"gate": "G6_rights_and_accessibility", "result": result, "evidence": "Exactly one effective rights result per visible unit/artifact/surface; accessibility remains evidence-specific"},
        {"gate": "G7_adapter_reversibility", "result": result, "evidence": "519678 native rows and all 75 projected selectors replayed exactly"},
        {"gate": "G8_deterministic_replay", "result": result, "evidence": "Two independent materializations are byte-identical"},
        {"gate": "G9_learner_route_and_reader_qa", "result": result, "evidence": "75 exact HTTPS readable-HTML routes; no machine-data learner target"},
        {"gate": "G10_publication_and_anonymous_readback", "result": "inherited", "evidence": "No publication performed; frozen v2.1 route evidence retained"},
        {"gate": "G11_aggregate_federation", "result": "not_applicable", "evidence": "Lane pilot only; aggregate onboarding is outside this package"},
    ]
    report = {
        "schema_id": "interlanguage/global-modular-mathematics-validation-report/2.2.0",
        "schema_version": "2.2.0",
        "package_id": manifest["package_id"],
        "dataset_id": manifest["dataset_id"],
        "recorded_at": manifest["recorded_at"],
        "result": result,
        "checks": checks,
        "counts": {
            "native_records_referenced": profile["expected_native"]["record_count"],
            "native_views": 17,
            "projected_records": manifest["record_count"],
            "record_tables": len(manifest["table_inventory"]),
            "visible_units": len(tables.get("units", [])),
            "routes": len(tables.get("routes", [])),
            "identity_map_rows": identity_map_rows,
            "errors": len(errors),
        },
        "hashes": {
            "manifest_sha256": sha256_path(package_root / "manifest.json"),
            "record_schema_sha256": sha256_path(package_root / "schema" / "record-v2.2.schema.json"),
            "state_vocabulary_sha256": sha256_path(package_root / "state-vocabulary-v2.2.json"),
            "lane_profile_sha256": sha256_path(package_root / "profiles" / "a00-lane-profile.json"),
            "native_shard_index_sha256": sha256_path(package_root / "native-shard-index.json"),
            "identity_map_sha256": sha256_path(package_root / "identity-map.jsonl"),
            "projection_inventory_sha256": sha256_path(package_root / "projection-inventory.json"),
            "projection_core_sha256": core_digest,
            "two_run_replay_sha256": manifest["build"]["build_a_sha256"],
            "sealed_digest_sha256": seal["sealed_digest_sha256"] if seal else None,
        },
        "limitations": profile["limitations"],
        "errors": errors,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--skip-seal", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = validate_package(args.package, args.skip_seal)
    except Exception as exc:
        print(json.dumps({"result": "fail", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

