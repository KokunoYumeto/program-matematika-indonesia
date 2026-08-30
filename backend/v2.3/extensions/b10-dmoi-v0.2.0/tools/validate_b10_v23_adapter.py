#!/usr/bin/env python3
"""Independently validate two isolated B10 backend-v2.3 adapter builds."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import jsonschema


RECORDED_AT = "2026-08-30T00:00:00Z"
LANE_NAMESPACE = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
OWNER_NAMESPACE = "e810c566-4edf-5b5a-ad52-de3dc04e2083"
CURRENT_COURSE_ID = "urn:uuid:8937ae38-2a8f-5cb6-b223-b62da2720974"
CURRENT_V1_COURSE_ID = "urn:uuid:5b7d2a5e-1421-5ac0-b02c-5ae619645272"
CURRENT_A30_COURSE_ID = "urn:uuid:def941e5-b60b-59ca-a3c7-1ed71ab3146d"
CURRENT_A30_V1_COURSE_ID = "urn:uuid:d1133682-6bc8-5b17-911d-47f36299c75d"
COURSE_ROOT = "https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/"
GENERIC_SCHEMA_PAIRS = [
    ("manifest.json", "lane-adapter-v2.3.1.schema.json"),
    ("capability-declarations-v0.2.0.json", "capability-declarations-v0.2.schema.json"),
    ("namespace-crosswalk-v0.2.0.json", "namespace-crosswalk-v0.2.schema.json"),
    ("translation-state-index-v0.2.0.json", "translation-state-index-v0.2.schema.json"),
    ("csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.schema.json"),
    ("scope-declaration-v0.2.0.json", "scope-declaration-v0.2.schema.json"),
]
CAPABILITY_NAMES = [
    "structure_localization", "terminology", "mathematical_preservation",
    "assessment_support", "assets", "accessibility", "corrections",
    "computational_interactives", "publication", "research_support",
]
TABLE_ORDER = [
    "owner_authorities", "datasets", "editions", "units",
    "course_unit_memberships", "native_bindings", "content_bindings",
    "relations", "rights", "rights_assignments", "artifacts",
    "build_recipes", "reader_surfaces", "routes", "search_documents",
    "adapter_profiles", "adapter_runs", "qa_events", "identity_crosswalks",
]
EXPECTED_COUNTS = {
    "owner_authorities": 1,
    "datasets": 1,
    "editions": 1,
    "units": 161,
    "course_unit_memberships": 161,
    "native_bindings": 161,
    "content_bindings": 0,
    "relations": 284,
    "rights": 5,
    "rights_assignments": 161,
    "artifacts": 1,
    "build_recipes": 0,
    "reader_surfaces": 1,
    "routes": 1,
    "search_documents": 161,
    "adapter_profiles": 1,
    "adapter_runs": 1,
    "qa_events": 1,
    "identity_crosswalks": 161,
}
EXPECTED_RECORD_TYPES = {
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


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_row_sha256(row: dict[str, Any]) -> str:
    return sha256_bytes((compact_json(row) + "\n").encode("utf-8"))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if raw:
        require(raw.endswith(b"\n") and not raw.endswith(b"\r\n"), f"nonempty JSONL must end in LF: {path.name}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        for number, line in enumerate(stream, 1):
            require(bool(line.strip()), f"blank JSONL line: {path.name}:{number}")
            row = json.loads(line)
            require(isinstance(row, dict), f"non-object JSONL row: {path.name}:{number}")
            require(compact_json(row) == line.rstrip("\r\n"), f"non-canonical JSONL row: {path.name}:{number}")
            rows.append(row)
    return rows


def identity_set_sha256(values: Iterable[str]) -> str:
    return sha256_bytes("".join(value + "\n" for value in sorted(set(values))).encode("utf-8"))


def inventory_sha256(facts: Iterable[dict[str, Any]]) -> str:
    data = "".join(
        f"{item['path']}\0{item['bytes']}\0{item['sha256']}\n"
        for item in sorted(facts, key=lambda item: item["path"])
    ).encode("utf-8")
    return sha256_bytes(data)


def combined_shard_identity(shards: Iterable[dict[str, Any]]) -> str:
    return sha256_bytes(
        "".join(
            f"{row['path']}\0{row['records']}\0{row['record_id_set_sha256']}\n"
            for row in sorted(shards, key=lambda item: item["path"])
        ).encode("utf-8")
    )


def list_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


def fact(path: Path, relative: str) -> dict[str, Any]:
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_build_identity(package_a: Path, package_b: Path) -> tuple[dict[str, Path], str, int]:
    files_a = list_files(package_a)
    files_b = list_files(package_b)
    require(set(files_a) == set(files_b), "A/B file sets differ")
    total_bytes = 0
    facts: list[dict[str, Any]] = []
    for relative in sorted(files_a):
        data_a = files_a[relative].read_bytes()
        data_b = files_b[relative].read_bytes()
        require(data_a == data_b, f"A/B byte mismatch: {relative}")
        total_bytes += len(data_a)
        facts.append({"path": relative, "bytes": len(data_a), "sha256": sha256_bytes(data_a)})
    return files_a, inventory_sha256(facts), total_bytes


def verify_checksums(package: Path, files: dict[str, Path]) -> None:
    checksum_path = package / "PACKAGE_CHECKSUMS.sha256"
    require(checksum_path.is_file(), "missing checksum file")
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    require(len(lines) == len(files) - 1, "checksum entry count mismatch")
    listed: set[str] = set()
    for line in lines:
        parts = line.split("  ", 1)
        require(len(parts) == 2 and len(parts[0]) == 64, "malformed checksum line")
        digest, relative = parts
        pure = PurePosixPath(relative)
        require(not pure.is_absolute() and ".." not in pure.parts, "unsafe checksum path")
        require(relative != "PACKAGE_CHECKSUMS.sha256" and relative not in listed, "duplicate/self checksum entry")
        require(relative in files and sha256_file(files[relative]) == digest, f"checksum mismatch: {relative}")
        listed.add(relative)
    require(listed == set(files) - {"PACKAGE_CHECKSUMS.sha256"}, "checksum closure mismatch")


def verify_manifest(package: Path, files: dict[str, Path]) -> dict[str, Any]:
    manifest = read_json(package / "manifest.json")
    require(manifest["schema_id"] == "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "manifest schema drift")
    require(manifest["schema_version"] == "2.3.1" and manifest["extension_version"] == "0.2.0", "manifest version drift")
    require(manifest["zero_copy_policy"] == {
        "aggregate_conformance_claim": False,
        "full_prose_centralized": False,
        "machine_data_is_learner_destination": False,
        "machine_surfaces_secondary": True,
        "owner_ids_reminted": False,
        "owner_native_authoritative": True,
    }, "zero-copy policy drift")
    require(manifest["csv_projection"]["record_count"] == sum(EXPECTED_COUNTS.values()), "manifest record count drift")
    require(manifest["csv_projection"]["table_csv_count"] == len(TABLE_ORDER), "manifest CSV table count drift")
    require(manifest["build"]["canonical_serialization"] == {
        "copied_schema_and_tool_files": "preserved_exact_source_bytes",
        "encoding": "UTF-8",
        "json_keys": "lexicographically_sorted",
        "newline": "LF",
        "scope": "builder_generated_json_jsonl_and_csv_only",
        "trailing_newline": True,
    }, "canonical serialization scope drift")
    actual_payload: list[dict[str, Any]] = []
    for relative, path in files.items():
        if relative in {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}:
            continue
        actual_payload.append({**fact(path, relative), "path_base": "package_root", "role": "package_payload"})
    require(manifest["files"] == actual_payload, "manifest payload inventory mismatch")
    payload_identity = inventory_sha256(actual_payload)
    require(manifest["build"]["build_a_sha256"] == payload_identity, "manifest build-A payload digest mismatch")
    require(manifest["build"]["build_b_sha256"] == payload_identity, "manifest build-B payload digest mismatch")
    for item in manifest["sidecars"]:
        path = package / item["path"]
        require(path.is_file() and fact(path, item["path"]) == {k: item[k] for k in ("path", "bytes", "sha256")}, f"sidecar binding drift: {item['path']}")
    scope = manifest["scope_declaration"]
    require(scope["path"] == "scope-declaration-v0.2.0.json", "scope binding path drift")
    return manifest


def verify_authorities(package: Path, repository_root: Path, owner_root: Path) -> dict[str, Any]:
    authority = read_json(package / "INPUT_AUTHORITIES.json")
    require(authority["owner_native_non_mutation"] is True, "owner non-mutation flag missing")
    require(len(authority["authorities"]) == 14, "frozen authority count drift")
    manifest = read_json(package / "manifest.json")
    require(manifest["authorities"] == authority["authorities"], "manifest/input authority inventory divergence")
    bases = {"program_repository_root": repository_root, "owner_package_root": owner_root}
    for item in authority["authorities"]:
        base = bases.get(item["path_base"])
        require(base is not None, "unknown authority path base")
        pure = PurePosixPath(item["path"])
        require(not pure.is_absolute() and ".." not in pure.parts, "unsafe authority path")
        path = base.joinpath(*pure.parts)
        require(path.is_file(), f"missing authority: {item['role']}")
        require(path.stat().st_size == item["bytes"] and sha256_file(path) == item["sha256"], f"authority drift: {item['role']}")
    owner_manifest = read_json(owner_root / "package.json")
    checked: list[dict[str, Any]] = []
    for item in owner_manifest["files"]:
        pure = PurePosixPath(item["path"])
        path = owner_root.joinpath(*pure.parts)
        require(path.is_file(), f"missing owner member: {item['path']}")
        current = {"path": item["path"], "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        require(current["bytes"] == item["bytes"] and current["sha256"] == item["sha256"], f"owner member drift: {item['path']}")
        checked.append({**current, "path_base": "owner_package_root", "role": "owner_manifest_member"})
    closure = authority["owner_manifest_closure"]
    require(len(checked) == closure["files"] == 78, "owner closure file count mismatch")
    require(sum(row["bytes"] for row in checked) == closure["bytes"] == 436966309, "owner closure byte mismatch")
    require(inventory_sha256(checked) == closure["inventory_sha256"], "owner closure digest mismatch")
    readback_rows = [item for item in authority["authorities"] if item["role"] == "learner_route_readback"]
    require(len(readback_rows) == 1, "learner-route readback authority missing")
    readback_path = repository_root.joinpath(*PurePosixPath(readback_rows[0]["path"]).parts)
    readback = read_json(readback_path)
    require(
        readback["result"] == "pass" and readback["authentication_used"] is False
        and readback["learner_route"] == COURSE_ROOT and len(readback["checks"]) == 2,
        "anonymous learner-route readback result drift",
    )
    require(all(row["status_code"] == 200 and row["bytes"] > 0 and len(row["sha256"]) == 64 for row in readback["checks"]), "anonymous learner-route byte facts invalid")
    return authority


def verify_tables(package: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    all_ids: list[str] = []
    for table in TABLE_ORDER:
        rows = read_jsonl(package / "tables" / f"{table}.jsonl")
        require(len(rows) == EXPECTED_COUNTS[table], f"table count drift: {table}")
        for row in rows:
            require(row["record_type"] == EXPECTED_RECORD_TYPES[table], f"record type/table mismatch: {table}")
            expected_id = "urn:uuid:" + str(uuid.uuid5(LANE_NAMESPACE, f"{row['record_type']}:{row['semantic_key']}"))
            require(row["id"] == expected_id, f"projection UUID formula mismatch: {table}")
            require(row["dataset_id"].startswith("urn:uuid:"), f"missing dataset ID: {table}")
            all_ids.append(row["id"])
        tables[table] = rows
    require(len(all_ids) == len(set(all_ids)), "global projected ID collision")
    dataset_id = tables["datasets"][0]["id"]
    owner_authority_id = tables["owner_authorities"][0]["id"]
    require(all(row["dataset_id"] == dataset_id for rows in tables.values() for row in rows), "non-uniform projected dataset ID")
    require(all(row["owner_authority_id"] == owner_authority_id for rows in tables.values() for row in rows), "non-uniform owner authority ID")

    units = tables["units"]
    native_to_projected: dict[str, str] = {}
    roots = 0
    kinds: dict[str, int] = {}
    for row in units:
        payload = row["payload"]
        native = payload["native_unit_id"]
        native_to_projected[native] = row["id"]
        kinds[payload["native_unit_kind"]] = kinds.get(payload["native_unit_kind"], 0) + 1
        if payload["parent_native_unit_id"] is None:
            roots += 1
        else:
            require(payload["parent_native_unit_id"] in native_to_projected or any(x["payload"]["native_unit_id"] == payload["parent_native_unit_id"] for x in units), "unit parent closure failed")
        route = payload["learner_route"]
        require(route["url"] == COURSE_ROOT and route["anchor"] is None, "invented/non-root learner route")
        require(route["route_state"] == "course_fallback_unit_route_planned_not_published", "unit route state drift")
        require(payload["translation_state"] == "published", "unit translation state drift")
    require(roots == 1, "structural root count drift")
    require(kinds == {"book": 1, "chapter": 7, "section": 36, "subsection": 117}, "structural kind counts drift")
    require(identity_set_sha256(native_to_projected) == "023c7832b6244ba795e6b7c15e36e9a11da7cc0022d6283f31264494dae1778f", "native structural identity digest drift")

    memberships = tables["course_unit_memberships"]
    require(len({row["payload"]["unit_id"] for row in memberships}) == 161, "membership unit uniqueness drift")
    for row in memberships:
        payload = row["payload"]
        require(payload["course_id"] == CURRENT_COURSE_ID, "membership course ID drift")
        require(payload["unit_id"] in set(native_to_projected.values()), "membership target closure failed")
        require(payload["native_unit_id"] in native_to_projected, "membership native closure failed")
        require(payload["required"] is None and payload["visible"] is None, "unbound membership policy was asserted")
        require(payload["membership_policy_state"] == "not_projected_no_bound_curriculum_policy", "membership policy limitation missing")

    for row in tables["native_bindings"]:
        payload = row["payload"]
        require(payload["native_id"] in native_to_projected and payload["subject_id"] == native_to_projected[payload["native_id"]], "native binding closure failed")
    for row in tables["identity_crosswalks"]:
        payload = row["payload"]
        require(payload["source_id"] in native_to_projected and payload["target_id"] == native_to_projected[payload["source_id"]], "table crosswalk closure failed")

    rights_ids = {row["id"] for row in tables["rights"]}
    for row in tables["rights_assignments"]:
        payload = row["payload"]
        require(payload["rights_id"] in rights_ids and payload["target_id"] in set(native_to_projected.values()), "rights assignment foreign-key failure")

    relations = tables["relations"]
    relation_counts: dict[str, int] = {}
    external: set[str] = set()
    for row in relations:
        payload = row["payload"]
        relation_counts[payload["relation_type"]] = relation_counts.get(payload["relation_type"], 0) + 1
        require(payload["concept_relation_inferred"] is False, "inferred concept relation")
        for endpoint in (payload["from_endpoint"], payload["to_endpoint"]):
            native = endpoint["native_id"]
            if native in native_to_projected:
                require(endpoint["projected_id"] == native_to_projected[native], "relation endpoint projection mismatch")
            else:
                require(endpoint["projected_id"] is None, "external endpoint projected without evidence")
                external.add(native)
    require(relation_counts == {"contains": 161, "precedes": 122, "requires_course": 1}, "relation counts drift")
    require(external == {"course:A30", "course:B10"}, "external endpoint set drift")
    prerequisite = [row for row in relations if row["payload"]["relation_type"] == "requires_course"]
    require(len(prerequisite) == 1, "prerequisite relation uniqueness drift")
    prerequisite_evidence = prerequisite[0]["payload"]["evidence"]
    require(
        prerequisite_evidence["current_b10_course_record_id"] == CURRENT_COURSE_ID
        and prerequisite_evidence["current_a30_course_record_id"] == CURRENT_A30_COURSE_ID
        and prerequisite_evidence["current_b10_v1_course_id"] == CURRENT_V1_COURSE_ID
        and prerequisite_evidence["current_a30_v1_course_id"] == CURRENT_A30_V1_COURSE_ID
        and prerequisite_evidence["current_prerequisite_course_ids"] == ["A30"]
        and prerequisite_evidence["current_prerequisite_binding_state"] == "reconfirmed_from_federation_v0.4.4",
        "current prerequisite evidence binding drift",
    )

    searches = tables["search_documents"]
    require({row["payload"]["native_unit_id"] for row in searches} == set(native_to_projected), "search/unit coverage drift")
    for row in searches:
        payload = row["payload"]
        require(payload["unit_id"] == native_to_projected[payload["native_unit_id"]], "search projected unit mismatch")
        require(payload["learner_url"] == COURSE_ROOT and payload["learner_anchor"] is None, "search route drift")

    route = tables["routes"][0]["payload"]
    require(route["course_id"] == CURRENT_COURSE_ID and route["public_url"] == COURSE_ROOT, "course-root route drift")
    require(route["unit_id"] is None and route["unit_anchor"] is None and route["unit_route_state"] == "planned_not_published", "unit route overclaim")
    require(route["machine_data_only"] is False and route["target_kind"] == "readable_html", "machine route exposed as learner route")
    require(route["access_state"] == "public_anonymous_readback_verified" and route["route_kind"] == "verified_course_root_fallback", "course route readback claim drift")
    artifact = tables["artifacts"][0]
    reader = tables["reader_surfaces"][0]
    require(reader["payload"]["artifact_id"] == artifact["id"] and route["surface_id"] == reader["id"], "artifact/reader/route foreign-key closure failed")
    require(artifact["payload"]["verification_authority"] == "learner_route_readback", "artifact readback authority missing")
    return tables, native_to_projected


def verify_owner_semantics(
    package: Path,
    repository_root: Path,
    owner_root: Path,
    tables: dict[str, list[dict[str, Any]]],
    native_to_projected: dict[str, str],
) -> None:
    """Replay compact adapter claims against owner-native table semantics."""
    owner_units = {row["id"]: row for row in read_jsonl(owner_root / "data/units.jsonl")}
    pilot_root = repository_root / "backend/v2.1/pilots/b10-dmoi"
    pilot_units = {row["stable_unit_id"]: row for row in read_jsonl(pilot_root / "units.jsonl")}
    structural = {
        row["id"]: row for row in owner_units.values()
        if row["unit_kind"] in {"book", "chapter", "section", "subsection"}
    }
    require(set(structural) == set(native_to_projected), "pilot/native structural selector mismatch")
    require(
        {kind: sum(1 for row in structural.values() if row["unit_kind"] == kind) for kind in {"book", "chapter", "section", "subsection"}}
        == {"book": 1, "chapter": 7, "section": 36, "subsection": 117},
        "owner structural-kind closure mismatch",
    )
    occurrences = {row["id"]: row for row in read_jsonl(owner_root / "data/occurrences.jsonl")}
    revisions = {row["id"]: row for row in read_jsonl(owner_root / "data/file_revisions.jsonl")}
    segments = {row["id"]: row for row in read_jsonl(owner_root / "data/segments.jsonl")}
    variants = {row["id"]: row for row in read_jsonl(owner_root / "data/segment_variants.jsonl")}
    for unit in tables["units"]:
        payload = unit["payload"]
        native = payload["native_unit_id"]
        owner_unit = structural[native]
        pilot = pilot_units[native]
        require(owner_unit["unit_kind"] == payload["native_unit_kind"], "owner unit-kind mismatch")
        for pilot_field, projected_field in {
            "native_unit_kind": "native_unit_kind", "native_locator": "native_locator",
            "parent_stable_unit_id": "parent_native_unit_id", "order_key": "order_key",
            "localized_title": "title", "locale": "title_locale",
            "localized_occurrence_id": "localized_occurrence_id",
            "localized_title_variant_id": "localized_title_variant_id",
            "localized_title_payload_sha256": "localized_title_payload_sha256",
            "source_file_revision_id": "source_file_revision_id", "source_file_sha256": "source_file_sha256",
            "source_subtree_sha256": "source_subtree_sha256", "target_file_revision_id": "target_file_revision_id",
            "target_file_sha256": "target_file_sha256", "target_subtree_sha256": "target_subtree_sha256",
            "translation_state": "translation_state",
        }.items():
            require(pilot[pilot_field] == payload[projected_field], f"pilot unit projection mismatch: {pilot_field}")
        target = occurrences.get(payload["localized_occurrence_id"])
        require(target is not None, "missing target occurrence")
        require(
            target["unit_id"] == native
            and target["locale"] == "id-ID"
            and target["translation_state"] == "published"
            and target["reader_visibility"] == "reader-facing",
            "target occurrence state mismatch",
        )
        source_occurrence_id = target["source_occurrence_id"]
        require(source_occurrence_id in occurrences, "missing source occurrence")
        source = occurrences[source_occurrence_id]
        require(source["unit_id"] == native and source["locale"] == "en-US", "source occurrence mismatch")
        require(source["file_revision_id"] == payload["source_file_revision_id"], "source revision ID mismatch")
        require(target["file_revision_id"] == payload["target_file_revision_id"], "target revision ID mismatch")
        require(source["subtree_sha256"] == payload["source_subtree_sha256"], "source subtree mismatch")
        require(target["subtree_sha256"] == payload["target_subtree_sha256"], "target subtree mismatch")
        require(revisions[source["file_revision_id"]]["sha256"] == payload["source_file_sha256"], "source file hash mismatch")
        require(revisions[target["file_revision_id"]]["sha256"] == payload["target_file_sha256"], "target file hash mismatch")
        variant = variants.get(payload["localized_title_variant_id"])
        require(variant is not None, "missing localized title variant")
        require(
            variant["locale"] == "id-ID"
            and variant["role"] == "translation"
            and variant["translation_state"] == "published"
            and variant["payload_sha256"] == payload["localized_title_payload_sha256"],
            "localized title variant mismatch",
        )
        segment = segments.get(variant["segment_id"])
        require(segment is not None and segment["unit_id"] == native and segment["segment_kind"] == "title", "title segment binding mismatch")

    owner_relations = {row["id"]: row for row in read_jsonl(owner_root / "data/relations.jsonl")}
    pilot_relations = read_jsonl(pilot_root / "relations.jsonl")
    pilot_native_relations = {row["evidence"]["native_relation_id"]: row for row in pilot_relations if row["evidence"].get("native_relation_id")}
    native_relation_rows = 0
    for relation in tables["relations"]:
        payload = relation["payload"]
        native_relation_id = payload["evidence"].get("native_relation_id")
        if native_relation_id is None:
            require(payload["relation_type"] == "requires_course", "non-native relation lacks prerequisite authority")
            continue
        native_relation_rows += 1
        native = owner_relations.get(native_relation_id)
        require(native is not None, "missing native relation evidence")
        require(native["relation_type"] == payload["relation_type"], "native relation type mismatch")
        require(native["from_id"] == payload["from_endpoint"]["native_id"], "native relation from-endpoint mismatch")
        require(native["to_id"] == payload["to_endpoint"]["native_id"], "native relation to-endpoint mismatch")
        require(native["strength"] == payload["strength"], "native relation strength mismatch")
        pilot_relation = pilot_native_relations[native_relation_id]
        require(
            pilot_relation["relation_type"] == payload["relation_type"]
            and pilot_relation["from_id"] == payload["from_endpoint"]["native_id"]
            and pilot_relation["to_id"] == payload["to_endpoint"]["native_id"]
            and pilot_relation["strength"] == payload["strength"]
            and all(payload["evidence"].get(key) == value for key, value in pilot_relation["evidence"].items()),
            "pilot relation projection mismatch",
        )
    require(native_relation_rows == 283, "native relation evidence count mismatch")

    courses = read_jsonl(repository_root / "backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl")
    by_course = {row["payload"]["course_id"]: row for row in courses}
    require(by_course["B10"]["payload"]["prerequisite_course_ids"] == ["A30"], "current prerequisite list mismatch")
    prerequisite = next(row for row in tables["relations"] if row["payload"]["relation_type"] == "requires_course")
    evidence = prerequisite["payload"]["evidence"]
    require(evidence["current_b10_course_record_sha256"] == canonical_row_sha256(by_course["B10"]), "current B10 row hash mismatch")
    require(evidence["current_a30_course_record_sha256"] == canonical_row_sha256(by_course["A30"]), "current A30 row hash mismatch")

    pilot_search = {row["stable_unit_id"]: row for row in read_jsonl(pilot_root / "search.jsonl")}
    for projected in tables["search_documents"]:
        payload = projected["payload"]
        source = pilot_search[payload["native_unit_id"]]
        require(
            payload["title"] == source["title"]
            and payload["bounded_search_text"] == source["search_text"]
            and payload["locale"] == source["locale"]
            and payload["order_key"] == source["order_key"]
            and payload["learner_url"] == source["learner_url"],
            "pilot search projection mismatch",
        )

    owner_rights = {row["id"]: row for row in read_jsonl(owner_root / "data/rights.jsonl")}
    for projected in tables["rights"]:
        payload = projected["payload"]
        native = owner_rights.get(payload["native_rights_id"])
        require(native is not None, "missing native rights component")
        for field in ("source_component_id", "assertion_status", "attribution", "license_expression", "third_party_status"):
            require(native[field] == payload[field], f"native rights field mismatch: {field}")

    accessibility = read_jsonl(owner_root / "data/accessibility.jsonl")
    require(len(accessibility) == 235, "native accessibility count mismatch")
    breakdown: dict[str, int] = {}
    for row in accessibility:
        key = f"{row['locale']}:{row['kind']}"
        breakdown[key] = breakdown.get(key, 0) + 1
    require(breakdown == {"id-ID:description": 183, "id-ID:shortdescription": 52}, "native accessibility breakdown mismatch")
    validation = read_json(owner_root / "validation_report.json")
    require(validation["result"] == "pass" and validation["metrics"]["records"] == 163583, "owner validation result drift")
    for table, count in {
        "terms": 106, "term_variants": 212, "assets": 482, "asset_revisions": 964,
        "accessibility": 235, "corrections": 79, "correction_claims": 114,
        "correction_bindings": 114, "interactives": 252, "rights": 5,
        "rights_assignments": 7636, "rights_rules": 7, "rights_rule_members": 514,
    }.items():
        require(validation["table_counts"][table] == count, f"owner capability table count drift: {table}")


def verify_sidecars(
    package: Path,
    owner_root: Path,
    native_to_projected: dict[str, str],
    tables: dict[str, list[dict[str, Any]]],
) -> None:
    scope = read_json(package / "scope-declaration-v0.2.0.json")
    require(scope["scope_kind"] == "lane_adapter" and scope["course_ids"] == ["B10"], "scope lane/course drift")
    require(scope["aggregate_conformance_claim"] is False and len(scope["unbound_curriculum_role_ids"]) == 39, "scope complement drift")
    require("B10" not in scope["unbound_curriculum_role_ids"], "B10 incorrectly marked unbound")

    capabilities = read_json(package / "capability-declarations-v0.2.0.json")
    rows = capabilities["capabilities"]
    require([row["name"] for row in rows] == CAPABILITY_NAMES, "capability order/name drift")
    expected_states = {
        "structure_localization": "referenced_native_shards", "terminology": "referenced_native_shards",
        "mathematical_preservation": "referenced_native_shards", "assessment_support": "not_projected",
        "assets": "referenced_native_shards", "accessibility": "referenced_native_shards",
        "corrections": "referenced_native_shards", "computational_interactives": "referenced_native_shards",
        "publication": "materialized", "research_support": "not_projected",
    }
    require({row["name"]: row["state"] for row in rows} == expected_states, "capability states drift")
    owner_manifest = read_json(owner_root / "package.json")
    owner_facts = {row["path"]: row for row in owner_manifest["files"]}
    for row in rows:
        require(row["version"] == "0.1.0" and row["closure_rules"], f"capability contract fields missing: {row['name']}")
        if row["state"] == "not_projected":
            require(row["native_count"] == row["projected_count"] == 0 and not row["shard_refs"], "not-projected capability overclaims native/projected closure")
            require(row["identity_set_scope"] == "none" and row["identity_set_sha256"] is None, "not-projected capability identity overclaim")
            require(row["loss_gap_report"]["status"] == "declared_limitation", "not-projected capability lacks limitation")
            continue
        for shard in row["shard_refs"]:
            expected = owner_facts[shard["path"]]
            path = owner_root.joinpath(*PurePosixPath(shard["path"]).parts)
            require(path.stat().st_size == shard["bytes"] == expected["bytes"] and sha256_file(path) == shard["sha256"] == expected["sha256"], "capability shard byte drift")
            records = read_jsonl(path)
            require(len(records) == shard["records"], "capability shard record-count drift")
            require(identity_set_sha256(record["id"] for record in records) == shard["record_id_set_sha256"], "capability shard identity-set drift")
        require(row["native_count"] == sum(shard["records"] for shard in row["shard_refs"]), "capability native-count semantics drift")
        if row["identity_set_scope"] == "native_shard_records":
            require(row["identity_set_sha256"] == combined_shard_identity(row["shard_refs"]), "capability native identity digest drift")
        require(row["loss_gap_report"]["status"] == "closed", "bound capability closure not marked closed")
    by_name = {row["name"]: row for row in rows}
    structure_ids = [row["id"] for name in ("units", "course_unit_memberships") for row in tables[name]]
    publication_ids = [row["id"] for name in ("artifacts", "reader_surfaces", "routes") for row in tables[name]]
    require(by_name["structure_localization"]["projected_count"] == len(structure_ids), "structure projected count drift")
    require(by_name["structure_localization"]["identity_set_sha256"] == identity_set_sha256(structure_ids), "structure projected identity digest drift")
    require(by_name["publication"]["projected_count"] == len(publication_ids), "publication projected count drift")
    require(by_name["publication"]["identity_set_sha256"] == identity_set_sha256(publication_ids), "publication projected identity digest drift")

    rights_cross = capabilities["rights_cross_cutting"]
    for shard in rights_cross["shard_refs"]:
        expected = owner_facts[shard["path"]]
        path = owner_root.joinpath(*PurePosixPath(shard["path"]).parts)
        require(path.stat().st_size == shard["bytes"] == expected["bytes"] and sha256_file(path) == shard["sha256"] == expected["sha256"], "rights shard byte drift")
        records = read_jsonl(path)
        require(len(records) == shard["records"] and identity_set_sha256(record["id"] for record in records) == shard["record_id_set_sha256"], "rights shard identity closure drift")
    require(rights_cross["native_count"] == sum(row["records"] for row in rights_cross["shard_refs"]), "rights native count drift")
    require(rights_cross["identity_set_sha256"] == combined_shard_identity(rights_cross["shard_refs"]), "rights identity digest drift")

    crosswalk = read_json(package / "namespace-crosswalk-v0.2.0.json")
    mappings = crosswalk["mappings"]
    require(len(mappings) == 162, "namespace mapping count drift")
    native_rows = [row for row in mappings if row["source_namespace"] == OWNER_NAMESPACE]
    require(len(native_rows) == 161, "native unit crosswalk count drift")
    for row in native_rows:
        require(row["source_record_id"] in native_to_projected and row["target_record_id"] == native_to_projected[row["source_record_id"]], "native crosswalk target mismatch")
        require(row["mapping_state"] == "mapped" and row["cardinality"] == "one_to_one" and row["reverse_recipe"], "native crosswalk state drift")
        require(row["identity_set_sha256"] == identity_set_sha256([row["source_record_id"], row["target_record_id"]]), "native crosswalk pair digest drift")
    course_rows = [row for row in mappings if row["source_record_id"] == CURRENT_V1_COURSE_ID]
    require(len(course_rows) == 1 and course_rows[0]["target_record_id"] == CURRENT_COURSE_ID, "current v1/v2 course mapping drift")
    candidates = crosswalk["unmaterialized_candidates"]
    require(len(candidates) == 1 and candidates[0]["state"] == "deterministic_id_proposal_not_a_mapping", "unmaterialized candidate state drift")
    require(candidates[0]["effective_cardinality"] == "unresolved_until_materialized", "unmaterialized candidate cardinality overclaim")
    require(crosswalk["identity_sets"]["native_units_sha256"] == identity_set_sha256(native_to_projected), "crosswalk native digest drift")
    require(crosswalk["identity_sets"]["projected_units_sha256"] == identity_set_sha256(native_to_projected.values()), "crosswalk projected digest drift")

    state_index = read_json(package / "translation-state-index-v0.2.0.json")
    states = state_index["records"]
    require(state_index["no_inference"] is True and state_index["coverage"]["inferred_rows"] == 0, "translation-state inference overclaim")
    require(len(states) == 161 and {row["native_unit_id"] for row in states} == set(native_to_projected), "translation state coverage drift")
    unit_payloads = {row["payload"]["native_unit_id"]: row["payload"] for row in tables["units"]}
    for row in states:
        payload = unit_payloads[row["native_unit_id"]]
        require(row["projected_unit_id"] == native_to_projected[row["native_unit_id"]], "translation projected unit mismatch")
        require(row["state"] == "published" and row["locale"] == "id-ID", "translation state/locale drift")
        for field in ("localized_occurrence_id", "localized_title_variant_id", "source_file_sha256", "source_subtree_sha256", "target_file_sha256", "target_subtree_sha256"):
            require(row[field] == payload[field], f"translation-state unit binding drift: {field}")
    require(state_index["identity_set_sha256"] == identity_set_sha256(native_to_projected.values()), "translation-state identity digest drift")

    rights = read_json(package / "evidence/rights_accessibility.json")
    require(len(rights["rights"]["components"]) == 5, "rights component closure drift")
    accessibility = rights["accessibility"]
    require(accessibility["native_record_count"] == 235, "accessibility record count drift")
    require(accessibility["record_counts_by_locale_and_kind"] == {"id-ID:description": 183, "id-ID:shortdescription": 52}, "accessibility breakdown drift")


def verify_csv(package: Path, tables: dict[str, list[dict[str, Any]]]) -> None:
    index = read_json(package / "csv-projection-manifest-v0.2.0.json")
    require(index["table_order"] == TABLE_ORDER and len(index["tables"]) == len(TABLE_ORDER), "CSV index table order drift")
    require(index["canonical_serialization"]["csv_dialect"] == "RFC4180-compatible quoting", "CSV dialect claim drift")
    require(index["canonical_serialization"]["record_terminator"] == "LF", "CSV record terminator claim drift")
    global_rows: list[list[str]] = []
    for table, entry in zip(TABLE_ORDER, index["tables"]):
        require(entry["table"] == table, "CSV index table mismatch")
        path = package / "csv" / f"{table}.csv"
        with path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        expected = [["stable_id", "record_type", "canonical_record_json"]] + [
            [row["id"], row["record_type"], compact_json(row)] for row in tables[table]
        ]
        require(rows == expected, f"CSV row mismatch: {table}")
        regenerated = bytearray()
        import io
        with io.StringIO(newline="") as text:
            writer = csv.writer(text, lineterminator="\n")
            writer.writerows(rows)
            regenerated.extend(text.getvalue().encode("utf-8"))
        require(bytes(regenerated) == path.read_bytes(), f"CSV byte replay mismatch: {table}")
        reconstructed = "".join(row[2] + "\n" for row in rows[1:]).encode("utf-8")
        require(reconstructed == (package / "tables" / f"{table}.jsonl").read_bytes(), f"CSV-to-JSONL mismatch: {table}")
        require(entry["roundtrip_sha256"] == sha256_bytes(reconstructed) and entry["roundtrip_state"] == "pass", f"CSV receipt drift: {table}")
        for ordinal, row in enumerate(rows[1:], 1):
            global_rows.append([f"tables/{table}.jsonl", str(ordinal), row[0], row[1], row[2]])
    global_rows.sort(key=lambda row: (row[3], row[2], row[0], int(row[1])))
    with (package / "records.csv").open("r", encoding="utf-8", newline="") as stream:
        actual_global = list(csv.reader(stream))
    expected_global = [["source_jsonl_path", "source_row_ordinal", "stable_id", "record_type", "canonical_record_json"]] + global_rows
    require(actual_global == expected_global, "global records.csv mismatch")
    require(index["records_csv"]["records"] == len(global_rows), "global CSV count drift")
    require(index["records_csv"]["roundtrip_sha256"] == sha256_bytes("".join(row[4] + "\n" for row in global_rows).encode("utf-8")), "global CSV roundtrip digest drift")
    csv_facts = [entry["csv"] for entry in index["tables"]] + [{k: index["records_csv"][k] for k in ("path", "bytes", "sha256", "role")}]
    require(index["aggregate_sha256"] == inventory_sha256(csv_facts), "CSV aggregate digest drift")


def verify_schemas_and_tools(package: Path, repository_root: Path, manifest: dict[str, Any]) -> None:
    schema_root = repository_root / "backend/v2.3/schema"
    format_checker = jsonschema.FormatChecker()
    for instance_name, schema_name in GENERIC_SCHEMA_PAIRS:
        package_schema = package / "schema" / schema_name
        repository_schema = schema_root / schema_name
        require(package_schema.read_bytes() == repository_schema.read_bytes(), f"packaged schema drift: {schema_name}")
        schema = read_json(package_schema)
        jsonschema.Draft202012Validator.check_schema(schema)
        instance = read_json(package / instance_name)
        errors = sorted(
            jsonschema.Draft202012Validator(schema, format_checker=format_checker).iter_errors(instance),
            key=lambda error: list(error.absolute_path),
        )
        require(not errors, f"schema validation failed: {instance_name}: {errors[0].message if errors else ''}")

    builder_repo = repository_root / "backend/v2.3/scripts/build_b10_v23_adapter.py"
    validator_repo = repository_root / "backend/v2.3/scripts/validate_b10_v23_adapter.py"
    require((package / "tools/build_b10_v23_adapter.py").read_bytes() == builder_repo.read_bytes(), "packaged builder revision drift")
    require((package / "tools/validate_b10_v23_adapter.py").read_bytes() == validator_repo.read_bytes(), "packaged validator revision drift")
    for name, repo_path in (("builder", builder_repo), ("validator", validator_repo)):
        binding = manifest["build"][name]
        require(binding["bytes"] == repo_path.stat().st_size and binding["sha256"] == sha256_file(repo_path), f"manifest {name} binding drift")


def verify_seal(package: Path, manifest: dict[str, Any], files: dict[str, Path]) -> dict[str, Any]:
    seal = read_json(package / "seal.json")
    require(seal["package_id"] == manifest["package_id"] and seal["seal_excluded_from_own_digest"] is True, "seal policy drift")
    expected = [
        {**fact(path, relative), "path_base": "package_root", "role": "package_payload"}
        for relative, path in files.items()
        if relative not in {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}
    ]
    expected.append({**fact(package / "manifest.json", "manifest.json"), "path_base": "package_root", "role": "package_manifest"})
    require(seal["files"] == expected, "seal file inventory drift")
    require(seal["file_count"] == len(expected) and seal["bytes"] == sum(row["bytes"] for row in expected), "seal count/byte drift")
    require(seal["aggregate_sha256"] == inventory_sha256(expected), "seal aggregate digest drift")
    return seal


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def validate(args: argparse.Namespace) -> dict[str, Any]:
    package_a = args.package_a.resolve()
    package_b = args.package_b.resolve()
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    require(package_a.is_dir() and package_b.is_dir(), "both package directories are required")
    files, full_inventory, total_bytes = verify_build_identity(package_a, package_b)
    verify_checksums(package_a, files)
    manifest = verify_manifest(package_a, files)
    authority = verify_authorities(package_a, repository_root, owner_root)
    tables, native_map = verify_tables(package_a)
    verify_owner_semantics(package_a, repository_root, owner_root, tables, native_map)
    verify_sidecars(package_a, owner_root, native_map, tables)
    verify_csv(package_a, tables)
    verify_schemas_and_tools(package_a, repository_root, manifest)
    seal = verify_seal(package_a, manifest, files)
    checks = [
        "A/B byte identity and exact file-set closure",
        "package checksums and manifest payload inventory",
        "14 frozen authorities and complete 78-file owner manifest closure",
        "six corpus-neutral v2.3.1 schemas and exact packaged tool revisions",
        "19 canonical JSONL tables and global projected-ID uniqueness",
        "161-unit structural, parent, title, translation, and null-anchor closure",
        "owner-native occurrence, file-revision, title-variant, relation, rights, accessibility, and capability-table replay",
        "284-relation topology plus current B10-to-A30 prerequisite row/hash closure",
        "161 search-document and course-root learner-route closure",
        "five-component rights and 235-record accessibility closure",
        "ten canonical capabilities with shard identities, closure rules, and explicit loss gaps",
        "161 reversible native/projected unit crosswalks plus one current course mapping and a non-mapping candidate",
        "161 owner-occurrence-and-variant-derived translation-state records",
        "19 per-table CSVs plus global records.csv exact round-trip",
        "non-circular package seal and complete checksum closure",
    ]
    return {
        "schema_id": "program-matematika-indonesia/b10-v23-adapter-validation-receipt/0.2.0",
        "recorded_at": RECORDED_AT,
        "status": "pass",
        "package_id": manifest["package_id"],
        "dataset_id": manifest["dataset_id"],
        "course_id": "B10",
        "builds_compared": 2,
        "build_labels": [package_a.name, package_b.name],
        "build_location_base": "program_repository_root/backend/v2.3/builds",
        "files_per_build": len(files),
        "bytes_per_build": total_bytes,
        "byte_identical": True,
        "full_inventory_sha256": full_inventory,
        "payload_inventory_sha256": manifest["build"]["build_a_sha256"],
        "seal_aggregate_sha256": seal["aggregate_sha256"],
        "canonical_records": sum(EXPECTED_COUNTS.values()),
        "pilot_materialized_records": 606,
        "owner_native_records_referenced": 163583,
        "owner_manifest_closure": authority["owner_manifest_closure"],
        "tool_bindings": manifest["build"],
        "schema_instances_validated": [pair[0] for pair in GENERIC_SCHEMA_PAIRS],
        "invocation_boundary": {
            "repository_root": "program_repository_root",
            "owner_package_root": "B10_owner_package_root",
            "package_a": package_a.name,
            "package_b": package_b.name,
            "receipt": f"coordinator_logbook/{args.receipt.name}"
        },
        "checks": checks,
        "learner_route": COURSE_ROOT,
        "unit_anchor_coverage": 0,
        "aggregate_40_role_conformance_claim": False,
        "owner_native_mutations": 0,
        "credentials_recorded": False,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--package-a", type=Path, required=True)
    parser.add_argument("--package-b", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        receipt = validate(args)
        write_receipt(args.receipt.resolve(), receipt)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(compact_json(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
